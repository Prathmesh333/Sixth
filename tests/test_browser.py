"""Opt-in browser checks against running local services: SIXTH_E2E=1 uv run pytest tests/test_browser.py."""

import json
import os
from pathlib import Path

import pytest
from playwright.sync_api import expect, sync_playwright

pytestmark = pytest.mark.skipif(
    os.environ.get("SIXTH_E2E") != "1", reason="Requires running API and frontend"
)


def test_consumer_workflow_and_responsive_layout():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            headless=True, channel=os.environ.get("SIXTH_BROWSER_CHANNEL", "chrome") or None
        )
        page = browser.new_page(viewport={"width": 1440, "height": 1000})
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.goto(os.environ.get("SIXTH_WEB_URL", "http://127.0.0.1:5173/"))
        page.wait_for_load_state("networkidle")
        page.get_by_text("Private web demo", exact=True).click()
        page.get_by_role("button", name="Enter your local workspace").click()
        expect(page.get_by_role("heading", name="Your everyday, connected.")).to_be_visible()
        composer = page.get_by_role("textbox", name="Message Sixth")

        def send(text):
            composer.fill(text)
            page.get_by_role("button", name="Send message").click()

        send("Maya is vegetarian")
        expect(page.get_by_text("I’ll remember that Maya is vegetarian.", exact=False)).to_be_visible()
        page.get_by_role("button", name="Start a new conversation").click()
        send("Plan Maya's birthday dinner for four")
        expect(page.get_by_role("button", name="Prepare test cart")).to_be_visible()
        send("Two more people are joining and Maya avoids dairy for this dinner")
        expect(page.get_by_role("heading", name="Golden chickpea & rice bowls")).to_be_visible()
        expect(page.get_by_text("250 g", exact=True)).to_be_visible()
        page.get_by_role("button", name="Prepare test cart").click()
        expect(page.get_by_text("Cart contents verified. No purchase made.")).to_be_visible()
        page.get_by_role("button", name="Why this plan?").last.click()
        expect(page.get_by_role("heading", name="A reason for every choice.")).to_be_visible()
        page.get_by_role("button", name="Close evidence").click()
        page.reload()
        page.wait_for_load_state("networkidle")
        page.get_by_role("button", name="Memory", exact=False).first.click()
        expect(page.get_by_text("vegetarian", exact=True)).to_be_visible()
        expect(page.get_by_text("This plan only", exact=True)).to_be_visible()
        page.get_by_role("button", name="Edit Maya's diet").click()
        page.get_by_role("textbox", name="Updated preference").fill("vegan")
        page.get_by_role("button", name="Save correction").click()
        expect(page.get_by_text("vegan", exact=True)).to_be_visible()
        page.get_by_role("button", name="Alex’s workspace").click()
        page.get_by_role("button", name="Paper", exact=True).click()
        expect(page.locator("html")).to_have_attribute("data-theme", "paper")
        page.add_script_tag(path="node_modules/axe-core/axe.min.js")
        violations = page.evaluate(
            "async () => (await axe.run(document, {runOnly: {type:'tag', values:['wcag2a','wcag2aa','wcag21aa']}})).violations"
        )
        assert violations == [], json.dumps(violations, indent=2)
        page.get_by_role("button", name="Grove", exact=True).click()
        expect(page.locator("html")).to_have_attribute("data-theme", "grove")
        page.get_by_role("button", name="Dusk", exact=True).click()
        page.get_by_role("button", name="Start a new conversation").click()
        Path("artifacts").mkdir(exist_ok=True)
        for width in [320, 768, 1024, 1440]:
            page.set_viewport_size({"width": width, "height": 900})
            assert page.evaluate("document.documentElement.scrollWidth <= innerWidth"), f"Overflow at {width}"
            expect(composer).to_be_visible()
            page.screenshot(path=f"artifacts/sixth-{width}.png", full_page=True)
        page.set_viewport_size({"width": 360, "height": 800})
        page.get_by_role("button", name="Open navigation").click()
        page.get_by_role("button", name="Memory", exact=False).first.click()
        expect(page.get_by_role("heading", name="A little context goes a long way.")).to_be_visible()
        page.get_by_role("button", name="Forget Maya's avoids").last.click()
        page.get_by_role("button", name="Forget this memory").click()
        expect(page.get_by_text("dairy", exact=True)).not_to_be_visible()
        assert errors == [], errors
        browser.close()
