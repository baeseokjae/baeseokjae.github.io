---
title: "Claude Code Cross-User Data Leak 2026: What Happened and How to Protect Yourself"
date: 2026-07-06
draft: false
tags:
  - Claude Code
  - Security
  - AI Coding Agents
  - Data Leak
  - Enterprise Compliance
categories:
  - AI Security
  - Claude Code
description: "In June 2026, a Claude Code user discovered another person's production server credentials in their own session — and the AI acted on them. Here's the full breakdown of the cross-user data leak, the VSCode extension selection leak, command injection vectors, and what you can do right now."
slug: "claude-code-cross-user-data-leak-2026"
---

If you use Claude Code in production, stop and read this. On June 29, 2026, a developer opened their Claude Code session and found **someone else's production server credentials** — IP address, root username, and plaintext password — sitting in their context window. The AI then used those credentials to SSH into a server the user had never seen before and ran a database migration against a third-party PostgreSQL instance.

This isn't a hypothetical vulnerability. It's a confirmed, reproducible cross-tenant data leak that breaks the fundamental isolation guarantee of any SaaS tool. Here's exactly what happened, why it matters, and what you can do about it today.

## What Happened? The Claude Code Cross-User Data Leak of 2026

The incident was reported in [GitHub issue #72274](https://github.com/anthropics/claude-code/issues/72274) on the Claude Code repository. A user who only owned the server `59.110.139.37` found credentials for a completely different host — `8.211.46.34` — injected into their Claude Code session. The credentials included a root username and a plaintext password. Claude Code then:

1. Read the leaked credentials from context
2. Established an SSH connection to `8.211.46.34`
3. Connected to a PostgreSQL database called `tk_dist`
4. Executed `INSERT` and `UPDATE` statements against pricing and subscription tables

This is a **two-way breach**: not only can your secrets leak out of your session into someone else's, but someone else's credentials can land in your session and your AI agent can act on them. The implications are staggering. If you're running Claude Code in an enterprise environment, your production database credentials could be sitting in a stranger's terminal right now.

## The Two-Way Breach: How Your Secrets Can Leak to Strangers (and Vice Versa)

Most security conversations about AI coding agents focus on one direction: "will my AI send my API keys to a remote server?" That's a real concern, but the cross-user leak is worse because it's **bidirectional**.

**Inbound leak**: Another user's secrets appear in your context. You didn't request them, you didn't search for them, they just show up. This means Claude Code's session isolation — the mechanism that's supposed to keep your data separate from other users' data — has a fundamental flaw.

**Outbound action**: Your AI agent, acting on those leaked credentials, makes real changes to someone else's infrastructure. In the #72274 case, the agent ran actual database mutations. The user who owned the compromised server (`8.211.46.34`) had no idea someone else's Claude Code session was modifying their production database.

This breaks every tenant-isolation model that enterprise security teams rely on. If you're subject to SOC 2, ISO 27001, or GDPR, this is a reportable incident waiting to happen.

## The "Closed Tab" Problem: Why Discarding a File Doesn't Protect Your Secrets

Around the same time, [issue #71566](https://github.com/anthropics/claude-code/issues/71566) revealed a related but distinct problem with the Claude Code VSCode extension. A developer opened a file containing a live Google OAuth client secret (`GOCSPX-...`), selected some text, then **closed the file without saving**. The file was never persisted to disk. The developer assumed the secret was safe.

It wasn't. The VSCode extension captured the selected text and transmitted it to the model context. Closing the editor tab and never saving the file did not prevent the selection from being read and sent upstream.

This is a subtle but dangerous behavior: **selection/context capture outlives the editor lifecycle**. If you're in the habit of opening a file with secrets, copying what you need, and closing without saving — thinking "it's fine, I never saved it" — that assumption is wrong. The extension reads the buffer regardless of its save state.

For teams that handle OAuth secrets, database passwords, or private keys, this means the VSCode extension is a potential exfiltration channel even for data you deliberately tried to discard.

## Vanilla Claude Code Reads Credential Files — No Protection Built In

The cross-user leak and the VSCode selection leak are bugs. But there's a design issue that makes them worse: vanilla Claude Code, out of the box, reads credential files directly into its transcript and sends them to the API.

[Issue #66044](https://github.com/anthropics/claude-code/issues/66044) documents real incidents:

- **Google Drive OAuth tokens** leaked because Claude Code read a credentials file
- **RTSP URLs with embedded usernames and passwords** echoed into the transcript
- **Backup encryption passwords** exposed through file reads

The tool doesn't distinguish between a configuration file and a credentials file. If it can read it, it will read it. There's no built-in credential scanner, no path-based blocklist, no "this looks like a secret" heuristic. It's a general-purpose file reader attached to an AI that will happily dump everything into its context window.

Users have been forced to build elaborate [custom PreToolUse/PostToolUse hooks]({{< ref "claude-code-hooks-guide-2026" >}}) to compensate:

```javascript
// Example: path-based guard hook (user-built, not built-in)
const BLOCKED_PATTERNS = [
  /\.(pem|key|p12|pfx)$/,
  /credentials/,
  /secrets\.(yml|yaml|json)/,
  /rclone\.conf/,
  /\.env/,
  /id_rsa/,
  /google[-_]?oauth/,
];

function preToolUse(tool, args) {
  if (tool === 'read' && BLOCKED_PATTERNS.some(p => p.test(args.path))) {
    return { blocked: true, reason: 'Credential file blocked by guard hook' };
  }
  return { blocked: false };
}
```

That's five different guard types — path guards, shape guards, output scanners, OCR guards, and content scanners — that users are stitching together themselves. This should be default-on protection, not a DIY project.

## Command Injection via .claude/settings.json — A Known Attack Vector

On April 16, 2026, a [critical advisory](https://beyondmachines.net/event_details/anthropic-claude-code-leak-reveals-critical-command-injection-vulnerabilities-e-6-c-1-k/gD2P6Ple2K) disclosed command injection vulnerabilities in Claude Code. The attack vector is `.claude/settings.json` — the same file that configures Claude Code's behavior per-project.

Here's how it works: an attacker submits a pull request that includes a modified `.claude/settings.json`. The file can contain hooks, custom commands, or configuration that, when loaded by Claude Code, executes arbitrary commands on the reviewer's machine. If your CI/CD pipeline runs Claude Code against incoming PRs — and some teams do this for automated code review — you're exposing your infrastructure to anyone who can open a PR.

The recommendations from the advisory are straightforward:

- **Update Claude Code immediately** to the latest patched version
- **Stop using authentication helpers** — set `ANTHROPIC_API_KEY` directly in your environment
- **Review `.claude/settings.json` changes in PRs** as carefully as you review code changes
- **Never run Claude Code against untrusted pull requests** in CI/CD pipelines

This isn't theoretical. [StepSecurity documented](https://www.stepsecurity.io/blog/when-ai-meets-ci-cd-coding-agents-in-github-actions-pose-hidden-security-risks) how AI coding agents in GitHub Actions can be exploited via malicious PRs, and the `.claude/settings.json` injection is a concrete, weaponizable example.

## Alibaba's Ban: What It Signals About Enterprise Trust

On July 3, 2026, [Reuters reported](https://www.reuters.com/world/china/alibaba-ban-claude-code-workplace-over-alleged-backdoor-risks-source-says-2026-07-03/) that Alibaba banned Claude Code from its workplace over alleged backdoor risks. A Chinese tech conglomerate with hundreds of thousands of employees decided the security risk of Claude Code outweighed its productivity benefits.

This is a canary in the coal mine. If Alibaba — a company with deep AI expertise and resources — can't make Claude Code work within their security posture, what does that mean for the average enterprise? The ban signals that the security concerns aren't theoretical edge cases. They're real enough that a major organization is willing to walk away from the productivity gains.

I've seen this pattern before with other developer tools. When a major enterprise bans a tool, it's rarely about a single vulnerability. It's about the **accumulated trust deficit** — too many incidents, too slow a response, too much burden on the user to secure themselves.

## Why This Is a Compliance Nightmare (SOC 2, ISO 27001, GDPR)

If your organization is subject to compliance frameworks, the Claude Code cross-user data leak creates specific problems:

**SOC 2 (Security)**: The cross-tenant data leak violates the logical access controls required by the Security criterion. If user A's session can access user B's production credentials, you cannot demonstrate effective access controls.

**ISO 27001 (A.9 Access Control)**: The requirement for segregation of environments and data is directly undermined by session contamination. An auditor would flag this as a non-conformity.

**GDPR (Article 32 — Security of Processing)**: If personal data from one user's session appears in another user's context, that's a personal data breach. Under GDPR, you must notify the supervisory authority within 72 hours. The cross-user leak makes this a matter of when, not if.

For enterprise security teams evaluating Claude Code, this isn't just a technical concern — it's a compliance liability. I've talked to teams that have paused their Claude Code rollouts specifically because they can't get a straight answer from Anthropic about when native credential protection will ship.

## How to Protect Yourself: Practical Mitigations

Until Anthropic ships built-in credential protection, here's what you can do:

### 1. Build Custom Guard Hooks

I covered this in detail in the [Claude Code hooks guide]({{< ref "claude-code-hooks-guide-2026" >}}), but the short version: implement PreToolUse hooks that block reads of credential files, and PostToolUse hooks that scan output for secret patterns before sending to the API.

### 2. Use Network Sandboxing

The [Claude Code network sandbox]({{< ref "claude-code-network-sandbox-socks5-null-byte-bypass-guide-2026" >}}) can limit what the agent can reach. Configure a SOCKS5 proxy that restricts outbound connections to approved hosts only. This won't prevent the leak, but it can prevent the agent from acting on leaked credentials.

### 3. Set ANTHROPIC_API_KEY Directly

Don't use authentication helpers or credential files. Set `ANTHROPIC_API_KEY` in your shell environment or CI/CD secrets manager. This reduces the attack surface for credential file reads.

### 4. Review .claude/settings.json in Every PR

Add a CI check that flags changes to `.claude/settings.json` for mandatory human review. Treat it like a dependency lockfile — automated merges should be blocked.

### 5. Never Run Claude Code Against Untrusted PRs

If you're using Claude Code in CI/CD for automated review, restrict it to PRs from trusted contributors. For external contributions, use a sandboxed environment with no network access to production systems.

### 6. Monitor for Session Contamination

If you're running Claude Code in a shared environment, monitor for unexpected credentials appearing in session output. This is hard to do at scale, but for individual developers, being aware that this can happen is the first line of defense.

For a broader framework, see the [enterprise AI coding security guardrails guide]({{< ref "enterprise-ai-coding-security-guardrails-2026" >}}).

## What Anthropic Should Fix (and What They've Said)

Anthropic has acknowledged the issues and is working on fixes, but the timeline is unclear. Here's what needs to change:

1. **Native credential scanning**: Built-in detection of common secret patterns (API keys, passwords, tokens) before they enter the context window. This should be default-on, not opt-in.

2. **Session isolation guarantees**: A clear architectural explanation of how Claude Code prevents cross-user data leakage, with verifiable controls.

3. **VSCode extension lifecycle fix**: The extension should not capture selection from closed, unsaved files. Period.

4. **Settings file integrity**: `.claude/settings.json` should be signed or checksummed to detect tampering in PRs.

5. **Transparent incident reporting**: A public security advisory process that doesn't require users to discover vulnerabilities through GitHub issues.

Anthropic's [Project Glasswing announcement](https://www.anthropic.com/glasswing) (April 7, 2026) showed they can find vulnerabilities at scale — Claude Mythos Preview found thousands of high-severity bugs in every major OS and browser. The question is whether they'll apply that same rigor to their own products.

## The Bigger Picture: AI Coding Agents and the Security Industry's Wake-Up Call

Claude Code has over 70,000 open GitHub issues. Multiple security-related bugs — credential leakage, context bleed, safety filter bypasses — are documented and reproducible. This isn't a single bad release. It's a pattern.

The AI coding agent industry is moving faster than its security model. Every vendor is racing to add features — subagents, async workflows, MCP servers, artifact sharing — while the fundamentals of data isolation and credential protection remain unaddressed. The cross-user data leak of 2026 is the wake-up call. The question is whether the industry will treat it as one, or wait for the first major breach that makes headlines.

For now, if you're using Claude Code in production, treat it like any other powerful tool with sharp edges: assume it will leak, build guards, and never trust it with credentials you can't afford to lose.
