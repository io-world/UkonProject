---
type: source-overview
client: sloanslake
retrieved: 2026-10-26
---

# Sloan's Lake Dental — what's real, what's simulated

The demo client is a **real Denver dental practice**. Everything a person could find about it publicly is
captured here as raw sources, with links, retrieved 2026-10-26. What only the agency, the carriers or the
practice itself would know is **simulated** and labeled as such in each file.

## Real (public)

| Source | What it gives | |
|---|---|---|
| [[raw/sloanslake/co_sos_entities\|Colorado business registry]] | Legal name **Sage Dentistry, PLLC** (Good Standing, formed 2015-06-02, 2750 W 29th Ave); a **delinquent** "Sloans Lake Dental PLLC" at the same address; six dissolved "Sage Dentistry II–VII" offices; an unrelated 2005 "SLOANS LAKE DENTAL PLLC" | entity resolution |
| [[raw/sloanslake/npi_registry\|NPI registry]] | Organization NPI 1316327604 "SAGE DENTISTRY PLLC SLOANS LAKE DENTAL" (ties trade name to entity); owner Dr. Sage Pollack; look-alikes (Sloanside Dental, Sage Dental Care, Sage Dental Group) | entity resolution |
| [[raw/sloanslake/website\|Website]] | 3 dentists; implant/cosmetic-heavy services; vendors: Adit (booking, bill pay), Progressive Dental Marketing (site), Trustindex; 620 Google reviews | industry, exposure |
| [[raw/sloanslake/dns_records\|DNS records]] | Paubox email, Microsoft 365 via GoDaddy, strict SPF (`-all`), **no DMARC** | exposure |
| [[raw/sloanslake/directory_listings\|Directory listings]] | Stale WebMD listing at **4441 W 29th Ave** (same phone); WebMD lists 7 dentists incl. former affiliates | conflicts to ignore |
| [[raw/sloanslake/press_releases\|Press releases]] | Aug/Sep 2025: one location, 3 dentists, in-house 3D printing | dentists, industry |
| [[raw/research/621210_dental_cyber\|Industry research]] | Real 2025–26 incidents: Longmont CO breach, Colorado ransomware listing, phished dental mailboxes, MSP-entry settlement, DMARC gap in breached orgs | client pack, brief |

## Not public, so estimated (flagged for the call)

- **Headcount:** none published. Estimated 12 (3 dentists × ~4 support staff, an assumption). Low confidence.
- **Revenue:** none published, none at the agency. $2.35M (range $1.65M–$3.2M) from two benchmark methods. Low confidence; the implant mix probably pushes it higher.
- **Patient records:** ~12,000 all-time (estimate).

## Simulated (labeled in each file)

- [[raw/sloanslake/ams_export|AMS export]] — the agency (Front Range IIG), its staff and the client's other policies.
- [[raw/sloanslake/call_1_intake|Intake call 1]] and [[raw/sloanslake/call_2_followup|call 2]] — never happened; answers are invented and are not statements by anyone at the practice. Speakers are roles.
- Carrier replies in `raw/sloanslake/indications/` — fictional carriers (Northwind, Cobalt Harbor, Ridgeline), invented premiums calibrated to [[raw/benchmarks/cyber_premium_benchmarks|published benchmarks]]. Real carrier names aren't used: a made-up quote on a real carrier's letterhead would be a fake document.

## The Stage 1 story this client tells

1. **Name search is a trap.** "Sloans Lake Dental PLLC" matches the trade name and the address exactly, but it's delinquent. The right named insured is Sage Dentistry, PLLC. Entity resolution penalizes non-good-standing status; a person confirms.
2. **Directories disagree.** WebMD shows a second address and seven dentists. The state and NPI records don't support either; the pipeline cites and ignores them.
3. **Good email hygiene, one gap.** Encrypted email and a hard-fail SPF, but no DMARC: a free fix that insurers and the [[raw/research/621210_dental_cyber|research]] both point to.
4. **Vendors are part of the exposure.** Adit (bookings, payments), Paubox, Microsoft 365, the website firm, and an IT provider all touch patient data.
