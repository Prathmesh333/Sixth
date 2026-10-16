# Security, privacy and user control

This document specifies engineering requirements for a personal assistant; it is not a legal compliance certification.

## Trust boundaries

User requests, trusted system policy, external documents, provider observations and model suggestions have different authority. A web page or receipt cannot grant permissions, select a tenant, change tools or authorize checkout. Keep instructions separate from retrieved data and enforce permissions in code.

## Isolation and credentials

Resolve graph and SQL ownership from authenticated identity. Check ownership on event streams, artifacts, plans and memory operations, not only chat endpoints. Use separate browser sessions per user/task and clear them according to session policy. Store provider credentials in encrypted server-side storage, never graph facts, prompts, browser-visible bundles or logs.

For the demo, authenticate two isolated fixture accounts or expose a single nonpublic local account. A public demo must not accept arbitrary user identity through a query parameter. Production auth is a separate implementation gate.

## Action policy

Read-only lookups may run within granted scopes. Internal plan edits follow user intent and can be undone. Review external writes by default during the hackathon. Purchases, bookings, sending communications and destructive actions require a preview of the exact effect. Bind decisions to action fingerprint, current evidence and expiry. Never store card details in memory.

## Memory control

Show what is remembered, who it concerns, sources, dates and confirmation status. Support correction, export, source deletion and account deletion. Avoid promoting sensitive inferred attributes into durable memory automatically. Explicit user preferences and observed account state remain distinct.

## Deletion implementation

Immediately tombstone requested items and block retrieval. Queue cleanup for graph nodes/edges, source artifacts, embeddings, prompt caches, derived summaries and checkpoint content. Invalidate affected plan decisions. Track provider-side deletion limits separately; Sixth cannot retract data already sent to an external provider by merely deleting its own graph.

Proposed operational policy: ordinary raw execution artifacts expire after seven days unless retained by the user; task metadata without personal content may last longer for debugging; account backup retention is at most thirty days. These are proposed defaults requiring implementation and disclosure, not existing guarantees. Restores must replay tombstones before serving requests. Give users a deletion status and explain backup expiry.

## Browser worker

Use a dedicated container/process, outbound domain restrictions, limited downloads and no access to the full host filesystem. Validate URLs and block internal-network destinations unless specifically required by the test environment. Restrict artifact sizes and redact screenshots where practical. Authentication challenges return a user-action state instead of repeated blind retries.

## Abuse and operational controls

Set per-user budgets and rate limits. Redact secrets, personal source text and private chain-of-thought from telemetry. Keep a minimal audit trail of tool, target, reviewed action and verified outcome. Pin dependencies, scan incorporated packages and review license files before distributing a derivative.

## Required negative tests

A malicious recipe page requests memory export; a forged source names another tenant; a stale approval targets a revised cart; a reconnect requests another user's SSE stream; a deleted fact appears in a checkpoint; and a timed-out checkout is replayed. Each must fail safely with an accurate status.
