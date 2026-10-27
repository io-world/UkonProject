"""Deterministic estimators. No LLM in this file — every number here is reproducible
and every method is written out in plain words so a human reviewer can check it.

The LLM's job in Stage 1 is extraction (reading messy sources into signals).
Turning signals into numbers happens here."""
from dataclasses import dataclass, field
from datetime import date

from . import config


@dataclass
class Signal:
    value: float
    source: str          # raw file path, e.g. "sloanslake/website.md"
    as_of: date
    note: str = ""
    estimated: bool = False   # derived from an assumption, not a direct count


@dataclass
class Estimate:
    value: float
    low: float
    high: float
    confidence: str      # high | medium | low
    method: str
    sources: list = field(default_factory=list)
    conflict: str | None = None
    needs_review: bool = False


def _months_between(a: date, b: date) -> int:
    return (b.year - a.year) * 12 + (b.month - a.month)


def _round_to(x: float, step: int) -> int:
    return int(round(x / step) * step)


def estimate_employees(signals: list[Signal], today: date, hiring: bool = False) -> Estimate:
    """Most recent direct count wins; range spans recent signals; old signals are context only."""
    recent = [s for s in signals if _months_between(s.as_of, today) <= config.SIGNAL_MAX_AGE_MONTHS]
    used = recent or signals
    latest = max(used, key=lambda s: s.as_of)
    lo = min(s.value for s in used)
    hi = max(s.value for s in used) + (1 if hiring else 0)
    spread = (max(s.value for s in used) - lo) / latest.value
    confidence = "high" if spread == 0 and len(used) > 1 else (
        "medium" if spread <= config.SIGNAL_AGREEMENT_MEDIUM else "low")
    if all(s.estimated for s in used):
        confidence = "low"
    conflict = None
    if spread > 0:
        conflict = "; ".join(f"{s.source} says {int(s.value)} ({s.as_of.isoformat()})" for s in used)
    ignored = [s for s in signals if s not in used]
    if all(s.estimated for s in used):
        lo, hi = round(latest.value * 0.75), round(latest.value * 1.25) + (1 if hiring else 0)
        return Estimate(latest.value, lo, hi, "low", f"{latest.note} Range ±25%.",
                        sources=[s.source for s in signals], needs_review=True)
    method = (f"Most recent direct count ({latest.source}, {latest.as_of.isoformat()}). "
              f"Range spans signals from the last {config.SIGNAL_MAX_AGE_MONTHS} months"
              + (", +1 for an open job posting" if hiring else "") + ". "
              + (f"Ignored as stale: {', '.join(s.source for s in ignored)}." if ignored else ""))
    return Estimate(latest.value, lo, hi, confidence, method,
                    sources=[s.source for s in signals], conflict=conflict,
                    needs_review=confidence == "low")


def estimate_revenue(agency_revenue: float | None, employees: float, dentists: int | None,
                     slug: str = config.CLIENT_SLUG, employees_estimated: bool = False) -> Estimate:
    """Waterfall: agency record → public filing → benchmark estimate.
    For a private dental practice with no revenue on file, two independent benchmark
    methods are computed and must roughly agree."""
    if agency_revenue:
        return Estimate(agency_revenue, agency_revenue, agency_revenue, "high",
                        "Agency management system record (rating basis on an existing policy).",
                        sources=[f"{slug}/ams_export.md"])

    by_staff = employees * config.DENTAL_REVENUE_PER_EMPLOYEE
    signals = [by_staff]
    method = (f"No revenue on file at the agency; private entity, no public filings. "
              f"Method A: {int(employees)} staff × ${config.DENTAL_REVENUE_PER_EMPLOYEE:,} revenue per employee "
              f"(Census 2022 ÷ BLS 2022) = ${by_staff:,.0f}.")
    if dentists:
        by_dentist = dentists * config.DENTAL_BILLINGS_PER_DENTIST
        signals.append(by_dentist)
        method += (f" Method B: {dentists} dentists × ${config.DENTAL_BILLINGS_PER_DENTIST:,} average gross billings "
                   f"(ADA 2025) = ${by_dentist:,.0f}.")
    mid = sum(signals) / len(signals)
    spread = (max(signals) - min(signals)) / mid
    confidence = "medium" if len(signals) > 1 and spread <= config.SIGNAL_AGREEMENT_MEDIUM else "low"
    if employees_estimated:
        confidence = "low"
        method += " Method A rests on an estimated headcount, so the two methods aren't independent."
    method += ((f" Methods agree within {spread:.0%}" if spread <= config.SIGNAL_AGREEMENT_MEDIUM
                else f" Methods differ by {spread:.0%}, so confidence is low")
               + "; estimate is their average, rounded to $50K. Confirm with the client before binding.")
    return Estimate(_round_to(mid, 50_000), _round_to(min(signals) * 0.9, 50_000),
                    _round_to(max(signals) * 1.1, 50_000), confidence, method,
                    sources=["benchmarks/dental_industry_benchmarks.md", f"{slug}/website.md",
                             f"{slug}/ams_export.md"],
                    needs_review=True)  # estimated revenue always gets a human look


