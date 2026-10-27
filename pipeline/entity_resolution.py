"""Stage 1 entity resolution. Scores candidates on several attributes together,
because name similarity alone is how you end up quoting the wrong company.
In the MVP every match is confirmed by a human; the score only pre-selects."""
import re
from difflib import SequenceMatcher

WEIGHTS = {"name": 0.25, "state": 0.20, "address": 0.30, "domain": 0.25}
_SUFFIXES = r"\b(pllc|llc|inc|pc|corp|co|ltd|group|associates)\b"


def _norm(s: str) -> str:
    s = re.sub(r"[^a-z0-9 ]", " ", (s or "").lower())
    s = re.sub(_SUFFIXES, " ", s)
    return re.sub(r"\s+", " ", s).strip()


def _addr_norm(s: str) -> str:
    s = (s or "").lower().replace("suite", "ste").replace("street", "st")
    return re.sub(r"[^a-z0-9]", "", s)


def score(ams: dict, cand: dict) -> dict:
    names = [cand.get("legal_name", ""), cand.get("dba") or ""]
    name_sim = max(SequenceMatcher(None, _norm(ams["account_name"]), _norm(n)).ratio() for n in names if n)
    ams_state = ams["mailing_address"].split(",")[-1].split()[0]
    signals = {
        "name": round(name_sim, 2),
        "state": 1.0 if cand.get("state") == ams_state else 0.0,
        "address": 1.0 if _addr_norm(cand.get("address", ""))[:18] == _addr_norm(ams["mailing_address"])[:18] else 0.0,
        "domain": 1.0 if cand.get("domain") and cand["domain"] == ams.get("contact_email_domain") else 0.0,
    }
    total = sum(WEIGHTS[k] * v for k, v in signals.items())
    # A perfect name + address match on a delinquent or dissolved entity is the classic wrong-company quote:
    # same owner, same office, but not the entity that should be the named insured.
    status = (cand.get("status") or "").lower()
    if status:
        signals["status"] = 1.0 if status.startswith(("good standing", "active")) else 0.0
        if not signals["status"]:
            total *= 0.5
    return {"match_score": round(total, 3), "signals": signals}
