# Strategy Review - 2026-06-19 run2

## Phase

Current phase: Phase 1 - First Signal Integration - early GSC signals + expanded KD range.

Phase 1 behavior applies: use external competitor/source discovery, read available analytics, and keep KD range expanded to 0-25. No dependable GSC query export was present for this heartbeat, so discovery stayed external-data-led with strict topic/post dedupe.

## Queue State

- Active queued topics before run: 39
- Candidates generated: 18
- Promoted to "queued": 18
- Rejected: 0
- New priority range: 6577-6594

## Major Competitor Signals (June 13-18, 2026)

This was an exceptionally dense week for agent platform launches. Major gaps identified:

### Agent Delivery/Orchestration Layer
A new architectural tier is emerging above individual agent harnesses. Four major launches hit within 5 days:

- **GitKraken Kepler** (June 15, 2026) — "Agentic Development Environment" (ADE) that treats cross-repo Tasks as first-class units with auto-rebasing, conflict resolution, and multi-agent oversight. No existing coverage in topics.json or posts.

- **Databricks Omnigent** (June 13, 2026) — Open-source meta-harness that wraps Claude Code, Codex, Pi, and custom agents under a common API. Adds composition, policy-based control (cost budgets, permissions), and live collaboration. No existing coverage.

- **Vercel Eve** (June 17, 2026) — Filesystem-first TypeScript agent framework with durable execution, sandboxed compute, HITL approvals, subagents, and evals built in. An agent is a directory of files. No existing coverage.

- **Cloudflare Flue** (June 17, 2026) — Open-source framework from the Astro team built on the Pi harness and Cloudflare Agents SDK. Agents defined by context, not orchestration scripts. No existing coverage.

- **OpenHands Agent Canvas** (June 16, 2026) — Workspace for self-hosted coding agent automations integrated with Slack, GitHub, Linear. No existing coverage.

### Agent Discovery/Governance
A new specification and two product launches address the "how do agents find the right tool" problem:

- **GitHub Copilot Agent Finder + ARD Spec** (June 17, 2026) — Agentic Resource Discovery (ARD) specification co-developed with Google, GoDaddy, Hugging Face, Microsoft. Agents discover capabilities at runtime instead of carrying every tool. No existing coverage.

- **GitLab Orbit** (June 12, 2026) — Context graph across the software lifecycle: code, work items, pipelines, deployments. Agents respond 11x faster, use 4.5x fewer tokens, 45x fewer hallucinations in internal testing. No existing coverage.

- **GitLab Governance for Agents** (June 12, 2026) — Identity, policy, audit, and approval mechanisms for agent-driven code changes. Private beta. No existing coverage.

- **GitLab Next Gen SCM** (June 12, 2026) — Replaces full repo clones with structured API access for AI agents. Private beta. No existing coverage.

### New Agent Observability Entrants
Three new platforms with differentiated approaches:

- **Omium** — Agent observability with execution checkpointing: snapshot agent state at every step, restore from any checkpoint, fork timelines. No existing coverage.

- **Dynatrace A2A Observability** — Agent-to-agent communication monitoring with A2A protocol tracing. Mature enterprise platform adding agent-specific traces. No existing coverage.

- **Latitude** — Open-source agent monitoring with semantic search across 100% of traces, issue clustering, and auto-generated eval datasets. No existing coverage.

- **Laminar** — Open-source agent observability with natural-language Signals, MCP/CLI debugging, and auto-eval dataset generation. Partial topic exists (laminar-ai-agent-evals-observability-guide-2026 — queued_throttled); new MCP debugging angle is unaddressed.

### Production MCP Operations
MCP security and operations content continues to mature with deeper, more actionable guides:

- **Digital Applied 75-Point MCP Security Audit Checklist** — Eight threat domains, 75 concrete checks, abuse-path mapping, SOC2 alignment. Most comprehensive MCP security methodology in market. No existing coverage.

- **Stacklok MCP Enterprise Security Guide** — Per-request identity, curated MCP registries, RBAC tool-level access. Enterprise deployment focus. No existing coverage.

- Multiple sources converged on Streamable HTTP deprecation of SSE, OAuth 2.1 + PKCE as mandatory, and per-tool least-privilege scoping as table stakes for MCP production deployments.

### Coding Agent Safety Evolution

- **Qwen Code v0.18.0** (June 13) — Output hygiene fix (skip thought parts in copied output), cancellation-safe tool execution, MCP project approval gating. Signals convergence on reliability/safety as a competitive axis for coding agents. No existing coverage of this specific safety angle.

- **Junie JetBrains GA** (June 17) — Left beta with ACP protocol, agentic debugging using the real IDE debugger, remote control, and plan mode. Existing Junie topics are older CLI/initial review; GA + ACP integration is new.

## Topics Added

