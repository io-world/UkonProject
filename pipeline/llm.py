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


def complete_json(system: str, user: str, max_tokens: int = 2500, label: str = "AI step") -> dict | None:
    """Ask for a single JSON object. Returns None if no key or the output won't parse; the caller then
    falls back to its cached output. A fallback is printed with the reason, so it's never silent."""
    if not available():
        return None
    import sys
    msg = client().messages.create(
        model=config.ANTHROPIC_MODEL, max_tokens=max_tokens, system=system,
        messages=[{"role": "user", "content": user}],
    )
    text = "".join(b.text for b in msg.content if getattr(b, "type", "") == "text")
    m = re.search(r"\{.*\}", text, re.S)
    why = None
    if msg.stop_reason == "max_tokens":
        why = f"the answer was cut off at {max_tokens} tokens"
    elif not m:
        why = "the answer had no JSON in it"
    else:
        try:
            return json.loads(m.group(0))
        except json.JSONDecodeError as e:
            why = f"the JSON didn't parse ({e.msg})"
    print(f"  note: live {label} unusable: {why}; using the cached output", file=sys.stderr)
    return None
