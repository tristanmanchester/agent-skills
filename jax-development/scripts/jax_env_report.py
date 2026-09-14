#!/usr/bin/env python3
"""Report versions/devices without dumping environment values. Backend probing initialises JAX."""
from __future__ import annotations
import argparse
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import sys


def build_report(smoke=False):
    packages, package_errors = {}, {}
    for name in ('jax', 'jaxlib', 'numpy', 'scipy', 'flax', 'optax', 'equinox', 'orbax-checkpoint'):
        try: packages[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError: packages[name] = None
        except Exception as error:
            packages[name] = None
            package_errors[name] = type(error).__name__
    report = {'ok': False, 'python': platform.python_version(), 'platform': platform.platform(),
              'packages': packages, 'package_errors': package_errors, 'environment_names_only': sorted(
                  k for k in os.environ if k.startswith(('JAX_', 'XLA_', 'CUDA_', 'NVIDIA_', 'NCCL_', 'TPU', 'ROCM', 'HIP_')))}
    try:
        import jax
        import jax.numpy as jnp
        report.update(backend=jax.default_backend(), devices=[str(d) for d in jax.devices()],
                      process_count=jax.process_count(), process_index=jax.process_index(),
                      x64=bool(jax.config.jax_enable_x64))
        if smoke:
            x = jnp.arange(8, dtype=jnp.float32)
            output = jax.jit(lambda a: a + 1)(x)
            jax.block_until_ready(output)
            report['smoke_test'] = {'ok': bool(jnp.all(output == x + 1)), 'scope': 'small compiled addition'}
            if not report['smoke_test']['ok']: return report
        report['ok'] = not package_errors
    except Exception as error:
        # Exception messages may contain paths, endpoint addresses, or configuration values.
        report['error_type'] = type(error).__name__
        report['next_step'] = 'Inspect the original import/backend error privately in the target environment'
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--smoke-test', action='store_true')
    parser.add_argument('--format', choices=('json', 'text'), default='json')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    report = build_report(args.smoke_test)
    text = json.dumps(report, indent=2) if args.format == 'json' else '\n'.join(f'{k}: {v}' for k, v in report.items())
    try:
        if args.output:
            descriptor = os.open(args.output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            with os.fdopen(descriptor, 'w', encoding='utf-8') as stream: stream.write(text + '\n')
        else: print(text)
    except OSError as error:
        print(json.dumps({'ok': False, 'error_type': type(error).__name__}), file=sys.stderr)
        return 2
    return 0 if report['ok'] else 2


if __name__ == '__main__': raise SystemExit(main())
