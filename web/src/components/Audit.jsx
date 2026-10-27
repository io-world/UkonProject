import { useEffect, useState } from 'react'
import { api, when } from '../api.js'

const show = (v) => (v == null ? '—' : typeof v === 'number' ? v.toLocaleString() : String(v))

export default function Audit({ tick }) {
  const [rows, setRows] = useState([])
  useEffect(() => { api.audit().then(setRows) }, [tick])
  return (
    <div className="stack">
      <section className="intro">
        <h2>Audit trail</h2>
        <p>Every human decision, with who, when and why. This is the compliance record, and also labeled data: where people
          keep overriding the AI is where the estimators need work.</p>
      </section>
      <ol className="timeline">
        {rows.map((r, i) => (
          <li key={i}>
            <div className="t-when">{when(r.at)}</div>
            <div className="t-body">
              <b>{r.actor}</b> <span className="muted">({r.role.replace('_', ' ')})</span> · {r.event.replaceAll('_', ' ')} · <b>{r.subject}</b>
              {r.event === 'field_change' && (
                <div className="t-detail">{show(r.detail.old)} → {show(r.detail.new)}{r.detail.reason && <> · "{r.detail.reason}"</>}</div>
              )}
            </div>
          </li>
        ))}
        {rows.length === 0 && <li className="muted">No human actions yet.</li>}
      </ol>
    </div>
  )
}
