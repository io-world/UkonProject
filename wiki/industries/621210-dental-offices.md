---
type: industry
naics: "621210"
title: Offices of Dentists
clients:
  - "[[clients/sloanslake|Sloan's Lake Dental]]"
last_updated: 2026-10-25
sources:
  - "[[raw/benchmarks/dental_industry_benchmarks]]"
  - "[[raw/benchmarks/claims_benchmarks]]"
  - "[[raw/benchmarks/cyber_premium_benchmarks]]"
---

# Offices of Dentists (NAICS 621210)

Shared industry page. Every dental client's report and agent brief draws on this page,
so each debrief logged by an agent makes the next dental proposal better.

## Why cyber matters for dental offices

- They hold **protected health information** (PHI) plus payment and insurance data, which
  makes them a breach-notification and regulatory exposure under HIPAA.
- They run on a single practice-management system. If it's locked, scheduling, charting, and
  billing all stop. Downtime is lost revenue by the hour.
- Small front-office teams handle lab, supply, and insurance payments by email, which is the
  setup business email compromise (BEC) targets.
- Healthcare is consistently a top-5 affected SME sector in cyber claims data. [[raw/benchmarks/claims_benchmarks|benchmarks/claims_benchmarks]]

## Scenario library (plain language; figures pulled from the DB, not written here)

1. **Locked out of the schedule.** Ransomware encrypts the practice-management system on a
   Monday morning. Patients are turned away while IT restores from backup.
   *Benchmark field:* `scenario.ransomware_incident_cost`
2. **The fake lab invoice.** An email that looks like the dental lab asks to update bank
   details. A payment goes to a criminal's account.
   *Benchmark field:* `scenario.bec_claim_cost`
3. **The breach letter.** Patient records are exposed. The practice has to notify patients,
   offer credit monitoring, and answer to regulators.
   *Benchmark field:* `scenario.sme_incident_cost`

## Limit guidance (benchmarks, not advice)

- About 80% of dental offices carry a $1M cyber limit; a common floor is ~2× monthly revenue. [[raw/benchmarks/dental_industry_benchmarks|benchmarks/dental_industry_benchmarks]]

## Objection library (CPL-approved answers — AI selects and tailors, does not invent)

| Objection | Approved answer (tailor names/numbers from DB only) |
|---|---|
| "We're too small to be a target." | Most cyber claims come from small and mid-sized businesses. Attacks are automated; they look for weak email setups, not big names. |
| "My IT company handles security." | Good IT lowers the chance of an attack; insurance pays for what happens when one gets through anyway: forensics, notification letters, lost income, legal costs. IT providers don't cover those. |
| "It's too expensive." | Compare the annual premium to one day of the office being closed. The recommended option is about the cost of [premium ÷ 12] a month. |
| "We've never been hacked." | Many practices find out from a patient or their bank. Also: the carrier will ask about near misses (like a fake invoice), and those count as experience, not a strike. |
| "Doesn't my BOP / malpractice cover this?" | **Escalate to CPL** if they name a specific endorsement. General answer: most business and malpractice policies exclude cyber or include only a small add-on limit. |

## Escalation triggers (route to Cyber Practice Leader)

- Any question about whether a specific situation would be covered.
- Comparing this policy's wording to an existing endorsement.
- HIPAA fine coverage questions specific to a state or regulator action.

## Application gates seen across carriers

- MFA on email and remote access (all three indicated carriers)
- Offline/immutable, tested backups
- EDR on endpoints (Ridgeline Mutual)
