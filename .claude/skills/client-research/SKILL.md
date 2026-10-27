---
name: client-research
description: Research recent real-world cyber events for a client's industry (breaches, ransomware, vendor incidents, regulation) and save them as cited items for the client pack and agent brief. Use when building or refreshing a client pack, or when the user asks for industry examples, news, or use cases for a client.
---

# Client research (web → wiki → client pack)

The client pack shows "Practices like yours, in the news"; the agent brief shows talking points.
Both read `wiki/raw/research/<naics>_<topic>.md`. This skill keeps that page current.

## Steps

1. Read the client page (`wiki/clients/<slug>.md`) and the industry page for context: industry,
   size, what the client uses (remote access, online payments, vendors).
2. Search the web for **real, recent** events for that industry. Prefer the last 12–18 months.
   Cover several kinds: ransomware at similar-sized businesses, breach roundups, vendor or
   clearinghouse incidents, business email compromise, and regulation (proposed or final rules).
   Read the actual article before using it.
3. Update the ```json block in `wiki/raw/research/<naics>_<topic>.md` (create it from the dental one
   if missing). Each item:
   - `id`, `category` (ransomware | breach | vendor | bec | regulation), `headline` (plain, short)
   - `summary`: 2–3 plain sentences; figures only as the source states them
   - `for_this_client`: one sentence linking it to this client's situation; **no new numbers**
   - `source`, `url`, `date` (publication date)
   - `use_in`: `["client_pack","agent_brief"]` for the 3–4 strongest; `["agent_brief"]` for the rest
4. Drop items you can't source, items older than about 3 years unless they're a landmark
   (e.g. the first ransomware settlement), and anything speculative.
5. Append `## [YYYY-MM-DD] research | <naics> — <n> items` to `wiki/log.md`.
6. Refresh the pack: `uv run python -m pipeline.refresh_pack <slug>` (rewrites `reports/<slug>/current.html`).
7. Report back: the items added or removed, with links, and note that a person should skim them
   before the pack goes to a client.

## Never

- Invent an incident, a figure, or a date. No URL, no item.
- Name or shame a real business in a way the source doesn't support.
- Put research figures into the AI narrative; they live only in the cited items.
