# Performance playbook

## Separate the costs

State the workload and reference implementation, then distinguish host preparation,
transfer, trace/lowering/compilation, dispatch, execution, materialisation, and
communication. Validate numerical outputs and gradients before optimising. Record
backend/devices, versions, shapes, dtypes, precision, sharding, and cache state.

## Benchmark independent inputs

The bundled `scripts/jax_benchmark_harness.py` imports a trusted module exposing
a function and a zero-argument input factory. Example target module:

```python
import jax.numpy as jnp

def step(x):
    return x + 1

def make_inputs():
    return (jnp.arange(1024, dtype=jnp.float32),), {}
```

Use `--file PATH --function step --factory make_inputs --jit --repeat 20`.
The factory must return fresh equivalent buffers for every invocation, including
warm-up and first call. This makes explicit `--donate-argnums 0` possible without
reusing invalidated arrays. Static arguments must remain stable; setup itself
must not dominate memory or change the workload. The helper does not detect every
aliasing mistake in user factories.

Inputs are synchronised outside timing; results are synchronised inside. Any
failure propagates rather than returning a plausible timing. Report median,
spread and raw samples, not only the fastest run. First-call time mixes multiple
costs and can hit caches. Use lower/compile probes or separate controlled processes
when isolated compilation/cold-cache measurements matter. A pre-jitted callable
can consume donated inputs even without the harness's `--jit` option.

A training loop is a different workload: carry the returned state into the next
iteration, use fresh batches/keys, and separate warm-up from steady-state throughput.
Do not keep resetting it and label the independent-input result training throughput.
For eager/JIT comparison, use separate fresh-input runs and compare correctness
and workload equivalence; donation invalidates shared comparison inputs too.

## Diagnose before rewriting

Repeated compilations: inspect changing shape/dtype/sharding/static values,
new closures/jitted functions, large captured constants and Python-loop unrolling.
Use the compile probe/recompile explorer as diagnostic aids and confirm with
compilation logs/traces; a signature heuristic is not an authoritative compile count.

Slow execution: inspect host conversions, tiny kernel dispatches, callbacks,
input starvation, resharding, and redundant computation. Consider larger compiled
regions, batching and structured loops only against an actual profile.

Memory pressure: measure live buffers and peaks, examine retained outputs,
replication, intermediates and autodiff residuals. Donation and checkpointing
have semantics and compute/memory trade-offs; neither is an automatic speed-up.
Use `jax.checkpoint` before experimental alternatives unless evidence favours them.

Synchronise trace windows, capture realistic iterations, and use the target
accelerator's profiler. CPU smoke tests cannot establish GPU/TPU throughput or
multi-host correctness. A persistent cache helps repeated compilation but must
be trusted and its warm/cold status included in measurements.

See [source baseline](SOURCES.md) for current APIs and official references.
