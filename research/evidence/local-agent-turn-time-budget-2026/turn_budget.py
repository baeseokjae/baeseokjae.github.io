#!/usr/bin/env python3
"""turn_budget.py - turn-time budget for a single-stream local coding agent.

Three jobs, one arithmetic core:

  measure    measure prefill and decode separately against a local Ollama
             endpoint, three prompts x three repeats, one JSONL record flushed
             per request, median and spread reported.
  summarise  read a JSONL run file back and print the medians and the spread
             gate verdict (no endpoint needed).
  compute    convert measured (or declared) rates into turn time and task time
             for a turn count, and invert the equation into the minimum decode
             rate and the prompt length at which prefill alone blows a timeout.
  example    print the worked example whose inputs are printed by llama-bench's
             README table (upstream sample rows, not a measurement made here).

Design rules this file enforces, because the numbers are only useful if they
come from the reader's own machine:

  * prefill and decode are derived per request from the server's own counters
    (prompt_eval_count, prompt_eval_cached_count, prompt_eval_duration,
    eval_count, eval_duration); never from a headline tokens/second figure.
    prompt_eval_count is the total input prompt (cached + newly evaluated)
    while prompt_eval_duration times the uncached evaluation only, so the
    prefill numerator is prompt_eval_count - prompt_eval_cached_count.
  * every record is written and fsynced before the next request starts, so a
    killed run still leaves usable evidence.
  * a run whose repeat-to-repeat spread exceeds 10% is reported as REJECTED
    and the medians are not printed as a baseline. Noise on a shared host is
    not a measurement.
  * no GPU, no cross-hardware table: the script measures one endpoint.

Only the Python standard library is required. It talks to a local HTTP endpoint
and writes a JSONL file; it does not download models and does not set any
server environment variable.

Usage (reader side, against an already-running Ollama):

  python3 turn_budget.py measure --model qwen3:8b \
      --jsonl "$TMPDIR/turn_budget_runs.jsonl" --repeats 3
  python3 turn_budget.py summarise --jsonl "$TMPDIR/turn_budget_runs.jsonl"
  python3 turn_budget.py compute --jsonl "$TMPDIR/turn_budget_runs.jsonl" \
      --turns 30 --output-tokens 256 --tool-overhead 2 --timeout 600

Usage (arithmetic only, no endpoint):

  python3 turn_budget.py example
  python3 turn_budget.py compute --prefill-tps 6.17 --decode-tps 4.05 \
      --prompt-tokens 512 --output-tokens 256 --tool-overhead 2 \
      --turns 30 --timeout 600
"""

import argparse
import json
import os
import statistics
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

SPREAD_GATE_PCT = 10.0
DEFAULT_ENDPOINT = "http://127.0.0.1:11434/api/generate"

# Worked-example inputs. Provenance, stated so a reader can check them:
#   prefill_tps 6.17, decode_tps 4.05 -> llama-bench README table, "llama 7B
#     mostly Q4_0", backend CPU, 1 thread, rows "pp 64" and "tg 16".
#   timeout_s 600 -> openai-python DEFAULT_TIMEOUT.
#   prompt_tokens 512, output_tokens 256, tool_overhead_s 2 -> this harness's
#     declared scenario, not a measurement.
# These are upstream sample rows; no figure here describes any reader's host.
EXAMPLE = {
    "prefill_tps": 6.17,
    "decode_tps": 4.05,
    "prompt_tokens": 512,
    "output_tokens": 256,
    "tool_overhead_s": 2.0,
    "turns": 30,
    "timeout_s": 600.0,
}


def rates(prompt_eval_count, prompt_eval_cached_count, prompt_eval_duration_ns,
          eval_count, eval_duration_ns):
    """Derive prefill and decode tokens/second from the server's counters.

    Ollama reports prompt_eval_count as the whole input prompt - cached tokens
    plus newly evaluated ones (llm/llama_server.go promptEvalCount() returns
    CacheN + PromptN) - while prompt_eval_duration times only the uncached
    evaluation (PromptMS). Dividing the count by the duration therefore
    overstates prefill on a prefix-cache hit, so the numerator is
    prompt_eval_count - prompt_eval_cached_count, exactly as Ollama's own
    metrics printer does in api/types.go. A missing cached count means the
    response carried no cache information and is treated as 0 (no cache).
    """
    if not prompt_eval_count or not prompt_eval_duration_ns:
        raise ValueError("server response lacks prompt_eval_count/prompt_eval_duration")
    if not eval_count or not eval_duration_ns:
        raise ValueError("server response lacks eval_count/eval_duration")
    cached = prompt_eval_cached_count or 0
    uncached = max(0, prompt_eval_count - cached)
    if uncached == 0:
        raise ValueError("server reports no uncached prompt tokens "
                         "(prompt_eval_count == prompt_eval_cached_count); "
                         "prefill rate is undefined")
    return (
        uncached / (prompt_eval_duration_ns / 1e9),
        eval_count / (eval_duration_ns / 1e9),
    )


