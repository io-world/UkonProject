"""Stage 3/4 prose (client pack, agent kit). The LLM writes stories and talking points from the wiki.
It is forbidden from writing numbers: any digit outside an approved {placeholder}
fails validation, and the renderer fills placeholders from the database."""
import json
import re

from .sources import read_source
from . import llm
from .config import RAW, WIKI

PLACEHOLDERS = {"business_name", "owner_last", "city", "email_accounts", "dentists", "staff"}
BLOCK_KEYS = ["why_it_matters", "scenarios", "exposure_explainer", "next_steps",
              "agent_pitch", "objection_tailoring"]

SYSTEM = """You write plain-language cyber insurance material for small business owners
and the insurance agents who serve them. Reading level: grades 6 to 8. Warm, concrete, no jargon.

HARD RULES
- Never write a number, price, percentage, limit, or date. No digits at all.
- Where a count is needed, use only these placeholders: {business_name} {owner_last} {city}
  {email_accounts} {dentists} {staff}. The system fills them from the database.
- Never describe what the policy covers or promise a claim will be paid. Coverage wording
  comes from an approved library, not from you.
- Never imply the price is final. These are estimates.
- Objection answers must tailor the approved answer you are given; do not invent new claims.
- The client facts include intake_so_far: what the owner already told the agent on intake calls.
  Acknowledge that conversation in next_steps and agent_pitch; refer to open items in general terms.
  The intake can be incomplete; never wait on it or say the proposal depends on it.

Return ONE JSON object with keys:
why_it_matters (string, 2 sentences),
scenarios (array of 3 objects: key, title, story — key is one of ransomware, bec, breach),
exposure_explainer (string, 2-3 sentences),
next_steps (string, 2 sentences),
agent_pitch (string, about 60 seconds spoken),
objection_tailoring (object keyed by: too_small, it_handles_it, too_expensive, never_hacked, bop_covers — each 1-2 sentences)."""


def find_violations(obj) -> list[str]:
    """Return any text fragments containing digits outside placeholders, or unknown placeholders."""
    bad = []
    def walk(x):
        if isinstance(x, str):
            stripped = re.sub(r"\{(\w+)\}", lambda m: "" if m.group(1) in PLACEHOLDERS else "§BADPH§", x)
            if re.search(r"\d", stripped) or "§BADPH§" in stripped:
                bad.append(x[:80])
        elif isinstance(x, dict):
            for v in x.values():
                walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)
    walk(obj)
    return bad


def _cached(slug: str) -> dict:
    return read_source(RAW / "_cache" / f"narrative_{slug}.md")


def generate(slug: str, client_facts: dict) -> tuple[dict, str]:
    """Returns (narrative, provenance). Provenance is 'live' or 'cached'."""
    industry_page = (WIKI / "industries" / "621210-dental-offices.md").read_text()
    user = (f"Industry page (source of truth for scenarios and approved objection answers):\n\n{industry_page}\n\n"
            f"Client facts (do not restate numbers; use placeholders):\n{json.dumps(client_facts, indent=2)}")
    for _ in range(2):  # one retry if the guard trips
        out = llm.complete_json(SYSTEM, user)
        if out is None:
            break
        if all(k in out for k in BLOCK_KEYS) and not find_violations(out):
            return out, "live"
        user += "\n\nYour previous answer contained digits or was missing keys. Remove every digit."
    cached = _cached(slug)
    assert not find_violations(cached), "cached narrative violates the no-numbers rule"
    return cached, "cached"


def fill(text: str, values: dict) -> str:
    return re.sub(r"\{(\w+)\}", lambda m: str(values.get(m.group(1), m.group(0))), text)
