# Client proposal pack (Stage 3; UKON's Stage 2 deliverable)

A **digital HTML report**: rendered from the client wiki, the carrier indications, the owner's answers
so far and the database, adjustable by the agent, frozen when submitted. It never waits on missing answers.

**Where it lives**
- `reports/sloanslake/current.html`: the working draft, rewritten on every change. Open it in any browser.
- `reports/sloanslake/v<N>.html`: written once when version N is submitted; never changes after.
- In the app: the **Stage 3 · Proposal pack** tab, and the "Open HTML report ↗" button (served at
  `/api/clients/sloanslake/report.html`).

## Design principle

A business owner reads in this order: **what does it cost → could this really happen to me →
what do I get → what do I do next.** Lead with price, not education. Grades 6–8 reading level.

## Outline (as built)

1. **At a glance:** business name, one or two sentences on why it matters to *this* business,
   then three options (Essential / Recommended / Premier) with monthly and annual estimated
   premium, limit, deductible, and the funds-transfer ("tricked into sending money") sublimit,
   called out because owners assume it's fully covered. "Most dental offices choose this" marks
   the recommended tier. Many owners will read only this section.
2. **What you've told us so far:** the intake topics (phone codes on email, remote access, tested
   backups, attack monitoring, payment call-backs, phishing training, past incidents), each marked
   In place / Partly in place / Not yet / To confirm. Fixed labels; status comes from the answers.
3. **What could happen to a practice like yours:** three industry-specific stories (ransomware
   lockout, fake lab invoice, breach letter) with a published benchmark cost under each.
4. **Your exposure snapshot:** a Lower / Moderate / Elevated meter and the plain reasons ("13 email
   accounts that could be phished", "email spoofing protection set to none"), plus which controls
   are unknown and would lower the score. Explicitly not a security rating.
5. **Practices like yours, in the news:** real, recent, cited events gathered by AI web research
   (e.g. a Philadelphia practice hit by ransomware, the 2026 dental breach roundup, a billing-vendor
   incident, the proposed HIPAA MFA rule), each with one line on why it matters to this client.
6. **What it pays for:** six coverage areas in plain language from an approved library, plus
   "Not covered" and the business-interruption waiting period.
7. **Common questions:** "We're too small to be a target," "Our IT company handles security."
8. **What happens next:** acknowledges the intake conversation, says the few open items will be
   closed, then final price and signature; lists what the insurer will ask about (MFA, backups) so
   nothing is a surprise at bind.
9. **Footer:** version number, "Not a quote or a binder," disclaimer that these are estimates.

## Where AI helps vs. doesn't

| Part | Source |
|---|---|
| Why it matters, scenario stories, exposure explainer, next steps | AI-written from the wiki; **no digits allowed** (validated) |
| Premiums, limits, deductibles, sublimits | Carrier indications in Postgres, **locked** |
| Scenario costs | Published benchmarks stored as DB fields |
| Coverage descriptions, disclaimer | CPL-approved library, verbatim |
| Tailoring to industry and size | AI, from the client and industry wiki pages |
| Intake status | Intake answers in Postgres, mapped to fixed labels |
| News items | AI web research, stored in the wiki with URL + date, human-reviewed |

## Agent mode vs client mode

- **Agent mode:** sliders for revenue, employees, exposure, records; carrier picker; AI value shown
  next to the current value; "indication needs refresh" banner if revenue drifts beyond ±15%;
  version history.
- **Client mode:** the latest *submitted* version only. No sliders, no "AI thinks."

## Versioning

AI draft → Agent edited → Submitted (locked) → Sent → Superseded. Editing after submit creates a
new version; the sent one never changes. Every slider move records who, when, old → new, and why.

## What could go wrong

| Risk | Catch |
|---|---|
| Implying a binding price | Disclaimer block, "est." labels, footer, "valid until" date |
| Overstating coverage | Library text only; sublimits shown per option |
| A scenario that doesn't fit the business | Scenarios come from the client's industry page |
| Stale price after an agent edit | Drift banner; premiums never recalculated locally |
