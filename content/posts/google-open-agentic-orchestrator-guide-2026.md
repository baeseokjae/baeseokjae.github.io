---
title: "Google's Open Agentic Orchestrator (AX) in 2026: What It Changes, and What It Doesn't"
date: 2026-09-29T19:20:21+00:00
tags:
  - google open agentic orchestrator
  - google ax orchestrator
  - google ax agent executor
  - agent executor google
  - ax google agentic orchestrator tutorial
  - ax apply task yaml
  - google ax vs kagent
  - google ax vs scion
  - ax vs langgraph
  - agent substrate google
  - agent substrate cncf
  - task workspace gateway model primitives
  - suspend resume agent sandbox
  - durable execution agent runtime
  - agent orchestration kubernetes
  - actor teleport gvisor snapshot
  - sub-second agent resume
  - when to use ax
  - ax kubernetes setup requirements
  - google agent runtime production
  - long running agent state persistence
description: "Google's open agentic orchestrator (AX) is a Kubernetes-style agent runtime, not a framework. What it does, its alpha limits, and who should adopt it now."
draft: false
cover:
  image: "/images/google-open-agentic-orchestrator-guide-2026.png"
  alt: "Google's Open Agentic Orchestrator (AX) in 2026: What It Changes, and What It Doesn't"
  relative: false
schema: "schema-google-open-agentic-orchestrator-guide-2026"
---

Google's open agentic orchestrator, AX (Agent Executor), is an Apache-2.0 declarative control plane for AI agents: you declare a Task, a Workspace and a Model, and a distributed runtime provisions an isolated sandbox, runs it, and can suspend and resume it. It is infrastructure under your agent framework, not a framework itself.

That one sentence is the difference between understanding AX and misreading it. Most coverage in late September 2026 described it as "Google's new agent framework" and then argued about features it was never designed to have. The co-creator of the project, Jaana Dogan, answered that framing directly on Hacker News: "AX is a layer that is closer to job orchestration... It's NOT an agentic framework."

This guide walks through what AX actually is, what Agent Substrate underneath it does, why its primitives are workload-shaped rather than prompt-shaped, what the alpha-state open issues mean for a real deployment, and how to decide between AX, kagent, Scion, and workflow-level durable execution tools like Temporal or LangGraph.

## What is Google's open agentic orchestrator (AX)?

AX stands for Agent Executor. It is an open-source, Go-written runtime and control plane, released under Apache 2.0 by Google, that runs agents as stateful actors rather than as microservices or batch jobs.

| Fact | Value |
| --- | --- |
| License | Apache-2.0 |
| Language | Go |
| Repository created | 2026-03-30 |
| Latest release at time of writing | v0.3.1 (2026-09-25) |
| Stars / forks (GitHub API) | 12,550 / 612 |
| Open issues | 59 |
| Announced on the Google Cloud blog | 2026-05-20 |
| Hacker News front page | 2026-09-21, #1, 664 points, 299 comments |
| Install path | `go install github.com/google/ax/cmd/ax@latest` |

The star count deserves a caveat that most write-ups skip. A GitHub page render of the same day showed roughly 1,955 stars while the GitHub API reported 12,550 — page snapshots lag. Quote API-scale figures, and attach a date to any Hacker News point count. The Algolia HN API returns 666 points and 300 comments for that thread as of 2026-09-29; secondary coverage of the same thread reports 621 points and 284 comments, and other snapshots show 179/74. Those are different moments of the same thread, not contradictions.

The project's own self-description on GitHub is "Google's open agentic orchestration runtime," and the landing page calls it "a distributed agent runtime designed for reliability, safety, customizability, and efficiency."

## Why is AX not an agent framework?

Because its primitives contain no prompts, no planner, no graph, and no memory abstraction. Everything it exposes is about where the work runs and what it is allowed to touch.

A framework answers "how does the agent decide what to do next?" A runtime answers "where does that agent run, what does it survive, and who can audit it?" AX is the second question. This is why you can run LangGraph as the Task command inside AX and lose nothing — the sandbox layer and its state survive when the Python process does not.

The sharpest available framing of the boundary comes from an analysis of the two event logs:

> One log lets you ask why the model chose something. The other lets you kill the machine and continue. Neither substitutes for the other.

A harness logs what the model saw — prompts, reasoning, tool calls, context injections. AX logs what the task did — process state, filesystem, scheduling. Conflating checkpointing with model memory is the single most common review mistake in this space, and it leads teams to expect AX to give them conversation memory or reasoning traces, which is not its job.

