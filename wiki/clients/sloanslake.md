---
type: client
generated: true
client_id: 1
legal_name: "UNCONFIRMED"
naics: "621210"
renewal_date: 2027-01-15
last_rendered: 2026-10-27T01:45:45+00:00
---

# Sloan's Lake Dental

Agency: Front Range Independent Insurance Group (fictional) · Renewal: **2027-01-15** · Stage: `report` · Industry: [[621210-dental-offices]]

> [!warning] Generated page — do not edit in Obsidian
> Rendered from the database on every change; edits here are overwritten. Change values in the app
> (logged with your name). Annotate in [[621210-dental-offices|the industry page]] or the raw sources instead.

## Entity resolution

- **Sage Dentistry, PLLC** (CO) — match 100% — `suggested` — name 100%, state 100%, domain 100%, status 100%, address 100% — registry: Good Standing — [[raw/sloanslake/co_sos_entities|co_sos_entities]] (ID 20151370188; DBA via NPI 1316327604)
- **Darren Bennett DDS PC** (CO) — match 40% — `suggested` — name 80%, state 100%, domain 0%, status 100%, address 0% — registry: Active (NPI) — [[raw/sloanslake/npi_registry|npi_registry]] (NPI 1245524800)
- **Sloans Lake Dental PLLC** (CO) — match 37% — `suggested` — name 97%, state 100%, domain 0%, status 0%, address 100% — registry: Delinquent since 2022-05-01 — [[raw/sloanslake/co_sos_entities|co_sos_entities]] (ID 20208083017)
- **Sage Dentistry II, PLLC** (CO) — match 30% — `suggested` — name 44%, state 100%, domain 0%, status 0%, address 100% — registry: Voluntarily Dissolved 2024-03-04 — [[raw/sloanslake/co_sos_entities|co_sos_entities]] (ID 20161256592)
- **SLOANS LAKE DENTAL PLLC** (CO) — match 22% — `suggested` — name 97%, state 100%, domain 0%, status 0%, address 0% — registry: Voluntarily Dissolved 2006-06-19 — [[raw/sloanslake/co_sos_entities|co_sos_entities]] (ID 20051017632)

## Indication fields

### Business legal name
- Value: **Sage Dentistry, PLLC**
- Confidence: medium · **needs review**
- Method: Top-scoring entity candidate; a person confirms the match, or edits the name (logged with its source).
- Sources: [[raw/sloanslake/co_sos_entities|co_sos_entities]] (ID 20151370188; DBA via NPI 1316327604)
- Last changed by: Jordan Pike

### Website / domain
- Value: **sloanslakedental.com**
- Confidence: high
- Method: Agency contact email domain matches the website and live mail (MX) records.
- Sources: [[raw/sloanslake/ams_export|ams_export]] (contact email domain), [[raw/sloanslake/website|website]], [[raw/sloanslake/dns_records|dns_records]] (MX via Paubox)
- Last changed by: Pipeline (AI)

### Industry
- Value: **Offices of Dentists (NAICS 621210)**
- Confidence: high
- Method: Agency SIC code 8021 crosswalked to NAICS 621210; matches the NPI dentist taxonomy and the website's services.
- Sources: [[raw/sloanslake/ams_export|ams_export]] (SIC 8021), [[raw/sloanslake/npi_registry|npi_registry]] (taxonomy 122300000X Dentist), [[raw/sloanslake/website|website]] (general, implant and cosmetic dentistry)
- Last changed by: Pipeline (AI)

### Business address / state
- Value: **2750 W 29th Ave, Denver, CO 80211**
- Confidence: high
- Method: Agency record, state registry (principal office), NPI record and website all agree. A WebMD listing at 4441 W 29th Ave with the same phone is ignored: no state or NPI record supports it.
- Sources: [[raw/sloanslake/ams_export|ams_export]], [[raw/sloanslake/co_sos_entities|co_sos_entities]], [[raw/sloanslake/npi_registry|npi_registry]], [[raw/sloanslake/website|website]]
- Last changed by: Pipeline (AI)

