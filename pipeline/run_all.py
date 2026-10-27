"""Reset the database and seed the demo client (Sloan's Lake Dental, config.CLIENT_SLUG) through the five stages.

UKON's brief has four stages; this prototype splits its Stage 1 in two:
  1. Confirm data   the five fields from the agency file + public records       (stage1_enrich)
  2. Indications    requests to the carrier panel, replies in, versioned        (indications)
  3. Proposal pack  report v1: plain-language why / options / cost               (stage3_proposal)
  4. Agent kit      pitch, objections, specimens: read from the pack, no seed step
  5. Apply & bind   presentation call 1 (Wispr Flow transcript), partial        (intake_ingest)

The seed takes two honest shortcuts, both labelled in the app: requests go out before the Stage 1 review
(so the live demo can still confirm the entity), and call 1 is ingested before the pack is drafted (so the pack
shows what the owner has said so far). Later calls and carrier replies are ingested from the app or the command line:
    uv run python -m pipeline.intake_ingest wiki/raw/sloanslake/call_2_followup.md
    uv run python -m pipeline.indications wiki/raw/sloanslake/indications/2026-11-06_northwind_indication_revised.pdf"""
import psycopg

from . import indications, intake_ingest, stage1_enrich, stage3_proposal
from .config import CLIENT_SLUG, DATABASE_URL, ROOT


def reset_schema():
    with psycopg.connect(DATABASE_URL) as conn:
        conn.execute((ROOT / "db" / "schema.sql").read_text())
    print("schema reset")


if __name__ == "__main__":
    reset_schema()
    stage1_enrich.run()        # Stage 1
    indications.run()          # Stage 2
    intake_ingest.run()        # Stage 5 call 1 (see the docstring)
    stage3_proposal.run()      # Stage 3
    print("ready: uv run uvicorn api.main:app --port 8000   then   cd web && uv run npm run dev")
    print(f"HTML report: reports/{CLIENT_SLUG}/current.html")
