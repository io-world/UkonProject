"""Intake — the human-in-the-loop step between enrichment and the client pack.

Two inputs, one record per question (table intake_answers):
- **Live taps**: what the agent marks on the app's Intake → Live call screen while talking.
- **The recording**: each call captured by Wispr Flow is saved to the wiki, and the LLM extracts
  answers that must quote the transcript line (pipeline/intake.py holds the prompt and rules).

A client can need several calls. Each call is merged into what's already known:
- an item this call didn't address keeps its earlier answer;
- hedged answers ("mostly", "I think") are flagged, never turned into "yes";
- where the recording disagrees with the agent's tap, the row is flagged as a CONFLICT;
- a different answer to something an agent already confirmed reopens it instead of overwriting.
The client pack is rebuilt after every call. Incomplete intake never blocks it.

    uv run python -m pipeline.intake_ingest [path/to/transcript.md]      (default: call 1 sample)"""
import sys
from pathlib import Path

from . import estimators, intake, llm, report, wiki_render
from .config import CLIENT_SLUG, RAW, WIKI
from .db import client_by_slug, connect, j, user_id
from .sources import read_source


# --- extraction ------------------------------------------------------------------

def extract(transcript: str, call_ref: str, slug: str, items: list[dict], app_bank: list[dict]):
    """(intake_answers, application_answers, coverage_questions, provenance)"""
    out = llm.complete_json(intake.SYSTEM, intake.prompt(items, app_bank, transcript), max_tokens=6000)
    if out and "intake" in out:
        return out["intake"], out.get("application", []), out.get("coverage_questions", []), "live"
    for cache in (RAW / "_cache" / f"call_extraction_{slug}_{call_ref}.md",
                  RAW / "_cache" / f"call_extraction_{call_ref}.md"):
        if cache.exists():
            d = read_source(cache)
            return d.get("intake", []), d.get("application", d.get("answers", [])), d.get("coverage_questions", []), "cached"
    raise SystemExit(f"No cached extraction for {call_ref}. Set ANTHROPIC_API_KEY to extract this call live.")


# --- seeding & live taps ---------------------------------------------------------------

def seed(conn, cid: int):
    """Every question-bank item gets a row from the start; identity items show the Stage 1 value."""
    fields = {r["key"]: r["current_value"] for r in
              conn.execute("SELECT key, current_value FROM fields WHERE client_id=%s", (cid,)).fetchall()}
    for it in intake.load_bank():
        pre = fields.get(it.get("prefill_from")) if it.get("prefill_from") else None
        conn.execute("""INSERT INTO intake_answers (client_id, item_key, ref, section, grp, label, question, value,
                        app_keys) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT (client_id, item_key) DO NOTHING""",
                     (cid, it["key"], it["ref"], it["section"], it.get("group"), it["label"], it["plain"], j(pre),
                      j(it.get("app_keys", []))))
    for q in intake.load_app_bank():
        if q.get("prefill_from") and not q.get("confirm_on_call"):
            v = fields.get(q["prefill_from"])
            ans, norm, status, quote = (str(v) if v is not None else None), "value", "prefilled", "From the database"
        else:
            v, ans, norm, status, quote = None, None, "unknown", "unanswered", None
        conn.execute("""INSERT INTO application_answers (client_id, question_key, question, answer, value, normalized,
                        status, source_quote) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                        ON CONFLICT (client_id, question_key) DO NOTHING""",
                     (cid, q["key"], q["formal"], ans, j(v), norm, status, quote))


def live_dict(conn, cid: int) -> dict:
    """Rebuild the live-tap structure intake.build_rows expects from what the app saved."""
    out = {"s0": {}, "q": {}, "checks": {}}
    for r in conn.execute("SELECT item_key, section, live FROM intake_answers WHERE client_id=%s AND live IS NOT NULL",
                          (cid,)).fetchall():
        lv = r["live"] or {}
        if r["section"] == "identity":
            out["s0"][r["item_key"]] = lv
        elif r["section"] == "walkthrough":
            out["checks"][r["item_key"].replace("check_", "")] = {"text": lv.get("text") or lv.get("note") or "",
                                                                   "flag": lv.get("flag", False)}
        else:
            out["q"][r["item_key"]] = {"value": lv.get("value", ""), "multi": lv.get("multi", []),
                                       "flag": lv.get("flag", False), "note": lv.get("note", "")}
    return out


