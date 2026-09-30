---
title: "Zero-Mem for Pi Review: Zero-Token Memory for a Coding Agent (2026)"
date: 2026-09-30T20:52:59+00:00
tags:
  - zero mem pi agent
  - zero-token memory coding agent
  - pi coding agent memory plugin
  - zero-mem paper explained
  - entity-context graph agent memory
description: "Zero-Mem for Pi gives the Pi coding agent long-term memory with zero LLM tokens per memory operation, using raw traces plus local NER and embeddings."
draft: false
cover:
  image: "/images/zero-mem-pi-coding-agent-memory.png"
  alt: "Zero-Mem for Pi Review: Zero-Token Memory for a Coding Agent (2026)"
  relative: false
schema: "schema-zero-mem-pi-coding-agent-memory"
---

Zero-Mem for Pi is a community extension that gives the Pi coding agent long-term memory without spending a single LLM token on memory operations. It keeps every finished session as a raw trace, indexes those traces with local NER and embedding models, and injects a small number of retrieved snippets into later prompts — so the model is called once, for the answer.

That is the whole idea, and it is narrower than the marketing line suggests. The architecture comes from the paper *Zero-Mem: Zero-Token Memory Operations for LLM Agents* (arXiv:2607.29377v1, 31 July 2026, CC BY-NC-SA 4.0), which reports a 57.6% reduction in memory-operation time cost versus the fastest baseline at matched final-answer quality. Two independent Pi ports exist as of this writing: `skorotkiewicz/zero-mem` (the early adaptation, roughly two stars, README package name `pi-zero-mem`) and `woolcoxm/zero-mem-pi` (a self-described "faithful reimplementation", 38 stars). Both are architectural adaptations of a paper whose reference implementation is still pending peer review, and both say so.

The headline finding of this review is not the token savings. It is that Zero-Mem removes generative rewriting from memory entirely: the original interaction traces stay the source of record, so a retrieved fact can be traced back to the message it came from instead of to a summary that quietly dropped it. That distinction is what makes the extension worth understanding even if you never install it.

## What Does "Zero Mem Pi Agent" Actually Describe?

It describes a memory layer for the Pi coding agent in which no LLM is invoked to write memory, summarize memory, or score a retrieval. Every step outside final question answering is deliberately non-generative: an encoder embeds text, an entity extractor tags it, a graph walk and a lexical/dense ranker select evidence, and a deterministic calibration step keeps the reader grounded in what was retrieved.

The paper states the constraint precisely: "no step outside final question answering invokes an LLM or consumes LLM input or output tokens," with encoder computation accounted separately. The abstract frames the motivation as a data-structure problem rather than a modelling problem — generating intermediate records and mediating their retrieval adds recurring token and time costs, and omitted or merged details can obscure the original evidence.

Pi is an unusually good host for that idea because Pi ships no memory model at all. According to a source-level analysis of `earendil-works/pi` (revision f9bcd351, analyzed 15 September 2026), Pi is a branchable session substrate: a JSONL session tree that forks and clones, deterministic file manifests on compaction, and more than 20 ExtensionAPI lifecycle events. Searching its SDK documentation for "memory" returns only `SessionManager.inMemory()` and `InMemoryCredentialStore` — storage backends, not agent memory. Any memory behaviour has to be built on `context`, `session_start`, and `session_before_compact`.

## What Does the Zero-Mem Paper Claim, With Numbers?

Three claims matter, and they are separable.

First, zero LLM tokens for memory. In the paper's efficiency comparison (Table 2, GPT-4o-mini, same concurrency and hardware), Zero-Mem consumes zero LLM input/output tokens for memory operations, while GAM — the strongest quality baseline — burned 28,570,674 memory tokens and 18,552.39 seconds of total overhead. Even LightMem, the most token-efficient baseline in the comparison, burned 877,086 tokens.

