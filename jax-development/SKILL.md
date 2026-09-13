---
name: jax-development
description: >-
  Write, debug, review, profile, or shard JAX numerical code. Use when the hard
  part is JAX tracing, autodiff, control flow, PRNGs, compilation, array placement,
  or runtime performance. Do not impose JAX on a NumPy-only or unrelated GPU task.
compatibility: Current-release baseline JAX 0.11.1 requires Python >=3.12; wheel/backend support must be checked separately. Diagnostics need Python 3.12+ and the project's JAX environment for runtime probes. Static helpers can run without JAX. Benchmark/probe commands execute trusted project code.
metadata:
  version: "3.0.0"
  reviewed: "2026-09-13"
  source: "https://github.com/jax-ml/jax/tree/jax-v0.11.1"
---

# JAX development

Make the mathematical contract explicit before changing transformations or kernels.
Record shapes, dtypes, numerical tolerances, randomness, differentiability, and
required backend. Preserve useful existing architecture; a new API does not itself
justify a rewrite. Use current public interfaces rather than compatibility shims.

## Inspect, reproduce, measure

Resolve `SKILL_DIR` to the directory containing this file. Bundled scripts live
there, not in the target project's `scripts/`. Run them in the project's actual
Python environment. Inspect each script's help before use.

```bash
python "$SKILL_DIR/scripts/jax_env_report.py" --format json
python "$SKILL_DIR/scripts/jax_project_scan.py" /absolute/project --format json
python "$SKILL_DIR/scripts/jax_compile_probe.py" --help
python "$SKILL_DIR/scripts/jax_recompile_explorer.py" --help
```

Environment probing initialises the backend and can allocate resources. The
report lists relevant environment variable names, never their values, and returns
nonzero for import/backend/smoke-test failure. It is not an exhaustive secret
scanner: review paths, devices, and private project output before sharing.
Static scans produce leads, not proof that a transformation is wrong. Importing,
tracing, lowering, and benchmarking a module execute code; use trusted inputs.

Reduce failures to the smallest reproducer retaining the relevant shape, dtype,
static argument, transform order, and backend. Compare against a simple reference
and check numerical/gradient invariants before measuring speed. Change one
hypothesis at a time and record the observed result.

## Select the relevant reference

- Tracing, shapes, pytrees: [mental model](references/MENTAL-MODEL.md),
  [transform decisions](references/TRANSFORM-DECISION-MATRIX.md), and
  [porting patterns](references/PORTING-PATTERNS.md).
- Correctness: [debugging](references/DEBUGGING-TRIAGE.md) and
  [review rubric](references/CODE-REVIEW-RUBRIC.md).
- Timing, compilation, memory: [performance](references/PERFORMANCE-PLAYBOOK.md).
- Placement, collectives, multi-host: [sharding](references/SHARDING-PLAYBOOK.md).
- Custom derivatives, export, Pallas, FFI: [extensions](references/ADVANCED-EXTENSIONS.md).
- Source-level diagnosis: [repo map](references/REPO-MAP.md),
  [workflow](references/EXPERT-WORKFLOW.md), and [source baseline](references/SOURCES.md).

The source baseline records current changes that affect these longer references.
Check the installed release rather than treating online `latest`/unreleased docs
as the API of a locked project. Useful templates and reproducer/evaluation assets
remain bundled; run selected examples against the target environment.

## Correctness and performance rules

Keep ordinary transformed functions pure; explicit `jax.ref` state is a separate
supported model with its own transform/effect restrictions, not permission for
hidden Python mutation. Thread typed PRNG keys and avoid reuse. Use structured
control flow for traced decisions; static Python loops can be appropriate when
small, so do not mechanically replace every loop with `scan`.

Keep host transfers and synchronisation deliberate. Separate input preparation,
trace/compile, dispatch, device execution, output materialisation, and communication.
Check x64 and matmul precision explicitly. `jax.numpy.empty` no longer promises
zero-initialised storage on the current release; use zeros when zeros are needed.

Donation consumes input buffers. For independent timing trials, construct fresh
inputs for every call; never reuse a donated warm-up argument. The benchmark
harness now requires an input factory and propagates synchronisation errors:

```bash
python "$SKILL_DIR/scripts/jax_benchmark_harness.py" \
  --file /absolute/project/benchmark_case.py --function step --factory make_inputs \
  --jit --donate-argnums 0 --repeat 20
```

`make_inputs()` returns `(args, kwargs)` with equivalent, fresh inputs. Preparation
and its synchronisation are outside the timer; output synchronisation is inside.
Keep shapes/dtypes/shardings/static values fixed and verify outputs separately.
First-call time includes compilation/execution and may use caches; it is not pure
compile time. For stateful training throughput, write a separate benchmark carrying
returned state forward, and report that different workload. No old JSON/arrayify
or unsafe donation compatibility path remains.

Prefer global-view code with deliberate sharding before manual `shard_map` when
it meets the objective. `NamedSharding` placement is not synonymous with explicit
sharding-in-types. Current mesh context uses `jax.set_mesh(mesh)`, not `with mesh`.
Test global/local shapes, replication, collectives, gradients, and output sharding;
a one-device run cannot validate multi-host communication.

## Finish with evidence

Return the diagnosis, patch/example, correctness checks, measured timings with
hardware and workload, and remaining backend limitations. Do not claim benchmarks
or compilation succeeded when a helper returned partial/error output. For helper
regressions run `python -m unittest discover -s "$SKILL_DIR/tests" -v`.
