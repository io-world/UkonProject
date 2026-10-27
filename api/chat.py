"""Stage 4 · Equip the agent — a chat with Claude over the client wiki, with the web as a fallback.

How an answer is sourced (decided by which tools ran, not by what the model says about itself):
  - "wiki"  every fact came from the wiki (search_wiki / read_wiki) or the database readers
  - "web"   Claude searched the internet (Anthropic's server-side web_search tool)
  - "both"  it used both; the answer must say which part came from where
  - "none"  it answered without looking anything up (shown as unverified)
The wiki is always tried first. "Wiki only" mode doesn't offer the web tool at all.

Same guardrails as "Ask about this client": read-only, numbers only from tool results, coverage
questions escalate to a CPL. Without an API key, a keyword search over the wiki answers instead
(no web). Chat history is sent back as plain text each turn; nothing is stored but the ask_log row."""
import json
import re
from pathlib import Path

from pipeline import llm
from pipeline.config import ANTHROPIC_MODEL, WIKI

from .ask import COVERAGE_Q, TOOLS as ASK_TOOLS, _readers

WEB_TOOL = {"type": "web_search_20250305", "name": "web_search", "max_uses": 3}

SYSTEM = """You are the research assistant on an insurance agent's "Equip the agent" screen, helping them get ready
to present cyber insurance to one client. The client's knowledge base is an Obsidian wiki (sources, the generated
client page, carrier indications, call answers, the shared dental industry page, cited research).

How to answer:
1. ALWAYS look in the wiki first: search_wiki, then read_wiki on the pages that matter. Numbers about this client
   (revenue, staff, premiums, limits) come only from get_fields / get_indications / get_application.
2. If the wiki answers the question, answer ONLY from the wiki. Don't add outside knowledge or web results.
   Cite the wiki paths you used, e.g. wiki/industries/621210-dental-offices.md.
3. Only if the wiki doesn't cover it {web_rule}
4. Never answer whether something would be covered or paid, and never compare policy wording: call escalate_to_cpl
   and tell the agent to check with their Cyber Practice Leader.
5. You are read-only. If the agent wants to change a value, tell them to change it in the app so it's logged.
6. Plain language, under 150 words unless the agent asks for more. No headings.
7. End with one line: "Sources:" then the wiki paths and/or URLs you actually used."""

WEB_ON = ("(or the agent explicitly asks about the outside world: news, regulations, other companies), use web_search. "
          "Say plainly that this part comes from the web, not the client's file, and cite each URL.")
WEB_OFF = ("say so plainly: \"The wiki doesn't cover this.\" Web search is turned off for this chat, so don't guess "
           "and don't use general knowledge.")

SEARCH_TOOL = {
    "name": "search_wiki",
    "description": "Keyword search across the client wiki (client pages, carrier replies, call transcripts, industry "
                   "page, research, benchmarks, carrier references). Returns matching pages with the lines that matched.",
    "input_schema": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]},
}

_STOP = set("a an and are as at be but by can did do does for from has have how i in is it its me my of on or our "
            "should so than that the their them then there these they this to was we what when where which who why "
            "will with would you your about any say said says tell told ask asked think".split())


def _wiki_files(slug: str) -> list[Path]:
    roots = [WIKI / "clients", WIKI / "industries", WIKI / "raw" / slug, WIKI / "raw" / "research",
             WIKI / "raw" / "carriers", WIKI / "raw" / "benchmarks", WIKI / "raw" / "intake"]
    files = [WIKI / "index.md"]
    for r in roots:
        if r.exists():
            files += sorted(p for p in r.rglob("*.md") if p.name.startswith(slug) or r.name != "clients")
    return files


def search_wiki(slug: str, query: str, limit: int = 6) -> list[dict]:
    """Deterministic keyword search, no model. Rare words count more than common ones (a word in every page,
    like "owner", barely counts; "backups" counts a lot), and the lines shown are the ones with the rarest words."""
    import math
    words = list(dict.fromkeys(w for w in re.findall(r"[a-z0-9$][a-z0-9.$%-]*", query.lower())
                               if w not in _STOP and len(w) > 1))
    if not words:
        return []
    pages = [(p, p.read_text(errors="ignore")) for p in _wiki_files(slug)]
    stems = {w: w[:-1] if w.endswith("s") and len(w) > 4 else w for w in words}   # "backups" also finds "backup"
    df = {w: sum(1 for _, t in pages if stems[w] in t.lower()) for w in words}
    idf = {w: math.log((len(pages) + 1) / (df[w] + 0.5)) for w in words}
    hits = []
    for p, text in pages:
        low = text.lower()
        found = [w for w in words if stems[w] in low]
        if not found:
            continue
        score = sum(idf[w] ** 2 * (1 + 0.25 * math.log(low.count(stems[w]))) for w in found)

        def line_score(ln):
            l = ln.lower()
            return sum(idf[w] for w in found if stems[w] in l)
        lines = [ln.strip() for ln in text.splitlines()
                 if ln.strip() and not ln.lstrip().startswith(("```", "{", "}", "---")) and line_score(ln) > 0]
        lines.sort(key=line_score, reverse=True)
        hits.append({"path": f"wiki/{p.relative_to(WIKI)}", "score": round(score, 2),
                     "matches": [ln[:240] for ln in lines[:4]]})
    return sorted(hits, key=lambda h: -h["score"])[:limit]


