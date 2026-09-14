# Agent skills

Task-focused instructions, references, templates, and tools for skills-compatible
agents. Each active skill has its own directory and `SKILL.md` entry point.

## Install and use

Read the selected skill's entry point, licence, dependencies, and account
requirements. The [Skills CLI](https://skills.sh/docs/cli) supports:

```bash
npx skills add tristanmanchester/agent-skills
```

This runs a CLI and changes the selected agent's skill installation. Select the
skills relevant to your work, or use your host's supported installation method.
Keep each entry point with its relative supporting files and record the source
revision. Do not keep duplicate active copies of the same skill.

Start with `SKILL.md`; load the references, assets, or scripts it identifies when
needed. Not every skill has a separate README. Resolve bundled scripts from the
installed skill directory, not an unrelated project's `scripts/` directory.
Instructions do not install dependencies, establish service access, or authorise
live mutations. Licences apply per skill; there is no blanket repository licence.

## Catalogue

The repository contains **36 active skill directories**. The September 2026
overhaul reviewed 37 baseline directories: 33 update PRs and one retirement PR
have merged, two skills were retained unchanged, and the `write-good-docs`
packaging proposal (#22) remains closed unmerged. Its existing skill is retained.

`meta-ads-control` was retired after its useful operations were consolidated into
[meta-ads-cli](meta-ads-cli/SKILL.md). The required merge order, #9 before #10, was
verified. There is no replacement compatibility entry point.

| Skill / entry point | Purpose |
| --- | --- |
| [agent-use](agent-use/SKILL.md) | Design and audit agent-facing capabilities, contracts, and recovery. |
| [ai-codebase-deep-modules](ai-codebase-deep-modules/SKILL.md) | Design cohesive modules, explicit ownership, and enforceable boundaries. |
| [animating-react-native-expo](animating-react-native-expo/SKILL.md) | Build native animations and gestures with a compatible Expo stack. |
| [assemblyai-transcribe](assemblyai-transcribe/SKILL.md) | AssemblyAI transcription workflows and speaker-aware local exports. |
| [audit-openclaw-security](audit-openclaw-security/SKILL.md) | Review OpenClaw exposure, policy, secrets, and diagnostic handling. |
| [auditing-appstore-readiness](auditing-appstore-readiness/SKILL.md) | Assess source, archive, runtime, and store submission evidence separately. |
| [designing-beautiful-websites](designing-beautiful-websites/SKILL.md) | Design and review purposeful, distinctive, accessible websites. |
| [display-quantitative-information](display-quantitative-information/SKILL.md) | Create and critique faithful quantitative displays. |
| [exa-search](exa-search/SKILL.md) | Use explicitly selected Exa search and content-retrieval workflows. |
| [expo-revenuecat-superwall-integration](expo-revenuecat-superwall-integration/SKILL.md) | Integrate purchases, offers, identity, restores, and entitlements. |
| [extracting-mistral-ocr](extracting-mistral-ocr/SKILL.md) | Mistral document extraction with bounded, organised exports. |
| [fabric-api](fabric-api/SKILL.md) | Build Fabric.so SDK/API integrations and upload workflows. |
| [fabric-cli](fabric-cli/SKILL.md) | Operate Fabric.so through its native CLI and scoped project memory. |
| [generating-novel-ideas](generating-novel-ideas/SKILL.md) | Explore distinct mechanisms, critique concepts, and define useful tests. |
| [giving-presentations](giving-presentations/SKILL.md) | Develop audience-focused narratives, visuals, and rehearsal plans. |
| [good-services-service-design](good-services-service-design/SKILL.md) | Review whole services with explicit evidence and scoped scoring. |
| [ios-simulator](ios-simulator/SKILL.md) | Run and inspect simulator apps with explicit targets and checked outcomes. |
| [jax-development](jax-development/SKILL.md) | Develop, debug, profile, and benchmark JAX code. |
| [meta-ads-cli](meta-ads-cli/SKILL.md) | Use the official Meta Ads CLI with bounded advanced API operations. |
| [nature-article-writer](nature-article-writer/SKILL.md) | Prepare scientific manuscripts with journal-specific checks. |
| [nextjs-framer-motion-animations](nextjs-framer-motion-animations/SKILL.md) | Implement Motion interactions and appropriate Next.js transition boundaries. |
| [optimising-expo-react-native-performance](optimising-expo-react-native-performance/SKILL.md) | Measure and improve native performance against reproducible baselines. |
| [parallel-ai-search](parallel-ai-search/SKILL.md) | Use explicitly selected Parallel search, research, and bounded job workflows. |
| [react-native-skia](react-native-skia/SKILL.md) | Build custom native graphics, gestures, snapshots, and shaders. |
| [reddit](reddit/SKILL.md) | Read-only research through permitted web/connector access or an approved OAuth API client; no anonymous JSON client. |
| [relationship-science-coach](relationship-science-coach/SKILL.md) | Practical relationship coaching with contextual safety and calibrated evidence. |
| [resend-api](resend-api/SKILL.md) | Build Resend SDK/API integrations, verified events, and Automations. |
| [resend-cli](resend-cli/SKILL.md) | Operate Resend through its native CLI with deliberate send and campaign scope. |
| [rust-anti-slop](rust-anti-slop/SKILL.md) | Apply the repository's intentional Rust code and lint policy. |
| [styling-nativewind-v4-expo](styling-nativewind-v4-expo/SKILL.md) | Configure and use the explicitly versioned NativeWind v4 stack. |
| [textual-tui](textual-tui/SKILL.md) | Build and test Textual interfaces, workers, and starter applications. |
| [todoist-api](todoist-api/SKILL.md) | Use Todoist's official CLI/API with explicit bulk-write recovery. |
| [track17](track17/SKILL.md) | Track parcels and ingest authenticated 17TRACK updates. |
| [tracking-pettracer-location](tracking-pettracer-location/SKILL.md) | Inspect owner-authorised PetTracer fixes and history through a bounded unofficial reader. |
| [wordly-wisdom](wordly-wisdom/SKILL.md) | Analyse decisions with explicit assumptions and checked arithmetic. |
| [write-good-docs](write-good-docs/SKILL.md) | Write and edit evidence-preserving technical documentation; packaging proposal #22 remains closed unmerged. |

## Review records

The [September 14 PR review](maintenance/pr-review-20260914.md) records the final
skill merges, checked bot findings, local tests, and remaining validation limits.
The [machine-readable checkpoint](maintenance/modernisation-progress.json) records
all baseline dispositions. GitHub remains the authority for later PR state.

The [September 13 source review](MAINTENANCE.md) and
[early September 14 template follow-up](maintenance/follow-up-20260914.md) are
historical records. Their open-PR counts describe those earlier checkpoints,
not the current repository. Merging source does not update existing installations
or establish live-provider, native-device, or agent-output performance.

## Contributing

Follow the [Agent Skills format](https://agentskills.io/specification): precise
activation, task-focused instructions, and supporting material loaded when useful.
Preserve useful methods and verified helpers. Check changing contracts against
current primary sources, and record which tests actually ran.

Keep one skill's changes in one PR. Repository-wide catalogue and maintenance
changes belong in a separate PR. A fixture, syntax check, mocked test, or merged
PR is not evidence that a live integration or a representative agent task passed.
