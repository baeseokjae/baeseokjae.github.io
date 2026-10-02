---
title: "A2A Routing Agents: State-Aware Mid-Execution Routing with Sprix SAGE Router"
date: 2026-10-01T00:33:08+00:00
tags:
  - a2a routing agents
  - state-aware routing a2a
  - sprix sage router
  - mid-execution rerouting agents
  - agent handoff vs collaboration
  - checkpoint-aware agent routing
description: "A2A routing agents pick who works after execution has started. A hands-on guide to the Sprix SAGE router, its three modes, and its benchmark limits."
draft: false
cover:
  image: "/images/a2a-agent-network-routing-sprix-sage.png"
  alt: "A2A Routing Agents: State-Aware Mid-Execution Routing with Sprix SAGE Router"
  relative: false
schema: "schema-a2a-agent-network-routing-sprix-sage"
---

A2A routing agents decide which agent configures, owns, or continues an in-flight task once execution has already begun. The Sprix SAGE Router is a dependency-free Python reference implementation of that policy: it compares SELF, COLLABORATE, and HANDOFF under permission, budget, and deadline constraints, and returns an auditable trace. Its own trajectory replay shows progress-awareness mainly buys restraint — wasted work falls from 0.104 to 0.059 and the switch rate from 80.1% to 58.4%, while utility stays inside overlapping error bars.

That is the honest headline, and it is more interesting than the marketing version. We cloned the repository, ran its demo, its examples and its 46-test suite, and reproduced a routing flip on our own machine. This guide covers what the router actually is, how its utility function works, what the benchmark does and does not prove, and the integration work it deliberately leaves to you.

## Why A2A Discovery Is Not Enough

