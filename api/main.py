"""FastAPI over the system of record. The UI never writes a premium: there is no route for it."""
import re
from datetime import date

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from pathlib import Path

from pipeline import html_report, intake, intake_ingest, report, wiki_render
from pipeline.config import RAW, WIKI
from pipeline.sources import read_source
from pipeline.db import client_by_slug, connect, j, user_id

from . import ask as ask_mod

app = FastAPI(title="UKON cyber renewal prototype")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


_SCHEMA_OK = False


@app.middleware("http")
async def _schema_guard(request, call_next):
    """If the database was built by an older schema.sql, say so instead of failing on a missing column."""
    global _SCHEMA_OK
    if request.url.path.startswith("/api/") and not _SCHEMA_OK:
        from fastapi.responses import JSONResponse
        from pipeline.config import SCHEMA_VERSION
        try:
            with connect() as conn:
                v = conn.execute("SELECT version FROM schema_info").fetchone()["version"]
        except Exception:
            v = None
        if v != SCHEMA_VERSION:
            return JSONResponse(status_code=409, content={"detail": "The database is from an older version of the "
                                "prototype. Reload it: uv run python -m pipeline.run_all (then refresh this page)."})
        _SCHEMA_OK = True
    return await call_next(request)


@app.exception_handler(ValueError)
def _unknown_client(request, exc: ValueError):
    """A client that isn't in the database yet usually means the demo data was never loaded."""
    from fastapi.responses import JSONResponse
    if str(exc).startswith("unknown client"):
        return JSONResponse(status_code=404, content={"detail": f"{exc}. Load the demo data first: "
                            "uv run python -m pipeline.run_all"})
    raise exc


class Actor(BaseModel):
    actor: str


SOURCE_TYPES = ("conversation", "clipboard", "api", "manual")


class FieldChange(Actor):
    value: float | int | str
    reason: str | None = None
    source_type: str = "manual"        # where the person got the new value
    source_ref: str | None = None      # e.g. call_1_intake, "email from Dr. Pollack 10/28", "agency AMS API"


class AnswerConfirm(Actor):
    answer: str | None = None
    normalized: str | None = None


class Question(Actor):
    question: str


def _num(x):
    return float(x) if x is not None else None


def _change_field(conn, cid, key, actor_id, value, reason, source_type="manual", source_ref=None):
    f = conn.execute("SELECT * FROM fields WHERE client_id=%s AND key=%s", (cid, key)).fetchone()
    if not f:
        raise HTTPException(404, f"no field {key}")
    if not f["adjustable"]:
        raise HTTPException(403, f"{f['label']} is locked")
    if f["kind"] in ("money", "int", "score"):
        value = int(round(float(value), -3)) if f["kind"] == "money" else int(round(float(value)))
        if f["kind"] == "score":
            value = max(0, min(100, value))
    if source_type not in SOURCE_TYPES:
        raise HTTPException(400, f"source_type must be one of {', '.join(SOURCE_TYPES)}")
    if isinstance(value, str) and not value.strip():
        raise HTTPException(400, "value can't be empty")
    conn.execute("INSERT INTO field_changes (field_id, actor_id, old_value, new_value, reason, source_type, source_ref) "
                 "VALUES (%s,%s,%s,%s,%s,%s,%s)",
                 (f["id"], actor_id, j(f["current_value"]), j(value), reason, source_type, source_ref))
    conn.execute("UPDATE fields SET current_value=%s, needs_review=FALSE, updated_by=%s, updated_at=now(), "
                 "source_type=%s, source_ref=%s WHERE id=%s",
                 (j(value), actor_id, source_type, source_ref, f["id"]))


@app.get("/api/users")
def users():
    with connect() as conn:
        return conn.execute("SELECT name, role FROM users WHERE role <> 'system' ORDER BY id").fetchall()


