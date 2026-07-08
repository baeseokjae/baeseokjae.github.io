---
title: "Claude Code Dev Team Stack Skills MCP 2026: What Is Worth Installing?"
date: 2026-07-08T12:00:00+00:00
tags: ["Claude Code", "MCP", "AI Coding", "Developer Tools"]
description: "A practical Claude Code stack for dev teams: skills, MCP servers, hooks, subagents, plugins, and security rules worth installing."
draft: false
cover:
  image: "/images/claude-code-dev-team-stack-skills-mcp-2026.png"
  alt: "Claude Code Dev Team Stack Skills MCP 2026"
  relative: false
schema: "schema-claude-code-dev-team-stack-skills-mcp-2026"
---

The best Claude Code dev team stack in 2026 is small: project CLAUDE.md rules, 6-8 focused skills, 4-5 read-first MCP servers, deterministic hooks, and subagents for noisy investigation. I've found that teams get more value from governing those layers than from installing every popular skill.

That matters because Claude Code has stopped being "just a terminal chatbot." The current extension surface includes skills, hooks, subagents, agent teams, code intelligence plugins, MCP servers, and packageable plugins. The temptation is to install a marketplace worth of tools on day one. In practice, that usually makes the system slower, harder to trust, and harder to debug.

My rule is simple: install a tool only when it removes repeated manual context transfer or encodes a team workflow you already trust. If a developer still has to paste Jira tickets, Sentry stack traces, database schemas, or release checklists into Claude every day, that is a stack gap. If the tool only makes a demo look impressive, leave it out.

## What Is The Lean Claude Code Stack Worth Installing First?

For a real engineering team, I would start with this stack before looking at community collections:

| Layer | Install first | Why it belongs in the default stack |
|---|---|---|
| Project memory | `CLAUDE.md`, plus scoped rules when needed | Holds build commands, package manager choices, test conventions, and "never do this" project facts. |
| Bundled skills | `/code-review`, `/debug`, `/batch`, `/loop`, `/run`, `/verify` | These are already maintained by Claude Code and cover common development loops. |
| Project skills | review, test, release, migration, incident, UI QA | Captures your team's actual way of working without loading long docs into every request. |
| MCP servers | GitHub, Sentry, docs/search, read-only Postgres, code index | Replaces copy-paste from tools the agent needs to inspect. |
| Hooks | format after edit, block protected files, audit config changes | Enforces rules without relying on the model to remember them. |
| Subagents | research, security review, performance review, UI verification | Keeps noisy investigation out of the main context. |
| Plugins | only after the setup repeats across repos | Packages skills, hooks, subagents, and MCP config once the pattern is proven. |

The shape is deliberately boring. Claude Code's official docs already say skills load on demand, unlike CLAUDE.md content that enters the context at startup. That one detail drives most of the stack design. Always-on facts belong in CLAUDE.md. Long procedures belong in skills. External system access belongs in MCP. Non-negotiable enforcement belongs in hooks.

If you are still comparing the broader skills ecosystem, my baseline is close to the argument in [Agent Skills Marketplace Guide 2026](/posts/agent-skills-marketplace-guide-2026-claude-codex-cursor-and-gemini-cli/): agent skills are useful, but only after you decide what work they should standardize.

## How Should You Choose Between Skills, MCP, Hooks, Subagents, Plugins, And CLAUDE.md?

The fastest way to make a messy Claude Code setup is to use the wrong extension layer. I use this decision table when reviewing team setups:

| Need | Use | Example |
|---|---|---|
| Claude should always know a convention | `CLAUDE.md` | "Use pnpm, not npm. Run `pnpm test` before committing." |
| Claude sometimes needs a long playbook | Skill | `/release` loads the release checklist and rollback steps. |
| Claude needs data from another system | MCP | Read a GitHub issue, Sentry event, or database schema directly. |
| A rule must fire every time | Hook | Block edits to `.env` or run Prettier after every `Edit` or `Write`. |
| A side task would flood context | Subagent | Research 40 files and return only the relevant findings. |
| Several repos need the same setup | Plugin | Bundle your review skill, hooks, and MCP server config for all services. |

Skills and MCP are the pair people confuse most. A skill teaches Claude how your team works. An MCP server gives Claude access to a tool or data source. For example, a Postgres MCP server can expose schemas and query tools; a database skill should explain which tables matter, which queries are safe, and what "read-only" means for your team.

