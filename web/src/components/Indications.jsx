import { useEffect, useState } from 'react'
import { api, money, when, SOURCE_LABEL, readClipboard } from '../api.js'

const STATE = {
  offered: ['Offered', 'ok'],
  pending_review: ['Figure to confirm', 'mid'],
  verbal_only: ['Verbal only', 'mid'],
  declined: ['Declined', 'no'],
  declined_verbal: ['Declined (verbal)', 'no'],
  rejected: ['Rejected, resend', 'no'],
  expired: ['Expired', 'no'],
  awaiting: ['Awaiting reply', 'mid'],
}
const CHANNEL = { pdf: 'PDF letter', email: 'Email', call: 'Underwriter call', portal: 'Portal', clipboard: 'Pasted text', api: 'API response', manual: 'Edited in the app' }
const COND = { met: 'ok', to_confirm: 'mid', unknown: 'mid', gap: 'no' }
const fmtVal = (v) => (typeof v === 'number' ? money(v) : v == null ? '—' : String(v))
const day = (s) => (s ? new Date(s + 'T12:00:00').toLocaleDateString('en-US', { month: 'short', day: 'numeric' }) : '—')

function Change({ ch }) {
  if (ch.field === 'condition_added') return <span className="chg add">+ {ch.new}</span>
  if (ch.field === 'condition_removed') return <span className="chg del">− {ch.old}</span>
  if (ch.field === 'trust') return <span className="chg">{ch.label}</span>
  return <span className="chg">{ch.label}: <s>{fmtVal(ch.old)}</s> → <b>{fmtVal(ch.new)}</b></span>
}

function Version({ v, actor, onChange }) {
  const [note, setNote] = useState('')
  const [busy, setBusy] = useState(false)
  const decide = async (decision) => {
    setBusy(true)
    try { await api.reviewIndication(v.id, decision, actor, note || null); onChange() } catch (e) { alert(`Couldn't save: ${e.message}`) }
    setBusy(false)
  }
  return (
    <li className={`ver ${v.trust}`}>
      <div className="ver-top">
        <b>v{v.version_no}</b>
        <span className="muted">{day(v.doc_date)} · {CHANNEL[v.channel]}</span>
        <span className={`badge in-${v.input_method}`}>In via: {SOURCE_LABEL[v.input_method]}</span>
        <span className={`badge ${v.trust}`}>{v.trust === 'verbal' ? 'Verbal · never shown to client' : 'Written'}</span>
        {v.review === 'verified' && <span className="badge ok">{v.extractor === 'structured' ? 'Structured API data, no AI' : 'Every figure found in source'}</span>}
        {v.review === 'pending_review' && <span className="badge warn">Needs a person</span>}
        {v.review === 'confirmed' && <span className="badge ok">Confirmed by {v.reviewed_by_name}</span>}
        {v.review === 'rejected' && <span className="badge no">Rejected by {v.reviewed_by_name}</span>}
        {v.channel !== 'manual' && <a className="link" href={api.indicationSourceUrl(v.path)} target="_blank" rel="noreferrer">Open source</a>}
      </div>
      <div className="ver-fig">
        {v.status === 'declined' ? <span className="declined">Declined{v.note ? `: ${v.note}` : ''}</span> : (
          <>
            <span className="prem">{money(v.premium)}{v.hedged && <em> (hedged)</em>}</span>
            <span className="muted"> /yr · social engineering {fmtVal(v.sublimits?.social_engineering)} · ransomware {fmtVal(v.sublimits?.ransomware)}
              {v.expires_on && <> · valid to {day(v.expires_on)}</>}</span>
          </>
        )}
      </div>
      {v.quote && <blockquote>“{v.quote}”</blockquote>}
      {v.changes?.length > 0 && <div className="chgs">{v.changes.map((ch, i) => <Change key={i} ch={ch} />)}</div>}
      {v.review === 'pending_review' && (
        <div className="row review-row">
          <input placeholder="Note (required to reject)" value={note} onChange={(e) => setNote(e.target.value)} />
          <button className="btn" disabled={busy} onClick={() => decide('confirmed')}>Matches the source · confirm as {actor}</button>
          <button className="btn ghost" disabled={busy || !note} onClick={() => decide('rejected')}>Reject</button>
        </div>
      )}
    </li>
  )
}

