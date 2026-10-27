---
name: call-ingest
description: Ingest an intake call for a renewal client from Wispr Flow into the wiki and merge it into the intake (checked against the agent's live taps; hedges and conflicts flagged). Use after any agent-client intake call, or when the user says ingest the call, process the Wispr recording, or update the intake.
---

# Call ingest (intake, human in the loop)

The agent runs the call from the app's **Intake → Live call** screen, tapping answers as the client
talks; Wispr Flow records it. This skill brings the recording in. Intake can take several calls;
each is merged into what's known, and the client pack is rebuilt even if items are still open.

## Steps

1. **Find the call in Wispr Flow.** Use the Wispr Flow tools: `search_meetings` with the client or
   contact name (e.g. "Sloan's Lake", "Sage Dentistry", "Pollack"), then `get_meeting` for the transcript and
   Flow Summary. If several match, list them with date and title and ask which one. Show times in
   the user's local time zone.
2. **Check consent.** The transcript must open with a recording disclosure and the client's
   agreement. If it doesn't, stop and tell the user; in some states it can't be used without it.
3. **Save the raw source.** Number the call after the existing ones in `wiki/raw/<slug>/`
   (`call_1_intake.md`, `call_2_followup.md`, …): write `call_<n>_<short-label>.md` with frontmatter
   `type: raw-source`, `immutable: true`, `source: wispr-flow`, then date and participants, then the
   transcript. Use `[mm:ss] **Speaker:**` lines when Wispr gives times; if it doesn't, keep its
   speaker lines as they are (answers will have no timestamp). Keep mis-transcriptions as-is.
   Raw files are never edited after this.
4. **Ingest.** Either click **Ingest** next to the file in **Intake → After the call**, or run
   `uv run python -m pipeline.intake_ingest wiki/raw/<slug>/call_<n>_<label>.md`.
   Needs `ANTHROPIC_API_KEY` for a new call (cached extractions exist only for the samples).
   What it does: extracts intake + application answers with quotes; hedged answers → follow-up;
   answers that disagree with the agent's live taps → CONFLICT; coverage questions → CPL list;
   merges with earlier calls (never overwriting a newer call or an agent-confirmed answer);
   recalculates exposure; rewrites `reports/<slug>/current.html`, `wiki/clients/<slug>.md` and
   `wiki/clients/<slug>-intake.md`.
5. **Add the call to `wiki/index.md`** under the client's raw sources.
6. **Report back** in a short list: what the call answered, what's flagged (exact quote), any
   conflicts with live taps, coverage questions for a CPL, what's still open, the new exposure score.

## Never

- Confirm an answer. The agent confirms in the app; the client e-signs the application.
- Upgrade a hedged or partial answer to "yes", or answer a coverage question.
- Hold up the client pack because intake is incomplete.
