---
title: "Ollama Structured Output vs a JSON Tool: measured tool-call loss and invented values on a local model (2026)"
date: 2026-11-10T09:00:00+00:00
tags:
  - ollama format json tool calls
  - ollama tools and format together
  - response_format overrides tools
  - ollama structured output vs tool calling
  - ollama no tool_calls done_reason stop
  - local llm json mode
  - qwen2.5 tool calling
  - ollama 0.20.3
  - agent harness schema validation
  - silent tool call suppression
description: "18 requests on Ollama 0.20.3: 3 of 3 tool calls without a constraint, 0 of 12 with one — HTTP 200, done_reason stop, schema-valid invented values in content."
draft: false
schema: "schema-ollama-structured-output-format-vs-json-tool-2026"
---

There are two documented ways to get machine-readable output from a local Ollama model, and they look interchangeable. You can constrain the reply with `format` — or `response_format` on the OpenAI-compatible endpoint — so the decoder emits JSON that matches a schema. Or you can register a tool and let the model call it, with the tool's result being the JSON you wanted.

The practical failure comes from doing both at once, which is a natural thing to do: keep the tools registered, and add `format` when a structured summary is due. On a self-hosted server the constraint wins and the tool call disappears. Nothing reports an error. The response is HTTP 200, `done_reason` is `stop`, `tool_calls` is absent, and `content` holds a schema-valid object in which the model has invented the values the tool was supposed to fetch.

