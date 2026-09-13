# Skills modernisation review and publication record

Snapshot: September 13, 2026. Source baseline:
`b28669d18b1731233a07fb73da3d00b39d41bee2`.

**All 37 baseline skill directories have a source-review disposition.** There
are 34 open skill PRs, one closed-unmerged skill PR, and two skills retained
without changes. The final continuation published 13 skill PRs (#26–#38), keeping
one skill per PR. Repository-only catalogue work remains in #25. No PR was merged
by this work; main was rechecked and still points to the baseline.

This completes the disposition pass, not exhaustive runtime certification of every
retained file or upstream fact. The individual PRs identify inspected source,
current primary-source checks, tests actually run, and important gaps. A source
review does not establish live service access, successful native builds, complete
accessibility, clinical efficacy, or improved agent output.

## Recover or review the work

Read the current default branch and actual open/closed PR state before acting on
this dated record. Reuse the existing skill branch/PR for further repairs rather
than creating a duplicate. A PR description reports work; it is not independent
proof of correctness. Read the changed code and relevant upstream contract.

**Merge #9 before #10:** retiring meta-ads-control depends on the capability-preserving
meta-ads-cli update. Other skill PRs were independently based on the same baseline,
not stacked with unrelated changes. Merging this catalogue does not merge those
skills, and an ordinary install from main does not include unmerged changes.

**#22 was observed closed without merging** (write-good-docs). It was not reopened,
recreated, or treated as accepted. Its prior packaging proposal remains available
in history; any further action needs the user's direction. Do not silently turn a
closed proposal into a new PR under a different name.

The machine-readable [checkpoint](maintenance/modernisation-progress.json) records
all 37 directories, their PR/disposition, latest published head commits, and test
counts. Reconcile it after review decisions or merges.

## Final publication batch

| PR | Skill | Verified repair or modernisation |
| --- | --- | --- |
| [#26](https://github.com/tristanmanchester/agent-skills/pull/26) | fabric-api | Official SDK first, explicit Memory API base scope, signed-upload and ambiguous-write recovery; inherited detailed routes labelled for current verification |
| [#27](https://github.com/tristanmanchester/agent-skills/pull/27) | fabric-cli | Native CLI, no false ask-read guarantee or blind JSON-failure replay; explicit resource type, workspace, and memory scope |
| [#28](https://github.com/tristanmanchester/agent-skills/pull/28) | animating-react-native-expo | Current RNGH3 cancellation, gesture offsets/pending state, compatible native stack, reduced motion and cleanup |
| [#29](https://github.com/tristanmanchester/agent-skills/pull/29) | react-native-skia | Current dependency-delivered binaries and animation contracts; remove obsolete postinstall/setup scoring while keeping drawing methods/templates |
| [#30](https://github.com/tristanmanchester/agent-skills/pull/30) | nextjs-framer-motion-animations | Framework route-transition versus local presence contracts, semantic controls and boundaries; remove heuristic scaffolding/import rewriting |
| [#31](https://github.com/tristanmanchester/agent-skills/pull/31) | textual-tui | Precise worker lifecycle plus bounded, non-writing starter previews and AST-safe titles; keep all eleven starter archetypes |
| [#32](https://github.com/tristanmanchester/agent-skills/pull/32) | reddit | Approved read-only access instead of anonymous-JSON retries; preserve original context, dates, truncation, and thread completeness |
| [#33](https://github.com/tristanmanchester/agent-skills/pull/33) | tracking-pettracer-location | Measurement-time freshness, finite coordinates, fixed-origin bounded reads, and raw unverified quality fields; no untested live watcher promise |
| [#34](https://github.com/tristanmanchester/agent-skills/pull/34) | wordly-wisdom | Fixed utility anchors avoid option-set rank reversal; strict finite probabilities/weights and explicit scenario/model assumptions |
| [#35](https://github.com/tristanmanchester/agent-skills/pull/35) | relationship-science-coach | Remove keyword-based safety decisions; preserve practical coaching with context, consent, autonomy, and calibrated evidence |
| [#36](https://github.com/tristanmanchester/agent-skills/pull/36) | ai-codebase-deep-modules | Correct import/visibility enforcement and remove unchecked placeholder generator; retain ownership/contracts/testing methods |
| [#37](https://github.com/tristanmanchester/agent-skills/pull/37) | good-services-service-design | Evidence states and scoped local scoring, distinct from the author's scale; proportional deliverables and preserved end-to-end service methods |
| [#38](https://github.com/tristanmanchester/agent-skills/pull/38) | designing-beautiful-websites | Distinctive, task-scoped design plus current selected accessibility checks; retain contrast helper and specialist references |

These are proposed changes, not claims that providers, stores, users, or reviewers
have accepted them. Removing a handwritten client in favour of a maintained
surface does not prove that surface covers every historical operation. The skill
must verify the specific required operation rather than quietly dropping it.

## Two skills retained without changes

### rust-anti-slop

Read the core, full rules reference, workspace-lints.toml, and clippy.toml. The
policy deliberately balances errors, unsafe code, cloning, concurrency, narrow
lint exceptions, and workspace inheritance. Selected lint availability and Cargo
configuration were checked against official documentation; no identified defect
justified changing the user's intentional Rust policy merely to make it look new.

This is a keep decision within that review scope, not a claim every Clippy option
was executed on every supported toolchain. No cargo/rustc/lint run was performed.
Selected sources: https://doc.rust-lang.org/clippy/ and
https://doc.rust-lang.org/cargo/reference/manifest.html#the-lints-section.

### giving-presentations

Read the core, source notes, and slide-design/visuals reference. The audience,
message, narrative, evidence, live-versus-async, rehearsal, quantitative integrity,
and readable/accessible visual methods remain useful. There is no API migration
or concrete packaging defect identified in those reviewed paths requiring a PR.

Timing, word-count, and design ranges remain heuristics, not universal empirical
laws. The whole inherited source bibliography was not freshly re-audited, and no
presentation, audience study, reading-order test, or model-output comparison was
run. Keeping it avoids a cosmetic rewrite of a useful method.

## Tests actually executed in this continuation

Thirty Python unittest methods passed on Linux / Python 3.13.5, and all three
suites passed again in the final check:

| Skill | Methods | What they establish |
| --- | ---: | --- |
| textual-tui | 8 | Literal quoted/injection-like titles, identifier validation, non-writing previews, complete preflight, exclusive output, symlink/path safeguards |
| tracking-pettracer-location | 10 | Measurement-time/coordinate semantics, explicit device selection, pre-network window validation, fixed origin, no retries/redirects, bounded mocked response |
| wordly-wisdom | 12 | Fixed-anchor invariance, finite/strict inputs, direction/bounds, EV arithmetic, duplicate/oversized JSON, CLI failures, input preservation |

The source files used locally were reconstructed selected files, not a full repo
clone. Network access from the execution container was unavailable; connected
GitHub performed the repository writes. Selected local implementation Git blob
hashes were compared with the published files, including the Textual scaffolder
and all three decision-math modules. PetTracer's script/test hashes are recorded
in its PR. No target account credentials or private user data were used in tests.

The Textual tests use synthetic templates; the full eleven-template self-check,
Textual/Pilot app runtime, and terminal/browser rendering were not run. PetTracer
transport is mocked; its unofficial live protocol, quality units, battery calibration,
and history completeness remain unverified. Decision arithmetic does not validate
the supplied utilities/probabilities or predict the user's outcome.

The other ten new skill PRs received source/documentation review rather than
executable regression suites. No authenticated Fabric/Reddit/PetTracer/provider
request, native build, store upload, browser/screen-reader test, paid job, clinical
study, or controlled agent-output evaluation was performed. Earlier batches' tests
were not all rerun; their reports remain scoped to their own PRs.

## Final cross-reference and status checks

Rechecked the decision skill's new core links against its actual tree and inspected
the retained scenario sample against the new input shape. Inspected current Skia
performance/evaluation references and indexed references to removed setup helpers;
these checks were targeted, not a complete link crawl of every retained file.
New web-design links were checked against its retrieved recursive tree.

The checkpoint was locally parsed/checked for 37 unique directories, 35 distinct
skill PR mappings, the 13 new PR numbers/head formats, two keep dispositions,
one closed-unmerged disposition, and the 30-method test sum. Live GitHub reported
35 open PRs total at final status check: 34 skill PRs plus repository PR25.

## Remaining verification before real use

Review and merge deliberately, then install the intended revision. Version-match
SDK/native types and run the actual integration paths that matter to the app or
account. Test live operations only within explicit authorisation and appropriate
test data. Preserve unresolved outcomes and never use a timeout as proof a mutation
did not occur. Evaluate skills on real representative agent tasks before claiming
better outputs. These are documented validation limits, not unassigned skill reviews.

Current-source entry points for this batch are linked in each skill PR. Apply
https://agentskills.io/specification and task-specific primary sources, preserving
provenance, licensing, and a clear separation between a method, a supplied fixture,
an observed test result, and a proposed improvement.
