import { useState } from 'react'
import { api } from '../api.js'

const SUGGESTED = [
  'Why is revenue what it is?',
  'What did each carrier offer?',
  'What still needs follow-up from the call?',
  'Who changed what?',
  'Would a ransomware payment be covered?',
]

export default function AskPanel({ actor, onClose }) {
  const [q, setQ] = useState('')
  const [log, setLog] = useState([])
  const [busy, setBusy] = useState(false)

  const ask = async (question) => {
    if (!question.trim()) return
    setBusy(true)
    try {
      const r = await api.ask(question, actor)
      setLog((l) => [{ q: question, ...r }, ...l])
      setQ('')
    } finally { setBusy(false) }
  }

  return (
    <div className="drawer" role="dialog" aria-label="Ask about this client">
      <header>
        <h3>Ask about this client</h3>
        <button className="link" onClick={onClose}>Close</button>
      </header>
      <p className="muted small">Read-only. Numbers come from the database, reasons from the wiki. Coverage questions go to your CPL.</p>
      <form onSubmit={(e) => { e.preventDefault(); ask(q) }}>
        <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="e.g. Why 13 employees?" disabled={busy} />
        <button className="btn" disabled={busy}>{busy ? '…' : 'Ask'}</button>
      </form>
      <div className="chips">{SUGGESTED.map((s) => <button key={s} className="chip ask" onClick={() => ask(s)}>{s}</button>)}</div>
      <div className="answers-log">
        {log.map((x, i) => (
          <div key={i} className="qa">
            <div className="qa-q">{x.q}</div>
            {x.escalated && <div className="pill warn">Escalated to CPL</div>}
            <pre className="qa-a">{x.answer}</pre>
          </div>
        ))}
      </div>
    </div>
  )
}