# --- merging -------------------------------------------------------------------------

def _later_calls(conn, cid: int, call_ref: str) -> set:
    """Calls ingested after this one. Re-ingesting an older call must not overwrite their answers."""
    me = conn.execute("SELECT ingested_at FROM intake_calls WHERE client_id=%s AND call_ref=%s",
                      (cid, call_ref)).fetchone()
    if not me:
        return set()
    return {r["call_ref"] for r in conn.execute(
        "SELECT call_ref FROM intake_calls WHERE client_id=%s AND ingested_at > %s", (cid, me["ingested_at"])).fetchall()}


def _merge_intake(conn, cid: int, row: dict, call_ref: str, later: set = frozenset()) -> str | None:
    old = conn.execute("SELECT * FROM intake_answers WHERE client_id=%s AND item_key=%s",
                       (cid, row["item_key"])).fetchone()
    if old["source_call"] in later:
        return None                     # a newer call already answered this
    addressed = not (row["normalized"] == "unknown" and not row["quote"])
    if not addressed and old["source_call"]:
        return None                     # an earlier call answered it; this one didn't touch it
    if not addressed and old["status"] == row["status"] and (old["notes"] or []) == row["notes"]:
        return None                     # nothing new for an item no call has answered yet
    status, notes, value, answer = row["status"], list(row["notes"]), row["value"], row["answer"]
    if old["status"] == "confirmed":
        if not addressed or intake._same(_bank()[row["item_key"]], old["value"], value):
            return None                 # same as what the agent confirmed
        status = "needs_followup"
        notes.insert(0, f"Changed on {call_ref}; previously confirmed as “{intake._show(old['value'])}”.")
    conn.execute("""UPDATE intake_answers SET answer=%s, value=%s, normalized=%s, status=%s, source_quote=%s,
                    source_ts=%s, source_call=%s, conflict=%s, notes=%s, confirmed_by=NULL, confirmed_at=NULL
                    WHERE id=%s""",
                 (answer, j(value), row["normalized"], status, row["quote"], row["ts"],
                  call_ref if addressed else old["source_call"], row["conflict"], j(notes), old["id"]))
    return status


_BANK = None


def _bank() -> dict:
    global _BANK
    if _BANK is None:
        _BANK = {i["key"]: i for i in intake.load_bank()}
    return _BANK


def _merge_app(conn, cid: int, q: dict, new: dict, call_ref: str, later: set = frozenset()) -> str | None:
    old = conn.execute("SELECT * FROM application_answers WHERE client_id=%s AND question_key=%s",
                       (cid, q["key"])).fetchone()
    if old and old["source_call"] in later:
        return None
    if new.get("normalized", "unknown") == "unknown" and not new.get("quote"):
        return None
    status = intake.hedge_check(new)
    answer = new.get("answer")
    if old and old["status"] == "confirmed":
        if old["normalized"] == new["normalized"]:
            return None
        status = "needs_followup"
        answer = f"Changed on {call_ref}: {answer} (previously confirmed: {old['answer']})"
    conn.execute("""UPDATE application_answers SET answer=%s, value=%s, normalized=%s, status=%s, source_quote=%s,
                    source_ts=%s, source_call=%s, confirmed_by=NULL, confirmed_at=NULL
                    WHERE client_id=%s AND question_key=%s""",
                 (answer, j(new.get("value")), new["normalized"], status, new.get("quote"), new.get("ts"), call_ref,
                  cid, q["key"]))
    return status


# --- derived outputs -------------------------------------------------------------------------

