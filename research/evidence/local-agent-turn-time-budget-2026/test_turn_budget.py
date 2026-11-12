#!/usr/bin/env python3
"""Tests for turn_budget.py. Stdlib unittest only; no network, no model server.

Run: python3 -m unittest -v test_turn_budget.py
"""

import io
import json
import os
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import turn_budget as tb

# Inputs of the worked example, kept here so a changed EXAMPLE cannot silently
# change the numbers the article prints.
EX = dict(prefill_tps=6.17, decode_tps=4.05, prompt_tokens=512, output_tokens=256,
          overhead_s=2.0, turns=30, timeout_s=600.0)


def example_budget():
    return tb.budget(EX["prefill_tps"], EX["decode_tps"], EX["prompt_tokens"],
                     EX["output_tokens"], EX["overhead_s"], EX["turns"], EX["timeout_s"])


def synthetic_records(decode=(3.10, 3.15, 3.20), prefill=(5.0, 5.1, 5.0), prompt_tokens=32):
    rows = []
    for i, (d, p) in enumerate(zip(decode, prefill)):
        rows.append({"fixture": "short", "repeat": i, "model": "m", "error": None,
                     "prompt_eval_count": prompt_tokens, "eval_count": 48,
                     "prefill_tps": p, "decode_tps": d, "wall_s": 20.0 + i})
    return rows


class WorkedExampleTest(unittest.TestCase):
    """The numbers in the article, recomputed from the printed inputs."""

    def test_example_constants_match_module(self):
        self.assertEqual(tb.EXAMPLE["prefill_tps"], EX["prefill_tps"])
        self.assertEqual(tb.EXAMPLE["decode_tps"], EX["decode_tps"])
        self.assertEqual(tb.EXAMPLE["timeout_s"], EX["timeout_s"])

    def test_prefill_and_decode_seconds(self):
        out = example_budget()["outputs"]
        self.assertAlmostEqual(out["prefill_s"], 82.98, places=2)
        self.assertAlmostEqual(out["decode_s"], 63.21, places=2)

    def test_turn_seconds(self):
        self.assertAlmostEqual(example_budget()["outputs"]["turn_s"], 148.19, places=2)

    def test_task_time_thirty_turns(self):
        out = example_budget()["outputs"]
        self.assertAlmostEqual(out["task_s"], 4445.8, delta=0.5)
        self.assertAlmostEqual(out["task_h"], 1.23, places=2)

    def test_min_decode_rate(self):
        self.assertAlmostEqual(example_budget()["outputs"]["min_decode_tps_for_turn"], 0.497,
                               places=3)

    def test_prefill_alone_at_timeout(self):
        self.assertEqual(example_budget()["outputs"]["prompt_tokens_at_timeout"], 3702)

    def test_turn_at_4096_prompt_tokens(self):
        turn = tb.turn_seconds(4096, 256, 6.17, 4.05, 2.0)
        self.assertAlmostEqual(turn, 729.1, places=1)

    def test_turn_does_not_fit_timeout_at_4096(self):
        self.assertFalse(tb.turn_seconds(4096, 256, 6.17, 4.05, 2.0) <= 600.0)


class InversionTest(unittest.TestCase):
    def test_min_decode_round_trips_to_the_timeout(self):
        prefill_s = tb.prefill_seconds(512, 6.17)
        rate = tb.min_decode_tps(256, 600.0, prefill_s, 2.0)
        self.assertAlmostEqual(tb.turn_seconds(512, 256, 6.17, rate, 2.0), 600.0, places=6)

    def test_min_decode_is_zero_when_prefill_alone_exceeds_timeout(self):
        self.assertEqual(tb.min_decode_tps(256, 600.0, 700.0, 2.0), 0.0)

    def test_slower_decode_needs_longer_turn(self):
        fast = tb.turn_seconds(512, 256, 6.17, 10.0, 2.0)
        slow = tb.turn_seconds(512, 256, 6.17, 5.0, 2.0)
        self.assertLess(fast, slow)


class SpreadGateTest(unittest.TestCase):
    def test_observed_research_rates_fail_the_gate(self):
        spread = tb.spread_pct([1.615, 3.165])
        self.assertAlmostEqual(spread, 96.0, delta=0.1)
        self.assertGreater(spread, tb.SPREAD_GATE_PCT)

    def test_ten_percent_boundary_passes(self):
        self.assertLessEqual(tb.spread_pct([3.0, 3.3]), tb.SPREAD_GATE_PCT)

    def test_single_record_has_no_spread(self):
        self.assertIsNone(tb.spread_pct([3.0]))

    def test_noisy_summary_is_rejected_not_averaged(self):
        summary = tb.summarise(synthetic_records(decode=(1.615, 3.165, 2.0)))
        self.assertEqual(summary["verdict"], "rejected_noisy")
        self.assertEqual(summary["fixtures"]["short"]["gate"], "rejected")

    def test_quiet_summary_is_usable(self):
        summary = tb.summarise(synthetic_records())
        self.assertEqual(summary["verdict"], "usable")
        self.assertAlmostEqual(summary["fixtures"]["short"]["decode_tps_median"], 3.15)


