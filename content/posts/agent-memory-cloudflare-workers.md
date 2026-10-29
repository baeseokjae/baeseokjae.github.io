---
title: "Agent Memory on Cloudflare Workers: The Documented API, the Compaction Lifecycle, and What to Build in Private Beta"
date: 2026-10-28T11:20:00+00:00
lastmod: 2026-10-28T11:20:00+00:00
tags:
  - cloudflare agent memory
  - agent memory cloudflare workers
  - durable objects agent memory
  - serverless agent memory
  - context compaction agent memory
  - vectorize agent memory
  - namespaces and profiles
  - private beta agent memory
description: "Cloudflare Agent Memory is a managed, namespace- and profile-scoped memory store for agents. What the private-beta documentation actually specifies: the binding, every documented method, ingest and recall limits, supersession, and what to build instead while access is gated."
draft: false
schema: schema-agent-memory-cloudflare-workers
cover:
  image: "/images/agent-memory-cloudflare-workers.png"
  alt: "Agent Memory on Cloudflare Workers: the documented API contract"
  relative: false
---

Cloudflare Agent Memory is a managed memory store for AI agents: you bind it to a Worker, address an isolated profile per user or tenant, hand it conversations, and get back extracted facts, events, instructions and tasks that survive context compaction. The documentation is public even though the service is in private beta, so the useful engineering question today is not "does it work" but "what exactly is specified, and what is left unspecified".

This page answers that second question for developers choosing a memory substrate for a Workers-based agent. It walks the documented isolation model, the binding configuration, every documented method with its real signature, the compaction integration pattern, the vendor-described ingestion and retrieval internals, the published limits, and the gaps the documentation does not close. It deliberately does not rank the service against mem0, Zep or any other memory system — the vendor publishes no measured result to rank it with.

## The short answer

If you are building on Workers and want durable per-entity memory without operating an extraction pipeline, Agent Memory is the substrate that matches your runtime: memory lives next to the compute, scoping is a platform concept rather than your schema, and the write path (chunking, extracting, deduplicating, verifying, superseding) is the vendor's problem. Three qualifications come with that.

First, the service is in private beta, so availability is gated and the API can change or be withdrawn. Second, no accuracy, latency, throughput or price figure is published anywhere in the material read for this page, so any comparison table that ranks it numerically against another memory system is unsupported. Third, the integration path the documentation points at for compaction is an experimental import path, not stable API. Plan for the shape of the service, not for its stability.

## What is specified, and what is not

