---
title: "Agentjacking Mitigation Guide 2026: Secure Sentry, Datadog, PagerDuty, and Jira for Coding Agents"
date: 2026-07-04T12:00:00+00:00
tags: ["agentjacking", "ai-security", "sentry", "datadog", "pagerduty", "jira", "mcp", "coding-agents", "prompt-injection"]
description: "A practical 2026 guide to securing Sentry, Datadog, PagerDuty, and Jira integrations against agentjacking attacks on Claude Code, Cursor, and Codex."
draft: false
cover:
  image: "/images/agentjacking-mitigation-guide-2026.png"
  alt: "Agentjacking Mitigation Guide 2026"
  relative: false
schema: "schema-agentjacking-mitigation-guide-2026"
---

Your coding agent trusts the tools it reads. That trust is the vulnerability.

When an attacker poisons a Sentry error report, a Datadog monitor alert, a PagerDuty incident, or a Jira ticket description with hidden prompt injection payloads, your agent doesn't know the difference between a legitimate instruction and a hijack attempt. I've spent the last few months digging into this attack surface across the four most common integrations teams wire up to Claude Code, Cursor, and Codex. Here's what I found and exactly how to fix it.

## What Is Agentjacking and Why Should You Care?

Agentjacking is the exploitation of AI coding agents through poisoned tool outputs. The core problem is structural: agents treat the data they receive from integrated tools as trusted context. When Sentry returns an error report, the agent reads the exception message, stack frame variables, and tags — and if any of those fields contain injected instructions, the agent may follow them.

This isn't theoretical. Invariant Labs demonstrated MCP Tool Poisoning Attacks against Anthropic, OpenAI, Zapier, and Cursor in early 2025. The OWASP Top 10 for Agentic Applications 2026 — built with input from over 100 industry experts — lists prompt injection and tool misuse as top-tier risks. Darktrace's 2026 survey found that 92% of security professionals are concerned about AI agent impact. And 19.5% of CISOs in the State of AI Agent Security 2026 report had already experienced an AI-agent-related security incident.

The attack surface is real, and it's growing. By the end of 2026, Gartner predicts 40% of enterprise applications will include task-specific AI agents. If you're running coding agents today, you need a mitigation strategy for the tools they connect to.

## The Four Critical Integration Risks

Each tool has a different attack vector, but the mitigation patterns are consistent. Let me walk through each one.

### Sentry MCP: Fake Error Reports

Sentry's MCP server lets agents query error events, stack traces, and performance data. The attack vector is straightforward: an attacker injects a fake error report into a Sentry project the agent monitors. The exception value, stack frame variables, tags, or event description contain a prompt injection payload. The agent reads the error, follows the injected instructions, and executes destructive commands.

The Sentry team has been responsive — PR #1056 added XML untrusted data boundary tags around the Description field. But I've found three bypass patterns in testing:

1. **Unsupported event types** — the wrapper only covers the Description field, not stack frame variables, tags, or breadcrumbs
2. **Response Notes enclosed inside the boundary** — the wrapper wraps the entire response, so Notes that should be outside end up inside
3. **Only Description is covered** — tags and extra data fields pass through raw

**Mitigations for Sentry:**
- Apply untrusted data boundary wrapping to ALL Sentry event fields, not just Description
- Use read-only API tokens scoped to minimal Sentry projects
- Implement a tool-call approval queue for any Sentry-triggered write operations
- Strip HTML/XML tags and control characters from Sentry event output before agent processing
- Add LLM eval canary tests that verify prompt-injection resistance on every Sentry MCP deployment

I covered the full attack walkthrough in the [Agentjacking Sentry MCP Attack Guide](/posts/agentjacking-sentry-mcp-attack-guide-2026/).

### Datadog: Poisoned Monitor Alerts and Logs

Datadog integrations typically use API keys or MCP servers to query monitors, dashboards, and logs. An attacker who can create a monitor alert or inject a log entry with a crafted message can hijack any agent that reads that data.

Datadog's API key model supports scoping — you can create restricted keys with read-only access to specific resources. The problem is that most teams don't. They use the same admin-level API key for agent integrations that they use for their CI/CD pipelines.

**Mitigations for Datadog:**
- Create Datadog API keys with read-only scopes for agent integrations — never use admin keys
- Restrict application key permissions to specific dashboards and monitors only
- Apply input sanitization to all Datadog event and monitor data before agent processing
- Use Datadog's restriction policies to limit which data agents can access
- Implement separate Datadog API keys per agent identity for audit trail
- Rotate Datadog API keys every 90 days minimum

### PagerDuty: Crafted Incident Payloads

PagerDuty's REST API and MCP integrations let agents query incidents, acknowledge alerts, and modify on-call schedules. An attacker who creates a fake incident with a crafted title or description can inject instructions that the agent follows.

PagerDuty supports read-only API tokens and scoped OAuth, which is good. But MCP integrations may not enforce field-level untrusted data boundaries on incident and alert data. The incident title, description, and custom details fields all pass through to the agent's context.

