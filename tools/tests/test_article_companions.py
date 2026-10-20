"""Keep the published executable examples consistent with their run evidence."""
import json
import subprocess
import sys
import unittest
from pathlib import Path


class ArticleCompanionTests(unittest.TestCase):
    def test_offline_examples_reproduce_the_published_results(self):
        folder = Path(__file__).resolve().parents[2] / "static/research/content-quality-2026-10"
        saved = json.loads((folder / "offline-results.json").read_text())
        output = subprocess.check_output(
            [sys.executable, "-B", str(folder / "verify_examples.py")], text=True
        )
        actual = json.loads(output)
        for key in ("passed", "boundary_checks", "responses_checks", "cost_examples",
                    "weight_memory_lower_bounds_decimal_GB", "file_sha256"):
            with self.subTest(field=key):
                self.assertEqual(actual[key], saved[key])


if __name__ == "__main__":
    unittest.main()
