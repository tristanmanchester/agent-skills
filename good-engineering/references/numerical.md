# Numerical and scientific code

In numerical code a wrong answer usually looks like a plausible answer. The standards
here exist so that results are checked against something other than themselves.

Contents: conventions at the boundary · tests · tolerances · accuracy claims · JAX ·
NumPy · PyTorch · measurement · research vs library code

## Conventions at the boundary

- **One public axis convention.** Pick one (`(z, y, x)` volumes, `(view, v, u)`
  projections) for everything callers see, and convert at the I/O boundary. Internally,
  a kernel may want a transposed, blocked or packed layout. That is a legitimate
  performance choice, as long as one module owns the conversion and tests it, and
  callers never have to manage it.
- **Units and frames are part of the interface.** Every public parameter with a
  physical meaning documents its unit and frame: `pixel_size_mm`, angles in radians,
  the detector frame's origin and handedness. Put units in names when it is ambiguous.
- **Results carry their context.** Return a volume with its geometry, voxel size and
  the settings that made it, not a bare array plus metadata the caller must keep in sync.
- **Validate before expensive work.** Check shapes, dtypes and finiteness at the public
  entry point and raise a clear error, so a bad input fails in milliseconds rather than
  after a GPU hour. Don't add guards for inputs that already raise, and don't engineer
  for magnitudes that never occur in real data. Non-finite output is not a loud failure:
  NaNs flow silently through a pipeline. Decide whether NaN means "invalid input"
  (reject it), "missing data" (document it), or a bug (find it).

## Tests

Use independent oracles; see [testing](testing.md). For numerics, that means:

- **Adjoint test** for every linear operator pair, across representative geometries
  and inputs. With random `x` and `y`, the normalised residual
  `|<A x, y> - <x, Aᵀ y>| / (‖A x‖ ‖y‖)` should be rounding noise. Choose the
  tolerance for the working precision and the operations involved, and confirm the
  working dtype is what you think it is: JAX stays in float32, with only a warning,
  unless x64 is enabled.
  Then perturb the adjoint slightly (scale one view, shift by half a pixel) and check the
  test fails: a small mismatch can hide under a loose tolerance or a lucky input. An
  inexact adjoint corrupts gradients and undermines solver convergence.

  ```python
  def test_backproject_is_adjoint_of_project(geom, key):
      kx, ky = jax.random.split(key)
      x = jax.random.normal(kx, geom.volume_shape)
      y = jax.random.normal(ky, geom.projection_shape)
      ax = project(geom, x)
      lhs = jnp.vdot(ax, y)
      rhs = jnp.vdot(x, backproject(geom, y))
      scale = jnp.linalg.norm(ax) * jnp.linalg.norm(y)
      assert abs(lhs - rhs) / scale < TOL  # set from measured float32 noise on these geometries
  ```

- **Analytic cases.** The line integral through a disc of radius `r` at offset `d` is
  `2·sqrt(r² − d²)`. Integrals of polynomials, steady states of linear systems and
  rotations by known angles all have closed forms. Use them.
- **Dense reference on a tiny problem.** Build the operator a second, independent way
  (exact intersection lengths, an explicit matrix from first principles, a brute-force
  sum) on an 8×6 grid with 5 angles, and compare. Building the matrix by applying the
  operator to basis vectors is not independent; it checks the operator against itself.
- **Inputs that expose axis and sign bugs.** Use asymmetric phantoms, non-square and
  odd sizes, anisotropic voxels, an off-centre rotation axis, and angles that aren't
  multiples of 90°. A centred sphere on a cube passes with x and y swapped.
- **Gradient checks.** Compare autodiff with finite differences
  (`jax.test_util.check_grads(f, (x,), order=2)`), and always test custom VJPs and
  hand-written gradients this way.
- **Convergence order.** For a discretisation, halve the step and check the error
  falls at the expected rate. This catches bugs that a single resolution hides.
- **Statistical code**: fixed seeds, several of them, and a tolerance derived from the
  known variance, not from one lucky run.
- **Every parameter that scales the answer gets a test at a non-default value.**
  Pixel size, detector spacing, step size and units all default to 1, and a test suite
  that only uses 1 can't see a missing scale factor. Test each one at 0.5 or 2 against
  an analytic result.
