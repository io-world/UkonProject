# Cyber in the Renewal Window — prototype

One real client (Sloan's Lake Dental, legal name Sage Dentistry, PLLC: a three-dentist practice in Denver, CO)
taken from "renewal coming up" through intake calls to a client pack and agent brief. Everything public
about the practice is real and saved in `wiki/raw/sloanslake/` with links (start at `00_overview.md`); the agency's records, the
calls and the carriers are simulated and labeled.

**Core rule: the database owns the numbers, the wiki owns the evidence.** AI extracts, explains
and writes prose; it never writes a premium, limit, or any figure that reaches a client.

Everything runs locally from this folder. No Docker.

## Prerequisites (macOS)

- **uv** (`curl -LsSf https://astral.sh/uv/install.sh | sh`). That's the only install.
- **Node is bundled too:** `uv sync` puts `node`/`npm` into `.venv` (the `nodejs-wheel` package), so you
  run them as `uv run npm …`. No system Node needed.
- **That's it.** Postgres is bundled in the project: `uv sync` installs the server programs into
  `.venv` (the `pgserver` package) and the data lives in `db/pgdata`. Nothing is installed
  system-wide, and deleting the folder removes all of it. (`PG_BIN=/path/to/bin` overrides this
  if you'd rather use another Postgres.)

## Run it

```bash
# 1. Python + bundled Postgres (uv creates .venv from uv.lock)
uv sync

# 2. Database: project-local Postgres on port 5433, data in db/pgdata
scripts/db.sh init            # first time only (later: scripts/db.sh start)
cp .env.example .env          # optional: add ANTHROPIC_API_KEY to run the AI steps live
uv run python -m pipeline.run_all

# Carrier replies: ingest a saved file (no screen for this; the client pack uses the result)
# uv run python -m pipeline.indications wiki/raw/sloanslake/indications/2026-11-06_northwind_indication_revised.pdf

# 3. Terminal 1 — backend (API on :8000)
uv run uvicorn api.main:app --port 8000 --reload

# 4. Terminal 2 — frontend (hot reload on :5173, calls the API on :8000)
cd web
uv run npm install            # first time only
uv run npm run dev            # open http://localhost:5173
```

**The HTML client pack** is written to `reports/sloanslake/current.html`: open it in any browser.
Each submitted version is saved alongside it as `v<N>.html` and never changes.

Edit `web/src` and the browser updates live. `uv run npm run build` refreshes `web/dist`, which the
API also serves at http://localhost:8000 (handy for a one-terminal demo).

After pulling an update, if the app says the database is from an older version, run
`uv run python -m pipeline.run_all` and refresh.

Stop the database with `scripts/db.sh stop`. Reset all demo data any time with
`uv run python -m pipeline.run_all`.

Without an API key everything still runs: the report narrative and call extraction use cached AI
outputs (in `wiki/raw/_cache/`, checked by the same guards) and "Ask" uses offline rules.

## Open the wiki in Obsidian

Obsidian → **Open folder as vault** → choose `UkonProject/wiki`. Start at `index`. Citations on
the client page are clickable, and graph view shows client ↔ industry ↔ sources. The client page
is regenerated from the database; annotate the industry page or raw sources instead.

## Demo script (≈8 minutes of the 30)

The flow: **enrich → carrier indications → intake (human in the loop, can be partial) → client pack → agent brief.**

1. **Get indications (the five fields).** Five real registry/NPI candidates. "Sloans Lake Dental PLLC" matches the trade name and
   address exactly but is delinquent since 2022; the one in good standing is Sage Dentistry, PLLC. Confirm it.
   Open "method & sources" on revenue: nothing public, nothing at the agency; two benchmark methods
   disagree by ~$1.1M, so it's low confidence and flagged. Same for headcount. **Edit** any field: pick where
   the value came from (conversation, clipboard, API, typed) and a reference; the card shows it from then on.
   Carrier indications are loaded in the background (fictional carriers) so the client pack has prices.
2. **Intake → Live call.** The screen the agent runs the call from: numbered questions, tap answers,
   "Client unsure," coverage questions logged for a CPL, and the limit walkthrough. Tap Q2 as
   "50–75%" (the recording says "Over 75%"). Call 1 (sample) is already ingested.
   **Intake → After the call:** recording vs taps per question, quotes, flags. Re-ingest call 1 →
   Q2 becomes a CONFLICT. Revenue stays open (the owner deferred to the accountant): type the confirmed
   figure → the report updates (logged).
3. **Client pack.** Built anyway from what's known. Click "Open HTML report ↗", or open
   `reports/sloanslake/current.html`. See "What you've told us so far" and "Practices like yours,
   in the news" (real, cited events, including a Longmont CO breach). Exposure 63, Moderate; the
   no-DMARC finding is the practice's real public DNS.
4. **The follow-up call.** Record a short call in Wispr Flow and run the `call-ingest` skill, or click
   **Ingest** next to `call_2_followup.md` under Intake → After the call.
   MFA and IT software close; backups stay open. Exposure drops to 45, Moderate; the HTML file updates.
5. **Adjust & lock.** Drag revenue to ~$2.8M → "indication needs refresh"; premiums don't move.
   Reset. Submit & lock → `reports/sloanslake/v1.html` appears. Send. Client view shows only that version.
6. **Agent brief.** Pitch, CPL-approved objections, news talking points, specimen map.
7. **Audit trail + Ask.** "Who changed what?" and "Would a ransomware payment be covered?" (escalates).

## Docs

| | |
|---|---|
| `docs/00-brief.md` | UKON's assignment |
| `docs/interview-notes.md` | **Start here for the interview:** what was built, use cases, conversation flows, workflows, demo talk track, Q&A prep |
| `docs/decisions.md` | Every design decision and why |
| `docs/workflow.md` | Renewal → bound: AI vs human vs failure modes per step (+ diagram) |
| `docs/proposal-pack.md` | The client deliverable |
| `docs/mvp-scope.md` | Critique, what's built, later, skipped |
| `docs/assumptions-risks-questions.md` | Write-up raw material |
| `docs/architecture.md` | Components, thresholds, tools used |
| `docs/deliverables.md` | Status of each deliverable + presentation outline |
| `docs/client-intake.md` | Intake questions + the limit walkthrough script (prose) |
| `docs/chat-log.md` | How the project was designed and built, exchange by exchange |

## What's fictional

The client, agency, carriers, indications, specimen sections and call transcripts are invented.
The news items in `wiki/raw/research/` are real, cited events. Premium
levels, dental revenue benchmarks and claim costs are real published figures, with sources in
`wiki/raw/benchmarks/`.