@app.get("/api/clients/{slug}")
def client(slug: str):
    with connect() as conn:
        c = client_by_slug(conn, slug)
        days = (c["renewal_date"] - date(2026, 10, 25)).days
        ents = conn.execute("""SELECT e.*, u.name AS decided_by_name FROM entity_candidates e
                               LEFT JOIN users u ON u.id=e.decided_by WHERE client_id=%s ORDER BY match_score DESC""",
                            (c["id"],)).fetchall()
        fields = conn.execute("""SELECT f.*, u.name AS updated_by_name FROM fields f LEFT JOIN users u ON u.id=f.updated_by
                                 WHERE client_id=%s ORDER BY f.id""", (c["id"],)).fetchall()
        for f in fields:
            f["ai_low"], f["ai_high"] = _num(f["ai_low"]), _num(f["ai_high"])
        for e in ents:
            e["match_score"] = float(e["match_score"])
        return {"client": c | {"days_to_renewal": days}, "entities": ents, "fields": fields}


@app.post("/api/clients/{slug}/entity/{cand_id}/confirm")
def confirm_entity(slug: str, cand_id: int, body: Actor):
    with connect() as conn:
        c = client_by_slug(conn, slug)
        uid = user_id(conn, body.actor)
        cand = conn.execute("SELECT * FROM entity_candidates WHERE id=%s AND client_id=%s", (cand_id, c["id"])).fetchone()
        if not cand:
            raise HTTPException(404)
        conn.execute("UPDATE entity_candidates SET status='rejected', decided_by=%s, decided_at=now() "
                     "WHERE client_id=%s AND id<>%s", (uid, c["id"], cand_id))
        conn.execute("UPDATE entity_candidates SET status='confirmed', decided_by=%s, decided_at=now() WHERE id=%s",
                     (uid, cand_id))
        f = conn.execute("SELECT * FROM fields WHERE client_id=%s AND key='legal_name'", (c["id"],)).fetchone()
        conn.execute("INSERT INTO field_changes (field_id, actor_id, old_value, new_value, reason) VALUES (%s,%s,%s,%s,%s)",
                     (f["id"], uid, j(f["current_value"]), j(cand["legal_name"]), "Entity match confirmed"))
        conn.execute("UPDATE fields SET current_value=%s, needs_review=FALSE, confidence='high', updated_by=%s "
                     "WHERE id=%s", (j(cand["legal_name"]), uid, f["id"]))
        report.refresh_working(conn, c["id"], uid, edited=False)
        wiki_render.render_client(conn, c["id"])
    wiki_render.log(f"review | {slug} — {body.actor} confirmed entity '{cand['legal_name']}'")
    return {"ok": True}


@app.post("/api/clients/{slug}/entity/undo")
def undo_entity(slug: str, body: Actor):
    """Undo a company confirmation: every candidate goes back to 'suggested' and the legal name back to the
    top-scoring candidate, flagged for review again. The undo itself is logged (who, what was undone)."""
    with connect() as conn:
        c = client_by_slug(conn, slug)
        uid = user_id(conn, body.actor)
        conf = conn.execute("SELECT * FROM entity_candidates WHERE client_id=%s AND status='confirmed'", (c["id"],)).fetchone()
        if not conf:
            raise HTTPException(409, "Nothing to undo: no company is confirmed")
        conn.execute("UPDATE entity_candidates SET status='suggested', decided_by=NULL, decided_at=NULL WHERE client_id=%s",
                     (c["id"],))
        f = conn.execute("SELECT * FROM fields WHERE client_id=%s AND key='legal_name'", (c["id"],)).fetchone()
        conn.execute("INSERT INTO field_changes (field_id, actor_id, old_value, new_value, reason, source_type) "
                     "VALUES (%s,%s,%s,%s,%s,'manual')",
                     (f["id"], uid, j(f["current_value"]), f["ai_value"] and j(f["ai_value"]),
                      f"Undid company confirmation ({conf['legal_name']})"))
        conn.execute("UPDATE fields SET current_value=ai_value, needs_review=TRUE, confidence='medium', updated_by=%s, "
                     "updated_at=now(), source_type='pipeline', source_ref=NULL WHERE id=%s", (uid, f["id"]))
        report.refresh_working(conn, c["id"], uid, edited=False)
        wiki_render.render_client(conn, c["id"])
    wiki_render.log(f"review | {slug} — {body.actor} undid the confirmation of '{conf['legal_name']}'")
    return {"ok": True}


