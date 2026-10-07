---
title: "Sprix Sage Router: State-Aware SELF/COLLABORATE/HANDOFF Routing for A2A Agent Routing"
date: 2026-10-01T08:52:28+00:00
tags:
  - a2a
  - agent-routing
  - multi-agent-systems
  - agent-orchestration
  - python
  - task-scheduling
description: "A2A agent routing decides whether an in-flight task continues, recruits peers, or hands off. How the Sprix SAGE router works, with real output."
draft: false
cover:
  image: "/images/sprix-sage-router-a2a-agent-routing.png"
  alt: "Sprix Sage Router: State-Aware SELF/COLLABORATE/HANDOFF Routing for A2A Agent Routing"
schema: "schema-sprix-sage-router-a2a-agent-routing"
---

A2A agent routing is the runtime decision of who should execute a task after the handshake: keep it with the incumbent (SELF), keep the incumbent as owner and recruit peers for uncovered requirements (COLLABORATE), or transfer ownership entirely (HANDOFF). The A2A protocol standardises discovery and transport; a router supplies the missing policy layer.

That is the short answer. The rest of this guide is the part that actually decides whether the router helps or hurts: what a state-aware utility function prices, why the honest benchmark signal is wasted work rather than the utility column, and the mode mix behind those numbers — SELF rising from 20% to 42% of decisions while HANDOFF falls from 66% to 44% — which shows that checkpoint awareness mainly teaches a router to leave a task where it is.

## Why Is A2A Discovery Not Enough for Agent Routing?

