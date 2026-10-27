# Stage 5 call: questions and limit-sizing script

Used on the Stage 5 call(s) (Present, apply, bind), captured by Wispr Flow, after the owner has seen the pack.
The file keeps its old name; the app and code still call these answers "intake." The
question bank behind it is `wiki/raw/intake/intake_questions.md` and the walkthrough script is
`wiki/raw/intake/walkthrough_script.md`; the agent screen is the app's **Stage 5 (Present, apply, bind) → Live call** view
(the original standalone screen is kept at `docs/archive/client-intake.html`). Say each number aloud
on the call ("Question 7") so the recording can be matched to the list. **[E]** = Stage 1 can usually pre-fill it, so the agent confirms rather than asks.
Offer ranges, not exact numbers, wherever the client is likely to guess.

## Section 0 · Business identity (ask first; enrichment keys off these)

1. Business legal name, plus any "doing business as" names
2. Website / domain(s), all of them
3. Industry (what the business does)
4. Annual revenue
5. State / business address

## Section 1 · Exposure questions

**Where customers are**
1. Which states or countries are your customers in? **[E]** partially. Privacy law follows the
   customer, not the business address.

**Downtime**
2. If your systems went down tomorrow, what share of the business would stop completely, and
   what could keep running manually? *(Most important question on the list.)*
3. How long could you run in that degraded mode before losing customers?
4. Do you have offline or immutable backups, and when did you last test a full restore?
5. How many critical systems would need rebuilding (servers, practice-management or ERP, POS)?
6. Which outside vendors, if they went down, would stop your business? About what share of
   revenue depends on each? **[E]** some are visible from the tech stack

**Data held**
7. Roughly how many customer and employee records hold personal info (SSNs, financial, health,
   logins)? *Under 10K / 10K–100K / over 100K*
8. Do you hold health data (HIPAA) or California residents' data?
9. Is sensitive data encrypted at rest?

**Payments**
10. Do you accept cards? Roughly how many card transactions a year?
11. Do you store card numbers, or does a processor handle them entirely?

**Money movement**
12. What's the largest single payment or wire you routinely send?
13. Do you verify payment-detail changes with a phone call back?

**Security posture** (moves the result between low, expected and severe)
14. Is multi-factor authentication on email, remote access and admin accounts?
15. Do you have endpoint detection software and an incident response plan?
16. Have you had a cyber incident before? **[E]** public breach disclosures
19. Does your team get training on spotting fake emails, at least once a year?
20. Who handles your computers and IT: someone on staff or an outside company?

*(Q19 and Q20 were added so one call also answers every application question. Numbers are stable
keys in `wiki/raw/intake/intake_questions.md`, so they stay out of order rather than renumbering.)*

**Current coverage**
17. Current cyber limit, deductible, waiting period and sublimits (ransomware, social
    engineering, business interruption)? *Pull from the policy rather than asking.*
18. Do any contracts require a minimum cyber limit?

If time is short, get **2, 7 and 12**: they drive most of the dollar output.

## Section 2 · Walking through the numbers (agent–client script)

Purpose: show the client how each number is built from their own answers, so the recommended
limit is something they understand rather than something they're told.

**Rules for the agent**
- Every figure comes from the report, which renders it from the database. `{placeholders}`
  below are filled from there; never quote a number from memory or work one out on the call.
- Present ranges (low / expected / severe), not a single prediction.
- If the client corrects an input, change it in the report. The change is logged with a reason,
  and the numbers update on screen.
- **"Would this be covered?" → don't answer.** Say: *"Good question. I'll get a coverage
  specialist to confirm that in writing."* Escalate to a CPL.

### Opening

> **Agent:** "Before we look at options, I'd like to show you how we got to a recommended limit.
> It's built from what you told us plus industry claims data, and every assumption is on the
> screen. If something looks wrong for your business, tell me and we'll change it together."

### 1 · Downtime (business interruption)

*How it's built:* daily gross profit × days down × share of the business actually stopped,
minus the policy's waiting period.

> **Agent:** "The biggest cost in most cyber claims isn't the hack itself, it's being shut down.
> You told us about {pct_impaired} of the business stops if systems go down, and the typical
> ransomware outage runs around {downtime_days} days. After your {waiting_period}-hour waiting
> period, that's roughly {bi_loss}."
>
> **Check:** "Does {downtime_days} days feel realistic, given your backups?"

