import { useEffect, useState } from 'react'
import { api, when } from '../api.js'

const LABEL = { prefilled: 'AI-filled · confirm', needs_followup: 'Needs follow-up', confirmed: 'Confirmed', unanswered: 'Not asked yet' }

function Row({ a, actor, onDone }) {
  const [edit, setEdit] = useState(false)
  const [answer, setAnswer] = useState(a.answer || '')
  const [norm, setNorm] = useState(a.normalized)
  const [note, setNote] = useState(null)
  const confirm = async (custom) => {
    const r = await api.confirmAnswer(a.question_key, actor, custom ? answer : null, custom ? norm : null)
    if (r.applied_to) setNote(`Applied to report field "${r.applied_to}" and logged.`)
    setEdit(false); onDone()
  }
  return (
    <div className={`ans s-${a.status}`}>
      <div className="ans-head">
        <div className="ans-q">{a.question}</div>
        <span className={`pill s-${a.status}`}>{LABEL[a.status]}</span>
      </div>
      <div className="ans-a">{a.answer || <span className="muted">—</span>} {a.normalized && !['value', 'unknown'].includes(a.normalized) && <code>{a.normalized}</code>}</div>
      {a.source_quote && a.source_ts && (
        <blockquote className="quote">"{a.source_quote}" <span>[{a.source_call} · {a.source_ts}]</span></blockquote>
      )}
      {a.status === 'confirmed' && <div className="muted small">Confirmed by {a.confirmed_by_name} · {when(a.confirmed_at)}</div>}
      {note && <div className="banner ok">{note}</div>}
      {a.status !== 'confirmed' && !edit && (
        <div className="row">
          {a.status === 'prefilled' && <button className="btn" onClick={() => confirm(false)}>Confirm</button>}
          <button className="btn ghost" onClick={() => setEdit(true)}>
            {a.status === 'prefilled' ? 'Correct' : 'Record answer'}
          </button>
        </div>
      )}
      {edit && (
        <div className="edit">
          <input value={answer} onChange={(e) => setAnswer(e.target.value)} />
          <select value={norm || ''} onChange={(e) => setNorm(e.target.value)}>
            {['yes', 'no', 'partial', 'unknown', 'value'].map((x) => <option key={x}>{x}</option>)}
          </select>
          <div className="row"><button className="btn" onClick={() => confirm(true)}>Save as {actor}</button>
            <button className="btn ghost" onClick={() => setEdit(false)}>Cancel</button></div>
        </div>
      )}
    </div>
  )
}

export default function Application({ actor, onChange, tick, embedded }) {
  const [rows, setRows] = useState([])
  useEffect(() => { api.application().then(setRows) }, [tick])
  const open = rows.filter((r) => ['needs_followup', 'unanswered'].includes(r.status))
  const done = rows.length > 0 && rows.every((r) => r.status === 'confirmed')
  const order = { needs_followup: 0, unanswered: 1, prefilled: 2, confirmed: 3 }
  const sorted = [...rows].sort((a, b) => order[a.status] - order[b.status])

  return (
    <div className="stack">
      <section className="card">
        <h3>Carrier application questions</h3>
        <p className="small">The detailed questions about the business and its security practices. Filled by the same call extraction as the live call. Confirming an intake answer confirms the application
          questions it fills; you can also confirm or correct them here. Hedged answers stay flagged.</p>
        <div className="kpis">
          <div><b>{rows.length}</b><span>questions</span></div>
          <div><b>{rows.length - open.length}</b><span>answered</span></div>
          <div><b>{open.length}</b><span>still open</span></div>
          <div><b>{rows.filter((r) => r.status === 'confirmed').length}</b><span>confirmed</span></div>
        </div>
      </section>

      {rows.length === 0 && <div className="card empty">No intake call yet. Ingest one under “After the call.”</div>}
      <div className="answers">{sorted.map((a) => <Row key={a.id} a={a} actor={actor} onDone={onChange} />)}</div>

      <section className={`card ${done ? '' : 'muted-card'}`}>
        <h3>Apply and bind</h3>
        <p className="small">Once the owner picks an option, these same answers pre-fill the carrier application. The application is
          the client's legal representation: they review and e-sign it; the transcript is never the final word.</p>
        <ol className="small bind-steps">
          <li>Client reviews and e-signs the application.</li>
          <li>The carrier confirms final terms (the quote can differ from the indication).</li>
          <li>Bind: coverage is in force. <span className="muted">Carrier submission and binding are simulated in this prototype.</span></li>
        </ol>
        <button className="btn primary" disabled={!done} title={done ? '' : 'Confirm every answer first'}>Send application for e-signature</button>
      </section>
    </div>
  )
}
