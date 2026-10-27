"""Stage 1 — the agent <-> carrier exchange.

Outbound: request indications from each carrier on the panel, with the five fields as a basis
snapshot (what exactly did we send, and was it reviewed?).

Inbound: carriers reply however they reply (PDF letter, email, a call with the underwriter captured
by Wispr Flow). Each reply is a raw source in the wiki; ingest() extracts it, checks every figure
against the source text, and appends a new version per carrier + option. Nothing is overwritten:
the history shows what each carrier said, when, and what changed. Changes become actions for the agent
by fixed rules (new condition, price moved, declined, verbal-only, figure to confirm).

    uv run python -m pipeline.indications                       # demo seed: requests + first replies
(The app no longer shows the carrier exchange; the client pack reads its result through the `indications` view.)
    uv run python -m pipeline.indications <reply.pdf|.md>       # ingest one carrier reply"""
import sys
from datetime import date
from pathlib import Path

from . import indication_extract as ix
from . import wiki_render
from .config import (CLIENT_SLUG, CONDITION_KEYS, INDICATION_EXPIRY_WARN_DAYS, RAW, REQUESTED_OPTIONS, REVENUE_DRIFT_TOLERANCE,
                     ROOT, WIKI)
from .db import client_by_slug, connect, j, user_id
from .sources import read_source

BASIS_KEYS = ["legal_name", "domain", "industry", "annual_revenue", "address"]
OPTION = {o["tier"]: o for o in REQUESTED_OPTIONS}

# Replies that exist when the demo starts (run_all). The Northwind revision is left for the live demo.
# Northwind's revised letter is left in the inbox for a live ingest.
SEED_REPLIES = ["2026-10-27_northwind_indication.pdf", "2026-10-28_cobalt_harbor_email.md",
                "2026-10-28_ridgeline_underwriter_call.md", "2026-10-30_ridgeline_indication.pdf"]
INPUT_LABEL = {"conversation": "Conversation (Wispr Flow)", "clipboard": "Copied from clipboard",
               "api": "Carrier API", "file": "File saved to the wiki", "manual": "Typed in by hand"}


def _money(v):
    return f"${v:,.0f}" if isinstance(v, (int, float)) else str(v)


def inbox_dir(slug: str) -> Path:
    return RAW / slug / "indications"


# --- outbound ------------------------------------------------------------------

def basis_snapshot(conn, cid: int) -> dict:
    f = {r["key"]: r for r in conn.execute("SELECT * FROM fields WHERE client_id=%s", (cid,)).fetchall()}
    confirmed = conn.execute("SELECT 1 FROM entity_candidates WHERE client_id=%s AND status='confirmed'",
                             (cid,)).fetchone() is not None
    return {"entity_confirmed": confirmed,
            "fields": {k: {"label": f[k]["label"], "value": f[k]["current_value"], "confidence": f[k]["confidence"],
                           "needs_review": f[k]["needs_review"]} for k in BASIS_KEYS if k in f}}


def unreviewed(basis: dict) -> list[str]:
    out = [] if basis["entity_confirmed"] else ["entity match"]
    return out + [v["label"] for v in basis["fields"].values() if v["needs_review"]]


def request_all(conn, cid: int, actor_id: int, reason: str, gate: bool = True) -> int:
    """Send (record) a request to every carrier on the panel. With gate=True the five fields must be
    reviewed first; the demo seed passes gate=False and says so in the reason."""
    basis = basis_snapshot(conn, cid)
    if gate and unreviewed(basis):
        raise ValueError("Review before sending: " + ", ".join(unreviewed(basis)))
    panel = read_source(RAW / "carriers" / "carrier_panel.md")["carriers"]
    for c in panel:
        conn.execute("""INSERT INTO indication_requests (client_id, carrier, channel, options, basis, reason, sent_by)
                        VALUES (%s,%s,%s,%s,%s,%s,%s)""",
                     (cid, c["carrier"], c["request_channel"], j(REQUESTED_OPTIONS), j(basis), reason, actor_id))
    conn.execute("UPDATE clients SET stage='indications' WHERE id=%s AND stage='enrichment'", (cid,))
    return len(panel)


