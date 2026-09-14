import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('bench', Path(__file__).parents[1] / 'scripts/jax_benchmark_harness.py')
bench = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bench)

class FakeJax:
    def __init__(self): self.blocks = []
    def block_until_ready(self, value): self.blocks.append(value)

class BenchmarkTests(unittest.TestCase):
    def test_fresh_inputs_for_every_call(self):
        created = []
        def factory():
            value = {'used': False}
            created.append(value)
            return ([value], {})
        def donated(value):
            self.assertFalse(value['used'])
            value['used'] = True
            return {'result': 1}
        fake = FakeJax()
        result = bench.measure(donated, factory, fake, repeat=3, warmup=2)
        self.assertEqual(len(created), 6)
        self.assertEqual(len(fake.blocks), 12)
        self.assertEqual(len(result['times_ms']), 3)
    def test_block_failure_is_not_swallowed(self):
        class Broken:
            def block_until_ready(self, value): raise RuntimeError('device failure')
        with self.assertRaisesRegex(RuntimeError, 'device failure'):
            bench.measure(lambda x: x, lambda: ([1], {}), Broken())
    def test_output_failure_propagates(self):
        class Broken:
            def block_until_ready(self, value):
                if value == 'output': raise RuntimeError('asynchronous failure')
        with self.assertRaisesRegex(RuntimeError, 'asynchronous failure'):
            bench.measure(lambda: 'output', lambda: ([], {}), Broken())
    def test_invalid_counts_fail_before_factory(self):
        for repeat, warmup in [(0, 1), (1, -1), (True, 1), (1, 1.5)]:
            with self.assertRaises(ValueError):
                bench.measure(None, None, FakeJax(), repeat=repeat, warmup=warmup)
    def test_malformed_factory_fails(self):
        with self.assertRaises(TypeError):
            bench.measure(lambda: None, lambda: ('bad', {}), FakeJax())
    def test_actual_cpu_donation(self):
        import jax
        import jax.numpy as jnp
        fn = jax.jit(lambda x: x + 1, donate_argnums=(0,))
        result = bench.measure(fn, lambda: ([jnp.arange(8, dtype=jnp.float32)], {}), jax, repeat=3)
        self.assertEqual(len(result['times_ms']), 3)

if __name__ == '__main__': unittest.main()
