# Method - agent-memory-embedding-dimensions-recall-curve-2026

Environment: ollama 0.20.3, Linux aarch64, 2 vCPU, 11.0 GiB RAM, no GPU.
Models (digests from /api/tags on 2026-11-21):
- snowflake-arctic-embed:33m  e8db018629b498a0a1a2eadbe8ab29477c1d7c4b6ba8ff2a69b0a6ed193713be (33M, bert, F16, 384 native dims)
- nomic-embed-text:latest     0a109f422b47e3a30ba2b10eca18548e944e8a23073ee3f3e947efcf3c45e59f (137M, 768 native dims)

## Fixture (fixture.json, generator seed 20261121, query seed 77)
800 fact strings = 200 subjects x 4 surface-form paraphrases of the same underlying fact
(subject, memory segment, retention days, per-agent MB cap), each variant carrying one unique
codename token. 40 queries: 20 cluster-level (answer = any of the 4 variants of one subject's fact)
and 20 exact-paraphrase (answer = one specific variant, addressed by its codename).

## Width semantics check (semantics-check.json), run first
For 5 probe texts per model and d in {32,64,128,256}: call /api/embed with dimensions=d and compare
against L2-normalised full[:d]. Result: returned length == d, unit norm to 1e-7, and max abs
difference vs normalise(full[:d]) <= 2.6e-07 for both models. Conclusion: the option truncates then
renormalises; it does not re-embed. Widths below native in the curve are therefore computed by
normalising the full vector's prefix, which is the same operation.

## Retrieval
Embeddings via POST /api/embed, batches of 32 facts and 8 queries, cosine similarity (vectors are
unit norm), top-10 ranked, metrics recall@1, recall@5, MRR. Widths: {384,256,128,64} for the 384-dim
encoder, {768,256,128,64} for the 768-dim encoder.

## Store construction (two passes - the first one is superseded and kept for audit)
run-1: store = random subset of the 800-fact corpus. This confounds absence with failure: a query
whose target fact is not in the subset can never be retrieved, so recall rose with store size for the
wrong reason. Its rows are preserved unedited as results.csv and are not used for any claim.
run-2: store = the query's own target facts plus random distractors up to the store size, drawn with
Random(1000*seed+query_id), seeds 1..3; targets are therefore always indexed and only crowding varies.
This is the basis of every arctic claim (results-arctic-presence-guaranteed.csv,
summary-arctic-presence-guaranteed.json). The nomic model was scored only at the full 800-fact store,
where the entire corpus is indexed and presence is guaranteed by construction (summary.json).

## Limits
Template-generated sentences (optimistic absolute recall), 800 facts max, one CPU host, no
quantisation, no reranking, no task prefixes for nomic-embed-text (vendor requires them, so its
absolute recall is understated). Latency is indicative, not a serving benchmark.

Total wall time: 322.7 s for run-1 (nomic embedding dominated: 319.8 s for 800 facts), 35.0 s for
run-2 (arctic only).
