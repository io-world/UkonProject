# Workflow: from upcoming renewal to bound policy

The one-page map for the deliverable is the diagram below; the tables underneath are the detail
for each stage. Guiding principle: **AI does the paperwork, people make the calls, and the
database, not the model, owns every number a client sees.**

```mermaid
flowchart LR
  Q[Renewal queue<br/>60–120 days out] --> S1

  subgraph S1[1 · Confirm data · UKON 1a]
    A1[Ingest sources into client wiki<br/>AMS · filings · website · DNS] --> A2[Score entity candidates]
    A2 --> H1{{Human confirms entity}}
    H1 --> A3[Five fields<br/>ranges · confidence · source]
    A3 --> H2{{Review by exception}}
  end

  H2 --> S2
  subgraph S2[2 · Get indications · UKON 1b]
    G1{{Agent approves Send to carriers<br/>gated on Stage 1}} --> G2[Replies in: PDF · email · call<br/>figures checked against source · versioned]
    G2 --> G3[Follow-ups by fixed rules<br/>price moved · new condition · declined]
    G3 --> G4{{Agent checks flagged figures<br/>closes follow-ups}}
  end

  S2 --> S3
  R[AI web research<br/>industry incidents · regulation<br/>cited, human-reviewed] --> S3

  subgraph S3[3 · Client proposal pack · UKON 2]
    B1[AI drafts narrative<br/>no numbers allowed] --> B2[HTML report: numbers from DB<br/>+ answers so far + research]
    B2 --> H3{{Agent adjusts estimates<br/>carrier numbers locked}}
    H3 --> H4{{Agent submits → locked v‹N›.html → sends}}
  end

  H4 --> S4
  subgraph S4[4 · Equip the agent · UKON 3]
    D1[Pitch · objections · specimens<br/>news talking points · Ask about this client]
  end

  S4 --> S5
  subgraph S5[5 · Questionnaire · UKON 4a]
    I1{{Calls and emails<br/>agent taps answers live}} --> I2[Transcript or email → wiki<br/>answers with quotes · hedges flagged]
    I2 --> I3{{Agent confirms answers}}
  end
  I3 -.corrected revenue.-> S1

  I3 --> S6
  subgraph S6[6 · Decision, bind, report · UKON 4b]
    C1{{Owner's choice<br/>or not now + reason}} --> C2[Firm quote in<br/>checked vs PDF · compared with indication]
    C2 --> C3{{Owner accepts final terms}}
    C3 --> C4{{Conditions met with evidence<br/>client e-signs}}
    C4 --> F[Bind]
    F --> C5[Reports: client summary · deal record<br/>30-60-90 + touchpoints to renewal]
  end

  C5 -.debrief, next renewal.-> W[(Client + industry wiki<br/>smarter next renewal)]
```

