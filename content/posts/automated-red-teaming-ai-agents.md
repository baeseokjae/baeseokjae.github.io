---
title: 'Automated Red Teaming for AI Agents: A Reproducible Tool-Boundary Check'
date: 2026-07-14
lastmod: '2026-10-20T07:02:10.628622+00:00'
description: Build a safe regression set for agent tool authorization, distinguish deterministic checks from model red teaming, and track failures with useful evidence.
draft: false
schema: schema-automated-red-teaming-ai-agents
cover:
  alt: 'Automated Red Teaming for AI Agents: A Reproducible Tool-Boundary Check'
  image: /images/automated-red-teaming-ai-agents.png
  relative: false
---

An agent can produce a reassuring answer while its application performs an unauthorized operation. A useful red-team program therefore checks the action boundary as well as the model's text. This guide starts with a small, reproducible example you can inspect, then explains what a real model evaluation must add.

The example reads synthetic project records. It has no network access, shell execution, real credentials, or write operations. It demonstrates application checks; it does not measure whether an LLM resists prompt injection.

## Define the boundary before collecting prompts

[OWASP's prompt-injection risk description](https://genai.owasp.org/llmrisk/llm01-prompt-injection/) covers attempts to redirect model behavior through supplied content. The [prevention guidance](https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html) recommends layered controls, including separating untrusted content and validating actions. A prompt filter alone does not establish authorization.

Tools such as [garak](https://raw.githubusercontent.com/NVIDIA/garak/main/README.md) can help organize model probes. Their output needs an application-specific interpretation: a refusal, a leaked string, and a blocked tool call are different events. Select the event that corresponds to the asset you are protecting.

## Run the offline example

Download [tool_boundary.py](/research/content-quality-2026-10/tool_boundary.py) and run:

```bash
python3 tool_boundary.py
```

The [recorded run](/research/content-quality-2026-10/offline-results.json) contains **12 passing deterministic cases**, including valid reads, a cross-tenant request, an unknown tool, malformed JSON, a forged tenant argument, a Boolean identifier, and an oversized argument string. The recorded Python version and source hashes identify exactly what ran.

The application obtains the tenant from its own session context. Model arguments can specify only a record identifier. An unknown record and an inaccessible record return the same error, avoiding an unnecessary existence signal. This is deliberately a small teaching implementation, not a replacement for your identity and authorization system.

## Why passing these cases is only the first layer

The fixture directly submits tool requests. It never asks a model to produce them. That makes failures easy to reproduce, but leaves important questions unanswered: whether the model attempts an unauthorized call, whether sensitive material reaches its context, and whether its answer reveals information without invoking a tool.

Use separate measurements for those questions:

| Layer | Observation to record | Useful control |
|---|---|---|
| Retrieval | Which documents entered context | Same query with an authorized and unauthorized document |
| Model behavior | Requested tool and arguments | Benign task that should succeed |
| Application boundary | Allowed or denied action | Exact replay of the proposed tool call |
| User-visible answer | Content returned to the requester | Check for false success and sensitive disclosure |
| Recovery | State after timeout or retry | Replay the same request identifier |

Keep benign controls in the suite. Blocking every request can make an attack metric look impressive while making the application useless. Report failed benign tasks beside unauthorized action attempts and completed unauthorized actions.

## Turn an incident into a regression

Write down the intended user task and the point where untrusted text entered the workflow. Replace private data with synthetic markers. Preserve the original failure mechanism, but remove unnecessary payload detail and unrelated environment state.

Store the model/version, system instructions, tool schema, retrieved fixture, requested call, application decision, and final answer. Repeat the case after changing one control at a time. If a model update changes the behavior, keep both transcripts so you can distinguish a model effect from a code change.

For tools that send messages, change permissions, or create resources, test against a mock or disposable environment with explicit authorization. A blocked model request must not be silently retried by a different component with broader permissions. Verify the final side effect, not just the assistant's claim that it stopped.

Use the [function-calling guide](/posts/llm-function-calling-tool-use-guide-2026/) to connect these checks to provider call IDs and bounded execution loops. Treat a green regression run as evidence for the covered cases, with its exact configuration and date.

## Revision note

**Updated October 20, 2026.** Removed vague case studies and claims that automation ensures comprehensive protection. Added executable synthetic boundary cases, their actual run record, and a separate protocol for model-level testing.

## Primary sources

Checked October 20, 2026: [owasp defense](https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html); [owasp injection](https://genai.owasp.org/llmrisk/llm01-prompt-injection/); [garak](https://raw.githubusercontent.com/NVIDIA/garak/main/README.md).
