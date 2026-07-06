---
cover:
  alt: AI Agent Production Go-Live Checklist 2026
  image: /images/ai-agent-production-go-live-checklist-2026.png
  relative: false
date: 2026-06-20 12:00:00+00:00
description: 45 production readiness checks for AI agents across 6 domains — security,
  observability, cost controls, eval gates, HITL, and incident response. With sc...
draft: false
schema: schema-ai-agent-production-go-live-checklist-2026
tags:
- ai agent production readiness
- agentic ai deployment checklist
- enterprise ai agent go-live
- ai agent governance
- agent observability monitoring
title: 'AI Agent Production Go-Live Checklist 2026: 45 Checks Before You Deploy'
---

78% of enterprises have AI agent pilots running, but only 14% have scaled to production — that is an 88% failure-before-production rate, and the top barrier is not model capability but governance, observability, and operational readiness (LangChain, Zepic, and Harness Engineering surveys, all 2026). This checklist gives you 45 concrete pass/fail checks across 6 domains with scoring thresholds to gate your deployment decision.

---

## Why 88% of AI Agent Pilots Never Make It to Production

The research data is consistent across every source I reviewed. Agents are technically working in pilots — the model can complete the task — but they stall before production for structural reasons that have nothing to do with model quality:

- **Only 24% of organizations have full visibility into what their agents are doing** (Zepic, 2026). You cannot deploy what you cannot see.
- **Top barrier: output quality** — 32% of respondents per the 2026 LangChain State of Agent Engineering survey, but output quality is usually a symptom of missing evaluation gates rather than a model problem.
- **Only 52% run any offline evaluations before shipping** (LangChain). The teams that ship are the ones that evaluate.
- **Data readiness (43%) and lack of technical maturity (43%)** are the top organizational obstacles (Moxo, 2026).

I have seen this pattern play out across multiple teams: the agent works in a demo, fails in staging because of a tool timeout, fails again because token costs blow past budget, and the deployment gets shelved indefinitely because there is no structured process to resolve each category of failure.

This checklist is the structured process. It is organized into three tiers — **Blocking** (must pass, score 0 or 1), **Risk-Reducing** (score 0-2), and **Maturity-Building** (score 0-3) — so you can calculate a composite readiness score and gate your production deploy on a threshold. I use a minimum score of 32 out of 45 total possible points before approving a production launch, with zero fails in any Blocking item.

## Domain 1: Security and Access Control (Blocking — 8 checks)

These are non-negotiable. If any of these fail, do not deploy.

| # | Check | Pass/Fail |
|---|---|---|
| 1 | Agent uses least-privilege credentials scoped to specific tools and APIs, not broad service accounts | P/F |
| 2 | Tool-level allowlist enforced (no denylist-only approach) | P/F |
| 3 | Credentials expire after task completion — no persistent long-lived keys | P/F |
| 4 | SSO, MFA, and RBAC implemented from day one (StackAI, 2026) | P/F |
| 5 | Input guardrail layer scans for prompt injection and PII leakage | P/F |
| 6 | Output guardrail layer validates against schema and business rules | P/F |
| 7 | Action guardrail layer requires confirmation before irreversible writes | P/F |
| 8 | Agent operates within defined workspace boundaries by team/function | P/F |

The three guardrail layers (input → output → action) come from the Stack Archive field research and are the single highest-impact pattern for production safety. I implement them as middleware in the agent runtime, not as prompt instructions — prompt-level guardrails are trivially bypassed by injection attacks.

### How to Implement Least-Privilege Credentials

If you are using an agent framework like LangGraph, OpenAI Agents SDK, or Google ADK, do not rely on the framework's built-in credential handling. Use a separate secrets service (Vault, AWS Secrets Manager, or a managed solution like WorkOS or Permit.io) that issues task-scoped, time-limited tokens:

```python
# Example: Task-scoped credential issuance
from vault import issue_credential

def on_agent_task_start(task: AgentTask):
    cred = issue_credential(
        agent_id=task.agent_id,
        user_id=task.user_id,
        allowed_tools=task.required_tools,
        ttl_seconds=300  # 5 minutes max
    )
    task.inject_credential(cred)
    return task
```

When the task completes or the TTL expires, the credential is revoked. This pattern alone eliminates the most common production agent security incident: a compromised agent with persistent keys.

## Domain 2: Observability and Monitoring (Blocking — 7 checks)

| # | Check | Pass/Fail |
|---|---|---|
| 9 | Decision trajectory logging, not just output logging | P/F |
| 10 | Every tool call logged with 7 fields (timestamp, agent_id, user_id, action, input, output summary, session_id) | P/F |
| 11 | Centralized telemetry with consistent tagging (conversation_id, agent_version) | P/F |
| 12 | Role-specific dashboards exist (real-time alerts for engineers, cost trends for execs) | P/F |
| 13 | Drift monitoring for schema, output format, and task success rate | P/F |
| 14 | Alerts configured for anomalous agent behavior (spike in tool call failures, latency degradation) | P/F |
| 15 | Rollback plan documented and tested under 5 minutes | P/F |

