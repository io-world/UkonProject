# Architecture

```
            ┌──────────── wiki/ (Obsidian vault) ────────────┐
            │ raw/ sources (immutable)  industries/  clients/ │
            └──────┬───────────────────────────────▲─────────┘
       read sources│                                │re-render on every change
                   ▼                                │
  ┌─────────── pipeline/ (Python, uv) ───────────────┴──┐
  │ stages · entity_resolution → estimators (no LLM)     │
  │ indications · narrative (no digits) · calls · HTML   │
  └───────────────┬──────────────────────────────────────┘
                  │ writes numbers, versions, answers
                  ▼
        Postgres (db/pgdata, port 5433) ◄──── api/ (FastAPI) ◄──── web/ (React + Vite)
                  ▲                              │
                  └──── "Ask" (read-only tools) ─┘     .claude/skills/ for Claude Code
```

## The rule

**The database owns the numbers; the wiki owns the evidence.** The LLM extracts signals from
sources, writes prose, and explains. Deterministic code computes estimates. Carriers supply
prices. A person confirms anything that matters. No code path lets a model write a figure that
reaches a client.

## Components

| Path | Role |
|---|---|
| `wiki/` | LLM-wiki knowledge layer. Raw sources as Markdown (JSON in a code block where structured); generated client page; shared industry page; `log.md`; schema in `wiki/CLAUDE.md`. |
| `db/schema.sql` | `fields` (value, AI value, range, confidence, method, sources), `field_changes` (append-only audit), `indication_requests` (basis as sent), `indication_sources` (each carrier reply), `indication_versions` (append-only, values locked by trigger), `indication_actions` (follow-ups), `indications` (read-only view: latest written, checked version), `report_versions` (immutable once submitted), `intake_calls` / `intake_answers` / `intake_escalations` (Stage 5 calls and emails), `application_answers`, `client_decisions` (owner's choice and final yes/no, append-only, with a reason on any no), `firm_quotes` (values locked by trigger), `bind_conditions` (met with evidence), `binders`, `ask_log`, `audit_trail` view. |
| `pipeline/stages.py` | The six stages (UKON's four, Stages 1 and 4 each split) and each stage's status, derived from the data. |
| `pipeline/sources.py` | Reads/writes the JSON block inside a wiki Markdown source. |
| `pipeline/entity_resolution.py` | Weighted match on name 25%, state 20%, address 30%, domain 25%. |
| `pipeline/estimators.py` | Employees, revenue waterfall, exposure score, revenue drift. No LLM. |
| `pipeline/narrative.py` | LLM prose with placeholders; rejects any digit; cached fallback. |
| `pipeline/stage3_proposal.py`, `pipeline/report.py` | Stage 3: draft v1; snapshot builder; working → submitted → sent → superseded. |
| `pipeline/intake.py` | Stage 5 questionnaire rules with no database: question bank, extraction prompt, hedge check, recording-vs-live-tap reconciliation, intake wiki page. |
| `pipeline/intake_ingest.py` | One call or email (`call_N.md`, `email_N.md`) → intake + application answers; merges across sources; conflicts with live taps; CPL questions; exposure; pack + wiki refresh. |
| `pipeline/indication_extract.py` | Carrier reply → text (pypdf / file) → LLM extraction (cached fallback) → deterministic check that every figure appears in the source. |
| `pipeline/indications.py` | Stage 2: requests out (gated on Stage 1, chosen carriers); replies in; versions + diffs; rule-based follow-ups; review of a flagged figure; condition status from the call answers; generated `wiki/clients/<slug>-indications.md`. |
| `pipeline/bind.py` | Stage 6: owner's choice (or not now + reason); firm quote in (extraction + figure/date check, compared with the written indication; conditions by what they require); final yes/no; conditions met with evidence; bind (simulated binder); client summary, deal record and after-bind plan (30-60-90 + touchpoints to renewal, by rules); generated `wiki/clients/<slug>-bind.md`. |
| `pipeline/html_report.py` | Snapshot → standalone HTML file in `reports/<slug>/`. |
| `pipeline/config.py` | Every review threshold in one place; loads `.env`. |
| `api/main.py`, `api/ask.py` | REST for the app (no route writes a carrier figure); Ask uses read-only tools (live with an API key, rule-based offline). |
| `api/chat.py` | Stage 4 "Ask the wiki" chat: searches and reads the wiki first, Anthropic web search only as a fallback; the wiki / web / both / unverified label is set from the tools that ran. Offline: keyword search over the wiki. `/api/wiki` serves a cited page read-only. |
| `web/` | Workbench, one tab per stage with a derived status: 1 Confirm data · 2 Get indications · 3 Proposal pack · 4 Equip the agent · 5 Questionnaire (Live call · After the call · Application; filter + collapsible sections) · 6 Decision, bind, report · Audit, plus Ask drawer. |
| `.claude/skills/` | `client-ingest`, `indication-ingest` (carrier replies), `call-ingest` (Wispr Flow intake), `client-research` (web), `client-ask`. |
| `reports/` | Generated HTML client packs: `current.html` + `v<N>.html` per submitted version. |

## Thresholds (pipeline/config.py)

| Setting | Value | Effect |
|---|---|---|
| `SIGNAL_AGREEMENT_MEDIUM` | ±20% | Signals agreeing within this → medium confidence; beyond → low → review |
| `SIGNAL_MAX_AGE_MONTHS` | 24 | Older signals shown but not used (PPP 2020) |
| `REVENUE_DRIFT_TOLERANCE` | ±15% | Beyond this, the report says "indication needs refresh" |
| `DENTAL_REVENUE_PER_EMPLOYEE` | $152,600 | Census SAS 2022 revenue ÷ BLS 2022 employment |
| `DENTAL_BILLINGS_PER_DENTIST` | $965,660 | ADA HPI 2025 |

## Tools used and why (for the brief's "tell us what you used")

- **Claude** (in Claude Code): research on benchmarks, design critique, and writing the code.
- **Postgres:** system of record with an audit trail that engineers trust; bundled in the project via the `pgserver` package (no Docker, no system install), data in `db/pgdata`.
- **Obsidian + LLM-wiki pattern:** knowledge that compounds across renewals and is readable by people.
- **FastAPI + React (Vite):** fastest path to a clickable, honest prototype.
- **uv:** reproducible Python environment from one lockfile.
- **Wispr Flow:** call capture for Stage 5 questionnaire calls and underwriter calls (Stage 2), pulled into the wiki by Claude skills.
