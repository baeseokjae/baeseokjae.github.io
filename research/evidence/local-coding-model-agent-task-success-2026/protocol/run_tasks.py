#!/usr/bin/env python3
"""Run the frozen task set against one adapter and write the raw run artifacts.

  python3 run_tasks.py --adapter reference --out "$TMPDIR/out"
  python3 run_tasks.py --adapter local --base-url http://127.0.0.1:8000 --model <id> --out "$TMPDIR/out"

Writes into --out:
  transcript.json   ordered, sanitized per-step log (no absolute host paths)
  matrix.csv        the scoring sheet: one row per task plus an aggregate row
  result.json       run header (adapter, task-set and sandbox hashes) + matrix + aggregates
The transcript and result hashes are what make a per-cell statement checkable later.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import harness  # noqa: E402
import models  # noqa: E402


def build_adapter(args):
    if args.adapter == "local":
        if not args.base_url or not args.model:
            raise SystemExit("--base-url and --model are required for the local adapter")
        return models.LocalOpenAICompatAdapter(
            args.base_url, args.model, temperature=args.temperature,
            max_tokens=args.max_tokens, seed=args.seed, timeout_s=args.timeout_s,
        )
    if args.adapter not in models.FIXTURES:
        raise SystemExit("unknown adapter %r; known: %s, local"
                         % (args.adapter, ", ".join(sorted(models.FIXTURES))))
    return models.FIXTURES[args.adapter]()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--adapter", default="reference")
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--workdir", type=Path)
    parser.add_argument("--tasks", type=Path)
    parser.add_argument("--base-url")
    parser.add_argument("--model")
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--max-tokens", type=int, default=1024)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--timeout-s", type=int, default=180)
    args = parser.parse_args()

    out = args.out
    out.mkdir(parents=True, exist_ok=True)
    workdir = args.workdir or (out / "workdir")
    adapter = build_adapter(args)
    tasks_path = args.tasks or (Path(__file__).resolve().parent / "tasks.json")

    result = harness.run_session(adapter, tasks_path=tasks_path, workdir=workdir)
    (out / "transcript.json").write_text(json.dumps(result["transcript"], indent=2) + "\n")
    (out / "matrix.csv").write_text(harness.matrix_csv(result))
    (out / "result.json").write_text(json.dumps(result, indent=2) + "\n")
    print("adapter=%s" % result["adapter"])
    print("sandbox_tree_sha256=%s" % result["sandbox_tree_sha256"])
    print("aggregate=%s" % json.dumps(result["aggregate"], sort_keys=True))
    for rec in result["records"]:
        print("  %-24s %-9s steps=%-2d tests=%-2d escalate=%d %.2fs %s"
              % (rec["task_id"], rec["status"], rec["steps"], rec["test_runs"],
                 rec["escalations"], rec["wall_clock_s"], json.dumps(rec["checks"])))
    print("RESULT: adapter=%s completed=%d partially=%d failed=%d"
          % (result["adapter"], result["aggregate"]["completed"],
             result["aggregate"]["partially"], result["aggregate"]["failed"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
