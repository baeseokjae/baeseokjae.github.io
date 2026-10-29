---
cover:
  alt: RockB — AI tools and engineering guides
  image: /images/og-default.png
  relative: false
title: "LiteLLM Rewrites Your Tool Call IDs: Debugging Broken Multi-Turn Tool Loops Across Ollama, Gemini and Responses Bridges"
date: 2026-10-28T16:00:00+00:00
tags:
  - "litellm tool call id"
  - "ollama_chat tool_calls"
  - "litellm proxy streaming"
  - "tool_call_id mismatch"
  - "litellm 1.106.5"
  - "stream_chunk_builder"
  - "gemini thought signature"
  - "responses api tool call"
  - "multi-turn tool loop"
  - "llm proxy debugging"
  - "openai compatible proxy"
  - "agent tool call identity"
description: "A litellm 1.106.5 probe with recorded upstream fixtures: ollama_chat/ drops assistant tool-call ids, streaming replaces the provider's id with a UUID, and a dict-shaped delta silently erases the call. Three reproducible failures, one case that did not reproduce, and a guard that keeps call identity stable."
draft: false
schema: "schema-litellm-tool-call-id-translation-2026"
---

Your agent calls a tool through a LiteLLM proxy. Turn one returns a tool call, the tool runs, and turn two comes back with an empty tool result or a 400 from the provider. The model never saw a different question — it saw a conversation whose tool call and tool result no longer share an identifier. That single broken invariant produces a whole family of symptoms that look like model failures, and the code paths responsible sit in the proxy, not in the model.

This article separates three failures that reproduce against the current release, one claim that did not reproduce in the harness used here, and one reported case that is kept at "reported, not verified". It ends with a guard you can put in front of the proxy so the next broken loop is detectable instead of mysterious.

## What was actually run, and what that is worth

Every runtime observation below comes from feeding recorded upstream payloads into litellm's own code paths at version 1.106.5 — the release uploaded 2026-10-27 according to the [PyPI project metadata](https://pypi.org/pypi/litellm/1.106.5/json). The fixtures are ordinary JSON: an OpenAI-shaped chunk stream and two native Ollama chunks. They are handed to `CustomStreamWrapper`, `stream_chunk_builder()`, `OllamaChatConfig.transform_request()` and `OllamaChatCompletionResponseIterator.chunk_parser()`. No proxy process was started, no socket was opened, no provider was called, and no key was used.

That design is deliberate: because the fixture *is* the upstream, any difference between the fixture and the emitted result is attributable to the proxy hop. It is a private local author verification, not a vendor measurement and not a published dataset — the probe script, fixtures and captured outputs live in the site repository's review evidence directory and are not offered as a reader download. The rest of the evidence is primary and public: the shipped source of the two releases, the open issue reports, and the [1.95.0 release metadata](https://pypi.org/pypi/litellm/1.95.0/json) that fixes the version named in the original bug report.

One scope correction matters before anything else. The topic was scoped to 1.95.0, released 2026-08-02. The id-destroying sites described below are unchanged in 1.106.5, so this is not a historical bug that a `pip install -U` has already closed.

## Three failures that reproduce at 1.106.5

### 1. ollama_chat/ rebuilds the assistant call without its id, then forwards the result's id

