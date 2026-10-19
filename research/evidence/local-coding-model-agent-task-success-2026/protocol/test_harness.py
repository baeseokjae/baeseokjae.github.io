#!/usr/bin/env python3
"""Deterministic unit tests for the task-success harness and scorer.

Offline, standard library only. Each test proves one property the article relies on:
the sandbox is frozen and its baseline failure is scoped, the reference double completes
every task, and each single-defect double moves only what it breaks.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import harness  # noqa: E402
import models  # noqa: E402

TASKS = HERE / "tasks.json"
SANDBOX = HERE / "sandbox"


def run(adapter, workdir):
    return harness.run_session(adapter, tasks_path=TASKS, workdir=Path(workdir))


class SandboxTests(unittest.TestCase):
    def test_tree_hash_is_stable(self):
        self.assertEqual(harness.tree_sha256(SANDBOX), harness.tree_sha256(SANDBOX))

    def test_frozen_baseline_fails_only_in_report_module(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            work = Path(tmp) / "repo"
            harness.materialize(SANDBOX, work)
            store = harness.run_suite(work, ["tests.test_store"])
            full = harness.run_suite(work)
        self.assertIn("OK", store)
        self.assertIn("FAILED", full)
        self.assertIn("test_report", full)

    def test_score_mapping(self):
        self.assertEqual(harness.score({"a": True, "b": True}), "completed")
        self.assertEqual(harness.score({"a": True, "b": False}), "partially")
        self.assertEqual(harness.score({"a": False, "b": False}), "failed")


class AdapterTests(unittest.TestCase):
    def setUp(self):
        import tempfile
        self._tmp = tempfile.TemporaryDirectory()
        self.workdir = Path(self._tmp.name) / "repo"

    def tearDown(self):
        self._tmp.cleanup()

    def test_reference_double_completes_every_task(self):
        result = run(models.ReferenceAdapter(), self.workdir)
        statuses = [r["status"] for r in result["records"]]
        self.assertEqual(statuses, ["completed"] * 4, result["records"])
        self.assertEqual(result["aggregate"]["completion_rate"], 1.0)
        self.assertEqual(result["aggregate"]["total_escalations"], 0)

    def test_stall_double_fails_every_task(self):
        result = run(models.StallAdapter(), self.workdir)
        self.assertEqual([r["status"] for r in result["records"]], ["failed"] * 4)

    def test_loop_double_exhausts_the_step_budget(self):
        result = run(models.LoopAdapter(), self.workdir)
        self.assertEqual([r["steps"] for r in result["records"]], [12, 12, 12, 12])
        self.assertEqual([r["status"] for r in result["records"]], ["failed"] * 4)

    def test_escalation_double_records_one_escalation_per_task(self):
        result = run(models.EscalationAdapter(), self.workdir)
        self.assertEqual([r["escalations"] for r in result["records"]], [1, 1, 1, 1])
        self.assertEqual(result["aggregate"]["total_escalations"], 4)

    def test_partial_rename_double_moves_only_the_rename_column(self):
        result = run(models.PartialRenameAdapter(), self.workdir)
        statuses = {r["task_id"]: r["status"] for r in result["records"]}
        self.assertEqual(statuses["T1-add-method"], "completed")
        self.assertEqual(statuses["T2-add-test"], "completed")
        self.assertEqual(statuses["T3-fix-failing-test"], "completed")
        self.assertEqual(statuses["T4-rename-across-files"], "partially")
        t4 = [r for r in result["records"] if r["task_id"].startswith("T4")][0]
        self.assertTrue(t4["checks"]["new_name_defined"])
        self.assertFalse(t4["checks"]["old_call_sites_gone"])

    def test_matrix_csv_shape(self):
        result = run(models.ReferenceAdapter(), self.workdir)
        rows = harness.matrix_csv(result).strip().splitlines()
        self.assertEqual(len(rows), 6)  # header + 4 tasks + aggregate
        self.assertTrue(rows[0].startswith("task_id,"))
        self.assertTrue(rows[5].startswith("AGGREGATE,"))

    def test_transcript_is_sanitized(self):
        result = run(models.ReferenceAdapter(), self.workdir)
        payload = repr(result["transcript"])
        self.assertNotIn(str(self.workdir), payload)
        self.assertTrue(all("op" in step for step in result["transcript"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