The Agent2Agent protocol solved a directory problem and, in doing so, made a runtime problem visible. Google launched A2A in April 2025; the Linux Foundation took over the project on 23 June 2025 with support from more than 100 technology companies, and A2A Protocol v1.0 — the first stable production-ready version — shipped on 12 March 2026. On 27 August 2026 A2A was accepted as a Growth Stage project at the Agentic AI Foundation. The reference `a2aproject/A2A` repository passed 25,977 stars and 2,638 forks in that period [Linux Foundation](https://www.linuxfoundation.org/press/linux-foundation-launches-the-agent2agent-protocol-project-to-enable-secure-intelligent-communication-between-ai-agents), [A2A blog](https://a2a-protocol.org/latest/blog/), [GitHub API](https://github.com/a2aproject/A2A).

What the specification gives you is a way to describe agents and move work between them: Agent Cards at `/.well-known/agent-card.json`, JSON-RPC 2.0 over HTTPS, SSE streaming, push notifications, and a task lifecycle that runs `submitted → working → terminal` with a hard rule that a caller waits forever if no terminal event is emitted [a2a-protocol.org specification](https://a2a-protocol.org/latest/specification/). What it does not give you is any statement about **who should be working on the task after the handshake is done**. That omission is structural, not an oversight: a protocol can standardize message shapes and lifecycle events, but it cannot know that the incumbent agent has finished two thirds of a dependency DAG and is about to spend an hour redoing work another agent could reuse.

The practical symptom shows up as a familiar operations question. A task has been running for twenty minutes. The executing agent is mediocre at the one requirement it has not started yet. A specialist exists and is idle. Do you let it finish, bolt a teammate on, or move the whole task? Most frameworks answer this with a static decision made before the first token: pick a team, then live with it. The runtime question — ownership transfer after progress exists — is where routing agents earn their name.

Three different things get called routing, so disambiguate before choosing tooling. **Model routing** picks which LLM answers a prompt (RouteLLM and friends). **Provider routing** picks which endpoint or vendor serves the request (gateways, load balancers, price arbitrage). **Agent routing** picks which agent owns a task and in what configuration. SAGE only does the third, and only over a task that is already in flight. If you arrive from an LLM-gateway search, you are in the wrong section of this article.

The academic version of the same problem is also live. STRMAC, described in [arXiv 2511.02200](https://arxiv.org/abs/2511.02200), is a state-aware routing framework that separately encodes interaction history and agent knowledge and selects the most suitable single agent at each step; its authors report up to 23.8% improvement over baselines and up to 90.1% less data-collection overhead than exhaustive search. STRMAC is a trained router with an encoder and a self-evolving data-generation pipeline. SAGE is the opposite design choice, and that contrast recurs throughout this guide.

## What the Sprix SAGE Router Actually Is

Sprix SAGE Router (`wang2122/sprix-sage-router`) is an MIT-licensed Python package that answers one question: for a task that has already started, should the incumbent continue, recruit a small complementary team, or hand ownership to a peer? The repository is a research preview published on 18 August 2026 by Sprix AI, the A2A initiative of 屿智同行, with v0.3.0 released on 28 August 2026 [GitHub API](https://github.com/wang2122/sprix-sage-router).

The provenance numbers, checked directly against the GitHub API on 1 October 2026: 4,261 stars, 186 forks, 181 watchers, 43 commits, 2 open issues, eight contributors, last push 28 August 2026, Python 3.10+, MIT license, and — the detail that matters most for adoption — **zero runtime dependencies**. There is no package on PyPI, so installation means cloning the repository.

SAGE is not a protocol and does not compete with A2A. It reads protocol and marketplace signals and produces a decision:

| A2A or marketplace signal | What SAGE maps it to |
|---|---|
| `AgentCard.skills` | Normalized capability vector, validated against locally supplied scores |
| Security requirements | Hard `permissions` eligibility filter |
| Supported input/output modes | Compatibility filter applied before scoring |
| Task status, artifacts, failures | `ExecutionState`: ownership, completed nodes, in-flight quality, artifact portability |
| Provider quote | `Bid(cost, latency, confidence)` |
| Completed task evaluation | Contextual trust, success model, bid-fidelity updates |

Two boundaries worth stating up front. First, `profile_from_agent_card` refuses to invent numbers: it only accepts scores for skill IDs the card actually declares, and it requires you to pass capability, cost, and latency evidence explicitly rather than deriving trust from a card's marketing text. Second, the prototype **decides but does not dispatch**. It does not transmit tasks, authenticate endpoints, or verify signatures; an A2A client remains responsible for `message/send`, streaming, polling, cancellation, and secure artifact handling [docs/INTEGRATION.md](https://github.com/wang2122/sprix-sage-router/blob/main/docs/INTEGRATION.md).

## The Three Routing Modes: SELF, COLLABORATE, and HANDOFF

The router evaluates exactly three routes in one objective, and the difference between them is a question of ownership rather than of team size:

| Route | Ownership | Choose it when |
|---|---|---|
| **SELF** | Incumbent agent keeps everything | Existing capability plus accumulated context is already sufficient |
| **COLLABORATE** | Incumbent retains ownership, recruits peers | A small complementary team covers the requirements the incumbent cannot |
| **HANDOFF** | One peer receives full ownership | Specialist advantage beats the context-transfer loss |

The intuition is easy to misread, so make it concrete. HANDOFF is not the "escalate to the better agent" button, and COLLABORATE is not "add more agents until quality rises." Each route is scored on net utility after paying for its own frictions: coordination overhead for collaboration, context-transfer loss for handoff. A team is only worth forming when its marginal requirement coverage beats that overhead, and a handoff is only worth it when the specialist's advantage is larger than the value of the context being abandoned.

That is why the modes compete inside one action space rather than forming a ladder, and why SAGE's own progress-masked and static-coalition baselines receive exactly the same registry, budget, and deadline as the full policies. If HANDOFF were free, every task with a better specialist available would switch, and the benchmark's "always hand off" row shows what that costs: 0.290 utility with 0.130 wasted work, the worst waste figure in the table.

In our own run of the shipped example (`examples/a2a_execution_plan.py`), a planner with 0.94 planning capability and a coder with 0.97 coding capability produced `COLLABORATE` with utility 0.7229, success probability 0.885, coverage 0.697, estimated cost 0.094 against a 0.25 budget, and a single communication edge `planner → coder`. That last field is the one adopters underestimate: the topology is an output, not an input.

## The SAGE Utility Function, Explained

Every feasible route is ranked by one equation, and reading it is the fastest way to understand the router's biases:

```
U(m,S,z,E) = V·p̂θ(y=1 | x,m,S,z,E)
           − λc·C − λl·L − λr·R − λh·H − λo·O − λu·U + β·B
```

In words: start from task value `V` multiplied by the model's predicted success probability, then subtract calibrated cost `C`, critical-path latency `L`, risk `R`, context-transfer loss `H`, and coordination overhead `O`, subtract an uncertainty penalty `U`, and add an exploration bonus `B`. `λ` weights are how you express policy — a latency-sensitive workload raises `λl`, a cost-obsessed one raises `λc`.

Two mechanics inside the equation carry most of the real behavior. The first is the reuse model. For requirement `r`, if the current owner has completed fraction `f_r` and a candidate owner can reuse fraction `η_r` of it, the expected quality for the assigned owner becomes:

```
q̄(a,r) = η_r · q_current(r) + (1 − η_r) · q(a,r)
```

where `η_r = f_r` when the owner is retained and `η_r = f_r · τ_r` when ownership changes, and `τ_r` is the artifact's portability. The same reused fraction reduces projected remaining cost and duration, so abandoned work is not charged twice inside the success estimate. Practically: switching owners does not reset the clock to zero, but it does discount the finished work by how portable it was.

The second mechanic is coverage assignment. Only the assigned owner contributes requirement coverage, and adding an unassigned teammate no longer creates a noisy-OR quality gain. A famous agent with no role in the DAG adds cost and coordination without adding quality. That single rule is why teams stay small.

Search is bounded deliberately. A hard permission-first filter removes unavailable, failed, and unauthorized agents before ranking; cost and latency quotes are inflated by learned bid-fidelity posteriors and current load; a deterministic quote-only prefilter then keeps the incumbent, active executors, and the highest-relevance peers up to `candidate_limit` (12 by default), turning the expensive combinatorial search into an `O(n|R|)` pass. After a team is formed, workload-sensitive team cost and DAG critical-path latency are re-checked, so a high learned score can never override permissions or availability.

When no plan satisfies budget and deadline, the default API returns the least-violating **authorized** plan with `feasible=False` and explicit `constraint_violations`; set `allow_degraded=False` to fail closed instead. Degraded routing never relaxes permissions, failure state, or availability, which is the correct ordering — a router should not be able to buy its way through an access-control boundary by being over budget.

## Checkpoint-Aware Replanning: Why Progress Changes the Decision

This is the repository's actual research claim: checkpoint-specific execution state improves runtime reconfiguration decisions. The state object is more specific than a percentage:

```python
from sprix_sage import ExecutionState

state = ExecutionState(
    active_agents=("planner",),
    active_assignments={"plan": "planner", "build": "planner"},
    completed_requirements=frozenset({"plan"}),
    inflight_requirement="build",
    inflight_progress=0.60,
    inflight_quality=0.74,
    artifact_transferability={"plan": 0.95, "build": 0.40},
)
```

Note the fields that a naive integration would skip. `inflight_quality` must come from an artifact evaluator or another observable signal, not from a hidden ground truth — the repository says so explicitly, because a router fed true quality would be reporting a grade rather than making a decision. `artifact_transferability` should describe what a new owner can actually consume: serialization, tool state, files, context. When those fields are absent the router falls back to a coarser scalar `progress` path for backward compatibility, which is exactly the progress-masked behavior the benchmark measures.

Does state-aware routing change decisions in practice? We reproduced a flip on a two-agent DAG with a strong specialist (incumbent 0.92 planning / 0.55 coding, specialist 0.35 / 0.96), holding everything constant except the in-flight fraction:

| In-flight fraction | Mode | Predicted utility |
|---:|---|---:|
| 0.0 | HANDOFF to specialist | 0.7286 |
| 0.2 | HANDOFF to specialist | 0.7370 |
| 0.4 | SELF | 0.7563 |
| 0.6 | SELF | 0.7938 |
| 0.8 | SELF | 0.8228 |
| 0.9 | SELF | 0.8366 |

The router hands the work to a specialist 0.96 versus 0.55 at the start, and refuses to move it once enough of the work exists. That is the continuation/handoff boundary the repository's controlled intervention is designed to isolate, and it is also why the word "rerouting" is misleading: most of what a checkpoint-aware router does is decline to reroute.

The controlled intervention in `docs/BENCHMARKING.md` holds task, registry, difficulty, artifact portability, budget, and deadline fixed and moves only the in-flight fraction from 0.0 to 0.9. Progress-aware minus progress-masked utility goes from `+0.0000` at 0.0, to `+0.0307` at 0.2, `+0.0463` at 0.5, `+0.0684` at 0.9. The two policies are identical when nothing has been completed. Any claimed benefit of checkpoint-awareness is therefore conditional on there being work worth preserving — a small, clean, unusually falsifiable result.

## Requirement-Conditioned Trust: One Reputation Score Is Not Enough

SAGE tracks reliability per agent **per requirement** instead of one reputation number per agent, and this is the design choice with the strongest measured separation. Both models receive the same exogenous round-robin evidence stream, so the per-requirement model cannot win by spending more on exploration. After 500 observations per seed in the heterogeneous specialist scenario:

| Trust model | Brier score | Selection regret | Mean identification observations |
|---|---:|---:|---:|
| **Per-requirement** | **0.0125 ± 0.0018** | **0.0094 ± 0.0008** | **20.0** |
| Single reputation | 0.0355 ± 0.0008 | 0.0310 ± 0.0359 | 38.2 |

The gap is roughly a factor of three on calibration and a factor of three on regret, and the per-requirement model identifies which agent is actually good at which requirement in about half as many observations. Then comes the negative control, which is the most credible thing in the repository: in a homogeneous setting where no specialization exists, **both** models have zero routing regret. The benchmark does not manufacture an advantage when there is nothing to learn. It also reports that per-requirement trust has *higher* Brier error in that homogeneous case, because it carries more parameters and has no specialization to fit — a finding a marketing team would have deleted.

This matches what practitioners see in A2A marketplaces. A card says an agent is excellent, and the vendor quote confirms the price, but neither tells you whether that excellence transfers to your requirement. Requirement-conditioned trust is how a router learns that the same agent is a 0.94 on extraction and a 0.61 on summarization, and why a single leaderboard score is a poor routing input.

## A2A Integration: From Agent Card to ExecutionPlan

The integration flow in `docs/INTEGRATION.md` is deliberately staged, and the staging is the point: discovery, local evidence, routing, execution, and evaluation stay separate so that each can be audited and versioned independently.

1. Discover an Agent Card through an authenticated registry or trusted endpoint.
2. Verify identity, signature, security schemes, supported modes, and policy requirements **outside** the router.
3. Combine declared skill IDs with locally calibrated capability, cost, latency, permission, availability, and load evidence.
4. Call `route_with_trace` for the selected route, feasible alternatives, and excluded-agent reasons.
5. Convert the selected route into an `ExecutionPlan`.
6. Dispatch plan steps through an A2A client, preserving dependency and cancellation semantics.
7. Evaluate completed artifacts and feed the strongest available evidence to `record_outcome`.
8. Persist learned state with `export_state`.

Step 5 is where the router hands off to transport. The plan is transport-neutral and carries ownership, assignments, DAG dependencies, communication edges, estimated resources, and rationale:

```python
from sprix_a2a import execution_plan

trace = router.route_with_trace(task, bids, state)
audit_record = trace.to_dict()
plan = execution_plan(task, trace.selected)
transport_payload = plan.to_dict()
```

`RoutingTrace.to_dict()` is JSON-serializable and contains the selected mode, team, assignments, topology, utility, and rationale; **all** feasible alternatives ranked by utility; every eligible agent; excluded agents with hard-filter reasons such as missing permissions, failure, or availability; the locally prefiltered agent IDs; and the `feasible` flag with explicit `constraint_violations` for degraded plans.

That record is the deliverable most teams actually need. When a task is reassigned at 60% progress and lands badly, the question asked in the post-mortem is never "what was the success probability" — it is "which agents were considered, which were excluded and why, and what did the router think it was buying." A trace with excluded-agent reasons answers that. A confidence score does not.

## Hands-On: Your First Routing Decision in Python

Adoption cost here is genuinely low — clone, run, read. No package install, no framework, no encoder to train.

```bash
git clone https://github.com/wang2122/sprix-sage-router.git
cd sprix-sage-router
python demo.py            # readable end-to-end routing decision
python -m unittest -v     # 46 tests on our run, all passing
```

A minimal in-flight decision, run against our clone, produced a real switch:

```python
from sprix_sage import Agent, ExecutionState, Requirement, SAGERouter, Task

agents = [
    Agent("planner", {"planning": 0.92, "coding": 0.55}, cost=0.08, latency_ms=900),
    Agent("coder",   {"planning": 0.35, "coding": 0.96}, cost=0.12, latency_ms=1200),
]

task = Task(
    "build-feature",
    requirements=(
        Requirement("planning", 0.4),
        Requirement("coding", 0.6, depends_on=("planning",)),
    ),
    value=1.0, budget=0.30, deadline_ms=4000, progress=0.35,
)

router = SAGERouter(agents, incumbent_id="planner")
state = ExecutionState(
    active_agents=("planner",),
    active_assignments={"planning": "planner", "coding": "planner"},
    completed_requirements=frozenset({"planning"}),
    inflight_requirement="coding",
    inflight_progress=0.35,
    inflight_quality=0.72,
    artifact_transferability={"planning": 0.95, "coding": 0.40},
)

trace = router.route_with_trace(task, state=state)
print(trace.selected.mode.value, trace.selected.assignments, trace.selected.utility)
# -> handoff {'coding': 'coder'} 0.7433

router.record_outcome(trace.selected, ExecutionOutcome(
    success=0.9,
    requirement_scores={"planning": 0.95, "coding": 0.86},
    actual_cost=0.19,
    actual_latency_ms=1450,
))
snapshot = router.export_state()
```

Three observations from actually running it, which the README does not spell out. The shipped `examples/` scripts import the top-level modules directly, so run them with `PYTHONPATH=.` from the clone root (or `pip install -e .`) or they fail with `ModuleNotFoundError: No module named 'sprix_a2a'`. The decision object exposes `explanation`, not `rationale`. And the router is genuinely dependency-free: the whole test suite finished in about one second on Python 3.12 with nothing installed.

`record_outcome` is the loop-closing call and the easiest one to get wrong. Feeding it a self-reported success number trains the router on the executor's own opinion of its work. Feeding it an artifact evaluator's score — or a human override signal — trains it on something the router did not already believe.

## Benchmarks: What the Numbers Do and Do Not Prove

`sage` ships three separate synthetic studies, and the repository is explicit that none of them is a public benchmark. Read the trajectory replay first, because it is the one that tests the actual research claim.

| Strategy | Utility | Added cost / budget | Recovery latency / deadline | Wasted work | Switch rate | Deadline miss |
|---|---:|---:|---:|---:|---:|---:|
| **Progress-aware SAGE** | **0.298 ± 0.021** | **0.191 ± 0.006** | 0.425 ± 0.015 | **0.059 ± 0.004** | 58.4% | **23.3%** |
| Progress-masked SAGE | 0.291 ± 0.021 | 0.204 ± 0.005 | 0.434 ± 0.018 | 0.104 ± 0.010 | 80.1% | 23.6% |
| Always continue | 0.085 ± 0.025 | 0.159 ± 0.005 | 0.627 ± 0.036 | 0.017 ± 0.003 | 0.0% | 34.4% |
| Always hand off | 0.290 ± 0.017 | 0.237 ± 0.008 | 0.508 ± 0.034 | 0.130 ± 0.010 | 100.0% | 30.5% |
| Static greedy team | 0.239 ± 0.031 | 0.248 ± 0.009 | 0.541 ± 0.035 | 0.080 ± 0.007 | 63.4% | 27.7% |
| Static coalition enumeration | 0.286 ± 0.026 | 0.265 ± 0.005 | 0.487 ± 0.034 | 0.104 ± 0.004 | 94.0% | 27.4% |
| Hidden-state dynamic oracle | 0.375 ± 0.019 | 0.243 ± 0.010 | **0.409 ± 0.014** | 0.085 ± 0.005 | 90.0% | 19.6% |

Source: 1,000 checkpoints over five seeds, 200 trajectories per seed, scored by `benchmark_dynamic_evaluator.py`, which never calls the router's switch-loss code.

Here is how to read that table like an engineer. The headline utility difference between progress-aware (0.298 ± 0.021) and progress-masked (0.291 ± 0.021) is **inside the error bars** — those two policies are statistically indistinguishable on utility. The real signal lives in three other columns: wasted work drops from 0.104 to 0.059, a 43% reduction; added cost falls from 0.204 to 0.191 of budget; and the switch rate falls from 80.1% to 58.4%. Progress-awareness, in other words, mostly teaches the router **restraint** — when it knows what has been finished, it stops thrashing. If you were hoping for a utility jump, that is not what this benchmark shows, and the repository does not claim otherwise.

Read the baselines with the same skepticism. "Always continue" is cheap on waste (0.017) but misses 34.4% of deadlines — it never loses work because it never moves. "Always hand off" scores 0.290 utility, essentially the same as the clever policies, while wasting 0.130, the worst figure in the table. Static coalition enumeration reaches 0.286 utility at 0.265 of budget and a 94% switch rate. The hidden-state oracle caps out at 0.375, so the entire headroom between a naive policy and an omniscient one is roughly nine utility points — this is a narrow optimization problem, not a transformation.

The regression suite tells a different and more favorable story, and it should be read separately because it is not about mid-execution routing:

| Strategy | Quality | Common utility | Cost / budget | Deadline miss |
|---|---:|---:|---:|---:|
| Incumbent only | 0.332 ± 0.009 | 0.134 ± 0.008 | 0.245 ± 0.005 | 38.0% |
| Greedy team | 0.577 ± 0.007 | 0.387 ± 0.009 | 0.435 ± 0.011 | 23.8% |
| Static SAGE | 0.491 ± 0.005 | 0.334 ± 0.008 | 0.327 ± 0.009 | 23.6% |
| **Learned SAGE, no exploration** | **0.613 ± 0.005** | **0.433 ± 0.008** | 0.428 ± 0.011 | 21.7% |
| Learned SAGE, random prior | 0.447 ± 0.052 | 0.308 ± 0.049 | **0.297 ± 0.034** | **15.2%** |

Learned SAGE beats a greedy team by 3.6 quality points and static SAGE by 12.2 across 2,500 independent tasks, which is a real gap at ±0.005. The interesting anomaly is the random-prior row: it has the lowest cost and the lowest deadline-miss rate in the table precisely because it is random — it fails fast and cheaply. A metric dashboard that optimizes deadline-miss rate would prefer the worst router here, which is a good reason to collect the full metric set rather than one number.

Now the boundary, stated by the project and worth repeating verbatim in your own evaluation notes: both evaluators are authored with the project, the numbers are "regression and falsification evidence only," and they are "**not** evidence of real-world superiority." A publishable evaluation still requires repeated checkpointed executions on heterogeneous real endpoints plus an independently governed artifact judge. The roadmap lists that item as unchecked. Treat every figure above as an internal consistency check, not a purchasing decision.

## Production Readiness: Audit Trails, Persistence, and Rollout Gates

The gap between "the router returns a decision" and "the router runs your agent network" is the whole production story, and SAGE's status badge says `Research Preview` for good reason. The prototype does not transmit tasks, authenticate endpoints, or verify signatures. Its roadmap leaves signed Agent Card ingestion, real A2A adapters for discovery and streaming, offline replay on anonymized marketplace traces, adversarial-bid evaluation, and a distributed router service with human approval gates all unchecked.

What the repository does provide is the auditable middle. `export_state()` captures contextual reliability, skill beliefs, pair synergy, cost and latency fidelity, and online model parameters; `restore_state()` validates the schema version and requires an exact agent roster match before touching live state. The snapshot contains no tasks, artifacts, credentials, or random-generator state — meaning it is safe to encrypt and store, and also meaning that a warm restart does not resume in-flight work.

The operations guide's request lifecycle is the checklist to implement around the router: validate the DAG and cap requirements, `candidate_limit`, beam width, and collaborator count; retrieve candidates from a trusted registry and treat the quote-only top-k as a second local bound rather than a replacement for indexed retrieval; record the trace with a correlation ID and policy version; require approval for high-risk, destructive, regulated, or high-cost routes; dispatch through an isolated executor with enforced cancellation deadlines; evaluate artifacts independently; and persist snapshots atomically with concurrency control so two workers cannot silently overwrite newer evidence.

Routing latency is bounded by the post-filter candidate count, not by beam width — keep `candidate_limit` finite, monitor `prefiltered_agents`, and run `benchmark_scaling.py` on your own hardware rather than trusting a number from a blog post. Because the router is pure Python with no dependencies, per-decision latency is measurable in your scheduler, but it is also CPU-bound: a large candidate set with a wide beam will not disappear.

A rollout sequence that respects those constraints: **offline replay** on recorded trajectories, where every decision is compared against what actually happened without changing production behavior; then **shadow mode**, where the router decides and logs while the existing scheduler acts, and you measure disagreement; then **canary** on a bounded slice of low-risk tasks with human approval on route changes; then bounded production scope with automatic fallback to the incumbent whenever the trace reports `feasible=False`. Skipping the replay stage is the common mistake, because a router that looks correct on synthetic tables can still be systematically wrong about your artifact portability.

## SAGE vs. Other Routing Approaches (MasRouter, DyLAN, GPTSwarm, RouteLLM)

The repository's own `RELATED_WORK.md` is unusually candid, and it should shape how you position this tool: SAGE does not claim that coalition formation, noisy-OR coverage, marginal team construction, constrained utility, beam search, Beta beliefs, online logistic regression, Thompson-style exploration, or communication graphs originated here. The focused hypothesis is narrower — checkpoint-specific execution state improves runtime reconfiguration decisions for software agents.

| Approach | What it routes | When it decides | What SAGE's authors say |
|---|---|---|---|
| **SAGE** | Ownership and configuration of an in-flight task DAG | After progress, artifacts, and failures exist | Narrow claim; no optimality, mechanism-design, or regret theorem |
| MasRouter | Collaboration mode, roles, and model choices | Learned, before execution | SAGE does not claim comparable trained-model evidence |
| DyLAN / GPTSwarm / AFlow | Dynamic team selection and agent/workflow graphs | During execution, mainly topology | SAGE evaluates continuation, augmentation, and handoff via artifact reuse |
| RouteLLM | Which model answers a prompt | Before a single call | SAGE acts on an in-flight requirement DAG, not one endpoint |
| STRMAC | Best single agent per step, via a trained encoder | Every step, with learned state | SAGE is a dependency-free constrained heuristic, not a trained router |
| MMA2A modality routing | Which modality parts reach which agent | At the protocol layer | Orthogonal; routing modality is not routing ownership |

The STRMAC comparison is the most instructive trade-off. STRMAC trains a router on separately encoded interaction history and agent knowledge, needs a self-evolving data-generation pipeline to accelerate collection of high-quality execution paths, and reports up to 23.8% improvement over baselines with up to 90.1% less data-collection overhead than exhaustive search. SAGE has no learned encoder, no data pipeline, and no paper. In exchange it is auditable line by line, ships with zero dependencies, and can be dropped into an existing scheduler without adopting a framework. If you have labeled trajectories and an ML team, the trained path likely wins on quality. If you have a scheduler, a budget, and a compliance reviewer, the heuristic path is the one that ships this quarter.

One adjacent result is worth knowing because it bounds what any routing layer can claim. A paper on modality-native routing in A2A networks ([arXiv 2604.12213](https://arxiv.org/abs/2604.12213)) reports 20 percentage points of accuracy improvement over text-bottleneck baselines (52% vs 32% on a 50-task benchmark, same LLM backend and tasks) — but only when the downstream reasoning agent can exploit the richer context. Replacing the reasoning agent with keyword matching eliminates the gap entirely (36% vs 36%). Routing is a two-layer requirement: the protocol layer must preserve signal, and the agent layer must be capable enough to use it. A better router cannot compensate for an incapable executor, which is also the honest limit on what SAGE's coverage scoring can promise.

## Limitations, Risks, and What to Watch Next

Six limits to write into your evaluation plan before you wire this into anything that spends money.

**Synthetic evidence only.** Both evaluators are authored with the project; the maintainers describe the numbers as regression and falsification evidence rather than proof of real-world superiority. Real-endpoint evaluation is an open roadmap item.

**Utility differences are not statistically separated.** Progress-aware and progress-masked SAGE overlap on utility (0.298 ± 0.021 vs 0.291 ± 0.021). The defensible claims are about wasted work, cost, and switch rate — do not quote a utility win.

**The quality signal must come from outside.** `inflight_quality` has to be produced by an artifact evaluator or an observable signal. Feed it ground truth and the benchmark is meaningless; feed it the executor's self-report and the router learns to trust confident agents.

**No dispatch, no auth, no verification.** The prototype returns a decision and a transport-neutral plan. Task transmission, endpoint authentication, signature verification, and artifact handling are your responsibility, as is every A2A lifecycle requirement including the "always emit a terminal event" rule.

**Heuristic, not optimal.** The `candidate_limit` prefilter, the beam search, and the workload-sensitive quotes are engineering bounds. SAGE makes no coalition-stability or global-optimality claim, and its reference list explicitly credits the prior work in coalition formation, combinatorial allocation, and contextual bandits.

**Adversarial bids are unmeasured.** Quotes are inflated by learned bid-fidelity posteriors, which helps against optimistic vendors but is not a defense against an agent that lies strategically. Adversarial-bid, churn, privacy, and policy-violation evaluation are all listed as unchecked roadmap items.

What to watch: signed Agent Card ingestion and candidate retrieval, real A2A adapters, offline replay on anonymized marketplace traces, and a distributed router service with observability and approval gates. The repository's trajectory is worth noting — published 18 August 2026, v0.3.0 ten days later, last push 28 August, 4,261 stars and 181 watchers against 43 commits. High attention, small committed core, eight contributors. That is a healthy shape for a research preview and an unhealthy shape for a dependency you cannot replace, which is another argument for treating the router as a replaceable policy behind your own interface.

## FAQ: A2A Routing Agents

### What are A2A routing agents?

A2A routing agents are the decision layer that sits above the Agent2Agent protocol and chooses which agent configuration should execute a task, in which mode, and why. A2A itself standardizes Agent Cards, messages, tasks, artifacts, authentication, and transport; it does not define who should work on a task after execution starts. Routing agents fill that gap by scoring candidate configurations against permissions, budget, deadline, artifact portability, and observed progress.

### How does the Sprix SAGE Router differ from an LLM router like RouteLLM?

An LLM router selects which model answers a single prompt before any execution happens. SAGE selects whether an in-flight task should stay with its incumbent (SELF), recruit complementary peers (COLLABORATE), or transfer ownership entirely (HANDOFF), after accounting for completed DAG nodes, reusable artifacts, observed partial quality, failures, budget, and deadline. The input is an execution state, not a prompt embedding, and the output is an ownership configuration, not an endpoint choice.

### Is progress-aware routing actually better than ignoring progress?

On the project's own trajectory replay, no clear utility advantage exists: progress-aware SAGE scores 0.298 ± 0.021 against 0.291 ± 0.021 for the progress-masked variant, so the error bars overlap. The measurable differences are operational — wasted work falls from 0.104 to 0.059, added cost from 0.204 to 0.191 of budget, and the switch rate from 80.1% to 58.4%. Knowing what has been completed mostly teaches the router to leave work in place.

### Can I use SAGE in production today?

Not as an orchestrator, and the project says so. It is an early-stage research preview: the prototype does not transmit tasks, authenticate endpoints, or verify signatures, and you remain responsible for A2A dispatch, streaming, polling, cancellation, and artifact security. What you can deploy responsibly today is a bounded adapter — offline replay, then shadow mode, then a canary slice with human approval — with the router as a replaceable policy behind your own interface, and automatic fallback to the incumbent whenever a trace reports `feasible=False`.

### How much does it cost to try the SAGE Router?

Nothing but your own time. It is MIT-licensed, depends on nothing at runtime, targets Python 3.10+, and has no PyPI release, so adoption means cloning the repository and running `python demo.py` plus `python -m unittest -v` — 46 tests that completed in about a second on our Python 3.12 run. There is no hosted service or paid tier to evaluate, and no vendor account to create, which makes the cheapest honest next step a self-contained spike in your own scheduler.