Second, lower wall-clock cost, not just lower token cost. Zero-Mem's total memory-operation time was 334.77 s, or 0.22 s per query, against LightMem's 788.76 s and 0.51 s per query — the source of the 57.6% figure. Encoder inference, indexing, retrieval and calibration still consume CPU or GPU time; what disappears is the *LLM-mediated* cost.

Third, quality is not sacrificed. In the same efficiency setting Zero-Mem also posted the best quality: 59.15 F1 and 52.96 BLEU-1, which the paper reports as +10.0% F1 and +11.5% BLEU-1 over GAM. That is the sentence to hold onto: eliminating LLM-based memory operations did not degrade answer quality in their setup.

| Method (Table 2, GPT-4o-mini) | Memory tokens | Total memory-op time | Per-query time |
| --- | --- | --- | --- |
| Zero-Mem | 0 | 334.77 s | 0.22 s |
| LightMem | 877,086 | 788.76 s | 0.51 s |
| GAM | 28,570,674 | 18,552.39 s | not reported |

## What Does "Zero-Token" Really Mean — and What Still Costs?

"Zero-token" is a scope claim, not a magic claim. Zero-Mem eliminates LLM calls and LLM tokens *from memory operations only*: entity extraction, embedding, graph construction, retrieval and calibration all still cost compute — 334.77 s across the paper's full run. If your constraint is a hard API bill, the promise holds. If your constraint is a GPU budget on a laptop, the promise is about the model calls, not about free compute.

Two practical consequences follow for a Pi user.

The first is that the only memory tokens you pay per turn are the injected snippets. In `woolcoxm/zero-mem-pi`, retrieval injects up to three snippets by default as a `## Prior session memory` block in the system prompt, and the README puts that at roughly 103 tokens per turn — the entire recurring memory cost of the system, versus per-turn or per-query LLM maintenance calls in LLM-managed designs. The broader market numbers Zero-Mem is aimed at are large: LangMem reportedly spends about 3.26M tokens per session and xMemory about 118k tokens per query (VentureBeat figures as relayed by Sesame Disk, 5 August 2026 — secondary sourcing).

The second is that if the local Python environment is missing, the `skorotkiewicz` port falls back to BM25 lexical retrieval rather than calling a model to substitute for the missing components. Degradation means "worse recall", not "a surprise API bill".

## How Does Zero-Mem Work? Traces, Two Views, and Calibration

The architecture is best understood as four deterministic stages plus one LLM call.

**Raw traces as the source of record.** Zero-Mem preserves original interaction traces rather than summarizing them. Nothing is merged, nothing is abstracted away at write time. This is the design decision that the Hacker News thread picked up on most, and the reason auditability improves: retrieval is grounded in evidence rather than in a summary's omissions.

**An entity–context graph.** The first view exposes connections across interactions. Entities — people, tools, files, projects, decisions — become nodes that let retrieval follow structure between sessions.

**A temporal hierarchy.** The second view preserves conversational locality and session state, so a query can recover the surrounding context of a turn rather than only its matching chunk.

**Query-dependent routing and evidence closure.** For each query Zero-Mem weighs the two views (the fusion weight `rho` defaults to 0.6), retrieves from both, and then follows their structure outward to recover supporting relations or adjacent context. This is the "closure" step the ablation tests.

**Deterministic calibration.** Before the reader sees anything, calibration discards conflicting evidence and keeps the final answer grounded in the retrieved traces. Only then is the LLM invoked — once, on the final QA step.

The community ports mirror these defaults: `rho = 0.6`, `gamma = 0.6`, and top-5 retrieved evidence, matching the parameters cited in the Rust clean-room port (`ptaranat/zeromem`) as well as the paper.

## What Do the Benchmarks and Ablations Show?

