---
type: raw-source
title: "AMS export — Sloan's Lake Dental"
format: json-in-markdown
---

# AMS export — Sloan's Lake Dental

> SIMULATED. The agency (Front Range Independent Insurance Group), its staff and the policies below are
> invented for the demo; an agency's own records are never public. Everything about the practice itself
> (name, address, owner, domain) is real public information (see the other sources in this folder).
> Deliberately thin, like a real P&C account: no revenue and no headcount on file, so Stage 1 has to
> estimate them.

Pipeline code reads the JSON block below. Keep it valid JSON.

```json
{
  "source": "Agency management system export (simulated)",
  "exported_at": "2026-10-24",
  "agency": "Front Range Independent Insurance Group (fictional)",
  "account_manager": "Jordan Pike",
  "producer": "Alex Moreno",
  "client": {
    "account_name": "Sloan's Lake Dental",
    "mailing_address": "2750 W 29th Ave, Denver, CO 80211",
    "primary_contact": "Dr. Sage Pollack (owner)",
    "contact_email_domain": "sloanslakedental.com",
    "sic_code": "8021",
    "sic_description": "Offices and clinics of dentists"
  },
  "policies": [
    {
      "line": "Business Owners Policy (BOP)",
      "carrier": "Existing carrier (not relevant to demo)",
      "expiration": "2027-01-15",
      "rating_basis": "building + business personal property",
      "gross_sales_on_file": null,
      "cyber_endorsement": false
    },
    {
      "line": "Dental Professional Liability",
      "expiration": "2027-01-15",
      "dentists_insured": 3
    }
  ],
  "cyber_coverage": "none on file"
}
```
