---
type: cached-ai-output
title: "Cached extraction — 2026-11-06_northwind_indication_revised"
format: json-in-markdown
---

# Cached extraction — 2026-11-06_northwind_indication_revised

> Cached LLM extraction of [[raw/quillfeather/indications/2026-11-06_northwind_indication_revised.pdf|2026-11-06_northwind_indication_revised]]. Set ANTHROPIC_API_KEY to extract live.
> The pipeline re-checks every money figure below against the source text; it never trusts this file alone.

Pipeline code reads the JSON block below. Keep it valid JSON.

```json
{
  "carrier": "Northwind Specialty",
  "document_date": "2026-11-06",
  "reference": "NWS-IND-26-04417-R1",
  "firmness": "written",
  "supersedes": "NWS-IND-26-04417",
  "revision_reason": "Updated healthcare underwriting guidelines effective November 1, 2026",
  "basis_revenue": 1950000,
  "expires_on": "2026-12-21",
  "specimen_form": "NWS-CY-100 (06/25)",
  "bi_waiting_period_hours": 8,
  "conditions": [
    "Multi-factor authentication (MFA) required on email and remote access",
    "Offline or immutable backups",
    "Endpoint detection and response (EDR) on all endpoints"
  ],
  "options": [
    {
      "limit": 1000000,
      "deductible": 10000,
      "status": "indicated",
      "premium": 2910,
      "sublimits": {
        "social_engineering": 100000,
        "ransomware": "full limit"
      },
      "quote": "$1,000,000 $10,000 $2,910 $100,000 Full limit"
    },
    {
      "limit": 2000000,
      "deductible": 25000,
      "status": "indicated",
      "premium": 4620,
      "sublimits": {
        "social_engineering": 250000,
        "ransomware": "full limit"
      },
      "quote": "$2,000,000 $25,000 $4,620 $250,000 Full limit"
    }
  ]
}
```