"Decision trajectory logging" is what distinguishes production-grade agent observability from debugging. You need to know not just what the agent output, but what path it took to get there — which tools it called in which order, why it chose each one (the model's chain-of-thought), and where it deviated from the expected path.

I wrote about this in more detail in the [AI Agent Observability & OpenTelemetry guide](/posts/ai-agent-observability-opentelemetry-2026/), but the short version is: store the full trajectory as structured events in your observability backend (Datadog, Grafana, or an OpenTelemetry-compatible collector).

## Domain 3: Evaluation and Testing (Blocking — 8 checks)

| # | Check | Pass/Fail |
|---|---|---|
| 16 | Minimum 20-30 representative eval test cases covering happy path, edge cases, and failure modes | P/F |
| 17 | Offline eval runs against golden dataset before every deployment | P/F |
| 18 | Regression gates block deploys when scores drop below threshold | P/F |
| 19 | Tool-call regression tests using recorded cassettes (no live API calls) | P/F |
| 20 | Load tested at 2× expected peak concurrent requests | P/F |
| 21 | Load testing includes adversarial prompts, not just volume | P/F |
| 22 | Shadow evaluation against production traces before canary rollout | P/F |
| 23 | Eval suite re-run on prompt change, model update, tool change, or monthly | P/F |

The 20-30 minimum eval cases figure comes from Stack Archive's production readiness framework, and in practice I have found it to be the minimum viable set. Fewer than 20 and you miss edge cases; more than 100 and the eval suite becomes too slow to run on every PR. The sweet spot is 25-35 cases with a mix of:

- **Golden path** (5-10 cases): the main workflow the agent was built for
- **Edge cases** (5-10): unusual inputs, partial data, missing context
- **Failure modes** (5-10): tool timeouts, rate limits, ambiguous queries
- **Adversarial** (3-5): injection attempts, out-of-scope requests

For a deeper look at how to integrate these eval gates into your CI/CD pipeline, see the [Agent CI/CD Eval Pipeline Integration Guide](/posts/agent-ci-cd-eval-pipeline-integration-guide-2026/).

## Domain 4: Cost Controls and Token Budgeting (Risk-Reducing — 7 checks)

| # | Check | Score (0-2) |
|---|---|---|
| 24 | Per-request token budget enforced in code | 0-2 |
| 25 | Per-user token budget enforced in code | 0-2 |
| 26 | Global token budget with hard stop | 0-2 |
| 27 | Loop detection: error after 3 identical tool calls with same params | 0-2 |
| 28 | Cost dashboard updated in real time | 0-2 |
| 29 | Canary deployment cost gate — auto-rollback if per-request cost spikes >20% | 0-2 |
| 30 | Multi-agent coordinator agent budget capped separately from workers | 0-2 |

The research from Bai et al. shows the same agentic coding task can vary 30× in token consumption with zero correlation to output quality. This means cost controls are not an optimization — they are a safety mechanism. Without per-request budgets, a single runaway agent run can burn through your entire monthly API allocation in minutes.

My recommended implementation uses a token bucket at three levels:

```python
class TokenBudget:
    def __init__(self):
        self.per_request = 50000  # 50K tokens max per agent request
        self.per_user = 500000     # 500K tokens per user per day
        self.global_daily = 50000000  # 50M tokens for the entire deployment

    def check(self, request):
        if request.estimated_tokens > self.per_request:
            raise BudgetExceeded("Request exceeds per-request budget")
        if self.user_total[request.user_id] > self.per_user:
            raise BudgetExceeded("User daily budget exceeded")
        if self.global_total > self.global_daily:
            raise BudgetExceeded("Global daily budget exhausted")
```

The separate coordinator-agent budget comes from Salim et al. "Tokenomics" (arXiv:2601.14470): coordinator agents in multi-agent systems consume 40-60% of total tokens. If you budget all agents together, the coordinator will starve the workers. Budget them separately.

For a detailed breakdown of token attribution strategies, check the [Agent Token Cost Attribution guide](/posts/agent-token-cost-attribution-2026/).

## Domain 5: Human-in-the-Loop and Escalation (Risk-Reducing — 7 checks)

| # | Check | Score (0-2) |
|---|---|---|
| 31 | 100% human review at launch for all irreversible actions | 0-2 |
| 32 | Staged autonomy plan defined (category-by-category removal over 2-4 weeks) | 0-2 |
| 33 | Human escalation pathways function when agent itself is the failure mode | 0-2 |
| 34 | Tiered approval gates: Tier 1 auto, Tier 2 async approval, Tier 3 synchronous | 0-2 |
| 35 | Approval SLA defined for Tier 2 and Tier 3 actions | 0-2 |
| 36 | Kill switch that pauses all agent execution in under 60 seconds | 0-2 |
| 37 | Incident response runbook specific to agent behavior failures | 0-2 |

Staged autonomy is the most operationally important pattern for high-risk agent deployments. You do not start with full autonomy. You start with 100% human review, measure the agent's false-positive rate and the human reviewer's override rate, and remove human review category by category over 2-4 weeks.

The Stack Archive research found that teams using staged autonomy achieved production deployment in 6-8 weeks vs. teams attempting full autonomy from day one, which averaged 14+ weeks with a 60%+ chance of reverting to pilot.

The kill switch is specifically tested with a timer. I have seen production incidents where the kill switch existed in the codebase but took an engineer 18 minutes to find, authenticate, and trigger. It should be a single button in your monitoring dashboard with a pre-authenticated session.

## Domain 6: Incident Response and Rollback (Maturity-Building — 8 checks)

| # | Check | Score (0-3) |
|---|---|---|
| 38 | Canary deployment strategy with graduated rollout (5% → 25% → 100%) | 0-3 |
| 39 | Auto-rollback trigger configured and tested | 0-3 |
| 40 | Rollback tested with sub-60-second kill switch (timer-verified) | 0-3 |
| 41 | Version history and rollback for agent workflows touching sensitive data | 0-3 |
| 42 | Incident paths defined: how to pause agent, roll back change, revoke access | 0-3 |
| 43 | Post-mortem process specific to agent failures (not generic incident process) | 0-3 |
| 44 | Agent scoring below 80% classified as Experimental — gated from production | 0-3 |
| 45 | Compliance checks re-run on every agent version bump | 0-3 |

The 80% threshold comes from the AI Reliability Institute's 30-Point Agentic Reliability Enforcement Checklist v1.3, which classifies agents scoring below 80% as Experimental and unsuitable for production. I use this as a hard gate in my own deployments.

Canary deployment for agents is harder than for traditional services because agent behavior is stochastic. A 5% canary that shows no errors may still degrade task completion by 15 points. The solution is dual monitoring: track both traditional metrics (latency, error rate, cost) and agent-specific metrics (task success rate, tool-call accuracy, trajectory divergence from baseline). Auto-rollback on either set.

### The 5-Minute Rollback

Every source I reviewed converged on sub-5-minute rollback as the production standard. The practical implementation:

1. **Infrastructure rollback**: `kubectl rollout undo deployment/agent-worker` or equivalent — takes 30 seconds
2. **Configuration rollback**: Feature flag that switches agent traffic to the previous version — takes 10 seconds
3. **Full stop**: Kill switch that pauses all agent execution — takes 5 seconds

Test all three paths under a timer before declaring production readiness. I have seen teams pass the infrastructure rollback and fail the configuration rollback because the feature flag was not wired to the agent router.

## Scoring and Deployment Gating

Total possible score: 45 (8 Blocking × 1 + 7 Risk-Reducing × 2 + 8 Maturity-Building × 3)

| Score | Verdict | Action |
|---|---|---|
| 0-15 | Experimental | Do not deploy. Address Blocking failures first. |
| 16-31 | Conditional | Deploy with restrictions. Full human review required. |
| 32-45 | Production Ready | Proceed with canary rollout. |

The Blocking items are pass/fail with no partial credit. If any Blocking check fails, the deployment is blocked regardless of total score. This is not negotiable — I learned this the hard way after a production incident caused by missing output guardrails that a "good enough" overall score had masked.

## FAQ

### What is the single most important check in this checklist?

Input guardrail layer (check #5) and trajectory logging (#9) tie for first. Without input guardrails, your agent can be prompt-injected. Without trajectory logging, you cannot debug why it happened. Every production incident I have responded to traces to one of these gaps.

### How long does it take to go through this checklist?

Plan for 4-8 weeks for the first pass through all 45 checks if starting from scratch. Teams that have already implemented observability and basic eval can do it in 2-3 weeks. The staged autonomy timeline adds another 2-4 weeks for high-risk actions.

### How often should I re-run these checks?

Re-run all Blocking checks on every deployment. Re-run the full checklist on model change, tool change, prompt update, or monthly (per Harness Engineering's recommendation). The AI Reliability Institute adds a specific trigger: any incident that causes a rollback triggers a full re-check.

### What is the difference between this checklist and the 25-check one from Harness Engineering?

Harness Engineering's 25 checks focus on functional correctness and technical verification (a subset of our Domain 3). This checklist covers the full production surface area — security, observability, cost, compliance, HITL, and incident response — at 45 checks across 6 domains with a unified scoring system and deployment gating thresholds.

### Can I skip the maturity-building checks and still go to production?

Yes, if you accept the risk. A score of 16-31 qualifies as "Conditional" — deployable with restrictions (full human review, canary-only, no auto-scaling). I would not run a customer-facing agent at that level, but internal tooling agents can operate conditionally while you build up the maturity checks.