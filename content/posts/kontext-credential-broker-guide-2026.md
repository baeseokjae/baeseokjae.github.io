---
title: "Kontext Credential Broker Guide 2026: Secure Credential Management for AI Coding Agents"
date: 2026-08-02T23:02:35+00:00
tags:
  - kontext
  - credential broker
  - AI agents
  - Claude Code
  - Codex
  - runtime security
  - AI security
description: "Learn how Kontext CLI acts as a credential broker for AI coding agents, providing short-lived credentials, runtime policy enforcement, and audit trails without exposing secrets."
draft: false
cover:
  image: "/images/kontext-credential-broker-guide-2026.png"
  alt: "Kontext Credential Broker Guide 2026: Secure Credential Management for AI Coding Agents"
  relative: false
schema: "schema-kontext-credential-broker-guide-2026"
---

## What is Kontext CLI?

Kontext CLI is an open-source credential broker and runtime security tool built specifically for AI coding agents. It intercepts every tool call made by agents like Claude Code, Codex, and Claude Cowork, brokers short-lived credentials at request time, and enforces security policies before any action reaches your infrastructure. Unlike traditional secrets managers that just store credentials, Kontext actively controls how and when agents use them.

## What is a Credential Broker for AI Agents?

A credential broker is a security layer that sits between an AI coding agent and the services it needs to access. Instead of giving the agent a long-lived API key or database password, the broker issues short-lived, scoped credentials on demand for each individual tool call. The agent never holds the actual secret — it receives a temporary token valid only for the specific operation it needs to perform.

This pattern is rapidly becoming essential infrastructure for teams deploying AI coding agents in production. The IETF is formalizing the concept through the CB4A (Credential Broker for Agents) Internet-Draft, which specifies that agents should never hold real long-lived credentials and should use workload identity systems like SPIFFE/SPIRE for authentication.

### How Kontext Differs from Traditional Secrets Management

Traditional secrets managers like HashiCorp Vault, AWS Secrets Manager, or 1Password are designed for human operators and CI/CD pipelines. They provide credential storage, rotation, and access control, but they assume the consumer is a trusted process with deterministic behavior. AI agents break this assumption because:

- **Agents are non-deterministic** — the same prompt can produce different tool calls each time
- **Agents can be manipulated** — prompt injection can trick an agent into calling tools the user never intended
- **Agents operate at machine speed** — a compromised agent can exfiltrate hundreds of credentials in seconds

Kontext addresses these gaps by combining credential brokering with runtime policy enforcement. It doesn't just hand over credentials — it evaluates each request against a policy engine before releasing them.

## Why Do AI Agents Need a Credential Broker?

The four most common credential patterns used with AI coding agents are all fundamentally broken:

| Pattern | How It Works | The Problem |
|---------|-------------|-------------|
| Hardcoded API keys | Keys embedded in `.env` files or agent config | Any prompt injection leaks every key instantly |
| Shared service accounts | One token used by the whole team | No audit trail, no per-user revocation |
| Token passthrough | Agent forwards the user's personal access token | Agent can use the token for anything, anywhere |
| Long-lived PATs | Personal access tokens with no expiration | Compromise means indefinite access until manually revoked |

### Prompt Injection Becomes a Systems Attack with Credentials

When an AI agent holds credentials, prompt injection stops being a content-quality problem and becomes a systems security incident. An attacker who injects a malicious instruction into a file the agent is reading can trick it into:

- Reading every secret from the secrets manager
- Making unauthorized API calls to production services
- Exfiltrating data through HTTP requests or git pushes
- Modifying infrastructure configurations

Kontext's pre-tool-use blocking architecture prevents this by evaluating every tool call against policy *before* the credential is released. If the agent tries to make an API call that doesn't match the allowed scope, Kontext blocks it regardless of what the agent's prompt says.

### Unlimited Blast Radius and No Surgical Revocation

Without a credential broker, a compromised agent has access to everything the credential it holds can do. If an agent is using a user's personal access token with read-write scope on all repositories, a single successful injection attack can modify any codebase, delete resources, or exfiltrate data across the entire organization.

