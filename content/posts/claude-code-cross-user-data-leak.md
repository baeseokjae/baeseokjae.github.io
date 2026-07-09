---
title: "Claude Code Cross-User Data Leak 2026: Privacy Incident and Session Protection Guide"
date: 2026-07-09T12:00:00+00:00
tags: ["Claude Code", "AI Security", "Privacy", "Developer Tools"]
description: "Practical guide to the Claude Code cross-user data leak reports, transcript risks, ZDR limits, and session protection controls."
draft: false
cover:
  image: "/images/claude-code-cross-user-data-leak.png"
  alt: "Claude Code Cross-User Data Leak 2026"
  relative: false
schema: "schema-claude-code-cross-user-data-leak"
---

The Claude Code cross-user data leak is not a publicly confirmed Anthropic breach, but the June 29, 2026 GitHub report is serious enough to treat as an incident pattern: foreign credentials appeared in a session and were allegedly used against a production PostgreSQL host.

## What Happened, And What Is Actually Confirmed?

The cleanest reading is this: a public GitHub issue in `anthropics/claude-code` alleges cross-session credential leakage, while the visible public thread does not show an Anthropic confirmation of root cause as of July 9, 2026. That distinction matters. If you call it a confirmed cross-tenant breach, you are going beyond the public evidence. If you ignore it because it is "just an issue," you are underreacting to a credible security report in the product's own repository.

