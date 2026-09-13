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

This catalogue covers the source directories at
`b28669d18b1731233a07fb73da3d00b39d41bee2`. PR links describe proposed changes;
they are **not merged changes or a certification that every runtime works**.
See [MAINTENANCE.md](MAINTENANCE.md) for evidence limits and continuation steps,
and [the machine-readable checkpoint](maintenance/modernisation-progress.json).
Update this snapshot when reviews or merges change it.

| Skill directory / entry point | Review status at this checkpoint |
| --- | --- |
| [agent-use](agent-use/SKILL.md) | [PR #21](https://github.com/tristanmanchester/agent-skills/pull/21) |
| [ai-codebase-deep-modules](ai-codebase-deep-modules/SKILL.md) | Review outstanding |
| [animating-react-native-expo](animating-react-native-expo/SKILL.md) | Review outstanding |
| [assemblyai-transcribe](assemblyai-transcribe/SKILL.md) | [PR #18](https://github.com/tristanmanchester/agent-skills/pull/18) |
| [audit-openclaw-security](audit-openclaw-security/SKILL.md) | [PR #3](https://github.com/tristanmanchester/agent-skills/pull/3) |
| [auditing-appstore-readiness](auditing-appstore-readiness/SKILL.md) | [PR #17](https://github.com/tristanmanchester/agent-skills/pull/17) |
| [designing-beautiful-websites](designing-beautiful-websites/SKILL.md) | Review outstanding |
| [display-quantitative-information](display-quantitative-information/SKILL.md) | [PR #23](https://github.com/tristanmanchester/agent-skills/pull/23) |
| [exa-search](exa-search/SKILL.md) | [PR #15](https://github.com/tristanmanchester/agent-skills/pull/15) |
| [expo-revenuecat-superwall-integration](expo-revenuecat-superwall-integration/SKILL.md) | [PR #8](https://github.com/tristanmanchester/agent-skills/pull/8) |
| [extracting-mistral-ocr](extracting-mistral-ocr/SKILL.md) | [PR #5](https://github.com/tristanmanchester/agent-skills/pull/5) |
| [fabric-api](fabric-api/SKILL.md) | Review outstanding |
| [fabric-cli](fabric-cli/SKILL.md) | Review outstanding |
| [generating-novel-ideas](generating-novel-ideas/SKILL.md) | [PR #24](https://github.com/tristanmanchester/agent-skills/pull/24) |
| [giving-presentations](giving-presentations/SKILL.md) | Review outstanding |
| [good-services-service-design](good-services-service-design/SKILL.md) | Review outstanding |
| [ios-simulator](ios-simulator/SKILL.md) | [PR #12](https://github.com/tristanmanchester/agent-skills/pull/12) |
| [jax-development](jax-development/SKILL.md) | [PR #19](https://github.com/tristanmanchester/agent-skills/pull/19) |
| [meta-ads-cli](meta-ads-cli/SKILL.md) | [PR #9](https://github.com/tristanmanchester/agent-skills/pull/9) |
| meta-ads-control | [Retirement PR #10](https://github.com/tristanmanchester/agent-skills/pull/10); merge #9 first |
| [nature-article-writer](nature-article-writer/SKILL.md) | [PR #20](https://github.com/tristanmanchester/agent-skills/pull/20) |
| [nextjs-framer-motion-animations](nextjs-framer-motion-animations/SKILL.md) | Review outstanding |
| [optimising-expo-react-native-performance](optimising-expo-react-native-performance/SKILL.md) | [PR #6](https://github.com/tristanmanchester/agent-skills/pull/6) |
| [parallel-ai-search](parallel-ai-search/SKILL.md) | [PR #16](https://github.com/tristanmanchester/agent-skills/pull/16) |
| [react-native-skia](react-native-skia/SKILL.md) | Review outstanding |
| [reddit](reddit/SKILL.md) | Review outstanding |
| [relationship-science-coach](relationship-science-coach/SKILL.md) | Review outstanding |
| [resend-api](resend-api/SKILL.md) | [PR #14](https://github.com/tristanmanchester/agent-skills/pull/14) |
| [resend-cli](resend-cli/SKILL.md) | [PR #13](https://github.com/tristanmanchester/agent-skills/pull/13) |
| [rust-anti-slop](rust-anti-slop/SKILL.md) | Review outstanding |
| [styling-nativewind-v4-expo](styling-nativewind-v4-expo/SKILL.md) | [PR #7](https://github.com/tristanmanchester/agent-skills/pull/7) |
| [textual-tui](textual-tui/SKILL.md) | Review outstanding |
| [todoist-api](todoist-api/SKILL.md) | [PR #11](https://github.com/tristanmanchester/agent-skills/pull/11) |
| [track17](track17/SKILL.md) | [PR #4](https://github.com/tristanmanchester/agent-skills/pull/4) |
| [tracking-pettracer-location](tracking-pettracer-location/SKILL.md) | Review outstanding |
| [wordly-wisdom](wordly-wisdom/SKILL.md) | Review outstanding |
| [write-good-docs](write-good-docs/SKILL.md) | [PR #22](https://github.com/tristanmanchester/agent-skills/pull/22) |

## Contributing

Follow the [Agent Skills format](https://agentskills.io/specification): precise
activation, concise task instructions, and supporting material loaded when useful.
Preserve useful methods and tested helpers; remove obsolete interfaces rather than
adding compatibility layers to new skill designs. Verify factual changes against
current primary sources and record the exact tests actually run.

Keep one skill's changes in one PR. Repository-wide catalogue or maintenance work
belongs in a separate PR. A parser check, fixture file, mocked test, or published
PR is not evidence of a successful live provider call or improved agent output.
