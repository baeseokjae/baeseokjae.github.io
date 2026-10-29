---
title: "vLLM Streaming Tool-Call Corruption: Detecting Merged, Truncated and Retyped Arguments Before Your Agent Executes Them"
date: 2026-10-28T00:00:00+00:00
lastmod: 2026-10-28T00:00:00+00:00
tags:
  - vLLM
  - vLLM tool call parser
  - streaming tool calls
  - tool call corruption
  - SSE chunk boundary
  - OpenAI compatible API
  - function calling
  - local LLM serving
  - agent safety
  - schema validation
  - tool-call gate
  - vLLM 0.32.0
description: "Three open vLLM reports show merged, truncated and dropped tool-call arguments at different version scopes. Here is how to localize the fault and gate execution."
draft: false
schema: "schema-vllm-streaming-tool-call-parser-corruption-2026"
---

A streaming tool call can reach your agent corrupted while every SSE frame on the wire is valid JSON. The damage shows up after reassembly: two calls fused into one, an argument string cut mid-token, or a number that became the string `"3"`. The request returns HTTP 200, `finish_reason` says `tool_calls`, and an agent that trusts the payload executes the wrong thing. The practical question is not whether vLLM is "broken" in general; it is whether the corruption is in the server's parser or in your client's reassembly, and how to stop execution until that is settled. This article separates what the current primary reports actually establish, shows how to localize the fault with a raw SSE capture, and ships a small gate that refuses any call whose arguments do not round-trip against your declared schema.

## What the three open reports actually establish

