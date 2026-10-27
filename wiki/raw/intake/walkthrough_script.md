---
type: raw-source
title: "Limit walkthrough script"
format: json-in-markdown
---

# Limit walkthrough script

> What the agent says when walking the client through how the recommended limit is built
> (Section 2 of [[raw/intake/intake_questions|the intake]]; prose version in `docs/client-intake.md`).
> Moved here from the original standalone intake screen so the app and this page share one script.

- `[[a:q7]]` is replaced on screen by the client's answer to that intake question.
- `[[r:key|label]]` is a figure from the report. **The agent reads it; never estimates it on the call.**
  Figures the prototype doesn't model yet show as a labelled placeholder.
- `check_key` links a step's check question to its walkthrough item in the question bank.

```json
{
  "steps": [
    {
      "id": "open",
      "n": "Opening",
      "title": "Set up the walkthrough",
      "say": "Before we look at options, I’d like to show you how we got to a recommended limit. It’s built from what you told us plus insurance claims data, and every assumption is on the screen. If something looks wrong for your business, tell me and we’ll change it together."
    },
    {
      "id": "f1",
      "n": "1",
      "title": "Downtime",
      "sub": "Business interruption",
      "built": "Daily gross profit × days down × share of the business actually stopped, minus the waiting period.",
      "say": "The biggest cost in most cyber claims isn’t the hack itself, it’s being shut down. You told us about [[a:q2]] of the practice stops if systems go down, and the typical ransomware outage runs around [[r:downtime_days|downtime days]]. After your [[r:waiting_period|waiting period]] waiting period, that’s roughly [[r:bi_loss|BI loss]].",
      "check": "Does that many days feel realistic, given your backups?",
      "note": "If the client says “we’d be back in a day,” ask when they last tested a full restore (Q4). If never, keep the default and note it.",
      "check_key": "check_f1"
    },
    {
      "id": "f2",
      "n": "2",
      "title": "A key vendor going down",
      "sub": "Dependent business interruption",
      "built": "Daily gross profit × share of revenue relying on that vendor × days it’s out.",
      "say": "You mentioned you rely on [[a:q6]]. If they get hit, you lose revenue even though your own systems are fine. That scenario is about [[r:dbi_loss|vendor outage loss]].",
      "low": "Little public data supports this one. Tell the client it’s an estimate."
    },
    {
      "id": "f3",
      "n": "3",
      "title": "Ransom payment",
      "sub": "Extortion",
      "built": "Published ransom-payment ranges for businesses this size. Not a percentage of revenue.",
      "say": "Fewer businesses pay ransoms these days, but when they do, payments for a business your size typically fall between [[r:ransom_low|low]] and [[r:ransom_high|high]]. We include it so the policy can cover it if paying is ever the right call.",
      "note": "Don’t advise whether to pay. That decision sits with the client, the carrier and the incident response team."
    },
    {
      "id": "f4",
      "n": "4",
      "title": "Incident response",
      "sub": "Forensics, legal, crisis services",
      "built": "Average crisis-services cost from insurance claims data for this kind of incident.",
      "say": "If something happens, the policy pays for the experts: forensics, lawyers, and the people who restore your systems. For practices like yours that typically runs [[r:ir_cost|incident response cost]]."
    },
    {
      "id": "f5",
      "n": "5",
      "title": "Restoring systems and data",
      "sub": "Data restoration",
      "built": "Critical systems × rebuild hours × hourly rate, plus re-creating lost data.",
      "say": "You listed [[a:q5]] critical systems. Rebuilding those comes to about [[r:restore_cost|restore cost]].",
      "low": "This rests on assumptions. Show them on screen."
    },
    {
      "id": "f6",
      "n": "6",
      "title": "Notifying patients",
      "sub": "Breach notification and credit monitoring",
      "built": "Records × (notification cost + credit monitoring × share who sign up).",
      "say": "If personal data gets out, the law requires you to notify everyone affected. With [[a:q7]] records, notification and credit monitoring come to roughly [[r:notification_cost|notification cost]].",
      "check": "Does that record count sound right? Include former patients you still hold records for.",
      "check_key": "check_f6"
    },
    {
      "id": "f7",
      "n": "7",
      "title": "Fake payment requests",
      "sub": "Social engineering, its own sublimit",
      "built": "Largest routine outgoing payment plus a buffer.",
      "say": "One of the most common claims we see is a fake email asking to change where a payment goes. Your largest regular payment is about [[a:q12]], so we’d want at least [[r:social_eng_sublimit|social engineering sublimit]] for this.",
      "check": "Do you call to confirm before changing anyone’s bank details?",
      "note": "Their answer to Q13 already covers this. Skip the check if it’s answered.",
      "check_key": "check_f7"
    },
    {
      "id": "f8",
      "n": "8",
      "title": "Regulators",
      "sub": "Regulatory fines and investigations",
      "built": "Records under each law (HIPAA, state privacy laws) × penalty × likelihood of enforcement.",
      "say": "Because you hold [[a:q8]], a regulator could investigate after a breach. We estimate that exposure at [[r:regulatory_exposure|regulatory exposure]]."
    },
    {
      "id": "f9",
      "n": "9",
      "title": "Lawsuits from patients",
      "sub": "Privacy litigation",
      "built": "Records × per-person damages (for California residents, the CCPA’s statutory range) × likelihood of a suit. Modelled low to mid range, where settlements land.",
      "say": "Patients can sue after a breach, and in some states the law sets a dollar amount per person. For your records, that’s about [[r:litigation_exposure|litigation exposure]]."
    },
    {
      "id": "f10",
      "n": "10",
      "title": "Card payments",
      "sub": "PCI assessments",
      "built": "Card records × (reissue cost + fraud assessment) + non-compliance fines.",
      "say": "Because you [[a:q11]], a card breach could mean charges from the card brands for reissuing cards and covering fraud. That’s around [[r:pci_exposure|PCI exposure]]."
    },
    {
      "id": "roll",
      "n": "Roll-up",
      "title": "Put it together",
      "built": "Don’t add all ten. A real incident is one of these scenarios; the larger one sets the limit.",
      "scen": true,
      "say": "Put together, your realistic worst case is a [[r:worst_scenario|worst scenario]] event at about [[r:scenario_total|expected total]], with a severe case near [[r:scenario_severe|severe total]]. Your current limit is [[r:current_limit|current limit]]. So the question is whether you’re comfortable covering the gap of [[r:gap|gap]] yourself, or whether we should look at [[r:recommended_limit|recommended limit]].",
      "check": "Is there anything here that doesn’t fit how your practice really works?",
      "check_key": "check_roll"
    },
    {
      "id": "close",
      "n": "Closing",
      "title": "Next steps",
      "say": "I’ll update the report with any changes you gave me, and you’ll see the carrier options side by side. The application questions come from what we just covered, so you’ll be reviewing and signing answers you already gave."
    }
  ]
}
```
