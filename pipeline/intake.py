"""Intake call extraction: each recorded call fills the client intake and the application.

Pure logic only (no database), so it can be tested without Postgres:
- the question bank and the extraction prompt
- the hedge check (shared with the application answers)
- reconciling what the agent tapped live against what the recording says
- rendering the completed-intake wiki page

Rules this module keeps:
- Every extracted answer quotes the transcript line it came from, with a timestamp.
- Hedged answers go to follow-up. "Mostly" never becomes "yes".
- Nothing is confirmed here. The agent confirms in the app; the client signs the application.
- Walkthrough items record what the client said about the numbers. They never hold a dollar figure."""
import json
import re
from datetime import datetime
from pathlib import Path

from .config import RAW
from .sources import read_source

BANK_PATH = RAW / "intake" / "intake_questions.md"
APP_BANK_PATH = RAW / "carriers" / "application_questions.md"

HEDGES = re.compile(r"\b(mostly|i think|i don't think|not sure|i believe|probably|i'd have to check|"
                    r"kind of|sort of|usually|most of|not that i know of)\b", re.I)

SYSTEM = """You extract answers from a recorded cyber insurance intake call between an agent and a client.
The agent reads numbered questions aloud ("Question 7", "Formula 6"); use those numbers to anchor answers,
but take the answer from what the CLIENT said, not the agent.

Return JSON: {"intake": [...], "application": [...], "coverage_questions": [...]}

Each "intake" object: key, answer (short plain summary of what the client said), normalized, value,
quote (the client's exact words), ts (the [mm:ss] timestamp of the quote, without brackets).
normalized is one of:
  confirmed  - identity item: the client agreed the pre-filled value is right (value = null)
  corrected  - identity item: the client gave a different value (value = the corrected value)
  option     - single/multi item: value = the matching option string (single) or list of option strings (multi),
               chosen ONLY from the options given
  value      - text/number item: value = the number or short text the client gave
  yes | no | partial
  unknown    - not answered on the call (quote = "")
Each "application" object: key, answer, normalized (yes | no | partial | unknown | value), value, quote, ts.

Each "coverage_questions" object: quote (the client's exact words), ts. List every time the client asks whether
something would be covered. Do not answer it; a licensed coverage specialist will.

Never upgrade a hedged answer ("mostly", "I think", "I believe") to a clean yes or a single option.
Never invent a dollar figure the client didn't say. Never fill an item the client didn't answer."""


def load_bank() -> list[dict]:
    return read_source(BANK_PATH)["items"]


def load_app_bank() -> list[dict]:
    return read_source(APP_BANK_PATH)["questions"]


def prompt(items: list[dict], app_questions: list[dict], transcript: str) -> str:
    intake = [{k: i[k] for k in ("key", "ref", "section", "type", "plain") if k in i}
              | ({"options": i["options"]} if i.get("options") else {}) for i in items]
    covered_by = {a: i["ref"] for i in items for a in i.get("app_keys", [])}
    app = [{"key": q["key"], "question": q["formal"], "asked_as": covered_by.get(q["key"])}
           for q in app_questions if not q.get("prefill_from") or q.get("confirm_on_call")]
    return (f"Intake items:\n{json.dumps(intake, indent=1, ensure_ascii=False)}\n\n"
            f"Application questions (asked_as = the intake question that covers it):\n"
            f"{json.dumps(app, indent=1, ensure_ascii=False)}\n\nTranscript:\n{transcript}")


def hedge_check(item: dict) -> str:
    """Status for an extracted answer. Shared with application answers."""
    norm, quote = item.get("normalized", "unknown"), item.get("quote") or ""
    if norm == "unknown" or not quote:
        return "unanswered" if norm == "unknown" and not quote else "needs_followup"
    if norm == "partial":
        return "needs_followup"
    if norm in ("yes", "no", "option") and HEDGES.search(quote):
        return "needs_followup"
    return "prefilled"


# --- reconcile against the agent's live taps ---------------------------------

def load_live(path: str | Path | None) -> dict:
    """Live taps exported from the intake screen ("Copy answers for ingest"). .md with a json block, or .json."""
    if not path:
        return {}
    p = Path(path)
    data = read_source(p) if p.suffix == ".md" else json.loads(p.read_text())
    return data.get("answers", data)


def _norm(s) -> str:
    return re.sub(r"[^a-z0-9]+", " ", str(s).lower()).strip()


def _num(s):
    m = re.sub(r"[^0-9.]", "", str(s))
    try:
        return float(m) if m else None
    except ValueError:
        return None


