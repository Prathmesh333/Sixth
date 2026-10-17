import hashlib
import json
import os
import secrets
import time
from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from threading import RLock

from fastapi import Depends, FastAPI, Header, HTTPException, Query, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from redis.exceptions import RedisError

from .config import Settings
from .connectors import calendar, fingerprint
from .memory import Memory
from .models import CorrectionInput, DecisionInput, DemoLogin, FactInput, MessageInput, now, uid
from .planner import Planner
from .postgres import PostgresStore
from .runtime import Runtime
from .storage import Store


def create_app(settings: Settings | None = None):
    settings = settings or Settings()
    if os.getenv("RENDER") == "true":
        if not settings.database_url:
            raise RuntimeError("Render requires SIXTH_DATABASE_URL; ephemeral SQLite is not allowed")
        if settings.demo_login and not settings.demo_access_code:
            raise RuntimeError("Hosted demo login requires SIXTH_DEMO_ACCESS_CODE")
    store_path = settings.data_dir / "sixth.sqlite"
    store = PostgresStore(settings.database_url, store_path) if settings.database_url else Store(store_path)
    memory = Memory(store, settings)
    planner = Planner(settings)
    runtime = Runtime(store, memory, planner)
    executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="sixth")
    mutation_lock = RLock()

    @asynccontextmanager
    async def lifespan(app):
        for owner in store.owners():
            for task in store.list(owner, "task"):
                if task["status"] in {"queued", "running"}:
                    executor.submit(runtime.run, owner, task["id"], task.get("decision"))
            runtime.project_outcomes(owner)
        yield
        executor.shutdown(wait=True)
        runtime.close()
        store.close()

    app = FastAPI(title="Sixth", version="0.1.0", lifespan=lifespan)
    app.state.store, app.state.memory, app.state.runtime = store, memory, runtime
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PATCH", "DELETE"],
        allow_headers=["Content-Type", "X-CSRF-Token", "Idempotency-Key", "Last-Event-ID"],
    )

    def origin_check(request: Request):
        if request.headers.get("origin") not in settings.allowed_origins:
            raise HTTPException(403, "This origin is not allowed")

    def session(request: Request):
        token = request.cookies.get("sixth_session", "")
        digest = hashlib.sha256(token.encode()).hexdigest()
        with store.transaction() as db:
            row = db.execute("SELECT * FROM sessions WHERE token_hash=?", (digest,)).fetchone()
        if not row:
            raise HTTPException(401, "Sign in to your local demo account")
        if (datetime.now(timezone.utc) - datetime.fromisoformat(row["created_at"])).total_seconds() > 86400:
            raise HTTPException(401, "Your demo session expired")
        if request.method not in {"GET", "HEAD", "OPTIONS"}:
            origin_check(request)
            if not secrets.compare_digest(request.headers.get("x-csrf-token", ""), row["csrf"]):
                raise HTTPException(403, "Invalid request token")
        return dict(row)

    def owned(owner, kind, identifier):
        item = store.get(owner, kind, identifier)
        if item is None:
            raise HTTPException(404, "Resource not found")
        return item

    def request_key(owner, route, key, body, operation):
        if not key or not 8 <= len(key) <= 200:
            raise HTTPException(422, "An Idempotency-Key of 8–200 characters is required")
        digest = hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest()
        with mutation_lock:
            with store.transaction() as db:
                row = db.execute(
                    "SELECT * FROM requests WHERE owner=? AND route=? AND key=?", (owner, route, key)
                ).fetchone()
            if row:
                if row["fingerprint"] != digest:
                    raise HTTPException(409, "This request key was already used for a different request")
                return json.loads(row["response"])
            result = operation()
            with store.transaction() as db:
                db.execute(
                    "INSERT INTO requests VALUES (?,?,?,?,?)", (owner, route, key, digest, json.dumps(result))
                )
            return result

    @app.exception_handler(HTTPException)
    async def http_error(request, exc):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "code": f"http_{exc.status_code}",
                "message": str(exc.detail),
                "request_id": uid(),
                "retryable": exc.status_code >= 500,
            },
        )

    @app.get("/health/live")
    def live():
        return {"status": "ok"}

    @app.exception_handler(RedisError)
    async def graph_error(request, exc):
        return JSONResponse(
            status_code=503,
            content={
                "code": "graph_unavailable",
                "message": "FalkorDB is unavailable. Check the configured connection.",
                "request_id": uid(),
                "retryable": True,
            },
        )

    @app.get("/health/ready")
    def ready(response: Response):
        state = memory.health()
        if not state["connected"]:
            response.status_code = 503
        return {"status": "ready" if state["connected"] else "unavailable", "memory": state}

    @app.post("/v1/session/demo")
    def login(body: DemoLogin, request: Request, response: Response):
        origin_check(request)
        if not settings.demo_login:
            raise HTTPException(403, "Demo sign-in is disabled")
        if settings.demo_access_code and not secrets.compare_digest(body.access_code, settings.demo_access_code):
            raise HTTPException(403, "Enter the private demo access code")
        token, csrf = secrets.token_urlsafe(32), secrets.token_urlsafe(24)
        with store.transaction() as db:
            db.execute(
                "INSERT INTO sessions VALUES (?,?,?,?)",
                (hashlib.sha256(token.encode()).hexdigest(), body.account, csrf, now()),
            )
        response.set_cookie(
            "sixth_session",
            token,
            httponly=True,
            samesite="strict",
            secure=settings.cookie_secure,
            max_age=86400,
        )
        return {"account": body.account, "name": body.account.title(), "csrf_token": csrf, "demo": True}

    @app.get("/v1/session")
    def get_session(auth=Depends(session)):
        return {
            "account": auth["owner"],
            "name": auth["owner"].title(),
            "csrf_token": auth["csrf"],
            "demo": True,
        }

    @app.get("/v1/status")
    def status(auth=Depends(session)):
        return {
            "memory": memory.health(),
            "planner": {"mode": planner.mode, "model": settings.model_name or None},
            "calendar": {"mode": "fixture", "connected": False},
            "store": {"mode": "sandbox"},
            "browser": {"connected": False},
            "voice": {"connected": False},
        }

    @app.get("/v1/conversations")
    def conversations(auth=Depends(session)):
        return store.list(auth["owner"], "conversation")

    @app.post("/v1/conversations", status_code=201)
    def create_conversation(auth=Depends(session)):
        return store.put(
            auth["owner"], "conversation", {"id": uid(), "title": "New conversation", "created_at": now()}
        )

    @app.get("/v1/conversations/{conversation_id}")
    def conversation(conversation_id: str, auth=Depends(session)):
        owner = auth["owner"]
        return {
            **owned(owner, "conversation", conversation_id),
            "messages": [m for m in store.list(owner, "message") if m["conversation_id"] == conversation_id],
            "tasks": [t for t in store.list(owner, "task") if t["conversation_id"] == conversation_id],
        }

    @app.post("/v1/conversations/{conversation_id}/messages", status_code=202)
    def message(
        conversation_id: str,
        body: MessageInput,
        idempotency_key: str | None = Header(None),
        auth=Depends(session),
    ):
        owner = auth["owner"]
        conv = owned(owner, "conversation", conversation_id)
        for source_id in body.source_ids:
            owned(owner, "source", source_id)

        def submit():
            task_id, source_id = uid(), uid()
            user_message = {
                "id": source_id,
                "conversation_id": conversation_id,
                "role": "user",
                "text": body.text,
                "created_at": now(),
            }
            task = {
                "id": task_id,
                "conversation_id": conversation_id,
                "text": body.text,
                "source_id": source_id,
                "status": "queued",
                "plan_revision": 1,
                "completed_action_ids": [],
                "outstanding_steps": [],
                "updated_at": now(),
            }
            with store.transaction() as db:
                store.put_tx(db, owner, "message", user_message)
                store.put_tx(db, owner, "task", task)
                if conv["title"] == "New conversation":
                    store.put_tx(db, owner, "conversation", {**conv, "title": body.text[:48]})
            return {"task_id": task_id, "events_url": f"/v1/tasks/{task_id}/events"}

        result = request_key(owner, "message:" + conversation_id, idempotency_key, body.model_dump(), submit)
        executor.submit(runtime.run, owner, result["task_id"])
        return result

    @app.get("/v1/tasks/{task_id}")
    def task(task_id: str, auth=Depends(session)):
        return owned(auth["owner"], "task", task_id)

    @app.get("/v1/tasks/{task_id}/events")
    def events(task_id: str, request: Request, after: int = 0, auth=Depends(session)):
        owner = auth["owner"]
        owned(owner, "task", task_id)
        try:
            after = max(after, int(request.headers.get("last-event-id", "0")))
        except ValueError as exc:
            raise HTTPException(422, "Invalid event offset") from exc

        def stream():
            cursor = after
            for _ in range(240):
                for event in store.events(owner, task_id, cursor):
                    cursor = event["sequence"]
                    yield f"id: {cursor}\ndata: {json.dumps(event)}\n\n"
                current = store.get(owner, "task", task_id)
                if current["status"] in {"awaiting_input", "completed", "failed", "cancelled"}:
                    return
                yield ": heartbeat\n\n"
                time.sleep(0.25)

        return StreamingResponse(
            stream(),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
        )

    @app.post("/v1/tasks/{task_id}/decisions", status_code=202)
    def decision(
        task_id: str, body: DecisionInput, idempotency_key: str | None = Header(None), auth=Depends(session)
    ):
        owner = auth["owner"]

        def apply():
            with runtime.lock:
                item = owned(owner, "task", task_id)
                action = item.get("action")
                if not action or item["status"] != "awaiting_input":
                    raise HTTPException(409, "This action is no longer awaiting review")
                plan = owned(owner, "plan", action["plan_id"])
                digest = fingerprint(owner, plan["id"], plan["revision"], plan["items"], plan["evidence_ids"])
                if (
                    body.decision_id != action["decision_id"]
                    or body.fingerprint != action["fingerprint"]
                    or body.fingerprint != digest
                    or body.plan_revision != plan["revision"]
                    or plan["status"] == "stale"
                    or datetime.fromisoformat(action["expires_at"]) < datetime.now(timezone.utc)
                ):
                    raise HTTPException(409, "The plan changed or this review expired. Request a fresh plan.")
                item["decision"] = body.decision
                item["status"] = "running"
                store.put(owner, "task", item)
                return {"accepted": True, "task_id": task_id}

        result = request_key(owner, "decision:" + task_id, idempotency_key, body.model_dump(), apply)
        executor.submit(runtime.run, owner, task_id, body.decision)
        return result

    @app.post("/v1/tasks/{task_id}/cancel", status_code=202)
    def cancel(task_id: str, auth=Depends(session)):
        owner = auth["owner"]
        with runtime.lock:
            item = owned(owner, "task", task_id)
            if item["status"] not in {"completed", "failed", "cancelled"}:
                item.update(status="cancelled", updated_at=now())
                store.put(owner, "task", item)
                store.event(owner, task_id, "task.cancelled", {})
        return {"accepted": True, "task_id": task_id}

    @app.get("/v1/memory")
    def facts(
        subject_id: str | None = None,
        status: str = "confirmed",
        cursor: int = Query(0, ge=0),
        limit: int = Query(30, ge=1, le=100),
        auth=Depends(session),
    ):
        if status not in {"proposed", "confirmed", "superseded", "disputed"}:
            raise HTTPException(422, "Unknown memory status")
        items = [
            f
            for f in memory.all(auth["owner"])
            if f["status"] == status and (subject_id is None or f["subject_id"] == subject_id)
        ]
        return {
            "items": items[cursor : cursor + limit],
            "next_cursor": str(cursor + limit) if len(items) > cursor + limit else None,
        }

    @app.post("/v1/memory", status_code=201)
    def add_fact(body: FactInput, auth=Depends(session)):
        with runtime.lock:
            fact = memory.add(auth["owner"], body)
            runtime.invalidate(auth["owner"], fact.get("supersedes"))
        return fact

    @app.patch("/v1/memory/{fact_id}")
    def correct(fact_id: str, body: CorrectionInput, auth=Depends(session)):
        try:
            with runtime.lock:
                fact = memory.correct(auth["owner"], fact_id, body.expected_version, body.value, body.reason)
                runtime.invalidate(auth["owner"], fact_id)
                return fact
        except KeyError as exc:
            raise HTTPException(404, "Memory not found") from exc
        except ValueError as exc:
            raise HTTPException(409, str(exc)) from exc

    @app.delete("/v1/memory/{fact_id}", status_code=202)
    def forget(fact_id: str, auth=Depends(session)):
        try:
            runtime.forget(auth["owner"], fact_id)
        except KeyError as exc:
            raise HTTPException(404, "Memory not found") from exc
        job = {
            "id": uid(),
            "target_id": fact_id,
            "status": "completed",
            "requested_at": now(),
            "completed_at": now(),
        }
        return store.put(auth["owner"], "deletion", job)

    @app.get("/v1/deletions/{job_id}")
    def deletion(job_id: str, auth=Depends(session)):
        return owned(auth["owner"], "deletion", job_id)

    @app.get("/v1/plans")
    def plans(auth=Depends(session)):
        return store.list(auth["owner"], "plan")

    @app.get("/v1/calendar")
    def calendar_events(auth=Depends(session)):
        return {"items": calendar(), "mode": "fixture"}

    @app.get("/v1/carts")
    def carts(auth=Depends(session)):
        return store.list(auth["owner"], "cart")

    @app.get("/v1/export")
    def export(auth=Depends(session)):
        owner = auth["owner"]
        facts = memory.all(owner)
        entities = {
            f["subject_id"]: {"id": f["subject_id"], "name": f["subject"], "kind": "Person"} for f in facts
        }
        sources = {s["source_id"]: s for f in facts for s in f["sources"]}
        return {
            "schema_version": "0.1",
            "exported_at": now(),
            "entities": list(entities.values()),
            "sources": list(sources.values()),
            "assertions": facts,
            "plans": store.list(owner, "plan"),
            "carts": store.list(owner, "cart"),
        }

    web_dist = Path(__file__).resolve().parents[2] / "web" / "dist"
    if web_dist.is_dir():
        app.mount("/", StaticFiles(directory=web_dist, html=True), name="web")
    return app


app = create_app()