**Mitigations for PagerDuty:**
- Use PagerDuty read-only API tokens for agent integrations — never use account-level tokens
- Scope API tokens to specific services and minimal permission sets
- Apply untrusted data boundary wrapping to all PagerDuty incident and alert data
- Implement human-in-the-loop approval for any PagerDuty write operations (acknowledge, resolve, create incidents)
- Use PagerDuty's audit logs to monitor agent-initiated actions
- Rotate PagerDuty API tokens every 90 days

### Jira: Injected Ticket Descriptions and Comments

Jira is the most dangerous integration because it's the most write-heavy. Agents read issue descriptions, comments, and custom fields — and they create, update, and transition issues. An attacker who can create a Jira ticket with an injected description can hijack any agent that reads it.

Jira's API token model is user-scoped with no granular permission model beyond project-level permissions. If your agent uses a personal account's API token, it inherits everything that account can do. Basic auth is deprecated in favor of API tokens, but the permission model hasn't improved.

**Mitigations for Jira:**
- Create dedicated Jira service accounts with minimal project permissions for agent integrations
- Use OAuth 2.0 (3LO) with scoped permissions instead of API tokens where possible
- Apply untrusted data boundary wrapping to all Jira field data (description, comments, custom fields)
- Implement tool-call approval queue for any Jira write operations (create, update, transition issues)
- Restrict agent access to specific Jira projects only
- Enable Jira audit logging and monitor for unusual agent activity patterns
- Never use personal Jira accounts for agent integrations — always use service accounts

## API Token Hygiene for Agent Integrations

Across all four tools, the single highest-impact change you can make is fixing your API token strategy. Here's what I've found works in practice:

**Dedicated tokens per agent.** Every agent gets its own API token. No sharing between agents, no sharing between agents and humans, no sharing between agents and CI/CD pipelines. When you rotate a token, you only affect one agent.

**Read-only by default.** Start with read-only tokens. Grant write access only when you have a specific use case that requires it, and scope that write access to the minimum resources needed.

**Automatic rotation.** Set a 90-day maximum token lifetime. Most platforms support token expiry natively. If yours doesn't, add a calendar reminder and a script that rotates tokens on schedule.

**Secrets management.** Store tokens in a secrets manager — Vault, AWS Secrets Manager, or 1Password. Never in code, never in config files, never in environment variables that get logged. I've seen too many tokens leak through CI/CD logs and debug output.

**Token tagging.** Tag every token with metadata: purpose, owner, expiry date, and the agent identity it belongs to. This makes lifecycle management and audits much easier.

## Untrusted Data Boundaries: Your First Line of Defense

The most effective technical control is wrapping all external tool output in explicit untrusted data boundary markers. The pattern looks like this:

```xml
<untrusted_data>
  <source>sentry_mcp</source>
  <event_id>12345</event_id>
  <content>
    Error: Connection refused on port 5432
    Stack trace: ...
  </content>
</untrusted_data>
```

The agent's system prompt should instruct it to treat anything inside `<untrusted_data>` tags as potentially malicious input, not as instructions. This is the same pattern the Sentry MCP PR #1056 implements, but you need to apply it to ALL fields, not just the Description.

**Sanitization techniques:**
- Strip HTML and XML tags from tool output before it reaches the agent
- Remove control characters and Unicode direction overrides
- Filter known injection patterns (e.g., "ignore previous instructions", "system prompt")
- Truncate excessively long fields that could hide payloads

**LLM eval canary tests.** For every deployment, run automated tests that verify boundary integrity. Create a test Sentry event with an injection payload in each field type, feed it through your sanitization pipeline, and verify the agent doesn't follow the injected instruction. If the test fails, your boundaries have a bypass.

**Known bypass patterns to watch for:**
- Unsupported event types that skip the wrapper entirely
- Nested boundaries that confuse the parser
- Encoding tricks (Unicode normalization, HTML entities, base64)
- Fields that the wrapper developer forgot to cover

## Human-in-the-Loop Approval Queues

Boundaries can be bypassed. That's why you need a second line of defense: approval queues for high-risk tool calls.

**Risk level classification:**
- **Low** (read-only queries) — auto-approve. Reading a Sentry event, querying a Datadog dashboard, listing Jira issues.
- **Medium** (issue updates, incident acknowledgments) — conditional approval. Auto-approve if the change matches expected patterns, flag for review if it doesn't.
- **High** (deletes, infrastructure changes, financial operations) — require human approval every time.

**Structured diffs in the approval UI.** When an agent proposes a change, show the reviewer exactly what will change. A diff view for Jira issue updates. A before/after for PagerDuty incident resolution. The reviewer should be able to verify the change in seconds.

**Rejection feedback loops.** When a reviewer rejects an action, feed the rejection reason back into the agent's context. The agent can then propose an alternative path. This turns rejections into learning opportunities rather than dead ends.

