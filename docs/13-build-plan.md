# Build plan and backlog

## Event horizon

The official event runs October 15-18, 2026, with submissions closing October 18 at 23:59 IST. [Source](https://www.wemakedevs.org/hackathons/falkordb). This plan starts October 16; blocks are effort estimates, not a claim about hours remaining today.

Build a broad product foundation with one polished end-to-end demonstration. Do not spend the remaining event implementing every consumer skill.

## Critical path

| Block | Effort estimate | Work | Exit evidence |
|---|---|---|---|
| A | 2-3 hours | Pin dependencies; start FalkorDB; test client and checkpoint | One graph query and restart smoke test |
| B | 3-4 hours | Seed two users; assertion service; bounded retrieval | Correct scoped facts and sources |
| C | 4-5 hours | Runtime stages, SQL action ledger, test-store API | Request reaches verified cart |
| D | 3-4 hours | Chat stream, action cards, memory/evidence views | User completes the loop in browser |
| E | 3-4 hours | Corrections, new session, worker restart and failure cases | No duplicate side effect; updated plan |
| F | 2-3 hours | Browser worker spike against test store | Recorded browser action with independent verification |
| G | 3-4 hours | Theme polish, demo recording, README and submission | Reproducible setup and complete submission |

Total estimated engineering effort is 20-27 hours, excluding unforeseen setup failures and breaks. A solo builder should cut optional work early. Parallel team roles are suggestions for humans, not a requirement to run multiple agents.

## Backlog

| ID | Priority | Item | Depends on | Done when |
|---|---|---|---|---|
| SIX-01 | P0 | Pin runtime and database versions | None | Lockfiles and image digest recorded |
| SIX-02 | P0 | Backend-owned user/graph mapping | SIX-01 | Two-user isolation test passes |
| SIX-03 | P0 | Sourced assertions and retrieval | SIX-02 | Current facts and source paths returned |
| SIX-04 | P0 | Calendar and recipe fixture adapters | SIX-01 | Typed results and mode labels |
| SIX-05 | P0 | Test-store cart adapter | SIX-01 | Cart state can be read independently |
| SIX-06 | P0 | Task runtime and persistent checkpoint | SIX-03,04 | Task can pause and resume |
| SIX-07 | P0 | Ledger, review binding and outbox | SIX-05,06 | Crash tests avoid duplicate cart effects |
| SIX-08 | P0 | Streaming chat and action review | SIX-06,07 | UI reflects persisted task state |
| SIX-09 | P0 | Correct, supersede and forget memory | SIX-03,07 | Plans invalidate and deleted facts disappear |
| SIX-10 | P0 | Evidence panel and session restart demo | SIX-08,09 | No previous transcript needed |
| SIX-11 | P1 | Browser-use test-store execution | SIX-05,07 | UI action verified through store API |
| SIX-12 | P1 | Dusk and Paper theme verification | SIX-08 | Responsive and keyboard checks pass |
| SIX-13 | P1 | Graphiti compatibility spike | SIX-03 | Tenant, temporal and deletion checks pass |
| SIX-14 | P2 | Live calendar connection | SIX-04,08 | Authenticated scoped read works |
| SIX-15 | P2 | Voice and messaging channel | SIX-08 | Same task model through another channel |

## Cut order

Cut Graphiti first if explicit memory works. Cut live OAuth, voice, extra themes, and native computer use before cutting evidence, persistent memory or verified actions. If the browser spike fails, use the test-store API and state that route in the submission. Do not disguise a deterministic adapter as browser automation.

## Suggested calendar

October 16: compatibility gate, memory, ledger and first complete backend loop. October 17: conversational interface, correction/restart behavior and browser spike. October 18: verification, polish, deployment/local setup, video and submission. Reserve at least two hours before the deadline for upload and final review.

## After the event

Weeks 1-2: onboarding, reliable real calendar, deletion/account controls and small user pilot. Weeks 3-4: one additional domain skill and opt-in reminders. Later: messaging/voice, broader browser tasks and production permissions. Sequence by verified user demand rather than matching every Instinct example.
