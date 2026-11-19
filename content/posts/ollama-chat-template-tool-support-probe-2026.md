---
title: "The Chat Template or a Built-in Parser Decides Whether Ollama Gives You a Tool Call"
date: 2026-11-02T06:20:00+00:00
lastmod: 2026-11-19T09:28:00+00:00
tags:
  - ollama does not support tools
  - ollama chat template
  - .Tools jinja template
  - ollama tool calling probe
  - ollama modelfile template
  - qwen2.5 tool call
  - local llm function calling
  - ollama 0.20.3
  - local agent debugging
  - prompt_eval_count tool schema
description: "Ollama 0.20.3 returned a read_file call with .Tools in the chat template and HTTP 400 \"does not support tools\" without it — unless a built-in parser grants tools. The check, the probe and the fix."
draft: false
schema: "schema-ollama-chat-template-tool-support-probe-2026"
---

You pass a `tools` array to `/api/chat`, the call fails, and nothing in the response explains why. On ollama 0.20.3 the failure is a bare HTTP 400 whose message is `registry.ollama.ai/library/<model>:latest does not support tools`, which names the model and points at the wrong layer. On a server old enough to have no `tools` field in its chat request at all — `v0.2.0` and earlier — that JSON key is dropped unread, so the same call returns HTTP 200 with a prose answer and no `tool_calls` field, and the client reports "the model ignored the schema".

The direct answer, measured on one host and readable in the pinned source: **on a build that configures no built-in tool parser**, whether it can emit a tool call is decided by its chat TEMPLATE, not by the model name, family or parameter count. A template that references `.Tools` declares the variable `tools`, the server grants the build the tools capability, and the tool schemas get rendered into the prompt. Remove that block and keep the identical weights in the identical blob, and the server refuses the request before the model ever runs.

The qualifier is not decoration. The same function in v0.20.3 grants the tools capability on either of two branches — `slices.Contains(v, "tools") || (builtinParser != nil && builtinParser.HasToolSupport())` — and `builtinParser` is resolved from `m.Config.Parser`. At that tag five built-in parsers (`cogito`, `gemma4`, `deepseek3`, `lfm2`, `ministral`) return `true` from `HasToolSupport()`, so a build whose Modelfile selects one of them has tools with no `.Tools` variable anywhere in its template. The build tested here selects none of them: its template-stripped derivative was refused, which shows the capability came from the template and from nothing else. Every measurement below therefore describes template-branch builds only. The probe does not speak for parser-configured builds, and no such build was run here.

## Thirty-second check, before you change model

Two commands answer the yes/no question for any local build:

```
ollama show --modelfile qwen2.5:0.5b | sed -n '/TEMPLATE """/,/"""/p' | grep -c '\.Tools'
ollama show qwen2.5:0.5b | sed -n '/Capabilities/,+3p'
```

The first prints a non-zero count for a build whose template contains a `.Tools` block. The second prints the capability list the server has derived — the list it later checks a tools request against. Read them in that order. A count of 0 with no `tools` in the list means no prompt engineering will help: the request will be refused or the schema will never be rendered. A count of 0 with `tools` in the list means a built-in parser is supplying the capability rather than the template, so the count tells you nothing about whether tools work; only a request does. `ollama show --modelfile` is where you look for the parser the build selected.

Reading the flag is necessary, not sufficient. A build flagged `tools` can still answer in prose if the weights are weak, if the schema is malformed, or if the client sends `stream: true` and the parser drops the call. The flag tells you the layer is capable; only a request tells you whether a call comes out.

## The three builds and their rows

One host, CPU only, 2 vCPU, 11 GB RAM, `ollama version is 0.20.3`, model `qwen2.5:0.5b` (digest `a8b0c5157701`, 397 MB, Q4_K_M, already resident). The two derivatives were built `FROM qwen2.5:0.5b` with the same SYSTEM line; `probe-notools:latest` deletes only the `{{- if .Tools }}...{{- end }}` conditional and the `or .Tools` clause in the message wrapper, and `probe-faketools:latest` re-adds the literal word "tools" as one prose sentence, with no `.Tools` reference.

