#!/usr/bin/env python3
"""v4: up to two near-duplicate decoys per cluster (forms[0] and forms[1] with only the
value substituted, when the substitution matches), so the answer surface must beat one
or two lexically near-identical competitors. 41 of the 60 attempted substitutions match,
which is why the shipped build has 221 documents: 120 answer forms, 60 near-miss decoys,
41 value-swapped near-duplicates (19 clusters with one, 11 with two).
Gate: answer at rank 2-10 for >=60% of queries and baseline hit@1 < 90%."""
import json, os, sys
from build_fixture import CLUSTERS, embed, cos, EMBED_MODEL
from build_fixture_v2 import DECOYS
from build_fixture_v3 import VALPAIR

def main(outdir):
    docs, doc_cluster, doc_kind = [], [], []
    for cid, fam, forms, q in CLUSTERS:
        for f in forms:
            docs.append(f); doc_cluster.append(cid); doc_kind.append("answer")
        for d in DECOYS[cid]:
            docs.append(d); doc_cluster.append(cid); doc_kind.append("decoy")
        correct, wrong = VALPAIR[cid]
        for src in (forms[0], forms[1]):
            nd = src.replace(correct, wrong)
            if nd != src:
                docs.append(nd); doc_cluster.append(cid); doc_kind.append("neardup")
    queries = [(cid, q) for cid, fam, forms, q in CLUSTERS]
    for _, q in queries:
        for d in docs:
            assert q.lower() not in d.lower(), ("query leaks into doc", q)
    de = embed(docs); qe = embed([q for _, q in queries])
    ranks, rows = [], []
    for i, (cid, q) in enumerate(queries):
        scored = sorted(((cos(qe[i], de[j]), j) for j in range(len(docs))), reverse=True)
        rank = next(r+1 for r, (s, j) in enumerate(scored) if doc_cluster[j] == cid and doc_kind[j] == "answer")
        ranks.append(rank)
        rows.append({"qid": cid, "answer_rank": rank, "top1_kind": doc_kind[scored[0][1]],
                     "top1_cluster": doc_cluster[scored[0][1]], "top1_sim": round(scored[0][0], 4)})
    hit1 = sum(1 for r in ranks if r == 1)
    in_gate = sum(1 for r in ranks if 2 <= r <= 10)
    gate = {"embedder": EMBED_MODEL, "docs": len(docs), "queries": len(queries),
            "hit_at_1": hit1, "hit_at_1_pct": round(100*hit1/len(ranks), 1),
            "answer_at_rank_2_to_10": in_gate, "answer_at_rank_2_to_10_pct": round(100*in_gate/len(ranks), 1),
            "rank_histogram": {str(k): ranks.count(k) for k in sorted(set(ranks))},
            "passes_gate": in_gate/len(ranks) >= 0.60 and hit1/len(ranks) < 0.90,
            "gate_rule": "answer surface at rank 2-10 for >=60% of queries AND baseline hit@1 < 90%",
            "fixture_history": [
              "v1 (120 docs, no decoys): hit@1 30/30 = 100% - saturated, gate fail per failure condition (a)",
              "v2 (180 docs, 2 near-miss decoys per cluster): hit@1 19/30 = 63.3%, 11/30 at rank 2-10 (36.7%) - gate fail",
              "v3 (210 docs, +1 value-swapped near-duplicate): hit@1 17/30 = 56.7%, 13/30 at rank 2-10 (43.3%) - gate fail",
              "v4 (221 docs: 120 answer forms + 60 near-miss + 41 value-swapped near-duplicates, 19 clusters with one and 11 with two): this run"]}
    os.makedirs(outdir, exist_ok=True)
    json.dump({"embedder": EMBED_MODEL, "doc_count": len(docs),
               "clusters": [{"id": c, "family": f, "forms": forms, "query": q,
                             "decoys": DECOYS[c],
                             "neardup_decoys": [s.replace(VALPAIR[c][0], VALPAIR[c][1])
                                                for s in (forms[0], forms[1])
                                                if s.replace(VALPAIR[c][0], VALPAIR[c][1]) != s]}
                            for c, f, forms, q in CLUSTERS]},
              open(os.path.join(outdir, "fixture.json"), "w"), indent=2)
    json.dump({"query_count": len(queries), "queries": [{"qid": c, "q": q} for c, q in queries]},
              open(os.path.join(outdir, "queries.json"), "w"), indent=2)
    json.dump({"gate": gate, "per_query": rows}, open(os.path.join(outdir, "prerun_gate.json"), "w"), indent=2)
    print(json.dumps(gate, indent=2))

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "evidence")
