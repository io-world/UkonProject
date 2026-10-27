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
