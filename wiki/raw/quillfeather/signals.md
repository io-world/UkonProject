---
type: extracted-signals
title: "Extracted signals — Quillfeather"
format: json-in-markdown
---

# Extracted signals — Quillfeather

> Structured signals extracted from the raw sources in this folder by the client-ingest skill (LLM extraction step). The deterministic pipeline turns these into estimates. Each signal cites its raw file.

Pipeline code reads the JSON block below. Edit values here and re-run the pipeline; keep it valid JSON.

```json
{
  "extracted_at": "2026-10-25",
  "entity_candidates": [
    {
      "legal_name": "Quillfeather Family Dentistry, PLLC",
      "dba": "Quillfeather Dental",
      "state": "CO",
      "address": "1450 Garrison St, Ste 200, Lakewood, CO 80215",
      "domain": "quillfeatherdental.com",
      "source": "quillfeather/sos_filing.md"
    },
    {
      "legal_name": "Quillfeather Dental Studio LLC",
      "dba": null,
      "state": "ID",
      "address": "802 W Bannock St, Boise, ID 83702",
      "domain": "quillfeatherstudio.com",
      "source": "quillfeather/decoy_sos_filing.md"
    }
  ],
  "employees": [
    {
      "value": 11,
      "source": "quillfeather/ams_export.md",
      "as_of": "2025-12-31",
      "note": "Workers' comp headcount, 2025 payroll audit"
    },
    {
      "value": 12,
      "source": "quillfeather/ppp_record.md",
      "as_of": "2020-04-28",
      "note": "PPP jobs reported"
    },
    {
      "value": 13,
      "source": "quillfeather/website.md",
      "as_of": "2026-10-24",
      "note": "Team page lists 13 people"
    }
  ],
  "hiring": {
    "value": true,
    "source": "quillfeather/job_postings.md",
    "note": "Open dental assistant posting"
  },
  "dentists": {
    "value": 2,
    "sources": [
      "quillfeather/website.md",
      "quillfeather/ams_export.md"
    ]
  },
  "agency_revenue": {
    "value": null,
    "source": "quillfeather/ams_export.md",
    "note": "BOP rated on property; no gross sales on file"
  },
  "industry": {
    "naics": "621210",
    "label": "Offices of Dentists",
    "sources": [
      "quillfeather/ams_export.md (SIC 8021)",
      "quillfeather/ppp_record.md (NAICS 621210)",
      "quillfeather/website.md"
    ]
  },
  "domain": {
    "value": "quillfeatherdental.com",
    "sources": [
      "quillfeather/ams_export.md (contact email domain)",
      "quillfeather/website.md",
      "quillfeather/dns_records.md (MX present)"
    ]
  },
  "address": {
    "value": "1450 Garrison St, Ste 200, Lakewood, CO 80215",
    "state": "CO",
    "sources": [
      "quillfeather/ams_export.md",
      "quillfeather/sos_filing.md",
      "quillfeather/ppp_record.md",
      "quillfeather/website.md"
    ]
  },
  "exposure_inputs": {
    "data_class": "phi",
    "online_payments": true,
    "records_est": 8000,
    "records_note": "Not stated anywhere. Estimated: ~1,500-2,000 active patients per general dentist x 2 dentists, all-time records typically 2-3x active. Ask on the call.",
    "dmarc": "none",
    "spf": "~all",
    "sources": [
      "quillfeather/dns_records.md",
      "quillfeather/website.md"
    ]
  },
  "owner": {
    "name": "Dr. Maya Ellery",
    "last": "Ellery",
    "source": "quillfeather/ams_export.md"
  },
  "city": "Lakewood"
}
```
