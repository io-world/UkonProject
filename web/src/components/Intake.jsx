import { useEffect, useState } from 'react'
import { api } from '../api.js'
import LiveCall from './intake/LiveCall.jsx'
import IntakeReview from './intake/IntakeReview.jsx'
import Application from './Application.jsx'

const VIEWS = [
  { id: 'live', label: 'Live call', sub: 'Tap answers while you talk' },
  { id: 'review', label: 'After the call', sub: 'Recording vs taps · confirm' },
  { id: 'app', label: 'Application', sub: 'Carrier questions · e-sign' },
]

export default function Intake({ actor, onChange, tick }) {
  const [view, setView] = useState('live')
  const [data, setData] = useState(null)
  const [local, setLocal] = useState(0)
  useEffect(() => { api.intake().then(setData) }, [tick, local])
  const refresh = () => { setLocal((x) => x + 1); onChange() }

  if (!data) return <div className="muted">Loading intake…</div>
  return (
    <div className="stack">
      <section className="intro">
        <h2>Stage 5 · Questionnaire</h2>
        <p>The application questions, answered over as many calls and emails as it takes. On a call the agent walks the owner through the questions, tapping answers live; Wispr Flow records it. Each recording is
          ingested into the wiki and checked against the taps: the AI quotes the line each answer came from, hedges stay flagged, and
          a recording that disagrees with a tap is a conflict, not an overwrite. It can take several calls. Confirmed answers flow back: a corrected revenue updates Stage 1 and, if it moved enough, flags the indications for re-request.</p>
        <div className="seg" role="tablist" aria-label="Intake view">
          {VIEWS.map((v) => (
            <button key={v.id} className={view === v.id ? 'on' : ''} onClick={() => setView(v.id)} title={v.sub}>{v.label}</button>
          ))}
        </div>
      </section>
      {view === 'live' && <LiveCall data={data} actor={actor} onSaved={() => setLocal((x) => x + 1)} />}
      {view === 'review' && <IntakeReview data={data} actor={actor} onChange={refresh} />}
      {view === 'app' && <Application actor={actor} onChange={refresh} tick={tick + local} embedded />}
    </div>
  )
}