This article measures that on one host and turns it into a decision plus a startup check you can run. It is not a discovery: the behaviour is filed upstream as [issue #18944](https://github.com/ollama/ollama/issues/18944) and [issue #13750](https://github.com/ollama/ollama/issues/13750), both open at the time of writing, and both are cited below. What those threads do not contain is a per-configuration count, so that is what this page adds.

## The short answer

If your harness needs a tool result, do not put a JSON constraint on the same request. Send one request with `tools` and no `format`, let the model call, execute the tool, append the result, and only then ask for JSON in a second request that carries `format` and no `tools`.

If your harness needs a JSON object and no tool is involved, `format` alone is fine and does what the documentation says. The 3 control requests in this probe confirmed that path produces schema-valid content on the same model.

The dangerous configuration is the combination. Measured here, 12 requests that carried both a tool array and a JSON constraint returned 0 tool calls, 18 out of 18 requests in the whole matrix returned HTTP 200, and no response signalled the difference between "the model decided not to call" and "the server never let it call".

## What the documentation says, and what it does not say

The `/api/chat` reference lists `format` and `tools` as separate optional fields with no stated interaction. `format` is described as: "Format to return a response in. Can be `json` or a JSON schema". `tools` is described as: "Optional list of function tools the model may call during the chat". Both descriptions live in the request schema on [the /api/chat page](https://docs.ollama.com/api/chat), and neither mentions the other.

The same separation appears on the OpenAI-compatibility side. That page ticks `Tools`, `JSON mode` and `response_format` as supported, in two separate checklists — `Supported features` carries JSON mode and Tools, `Supported request fields` carries `response_format` — with no precedence rule anywhere on [the OpenAI-compatibility page](https://docs.ollama.com/api/openai-compatibility).

The structured-outputs guidance is about the constraint alone: structured outputs "let you enforce a JSON schema on model responses so you can reliably extract structured data, describe images, or keep every reply consistent", per [the structured-outputs capability page](https://docs.ollama.com/capabilities/structured-outputs). It also carries a note that "Ollama's cloud currently does not support structured outputs", which matters later when comparing against the cloud-vs-self-hosted report in #13750.

An absent precedence rule is an absent rule, not evidence that the fields are independent. That distinction is the whole reason this page reports counts instead of quoting the docs.

## Method: 18 requests, six configurations, one small model

Everything below was measured on one host. The server reported `{"version":"0.20.3"}` from `/api/version`, and the model was `qwen2.5:0.5b`, already installed. The machine had 2 CPU cores and about 11.9 GB of RAM, with no GPU in use. Sampling was `temperature: 0, seed: 7`, `stream: false`, and a single user message.

The prompt was chosen so that a fabricated answer is detectable by construction: "What is the current temperature in Lisbon right now? You must use the get_weather tool to find out." The live temperature exists only behind the tool, so any numeric temperature in `content` next to zero `tool_calls` is invented, not retrieved. The probe never executed the tool, which is deliberate: the question is not what the tool returns, it is whether the model reaches the tool path at all.

The registered tool had one required argument:

```json
{"type": "function",
 "function": {"name": "get_weather",
              "description": "Get the current air temperature for a city from the weather service.",
              "parameters": {"type": "object",
                             "properties": {"city": {"type": "string"}},
                             "required": ["city"]}}}
```

Six configurations, three repetitions each, 18 requests total:

| id | endpoint | extra fields |
|----|----------|--------------|
| a | `/api/chat` | `tools` only |
| b | `/api/chat` | `tools` + `format` = 2-field schema `{city, temperature_c}` |
| c | `/api/chat` | `tools` + `format` = enum-only schema `{decision: use_tool\|answer_directly}` |
| d | `/api/chat` | `tools` + `format` = `"json"` |
| e | `/api/chat` | `format` = 2-field schema, no `tools` (control) |
| f | `/v1/chat/completions` | `tools` + `response_format` json_schema (same schema as b) |

The exact request body for cell b, which is the one most readers will recognise from their own code:

```json
{"model": "qwen2.5:0.5b",
 "messages": [{"role": "user",
               "content": "What is the current temperature in Lisbon right now? You must use the get_weather tool to find out."}],
 "stream": false,
 "options": {"temperature": 0, "seed": 7},
 "tools": [ ... get_weather ... ],
 "format": {"type": "object",
            "properties": {"city": {"type": "string"}, "temperature_c": {"type": "number"}},
            "required": ["city", "temperature_c"]}}
```

Per request the run recorded the endpoint, configuration, model, repetition, HTTP status, `done_reason` or `finish_reason`, `n_calls`, the called function and its arguments, `content` length and text, whether `content` parsed as JSON, whether it validated against the required keys, `eval_count`, wall seconds, and a fabrication flag (zero calls plus a temperature-shaped value). The rows are appended to an append-only NDJSON log, [results.jsonl](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/ollama-structured-output-format-vs-json-tool-2026/results.jsonl), which is published with this article alongside the harness; every count in the tables below is a field of that file.

## Result: 3 of 3 calls without a constraint, 0 of 12 with one

| id | configuration | n | HTTP 200 | tool calls | done_reason | content parses as JSON | satisfies the schema it was sent | fabricated value | mean wall s (load-contaminated) |
|----|---------------|---|----------|------------|-------------|------------------------|----------------------------------|------------------|-----------------------------------|
| a | tools only | 3 | 3 | **3** | stop | n/a (no content) | n/a | 0 | 7.61 |
| b | tools + 2-field schema | 3 | 3 | **0** | stop | 3 | 3 (two-field) | 3 | 2.66 |
| c | tools + enum schema | 3 | 3 | **0** | stop | 3 | 3 (enum) | 0 | 1.83 |
| d | tools + `format: json` | 3 | 3 | **0** | stop | 3 | n/a (no schema sent) | 0 | 3.23 |
| e | schema, no tools | 3 | 3 | 0 | stop | 3 | 3 (two-field) | 3 | 7.38 |
| f | `/v1` tools + `response_format` | 3 | 3 | **0** | stop | 3 | 3 (two-field) | 3 | 4.87 |

The two validity columns are separate on purpose. A per-row validator in the harness scores every reply against the two-field `{city, temperature_c}` reference schema, so the log records `false` with reason `missing:city,temperature_c` for cells c and d — that number says the reply did not match a reference schema those requests were never given, not that the reply was malformed. Scored against what each request actually carried, cell c's `{"decision": "use_tool"}` satisfies the enum schema, and cell d was sent the bare string `"json"`, which carries no schema to satisfy at all. The `mean wall s` column is labelled with its defect rather than removed: those means mix a 15.67 s cold start with warm calls of 2-5 s, so they are wall times, not a comparison of the two paths (see the latency note below).

Read the tool-call column against the configuration column. Without a constraint, every request produced a `get_weather` call with `{"city": "Lisbon"}` and an empty `content`. With any JSON constraint — a two-field schema, an enum-only schema, the bare string `"json"`, or the OpenAI-compatible `response_format` — no request produced a call. Nine of those twelve were on `/api/chat` and three on `/v1/chat/completions`; the count is 0 in both groups.

Cell e is the important control. With no tool in the request at all, the same model under the same schema returned the same fabricated object as cell b. That is expected — there was nothing to call — and it establishes that the constrained path is the "answer directly" path by construction. Adding `tools` to that configuration did not reopen the tool path: b and e behaved identically apart from token counts.

`eval_count` separates the two cases at the wire level: 22 completion tokens for a tool-call turn without a constraint, 17 for the constrained two-field reply, 10 for the enum reply, 19 for the `format: json` reply. The model was generating either way; only the destination changed.

## What the model produced instead

Three different shapes appeared in `content`, and each one defeats a different kind of check.

**A schema-valid invention.** Cell b returned `{"city": "Lisbon", "temperature_c": 10}` in all three repetitions, byte-identical. It parses, it validates, and the temperature is made up. Any harness that asserts "the final object matches the schema" passes. This is the shape that ends up in a spreadsheet.

**A pseudo-call in prose.** Cell d returned `{"name": "get_weather", "arguments": {"city": "Lisbon"}}` three times. The model's intent survived intact; the server routed it into `content` as data instead of into `tool_calls`. A harness that greps `content` for a function name might even "work" here by accident, and a harness that expects `tool_calls` silently gets nothing.

**A decision object that says the right thing and does nothing.** The enum schema in cell c returned `{"decision": "use_tool"}` in all three runs. The model wanted to call the tool, said so, and the constraint left it no way to express that as a call. The schema was satisfied; the request was not.

Cell f adds a detail worth noting for anyone comparing endpoints. On `/v1/chat/completions` the fabricated temperatures were 14.5, 17 and 18.2 — three different invented values under `temperature: 0` and `seed: 7`, where the native endpoint returned the same byte string three times. Reproducibility settings are not carried identically across the two surfaces, so a determinism argument built on one endpoint does not transfer to the other.

## Prior art: the behaviour is filed upstream

[Issue #18944](https://github.com/ollama/ollama/issues/18944), opened 2026-10-11 and open at the time of writing, reports it for `qwen3.5:9b` on `/api/chat`: "When using the /api/chat endpoint and the format is set to json, then the model is unable to use any tool calls. It might either try to use the tool call in the response or it will make something up in the response." Both observed shapes in this probe — pseudo-call in `content`, invented values — are named in that report.

The thread also documents the reasoning, and the correction to it. A maintainer first replied that "a tool call does not confirm to a JSON schema, so the model can't generate the tool call". The reporter then noted that tools worked with a JSON format until roughly version 0.32, and the maintainer agreed that his first comment reflected older versions: it worked for thinking models up to 0.34.3, and the behaviour changed in 0.34.4 with a linked pull request, #18479. Those version numbers come from the thread; nothing on this host can confirm them, and the server measured here reports 0.20.3 while still reproducing the failure. No regression boundary is asserted anywhere in this article.

[Issue #13750](https://github.com/ollama/ollama/issues/13750), opened 2026-01-16 and open at the time of writing, states the precedence directly: "When both tools and response_format are present in the request, response_format takes complete priority over tools. The model is forced to generate a hallucinated JSON response conforming to the schema without ever considering tool calls." The reporter also reports that the same request works on Ollama.com, which conflicts with the current documentation note that the cloud does not support structured outputs. Both statements are recorded here as reported; they are not reconciled into a claim.

None of the comments in either thread reports a per-configuration call count, which is the gap this page fills. It is also why the article is framed as a measured decision and a detection rule, not as a bug discovery.

## The detection rule a harness should run

`finish_reason` cannot distinguish a suppressed call from a legitimate one. Neither can schema validation: cell b passed it while inventing the number. The failure is visible only in the relationship between the request's shape and the response's shape, which means detection belongs at the configuration level, not per response.

The cheap version is a startup canary: send the same deterministic request twice, once with `tools` only and once with `tools` plus `format`, and compare the call counts. If the unconstrained request calls and the constrained one never does, the server has this behaviour and every "tools + format" code path in the harness is dead.

```python
def canary(base, model, tool, schema, prompt):
    def ask(extra):
        body = {"model": model, "stream": False,
                "messages": [{"role": "user", "content": prompt}],
                "options": {"temperature": 0, "seed": 7},
                "tools": [tool], **extra}
        req = urllib.request.Request(base + "/api/chat",
                                     data=json.dumps(body).encode(),
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=120) as r:
            d = json.loads(r.read())
        return len((d.get("message") or {}).get("tool_calls") or []), d

    bare = ask({})[0]
    constrained, resp = ask({"format": schema})
    if bare and not constrained:
        raise RuntimeError(
            "tools+format suppresses tool calls on this server: bare=%d constrained=%d "
            "done_reason=%r content=%r" % (
                bare, constrained, resp.get("done_reason"),
                ((resp.get("message") or {}).get("content") or "")[:120]))
```

The canary costs two requests and fails at boot instead of six weeks later in a spreadsheet. Keep it alongside your version check: the behaviour is version- and model-scoped, so a server upgrade or a model swap is exactly when it should run again.

A per-response check is possible but weaker, because "the model correctly decided not to call" is indistinguishable from "the call was suppressed" without knowing whether the prompt required the tool. If you must do it per response, make provenance explicit: require that every fact field in the final object carry the `tool_call_id` that produced it, and reject a reply whose fact fields have no tool provenance. That converts cell b from a pass into a loud failure without needing to infer intent.

## Decision table

| Your need | Configuration | Status in this probe |
|-----------|---------------|----------------------|
| Final JSON, no tool involved | `format` alone | Measured: schema-valid content in 3 of 3 (e). |
| A tool result, then more work | `tools` only on the call turn | Measured: calls in 3 of 3 (a). |
| Tool result and a JSON summary in one flow | two requests: call with `tools`, then summarise with `format` and no `tools` | Not measured here. Follows from the suppression above and is the obvious workaround, but treat it as a hypothesis until your own canary confirms it. |
| Both fields in one request | none — treat the tool as unavailable | Measured: 0 calls in 12 of 12 constrained requests; invented values in 6. |

The two-turn path is the one readers will reach for, and it is worth being blunt that this run did not execute it: no second arm, no final-output validity rate. What this run establishes is the boundary that makes the two-turn design necessary — an unconstrained call turn works, and any constraint on that same turn does not.

## Wall times: recorded, not a latency comparison

The title of this page does not claim a latency result, and this section is why. The mean wall times in the table are contaminated by model load. The first `a` request took 15.67 s while the process was loading `qwen2.5:0.5b` onto 2 CPU cores; the next two took 2.5 s and 4.7 s. With n=3 per cell, a single cold start moves the mean by seconds, and the constrained cells look faster partly because they emit fewer completion tokens (17 versus 22). Do not read those means as a comparison of the two paths. A real comparison needs a warmed model, interleaved repetitions, and many more than three samples per cell.

## Limitations

One model (`qwen2.5:0.5b`), one server version (0.20.3), one host, one prompt wording, one turn, three repetitions per cell. A 0-in-3 result is compatible with a truly zero rate and with a substantial rate, so the claim is "no call in 12 constrained requests on this configuration", not "this never happens anywhere". The upstream reports show the same shape on `qwen3.5:9b` and on 0.14.1 and 0.16.1, which is why the behaviour looks server-side rather than model-specific, but no larger model was run here.

The tool was never executed, so no real temperature exists to compare the invented one against; fabrication is established by the question being unanswerable without the tool, not by diffing against a live reading. The exact invented number is model- and prompt-specific.

No second prompt wording was run, so the effect is shown not to depend on sampling (identical output across repetitions at `temperature: 0`) but not shown to be independent of phrasing. No two-turn loop was measured.

## How to reproduce it

The harness behind the table is a single stdlib-only Python file: one `urllib` POST per request, an NDJSON append per response, and a wall-clock budget that stops the run and keeps partial rows. It is published with the run record, along with a test that exercises it without a model:

| file | what it is |
|------|------------|
| [probe.py](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/ollama-structured-output-format-vs-json-tool-2026/probe.py) | the matrix harness: six configurations, both endpoints, `PROBE_MODELS` / `PROBE_REPS` / `PROBE_DEADLINE_S` from the environment |
| [results.jsonl](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/ollama-structured-output-format-vs-json-tool-2026/results.jsonl) | the 18 rows behind the table, one JSON object per request |
| [summary.json](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/ollama-structured-output-format-vs-json-tool-2026/summary.json) | per-configuration counts and means, derived from those rows |
| [run_meta.json](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/ollama-structured-output-format-vs-json-tool-2026/run_meta.json) | model, repetitions, deadline and the host server version reported at run time |
| [fixture_test.py](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/ollama-structured-output-format-vs-json-tool-2026/fixture_test.py) | stdlib mock server that replays one tool-calling and one constrained reply, then runs the harness against it |
| [fixture_output.txt](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/ollama-structured-output-format-vs-json-tool-2026/fixture_output.txt) | the recorded output of that test: 14 assertions, 0 failed |

```
PROBE_MODELS=qwen2.5:0.5b PROBE_REPS=3 PROBE_DEADLINE_S=140 \
  python3 probe.py
```

Keep the two kinds of check apart, because they establish different things. The fixture test proves the harness mechanics — that the request bodies are shaped as described, that each response becomes one NDJSON row with the recorded fields, that the validator scores a reply against the two-field reference schema, and that the canary below raises when a call is suppressed. It runs against a mock server on `127.0.0.1` with a fixed replay rule and no model, so it is not evidence about any Ollama build and says nothing about tool-call rates. The table is the live part: 18 requests against Ollama 0.20.3 with `qwen2.5:0.5b` on 2026-11-10, and only that run is evidence about the server.

To repeat the live run, point the harness at a server on `127.0.0.1:11434`, or change one constant for a remote host. A fresh run either reproduces the table or shows that the installed version no longer behaves this way — which is the result worth having either way, since the upstream thread's own version attribution is unresolved.

If you arrived here from a build guide, the surrounding pieces are in [the local agents guide](/posts/local-ai-agents-guide-2026/), the two-path overview is in [the function-calling guide](/posts/llm-function-calling-tool-use-guide-2026/), the library-level decision this page does not repeat is in [the structured-output guide](/posts/llm-structured-output-guide-2026/), and the endpoint reference is [the Ollama API integration guide](/posts/ollama-api-local-llm-integration-developer-guide-2026/).

Two neighbouring silent failures are worth telling apart from this one. A tool call can also vanish through conversation-history replay, with a different signature: empty `content`, no `tool_calls`, non-zero `eval_count`, covered in [the history-corruption write-up](/posts/ollama-tool-call-history-corruption-2026/). And a prompt that overflows the context window truncates silently, which produces the same "nothing useful came back" experience from the input side, covered in [the context-truncation note](/posts/ollama-silent-context-truncation-2026/). Neither is this constraint path; the equivalent defect on a different local server, where the streaming parser corrupts calls, is in [the vLLM parser write-up](/posts/vllm-streaming-tool-call-parser-corruption-2026/).

The one-line version: a JSON constraint and a registered tool are not two ways to the same end. On a self-hosted Ollama server measured here, the constraint wins silently, the call disappears, and the object that comes back is valid, plausible, and invented.
