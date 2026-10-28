import { useEffect, useState } from 'react'
import { api, money, when } from '../api.js'
import OwnerDecision from './OwnerDecision.jsx'

const fmt = (v) => (typeof v === 'number' ? money(v) : v == null ? '—' : String(v))
const day = (s) => (s ? new Date(s + 'T12:00:00').toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }) : '—')
const COND = { met: ['Met per application', 'ok'], to_confirm: ['Application answer to confirm', 'mid'],
  unknown: ['Not asked yet', 'mid'], gap: ['Not in place per application', 'no'] }

function Step({ n, title, done, children, sub }) {
  return (
    <section className={`card step ${done ? 'step-done' : ''}`}>
      <div className="step-head"><span className="step-n">{done ? '✓' : n}</span><div><h3>{title}</h3>{sub && <p className="small muted">{sub}</p>}</div></div>
      {children}
    </section>
  )
}

function QuoteStep({ d, actor, run, busy }) {
  const q = d.quote
  const [note, setNote] = useState('')
  if (!q) {
    return (
      <Step n={2} title="Firm quote in" sub="After the signed application goes to the carrier, its firm quote comes back. It's taken in like an indication: kept as received, every figure checked against the document, compared with the indication.">
        {!d.present || d.present.decision !== 'chose'
          ? <p className="small muted">Waiting on step 1: record which option the owner chose.</p>
          : d.inbox.length === 0
            ? <p className="small muted">Waiting on {d.present.carrier}'s firm quote for {d.present.option_label}.</p>
            : <ul className="received">{d.inbox.map((p) => (
                <li key={p}><span className="mono">{p.split('/').pop()}</span>
                  <button className="btn sm" disabled={!!busy} onClick={() => run(() => api.ingestQuote(p, actor), `quote:${p}`)}>
                    {busy === `quote:${p}` ? <><span className="spin" /> Reading the quote…</> : 'Take in'}</button></li>))}</ul>}
        {busy?.startsWith('quote:') && <p className="small muted">Reading every figure and checking it against the document. This can take a few seconds.</p>}
      </Step>
    )
  }
  const ind = q.indication
  return (
    <Step n={2} title="Firm quote in" done={['verified', 'confirmed'].includes(q.review)}>
      <div className="row small">
        <b>{q.carrier}</b><span>{q.option_label}</span><span className="muted">quote {q.reference} · {day(q.doc_date)} · valid to {day(q.expires_on)}</span>
        {q.review === 'verified' && <span className="chip ok">Every figure found in the PDF</span>}
        {q.review === 'confirmed' && <span className="chip ok">Confirmed by {q.reviewed_by_name}</span>}
        {q.review === 'pending_review' && <span className="chip mid">Needs a person</span>}
        {q.review === 'rejected' && <span className="chip no">Rejected</span>}
        <a className="link" href={api.wikiUrl(q.path)} target="_blank" rel="noreferrer">Open the PDF</a>
      </div>
      <div className="qcmp mt">
        <div className="qcmp-col"><div className="muted small">Indication{ind && ` · ${ind.carrier} v${ind.version_no}, ${day(ind.doc_date)}`}</div>
          <div className="qcmp-fig">{ind ? money(ind.premium) : '—'}</div></div>
        <div className="qcmp-arrow" aria-hidden>→</div>
        <div className="qcmp-col"><div className="muted small">Firm quote</div>
          <div className="qcmp-fig strong">{money(q.premium)}</div></div>
        {ind && q.premium && <div className={`qcmp-delta ${q.premium > ind.premium ? 'up' : 'down'}`}>
          {q.premium > ind.premium ? '+' : ''}{money(q.premium - ind.premium)} ({((q.premium - ind.premium) / ind.premium * 100).toFixed(0)}%)</div>}
      </div>
      {q.premium_reason && <blockquote className="quote">Carrier's reason: “{q.premium_reason}”</blockquote>}
      <dl className="qterms small">
        <div><dt>Limit / retention</dt><dd>{money(q.limit_amount)} / {money(q.deductible)}</dd></div>
        <div><dt>Social engineering</dt><dd>{fmt(q.sublimits.social_engineering)}</dd></div>
        <div><dt>Ransomware</dt><dd>{fmt(q.sublimits.ransomware)}</dd></div>
        <div><dt>BI waiting period</dt><dd>{q.bi_waiting_hours} hours</dd></div>
        <div><dt>Policy period</dt><dd>{day(q.effective_date)} to {day(q.expiration_date)}</dd></div>
        <div><dt>Other changes vs indication</dt><dd>{q.changes.filter((c) => c.field !== 'premium').length === 0 ? 'None' :
          q.changes.filter((c) => c.field !== 'premium').map((c) => `${c.label}: ${fmt(c.old)} → ${fmt(c.new)}`).join('; ')}</dd></div>
      </dl>
      {q.review === 'pending_review' && (
        <div className="row mt">
          <span className="small warn-text">{q.failed_checks.join('; ')}</span>
          <input placeholder="Note (required to reject)" value={note} onChange={(e) => setNote(e.target.value)} />
          <button className="btn" onClick={() => run(() => api.reviewQuote('confirmed', note || null, actor))}>Matches the PDF · confirm</button>
          <button className="btn ghost" disabled={!note} onClick={() => run(() => api.reviewQuote('rejected', note, actor))}>Reject</button>
        </div>
      )}
    </Step>
  )
}

function FinalStep({ d, actor, run }) {
  const [reason, setReason] = useState('')
  const [note, setNote] = useState('')
  const [declining, setDeclining] = useState(false)
  const q = d.quote
  const f = d.final
  const ready = q && ['verified', 'confirmed'].includes(q.review)
  return (
    <Step n={3} title="Present final terms" done={f?.decision === 'accepted'}
          sub="What changed since the proposal pack, and what the owner must do to bind. The owner accepts, or declines with a reason.">
      {!ready ? <p className="small muted">Waiting on a checked firm quote.</p> : (
        <>
          <ul className="small final-points">
            {q.indication && q.premium !== q.indication.premium &&
              <li>Price moved from {money(q.indication.premium)} to <b>{money(q.premium)}</b> a year. The carrier's reason is quoted above.</li>}
            {d.conditions.filter((c) => c.timing === 'before').map((c) => <li key={c.id}>Before coverage starts: {c.text.replace(/^before binding:\s*/i, '')}</li>)}
            {d.conditions.filter((c) => c.timing === 'after').map((c) => <li key={c.id}>Within {c.due_days} days after: {c.text.replace(/^within \d+ days of binding:\s*/i, '')}{c.is_new && <span className="chip mid">new since the indication</span>}</li>)}
          </ul>
          {f && <p className="small"><b>{f.decision === 'accepted' ? 'Accepted' : `Declined: ${f.reason_label}`}</b>{f.note && ` “${f.note}”`}
            <span className="muted"> · {f.actor_name}, {when(f.created_at)}</span></p>}
          {!d.binder && (
            <div className="row">
              <button className="btn primary" onClick={() => run(() => api.decide({ stage: 'final', decision: 'accepted', note }, actor))}>Owner accepts</button>
              <button className="btn ghost" onClick={() => setDeclining(!declining)}>Owner declines…</button>
              {declining && <>
                <select value={reason} onChange={(e) => setReason(e.target.value)}>
                  <option value="">Reason…</option>
                  {Object.entries(d.reasons).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
                </select>
                <input placeholder="In their words" value={note} onChange={(e) => setNote(e.target.value)} />
                <button className="btn" disabled={!reason} onClick={() => run(() => api.decide({ stage: 'final', decision: 'declined', reason, note }, actor))}>Record decline</button>
              </>}
            </div>
          )}
        </>
      )}
    </Step>
  )
}

function Condition({ c, actor, run, locked }) {
  const [ev, setEv] = useState(c.evidence || '')
  const met = c.status === 'met'
  const [lbl, tone] = COND[c.intake_status] || ['—', 'mid']
  return (
    <li className={`bcond ${c.status}`}>
      <div className="row">
        <span className="grow">{c.text}</span>
        <div className="seg small-seg" role="group" aria-label="Condition met?">
          <button className={met ? 'on' : ''} disabled={locked} onClick={() => !met && run(() => api.setCondition(c.id, true, ev || null, actor))}>Met</button>
          <button className={!met ? 'on' : ''} disabled={locked} onClick={() => met && run(() => api.setCondition(c.id, false, null, actor))}>Not yet</button>
        </div>
      </div>
      <div className="small muted">{c.timing === 'before' ? 'Before binding' : `Within ${c.due_days} days after binding`} · the application said: <span className={`chip ${tone}`}>{lbl}</span>
        {met && <> · marked met by {c.met_by_name}, {when(c.met_at)}</>}</div>
      {met
        ? (c.evidence && <div className="small">Proof: {c.evidence}</div>)
        : <input className="grow" placeholder="Proof (optional), e.g. IT provider's MFA report, emailed 12/8" value={ev} onChange={(e) => setEv(e.target.value)} />}
    </li>
  )
}

function BindStep({ d, actor, run }) {
  const b = d.binder
  return (
    <Step n={4} title="Bind" done={!!b} sub="Binding is when coverage starts. The carrier binds once its conditions are met and the owner has said yes; simulated here.">
      {!d.quote ? <p className="small muted">Waiting on the firm quote.</p> : (
        <>
          <ul className="bconds">{d.conditions.map((c) => <Condition key={c.id} c={c} actor={actor} run={run} locked={!!b && c.timing === 'before'} />)}</ul>
          {b ? (
            <div className="bound mt">
              <div><span className="muted small">Policy number</span><b>{b.policy_number}</b></div>
              <div><span className="muted small">In force</span><b>{day(b.effective_date)} to {day(b.expiration_date)}</b></div>
              <div><span className="muted small">Annual premium</span><b>{money(b.premium)}</b></div>
              <div><span className="muted small">Bound by</span><b>{b.bound_by_name}</b></div>
              {b.simulated && <p className="small muted">Simulated: in production the carrier issues the binder and policy number.</p>}
            </div>
          ) : (
            <div className="row mt">
              <button className="btn primary" disabled={d.blockers.length > 0} onClick={() => run(() => api.bind(actor))}>Bind coverage</button>
              {d.blockers.length > 0 && <span className="small muted">Not yet: {d.blockers.join('; ')}.</span>}
            </div>
          )}
        </>
      )}
    </Step>
  )
}

function ClientSummary({ s }) {
  if (!s) return <p className="muted small">Appears once the firm quote is in.</p>
  return (
    <div className="doc-sum">
      <div className="doc-kicker">{s.bound ? 'Your cyber policy' : 'Draft: becomes final when bound'}</div>
      <h3>{s.client}: what you have</h3>
      <dl className="qterms small">
        <div><dt>Carrier</dt><dd>{s.carrier}</dd></div>
        <div><dt>Policy number</dt><dd>{s.policy_number || 'Issued at binding'}{s.simulated && ' (simulated)'}</dd></div>
        <div><dt>Coverage dates</dt><dd>{day(s.effective_date)} to {day(s.expiration_date)}</dd></div>
        <div><dt>Annual premium</dt><dd>{money(s.premium)}</dd></div>
        <div><dt>Total limit</dt><dd>{money(s.limit)} a year, with {money(s.deductible)} paid by the practice per claim</dd></div>
        <div><dt>Ransomware</dt><dd>{fmt(s.sublimits.ransomware)}</dd></div>
        <div><dt>Fraudulent payment requests</dt><dd>up to {fmt(s.sublimits.social_engineering)}</dd></div>
        <div><dt>Lost income starts after</dt><dd>{s.bi_waiting_hours} hours of downtime</dd></div>
      </dl>
      <h4 className="mt">If something happens</h4>
      <ol className="small">{s.incident_steps.map((x) => <li key={x}>{x}</li>)}</ol>
      <h4 className="mt">What you agreed to keep in place</h4>
      <ul className="small">
        {s.conditions.map((c) => <li key={c.text}>{c.text}</li>)}
        {s.controls.map((c) => { const x = c.replace(/^Is |^Are /, '').replace(/\?$/, ''); return <li key={c}>{x[0].toUpperCase() + x.slice(1)}: yes, per your application</li> })}
      </ul>
      <p className="small muted">{s.coverage_note}</p>
    </div>
  )
}

function DealRecord({ r }) {
  return (
    <div className="stack-s">
      <p className="small"><span className={`chip ${r.outcome.status === 'bound' ? 'ok' : r.outcome.status === 'lost' ? 'no' : 'mid'}`}>{r.outcome.status}</span> {r.outcome.text}</p>
      {r.price.quote && <p className="small">Price: indication {money(r.price.indication)} ({r.price.indication_ref}) → firm quote <b>{money(r.price.quote)}</b>.
        {r.price.reason && <span className="muted"> {r.price.reason}</span>}</p>}
      <table className="vtable">
        <thead><tr><th>Milestone</th><th>When</th></tr></thead>
        <tbody>{r.milestones.map((m) => <tr key={m.label} className={m.at ? '' : 'muted'}><td>{m.label}</td><td>{m.at ? when(m.at) : 'not yet'}</td></tr>)}</tbody>
      </table>
      <p className="small muted">Times are when each step happened in this demo; in production this is the cycle time from first request to bind.</p>
      <h4 className="mt">Who did what</h4>
      <p className="small">{r.people.map((p) => `${p.actor} (${p.role.replace('_', ' ')}): ${p.n} actions`).join(' · ')}</p>
      {r.decisions.length > 0 && <>
        <h4 className="mt">The owner's decisions</h4>
        <ul className="small">{r.decisions.map((d) => <li key={d.id}>{d.stage === 'present' ? 'On the proposal' : 'On the firm quote'}: {d.decision.replace('_', ' ')}
          {d.carrier && ` · ${d.carrier} ${d.option_label}`}{d.reason_label && ` · reason: ${d.reason_label}`}{d.note && ` · “${d.note}”`}</li>)}</ul>
      </>}
      <h4 className="mt">Sources behind the numbers</h4>
      <ul className="small">{r.sources.map((s) => <li key={s}><a className="link" href={api.wikiUrl(s)} target="_blank" rel="noreferrer">{s}</a></li>)}</ul>
    </div>
  )
}

const OWNER_TONE = { Agent: 'k-call', UKON: 'k-ai', Carrier: 'k-public', Client: '' }

function AfterBind({ p }) {
  if (!p.items.length) return <p className="muted small">Appears once the firm quote is in (the dates come from its policy period).</p>
  return (
    <div className="stack-s">
      <p className="small">{p.draft && <b>Draft until bound. </b>}Policy year {day(p.start)} to {day(p.renewal)}. Built by rules from the binder, the carrier's
        conditions, the application's weak spots and the exposure findings. {p.owner_note}</p>
      <div className="ninety">
        {p.buckets.slice(0, 3).map((b) => (
          <div key={b.label} className="ninety-col">
            <h4>{b.label}</h4>
            {b.items.length === 0 && <p className="small muted">Nothing scheduled.</p>}
            {b.items.map((i, k) => (
              <div key={k} className={`tp tp-${i.kind}`}>
                <div className="row small"><b>Day {i.day}</b><span className="muted">{day(i.date)}</span><span className={`pill ${OWNER_TONE[i.owner]}`}>{i.owner}</span></div>
                <div className="small">{i.what}</div>
                <div className="small muted">{i.why}</div>
              </div>
            ))}
          </div>
        ))}
      </div>
      <h4 className="mt">Through the year to renewal</h4>
      <ol className="year">
        {p.buckets.slice(3).flatMap((b) => b.items).map((i, k) => (
          <li key={k} className={`tp-${i.kind}`}>
            <span className="small"><b>{day(i.date)}</b> <span className="muted">day {i.day}</span></span>
            <span className="small"><span className={`pill ${OWNER_TONE[i.owner]}`}>{i.owner}</span> {i.what} <span className="muted">· {i.why}</span></span>
          </li>
        ))}
      </ol>
    </div>
  )
}

function Reports({ d }) {
  const [view, setView] = useState('client')
  return (
    <Step n={5} title="Report" done={!!d.binder} sub="One for the client, one for the agency and UKON, and the plan after bind.">
      <div className="seg small-seg">
        {[['client', 'Client summary'], ['deal', 'Deal record (agency + UKON)'], ['plan', 'After bind: 30-60-90 + the year']].map(([k, l]) => (
          <button key={k} className={view === k ? 'on' : ''} onClick={() => setView(k)}>{l}</button>))}
        <button onClick={() => window.print()}>Print</button>
      </div>
      <div className="mt">
        {view === 'client' && <ClientSummary s={d.summary} />}
        {view === 'deal' && <DealRecord r={d.deal} />}
        {view === 'plan' && <AfterBind p={d.plan} />}
      </div>
    </Step>
  )
}

export default function Close({ actor, onChange, tick }) {
  const [d, setD] = useState(null)
  const [err, setErr] = useState(null)
  const [local, setLocal] = useState(0)
  useEffect(() => { api.close().then(setD).catch((e) => setErr(e.message)) }, [tick, local])
  const [busy, setBusy] = useState(null)
  const [actErr, setActErr] = useState(null)
  // One Stage 6 action at a time: a second click while the first is running is ignored, and errors show on the page.
  const run = async (fn, key = 'action') => {
    if (busy) return
    setBusy(key); setActErr(null)
    try { await fn(); setLocal((x) => x + 1); onChange() } catch (e) { setActErr(e.message) } finally { setBusy(null) }
  }
  if (err) return <div className="card">Couldn't load Stage 6: {err}</div>
  if (!d) return <div className="card empty">Loading…</div>
  const lost = d.present?.decision === 'not_now'
  return (
    <div className="stack">
      <section className="intro">
        <h2>Stage 6 · Decision, bind, report</h2>
        <p>The agent presents the proposal pack and records the owner's choice, or "not now" with the reason. The signed
          application goes to the carrier for that option and a firm quote comes back. It can differ from the indication, so it's
          compared line by line and presented again. The owner accepts, the carrier's before-binding conditions are met with
          evidence, and the policy is bound. Then the reports: a plain summary for the client, a deal record for the agency
          and UKON, and the plan for the year after bind.</p>
      </section>
      <OwnerDecision actor={actor} onChange={() => { setLocal((x) => x + 1); onChange() }} tick={tick + local} locked={!!d.quote} />
      {!lost && <>
        {actErr && <div className="card err small" role="alert">{actErr} <button className="btn ghost sm" onClick={() => setActErr(null)}>Dismiss</button></div>}
        <QuoteStep d={d} actor={actor} run={run} busy={busy} />
        <FinalStep d={d} actor={actor} run={run} />
        <BindStep d={d} actor={actor} run={run} />
      </>}
      <Reports d={d} />
    </div>
  )
}
