import { useEffect, useState } from 'react'
import { api, money, short } from '../api.js'
import WikiChat from './WikiChat.jsx'

// A wiki path, printed in full and openable (pages as text, carrier letters as PDF). "#Section" names a heading.
export function WikiPath({ path }) {
  const [file, section] = path.split('#')
  return (
    <a className="wpath" href={api.wikiUrl(file)} target="_blank" rel="noreferrer" title="Open in the wiki">
      {file}{section && <span className="wpath-sec"> § {section}</span>}
    </a>
  )
}

function Sources({ label = 'Source', paths, note }) {
  if (!paths?.length) return null
  return (
    <div className="sources-line">
      <span className="sources-k">{label}</span>
      {paths.map((p) => <WikiPath key={p} path={p} />)}
      {note && <span className="muted">{note}</span>}
    </div>
  )
}

const NOTE_KIND = { public: 'public record', call: 'simulated call', ai: 'AI-suggested' }
const STATUS = { prefilled: 'answered', needs_followup: 'follow up', confirmed: 'confirmed', unanswered: 'not asked yet' }

export default function Brief({ tick, actor }) {
  const [b, setB] = useState(null)
  const [open, setOpen] = useState(() => new Set(['too_small']))
  const toggle = (k) => setOpen((o) => { const n = new Set(o); n.has(k) ? n.delete(k) : n.add(k); return n })
  useEffect(() => { api.brief().then(setB) }, [tick])
  if (!b) return <div className="muted">Loading brief…</div>
  const r = b.recommended
  const src = b.sources || {}

  return (
    <div className="stack">
      <section className="intro">
        <h2>Stage 4 · Equip the agent</h2>
        <p>Everything the producer needs before presenting the pack: talking points, likely objections and answers, and the policy specimens. AI tailors the pitch and selects objection answers from a
          CPL-approved library; it doesn't invent new ones, and it never interprets coverage.</p>
      </section>

      <div className="brief-grid">
        <WikiChat actor={actor} />

        <section className="card">
          <h3>60-second pitch</h3>
          <blockquote className="pitch">{b.pitch}</blockquote>
          {r && <p className="small">Lead with <b>{short(r.limit)}</b> from {b.carrier}: <b>{money(r.monthly)}/mo</b> ({money(r.premium)}/yr), {money(r.deductible)} deductible.</p>}
          <Sources label="Written by AI from" paths={src.pitch} />
          <Sources label="Figures from" paths={src.pitch_figures} note="(database, Stage 2)" />
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
          <Sources label="Approved answers from" paths={src.objections} />
        </section>

        <section className="card">
          <h3>Loop in your Cyber Practice Leader when…</h3>
          <ul>{b.escalations.map((e) => <li key={e}>{e}</li>)}</ul>
          <Sources paths={src.escalations} />
        </section>

        <section className="card">
          <h3>Policy specimen · {b.specimen.form}</h3>
          <p className="muted small">AI points to where each item is in the carrier form; it doesn't interpret it. In production every reference must match real text on that page, or it's dropped.</p>
          <table className="spec">
            <thead><tr><th>Topic</th><th>Section</th><th>Page</th></tr></thead>
            <tbody>{b.specimen.items?.map((i) => <tr key={i.topic}><td>{i.topic}</td><td>{i.section}</td><td>{i.page}</td></tr>)}</tbody>
          </table>
          <p className="small">Carrier conditions: {b.conditions.join(' · ')}</p>
          <Sources label="Form number from" paths={src.specimen_form} />
          <Sources label="Sections and pages from" paths={src.specimen} note="(simulated: no real specimen PDF yet)" />
          <Sources label="Conditions from" paths={src.conditions} />
        </section>

        {b.people?.length > 0 && (
          <section className="card wide">
            <h3>People at the practice</h3>
            <p className="muted small">Who you'll be talking to, from the client's wiki. Every note is labeled:
              <span className="pill k-public">public record</span> real and sourced,
              <span className="pill k-call">simulated call</span> invented for the demo and tied to a role, not a real person,
              <span className="pill k-ai">AI-suggested</span> an opener written from the public notes. Nothing personal is made up about a real person.</p>
            <div className="people">
              {b.people.map((p) => (
                <article key={p.name} className={`person ${p.simulated ? 'sim' : ''}`}>
                  <header><b>{p.name}</b><span className="muted small">{p.role}</span></header>
                  <ul>
                    {p.notes.map((n, i) => (
                      <li key={i}>
                        <span className={`pill k-${n.kind}`}>{NOTE_KIND[n.kind]}</span>
                        <span>{n.text}</span>
                        <WikiPath path={n.source} />
                      </li>
                    ))}
                  </ul>
                </article>
              ))}
            </div>
            <Sources label="Compiled in" paths={src.people} />
          </section>
        )}

        {b.research?.length > 0 && (
          <section className="card wide">
            <h3>Talking points from recent events</h3>
            <p className="muted small">Gathered from the web by the <code>client-research</code> skill, every item cited. Use them to make
              "could this happen to us?" concrete. Don't speculate past what the source says.</p>
            <ul className="news-brief">
              {b.research.map((r) => (
                <li key={r.id}><b>{r.headline}</b> <span className="pill">{r.category}</span>
                  <div className="small">{r.for_this_client}</div>
                  <div className="muted small"><a href={r.url} target="_blank" rel="noreferrer">{r.source}</a>, {r.date} · <WikiPath path={r.wiki} /></div></li>
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
          <Sources label="Questions from" paths={src.application?.slice(0, 1)} />
          <Sources label="Answers so far from" paths={src.application?.slice(1)} />
        </section>
      </div>
    </div>
  )
}
