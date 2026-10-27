import { useCallback, useEffect, useState } from 'react'
import { api } from './api.js'
import Enrichment from './components/Enrichment.jsx'
import ReportTab from './components/ReportTab.jsx'
import Brief from './components/Brief.jsx'
import Intake from './components/Intake.jsx'
import Audit from './components/Audit.jsx'
import AskPanel from './components/AskPanel.jsx'

const TABS = [
  { id: 'enrich', n: 1, label: 'Get indications', sub: 'Five fields carriers need' },
  { id: 'app', n: 2, label: 'Intake', sub: 'Live call · recording · confirm' },
  { id: 'report', n: 3, label: 'Client pack', sub: 'HTML report for the owner' },
  { id: 'brief', n: 4, label: 'Agent brief', sub: 'Pitch, objections, news' },
  { id: 'audit', n: null, label: 'Audit trail', sub: 'Who changed what' },
]

export default function App() {
  const [tab, setTab] = useState('enrich')
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
  const review = data.fields.filter((f) => f.needs_review).length + (data.entities.some((e) => e.status === 'confirmed') ? 0 : 1)

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
            {c.agency} · renews {c.renewal_date} · <strong>{c.days_to_renewal} days</strong> out · stage <code>{c.stage}</code>
          </div>
        </div>
        <label className="actor">
          <span>Acting as</span>
          <select value={actor} onChange={(e) => setActor(e.target.value)}>
            {users.map((u) => <option key={u.name} value={u.name}>{u.name} · {u.role.replace('_', ' ')}</option>)}
          </select>
        </label>
      </header>

      <nav className="tabs" role="tablist">
        {TABS.map((t) => (
          <button key={t.id} role="tab" aria-selected={tab === t.id} className={tab === t.id ? 'tab on' : 'tab'}
                  onClick={() => setTab(t.id)}>
            {t.n && <span className="tab-n">{t.n}</span>}
            <span className="tab-label">{t.label}</span>
            <span className="tab-sub">{t.sub}</span>
            {t.id === 'enrich' && review > 0 && <span className="pill warn">{review} to review</span>}
          </button>
        ))}
        <button className="ask-btn" onClick={() => setAskOpen(true)}>Ask about this client</button>
      </nav>

      <main className="main">
        {tab === 'enrich' && (
          <Enrichment data={data} actor={actor} onChange={refresh} />
        )}
        {tab === 'report' && <ReportTab data={data} actor={actor} onChange={refresh} tick={tick} />}
        {tab === 'brief' && <Brief tick={tick} />}
        {tab === 'app' && <Intake actor={actor} onChange={refresh} tick={tick} />}
        {tab === 'audit' && <Audit tick={tick} />}
      </main>

      {askOpen && <AskPanel actor={actor} onClose={() => setAskOpen(false)} />}
    </div>
  )
}
