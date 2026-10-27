"""'Ask about this client' — the Stage 3 skill, exposed to the app.

Read-only by construction: the only tools are readers. Numbers come from DB tools;
the 'why' comes from wiki pages. Coverage-interpretation questions escalate to a CPL."""
import json
import re

from pipeline import llm
from pipeline.config import ANTHROPIC_MODEL, WIKI

SYSTEM = """You answer an insurance agent's questions about one client, before or after a meeting.
Rules:
- You are read-only. If the agent wants to change a value, tell them to use the slider in the report
  so the change is logged with their name.
- Every number must come from a tool result. Never estimate or round differently than the tool shows.
- Explain 'why' using the wiki pages (methods, sources, conflicts).
- If the question asks whether something would be covered or paid, or compares policy wording,
  call escalate_to_cpl and tell the agent to check with their Cyber Practice Leader.
- End with a line 'Sources:' listing field keys (db:<key>), carriers (db:indications:<carrier>)
  or wiki paths you used. Keep answers under 120 words."""

TOOLS = [
    {"name": "get_fields", "description": "Current values, AI recommendations, confidence, method and sources for client fields.",
     "input_schema": {"type": "object", "properties": {"keys": {"type": "array", "items": {"type": "string"}}}}},
    {"name": "get_indications", "description": "Locked carrier indications: limits, deductibles, premiums, sublimits, conditions.",
     "input_schema": {"type": "object", "properties": {"carrier": {"type": "string"}}}},
    {"name": "get_audit", "description": "Timeline of who changed what and when, with reasons.",
     "input_schema": {"type": "object", "properties": {}}},
    {"name": "get_application", "description": "Application answers from the call, with status and transcript quotes.",
     "input_schema": {"type": "object", "properties": {}}},
    {"name": "read_wiki", "description": "Read a wiki page: 'client', 'industry', or a raw source like 'raw/sloanslake/website.md'.",
     "input_schema": {"type": "object", "properties": {"page": {"type": "string"}}, "required": ["page"]}},
    {"name": "escalate_to_cpl", "description": "Flag that this question needs a Cyber Practice Leader.",
     "input_schema": {"type": "object", "properties": {"reason": {"type": "string"}}, "required": ["reason"]}},
]


def _readers(conn, cid, slug):
    def get_fields(keys=None):
        q = "SELECT key,label,current_value,ai_value,ai_low,ai_high,confidence,method,sources FROM fields WHERE client_id=%s"
        rows = conn.execute(q, (cid,)).fetchall()
        return [dict(r, ai_low=float(r["ai_low"]) if r["ai_low"] is not None else None,
                     ai_high=float(r["ai_high"]) if r["ai_high"] is not None else None)
                for r in rows if not keys or r["key"] in keys]

    def get_indications(carrier=None):
        rows = conn.execute("""SELECT carrier,tier,limit_amount,deductible,premium,basis_revenue,sublimits,conditions,
                               bi_waiting_hours,specimen_form,expires_on::text FROM indications WHERE client_id=%s""",
                            (cid,)).fetchall()
        return [dict(r) for r in rows if not carrier or carrier.lower() in r["carrier"].lower()]

    def get_audit():
        return [dict(r, at=str(r["at"])) for r in
                conn.execute("SELECT * FROM audit_trail WHERE client_id=%s ORDER BY at", (cid,)).fetchall()]

    def get_application():
        return [dict(r, confirmed_at=str(r["confirmed_at"])) for r in conn.execute(
            "SELECT question_key,question,answer,status,source_quote,source_ts,confirmed_at FROM application_answers "
            "WHERE client_id=%s", (cid,)).fetchall()]

    def read_wiki(page):
        allowed = {"client": WIKI / "clients" / f"{slug}.md",
                   "industry": WIKI / "industries" / "621210-dental-offices.md"}
        path = allowed.get(page) or (WIKI / page)
        path = path.resolve()
        if not str(path).startswith(str(WIKI.resolve())) or not path.exists():
            return "not found"
        return path.read_text()[:6000]

    return {"get_fields": get_fields, "get_indications": get_indications, "get_audit": get_audit,
            "get_application": get_application, "read_wiki": read_wiki}