Google launched the Agent2Agent (A2A) protocol on 9 April 2025 with more than 50 technology partners, including Atlassian, Box, Cohere, Intuit, LangChain, MongoDB, PayPal, Salesforce, SAP, ServiceNow, UKG and Workday ([Google Developers Blog](https://developers.googleblog.com/en/a2a-a-new-era-of-agent-interoperability/)). On 23 June 2025 the Linux Foundation announced the Agent2Agent project, seeded by Google's transfer of the specification, SDKs and developer tooling, with AWS, Cisco, Google, Microsoft, Salesforce, SAP and ServiceNow as founding members and more than 100 supporting companies ([Google Cloud donation post](https://developers.googleblog.com/en/google-cloud-donates-a2a-to-linux-foundation/)).

A2A v1.0.0 shipped on 12 March 2026 as the first stable production-ready release, and v1.0.1 followed on 28 May 2026. In August 2026 the protocol was accepted as a Growth Stage project at the Agentic AI Foundation, operating under Linux Foundation-directed governance alongside MCP, goose and AGENTS.md, backed by over 150 organisations ([AAIF announcement](https://a2a-protocol.org/latest/blog/2026/08/27/a-new-chapter-for-a2a-joining-the-agentic-ai-foundation/)). The reference `a2aproject/A2A` repository stood at 25,976 stars and 2,639 forks on 1 October 2026, with 265 open issues (GitHub REST API, Apache-2.0).

Every one of those milestones solved the same class of problem: a directory problem. A2A tells you which agents exist, what they claim to do, and how to reach them. It does not tell you who should do the work — and it certainly does not tell you what to do when a task is already half finished and the incumbent turns out to be the wrong specialist. That second question is a scheduling question, and scheduling is exactly what the protocol leaves to you.

## What Does the A2A Protocol Actually Standardise?

A2A v1.0 is layered, and knowing which layer owns what prevents a lot of wasted architecture debate. Layer 1 is the canonical data model as Protocol Buffer messages, where `spec/a2a.proto` is the single authoritative normative definition. Layer 2 is the abstract operations. Layer 3 is the protocol bindings: JSON-RPC, gRPC and HTTP+JSON/REST.

The practical details that matter for a router:

| A2A element | What it gives you | What it does not give you |
|---|---|---|
| Agent Card at `/.well-known/agent-card.json` | Declared skills, capabilities, security requirements, provider info | Measured reliability per requirement |
| JSON-RPC 2.0 over HTTP(S) + SSE | Message transport and streaming | Any statement of who should be called |
| REST binding (`application/a2a+json`, `POST /message:send`) | HTTP-native integration path | Task ownership semantics |
| Task lifecycle (submitted → working → terminal) | Progress vocabulary; the caller must emit a terminal event | Automatic re-planning when progress stalls |
| `A2A-Version` header service parameter | Version negotiation and extension handling | Routing policy versioning |

The Agent Card URI was renamed from `agent.json` in v0.3 and is a permanent RFC 8615 well-known URI. Streaming uses Server-Sent Events, and webhook push notifications cover long-running work. What the protocol never defines is the decision of *which* card in that directory should own an in-flight task — which is why "A2A connected the agents, now someone has to route them" became the standard framing within weeks of the v1.0 release.

## What Is the Sprix Sage Router?

Sprix SAGE Router (`wang2122/sprix-sage-router`) is an MIT-licensed, early-stage research preview that reframes agent routing as a **stateful scheduling problem**. "SAGE" stands for State-Aware Graph Exchange: the router reads the current execution state of a task, filters the candidate roster, and returns a routing decision plus a transport-neutral plan.

Its provenance, verified against the GitHub REST API on 1 October 2026:

- Created 18 August 2026; v0.1.0 published the same day and v0.3.0 on 28 August 2026
- 4,261 stars, 186 forks, 181 watchers, 8 contributors, 43 commits, 2 open issues
- MIT licence, Python 3.10+, **zero runtime dependencies**
- Last push 2026-08-28

That star figure moves fast enough to be a lesson in itself. Independent articles published within days of launch quote about 677 stars (22 August), 3,456 stars and 401 forks (5 September) and 3,814 (7 September). Two of the three mainstream write-ups also quote pre-release benchmark tables that no longer match the v0.3 numbers. **Always date a number**, and prefer the API figure over a blog's cached widget.

One installation fact you should not get wrong: as of 1 October 2026 PyPI returns 404 for `sprix-sage`, `sprix-sage-router` and `sprix-a2a`. The only install path is `git clone`. If an article tells you to `pip install` it, that article is guessing.

## SELF vs COLLABORATE vs HANDOFF: Which Route Wins?

The three routes share one utility function, so the choice is a comparison rather than a hard-coded state machine. That matters more than it sounds: a three-branch state machine with hand-tuned thresholds cannot express "recruiting two peers is worth it here but not there."

| Route | What happens | The mechanism that justifies it |
|---|---|---|
| **SELF** | The incumbent keeps the task | Its estimated success, adjusted for the work already completed, beats every alternative once redo and transfer costs are priced |
| **COLLABORATE** | The incumbent stays owner; peers join to cover missing requirements | Marginal requirement coverage exceeds the coordination overhead of extra participants |
| **HANDOFF** | A peer takes full ownership | The specialist advantage outweighs the discarded work, the context-transfer loss and any deadline impact |

The design judgement worth stealing is that **a router needs an explicit reason not to recruit**. Every added participant adds messages, dependencies, conflicting estimates, and an attribution problem when the task eventually fails. COLLABORATE is not a free upgrade over SELF; it is a purchase with a price attached.

## How Does Checkpoint-Aware Routing Change the Decision?

This is where the project's own numbers get genuinely interesting, and where every existing article stops short. In a 1,000-checkpoint, five-seed trajectory replay, the checkpoint-aware router was compared against a progress-masked variant — identical except that it cannot see how much of the task is already done.

The headline utility gap is *not* the story:

| Policy | Utility | Wasted work | Switch rate | Deadline miss |
|---|---|---|---|---|
| Progress-aware SAGE | 0.298 ± 0.021 | 0.059 | 58.4% | 23.3% |
| Progress-masked SAGE | 0.291 ± 0.021 | 0.104 | 80.1% | 23.6% |
| Always-continue | 0.085 | — | — | 34.4% |
| Always-handoff | 0.290 | 0.130 | — | — |
| Hidden-state dynamic oracle | 0.375 | — | — | 19.6% |

The two utility error bars overlap (0.298 versus 0.291), so the utility column proves almost nothing. The real signals are 43% less wasted work (0.104 → 0.059) and a switch rate falling from 80.1% to 58.4%.

The mode mix explains the mechanism, and this breakdown is not published in the project README:

| Policy | SELF | COLLABORATE | HANDOFF |
|---|---|---|---|
| Progress-aware SAGE | 416 (42%) | 142 (14%) | 442 (44%) |
| Progress-masked SAGE | 199 (20%) | 136 (14%) | 665 (66%) |
| Hidden-state dynamic oracle | 100 (10%) | 379 (38%) | 521 (52%) |

Checkpoint awareness roughly doubles the decision to stay put and cuts handoffs by about a third. Collaboration barely moves — 14% either way. The lesson is not "add more agents"; it is that knowing what is already finished mostly teaches the router to leave well enough alone.

Note also how the oracle behaves: it is the **most handoff-happy** policy in the comparison, choosing HANDOFF 52% of the time and SELF only 10%. Better information does not automatically mean keeping the incumbent — it means not confusing the two decisions.

A controlled intervention confirms the causality. Holding task, agents, difficulty, artifact portability, budget and deadline fixed while sweeping in-flight completion from 0.0 to 0.9, progress-aware minus progress-masked utility climbs monotonically from **+0.0000 to +0.0684**, and the two policies are identical at zero completion. When there is no work to preserve, checkpoint awareness is worth exactly nothing.

## What Goes Into the SAGE Utility Function?

The utility is predicted success minus a set of priced costs, with uncertainty and exploration terms on top:

- **Predicted success**, from calibrated per-agent, per-requirement estimates rather than one blanket reputation score
- **Direct cost** — the provider's quote for the work
- **Critical-path latency**, not just total latency
- **Risk**, including deadline and budget exposure
- **Context-transfer loss** — the part of the current artifact that a new owner cannot actually reuse
- **Coordination overhead** — the message, dependency and estimation cost of every extra participant
- **Uncertainty and exploration** terms, so the router can buy information

The key reuse rule is that estimated reuse is the completed fraction multiplied by **artifact portability**, plus observed partial quality. A checkpointed artifact that only its author's framework can read is worth almost nothing to a new owner, no matter how complete it is. That is why artifact portability is a first-class parameter and not a footnote: it is the difference between a handoff that resumes work and a handoff that starts over.

Crucially, **hard filters run before any scoring**. Permissions, availability and failure state are applied first; a high learned score can never override them. A ranking model that recommends an agent which cannot meet a security requirement is not a slightly worse router — it is a broken one.

## Why Is One Reputation Score Per Agent Not Enough?

Because reputation does not transfer across skills. An agent that is reliable at schema migration may be unreliable at security review, and a single reputation number averages the two into a figure that is wrong for both.

The project tests this directly. Tracking trust per agent **per requirement** beat a single score per agent after 500 observations per seed in a heterogeneous specialist setting:

| Method | Brier score | Selection regret |
|---|---|---|
| Per-agent, per-requirement trust | 0.0125 ± 0.0018 | 0.0094 ± 0.0008 |
| One reputation score per agent | 0.0355 ± 0.0008 | 0.0310 ± 0.0359 |

The negative control is the part that earns trust in the benchmark: in a **homogeneous** setting where specialisation is absent, both methods show zero routing regret. The study does not manufacture an advantage that the setup cannot support. That is a rarer virtue in routing benchmarks than it should be.

The same principle governs team scoring. Coverage moved from a noisy-OR over every selected teammate to **assigned-owner, checkpoint-adjusted coverage** — because crediting the team for every skill anyone on it happens to possess is how you end up with four impressive agents and one unfinished task.

## How Do You Go From an Agent Card to an ExecutionPlan in Python?

The repository ships a demo that runs with no dependencies at all. Clone it and run `demo.py`:

```
mode=collaborate
agents=incumbent-planner, security-reviewer, code-specialist
utility=0.673  p(success)=0.859  cost=0.139  latency=1297 ms
```

That is the whole "run it yourself" argument in four lines: a real COLLABORATE decision with a real utility number, no API keys, no model calls, no package install.

The adapter path is `profile_from_agent_card(...)`, which converts an A2A Agent Card into the capability vectors, permission constraints and provider metadata the router needs. The mapping is direct: `AgentCard.skills` becomes capability vectors, `securityRequirements` becomes hard permission filters, and provider quotes become structured bids.

The shape of the state you pass in is what makes it state-aware:

```python
state = ExecutionState(
    inflight_owner="generalist",
    inflight_completion=0.6,
    inflight_quality=0.71,
    artifact_transferability=0.4,   # how much a new owner can actually reuse
    deadline_s=900,
    budget=1.0,
)
```

Run against the bundled example, that plan emits `mode=collaborate` with utility 0.7229, success 0.8852, coverage 0.6966, cost 0.09416, latency 1005.7 ms, `feasible=true` and an empty `constraint_violations` list. Note that `examples/` requires `PYTHONPATH=<repo root>` (or an installed package) — otherwise the import fails and you will wrongly conclude the example is broken.

The replanning example is the clearest demonstration of the whole thesis:

```
initial:  self    -> ('generalist',)
replan after recorded failure: handoff -> ('specialist',)
```

One recorded failure flips the decision from SELF to HANDOFF. That is checkpoint-aware rerouting in two lines, and no article in the current top results actually shows it.

The repo's unit tests run in about a second (`python -m unittest -q` → 46 tests, OK), which makes it a reasonable read: small enough to audit, structured enough to extend.

## How Is the Benchmark Built — and What Does It Actually Show?

Three synthetic studies sit behind the numbers. All three are project-authored, and the project says so.

**1. Dynamic trajectory replay (1,000 checkpoints, 5 seeds × 200, evaluator `checkpoint_artifact_v1`)** — the source of the utility, wasted-work and switch-rate table above. Running it locally reproduces every README figure to three decimals and prints its own scope string: *"synthetic falsification study; not evidence of production or real-endpoint superiority."*

**2. Trust convergence (500 observations per seed)** — the Brier and regret table above, with the homogeneous negative control.

**3. Independent-task regression suite (2,500 tasks)** — a quality comparison across routing policies:

| Policy | Quality |
|---|---|
| Learned SAGE | 0.613 ± 0.005 |
| Greedy team | 0.577 |
| Static SAGE | 0.491 |
| Learned SAGE with random prior | 0.447 |
| Advertised-skill solo | 0.445 |
| Incumbent-only | 0.332 |

Two things stand out. The gap between learned and greedy is real but modest — about 3.6 points. And swapping the prior for a random one costs 16.6 points, which means **the learned prior does most of the work**. If your priors are wrong, the router is not much better than a coin with an opinion.

Latency is bounded but environment-specific. The README reports a median of 78.4 ms at 20 agents, 78.9 ms at 40 and 80.1 ms at 80 on one Apple Silicon machine. Re-running the scaling benchmark on container CPU produced 23.27 ms at 5 agents and roughly 250 ms at 20, 40 and 80 — about three times slower in absolute terms, but **flat from 20 to 80 agents**, which reproduces the bounded-prefilter claim rather than the absolute numbers. The prefilter caps candidates (default `candidate_limit=12`), so per-request routing cost does not scale with roster size.

Read that honestly and the conclusion is: the design is rigorous, the numbers are not evidence of real-world superiority, and the project is the first to say so. Its own evaluation boundary states that both evaluators are authored with the project, and that a publishable evaluation still requires repeated checkpointed executions on heterogeneous real endpoints plus an independently governed artifact judge.

## What Does the Prototype Deliberately Not Do?

It returns a routing decision and a plan. It does not execute anything:

- No task transmission (`message/send` is yours to call)
- No endpoint authentication, no signature verification
- No streaming, polling or cancellation
- No artifact handling or evaluation
- No idempotency, secret isolation or human approval gates

The integration documentation puts the boundary bluntly: *do not treat a successful routing decision as a successful task execution.* An A2A client remains responsible for all of the above, and an independent directory review scored the project 69/100 — "some gaps" — listing "teams needing production A2A execution, auth or secure transport" as an explicit **not a fit**.

Related work in the same space sets useful expectations. STRMAC reports up to 23.8% improvement over baselines with up to 90.1% less data-collection overhead than exhaustive search (arXiv 2511.02200). Dynamic coalition formation with communication pricing reaches 99.5% of brute-force-optimal utility while activating 1.96 of 8 agents on average, against 38.8% for full broadcast — and degrades to 66% under strong submodularity violations or noisy value estimates (arXiv 2608.07532). Modality-native routing in A2A networks lifts task completion to 52% versus 32% for a text bottleneck at a 1.8× latency cost, but an ablation replacing LLM reasoning with keyword matching erases the gain entirely, 36% versus 36% (arXiv 2604.12213). That last ablation is the most useful warning in the set: the value lives in the reasoning, not the routing scaffold.

## When Is a State-Aware Router the Wrong Tool?

State-aware routing is not a default. Skip it when:

- **The workflow is short and deterministic.** If there is no meaningful mid-flight state, there is nothing to be aware of.
- **You have one agent.** Routing between one option and itself is a no-op with extra latency.
- **You have no calibrated outcome evaluator.** The checkpoint signal does not exist without one. The router reads completeness and quality; if you cannot observe artifact quality, the whole state input is fiction.
- **Your tasks are single-requirement.** No coverage gap means COLLABORATE has nothing to buy.
- **You need transport, auth or security guarantees.** Those are A2A client responsibilities, not router responsibilities.
- **Your routing regret signal is unobservable.** Outcome feedback currently cannot separate agent quality from task difficulty from the router's own prior choices. Without logged propensities and off-policy evaluation, learning can become self-confirming.

That attribution gap is the honest frontier here. Neither the project nor its reviewers have closed it, and until someone does, "the router got better" is a hypothesis rather than a measurement.

**A practical adoption checklist:**

1. Instrument completion, quality and artifact portability per checkpoint before you route on them.
2. Enforce permission, availability and failure-state filters **before** scoring — make hard filters unfalsifiable by any learned score.
3. Track trust per agent per requirement, not per agent.
4. Establish your incumbent-only baseline and your greedy baseline first. If learned routing does not beat greedy, stop.
5. Run the trajectory replay on your own traces rather than trusting the synthetic one.
6. Log propensities on every decision so off-policy evaluation is possible later.
7. Start in shadow mode: produce decisions, compare them to what your team already does, change nothing.
8. Keep an A2A client — authentication, streaming, cancellation, idempotency and human approval stay yours.

## FAQ: A2A Agent Routing

**What is A2A agent routing?**
It is the runtime decision of which agent or agent team should execute a task in an Agent2Agent network — covering who owns the task, who joins, and what topology connects them. A2A itself standardises discovery and transport; a router supplies the missing policy layer.

**Does the A2A protocol include a router?**
No. A2A v1.0 defines Agent Cards, messages, tasks, artifacts, authentication and transport bindings. It tells you which agents exist and how to reach them; it does not decide who should do the work after execution has started.

**What is the difference between SELF, COLLABORATE and HANDOFF?**
SELF keeps the task with the incumbent. COLLABORATE keeps the incumbent as owner and recruits peers to cover missing requirements. HANDOFF gives a peer full ownership. They share one utility function, so the choice is a comparison, not a hard-coded state machine.

**How do you decide when to hand off an in-flight agent task?**
Estimate how much of the current owner's work a new owner can actually reuse: completed fraction times artifact portability, plus observed partial quality. Then compare the specialist advantage against the redo cost, transfer loss, coordination overhead and any deadline or budget impact.

**Is Sprix SAGE Router production-ready?**
No. It describes itself as an early-stage research preview. It returns a routing decision and a transport-neutral plan but does not send tasks, authenticate endpoints, verify signatures, stream, poll or cancel. Production use needs an A2A client, calibrated evaluators, identity and signing, observability and human approval gates.

## Sources

- Sprix SAGE Router repository, README / ALGORITHM.md / docs/INTEGRATION.md / docs/OPERATIONS.md — https://github.com/wang2122/sprix-sage-router (verified 2026-10-01, commit bdc9c24)
- Agent2Agent (A2A) Protocol Specification v1.0.0 — https://a2a-protocol.org/latest/specification/
- A2A reference repository and release history — https://github.com/a2aproject/A2A (GitHub REST API, verified 2026-10-01)
- A2A joins the Agentic AI Foundation — https://a2a-protocol.org/latest/blog/2026/08/27/a-new-chapter-for-a2a-joining-the-agentic-ai-foundation/
- Google Cloud donates A2A to the Linux Foundation — https://developers.googleblog.com/en/google-cloud-donates-a2a-to-linux-foundation/
- A2A launch announcement, 9 April 2025 — https://developers.googleblog.com/en/a2a-a-new-era-of-agent-interoperability/
- STRMAC state-aware routing — https://arxiv.org/abs/2511.02200
- Dynamic coalition formation and communication pricing — https://arxiv.org/abs/2608.07532
- Modality-native routing in A2A networks (MMA2A) — https://arxiv.org/abs/2604.12213
- RouteLLM: preference-trained routing — https://arxiv.org/abs/2406.18665
- MasRouter: Multi-Agent System Routing — https://arxiv.org/abs/2502.11133
