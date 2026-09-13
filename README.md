# Agent skills

Task-focused instructions, references, templates, and tools for skills-compatible
agents. Each skill lives in its own directory with a `SKILL.md` entry point.
The collection is not restricted to Clawdbot or any other single host; individual
skills can still have platform, runtime, dependency, or account requirements.

## Install deliberately

Read the selected skill and its licence/dependencies before use. The
[Skills CLI](https://skills.sh/docs/cli) supports installing this repository:

```bash
DISABLE_TELEMETRY=1 npx skills add tristanmanchester/agent-skills
```

This downloads/runs a CLI and changes the selected agent's skill installation.
The environment setting opts out of that CLI's documented telemetry. Select only
skills relevant to the workflow, or install reviewed directories using the host's
own mechanism. Keep each entry point with its relative supporting files, record
the source revision, and avoid duplicate active copies of a skill.

A skill's instructions do not install dependencies, establish API access, or grant
permission for live mutations. Resolve bundled scripts from the installed skill
directory, not from an unrelated project's `scripts/` folder. Read the applicable
licence per skill; no blanket repository-wide redistribution licence is asserted.

## Catalogue and modernisation status

All **37 baseline skill directories now have a source-review disposition**.
At the September 13, 2026 checkpoint, 34 skill PRs are open, one was closed
unmerged, and two skills are retained without changes. The latest batch added
13 skill PRs (#26–#38). No PR was merged by this work, and the baseline remains
`b28669d18b1731233a07fb73da3d00b39d41bee2`.

A proposed change is not an installed update. Source review, local regression
tests, live integration tests, and agent-output evaluations are different evidence.
See [MAINTENANCE.md](MAINTENANCE.md) for exact scope, retained-skill rationale,
verification gaps, and recovery instructions, and
[the machine-readable checkpoint](maintenance/modernisation-progress.json).
Recheck GitHub before relying on this dated status table.

| Skill directory / entry point | Disposition at this checkpoint |
| --- | --- |
| [agent-use](agent-use/SKILL.md) | Proposed in [#21](https://github.com/tristanmanchester/agent-skills/pull/21) |
| [ai-codebase-deep-modules](ai-codebase-deep-modules/SKILL.md) | Proposed in [#36](https://github.com/tristanmanchester/agent-skills/pull/36) |
| [animating-react-native-expo](animating-react-native-expo/SKILL.md) | Proposed in [#28](https://github.com/tristanmanchester/agent-skills/pull/28) |
| [assemblyai-transcribe](assemblyai-transcribe/SKILL.md) | Proposed in [#18](https://github.com/tristanmanchester/agent-skills/pull/18) |
| [audit-openclaw-security](audit-openclaw-security/SKILL.md) | Proposed in [#3](https://github.com/tristanmanchester/agent-skills/pull/3) |
| [auditing-appstore-readiness](auditing-appstore-readiness/SKILL.md) | Proposed in [#17](https://github.com/tristanmanchester/agent-skills/pull/17) |
| [designing-beautiful-websites](designing-beautiful-websites/SKILL.md) | Proposed in [#38](https://github.com/tristanmanchester/agent-skills/pull/38) |
| [display-quantitative-information](display-quantitative-information/SKILL.md) | Proposed in [#23](https://github.com/tristanmanchester/agent-skills/pull/23) |
| [exa-search](exa-search/SKILL.md) | Proposed in [#15](https://github.com/tristanmanchester/agent-skills/pull/15) |
| [expo-revenuecat-superwall-integration](expo-revenuecat-superwall-integration/SKILL.md) | Proposed in [#8](https://github.com/tristanmanchester/agent-skills/pull/8) |
| [extracting-mistral-ocr](extracting-mistral-ocr/SKILL.md) | Proposed in [#5](https://github.com/tristanmanchester/agent-skills/pull/5) |
| [fabric-api](fabric-api/SKILL.md) | Proposed in [#26](https://github.com/tristanmanchester/agent-skills/pull/26) |
| [fabric-cli](fabric-cli/SKILL.md) | Proposed in [#27](https://github.com/tristanmanchester/agent-skills/pull/27) |
| [generating-novel-ideas](generating-novel-ideas/SKILL.md) | Proposed in [#24](https://github.com/tristanmanchester/agent-skills/pull/24) |
| [giving-presentations](giving-presentations/SKILL.md) | Retain; no change justified by this source review |
| [good-services-service-design](good-services-service-design/SKILL.md) | Proposed in [#37](https://github.com/tristanmanchester/agent-skills/pull/37) |
| [ios-simulator](ios-simulator/SKILL.md) | Proposed in [#12](https://github.com/tristanmanchester/agent-skills/pull/12) |
| [jax-development](jax-development/SKILL.md) | Proposed in [#19](https://github.com/tristanmanchester/agent-skills/pull/19) |
| [meta-ads-cli](meta-ads-cli/SKILL.md) | Proposed in [#9](https://github.com/tristanmanchester/agent-skills/pull/9) |
| meta-ads-control | [Retirement #10](https://github.com/tristanmanchester/agent-skills/pull/10); merge #9 first |
| [nature-article-writer](nature-article-writer/SKILL.md) | Proposed in [#20](https://github.com/tristanmanchester/agent-skills/pull/20) |
| [nextjs-framer-motion-animations](nextjs-framer-motion-animations/SKILL.md) | Proposed in [#30](https://github.com/tristanmanchester/agent-skills/pull/30) |
| [optimising-expo-react-native-performance](optimising-expo-react-native-performance/SKILL.md) | Proposed in [#6](https://github.com/tristanmanchester/agent-skills/pull/6) |
| [parallel-ai-search](parallel-ai-search/SKILL.md) | Proposed in [#16](https://github.com/tristanmanchester/agent-skills/pull/16) |
| [react-native-skia](react-native-skia/SKILL.md) | Proposed in [#29](https://github.com/tristanmanchester/agent-skills/pull/29) |
| [reddit](reddit/SKILL.md) | Proposed in [#32](https://github.com/tristanmanchester/agent-skills/pull/32) |
| [relationship-science-coach](relationship-science-coach/SKILL.md) | Proposed in [#35](https://github.com/tristanmanchester/agent-skills/pull/35) |
| [resend-api](resend-api/SKILL.md) | Proposed in [#14](https://github.com/tristanmanchester/agent-skills/pull/14) |
| [resend-cli](resend-cli/SKILL.md) | Proposed in [#13](https://github.com/tristanmanchester/agent-skills/pull/13) |
| [rust-anti-slop](rust-anti-slop/SKILL.md) | Retain; intentional policy remains useful |
| [styling-nativewind-v4-expo](styling-nativewind-v4-expo/SKILL.md) | Proposed in [#7](https://github.com/tristanmanchester/agent-skills/pull/7) |
| [textual-tui](textual-tui/SKILL.md) | Proposed in [#31](https://github.com/tristanmanchester/agent-skills/pull/31) |
| [todoist-api](todoist-api/SKILL.md) | Proposed in [#11](https://github.com/tristanmanchester/agent-skills/pull/11) |
| [track17](track17/SKILL.md) | Proposed in [#4](https://github.com/tristanmanchester/agent-skills/pull/4) |
| [tracking-pettracer-location](tracking-pettracer-location/SKILL.md) | Proposed in [#33](https://github.com/tristanmanchester/agent-skills/pull/33) |
| [wordly-wisdom](wordly-wisdom/SKILL.md) | Proposed in [#34](https://github.com/tristanmanchester/agent-skills/pull/34) |
| [write-good-docs](write-good-docs/SKILL.md) | [#22](https://github.com/tristanmanchester/agent-skills/pull/22) closed unmerged; not reopened or recreated |

## Contributing

Follow the [Agent Skills format](https://agentskills.io/specification): precise
activation, concise task instructions, and supporting material loaded when useful.
Preserve useful methods and tested helpers; remove obsolete interfaces rather than
adding compatibility layers to new skill designs. Verify factual changes against
current primary sources and record the exact tests actually run.

Keep one skill's changes in one PR. Repository-wide catalogue or maintenance work
belongs in a separate PR. A parser check, fixture file, mocked test, or published
PR is not evidence of a successful live provider call or improved agent output.
