---
name: track17
description: Register and track parcels with the 17TRACK API, inspect saved delivery events, and ingest authenticated 17TRACK webhooks. Use when the user asks to manage their 17TRACK parcels, not for generic shipment guesses or other tracking providers.
compatibility: Python 3.10+, TRACK17_TOKEN, and an explicit private absolute TRACK17_DATA_DIR. No third-party Python packages required.
metadata:
  version: "2.0.0"
  reviewed: "2026-09-13"
---

# Track parcels with 17TRACK

Resolve `SKILL_DIR` to this skill's installation directory. Use the bundled CLI rather than recreating storage or signature handling. Commands return JSON; non-zero exit status means failure or an incomplete sync.

## Setup

Set `TRACK17_TOKEN` through the host's secret store/environment; never print it. Set `TRACK17_DATA_DIR` to a private absolute directory outside the repository. Then run:

```bash
python3 "$SKILL_DIR/scripts/track17.py" init
python3 "$SKILL_DIR/scripts/track17.py" --help
```

This revision uses a new local schema. An old database containing `packages` is rejected without modification. Choose a new data directory, inspect/export the old records locally, and register only the parcels the user still wants. Do not delete the old database or automatically re-register everything: provider quota can be consumed.

## Normal workflow

Prefer polling unless push delivery is needed. Read the current parcel list before adding or removing anything. Resolve parcel identity by **tracking number plus carrier code**, not a guessed local ID.

```bash
python3 "$SKILL_DIR/scripts/track17.py" list
python3 "$SKILL_DIR/scripts/track17.py" carriers-search DHL
python3 "$SKILL_DIR/scripts/track17.py" add RR123456789CN --label "Headphones"
python3 "$SKILL_DIR/scripts/track17.py" sync
python3 "$SKILL_DIR/scripts/track17.py" status RR123456789CN --carrier 3011 --refresh
python3 "$SKILL_DIR/scripts/track17.py" quota
```

Carrier numbers above are examples, not universal defaults. Use `--carrier` when automatic detection cannot resolve the carrier; use `--param` only when that carrier requires additional information. Registration success does not imply that tracking events are already available.

`stop`, `retrack`, and `remove` require the tracking number and `--carrier`. `remove` is local unless `--delete-remote` is explicitly supplied. Clarify remote deletion before executing it. After an ambiguous network failure, reconcile provider state before retrying a mutation; the client does not replay writes automatically.

## Authenticated webhooks

17TRACK signs the **original body bytes** followed by `/` and the API security key with SHA-256. The signature arrives in the `sign` header. The helper uses `TRACK17_TOKEN` as that key; never invent a separate unrelated webhook secret or substitute HMAC for the provider's algorithm.

For captured deliveries, preserve the body unchanged and supply its real signature:

```bash
python3 "$SKILL_DIR/scripts/track17.py" ingest-webhook --file delivery.json --signature "$DELIVERY_SIGN"
```

For push delivery:

```bash
python3 "$SKILL_DIR/scripts/track17.py" webhook-server --port 8789
```

The receiver binds to loopback. Put an intentionally configured TLS reverse proxy in front of it, preserving `sign` and the raw body. Do not expose a development server casually. Missing, invalid, or duplicate authentication headers fail; accepted delivery is acknowledged only after the database transaction commits. Storage failures return a failure response so the provider can retry. There is no unsigned import path or deferred inbox processor.

Identical deliveries are idempotent. Older dated updates cannot overwrite a newer dated snapshot. This is not universal ordering: timestamps do not resolve same-time corrections or prove the freshness of undated updates. Report event time separately from local receipt time.

## Report

Prioritise delivered, out-for-delivery, pickup, failed delivery, and exceptions. Include the carrier, event time, and last successful refresh; distinguish saved state from a fresh provider response. Treat partial syncs and missing events as incomplete evidence, not “no changes”. Never infer a delivery date from an unrelated parcel or a stale snapshot.

## Sources and checks

[17TRACK API documentation](https://api.17track.net/en/doc), reviewed 2026-09-13, documents the signing scheme and explicitly keeps v2.2 online. This helper deliberately retains that supported response contract; v2.4 is not a drop-in version-string change because additional registration fields differ.

Run offline and loopback HTTP regressions:

```bash
python3 -m unittest discover -s "$SKILL_DIR/tests" -v
```
