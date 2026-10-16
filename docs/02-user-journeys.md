# User journeys and acceptance criteria

## First conversation

The user shares preferences in ordinary language. Sixth proposes a compact memory card: who the fact concerns, what was said, and where it came from. Explicit instructions can become confirmed facts; uncertain extraction stays proposed. The user can edit it immediately.

Acceptance: "Maya is vegetarian" attaches to Maya, not the user; two people named Maya remain separate until disambiguated. The original message remains the evidence.

## Birthday dinner

1. User requests dinner planning for Maya on October 17, 2026 at 19:00 Asia/Calcutta.
2. Sixth resolves Maya's identity and retrieves current preferences, guest count, pantry and calendar availability.
3. It offers a menu and a shopping preview with missing quantities.
4. User reviews the cart mutation in the test store.
5. Tool execution returns cart ID, contents, revision, and simulation status.
6. Sixth verifies the cart and reports the actual completed work.

Acceptance: vegetarian constraints affect recipe selection; pantry quantities reduce shopping quantities; missing information is asked once in context. A birthday date and a dinner reservation are different facts.

## A new constraint

"Two more people are joining and Maya now avoids dairy." Sixth confirms whether the dairy preference is ongoing or just for this meal. A new assertion supersedes the appropriate earlier fact. It revises recipes, servings and cart quantities. Previously reviewed cart arguments cannot silently authorize different ones.

Acceptance: explain the changed ingredients using the new assertion's source. Do not erase historical preferences needed to explain the old plan.

## Return tomorrow

A new conversation asks what remains for dinner. Sixth retrieves the persisted plan and verified cart state. If it needs live data, it refreshes the connector instead of treating old observations as current.

Acceptance: this succeeds after the backend process restarts and the previous transcript is absent from model input. It does not rebuild or duplicate the cart.

## Cancel, deny, and forget

A user can stop execution between steps, reject a proposed action, or forget Maya's preference. Stop prevents new actions; an in-flight irreversible request may require reconciliation. Rejection is stored as a decision scoped to the plan, not automatically as a permanent preference. Forget removes retrievable assertions, projections, indexes and affected caches.

Acceptance: there is a visible terminal or pending-reconciliation status. A deleted fact cannot be retrieved from a new session, and dependent plans become stale when appropriate.

## Extending to travel

A later travel skill uses the same people, preferences, constraints, action ledger and evidence model. New domain entities can be added without a separate memory system. Travel booking remains a planned capability until a real connector and verification path exist.
