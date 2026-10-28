"""FastAPI over the system of record. The UI never writes a premium: there is no route for it."""
import re
from datetime import date

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from pathlib import Path

from pipeline import bind as bind_mod
from pipeline import html_report, indications, intake, intake_ingest, report, stages, wiki_render
from pipeline.config import RAW, WIKI
from pipeline.sources import read_source
from pipeline.db import client_by_slug, connect, j, user_id

from . import ask as ask_mod
from . import chat as chat_mod

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
        except Exception as e:
            if "connection" in str(e).lower() and "refused" in str(e).lower():
                return JSONResponse(status_code=503, content={"detail": "Can't reach the database. Start it: "
                                    "scripts/db.sh start (then refresh this page)."})
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
        return {"client": c | {"days_to_renewal": days}, "entities": ents, "fields": fields,
                "progress": stages.derive(conn, c["id"])}


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


# ---------------------------------------------------------------------------------------------
# Stage 2: get indications. Send the five fields to carriers (gated on Stage 1), bring replies in from the
# inbox, and show what each carrier said. Carrier figures are read-only: there is no route that writes one.
# ---------------------------------------------------------------------------------------------

class SendRequest(Actor):
    carriers: list[str]


class IngestReply(Actor):
    path: str


class Review(Actor):
    decision: str            # confirmed | rejected
    note: str | None = None


@app.get("/api/clients/{slug}/indications")
def indications_view(slug: str):
    with connect() as conn:
        c = client_by_slug(conn, slug)
        st = indications.state(conn, c["id"])
    return st | {"panel": indications.panel()}


@app.post("/api/clients/{slug}/indications/send")
def indications_send(slug: str, body: SendRequest):
    with connect() as conn:
        c = client_by_slug(conn, slug)
        uid = user_id(conn, body.actor)
        prior = conn.execute("SELECT 1 FROM indication_requests WHERE client_id=%s", (c["id"],)).fetchone()
        try:
            n = indications.request_all(conn, c["id"], uid, "re-request (reviewed basis)" if prior else "initial",
                                        gate=True, carriers=body.carriers)
        except ValueError as e:
            raise HTTPException(409, str(e))
        indications.render_wiki(conn, c["id"])
    wiki_render.log(f"request | {slug} — {body.actor} sent indication requests to {', '.join(body.carriers)}")
    return {"sent": n}


@app.post("/api/clients/{slug}/indications/ingest")
def indications_ingest(slug: str, body: IngestReply):
    """Ingest a carrier reply that's waiting in the client's inbox (wiki/raw/<slug>/indications/)."""
    with connect() as conn:
        c = client_by_slug(conn, slug)
        inbox = indications.state(conn, c["id"])["inbox"]
        if body.path not in inbox:
            raise HTTPException(404, f"{body.path} isn't waiting in the inbox")
        if body.path != inbox[0]:
            raise HTTPException(409, f"Replies arrive in date order: take in {inbox[0].split('/')[-1]} first")
        uid = user_id(conn, body.actor)
        try:
            res = indications.ingest(conn, c["id"], body.path, uid, input_by=uid)
        except ValueError as e:
            raise HTTPException(409, str(e))
        indications.after_change(conn, c["id"], uid)
    wiki_render.log(f"indication | {slug} — {res['carrier']} via {res['channel']} ingested by {body.actor}: "
                    + "; ".join(res["options"]))
    return res


@app.post("/api/clients/{slug}/indications/versions/{vid}/review")
def indications_review(slug: str, vid: int, body: Review):
    with connect() as conn:
        c = client_by_slug(conn, slug)
        uid = user_id(conn, body.actor)
        try:
            res = indications.review_version(conn, c["id"], vid, uid, body.decision, body.note)
        except LookupError as e:
            raise HTTPException(404, str(e))
        except ValueError as e:
            raise HTTPException(409, str(e))
        indications.after_change(conn, c["id"], uid)
    wiki_render.log(f"review | {slug} — {body.actor} {res['review']} {res['carrier']} {res['tier']} figures")
    return res


class ActionDone(Actor):
    note: str


