import { useEffect, useState } from 'react'
import { api, money, when } from '../api.js'

// What each carrier + option looks like right now (computed by pipeline/indications.state).
const STATE = {
  awaiting: ['Awaiting reply', ''],
  offered: ['Indicated', 'ok'],
  expired: ['Expired · re-request', 'bad'],
  declined: ['Declined', 'bad'],
  declined_verbal: ['Declined (verbal)', 'bad'],
  pending_review: ['Figure to check', 'warn'],
  rejected: ['Rejected on review', 'bad'],
  verbal_only: ['Verbal only · not client-facing', 'warn'],
}
const CHANNEL = { pdf: 'PDF letter', email: 'Email', call: 'Underwriter call', portal: 'Portal', api: 'API', clipboard: 'Pasted', manual: 'Typed' }
const KIND = {
  confirm_extraction: 'Check a figure', get_in_writing: 'Get it in writing', new_condition: 'New condition',
  price_change: 'Price changed', declined: 'Declined', terms_change: 'Terms changed',
}

// ---- Compare carriers at a glance -------------------------------------------------------------
// One bar chart per requested option (premium per carrier, same scale across both), then a terms grid.
// Figures come from each carrier's latest written version; anything not client-ready says why in words.
const NOT_READY = {
  awaiting: 'No reply yet', declined: 'Declined', declined_verbal: 'Declined (verbal)', rejected: 'Rejected on review',
  pending_review: 'Figure to check', verbal_only: 'Verbal only', expired: 'Expired',
}
const latestOf = (o) => [...o.history].reverse().find((v) => v.trust === 'written') || o.history[o.history.length - 1]
const shortMoney = (n) => (n == null ? '—' : n === 0 ? '$0' : n >= 1e6 ? `$${n / 1e6}M` : n >= 1e3 ? `$${+(n / 1e3).toFixed(1)}K` : money(n))
const sub = (v) => (v == null ? '—' : v === 'full limit' ? 'Full limit' : shortMoney(v))

