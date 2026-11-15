---
title: "Prompt-Prefix Cache in a Local Agent Loop: One Mutable Line at the Top Defeats Prefix Reuse (2026)"
date: 2026-11-14T00:00:00+00:00
description: "On one 2-vCPU host running Ollama 0.20.3 and qwen2.5:0.5b, an append-only second turn prefilled 962 tokens in 2.4711 s, while the same turn with one regenerated 'Session started' line on top took 36.8326 s. The seconds are host-specific; the hit/miss class is what reproduces. How to detect it without a cached-token counter, which harness writes break the prefix, and four assertions to keep it broken or fixed."
draft: false
schema: "schema-local-agent-prompt-cache-invalidation-2026"
tags:
  - prompt prefix cache
  - ollama prompt cache
  - kv cache reuse local llm
  - prompt_eval_duration
  - agent prompt invalidation
  - ollama api generate fields
  - local llm prefill time
  - agent harness timestamp prompt
  - tool registry key order
  - cache miss detection
  - llm agent latency debugging
  - local inference reproducibility
---

Two consecutive turns of a local agent loop can differ by more than an order of magnitude in prefill time while the model, the output length and - within 31 tokens - the prompt size stay nearly the same. On the host used for this article, an append-only second turn prefilled 962 tokens in 2.4711 s. The same second turn, with one line regenerated at the top of the system block, prefilled 993 tokens in 36.8326 s. Nothing errored, nothing was truncated, and no tokens-per-second figure on either turn would have told you which one you were looking at.

The measurement is small and specific: Ollama 0.20.3 at `127.0.0.1:11434`, `qwen2.5:0.5b` Q4_K_M (digest `a8b0c51577010a279d933d14c2a8ab4b268079d44c5c8830c0a93900f1827c67`), `raw=true`, `temperature=0`, `num_predict=3`, `keep_alive=30m`, one model held loaded, ten recorded requests, on a 2-vCPU ARM Neoverse-N1 host that also runs other work. Every timing below belongs to that host. Five turn-1 cold prefills of the same fixture (941-977 server-reported tokens, four distinct prompt hashes) measured 13.2029 s, 25.1871 s, 34.5282 s, 87.9 s and 88.139 s in the same sweep, a 6.7x spread across the same work, and the append-only cold turn repeated 3.49x apart. So the reproducible finding here is the class flip, not any multiplier, and this article quotes none.

## Two consecutive turns, same model, different cache class

The fixture is deterministic: a 25-line policy block (~1.9k characters), six terse JSON function definitions (~1.7k characters), and a scripted user sequence whose prompts grow monotonically. `raw=true` means no chat template is applied, so the sha256 of the prompt string is a faithful fingerprint of the bytes the server received. Each request asked for three output tokens, so decode time could not mask prefill time.

| Arm | Turn | Server prompt tokens | Prefill | Class |
| --- | --- | --- | --- | --- |
| append-only | 1 | 946 | 87.9 s | miss |
| append-only | 2 | 962 | 2.4711 s | hit |
| append-only, repeat | 1 | 946 | 25.1871 s | miss |
| append-only, repeat | 2 | 962 | 2.9636 s | hit |
| timestamp on top | 1 | 977 | 88.139 s | miss |
| timestamp on top | 2 | 993 | 36.8326 s | miss |
| tool keys shuffled once | 1 | 946 | 34.5282 s | miss |
| tool keys shuffled once | 2 | 962 | 0.8822 s | hit |
| tool keys shuffled every turn | 1 | 941 | 13.2029 s | miss |
| tool keys shuffled every turn | 2 | 961 | 11.8796 s | miss |

Read the two middle rows together and the whole problem appears: the timestamp arm's turn 2 sent 993 tokens and took 36.8326 s; the append-only arm's turn 2 sent 962 tokens of the same content and took 2.4711 s. The 31 extra tokens are a 44-character line - the template `Session started <ISO8601-with-microseconds>` plus its newline, regenerated on every turn. The records store only `prompt_chars` and `prompt_sha256`, never the prompt text, so that template is quoted from `method.md` rather than from a recorded request. Both arms were on the same loaded model, minutes apart, same host, same output length.

