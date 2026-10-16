-- Proposed SQLite schema. Validated as DDL only; not an implemented action service.
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS tasks (
  id TEXT PRIMARY KEY,
  owner_id TEXT NOT NULL,
  conversation_id TEXT NOT NULL,
  status TEXT NOT NULL,
  plan_revision INTEGER NOT NULL DEFAULT 1,
  state_json TEXT NOT NULL,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS actions (
  id TEXT PRIMARY KEY,
  task_id TEXT NOT NULL REFERENCES tasks(id),
  owner_id TEXT NOT NULL,
  tool TEXT NOT NULL,
  fingerprint TEXT NOT NULL,
  idempotency_key TEXT NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('proposed','awaiting_review','ready','running','reconciling','succeeded','failed','cancelled')),
  arguments_json TEXT NOT NULL,
  result_json TEXT,
  provider_ref TEXT,
  lease_owner TEXT,
  lease_expires_at TEXT,
  version INTEGER NOT NULL DEFAULT 1,
  UNIQUE(owner_id,idempotency_key)
);
CREATE TABLE IF NOT EXISTS decisions (
  id TEXT PRIMARY KEY,
  action_id TEXT NOT NULL REFERENCES actions(id),
  owner_id TEXT NOT NULL,
  fingerprint TEXT NOT NULL,
  plan_revision INTEGER NOT NULL,
  decision TEXT CHECK (decision IN ('approve','reject') OR decision IS NULL),
  expires_at TEXT NOT NULL,
  decided_at TEXT
);
CREATE TABLE IF NOT EXISTS task_events (
  task_id TEXT NOT NULL REFERENCES tasks(id),
  sequence INTEGER NOT NULL,
  type TEXT NOT NULL,
  occurred_at TEXT NOT NULL,
  payload_json TEXT NOT NULL,
  PRIMARY KEY(task_id,sequence)
);
CREATE TABLE IF NOT EXISTS outbox (
  id TEXT PRIMARY KEY,
  owner_id TEXT NOT NULL,
  kind TEXT NOT NULL,
  payload_json TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'pending',
  attempts INTEGER NOT NULL DEFAULT 0,
  created_at TEXT NOT NULL,
  applied_at TEXT
);
CREATE TABLE IF NOT EXISTS deletion_jobs (
  id TEXT PRIMARY KEY,
  owner_id TEXT NOT NULL,
  target_id TEXT NOT NULL,
  status TEXT NOT NULL,
  requested_at TEXT NOT NULL,
  completed_at TEXT
);
-- Add migrations, attempts, request idempotency, identities, source and conversation
-- tables during implementation. LangGraph owns its checkpoint tables.