UKON's brief has four stages; this splits its Stage 1 into **1 · Confirm data** and **2 · Get indications**
(decision #55) and its Stage 4 into **5 · Questionnaire** and **6 · Decision, bind, report** (decisions #59–60),
so stages 3 and 4 here are UKON's 2 and 3.

Legend: rectangles = AI or system; hexagons = a human decision.

---

## Stage 0 · Spot the renewal

| | |
|---|---|
| **AI / system** | Pull renewals 60–120 days out from the agency management system (AMS); rank by fit (industry, size, data sensitivity) so the agent works the best opportunities first. |
| **Human** | Agent or account manager picks which to pursue; can snooze a client. |
| **What could go wrong** | Clients already have cyber (as a BOP endorsement or elsewhere) → wasted effort. **Catch:** check existing policies and endorsements in the AMS before queuing. *(Designed, not built.)* |

## Stage 1 · Confirm data (built; UKON Stage 1, part 1)

| Step | AI does | Human does | What could go wrong → how it's caught |
|---|---|---|---|
| Ingest | Reads the AMS row, state registry, NPI registry, website, directory listings, press releases and DNS records into the client wiki; extracts signals with a citation per value. | — | Prompt injection or junk in sources → sources are data, never instructions; every value cites its raw file. |
| Entity resolution | Scores candidates on name + state + address + domain together; a delinquent or dissolved entity's score is halved. | **Always confirms** the match. | Same name at the same address but delinquent → the real demo case ("Sloans Lake Dental PLLC", delinquent since 2022, vs Sage Dentistry, PLLC in good standing). |
| Domain, industry, address | Cross-checks independent sources; high confidence when they agree. | Only if flagged. | Wrong domain → wrong carrier scan → wrong price. Needs agreement across AMS email domain, website, and MX records. |
| Employees | Most recent direct count wins; range spans recent signals; stale signals ignored. With no published count, an explicit estimate (dentists × support-staff assumption), low confidence. | Reviews if signals disagree beyond ±20%, or if the count is estimated. | Headcount ≠ FTEs → stated as an assumption; confirmed on the call. |
| Revenue | Waterfall: agency record → public filing → two benchmark methods (staff × revenue/employee; dentists × billings/dentist). Range + confidence. | **Always reviews** estimated revenue. | Revenue isn't public for private SMBs → two independent methods must agree; flagged for confirmation before binding. |
| Exposure | Rough, explainable score: data sensitivity, email accounts, DMARC/SPF, online payments, record volume. | Adjusts with a slider. | Mistaken for a security rating → labeled "not a security scan"; controls unknown until the call. |

Review by exception: in the demo, 3 of ~8 items need a person (entity, revenue, plus anything with conflicting signals).

## Stage 2 · Get indications: the agent ↔ carrier exchange (built; UKON Stage 1, part 2)

An indication is a carrier's non-binding ballpark for a given limit and deductible. UKON's Stage 1 isn't done
until those come back, so the prototype gives the round trip its own stage, with a person's approval before
anything is sent. The app's Stage 2 screen sends (gated on Stage 1), reads replies in from the inbox, shows
every carrier's versions read-only, lets a person check a flagged figure, and closes follow-ups with a note.

| Step | AI does | Human does | What could go wrong → how it's caught |
|---|---|---|---|
| Request (outbound) | Sends the five fields to each carrier on the panel for two options: **$1M / $10K** and **$2M / $25K**. Stores the basis exactly as sent, with what was still unreviewed. | Sends (re-requests are gated: entity confirmed and flagged fields reviewed). | Wrong company or stale revenue priced → the basis snapshot shows what each carrier priced on; revenue drift beyond ±15% raises "re-request". |
| Reply arrives | Nothing: the reply is saved as received in `wiki/raw/<client>/indications/`, recording **how it came in**. PDF letters, emails and Wispr Flow captures of underwriter calls are saved as files and ingested. (Paste / API inputs were prototyped and removed.) | Saves the file. | Same reply twice → content hash recorded. |
| Extract | Reads the text (pypdf / pasted text), then an LLM pulls carrier, options, premiums, sublimits, conditions, expiry, with the line each came from. | — | Model invents or mis-reads a figure → next step. |
| Check | **Deterministic:** every money figure and the expiry date must appear in the source, written in full. Client name and carrier name must appear. | Confirms or rejects anything that fails (e.g. Cobalt's "5.29k"). | Shorthand, calculated dates, a reply for another client → flagged, never auto-accepted. |
| Version | Appends a version per carrier + option; nothing is overwritten. Diff vs the previous version (premium, limit, deductible, sublimits, conditions, expiry, verbal → written). | — | History lost → append-only table, values locked by a database trigger. |
| Act | Fixed rules turn the diff into actions: price changed (and whether a sent pack showed the old price), new condition (with the intake's answer), declined, verbal-only, figure to confirm. Alerts for expiring indications and revenue drift. | Works the list; closes each action with a note. | Agent misses a change → it stays in "Needs attention" until a person closes it. |
| Current state | The client pack reads only the latest **written**, **checked** version per carrier + option. | Picks the carrier to show (default rule: cheapest $1M with full-limit ransomware). | Verbal number reaches the client → impossible: verbal versions are excluded from the view. |

Demo: Stage 2 starts empty. After Stage 1 is reviewed the agent sends the requests; five replies then wait in the carrier
inbox and are taken in live, in date order (Northwind PDF, Cobalt email, Ridgeline call then letter, Northwind's revised
letter). A reply is refused for a carrier nobody asked.

## Industry research (built)

| | |
|---|---|
| **AI does** | Searches the web for recent, real events in the client's industry (breaches, ransomware, vendor incidents, regulation) and writes cited items to `wiki/raw/research/` (`client-research` skill). |
| **Human does** | Reviews the items; deletes any that don't fit. Each item is tagged for the client pack, the agent brief, or both. |
| **What could go wrong** | Invented or stale events → every item needs a URL and date; figures are quoted from the source; the tailored line may not add numbers. |

> **Stages 2 and 3 loop.** The owner usually asks for changes after seeing the pack (another limit or deductible, a
> corrected fact), and the agent goes back to the carriers for a new round, until the owner decides or the renewal date
> arrives. The prototype re-requests on a changed basis and versions every reply, but doesn't capture the owner's
> requested changes yet (see "Things flagged" in `decisions.md`).

## Stage 3 · Client proposal pack: the HTML report (built)

| Step | AI does | Human does | What could go wrong → how it's caught |
|---|---|---|---|
| Draft | Writes the "why it matters" text, three industry scenarios, exposure explainer, next steps, using placeholders for any count. | — | AI invents a figure → **any digit in AI prose fails validation**; figures are filled from the DB. |
| Numbers | — (rendered from DB: premiums, limits, deductibles, sublimits, benchmark costs) | — | Hallucinated price → impossible; no code path from model to price. |
| Coverage text | — (from a CPL-approved plain-language library) | — | Overstating coverage → library text only; funds-transfer sublimit is flagged visually. |
| Adjust | Shows its recommendation next to the current value. | Moves revenue, employees, exposure, records, carrier; adds a reason. | Revenue moves far from what carriers priced on → "indication needs refresh" banner; premiums are not recalculated. |
| Lock & send | — | Submits (version locked), then sends. Any later change creates a new version. Before sending, can **undo submit**: the version is marked withdrawn (who, when, why), never unlocked, and editing continues in a new draft. A dropdown opens any locked version read-only. | Client sees an unreviewed draft → client view only shows submitted versions. |

## Stage 4 · Equip the agent: the brief (built)

| Step | AI does | Human does | What could go wrong → how it's caught |
|---|---|---|---|
| Brief | Tailors a 60-second pitch; selects and tailors objection answers from the **CPL-approved library**; maps where key items live in the specimen form. | Reads it before the meeting. | AI invents an objection answer → library-only; tailoring can't add claims. Specimen references must resolve to real text on the cited page, or they're dropped (production rule). |
| Ask about this client | Answers from DB (numbers) + wiki (reasons), cited; read-only. | Asks questions. | Coverage interpretation → **escalates to CPL**. Agent wants to change a value → told to use the slider so it's logged. |
| Debrief *(designed)* | Ingests meeting notes and new objections into client + industry pages. | Logs outcome. | New objections bypass review → go to CPLs before entering the library. |

## Stage 5 · Questionnaire: calls and emails, human in the loop (built; UKON Stage 4, part 1)

The application questions, in plain language, answered over as many calls and emails as it takes. They come after
the pack because asking about security practices before the owner has seen a price adds friction, and they don't
depend on which carrier wins. (The demo seed runs call 1 before the pack, then call 2 and an email after it.)

| Step | AI does | Human does | What could go wrong → how it's caught |
|---|---|---|---|
| Question list | Plain-language questions from the carrier question bank, minus what the wiki/DB already knows. | — | Jargon → plain wording ("a code from your phone" for MFA). |
| Calls and emails | — | Agent runs calls from **Stage 5 → Live call** (numbered questions, taps, "client unsure", CPL questions logged, limit walkthrough), recorded with consent by Wispr Flow; the owner or office manager can also answer by email. Answers already on record show with their source; **Correct** opens the inputs. | No consent → transcript not used. Agent answers a coverage question → script says escalate; it's logged. |
| Extract & merge | Pulls intake + application answers with the quoted line per call or email; checks calls against the live taps; merges with earlier sources. | — | "Mostly", "I think" → **hedge check forces follow-up**. Recording ≠ tap → **CONFLICT**. A later source contradicts a confirmed answer → reopened, never silently overwritten. Re-ingesting an older source never overwrites a newer one. |
| Navigate | Filter: all / not answered / answered; collapsible sections with open/answered counts. | Works the open items. | Agent loses track over several touches → "not answered" shows only what's left. |
| Proceed incomplete | Exposure score recalculated from controls confirmed so far. | Agent decides it's enough to build the pack. | Owner thinks the gaps block a price → pack lists them as "to confirm". |
| Confirm | — | Agent confirms in **After the call** or **Application**; confirmed revenue/records update the report as logged changes. | Wrong answer reaches the application → agent review now, client signature later. |

Demo: call 1 leaves items open; call 2 closes MFA and EDR (exposure 63 → 45); the office manager's email closes revenue
($2.52M per the accountant), encryption and California, and flags "I think the limit is $50,000" on a breach
endorsement: the "already covered" belief. Three questions stay open.

## Stage 6 · Decision, bind, report (built; carrier side simulated; UKON Stage 4, part 2)

| Step | AI does | Human does | What could go wrong → how it's caught |
|---|---|---|---|
| Owner's choice | — | Agent presents the pack and records the option chosen, or **not now** with a reason from a fixed list (price, already covered, no need, carrier requirements, timing, other). Append-only; locked once the firm quote is in. | Lost deals with no reason → a "no" can't be saved without one; reasons feed the deal record. |
| Firm quote in | Extracts the carrier's firm quote (cached offline); checks every figure and the policy dates against the PDF; compares with the written indication; conditions compared by what they require, not wording; each tagged before or after binding. | Confirms a figure the check couldn't find. | Quote ≠ indication → shown side by side with the carrier's stated reason. Quote for the wrong option → refused. |
| Final terms | — | Presents what changed and what's needed; owner **accepts**, or declines with a reason. | Owner surprised at bind → the change is presented before the yes. |
| Bind | Records the binder (simulated policy number). | Marks each before-binding condition **met with evidence**; client e-signs the complete application. | Binding with an open condition, an unconfirmed answer or no "yes" → the Bind button stays disabled and says why. |
| Report | Client summary (plain language; coverage questions go to a CPL); deal record (milestones, who did what, sources, outcome and reason); after-bind plan built by rules from the binder, post-bind conditions, weak answers and exposure findings: 30-60-90 plus touchpoints to renewal (120/90/60/30 days out). | Owns the touchpoints. | Who owns each touchpoint (agent, UKON, carrier) is unknown → owners are labelled "proposed"; it's an interview question. |

Option for lower-touch clients *(designed)*: the same plain-language questions as a link the
owner answers on their phone, with the call as the default for relationship clients.