# --- inbound -------------------------------------------------------------------

def _tier_for(limit: int) -> str | None:
    return next((o["tier"] for o in REQUESTED_OPTIONS if o["limit"] == limit), None)


def condition_keys(text: str) -> list[str]:
    t = text.lower()
    return [key for words, key in CONDITION_KEYS if any(w in t for w in words)]


def condition_status(conn, cid: int, text: str) -> dict:
    """Is this carrier condition met, per the intake? Worst status across the answers it maps to."""
    keys = condition_keys(text)
    if not keys:
        return {"keys": [], "status": "unknown", "label": "Not covered by the intake: ask the client"}
    rows = {r["question_key"]: r for r in conn.execute(
        "SELECT question_key, status, normalized FROM application_answers WHERE client_id=%s AND question_key = ANY(%s)",
        (cid, keys)).fetchall()}
    rank = {"met": 0, "to_confirm": 1, "unknown": 2, "gap": 3}
    worst = "met"
    for k in keys:
        r = rows.get(k)
        if not r or r["status"] == "unanswered":
            s = "unknown"
        elif r["normalized"] == "yes" and r["status"] in ("confirmed", "prefilled"):
            s = "met"
        elif r["normalized"] == "no":
            s = "gap"
        else:
            s = "to_confirm"
        worst = max(worst, s, key=rank.get)
    label = {"met": "Met per intake", "to_confirm": "Intake answer to confirm",
             "unknown": "Not asked yet", "gap": "Not in place per intake"}[worst]
    return {"keys": keys, "status": worst, "label": label}


def _diff(prev: dict | None, new: dict) -> list[dict]:
    if not prev:
        return []
    out = []
    # After a phone call, only compare what was actually said: the letter fills in the rest.
    from_verbal = prev.get("trust") == "verbal"
    fields = [("status", "Status"), ("premium", "Premium"), ("limit_amount", "Limit"), ("deductible", "Deductible")]
    if not from_verbal:
        fields += [("bi_waiting_hours", "BI waiting period (hours)"), ("expires_on", "Valid until"),
                   ("specimen_form", "Policy form")]
    for field, label in fields:
        a, b = prev.get(field), new.get(field)
        a = a.isoformat() if isinstance(a, date) else a
        b = b.isoformat() if isinstance(b, date) else b
        if b is not None and a != b:
            out.append({"field": field, "label": label, "old": a, "new": b})
    for k in set(prev.get("sublimits") or {}) | set(new.get("sublimits") or {}):
        a, b = (prev.get("sublimits") or {}).get(k), (new.get("sublimits") or {}).get(k)
        if b is not None and a != b:
            out.append({"field": f"sublimit.{k}", "label": f"{k.replace('_', ' ').capitalize()} sublimit",
                        "old": a, "new": b})
    old_c, new_c = list(prev.get("conditions") or []), list(new.get("conditions") or [])
    if from_verbal or (new.get("trust") == "verbal" and not new_c):
        old_c = new_c
    for c in new_c:
        if c not in old_c:
            out.append({"field": "condition_added", "label": "New condition", "old": None, "new": c})
    for c in old_c:
        if c not in new_c:
            out.append({"field": "condition_removed", "label": "Condition dropped", "old": c, "new": None})
    if prev.get("trust") != new.get("trust"):
        out.append({"field": "trust", "label": "Now in writing" if new["trust"] == "written" else "Verbal update",
                    "old": prev.get("trust"), "new": new["trust"]})
    return out


def _action(conn, cid, carrier, version_id, kind, text):
    conn.execute("INSERT INTO indication_actions (client_id, carrier, version_id, kind, text) VALUES (%s,%s,%s,%s,%s)",
                 (cid, carrier, version_id, kind, text))


