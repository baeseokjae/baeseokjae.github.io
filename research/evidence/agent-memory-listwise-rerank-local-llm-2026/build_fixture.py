#!/usr/bin/env python3
"""Build the 30-cluster / 120-document fixture and the 30-query set, then run the
pre-run gate: embedder must place the answer cluster at rank 2-10 for >=60% of queries.

Facts, surface forms and queries are authored in this file. Surface forms are written
as ordinary ops notes, not template slots, so paraphrase distance is realistic.
"""
import json, math, os, sys, urllib.request

OLLAMA = os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434")
EMBED_MODEL = "snowflake-arctic-embed:33m"

# (cluster_id, family, [4 surface forms], query)
CLUSTERS = [
 ("C01","index",[
  "recall-svc index rebuild takes 41 minutes on the 2 vCPU box.",
  "A full rebuild of the recall-svc index costs about 41 minutes of wall clock.",
  "On this two-core host the index rebuild for recall-svc finishes in roughly 41 min.",
  "Rebuilding recall-svc's index: expect 41 minutes, longer if the box is busy."],
  "How long does a full index rebuild of the recall service take on a two-core host?"),
 ("C02","index",[
  "The default top-k for recall-svc queries is 10 candidates.",
  "recall-svc returns 10 candidates per query unless the caller asks for more.",
  "Top-k defaults to ten in recall-svc.",
  "If you do not set k yourself, the recall service gives back ten hits."],
  "What is the default number of candidates returned by the recall service?"),
 ("C03","index",[
  "Embedding dimension on the 33m arctic model is 384 floats.",
  "The arctic 33m encoder emits 384-dimensional vectors.",
  "Vectors from the small arctic embedder are 384 floats wide.",
  "Dimension of the 33m arctic embedding is 384."],
  "How many dimensions does the small arctic embedding model produce?"),
 ("C04","index",[
  "The HNSW graph uses M=16 and efConstruction=200.",
  "Graph parameters are M equal to 16 and efConstruction set to 200.",
  "We build HNSW with M=16, efConstruction=200.",
  "Index construction uses sixteen links per node and a 200-wide build beam."],
  "Which HNSW build parameters are configured for the vector index?"),
 ("C05","index",[
  "Similarity search uses cosine distance, not dot product.",
  "Distance metric in recall-svc is cosine.",
  "We score with cosine similarity; dot product is disabled.",
  "Cosine, not inner product, is the metric used at query time."],
  "Which distance metric does the vector search use at query time?"),

 ("C06","retention",[
  "Episodic memories are dropped after 30 days unless pinned.",
  "Retention for episodic rows is thirty days, pinning exempts them.",
  "Unpinned episodic records expire at 30 days.",
  "Anything episodic older than 30 days is deleted unless it carries a pin."],
  "How long are unpinned episodic records kept before expiry?"),
 ("C07","retention",[
  "Compaction merges duplicate facts when their cosine similarity exceeds 0.94.",
  "The dedupe pass collapses two records above 0.94 cosine similarity.",
  "Duplicates are merged above a 0.94 similarity cutoff.",
  "Compaction threshold for merging near-identical memories is 0.94."],
  "At what similarity score does compaction merge duplicate memories?"),
 ("C08","retention",[
  "Pinned memories never expire but are capped at 2,000 rows per tenant.",
  "The pin cap is 2000 entries for each tenant; pins do not expire.",
  "Each tenant may pin at most 2,000 memories, which then live forever.",
  "Pins are permanent, with a ceiling of two thousand per tenant."],
  "How many permanently pinned memories can one tenant keep?"),
 ("C09","retention",[
  "Soft-deleted rows are purged by a nightly job at 03:15 UTC.",
  "Purge of soft-deleted records runs nightly at 03:15 UTC.",
  "The 03:15 UTC nightly task removes rows marked deleted.",
  "Deleted-but-not-purged rows disappear during the 03:15 UTC sweep."],
  "When does the nightly purge of soft-deleted rows run?"),
 ("C10","retention",[
  "Backups keep 7 daily and 4 weekly snapshots.",
  "Snapshot retention is seven daily plus four weekly copies.",
  "We hold 7 daily backups and 4 weekly ones.",
  "Backup rotation preserves a week of dailies and a month of weeklies."],
  "How many daily and weekly backup snapshots are retained?"),

 ("C11","failure",[
  "Writes fail with 429 when the tenant exceeds 50 requests per second.",
  "The rate limiter returns 429 above 50 rps for a tenant.",
  "Exceeding fifty requests per second per tenant yields HTTP 429.",
  "A tenant over 50 req/s gets throttled with a 429 response."],
  "Which error is returned when a tenant exceeds its write rate limit?"),
 ("C12","failure",[
  "The embedder times out at 8 seconds and retries twice.",
  "Embedding calls abort after 8s with two retries.",
  "Timeout on the embedding backend is eight seconds, retry budget two.",
  "If embedding takes longer than 8 seconds we retry it twice then fail."],
  "What is the embedding call timeout and retry budget?"),
 ("C13","failure",[
  "A stale index returns empty results instead of an error.",
  "When the index lags, queries come back empty rather than erroring.",
  "Stale index state produces zero hits silently.",
  "Readers see no results during index lag; no exception is raised."],
  "What happens to queries while the index is stale?"),
 ("C14","failure",[
  "The recall service drops to read-only mode when disk usage hits 85 percent.",
  "At 85% disk full, recall-svc switches to read-only.",
  "Read-only mode engages once disk crosses 85%.",
  "Disk pressure at 85 percent blocks writes by forcing read-only operation."],
  "At what disk usage does the service become read-only?"),
 ("C15","failure",[
  "Poison messages go to a dead-letter queue after 5 delivery attempts.",
  "Five failed deliveries move a message to the DLQ.",
  "The dead-letter queue catches messages after 5 tries.",
  "After five attempts a bad message is parked in the DLQ."],
  "How many delivery attempts before a message is dead-lettered?"),

 ("C16","schema",[
  "Every memory row carries tenant_id, agent_id, and a 26-char ULID.",
  "Row identity is a 26-character ULID plus tenant and agent columns.",
  "Keys: tenant_id, agent_id, and ulid (26 chars).",
  "The primary key columns are tenant_id, agent_id and a 26-char ULID."],
  "Which columns identify a memory row?"),
 ("C17","schema",[
  "The memory text column is capped at 8,192 characters.",
  "Text payloads are limited to 8192 characters.",
  "We truncate anything past 8,192 characters in the body field.",
  "Maximum stored text length per memory is 8192 chars."],
  "What is the maximum length of stored memory text?"),
 ("C18","schema",[
  "Timestamps are stored as UTC microsecond integers, not ISO strings.",
  "created_at is a microsecond epoch integer in UTC.",
  "We keep time as integer microseconds since epoch, UTC.",
  "Dates live as UTC microsecond integers rather than formatted text."],
  "How are timestamps represented in the memory table?"),
 ("C19","schema",[
  "Metadata is a JSONB blob limited to 4 KB per row.",
  "The metadata column holds JSONB up to 4 KB.",
  "4 KB is the ceiling for the JSONB metadata field.",
  "Per-row metadata is capped at four kilobytes of JSONB."],
  "What is the size limit on the metadata column?"),
 ("C20","schema",[
  "Scope tags are a text array with a GIN index.",
  "scope_tags is text[] indexed with GIN.",
  "We index the scope tag array using GIN.",
  "A GIN index covers the text-array scope column."],
  "How is the scope tag column indexed?"),

 ("C21","tooling",[
  "The rerank stage is optional and off by default in the SDK.",
  "SDKs ship with reranking disabled unless you enable it.",
  "By default the client does not call any reranker.",
  "Reranking must be turned on explicitly; the default client skips it."],
  "Is reranking enabled by default in the client SDK?"),
 ("C22","tooling",[
  "The CLI flag for a dry run is --no-write.",
  "Use --no-write to preview without persisting.",
  "Dry runs are invoked with the --no-write switch.",
  "Passing --no-write makes the command read-only."],
  "Which command-line flag performs a dry run without writing?"),
 ("C23","tooling",[
  "Local inference is served by ollama on port 11434.",
  "ollama listens on 11434 for local model calls.",
  "The model server binds 11434.",
  "Port 11434 hosts the local ollama endpoint."],
  "Which port does the local model server listen on?"),
 ("C24","tooling",[
  "Thinking mode must be disabled with think=false for qwen3.",
  "qwen3 needs think=false to skip its reasoning block.",
  "Set think to false or qwen3 emits a long scratchpad first.",
  "Disabling the think flag is required before qwen3 answers directly."],
  "How do you stop qwen3 from emitting its reasoning scratchpad?"),
 ("C25","tooling",[
  "The eval harness records per-query output in raw/<arm>/<qid>.txt.",
  "Raw model text is written under raw per arm and query id.",
  "Each arm stores its verbatim answers in a raw folder.",
  "Audit output lives at raw/<arm>/<query_id>.txt."],
  "Where does the harness save verbatim model output for auditing?"),

 ("C26","cost",[
  "A rerank over 10 candidates consumes about 480 prompt tokens.",
  "Top-10 rerank prompts run roughly 480 tokens of input.",
  "Input cost of the k=10 rerank is near 480 tokens.",
  "Ten candidates plus instructions come to about 480 prompt tokens."],
  "How many prompt tokens does a ten-candidate rerank use?"),
 ("C27","cost",[
  "Output for a reordered list of 10 ids is under 40 tokens.",
  "Rerank answers stay below forty output tokens.",
  "The model emits fewer than 40 tokens for a ten-item ordering.",
  "Expect under 40 tokens of output for the reordered ids."],
  "How many output tokens does an ordering of ten ids take?"),
 ("C28","cost",[
  "qwen3:0.6b generates about 5.7 tokens per second on this host.",
  "Throughput here is roughly 5.7 tok/s for the 0.6b qwen3 model.",
  "This box sustains 5.7 tokens/second with qwen3 0.6b.",
  "Generation speed measured on the host: 5.7 tok/s."],
  "What generation speed does the small qwen model reach on this machine?"),
 ("C29","cost",[
  "A 30-query rerank sweep costs about 24 minutes of wall clock.",
  "Thirty reranked queries take roughly 24 minutes end to end.",
  "The full 30-query pass runs for around 24 min.",
  "Budget about 24 minutes for a thirty-query rerank sweep."],
  "How long does a full thirty-query rerank sweep take?"),
 ("C30","cost",[
  "Hosted cross-encoder reranking is billed per 1,000 searches.",
  "Cross-encoder vendors charge per thousand search requests.",
  "Pricing for hosted rerankers is quoted per 1k searches.",
  "Vendors price cross-encoder reranks per thousand queries."],
  "How do hosted cross-encoder vendors price their reranking?"),
]

