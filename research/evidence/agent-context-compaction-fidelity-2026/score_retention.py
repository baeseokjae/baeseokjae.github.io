#!/usr/bin/env python3
"""Score compaction-retention probes against a responses file.

Deterministic, standard library only. The scorer does not call a model and does
not decide whether a paraphrase is semantically right; it classifies each
answer mechanically so that the five outcomes are reproducible by a second
reader. Read the rules below before trusting a retention number.

Outcome rules, applied in this order to a normalized response:
  silence       empty or whitespace-only answer
  correct       the probe's `expected` string appears as a substring
  fabrication   any transcript distractor appears (a plausible wrong value)
  paraphrase    every probe `keyword` appears but `expected` does not
  abstention    an abstention cue appears and no expected value or distractor
  other         none of the above (counted separately, never as retained)

retention_rate = (correct + paraphrase) / probes answered
exact_rate     = correct / probes answered

Usage:
  python3 score_retention.py --probes probe-template.json --responses responses.json
  python3 score_retention.py --probes P --responses R --json out.json
"""
import argparse
import json
import re
import sys
from collections import defaultdict

OUTCOMES = ("correct", "paraphrase", "fabrication", "abstention", "silence", "other")
CONTROL = "control"


def norm(text):
    text = (text or "").lower()
    text = text.replace("_", " ").replace("-", " ")
    return re.sub(r"\s+", " ", text).strip()


def score_answer(probe, response, distractors, cues):
    answer = norm(response)
    if not answer:
        return "silence"
    expected = norm(probe["expected"])
    if expected and expected in answer:
        return "correct"
    if any(norm(d) and norm(d) in answer for d in distractors):
        return "fabrication"
    keywords = [norm(k) for k in probe.get("keywords", []) if norm(k)]
    if keywords and all(k in answer for k in keywords):
        return "paraphrase"
    if any(norm(c) and norm(c) in answer for c in cues):
        return "abstention"
    return "other"


def score(probes_doc, responses):
    probes = {p["id"]: p for p in probes_doc["probes"]}
    distractors = probes_doc.get("distractors", [])
    cues = probes_doc.get("abstention_cues", [])
    rows = defaultdict(lambda: defaultdict(int))
    by_class = defaultdict(lambda: defaultdict(int))
    unknown = []
    for item in responses:
        pid = item.get("probe_id")
        if pid not in probes:
            unknown.append(pid)
            continue
        strategy = item.get("strategy") or "unlabelled"
        outcome = score_answer(probes[pid], item.get("response", ""), distractors, cues)
        rows[strategy][outcome] += 1
        rows[strategy]["answered"] += 1
        by_class[strategy][probes[pid].get("class", "unclassified") + ":" + outcome] += 1
        by_class[strategy][probes[pid].get("class", "unclassified") + ":answered"] += 1

    summary = {}
    for strategy, counts in sorted(rows.items()):
        answered = counts.get("answered", 0)
        retained = counts.get("correct", 0) + counts.get("paraphrase", 0)
        classes = {}
        for key, value in by_class[strategy].items():
            cls, _, field = key.rpartition(":")
            classes.setdefault(cls, {"answered": 0, "correct": 0, "paraphrase": 0,
                                     "fabrication": 0, "abstention": 0, "silence": 0, "other": 0})
            classes[cls][field] = value
        for cls, counts_cls in classes.items():
            n = counts_cls["answered"]
            counts_cls["retention_rate"] = round(
                (counts_cls["correct"] + counts_cls["paraphrase"]) / n, 4) if n else None
        summary[strategy] = {
            "answered": answered,
            "outcomes": {k: counts.get(k, 0) for k in OUTCOMES},
            "retention_rate": round(retained / answered, 4) if answered else None,
            "exact_rate": round(counts.get("correct", 0) / answered, 4) if answered else None,
            "by_class": classes,
        }

    transcript = probes_doc.get("transcript", {})
    before, after = transcript.get("tokens_before"), transcript.get("tokens_after")
    reduction = None
    if isinstance(before, int) and isinstance(after, int) and before > 0:
        reduction = round(1 - after / before, 4)

    control = summary.get(CONTROL)
    return {
        "transcript_id": transcript.get("id"),
        "token_reduction": reduction,
        "control_present": control is not None,
        "control_exact_rate": control["exact_rate"] if control else None,
        "strategies": summary,
        "unknown_probe_ids": unknown,
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description="Score compaction-retention probes against a responses file.")
    ap.add_argument("--probes", required=True)
    ap.add_argument("--responses", required=True)
    ap.add_argument("--control-threshold", type=float, default=0.95,
                    help="control arm exact-rate below which loss cannot be attributed to compaction")
    ap.add_argument("--json", help="write the summary here as well as stdout")
    args = ap.parse_args(argv)

    with open(args.probes, encoding="utf-8") as fh:
        probes_doc = json.load(fh)
    with open(args.responses, encoding="utf-8") as fh:
        responses = json.load(fh)
    if isinstance(responses, dict):
        responses = responses.get("responses", [])

    result = score(probes_doc, responses)
    result["control_threshold"] = args.control_threshold
    result["control_ok"] = (
        result["control_exact_rate"] is not None
        and result["control_exact_rate"] >= args.control_threshold
    )
    if result["unknown_probe_ids"]:
        result["warning"] = "responses reference probe ids missing from the probe file"

    text = json.dumps(result, indent=2, sort_keys=True)
    print(text)
    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            fh.write(text + "\n")
    return 0 if result["control_ok"] else 3


if __name__ == "__main__":
    sys.exit(main())