const EDIT_SOURCES = [['conversation', 'Conversation (Wispr Flow)'], ['clipboard', 'Copied from clipboard'], ['api', 'API'], ['manual', 'Typed in by hand']]

function OptionEdit({ carrier, o, cur, actor, onDone, onCancel }) {
  const sl = cur?.sublimits || {}
  const [f, setF] = useState({
    status: cur?.status || 'indicated', premium: cur?.premium ?? '', limit_amount: cur?.limit_amount ?? o.limit,
    deductible: cur?.deductible ?? o.deductible, expires_on: cur?.expires_on || '',
    se: sl.social_engineering ?? '', rw: sl.ransomware ?? '',
  })
  const [src, setSrc] = useState('manual'); const [ref, setRef] = useState(''); const [note, setNote] = useState('')
  const [err, setErr] = useState(null)
  const set = (k) => (e) => setF({ ...f, [k]: e.target.value })
  const save = async () => {
    if (src !== 'manual' && !ref.trim()) { setErr('Say where it came from (reference).'); return }
    const changes = { status: f.status, premium: f.premium, limit_amount: f.limit_amount, deductible: f.deductible,
      expires_on: f.expires_on, sublimits: { social_engineering: f.se, ransomware: f.rw } }
    try { await api.editIndication(carrier, o.tier, changes, actor, src, ref.trim(), note.trim()); onDone() } catch (e) { setErr(e.message) }
  }
  return (
    <div className="opt-edit">
      <div className="opt-edit-grid">
        <label>Status<select value={f.status} onChange={set('status')}><option value="indicated">Offered</option><option value="declined">Declined</option></select></label>
        <label>Annual premium<input type="number" value={f.premium} onChange={set('premium')} /></label>
        <label>Limit<input type="number" value={f.limit_amount} onChange={set('limit_amount')} /></label>
        <label>Deductible<input type="number" value={f.deductible} onChange={set('deductible')} /></label>
        <label>Social engineering<input value={f.se} onChange={set('se')} placeholder="e.g. 100000" /></label>
        <label>Ransomware<input value={f.rw} onChange={set('rw')} placeholder="full limit or 500000" /></label>
        <label>Valid until<input type="date" value={f.expires_on} onChange={set('expires_on')} /></label>
      </div>
      <div className="seg small-seg">{EDIT_SOURCES.map(([k, l]) => <button key={k} className={src === k ? 'on' : ''} onClick={() => setSrc(k)}>{l}</button>)}</div>
      <div className="row">
        <input className="grow" placeholder="Where from? e.g. call with the underwriter 10/29, carrier email" value={ref} onChange={(e) => setRef(e.target.value)} />
        <input className="grow" placeholder="Note (logged with your name)" value={note} onChange={(e) => setNote(e.target.value)} />
      </div>
      {err && <div className="err small">{err}</div>}
      <div className="row">
        <button className="btn" onClick={save}>Save as new version ({actor})</button>
        <button className="btn ghost" onClick={onCancel}>Cancel</button>
        <span className="small muted">The previous version stays in the history.</span>
      </div>
    </div>
  )
}

