---
type: schema
---

# Client Wiki — Schema

This wiki follows the LLM Wiki pattern (raw sources → LLM-maintained pages → schema).
It is the **knowledge layer** for UKON's cyber-in-the-renewal-window workflow.

## The one rule that matters

**The database owns the numbers. The wiki owns the evidence.**

- Postgres is the system of record for every field value, carrier indication, report
  version, and every change a human makes (who, when, old → new, why).
- The wiki holds sources, reasoning, contradictions, and industry knowledge.
- An LLM may write wiki prose. An LLM may never write a premium, limit, deductible, or
  any figure that appears in a client report. Numbers flow DB → report, never LLM → report.

## Layout

```
wiki/
  CLAUDE.md            this file (schema + rules)
  index.md             catalog of every page, one line each
  log.md               append-only: ingest | estimate | review | report | call | ask
  raw/                 immutable sources (never edited after landing)
    <client-slug>/     AMS export, filings, website capture, DNS, call transcripts (call_N), emails (email_N), signals
    benchmarks/        published industry + premium benchmarks, with URLs
    research/          cited recent events per industry (client-research skill)
    intake/            Stage 5 questionnaire question bank + limit walkthrough script
    <client-slug>/indications/  carrier replies as received: PDF letters, emails, underwriter calls
    <client-slug>/quotes/       carrier firm quotes as received (Stage 6)
    carriers/          carrier panel, specimen map, coverage language, application question bank
    _cache/            cached AI output used when no API key is set
  clients/<slug>.md    one page per client (generated from DB + raw, re-rendered on change)
  clients/<slug>-intake.md  the Stage 5 questionnaire answers, answer by answer (generated)
  clients/<slug>-indications.md  requests, every carrier reply as a version, diffs, actions (generated)
  clients/<slug>-bind.md  Stage 6: owner's decisions, firm quote vs indication, conditions, binder, after-bind plan (generated)
  industries/<naics>.md shared industry pages — compound across every client in that industry
```

## Client page conventions

- Frontmatter: `client_id`, `legal_name`, `naics`, `renewal_date`, `last_rendered`.
- Each of the five indication fields gets a section: value, range, confidence, method, sources.
- Every claim cites a raw file as an Obsidian wikilink: `[[raw/sloanslake/website|website]]`.
- The client page is **generated** (`pipeline/wiki_render.py`). Never hand-edit it; it carries a
  warning callout. Change values in the app so the change is logged.
- Contradictions are **flagged, never silently resolved**:
  `> CONFLICT: AMS says 11 employees (2025 WC audit); website team page lists 13 (2026).`
- Estimates always state their method and show a range, never a bare point value.

## Operations

| Op | Trigger | What happens |
|---|---|---|
| ingest | new raw source lands | extract facts → update client page + industry page → log |
| estimate | after ingest | deterministic estimators (pipeline/estimators.py) compute ranges → DB |
| review | human confirms/overrides | DB records actor + reason; client page re-renders |
| report | agent submits | immutable report version snapshot in DB; log entry |
| indication | carrier reply lands (PDF, email, call) | extract → check figures in source → new version + diff → actions; pack refresh |
| call / email | Stage 5 call transcript or client email lands (one of several) | extract answers, merge with earlier sources; hedged answers flagged; exposure + pack refresh |
| quote | carrier firm quote lands (Stage 6) | extract → check figures and dates in source → compare with indication → conditions; bind page refresh |
| research | building/refreshing a pack | cited industry events into `raw/research/`; human-reviewed |
| ask | agent asks a question | answer from DB (numbers) + wiki (why), cited, read-only |
| lint | weekly / pre-renewal | stale facts (>12 mo), unresolved conflicts, missing sources |

## Confidence scale

- **high** — direct record from the agency or an official filing, < 12 months old
- **medium** — two or more independent signals agree within ±20% (`SIGNAL_AGREEMENT_MEDIUM`)
- **low** — single signal, old signal, or signals disagree → goes to human review

## Escalation

Questions that require interpreting policy coverage ("would this claim be paid?") are never
answered from the wiki. Route to the Cyber Practice Leader (CPL).

## Obsidian conventions

- This folder is the vault. Everything in it is `.md` so Obsidian shows and links it.
- Structured sources (AMS export, indications, signals…) keep their data in **one ```json block**.
  The pipeline reads that block (`pipeline/sources.py`); keep it valid JSON if you edit it.
- Links are wikilinks with vault-relative paths: `[[raw/sloanslake/indications/2026-10-27_northwind_indication.pdf]]`.
- Frontmatter `type:` values: `schema`, `index`, `client`, `industry`, `raw-source`, `benchmark`,
  `client-indications`, `carrier-reference`, `extracted-signals`, `cached-ai-output`, `research`, `client-intake`.
