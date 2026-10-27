---
type: carrier-reference
title: "Approved plain-language coverage library"
format: json-in-markdown
---

# Approved plain-language coverage library

> Approved plain-language coverage descriptions (CPL-reviewed library). The report uses these verbatim; the LLM does not write coverage descriptions. Reading level target: grades 6-8.

Pipeline code reads the JSON block below. Edit values here and re-run the pipeline; keep it valid JSON.

```json
{
  "covered": [
    {
      "key": "breach_response",
      "title": "Cleaning up after a breach",
      "plain": "Pays for experts to find out what happened, letters to affected patients, credit monitoring, and a call center for their questions."
    },
    {
      "key": "ransomware",
      "title": "Ransomware and extortion",
      "plain": "Pays specialists to deal with criminals who lock your systems, and in many cases the ransom itself if paying is the right call. Check the limit on your option."
    },
    {
      "key": "business_interruption",
      "title": "Lost income while you're down",
      "plain": "Replaces income you lose while your systems are down, after a short waiting period of hours."
    },
    {
      "key": "funds_transfer_fraud",
      "title": "Tricked into sending money",
      "plain": "Covers money sent to a criminal after a fake email or invoice. This usually has a smaller limit than the rest of the policy — see your option.",
      "flag_sublimit": true
    },
    {
      "key": "privacy_liability",
      "title": "Lawsuits from patients",
      "plain": "Pays legal defense and settlements if patients sue over their exposed information."
    },
    {
      "key": "regulatory",
      "title": "Regulator investigations",
      "plain": "Helps with costs from a health-privacy regulator investigation, including some fines where the law allows insurance to pay them."
    }
  ],
  "not_covered": [
    "Upgrading your computers or security after an incident (betterment)",
    "Incidents you knew about before the policy started",
    "Property damage or bodily injury",
    "Lost future value of the practice"
  ],
  "disclaimer": "These are estimates from insurance companies, not final quotes. The final price and terms are confirmed after you complete an application. Coverage is described in plain language here; the policy itself is what governs."
}
```
