# track17

A shell-agent skill for 17TRACK parcel registration, polling, delivery-event inspection, and authenticated webhook ingestion. Start with [SKILL.md](SKILL.md).

Requires Python 3.10+, `TRACK17_TOKEN`, and an explicit absolute `TRACK17_DATA_DIR`. No runtime packages are required. API calls are made only by commands that need provider access; the test suite uses synthetic inputs and a loopback HTTP server.

## Revision 2

This revision removes optional authentication, success-before-persistence acknowledgements, implicit workspace storage discovery, local numeric-ID addressing, and the unsafe deferred inbox spooler. Webhooks are verified against the raw body and API key, deduplicated, and applied atomically before acknowledgement. Failed requests never count as successful syncs.

Storage uses a new schema. Old databases are detected and left unchanged; there is no automatic migration or silent reuse. Select a new data directory and deliberately re-register parcels still needed. Keep old data until you have exported and checked it.

The API remains v2.2 because 17TRACK explicitly supports it. The new v2.4 additional-field contract is not implemented by changing an endpoint string.

## Validation

```bash
python3 -m unittest discover -s /absolute/path/to/track17/tests -v
```

Tests cover exact-byte signatures, invalid/missing authentication with no table changes, duplicate deliveries, transaction rollback, stale updates, malformed records, unconfirmed provider mutations, old-database preservation, HTTP authentication, and storage-failure responses. They do not establish live carrier/API availability or validate a production reverse proxy.
