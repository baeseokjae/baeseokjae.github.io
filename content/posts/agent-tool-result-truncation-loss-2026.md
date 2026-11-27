---
date: 2026-11-22 00:00:00+00:00
description: 'A 400,110-character tool payload behind a 20,000-character cap loses 95% of its text, and the rule that places the cap decides whether the line that answers the question survives: head-N kept it at 1 of 5 planted positions, tail-N at 1, head+tail at 2, middle-out at 1, and a pattern-centred window at 5. A deterministic survival matrix, the Codex and Ollama code the policies mirror, and a decision rule for paginating instead.'
draft: false
schema: schema-agent-tool-result-truncation-loss-2026
tags:
- ai-agents
- context-management
- agent-tooling
- harness-design
- evaluation
title: 'Your Agent Drops 380 KB of Tool Output. Which Line Survives?'
cover:
  image: /images/agent-tool-result-truncation-loss-2026-presentation.svg
  alt: 'Five-by-five survival matrix: five truncation policies (head-N, tail-N, head+tail, middle-out, match-centred) against five positions of a planted evidence line in a 400,110-character payload at a 20,000-character budget. Head-N keeps the line only at 0%, tail-N only at 100%, head+tail at 0% and 100%, middle-out only at 50%, and the pattern-centred window at all five positions.'
  caption: 'Deterministic fixture, 20,000-character budget of a 400,110-character payload. Filled cells mark the positions where the evidence line survived. No model was called.'
  relative: false
  hidden: false
images:
- /images/agent-tool-result-truncation-loss-2026-presentation.svg
lastmod: '2026-11-26T06:56:00+00:00'
---

A coding agent runs a test suite, a log tail or a recursive grep. The tool returns 400 KB. The harness caps it before the text reaches the model, and the cap is almost always a character or byte budget applied to a fixed part of the string — the head, or the two ends. The agent then answers confidently about a failure whose stack frame was at 62% of the output and never made it into the prompt.

Nothing in the run marks that loss. The tool call succeeded, the model returned prose, the turn billed normally. The only signal is downstream: the agent explains a plausible cause that is not the actual one, or asks for a file it already had.

This article measures the narrow, decidable part of that problem. For a payload where the evidence can be anywhere, which truncation rule keeps the evidence? The experiment is deterministic — a fixed fixture, five policies, five planted positions, one budget, no model — so the numbers below are reproducible on any machine in about a tenth of a second. The model arm (does a model still answer correctly when the evidence survives but sits near a cut?) was not run for this article, and no ranking of policies by answer accuracy is claimed; the last section says exactly what remains unmeasured.

## Three shipped truncation paths, three different cuts

Truncation happens at two layers that are easy to conflate. The first is the model server refusing to render more than its context window. Ollama's `chatPrompt` drops whole messages from the front of the conversation until the rendered prompt fits, re-collecting system messages from the skipped prefix and always keeping the latest message (https://raw.githubusercontent.com/ollama/ollama/v0.20.3/server/prompt.go). That is message-level loss, not character-level: a tool result either fits as a message or disappears entirely. It also interacts with the default the same vendor documents — "By default, Ollama uses a context window size of 4096 tokens", overridable per request through `num_ctx` (https://docs.ollama.com/faq.md, https://docs.ollama.com/api/generate.md). A 400 KB tool result is roughly 100,000 tokens at the four-bytes-per-token approximation Codex uses, so at a 4096-token default no single tool message of that size can be carried at all.

The second layer is the harness trimming the string before it becomes a message. This is where the interesting geometry lives, and OpenAI's Codex CLI ships it in the open. `truncate_middle_chars` splits a byte budget in half, keeps that much from each end, and joins the halves with a marker that names the number of characters removed; `truncate_middle_with_token_budget` does the same on an approximate token budget of four bytes per token, and `plan_token_truncation` builds the same head-and-tail edit with a token-count marker (https://raw.githubusercontent.com/openai/codex/104d2564181d8eb4e67d0c92005f3ab1052051d4/codex-rs/utils/string/src/truncate.rs). The source is explicit that "the marker is outside the retained-text budget", with a separate `truncate_middle_with_marker` for call sites that must fit a hard byte limit including the notice. Codex's tool runner imports `truncate_text` and applies it to tool output bodies before assembling the turn.

