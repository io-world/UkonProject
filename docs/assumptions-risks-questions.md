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

- How do carriers return indications today: API, portal, email? Which carriers matter most?
- Do carriers accept revenue bands for indications?
- What does the agency actually have in its AMS, and will it share an export?
- Which step do agents say kills the deal today: data gathering, explaining cyber, or the application?
- How many clients per producer renew per month, and how many get cyber offered today?
- Does Wispr Flow capture phone calls, or only meetings and dictation?
- Where do CPLs spend their time per bound policy now?

### After bind (added Oct 27)
- Which carriers monitor insureds after bind, how often, and who receives the alerts (client, agent, UKON)?
- What happens when a control from the application lapses mid-term? How often are claims disputed because the application didn't match reality?
- At renewal, what is re-checked: new application, rescan, attestations, evidence?
- What share of UKON's cyber policies renew at year two, and of the rest, who ended it (client or carrier) and why?

### Why SMBs don't buy or keep cyber (added Oct 27)
The brief says agents don't raise it because it's too much manual work. Competing explanations to test: price, belief
they're already covered by another policy, low perceived value, carriers declining or re-pricing on missing controls, and
an application owners can't answer. See the interview plan page (`web/public/interview/1-interview-plan.html#why-not`)
for evidence, tests and design consequences. The fastest single answer: ops' split of non-renewals into client vs carrier.

