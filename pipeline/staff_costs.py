"""Staff cost and payroll figures: plain arithmetic on database fields. No AI anywhere in here.

The same formulas work for any industry; only the wage benchmark page changes (wiki/raw/benchmarks/wages_<naics>.md).
"""
import re

from .config import RAW
from .sources import read_source

FTE_HOURS = 2080        # one full-time equivalent: 40 hours × 52 weeks (the standard definition)
PAY_RUNS_PER_YEAR = 26  # paid every two weeks, the most common US pay frequency; to confirm with the owner


def wage_benchmark(industry_text: str | None) -> dict | None:
    """Find the wage page for the client's industry by NAICS code ('... (NAICS 621210)' → wages_621210.md)."""
    m = re.search(r"\b(\d{4,6})\b", industry_text or "")
    if not m:
        return None
    code = m.group(1)
    for n in range(len(code), 3, -1):           # 621210 → 62121 → 6212
        for page in (RAW / "benchmarks").glob(f"wages_{code[:n]}*.md"):
            return read_source(page) | {"wiki": f"raw/benchmarks/{page.stem}"}
    return None


def compute(staff: float, avg_pay: float) -> dict:
    staff, avg_pay = float(staff), float(avg_pay)
    annual = staff * avg_pay
    return {
        "staff": int(staff), "avg_pay": avg_pay,
        "annual": round(annual, -2),
        "per_day": round(annual / 365, -1),                       # calendar day, same basis as operating costs
        "per_work_hour": round(annual / FTE_HOURS),               # whole team, per working hour
        "hourly_avg": round(avg_pay / FTE_HOURS, 2),              # one person's average hourly wage
        "paycheck": round(avg_pay / PAY_RUNS_PER_YEAR, -1),       # one person's pay for one pay run
        "pay_run": round(annual / PAY_RUNS_PER_YEAR, -2),         # the whole team's pay for one pay run
        "fte_hours": FTE_HOURS, "pay_runs": PAY_RUNS_PER_YEAR,
    }
