---
title: "Same Seed, Different Bytes: Measuring Tool-Call Repeatability Before You Trust an Agent Eval (2026)"
date: 2026-11-15T13:38:00+00:00
lastmod: 2026-11-15T14:00:00+00:00
description: "13 replays of one fixed tool-calling request on Ollama 0.20.3 with qwen3:0.6b at seed 42: all 13 calls were semantically identical, but only 11 were byte-identical, and both flips happened at temperature 0.0. Includes the probe, the raw per-call JSONL and a normalise-then-hash helper."
draft: false
tags:
  - tool call repeatability
  - agent eval flakiness
  - seed determinism
  - temperature 0 not deterministic
  - tool_calls arguments
  - JSON key order
  - golden file test
  - Ollama tool calling
  - eval snapshot testing
  - local LLM reproducibility
schema: "schema-agent-tool-call-repeatability-2026"
---

A team re-runs its agent eval after a one-line prompt change and the pass rate moves five points. They revert the prompt; the number does not come back. They blame the harness, then the model vendor, and eventually pin `temperature=0` and `seed=42` everywhere — and the number still moves. Nobody in that loop can answer the question that comes before all of it: at the sampling settings the harness already uses, is the emitted tool call even the same object twice?

Three different properties get conflated in that question. **Semantic agreement** is the same tool name with the same argument values, which is all an eval should assert on. **Byte identity** is the same argument text, including key order and numeric formatting, which is what a golden-file or snapshot test actually asserts on. **Prompt-shape dependence** is the fact that the same question asked as turn one and as turn four arrives with different history and different prefill, so a flip measured in one shape says nothing about the other.

This page answers four questions with a measurement rather than an argument: how often a pinned call repeats semantically and how often byte-for-byte; whether those two rates differ and in which direction; whether adding one history turn or padding the prompt changes either; and what a harness should therefore assert. The sample is small and is stated up front so nothing below has to be discounted later: **13 calls across four prompt shapes**, one model, one host, seed 42, zero errors. All 13 were semantically identical. Eleven of 13 were byte-identical, and both of the byte flips happened at `temperature=0.0`. The N=20-per-condition matrix in the original plan was not run — the attempt budget does not hold 20–40 minutes of wall time on the host — so the numbers below are **counts with denominators, not rates**, and the difference matters.

## What the vendors actually promise

Ollama's API documentation offers the seed as the route to repeatability: "For reproducible outputs, set `seed` to a number" ([github.com/ollama/ollama/blob/main/docs/api.md](https://github.com/ollama/ollama/blob/main/docs/api.md)). Its Modelfile reference states the promise more directly — setting `seed` to a specific number "will make the model generate the same text for the same prompt" ([docs/modelfile.mdx](https://github.com/ollama/ollama/blob/main/docs/modelfile.mdx)). vLLM frames the same property at the sampling layer, and goes further about temperature: "In V1, the seed parameter defaults to 0 which sets the random state for each worker, so the results will remain consistent for each vLLM run even if temperature > 0" — while also opening its page with "vLLM does not guarantee the reproducibility of the results by default, for the sake of performance" ([docs.vllm.ai reproducibility](https://docs.vllm.ai/en/latest/usage/reproducibility.html)).