def refresh_exposure(conn, cid: int, slug: str):
    """Recompute the AI exposure score with controls the intake confirmed cleanly. An agent's
    override of the score stays; only the AI recommendation moves."""
    sig = read_source(RAW / slug / "signals.md")["exposure_inputs"]
    answers = conn.execute("SELECT question_key, normalized, status FROM application_answers WHERE client_id=%s",
                           (cid,)).fetchall()
    emp = conn.execute("SELECT current_value FROM fields WHERE client_id=%s AND key='employee_count'",
                       (cid,)).fetchone()["current_value"]
    rec = conn.execute("SELECT current_value FROM fields WHERE client_id=%s AND key='records_estimate'",
                       (cid,)).fetchone()["current_value"]
    ex = estimators.exposure_score(sig["data_class"], int(emp), sig["dmarc"], sig["spf"], sig["online_payments"],
                                   int(rec), estimators.controls_from_answers(answers))
    f = conn.execute("SELECT * FROM fields WHERE client_id=%s AND key='exposure_score'", (cid,)).fetchone()
    agent_owned = f["current_value"] != f["ai_value"]
    conn.execute("UPDATE fields SET ai_value=%s, current_value=CASE WHEN %s THEN current_value ELSE %s END, "
                 "method=%s, updated_at=now() WHERE id=%s",
                 (j(ex["score"]), agent_owned, j(ex["score"]),
                  "Rough proxy, not a security scan: data sensitivity + email accounts + public DNS email settings "
                  "+ online payments + record volume, minus credits for controls the intake confirmed cleanly.",
                  f["id"]))
    conn.execute("UPDATE fields SET current_value=%s, ai_value=%s WHERE client_id=%s AND key='exposure_breakdown'",
                 (j(ex), j(ex), cid))
    return ex


def render_intake_page(conn, cid: int, slug: str, provenance: str = "—"):
    c = conn.execute("SELECT * FROM clients WHERE id=%s", (cid,)).fetchone()
    name = conn.execute("SELECT current_value FROM fields WHERE client_id=%s AND key='legal_name'",
                        (cid,)).fetchone()
    bank = _bank()
    rows = []
    for r in conn.execute("SELECT * FROM intake_answers WHERE client_id=%s ORDER BY id", (cid,)).fetchall():
        it = bank.get(r["item_key"], {})
        rows.append({"item_key": r["item_key"], "ref": r["ref"], "section": r["section"], "group": r["grp"],
                     "label": r["label"], "question": r["question"], "answer": r["answer"], "value": r["value"],
                     "status": r["status"], "quote": r["source_quote"], "ts": r["source_ts"],
                     "source_call": r["source_call"], "notes": r["notes"] or [], "app_keys": it.get("app_keys", []),
                     "conflict": r["conflict"]})
    app_rows = [{"key": a["question_key"], "question": a["question"], "status": a["status"]} for a in
                conn.execute("SELECT * FROM application_answers WHERE client_id=%s ORDER BY id", (cid,)).fetchall()]
    calls = [r["call_ref"] for r in conn.execute(
        "SELECT call_ref FROM intake_calls WHERE client_id=%s ORDER BY ingested_at, id", (cid,)).fetchall()]
    cov = [{"quote": e["text"], "ts": e["call_time"], "call": e["call_ref"]} for e in conn.execute(
        "SELECT * FROM intake_escalations WHERE client_id=%s ORDER BY id", (cid,)).fetchall()]
    text = intake.render_page(slug, str(name["current_value"] if name else c["display_name"]), rows, app_rows,
                              calls, provenance, cov)
    (WIKI / "clients").mkdir(exist_ok=True)
    (WIKI / "clients" / f"{slug}-intake.md").write_text(text)


def after_change(conn, cid: int, slug: str, actor_id: int, edited: bool = False, provenance: str = "—"):
    """Everything downstream of an intake change: exposure, client pack (HTML), wiki pages."""
    ex = refresh_exposure(conn, cid, slug)
    if conn.execute("SELECT 1 FROM report_versions WHERE client_id=%s", (cid,)).fetchone():
        report.refresh_working(conn, cid, actor_id, edited=edited)
    wiki_render.render_client(conn, cid)
    render_intake_page(conn, cid, slug, provenance)
    return ex


# --- one call ------------------------------------------------------------------------------

