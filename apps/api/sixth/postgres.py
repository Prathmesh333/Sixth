"""PostgreSQL implementation of the owned operational store.

The small SQL boundary accepts our static qmark queries, never model-generated SQL.
An advisory transaction lock preserves the local store's serialized mutations
across processes. This favors correctness over throughput for the private demo.
"""

import json
from contextlib import contextmanager
from pathlib import Path
from threading import RLock

import psycopg

from .storage import Store


def record_row(cursor):
    names = [column.name for column in cursor.description or ()]

    class Row(dict):
        def __getitem__(self, key):
            return super().__getitem__(names[key] if isinstance(key, int) else key)

    return lambda values: Row(zip(names, values))


class Connection:
    def __init__(self, connection):
        self.connection = connection

    def execute(self, query, params=()):
        return self.connection.execute(query.replace("?", "%s"), params)


class PostgresStore(Store):
    def __init__(self, database_url: str, path: Path):
        self.database_url, self.path, self.lock = database_url, path, RLock()
        with self.transaction() as db:
            for statement in (
                "CREATE TABLE IF NOT EXISTS records (owner TEXT NOT NULL, kind TEXT NOT NULL, "
                "id TEXT NOT NULL, data TEXT NOT NULL, position BIGSERIAL, PRIMARY KEY(owner,kind,id))",
                "CREATE TABLE IF NOT EXISTS events (owner TEXT NOT NULL, task_id TEXT NOT NULL, "
                "sequence INTEGER NOT NULL, data TEXT NOT NULL, PRIMARY KEY(owner,task_id,sequence))",
                "CREATE TABLE IF NOT EXISTS sessions (token_hash TEXT PRIMARY KEY, owner TEXT NOT NULL, "
                "csrf TEXT NOT NULL, created_at TEXT NOT NULL)",
                "CREATE TABLE IF NOT EXISTS requests (owner TEXT NOT NULL, route TEXT NOT NULL, "
                "key TEXT NOT NULL, fingerprint TEXT NOT NULL, response TEXT NOT NULL, "
                "PRIMARY KEY(owner,route,key))",
                "CREATE TABLE IF NOT EXISTS action_ledger (owner TEXT NOT NULL, id TEXT NOT NULL, "
                "fingerprint TEXT NOT NULL, data TEXT NOT NULL, PRIMARY KEY(owner,id), UNIQUE(owner,fingerprint))",
                "CREATE TABLE IF NOT EXISTS sixth_schema_versions (version INTEGER PRIMARY KEY)",
                "INSERT INTO sixth_schema_versions VALUES (1) ON CONFLICT DO NOTHING",
            ):
                db.execute(statement)

    @contextmanager
    def transaction(self):
        with self.lock, psycopg.connect(
            self.database_url, row_factory=record_row, connect_timeout=10, prepare_threshold=None
        ) as connection:
            connection.execute("SET LOCAL statement_timeout = '20s'")
            connection.execute("SELECT pg_advisory_xact_lock(73698401)")
            yield Connection(connection)

    def list(self, owner: str, kind: str):
        with self.transaction() as db:
            rows = db.execute(
                "SELECT data FROM records WHERE owner=? AND kind=? ORDER BY position", (owner, kind)
            ).fetchall()
        return [json.loads(row[0]) for row in rows]
