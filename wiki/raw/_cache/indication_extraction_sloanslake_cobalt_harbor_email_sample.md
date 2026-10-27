---
type: cached-ai-output
title: "Cached extraction — 2026-10-28_cobalt_harbor_email"
format: json-in-markdown
content_sha256: 2deea3c9ae20ea220ab4db9987c014ea7f20a4bfa532dd709f1a33b8b3bd98c2
---

# Cached extraction — 2026-10-28_cobalt_harbor_email

> Cached LLM extraction of [[raw/sloanslake/indications/samples/cobalt_harbor_email|the Cobalt Harbor email sample]] (matched by content hash when pasted). Set ANTHROPIC_API_KEY to extract live.
> The pipeline re-checks every money figure below against the source text; it never trusts this file alone.

Pipeline code reads the JSON block below. Keep it valid JSON.

```json
{
  "carrier": "Cobalt Harbor Insurance",
  "document_date": "2026-10-28",
  "reference": "CHI-26-7731",
  "firmness": "written",
  "supersedes": null,
  "basis_revenue": 2350000,
  "expires_on": "2026-11-27",
  "specimen_form": "CHI-CYBR-2025",
  "bi_waiting_period_hours": 12,
  "conditions": [
    "MFA required on email",
    "Annual phishing training for all staff"
  ],
  "options": [
    {
      "limit": 1000000,
      "deductible": 10000,
      "status": "indicated",
      "premium": 3340,
      "sublimits": {
        "social_engineering": 50000,
        "ransomware": "full limit"
      },
      "quote": "$1,000,000 limit / $10,000 retention: $3,340 annual"
    },
    {
      "limit": 2000000,
      "deductible": 25000,
      "status": "indicated",
      "premium": 5290,
      "sublimits": {
        "social_engineering": 100000,
        "ransomware": "full limit"
      },
      "quote": "$2M limit / $25K retention: 5.29k annual"
    }
  ]
}
```
