---
type: cached-ai-output
title: "Cached extraction — intake call 2"
format: json-in-markdown
---

# Cached extraction — intake call 2

> Cached LLM extraction of [[raw/sloanslake/call_2_followup|call_2_followup]]. Set ANTHROPIC_API_KEY to extract live.

Pipeline code reads the JSON block below. Edit values here and re-run the pipeline; keep it valid JSON.

```json
{
  "intake": [
    {
      "key": "q14",
      "answer": "Phone codes on for every email account now, including the hygienists; remote access already had them",
      "normalized": "option",
      "value": [
        "Email",
        "Remote access"
      ],
      "quote": "Yes. Peak Tech turned on the phone codes for all three hygienists on Monday, so it's everyone now.",
      "ts": "00:13"
    },
    {
      "key": "q15",
      "answer": "Endpoint detection and response on all computers, monitored by the IT provider; no word on a written plan",
      "normalized": "option",
      "value": [
        "Endpoint detection"
      ],
      "quote": "They confirmed it's endpoint detection and response, on all nine computers, and they watch the alerts.",
      "ts": "00:25"
    },
    {
      "key": "q4",
      "answer": "Nightly cloud backups; a restore has still never been tested (test scheduled next month)",
      "normalized": "option",
      "value": "Backups, never tested",
      "quote": "Not yet. They've scheduled a restore test for next month.",
      "ts": "00:37"
    }
  ],
  "application": [
    {
      "key": "mfa_email",
      "answer": "Yes — phone codes now on for every account, including the three hygienists",
      "normalized": "yes",
      "quote": "Yes. Peak Tech turned on the phone codes for all three hygienists on Monday, so it's everyone now.",
      "ts": "00:13"
    },
    {
      "key": "edr",
      "answer": "Yes — endpoint detection and response on all computers, monitored by the IT provider",
      "normalized": "yes",
      "quote": "They confirmed it's endpoint detection and response, on all nine computers, and they watch the alerts.",
      "ts": "00:25"
    },
    {
      "key": "backups",
      "answer": "Restore still not tested; test scheduled next month",
      "normalized": "partial",
      "quote": "Not yet. They've scheduled a restore test for next month.",
      "ts": "00:37"
    }
  ],
  "coverage_questions": []
}
```