| Build | `.Tools` in TEMPLATE | Tools sent | HTTP | Response class | prompt_eval_count |
|---|---|---|---|---|---|
| qwen2.5:0.5b | yes | yes, 2 runs | 200 | `tool_calls`: one `read_file` | 180 |
| qwen2.5:0.5b | yes | no, 2 runs | 200 | prose, no call | 51 |
| probe-notools:latest | no | yes, 2 runs | 400 | refused before generation | not returned |
| probe-notools:latest | no | no, 2 runs | 200 | prose, no call | 52 |
| probe-faketools:latest | no (prose "tools" only) | yes, 2 runs | 400 | refused before generation | not returned |

Every tools-carrying request against a build without the block came back 400, twice out of twice, with `does not support tools` in the error. The same request against the parent build produced a `read_file` call both times, with `message.content` empty and `prompt_eval_count: 180`.

## What the token count proves

Without a tools array, the identical messages and options produced `prompt_eval_count: 51`. With the one-tool schema they produced `180`. The delta is the receipt that the schema text actually entered the prompt instead of being accepted by the API and quietly discarded. That is the cheap field to read when a client says "the model ignores my tools": if `prompt_eval_count` is unchanged with and without the array, the schema never reached the model, and the fault is above the weights.

`prompt_eval_count` is a token count, not a diff of the rendered text, so it shows extra input was rendered, not that the schema was rendered well. The extracted template for the parent build is published with this post (linked under Reproduction), so you can confirm the exact strings yourself instead of inferring them from a count.

## The probe you can rerun

The measured runs used a stdlib-only script that extracts the template, builds the derivative, posts the same payload to `/api/chat` and classifies the answer. The essential loop is small enough to paste into a file:

```python
import json, urllib.request
payload = {"model": "qwen2.5:0.5b", "stream": False,
           "messages": [{"role": "user", "content": "Read /etc/hostname with the read_file tool."}],
           "options": {"temperature": 0, "seed": 7, "num_predict": 128},
           "tools": [{"type": "function", "function": {
               "name": "read_file", "description": "Read a file from disk.",
               "parameters": {"type": "object", "required": ["path"],
                              "properties": {"path": {"type": "string"}}}}}]}
req = urllib.request.Request("http://127.0.0.1:11434/api/chat",
                             data=json.dumps(payload).encode(),
                             headers={"Content-Type": "application/json"})
try:
    body = urllib.request.urlopen(req, timeout=120).read()
    d = json.loads(body); msg = d.get("message", {})
    cls = "tool_calls" if msg.get("tool_calls") else "prose_no_call"
    print(cls, d.get("prompt_eval_count"), msg.get("content", "")[:120])
except urllib.error.HTTPError as e:
    print("refused", e.code, e.read().decode()[:200])
```

Run it twice, then rerun it without the `tools` key and compare `prompt_eval_count`. Repeat after every re-pull, re-quant or `ollama create`, because the digest and the template can change together.

## Which layer is at fault

| Symptom | Layer | Check | Fix |
|---|---|---|---|
| 400 `does not support tools` | template / capability gate | `ollama show --modelfile <model>` has no `.Tools` block | add a `.Tools` block to the Modelfile, `ollama create` a new tag |
| 200, prose, `prompt_eval_count` unchanged without/with tools | template | same as above | same as above |
| 200, prose, `prompt_eval_count` higher with tools | model or prompt | schema reached the prompt | strengthen the instruction, check the model actually learned the format |
| 200, `tool_calls` present in raw JSON, absent in your client | client parser | curl the endpoint directly | fix the streaming/JSON parser, not the model |

The last row is the reason to always test with a direct HTTP call before blaming the model: a framework that parses only `content` will report "no tool call" for a perfectly good response.

