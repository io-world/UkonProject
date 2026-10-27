---
name: client-ask
description: Answer an agent's question about a renewal client from the database (numbers) and the client wiki (reasons), read-only and cited. Use when someone asks about a client's revenue, staff, exposure, carrier options, call answers, or who changed what.
---

# Ask about this client (any stage)

Read-only. You explain; you don't change anything.

## Where answers come from

| Need | Source |
|---|---|
| Any number (revenue, staff, premium, limit, score) | Database: `GET /api/clients/<slug>` (fields) and `GET /api/clients/<slug>/report?mode=agent` (indications, options) |
| Why a number is what it is | `wiki/clients/<slug>.md` (method, sources, conflicts) and the raw files it cites |
| Who changed what | `GET /api/clients/<slug>/audit` |
| What the client said on intake calls | `GET /api/clients/<slug>/application` (answers, quotes, which call) and `/intake/calls` |
| The client pack itself | `reports/<slug>/current.html` (draft) or `v<N>.html` (submitted) |
| Industry news / examples | `wiki/raw/research/<naics>_*.md` (cited) |
| Industry context, approved objection answers | `wiki/industries/<naics>-*.md` |

If the API isn't running, query Postgres directly (`scripts/db.sh psql`, port 5433) (schema `ukon`, tables `fields`, `indications`,
`application_answers`, view `audit_trail`), read-only.

## Rules

1. Every number must come from a tool result. Quote it exactly as stored.
2. Give the reason from the wiki, in one or two sentences, with the source file.
3. If asked whether something is *covered* or would be *paid*, or to compare policy wording:
   don't answer. Say it needs the Cyber Practice Leader and name what they should check.
4. If the agent wants to change a value, tell them to use the slider in the report, so the change
   is logged with their name and reason. Do not call write endpoints.
5. End with `Sources:` listing `db:<field>`, `db:indications`, or wiki paths used.
6. Under 120 words unless asked for more.

The same rules run inside the app's "Ask about this client" panel (`api/ask.py`).
