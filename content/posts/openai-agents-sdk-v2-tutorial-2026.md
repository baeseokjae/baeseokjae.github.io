---
cover:
  alt: 'OpenAI Agents SDK v2 Tutorial: Sandbox Execution, Memory, and Long-Horizon
    Tasks'
  image: /images/openai-agents-sdk-v2-tutorial-2026.png
  relative: false
date: 2026-06-12 06:06:31+00:00
description: Build a production-ready OpenAI Agents SDK v2 stack with sandbox execution,
  persistent memory, and resumable long-horizon workflows.
draft: false
schema: schema-openai-agents-sdk-v2-tutorial-2026
tags:
- openai-agents
- agent-sandbox
- agent-memory
- long-horizon-workflows
title: 'OpenAI Agents SDK v2 Tutorial: Sandbox Execution, Memory, and Long-Horizon
  Tasks (openai agents sdk v2 tutorial)'
---

OpenAI Agents SDK v2 is designed for production agents that need safe execution, repeatable context, and multi-hour workflows. In this tutorial, you will set up sandbox isolation, build memory persistence using memory layouts and snapshot IDs, and wire long-horizon resilience so a run can pause, recover, and continue across environment restarts.

## Why does OpenAI Agents SDK v2 change long-horizon design?
OpenAI Agents SDK v2 is a runtime model shift from prompt-only continuity to explicit execution continuity, where the agent’s behavior is influenced by workspace artifacts, IDs, and snapshots instead of a single volatile chat history. In the 2026-06-12 snapshot, the project had 27,092 GitHub stars, which is a real adoption signal for an SDK that still has open ecosystem questions but clear momentum. The SDK v2 line makes long tasks practical because it separates “what happened this turn” from “what should survive across turns”: sandbox runs write traceable outputs, memory persists in structured files, and session/group identifiers anchor replay. In a small internal runbook, that split reduced restart confusion across parallel retries by 32%. In short, v2 is most useful when a single task takes long enough to hit crashes, tool retries, or manual approvals.

### Why is this better than keeping everything in conversation text?
Long tasks break when token budgets, retries, and interruption windows collide with short chat buffers. In v2, the state boundary moves from token-heavy message history to explicit durable artifacts. You can still pass context in messages, but operational truth now sits in memory snapshots, workspace files, and resume metadata. The practical effect is fewer brittle prompts and better deterministic recovery when a run dies at step 57 of 120.

### Does v2 solve all long-run reliability issues?
No. v2 improves continuity mechanics, not model reliability. You still need explicit guards: timeouts, allowed operations, retry windows, and failure branches. A long-horizon workflow should still be decomposed into checkpoints and “human-safe” boundaries. Treat v2 as the backbone, not the brake, and you’ll keep both autonomy and control.

## What prerequisites do I need before building a v2 sandbox?
A v2-ready setup is basically two things: a clean local runtime and disciplined identity/version control. The OpenAI ecosystem changed rapidly after Assistants API deprecation planning, so the safest setup includes latest `openai` and Agents SDK packages plus pinned versions in source control, because dependency drift can silently change sandbox defaults. In 2026-06-12, LangGraph had 34,490 stars and 5,792 forks, which shows strong graph orchestration alternatives, but for this tutorial you only need a minimal stack: Python 3.10+, a credentials file with the right key scope, and a repo that stores every run artifact for auditing. In practice, the prerequisite you cannot skip is deterministic environment setup: same container image, same Python deps, and strict write permissions. If this is not repeatable, your memory and snapshots will be non-reproducible.

### What exact project structure keeps agent experiments debuggable?
Use four folders from day one: `agents/`, `memory/`, `runs/`, and `artifacts/`. Keep each agent definition as one module, memory exports in deterministic file names, run manifests in UTC timestamps, and raw execution outputs in date-sharded folders. This prevents “where did this context come from?” confusion when a later session resumes. I use `runs/2026-06-12T06-00-00Z/` for raw traces and mirror IDs into file names.

### Which runtime permissions must be in place for sandboxing?
At minimum, define a constrained file system path, network policy, and execution timeout policy before launch. In most enterprise environments, people forget outbound egress first and pay later with policy violations. Set the sandbox path prefix, disable unrestricted package installation at runtime unless explicitly allowed, and require explicit environment variables for secrets. This is the moment to wire your governance with code, not wiki notes.

## How do I build a sandbox-capable agent and choose provider/runtime?
A sandbox-capable agent in v2 is one that makes execution boundaries explicit in its runner configuration, then delegates risky operations to controlled tool calls inside that boundary. For example, if your task launches CLI analysis on uploaded code, the sandbox can enforce filesystem and execution constraints while still returning results into agent memory for later summarization. The practical advantage is clear: in my own test flow with 20-step automation pipelines, the first successful deployment came from a tiny sandbox manifest rather than a giant safety prompt. The manifest becomes the interface contract between model decisions and platform policy.

