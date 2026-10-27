---
type: raw-source
title: "AMS export — Quillfeather Dental"
format: json-in-markdown
---

# AMS export — Quillfeather Dental

> FICTIONAL. Simulated agency management system (AMS) export row for the demo client.

Pipeline code reads the JSON block below. Edit values here and re-run the pipeline; keep it valid JSON.

```json
{
  "source": "Agency management system export",
  "exported_at": "2026-10-24",
  "agency": "Front Range Independent Insurance Group (fictional)",
  "account_manager": "Jordan Pike",
  "producer": "Alex Moreno",
  "client": {
    "account_name": "Quillfeather Dental",
    "mailing_address": "1450 Garrison St, Ste 200, Lakewood, CO 80215",
    "primary_contact": "Dr. Maya Ellery (owner)",
    "contact_email_domain": "quillfeatherdental.com",
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
      "line": "Workers Compensation",
      "expiration": "2027-01-15",
      "rating_basis": "payroll",
      "payroll_on_file": 612000,
      "employee_count_on_file": 11,
      "payroll_audit_period": "2025 policy year"
    },
    {
      "line": "Dental Professional Liability",
      "expiration": "2027-01-15",
      "dentists_insured": 2
    }
  ],
  "cyber_coverage": "none on file"
}
```