def _close_actions(conn, cid, carrier, kind, actor_id, note, version_id=None):
    conn.execute(f"""UPDATE indication_actions SET status='done', closed_by=%s, closed_at=now(), close_note=%s
                     WHERE client_id=%s AND carrier=%s AND kind=%s AND status='open'
                     {'AND version_id=%s' if version_id else ''}""",
                 (actor_id, note, cid, carrier, kind) + ((version_id,) if version_id else ()))


def _resolve(path: str | Path) -> Path:
    p = Path(path)
    for cand in (p, ROOT / p, WIKI / p):
        if cand.exists():
            return cand.resolve()
    raise FileNotFoundError(path)


def ingest(conn, cid: int, path: str | Path, actor_id: int, input_by: int | None = None) -> dict:
    p = _resolve(path)
    rel = str(p.relative_to(WIKI))
    if conn.execute("SELECT 1 FROM indication_sources WHERE client_id=%s AND path=%s", (cid, rel)).fetchone():
        return {"skipped": True, "path": rel}
    c = conn.execute("SELECT * FROM clients WHERE id=%s", (cid,)).fetchone()
    legal = conn.execute("SELECT current_value FROM fields WHERE client_id=%s AND key='legal_name'",
                         (cid,)).fetchone()
    names = [n for n in [legal and legal["current_value"], c["display_name"]] if n]

    channel = ix.channel_of(p)
    method = ix.input_method_of(p, channel)
    text = ix.source_text(p)
    ext, provenance = ix.extract(p, text)
    verbal = channel == "call" or ext.get("firmness") == "verbal"
    checks = ix.check_numbers(ext, text, names, verbal)
    sha = ix.content_sha(text)
    src = conn.execute("""INSERT INTO indication_sources (client_id, carrier, channel, input_method, content_sha, path,
                          doc_date, reference, extractor, input_by, extraction, checks, ingested_by)
                          VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id""",
                       (cid, ext["carrier"], channel, method, sha, rel, ext["document_date"], ext.get("reference"),
                        provenance, input_by, j(ext), j(checks), actor_id)).fetchone()["id"]

    carrier, summary, first_vid = ext["carrier"], [], None
    sent_pack = conn.execute("""SELECT version_no FROM report_versions WHERE client_id=%s AND state IN ('submitted','sent')
                                ORDER BY version_no DESC LIMIT 1""", (cid,)).fetchone()
    for o in ext["options"]:
        tier = _tier_for(o["limit"])
        if not tier:
            _action(conn, cid, carrier, None, "terms_change",
                    f"{carrier} replied with an option we didn't request ({_money(o['limit'])} / "
                    f"{_money(o['deductible'])}). Not loaded; decide whether to request it.")
            continue
        prev = conn.execute("""SELECT * FROM indication_versions WHERE client_id=%s AND carrier=%s AND tier=%s
                               ORDER BY version_no DESC LIMIT 1""", (cid, carrier, tier)).fetchone()
        prev_written = conn.execute("""SELECT * FROM indication_versions WHERE client_id=%s AND carrier=%s AND tier=%s
                                       AND trust='written' ORDER BY version_no DESC LIMIT 1""",
                                    (cid, carrier, tier)).fetchone()
        fails = ix.failures_for(checks, o["limit"])
        review = "not_applicable" if verbal else ("pending_review" if fails else "verified")
        new = {"status": o["status"], "trust": "verbal" if verbal else "written", "premium": o.get("premium"),
               "limit_amount": o["limit"], "deductible": o["deductible"], "sublimits": o.get("sublimits") or {},
               "conditions": ext.get("conditions") or [], "bi_waiting_hours": ext.get("bi_waiting_period_hours"),
               "expires_on": ext.get("expires_on"), "specimen_form": ext.get("specimen_form")}
        changes = _diff(prev, new)
        vid = conn.execute("""INSERT INTO indication_versions (client_id, carrier, tier, version_no, status, trust, review,
                              limit_amount, deductible, premium, basis_revenue, sublimits, conditions, bi_waiting_hours,
                              specimen_form, expires_on, note, quote, hedged, source_id, changes)
                              VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id""",
                           (cid, carrier, tier, (prev["version_no"] + 1) if prev else 1, o["status"], new["trust"], review,
                            o["limit"], o["deductible"], o.get("premium"), ext.get("basis_revenue"), j(new["sublimits"]),
                            j(new["conditions"]), new["bi_waiting_hours"], new["specimen_form"], new["expires_on"],
                            o.get("note"), o.get("quote"), bool(o.get("hedged")), src, j(changes))).fetchone()["id"]
        first_vid = first_vid or vid
        label = OPTION[tier]["label"]

        # --- rules: what this reply means for the agent ---
        if review == "pending_review":
            where = {"pdf": "PDF", "clipboard": "pasted text", "api": "API response"}.get(channel, channel)
            _action(conn, cid, carrier, vid, "confirm_extraction",
                    f"Check {carrier} {label} against the {where}: " + "; ".join(fails) + ".")
        same_as_written = bool(prev_written and prev_written["premium"] == o.get("premium"))
        if verbal and o["status"] == "indicated" and not same_as_written:
            _action(conn, cid, carrier, vid, "get_in_writing",
                    f"{carrier} {label}: verbal only (about {_money(o.get('premium'))}"
                    + (", hedged" if o.get("hedged") else "") + "). Not shown to the client until it's in writing.")
        if not verbal:
            _close_actions(conn, cid, carrier, "get_in_writing", actor_id, f"Written indication received: {rel}")
        if o["status"] == "declined" and not (prev_written and prev_written["status"] == "declined"):
            if not verbal:   # a written decline replaces the verbal heads-up
                _close_actions(conn, cid, carrier, "declined", actor_id, f"Confirmed in writing: {rel}")
            _action(conn, cid, carrier, vid, "declined",
                    f"{carrier} declined {label}" + (f": {o['note'].rstrip('.')}" if o.get("note") else "")
                    + (" (verbal; expect it in writing)" if verbal else ". Offer this option from another carrier."))
        if not verbal and prev_written and o["status"] == "indicated":
            old, newp = prev_written["premium"], o.get("premium")
            if old and newp and old != newp:
                where = (f"Report v{sent_pack['version_no']} already went out with {_money(old)}: tell the client."
                         if sent_pack else "The working client pack now shows the new price.")
                _action(conn, cid, carrier, vid, "price_change",
                        f"{carrier} {label}: premium {_money(old)} → {_money(newp)} "
                        f"({(newp - old) / old:+.0%}). {where}")
            for ch in changes:
                if ch["field"].startswith("sublimit.") or ch["field"] in ("limit_amount", "deductible"):
                    _action(conn, cid, carrier, vid, "terms_change",
                            f"{carrier} {label}: {ch['label']} {_money(ch['old'])} → {_money(ch['new'])}.")
        summary.append(f"{label} {o['status']}" + (f" {_money(o.get('premium'))}" if o.get("premium") else "")
                       + f" [{review}]")

    # Conditions are carrier-wide: one action per newly added condition, with the intake's view of it.
    if not verbal:
        prior = conn.execute("""SELECT conditions FROM indication_versions WHERE client_id=%s AND carrier=%s
                                AND trust='written' AND source_id<>%s ORDER BY id DESC LIMIT 1""",
                             (cid, carrier, src)).fetchone()
        if prior:
            for cond in ext.get("conditions") or []:
                if cond not in prior["conditions"]:
                    st = condition_status(conn, cid, cond)
                    _action(conn, cid, carrier, first_vid, "new_condition",
                            f"{carrier} added a condition: \"{cond}\". Intake when received: {st['label'].lower()}.")

    _refresh_default_carrier(conn, cid, actor_id)
    return {"path": rel, "carrier": carrier, "channel": channel, "input_method": method, "extractor": provenance,
            "verbal": verbal,
            "options": summary, "failed_checks": [c["note"] for c in checks if not c["found"]]}


