import { useState } from 'react'
import { api, money, SOURCE_LABEL, readClipboard } from '../api.js'

const INDICATION_KEYS = ['legal_name', 'domain', 'industry', 'annual_revenue', 'address']

function fmt(f, v = f.current_value) {
  if (v == null) return '—'
  if (f.kind === 'money' || f.kind === 'benchmark') return money(v)
  if (typeof v === 'number') return v.toLocaleString()
  return String(v)
}

function Confidence({ level }) {
  return <span className={`conf conf-${level}`}>{level} confidence</span>
}

const SOURCES = ['conversation', 'clipboard', 'api', 'manual']
const REF_HINT = {
  conversation: 'Which call? e.g. call_1_intake, or "call with Dr. Pollack 10/29"',
  clipboard: 'Copied from where? e.g. CO SOS page, email from the office manager',
  api: 'Which API? e.g. agency AMS, Colorado SOS open data',
  manual: 'Optional: how you know',
}

function Provenance({ f }) {
  const st = f.source_type || 'pipeline'
  return (
    <div className={`prov prov-${st}`}>
      <span className="prov-k">Source</span> {SOURCE_LABEL[st]}
      {f.source_ref && <> · <span className="prov-ref">{f.source_ref}</span></>}
      {st !== 'pipeline' && f.updated_by_name && <> · {f.updated_by_name}</>}
    </div>
  )
}

export function FieldCard({ f, actor, onChange, required }) {
  const [editing, setEditing] = useState(false)
  const [val, setVal] = useState(f.current_value)
  const [reason, setReason] = useState('')
  const [src, setSrc] = useState('manual')
  const [ref, setRef] = useState('')
  const [err, setErr] = useState(null)
  const [open, setOpen] = useState(false)
  const changed = JSON.stringify(f.ai_value) !== JSON.stringify(f.current_value)

  const start = () => { setVal(f.current_value); setSrc('manual'); setRef(''); setReason(''); setErr(null); setEditing(true) }
  const paste = async () => {
    const t = await readClipboard()
    if (t == null) { setErr('The browser blocked clipboard access; paste into the box with Cmd+V instead.'); return }
    setVal(f.kind === 'text' ? t.trim() : t.replace(/[^0-9.]/g, '')); setSrc('clipboard')
  }
  const save = async () => {
    if (src !== 'manual' && !ref.trim()) { setErr('Say where it came from (the reference box).'); return }
    try {
      await api.changeField(f.key, f.kind === 'text' ? val : Number(val), actor, reason || null, src, ref.trim() || null)
      setEditing(false); onChange()
    } catch (e) { setErr(e.message) }
  }

  return (
    <article className={`field ${f.needs_review ? 'needs' : ''}`}>
      <header>
        <div className="field-label">{f.label}{required && <span className="req">indication</span>}</div>
        {f.confidence && <Confidence level={f.confidence} />}
      </header>
      <div className="field-value">{fmt(f)}</div>
      {changed && <div className="ai-vs">AI recommended {fmt(f, f.ai_value)} · changed by {f.updated_by_name}</div>}
      {f.ai_low != null && f.kind !== 'score' && (
        <div className="range">Range {fmt(f, f.ai_low)} – {fmt(f, f.ai_high)}</div>
      )}
      <Provenance f={f} />
      <button className="link" onClick={() => setOpen(!open)}>{open ? 'Hide' : 'Show'} method & sources</button>
      {open && (
        <div className="method">
          <p>{f.method}</p>
          {f.sources?.length > 0 && <ul>{f.sources.map((s) => <li key={s}><code>raw/{s}</code></li>)}</ul>}
        </div>
      )}
      {f.needs_review && <div className="review-note">Needs a human look before indications go out.</div>}
      <footer>
        {f.adjustable && !editing && <button className="btn ghost" onClick={start}>Edit</button>}
        {f.needs_review && f.adjustable && !editing && f.key !== 'legal_name' && (
          <button className="btn" onClick={async () => { try { await api.approveField(f.key, actor); onChange() } catch (e) { alert(e.message) } }}>Approve AI value</button>
        )}
        {f.key === 'legal_name' && f.needs_review && !editing && <span className="muted small">Or confirm the company above</span>}
      </footer>
      {editing && (
        <div className="edit">
          <div className="row">
            <input className="grow" value={val ?? ''} onChange={(e) => setVal(e.target.value)} type={f.kind === 'text' ? 'text' : 'number'} />
            <button className="btn ghost sm" onClick={paste} title="Fill from what you last copied">Paste</button>
          </div>
          <label className="small muted">Where did this come from?</label>
          <div className="seg small-seg">
            {SOURCES.map((s) => <button key={s} className={src === s ? 'on' : ''} onClick={() => setSrc(s)}>{SOURCE_LABEL[s]}</button>)}
          </div>
          <input placeholder={REF_HINT[src]} value={ref} onChange={(e) => setRef(e.target.value)} />
          <input placeholder="Reason (logged with your name)" value={reason} onChange={(e) => setReason(e.target.value)} />
          {err && <div className="err small">{err}</div>}
          <div className="row">
            <button className="btn" onClick={save}>Save as {actor}</button>
            <button className="btn ghost" onClick={() => setEditing(false)}>Cancel</button>
          </div>
        </div>
      )}
    </article>
  )
}