function Carrier({ c, actor, onChange }) {
  const [open, setOpen] = useState({})
  const [editing, setEditing] = useState(null)
  return (
    <article className={`card carrier ${c.selected ? 'sel' : ''}`}>
      <header className="carrier-head">
        <h3>{c.carrier}</h3>
        {c.selected && <span className="pill s-confirmed">Shown to client</span>}
        <span className="muted small">
          requested via {c.request?.channel}{c.requests > 1 && ` (${c.requests}×)`}
          {c.expires_on && <> · valid to {day(c.expires_on)}</>}
          {c.basis_revenue && <> · priced on {money(c.basis_revenue)}</>}
        </span>
      </header>
      <div className="opts">
        {c.options.map((o) => {
          const [label, tone] = STATE[o.state]
          const cur = [...o.history].reverse().find((v) => v.trust === 'written') || o.history[o.history.length - 1]
          return (
            <div key={o.tier} className="opt">
              <div className="opt-row">
                <span className="opt-label">{o.label}</span>
                <span className={`chip ${tone}`}>{label}</span>
                <span className="opt-price">{o.state === 'offered' && cur ? money(cur.premium) : ''}</span>
                <span className="row">
                  {o.history.length > 0 && (
                    <button className="link" onClick={() => setOpen({ ...open, [o.tier]: !open[o.tier] })}>
                      {open[o.tier] ? 'Hide' : 'History'} ({o.history.length})
                    </button>
                  )}
                  <button className="link" onClick={() => setEditing(editing === o.tier ? null : o.tier)}>Edit</button>
                </span>
              </div>
              {editing === o.tier && <OptionEdit carrier={c.carrier} o={o} cur={cur} actor={actor}
                                                  onDone={() => { setEditing(null); onChange() }} onCancel={() => setEditing(null)} />}
              {open[o.tier] && (
                <ol className="versions">
                  {[...o.history].reverse().map((v) => <Version key={v.id} v={v} actor={actor} onChange={onChange} />)}
                </ol>
              )}
            </div>
          )
        })}
      </div>
      {c.conditions.length > 0 && (
        <div className="conds">
          <div className="small muted">Conditions to bind · checked against the intake</div>
          {c.conditions.map((k) => (
            <div key={k.text} className="cond"><span>{k.text}</span><span className={`chip ${COND[k.status]}`}>{k.label}</span></div>
          ))}
        </div>
      )}
    </article>
  )
}

const METHODS = [
  { id: 'conversation', label: 'From a conversation', hint: 'Paste the Wispr Flow transcript of a call with the underwriter. Verbal figures are kept but never shown to a client.' },
  { id: 'clipboard', label: 'Paste from clipboard', hint: 'Copy the email, the PDF text, or the portal page and paste it here. AI reads it; every figure is checked against what you pasted.' },
  { id: 'api', label: 'Import from API', hint: "A carrier's structured response (JSON). No AI reads it. Simulated: we don't yet know which carriers offer an API." },
]

