---
title: "dsh-auto-review: Second-Model AI Review for DeepSeek Harness Approval Requests"
date: 2026-09-05T07:01:36+00:00
tags:
  - deepseek harness
  - dsh-auto-review
  - AI approval
  - second model review
  - AI code review
  - approval automation
  - fail closed
description: "dsh-auto-review puts a read-only second model on DeepSeek Harness approval requests, returning a structured allow/deny verdict with reasons and failing closed by default."
draft: false
cover:
  image: "/images/dsh-auto-review-second-model-approval-2026.png"
  alt: "dsh-auto-review: Second-Model AI Review for DeepSeek Harness Approval Requests"
  relative: false
schema: "schema-dsh-auto-review-second-model-approval-2026"
---

dsh-auto-review is a DeepSeek Harness plugin that puts a read-only second model on the approval chain, deciding allow or deny for every tool request and returning a structured verdict with a reason. It fails closed by default, so any crash, timeout, or schema mismatch resolves to rejected rather than a silent grant, and it feeds deny reasons back to the calling model so the agent learns instead of retrying blindly.

## What is dsh-auto-review and why a second model?

dsh-auto-review is one of 33 DeepSeek Harness plugins maintained by PerryLink, and it plugs directly into the approval/request waterfall of DeepSeek Harness, the host platform that has grown to 212,530+ GitHub stars. Instead of relying on pattern-based rules alone, it introduces a second, independent model as a read-only reviewer subagent that examines actual workspace evidence before deciding whether a tool call should proceed.

The core idea is that a second model adds a layer of judgment that static rules cannot. A regex rule can catch a known-bad pattern, but it cannot reason about context, intent, or whether a command is safe given the current state of the repository. The reviewer reads real files, globs the workspace, and greps for evidence, then returns a structured verdict with a reason. That reason is what makes the difference: the calling model learns why a request was denied and can adjust, rather than blindly retrying the same action.

## How the approval chain works (answerer waterfall, ai/human/never policies)

DeepSeek Harness routes every tool request through an answerer chain, and dsh-auto-review inserts itself as a second-model reviewer on that chain. The plugin is session- and tool-policy-scoped for the interactive harness, and it never infers durable grants. Every tool call is evaluated against a per-tool policy that can be one of three values:

- **ai** — the second-model reviewer decides allow or deny autonomously.
- **human** — the request is delegated to the human approval chain.
- **never** — the tool is hard-disabled and can never be approved.

Out of the box, the shipped patch AI-reviews `bash` and `write`; every other tool, including `edit`, delegates to the human chain. This is a deliberately conservative default: only the two highest-risk tools are handed to the autonomous reviewer, and everything else keeps a human in the loop.

The plugin delegates everything it does not own via `next()`, so the rest of the answerer waterfall continues to work normally. This is a key design point — dsh-auto-review does not replace the approval chain, it sits on it and makes a decision for the tools it is configured to review.

## Installing dsh-auto-review

dsh-auto-review requires Node `^22.19 || >=24.0.0` and DeepSeek Harness `0.1.2-rc.1` (peers `>=0.1.0-rc.8 <0.2.0`). There are several installation channels:

| Channel | Command | Notes |
|---------|---------|-------|
| Git | `git clone https://github.com/PerryLink/dsh-auto-review` | Full source, best for development |
| npm | `npm install dsh-auto-review` | Standard package install |
| 1024 store | `dsh plugin install dsh-auto-review` | DeepSeek Harness plugin store |
| Tarball | `npm pack` / direct tarball | For offline or pinned installs |

After installing, you enable the plugin in your DeepSeek Harness configuration and point it at your `cordis.yml` file, where all routing and safety settings live. The plugin ships with a patch that applies the default `ai` policy to `bash` and `write`, so you can start reviewing immediately and then tune the policy to your needs.

## Configuring toolsPolicy, riskRules, and reviewer settings in cordis.yml

All routing and safety configuration lives in `cordis.yml`, which makes the whole system config-driven and changeable without touching code. The three main sections are:

**toolsPolicy** — maps each tool to `ai`, `human`, or `never`. This is where you decide which tools the second model reviews autonomously and which stay on the human chain.

