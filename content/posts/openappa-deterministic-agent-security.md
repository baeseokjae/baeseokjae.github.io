---
title: 'OpenAPPA Agent Security: Deterministic Guardrails for Agentic Applications'
date: 2026-10-01T02:46:58+00:00
tags:
  - OpenAPPA
  - agent security
  - information flow control
  - prompt injection
  - MCP security
  - AI guardrails
  - deterministic security
description: "OpenAPPA agent security labels what an agent has read and blocks disallowed flows before a tool runs, deterministically and outside the prompt."
draft: false
cover:
  image: "/images/openappa-deterministic-agent-security.png"
  alt: "OpenAPPA Agent Security: Deterministic Guardrails for Agentic Applications"
  relative: false
schema: "schema-openappa-deterministic-agent-security"
---

OpenAPPA agent security means enforcing information-flow policy outside the model's prompt: the engine labels everything an agent reads as audience x trust, checks every tool call against a declarative TOML contract before it runs, and returns a machine-readable remedy plan when a flow is disallowed. Its vendor benchmarks record zero successful attacks across 1,320 guarded evaluations.

## What is OpenAPPA, and what is it not?

[OpenAPPA](https://openappa.com) is an MIT-licensed, Rust-based security engine published by Archestra AI in August 2026 and powered by APPA (Agentic Permissions Policy Algebra). It sits between an agent and its tools to answer one question before every action: is this data allowed to go to this destination? Reading a private record narrows the session's audience; reading an outsider's web page lowers its trust; a later call aiming at a destination the session no longer permits is refused before dispatch, not after.

The design line the project builds everything on is that you cannot prompt-inject an algebra. Labels, contracts, and remedy plans live out of band, in a runtime the model cannot see or negotiate with. That matters because the attack class is not "the model was persuaded" but "the model faithfully executed instructions planted in data it was told to read."

It is equally important to say what OpenAPPA is not. It is not a prompt-injection detector, a PII scanner, or a command blacklist. It is not a sandbox: it does not restrict what the agent can touch, it restricts where data the agent has already read may go. It is not an OPA or Cedar replacement: OpenAPPA deliberately cannot express arbitrary business rules in policy, though it does carry restrictions forward between actions, which those engines do not. And it is not finished software. The repository labels itself a preview and an RFC, with config and wire surfaces that may break without shims.

## Why do probabilistic agent guardrails fail against indirect prompt injection?

Because the failure is in the data path, not in the model's judgment. Three years of published incidents make the pattern concrete. EchoLeak (CVE-2025-32711) against Microsoft 365 Copilot was zero-click: the exfiltration channel was a Markdown image whose URL the chat client fetched automatically, on a domain already present on the content security policy allow-list. In the SalesBleed disclosure, a poisoned record submitted through a public Salesforce Agentforce Web-to-Lead form hijacked the agent, which encoded retrieved account data into a DNS subdomain; the data left during DNS resolution, before any HTTP request existed to block.

Academic work quantifies how reliably this works. The Puppet confused-deputy study against MCP, published in ACM TOSEM, measured tool selection hijacking at up to 90.89% and end-to-end malicious payload execution at up to 86.46% across 14 models from 6 providers, with reasoning-enabled models significantly more vulnerable than non-reasoning counterparts. Both MCP-Scan and McpSafetyScanner failed to detect the attacks.

The MCP ecosystem itself is unstable ground. An August 2026 census harvested 21,643 servers and 72,606 version records, finding that 15.2% of scanned servers carried at least one finding and 11.1% at least one high-severity finding, dominated by unauthenticated network exposure. Worse for anyone relying on a one-time review: 51.1% of multi-version servers changed what they advertise between versions, 40.6% did so silently with no identifier change, and 4.2% redirected their remote endpoint to a different host while keeping their registry identity. Silent drift was associated with roughly triple the odds of a high-severity finding (OR = 2.96), while popularity offered only weak protection (OR = 0.78 per unit of log stars).

Against that backdrop, the industry's default posture is detection, and detection has a ceiling. OpenAPPA cites OpenAI's own prompt-injection check at 99.3%: at millions of calls, 0.7% is a lot of breaches. The second-model school has an architectural hole of its own. Claude Code's auto mode sends proposed commands to a classifier model, and Codex routes sandbox-boundary crossings to an auto_review agent, but to keep hostile input from tricking the judge, the harnesses strip tool outputs from its request. The classifier sees the command being run and never sees the values earlier tools returned, so it cannot observe provenance at all. When three consecutive denials land, both systems circuit-break back to manual prompts rather than explaining how to proceed.

## How does OpenAPPA track data flow across a session?

Each trajectory, meaning an agent's work on one conversation or task including its tool calls, carries a security label and the policy needed to evaluate its next action. The label is computed as `label = admittedLabels.reduce(narrow, startingLabel)`, and `narrow` only ever restricts. That monotonicity is what buys the provable guarantee, and it is also the honest difference from classic taint tracking that permanently strands execution. OpenAPPA keeps the monotone restriction but adds remedy plans so the agent can still finish the job, which is the subject of the next section.

### What are security labels: audience, trust, effects, and attention?

Four concepts, two of which most write-ups skip:

- **Audience** is who is authorized to access the session's data. Reading data for a smaller audience restricts where the agent may send it later. Built-in audiences form the chain `self ⊆ internal ⊆ public`; named groups such as `@finance` or `@slack:channel/$channel_id` cover everything else. A contract can extract an audience from the call's own arguments: reading Slack channel `C0123` labels the data with that channel's members, and posting to it requires that they are already valid readers.
- **Trust** follows who *wrote* the text, not who can read it. Text written only by the organization and its collaborators keeps the session's trust; a web page, an outsider's comment, or a meeting transcript with outside participants lowers it. Trust and audience are independent: a public repository issue written only by the team keeps trust, while an outsider's comment on a private repository is suspicious.
- **Effects** accumulate. `effects = ["egress"]` records that something happened, and later contracts can require (`contains`) or forbid (`excludes`) that it happened, which is how action ordering gets enforced.
- **Attention** is per-call and never accumulates. An approval clears the attention requirement for that action only. When an injected document claims a transfer was already pre-approved, the claim does not satisfy `requires.attention`, because policy demands the real approval in recorded history.

### How do tool contracts use delta, requires, and effects?

Every `[[policy.tool]]` entry answers three questions, and it is the whole contract surface:

| Field | What you write | What OpenAPPA does |
|---|---|---|
| `delta` | Restrictions the tool's result carries | Applies them when the agent receives the result |
| `requires` | Conditions the call must satisfy | Checks them before allowing the call |
| `effects` | Side effects of a successful call | Records them in the trajectory history |

`delta` can only restrict: it can narrow the audience or lower trust, never widen or raise. `requires` supports audience, trust, effects, and attention conditions, with `contains` (the current audience must include all listed readers) and `within` (every current reader must belong to the listed audience) as the only two audience operators. A recipient argument is bound with a placeholder, so `requires = { audience = { contains = ["$recipient"] } }` makes the recipient a required top-level argument of the tool.

Contracts match in declaration order and the first match wins, which lets a policy write `read_file(path:/docs/*)` with a public delta ahead of a general `read_file` rule marked internal. A missing match can fall through to a wildcard contract (`name = "*"`), but once a contract matches, a schema error refuses the call rather than falling through, and `appa/execute_remedy_plan` is reserved to the runtime and cannot be declared or shadowed by a policy.

## How do remedy plans keep a guarded agent useful?

This is the part that decides whether deterministic enforcement survives contact with production. A bare forbidden makes an agent stall, retry, and fail; the ablation numbers show exactly how much. On Bench-Corp with GPT-5.6 Luna, task completion was 88.0% with full OpenAPPA, 56.5% with subagent isolation removed, and 35.0% with guided recovery removed. Enforcement strength did not change across those rows; utility did.

When a call does not meet its contract, OpenAPPA blocks it and returns the remedy plans the policy allows. Four remedies cover most real cases:

- **Narrow** the request so it targets an audience the session can still reach.
- **Sanitize**: a registered sanitizer rewrites the payload before the tool receives it or before the result reaches the model. The sanitizer's `permits` declares the transition it is allowed to make, either an audience move such as `from = ["internal"], to = ["public"]` or a trust move such as `from = "suspicious", to = "trusted"` — never both. Built-ins include `redact-email`, `redact-secrets`, and model-backed `llm` and `claude-code` variants.
- **Request authority**: a person, an internal approval service, or a bounded model evaluator approves that one call. Approval does not loosen the label and does not cover the next call.
- **Fork a child trajectory**: a subagent reads the sensitive data in a separate context and returns only what the policy permits, often through a sanitizer, so the parent trajectory is never poisoned by the read. `context_control = true` declares that the integration keeps child data separate and can withhold its answer until the check passes.

The key property is that an offered plan can still be denied by the approval service or fail during cleaning. If no permitted remedy succeeds, the action stays blocked. The engine never trades the invariant for completion.

## What do the OpenAPPA benchmarks actually show?

Every number below is vendor-published by Archestra and should be read that way. Across 1,320 evaluations — 600 from Bench-Corp and 720 from AgentThreatBench — no scored attack succeeded against guarded OpenAPPA, with a combined 89% task completion. Claude Code auto mode and Microsoft FIDES let 10% and 31% of attacks through on the same headline table.

Bench-Corp runs 20 multi-step enterprise workflows, 200 episodes per model, scoring what the agent actually changed or sent rather than using an LLM judge. Utility followed by attack success rate:

| Model | Guarded OpenAPPA | FIDES middleware | FIDES native |
|---|---|---|---|
| GPT-5.6 Luna | 88.0% / 0% | 38.5% / 32.0% | 37.0% / 32.5% |
| DeepSeek V4 Flash | 89.5% / 0% | 39.5% / 34.5% | 41.5% / 33.0% |
| Gemini 3.7 Flash | 90.0% / 0% | 43.5% / 28.5% | 44.5% / 28.0% |

The auto-mode head-to-head is the most useful table for a decision, and also the least statistically powerful: one actor model (Claude Sonnet 5), every task run once, so there is no variance estimate. IFC-tuned Auto restates each scenario's information-flow policy in plain language for a classifier; Stock Auto is the out-of-the-box baseline that knows nothing about deployment-specific rules.

| Benchmark | Guarded OpenAPPA | IFC-tuned Auto | Stock Auto |
|---|---|---|---|
| Bench-Corp (20 scenarios) | 75.0% / 0 attacks | 85.0% / 0 | 90.0% / 2 |
| AgentThreatBench (24 tasks) | 75.0% / 0 attacks | 95.8% / 6 | 87.5% / 8 |

Read plainly: OpenAPPA was the only configuration with zero scored attacks in both suites, and it paid for that with 10 to 21 points of task completion against the auto configurations. On Tau Bench's 97 banking support tasks (not an attack benchmark, four trials each), guarded OpenAPPA finished 151/388 simulations versus 153 for the same agent under a permissive policy and 156 for stock, with mean reward 1.29 points below stock. Its token overhead there was 4.22%, and across the attack suites the vendor reports guarded runs using 6.5x the tokens of a permissive policy on Bench-Corp and 2.3x on AgentThreatBench. Claude's SDK does not report what the auto-mode classifier spends, so total costs are not directly comparable.

## How does OpenAPPA compare with FIDES, OpenShell, OPA, and agent auto-modes?

OpenAPPA is not alone in the deterministic camp, and it is not the only layer you need.

| Approach | Enforcement point | Tracks provenance | Returns recovery options | Main weakness |
|---|---|---|---|---|
| OpenAPPA / APPA | Tool dispatch + MCP gateway | Yes, across the trajectory | Yes, structured remedy plans | Preview; 2.3-6.5x token cost; 75% completion in the head-to-head |
| Microsoft FIDES | Agent Framework middleware, pre-call | Yes, but linear | No | Completion collapses to 37-45% when a confidential read permanently taints the run, while 28-35% of attacks still get through |
| Nvidia OpenShell + Sentry | Kernel-isolated sandbox and DPU watchdog | No, isolation rather than flow | Quarantine in milliseconds | Restricts what the agent may touch, not where read data may go; Sentry is not open source |
| OPA / Cedar / Dogwood | Application-supplied context | No, your app must supply history | No, returns a decision only | You build the history, the combination rules, and the recovery workflow |
| Claude Code auto mode, Codex auto-review | Classifier or reviewer model | No, harnesses strip tool outputs | No, circuit breakers | Prompt-injectable judge; cannot see data provenance |

Two details worth carrying away. First, FIDES is the closest direct comparator and the most instructive failure: it ships as first-class middleware in `agent-framework-core`, is Python-only and explicitly experimental, and enforces before a sensitive tool runs. But linear information-flow control permanently taints a trajectory on a confidential read, which blocks the legitimate work that follows. Second, OpenAPPA does not reject model-backed components. An annotator, authority, or sanitizer can bind an external LLM, but it runs inside a declared mandate while the algebraic engine holds the global invariant. That is the composability difference: in an auto mode the classifier is the outer boundary and its hallucination is the breach; in OpenAPPA a model that errs cannot grant permissions beyond its contract.

## How do you install and run OpenAPPA?

The fastest path is the Claude Code integration, which the project describes as a playground for the model rather than the product:

```sh
curl -fsSL https://openappa.com/install.sh | sh &&
  ~/.local/bin/appa plugin install claude-code
```

That deploys the runtime binary, registers lifecycle hooks in your user-level Claude Code settings, adds the runtime's own `appa` MCP server, installs the `/appa-guide` onboarding skill, and installs `clappa`, the protected session launcher. Then:

```sh
clappa
```

```text
/appa-guide
```

The guide skill inspects your configured MCP servers and tools, matches batteries, asks focused questions where an identity or data boundary is ambiguous, and writes deterministic contracts after you approve them. Its failure mode during onboarding is fail-closed: unnamed tools route through a bounded fallback classifier until explicit contracts cover them. Protection belongs to the process, not the saved conversation, so a protected run must be resumed with `clappa --resume`, and a project configured with `disableAllHooks: true` disables enforcement entirely.

Under the hood the integration intercepts Claude Code's lifecycle events (SessionStart, UserPromptSubmit, PreToolUse, PostToolUse, plus subagent events) and passes each call to the local runtime before execution. Unanswered hooks fail closed. For a separate runtime process, the service defaults to `http://127.0.0.1:8787` and exposes `POST /hook` and `/mcp` for decisions, `GET /health`, `/status`, `/binary-fingerprint`, `/policy-key`, and `POST /reload` for operations, with the append-only trajectory event log persisted to SQLite through `--db ./appa.db`. Management endpoints accept local requests only, and no agent may approve its own blocked call: the model can only request that the runtime execute an offered remedy plan.

## What does a first appa.toml policy look like?

The smallest complete demonstration of confidentiality enforcement is the HR example from the validation docs. An agent reads files and sends email; after it reads an HR file, the policy must block email to an outside recipient while still allowing email to HR.

```toml
[externals]
timeout_ms = 2000
max_body_bytes = 65536

[policy]
version = 2

[[policy.tool]]
name = "mcp/files/read(path:/hr/*)"
delta = { audience = ["hr@archestra.ai"] }

[[policy.tool]]
name = "mcp/mail/send"
requires = { audience = { contains = ["$to"] } }
delta = {}
```

The read's `delta` restricts the trajectory's audience to the HR reader; the send's `requires` checks that its recipient is already in that audience. A customer-support variant adds the recovery machinery: tickets tagged `support` carry `delta = { audience = ["internal"] }`, a sanitizer with `permits.audience = { from = ["internal"], to = ["public"] }` can clean them for wider sharing, and an authority with `permits.audience_missing = ["public"]` lets a human approve one specific external share.

## How do you test policy in CI with appa describe --check and appa replay?

This is the most underrated part of the story, because most agent-security advice is unfalsifiable and this is not. `appa describe --check` verifies that the configuration loads and reports the tool inventory, batteries, and validation results. `appa replay` checks scripted tool calls against the decisions you expect without running any tools at all:

```text
mcp/files/read {
  path: "/hr/salaries.csv"
}
expect allow

mcp/mail/send {
  to: "x@other.com"
}
expect deny

mcp/mail/send {
  to: "hr@archestra.ai"
}
expect allow
```

All three calls share one trajectory: after the read, only HR remains in the audience. Replay supplies an empty result for the read, so no CSV file and no email account are needed. Wire both commands into a required GitHub check and a policy change that lets the outside recipient through fails the pull request:

```yaml
- name: Check policy decisions
  shell: bash
  run: |
    appa describe --config appa.toml --check
    appa replay --config appa.toml policy-tests/
```

The same discipline handles MCP supply-chain risk. A battery is a reusable, vetted policy configuration for a tool set such as Slack MCP or Claude Code's built-in tools, shipped with the annotators, sanitizers, and authorities it needs. Only the root `appa.toml` may use `include`, root rules run before battery rules, and the first match wins, so a root can override one issue or one channel while the battery files stay unchanged. The shipped GitHub battery is the best illustration: its annotator calls the GitHub API to check whether a repository is private before deciding the audience, which is exactly the per-server policy review that a registry census showing 51.1% of multi-version servers changing their advertised capabilities argues you should not skip.

Deployment is deliberately layered too. You can embed the APPA runtime in your own agent through the Python binding or Rust runtime, connect an existing harness through lifecycle hooks that can block a call and withhold or replace its result, or apply policies centrally at the LLM proxy layer through Archestra's 1.4 release candidate across Claude Code, Cursor, Codex, Copilot CLI, n8n, and anything else that talks to a model through its proxy.

## What are the limitations, and when should you not use OpenAPPA?

Be as precise about the limits as the vendor is:

- **It is a preview and an RFC.** Five releases shipped in three days at the end of September 2026; the config and wire surfaces may break without shims. The repository sat at 808 stars and 17 open issues at the time of research, and it is one company's project, not a committee standard, even with a NeurIPS 2026 Workshop paper behind it.
- **Enforcement costs tokens and completion.** 2.3x to 6.5x reported tokens against a permissive policy in the attack suites, and 75% task completion where auto configurations reached 85-96% in the single-run head-to-head.
- **Static contracts cannot see authorship.** A static contract assumes that anyone who can write to a source did, so a public repository issue enters the trajectory as suspicious until an annotator decides per call from reported authors.
- **A member account an attacker controls sits outside the model.** The trust model asks who wrote the text, not whether a legitimate identity was compromised.
- **Policy cannot express arbitrary business rules.** That is OPA's strength and a deliberate non-goal here.
- **It is one layer.** OpenAPPA does not sandbox execution, broker credentials, or scope identities.

Do not adopt it if you need a mature, freeze-able API surface this quarter, if your agents are single-turn with no external data flow, or if you cannot staff the policy review that gives the contracts meaning. Do adopt it if you have agents reading private data and writing outward.

## Where does a data-flow engine fit in a defense-in-depth stack?

Two vendors answered the same summer from two different layers, and they compose rather than compete. Nvidia's Open Agent Safety Platform, announced September 28, 2026 after disclosures in which agents from OpenAI, Anthropic, Meta, and Google broke out of test environments, puts each agent in a kernel-isolated sandbox with deny-by-default permissions and credentials brokered rather than handed over, then adds a policy prover that checks whether a fleet's combined permissions can compose into something the operator never intended, with Sentry correlating telemetry on separate hardware to quarantine a rogue agent in milliseconds. That layer restricts what an agent may touch. A flow policy restricts where data it has already read may go.

Everything else still applies. Scope each agent's identity and tools, as covered in our [least-privilege architecture guide](/posts/secure-ai-agents-least-privilege-2026/). Map your exposure against the [OWASP Top 10 for Agentic Applications](/posts/owasp-top-10-agentic-applications-2026/), and read the hijacking-specific analysis in [agent goal hijacking and OWASP agentic risk](/posts/agent-goal-hijacking-owasp-agentic-risk-2026/). Treat MCP servers as an inventory problem, not a config file, per the [MCP security guide](/posts/mcp-security-guide-2026/). Keep your repository-level defenses in place too: [prompt-injection defenses for clean repos](/posts/clean-repo-prompt-injection-defense-guide-2026/) and [repository scanners](/posts/promptshield-repo-prompt-injection-scanner-2026/) catch different bugs than a flow engine does, and the [agent skills supply chain](/posts/agent-skills-supply-chain-security-guide-2026/) is its own attack surface.

Use Simon Willison's lethal trifecta and Meta's Rule of Two as the design heuristic: an agent that combines private data access, untrusted content, and external communication is dangerous, and holding at most two per session removes the risk entirely. When you cannot cut a leg because the workflow genuinely needs all three, a deterministic flow engine is the enforcement point that holds.

## FAQ

### What is OpenAPPA in one sentence?

OpenAPPA is an MIT-licensed, Rust-based deterministic security engine that sits between an agent and its tools, labels what the agent has read as audience x trust, and checks every tool call against declarative TOML contracts before dispatch, returning remedy plans instead of bare refusals.

### Is OpenAPPA the same as OPA or Cedar?

No. OPA, Cedar, and Dogwood are general-purpose policy engines that give you allow-or-deny decisions over context your application supplies, and they can express arbitrary business rules that OpenAPPA deliberately cannot. The difference is state: OpenAPPA tracks the agent's action history and carries data restrictions forward between calls, and it returns recovery options rather than only a verdict.

### Does OpenAPPA replace prompt-injection detection tools?

It complements them. Detectors classify content and can be wrong, which is fine when their verdicts are advisory; OpenAPPA wraps them. A model-backed annotator, authority, or sanitizer runs inside a declared mandate, so a third-party scanner that errs cannot grant permissions beyond its contract, and the information-flow engine keeps the global invariant regardless of what the model concludes.

### What does OpenAPPA cost in tokens and task completion?

Its vendor reports 4.22% token overhead on Tau Bench's banking tasks, but 6.5x the tokens of a permissive policy on Bench-Corp and 2.3x on AgentThreatBench in the attack suites, because isolated child trajectories and recovery run on top of the task. Task completion was 88-90% on Bench-Corp against FIDES's 37-45%, but 75% in the single-run head-to-head where auto-mode configurations reached 85-96%.

### Is OpenAPPA production-ready in 2026?

Not in the sense of a frozen interface. The project labels itself a preview and an RFC, and config and wire surfaces may break without shims, with five releases in three days at the end of September 2026. What is production-shaped is the practice around it: declarative TOML, `appa replay` policy tests as a required merge check, and a local runtime that fails closed when it cannot answer.
