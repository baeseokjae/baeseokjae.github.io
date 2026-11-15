#!/usr/bin/env python3
"""Deterministic scoped-retrieval probe harness (fixture generator + scorer).

Reproduces the read-path filter-placement effect described in
research/agent-memory-scoped-retrieval-probe-2026.json:
  (a) post_filter   global top-k, then filter rows by caller tenant in application code
  (b) scoped        caller-tenant candidate set ranked before top-k
  (c) leak          raw global top-k handed to the prompt unfiltered

Vector scoring is exact cosine over every document (no ANN index), so approximation
error cannot be confused with the effect under test. Embeddings come from a local
Ollama endpoint; pass --vectors FILE to rescore committed vectors offline instead.

Usage:
  python3 harness.py --out .                      # embed + score (needs ollama)
  python3 harness.py --out . --vectors vectors.json --offline

Deterministic: fixture text is a pure function of (tenant index, fact index); the
embedding model is pinned by digest in env.json; no randomness and no clock input.
"""
import argparse, json, math, os, sys, time, urllib.request

OLLAMA = os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434")
MODEL = os.environ.get("EMBED_MODEL", "all-minilm:latest")

TENANTS = ["northwind", "contoso", "fabrikam", "initech", "umbrella", "wayne",
           "stark", "cyberdyne", "tyrell", "weyland", "acme", "globex",
           "soylent", "oscorp", "vandelay", "hooli", "pied-piper",
           "massive-dynamic", "dunder-mifflin", "prestige-worldwide",
           "sterling-cooper", "bluth-company", "wonka", "gringotts",
           "monsters-inc", "aperture", "black-mesa", "abstergo", "virtucon", "zorg"]

# (fact name, value templates, query phrasing). Ten fact types per tenant, as planned.
FACTS = [
    ("database host",      ["pg-core-{a}.corp.internal", "mysql-ro-{a}.corp.internal", "pg-shard-{a}.corp.internal"],
     "the primary database host"),
    ("token lifetime",     ["{m} minutes", "{m} minutes", "{m} hours"],
     "the API token lifetime"),
    ("service owner",      ["team-{a}", "team-{a}", "squad-{a}"],
     "the owning team for the billing service"),
    ("queue retry budget", ["{m} attempts", "{m} attempts", "{m} retries"],
     "the queue retry budget"),
    ("region",             ["eu-west-{a}", "us-east-{a}", "ap-south-{a}"],
     "the deployment region"),
    ("cluster version",    ["1.{a}.4", "1.{a}.9", "2.{a}.1"],
     "the Kubernetes cluster version"),
    ("on-call day",        ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
     "the on-call handover day"),
    ("log retention",      ["{m} days", "{m} days", "{m} days"],
     "the log retention window"),
    ("API rate limit",     ["{m} requests per minute", "{m} requests per second", "{m} calls per minute"],
     "the API rate limit"),
    ("cache bucket",       ["cache-{a}-primary", "cache-{a}-replica", "cdn-{a}"],
     "the cache bucket name"),
]

def _num(t, f):
    # deterministic pseudo-random integers, no RNG state
    h = (t * 7919 + f * 104729) % 9973
    return h

def fact_value(t, f):
    _, templates, _ = FACTS[f]
    tpl = templates[_num(t, f) % len(templates)]
    return tpl.format(a=(_num(t, f) % 90) + 1, m=[15, 30, 45, 60, 90, 120, 180, 240, 5, 7][_num(t, f) % 10])

def doc_text(t, f):
    """One memory row. Deliberately generous to the post-filter strategy: the
    tenant slug appears in the row, so a lexical matcher can find gold at all."""
    return f"{FACTS[f][0]} for {TENANTS[t]}: {fact_value(t, f)}"

def single_query(t, f):
    return f"What is {FACTS[f][2]} for {TENANTS[t]}?"

def multi_query(t, f1, f2):
    return f"For {TENANTS[t]}, what are {FACTS[f1][2]} and {FACTS[f2][2]}?"

def embed(texts, batch=32):
    out = []
    for i in range(0, len(texts), batch):
        chunk = texts[i:i + batch]
        body = json.dumps({"model": MODEL, "input": chunk}).encode()
        req = urllib.request.Request(OLLAMA + "/api/embed", data=body,
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=180) as r:
            out.extend(json.loads(r.read())["embeddings"])
    return out

def norm(v):
    n = math.sqrt(sum(x * x for x in v)) or 1.0
    return [x / n for x in v]

def dot(a, b):
    return sum(x * y for x, y in zip(a, b))

def build_fixture(n_tenants):
    rows = []
    for t in range(n_tenants):
        for f in range(len(FACTS)):
            rows.append({"id": f"t{t}-f{f}", "tenant": TENANTS[t], "fact": FACTS[f][0],
                         "text": doc_text(t, f)})
    return rows

def build_queries(n_tenants):
    qs = []
    for t in range(n_tenants):
        for f in range(len(FACTS)):
            qs.append({"qid": f"t{t}-s{f}", "tenant": TENANTS[t], "kind": "single",
                       "text": single_query(t, f), "gold": [f"t{t}-f{f}"]})
        # multi-fact: pair each fact with the one six slots away (wrap), all 10 covered
        for f in range(len(FACTS)):
            g = (f + 6) % len(FACTS)
            if f < g:
                qs.append({"qid": f"t{t}-m{f}-{g}", "tenant": TENANTS[t], "kind": "multi",
                           "text": multi_query(t, f, g), "gold": [f"t{t}-f{f}", f"t{t}-f{g}"]})
    return qs

