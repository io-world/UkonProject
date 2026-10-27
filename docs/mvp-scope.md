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
5. **Stage 4: offer the call or a link.** The call is right for relationship clients; a phone-
   friendly link keeps low-touch clients from eating agent time.
6. **Be ready for "why a wiki *and* a database?"** → The DB holds facts and versions; the wiki holds
   evidence and industry knowledge that compounds across clients and years.

## Randy's call

**One client, built deep, end to end**: wiki, Postgres, skills, Wispr Flow, simple React front
end. Add a "how this scales" slide showing the renewal queue so the panel sees it was designed
for many clients even though the prototype runs one.

## Built

- Stage 1: ingest → entity resolution (human-confirmed) → five fields + exposure with ranges,
  confidence, method, sources; review by exception
- Carrier indications (three fictional carriers, benchmark-calibrated), locked
- Stage 2: digital report, agent/client modes, sliders, drift banner, versions, audit trail
- Stage 3: agent brief (pitch, CPL objection library, escalations, specimen map, application
  preview) + "Ask about this client" (app panel + Claude Code skill)
- Intake (before the pack): one or more call transcripts → answers merged across calls, with
  quotes, hedge flags and agent confirmation; proceeds incomplete; Wispr Flow skill
- Industry research from the web (cited) feeding the pack and the brief
- Standalone HTML report files in `reports/`

## Later (designed, not built)

- Renewal queue across a whole book; prioritization
- Existing-cyber check (BOP endorsements) and appetite/class-code filter before submission
- Real carrier integrations (API/portal), indication refresh
- Client self-serve question link (alternative to the call)
- Debrief ingestion; CPL review of new objections
- Practice mode: AI role-plays this skeptical owner so the agent can rehearse
- Golden dataset (15–20 businesses with known values) for field-level accuracy
- Live DNS lookups; licensed firmographic data instead of scraping

## Deliberately skipped (mocked)

- Binding, payment, e-signature integration
- Multi-agency tenancy and permissions (noted: an agent must only ever see their agency's clients)
- Authentication
