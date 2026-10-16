# Product requirements

## Purpose and audience

Sixth helps an individual delegate everyday tasks without repeatedly explaining their circumstances. Start with students and working adults who organize their own calendars, meals, purchases, travel, and social commitments. Audience demand and willingness to pay remain hypotheses to validate.

The experience is conversational. Supporting views explain actions and memory; users should not need to maintain a knowledge graph manually.

## Product loop

Capture a request, retrieve relevant context, propose a plan, perform permitted actions, verify results, and remember useful outcomes. A failed step must leave an accurate partial result and a recoverable task.

## Scope

| Area | Hackathon requirement | Later product |
|---|---|---|
| Conversation | Text, streaming progress, interruption | Voice and messaging channels |
| Personal memory | People, preferences, events, sources; correction and deletion | Richer document extraction and import |
| Scheduling | Fixture calendar read; optional real provider after setup | Calendar writes and conflict resolution |
| Planning | Recipes and ingredient quantities with structured constraints | Travel, gifts, learning, household skills |
| Shopping | Build and revise cart in test storefront | Merchant integrations and reviewed checkout |
| Actions | Review cards, status, verification, retry handling | Broader delegated permissions |
| Proactivity | Manual "what changed?" replan | Opt-in event-triggered reminders |
| Identity | Two isolated demo users, backend-owned identity | Production account and recovery system |

## Functional requirements

- FR1: Every request belongs to one authenticated user and conversation.
- FR2: Memory retrieval returns fact IDs, sources, scope, status, and relevant dates.
- FR3: Personal assertions distinguish user statements, connector observations, and model hypotheses.
- FR4: Plans contain typed steps, prerequisites, tool names, expected results, and revision numbers.
- FR5: Changes invalidate affected downstream steps and stale action approvals.
- FR6: An action is successful only when a tool observation confirms its intended effect.
- FR7: A new conversation can retrieve durable facts without loading the prior transcript.
- FR8: Users can inspect, edit, export, or delete personal memory and see deletion progress.
- FR9: Calendar, meal, and cart skills operate through the same tool and task interfaces.
- FR10: Simulation is visible on each simulated tool result and final answer.

## Acceptance targets

All are proposed targets, not measured performance: first progress event within two seconds excluding cold start; relevant evidence visible for every personalized decision in the demo suite; zero duplicate side effects in restart tests; zero cross-user results in isolation tests; all required fixture constraints satisfied. Measure full task latency and spend rather than promising a fixed response time.

## Explicit exclusions for the event

No universal mobile or desktop control, autonomous checkout, phone calling, production payment collection, full inbox ingestion, or unrestricted code execution. These exclusions bound implementation effort while preserving a broad skill architecture.

## Product success

Count tasks with independently verified outcomes, user corrections required, repeated context requests, resumed tasks completed, and facts successfully forgotten. A high count of stored memories or tool calls is not a user outcome.
