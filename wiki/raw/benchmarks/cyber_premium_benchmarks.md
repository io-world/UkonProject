---
type: benchmark
immutable: true
---

# Small-business cyber premium benchmarks (published, 2025–2026)

Used to calibrate the fictional carrier indications in [[raw/sloanslake/indications/2026-10-27_northwind_indication.pdf|the Sloan's Lake carrier replies]].
These are real published figures; the carriers and their quotes are fictional.

| Benchmark | Figure | Source |
|---|---|---|
| National SMB average, $1M limit | ~$83/mo (~$999/yr) | MoneyGeek 2026, via QuoteSweep — https://www.quotesweep.com/blog/cyber-insurance-cost |
| Insureon customer average | ~$129/mo (~$1,552/yr) | Insureon 2026, via QuoteSweep (same URL) |
| Higher-risk industries incl. healthcare, $1M limit | ~$2,500–$5,000/yr | Beancount, Jul 2026 — https://beancount.io/blog/2026/07/26/cyber-insurance-small-business-coverage-gaps-guide |
| 10–50 employees, $1M–$5M revenue, $1M limit, $2,500 deductible | ~$1,740–$3,500/yr | TrustMyIP, 2026 — https://trustmyip.com/blog/cyber-insurance-cost |
| $1M revenue moderate-risk business: $1M limit / $10K deductible | $1,501/yr | AdvisorSmith study via Business Insurance — https://www.businessinsurance.com/average-costs-of-cyber-liability-insurance-studied/ |
| Same study: $500K limit / $5K deductible | $1,146/yr | same |
| Same study: $250K limit / $2.5K deductible | $739/yr | same |
| Social-engineering / wire-fraud sublimits | commonly $25K–$50K even on $1M policies | Beancount, Jul 2026 — https://beancount.io/bg/blog/2026/07/22/cyber-insurance-small-business-cost-breach-guide |
| Premium drivers | revenue tier, industry, data sensitivity (PHI/PII/cards), security controls | DataStrive — https://datastrive.com/?p=992015 |

## Calibration used for the demo client (healthcare, ~$1.95M revenue, ~13 staff)

- $1M limit lands in **$2,400–$3,200**: inside both the healthcare band and the 10–50 employee band.
- $500K limit ≈ 60% of the $1M premium; $2M limit ≈ 1.6×. (AdvisorSmith's $500K/$1M ratio is
  ~0.76, but at different deductibles; the demo uses a steeper ratio. This is an **assumption**,
  stated in the write-up, not a sourced figure.)
