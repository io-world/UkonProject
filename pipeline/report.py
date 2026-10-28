"""Stage 3 — the client proposal pack (digital report). One snapshot builder feeds both the agent view (editable)
and the client view (a frozen, submitted version). Versions are immutable once submitted."""
import json

from .sources import read_source
from . import estimators, narrative
from .config import RAW, ROOT
from .db import j

TIERS = ["recommended", "premier"]   # the two options requested from carriers (config.REQUESTED_OPTIONS)

# Intake topics shown to the owner. Labels are fixed text; status comes from the answer, not from AI prose.
INTAKE_TOPICS = [
    ("mfa_email", "Phone codes on every email login"),
    ("mfa_remote", "Phone codes for remote access"),
    ("backups", "Backups that are tested and out of a hacker's reach"),
    ("edr", "Attack-monitoring software on every computer"),
    ("payment_verify", "Calling to confirm payment changes"),
    ("phishing_training", "Fake-email training for staff"),
    ("prior_incidents", "Past incidents"),
]


def _topic_status(key: str, a: dict | None) -> tuple[str, str]:
    """(status_code, plain label) for one intake topic."""
    if not a or a["status"] == "unanswered":
        return "open", "To confirm"
    if a["normalized"] == "partial":
        return "partial", "Partly in place, to confirm"
    if a["status"] == "needs_followup":
        return "open", "To confirm"
    if key == "prior_incidents":
        return ("ok", "None reported") if a["normalized"] == "no" else ("open", "Reported, to review")
    return ("ok", "In place") if a["normalized"] == "yes" else ("gap", "Not yet")


def intake_summary(conn, cid: int) -> dict:
    rows = {r["question_key"]: r for r in conn.execute(
        "SELECT * FROM application_answers WHERE client_id=%s", (cid,)).fetchall()}
    calls = conn.execute("SELECT call_ref, ingested_at FROM intake_calls WHERE client_id=%s ORDER BY ingested_at",
                         (cid,)).fetchall()
    topics = []
    for key, label in INTAKE_TOPICS:
        code, status = _topic_status(key, rows.get(key))
        topics.append({"key": key, "label": label, "code": code, "status": status,
                       "source_call": rows[key]["source_call"] if key in rows else None})
    open_n = sum(1 for r in rows.values() if r["status"] in ("needs_followup", "unanswered"))
    return {"calls": [c["call_ref"] for c in calls], "topics": topics,
            "answered": sum(1 for r in rows.values() if r["status"] in ("prefilled", "confirmed")),
            "open": open_n, "total": len(rows)}


def research_items(naics: str, use: str = "client_pack") -> list[dict]:
    """Cited industry research gathered by the client-research skill (wiki/raw/research/)."""
    items = []
    for page in sorted((RAW / "research").glob(f"{naics}_*.md")):
        items += [dict(i, wiki=f"raw/research/{page.stem}") for i in read_source(page)["items"]
                  if use in i.get("use_in", []) and i.get("url")]
    return items


def _fields(conn, cid):
    rows = conn.execute("SELECT * FROM fields WHERE client_id=%s ORDER BY id", (cid,)).fetchall()
    return {r["key"]: r for r in rows}