def ask_live(conn, cid, slug, question):
    tools = _readers(conn, cid, slug)
    msgs = [{"role": "user", "content": question}]
    escalated = False
    citations = []
    for _ in range(6):
        resp = llm.client().messages.create(model=ANTHROPIC_MODEL, max_tokens=800, system=SYSTEM,
                                            tools=TOOLS, messages=msgs)
        if resp.stop_reason != "tool_use":
            text = "".join(b.text for b in resp.content if b.type == "text")
            return text, citations, escalated
        msgs.append({"role": "assistant", "content": resp.content})
        results = []
        for b in resp.content:
            if b.type != "tool_use":
                continue
            if b.name == "escalate_to_cpl":
                escalated = True
                out = "escalation recorded"
            else:
                out = tools[b.name](**(b.input or {}))
                citations.append({"tool": b.name, "input": b.input})
            results.append({"type": "tool_result", "tool_use_id": b.id, "content": json.dumps(out, default=str)[:12000]})
        msgs.append({"role": "user", "content": results})
    return "I couldn't finish that lookup — try a narrower question.", citations, escalated


COVERAGE_Q = re.compile(r"\b(cover(ed|s)?|pay(s)? for|would .* pay|claim|exclu)", re.I)


def ask_offline(conn, cid, slug, question):
    """Keyword router used when no API key is set. Same rules: DB numbers, wiki reasons, escalation."""
    t = _readers(conn, cid, slug)
    q = question.lower()
    if COVERAGE_Q.search(q) and not re.search(r"\b(premium|price|cost)\b", q):
        return ("That's a coverage-interpretation question, so I won't answer it from the file. "
                "Loop in your Cyber Practice Leader (Sam Ortiz) — they can check the policy wording.\n"
                "Sources: industry page — escalation triggers"), [{"tool": "escalate_to_cpl"}], True
    if "revenue" in q:
        f = t["get_fields"](["annual_revenue"])[0]
        return (f"Revenue in the report is ${f['current_value']:,.0f} (AI estimated ${f['ai_value']:,.0f}, "
                f"range ${f['ai_low']:,.0f}–${f['ai_high']:,.0f}, {f['confidence']} confidence). Why: {f['method']}\n"
                "Sources: db:annual_revenue, wiki:client"), [{"tool": "get_fields", "input": ["annual_revenue"]}], False
    if any(w in q for w in ("employee", "staff", "headcount")):
        f = t["get_fields"](["employee_count"])[0]
        return (f"{f['current_value']} employees in the report ({f['confidence']} confidence). {f['method']}\n"
                "Sources: db:employee_count, wiki:client"), [{"tool": "get_fields", "input": ["employee_count"]}], False
    if any(w in q for w in ("premium", "price", "cost", "carrier", "quote", "option")):
        sel = t["get_fields"](["selected_carrier"])[0]["current_value"]
        rows = sorted(t["get_indications"](), key=lambda r: (r["carrier"], r["limit_amount"]))
        lines = [f"{r['carrier']}{' (shown to client)' if r['carrier'] == sel else ''} · {r['tier']}: "
                 f"${r['limit_amount']:,} limit / ${r['deductible']:,} deductible — ${r['premium']:,}/yr"
                 for r in rows]
        return ("\n".join(lines) + "\nThese are non-binding indications.\nSources: db:indications"), \
               [{"tool": "get_indications"}], False
    if any(w in q for w in ("who", "changed", "moved", "audit", "history")):
        rows = t["get_audit"]()[-5:]
        lines = [f"{r['at'][:16]} — {r['actor']}: {r['event']} {r['subject']}" for r in rows]
        return "Latest changes:\n" + "\n".join(lines) + "\nSources: db:audit_trail", [{"tool": "get_audit"}], False
    if any(w in q for w in ("mfa", "backup", "edr", "application", "follow", "call")):
        rows = [r for r in t["get_application"]() if r["status"] == "needs_followup"]
        lines = [f"{r['question_key']}: {r['answer']} (\"{r['source_quote']}\" at {r['source_ts']})" for r in rows]
        return ("Needs follow-up before the application goes out:\n" + "\n".join(lines) +
                "\nSources: db:application_answers"), [{"tool": "get_application"}], False
    return ("I can answer questions about this client's revenue, staff, exposure, carrier options, the call answers, "
            "or who changed what. Set ANTHROPIC_API_KEY for open-ended questions.\nSources: —"), [], False


def ask(conn, cid, slug, question):
    if llm.available():
        return ask_live(conn, cid, slug, question)
    return ask_offline(conn, cid, slug, question)
