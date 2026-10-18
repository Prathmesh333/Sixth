# Profile availability and invitations

Sixth stores availability and invitations in the operational database: PostgreSQL in the hosted app, or SQLite locally. FalkorDB stores personal memories. No external calendar connection is required.

## Set your availability

1. Open **Availability**.
2. Select **Available**, **Busy**, **Away**, or **Not set**.
3. If necessary, enter an expiry time.
4. Select **Update status**.

After the expiry time, the flag becomes unknown. Expiry is calculated when the server reads the status. It does not require a background job.

To reserve a period, enter a title, start time, and end time. Select **Save my busy slot**. The form shows the timezone used for these times.

## Share with a friend

1. Add a friend by their Sixth username.
2. Wait for the friend to accept.
3. Open **Friends**, then **Manage sharing**.
4. Select the free/busy checkbox or specific memories.
5. Select **Save sharing**.

Sharing is off by default. Free/busy results include status and busy time ranges. They exclude private slot titles. Selected memories include fact values, without source excerpts or chat access. Removing the friendship removes access. Forgotten memories are no longer returned.

## Ask, invite, and book

1. Open **Availability**.
2. Enter the proposed start and end times.
3. Select one or more accepted friends.
4. Select **Check availability**, **Ask if available**, or **Send invitation**.

A question lets each recipient answer for that period. The answer does not enable ongoing sharing and does not create a booking.

For an invitation, every recipient must accept. The organizer then selects **Confirm booking**. Sixth checks every participant for conflicts again. It saves all participant slots in one database transaction. If a conflict exists, it saves no booking slots. The organizer can cancel the meeting for everyone.

The inbox refreshes every 20 seconds while this page is visible. Select **Refresh inbox** for an immediate check.

## Ask the AI

With a model configured, try these requests:

- `Set my profile status to busy until 3 PM today.`
- `Save a busy slot tomorrow from 1 PM to 3 PM.`
- `Check whether Jules is available tomorrow from 2 PM to 3 PM.`
- `Ask Jules if they are available tomorrow from 2 PM to 3 PM.`
- `Invite Jules for tea tomorrow from 4 PM to 5 PM.`
- `Show my invitations.`
- `Accept the tea invitation.`
- `Confirm the tea meeting booking.`

The AI reads your saved slots, accepted friend names, request states, and memories explicitly shared with you. Read operations do not change records. Before a write, Sixth shows an approval card with the proposed action and exact times. Missing details require clarification. Each invitee answers for themselves.

Unknown availability means the friend has not granted access. **No recorded conflict** means Sixth found no saved busy slot or blocking flag. It does not guarantee the person is available.

## API and storage

- `GET/PUT /v1/availability`: profile status and optional expiry.
- `GET/POST /v1/calendar/events`: internal busy slots.
- `PUT /v1/friends/{id}/sharing`: per-friend permissions.
- `GET /v1/friends/{id}/context`: permitted shared facts.
- `GET /v1/friends/{id}/availability`: status for a time range.
- `GET /v1/scheduling/inbox`: requests that include the signed-in user.
- `POST /v1/scheduling/{kind}`: a meeting or availability request.
- `POST /v1/scheduling/{kind}/{id}/respond`: the recipient's answer.
- `POST /v1/scheduling/meeting/{id}/confirm`: the organizer's final booking.
- `POST /v1/scheduling/meeting/{id}/cancel`: cancellation for all participants.

Writes require the existing session, origin check, and CSRF token. Request creation, responses, and confirmation also require an idempotency key. PostgreSQL transactions use the existing advisory lock to serialize conflict checks and booking writes.

## Interrupted requests

An active worker renews a 90-second database lease. A recovery check runs every 15 seconds. If a worker stops during a deployment, the replacement worker resumes queued or running tasks after the lease expires. Requests awaiting user approval remain paused. Stable action IDs prevent repeated slot creation when an approved action resumes.
