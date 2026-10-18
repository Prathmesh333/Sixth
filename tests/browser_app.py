"""Isolated browser-test app. Never included in the deployment image."""
import json
import os

from sixth.accounts import Accounts
from sixth.config import Settings
from sixth.main import create_app

if os.environ.get('SIXTH_E2E') != '1':
    raise RuntimeError('This test application requires SIXTH_E2E=1')

Accounts.verify_google = lambda self, credential: json.loads(credential)
configuration = Settings()
configuration.google_client_id = 'browser-test.apps.googleusercontent.com'
app = create_app(configuration)
