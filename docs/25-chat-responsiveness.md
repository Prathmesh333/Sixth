# Chat updates and model responses

## Message updates

Sixth shows a user message before the server accepts the request. The server returns the stored message ID. The interface keeps the same message element when it replaces the temporary ID.

The interface starts the task event stream after acceptance. It does not reload status, conversations, memories, and plans before listening for the reply. When the task ends, the interface updates the current conversation. Memory and plan records refresh when the task contains those results.

An interrupted event stream triggers a task-state check. Replayed review events do not end a cart operation that is currently running. If a reply is delayed, the interface continues checking the task without clearing the conversation.

New messages and plan cards use short entrance animations. A thinking indicator shows pending work. Automatic scrolling follows new content when the reader is near the bottom. Reading older messages stops automatic following. Reduced-motion mode removes the spatial animations.

## Model context and output

The hosted provider is Groq with `openai/gpt-oss-20b`. Each model request includes the current message, up to twelve earlier messages from the same conversation, and bounded saved personal context for that owner.

The GPT-OSS request uses a strict JSON schema and low reasoning effort. The system prompt and assistant-history examples use the same response structure. General requests return a conversational answer in the `response` field. Typed workflow code still controls memory writes, plans, and cart approval.

Provider rate limits, rejected credentials, timeouts, truncated output, and unreadable responses have separate messages. The application does not show raw provider diagnostics or credentials.

## Verification

- Thirty local API, account, connector, and model-context tests passed.
- Both browser workflows passed, including cart approval, accessibility, and responsive layouts.
- Browser assertions verified that a user message appears before the POST completes, earlier message elements remain mounted, and sending messages causes no document navigation or repeated status request.
- Browser assertions checked normal motion and reduced-motion behavior.
- Live Groq probes returned a greeting and a contextual tea suggestion in approximately 1.4 and 0.9 seconds. These provider-call timings do not measure the complete hosted application request.
- The [backend CI run](https://github.com/Prathmesh333/Sixth/actions/runs/39107694979) passed application, PostgreSQL, real graph, and container jobs.

The app streams workflow events. Model response text appears when the structured response is complete; it is not streamed token by token.
