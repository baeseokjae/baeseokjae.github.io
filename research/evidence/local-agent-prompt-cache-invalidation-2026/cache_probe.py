#!/usr/bin/env python3
"""Reader-facing prefix-reuse probe for a local Ollama server.

Point it at your own endpoint and your own prompt builder; it prints, per turn,
the server-reported prompt tokens, the prefill seconds and a hit|miss|unknown
class, then runs four assertions:

  A1  turn N+1's prompt starts with turn N's prompt (byte-level prefix identity)
  A2  turn 2 is classified a hit (the prefix was reused)
  A3  one deliberately mutable line prepended above the stable block flips the
      next turn to a miss (the negative control that proves the probe is
      measuring what it claims)
  A4  hit and miss classes are separated on this host by a factor you print,
      so you know your own threshold instead of importing someone else's

This is the condensed reference for the sweep published with the article
"Prompt-Prefix Cache in a Local Agent Loop". The full harness that produced
results.jsonl (variant interleaving, deadline reserve, fsync per record) is
probe.py; this file is the small version meant to be dropped into a repo and
adapted to a real agent's prompt builder.

Usage:
  cache_probe.py --model qwen3:0.6b                  # live run, 3 requests
  cache_probe.py --dry-run                           # prefix assertions only

Exit code 0 = all assertions passed, 1 = a FAIL line was printed.

Stdlib only. No network beyond the endpoint argument. No credentials.
"""
import argparse
import datetime
import hashlib
import json
import urllib.request

DEFAULT_ENDPOINT = "http://127.0.0.1:11434"
NUM_PREDICT = 3
TRAILER = "\nAssistant:"


def policy_block(n=8):
    """Deterministic 'system policy' stand-in: same bytes on every turn."""
    return "SYSTEM POLICY\n" + "\n".join(
        "Policy line %02d: keep the stable block stable; revision=r%d." % (i, i % 7)
        for i in range(1, n + 1)
    ) + "\nEND POLICY\n"


def registry(seed=None):
    """Two tool definitions; seed permutes JSON key order only, not content."""
    tools = [
        {"type": "function", "function": {"name": "read_file", "description": "Read a file.",
                                          "parameters": {"type": "object"}}},
        {"type": "function", "function": {"name": "terminal", "description": "Run a command.",
                                          "parameters": {"type": "object"}}},
    ]
    if seed is not None:
        permuted = []
        for t in tools:
            fn = t["function"]
            keys = list(fn)[::-1] if seed % 2 else list(fn)
            permuted.append({"type": t["type"], "function": {k: fn[k] for k in keys}})
        tools = permuted
    return "TOOLS\n" + "\n".join(json.dumps(t, separators=(",", ":")) for t in tools) + "\nEND TOOLS\n"


def build_prompt(turn, history, mutate=False):
    """The only function most readers need to replace.

    Stable bytes first, then the growing history. `mutate` prepends one line
    that changes every turn - the harness write under test.

    `turn` is the index of the last user line included, so prompt N+1 contains
    prompt N's bytes followed by more. The trailing generation marker is not
    part of the reusable prefix: a server matches tokens until the prompt
    diverges from the retained sequence, and the marker is exactly where the
    previous request ended.
    """
    stable = policy_block() + registry()
    head = ""
    if mutate:
        head = "Session started %s\n" % datetime.datetime.now(datetime.timezone.utc).isoformat()
    return head + stable + "\n" + "\n".join(history[:turn + 1]) + TRAILER


