---
type: benchmark
immutable: true
---

# Dental industry benchmarks (NAICS 6212 — Offices of Dentists)

Used by `pipeline/estimators.py` for revenue estimation when the agency has no revenue on file.

| Benchmark | Figure | Source |
|---|---|---|
| Total revenue, offices of dentists (employer firms), 2022 | $157,906M | U.S. Census Bureau Service Annual Survey, via FRED series REVEF6212ALLEST — https://fred.stlouisfed.org/data/REVEF6212ALLEST |
| Employment, offices of dentists, 2022 | 1,034.9K | BLS, via FRED — https://fred.stlouisfed.org/data/IPURN62121W200000000 |
| **Derived revenue per employee, 2022** | **≈ $152,600** | 157,906M ÷ 1,034.9K |
| Average general-practice gross billings per dentist, 2025 | $965,660 | ADA Health Policy Institute, as cited by Stealth Agents (Sep 2026) — https://stealthagents.com/research/dental-practice-administrative-staffing-costs-2026 |
| Share of dental offices carrying $1M cyber | ~80% | Florida Dental Association Services blog — https://blog.floridadental.org/2025/07/17/hackers-dont-care-youre-a-dentist-why-cyber-insurance-matters-now/ |
| Rule of thumb for minimum limit | ~2× monthly revenue | same |

## Notes

- Revenue-per-employee is a 2022 figure; the estimator does not inflate it, and says so.
  That keeps the estimate conservative and the method auditable.
- Gross billings are not collections. The per-dentist method is treated as an upper signal.
