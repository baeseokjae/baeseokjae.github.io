---
cover:
  alt: How to Set Up Windsurf IDE 2026
  image: /images/windsurf-setup-tutorial-2026.png
  relative: false
date: 2026-04-18 05:16:15+00:00
description: Complete guide to setup Windsurf IDE 2026 — install on macOS, Windows,
  or Linux, configure .windsurfrules, and run your first Cascade flow.
draft: false
schema: schema-windsurf-setup-tutorial-2026
tags:
- windsurf
- ide
- ai-coding
- tutorial
- cascade
title: 'How to Set Up Windsurf IDE 2026: Installation, Config, and First Project'
---

Windsurf IDE is a production-ready AI-native code editor that reached 1M+ active users by March 2026. Unlike VS Code with an AI plugin bolted on, Windsurf was designed from scratch around Cascade — an autonomous agent that plans multi-step tasks, runs terminal commands, and iterates on its own. Setting it up correctly takes about 20 minutes and the defaults are conservative on purpose. Here's exactly how to do it.

## What Makes Windsurf Different From Other AI Editors?

Windsurf is an AI-native IDE built around Cascade, an autonomous agent that can plan multi-step workflows, execute terminal commands, read files across your entire repo, and iterate without waiting for step-by-step instructions. By March 2026, Windsurf had 1M+ active users generating 70M+ lines of AI-written code per day, with 94% of its code output being AI-generated. Unlike GitHub Copilot (which autocompletes inline) or Cursor (which focuses on precision edit suggestions), Windsurf's core value proposition is agentic autonomy: describe an outcome, and Cascade plans and executes the path to get there. ServiceNow deployed Windsurf across ~7,000 engineers and saw a 10% productivity boost. The fundamental distinction is philosophy — Windsurf optimizes for "describe what you want" workflows, while Cursor optimizes for "precise, surgical edits." If your team produces greenfield features or prototypes frequently, Windsurf's architecture pays off. If you do mostly targeted refactors on large mature codebases, the tradeoff is different.

## System Requirements Before You Install

Before downloading, confirm your machine meets the minimum specs. Windsurf runs on any modern hardware but performs noticeably better with adequate RAM. The tool's idle memory footprint is ~1.1GB and cold start time is approximately 3.4 seconds on a modern machine — the AI completion latency runs 102ms, fast enough that it doesn't interrupt flow. On 8GB RAM machines running Codebase context mode on large repos, expect slowdown during the initial embedding scan because Windsurf indexes your entire repository before enabling full multi-file awareness.

**Minimum requirements:**
- macOS: OS X Yosemite (10.10) or later
- Windows: Windows 10 64-bit or later
- Linux: Ubuntu 18.04+ or equivalent glibc 2.17+ distribution
- RAM: 8GB minimum
- RAM: 16GB recommended if you plan to use Codebase context mode on projects over 10k lines

If you're on 8GB RAM and plan to run Codebase context mode on large repos, expect some slowdown during the initial embedding scan. You can work around this with a `.codeiumignore` file to exclude `node_modules`, `dist`, `.git`, and other large generated directories from the index.

## Step 1: Download and Install Windsurf

Download Windsurf from the official site (windsurf.com) for your platform. All three major platforms are supported with native packages. Installation is straightforward but there are a few platform-specific gotchas worth knowing before you start, particularly on macOS where Gatekeeper may block the first launch and on Linux where the apt repository setup requires a few extra commands.

**macOS:**
```bash
brew install --cask windsurf
```
Or download the `.dmg` directly. If macOS Gatekeeper blocks the app on first launch, go to **System Settings → Privacy & Security** and click "Open Anyway." This is expected for apps downloaded outside the App Store.

**Ubuntu / Debian Linux:**
```bash
# Add the Codeium apt repository
curl -fsSL https://windsurf-stable.codeiumdata.com/wVxQEIWkwPUEAGf3/windsurf.gpg \
  | sudo gpg --dearmor -o /usr/share/keyrings/windsurf-stable-archive-keyring.gpg

echo "deb [signed-by=/usr/share/keyrings/windsurf-stable-archive-keyring.gpg arch=amd64] \
  https://windsurf-stable.codeiumdata.com/wVxQEIWkwPUEAGf3/apt stable main" \
  | sudo tee /etc/apt/sources.list.d/windsurf.list > /dev/null

sudo apt-get update && sudo apt-get install windsurf
```

