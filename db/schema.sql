-- UKON cyber-in-the-renewal-window — system of record
-- Rule: numbers live here. The LLM never writes a figure that reaches a client report.

DROP SCHEMA IF EXISTS ukon CASCADE;
CREATE SCHEMA ukon;
SET search_path TO ukon;

-- Which version of this file built the database (checked by the API; see config.SCHEMA_VERSION).
CREATE TABLE schema_info (version TEXT NOT NULL);
INSERT INTO schema_info VALUES ('2026-10-27b');

CREATE TABLE users (
  id          SERIAL PRIMARY KEY,
  name        TEXT NOT NULL,
  role        TEXT NOT NULL CHECK (role IN ('account_manager','producer','cpl','ops','system'))
);

CREATE TABLE clients (
  id            SERIAL PRIMARY KEY,
  slug          TEXT UNIQUE NOT NULL,
  display_name  TEXT NOT NULL,
  renewal_date  DATE NOT NULL,
  agency        TEXT NOT NULL,
  -- Furthest stage reached (five stages: UKON's Stage 1 split into confirm + indications). The API also derives
  -- each stage's status from the data, which is what the app shows.
  stage         TEXT NOT NULL DEFAULT 'confirm'
                CHECK (stage IN ('confirm','indications','proposal','agent_kit','apply_bind','bound')),
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Stage 1 (confirm data): entity resolution is always human-confirmed in the MVP
CREATE TABLE entity_candidates (
  id           SERIAL PRIMARY KEY,
  client_id    INT NOT NULL REFERENCES clients(id),
  legal_name   TEXT NOT NULL,
  state        TEXT NOT NULL,
  address      TEXT,
  domain       TEXT,
  match_score  NUMERIC(4,3) NOT NULL,
  signals      JSONB NOT NULL,          -- which attributes matched / didn't
  status       TEXT NOT NULL DEFAULT 'suggested' CHECK (status IN ('suggested','confirmed','rejected')),
  decided_by   INT REFERENCES users(id),
  decided_at   TIMESTAMPTZ
);

-- Stage 1 (the five fields) and Stage 3 (pack estimates): every field that feeds an indication or a report
CREATE TABLE fields (
  id            SERIAL PRIMARY KEY,
  client_id     INT NOT NULL REFERENCES clients(id),
  key           TEXT NOT NULL,          -- e.g. annual_revenue, employee_count, exposure_score
  label         TEXT NOT NULL,
  kind          TEXT NOT NULL CHECK (kind IN ('text','money','int','score','benchmark')),
  ai_value      JSONB,                  -- what the pipeline recommended
  ai_low        NUMERIC,
  ai_high       NUMERIC,
  confidence    TEXT CHECK (confidence IN ('high','medium','low')),
  method        TEXT,                   -- human-readable estimation method
  sources       JSONB NOT NULL DEFAULT '[]',
  current_value JSONB,                  -- what's in force now (AI value until a human changes it)
  adjustable    BOOLEAN NOT NULL DEFAULT TRUE,   -- agents may move it (slider/edit)
  needs_review  BOOLEAN NOT NULL DEFAULT FALSE,  -- review-by-exception flag
  updated_by    INT REFERENCES users(id),
  updated_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  -- Where the value in force came from: the pipeline (public records / agency file), or a person entering it
  -- from a conversation, the clipboard, an API, or typing it in.
  source_type   TEXT NOT NULL DEFAULT 'pipeline'
                CHECK (source_type IN ('pipeline','conversation','clipboard','api','manual')),
  source_ref    TEXT,                   -- e.g. call_1_intake, a pasted email's subject, an API name
  UNIQUE (client_id, key)
);

-- Who moved what slider, when, and why. Append-only.
CREATE TABLE field_changes (
  id          SERIAL PRIMARY KEY,
  field_id    INT NOT NULL REFERENCES fields(id),
  actor_id    INT NOT NULL REFERENCES users(id),
  old_value   JSONB,
  new_value   JSONB,
  reason      TEXT,
  source_type TEXT,                     -- conversation | clipboard | api | manual | pipeline
  source_ref  TEXT,
  changed_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ===== Stage 2: the agent <-> carrier exchange (indications) =====================================
-- Outbound: one request per carrier, with the five fields exactly as sent (basis snapshot).
CREATE TABLE indication_requests (
  id          SERIAL PRIMARY KEY,
  client_id   INT NOT NULL REFERENCES clients(id),
  carrier     TEXT NOT NULL,
  channel     TEXT NOT NULL CHECK (channel IN ('portal','email','phone','api')),
  options     JSONB NOT NULL,          -- [{tier, limit, deductible}] requested
  basis       JSONB NOT NULL,          -- the five fields as sent, with confidence + review state
  reason      TEXT,                    -- 'initial', 're-request: expired', 're-request: basis changed'
  sent_by     INT NOT NULL REFERENCES users(id),
  sent_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Inbound: every carrier reply as received (PDF, email, underwriter call). Immutable raw file in the wiki.
CREATE TABLE indication_sources (
  id           SERIAL PRIMARY KEY,
  client_id    INT NOT NULL REFERENCES clients(id),
  carrier      TEXT NOT NULL,
  channel      TEXT NOT NULL CHECK (channel IN ('pdf','email','call','portal','clipboard','api','manual')),
  -- How the reply got into the system. We don't know how carriers deliver indications to UKON today,
  -- so all three are supported and every reply records which one was used.
  input_method TEXT NOT NULL CHECK (input_method IN ('conversation','clipboard','api','file','manual')),
  content_sha  TEXT,                  -- hash of the pasted / imported content, to catch duplicates
  path         TEXT NOT NULL,          -- wiki-relative, e.g. raw/quillfeather/indications/x.pdf
  doc_date     DATE NOT NULL,
  reference    TEXT,
  extractor    TEXT NOT NULL CHECK (extractor IN ('live','cached','structured')),
  input_by     INT REFERENCES users(id),   -- the person who pasted / imported it
  extraction   JSONB NOT NULL,
  checks       JSONB NOT NULL DEFAULT '[]',   -- number-in-source checks: [{field, value, found, note}]
  ingested_by  INT NOT NULL REFERENCES users(id),
  ingested_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (client_id, path)
);

-- History: append-only. A new reply adds a version; nothing is overwritten.
-- trust: 'written' (letter, email, portal) or 'verbal' (call). Verbal never reaches a client.
-- review: 'verified' (every figure found verbatim in the source), 'pending_review' (a check failed:
--         a person must confirm), 'confirmed' / 'rejected' (a person did), 'not_applicable' (verbal).
CREATE TABLE indication_versions (
  id                SERIAL PRIMARY KEY,
  client_id         INT NOT NULL REFERENCES clients(id),
  carrier           TEXT NOT NULL,
  tier              TEXT NOT NULL CHECK (tier IN ('essential','recommended','premier')),
  version_no        INT NOT NULL,
  status            TEXT NOT NULL CHECK (status IN ('indicated','declined')),
  trust             TEXT NOT NULL CHECK (trust IN ('written','verbal')),
  review            TEXT NOT NULL CHECK (review IN ('verified','pending_review','confirmed','rejected','not_applicable')),
  limit_amount      INT NOT NULL,
  deductible        INT NOT NULL,
  premium           INT,
  basis_revenue     INT,
  sublimits         JSONB NOT NULL DEFAULT '{}',
  conditions        JSONB NOT NULL DEFAULT '[]',
  bi_waiting_hours  INT,
  specimen_form     TEXT,
  expires_on        DATE,
  note              TEXT,
  quote             TEXT,                -- the line in the source this came from
  hedged            BOOLEAN NOT NULL DEFAULT FALSE,
  source_id         INT NOT NULL REFERENCES indication_sources(id),
  changes           JSONB NOT NULL DEFAULT '[]',   -- diff vs this carrier+tier's previous version
  reviewed_by       INT REFERENCES users(id),
  reviewed_at       TIMESTAMPTZ,
  review_note       TEXT,
  created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (client_id, carrier, tier, version_no)
);

-- Carrier numbers are locked: only the review columns may ever change on a version.
CREATE FUNCTION lock_indication_values() RETURNS trigger AS $$
BEGIN
  IF (NEW.limit_amount, NEW.deductible, NEW.premium, NEW.basis_revenue, NEW.sublimits, NEW.conditions,
      NEW.expires_on, NEW.status, NEW.trust, NEW.carrier, NEW.tier, NEW.version_no)
     IS DISTINCT FROM
     (OLD.limit_amount, OLD.deductible, OLD.premium, OLD.basis_revenue, OLD.sublimits, OLD.conditions,
      OLD.expires_on, OLD.status, OLD.trust, OLD.carrier, OLD.tier, OLD.version_no) THEN
    RAISE EXCEPTION 'carrier indication values are locked (version %)', OLD.id;
  END IF;
  RETURN NEW;
END $$ LANGUAGE plpgsql;
CREATE TRIGGER indication_values_locked BEFORE UPDATE ON indication_versions
  FOR EACH ROW EXECUTE FUNCTION lock_indication_values();
CREATE RULE indication_versions_no_delete AS ON DELETE TO indication_versions DO INSTEAD NOTHING;

-- What needs doing because of a reply (from deterministic rules, never from the model).
CREATE TABLE indication_actions (
  id          SERIAL PRIMARY KEY,
  client_id   INT NOT NULL REFERENCES clients(id),
  carrier     TEXT NOT NULL,
  version_id  INT REFERENCES indication_versions(id),
  kind        TEXT NOT NULL CHECK (kind IN ('confirm_extraction','get_in_writing','new_condition',
                                            'price_change','declined','terms_change')),
  text        TEXT NOT NULL,
  status      TEXT NOT NULL DEFAULT 'open' CHECK (status IN ('open','done')),
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
  closed_by   INT REFERENCES users(id),
  closed_at   TIMESTAMPTZ,
  close_note  TEXT
);

-- Current state, read by the client pack, brief and Ask: the latest WRITTEN version per
-- carrier + option, only if it is an offer and a person or the number check has cleared it.
-- A view, so nothing can write to it.
CREATE VIEW indications AS
  SELECT v.id, v.client_id, v.carrier, v.tier, v.limit_amount, v.deductible, v.premium, v.basis_revenue,
         v.sublimits, v.conditions, v.bi_waiting_hours, v.specimen_form, v.expires_on, v.version_no,
         v.expires_on < current_date AS expired, s.doc_date AS received_on
    FROM (SELECT DISTINCT ON (client_id, carrier, tier) *
            FROM indication_versions WHERE trust = 'written'
           ORDER BY client_id, carrier, tier, version_no DESC) v
    JOIN indication_sources s ON s.id = v.source_id
   WHERE v.status = 'indicated' AND v.review IN ('verified','confirmed');

-- Report versions are immutable snapshots once submitted. "Undo submit" never unlocks one: the submitted
-- version is marked 'withdrawn' (who, when, why; its content and v<N>.html stay as they were), the version it
-- had superseded gets its earlier state back, and editing continues in a new draft. Sent versions can't be withdrawn.
CREATE TABLE report_versions (
  id              SERIAL PRIMARY KEY,
  client_id       INT NOT NULL REFERENCES clients(id),
  version_no      INT NOT NULL,
  state           TEXT NOT NULL CHECK (state IN ('ai_draft','agent_edited','submitted','sent','superseded','withdrawn')),
  snapshot        JSONB NOT NULL,        -- fields + indications + narrative at that moment
  narrative       JSONB NOT NULL,        -- AI prose blocks (no figures; validated)
  created_by      INT NOT NULL REFERENCES users(id),
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  submitted_by    INT REFERENCES users(id),
  submitted_at    TIMESTAMPTZ,
  sent_at         TIMESTAMPTZ,
  superseded_from TEXT CHECK (superseded_from IN ('submitted','sent')),  -- state before a newer submit superseded it
  withdrawn_by    INT REFERENCES users(id),
  withdrawn_at    TIMESTAMPTZ,
  withdraw_reason TEXT,
  UNIQUE (client_id, version_no)
);

-- Stage 5 (present, apply, bind): each call (Wispr Flow capture) ingested into the wiki. A client can have several.
CREATE TABLE intake_calls (
  id           SERIAL PRIMARY KEY,
  client_id    INT NOT NULL REFERENCES clients(id),
  call_ref     TEXT NOT NULL,          -- transcript file stem, e.g. call_2_followup
  wiki_path    TEXT NOT NULL,
  answered     INT NOT NULL DEFAULT 0, -- questions this call answered or updated
  flagged      INT NOT NULL DEFAULT 0,
  ingested_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (client_id, call_ref)
);

-- Intake answers: one row per question-bank item (wiki/raw/intake/intake_questions.md).
-- Two sources per row: what the agent tapped live on the call screen, and what the recording says.
-- Calls merge into these rows; a later call never silently overwrites an agent-confirmed answer.
CREATE TABLE intake_answers (
  id            SERIAL PRIMARY KEY,
  client_id     INT NOT NULL REFERENCES clients(id),
  item_key      TEXT NOT NULL,
  ref           TEXT NOT NULL,
  section       TEXT NOT NULL CHECK (section IN ('identity','exposure','walkthrough')),
  grp           TEXT,
  label         TEXT NOT NULL,
  question      TEXT NOT NULL,
  answer        TEXT,                 -- plain summary of what the client said (from the recording)
  value         JSONB,                -- option / list / number / text
  normalized    TEXT,
  status        TEXT NOT NULL DEFAULT 'unanswered'
                CHECK (status IN ('unanswered','prefilled','needs_followup','confirmed')),
  source_quote  TEXT,
  source_ts     TEXT,
  source_call   TEXT,
  live          JSONB,                -- agent's live taps: {value, multi, confirmed, corrected, flag, note, text}
  live_by       INT REFERENCES users(id),
  live_at       TIMESTAMPTZ,
  conflict      BOOLEAN NOT NULL DEFAULT FALSE,
  notes         JSONB NOT NULL DEFAULT '[]',
  app_keys      JSONB NOT NULL DEFAULT '[]',
  confirmed_by  INT REFERENCES users(id),
  confirmed_at  TIMESTAMPTZ,
  UNIQUE (client_id, item_key)
);

-- "Would this be covered?" questions: never answered by the agent or the AI; routed to a CPL.
CREATE TABLE intake_escalations (
  id          SERIAL PRIMARY KEY,
  client_id   INT NOT NULL REFERENCES clients(id),
  text        TEXT NOT NULL,
  call_time   TEXT,                   -- mm:ss on the call timer or transcript
  source      TEXT NOT NULL CHECK (source IN ('live','call')),
  call_ref    TEXT,
  created_by  INT REFERENCES users(id),
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Carrier application answers, merged across calls (filled by the same extraction as the intake).
CREATE TABLE application_answers (
  id             SERIAL PRIMARY KEY,
  client_id      INT NOT NULL REFERENCES clients(id),
  question_key   TEXT NOT NULL,
  question       TEXT NOT NULL,
  answer         TEXT,
  value          JSONB,                -- machine value when the answer is a number/string to apply
  normalized     TEXT CHECK (normalized IN ('yes','no','partial','unknown','value')),
  status         TEXT NOT NULL CHECK (status IN ('confirmed','needs_followup','unanswered','prefilled')),
  source_quote   TEXT,
  source_ts      TEXT,
  source_call    TEXT,                 -- which call last answered it
  confirmed_by   INT REFERENCES users(id),
  confirmed_at   TIMESTAMPTZ,
  UNIQUE (client_id, question_key)
);

-- Any stage: every question an agent asks the "Ask about this client" skill
CREATE TABLE ask_log (
  id          SERIAL PRIMARY KEY,
  client_id   INT NOT NULL REFERENCES clients(id),
  actor_id    INT NOT NULL REFERENCES users(id),
  question    TEXT NOT NULL,
  answer      TEXT NOT NULL,
  citations   JSONB NOT NULL DEFAULT '[]',
  escalated   BOOLEAN NOT NULL DEFAULT FALSE,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- One timeline for the demo's audit panel
CREATE VIEW audit_trail AS
  SELECT fc.changed_at AS at, u.name AS actor, u.role, 'field_change' AS event,
         f.client_id, f.label AS subject,
         jsonb_build_object('old', fc.old_value, 'new', fc.new_value, 'reason', fc.reason,
                            'source', fc.source_type, 'source_ref', fc.source_ref) AS detail
    FROM field_changes fc JOIN fields f ON f.id = fc.field_id JOIN users u ON u.id = fc.actor_id
  UNION ALL
  SELECT ec.decided_at, u.name, u.role, 'entity_' || ec.status, ec.client_id, ec.legal_name,
         jsonb_build_object('score', ec.match_score)
    FROM entity_candidates ec JOIN users u ON u.id = ec.decided_by WHERE ec.decided_at IS NOT NULL
  UNION ALL
  SELECT rv.created_at, u.name, u.role, 'report_v' || rv.version_no || '_created', rv.client_id,
         'Report v' || rv.version_no, '{}'::jsonb
    FROM report_versions rv JOIN users u ON u.id = rv.created_by
  UNION ALL
  SELECT rv.submitted_at, u.name, u.role, 'report_v' || rv.version_no || '_submitted', rv.client_id,
         'Report v' || rv.version_no, '{}'::jsonb
    FROM report_versions rv JOIN users u ON u.id = rv.submitted_by WHERE rv.submitted_at IS NOT NULL
  UNION ALL
  SELECT rv.withdrawn_at, u.name, u.role, 'report_v' || rv.version_no || '_withdrawn', rv.client_id,
         'Report v' || rv.version_no, jsonb_build_object('reason', rv.withdraw_reason)
    FROM report_versions rv JOIN users u ON u.id = rv.withdrawn_by WHERE rv.withdrawn_at IS NOT NULL
  UNION ALL
  SELECT aa.confirmed_at, u.name, u.role, 'answer_confirmed', aa.client_id, aa.question,
         jsonb_build_object('answer', aa.answer)
    FROM application_answers aa JOIN users u ON u.id = aa.confirmed_by WHERE aa.confirmed_at IS NOT NULL
  UNION ALL
  SELECT ia.confirmed_at, u.name, u.role, 'intake_confirmed', ia.client_id, ia.ref || ' ' || ia.label,
         jsonb_build_object('value', ia.value)
    FROM intake_answers ia JOIN users u ON u.id = ia.confirmed_by WHERE ia.confirmed_at IS NOT NULL
  UNION ALL
  SELECT ie.created_at, COALESCE(u.name, 'Pipeline (AI)'), COALESCE(u.role, 'system'), 'coverage_question_for_cpl',
         ie.client_id, ie.text, jsonb_build_object('source', ie.source, 'call', ie.call_ref)
    FROM intake_escalations ie LEFT JOIN users u ON u.id = ie.created_by
  UNION ALL
  SELECT ic.ingested_at, 'Pipeline (AI)', 'system', 'intake_call_ingested', ic.client_id, ic.call_ref,
         jsonb_build_object('answered', ic.answered, 'flagged', ic.flagged)
    FROM intake_calls ic
  UNION ALL
  SELECT r.sent_at, u.name, u.role, 'indication_requested', r.client_id, r.carrier,
         jsonb_build_object('reason', r.reason, 'channel', r.channel)
    FROM indication_requests r JOIN users u ON u.id = r.sent_by
  UNION ALL
  SELECT s.ingested_at, u.name, u.role, 'indication_received', s.client_id,
         s.carrier || ' (' || s.channel || ', via ' || s.input_method || ')',
         jsonb_build_object('path', s.path, 'input_method', s.input_method)
    FROM indication_sources s JOIN users u ON u.id = s.ingested_by
  UNION ALL
  SELECT v.reviewed_at, u.name, u.role, 'indication_' || v.review, v.client_id,
         v.carrier || ' ' || v.tier || ' v' || v.version_no, jsonb_build_object('reason', v.review_note)
    FROM indication_versions v JOIN users u ON u.id = v.reviewed_by WHERE v.reviewed_at IS NOT NULL
  UNION ALL
  SELECT a.closed_at, u.name, u.role, 'indication_action_done', a.client_id, a.text,
         jsonb_build_object('reason', a.close_note)
    FROM indication_actions a JOIN users u ON u.id = a.closed_by WHERE a.closed_at IS NOT NULL;