def uncached_prompt_tokens(record):
    """Prompt tokens that actually cost prefill in one measurement record."""
    stored = record.get("prompt_eval_uncached_count")
    if stored is not None:
        return stored
    return max(0, (record.get("prompt_eval_count") or 0)
               - (record.get("prompt_eval_cached_count") or 0))


def prefill_seconds(prompt_tokens, prefill_tps):
    return prompt_tokens / prefill_tps


def decode_seconds(output_tokens, decode_tps):
    return output_tokens / decode_tps


def turn_seconds(prompt_tokens, output_tokens, prefill_tps, decode_tps, overhead_s):
    """One agent turn = prefill + decode + declared tool/transport overhead."""
    return (
        prefill_seconds(prompt_tokens, prefill_tps)
        + decode_seconds(output_tokens, decode_tps)
        + overhead_s
    )


def task_seconds(turn_s, turns):
    return turn_s * turns


def min_decode_tps(output_tokens, timeout_s, prefill_s, overhead_s):
    """Inverse: the slowest decode rate that still fits one request in timeout."""
    budget = timeout_s - prefill_s - overhead_s
    if budget <= 0:
        return 0.0
    return output_tokens / budget


def prompt_tokens_at_timeout(prefill_tps, timeout_s):
    """Prompt length at which prefill alone consumes the whole timeout."""
    return prefill_tps * timeout_s


def spread_pct(values):
    """Repeat-to-repeat spread as (max - min) / min * 100, on >= 2 values."""
    values = [v for v in values if v is not None and v > 0]
    if len(values) < 2:
        return None
    return (max(values) - min(values)) / min(values) * 100.0


def budget(prefill_tps, decode_tps, prompt_tokens, output_tokens,
           overhead_s, turns, timeout_s):
    """The full arithmetic block, in one dict, from two rates and a scenario."""
    p_s = prefill_seconds(prompt_tokens, prefill_tps)
    d_s = decode_seconds(output_tokens, decode_tps)
    t_s = turn_seconds(prompt_tokens, output_tokens, prefill_tps, decode_tps, overhead_s)
    task_s = task_seconds(t_s, turns)
    return {
        "inputs": {
            "prefill_tps": prefill_tps,
            "decode_tps": decode_tps,
            "prompt_tokens": prompt_tokens,
            "output_tokens": output_tokens,
            "tool_overhead_s": overhead_s,
            "turns": turns,
            "timeout_s": timeout_s,
        },
        "outputs": {
            "prefill_s": round(p_s, 2),
            "decode_s": round(d_s, 2),
            "turn_s": round(t_s, 2),
            "task_s": round(task_s, 1),
            "task_h": round(task_s / 3600.0, 2),
            "min_decode_tps_for_turn": round(
                min_decode_tps(output_tokens, timeout_s, p_s, overhead_s), 3),
            "prompt_tokens_at_timeout": round(prompt_tokens_at_timeout(prefill_tps, timeout_s)),
            "turn_fits_timeout": t_s <= timeout_s,
        },
        "turn_multipliers": {
            "prompt_x2_turn_s": round(turn_seconds(prompt_tokens * 2, output_tokens,
                                                   prefill_tps, decode_tps, overhead_s), 2),
            "prompt_x8_turn_s": round(turn_seconds(prompt_tokens * 8, output_tokens,
                                                   prefill_tps, decode_tps, overhead_s), 2),
        },
    }