@app.post("/api/clients/{slug}/fields/{key}")
def change_field(slug: str, key: str, body: FieldChange):
    with connect() as conn:
        c = client_by_slug(conn, slug)
        uid = user_id(conn, body.actor)
        _change_field(conn, c["id"], key, uid, body.value, body.reason, body.source_type, body.source_ref)
        v = report.refresh_working(conn, c["id"], uid)
        wiki_render.render_client(conn, c["id"])
    wiki_render.log(f"review | {slug} — {body.actor} set {key} = {body.value}" + (f" ({body.reason})" if body.reason else ""))
    return {"version_no": v["version_no"], "state": v["state"]}


@app.post("/api/clients/{slug}/fields/{key}/approve")
def approve_field(slug: str, key: str, body: Actor):
    with connect() as conn:
        c = client_by_slug(conn, slug)
        uid = user_id(conn, body.actor)
        f = conn.execute("SELECT * FROM fields WHERE client_id=%s AND key=%s", (c["id"], key)).fetchone()
        conn.execute("INSERT INTO field_changes (field_id, actor_id, old_value, new_value, reason) VALUES (%s,%s,%s,%s,%s)",
                     (f["id"], uid, j(f["current_value"]), j(f["current_value"]), "Reviewed — kept AI value"))
        conn.execute("UPDATE fields SET needs_review=FALSE, updated_by=%s WHERE id=%s", (uid, f["id"]))
        wiki_render.render_client(conn, c["id"])
    return {"ok": True}


@app.get("/api/clients/{slug}/report")
def get_report(slug: str, mode: str = "agent"):
    with connect() as conn:
        c = client_by_slug(conn, slug)
        if mode == "client":
            v = conn.execute("""SELECT * FROM report_versions WHERE client_id=%s AND state IN ('submitted','sent')
                                ORDER BY version_no DESC LIMIT 1""", (c["id"],)).fetchone()
        else:
            v = conn.execute("SELECT * FROM report_versions WHERE client_id=%s ORDER BY version_no DESC LIMIT 1",
                             (c["id"],)).fetchone()
        if not v:
            return {"version": None}
        return {"version": {k: v[k] for k in ("version_no", "state", "created_at", "submitted_at", "sent_at")},
                "snapshot": v["snapshot"]}


@app.get("/api/clients/{slug}/versions")
def versions(slug: str):
    with connect() as conn:
        c = client_by_slug(conn, slug)
        return conn.execute("""SELECT v.version_no, v.state, v.created_at, v.submitted_at, v.sent_at,
                               cu.name AS created_by, su.name AS submitted_by,
                               v.snapshot->'facts'->'annual_revenue'->>'value' AS revenue,
                               v.snapshot->'facts'->'employee_count'->>'value' AS employees,
                               v.snapshot->'exposure'->>'score' AS exposure,
                               v.snapshot->>'selected_carrier' AS carrier
                               FROM report_versions v JOIN users cu ON cu.id=v.created_by
                               LEFT JOIN users su ON su.id=v.submitted_by
                               WHERE v.client_id=%s ORDER BY v.version_no DESC""", (c["id"],)).fetchall()


@app.get("/api/clients/{slug}/report.html", response_class=HTMLResponse)
def report_html(slug: str, version: int | None = None):
    """The standalone HTML report, rendered from a stored version (latest if none given).
    The same file is written to reports/<slug>/ on disk."""
    with connect() as conn:
        c = client_by_slug(conn, slug)
        q = "SELECT * FROM report_versions WHERE client_id=%s" + (" AND version_no=%s" if version else "") + \
            " ORDER BY version_no DESC LIMIT 1"
        v = conn.execute(q, (c["id"], version) if version else (c["id"],)).fetchone()
        if not v:
            raise HTTPException(404, "no report yet")
        return html_report.render(v["snapshot"], v, client_view=v["state"] in ("submitted", "sent", "superseded"))


