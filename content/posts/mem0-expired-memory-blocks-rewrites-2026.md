---
date: 2026-10-28 00:00:00+00:00
description: 'On mem0ai 2.2.1 an expired memory still reaches the extraction prompt and the md5 dedup set, so a fresh add() of the same fact returns an empty list. Read the code path, the provider call an expiry update still makes, and a delete-then-add workaround.'
draft: false
schema: schema-mem0-expired-memory-blocks-rewrites-2026
tags:
- mem0
- agent-memory
- expiration
- deduplication
- debugging
title: 'When an Expired Memory Blocks the New One: mem0 OSS Expiry, Deduplication and the Write That Never Lands'
---

Your agent stored `user prefers aisle seats` with an expiration date. The date passed. The user says it again. You call `add()` with a fresh `expiration_date`, get no exception, get an empty `results` list, and `get_all()` shows nothing. The fact never lands, and it will never land as long as the expired copy is what the search returns.

On mem0ai 2.2.1 — the Python OSS package, self-hosted — the cause is a read/write asymmetry. Expiration is applied as a filter on the read paths but not on the ADD path. The expired row is still handed to the extraction LLM as an "existing memory", and its `hash` is still loaded into the dedup set, so the fresh write is dropped as a duplicate of a record the user can no longer see. The same write machinery adds a second dependency: an update that only touches metadata or the expiry date still calls the embedding provider, and a provider error stops that update before anything is persisted.

This article walks the exact code path at a pinned tag, separates what is verified in source from what is only reported in the issue tracker, and gives a write pattern that does not depend on a fix shipping.

Everything below is scoped to `mem0ai==2.2.1` (Python, self-hosted vector store). The hosted platform is out of scope, and no recall or accuracy benchmark is claimed.

## The two-minute check

Before reading further, decide which failure you actually have. The first two look identical from the caller's side — a successful call, no error, nothing visible. The third surfaces as an update that failed or changed nothing.

```python
mem = Memory.from_config(cfg)          # pinned: mem0ai==2.2.1
res = mem.add("user prefers aisle seats", user_id=u,
              expiration_date="2026-11-30")   # future date, same fact as an expired row
print(res)                                  # empty results means the write was suppressed
# get_all() takes entity scope inside `filters`; top-level user_id is rejected on 2.2.1
print(mem.get_all(filters={"user_id": u})["results"])                     # expired rows stay hidden
print(mem.get_all(filters={"user_id": u}, show_expired=True)["results"])  # the ghost row is still there
```

If `results` is empty while `show_expired=True` still lists the old row, you are in the expired-record suppression case. If the date itself is impossible (`2099-02-30`), you are in the CLI validation case. If a metadata-only or expiry-only `update()` raises a provider error — or leaves the record unchanged because your retry wrapper swallowed one — you are in the unnecessary-embedding path described in issue #7561, covered below.

## Expiration in 2.2.1 hides a record; it does not delete it

`_payload_is_expired` compares the stored `expiration_date` against today's UTC date, and both `get_all()` and `search()` skip rows it flags unless `show_expired=True` is passed. The helper spans lines 442-451 of `mem0/memory/main.py` at tag `v2.2.1`, with the comparison at line 449 and the `except ValueError: return False` closing it at 450-451. The read-path filters are applied at lines 1369 and 1684. Because the date comparison is `< now`, a memory that expires today is still visible today.

