"""Isolated browser-test app. Never included in the deployment image."""
import json
import os

from sixth.accounts import Accounts
from sixth.config import Settings
from sixth.main import create_app
from sixth.models import Intent
from sixth.planner import Planner

if os.environ.get('SIXTH_E2E') != '1':
    raise RuntimeError('This test application requires SIXTH_E2E=1')

Accounts.verify_google = lambda self, credential: json.loads(credential)
configuration = Settings()
configuration.google_client_id = 'browser-test.apps.googleusercontent.com'
app = create_app(configuration)


original_parse = Planner.parse


def browser_planner(self, text, **kwargs):
    # Only these synthetic test phrases use a stub classifier. The scheduling
    # tools, persistence, permissions and approval flow run unchanged.
    context = kwargs.get("scheduling_context", {})
    if text == "Find a time for tea with Browser-Jules tomorrow":
        friend = next(person for person in context["friends"] if person["name"] == "Browser-Jules")
        return Intent(kind="scheduling", schedule_action="find_times", friend_usernames=[friend["username"]], schedule_date="tomorrow", meeting_title="Tea")
    if text == "Invite them for the second option":
        previous = context["recent_conversation_scheduling"][-1]
        return Intent(kind="scheduling", schedule_action="propose_meeting", friend_usernames=previous["friends"], meeting_title=previous["title"], **previous["suggested_slots"][1])
    if text == "Confirm the tea booking":
        invitation = next(item for item in context["requests"] if item["title"] == "Tea" and item["status"] == "ready_to_book")
        return Intent(kind="scheduling", schedule_action="confirm_meeting", request_id=invitation["id"])
    return original_parse(self, text, **kwargs)


Planner.parse = browser_planner
