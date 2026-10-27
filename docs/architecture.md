# Architecture

```
            ┌──────────── wiki/ (Obsidian vault) ────────────┐
            │ raw/ sources (immutable)  industries/  clients/ │
            └──────┬───────────────────────────────▲─────────┘
       read sources│                                │re-render on every change
                   ▼                                │
  ┌─────────── pipeline/ (Python, uv) ───────────────┴──┐
  │ entity_resolution → estimators (no LLM) → indications│
  │ narrative (LLM, no digits) · intake ingest · HTML out │
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
| `db/schema.sql` | `fields` (value, AI value, range, confidence, method, sources), `field_changes` (append-only audit), `indication_requests` (basis as sent), `indication_sources` (each carrier reply), `indication_versions` (append-only, values locked by trigger), `indication_actions`, `indications` (read-only view: latest written, checked version), `report_versions` (immutable once submitted), `application_answers`, `ask_log`, `audit_trail` view. |
| `pipeline/sources.py` | Reads/writes the JSON block inside a wiki Markdown source. |
| `pipeline/entity_resolution.py` | Weighted match on name 25%, state 20%, address 30%, domain 25%. |
| `pipeline/estimators.py` | Employees, revenue waterfall, exposure score, revenue drift. No LLM. |
| `pipeline/narrative.py` | LLM prose with placeholders; rejects any digit; cached fallback. |
| `pipeline/report.py` | Snapshot builder; working → submitted → sent → superseded. |
| `pipeline/intake.py` | Intake rules with no database: question bank, extraction prompt, hedge check, recording-vs-live-tap reconciliation, intake wiki page. |
| `pipeline/intake_ingest.py` | One call → intake + application answers; merges across calls; conflicts with live taps; CPL questions; exposure; pack + wiki refresh. |
| `pipeline/indication_extract.py` | Carrier reply → text (pypdf / file) → LLM extraction (cached fallback) → deterministic check that every figure appears in the source. |
| `pipeline/indications.py` | Requests out; replies in; versions + diffs; rule-based actions; condition status from the intake; generated `wiki/clients/<slug>-indications.md`. |
| `pipeline/html_report.py` | Snapshot → standalone HTML file in `reports/<slug>/`. |
| `pipeline/config.py` | Every review threshold in one place; loads `.env`. |
| `api/main.py`, `api/ask.py` | REST for the app; Ask uses read-only tools (live with an API key, rule-based offline). |
| `web/` | Workbench tabs: Enrich · Indications · Intake (Live call · After the call · Application) · Client pack · Agent brief · Audit, plus Ask drawer. |
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
- **Wispr Flow:** call capture for the Stage 4 Q&A, pulled into the wiki by a Claude skill.
