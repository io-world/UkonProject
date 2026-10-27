# Cyber in the Renewal Window — prototype

One real client (Sloan's Lake Dental, legal name Sage Dentistry, PLLC: a three-dentist practice in Denver, CO)
taken through six stages, from "renewal coming up" to a bound policy (simulated) and a plan for the year after. Everything public
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
# optional: create .env (git-ignored) with ANTHROPIC_API_KEY=... to run the AI steps live
uv run python -m pipeline.run_all

# Carrier replies: Stage 2 → Carrier inbox → "Read it in", or ingest a saved file from the command line
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

Six stages: UKON's four, with its Stage 1 split into **confirm data** and **get indications** (decision #55) and its
Stage 4 split into **questionnaire** and **decision, bind, report** (decisions #59–60).
**1 Confirm data → 2 Get indications → 3 Proposal pack → 4 Equip the agent → 5 Questionnaire → 6 Decision, bind, report.**
The app's tabs are the stages; each shows a status derived from the data (done, to do, in progress).

1. **Stage 1 · Confirm data.** Five real registry/NPI candidates. "Sloans Lake Dental PLLC" matches the trade name and
   address exactly but is delinquent since 2022; the one in good standing is Sage Dentistry, PLLC. Confirm it.
   Open "method & sources" on revenue: nothing public, nothing at the agency; two benchmark methods
   disagree by ~$1.1M, so it's low confidence and flagged. Approve or **Edit** it (pick where the value came
   from: conversation, clipboard, API, typed). Only the five fields live here.
2. **Stage 2 · Get indications.** What goes to carriers, with its review state; pick carriers and **Re-request**
   (gated: try it before Stage 1 is reviewed and it refuses). The demo seed's first requests went out before review,
   and the screen says so. In the **carrier inbox**, click **Read it in** on Northwind's revised letter: both
   premiums rise 10% and a new EDR condition appears, checked against the client's answers, as follow-ups.
   Open Cobalt's reply history: $5,290 was written "5.29k", so it waits for a person: **Matches the source**.
3. **Stage 3 · Proposal pack.** Click "Open HTML report ↗", or open `reports/sloanslake/current.html`. See "What
   you've told us so far" and "Practices like yours, in the news" (real, cited events, including a Longmont CO
   breach). Drag revenue to ~$2.8M → "indication needs refresh"; premiums don't move. Reset. Submit & lock →
   `reports/sloanslake/v1.html` appears. **Undo submit** (with a reason): v1 stays on record as withdrawn and
   editing continues in v2; the **Locked versions** dropdown shows every submitted version read-only.
   Submit again, then Send: the client view shows only that version, and a sent version can't be undone.
4. **Stage 4 · Equip the agent.** **Ask the wiki**: "What did the owner say about backups and MFA?" comes back
   *From the wiki* with the pages it used; "Any recent ransomware news for dental practices?" (with web on) is labelled
   *From the web* with links; "Would a breach at Peak Tech be covered?" escalates to the CPL. Then the pitch,
   objections (+/−), news talking points and specimen map. Without an API key the chat falls back to a keyword search.
5. **Stage 5 · Questionnaire.** Seeded with call 1, call 2 and an email from the office manager (all simulated, in the
   wiki), so 3 of 25 questions are open. Filter **Not answered**; sections fold. Answers already on record show with the
   line they came from; **Correct** opens the inputs. On **Live call**, tap Q2 as "50–75%" (the recording says "Over 75%");
   **After the call**, re-ingest call 1 → Q2 becomes a CONFLICT. The email's "I think the limit is $50,000" (a breach
   endorsement on their business owner's policy) is flagged: the "already covered" belief, in the client's words.
   **Application:** confirm the answers (the client signs a complete application).
6. **Stage 6 · Decision, bind, report.** Record **the owner's choice** (Northwind, $1M / $10K) or "not now" with a reason.
   **Take in** Northwind's firm quote: every figure checked against the PDF; $2,980 → $3,410 (+14%) with the carrier's
   reason quoted (revenue $2.52M, no phishing training, backups untested). **Owner accepts**, mark the two before-binding
   conditions met with evidence, **Bind coverage** (simulated policy number). **Report:** client summary, deal record
   (milestones, who did what, sources, outcome), and **After bind: 30-60-90 + the year** to renewal.
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

The agency, carriers, indications, firm quote, binder, specimen sections, call transcripts and the office manager's email are
invented and labelled; everything about the practice itself is public and real.
The news items in `wiki/raw/research/` are real, cited events. Premium
levels, dental revenue benchmarks and claim costs are real published figures, with sources in
`wiki/raw/benchmarks/`.
