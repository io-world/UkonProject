"""Stage 6 — decision, bind, report.

Stage 6 opens with the owner's decision on the proposal pack: which option, or "not now" and why (the
questionnaire in Stage 5 doesn't depend on it). Then it closes the deal:
  1. Firm quote in   the carrier's firm quote is a raw source (wiki/raw/<slug>/quotes/), extracted by the model
                     (or its cached output), every figure and date checked against the text, and compared with
                     the written indication it follows. Carrier values are locked (DB trigger).
  2. Final terms     the owner accepts or declines the firm terms (decline needs a reason).
  3. Bind            every "before binding" condition is marked met by a person, with evidence; then the binder
                     is recorded. The carrier's side of binding is simulated in this prototype.
  4. Report          a plain-language summary for the client, a deal record for the agency and UKON, and the
                     after-bind plan: 30-60-90 days and the touchpoints through the year to the next renewal.

Rules, not the model, decide everything here: what changed, which conditions are open, the plan's dates.

    uv run python -m pipeline.bind <quote.pdf>      # ingest a firm quote from the command line"""
import re
import sys
from datetime import date, timedelta
from pathlib import Path

from . import indication_extract as ix
from . import indications, llm, wiki_render
from .config import CLIENT_SLUG, RAW, REQUESTED_OPTIONS, WIKI
from .db import client_by_slug, connect, j, user_id
from .sources import read_source

OPTION = {o["tier"]: o for o in REQUESTED_OPTIONS}
REASONS = {"price": "Price", "already_covered": "Thinks another policy already covers it",
           "no_need": "Doesn't see the need", "carrier_requirements": "Can't meet the carrier's requirements",
           "timing": "Wants to revisit later", "other": "Other"}


def _money(v):
    return f"${v:,.0f}" if isinstance(v, (int, float)) else str(v)


def _iso(d):
    return d.isoformat() if isinstance(d, date) else d


# --- decisions (Stage 6: on the proposal, then on the firm quote) ---------------------------------------------

