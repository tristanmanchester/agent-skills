## Draft

`getEvents` gets events. It has parameters and returns things.

## Release 1.8 contract

Signature: `getEvents(limit: number = 50, cursor?: string): EventPage`
Returns events visible to the caller, oldest first. `limit` must be an integer from 1 to 100; its default is 50. `cursor` retrieves the next page. The return value is `EventPage`. The caller needs `events:read`. No behavior for explicit null, invalid cursors, retry policy, or error codes is supplied.
