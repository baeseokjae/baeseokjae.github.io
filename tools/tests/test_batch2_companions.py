"""Verify the actual published synthetic examples without rewriting evidence."""
import json
import subprocess
import sys
import unittest
from pathlib import Path


class BatchTwoCompanionTests(unittest.TestCase):
    def test_recorded_cases_and_source_hashes_reproduce(self):
        folder = Path(__file__).resolve().parents[2] / "static/research/content-quality-batch2-2026-10"
        before = (folder / "offline-results.json").read_bytes()
        saved = json.loads(before)
        actual = json.loads(subprocess.check_output(
            [sys.executable, "-B", str(folder / "verify_examples.py")], text=True))
        for key in ("passed", "cases", "files", "illustrations", "method", "limits"):
            with self.subTest(field=key):
                self.assertEqual(saved[key], actual[key])
        self.assertEqual(before, (folder / "offline-results.json").read_bytes())


if __name__ == "__main__":
    unittest.main()
