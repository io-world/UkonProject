---
type: extracted-signals
title: "Extracted signals — Sloan's Lake Dental"
format: json-in-markdown
---

# Extracted signals — Sloan's Lake Dental

> Structured signals extracted from the REAL public sources in this folder (plus the simulated AMS row) by
> the client-ingest skill. The deterministic pipeline turns these into estimates. Each signal cites its raw file.
> Headcount and revenue are not published anywhere; they are estimated and flagged for the call.

Pipeline code reads the JSON block below. Keep it valid JSON.

```json
{
  "extracted_at": "2026-10-26",
  "entity_candidates": [
    {
      "legal_name": "Sage Dentistry, PLLC",
      "dba": "Sloan's Lake Dental",
      "state": "CO",
      "status": "Good Standing",
      "address": "2750 W 29th Ave, Denver, CO 80211",
      "domain": "sloanslakedental.com",
      "source": "sloanslake/co_sos_entities.md (ID 20151370188; DBA via NPI 1316327604)"
    },
    {
      "legal_name": "Sloans Lake Dental PLLC",
      "dba": null,
      "state": "CO",
      "status": "Delinquent since 2022-05-01",
      "address": "2750 W 29th Ave, Denver, CO 80211",
      "domain": null,
      "source": "sloanslake/co_sos_entities.md (ID 20208083017)"
    },
    {
      "legal_name": "Sage Dentistry II, PLLC",
      "dba": null,
      "state": "CO",
      "status": "Voluntarily Dissolved 2024-03-04",
      "address": "2750 W 29th Ave, Denver, CO 80211",
      "domain": null,
      "source": "sloanslake/co_sos_entities.md (ID 20161256592)"
    },
    {
      "legal_name": "Darren Bennett DDS PC",
      "dba": "Sloanside Dental",
      "state": "CO",
      "status": "Active (NPI)",
      "address": "2045 Sheridan Blvd, Suite H, Edgewater, CO 80214",
      "domain": null,
      "source": "sloanslake/npi_registry.md (NPI 1245524800)"
    },
    {
      "legal_name": "SLOANS LAKE DENTAL PLLC",
      "dba": null,
      "state": "CO",
      "status": "Voluntarily Dissolved 2006-06-19",
      "address": "1776 S. Jackson St, Suite 612, Denver, CO 80210",
      "domain": null,
      "source": "sloanslake/co_sos_entities.md (ID 20051017632)"
    }
  ],
  "employees": [
    {
      "value": 12,
      "source": "sloanslake/website.md",
      "as_of": "2026-10-26",
      "estimated": true,
      "note": "Not published. Estimated: 3 dentists on the team page x about 4 support staff per dentist (hygienists, assistants, front office). The 4-per-dentist ratio is an assumption, not a sourced figure; confirm on the call."
    }
  ],
  "hiring": {
    "value": false,
    "source": null,
    "note": "No current job postings found"
  },
  "dentists": {
    "value": 3,
    "sources": [
      "sloanslake/website.md (team page, Oct 2026)",
      "sloanslake/press_releases.md (Aug 2025: three dentists)",
      "sloanslake/ams_export.md (3 dentists on professional liability, simulated)"
    ],
    "note": "WebMD lists 7 at this address, likely including dentists from the dissolved Sage Dentistry offices.",
    "method": "Website team page (3) matches the Aug 2025 press release (3) and the professional liability policy. WebMD's 7 likely includes dentists from the dissolved Sage Dentistry offices."
  },
  "agency_revenue": {
    "value": null,
    "source": "sloanslake/ams_export.md",
    "note": "BOP rated on property; no gross sales on file"
  },
  "industry": {
    "naics": "621210",
    "label": "Offices of Dentists",
    "sources": [
      "sloanslake/ams_export.md (SIC 8021)",
      "sloanslake/npi_registry.md (taxonomy 122300000X Dentist)",
      "sloanslake/website.md (general, implant and cosmetic dentistry)"
    ],
    "method": "Agency SIC code 8021 crosswalked to NAICS 621210; matches the NPI dentist taxonomy and the website's services."
  },
  "domain": {
    "value": "sloanslakedental.com",
    "sources": [
      "sloanslake/ams_export.md (contact email domain)",
      "sloanslake/website.md",
      "sloanslake/dns_records.md (MX via Paubox)"
    ],
    "method": "Agency contact email domain matches the website and live mail (MX) records."
  },
  "address": {
    "value": "2750 W 29th Ave, Denver, CO 80211",
    "state": "CO",
    "sources": [
      "sloanslake/ams_export.md",
      "sloanslake/co_sos_entities.md",
      "sloanslake/npi_registry.md",
      "sloanslake/website.md"
    ],
    "note": "One WebMD listing shows 4441 W 29th Ave with the same phone; no state record supports it (stale listing).",
    "method": "Agency record, state registry (principal office), NPI record and website all agree. A WebMD listing at 4441 W 29th Ave with the same phone is ignored: no state or NPI record supports it."
  },
  "exposure_inputs": {
    "data_class": "phi",
    "online_payments": true,
    "records_est": 12000,
    "records_low": 8000,
    "records_high": 16000,
    "records_note": "Not published. Estimated: ~1,500 active patients per dentist x 3 dentists, all-time records typically 2-3x active; 620 Google reviews suggest a large, long-running patient base. Ask on the call.",
    "dmarc": "missing",
    "spf": "-all",
    "sources": [
      "sloanslake/dns_records.md",
      "sloanslake/website.md (Adit online bill pay)"
    ]
  },
  "tech_stack": [
    {
      "vendor": "Paubox",
      "role": "Inbound/outbound email (HIPAA encrypted email)",
      "source": "sloanslake/dns_records.md"
    },
    {
      "vendor": "Microsoft 365 (via GoDaddy)",
      "role": "Mailboxes and office apps",
      "source": "sloanslake/dns_records.md"
    },
    {
      "vendor": "GoDaddy",
      "role": "Domain DNS",
      "source": "sloanslake/dns_records.md"
    },
    {
      "vendor": "Adit",
      "role": "Online booking and patient bill pay",
      "source": "sloanslake/website.md"
    },
    {
      "vendor": "Progressive Dental Marketing",
      "role": "Website (WordPress) and marketing",
      "source": "sloanslake/website.md"
    }
  ],
  "owner": {
    "name": "Dr. Sage Pollack",
    "last": "Pollack",
    "source": "sloanslake/npi_registry.md (authorized official, owner)"
  },
  "city": "Denver"
}
```