def run(slug: str = CLIENT_SLUG, transcript_path: str | None = None) -> dict:
    path = Path(transcript_path) if transcript_path else RAW / slug / "call_1_intake.md"
    if not path.is_absolute() and not path.exists():
        path = RAW / slug / path.name
    transcript = path.read_text()
    call_ref = path.stem if path.stem.startswith("call_") else f"call_{path.stem}"
    dest = RAW / slug / f"{call_ref}.md"
    if not dest.exists():                       # transcripts become immutable wiki sources
        dest.write_text(transcript)
    items, app_bank = intake.load_bank(), intake.load_app_bank()
    intake_ans, app_ans, coverage, provenance = extract(transcript, call_ref, slug, items, app_bank)

    with connect() as conn:
        c = client_by_slug(conn, slug)
        cid = c["id"]
        ai = user_id(conn, "Pipeline (AI)")
        seed(conn, cid)
        fields = {r["key"]: r["current_value"] for r in
                  conn.execute("SELECT key, current_value FROM fields WHERE client_id=%s", (cid,)).fetchall()}
        rows = intake.build_rows(items, intake_ans, live_dict(conn, cid), prefills=fields)
        later = _later_calls(conn, cid, call_ref)
        touched = {}
        for row in rows:
            st = _merge_intake(conn, cid, row, call_ref, later)
            if st:
                touched[row["item_key"]] = st
        app_by_key = {a["key"]: a for a in app_ans}
        app_touched = {}
        for q in app_bank:
            if q["key"] in app_by_key:
                st = _merge_app(conn, cid, q, app_by_key[q["key"]], call_ref, later)
                if st:
                    app_touched[q["key"]] = st
        for cq in coverage:
            if not conn.execute("SELECT 1 FROM intake_escalations WHERE client_id=%s AND text=%s",
                                (cid, cq["quote"])).fetchone():
                conn.execute("INSERT INTO intake_escalations (client_id, text, call_time, source, call_ref) "
                             "VALUES (%s,%s,%s,'call',%s)", (cid, cq["quote"], cq.get("ts"), call_ref))
        flagged = sum(1 for s in touched.values() if s == "needs_followup")
        conflicts = sum(1 for r in rows if r["conflict"] and r["item_key"] in touched)
        conn.execute("""INSERT INTO intake_calls (client_id, call_ref, wiki_path, answered, flagged)
                        VALUES (%s,%s,%s,%s,%s) ON CONFLICT (client_id, call_ref) DO UPDATE SET
                        answered=EXCLUDED.answered, flagged=EXCLUDED.flagged""",
                     (cid, call_ref, f"raw/{slug}/{call_ref}.md", len(touched), flagged))
        if c["stage"] in ("enrichment", "indications"):
            conn.execute("UPDATE clients SET stage='intake' WHERE id=%s", (cid,))
        ex = after_change(conn, cid, slug, ai, provenance=provenance)
        still_open = conn.execute("SELECT count(*) AS n FROM intake_answers WHERE client_id=%s AND section<>'walkthrough' "
                                  "AND status IN ('needs_followup','unanswered')", (cid,)).fetchone()["n"]

    summary = {"call_ref": call_ref, "provenance": provenance, "intake_updated": len(touched), "flagged": flagged,
               "conflicts": conflicts, "coverage_questions": len(coverage), "application_updated": len(app_touched),
               "still_open": still_open, "exposure": ex["score"], "band": ex["band"]}
    wiki_render.log(f"call | {slug} — {call_ref}: {len(touched)} intake items updated ({provenance}); {flagged} flagged, "
                    f"{conflicts} conflicts with live taps, {len(coverage)} coverage questions for a CPL; "
                    f"{still_open} still open; exposure {ex['score']}")
    print(f"{call_ref} ingested ({provenance}): {len(touched)} intake items updated, {flagged} flagged, "
          f"{conflicts} conflicts, {len(coverage)} for a CPL; {still_open} still open; exposure {ex['score']} ({ex['band']})")
    return summary


if __name__ == "__main__":
    run(transcript_path=sys.argv[1] if len(sys.argv) > 1 else None)