Classification rule used here: prefill under 5 s is a hit, over 5 s is a miss. No threshold anywhere in the 3-10 s band changes any of the ten labels, because the two groups measured 0.8822-2.9636 s and 11.8796-88.139 s. The gap is a property of this host's prefill speed versus near-zero reuse cost, not a constant, and the script below makes you calibrate your own.

## What the server actually reuses

The reused object is the evaluated key/value prefix, not "the prompt" as a document. A server that keeps a prefix compares the incoming token sequence against the retained one until the first divergence and evaluates only what follows. A divergence at position 0 discards every token after it, which is why a line prepended above the system block is worse than the same line appended at the end: the append is below the divergence point and costs nothing beyond its own tokens.

The per-request fields are documented, and their units matter. `prompt_eval_count` is "Number of input tokens in the prompt", `prompt_eval_cached_count` is "Number of prompt tokens read from the cache", `prompt_eval_duration` is "Time spent evaluating uncached prompt tokens in nanoseconds", and `load_duration` is "Time spent loading the model in nanoseconds" ([Ollama generate endpoint reference](https://docs.ollama.com/api/generate)). The API documentation states the convention directly: "All durations are returned in nanoseconds" ([Ollama API docs](https://raw.githubusercontent.com/ollama/ollama/main/docs/api.md)), which is why a raw response delivers these values as nanosecond integers: the table's 2.4711 s is 2471100000 ns (seconds x 1e9). Note the direction of that conversion - the published `results.jsonl` stores `prompt_eval_duration_s` rounded to four decimals, so the nanosecond integer is reconstructed from the stored seconds, not read out of the record.

Two consequences follow from those definitions. First, `prompt_eval_duration` times only the uncached remainder, so a hit's prefill rate is not comparable to a cold prefill rate computed from `prompt_eval_count` - the denominator differs by the size of the reused prefix. Second, if a build returns no cached-token count, the duration is the only signal you have, and it is a duration rather than a count, so it carries the host's noise with it. That is exactly the situation measured here: none of the ten responses contained `prompt_eval_cached_count`. Every response carried the same eleven keys - `created_at`, `done`, `done_reason`, `eval_count`, `eval_duration`, `load_duration`, `model`, `prompt_eval_count`, `prompt_eval_duration`, `response`, `total_duration` - so the token split is not directly readable on this build, and the class has to be inferred from time.

The scope of the reuse is per loaded slot, which is why the sweep ran variants consecutively rather than interleaved. llama.cpp's server, which underlies this style of local serving, advertises "Parallel decoding with multi-user support" and continuous batching ([llama.cpp server README](https://raw.githubusercontent.com/ggml-org/llama.cpp/master/tools/server/README.md)); retained prefix state therefore belongs to a slot, and sending variant B between two turns of variant A would overwrite the very prefix being tested. The cost of that choice is that cross-variant comparisons in the table above carry host drift, which is a second reason only the class is asserted. For what happens when two loops genuinely share one server, that is slot contention, and it is a different mechanism from prefix invalidation.

## Detecting a hit when there is no cached-token counter

Start by printing your own response keys. If `prompt_eval_cached_count` is present and non-zero, read the split directly and stop guessing. If it is absent - as it was in all ten responses here - derive the class from `prompt_eval_duration`, or send the same prompt twice and compare. The first method is cheaper and was used for this sweep; the second is more robust because it does not depend on a threshold.

The rule that worked here: a hit prefills at hundreds to a thousand tokens per second, a cold prefill at tens. Expressed in seconds rather than rates, hits landed at 0.8822-2.9636 s and misses at 11.8796-88.139 s on a ~950-token fixture. The 4.01x floor between the slowest hit and the fastest miss is what makes a threshold usable, and it is also why the threshold is not portable: a machine that prefills 950 tokens in 0.3 s compresses both groups into a band where 5 s is meaningless. Calibrate with one deliberate cold request and one deliberate reuse on your own host before trusting any label.

Log per turn, not per session, or the record cannot answer the question later:

```json
{"variant": "append_only", "turn": 2, "prompt_chars": 3746,
 "prompt_sha256": "c9bde789f79072c732732fa18a59ea7706af248a50c6ef5495001e319cad14b8",
 "prompt_eval_count": 962, "prompt_eval_cached_count": null,
 "prompt_eval_duration_s": 2.4711, "eval_count": 3, "eval_duration_s": 2.4844,
 "load_duration_s": 0.3559, "wall_s": 5.332,
 "response_keys": ["created_at", "done", "done_reason", "eval_count", "eval_duration",
                   "load_duration", "model", "prompt_eval_count", "prompt_eval_duration",
                   "response", "total_duration"]}
```

That record shape is the one in the published `results.jsonl`, and `prompt_eval_cached_count` is stored as `null` rather than coerced to `0`, because a missing field and a measured zero mean different things to whoever reads the file next.

## The four harness writes that break the prefix

Two of these were measured in the sweep; two are reasoned from prefix identity and are labelled as untested here.

A timestamp or step counter above the system block. Measured. The 44-character `Session started` line cost 31 server-reported prompt tokens and moved the turn from the hit class to the miss class: 993 tokens in 36.8326 s against 962 tokens in 2.4711 s. It is the most common version of this bug because it looks like good observability.

A tool registry re-serialised with a different key order on every turn. Measured. The same six definitions, differing only in JSON key order per turn, produced a miss on turn 2 at 961 tokens and 11.8796 s. The control matters more than the finding: the identical registry shuffled once and then held constant produced a hit at 962 tokens and 0.8822 s. Key order is not harmful by itself; per-turn key instability is. Any registry built from a dict whose insertion order depends on iteration, a set, a database result, or a template engine with unstable ordering is exposed.

A memory or scratch block inserted above the conversation instead of appended. Reasoned, not tested here. Insertion above the history moves the divergence point to the insertion, which discards the system block and every prior turn. Appending the same text below the last user line leaves the prefix intact.

Messages reassembled in a different order, or re-summarised each turn. Reasoned, not tested here. Both replace the retained sequence rather than extending it. Note that re-summarising is the expensive case twice over: it breaks the prefix and it changes content.

No multiplier is attached to any of these. The 6.7x spread across five turn-1 cold prefills of the same fixture (941-977 tokens) makes per-arm ratios meaningless, and the 36.8326 s figure is what this loaded host produced at 18:08 UTC on 2026-11-14, not a prediction.

## What it costs across a loop, honestly

This sweep measured two turns per arm, not ten, so the loop-level cost below is arithmetic over the measured per-turn costs, labelled as arithmetic, and never presented as a measured cumulative.

Take the two measured per-turn costs for the same fixture: a hit at 2.4711 s and a cold prefill at 87.9 s on this host. A ten-turn loop with a stable prefix pays one cold prefill plus nine hits: 87.9 + 9 x 2.4711 = 110.14 s of prefill. The same loop with a per-turn timestamp line at the top pays ten cold prefills: 10 x 87.9 = 879 s. That comparison is honest only if you also read the noise: the same cold turn re-measured at 25.1871 s, so the same arithmetic on a quieter moment gives 25.19 + 9 x 2.4711 = 47.43 s against 251.9 s. The shape of the difference survives; the numbers do not transfer.

The practical translation is not a ratio but a question about your own logs: in a ten-turn session, is the prefill duration roughly constant across turns, or does it collapse after turn 1? If it collapses, you have reuse. If it stays flat while the prompt grows, something above the conversation is being rewritten, and the fix is to move that write below the first stable token.

## Asserting it in CI

Four assertions, in increasing order of strength. The first two catch regressions in a harness that currently works; the third proves the test is measuring what it claims; the fourth keeps the threshold honest on the machine running it.

1. Prefix identity. For an append-only turn, the next prompt must repeat every byte of the previous prompt up to the previous generation point. Compare hashes of the common region, not strings by eye - and note that the generation trailer is not part of the reusable prefix, because a server matches tokens until divergence and the trailer is where the previous request stopped. Getting this wrong produces a false failure, which is how this article's own reader script initially failed its own check.
2. Class expectation. Turn 2 of an append-only loop must classify as a hit. If it does not, either the harness changed or the server dropped the prefix; both are worth failing the build for.
3. Negative control. Prepend one deliberately mutable line and require the next turn to flip to a miss. Without this, a probe that never had a hit in the first place passes assertion 2 by accident on a fast host.
4. Threshold calibration. Print the measured cold and reuse durations and their separation on the current host. A threshold imported from another machine is not a test.

Two false positives to design around, both observed while building this sweep. A cold model load looks like an invalidation: `load_duration` is reported separately, and the first request after an idle period carries it, so warm the model once with a throwaway request and set `keep_alive` explicitly. And a warm-up miss looks like a regression if it is counted as turn 1, so start recording after the warm-up and say so in the run record.

The condensed probe that implements these four assertions is published with this article: [`cache_probe.py`](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/local-agent-prompt-cache-invalidation-2026/cache_probe.py). It is stdlib-only, takes `--model` and `--endpoint`, replaces one `build_prompt()` function to point at your own agent, prints `prompt tokens, prefill s, hit|miss|unknown` per turn, and exits non-zero on a failed assertion. `--dry-run` performs the prefix assertions without sending a request, which is what a CI job can run on every commit. Both modes were checked here: the first dry-run failed assertion 1 on the script's own fixture, because the comparison included the generation trailer - the false failure described above - and passed once the comparison was cut at the previous generation point. A live re-run against `qwen3:0.6b` on the same server then reported all four assertions PASS over three requests, at server-reported prompt sizes of 202, 211 and 247 tokens for the cold turn, the append-only second turn and the mutated control. That check is a private local author verification: its run record was not added to this article's published evidence set, so its timings are not quoted and cannot be re-derived from the files below. The token sizes belong to a different fixture and model and are not part of the findings above either; mixing them into the table would be exactly the unlabelled transplant this article warns about.

The full harness that produced the numbers - variant sequencing, deadline reserve, per-record fsync - is also published, along with the raw records and the environment capture:

- [`results.jsonl`](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/local-agent-prompt-cache-invalidation-2026/results.jsonl) - ten raw records, one per request
- [`summary.json`](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/local-agent-prompt-cache-invalidation-2026/summary.json) - derived table, hit/miss bounds, noise caveat
- [`env.json`](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/local-agent-prompt-cache-invalidation-2026/env.json) - host, Ollama version, model digest, response keys
- [`method.md`](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/local-agent-prompt-cache-invalidation-2026/method.md) - fixture, variants, classification rule, limitations
- [`probe.py`](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/local-agent-prompt-cache-invalidation-2026/probe.py) and `probe2.py` - the sweep harness as run

Files may lag the article by one deployment; if a link 404s in the first minutes, the path is right and the commit is not.

## What this does not tell you

It is not a hardware benchmark: one shared 2-vCPU host, one model, ten requests, and a 6.7x spread across five cold prefills of the same fixture (941-977 tokens). It is not a statement about Ollama in general: the behaviour was observed on 0.20.3, engine-internal cache policy was not read in source, and a different version may return `prompt_eval_cached_count` and make the whole inference unnecessary. It says nothing about hosted prompt-caching products, whose accounting and invalidation rules this sweep never touched. It says nothing about multi-slot concurrency beyond noting that retained prefixes are per slot. And it does not give you a per-turn cost you can put in a budget: the class is portable, the seconds are not.

What it does give you is a detection method that costs one extra request and one assertion: send a second turn, look at `prompt_eval_duration`, and check whether the bytes at the top of the prompt are the same bytes you sent last time. If you are debugging a local agent that feels fast on turn one and slow on turn eight, start there - before you change the model, the quantisation, or the context length. The related arithmetic for what a turn costs once prefill is settled is in [the turn-time budget breakdown](/posts/local-agent-turn-time-budget-2026/), the standing per-turn price of the tool registry is measured in [the tool-definition token cost audit](/posts/ollama-tool-definition-prompt-token-cost-2026/), and the other reason two local agent loops slow each other down is covered in [concurrent local agent sessions](/posts/local-llm-concurrent-agent-sessions-2026/).
