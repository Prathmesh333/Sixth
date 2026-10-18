from .models import now, uid


def submit_message(store, owner, conversation_id, text, *, task_id=None, source_id=None, channel="web", timezone="Asia/Calcutta"):
    task_id, source_id = task_id or uid(), source_id or uid()
    with store.transaction() as db:
        existing = db.execute(
            "SELECT data FROM records WHERE owner=? AND kind='task' AND id=?", (owner, task_id),
        ).fetchone()
        if existing:
            return task_id
        store.put_tx(db, owner, "message", {
            "id": source_id, "conversation_id": conversation_id, "role": "user", "text": text,
            "created_at": now(), "channel": channel,
        })
        store.put_tx(db, owner, "task", {
            "id": task_id, "conversation_id": conversation_id, "text": text, "source_id": source_id,
            "status": "queued", "plan_revision": 1, "completed_action_ids": [],
            "outstanding_steps": [], "updated_at": now(), "channel": channel,
            "timezone": timezone,
        })
    return task_id
