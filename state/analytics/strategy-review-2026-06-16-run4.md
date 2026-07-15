# Strategy Review - 2026-06-16 Run 4

## Phase

Current phase: Phase 1 (Days 30-90). No reliable GSC query export was present in `state/analytics/`, so discovery stayed external-data-led and used fresh competitor/source gaps plus strict dedupe.

## Queue State

- Active queued topics before run: 1
- Candidates evaluated: 17
- Promoted to queued: 17
- Rejected: 0
- Priority range added: 6379-6395

## Competitor And Source Gaps

Sources reviewed:

- LangChain/LangSmith: self-hosted LangSmith on Kubernetes and agent sandbox execution.
- Kubernetes: Agent Sandbox for running stateful agents on Kubernetes.
- Northflank: enterprise AI coding-agent deployment infrastructure, BYOC, RBAC, SSO, and audit logs.
- Google Cloud: Agent Executor, Gemini Enterprise Agent Platform, Vertex AI Agent Builder tool governance, and managed MCP servers with IAM Deny controls.
- AWS: Spring AI SDK for Bedrock AgentCore and serverless LangGraph multi-agent systems on AgentCore.
- OpenAI: Frontier enterprise agents, Codex agent loop, and harness engineering.
- Microsoft/Kyndryl: agent behavior governance and policy-as-code controls.
- Endor Labs/Firecrawl: coding-agent security benchmark and harness/cost/accuracy comparisons.

## Topics Added

- LangSmith Self-Hosted Kubernetes Guide 2026: Operate Agent Traces in Your Cluster
- Kubernetes Agent Sandbox Guide 2026: Run Stateful AI Agents Safely on K8s
- Enterprise AI Coding Agent Deployment Guide 2026: BYOC, Sandboxes, RBAC, and Audit Logs
- Google Agent Executor Runtime Guide 2026: Resumable Distributed Agent Deployment
- Gemini Enterprise Agent Platform Guide 2026: Build, Govern, and Optimize Agents
- Vertex AI Agent Builder Tool Governance Guide 2026: Memory, Tool Approval, and Runtime Controls
- Google Managed MCP Servers IAM Deny Policy Guide 2026: Secure Cloud Tools for Agents
- Spring AI Bedrock AgentCore SDK Guide 2026: Java Agents with Runtime, Memory, Browser, and Evals
- LangGraph Bedrock AgentCore Serverless Guide 2026: Build Scalable Multi-Agent Systems on AWS
- OpenAI Frontier Enterprise Agents Guide 2026: Shared Context, Permissions, and Boundaries
- Codex Agent Loop Harness Guide 2026: Tools, Prompts, and Execution Flow Explained
- OpenAI Harness Engineering Guide 2026: Turn Agent Failures into Better Tools and Guardrails
- Endor Labs AI Coding Agent Security Benchmark Guide 2026: Test Agents Against Real CWE Tasks
- Microsoft AI Agent Behavior Governance Guide 2026: Align User, Developer, Role, and Org Intent
- Agent Policy as Code Guide 2026: Deterministic Guardrails for Regulated AI Workflows
- AI Coding Agents Harness Comparison 2026: Cost, Accuracy, Remote Agents, and Benchmarks
- AgentOps Policy Metrics Guide 2026: Track Memory, Gateway, Identity, and Policy Controls

## Rejected Or Skipped

- Skipped before append: `bedrock-agentcore-agentops-guide-2026` and `bedrock-agentcore-multi-tenant-agents-guide-2026` because existing topics already cover them.
- Skipped before append: a direct LangSmith Sandboxes candidate because the keyword already exists in `topics.json`.
- No appended candidates were rejected.

## Strategy Adjustment

The queue now has a fresher implementation-specific mix instead of another generic agent-auth/MCP/OTel refill. Next strategy pass should avoid these newly added implementation topics and look for hands-on deployment guides, runtime cost controls, and enterprise rollout checklists that are not already queued or queued_throttled.

## Validation

Each queued candidate was checked for:

- KD within 0-25
- Estimated search volume of at least 200
- Required title, slug, and keyword
- Slug not already present in `topics.json`
- Slug not already published in `content/posts`
- Keyword not already present in `topics.json`
- Fit with focus topics or current cluster priority
