---
date: 2026-11-01 00:52:00+00:00
description: A 650-trial local fault injection separates a stall before the commit from a stall after it. Regenerating the call id duplicated the effect in 50 of 50 post-commit trials, reusing it duplicated none, and the retry resent 5,640 characters where one call sent 1,920.
draft: false
schema: schema-agent-tool-retry-duplicate-side-effects-2026
tags:
- ai-agents
- reliability
- idempotency
- distributed-systems
- cost-engineering
title: 'Retrying a Failed Tool Call: Duplicate Side Effects and the Token Bill Nobody Meters'
---

An agent loop calls a tool that files a ticket, posts a review comment, or inserts a row. The call stalls and the client gives up at its timeout. The loop does what every retry wrapper does: it tries again. Nobody in that loop knows whether the first attempt reached the database, so the second attempt may be the first real write or the second one. When it is the second, the user sees a duplicate comment under a single logical step, and the token meter shows one step because the meter counts steps, not executions.

The correct answer is not "retry less". It is that a retry is only safe when the server can recognise the second attempt as the same operation. This post measures the difference between the two failure shapes that a client cannot distinguish, and then measures what the retry costs in resent prompt text. The experiment is 650 trials on one host against a local tool server with a SQLite effect ledger, so the duplicate count is read from the database rather than inferred from logs. The retry budget half of this problem is covered in [the circuit-breaker and retry-budget guide](https://baeseokjae.github.io/posts/agent-cost-circuit-breaker-pattern-guide-2026/); this post is about the correctness half that assumes away.

## A timeout is not a failure signal

Amazon's guidance is blunt about the assumption most retry wrappers are built on: "retrying a service call as mitigation for a transient fault is based on a simplifying assumption that an operation can be retried without any side effects" (https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/). The same article states the goal a retry loop has to meet: "we want to make sure that the result of the call happens only once, even if we need to make that call multiple times as part of our retry loop."

The client-side version of the problem is stated just as directly in the AWS timeouts and backoff article: "A timeout or failure doesn't necessarily mean that side effects haven't happened" (https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/). That sentence is the entire failure mode. The client observes a transport outcome; the server holds the truth about the commit; and no amount of retry logic on the client side can recover the truth by trying again.

HTTP does not rescue you either, because agent tool calls are almost always writes. Per RFC 9110 as restated in the Idempotency-Key Internet-Draft, "the methods `OPTIONS`, `HEAD`, `GET`, `PUT` and `DELETE` are idempotent while methods `POST` and `PATCH` are not" (https://datatracker.ietf.org/doc/html/draft-ietf-httpapi-idempotency-key-header). A tool call that creates a comment or a ticket is a POST. It inherits no idempotency guarantee from the protocol, so the guarantee has to be constructed by the caller and honoured by the server.

Stripe's API documentation shows what that construction looks like when it is done properly: the API "supports idempotency for safely retrying requests without accidentally performing the same operation twice", and for API v1 "Stripe saves the status code and body of the first request made with a given idempotency key after endpoint execution begins. Retries with the same key return the saved response" (https://docs.stripe.com/api/idempotent_requests). That construction comes with an expiry, and the wording matters: "For API v1, you can remove keys from the system automatically after they're at least 24 hours old. We generate a new request if a key is reused after the original is pruned." That is permission for the operator to prune keys, not a promise that Stripe expires them on a timer, and it still fixes the boundary a retry loop lives inside: once the key is gone, the same call id is a brand-new request.

## The fixture: one ledger, four policies

The experiment is deliberately small and offline: a `ThreadingHTTPServer` on 127.0.0.1 with one `POST /tool` endpoint, an append-only `effects` table in SQLite, and a `responses` table that stores the status and body under the request's `Idempotency-Key`. A duplicate is a second row in `effects` for the same trial, counted in the database after the client has finished, not inferred from the client's own bookkeeping.

Three fault modes are injected at the server, and the client's timeout is 0.12 s while the late reply takes 0.35 s:

| Fault mode | What the server does | What the client sees |
|---|---|---|
| `none` | Commits, replies 200 | 200 |
| `error_502_before` | Replies 502 without touching the ledger | 502 |
| `timeout_before` | Sleeps past the client timeout, never commits | Timeout, every attempt |
| `timeout_after` | Commits first, then sleeps past the client timeout on the first attempt | Timeout on attempt 1, indistinguishable from `timeout_before` |

Four client policies run against those faults, and the difference between the first two is the whole subject of this post. Policy A retries up to three times, regenerating both the tool call id and the `Idempotency-Key` on each attempt. Policy B retries with the original tool call id reused as the `Idempotency-Key`. Policy C keeps regenerating keys but the server dedupes on `(tool, sha256(args))`. Policy D fails closed and never retries.

Fifty trials run per policy per fault mode (four policies × three fault modes × 50 = 600), plus a 50-trial no-fault control under the blind policy, for 650 ledger rows in total. Two controls had to come out clean before any cell could be read as a finding: the no-fault cell had to commit exactly one effect per trial, and the pre-commit stall had to produce zero duplicates under every policy. The full matrix ran in 108.48 s of wall time on this host, with no model calls and no external network.

## What the 650 trials showed

The table below is the complete fault matrix, read back from `ledger.csv`; every cell is 50 trials. "Effects" is the number of rows the server actually committed per trial, and "final status" is what the client last received, with 0 meaning it timed out and got nothing.

| Policy | Stall before commit | Stall after commit | 502 before commit |
|---|---|---|---|
| A: blind retry, new call id | 0/50 duplicates, 0 effects, 4.0 attempts | **50/50 duplicates, 2 effects**, 2.0 attempts | 0/50 duplicates, 0 effects, 4.0 attempts |
| B: retry, reuse call id | 0/50 duplicates, 0 effects, 4.0 attempts | 0/50 duplicates, 1 effect, 2.0 attempts | 0/50 duplicates, 0 effects, 4.0 attempts |
| C: arg-hash dedupe | 0/50 duplicates, 0 effects, 4.0 attempts | 0/50 duplicates, 1 effect, 2.0 attempts | 0/50 duplicates, 0 effects, 4.0 attempts |
| D: no retry | 0/50 duplicates, 0 effects, 1.0 attempt | 0/50 duplicates, 1 effect, 1.0 attempt | 0/50 duplicates, 0 effects, 1.0 attempt |

The obvious objection is that duplicating after an injected post-commit stall is true by construction. It is, for policy A, and that is exactly why it is presented as a control rather than a discovery: it proves the injector commits before the client gives up, and that the ledger can see the second row. The finding is in the columns beside it. Under the same injected fault, reusing the original call id (B) and server-side argument-hash dedupe (C) both dropped to zero duplicates and left exactly one row in the ledger, by two different mechanisms: B's retry carried the same key and was answered from the response stored under it, while C's retry arrived with a fresh key and was caught by the argument-hash branch, which replied 200 with the id of the effect already written instead of inserting a second one. The pre-commit column is where matching outcomes hide different behaviour. All four policies wrote nothing and duplicated nothing there, but A, B and C averaged 4.0 attempts each against 1.0 for D, and every retrying client still finished with status 0 and no knowledge of whether anything had happened.

That last point is the part that gets lost in retry-policy debates. "Zero duplicates" is not the same as "safe". The pre-commit stall is the honest control for the opposite reason: no effect landed at all, and the retrying policies burned four attempts trying to establish an outcome they never got, ending with status 0 and an unknown result. Duplicate-freedom in that column is not a property of the policy; it is a property of the server never having written anything.

Policy D shows the same trap from the other side. It produced zero duplicates in every column, including the post-commit stall, where exactly one effect did land. The client still ended with no response, so the loop's knowledge of the world after that trial is "unknown", and this harness cannot distinguish D's zero duplicates from a write that succeeded quietly. Anyone adopting fail-closed as the safe option needs a reconciliation step — list-by-causation-id, or a read-back of the resource — or the effect stays unconfirmed until a human notices.

The 502 column adds a cheaper lesson. A 502 that never resolves is a fault no retry can fix, and the retrying policies spent four attempts and 13,080 characters per trial to establish that nothing was written. None of those attempts duplicated anything, because the server rejected them before the ledger, but none of them made progress either.

## The token bill nobody meters

Every retried step re-sends the transcript, and in these trials the resent prompt text is the measurable part of the bill. The first attempt sends a 1,920-character payload; each retry sends that payload plus a 1,800-character transcript allowance.

| Outcome per trial | Attempts | Characters resent | Multiple of one call |
|---|---|---|---|
| Served first time, no fault | 1.0 | 1,920 | 1.00× |
| Post-commit stall, one retry | 2.0 | 5,640 | 2.94× |
| Retries exhausted (stall or 502 before commit) | 4.0 | 13,080 | 6.81× |

The 2.94× is the number a step meter hides. The meter records one tool step; the executions were two; the prompt text sent is 2.94 times what a single execution sends at this payload size. The 6.81× is what a retry loop costs when the fault never clears — and in the 502 column it bought nothing at all. These are character counts from this fixture, not billed tokens: no tokenizer and no vendor price was applied, so the ratios describe the shape of the multiplication, not a dollar figure. The mechanism that makes step meters under-count is the same one described in [the guide to token meters for agent cost tracking](https://baeseokjae.github.io/posts/token-usage-meters-for-agent-cost-tracking/), which counts a logical step per recorded call.

There is a second, quieter cost in the blind-retry policy: the regenerated call id is what made the duplicate possible. In the post-commit column, the call id changed on 50 of 50 policy-A trials and on 0 of 50 under policies B and C, and that difference is the mechanism, not a side effect. A retry wrapper that rebuilds the request from scratch — new id, new key, same arguments — is a duplicate generator the moment the first attempt committed. A retry wrapper that carries the original id forward is a dedupe client.

## What to change in your loop

Carry the tool call id into the idempotency key and do not mint a new one on retry. That single change took the post-commit column from 50/50 to 0/50 here, and it costs nothing in the happy path because the key is only consulted when a retry arrives. If your wrapper builds a fresh request object per attempt, the call id is usually sitting in the original request and only has to be threaded through the retry path rather than regenerated.

Add server-side dedupe on `(tool, argument hash)` as the second line for the case where keys are regenerated by a framework you do not control. Policy C matched policy B's result from the other side of the wire, which matters because the client is not always the component you can change.

Treat the retention window as a real boundary. A stored response only prevents a duplicate while it is still stored; Stripe documents 24 hours as the earliest age at which an API v1 key can be removed, and a key reused after the original is pruned generates a new request. Any retry, replay, or queue-drain path that can run later than the window needs a durable causation record of its own.

Do not adopt fail-closed without a reconcile step. Policy D's zero duplicates includes trials where the effect landed and the client never learned it, and an agent that reports "the tool call failed" in that state will either retry it manually later or tell a user something false. Log the outcome as unknown and read back the resource.

## What this fixture does not show

This is one HTTP server, one SQLite file and a loopback network on a single host. No vendor endpoint, load balancer, or multi-region retry path was exercised, and no named product's retry behaviour is being characterised. The 0.12 s client timeout against a 0.35 s reply is chosen to make the race deterministic, not to model production latency. Only the first attempt of a post-commit trial stalls; a fault that stalls every attempt was run in an earlier pass and discarded because no retry could ever observe the stored response. Retries stop at four attempts, so nothing here says what happens across a process restart, and the argument-hash policy only covers retries that send identical arguments.

The harness, the 650-row ledger, the summary and the method note are published so the matrix can be re-run rather than believed:

- https://github.com/baeseokjae/baeseokjae.github.io/raw/main/research/evidence/agent-tool-retry-duplicate-side-effects-2026/tool_retry_fault_harness.py
- https://github.com/baeseokjae/baeseokjae.github.io/raw/main/research/evidence/agent-tool-retry-duplicate-side-effects-2026/ledger.csv
- https://github.com/baeseokjae/baeseokjae.github.io/raw/main/research/evidence/agent-tool-retry-duplicate-side-effects-2026/summary.json
- https://github.com/baeseokjae/baeseokjae.github.io/raw/main/research/evidence/agent-tool-retry-duplicate-side-effects-2026/method.md

Run it from a private scratch directory with `python3 tool_retry_fault_harness.py --out ledger.csv --faults 50 --db "$TMPDIR/effects.sqlite"`; it writes a fresh ledger and summary and needs no network access beyond loopback. If your agent stack retries tool calls, the useful thing to copy is not the fixture but the two controls: prove that a stall before the commit never duplicates, and prove that the post-commit case does — until the second one fails, a retry policy has not been tested at all.
