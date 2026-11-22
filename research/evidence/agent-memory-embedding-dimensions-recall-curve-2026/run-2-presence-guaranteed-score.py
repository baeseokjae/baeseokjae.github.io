#!/usr/bin/env python3
"""Corrected store construction: the evaluated query's target facts are always present
in the index, and only distractors vary. Arctic re-run (cheap); nomic store=800 cell from
the first pass is already unconfounded (whole corpus present) and is reused."""
import json, math, os, random, statistics, time, urllib.request, csv
from operator import mul

SLUG = "agent-memory-embedding-dimensions-recall-curve-2026"
TREE = os.environ["TREE"]
EV = os.path.join(TREE, "research", "evidence", SLUG)
API = "http://127.0.0.1:11434"
MODEL, NATIVE = "snowflake-arctic-embed:33m", 384
WIDTHS = [384, 256, 128, 64]
STORES = [50, 200, 800]
SEEDS = [1, 2, 3]

fx = json.load(open(os.path.join(EV, "fixture.json")))
facts = [f["text"] for f in fx["facts"]]
queries = fx["queries"]


def post(payload):
    req = urllib.request.Request(API + "/api/embed", data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=240) as r:
        return json.loads(r.read())["embeddings"], time.time() - t0


def norm(v):
    s = math.sqrt(sum(x * x for x in v))
    return [x / s for x in v]


def dot(a, b):
    return sum(map(mul, a, b))


t0 = time.time()
F, Q, lats = [], [], []
for i in range(0, len(facts), 32):
    E, dt = post({"model": MODEL, "input": facts[i:i + 32]})
    F += [norm(v) for v in E]; lats.append(dt / len(E))
for i in range(0, len(queries), 8):
    E, dt = post({"model": MODEL, "input": [q["q"] for q in queries[i:i + 8]]})
    Q += [norm(v) for v in E]; lats.append(dt / len(E))
json.dump({"model": MODEL, "native_dims": NATIVE, "facts": F, "queries_emb": Q,
           "p50_s_per_text": statistics.median(lats)}, open(os.path.join(EV, "embeddings-arctic-33m.json"), "w"))

rows, agg = [], {}
for width in WIDTHS:
    Fw = [norm(v[:width]) for v in F]
    Qw = [norm(v[:width]) for v in Q]
    sims = [[dot(q, f) for f in Fw] for q in Qw]
    for store in STORES:
        for seed in SEEDS:
            r1 = r5 = 0; rr = 0.0
            for qi_, q in enumerate(queries):
                tg = q["target_facts"]
                others = [i for i in range(len(facts)) if i not in tg]
                random.Random(1000 * seed + qi_).shuffle(others)
                kept = tg + others[:max(0, store - len(tg))]
                ranked = sorted(kept, key=lambda fid: -sims[qi_][fid])[:10]
                pos = next((k for k, fid in enumerate(ranked) if fid in tg), None)
                r1 += pos == 0; r5 += pos is not None and pos < 5
                rr += 0.0 if pos is None else 1.0 / (pos + 1)
                rows.append({"model": MODEL, "width": width, "store": store, "seed": seed,
                             "query_id": qi_, "query_type": q["type"], "targets_in_store": len(tg),
                             "rank_of_target": -1 if pos is None else pos + 1,
                             "recall_at_1": int(pos == 0),
                             "recall_at_5": int(pos is not None and pos < 5),
                             "reciprocal_rank": round(0.0 if pos is None else 1.0 / (pos + 1), 6),
                             "bytes_per_vector": 4 * width})
            agg[(width, store, seed)] = (r1 / 40, r5 / 40, rr / 40)

with open(os.path.join(EV, "results-arctic-presence-guaranteed.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)

summary = []
for store in STORES:
    for width in WIDTHS:
        v = [agg[(width, store, s)] for s in SEEDS]
        summary.append({"model": MODEL, "width": width, "store": store, "bytes_per_vector": 4 * width,
                        "recall_at_1_mean": round(statistics.mean(x[0] for x in v), 4),
                        "recall_at_5_mean": round(statistics.mean(x[1] for x in v), 4),
                        "mrr_mean": round(statistics.mean(x[2] for x in v), 4),
                        "recall_at_5_per_seed": [round(x[1], 4) for x in v],
                        "spread_r5": round(max(x[1] for x in v) - min(x[1] for x in v), 4)})
json.dump({"summary": summary, "store_construction": "per-query: target facts always present, distractors sampled with seed 1000*seed+query_id",
           "elapsed_s": round(time.time() - t0, 1), "model": MODEL,
           "p50_s_per_text": round(statistics.median(lats), 4)},
          open(os.path.join(EV, "summary-arctic-presence-guaranteed.json"), "w"), indent=1)
for s in summary:
    print("store=%-4d w=%-4d R@1=%.3f R@5=%.3f MRR=%.3f spreadR5=%.3f %dB" % (
        s["store"], s["width"], s["recall_at_1_mean"], s["recall_at_5_mean"], s["mrr_mean"],
        s["spread_r5"], s["bytes_per_vector"]))
print("elapsed", round(time.time() - t0, 1), "s")
