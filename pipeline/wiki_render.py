"""Render a client's wiki page from the database. The page is a view, not a source:
it is regenerated whenever a field changes, so wiki and DB can't drift apart."""
from datetime import datetime, timezone

import re

from .config import WIKI

_SRC = re.compile(r"^(\S+?)\.md(?:\s+\((.*)\))?$")


def cite(source: str) -> str:
    """'sloanslake/ams_export.md (SIC 8021)' -> '[[raw/sloanslake/ams_export|ams_export]] (SIC 8021)'
    so citations are clickable in Obsidian and show up in graph view."""
    m = _SRC.match(source.strip())
    if not m:
        return source
    path, note = m.groups()
    link = f"[[raw/{path}|{path.split('/')[-1]}]]"
    return f"{link} ({note})" if note else link


def _fmt(field):
    v = field["current_value"]
    if field["kind"] == "money" and isinstance(v, (int, float)):
        return f"${v:,.0f}"
    return str(v)


def _fmt_num(kind, x):
    if x is None:
        return "—"
    return f"${float(x):,.0f}" if kind == "money" else f"{float(x):,.0f}"


def render_client(conn, client_id: int) -> str:
    c = conn.execute("SELECT * FROM clients WHERE id=%s", (client_id,)).fetchone()
    ent = conn.execute("""SELECT * FROM entity_candidates WHERE client_id=%s ORDER BY match_score DESC""",
                       (client_id,)).fetchall()
    fields = conn.execute("""SELECT f.*, u.name AS updated_by_name FROM fields f
                             LEFT JOIN users u ON u.id=f.updated_by
                             WHERE client_id=%s AND kind <> 'benchmark' ORDER BY id""", (client_id,)).fetchall()
    changes = conn.execute("""SELECT fc.*, f.label, u.name FROM field_changes fc
                              JOIN fields f ON f.id=fc.field_id JOIN users u ON u.id=fc.actor_id
                              WHERE f.client_id=%s ORDER BY fc.changed_at""", (client_id,)).fetchall()
    legal = next((e["legal_name"] for e in ent if e["status"] == "confirmed"), None)

    out = [
        "---",
        "type: client",
        "generated: true",
        f"client_id: {c['id']}",
        f"legal_name: \"{legal or 'UNCONFIRMED'}\"",
        "naics: \"621210\"",
        f"renewal_date: {c['renewal_date']}",
        f"last_rendered: {datetime.now(timezone.utc).isoformat(timespec='seconds')}",
        "---", "",
        f"# {c['display_name']}", "",
        f"Agency: {c['agency']} · Renewal: **{c['renewal_date']}** · Stage: `{c['stage']}` · "
        "Industry: [[621210-dental-offices]]", "",
        "> [!warning] Generated page — do not edit in Obsidian",
        "> Rendered from the database on every change; edits here are overwritten. Change values in the app",
        "> (logged with your name). Annotate in [[621210-dental-offices|the industry page]] or the raw sources instead.", "",
        "## Entity resolution", "",
    ]
    for e in ent:
        sig = dict(e["signals"])
        src = sig.pop("source", None)
        registry = sig.pop("registry", None)
        out.append(f"- **{e['legal_name']}** ({e['state']}) — match {float(e['match_score']):.0%} — `{e['status']}` — "
                   + ", ".join(f"{k} {v:.0%}" for k, v in sig.items()) + (f" — registry: {registry}" if registry else "")
                   + (f" — {cite(src)}" if src else ""))
    out += ["", "## Indication fields", ""]
    breakdown = next((f["current_value"] for f in fields if f["key"] == "exposure_breakdown"), None)
    for f in fields:
        if f["key"] == "exposure_breakdown":
            continue
        out.append(f"### {f['label']}")
        if f["key"] == "exposure_score" and breakdown:
            for fac in breakdown["factors"]:
                out.append(f"  - {fac['label']}: {fac['points']:+}")
            out.append(f"  - Unknown until the call: {', '.join(breakdown['unknown_controls'])}")
        out.append(f"- Value: **{_fmt(f)}**" + (f" (AI recommended {f['ai_value']})" if f["ai_value"] != f["current_value"] else ""))
        if f["ai_low"] is not None:
            out.append(f"- Range: {_fmt_num(f['kind'], f['ai_low'])} – {_fmt_num(f['kind'], f['ai_high'])}")
        out.append(f"- Confidence: {f['confidence']}" + (" · **needs review**" if f["needs_review"] else ""))
        out.append(f"- Method: {f['method']}")
        out.append("- Sources: " + (", ".join(cite(s) for s in (f["sources"] or [])) or "none (estimate — confirm on the call)"))
        if f.get("updated_by_name"):
            out.append(f"- Last changed by: {f['updated_by_name']}")
        out.append("")
    if changes:
        out += ["## Human changes", ""]
        for ch in changes:
            out.append(f"- {ch['changed_at']:%Y-%m-%d %H:%M} — {ch['name']} changed **{ch['label']}** "
                       f"{ch['old_value']} → {ch['new_value']}" + (f" — \"{ch['reason']}\"" if ch["reason"] else ""))
        out.append("")
    text = "\n".join(out)
    (WIKI / "clients").mkdir(exist_ok=True)
    (WIKI / "clients" / f"{c['slug']}.md").write_text(text)
    return text


def log(entry: str):
    stamp = datetime.now().strftime("%Y-%m-%d")
    with open(WIKI / "log.md", "a") as fh:
        fh.write(f"## [{stamp}] {entry}\n")
