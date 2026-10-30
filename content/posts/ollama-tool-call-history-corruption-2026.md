---
title: "Ollama's Silent Tool-Call Failures: Conversation-History Round-Trip, Dropped Calls and Retyped Arguments"
date: 2026-10-29T00:17:00+00:00
tags:
  - ollama tool_calls empty
  - ollama done_reason stop
  - ollama tool call history
  - flint renderer integer arguments
  - gemma4 tool call parsing failed
  - qwen3 tool call dropped
  - ollama api chat troubleshooting
  - local llm agent loop
  - function calling schema validation
  - silent tool call drop
  - ollama v0.40.12
description: "Four open Ollama reports: tool calls vanish or come back retyped — empty turns with done_reason stop, an integer returned as \"30000.0\", prose-only replies."
draft: false
schema: "schema-ollama-tool-call-history-corruption-2026"
---

An agent loop calls a local Ollama server, the HTTP status is 200, the stream ends cleanly, and the assistant message contains nothing: no `content`, no `tool_calls`, `done_reason: "stop"`. The loop treats that as "the model is done" and stops. Nothing was done. No error was raised.

That is the failure this article is about. It is not one bug with one cause. Four separate, currently open reports against Ollama between versions 0.34.1 and 0.40.8 describe four different ways a tool call disappears or comes back mutated, and the source of tag v0.40.12 shows which of those paths are still present in the newest release at the time of writing.

The evidence boundary matters, so state it up front: four public issue reports written by other people, plus reads of the tagged source. No Ollama server was started for this article, so nothing here is a benchmark, and nothing here is our own reproduction. Where a number is quoted, it is the reporter's own count on their own harness, at the version they named.

## The signature to recognise before anything else

A dropped tool call and a genuinely finished turn look identical in most clients, because both are `done_reason: "stop"` with an assistant message. The distinguishing field is `eval_count`. A dropped call still generated tokens: the model wrote a call, the server failed to return it as `tool_calls`, and the tokens are counted. The reporter on `qwen3:8b` saw `eval_count` between 20 and 160 on replies whose `content` and `tool_calls` were both empty.

So the operational rule is narrow and testable: an assistant turn with empty `content`, no `tool_calls`, `done_reason` of `stop` and a non-zero `eval_count` is a server-side loss, not a completed task. A turn with `eval_count: 0` may genuinely be empty output. Most agent frameworks collapse both into "finished" and move on.

The rest of this article is the four paths that produce the first case, then the guard.

## The four paths in one table

| Path | Trigger | Wire symptom | Server signal | Reported on |
|---|---|---|---|---|
| History retyping | An integer argument from an earlier tool call is replayed through history | Next call returns the argument as the string `"30000.0"`, client schema validation rejects it, and keeps rejecting it | none | 0.40.8, `flint:40b-a2b-qat-int4` |
| Unregistered tool | Model calls a function name that is not in the request's `tools` array | `content` empty, `tool_calls` absent, `eval_count` above zero | none | 0.40.7 (also 0.40.4/0.40.5), `qwen3:8b`; 0.40.8, `qwen3:0.6b` |
| Unclosed list in arguments | gemma4 leaves the `edits` list unclosed in a tool call | Empty assistant turn, no error field | `gemma4 tool call parsing failed` | 0.40.6 (Windows/CUDA), `gemma4:e4b` |
| Preamble before the call | System prompt asks for prose, then a call | Prose only, `tool_calls: null`, `done_reason: stop` | none | 0.34.1, `qwen3.8:27b-mlx` |

Two of the four are parser or renderer defects. One is a type loss in the API decode that only becomes visible through a renderer. One is a model- and build-specific suppression that has not been shown to exist on newer versions. Treating them as a single "Ollama drops tool calls" defect would be wrong, and the scope of each is the reason the fixes are tracked as separate pull requests.

## Path 1: history replay retypes an integer