def build_snapshot(conn, cid: int, narrative_blocks: dict) -> dict:
    c = conn.execute("SELECT * FROM clients WHERE id=%s", (cid,)).fetchone()
    f = _fields(conn, cid)
    val = lambda k: f[k]["current_value"] if k in f else None
    sig = read_source(RAW / c["slug"] / "signals.md")

    inds = conn.execute("SELECT * FROM indications WHERE client_id=%s ORDER BY carrier, limit_amount", (cid,)).fetchall()
    carriers = {}
    for i in inds:
        carriers.setdefault(i["carrier"], {"carrier": i["carrier"], "conditions": i["conditions"],
                                           "bi_waiting_hours": i["bi_waiting_hours"],
                                           "specimen_form": i["specimen_form"],
                                           "expires_on": i["expires_on"].isoformat(), "options": {}})
        carriers[i["carrier"]]["options"][i["tier"]] = {
            "limit": i["limit_amount"], "deductible": i["deductible"], "premium": i["premium"],
            "monthly": round(i["premium"] / 12) if i["premium"] is not None else None, "sublimits": i["sublimits"], "version_no": i["version_no"],
            "expired": i["expired"]}
    # Why an option is missing for a carrier (declined, waiting on writing, flagged figure, expired)
    from . import indications as ind_mod
    for car in ind_mod.state(conn, cid)["carriers"]:
        if car["carrier"] in carriers:
            carriers[car["carrier"]]["option_state"] = {o["tier"]: o["state"] for o in car["options"]}
    selected = val("selected_carrier")
    sel_rows = [i for i in inds if i["carrier"] == selected]
    basis = (sel_rows or inds)[0]["basis_revenue"] if inds else None
    drift = estimators.revenue_drift(float(val("annual_revenue")), basis) if basis else None

    # Exposure: AI breakdown + whatever score is in force (agent may have moved it)
    breakdown = val("exposure_breakdown") or {}
    score = val("exposure_score")
    band = "Elevated" if score >= 65 else "Moderate" if score >= 40 else "Lower"

    placeholders = {"business_name": c["display_name"], "owner_last": sig["owner"]["last"], "city": sig["city"],
                    "email_accounts": val("employee_count"), "dentists": val("dentists"), "staff": val("employee_count")}
    filled = json.loads(narrative.fill(json.dumps(narrative_blocks), placeholders))

    bench = {k: f[k]["current_value"] for k in f if k.startswith("scenario.")}
    # The "how" text is a fixed template (not AI); the figures come from the benchmark fields.
    spg = ("S&P Global Market Intelligence", "https://www.spglobal.com/marketintelligence/en/news-insights/latest-news-headlines/"
           "cyber-insurance-claims-rising-for-small-medium-sized-businesses-62084560")
    ndl = ("NetDiligence 2025 Cyber Claims Study, via Baker Donelson",
           "https://www.bakerdonelson.com/cybersecurity-awareness-month-2025-avoid-cyber-claims-scares")
    scenario_costs = {
        "ransomware": {"low": bench.get("scenario.ir_cost_median"), "high": bench.get("scenario.ir_cost_average"),
                       "label": "Typical small-business incident response cost (median to average)",
                       "how": "Not calculated for your practice: two published industry figures for what small businesses pay "
                              "for incident response (the experts who find out what happened and get systems back). The low end "
                              "is the median, the middle claim; the high end is the average, pulled up by a few very large "
                              "claims. Lost revenue while closed isn't included (see operating costs above).",
                       "source": spg[0], "source_url": spg[1]},
        "bec": {"low": bench.get("scenario.bec_claim_cost"), "high": None, "label": "Average fake-invoice (BEC) claim",
                "how": "Not calculated for your practice: the average insurance claim for business email compromise "
                       "(a fake invoice or changed bank details that gets paid), across all claims in the study.",
                "source": ndl[0], "source_url": ndl[1]},
        "breach": {"low": bench.get("scenario.sme_incident_cost"), "high": None,
                   "label": "Average cyber incident cost for small and mid-sized businesses",
                   "how": "Not calculated for your practice: the average total cost of a cyber incident for small and "
                          "mid-sized businesses across all claims in the study (all incident types, not only breaches).",
                   "source": ndl[0], "source_url": ndl[1]},
    }
    # Operating costs (OPEX): revenue × typical dental overhead, per calendar day. Computed here, never by the AI.
    opex = None
    if "benchmark.overhead_low" in f and "benchmark.overhead_high" in f:
        rev = float(val("annual_revenue"))
        lo, hi = float(val("benchmark.overhead_low")), float(val("benchmark.overhead_high"))
        opex = {"ratio_low": lo, "ratio_high": hi, "revenue": rev,
                "annual_low": round(rev * lo, -3), "annual_high": round(rev * hi, -3),
                "daily_low": round(rev * lo / 365, -2), "daily_high": round(rev * hi / 365, -2),
                "source": "American Dental Association, via Overjet (2025)",
                "source_url": "https://www.overjet.com/blog/average-dental-office-overhead-complete-breakdown-by-practice-size"}
    coverage = read_source(RAW / "carriers" / "coverage_language.md")
    naics = sig["industry"]["naics"]

    return {
        "client": {"name": c["display_name"], "renewal_date": c["renewal_date"].isoformat()},
        "facts": {k: {"label": f[k]["label"], "value": f[k]["current_value"], "ai_value": f[k]["ai_value"],
                      "confidence": f[k]["confidence"], "adjustable": f[k]["adjustable"]}
                  for k in ["legal_name", "domain", "industry", "address", "annual_revenue", "employee_count",
                            "records_estimate"] if k in f},
        "exposure": {"score": score, "ai_score": f["exposure_score"]["ai_value"], "band": band,
                     "factors": breakdown.get("factors", []), "unknown_controls": breakdown.get("unknown_controls", [])},
        "selected_carrier": selected,
        "carriers": list(carriers.values()),
        "options": carriers.get(selected, {}).get("options", {}),
        "recommended_tier": "recommended",
        "limit_guidance": {"two_months_revenue": round(float(val("annual_revenue")) / 6, -3)},
        "revenue_drift": drift,
        "scenario_costs": scenario_costs,
        "opex": opex,
        "narrative": filled,
        "coverage": coverage,
        "intake": intake_summary(conn, cid),
        "research": research_items(naics, "client_pack"),
    }


