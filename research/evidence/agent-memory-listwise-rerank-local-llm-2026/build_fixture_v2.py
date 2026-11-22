#!/usr/bin/env python3
"""Rebuild pass: add near-miss decoys that share the entity/attribute and differ only
in the value, so the embedder must resolve a numeric/detail distinction rather than a
topic. Gate: answer cluster at rank 2-10 for >=60% of queries and baseline hit@1 < 90%.
"""
import json, math, os, sys, urllib.request
from build_fixture import CLUSTERS, post, embed, cos, EMBED_MODEL

# two decoys per cluster: same entity and attribute, wrong value, close surface wording
DECOYS = {
 "C01": ["A rebuild of the recall-svc index takes 14 minutes on the two-core host.",
         "Full recall-svc index rebuild: about 90 minutes on 2 vCPU."],
 "C02": ["recall-svc returns 20 candidates per query by default.",
         "Default top-k in recall-svc is 5 candidates."],
 "C03": ["The 33m arctic encoder outputs 768-dimensional vectors.",
         "Vectors from the small arctic embedder are 1024 floats wide."],
 "C04": ["HNSW is built with M=32 and efConstruction=100.",
         "Graph build parameters: M=8, efConstruction=400."],
 "C05": ["Vector search scores candidates with dot product, not cosine.",
         "Query-time metric is inner product; cosine is disabled."],
 "C06": ["Episodic memories expire after 90 days unless pinned.",
         "Unpinned episodic rows are dropped at 7 days."],
 "C07": ["Compaction merges duplicates above 0.85 cosine similarity.",
         "The dedupe pass collapses records above 0.99 similarity."],
 "C08": ["Pinned memories are capped at 500 rows per tenant.",
         "Each tenant may pin at most 20,000 memories."],
 "C09": ["The purge of soft-deleted rows runs nightly at 01:00 UTC.",
         "Soft-deleted records are swept at 04:45 UTC each night."],
 "C10": ["Backups keep 30 daily and 12 weekly snapshots.",
         "Snapshot retention is three daily plus two weekly copies."],
 "C11": ["Writes above 200 requests per second per tenant get HTTP 503.",
         "Over 50 rps for a tenant the limiter answers 403, not 429."],
 "C12": ["The embedder times out at 30 seconds with no retries.",
         "Embedding aborts after 2 seconds and retries five times."],
 "C13": ["A stale index returns HTTP 500 instead of empty results.",
         "During index lag queries return the last cached answer."],
 "C14": ["Recall-svc goes read-only at 95% disk usage.",
         "Read-only mode engages once disk crosses 70%."],
 "C15": ["Poison messages are dead-lettered after 12 delivery attempts.",
         "The DLQ receives a message after 3 failed tries."],
 "C16": ["A memory row is keyed on tenant_id and a 16-char UUID.",
         "Row identity is an autoincrement integer plus agent_id."],
 "C17": ["The stored memory text is capped at 2,048 characters.",
         "Text payloads are limited to 32,768 characters."],
 "C18": ["Timestamps are stored as ISO-8601 strings with an offset.",
         "created_at is a millisecond epoch integer, local time."],
 "C19": ["The metadata JSONB blob is limited to 64 KB per row.",
         "Per-row metadata is capped at 512 bytes."],
 "C20": ["Scope tags are a text array with a BRIN index.",
         "The scope column is a single text field indexed with btree."],
 "C21": ["The SDK enables reranking by default for all queries.",
         "Clients call a reranker automatically unless you opt out."],
 "C22": ["The dry-run CLI flag is --preview-only.",
         "Use --check to run a command without persisting."],
 "C23": ["Local model calls go to ollama on port 8080.",
         "The model server binds port 3000."],
 "C24": ["qwen3 needs think=true to produce a usable answer.",
         "Setting think to true suppresses the reasoning block."],
 "C25": ["Verbatim answers are stored in logs/<arm>/<qid>.json.",
         "Per-query output is appended to runs.csv, one row per arm."],
 "C26": ["A ten-candidate rerank uses about 1,900 prompt tokens.",
         "Top-10 rerank input is roughly 120 tokens."],
 "C27": ["A ten-item ordering emits about 300 output tokens.",
         "Rerank answers run to about 120 output tokens."],
 "C28": ["qwen3:0.6b generates about 42 tokens per second on this host.",
         "Throughput here is roughly 1.1 tok/s with the 0.6b model."],
 "C29": ["A 30-query rerank sweep costs about 3 minutes of wall clock.",
         "Thirty reranked queries take roughly 2 hours end to end."],
 "C30": ["Hosted cross-encoder reranking is billed per token processed.",
         "Cross-encoder vendors charge a flat monthly fee, not per search."],
}

def main(outdir):
    docs, doc_cluster, doc_kind = [], [], []
    for cid, fam, forms, q in CLUSTERS:
        for f in forms:
            docs.append(f); doc_cluster.append(cid); doc_kind.append("answer")
        for d in DECOYS[cid]:
            docs.append(d); doc_cluster.append(cid); doc_kind.append("decoy")
    queries = [(cid, q) for cid, fam, forms, q in CLUSTERS]
    assert len(docs) == 180
    for _, q in queries:
        for d in docs:
            assert q.lower() not in d.lower(), ("query leaks into doc", q)
    de = embed(docs); qe = embed([q for _, q in queries])
    ranks, rows = [], []
    for i, (cid, q) in enumerate(queries):
        scored = sorted(((cos(qe[i], de[j]), j) for j in range(len(docs))), reverse=True)
        # rank = position of the best ANSWER-surface doc (decoy does not count as a hit)
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
            "gate_rule": "answer surface at rank 2-10 for >=60% of queries AND baseline hit@1 < 90%"}
    os.makedirs(outdir, exist_ok=True)
    json.dump({"embedder": EMBED_MODEL, "doc_count": len(docs),
               "clusters": [{"id": c, "family": f, "forms": forms, "query": q, "decoys": DECOYS[c]}
                            for c, f, forms, q in CLUSTERS]},
              open(os.path.join(outdir, "fixture.json"), "w"), indent=2)
    json.dump({"query_count": len(queries), "queries": [{"qid": c, "q": q} for c, q in queries]},
              open(os.path.join(outdir, "queries.json"), "w"), indent=2)
    json.dump({"gate": gate, "per_query": rows}, open(os.path.join(outdir, "prerun_gate.json"), "w"), indent=2)
    print(json.dumps(gate, indent=2))

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "evidence")
