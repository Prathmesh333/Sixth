from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from threading import RLock

from .models import now, uid


class Store:
    """Persistent owned records; short transactions never wrap model/provider calls."""

    def __init__(self, path: Path):
        self.path = path
        path.parent.mkdir(parents=True, exist_ok=True)
        self.lock = RLock()
        with self.transaction() as db:
            db.executescript("""
                PRAGMA journal_mode=WAL;
                CREATE TABLE IF NOT EXISTS records (
                  owner TEXT NOT NULL, kind TEXT NOT NULL, id TEXT NOT NULL,
                  data TEXT NOT NULL, PRIMARY KEY(owner,kind,id));
                CREATE TABLE IF NOT EXISTS events (
                  owner TEXT NOT NULL, task_id TEXT NOT NULL, sequence INTEGER NOT NULL,
                  data TEXT NOT NULL, PRIMARY KEY(owner,task_id,sequence));
                CREATE TABLE IF NOT EXISTS sessions (
                  token_hash TEXT PRIMARY KEY, owner TEXT NOT NULL, csrf TEXT NOT NULL,
                  created_at TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS requests (
                  owner TEXT NOT NULL, route TEXT NOT NULL, key TEXT NOT NULL,
                  fingerprint TEXT NOT NULL, response TEXT NOT NULL,
                  PRIMARY KEY(owner,route,key));
                CREATE TABLE IF NOT EXISTS action_ledger (
                  owner TEXT NOT NULL, id TEXT NOT NULL, fingerprint TEXT NOT NULL,
                  data TEXT NOT NULL, PRIMARY KEY(owner,id), UNIQUE(owner,fingerprint));
            """)

    @contextmanager
    def transaction(self):
        with self.lock:
            db = sqlite3.connect(self.path, timeout=20)
            db.row_factory = sqlite3.Row
            try:
                db.execute("BEGIN IMMEDIATE")
                yield db
                db.commit()
            except BaseException:
                db.rollback()
                raise
            finally:
                db.close()

    @staticmethod
    def put_tx(db, owner: str, kind: str, value: dict):
        db.execute(
            "INSERT INTO records VALUES (?,?,?,?) ON CONFLICT(owner,kind,id) DO UPDATE SET data=excluded.data",
            (owner, kind, value["id"], json.dumps(value)),
        )

    def put(self, owner: str, kind: str, value: dict):
        with self.transaction() as db:
            self.put_tx(db, owner, kind, value)
        return value

    def get(self, owner: str, kind: str, identifier: str) -> dict | None:
        with self.transaction() as db:
            row = db.execute(
                "SELECT data FROM records WHERE owner=? AND kind=? AND id=?", (owner, kind, identifier)
            ).fetchone()
        return json.loads(row[0]) if row else None

    def list(self, owner: str, kind: str) -> list[dict]:
        with self.transaction() as db:
            rows = db.execute(
                "SELECT data FROM records WHERE owner=? AND kind=? ORDER BY rowid", (owner, kind)
            ).fetchall()
        return [json.loads(row[0]) for row in rows]

    def delete(self, owner: str, kind: str, identifier: str):
        with self.transaction() as db:
            db.execute("DELETE FROM records WHERE owner=? AND kind=? AND id=?", (owner, kind, identifier))

    def event(self, owner: str, task_id: str, event_type: str, payload: dict):
        with self.transaction() as db:
            sequence = db.execute(
                "SELECT COALESCE(MAX(sequence),0)+1 FROM events WHERE owner=? AND task_id=?", (owner, task_id)
            ).fetchone()[0]
            event = {
                "task_id": task_id,
                "sequence": sequence,
                "type": event_type,
                "timestamp": now(),
                "payload": payload,
            }
            db.execute("INSERT INTO events VALUES (?,?,?,?)", (owner, task_id, sequence, json.dumps(event)))
        return event

    def events(self, owner: str, task_id: str, after: int = 0) -> list[dict]:
        with self.transaction() as db:
            rows = db.execute(
                "SELECT data FROM events WHERE owner=? AND task_id=? AND sequence>? ORDER BY sequence",
                (owner, task_id, after),
            ).fetchall()
        return [json.loads(row[0]) for row in rows]

    def message(self, owner: str, conversation_id: str, role: str, text: str, **extra):
        return self.put(
            owner,
            "message",
            {
                "id": uid(),
                "conversation_id": conversation_id,
                "role": role,
                "text": text,
                "created_at": now(),
                **extra,
            },
        )