So the real menu is small: drop from the front (a head cap, the cheapest rule), keep both ends, keep a middle window, or place the window where a pattern matched. The policies below are exactly those four geometries plus a symmetric tail cap, implemented in stdlib Python and run against the same fixture.

## The measurement

The fixture is deterministic log-shaped text — timestamped `INFO` lines with service, step id, elapsed time and a message — emitted until the payload passes 400,000 characters, with one evidence line inserted at a chosen fraction of the payload, snapped forward to a line boundary:

```
2026-11-22T17:12:00Z ERROR EVIDENCE-MARKER-7f3a build_id=8412 shard=blue-17 status=FAILED
```

The observed payload is 400,110 characters and 400,110 bytes (ASCII), the overshoot being the final whole line plus the evidence line. Every policy is held to the same 20,000-character budget, and the question asked of each is narrow: is the exact evidence line a substring of the emitted string? The five policies are a head cap, a tail cap, a head+tail split of 10,000 characters per end joined by `\n[...snip...]\n`, a 20,000-character window centred on the payload midpoint, and a 20,000-character window centred on the first line matching `ERROR|FATAL|Exception`.

| policy | 0% | 25% | 50% | 75% | 100% | kept |
|---|---|---|---|---|---|---|
| head-N | kept | – | – | – | – | 1/5 |
| tail-N | – | – | – | – | kept | 1/5 |
| head+tail | kept | – | – | – | kept | 2/5 |
| middle-out | – | – | kept | – | – | 1/5 |
| match-centred | kept | kept | kept | kept | kept | 5/5 |

Five policies at five positions is 25 cells; each cell is one row of the results file, with the character spans that survived recorded alongside the verdict. The whole run took 0.067 seconds on one CPU-only host with Python 3.12.3 and the standard library.

The span data is what makes the table more than trivia. With the evidence at 25% (character offset 100,090) and a 20,000-character head cap, the surviving span is `[0, 20000]` — the evidence sits 80,090 characters beyond the cut. The tail cap's span is `[380110, 400110]` at every position: it is not looking at the payload at all, it is looking at its last 5%. The middle-out window is `[190055, 210055]` regardless of the evidence, so it wins exactly where its centre happens to be and nowhere else. Those three rules are position-blind: their spans are constants, and the evidence survives only if the payload happens to place it inside a fixed region.

The pattern-centred window behaves differently in kind, not degree. Its span moves: `[90134, 110134]` at 25%, `[190114, 210114]` at 50%, `[290084, 310084]` at 75%. Because the window follows the first match of the failure regex, and in this fixture the evidence line is itself the first match, it keeps the line at all five positions. That 5/5 is an upper bound with a specific price: the harness has to know what to look for before it truncates, and the first match is not necessarily the informative one. A payload with an early `WARN` converted to `ERROR` by an unrelated retry will capture the window and still lose the answer.

One implementation detail worth copying precisely: the head+tail policy emits 20,014 characters, not 20,000. The 14-character separator sits outside the budget, exactly as Codex documents for its markers. If your cap is enforced against a hard context limit downstream, that overflow is a real byte, and `truncate_middle_with_marker` exists for that reason.

## What the matrix does and does not say

Read as a policy comparison, the table says something unfashionable: for a payload where the evidence can be anywhere, no position-blind rule does better than 2/5, and the common default (a head cap) does 1/5. Increasing the budget does not fix this, because the failure is geometric rather than arithmetic. Doubling the cap to 40,000 characters moves the head cap's reach from 5% of the payload to 10%; the evidence at 62% is still outside it. Only a rule whose span depends on the content, or a budget large enough to hold everything, changes the outcome.

Read as a claim about models, the table says nothing at all. Character survival is not answer correctness. A line that survives inside a 400 KB prompt may still be missed because of where it sits, how the task is phrased, or the model's own limits — and this run did not put a model in the loop. The deterministic half is deliberately separate from that question because it is checkable by anyone: the fixture generator, the five policy functions and the scorer are one 143-line file with no dependencies, and the span arithmetic can be audited line by line.

