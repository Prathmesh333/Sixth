# Product strategy and cost model

## Positioning

Sixth is a broad personal assistant with one recurring promise: it remembers the relevant context and carries a task forward. Instinct is a product-experience reference; the repositories are implementation references. We have not established that Sixth has unique market positioning or superior capability.

A chat interface lowers the need to learn another organizer. Memory inspection and source-backed actions give users a way to understand and correct the assistant.

## Starting audience and distribution hypotheses

Start with people who already use AI to organize plans but repeatedly paste the same preferences and context. Recruit a small pilot through the hackathon community and personal networks. Observe real tasks and correction behavior. These are proposed channels, not evidence of demand.

Measure weekly completed tasks, time to first useful outcome, repeat use, context repetition, action corrections and willingness to connect another service. Interview users who stop using it; an attractive demo does not establish retention.

## Packaging hypotheses

A free tier could offer manual chat, memory inspection and limited planning. A paid tier could add higher task budgets, connectors and scheduled follow-through. Household sharing is a later opt-in product with explicit memory permissions. Do not choose prices until execution cost and willingness to pay are measured.

## Cost model

For each task: input tokens / 1,000,000 * current input rate + output tokens / 1,000,000 * current output rate + embedding usage + browser runtime + connector fees + allocated storage/hosting.

No current vendor prices are assumed. Configure rates with provider/model/version and retrieval date. Record actual billable tokens, cache behavior, browser minutes and retries. Batch independent lookups and bound retrieved context to reduce repeated expense. A model list or README benchmark does not establish unit economics.

## Retention and trust

Memory must produce useful decisions, not merely personal-sounding responses. Ask permission for proactive behavior and keep notifications quiet unless useful. Let users inspect and forget context. Avoid storing more data solely to increase lock-in; export should remain possible.

## Expansion

After the dinner/calendar/cart loop, add gift preparation and travel planning through the same tool contracts. Add voice after text actions are reliable. Full native computer use, purchases and bookings need separate operational work. Prioritize a second skill that reuses the personal graph and proves breadth without adding another framework.

## Research to run

Five observed onboarding sessions, ten user-selected tasks, a seven-day follow-up, and a cost trace per task type. Report those as a small exploratory pilot, not statistical proof of market size or product superiority.
