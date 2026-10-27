const SLUG = 'sloanslake'
const base = `/api/clients/${SLUG}`

async function req(path, opts = {}) {
  const res = await fetch(path, {
    headers: { 'content-type': 'application/json' },
    ...opts,
    body: opts.body ? JSON.stringify(opts.body) : undefined,
  })
  const data = await res.json().catch(() => ({}))
  if (!res.ok) throw new Error(data.detail || res.statusText)
  return data
}

export const api = {
  users: () => req('/api/users'),
  client: () => req(base),
  undoEntity: (actor) => req(`${base}/entity/undo`, { method: 'POST', body: { actor } }),
  confirmEntity: (id, actor) => req(`${base}/entity/${id}/confirm`, { method: 'POST', body: { actor } }),
  changeField: (key, value, actor, reason, source_type = 'manual', source_ref = null) =>
    req(`${base}/fields/${key}`, { method: 'POST', body: { actor, value, reason, source_type, source_ref } }),
  approveField: (key, actor) => req(`${base}/fields/${key}/approve`, { method: 'POST', body: { actor } }),
  report: (mode) => req(`${base}/report?mode=${mode}`),
  reportVersion: (n) => req(`${base}/report?version=${n}`),
  undoSubmit: (actor, reason) => req(`${base}/report/undo-submit`, { method: 'POST', body: { actor, reason } }),
  versions: () => req(`${base}/versions`),
  submit: (actor) => req(`${base}/report/submit`, { method: 'POST', body: { actor } }),
  send: (actor) => req(`${base}/report/send`, { method: 'POST', body: { actor } }),
  // Stage 2: indications (carrier figures are read-only; no call writes one)
  indications: () => req(`${base}/indications`),
  sendToCarriers: (carriers, actor) => req(`${base}/indications/send`, { method: 'POST', body: { actor, carriers } }),
  ingestReply: (path, actor) => req(`${base}/indications/ingest`, { method: 'POST', body: { actor, path } }),
  reviewIndication: (vid, decision, note, actor) =>
    req(`${base}/indications/versions/${vid}/review`, { method: 'POST', body: { actor, decision, note } }),
  actionDone: (id, note, actor) => req(`${base}/indications/actions/${id}/done`, { method: 'POST', body: { actor, note } }),
  brief: () => req(`${base}/brief`),
  application: () => req(`${base}/application`),
  intakeCalls: () => req(`${base}/intake/calls`),
  intake: () => req(`${base}/intake`),
  intakeLive: (key, live, actor) => req(`${base}/intake/${key}/live`, { method: 'POST', body: { actor, live } }),
  intakeConfirm: (key, actor, value) =>
    req(`${base}/intake/${key}/confirm`, { method: 'POST', body: { actor, value: value === undefined ? null : value } }),
  intakeEscalate: (text, call_time, actor) => req(`${base}/intake/escalations`, { method: 'POST', body: { actor, text, call_time } }),
  intakeIngest: (transcript, actor) => req(`${base}/intake/ingest`, { method: 'POST', body: { actor, transcript } }),
  htmlUrl: (version) => `${base}/report.html${version ? `?version=${version}` : ''}`,
  confirmAnswer: (key, actor, answer, normalized) =>
    req(`${base}/application/${key}/confirm`, { method: 'POST', body: { actor, answer, normalized } }),
  audit: () => req(`${base}/audit`),
  ask: (question, actor) => req(`${base}/ask`, { method: 'POST', body: { actor, question } }),
}

// Where a value came from. Shown on every field and every carrier reply.
export const SOURCE_LABEL = {
  pipeline: 'Public records & agency file (pipeline)', conversation: 'Conversation (Wispr Flow)',
  clipboard: 'Copied from clipboard', api: 'API', manual: 'Typed in by hand',
}

export async function readClipboard() {
  try { return await navigator.clipboard.readText() } catch { return null }
}

export const money = (n) =>
  n == null ? '—' : '$' + Number(n).toLocaleString('en-US', { maximumFractionDigits: 0 })
export const short = (n) =>
  n >= 1e6 ? `$${(n / 1e6).toFixed(n % 1e6 ? 2 : 0)}M` : n >= 1e3 ? `$${Math.round(n / 1e3)}K` : money(n)
export const when = (s) =>
  s ? new Date(s).toLocaleString('en-US', { month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' }) : '—'
