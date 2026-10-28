import { money, short } from '../api.js'

const TIER_NAME = { recommended: 'Recommended', premier: 'Premier' }
const MISSING = (st) => (st || 'awaiting').startsWith('declined') ? 'Not offered by this insurer for a practice this size.' : "Waiting on the insurer's written price."
const PLAIN_CONTROL = { mfa_email: 'phone codes on email logins', tested_backups: 'tested backups', edr: 'attack-monitoring software', payment_verify: 'payment-change call-backs' }

function Meter({ score, band }) {
  return (
    <div className="meter" role="img" aria-label={`Exposure ${score} of 100, ${band}`}>
      <div className="meter-track">
        <div className="meter-zone lo" /><div className="meter-zone mid" /><div className="meter-zone hi" />
        <div className="meter-pin" style={{ left: `${score}%` }} />
      </div>
      <div className="meter-labels"><span>Lower</span><span>Moderate</span><span>Elevated</span></div>
    </div>
  )
}

export default function ReportDocument({ s, version, agentMode }) {
  const n = s.narrative
  const opts = s.options || {}
  const carrier = s.carriers.find((c) => c.carrier === s.selected_carrier) || {}
  const stale = s.revenue_drift?.needs_refresh

  return (
    <article className="doc">
      {agentMode && <div className="doc-ribbon">Preview of what the client will see</div>}
      <header className="doc-head">
        <div className="doc-kicker">Cyber protection options for</div>
        <h1>{s.client.name}</h1>
        <p className="lede">{n.why_it_matters}</p>
      </header>

      <section>
        <h2>Your options at a glance</h2>
        {stale && agentMode && <div className="banner warn">Prices below are from the original indication and need a refresh before sending.</div>}
        {!s.selected_carrier && agentMode && <div className="banner warn">No carrier replies yet: prices appear here once Stage 2's replies are in.</div>}
        <div className="tiers">
          {['recommended', 'premier'].map((t) => {
            const o = opts[t]
            if (!o) return (
              <div key={t} className="tier off"><div className="tier-name">{TIER_NAME[t]}</div>
                <p className="muted small">{MISSING(carrier.option_state?.[t])}</p></div>
            )
            return (
              <div key={t} className={`tier ${t === s.recommended_tier ? 'rec' : ''}`}>
                {t === s.recommended_tier && <div className="tier-flag">Most dental offices choose this</div>}
                <div className="tier-name">{TIER_NAME[t]}</div>
                <div className="tier-price">{money(o.monthly)}<span>/month est.</span></div>
                <div className="tier-annual">{money(o.premium)} per year</div>
                <dl>
                  <dt>Protection up to</dt><dd>{short(o.limit)}</dd>
                  <dt>You pay first</dt><dd>{money(o.deductible)}</dd>
                  <dt>Tricked into sending money</dt><dd className="flagged">up to {short(o.sublimits.social_engineering)}</dd>
                </dl>
              </div>
            )
          })}
        </div>
        <p className="disclaimer">{s.coverage.disclaimer}{s.selected_carrier && <> Estimates from {s.selected_carrier}; valid until {carrier.expires_on}.</>}</p>
      </section>

      {s.intake?.topics && (
        <section>
          <h2>What you've told us so far</h2>
          <p className="small muted">From {s.intake.calls.length} conversation{s.intake.calls.length !== 1 ? 's' : ''} with your agent.
            Items marked "to confirm" don't hold anything up.</p>
          <ul className="intake-list">
            {s.intake.topics.map((t) => (
              <li key={t.key}><span>{t.label}</span>
                <span className={`st st-${t.code}`}>{t.status}</span>
                {agentMode && t.source_call && <span className="muted small"> · {t.source_call}</span>}</li>
            ))}
          </ul>
        </section>
      )}

      <section>
        <h2>What could happen to a practice like yours</h2>
        {s.opex && (
          <div className="opex">
            <div className="opex-fig">
              <span className="opex-tag">Operating costs (OPEX)</span>
              <b>{money(s.opex.daily_low)}–{money(s.opex.daily_high)}</b>
              <span>a day to keep the practice running, open or closed</span>
            </div>
            <p>Staff, rent, supplies and loans keep costing money while systems are down. That's about {short(s.opex.annual_low)}–{short(s.opex.annual_high)} a
              year, based on typical dental overhead of {Math.round(s.opex.ratio_low * 100)}–{Math.round(s.opex.ratio_high * 100)}% of revenue.</p>
            <details className="info">
              <summary>What's OPEX, and how is this calculated?</summary>
              <p><b>OPEX</b> (operating expenses) is what it costs to keep the doors open: staff pay, rent, supplies, lab fees,
                software and equipment leases, loan payments. Unlike revenue, it doesn't stop when systems go down.</p>
              <p className="formula">{money(s.opex.revenue)} annual revenue × {Math.round(s.opex.ratio_low * 100)}% to {Math.round(s.opex.ratio_high * 100)}% typical
                dental overhead = {money(s.opex.annual_low)} to {money(s.opex.annual_high)} a year<br />
                ÷ 365 days = {money(s.opex.daily_low)} to {money(s.opex.daily_high)} a day (rounded)</p>
              <p className="muted small">Every calendar day, because rent, salaries and loans keep running on days the office is closed.
                The revenue is the figure your agent has on file; the overhead share is an industry average, not your books, so your
                accountant can give the real number. This is a cost to you, not a statement of what any policy pays.</p>
            </details>
            <p className="muted small">Source: <a href={s.opex.source_url} target="_blank" rel="noreferrer">{s.opex.source}</a>.{agentMode && <> · revenue from the database · wiki: <code>raw/benchmarks/dental_overhead_benchmarks.md</code></>}</p>
          </div>
        )}
        <div className="scenarios">
          {n.scenarios.map((sc) => {
            const cost = s.scenario_costs[sc.key]
            return (
              <div key={sc.key} className="scenario">
                <h4>{sc.title}</h4>
                <p>{sc.story}</p>
                {cost && (
                  <div className="cost">
                    <b>{cost.high ? `${short(cost.low)}–${short(cost.high)}` : short(cost.low)}</b>
                    <span>{cost.label}</span>
                    {cost.how && (
                      <details className="info">
                        <summary>How is this figure worked out?</summary>
                        <p>{cost.how}</p>
                        <p className="muted small">Source: <a href={cost.source_url} target="_blank" rel="noreferrer">{cost.source}</a></p>
                      </details>
                    )}
                  </div>
                )}
              </div>
            )
          })}
        </div>
      </section>

      <section className="exposure">
        <h2>Your exposure snapshot</h2>
        <Meter score={s.exposure.score} band={s.exposure.band} />
        <p>{n.exposure_explainer}</p>
        <ul className="factors">
          {s.exposure.factors.map((f) => <li key={f.label}>{f.label}</li>)}
        </ul>
        {s.exposure.unknown_controls?.length > 0 && (
          <p className="muted small">We don't know yet whether you have {s.exposure.unknown_controls.map((k) => PLAIN_CONTROL[k]).join(', ')}. Each one lowers this score.</p>
        )}
        {agentMode && s.exposure.score !== s.exposure.ai_score && (
          <p className="agent-note">AI score {s.exposure.ai_score} · set to {s.exposure.score} by agent</p>
        )}
      </section>

      {s.research?.length > 0 && (
        <section>
          <h2>Practices like yours, in the news</h2>
          <div className="news">
            {s.research.map((r) => (
              <div key={r.id} className="scenario">
                <h4><a href={r.url} target="_blank" rel="noreferrer">{r.headline}</a></h4>
                <p>{r.summary}</p>
                <p className="yours">{r.for_this_client}</p>
                <div className="muted small">Source: <a href={r.url} target="_blank" rel="noreferrer">{r.source}</a>, {r.date}
                  {agentMode && <> · wiki: <code>{r.wiki}</code></>}</div>
              </div>
            ))}
          </div>
        </section>
      )}

      <section>
        <h2>What it pays for</h2>
        <div className="coverage">
          {s.coverage.covered.map((c) => (
            <div key={c.key} className={`cov ${c.flag_sublimit ? 'flag' : ''}`}>
              <h4>{c.title}</h4><p>{c.plain}</p>
            </div>
          ))}
        </div>
        <h4 className="mt">Not covered</h4>
        <ul className="notcov">{s.coverage.not_covered.map((x) => <li key={x}>{x}</li>)}</ul>
        <p className="small muted">Systems down: income replacement starts after {carrier.bi_waiting_hours} hours.</p>
      </section>

      <section>
        <h2>Common questions</h2>
        <div className="faq">
          <div><h4>"We're too small to be a target."</h4><p>{n.objection_tailoring.too_small}</p></div>
          <div><h4>"Our IT company handles security."</h4><p>{n.objection_tailoring.it_handles_it}</p></div>
        </div>
      </section>

      <section className="next">
        <h2>What happens next</h2>
        <p>{n.next_steps}</p>
        {carrier.conditions?.length > 0 && (
          <p className="small">The insurer will ask about: {carrier.conditions.join('; ')}.</p>
        )}
      </section>

      <footer className="doc-foot">
        {version ? `Version ${version.version_no}` : ''} · Prepared by your agent with UKON · Not a quote or a binder.
        {agentMode && <> · Narrative: {n._provenance === 'live' ? 'generated live' : 'cached AI output'}; every figure from the database.</>}
      </footer>
    </article>
  )
}
