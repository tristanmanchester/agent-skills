# Write good docs

Version **2.1.0** is an agent skill for writing, editing, and reviewing technical documentation. It combines Google-derived house style with evidence-preserving editing, reader-oriented structure, and guidance against formulaic or unsupported prose.

## Install or replace the skill

Extract the archive and place the enclosed `write-good-docs` directory in your agent's configured skills location. Keep the directory name unchanged and preserve its `SKILL.md` and relative reference paths. Follow your host's installation or reload procedure; this package does not depend on a particular agent client.

For an upgrade, keep a backup of the old version outside the agent's active skill-discovery location, then replace its `write-good-docs` directory with this one. Do not keep two active versions with the same skill name.

Ordinary writing needs only [SKILL.md](SKILL.md) and the files in `references/`. Maintenance scripts are optional, require Python 3.10 or later, and use only the standard library. They do not contact model APIs or execute commands appearing in documentation fixtures.

## Use it

Ask the agent to use `write-good-docs` for a documentation task. For example:

> Use write-good-docs to improve this README. Preserve commands and product facts; fix the reader path and unnecessary repetition.

Explicit invocation also applies compatible prose and fidelity rules to other nonfiction formats without imposing documentation sections:

> Use write-good-docs to tighten this email summary. Keep the finding and its material uncertainty in one paragraph.

Automatic activation remains focused on technical documentation and findings reports. Translation-only tasks, ordinary emails, chat explanations, and marketing do not automatically activate it. User instructions and coherent project conventions override the fallback American English and other house-style preferences.

## What changed

The revision distinguishes prose-only edits from evidence-enriched rewrites, matches authority to the kind of claim, and makes every teaching example evidence-complete. It adds direct uncertainty, supported causal implications, connected paragraphs, preservation of good existing writing, and a findings-report route. Reference loading is decision-based, and the core is shorter than the supplied v2.0.0 core.

See [the changelog](CHANGELOG.md) for the full change list and [attribution](ATTRIBUTION.md) for sources and licensing.

## Validate and evaluate

From this directory:

```sh
python3 scripts/check_package.py
python3 -m unittest discover -s evals/tests -v
```

The package includes 20 fixed writing cases, 32 routing probes, a case exporter, and mechanical output checks. See [the evaluation workflow](evals/README.md). Generated outputs must also pass semantic and safety review; style scores cannot offset a material correctness failure.

The shipped [validation record](VALIDATION.md) covers package and maintenance-tool checks. No no-skill/v2.0.0/v2.1.0 model-output comparison has been run for this release. Treat improvements in generated prose as a hypothesis to test, not a reported benchmark result.

`MANIFEST.json` records the byte size and SHA-256 hash of each other shipped file. The package checker verifies it when present. After intentional local edits, it will report a mismatch against the released package. For a development checkout, move the old manifest outside the skill directory; restore or regenerate a manifest when distributing a new frozen release. The manifest detects changes relative to itself; it is not a signed authenticity guarantee.