Both promises are about the same kind of object: generated text, or the random state that produces it. The thing an agent harness asserts on is a different kind of object. `tool_calls[0].function.arguments` is a structured value that the server serialises back to JSON, and a JSON object is, per RFC 8259, "an unordered collection of zero or more name/value pairs" ([rfc-editor.org/rfc/rfc8259.txt](https://www.rfc-editor.org/rfc/rfc8259.txt)). Two serialisations of the same arguments can therefore differ in member order while denoting the same value. None of the three vendor pages above says anything about member order in a structured argument payload, and none of them measures it. A harness that treats the serialised arguments as a string inherits a property that its vendor documentation never claimed to control.

## What was measured, and what it cannot tell you

The fixture is one fixed coding-agent request: a single tool `stat_path` with `path` (string), `mode` (enum `stat|read|hash`) and `max_bytes` (integer), and the instruction "Check whether docs/config.md exists and get its hash. Use the tool." Every response was recorded verbatim; no expected output was written by hand. The probe posted to `http://127.0.0.1:11434/api/chat` with `stream=false`, `think=false`, `num_predict=80`, `num_ctx=4096` and `seed=42`, and recorded per call the raw arguments value, the deserialised object, its key order, and two digests: `sha256(json.dumps(args))` for the byte form and `sha256(json.dumps(args, sort_keys=True))` for the semantic form.

The server was Ollama 0.20.3 on a CPU-only Linux host (2 vCPU, 11 GB RAM, no GPU). The model was `qwen3:0.6b`, digest `7df6b6e09427a769808717c0a93cadc4ae99ed4eb8bf5ca557c90846becea435`, Q4_K_M, 751.63M parameters as reported by the server. `qwen2.5:0.5b` was installed and identified but not measured, so nothing here is a two-model claim. The four conditions and their sample sizes are in the table below; the exact environment, request body and the deviations from the original plan are in [METHOD.md](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/agent-tool-call-repeatability-2026/METHOD.md).

| Condition | Shape | Temp | N | Semantic distinct | Byte distinct | Byte identical | Key orders observed | prompt_eval_count |
|---|---|---|---|---|---|---|---|---|
| S1 | single turn | 0.0 | 4 | 1 | 1 | 4/4 | (path,mode)×4 | 197 |
| S2 | one prior turn (user, assistant tool_call, tool result) | 0.0 | 3 | 1 | 2 | 2/3 | (mode,path)×2, (path,mode)×1 | 268 |
| S3 | ~1,200-token repository listing prefix (1,420 total prompt tokens) | 0.0 | 3 | 1 | 2 | 2/3 | (path,mode)×2, (mode,path)×1 | 1,420 |
| S4 | single turn | 0.7 | 3 | 1 | 1 | 3/3 | (path,mode)×3 | 197 |

Three caveats belong next to that table rather than after it. The host was **shared with a concurrent stage workload for the entire window**, so wall time was recorded but is not interpretable and no latency or throughput claim is made. The design was **round-robin rather than condition-by-condition**, because a sequential loop would have spent the whole budget on S1 when each long-prompt call took 87–116 seconds. And the digests score the arguments object **as the `/api/chat` response serialises it** — this run cannot separate a model-side token-order difference from a server-side parse-and-reserialise step, and does not assert which it was.

## Result: 13/13 semantic, 11/13 byte

Every one of the 13 calls emitted exactly one tool call, named `stat_path`, with `path=docs/config.md`, `mode=hash` and no `max_bytes`. Argument values never drifted, no required argument went missing, and no extra field appeared. Under sorted-key comparison the 13 calls collapse to a single digest; replayed through the normaliser in the last section, all 13 records produce one distinct semantic digest.

Byte identity is the part that did not hold. In S2 and S3, one call out of three carried the same two members in the opposite order from its two siblings. The flip is the whole finding, so it is worth seeing in full:

```json
{"path": "docs/config.md", "mode": "hash"}
{"mode": "hash", "path": "docs/config.md"}
```

That is a difference a consumer of the call cannot observe — `json.loads` produces an equal dict either way — and a difference a text diff observes immediately. In this sample it appeared in the two conditions whose prompt was not the minimal one, and it did not appear at `temperature=0.7`.

Which is exactly where the result has to be handled carefully. The most tempting sentence to write here is "temperature does not matter", and it is not supported. With N=3–4 there is no power to order conditions by flip probability; temperature and prompt shape are confounded with **which condition happened to catch a flip**; and 3/3 stability at `temperature=0.7` is not evidence that 0.7 is safer. The defensible claim is narrower and still useful: in this sample, pinning `temperature=0` was **not sufficient** for byte identity, so a harness that attributes a moved pass rate to its prompt has at least one other candidate cause it has not eliminated.

## Why a golden-file test is the wrong assertion

A snapshot test that stores `json.dumps(arguments)` and compares strings is asserting on member order. JSON defines that order as carrying no meaning, so the assertion is stricter than the contract the data is published under. The failure modes that follow are ordinary and expensive:

- **Snapshot churn for no reason.** A stored call expires because the same value came back in a different order. Someone re-records the snapshot; the test goes green; nobody learns anything.
- **Retry accounting that hides the real difference.** If a harness retries on snapshot mismatch, a flip costs an extra call and the recorded pass rate now depends on retry policy — a separate and much better-documented hazard ([agent-tool-retry-duplicate-side-effects-2026](https://baeseokjae.github.io/posts/agent-tool-retry-duplicate-side-effects-2026/)).
- **A pass rate that moves for reasons unrelated to the change under test.** This is the opening scene. The flip is not proof that it explains a five-point move — 13 calls cannot support that — but it is a mechanism that produces exactly that symptom while every input is held fixed.

Two adjacent failures are worth separating out, because both look like this and neither is. An agent that repeats a failing action because its loop has no state guard is a control-flow bug, not sampling variance ([deterministic-agent-loop-failures-2026](https://baeseokjae.github.io/posts/deterministic-agent-loop-failures-2026/)). A tool call that comes back with its arguments retyped or its history corrupted is a transcript-handling problem, and the first thing to rule out is ordinary run-to-run variance, which is what this page measures ([ollama-tool-call-history-corruption-2026](https://baeseokjae.github.io/posts/ollama-tool-call-history-corruption-2026/)).

## What to assert instead: normalise, then compare, then hash

The recipe is short. Extract the tool name and the arguments, coerce a JSON-string argument into an object, compare with sorted keys, and hash the sorted form when a test needs a stable identifier. The helper below is a real file in the evidence directory, standard library only, and it is what produced the "one distinct digest" statement above when replayed over the 13 raw records:

```python
def normalise_tool_call(message, required=None):
    calls = (message or {}).get("tool_calls") or []
    if not calls:
        return None, {}, None, ["no_tool_call"]
    fn = calls[0].get("function") or {}
    name, args, problems = fn.get("name"), fn.get("arguments"), []
    if isinstance(args, str):                 # args emitted as a JSON string
        args = json.loads(args)
    if not isinstance(args, dict):
        return name, {}, None, ["arguments_not_object"]
    problems += ["missing:" + k for k in (required or []) if k not in args]
    canon = json.dumps({"name": name, "arguments": args},
                       sort_keys=True, separators=(",", ":"))
    return name, args, hashlib.sha256(canon.encode()).hexdigest(), problems
```

The four cases a normaliser has to survive are the ones that actually appear in transcripts: arguments already an object; arguments emitted as a JSON string; a required argument missing; and no tool call at all. The version in [normalise_tool_call.py](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/agent-tool-call-repeatability-2026/normalise_tool_call.py) carries those four plus the missing-argument variant as runnable self-tests, and [normalise_selftest.txt](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/agent-tool-call-repeatability-2026/normalise_selftest.txt) is the captured output of the run, including the replay over all 13 records: one digest, five cases passing.

Normalising fixes the assertion. It does not fix the ambiguity about whether the model's *values* are stable, which is why the second half of the recipe is a stability check at the settings the harness actually uses.

## How to size your own check

The probe is in the evidence directory as it was run — interleaved round-robin, an internal wall-clock budget, append-only JSONL flushed before the next call starts, tolerant of str-or-dict arguments ([repeat_probe.py](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/agent-tool-call-repeatability-2026/repeat_probe.py)). Point it at your own server and model, and run it in the prompt shapes your harness actually uses, not just the minimal one: in this table the flips appeared only in the two non-minimal shapes, and a stability check that only covers single-turn prompts would have reported 4/4 and 3/3 and missed them.

The decision rule is what to do with the output, and it has to respect the sample. If every call in your sample is identical, that is a statement about your sample, your model and your prompt shapes — not about determinism in general. If some calls flip, you have found the mechanism and still cannot size it from a handful of replays; report the counts with their denominators and say so. A 2/3 result is compatible with anything from a few percent to most calls flipping, and a table that prints it as "67% flaky" is inventing a rate the sample cannot support.

Every file behind the table is downloadable and was inspected for credentials and host-identifying data before publication: the raw per-call records are in [run.jsonl](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/agent-tool-call-repeatability-2026/run.jsonl), the one-line-per-call log including the two `BUDGET_EXHAUSTED` markers is [probe.log](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/agent-tool-call-repeatability-2026/probe.log), and the table above is also stored as [flip_table.csv](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/agent-tool-call-repeatability-2026/flip_table.csv). Each record carries the condition label, the emitted tool call with its key order and both digests, and the server counters; the prompt text itself (the single-turn instruction, the history turn and the repository listing) lives in `repeat_probe.py`.

## What this does not show

One host, one model, one fixture, 13 calls, a shared machine. Nothing here estimates a flip rate, and nothing here attributes the key-order difference to the model or to the server — the measurement scores the serialised response and stops there. Only `qwen3:0.6b` was run, so there is no quantisation comparison and no two-model comparison. The fixture instruction has one obviously correct call, which means argument-*value* drift under genuine ambiguity is untested and is a different question from the key-order drift observed here. The vendor pages establish what is promised, not what a specific server build implements, and none of them was checked for version drift against Ollama 0.20.3.

The follow-up that would change the picture is ordinary and unglamorous: the same fixture across two models, with N large enough on an idle host to separate a rate from a coincidence. Until someone runs it, the safe harness is the one that normalises before comparing — safe regardless of how these counts replicate — and the safe benchmark claim is the one that names its sample size instead of implying determinism it never measured.

Related reading: the principle that eval scores move between runs, at benchmark scale rather than at the level of one emitted call, is covered in [llm-benchmark-variance-2026](https://baeseokjae.github.io/posts/llm-benchmark-variance-2026/); the request shape and tool registry used here are in [ollama-api-local-llm-integration-developer-guide-2026](https://baeseokjae.github.io/posts/ollama-api-local-llm-integration-developer-guide-2026/); what the same registry costs in prompt tokens is in [ollama-tool-definition-prompt-token-cost-2026](https://baeseokjae.github.io/posts/ollama-tool-definition-prompt-token-cost-2026/); and how to declare the assertion this table justifies is in [assert-agent-evaluation-harness-2026](https://baeseokjae.github.io/posts/assert-agent-evaluation-harness-2026/).
