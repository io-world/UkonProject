---
type: benchmark
immutable: true
---

# Dental practice overhead (for the "what a day closed costs" figure)

| Benchmark | Figure | Source |
|---|---|---|
| Typical overhead, general dental practice | 60–65% of collections | American Dental Association, as cited by Overjet (Sep 2025) — https://www.overjet.com/blog/average-dental-office-overhead-complete-breakdown-by-practice-size |
| Same range, corroborating | 60–65% of collections | NetSuite — https://netsuite.com/portal/resource/articles/financial-management/dental-office-overhead-percentages.shtml |

## How the pack uses this

Operating costs (OPEX) = annual revenue (the database field) × 60% to 65%, divided by 365 for a per-day figure.
Calendar days, not working days: rent, salaries and loans keep running on days the office is closed, and it
avoids assuming a schedule we don't know. The figure is computed in code; the AI never writes it.

## Limits

- Secondhand ADA citation; the primary ADA HPI table isn't public in text form.
- An industry average, not this practice's books. The owner's accountant can give the real number.
- Says nothing about what a policy pays. Coverage questions go to a licensed person.