Hooks are different again. A hook is not advice. It is an event-driven command, HTTP request, prompt, or subagent that runs at a specific point in the Claude Code lifecycle. If you write "never edit `.env`" in CLAUDE.md, you have a request. If you add a `PreToolUse` hook that blocks `Edit|Write` on `.env`, you have enforcement.

## What Do The 2026 Claude Code Docs Change For Team Setups?

Three current docs details change how I would set up a team in 2026.

First, bundled skills are now a serious default. Claude Code includes `/code-review`, `/batch`, `/debug`, `/loop`, and `/claude-api`, and the current app-running flow includes `/run`, `/verify`, and `/run-skill-generator` for Claude Code v2.1.145 or later. I would not replace those casually. Start with the bundled behavior, then override only when the review or verification process is genuinely wrong for your repo.

Second, MCP installation is mature enough for team use, but still needs explicit scoping. The official CLI supports remote HTTP servers:

```bash
claude mcp add --transport http sentry https://mcp.sentry.dev/mcp

claude mcp add --transport http github https://api.githubcopilot.com/mcp/ \
  --header "Authorization: Bearer YOUR_GITHUB_PAT"
```

It also supports local stdio servers, which is where I am stricter:

```bash
claude mcp add --transport stdio db -- npx -y @bytebase/dbhub \
  --dsn "postgresql://readonly:pass@prod.db.com:5432/analytics"
```

That `readonly` user is not a cosmetic detail. If the agent only needs schema inspection and analytical queries, do not hand it a write-capable credential.

Third, tool search changes the context-cost argument. Current Claude Code docs describe MCP tool definitions as deferred by default, so adding an MCP server is not the same as dumping every tool schema into the prompt at startup. That makes MCP safer from a context budget perspective, but not from a permission perspective. A deferred dangerous tool is still dangerous when discovered.

## Which Core Skills Should Every Dev Team Start With?

I would start with six project skills, then add more only when the team repeats the same prompt several times.

### Which Review Skill Should You Keep?

Use the bundled `/code-review` first. Then add a project-specific `review` skill only if your team has review rules that Claude repeatedly misses: domain invariants, database migration rules, API compatibility checks, or product-specific edge cases.

For example:

```markdown
---
name: review-service-change
description: Review service changes for API compatibility, migration safety, and test gaps
allowed-tools: Read Grep
---

Review $ARGUMENTS with this checklist:
1. Public API compatibility: request shape, response shape, error codes.
2. Database safety: migrations are reversible or explicitly documented.
3. Tests: changed behavior has unit or integration coverage.
4. Operational risk: logs, metrics, feature flags, and rollback path.
Return only blocking issues first, then non-blocking notes.
```

That is specific enough to route well. It does not try to be a universal senior engineer in 900 lines.

### Which Debug And Verification Skills Should You Keep?

Use `/debug`, `/run`, and `/verify` before inventing your own workflow. In practice, `/verify` is more useful than telling Claude "run tests" because it asks Claude to prove the running app behavior, not just run a typecheck and call it done.

Where teams should invest is `/run-skill-generator`. Run it once for projects with non-obvious startup requirements: Docker Compose, seeded databases, localstack, feature flags, or a frontend that needs a specific environment file. The generated project skill saves every future session from rediscovering the same launch sequence.

### Which Docs Skill Is Worth Creating?

Create a docs skill when your team has source-of-truth documentation that is not obvious from the code. That might be an internal API design guide, a migration playbook, a billing rules document, or a frontend component policy.

Do not put a 40-page handbook into CLAUDE.md. Keep CLAUDE.md short and point to the skill. The skill should have a sharp description and, when possible, supporting reference files. Skills load when relevant; always-on memory should stay lean.

### Which Security Skill Should Be Project-Level?

Every team using MCP should have a security review skill that covers prompt injection, credentials, outbound network calls, and tool permissions. This is especially important for observability and issue-tracker MCP servers, because those systems contain user-controlled text.

I would pair that skill with the operational guidance in [Agentjacking Mitigation Guide 2026](/posts/agentjacking-mitigation-guide-2026/) and [Sentry MCP Safe Monitoring Setup 2026](/posts/sentry-mcp-safe-monitoring-setup-2026/) if your team lets agents read monitoring events.

## Which MCP Servers Are Actually Worth Adding First?

MCP is worth installing when it stops a developer from copying external context into chat. That is the filter.

### Which Code And Issue MCP Should Be First?