@app.post("/api/clients/{slug}/report/submit")
def submit(slug: str, body: Actor):
    with connect() as conn:
        c = client_by_slug(conn, slug)
        v = report.submit(conn, c["id"], user_id(conn, body.actor))
    wiki_render.log(f"report | {slug} — v{v['version_no']} submitted (locked) by {body.actor}")
    return {"version_no": v["version_no"], "state": v["state"]}


@app.post("/api/clients/{slug}/report/send")
def send(slug: str, body: Actor):
    with connect() as conn:
        c = client_by_slug(conn, slug)
        try:
            v = report.send(conn, c["id"])
        except ValueError as e:
            raise HTTPException(400, str(e))
    wiki_render.log(f"report | {slug} — v{v['version_no']} sent to client by {body.actor}")
    return {"version_no": v["version_no"], "state": v["state"]}


@app.get("/api/clients/{slug}/audit")
def audit(slug: str):
    with connect() as conn:
        c = client_by_slug(conn, slug)
        return conn.execute("SELECT * FROM audit_trail WHERE client_id=%s ORDER BY at DESC", (c["id"],)).fetchall()


def _table(md: str, heading: str):
    section = md.split(heading, 1)[1].split("\n## ", 1)[0]
    rows = [r for r in section.splitlines() if r.startswith("|") and not r.startswith("|---")][1:]
    return [[cell.strip() for cell in r.strip("|").split("|")] for r in rows]


def _bullets(md: str, heading: str):
    section = md.split(heading, 1)[1].split("\n## ", 1)[0]
    return [l[2:].strip() for l in section.splitlines() if l.startswith("- ")]


@app.get("/api/clients/{slug}/brief")
def brief(slug: str):

    with connect() as conn:
        c = client_by_slug(conn, slug)
        v = conn.execute("SELECT * FROM report_versions WHERE client_id=%s ORDER BY version_no DESC LIMIT 1",
                         (c["id"],)).fetchone()
        apps = conn.execute("SELECT question_key, status FROM application_answers WHERE client_id=%s",
                            (c["id"],)).fetchall()
    snap = v["snapshot"]
    industry = (WIKI / "industries" / "621210-dental-offices.md").read_text()
    keys = ["too_small", "it_handles_it", "too_expensive", "never_hacked", "bop_covers"]
    lib = _table(industry, "## Objection library")
    objections = []
    for key, row in zip(keys, lib):
        objections.append({"key": key, "objection": row[0].strip('"'), "approved": row[1],
                           "tailored": snap["narrative"]["objection_tailoring"].get(key),
                           "escalate": "Escalate to CPL" in row[1]})
    specimen = read_source(RAW / "carriers" / "specimen_map.md")
    questions = read_source(RAW / "carriers" / "application_questions.md")["questions"]
    return {
        "pitch": snap["narrative"]["agent_pitch"],
        "recommended": snap["options"].get("recommended"),
        "carrier": snap["selected_carrier"],
        "objections": objections,
        "escalations": _bullets(industry, "## Escalation triggers"),
        "specimen": specimen.get(snap["selected_carrier"], {}),
        "conditions": next((c["conditions"] for c in snap["carriers"] if c["carrier"] == snap["selected_carrier"]), []),
        "research": report.research_items("621210", "agent_brief"),
        "application_preview": [{"key": q["key"], "plain": q["plain"], "gate": q.get("gate", False)}
                                for q in questions if not q.get("prefill_from")],
        "application_status": {a["question_key"]: a["status"] for a in apps},
    }


