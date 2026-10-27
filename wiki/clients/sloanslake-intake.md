---
type: client-intake
generated: true
client: sloanslake
complete: false
calls:
  - raw/sloanslake/call_1_intake
last_rendered: 2026-10-26T20:31:19-06:00
---

# Intake — Sage Dentistry, PLLC

> [!warning] Generated page — do not edit in Obsidian
> Rendered from the database after each call is ingested and whenever an agent confirms an answer
> in the app (logged with their name).

Calls: [[raw/sloanslake/call_1_intake|call_1_intake]] · last extraction: cached · 0 confirmed · 19 ready to confirm · 8 need follow-up · 2 not covered

**Status: draft.** The intake is complete when every identity and exposure item is confirmed by an agent.

## Section 0 · Business identity

### 0.1 · Business legal name
- Asked: Is “Sage Dentistry, PLLC” your exact legal name? Do you trade under any other names?
- Answer: **Sage Dentistry, PLLC** — Confirmed; also known as Sloan's Lake Dental
- Status: `ready to confirm`
- Client said: “Yes, that's the company. Everyone knows us as Sloan's Lake Dental.” ([[raw/sloanslake/call_1_intake|call_1_intake]] 00:19)
- Fills application: legal_name

### 0.2 · Website / domain
- Asked: Is sloanslakedental.com your only website? Do you use any other domains for email?
- Answer: **sloanslakedental.com** — Confirmed, only domain
- Status: `ready to confirm`
- Client said: “Just that one.” ([[raw/sloanslake/call_1_intake|call_1_intake]] 00:29)

### 0.3 · Industry
- Asked: You run a general dental practice, is that right? Anything else under the same business, like a lab?
- Answer: **Offices of Dentists (NAICS 621210)** — Confirmed: general dentistry plus implant and cosmetic work, Botox for TMJ, some in-house 3D printing; one practice
- Status: `ready to confirm`
- Client said: “General, plus a lot of implant and cosmetic work. We do Botox for TMJ, and we 3D print some things in-house, but it's all one practice.” ([[raw/sloanslake/call_1_intake|call_1_intake]] 00:36)

### 0.4 · Annual revenue
- Asked: We estimated annual revenue at about $2.35 million. Is that in the right range?
- Answer: **$2,350,000** — Owner believes revenue is higher than the $2.35M estimate (implant-heavy); exact figure to come from the accountant
- Status: `needs follow-up`
- Client said: “It's higher than that, I'm pretty sure. Implants are a big part of what we do now. I'd want our accountant to give you the real number.” ([[raw/sloanslake/call_1_intake|call_1_intake]] 00:46)
- Not confirmed on the call; still the Stage 1 value.
- Fills application: revenue

### 0.5 · State / business address
- Asked: Is 2750 W 29th Ave still your only location?
- Answer: **2750 W 29th Ave, Denver, CO 80211** — Confirmed, one office; older Sage Dentistry offices closed
- Status: `ready to confirm`
- Client said: “Yes, just this one. We closed the other offices a few years ago.” ([[raw/sloanslake/call_1_intake|call_1_intake]] 00:59)

## Section 1 · Exposure questions

#### Where patients are

### Q1 · Patient locations
- Asked: Which states or countries are your patients in?
- Answer: **Colorado; a few from Wyoming** — Almost all Colorado; a handful from Wyoming
- Status: `ready to confirm`
- Client said: “Almost all Colorado. A handful drive down from Wyoming.” ([[raw/sloanslake/call_1_intake|call_1_intake]] 01:07)

#### Downtime

### Q2 · Share of practice that stops
- Asked: If your systems went down tomorrow, what share of the practice would stop completely, and what could keep running on paper?
- Answer: **Over 75%** — About 80–85% stops; emergencies possible on paper
- Status: `ready to confirm`
- Client said: “I'd say eighty, eighty-five percent stops.” ([[raw/sloanslake/call_1_intake|call_1_intake]] 01:19)

### Q3 · Time in degraded mode
- Asked: How long could you run in that slowed-down mode before losing patients?
- Answer: **1–3 days** — A day or two before patients rebook elsewhere
- Status: `ready to confirm`
- Client said: “A day or two. After that people rebook somewhere else.” ([[raw/sloanslake/call_1_intake|call_1_intake]] 01:35)

