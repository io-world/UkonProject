---
type: carrier-reference
title: "Policy specimen locations"
format: json-in-markdown
---

# Policy specimen locations

> FICTIONAL specimen-form locations. In production, AI locates these in the real carrier PDF and every reference must resolve to actual text on the cited page, or it is dropped.

Pipeline code reads the JSON block below. Edit values here and re-run the pipeline; keep it valid JSON.

```json
{
  "Northwind Specialty": {
    "form": "NWS-CY-100 (06/25)",
    "items": [
      {
        "topic": "Funds transfer / social engineering sublimit",
        "section": "Sec. IV.C",
        "page": 7
      },
      {
        "topic": "Ransomware / cyber extortion",
        "section": "Insuring Agreement B",
        "page": 3
      },
      {
        "topic": "Business interruption waiting period",
        "section": "Sec. II.D",
        "page": 5
      },
      {
        "topic": "MFA warranty / condition",
        "section": "Sec. VII.4",
        "page": 14
      },
      {
        "topic": "Regulatory fines (HIPAA)",
        "section": "Insuring Agreement E",
        "page": 4
      }
    ]
  },
  "Cobalt Harbor Insurance": {
    "form": "CHI-CYBR-2025",
    "items": [
      {
        "topic": "Funds transfer / social engineering sublimit",
        "section": "Endorsement 3",
        "page": 22
      },
      {
        "topic": "Ransomware / cyber extortion",
        "section": "Coverage 2",
        "page": 4
      },
      {
        "topic": "Business interruption waiting period",
        "section": "Definitions — Waiting Period",
        "page": 11
      },
      {
        "topic": "MFA warranty / condition",
        "section": "Conditions 9",
        "page": 17
      },
      {
        "topic": "Regulatory fines (HIPAA)",
        "section": "Coverage 5",
        "page": 6
      }
    ]
  },
  "Ridgeline Mutual": {
    "form": "RM-CYB-4 (01/26)",
    "items": [
      {
        "topic": "Funds transfer / social engineering sublimit",
        "section": "Part C",
        "page": 9
      },
      {
        "topic": "Ransomware sublimit",
        "section": "Schedule — Sublimits",
        "page": 2
      },
      {
        "topic": "Business interruption waiting period",
        "section": "Part D.3",
        "page": 10
      },
      {
        "topic": "EDR condition",
        "section": "Part H.2",
        "page": 15
      },
      {
        "topic": "Regulatory fines (HIPAA)",
        "section": "Part E",
        "page": 8
      }
    ]
  }
}
```
