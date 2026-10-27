# Assumptions, success metrics, risks, open questions

Raw material for the 1–2 page write-up.

## Key assumptions

- Agencies can export renewals and client records from their AMS (name, address, email domain,
  line-of-business details, workers' comp headcount/payroll).
- Carriers will price an indication from the five fields; some may accept a **revenue band**.
- Indications arrive through a mix of carrier APIs, portals and email (unknown; see questions).
- A licensed producer presents and advises; AI drafts and explains, never advises on coverage
  (licensing / E&O boundary).
- Business owners will do a 10-minute call or answer a short link, but won't read a long form.
- Headcount stands in for FTEs and email accounts until confirmed on the call.
- Prototype-specific: the 2022 Census/BLS revenue-per-employee figure is used without inflation
  adjustment (conservative). The $500K and $2M premium ratios to the $1M tier are assumptions
  (see `wiki/raw/benchmarks/cyber_premium_benchmarks.md`).

## How to measure success

- **North star:** agent minutes per bound cyber policy.
- **Funnel:** % of renewals made indication-ready → % presented → % applied → % bound,
  all within the renewal window.
- **Quality:** field-level accuracy against a golden set; how often low-confidence flags were
  actually wrong; override rate per field (from the audit trail).
- **Speed:** time from "renewal identified" to "indications back."
- **Trust:** agent adoption (weekly active producers), CPL escalation rate, client questions per report.

## Biggest risks

| Area | Risk | Mitigation in the design |
|---|---|---|
| AI accuracy | Wrong company, wrong revenue, wrong domain → wrong price | Multi-attribute entity scoring + human confirm; revenue waterfall with two methods and ranges; review by exception; overrides logged as training signal |
| AI accuracy | Model invents a figure in client material | No digits allowed in AI prose; all figures from the DB |
| Compliance | Implying a binding price; overstating coverage | Disclaimers, approved coverage library, locked carrier numbers, "not a quote" footer |
| Compliance | Application misrepresentation | Hedge check, agent confirmation, client e-signature |
| Compliance | Call recording without consent | Disclosure at call start; transcript not usable without it |
| Data privacy | Sole-prop addresses are home addresses; insurance data under GLBA and state insurance data-security laws; scraping terms of service | Agency-scoped access; license firmographic data rather than scrape; transcripts stored as client records |
| Adoption | Agents see it as more work | Review by exception; UKON CPLs/ops absorb review; renewal queue does the prioritizing |

## Open questions (for interviews)

Rule: only ask what only UKON can answer. In order (A workflow today, B after bind, C why the window is missed). Sources for #2 and #11 are on `web/public/interview/1-interview-plan.html`.

1. **Matt (CEO)** [C] You wrote that the renewal moment gets missed because it's too much manual work. What is that based on: numbers, what agents tell you, or a specific deal?
2. **Matt (CEO)** [C] Public research points to a few causes besides manual work: price, owners believing another policy already covers them, and carriers requiring controls like MFA before they'll quote. Which of those do you actually see at UKON?
3. **Matt, then Ops for the data** [C] When a cyber policy doesn't renew, or a quote doesn't bind, is a postmortem done that tells you exactly why? Can I see the list or the reasons?
4. **Matt (CEO)** [A] As a wholesaler, what does UKON actually own? Who holds the client relationship, who has authority to quote and bind, and who prices the risk? Is anyone at UKON pricing or underwriting, or does every number come from the carrier? And how do UKON and the agent get paid?
5. **CPL, with Ops in the room** [A] Here's the workflow I built in six stages: confirm the client's data, get indications from carriers, build the proposal pack, equip the agent, run the questionnaire, then the owner's choice, firm quote, bind and report. Does the application happen before or after the client picks a carrier? Where is it wrong? At each stage, who hands what to whom: agent, UKON, carrier, client?
6. **CPL** [A] Walk me through three recent deals: one that bound, one that stalled and one that died. Who did what, when, and in which tool? Can I see what the agent sent you at the start, redacted?
7. **CPL** [C] Tell me about the last client who said no. What reason did they give, and what do you think the real reason was?
8. **Ops / submissions** [A] For each carrier you use for small-business cyber, how do you request an indication, how does it come back (portal, email, PDF, API or phone), and how long does it take? Can you show me one on screen, including what gets typed twice?
9. **Agency success** [A] Walk me through how one of your agencies runs a renewal at 120, 90, 60 and 30 days out. Who does what, and what can UKON see from the agency's system?
10. **Service / account management** [B] Once a policy is bound, what are the touchpoints during the year that make the renewal easier, and who owns each one: the agent, UKON or the carrier? Do any carriers monitor the client's security mid-term, and does UKON or the agent ever see those alerts?
11. **Service / claims** [B] Walk me through the last incident a UKON client reported, and any claim that was disputed. Was it because the application didn't match what was really in place?
