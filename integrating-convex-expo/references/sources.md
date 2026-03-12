# Sources used to rewrite this skill

Checked or reviewed on 2026-03-12.

## Agent Skills guidance

- Agent Skills specification
- Optimizing skill descriptions
- Evaluating skills
- Using scripts
- The complete skill-building guide supplied with this task

## Convex and Expo guidance

- Expo guide for using Convex
- Convex React Native and deployment URL docs
- Convex validation, actions, internal functions, error handling, and pagination docs
- Convex best practices and ESLint docs
- Convex Clerk integration docs
- Convex Auth docs
- Convex file upload guidance
- Convex blog post on uploading files from React Native or Expo

## Local plugin inputs folded into this rewrite

From the attached `convex-agent-plugins` repository, the rewrite incorporates guidance inspired by:

- `argument-validation.mdc`
- `async-handling.mdc`
- `authentication-checks.mdc`
- `custom-functions-for-auth.mdc`
- `function-organization.mdc`
- `no-date-now-in-queries.mdc`
- `query-optimization.mdc`
- `schema-design.mdc`
- `use-components-for-encapsulation.mdc`
- `use-eslint-always.mdc`
- `use-node-for-actions.mdc`
- `use-pagination-for-large-datasets.mdc`

and the bundled skills:

- `auth-setup`
- `components-guide`
- `convex-helpers-guide`
- `convex-quickstart`
- `function-creator`
- `migration-helper`
- `schema-builder`

## Intent of the rewrite

This skill deliberately tightens:

- frontmatter quality and trigger specificity,
- progressive disclosure through references,
- script interfaces for agentic use,
- Convex safety defaults,
- Expo-specific environment handling,
- and evaluation scaffolding.
