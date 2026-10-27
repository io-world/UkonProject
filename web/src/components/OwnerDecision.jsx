import { useEffect, useState } from 'react'
import { api, money, when, SOURCE_LABEL } from '../api.js'

// Stage 5 opens with the owner's answer to the proposal pack: which option, or "not now" and why.
// Append-only: changing it records a new decision; the reason list feeds the deal record (why deals are lost).
export default function OwnerDecision({ actor, onChange, tick }) {
  const [d, setD] = useState(null)
  const [edit, setEdit] = useState(false)
  const [pick, setPick] = useState('')
  const [mode, setMode] = useState('chose')
  const [reason, setReason] = useState('')
  const [note, setNote] = useState('')
  const [source, setSource] = useState('conversation')
  const [err, setErr] = useState(null)
  useEffect(() => { api.close().then((x) => {
    setD(x)
    const def = x.offers.find((o) => o.carrier === x.selected_carrier && o.tier === 'recommended') || x.offers[0]
    if (def) setPick(`${def.carrier}|${def.tier}`)
  }) }, [tick])
  if (!d) return null
  const cur = d.present
  const save = async () => {
    setErr(null)
    const [carrier, tier] = pick.split('|')
    try {
      await api.decide(mode === 'chose'
        ? { stage: 'present', decision: 'chose', carrier, tier, note, source_type: source }
        : { stage: 'present', decision: 'not_now', reason, note, source_type: source }, actor)
      setEdit(false); setNote(''); onChange()
    } catch (e) { setErr(e.message) }
  }

  return (
    <section className={`card decision ${cur ? (cur.decision === 'chose' ? 'd-yes' : 'd-no') : ''}`}>
      <div className="row" style={{ justifyContent: 'space-between' }}>
        <h3>The owner's decision on the proposal</h3>
        {cur && !edit && <button className="btn ghost sm" onClick={() => setEdit(true)}>Record a change</button>}
      </div>
      {cur && !edit && (
        <p className="small">
          {cur.decision === 'chose'
            ? <><b>Chose {cur.carrier}, {cur.option_label}.</b> The application below is for this option.</>
            : <><b>Not now: {cur.reason_label}.</b>{cur.note && <> “{cur.note}”</>} Stage 6 records the deal as lost with this reason.</>}
          <span className="muted"> · {cur.actor_name}, {when(cur.created_at)} · from {SOURCE_LABEL[cur.source_type].toLowerCase()}</span>
        </p>
      )}
      {(!cur || edit) && (
        <div className="stack-s">
          <p className="small muted">After walking the owner through the pack, record what they decided. A "not now" needs the
            reason they gave: those reasons are how UKON learns why deals are lost.</p>
          <div className="seg small-seg">
            <button className={mode === 'chose' ? 'on' : ''} onClick={() => setMode('chose')}>Chose an option</button>
            <button className={mode === 'not_now' ? 'on' : ''} onClick={() => setMode('not_now')}>Not now</button>
          </div>
          {mode === 'chose' ? (
            <div className="offer-pick">
              {d.offers.map((o) => (
                <label key={`${o.carrier}|${o.tier}`} className={`offer ${pick === `${o.carrier}|${o.tier}` ? 'on' : ''}`}>
                  <input type="radio" name="offer" checked={pick === `${o.carrier}|${o.tier}`} disabled={o.expired}
                         onChange={() => setPick(`${o.carrier}|${o.tier}`)} />
                  <span><b>{o.carrier}</b> · {o.option_label}</span>
                  <span className="muted">{money(o.premium)}/yr{o.expired && ' · expired'}</span>
                </label>
              ))}
            </div>
          ) : (
            <div className="row">
              <select value={reason} onChange={(e) => setReason(e.target.value)}>
                <option value="">Reason the owner gave…</option>
                {Object.entries(d.reasons).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
              </select>
            </div>
          )}
          <div className="row">
            <input className="grow" placeholder={mode === 'chose' ? 'Note (optional)' : 'In their words (optional; required for "Other")'}
                   value={note} onChange={(e) => setNote(e.target.value)} />
            <select value={source} onChange={(e) => setSource(e.target.value)} title="Where this came from">
              {['conversation', 'manual', 'clipboard', 'api'].map((s) => <option key={s} value={s}>{SOURCE_LABEL[s]}</option>)}
            </select>
          </div>
          {err && <div className="err small">{err}</div>}
          <div className="row">
            <button className="btn primary" disabled={mode === 'not_now' ? !reason : !pick} onClick={save}>Save as {actor}</button>
            {edit && <button className="btn ghost" onClick={() => setEdit(false)}>Cancel</button>}
          </div>
        </div>
      )}
    </section>
  )
}