export default function Enrichment({ data, actor, onChange, goNext }) {
  const byKey = Object.fromEntries(data.fields.map((f) => [f.key, f]))
  const confirmed = data.entities.find((e) => e.status === 'confirmed')
  const reviewCount = INDICATION_KEYS.filter((k) => byKey[k]?.needs_review).length
  const left = reviewCount + (confirmed ? 0 : 1)

  return (
    <div className="stack">
      <section className="intro">
        <h2>Stage 1 · Confirm data</h2>
        <p>
          Carriers need five facts for an indication. This is a renewal, so most are already in the agency's file; the pipeline
          fills the rest from public records and flags what a person must check. Every value shows where it came from (agency file
          or public records, a conversation, the clipboard, an API, or typed in), and anyone can correct one.
          Only gaps go back to the client, usually the domain or this year's revenue. <strong>{left} item{left === 1 ? '' : 's'}</strong> need a human.
        </p>
      </section>

      <section className="card">
        <h3>Which company is this? <span className="muted">· always confirmed by a person</span></h3>
        <p className="muted">The agency calls this client "{data.client.display_name}." The state registry has two entities at the practice's address (one delinquent) plus older and look-alike names, all real public records.</p>
        <div className="entities">
          {data.entities.map((e) => (
            <div key={e.id} className={`entity ${e.status}`}>
              <div className="entity-top">
                <strong>{e.legal_name}</strong>
                <span className="score">{Math.round(e.match_score * 100)}% match</span>
              </div>
              <div className="muted">{e.address}{e.domain ? ` · ${e.domain}` : ''}{e.signals.registry ? ` · ${e.signals.registry}` : ''}</div>
              <div className="chips">
                {['name', 'state', 'address', 'domain', 'status'].filter((k) => k in e.signals).map((k) => (
                  <span key={k} className={`chip ${e.signals[k] >= 0.9 ? 'ok' : e.signals[k] > 0 ? 'mid' : 'no'}`}>
                    {k} {e.signals[k] >= 0.9 ? '✓' : e.signals[k] > 0 ? `${Math.round(e.signals[k] * 100)}%` : '✗'}
                  </span>
                ))}
              </div>
              {e.status === 'suggested' && !confirmed && (
                <button className="btn" onClick={async () => { try { await api.confirmEntity(e.id, actor); onChange() } catch (err) { alert(`Couldn't confirm: ${err.message}`) } }}>
                  Confirm this is the client
                </button>
              )}
              {e.status !== 'suggested' && (
                <div className="row">
                  <div className={`status ${e.status}`}>{e.status} by {e.decided_by_name}</div>
                  {e.status === 'confirmed' && (
                    <button className="btn ghost sm" onClick={async () => {
                      if (!window.confirm(`Undo confirming ${e.legal_name}? The match goes back to review.`)) return
                      try { await api.undoEntity(actor); onChange() } catch (err) { alert(`Couldn't undo: ${err.message}`) }
                    }}>Undo</button>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      </section>

      <section>
        <h3 className="section-h">The five fields carriers need</h3>
        <div className="grid">
          {INDICATION_KEYS.map((k) => byKey[k] && <FieldCard key={k} f={byKey[k]} actor={actor} onChange={onChange} required />)}
        </div>
      </section>
      <section className={`card next ${left ? 'muted-card' : ''}`}>
        <div className="row">
          <div className="grow">
            <b>Next: Stage 2 · Get indications.</b>{' '}
            {left ? <span className="muted">Sending is gated on this review: {left} item{left === 1 ? '' : 's'} left.</span>
              : <span>All five fields are reviewed. Pick carriers and send.</span>}
          </div>
          <button className="btn primary" onClick={goNext}>Go to Stage 2 →</button>
        </div>
        <p className="small muted">Headcount, record counts, security controls and the exposure score aren't needed for an
          indication. They live in the proposal pack (Stage 3) and the application (Stage 5).</p>
      </section>
    </div>
  )
}
