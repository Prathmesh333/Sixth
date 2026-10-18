from datetime import datetime, timezone
from typing import Literal
from uuid import uuid4
from zoneinfo import ZoneInfo

from pydantic import BaseModel, ConfigDict, Field, field_validator


def uid() -> str:
    return uuid4().hex


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


class Input(BaseModel):
    model_config = ConfigDict(extra="forbid")


class DemoLogin(Input):
    account: Literal["alex", "jordan"] = "alex"
    access_code: str = Field(default="", max_length=256)


class MessageInput(Input):
    text: str = Field(min_length=1, max_length=16000)
    timezone: str = "Asia/Calcutta"
    source_ids: list[str] = Field(default_factory=list, max_length=20)

    @field_validator("timezone")
    @classmethod
    def valid_timezone(cls, value: str) -> str:
        try:
            ZoneInfo(value)
        except (KeyError, ValueError) as exc:
            raise ValueError("Use a valid IANA timezone") from exc
        return value


class DecisionInput(Input):
    decision_id: str
    decision: Literal["approve", "reject"]
    fingerprint: str
    plan_revision: int = Field(ge=1)


class FactInput(Input):
    subject: str = Field(min_length=1, max_length=100)
    predicate: str = Field(min_length=1, max_length=80)
    value: str = Field(min_length=1, max_length=1000)
    scope_type: Literal["person", "event", "task"] = "person"
    scope_id: str = ""
    source_text: str = Field(min_length=1, max_length=4000)


class CorrectionInput(Input):
    expected_version: int = Field(ge=1)
    value: str = Field(min_length=1, max_length=1000)
    reason: str = Field(min_length=1, max_length=2000)


class Intent(Input):
    kind: Literal["remember", "dinner", "calendar", "recall", "general", "scheduling"]
    subject: str = ""
    predicate: str = ""
    value: str = ""
    guests: int | None = Field(default=None, ge=1, le=50)
    additional_guests: int = Field(default=0, ge=0, le=30)
    dairy_free: bool = False
    scope_type: Literal["person", "event"] = "person"
    response: str = ""
    schedule_action: Literal["", "set_status", "add_event", "find_times", "check_availability", "ask_availability", "propose_meeting", "list_invitations", "confirm_meeting", "accept_invitation", "decline_invitation", "cancel_meeting"] = ""
    friend_usernames: list[str] = Field(default_factory=list, max_length=10)
    starts_at: str = ""
    ends_at: str = ""
    meeting_title: str = ""
    request_id: str = ""
    request_kind: Literal["meeting", "availability_request"] = "meeting"
    schedule_date: str = Field(default="", max_length=10)
    duration_minutes: int = Field(default=30, ge=5, le=480)
    after_event_id: str = ""
