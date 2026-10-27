"""Reset the database and run the demo flow for the demo client (Sloan's Lake Dental, config.CLIENT_SLUG):

  1. Enrich       Stage 1 fields from public + agency sources        (stage1_enrich)
  2. Indications  carrier ballparks, locked                          (indications)
  3. Intake       first intake call (Wispr Flow transcript), partial (intake_ingest, call 1)
  4. Client pack  report v1 from enrichment + intake + research      (stage2_draft)

Later intake calls are ingested separately; open questions don't block the client pack:
    uv run python -m pipeline.intake_ingest wiki/raw/sloanslake/call_2_followup.md"""
import psycopg

from . import indications, intake_ingest, stage1_enrich, stage2_draft
from .config import CLIENT_SLUG, DATABASE_URL, ROOT


def reset_schema():
    with psycopg.connect(DATABASE_URL) as conn:
        conn.execute((ROOT / "db" / "schema.sql").read_text())
    print("schema reset")


if __name__ == "__main__":
    reset_schema()
    stage1_enrich.run()
    indications.run()
    intake_ingest.run()
    stage2_draft.run()
    print("ready: uv run uvicorn api.main:app --port 8000   then   cd web && npm run dev")
    print(f"HTML report: reports/{CLIENT_SLUG}/current.html")
