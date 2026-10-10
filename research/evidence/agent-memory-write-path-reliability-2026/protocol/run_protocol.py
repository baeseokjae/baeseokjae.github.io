"""Write-path reliability harness (generic).

Drives any MemoryAdapter (see protocol/adapters.py) through a fixed order:

    ingest -> write-success check -> update + staleness check -> contradiction
    -> delete + residue check -> provenance check -> out-of-scope probes

and emits two artifacts:

    transcript.json  ordered request/response log, sanitized, hashed
    scores.json      per-item rows + the six aggregate rates + transcript_sha256

Run it against the shipped deterministic fixture:

    python3 run_protocol.py --adapter fixture-reference --out "$TMPDIR/out"
    python3 run_protocol.py --adapter fixture-write --out "$TMPDIR/out"

The fixture adapters are synthetic. `--adapter fixture-*` results are FIXTURE-ONLY
harness self-tests, never vendor measurements. To score a real system, import this
module and pass a MemoryAdapter that calls the system's own documented write API.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from adapters import MemoryAdapter, ReferenceAdapter, tokens  # noqa: E402

DEFECTS = {"fixture-reference": "none", "fixture-write": "write", "fixture-stale": "stale",
           "fixture-contradiction": "contradiction", "fixture-delete": "delete",
           "fixture-provenance": "provenance", "fixture-fabricate": "fabricate"}


def diff_tokens(old: str, new: str):
    """Tokens that appear only in the new (resp. old) assertion.

    The dataset provides old_text/new_text, so the harness can derive exactly
    which token marks the change; the scoring then checks the current value
    carries the new token and the answer to the stale question does not carry
    the old one. Deterministic: longest token, then alphabetical.
    """
    new_only = tokens(new) - tokens(old)
    old_only = tokens(old) - tokens(new)

    def pick(candidates):
        return sorted(candidates, key=lambda t: (-len(t), t))[0] if candidates else None

    return pick(new_only), pick(old_only)


def load_dataset(path: Path) -> dict:
    return json.loads(path.read_text())


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def norm(value) -> str:
    return (value or "").strip().lower()


def run(adapter: MemoryAdapter, dataset: dict, meta: dict) -> dict:
    rows: list[dict] = []
    log: list[dict] = []

    def rec(step, **kw):
        log.append({"seq": len(log) + 1, "step": step, **kw})

    # ---- phase 1: ingest + write-success -------------------------------------
    write_units = []
    for f in dataset["stable"]:
        write_units.append((f["id"], f["text"], f["scope"], "stable"))
    for f in dataset["updates"]:
        write_units.append((f["id"], f["old_text"], f["scope"], "update"))
    for f in dataset["contradictions"]:
        write_units.append((f["id"] + "a", f["source_a"], f["scope"], "contradiction"))
        write_units.append((f["id"] + "b", f["source_b"], f["scope"], "contradiction"))
    for f in dataset["deletions"]:
        write_units.append((f["id"], f["text"], f["scope"], "deletion"))

    for item_id, text, scope, kind in write_units:
        adapter.write(item_id, text, scope)
        got = adapter.retrieve_exact(item_id, scope)
        ok = norm(got) == norm(text)
        rows.append({"item": item_id, "kind": kind, "measure": "write_success", "pass": ok})
        rec("write", item=item_id, retrieved_ok=ok)

    # ---- phase 2: update + staleness -----------------------------------------
    for f in dataset["updates"]:
        adapter.update(f["id"], f["new_text"], f["scope"])
        cur = adapter.query(f["current_question"], f["scope"])
        stale = adapter.query(f["stale_question"], f["scope"])
        new_tok, old_tok = diff_tokens(f["old_text"], f["new_text"])
        current_ok = new_tok is not None and new_tok in tokens(cur)
        stale_gone = old_tok is None or old_tok not in tokens(stale)
        rows.append({"item": f["id"], "kind": "update", "measure": "staleness_after_update",
                     "pass": bool(current_ok and stale_gone), "current_ok": current_ok, "stale_gone": stale_gone})
        rec("update", item=f["id"], current_ok=current_ok, stale_gone=stale_gone)

    # ---- phase 3: contradiction handling -------------------------------------
    for f in dataset["contradictions"]:
        trace = adapter.contradiction_trace(f["question"], f["scope"])
        flagged = bool(trace.get("flagged")) and len(trace.get("values", [])) >= 2
        rows.append({"item": f["id"], "kind": "contradiction", "measure": "contradiction_handling",
                     "pass": flagged})
        rec("contradiction", item=f["id"], flagged=flagged, values=len(trace.get("values", [])))

    # ---- phase 4: delete + residue -------------------------------------------
    for f in dataset["deletions"]:
        adapter.delete(f["id"], f["scope"])
        residual_exact = adapter.retrieve_exact(f["id"], f["scope"]) is not None
        residual_semantic = bool(adapter.semantic_hit(f["text"], f["scope"]))
        clean = not residual_exact and not residual_semantic
        rows.append({"item": f["id"], "kind": "deletion", "measure": "deletion_effectiveness",
                     "pass": clean, "residual_exact": residual_exact, "residual_semantic": residual_semantic})
        rec("delete", item=f["id"], residual_exact=residual_exact, residual_semantic=residual_semantic)

    # ---- phase 5: provenance --------------------------------------------------
    for f in dataset["stable"] + dataset["updates"]:
        prov = adapter.provenance(f["id"], f["scope"])
        ok = bool(prov)
        rows.append({"item": f["id"], "kind": "provenance", "measure": "provenance_traceability", "pass": ok})
        rec("provenance", item=f["id"], sources=len(prov))

    # ---- phase 6: out-of-scope probes ----------------------------------------
    for f in dataset["out_of_scope"]:
        answer = adapter.query(f["question"], f["scope"])
        fabricated = answer is not None and str(answer).strip() != ""
        rows.append({"item": f["id"], "kind": "out_of_scope", "measure": "out_of_scope_abstention",
                     "pass": not fabricated})
        rec("out_of_scope", item=f["id"], fabricated=fabricated)

    return {"rows": rows, "log": log, "meta": meta}


def aggregate(rows: list[dict]) -> dict:
    measures = ["write_success", "staleness_after_update", "contradiction_handling",
                "deletion_effectiveness", "provenance_traceability", "out_of_scope_abstention"]
    out = {}
    for m in measures:
        subset = [r for r in rows if r["measure"] == m]
        total = len(subset)
        passed = sum(1 for r in subset if r["pass"])
        out[m] = {"passed": passed, "total": total,
                  "rate": round(passed / total, 4) if total else None}
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dataset", default=str(HERE / "dataset.json"))
    ap.add_argument("--adapter", default="fixture-reference", choices=sorted(DEFECTS))
    ap.add_argument("--system", default="fixture-reference")
    ap.add_argument("--version", default="1.0")
    ap.add_argument("--model", default="none")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    dataset_path = Path(args.dataset)
    dataset = load_dataset(dataset_path)
    dataset_hash = hashlib.sha256(dataset_path.read_bytes()).hexdigest()
    adapter = ReferenceAdapter(defect=DEFECTS[args.adapter])
    meta = {"system": args.system, "version": args.version, "model": args.model,
            "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "dataset_sha256": dataset_hash, "adapter_class": type(adapter).__name__}
    result = run(adapter, dataset, meta)
    scores = aggregate(result["rows"])
    scores["rows"] = result["rows"]  # per-item detail; aggregate() only derives the rates
    scores["meta"] = meta
    scores["fixture_only"] = args.adapter.startswith("fixture-")

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    transcript = {"meta": meta, "log": result["log"]}
    transcript_text = json.dumps(transcript, indent=2, sort_keys=True)
    scores["transcript_sha256"] = sha256_text(transcript_text)
    (out / "transcript.json").write_text(transcript_text)
    (out / "scores.json").write_text(json.dumps(scores, indent=2, sort_keys=True))
    print(json.dumps({"meta": meta, "rates": {k: v["rate"] for k, v in scores.items() if isinstance(v, dict) and "rate" in v},
                      "transcript_sha256": scores["transcript_sha256"], "fixture_only": scores["fixture_only"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