@app.post("/api/clients/{slug}/indications/actions/{aid}/done")
def indications_action_done(slug: str, aid: int, body: ActionDone):
    """Close a follow-up a carrier reply created (e.g. "tell the client the price moved"). The note is required."""
    if not body.note.strip():
        raise HTTPException(400, "Say what you did (the note is logged with your name)")
    with connect() as conn:
        c = client_by_slug(conn, slug)
        uid = user_id(conn, body.actor)
        r = conn.execute("""UPDATE indication_actions SET status='done', closed_by=%s, closed_at=now(), close_note=%s
                            WHERE id=%s AND client_id=%s AND status='open' RETURNING text""",
                         (uid, body.note.strip(), aid, c["id"])).fetchone()
        if not r:
            raise HTTPException(404, "No open action with that id")
        indications.render_wiki(conn, c["id"])
    wiki_render.log(f"action | {slug} — {body.actor} closed: {r['text'][:80]} ({body.note.strip()})")
    return {"ok": True}


@app.get("/api/clients/{slug}/report")
def get_report(slug: str, mode: str = "agent", version: int | None = None):
    """mode=agent: the latest version (the working draft); mode=client: the latest submitted or sent one;
    version=N: that exact version, read-only (used by the locked-versions dropdown)."""
    with connect() as conn:
        c = client_by_slug(conn, slug)
        if version is not None:
            v = conn.execute("SELECT * FROM report_versions WHERE client_id=%s AND version_no=%s",
                             (c["id"], version)).fetchone()
            if not v:
                raise HTTPException(404, f"no version {version}")
        elif mode == "client":
            v = conn.execute("""SELECT * FROM report_versions WHERE client_id=%s AND state IN ('submitted','sent')
                                ORDER BY version_no DESC LIMIT 1""", (c["id"],)).fetchone()
        else:
            v = conn.execute("SELECT * FROM report_versions WHERE client_id=%s ORDER BY version_no DESC LIMIT 1",
                             (c["id"],)).fetchone()
        if not v:
            return {"version": None}
        return {"version": {k: v[k] for k in ("version_no", "state", "created_at", "submitted_at", "sent_at",
                                              "withdrawn_at", "withdraw_reason")},
                "snapshot": v["snapshot"]}