def pick_default_carrier(rows: list[dict]) -> str | None:
    """Rule, not model: cheapest $1M option that keeps ransomware at the full limit and hasn't expired."""
    ok = [(r["premium"], r["carrier"]) for r in rows
          if r["tier"] == "recommended" and r["sublimits"].get("ransomware") == "full limit" and not r["expired"]]
    return min(ok)[1] if ok else None


def _refresh_default_carrier(conn, cid: int, actor_id: int):
    from .stage1_enrich import upsert_field
    rows = conn.execute("SELECT * FROM indications WHERE client_id=%s", (cid,)).fetchall()
    default = pick_default_carrier(rows)
    if default:
        upsert_field(conn, cid, "selected_carrier", "Carrier shown to client", "text", default, confidence="high",
                     method="Default rule: lowest $1M premium that keeps ransomware at the full limit, from written, "
                            "checked indications. Agent may switch.",
                     sources=[f"{r['carrier']} v{r['version_no']}" for r in rows if r["tier"] == "recommended"],
                     actor=actor_id)
        # Follow the rule until a person picks a carrier; never override their choice.
        conn.execute("""UPDATE fields SET current_value=%s WHERE client_id=%s AND key='selected_carrier'
                        AND NOT EXISTS (SELECT 1 FROM field_changes fc WHERE fc.field_id=fields.id)""",
                     (j(default), cid))