class JsonlAndRecomputeTest(unittest.TestCase):
    """A run file written by measure() must reproduce the printed task time."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.jsonl = os.path.join(self.tmp.name, "runs.jsonl")

    def test_summarise_then_compute_reproduces_task_time(self):
        with open(self.jsonl, "w") as handle:
            for row in synthetic_records():
                handle.write(json.dumps(row) + "\n")
        summary = tb.summarise(tb.load_records(self.jsonl))
        rates = summary["fixtures"]["short"]
        rebuilt = tb.budget(rates["prefill_tps_median"], rates["decode_tps_median"],
                            prompt_tokens=32, output_tokens=48, overhead_s=2.0,
                            turns=30, timeout_s=600.0)
        direct = tb.turn_seconds(32, 48, 5.0, 3.15, 2.0)
        self.assertAlmostEqual(rebuilt["outputs"]["turn_s"], round(direct, 2), places=2)
        self.assertAlmostEqual(rebuilt["outputs"]["task_s"], round(direct * 30, 1), delta=0.1)

    def test_measure_flushes_one_line_per_request_even_when_a_request_fails(self):
        body = {"prompt_eval_count": 32, "prompt_eval_duration": 4_000_000_000,
                "eval_count": 48, "eval_duration": 12_000_000_000}
        calls = {"n": 0}

        class FakeResponse(io.BytesIO):
            def __enter__(self):
                return self

            def __exit__(self, *exc):
                return False

        def fake_urlopen(request, timeout=None):
            calls["n"] += 1
            if calls["n"] == 2:
                raise OSError("connection reset")
            return FakeResponse(json.dumps(body).encode())

        fixtures = [{"name": "short", "prompt": "one two three"}]
        with mock.patch.object(tb.urllib.request, "urlopen", fake_urlopen):
            written = tb.measure("http://127.0.0.1:1/api/generate", "fake:1b", fixtures,
                                 repeats=2, jsonl_path=self.jsonl, timeout_s=5,
                                 deadline_s=60)
        rows = tb.load_records(self.jsonl)
        self.assertEqual(written, 2)
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["error"], None)
        self.assertIn("connection reset", rows[1]["error"])
        self.assertAlmostEqual(rows[0]["prefill_tps"], 8.0, places=3)
        self.assertAlmostEqual(rows[0]["decode_tps"], 4.0, places=3)

    def test_rates_rejects_missing_counters(self):
        with self.assertRaises(ValueError):
            tb.rates(None, None, None, 48, 12_000_000_000)
        with self.assertRaises(ValueError):
            tb.rates(32, None, 4_000_000_000, 0, 12_000_000_000)

    def test_rates_subtracts_cached_prompt_tokens(self):
        # 64 total input tokens of which 32 came from the prefix cache: only
        # the 32 uncached ones were timed by prompt_eval_duration.
        prefill_tps, decode_tps = tb.rates(64, 32, 4_000_000_000, 48, 12_000_000_000)
        self.assertAlmostEqual(prefill_tps, 8.0, places=6)
        self.assertAlmostEqual(decode_tps, 4.0, places=6)

    def test_rates_treats_missing_cached_count_as_zero(self):
        prefill_tps, _ = tb.rates(32, None, 4_000_000_000, 48, 12_000_000_000)
        self.assertAlmostEqual(prefill_tps, 8.0, places=6)

    def test_rates_rejects_fully_cached_prompt(self):
        # Nothing was evaluated, so there is no prefill rate to report.
        with self.assertRaises(ValueError):
            tb.rates(32, 32, 1_000_000, 48, 12_000_000_000)

    def test_measure_records_cached_and_uncached_counts(self):
        body = {"prompt_eval_count": 64, "prompt_eval_cached_count": 32,
                "prompt_eval_duration": 4_000_000_000,
                "eval_count": 48, "eval_duration": 12_000_000_000}

        class FakeResponse(io.BytesIO):
            def __enter__(self):
                return self

            def __exit__(self, *exc):
                return False

        fixtures = [{"name": "short", "prompt": "one two three"}]
        with mock.patch.object(tb.urllib.request, "urlopen",
                               lambda request, timeout=None: FakeResponse(json.dumps(body).encode())):
            tb.measure("http://127.0.0.1:1/api/generate", "fake:1b", fixtures,
                       repeats=1, jsonl_path=self.jsonl, timeout_s=5, deadline_s=60)
        row = tb.load_records(self.jsonl)[0]
        self.assertEqual(row["prompt_eval_count"], 64)
        self.assertEqual(row["prompt_eval_cached_count"], 32)
        self.assertEqual(row["prompt_eval_uncached_count"], 32)
        self.assertAlmostEqual(row["prefill_tps"], 8.0, places=3)

    def test_uncached_prompt_tokens_handles_legacy_records(self):
        # Records written before the fix carry no cached or uncached field.
        self.assertEqual(tb.uncached_prompt_tokens({"prompt_eval_count": 32}), 32)
        self.assertEqual(tb.uncached_prompt_tokens(
            {"prompt_eval_count": 64, "prompt_eval_cached_count": 32}), 32)
        self.assertEqual(tb.uncached_prompt_tokens(
            {"prompt_eval_count": 64, "prompt_eval_uncached_count": 40}), 40)


if __name__ == "__main__":
    unittest.main()
