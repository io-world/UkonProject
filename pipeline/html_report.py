"""Render a report snapshot as one standalone HTML file (no server, no JavaScript).

Written to reports/<slug>/current.html for the working draft and reports/<slug>/v<N>.html for
each submitted version. Every figure comes from the snapshot, which comes from the database."""
from html import escape
from datetime import datetime

TIER_NAME = {"essential": "Essential", "recommended": "Recommended", "premier": "Premier"}
PLAIN_CONTROL = {"mfa_email": "phone codes on email logins", "tested_backups": "tested backups",
                 "edr": "attack-monitoring software", "payment_verify": "payment-change call-backs"}


def _m(n):
    return "—" if n is None else f"${float(n):,.0f}"


def _short(n):
    if n is None:
        return "—"
    n = float(n)
    if n >= 1e6:
        return f"${n / 1e6:.2f}".rstrip("0").rstrip(".") + "M"
    if n >= 1e3:
        return f"${round(n / 1e3):,}K"
    return _m(n)


def _e(s):
    return escape(str(s)) if s is not None else ""


CSS = """
:root{--ink:#16202e;--ink2:#3c4a5c;--muted:#6b7788;--line:#e3e0d8;--paper:#fbfaf7;--accent:#0f6b62;--accent2:#e7f2f0;
--amber:#b26a00;--amberbg:#fff4e0;--green:#2f7d4b;--greenbg:#e9f5ee;--red:#b3372f;--redbg:#fdecea}
*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:15px/1.55 Inter,system-ui,-apple-system,sans-serif}
.page{max-width:920px;margin:32px auto;background:#fff;border:1px solid var(--line);border-radius:14px;padding:40px 46px}
h1,h2{font-family:'Source Serif 4',Georgia,serif;font-weight:600}h1{font-size:32px;margin:4px 0 10px}
h2{font-size:21px;margin:34px 0 12px;padding-top:20px;border-top:1px solid #eeebe4}h4{margin:0 0 6px;font-size:14.5px}
p{margin:0 0 8px}.kicker{text-transform:uppercase;letter-spacing:.08em;font-size:11px;color:var(--accent);font-weight:700}
.lede{font-size:17px;color:var(--ink2)}.muted{color:var(--muted)}.small{font-size:12.5px}
.banner{background:var(--amberbg);color:#6d4300;border:1px solid #f1d9a8;border-radius:8px;padding:9px 12px;font-size:13px;margin:12px 0}
.tiers{display:grid;grid-template-columns:repeat(2,1fr);gap:12px}.tier{border:1px solid var(--line);border-radius:12px;padding:16px;position:relative}
.tier.rec{border:2px solid var(--accent);background:linear-gradient(180deg,var(--accent2),#fff 45%)}.tier.off{background:#f3f1ec}
.flag{position:absolute;top:-10px;left:14px;background:var(--accent);color:#fff;font-size:11px;font-weight:600;padding:2px 9px;border-radius:999px}
.price{font:600 28px 'Source Serif 4',Georgia,serif}.price span{font:500 12px Inter,sans-serif;color:var(--muted)}
dl{display:grid;grid-template-columns:1fr auto;gap:4px 8px;margin:10px 0 0;font-size:13px}dt{color:var(--ink2)}dd{margin:0;font-weight:600;text-align:right}
dd.warn{color:var(--amber)}.grid3{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}
.box{background:var(--paper);border-radius:12px;padding:14px}.box p{font-size:13.5px;color:var(--ink2)}
.cost{border-top:1px dashed var(--line);padding-top:8px;margin-top:6px}.cost b{font:600 18px 'Source Serif 4',Georgia,serif;display:block}
.cost span{font-size:11.5px;color:var(--muted)}
.meter{position:relative;display:grid;grid-template-columns:40fr 25fr 35fr;height:12px;max-width:560px;margin:8px 0 4px}
.meter i:nth-child(1){background:#cfe6d8;border-radius:999px 0 0 999px}.meter i:nth-child(2){background:#f6dea9}.meter i:nth-child(3){background:#f1b8b2;border-radius:0 999px 999px 0}
.pin{position:absolute;top:-5px;width:4px;height:22px;background:var(--ink);border-radius:2px;transform:translateX(-2px)}
.mlabels{display:grid;grid-template-columns:40fr 25fr 35fr;max-width:560px;font-size:11px;color:var(--muted)}
.intake{list-style:none;padding:0;margin:0;display:grid;gap:6px}.intake li{display:flex;justify-content:space-between;gap:12px;border-bottom:1px solid #eeebe4;padding:7px 0}
.st{font-size:12px;font-weight:600;padding:2px 9px;border-radius:999px;white-space:nowrap}
.st.ok{background:var(--greenbg);color:var(--green)}.st.gap{background:var(--redbg);color:var(--red)}
.st.partial,.st.open{background:var(--amberbg);color:var(--amber)}
.news{display:grid;gap:12px}.news .box h4 a{color:var(--ink);text-decoration:none}.news .src{font-size:12px;color:var(--muted)}
.news .yours{font-size:13px;color:var(--accent);margin-top:4px}
.cov{display:grid;grid-template-columns:1fr 1fr;gap:10px}.cov div{border-left:3px solid var(--accent);padding:4px 12px}
.cov div.f{border-left-color:var(--amber)}.cov p{font-size:13.5px;color:var(--ink2)}
.faq{display:grid;grid-template-columns:1fr 1fr;gap:14px}.faq p{font-size:13.5px;color:var(--ink2)}
footer{margin-top:30px;padding-top:12px;border-top:1px solid #eeebe4;font-size:12px;color:var(--muted)}
@media(max-width:760px){.page{margin:0;border:0;border-radius:0;padding:22px 16px}.tiers,.grid3,.cov,.faq{grid-template-columns:1fr}}
@media print{body{background:#fff}.page{border:0;margin:0;padding:0}}
"""