### Employees
- Value: **12**
- Range: 9 – 15
- Confidence: low · **needs review**
- Method: Not published. Estimated: 3 dentists on the team page x about 4 support staff per dentist (hygienists, assistants, front office). The 4-per-dentist ratio is an assumption, not a sourced figure; confirm on the call. Range ±25%.
- Sources: [[raw/sloanslake/website|website]]
- Last changed by: Pipeline (AI)

### Annual revenue
- Value: **$2,350,000**
- Range: $1,650,000 – $3,200,000
- Confidence: low · **needs review**
- Method: No revenue on file at the agency; private entity, no public filings. Method A: 12 staff × $152,600 revenue per employee (Census 2022 ÷ BLS 2022) = $1,831,200. Method B: 3 dentists × $965,660 average gross billings (ADA 2025) = $2,896,980. Method A rests on an estimated headcount, so the two methods aren't independent. Methods differ by 45%, so confidence is low; estimate is their average, rounded to $50K. Confirm with the client before binding.
- Sources: [[raw/benchmarks/dental_industry_benchmarks|dental_industry_benchmarks]], [[raw/sloanslake/website|website]], [[raw/sloanslake/ams_export|ams_export]]
- Last changed by: Pipeline (AI)

### Exposure score (0–100)
  - Handles patient health information: +25
  - 12 email accounts that could be phished: +14.4
  - No email spoofing protection (DMARC) record: +12
  - Sender policy (SPF) ends in '-all': +0
  - Takes payments online: +7
  - Holds more than 5,000 records: +10
  - Calls to confirm payment changes (from intake): -5
  - Unknown until the call: mfa_email, tested_backups, edr
- Value: **63**
- Range: 0 – 100
- Confidence: low
- Method: Rough proxy, not a security scan: data sensitivity + email accounts + public DNS email settings + online payments + record volume, minus credits for controls the intake confirmed cleanly.
- Sources: [[raw/sloanslake/dns_records|dns_records]], [[raw/sloanslake/website|website]] (Adit online bill pay)
- Last changed by: Pipeline (AI)

### Patient records held (est.)
- Value: **12000**
- Range: 8,000 – 16,000
- Confidence: low
- Method: Not published. Estimated: ~1,500 active patients per dentist x 3 dentists, all-time records typically 2-3x active; 620 Google reviews suggest a large, long-running patient base. Ask on the call.
- Sources: none (estimate — confirm on the call)
- Last changed by: Pipeline (AI)

### Dentists
- Value: **3**
- Confidence: high
- Method: Website team page (3) matches the Aug 2025 press release (3) and the professional liability policy. WebMD's 7 likely includes dentists from the dissolved Sage Dentistry offices.
- Sources: [[raw/sloanslake/website|website]] (team page, Oct 2026), [[raw/sloanslake/press_releases|press_releases]] (Aug 2025: three dentists), [[raw/sloanslake/ams_export|ams_export]] (3 dentists on professional liability, simulated)
- Last changed by: Pipeline (AI)

### Carrier shown to client
- Value: **Northwind Specialty**
- Confidence: high
- Method: Default rule: lowest $1M premium that keeps ransomware at the full limit, from written, checked indications. Agent may switch.
- Sources: Northwind Specialty v1, Ridgeline Mutual v2
- Last changed by: Pipeline (AI)

## Human changes

- 2026-10-26 19:43 — Jordan Pike changed **Business legal name** Sage Dentistry, PLLC → Sage Dentistry, PLLC — "Entity match confirmed"
- 2026-10-26 19:45 — Jordan Pike changed **Business legal name** Sage Dentistry, PLLC → Sage Dentistry, PLLC — "Undid company confirmation (Sage Dentistry, PLLC)"
- 2026-10-26 19:45 — Jordan Pike changed **Business legal name** Sage Dentistry, PLLC → Darren Bennett DDS PC — "Entity match confirmed"
- 2026-10-26 19:45 — Jordan Pike changed **Business legal name** Darren Bennett DDS PC → Sage Dentistry, PLLC — "Undid company confirmation (Darren Bennett DDS PC)"
