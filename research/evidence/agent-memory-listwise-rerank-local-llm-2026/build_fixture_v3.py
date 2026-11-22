#!/usr/bin/env python3
"""Third decoy pass: add one near-duplicate decoy per cluster whose text equals the
answer's first surface form with only the value substituted. This is the exact
condition a reranker exists to fix (identical wording, wrong value), and it makes
the embedder's ordering non-trivial. Gate unchanged: answer at rank 2-10 for >=60%
of queries and baseline hit@1 < 90%.
"""
import json, os, sys
from build_fixture import CLUSTERS, embed, cos, EMBED_MODEL
from build_fixture_v2 import DECOYS

# cid -> (substring holding the correct value in forms[0], wrong value substring)
VALPAIR = {
 "C01": ("41 minutes", "14 minutes"), "C02": ("10 candidates", "20 candidates"),
 "C03": ("384", "768"), "C04": ("M=16 and efConstruction=200", "M=32 and efConstruction=100"),
 "C05": ("cosine distance", "dot product"), "C06": ("30 days", "90 days"),
 "C07": ("0.94", "0.85"), "C08": ("2,000 rows", "500 rows"),
 "C09": ("03:15 UTC", "01:00 UTC"), "C10": ("7 daily and 4 weekly", "30 daily and 12 weekly"),
 "C11": ("429", "503"), "C12": ("8 seconds", "30 seconds"),
 "C13": ("empty results", "HTTP 500"), "C14": ("85 percent", "95 percent"),
 "C15": ("5 delivery attempts", "12 delivery attempts"), "C16": ("26-char ULID", "16-char UUID"),
 "C17": ("8,192 characters", "2,048 characters"), "C18": ("UTC microsecond integers", "ISO-8601 strings"),
 "C19": ("4 KB", "64 KB"), "C20": ("GIN index", "BRIN index"),
 "C21": ("off by default", "on by default"), "C22": ("--no-write", "--preview-only"),
 "C23": ("11434", "8080"), "C24": ("think=false", "think=true"),
 "C25": ("raw/<arm>/<qid>.txt", "logs/<arm>/<qid>.json"), "C26": ("480 prompt tokens", "1,900 prompt tokens"),
 "C27": ("under 40 tokens", "about 300 output tokens"), "C28": ("5.7 tokens per second", "42 tokens per second"),
 "C29": ("24 minutes", "3 minutes"), "C30": ("per 1,000 searches", "per token processed"),
}

def main(outdir):
    docs, doc_cluster, doc_kind = [], [], []
    for cid, fam, forms, q in CLUSTERS:
        for f in forms:
            docs.append(f); doc_cluster.append(cid); doc_kind.append("answer")
        for d in DECOYS[cid]:
            docs.append(d); doc_cluster.append(cid); doc_kind.append("decoy")
        correct, wrong = VALPAIR[cid]
        nd = forms[0].replace(correct, wrong)
        assert nd != forms[0], (cid, correct)
        docs.append(nd); doc_cluster.append(cid); doc_kind.append("neardup")
    queries = [(cid, q) for cid, fam, forms, q in CLUSTERS]
    assert len(docs) == 210
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
              "v1 (120 docs, no decoys) saturated: hit@1 = 30/30, gate fail per failure condition (a)",
              "v2 (180 docs, 2 near-miss decoys per cluster) under-discriminated: hit@1 = 19/30 (63.3%), only 11/30 at rank 2-10",
              "v3 (210 docs, + 1 near-duplicate decoy per cluster differing only in the value): this run"]}
    os.makedirs(outdir, exist_ok=True)
    json.dump({"embedder": EMBED_MODEL, "doc_count": len(docs), "generated_at_utc": "2026-11-21T17:27:00Z",
               "clusters": [{"id": c, "family": f, "forms": forms, "query": q,
                             "decoys": DECOYS[c], "neardup_decoy": forms[0].replace(VALPAIR[c][0], VALPAIR[c][1])}
                            for c, f, forms, q in CLUSTERS]},
              open(os.path.join(outdir, "fixture.json"), "w"), indent=2)
    json.dump({"query_count": len(queries), "queries": [{"qid": c, "q": q} for c, q in queries]},
              open(os.path.join(outdir, "queries.json"), "w"), indent=2)
    json.dump({"gate": gate, "per_query": rows}, open(os.path.join(outdir, "prerun_gate.json"), "w"), indent=2)
    print(json.dumps(gate, indent=2))

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "evidence")
