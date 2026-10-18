"""Opt-in browser checks against running local services: SIXTH_E2E=1 uv run pytest tests/test_browser.py."""

import json
import os
from pathlib import Path

import pytest
from playwright.sync_api import expect, sync_playwright

pytestmark = pytest.mark.skipif(
    os.environ.get("SIXTH_E2E") != "1", reason="Requires running API and frontend"
)


def test_google_only_welcome_and_responsive_layout():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True, channel=os.environ.get("SIXTH_BROWSER_CHANNEL", "chrome") or None)
        page = browser.new_page(viewport={"width": 1440, "height": 1000})
        page.goto(os.environ.get("SIXTH_WEB_URL", "http://127.0.0.1:5173/"))
        expect(page.get_by_role("button", name="Continue with Google")).to_be_visible()
        assert page.get_by_role("textbox").count() == 0
        assert page.get_by_text("Private web demo", exact=True).count() == 0
        page.locator("#experience").evaluate("section => window.scrollTo({top: scrollY + section.getBoundingClientRect().top + (section.offsetHeight - innerHeight) * 0.85, behavior: 'instant'})")
        expect(page.locator(".lp-demo-window")).to_have_attribute("data-step", "3")
        page.set_viewport_size({"width": 686, "height": 664})
        page.locator("#experience").evaluate("section => window.scrollTo({top: scrollY + section.getBoundingClientRect().top, behavior: 'instant'})")
        expect(page.locator(".lp-demo-window")).to_have_attribute("data-step", "0")
        page.locator("#experience").evaluate("section => window.scrollTo({top: scrollY + section.getBoundingClientRect().top + (section.offsetHeight - innerHeight) * 0.6, behavior: 'instant'})")
        expect(page.locator(".lp-demo-window")).to_have_attribute("data-step", "2")
        expect(page.get_by_role("heading", name="People change. Context can too.", exact=True)).to_be_visible()
        page.set_viewport_size({"width": 1440, "height": 1000})
        page.get_by_role("button", name="Pause logo animation", exact=True).click()
        expect(page.get_by_role("button", name="Resume logo animation", exact=True)).to_have_attribute("aria-pressed", "true")
        expect(page.locator(".lp-tech-wheel")).to_have_attribute("data-running", "false")
        expect(page.locator(".lp-tech-rotor a")).to_have_count(8)
        for logo in page.locator(".lp-tech-wheel img").all():
            expect(logo).to_have_js_property("complete", True)
            assert logo.evaluate("image => image.naturalWidth > 0")
        page.locator(".lp-technologies").screenshot(path="artifacts/sixth-technology-wheel.png")
        page.emulate_media(reduced_motion="reduce")
        page.get_by_role("button", name="04 Your next move").click()
        expect(page.locator(".lp-pantry-preview")).to_be_visible()
        assert page.locator(".lp-recipe").count() == 0
        page.get_by_role("button", name="Review sample cart", exact=True).click()
        expect(page.get_by_role("dialog")).to_be_visible()
        page.get_by_role("button", name="Prepare sample cart", exact=True).click()
        expect(page.get_by_text("Sample cart prepared. Nothing purchased.")).to_be_visible()
        page.keyboard.press("Escape")
        expect(page.get_by_role("dialog")).not_to_be_visible()
        page.get_by_role("button", name="Plan for six guests", exact=True).click()
        expect(page.locator(".lp-quantity-row").get_by_text("900 g", exact=True)).to_be_visible()
        page.get_by_role("button", name="Plan for four guests", exact=True).click()
        expect(page.get_by_text("400 g", exact=True)).to_be_visible()
        page.get_by_role("button", name="Every connection has a little context").click()
        expect(page.locator(".lp-source-excerpt")).to_be_visible()
        page.get_by_role("button", name="dusk", exact=True).click()
        expect(page.locator(".lp-appearance")).to_have_attribute("data-appearance", "dusk")
        page.get_by_role("button", name="paper", exact=True).click()
        page.get_by_text("Will Sixth buy anything for me?", exact=True).click()
        expect(page.get_by_text("No. This preview prepares a local test cart", exact=False)).to_be_visible()
        page.get_by_role("button", name="02 A dinner together").click()
        expect(page.get_by_text("Maya’s birthday dinner", exact=True)).to_be_visible()
        expect(page.locator(".lp-recipe img")).to_have_js_property("complete", True)
        assert page.locator(".lp-recipe img").evaluate("image => image.naturalWidth > 0")
        page.locator(".lp-story-sticky").screenshot(path="artifacts/sixth-updated-slides.png")
        page.get_by_role("button", name="03 Room for change").click()
        expect(page.locator(".lp-preference-update").get_by_text("Green tea", exact=True)).to_be_visible()
        assert page.locator(".lp-recipe").count() == 0
        page.get_by_role("button", name="01 A small detail").click()
        expect(page.get_by_text("You · Coffee with oat milk", exact=True)).to_be_visible()
        assert page.locator(".lp-recipe").count() == 0
        page.add_script_tag(path="node_modules/axe-core/axe.min.js")
        violations = page.evaluate("async () => (await axe.run(document, {runOnly: {type:'tag', values:['wcag2a','wcag2aa','wcag21aa']}})).violations")
        assert violations == [], json.dumps([
            {"id": item["id"], "nodes": [{"target": node["target"], "reason": node.get("failureSummary")} for node in item["nodes"]]}
            for item in violations
        ], indent=2)
        for width in [320, 390, 768, 1440]:
            page.set_viewport_size({"width": width, "height": 1000})
            page.evaluate("window.scrollTo({top: 0, behavior: 'instant'})")
            assert page.evaluate("document.documentElement.scrollWidth <= innerWidth"), f"Overflow at {width}"
            page.screenshot(path=f"artifacts/sixth-landing-hero-{width}.png")
            page.screenshot(path=f"artifacts/sixth-welcome-{width}.png", full_page=True)
        browser.close()


