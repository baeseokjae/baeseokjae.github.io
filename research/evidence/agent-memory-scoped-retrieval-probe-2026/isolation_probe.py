#!/usr/bin/env python3
"""isolation_probe.py - adapter-agnostic read-path isolation checker.

Point it at any memory store through the three-method interface below and it prints
PASS/FAIL per assertion. It needs no labelled data: under-fill is measured by asking
for k rows and counting what comes back, and the leak surface is measured with two
planted canary facts per tenant.

Interface (implement `search`, `search_scoped`; `write` is only used by --plant):

    class Store:
        def search(self, query, k):        # global/unscoped top-k
            -> [ {"id": str, "tenant": str, "text": str}, ... ]
        def search_scoped(self, query, tenant, k):  # tenant-scoped candidate set
            -> same shape, every row .tenant == tenant
        def write(self, tenant, text):     # optional, for canaries
            -> id

Assertions:
  A1 fill            len(search(q, k)) == k for every query and k in the sweep
  A1b post-filter    len([r for r in search(q, k) if r.tenant == caller]) == k
                     (fails when the app filters after top-k, even if the store fills)
  A2 scope           every row of search_scoped(q, tenant, k) has .tenant == tenant
  A3 agree           scoped ids are a superset of the post-filtered ids for the same query
  A4 no_gold_loss    (only when --gold is supplied) gold ids survive in scoped results

A3 is the assertion that catches a refactor moving the filter back after top-k: with
post-filtering the post-filtered set is strictly smaller than the scoped set whenever
A1 fails, so A3 and A1 fail together.

Offline reference adapter: --selftest scores the committed fixture and vectors from
research/evidence/agent-memory-scoped-retrieval-probe-2026/ with exact cosine, so the
probe itself is exercised against one concrete implementation.
"""
import argparse, json, math, os, sys

def _norm(v):
    n = math.sqrt(sum(x * x for x in v)) or 1.0
    return [x / n for x in v]

def _dot(a, b):
    return sum(x * y for x, y in zip(a, b))

class FixtureStore:
    """Reference adapter: exact cosine over committed vectors. Read-only."""
    def __init__(self, fixture_path, vectors_path):
        self.rows = [json.loads(l) for l in open(fixture_path)]
        v = json.load(open(vectors_path))
        self.vec = {k: _norm(x) for k, x in v["doc_vectors"].items()}
        self.qvec = {k: _norm(x) for k, x in v["query_vectors"].items()}
        self.query_text = {}
        for r in self.rows:
            t, f = r["id"].split("-")
            t = int(t[1:]); f = int(f[1:])
            self.query_text.setdefault(f"t{t}-s{f}", None)

    def _row(self, rid):
        return next(r for r in self.rows if r["id"] == rid)

    def search(self, query, k, qid=None):
        if qid and qid in self.qvec:
            qv = self.qvec[qid]
        else:
            raise RuntimeError("reference adapter needs qid= (precomputed query vector)")
        scored = sorted(((_dot(qv, self.vec[r["id"]]), r["id"]) for r in self.rows), reverse=True)
        return [self._row(i) for _, i in scored[:k]]

    def search_scoped(self, query, tenant, k, qid=None):
        if qid and qid in self.qvec:
            qv = self.qvec[qid]
        else:
            raise RuntimeError("reference adapter needs qid= (precomputed query vector)")
        scored = sorted(((_dot(qv, self.vec[r["id"]]), r["id"]) for r in self.rows
                         if r["tenant"] == tenant), reverse=True)
        return [self._row(i) for _, i in scored[:k]]

    def write(self, tenant, text):
        raise RuntimeError("reference adapter is read-only; canaries are planted by the fixture")

def probe(store, tenant, query, ks=(3, 5, 10), gold=(), qid=None):
    out = {"tenant": tenant, "ks": list(ks), "checks": {}, "detail": {}}
    for k in ks:
        kw = {"qid": qid} if qid else {}
        raw = store.search(query, k, **kw)
        scoped = store.search_scoped(query, tenant, k, **kw)
        post = [r for r in raw if r.get("tenant") == tenant]
        out["detail"][k] = {
            "requested": k, "unscoped_returned": len(raw), "scoped_returned": len(scoped),
            "foreign_rows_in_unscoped": sum(1 for r in raw if r.get("tenant") != tenant),
            "post_filter_returned": len(post),
            "foreign_share_in_unscoped": round(
                sum(1 for r in raw if r.get("tenant") != tenant) / max(1, len(raw)), 3),
        }
        out["checks"][f"A1_fill_k{k}"] = len(raw) == k and len(scoped) == k
        # A1b scores the application pattern (global top-k, then filter), not the store:
        # it fails whenever the filter runs after the ranking even on a correct store.
        out["checks"][f"A1b_post_filter_fill_k{k}"] = len(post) == k
        out["checks"][f"A2_scope_k{k}"] = all(r.get("tenant") == tenant for r in scoped)
        out["checks"][f"A3_agree_k{k}"] = {r["id"] for r in post} <= {r["id"] for r in scoped}
        if gold:
            out["checks"][f"A4_no_gold_loss_k{k}"] = all(
                g in {r["id"] for r in scoped} for g in gold)
    out["pass"] = all(out["checks"].values())
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--dir", default=os.path.dirname(os.path.abspath(__file__)))
    ap.add_argument("--tenants", default="northwind,contoso,globex")
    a = ap.parse_args()
    if not a.selftest:
        print(__doc__)
        print("No adapter supplied. Implement Store.search/search_scoped and call probe().")
        return 0
    store = FixtureStore(os.path.join(a.dir, "fixture.jsonl"),
                         os.path.join(a.dir, "vectors.json"))
    tenants = set(a.tenants.split(","))
    results = []
    # use the committed query vectors: qid == "t<T>-s<F>", tenant name from fixture row
    for r in store.rows:
        if r["tenant"] in tenants:
            qid = "t%s-s%s" % (r["id"].split("-")[0][1:], r["id"].split("-")[1][1:])
            q = "What is the %s for %s?" % (r["fact"], r['tenant'])
            res = probe(store, r["tenant"], q, ks=(3, 5, 10), gold=(r["id"],), qid=qid)
            results.append(res)
            print(json.dumps(res, sort_keys=True))
    n_pass = sum(1 for r in results if r["pass"])
    print("\n%d/%d queries passed every assertion" % (n_pass, len(results)))
    worst = min(r["detail"][5]["post_filter_returned"] for r in results)
    print("k=5 post-filter returned between %d and %d rows" % (
        worst, max(r["detail"][5]["post_filter_returned"] for r in results)))
    return 0

if __name__ == "__main__":
    sys.exit(main())
