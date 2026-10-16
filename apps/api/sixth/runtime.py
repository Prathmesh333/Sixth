import sqlite3
from datetime import datetime, timedelta, timezone
from threading import RLock
from typing import TypedDict

from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

from .connectors import build_menu, calendar, execute_cart, fingerprint
from .memory import Memory
from .models import FactInput, now, uid
from .planner import Planner
from .storage import Store


class State(TypedDict):
    owner: str
    task_id: str


class Runtime:
    def __init__(self, store: Store, memory: Memory, planner: Planner):
        self.store, self.memory, self.planner = store, memory, planner
        self.lock = RLock()
        self.connection = sqlite3.connect(store.path.parent / "checkpoints.sqlite", check_same_thread=False)
        self.checkpointer = SqliteSaver(self.connection)
        self.checkpointer.setup()
        builder = StateGraph(State)
        builder.add_node("prepare", self.prepare)
        builder.add_node("review", self.review)
        builder.add_node("execute", self.execute)
        builder.add_node("finish", self.finish)
        builder.add_edge(START, "prepare")
        builder.add_conditional_edges("prepare", self.route)
        builder.add_edge("review", "execute")
        builder.add_edge("execute", "finish")
        builder.add_edge("finish", END)
        self.graph = builder.compile(checkpointer=self.checkpointer)

    def close(self):
        self.connection.close()

    def config(self, owner: str, task_id: str):
        return {"configurable": {"thread_id": f"{owner}:{task_id}"}}

    def run(self, owner: str, task_id: str, decision: str | None = None):
        with self.lock:
            task = self.store.get(owner, "task", task_id)
            if not task or task["status"] in {"cancelled", "completed", "failed"}:
                return
            try:
                self.graph.invoke(
                    Command(resume=decision) if decision else {"owner": owner, "task_id": task_id},
                    self.config(owner, task_id),
                )
            except Exception:
                task = self.store.get(owner, "task", task_id)
                if task and task["status"] != "cancelled":
                    task.update(
                        status="failed",
                        reply="I couldn’t finish this request. Your earlier work is saved. Check the connection status and try again.",
                        updated_at=now(),
                    )
                    self.store.put(owner, "task", task)
                    self.store.event(owner, task_id, "task.failed", {"message": task["reply"]})
                    self.store.put(
                        owner,
                        "message",
                        {
                            "id": task_id + "-reply",
                            "conversation_id": task["conversation_id"],
                            "role": "assistant",
                            "text": task["reply"],
                            "task_id": task_id,
                            "created_at": now(),
                        },
                    )

    def route(self, state: State):
        task = self.store.get(state["owner"], "task", state["task_id"])
        return "review" if task.get("action") and task["status"] != "cancelled" else "finish"

    def prepare(self, state: State):
        owner, task_id = state["owner"], state["task_id"]
        task = self.store.get(owner, "task", task_id)
        if task["status"] == "cancelled":
            return state
        task.update(status="running", updated_at=now())
        self.store.put(owner, "task", task)
        self.store.event(owner, task_id, "task.started", {"planner": self.planner.mode})
        intent = self.planner.parse(task["text"])
        task["intent"] = intent.model_dump()
        task["evidence"] = []
        if intent.kind == "remember":
            fact = self.memory.add(
                owner,
                FactInput(
                    subject=intent.subject,
                    predicate=intent.predicate,
                    value=intent.value,
                    source_text=task["text"],
                ),
                source_id=task["source_id"],
                fact_id=task_id + "-fact",
            )
            self.invalidate(owner, fact.get("supersedes"), exclude=task_id)
            task["reply"] = (
                f"I’ll remember that {fact['subject']} {self.fact_phrase(fact)}. You can inspect, edit or forget this in Memory."
            )
            task["evidence"] = [fact]
            self.store.event(owner, task_id, "memory.updated", {"fact_id": fact["id"]})
        elif intent.kind == "dinner":
            self.prepare_dinner(owner, task, intent)
        elif intent.kind == "calendar":
            task["calendar"] = calendar()
            task["reply"] = (
                "On your sample calendar for Saturday: coffee with Sam at 11 am, then dinner at home from 7–9 pm. These are fixture events; no live calendar is connected."
            )
        elif intent.kind == "recall":
            task["evidence"] = self.memory.current(owner)
            facts = task["evidence"]
            task["reply"] = (
                (
                    "Here’s what you’ve asked me to remember:\n"
                    + "\n".join(f"• {f['subject']} {self.fact_phrase(f)}" for f in facts)
                )
                if facts
                else "Your memory is empty. Tell me something useful, such as ‘Maya is vegetarian’."
            )
        else:
            task["reply"] = (
                intent.response
                or "I can help with personal memory, a sample calendar and dinner planning. What would you like to do?"
            )
        self.store.put(owner, "task", task)
        return state

    @staticmethod
    def fact_phrase(fact):
        verb = {"diet": "is", "avoids": "avoids", "allergy": "has an allergy to"}.get(
            fact["predicate"], "prefers"
        )
        return f"{verb} {fact['value']}"

    def prepare_dinner(self, owner, task, intent):
        plans = self.store.list(owner, "plan")
        previous = next((p for p in reversed(plans) if p["conversation_id"] == task["conversation_id"]), None)
        if not previous and (intent.additional_guests or intent.dairy_free):
            previous = plans[-1] if plans else None
        plan_id = previous["id"] if previous else uid()
        guests = intent.guests or ((previous["guests"] if previous else 4) + intent.additional_guests)
        if not 1 <= guests <= 50:
            task["reply"] = "Please choose a guest count between 1 and 50."
            return
        revision = previous["revision"] + 1 if previous else 1
        subject = intent.subject or (previous["subject"] if previous else "Maya")
        if intent.dairy_free:
            fact = self.memory.add(
                owner,
                FactInput(
                    subject=subject,
                    predicate="avoids",
                    value="dairy",
                    source_text=task["text"],
                    scope_type=intent.scope_type,
                    scope_id=plan_id if intent.scope_type == "event" else subject.casefold(),
                ),
                source_id=task["source_id"],
                fact_id=task["id"] + "-fact",
            )
            self.invalidate(owner, fact.get("supersedes"), exclude=task["id"])
        self.memory.ensure_event(owner, plan_id, [subject, owner, "Me"])
        facts = self.memory.current(owner, plan_id)
        self.store.event(
            owner,
            task["id"],
            "context.retrieved",
            {"fact_ids": [f["id"] for f in facts], "backend": self.memory.settings.memory_backend},
        )
        recipe, items, evidence, unsupported = build_menu(facts, guests, subject, owner)
        task["evidence"] = evidence
        if unsupported:
            task["reply"] = unsupported + ". Please review the restriction in Memory before I suggest a cart."
            return
        plan = {
            "id": plan_id,
            "conversation_id": task["conversation_id"],
            "title": f"{subject}’s birthday dinner",
            "subject": subject,
            "guests": guests,
            "revision": revision,
            "recipe": recipe,
            "items": items,
            "evidence_ids": [f["id"] for f in evidence],
            "status": "awaiting_review",
            "updated_at": now(),
            "starts_at": "2026-10-17T19:00:00+05:30",
            "mode": "sandbox",
        }
        if previous:
            self.invalidate_plan(owner, plan_id, exclude=task["id"])
        self.memory.record_plan(owner, plan)
        self.store.put(owner, "plan", plan)
        digest = fingerprint(owner, plan_id, revision, items, plan["evidence_ids"])
        task["plan"] = plan
        task["plan_revision"] = revision
        task["action"] = {
            "action_id": uid(),
            "decision_id": uid(),
            "plan_id": plan_id,
            "tool": "store.replace_cart",
            "arguments": {"items": items},
            "fingerprint": digest,
            "plan_revision": revision,
            "evidence_ids": plan["evidence_ids"],
            "mode": "sandbox",
            "effect_class": "external_write",
            "expires_at": (datetime.now(timezone.utc) + timedelta(minutes=30)).isoformat(),
        }
        task["reply"] = (
            f"I’ve planned {recipe['name'].lower()} for {guests}. "
            + (
                "I used the preferences you shared to choose the menu. "
                if evidence
                else "Both options in the sample catalog are vegetarian. "
            )
            + "Review the ingredients below and I’ll prepare your test cart. No purchase will be made."
        )
        task["status"] = "awaiting_input"
        self.store.event(owner, task["id"], "plan.updated", {"plan_id": plan_id, "revision": revision})

    def review(self, state: State):
        task = self.store.get(state["owner"], "task", state["task_id"])
        if not task.get("decision"):
            self.store.event(
                state["owner"],
                state["task_id"],
                "input.required",
                {"decision_id": task["action"]["decision_id"]},
            )
        interrupt({"decision_id": task["action"]["decision_id"], "task_id": state["task_id"]})
        return state

    def execute(self, state: State):
        owner, task_id = state["owner"], state["task_id"]
        task = self.store.get(owner, "task", task_id)
        if task["status"] == "cancelled":
            return state
        if task.get("decision") != "approve":
            task["reply"] = "I haven’t changed your cart. The plan is saved if you want to revise it."
        else:
            action = task["action"]
            self.store.event(owner, task_id, "tool.started", {"tool": action["tool"], "mode": "sandbox"})
            result = execute_cart(self.store, owner, action)
            task["result"] = result
            task["completed_action_ids"] = [action["action_id"]]
            plan = self.store.get(owner, "plan", action["plan_id"])
            plan["status"] = "cart_ready"
            self.store.put(owner, "plan", plan)
            task["plan"] = plan
            task["reply"] = (
                f"Your test cart is ready for {plan['guests']} people. I checked the saved cart against the plan. This is a sandbox cart; nothing has been purchased."
            )
            self.store.event(
                owner, task_id, "tool.completed", {"action_id": action["action_id"], "result": result}
            )
        self.store.put(owner, "task", task)
        self.project_outcomes(owner)
        return state

    def project_outcomes(self, owner):
        if not self.memory.enabled:
            return
        for item in self.store.list(owner, "outbox"):
            if item["status"] == "applied":
                continue
            try:
                self.memory.graph(owner).query(
                    """
                    MERGE (a:Action {id:$id}) MERGE (o:Outcome {id:$id})
                    SET o.status='verified', o.mode='sandbox', o.verified_at=$at
                    MERGE (a)-[:PRODUCED]->(o)
                """,
                    params={"id": item["id"], "at": item["result"]["verified_at"]},
                )
                item["status"] = "applied"
                self.store.put(owner, "outbox", item)
            except Exception:
                return  # Pending projection is retried without repeating the cart mutation.

    def finish(self, state: State):
        owner, task_id = state["owner"], state["task_id"]
        task = self.store.get(owner, "task", task_id)
        if task["status"] == "cancelled":
            return state
        task.update(status="completed", updated_at=now())
        self.store.put(owner, "task", task)
        self.store.put(
            owner,
            "message",
            {
                "id": task_id + "-reply",
                "conversation_id": task["conversation_id"],
                "role": "assistant",
                "text": task["reply"],
                "task_id": task_id,
                "created_at": now(),
            },
        )
        self.store.event(owner, task_id, "task.completed", {"reply": task["reply"]})
        return state

    def invalidate_plan(self, owner, plan_id, exclude=None):
        for task in self.store.list(owner, "task"):
            if (
                task["id"] != exclude
                and task.get("plan", {}).get("id") == plan_id
                and task["status"] == "awaiting_input"
            ):
                task.update(status="cancelled", stale=True, updated_at=now())
                self.store.put(owner, "task", task)
                self.store.event(
                    owner, task["id"], "task.cancelled", {"reason": "Plan changed; review the new revision."}
                )

    def invalidate(self, owner, fact_id, exclude=None):
        if not fact_id:
            return
        for plan in self.store.list(owner, "plan"):
            if fact_id in plan["evidence_ids"]:
                plan["status"] = "stale"
                self.store.put(owner, "plan", plan)
                self.invalidate_plan(owner, plan["id"], exclude)

    def forget(self, owner: str, fact_id: str):
        with self.lock:
            fact = self.memory.forget(owner, fact_id)
            self.invalidate(owner, fact_id)
            source_ids = {source["source_id"] for source in fact["sources"]}
            for task in self.store.list(owner, "task"):
                if (
                    fact_id in [f["id"] for f in task.get("evidence", [])]
                    or task.get("source_id") in source_ids
                ):
                    self.checkpointer.delete_thread(f"{owner}:{task['id']}")
                    task.update(
                        evidence=[],
                        text="[Removed with forgotten memory]",
                        reply="This context was removed from memory.",
                    )
                    self.store.put(owner, "task", task)
                    self.store.delete(owner, "message", task["id"] + "-reply")
            for message in self.store.list(owner, "message"):
                if message["id"] in source_ids:
                    self.store.delete(owner, "message", message["id"])
            return fact
