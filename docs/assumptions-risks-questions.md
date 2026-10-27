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

Rule: only ask what only UKON can answer (its process, systems, numbers, recent cases). Anything
answerable from public research is in the background section of the interview plan instead.
Full list by person: `web/public/interview/1-interview-plan.html`. The three gaps:

### A. How the work actually moves today
- Walk through three recent deals (bound, stalled, died): who did what, when, in which tool.
- What an agent actually sends to start a quote (see a redacted one).
- Per carrier: how an indication is requested, how it comes back (portal, email, PDF, API, phone), how long.
- How carriers are chosen for a client; last quarter's declines and info requests, and why.
- Who tells the agent when an indication arrives; where data is re-typed; existing carrier integrations.
- How an agency runs a renewal (120/90/60/30) and what UKON can see from agency systems.
- How UKON and the agent are paid on cyber, new and renewal.

### B. What happens after bind
- Who the client's contact is for the policy year; what UKON does between bind and renewal.
- Which panel carriers monitor mid-term, and whether alerts reach UKON or the agent.
- The last incident a UKON client reported, end to end; any disputed claims and why.
- How the cyber policy's own renewal starts and what is collected again; mid-term changes.
- Who is responsible when an application answer turns out wrong.

### C. Why the renewal window is missed (Matt's view vs research)
- What the "too much manual work" diagnosis is based on.
- Which of price / "already covered" / low perceived value / carrier declines UKON actually sees.
- Year-two retention, and the split between client-walked and carrier-declined.
- First-time adoption vs retention: which is the bigger prize.
- Reason codes for quoted-not-bound and non-renewal; the offered → quoted → bound → year-2 funnel.
- What agents say when a renewing client wasn't offered cyber; what UKON has already tried.