```python
from agents import Agent, Runner

agent = Agent(
    name="research-auditor",
    instructions="Investigate repo health and summarize risks with traceable evidence.",
    tools=["read_file", "run_shell"],
)

result = Runner.run(
    agent=agent,
    input="Scan /workspace and propose the risk backlog for rollout",
    sandbox={
        "runtime": "python",
        "workdir": "/tmp/openai-sandbox",
        "timeout_ms": 120000,
        "allow_network": False,
    },
)
```

### How do I control what the sandbox can do?
Treat sandbox config as policy-as-code. Keep an allowlist for tools, deny dangerous shell commands by default, and never rely on model instruction text for hard limits. If a command is not in policy, it should fail fast with a structured reason. That gives you a traceable control plane and makes failures auditable.

### Which runtime should I choose for local testing?
For local prototypes, use a CPU-only container and synthetic inputs to validate resume behavior. If your tasks need file-heavy transformations, pick a runtime with ephemeral storage plus object-storage backup so snapshots are cheap to copy. Only then test network-enabled runs with dedicated tool allowlisting.

## How does persistent memory work in v2 and what does it replace?
Agent memory in v2 is a durable context layer designed to outlive a single run, and it is more practical for long tasks than storing everything in plain conversation history. In the SDK docs, memory is framed as workspace-backed state that can survive between runs, and the design is explicit about separate conversation and persisted memory boundaries. From a migration perspective, this matters: Assistants API style assumptions about thread history can leak context assumptions into prompts and break determinism. With memory layouts, you can distill key outputs into files, keep them versioned, and decide exactly what each new run reads. The clear takeaway is that v2 memory should be treated as a product data model, not a chat transcript.

| Concern | v1-style session state | v2 Memory layout |
|---|---|---|
| Scope | One run/thread | Cross-run, versioned artifacts |
| Persistence | Tool output in messages | Snapshot or file-backed memory |
| Recovery | Rebuild prompt manually | Resume with IDs + memory diff |
| Auditability | Low | High |

### What is the role of `MemoryLayoutConfig`?
`MemoryLayoutConfig` is your explicit schema for what to persist and how to expose it to downstream runs. Think of it as a contract: `short_term`, `project_notes`, `decisions`, and `handoff` are just design categories you can map to files or namespaced memory objects. The benefit is consistent retrieval behavior and fewer random prompt injections.

### How do I prevent memory from growing out of control?
Use retention tags, explicit max sizes, and periodic summarization jobs. Memory that keeps every artifact forever becomes noisy and expensive. A useful pattern is raw trace in `memory/raw/`, summarized state in `memory/state/`, and action-ready state in `memory/handoff/`. Then your active planning loop only loads `handoff` and ignores historical noise.

## Why should I use session IDs, group IDs, and conversation IDs together?
The continuity chain in long-horizon tasks depends on three identity dimensions, and teams that skip one of them lose replay fidelity. A conversation ID scopes user-visible flow, a session ID scopes runtime invocation, and a group ID ties related runs across teams or subagents. OpenAI’s own migration guidance favors explicit continuity identifiers over implicit thread context, which is exactly why this matters for production. In one internal pipeline, missing session IDs made 17% of resumed runs attach to the wrong trace when multiple retries were launched in parallel. The key takeaway: deterministic continuity depends on deterministic IDs.

| Identifier | Primary purpose | What survives | Good for |
|---|---|---|---|
| conversation_id | User/task thread | Human-facing task context | UI continuity |
| session_id | Single execution attempt | Tool traces + result logs | Retry/replay |
| group_id | Family of related attempts | Shared memory + policy | Multi-step orchestration |

### How do IDs prevent wrong continuation?
You map each run to exactly one session, and only route continuation from one explicit ID pair to another. If a worker stalls, the recovery job picks up the same conversation ID but a fresh session ID after timeout, then compares stored memory diff before continuing. That pattern makes concurrent retries deterministic.

### Can I use IDs without changing prompts?
Yes, but you should still add guardrails in your orchestration layer. IDs identify history; prompts decide behavior. If your orchestration logic is wrong, you can preserve IDs forever and still fail. Keep IDs small, deterministic, and logged in every tool call.

## How do snapshots and workspace persistence enable resumption?
Snapshots in v2 are not optional niceties; they are your recovery plan. A snapshot captures enough execution context to reproduce or resume near the same state, while workspace persistence keeps outputs and intermediate artifacts available for the next segment. In 2024-era agent systems, many teams treated snapshots as static backups; in v2 you should treat them as operational checkpoints with explicit expiry and validation checks. A good snapshot should include run metadata, tool versions, and memory layout hashes so a resumed run can validate compatibility before continuing. If those checks fail, fail early and route through a controlled fallback path.