@app.get("/api/clients/{slug}/versions")
def versions(slug: str):
    with connect() as conn:
        c = client_by_slug(conn, slug)
        return conn.execute("""SELECT v.version_no, v.state, v.created_at, v.submitted_at, v.sent_at,
                               v.withdrawn_at, v.withdraw_reason, wu.name AS withdrawn_by,
                               cu.name AS created_by, su.name AS submitted_by,
                               v.snapshot->'facts'->'annual_revenue'->>'value' AS revenue,
                               v.snapshot->'facts'->'employee_count'->>'value' AS employees,
                               v.snapshot->'exposure'->>'score' AS exposure,
                               v.snapshot->>'selected_carrier' AS carrier
                               FROM report_versions v JOIN users cu ON cu.id=v.created_by
                               LEFT JOIN users su ON su.id=v.submitted_by
                               LEFT JOIN users wu ON wu.id=v.withdrawn_by
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
        return html_report.render(v["snapshot"], v, client_view=v["state"] in ("submitted", "sent", "superseded", "withdrawn"))


@app.post("/api/clients/{slug}/report/submit")
def submit(slug: str, body: Actor):
    with connect() as conn:
        c = client_by_slug(conn, slug)
        try:
            v = report.submit(conn, c["id"], user_id(conn, body.actor))
        except ValueError as e:
            raise HTTPException(409, str(e))
    wiki_render.log(f"report | {slug} — v{v['version_no']} submitted (locked) by {body.actor}")
    return {"version_no": v["version_no"], "state": v["state"]}


class UndoSubmit(Actor):
    reason: str | None = None


@app.post("/api/clients/{slug}/report/undo-submit")
def undo_submit(slug: str, body: UndoSubmit):
    with connect() as conn:
        c = client_by_slug(conn, slug)
        try:
            res = report.undo_submit(conn, c["id"], user_id(conn, body.actor), (body.reason or "").strip() or None)
        except ValueError as e:
            raise HTTPException(409, str(e))
        wiki_render.render_client(conn, c["id"])
    wiki_render.log(f"report | {slug} — v{res['withdrawn']} submit undone (withdrawn) by {body.actor}"
                    + (f" ({body.reason.strip()})" if (body.reason or '').strip() else "")
                    + f"; editing continues in v{res['draft']}")
    return res


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
    # Where every block on this page comes from, as wiki paths (shown on the page, openable via /api/wiki).
    industry_path = "wiki/industries/621210-dental-offices.md"
    with connect() as conn:
        letter = conn.execute("""SELECT s.path FROM indications i JOIN indication_versions v ON v.id = i.id
                                 JOIN indication_sources s ON s.id = v.source_id
                                 WHERE i.client_id=%s AND i.carrier=%s ORDER BY i.tier LIMIT 1""",
                              (c["id"], snap["selected_carrier"])).fetchone()
    letter_path = f"wiki/{letter['path']}" if letter else None
    cached = snap["narrative"].get("_provenance") == "cached"
    sources = {
        "pitch": [industry_path, f"wiki/clients/{slug}.md"] + ([f"wiki/raw/_cache/narrative_{slug}.md"] if cached else []),
        "pitch_figures": [p for p in [letter_path] if p],
        "objections": [f"{industry_path}#Objection library"]
                      + ([f"wiki/raw/_cache/narrative_{slug}.md"] if cached else []),
        "escalations": [f"{industry_path}#Escalation triggers"],
        "specimen": ["wiki/raw/carriers/specimen_map.md"],
        "specimen_form": [p for p in [letter_path] if p],
        "conditions": [p for p in [letter_path] if p] + [f"wiki/clients/{slug}-indications.md"],
        "research": sorted({f"wiki/{r['wiki']}.md" for r in report.research_items("621210", "agent_brief")}),
        "application": ["wiki/raw/carriers/application_questions.md", f"wiki/clients/{slug}-intake.md"],
        "people": [f"wiki/raw/{slug}/people.md"],
    }
    people_file = RAW / slug / "people.md"
    people = read_source(people_file)["people"] if people_file.exists() else []
    return {
        "sources": sources,
        "pitch": snap["narrative"]["agent_pitch"],
        "recommended": snap["options"].get("recommended"),
        "carrier": snap["selected_carrier"],
        "objections": objections,
        "escalations": _bullets(industry, "## Escalation triggers"),
        "specimen": specimen.get(snap["selected_carrier"], {}),
        "conditions": next((c["conditions"] for c in snap["carriers"] if c["carrier"] == snap["selected_carrier"]), []),
        "research": [dict(r, wiki=f"wiki/{r['wiki']}.md") for r in report.research_items("621210", "agent_brief")],
        "application_preview": [{"key": q["key"], "plain": q["plain"], "gate": q.get("gate", False)}
                                for q in questions if not q.get("prefill_from")],
        "application_status": {a["question_key"]: a["status"] for a in apps},
        "people": people,
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


# ---------------------------------------------------------------------------------------------
# Stage 5 (present, apply, bind): live call screen + recorded calls, one record per question-bank item
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
        app_rows = {a["question_key"]: {"question": a["question"], "answer": a["answer"], "normalized": a["normalized"],
                                        "status": a["status"]} for a in conn.execute(
            "SELECT question_key, question, answer, normalized, status FROM application_answers WHERE client_id=%s",
            (c["id"],)).fetchall()}
    bank = intake.load_bank()
    items = []
    for it in bank:
        r = rows.get(it["key"]) or {}
        f = fields.get(it.get("prefill_from")) if it.get("prefill_from") else None
        items.append(it | {"row": r, "app": [app_rows[k] | {"key": k} for k in (it.get("app_keys") or []) if k in app_rows],
                           "prefill": None if not f else {
            "value": f["current_value"], "confidence": f["confidence"], "method": f["method"],
            "needs_review": f["needs_review"]}})
    ingested = {c["call_ref"] for c in calls}
    transcripts = sorted(p.name for pat in ("call_*.md", "email_*.md") for p in (RAW / slug).glob(pat))
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
        corrected = body.value is not None and body.value != r["value"]
        for app_key in (r["app_keys"] or []):
            if corrected:   # the application is read-only now: a correction here is what the application says
                text = ", ".join(map(str, value)) if isinstance(value, list) else (f"${value:,.0f}" if key == "revenue"
                       and isinstance(value, (int, float)) else str(value))
                low = text.strip().lower()
                norm = "yes" if low.startswith("yes") else "no" if low.startswith("no") else \
                       "partial" if low.startswith(("partial", "some")) else None
                if isinstance(value, (int, float)):
                    conn.execute("UPDATE application_answers SET value=%s WHERE client_id=%s AND question_key=%s",
                                 (j(value), cid, app_key))
                a = _confirm_app(conn, cid, app_key, uid, text, norm)
            else:
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
    if not path.exists() or not name.startswith(("call_", "email_")):
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
# Stage 4: chat with Claude over the client wiki (web search as a fallback). Read-only.
# ---------------------------------------------------------------------------------------------

class ChatTurn(BaseModel):
    role: str            # user | assistant
    content: str


class ChatRequest(Actor):
    messages: list[ChatTurn]
    web: bool = True     # False = wiki only


@app.post("/api/clients/{slug}/chat")
def chat(slug: str, body: ChatRequest):
    history = [m.model_dump() for m in body.messages if m.role in ("user", "assistant")][-12:]
    if not history or history[-1]["role"] != "user" or not history[-1]["content"].strip():
        raise HTTPException(400, "Ask a question")
    with connect() as conn:
        c = client_by_slug(conn, slug)
        uid = user_id(conn, body.actor)
        try:
            out = chat_mod.chat(conn, c["id"], slug, history, body.web)
        except Exception as e:      # API errors (rate limit, bad key, network) reach the chat as a message
            raise HTTPException(502, f"Claude couldn't answer: {type(e).__name__}: {str(e)[:200]}")
        conn.execute("INSERT INTO ask_log (client_id, actor_id, question, answer, citations, escalated) "
                     "VALUES (%s,%s,%s,%s,%s,%s)",
                     (c["id"], uid, history[-1]["content"], out["answer"],
                      j({"channel": "stage4_chat", "source": out["source"], "wiki": out["wiki"], "web": out["web"]}),
                      out["escalated"]))
    short_q = re.sub(r"\s+", " ", history[-1]["content"])[:80]
    wiki_render.log(f"ask | {slug} — {body.actor} (Stage 4 chat, {out['source']}): {short_q}")
    return out


@app.get("/api/wiki")
def wiki_page(path: str):
    """Read-only view of one wiki page, so a cited source can be opened from the chat."""
    from fastapi.responses import FileResponse, PlainTextResponse
    p = (WIKI / path.split("#", 1)[0].removeprefix("wiki/")).resolve()
    if not str(p).startswith(str(WIKI.resolve())) or p.suffix not in (".md", ".pdf") or not p.exists():
        raise HTTPException(404, "no such wiki page")
    if p.suffix == ".pdf":
        return FileResponse(p, media_type="application/pdf")
    return PlainTextResponse(p.read_text())


# ---------------------------------------------------------------------------------------------
# Stage 5's decision + Stage 6: final terms, bind, report (pipeline/bind.py). No route writes a carrier figure.
# ---------------------------------------------------------------------------------------------
class Decision(Actor):
    stage: str
    decision: str
    carrier: str | None = None
    tier: str | None = None
    reason: str | None = None
    note: str | None = None
    source_type: str = "conversation"


class QuoteIngest(Actor):
    path: str


class QuoteReview(Actor):
    decision: str
    note: str | None = None


class ConditionSet(Actor):
    met: bool
    evidence: str | None = None


def _bind_call(slug, actor, fn, log=None):
    with connect() as conn:
        c = client_by_slug(conn, slug)
        uid = user_id(conn, actor)
        try:
            res = fn(conn, c["id"], uid)
        except LookupError as e:
            raise HTTPException(404, str(e))
        except ValueError as e:
            if str(e).startswith("unknown client"):
                raise
            raise HTTPException(409, str(e))
        bind_mod.render_wiki(conn, c["id"])
    if log:
        wiki_render.log(f"{log} | {slug} — {actor}")
    return res


@app.get("/api/clients/{slug}/close")
def close_view(slug: str):
    with connect() as conn:
        c = client_by_slug(conn, slug)
        return bind_mod.state(conn, c["id"])


@app.post("/api/clients/{slug}/decision")
def decision(slug: str, body: Decision):
    if body.source_type not in SOURCE_TYPES:
        raise HTTPException(400, f"source_type must be one of {', '.join(SOURCE_TYPES)}")
    return _bind_call(slug, body.actor, lambda conn, cid, uid: bind_mod.decide(
        conn, cid, uid, body.stage, body.decision, body.carrier, body.tier, body.reason, body.note, body.source_type),
        f"decision {body.stage}: {body.decision}")


@app.post("/api/clients/{slug}/quote/ingest")
def quote_ingest(slug: str, body: QuoteIngest):
    def fn(conn, cid, uid):
        c = conn.execute("SELECT slug FROM clients WHERE id=%s", (cid,)).fetchone()
        conn.execute("SELECT pg_advisory_xact_lock(%s)", (cid,))  # one take-in at a time per client; held to commit
        if conn.execute("SELECT 1 FROM firm_quotes WHERE client_id=%s AND path=%s", (cid, body.path)).fetchone():
            return {"skipped": True, "path": body.path}       # already taken in (e.g. a double click): not an error
        if body.path not in bind_mod.quote_inbox(conn, cid, c["slug"]):
            raise LookupError(f"{body.path} isn't waiting in the quote inbox")
        return bind_mod.ingest_quote(conn, cid, body.path, uid)
    return _bind_call(slug, body.actor, fn, f"firm quote ingested: {body.path}")


@app.post("/api/clients/{slug}/quote/review")
def quote_review(slug: str, body: QuoteReview):
    return _bind_call(slug, body.actor, lambda conn, cid, uid: bind_mod.review_quote(conn, cid, uid, body.decision, body.note),
                      f"firm quote {body.decision}")


@app.post("/api/clients/{slug}/conditions/{cond_id}")
def condition_set(slug: str, cond_id: int, body: ConditionSet):
    return _bind_call(slug, body.actor, lambda conn, cid, uid: bind_mod.set_condition(conn, cid, cond_id, uid, body.met, body.evidence),
                      f"bind condition {cond_id} {'met' if body.met else 'reopened'}")


@app.post("/api/clients/{slug}/bind")
def bind_now(slug: str, body: Actor):
    res = _bind_call(slug, body.actor, lambda conn, cid, uid: bind_mod.bind(conn, cid, uid), "bound (simulated)")
    return {"policy_number": res["policy_number"]}


# ---------------------------------------------------------------------------------------------
# Demo reset (/reset page): everything back to the seeded starting state. Local demo only.
# ---------------------------------------------------------------------------------------------
class ResetBody(BaseModel):
    confirm: bool = False
    live_ai: bool = False


@app.post("/api/reset")
def reset_demo_route(body: ResetBody):
    if not body.confirm:
        raise HTTPException(400, "Confirm the reset")
    import time
    from pipeline import run_all
    t0 = time.time()
    res = run_all.reset_demo(offline=not body.live_ai)
    return res | {"seconds": round(time.time() - t0, 1)}


# ---------------------------------------------------------------------------------------------
# The built front end (web/dist) is served from the same port, so the app runs without Node:
#   uv run uvicorn api.main:app --port 8000   →   http://localhost:8000
# Rebuild after editing web/src:  cd web && npm install && npm run build   (needs Node)
# ---------------------------------------------------------------------------------------------
_DIST = Path(__file__).resolve().parent.parent / "web" / "dist"
if _DIST.exists():
    app.mount("/", StaticFiles(directory=_DIST, html=True), name="web")
