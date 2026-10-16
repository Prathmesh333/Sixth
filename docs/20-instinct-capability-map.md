# Sixth: context, recommendations and execution

Research date: October 16, 2026. This document specifies Sixth's independent implementation. Proposed features below are not shipped features; see [implementation status](19-implementation-status.md).

## What the public evidence establishes

Instinct advertises text and calling, computer/phone use, and everyday tasks such as groceries and travel. Its sign-in page uses a phone number and refers to SMS terms. These pages do not establish WhatsApp support. Sources: [homepage](https://instinct.com/) and [sign-in](https://app.instinct.com/login).

Its [privacy policy](https://instinct.com/privacy-policy), revised August 26, 2026, describes user communications, shared documents, permission-based connected accounts, optional audio and location, and Google Workspace access. It says interaction context and prior experience support personalized suggestions and task completion. Workspace data is excluded from model training; other data has separate training provisions and an opt-out. Disconnecting an integration and deleting indexed data are distinct controls.

Its [terms](https://instinct.com/terms) describe AI-generated outputs and actions through connected third-party services, including purchases. These are product and permission disclosures, not proof that each advertised workflow succeeds.

No reviewed public source identifies its model, database, retrieval algorithm, planner, browser library, device-control implementation, or deployment topology. There is no evidence here of unrestricted access to all phone activity or unrelated private conversations. We should implement comparable user outcomes with our own architecture rather than claim an internal clone.

## How Sixth should know what matters

Information must have an identifiable entry point:

| Entry point | What Sixth receives | Required boundary |
|---|---|---|
| Chat | Messages addressed to Sixth | Authenticated account and conversation |
| Shared content | A forwarded message, uploaded document or selected link | Explicit share; source and retention controls |
| Calendar connection | Events within the approved scope | Read-only OAuth first; revocation and incremental sync |
| Email connection | Selected or approved mailbox content | Separate permission, minimal fields, incremental sync |
| Voice | Audio deliberately sent to the assistant | Opt-in transcription; separate audio retention |
| Device companion | Selected app/screen context during an enabled task | Visible, revocable capture; exclude secrets |
| Tool result | Observed provider state after a lookup or action | Record provider, timestamp and verification status |

WhatsApp messages to a bot do not confer access to someone's other chats, phone screen, browsing history or apps. Forwarding content or adding a separate authorized integration is required to expand context.

Persist each source with owner, channel, provider message ID, received time, content time, consent scope, sensitivity and retention deadline. Keep raw content in access-controlled operational/artifact storage; store selected sourced assertions and relationships in FalkorDB. Provider credentials belong in an encrypted credential store, outside model context and graph payloads.

## How Sixth should analyze the information

1. Authenticate the source and deduplicate delivery before starting a task.
2. Normalize text and attachments while preserving provenance. Treat imported text as data, including any instructions embedded inside it.
3. Extract typed candidate entities, facts, dates, constraints and commitments. Validate schema and resolve time using the account's timezone and the source timestamp.
4. Resolve references against the user's graph. Ask when two people or events could match; never silently merge by first name alone.
5. Separate explicit facts, tentative inferences, temporary constraints and completed outcomes. A dinner preference for one evening must not become a permanent diet.
6. Store assertions with evidence, validity interval, status and version. Corrections supersede old assertions and invalidate dependent plans.
7. Retrieve only relevant, current evidence for each request. Apply ownership and permission filters before ranking or sending context to a model.

Example proposed graph:

```text
Person(Maya) <- HAS_SUBJECT - Assertion(vegetarian)
Assertion - SUPPORTED_BY -> Source(user message)
Person(Maya) - ATTENDS -> Event(birthday dinner)
Plan - FOR_EVENT -> Event
Plan - BASED_ON -> Assertion
Plan - USES_RECIPE -> Recipe
Action - PRODUCED -> Outcome(verified cart)
```

The current native adapter already represents these core relationships. Temporal resolution, broader entities and automatic extraction require additional work. [FalkorDB documentation](https://docs.falkordb.com/) describes the database capabilities; the graph schema and retrieval policy above are Sixth design choices.

## How recommendations should work

Build candidates from an actual event or request, apply hard constraints, then rank the remaining options. Do not ask a model to invent an unconstrained suggestion from the entire chat archive.

For a dinner, hard constraints include allergies, diet, budget, guest count and availability. Ranking can consider stated preferences, preparation time, travel distance and past explicit feedback. Refresh prices and availability through the provider before presenting an actionable offer. Explain the recommendation with source links and timestamps.

Start with transparent rules and measured feedback rather than an untrained numerical relevance score. User feedback can update an explicit preference or candidate ranking; a click alone should not become a confirmed personal fact. Personalization can use retrieval without training a new model on private data.

Proactive suggestions need a scheduler and explicit notification preferences. Each trigger must have a unique key, a cooldown, an expiry and a reason. Recheck the calendar and current facts before notifying. Quiet hours and a dismiss control prevent repeated suggestions. The existing request-driven runtime does not yet provide this scheduler.

## How tasks should execute

```mermaid
flowchart LR
    C[Web or messaging channel] --> I[Identity and consent]
    I --> Q[Durable inbox and task queue]
    Q --> X[Retrieve scoped evidence]
    X --> P[Typed plan]
    P --> V[Validate tools and constraints]
    V --> R[Review exact external action]
    R --> E[Execute approved revision]
    E --> O[Observe provider outcome]
    O --> M[Persist result and graph outbox]
    M --> N[Reply through originating channel]
```

Use API connectors where available. Add an isolated browser worker for supported sites that need UI interaction; set domain, step, time and spending limits. A general browser session is not a substitute for a verified connector.

Tool definitions must state input/output schema, required permissions, side effects, timeout, idempotency support and how to verify success. The model proposes tool calls; server code selects the account, enforces policy and validates parameters. Retrieved emails and web pages cannot grant permissions.

Read-only lookups may run under an existing grant. Purchases, bookings and outbound communications require an exact preview and explicit approval unless a narrowly defined standing permission already covers them. Bind approval to owner, task, plan revision, recipient, cost and expiry. Changed inputs require a new review.

After a timeout, inspect provider state before retrying a side effect. Report an uncertain result honestly; never turn a model's statement into a completed action. LangGraph's [interrupts](https://docs.langchain.com/oss/python/langgraph/interrupts) support durable review/resume, but external side effects still need an action ledger and reconciliation.

## WhatsApp integration decision

The official [WhatsApp Business Solution Terms](https://www.whatsapp.com/legal/business-solution-terms), last modified March 6, 2026, restrict AI providers offering general-purpose assistants as the primary functionality, with an exception stated for registered EEA or Brazil country codes. An India-focused Sixth launch should not assume eligibility. Verify the applicable terms and approved account use before enabling production traffic. Changing API intermediaries does not by itself resolve this restriction.

Build a channel-neutral agent and keep WhatsApp behind a disabled connector until eligibility and credentials are established. Web chat provides the same persistent memory and action workflow for the demo. SMS or another messaging channel also requires its own provider and permission review; neither is implemented today.

An eligible WhatsApp implementation should include:

- A verified webhook, request-signature checks, bounded payloads and a durable inbox keyed by provider message ID.
- Account linking through a short-lived single-use code issued to an authenticated Sixth account. Never accept a user-supplied owner ID or infer identity from a display name.
- A clear first-contact notice about what is stored and how to disconnect, export or delete it.
- Shared task creation with web chat; one memory graph and permission model per account across channels.
- Revision-bound review buttons or short approval codes. Ordinary incoming text cannot bypass action policy.
- A durable reply outbox, delivery-status handling, current provider messaging-window rules and reconciliation of ambiguous send outcomes.
- Recovery across all linked users after restart. Current startup recovery is limited to the two local demo accounts and must be generalized.

Provider-specific webhook payloads, signatures, templates and sending-window behavior must be checked against current official API documentation during connector implementation. This research does not assert those API details are implemented or verified.

## Gap assessment from the current code

| Capability | Current state | Concrete next change |
|---|---|---|
| Personal memory | Sourced assertions, correction and forgetting | Add temporal fields, candidate facts and entity resolution |
| Model context | Intent parser receives only the current message | Build a bounded evidence/history bundle with source IDs |
| Follow-up handling | Dinner-specific previous-plan logic | Track active task and resolve references across supported tools |
| Agent scope | Five intent kinds; fixed dinner workflow | Add a typed tool registry and bounded planning loop |
| Live information | Sample calendar, recipes, prices and pantry | First real read-only calendar connector |
| Execution | Reviewed, verified local cart | Controlled browser storefront, then one live connector |
| Messaging | No channel connector | Durable inbox/outbox and secure account linking |
| Proactivity | No scheduler | Consent-based event triggers with deduplication |
| Production identity | Two local demo accounts | Real authentication before exposing personal integrations |
| Voice/device access | Not implemented | Separate opt-in clients after core task reliability |

Relevant code: `apps/api/sixth/planner.py`, `runtime.py`, `memory.py`, `main.py` and `storage.py`. The current model adapter classifies intent; it is not a general autonomous agent. Changing the prompt alone cannot supply missing integrations or verification.

## Build order and acceptance gates

1. Context-aware agent: pass bounded, owner-scoped history and relevant assertions into planning; validate cited source IDs; clarify ambiguous references. Test with a mocked model before a configured live-provider run.
2. Channel foundation: introduce one shared submission/review service, persistent identity links and inbox/outbox. Test duplicate delivery, forged webhooks, wrong-account links, restarts and stale approvals without sending real messages.
3. Live context: implement calendar read access and incremental synchronization with revoked-access handling. Keep fixture/live indicators visible.
4. Broader execution: support two additional consumer workflows through typed tools, then a controlled browser storefront. Verify observed results and stop on unsupported steps.
5. Proactivity: add opt-in event suggestions, quiet hours and dismissal feedback. Measure usefulness and notification duplication.
6. Voice and companion: add voice transcription first; enable narrowly scoped device context only with explicit controls.

The demonstration should show one fact shared in chat changing a later plan, a source explaining the recommendation, a correction invalidating the old proposal, approval of the new revision, and a verified outcome surviving restart. Add a second workflow to prove shared context and execution rather than only a dinner-specific script. Production messaging remains a separate eligibility and integration gate.