If the call does come out and the trouble starts on the next turn — the assistant turn comes back with empty `content`, no `tool_calls` and an `eval_count` above zero, or an argument is returned retyped — you are past this layer; that failure is diagnosed in [the history-rewriting write-up](https://baeseokjae.github.io/posts/ollama-tool-call-history-corruption-2026/). If instead the open question is terminology — what a tool schema, a `tool_calls` message and a tool result are, and where each one sits in the request — start with [the function-calling and tool-use guide](https://baeseokjae.github.io/posts/llm-function-calling-tool-use-guide-2026/), which maps each provider's call and result pair and shows how to keep that pair intact.

## What the pinned source says

In `v0.20.3` the capability list is computed from the template and from the configured parser, not from the model name. The server warns if the template does not parse, then appends the tools capability when **either** the template's declared variables contain `tools` **or** the parser named by `m.Config.Parser` reports tool support — [server/images.go at v0.20.3](https://raw.githubusercontent.com/ollama/ollama/v0.20.3/server/images.go):

```go
builtinParser := parsers.ParserForName(m.Config.Parser)
// Check for tools capability
v, err := m.Template.Vars()
if err != nil {
    slog.Warn("model template contains errors", "error", err)
}
if slices.Contains(v, "tools") || (builtinParser != nil && builtinParser.HasToolSupport()) {
    capabilities = append(capabilities, model.CapabilityTools)
}
```

`Vars()` returns the identifiers the template actually references, lower-cased and de-duplicated — [template/template.go on main](https://raw.githubusercontent.com/ollama/ollama/main/template/template.go) walks the parsed root nodes and collects identifiers, which is why a sentence containing the word "tools" contributes nothing: prose is not an identifier. That is the first branch, and it matches the measured control: `probe-faketools:latest`, which configures no parser, was refused in both runs.

The second branch is read from source here, not measured. `parsers.ParserForName(m.Config.Parser)` resolves whatever parser the build selected, and at v0.20.3 `HasToolSupport()` returns `true` in [model/parsers/cogito.go](https://raw.githubusercontent.com/ollama/ollama/v0.20.3/model/parsers/cogito.go), [gemma4.go](https://raw.githubusercontent.com/ollama/ollama/v0.20.3/model/parsers/gemma4.go), [deepseek3.go](https://raw.githubusercontent.com/ollama/ollama/v0.20.3/model/parsers/deepseek3.go), [lfm2.go](https://raw.githubusercontent.com/ollama/ollama/v0.20.3/model/parsers/lfm2.go) and [ministral.go](https://raw.githubusercontent.com/ollama/ollama/v0.20.3/model/parsers/ministral.go). A build that selects one of those gets `tools` in its capability list with no `.Tools` in its template, so a probe that only inspects the template would classify it as incapable when the server accepts its tools requests. The fetched excerpts and their file hashes are in the [parser-branch excerpt](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/ollama-chat-template-tool-support-probe-2026/upstream-parser-tool-support-v0.20.3.txt) published with this post.

The chat handler takes the other half of the decision. It appends the tools capability to the requested set whenever the request carries a non-empty `tools` array, then asks the scheduler for a runner with that set — [server/routes.go at v0.20.3](https://raw.githubusercontent.com/ollama/ollama/v0.20.3/server/routes.go):

```go
caps := []model.Capability{model.CapabilityCompletion}
if len(req.Tools) > 0 {
    caps = append(caps, model.CapabilityTools)
}
```

So the API always accepts the field and always asks for the capability; the refusal happens when the build's own capability list cannot satisfy it. The message itself is assembled in the same file as the check: `CheckCapabilities` joins a sentinel `does not support` with `tools` into one error, which is how a template property ends up reported as a model property. The 400 status is what the probe observed on the wire in 0.20.3; treat the exact wording as an observation of this build, not as a documented API contract.

The API documentation is not where you learn this. [docs/api.md at v0.20.3](https://raw.githubusercontent.com/ollama/ollama/v0.20.3/docs/api.md) shows a `tools` array in a `/api/chat` example and says nothing about which builds accept it, so a developer reading the docs reasonably concludes that the field is universally supported and that a model which "ignores" it is at fault.

Newer code on `main`, read on 2026-11-02 with no binary built or run here, is looser: the chat-template path grants the tools capability on a plain substring test for `tools` or `tool_call` rather than on declared variables — [server/images.go on main](https://raw.githubusercontent.com/ollama/ollama/main/server/images.go):

```go
func chatTemplateHasToolSupport(chatTemplate string) bool {
	return strings.Contains(chatTemplate, "tools") || strings.Contains(chatTemplate, "tool_call")
}
```

That is a source-level observation about newer code, not a measurement: no main-branch binary was built or run here, so nothing is claimed about whether `probe-faketools:latest` would be accepted by it. If you are on a newer build, run the probe rather than assuming either rule applies.

## Limits

Single host, CPU only, one 0.5B model and two derivative builds. Everything above is a behaviour observation — did a call happen, was the request refused — and wall times from these runs (0.1 s to 54 s, unloaded model on 2 vCPU) are logged in the run record but not claimed as latency. No GPU, no larger model and no parser-configured build were tested, so nothing here says how often a bigger flagged build produces a well-formed call, and nothing here measures the `HasToolSupport()` branch at runtime. The version where the `tools` field and the capability gate first appeared was not bisected, but the window is narrow: [api/types.go at v0.2.0](https://raw.githubusercontent.com/ollama/ollama/v0.2.0/api/types.go) has no `Tools` field in `ChatRequest` at all, while [server/routes.go at v0.2.8](https://raw.githubusercontent.com/ollama/ollama/v0.2.8/server/routes.go) already appends the tools capability when the request carries a non-empty array. On a build before that window the key is dropped by the JSON decoder and the reply is prose with HTTP 200 — read from source for this post, not measured on this host, and not offered as a claim about any particular release in between.

## Reproduction

The run record, the control run, all three Modelfiles and the extracted templates for the positive and negative cases are published with this post. These are local first-party measurements on the host described above, not vendor benchmarks or third-party downloads:

- Probe driver that produced the rows (edit the `EV` path at the top to your own evidence directory): https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/ollama-chat-template-tool-support-probe-2026/probe_tool_template.py
- Run record for the parent and `probe-notools` builds, with per-run status, response class, token counts and timestamps: https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/ollama-chat-template-tool-support-probe-2026/probe-run.json
- Control run for the prose-mention build: https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/ollama-chat-template-tool-support-probe-2026/probe-faketools.json
- Modelfile for the negative case, with only the `.Tools` conditional removed: https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/ollama-chat-template-tool-support-probe-2026/Modelfile.notools
- Extracted template of the negative derivative, with the `.Tools` block absent: https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/ollama-chat-template-tool-support-probe-2026/template-probe-notools.txt
- Full `ollama show --modelfile` dump for the parent build, the file the derivative was cut from: https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/ollama-chat-template-tool-support-probe-2026/modelfile-qwen2.5-0.5b.txt
- Extracted TEMPLATE of the parent build — the positive case behind the higher prompt token count: https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/ollama-chat-template-tool-support-probe-2026/template-qwen2.5-0.5b.txt
- Modelfile for the prose-mention control, where the word "tools" sits in a sentence and `.Tools` appears nowhere: https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/ollama-chat-template-tool-support-probe-2026/Modelfile.faketools
- Parser-branch source excerpt for v0.20.3, with the capability condition and the five `HasToolSupport()` returns plus per-file sha256: https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/ollama-chat-template-tool-support-probe-2026/upstream-parser-tool-support-v0.20.3.txt

The practical conclusion is one habit: before you debug a client, a prompt or a model choice, ask the build whether it can accept tools at all — read the capability list, then send one tools request and read `prompt_eval_count`. If neither the template nor a configured parser can grant the capability, swap the template or the parser, not the model: the weights were never the problem.
