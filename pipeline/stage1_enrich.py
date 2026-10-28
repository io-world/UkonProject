"""Stage 1 — turn extracted signals into the five indication fields (plus exposure),
each with value, range, confidence, method and sources. Writes DB, then renders the wiki."""
from datetime import date

from .sources import read_source
from . import entity_resolution, estimators, staff_costs, wiki_render
from .config import CLIENT_SLUG, RAW
from .db import client_by_slug, connect, j, user_id

USERS = [("Pipeline (AI)", "system"), ("Jordan Pike", "account_manager"),
         ("Alex Moreno", "producer"), ("Sam Ortiz", "cpl")]

BENCHMARKS = [
    ("scenario.ir_cost_median", "Small-business incident response — median", 36_000,
     "benchmarks/claims_benchmarks.md (S&P Global)"),
    ("scenario.ir_cost_average", "Small-business incident response — average", 175_000,
     "benchmarks/claims_benchmarks.md (S&P Global)"),
    ("scenario.bec_claim_cost", "Average business email compromise claim", 75_000,
     "benchmarks/claims_benchmarks.md (NetDiligence 2025)"),
    ("scenario.sme_incident_cost", "SME average cyber incident cost", 264_000,
     "benchmarks/claims_benchmarks.md (NetDiligence 2025)"),
    ("benchmark.overhead_low", "Dental practice overhead — low (share of revenue)", 0.60,
     "benchmarks/dental_overhead_benchmarks.md (ADA via Overjet)"),
    ("benchmark.overhead_high", "Dental practice overhead — high (share of revenue)", 0.65,
     "benchmarks/dental_overhead_benchmarks.md (ADA via Overjet)"),
]


def upsert_field(conn, client_id, key, label, kind, value, *, low=None, high=None, confidence=None,
                 method="", sources=(), adjustable=True, needs_review=False, actor=None):
    conn.execute("""
        INSERT INTO fields (client_id, key, label, kind, ai_value, ai_low, ai_high, confidence, method,
                            sources, current_value, adjustable, needs_review, updated_by)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        ON CONFLICT (client_id, key) DO UPDATE SET
          ai_value=EXCLUDED.ai_value, ai_low=EXCLUDED.ai_low, ai_high=EXCLUDED.ai_high,
          confidence=EXCLUDED.confidence, method=EXCLUDED.method, sources=EXCLUDED.sources,
          needs_review=EXCLUDED.needs_review, updated_at=now()
    """, (client_id, key, label, kind, j(value), low, high, confidence, method, j(list(sources)),
          j(value), adjustable, needs_review, actor))


def seed(conn, slug: str):
    for name, role in USERS:
        conn.execute("INSERT INTO users (name, role) SELECT %s,%s WHERE NOT EXISTS "
                     "(SELECT 1 FROM users WHERE name=%s)", (name, role, name))
    ams = read_source(RAW / slug / "ams_export.md")
    conn.execute("""INSERT INTO clients (slug, display_name, renewal_date, agency)
                    VALUES (%s,%s,%s,%s) ON CONFLICT (slug) DO NOTHING""",
                 (slug, ams["client"]["account_name"], ams["policies"][0]["expiration"], ams["agency"]))
    return ams


