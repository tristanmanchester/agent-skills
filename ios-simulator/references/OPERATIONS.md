# Operations and diagnosis

Use an explicit `UDID` and inspect installed `simctl help`/`idb --help` before
using optional flags. Do not add `|| true` to mutation commands. Native nonzero
results must be explained and reconciled, not converted to success.

## Native operations

Examples use the selected simulator, never `all`:

```bash
xcrun simctl list --json
xcrun simctl boot "$UDID"
xcrun simctl bootstatus "$UDID" -b
xcrun simctl shutdown "$UDID"
xcrun simctl get_app_container "$UDID" com.example.MyApp data
xcrun simctl terminate "$UDID" com.example.MyApp
```

For creation, select exact available device-type and runtime identifiers from
the inventory, then use `simctl create NAME TYPE_ID RUNTIME_ID`. Record the
returned UDID. Erase/delete/uninstall require a deliberately authorised target
and loss assessment; verify the result with inventory or app state. They are
not generic troubleshooting steps.

## Accessibility

```bash
idb ui describe-all --udid "$UDID"
idb ui describe 'login.submit' --match-key AXUniqueId --udid "$UDID"
idb ui tap 'login.submit' --match-key AXUniqueId --expected-value 'Log in' --udid "$UDID"
idb ui button HOME --udid "$UDID"
```

These marker/guard options require a current implementation advertising them in
help. Markers use substring matching and may choose the first result. Inspect
the complete relevant candidate set, enabled/interactable state, and intended
label before acting. Truncated/depth-limited output is not proof of uniqueness.
Use accessibility IDs exposed by the app, not invented IDs from this example.

Reads support different output formats/backends; inspect the schema actually
returned rather than assuming every response is a flat array. A missing node can
mean wrong frontmost app, inaccessible content, incomplete depth, or backend
limitations. Consult the upstream accessibility guide before switching backend.
Bound waits by a deadline and report the last observed state; never poll forever.

## Evidence, permissions, and input

- Screenshot: `xcrun simctl io "$UDID" screenshot /absolute/path/screen.png`.
  Verify the created file and its contents. Use unique private output paths.
- Video: `xcrun simctl io "$UDID" recordVideo /absolute/path/flow.mp4` in a
  controlled foreground session. Stop cleanly, allow finalisation, then inspect
  the recording. A killed recorder may leave an unusable file.
- Logs: `xcrun simctl spawn "$UDID" log show --last 5m --predicate 'process == "MyApp"'`.
  Bound time and filters; logs may contain personal data and tokens.
- Clipboard: `simctl pbpaste "$UDID"` / `simctl pbcopy "$UDID"` (copy reads stdin).
  Use native input piping, not the runner, whose stdin is deliberately closed.
- URL: `simctl openurl "$UDID" URL`. Deep links can mutate remote state.
- Privacy: `simctl privacy "$UDID" grant SERVICE BUNDLE_ID`; also inspect help for
  revoke/reset and supported service names. Verify requested permissions in-app.
- Push: `simctl push "$UDID" BUNDLE_ID /absolute/path/payload.apns`. Create the
  JSON privately, verify its intended app/payload, then remove the temporary file.
  Simulated delivery does not test production APNs registration or routing.

## Diagnosis

Check selected developer directory and installed runtimes before changing them.
Prefer an explicitly scoped `DEVELOPER_DIR` over changing the entire machine's
Xcode selection without permission. First-launch setup and runtime installation
are real host changes. Missing CLT-only simctl support needs full Xcode.

For idb, verify the actual companion target, host architecture, Xcode selection,
and client/companion versions. An executable in PATH is not a working connection.
Use loopback/local sockets or an explicitly secured remote connection. Check the
frontmost app and read its tree before retrying input.

For repeatable app assertions, prefer the project's XCTest/XCUITest suite and
retain the test result bundle. Installing a test bundle or launching a test is
not equivalent to an assertion passing. Keep simulator-only limitations in the
report and reserve hardware/performance/billing checks for appropriate devices.

## Sources reviewed 2026-09-13

- [idb installation](https://fbidb.io/docs/idb/installation/)
- [idb commands](https://fbidb.io/docs/idb/commands/)
- [UI automation](https://fbidb.io/docs/idb/ui/)
- [Accessibility](https://fbidb.io/docs/idb/accessibility/)
- Apple tool contracts: installed `xcrun simctl help` and `xcodebuild -help`.