def _same(item: dict, a, b) -> bool:
    if item["type"] == "text" and item["section"] != "identity":
        return True                     # free text: the agent's wording is kept as a note, not a conflict
    if item["type"] == "multi":
        return {_norm(x) for x in (a or [])} == {_norm(x) for x in (b or [])}
    if item["type"] == "number" or item["key"] == "revenue":
        na, nb = _num(a), _num(b)
        if na is None or nb is None:
            return True
        if item["key"] == "revenue" and na < 1000:      # "$2.1M" typed live vs 2100000 extracted
            na *= 1_000_000
        if item["key"] == "revenue" and nb < 1000:
            nb *= 1_000_000
        return abs(na - nb) <= 0.02 * max(na, nb)
    return _norm(a) == _norm(b)


def build_rows(items: list[dict], extracted: list[dict], live: dict | None = None,
               prefills: dict | None = None) -> list[dict]:
    """One row per intake item: extraction + hedge status + live-tap reconciliation."""
    by_key = {a["key"]: a for a in extracted}
    live = live or {}
    prefills = prefills or {}
    rows = []
    for it in items:
        a = by_key.get(it["key"], {"normalized": "unknown", "quote": "", "answer": None, "value": None})
        status = hedge_check(a)
        notes = []
        if status == "needs_followup" and a.get("normalized") in ("yes", "no", "option"):
            m = HEDGES.search(a.get("quote") or "")
            if m:
                notes.append(f"Client hedged (“{m.group(0)}”). Confirm before it goes on the application.")
        if status == "needs_followup" and a.get("normalized") == "partial":
            notes.append("Partial answer. Confirm the rest before it goes on the application.")
        value = a.get("value")
        if it.get("prefill_from"):
            pre = prefills.get(it["prefill_from"])
            if a.get("normalized") == "confirmed":
                value = pre
            elif a.get("normalized") == "corrected":
                notes.append(f"Client corrected the pre-filled value ({_money(pre) if it['key'] == 'revenue' else pre}). Confirming it in the app "
                             f"applies it to the report as a logged change.")
            elif a.get("normalized") == "unknown":
                value = pre
                notes.append("Not confirmed on the call; still the Stage 1 value.")
        if it.get("policy") and a.get("normalized") == "unknown":
            notes.append("Pull from the current policy.")

        # live taps
        lv, live_value, conflict = _live_for(it, live), None, False
        if lv is not None:
            live_value = lv["value"]
            if lv.get("flag"):
                status = "needs_followup"
                notes.append("Agent marked the client unsure during the call.")
            if lv.get("note"):
                notes.append(f"Agent note: {lv['note']}")
            if live_value not in (None, "", []) and it["type"] == "text" and it["section"] != "identity" \
                    and a.get("normalized") != "unknown" and _norm(live_value) != _norm(value):
                notes.append(f"Agent typed during the call: “{_show(live_value)}”.")
            if live_value not in (None, "", []):
                extracted_value = value if a.get("normalized") != "confirmed" else prefills.get(it.get("prefill_from"))
                if a.get("normalized") == "unknown":
                    status = "needs_followup"
                    notes.append("Agent tapped an answer, but it isn't on the recording. Confirm with the client.")
                elif a.get("normalized") in ("option", "value", "corrected", "confirmed") \
                        and not _same(it, live_value, extracted_value):
                    conflict, status = True, "needs_followup"
                    notes.append(f"CONFLICT: agent tapped “{_show(live_value)}”; the recording says "
                                 f"“{_show(extracted_value)}”. The recording wins unless the agent decides otherwise.")
        rows.append({
            "item_key": it["key"], "ref": it["ref"], "section": it["section"], "group": it.get("group"),
            "label": it["label"], "question": it["plain"], "answer": a.get("answer"),
            "normalized": a.get("normalized", "unknown"), "value": value, "status": status,
            "quote": a.get("quote") or None, "ts": a.get("ts"), "live_value": live_value,
            "conflict": conflict, "notes": notes, "app_keys": it.get("app_keys", []),
        })
    return rows


def _live_for(it: dict, live: dict):
    """Map the intake screen's saved state to one item. Returns {'value','flag','note'} or None."""
    if not live:
        return None
    k = it["key"]
    if it["section"] == "identity":
        s = (live.get("s0") or {}).get(k)
        if not s:
            return None
        v = s.get("value") if s.get("value") not in (None, "") and s.get("corrected") else None
        return {"value": v, "flag": s.get("flag"), "note": s.get("note")}
    if it["section"] == "walkthrough":
        c = (live.get("checks") or {}).get(k.replace("check_", ""))
        if not c:
            return None
        note = c.get("text") or ""
        if c.get("flag"):
            note = (note + " " if note else "") + "(Agent marked: this changes an input in the report.)"
        return {"value": None, "flag": False, "note": note}
    q = (live.get("q") or {}).get(k)
    if not q:
        return None
    v = q.get("multi") if it["type"] == "multi" else q.get("value")
    return {"value": v, "flag": q.get("flag"), "note": q.get("note")}


