---
name: ios-simulator
description: >-
  Run and inspect an app on an iOS Simulator: choose a target, install and launch,
  capture evidence, exercise accessibility-driven UI, and diagnose simulator
  failures. Use for explicit simulator testing or automation, not general iOS
  implementation, physical-device validation, or App Store approval.
compatibility: Local simctl needs macOS and full Xcode with an installed simulator runtime. Current idb companion binaries require arm64, macOS 15+, and Xcode 26+; a remote client can run elsewhere. The optional checked runner requires Node.js 22+.
metadata:
  version: "2.0.0"
  reviewed: "2026-09-13"
---

# iOS Simulator

Use Apple's `xcrun simctl` for lifecycle and app operations, and current `idb` for
accessibility/input. Keep native command syntax rather than a second simulator
API. Resolve `SKILL_DIR` to the directory containing this file; it is not the app
repository's `scripts/` directory.

## Establish the target

```bash
xcode-select -p
xcodebuild -version
xcrun simctl list --json
idb --help
idb list-targets
```

Record the Xcode/runtime, exact simulator UDID, app bundle ID, build/configuration,
and reproduction steps. Choose from the actual inventory; never choose the first
fuzzy name match or silently switch to a different booted device. Use the same
explicit UDID for every operation. Inspect effective `IDB_COMPANION`/`IDB_UDID`
configuration without exposing credentials before assuming a local target.

Only install missing tools or runtimes when authorised. The current upstream
route is `brew install facebook/fb/idb`, which includes client and companion.
Full Xcode is required, not standalone Command Line Tools. Check host requirements
against [installation](https://fbidb.io/docs/idb/installation/); do not force an
unsupported binary onto a different architecture. The client may connect to an
explicitly authorised remote Mac; do not invent a remote-execution tool or expose
a companion to the public network.

## Run, observe, act, verify

1. Inspect `xcrun simctl help COMMAND` or `idb ui COMMAND --help` for the installed
   version. Unsupported syntax is a setup issue, not a reason to guess fallbacks.
2. Boot only when needed, then wait with `xcrun simctl bootstatus "$UDID" -b`.
   A boot request is not proof that the app is ready; an already-booted error is
   acceptable only after confirming the intended target's actual state.
3. Install the simulator-compatible `.app`, launch the exact bundle, and capture
   the initial screenshot/accessibility state.
4. Read the current UI; resolve a unique intended element; take one authorised
   action; check its expected postcondition. Re-read after layout/navigation changes.
5. Save the smallest useful evidence and distinguish process completion from
   app behaviour. A screenshot or successful tap alone does not pass a test.

```bash
xcrun simctl install "$UDID" /absolute/path/MyApp.app
xcrun simctl launch "$UDID" com.example.MyApp
idb ui describe-all --udid "$UDID"
idb ui text 'test text' --udid "$UDID"
xcrun simctl io "$UDID" screenshot /absolute/path/evidence.png
```

`idb ui text`, not `idb text`, targets the currently focused field. Use synthetic
values, not real credentials in arguments. Prefer a verified accessibility
identifier when available. Current marker matching is **first substring match**,
not unique equality: inspect candidates before tapping; refuse ambiguity. For
installed versions supporting it, guard with `--expected-value`. A coordinate
fallback needs a fresh image, correct point scaling, and a checked target; it is
not equivalent to accessibility activation.

See [operations and diagnosis](references/OPERATIONS.md) for remaining lifecycle,
permissions, push, clipboard, recording, logs, and test workflows.

## Reliable command outcomes

The optional helper runs a bounded, non-interactive command without a shell:

```bash
node "$SKILL_DIR/scripts/run.mjs" --timeout-ms 120000 -- \
  xcrun simctl bootstatus "$UDID" -b
```

It reports a JSON envelope and nonzero exit for failed launch, nonzero child exit,
signal, timeout, or output overflow. Captured output defaults to 1 MiB total;
`--max-bytes` adjusts that bound up to 16 MiB. It does not parse the command's own
result, approve actions, redact output, or guarantee termination of remote work.
Inspect nested results and verify state. A timed-out write may already have run;
do not blindly repeat a tap, purchase, push, or destructive operation.

Run recordings, interactive tools, and streaming logs directly with explicit
lifecycle control, not through this bounded helper. Some execution interfaces
(such as idb-repl) report execution errors in their output despite exit zero;
process status alone cannot validate them.

## Safety and acceptance

A simulator app can reach real services. UI input, URLs, push, permissions,
uninstall, erase, and delete are mutations, not a blanket safe tier. Use test
accounts/backends and the user's authorised scope. Before destructive operations,
identify the target and data loss; never default to `all` or erase to fix an
unrelated failure. Keep screenshots/logs private and review them before sharing.

Report the build/UDID, actions, expected versus observed results, evidence paths,
and unresolved failures. Simulator success does not establish physical-device
performance, store billing, hardware behaviour, or submission readiness.

Maintainer check: `node --test "$SKILL_DIR/tests/run.test.mjs"`. These runner tests
exercise local subprocess semantics, not Xcode, idb, or a real application.