**Windows:**
Download the `.exe` installer from windsurf.com and run it. Windsurf installs to `%LOCALAPPDATA%\Programs\Windsurf` by default.

## Step 2: Complete the Onboarding Flow

When Windsurf launches for the first time, it walks you through a 4-step onboarding that sets up your core preferences. This is worth doing carefully — the choices here save you configuration time later. The onboarding sequence takes about 3-5 minutes, and you can import your existing VS Code or Cursor setup at this stage rather than rebuilding your configuration from scratch. Windsurf copies your extensions list, keybindings, and settings.json automatically during the import, which means most developers are functional within minutes rather than spending an hour reconfiguring their environment.

**Onboarding steps:**
1. **Setup path** — Choose one: "Start fresh," "Import from VS Code," or "Import from Cursor." If you're migrating, pick the import option.
2. **Theme selection** — Dark, light, or high-contrast. This can be changed anytime.
3. **Keybindings** — Choose VS Code keybindings (default) or Vim bindings. Vim users: select this now.
4. **Account creation / login** — Sign up for a free account at codeium.com or log in. The free tier gives you 25 Cascade flow actions per month.

If you skipped the VS Code import during onboarding, trigger it afterward via the Command Palette (`Cmd+Shift+P` / `Ctrl+Shift+P`): search "Import VS Code Settings." Note that other AI completion extensions (GitHub Copilot, Tabnine) and proprietary language server extensions are incompatible with Windsurf and will be flagged during import.

## Step 3: Create Your .windsurfrules File

The `.windsurfrules` file is the single highest-leverage configuration in Windsurf. It lives at your project root and tells Cascade your stack, coding conventions, file structure boundaries, and constraints — before every single prompt. Teams that skip this file spend 2-3x more tokens repeating context. Teams that write a good `.windsurfrules` file cut their prompt length in half and see dramatically more consistent output from Cascade. Think of it as a permanent system prompt that applies to every Cascade interaction in your project. Unlike one-off instructions in a chat window, `.windsurfrules` is committed to git, visible to your whole team, and applied automatically without requiring anyone to remember to include it.

Create it at your project root:
```bash
touch .windsurfrules
```

A practical starter template for a Node.js/TypeScript project:
```
# Stack
- Node.js 22, TypeScript 5.4, Express 4.x
- PostgreSQL via pg (raw SQL, no ORM)
- Jest for tests, ESLint + Prettier for formatting

# Conventions
- Use async/await, never .then() chains
- All database calls go in /src/db/*.ts files
- Error handling: throw typed errors, catch at route level
- Never commit console.log statements

# File structure
- /src/routes — Express route handlers
- /src/db — database queries
- /src/services — business logic
- /src/types — shared TypeScript types

# Boundaries
- Do NOT modify any file in /migrations directly — write a new migration file instead
- Do NOT change package.json or package-lock.json
```

The more specific your rules, the better Cascade's output. Include your exact library versions, the things your team has decided never to do, and where each concern lives in the repo.

## Step 4: Configure Cascade Context Mode

Cascade has three context modes that control how much of your codebase it reads before generating. Choosing the wrong one is the most common reason Windsurf feels slow or produces inaccurate suggestions. The default is File mode — Cascade reads only your currently open file — which is deliberately conservative. For most real development work where features span multiple files, you'll want to switch to Codebase mode. The mode you choose has a direct impact on both response quality and machine performance, so understanding the tradeoffs before you start using Cascade seriously is worth 5 minutes of your time.

| Mode | What It Reads | Best For |
|------|--------------|----------|
| **File** | Only the currently open file | Quick edits on isolated files |
| **Codebase** | Embeds entire repo (< 50k lines) | Multi-file features, refactors |
| **Explicit @file** | Only files you reference with @ | Targeted work on large repos |

**To set context mode:** Open Cascade panel (`Cmd+L` / `Ctrl+L`), click the context dropdown at the top.

For projects under 50k lines, switch to Codebase mode. The first time you do this, Windsurf scans and indexes your repo — 30-120 seconds depending on size. After that, index updates are incremental.

