---
type: index
---

# Wiki Index

Open this `wiki/` folder as an Obsidian vault. Rules for how it's maintained: [[CLAUDE]].
Activity history: [[log]].

## Clients
- [[clients/sloanslake|Sloan's Lake Dental (Sage Dentistry, PLLC)]] — REAL Denver dental practice; renews 2027-01-15 (simulated); no cyber on file. *Generated from the database.*
- [[clients/sloanslake-indications|Sloan's Lake carrier indications]] — requests sent, every reply as a version, diffs, actions. *Generated.*
- [[clients/sloanslake-intake|Sloan's Lake intake]] — every intake answer with its quote, call, status and conflicts. *Generated.*
- [[raw/sloanslake/00_overview|What's real vs simulated for this client]] — start here.

## Industries
- [[industries/621210-dental-offices|Offices of Dentists (621210)]] — scenarios, CPL-approved objection library, escalation triggers, carrier gates

## Raw sources — Sloan's Lake Dental (REAL public data unless marked)
- [[raw/sloanslake/00_overview|Overview: real vs simulated]]
- [[raw/sloanslake/co_sos_entities|Colorado business registry]] — Sage Dentistry, PLLC in good standing; delinquent "Sloans Lake Dental PLLC" at the same address; dissolved Sage Dentistry II–VII
- [[raw/sloanslake/npi_registry|NPI registry]] — practice NPI ties the trade name to the LLC; owner; look-alike names
- [[raw/sloanslake/website|Website capture]] — 3 dentists, implant/cosmetic services, Adit booking and bill pay, 620 reviews
- [[raw/sloanslake/dns_records|DNS email records]] — Paubox + Microsoft 365, SPF -all, no DMARC
- [[raw/sloanslake/directory_listings|Directory listings]] — stale second address; 7 dentists listed (former affiliates)
- [[raw/sloanslake/press_releases|Press releases]] — Aug/Sep 2025, self-reported
- [[raw/sloanslake/signals|Extracted signals]] — what the ingest step pulled out, per source
- [[raw/sloanslake/ams_export|AMS export]] — SIMULATED agency record: no revenue, no headcount
- [[raw/sloanslake/call_1_intake|Intake call 1]] — SIMULATED; owner (role); revenue left to the accountant; one coverage question for a CPL
- [[raw/sloanslake/call_2_followup|Intake call 2]] — SIMULATED; office manager (role); closes MFA and EDR, backups still open

## Carrier replies — Sloan's Lake (SIMULATED: fictional carriers, real insured)
- [[raw/sloanslake/indications/2026-10-27_northwind_indication.pdf|Northwind letter, Oct 27]] — $1M $2,980 · $2M $4,720
- [[raw/sloanslake/indications/2026-10-28_cobalt_harbor_email|Cobalt Harbor email, Oct 28]] — $2M written as "5.29k" (figure to confirm)
- [[raw/sloanslake/indications/2026-10-28_ridgeline_underwriter_call|Ridgeline underwriter call, Oct 28]] — verbal "around twenty-six hundred"; $2M declined
- [[raw/sloanslake/indications/2026-10-30_ridgeline_indication.pdf|Ridgeline letter, Oct 30]] — $1M $2,590 in writing; $2M declined
- [[raw/sloanslake/indications/2026-11-06_northwind_indication_revised.pdf|Northwind revised letter, Nov 6]] — +10%, adds EDR (demo: ingest live)

## Intake
- [[raw/intake/intake_questions|Intake question bank]] — drives the call screen, extraction and the intake page
- [[raw/intake/walkthrough_script|Limit walkthrough script]]

## Industry research (real, cited)
- [[raw/research/621210_dental_cyber|Dental offices and cyber, Oct 2026]] — 13 real, cited items: Colorado breaches and ransomware listings, phished dental mailboxes, vendor/MSP incidents, DMARC, regulation

## Benchmarks (real, published)
- [[raw/benchmarks/cyber_premium_benchmarks|Cyber premium benchmarks]]
- [[raw/benchmarks/dental_industry_benchmarks|Dental industry benchmarks]]
- [[raw/benchmarks/claims_benchmarks|Cyber claims benchmarks]]

## Carrier material (fictional carriers, benchmark-calibrated)
- [[raw/carriers/carrier_panel|Carrier panel]] — who gets indication requests, and how
- [[raw/carriers/coverage_language|Approved coverage language]]
- [[raw/carriers/specimen_map|Specimen locations]]
- [[raw/carriers/application_questions|Application question bank]]

## Cached AI output (used when no API key is set)
- [[raw/_cache/narrative_sloanslake|Report narrative]]
- [[raw/_cache/call_extraction_sloanslake_call_1_intake|Extraction — intake call 1]]
- [[raw/_cache/call_extraction_sloanslake_call_2_followup|Extraction — intake call 2]]
- Carrier reply extractions: `raw/_cache/indication_extraction_sloanslake_*` (one per reply)
