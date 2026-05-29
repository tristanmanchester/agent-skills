# Contacts, broadcasts, and subscriptions

## Prefer Segments over Audiences

Resend still exposes Audiences in the stable API, but the docs and schema mark them as deprecated.
For new work, prefer:

- Contacts
- Contact Properties
- Topics
- Segments
- Broadcasts

## Contacts

Stable contact endpoints:

- `POST /contacts`
- `GET /contacts`
- `GET /contacts/{id}`
- `PATCH /contacts/{id}`
- `DELETE /contacts/{id}`
- `GET /contacts/{contact_id}/segments`
- `POST /contacts/{contact_id}/segments/{segment_id}`
- `DELETE /contacts/{contact_id}/segments/{segment_id}`
- `GET /contacts/{contact_id}/topics`
- `PATCH /contacts/{contact_id}/topics`

Notable contact fields:

- `email` — required on create
- `first_name`
- `last_name`
- `unsubscribed` — global opt-out across broadcasts
- `properties` — custom key/value map
- `segments` — initial segment IDs to attach
- `topics` — per-topic opt-in/opt-out array

`GET /contacts/{id}` can retrieve by contact ID or email, which is handy in support or debugging
flows.

## Contact Properties

Use Contact Properties to define typed profile fields before relying on them in filters or
broadcast logic.

Stable endpoints:

- `POST /contact-properties`
- `GET /contact-properties`
- `GET /contact-properties/{id}`
- `PATCH /contact-properties/{id}`
- `DELETE /contact-properties/{id}`

Rules from the stable schema:

- `key` max length: 50
- key characters: alphanumeric or underscore
- `type`: `string` or `number`
- `fallback_value` must match the declared type

## Topics

Topics control subscription semantics and unsubscribe-page visibility.

Stable endpoints:

- `POST /topics`
- `GET /topics`
- `GET /topics/{id}`
- `PATCH /topics/{id}`
- `DELETE /topics/{id}`

Topic creation fields:

- `name` — required, max 50 chars
- `default_subscription` — required, `opt_in` or `opt_out`
- `description` — optional, max 200 chars
- `visibility` — `public` or `private`, default `private`

Important note: `default_subscription` cannot be changed after creation.

## Segments

Segments describe a filtered group of contacts and are the preferred broadcast target.

Stable endpoints:

- `POST /segments`
- `GET /segments`
- `GET /segments/{id}`
- `DELETE /segments/{id}`

Create fields:

- `name` — required
- `filter` — object representing the segment conditions
- `audience_id` — deprecated

Use segments for marketing/newsletter cohorts, lifecycle buckets, or property-based recipient groups.

## Broadcasts

Broadcasts are the campaign layer on top of Contacts/Segments/Topics.

Stable endpoints:

- `POST /broadcasts`
- `GET /broadcasts`
- `GET /broadcasts/{id}`
- `PATCH /broadcasts/{id}`
- `DELETE /broadcasts/{id}`
- `POST /broadcasts/{id}/send`

Important request fields:

- `segment_id` — required for new work
- `from` — required
- `subject` — required
- `html` / `text`
- `reply_to`
- `preview_text`
- `topic_id`
- `send`
- `scheduled_at`

Useful patterns:

- create a draft broadcast with `send: false`
- review or patch it
- call `/broadcasts/{id}/send` when ready

Deletion rule from the stable endpoint summary: only broadcasts still in **draft** status are
expected to be removable.

## Subscription model guidance

Use the right layer for the right purpose:

- **Global unsubscribe** → contact-level `unsubscribed`
- **Category/topic consent** → contact topic subscriptions
- **Campaign audience** → segments
- **Profile data** → contact properties

When the user describes “newsletter preferences”, “marketing categories”, or “product update opt-in”,
that is usually a Topics + Contacts + Broadcasts design, not a transactional send design.

## Minimal example flow

1. create a Topic for “product-updates”
2. create a Contact Property such as `plan_tier`
3. create/update Contacts with properties and topic subscriptions
4. create a Segment filtered on the contact data
5. create a Broadcast to the Segment, optionally scoped to the Topic
6. send immediately or schedule it

## Useful assets

- `assets/create-contact.json`
- `assets/create-broadcast.json`
