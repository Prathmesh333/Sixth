# WhatsApp Business test integration

October 17, 2026. Implementation is prepared for limited test recipients. Meta account setup and actual provider delivery are not yet verified. Live sending defaults to disabled. This does not establish eligibility for a public general-purpose assistant rollout.

## User flow

The welcome screen presents Connect your WhatsApp and a separate private web-demo section. Until configured, the WhatsApp form is disabled and identifies setup as pending.

An allowed test recipient enters an international phone number and explicitly agrees to message storage/processing. The backend issues an expiring connection code and a separate HttpOnly browser secret. The browser opens a `wa.me` message addressed to Sixth. Sending that message from the entered number proves phone possession through Meta's signed webhook.

The browser polls for confirmation using its separate secret, then receives an account session and CSRF token. The code visible in WhatsApp cannot authenticate another browser. A mistyped number or message from a different sender cannot establish the connection. WhatsApp accounts have independent owner IDs and do not inherit the shared Alex/Jordan demo accounts.

Messages sent to Sixth become durable operational conversations and tasks through the same submission function as web chat. The existing agent extracts sourced facts into the account's configured memory backend. Replies return through a durable outbox. Dinner/cart actions require review through the existing web approval UI; WhatsApp text never bypasses that review. Media, voice, templates, proactive reminders and WhatsApp-native approval buttons are not implemented.

## Server environment

Keep both switches false while preparing:

```env
SIXTH_WHATSAPP_ENABLED=false
SIXTH_WHATSAPP_SEND_ENABLED=false
SIXTH_PUBLIC_URL=https://sixth-one.vercel.app
```

Configure these secrets directly in Render:

| Variable | Source |
|---|---|
| `SIXTH_WHATSAPP_APP_SECRET` | Meta developer app settings |
| `SIXTH_WHATSAPP_VERIFY_TOKEN` | A new random server secret; same value used in Meta's webhook form |
| `SIXTH_WHATSAPP_IDENTITY_SECRET` | A separate stable random secret, used for private identity mapping and connection hashes |
| `SIXTH_WHATSAPP_ENCRYPTION_KEY` | A Fernet key generated with the installed cryptography package |
| `SIXTH_WHATSAPP_PHONE_NUMBER_ID` | Phone Number ID from Meta's WhatsApp API setup |
| `SIXTH_WHATSAPP_BUSINESS_NUMBER` | The test business number, international digits only |
| `SIXTH_WHATSAPP_ALLOWED_NUMBERS` | JSON array of international digit strings; only approved test recipients |
| `SIXTH_WHATSAPP_ACCESS_TOKEN` | Meta token authorized for the configured business number |
| `SIXTH_WHATSAPP_API_VERSION` | An explicit version supported by the Meta app, such as the version displayed in API Setup |

Never put these secrets in Vercel frontend variables or Git. Identity/encryption-key changes need a migration and recovery plan: changing the Meta app secret alone does not change account IDs.

## Meta setup

1. Create/sign in to a Meta developer account. The account owner completes identity verification, security checks and agreement acceptance.
2. Create an appropriate app and add the WhatsApp use case/product where available. Start with Meta's test business number and approved test recipients. Do not add billing or activate public production traffic for this test.
3. Configure the settings above. Set `SIXTH_WHATSAPP_ENABLED=true`, retaining `SIXTH_WHATSAPP_SEND_ENABLED=false`, and redeploy.
4. Set callback URL to `https://sixth-api.onrender.com/webhooks/whatsapp` and enter the matching verify token. Subscribe to incoming messages.
5. Confirm Meta can verify the callback and that a real signed message is ingested. Confirm linking from the same number and rejection of a different sender.
6. After account eligibility, permissions and applicable pricing are checked, explicitly enable `SIXTH_WHATSAPP_SEND_ENABLED=true` for the allowlisted test recipients. Verify one real provider response and its delivery before claiming the integration works.

Provider interfaces and supported API versions must be checked in the configured Meta account. Public documentation was partly inaccessible during development; mocked API tests do not establish actual Meta delivery or account approval. The current official reference collection is [Meta's WhatsApp Business Platform workspace](https://www.postman.com/meta/whatsapp-business-platform/overview).

## Security and persistence

The webhook verifies HMAC-SHA256 over the raw body with the Meta app secret, limits payload size, checks business phone ID, filters test recipients and deduplicates provider message IDs. Acknowledgement persists the inbox; model calls happen in the worker, not the webhook handler. Incoming phone/text envelopes and outgoing reply envelopes are encrypted with Fernet. Phone lookup IDs use a separate HMAC identity secret.

Once ingested, conversation/task text and selected sourced graph assertions follow Sixth's existing storage path; those fields are not application-level encrypted by this connector. Database/storage-provider encryption and access controls are separate. Do not present this as end-to-end encryption against the Sixth server. WhatsApp grants no access to unrelated personal chats, device activity or contacts.

The worker uses the existing PostgreSQL/SQLite owned record store. Restart recovery preserves queued tasks, replies and deduplication. A response left in sending state is marked uncertain on restart; timeouts and 5xx responses are not blindly retried. Explicit rate-limit responses receive bounded retries. Replies older than a conservative 23-hour boundary from the inbound message timestamp expire rather than sending a non-template message outside the implemented window. A successful send records Meta's returned message ID; it is not a delivered/read receipt. Delivery-event reconciliation remains future work.

Deploy exactly one API worker and one service instance. This implementation does not provide distributed task leases. Free Render sleep can delay replies. Full account deletion, inbox retention cleanup, key rotation, recovery tooling and production privacy controls remain rollout work. The public test allowlist is deliberately required before enabling the channel.

## Verification

Automated tests cover callback verification, invalid signatures, mismatched phone possession, browser-secret separation, link expiry, anonymous rate limits, durable deduplication, encrypted channel records, separate owner memory, disabled sending, stale reply expiry and uncertainty without unsafe retries. Both local and PostgreSQL CI suites exercise the integration. The existing browser demo remains available while Meta setup is pending.