With Kontext, each credential is scoped to a specific operation. If an agent is compromised mid-session, the blast radius is limited to the credentials already issued — and those credentials expire within minutes. The attacker cannot request new credentials because the policy engine blocks requests that don't match the approved scope.

## Kontext Architecture Overview

Kontext uses a control plane / data plane architecture inspired by NIST SP 800-207 (Zero Trust Architecture), the same framework that informs the CB4A IETF draft.

### Control Plane vs Data Plane

The **control plane** handles policy evaluation, credential brokering, and audit logging. It runs as a local daemon on the developer's machine and can optionally sync to the Kontext cloud dashboard for team-wide visibility.

The **data plane** is the actual API calls made by the AI agent. Kontext intercepts these at the agent integration layer — through Claude Code's pre-tool-use hooks, Codex's command wrappers, or MCP server interceptors. The data plane never touches credentials directly; it only receives short-lived tokens from the control plane.

### Local-First Decision Path with Optional Cloud Export

Kontext is designed to work entirely offline. All policy decisions are evaluated locally on the developer's machine, which means:

- **Zero latency** — policy checks complete in ~22ms for the SVM classifier
- **No cloud dependency** — the agent keeps working even without internet access
- **Privacy by default** — sensitive API call details never leave the machine

For enterprise teams, Kontext offers a managed mode where audit logs and policy configurations sync to a cloud dashboard. This gives security teams visibility across the organization without compromising the local-first performance model.

### The 3-Layer Authorization Model

Kontext enforces policies at three levels:

1. **Org-level policies** — defined by the security team, apply to all agents in the organization. These might include "block all write operations to production databases" or "require approval for any deployment command."

2. **User-level policies** — defined by individual developers for their own agents. These might include "allow read access to staging API but require confirmation for write operations."

3. **Application-level policies** — defined per agent or per project. These might include "Claude Code can access the GitHub API but only for pull request operations."

This layered model means a single Kontext installation can serve different security postures for different teams, projects, and agent types.

## Installation and Setup

### macOS Quickstart with Homebrew

Installing Kontext on macOS takes less than a minute:

```bash
brew tap kontext-security/tap
brew install kontext
```

This installs the `kontext` CLI binary, the local daemon, and the default policy set. After installation, you need to create an install token to link your local instance to your Kontext account.

### Creating an Install Token in the Kontext Dashboard