@app.get("/api/clients/{slug}/application")
def application(slug: str):
    with connect() as conn:
        c = client_by_slug(conn, slug)
        return conn.execute("""SELECT a.*, u.name AS confirmed_by_name FROM application_answers a
                               LEFT JOIN users u ON u.id=a.confirmed_by WHERE client_id=%s ORDER BY a.id""",
                            (c["id"],)).fetchall()


@app.get("/api/clients/{slug}/intake/calls")
def intake_calls(slug: str):
    with connect() as conn:
        c = client_by_slug(conn, slug)
        return conn.execute("SELECT call_ref, wiki_path, answered, flagged, ingested_at FROM intake_calls "
                            "WHERE client_id=%s ORDER BY ingested_at", (c["id"],)).fetchall()


APPLY_TO_FIELD = {"revenue": "annual_revenue", "records": "records_estimate"}


def _confirm_app(conn, cid: int, key: str, uid: int, answer=None, normalized=None) -> str | None:
    """Confirm one application answer; a confirmed revenue/record count updates the report field (logged)."""
    a = conn.execute("SELECT * FROM application_answers WHERE client_id=%s AND question_key=%s", (cid, key)).fetchone()
    if not a or a["status"] == "unanswered" and answer is None:
        return None
    conn.execute("""UPDATE application_answers SET status='confirmed', confirmed_by=%s, confirmed_at=now(),
                    answer=COALESCE(%s, answer), normalized=COALESCE(%s, normalized) WHERE id=%s""",
                 (uid, answer, normalized, a["id"]))
    if key in APPLY_TO_FIELD and isinstance(a["value"], (int, float)):
        cur = conn.execute("SELECT current_value FROM fields WHERE client_id=%s AND key=%s",
                           (cid, APPLY_TO_FIELD[key])).fetchone()
        if cur and cur["current_value"] != a["value"]:
            _change_field(conn, cid, APPLY_TO_FIELD[key], uid, a["value"],
                          f"Confirmed by client on {a['source_call'] or 'call'} [{a['source_ts']}]",
                          "conversation", a["source_call"])
            return APPLY_TO_FIELD[key]
    return None


@app.post("/api/clients/{slug}/application/{key}/confirm")
def confirm_answer(slug: str, key: str, body: AnswerConfirm):
    with connect() as conn:
        c = client_by_slug(conn, slug)
        uid = user_id(conn, body.actor)
        if not conn.execute("SELECT 1 FROM application_answers WHERE client_id=%s AND question_key=%s",
                            (c["id"], key)).fetchone():
            raise HTTPException(404)
        applied = _confirm_app(conn, c["id"], key, uid, body.answer, body.normalized)
        intake_ingest.after_change(conn, c["id"], slug, uid, edited=True)
    wiki_render.log(f"review | {slug} — {body.actor} confirmed application answer '{key}'")
    return {"ok": True, "applied_to": applied}


# ---------------------------------------------------------------------------------------------
# Intake: live call screen + recorded calls, one record per question-bank item
# ---------------------------------------------------------------------------------------------

class LiveTap(Actor):
    live: dict


class IntakeConfirm(Actor):
    value: int | float | str | list | None = None


class Escalation(Actor):
    text: str
    call_time: str | None = None


class IngestCall(Actor):
    transcript: str


def _figures(conn, cid: int) -> dict:
    """Report figures the walkthrough script can quote. Only what the database actually holds;
    everything else stays a labelled placeholder (the limit model is not built yet)."""
    v = conn.execute("SELECT snapshot FROM report_versions WHERE client_id=%s ORDER BY version_no DESC LIMIT 1",
                     (cid,)).fetchone()
    if not v:
        return {}
    s = v["snapshot"]
    opts = s.get("options", {})
    rec = opts.get("recommended") or {}
    carrier = next((x for x in s.get("carriers", []) if x["carrier"] == s.get("selected_carrier")), {})
    sc = s.get("scenario_costs", {})
    fig = {}
    if carrier.get("bi_waiting_hours") is not None:
        fig["waiting_period"] = f"{carrier['bi_waiting_hours']}-hour"
    if sc.get("ransomware", {}).get("low"):
        fig["ir_cost"] = f"${sc['ransomware']['low']:,.0f}–${sc['ransomware']['high']:,.0f}"
    if rec.get("sublimits", {}).get("social_engineering"):
        fig["social_eng_sublimit"] = f"${rec['sublimits']['social_engineering']:,.0f}"
    if rec.get("limit"):
        fig["recommended_limit"] = f"${rec['limit']:,.0f}"
    fig["current_limit"] = "no cyber coverage on file"
    return fig