**Track these metrics:**
- Approval items per day
- Approval rate (what percentage of requests are approved)
- Median review time
- Stale items (requests that haven't been reviewed in > 1 hour)

## Least Privilege Architecture for Coding Agents

The WorkOS containment paper got this right: prompt injection may still occur, but the blast radius should be bounded by permissions, not detection. Design your agents as untrusted workers operating inside a policy-controlled perimeter.

**Every tool call is an authorization event.** Don't check permissions once at startup. Validate on every single request. The agent's identity, the tool being called, the resource being accessed, and the action being performed should all be checked against a policy.

**Put policy outside the prompt.** Prompts are not durable security boundaries. An attacker who successfully injects instructions can override any security rules in the system prompt. The policy must live in the runtime — the tool-call router, the API gateway, the authorization layer.

**Separate identities per environment.** Your dev agent should use different API tokens than your staging agent, which should use different tokens than your production agent. This limits blast radius and makes audit trails meaningful.

**Deny-by-default.** Agents can only access explicitly permitted resources. If you haven't configured access to a Jira project, the agent can't read it. If you haven't granted write access to a Datadog dashboard, the agent can't modify it.

I covered the identity and access control layer in more detail in the [AI Agent Identity Framework guide](/posts/ai-agent-identity-framework-guide-2026/).

## Monitoring and Detection

Even with all the above controls in place, you need to detect when something goes wrong.

**Log all agent tool calls.** Every call should record: the agent identity, the tool called, the resource accessed, the action performed, the timestamp, and whether it was approved or rejected. Store this in a centralized logging system.

**Anomaly detection.** Set up alerts for:
- Agent calling tools it doesn't normally use
- Agent operating outside its normal hours
- Agent making an unusual volume of calls
- Agent making failed approval attempts (potential injection probe)

**Dashboards.** Create a dashboard showing agent activity across all integrated tools. I recommend tracking: calls per agent per hour, approval rate over time, top tools called, top resources accessed, and error rate.

**Circuit breakers.** If an agent makes N failed approval attempts in T minutes, pause the agent automatically. This stops an active injection attack from continuing to probe for bypasses.

**Regular audit reviews.** Every month, review the agent activity logs. Look for patterns that don't match expected behavior. Revoke tokens that haven't been used in 90 days. Update permission scopes based on actual usage.

## Putting It All Together: A Mitigation Checklist

Here's the actionable checklist I use when securing a new agent deployment. Order by impact and effort.

**Week 1 — High Impact, Low Effort:**
- [ ] Create dedicated read-only API tokens for each agent integration
- [ ] Store tokens in a secrets manager, not in code or config files
- [ ] Set 90-day token rotation
- [ ] Tag tokens with purpose, owner, and expiry metadata

**Week 2 — High Impact, Medium Effort:**
- [ ] Apply untrusted data boundary wrapping to all tool output fields
- [ ] Implement input sanitization (strip HTML/XML, control characters)
- [ ] Add LLM eval canary tests for boundary integrity
- [ ] Test known bypass patterns (unsupported event types, encoding tricks)

**Week 3 — Medium Impact, Medium Effort:**
- [ ] Implement tool-call approval queue for write operations
- [ ] Define risk levels and auto-approve rules
- [ ] Set up structured diffs in approval UI
- [ ] Configure rejection feedback loops

**Week 4 — Medium Impact, Higher Effort:**
- [ ] Create dedicated service accounts per agent per environment
- [ ] Implement deny-by-default access policies
- [ ] Set up centralized agent activity logging
- [ ] Configure anomaly detection alerts and circuit breakers
- [ ] Schedule monthly audit reviews

## FAQ

**What is agentjacking?**
Agentjacking is an attack where malicious instructions are injected into the data that AI coding agents read from integrated tools like Sentry, Datadog, PagerDuty, and Jira. The agent treats the poisoned data as trusted context and follows the injected instructions, potentially executing destructive actions.

**Which coding agents are vulnerable to agentjacking?**
Any agent that reads external tool output is potentially vulnerable. This includes Claude Code, Cursor, GitHub Copilot, Codex CLI, and custom agent frameworks that integrate with observability and project management tools via MCP servers or REST APIs.

**Can untrusted data boundaries be bypassed?**
Yes. Known bypass patterns include unsupported event types that skip the wrapper, nested boundaries that confuse the parser, and encoding tricks like Unicode normalization and HTML entities. Regular LLM eval canary tests are essential to catch bypasses.

**Should I use API tokens or OAuth for agent integrations?**
OAuth 2.0 with scoped permissions is preferred where available, because it supports granular permission scoping and token revocation. API tokens are a reasonable fallback, but they should be read-only, scoped to minimal resources, rotated every 90 days, and stored in a secrets manager.

**How do I detect an active agentjacking attack?**
Monitor for unusual agent behavior: calls to tools the agent doesn't normally use, operation outside normal hours, unusual call volume, and a spike in failed approval attempts. Set up circuit breakers that pause the agent after N failed attempts in T minutes.
