import { useState } from 'react'
export const STATUS = {
  prefilled: { label: 'Recorded · confirm', cls: 's-prefilled' },
  needs_followup: { label: 'Needs follow-up', cls: 's-needs_followup' },
  confirmed: { label: 'Confirmed', cls: 's-confirmed' },
  unanswered: { label: 'Not on a call yet', cls: 's-unanswered' },
}

export function show(v) {
  if (v === null || v === undefined || v === '') return ''
  if (Array.isArray(v)) return v.join(', ')
  if (typeof v === 'number') return v >= 10000 ? v.toLocaleString('en-US') : String(v)
  if (typeof v === 'object') return JSON.stringify(v)
  return String(v)
}

export function money(v) {
  const n = typeof v === 'number' ? v : Number(String(v).replace(/[^0-9.]/g, ''))
  return Number.isFinite(n) && n > 0 ? '$' + n.toLocaleString('en-US') : show(v)
}

/** What the agent tapped live, as display text. */
export function liveText(item) {
  const lv = item.row?.live
  if (!lv) return ''
  if (item.section === 'identity') return lv.corrected && lv.value ? lv.value : lv.confirmed ? 'confirmed as shown' : ''
  if (item.section === 'walkthrough') return lv.text || ''
  return item.type === 'multi' ? (lv.multi || []).join(', ') : show(lv.value)
}

/** Best known answer: agent's live tap, else what the recording said. */
export function answerText(item) {
  const lt = liveText(item)
  if (lt && item.section !== 'identity') return lt
  const r = item.row || {}
  if (r.status && r.status !== 'unanswered' && r.value !== null && r.value !== undefined) {
    return item.key === 'revenue' ? money(r.value) : show(r.value)
  }
  return ''
}

export function StatusPill({ row }) {
  const s = STATUS[row?.status || 'unanswered']
  return <span className={`pill ${s.cls}`}>{s.label}</span>
}

// --- Filtering and folding (Stage 5 is usually several calls and emails: show what's left) ---
export const isAnswered = (status) => status === 'prefilled' || status === 'confirmed'

export function FilterBar({ value, onChange, counts, onAll }) {
  const opts = [['all', 'All'], ['open', 'Not answered'], ['answered', 'Answered']]
  return (
    <div className="filterbar">
      <div className="seg small-seg" role="group" aria-label="Show questions">
        {opts.map(([k, l]) => (
          <button key={k} className={value === k ? 'on' : ''} onClick={() => onChange(k)}>
            {l}{counts && <span className="fcount">{counts[k]}</span>}
          </button>
        ))}
      </div>
      {onAll && <span className="small">
        <button className="link" onClick={() => onAll(true)}>Expand all</button> · <button className="link" onClick={() => onAll(false)}>Collapse all</button>
      </span>}
    </div>
  )
}

export function Fold({ id, title, sub, open, onToggle, open_n, done_n, children, empty }) {
  return (
    <section id={id} className={`fold ${open ? 'is-open' : ''}`}>
      <button className="fold-head" onClick={onToggle} aria-expanded={open}>
        <span className="fold-caret" aria-hidden>{open ? '▾' : '▸'}</span>
        <span className="fold-title">{title}</span>
        {sub && <span className="muted small">{sub}</span>}
        <span className="fold-counts small">
          {open_n > 0 && <span className="pill warn">{open_n} open</span>}
          {done_n > 0 && <span className="pill s-confirmed">{done_n} answered</span>}
        </span>
      </button>
      {open && <div className="fold-body">{empty ? <p className="muted small">{empty}</p> : children}</div>}
    </section>
  )
}

/** Open/closed state per section, all open by default. */
export function useFolds() {
  const [closed, setClosed] = useState({})
  return {
    isOpen: (id) => !closed[id],
    toggle: (id) => setClosed((c) => ({ ...c, [id]: !c[id] })),
    open: (id) => setClosed((c) => ({ ...c, [id]: false })),
    all: (ids, open) => setClosed(Object.fromEntries(ids.map((i) => [i, !open]))),
  }
}
