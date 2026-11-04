#!/usr/bin/env python3
"""Pin the arithmetic to hand-computed values so it cannot drift silently."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import plan  # noqa: E402

MODELS = plan.load()["models"]


class PlanTest(unittest.TestCase):
    def test_qwen3_8b_bytes_per_token_f16(self):
        per_token, fixed, kind = plan.kv_bytes_per_token(MODELS["qwen3-8b"], "f16")
        self.assertEqual(per_token, 147456)  # 2 * 36 * 8 * 128 * 2
        self.assertEqual(fixed, 0)
        self.assertEqual(kind, "dense")

    def test_qwen3_8b_kv_at_native_context(self):
        result = plan.plan(MODELS["qwen3-8b"], "Q4_K_M", 40960, overhead_gib=0)
        self.assertAlmostEqual(result["kv_gib"], 5.625, places=3)   # 40960 * 147456 B = 5.62 GiB
        self.assertAlmostEqual(result["total_gib"], 10.305, places=3)  # + 4.68 GiB Q4_K_M

    def test_qwen3_8b_kv_at_8k(self):
        result = plan.plan(MODELS["qwen3-8b"], "Q4_K_M", 8192, overhead_gib=0)
        self.assertAlmostEqual(result["kv_gib"], 1.125, places=3)

    def test_parallel_slots_multiply_kv_only(self):
        one = plan.plan(MODELS["qwen3-8b"], "Q4_K_M", 32768, parallel=1)
        four = plan.plan(MODELS["qwen3-8b"], "Q4_K_M", 32768, parallel=4)
        self.assertAlmostEqual(four["kv_gib"], one["kv_gib"] * 4, places=5)
        self.assertEqual(four["weights_gib"], one["weights_gib"])

    def test_hybrid_fixed_window_term(self):
        per_token, fixed, kind = plan.kv_bytes_per_token(MODELS["gemma-4-31b-it"], "f16")
        self.assertEqual(kind, "hybrid")
        self.assertEqual(per_token, 81920)        # 2 * 10 * 4 * 512 * 2
        self.assertEqual(fixed, 838860800)        # 2 * 50 * 16 * 256 * 2 * 1024
        result = plan.plan(MODELS["gemma-4-31b-it"], "Q4_K_M", 32768)
        self.assertAlmostEqual(result["kv_gib"], 3.28, places=2)  # not the 30 GiB naive slope

    def test_overflow_exit_code(self):
        self.assertEqual(plan.main(["--model", "qwen3-8b", "--quant", "Q4_K_M",
                                     "--context", "40960", "--vram", "10"]), 1)
        self.assertEqual(plan.main(["--model", "qwen3-8b", "--quant", "Q4_K_M",
                                     "--context", "8192", "--vram", "10"]), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