1. Navigate to the Kontext dashboard at [https://kontext.security](https://kontext.security)
2. Create an account or sign in with GitHub OAuth
3. Go to Settings → Install Tokens → Generate New Token
4. Copy the token and run:

```bash
kontext auth --token YOUR_INSTALL_TOKEN
```

This links your local CLI to your Kontext account, enabling cloud sync for audit logs and policy management.

### Verifying Setup with kontext doctor

Kontext includes a diagnostic command that verifies every component is working correctly:

```bash
kontext doctor
```

This checks:
- The local daemon is running and healthy
- The install token is valid
- The default policy set is loaded
- Agent integrations are properly configured
- The SVM risk classifier model is downloaded

If everything passes, you'll see a green checkmark for each component. If any check fails, `kontext doctor` provides specific remediation steps.

## Supported AI Coding Agents

Kontext supports three major AI coding agents with deep integrations that go beyond simple credential injection.

### Claude Code Integration (Pre-Tool-Use Blocking)

Claude Code integration is Kontext's flagship feature. It uses Claude Code's pre-tool-use hook system to intercept every tool call *before* it executes. This means:

- Kontext evaluates the tool call against policy before Claude Code sends it to the API
- If the call is blocked, Claude Code never sees the credential and never makes the request
- The user sees a clear explanation of why the call was blocked

Configuration is done through Claude Code's project settings:

```json
{
  "hooks": {
    "preToolUse": "kontext hook claude"
  }
}
```

### Codex Hook Configuration

For OpenAI Codex, Kontext provides a command wrapper that intercepts tool calls at the shell level:

```bash
codex --hook "kontext hook codex"
```

This wraps every Codex tool execution in a Kontext policy check. The integration supports all Codex tool types including file operations, shell commands, and HTTP requests.

### Claude Cowork Support

Claude Cowork, Anthropic's collaborative coding environment, is supported through the same pre-tool-use hook mechanism as Claude Code. The setup is identical:

```bash
kontext hook install claude-cowork
```

This installs the hook globally so all Claude Cowork sessions are automatically protected.

## Kontext Guard — Runtime Security

Kontext Guard is the runtime security engine that evaluates every tool call against policy before releasing credentials. It uses a three-tier evaluation pipeline.

### Deterministic Policy for Credential Access and Destructive Commands

The first tier is a deterministic policy engine that evaluates tool calls against explicit allow/deny rules. These rules are defined in YAML and can cover:

- **Credential access** — which credentials can be requested, for which services, by which agents
- **Destructive commands** — blocking `rm -rf`, `DROP TABLE`, `DELETE FROM`, and other dangerous operations
- **Network destinations** — which hosts and ports the agent can connect to
- **File system access** — which directories the agent can read or write

Deterministic policies are evaluated in under 1ms and provide hard guarantees. If a rule explicitly denies an operation, it is blocked regardless of what the risk classifier or guardrail LLM says.

### SVM Risk Classifier (0.987 Precision)

The second tier is a machine learning risk classifier based on a Support Vector Machine (SVM) model. It evaluates each tool call and assigns a risk score based on:

- The type of operation (read vs write vs delete)
- The target service or resource
- The historical context of similar operations
- The agent's recent behavior patterns

The SVM classifier achieves 0.987 precision, meaning it correctly identifies risky operations 98.7% of the time. It processes each decision in approximately 22ms, adding negligible latency to every tool call.

### Guardrail LLM (Qwen3-0.6B) for Edge Cases

The third tier is a small guardrail LLM (Qwen3-0.6B) that handles edge cases the deterministic policy and SVM classifier can't resolve confidently. This model runs locally and evaluates:

- Ambiguous tool calls that don't clearly match any policy rule
- Novel operation patterns the SVM hasn't been trained on
- Natural language descriptions in tool call parameters

The guardrail LLM has 0.585 precision and takes approximately 200ms per decision. It is only invoked when the first two tiers produce a low-confidence result, so it doesn't impact the common case.

### Observe Mode vs Enforce Mode

Kontext Guard operates in two modes:

**Observe mode** logs every tool call and shows what would have been blocked, but allows the operation to proceed. This is ideal for:
- Initial setup and policy tuning
- Understanding what your agents actually do
- Building confidence before enabling enforcement

**Enforce mode** actively blocks policy-violating operations. The agent receives a clear error message explaining why the call was blocked, and the user can review the decision in the audit log.

The recommended adoption path is to start in observe mode for one week, review the audit log, adjust policies, then switch to enforce mode.

## Credential Brokering with Kontext SDK

Beyond runtime security, Kontext provides a credential brokering SDK that integrates with your own applications and MCP servers.

### Short-Lived, Scoped Credentials Per Request

When an agent needs to call an API, Kontext issues a credential that is:

- **Short-lived** — expires in minutes (configurable, default 5 minutes)
- **Scoped** — limited to the specific operation requested
- **Auditable** — every credential issuance is logged with the full context of the request

The credential is delivered directly to the target service, not to the agent. The agent receives a reference or one-time use token that it can exchange for the credential at the service endpoint.

### OAuth 2.0 with PKCE for User Delegation

Kontext uses OAuth 2.0 with PKCE (Proof Key for Code Exchange) for user delegation flows. When an agent needs to act on behalf of a user:

1. The agent requests a credential through Kontext
2. Kontext initiates an OAuth 2.0 PKCE flow with the identity provider
3. The user authorizes the specific scope requested
4. Kontext receives the access token and issues a short-lived derived credential to the agent
5. The agent uses the credential for the single operation

This means the user's long-lived OAuth tokens never leave Kontext's secure storage, and every agent action is explicitly authorized by the user.

### Integration with MCP Servers

Kontext integrates with the Model Context Protocol (MCP) to broker credentials for MCP server connections. When an agent connects to an MCP server, Kontext:

1. Intercepts the MCP connection request
2. Evaluates the requested resource access against policy
3. Brokers the appropriate credential for the MCP session
4. Monitors MCP tool calls for policy violations

This makes Kontext a natural fit for teams building MCP-based agent architectures, as it provides a unified credential and policy layer across all MCP servers.

## Kontext vs Competitors (2026 Landscape)

The credential broker space has seen rapid growth in 2026, with multiple open-source tools emerging. Here's how Kontext compares:

| Feature | Kontext | Postern | Sesame OSS | BlindVault | AgentWrit |
|---------|---------|---------|------------|------------|-----------|
| Runtime policy enforcement | ✅ Yes (3-tier Guard) | ❌ No | ❌ No | ❌ No | ❌ No |
| Pre-tool-use blocking | ✅ Yes | ❌ No | ❌ No | ❌ No | ❌ No |
| Short-lived credentials | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| Audit trail | ✅ Yes | ✅ Yes | ✅ Yes | ❌ No | ❌ No |
| Local-first architecture | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| Cloud dashboard (optional) | ✅ Yes | ❌ No | ✅ Yes | ❌ No | ❌ No |
| Risk classification (ML) | ✅ Yes (SVM 0.987) | ❌ No | ❌ No | ❌ No | ❌ No |
| Guardrail LLM | ✅ Yes (Qwen3-0.6B) | ❌ No | ❌ No | ❌ No | ❌ No |
| Claude Code integration | ✅ Deep (pre-tool-use) | ❌ No | ❌ No | ❌ No | ❌ No |
| Codex integration | ✅ Yes | ❌ No | ❌ No | ❌ No | ❌ No |
| MCP server support | ✅ Yes | ❌ No | ❌ No | ❌ No | ❌ No |
| IETF draft alignment | ✅ Yes (CB4A) | ❌ No | ❌ No | ❌ No | ❌ No |
| GitHub stars | 210 | 9 | 9 | 3 | 3 |
| License | MIT | MIT | Source-available | MIT | MIT |

### Postern — HTTPS Proxy Approach

Postern is a credential-brokering HTTPS proxy for AI agents written in Go. It brokers secrets from 1Password and Bitwarden at request time, meaning agents call authenticated APIs without ever holding credentials. Postern's proxy-based approach works well for HTTP-based tool calls but doesn't provide runtime policy enforcement or pre-tool-use blocking. It has 9 GitHub stars as of August 2026.

### Sesame — Self-Hosted Broker

Sesame OSS is a minimal, source-available, self-hosted edition of the Sesame credential broker. It includes a broker, dashboard, and CLI, all written in Python. Sesame provides credential brokering and audit logging but lacks runtime security features like risk classification or pre-tool-use blocking. It has 9 GitHub stars.

### CB4A IETF Draft — Emerging Standard

The CB4A (Credential Broker for Agents) Internet-Draft is an IETF specification that formalizes the credential broker pattern. It specifies that agents should never hold real long-lived credentials, uses SPIFFE/SPIRE for workload identity, follows the PDP/CDP separation pattern from NIST SP 800-207, and uses DPoP (RFC 9449) for sender-constrained token binding. Kontext is an early implementation of this emerging standard.

### BlindVault and AgentWrit

BlindVault is a secrets manager for AI agents that lets LLM agents use API keys and database passwords without ever seeing plaintext, protected by a master password. AgentWrit provides temporary, task-scoped tokens with automatic revocation and is free for internal use. Both are smaller projects with 3 GitHub stars each and limited integration support.

## Best Practices for Production Deployments

### Start in Observe Mode, Inspect the Ledger

The safest path to production with Kontext is to start in observe mode. Run your AI coding agents normally for one to two weeks while Kontext logs every tool call and shows what would have been blocked. Review the audit ledger to understand:

- What services your agents actually access
- What operations are most common
- Which operations would be blocked under your intended policies
- Whether any legitimate operations would be disrupted

This observation period is critical for building policies that protect without breaking workflows.

### Enable Enforcement Gradually

Once you understand your agent's behavior patterns, enable enforcement in stages:

1. **Start with read-only policies** — block destructive commands first (delete, drop, rm -rf)
2. **Add credential scope restrictions** — limit which credentials each agent can request
3. **Enable risk classification** — turn on the SVM classifier for suspicious patterns
4. **Enable the guardrail LLM** — add the Qwen3-0.6B model for edge case handling

Each stage should be tested for at least a few days before moving to the next.

### Managed Deployment for Enterprise Teams

For enterprise teams, Kontext's managed mode provides:

- Centralized policy management across the organization
- Real-time audit dashboard with search and filtering
- Alerting for policy violations and suspicious patterns
- Role-based access control for policy administration
- Integration with SIEM systems through webhook exports

The managed mode syncs policy decisions and audit logs to the cloud dashboard while keeping the actual credential brokering and policy evaluation local to each developer's machine.

## FAQ

### What is a credential broker for AI agents?

A credential broker is a security layer that issues short-lived, scoped credentials to AI agents on demand for each individual tool call. The agent never holds long-lived secrets — it receives temporary tokens valid only for the specific operation it needs to perform. This limits the blast radius of any compromise and provides full auditability of every credential usage.

### How does Kontext differ from HashiCorp Vault or 1Password?

Traditional secrets managers like Vault and 1Password are designed for human operators and CI/CD pipelines — they store and rotate credentials but assume the consumer is a trusted process. Kontext is built for the non-deterministic nature of AI agents: it combines credential brokering with runtime policy enforcement, risk classification, and pre-tool-use blocking. Vault can store the credentials, but Kontext controls how and when agents use them.

### Does Kontext work offline?

Yes. Kontext is designed as a local-first tool. All policy decisions, credential brokering, and risk classification happen on the developer's machine with no cloud dependency. The SVM classifier processes decisions in ~22ms locally. Cloud sync is optional and only used for team-wide audit dashboards and centralized policy management.

### Which AI coding agents does Kontext support?

Kontext supports Claude Code (with pre-tool-use blocking hooks), OpenAI Codex (through command wrappers), and Claude Cowork (through the same hook system as Claude Code). It also integrates with MCP servers for broader agent ecosystem support. The integration depth varies — Claude Code has the deepest integration with pre-tool-use blocking, while Codex uses shell-level command wrapping.

### Is Kontext free and open source?

Yes. Kontext CLI is released under the MIT license and is free to use. The source code is available on GitHub at github.com/kontext-security/kontext-cli. As of August 2026, the project has 210 GitHub stars, 7 forks, and has shipped 20 releases from v0.5.0 to v0.16.0. The cloud dashboard for managed deployments has separate pricing for enterprise teams.

## Conclusion

The credential broker is rapidly becoming essential infrastructure for teams deploying AI coding agents in production. As the IETF formalizes the pattern through the CB4A draft and multiple open-source tools emerge, the industry is converging on a simple truth: AI agents should never hold long-lived credentials.

Kontext stands out in this landscape by combining credential brokering with runtime security. Its three-tier Guard engine — deterministic policy, SVM risk classification, and guardrail LLM — provides defense in depth that no other credential broker offers. With support for Claude Code, Codex, Claude Cowork, and MCP servers, Kontext covers the major AI coding agent platforms while maintaining a local-first architecture that keeps decisions fast and private.

For teams already using AI coding agents in development or production, adding a credential broker is one of the highest-impact security improvements available in 2026. Start in observe mode, review the audit ledger, and enable enforcement gradually. The credential broker pattern isn't just a nice-to-have — it's becoming the standard way to secure AI agent operations.
