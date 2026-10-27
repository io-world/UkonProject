---
type: cached-ai-output
title: "Cached extraction — 2026-12-03_northwind_firm_quote"
format: json-in-markdown
---

# Cached extraction — 2026-12-03_northwind_firm_quote

> Cached LLM extraction of [[raw/sloanslake/quotes/2026-12-03_northwind_firm_quote.pdf|2026-12-03_northwind_firm_quote]]. Set ANTHROPIC_API_KEY to extract live.
> The pipeline re-checks every money figure and date below against the source text; it never trusts this file alone.

Pipeline code reads the JSON block below. Keep it valid JSON.

```json
{
  "carrier": "Northwind Specialty",
  "document_date": "2026-12-03",
  "reference": "NWS-QTE-26-11982",
  "follows_indication": "NWS-IND-26-04417",
  "firmness": "written",
  "basis_revenue": null,
  "expires_on": "2027-01-14",
  "effective_date": "2027-01-15",
  "expiration_date": "2028-01-15",
  "specimen_form": "NWS-CY-100 (06/25)",
  "bi_waiting_period_hours": 8,
  "premium_reason": "Premium reflects the signed application dated December 1, 2026: phishing awareness training is not currently in place, and multi-factor authentication on email is partially deployed.",
  "conditions": [
    "Before binding: written confirmation that MFA is enforced on all email accounts",
    "Before binding: written confirmation that backups are offline or immutable and were restore-tested in the last 12 months",
    "Within 60 days of binding: phishing awareness training completed by all staff, with evidence provided"
  ],
  "options": [
    {
      "limit": 1000000,
      "deductible": 10000,
      "status": "indicated",
      "premium": 3410,
      "sublimits": {"social_engineering": 100000, "ransomware": "full limit"},
      "hedged": false,
      "note": null,
      "quote": "$1,000,000 $10,000 $3,410 $100,000 Full limit"
    }
  ]
}
```
