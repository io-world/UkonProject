"""Read structured data out of wiki markdown files.

Raw sources live in the Obsidian vault as .md so they're visible and linkable there.
Structured ones carry their data in a single ```json fenced block; this pulls it out."""
import json
import re
from pathlib import Path

_BLOCK = re.compile(r"```json\s*\n(.*?)\n```", re.S)


def read_source(path: Path) -> dict:
    text = Path(path).read_text()
    m = _BLOCK.search(text)
    if not m:
        raise ValueError(f"{path} has no ```json block")
    return json.loads(m.group(1))


def write_source(path: Path, data: dict) -> None:
    """Replace the JSON block in place, keeping the page's frontmatter and prose."""
    text = Path(path).read_text()
    block = "```json\n" + json.dumps(data, indent=2, ensure_ascii=False) + "\n```"
    Path(path).write_text(_BLOCK.sub(lambda _: block, text, count=1))
