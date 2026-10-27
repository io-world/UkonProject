import { useEffect, useState } from 'react'
import { api, when } from '../api.js'
import { FilterBar, Fold, isAnswered, useFolds } from './intake/shared.jsx'

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
      {a.source_quote && a.source_quote !== 'From the database' && (
        <blockquote className="quote">"{a.source_quote}" <span>[{a.source_call}{a.source_ts ? ` · ${a.source_ts}` : ''}]</span></blockquote>
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
  const [filter, setFilter] = useState('all')
  const folds = useFolds()
  const groups = [
    { id: 'ap-open', title: 'Still open', sub: 'Needs follow-up or not asked yet', match: (r) => !isAnswered(r.status) },
    { id: 'ap-confirm', title: 'Answered, to confirm', sub: 'From a call or email; a person confirms', match: (r) => r.status === 'prefilled' },
    { id: 'ap-done', title: 'Confirmed', match: (r) => r.status === 'confirmed' },
  ].filter((g) => filter === 'all' || (filter === 'open' ? g.id === 'ap-open' : g.id !== 'ap-open'))
  const fcounts = { all: rows.length, open: rows.filter((r) => !isAnswered(r.status)).length, answered: rows.filter((r) => isAnswered(r.status)).length }

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
      {rows.length > 0 && <FilterBar value={filter} onChange={setFilter} counts={fcounts} onAll={(o) => folds.all(groups.map((g) => g.id), o)} />}
      {rows.length > 0 && groups.map((g) => {
        const these = sorted.filter(g.match)
        return (
          <Fold key={g.id} id={g.id} title={g.title} sub={g.sub} open={folds.isOpen(g.id)} onToggle={() => folds.toggle(g.id)}
                open_n={g.id === 'ap-open' ? these.length : 0} done_n={g.id === 'ap-open' ? 0 : these.length}
                empty={these.length === 0 ? 'None.' : null}>
            <div className="answers">{these.map((a) => <Row key={a.id} a={a} actor={actor} onDone={onChange} />)}</div>
          </Fold>
        )
      })}

      <section className={`card ${done ? '' : 'muted-card'}`}>
        <h3>Sign and submit</h3>
        <p className="small">These answers pre-fill the application for the option the owner chose. The application is
          the client's legal representation: they review and e-sign it; the transcript is never the final word.
          The carrier's firm quote, final terms and binding are Stage 6.</p>
        <button className="btn primary" disabled={!done} title={done ? '' : 'Confirm every answer first'}>Send application for e-signature</button>
      </section>
    </div>
  )
}