function AddReply({ actor, carriers, onDone }) {
  const [method, setMethod] = useState('clipboard')
  const [text, setText] = useState('')
  const [carrier, setCarrier] = useState('')
  const [apiName, setApiName] = useState('')
  const [samples, setSamples] = useState(null)
  const [busy, setBusy] = useState(false)
  const [msg, setMsg] = useState(null)
  useEffect(() => { api.indicationSamples().then(setSamples).catch(() => setSamples({})) }, [])
  const m = METHODS.find((x) => x.id === method)

  const switchTo = (id) => { setMethod(id); setText(''); setMsg(null) }
  const loadSample = (s) => {
    if (method === 'api') { setText(JSON.stringify(s.payload, null, 2)); setApiName(s.payload.api || 'carrier API'); setCarrier(s.payload.carrier || '') }
    else { setText(s.text); setCarrier(s.carrier || '') }
    setMsg(null)
  }
  const fromClipboard = async () => {
    const t = await readClipboard()
    if (t == null) setMsg({ err: true, text: 'The browser blocked clipboard access; click in the box and press Cmd+V.' })
    else setText(t)
  }
  const submit = async () => {
    setBusy(true); setMsg(null)
    try {
      let r
      if (method === 'api') {
        let payload
        try { payload = JSON.parse(text) } catch { throw new Error("That isn't valid JSON.") }
        r = await api.importIndication(payload, apiName || 'carrier API', actor)
      } else {
        r = await api.pasteIndication(method, text, carrier, actor)
      }
      setMsg({ text: `${r.carrier}: ${r.options.join('; ')}` + (r.failed_checks.length ? ` · ${r.failed_checks.length} figure(s) for a person to confirm` : ''), path: r.path })
      setText(''); onDone()
    } catch (e) { setMsg({ err: true, text: e.message }) }
    setBusy(false)
  }

  return (
    <section className="card add-reply">
      <h3>Add a carrier reply</h3>
      <p className="small muted">We don't know yet how each carrier sends indications, so there are three ways in. Each one is saved
        to the wiki exactly as received, and the reply records which way it came in and who entered it.</p>
      <div className="seg mt-s">
        {METHODS.map((x) => <button key={x.id} className={method === x.id ? 'on' : ''} onClick={() => switchTo(x.id)}>{x.label}</button>)}
      </div>
      <p className="small hint">{m.hint}</p>
      <div className="row">
        {method !== 'api' && (
          <select value={carrier} onChange={(e) => setCarrier(e.target.value)}>
            <option value="">Carrier (optional; read from the text)</option>
            {carriers.map((c) => <option key={c}>{c}</option>)}
          </select>
        )}
        {method === 'api' && <input placeholder="Which API? e.g. Aspen Line quoting API" value={apiName} onChange={(e) => setApiName(e.target.value)} />}
        {method === 'clipboard' && <button className="btn ghost sm" onClick={fromClipboard}>Paste what I copied</button>}
        {(samples?.[method] || []).map((s) => (
          <button key={s.label} className="btn ghost sm" onClick={() => loadSample(s)}>Load sample: {s.label}</button>
        ))}
      </div>
      <textarea className={`reply-box ${method === 'api' ? 'mono' : ''}`} rows={method === 'api' ? 12 : 9} value={text}
                onChange={(e) => setText(e.target.value)}
                placeholder={method === 'api' ? '{ "carrier": "...", "insured": "...", "document_date": "YYYY-MM-DD", "options": [ ... ] }'
                  : method === 'conversation' ? '[00:00] Agent: ...\n[00:05] Underwriter: ...' : 'Paste the email or letter here'} />
      <div className="row">
        <button className="btn primary" disabled={busy || !text.trim()} onClick={submit}>{busy ? 'Reading…' : `Add reply as ${actor}`}</button>
        {msg && <span className={`small ${msg.err ? 'err' : 'ok-text'}`}>{msg.text}{msg.path && <> · saved as <code>{msg.path.split('/').pop()}</code></>}</span>}
      </div>
    </section>
  )
}

