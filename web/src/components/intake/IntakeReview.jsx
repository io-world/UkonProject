import { useState } from 'react'
import { api, when } from '../../api.js'
import { StatusPill, liveText, money, show } from './shared.jsx'

function ItemCard({ it, actor, onDone }) {
  const r = it.row || {}
  const [edit, setEdit] = useState(false)
  const [val, setVal] = useState('')
  const [msg, setMsg] = useState(null)
  const recorded = it.key === 'revenue' && typeof r.value === 'number' ? money(r.value) : show(r.value)
  const tapped = liveText(it)

  const confirm = async (value) => {
    const res = await api.intakeConfirm(it.key, actor, value)
    if (res.applied_to?.length) setMsg(`Applied to ${res.applied_to.join(', ')} in the report (logged).`)
    setEdit(false); onDone()
  }
  const parseVal = () => {
    if (it.type === 'multi') return val.split(',').map((x) => x.trim()).filter(Boolean)
    if (it.type === 'number' || it.key === 'revenue') { const n = Number(val.replace(/[^0-9.]/g, '')); return Number.isFinite(n) ? n : val }
    return val
  }

  return (
    <div className={`ans s-${r.status} ${r.conflict ? 'conflict' : ''}`}>
      <div className="ans-head">
        <div className="ans-q"><b>{it.ref}</b> · {it.label}</div>
        <StatusPill row={r} />
      </div>
      <div className="ans-a">{recorded || r.answer || <span className="muted">No answer yet</span>}</div>
      {r.answer && recorded && r.answer !== recorded && <div className="small muted">{r.answer}</div>}
      {r.source_quote && r.source_quote !== 'From the database' && (
        <blockquote className="quote">“{r.source_quote}” <span>[{r.source_call}{r.source_ts ? ` · ${r.source_ts}` : ''}]</span></blockquote>
      )}
      {tapped && <div className="small">Agent tapped live: <b>{tapped}</b>{r.live_by_name && <span className="muted"> · {r.live_by_name}</span>}</div>}
      {(r.notes || []).map((n, i) => (
        <div key={i} className={n.startsWith('CONFLICT') ? 'banner warn small' : 'small note-line'}>{n}</div>
      ))}
      {it.app_keys?.length > 0 && <div className="small muted">Fills application: {it.app_keys.join(', ')}</div>}
      {r.status === 'confirmed' && <div className="muted small">Confirmed by {r.confirmed_by_name} · {when(r.confirmed_at)}</div>}
      {msg && <div className="banner ok small">{msg}</div>}
      {r.status !== 'confirmed' && it.section !== 'walkthrough' && !edit && (
        <div className="row">
          {r.status !== 'unanswered' && <button className="btn" onClick={() => confirm(undefined)}>Confirm</button>}
          <button className="btn ghost" onClick={() => { setVal(tapped || recorded || ''); setEdit(true) }}>
            {r.status === 'unanswered' ? 'Record answer' : 'Correct'}</button>
        </div>
      )}
      {edit && (
        <div className="edit">
          {it.options ? (
            <div className="opts">{it.options.map((o) => (
              <button key={o} className={`opt ${(it.type === 'multi' ? val.split(',').map((x) => x.trim()).includes(o) : val === o) ? 'on' : ''}`}
                      onClick={() => {
                        if (it.type !== 'multi') return setVal(o)
                        const cur = val.split(',').map((x) => x.trim()).filter(Boolean)
                        setVal((cur.includes(o) ? cur.filter((x) => x !== o) : [...cur, o]).join(', '))
                      }}>{o}</button>
            ))}</div>
          ) : <input value={val} onChange={(e) => setVal(e.target.value)} placeholder={it.ph || ''} />}
          <div className="row">
            <button className="btn" onClick={() => confirm(parseVal())}>Save as {actor}</button>
            <button className="btn ghost" onClick={() => setEdit(false)}>Cancel</button>
          </div>
        </div>
      )}
    </div>
  )
}