def run(n_tenants, k, fixtures, qvecs, dvecs, mode):
    docs = fixtures[n_tenants]
    qs = DOCQ[n_tenants]
    per_q = []
    for q in qs:
        qv = qvecs[q["qid"]]
        scored = sorted(((dot(qv, dvecs[d["id"]]), d["id"]) for d in docs), reverse=True)
        raw = [i for _, i in scored[:k]]
        raw_foreign = [i for i in raw if i.split("-")[0] != "t" + str(TENANTS.index(q["tenant"]))]
        if mode == "post_filter":
            kept = [i for i in raw if i.split("-")[0] == "t" + str(TENANTS.index(q["tenant"]))]
            gold_hit = all(g in kept for g in q["gold"])
        elif mode == "scoped":
            own = sorted(((dot(qv, dvecs[d["id"]]), d["id"]) for d in docs
                          if d["tenant"] == q["tenant"]), reverse=True)
            kept = [i for _, i in own[:k]]
            gold_hit = all(g in kept for g in q["gold"])
        else:  # leak: prompt assembled from the raw top-k
            kept = raw
            gold_hit = all(g in raw for g in q["gold"])
        per_q.append({"n": n_tenants, "k": k, "mode": mode, "qid": q["qid"], "kind": q["kind"],
                      "tenant": q["tenant"], "returned": len(kept), "gold_in_context": gold_hit,
                      "raw_foreign": len(raw_foreign), "rank_of_gold": [
                          (i + 1) for i in range(len(scored)) if scored[i][1] in q["gold"]]})
    return per_q

def summarize(per_q):
    out = []
    for mode in ("post_filter", "scoped", "leak"):
        for kind in ("single", "multi", "all"):
            sel = [r for r in per_q if r["mode"] == mode and (kind == "all" or r["kind"] == kind)]
            if not sel:
                continue
            ret = [r["returned"] for r in sel]
            out.append({
                "mode": mode, "kind": kind, "queries": len(sel),
                "mean_returned_rows": round(sum(ret) / len(ret), 3),
                "min_returned_rows": min(ret), "max_returned_rows": max(ret),
                "share_under_filled": round(sum(1 for x in ret if x < sel[0]["k"]) / len(ret), 3),
                "gold_in_context_rate": round(sum(1 for r in sel if r["gold_in_context"]) / len(sel), 3),
                "mean_foreign_rows_in_raw_top_k": round(sum(r["raw_foreign"] for r in sel) / len(sel), 3),
            })
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=".")
    ap.add_argument("--vectors", default=None)
    ap.add_argument("--offline", action="store_true")
    ap.add_argument("--tenants", default="2,5,12,30")
    ap.add_argument("--ks", default="3,5,10")
    a = ap.parse_args()
    ns = [int(x) for x in a.tenants.split(",")]
    ks = [int(x) for x in a.ks.split(",")]
    maxn = max(ns)
    fixtures = {n: build_fixture(n) for n in ns}
    global DOCQ
    DOCQ = {n: build_queries(n) for n in ns}

    docs_all = fixtures[maxn]
    if a.offline:
        v = json.load(open(a.vectors))
        dvecs, qvec = v["doc_vectors"], v["query_vectors"]
        qvecs = {k: norm(x) for k, x in qvec.items()}
        dvecs = {k: norm(x) for k, x in dvecs.items()}
    else:
        t0 = time.time()
        dvecs = {d["id"]: norm(vector) for d, vector in zip(docs_all, embed([d["text"] for d in docs_all]))}
        qtexts = {q["qid"]: q["text"] for q in DOCQ[maxn]}
        qraw = embed([qtexts[q] for q in qtexts])
        qvecs = {q: norm(v) for q, v in zip(qtexts, qraw)}
        print(f"embedded {len(dvecs)} docs + {len(qvecs)} queries in {time.time()-t0:.1f}s", file=sys.stderr)
        json.dump({"doc_vectors": {k: v for k, v in dvecs.items()},
                   "query_vectors": qvecs}, open(os.path.join(a.out, "vectors.json"), "w"))

    all_rows, table = [], []
    for n in ns:
        for k in ks:
            per_q = []
            for mode in ("post_filter", "scoped", "leak"):
                per_q.extend(run(n, k, fixtures, qvecs, dvecs, mode))
            all_rows.extend(per_q)
            for s in summarize(per_q):
                s["n_tenants"] = n
                s["k"] = k
                table.append(s)

    with open(os.path.join(a.out, "results.jsonl"), "w") as fh:
        for r in all_rows:
            fh.write(json.dumps(r, sort_keys=True) + "\n")
    with open(os.path.join(a.out, "summary.json"), "w") as fh:
        json.dump(table, fh, indent=1, sort_keys=True)
    with open(os.path.join(a.out, "fixture.jsonl"), "w") as fh:
        for d in docs_all:
            fh.write(json.dumps(d, sort_keys=True) + "\n")
    print(json.dumps(table, indent=1, sort_keys=True))

if __name__ == "__main__":
    main()
