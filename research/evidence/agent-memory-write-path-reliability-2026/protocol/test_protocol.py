"""Deterministic fixture tests for the write-path protocol.

They exercise a *synthetic* in-memory double (adapters.ReferenceAdapter) so the
harness and every promised measure are proven runnable with no credentials,
network or hosting. Assertions are exact fixture numbers and must never be
reported as vendor benchmarks.

Run:  python3 test_protocol.py            # unittest, no third-party deps
"""
from __future__ import annotations

import hashlib
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from adapters import ReferenceAdapter  # noqa: E402
import run_protocol  # noqa: E402

DATASET = HERE / "dataset.json"


class DatasetShape(unittest.TestCase):
    def test_dataset_counts(self):
        ds = run_protocol.load_dataset(DATASET)
        self.assertEqual(len(ds["stable"]), 12)
        self.assertEqual(len(ds["updates"]), 8)
        self.assertEqual(len(ds["contradictions"]), 6)
        self.assertEqual(len(ds["deletions"]), 8)
        self.assertEqual(len(ds["out_of_scope"]), 6)
        # roughly 40 write units: stable + updates + (contradiction a+b) + deletions
        writes = len(ds["stable"]) + len(ds["updates"]) + 2 * len(ds["contradictions"]) + len(ds["deletions"])
        self.assertEqual(writes, 40)

    def test_dataset_hash_stable(self):
        first = hashlib.sha256(DATASET.read_bytes()).hexdigest()
        run_protocol.load_dataset(DATASET)
        second = hashlib.sha256(DATASET.read_bytes()).hexdigest()
        self.assertEqual(first, second)


class ReferenceScores(unittest.TestCase):
    def rates(self, defect):
        ds = run_protocol.load_dataset(DATASET)
        adapter = ReferenceAdapter(defect=defect)
        res = run_protocol.run(adapter, ds, {"system": "fixture", "version": "1.0", "model": "none"})
        return run_protocol.aggregate(res["rows"])

    def test_reference_passes_every_measure(self):
        sc = self.rates("none")
        for measure in ("write_success", "staleness_after_update", "contradiction_handling",
                        "deletion_effectiveness", "provenance_traceability", "out_of_scope_abstention"):
            self.assertEqual(sc[measure]["rate"], 1.0, measure)

    def test_write_defect_drops_write_success(self):
        sc = self.rates("write")
        self.assertEqual(sc["write_success"]["passed"], 39)
        self.assertEqual(sc["write_success"]["total"], 40)
        self.assertLess(sc["write_success"]["rate"], 1.0)

    def test_stale_defect_drops_staleness(self):
        sc = self.rates("stale")
        self.assertEqual(sc["staleness_after_update"]["rate"], 0.0)

    def test_contradiction_defect_drops_contradiction(self):
        sc = self.rates("contradiction")
        self.assertEqual(sc["contradiction_handling"]["passed"], 5)
        self.assertEqual(sc["contradiction_handling"]["total"], 6)

    def test_delete_defect_drops_deletion(self):
        sc = self.rates("delete")
        self.assertEqual(sc["deletion_effectiveness"]["passed"], 7)
        self.assertEqual(sc["deletion_effectiveness"]["total"], 8)

    def test_provenance_defect_drops_provenance(self):
        sc = self.rates("provenance")
        self.assertEqual(sc["provenance_traceability"]["rate"], 19 / 20)

    def test_fabricate_defect_is_caught_by_out_of_scope(self):
        sc = self.rates("fabricate")
        self.assertEqual(sc["out_of_scope_abstention"]["passed"], 5)
        self.assertEqual(sc["out_of_scope_abstention"]["total"], 6)

    def test_transcript_hash_is_deterministic(self):
        ds = run_protocol.load_dataset(DATASET)
        a = run_protocol.run(ReferenceAdapter("none"), ds, {"system": "f", "version": "1", "model": "none"})
        b = run_protocol.run(ReferenceAdapter("none"), ds, {"system": "f", "version": "1", "model": "none"})
        ha = hashlib.sha256(str(a["log"]).encode()).hexdigest()
        hb = hashlib.sha256(str(b["log"]).encode()).hexdigest()
        self.assertEqual(ha, hb)


if __name__ == "__main__":
    unittest.main(verbosity=2)
