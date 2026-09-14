# Source baseline and maintenance

Reviewed 2026-09-13. The public release baseline is **JAX 0.11.1**, released
2026-08-17, whose PyPI metadata requires Python **>=3.12**. There is no blanket
upper bound in that metadata; this does not guarantee wheels/backend support for
every future interpreter. Check jaxlib, accelerator plugin, driver, and platform
requirements separately. Python 3.13 free-threaded support was dropped in 0.11.0;
do not conflate it with ordinary CPython 3.13.

Traceable upstream source: tag `jax-v0.11.1`, commit
`2d66622450e2c8633cda2307688ef7aa294bd6eb` in `jax-ml/jax`. This supersedes the
unidentified `jax-main.zip` provenance claim; it does not assert every bundled
example came from that tag or that a current-version runtime test was performed.

## Current changes relevant to the retained references

- Prefer `with jax.set_mesh(mesh):`; the old Mesh context is deprecated.
- `NamedSharding` is a placement object. Explicit sharding-in-types requires the
  appropriate mesh axis types and propagation rules; merely constructing this
  object is not enough to claim explicit-mode semantics.
- Ordinary pure-function design remains a useful default. Public `jax.ref` offers
  explicit stateful arrays with defined effects; inspect its rules for transforms,
  autodiff, and lifetimes rather than categorically banning all state.
- `jnp.empty`/`empty_like` are uninitialised in 0.11.0+, not zero constructors.
- Current export deserialisation checks its compatibility window. Keep provenance,
  producer/consumer versions and actual load/execute tests; do not bypass expiry
  errors to pretend an artefact is still supported. Prefer `in_shardings_jax` and
  `out_shardings_jax` over the deprecated HLO sharding fields.
- Many `jax.core`/`jax.interpreters` internals were removed. Use public interfaces
  and documented `jax.extend` where appropriate; match source-level debugging to
  the exact installed commit. Experimental hijax, Pallas, and custom rematerialisation
  are targeted tools, not obligatory rewrites for every numerical function.
- A persistent compilation cache is trusted executable infrastructure. Do not
  use a cache directory writable by untrusted users or accept arbitrary exported
  executables as inert data.

## Primary references

- [Package metadata](https://pypi.org/project/jax/)
- [Release-tag source](https://github.com/jax-ml/jax/tree/jax-v0.11.1)
- [Changelog](https://docs.jax.dev/en/latest/changelog.html)
- [Installation](https://docs.jax.dev/en/latest/installation.html)
- [Donation](https://docs.jax.dev/en/latest/buffer_donation.html)
- [Benchmarking](https://docs.jax.dev/en/latest/benchmarking.html)
- [Export](https://docs.jax.dev/en/latest/export/export.html)
- [Refs](https://docs.jax.dev/en/latest/array_refs.html)
- [Compilation cache](https://docs.jax.dev/en/latest/persistent_compilation_cache.html)

For maintenance, identify the latest stable release, read its versioned changes,
then inspect the exact changed method/types. Do not copy unreleased examples into
stable guidance. Test selected numerical templates, backend features, and helper
failure paths, recording the runtime actually used. Keep static scan/evaluation
fixtures separate from measured runtime evidence.
