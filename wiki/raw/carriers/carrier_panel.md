---
type: carrier-reference
title: "Carrier panel — cyber"
format: json-in-markdown
---

# Carrier panel — cyber (FICTIONAL)

> Which carriers the agency sends cyber indication requests to, and how. Outbound channel is how
> the request goes out; replies come back however the carrier chooses (PDF, email, phone).
> The two requested options are set in `pipeline/config.py` (`REQUESTED_OPTIONS`).

```json
{
  "carriers": [
    {"carrier": "Northwind Specialty", "request_channel": "portal", "contact": "Hannah Whitcombe"},
    {"carrier": "Cobalt Harbor Insurance", "request_channel": "email", "contact": "Priya Natarajan"},
    {"carrier": "Ridgeline Mutual", "request_channel": "email", "contact": "Dale Kirkpatrick"}
  ]
}
```
