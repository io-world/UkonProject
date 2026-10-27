import { useEffect, useState } from 'react'
import { api, money, when } from '../api.js'
import ReportDocument from './ReportDocument.jsx'
import { FieldCard } from './Enrichment.jsx'

const STATE_LABEL = {
  ai_draft: 'AI draft', agent_edited: 'Agent edited', submitted: 'Submitted · locked',
  sent: 'Sent to client', superseded: 'Superseded', withdrawn: 'Withdrawn (submit undone)',
}
const LOCKED_STATES = ['submitted', 'sent', 'superseded', 'withdrawn']

function Slider({ label, k, fact, min, max, step, fmt, actor, onApplied, aiOverride }) {
  const current = Number(fact?.value ?? aiOverride)
  const ai = Number(fact?.ai_value ?? aiOverride)
  const [v, setV] = useState(current)
  const [reason, setReason] = useState('')
  useEffect(() => setV(current), [current])
  const dirty = v !== current
  return (
    <div className="slider">
      <div className="slider-top">
        <span>{label}</span>
        <strong>{fmt(v)}</strong>
      </div>
      <input type="range" min={min} max={max} step={step} value={v} onChange={(e) => setV(Number(e.target.value))} />
      <div className="slider-meta">
        <span>AI recommended <b>{fmt(ai)}</b></span>
        {current !== ai && <span className="you">In report: {fmt(current)}</span>}
      </div>
      {dirty && (
        <div className="apply">
          <input placeholder="Why? (logged with your name)" value={reason} onChange={(e) => setReason(e.target.value)} />
          <button className="btn" onClick={async () => { await api.changeField(k, v, actor, reason || null); setReason(''); onApplied() }}>Apply</button>
          <button className="btn ghost" onClick={() => setV(current)}>Reset</button>
        </div>
      )}
    </div>
  )
}

