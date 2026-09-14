---
name: textual-tui
description: >-
  Build, debug, test, or package Python Textual terminal interfaces: screens,
  widgets, TCSS, reactive state, workers, keyboard workflows, and optional browser
  delivery. Use when Textual is selected or an existing Textual app is involved;
  do not turn a noninteractive CLI or simple Rich output into a TUI unnecessarily.
license: Proprietary
compatibility: Textual currently supports Python >=3.9,<4. Use the project's locked Textual and developer-tool versions. Bundled scaffold checks parse source without importing the generated application; runtime tests need Textual and the app's dependencies.
metadata:
  version: "3.0.0"
  reviewed: "2026-09-13"
---

# Textual applications

Inspect the app, locked dependencies, entry point, TCSS, tests, and actual user
workflow. Choose built-in widgets and composition before custom rendering. Keep
application state separate from long-running work and make keyboard paths first-
class. Do not require a dashboard, mode system, or command palette for every app.

## Choose a structure

A small tool can keep one App; separate Screens when the user's context changes,
ModalScreen for short interruptions, ContentSwitcher for local steps, and modes
for genuinely independent top-level screen stacks. Use stable IDs and semantic
classes for styling and tests, with narrow-terminal layouts before wider panes.
Prefer DataTable, Tree/DirectoryTree, MarkdownViewer, TextArea, and built-in input
widgets when their behaviour fits. Do not split a cohesive component merely to
satisfy a line-count heuristic.

Read [architecture](references/architecture-decision-tree.md),
[widgets](references/widget-selection-atlas.md), or
[screens](references/screens-modes-command-palette.md) only as needed.

## Responsive work and state

Read [reactivity and workers](references/reactivity-and-workers.md) before changing
concurrent behaviour. Async workers share the event loop: blocking calls do not
become nonblocking when wrapped in async def or @work. Use async APIs, thread=True
for blocking I/O, and a suitable process/native strategy for substantial CPU work.

Exclusive cancellation is not a transaction rollback or a guarantee that a thread
has stopped. Carry a request revision and check it again when applying results on
the UI thread. Keep worker failure, cancellation, empty data, and successful data
distinct. A cancelled remote write may still have happened.

reactive controls refresh-related state; var retains reactive features without
automatic refresh/layout. Neither is a substitute for a plain field where reactive
behaviour is unnecessary. Keep compute methods cheap and pure, and watchers free
of blocking work. Initialise pre-mount reactive values deliberately.

## Existing projects and source tools

Resolve SKILL_DIR to this installed skill directory, not the app repository.
The inspect/audit helpers provide heuristic source leads, not proof of architecture,
responsive runtime behaviour, or missing capabilities. Read flagged code before
changing it. Do not add palette/browser/export/breakpoint machinery only to clear
a heuristic warning.

`dump_dom_and_bindings.py` imports and runs the application under run_test; it can
execute startup/network/filesystem actions. Run it only in an authorised isolated
test environment with fake services and suitable configuration. It is not a passive
source read. The same applies to generated Pilot tests and snapshot tooling.

## Safe scaffolding

The starter templates remain available, but generation now previews by default:

```bash
python "$SKILL_DIR/scripts/scaffold_textual_app.py" --list-templates
python "$SKILL_DIR/scripts/scaffold_textual_app.py" \
  --template data-explorer --module my_app --class-name MyApp --app-title 'My App'
```

Review the rendered app, TCSS, and tests. To write, add `--write --output-dir` with
a new final directory whose parent already exists. There is no force/overwrite or
automatic pyproject/CI option. Free titles are inserted as AST string values,
identifiers are validated, and all selected templates are parsed before any write.
Generated Python is reformatted by ast.unparse, not executed. A write failure can
leave a private partial draft; it is not an atomic multi-file transaction.

For the chat starter, read [request ownership and tests](references/chat-template.md).
Its explicit Stop action, draft preservation, and late-result checks are part of
the supplied example, not behaviour to infer from the worker decorator.

Integrate selected output deliberately into the app. Review packaging/CI against
the existing project and current supported Python/tool versions rather than copying
a new universal build system. Older standalone emit helpers are optional starting
scaffolds, not a current dependency/CI policy or automatic upgrade path.

## Runtime, delivery, and testing

Use the installed textual-dev CLI help for devtools/console/serve. Serving exposes
a server-side app with its filesystem and service permissions; it is not a sandbox
or automatic authentication boundary. Verify network binding, auth, tenant isolation,
and the exact files offered for download before browser delivery. Treat user text
and terminal/markup escapes as untrusted display data.

Test the changed behaviour with run_test/Pilot, including actual assertions, failure/
cancellation, focus and keyboard actions, narrow/wide sizes, and teardown. Use
snapshots when visual layout is the relevant risk, not a mandatory quota for every
change. Fixed sleeps are not proof a worker or layout settled; await a bounded
observable state. Headless tests do not prove every real terminal/browser renders
identically. Preserve the user's scroll position rather than always auto-anchoring
logs when they are reading earlier content.

Report the patch, actual test commands/results, and untested terminal/browser paths.
Do not claim a starter, syntactic parse, or golden screenshot proves production
readiness. Keep [testing](references/testing-matrix.md),
[browser delivery](references/browser-and-delivery.md), and
[packaging](references/packaging-and-ci.md) as targeted references.

Maintainers: `python "$SKILL_DIR/scripts/self_check.py"` parses all local starter
outputs; `python -m unittest discover -s "$SKILL_DIR/tests" -v` tests the scaffold
engine. Neither executes generated apps.

Sources reviewed 2026-09-13: [Textual metadata](https://pypi.org/project/textual/),
[workers](https://textual.textualize.io/guide/workers/),
[reactivity](https://textual.textualize.io/guide/reactivity/), and
[testing](https://textual.textualize.io/guide/testing/).
