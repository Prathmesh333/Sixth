# Interface, brand and themes

## Product voice

Name: Sixth. Tagline: "Your sixth sense for everyday life." Describe it as a personal assistant that remembers context and helps act on it. Naming is a working product decision; domain and trademark availability have not been checked.

Use short, concrete updates: "I found a conflict at 7 pm," "Your test cart is ready," or "I need to know which Maya you mean." Avoid implying mind reading, guaranteed outcomes, or completed purchases without evidence.

## Interaction model

Conversation is the primary surface. A small sidebar holds recent conversations, Plans, Memory and Settings. The central transcript contains expandable action cards. A contextual side panel shows evidence, plan steps or a browser preview only when needed. On mobile, use sheets and full-screen detail views instead of three squeezed columns.

| Surface | Required contents |
|---|---|
| Welcome | One composer, useful examples, honest connection state |
| Conversation | Messages, progress, stop control, tool outcomes |
| Action review | Exact target, arguments, effects, mode and approve/reject |
| Plans | Current revision, completed steps, unresolved dependencies |
| Memory | Subject, assertion, source, effective dates, edit/forget |
| Connections | Provider, scopes, availability, disconnect |
| Evidence | Plain-language reasons, source snippets, optional graph |

The graph is an explanation view. Always provide a keyboard-accessible list of the same entities and connections. It should answer "why this choice?" without becoming a dashboard users must learn.

## Three original themes

| Theme | Character | Main colors | Recommendation |
|---|---|---|---|
| Dusk | Calm dark canvas with soft periwinkle emphasis | Ink, slate, pale violet | Default demo theme |
| Paper | Warm light canvas with restrained indigo | Warm white, charcoal, deep indigo | Daytime alternative |
| Grove | Dark neutral canvas with muted mint | Deep green-gray, off-white, mint | Optional preference |

These are Sixth designs. [LobeHub's token model](research/repositories/lobehub--lobe-chat.md) informs semantic naming, not copying its assets or values. [assistant-ui](research/repositories/assistant-ui--assistant-ui.md) is a candidate primitive layer; its adapter and styles must be tested before adoption.

## Theme implementation

[themes.css](../design/themes.css) defines variables under `data-theme`. [tokens.json](../design/tokens.json) stores corresponding values and spacing/type scales. Components consume surface, text, muted, border, accent, focus, success, warning and danger roles. Persist a user preference and support system appearance when no preference exists.

Use system sans-serif initially, with 16px body text, 1.5 line height, 12/14px metadata only where readable, a 4px spacing scale and 12px card corners. Favor modest borders over stacked glowing surfaces. A proposed icon is six offset points forming a subtle directional ring; create original assets later.

## States and accessibility

Design empty, loading, disconnected, expired, denied, failed, partial, reconciling and completed states. Simulation labels remain visible in every theme. Color never carries status alone. Provide visible focus, labels for icon buttons, reduced-motion support, and touch targets of at least 44px for primary mobile controls.

Validate WCAG AA contrast in the implementation, including muted text and focus indicators on every surface. The documentation validator checks the supplied token pairs mathematically; that does not certify the rendered interface. Announce concise task-state changes through a polite live region and avoid reading every token aloud.

## Motion

Use 120-180ms opacity/position changes for new cards, disable movement under reduced motion, and keep an active stop button reachable. Show tool progress as real execution states rather than artificial typing delays.
