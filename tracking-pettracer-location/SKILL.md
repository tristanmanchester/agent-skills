---
name: tracking-pettracer-location
description: >-
  Retrieve and interpret an authorised owner's PetTracer collar inventory, latest
  known GPS fix, or bounded location history. Use for explicit PetTracer work,
  not generic pet questions or tracking a person. Distinguish measurement time,
  contact time, missing data, and stale fixes.
compatibility: Optional Python 3.10+ standard-library helper uses the unofficial PetTracer portal protocol. It requires authorised credentials for live reads; vendor API stability and current field semantics are not guaranteed.
metadata:
  version: "1.0.0"
  reviewed: "2026-09-13"
---

# PetTracer location evidence

Keep this skill: it solves a specific owner's lookup task. No current official
public developer API or replacement CLI was established during this review. The
portal helper is therefore explicitly unofficial, not a vendor-supported client
or a guarantee of live tracking. Prefer the official app/portal when its behaviour
or the account contract differs.

## Establish the target and permission

Use only an account/collar the user owns or is authorised to inspect. Confirm the
actual device ID against the account inventory and official app before interpreting
coordinates as the pet's location. A HomeStation's configured position is not a
collar GPS fix. An absent device-type field remains unverified; do not infer type
from an arbitrary name or the first item in a response.

Resolve SKILL_DIR to this installed skill directory. Set PETTRACER_TOKEN privately,
or PETTRACER_USERNAME and PETTRACER_PASSWORD for an authorised login. Never ask for
credentials in chat or pass them in command arguments. The helper does not store
or print tokens and does not accept arbitrary API origins or credential redirects.

```bash
python "$SKILL_DIR/scripts/pettracer.py" list
python "$SKILL_DIR/scripts/pettracer.py" locate --device-id 12345 --max-age-seconds 900
```

Replace the sample ID with the verified collar ID. The 900-second default is a
local reporting threshold, not a manufacturer guarantee or the right threshold
for every tracking mode. `recent` means the supplied measurement timestamp passes
that chosen threshold; it does not mean the pet has stayed at those coordinates.

## Read timestamps literally

Use only `timeMeasure` to compute fix age. Keep `timeDb` and `lastContact` separate;
new database activity/contact cannot make an old position fresh. Reject timezone-
less dates rather than silently calling them UTC. Unknown times and future times
are explicit states, never fresh by default. Display the actual fix time/timezone
and age alongside retrieval time.

The helper validates finite latitude/longitude ranges and preserves zero values.
It does not estimate a battery percentage or convert raw signal/accuracy fields
without a verified calibration/units contract. `acc` and `horiPrec` remain separate
raw quality fields with unverified units; do not call either a metre-radius merely
because a community integration did. `home` is a device flag, not proof the pet is
inside a precise geofence.

## History

Use an explicit timezone-aware window, at most seven days per helper request:

```bash
python "$SKILL_DIR/scripts/pettracer.py" history --device-id 12345 \
  --from-time 2026-09-13T06:00:00+02:00 --to-time 2026-09-13T12:00:00+02:00
```

These are example times, not the current requested interval. The helper preserves
provider order and states completeness is unverified. Check returned timestamps
against the requested interval; unknown/out-of-window points remain labelled.
Sort or deduplicate deliberately for a route, preserving originals and gaps.
Straight lines between sparse GPS fixes are not the actual path travelled.

## Live updates and modes

For immediate owner search/live mode use the official app/portal. A subscription
to updates does not itself command the collar to obtain a new fix. Changing modes
can affect battery and device behaviour; do not change settings as a side effect
of a location read. The old unbounded watcher is removed; retained protocol notes
in [portal and streaming](references/PORTAL.md) describe the evidence needed for
an explicitly scoped new integration, not a tested live client.

Do not promise continuous watching or future notification unless an authorised
running service/scheduler has actually been established. A failed stream or no GPS
fix is not evidence that the pet is safe, stationary, indoors, or at home.

## Return an honest location result

State the selected collar, latest valid measured coordinates, measurement time,
age/freshness state, and relevant missing/quality data. Report last contact separately.
A map link can disclose precise location to a third party; include it only as
appropriate to the user's request and keep raw history private. Do not overstate
accuracy, reverse-geocode a precise address without need, or infer human routines.

Exit zero means the read was processed, not that a recent GPS fix exists. Inspect
`last_fix.freshness` and `device_type_verified`. Missing/invalid fixes, schema errors,
auth failures, and empty history are different outcomes. Per-request socket timeout
and a 2 MiB response bound are not a total wall-clock SLA. There are no automatic
retries or re-login loops; verify an unexpected endpoint/schema before retrying.

Maintainers: `python -m unittest discover -s "$SKILL_DIR/tests" -v` tests parsing,
selection, request boundaries, and mocked transport. No live account or collar was
queried in this review. Vendor operational help: https://help.pettracer.com/.

History results retain each original record and label its measurement time as inside,
outside, or unknown relative to the requested inclusive window. This is separate
from fix age. A non-object `lastPos` is a schema error, not evidence of no GPS fix.
