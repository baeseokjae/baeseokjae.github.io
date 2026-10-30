---
title: "When Agent Memory Returns Nothing: Cognee's Silent Empty-Recall Failures, Measured From Its Own Telemetry"
date: 2026-10-29T00:00:00+00:00
lastmod: 2026-10-29T00:00:00+00:00
tags:
  - Cognee
  - agent memory
  - empty recall
  - NoDataError
  - knowledge graph
  - memory reliability
  - SubprocessTransportError
  - RAG failure modes
  - observability
  - data pipeline
  - cognee 1.6.4
  - agent debugging
description: "Vendor telemetry put 404 NoDataError on 25.8% of Cognee 1.6.1 POST /recall calls on 2026-10-08. A symptom-to-cause triage table, with the v1.6.4 code lines behind each silent failure."
draft: false
schema: "schema-cognee-empty-memory-recall-2026"
---

A memory layer fails quietly in one specific way that matters more than any benchmark score: the agent asks for context, receives nothing usable, and answers anyway. Nothing raises in the application. The model's confidence is unchanged, the user gets a plausible answer with no memory behind it, and no alert fires because from the client's point of view the call returned. Cognee is a graph-and-vector memory library for agents, and its maintainers publish dated fleet telemetry as public GitHub issues. That telemetry is unusual: it gives per-release, per-day denominators for exactly this failure, so the silence can be measured rather than described. This article maps each visible symptom to one cause, one probe, and one fix, and keeps every number tied to the release and date printed in the issue it came from.

The framing that makes the numbers usable: a graph that was never built and a graph that was built but matched nothing are different states, and so is a read path that died mid-session. Cognee reports all three to a careless client as some flavour of "no results". They have separate causes and separate repairs, and the telemetry shows they have wildly different prevalence across releases.

Two limits up front, because they bound everything below. First, every percentage here is the vendor's own fleet aggregate over their installs and calls on a named date, not a rate your deployment should expect; the cohort effect in one of the issues proves how misleading a fleet rate can be. Second, the code mechanisms were checked by reading the source of tag **v1.6.4** at the line numbers cited, not by running a reproduction. No local probe result appears in this article, and none is implied.

## The mechanics: an empty graph, a poisoned pipeline, a dead worker

