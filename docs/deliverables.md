# Deliverables tracker

| Deliverable (from the brief) | Status | Where |
|---|---|---|
| Interview plan | Draft: `web/public/interview/1-interview-plan.html` · source | `interview-notes.md` §16 (seed questions also in `assumptions-risks-questions.md`) |
| One-page workflow map | Draft | `workflow.md` (Mermaid diagram renders in Obsidian/GitHub) |
| Proposal pack outline/mockup | Done: real HTML file | `proposal-pack.md` + `reports/sloanslake/current.html` |
| Prototype | Built; needs a run-through on Randy's Mac and a real Wispr Flow mock call | this repo · `README.md` |
| Write-up (1–2 pages) | Draft written (review in Randy's voice) | `web/public/interview/5-write-up.html` |

**HTML versions of all five:** http://localhost:5173/interview (files in `web/public/interview/`) (self-contained pages; screenshots embedded).

## Presentation (30 minutes to execs + engineers)

Full talk track, demo steps and Q&A prep: `interview-notes.md` §14–15.

Suggested flow, ~10–12 slides:

1. The problem in one line: the renewal window is missed because "no cyber → protected" is too much manual work
2. Users: agent (time, commission economics) and owner (not technical, needs price first)
3. Interview plan: who and what we'd ask before building
4. Workflow map: six stages (UKON's four, Stages 1 and 4 each split), AI vs human per step
5. Where AI helps / where it doesn't (DB owns numbers, wiki owns evidence)
6. Live demo (~8 min; script in `README.md`)
7. How this scales: the renewal queue
8. What I'd build first / deliberately skip
9. Metrics: agent minutes per bound policy + funnel
10. Risks and how they're caught
11. Open questions
12. How I used AI to build this (Claude for research, design critique, and code; Wispr Flow for call capture)

## Before the demo

- [ ] Reload the demo data (`uv run python -m pipeline.run_all`) and click through the six stage tabs + audit (Stage 6: choose, take in the firm quote, accept, mark conditions, bind, open the three reports)
- [ ] Record a short mock Stage 5 questionnaire call in Wispr Flow, then run the `call-ingest` skill against it
- [ ] Run `client-research` once more close to the presentation so the news items are current
- [ ] Optional: set `ANTHROPIC_API_KEY` so narrative, extraction and Ask run live
- [ ] Verify whether Wispr Flow captures phone calls