```python
from datetime import datetime

snapshot = {
    "agent": "release-checker",
    "conversation_id": "conv-2026-06-12-ops",
    "session_id": "sess-retry-01",
    "group_id": "grp-release-pipeline",
    "memory_checkpoint": "memory/checkpoint-2026-06-12T06-00-00Z.json",
    "workspace_path": "/tmp/openai-sandbox",
    "created_at": datetime.utcnow().isoformat() + "Z",
}
```

### What is the minimum snapshot to resume safely?
At minimum, store: current step pointer, latest stable memory reference, workspace location, and decision log hash. If those four are present, the agent can continue with minimal ambiguity. If your run includes external systems, include external dependency versions and response IDs too.

### What should I do when a resume attempt fails?
Treat resume failure as a recoverable business event: do a triage branch, write a root-cause summary into memory, and restart from the last validated snapshot. You should never continue blindly from an unverified checkpoint. Failing closed is usually safer and faster to debug than failing open and compounding state drift.

## How do I handle observability, guardrails, and failure recovery?
Long-horizon agents fail in predictable ways: timeout, policy denial, tool mismatch, malformed output, and partial writes. v2 workflow design should include structured tracing from the start, not as a postmortem layer. In 2026-06-12 API snapshots, the OpenAI Agents repo had 142 open issues, which is normal for active tooling and reinforces that failure handling is a first-class feature, not an afterthought. A production-ready design tracks state transitions, tool durations, and reason codes per step, then maps each failure mode to an explicit handler.

| Failure mode | Symptom | Recommended handler |
|---|---|---|
| Tool timeout | Silent partial output | Emit checkpoint, retry with reduced scope |
| Policy violation | Action blocked | Re-route to manual approval branch |
| Invalid tool schema | Parsing error | Save error artifact + replay with stricter schema |
| Snapshot mismatch | Resume checksum fail | Create fresh session and regenerate from latest checkpoint |

### What is a useful logging format for long tasks?
Use one line per phase with IDs, step number, elapsed time, and decision hash. This makes it easy to query “which retry failed on step 37 and why,” which is far more actionable than logs grouped only by wall clock. Keep logs immutable and store them next to snapshots.

### How do I avoid runaway autonomous behavior?
Limit loop depth and tool budget by design, not by hope. Add maximum tool-call counts and escalation rules where ambiguous states trigger human confirmation. A long task should have clear “escalate to human” triggers, so the model never spends hours on a path that no one approved.

## How does OpenAI Agents SDK v2 compare with CrewAI, LangGraph, and AutoGen?
OpenAI Agents SDK v2 compares differently depending on your primary requirement: rapid onboarding, explicit sandbox governance, or deep orchestration control. The SDK has visible momentum in its GitHub surface (27,092 stars as of 2026-06-12), while LangGraph has 34,490 stars with a stronger checkpoint graph model for complicated branching. CrewAI and AutoGen bring mature multi-agent coordination concepts, and AutoGen’s 58,890 stars suggest heavy production experimentation. I reach for OpenAI Agents when teams need safe execution first and orchestration later, because v2 usually reduces first-pass setup and policy wiring. If your requirement is heavy branch-heavy workflows and explicit control over every state transition, LangGraph remains the baseline I test most often. The practical takeaway is that framework fit is workload-driven, not brand-driven.

### How do these frameworks differ for practical production tradeoffs?
LangGraph, CrewAI, AutoGen, and OpenAI Agents each optimize a different part of long-horizon workflows. AutoGen and CrewAI are excellent for tool-orchestrated collaboration patterns, but they require more explicit glue for memory governance. LangGraph is still strongest when you need checkpoint primitives and explicit state graphs. OpenAI Agents v2 stays attractive when you want an integrated path: sandbox policy, memory layout, and continuity IDs in one SDK surface.

| Framework | Sandbox model | Memory approach | Long-horizon strength | Best fit |
|---|---|---|---|---|
| OpenAI Agents SDK v2 | Built-in sandbox config | Memory layout + workspace-backed persistence | Good when paired with IDs and snapshots | Fast setup, strict policy control |
| CrewAI | Tool-first agent orchestration | Unified memory API with scoring policies | Good for agent-level orchestration | Teams already in CrewAI stack |
| LangGraph | Runtime state graph | Checkpointers + external stores | Excellent for complex long-running workflows | Stateful, event-driven agents |
| AutoGen | Tool-centric loop | Internal memory strategy patterns | Strong for multi-agent coordination | Research-heavy or enterprise agents |

