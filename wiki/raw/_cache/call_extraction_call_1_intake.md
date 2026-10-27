---
type: cached-ai-output
title: "Cached extraction — intake call 1"
format: json-in-markdown
---

# Cached extraction — intake call 1

> Cached LLM extraction of [[raw/quillfeather/call_1_intake|call_1_intake]]. Set ANTHROPIC_API_KEY to extract live.

Pipeline code reads the JSON block below. Edit values here and re-run the pipeline; keep it valid JSON.

```json
{
  "intake": [
    {
      "key": "legal",
      "answer": "Confirmed; also known as Quillfeather Dental",
      "normalized": "confirmed",
      "value": null,
      "quote": "Yes, that's us. Everyone just calls us Quillfeather Dental.",
      "ts": "00:19"
    },
    {
      "key": "domain",
      "answer": "Confirmed, only domain",
      "normalized": "confirmed",
      "value": null,
      "quote": "Just that one.",
      "ts": "00:29"
    },
    {
      "key": "industry",
      "answer": "Confirmed, general dentistry; lab work is sent out",
      "normalized": "confirmed",
      "value": null,
      "quote": "Right, general dentistry. We send lab work out.",
      "ts": "00:36"
    },
    {
      "key": "revenue",
      "answer": "Closer to $2.1M last year; added a full-time dentist in the spring",
      "normalized": "corrected",
      "value": 2100000,
      "quote": "It was a little higher, closer to two point one. We added Dr. Reyes full time in the spring.",
      "ts": "00:46"
    },
    {
      "key": "address",
      "answer": "Confirmed, one office",
      "normalized": "confirmed",
      "value": null,
      "quote": "Yes, just the one office.",
      "ts": "00:59"
    },
    {
      "key": "q1",
      "answer": "Almost all Colorado; a handful from Wyoming",
      "normalized": "value",
      "value": "Colorado; a few from Wyoming",
      "quote": "Almost all Colorado. A handful drive down from Wyoming.",
      "ts": "01:07"
    },
    {
      "key": "q2",
      "answer": "About 80–85% stops; emergencies possible on paper",
      "normalized": "option",
      "value": "Over 75%",
      "quote": "I'd say eighty, eighty-five percent stops.",
      "ts": "01:19"
    },
    {
      "key": "q3",
      "answer": "A day or two before patients rebook elsewhere",
      "normalized": "option",
      "value": "1–3 days",
      "quote": "A day or two. After that people rebook somewhere else.",
      "ts": "01:35"
    },
    {
      "key": "q4",
      "answer": "Nightly cloud backups by Peak Tech; restore never tested",
      "normalized": "option",
      "value": "Backups, never tested",
      "quote": "Our IT company, Peak Tech, backs up every night to the cloud. I don't think we've ever actually tested a restore.",
      "ts": "01:46"
    },
    {
      "key": "q5",
      "answer": "Four critical systems (five counting phones)",
      "normalized": "value",
      "value": 4,
      "quote": "So four. Five if you count the phones.",
      "ts": "02:02"
    },
    {
      "key": "q6",
      "answer": "Cloud charting system (~100% of revenue); insurance clearinghouse (~70% of collections)",
      "normalized": "value",
      "value": "Cloud charting system, about 100%; insurance claims clearinghouse, about 70%",
      "quote": "The cloud charting system. If that's down, we're basically closed, so call it all of our revenue. And the clearinghouse for insurance claims, that's maybe seventy percent of what we collect.",
      "ts": "02:18"
    },
    {
      "key": "q7",
      "answer": "About 3,200 active, about 9,000 all-time",
      "normalized": "option",
      "value": "Under 10K",
      "quote": "Active, maybe thirty-two hundred. All-time in the system, probably nine thousand or so.",
      "ts": "02:37"
    },
    {
      "key": "q8",
      "answer": "HIPAA yes; California residents unknown",
      "normalized": "option",
      "value": [
        "HIPAA health data"
      ],
      "quote": "HIPAA, yes. California, I'm not sure. Maybe a few people who moved?",
      "ts": "02:51"
    },
    {
      "key": "q9",
      "answer": "Doesn't know; would check with Peak Tech",
      "normalized": "option",
      "value": "Don’t know",
      "quote": "I'd have to check with Peak Tech.",
      "ts": "03:02"
    },
    {
      "key": "q10",
      "answer": "Yes, front desk and online; about 6,000 a year",
      "normalized": "option",
      "value": "Under 20K a year",
      "quote": "Yes, at the front desk and online. Maybe six thousand a year.",
      "ts": "03:10"
    },
    {
      "key": "q11",
      "answer": "Terminal company handles card numbers",
      "normalized": "option",
      "value": "Processor handles them",
      "quote": "The terminal company handles all of it. We never see the full numbers.",
      "ts": "03:20"
    },
    {
      "key": "q12",
      "answer": "About $40,000 a month to the dental supplier",
      "normalized": "value",
      "value": "About $40,000 a month (dental supply order)",
      "quote": "Our dental supply order, around forty thousand a month.",
      "ts": "03:30"
    },
    {
      "key": "q13",
      "answer": "Always; office manager calls back",
      "normalized": "option",
      "value": "Always",
      "quote": "Yes. Rosa always calls. We almost got burned on a lab invoice two years ago, so that's a hard rule now.",
      "ts": "03:42"
    },
    {
      "key": "q14",
      "answer": "Email MFA for owner and front desk, unsure for hygienists; remote desktop has MFA",
      "normalized": "option",
      "value": [
        "Email",
        "Remote access"
      ],
      "quote": "Mostly. I do, and the front desk does. I'm honestly not sure about the hygienists' accounts. Remote desktop for me and Rosa has the phone code.",
      "ts": "03:57"
    },
    {
      "key": "q15",
      "answer": "Believes EDR was installed; no written plan",
      "normalized": "option",
      "value": [
        "Endpoint detection"
      ],
      "quote": "I believe Peak Tech installed something last year. A written plan, no.",
      "ts": "04:15"
    },
    {
      "key": "q16",
      "answer": "No incidents; one attempted invoice fraud caught before payment",
      "normalized": "option",
      "value": "No",
      "quote": "No. Just that lab invoice scare, but we caught it before any money went out.",
      "ts": "04:25"
    },
    {
      "key": "q19",
      "answer": "No formal training",
      "normalized": "option",
      "value": "No",
      "quote": "Not formal training, no.",
      "ts": "04:36"
    },
    {
      "key": "q20",
      "answer": "Peak Tech Solutions, outside company",
      "normalized": "value",
      "value": "Peak Tech Solutions (outside)",
      "quote": "Peak Tech Solutions, outside company.",
      "ts": "04:42"
    },
    {
      "key": "q17",
      "answer": null,
      "normalized": "unknown",
      "value": null,
      "quote": "",
      "ts": null
    },
    {
      "key": "q18",
      "answer": "No known contract minimum",
      "normalized": "no",
      "value": null,
      "quote": "Not that I know of.",
      "ts": "04:52"
    },
    {
      "key": "check_f1",
      "answer": "Could be longer, since backups were never tested",
      "normalized": "value",
      "value": "Could be longer; backups never tested",
      "quote": "Honestly, with backups we've never tested, it could be longer.",
      "ts": "05:06"
    },
    {
      "key": "check_f6",
      "answer": "About 9,000 records is right",
      "normalized": "value",
      "value": "About 9,000 is right",
      "quote": "Yes, nine thousand is about right.",
      "ts": "05:17"
    },
    {
      "key": "check_f7",
      "answer": null,
      "normalized": "unknown",
      "value": null,
      "quote": "",
      "ts": null
    },
    {
      "key": "check_roll",
      "answer": "Fits; downtime is the main worry",
      "normalized": "value",
      "value": "Fits; downtime is the main worry",
      "quote": "No, that all makes sense. The downtime part is the one that worries me.",
      "ts": "05:30"
    }
  ],
  "application": [
    {
      "key": "revenue",
      "answer": "Closer to $2.1M last year",
      "normalized": "value",
      "value": 2100000,
      "quote": "It was a little higher, closer to two point one. We added Dr. Reyes full time in the spring.",
      "ts": "00:46"
    },
    {
      "key": "records",
      "answer": "About 9,000 all-time records",
      "normalized": "value",
      "value": 9000,
      "quote": "Active, maybe thirty-two hundred. All-time in the system, probably nine thousand or so.",
      "ts": "02:37"
    },
    {
      "key": "mfa_email",
      "answer": "Owner and front desk yes; hygienists unknown",
      "normalized": "partial",
      "value": null,
      "quote": "Mostly. I do, and the front desk does. I'm honestly not sure about the hygienists' accounts.",
      "ts": "03:57"
    },
    {
      "key": "mfa_remote",
      "answer": "Yes, remote desktop requires MFA",
      "normalized": "yes",
      "value": null,
      "quote": "Remote desktop for me and Rosa has the phone code.",
      "ts": "03:57"
    },
    {
      "key": "backups",
      "answer": "Nightly cloud backups; never tested",
      "normalized": "partial",
      "value": null,
      "quote": "Our IT company, Peak Tech, backs up every night to the cloud. I don't think we've ever actually tested a restore.",
      "ts": "01:46"
    },
    {
      "key": "edr",
      "answer": "Believes EDR was installed",
      "normalized": "yes",
      "value": null,
      "quote": "I believe Peak Tech installed something last year.",
      "ts": "04:15"
    },
    {
      "key": "payment_verify",
      "answer": "Yes, always called back",
      "normalized": "yes",
      "value": null,
      "quote": "Yes. Rosa always calls.",
      "ts": "03:42"
    },
    {
      "key": "phishing_training",
      "answer": "No formal training",
      "normalized": "no",
      "value": null,
      "quote": "Not formal training, no.",
      "ts": "04:36"
    },
    {
      "key": "prior_incidents",
      "answer": "No incidents; attempted invoice fraud caught",
      "normalized": "no",
      "value": null,
      "quote": "No. Just that lab invoice scare, but we caught it before any money went out.",
      "ts": "04:25"
    },
    {
      "key": "it_provider",
      "answer": "Outsourced: Peak Tech Solutions",
      "normalized": "value",
      "value": "Peak Tech Solutions (outsourced)",
      "quote": "Peak Tech Solutions, outside company.",
      "ts": "04:42"
    }
  ],
  "coverage_questions": [
    {
      "quote": "Would a breach that starts at Peak Tech be covered?",
      "ts": "05:30"
    }
  ]
}
```
