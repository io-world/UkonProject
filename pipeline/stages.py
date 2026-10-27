"""The five stages, and where a client is in each, derived from the data (not from a status someone sets).

UKON's brief lists four stages. Its Stage 1 ("get indications") hides two jobs with different owners and
failure modes, so the prototype splits it:

  #  key          name                      UKON stage   done when
  1  confirm      Confirm data              1 (part 1)   entity confirmed and the five fields reviewed
  2  indications  Get indications           1 (part 2)   at least one written, checked indication is in
  3  proposal     Client proposal pack      2            a pack version has been submitted (locked)
  4  agent_kit    Equip the agent           3            the pack has been sent to the client
  5  apply_bind   Present, apply, bind      4            every application answer is confirmed (binding is simulated)

Status per stage: 'done', 'attention' (something needs a person), 'active' (in progress) or 'todo'.
"""
from .indications import BASIS_KEYS

STAGES = [
    {"n": 1, "key": "confirm", "label": "Confirm data", "sub": "The five fields carriers need", "ukon": "1a"},
    {"n": 2, "key": "indications", "label": "Get indications", "sub": "Send to carriers · replies in", "ukon": "1b"},
    {"n": 3, "key": "proposal", "label": "Proposal pack", "sub": "Plain-language pack for the owner", "ukon": "2"},
    {"n": 4, "key": "agent_kit", "label": "Equip the agent", "sub": "Pitch · objections · specimens", "ukon": "3"},
    {"n": 5, "key": "apply_bind", "label": "Present, apply, bind", "sub": "Call · application · bind", "ukon": "4"},
]


def _one(conn, sql, args):
    r = conn.execute(sql, args).fetchone()
    return list(r.values())[0] if r else None


def derive(conn, cid: int) -> dict:
    entity = bool(_one(conn, "SELECT count(*) FROM entity_candidates WHERE client_id=%s AND status='confirmed'", (cid,)))
    to_review = _one(conn, "SELECT count(*) FROM fields WHERE client_id=%s AND key = ANY(%s) AND needs_review",
                     (cid, BASIS_KEYS)) + (0 if entity else 1)
    requests = _one(conn, "SELECT count(*) FROM indication_requests WHERE client_id=%s", (cid,))
    offered = _one(conn, "SELECT count(DISTINCT carrier) FROM indications WHERE client_id=%s", (cid,))
    open_actions = _one(conn, "SELECT count(*) FROM indication_actions WHERE client_id=%s AND status='open'", (cid,))
    packs = conn.execute("SELECT state FROM report_versions WHERE client_id=%s", (cid,)).fetchall()
    states = {p["state"] for p in packs}
    calls = _one(conn, "SELECT count(*) FROM intake_calls WHERE client_id=%s", (cid,))
    app_total = _one(conn, "SELECT count(*) FROM application_answers WHERE client_id=%s", (cid,))
    app_open = _one(conn, "SELECT count(*) FROM application_answers WHERE client_id=%s AND status<>'confirmed'", (cid,))

    s = {}
    s["confirm"] = ("done", "Five fields reviewed") if to_review == 0 else ("attention", f"{to_review} to review")
    if offered and not open_actions:
        s["indications"] = ("done", f"{offered} carrier{'s' if offered != 1 else ''} offering")
    elif offered:
        s["indications"] = ("attention", f"{offered} offering · {open_actions} to act on")
    elif requests:
        s["indications"] = ("active", "Waiting on carriers")
    else:
        s["indications"] = ("todo", "Not sent yet")
    if states & {"submitted", "sent"}:
        s["proposal"] = ("done", "Submitted")
    elif packs:
        s["proposal"] = ("active", "Draft")
    else:
        s["proposal"] = ("todo", "Needs indications")
    if "sent" in states:
        s["agent_kit"] = ("done", "Pack sent to client")
    elif packs:
        s["agent_kit"] = ("active", "Ready to prepare")
    else:
        s["agent_kit"] = ("todo", "Needs the pack")
    if app_total and not app_open:
        s["apply_bind"] = ("done", "Application ready to sign")
    elif calls:
        s["apply_bind"] = ("active", f"{calls} call{'s' if calls != 1 else ''} · {app_open} answers to confirm")
    else:
        s["apply_bind"] = ("todo", "No call yet")

    out = [st | {"status": s[st["key"]][0], "note": s[st["key"]][1]} for st in STAGES]
    current = next((st["key"] for st in out if st["status"] != "done"), "apply_bind")
    return {"stages": out, "current": current}