- **Rays and samples exactly on cell edges and corners.** Axis-aligned rays at integer
  offsets and 45° rays through grid corners are where tracers double-count, drop or
  misassign length. Choose a convention, such as splitting evenly between neighbours
  (symmetric) or half-open cells (simple), apply it consistently despite floating-point
  noise, document it, and test it.

## Tolerances

A tolerance says how much error you expect and why. Base it on the precision, the
algorithm, the conditioning, the normalisation and any discretisation error. Then
calibrate it on representative cases against a higher-precision or independent
reference, and say in a comment what error it allows. For orientation: float32
epsilon is about 1.2e-7 and float64 about 2.2e-16. The worst-case summation error of
`n` terms grows with `n` for a naive loop and with `log2(n)` for balanced pairwise
summation, with typical errors smaller than that. Cancellation and ill-conditioning
can dominate both. NumPy doesn't use pairwise summation along every axis and layout,
so check the reduction you actually use.

- `np.testing.assert_allclose(actual, expected, rtol=..., atol=...)` with both values
  explicit. The defaults differ between `np.allclose` (`rtol=1e-5, atol=1e-8`) and
  `assert_allclose` (`rtol=1e-7, atol=0`), and near zero only `atol` matters.
- A failing tolerance is a finding. Find the error source before touching the number.

## Accuracy claims

- **A lower residual is not a more accurate result.** Residuals fall when a method fits
  noise. Check error against ground truth (a phantom, a held-out acquisition, a known
  pose) whenever you claim an improvement.
- **Speed only counts at equal quality.** Report time and accuracy together.
- **General, not tuned.** An improvement must hold across geometries and datasets, not
  just the benchmark phantom. Hold out cases you didn't tune on.
- **Fix the method, don't wrap it.** If an estimator is biased on some inputs, fix its
  model, weighting or regularisation. A guard that detects the case and discards the
  result hides the bias and fails at the threshold.

## JAX

- `jit` retraces on every new shape, dtype or static argument. Keep shapes stable in
  hot loops, and mark configuration arguments `static_argnames`.
- Python side effects inside `jit` run once at trace time. Use `jax.debug.print` and
  `jax.debug.callback`.
- Python `if` and `for` on traced values fail or unroll. Use `lax.cond`, `lax.fori_loop`,
  `lax.scan` and `jnp.where`.
- **Out-of-bounds indexing doesn't raise**: gathers clamp the index and scatters drop
  the update. Check index ranges yourself.
- Arrays are immutable: `x = x.at[i].set(v)`.
- PRNG keys are explicit. Reusing a key repeats the randomness, so `split` for every
  consumer.
- Float64 needs `jax.config.update("jax_enable_x64", True)` before arrays are created.
  Without it, `float64` requests become `float32` with nothing more than a warning.
- Debug NaNs with `jax.config.update("jax_debug_nans", True)`.
- Dispatch is asynchronous. Time with `.block_until_ready()`, or you measure dispatch,
  not compute.

## NumPy

- Broadcasting succeeds silently on the wrong shapes: `(n,)` minus `(n, 1)` is
  `(n, n)`. Validate shapes at public entry points and raise `ValueError`. Internally,
  give array variables names or annotations that carry their shape.
- Basic slices are views, and fancy indexing makes copies. Writing through a view
  changes the caller's array; copy before mutating inputs.
- Integer image data (`uint8`, `uint16`) wraps on overflow. Convert to float before
  arithmetic.
- NaN compares false with everything and spreads through reductions. `nanmean` and
  friends hide the NaN rather than fixing its cause.
- Prefer vectorised operations to Python loops; a loop over pixels is a bug in
  performance-sensitive code.

## PyTorch

- Time GPU work after `torch.cuda.synchronize()`.
- Wrap evaluation in `torch.inference_mode()` and set `model.eval()`; dropout and batch
  norm behave differently in training mode.
- In-place ops on tensors that autograd needs raise errors or corrupt gradients. Avoid
  `x += ...` on anything that requires grad.

## Measurement

- Separate cold time (fresh process, including compile) from warm time. Report the
  median of several runs and peak device memory.
- Compare methods under one protocol on the same hardware. Never mix numbers from
  different timing protocols.
- Record the command, commit, date and hardware for each headline number so anyone can
  rerun it. Keep raw results out of the repo; keep the recipe in it.

## Research code vs library code

Notebooks, benchmark drivers and exploration scripts can be scrappy. They live
outside the installed package and are never imported by it. Anything the library
ships follows every rule in this skill.