export default function ReportTab({ data, actor, onChange, tick }) {
  const [mode, setMode] = useState('agent')
  const [rep, setRep] = useState(null)
  const [versions, setVersions] = useState([])
  const [busy, setBusy] = useState(false)
  const [viewing, setViewing] = useState(null)      // a locked version number, shown read-only
  const [undoOpen, setUndoOpen] = useState(false)
  const [undoReason, setUndoReason] = useState('')
  const [err, setErr] = useState(null)

  useEffect(() => {
    const load = viewing ? api.reportVersion(viewing) : api.report(mode)
    load.then(setRep).catch((e) => setErr(e.message))
    api.versions().then(setVersions)
  }, [mode, tick, viewing])

  if (!rep) return <div className="muted">Loading report…</div>
  const s = rep.snapshot
  const v = rep.version
  const locked = v && ['submitted', 'sent'].includes(v.state)
  const lockedVersions = versions.filter((x) => LOCKED_STATES.includes(x.state))
  const showControls = mode === 'agent' && !viewing

  const act = async (fn) => {
    setBusy(true); setErr(null)
    try { await fn(actor) } catch (e) { setErr(e.message) } finally { setBusy(false); onChange() }
  }
  const undo = async () => {
    setBusy(true); setErr(null)
    try { await api.undoSubmit(actor, undoReason); setUndoOpen(false); setUndoReason('') }
    catch (e) { setErr(e.message) } finally { setBusy(false); onChange() }
  }

  const inputs = data.fields.filter((f) => ['employee_count', 'dentists', 'records_estimate'].includes(f.key) || f.kind === 'benchmark')

  return (
    <div className="stack">
      <section className="intro">
        <h2>Stage 3 · Client proposal pack</h2>
        <p>Built from the carriers' indications: why cyber matters to this practice, the options, and what they cost, in plain
          language for an owner who isn't technical. AI writes the prose; every figure comes from the database, and carrier
          numbers can't be moved here. The agent adjusts estimates, submits a locked version, and sends it. Questions the owner
          hasn't answered yet show as “to confirm”; they never block the pack.</p>
      </section>
      <div className="report-bar">
        <div className="seg" role="tablist" aria-label="Report view">
          <button className={mode === 'agent' && !viewing ? 'on' : ''} onClick={() => { setViewing(null); setMode('agent') }}>Agent view</button>
          <button className={mode === 'client' && !viewing ? 'on' : ''} onClick={() => { setViewing(null); setMode('client') }}>Client view</button>
        </div>
        <label className="locked-pick">
          <span>Locked versions</span>
          <select value={viewing ?? ''} onChange={(e) => setViewing(e.target.value ? Number(e.target.value) : null)}
                  disabled={lockedVersions.length === 0}>
            <option value="">{lockedVersions.length ? 'Current (not a locked version)' : 'None submitted yet'}</option>
            {lockedVersions.map((x) => (
              <option key={x.version_no} value={x.version_no}>
                v{x.version_no} · {STATE_LABEL[x.state]} · {x.submitted_by || x.created_by} · {when(x.submitted_at || x.created_at)}
              </option>
            ))}
          </select>
        </label>
        {v && <div className={`vbadge s-${v.state}`}>v{v.version_no} · {STATE_LABEL[v.state]}</div>}
        {v && <a className="btn ghost" href={api.htmlUrl(viewing || (mode === 'client' ? v.version_no : null))} target="_blank" rel="noreferrer">Open HTML report ↗</a>}
        {showControls && v && (
          <div className="row">
            {!locked && <button className="btn" disabled={busy} onClick={() => act(api.submit)}>Submit & lock v{v.version_no}</button>}
            {v.state === 'submitted' && !undoOpen && <button className="btn ghost" disabled={busy} onClick={() => setUndoOpen(true)}>Undo submit</button>}
            {v.state === 'submitted' && <button className="btn primary" disabled={busy} onClick={() => act(api.send)}>Send to client</button>}
            {v.state === 'sent' && <span className="muted">Sent to the client, so it can't be undone. Any change creates v{v.version_no + 1}.</span>}
            {v.state === 'submitted' && !undoOpen && <span className="muted">Locked. Any change creates v{v.version_no + 1}.</span>}
          </div>
        )}
        {showControls && undoOpen && v?.state === 'submitted' && (
          <div className="undo-box">
            <input placeholder="Why undo? (optional, logged with your name)" value={undoReason} onChange={(e) => setUndoReason(e.target.value)} />
            <button className="btn" disabled={busy} onClick={undo}>Undo submit of v{v.version_no}</button>
            <button className="btn ghost" onClick={() => setUndoOpen(false)}>Cancel</button>
            <span className="muted small">v{v.version_no} stays on record as withdrawn (its file doesn't change); editing continues in v{v.version_no + 1}.</span>
          </div>
        )}
      </div>
      {err && <div className="err small">{err}</div>}
      {viewing && v && (
        <div className="banner warn">
          Viewing v{v.version_no} read-only · {STATE_LABEL[v.state]}
          {v.state === 'withdrawn' && v.withdraw_reason ? ` · reason: ${v.withdraw_reason}` : ''}
          {' '}<button className="link" onClick={() => setViewing(null)}>Back to the current version</button>
        </div>
      )}

      {mode === 'client' && !viewing && !v && (
        <div className="card empty">Nothing has been submitted yet. The client only ever sees a locked version.</div>
      )}

      {s && (
        <div className={showControls ? 'split' : ''}>
          {showControls && (
            <aside className="controls">
              <h3>Adjust estimates</h3>
              <p className="muted small">Estimates move. Carrier numbers don't: premiums, limits and deductibles are locked to the indications.</p>
              {s.revenue_drift?.needs_refresh && (
                <div className="banner warn">
                  Revenue is {Math.round(s.revenue_drift.drift * 100)}% from what carriers priced on
                  (tolerance ±{Math.round(s.revenue_drift.tolerance * 100)}%). <b>Indication needs refresh</b>; premiums are not recalculated here.
                </div>
              )}
              <Slider label="Annual revenue" k="annual_revenue" fact={s.facts.annual_revenue} min={1000000} max={3500000}
                      step={50000} fmt={money} actor={actor} onApplied={onChange} />
              <Slider label="Employees" k="employee_count" fact={s.facts.employee_count} min={1} max={40} step={1}
                      fmt={(n) => n} actor={actor} onApplied={onChange} />
              <Slider label="Exposure score" k="exposure_score" fact={{ value: s.exposure.score, ai_value: s.exposure.ai_score }}
                      min={0} max={100} step={1} fmt={(n) => `${n} / 100`} actor={actor} onApplied={onChange} />
              <Slider label="Patient records held" k="records_estimate" fact={s.facts.records_estimate} min={1000} max={20000}
                      step={500} fmt={(n) => Number(n).toLocaleString()} actor={actor} onApplied={onChange} />
              <div className="slider">
                <div className="slider-top"><span>Carrier shown to client</span></div>
                <select value={s.selected_carrier}
                        onChange={async (e) => { await api.changeField('selected_carrier', e.target.value, actor, 'Agent switched carrier'); onChange() }}>
                  {s.carriers.map((c) => <option key={c.carrier}>{c.carrier}</option>)}
                </select>
              </div>

              <p className="small muted">On disk: <code>reports/sloanslake/current.html</code> (working draft) and <code>v&lt;N&gt;.html</code> for each submitted version.</p>
              <h3 className="mt">Versions</h3>
              <table className="vtable">
                <thead><tr><th>v</th><th>State</th><th>Revenue</th><th>By</th><th>When</th></tr></thead>
                <tbody>
                  {versions.map((x) => (
                    <tr key={x.version_no} className={`v-${x.state}`} title={x.state === 'withdrawn' ? `Withdrawn by ${x.withdrawn_by}${x.withdraw_reason ? `: ${x.withdraw_reason}` : ''}` : ''}>
                      <td>{x.version_no}</td><td>{STATE_LABEL[x.state]}</td><td>{money(x.revenue)}</td>
                      <td>{x.withdrawn_by || x.submitted_by || x.created_by}</td><td>{when(x.withdrawn_at || x.submitted_at || x.created_at)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </aside>
          )}
          <ReportDocument s={s} version={v} agentMode={mode === 'agent' && !viewing} />
        </div>
      )}

      {showControls && inputs.length > 0 && (
        <details className="card">
          <summary><b>Estimates and benchmarks behind the pack</b> <span className="muted small">· not sent to carriers; editable, every change logged</span></summary>
          <div className="grid mt">{inputs.map((f) => <FieldCard key={f.key} f={f} actor={actor} onChange={onChange} />)}</div>
        </details>
      )}
    </div>
  )
}