def post(path, payload, timeout=120):
    req = urllib.request.Request(OLLAMA + path, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())

def embed(texts):
    out = []
    for t in texts:
        r = post("/api/embed", {"model": EMBED_MODEL, "input": t})
        out.append(r["embeddings"][0])
    return out

def cos(a, b):
    d = sum(x*y for x, y in zip(a, b))
    na = math.sqrt(sum(x*x for x in a)); nb = math.sqrt(sum(y*y for y in b))
    return d/(na*nb) if na and nb else 0.0

def main(outdir):
    docs, doc_cluster = [], []
    for cid, fam, forms, q in CLUSTERS:
        for f in forms:
            docs.append(f); doc_cluster.append(cid)
    queries = [(cid, q) for cid, fam, forms, q in CLUSTERS]
    assert len(docs) == 120 and len(queries) == 30
    # disjointness: no query string may appear verbatim in any doc
    for _, q in queries:
        for d in docs:
            assert q.lower() not in d.lower(), ("query leaks into doc", q)
    de = embed(docs); qe = embed([q for _, q in queries])
    ranks, rows = [], []
    for i, (cid, q) in enumerate(queries):
        scored = sorted(((cos(qe[i], de[j]), j) for j in range(len(docs))), reverse=True)
        rank = next(r+1 for r, (s, j) in enumerate(scored) if doc_cluster[j] == cid)
        top1 = doc_cluster[scored[0][1]]
        ranks.append(rank)
        rows.append({"qid": cid, "query": q, "answer_rank": rank,
                     "top1_cluster": top1, "top1_sim": round(scored[0][0], 4),
                     "answer_sim": round(next(s for s, j in scored if doc_cluster[j] == cid), 4)})
    hit1 = sum(1 for r in ranks if r == 1)
    in_gate = sum(1 for r in ranks if 2 <= r <= 10)
    gate = {
        "embedder": EMBED_MODEL, "docs": len(docs), "queries": len(queries),
        "hit_at_1": hit1, "hit_at_1_pct": round(100*hit1/len(ranks), 1),
        "answer_at_rank_2_to_10": in_gate, "answer_at_rank_2_to_10_pct": round(100*in_gate/len(ranks), 1),
        "rank_histogram": {str(k): ranks.count(k) for k in sorted(set(ranks))},
        "passes_gate": (2 <= 0) or (in_gate/len(ranks) >= 0.60 and hit1/len(ranks) < 0.90),
        "gate_rule": "answer cluster at rank 2-10 for >=60% of queries AND baseline hit@1 < 90%",
    }
    os.makedirs(outdir, exist_ok=True)
    json.dump({"generated_by": "build_fixture.py", "embedder": EMBED_MODEL,
               "clusters": [{"id": c, "family": f, "forms": forms, "query": q} for c, f, forms, q in CLUSTERS]},
              open(os.path.join(outdir, "fixture.json"), "w"), indent=2)
    json.dump({"query_count": len(queries), "queries": [{"qid": c, "q": q} for c, q in queries]},
              open(os.path.join(outdir, "queries.json"), "w"), indent=2)
    json.dump({"gate": gate, "per_query": rows}, open(os.path.join(outdir, "prerun_gate.json"), "w"), indent=2)
    print(json.dumps(gate, indent=2))

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "evidence")
