import { useCallback, useEffect, useState } from 'react'
import { api } from './api.js'
import Enrichment from './components/Enrichment.jsx'
import Indications from './components/Indications.jsx'
import ReportTab from './components/ReportTab.jsx'
import Brief from './components/Brief.jsx'
import Intake from './components/Intake.jsx'
import Close from './components/Close.jsx'
import Audit from './components/Audit.jsx'
import AskPanel from './components/AskPanel.jsx'

// The six stages come from the API (pipeline/stages.py), each with a status derived from the data.
// UKON's brief has four; its Stage 1 is split (confirm data, get indications) and so is its Stage 4 (present and apply; final terms, bind, report).

export default function App() {
  const [tab, setTab] = useState('confirm')
  const [users, setUsers] = useState([])
  const [actor, setActor] = useState('Jordan Pike')
  const [data, setData] = useState(null)
  const [tick, setTick] = useState(0)
  const [askOpen, setAskOpen] = useState(false)
  const [err, setErr] = useState(null)

  const refresh = useCallback(() => setTick((t) => t + 1), [])
  useEffect(() => { api.users().then(setUsers).catch((e) => setErr(e.message)) }, [])
  useEffect(() => { api.client().then(setData).catch((e) => setErr(e.message)) }, [tick])

  if (err) return <div className="boot">Can't reach the API ({err}). Start it with <code>uv run uvicorn api.main:app --port 8000</code>.</div>
  if (!data) return <div className="boot">Loading…</div>

  const c = data.client
  const { stages, current } = data.progress
  const cur = stages.find((s) => s.key === current)

  return (
    <div className="shell">
      <header className="top">
        <div className="brand">
          <span className="mark" aria-hidden>◆</span>
          <div>
            <div className="brand-name">Renewal Workbench</div>
            <div className="brand-sub">Cyber in the renewal window · prototype</div>
          </div>
        </div>
        <div className="client-head">
          <div className="client-name">{c.display_name}</div>
          <div className="client-meta">
            {c.agency} · renews {c.renewal_date} · <strong>{c.days_to_renewal} days</strong> out · next: <strong>Stage {cur.n} · {cur.label}</strong>
          </div>
        </div>
        <label className="actor">
          <span>Acting as</span>
          <select value={actor} onChange={(e) => setActor(e.target.value)}>
            {users.map((u) => <option key={u.name} value={u.name}>{u.name} · {u.role.replace('_', ' ')}</option>)}
          </select>
        </label>
      </header>

      <nav className="tabs stages" role="tablist">
        {stages.map((s) => (
          <button key={s.key} role="tab" aria-selected={tab === s.key} className={`tab stage-${s.status} ${tab === s.key ? 'on' : ''}`}
                  onClick={() => setTab(s.key)} title={`UKON stage ${s.ukon}`}>
            <span className="tab-n">{s.status === 'done' ? '✓' : s.n}</span>
            <span className="tab-label">{s.label}</span>
            <span className="tab-sub">{s.note}</span>
            {s.status === 'attention' && <span className="pill warn">to do</span>}
          </button>
        ))}
        <button className={tab === 'audit' ? 'tab on' : 'tab'} onClick={() => setTab('audit')}>
          <span className="tab-label">Audit trail</span><span className="tab-sub">Who changed what</span>
        </button>
        <button className="ask-btn" onClick={() => setAskOpen(true)}>Ask about this client</button>
      </nav>
      <div className="stage-map small muted">
        UKON's brief has four stages. This splits its Stage 1 into <b>1 · Confirm data</b> and <b>2 · Get indications</b>, and its
        Stage 4 into <b>5 · Questionnaire</b> and <b>6 · Decision, bind, report</b>. Stages 3 and 4 here are UKON's 2 and 3.
      </div>

      <main className="main">
        {tab === 'confirm' && <Enrichment data={data} actor={actor} onChange={refresh} goNext={() => setTab('indications')} />}
        {tab === 'indications' && <Indications data={data} actor={actor} onChange={refresh} tick={tick} goStage1={() => setTab('confirm')} />}
        {tab === 'proposal' && <ReportTab data={data} actor={actor} onChange={refresh} tick={tick} />}
        {tab === 'agent_kit' && <Brief tick={tick} actor={actor} />}
        {tab === 'apply_bind' && <Intake actor={actor} onChange={refresh} tick={tick} />}
        {tab === 'close' && <Close actor={actor} onChange={refresh} tick={tick} />}
        {tab === 'audit' && <Audit tick={tick} />}
      </main>

      {askOpen && <AskPanel actor={actor} onClose={() => setAskOpen(false)} />}
    </div>
  )
}