The first silence is an unbuilt graph. [topoteretes/cognee#5052](https://github.com/topoteretes/cognee/issues/5052), closed on 2026-09-17, replaced a phantom LLM answer with an explicit error: when the knowledge graph is empty but the dataset exists, recall raises `NoDataError`, which the API maps to HTTP 404 with the message "The knowledge graph is empty. Add data and run cognify before searching." When the graph is populated and retrieval simply matched nothing, the same path returns an empty list — a quiet miss with no LLM call. That split is a deliberate contract, and it is also the exact place where naive clients lose information: code that treats any non-200 as "no context available" collapses 404 and 500 into the same branch, and code that treats an empty list as success never notices that the graph is empty.

The second silence is a pipeline whose state is poisoned. In [topoteretes/cognee#5943](https://github.com/topoteretes/cognee/issues/5943) the maintainers trace what happens when a document's source file is deleted after ingest. The per-item status writer only runs on the success path, so an errored item is left without a terminal status; the next `cognify` sees an item that is not marked complete, re-reads the same vanished file, and raises again. One missing file therefore ends every later memory build for that collection, indefinitely, and the operator sees a generic failure rather than "document 7's file is gone."

The third mechanism is about the worker process. Cognee delegates graph-database work to a subprocess harness, and [topoteretes/cognee#5969](https://github.com/topoteretes/cognee/issues/5969) reports a release where recall calls began failing with `SubprocessTransportError` after the engine had been shut down, with the maintainers' own diagnosis marked "likely": the respawn path refuses to run once a shutdown was requested, so a deliberately closed worker stays closed for the life of the client process.

## Symptom triage table

Read this as the operational core. Each row is one symptom as a caller sees it, the cause that produces it, the single cheapest probe that distinguishes it, and the repair — with the source issue that documents the mechanism.

| Symptom at the caller | Likely cause | One probe | One repair | Documented in |
| --- | --- | --- | --- | --- |
| Every recall returns HTTP 404 `NoDataError` | Graph never built, or built into a different dataset | `GET` the dataset's item statuses, then call recall on a dataset known to have vertices | Run `cognify` and assert vertex count is greater than zero before enabling recall | [#5052](https://github.com/topoteretes/cognee/issues/5052), [#5585](https://github.com/topoteretes/cognee/issues/5585) |
| Recall returns `[]` for a query you know is answerable | Read path alive, retrieval threshold or index empty for that query | Call recall twice: once with the exact document's identifier, once with nonsense | Fix retrieval, not ingest; a nonsense query returning `[]` is correct behaviour | [#5052](https://github.com/topoteretes/cognee/issues/5052) |
| `cognify` raises `FileNotFoundError` on every run | An item with no terminal status is re-read each build | Compare dataset item list against the files currently on disk | Delete or replace the orphaned item, then re-run; retrying alone does not clear it | [#5943](https://github.com/topoteretes/cognee/issues/5943) |
| Recall fails with `SubprocessTransportError` after idle time | Worker was shut down and respawn is gated off | Check the client process has not restarted since the first failure | Restart the client process; treat worker death as fatal to the session | [#5969](https://github.com/topoteretes/cognee/issues/5969) |
| Recall fails with HTTP 409 and no cause in the body | Any non-Cognee exception collapsed by the router | Read the server log line `Recall endpoint error`, not the response | Fix the underlying exception; the 409 will never name it | [#5991](https://github.com/topoteretes/cognee/issues/5991) |
| `cognify` ran but the extractor you asked for did not | Keyword arguments are accepted and discarded | `grep` the process for the extractor name in logs | Construct explicit parameters and assert the pipeline config you got back | [#5773](https://github.com/topoteretes/cognee/issues/5773) |
| Relevant passages never returned for noise prompts | No relevance cutoff, so top-k always returns something | Ask a question with no answer in the corpus | Apply a score threshold before injecting context | [#5222](https://github.com/topoteretes/cognee/issues/5222) |

## Case 1: an empty graph is a 404, an unmatched query is an empty list

The prevalence of the first symptom is the largest published number in this series. On 2026-10-08, [topoteretes/cognee#5585](https://github.com/topoteretes/cognee/issues/5585) reports, 25.8% of `POST /recall` calls on release 1.6.1 — 4,895 of 18,945 — returned 404 `NoDataError`, across 214 of 298 deployments, and the same issue records 0.2% on 1.6.2. The issue also names the compounding factor: a set of claude-observer deployments whose builds were failing at a high rate, so their graphs stayed empty and their recalls kept hitting the empty-graph branch. That is why the rate collapsed between adjacent releases without a change to the 404 contract itself.

The operator lesson is not "upgrade" — it is that a 404 and a 500 must not share a branch. A 404 from recall is a fact about your data: there are no vertices. A 500 or a 409 is a fact about your system. Treating them alike turns a one-line diagnostic into an afternoon, because an empty graph and a broken server both look like "memory unavailable".

The probe is cheap enough to run in a test suite, and it distinguishes the four states that matter. The route and payload are left as a placeholder on purpose: the HTTP surface is version-specific, and pinning a path here would be a fabricated API detail.

```python
import httpx

RECALL_PATH = "/replace/with/your/recall/route"   # route and payload are version-specific
BODY = lambda ds, q: {"query": q, "dataset": ds}  # adapt to your release's schema

def classify(status: int, body: str) -> str:
    if status == 404 and "empty" in body.lower():
        return "no_data"               # graph has no vertices: run cognify
    if status == 200 and body.strip() in ("[]", '{"results": []}'):
        return "no_results"            # graph populated, retrieval missed
    if status == 409:
        return "opaque_server_error"   # read the server log, not the body
    return f"other:{status}"

def probe(base: str, datasets: dict[str, str]) -> dict[str, str]:
    out = {}
    with httpx.Client(base_url=base, timeout=30) as c:
        for label, ds in datasets.items():
            r = c.post(RECALL_PATH, json=BODY(ds, "unrelated nonsense string"))
            out[label] = classify(r.status_code, r.text)
    return out

print(probe("http://127.0.0.1:8000", {"never_built": "ds_a", "built": "ds_b"}))
```

Run that against a dataset that was never cognified and one that was, and your client's classification function gets a written-down answer for each. The important assertion is not the status code — it is that your agent's code path can tell the two apart without a human reading a log.

## Case 2: one deleted file fails every later cognify

The mechanism is visible in the v1.6.4 source of [`cognee/modules/pipelines/operations/run_tasks_data_item.py`](https://raw.githubusercontent.com/topoteretes/cognee/v1.6.4/cognee/modules/pipelines/operations/run_tasks_data_item.py). At line 254 the success path writes `status_for_pipeline[str(dataset.id)] = DataItemStatus.DATA_ITEM_PROCESSING_COMPLETED`. The exception handler begins at line 267, and on the default configuration its path ends in a re-raise at line 292 — the only per-item status written for that data item is written on success. Under the default `RAISE_INCREMENTAL_LOADING_ERRORS` value of `"true"`, the error branch logs and re-raises, which is what turns one unreadable file into a failing build rather than a skipped item.

The field rate makes this the second-largest measured contributor. Per [topoteretes/cognee#5943](https://github.com/topoteretes/cognee/issues/5943), `FileNotFoundError` ended 25.8% of failed runs on 2026-10-15 (680 of 2,639) against 1.8% over 2026-10-08 through 2026-10-12, and one 1.6.4 deployment failed 100% of its runs. Read that denominator carefully: it is the share of *failed runs* that ended on this error, not the share of all ingests. Quoting it as "26% of cognify calls fail" would be a category error, and the jump from 1.8% to 25.8% in a week is better explained by a handful of affected deployments than by a fleet-wide regression.

The repair is a dataset-mutation procedure, not a retry. Treat the ingestion of a document as a pair of events — add file, add item — and require the inverse pair on delete. When a build fails this way, reconcile the dataset's item list against the files that exist, remove the orphaned item, and re-run; the second `cognify` will succeed because the item that could not be read is no longer scheduled.

## Case 3: the worker does not come back

[`cognee_db_workers/harness.py`](https://raw.githubusercontent.com/topoteretes/cognee/v1.6.4/cognee_db_workers/harness.py) at v1.6.4 defines `_can_respawn()` at line 1221, returning `self._respawn_factory is not None and not self._shutdown_requested` at line 1222. The respawn machinery exists — that is the part that reads as reassurance in a code review — but it is gated on the same flag that a deliberate shutdown sets, and `call_async` re-raises `SubprocessTransportError` when `attempts_left <= 0` or `_can_respawn()` is false. Once a shutdown has been requested, the client has no path back to a live worker.

The measured consequence, from [topoteretes/cognee#5969](https://github.com/topoteretes/cognee/issues/5969): on 2026-10-16, 19.8% of 1.6.4 SDK recalls failed versus 2.0% on 2026-10-15, with 1,391 `SubprocessTransportError` events plus 273 failed runs from a single deployment; the maintainers' headline figure for that window is that worker transport errors accounted for 51% of fleet recall errors. The same issue records 1.6.3's errored-run share rising to 16–21% from 8.4% on 2026-10-13, and notes that at most three deployments repeating one error accounted for 57–75% of the total.

Label this one honestly: the vendor writes "likely", and the code line corroborates the shape of the mechanism without proving that it caused those specific failures. What the article can assert is narrower and still actionable — a transport error that survives one retry will not clear on its own, so the correct response to `SubprocessTransportError` is a process-level restart plus a health check, not a retry loop behind a cache that keeps the dead harness object.

## Two holes that hide the cause

The first is an opaque status code. [`cognee/api/v1/recall/routers/get_recall_router.py`](https://raw.githubusercontent.com/topoteretes/cognee/v1.6.4/cognee/api/v1/recall/routers/get_recall_router.py) at v1.6.4 handles `CogneeApiError` at line 340, then falls through to a bare `except Exception` at line 361 and logs `"Recall endpoint error"` at line 363 before returning status 409 at line 365. The message is rebuilt rather than echoed, so the HTTP response names no cause. [topoteretes/cognee#5991](https://github.com/topoteretes/cognee/issues/5991) reports the rate for the 1.6.3 API lane: `RuntimeError` failures at 5.3–9.9% daily since 2026-10-12, against 0.8% on 2026-10-11, observed across only 2–6 deployments. The maintainers themselves flag that these errors carry no telemetry, which is the actual complaint: the rate is visible in aggregate while the cause is not visible at all.

The second hole is argument swallowing. [topoteretes/cognee#5773](https://github.com/topoteretes/cognee/issues/5773) documents that `cognify()` ends its signature with `**kwargs` which is never validated, forwarded, or used, so a typo such as `extactor="gliner_demo"` is accepted and discarded with no warning and no error — the call proceeds with the default extractor and the operator believes the requested one ran. This is reported by the issue's author, not by this article's own run, and it stays open at the time of reading.

Both holes share a defence: never assert on the mood of a response. Assert on the status code and the named error class, and assert separately that the configuration you requested is the configuration in effect.

## The other silence: confident, wrong memory

Empty recall is half the problem; the other half is recall that returns something unrelated and is believed. [topoteretes/cognee#5222](https://github.com/topoteretes/cognee/issues/5222) is a request for an optional relevance cutoff, and it carries a reviewed 28-case benchmark against `cognee/cognee:1.6.1` with roughly 400 documents. The result worth quoting: all 7 prompts that had no relevant memory still received 4–5 unrelated passages, 34 in total, and 2 of the 21 cases with known relevant documents missed the top 5 — both exact-identifier lookups, a commit SHA and a ticket or PR number.

Seven noise prompts cannot produce a precise rate, and one lab's corpus is not yours. The transferable finding is the failure shape: with no threshold, top-k retrieval converts "nothing relevant exists" into "here are k passages", which is indistinguishable to the model from genuine context. The fix is different from every fix above — a score cutoff or a lexical boost for identifier-shaped queries — and it deserves its own check, because an agent can pass an empty-recall smoke test and still be answering from noise. If you are choosing where the same symptom shows up on other memory layers, the write-side counterpart is covered in [the Mem0 write-path guide](https://baeseokjae.github.io/posts/mem0-agent-memory-guide-2026/), and [the framework comparison](https://baeseokjae.github.io/posts/agent-memory-comparison-2026/) puts Cognee's position in context.

## What the numbers do and do not say

Three cautions, each grounded in one of the issues above.

A fleet rate is a composition, not a property. [topoteretes/cognee#5353](https://github.com/topoteretes/cognee/issues/5353) reports the 1.6.1 PyPI error rate going from 3.2% on 2026-09-30 to 32.4% on 2026-10-03 as 182 claude-observer deployments arrived from 1.6.0, and shows that errored deployments matched cohort size on both versions — 272 versus 273 on 2026-10-01 — concluding that upgrading did not fix them. A rise in a published rate can be new arrivals failing the same way, so never read one as a regression in code you run.

A rate does not survive re-dating. The 25.8% empty-graph share on 1.6.1 and the 0.2% on 1.6.2 are the same measurement over adjacent releases; quoting either as "Cognee's failure rate" erases the only thing that makes them evidence.

Concentration matters as much as the average. The 57–75% figure in #5969 comes from at most three deployments repeating one error, and the 100% failure in #5943 is one deployment. Fleet percentages are dominated by a few installs with a shared configuration, which is exactly the situation a reader is in — not an independent sample of many.

One more scope limit: the code was read at tag v1.6.4, but [the release list](https://api.github.com/repos/topoteretes/cognee/releases) shows v1.6.5 published 2026-10-16 and v1.6.6rc1 on 2026-10-23, and neither was audited here. The issues cited were open at read time, which is not the same as unfixed in a shipped release. Before you conclude a mechanism is present in your install, check your version and read that version's source.

## A short operational checklist

- Log the HTTP status and the exception class of every memory read. A bare "no results" string is not telemetry, and it is the reason the 409 lane produced a rate with no cause.
- After every `cognify`, assert that each document in the dataset has a terminal item status. The absence of a status is the poison that fails the next build, and it is invisible unless you list items explicitly.
- Treat deleting a source file as a dataset mutation that must be reconciled before the next build. A retry on its own re-raises.
- Distinguish 404 from 409 in client code, and route them to different operator messages: rebuild the graph versus read the server log.
- Run two smoke recalls per upgrade — a known-answer query and a known-empty dataset — and assert the status codes, not the text. [The local observability walkthrough](https://baeseokjae.github.io/posts/agent-doctor-local-observability/) covers how to capture that evidence without a hosted tracer, and [the Zep review](https://baeseokjae.github.io/posts/zep-ai-agent-memory-review-2026/) is the place to compare this failure surface against a temporal-graph alternative.
- For identifier-shaped questions (commit SHAs, ticket numbers), test recall separately from prose questions; both misses in the 28-case benchmark were of that kind.

## What this article did and did not verify

The code claims above are a private author verification by reading v1.6.4 at the cited line numbers; the same three files are linked at their public raw URLs so any reader can repeat the reading, and the line numbers are stable for that tag. No reproduction of the four failure cases was executed for this article, so no pass/fail, timing, or process-table result is reported here — the triage table's probe column is a procedure to run in your own environment, not a result from this one. Every telemetry figure is transcribed as published in its own issue, with that issue's date, denominator, and release attached; the CSV aggregates those issues link were not re-downloaded, so they are cited as the vendor's published aggregate rather than as an independent audit. Where an issue's diagnosis is an inference — the respawn explanation in #5969 — it is labelled as one.