That is a visibility filter over live rows, not a deletion and not a tombstone. Nothing in the expiry helper removes the vector, and there is no expiry-driven cleanup pass in the file. So the row keeps its payload, keeps its `hash`, and keeps being a candidate for any code path that does not call `_payload_is_expired`. Source: [mem0ai/mem0 v2.2.1 main.py](https://raw.githubusercontent.com/mem0ai/mem0/v2.2.1/mem0/memory/main.py).

## The ADD path never applies that filter

`_add_to_vector_store()` runs in phases. Phase 1 retrieves candidate existing memories with `vector_store.search(...)` at `top_k=10` and immediately maps them into the extraction prompt without checking expiry (lines 925-943):

```python
# Phase 1: Existing memory retrieval
existing_results = self.vector_store.search(
    query=parsed_messages,
    vectors=query_embedding,
    top_k=10,
    filters=search_filters,
)
...
existing_memories.append({"id": str(idx), "text": mem.payload.get("data", "")})
```

Phase 5 then builds the dedup set from the same unfiltered list (lines 1007-1013):

```python
# Phase 4: Per-memory CPU processing + Phase 5: Hash dedup
existing_hashes = set()
for mem in existing_results:
    h = mem.payload.get("hash") if hasattr(mem, "payload") and mem.payload else None
    if h:
        existing_hashes.add(h)
```

Two consequences follow, and only one of them is obvious.

The first is prompt contamination. The extraction LLM receives the expired text inside the "existing memories" block. With an additive prompt, the model is being asked whether the incoming statement adds anything new relative to what it is shown — and it is shown the expired copy. So the model can legitimately decide there is nothing new to extract, and return no memories at all.

The second is silent deduplication. If extraction does emit the text, the loop at lines 1022-1025 computes `hashlib.md5(text.encode()).hexdigest()` and skips the record when that hash is in `existing_hashes`. The expired row's hash is in that set.

Both routes end at the same branch. When every candidate record is skipped, the function saves the messages for context and returns an empty list to `add()` (lines 1043-1045, with `return []` at line 1045). No exception, no warning at default log level — the caller sees a successful-shaped result object with nothing in it.

This is the mechanism the reporter describes in [mem0ai/mem0#7612](https://github.com/mem0ai/mem0/issues/7612), which reports it for both `Memory` and `AsyncMemory`. The issue is open, created 2026-10-12, with three comments at the time this analysis read it.

## Why the suppression is deterministic only sometimes

The dedup gate is `md5` over the exact extracted string, not over a normalized form and not over a semantic embedding. `text_lemmatized` is computed for BM25, and it is stored in the payload, but it is not what participates in deduplication.

That has a practical implication for anyone trying to reproduce the bug: the failure is exact only when the extraction LLM emits the same characters as the stored, expired copy. Rephrase the fact (`aisle seats` versus `prefers an aisle seat`) and the hash differs, the dedup check passes, and a new row is written — while the stale one stays hidden. Two readers with the same package version can therefore disagree about whether the bug exists, depending on their prompt and model. Treat "reproduces" as "same extraction text on the same top-10 result set", not as a version-level guarantee.

The contaminated-prompt half of the mechanism is softer still, because it depends on how the model reacts to seeing its own expired text. Source-level inspection establishes that the expired row is passed in; it cannot establish what a given model does with it.

## The other half: clearing an expiry still calls the embedding provider

If the row is hidden rather than deleted, the obvious repair is to clear its expiry and let the next `add()` update it in place. In the Python SDK at 2.2.1 the field handling works: `update()` takes `expiration_date` with a sentinel default, and an explicit `None` normalizes to `None`, which `_payload_is_expired` treats as "no expiry":

```python
if expiration_date is not _UNSET:
    update_metadata = update_metadata or {}
    update_metadata["expiration_date"] = _normalize_expiration_date(expiration_date)
```

That is lines 1871-1873, and `_normalize_expiration_date(None)` returns `None` at lines 427-429. Note the sentinel: omitting the argument leaves the field alone, while passing `None` clears it. Collapsing those two cases in your own wrapper is how you get an "update that silently removes the expiry".

What the SDK does not give you is a free clear. `update()` itself embeds only when you pass new text — lines 1875-1877 leave the map empty otherwise:

```python
existing_embeddings = {}
if text is not None:
    existing_embeddings[text] = self.embedding_model.embed(text, "update")
```

That guard is where a source skim stops, and it is not the last word on the call path. `update()` passes the map to `_update_memory()` at line 1879. There, a missing `data` argument is replaced with the stored text (lines 2065-2067), and the embedding step is a cache-or-embed:

```python
if data in existing_embeddings:
    embeddings = existing_embeddings[data]
else:
    embeddings = self.embedding_model.embed(data, "update")
```

For a metadata-only or expiry-only call the map is empty, so the `else` branch always runs: line 2085 embeds the unchanged text, and only then does line 2087 write the payload through `vector_store.update`. The provider call is unnecessary — the vector cannot change — but it sits on the critical path. If it raises, the payload write is never reached, and the expiry is still set on the stored row.

That is exactly what [mem0ai/mem0#7561](https://github.com/mem0ai/mem0/issues/7561) reports: each metadata-only, expiration-set and expiration-clear operation calls embedding once, and injecting an embedding `APIConnectionError` prevents the update while the existing record stays intact. The issue is open, created 2026-10-07, with four comments when read on 2026-10-28, and its environment block names an installed `mem0ai` 2.2.1 distribution running against a real `Memory`/`AsyncMemory`, a temporary local Qdrant and in-memory SQLite, mocking only the external OpenAI `Embeddings.create` boundary. That is the same code the excerpts above come from, which is why this is a confirmed defect on the pinned version rather than an ageing report.

So the clear is conditional: it works when your embedding provider is healthy — at the cost of one embedding call the operation does not need — and raises before persisting when it is not. If the provider is the component that is failing, treat delete-then-add as the fallback rather than the clear, with the caveat in the workaround section that `add()` embeds too: the fallback changes which failure you see, not whether a provider is needed.

The CLIs are worse off. Both expose `--expires` to set an expiration and neither exposes a clear operation, and their platform backends only attach `expiration_date` when the value is truthy, so an explicit null is dropped rather than sent as a clear. That gap is documented in [mem0ai/mem0#7699](https://github.com/mem0ai/mem0/issues/7699), open since 2026-10-21. If your agent's memory maintenance runs through the CLI, the SDK escape hatch is not reachable from it — you need the SDK path or an explicit delete.

## The third path: an impossible date that escapes validation

`2099-02-30` is correctly shaped and impossible. Per [mem0ai/mem0#7713](https://github.com/mem0ai/mem0/issues/7713) (open, created 2026-10-23), the Python CLI's shared `_validate_expires()` helper lets such a date reach `date.fromisoformat`, which raises `ValueError` — uncaught, and in agent mode outside the normal JSON error envelope, so a calling agent gets a traceback-shaped failure instead of a structured error it can branch on.

The reporter's reproduction invokes the real Typer parser with a mocked backend and telemetry disabled; no credentials or live HTTP requests are involved. That is a valid way to test input validation, and it is also why the article treats this as a reported CLI defect rather than something verified against a live install here: the CLI ships separately from the `mem0ai` wheel, so a wheel-version pin does not pin the CLI.

The SDK raises the same `ValueError` deliberately. `_normalize_expiration_date` wraps `date.fromisoformat` and re-raises with a readable message ("expiration_date must be a valid date in YYYY-MM-DD format.") at lines 435-438. The difference is where the error surfaces, not whether it exists: your boundary should reject the date before either the CLI or the SDK has to.

## What actually holds at mem0ai 2.2.1

| Behaviour | Holds at `mem0ai==2.2.1`? | Basis |
| --- | --- | --- |
| Expired row suppresses a fresh inferred `add()` of identical text | Yes | unfiltered `existing_results` in Phase 1/5, `return []` at 1045 |
| Expiry hides rather than deletes | Yes | `_payload_is_expired` used only on read paths |
| SDK clears an expiry via `expiration_date=None` | Yes, at the cost of one embedding call | sentinel at 1871-1873; embed at 2085 before write at 2087 |
| CLI can clear an expiry | No | no flag; falsy value omitted ([#7699](https://github.com/mem0ai/mem0/issues/7699)) |
| Metadata- or expiry-only `update()` calls the embedding provider | Yes | cache miss in `_update_memory`, embed at 2085 ([#7561](https://github.com/mem0ai/mem0/issues/7561)) |
| Impossible CLI date raises uncaught `ValueError` | Reported, not re-executed | [#7713](https://github.com/mem0ai/mem0/issues/7713) |

Version context: `mem0ai` 2.2.1 was uploaded 2026-09-25, per [PyPI metadata](https://pypi.org/pypi/mem0ai/json). The npm/TypeScript line is a separate release train (`ts-v3.3.1`) and is not covered by any claim here.

## A write pattern that does not wait for a fix

The fix belongs upstream. Your agent still has to store the preference tonight, so the pattern below removes the dependency on both halves of the suppression: it deletes the hidden row by identity, writes the new fact with a clean dedup set, and asserts visibility instead of trusting the return value.

```python
from datetime import date, datetime, timezone

def _valid_date(s: str) -> str:
    d = date.fromisoformat(s)                       # raises on 2099-02-30
    if d < datetime.now(timezone.utc).date():
        raise ValueError("expiration_date is already in the past")
    return d.isoformat()

def rewrite_fact(mem, text: str, user_id: str, expires: str) -> dict:
    expires = _valid_date(expires)
    # 1. remove any copy that is expired (hidden from reads, still in dedup)
    for old in mem.get_all(filters={"user_id": user_id}, show_expired=True)["results"]:
        if old["memory"] == text and old.get("expiration_date") and \
           date.fromisoformat(old["expiration_date"]) < datetime.now(timezone.utc).date():
            mem.delete(old["id"])
    # 2. write with a dedup set that no longer contains the ghost
    res = mem.add(text, user_id=user_id, expiration_date=expires)
    # 3. assert the outcome the API will not assert for you
    visible = [m for m in mem.get_all(filters={"user_id": user_id})["results"]
               if m["memory"] == text]
    if not visible:
        raise RuntimeError(f"mem0 accepted the write but it is not visible: {res}")
    return {"added": res, "visible_ids": [m["id"] for m in visible]}
```

Three details make this work rather than merely look tidy. `show_expired=True` is required on the lookup, because the row you must delete is precisely the one the default read hides. `get_all()` returns a `{"results": [...]}` envelope in 2.2.1 and rejects top-level `user_id`, so both the lookup and the verification index `["results"]` and pass the user through `filters`. The delete happens before the add, so the expired hash is absent from the `top_k=10` result set that Phase 5 reads. And the final assertion is on `get_all()`, not on the return value of `add()`, because an empty `results` list is a legal return for "everything was deduplicated".

The assertion generalizes into a test you can keep:

```python
def test_expired_memory_does_not_block_rewrite(mem, user_id):
    mem.add("user prefers aisle seats", user_id=user_id, expiration_date="2026-01-01")
    assert mem.get_all(filters={"user_id": user_id})["results"] == []        # expired = hidden
    assert len(mem.get_all(filters={"user_id": user_id},
                           show_expired=True)["results"]) == 1               # still stored
    rewrite_fact(mem, "user prefers aisle seats", user_id, "2026-12-31")
    assert len([m for m in mem.get_all(filters={"user_id": user_id})["results"]
                if m["memory"] == "user prefers aisle seats"]) == 1
```

One operational note that follows from the same code: delete-then-add does not make the embedding provider optional, because `add()` embeds as well — once for the Phase 1 search query and once per extracted memory. What it changes is where the failure lands. The delete runs first, so a failed `add()` leaves the fact absent rather than merely stale, which is worse if you cannot retry. If the row must survive a failed write, add a differently-worded copy first, confirm it is visible, and only then delete the expired original. And if you write through the CLI, validate the date yourself before it reaches `_validate_expires()`; the SDK's `ValueError` is useful, the CLI's uncaught one is not.

This pattern instantiates the vendor-agnostic checks in [agent memory write-path reliability](/posts/agent-memory-write-path-reliability-2026/): a write is not complete until a read confirms it, and dedup must operate on the same visibility scope as the read path. If you have not set up mem0 yet, the [mem0 setup guide](/posts/mem0-agent-memory-guide-2026/) covers the configuration this pattern assumes; if the question is whether to stay on mem0 at all, compare frameworks in [mem0 vs Zep](/posts/mem0-vs-zep-production-guide-2026/) before debugging expiry, and see the [agent memory framework landscape](/posts/best-ai-agent-memory-frameworks-2026/) for the wider field.

## What this article does and does not establish

Verified by reading the tag, not by running an install: the file at `v2.2.1` was fetched on 2026-10-28 and hashed `f329ca4a17af1fbefb32ac10d4cc7ae7ddbdb7435a87eb74c30915cff98b8b7c`, and the phases, guards, sentinel handling and `return []` quoted above are from that file. No live `add()` or `update()` was executed for this piece, so the end-to-end failures are reconstructed from the pinned control flow and reported by the issue authors against their own installs — including the `update()` embed at line 2085, which the #7561 reporter observed on an installed 2.2.1 with only the external embedding boundary mocked. The CLI date defect is likewise reported, with the reporter's own mocked-backend reproduction, and the CLI is not pinned by the wheel version. Every check here is author-side verification against a public tag you can fetch yourself; no fixture set or evidence directory is offered for download.

Out of scope and not claimed: hosted-platform behaviour, non-Qdrant vector stores beyond the reporter's local setup, async variants as separately tested code paths (they contain the same unfiltered retrieval and dedup blocks), and any statement about recall quality. The one thing worth carrying away is structural: when a system implements expiry as a read-time filter, every write path that reuses unfiltered search results inherits a memory of things the user can no longer see — and a metadata-only update that re-embeds its own text inherits a provider dependency it never needed.