The first report is [vllm-project/vllm#64012](https://github.com/vllm-project/vllm/issues/64012), filed 2026-10-27 and still open. It is explicitly a legacy-version report: the reporter confirms the failure on **vLLM 0.19.0** with `vllm/tool_parsers/qwen3xml_tool_parser.py` at SHA256 `7c2ba229b0b6dcd061b9f581390a5fb892a2fc20023b20656d91706522f311bd`, states that the v0.19.1 source is byte-identical, and says the reproduction needs no GPU, weights, tokenizer or network. Two independent `<tool_call>` blocks parse correctly when they arrive in one chunk or when the split falls between the calls. When a chunk holds the first call's closing tags plus the opening of the second, the same concatenated text produces malformed JSON and can truncate a string value. The reporter adds that #45003 removed the old XML parser and #45413 introduced newer engine routing, and calls this "the legacy v0.19.0 implementation, not an asserted regression on current main." That boundary matters: reading this thread as evidence about v0.32.x is a version error.

The second report, [vllm-project/vllm#63983](https://github.com/vllm-project/vllm/issues/63983), is a different failure and a different scope. Against **main at commit 5d35ce3**, with parser code only and no GPU, the `functiongemma` parser extracts arguments written as `key:<escape>value<escape>`. FunctionGemma's own chat template wraps only strings that way; numbers, booleans, arrays and objects are emitted bare, never match the parser's regex, and are silently dropped. The issue's printed output makes the consequence concrete: a `set_alarm` call carrying `hour:7`, `enabled:true`, `days:[mon,tue]` and `snooze:{minutes:5}` comes back as `{"label": "Wake up"}`. The call "succeeds" with four of its five arguments missing.

The third, [vllm-project/vllm#63941](https://github.com/vllm-project/vllm/issues/63941), concerns Kimi K3 at **main commit cd9aa5b5ee** (2026-10-26), also parser-level and CPU-only. When a generation is cut inside an XTML control marker by `max_tokens`, the non-streaming path returns the raw partial marker text as user-visible `content`, while the streaming path withholds the same fragment. The two paths disagree about the same tokens. The reporter notes that current main tip `6fe3d447ac` does not touch `kimi_k3_tool_parser.py`.

| Report | Version scope | Symptom | What the report does not show |
| --- | --- | --- | --- |
| #64012 | v0.19.0 legacy `qwen3_xml` | Merged/truncated arguments when a chunk straddles two calls | Any regression on current releases; v0.19.1 was never executed |
| #63983 | main @ 5d35ce3, `functiongemma` | Non-string arguments silently dropped | Chunk-boundary behaviour; other parser families |
| #63941 | main @ cd9aa5b5ee, Kimi K3 | Non-streaming leaks a partial XTML marker that streaming withholds | That the leak affects schema-valid calls or other parsers |

Read together, the three reports support a failure class, not one release-wide defect: chunk-boundary merge and truncation in a legacy parser, silent argument loss in one current parser, and stream/non-stream divergence in another. No single tag is shown to carry all three symptoms, and none of the reports is a measurement of your deployment. The adjacent [Ubicloud write-up](https://www.ubicloud.com/blog/fixing-tool-call-accuracy-in-vllm) is often cited alongside them and should not be: it measured schema accuracy, not chunk boundaries. It reports 92% schema accuracy serving Kimi K2.6 on vLLM 0.28 against the 2,000-request K2VV ToolCall workload, 100% after constrained decoding was enabled as a vLLM 0.31 server flag, and a drop to 91% when a later release changed the default. That is a constrained-decoding story about argument *validity*, and it is useful context for why strictness flags exist. It is not evidence that streaming splits corrupt calls.

## The flag semantics that matter, pinned to v0.32.0

The current stable release on 2026-10-28 is v0.32.0 (published 2026-10-18), followed by v0.31.0 and v0.30.0, according to the [release list](https://api.github.com/repos/vllm-project/vllm/releases?per_page=6). The [tool-calling documentation pinned to that tag](https://docs.vllm.ai/en/v0.32.0/features/tool_calling.html) defines the startup flags plainly: `--enable-auto-tool-choice` is mandatory for automatic tool choice, `--tool-call-parser` selects the parser, `--tool-parser-plugin` optionally registers a custom one, and `--chat-template` is optional. It also states the division of labour that this article is about: "Remember that it's the caller's responsibility to ... Handle the tool calls in your application logic." The server flags choose and drive a parser; they do not certify the arguments your application is about to execute.

The same page documents the strictness behaviour that changed the risk picture in this release line. Structural tags constrain the tool-call envelope (markup and function name) always for `tool_choice="required"` and named calls, and for `tool_choice="auto"` only once a tool sets `strict: true` or the server raises the floor. Argument schemas are pinned only for tools marked `strict: true`, or under `--tool-strict-level parameter`. The `--tool-strict-level` values are `auto` (default, follow the request), `function` (constrain envelope for every request with tools), and `parameter` (pin every tool's argument schema). `VLLM_ENFORCE_STRICT_TOOL_CALLING` defaults to true and, when false, disables structural tags entirely. The page names the reason a gate is still needed: with `tool_choice="auto"` and no strict tools, "the model generates tool calls without any grammar and malformed markup can leak into the response."

Parser coverage is version-specific too. The v0.32.0 page lists FunctionGemma under `functiongemma` and Kimi-K2 under `kimi_k2`; the string `kimi_k3` does not appear on that page at all. So the Kimi K3 defect in #63941 is a main-branch parser report, not a documented v0.32.0 parser you can select by reading this page.

## Localize the fault before you patch anything

Three checks separate a server parser defect from a client reassembly defect, and they take minutes rather than a GPU rental.

First, capture the stream verbatim. `curl -N --no-buffer` with your normal request body, redirected to a file, preserves event framing, `data:` lines and chunk order. Second, replay that capture through the exact buffering code your agent uses, splitting the captured bytes at every offset. A client that decodes each TCP read independently will fail inside multi-byte characters; a client that trims whitespace or re-serialises `arguments` will fail on types. Third, send the same prompt non-streaming and compare the resulting calls. If the raw deltas concatenate to valid JSON and the non-streaming call matches, the fault is client-side reassembly. If the raw deltas themselves are invalid or short, the fault is upstream of your client. If both parse but disagree on types or call count, suspect the parser or the model's chat template rather than transport.

The gate published with this article includes that boundary replay as a selftest. It builds a five-event stream carrying two parallel calls, serialises it as OpenAI SSE frames, and re-runs reassembly plus validation at all 760 byte offsets. All 760 splits reassembled without a false rejection, which is the property you want before you trust a gate to tell you that a real corruption is real. That number comes from the run record in this article's evidence directory; it is a fixture check, not a vLLM measurement.

## A gate that runs before dispatch

The gate is deliberately boring: reassemble the stream the way the OpenAI-compatible client does, parse each `arguments` string as JSON, then compare the parsed object with the schema the model was given. It fails closed on five conditions - unparseable JSON, non-object arguments, missing required fields, a JSON type that does not match the declaration, and a call count that differs from what the request expected. Types are compared exactly, because Python's `bool` is a subclass of `int` and because accepting `"3"` where `integer` was declared is precisely the silent retyping a coercing client can produce.

```python
def validate(calls, tools, expected_calls):
    issues = []
    if expected_calls is not None and len(calls) != expected_calls:
        issues.append(("CALL_COUNT_MISMATCH", f"{len(calls)} of {expected_calls}"))
    for call in calls:
        spec = tools.get(call["name"])
        try:
            args = json.loads(call["arguments"])
        except ValueError:
            issues.append(("ARGUMENTS_NOT_JSON", call["name"])); continue
        for name in spec.get("required", []):
            if name not in args:
                issues.append(("MISSING_REQUIRED", name))
        for name, value in args.items():
            declared = spec["properties"].get(name, {}).get("type")
            if declared and type_name(value) not in declared:
                issues.append(("TYPE_MISMATCH", f"{name}={value!r}"))
    return issues
```

Call it on the assembled message, before any tool dispatcher or agent loop sees it. On a rejection, log the raw `arguments` string and the `finish_reason`, return the errors to the model as a tool result if your loop supports that, and retry. Do not coerce values to make the call pass: coercion converts a detected type error into an undetected wrong argument, which is the failure this gate exists to prevent.

The published selftest exercises four constructed corruptions derived from the clean fixture, and each is caught by a distinct code rather than by a generic exception:

| Constructed corruption | Detected as | Calls reassembled |
| --- | --- | --- |
| Two calls merged into one delta | `ARGUMENTS_NOT_JSON` + `CALL_COUNT_MISMATCH` | 1 of 2 |
| Arguments cut mid-string | `ARGUMENTS_NOT_JSON` | 2 |
| Integer, boolean, array re-encoded as strings | `TYPE_MISMATCH` | 2 |
| Non-string arguments dropped | `MISSING_REQUIRED` | 2 |

Two limits follow from the design. A merged call cannot be reconstructed, only rejected, so the correct recovery is a retry with the error surfaced, not a repair heuristic. And a schema-valid but semantically wrong argument - the failure class Ubicloud measured - passes the gate by definition; strict decoding and a stronger schema are the tools for that, not this check.

## What is verified, what is not

Everything about the three reports above was re-read from the GitHub API on 2026-10-28 between 12:01:39 and 12:01:43 UTC, the window recorded in the research fetch log for this article, and the pinned documentation and release list were fetched inside that same window. The gate and its fixtures were executed in the same session, and the run record captures the command, exit code, stdout and input hashes. What was not done matters just as much: vLLM is not installed in this workspace image, so no parser was imported and no claim is made that any listed defect reproduces at v0.32.0. The reports' own commits and version labels are quoted as the reporters stated them. There is no throughput, latency, cost or accuracy measurement here, and no claim that all vLLM parsers are affected - the matrix is one legacy parser, one current parser family and one current stream/non-stream divergence.

If you operate a vLLM endpoint for an agent, the operational order is: pin the tag you actually run, capture one streaming and one non-streaming response with parallel calls, replay the capture at every byte boundary through your client, and enable the gate before the next deploy. If the corruption survives that sequence at a pinned tag, you have a reproducible parser report to file rather than an intermittent symptom to describe.

## Sources

Primary sources, all re-fetched on 2026-10-28 UTC:

- #64012, legacy qwen3_xml chunk-boundary report - https://github.com/vllm-project/vllm/issues/64012
- #63983, FunctionGemma non-string argument drop - https://github.com/vllm-project/vllm/issues/63983
- #63941, Kimi K3 stream/non-stream marker leak - https://github.com/vllm-project/vllm/issues/63941
- Published releases and dates (v0.32.0 latest stable in this window) - https://api.github.com/repos/vllm-project/vllm/releases?per_page=6
- Tool-calling flags, strict mode and `--tool-strict-level`, pinned to v0.32.0 - https://docs.vllm.ai/en/v0.32.0/features/tool_calling.html
- Adjacent schema-accuracy measurement (different failure class; not chunk boundaries) - https://www.ubicloud.com/blog/fixing-tool-call-accuracy-in-vllm

First-party artifacts published with this article (constructed fixtures, no model output; local fixture check, not vendor measurement):

- Gate and boundary selftest - https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/vllm-streaming-tool-call-parser-corruption-2026/toolcall_gate.py
- Parallel-call SSE fixture - https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/vllm-streaming-tool-call-parser-corruption-2026/fixtures/sse_parallel_toolcalls.json
- Declared tool schema used by the gate - https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/vllm-streaming-tool-call-parser-corruption-2026/fixtures/tool_schema.json
- Run record: command, exit code, stdout, input hashes - https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/vllm-streaming-tool-call-parser-corruption-2026/first-party-fixture-run-2026-10-28.json

For the argument shapes a parser is supposed to produce, see [LLM function calling and tool use](https://baeseokjae.github.io/posts/llm-function-calling-tool-use-guide-2026/); for why this serving stack was chosen before parsing became the concern, see [vLLM vs Ollama in production](https://baeseokjae.github.io/posts/vllm-vs-ollama-production-2026/) and [local model serving frameworks compared](https://baeseokjae.github.io/posts/local-ai-model-serving-frameworks-2026/).
