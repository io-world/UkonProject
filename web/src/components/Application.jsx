import { useEffect, useState } from 'react'
import { api, when } from '../api.js'
import { FilterBar, Fold, isAnswered, useFolds } from './intake/shared.jsx'

// Read-only. Every answer here comes from a call or email and is confirmed once, in "2 · Check the recording".
// The owner's e-signature is the final confirmation.
const LABEL = { prefilled: 'To confirm', needs_followup: 'Needs follow-up', confirmed: 'Confirmed', unanswered: 'Not asked yet' }

function Row({ a }) {
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
    </div>
  )
}

export default function Application({ tick, goReview }) {
  const [rows, setRows] = useState([])
  useEffect(() => { api.application().then(setRows) }, [tick])
  const open = rows.filter((r) => ['needs_followup', 'unanswered'].includes(r.status))
  const toConfirm = rows.filter((r) => r.status === 'prefilled')
  const done = rows.length > 0 && rows.every((r) => r.status === 'confirmed')
  const order = { needs_followup: 0, unanswered: 1, prefilled: 2, confirmed: 3 }
  const sorted = [...rows].sort((a, b) => order[a.status] - order[b.status])
  const [filter, setFilter] = useState('all')
  const folds = useFolds()
  const groups = [
    { id: 'ap-open', title: 'Still open', sub: 'Needs follow-up or not asked yet', match: (r) => !isAnswered(r.status) },
    { id: 'ap-confirm', title: 'Answered, waiting on confirmation', sub: 'Confirmed in 2 · Check the recording', match: (r) => r.status === 'prefilled' },
    { id: 'ap-done', title: 'Confirmed', match: (r) => r.status === 'confirmed' },
  ].filter((g) => filter === 'all' || (filter === 'open' ? g.id === 'ap-open' : g.id !== 'ap-open'))
  const fcounts = { all: rows.length, open: rows.filter((r) => !isAnswered(r.status)).length, answered: rows.filter((r) => isAnswered(r.status)).length }

  return (
    <div className="stack">
      <section className="card">
        <h3>Carrier application questions</h3>
        <p className="small">What the carrier's application will say, filled from the calls and emails. Read-only: answers are
          confirmed or corrected once, in <button className="link" onClick={goReview}>2 · Check the recording</button>, and show up here.</p>
        <div className="kpis">
          <div><b>{rows.length}</b><span>questions</span></div>
          <div><b>{rows.filter((r) => r.status === 'confirmed').length}</b><span>confirmed</span></div>
          <div><b>{toConfirm.length}</b><span>to confirm</span></div>
          <div><b>{open.length}</b><span>still open</span></div>
        </div>
      </section>

      {rows.length === 0 && <div className="card empty">No call yet. Take one in under “2 · Check the recording.”</div>}
      {rows.length > 0 && <FilterBar value={filter} onChange={setFilter} counts={fcounts} onAll={(o) => folds.all(groups.map((g) => g.id), o)} />}
      {rows.length > 0 && groups.map((g) => {
        const these = sorted.filter(g.match)
        return (
          <Fold key={g.id} id={g.id} title={g.title} sub={g.sub} open={folds.isOpen(g.id)} onToggle={() => folds.toggle(g.id)}
                open_n={g.id === 'ap-open' ? these.length : 0} done_n={g.id === 'ap-open' ? 0 : these.length}
                empty={these.length === 0 ? 'None.' : null}>
            <div className="answers">{these.map((a) => <Row key={a.id} a={a} />)}</div>
          </Fold>
        )
      })}

      <section className={`card ${done ? '' : 'muted-card'}`}>
        <h3>Sign and submit</h3>
        <p className="small">The application is the client's own statement: they review and e-sign it, and the transcript is never
          the final word. The carrier's firm quote, final terms and binding are Stage 6.</p>
        {!done && rows.length > 0 && (
          <p className="small">{toConfirm.length + open.length} answer{toConfirm.length + open.length === 1 ? '' : 's'} still to confirm or follow up.{' '}
            <button className="link" onClick={goReview}>Go to 2 · Check the recording</button></p>
        )}
        <button className="btn primary" disabled={!done} title={done ? '' : 'Every answer is confirmed in 2 · Check the recording first'}>Send application for e-signature</button>
      </section>
    </div>
  )
}