def measure(endpoint, model, fixtures, repeats, jsonl_path, timeout_s, deadline_s,
            num_predict=48, num_ctx=8192):
    """Measure prefill and decode per request; flush every record immediately."""
    path = Path(jsonl_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    written = 0
    for fixture in fixtures:
        for repeat in range(repeats):
            elapsed = time.monotonic() - started
            if elapsed > deadline_s:
                print(f"stop: {elapsed:.1f}s elapsed exceeds the {deadline_s}s cap; "
                      f"{written} records kept", file=sys.stderr)
                return written
            record = {
                "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "fixture": fixture["name"],
                "fixture_words": len(fixture["prompt"].split()),
                "repeat": repeat,
                "model": model,
                "endpoint": endpoint,
                "num_predict": num_predict,
                "num_ctx": num_ctx,
            }
            payload = json.dumps({
                "model": model,
                "prompt": fixture["prompt"],
                "stream": False,
                "options": {"num_predict": num_predict, "num_ctx": num_ctx,
                            "temperature": 0, "seed": 42},
                "keep_alive": "10m",
            }).encode()
            request = urllib.request.Request(
                endpoint, data=payload, headers={"Content-Type": "application/json"})
            t0 = time.monotonic()
            try:
                with urllib.request.urlopen(request, timeout=timeout_s) as response:
                    body = json.loads(response.read().decode())
            except (urllib.error.URLError, OSError, ValueError) as exc:
                record.update({"error": f"{type(exc).__name__}: {exc}", "wall_s": None,
                               "prefill_tps": None, "decode_tps": None})
            else:
                wall = time.monotonic() - t0
                try:
                    cached = body.get("prompt_eval_cached_count")
                    prefill_tps, decode_tps = rates(
                        body.get("prompt_eval_count"), cached,
                        body.get("prompt_eval_duration"),
                        body.get("eval_count"), body.get("eval_duration"))
                except ValueError as exc:
                    record.update({"error": str(exc), "wall_s": round(wall, 3),
                                   "prefill_tps": None, "decode_tps": None})
                else:
                    record.update({
                        "error": None,
                        "wall_s": round(wall, 3),
                        "prompt_eval_count": body.get("prompt_eval_count"),
                        "prompt_eval_cached_count": cached,
                        "prompt_eval_uncached_count": max(
                            0, (body.get("prompt_eval_count") or 0) - (cached or 0)),
                        "prompt_eval_duration_ns": body.get("prompt_eval_duration"),
                        "eval_count": body.get("eval_count"),
                        "eval_duration_ns": body.get("eval_duration"),
                        "prefill_tps": round(prefill_tps, 3),
                        "decode_tps": round(decode_tps, 3),
                    })
            with path.open("a") as handle:
                handle.write(json.dumps(record) + "\n")
                handle.flush()
                os.fsync(handle.fileno())
            written += 1
    return written


def load_records(jsonl_path):
    records = []
    for line in Path(jsonl_path).read_text().splitlines():
        line = line.strip()
        if line:
            records.append(json.loads(line))
    return records


def summarise(records, gate_pct=SPREAD_GATE_PCT):
    """Median rate per fixture plus the spread verdict the gate depends on."""
    ok = [r for r in records if r.get("error") is None and r.get("decode_tps")]
    by_fixture = {}
    for record in ok:
        by_fixture.setdefault(record["fixture"], []).append(record)
    fixtures = {}
    rejected = False
    for name, rows in sorted(by_fixture.items()):
        decode_spread = spread_pct([r["decode_tps"] for r in rows])
        prefill_spread = spread_pct([r["prefill_tps"] for r in rows])
        gate_pass = (
            decode_spread is not None and prefill_spread is not None
            and decode_spread <= gate_pct and prefill_spread <= gate_pct
        )
        rejected = rejected or not gate_pass
        fixtures[name] = {
            "repeats": len(rows),
            "decode_tps_median": round(statistics.median([r["decode_tps"] for r in rows]), 3),
            "prefill_tps_median": round(statistics.median([r["prefill_tps"] for r in rows]), 3),
            "decode_spread_pct": None if decode_spread is None else round(decode_spread, 1),
            "prefill_spread_pct": None if prefill_spread is None else round(prefill_spread, 1),
            "gate": "pass" if gate_pass else "rejected",
        }
    return {
        "records_total": len(records),
        "records_usable": len(ok),
        "gate_pct": gate_pct,
        "verdict": "rejected_noisy" if (rejected or not fixtures) else "usable",
        "note": ("Medians are not a baseline when verdict is rejected_noisy: "
                 "the repeats disagree by more than the gate allows."),
        "fixtures": fixtures,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    p_measure = sub.add_parser("measure", help="measure prefill/decode against a local endpoint")
    p_measure.add_argument("--endpoint", default=DEFAULT_ENDPOINT)
    p_measure.add_argument("--model", required=True)
    p_measure.add_argument("--fixture", default=str(Path(__file__).with_name("fixtures") / "prompts.json"))
    p_measure.add_argument("--jsonl", required=True)
    p_measure.add_argument("--repeats", type=int, default=3)
    p_measure.add_argument("--request-timeout", type=float, default=110.0)
    p_measure.add_argument("--deadline", type=float, default=900.0)

    p_sum = sub.add_parser("summarise", help="read a JSONL run file and apply the spread gate")
    p_sum.add_argument("--jsonl", required=True)

    for name, help_text in (("compute", "convert rates into turn/task time and invert it"),
                            ("example", "print the worked example from declared inputs")):
        p = sub.add_parser(name, help=help_text)
        p.add_argument("--jsonl", help="read medians from this run file instead of --*-tps")
        p.add_argument("--prefill-tps", type=float)
        p.add_argument("--decode-tps", type=float)
        p.add_argument("--fixture-name")
        p.add_argument("--prompt-tokens", type=int)
        p.add_argument("--output-tokens", type=int, default=256)
        p.add_argument("--tool-overhead", type=float, default=2.0)
        p.add_argument("--turns", type=int, default=30)
        p.add_argument("--timeout", type=float, default=600.0)

    args = parser.parse_args(argv)

    if args.command == "measure":
        fixtures = json.loads(Path(args.fixture).read_text())["fixtures"]
        written = measure(args.endpoint, args.model, fixtures, args.repeats, args.jsonl,
                          args.request_timeout, args.deadline)
        print(json.dumps({"records_written": written, "jsonl": args.jsonl}, indent=2))
        return 0

    if args.command == "summarise":
        print(json.dumps(summarise(load_records(args.jsonl)), indent=2))
        return 0

    if args.command == "example":
        defaults = {"prompt_tokens": EXAMPLE["prompt_tokens"],
                    "output_tokens": EXAMPLE["output_tokens"],
                    "tool_overhead": EXAMPLE["tool_overhead_s"],
                    "turns": EXAMPLE["turns"],
                    "timeout": EXAMPLE["timeout_s"]}
        for key, value in defaults.items():
            if getattr(args, key) is None:
                setattr(args, key, value)
        args.prefill_tps = EXAMPLE["prefill_tps"]
        args.decode_tps = EXAMPLE["decode_tps"]
        result = budget(args.prefill_tps, args.decode_tps, args.prompt_tokens,
                        args.output_tokens, args.tool_overhead, args.turns, args.timeout)
        result["provenance"] = {
            "prefill_tps": "llama-bench README table, llama 7B mostly Q4_0, CPU, 1 thread, pp 64 row",
            "decode_tps": "llama-bench README table, same model/backend/threads, tg 16 row",
            "timeout_s": "openai-python DEFAULT_TIMEOUT",
            "prompt_tokens/output_tokens/tool_overhead_s": "declared scenario of this harness",
            "caveat": "upstream sample rows, not a measurement of this script or of the reader's host",
        }
        print(json.dumps(result, indent=2))
        return 0

    # compute
    if args.prefill_tps is None or args.decode_tps is None:
        if not args.jsonl:
            parser.error("compute needs --jsonl or both --prefill-tps and --decode-tps")
        summary = summarise(load_records(args.jsonl))
        if summary["verdict"] != "usable":
            print(json.dumps({"status": "rejected_noisy", "summary": summary,
                              "message": "spread gate failed; medians are not a baseline"},
                             indent=2))
            return 2
        chosen = summary["fixtures"]
        name = args.fixture_name or sorted(chosen)[0]
        if name not in chosen:
            parser.error(f"fixture {name!r} not in run file: {sorted(chosen)}")
        args.prefill_tps = chosen[name]["prefill_tps_median"]
        args.decode_tps = chosen[name]["decode_tps_median"]
        if args.prompt_tokens is None:
            rows = [r for r in load_records(args.jsonl)
                    if r.get("fixture") == name and r.get("error") is None]
            args.prompt_tokens = int(statistics.median(
                [uncached_prompt_tokens(r) for r in rows]))
    if args.prompt_tokens is None:
        parser.error("--prompt-tokens is required when no --jsonl is given")
    print(json.dumps(budget(args.prefill_tps, args.decode_tps, args.prompt_tokens,
                            args.output_tokens, args.tool_overhead, args.turns,
                            args.timeout), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
