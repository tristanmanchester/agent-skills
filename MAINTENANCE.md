# Skills modernisation checkpoint

Snapshot: September 13, 2026. Source baseline:
`b28669d18b1731233a07fb73da3d00b39d41bee2`.

**22 of the 37 baseline skill directories have a dedicated proposed-change PR
(#3–#24). Fifteen reviews remain outstanding.** The catalogue and JSON checkpoint
list them explicitly. Outstanding is not a keep/delete judgement and does not mean
the skill has been verified current. No PR has been merged by this work.

## Recovering work after an interrupted session

Read this checkpoint, then inspect the actual current default-branch head and
open/closed PRs. Do not assume this dated file is still current. Reuse an existing
skill branch/PR when continuing its repair instead of creating a duplicate.
Fetch changed source and relevant upstream contracts; a PR description is a report
of work, not independent verification of its correctness.

All skill PRs at this checkpoint were created independently from the baseline,
not as a stack of unrelated skill changes. Scope new changes to one skill.
**Merge #9 before #10**: Meta Ads control retirement depends on the retained
Meta CLI skill receiving its capability-preserving replacement first. Do not merge
or publish to production merely because this maintenance document lists a PR.

## Latest completed publication batch

| PR | Skill | Exact head commit |
| --- | --- | --- |
| [#21](https://github.com/tristanmanchester/agent-skills/pull/21) | agent-use | `f344bbb18345ad98612b876635be91b6a6f05705` |
| [#22](https://github.com/tristanmanchester/agent-skills/pull/22) | write-good-docs | `f0bcbc93e828cb631d9e5c750e1dc98097e2ca72` |
| [#23](https://github.com/tristanmanchester/agent-skills/pull/23) | display-quantitative-information | `52ca9054bf76e0dd87f6cea08918ee1b5a9f2205` |
| [#24](https://github.com/tristanmanchester/agent-skills/pull/24) | generating-novel-ideas | `f2656aff6d98728284bd8de88eaaee202b57e423` |

The previous resumed work also published JAX (#19) and Nature writing (#20).
They were found in the live PR inventory rather than recreated.

## Evidence from this batch

The local Python regression suites passed 32 test methods: 11 for agent-use
scaffolding/structural validation, 14 for quantitative SVG geometry/input/output,
and 7 for ideation lexical parsing/overlap. The writing skill received a packaging
repair; its existing full test suite was not rerun in this batch. Earlier PR
validation claims remain recorded in their own descriptions and were not all
re-executed during recovery.

The new A2A card was checked against selected current specification fields and
fixtures, not a complete live protocol-conformance suite. SVG geometry tests are
not a visual readability or accessibility certification. Lexical overlap does not
measure novelty. Ideation/authoring evaluation scenarios have not been converted
into a controlled model-output comparison by this work.

No authenticated provider operation, simulator/native build, store submission,
A2A deployment, advertisement, email send, or paid research job was performed in
this batch. GitHub is the only connected service mutated. Public upstream docs
and repository source were read. Network access from the local execution container
was unavailable, so local tests used reconstructed selected source files; no full
repository clone/build was claimed.

## Outstanding review leads

Start from the actual sources for the fifteen outstanding entries in the catalogue.
The original pasted audit is a source of leads, not a set of accepted conclusions.
Preserve sound design/presentation/service/Rust-policy methods instead of changing
them merely because they are old or lack fashionable API terminology.

Three mobile entry points received an initial read after the latest batch, but
remain outstanding rather than being marked fully reviewed:

- **react-native-skia:** check its audit helper/templates against the current
  React/RN/Reanimated/Worklets and platform requirements. Current installation
  docs also describe changed binary delivery and an optional Graphite preview;
  do not enable a preview by default or infer compatibility from the skill title.
- **animating-react-native-expo:** verify setup checks, installed Gesture Handler
  hook API support, reduced-motion behaviour, and device outcomes. Its existing
  Reanimated-4 direction is not automatically obsolete.
- **nextjs-framer-motion-animations:** compare the retained scaffold/migration
  machinery and router examples with current Motion and Next.js contracts. Motion
  13 changes styled-component prop validation; do not assume an older package
  strategy or a persistent wrapper proves all App Router exit behaviours.

Those are leads, not a claim that their scripts or application examples were tested.
Fabric, Reddit, and PetTracer need especially careful checks of provider identity,
authorisation, unofficial interfaces, and live-call boundaries. Do not run account
mutations as a substitute for a source review.

## Primary source entry points

Reviewed during this batch or its final reconnaissance:

- https://agentskills.io/specification
- https://agentskills.io/skill-creation/best-practices
- https://a2a-protocol.org/latest/specification/
- https://www.rfc-editor.org/rfc/rfc9727.html
- https://developers.google.com/terms/site-policies
- https://diataxis.fr/colophon/
- https://shopify.github.io/react-native-skia/docs/getting-started/installation/
- https://docs.swmansion.com/react-native-reanimated/docs/fundamentals/getting-started/
- https://motion.dev/docs/react-upgrade-guide
- https://skills.sh/docs/cli

Use the exact installed version and current relevant source for each actual repair;
this index is not a blanket assertion that every linked API was fully validated.
