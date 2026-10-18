"""Owned calendars, permissioned friend context, and recipient-approved meetings."""
import hashlib
import json
from datetime import datetime, timedelta, timezone
from typing import Literal
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from .accounts import ACCOUNTS
from .models import now, uid

SCHEDULING = "__scheduling__"


class SchedulingError(ValueError):
    pass


class PresenceInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    status: Literal["available", "busy", "away", "unknown"]
    until: str | None = None


class EventInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    title: str = Field(min_length=1, max_length=160)
    starts_at: str
    ends_at: str
    timezone: str = "Asia/Calcutta"


class MeetingInput(EventInput):
    friend_usernames: list[str] = Field(min_length=1, max_length=10)


class SharingInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    availability: bool = False
    memory_ids: list[str] = Field(default_factory=list, max_length=100)


class ResponseInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    accepted: bool


def window(starts_at, ends_at, zone="Asia/Calcutta"):
    try:
        ZoneInfo(zone)
        start = datetime.fromisoformat(starts_at.replace("Z", "+00:00"))
        end = datetime.fromisoformat(ends_at.replace("Z", "+00:00"))
        if start.tzinfo is None or end.tzinfo is None:
            raise ValueError
        if not start < end or end - start > timedelta(days=31):
            raise ValueError
    except (ValueError, KeyError, AttributeError):
        raise SchedulingError("Use a valid timezone and a start and end time with UTC offsets. The end must follow the start within 31 days.") from None
    return start, end


