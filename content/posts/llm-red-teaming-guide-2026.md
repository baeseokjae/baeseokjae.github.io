---
cover:
  alt: 'LLM Red Teaming Guide: Scope, Failure Evidence and Regression Cases'
  image: /images/llm-red-teaming-guide-2026.png
  relative: false
date: 2026-05-10 00:00:00+00:00
draft: false
schema: schema-llm-red-teaming-guide-2026
slug: llm-red-teaming-guide-2026
tags:
- red-teaming
- ai-security
- llm
- prompt-injection
- security
title: 'LLM Red Teaming Guide: Scope, Failure Evidence and Regression Cases'
description: Design an authorized agent evaluation with defined trust boundaries, reproducible failure records and metrics that distinguish refusal from safe execution.
lastmod: '2026-10-20T08:06:38.069366+00:00'
---

An LLM red-team exercise is useful when it reveals a failure you can reproduce, explain and fix. Collecting dramatic prompts without an application boundary or an outcome definition produces little evidence about a deployed agent.

This guide focuses on authorized testing of systems you own or have permission to assess. It provides a runbook and result schema, not a claimed security score for a model or product.

## Define the trust boundary

[OWASP's prompt-injection description](https://genai.owasp.org/llmrisk/llm01-prompt-injection/) covers adversarial instructions entering through prompts or external content. Its [prevention guidance](https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html) recommends layered controls instead of treating natural-language instructions as an authorization system.

[PyRIT](https://raw.githubusercontent.com/Azure/PyRIT/main/README.md) and [garak](https://raw.githubusercontent.com/NVIDIA/garak/main/README.md) provide tooling for organizing or running evaluations. Tool availability does not establish that a particular application passed a meaningful test.

For an agent, enumerate data sources, available tools, credentials and side effects. A model can refuse in prose while an application still executes a harmful action. Conversely, an alarming generated sentence may produce no unauthorized operation. Record both behavior and actual effects.

## Write a bounded test charter

The [red-team case sheet](/research/content-quality-batch2-2026-10/redteam-cases.csv) records the system version, entry point, asset, attempted policy violation, expected control and observed outcome.

Specify the allowed environment, accounts, execution budget and stop condition before starting. Use synthetic records and harmless sentinel strings instead of customer data or live credentials. Route any simulated external destination to a test sink you control.

Start with application-specific failures: another tenant's record, an unauthorized tool operation, a retrieved document pretending to override instructions, or a repeated request that would duplicate a side effect. Include a valid authorized request so denial of everything is not mistaken for success.

## Record enough to reproduce a failure

Retain model/version, system configuration, tool schemas, retrieved fixture, request sequence, sampling settings and timestamps. Save the actual tool request and the application's authorization decision. Redact secrets before storing or sharing the record.

For a state-changing operation, inspect the resulting state rather than relying on the assistant's narration. For an information disclosure, compare the returned content with the synthetic sentinel. For an availability issue, record the resource limit and recovery path.

Re-run cases because model outputs may vary. Preserve all attempts and the tested configuration. A repeatable application-policy failure can be deterministic even when the language model is not.

## Metrics with honest denominators

Define “success” before counting it. Separate attempted unauthorized tool calls, actually authorized calls, completed harmful side effects and textual policy violations. Report the number of attempts and cases represented.

If one case is attempted repeatedly, do not count every attempt as an independent vulnerability. Report both case coverage and attempt-level outcomes. When a model refuses, verify that the application did not perform the disallowed action through another path.

Track valid-request completion too. A mitigation that blocks legitimate work can look secure while making the product unusable. Avoid claiming that a finite test set proves the absence of all prompt-injection vulnerabilities.

## Turn findings into regression controls

Fix the failing boundary where possible: server-side authorization, bounded tool inputs, controlled data access and explicit approval for consequential operations. Keep prompt changes as one layer rather than the only control.

Add the minimized failure as a regression case and re-run both denied and allowed paths after model, retrieval or tool changes. The [automated tool-boundary example](/posts/automated-red-teaming-ai-agents/) supplies a small deterministic starting point. It is not a live model red-team result.

Close a finding when the relevant control demonstrably prevents the recorded failure and the normal workflow still works. Keep remaining uncertainty in the report.

## Revision note

**Updated October 20, 2026.** Removed unsupported security-market and adoption projections. Replaced generic assurances with a scoped defensive runbook, evidence schema and explicit outcome definitions.

## Primary sources

Checked October 20, 2026: [owasp injection](https://genai.owasp.org/llmrisk/llm01-prompt-injection/); [owasp defense](https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html); [pyrit](https://raw.githubusercontent.com/Azure/PyRIT/main/README.md); [garak](https://raw.githubusercontent.com/NVIDIA/garak/main/README.md).