export default function Indications({ actor, onChange, tick, embedded = false }) {
  const [d, setD] = useState(null)
  const [err, setErr] = useState(null)
  const [busy, setBusy] = useState(null)
  const load = () => api.indications().then(setD).catch((e) => setErr(e.message))
  useEffect(() => { load() }, [tick])
  const changed = () => { load(); onChange() }
  if (err) return <div className="card">Couldn't load indications: {err}</div>
  if (!d) return <div className="card empty">Loading…</div>

  const open = d.actions.filter((a) => a.status === 'open')
  const done = d.actions.filter((a) => a.status === 'done')
  const sentAt = d.requests[0]?.sent_at

  const ingest = async (path) => {
    setBusy(path)
    try { await api.ingestIndication(path, actor); changed() } catch (e) { alert(e.message) }
    setBusy(null)
  }
  const closeAction = async (a) => {
    const note = window.prompt('What was done? (logged with your name)', '')
    if (note === null) return
    try { await api.closeIndicationAction(a.id, actor, note || null); changed() } catch (e) { alert(`Couldn't save: ${e.message}`) }
  }
  const reRequest = async () => {
    try { const r = await api.requestIndications(actor); alert(`Re-requested from ${r.sent} carriers`); changed() } catch (e) { alert(e.message) }
  }

  return (
    <div className="stack">
      {embedded ? <h3 className="step-h"><span className="step-n">B</span> Send to carriers, bring the replies back</h3> : (
        <section className="intro">
        <h2>Stage 1 · Carrier indications</h2>
        <p>
          Requests go out with the five fields; replies come back however each carrier sends them: a PDF letter, an email,
          a call with the underwriter. Every reply is kept as received, and each one adds a version. Nothing is overwritten.
          Every figure is checked against the source text. Verbal numbers never reach the client, and a figure that doesn't
          pass the check waits for a person.
        </p>
      </section>
      )}

      <section className="card attention">
        <h3>Needs attention <span className="muted">· {open.length + d.alerts.length}</span></h3>
        {d.alerts.length + open.length === 0 && <p className="muted">Nothing open.</p>}
        <ul className="actions">
          {d.alerts.map((a, i) => <li key={`al${i}`} className={`act ${a.kind}`}><span className="act-kind">{a.kind}</span>{a.text}</li>)}
          {open.map((a) => (
            <li key={a.id} className={`act ${a.kind}`}>
              <span className="act-kind">{a.kind.replaceAll('_', ' ')}</span>
              <span>{a.text}</span>
              {a.kind !== 'confirm_extraction' && <button className="btn ghost sm" onClick={() => closeAction(a)}>Done</button>}
            </li>
          ))}
        </ul>
        {done.length > 0 && (
          <details className="done">
            <summary className="small muted">{done.length} closed</summary>
            <ul className="actions">
              {done.map((a) => <li key={a.id} className="act closed"><span className="act-kind">{a.kind.replaceAll('_', ' ')}</span>
                <span>{a.text} <span className="muted">· {a.closed_by_name}{a.close_note && `: ${a.close_note}`}</span></span></li>)}
            </ul>
          </details>
        )}
      </section>

      <div className="split2">
        <section className="card">
          <h3>Sent {sentAt && <span className="muted">· {when(sentAt)}</span>}</h3>
          <p className="small muted">{d.options.map((o) => o.label).join(' and ')} to {new Set(d.requests.map((r) => r.carrier)).size} carriers.
            Basis as sent:</p>
          {d.basis && (
            <dl className="basis">
              {Object.entries(d.basis.fields).map(([k, f]) => (
                <div key={k}><dt>{f.label}</dt><dd>{f.label.includes('revenue') ? money(f.value) : String(f.value)}
                  {f.needs_review && <span className="chip mid">unreviewed</span>}</dd></div>
              ))}
            </dl>
          )}
          {d.basis_unreviewed.length > 0 && (
            <p className="small warn-text">Sent before review of: {d.basis_unreviewed.join(', ')}. In production, sending waits for that review.</p>
          )}
          <button className="btn ghost" onClick={reRequest} disabled={d.current_basis_unreviewed.length > 0}
                  title={d.current_basis_unreviewed.length ? `Review first: ${d.current_basis_unreviewed.join(', ')}` : ''}>
            Re-request with current basis
          </button>
          {d.current_basis_unreviewed.length > 0 && <p className="small muted">Review first: {d.current_basis_unreviewed.join(', ')} (step A above).</p>}
        </section>

        <section className="card">
          <h3>Received</h3>
          <ul className="received">
            {d.sources.map((s) => (
              <li key={s.id}>
                <span>{day(s.doc_date)}</span><b>{s.carrier}</b>
                <span className="muted">{CHANNEL[s.channel]} · <span className={`in-txt in-${s.input_method}`}>{SOURCE_LABEL[s.input_method]}</span>{s.input_by_name && ` · ${s.input_by_name}`}</span>
                {s.channel !== 'manual' ? <a className="link" href={api.indicationSourceUrl(s.path)} target="_blank" rel="noreferrer">open</a> : <span />}
              </li>
            ))}
          </ul>
          {d.inbox.length > 0 && (
            <>
              <h4 className="mt">Files saved to the wiki, not yet ingested</h4>
              <ul className="received">
                {d.inbox.map((p) => (
                  <li key={p}><span className="mono">{p.split('/').pop()}</span>
                    <button className="btn sm" disabled={busy === p} onClick={() => ingest(p)}>{busy === p ? 'Reading…' : 'Ingest'}</button></li>
                ))}
              </ul>
            </>
          )}
        </section>
      </div>

      <AddReply actor={actor} carriers={[...new Set(d.requests.map((r) => r.carrier))]} onDone={changed} />

      <section>
        <h3 className="section-h">By carrier</h3>
        <div className="carriers">
          {d.carriers.map((c) => <Carrier key={c.carrier} c={c} actor={actor} onChange={changed} />)}
        </div>
      </section>
    </div>
  )
}