Cloudflare frames the product as memory that removes the need to build your own extraction, storage, search and summarization pipeline, with isolated profiles for users, agents, tenants, teams or application entities ([docs index](https://developers.cloudflare.com/agent-memory/)). That framing is the honest scope statement: the thing you are buying is the pipeline, not the storage.

| Question | Documented answer | Status |
|---|---|---|
| Isolation unit | namespace > profile > memory, plus sessions scoped to a profile | Specified |
| Write API | `ingest()` for conversations, `remember()` for single memories | Specified |
| Read API | `recall()` returns a synthesized answer, `list()` and `get()` return rows | Specified |
| Deletion | `delete(memoryId)`, `deleteSession()`, `deleteProfile()` | Specified |
| Hard limits | 500 messages per ingest, 32 KB per message, 1 KB recall query | Specified |
| Extraction pipeline | Content-addressed IDs, two-pass extraction, eight-check verifier | Vendor-described |
| Retrieval | Five channels fused with Reciprocal Rank Fusion | Vendor-described, weights unpublished |
| Accuracy or latency figure | None published | Not specified |
| Price | Not billed during beta, no unit price published | Not specified |
| Export endpoint | A stated commitment to exportability, no endpoint documented | Not specified |

The distinction between "specified" and "vendor-described" matters when you are deciding whether to depend on a behaviour. Method names and limits you can build against. Pipeline internals you can only treat as a description of intent, because a private-beta implementation is free to change them without a changelog entry.

## The isolation model: namespace, profile, memory

The service uses a two-level isolation model. A namespace is a top-level container that scopes a set of profiles, and you use it to separate applications, environments, tenants, or memory layers such as user, team and organization memory. A profile is an isolated store for a single entity, with its own memories and its own retrieval indexes. Memories then sit inside a profile, and sessions group the memories that came from one conversation ([namespaces and profiles](https://developers.cloudflare.com/agent-memory/concepts/namespaces-profiles/)).

Two properties of that model are worth designing around. Sessions are scoped to a profile, so the same session identifier can exist in two profiles without conflict — you do not need globally unique session IDs, only per-profile ones. And a recall issued on one profile never returns another profile's memories, which is what makes a multi-tenant deployment tractable without an application-level tenant filter in every query.

The namespace is a binding-level concept, not a runtime argument. A binding entry names exactly one namespace, so separating production from staging means two binding entries and two environment variable names, not one binding plus a namespace parameter at call time. That is a small detail with a large consequence: namespace selection happens at deploy time, in configuration, which is also why a mis-pointed binding is a deployment problem rather than a code path you can unit-test easily.

## The binding, exactly as documented

Agent Memory is reached through an `agent_memory` array in the Wrangler configuration. Each entry carries `binding`, the variable name used in Worker code, and `namespace`, the Agent Memory namespace to bind to. Binding several namespaces means adding several entries ([Workers API](https://developers.cloudflare.com/agent-memory/api/workers-api/)).

```jsonc
{
  "$schema": "./node_modules/wrangler/config-schema.json",
  "agent_memory": [
    { "binding": "MEMORY", "namespace": "assistant-prod" },
    { "binding": "MEMORY_STAGING", "namespace": "assistant-staging" }
  ]
}
```

```toml
[[agent_memory]]
binding = "MEMORY"
namespace = "assistant-prod"
```

`npx wrangler types` generates the corresponding `AgentMemoryNamespace` type on `Env`, so the binding is typed end to end. Note what is not in that configuration: no region, no capacity, no retention policy, and no vector index name. Those are either platform decisions or undocumented, and neither case gives you a knob to set today.

## The full method surface

The reference page documents ten methods across two levels. The namespace level gives you `getProfile(profileName)`, which returns a profile and creates it if it does not exist, and `deleteProfile(profileName)`, which marks a profile and all its memories and messages for deletion. Both take names up to 100 characters, and the documentation warns that the first `getProfile()` call for a new profile may take longer while the profile is created — a first-request cost you should not put on a user-facing latency path without a warm-up.

The profile level is where the work happens.

```ts
// Namespace level
const profile = await env.MEMORY.getProfile(`user:${userId}`);

// Bulk path: a whole conversation segment, one call
await profile.ingest(
  [
    { role: "user", content: "I prefer concise answers." },
    { role: "assistant", content: "Noted." },
    { role: "user", content: "Deploy to the EU region, not the US." }
  ],
  { sessionId: "conv-8891" }
);

// Explicit path: your application already knows the fact
const memory = await profile.remember({
  content: "Deploys target the EU region.",
  sessionId: "conv-8891"
});
```

Three details of `remember()` are load-bearing for anyone migrating from a self-managed store. It accepts only `content` and an optional `sessionId`; the service classifies the memory type and writes the summary itself. There is no caller-assigned type field and no embedding parameter at write time. The type comes back on the stored object as one of `fact`, `event`, `instruction` or `task`, so you can filter on it after the fact through `list()` but you cannot decide it at write time. And the return value is the stored memory, which makes it the right place to capture an ID for later deletion.

Reads come in two distinct shapes, and confusing them is the most common integration error.

```ts
// Synthesized answer for the model
const recall = await profile.recall("which region do deployments target?", {
  thinkingLevel: "low",
  responseLength: "short"
});
// recall = { count, answer, candidates: [{ id, summary, sessionId, score }] }

// Rows for your own UI, audit or export logic
const page = await profile.list({ limit: 50, type: "instruction" });
for (const entry of page.memories) {
  const full = await profile.get(entry.id); // list() entries omit content
}
```

`recall()` returns a grounded synthesized answer plus a candidate count and scored candidates, not raw memory rows. `thinkingLevel` accepts `low`, `medium` or `high` with a default of `low` and trades retrieval breadth against time; `responseLength` accepts `short`, `medium` or `long` with a default of `medium`; `referenceDate` anchors date-relative queries. If nothing matches, the answer is empty rather than invented. `list()` paginates by an opaque cursor, filters by session and type, and deliberately omits `content` — the documentation is explicit that you must call `get(memoryId)` for the full memory.

Deletion is a three-granularity model, which is more than most memory APIs offer and is the part that makes the service answerable to data-deletion requests: `delete(memoryId)` removes one memory and its linked source messages, `deleteSession(sessionId)` marks every memory and message tagged with that session in the profile, and `deleteProfile(profileName)` marks the whole profile. Session deletion is idempotent — deleting a session with no rows is a no-op — which means you can call it on every logout without a pre-check.

Finally, `getSummary()` returns a structured Markdown summary of everything stored in a profile, optionally scoped to one session. Treat it as the debugging surface: it is how you inspect what the agent actually remembers about an entity without writing your own aggregation.

## The compaction lifecycle

Context compaction is the moment a harness decides what to do with a conversation that no longer fits. The pattern the documentation describes is to make compaction a write, not a discard: the harness bulk-ingests the conversation into the profile at a natural checkpoint — typically when it compacts context, or after the user goes idle — instead of calling the write path on every model turn ([get started](https://developers.cloudflare.com/agent-memory/get-started/)).

Read that as an architecture instruction rather than a performance tip. The write path runs extraction, verifier checks and background vectorization, so per-turn writes put that work on the critical path of every response. A batch at compaction puts it once, on a boundary the harness already treats as expensive. The documentation also points at the Cloudflare Agents SDK session API as the reference implementation for handling compaction, remembering and searching — but the import in that example is from `agents/experimental/memory/session`, an experimental namespace. If you depend on that wiring, pin the version you tested and expect the path to move.

The retrieval side of the lifecycle is where most implementations get it wrong in a way that no amount of storage quality fixes. A memory that is written but never recalled costs money and buys nothing. The read that matters is the one at session start, where the agent asks a small number of targeted questions — what does this entity prefer, what is the current state of the object in question, what rules apply — and rebuilds context from answers rather than from a re-read of the transcript.

## Ingestion, as the vendor describes it

The pipeline description comes from Cloudflare's launch post on Agent Memory ([launch post](https://blog.cloudflare.com/introducing-agent-memory/)), not from an independent audit, and the exact hash construction is described rather than published as code.

Each message receives a deterministic ID: a SHA-256 hash of the session ID, role and content, truncated to 128 bits. Because the ID is derived from content, re-ingesting the same conversation resolves to the same IDs and creates no duplicates. That is the mechanism behind the documented idempotency of `ingest()`, and it is the reason a retry after a timeout is safe.

Extraction runs in two passes. A full pass handles the conversation in chunks of roughly 10,000 characters with a two-message overlap and processes up to four chunks concurrently. When a conversation is long enough — the post gives 9 or more messages as the threshold — a detail pass re-reads overlapping windows looking for concrete values such as names, prices and version numbers that a full pass tends to blur. Extracted items then pass an eight-check verifier covering entity identity, object identity, location context, temporal accuracy, organizational context, completeness, relational context and fact support. Each extracted item is classified as a fact, an event, an instruction or a task.

Supersession is the property to read carefully, because it is easy to describe in a way that is simply wrong. Facts and instructions are keyed by a normalized topic key. When a new memory shares a topic key with an existing one, the older memory is marked superseded rather than deleted: the latest version surfaces in recall results while the full history is preserved, producing a version chain with a forward pointer ([how Agent Memory works](https://developers.cloudflare.com/agent-memory/concepts/how-agent-memory-works/)). Tasks are session-scoped and deprioritized after the session ends. Events accumulate and do not conflict with each other.

A preserved supersession chain is a different product from a delete-on-update store. It means an agent can be asked why a fact changed and answer from stored history, and it means a bad extraction can be traced rather than silently overwritten. It also means deletion semantics deserve a second look before you promise anyone that a fact is gone: `delete(memoryId)` removes that memory and its linked source messages, and the chain around it is what you have to reason about afterwards.

## Retrieval, as the vendor describes it

A recall runs five channels in parallel: full-text search with Porter stemming, exact fact-key lookup, raw message full-text search, direct vector search, and HyDE vector search, in which a hypothetical document is embedded to improve matching against paraphrased queries. The five result lists are fused with Reciprocal Rank Fusion using per-channel weights, with fact-key matches weighted highest.

RRF is a sensible choice here for the same reason it is popular elsewhere: it combines ranked lists without requiring the scores from different channels to be commensurable. What the documentation does not publish is the weight values, so there is no way to reproduce the ranking from outside, and no way to claim a specific scoring behaviour.

Two consequences follow. Raw conversation messages are stored verbatim alongside extracted memories so that the transcript remains searchable, but the content of a recall candidate is a summary. Verbatim storage is not verbatim retrieval: `recall()` synthesizes, and `list()` omits content. If you need exact quotes, store them yourself as an explicit memory and fetch them with `get()`, rather than relying on the synthesizer to preserve them.

The benchmarks section is where a fair reading matters most. The launch post names LongMemEval, LoCoMo and BEAM as the industry benchmarks used to compare memory systems, and warns that tuning to a single benchmark produces systems that break in production. It publishes no result for Agent Memory on any of them. The correct statement is therefore that no accuracy figure exists, not that the service performs well or poorly on those benchmarks.

## Limits, and one documentation inconsistency

| Feature | Documented limit |
|---|---|
| Messages per `ingest()` call | 500 |
| Message content size | 32 KB (32,768 bytes UTF-8) |
| Recall query size | 1 KB (1,024 bytes UTF-8) |
| Session ID length | 64 characters |
| Profile name length | 100 characters |
| Namespace name length | 32 characters |
| List page size | 1 to 1,000, default 20 |

The table comes from the [limits page](https://developers.cloudflare.com/agent-memory/platform/limits/). One row does not agree with the [Workers API reference](https://developers.cloudflare.com/agent-memory/api/workers-api/), which states a default of 20 and a maximum of 500 for the list limit while the limits page allows up to 1,000. Build to the lower bound until the two pages agree: page at 500 or fewer, and handle a response shorter than the limit as the end of the data rather than assuming your requested size was honoured.

The practical reading of these numbers is that the 500-message cap and the 32 KB message cap are both reachable by a real compaction event. A long agent session will exceed 500 messages, so the compaction path needs to shard by message count and check byte length per message before calling `ingest()`. A single oversized tool result will exceed 32 KB, so truncation or summarization of the oversized message belongs in your harness, before ingest, not in the memory layer.

## The beta boundary: three claims not to make

The service is not billed during private beta, and Cloudflare commits to at least 30 days of notice before making changes or starting to charge ([pricing](https://developers.cloudflare.com/agent-memory/platform/pricing/)). No unit price, quota or usage measure is published, so real usage and monetary cost are unknown rather than zero. Any cost model you build now is a guess with an expiry date.

Three claims circulate in write-ups of this service and none of them survives a check against the primary material. Single-digit-millisecond same-region read latency: no latency figure appears in the documentation or the launch post. A caller-controlled memory type or an embedding toggle at write time: `remember()` takes content and a session ID, and the service assigns the type. Cross-region replication with defined consistency: no replication model is documented. If a number or a behaviour is not in the reference pages, it is somebody's inference, and the honest way to use it is to say so or leave it out.

Exportability sits in a different category: Cloudflare states that a customer's memories are exportable and that accumulated knowledge can leave the platform, while the launch post describes R2 snapshots and exports as future work and no export endpoint appears in the reference pages. That is a stated commitment, useful for procurement, and not an API you can call today. Plan your exit path against the endpoints that exist, which are `list()` plus `get()`.

## What to build while access is gated

The productive move during a private beta is to own the seam. Define the memory operations your agent needs as an interface with the same shape as the documented surface, implement it twice — once against Agent Memory, once against a local store — and let the article-level behaviour (what gets written, when compaction fires, what questions are asked at session start) live above the seam. Then a change in the beta API costs you one adapter, not a rewrite.

The skeleton below is an implementation guide for the local adapter, not a benchmark: it implements the documented scoping semantics — namespace, profile, session — over SQLite with an FTS5 index, including supersession as a preserved chain rather than a delete. It is short on purpose; the parts that matter are the scoping keys and the supersession pointer.

```python
import sqlite3, hashlib, json, time

SCHEMA = """
CREATE TABLE IF NOT EXISTS memory (
  id TEXT PRIMARY KEY, namespace TEXT, profile TEXT, session TEXT,
  type TEXT, content TEXT, topic_key TEXT, created_at REAL,
  superseded_by TEXT, deleted INTEGER DEFAULT 0
);
CREATE VIRTUAL TABLE IF NOT EXISTS memory_fts
  USING fts5(content, content='memory', content_rowid='rowid', tokenize='porter');
"""

def message_id(session, role, content):
    raw = f"{session}\\x00{role}\\x00{content}".encode()
    return hashlib.sha256(raw).hexdigest()[:32]   # 128-bit truncation, as documented

def remember(db, ns, profile, content, session=None, topic_key=None, mtype="fact"):
    row_id = hashlib.sha256(f"{ns}|{profile}|{content}".encode()).hexdigest()[:32]
    with db:
        if topic_key:                            # supersede, never delete
            db.execute(
                "UPDATE memory SET superseded_by=? "
                "WHERE namespace=? AND profile=? AND topic_key=? AND superseded_by IS NULL",
                (row_id, ns, profile, topic_key))
        db.execute(
            "INSERT OR IGNORE INTO memory (id, namespace, profile, session, type, content,"
            " topic_key, created_at) VALUES (?,?,?,?,?,?,?,?)",
            (row_id, ns, profile, session, mtype, content, topic_key, time.time()))
        db.execute("INSERT INTO memory_fts (rowid, content) "
                   "SELECT rowid, content FROM memory WHERE id=?", (row_id,))
    return row_id

def recall(db, ns, profile, query, limit=10):
    # lexical channel only; a real adapter adds an embedding channel and fuses ranks
    rows = db.execute(
        "SELECT m.id, m.content, m.type FROM memory_fts f "
        "JOIN memory m ON m.rowid = f.rowid "
        "WHERE memory_fts MATCH ? AND m.namespace=? AND m.profile=? "
        "AND m.deleted=0 AND m.superseded_by IS NULL LIMIT ?",
        (query, ns, profile, limit)).fetchall()
    return [{"id": r[0], "summary": r[1][:200], "type": r[2]} for r in rows]
```

The scoping predicates in `recall()` are the whole point of the exercise: `namespace` and `profile` are mandatory filters in every statement, so an accidental cross-tenant read is a query you had to write deliberately. `superseded_by IS NULL` is what makes the current fact win while the chain stays on disk. What the skeleton does not do is the part you are buying from the vendor: extraction, the verifier, the vector channels, HyDE and the synthesis step — which is exactly the work that a managed substrate removes, and the reason the build-versus-buy decision here is a decision about pipeline ownership rather than about SQLite.

## A community implementation with a thin track record

One MIT-licensed project implements the same idea directly on Cloudflare primitives: [thisuxhq/agent-memory](https://github.com/thisuxhq/agent-memory) puts one SQLite Durable Object per profile behind Hono, uses FTS5 as the source of truth, Workers AI `bge-m3` with Vectorize for semantic recall including HyDE, and an OpenRouter model for extraction, classification, query analysis and synthesis. Its routes mirror the managed service — `remember` synchronous, a queue for idle-batch extraction, `ingest` to write and extract immediately, `recall` for hybrid search plus a synthesized answer, plus `summary` and `memories` — and its ingest and queue routes are idempotent on session, role and content.

The repository's own README carries a section headed "Cost (1k users, 20 chats)" whose entire text is "Luna ~$40. Cloudflare floor $5. DOs $0. Embeddings + Vectorize ~cents." Neither figure carries a time unit, a method or a date, so read the $40 as the author's rough estimate rather than a monthly bill, and not as a measurement of this project or of the managed service. The repository metadata is the more useful signal — created 2026-08-16, last push the same day, a handful of stars at the time of checking. It is a readable reference implementation of the pattern, not a maintained dependency.

## When the managed substrate fits

Use Agent Memory when you are on Workers and want memory pinned to the runtime; when your isolation unit is a user, tenant or agent and you would otherwise hand-roll tenant filters into every query; when deletion at profile, session and memory granularity needs to be a platform primitive because someone will eventually ask you to prove it; and when the history of a changed fact matters more than the storage cost of keeping it.

Do not use it as a general-purpose database, as a vector index you control and tune, or as a verbatim transcript retrieval system — recall synthesizes, list omits content, and summary compresses. And do not adopt it as a hard dependency while it is in private beta without an adapter boundary and an exit path through `list()` and `get()`.

The architecture decision underneath all of this is unchanged from before the service existed: agent memory is a substrate choice, not a feature. What Cloudflare has added to the option set is a version where the extraction pipeline, the scoping model and the compaction integration are configured in Wrangler rather than written in your repository — and where the price of that convenience is a beta boundary you should be able to describe precisely to your team before you ship on it.

## Related reading

- [AI Agent Memory Architecture Guide 2026](https://baeseokjae.github.io/posts/agent-memory-architecture-guide-2026/) — the architecture-level view this page assumes.
- [Best AI Agent Memory Frameworks in 2026](https://baeseokjae.github.io/posts/best-ai-agent-memory-frameworks-2026/) — the framework comparison this page deliberately does not repeat.
- [Agent Memory Layer Comparison 2026](https://baeseokjae.github.io/posts/agent-memory-comparison-2026/) — product-level comparison of Mem0, Zep, Déjà Vu and Agent Memory MCP.
- [Agent Memory Write-Path Reliability](https://baeseokjae.github.io/posts/agent-memory-write-path-reliability-2026/) — how to test whether a write path records, updates, contradicts and deletes correctly.

## How this page was checked

Every API statement here was compared against saved copies of the public Agent Memory documentation and the launch post, fetched on 2026-10-28, by asserting each quoted sentence as an exact substring of the saved text. The saved pages are not all the same age. The index, `concepts/namespaces-profiles`, `concepts/how-agent-memory-works` and `platform/pricing` pages carry "Last updated Jun 2, 2026"; `api/workers-api` and `platform/limits` carry Jun 3, 2026; and `get-started`, which is the source for the compaction lifecycle and the experimental import, carries "Last updated Oct 21, 2026", a week before this check. The launch post carries datePublished 2026-04-17 and dateModified 2026-07-15. The June reference pages are therefore several months old and undocumented changes in them cannot be ruled out, while the get-started page that carries the lifecycle material is current to within a week. That comparison was a private, local author verification: the saved copies are third-party page captures and are not redistributed with this article, which is why every claim above links to the live page instead. No managed-service test was run — no latency, cost, accuracy or isolation measurement — because private-beta access was not available, and no such figure appears in the text.
