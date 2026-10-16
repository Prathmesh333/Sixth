import re

import httpx

from .config import Settings
from .models import Intent


class Planner:
    def __init__(self, settings: Settings):
        self.settings = settings

    @property
    def mode(self):
        return "model" if self.settings.model_api_key and self.settings.model_name else "local"

    def parse(self, text: str) -> Intent:
        if self.mode == "model":
            return self.model_parse(text)
        lower = text.casefold()
        numbers = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "eight": 8, "ten": 10}
        guests = None
        count = re.search(r"(?:for|serves?)\s+(\d+|one|two|three|four|five|six|eight|ten)\b", lower)
        if count:
            guests = int(count[1]) if count[1].isdigit() else numbers[count[1]]
        more = re.search(r"(\d+|two|three|four)\s+more\s+(?:people|guests|friends)", lower)
        additional = (int(more[1]) if more[1].isdigit() else numbers[more[1]]) if more else 0
        dairy = any(word in lower for word in ["dairy", "vegan"])
        if any(word in lower for word in ["dinner", "meal", "menu", "more people", "more guests", "replan"]):
            named = re.search(r"([A-Z][a-z]+)[’']s\s+(?:birthday\s+)?(?:dinner|meal)", text)
            return Intent(
                kind="dinner",
                subject=named[1] if named else "",
                guests=guests,
                additional_guests=additional,
                dairy_free=dairy,
                scope_type="event" if "this dinner" in lower else "person",
            )
        if any(word in lower for word in ["calendar", "schedule", "what's on", "what is on"]):
            return Intent(kind="calendar")
        if any(word in lower for word in ["remember about", "what do you know", "my memory", "what matters"]):
            return Intent(kind="recall")
        preference = re.search(
            r"(?:remember(?: that)?\s+)?([A-Z][a-z]+|I)\s+(?:is|am|prefers?|avoids?|likes?)\s+(.+?)[.!]?$",
            text,
        )
        if preference:
            subject = "Me" if preference[1] == "I" else preference[1]
            value = preference[2].strip().rstrip(".! ")
            if value.casefold() in {"vegetarian", "vegan"}:
                predicate = "diet"
            elif dairy:
                predicate, value = "avoids", "dairy"
            else:
                predicate = "preference"
            return Intent(kind="remember", subject=subject, predicate=predicate, value=value)
        return Intent(
            kind="general",
            response="I can remember preferences, check the sample calendar, and plan a dinner with a reviewed test shopping cart. Try ‘Maya is vegetarian’ or ‘Plan Maya’s birthday dinner for four’. Connect a model in Settings for broader language understanding.",
        )

    def model_parse(self, text: str) -> Intent:
        # The model classifies intent; it cannot authorize writes or select a tenant.
        prompt = (
            "Classify the user's request into the JSON schema. Only use remember for an explicit personal fact. "
            "Use dinner for meals, guest changes or meal restrictions; calendar for schedule lookup; recall for memory lookup. "
            "Other requests are general: explain capabilities or draft a useful response without claiming external actions. "
            "Never invent completed tasks, sources or user preferences. Schema: "
            + str(Intent.model_json_schema())
        )
        with httpx.Client(timeout=35) as client:
            response = client.post(
                self.settings.model_base_url.rstrip("/") + "/chat/completions",
                headers={"Authorization": "Bearer " + self.settings.model_api_key},
                json={
                    "model": self.settings.model_name,
                    "temperature": 0,
                    "response_format": {"type": "json_object"},
                    "max_tokens": 1200,
                    "messages": [{"role": "system", "content": prompt}, {"role": "user", "content": text}],
                },
            )
            response.raise_for_status()
            return Intent.model_validate_json(response.json()["choices"][0]["message"]["content"])
