import { Fragment, useEffect, useMemo, useRef, useState } from 'react'
import { api } from '../../api.js'
import { FilterBar, Fold, StatusPill, answerText, isAnswered, money, show, useFolds } from './shared.jsx'

const fmt = (ms) => {
  const s = Math.floor(ms / 1000)
  return String(Math.floor(s / 60)).padStart(2, '0') + ':' + String(s % 60).padStart(2, '0')
}

function useTimer() {
  const [start, setStart] = useState(null)
  const [elapsed, setElapsed] = useState(0)
  const [, tick] = useState(0)
  useEffect(() => {
    if (!start) return
    const t = setInterval(() => tick((x) => x + 1), 1000)
    return () => clearInterval(t)
  }, [start])
  const now = elapsed + (start ? Date.now() - start : 0)
  const toggle = () => {
    if (start) { setElapsed(now); setStart(null) } else setStart(Date.now())
  }
  return { now, running: !!start, toggle, label: start ? 'Pause' : elapsed ? 'Resume' : 'Start call' }
}

/** Fill [[a:q7]] with the client's answer and [[r:key|label]] with a report figure (or a labelled placeholder). */
function Say({ text, items, figures }) {
  const parts = text.split(/(\[\[[ar]:[^\]]+\]\])/g)
  return (
    <p className="say">
      {parts.map((p, i) => {
        const a = p.match(/^\[\[a:(\w+)\]\]$/)
        if (a) {
          const it = items[a[1]]
          const v = it && answerText(it)
          return v ? <mark key={i} className="ans-in">{v}</mark>
            : <span key={i} className="ph">[{it?.ref || a[1]} answer]</span>
        }
        const r = p.match(/^\[\[r:(\w+)\|([^\]]+)\]\]$/)
        if (r) {
          return figures[r[1]] ? <mark key={i} className="fig" title="From the report (database)">{figures[r[1]]}</mark>
            : <span key={i} className="ph fig-missing" title="This figure isn't modelled in the prototype yet">{r[2]} · not modelled yet</span>
        }
        return <Fragment key={i}>{p}</Fragment>
      })}
    </p>
  )
}