# --- read model (API + wiki) ------------------------------------------------------------

def state(conn, cid: int, today: date | None = None) -> dict:
    today = today or date.today()
    c = conn.execute("SELECT * FROM clients WHERE id=%s", (cid,)).fetchone()
    reqs = conn.execute("""SELECT r.*, u.name AS sent_by_name FROM indication_requests r JOIN users u ON u.id=r.sent_by
                           WHERE client_id=%s ORDER BY sent_at""", (cid,)).fetchall()
    vers = conn.execute("""SELECT v.*, s.path, s.channel, s.input_method, s.doc_date, s.reference, s.extractor,
                                  u.name AS reviewed_by_name
                           FROM indication_versions v JOIN indication_sources s ON s.id=v.source_id
                           LEFT JOIN users u ON u.id=v.reviewed_by
                           WHERE v.client_id=%s ORDER BY v.carrier, v.tier, v.version_no""", (cid,)).fetchall()
    sources = conn.execute("""SELECT s.*, u.name AS ingested_by_name, ib.name AS input_by_name
                              FROM indication_sources s JOIN users u ON u.id=s.ingested_by
                              LEFT JOIN users ib ON ib.id=s.input_by
                              WHERE client_id=%s ORDER BY doc_date, id""", (cid,)).fetchall()
    for s_ in sources:
        s_["input_label"] = INPUT_LABEL[s_["input_method"]]
    actions = conn.execute("""SELECT a.*, u.name AS closed_by_name FROM indication_actions a
                              LEFT JOIN users u ON u.id=a.closed_by WHERE client_id=%s
                              ORDER BY (a.status='open') DESC, a.created_at DESC, a.id DESC""", (cid,)).fetchall()
    current = {(r["carrier"], r["tier"]): r for r in
               conn.execute("SELECT * FROM indications WHERE client_id=%s", (cid,)).fetchall()}
    revenue = conn.execute("SELECT current_value FROM fields WHERE client_id=%s AND key='annual_revenue'",
                           (cid,)).fetchone()
    selected = conn.execute("SELECT current_value FROM fields WHERE client_id=%s AND key='selected_carrier'",
                            (cid,)).fetchone()

    for v in vers:
        v["expires_on"] = v["expires_on"].isoformat() if v["expires_on"] else None
        v["doc_date"] = v["doc_date"].isoformat()
    carriers, alerts = [], []
    names = list(dict.fromkeys([r["carrier"] for r in reqs] + [v["carrier"] for v in vers]))
    for name in names:
        options = []
        for opt in REQUESTED_OPTIONS:
            hist = [v for v in vers if v["carrier"] == name and v["tier"] == opt["tier"]]
            written = [v for v in hist if v["trust"] == "written"]
            lw = written[-1] if written else None
            cur = current.get((name, opt["tier"]))
            if not hist:
                st = "awaiting"
            elif cur and cur["expired"]:
                st = "expired"
            elif cur:
                st = "offered"
            elif lw and lw["status"] == "declined":
                st = "declined"
            elif lw and lw["review"] == "pending_review":
                st = "pending_review"
            elif lw and lw["review"] == "rejected":
                st = "rejected"
            elif hist[-1]["status"] == "declined":
                st = "declined_verbal"
            else:
                st = "verbal_only"
            options.append({**opt, "state": st, "current_id": cur["id"] if cur else None, "history": hist})
        latest = next((v for v in reversed([v for v in vers if v["carrier"] == name and v["trust"] == "written"])), None) \
            or next((v for v in reversed([v for v in vers if v["carrier"] == name])), None)
        conds = [{"text": t, **condition_status(conn, cid, t)} for t in (latest["conditions"] if latest else [])]
        exp = latest["expires_on"] if latest and latest["trust"] == "written" else None
        if exp:
            days = (date.fromisoformat(exp) - today).days
            if days < 0:
                alerts.append({"carrier": name, "kind": "expired", "text": f"{name} indication expired {exp}. Re-request."})
            elif days <= INDICATION_EXPIRY_WARN_DAYS:
                alerts.append({"carrier": name, "kind": "expiring",
                               "text": f"{name} indication expires {exp} ({days} days)."})
        basis = next((v["basis_revenue"] for v in reversed(vers) if v["carrier"] == name and v["basis_revenue"]), None)
        if basis and revenue and revenue["current_value"]:
            drift = (float(revenue["current_value"]) - basis) / basis
            if abs(drift) > REVENUE_DRIFT_TOLERANCE:
                alerts.append({"carrier": name, "kind": "basis",
                               "text": f"{name} priced on {_money(basis)} revenue; we now have "
                                       f"{_money(revenue['current_value'])} ({drift:+.0%}). Re-request with the new basis."})
        req = [r for r in reqs if r["carrier"] == name]
        carriers.append({"carrier": name, "selected": selected and selected["current_value"] == name,
                         "request": req[-1] if req else None, "requests": len(req), "options": options,
                         "conditions": conds, "expires_on": exp, "basis_revenue": basis,
                         "sources": [s["path"] for s in sources if s["carrier"] == name]})
    ingested = {s["path"] for s in sources}
    inbox = [str(p.relative_to(WIKI)) for p in sorted(inbox_dir(c["slug"]).glob("*"))
             if p.suffix in (".pdf", ".md") and str(p.relative_to(WIKI)) not in ingested]
    last_basis = reqs[-1]["basis"] if reqs else None
    return {"requests": reqs, "basis": last_basis, "basis_unreviewed": unreviewed(last_basis) if last_basis else [],
            "current_basis_unreviewed": unreviewed(basis_snapshot(conn, cid)),
            "options": REQUESTED_OPTIONS, "carriers": carriers, "actions": actions, "alerts": alerts,
            "sources": sources, "inbox": inbox, "input_labels": INPUT_LABEL}