def _wiki_rel(page: str, slug: str) -> str | None:
    aliases = {"client": f"clients/{slug}.md", "industry": "industries/621210-dental-offices.md"}
    page = aliases.get(page, page).removeprefix("wiki/")
    p = (WIKI / page).resolve()
    if not str(p).startswith(str(WIKI.resolve())) or not p.exists():
        return None
    return f"wiki/{p.relative_to(WIKI.resolve())}"


def chat_live(conn, cid: int, slug: str, history: list[dict], allow_web: bool) -> dict:
    readers = _readers(conn, cid, slug)
    tools = [t for t in ASK_TOOLS] + [SEARCH_TOOL] + ([WEB_TOOL] if allow_web else [])
    system = SYSTEM.replace("{web_rule}", WEB_ON if allow_web else WEB_OFF)
    msgs = [{"role": m["role"], "content": m["content"]} for m in history if m.get("content")]
    read, searched, db_used, web_urls, searched_web, escalated = [], [], [], {}, False, False
    text_parts = []
    for _ in range(10):
        resp = llm.client().messages.create(model=ANTHROPIC_MODEL, max_tokens=1500, system=system,
                                            tools=tools, messages=msgs)
        for b in resp.content:
            if b.type == "server_tool_use":
                searched_web = True
            elif b.type == "web_search_tool_result" and isinstance(b.content, list):
                for r in b.content:
                    web_urls.setdefault(r.url, r.title)
            elif b.type == "text" and getattr(b, "citations", None):
                for c in b.citations:
                    if getattr(c, "url", None):
                        web_urls.setdefault(c.url, c.title)
        if resp.stop_reason == "pause_turn":          # long web search: send the turn back unchanged
            msgs.append({"role": "assistant", "content": resp.content})
            continue
        if resp.stop_reason != "tool_use":
            text_parts.append("".join(b.text for b in resp.content if b.type == "text"))
            break
        msgs.append({"role": "assistant", "content": resp.content})
        results = []
        for b in resp.content:
            if b.type != "tool_use":
                continue
            args = b.input or {}
            if b.name == "escalate_to_cpl":
                escalated, out = True, "escalation recorded"
            elif b.name == "search_wiki":
                out = search_wiki(slug, args.get("query", ""))
                searched += [h["path"] for h in out[:3]]
            elif b.name == "read_wiki":
                rel = _wiki_rel(args.get("page", ""), slug)
                out = readers["read_wiki"](args.get("page", "")) if rel else "not found"
                if rel:
                    read.append(rel)
            else:
                out = readers[b.name](**args)
                db_used.append(b.name)
            results.append({"type": "tool_result", "tool_use_id": b.id, "content": json.dumps(out, default=str)[:12000]})
        msgs.append({"role": "user", "content": results})
    else:
        text_parts.append("I couldn't finish that lookup. Try a narrower question.")

    answer = "\n".join(t for t in text_parts if t).strip()
    # Cite pages Claude opened; pages it only saw in search results count only for a wiki-only answer.
    wiki = list(dict.fromkeys(read or ([] if (web_urls or searched_web) else searched)))
    used_wiki, used_web = bool(read or db_used), bool(web_urls) or searched_web
    # The label comes from which tools ran, not from the model's own claim.
    source = ("both" if used_wiki and used_web else "web" if used_web else "wiki" if (used_wiki or searched)
              else "none")
    return {"answer": answer, "source": source, "escalated": escalated, "wiki": wiki,
            "db": list(dict.fromkeys(db_used)), "web": [{"url": u, "title": t} for u, t in web_urls.items()],
            "mode": "live"}


def chat_offline(conn, cid: int, slug: str, question: str) -> dict:
    """No API key: answer from a keyword search of the wiki, quoted, with no web."""
    if COVERAGE_Q.search(question) and not re.search(r"\b(premium|price|cost)\b", question, re.I):
        return {"answer": "That's a coverage question, so it goes to your Cyber Practice Leader, not the wiki or the web.",
                "source": "wiki", "escalated": True, "wiki": [], "db": [], "web": [], "mode": "offline"}
    hits = search_wiki(slug, question, limit=3)
    if not hits:
        return {"answer": "The wiki doesn't cover this. (Web search needs ANTHROPIC_API_KEY.)", "source": "wiki",
                "escalated": False, "wiki": [], "db": [], "web": [], "mode": "offline"}
    body = "\n\n".join(f"{h['path']}\n" + "\n".join(f"  • {m}" for m in h["matches"]) for h in hits)
    return {"answer": "From the wiki (keyword search; set ANTHROPIC_API_KEY for written answers):\n\n" + body,
            "source": "wiki", "escalated": False, "wiki": [h["path"] for h in hits], "db": [], "web": [],
            "mode": "offline"}


def chat(conn, cid: int, slug: str, history: list[dict], allow_web: bool) -> dict:
    question = next((m["content"] for m in reversed(history) if m["role"] == "user"), "")
    if not llm.available():
        return chat_offline(conn, cid, slug, question)
    try:
        return chat_live(conn, cid, slug, history, allow_web)
    except Exception as e:  # e.g. web search not enabled for the org: retry wiki-only and say so
        if allow_web and "web_search" in str(e):
            out = chat_live(conn, cid, slug, history, False)
            out["answer"] += "\n\n(Web search isn't available for this API key, so this answer is wiki-only.)"
            return out
        raise