GitHub or your code host should be near the top. Claude can read issues, inspect pull requests, and create follow-up work without you manually pasting the ticket body. I still start with narrow repository access and fine-grained tokens. A personal access token with access to every repo in the company is a bad default.

For large codebases, a code index MCP or code intelligence plugin is often more valuable than another general-purpose skill. If the agent spends 15 tool calls finding a symbol and its callers, you are paying context and latency tax before any useful work starts. I covered that trade-off in [AI Coding Agent Code Index MCP Comparison 2026](/posts/ai-coding-agent-code-index-mcp-comparison-2026/), and the short version still holds: code navigation tools reduce search churn when the repo is big enough.

### Which Observability MCP Belongs In The Stack?

Sentry is the first observability MCP I would add for most web teams because error events, stack traces, release data, and suspected regressions are exactly the kind of context developers otherwise paste into Claude. The official Claude Code MCP docs use Sentry as a practical example with:

```bash
claude mcp add --transport http sentry https://mcp.sentry.dev/mcp
```

The trade-off is prompt injection risk. Error messages, request paths, breadcrumbs, tags, and issue comments can contain attacker-controlled text. Keep the server read-first, restrict project scope, and teach your review skill to treat external tool output as untrusted data.

### Which Database MCP Is Safe Enough?

A database MCP is useful only with a read-only role, a non-production replica where possible, and a narrow schema. I have watched agents generate impressive SQL and then overreach because the question was under-specified. The safest team pattern is:

```text
analytics_readonly role
allowed schemas: public_reporting, billing_analytics
blocked schemas: auth, secrets, payment_tokens
query timeout: 30s
result limit: 100 rows by default
```

Then add a skill that explains the business meaning of those tables. MCP gives access. The skill gives judgment.

### Which Browser Or Web MCP Should Be Optional?

Browser rendering and web crawling tools are useful for UI verification, screenshots, docs lookup, and competitive research. They are also easy to overuse. I prefer a browser MCP at user scope for developers who need it regularly, then project scope only when the workflow is part of CI, QA, docs work, or frontend review.

## Which Tools Should Stay Optional Rather Than Default?

Do not install everything globally. The stack gets worse when every session exposes tools Claude rarely needs.

| Tool category | Default? | Why |
|---|---:|---|
| Figma or design MCP | Situational | Great for frontend teams, noise for backend-only services. |
| Deployment MCP | Usually no | Write operations need strict approval, audit, and rollback ownership. |
| Database write tools | No | Use read-only by default; writes belong behind human-approved workflows. |
| Broad web crawler | Situational | Useful for research, risky for prompt injection and noisy content. |
| "Everything" skill packs | No | Overlapping descriptions hurt routing and trust. |
| Personal productivity skills | User scope | Keep experiments out of shared repo config until proven. |

I've found that eight good skills beat 30 vague ones. Vague skills compete with each other, trigger at the wrong time, and leave developers wondering which hidden instruction influenced the answer. A skill should have one job, a concrete description, and a reason to exist.

## How Do Hooks And Subagents Make The Stack Safer?

Hooks and subagents are the parts many teams underuse.

