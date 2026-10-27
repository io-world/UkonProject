import { useEffect, useRef, useState } from 'react'
import { api } from '../api.js'

// Where an answer came from is decided by the backend from the tools that actually ran.
const SOURCE = {
  wiki: ['From the wiki', 'src-wiki'],
  web: ['From the web, not the client file', 'src-web'],
  both: ['Wiki + web', 'src-both'],
  none: ['Not from the wiki · unverified', 'src-none'],
}

const SUGGESTED = [
  'What objections should I expect from this owner, and how do I answer them?',
  'What did the owner say about backups and MFA?',
  'Why does the pack recommend Northwind?',
  'Any recent ransomware news involving dental practices?',
  'Would a breach that starts at Peak Tech be covered?',
]

export default function WikiChat({ actor }) {
  const [turns, setTurns] = useState([])     // {role, content, meta?}
  const [q, setQ] = useState('')
  const [web, setWeb] = useState(true)
  const [busy, setBusy] = useState(false)
  const [err, setErr] = useState(null)
  const end = useRef(null)
  useEffect(() => { end.current?.scrollIntoView({ block: 'nearest' }) }, [turns, busy])

  const send = async (text) => {
    const question = (text ?? q).trim()
    if (!question || busy) return
    const next = [...turns, { role: 'user', content: question }]
    setTurns(next); setQ(''); setBusy(true); setErr(null)
    try {
      const r = await api.chat(next.map(({ role, content }) => ({ role, content })), web, actor)
      setTurns([...next, { role: 'assistant', content: r.answer, meta: r }])
    } catch (e) {
      setErr(e.message); setTurns(turns); setQ(question)
    } finally { setBusy(false) }
  }

  return (
    <section className="card wide chat">
      <div className="chat-head">
        <div>
          <h3>Ask the wiki</h3>
          <p className="muted small">Claude answers from this client's wiki first: sources, call answers, carrier replies, the
            dental industry page and cited research. Numbers come from the database. Coverage questions go to your CPL.</p>
        </div>
        <div className="seg small-seg" role="radiogroup" aria-label="Where to look">
          <button className={!web ? 'on' : ''} onClick={() => setWeb(false)} aria-pressed={!web}>Wiki only</button>
          <button className={web ? 'on' : ''} onClick={() => setWeb(true)} aria-pressed={web}>Wiki first, then web</button>
        </div>
      </div>

      <div className="chat-log" aria-live="polite">
        {turns.length === 0 && (
          <div className="chips">{SUGGESTED.map((s) => <button key={s} className="chip ask" onClick={() => send(s)}>{s}</button>)}</div>
        )}
        {turns.map((t, i) => t.role === 'user'
          ? <div key={i} className="msg msg-user">{t.content}</div>
          : (
            <div key={i} className="msg msg-ai">
              <div className="msg-tags">
                <span className={`src ${SOURCE[t.meta.source][1]}`}>{SOURCE[t.meta.source][0]}</span>
                {t.meta.escalated && <span className="pill warn">Escalated to CPL</span>}
                {t.meta.mode === 'offline' && <span className="pill">keyword search (no API key)</span>}
              </div>
              <div className="msg-text">{t.content}</div>
              {(t.meta.wiki.length > 0 || t.meta.web.length > 0) && (
                <div className="msg-sources">
                  {t.meta.wiki.map((p) => (
                    <a key={p} className="srcchip wiki" href={api.wikiUrl(p)} target="_blank" rel="noreferrer" title="Open the wiki page">{p.replace(/^wiki\//, '')}</a>
                  ))}
                  {t.meta.web.map((w) => (
                    <a key={w.url} className="srcchip web" href={w.url} target="_blank" rel="noreferrer" title={w.url}>{w.title || w.url}</a>
                  ))}
                </div>
              )}
            </div>
          ))}
        {busy && <div className="msg msg-ai muted">Looking in the wiki{web ? ', then the web if needed' : ''}…</div>}
        <div ref={end} />
      </div>

      {err && <div className="err small">{err}</div>}
      <form className="chat-input" onSubmit={(e) => { e.preventDefault(); send() }}>
        <input value={q} onChange={(e) => setQ(e.target.value)} disabled={busy}
               placeholder="Ask about this client, the industry, or (if web is on) anything current" />
        <button className="btn primary" disabled={busy || !q.trim()}>Ask</button>
        {turns.length > 0 && <button type="button" className="btn ghost" onClick={() => setTurns([])} disabled={busy}>New chat</button>}
      </form>
    </section>
  )
}