Three limits bound the numbers. First, the fixture is synthetic and log-shaped with uniform line lengths; real `grep` output has long lines, real test output has clustered failures, and absolute survival at a given position will differ, though the geometry — which span each policy keeps — does not. Second, budgets are characters, not tokens; a tokenizer shifts each policy's effective coverage by an amount this run did not measure, and it can split a line at a boundary. Third, one budget and one payload size were tested; the 20,000-character cap is a realistic harness default, not a universal one, and a policy that loses here can win at a cap near the payload size — where the whole question dissolves anyway.

## The decision rule

Three rules follow from the geometry, and they are ordered by how much they cost you to adopt.

Paginate when the tool can page. If the harness controls the tool, the correct fix is not a better cut but a smaller request: `grep -m`, a log query with a time window, `--tail` on the reader, or a tool-specific offset parameter so the agent can ask for the next slice. A paginated tool makes the loss visible and reversible, which no truncation policy does.

Classify before you centre, and treat the window as a hint. A pattern-centred window only earns its 5/5 when the regex matches the evidence rather than the noise. If you adopt it, centre on a class of lines that is genuinely diagnostic (`ERROR|FATAL|panic|Traceback`, plus the first line of a failure block rather than the last), and keep the head cap behind it so a payload with no match still returns something.

Never rely on a head cap for evidence that can be anywhere — and if you must, say so in the returned text. A silent cap is the failure mode that makes the agent confidently wrong, because the model receives a truncated string with no signal that it is truncated. Codex's marker names the removed count; a bare `text[:20000]` names nothing. The cheapest improvement to most harnesses is not a different rule but a visible one: emit the kept spans, the dropped character count, and enough of the boundary to let the model ask for the rest.

A fourth observation is a warning rather than a rule. The policies that scored 1/5 are not bugs; they are correct implementations of a decision made once, at a layer that cannot see the payload. Whoever sets that budget is choosing where evidence may live. Making the choice explicit — in the tool's contract, in the truncation notice, and in the run log — is worth more than any individual policy in the table.

## Reproduce it, or run it against your own truncator

The measurement is one stdlib script and one results file. Both are published with this article:

- [`truncation_survival.py`](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/agent-tool-result-truncation-loss-2026/truncation_survival.py) — fixture generator, five policies, span recorder, scorer; `python3 truncation_survival.py out.json` takes about 0.07 s.
- [`part_a_results.json`](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/agent-tool-result-truncation-loss-2026/part_a_results.json) — all 25 rows, kept spans, per-fixture SHA-256, environment.
- [`method.md`](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/agent-tool-result-truncation-loss-2026/method.md) — fixture, policies, scoring rule, and the limits repeated above.

To test your own harness rather than this fixture, replace the policy functions with your truncator — the scorer only needs the emitted string and the evidence substring, so a `truncate(text)` wrapper around your production code is enough. Keep the control: run the same payload with truncation disabled and confirm the evidence line is findable in the full text before attributing a miss to the cap.

What remains unmeasured is the model half, and it is the half readers will ask about. The planned arm is a small local model asked, at temperature 0 with repetitions, to quote the evidence line given the truncated context under each policy, with the untruncated payload as the floor control and `prompt_eval_count` recorded so the token cost of each policy is visible. It was not run here. If that control arm fails to quote the line from the full payload, any policy comparison built on it is measuring the model's floor rather than the truncator, and the honest result is that a small model cannot rank policies at all. Until those runs exist, treat the matrix above as what it is: the part of the problem that is arithmetic, and therefore settled.

Two neighbouring measurements bracket this one. The strategy-level question — whether to elide text or summarise it — is covered in [harness design for coding agents](/posts/harness-design-coding-agent-performance-2026/), which finds elision-only competitive but does not resolve where a cut lands. The summarise-side counterpart is [compaction fidelity](/posts/agent-context-compaction-fidelity-2026/), which measures what a summariser retains; a cut is not a summary and fails with a different signature. Where the oversized payload comes from in the first place is the subject of [coding-agent debug logs](/posts/coding-agent-debug-logs-guide-2026/), and the token cost of sending more of it is the subject of [token-waste reduction](/posts/coding-agent-token-waste-reduction-guide-2026/).