def test_consumer_workflow_and_responsive_layout():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            headless=True, channel=os.environ.get("SIXTH_BROWSER_CHANNEL", "chrome") or None
        )
        page = browser.new_page(viewport={"width": 1440, "height": 1000})
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.emulate_media(reduced_motion="reduce")
        page.goto(os.environ.get("SIXTH_WEB_URL", "http://127.0.0.1:5173/"))
        page.wait_for_load_state("networkidle")
        base = os.environ.get("SIXTH_WEB_URL", "http://127.0.0.1:5173/").rstrip("/")
        response = page.request.post(base + "/v1/session/demo", data={"account": "alex"}, headers={"Origin": base})
        assert response.status == 200
        page.reload()
        expect(page.get_by_role("heading", name="Your everyday, connected.")).to_be_visible()
        page.add_script_tag(path="node_modules/axe-core/axe.min.js")

        def check_workspace_accessibility():
            issues = page.evaluate("async () => (await axe.run(document, {runOnly: {type:'tag', values:['wcag2a','wcag2aa','wcag21aa']}})).violations")
            assert issues == [], json.dumps(issues, indent=2)

        check_workspace_accessibility()
        expect(page.locator("html")).to_have_attribute("data-theme", "paper")
        page.screenshot(path="artifacts/sixth-workspace-paper.png")
        page.get_by_role("button", name="About Sixth", exact=True).click()
        expect(page.get_by_role("heading", name="Less on your mind. More room for life.")).to_be_visible()
        page.get_by_role("button", name="Return to your workspace").click()
        expect(page.get_by_role("heading", name="Your everyday, connected.")).to_be_visible()
        page.get_by_role("button", name="Show personal context").click()
        expect(page.get_by_role("button", name="Close personal context")).to_be_visible()
        page.get_by_role("button", name="Close personal context").click()
        composer = page.get_by_role("textbox", name="Message Sixth")
        navigations = []
        requests = []
        page.on("framenavigated", lambda frame: navigations.append(frame.url) if frame == page.main_frame else None)
        page.on("request", lambda request: requests.append(request.url))
        optimistic_checks = []

        def delay_message_submission(route):
            # The user bubble must exist before the POST is allowed to finish.
            optimistic_checks.append(page.locator('.message.user p').last.inner_text())
            route.continue_()

        page.route("**/v1/conversations/*/messages", delay_message_submission)

        def send(text):
            composer.fill(text)
            page.get_by_role("button", name="Send message").click()

        send("Maya is vegetarian")
        expect(page.get_by_text("I’ll remember that Maya is vegetarian.", exact=False)).to_be_visible()
        expect(page.get_by_role("button", name="Stop current task")).not_to_be_visible()
        assert optimistic_checks == ["Maya is vegetarian"]
        assert navigations == []
        assert not any(url.endswith("/v1/status") for url in requests)
        assert page.locator('.message.user').count() == 1
        page.locator('.message.user').evaluate("element => element.dataset.continuity = 'keep'")
        assert page.locator('.message.user').evaluate("element => getComputedStyle(element).animationName") == "none"
        page.emulate_media(reduced_motion="no-preference")
        send("Sam likes green tea")
        expect(page.get_by_text("I’ll remember that Sam prefers green tea.", exact=False)).to_be_visible()
        assert page.locator('[data-continuity="keep"]').count() == 1
        assert navigations == []
        assert page.locator('.message.user').last.evaluate("element => getComputedStyle(element).animationName") == "workspace-enter"
        page.emulate_media(reduced_motion="reduce")
        page.unroute("**/v1/conversations/*/messages", delay_message_submission)
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
        check_workspace_accessibility()
        page.screenshot(path="artifacts/sixth-workspace-evidence.png")
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
        page.add_script_tag(path="node_modules/axe-core/axe.min.js")
        check_workspace_accessibility()
        page.screenshot(path="artifacts/sixth-workspace-memory.png")
        page.get_by_role("button", name="Your plans", exact=False).click()
        expect(page.get_by_role("heading", name="Good intentions, taking shape.")).to_be_visible()
        expect(page.locator(".plan-card")).to_have_count(1)
        check_workspace_accessibility()
        page.screenshot(path="artifacts/sixth-workspace-plans.png")
        page.get_by_role("button", name="Alex’s workspace").click()
        page.get_by_role("button", name="Paper", exact=True).click()
        expect(page.locator("html")).to_have_attribute("data-theme", "paper")
        page.screenshot(path="artifacts/sixth-workspace-settings.png")
        page.add_script_tag(path="node_modules/axe-core/axe.min.js")
        violations = page.evaluate(
            "async () => (await axe.run(document, {runOnly: {type:'tag', values:['wcag2a','wcag2aa','wcag21aa']}})).violations"
        )
        assert violations == [], json.dumps(violations, indent=2)
        page.get_by_role("button", name="Grove", exact=True).click()
        expect(page.locator("html")).to_have_attribute("data-theme", "grove")
        check_workspace_accessibility()
        page.get_by_role("button", name="Dusk", exact=True).click()
        check_workspace_accessibility()
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