## What AX primitives exist: Task, Workspace, and Model?

Three declarative resources under the `ax.io/v1alpha1` API group. Each is deliberately workload-shaped and none of them is about prompting.

| Primitive | What it declares | Why it exists |
| --- | --- | --- |
| Task | Execution lifecycle and sandbox resource constraints (CPU, memory) | The unit of resumable, isolated work |
| Workspace | Pre-execution environment assembly: git repos, MCP servers, skill bundles, and a natural-language goal executed by an init agent | Turns "get the environment ready" into a declarative step instead of a shell script |
| Model | Provider plus parameters, plus a Kubernetes secret reference for credentials | Keeps model selection, keys and parameters out of application code |

Tasks are immutable once created. Suspend and resume are first-class RPCs — `SuspendTask`, `ResumeTask`, and a streaming `WatchTask` — not side effects of deleting and recreating a pod.

A fourth resource, `Gateway`, was removed from AX on 2026-09-24 (issue google/ax#395). It had declared outbound network allowlists and egress policy, and the maintainers deleted it across the API, controller, server, CLI, store and documentation, reserving protobuf field 8 and stripping the Gateway RPCs. The stated reason is architectural: Gateway "introduced an unnecessary layer and architectural bifurcation between Agent Substrate and AX." The current `ax.proto` contains no Gateway message or service at all.

That removal matters beyond bookkeeping, because it is why several September 2026 write-ups still describe "four primitives." If you see a Gateway table in an AX guide, it was written from an early release or from secondary coverage rather than the source tree. It also removes the network-allowlist control surface from the AX API — network policy is now Substrate's to own, which is the direction the roadmap confirms.

A `Sandbox` / `SandboxConfig` resource is listed as roadmap, not shipped: the roadmap puts runtime isolation backends, kernel and syscall constraints, filesystem mounts and security profiles under "stabilize core specs." Do not design against it yet.

The CLI is intentionally kubectl-shaped: `ax apply`, `ax get`, `ax describe`, `ax watch`, `ax delete`, `ax ssh`, plus agent-specific verbs. If you already operate Kubernetes, the muscle memory transfers on day one. If you do not, this is the moment to notice that the ergonomics promise in the README and the actual requirements do not quite line up — more on that below.

## How does AX store state, and why not in etcd?

AX deliberately does not store its state in etcd. Its DESIGN.md states the reason plainly: keeping millions of short-lived tasks as Kubernetes custom resources would exceed etcd's comfort zone, both the single-digit-GB size limit and the write rate. Instead AX persists state in Redis and reconciles directly with Agent Substrate under distributed locks.

The binary layout reflects the same split:

- `ax` — the CLI
- `ax-server` — gRPC on port 8080, with `/healthz`
- `ax-task-runner` — PID 1 inside every task container

That design choice is the tell that AX was built by people who intend to run it at a density Kubernetes was not designed for. CRDs are a fine control-plane contract and a poor high-frequency database.

## What does Agent Substrate actually do under AX?

Agent Substrate is the compute runtime. It is where the suspend/resume magic that everyone quotes actually happens, and it is a separate project with a separate governance path.

| Claim | Figure | Source |
| --- | --- | --- |
| Resume latency | Sub-500ms | agent-substrate/substrate |
| Suspend/resume throughput | 500+ activations per second | agent-substrate/substrate |
| Sandbox density vs standard container runtimes | 10x | agent-substrate/substrate |
| Demo oversubscription | ~250 stateful actors on 8 physical pods (30x+) | agent-substrate/substrate |
| Roadmap target | Sub-100ms p95 activation latency | cncf/sandbox#523 |
| Stars / forks | 3,962 / 473 | GitHub API |
| Created | 2026-05-13 | GitHub API |

The 30x oversubscription number is the one to internalize. An agent's wall-clock life is mostly waiting — on model tokens, on tool round-trips, on a human approval. Standard container scheduling keeps the sandbox hot through that waiting or pays cold-start latency when the agent comes back. Substrate multiplexes many suspended actors onto shared host workers and restores them in under half a second, so density and latency stop being a tradeoff.

The resume path is not a shortcut; it is a real distributed transaction. The documented flow runs CoreDNS (which resolves the actor's name to the atenet router ClusterIP, never the worker IP), then Envoy's `ext_proc` filter on `:50051`, which parses the `:authority` header into an `(atespace, actor_name)` pair and calls `ResumeActor` with request coalescing so that 50 concurrent requests to a cold actor do not cause 50 resumes. From there ateapi acquires `lock:actor:<atespace>:<name>` in Redis (30-second TTL, 28-second workflow timeout), picks an eligible idle worker, dials the atelet DaemonSet on that worker's node, and atelet fetches the checkpoint from object storage and calls `runsc restore -background -direct` into a gVisor sandbox. Finally ExtProc rewrites `:authority` to the pod IP and the request lands on the workload.

Isolation is gVisor, not just a container namespace, and pod snapshots are backed by object storage. The community nickname for the mechanism — "Actor Teleport" — is descriptive enough to be worth keeping.

## Why does AX depend on Kubernetes, and what does the objection get right?

Because Substrate uses Kubernetes for provisioning, WorkerPool pod lifecycle, CRD reconciliation through atecontroller, and node scheduling, with Envoy as the ingress gateway for the atenet-router. The custom resources include WorkerPool, ActorTemplate, and SandboxConfig.

The practitioner objection is real and it was repeated almost verbatim across the Hacker News thread: the README quickstart needs a cluster, `ko`, a registry your nodes can pull from, and a reachable Agent Substrate control API — while the same README markets "uncompromising ergonomics." Commenters called that out as a mismatch, and one wrote plainly, "LOL. Bye!" at the cluster requirement.

The maintainers answered the substance rather than the tone. Dogan noted that they do mention Agent Substrate, and that Substrate "is working on Kubernetes but isn't exclusive to Kubernetes." AX targets teams that want one stack on any cluster and that struggle to deliver agentic applications onto someone else's compute. That is a coherent position. It is just not a position aimed at a developer with a laptop and one agent.

There is a second, sharper objection worth quoting: with AX and Substrate you opt into a large stack and must build for Substrate, unlike projects such as Scion that run existing harnesses — Claude Code, Codex, OpenCode — both locally and in-cluster. If your instinct is "I just want my existing agent to be resumable," AX asks you to rebuild the workload, not just retarget it.

## What is the real cost of migrating to AX?

The CLI is not the migration. The workload model is.

| Kubernetes assumption | What Substrate changes |
| --- | --- |
| Kubernetes Jobs run your container | Kubernetes Jobs do not run inside a secure runtime; agents run as Substrate actors |
| Every workload talks through the API server | Substrate bypasses the standard Kubernetes control plane on the hot path |
| A Service fronts each task | Routing happens by rewriting the request's `:authority` to the actor's pod IP |
| Deployments are long-lived and hot | Actors suspend on idle and resume on demand |

Google's stated scale target explains why the control plane had to be bypassed on the hot path: hundreds of millions of registered agents, billions of tasks per cluster, and what the Cloud blog calls "the chatter of millions of sub-second tool calls."

If your workload is a nightly batch job that runs for four minutes and exits, none of this buys you anything. If your workload is 40,000 long-lived agents that each spend 95% of their life waiting, it is the entire product.

## What does the practical setup actually require?

The honest quickstart, stripped of marketing:

1. Install Go and the AX CLI: `go install github.com/google/ax/cmd/ax@latest`
2. Have a Kubernetes cluster reachable with credentials.
3. Have `ko` available for building images.
4. Have a container registry your nodes can pull from.
5. Have a reachable Agent Substrate control API — the in-cluster default is `api.ate-system.svc.cluster.local:443`.
6. Deploy with `make deploy AX_IMAGE_REPO=<your-registry>`, which lands Redis and the control plane in the `ax-system` namespace.

Then the operational loop is `ax apply -f task.yaml`, followed by waiting on the `WorkspaceReady` and `Ready` conditions rather than the phase string. Keep `debug: true` while learning, because without it guest services stay off — and therefore `ax ssh` does not work.

The confidence test every new user should run before trusting a multi-hour job: `ax ssh` in, write a file, `ax suspend task`, `ax resume task`, ssh back, and confirm the file survived. If it did, you have understood what AX is for.

## What is broken in AX right now?

AX is pre-1.0 with breaking changes explicitly expected, and the issue tracker documents the rough edges rather than hiding them. Here is the honest list.

| Issue | Symptom | Practical impact |
| --- | --- | --- |
| google/ax#347 | `WorkspaceReady` can report ready on an empty git clone | Always verify environment contents over `ax ssh` instead of trusting the condition |
| google/ax#348 territory | Task env values are plain; no `valueFrom`, no clean secret mount story | Do not assume Kubernetes secret plumbing works here |
| Egress allowlist footgun | Hostname-style allowlists can block all TLS egress | Start with host `*` on port 443, then tighten deliberately |
| google/ax#337 | Per-request `harness_config` overlay allows process spawn via `mcp_servers` | Security review required before multi-tenant use |

Release cadence tells the same story from another angle: v0.1.0, then v0.2.0 and v0.2.1 on 2026-07-22, v0.2.2 on 2026-07-23, v0.2.3 on 2026-08-13, v0.3.0 on 2026-09-20, v0.3.1 on 2026-09-25. That is a project moving fast enough that pinning versions and reading changelogs is not optional.

One more caution for readers doing their own research: a widely circulated aggregator post (a dev.to article, now 404) attributed AX to a September 18 I/O unveil with a modular DAG engine, a Gemini 1.5 Pro reference implementation, and a 27% benchmark win over LangChain. None of those specifics appear in the repository, the docs, or Google's blog post. Treat them as fabricated. The repository, the Cloud blog announcement, the DESIGN.md file, and the issue tracker are the sources that hold up.

## Why did a May 2026 project go viral in September 2026?

Because the announcement and the attention were four months apart, and that gap is a useful signal rather than a mystery.

AX was announced on the Google Cloud blog on 2026-05-20 by Jaana Dogan and Ethan Bao. It hit #1 on Hacker News on 2026-09-21 with 664 points and 299 comments — roughly four months later. That is why many late-September write-ups misdate the launch, and why the project suddenly seems to have appeared everywhere at once. The likely interpretation is late discovery crossing a maturity threshold: by late September there was a v0.3 release line, a real install path, a roadmap, and enough practitioner experience to argue about.

## Is AX vendor-neutral, or is it a Google Cloud moat?

Both, in different layers, and the distinction matters for an adoption decision.

| Layer | Where it lives | Governance status |
| --- | --- | --- |
| AX (Agent Executor) | github.com/google/ax | Google org, Apache-2.0, no support disclaimer in the repository — and no explicit support commitment either |
| Agent Substrate | github.com/agent-substrate/substrate | Non-Google org, CNCF Sandbox application filed 2026-09-08 (cncf/sandbox#523) |

The CNCF application discloses that Kubernetes is used for provisioning, WorkerPool pod lifecycle, atecontroller CRD reconciliation, and node scheduling, and that Envoy handles the atenet-router ingress gateway. It also discloses, without softening, that Google's business model here is "strictly infrastructure-centric" — users run the open-source stack on VMs they buy and manage. And it flags maintainer diversity as a non-blocking technical oversight committee item: 16 of 18 maintainers come from one organization.

What CNCF ownership buys you is a governance and contribution path that does not depend on one vendor's roadmap, plus a documented neutrality commitment. What it does not buy you is a rewrite of the technical dependency: Substrate still needs Kubernetes and Envoy, and Google still leads development. A CNCF badge is a hedge on governance, not an erasure of architecture. The process is also not finished, and adopters should watch the vote rather than the announcement: as of 2026-09-25 the binding TOC vote stood at 4 in favour, 0 against, and 7 not yet voted, against a 66% threshold. The vendor-neutrality claim is real but still pending approval.

Ecosystem context from the same thread is worth noting too: `kagent` has experimental Substrate support, and `agent-sandbox` (kubernetes-sigs) is the Kubernetes-native cousin — 4,085 stars, created 2025-08-12 — with a different set of tradeoffs.

## How does AX compare to kagent, Scion, and LangGraph or Temporal?

They solve different problems at different layers, which is why most teams need one of them rather than three.

| Option | Layer | Model | Best fit | 2026 signal |
| --- | --- | --- | --- | --- |
| Google AX | Execution runtime + declarative control plane | Tasks as suspendable actors on Substrate | Platform teams with bursty, long-lived, sandbox-needing agents | 12,550 stars, v0.3.1, Apache-2.0, three primitives after the Gateway removal |
| kagent | Kubernetes control plane | Agents as CRDs, GitOps-shaped | Kubernetes-native shops that want agents in manifests | 3,885 stars, CNCF Sandbox, built by Istio founders, experimental Substrate support |
| Google Scion | Multi-agent coordination | One isolated container plus optional git worktree per agent, coordination via CLI | Running several agents on one repository without file collisions | 1,729 stars, GoogleCloudPlatform org, carries a project disclaimer |
| LangGraph / Temporal | Application-level durable execution | Workflow checkpoints inside your process | Durability of control flow without a sandbox runtime | Mature, widely adopted |

The Scion comparison is instructive because its failure mode is concrete: three Claude Code agents editing one repository read the same file and overwrite each other. Container isolation separates processes; worktree isolation separates files. Scion addresses coordination, AX addresses resumable execution, and both are Apache-2.0 Go projects created in March 2026. That layering — coordination, execution, declarative control — is evidence of a deliberate infrastructure strategy rather than one monolithic framework.

If what you actually want is "my workflow survives a process crash," Temporal or LangGraph checkpoints may be sufficient and far cheaper. You only need AX when the sandbox itself — the filesystem, the running process tree, the network policy — has to survive too.

## What is on the governance and security roadmap?

Mostly roadmap, which is exactly why regulated adopters should read it as a checklist rather than as shipped capability.

- SPIFFE identities for tasks: X.509-SVIDs for zero-trust mTLS between tasks
- Egress gateway credential injection, so agent containers never hold long-lived secrets
- Substrate becoming an OIDC and SPIFFE identity provider; Google Agent Identity is already built around SPIFFE
- Least-privilege setup versus runtime policies, splitting workspace initialization from execution permissions
- Idleness detection with automatic suspension for density
- Stateful task branching from checkpoints
- Full audit trail and trajectory collection
- Budget guardrails and telemetry
- Stabilizing the `ax.io/v1alpha1` specs for Task, Workspace, Model and the roadmap `Sandbox`/`SandboxConfig`
- A separate workspace-setup actor, and a new Agent Substrate Actor migration

The egress gateway design is genuinely good: injecting credentials at the edge means a compromised sandbox has nothing durable to steal. But "roadmap" is the operative word for the SPIFFE task identity story. If your compliance requirements demand per-task cryptographic identity today, AX is not there yet.

## Who should adopt AX now, and who should wait?

Adopt when most of these are true:

- You already run Kubernetes and have a platform team that owns it.
- Your agents are long-lived and bursty, spending most wall-clock time waiting.
- You need agents to survive outages, deploys, or human-in-the-loop pauses without losing workspace state.
- You need sandbox isolation stronger than namespaces, and you can accept gVisor.
- You need to run agents on your own compute, in your own data plane.
- You can absorb pre-1.0 breaking changes and track releases closely.

Wait when most of these are true:

- Your agents are short-lived, single-turn, or stateless.
- You are one developer on a laptop with one agent — the cluster, `ko`, and registry requirements will cost you a day before you run anything.
- You need per-task SPIFFE identity or a mature secret-mount story today.
- You need a supported product with an SLA rather than an early open-source project.
- Your durability problem is control flow, not sandboxing — in which case LangGraph or Temporal is the cheaper answer.

A reasonable middle path for the undecided: run the suspend/resume confidence test on one real workload in a scratch cluster. If your reaction to "the file survived a suspend and resume" is "that solves a problem I currently pay for," AX is worth the rebuild. If it is "that is neat," you do not have the problem yet.

## What does the AX story actually prove?

It proves that a serious infrastructure vendor now treats agent execution as a systems problem rather than a prompting problem. The five native capabilities Google claims — durable execution, secure isolation, session consistency, connection recovery, and trajectory branching from checkpoints — are all statements about process lifecycle, not about intelligence. The single-writer architecture and the append-only event log exist so that a client can reconnect and backfill from the last sequence it saw, which is a property of distributed systems.

It also proves that the community will not accept the pitch uncritically. The top responses to AX were not about features; they were about a cluster requirement hiding under an ergonomics headline, a company's track record of discontinuing projects, and whether opting into Substrate means rebuilding workloads. Those are fair objections, and Google's maintainers engaged them with specifics — Substrate is not exclusive to Kubernetes, identities are moving to SPIFFE, the layer is being donated to CNCF — rather than dismissing them.

The unresolved question is the one that matters for anyone reading this in 2026. AX solves a real and expensive problem: paying full compute for agents that are idle. Whether the answer is a new runtime with its own actor model, or the existing Kubernetes ecosystem growing the same capability, is not yet settled. What is settled is that the problem is now named, and that the vocabulary of orchestrator, runtime, harness, and framework has been usefully separated.

## FAQ

### Do I need Google Cloud or Gemini to run AX?

No. AX is Apache-2.0 and runs on any Kubernetes cluster you control, with the Model primitive abstracting the provider and holding the credential secret reference. Google's egress gateway design assumes you are running the open-source stack on VMs you buy and manage, which is the business model the CNCF application states explicitly. What you are adopting is an early-stage, unsupported project rather than a product with a support commitment — the repository carries no support disclaimer, which is not the same as carrying a promise.

### Is AX a replacement for LangGraph or Google ADK?

No, and the co-creator says so directly: "AX is a layer that is closer to job orchestration... It's NOT an agentic framework." After the Gateway resource was removed in September 2026, the primitives are Task, Workspace, and Model — there is no planner, graph, memory, or prompt abstraction anywhere in the surface. You can run LangGraph as the Task command inside AX and keep your entire framework investment; what changes is that the sandbox and its state survive when the Python process does not.

### How much does the Kubernetes dependency actually cost me?

The hard requirement is a cluster, `ko`, a registry your nodes can pull from, and a reachable Agent Substrate control API. On top of that, the workload model changes: Kubernetes Jobs do not run inside a secure runtime, there are no CRDs on the hot path, and inbound routing works by rewriting the request's `:authority` to the actor's pod IP rather than through per-task Services. For a platform team already running Kubernetes, that is a week of learning. For a solo developer, it is a day before hello world and a much larger rebuild after.

### Why did a project announced in May 2026 go viral in September 2026?

Because the announcement and the attention were four months apart. Google's Cloud blog post by Jaana Dogan and Ethan Bao landed on 2026-05-20; the Hacker News thread reached #1 on 2026-09-21 with 664 points and 299 comments. In between, the project shipped a v0.2 and v0.3 line, added a documented install path and roadmap, and accumulated enough practitioner experience to argue about. Late write-ups that call September the launch date are misdating it.

### Is AX production-ready in late 2026?

Not by most definitions. The project is pre-1.0 and its README warns of major breaking changes prior to a stable release; the release line went from v0.1.0 to v0.3.1 between July and September 2026. Documented alpha-state defects include `WorkspaceReady` reporting ready on an empty git clone (issue #347), no clean Task secret-mount story (issue #348 territory), an egress allowlist that can block all TLS, and a security report (#337) about the per-request harness overlay spawning processes via `mcp_servers`. It is ready for evaluation on a scratch cluster and for platform teams who can absorb churn — not for a regulated production deployment that needs per-task SPIFFE identity today.

## Sources

- Google Cloud Blog — "Agent Executor: Google's distributed agent runtime" (Jaana Dogan, Ethan Bao, 2026-05-20): https://cloud.google.com/blog/products/ai-machine-learning/agent-executor-googles-distributed-agent-runtime
- Agent Executor landing page: https://agentexecutor.io/
- google/ax repository and DESIGN.md: https://github.com/google/ax and https://raw.githubusercontent.com/google/ax/main/DESIGN.md
- google/ax roadmap: https://raw.githubusercontent.com/google/ax/main/docs/roadmap.md
- google/ax issue tracker (#337, #347, #348, #395 removing the Gateway resource): https://github.com/google/ax/issues
- google/ax API surface, `pkg/apis/v1alpha1/ax.proto`: https://raw.githubusercontent.com/google/ax/main/pkg/apis/v1alpha1/ax.proto
- InfoQ — "Google's AX orchestrator" (2026-09): https://www.infoq.com/news/2026/09/google-ax-orchestrator/
- Forkast / Yahoo Tech — "Google's open agentic orchestrator hit..." (2026-09): https://tech.yahoo.com/ai/gemini/articles/google-open-agentic-orchestrator-hit-072928739.html
- Hacker News discussion, "AX — Google's Open Agentic Orchestrator" (2026-09-21): https://news.ycombinator.com/item?id=49780797
- Tutorial — "AX: Google Open Agentic Orchestrator" step-by-step setup: https://www.qwe.edu.pl/tutorial/ax-google-open-agentic-orchestrator-tutorial/
- Medium — "Google's Agent Orchestrator Treats Your Harness as a Workload": https://medium.com/@sebuzdugan/googles-agent-orchestrator-treats-your-harness-as-a-workload-6d27b9418f00
- besthub — "How Google's New Open Source Projects Make AI Agents Production Ready": https://www.besthub.dev/articles/how-google-s-new-open-source-projects-make-ai-agents-production-ready-b373cc8d3d52
- CNCF Sandbox application for Agent Substrate: https://github.com/cncf/sandbox/issues/523
- Agent Substrate repository: https://github.com/agent-substrate/substrate
- Agent Substrate resume flow documentation: https://learn.agentsubstrate.dev/flows/resume-actor
- GitHub API — google/ax, agent-substrate/substrate, kagent-dev/kagent, GoogleCloudPlatform/scion repository metrics