On repos over 50k lines or on 8GB RAM machines, use explicit `@file` references instead: `@src/auth/middleware.ts update this to support OAuth2 PKCE flow`.

## Step 5: Run Your First Cascade Flow

A Cascade Flow is a multi-step agentic task. You describe the outcome; Cascade reads the relevant files, writes a plan, executes it across multiple files, runs tests, fixes failures, and reports back. Open the Cascade panel with `Cmd+Shift+L` (macOS) or `Ctrl+Shift+L` (Windows/Linux). The key shift in mindset from Copilot or Cursor is that you stop describing steps and start describing end states. In benchmarks from devtoolsreview.com, Cascade completed a Redis rate-limiting implementation in 3.5 minutes versus 45-60 minutes manually — reading files, writing middleware, adding env vars, applying routes, writing tests, and fixing test failures autonomously. Cascade works correctly on clearly scoped tasks about 75-80% of the time.

**Outcome-first prompt example:**
```
Add rate limiting middleware to all /api routes. Use Redis via ioredis.
Limit to 100 requests per minute per IP. Return 429 with Retry-After header.
Add integration tests in /tests/rate-limiting.test.ts.
```

**What to avoid:** Don't write step-by-step instructions like "First read middleware.ts, then add a new file..." — Cascade plans steps internally. Describe the end state, not the path.

