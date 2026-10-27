---
type: raw-source
title: "DNS email records — quillfeatherdental.com"
format: json-in-markdown
---

# DNS email records — quillfeatherdental.com

> SIMULATED DNS lookup result. In production these come from a live public DNS query (TXT records), which is not a security scan.

Pipeline code reads the JSON block below. Edit values here and re-run the pipeline; keep it valid JSON.

```json
{
  "domain": "quillfeatherdental.com",
  "queried_at": "2026-10-24T18:02:00Z",
  "mx": [
    "quillfeatherdental-com.mail.protection.outlook.com"
  ],
  "spf": "v=spf1 include:spf.protection.outlook.com ~all",
  "dmarc": "v=DMARC1; p=none; rua=mailto:dmarc@quillfeatherdental.com",
  "interpretation_hints": {
    "spf_all_qualifier": "~all (softfail): spoofed mail is marked but usually still delivered",
    "dmarc_policy": "p=none: monitoring only; spoofed mail claiming to be from this domain is not blocked"
  }
}
```
