---
title: "Zep Temporal Memory and Stale Facts: A Reproducible 30-Case Fixture (2026)"
date: 2026-10-30T00:00:00+00:00
lastmod: 2026-11-24T11:45:00+00:00
tags:
  - Zep
  - Graphiti
  - temporal knowledge graph
  - agent memory
  - stale facts
  - fact invalidation
  - bitemporal
  - knowledge graph
  - memory architecture
  - reproducible fixture
description: "A 30-case, stdlib-only fixture that separates stale facts caused by a store's invalidation policy from stale facts caused by extraction error, with the full 16-cell result matrix."
cover:
  image: /images/zep-temporal-memory-stale-fact-fixture-2026-presentation.png
  alt: 'Table of stale-return rates from the 30-case fixture: append-only recency and last-write-wins upsert return a superseded value in 66.7% of current-truth queries, both bitemporal policies return none, and without a query-time as-of predicate the bitemporal store answers only 13.3% of 2026-08-01 queries correctly.'
  caption: 'Four modelled policies, 30 cases per cell, clean extraction arm · fixture output, not a vendor benchmark'
draft: false
schema: "schema-zep-temporal-memory-stale-fact-fixture-2026"
---

An agent answers "your plan is the Starter tier" three weeks after the account moved to Enterprise. The fact is in the store. The store has timestamps. The answer is still wrong. When that happens the team usually has three suspects and no way to tell them apart: the extraction step filed something incorrectly, the store's invalidation rule never closed the old fact, or the retrieval query asked the wrong question. This post is a fixture that splits those three apart on paper and in code, so you can tell which one you are looking at. To be precise about the scope: what the fixture exercises is four modelled invalidation policies, not Zep or Graphiti themselves — neither product is run anywhere below. The governance version of the same argument is in [the anatomy of persistent memory](/posts/anatomy-of-persistent-memory-contextnest-vs-mem0-vs-zep/); this post is the measurement that argument does not carry.

## What Zep and Graphiti actually claim about temporal invalidation