The request transform for the Ollama chat provider rebuilds every assistant `tool_calls` entry as a fresh `OllamaToolCall(function=OllamaToolCallFunction(name=..., arguments=...))` — a structure with no id field at all — while the tool-result message keeps its `tool_call_id` verbatim. The two sites are adjacent in the [shipped transformation module](https://github.com/BerriAI/litellm/blob/main/litellm/llms/ollama/chat/transformation.py): the rebuild discards the id, the passthrough keeps it.

Fed a three-message conversation — user, assistant call `call_up_F1`, tool result `call_up_F1` — the transform returned an outgoing assistant message whose first tool call had no id, and a tool message whose `tool_call_id` was still `call_up_F1`. The provider is therefore asked to match a result to a call it was never told the name of. In practice that surfaces as empty tool output, or as a model that re-requests the same tool because it cannot see the answer. The open report [BerriAI/litellm#48457](https://github.com/BerriAI/litellm/issues/48457), created 2026-10-26, describes exactly this and notes that it reproduces through the Chat Completions, Responses and Anthropic Messages bridges, which is what makes it a proxy-layer problem rather than one bad integration.

### 2. Streaming replaces an id the provider actually sent with a UUID

Ollama's own streaming protocol does emit tool-call ids. The provider's chunk parser still overwrites them. In the streaming parser, whenever the arguments parse as a complete call, the code executes `tool_call["id"] = str(uuid.uuid4())` with no check for an id already present — the same statement in both releases, and visible in the [current transformation module](https://github.com/BerriAI/litellm/blob/main/litellm/llms/ollama/chat/transformation.py). The open report is [BerriAI/litellm#46543](https://github.com/BerriAI/litellm/issues/46543), created 2026-10-14.

Replaying a native Ollama chunk that carried `id: "call_8uaqob2r"` through the chunk parser at 1.106.5 produced `id: "cce1e8a6-e2ef-4364-a9e4-87db6c7825a6"` in the emitted delta. The function name and arguments survived; the identity did not. Any client that matches a later tool result by id — which is the correct thing to do — now holds an id the proxy will never emit again.

### 3. One object instead of a list, and the call disappears without a word

The stream assembly path normalises tool calls only when `delta.tool_calls` is a list. A delta that carries a single object is never normalised, and nothing raises. Assembling a two-chunk stream whose first delta held `tool_calls` as an object, rather than a one-element list, returned a message with `tool_calls == []` and no exception, no warning, and no log line at the default level in this harness. The reported behaviour and the localisation are in [BerriAI/litellm#46202](https://github.com/BerriAI/litellm/issues/46202), created 2026-10-13.

This is the worst failure mode of the three because it is silent. A dropped call and a model that chose not to call a tool are indistinguishable from the client side, so the obvious next step — retry, raise the temperature, change the model — is wasted effort.

## What did not reproduce

Two related claims are worth separating from the failures, because repeating them would be wrong.

First, the whole-call-in-one-delta case. [BerriAI/litellm#39796](https://github.com/BerriAI/litellm/issues/39796), open since 2026-09-04, reports that a proxy in passthrough mode drops `tool_calls[].id` and `function.name` when the upstream sends a complete call in a single SSE delta, leaving only `arguments`. Replaying that exact shape through `CustomStreamWrapper` at 1.106.5 emitted a fragment that still carried `id: "call_up_F2"` and `name: "get_ticket_status"`. The split-delta shape also kept its identity on the fragment that opens the call. That does not refute the report — the reporter's configuration is the proxy passthrough route with `modify_params: false`, which is a different code path from the wrapper exercised here — but it does mean the claim stays "reported" in this article and you should test your own route rather than assume it.

Second, the Gemini case. [BerriAI/litellm#41534](https://github.com/BerriAI/litellm/issues/41534), created 2026-09-17, reports that with a router fallback chain a thought signature embedded in `tool_call.id` is forwarded into the Responses API `input[N].id` and OpenAI rejects the request with a 400 string-too-long. A grep for `thought_signature` across the responses transformation, the Gemini chat transformation and `router.py` in the 1.106.5 wheel returned zero hits, so the handling either lives elsewhere or the signature enters through provider-specific fields. It is left out of the pass/fail set rather than softened into a guess.

## Prove the corruption is in the proxy, not the model

The method that settles these arguments is cheap: capture both sides of the hop and compare identities per call.

1. Log the raw upstream SSE bytes before the proxy touches them — the provider's own `id`, `function.name` and `index` for each tool call fragment.
2. Log what your client receives, or what `stream_chunk_builder()` assembles.
3. Key the comparison on id, name and index, not on the arguments string, which legitimately changes between fragments.
4. On the next turn, assert that every assistant `tool_calls[].id` has a matching tool-result `tool_call_id` in the request body you are about to send.

If step 1 shows an id and step 3 shows a different one, the proxy rewrote it. If step 1 shows no id at all, the provider never sent one and the proxy is synthesising — which is legal only if it synthesises once and reuses the same value for the result. Keeping that boundary explicit is the same discipline you need when auditing a recorded trajectory after the fact, which is what [ToolReplay's session replay approach](https://baeseokjae.github.io/posts/toolreplay-agent-tool-call-audit-2026/) does, and when watching tool calls and token spend together, as in [agent trajectory monitoring](https://baeseokjae.github.io/posts/agent-trajectory-monitor-tool-calls-token-spend/).

## A guard that keeps call identity stable

The following wrapper sits in front of the provider call and fixes the three reproducible failures without patching litellm. It preserves ids that exist, synthesises one only when the provider omitted it, normalises a dict-shaped `tool_calls` into a list, and refuses to send a conversation whose tool results reference ids no assistant message contains.

```python
import json, uuid

def normalize_tool_calls(raw):
    if raw is None:
        return []
    return [raw] if isinstance(raw, dict) else list(raw)

def guard_request(body):
    """body: OpenAI-shaped request dict with messages[]. Fail closed on identity breaks."""
    seen = set()
    for msg in body.get("messages", []):
        if msg.get("role") == "assistant":
            calls = normalize_tool_calls(msg.get("tool_calls"))
            for call in calls:
                if not call.get("id"):                 # provider omitted the id
                    call["id"] = f"call_{uuid.uuid4().hex[:16]}"
            msg["tool_calls"] = calls
            seen.update(c["id"] for c in calls)
        elif msg.get("role") == "tool":
            if msg.get("tool_call_id") not in seen:
                raise ValueError(
                    f"orphan tool result {msg.get('tool_call_id')!r}: no assistant call carries that id"
                )
    return body
```

Use it with two rules the probe justifies. Synthesise ids at the point of creation, never at the point of forwarding, so the same value reaches both the assistant message and the tool result. And treat a missing `tool_calls` entry after assembly as an error, not as an empty list, because failure 3 above produces exactly that and stays quiet about it.

## Before you upgrade or blame the model

Check the version first. Both `ollama_chat/` id sites are unchanged between 1.95.0 and 1.106.5, so an upgrade alone does not close failures 1 and 2; the version is still worth pinning in any report you file. Then check the route: the passthrough streaming path and the standard wrapper path differ, and the difference decides whether failure 3 in this article is your failure too. Finally, if your architecture puts a gateway in front of several providers, the wire-format question and the routing question are separate decisions, and the [LLM gateway comparison](https://baeseokjae.github.io/posts/llm-gateway-comparison-2026/) covers the second while this article covers the first. If the hop is direct to Ollama with no proxy in between, the failure belongs to a different layer and the [Ollama API integration guide](https://baeseokjae.github.io/posts/ollama-api-local-llm-integration-developer-guide-2026/) is the closer reference.

The narrow conclusion: at 1.106.5 a recorded upstream call with id `call_8uaqob2r` is re-emitted with a freshly generated UUID, an assistant call loses its id while its result keeps one, and a single-object delta erases the call without an error. Those are three testable statements, each with a fixture, a captured output and an open upstream report behind it — enough to stop blaming the model for a broken identifier.