*If the client says "we'd be back in a day":* ask when they last tested a full restore. If
never, keep the default and note it.

### 2 · A key vendor going down (dependent business interruption)

*How it's built:* daily gross profit × share of revenue relying on that vendor × days it's out.

> **Agent:** "You mentioned {vendor_name} runs {vendor_dependency_pct} of your operations. If they
> get hit, you lose revenue even though your own systems are fine. That scenario is about
> {dbi_loss}."

*Confidence note for the agent:* little public data supports this one. Say it's an estimate.

### 3 · Ransom payment (extortion)

*How it's built:* published ransom-payment ranges for businesses your size, not a percentage of
revenue.

> **Agent:** "Fewer businesses pay ransoms these days, but when they do, payments for a business
> your size typically fall between {ransom_low} and {ransom_high}. We include it so the policy
> can cover it if paying is ever the right call."

### 4 · Incident response

*How it's built:* average crisis-services cost from insurance claims data for your incident type.

> **Agent:** "If something happens, the policy pays for the experts: forensics, lawyers, and the
> people who restore your systems. For businesses like yours that typically runs {ir_cost}."

### 5 · Restoring systems and data

*How it's built:* critical systems × rebuild hours × hourly rate, plus re-creating lost data.

> **Agent:** "You listed {critical_systems} critical systems. Rebuilding those comes to about
> {restore_cost}."

*Flag:* this rests on assumptions; show them.

### 6 · Notifying customers

*How it's built:* records × (notification cost + credit monitoring × share who take it up).

> **Agent:** "If personal data gets out, the law requires you to notify everyone affected. With
> about {record_count} records, notification and credit monitoring come to roughly
> {notification_cost}."
>
> **Check:** "Does {record_count} sound right? Include former customers or patients you still
> hold records for."

### 7 · Fake payment requests (social engineering)

*How it's built:* largest routine outgoing payment plus a buffer. Usually a separate sublimit.

> **Agent:** "One of the most common claims we see is a fake email asking to change where a
> payment goes. Your largest regular payment is about {largest_payment}, so we'd want at least
> {social_eng_sublimit} for this."
>
> **Check:** "Do you call to confirm before changing anyone's bank details?"

### 8 · Regulators

*How it's built:* records under each law (HIPAA, state privacy laws) × penalty × likelihood of
enforcement.

> **Agent:** "Because you hold {regulated_data_type}, a regulator could investigate after a
> breach. We estimate that exposure at {regulatory_exposure}."

### 9 · Lawsuits from customers

*How it's built:* records × per-person damages (for California, the CCPA's statutory range) ×
likelihood of a suit. Modelled in the low-to-mid range, which is where settlements land.

> **Agent:** "Customers can sue after a breach, and in some states the law sets a dollar amount
> per person. For your records, that's about {litigation_exposure}."

### 10 · Card payments (PCI)

*How it's built:* card records × (reissue cost + fraud assessment) + non-compliance fines.
Skip it if a processor handles card numbers entirely.

> **Agent:** "Because you {card_handling}, a card breach could mean charges from the card brands
> for reissuing cards and covering fraud. That's around {pci_exposure}."

### Rolling it up

Don't add all ten together. A real incident is one of two scenarios:

- **Ransomware:** 1 + 3 + 4 + 5
- **Data breach:** 4 + 6 + 8 + 9 + 10
- **Social engineering:** 7, as its own sublimit

> **Agent:** "Put together, your realistic worst case is a {worst_scenario} event at about
> {scenario_total}, with a severe case near {scenario_severe}. Your current limit is
> {current_limit}. So the question is whether you're comfortable covering the gap of {gap}
> yourself, or whether we should look at {recommended_limit}."
>
> **Check:** "Is there anything here that doesn't fit how your business really works?"

### Closing

> **Agent:** "I'll update the report with any changes you gave me, and you'll see the carrier
> options side by side. The application questions come from what we just covered, so you'll be
> reviewing and signing answers you already gave."

## Notes

- Formulas are calibrated against insurance claims data (NetDiligence), not breach-cost surveys
  (IBM), which run several times higher.
- Defaults that need sourcing before the demo: downtime days, ransom ranges by size, crisis
  services cost, notification and monitoring rates, PCI per-card cost. Cite the source year in
  the report.
