---
title: "Sentry MCP Safe Error Monitoring Setup 2026: Secure Configuration Guide for AI Coding Agents"
date: 2026-07-04T14:00:00+00:00
lastmod: 2026-10-21 00:00:00+00:00
tags: ["sentry", "mcp", "ai-security", "error-monitoring", "claude-code", "cursor", "codex-cli", "oauth", "ssrf"]
description: "A practical 2026 guide to configuring Sentry MCP for AI coding agents: token modes, self-hosted overrides, tool-exposure narrowing, embedded-agent provider pinning, telemetry-based monitoring, and what the project still flags as unfinished."
draft: false
schema: schema-sentry-mcp-safe-monitoring-setup-2026
cover:
  image: "/images/sentry-mcp-safe-monitoring-setup-2026.png"
  alt: "Sentry MCP Safe Monitoring Setup 2026"
  relative: false
---

## Why This Guide Exists

[getsentry/sentry-mcp](https://github.com/getsentry/sentry-mcp) is the URL most people still have, and it no longer names the project: the repository now returns HTTP 301 to [getsentry/toolkit](https://github.com/getsentry/toolkit). The record is active rather than dormant — as of 2026-10-21T00:31Z the resolved `getsentry/toolkit` record reported 936 stars, 165 forks, `archived: false`, and a last push at 2026-10-21T00:02:35Z, with [cli@0.47.0](https://github.com/getsentry/toolkit/releases) published on 2026-10-05. Those counts belong to the resolved `toolkit` record, not to a separate server repository. Sentry describes it as "agentic tooling for Sentry."

The security question that follows the [agentjacking disclosure](/posts/agentjacking-sentry-mcp-attack-guide-2026/) is narrower than "is this safe": it is "which defaults do I have to change before an untrusted event payload reaches a coding agent?" This guide answers that from the project's own documentation, states plainly which controls are not finished, and ends with a checklist you can apply to a deployment.

One boundary up front. Everything below is read from the current `main` README, the operations docs and the telemetry reference in `getsentry/toolkit` on 2026-10-21. I did not run a Sentry MCP deployment or an attack against one for this revision, so nothing here is a benchmark or a penetration-test result.

## What Sentry MCP Actually Is

The [README](https://raw.githubusercontent.com/getsentry/toolkit/main/README.md) is explicit that this is not a general-purpose Sentry API wrapper: "Sentry's MCP service is primarily designed for human-in-the-loop coding agents," focused on "developer workflows and debugging use cases." The remote server "acts as middleware to the upstream Sentry API, optimized for coding assistants like Cursor, Claude Code, and similar development tools."

That sentence is the frame for every control below. You are not hardening a read-only dashboard proxy; you are deciding how much of a live error-tracking tenant an automated agent can see and how it may act on what it reads.

## Authentication: Two Token Paths, One Difference That Matters

Remote deployments expose two distinct paths, and the README keeps them deliberately separate. `Bearer` is "reserved for MCP OAuth access tokens." `Sentry-Bearer` is a passthrough: "the worker does not store, validate, exchange, or refresh the upstream token. It forwards the token through the same Sentry API calls used by OAuth-backed sessions, and the client or upstream provider remains responsible for token lifetime and refresh."

That is the whole security delta, and it is easy to misread as "OAuth is safer, passthrough is unsafe." The real difference is where the upstream Sentry credential lives and who owns its lifetime. [docs/operations/security.md](https://raw.githubusercontent.com/getsentry/toolkit/main/docs/operations/security.md) splits the OAuth path into two distinct tokens: an upstream Sentry token that is "Stored inside the MCP grant props" and "Never sent directly to the MCP client," and a downstream MCP token issued by the MCP OAuth provider, whose encrypted props carry the upstream token, granted skills and optional org/project constraints.

| | `Bearer` (MCP OAuth) | `Sentry-Bearer` (passthrough) |
|---|---|---|
| Who holds the Sentry credential | server side, inside the encrypted MCP grant props | the client or its provider |
| Renewal | worker reuses the stored upstream token while it stays valid; a rejected token forces re-authorization | client/provider responsibility |
| Worker storage of upstream token | stored inside the MCP grant props (encrypted), never sent to the MCP client | explicitly not stored, validated, exchanged or refreshed |
| Good fit | shared or multi-user deployments | sandboxed, single-tenant clients |

Only the second row of that last line is a gap. If you choose passthrough, you inherit the refresh problem: a token that expires mid-session fails as an authentication error inside a tool call, which is harder to diagnose than a login prompt.

For local CLI use the project ships a stdio transport and calls it "still a work in progress," while noting it "is the easiest way to adapt run the MCP against a self-hosted Sentry install." Stdio needs a Sentry User Auth Token with the scopes the README lists — `org:read`, `project:read`, `project:write`, `team:read`, `team:write`, `event:write` — passed as `--access-token` or `SENTRY_ACCESS_TOKEN`:

```bash
export SENTRY_ACCESS_TOKEN="sntrys_..."
npx @sentry/mcp-server@latest --access-token "$SENTRY_ACCESS_TOKEN"
```

Never place that token in a checked-in `mcp.json` or `claude.json`. Environment variables or a secrets manager are the only sane options, because the token is the entire authority boundary.

## Self-Hosted Deployments: What The README Actually Promises

Earlier revisions of this article withdrew an SSRF claim because a code search under the old repository name returned nothing. That withdrawal was wrong, and it is worth showing why: the search was run against the stale name and re-runs as `total_count=0, incomplete_results=true`, while the current name returns 4 hits for `validateRegionUrl` and 3 for `SENTRY_ALLOWED_REGION_DOMAINS`.

The guard is real and documented twice. [packages/mcp-core/src/internal/tool-helpers/validate-region-url.ts](https://raw.githubusercontent.com/getsentry/toolkit/main/packages/mcp-core/src/internal/tool-helpers/validate-region-url.ts) implements `validateRegionUrl(regionUrl, baseHost)` with four rules, three of them numbered in its doc comment: the base host is allowed by default; any other host must be in `SENTRY_ALLOWED_REGION_DOMAINS` and also pass `isSaaSTrustOrigin(regionUrl)`; the protocol must be HTTPS; and URL credentials (`user:pass@`) are rejected by an un-commented body check. [docs/operations/security.md](https://raw.githubusercontent.com/getsentry/toolkit/main/docs/operations/security.md), under "SSRF Protection," states the same rules and lists `sentry.io`, `us.sentry.io` and `de.sentry.io` as the allowlist examples, with `https://eu.sentry.io` and `https://sub.mycompany.com` rejected. Note that the doc's implementation path still says `packages/mcp-server/...` while the code now lives under `packages/mcp-core/...`; read `main` rather than trusting a path in prose.

What the [README](https://raw.githubusercontent.com/getsentry/toolkit/main/README.md) documents for self-hosted installs is configuration:

- `--host` (or `SENTRY_HOST`) points the server at a self-hosted install; leaving it unset targets Sentry SaaS.
- `--insecure-http` exists for self-hosted instances without TLS.
- Setting `SENTRY_HOST` "also drops the `seer` skill from the default set, since Seer is not available on self-hosted Sentry," and you can opt back in with `MCP_SKILLS`.

```bash
npx @sentry/mcp-server@latest --access-token=TOKEN --host=sentry.example.com
```

The practical reading: the self-hosted path is a host-override story. Any SSRF-style control you depend on should be verified in the source at the version you deploy, and `--insecure-http` should be confined to an isolated internal network — plaintext transport hands the token to anything on the path.

## Prompt Injection: Still An Open Merge Request

Error payloads are attacker-influenced text. Anyone who can trigger an exception can put words in an issue title, a stack frame, or a log line, and those words land in a model's context.

The project's fix for the most sensitive read path is [PR #1056, "fix(formatting): wrap get_issue_details output in untrusted data boundary"](https://github.com/getsentry/toolkit/pull/1056), which as of 2026-10-21 is still **open** and last updated 2026-06-05. A companion change, [PR #1045, "feat(mcp): Add structured Sentry tool results"](https://github.com/getsentry/toolkit/pull/1045), is **closed without merging**, last updated 2026-07-28.

The operational consequence is blunt: while the boundary change sits unmerged, assume issue descriptions and event text arrive at your agent as ordinary model input, with no framework-level guarantee that instructions inside them are ignored. Do not read "there is a PR" as "there is a control."

Until that changes, the defensible posture is architectural rather than prompt-level:

1. Keep the agent's Sentry tool surface read-mostly, and treat any output containing shell commands, URLs, or "ignore previous" phrasing as hostile by default.
2. Put a relay or gateway between the agent and Sentry MCP that strips markdown code fences, inline code, and command-shaped strings from descriptions before they reach the model:

```typescript
// Relay filter — strip markdown code blocks and command-shaped lines
function sanitizeErrorDescription(description: string): string {
  return description
    .replace(/```[\s\S]*?```/g, '[code block removed]')
    .replace(/`[^`]+`/g, '')
    .replace(/#{1,6}\s+.+/g, '')
    .replace(/npx\s+\S+/g, '[command removed]');
}
```

3. Require human approval for anything the agent wants to execute that originated in tool output.

A filter like the one above removes obvious payload carriers; it is not a parser and will not stop prose instructions. Its value is that it fails visibly in review, not silently in production.

## Tool Exposure: Narrow At Connect Time

The default is wide. Per the [README](https://raw.githubusercontent.com/getsentry/toolkit/main/README.md), "Direct remote auth defaults to all active MCP skills," and narrowing happens at connect time with query parameters or CLI flags:

```bash
# Remote URL: restrict to the tools you actually need
# https://your-deployment.example/mcp/your-org?skills=inspect,triage

# CLI equivalent
npx @sentry/mcp-server@latest --access-token=TOKEN --skills=inspect,triage
npx @sentry/mcp-server@latest --access-token=TOKEN --disable-skills=project-management
```

The Claude Code plugin adds a second layer that is easy to overlook: installing it registers a `sentry-mcp` subagent that "Claude automatically delegates to when you ask about Sentry errors, issues, traces, or performance." An agent that delegates without a human in the loop inherits whatever skill set you exposed, so the exposure decision is the delegation decision. Review the plugin's subagent configuration against the skills you granted rather than assuming the two agree.

There is also an experimental channel — `claude plugin install sentry-mcp@sentry-mcp-experimental` in the plugin flow, and `?experimental=1` on the remote URL. The project instruments that flag with a dedicated metric, `app.server.mode.experimental`, described in [TELEMETRY.md](https://raw.githubusercontent.com/getsentry/toolkit/main/TELEMETRY.md) as tracking "`?experimental=1` or stdio `--experimental` adoption." Being able to count adoption is not a safety argument; keep it out of production.

## Embedded Agent: Pin The Provider

The AI-powered search tools require an LLM provider — "OpenAI, Azure OpenAI, Anthropic, or OpenRouter" — and without one "these specific tools will be unavailable, but all other tools will function normally." Provider choice is `EMBEDDED_AGENT_PROVIDER`, and the README's instruction is unusually direct: "Always set `EMBEDDED_AGENT_PROVIDER` to explicitly specify your LLM provider. Auto-detection based on API keys alone is deprecated and will be removed in a future release."

Both halves of that instruction live in [docs/operations/embedded-agents.md](https://raw.githubusercontent.com/getsentry/toolkit/main/docs/operations/embedded-agents.md), and the README's environment block states the shorter version: `EMBEDDED_AGENT_PROVIDER` is "Required when multiple provider keys are set." The doc adds the resolution order — explicit configuration first (`EMBEDDED_AGENT_PROVIDER` or `--agent-provider`), then conflict detection, then key-based auto-detection as the lowest priority and marked **deprecated**, with a deprecation warning logged when that fallback is used. Conflict detection is the part worth knowing: if several provider keys are set without an explicit provider, the server throws an error rather than picking one, and the doc's stated rationale is "This prevents silent bugs when external tools inject API keys." So the failure mode in a shell with several keys is a startup error, not a silently different provider.

```bash
# Pin explicitly whenever more than one provider key can be present
export EMBEDDED_AGENT_PROVIDER="openai"
export OPENAI_API_KEY="sk-..."
```

Use a dedicated key for Sentry MCP rather than a shared production key, so that revoking the agent's access does not take down something else, and so that the agent's spend is attributable.

## Monitoring the Monitor: Observability Setup

Sentry MCP instruments itself, and the repository publishes the attribute contract in [TELEMETRY.md](https://raw.githubusercontent.com/getsentry/toolkit/main/TELEMETRY.md). The parts worth knowing when you audit an agent:

- `gen_ai.tool.name` — which MCP tool was called, carried on spans and issues.
- `mcp.session.id` — MCP session identity, for reconstructing a session timeline.
- `gen_ai.provider.name` and `gen_ai.request.model` — which provider and model handled a request.
- `app.transport` — transport in use (stdio, SSE, or HTTP).
- `app.server.response` — the response-rate metric, queryable by `http.route` and paired with `app.response.reason` and `app.rate_limit.scope` for local rate-limit diagnosis.

The documented query recipes are the useful part, because they turn "look at the dashboard" into something reproducible. [TELEMETRY.md](https://raw.githubusercontent.com/getsentry/toolkit/main/TELEMETRY.md) carries a recipe for MCP mode adoption by client family, and this is the exact line as written there:

```text
dataset=tracemetrics query='metric:app.server.response http.route:"/mcp/:organizationSlug?/:projectSlug?"'
```

The companion recipe for response rates by route and status swaps in a concrete route and adds an aggregation, which is the form you want in a runbook:

```text
dataset=tracemetrics query='metric:app.server.response http.route:"<route>"'
aggregate=sum(value) by http.route,http.response.status_code
```

A tool timeline is read from spans filtered on `gen_ai.tool.name`.

That gives you the what. It does not give you the why, and this is the honest limit of alert-driven monitoring: a Sentry alert tells you that a tool failed and roughly when, but the ordered sequence of calls, arguments and results that produced the failure is a different artifact, and reconstructing it from span attributes is manual work. The target page puts the distinction well: "Dashboards show you totals; the transcript shows you the sequence."

When an alert points at an unexpected tool call and you need that sequence, the practical next step is to audit the recorded transcript rather than to keep querying aggregates. [ToolReplay: auditing an agent session for non-determinism and scope overreach](/posts/toolreplay-agent-tool-call-audit-2026/) walks through a bounded method for exactly that: ToolReplay v0.6.0 is a dependency-free Python CLI that replays one recorded tool-call transcript and reports non-determinism, redundant calls and permission overreach, with the reproduced run, the three detector rules and its own documented blind spots on the page. It reads a local transcript file — it is not a Sentry integration, it does not replace Sentry alerting, and it cannot see calls your agent did not record.

The pairing is the point: Sentry tells you a session went wrong, the transcript audit tells you what the session did. Neither one covers the other's blind spot.

## Production Checklist

**Authentication**
- [ ] Choose `Bearer` (MCP OAuth) for shared deployments; reserve `Sentry-Bearer` for sandboxed single-tenant clients and own the refresh problem
- [ ] For stdio: pass `SENTRY_ACCESS_TOKEN` or `--access-token`, never a checked-in config file
- [ ] Scope the Sentry token to the minimum orgs and projects the agent needs

**Tool Exposure**
- [ ] Narrow with `?skills=inspect,triage` or `--skills=` / `--disable-skills=`
- [ ] Review what the Claude Code plugin's delegated subagent can reach, not just the server flags
- [ ] Keep the experimental plugin or `?experimental=1` out of production

**Prompt Injection**
- [ ] Track whether PR #1056 has merged; until then treat issue and event text as untrusted model input
- [ ] Deploy a relay that strips code fences and command-shaped strings from descriptions
- [ ] Require human approval for commands that originated in tool output
- [ ] Run a scanner such as [MCP-Scan, now Snyk Agent Scan](https://github.com/snyk/agent-scan) against your MCP configuration

**Embedded Agent**
- [ ] Set `EMBEDDED_AGENT_PROVIDER` explicitly whenever more than one provider key can be present
- [ ] Use a dedicated API key and not a shared production one
- [ ] Leave the AI-powered search tools off if you do not need them

**Self-Hosted**
- [ ] Point at your install with `--host` / `SENTRY_HOST`; confirm which skills that drops
- [ ] Avoid `--insecure-http` outside an isolated internal network
- [ ] Verify `validateRegionUrl` and the `SENTRY_ALLOWED_REGION_DOMAINS` allowlist still match the version you deploy

**Monitoring**
- [ ] Confirm `gen_ai.tool.name`, `mcp.session.id` and `app.server.response` are queryable in your Sentry project before you rely on them
- [ ] Build the metrics query for `app.server.response` by route once, and keep it in your runbook
- [ ] Decide in advance which alerts escalate to a transcript audit, and where the transcript is retained

## The Bottom Line

Sentry MCP's token separation, connect-time skill narrowing and published telemetry attributes are real, documented controls, and they cover most of what a team needs to run an agent against production errors. Two things are not covered: the untrusted-data boundary for issue text is still an open pull request, and the embedded agent's provider should be pinned rather than inferred. Configure those two deliberately and the remaining risk is the ordinary one — the agent can see whatever your Sentry token can see.

For the wider picture, see the [Agent Skills Supply Chain Security Guide](/posts/agent-skills-supply-chain-security-guide-2026/) and the [AI Agent Identity Framework](/posts/ai-agent-identity-framework-guide-2026/) for zero-trust patterns, and start with the [agentjacking deep dive](/posts/agentjacking-sentry-mcp-attack-guide-2026/) if you have not read it — understanding the attack is the first step to configuring the defense.

## Sources Checked For This Revision

Primary material read on 2026-10-21 for the claims above, listed so you can re-check them at the same revision:

- Sentry MCP README (fetched from `main`): https://raw.githubusercontent.com/getsentry/toolkit/main/README.md
- Telemetry attribute and query reference: https://raw.githubusercontent.com/getsentry/toolkit/main/TELEMETRY.md
- Security model and SSRF protection: https://raw.githubusercontent.com/getsentry/toolkit/main/docs/operations/security.md
- Region-URL validation source: https://raw.githubusercontent.com/getsentry/toolkit/main/packages/mcp-core/src/internal/tool-helpers/validate-region-url.ts
- Embedded-agent provider resolution: https://raw.githubusercontent.com/getsentry/toolkit/main/docs/operations/embedded-agents.md
- Resolved repository record (stars, forks, `archived`, last push; the old `sentry-mcp` URL 301s here): https://github.com/getsentry/toolkit
- Published releases: https://github.com/getsentry/toolkit/releases
- Untrusted-data boundary pull request: https://github.com/getsentry/toolkit/pull/1056
- Structured tool results pull request: https://github.com/getsentry/toolkit/pull/1045
- ToolReplay transcript-audit article, checked live (HTTP 200, self-canonical, `index, follow`): https://baeseokjae.github.io/posts/toolreplay-agent-tool-call-audit-2026/
- This article's live page, checked live (HTTP 200, self-canonical, `index, follow`): https://baeseokjae.github.io/posts/sentry-mcp-safe-monitoring-setup-2026/