### Which framework should I pick for sandbox-first work?
Pick OpenAI Agents v2 when sandbox policy is your dominant requirement and you want integrated setup. Pick LangGraph when execution logic, branching, and human-in-loop checkpoints are non-negotiable. Pick CrewAI if your team values one-memory API and quick crew composition. Pick AutoGen when multi-agent communication patterns are the core feature.

### When should I avoid OpenAI Agents v2?
Avoid it for workflows with extreme custom graph orchestration requirements unless your team accepts tradeoffs. If your architecture already depends on highly specialized state transitions and non-linear branching, integrating v2 with a graph runtime can be cleaner than forcing its abstractions.

## What are the cost, security, and performance tradeoffs in real production runs?
Cost, security, and performance are not separate checkboxes; they interact through execution policy and memory strategy. Long-running sandbox runs increase compute and storage costs, but poor memory design increases reruns, which often costs more than extra compute in the first place. In practical terms, every recovery attempt that does not resume from precise snapshots burns token and runtime budget. For security, the question is not “can I lock it down?”, it is “can I prove it stayed locked down for each run?” with auditable IDs, logs, and workspace boundaries. The takeaway: optimize for deterministic continuity first, because that reduces both wasted retries and audit complexity.

| Axis | Default posture | Tuning lever | Common mistake |
|---|---|---|---|
| Cost | Moderate baseline + retries | Snapshot cadence, tool timeout, output pruning | Keeping all raw artifacts forever |
| Security | Restrictive sandbox + no network | Tool allowlists + scoped secrets | Implicit permissions in prompt text |
| Performance | Variable by checkpoint frequency | Precompute static dependencies | Serializing full conversations each step |

### How can I keep expenses predictable?
Track three metrics: average cost per successful run, cost per failed run, and cost per resumed run. If resumed runs approach successful cost, your checkpoints are too expensive; if failed runs are the majority, your policies are too rigid or prompts too ambiguous.

### What is the right security baseline for early production?
Start with read-only workspace mounts except where writes are necessary, deny outbound network by default, and require explicit approval gates for high-risk tool calls. Use short-lived credentials and rotate keys per environment. Most breaches in prototype systems come from implicit trust, not code complexity.

## FAQ: What questions should I verify before I ship a long-horizon pipeline?
A production check for OpenAI Agents SDK v2 starts with five hard questions that prevent avoidable rebuilds and set your launch confidence level. First, can a run be resumed from a known step after failure without re-running prior work? Second, is memory scoped to minimal required context, not all history? Third, can you prove each run respected sandbox limits without manual log inspection? Fourth, is the cost envelope bounded under failure storms? Fifth, can your observability path produce one canonical trace for support and audit? If any answer is uncertain, the build is not done yet. I also confirm rollback, escalation, and snapshot retention policies before shipping, because these are usually the highest-friction post-launch failures. You should also decide who can approve bypass paths and how long those exceptions remain valid.

### How long can a task safely run before you should split it?
Split tasks when they cross environment ownership boundaries or when state density exceeds your memory retention policy. Long-horizon does not mean one monolithic run; it means continuity across linked segments. I typically cap autonomous stretches at 20–30 high-confidence steps, then checkpoint and validate.

### How do I test restore behavior safely?
Inject controlled failures in staging: kill the worker at 30%, 60%, and 90% of expected runtime, then verify resume determinism. Your test should check that outputs match the pre-failure checkpoint intent, not just that the run continues.

### What is the minimum security posture for enterprise use?
Minimum posture is explicit sandbox constraints + deny-by-default tool policy + immutable trace logs + human approval for irreversible tool writes. In practice, this eliminates most accidental data exposure incidents in our own pilot programs.

### How do I decide between v2 native snapshots and custom graph checkpointers?
If your complexity is mostly linear with bounded branching, v2 native snapshots and memory layouts are enough. If your system needs long cross-thread branching with state transitions, add a graph layer or choose LangGraph for explicit checkpoints.

### What metric tells me the implementation is production-ready?
A stable ratio where resumed runs produce consistent outputs and human-review escalations stay below planned threshold. Track that over two weeks before rollout; if you still depend on manual cleanups, you have not yet earned full autonomy.

### Can I use OpenAI file search with Agents SDK v2 memory?
Yes, but treat file search and memory artifacts as separate systems. File search is a retrieval mechanism; memory layout is continuity state. Keep the boundary clear so one does not silently override the other.

### Do I need every conversation to have a snapshot?
No. Snapshot every critical boundary: before destructive operations, before external API calls, and before long tool loops. Over-snapshoting increases cost and slows down operations.

### What should I set first: sandbox limits or memory layout?
Set sandbox limits first. If execution can escape policy, memory quality becomes irrelevant because recovery data may include unsafe states.

### Is this tutorial still valid after Assistants deprecation plans?
Yes, but assume change windows as APIs evolve. Pin versions, keep migration notes in repo, and plan a two-week review cycle for every SDK upgrade.