When Cascade enters a loop (you'll see it running the same commands repeatedly), interrupt with `Cmd+K` / `Ctrl+K` and break the task into smaller pieces.

## Step 6: Set Up Memories and Rules for Persistent AI Behavior

Windsurf has two persistence mechanisms beyond `.windsurfrules` that let you encode preferences once and have Cascade apply them automatically forever after. Memories are personal facts Cascade stores about your working style, stored in your Windsurf account and applying across all your projects. Global Rules are project-agnostic preferences that sit above your `.windsurfrules` in the priority chain. Together with `.windsurfrules`, these three layers let you encode your entire development philosophy once and stop repeating yourself every session. Understanding the priority order prevents confusion when Cascade seems to ignore something you've told it: Global Rules override everything, then `.windsurfrules`, then Memories, then your current prompt.

**Memories** — Open Cascade → click the brain icon → "Manage Memories." Tell Cascade to remember something inline: `@Cascade remember: we never use moment.js, always date-fns`.

**Global Rules** — Go to **Settings → Windsurf → Cascade → Rules** and add rules like "Always use TypeScript strict mode" or "Prefer functional components in React."

The priority order is: Global Rules → .windsurfrules → Memories → your prompt.

## Step 7: Set Up Workspace Snippets and prompts.md

For prompts you type repeatedly, Windsurf supports a `prompts.md` shortcut system that saves keystrokes and ensures consistent prompting across your team. Create a `prompts.md` file at your repo root — each H2 heading becomes a named snippet accessible by typing `/` in the Cascade panel. This is one of the most underused features in Windsurf: teams that skip it end up with each developer writing their own variation of the same test-generation or code-review prompt, producing inconsistent Cascade outputs. A `prompts.md` committed to git means every developer uses the same tested, refined prompt templates for common tasks like writing tests, reviewing diffs, or generating documentation. It eliminates prompt quality variance that makes AI output inconsistent across team members, and it compounds over time as your team refines and improves the templates together.

Example `prompts.md`:
```markdown
## write-test
Write a Jest integration test for the function I have selected.
Use supertest for HTTP tests. Mock external APIs with nock.

## review-pr
Review this diff for: security issues, missing error handling,
N+1 queries, and consistency with our coding conventions.

## explain
Explain what this code does, including non-obvious side effects.
Assume the reader knows the language but not this codebase.
```

Type `/write-test` in the Cascade panel to insert the full prompt template.

## Step 8: Connect MCP Servers to Extend Cascade

Model Context Protocol (MCP) servers let Cascade access external tools — databases, APIs, GitHub, Slack, file systems. This is one of Windsurf's most powerful but least-configured features among new users. Once connected, an MCP server gives Cascade live context it can't get from reading source code alone. A database MCP server, for example, lets Cascade query your actual schema before writing a migration — eliminating the column-name hallucinations that make AI-generated SQL unreliable. Teams that add a database MCP server on day one report Cascade generating syntactically correct SQL on first attempt over 80% of the time, compared to frequent schema mistakes without it.

**To add an MCP server:** Go to **Settings → Windsurf → Cascade → MCP Servers** → click "Add Server."

Example: connecting to a local PostgreSQL database:
```json
{
  "name": "postgres",
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-postgres", "postgresql://localhost:5432/mydb"]
}
```

Common MCP servers to add early:
- `@modelcontextprotocol/server-github` — PR creation, issue lookup
- `@modelcontextprotocol/server-filesystem` — read/write access outside the current project
- `@modelcontextprotocol/server-postgres` or `server-sqlite` — database access

## Step 9: Creating Your First Full Project With Cascade

Here's a concrete walkthrough: scaffolding a new Express API from scratch using Windsurf's built-in project generation. This covers the complete first-use experience from blank canvas to a working API with authentication and tests — the kind of greenfield task where Windsurf genuinely outperforms every other AI coding tool available in 2026. The goal isn't just to see Cascade write code; it's to build the habit of outcome-first prompting and understand where to intervene when Cascade needs guidance.

1. Open Windsurf → click "Generate a project" from the welcome screen (or Command Palette: "Windsurf: New AI Project")
2. Describe the project: `Express REST API with TypeScript, PostgreSQL, JWT auth, and Jest tests. Users can create accounts, login, and manage todos.`
3. Windsurf generates the initial scaffold, installs dependencies, and opens the project
4. Immediately create your `.windsurfrules` file with the stack details
5. Switch Cascade to Codebase context mode
6. Add your first feature: `Add the todo CRUD endpoints. Include validation with zod. All routes should require JWT authentication. Write tests.`

Cascade will read the existing auth middleware, understand the schema, write route handlers, add zod validation, update the router index, and write tests. Review the diff before accepting — check migration files and security-critical paths carefully.

## Windsurf Pricing: What You Get at Each Tier

| Plan | Price | Cascade Flow Actions | Best For |
|------|-------|---------------------|----------|
| **Free** | $0/month | 25/month | Evaluation, hobby projects |
| **Pro** | $15/month | Unlimited | Individual developers |
| **Teams** | $30/user/month | Unlimited + collab | Small-to-mid teams |
| **Enterprise** | Custom | Unlimited + private models | SOC2/FedRAMP/HIPAA needs |

For context: Cursor Pro is $20/month. Windsurf Pro at $15/month is the more affordable option for developers who lean heavily on agentic flows. The free tier's 25 flow actions/month is enough to evaluate the tool but a typical workday of serious development burns 15-30 actions, making the free tier insufficient for daily use. Windsurf reported $82M ARR with 350+ enterprise customers as of July 2025, with 4,000+ enterprises in production and 59% of Fortune 500 companies building with it. Enterprise features include SSO, RBAC, audit logs, SOC 2 Type II compliance, FedRAMP High authorization, HIPAA compliance, and hybrid/on-premise deployment.

## Troubleshooting Common Setup Issues

**macOS Gatekeeper blocks Windsurf on launch:**
Go to System Settings → Privacy & Security → scroll down → "Open Anyway." One-time step for apps downloaded outside the App Store.

**Cascade enters an execution loop:**
Press `Cmd+K` / `Ctrl+K` to interrupt. The most common cause is an ambiguous task scope or a missing dependency. Break the task into smaller pieces and be explicit about constraints.

**Codebase context mode is slow or crashes:**
Add a `.codeiumignore` file (same syntax as `.gitignore`) to exclude `node_modules`, `dist`, `.git`, large binary assets, and generated files. Also exclude directories over 5MB.

**Extensions conflict with Windsurf:**
Disable other AI completion extensions (Copilot, Tabnine, Codeium standalone). They compete for the same completion hooks and cause latency spikes or silent failures.

**VS Code settings didn't import correctly:**
Open Command Palette → "Open User Settings (JSON)" and verify `~/.config/windsurf/User/settings.json`. Most VS Code settings keys work unchanged in Windsurf.

## Windsurf vs Cursor Setup: Different Philosophies

Windsurf and Cursor are both serious AI coding tools, but their setup process reveals fundamentally different workflow philosophies — and choosing the wrong one for your team's working style is a common source of frustration. Windsurf optimizes for autonomous, outcome-driven work: configure it once with `.windsurfrules` and context mode, then describe what you want to build. Cursor optimizes for precision: inline suggestions and targeted edits where you maintain tight control over each change. In benchmark tests, Windsurf's Cascade completed a Redis rate-limiting task in 3.5 minutes with zero step-by-step guidance; Cursor would have required more manual steering for the same task. Understanding which philosophy fits your team saves weeks of adapting to the wrong tool.

| Aspect | Windsurf | Cursor |
|--------|----------|--------|
| **Core model** | Autonomous agent (Cascade) | Precision edit assistant |
| **Setup config** | .windsurfrules + context mode | .cursorrules + context files |
| **Autocomplete** | Conservative, high accuracy | Aggressive, 68-72% immediate usability |
| **Best for** | Greenfield features, prototyping | Targeted refactors, surgical edits |
| **Price** | $15/month Pro | $20/month Pro |
| **Weakness** | Loops on multi-constraint tasks | Codebase-wide agentic tasks |

Windsurf is better when you frequently build new features and prefer describing outcomes. Cursor is better when you work on mature, large codebases and want precise, predictable suggestions. Many teams use both.

## Enterprise Teams: SSO, FedRAMP, and RBAC Setup

For teams on the Enterprise plan, setup involves three additional steps beyond the standard installation that enable the compliance and access control features that make Windsurf viable in regulated industries. Windsurf achieved FedRAMP High authorization and HIPAA compliance in 2025, making it one of the few AI coding tools cleared for federal and healthcare environments. The enterprise setup process follows a standard identity provider integration pattern, so if your team already uses Okta, Azure AD, or Google Workspace, SSO configuration takes under 30 minutes. RBAC setup follows after SSO and controls which developers can use which Cascade features.

**SSO configuration:** Admin panel → Settings → Authentication → "Enable SSO." Supports SAML 2.0 and OIDC. Paste your IdP metadata URL (Okta, Azure AD, Google Workspace all work). Test before rollout.

**RBAC setup:** Admin panel → Policies → define roles. Typical setup: developers get full Cascade access, contractors get File context mode only, read-only reviewers can see AI suggestions but not trigger flows.

**FedRAMP / HIPAA:** For government or healthcare deployments, contact enterprise sales for hybrid deployment — Cascade inference runs on-premise with your data never leaving your infrastructure.

**Audit logs:** Admin panel → Audit Log. Captures every Cascade flow, every file written, every terminal command, and every external API call. Required for SOC 2 Type II reviews.

## FAQ

**Can I use Windsurf without a paid subscription?**
Yes. The free tier gives you 25 Cascade flow actions per month, unlimited autocomplete suggestions, and access to base models. For occasional or evaluation use, the free tier works. For daily development, most developers find they need Pro ($15/month) within the first week since a typical workday burns 15-30 flow actions.

**How do I import my VS Code extensions into Windsurf?**
During onboarding, select "Import from VS Code." Afterward, use the Command Palette and search "Install Extensions from VS Code." Extensions requiring VS Code's proprietary APIs or competing AI completion extensions (Copilot, Tabnine) won't work and will be flagged automatically.

**What's the difference between Cascade flows and regular chat?**
Regular chat (`Cmd+L`) gives you a conversational interface for questions and suggestions you apply manually. Cascade flows (`Cmd+Shift+L`) give Cascade permission to read files, write code, run terminal commands, and execute multi-step plans autonomously. Flows consume from your monthly action quota; chat does not.

**How does .windsurfrules differ from Memories?**
`.windsurfrules` is project-specific, checked into git, and applies to everyone on the team. Memories are personal, stored in your Windsurf account, and apply across all your projects. Use `.windsurfrules` for team conventions and stack definitions. Use Memories for personal preferences like "always add JSDoc to public functions."

**Is Windsurf safe for codebases with proprietary or sensitive code?**
Windsurf offers enterprise options with SOC 2 Type II, FedRAMP High, and HIPAA compliance, plus hybrid/on-premise deployment where Cascade inference runs within your infrastructure. For standard cloud plans, code is sent to Codeium's servers for AI inference. Review Windsurf's data processing agreement before using it on codebases with contractual data residency requirements.