def call(endpoint, model, prompt, timeout=600):
    payload = json.dumps({
        "model": model, "prompt": prompt, "raw": True, "stream": False,
        "keep_alive": "30m",
        "options": {"temperature": 0, "num_predict": NUM_PREDICT, "seed": 42},
    }).encode()
    req = urllib.request.Request(endpoint.rstrip("/") + "/api/generate", data=payload,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def seconds(ns):
    return None if ns is None else round(ns / 1e9, 4)


def classify(prefill_s, hit_ceiling_s):
    if prefill_s is None:
        return "unknown"
    return "hit" if prefill_s < hit_ceiling_s else "miss"


def reuses(previous_prompt, next_prompt):
    """True when the next prompt repeats every byte the previous one sent,
    up to and including the last user line (the generation trailer is where
    the previous request stopped, not part of the reusable prefix)."""
    return next_prompt.startswith(previous_prompt[:-len(TRAILER)])


def record(resp, prompt, turn, label):
    return {
        "label": label,
        "turn": turn,
        "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
        "prompt_eval_count": resp.get("prompt_eval_count"),
        "prompt_eval_cached_count": resp.get("prompt_eval_cached_count"),
        "prompt_eval_duration_s": seconds(resp.get("prompt_eval_duration")),
        "response_keys": sorted(resp.keys()),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="qwen2.5:0.5b")
    ap.add_argument("--endpoint", default=DEFAULT_ENDPOINT)
    ap.add_argument("--turns", type=int, default=2)
    ap.add_argument("--hit-ceiling", type=float, default=5.0,
                    help="seconds below which a prefill is called a hit; calibrate on your host (A4)")
    ap.add_argument("--jsonl", help="append every record here")
    ap.add_argument("--dry-run", action="store_true", help="prompt/prefix assertions only, no requests")
    a = ap.parse_args()
    history = ["User turn %d: report one number." % (i + 1) for i in range(max(a.turns, 2))]
    failures = []

    if a.dry_run:
        first, second = build_prompt(0, history), build_prompt(1, history)
        ok = reuses(first, second)
        print("A1 prefix identity (dry-run): %s" % ("PASS" if ok else "FAIL"))
        mutated = build_prompt(1, history, mutate=True)
        bad = reuses(first, mutated)
        print("A3 mutated prompt breaks prefix (dry-run): %s" % ("PASS" if not bad else "FAIL"))
        print("prompt chars: base=%d turn2=%d mutated=%d" % (len(first), len(second), len(mutated)))
        raise SystemExit(0 if ok and not bad else 1)

    print("endpoint=%s model=%s" % (a.endpoint, a.model))
    # Warm the model so a load cannot be mistaken for a cache miss.
    call(a.endpoint, a.model, "Warmup. Reply OK.")

    recs, prompts = [], []
    for turn in range(a.turns):
        prompt = build_prompt(turn, history)
        prompts.append(prompt)
        resp = call(a.endpoint, a.model, prompt)
        rec = record(resp, prompt, turn + 1, "append_only")
        rec["class"] = classify(rec["prompt_eval_duration_s"], a.hit_ceiling)
        recs.append(rec)
        print("append_only turn %d: prompt tokens=%s prefill=%ss class=%s cached=%s"
              % (rec["turn"], rec["prompt_eval_count"], rec["prompt_eval_duration_s"],
                 rec["class"], rec["prompt_eval_cached_count"]))

    if a.turns >= 2:
        ok = reuses(prompts[0], prompts[1])
        print("A1 prefix identity: %s" % ("PASS" if ok else "FAIL"))
        if not ok:
            failures.append("A1")
        hit2 = recs[1]["class"] == "hit"
        print("A2 turn 2 reuses the prefix: %s" % ("PASS" if hit2 else "FAIL"))
        if not hit2:
            failures.append("A2")
        miss_s = recs[0]["prompt_eval_duration_s"]
        if recs[1]["prompt_eval_duration_s"] and miss_s:
            print("A4 separation on this host: cold %.4fs vs reuse %.4fs = %.2fx"
                  % (miss_s, recs[1]["prompt_eval_duration_s"],
                     miss_s / recs[1]["prompt_eval_duration_s"]))

    # Negative control: same content, one mutable line on top.
    mutated = build_prompt(a.turns - 1, history, mutate=True)
    resp = call(a.endpoint, a.model, mutated)
    rec = record(resp, mutated, a.turns, "timestamp_top")
    rec["class"] = classify(rec["prompt_eval_duration_s"], a.hit_ceiling)
    recs.append(rec)
    print("timestamp_top turn %d: prompt tokens=%s prefill=%ss class=%s"
          % (rec["turn"], rec["prompt_eval_count"], rec["prompt_eval_duration_s"], rec["class"]))
    flipped = rec["class"] == "miss"
    print("A3 one mutable line flips the class to miss: %s" % ("PASS" if flipped else "FAIL"))
    if not flipped:
        failures.append("A3")

    if a.jsonl:
        with open(a.jsonl, "a") as f:
            for rec in recs:
                f.write(json.dumps(rec) + "\n")
        print("wrote %d records to %s" % (len(recs), a.jsonl))

    print("RESULT: %s" % ("PASS" if not failures else "FAIL " + ",".join(failures)))
    raise SystemExit(0 if not failures else 1)


if __name__ == "__main__":
    main()