### Q4 · Backups
- Asked: Do you have offline backups? When did you last test restoring everything from them?
- Answer: **Backups, never tested** — Nightly cloud backups by Peak Tech; restore never tested
- Status: `needs follow-up`
- Client said: “Our IT company, Peak Tech, backs up every night to the cloud. I don't think we've ever actually tested a restore.” ([[raw/sloanslake/call_1_intake|call_1_intake]] 01:46)
- Client hedged (“I don't think”). Confirm before it goes on the application.
- Fills application: backups

### Q5 · Critical systems
- Asked: How many critical systems would need rebuilding? Think servers, practice-management software, imaging, payments.
- Answer: **4** — Four critical systems (five counting phones)
- Status: `ready to confirm`
- Client said: “So four. Five if you count the phones.” ([[raw/sloanslake/call_1_intake|call_1_intake]] 02:02)

### Q6 · Critical vendors
- Asked: Which outside vendors would stop the practice if they went down? Roughly what share of revenue depends on each?
- Answer: **Cloud charting system, about 100%; insurance claims clearinghouse, about 70%; Adit (online booking and bill pay)** — Cloud charting system (~100% of revenue); insurance clearinghouse (~70% of collections); Adit for online booking and payments
- Status: `ready to confirm`
- Client said: “The cloud charting system. If that's down, we're basically closed, so call it all of our revenue. And the clearinghouse for insurance claims, that's maybe seventy percent of what we collect. Adit too, that's our online booking and payments.” ([[raw/sloanslake/call_1_intake|call_1_intake]] 02:18)

#### Data held

### Q7 · Records held
- Asked: Roughly how many patient and employee records do you hold with personal info: SSNs, insurance, health or payment details?
- Answer: **10K–100K** — About 4,500 active, about 12,000 all-time
- Status: `needs follow-up`
- Client said: “Active, maybe forty-five hundred. All-time in the system, probably twelve thousand or so.” ([[raw/sloanslake/call_1_intake|call_1_intake]] 02:37)
- Client hedged (“probably”). Confirm before it goes on the application.
- Fills application: records

### Q8 · Regulated data
- Asked: Do you hold health data covered by HIPAA, or data on California residents?
- Answer: **HIPAA health data** — HIPAA yes; California residents unknown
- Status: `needs follow-up`
- Client said: “HIPAA, yes. California, I'm not sure. Maybe a few people who moved?” ([[raw/sloanslake/call_1_intake|call_1_intake]] 02:51)
- Client hedged (“not sure”). Confirm before it goes on the application.

### Q9 · Encryption at rest
- Asked: Is sensitive data encrypted where it’s stored?
- Answer: **Don’t know** — Email encrypted through Paubox; stored data unknown, would check with Peak Tech
- Status: `needs follow-up`
- Client said: “Our email goes through Paubox, so that's encrypted. The server, I'd have to check with Peak Tech.” ([[raw/sloanslake/call_1_intake|call_1_intake]] 03:02)
- Client hedged (“I'd have to check”). Confirm before it goes on the application.

#### Payments

### Q10 · Card volume
- Asked: Do you accept cards? Roughly how many card transactions a year?
- Answer: **Under 20K a year** — Yes, front desk and online (Adit); about 8,000 a year
- Status: `ready to confirm`
- Client said: “Yes, at the front desk and online through Adit. Maybe eight thousand a year.” ([[raw/sloanslake/call_1_intake|call_1_intake]] 03:10)

### Q11 · Card storage
- Asked: Do you store card numbers anywhere, or does a processor handle them entirely?
- Answer: **Processor handles them** — Terminal company handles card numbers
- Status: `ready to confirm`
- Client said: “The terminal company handles all of it. We never see the full numbers.” ([[raw/sloanslake/call_1_intake|call_1_intake]] 03:20)

#### Money movement

### Q12 · Largest routine payment
- Asked: What’s the largest single payment or wire you routinely send?
- Answer: **About $60,000 a month (implant lab and supplies)** — About $60,000 a month to the implant lab and suppliers
- Status: `ready to confirm`
- Client said: “The implant lab and supply orders, around sixty thousand a month.” ([[raw/sloanslake/call_1_intake|call_1_intake]] 03:30)

### Q13 · Payment-change callback
- Asked: When a vendor asks to change their bank details, do you call them back on a number you already have?
- Answer: **Always** — Always; office manager calls back
- Status: `ready to confirm`
- Client said: “Yes. Our office manager always calls. We almost got burned on a lab invoice two years ago, so that's a hard rule now.” ([[raw/sloanslake/call_1_intake|call_1_intake]] 03:42)
- Fills application: payment_verify

#### Security posture

### Q14 · Multi-factor authentication
- Asked: Is multi-factor authentication turned on for email, remote access and admin accounts?
- Answer: **Email, Remote access** — Email MFA for owner and front desk, unsure for hygienists; remote desktop has MFA
- Status: `needs follow-up`
- Client said: “Mostly. I do, and the front desk does. I'm honestly not sure about the hygienists' accounts. Remote desktop for me and the office manager has the phone code.” ([[raw/sloanslake/call_1_intake|call_1_intake]] 03:57)
- Client hedged (“Mostly”). Confirm before it goes on the application.
- Fills application: mfa_email, mfa_remote

### Q15 · Detection and response plan
- Asked: Do you have endpoint detection software, and a written plan for responding to an incident?
- Answer: **Endpoint detection** — Believes EDR was installed; no written plan
- Status: `needs follow-up`
- Client said: “I believe Peak Tech installed something last year. A written plan, no.” ([[raw/sloanslake/call_1_intake|call_1_intake]] 04:15)
- Client hedged (“I believe”). Confirm before it goes on the application.
- Fills application: edr

### Q16 · Prior incidents
- Asked: Have you had a cyber incident before, even a small one?
- Answer: **No** — No incidents; one attempted invoice fraud caught before payment
- Status: `ready to confirm`
- Client said: “No. Just that lab invoice scare, but we caught it before any money went out.” ([[raw/sloanslake/call_1_intake|call_1_intake]] 04:25)
- Fills application: prior_incidents

### Q19 · Phishing training
- Asked: Does your team get any training on spotting fake emails, at least once a year?
- Answer: **No** — No formal training
- Status: `ready to confirm`
- Client said: “Not formal training, no.” ([[raw/sloanslake/call_1_intake|call_1_intake]] 04:36)
- Fills application: phishing_training

### Q20 · IT provider
- Asked: Who handles your computers and IT: someone on staff or an outside company?
- Answer: **Peak Tech Solutions (outside)** — Peak Tech Solutions, outside company
- Status: `ready to confirm`
- Client said: “Peak Tech Solutions, outside company.” ([[raw/sloanslake/call_1_intake|call_1_intake]] 04:42)
- Fills application: it_provider

#### Current coverage

### Q17 · Current cyber policy
- Asked: Current cyber limit, deductible, waiting period and sublimits. Pull from the policy; ask only if it’s missing.
- Answer: **—**
- Status: `not covered on the call`
- Pull from the current policy.

### Q18 · Contract minimums
- Asked: Do any contracts require you to carry a minimum cyber limit?
- Answer: **No known contract minimum**
- Status: `needs follow-up`
- Client said: “Not that I know of.” ([[raw/sloanslake/call_1_intake|call_1_intake]] 04:52)
- Client hedged (“Not that I know of”). Confirm before it goes on the application.

## Section 2 · Walkthrough reactions

What the client said about the numbers. Figures themselves live in the report.

### F1 · Downtime days realistic?
- Asked: Does that many days feel realistic, given your backups?
- Answer: **Could be longer; backups never tested** — Could be longer, since backups were never tested
- Status: `ready to confirm`
- Client said: “Honestly, with backups we've never tested, it could be longer.” ([[raw/sloanslake/call_1_intake|call_1_intake]] 05:06)

### F6 · Record count right?
- Asked: Does that record count sound right? Include former patients you still hold records for.
- Answer: **About 12,000 is right** — About 12,000 records is right
- Status: `ready to confirm`
- Client said: “Yes, twelve thousand is about right.” ([[raw/sloanslake/call_1_intake|call_1_intake]] 05:17)

### F7 · Callback before bank changes?
- Asked: Do you call to confirm before changing anyone’s bank details?
- Answer: **—**
- Status: `not asked`

### Roll-up · Anything that doesn’t fit?
- Asked: Is there anything here that doesn’t fit how your practice really works?
- Answer: **Fits; downtime is the main worry**
- Status: `ready to confirm`
- Client said: “No, that all makes sense. The downtime part is the one that worries me.” ([[raw/sloanslake/call_1_intake|call_1_intake]] 05:30)

## Coverage questions for a CPL

Not answered on the call. Escalate to a licensed coverage specialist for a written answer.

- “Would a breach that starts at Peak Tech be covered?” ([[raw/sloanslake/call_1_intake|call_1_intake]] 05:30)

## Application coverage

| Application question | Status | From |
|---|---|---|
| Applicant legal name | ready to confirm | 0.1 |
| Gross annual revenue, most recent fiscal year | needs follow-up | 0.4 |
| Approximate number of unique individuals' PII/PHI records held | ready to confirm | Q7 |
| Is MFA enforced for all email accounts? | needs follow-up | Q14 |
| Is MFA enforced for all remote access to the network? | ready to confirm | Q14 |
| Are backups performed at least weekly, stored offline or immutable, and tested? | needs follow-up | Q4 |
| Is endpoint detection and response (EDR) deployed on all endpoints? | needs follow-up | Q15 |
| Are requests to change vendor/bank payment instructions verified out-of-band? | ready to confirm | Q13 |
| Do employees receive phishing awareness training at least annually? | ready to confirm | Q19 |
| In the past 5 years, any cyber incidents, breaches, or claims? | ready to confirm | Q16 |
| Is IT managed internally or by an outsourced provider? | ready to confirm | Q20 |
