#!/usr/bin/env python3
"""Self-test for score_retention.py on a synthetic fixture.

The fixture is a scoring test: its responses were written by hand to exercise
each of the five outcome rules. It contains no model output and no compaction
measurement. Run from this directory:

    python3 -m unittest test_score_retention -v
"""
import json
import os
import subprocess
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import score_retention  # noqa: E402


def load(name):
    with open(os.path.join(HERE, "fixtures", name), encoding="utf-8") as fh:
        return json.load(fh)


class FixtureScoringTest(unittest.TestCase):
    def setUp(self):
        self.result = score_retention.score(load("fixture-probes.json"), load("fixture-responses.json"))

    def test_token_reduction(self):
        self.assertEqual(self.result["token_reduction"], 0.75)

    def test_strategy_retention(self):
        summaries = self.result["strategies"]
        self.assertEqual(summaries["control"]["retention_rate"], 1.0)
        self.assertEqual(summaries["summary_free_text"]["retention_rate"], 0.25)
        self.assertEqual(summaries["structured_pinned"]["retention_rate"], 1.0)
        self.assertEqual(summaries["structured_pinned"]["exact_rate"], 0.5)

    def test_all_five_outcomes_appear(self):
        outcomes = self.result["strategies"]["summary_free_text"]["outcomes"]
        self.assertEqual(outcomes["correct"], 1)
        self.assertEqual(outcomes["fabrication"], 1)
        self.assertEqual(outcomes["abstention"], 1)
        self.assertEqual(outcomes["silence"], 1)
        self.assertEqual(outcomes["paraphrase"], 0)
        self.assertEqual(self.result["strategies"]["structured_pinned"]["outcomes"]["paraphrase"], 2)

    def test_control_arm_is_required(self):
        doc = load("fixture-probes.json")
        responses = [r for r in load("fixture-responses.json") if r["strategy"] != "control"]
        result = score_retention.score(doc, responses)
        self.assertFalse(result["control_present"])
        self.assertIsNone(result["control_exact_rate"])

    def test_unmatched_probe_id_is_reported(self):
        responses = load("fixture-responses.json") + [{"probe_id": "nope", "strategy": "control", "response": "x"}]
        result = score_retention.score(load("fixture-probes.json"), responses)
        self.assertEqual(result["unknown_probe_ids"], ["nope"])

    def test_cli_exit_code_reflects_control(self):
        proc = subprocess.run(
            [sys.executable, os.path.join(HERE, "score_retention.py"),
             "--probes", os.path.join(HERE, "fixtures", "fixture-probes.json"),
             "--responses", os.path.join(HERE, "fixtures", "fixture-responses.json")],
            capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn('"control_ok": true', proc.stdout)


if __name__ == "__main__":
    unittest.main()