# ---------------------------------------------------------------------------
# Exposure score — a rough, explainable proxy used instead of a security scan.
# It is NOT a security rating. It tells a non-technical owner how many "doors"
# they have and how easy it is to impersonate them. Agents can move it.
# ---------------------------------------------------------------------------
EXPOSURE_FACTORS = {
    "data_sensitivity": {"phi": 25, "pii": 15, "cards_only": 10, "minimal": 3},
    "per_email_account": 1.2, "email_cap": 20,
    "dmarc": {"none": 10, "quarantine": 5, "reject": 0, "missing": 12},
    "spf": {"~all": 3, "-all": 0, "?all": 6, "missing": 8},
    "online_payments": 7,
    "records_over_5000": 10,
}
CONTROL_CREDITS = {"mfa_email": -12, "tested_backups": -8, "edr": -6, "payment_verify": -5}

# Intake answer key -> exposure control. Only a clear "yes" earns the credit;
# partial, unknown, or still-open answers earn nothing.
ANSWER_TO_CONTROL = {"mfa_email": "mfa_email", "backups": "tested_backups", "edr": "edr",
                     "payment_verify": "payment_verify"}


def controls_from_answers(answers: list[dict]) -> dict:
    return {ANSWER_TO_CONTROL[a["question_key"]]: True for a in answers
            if a["question_key"] in ANSWER_TO_CONTROL and a["normalized"] == "yes"
            and a.get("status", "prefilled") in ("prefilled", "confirmed")}   # hedged "yes" earns nothing


CONTROL_LABELS = {"mfa_email": "Phone codes on every email login (from intake)",
                  "tested_backups": "Tested, offline backups (from intake)",
                  "edr": "Attack-monitoring software on every computer (from intake)",
                  "payment_verify": "Calls to confirm payment changes (from intake)"}


def exposure_score(data_class: str, email_accounts: int, dmarc: str, spf: str,
                   online_payments: bool, records_est: int, controls: dict | None = None) -> dict:
    f = EXPOSURE_FACTORS
    parts = [
        ("Handles patient health information", f["data_sensitivity"][data_class]),
        (f"{email_accounts} email accounts that could be phished",
         min(f["email_cap"], round(email_accounts * f["per_email_account"], 1))),
        ("No email spoofing protection (DMARC) record" if dmarc == "missing"
         else f"Email spoofing protection (DMARC) set to '{dmarc}'", f["dmarc"][dmarc]),
        (f"Sender policy (SPF) ends in '{spf}'", f["spf"][spf]),
        ("Takes payments online", f["online_payments"] if online_payments else 0),
        ("Holds more than 5,000 records", f["records_over_5000"] if records_est > 5000 else 0),
    ]
    for key, credit in CONTROL_CREDITS.items():
        if controls and controls.get(key):
            parts.append((CONTROL_LABELS[key], credit))
    total = max(0, min(100, round(sum(p for _, p in parts))))
    band = "Elevated" if total >= 65 else "Moderate" if total >= 40 else "Lower"
    return {"score": total, "band": band, "factors": [{"label": l, "points": p} for l, p in parts],
            "unknown_controls": [k for k in CONTROL_CREDITS if not (controls or {}).get(k)]}


def revenue_drift(current_revenue: float, basis_revenue: float) -> dict:
    drift = (current_revenue - basis_revenue) / basis_revenue
    return {"drift": round(drift, 3), "needs_refresh": abs(drift) > config.REVENUE_DRIFT_TOLERANCE,
            "tolerance": config.REVENUE_DRIFT_TOLERANCE}
