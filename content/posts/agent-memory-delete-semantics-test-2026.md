---
title: "Delete Returns 200: What Agent-Memory Stores Actually Remove (and the read-back that proves it)"
date: 2026-11-01T21:40:00+00:00
lastmod: 2026-11-01T21:47:33+00:00
description: "At mem0 commit 753496c, delete() removes the vector entry, returns success, and writes the deleted text into its SQLite history table, where history(memory_id) returns it with no is_deleted filter. A code-level trace plus a read-back probe you can run against your own store."
draft: false
tags:
  - agent memory deletion
  - mem0 delete history
  - recall after delete
  - memory erasure test
  - vector store delete semantics
  - delete returns success
  - GDPR right to erasure agents
  - agent memory audit
  - mem0 history table
  - chroma delete where filter
schema: "schema-agent-memory-delete-semantics-test-2026"
---

A team tells a customer, or answers a data-protection questionnaire, that a fact can be removed from its agent's memory. The store accepts the delete — by id, by metadata filter, or through a natural-language "forget this" tool — and returns a success message. Nobody runs a recall afterwards. Weeks later the assistant mentions the fact again, or an auditor asks how you proved it was gone and the honest answer is that you watched a return code.

This article is about the gap between those two things. It traces, at one pinned commit, what a successful delete actually removes and what it writes instead, and then hands you a small probe that answers the only question that matters: after the delete says OK, can the fact still be read back?

The short answer for one widely used library: mem0's `Memory.delete(memory_id)` at commit `753496cf1435d76c3a711f3af51303f7fdcb6420` removes the vector entry and returns `{"message": "Memory deleted successfully!"}`, then writes the deleted memory's full text into the `history` table. The read API `Memory.history(memory_id)` selects that text back out with no `is_deleted` filter. Deletion is real for the vector layer and nominal for the audit layer. Whether normal search returns the fact after deletion is a separate question this article does not answer, because answering it needs a runtime probe that was not run here.