def decide(conn, cid: int, actor_id: int, stage: str, decision: str, carrier: str | None = None,
           tier: str | None = None, reason: str | None = None, note: str | None = None,
           source_type: str = "conversation") -> dict:
    allowed = {"present": ("chose", "not_now"), "final": ("accepted", "declined")}
    if decision not in allowed.get(stage, ()):
        raise ValueError(f"{stage}: decision must be one of {', '.join(allowed.get(stage, ()))}")
    if decision in ("not_now", "declined"):
        if reason not in REASONS:
            raise ValueError("Pick the reason the owner gave")
        if reason == "other" and not (note or "").strip():
            raise ValueError("Say what the reason was")
        if stage == "present":
            carrier = tier = None
    if stage == "present" and decision == "chose":
        offered = conn.execute("SELECT 1 FROM indications WHERE client_id=%s AND carrier=%s AND tier=%s",
                               (cid, carrier, tier)).fetchone()
        if not offered:
            raise ValueError(f"{carrier} has no written, checked offer for {OPTION.get(tier, {}).get('label', tier)}")
        reason = None
    if stage == "final":
        q = current_quote(conn, cid)
        if not q:
            raise ValueError("No firm quote yet")
        if q["review"] not in ("verified", "confirmed"):
            raise ValueError("Check the firm quote's figures against the PDF first")
        carrier, tier = q["carrier"], q["tier"]
        if decision == "accepted":
            reason = None
    conn.execute("""INSERT INTO client_decisions (client_id, stage, decision, carrier, tier, reason, note, source_type, actor_id)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                 (cid, stage, decision, carrier, tier, reason, (note or "").strip() or None, source_type, actor_id))
    return latest_decision(conn, cid, stage)


def latest_decision(conn, cid: int, stage: str) -> dict | None:
    d = conn.execute("""SELECT d.*, u.name AS actor_name FROM client_decisions d JOIN users u ON u.id=d.actor_id
                        WHERE client_id=%s AND stage=%s ORDER BY d.id DESC LIMIT 1""", (cid, stage)).fetchone()
    if d:
        d["reason_label"] = REASONS.get(d["reason"])
        d["option_label"] = OPTION.get(d["tier"], {}).get("label")
    return d


# --- firm quote in ---------------------------------------------------------------------------

QUOTE_SYSTEM = ix.SYSTEM + """
This document is a FIRM QUOTE (bindable), not an indication. Also return:
 "follows_indication": str|null, "effective_date": "YYYY-MM-DD"|null, "expiration_date": "YYYY-MM-DD"|null
 (the policy period as written), "premium_reason": str|null (the carrier's stated reason for the premium, verbatim).
Put every subjectivity in "conditions" exactly as written, including any "before binding" / "within N days" wording."""


def quote_dir(slug: str) -> Path:
    return RAW / slug / "quotes"


def quote_inbox(conn, cid: int, slug: str) -> list[str]:
    done = {r["path"] for r in conn.execute("SELECT path FROM firm_quotes WHERE client_id=%s", (cid,)).fetchall()}
    return [str(p.relative_to(WIKI)) for p in sorted(quote_dir(slug).glob("*"))
            if p.suffix in (".pdf", ".md") and str(p.relative_to(WIKI)) not in done]


def _extract(p: Path, text: str, slug: str) -> tuple[dict, str]:
    out = llm.complete_json(QUOTE_SYSTEM, f"Source file: {p.name}\n\n<source>\n{text}\n</source>", max_tokens=3000,
                            label=f"firm quote extraction ({p.name})")
    if out and out.get("options"):
        return out, "live"
    cache = RAW / "_cache" / f"quote_extraction_{slug}_{p.stem}.md"
    if cache.exists():
        return read_source(cache), "cached"
    raise ValueError(f"No cached extraction for {p.name}. Set ANTHROPIC_API_KEY to extract it live.")


_DUE = re.compile(r"within\s+(\d+)\s+days", re.I)


def _timing(text: str) -> tuple[str, int | None]:
    m = _DUE.search(text)
    if m and "bind" in text.lower():
        return "after", int(m.group(1))
    return "before", None


def current_quote(conn, cid: int) -> dict | None:
    return conn.execute("""SELECT q.*, u.name AS reviewed_by_name FROM firm_quotes q LEFT JOIN users u ON u.id=q.reviewed_by
                           WHERE client_id=%s ORDER BY q.id DESC LIMIT 1""", (cid,)).fetchone()


def ingest_quote(conn, cid: int, path: str | Path, actor_id: int) -> dict:
    p = indications._resolve(path)
    rel = str(p.relative_to(WIKI))
    if conn.execute("SELECT 1 FROM firm_quotes WHERE client_id=%s AND path=%s", (cid, rel)).fetchone():
        return {"skipped": True, "path": rel}
    c = conn.execute("SELECT * FROM clients WHERE id=%s", (cid,)).fetchone()
    chosen = latest_decision(conn, cid, "present")
    if not chosen or chosen["decision"] != "chose":
        raise ValueError("Record which option the owner chose (Stage 6, step 1) before taking in a firm quote")
    legal = conn.execute("SELECT current_value FROM fields WHERE client_id=%s AND key='legal_name'", (cid,)).fetchone()
    names = [n for n in [legal and legal["current_value"], c["display_name"]] if n]

    text = ix.source_text(p)
    ext, provenance = _extract(p, text, c["slug"])
    ext["carrier"] = ix.canonical_carrier(ext.get("carrier"), [x["carrier"] for x in indications.panel()])
    if len(ext.get("options") or []) != 1:
        raise ValueError("A firm quote should quote exactly one option")
    o = ext["options"][0]
    tier = indications._tier_for(o["limit"])
    if (ext["carrier"], tier) != (chosen["carrier"], chosen["tier"]):
        raise ValueError(f"This quote is {ext['carrier']} {OPTION.get(tier, {}).get('label', o['limit'])}; the owner "
                         f"chose {chosen['carrier']} {chosen['option_label']}")
    checks = ix.check_numbers(ext, text, names)
    flat = " ".join(text.split()).lower()
    for field in ("effective_date", "expiration_date"):
        if ext.get(field):
            ok = any(f.lower() in flat for f in ix._date_forms(date.fromisoformat(ext[field])))
            checks.append({"scope": "carrier", "field": field, "value": ext[field], "found": ok,
                           "note": None if ok else f"{field.replace('_', ' ').capitalize()} isn't written in the source"})
    fails = ix.failures_for(checks, o["limit"])

    prev = conn.execute("""SELECT * FROM indication_versions WHERE client_id=%s AND carrier=%s AND tier=%s
                           AND trust='written' AND status='indicated' ORDER BY version_no DESC LIMIT 1""",
                        (cid, ext["carrier"], tier)).fetchone()
    new = {"status": "indicated", "trust": "written", "premium": o.get("premium"), "limit_amount": o["limit"],
           "deductible": o["deductible"], "sublimits": o.get("sublimits") or {}, "conditions": ext.get("conditions") or [],
           "bi_waiting_hours": ext.get("bi_waiting_period_hours"), "specimen_form": ext.get("specimen_form"),
           "expires_on": ext.get("expires_on")}
    # Conditions are compared by what they require (keywords → application question), not by wording:
    # a carrier rephrasing "MFA on email" isn't a new condition. Conditions are listed separately with that flag.
    changes = [ch for ch in indications._diff(prev, new)
               if ch["field"] not in ("expires_on", "condition_added", "condition_removed")]
    prior_keys = {k for t in (prev["conditions"] if prev else []) for k in indications.condition_keys(t)}
    qid = conn.execute("""INSERT INTO firm_quotes (client_id, carrier, tier, path, doc_date, reference, extractor, extraction,
                          checks, review, limit_amount, deductible, premium, sublimits, bi_waiting_hours, specimen_form,
                          expires_on, effective_date, expiration_date, premium_reason, compared_to, changes, ingested_by)
                          VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id""",
                       (cid, ext["carrier"], tier, rel, ext["document_date"], ext.get("reference"), provenance, j(ext),
                        j(checks), "pending_review" if fails else "verified", o["limit"], o["deductible"], o.get("premium"),
                        j(new["sublimits"]), new["bi_waiting_hours"], new["specimen_form"], ext.get("expires_on"),
                        ext.get("effective_date"), ext.get("expiration_date"), ext.get("premium_reason"),
                        prev["id"] if prev else None, j(changes), actor_id)).fetchone()["id"]
    for t in ext.get("conditions") or []:
        timing, due = _timing(t)
        st = indications.condition_status(conn, cid, t)
        keys = set(indications.condition_keys(t))
        conn.execute("""INSERT INTO bind_conditions (client_id, quote_id, text, timing, due_days, intake_status, is_new)
                        VALUES (%s,%s,%s,%s,%s,%s,%s)""",
                     (cid, qid, t, timing, due, st["status"], not keys or not keys <= prior_keys))
    return {"path": rel, "carrier": ext["carrier"], "tier": tier, "premium": o.get("premium"), "extractor": provenance,
            "changes": len(changes), "failed_checks": fails}


def review_quote(conn, cid: int, actor_id: int, decision: str, note: str | None) -> dict:
    q = current_quote(conn, cid)
    if not q or q["review"] != "pending_review":
        raise ValueError("Nothing to review")
    if decision not in ("confirmed", "rejected"):
        raise ValueError("decision must be confirmed or rejected")
    if decision == "rejected" and not (note or "").strip():
        raise ValueError("Say why (the note is logged with your name)")
    conn.execute("UPDATE firm_quotes SET review=%s, reviewed_by=%s, reviewed_at=now(), review_note=%s WHERE id=%s",
                 (decision, actor_id, note, q["id"]))
    return {"review": decision}


# --- bind ------------------------------------------------------------------------------------

def set_condition(conn, cid: int, cond_id: int, actor_id: int, met: bool, evidence: str | None) -> dict:
    if met and not (evidence or "").strip():
        raise ValueError("Say what shows it's met (e.g. 'MSP screenshot of MFA policy, emailed 12/8')")
    if conn.execute("SELECT 1 FROM binders WHERE client_id=%s", (cid,)).fetchone():
        b = conn.execute("SELECT timing FROM bind_conditions WHERE id=%s", (cond_id,)).fetchone()
        if b and b["timing"] == "before":
            raise ValueError("Already bound: before-binding conditions can't be reopened")
    r = conn.execute("""UPDATE bind_conditions SET status=%s, evidence=%s, met_by=%s,
                        met_at=CASE WHEN %s THEN now() END WHERE id=%s AND client_id=%s RETURNING id""",
                     ("met" if met else "open", (evidence or "").strip() or None, actor_id if met else None,
                      met, cond_id, cid)).fetchone()
    if not r:
        raise LookupError("no such condition")
    return {"ok": True}


def _policy_number(carrier: str, qid: int) -> str:
    initials = "".join(w[0] for w in carrier.split()[:2]).upper()
    return f"{initials}-CY-27-{10000 + qid}"


def bind(conn, cid: int, actor_id: int) -> dict:
    if conn.execute("SELECT 1 FROM binders WHERE client_id=%s", (cid,)).fetchone():
        raise ValueError("Already bound")
    q = current_quote(conn, cid)
    blockers = bind_blockers(conn, cid, q)
    if blockers:
        raise ValueError("Can't bind yet: " + "; ".join(blockers))
    eff = q["effective_date"] or date.today()
    exp = q["expiration_date"] or eff.replace(year=eff.year + 1)
    conn.execute("""INSERT INTO binders (client_id, quote_id, policy_number, effective_date, expiration_date, premium, bound_by)
                    VALUES (%s,%s,%s,%s,%s,%s,%s)""",
                 (cid, q["id"], _policy_number(q["carrier"], q["id"]), eff, exp, q["premium"], actor_id))
    conn.execute("UPDATE clients SET stage='bound' WHERE id=%s", (cid,))
    return conn.execute("SELECT * FROM binders WHERE client_id=%s", (cid,)).fetchone()


def bind_blockers(conn, cid: int, q: dict | None) -> list[str]:
    if not q:
        return ["no firm quote"]
    out = []
    if q["review"] not in ("verified", "confirmed"):
        out.append("check the firm quote against the PDF")
    final = latest_decision(conn, cid, "final")
    if not final or final["decision"] != "accepted":
        out.append("the owner hasn't accepted the final terms")
    n = conn.execute("""SELECT count(*) AS n FROM bind_conditions WHERE quote_id=%s AND timing='before' AND status<>'met'""",
                     (q["id"],)).fetchone()["n"]
    if n:
        out.append(f"{n} before-binding condition{'s' if n != 1 else ''} not marked met")
    open_app = conn.execute("""SELECT count(*) AS n FROM application_answers WHERE client_id=%s AND status<>'confirmed'""",
                            (cid,)).fetchone()["n"]
    if open_app:
        out.append(f"{open_app} application answer{'s' if open_app != 1 else ''} not confirmed (the client signs a "
                   "complete application)")
    return out


# --- report: after-bind plan ------------------------------------------------------------------

CONTROL_KEYS = {"mfa_email", "mfa_remote", "backups", "edr", "phishing_training", "payment_verify"}
OWNER_NOTE = ("Owners are proposed. Who actually owns each touchpoint (agent, UKON or carrier) is an open question for "
              "UKON (interview question #10).")


def plan(conn, cid: int) -> dict:
    """The 30-60-90 after bind and the touchpoints through the year. Built from the binder (or the quote's dates
    before binding), the open conditions, the application's weak spots and the exposure findings."""
    b = conn.execute("SELECT * FROM binders WHERE client_id=%s", (cid,)).fetchone()
    q = current_quote(conn, cid)
    if not b and not q:
        return {"draft": True, "items": [], "start": None, "renewal": None, "owner_note": OWNER_NOTE}
    start = b["effective_date"] if b else (q["effective_date"] or date.today())
    end = b["expiration_date"] if b else (q["expiration_date"] or start.replace(year=start.year + 1))
    items = []

    def add(day, owner, what, why, kind="touchpoint"):
        items.append({"day": day, "date": (start + timedelta(days=day)).isoformat(), "owner": owner, "what": what,
                      "why": why, "kind": kind})

    add(0, "Agent", "Welcome call: walk the owner and office manager through the one-page summary; save the incident steps "
        "where staff can find them", "Coverage is only useful if staff know the first call to make")
    add(7, "Carrier", "Carrier onboarding: policyholder portal and any included security services switched on",
        "Many cyber carriers include services the client never activates; confirm what this carrier offers")
    if q:
        for c in conn.execute("SELECT * FROM bind_conditions WHERE quote_id=%s AND timing='after' ORDER BY id",
                              (q["id"],)).fetchall():
            due = c["due_days"] or 60
            add(max(due - 30, 14), "Agent", f"Check progress: {c['text'].split(':', 1)[-1].strip()}",
                f"Carrier condition due day {due}; missing it can mean cancellation", "condition")
            add(due, "Client", f"Due: {c['text'].split(':', 1)[-1].strip()} (send evidence to the carrier)",
                "Post-binding subjectivity on the firm quote", "deadline")
    covered = {k for c in (conn.execute("SELECT text FROM bind_conditions WHERE quote_id=%s", (q["id"],)).fetchall() if q else [])
               for k in indications.condition_keys(c["text"])}
    weak = conn.execute("""SELECT question_key, question, normalized FROM application_answers WHERE client_id=%s
                           AND normalized IN ('partial','no') AND question_key = ANY(%s)""",
                        (cid, list(CONTROL_KEYS - covered))).fetchall()
    for w in weak:
        add(45, "Agent", f"Follow up on a weak spot from the application: {w['question']} (answered "
            f"'{w['normalized']}')", "Fixing it before renewal can lower next year's premium", "control")
    expo = conn.execute("SELECT current_value FROM fields WHERE client_id=%s AND key='exposure_breakdown'", (cid,)).fetchone()
    for f in (expo["current_value"]["factors"] if expo else []):
        if "DMARC" in f["label"]:
            add(60, "Client", "Add a DMARC record to the practice's email domain (with the IT provider)",
                f"Exposure finding: {f['label']}", "control")
    add(90, "Agent", "First quarterly check-in (15 minutes): any incidents, new staff, new vendors or IT provider, "
        "new location, revenue change?", "Mid-term changes can need a policy update; it also keeps the renewal file current")
    add(180, "Agent", "Mid-year check-in: same questions; confirm the controls the carrier relied on are still in place",
        "The application is the client's representation all year")
    days = (end - start).days
    add(days - 120, "UKON", "Renewal prep: pre-fill next year's application from this year's confirmed answers; ask only "
        "what changed", "Renewal is re-underwriting: the carrier asks again", "renewal")
    add(days - 90, "UKON", "Renewal submission to the carrier (and others if the terms moved)", "Gives time for a firm quote",
        "renewal")
    add(days - 60, "Agent", "Present renewal terms; compare with this year's", "Owner decides with time to spare", "renewal")
    add(days - 30, "Agent", "Bind the renewal", "No lapse in coverage", "renewal")
    items.sort(key=lambda x: x["day"])
    buckets = [("First 30 days", 0, 30), ("Days 31–60", 31, 60), ("Days 61–90", 61, 90),
               ("Rest of the year", 91, days - 121), ("Renewal", days - 120, days)]
    return {"draft": not b, "start": start.isoformat(), "renewal": end.isoformat(), "owner_note": OWNER_NOTE,
            "items": items,
            "buckets": [{"label": l, "items": [i for i in items if lo <= i["day"] <= hi]} for l, lo, hi in buckets]}


# --- report: client summary + deal record ----------------------------------------------------

def _plain_condition(c: dict) -> str:
    """The carrier's subjectivity, reworded for the owner: what has to be true, and by when."""
    t = re.sub(r"^(before binding|within \d+ days of binding):\s*", "", c["text"], flags=re.I)
    t = re.sub(r"^written confirmation that\s+", "", t, flags=re.I)
    t = t[0].upper() + t[1:]
    return t + (" (confirmed before coverage started)" if c["timing"] == "before" else f" (due within {c['due_days']} days of the start date)")


def client_summary(conn, cid: int) -> dict | None:
    b = conn.execute("SELECT * FROM binders WHERE client_id=%s", (cid,)).fetchone()
    q = current_quote(conn, cid)
    if not q:
        return None
    c = conn.execute("SELECT * FROM clients WHERE id=%s", (cid,)).fetchone()
    conds = conn.execute("SELECT * FROM bind_conditions WHERE quote_id=%s ORDER BY id", (q["id"],)).fetchall()
    keep = conn.execute("""SELECT question FROM application_answers WHERE client_id=%s AND normalized='yes'
                           AND question_key IN ('mfa_remote','mfa_email','backups','edr','payment_verify')""",
                        (cid,)).fetchall()
    return {"bound": bool(b), "client": c["display_name"], "carrier": q["carrier"], "option": OPTION[q["tier"]]["label"],
            "policy_number": b["policy_number"] if b else None, "simulated": bool(b and b["simulated"]),
            "premium": q["premium"], "limit": q["limit_amount"], "deductible": q["deductible"], "sublimits": q["sublimits"],
            "bi_waiting_hours": q["bi_waiting_hours"], "specimen_form": q["specimen_form"],
            "effective_date": _iso(b["effective_date"] if b else q["effective_date"]),
            "expiration_date": _iso(b["expiration_date"] if b else q["expiration_date"]),
            "conditions": [{"text": _plain_condition(x), "timing": x["timing"], "status": x["status"]} for x in conds],
            "controls": [k["question"] for k in keep],
            "incident_steps": ["Call your agent and the carrier's breach line (printed on your policy declarations) "
                               "before anything else.",
                               "Don't wipe or rebuild computers, and don't pay or answer a ransom demand, until the "
                               "carrier's response team says so: evidence matters for the claim.",
                               "Write down what happened and when; keep any suspicious emails."],
            "coverage_note": "Whether a specific event would be covered is answered by the policy wording and a "
                             "specialist (CPL), not this summary."}


def _ts(conn, sql, args):
    r = conn.execute(sql, args).fetchone()
    return list(r.values())[0] if r else None


def deal_record(conn, cid: int) -> dict:
    milestones = [
        ("Indications requested", "SELECT min(sent_at) FROM indication_requests WHERE client_id=%s"),
        ("First written indication in", "SELECT min(ingested_at) FROM indication_sources WHERE client_id=%s AND channel<>'call'"),
        ("Proposal pack submitted", "SELECT min(submitted_at) FROM report_versions WHERE client_id=%s"),
        ("Pack sent to client", "SELECT min(sent_at) FROM report_versions WHERE client_id=%s"),
        ("First call with the owner", "SELECT min(ingested_at) FROM intake_calls WHERE client_id=%s"),
        ("Owner chose an option", "SELECT max(created_at) FROM client_decisions WHERE client_id=%s AND stage='present' AND decision='chose'"),
        ("Application answers all confirmed", "SELECT CASE WHEN bool_and(status='confirmed') THEN max(confirmed_at) END FROM application_answers WHERE client_id=%s"),
        ("Firm quote in", "SELECT min(ingested_at) FROM firm_quotes WHERE client_id=%s"),
        ("Final terms accepted", "SELECT max(created_at) FROM client_decisions WHERE client_id=%s AND stage='final' AND decision='accepted'"),
        ("Bound", "SELECT bound_at FROM binders WHERE client_id=%s"),
    ]
    rows = [{"label": l, "at": _ts(conn, sql, (cid,))} for l, sql in milestones]
    q = current_quote(conn, cid)
    ind = conn.execute("SELECT * FROM indication_versions WHERE id=%s", (q["compared_to"],)).fetchone() if q and q["compared_to"] else None
    present, final = latest_decision(conn, cid, "present"), latest_decision(conn, cid, "final")
    b = conn.execute("SELECT * FROM binders WHERE client_id=%s", (cid,)).fetchone()
    if b:
        outcome = {"status": "bound", "text": f"Bound with {q['carrier']}, {OPTION[q['tier']]['label']}, {_money(b['premium'])}/yr"}
    elif present and present["decision"] == "not_now":
        outcome = {"status": "lost", "text": f"Not now at presentation: {present['reason_label']}"
                   + (f" ({present['note']})" if present["note"] else "")}
    elif final and final["decision"] == "declined":
        outcome = {"status": "lost", "text": f"Declined the firm quote: {final['reason_label']}"
                   + (f" ({final['note']})" if final["note"] else "")}
    else:
        outcome = {"status": "open", "text": "Open"}
    people = conn.execute("""SELECT actor, role, count(*) AS n FROM audit_trail WHERE client_id=%s AND role<>'system'
                             GROUP BY actor, role ORDER BY n DESC""", (cid,)).fetchall()
    sources = [r["path"] for r in conn.execute("SELECT path FROM indication_sources WHERE client_id=%s ORDER BY doc_date", (cid,))]
    sources += [r["wiki_path"] for r in conn.execute("SELECT wiki_path FROM intake_calls WHERE client_id=%s ORDER BY id", (cid,))]
    sources += [r["path"] for r in conn.execute("SELECT path FROM firm_quotes WHERE client_id=%s", (cid,))]
    return {"outcome": outcome, "milestones": rows, "people": people, "sources": sources,
            "price": {"indication": ind["premium"] if ind else None,
                      "indication_ref": f"{ind['carrier']} v{ind['version_no']}" if ind else None,
                      "quote": q["premium"] if q else None,
                      "reason": q["premium_reason"] if q else None},
            "decisions": [d for d in (present, final) if d]}


# --- read model --------------------------------------------------------------------------------

def state(conn, cid: int) -> dict:
    c = conn.execute("SELECT * FROM clients WHERE id=%s", (cid,)).fetchone()
    q = current_quote(conn, cid)
    if q:
        for k in ("doc_date", "expires_on", "effective_date", "expiration_date"):
            q[k] = _iso(q[k])
        q["option_label"] = OPTION[q["tier"]]["label"]
        q["failed_checks"] = [x["note"] for x in q["checks"] if not x["found"]]
        ind = conn.execute("""SELECT v.*, s.path, s.doc_date FROM indication_versions v JOIN indication_sources s ON s.id=v.source_id
                              WHERE v.id=%s""", (q["compared_to"],)).fetchone() if q["compared_to"] else None
        if ind:
            ind["doc_date"], ind["expires_on"] = _iso(ind["doc_date"]), _iso(ind["expires_on"])
        q["indication"] = ind
    conds = conn.execute("""SELECT bc.*, u.name AS met_by_name FROM bind_conditions bc LEFT JOIN users u ON u.id=bc.met_by
                            WHERE bc.quote_id=%s ORDER BY bc.timing DESC, bc.id""", (q["id"],)).fetchall() if q else []
    b = conn.execute("""SELECT b.*, u.name AS bound_by_name FROM binders b JOIN users u ON u.id=b.bound_by
                        WHERE client_id=%s""", (cid,)).fetchone()
    if b:
        b["effective_date"], b["expiration_date"] = _iso(b["effective_date"]), _iso(b["expiration_date"])
    offers = conn.execute("SELECT carrier, tier, premium, expired FROM indications WHERE client_id=%s ORDER BY tier DESC, premium",
                          (cid,)).fetchall()
    for o in offers:
        o["option_label"] = OPTION[o["tier"]]["label"]
    selected = conn.execute("SELECT current_value FROM fields WHERE client_id=%s AND key='selected_carrier'", (cid,)).fetchone()
    return {"reasons": REASONS, "offers": offers, "selected_carrier": selected and selected["current_value"],
            "present": latest_decision(conn, cid, "present"), "final": latest_decision(conn, cid, "final"),
            "quote": q, "conditions": conds, "binder": b, "blockers": bind_blockers(conn, cid, q) if q else [],
            "inbox": quote_inbox(conn, cid, c["slug"]), "summary": client_summary(conn, cid),
            "deal": deal_record(conn, cid), "plan": plan(conn, cid)}


def render_wiki(conn, cid: int) -> str:
    c = conn.execute("SELECT * FROM clients WHERE id=%s", (cid,)).fetchone()
    s = state(conn, cid)
    out = ["---", "type: client-bind", "generated: true", f"client_id: {cid}", "---", "",
           f"# {c['display_name']} — decision, final terms, bind", "",
           "> [!warning] Generated page — do not edit in Obsidian", "> Rendered from the database after every Stage 6 change.", ""]
    for label, d in (("Presentation", s["present"]), ("Final terms", s["final"])):
        if d:
            out.append(f"- **{label}:** {d['decision']}" + (f" — {d['carrier']} {d['option_label']}" if d["carrier"] else "")
                       + (f" — reason: {d['reason_label']}" if d["reason"] else "") + f" ({d['actor_name']}, {d['created_at']:%Y-%m-%d})")
    q = s["quote"]
    if q:
        out += ["", "## Firm quote", "",
                f"- {q['carrier']} {q['option_label']}: **{_money(q['premium'])}** · review `{q['review']}` · [[{q['path']}|source]]"]
        if q["indication"]:
            out.append(f"- Compared with indication v{q['indication']['version_no']}: {_money(q['indication']['premium'])}")
        for ch in q["changes"]:
            out.append(f"  - {ch['label']}: {_money(ch['old']) if ch['old'] is not None else '—'} → "
                       f"{_money(ch['new']) if ch['new'] is not None else '—'}")
        out += ["", "## Conditions", ""] + [f"- [{'x' if x['status'] == 'met' else ' '}] ({x['timing']}) {x['text']}"
                                            + (f" — {x['evidence']}" if x["evidence"] else "") for x in s["conditions"]]
    if s["binder"]:
        b = s["binder"]
        out += ["", "## Bound", "", f"- Policy {b['policy_number']} ({'simulated' if b['simulated'] else 'carrier binder'}), "
                f"{b['effective_date']} to {b['expiration_date']}, {_money(b['premium'])}"]
    if s["plan"]["items"]:
        out += ["", "## After-bind plan" + (" (draft)" if s["plan"]["draft"] else ""), ""]
        out += [f"- Day {i['day']} ({i['date']}) · {i['owner']} · {i['what']}" for i in s["plan"]["items"]]
    text = "\n".join(out) + "\n"
    (WIKI / "clients" / f"{c['slug']}-bind.md").write_text(text)
    return text


def ingest_file(path: str, slug: str = CLIENT_SLUG, actor: str = "Pipeline (AI)") -> dict:
    with connect() as conn:
        cid = client_by_slug(conn, slug)["id"]
        res = ingest_quote(conn, cid, path, user_id(conn, actor))
        render_wiki(conn, cid)
    if not res.get("skipped"):
        wiki_render.log(f"firm quote | {slug} — {res['carrier']} {res['tier']} {_money(res['premium'])} ({res['extractor']})")
    print(res)
    return res


if __name__ == "__main__":
    ingest_file(sys.argv[1])
