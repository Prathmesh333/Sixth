# Demo and submission

## Pitch

Sixth is a personal assistant that connects what it knows about your life to the actions it takes. It remembers people, preferences and past decisions, adapts when circumstances change, and shows the evidence behind its choices.

Tagline: "Your sixth sense for everyday life."

## Three-minute storyboard

| Time | What the viewer sees | What it proves |
|---|---|---|
| 0:00-0:20 | Add Maya's preference and a pantry note | Sourced personal memory |
| 0:20-0:40 | Open a new conversation and request birthday dinner | Recall across sessions |
| 0:40-1:10 | Calendar check, menu and shopping preview | Connected planning |
| 1:10-1:35 | Review test-cart action; watch tool execution | Agent action with observed outcome |
| 1:35-2:05 | Add guests and a dairy restriction | Correction changes downstream actions |
| 2:05-2:35 | Restart backend and resume | Durable task state and no duplicate mutation |
| 2:35-3:00 | Open evidence path and show actual queries | FalkorDB is central to decisions |

Use synthetic data. Keep the test-store label visible. If browser execution was not completed, show the API adapter honestly. Narration should distinguish recorded memory from new in-session context.

## Demo graph story

Request -> Event -> Attendees -> Current preference assertions -> Sources -> Recipe constraints -> Ingredient quantities -> Cart action -> Verified outcome.

Change a preference, run the same query again, and show a different menu/cart revision. This makes the graph contribution observable. A graph visualization without behavior changing is insufficient.

## Track positioning

Primary: Agents That Act on Connected Data. Secondary: Agent Memory and Coordination. If specialist nodes share persisted findings, demonstrate the actual handoff. Do not claim the Company Brain track based only on personal knowledge or add fake agents to maximize track count. [Track definitions](https://www.wemakedevs.org/hackathons/falkordb).

## Evidence to capture after implementation

Record the pinned dependency versions, setup commands, graph schema, executed query examples, test results, restart trace and a short comparison with no-context behavior. Publish measured numbers only. Show known limitations and live versus simulated integrations.

## Submission package

- Public repository with original event work and required notices.
- Concise README explaining the problem, architecture and FalkorDB role.
- Working deployment where feasible, or complete local setup and demo video.
- Environment-variable names without credentials.
- Screenshots showing chat, action result, memory correction and evidence.
- Video link, team details and selected tracks.
- Optional technical blog about memory, replay and graph-driven decisions.

The [official brief](https://www.wemakedevs.org/hackathons/falkordb) prefers deployment and requires complete local instructions/video when deployment is not possible. Submission closes October 18, 2026 at 23:59 IST. Main FalkorDB implementation must be new event work; general libraries and templates may be reused.

## Draft submission description

Sixth helps people delegate everyday tasks without repeating their context. A FalkorDB personal graph links people, preferences, events and past outcomes. The agent retrieves those relationships to plan and revise actions, while an execution ledger preserves progress across interruptions. Our demonstration connects dinner planning, calendar context and a test shopping cart, then shows how a corrected preference changes the result in a new session.

This paragraph describes the intended final submission. Rewrite it to match the implemented feature set before publishing.
