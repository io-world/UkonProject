---
type: cached-ai-output
title: "Cached extraction — 2026-10-27_northwind_indication"
format: json-in-markdown
---

# Cached extraction — 2026-10-27_northwind_indication

> Cached LLM extraction of [[raw/quillfeather/indications/2026-10-27_northwind_indication.pdf|2026-10-27_northwind_indication]]. Set ANTHROPIC_API_KEY to extract live.
> The pipeline re-checks every money figure below against the source text; it never trusts this file alone.

Pipeline code reads the JSON block below. Keep it valid JSON.

```json
{
  "carrier": "Northwind Specialty",
  "document_date": "2026-10-27",
  "reference": "NWS-IND-26-04417",
  "firmness": "written",
  "supersedes": null,
  "basis_revenue": 1950000,
  "expires_on": "2026-12-11",
  "specimen_form": "NWS-CY-100 (06/25)",
  "bi_waiting_period_hours": 8,
  "conditions": [
    "Multi-factor authentication (MFA) required on email and remote access",
    "Offline or immutable backups"
  ],
  "options": [
    {
      "limit": 1000000,
      "deductible": 10000,
      "status": "indicated",
      "premium": 2640,
      "sublimits": {
        "social_engineering": 100000,
        "ransomware": "full limit"
      },
      "quote": "$1,000,000 $10,000 $2,640 $100,000 Full limit"
    },
    {
      "limit": 2000000,
      "deductible": 25000,
      "status": "indicated",
      "premium": 4180,
      "sublimits": {
        "social_engineering": 250000,
        "ransomware": "full limit"
      },
      "quote": "$2,000,000 $25,000 $4,180 $250,000 Full limit"
    }
  ]
}
```
