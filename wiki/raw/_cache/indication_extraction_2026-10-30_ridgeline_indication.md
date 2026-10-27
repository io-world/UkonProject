---
type: cached-ai-output
title: "Cached extraction — 2026-10-30_ridgeline_indication"
format: json-in-markdown
---

# Cached extraction — 2026-10-30_ridgeline_indication

> Cached LLM extraction of [[raw/quillfeather/indications/2026-10-30_ridgeline_indication.pdf|2026-10-30_ridgeline_indication]]. Set ANTHROPIC_API_KEY to extract live.
> The pipeline re-checks every money figure below against the source text; it never trusts this file alone.

Pipeline code reads the JSON block below. Keep it valid JSON.

```json
{
  "carrier": "Ridgeline Mutual",
  "document_date": "2026-10-30",
  "reference": "RM-Q-118204",
  "firmness": "written",
  "supersedes": null,
  "basis_revenue": 1950000,
  "expires_on": "2026-12-14",
  "specimen_form": "RM-CYB-4 (01/26)",
  "bi_waiting_period_hours": 10,
  "conditions": [
    "MFA required on email",
    "Endpoint detection and response (EDR) on all devices"
  ],
  "options": [
    {
      "limit": 1000000,
      "deductible": 10000,
      "status": "indicated",
      "premium": 2290,
      "sublimits": {
        "social_engineering": 100000,
        "ransomware": 500000
      },
      "quote": "$1,000,000 $10,000 $2,290 $100,000 $500,000"
    },
    {
      "limit": 2000000,
      "deductible": 25000,
      "status": "declined",
      "premium": null,
      "sublimits": {},
      "note": "Ridgeline does not offer limits above $1,000,000 for dental offices with fewer than 20 employees.",
      "quote": "$2,000,000 option declined: Ridgeline does not offer limits above $1,000,000 for dental offices with fewer than 20 employees."
    }
  ]
}
```