def working_version(conn, cid: int, actor_id: int) -> dict:
    """Latest editable version, or a fresh one copied from the latest locked version."""
    latest = conn.execute("SELECT * FROM report_versions WHERE client_id=%s ORDER BY version_no DESC LIMIT 1",
                          (cid,)).fetchone()
    if latest and latest["state"] in ("ai_draft", "agent_edited"):
        return latest
    if not latest:
        raise ValueError("no draft yet — run pipeline.run_all first")
    return conn.execute("""INSERT INTO report_versions (client_id, version_no, state, snapshot, narrative, created_by)
                           VALUES (%s,%s,'agent_edited',%s,%s,%s) RETURNING *""",
                        (cid, latest["version_no"] + 1, j(latest["snapshot"]), j(latest["narrative"]),
                         actor_id)).fetchone()


def refresh_working(conn, cid: int, actor_id: int, edited: bool = True) -> dict:
    v = working_version(conn, cid, actor_id)
    snap = build_snapshot(conn, cid, v["narrative"])
    state = "agent_edited" if edited else v["state"]
    v = conn.execute("UPDATE report_versions SET snapshot=%s, state=%s WHERE id=%s RETURNING *",
                     (j(snap), state, v["id"])).fetchone()
    export_html(conn, cid, v)
    return v


def export_html(conn, cid: int, v: dict) -> str:
    """Write the standalone HTML report. Working versions overwrite reports/<slug>/current.html;
    submitted/sent versions are written once as v<N>.html and never changed afterwards."""
    from . import html_report
    slug = conn.execute("SELECT slug FROM clients WHERE id=%s", (cid,)).fetchone()["slug"]
    out = ROOT / "reports" / slug
    out.mkdir(parents=True, exist_ok=True)
    locked = v["state"] in ("submitted", "sent")
    path = out / (f"v{v['version_no']}.html" if locked else "current.html")
    path.write_text(html_report.render(v["snapshot"], v, client_view=locked))
    return str(path.relative_to(ROOT))


def submit(conn, cid: int, actor_id: int) -> dict:
    if not conn.execute("SELECT 1 FROM indications WHERE client_id=%s", (cid,)).fetchone():
        raise ValueError("No carrier prices yet: take in at least one written indication in Stage 2 before submitting the pack")
    v = refresh_working(conn, cid, actor_id, edited=False)
    conn.execute("""UPDATE report_versions SET superseded_from=state, state='superseded'
                    WHERE client_id=%s AND state IN ('submitted','sent')""", (cid,))
    v = conn.execute("""UPDATE report_versions SET state='submitted', submitted_by=%s, submitted_at=now()
                        WHERE id=%s RETURNING *""", (actor_id, v["id"])).fetchone()
    export_html(conn, cid, v)
    return v


def undo_submit(conn, cid: int, actor_id: int, reason: str | None) -> dict:
    """Undo the latest submit without unlocking anything: that version becomes 'withdrawn' (content and
    v<N>.html unchanged, who/when/why recorded), the version it superseded gets its earlier state back,
    and editing continues in a new draft copied from it. A version already sent to the client can't be withdrawn."""
    latest = conn.execute("SELECT * FROM report_versions WHERE client_id=%s ORDER BY version_no DESC LIMIT 1",
                          (cid,)).fetchone()
    if not latest or latest["state"] != "submitted":
        if latest and latest["state"] == "sent":
            raise ValueError(f"v{latest['version_no']} was already sent to the client, so it can't be withdrawn. "
                             "Make the change and submit a new version.")
        raise ValueError("Nothing to undo: the latest version isn't submitted")
    conn.execute("""UPDATE report_versions SET state='withdrawn', withdrawn_by=%s, withdrawn_at=now(), withdraw_reason=%s
                    WHERE id=%s""", (actor_id, reason, latest["id"]))
    prev = conn.execute("""SELECT * FROM report_versions WHERE client_id=%s AND state='superseded'
                           AND superseded_from IS NOT NULL ORDER BY version_no DESC LIMIT 1""", (cid,)).fetchone()
    if prev:
        conn.execute("UPDATE report_versions SET state=superseded_from, superseded_from=NULL WHERE id=%s", (prev["id"],))
    draft = conn.execute("""INSERT INTO report_versions (client_id, version_no, state, snapshot, narrative, created_by)
                            VALUES (%s,%s,'agent_edited',%s,%s,%s) RETURNING *""",
                         (cid, latest["version_no"] + 1, j(latest["snapshot"]), j(latest["narrative"]), actor_id)).fetchone()
    export_html(conn, cid, draft)
    return {"withdrawn": latest["version_no"], "restored": prev["version_no"] if prev else None,
            "draft": draft["version_no"]}


def send(conn, cid: int) -> dict:
    v = conn.execute("""SELECT * FROM report_versions WHERE client_id=%s AND state='submitted'
                        ORDER BY version_no DESC LIMIT 1""", (cid,)).fetchone()
    if not v:
        raise ValueError("nothing submitted to send")
    conn.execute("UPDATE clients SET stage='agent_kit' WHERE id=%s AND stage IN ('confirm','indications','proposal')", (cid,))
    v = conn.execute("UPDATE report_versions SET state='sent', sent_at=now() WHERE id=%s RETURNING *",
                     (v["id"],)).fetchone()
    export_html(conn, cid, v)
    return v