def run(slug: str = CLIENT_SLUG, today: date = date(2026, 10, 26)):
    sig = read_source(RAW / slug / "signals.md")
    with connect() as conn:
        ams = seed(conn, slug)
        cid = client_by_slug(conn, slug)["id"]
        ai = user_id(conn, "Pipeline (AI)")

        # Entity candidates — scored, never auto-confirmed
        conn.execute("DELETE FROM entity_candidates WHERE client_id=%s AND status='suggested'", (cid,))
        for cand in sig["entity_candidates"]:
            s = entity_resolution.score(ams["client"], cand)
            conn.execute("""INSERT INTO entity_candidates (client_id, legal_name, state, address, domain,
                            match_score, signals) VALUES (%s,%s,%s,%s,%s,%s,%s)""",
                         (cid, cand["legal_name"], cand["state"], cand["address"], cand["domain"],
                          s["match_score"], j(s["signals"] | {"source": cand["source"], "registry": cand.get("status")})))
        top = max(sig["entity_candidates"], key=lambda c: entity_resolution.score(ams["client"], c)["match_score"])
        upsert_field(conn, cid, "legal_name", "Business legal name", "text", top["legal_name"],
                     confidence="medium", method="Top-scoring entity candidate; a person confirms the match, or edits the name (logged with its source).",
                     sources=[top["source"]], adjustable=True, needs_review=True, actor=ai)

        # Domain, industry, address — high confidence when independent sources agree
        upsert_field(conn, cid, "domain", "Website / domain", "text", sig["domain"]["value"], confidence="high",
                     method=sig["domain"].get("method", "Agency contact email domain matches the website and live mail (MX) records."),
                     sources=sig["domain"]["sources"], actor=ai)
        upsert_field(conn, cid, "industry", "Industry", "text",
                     f"{sig['industry']['label']} (NAICS {sig['industry']['naics']})", confidence="high",
                     method=sig["industry"].get("method", "Agency SIC code crosswalked to NAICS; matches public records and website content."),
                     sources=sig["industry"]["sources"], actor=ai)
        upsert_field(conn, cid, "address", "Business address / state", "text", sig["address"]["value"],
                     confidence="high", method=sig["address"].get("method", "Agency, state filing and website all agree."),
                     sources=sig["address"]["sources"], actor=ai)

        # Employees → revenue
        emp = estimators.estimate_employees(
            [estimators.Signal(s["value"], s["source"], date.fromisoformat(s["as_of"]), s["note"], s.get("estimated", False))
             for s in sig["employees"]], today, hiring=sig["hiring"]["value"])
        upsert_field(conn, cid, "employee_count", "Employees", "int", int(emp.value), low=emp.low, high=emp.high,
                     confidence=emp.confidence, method=emp.method + (f" CONFLICT: {emp.conflict}" if emp.conflict else ""),
                     sources=emp.sources, needs_review=emp.needs_review, actor=ai)
        rev = estimators.estimate_revenue(sig["agency_revenue"]["value"], emp.value, sig["dentists"]["value"], slug,
                                          employees_estimated=all(s.get("estimated") for s in sig["employees"]))
        upsert_field(conn, cid, "annual_revenue", "Annual revenue", "money", rev.value, low=rev.low, high=rev.high,
                     confidence=rev.confidence, method=rev.method, sources=rev.sources,
                     needs_review=rev.needs_review, actor=ai)

        # Exposure (stand-in for a security scan)
        ex_in = sig["exposure_inputs"]
        ex = estimators.exposure_score(ex_in["data_class"], int(emp.value), ex_in["dmarc"], ex_in["spf"],
                                       ex_in["online_payments"], ex_in["records_est"])
        upsert_field(conn, cid, "exposure_score", "Exposure score (0–100)", "score", ex["score"], low=0, high=100,
                     confidence="low",
                     method="Rough proxy, not a security scan: data sensitivity + email accounts + public DNS email "
                            "settings + online payments + record volume. Security controls unknown until the call.",
                     sources=ex_in["sources"], needs_review=False, actor=ai)
        upsert_field(conn, cid, "exposure_breakdown", "Exposure breakdown", "text", ex, adjustable=False, actor=ai)
        upsert_field(conn, cid, "records_estimate", "Patient records held (est.)", "int", ex_in["records_est"],
                     low=ex_in.get("records_low"), high=ex_in.get("records_high"), confidence="low", method=ex_in["records_note"], sources=[], actor=ai)
        upsert_field(conn, cid, "dentists", "Dentists", "int", sig["dentists"]["value"], confidence="high",
                     method=sig["dentists"].get("method", "Website team page and professional liability policy agree."),
                     sources=sig["dentists"]["sources"], adjustable=True, actor=ai)

        # Average staff pay: national wage data for the client's industry (no AI). The agent can move it on Stage 3;
        # the owner's real payroll replaces it once confirmed.
        wb = staff_costs.wage_benchmark(f"{sig['industry']['naics']}")
        if wb:
            upsert_field(conn, cid, "avg_staff_pay", "Average staff pay (per person, per year)", "money",
                         wb["default_avg_pay"], low=wb["low"], high=wb["high"], confidence="low",
                         method=f"{wb['source']}: average pay of {wb['who']}, weighted by how many people hold each role. "
                                "National wages only (no benefits or payroll taxes), not this practice's payroll.",
                         sources=[f"{wb['wiki']}.md"], adjustable=True, actor=ai)

        for key, label, value, src in BENCHMARKS:
            upsert_field(conn, cid, key, label, "benchmark", value, confidence="high",
                         method="Published benchmark", sources=[src], adjustable=True, actor=ai)

        wiki_render.render_client(conn, cid)
    wiki_render.log(f"estimate | {slug} — stage 1 fields computed")
    print(f"stage 1 done: employees={emp.value:.0f} ({emp.confidence}), revenue=${rev.value:,} ({rev.confidence}), "
          f"exposure={ex['score']} ({ex['band']})")


if __name__ == "__main__":
    run()