def test_personal_availability_invite_accept_and_book():
    from datetime import datetime, timedelta

    base = os.environ['SIXTH_WEB_URL'].rstrip('/')
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True, channel=os.environ.get('SIXTH_BROWSER_CHANNEL','chrome') or None)
        a, b = browser.new_context(), browser.new_context()
        def sign_in(context, subject):
            headers={'Origin':base}
            nonce=context.request.post(base+'/v1/auth/google/start',headers=headers).json()['nonce']
            response=context.request.post(base+'/v1/auth/google',headers=headers,data={'credential':json.dumps({'sub':subject,'given_name':subject.title(),'email_verified':True,'nonce':nonce}),'consent':True})
            assert response.status==200
            return {**headers,'X-CSRF-Token':response.json()['csrf_token']}
        ah,bh=sign_in(a,'browser-avery'),sign_in(b,'browser-jules')
        username=b.request.get(base+'/v1/friends').json()['username']
        friend=a.request.post(base+'/v1/friends',headers=ah,data={'username':username}).json()['id']
        assert b.request.post(base+f'/v1/friends/{friend}/accept',headers=bh).status==200
        page=a.new_page()
        page.goto(base)
        page.get_by_role('button',name='Friends',exact=True).click()
        page.get_by_text('Manage sharing',exact=True).click()
        page.get_by_label('Let this friend check my status and busy times').check()
        page.get_by_role('button',name='Save sharing',exact=True).click()
        expect(page.get_by_text('Sharing saved.',exact=True)).to_be_visible()
        page.get_by_role('button',name='Availability',exact=True).click()
        page.get_by_label('Status',exact=True).select_option('available')
        page.get_by_role('button',name='Update status',exact=True).click()
        expect(page.get_by_role('heading',name='Right now · available')).to_be_visible()
        start=(datetime.now()+timedelta(days=3)).replace(hour=13,minute=0,second=0,microsecond=0)
        page.get_by_label('What’s the plan?',exact=True).fill('A quiet tea break')
        page.get_by_label('Starts',exact=True).fill(start.strftime('%Y-%m-%dT%H:%M'))
        page.get_by_label('Ends',exact=True).fill((start+timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M'))
        page.get_by_role('checkbox',name='Browser-Jules',exact=False).check()
        page.get_by_role('button',name='Send invitation',exact=True).click()
        expect(page.locator('.schedule-card').get_by_text('A quiet tea break',exact=True)).to_be_visible()
        other=b.new_page()
        other.goto(base)
        other.get_by_role('button',name='Availability',exact=True).click()
        expect(other.get_by_text('A quiet tea break',exact=True)).to_be_visible()
        other.get_by_role('button',name='Accept',exact=True).click()
        expect(other.get_by_text('Invitation from Browser-Avery · ready to book',exact=True)).to_be_visible()
        page.get_by_role('button',name='Refresh inbox',exact=True).click()
        page.get_by_role('button',name='Confirm booking',exact=True).click()
        expect(page.get_by_text('Invitation from Browser-Avery · booked',exact=True)).to_be_visible()
        assert len(a.request.get(base+'/v1/calendar/events').json()['items'])==1
        assert len(b.request.get(base+'/v1/calendar/events').json()['items'])==1
        assert b.request.put(base+f'/v1/friends/{friend}/sharing',headers=bh,data={'availability':True}).status==200
        page.get_by_role('button',name='Start a new conversation',exact=True).click()
        composer=page.get_by_role('textbox',name='Message Sixth',exact=True)
        def chat(text):
            composer.fill(text)
            page.get_by_role('button',name='Send message',exact=True).click()
        chat('Find a time for tea with Browser-Jules tomorrow')
        expect(page.get_by_text('I found these 30-minute options',exact=False)).to_be_visible()
        expect(page.locator('.message.assistant .message-markdown ol li')).to_have_count(4)
        assert page.locator('.message.assistant .message-content').last.evaluate('node => getComputedStyle(node).borderTopWidth') == '1px'
        assert page.locator('.message.assistant .message-content').last.evaluate('node => getComputedStyle(node).backgroundColor') != 'rgba(0, 0, 0, 0)'
        conversation=a.request.get(base+'/v1/conversations').json()[-1]
        detail=a.request.get(base+'/v1/conversations/'+conversation['id']).json()
        slot=detail['tasks'][-1]['scheduling']['suggested_slots'][1]
        assert len(a.request.get(base+'/v1/scheduling/inbox').json()['items'])==1
        chat('Invite them for the second option')
        expect(page.get_by_role('button',name='Send meeting invitation',exact=True)).to_be_visible()
        assert len(a.request.get(base+'/v1/scheduling/inbox').json()['items'])==1
        page.get_by_role('button',name='Send meeting invitation',exact=True).click()
        expect(page.get_by_text("Sent to your friends' Sixth inboxes.",exact=False)).to_be_visible()
        invitation=next(item for item in b.request.get(base+'/v1/scheduling/inbox').json()['items'] if item['title']=='Tea')
        assert datetime.fromisoformat(invitation['starts_at'])==datetime.fromisoformat(slot['starts_at'])
        other.get_by_role('button',name='Refresh inbox',exact=True).click()
        tea=other.locator('.schedule-card').filter(has=other.get_by_text('Tea',exact=True))
        tea.get_by_role('button',name='Accept',exact=True).click()
        expect(tea.get_by_text('Invitation from Browser-Avery · ready to book',exact=True)).to_be_visible()
        chat('Confirm the tea booking')
        expect(page.get_by_role('button',name='Confirm meeting booking',exact=True)).to_be_visible()
        # Completion must still appear if the final event stream disconnects.
        page.route('**/v1/tasks/*/events',lambda route: route.fulfill(status=200,content_type='text/event-stream',body=': interrupted stream\n\n'))
        page.get_by_role('button',name='Confirm meeting booking',exact=True).click()
        expect(page.get_by_text("Booked in every participant's Sixth calendar",exact=False)).to_be_visible(timeout=10000)
        assert len(a.request.get(base+'/v1/calendar/events').json()['items'])==2
        assert len(b.request.get(base+'/v1/calendar/events').json()['items'])==2
        page.screenshot(path='artifacts/sixth-conversational-scheduling-desktop.png',full_page=True)
        page.screenshot(path='artifacts/sixth-availability-desktop.png',full_page=True)
        page.set_viewport_size({'width':390,'height':844})
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        page.screenshot(path='artifacts/sixth-conversational-scheduling-mobile.png',full_page=True)
        page.add_script_tag(path='node_modules/axe-core/axe.min.js')
        violations=page.evaluate("async () => (await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa']}})).violations")
        assert violations==[], json.dumps([{'id':v['id'],'nodes':[n['target'] for n in v['nodes']]} for v in violations])
        browser.close()
