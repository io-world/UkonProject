---
type: client-people
client: sloanslake
compiled: 2026-10-27
format: json-in-markdown
---

# People at Sloan's Lake Dental — notes for the agent

> Compiled from this client's wiki sources so the producer knows who they'll talk to. Three kinds of note,
> always labeled:
> - **public**: from a real public record (state registry, NPI, the practice's website, its press releases).
> - **call (simulated)**: from the simulated intake calls. Invented for the demo and tied to a role, never to a
>   real person's name, because no one at the practice actually said it.
> - **AI-suggested**: conversation openers written by AI from the public notes only. They add no new facts:
>   nothing personal (family, hobbies, health) is ever made up about a real person.
>
> Not included on purpose: staff first names that appear only in patients' Google reviews, and anything personal
> that isn't part of the business's own public record.

Pipeline code reads the JSON block below. Keep it valid JSON.

```json
{
  "people": [
    {
      "name": "Dr. Sage Pollack, DMD",
      "role": "Owner and founder; decision-maker",
      "notes": [
        {"kind": "public", "text": "Owner of Sage Dentistry, PLLC and its authorized official on the federal NPI record; registered agent with the Colorado Secretary of State.", "source": "wiki/raw/sloanslake/npi_registry.md"},
        {"kind": "public", "text": "DMD from Midwestern University College of Dental Medicine; Associate Fellow of the American Academy of Implant Dentistry. Focus: implants, cosmetic and full-mouth reconstruction, TMJ.", "source": "wiki/raw/sloanslake/website.md"},
        {"kind": "public", "text": "Individual NPI since 2007. Described as the practice's founder in the Sept 2025 press release.", "source": "wiki/raw/sloanslake/npi_registry.md"},
        {"kind": "public", "text": "Ran several 'Sage Dentistry' offices (Lakewood, Lafayette, Boulder, Arvada, Denver) between 2016 and 2024; all were dissolved, leaving Sloan's Lake as the one office.", "source": "wiki/raw/sloanslake/co_sos_entities.md"},
        {"kind": "ai", "text": "Open with the practice, not cyber: \"You've brought everything under one roof at Sloan's Lake. How has running one office instead of several changed things?\"", "source": "wiki/raw/sloanslake/co_sos_entities.md"},
        {"kind": "ai", "text": "Implant work means large lab and supply payments. That's a natural bridge to the fake-invoice scenario in the pack.", "source": "wiki/raw/sloanslake/website.md"},
        {"kind": "ai", "text": "The practice already pays for encrypted email (Paubox). Acknowledge it before mentioning the missing DMARC record: she's already invested in security.", "source": "wiki/raw/sloanslake/dns_records.md"}
      ]
    },
    {
      "name": "Dr. Stephanie Flaksman, DMD",
      "role": "Associate dentist",
      "notes": [
        {"kind": "public", "text": "DMD from LECOM (Lake Erie College of Osteopathic Medicine), Bradenton, Florida.", "source": "wiki/raw/sloanslake/website.md"},
        {"kind": "public", "text": "Named alongside Dr. Pollack in the Aug 2025 press release; on the current team page.", "source": "wiki/raw/sloanslake/press_releases.md"},
        {"kind": "ai", "text": "Each dentist has an email login. If she joins the meeting, the phone-codes-on-every-login question applies to her account too.", "source": "wiki/raw/sloanslake/website.md"}
      ]
    },
    {
      "name": "Dr. Brian Ferguson, DMD",
      "role": "Associate dentist",
      "notes": [
        {"kind": "public", "text": "DMD from the University of Pittsburgh; previously practiced in Seattle.", "source": "wiki/raw/sloanslake/website.md"},
        {"kind": "public", "text": "On the current team page but not in the Aug 2025 press release, so likely a recent addition.", "source": "wiki/raw/sloanslake/press_releases.md"},
        {"kind": "ai", "text": "A newer dentist is a good reason to ask how new staff get email and system access: onboarding is where phone codes get skipped.", "source": "wiki/raw/sloanslake/website.md"}
      ]
    },
    {
      "name": "Dr. Dat Le",
      "role": "Dentist (confirm still with the practice)",
      "notes": [
        {"kind": "public", "text": "Named in the Aug 2025 press release and in patient reviews, but not on the current team page.", "source": "wiki/raw/sloanslake/press_releases.md"},
        {"kind": "ai", "text": "If he has left, ask whether his email and system accounts were closed. Former staff accounts are a common way in.", "source": "wiki/raw/sloanslake/website.md"}
      ]
    },
    {
      "name": "Practice owner (role in the simulated calls)",
      "role": "As voiced in intake call 1",
      "simulated": true,
      "notes": [
        {"kind": "call", "text": "Thinks revenue is higher than our $2.35M estimate because of implant volume; wants the accountant to give the real figure.", "source": "wiki/raw/sloanslake/call_1_intake.md"},
        {"kind": "call", "text": "Downtime is the main worry: \"The downtime part is the one that worries me.\" Lead with business interruption.", "source": "wiki/raw/sloanslake/call_1_intake.md"},
        {"kind": "call", "text": "Asked whether a breach that starts at the IT provider would be covered. Bring the CPL's written answer; don't answer it yourself.", "source": "wiki/raw/sloanslake/call_1_intake.md"},
        {"kind": "call", "text": "Nearly paid a fake lab invoice two years ago; caught it before money went out.", "source": "wiki/raw/sloanslake/call_1_intake.md"}
      ]
    },
    {
      "name": "Office manager (role in the simulated calls)",
      "role": "Day-to-day contact for IT and payments; name not on file",
      "simulated": true,
      "notes": [
        {"kind": "call", "text": "Always calls vendors back on a known number before changing bank details: a hard rule since the lab-invoice scare.", "source": "wiki/raw/sloanslake/call_1_intake.md"},
        {"kind": "call", "text": "Got the IT provider to turn on phone codes for all three hygienists and confirmed attack-monitoring software on all nine computers.", "source": "wiki/raw/sloanslake/call_2_followup.md"},
        {"kind": "call", "text": "Backup restore test scheduled for next month: follow up after it happens.", "source": "wiki/raw/sloanslake/call_2_followup.md"},
        {"kind": "ai", "text": "Best person for the remaining application questions (backups, encryption, training). Get the name and direct line on the next call.", "source": "wiki/raw/sloanslake/call_2_followup.md"}
      ]
    }
  ]
}
```
