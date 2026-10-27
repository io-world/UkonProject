---
type: cached-ai-output
title: "Cached extraction — 2026-10-28_ridgeline_underwriter_call"
format: json-in-markdown
---

# Cached extraction — 2026-10-28_ridgeline_underwriter_call

> Cached LLM extraction of [[raw/quillfeather/indications/2026-10-28_ridgeline_underwriter_call.md|2026-10-28_ridgeline_underwriter_call]]. Set ANTHROPIC_API_KEY to extract live.
> The pipeline re-checks every money figure below against the source text; it never trusts this file alone.

Pipeline code reads the JSON block below. Keep it valid JSON.

```json
{
  "carrier": "Ridgeline Mutual",
  "document_date": "2026-10-28",
  "reference": null,
  "firmness": "verbal",
  "supersedes": null,
  "basis_revenue": null,
  "expires_on": null,
  "specimen_form": null,
  "bi_waiting_period_hours": null,
  "conditions": [
    "MFA required on email",
    "EDR on every machine (underwriter: \"I think\"; to be confirmed in the letter)"
  ],
  "options": [
    {
      "limit": 1000000,
      "deductible": 10000,
      "status": "indicated",
      "premium": 2300,
      "sublimits": {
        "social_engineering": 100000,
        "ransomware": 500000
      },
      "hedged": true,
      "quote": "I'm probably looking at somewhere around twenty-three hundred. Could move a bit once I actually run it.",
      "ts": "00:19"
    },
    {
      "limit": 2000000,
      "deductible": 25000,
      "status": "declined",
      "premium": null,
      "sublimits": {},
      "note": "Underwriter guideline: no $2M for dental offices under 20 employees",
      "quote": "I can't do two mil for a dental office under twenty employees.",
      "ts": "00:43"
    }
  ]
}
```
