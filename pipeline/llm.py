"""Optional Claude access. Every caller has a cached fallback, so the demo runs
offline; with ANTHROPIC_API_KEY set, outputs are generated live."""
import json
import re

from . import config

_client = None


def available() -> bool:
    return bool(config.ANTHROPIC_API_KEY)


def client():
    global _client
    if _client is None:
        import anthropic
        _client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
    return _client


def complete_json(system: str, user: str, max_tokens: int = 2500) -> dict | None:
    """Ask for a single JSON object. Returns None if no key or the output won't parse."""
    if not available():
        return None
    msg = client().messages.create(
        model=config.ANTHROPIC_MODEL, max_tokens=max_tokens, system=system,
        messages=[{"role": "user", "content": user}],
    )
    text = "".join(b.text for b in msg.content if getattr(b, "type", "") == "text")
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError:
        return None