If the failure you are chasing is writes that never landed, or expiry rewrites that quietly changed a value, those are covered in [the write-path reliability review](https://baeseokjae.github.io/posts/agent-memory-write-path-reliability-2026/). This page is the read-back side of the same lifecycle.

## Three places a deleted fact can survive

A memory in an agent stack is not one row. It is at least three, and a delete call usually touches only the first.

1. **The vector entry.** An embedding plus payload in Chroma, Qdrant, pgvector, or an in-process store. Delete it and similarity search stops finding it — provided the search runs against the same collection and the same filter scope.
2. **The relational or metadata row.** A `memories` table, a document in a document store, a metadata payload. Delete-by-filter lands here, and this is where filters quietly stop matching: a row written without `user_id` in the payload can never be matched by `where={"user_id": ...}`.
3. **The history, audit, or consolidation table.** The layer that records what changed, so a UI can show "memory edited from X to Y". It exists to preserve the old value. Any read API over it that does not exclude deleted rows will hand the deleted text back.

The reader-facing consequence is simple. "Deleted" is a claim about all three layers, and a status code is evidence about none of them. The only acceptable evidence is a read-back: after the delete returns, query the store the way your agent would, and query the surfaces an operator or auditor would.

## What mem0's delete() does at commit 753496c

The sync path starts at `delete()` in `mem0/memory/main.py`. The whole method is a lookup, a call, some telemetry, and a success string:

```
1883|    def delete(self, memory_id):
...
1892|        existing_memory = self.vector_store.get(vector_id=memory_id)
1893|        if existing_memory is None:
1894|            raise ValueError(f"Memory with id {memory_id} not found")
1895|
1896|        self._delete_memory(memory_id, existing_memory)
...
1902|        return {"message": "Memory deleted successfully!"}
```

The interesting part is `_delete_memory`, at line 2116 in the same class. It reads the payload text first, deletes the vector, and then writes an audit row that contains the text it just deleted:

```
2116|    def _delete_memory(self, memory_id, existing_memory=None):
...
2122|        prev_value = existing_memory.payload.get("data", "")
...
2127|        self.vector_store.delete(vector_id=memory_id)
2128|        self.db.add_history(
2129|            memory_id,
2130|            prev_value,
2131|            None,
2132|            "DELETE",
...
2137|            is_deleted=1,
2138|        )
```

So the vector entry does go. `vector_store.delete(vector_id=memory_id)` is a real removal request against the backing store, and the payload copy is gone from the collection. If your question was "will similarity search still return this vector", the answer for this path is no, assuming the vector store honours delete-by-id — which, for Chroma, its documentation states plainly.

The same file's async mirror at line 3838 does the identical sequence, so an async caller gets the same audit row.

Two operational details are easy to miss in that excerpt.

**Batch deletes only remove what `list()` returns.** `delete_all()` at line 1904 loops from line 1936 until `vector_store.list()` comes back empty, and the source comments on why it loops rather than trusting one pass:

```
1936|        while True:
1937|            memories = self.vector_store.list(
1938|                filters=filters, top_k=DELETE_ALL_BATCH_SIZE
1939|            )[0]
```

The comment just above the loop, at lines 1932-1933, says most vector stores cap `list()` at 100 results by default, "which silently truncates deletes". The loop exists because an unlooped `delete_all` would have removed a page and reported success. That is the nominal-delete problem in miniature: the caller cannot distinguish "removed everything" from "removed the first page".

**Scope is not enforced by the delete path.** `delete(memory_id)` never checks that the id belongs to the caller's `user_id`; it fetches by id and deletes. Tenant scoping in this call path is the caller's responsibility, not the library's. That is a security-adjacent property worth knowing before you expose a delete tool to a model.

## The read-back nobody checks

`Memory.history(memory_id)` is a public method — line 1960 in the same file — and it delegates to the SQLite store:

```
1971|        history = self.db.get_history(memory_id)
```

`get_history` in `mem0/memory/storage.py` is the whole story:

```
227|    def get_history(self, memory_id: str) -> List[Dict[str, Any]]:
228|        with self._lock:
229|            cur = self.connection.execute(
230|                """
231|                SELECT id, memory_id, old_memory, new_memory, event,
232|                       created_at, updated_at, is_deleted, actor_id, role
233|                FROM history
234|                WHERE memory_id = ?
235|                ORDER BY created_at ASC, DATETIME(updated_at) ASC
236|            """,
237|                (memory_id,),
238|            )
```

`is_deleted` is selected and returned as a field. It is not used as a predicate. The `WHERE` clause has exactly one condition, `memory_id = ?`, and no event exclusion, so the `DELETE` row written by `_delete_memory` — the one carrying `old_memory = prev_value` — comes back verbatim in the result list. The caller receives the deleted sentence, its timestamps, and `"is_deleted": true` next to it.

I searched both pinned files for any statement that removes rows from `history`. There is one `DELETE FROM` in `storage.py`, at line 284, and it targets `messages`, the session message cache, with a trimming condition — not the history table. Nothing in the traced code erases history rows for a deleted memory.

Put the two findings together and the failure mode is precise: the promise "we deleted it" is true of the vector layer and false of the audit layer, in the same process, with the plaintext one method call away. The deleted text is not merely retained on disk; it is reachable through a shipped, documented read API that a normal caller can invoke without any special privileges. What follows from that depends on your threat model — an operator console, a support tool, or a "show me what you remember about me" feature built on `history()` all inherit it.

What this does **not** establish: that `search()` returns the fact after deletion. The vector is gone from the collection in this path, so the recall path should not surface it — but "should" is exactly the word this article is trying to retire. Running that check requires an installed store, and none was installed here. See the limitations at the end.

## What Chroma's delete actually covers

Chroma's own documentation for the delete operation, read on 2026-11-01, is unambiguous about matched items:

```
Chroma supports deleting items from a collection by id using .delete. The embeddings,
documents, and metadata associated with each item will be deleted.
```

and, for filters:

```
.delete also supports the where filter. It will delete all items in the collection
that match the where filter.
```

Read literally, both sentences are about items that **match**. Three consequences follow, none of them a defect in Chroma, all of them ways a deletion looks complete and is not:

- **A filter that no longer matches removes nothing.** Delete-by-`where` against a payload key that was never written, or was written as an int where the filter compares a string, matches zero items and returns without error. The caller sees the same success as a delete that matched.
- **Derived copies are out of scope.** A summarised profile, a cached context block, a copy in a second collection, a nightly export — none of these are items in the collection the delete ran against. Chroma's sentence cannot cover them because the API never sees them.
- **Deleting the embedding does not delete your audit trail.** Chroma has no opinion about the SQLite file mem0 writes alongside it. That division of labour is precisely how the mem0 finding above arises.

## The read-back probe

The protocol below is the deliverable. It is four deletion paths and six recall probes per path, with the fields that decide pass or fail recorded per probe rather than summarised into a single boolean that hides which path leaked.

**Fixture.** Seven synthetic facts — invented company, invented people, invented dates — of which four are deleted, one per path. Each fact carries a sentinel string so a leak is unambiguous rather than a judgment call.

**Paths.** delete by id; delete by metadata filter; a natural-language "forget the name of the security questionnaire contact" resolved to candidates and then deleted by id; and a TTL sweep that deletes rows past a retention window.

**Probes.** Per deleted fact, one verbatim recall and five paraphrased recalls phrased the way a user would type them.

**Recorded per probe:** `api_return` (what the delete call returned), `vector_present`, `raw_row_present`, `recall_ids`, `recall_hit`, `returned_text`, `history_row_returned_after_delete`, `history_contains_deleted_text`, `timestamp`.

**Pass/fail, per path, not per store:**

- fail if any of the six recall probes returns the fact's sentinel;
- fail if any shipped read API returns the deleted plaintext after a success return;
- pass only when both are false for that path.

Everything is stdlib Python and SQLite: the harness, the fixture, and a reference store of about ninety lines that implements the six methods your own store needs. To point it at your store you implement the same adapter surface — add, search, delete by id, delete by filter, history, presence checks — and run the four paths unchanged.

Files for this article:

- Probe harness — https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/agent-memory-delete-semantics-test-2026/readback_probe.py
- Synthetic fixture — https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/agent-memory-delete-semantics-test-2026/fixtures/memory_facts.json
- Run record (commands, exit codes, hashes, both runs) — https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/agent-memory-delete-semantics-test-2026/first-party-fixture-run-2026-11-01.json

## What the fixture run showed, and what it did not

The harness was run twice against its own reference store on 2026-11-01, in a local fixture check, not against mem0 or Chroma. Both runs wrote 24 records.

Run 1 keeps an audit table whose read API does not exclude deleted rows — the pattern this article audits. All four paths were flagged: 4 of 4 failed on the history read-back, and 0 of 24 recall probes returned a deleted fact. That split is the point: the recall layer looked clean while the audit layer handed the deleted sentence back on every path.

Run 2 is the same store with the audit read filtered to exclude deleted rows. All four paths passed, 0 of 4 failed, 0 of 24 recall hits. The instrument responds in both directions, which is the minimum bar for believing a negative result from it.

Neither run is a measurement of a vendor product. A store written to demonstrate the probe cannot testify about mem0's or Chroma's behaviour, and the numbers above are counts of records in a JSONL file, not a leak rate in anyone's deployment. The vendor claim in this article comes from the pinned source trace, and it is narrower than the numbers: the plaintext survives the delete in `history`, and `history()` returns it.

## What to assert in CI before promising deletion

If your product tells a customer a fact is gone, the assertion belongs in your test suite, not in a support conversation. In order of how often they catch something:

1. **Delete, then recall.** Six probes: one verbatim, five paraphrased. Assert zero hits. This is the assertion almost no suite has.
2. **Delete, then read every surface an operator can reach.** History endpoints, admin consoles, "what do you know about me" endpoints, exports. Assert the sentinel is absent from all of them. The mem0 finding is invisible to probe 1 alone.
3. **Delete by filter, then check the row count.** A filter that matches nothing returns success. Assert `matched > 0` before you assert the deletion.
4. **Delete, then re-ingest.** Ingest the same source document again and see whether the fact returns through a summary that was never deleted. Deletion that survives one ingest and fails the next is not deletion.
5. **Batch deletes: assert the count.** `delete_all` removes what `list()` pages through. Assert the number of removed ids equals the number stored.
6. **Record the pin.** Write the library commit, the vector-backend version, and the date into the test's output. A deletion property verified against `main` is not verified against the release you ship.

The probe in this article is the shape of assertion 1 and 2, with the fields that make failures diagnosable. Point it at the store you actually deploy, and keep the JSONL.

## Sources for the trace

Every file and line number above was taken from these, fetched on 2026-11-01:

- mem0 memory API (raw file, `main` as fetched) — https://raw.githubusercontent.com/mem0ai/mem0/main/mem0/memory/main.py
- mem0 SQLite history store (raw file, `main` as fetched) — https://raw.githubusercontent.com/mem0ai/mem0/main/mem0/memory/storage.py
- Same two files pinned to the traced commit — https://github.com/mem0ai/mem0/blob/753496cf1435d76c3a711f3af51303f7fdcb6420/mem0/memory/main.py and https://github.com/mem0ai/mem0/blob/753496cf1435d76c3a711f3af51303f7fdcb6420/mem0/memory/storage.py
- Chroma delete documentation, read 2026-11-01 — https://docs.trychroma.com/docs/collections/delete-data

A reader re-verifying this needs no install: open the pinned permalink for the commit and the anchors above resolve exactly as printed, because every excerpt was read from those two files at `753496c` on 2026-11-01. If `main` has advanced since, the permalinks still resolve and the surrounding function is unchanged in structure.

## Limitations

- **Static trace, one commit, one backend.** The mem0 findings are from reading `main.py` and `storage.py` at commit `753496cf1435d76c3a711f3af51303f7fdcb6420`, fetched on 2026-11-01. Later commits may add the missing filter; non-default history backends and the hosted platform were not examined. Do not generalise this to mem0 Cloud or to other libraries.
- **No runtime probe against a vendor store.** mem0, Chroma, Qdrant and pgvector were not installed in the environment this was written in, so no call was executed against them. Every vendor statement above is a reading of pinned source or documentation, not an observation of a running store.
- **`search()` after delete is untested.** The trace shows the vector entry is removed; it does not show that recall is clean. Treat that as unmeasured.
- **Chroma statements are documentation-level.** "Match" is the documented unit of deletion. The article does not claim Chroma fails to delete what it matches.
- **Compliance framing stops here.** This audit does not prove erasure, and nothing here is legal advice. It shows how to produce evidence that a specific delete removed a specific fact from specific surfaces — which is what a DPO question actually asks for.

The wider architecture question — where memory belongs, what should be summarised, what should expire — sits in [the memory architecture pillar](https://baeseokjae.github.io/posts/agent-memory-architecture-guide-2026/). If you are choosing a store first, [the mem0 guide](https://baeseokjae.github.io/posts/mem0-agent-memory-guide-2026/) covers the product surface this trace cuts into, and [the Zep review](https://baeseokjae.github.io/posts/zep-ai-agent-memory-review-2026/) covers a graph-based alternative whose deletion semantics differ. All three assume the delete works. This page is the check that it did.