The primary source is [arXiv:2501.13956, "Zep: A Temporal Knowledge Graph Architecture for Agent Memory"](https://arxiv.org/abs/2501.13956), submitted 2025-01-20 by Rasmussen, Paliychuk, Beauvais, Ryan and Chalef. All five authors are Zep-affiliated, and as of 2026-10-30 the arXiv API lists a single version, v1. The abstract reports Deep Memory Retrieval accuracy of 94.8% against 93.4% for MemGPT, and LongMemEval accuracy improvements of up to 18.5% with a 90% latency reduction against "baseline implementations". Those are vendor-authored claims. This post does not re-run them, and nothing below should be read as a check on them.

The framework documentation is more specific about the mechanism. [The Graphiti README](https://raw.githubusercontent.com/getzep/graphiti/main/README.md) states that facts "have validity windows", that "when information changes, old facts are invalidated — not deleted", and that a caller can "query what's true now, or what was true at any point in time". Its comparison table contrasts "explicit bi-temporal tracking with automatic fact invalidation" against "basic timestamp tracking". [The Graphiti docs overview](https://help.getzep.com/graphiti/getting-started/overview) describes the framework as covering "entity and edge extraction, the bi-temporal model, fact invalidation, and hybrid retrieval", and says edges "include temporal metadata to record relationship lifecycles". Repository metadata re-read on 2026-11-24 from [the GitHub REST API](https://api.github.com/repos/getzep/graphiti) shows Apache-2.0, 33,049 stars, last push 2026-11-24T00:19:58Z, and [the latest release](https://api.github.com/repos/getzep/graphiti/releases/latest) tagged mcp-v1.1.4 published 2026-11-23T21:44:16Z; the 2026-10-30 read recorded 32,367 stars with v0.31.2. Metadata only: no Graphiti process, graph database or LLM extraction call was made for this article.

That distinction matters because documentation describes a design contract, not observed behaviour. If the paper's pages go deeper on what those benchmarks measure, [the source-based review of Zep's paper](/posts/zep-ai-agent-memory-review-2026/) covers it; this page deliberately does not re-litigate it.

## Why vendor benchmarks cannot answer the stale-fact question

DMR and LongMemEval score end-task answers. Neither reports a stale-return rate, and neither separates an error caused by the store's invalidation rule from an error caused by a fact that was never extracted correctly in the first place. A model that answers a temporal question well can still be reading a superseded edge; a model that answers badly may simply have been handed the wrong fact. The paper and the framework documentation, as of 2026-10-30, do not publish a measurement that isolates the two — which is not the same as claiming nobody has measured it, only that these four artifacts do not.

So the useful question for a team is narrower than "is this memory layer accurate": given the same 30 changing facts, does the invalidation policy change how often a superseded value comes back, and how much of the residual error is extraction?

## The fixture: 30 cases, four policies, two instants, two extraction arms

The fixture is [scripts/stale_fact_fixture.py](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/zep-temporal-memory-stale-fact-fixture-2026/scripts/stale_fact_fixture.py) — Python standard library only, no network at run time, no model, no container. Its input is a frozen dataset of 30 scripted facts, [fixtures/stale_fact_cases.json](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/zep-temporal-memory-stale-fact-fixture-2026/fixtures/stale_fact_cases.json): each case names an entity, an attribute, and two or three events carrying a value, a valid-time window and an ingestion timestamp. The fixture validates that each case's windows are disjoint and that at most one event covers each evaluation instant — with deliberate zero-coverage instants where the truthful answer is "no active fact" (20 of the 60 case-instant pairs: the ten late-arriving corrections fall into a gap between windows at 2026-08-01, and the ten time-bounded cases have nothing valid left at 2026-10-29) — so the correct answer at any moment is known by construction rather than by judgement.

The cases cover three change shapes. Ten are in-order updates, where ingestion order agrees with valid-time order. Ten are late-arriving corrections, where a fact for a historical window is ingested after the current value, so the most recently ingested edge is not the current truth. Ten are time-bounded validity, where the attribute simply lapsed, so the truthful current answer is "no active fact".

Four store policies are implemented in roughly fifteen lines each, as stand-ins for design patterns rather than for any product: append-only with recency ranking, last-write-wins upsert, bitemporal invalidation (supersession stamped from *valid-time* order, an edge closed at its successor's `valid_from`), and bitemporal invalidation plus a query-time as-of predicate. Each policy is evaluated at two instants — "what is X now" at 2026-10-29 and "what was X on 2026-08-01" — and under two extraction conditions: a clean store, and a seeded arm in which 3 of 30 cases (10%) have the edge covering the current instant stored under a wrong attribute, modelling a mis-extraction.

An error is counted as extraction-attributable only when that same policy answered the same case correctly with a clean store. If the policy was already wrong with a perfect store, the error stays with the policy. That rule is what keeps the attribution from flattering either side.

## Results: the full 16-cell matrix

Run with `python3 research/evidence/zep-temporal-memory-stale-fact-fixture-2026/scripts/stale_fact_fixture.py`. The published output is [results/stale_fact_matrix.csv](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/zep-temporal-memory-stale-fact-fixture-2026/results/stale_fact_matrix.csv), reproduced here row for row:

| policy | query | arm | n | exact correct | exact accuracy | stale returns | stale rate | extraction errors | policy errors |
|---|---|---|---|---|---|---|---|---|---|
| append_only_recency | current | clean | 30 | 10 | 33.3 | 20 | 66.7 | 0 | 20 |
| append_only_recency | current | mis_extraction_10pct | 30 | 9 | 30.0 | 21 | 70.0 | 1 | 20 |
| append_only_recency | as_of | clean | 30 | 14 | 46.7 | 16 | 53.3 | 0 | 16 |
| append_only_recency | as_of | mis_extraction_10pct | 30 | 15 | 50.0 | 15 | 50.0 | 0 | 15 |
| lww_upsert | current | clean | 30 | 10 | 33.3 | 20 | 66.7 | 0 | 20 |
| lww_upsert | current | mis_extraction_10pct | 30 | 9 | 30.0 | 21 | 70.0 | 1 | 20 |
| lww_upsert | as_of | clean | 30 | 14 | 46.7 | 16 | 53.3 | 0 | 16 |
| lww_upsert | as_of | mis_extraction_10pct | 30 | 15 | 50.0 | 15 | 50.0 | 0 | 15 |
| bitemporal_invalidate | current | clean | 30 | 30 | 100.0 | 0 | 0.0 | 0 | 0 |
| bitemporal_invalidate | current | mis_extraction_10pct | 30 | 27 | 90.0 | 0 | 0.0 | 3 | 0 |
| bitemporal_invalidate | as_of | clean | 30 | 4 | 13.3 | 16 | 53.3 | 0 | 26 |
| bitemporal_invalidate | as_of | mis_extraction_10pct | 30 | 6 | 20.0 | 13 | 43.3 | 0 | 24 |
| bitemporal_asof | current | clean | 30 | 30 | 100.0 | 0 | 0.0 | 0 | 0 |
| bitemporal_asof | current | mis_extraction_10pct | 30 | 27 | 90.0 | 0 | 0.0 | 3 | 0 |
| bitemporal_asof | as_of | clean | 30 | 30 | 100.0 | 0 | 0.0 | 0 | 0 |
| bitemporal_asof | as_of | mis_extraction_10pct | 30 | 30 | 100.0 | 0 | 0.0 | 0 | 0 |

Rates are percentages of the 30 evaluations in that cell; "stale returns" counts answers that named a real value of that attribute which was not the value asked for, as opposed to returning no fact at all. The run record is [first-party-fixture-run-2026-10-30.json](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/zep-temporal-memory-stale-fact-fixture-2026/first-party-fixture-run-2026-10-30.json): Python 3.12.3 on Linux aarch64, 2 CPUs, 480 evaluations, and 0.0042 s inside the evaluation loop, which is the only timing the script itself records. Whole-script wall time sits next to it in the same record as an external measurement rather than a script figure: five runs of the script, timed from interpreter start to exit on the same 2-vCPU host, gave 0.056-0.057 s, median 0.057 s. Sub-0.1 s numbers move with host and load — independent re-measurement during review gave 0.07 s for the same script, and a 2026-11-24 relocation check recorded 0.0051 s inside the loop and 0.07 s wall — so read both as "well under a second", not as a benchmark. No product, model or graph database was executed. When these files moved into the evidence bundle, that check also re-derived the CSV byte for byte and confirmed a tampered copy still fails verification; its [verification record](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/zep-temporal-memory-stale-fact-fixture-2026/verification-2026-11-24.json) carries the current file hashes.

## Reading the matrix: policy failure versus extraction failure

Change only the policy, keep extraction clean, and the current-truth question separates hard: append-only recency and last-write-wins both land at 33.3% exact accuracy with a 66.7% stale-return rate, while both bitemporal policies reach 100% with zero stale returns. All twenty clean-arm errors for the recency policies are policy-attributable, and they cluster exactly where you would expect: the ten late-arriving corrections, whose newest-ingested edge is a historical one, and the ten lapsed attributes, whose last ingested edge is expired.

Append-only and last-write-wins produce identical rows in every cell, and that is a finding rather than a bug in the fixture: when retrieval ranks by ingestion time and no temporal predicate is applied, keeping every historical edge and overwriting it are behaviourally the same answer. History that is stored but never queried does not protect anyone.

Change only the query instant and the picture inverts. Without a query-time as-of predicate, the bitemporal policy answers every as-of question with the current truth and scores 13.3% — it only succeeds on the four cases whose value had already stopped changing before 2026-08-01. Adding the predicate takes the same store to 100%. Invalidation alone fixes "what is X now"; it does not give you "what was X then", which needs the predicate at query time, not at write time.

The 10% extraction arm is where the attribution earns its keep. Under both bitemporal policies, 3 of 30 current-truth answers become wrong and all three are extraction-attributable — the store is right, the fact was filed under the wrong attribute, and the query returns no current fact at all, so the stale-return rate stays at zero while exact accuracy drops to 90%. Mis-extraction under a bitemporal store shows up as silence, not as a stale value. Under the recency policies the same corruption surfaces differently: one case flips to a stale answer, because dropping the newest edge from the ranking promotes the previous one.

Two honest artifacts are worth naming. First, the 10% arm moves the recency policy's as-of score *up*, from 46.7% to 50.0%, and the bitemporal policy's as-of score from 13.3% to 20.0%: removing a fact can accidentally improve a coarse policy, which is exactly why single-cell deltas should not be read as quality signals. Second, the extraction arm's three faults are a seeded synthetic condition, not a measured extraction error rate of any product.

What this means operationally is narrow but useful. Instrument the two failure modes separately: log the edges your store considers currently valid for an attribute, and log whether the queried attribute had zero current edges. A zero-edge result under a bitemporal store points at extraction or entity resolution; a non-zero edge set containing a superseded value points at the policy or at a write path that never stamped supersession. One counter per failure mode will tell you which one you are paying for.

## Reproduce it and check the numbers

```bash
git clone --depth 1 https://github.com/baeseokjae/baeseokjae.github.io
cd baeseokjae.github.io
python3 research/evidence/zep-temporal-memory-stale-fact-fixture-2026/scripts/stale_fact_fixture.py --verify
```

`--verify` re-derives all sixteen cells from the frozen case file and compares them byte for byte against the published CSV, exiting non-zero on any mismatch; the CSV sha256 recorded here is `c1d96ab3fe5b0112e6705f0f22ffa936ce4927517c58b06b4f19da97f9953548`. If you edit a policy or add cases, drop `--verify` to regenerate, then read [results/STALE-FACT-NOTES.md](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/zep-temporal-memory-stale-fact-fixture-2026/results/STALE-FACT-NOTES.md) for the exact commands, hashes and the two artifacts above. The script, case file, CSV and notes all live in `research/evidence/zep-temporal-memory-stale-fact-fixture-2026/`, so they stay together and the command works from any checkout. The script and dataset are first-party originals written for this post; no third-party source downloads and no credentials are included.

## What this fixture does not prove

It does not test Graphiti or Zep Cloud. No server was installed, no Neo4j, FalkorDB or Neptune instance was created, no extraction model was called, and no account was used. The four policies model documented patterns; the numbers describe those models and nothing about vendor runtime behaviour, latency or cost.

It is synthetic by construction: 30 cases with clean, disjoint valid-time windows and a single attribute per case. Real corpora bring overlapping assertions, entity-resolution ambiguity and extraction quality that no seeded 10% arm represents. Its value is as a control: if a policy cannot suppress superseded facts here, it will not do so on messy data either.

For choosing between vendor memory layers, [the Mem0-versus-Zep production guide](/posts/mem0-vs-zep-production-guide-2026/) covers pricing and deployment questions this post does not touch, and [the agent memory comparison](/posts/agent-memory-comparison-2026/) is the framework selection matrix. If you want to run the equivalent split against a real system rather than a model of one, that is the measurement still missing from this site — and from the sources cited above.