On LoCoMo, Zero-Mem takes the best average F1 and BLEU-1 under both readers: 59.15 / 52.96 with GPT-4o-mini (+5.40 F1, +5.45 BLEU-1 over GAM) and 57.57 / 51.41 with Qwen2.5-14B (+4.87 / +4.86). The benchmark covers single-hop, multi-hop, temporal and open-domain questions — the last two being where a temporal hierarchy is supposed to earn its keep.

On HotpotQA, Zero-Mem holds the highest F1 across all readers as context grows from 56K to 448K tokens, averaging +5.52 F1 over the strongest baseline. The ablation at 56K context with GPT-4o-mini is the most informative single table in the paper:

| Configuration (HotpotQA, 56K, GPT-4o-mini) | F1 | BLEU-1 |
| --- | --- | --- |
| Full Zero-Mem | 72.07 | 69.66 |
| Graph view only (no hierarchy) | 62.50 | 59.90 |
| Temporal hierarchy only (no graph) | 54.88 | 51.40 |
| Without evidence closure | 67.90 | 65.43 |
| Without calibration | 70.13 | 66.45 |

The two views are complementary rather than redundant, and on HotpotQA the graph does the heavier lifting — dropping the hierarchy costs 9.6 F1, while dropping the graph costs 17.2. The retrieval-budget study is equally practical: performance improves sharply from top-1 to top-5, peaks in the average around top-10, then flattens. The paper uses top-5 to match its baselines, which is also where the Pi ports sit.

## Why Does This Matter More on Pi Than on Other Coding Agents?

Because Pi hands the problem to the extension author instead of solving it internally. Pi's own surface area is a session tree — sessions fork, clone, and compact — and compaction is the moment when a coding agent normally loses fidelity: history is replaced by a generated checkpoint.

Both Pi ports treat that moment as a hook rather than a loss. In the `skorotkiewicz` port, Pi compaction becomes a *fixed non-generative* checkpoint, and the original branch traces stay retrievable afterwards, including sibling branches and messages that compaction would otherwise hide. In `woolcoxm/zero-mem-pi`, every finalized message is captured as a trace unit with provenance (session, project, time) plus entities, and a derived "identity slot" is injected on the first turn so the agent starts a session with project context it did not have to re-read.

Neither port claims to reproduce the paper's benchmarks. `skorotkiewicz/zero-mem` states outright that it is a "Pi-oriented implementation of the architecture, not a reproduction of the paper's reported benchmark. It does not rewrite final agent answers." That honesty is worth more than a star count.

## How Do the Two Pi Implementations Compare?

They differ in ways that matter to how you would run them.

| Aspect | skorotkiewicz/zero-mem (early adaptation) | woolcoxm/zero-mem-pi (faithful reimplementation) |
| --- | --- | --- |
| Shape | TypeScript extension (`extensions/zero-mem.ts`, ~41 KB) plus a Python NLP worker | Self-contained TypeScript |
| NER | spaCy | compromise-style JS extraction |
| Embeddings | BGE-M3 | bge-small-en-v1.5 (earlier MiniLM); int8-quantized sidecar |
| Ranking | Hybrid BM25 + BGE-M3 | Hybrid BM25 + dense + session-adjacent turn closure, no recency prior |
| Graph routing | Five primary traces plus bounded graph/local neighbours | Personalized PageRank per the paper's Eq. 8–10; full temporal hierarchy only partially realized |
| Injected context | Retrieved snippets, XML-escaped, with instruction-like traces rejected | Up to 3 snippets as `## Prior session memory`, ~103 tokens/turn |
| Storage | Pi's session JSONL stays the source of record | Project-scoped `~/.pi/agent/zero-mem/store.json` + int8 embedding sidecar; switches to pure-JS HNSW above ~10k units |
| Safety filter | Deterministic rejection of "instruction-like" historical traces (prompt-injection guard) | Not documented to the same degree |
| Inspection | `/zero-mem` command shows route, engine, selected count, blocked instructions | Identity slot on first turn; retention policy (`maxAgeMs`/`maxUnits`) |
| Degraded mode | BM25 fallback if the Python env is missing | Pure-JS path |
| Adoption | ~2 stars, 0 issues, 29 commits, all 6–8 August 2026 | 38 stars, 2 forks, created 13 August 2026, last push 14 August 2026 |