def render_wiki(conn, cid: int) -> str:
    c = conn.execute("SELECT * FROM clients WHERE id=%s", (cid,)).fetchone()
    s = state(conn, cid)
    out = ["---", "type: client-indications", "generated: true", f"client_id: {cid}", "---", "",
           f"# {c['display_name']} — carrier indications", "",
           "> [!warning] Generated page — do not edit in Obsidian",
           "> Rendered from the database after every carrier reply or review. Raw replies are linked below.", "",
           "## Requests sent", ""]
    for r in s["requests"]:
        out.append(f"- {r['sent_at']:%Y-%m-%d} — **{r['carrier']}** via {r['channel']} by {r['sent_by_name']} "
                   f"({r['reason']})")
    if s["basis"]:
        out += ["", "Basis sent:"] + [f"- {v['label']}: {_money(v['value'])}" + (" *(unreviewed)*" if v["needs_review"] else "")
                                      for v in s["basis"]["fields"].values()]
    out += ["", "## By carrier", ""]
    for car in s["carriers"]:
        out.append(f"### {car['carrier']}" + (" — shown to client" if car["selected"] else ""))
        for o in car["options"]:
            out.append(f"- **{o['label']}** — `{o['state']}`")
            for v in o["history"]:
                fig = _money(v["premium"]) if v["premium"] else v["status"]
                out.append(f"  - v{v['version_no']} {v['doc_date']} · {v['trust']} · {fig} · review `{v['review']}` · "
                           f"[[{v['path'].rsplit('.', 1)[0] if v['path'].endswith('.md') else v['path']}|{v['channel']}]]"
                           f" · in via {INPUT_LABEL[v['input_method']].lower()}")
                for ch in v["changes"]:
                    if ch["field"] == "condition_added":
                        out.append(f"    - New condition: {ch['new']}")
                    elif ch["field"] == "condition_removed":
                        out.append(f"    - Condition dropped: {ch['old']}")
                    else:
                        out.append(f"    - {ch['label']}: {_money(ch['old'])} → {_money(ch['new'])}")
        for cond in car["conditions"]:
            out.append(f"- Condition: {cond['text']} — {cond['label']}")
        out.append("")
    out += ["## Actions", ""]
    for a in s["actions"]:
        out.append(f"- [{'x' if a['status'] == 'done' else ' '}] {a['text']}"
                   + (f" — {a['closed_by_name']}: {a['close_note']}" if a["status"] == "done" else ""))
    text = "\n".join(out) + "\n"
    (WIKI / "clients" / f"{c['slug']}-indications.md").write_text(text)
    return text


