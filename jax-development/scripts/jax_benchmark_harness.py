#!/usr/bin/env python3
"""Benchmark fresh, independent JAX inputs. Imports and executes trusted project code."""
from __future__ import annotations
import argparse
import contextlib
import importlib.util
import json
from pathlib import Path
import statistics
import sys
import time


def measure(fn, make_inputs, jax, *, repeat=10, warmup=1):
    """Factory returns (positional args, keyword args), with fresh donated buffers."""
    if type(repeat) is not int or repeat < 1 or type(warmup) is not int or warmup < 0:
        raise ValueError('repeat must be positive; warmup must be nonnegative')
    if not callable(fn) or not callable(make_inputs):
        raise TypeError('Function and input factory must be callable')

    def once():
        args, kwargs = make_inputs()
        if not isinstance(args, (tuple, list)) or not isinstance(kwargs, dict):
            raise TypeError('Input factory must return (args sequence, kwargs dictionary)')
        # Preparation/transfers are excluded. Blocking errors must propagate.
        jax.block_until_ready((args, kwargs))
        start = time.perf_counter()
        result = fn(*args, **kwargs)
        jax.block_until_ready(result)
        return (time.perf_counter() - start) * 1000

    first = once()
    for _ in range(warmup):
        once()
    samples = [once() for _ in range(repeat)]
    return {'first_call_ms': first, 'times_ms': samples,
            'median_ms': statistics.median(samples), 'min_ms': min(samples),
            'max_ms': max(samples), 'stdev_ms': statistics.pstdev(samples),
            'input_preparation_timed': False, 'output_synchronisation_timed': True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--file', type=Path, required=True)
    parser.add_argument('--function', required=True)
    parser.add_argument('--factory', required=True, help='No-argument function returning fresh (args, kwargs)')
    parser.add_argument('--jit', action='store_true')
    parser.add_argument('--static-argnums', default='')
    parser.add_argument('--donate-argnums', default='')
    parser.add_argument('--repeat', type=int, default=10)
    parser.add_argument('--warmup', type=int, default=1)
    options = parser.parse_args()
    try:
        if not options.jit and (options.static_argnums or options.donate_argnums):
            raise ValueError('Static/donation options require --jit')
        if options.repeat < 1 or options.warmup < 0:
            raise ValueError('Invalid repeat/warmup count')
        # Keep stdout machine-readable even when the imported module prints.
        with contextlib.redirect_stdout(sys.stderr):
            import jax
            import jaxlib
            spec = importlib.util.spec_from_file_location('_jax_benchmark_target', options.file.resolve())
            if spec is None or spec.loader is None:
                raise ImportError('Cannot load benchmark module')
            module = importlib.util.module_from_spec(spec)
            sys.modules[spec.name] = module
            spec.loader.exec_module(module)
            fn, factory = getattr(module, options.function), getattr(module, options.factory)
            indices = lambda text: tuple(int(x.strip()) for x in text.split(',') if x.strip())
            if options.jit:
                fn = jax.jit(fn, static_argnums=indices(options.static_argnums),
                             donate_argnums=indices(options.donate_argnums))
            report = measure(fn, factory, jax, repeat=options.repeat, warmup=options.warmup)
            report.update(jax=jax.__version__, jaxlib=jaxlib.__version__,
                          python=sys.version.split()[0], backend=jax.default_backend(),
                          devices=[str(d) for d in jax.devices()], jit=options.jit,
                          factory=options.factory, repeat=options.repeat, warmup=options.warmup,
                          note='Independent-input latency, not chained training throughput or isolated compilation time')
        print(json.dumps(report, indent=2))
        return 0
    except Exception as error:
        print(json.dumps({'ok': False, 'error': f'{type(error).__name__}: {error}'}), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