**riskRules** — regex-based rules that flag risky arguments or patterns. These run before the model review and can force a denial or escalate a request to human review based on what the tool is about to do.

**reviewer settings** — configuration for the reviewer subagent itself, including the model to use, the timeout, and the fallback policy.

A typical configuration looks like this:

```yaml
toolsPolicy:
  bash: ai
  write: ai
  edit: human
  rm: never

riskRules:
  - pattern: "rm -rf /"
    action: deny
  - pattern: "curl.*\\|.*sh"
    action: human

reviewer:
  model: deepseek-reviewer
  timeoutMs: 60000
  fallbackPolicy: rejected
```

The default reviewer timeout is 60000ms, and the default `fallbackPolicy` is `rejected`, meaning the system fails closed. You can change any of these values from `cordis.yml` without rebuilding or redeploying the plugin.

## The read-only reviewer subagent: verdicts, redaction, and context isolation

The reviewer is a read-only subagent with a strict tool allow-list: `read`, `glob`, and `grep`. It cannot write, edit, run bash, fetch the network, or delegate. This is a hard security boundary — the decision-maker has no way to mutate the system it is judging.

When a tool request arrives, the reviewer examines the workspace, gathers evidence, and returns a structured verdict with three fields:

- **decision** — `allow` or `deny`
- **reason** — a human-readable explanation of the decision
- **riskLevel** — a severity rating for the request

Two additional protections make the reviewer trustworthy. First, sensitive arguments are redacted before they enter the reviewer prompt: tokens, passwords, `api_key`, `Authorization` headers, credentials, and private keys are stripped so secrets never reach the decision-maker. Second, workspace instruction files such as `AGENTS.md` and `CLAUDE.md` are filtered out, so repository-controlled text cannot influence the reviewer. This context isolation means the second model judges the request on its own evidence, not on instructions that a repository owner could inject.

## Fail-closed behavior and fallbackPolicy

The most important safety property of dsh-auto-review is that it fails closed. Every abnormal path resolves to `rejected` by default:

- **Reviewer crash** — if the reviewer process dies, the request is denied.
- **Timeout** — if the reviewer exceeds the 60000ms default timeout, the request is denied.
- **Schema mismatch** — if the reviewer returns a verdict that does not match the expected structure, the request is denied.

In all three cases, the request resolves through `fallbackPolicy`, which defaults to `rejected`. There is no silent grant path. If the second model cannot make a decision, the safe answer is no. This is the opposite of fail-open systems, where an error might let a dangerous command through because the guard failed.

## Safety knobs: circuit breaker, risk policy, /auto-review approve override

Beyond the core allow/deny decision, dsh-auto-review ships several safety knobs that let you tune how aggressive or conservative the review is:

**Rejection circuit breaker** — the default is 3 consecutive denials, or 6 of the last 10 verdicts, per turn. When the breaker trips, the reviewer stops accepting requests for that turn, preventing a runaway loop of denied actions from consuming resources or masking a deeper problem.

**Risk-level policy** — you can set a maximum acceptable risk level. Requests above that level are denied or escalated regardless of the reviewer's verdict, giving you a hard ceiling on what the second model is allowed to approve.

**One-shot `/auto-review approve` override** — a single explicit command that approves a specific request, bypassing the reviewer for that one call. This is a deliberate escape hatch for cases where a human has verified the action and wants to proceed without waiting for the model.

**Never-policy hard disable** — for tools you never want used, the `never` policy is a hard disable. No override, no escalation, no approval path. The tool simply cannot run.

## Audit trail and session-log reconstruction

Every decision is recorded in the session log, and the full audit trail can be reconstructed from three event types:

- **approval/asked** — the tool request entered the approval chain.
- **autoReview/verdict** — the reviewer returned its structured verdict.
- **approval/decided** — the final allow/deny decision was made.

By correlating these events, you can reconstruct exactly what was requested, what the second model decided, and what the final outcome was. This is critical for compliance, debugging, and understanding why an agent behaved a certain way. The deny reasons are also fed back to the calling model, so the audit trail captures not just the decision but the reasoning behind it.