def render(s: dict, version: dict, client_view: bool = True) -> str:
    n = s["narrative"]
    opts = s.get("options", {})
    carrier = next((c for c in s["carriers"] if c["carrier"] == s["selected_carrier"]), {})
    intake = s.get("intake", {})
    out = []
    w = out.append

    if not client_view:
        w('<div class="banner"><b>Working draft (not sent).</b> This file is overwritten on every change. '
          'Submitted versions are saved as v&lt;N&gt;.html and never change.</div>')
        if (s.get("revenue_drift") or {}).get("needs_refresh"):
            w('<div class="banner">Revenue has moved beyond the tolerance carriers priced on. '
              '<b>Indication needs refresh</b> before this is sent.</div>')

    w(f'<div class="kicker">Cyber protection options for</div><h1>{_e(s["client"]["name"])}</h1>')
    w(f'<p class="lede">{_e(n["why_it_matters"])}</p>')

    # Options
    w('<h2>Your options at a glance</h2><div class="tiers">')
    for t in ["recommended", "premier"]:
        o = opts.get(t)
        if not o:
            st = (carrier.get("option_state") or {}).get(t, "declined")
            why = ("Not offered by this insurer for a practice this size." if st.startswith("declined")
                   else "Waiting on the insurer's written price.")
            w(f'<div class="tier off"><h4>{TIER_NAME[t]}</h4><p class="small muted">{why}</p></div>')
            continue
        rec = t == s.get("recommended_tier")
        w(f'<div class="tier{" rec" if rec else ""}">' + ('<div class="flag">Most dental offices choose this</div>' if rec else ""))
        w(f'<h4>{TIER_NAME[t]}</h4><div class="price">{_m(o["monthly"])}<span> /month est.</span></div>'
          f'<div class="small muted">{_m(o["premium"])} per year</div><dl>'
          f'<dt>Protection up to</dt><dd>{_short(o["limit"])}</dd>'
          f'<dt>You pay first</dt><dd>{_m(o["deductible"])}</dd>'
          f'<dt>Tricked into sending money</dt><dd class="warn">up to {_short(o["sublimits"].get("social_engineering"))}</dd>'
          f'</dl></div>')
    w('</div>')
    w(f'<p class="small muted">{_e(s["coverage"]["disclaimer"])} Estimates from {_e(s["selected_carrier"])}; '
      f'valid until {_e(carrier.get("expires_on"))}.</p>')

    # Intake
    if intake.get("topics"):
        calls = len(intake.get("calls", []))
        w('<h2>What you\'ve told us so far</h2>')
        w(f'<p class="small muted">From {calls} conversation{"s" if calls != 1 else ""} with your agent. '
          f'Items marked "to confirm" don\'t hold anything up; we\'ll close them before the application.</p>')
        w('<ul class="intake">')
        for t in intake["topics"]:
            w(f'<li><span>{_e(t["label"])}</span><span class="st {t["code"]}">{_e(t["status"])}</span></li>')
        w('</ul>')

    # Scenarios
    w('<h2>What could happen to a practice like yours</h2><div class="grid3">')
    for sc in n["scenarios"]:
        cost = s["scenario_costs"].get(sc["key"]) or {}
        rng = f'{_short(cost.get("low"))}–{_short(cost.get("high"))}' if cost.get("high") else _short(cost.get("low"))
        w(f'<div class="box"><h4>{_e(sc["title"])}</h4><p>{_e(sc["story"])}</p>'
          + (f'<div class="cost"><b>{rng}</b><span>{_e(cost.get("label"))}</span></div>' if cost else "") + '</div>')
    w('</div>')

    # Exposure
    ex = s["exposure"]
    w('<h2>Your exposure snapshot</h2>')
    w(f'<div class="meter"><i></i><i></i><i></i><span class="pin" style="left:{ex["score"]}%"></span></div>'
      '<div class="mlabels"><span>Lower</span><span>Moderate</span><span>Elevated</span></div>')
    w(f'<p style="margin-top:12px">{_e(n["exposure_explainer"])}</p><ul class="small">')
    for fac in ex["factors"]:
        w(f'<li>{_e(fac["label"])}</li>')
    w('</ul>')
    unknown = [PLAIN_CONTROL.get(k, k) for k in ex.get("unknown_controls", [])]
    if unknown:
        w(f'<p class="small muted">Not confirmed yet: {_e(", ".join(unknown))}. Each one lowers this score. '
          'This is a rough estimate, not a security rating.</p>')

    # Research
    if s.get("research"):
        w('<h2>Practices like yours, in the news</h2><div class="news">')
        for r in s["research"]:
            w(f'<div class="box"><h4><a href="{_e(r["url"])}">{_e(r["headline"])}</a></h4><p>{_e(r["summary"])}</p>'
              f'<p class="yours">{_e(r["for_this_client"])}</p>'
              f'<div class="src">Source: <a href="{_e(r["url"])}">{_e(r["source"])}</a>, {_e(r["date"])}</div></div>')
        w('</div>')

    # Coverage
    w('<h2>What it pays for</h2><div class="cov">')
    for c in s["coverage"]["covered"]:
        w(f'<div class="{"f" if c.get("flag_sublimit") else ""}"><h4>{_e(c["title"])}</h4><p>{_e(c["plain"])}</p></div>')
    w('</div><h4 style="margin-top:16px">Not covered</h4><ul class="small">')
    for x in s["coverage"]["not_covered"]:
        w(f'<li>{_e(x)}</li>')
    w(f'</ul><p class="small muted">Systems down: income replacement starts after {_e(carrier.get("bi_waiting_hours"))} hours.</p>')

    # FAQ + next
    ot = n["objection_tailoring"]
    w('<h2>Common questions</h2><div class="faq">'
      f'<div><h4>"We\'re too small to be a target."</h4><p>{_e(ot["too_small"])}</p></div>'
      f'<div><h4>"Our IT company handles security."</h4><p>{_e(ot["it_handles_it"])}</p></div></div>')
    w(f'<h2>What happens next</h2><p>{_e(n["next_steps"])}</p>')
    if carrier.get("conditions"):
        w(f'<p class="small">The insurer will ask about: {_e("; ".join(carrier["conditions"]))}.</p>')

    state = {"ai_draft": "AI draft", "agent_edited": "Agent edited", "submitted": "Submitted",
             "sent": "Sent", "superseded": "Superseded", "withdrawn": "Withdrawn"}.get(version.get("state"), "")
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    w(f'<footer>Version {version.get("version_no")} · {state} · rendered {stamp} · Prepared by your agent with UKON · '
      'Not a quote or a binder.</footer>')

    title = f'Cyber options — {_e(s["client"]["name"])} (v{version.get("version_no")})'
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width,initial-scale=1"><title>{title}</title>'
            f'<style>{CSS}</style></head><body><main class="page">{"".join(out)}</main></body></html>')