Hooks should handle deterministic controls. Claude Code's current hook examples include `PostToolUse` formatting after edits and `PreToolUse` blocking edits to protected files. A team-level project hook for JavaScript formatting might look like this:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "jq -r '.tool_input.file_path' | xargs npx prettier --write"
          }
        ]
      }
    ]
  }
}
```

For protected files, use a `PreToolUse` hook instead of hoping CLAUDE.md is obeyed. The docs recommend a script that exits with code 2 to block edits. In a team setting, I would block `.env`, private key material, lockfiles unless explicitly allowed, and generated files that should only be changed by build tools.

Subagents solve a different problem: context hygiene. When Claude needs to investigate a large failure, let a research or debugging subagent read logs, search files, and inspect hypotheses, then return a compact summary. Your main conversation should not contain 80 intermediate grep results unless you need to audit them.

Security review is also a good subagent use case. A focused security subagent can inspect changed code for auth bypasses, injection risks, unsafe MCP output handling, and secret exposure, then report findings back to the lead session.

## How Should A Team Install This Across Personal, Project, And Plugin Scopes?

Use three scopes.

Personal scope is for experimentation. A developer can try a new browser skill, design skill, or research tool without changing how the whole team works.

Project scope is for behavior the repo depends on. Put stable project skills under `.claude/skills`, project MCP config in `.mcp.json` when the server is safe to share, and project hooks in `.claude/settings.json` when the enforcement belongs with the codebase.

Plugin scope is for reuse across repos. Do not create a plugin on day one. Wait until you have the same skill, hook, subagent, and MCP setup copied into a second or third repo. At that point, a plugin becomes useful because it packages the setup and gives you one update path.

This is also where governance starts. Assign owners. Review changes to shared skills the same way you review build scripts. Require approval for new MCP servers. Keep tokens in environment variables or OAuth flows, not committed config. Delete tools that nobody has used in a month.

## What Security Checklist Should You Run Before Installing Anything?

Before adding a skill, MCP server, hook, or plugin, I would ask these questions:

| Check | Good answer |
|---|---|
| Who owns it? | A named team or maintainer, not "everyone." |
| What can it read? | Only the repositories, projects, schemas, or docs it needs. |
| What can it write? | Nothing by default; writes require explicit approval. |
| Where are secrets stored? | Environment variables, OAuth, or keychain storage. Not markdown. |
| Does it run scripts? | Scripts are short, reviewed, and deterministic. |
| Can external content influence the agent? | Yes, so tool output is treated as untrusted. |
| How do we remove it? | Documented uninstall or rollback path. |
| How often is it reviewed? | At least monthly for shared agent tooling. |

MCP adoption is large enough now that this cannot be treated as a toy config. Anthropic reported in December 2025 that MCP had more than 10,000 active public servers and 97 million monthly SDK downloads across Python and TypeScript. That scale is good for ecosystem health, but it also means teams need inventory and permission discipline.

## What Stack Should Different Teams Use In 2026?

For a two-person startup, I would use CLAUDE.md, bundled skills, Sentry MCP, GitHub MCP, one docs/search tool, and two hooks: format after edit and block secrets. Keep everything else personal until the workflow stabilizes.

For a product engineering team, I would add project skills for review, release, incidents, and database querying. I would add read-only Postgres or analytics MCP, a code index tool for larger repos, and a security review subagent. Shared config should be reviewed like application code.

For an enterprise team, I would add managed policy, SSO or gateway controls, audit logging, plugin packaging, and a quarterly cleanup process. Enterprise teams should care less about finding one more clever skill and more about knowing which agent can access which system on which developer's machine.

The final ranking:

| Rank | Install decision | Tools |
|---|---|---|
| Must install | Default for most teams | CLAUDE.md, bundled skills, project review/test skills, GitHub MCP, Sentry MCP, formatting and protection hooks |
| Strongly consider | Add when the workflow is frequent | code index MCP, read-only database MCP, docs/search MCP, security subagent, `/run-skill-generator` output |
| Situational | Add by team type | browser rendering MCP, Figma MCP, release automation skill, incident workflow skill |
| Skip by default | Keep out of shared config | broad write-capable MCP tools, unreviewed community skill packs, global database credentials, deployment tools without audit |

The stack that works is not the largest one. It is the one where developers can explain why every extension exists, what it can access, and how to disable it when it misbehaves.

## What Questions Come Up Most Often?

### What is the difference between Claude Code skills and MCP?

Skills are instructions, knowledge, and workflows that Claude can load when relevant or when you invoke them directly. MCP servers connect Claude Code to external tools, APIs, databases, and systems. Use skills to teach Claude how your team works. Use MCP when Claude needs real data or tool access outside the repository.

### How many Claude Code skills should a dev team install?

Start with the bundled skills and 6-8 project skills. That usually covers review, debugging, verification, release, incidents, docs, security, and one domain-specific workflow. Add more only when developers repeat the same prompt or checklist often enough to justify maintaining it.

### Should MCP servers be installed globally or per project?

Install experimental MCP servers at user scope. Install shared, repo-specific MCP servers at project scope only after reviewing permissions and credentials. For cross-repo standards, package the setup as a plugin after it proves useful in more than one repository.

### Are Claude Code MCP servers safe for production systems?

They can be, but the safe default is read-only access, narrow scopes, short timeouts, explicit approvals for writes, and regular audits. Treat MCP output from issue trackers, monitoring systems, browsers, and docs sites as untrusted because it can contain prompt injection content.

### When should a team create a Claude Code plugin?

Create a plugin when the same skills, hooks, subagents, and MCP configuration are needed across multiple repositories. Do not start with a plugin. Let the workflow prove itself in one repo, refine it, then package it when duplication becomes the maintenance problem.