@app.get("/api/clients/{slug}/intake")
def intake_view(slug: str):
    with connect() as conn:
        c = client_by_slug(conn, slug)
        intake_ingest.seed(conn, c["id"])
        rows = {r["item_key"]: r for r in conn.execute(
            """SELECT ia.*, u.name AS confirmed_by_name, lu.name AS live_by_name FROM intake_answers ia
               LEFT JOIN users u ON u.id = ia.confirmed_by LEFT JOIN users lu ON lu.id = ia.live_by
               WHERE client_id=%s""", (c["id"],)).fetchall()}
        fields = {r["key"]: r for r in conn.execute("SELECT * FROM fields WHERE client_id=%s", (c["id"],)).fetchall()}
        esc = conn.execute("""SELECT e.*, u.name AS created_by_name FROM intake_escalations e
                              LEFT JOIN users u ON u.id = e.created_by WHERE client_id=%s ORDER BY e.id""",
                           (c["id"],)).fetchall()
        calls = conn.execute("SELECT call_ref, wiki_path, answered, flagged, ingested_at FROM intake_calls "
                             "WHERE client_id=%s ORDER BY ingested_at, id", (c["id"],)).fetchall()
        figures = _figures(conn, c["id"])
    bank = intake.load_bank()
    items = []
    for it in bank:
        r = rows.get(it["key"]) or {}
        f = fields.get(it.get("prefill_from")) if it.get("prefill_from") else None
        items.append(it | {"row": r, "prefill": None if not f else {
            "value": f["current_value"], "confidence": f["confidence"], "method": f["method"],
            "needs_review": f["needs_review"]}})
    ingested = {c["call_ref"] for c in calls}
    transcripts = sorted(p.name for p in (RAW / slug).glob("call_*.md"))
    return {"items": items, "groups": read_source(RAW / "intake" / "intake_questions.md").get("groups", []),
            "steps": read_source(RAW / "intake" / "walkthrough_script.md")["steps"],
            "escalations": esc, "calls": calls, "figures": figures,
            "transcripts": [{"file": t, "ingested": t[:-3] in ingested} for t in transcripts]}


@app.post("/api/clients/{slug}/intake/{key}/live")
def intake_live(slug: str, key: str, body: LiveTap):
    """Save what the agent tapped on the live call screen. Not a confirmation: the recording is
    checked against it when the call is ingested."""
    with connect() as conn:
        c = client_by_slug(conn, slug)
        uid = user_id(conn, body.actor)
        r = conn.execute("UPDATE intake_answers SET live=%s, live_by=%s, live_at=now() WHERE client_id=%s "
                         "AND item_key=%s RETURNING id", (j(body.live), uid, c["id"], key)).fetchone()
        if not r:
            raise HTTPException(404)
    return {"ok": True}


