---
type: research
naics: "621210"
gathered: 2026-10-26 (refreshed for Sloan's Lake Dental)
gathered_by: client-research skill (web search), reviewed by a human before use
format: json-in-markdown
---

# Industry research — dental offices and cyber (Oct 2026)

Real, recent events gathered from the web for dental practices. The client pack shows the items
tagged `client_pack`; the agent brief shows all of them as talking points.

**Rules:** every item needs a source URL and date. Figures inside an item are quoted from that
source, not generated. The `for_this_client` line is the only tailored text, and it must not
introduce new numbers. Remove an item by deleting it from the JSON block below.

```json
{
  "naics": "621210",
  "items": [
    {
      "id": "artistic-smiles-longmont",
      "category": "breach",
      "headline": "Longmont, Colorado dental practice reports a network breach",
      "summary": "Artistic Smiles in Longmont found unauthorized access to its network between June 14 and June 21, 2026. It reported 3,735 affected individuals to HHS; names, addresses, birth dates and dental and medical treatment information may have been accessed.",
      "for_this_client": "This is a Front Range dental office, up the road from Denver, hit this summer.",
      "source": "Becker's Dental Review",
      "url": "https://www.beckersdental.com/?p=27834",
      "date": "2026-10-20",
      "use_in": [
        "client_pack",
        "agent_brief"
      ]
    },
    {
      "id": "360-dental-ransomware",
      "category": "ransomware",
      "headline": "Philadelphia dental practice locked out by ransomware",
      "summary": "In November 2025 an attacker got into 360 Dental's internal server and locked its files. About 11,273 patients were notified; names, birth dates, insurance details and treatment records were involved. The practice replaced computers, rebuilt the server, and added multi-factor authentication and VPN-only remote access afterward.",
      "for_this_client": "The fixes this practice made after the attack (phone codes on every login, remote access only through a secure connection) are the same things insurers ask a practice like Sloan's Lake about up front.",
      "source": "Paubox",
      "url": "https://www.paubox.com/blog/360-dental-pc-reports-ransomware-incident-affecting-over-11k",
      "date": "2026-02-16",
      "use_in": [
        "client_pack",
        "agent_brief"
      ]
    },
    {
      "id": "beckers-2026-breaches",
      "category": "breach",
      "headline": "23 dental data breaches reported so far in 2026",
      "summary": "A September 2026 roundup lists 23 dental breaches this year, from single-office practices to multi-location groups: from about 500 to 45,853 patients affected. Causes include ransomware, network intrusions, and a compromised account used to reach patient records.",
      "for_this_client": "Most of these were single-office and small group practices, not hospitals.",
      "source": "Becker's Dental Review",
      "url": "https://www.beckersdental.com/?p=27141",
      "date": "2026-09-24",
      "use_in": [
        "client_pack",
        "agent_brief"
      ]
    },
    {
      "id": "paubox-dmarc-2026",
      "category": "email",
      "headline": "Most healthcare email breaches hit organizations without DMARC enforcement",
      "summary": "Paubox's 2026 Healthcare Email Security Report analyzed 170 email-related healthcare breaches from 2025: 74% of the breached organizations either lacked DMARC or used it for monitoring only. DMARC stops others from sending mail as your domain, but not look-alike domains or a hijacked mailbox.",
      "for_this_client": "Sloan's Lake already uses Paubox for encrypted email and a strict sender list, but its domain has no DMARC record, the gap this report keeps finding in breached practices. It's a free DNS change.",
      "source": "Paubox",
      "url": "https://www.paubox.com/blog/why-dmarc-cannot-stop-every-healthcare-impersonation-attack",
      "date": "2026-09-01",
      "use_in": [
        "client_pack",
        "agent_brief"
      ]
    },
    {
      "id": "dental-email-compromise-2026",
      "category": "email",
      "headline": "Phished staff email accounts behind a run of 2026 dental breaches",
      "summary": "An Indianapolis pediatric dental practice had an employee's email account taken over after the employee answered a phishing email (5,900 people affected). A vendor whose email accounts were phished exposed patients of four dental practices in Virginia and North Carolina, and several Washington and New York practices reported unauthorized email access.",
      "for_this_client": "Every Microsoft 365 mailbox at the practice is a door like these, which is why insurers ask about phone codes on email first.",
      "source": "The HIPAA Journal",
      "url": "https://www.hipaajournal.com/cybersecurity-incidents-multiple-dental-practices/",
      "date": "2026-06-10",
      "use_in": [
        "client_pack",
        "agent_brief"
      ]
    },
    {
      "id": "eassist-vendor",
      "category": "vendor",
      "headline": "Dental billing vendor reports a security incident",
      "summary": "eAssist, a dental billing service, notified customers in September 2026 of a possible information security incident after a ransomware group claimed access.",
      "for_this_client": "Sloan's Lake's patient data also sits with outside vendors: Adit for booking and bill pay, Paubox for email, its website and marketing firm, and its IT provider. A problem at a vendor can still become the practice's notification duty.",
      "source": "Becker's Dental Review",
      "url": "https://www.beckersdental.com/?p=27141",
      "date": "2026-09-24",
      "use_in": [
        "client_pack",
        "agent_brief"
      ]
    },
    {
      "id": "change-healthcare",
      "category": "vendor",
      "headline": "Clearinghouse attack stalled dental insurance claims for weeks",
      "summary": "The February 2024 ransomware attack on Change Healthcare, which entered through a remote login without multi-factor authentication, disrupted dental claims processing for weeks and squeezed practice cash flow.",
      "for_this_client": "Even with no breach at the practice, an outage at a partner can stop insurance payments.",
      "source": "Siotek IT Solutions",
      "url": "https://siotek.net/resources/dental-practice-cybersecurity-2026",
      "date": "2026-04-13",
      "use_in": [
        "agent_brief"
      ]
    },
    {
      "id": "bec-fake-invoices",
      "category": "bec",
      "headline": "Fake vendor invoices are a common attack on dental front offices",
      "summary": "Business email compromise against dental practices includes fake vendor invoices with changed bank details, impersonated owners, payroll redirects, and compromised vendor email accounts.",
      "for_this_client": "An implant-heavy practice pays large lab and supply invoices, which is exactly what fake-invoice scams go after.",
      "source": "Siotek IT Solutions",
      "url": "https://siotek.net/resources/dental-practice-cybersecurity-2026",
      "date": "2026-04-13",
      "use_in": [
        "agent_brief"
      ]
    },
    {
      "id": "ocr-first-ransomware-settlement",
      "category": "regulation",
      "headline": "First federal HIPAA settlement over a ransomware attack",
      "summary": "In October 2023 HHS's Office for Civil Rights settled with Doctors' Management Services for $100,000 after a ransomware attack affecting 206,695 people, citing a missing risk analysis and weak activity monitoring, plus a three-year corrective plan.",
      "for_this_client": "Regulators look at whether a practice assessed its risks before an attack, not only at the attack itself.",
      "source": "Jones Day",
      "url": "https://www.jonesday.com/en/insights/2023/12/hhs-enters-into-firstever-ransomware-resolution-agreement-and-corrective-action-plan",
      "date": "2023-12-01",
      "use_in": [
        "agent_brief"
      ]
    },
    {
      "id": "hipaa-security-rule-update",
      "category": "regulation",
      "headline": "Proposed HIPAA rule would make MFA and encryption mandatory",
      "summary": "A proposed update to the HIPAA Security Rule would require multi-factor authentication for access to patient-data systems and encryption of that data. It is not final; the final rule is currently projected for July 2027.",
      "for_this_client": "Turning on phone codes for every login now gets ahead of the rule and is already an insurer requirement.",
      "source": "ComplianceHub",
      "url": "https://compliancehub.wiki/blog/hipaa-security-rule-final-rule-may-2026-mfa-encryption-uncertainty",
      "date": "2026-08-27",
      "use_in": [
        "client_pack",
        "agent_brief"
      ]
    },
    {
      "id": "co-dental-wellness-anubis",
      "category": "ransomware",
      "headline": "Ransomware group lists a Colorado dental practice",
      "summary": "The Anubis ransomware group claimed Colorado Dental Wellness Center as a victim on May 1, 2026, according to the breach-tracking site Breachsense. The size and type of data were not disclosed; this is the attacker's claim, not a confirmed breach notice.",
      "for_this_client": "Ransomware crews are listing Colorado dental offices by name this year.",
      "source": "Breachsense",
      "url": "https://www.breachsense.com/breaches/colorado-dental-wellness-center-data-breach/",
      "date": "2026-05-01",
      "use_in": [
        "agent_brief"
      ]
    },
    {
      "id": "absolute-dental-msp",
      "category": "vendor",
      "headline": "$3.3M settlement after attackers came in through a dental group's IT provider",
      "summary": "Absolute Dental, a Las Vegas group with more than 50 Nevada locations, received final approval for a $3.3 million class-action settlement. Attackers got in between February 19 and March 5, 2025 through an account linked to its third-party managed IT provider; the class is estimated at more than 1.2 million people.",
      "for_this_client": "An outside IT company's access is a door into the practice too, and a lawsuit can follow even for a single office.",
      "source": "Becker's Dental Review",
      "url": "https://www.beckersdental.com/?p=25901",
      "date": "2026-08-04",
      "use_in": [
        "agent_brief"
      ]
    },
    {
      "id": "wsda-compromised-office-email",
      "category": "email",
      "headline": "Dental offices' own email accounts used to phish patients and vendors",
      "summary": "The Washington State Dental Association warned members that compromised dental office email accounts were sending phishing messages with vague subjects such as \"new approved statement\" and unexpected attachments to the office's contacts.",
      "for_this_client": "If a mailbox at the practice is taken over, the next victims are its own patients and suppliers, which is a liability claim, not just an IT problem.",
      "source": "Washington State Dental Association",
      "url": "https://www.wsda.org/news/blog/2025/06/13/recent-email-scams-targeting-dental-offices--what-to-watch-for-and-how-to-respond",
      "date": "2025-06-13",
      "use_in": [
        "agent_brief"
      ]
    }
  ],
  "client": "sloanslake"
}
```
