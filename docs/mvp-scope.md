# MVP scope and the critique behind it

## Critical review of the design (Oct 25)

Randy asked for a critical read of the workflow as designed. The core instincts held up: locked
carrier numbers, human review at the right points, versioning with an audit trail, and a wiki
that compounds across renewals are exactly the "judgment on where AI helps" UKON is grading.
The problems were scope and who does the work:

1. **It's a platform, not an MVP.** Wiki + Postgres + versioning + sliders + Ask skill + practice
   mode + call capture is a year of roadmap. The brief asks what to build first and *deliberately
   skip*; "everything" reads as weak prioritization. → Needs a hard cut (below).
2. **Count the agent's touchpoints.** The goal is "as little extra work for the agent as possible,"
   but the agent reviews entities, adjusts sliders, approves the report, reads a brief, runs a
   call, and confirms answers. → **Review by exception** (high-confidence fields pass), and
   **move review work to UKON** (CPLs/ops do entity resolution and estimate review). That's also
   the business story: UKON's team absorbs the work.
3. **It's designed one client at a time; the goal is many.** → The agent's home screen should be a
   **renewal queue**: everyone renewing in 90 days, ranked, with stage and blockers.
4. **Frame it around agent economics.** Agents skip cyber because premium (and commission) is small
   relative to effort. → North-star metric: **agent minutes per bound policy.**
5. **Stage 5 (questionnaire, UKON's Stage 4): offer the call or a link.** The call is right for relationship clients; a phone-
   friendly link keeps low-touch clients from eating agent time.
6. **Be ready for "why a wiki *and* a database?"** → The DB holds facts and versions; the wiki holds
   evidence and industry knowledge that compounds across clients and years.

## Randy's call

**One client, built deep, end to end**: wiki, Postgres, skills, Wispr Flow, simple React front
end. Add a "how this scales" slide showing the renewal queue so the panel sees it was designed
for many clients even though the prototype runs one.

**What to build first in production (Randy, Oct 27):** (1) process-mine the real workflow (mining tool + an AI
layer turning emails, carrier documents and call notes into source-linked events; tag why each manual step is
manual: relationship, judgment, missing data, habit); (2) model how the two or three main carriers work; (3) automate
the paperwork and augment the relationships, ranked by deals lost × cost to fix, measured against the same event log.

## Built

Six stages: UKON's four, with its Stage 1 split in two (decision #55) and its Stage 4 split in two (decisions #59–60).

- Stage 1 · Confirm data: ingest → entity resolution (human-confirmed) → the five fields with ranges,
  confidence, method, sources; review by exception
- Stage 2 · Get indications: send to chosen carriers (gated on Stage 1) → replies from any channel
  checked against the source and versioned → rule-based follow-ups (three fictional carriers,
  benchmark-calibrated; values locked)
- Stage 3 · Proposal pack: digital report, agent/client modes, sliders, drift banner, versions, audit
  trail; standalone HTML files in `reports/`; cited industry research from the web
- Stage 4 · Equip the agent: brief (pitch, CPL objection library, escalations, specimen map,
  application preview) + "Ask about this client" (app panel + Claude Code skill)
- Stage 5 · Questionnaire: calls and emails → answers merged across sources, with quotes, hedge flags and
  agent confirmation; filter (all / not answered / answered) and collapsible sections; answers on record shown
  with their source until the agent corrects them; application filled from them
- Stage 6 · Decision, bind, report: owner's choice or "not now" + reason; firm quote checked against the PDF and
  compared with the indication; final yes/no; before-binding conditions met with evidence; bind (simulated);
  client summary, deal record, after-bind 30-60-90 and touchpoints to renewal

## Later (designed, not built)

- Renewal queue across a whole book; prioritization
- Existing-cyber check (BOP endorsements) and appetite/class-code filter before submission
- Real carrier integrations (API/portal)
- Client self-serve question link (alternative to the call)
- Debrief ingestion; CPL review of new objections
- Practice mode: AI role-plays this skeptical owner so the agent can rehearse
- Golden dataset (15–20 businesses with known values) for field-level accuracy
- Live DNS lookups; licensed firmographic data instead of scraping

## Deliberately skipped (mocked)

- Binding, payment, e-signature integration
- Multi-agency tenancy and permissions (noted: an agent must only ever see their agency's clients)
- Authentication
