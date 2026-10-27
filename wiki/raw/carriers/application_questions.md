---
type: carrier-reference
title: "Cyber application question bank"
format: json-in-markdown
---

# Cyber application question bank

> Representative cyber application question bank (union across the three fictional carriers). 'plain' is how the agent asks it on the call. 'prefill_from' names a DB field that can answer it without asking.

Pipeline code reads the JSON block below. Edit values here and re-run the pipeline; keep it valid JSON.

```json
{
  "questions": [
    {
      "key": "legal_name",
      "formal": "Applicant legal name",
      "plain": "(prefilled)",
      "prefill_from": "legal_name"
    },
    {
      "key": "revenue",
      "formal": "Gross annual revenue, most recent fiscal year",
      "plain": "(prefilled — confirm on the call)",
      "prefill_from": "annual_revenue",
      "confirm_on_call": true
    },
    {
      "key": "records",
      "formal": "Approximate number of unique individuals' PII/PHI records held",
      "plain": "Roughly how many patients do you have on file, including past patients?",
      "prefill_from": null
    },
    {
      "key": "mfa_email",
      "formal": "Is MFA enforced for all email accounts?",
      "plain": "When your team logs into email, do they need a code from their phone too — every person, every time?",
      "prefill_from": null,
      "gate": true
    },
    {
      "key": "mfa_remote",
      "formal": "Is MFA enforced for all remote access to the network?",
      "plain": "If anyone works from home or logs in remotely, do they need that phone code too?",
      "prefill_from": null,
      "gate": true
    },
    {
      "key": "backups",
      "formal": "Are backups performed at least weekly, stored offline or immutable, and tested?",
      "plain": "Do you back up your patient system at least weekly, kept somewhere a hacker couldn't reach, and have you ever tested restoring it?",
      "prefill_from": null,
      "gate": true
    },
    {
      "key": "edr",
      "formal": "Is endpoint detection and response (EDR) deployed on all endpoints?",
      "plain": "Does your IT provider run security software on every computer that watches for attacks — not just regular antivirus?",
      "prefill_from": null
    },
    {
      "key": "payment_verify",
      "formal": "Are requests to change vendor/bank payment instructions verified out-of-band?",
      "plain": "If a vendor emails asking you to change where you send payment, does someone call them at a known number to confirm?",
      "prefill_from": null
    },
    {
      "key": "phishing_training",
      "formal": "Do employees receive phishing awareness training at least annually?",
      "plain": "Does your team get any training on spotting fake emails, at least once a year?",
      "prefill_from": null
    },
    {
      "key": "prior_incidents",
      "formal": "In the past 5 years, any cyber incidents, breaches, or claims?",
      "plain": "In the last five years, have you had any hacking, ransomware, data breach, or a fraudulent payment?",
      "prefill_from": null,
      "gate": true
    },
    {
      "key": "it_provider",
      "formal": "Is IT managed internally or by an outsourced provider?",
      "plain": "Who handles your computers and IT — someone on staff or an outside company?",
      "prefill_from": null
    }
  ]
}
```