class Scheduling:
    def __init__(self, store, memory):
        self.store, self.memory = store, memory

    @staticmethod
    def get(db, owner, kind, identifier):
        row = db.execute("SELECT data FROM records WHERE owner=? AND kind=? AND id=?", (owner, kind, identifier)).fetchone()
        return json.loads(row[0]) if row else None

    @staticmethod
    def rows(db, owner, kind):
        return [json.loads(row[0]) for row in db.execute("SELECT data FROM records WHERE owner=? AND kind=?", (owner, kind)).fetchall()]

    def friend(self, db, owner, identifier=None, username=None):
        if username:
            account = self.get(db, ACCOUNTS, "account", username.lower().lstrip("@"))
            if not account:
                matches = []
                for item in self.rows(db, ACCOUNTS, "friend"):
                    if item["status"] != "accepted" or owner not in item["members"]:
                        continue
                    other = next(member for member in item["members"] if member != owner)
                    if self.label(db, other)["name"].casefold() == username.casefold():
                        matches.append(other)
                if len(matches) == 1:
                    account = {"owner": matches[0]}
            if not account or account["owner"] == owner:
                raise SchedulingError("Choose an accepted friend by their Sixth username.")
            identifier = hashlib.sha256(":".join(sorted([owner, account["owner"]])).encode()).hexdigest()
        friend = self.get(db, ACCOUNTS, "friend", identifier)
        if not friend or owner not in friend["members"] or friend["status"] != "accepted":
            raise SchedulingError("This action requires an accepted friendship.")
        other = next(member for member in friend["members"] if member != owner)
        return friend, other

    def label(self, db, owner):
        profile = self.get(db, owner, "profile", "self") or {}
        return {"name": profile.get("name", "Sixth user"), "username": profile.get("username", owner if owner in {"alex", "jordan"} else "")}

    def events_tx(self, db, owner, start, end):
        events = []
        for event in self.rows(db, owner, "calendar_event"):
            if event.get("status") == "cancelled":
                continue
            a, b = window(event["starts_at"], event["ends_at"], event["timezone"])
            if a < end and start < b:
                events.append(event)
        return events

    def presence(self, owner):
        item = self.store.get(owner, "presence", "self") or {"status": "unknown", "until": None}
        if item.get("until") and datetime.fromisoformat(item["until"]) <= datetime.now(timezone.utc):
            return {"status": "unknown", "until": None}
        return {"status": item["status"], "until": item.get("until")}

    def set_presence(self, owner, status, until=None):
        if status not in {"available", "busy", "away", "unknown"}:
            raise SchedulingError("Choose available, busy, away or unknown.")
        if until:
            try:
                parsed = datetime.fromisoformat(until)
                if parsed.utcoffset() is None or parsed <= datetime.now(timezone.utc):
                    raise ValueError()
            except ValueError:
                raise SchedulingError("Choose a future expiry time with a timezone offset.") from None
        return self.store.put(owner, "presence", {"id": "self", "status": status, "until": until, "updated_at": now()})

    def conflicts_tx(self, db, owner, start, end):
        if self.events_tx(db, owner, start, end):
            return True
        flag = self.get(db, owner, "presence", "self") or {}
        until = datetime.fromisoformat(flag["until"]) if flag.get("until") else None
        return flag.get("status") in {"busy", "away"} and (until is None or until > max(start, datetime.now(timezone.utc)))

    def own_events(self, owner):
        return sorted((event for event in self.store.list(owner, "calendar_event") if event.get("status") != "cancelled"), key=lambda event: event["starts_at"])

    def add_event(self, owner, body, identifier=None):
        start, end = window(body["starts_at"], body["ends_at"], body["timezone"])
        identifier = identifier or uid()
        with self.store.transaction() as db:
            existing = self.get(db, owner, "calendar_event", identifier)
            if existing:
                return existing
            if self.events_tx(db, owner, start, end):
                raise SchedulingError("This time overlaps an event in your Sixth calendar. Choose another time.")
            event = {"id": identifier, **body, "starts_at": start.isoformat(), "ends_at": end.isoformat(), "status": "confirmed", "source": "sixth_calendar", "created_at": now()}
            self.store.put_tx(db, owner, "calendar_event", event)
        return event

    def sharing(self, owner, friend_id, body):
        available = {fact["id"] for fact in self.memory.current(owner) if fact.get("scope_type") == "person"}
        if not set(body.memory_ids) <= available:
            raise SchedulingError("Only your current personal memories can be shared. Refresh the memory list and retry.")
        with self.store.transaction() as db:
            friend, _ = self.friend(db, owner, friend_id)
            grants = friend.get("sharing", {})
            grants[owner] = {"availability": body.availability, "memory_ids": list(dict.fromkeys(body.memory_ids))}
            self.store.put_tx(db, ACCOUNTS, "friend", {**friend, "sharing": grants})
        return {"availability": body.availability, "memory_ids": grants[owner]["memory_ids"]}

    def shared_context(self, owner, friend_id):
        with self.store.transaction() as db:
            friend, other = self.friend(db, owner, friend_id)
            granted = friend.get("sharing", {}).get(other, {})
            result = {"friend": self.label(db, other), "availability_shared": bool(granted.get("availability")),
                      "your_sharing": friend.get("sharing", {}).get(owner, {"availability": False, "memory_ids": []})}
        allowed = set(granted.get("memory_ids", []))
        result["memories"] = [{key: fact[key] for key in ("id", "subject", "predicate", "value", "version")}
                              for fact in self.memory.current(other) if fact["id"] in allowed and fact.get("scope_type") == "person"] if allowed else []
        return result

    def availability(self, owner, username, starts_at, ends_at, zone="Asia/Calcutta"):
        start, end = window(starts_at, ends_at, zone)
        with self.store.transaction() as db:
            friend, other = self.friend(db, owner, username=username)
            label = self.label(db, other)
            permitted = friend.get("sharing", {}).get(other, {}).get("availability", False)
            if not permitted:
                return {"friend": label, "status": "unknown", "source": "not_shared", "busy": []}
            events = self.events_tx(db, other, start, end)
            presence = self.get(db, other, "presence", "self") or {}
            until = datetime.fromisoformat(presence["until"]) if presence.get("until") else None
            active = until is None or until > max(start, datetime.now(timezone.utc))
            flag = presence.get("status", "unknown") if active else "unknown"
        return {"friend": label, "status": "busy" if events else flag if flag in {"busy", "away", "available"} else "no_recorded_conflict", "source": "sixth_calendar",
                "busy": [{"starts_at": event["starts_at"], "ends_at": event["ends_at"]} for event in events]}

    def create_request(self, owner, body, kind, identifier=None):
        start, end = window(body["starts_at"], body["ends_at"], body["timezone"])
        if start < datetime.now(timezone.utc):
            raise SchedulingError("Choose a future start time for an availability request or meeting invitation.")
        identifier = identifier or uid()
        with self.store.transaction() as db:
            existing = self.get(db, SCHEDULING, kind, identifier)
            if existing:
                if owner not in existing["members"]:
                    raise SchedulingError("This request is not available.")
                return self.present(db, owner, existing)
            members = [owner]
            for username in body["friend_usernames"]:
                _, other = self.friend(db, owner, username=username)
                if other not in members:
                    members.append(other)
            item = {"id": identifier, "kind": kind, "organizer": owner, "members": members,
                    "title": body["title"], "starts_at": start.isoformat(), "ends_at": end.isoformat(),
                    "timezone": body["timezone"], "status": "pending", "responses": {owner: "accepted"}, "created_at": now()}
            self.store.put_tx(db, SCHEDULING, kind, item)
            return self.present(db, owner, item)

    def present(self, db, owner, item):
        return {key: item[key] for key in ("id", "kind", "title", "starts_at", "ends_at", "timezone", "status")} | {
            "organizer": self.label(db, item["organizer"]), "is_organizer": owner == item["organizer"],
            "your_response": item["responses"].get(owner, "pending"),
            "participants": [{**self.label(db, member), "response": item["responses"].get(member, "pending")} for member in item["members"]],
        }

    def inbox(self, owner):
        with self.store.transaction() as db:
            return [self.present(db, owner, item) for kind in ("meeting", "availability_request")
                    for item in self.rows(db, SCHEDULING, kind) if owner in item["members"]]

    def respond(self, owner, kind, identifier, accepted):
        with self.store.transaction() as db:
            item = self.get(db, SCHEDULING, kind, identifier)
            if not item or owner not in item["members"] or item["organizer"] == owner:
                raise SchedulingError("Only an invited recipient can answer this request.")
            self.friend(db, owner, username=self.label(db, item["organizer"])["username"])
            if item["status"] in {"booked", "cancelled"} or datetime.fromisoformat(item["ends_at"]) <= datetime.now(timezone.utc):
                raise SchedulingError("This invitation is no longer open.")
            answer = "accepted" if accepted else "declined"
            if item["responses"].get(owner) == answer:
                return self.present(db, owner, item)
            if accepted and kind == "meeting" and self.conflicts_tx(db, owner, *window(item["starts_at"], item["ends_at"], item["timezone"])):
                raise SchedulingError("This meeting overlaps an event in your Sixth calendar. Decline or choose a different time.")
            item["responses"][owner] = answer
            responses = [item["responses"].get(member, "pending") for member in item["members"]]
            item["status"] = "declined" if "declined" in responses else "ready_to_book" if all(value == "accepted" for value in responses) else "pending"
            if kind == "availability_request" and "pending" not in responses:
                item["status"] = "answered"
            self.store.put_tx(db, SCHEDULING, kind, item)
            return self.present(db, owner, item)

    def confirm(self, owner, identifier):
        with self.store.transaction() as db:
            item = self.get(db, SCHEDULING, "meeting", identifier)
            if not item or item["organizer"] != owner:
                raise SchedulingError("Only the meeting organizer can confirm the booking.")
            if item["status"] == "booked":
                return self.present(db, owner, item)
            if item["status"] != "ready_to_book":
                raise SchedulingError("Every invited friend must accept before you confirm the booking.")
            start, end = window(item["starts_at"], item["ends_at"], item["timezone"])
            if start < datetime.now(timezone.utc):
                raise SchedulingError("This proposed start time has passed. Propose a new time.")
            for member in item["members"]:
                if member != owner:
                    self.friend(db, owner, username=self.label(db, member)["username"])
                if self.conflicts_tx(db, member, start, end):
                    raise SchedulingError("A participant now has a conflict in their Sixth calendar. Propose another time before booking.")
            for member in item["members"]:
                self.store.put_tx(db, member, "calendar_event", {"id": "meeting-" + identifier,
                    "meeting_id": identifier, "title": item["title"], "starts_at": item["starts_at"],
                    "ends_at": item["ends_at"], "timezone": item["timezone"], "source": "sixth_calendar", "status": "confirmed", "created_at": now()})
            item["status"] = "booked"
            self.store.put_tx(db, SCHEDULING, "meeting", item)
            return self.present(db, owner, item)

    def cancel(self, owner, identifier):
        with self.store.transaction() as db:
            item = self.get(db, SCHEDULING, "meeting", identifier)
            if not item or item["organizer"] != owner:
                raise SchedulingError("Only the organizer can cancel this meeting for everyone.")
            for member in item["members"]:
                event = self.get(db, member, "calendar_event", "meeting-" + identifier)
                if event:
                    self.store.put_tx(db, member, "calendar_event", {**event, "status": "cancelled"})
            item["status"] = "cancelled"
            self.store.put_tx(db, SCHEDULING, "meeting", item)
            return self.present(db, owner, item)

    def context(self, owner):
        with self.store.transaction() as db:
            friends = []
            shared = []
            for item in self.rows(db, ACCOUNTS, "friend"):
                if item["status"] == "accepted" and owner in item["members"]:
                    other = next(member for member in item["members"] if member != owner)
                    grant = item.get("sharing", {}).get(other, {})
                    if grant.get("memory_ids"):
                        shared.append((other, set(grant["memory_ids"]), self.label(db, other)))
                    friends.append({**self.label(db, other), "free_busy_shared": bool(item.get("sharing", {}).get(other, {}).get("availability"))})
            requests = [self.present(db, owner, item) for kind in ("meeting", "availability_request")
                        for item in self.rows(db, SCHEDULING, kind) if owner in item["members"] and item["status"] != "cancelled"]
            events = [event for event in self.rows(db, owner, "calendar_event") if event.get("status") != "cancelled"]
        shared_memories = [{"friend": label, "facts": [{key: fact[key] for key in ("subject", "predicate", "value")}
                            for fact in self.memory.current(other) if fact["id"] in allowed and fact.get("scope_type") == "person"]}
                           for other, allowed, label in shared]
        return {"shared_memories": shared_memories, "source": "sixth_calendar_only", "external_calendar_connected": False,
                "friends": friends, "events": events[-20:], "requests": requests[-15:]}

    @staticmethod
    def digest(owner, arguments):
        return hashlib.sha256((owner + json.dumps(arguments, sort_keys=True)).encode()).hexdigest()

    def prepare(self, owner, task, intent):
        operation = intent.schedule_action
        if operation == "list_invitations":
            requests = self.inbox(owner)
            task["scheduling"] = {"operation": operation, "title": "Your scheduling inbox", "items": requests}
            task["reply"] = "\n".join(f"{item['title']}: {item['starts_at']} — {item['status']} (from {item['organizer']['name']})" for item in requests) if requests else "You have no scheduling requests yet."
            return
        ranged = operation in {"add_event", "check_availability", "ask_availability", "propose_meeting"}
        if ranged and (not intent.starts_at or not intent.ends_at):
            task["reply"] = "What date, start time, end time, and timezone should I use? I will show the exact times before anything is saved or sent."
            return
        zone = task.get("timezone", "Asia/Calcutta")
        if ranged:
            window(intent.starts_at, intent.ends_at, zone)
        if operation in {"check_availability", "ask_availability", "propose_meeting"} and not intent.friend_usernames:
            task["reply"] = "Which accepted friend should I include? You can use their name or Sixth username."
            return
        if operation == "check_availability":
            results = [self.availability(owner, username, intent.starts_at, intent.ends_at, zone) for username in intent.friend_usernames]
            task["scheduling"] = {"operation": operation, "title": "Friend availability", "starts_at": intent.starts_at,
                                  "ends_at": intent.ends_at, "timezone": zone, "results": results}
            task["reply"] = "\n".join(f"{item['friend']['name']}: {item['status']}" + (". They have not shared free/busy access; you can ask them for this slot." if item["status"] == "unknown" else " in their Sixth calendar. Other calendars are not connected.") for item in results)
            return
        if operation in {"confirm_meeting", "accept_invitation", "decline_invitation", "cancel_meeting"} and not intent.request_id:
            task["reply"] = "Which invitation do you mean? Open Availability to select the request, or tell me its title and date."
            return
        labels = {"set_status": "Update profile status", "add_event": "Save busy slot", "ask_availability": "Send availability request",
                  "propose_meeting": "Send meeting invitation", "confirm_meeting": "Confirm meeting booking",
                  "accept_invitation": "Accept invitation", "decline_invitation": "Decline invitation", "cancel_meeting": "Cancel meeting"}
        if operation not in labels:
            task["reply"] = "I can save an event, check shared availability, ask a friend, propose a meeting, or review an invitation. What would you like to do?"
            return
        body = {"title": intent.meeting_title or "Meeting", "starts_at": intent.starts_at, "ends_at": intent.ends_at,
                "timezone": zone, "friend_usernames": intent.friend_usernames}
        if operation in {"ask_availability", "propose_meeting"}:
            with self.store.transaction() as db:
                for username in intent.friend_usernames:
                    self.friend(db, owner, username=username)
        if intent.request_id:
            with self.store.transaction() as db:
                kind = intent.request_kind if operation in {"accept_invitation", "decline_invitation"} else "meeting"
                item = self.get(db, SCHEDULING, kind, intent.request_id)
                if not item or owner not in item["members"]:
                    raise SchedulingError("That invitation is not available to your account.")
                body.update(title=item["title"], starts_at=item["starts_at"], ends_at=item["ends_at"], timezone=item["timezone"],
                            friend_usernames=[self.label(db, member)["username"] for member in item["members"] if member != owner])
        if operation == "set_status":
            if intent.value not in {"available", "busy", "away", "unknown"}:
                task["reply"] = "Which status should I set: available, busy, away, or unknown?"
                return
            body = {"title": "Status: " + intent.value, "status": intent.value, "until": intent.ends_at or None,
                    "starts_at": now() if intent.ends_at else "", "ends_at": intent.ends_at, "timezone": zone}
        arguments = {"operation": operation, "body": body, "request_id": intent.request_id, "request_kind": intent.request_kind}
        task["scheduling"] = {"operation": operation, "title": body["title"], "starts_at": body["starts_at"],
                              "ends_at": body["ends_at"], "timezone": body["timezone"], "friends": body.get("friend_usernames", []),
                              "action_label": labels[operation], "source": "Sixth calendar and in-app invitations"}
        task["action"] = {"action_id": task["id"] + "-schedule", "decision_id": uid(), "plan_id": task["id"],
                          "tool": "scheduling.apply", "arguments": arguments, "fingerprint": self.digest(owner, arguments),
                          "plan_revision": 1, "evidence_ids": [], "mode": "sixth_calendar",
                          "expires_at": (datetime.now(timezone.utc) + timedelta(minutes=30)).isoformat()}
        task["status"] = "awaiting_input"
        task["reply"] = labels[operation] + "? Review the people and exact times below. Meeting invitations require recipient acceptance and a final organizer confirmation before booking."

    def execute(self, owner, action):
        arguments = action["arguments"]
        if action["fingerprint"] != self.digest(owner, arguments):
            raise SchedulingError("The scheduling request changed. Review a fresh proposal.")
        operation, body = arguments["operation"], arguments["body"]
        identifier = action["action_id"]
        if operation == "set_status":
            result = self.set_presence(owner, body["status"], body.get("until"))
            reply = "Your profile status is now " + body["status"] + "."
        elif operation == "add_event":
            result = self.add_event(owner, {key: body[key] for key in ("title", "starts_at", "ends_at", "timezone")}, identifier)
            reply = "Saved to your Sixth calendar. Free/busy access is visible only to friends you have authorized. No external calendar was changed."
        elif operation in {"ask_availability", "propose_meeting"}:
            kind = "availability_request" if operation == "ask_availability" else "meeting"
            result = self.create_request(owner, body, kind, identifier)
            reply = "Sent to your friends' Sixth inboxes. " + ("Their answers will appear in Calendar. No meeting has been booked." if kind == "availability_request" else "Each recipient must accept. Then you can confirm the booking in Calendar.")
        elif operation == "confirm_meeting":
            result = self.confirm(owner, arguments["request_id"])
            reply = "Booked in every participant's Sixth calendar after acceptance and a fresh conflict check. No external calendar was changed."
        elif operation == "cancel_meeting":
            result = self.cancel(owner, arguments["request_id"])
            reply = "Cancelled this meeting in every participant's Sixth calendar."
        else:
            result = self.respond(owner, arguments["request_kind"], arguments["request_id"], operation == "accept_invitation")
            reply = "Your answer is saved in the organizer's Sixth inbox. A meeting is booked only after the organizer's final confirmation."
        return result, reply

    def router(self, session, request_key):
        router = APIRouter()

        def mutate(auth, route, key, body, operation):
            try:
                return request_key(auth["owner"], route, key, body, operation)
            except SchedulingError as exc:
                raise HTTPException(409, str(exc)) from None

        @router.get("/v1/availability")
        def presence(auth=Depends(session)):
            return self.presence(auth["owner"])

        @router.put("/v1/availability")
        def set_presence(body: PresenceInput, auth=Depends(session)):
            try:
                return self.set_presence(auth["owner"], body.status, body.until)
            except SchedulingError as exc:
                raise HTTPException(422, str(exc)) from None

        @router.get("/v1/calendar/events")
        def events(auth=Depends(session)):
            return {"source": "sixth_calendar", "external_connected": False, "items": self.own_events(auth["owner"])}

        @router.post("/v1/calendar/events", status_code=201)
        def create(body: EventInput, idempotency_key: str | None = Header(None), auth=Depends(session)):
            identifier = hashlib.sha256(f"{auth['owner']}:event:{idempotency_key}".encode()).hexdigest()
            return mutate(auth, "calendar_event", idempotency_key, body.model_dump(), lambda: self.add_event(auth["owner"], body.model_dump(), identifier))

        @router.delete("/v1/calendar/events/{identifier}")
        def cancel_event(identifier: str, auth=Depends(session)):
            with self.store.transaction() as db:
                event = self.get(db, auth["owner"], "calendar_event", identifier)
                if not event:
                    raise HTTPException(404, "Event not found")
                if event.get("meeting_id"):
                    raise HTTPException(409, "Use the meeting cancellation control so every participant is updated.")
                self.store.put_tx(db, auth["owner"], "calendar_event", {**event, "status": "cancelled"})
            return {"cancelled": True}

        @router.put("/v1/friends/{identifier}/sharing")
        def share(identifier: str, body: SharingInput, auth=Depends(session)):
            try:
                return self.sharing(auth["owner"], identifier, body)
            except SchedulingError as exc:
                raise HTTPException(409, str(exc)) from None

        @router.get("/v1/friends/{identifier}/context")
        def context(identifier: str, auth=Depends(session)):
            try:
                return self.shared_context(auth["owner"], identifier)
            except SchedulingError as exc:
                raise HTTPException(404, str(exc)) from None

        @router.get("/v1/friends/{identifier}/availability")
        def available(identifier: str, starts_at: str, ends_at: str, timezone: str = "Asia/Calcutta", auth=Depends(session)):
            try:
                with self.store.transaction() as db:
                    _, other = self.friend(db, auth["owner"], identifier)
                    username = self.label(db, other)["username"]
                return self.availability(auth["owner"], username, starts_at, ends_at, timezone)
            except SchedulingError as exc:
                raise HTTPException(409, str(exc)) from None

        @router.get("/v1/scheduling/inbox")
        def inbox(auth=Depends(session)):
            return {"items": self.inbox(auth["owner"])}

        @router.post("/v1/scheduling/{kind}", status_code=201)
        def propose(kind: str, body: MeetingInput, idempotency_key: str | None = Header(None), auth=Depends(session)):
            if kind not in {"meeting", "availability_request"}:
                raise HTTPException(404, "Unknown request type")
            identifier = hashlib.sha256(f"{auth['owner']}:{kind}:{idempotency_key}".encode()).hexdigest()
            return mutate(auth, "scheduling:" + kind, idempotency_key, body.model_dump(),
                          lambda: self.create_request(auth["owner"], body.model_dump(), kind, identifier))

        @router.post("/v1/scheduling/{kind}/{identifier}/respond")
        def respond(kind: str, identifier: str, body: ResponseInput, idempotency_key: str | None = Header(None), auth=Depends(session)):
            if kind not in {"meeting", "availability_request"}:
                raise HTTPException(404, "Unknown request type")
            return mutate(auth, "respond:" + identifier, idempotency_key, body.model_dump(),
                          lambda: self.respond(auth["owner"], kind, identifier, body.accepted))

        @router.post("/v1/scheduling/meeting/{identifier}/confirm")
        def confirm(identifier: str, idempotency_key: str | None = Header(None), auth=Depends(session)):
            return mutate(auth, "confirm:" + identifier, idempotency_key, {}, lambda: self.confirm(auth["owner"], identifier))

        @router.post("/v1/scheduling/meeting/{identifier}/cancel")
        def cancel(identifier: str, idempotency_key: str | None = Header(None), auth=Depends(session)):
            return mutate(auth, "cancel_meeting:" + identifier, idempotency_key, {}, lambda: self.cancel(auth["owner"], identifier))

        return router
