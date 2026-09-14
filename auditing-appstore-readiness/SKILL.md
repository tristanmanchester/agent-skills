---
name: auditing-appstore-readiness
description: >-
  Audit an iOS app's source, distribution archive, runtime behaviour, and App Store
  Connect setup for a planned submission. Use for explicit App Store/TestFlight
  readiness reviews of native, React Native, or Expo apps. Distinguish verified
  blockers from checks that still need build, device, account, or policy evidence.
compatibility: Static inventory requires Python 3.10+. Archive/runtime checks require an authorised macOS/Xcode or CI environment; live policy and App Store Connect checks require their respective access.
metadata:
  version: "2.0.0"
  reviewed: "2026-09-13"
---

# App Store readiness audit

A source scan cannot establish submission readiness. Assess four separate layers:
source configuration, the exact distribution archive, runtime behaviour, and
App Store Connect/policy state. Mark untested layers explicitly.

## Establish scope and evidence

Identify the intended app, target/scheme, platforms, release configuration, commit
and local changes, bundle ID, version/build, archive/build ID, and submission date.
In a monorepo, enumerate candidates rather than choosing the first plist or an
arbitrary 'best' project. Generated settings and `$(...)` placeholders need actual
resolved-build evidence.

Resolve `SKILL_DIR` to the installed directory containing this file, not the app
repository. The optional inventory reads bounded source metadata without executing
project code, installing dependencies, resolving dynamic config, or contacting services:

```bash
python "$SKILL_DIR/scripts/inspect_repo.py" --repo /absolute/path/to/app > /private/output/inventory.json
```

Choose an existing private output directory and a new filename before redirecting.
The script emits JSON with `submission_readiness: NOT_ASSESSED` **in every case**.
Exit 0 means inventory completed within its stated scope, 2 means partial/metadata
issues, and 1 means a fatal tool error. It excludes dependency/build directories,
skips symlinks, and reports traversal/size/entry limits. Its output is not a
secret-redacted public report or a full security/compliance scan.

## Check current submission requirements

Read Apple's [requirements](https://developer.apple.com/news/upcoming-requirements/)
and [review guidelines](https://developer.apple.com/app-store/review/guidelines/)
for the intended submission date and storefront. Record the applicable rule,
effective date, evidence, and any access limitation.

At this review (2026-09-13), iOS/iPadOS uploads have required Xcode 26 or later
and an iOS/iPadOS 26 SDK since **April 28, 2026**. Verify the actual uploaded
archive's build provenance, not just a locally installed Xcode version. A minimum
build SDK is not the same as the app's minimum supported OS. Recheck this rule
for each future submission rather than treating this dated snapshot as permanent.

## Source findings are leads, not automatic policy verdicts

Recognise arbitrary-named `.appiconset` resources, modern universal entries,
Icon Composer `.icon` resources, and Expo icon strings/appearance objects. A missing
`ios-marketing` entry is not by itself a blocker. Presence is also not enough:
verify the selected target's compiled icon and inspect required appearances.

Missing checked-in `Info.plist`, storyboard, or privacy manifest can reflect
generation/configuration, not a broken app. Resolve the actual build before
calling it a blocker. Trace runtime API use before requiring purpose strings or
ATT; a dependency name alone does not establish microphone use or tracking.
Public certificates are not automatically leaked private keys.

Use [evidence gates](references/GATES.md) for the full source/archive/runtime/store
checklist. Do not add boilerplate privacy declarations, collect extra permissions,
change signing, upload a build, or erase data merely to make a checker green.

## Build and runtime checks

Use an available authorised environment; do not invent a paired Mac or remote shell.
Record installed tool versions and select actual schemes/runtimes. Dependency
resolution, Expo config execution/prebuild, build scripts, signing, archiving, and
uploads can execute code or modify local/remote state; stay within authorised scope.
A simulator Release build is useful but not a substitute for a signed device archive
or device-only behaviours. Preserve logs/result bundles and exact artefact identity.

## Report

Return a compact gate table with `verified`, `blocked`, `unverified`, or
`not applicable` for each layer, followed by actionable findings. Each finding
needs evidence, consequence, remediation, and the verification that closes it.

Use **BLOCKED** for demonstrated submission blockers; **UNVERIFIED** when required
checks remain; **READY TO SUBMIT** only when the defined gates have actually been
checked for the exact build and account. That recommendation does not guarantee
Apple approval. Keep assumptions and unresolved items visible; a static inventory
must never be relabelled PASS/ready-to-submit.

Maintainer tests: `python -m unittest discover -s "$SKILL_DIR/tests" -v`.
These test source-inventory behaviour, not Apple acceptance or a native build.
