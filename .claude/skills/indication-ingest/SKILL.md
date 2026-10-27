---
name: indication-ingest
description: Ingest a carrier's reply to a cyber indication request (PDF letter, email, or an underwriter call captured with Wispr Flow) for a renewal client, version it against earlier replies, and report what changed and what the agent must do. Use when a carrier indication arrives, or the user says ingest the indication, the carrier replied, or process the underwriter call.
---

# Indication ingest (Stage 1, inbound)

Carriers answer indication requests however they like. Each reply becomes an immutable raw source,
then a new version per carrier + option. Nothing is overwritten.

## Steps

1. **Save the reply as received** in `wiki/raw/<slug>/indications/`, named `<YYYY-MM-DD>_<carrier>_<kind>.<ext>`:
   - PDF letter: copy the file as is.
   - Email: `.md` with frontmatter `type: raw-source`, `immutable: true`, `channel: email`, `carrier:`,
     `received:`, then the headers (From, To, Date, Subject) and the body, unedited.
   - Underwriter call: find it in Wispr Flow (`search_meetings` by carrier or underwriter name, then
     `get_meeting`); check the recording disclosure is at the start; save as `.md` with `channel: call`,
     `source: wispr-flow`, transcript as `[mm:ss] **Speaker:**` lines. Keep mis-transcriptions.
   In the app the agent can skip this step: **Get indications → Add a carrier reply** takes a pasted
   Wispr Flow transcript (*From a conversation*), a pasted email or letter (*Paste from clipboard*), or a
   carrier's JSON (*Import from API*), saves it to the wiki with how it came in and who entered it, and ingests it.
2. **Ingest:** click **Ingest** under *Received → Files saved to the wiki* in the Get indications tab, or run
   `uv run python -m pipeline.indications wiki/raw/<slug>/indications/<file>`.
   A new reply needs `ANTHROPIC_API_KEY` (cached extractions exist only for the samples).
3. **Add it to `wiki/index.md`** under the client's carrier replies.
4. **Report back** briefly: per option, the figure and its state (offered / to confirm / declined / verbal
   only); what changed vs the previous version; the actions created; any figure that failed the source check.

## Never

- Type, correct or "fix" a carrier figure. If extraction is wrong, the agent rejects the version and the
  carrier resends. Confirming a flagged figure is the agent's click, with a note.
- Treat a verbal number as an offer, or show it to a client.
- Interpret coverage. Questions about what a condition or sublimit means go to the CPL.
