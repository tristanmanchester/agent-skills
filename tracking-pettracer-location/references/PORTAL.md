# Unofficial portal contract and streaming boundary

The endpoint/field evidence below comes from the inspected repository implementation,
not a current public PetTracer developer specification. Review date 2026-09-13.
The official product/help sites were searched; no supported replacement CLI/API
was established. This is not proof no private partner API exists.

## Bounded snapshot/history helper

The inherited portal origin is `https://portal.pettracer.com/api`:

- POST /user/login with login/password; accept only the expected access_token.
- GET /map/getccs returns an account device array.
- POST /map/getccpositions with devId, filterTime, toTime returns history; timestamps
  in the request are epoch milliseconds.

These are the helper's only operations. History uses POST for a read; no device
configuration, delete, mode-change, or arbitrary raw-request operation is exposed.
The credential-bearing origin is fixed, redirects refused, bodies bounded, and
errors omit raw server bodies. If the vendor changes hosts/auth, deliberately review
the new contract; do not solve it by sending credentials to a caller-supplied URL.

An explicit selected ID must occur exactly once in the account inventory. Observed
type1 is a HomeStation, type0 a collar. Missing type is surfaced as unverified;
unknown types fail. Verify identity in the official UI before relying on it. The
helper never substitutes top-level HomeStation coordinates for a missing lastPos.

Only timezone-aware timeMeasure establishes measurement time. timeDb is retained
separately. Unknown/future measurement timestamps do not pass freshness. Latitude
and longitude must be finite and in geographic range; quality metadata must not
be converted to metres, percent, or confidence without a verified vendor contract.

## Live protocol investigation

The old implementation records a SockJS/STOMP endpoint rooted at
`wss://pt.pettracer.com/sc`, with server/session path segments and a token in the
query string. It sends STOMP CONNECT after SockJS open, waits for CONNECTED,
subscribes to /user/queue/messages and /user/queue/portal, then sends deviceIds to
/app/subscribe. These are **inherited observations**, not a freshly verified
protocol or an endorsement to connect without account authorisation.

A new live implementation must verify that handshake against the authorised current
portal, keep query tokens out of logs/traces, validate the TLS origin and selected
account device IDs, and bound session duration, frame sizes, reconnect attempts,
and backoff. Parse complete SockJS and STOMP frames, including content-length,
heartbeat, error, disconnect, and partial-message behaviour. Check device identity
for every update, not just at subscription time.

Use actual measurement timestamps to reject stale regressions; receive time is
not fix time. Preserve unknown updates without guessing a location shape. Close
subscriptions, sockets, and clients on timeout/cancellation. Reconnecting must not
implicitly enable live search or increase the collar's GPS rate. Test loss/reorder,
expired tokens, wrong device, no-new-fix, and teardown before claiming live support.
Until that integration is verified, use the maintained official app for live search.

## Scope of verification

The bundled tests establish local data/transport rules only. They do not establish
live login success, subscription entitlement, vendor field units, GPS accuracy,
history completeness, radio coverage, or mode/battery behaviour. A fresh retrieval
is evidence of a retrieved record, not a new satellite measurement.

Official user-facing entry points:
- https://pettracer.com/
- https://help.pettracer.com/
