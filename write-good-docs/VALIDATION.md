# Validation record

Version: **2.1.0**. Date: **September 13, 2026**.

## Checks performed

The package was checked locally with:

```sh
python3 scripts/check_package.py
python3 -m unittest discover -s evals/tests -v
```

The structural check passed for the package's simple frontmatter layout, naming and version consistency, local Markdown file targets and applicable anchors, the 20 case definitions and their supplied fixtures, and the release manifest. All **36 maintenance-tool unit tests passed**.

The tests cover case loading, writer/rubric separation, overwrite refusal, relative path safety, output outside the skill directory, protected literals, exact-text preservation, platform line-ending normalization, local edit boundaries, warning repetition and ordering, explicit format/length constraints, error handling, local-link checks, and manifest mutation detection.

One test deliberately supplies an unsupported claim that contains all required literal tokens. It confirms that the tool reports only a mechanical pass and still requires semantic review. Mechanical checks do not establish factual or stylistic quality.

The archive was extracted into a fresh directory and the same package and unit-test checks were repeated. ZIP integrity and the extracted file hashes were checked. No macOS resource-fork entries, temporary build files, Python bytecode, or model-run outputs are included.

## Editorial inspection

The source package and supplied review were read before revision. The revised instructions and examples were checked for contradictory authority rules, unsupported enrichment, modality drift, destructive-validation authorization, and overgeneralized prose restrictions. Selected primary guidance was rechecked as recorded in the source map; inherited external links were not comprehensively re-audited.

## Not performed

No controlled comparison of model-generated output with no skill, v2.0.0, and v2.1.0 was run. The 20 writing cases and 32 routing probes are supplied for that comparison, not reported as passed model evaluations. Generated prose, automatic activation, actual reference-loading cost, and model-dependent behavior remain to be evaluated on the target agents.

The package checker is intentionally small. It validates the frontmatter and Markdown conventions used by this package, not arbitrary YAML syntax or every renderer's anchor algorithm. Hashes detect changes relative to the manifest; the manifest is not signed proof of origin.