# --- entry points ---------------------------------------------------------------

def after_change(conn, cid: int, actor_id: int):
    """Keep the client pack and wiki in step after any carrier reply or review."""
    from . import report
    if conn.execute("SELECT 1 FROM report_versions WHERE client_id=%s", (cid,)).fetchone():
        report.refresh_working(conn, cid, actor_id, edited=False)
    render_wiki(conn, cid)


def ingest_file(path: str, slug: str = CLIENT_SLUG, actor: str = "Pipeline (AI)") -> dict:
    with connect() as conn:
        cid = client_by_slug(conn, slug)["id"]
        uid = user_id(conn, actor)
        res = ingest(conn, cid, path, uid)
        if not res.get("skipped"):
            after_change(conn, cid, uid)
    if res.get("skipped"):
        print(f"already ingested: {res['path']}")
    else:
        wiki_render.log(f"indication | {slug} — {res['carrier']} via {res['channel']}, input {res['input_method']} "
                        f"({res['extractor']}): "
                        + "; ".join(res["options"])
                        + (f"; {len(res['failed_checks'])} figure(s) to confirm" if res["failed_checks"] else ""))
        print(f"{res['carrier']} ({res['channel']}, {res['extractor']}): " + "; ".join(res["options"]))
        for f in res["failed_checks"]:
            print("  check:", f)
    return res


def run(slug: str = CLIENT_SLUG):
    """Demo seed: requests go out, the first four replies come back."""
    with connect() as conn:
        cid = client_by_slug(conn, slug)["id"]
        n = request_all(conn, cid, user_id(conn, "Pipeline (AI)"), "initial (demo seed: sent before review)", gate=False)
    wiki_render.log(f"request | {slug} — indication requests sent to {n} carriers "
                    f"({', '.join(o['label'] for o in REQUESTED_OPTIONS)})")
    print(f"requests sent to {n} carriers")
    for name in SEED_REPLIES:
        ingest_file(str(inbox_dir(slug) / name), slug)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        ingest_file(sys.argv[1])
    else:
        run()
