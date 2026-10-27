---
type: cached-ai-output
title: "Cached extraction — Cobalt underwriter call (sample)"
format: json-in-markdown
content_sha256: e275ca0673f5f74e1dc7f7330f6915621adcad17e1d181c2e1a4bce723949e2b
---

# Cached extraction — Cobalt underwriter call (sample)

> Cached LLM extraction of [[raw/sloanslake/indications/samples/cobalt_underwriter_call|the Cobalt call sample]], matched by content hash when pasted. Set ANTHROPIC_API_KEY to extract live.

```json
{
  "carrier": "Cobalt Harbor Insurance",
  "document_date": "2026-10-29",
  "reference": null,
  "firmness": "verbal",
  "supersedes": null,
  "basis_revenue": null,
  "expires_on": null,
  "specimen_form": null,
  "bi_waiting_period_hours": null,
  "conditions": [],
  "notes": [
    "Underwriter clarifies the emailed '5.29k' as $5,290 annual"
  ],
  "options": [
    {
      "limit": 1000000,
      "deductible": 10000,
      "status": "indicated",
      "premium": 3340,
      "sublimits": {},
      "hedged": false,
      "note": "Unchanged from the email",
      "quote": "Right, nothing changed there.",
      "ts": "00:27"
    },
    {
      "limit": 2000000,
      "deductible": 25000,
      "status": "indicated",
      "premium": 5290,
      "sublimits": {},
      "hedged": false,
      "note": "Clarifies '5.29k' in the email",
      "quote": "Yes, fifty-two ninety annual for the two million with the twenty-five K retention. Sorry for the shorthand.",
      "ts": "00:16"
    }
  ]
}
```