def _money(v) -> str:
    n = _num(v) if not isinstance(v, (int, float)) else v
    return f"${n:,.0f}" if n is not None else str(v)


def _show(v) -> str:
    if isinstance(v, list):
        return ", ".join(map(str, v))
    if isinstance(v, (int, float)) and v >= 10_000:
        return f"{v:,.0f}"
    return "" if v is None else str(v)


# --- completed-intake page -----------------------------------------------------

STATUS_LABEL = {"prefilled": "ready to confirm", "needs_followup": "needs follow-up",
                "unanswered": "not covered on the call", "confirmed": "confirmed"}


def render_page(slug: str, client_name: str, rows: list[dict], app_rows: list[dict],
                calls: list[str], provenance: str, coverage_questions: list[dict] | None = None) -> str:
    """Rows come from the database (merged across calls); each carries its own source_call."""
    def cite_for(call):
        return f"[[raw/{slug}/{call}|{call}]]" if call else "the call screen"
    counts = {s: sum(r["status"] == s for r in rows) for s in STATUS_LABEL}
    complete = all(r["status"] == "confirmed" for r in rows if r["section"] != "walkthrough")
    out = ["---", "type: client-intake", "generated: true", f"client: {slug}",
           f"complete: {str(complete).lower()}", "calls:"] + [f"  - raw/{slug}/{c}" for c in calls] + [
           f"last_rendered: {datetime.now().astimezone().isoformat(timespec='seconds')}", "---", "",
           f"# Intake — {client_name}", "",
           "> [!warning] Generated page — do not edit in Obsidian",
           "> Rendered from the database after each call is ingested and whenever an agent confirms an answer",
           "> in the app (logged with their name).", "",
           f"Calls: {', '.join(cite_for(c) for c in calls) or 'none yet'} · last extraction: {provenance} · "
           f"{counts['confirmed']} confirmed · {counts['prefilled']} ready to confirm · "
           f"{counts['needs_followup']} need follow-up · {counts['unanswered']} not covered", ""]
    if not complete:
        out += ["**Status: draft.** The intake is complete when every identity and exposure item is "
                "confirmed by an agent.", ""]

    def item(r):
        val = (_money(r["value"]) if r["item_key"] == "revenue" and r["value"] is not None else _show(r["value"])) \
            or (r["answer"] or "—")
        status = "not asked" if r["section"] == "walkthrough" and r["status"] == "unanswered" else STATUS_LABEL[r["status"]]
        line = [f"### {r['ref']} · {r['label']}", f"- Asked: {r['question']}",
                f"- Answer: **{val}**" + (f" — {r['answer']}" if r["answer"] and r["answer"] != val else ""),
                f"- Status: `{status}`"]
        if r["quote"]:
            line.append(f"- Client said: “{r['quote']}” ({cite_for(r.get('source_call'))} {r['ts'] or ''})".rstrip())
        for n in r["notes"]:
            line.append(f"- {'> ' if n.startswith('CONFLICT') else ''}{n}")
        if r["app_keys"]:
            line.append(f"- Fills application: {', '.join(r['app_keys'])}")
        return line + [""]

    out += ["## Section 0 · Business identity", ""]
    for r in rows:
        if r["section"] == "identity":
            out += item(r)
    out += ["## Section 1 · Exposure questions", ""]
    group = None
    for r in rows:
        if r["section"] == "exposure":
            if r["group"] != group:
                group = r["group"]
                out += [f"#### {group}", ""]
            out += item(r)
    out += ["## Section 2 · Walkthrough reactions", "",
            "What the client said about the numbers. Figures themselves live in the report.", ""]
    for r in rows:
        if r["section"] == "walkthrough":
            out += item(r)
    out += ["## Coverage questions for a CPL", ""]
    if coverage_questions:
        out += ["Not answered on the call. Escalate to a licensed coverage specialist for a written answer.", ""]
        out += [f"- “{c['quote']}” ({cite_for(c.get('call'))} {c.get('ts') or ''})".rstrip() for c in coverage_questions] + [""]
    else:
        out += ["None asked.", ""]
    if app_rows:
        out += ["## Application coverage", "", "| Application question | Status | From |", "|---|---|---|"]
        from_ref = {k: r["ref"] for r in rows for k in r["app_keys"]}
        for a in app_rows:
            out.append(f"| {a['question']} | {STATUS_LABEL.get(a['status'], a['status'])} | {from_ref.get(a['key'], '—')} |")
        out.append("")
    return "\n".join(out)