The `skorotkiewicz` port's instruction-trace rejection is the most underrated feature in either codebase: it deterministically refuses to re-inject historical text that reads like an instruction, which closes the obvious prompt-injection channel a retrieved-memory system opens by design. The `woolcoxm` port has the better engineering story for scale — int8 embeddings, an HNSW switch, a retention policy — and the larger audience.

## How Do You Install Zero-Mem on Pi?

Both ports follow Pi's extension model, so the shape is the same: clone the extension, make the local retrieval dependencies available, point Pi at it, then restart Pi properly.

1. Install the extension into Pi's agent directory — for `woolcoxm/zero-mem-pi`, symlinking the repo into `~/.pi/agent/extensions/zero-mem/` is supported and is the least surprising layout.
2. For the `skorotkiewicz` port, set up the Python side: `uv sync` in the repo, then download the spaCy model the worker expects.
3. If the Python interpreter is not on the default path, set `ZERO_MEM_PYTHON` so the extension can find it. If it is missing entirely, expect the BM25 fallback rather than an error.
4. Restart Pi *fully* — not `/reload`. The documented gotcha in the `woolcoxm` README is that code changes are not picked up by a reload; a full restart is required, and this is the single most common "it does not work" report in early adoption.
5. Verify with the inspection command. `/zero-mem` in the `skorotkiewicz` port prints the retrieval route, the engine in use, how many traces were selected, and how many historical instructions were blocked — which is exactly the output you want when memory returns nothing useful.

Storage defaults are conservative: `woolcoxm/zero-mem-pi` keeps everything project-scoped under `~/.pi/agent/zero-mem/`, with retention limits you can tune; the `skorotkiewicz` port keeps Pi's own session JSONL as the record of truth and treats the index as derived state.

## Zero-Mem vs Other Pi Memory Options

The Pi memory ecosystem is small and fragmented. Zero-Mem is not the only option, and for some workflows it is not the right one.

| Option | Storage model | Retrieval | Honest positioning |
| --- | --- | --- | --- |
| zero-mem (either port) | Raw traces + entity graph + embeddings | Hybrid lexical/dense plus graph walk | Best fit when you want memory without model calls and traces that stay auditable |
| pi-mem (~79★) | Plain Markdown files | None documented | Simplest to read and edit by hand; no embeddings, so recall depends on the agent reading files |
| pi-memory (npm) | Note store | Semantic search via qmd | Semantic recall without building a graph |
| Magic Context | Context management | Not benchmarked here | Adjacent tooling rather than a memory store |
| pi-agent-memory | Session memory | Not benchmarked here | Listed in the Pi package directory |

The trade-off is structural, not a matter of polish. Markdown memory is inspectable and zero-dependency but does not scale; vector-search memory scales but loses provenance; Zero-Mem keeps provenance and structure at the cost of a local encoder and a graph.

## What Are the Limitations and Open Questions?

The paper's reference implementation is not released yet — the abstract says code and implementation details will be available *after peer review*. Everything discussed here is a community port, and both ports disclaim benchmark parity in writing.

Mutation and contradiction remain unproven. The sharpest critique in the Hacker News thread (from `russlan`) argues that if an entity's attributes change across sessions, the graph plus temporal hierarchy must preserve both states, surface the conflict, and show which trace justified the answer. The paper's calibration step discards conflicting evidence, which is the right default for grounded QA but is not the same as conflict *reporting*. A production agent arguably needs both.

Stale, conflicting and adversarial traces are unmeasured in public. The community's suggested benchmark — unsupported-answer rate and evidence recall on adversarial memory — does not exist yet for either port. `skorotkiewicz`'s instruction-trace filter is a good start, but one deterministic rule is not a red-team result.

