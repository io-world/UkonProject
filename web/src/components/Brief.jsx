import { useEffect, useState } from 'react'
import { api, money, short } from '../api.js'

const STATUS = { prefilled: 'answered', needs_followup: 'follow up', confirmed: 'confirmed', unanswered: 'not asked yet' }

export default function Brief({ tick }) {
  const [b, setB] = useState(null)
  const [open, setOpen] = useState(() => new Set(['too_small']))
  const toggle = (k) => setOpen((o) => { const n = new Set(o); n.has(k) ? n.delete(k) : n.add(k); return n })
  useEffect(() => { api.brief().then(setB) }, [tick])
  if (!b) return <div className="muted">Loading brief…</div>
  const r = b.recommended

  return (
    <div className="stack">
      <section className="intro">
        <h2>Stage 4 · Equip the agent</h2>
        <p>Everything the producer needs before presenting the pack: talking points, likely objections and answers, and the policy specimens. AI tailors the pitch and selects objection answers from a
          CPL-approved library; it doesn't invent new ones, and it never interprets coverage.</p>
      </section>

      <div className="brief-grid">
        <section className="card">
          <h3>60-second pitch</h3>
          <blockquote className="pitch">{b.pitch}</blockquote>
          {r && <p className="small">Lead with <b>{short(r.limit)}</b> from {b.carrier}: <b>{money(r.monthly)}/mo</b> ({money(r.premium)}/yr), {money(r.deductible)} deductible.</p>}
        </section>

        <section className="card">
          <div className="obj-head">
            <h3>Likely objections</h3>
            <div className="row">
              <button className="link" onClick={() => setOpen(new Set(b.objections.map((o) => o.key)))}>Expand all</button>
              <button className="link" onClick={() => setOpen(new Set())}>Collapse all</button>
            </div>
          </div>
          {b.objections.map((o) => (
            <div key={o.key} className={`obj ${open.has(o.key) ? 'open' : ''}`}>
              <button className="obj-q" onClick={() => toggle(o.key)} aria-expanded={open.has(o.key)}
                      aria-controls={`obj-${o.key}`}>
                <span className="obj-icon" aria-hidden>{open.has(o.key) ? '−' : '+'}</span>
                <span className="obj-text">"{o.objection}"</span>
                {o.escalate && <span className="pill warn">CPL</span>}
              </button>
              {open.has(o.key) && (
                <div className="obj-a" id={`obj-${o.key}`}>
                  <div className="label">Say this (tailored)</div><p>{o.tailored}</p>
                  <div className="label">Approved source answer</div><p className="muted">{o.approved}</p>
                </div>
              )}
            </div>
          ))}
        </section>

        <section className="card">
          <h3>Loop in your Cyber Practice Leader when…</h3>
          <ul>{b.escalations.map((e) => <li key={e}>{e}</li>)}</ul>
        </section>

        <section className="card">
          <h3>Policy specimen · {b.specimen.form}</h3>
          <p className="muted small">AI points to where each item is in the carrier form; it doesn't interpret it. In production every reference must match real text on that page, or it's dropped.</p>
          <table className="spec">
            <thead><tr><th>Topic</th><th>Section</th><th>Page</th></tr></thead>
            <tbody>{b.specimen.items?.map((i) => <tr key={i.topic}><td>{i.topic}</td><td>{i.section}</td><td>{i.page}</td></tr>)}</tbody>
          </table>
          <p className="small">Carrier conditions: {b.conditions.join(' · ')}</p>
        </section>

        {b.research?.length > 0 && (
          <section className="card wide">
            <h3>Talking points from recent events</h3>
            <p className="muted small">Gathered from the web by the <code>client-research</code> skill, every item cited. Use them to make
              "could this happen to us?" concrete. Don't speculate past what the source says.</p>
            <ul className="news-brief">
              {b.research.map((r) => (
                <li key={r.id}><b>{r.headline}</b> <span className="pill">{r.category}</span>
                  <div className="small">{r.for_this_client}</div>
                  <div className="muted small"><a href={r.url} target="_blank" rel="noreferrer">{r.source}</a>, {r.date}</div></li>
              ))}
            </ul>
          </section>
        )}

        <section className="card wide">
          <h3>Application preview: what the client will be asked</h3>
          <p className="muted small">Pre-qualify these in the meeting. Gate questions can decide eligibility.</p>
          <ul className="appq">
            {b.application_preview.map((q) => (
              <li key={q.key}>
                <span>{q.plain}</span>
                {q.gate && <span className="pill">gate</span>}
                {b.application_status[q.key] && <span className={`pill s-${b.application_status[q.key]}`}>{STATUS[b.application_status[q.key]]}</span>}
              </li>
            ))}
          </ul>
        </section>
      </div>
    </div>
  )
}
