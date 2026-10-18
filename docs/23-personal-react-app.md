# Sixth personal React app

Sixth uses its own React interface for Google sign-in, chat, memory, plans and friends. There are no password, phone-number or demo-code forms on the welcome screen. WhatsApp is an optional future channel.

## Working flows

- Continue with Google to create a personal account. Sixth assigns a friend username and takes a display name from the verified identity. The sign-in screen explains message storage and AI processing.
- Sign in again from another browser to retrieve that account's saved conversations and memories.
- Sign out to revoke the current server session.
- Send friend requests using exact usernames. Recipients can accept or decline; senders can cancel; either friend can remove the connection.
- Friendship alone exposes the display name and username. Each user can separately grant free/busy access or share selected memories. Tasks and conversations stay private.

User and friendship records live in the operational store, with random internal user IDs. Conversation, task and memory ownership uses those IDs. Google subject identifiers are hashed for identity lookup; Google credentials and client secrets are not stored. Google's official verifier checks signature, audience, issuer and expiry. Sixth additionally requires verified email and a single-use, expiring nonce bound to an HTTP-only browser cookie. Sessions use HTTP-only cookies, CSRF tokens, origin checks and server-side revocation. Authentication and friend-request attempts have persistent limits. Personalized API responses are marked no-store.

## Google setup

Create a Google OAuth Web application client, with `https://sixth-one.vercel.app` in Authorized JavaScript origins. Redirect URIs are not used by the JavaScript callback flow. Set `SIXTH_GOOGLE_CLIENT_ID` on the backend; no client secret is needed. Set `SIXTH_DEMO_LOGIN=false` for Google-only access. Local automated fixtures explicitly enable sample-account login; it has no welcome-screen UI. Include intended test accounts in Google Auth Platform's audience settings where required. Real browser login must be verified separately from mocked provider tests.

## Android path

Keep React components and the API contract reusable. A later Android release can package the interface with Capacitor or provide an Android-specific client against the same backend. That phase must implement and test its own origin, authentication, secure storage, navigation and notification behavior; the current same-origin cookie setup must not simply be assumed to work inside a native wrapper. An APK has not been built in this change.

## Preview boundaries

Use synthetic information for the hackathon. Account deletion, abuse reporting/blocking, direct friend messaging are not implemented. Selective memory sharing and internal availability are described below. Google manages sign-in and account recovery. Friend lists refresh when opened or after an action; they are not live subscriptions.

WhatsApp is removed from the signup screen and remains disabled as an optional connector. No Android packaging, app-store release, push notifications or offline storage is implied. Deployment still requires one API worker and one service instance. Before broader rollout, add recovery/deletion controls, stronger abuse controls and the remaining data-protection work documented in the hosting and WhatsApp notes.

## Checks

API tests with a mocked Google verifier cover durable identity, nonce matching, replay/expiry rejection, consent, invalid provider verification, logout revocation, owner isolation and recipient-controlled friendship. Browser checks cover the Google-only welcome page, accessibility, narrow layouts and the existing assistant workflow using a test-only API session. CI runs account tests against SQLite and PostgreSQL.

Identity verification follows [Google's server-side token guidance](https://developers.google.com/identity/gsi/web/guides/verify-google-id-token).

## Profile availability

Profiles now support status flags, busy slots, per-friend sharing, availability questions, and confirmed invitations. See [Profile availability](26-profile-availability.md) for the current flow and access rules.
