"""Shared configuration. Every threshold that drives a human-review decision lives here,
so the panel (and engineers) can see exactly where the lines are drawn."""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WIKI = ROOT / "wiki"
RAW = WIKI / "raw"

# The demo client. Real public data lives in wiki/raw/<slug>/; agency records, calls and carrier replies are simulated.
CLIENT_SLUG = "sloanslake"

# Bump when db/schema.sql changes; the API refuses to run against an older database (run pipeline.run_all).
SCHEMA_VERSION = "2026-10-26c"


def _load_dotenv(path: Path) -> None:
    """Minimal .env loader (no dependency). Real environment variables win."""
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, value = line.partition("=")
            if value.strip():
                os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


_load_dotenv(ROOT / ".env")

# Local Postgres whose data directory lives in db/pgdata (see scripts/db.sh). Port 5433 so it
# never collides with another Postgres you may already run on 5432.
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://ukon:ukon@localhost:5433/ukon")

# LLM (optional). Without a key, the pipeline uses cached outputs stored in wiki/raw/_cache.
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
ANTHROPIC_MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-5-5")

# --- Review-by-exception thresholds ---------------------------------------
ENTITY_AUTO_SUGGEST = 0.85        # above this, the candidate is pre-selected for the reviewer
SIGNAL_AGREEMENT_MEDIUM = 0.20    # signals within ±20% of the estimate → medium confidence
SIGNAL_MAX_AGE_MONTHS = 24        # older signals are shown but not used for the estimate

# --- Indication drift ------------------------------------------------------
# If an agent moves revenue more than this from what the carrier priced on,
# the report shows "indication needs refresh" instead of recalculating a premium.
REVENUE_DRIFT_TOLERANCE = 0.15

# --- Benchmarks (sourced in wiki/raw/benchmarks) ---------------------------
DENTAL_REVENUE_PER_EMPLOYEE = 152_600   # Census SAS 2022 revenue / BLS 2022 employment
DENTAL_BILLINGS_PER_DENTIST = 965_660   # ADA HPI 2025 general practice gross billings

# --- Stage 1: the agent <-> carrier exchange --------------------------------
# The two options requested from every carrier. `tier` keys the client pack columns.
REQUESTED_OPTIONS = [
    {"tier": "recommended", "label": "$1M / $10K", "limit": 1_000_000, "deductible": 10_000},
    {"tier": "premier", "label": "$2M / $25K", "limit": 2_000_000, "deductible": 25_000},
]
INDICATION_EXPIRY_WARN_DAYS = 14   # warn the agent this many days before an indication lapses

# Carrier subjectivity -> intake/application answer that shows whether it's met (keyword match, no model).
CONDITION_KEYS = [
    (("remote",), "mfa_remote"),
    (("mfa", "multi-factor"), "mfa_email"),
    (("backup",), "backups"),
    (("edr", "endpoint detection"), "edr"),
    (("phishing",), "phishing_training"),
]