The first report ([issue #19191](https://github.com/ollama/ollama/issues/19191)) is precise enough to read as a specification. With `flint:40b-a2b-qat-int4` on Ollama 0.40.8 (`f580b54`), a request whose history contains an earlier tool call carrying `timeout_ms: 30000` returns the next call with `{"command":"pwd","timeout_ms":"30000.0"}`. Without that earlier call in history, the same model returns proper integers on nine of nine runs; with it, the wrong form appears on three of three.

Two layers produce that, and separating them matters if you are deciding what to patch.

The decode layer loses the integer type before any model sees the prompt. In [`api/types.go` at tag v0.40.12](https://github.com/ollama/ollama/blob/v0.40.12/api/types.go), `ToolCallFunctionArguments.UnmarshalJSON` rebuilds the arguments with `json.Unmarshal` into an ordered map, which decodes every JSON number as `float64`. `Message.UnmarshalJSON` wraps its alias type, so this path runs for every history message that carries tool calls. This is type loss, not value loss: `float64` holds integers exactly far beyond any plausible timeout value, but the fact that the value was an integer is gone by the time a renderer formats it.

The render layer decides whether the type loss becomes visible text. In [`model/renderers/flint_json.go` at the same tag](https://github.com/ollama/ollama/blob/v0.40.12/model/renderers/flint_json.go), `flintJSONValue` handles floats itself: it formats with `strconv.FormatFloat(..., 'g', -1, ...)`, appends `.0` whenever the result contains no `.`, `e` or `E`, and returns the string as a `json.Number`, so a `float64` of `30000` is turned into the literal `30000.0` before the shared writer sees it. [`flint.go`](https://github.com/ollama/ollama/blob/v0.40.12/model/renderers/flint.go) sends every non-string tool-call argument through that conversion on the way into `<arg_value>`, which is how `30000` becomes `<arg_value>30000.0</arg_value>` in the Flint prompt. Flint then copies the form it was shown, and returns it as a string.

That `.0` is this renderer's, not a rule of Ollama's JSON handling in general. `pythonScalar` in [`model/renderers/json.go` at the same tag](https://github.com/ollama/ollama/blob/v0.40.12/model/renderers/json.go) re-reads the marshalled value with `UseNumber` and returns a number literal that contains no `.`, `e` or `E` unchanged; only a literal that does contain one is parsed to `float64`, formatted with `'f'`, and given a trailing `.0` when that result has no dot. A raw `float64` of `30000` marshals to `30000` and comes out as `30000` there.

The downstream damage is durable rather than transient. Once a call carrying the string form is appended to history, every later call that sets the same argument is rendered from the same mutated history and fails the same validation, so an agent that survived turn two dies on turn three and stays dead for the session. The reporter's client rejected it with `invalid type: string "30000.0", expected u64`, and their shell tool could not run any command for the rest of the session.

Both halves are addressed in open pull requests, neither merged into v0.40.12: `api: preserve integer types in decoded tool call arguments` ([PR #19195](https://github.com/ollama/ollama/pull/19195)) switches the decode to preserve number representation, and `Fix tool calls rendering integer arguments as decimals` ([PR #19252](https://github.com/ollama/ollama/pull/19252)) stops the renderer from rewriting the numeric form. If your client validates argument types, check your server version against both before assuming a fix is present.

## Path 2: the call names a tool that is not in `tools`

The second path is the one that most often hides inside a working agent, because the trigger is a design pattern people adopt deliberately: a tool offered on demand, named inside another tool's description, rather than listed in the request's `tools` array.

The report is [issue #19187](https://github.com/ollama/ollama/issues/19187). On Ollama 0.40.7 with `qwen3:8b`, `/api/chat` streaming, `num_ctx` 32768, a call to such a name returned no `content` and no `tool_calls`, with `eval_count` between 20 and 160. Replaying sixteen captured requests, the reporter got that empty reply on 28 of 32 runs. Generating raw text for the same requests with the model's own template produced a well-formed `<tool_call>` to the unlisted name every time, and adding the missing names to `tools` with empty schemas restored the call on 30 of 32. The model was calling; the server was dropping the call on the way out.

An independent reporter [reproduced it on 0.40.8](https://github.com/ollama/ollama/issues/19187#issuecomment-6333800763) (Linux, CPU) with `qwen3:0.6b`, and their counts are cleaner: with the target tool absent from `tools`, eight of eight seeds returned no content and no `tool_calls` with `eval_count` 25; with it listed, eight of eight returned the call. They saw the same empty reply through `/v1/chat/completions`, with `finish_reason` `stop`, so switching endpoints does not route around it.

The mechanism proposed in [PR #19240](https://github.com/ollama/ollama/pull/19240) is that the parser buffers a tagged call for a name it does not recognise, and the content accessor returns an empty string for non-JSON tags, so the API emits a successful response with neither content nor tool calls. That is the contributor's account, not a path confirmed by reading v0.40.12, so treat it as the best available explanation rather than a verified one. The PR is open.

The practical consequence: if your agent exposes tools dynamically by mentioning them in a description, the request that "should" work will silently produce nothing, and the retry loop will keep producing nothing. Listing the tool, even with an empty parameter schema, is the difference between 28 of 32 empty and 30 of 32 working.

## Path 3: the repair closes braces, never brackets

The third path is in gemma4 argument parsing ([issue #19273](https://github.com/ollama/ollama/issues/19273)), and it is the clearest case of a one-line log message that looks harmless. The reporter's build is Ollama 0.40.6 on Windows with CUDA, and they note that `model/parsers/gemma4.go` has not changed since commit `a9d8953` (2026-09-22), so their observation extends to 0.40.11.

A gemma4 call that leaves the `edits` list unclosed still ends with its closing tag, so the model finished the call. The parser's repair candidates close a string delimiter, and they add a missing `}` only when another repair already changed the text. At v0.40.12, in [`model/parsers/gemma4.go`](https://github.com/ollama/ollama/blob/v0.40.12/model/parsers/gemma4.go), the object-close repair returns immediately when the argument text already ends in `}`, and no repair step inserts a `]` at all. So a call of the shape `call:edit{edits:[{newText:S,oldText:S,path:S}` has nothing in the repair path that can rescue it. The parser logs `gemma4 tool call parsing failed` and returns a reply with no `content`, no `tool_calls`, `done_reason: "stop"`, and no error field.

The reporter's counts come from five days of agent evals with `gemma4:e4b` through OpenClaw: 30 dropped `edit` calls in the server log, every one leaving the `edits` list unclosed, across 16 failed runs in 28 rounds. Their four observed call shapes split on what is missing — `path` inside the item with both `]` and the outer `}` absent (20 occurrences), `]` missing before `,path` (5), `]` and outer `}` missing (4), and one case with two items where only the `]` was missing. Those are one reporter's task mix, not a benchmark, but the shape distribution is the useful part: a single missing bracket, not a mangled call.

[PR #19274](https://github.com/ollama/ollama/pull/19274) adds a repair that closes the lists a finished gemma4 call leaves open. It is open. Until it lands, a gemma4 agent should treat the log line `gemma4 tool call parsing failed` as an incident marker and re-ask, not as noise.

## Path 4: the announce-then-call pattern on an MLX build

The fourth path is the narrowest and the one most likely to be a version artifact, so it is stated with its environment attached.

The report is [issue #19353](https://github.com/ollama/ollama/issues/19353). On `qwen3.8:27b-mlx` with Ollama 0.34.1 (macOS 26.5.2, Apple M4 Pro, 48 GB, `qwen3_5` architecture, nvfp4), a system prompt that asks the model to say something in natural language before calling the tool produces prose only: `tool_calls` is `null` and `done_reason` is `stop`. The same request with a tool-directive prompt returns parsed calls, and a control model, `qwen3:4b`, returns `finish_reason: tool_calls` with a non-empty preamble on three of four runs of the identical prompt. Only the system prompt differs between the two cases.

This is the shape of an announce-then-call instruction, which is a common agent pattern, so the report matters even though the version does not overlap the 0.40.x series. What it does not support is any claim about v0.40.12. Nothing here shows the behaviour reproduced on a newer build, and no source shows it fixed. If you run a preamble-style prompt on an MLX build, check this first; if you run it on a current CPU or CUDA build, you have no evidence either way from this report.

## The guard: an empty turn is an error, not a completion

Everything above is detectable client-side without patching the server, because the failure is a specific shape on the wire rather than an exception. The whole check is small enough to paste into the response handler:

```python
def lost_tool_call(msg, done_reason, eval_count):
    return (done_reason == "stop"
            and not (msg.get("content") or "").strip()
            and not msg.get("tool_calls")
            and (eval_count or 0) > 0)
```

When that predicate is true, treat the turn as a transport-level failure for the loop's purposes: do not append it to history as an assistant completion, do not fall through to a final answer, and either re-ask with the tool registered in `tools` or surface an error to the caller. Appending the empty message is the specific mistake that turns a recoverable drop into a session-ending stop, because the next request then replays a history in which the model appears to have said nothing.

Three supporting behaviours make the guard usable in practice:

- Log `done_reason` and `eval_count` on every turn, not only on errors. Without `eval_count` you cannot tell a dropped call from a genuinely empty reply, and you will spend the debugging session on the model.
- Validate argument types against the tool schema on the way in, before you append a call to history. The integer-to-string mutation survives forever once replayed, so the cheapest place to catch it is the moment it arrives.
- Before concluding a fix is missing or present, read the server version and compare it with the open pull requests listed above. The [v0.40.12 release](https://github.com/ollama/ollama/releases/tag/v0.40.12) was published on 2026-10-27T00:07:12Z, and none of the four pull requests referenced here is merged into it.

## Where to look first when a turn comes back empty

Order the checks by cost, cheapest first, and stop at the first one that explains the observation:

1. History serialisation. Does the request you sent contain the argument types you intended, or did a previous response already hand you `"30000.0"`? If the latter, the server-side retype happened one turn earlier.
2. The `tools` array. Is every function name the model could plausibly call actually listed, including the ones you only mention inside descriptions?
3. The server log. One line, `gemma4 tool call parsing failed`, names the parser path outright; its absence does not clear the other paths, which log nothing.
4. The model and build. Preamble suppression and MLX render paths are model- and build-specific, and are the last thing to blame, not the first.

For the surrounding mechanics, the [Ollama API integration guide](https://baeseokjae.github.io/posts/ollama-api-local-llm-integration-developer-guide-2026/) covers the `/api/chat` request shape these probes use, and the [gemma4 setup guide](https://baeseokjae.github.io/posts/gemma-4-local-setup-guide-2026/) covers installation and the errors that are not tool-call related. If a model looks worse rather than silent, [why a local LLM feels dumber](https://baeseokjae.github.io/posts/local-llm-feels-dumber/) covers quantisation, context and sampling — a different failure class from state corruption.

## What this article does not claim

It does not claim that all Ollama parsers or renderers share one defect: each of the four paths is reported against one model-parser or model-renderer pair, and the code observations are specific files at one tag. It does not claim the paths were reproduced here; no server was run. It does not claim the reports are current for v0.40.12 in either direction — none of them shows the behaviour on that tag, and none of the four pull requests is merged. The counts quoted, including 28 of 32, 30 of 32, eight of eight, three of three, 30 dropped calls and 16 of 28 runs, are the reporters' own on their own harnesses, at the versions they named, and are not normalised for hardware. No search-volume, keyword or traffic figure is claimed anywhere; the demand signal for this topic was repository issue incidence, which measures reported pain, not query volume.

The source records, fetched page bodies and code files behind this article are a private local author check kept beside the draft, not a downloadable dataset: the issue and pull-request payloads are third-party content, and republishing them is not something this article does. Every claim above links to the public page it came from, and those pages are the record to open.
