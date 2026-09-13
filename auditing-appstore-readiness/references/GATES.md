# Evidence gates

## Source and effective configuration

Record every candidate app/extension and the target actually being submitted.
Check resolved bundle IDs, version/build numbering, device support, orientations,
entitlements, launch configuration, URL schemes, and build environment. Source
values can be generated or overridden; `$(PRODUCT_BUNDLE_IDENTIFIER)` is not the
resolved identifier. A clean Git tree is useful provenance, not an App Store rule.

For Expo, inspect the installed SDK, app configuration, config plugins, EAS profile,
remote versioning, and generated native output. Running `expo config` executes
project configuration; do not call it a passive file read. Avoid prebuild/install
side effects during a source-only audit. For bare React Native/native apps, include
native targets, linked SDKs, Pods/SPM dependencies, and their release configuration.

## Icons and launch presentation

Current supported workflows include asset-catalog single/universal icons and
Icon Composer `.icon` resources; Expo can select a path, `.icon` directory, or
appearance-specific object depending on its SDK. Do not require the literal name
`AppIcon` or one historical `ios-marketing` JSON entry. Inspect the selected
asset/build settings and compiled result, resolution/colour/appearance requirements,
and rendering on supported devices. The inventory does not decode artwork or
validate Icon Composer internals; `exists` means only a source path exists.
Remote Expo icon URLs are reported as not fetched, not missing local files.

Launch presentation may be declarative (`UILaunchScreen`), generated, or storyboard
based. Verify what the archive includes and what appears on launch instead of
requiring one filename. Check default/dark appearance, supported screen sizes,
localisation, and accessibility in the app's actual release build.

## Privacy, permissions, transport, and security

Trace actual data flows and API calls in the app and embedded SDKs. Match purpose
strings/localisations to capabilities actually used; playback-only audio is not
proof of microphone access, and analytics is not automatically cross-app tracking.
Review consent/ATT where applicable, refusal paths, required-reason API declarations,
SDK manifests/signatures, and the archive's privacy report. A parseable manifest
is not proof its declarations are correct. Do not invent approved reasons just to
silence a warning.

Inspect effective ATS exceptions and justification, outbound hosts, embedded
credentials, local storage, account deletion/export flows where applicable, and
privacy-policy accuracy. A filename-only secret check is insufficient: distinguish
private keys/tokens from public certificates and sample placeholders. Verify an
actual exposure before proposing rotation/history rewriting; perform changes only
within the authorised recovery scope. Keep reports/logs private.

## Exact archive and runtime

Record the source commit plus changes, build service/job, Xcode/SDK used, distribution
archive hash/build ID, bundle/version/build values, signing team/profile, and
entitlements. Inspect the archive being uploaded, not an unrelated local build.
Verify asset compilation, packaging, supported architectures, and validation/upload
results. Build success, upload acceptance, TestFlight processing, and App Review
approval are distinct states.

Exercise first launch, upgrade/data preservation, denied permissions, offline and
poor-network paths, login/logout/deletion where provided, deep links, background
behaviour, accessibility, and critical app flows. Use approved test accounts and
backend environments. For purchases, check products, prices, restore, cancellation,
entitlement fulfilment, and subscription disclosure in the appropriate sandbox;
a simulated UI tap or mocked store response does not establish real billing.

## Store and policy state

Review current App Store Connect metadata, screenshots/previews, age-rating
questionnaire, category, availability, privacy/support URLs, nutrition labels,
export-compliance answers, review notes/demo access, agreements, and applicable
regional/account requirements. Check IP/content rights and SDK/asset licences.
Apply current storefront-specific rules for accounts, payments, links, and trader
status rather than one universal historical assumption. Missing account access
means unverified, not automatically compliant or noncompliant.

## Sources reviewed 2026-09-13

- [Apple submission requirements](https://developer.apple.com/news/upcoming-requirements/)
- [App Review Guidelines](https://developer.apple.com/app-store/review/guidelines/)
- [Icon Composer](https://developer.apple.com/icon-composer/)
- [Expo app configuration](https://docs.expo.dev/versions/latest/config/app/)
- [Expo store assets](https://docs.expo.dev/guides/store-assets/)

These links establish the review baseline, not a substitute for checking the
rules and exact project SDK when performing an audit.