function CompareCarriers({ carriers, options }) {
  const all = carriers.flatMap((c) => c.options.map((o) => latestOf(o)?.premium || 0))
  const top = Math.max(1, ...all)
  const step = [500, 1000, 2000, 2500, 5000, 10000].find((st) => top / st <= 6) || 20000
  const max = Math.ceil((top * 1.05) / step) * step             // axis ends on a round number
  const ticks = Array.from({ length: max / step + 1 }, (_, i) => i * step)

  return (
    <section className="card compare">
      <h3>Compare carriers <span className="muted">· annual premium for each requested option, same scale</span></h3>
      <div className="cmp-charts">
        {options.map((opt) => {
          const rows = carriers.map((c) => {
            const o = c.options.find((x) => x.tier === opt.tier)
            const v = o && latestOf(o)
            return { c, o, v, ready: o?.state === 'offered' }
          })
          const readyPrices = rows.filter((r) => r.ready).map((r) => r.v.premium)
          const low = readyPrices.length ? Math.min(...readyPrices) : null
          return (
            <figure key={opt.tier} className="cmp-chart">
              <figcaption><b>{opt.label}</b> <span className="muted small">limit / deductible</span></figcaption>
              <div className="cmp-axis" aria-hidden>{ticks.map((t) => <span key={t} style={{ left: `${(t / max) * 100}%` }}>{shortMoney(t)}</span>)}</div>
              {rows.map(({ c, o, v, ready }) => {
                const pct = v?.premium ? (v.premium / max) * 100 : 0
                const why = ready ? null : NOT_READY[o?.state] || '—'
                const tip = `${c.carrier} · ${opt.label}: ${v?.premium ? money(v.premium) + '/yr' : 'no figure'}${why ? ` (${why})` : ''}`
                  + (v?.sublimits ? ` · social engineering ${sub(v.sublimits.social_engineering)} · ransomware ${sub(v.sublimits.ransomware)}` : '')
                return (
                  <div key={c.carrier} className="cmp-row" title={tip}>
                    <span className="cmp-name">{c.carrier}{c.selected && <span className="cmp-tag">shown to client</span>}</span>
                    <span className="cmp-track">
                      {pct > 0 && <span className={`cmp-bar ${ready ? '' : 'muted-bar'} ${o?.state === 'verbal_only' ? 'verbal' : ''}`} style={{ width: `${pct}%` }} />}
                      <span className="cmp-val" style={{ left: `${pct}%` }}>
                        {v?.premium && o?.state !== 'declined' && o?.state !== 'declined_verbal' ? <b>{money(v.premium)}</b> : null}
                        {why && <span className="cmp-why">{v?.premium && !String(o?.state).startsWith('declined') ? ' · ' : ''}{why}</span>}
                        {ready && v.premium === low && readyPrices.length > 1 && <span className="cmp-low">lowest</span>}
                      </span>
                    </span>
                  </div>
                )
              })}
            </figure>
          )
        })}
      </div>

      <div className="cmp-table-wrap">
        <table className="cmp-table">
          <thead>
            <tr><th>Carrier</th>{options.map((o) => <th key={o.tier}>{o.label}</th>)}
              <th>Social engineering<br /><span className="muted small">($1M option)</span></th><th>Ransomware</th>
              <th>BI waiting period</th><th>Conditions met</th><th>Valid until</th></tr>
          </thead>
          <tbody>
            {carriers.map((c) => {
              const first = c.options[0] && latestOf(c.options[0])
              const rw = first?.sublimits?.ransomware
              const met = c.conditions.filter((k) => k.status === 'met').length
              const days = c.expires_on ? Math.round((new Date(c.expires_on) - new Date()) / 864e5) : null
              return (
                <tr key={c.carrier} className={c.selected ? 'sel' : ''}>
                  <td><b>{c.carrier}</b></td>
                  {c.options.map((o) => {
                    const v = latestOf(o)
                    return <td key={o.tier}>{o.state === 'offered' ? money(v.premium) : <span className="muted">{NOT_READY[o.state]}{v?.premium && !o.state.startsWith('declined') ? ` (${money(v.premium)})` : ''}</span>}</td>
                  })}
                  <td>{sub(first?.sublimits?.social_engineering)}</td>
                  <td>{rw == null ? '—' : rw === 'full limit' ? 'Full limit' : <span className="flag-txt">⚠ capped at {shortMoney(rw)}</span>}</td>
                  <td>{first?.bi_waiting_hours ? `${first.bi_waiting_hours} hours` : '—'}</td>
                  <td>{c.conditions.length ? <span className={met === c.conditions.length ? 'ok-txt' : 'flag-txt'}>{met === c.conditions.length ? '✓' : '⚠'} {met} of {c.conditions.length} confirmed</span> : '—'}</td>
                  <td>{c.expires_on ? <>{c.expires_on}{days != null && days <= 14 && <span className="flag-txt"> · {days < 0 ? 'expired' : `${days} days`}</span>}</> : '—'}</td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
      <p className="small muted">Grey bars aren't client-ready (verbal, a figure to check, or expired). "Conditions met" checks each carrier's
        subjectivities against the intake answers so far.</p>
    </section>
  )
}

function SendPanel({ ind, data, actor, onDone, goStage1 }) {
  const [picked, setPicked] = useState(() => ind.panel.map((c) => c.carrier))
  const [busy, setBusy] = useState(false)
  const [err, setErr] = useState(null)
  const blocked = ind.current_basis_unreviewed
  const byKey = Object.fromEntries(data.fields.map((f) => [f.key, f]))
  const basis = ['legal_name', 'domain', 'industry', 'annual_revenue', 'address']
  const sentBefore = ind.requests.length > 0
  const seeded = ind.requests.some((r) => (r.reason || '').includes('demo seed'))
  const toggle = (c) => setPicked((p) => (p.includes(c) ? p.filter((x) => x !== c) : [...p, c]))

  const send = async () => {
    setBusy(true); setErr(null)
    try { await api.sendToCarriers(picked, actor); onDone() } catch (e) { setErr(e.message) } finally { setBusy(false) }
  }

  return (
    <section className="card">
      <h3>{sentBefore ? 'Re-request indications' : 'Send to carriers'} <span className="muted">· a person approves before client data leaves the agency</span></h3>
      {seeded && (
        <div className="banner warn">Demo shortcut: the first requests went out before Stage 1 was reviewed (labelled “demo seed”).
          Re-sending below is gated on the review, the way production would be.</div>)}
      <div className="send-grid">
        <div>
          <div className="label">What goes to the carriers</div>
          <table className="basis">
            <tbody>
              {basis.map((k) => byKey[k] && (
                <tr key={k} className={byKey[k].needs_review ? 'needs' : ''}>
                  <td>{byKey[k].label}</td>
                  <td><b>{k === 'annual_revenue' ? money(byKey[k].current_value) : String(byKey[k].current_value ?? '—')}</b></td>
                  <td className="muted small">{byKey[k].needs_review ? 'not reviewed' : byKey[k].source_type === 'pipeline' ? 'reviewed' : `from ${byKey[k].source_type}`}</td>
                </tr>
              ))}
            </tbody>
          </table>
          <div className="small muted">Options requested from every carrier: {ind.options.map((o) => o.label).join(' and ')}.</div>
        </div>
        <div>
          <div className="label">Carriers</div>
          {ind.panel.map((c) => (
            <label key={c.carrier} className="pick">
              <input type="checkbox" checked={picked.includes(c.carrier)} onChange={() => toggle(c.carrier)} />
              <span><b>{c.carrier}</b> <span className="muted small">via {c.request_channel}</span></span>
            </label>
          ))}
          {blocked.length > 0 && (
            <div className="banner warn">Finish Stage 1 first: review {blocked.join(', ')}.{' '}
              <button className="link" onClick={goStage1}>Go to Stage 1</button></div>)}
          {err && <div className="err small">{err}</div>}
          <button className="btn primary" disabled={busy || blocked.length > 0 || picked.length === 0} onClick={send}>
            {sentBefore ? 'Re-request' : 'Send'} to {picked.length} carrier{picked.length === 1 ? '' : 's'} as {actor}
          </button>
        </div>
      </div>
    </section>
  )
}

function Version({ v, actor, onDone }) {
  const [note, setNote] = useState('')
  const review = async (decision) => {
    try { await api.reviewIndication(v.id, decision, note || null, actor); onDone() } catch (e) { alert(e.message) }
  }
  return (
    <li className={`ver t-${v.trust}`}>
      <div className="row">
        <b>v{v.version_no}</b>
        <span>{v.status === 'declined' ? 'Declined' : money(v.premium) + '/yr'}</span>
        <span className="muted small">{CHANNEL[v.channel] || v.channel} · {v.doc_date}{v.trust === 'verbal' ? ' · verbal' : ''}</span>
        {v.review === 'pending_review' && <span className="pill warn">check figure</span>}
        {v.review === 'confirmed' && <span className="pill s-confirmed">checked by {v.reviewed_by_name}</span>}
        {v.review === 'rejected' && <span className="pill s-unanswered">rejected</span>}
      </div>
      {v.changes?.length > 0 && (
        <ul className="changes">{v.changes.map((c, i) => (
          <li key={i}>{c.field === 'condition_added' ? <>New condition: {c.new}</> : c.field === 'condition_removed'
            ? <>Dropped: {c.old}</> : <>{c.label}: {typeof c.old === 'number' ? money(c.old) : c.old ?? '—'} → {typeof c.new === 'number' ? money(c.new) : c.new}</>}</li>
        ))}</ul>
      )}
      {v.quote && <blockquote className="quote">"{v.quote}" <span>[{v.path}]</span></blockquote>}
      {v.review === 'pending_review' && (
        <div className="row">
          <input className="grow" placeholder="Note (optional), e.g. matches the email body" value={note} onChange={(e) => setNote(e.target.value)} />
          <button className="btn sm" onClick={() => review('confirmed')}>Matches the source</button>
          <button className="btn ghost sm" onClick={() => review('rejected')}>Doesn't match</button>
        </div>
      )}
    </li>
  )
}

function CarrierCard({ car, actions, alerts, actor, onDone }) {
  const [open, setOpen] = useState(false)
  const openActs = actions.filter((a) => a.status === 'open')
  const doneActs = actions.filter((a) => a.status === 'done')
  return (
    <article id={`carrier-${car.carrier.replace(/\W+/g, '-')}`} className={`card carrier ${car.selected ? 'sel' : ''}`}>
      <header className="row">
        <h3>{car.carrier}</h3>
        {car.selected && <span className="pill s-confirmed">shown to client</span>}
        <span className={`pill ${openActs.length ? 'warn' : ''}`}>{openActs.length ? `${openActs.length} follow-up${openActs.length === 1 ? '' : 's'}` : 'no follow-ups'}</span>
        <span className="muted small">requested via {car.request?.channel || '—'}{car.request ? ` · ${when(car.request.sent_at)}` : ''}{car.requests > 1 ? ` · ${car.requests} requests` : ''}</span>
      </header>
      <table className="opts-t">
        <thead><tr><th>Option</th><th>Status</th><th>Premium</th></tr></thead>
        <tbody>
          {car.options.map((o) => {
            const last = o.history[o.history.length - 1]
            const [label, tone] = STATE[o.state]
            return (
              <tr key={o.tier}>
                <td>{o.label}</td>
                <td><span className={`ix-${tone || 'none'}`}>{label}</span></td>
                <td>{o.state === 'offered' || o.state === 'expired' ? <b>{money(last?.premium)}</b> : last?.premium ? <span className="muted">{money(last.premium)}</span> : '—'}</td>
              </tr>
            )
          })}
        </tbody>
      </table>
      {car.conditions.length > 0 && (
        <ul className="conds">{car.conditions.map((c) => (
          <li key={c.text}><span>{c.text}</span> <span className={`pill c-${c.status}`}>{c.label}</span></li>
        ))}</ul>
      )}
      {car.expires_on && <div className="small muted">Valid until {car.expires_on}</div>}
      <div className="carrier-fu">
        <div className="label">Follow-ups from {car.carrier}'s replies</div>
        {alerts.map((a, i) => <div key={i} className="banner warn small">{a.text}</div>)}
        {openActs.length === 0 && alerts.length === 0 && <p className="muted small">Nothing open.</p>}
        <ul className="actions">{openActs.map((a) => <Action key={a.id} a={a} actor={actor} onDone={onDone} />)}</ul>
        {doneActs.length > 0 && (
          <details><summary className="small muted">{doneActs.length} done</summary>
            <ul className="actions">{doneActs.map((a) => <Action key={a.id} a={a} actor={actor} onDone={onDone} />)}</ul>
          </details>
        )}
      </div>
      <button className="link" onClick={() => setOpen(!open)}>{open ? 'Hide' : 'Show'} reply history</button>
      {open && car.options.map((o) => o.history.length > 0 && (
        <div key={o.tier}>
          <div className="label">{o.label}</div>
          <ul className="history">{o.history.map((v) => <Version key={v.id} v={v} actor={actor} onDone={onDone} />)}</ul>
        </div>
      ))}
    </article>
  )
}

function Action({ a, actor, onDone }) {
  const [note, setNote] = useState('')
  const [open, setOpen] = useState(false)
  if (a.status === 'done') {
    return <li className="action done"><span className="pill">{KIND[a.kind]}</span> {a.text} <span className="muted small">— {a.closed_by_name}: {a.close_note}</span></li>
  }
  return (
    <li className="action">
      <span className="pill warn">{KIND[a.kind]}</span> {a.text}
      {a.kind !== 'confirm_extraction' && !open && <button className="link" onClick={() => setOpen(true)}>Mark done</button>}
      {a.kind === 'confirm_extraction' && <span className="muted small"> Check it in the carrier's reply history.</span>}
      {open && (
        <div className="row">
          <input className="grow" placeholder="What did you do? (logged with your name)" value={note} onChange={(e) => setNote(e.target.value)} />
          <button className="btn sm" disabled={!note.trim()} onClick={async () => {
            try { await api.actionDone(a.id, note, actor); onDone() } catch (e) { alert(e.message) }
          }}>Done</button>
          <button className="btn ghost sm" onClick={() => setOpen(false)}>Cancel</button>
        </div>
      )}
    </li>
  )
}

export default function Indications({ data, actor, onChange, tick, goStage1 }) {
  const [ind, setInd] = useState(null)
  const [busy, setBusy] = useState(null)
  const [msg, setMsg] = useState(null)
  const [local, setLocal] = useState(0)
  useEffect(() => { api.indications().then(setInd).catch((e) => setMsg({ err: e.message })) }, [tick, local])
  const done = () => { setLocal((x) => x + 1); onChange() }
  if (!ind) return <div className="muted">Loading indications…</div>

  const open = ind.actions.filter((a) => a.status === 'open')
  const ingest = async (path) => {
    setBusy(path); setMsg(null)
    try {
      const r = await api.ingestReply(path, actor)
      setMsg({ ok: `${r.carrier} (${CHANNEL[r.channel] || r.channel}): ${r.options.join('; ')}` + (r.failed_checks.length ? ` · ${r.failed_checks.length} figure(s) to check` : '') })
      done()
    } catch (e) { setMsg({ err: e.message }) } finally { setBusy(null) }
  }

  return (
    <div className="stack">
      <section className="intro">
        <h2>Stage 2 · Get indications</h2>
        <p>The five confirmed fields go to the carrier panel; each carrier replies however it replies (PDF letter, email, a call
          with the underwriter). Every reply is a raw source in the wiki: AI reads it, every figure is checked against the source
          text, and each reply adds a version instead of overwriting the last. <b>Carrier figures are read-only here.</b> Verbal
          numbers never reach the client, and fixed rules (not the model) turn changes into follow-ups.</p>
      </section>

      <SendPanel ind={ind} data={data} actor={actor} onDone={done} goStage1={goStage1} />

      {(ind.inbox.length > 0 || msg) && (
        <section className="card">
          <h3>Carrier inbox <span className="muted">· replies waiting to be read in</span></h3>
          {ind.inbox.map((p) => (
            <div key={p} className="row inbox">
              <code>{p.split('/').pop()}</code>
              <button className="btn sm" disabled={busy === p} onClick={() => ingest(p)}>{busy === p ? 'Reading…' : 'Read it in'}</button>
            </div>
          ))}
          {msg?.ok && <div className="banner ok">{msg.ok}</div>}
          {msg?.err && <div className="err small">{msg.err}</div>}
        </section>
      )}

      {ind.carriers.some((c) => c.options.some((o) => o.history.length)) && <CompareCarriers carriers={ind.carriers} options={ind.options} />}

      {(open.length > 0 || ind.alerts.length > 0) && (
        <div className="fu-summary small">
          <b>Follow-ups by carrier:</b>
          {ind.carriers.map((c) => {
            const n = open.filter((a) => a.carrier === c.carrier).length + ind.alerts.filter((a) => a.carrier === c.carrier).length
            return <a key={c.carrier} href={`#carrier-${c.carrier.replace(/\W+/g, '-')}`} className={`pill ${n ? 'warn' : ''}`}>{c.carrier} · {n}</a>
          })}
        </div>
      )}

      <div className="carriers">{ind.carriers.map((c) => (
        <CarrierCard key={c.carrier} car={c} actor={actor} onDone={done}
                     actions={ind.actions.filter((a) => a.carrier === c.carrier)}
                     alerts={ind.alerts.filter((a) => a.carrier === c.carrier)} />
      ))}</div>
    </div>
  )
}