The central report is [GitHub issue #72274](https://github.com/anthropics/claude-code/issues/72274), opened on June 29, 2026 and labeled `area:security` and `bug`. The reporter says their Claude Code session contained another user's server credentials, including a host, root user, and redacted root password. The assistant then allegedly connected to that host and made read/write changes to a `tk_dist` PostgreSQL database. The reporter also states that their intended server was different from the exposed host.

I've found that privacy incidents around coding agents usually have two separate risks. First, there is the data-isolation question: why did this context appear at all? Second, there is the tool-execution question: why was the agent able to use a credential-shaped string against real infrastructure? Even if the first part later turns out to be local contamination or hallucination, the second part is still a design problem for teams running agentic tools near production systems.

## What Is The 2026 Claude Code Privacy Timeline?

The June 29 report did not appear in isolation. Several adjacent reports in the Claude Code issue tracker describe credentials, transcripts, local session files, and possible context confusion. They are not all the same bug, but together they describe the surfaces a developer should audit.

| Date | Public report | What it claimed | Why it matters |
| --- | --- | --- | --- |
| April 17, 2026 | [Issue #50014](https://github.com/anthropics/claude-code/issues/50014) | After about 30 days of use, a grep found 5 distinct secrets across 34 local session files totaling 418 MB under `~/.claude/projects/`. | Local transcripts are a secret surface, not just chat history. |
| June 26, 2026 | [Issue #71654](https://github.com/anthropics/claude-code/issues/71654) | Claude Code 2.1.193 wrote a GitHub PAT and Forgejo admin token into persisted transcripts through stdout and an exception string. | Tool output and exceptions can persist secrets even when the model did not "intend" to leak them. |
| June 29, 2026 | [Issue #72274](https://github.com/anthropics/claude-code/issues/72274) | Another user's infrastructure credentials allegedly appeared in a session and were used against a production database. | This is the cross-user data leak allegation that raises tenant-isolation concerns. |
| July 4, 2026 | [Issue #74066](https://github.com/anthropics/claude-code/issues/74066) | Claude Code 2.1.199 in an Enterprise ZDR workspace allegedly picked up unrelated "Minecraft temple" context. | ZDR does not remove the need to understand cache, session, workspace, and local context boundaries. |

I am intentionally separating these from the March 2026 Claude Code source-map leak reports. A package source-map exposure and a cross-user session privacy allegation are different classes of incident. Mixing them creates a bigger headline and worse engineering judgment.

## Why Is The Root Cause Still Unconfirmed?

There are at least three plausible explanations, and the public evidence does not let us choose one with confidence.

### Could This Be A Real Cross-Session Or Cross-Tenant Isolation Failure?

Yes, that is the scary version. If a context cache, transcript summary, session resumption object, or prompt-cache key crossed account boundaries, credentials from one user could appear in another user's session. The June 29 report explicitly frames the problem that way and asks Anthropic to audit session context, summaries, transcript links, and cache keys.

That would be a severe privacy incident because coding agents do not only see text. They see repository paths, `.env` snippets, shell output, error logs, hostnames, database names, cloud account IDs, and sometimes credentials. A normal chat context leak is bad. A coding-agent context leak can become operational access.

### Could This Be Local Context Contamination?

Also yes. Claude Code stores and reads local project context. Official [Claude Code data usage docs](https://code.claude.com/docs/en/data-usage) say local clients store session transcripts in plaintext under `~/.claude/projects/` for 30 days by default to support session resumption, adjustable with `cleanupPeriodDays`. Project instructions, shell history, paste caches, debug files, subagent logs, and old transcripts can all become accidental context sources.

When building with agent tools, I have seen stale local context cause surprisingly convincing mistakes: an old staging hostname shows up in a new task, a copied curl command survives in shell history, or a project-level instruction from the wrong directory steers an agent into the wrong repo. That is not a vendor-side tenant breach, but it can still put real secrets into the model's working context.

### Could This Be A Model Confabulation?

It is possible, but it is not a satisfying default answer. Models can invent credentials, infrastructure details, or database names. The reason #72274 is more serious than a normal hallucination report is the alleged follow-through: the assistant reportedly connected to the host and modified database tables. If a real connection happened, then at least some credential material was operationally valid or the environment had another route into the system.

In practice, the right response is not to debate hallucination first. Treat unknown credentials as third-party confidential data, preserve evidence, and prevent the agent from taking more actions.

## What Should You Do Immediately If Foreign Credentials Appear?

If Claude Code shows a password, token, host, screenshot, prompt, repo path, or customer detail that is not yours, stop the session. Do not test the credential. Do not SSH to the host. Do not run `psql` to "confirm." Accidentally receiving another user's secret does not authorize access, and testing can turn a disclosure into unauthorized use.

Use a short incident routine:

1. Stop the agent before it calls more tools.
2. Capture the timestamp, Claude Code version, account/workspace, working directory, session ID if visible, and the exact command that preceded the disclosure.
3. Preserve the relevant local transcript file, but redact secret values before sharing outside your incident channel.
4. Rotate any of your own credentials that were present in the same session or project.
5. Report through Anthropic's security or support channel. If you use a public GitHub issue, do not paste live secrets.
6. If the data appears to identify another organization, ask the vendor to notify the affected owner instead of trying to contact or investigate them yourself.

The key is to preserve enough detail for root-cause analysis without spreading the secret further. I use the same rule for AI-agent incidents that I use for production credential leaks: file names, timestamps, token prefixes, and hash digests are usually enough for triage. Full token values almost never belong in a ticket.

## How Do You Audit Local Claude Code Transcripts Safely?

Start with file discovery, not content dumping. The fastest mistake is to grep secrets and paste the matching lines into Slack, which creates a second leak. List candidate files first, then inspect locally with a redaction habit.

```bash
# List local Claude Code files likely to contain common secret patterns.
# This prints file names only. Do not paste raw matching lines into tickets.
grep -RIlE 'ghp_|github_pat_|sk-[A-Za-z0-9]|xox[baprs]-|Authorization: Bearer|AKIA[0-9A-Z]{16}' \
  ~/.claude/projects ~/.claude/history.jsonl ~/.claude/paste-cache ~/.claude/file-history 2>/dev/null
```

Then check file age and size. Large JSONL transcript files are not automatically bad, but they are where tool output, stack traces, and previous task summaries tend to accumulate.

```bash
find ~/.claude/projects -type f -name '*.jsonl' -mtime +7 -print 2>/dev/null
find ~/.claude/projects -type f -name '*.jsonl' -size +10M -print 2>/dev/null
```

For teams, I prefer a weekly local audit that reports counts and paths, not secret values. If the scanner finds a token-like string, the developer rotates the credential and deletes or redacts the local transcript according to policy. This is boring work, but it is much cheaper than discovering six weeks later that an agent transcript became the easiest place to harvest production tokens.

If you want deeper coverage, include:

- `~/.claude/projects/**/*.jsonl`
- `~/.claude/projects/**/subagents/*.jsonl`
- `~/.claude/feedback-bundles/`
- `~/.claude/paste-cache/`
- `~/.claude/file-history/`
- `~/.claude/history.jsonl`
- `~/.claude/debug/`

For broader agent hygiene, the same mental model applies to MCP servers and subagents. I wrote about controlling extension sprawl in [Claude Code Dev Team Stack Skills MCP 2026](/posts/claude-code-dev-team-stack-skills-mcp-2026/) and keeping delegated work isolated in [Claude Code Subagents Parallel Agents Guide 2026](/posts/claude-code-subagents-guide-2026/). Privacy bugs get harder to diagnose when every session loads a different pile of tools, instructions, and side effects.

## How Should You Lock Down Permissions And Tool Access?

Claude Code permissions are not decoration. The official [permissions docs](https://code.claude.com/docs/en/permissions) say deny rules are evaluated before ask rules and allow rules, and that `bypassPermissions` should only be used in isolated environments like containers or VMs. That is the right default for this incident class.

Here is a conservative project-level shape I would start from and then adapt:

```json
{
  "cleanupPeriodDays": 7,
  "defaultMode": "default",
  "permissions": {
    "disableBypassPermissionsMode": "disable",
    "disableAutoMode": "disable",
    "allow": [
      "Read(src/**)",
      "Read(test/**)",
      "Edit(src/**)",
      "Edit(test/**)",
      "Bash(npm test)",
      "Bash(npm run lint)"
    ],
    "ask": [
      "Bash(*)",
      "WebFetch(domain:*)"
    ],
    "deny": [
      "Read(.env)",
      "Read(**/.env)",
      "Read(//**/.env)",
      "Read(~/.ssh/**)",
      "Bash(ssh *)",
      "Bash(psql *)",
      "Bash(mysql *)",
      "Bash(curl *Authorization*)",
      "mcp__*"
    ]
  }
}
```

That config is intentionally restrictive. It blocks `.env` reads, SSH, direct database clients, obvious bearer-token curl commands, and MCP tools by default. It also disables `auto` and `bypassPermissions` modes through settings. For a team, I would move these into managed settings so a local project cannot quietly weaken the policy.

The trade-off is friction. Developers will approve more prompts, and some legitimate debugging workflows will need explicit exceptions. I accept that cost around production credentials. The alternative is letting an agent treat an unknown root password as just another string to try.

If your workflow really needs broad shell access, run it inside a sandbox. Container or VM isolation does not solve cross-session context leakage, but it reduces the damage when a model acts on bad context. The practical question is not "do we trust Claude?" It is "what can this process reach if the next tool call is wrong?"

## What Does ZDR Cover, And What Does It Not Cover?

Zero Data Retention is useful, but it is not a magic privacy blanket. Anthropic's [ZDR docs](https://code.claude.com/docs/en/zero-data-retention) say ZDR for Claude Code on Claude for Enterprise applies to model inference calls: prompts and responses are processed in real time and not stored after the response is returned, except for legal compliance or misuse prevention. It is enabled per organization and is not included automatically in the standard Enterprise plan.

The same docs also list exclusions. ZDR does not cover third-party integrations, MCP servers, external tools, Claude.ai chat, Cowork sessions, user and seat management data, or Claude Code analytics metadata. Features requiring stored prompts or completions, such as Claude Code on the web, cloud sessions from Desktop, artifacts, and `/feedback`, are blocked under ZDR.

That matters for the July 4 report because the user said the session was in an Enterprise ZDR workspace on Claude Code 2.1.199. A ZDR customer can still have local transcripts, tool output, MCP-side storage, workspace metadata, analytics, browser state, shell history, or project configuration that is outside the narrow inference-retention guarantee.

For sensitive teams, I would document the boundary like this:

| Surface | ZDR helps? | Still needs controls? |
| --- | --- | --- |
| Prompt and model response retention on Anthropic direct Claude Code inference | Yes, for eligible enabled orgs | Yes, because policy exceptions can apply |
| Local plaintext transcripts under `~/.claude/projects/` | No | Yes, tune cleanup, scan, delete, and restrict filesystem access |
| MCP servers and third-party tools | No | Yes, require auth, scope tokens, log calls, and allowlist servers |
| Shell commands and database clients | No | Yes, use permissions, sandboxing, and network controls |
| `/feedback` transcript sharing | Blocked under ZDR | Yes, disable outside ZDR if policy requires it |

For MCP specifically, do not ship long-lived static tokens into agent tools if you can avoid it. Use OAuth, short-lived access tokens, scopes, and audience checks. The implementation details are covered in [MCP OAuth 2.1 Authentication: Complete Developer Guide 2026](/posts/mcp-oauth-authentication-guide-2026/), but the privacy principle is simple: a leaked tool token should expire quickly and authorize very little.

## What Should Enterprise Teams Change This Week?

I would not wait for a perfect postmortem before tightening controls. The changes below are useful even if the June 29 allegation later turns out to be local contamination.

### Which Client Settings Should Be Standard?

Set a shorter `cleanupPeriodDays` if your work involves credentials or customer data. The official default described in the data-usage docs is 30 days for local plaintext session transcripts. For normal app code that may be fine. For production debugging, incident response, or regulated data, seven days is a more defensible starting point.

Disable nonessential traffic where your policy requires it:

```bash
export DISABLE_TELEMETRY=1
export DISABLE_ERROR_REPORTING=1
export DISABLE_FEEDBACK_COMMAND=1
export CLAUDE_CODE_DISABLE_FEEDBACK_SURVEY=1
export CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1
```

Those variables are not a substitute for ZDR or managed settings, but they reduce accidental outbound reporting paths. The data-usage docs also say `/feedback` can include conversation history and code, so I prefer disabling it by default in enterprise environments and using a controlled support bundle process instead.

### Which Tool Calls Should Require Human Approval?

Require approval for:

- SSH and remote shell commands
- Database clients such as `psql`, `mysql`, `mongosh`, and `redis-cli`
- Cloud CLIs that can mutate infrastructure
- Commands containing `Authorization`, `Bearer`, `token`, or `password`
- WebFetch to unapproved domains
- MCP tools that read tickets, docs, email, cloud resources, or databases

Allow without prompts only the commands your repo runs all day: test, lint, format, typecheck, and safe read-only introspection. If the agent needs to touch production, the approval path should feel like a deploy approval, not an autocomplete confirmation.

### How Should You Govern MCP Servers?

Use an allowlist, not a marketplace free-for-all. MCP servers can read browser state, query SaaS systems, call databases, and return large chunks of private context into the model. That makes them part of the agent control plane. For every MCP server, record owner, auth method, scopes, data classes, log retention, and emergency revoke procedure.

In practice, I keep MCP tools boring: read-only first, scoped per environment, no production write access unless there is a separate approval gate, and no shared admin tokens. If a server cannot identify the calling user and enforce per-user authorization, it should not be connected to sensitive systems.

## What Should You Avoid Doing?

Do not paste leaked credentials into public issues. Do not test a third-party host. Do not download leaked source code to "verify" a claim. Do not make the agent keep working after it has shown you context that clearly belongs elsewhere.

Also avoid the opposite failure mode: pretending local transcripts are harmless because they live on your laptop. In issue #71654, the reported leak path was mundane: a command printed a GitHub PAT, and an exception serialized an authorization header. That is exactly how real secrets land in logs. The model does not need to be malicious, and the vendor does not need to have a cross-tenant bug, for a local transcript to become sensitive.

My working rule is simple: if I would not put a value in a GitHub issue, I do not want it in an agent transcript. If I must expose it during debugging, I rotate it afterward.

## Is Claude Code Safe To Use After These Reports?

Yes, with the right boundaries. I would still use Claude Code for local development, code review, refactors, tests, and repo exploration. I would not run it with unrestricted shell access against production infrastructure, long-lived secrets, broad MCP tools, and month-long plaintext transcript retention.

The real lesson from the Claude Code cross-user data leak reports is that agent sessions are not just conversations. They are semi-operational workspaces with memory, tools, credentials, local logs, and external integrations. Treat them like a developer workstation plus a junior operator who can type very fast. Useful, but not something you leave unbounded.

## FAQ: Is Claude Code Safe To Use After The 2026 Privacy Reports?

### Was The Claude Code Cross-User Data Leak Confirmed By Anthropic?

Not in the visible public GitHub thread as of July 9, 2026. The June 29 report is a public `area:security` and `bug` issue alleging cross-session credential leakage and unauthorized database modification. Treat it as a serious allegation, not as a fully confirmed public breach report.

### What Is The Biggest Practical Risk For Developers?

The biggest practical risk is credential exposure through session context, tool output, and local transcripts. Even without a vendor-side cross-tenant bug, Claude Code can persist prompts, stdout, exceptions, file contents, and summaries under `~/.claude/projects/`. Those files should be scanned and cleaned like other sensitive logs.

### Should I Disable Claude Code Until Anthropic Publishes A Root Cause?

Most teams do not need a full shutdown. A better response is to remove production access, disable bypass permissions, shorten transcript retention, deny reads of `.env` and SSH material, restrict MCP servers, and require approval for remote shells, database clients, and cloud mutation commands.

### Does Zero Data Retention Prevent This Class Of Incident?

ZDR reduces Anthropic-side retention for eligible Claude Code inference calls, but it does not cover everything around a session. Local transcripts, third-party integrations, MCP servers, analytics metadata, shell history, and external tool storage still need separate controls.

### What Should I Do If Claude Code Shows Someone Else's Secret?

Stop the session, do not test the secret, preserve redacted evidence, rotate any of your own credentials exposed in the same context, and report through the vendor's security channel. If the secret appears to belong to another user, let the vendor handle notification and containment.
