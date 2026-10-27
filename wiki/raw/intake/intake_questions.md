---
type: raw-source
title: "Client intake question bank"
format: json-in-markdown
---

# Client intake question bank

> The questions an agent reads on the intake call, in order. One list drives the app's Intake →
> Live call screen, call extraction (`pipeline/intake.py`) and the completed intake page.
> Keys are stable: never rename one, add a new key instead.

- `ref` is what the agent says aloud ("Question 7") so extraction can anchor on it.
- `prefill_from` names a database field Stage 1 already filled; the agent confirms it on the call.
- `app_keys` lists the [[raw/carriers/application_questions|application questions]] this item
  answers, so one call fills both the intake and the application.
- `hint`, `signal`, `ph`, `excl` are screen copy: a tip for the agent, what enrichment already
  suggests, an input placeholder, and options that clear the others in a multi-select.
- `walkthrough` items record the client's reaction to the limit walkthrough. They never hold a
  dollar figure.

Pipeline code reads the JSON block below. Keep it valid JSON.

```json
{
  "items": [
    {
      "key": "legal",
      "ref": "0.1",
      "section": "identity",
      "label": "Business legal name",
      "type": "text",
      "prefill_from": "legal_name",
      "app_keys": [
        "legal_name"
      ],
      "plain": "Is “Sage Dentistry, PLLC” your exact legal name? Do you trade under any other names?"
    },
    {
      "key": "domain",
      "ref": "0.2",
      "section": "identity",
      "label": "Website / domain",
      "type": "text",
      "prefill_from": "domain",
      "app_keys": [],
      "plain": "Is sloanslakedental.com your only website? Do you use any other domains for email?"
    },
    {
      "key": "industry",
      "ref": "0.3",
      "section": "identity",
      "label": "Industry",
      "type": "text",
      "prefill_from": "industry",
      "app_keys": [],
      "plain": "You run a general dental practice, is that right? Anything else under the same business, like a lab?"
    },
    {
      "key": "revenue",
      "ref": "0.4",
      "section": "identity",
      "label": "Annual revenue",
      "type": "number",
      "prefill_from": "annual_revenue",
      "app_keys": [
        "revenue"
      ],
      "plain": "We estimated annual revenue at about $2.35 million. Is that in the right range?"
    },
    {
      "key": "address",
      "ref": "0.5",
      "section": "identity",
      "label": "State / business address",
      "type": "text",
      "prefill_from": "address",
      "app_keys": [],
      "plain": "Is 2750 W 29th Ave still your only location?"
    },
    {
      "key": "q1",
      "ref": "Q1",
      "section": "exposure",
      "group": "Where patients are",
      "label": "Patient locations",
      "type": "text",
      "app_keys": [],
      "plain": "Which states or countries are your patients in?",
      "ph": "e.g. Colorado, a few in Wyoming",
      "hint": "Privacy law follows where the patient lives, not the office address.",
      "signal": "Office is in Colorado. Out-of-state patients are unknown."
    },
    {
      "key": "q2",
      "ref": "Q2",
      "section": "exposure",
      "group": "Downtime",
      "label": "Share of practice that stops",
      "type": "single",
      "options": [
        "Under 25%",
        "25–50%",
        "50–75%",
        "Over 75%"
      ],
      "top": true,
      "app_keys": [],
      "plain": "If your systems went down tomorrow, what share of the practice would stop completely, and what could keep running on paper?",
      "hint": "The most important question. It sets how much of each day’s profit is lost."
    },
    {
      "key": "q3",
      "ref": "Q3",
      "section": "exposure",
      "group": "Downtime",
      "label": "Time in degraded mode",
      "type": "single",
      "options": [
        "Under 1 day",
        "1–3 days",
        "4–7 days",
        "Over a week"
      ],
      "app_keys": [],
      "plain": "How long could you run in that slowed-down mode before losing patients?"
    },
    {
      "key": "q4",
      "ref": "Q4",
      "section": "exposure",
      "group": "Downtime",
      "label": "Backups",
      "type": "single",
      "options": [
        "Offline, tested this year",
        "Backups, never tested",
        "Cloud sync only",
        "None or don’t know"
      ],
      "app_keys": [
        "backups"
      ],
      "plain": "Do you have offline backups? When did you last test restoring everything from them?",
      "signal": "Unknown until the call."
    },
    {
      "key": "q5",
      "ref": "Q5",
      "section": "exposure",
      "group": "Downtime",
      "label": "Critical systems",
      "type": "number",
      "app_keys": [],
      "plain": "How many critical systems would need rebuilding? Think servers, practice-management software, imaging, payments.",
      "ph": "e.g. 4"
    },
    {
      "key": "q6",
      "ref": "Q6",
      "section": "exposure",
      "group": "Downtime",
      "label": "Critical vendors",
      "type": "text",
      "app_keys": [],
      "plain": "Which outside vendors would stop the practice if they went down? Roughly what share of revenue depends on each?",
      "ph": "e.g. cloud practice-management system, about 90%"
    },
    {
      "key": "q7",
      "ref": "Q7",
      "section": "exposure",
      "group": "Data held",
      "label": "Records held",
      "type": "single",
      "options": [
        "Under 10K",
        "10K–100K",
        "Over 100K"
      ],
      "top": true,
      "app_keys": [
        "records"
      ],
      "plain": "Roughly how many patient and employee records do you hold with personal info: SSNs, insurance, health or payment details?",
      "hint": "Remind them to include former patients.",
      "signal": "Enrichment estimate: more than 5,000 records."
    },
    {
      "key": "q8",
      "ref": "Q8",
      "section": "exposure",
      "group": "Data held",
      "label": "Regulated data",
      "type": "multi",
      "options": [
        "HIPAA health data",
        "California residents",
        "Neither"
      ],
      "app_keys": [],
      "plain": "Do you hold health data covered by HIPAA, or data on California residents?",
      "excl": [
        "Neither"
      ],
      "signal": "Handles patient health information."
    },
    {
      "key": "q9",
      "ref": "Q9",
      "section": "exposure",
      "group": "Data held",
      "label": "Encryption at rest",
      "type": "single",
      "options": [
        "Yes",
        "No",
        "Don’t know"
      ],
      "app_keys": [],
      "plain": "Is sensitive data encrypted where it’s stored?"
    },
    {
      "key": "q10",
      "ref": "Q10",
      "section": "exposure",
      "group": "Payments",
      "label": "Card volume",
      "type": "single",
      "options": [
        "No cards",
        "Under 20K a year",
        "20K–1M a year",
        "Over 1M a year"
      ],
      "app_keys": [],
      "plain": "Do you accept cards? Roughly how many card transactions a year?",
      "signal": "Takes payments online."
    },
    {
      "key": "q11",
      "ref": "Q11",
      "section": "exposure",
      "group": "Payments",
      "label": "Card storage",
      "type": "single",
      "options": [
        "Processor handles them",
        "We store card numbers",
        "Don’t know"
      ],
      "app_keys": [],
      "plain": "Do you store card numbers anywhere, or does a processor handle them entirely?",
      "hint": "If a processor handles them, formula 10 mostly drops out."
    },
    {
      "key": "q12",
      "ref": "Q12",
      "section": "exposure",
      "group": "Money movement",
      "label": "Largest routine payment",
      "type": "text",
      "top": true,
      "app_keys": [],
      "plain": "What’s the largest single payment or wire you routinely send?",
      "ph": "e.g. $38,000 a month to the dental supplier"
    },
    {
      "key": "q13",
      "ref": "Q13",
      "section": "exposure",
      "group": "Money movement",
      "label": "Payment-change callback",
      "type": "single",
      "options": [
        "Always",
        "Sometimes",
        "No"
      ],
      "app_keys": [
        "payment_verify"
      ],
      "plain": "When a vendor asks to change their bank details, do you call them back on a number you already have?"
    },
    {
      "key": "q14",
      "ref": "Q14",
      "section": "exposure",
      "group": "Security posture",
      "label": "Multi-factor authentication",
      "type": "multi",
      "options": [
        "Email",
        "Remote access",
        "Admin accounts",
        "None",
        "Don’t know"
      ],
      "app_keys": [
        "mfa_email",
        "mfa_remote"
      ],
      "plain": "Is multi-factor authentication turned on for email, remote access and admin accounts?",
      "excl": [
        "None",
        "Don’t know"
      ],
      "signal": "Unknown until the call."
    },
    {
      "key": "q15",
      "ref": "Q15",
      "section": "exposure",
      "group": "Security posture",
      "label": "Detection and response plan",
      "type": "multi",
      "options": [
        "Endpoint detection",
        "Incident response plan",
        "Neither",
        "Don’t know"
      ],
      "app_keys": [
        "edr"
      ],
      "plain": "Do you have endpoint detection software, and a written plan for responding to an incident?",
      "excl": [
        "Neither",
        "Don’t know"
      ]
    },
    {
      "key": "q16",
      "ref": "Q16",
      "section": "exposure",
      "group": "Security posture",
      "label": "Prior incidents",
      "type": "single",
      "options": [
        "No",
        "Yes",
        "Not sure"
      ],
      "app_keys": [
        "prior_incidents"
      ],
      "plain": "Have you had a cyber incident before, even a small one?",
      "hint": "If yes, note what happened and when."
    },
    {
      "key": "q19",
      "ref": "Q19",
      "section": "exposure",
      "group": "Security posture",
      "label": "Phishing training",
      "type": "single",
      "options": [
        "Yes, at least yearly",
        "Informal only",
        "No"
      ],
      "app_keys": [
        "phishing_training"
      ],
      "plain": "Does your team get any training on spotting fake emails, at least once a year?"
    },
    {
      "key": "q20",
      "ref": "Q20",
      "section": "exposure",
      "group": "Security posture",
      "label": "IT provider",
      "type": "text",
      "app_keys": [
        "it_provider"
      ],
      "plain": "Who handles your computers and IT: someone on staff or an outside company?",
      "ph": "e.g. Peak Tech Solutions, outside company"
    },
    {
      "key": "q17",
      "ref": "Q17",
      "section": "exposure",
      "group": "Current coverage",
      "label": "Current cyber policy",
      "type": "text",
      "policy": true,
      "app_keys": [],
      "plain": "Current cyber limit, deductible, waiting period and sublimits. Pull from the policy; ask only if it’s missing.",
      "ph": "e.g. $250K limit, $2,500 deductible, 12-hour waiting period",
      "hint": "Pull these from the policy instead of asking. Only ask if the policy is missing."
    },
    {
      "key": "q18",
      "ref": "Q18",
      "section": "exposure",
      "group": "Current coverage",
      "label": "Contract minimums",
      "type": "text",
      "app_keys": [],
      "plain": "Do any contracts require you to carry a minimum cyber limit?",
      "ph": "e.g. a dental service organization agreement requires $1M"
    },
    {
      "key": "check_f1",
      "ref": "F1",
      "section": "walkthrough",
      "label": "Downtime days realistic?",
      "type": "text",
      "app_keys": [],
      "plain": "Does that many days feel realistic, given your backups?"
    },
    {
      "key": "check_f6",
      "ref": "F6",
      "section": "walkthrough",
      "label": "Record count right?",
      "type": "text",
      "app_keys": [],
      "plain": "Does that record count sound right? Include former patients you still hold records for."
    },
    {
      "key": "check_f7",
      "ref": "F7",
      "section": "walkthrough",
      "label": "Callback before bank changes?",
      "type": "text",
      "app_keys": [],
      "plain": "Do you call to confirm before changing anyone’s bank details?"
    },
    {
      "key": "check_roll",
      "ref": "Roll-up",
      "section": "walkthrough",
      "label": "Anything that doesn’t fit?",
      "type": "text",
      "app_keys": [],
      "plain": "Is there anything here that doesn’t fit how your practice really works?"
    }
  ],
  "groups": [
    {
      "title": "Where patients are",
      "feeds": "Formulas 8, 9"
    },
    {
      "title": "Downtime",
      "feeds": "Formulas 1, 2, 5"
    },
    {
      "title": "Data held",
      "feeds": "Formulas 6, 8, 9"
    },
    {
      "title": "Payments",
      "feeds": "Formula 10"
    },
    {
      "title": "Money movement",
      "feeds": "Formula 7"
    },
    {
      "title": "Security posture",
      "feeds": "Moves results between low, expected and severe"
    },
    {
      "title": "Current coverage",
      "feeds": "Needed for the gap"
    }
  ]
}
```