- 6577. GitKraken Kepler Agentic Delivery Engine Guide 2026 — AI coding tools, KD 5, SV 300
- 6578. Databricks Omnigent Meta-Harness Guide 2026 — AI for developers, KD 5, SV 340
- 6579. Vercel Eve Agent Framework Tutorial 2026 — AI for developers, KD 6, SV 380
- 6580. Cloudflare Flue Agent Framework Guide 2026 — AI for developers, KD 5, SV 280
- 6581. OpenHands Agent Canvas Guide 2026 — AI coding tools, KD 4, SV 260
- 6582. GitHub Copilot Agent Finder and ARD Specification Guide 2026 — AI coding tools, KD 5, SV 320
- 6583. GitLab Orbit Context Graph for AI Agents Guide 2026 — AI for developers, KD 5, SV 300
- 6584. GitLab Governance for AI Agents Guide 2026 — AI for developers, KD 6, SV 360
- 6585. Agentic Resource Discovery vs MCP Server Discovery 2026 — AI for developers, KD 6, SV 320
- 6586. Omium Agent Observability Checkpoint Recovery Guide 2026 — AI for developers, KD 4, SV 240
- 6587. Dynatrace A2A Agent-to-Agent Observability Guide 2026 — AI for developers, KD 5, SV 300
- 6588. Latitude Open-Source Agent Monitoring Guide 2026 — AI for developers, KD 4, SV 260
- 6589. MCP Server Security 75-Point Audit Checklist 2026 — AI for developers, KD 6, SV 380
- 6590. Junie JetBrains GA with ACP Protocol Guide 2026 — AI coding tools, KD 5, SV 350
- 6591. Qwen Code Agent Loop Safety and Output Hygiene Guide 2026 — AI coding tools, KD 4, SV 220
- 6592. Laminar Agent Observability MCP Debugging Guide 2026 — AI for developers, KD 4, SV 240
- 6593. GitLab Next Gen SCM for AI Agents Guide 2026 — AI coding tools, KD 4, SV 260
- 6594. MCP Server Production Health Checks and Monitoring Guide 2026 — AI for developers, KD 5, SV 300

## Validation

Every promoted candidate passed the run checks: KD within 0-25, estimated search volume >= 200, required title/slug/keyword present, focus-topic or cluster-priority fit, no exact slug match in `research/topics.json` before append, and no published filename match in `content/posts`.

## Strategy Adjustment

### New Cluster: Agent Delivery/Orchestration Layer
The emergence of Kepler (ADE), Omnigent (meta-harness), Eve (filesystem-first framework), Flue (Pi-based framework), and Agent Canvas (automation workspace) within a single week signals a new architectural tier above individual agent harnesses. This "meta-orchestration" layer is the most important new category since MCP. Focus: 2-3 more topics covering runtime comparison and architectural patterns once primary sources stabilize.

### Agent Discovery Standards
ARD + MCP + A2A create a three-standard discovery landscape. The ARD specification is brand new and warrants close monitoring for implementation guides as client support broadens.

### MCP Operations Deepening
MCP security content is maturing from "add auth" to "75-point audit checklists." Production health checks, monitoring, and incident response for MCP servers remain under-addressed vs the depth of comparable API gateway operations content.

### Next Run Guidance
Avoid repeating: agent delivery/orchestration layer (Kepler, Omnigent, Eve, Flue, Agent Canvas — already covered), agent discovery standards (ARD — already covered), GitLab Orbit/Governance/SCM (already covered), new observability entrants (Omium, Dynatrace, Latitude — already covered). Strong remaining opportunities: production MCP server incident response runbooks, multi-agent orchestration (Kepler vs Omnigent vs Eve comparison), and agent-to-agent protocol interoperability testing.

## Sources Consulted

- https://www.gitkraken.com/blog/introducing-kepler-the-delivery-engine-for-agent-driven-development
- https://www.databricks.com/blog/introducing-omnigent-meta-harness-combine-control-and-share-your-agents
- https://vercel.com/changelog/introducing-eve-an-open-source-agent-framework
- https://blog.cloudflare.com/agents-platform-flue-sdk/
- https://www.openhands.dev/blog/introducing-agent-canvas
- https://github.blog/changelog/2026-06-17-agent-finder-for-github-copilot-now-available/
- https://itbrief.ca/story/gitlab-unveils-tools-for-governed-agentic-software-delivery
- https://blog.jetbrains.com/junie/2026/06/junie-coding-agent-out-of-beta/
- https://ngtech.app/insights/2026-06-13-qwen-code-v0-18-0-improves-copied-output-hygiene-and-agent-loop-safety
- https://www.digitalapplied.com/blog/mcp-server-security-audit-75-point-checklist-2026
- https://stacklok.com/blog/mcp-security-best-practices-what-every-enterprise-team-needs-to-know-in-2026/
- https://omium.ai/
- https://laminar.sh/
- https://latitude.so/
- https://www.dynatrace.com/solutions/ai-observability/
- https://www.digitalapplied.com/blog/mcp-server-security-best-practices-2026-engineering-guide
- https://particula.tech/blog/mcp-server-security-hardening-production-checklist
- https://www.exploreagentic.ai/insights/mcp-server-security-hardening/
- https://aws.amazon.com/blogs/machine-learning/amazon-bedrock-agentcore-harness-is-now-generally-available/