## The standalone MCP server for external clients

dsh-auto-review also ships a standalone MCP server that exposes the same deterministic rules and cache to external clients such as Claude or Codex. This server runs the rule-based layer — `toolsPolicy`, `riskRules`, and the cache — without invoking a model review. It is useful when you want the deterministic guardrails of dsh-auto-review outside the DeepSeek Harness environment, or when you want a lightweight, model-free approval layer for other tools.

The MCP server is a good fit for teams that want the policy and risk-rule enforcement without the cost or latency of a second-model call on every request.

## dsh-auto-review vs dsh-auto-approval: which to choose

There are two similar plugins in the ecosystem, and they differ in important ways. The table below summarizes the key differences:

| Aspect | dsh-auto-review | dsh-auto-approval |
|--------|-----------------|-------------------|
| Position | Official answerer chain | Tools/pre-execute waterfall |
| Decision model | Read-only second model, structured verdict | Two-state allow/deny classifier |
| Delegation | Always delegates what it does not own via `next()` | Monorepo of host + client UI halves |
| Output | `{decision, reason, riskLevel}` | Allow/deny only |
| Deny reasons | Fed back to calling model | Not fed back |
| Audit | Session-log events | File-log audit |
| Scope | Session- and tool-policy-scoped | Classifies every tool call |

If you want a second model that reasons about evidence, explains its decisions, and feeds reasons back to the agent, dsh-auto-review is the stronger choice. If you want a lightweight two-state classifier that runs on the pre-execute waterfall with a file-log audit, dsh-auto-approval may be simpler. For most teams that already use DeepSeek Harness, dsh-auto-review's official answerer-chain integration and structured verdicts make it the more capable option.

## Known limitations and security boundaries

dsh-auto-review is powerful, but it has clear boundaries you should understand before relying on it:

- **It is not a human replacement.** The `ai` policy is for tools you trust the second model to judge. High-stakes or irreversible actions should stay on the `human` chain.
- **It never infers durable grants.** Every decision is scoped to the current session and tool policy. There is no persistent "trusted" state that carries across sessions.
- **The reviewer is read-only by design.** It can only read, glob, and grep. It cannot verify a command by running it, so its judgment is based on static evidence.
- **Fail-closed means false denials are possible.** A timeout or crash denies a request even if it was safe. This is the intended trade-off for safety.
- **The MCP server has no model review.** If you use the standalone server, you get deterministic rules only, not the second-model judgment.

The security boundary is deliberately conservative: the reviewer cannot mutate anything, secrets are redacted, and repository-controlled instruction files are filtered out. This makes dsh-auto-review a strong guardrail, but you should still pair it with human oversight for the most sensitive operations.

## FAQ

**What is dsh-auto-review?**
dsh-auto-review is a DeepSeek Harness plugin that adds a read-only second-model reviewer to the approval chain. It decides allow or deny for tool requests and returns a structured verdict with a reason, failing closed by default.

**How does the second model review work?**
The reviewer subagent uses a read-only tool allow-list (read, glob, grep) to examine workspace evidence, then returns a structured verdict with decision, reason, and riskLevel. Sensitive arguments are redacted and repository instruction files are filtered out before the request reaches the model.

**What does fail closed mean in dsh-auto-review?**
Fail closed means any abnormal path — reviewer crash, timeout, or schema mismatch — resolves to rejected through the fallbackPolicy, which defaults to rejected. There is no silent grant path; if the reviewer cannot decide, the safe answer is no.

**Which tools does dsh-auto-review review by default?**
Out of the box, the shipped patch AI-reviews `bash` and `write`. Every other tool, including `edit`, delegates to the human approval chain. You can change this in `cordis.yml` with per-tool `ai`, `human`, or `never` policies.

**How do I install dsh-auto-review?**
You can install it via git clone, npm, the 1024 plugin store, or a tarball. It requires Node `^22.19 || >=24.0.0` and DeepSeek Harness `0.1.2-rc.1` (peers `>=0.1.0-rc.8 <0.2.0`).
