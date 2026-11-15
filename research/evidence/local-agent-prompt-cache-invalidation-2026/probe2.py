#!/usr/bin/env python3
"""Follow-up sweep: per-turn tool permutation (d) + append-only repeat (a2).

(a2) re-runs the append-only pair after the first sweep to expose host drift.
(d)  re-serialises the same tool registry with a DIFFERENT key order on every
     turn, which is what a harness that rebuilds the registry from an unordered
     dict does.  Content is identical; only key order moves.
"""
import argparse, datetime, hashlib, json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import probe

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--model", default="qwen2.5:0.5b")
    ap.add_argument("--deadline-epoch", type=float, required=True)
    ap.add_argument("--reserve", type=float, default=150.0)
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args()
    seed = a.seed or int(time.time())

    def build(kind, turn_idx):
        seed_t = seed + turn_idx if kind == "tools_permuted_per_turn" else None
        body = probe.system_block() + probe.tools_block(order_seed=seed_t)
        hist = "\n".join(probe.TURNS[:turn_idx + 1])
        if kind == "timestamp_top":
            stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            return "Session started %s\n" % stamp + body + "\n" + hist + "\nAssistant:"
        return body + "\n" + hist + "\nAssistant:"

    order = [("tools_permuted_per_turn", "d"), ("append_only", "a2")]
    n = 0
    reason = "done"
    for kind, label in order:
        for turn_idx in range(2):
            left = a.deadline_epoch - time.time()
            if left < a.reserve:
                reason = "deadline_reserve (%.0fs left)" % left
                break
            prompt = build(kind, turn_idx)
            try:
                resp, wall = probe.call(prompt, a.model)
            except Exception as e:
                print("ERROR", label, turn_idx + 1, repr(e), flush=True)
                continue
            rec = {
                "ts_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "model": a.model, "variant": kind, "label": label, "turn": turn_idx + 1,
                "prompt_chars": len(prompt),
                "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
                "prompt_eval_count": resp.get("prompt_eval_count"),
                "prompt_eval_cached_count": resp.get("prompt_eval_cached_count"),
                "prompt_eval_duration_s": probe.ns_to_s(resp.get("prompt_eval_duration")),
                "eval_count": resp.get("eval_count"),
                "eval_duration_s": probe.ns_to_s(resp.get("eval_duration")),
                "load_duration_s": probe.ns_to_s(resp.get("load_duration")),
                "total_duration_s": probe.ns_to_s(resp.get("total_duration")),
                "wall_s": round(wall, 3),
                "response_text": (resp.get("response") or "")[:80],
                "response_keys": sorted(resp.keys()),
            }
            with open(a.out, "a") as f:
                f.write(json.dumps(rec) + "\n"); f.flush(); os.fsync(f.fileno())
            n += 1
            print("%-24s turn %d peval=%s cached=%s prefill=%ss wall=%.2fs"
                  % (label, turn_idx + 1, rec["prompt_eval_count"],
                     rec["prompt_eval_cached_count"], rec["prompt_eval_duration_s"], wall), flush=True)
        else:
            continue
        break
    print("records=%d stop=%s" % (n, reason), flush=True)

if __name__ == "__main__":
    main()