Adoption is thin. Roughly two stars on one port and 38 on the other, with zero issues on the early one, means there is very little real-world mileage to generalize from — no reports from long-running monorepos, no migration stories, no deletion semantics. Pi itself has no memory contract to inherit: there is no scope primitive and no deletion hook, so every plugin invents its own, and uninstalling cleanly is your problem.

Finally, the "zero-token" framing invites the wrong comparison. The alternatives the HN thread surfaced are attention-level and cache-level retrieval — storing conversation KV caches and retrieving on attention scores (reported SOTA on LoCoMo and LongMemEval by one commenter's project), or an approach one commenter described as ~0.3 s retrieval over a few million pre-chunked tokens needing roughly 200 GB of RAM/VRAM. Those attack latency, not token spend, and they are not deployable on a developer laptop. Zero-Mem's bet is that a deterministic structure gets most of the recall for none of the API cost.

## Verdict: Who Should Install Zero-Mem for Pi Today?

Install it if you already live in Pi, you care about the API bill of long-running sessions, and you want memory you can audit back to the original message. The `woolcoxm/zero-mem-pi` port is the better-supported starting point: more adoption, simpler dependency story, quantized embeddings, retention controls, and an HNSW escape hatch as your store grows. Reach for `skorotkiewicz/zero-mem` if the determinism story is what you are evaluating — its instruction-trace rejection and `/zero-mem` inspection command are the clearest expression of the auditability argument, and its Python worker is easier to read if you intend to modify retrieval.

Wait if you need conflict handling, deletion guarantees, or evidence from production workloads before you trust a memory layer with your project history. The paper's efficiency claims are specific and well-argued, the auditability argument is stronger than the cost argument, and neither is yet backed by a released, peer-reviewed implementation. Treat the Pi ports as an unusually clean architectural preview, not as a drop-in memory product.

## FAQ

**Is Zero-Mem for Pi really zero tokens — nothing at all?**

Memory operations consume zero LLM input/output tokens, which is the claim the paper makes and the ports preserve: no summarization call at write time, no scoring call at read time. You still pay tokens for the one final answer, plus the injected snippets — about 103 tokens per turn in the `woolcoxm` default of three snippets. Local encoder and indexing compute is real, it just is not billed as LLM tokens.

**Does it work offline, and does it need a GPU?**

The retrieval pipeline is local by design: entity extraction plus embedding models running on your machine, with no network call for memory. The reference embeddings used by the ports (`bge-small-en-v1.5`, BGE-M3, MiniLM variants) run acceptably on CPU for developer-scale stores, and the `skorotkiewicz` port degrades to BM25 if its Python environment is unavailable. Where you will want a GPU is the final answering model, which is unchanged from Pi's normal behaviour.

**Does Zero-Mem replace Pi's compaction?**

No. It changes what compaction means. Both ports keep the original branch traces retrievable and treat the compacted checkpoint as a fixed, non-generative artifact rather than a generated summary, so compaction stops being the moment your history is permanently rewritten. Messages hidden by compaction remain in the retrievable trace set.

**Does it work with Claude Code, Codex, or Hermes instead of Pi?**

The architecture is host-agnostic, but both implementations shipped so far are Pi extensions built on Pi's lifecycle events (`context`, `session_start`, `session_before_compact`). Porting means re-implementing those hooks against another harness's extension API plus a trace store with provenance. The clean-room Rust port (`ptaranat/zeromem`) is the most portable starting point if you are evaluating that path.

**How much does it actually help?**

On the paper's benchmarks, memory-operation time drops 57.6% versus the fastest baseline while quality improves rather than degrades — best average F1 and BLEU-1 on LoCoMo under both readers, and the highest F1 on HotpotQA as context scales to 448K tokens. On Pi specifically there is no published before/after, so the honest answer is that the architecture is well-evidenced and the adapters are unmeasured.