export default function LiveCall({ data, actor, onSaved }) {
  const items = useMemo(() => Object.fromEntries(data.items.map((i) => [i.key, i])), [data.items])
  const [live, setLive] = useState(() => Object.fromEntries(data.items.map((i) => [i.key, i.row?.live || {}])))
  const [saving, setSaving] = useState({})
  const [cpl, setCpl] = useState('')
  const timer = useTimer()
  const timers = useRef({})

  useEffect(() => {
    setLive((cur) => {
      const next = { ...cur }
      data.items.forEach((i) => { if (!timers.current[i.key]) next[i.key] = i.row?.live || cur[i.key] || {} })
      return next
    })
  }, [data])

  const update = (key, patch, delay = 400) => {
    setLive((cur) => {
      const v = { ...(cur[key] || {}), ...patch }
      clearTimeout(timers.current[key])
      setSaving((s) => ({ ...s, [key]: true }))
      timers.current[key] = setTimeout(async () => {
        await api.intakeLive(key, v, actor)
        delete timers.current[key]
        setSaving((s) => ({ ...s, [key]: false }))
        onSaved?.()
      }, delay)
      return { ...cur, [key]: v }
    })
  }

  const identity = data.items.filter((i) => i.section === 'identity')
  const exposure = data.items.filter((i) => i.section === 'exposure')
  const answeredLive = (i) => {
    const lv = live[i.key] || {}
    if (i.section === 'identity') return lv.confirmed || (lv.corrected && lv.value)
    return i.type === 'multi' ? (lv.multi || []).length > 0 : String(lv.value ?? '').trim() !== ''
  }
  const asked = [...identity, ...exposure]
  const [filter, setFilter] = useState('all')
  const folds = useFolds()
  const isDone = (i) => answeredLive(i) || isAnswered(i.row?.status)
  const keep = (i) => filter === 'all' || (filter === 'answered') === !!isDone(i)
  const fcounts = { all: asked.length, open: asked.filter((i) => !isDone(i)).length, answered: asked.filter(isDone).length }
  const stepDone = (s) => { const ck = s.check_key && items[s.check_key]; return !ck || isAnswered(ck.row?.status) || !!(live[s.check_key]?.text) }
  const keepStep = (s) => filter === 'all' || (filter === 'answered') === stepDone(s)
  const done = asked.filter((i) => answeredLive(i) || ['prefilled', 'confirmed'].includes(i.row?.status)).length
  const flags = asked.filter((i) => live[i.key]?.flag)
  const groups = data.groups.length ? data.groups : [...new Set(exposure.map((i) => i.group))].map((t) => ({ title: t }))

  const copyNotes = async () => {
    const L = [`Sloan's Lake Dental intake — call notes (${fmt(timer.now)})`, '']
    identity.forEach((i) => {
      const lv = live[i.key] || {}
      L.push(`${i.ref} ${i.label}: ${lv.corrected && lv.value ? lv.value + ' (corrected)' : lv.confirmed ? 'confirmed' : '—'}${lv.flag ? ' [UNSURE]' : ''}`)
    })
    exposure.forEach((i) => {
      const lv = live[i.key] || {}
      const v = i.type === 'multi' ? (lv.multi || []).join(', ') : show(lv.value)
      L.push(`${i.ref} ${i.label}: ${v || '—'}${lv.flag ? ' [UNSURE]' : ''}${lv.note ? ' — ' + lv.note : ''}`)
    })
    data.escalations.forEach((e) => L.push(`CPL: ${e.text} (${e.call_time || '—'})`))
    try { await navigator.clipboard.writeText(L.join('\n')) } catch { /* clipboard blocked */ }
  }

  const logCpl = async () => {
    if (!cpl.trim()) return
    await api.intakeEscalate(cpl.trim(), fmt(timer.now), actor)
    setCpl('')
    onSaved?.()
  }

  return (
    <div className="live">
      <div className="live-bar">
        <div className="live-progress">
          <div className="bar"><i style={{ width: `${(done / asked.length) * 100}%` }} /></div>
          <span>{done} of {asked.length} answered</span>
          {flags.length > 0 && <span className="pill warn">{flags.length} unsure</span>}
        </div>
        <button className="btn ghost" onClick={timer.toggle}>{timer.label} <code>{fmt(timer.now)}</code></button>
        <button className="btn ghost" onClick={copyNotes}>Copy call notes</button>
        <span className="muted small">Taps save automatically{Object.values(saving).some(Boolean) ? '…' : ' ✓'}</span>
      </div>

      <div className="live-grid">
        <nav className="live-index">
          <a href="#sec-identity" onClick={() => folds.open('sec-identity')}>Business identity</a>
          {groups.map((g) => <a key={g.title} href={`#g-${g.title}`} onClick={() => folds.open(`g-${g.title}`)}>{g.title}</a>)}
          <a href="#sec-walk" onClick={() => folds.open('sec-walk')}>Walking through the numbers</a>
        </nav>

        <main className="live-main">
          <FilterBar value={filter} onChange={setFilter} counts={fcounts}
                     onAll={(o) => folds.all(['sec-identity', ...groups.map((g) => `g-${g.title}`), 'sec-walk'], o)} />
          {(filter === 'all' || identity.some(keep)) && <Fold id="sec-identity" title="Business identity" sub="Section 0" open={folds.isOpen('sec-identity')}
                onToggle={() => folds.toggle('sec-identity')} open_n={identity.filter((i) => !isDone(i)).length}
                done_n={identity.filter(isDone).length} empty={identity.filter(keep).length ? null : 'Nothing to show with this filter.'}>
            <p className="muted small">Stage 1 already has these. Confirm them, or type the correction (it updates Stage 1, logged).</p>
            {identity.filter(keep).map((it) => {
              const lv = live[it.key] || {}
              const pre = it.prefill || {}
              const shown = it.key === 'revenue' ? money(pre.value) : show(pre.value)
              return (
                <div key={it.key} className={`lq ${lv.flag ? 'flagged' : ''}`} id={`q-${it.key}`}>
                  <div className="lq-ref">{it.ref}</div>
                  <div>
                    <div className="lq-head"><b>{it.label}</b>
                      {pre.confidence && <span className={`conf conf-${pre.confidence}`}>{pre.confidence}</span>}
                      {it.row?.status && it.row.status !== 'unanswered' && <StatusPill row={it.row} />}
                    </div>
                    <p className="ask">“{it.plain}”</p>
                    <div className="lq-prefill">On file: <b>{shown || '—'}</b>{pre.method && <span className="muted small"> · {pre.method}</span>}</div>
                    <div className="row">
                      <button className={`opt ${lv.confirmed ? 'on' : ''}`} onClick={() => update(it.key, { confirmed: !lv.confirmed, corrected: false }, 0)}>✓ Confirmed on call</button>
                      <input className="lq-input" placeholder="Or type the correction" value={lv.corrected ? lv.value || '' : ''}
                             onChange={(e) => update(it.key, { value: e.target.value, corrected: e.target.value !== '', confirmed: false })} />
                      <button className={`opt flag ${lv.flag ? 'on' : ''}`} onClick={() => update(it.key, { flag: !lv.flag }, 0)}>Client unsure</button>
                    </div>
                  </div>
                </div>
              )
            })}
          </Fold>}

            {groups.map((g) => { const gi = exposure.filter((i) => i.group === g.title); if (filter !== 'all' && !gi.some(keep)) return null; return (
              <Fold key={g.title} id={`g-${g.title}`} title={g.title} sub={g.feeds ? `feeds ${g.feeds}` : null}
                    open={folds.isOpen(`g-${g.title}`)} onToggle={() => folds.toggle(`g-${g.title}`)}
                    open_n={gi.filter((i) => !isDone(i)).length} done_n={gi.filter(isDone).length}
                    empty={gi.filter(keep).length ? null : 'Nothing to show with this filter.'}>
                {gi.filter(keep).map((it) => {
                  const lv = live[it.key] || {}
                  const multi = lv.multi || []
                  const setMulti = (o) => {
                    const excl = it.excl || []
                    let next = multi.includes(o) ? multi.filter((x) => x !== o) : [...multi, o]
                    if (!multi.includes(o)) next = excl.includes(o) ? [o] : next.filter((x) => !excl.includes(x))
                    update(it.key, { multi: next }, 0)
                  }
                  const rec = it.row || {}
                  return (
                    <div key={it.key} className={`lq ${lv.flag ? 'flagged' : ''} ${rec.conflict ? 'conflict' : ''}`} id={`q-${it.key}`}>
                      <div className="lq-ref">{it.ref}{it.top && <span className="star" title="Top question">★</span>}</div>
                      <div>
                        <div className="lq-head"><b>{it.label}</b>{rec.status && rec.status !== 'unanswered' && <StatusPill row={rec} />}</div>
                        <p className="ask">“{it.plain}”</p>
                        {it.hint && <div className="hint">{it.hint}</div>}
                        {it.signal && <div className="signal">Enrichment: {it.signal}</div>}
                        {it.type === 'single' && (
                          <div className="opts">{it.options.map((o) => (
                            <button key={o} className={`opt ${lv.value === o ? 'on' : ''}`} onClick={() => update(it.key, { value: lv.value === o ? '' : o }, 0)}>{o}</button>
                          ))}</div>
                        )}
                        {it.type === 'multi' && (
                          <div className="opts">{it.options.map((o) => (
                            <button key={o} className={`opt ${multi.includes(o) ? 'on' : ''}`} onClick={() => setMulti(o)}>{o}</button>
                          ))}</div>
                        )}
                        {(it.type === 'text' || it.type === 'number') && (
                          <input className="lq-input wide" type={it.type === 'number' ? 'number' : 'text'} placeholder={it.ph || ''}
                                 value={lv.value ?? ''} onChange={(e) => update(it.key, { value: e.target.value })} />
                        )}
                        <div className="row">
                          <button className={`opt flag ${lv.flag ? 'on' : ''}`} onClick={() => update(it.key, { flag: !lv.flag }, 0)}>Client unsure</button>
                          <input className="lq-input" placeholder="Note" value={lv.note || ''} onChange={(e) => update(it.key, { note: e.target.value })} />
                        </div>
                        {rec.status && rec.status !== 'unanswered' && (
                          <div className="recorded">Recording ({rec.source_call}): <b>{show(rec.value) || rec.answer}</b>
                            {rec.conflict && <span className="pill warn">differs from your tap</span>}</div>
                        )}
                      </div>
                    </div>
                  )
                })}
              </Fold>
            ) })}

          {(filter === 'all' || data.steps.some(keepStep)) && <Fold id="sec-walk" title="Walking through the numbers" sub="Section 2" open={folds.isOpen('sec-walk')}
                onToggle={() => folds.toggle('sec-walk')} open_n={data.steps.filter((x) => !stepDone(x)).length}
                done_n={data.steps.filter((x) => x.check_key && stepDone(x)).length}
                empty={data.steps.filter(keepStep).length ? null : 'Nothing to show with this filter.'}>
            <p className="muted small">Read figures from the report; never estimate one on the call. Highlighted text is the client's
              own answer or a figure from the database; grey labels are figures the prototype doesn't model yet.</p>
            {data.steps.filter(keepStep).map((s) => {
              const ck = s.check_key && items[s.check_key]
              const lv = (ck && live[s.check_key]) || {}
              return (
                <div key={s.id} className="wstep">
                  <div className="wstep-n">{/^\d+$/.test(s.n) ? `F${s.n}` : s.n}</div>
                  <div>
                    <div className="lq-head"><b>{s.title}</b>{s.sub && <span className="muted small">{s.sub}</span>}</div>
                    {s.built && <div className="built">How it's built: {s.built}</div>}
                    <Say text={s.say} items={items} figures={data.figures} />
                    {s.low && <div className="hint">Low confidence: {s.low}</div>}
                    {s.note && <div className="hint">{s.note}</div>}
                    {ck && (
                      <div className="check">
                        <div className="small"><b>Check:</b> “{s.check}”</div>
                        <div className="row">
                          <input className="lq-input wide" placeholder="What the client said" value={lv.text || ''}
                                 onChange={(e) => update(s.check_key, { text: e.target.value })} />
                          <button className={`opt flag ${lv.flag ? 'on' : ''}`} onClick={() => update(s.check_key, { flag: !lv.flag }, 0)}>Changes an input</button>
                        </div>
                        {ck.row?.status && ck.row.status !== 'unanswered' && (
                          <div className="recorded">Recording ({ck.row.source_call}): <b>{show(ck.row.value) || ck.row.answer}</b></div>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              )
            })}
          </Fold>}
          {filter !== 'all' && fcounts[filter] === 0 && <p className="muted small">{filter === 'open' ? 'Every question has an answer.' : 'Nothing answered yet.'}</p>}
        </main>

        <aside className="live-rail">
          <div className="panel cpl">
            <h4>Coverage questions go to a CPL</h4>
            <p className="say-line">“Good question. I'll get a coverage specialist to confirm that in writing.”</p>
            <form className="row" onSubmit={(e) => { e.preventDefault(); logCpl() }}>
              <input className="lq-input" placeholder="What did the client ask?" value={cpl} onChange={(e) => setCpl(e.target.value)} />
              <button className="btn">Log it</button>
            </form>
            <ul className="esc">{data.escalations.map((e) => (
              <li key={e.id}>“{e.text}” <span className="muted small">{e.call_time} · {e.source === 'call' ? `from ${e.call_ref}` : e.created_by_name}</span></li>
            ))}</ul>
          </div>
          <div className="panel">
            <h4>Short on time? Get these three</h4>
            {exposure.filter((i) => i.top).map((i) => (
              <a key={i.key} href={`#q-${i.key}`} className={`top3 ${answeredLive(i) ? 'done' : ''}`}>{i.ref} · {i.label}{answeredLive(i) ? ' ✓' : ''}</a>
            ))}
          </div>
          <div className="panel">
            <h4>Flagged as unsure</h4>
            {flags.length === 0 ? <p className="muted small">None yet.</p> :
              flags.map((i) => <a key={i.key} href={`#q-${i.key}`} className="top3">{i.ref} · {i.label}</a>)}
          </div>
          <div className="panel">
            <h4>On this call</h4>
            <ul className="small tips">
              <li>Open with the recording disclosure and get a yes.</li>
              <li>Say the number aloud (“Question 7”) so the recording lines up.</li>
              <li>Offer ranges. Clients guess on record counts and downtime.</li>
              <li>Mark “Client unsure” on any hedged answer.</li>
              <li>Never answer “would this be covered?”</li>
            </ul>
          </div>
        </aside>
      </div>
    </div>
  )
}
