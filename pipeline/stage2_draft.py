"""Client pack — generate the AI draft (report v1) from enrichment + intake so far + industry research.
Prose from the LLM; numbers from the DB. Also writes reports/<slug>/current.html."""
from .config import CLIENT_SLUG
from . import narrative, report, wiki_render
from .db import client_by_slug, connect, j, user_id


def run(slug: str = CLIENT_SLUG):
    with connect() as conn:
        cid = client_by_slug(conn, slug)["id"]
        ai = user_id(conn, "Pipeline (AI)")
        facts = {r["key"]: r["current_value"] for r in
                 conn.execute("SELECT key, current_value FROM fields WHERE client_id=%s AND key IN "
                              "('industry','address','domain')", (cid,)).fetchall()}
        facts |= {"has_cyber": False, "handles_phi": True, "dmarc": "none", "online_payments": True,
                  "intake_so_far": [{"topic": t["label"], "status": t["status"]}
                                    for t in report.intake_summary(conn, cid)["topics"]]}
        blocks, provenance = narrative.generate(slug, facts)
        blocks["_provenance"] = provenance
        conn.execute("DELETE FROM report_versions WHERE client_id=%s", (cid,))
        snap = report.build_snapshot(conn, cid, blocks)
        v = conn.execute("""INSERT INTO report_versions (client_id, version_no, state, snapshot, narrative, created_by)
                            VALUES (%s, 1, 'ai_draft', %s, %s, %s) RETURNING *""", (cid, j(snap), j(blocks), ai)).fetchone()
        html_path = report.export_html(conn, cid, v)
        conn.execute("UPDATE clients SET stage='report' WHERE id=%s", (cid,))
    wiki_render.log(f"report | {slug} — v1 ai_draft created (narrative: {provenance})")
    print(f"report v1 drafted (narrative {provenance}) -> {html_path}")


if __name__ == "__main__":
    run()