@app.post("/api/clients/{slug}/intake/{key}/confirm")
def intake_confirm(slug: str, key: str, body: IntakeConfirm):
    """Agent confirms an intake answer (optionally correcting it). Confirms the application answers it
    feeds; a confirmed revenue or record count updates the report as a logged change."""
    with connect() as conn:
        c = client_by_slug(conn, slug)
        cid = c["id"]
        uid = user_id(conn, body.actor)
        r = conn.execute("SELECT * FROM intake_answers WHERE client_id=%s AND item_key=%s", (cid, key)).fetchone()
        if not r:
            raise HTTPException(404)
        value = body.value if body.value is not None else r["value"]
        notes = (r["notes"] or []) + ([f"Corrected by {body.actor} when confirming."] if body.value is not None
                                      and body.value != r["value"] else [])
        conn.execute("""UPDATE intake_answers SET status='confirmed', value=%s, notes=%s, conflict=FALSE,
                        confirmed_by=%s, confirmed_at=now() WHERE id=%s""", (j(value), j(notes), uid, r["id"]))
        applied = []
        if key == "revenue" and isinstance(value, (int, float)):
            cur = conn.execute("SELECT current_value FROM fields WHERE client_id=%s AND key='annual_revenue'",
                               (cid,)).fetchone()["current_value"]
            if cur != value:
                _change_field(conn, cid, "annual_revenue", uid, value,
                              f"Confirmed with client on {r['source_call'] or 'call'} [{r['source_ts']}]",
                              "conversation", r["source_call"])
                applied.append("annual_revenue")
        for app_key in (r["app_keys"] or []):
            a = _confirm_app(conn, cid, app_key, uid)
            if a and a not in applied:
                applied.append(a)
        intake_ingest.after_change(conn, cid, slug, uid, edited=True)
    wiki_render.log(f"review | {slug} — {body.actor} confirmed intake {r['ref']} {r['label']}")
    return {"ok": True, "applied_to": applied}


@app.post("/api/clients/{slug}/intake/escalations")
def intake_escalate(slug: str, body: Escalation):
    with connect() as conn:
        c = client_by_slug(conn, slug)
        conn.execute("INSERT INTO intake_escalations (client_id, text, call_time, source, created_by) "
                     "VALUES (%s,%s,%s,'live',%s)", (c["id"], body.text, body.call_time, user_id(conn, body.actor)))
        intake_ingest.render_intake_page(conn, c["id"], slug)
    wiki_render.log(f"call | {slug} — coverage question logged for a CPL by {body.actor}")
    return {"ok": True}


@app.post("/api/clients/{slug}/intake/ingest")
def intake_ingest_call(slug: str, body: IngestCall):
    """Ingest a call transcript that's already in the wiki (e.g. saved there by the call-ingest skill
    from Wispr Flow). Runs the same pipeline as the command line."""
    name = Path(body.transcript).name
    path = RAW / slug / name
    if not path.exists() or not name.startswith("call_"):
        raise HTTPException(404, f"no transcript {name} in wiki/raw/{slug}/")
    try:
        return intake_ingest.run(slug, str(path))
    except SystemExit as e:
        raise HTTPException(400, str(e))


@app.post("/api/clients/{slug}/ask")
def ask(slug: str, body: Question):
    with connect() as conn:
        c = client_by_slug(conn, slug)
        uid = user_id(conn, body.actor)
        answer, cites, escalated = ask_mod.ask(conn, c["id"], slug, body.question)
        conn.execute("INSERT INTO ask_log (client_id, actor_id, question, answer, citations, escalated) "
                     "VALUES (%s,%s,%s,%s,%s,%s)", (c["id"], uid, body.question, answer, j(cites), escalated))
    short_q = re.sub(r"\s+", " ", body.question)[:80]
    wiki_render.log(f"ask | {slug} — {body.actor}: {short_q}")
    return {"answer": answer, "escalated": escalated, "citations": cites}


# ---------------------------------------------------------------------------------------------
# The built front end (web/dist) is served from the same port, so the app runs without Node:
#   uv run uvicorn api.main:app --port 8000   →   http://localhost:8000
# Rebuild after editing web/src:  cd web && npm install && npm run build   (needs Node)
# ---------------------------------------------------------------------------------------------
_DIST = Path(__file__).resolve().parent.parent / "web" / "dist"
if _DIST.exists():
    app.mount("/", StaticFiles(directory=_DIST, html=True), name="web")