export default function IntakeReview({ data, actor, onChange }) {
  const [busy, setBusy] = useState(null)
  const [result, setResult] = useState(null)
  const [err, setErr] = useState(null)
  const order = { needs_followup: 0, unanswered: 1, prefilled: 2, confirmed: 3 }
  const sections = [
    ['identity', 'Section 0 · Business identity'],
    ['exposure', 'Section 1 · Exposure questions'],
    ['walkthrough', 'Section 2 · Walkthrough reactions'],
  ]
  const ingest = async (file) => {
    setBusy(file); setErr(null)
    try { setResult(await api.intakeIngest(file, actor)); onChange() } catch (e) { setErr(e.message) } finally { setBusy(null) }
  }
  const asked = data.items.filter((i) => i.section !== 'walkthrough')
  const count = (s) => asked.filter((i) => (i.row?.status || 'unanswered') === s).length

  return (
    <div className="stack">
      <div className="review-top">
        <section className="card">
          <h3>Calls</h3>
          <ol className="calls">
            {data.calls.map((c) => (
              <li key={c.call_ref}><code>{c.call_ref}</code> · {c.answered} items updated
                {c.flagged > 0 && <> · <span className="pill warn">{c.flagged} flagged</span></>}
                <span className="muted small"> · {when(c.ingested_at)}</span></li>
            ))}
            {data.calls.length === 0 && <li className="muted">No calls ingested yet.</li>}
          </ol>
          <h4 className="mt">Transcripts in the wiki</h4>
          <ul className="transcripts">
            {data.transcripts.map((t) => (
              <li key={t.file}><code>{t.file}</code>
                <button className="btn ghost" disabled={!!busy} onClick={() => ingest(t.file)}>
                  {busy === t.file ? 'Ingesting…' : t.ingested ? 'Re-ingest' : 'Ingest'}</button></li>
            ))}
          </ul>
          <p className="muted small">From Wispr Flow: in Claude Code, run the <code>call-ingest</code> skill. It saves the transcript here
            and ingests it. Re-ingesting an older call never overwrites a newer call's answers.</p>
          {result && <div className="banner ok small">{result.call_ref}: {result.intake_updated} items updated, {result.flagged} flagged,
            {' '}{result.conflicts} conflicts with live taps, {result.coverage_questions} for a CPL. Exposure now {result.exposure} ({result.band}).
            {result.provenance !== 'live' && ' (cached extraction)'}</div>}
          {err && <div className="banner warn small">{err}</div>}
        </section>
        <section className="card">
          <h3>Status</h3>
          <div className="kpis">
            <div><b>{count('confirmed')}</b><span>confirmed</span></div>
            <div><b>{count('prefilled')}</b><span>recorded, to confirm</span></div>
            <div><b>{count('needs_followup')}</b><span>need follow-up</span></div>
            <div><b>{count('unanswered')}</b><span>not covered yet</span></div>
          </div>
          <p className="small">Open items don't block the client pack; it shows them as “to confirm.” Confirming an answer also confirms
            the application questions it fills, and a confirmed revenue or record count updates the report (logged).</p>
          <h4 className="mt">Coverage questions for a CPL</h4>
          <ul className="esc">{data.escalations.map((e) => (
            <li key={e.id}>“{e.text}” <span className="muted small">{e.call_time} · {e.source === 'call' ? e.call_ref : `logged live by ${e.created_by_name}`}</span></li>
          ))}{data.escalations.length === 0 && <li className="muted small">None.</li>}</ul>
        </section>
      </div>

      {sections.map(([sec, title]) => (
        <section key={sec}>
          <h3 className="section-h">{title}</h3>
          <div className="answers">
            {data.items.filter((i) => i.section === sec)
              .sort((a, b) => order[a.row?.status || 'unanswered'] - order[b.row?.status || 'unanswered'])
              .map((it) => <ItemCard key={it.key} it={it} actor={actor} onDone={onChange} />)}
          </div>
        </section>
      ))}
    </div>
  )
}
