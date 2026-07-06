---
cover:
  alt: 'OpenAI Codex CLI Guide 2026: Terminal AI Coding with the Rust-Built Agent'
  image: /images/openai-codex-cli-guide-2026.png
  relative: false
date: 2026-04-24 18:04:05+00:00
description: 'Complete guide to OpenAI Codex CLI 2026: install the Rust-built terminal
  agent, configure AGENTS.md, set approval modes, and integrate MCP tools.'
draft: false
schema: schema-openai-codex-cli-guide-2026
tags:
- ai-coding
- developer-tools
- ai-agents
- openai
title: 'OpenAI Codex CLI Guide 2026: Terminal AI Coding with the Rust-Built Agent'
---

OpenAI Codex CLI is a terminal-based AI coding agent that reads your codebase, writes and edits files, runs tests, and commits changes — all from your command line. Unlike web-based AI tools, Codex CLI runs locally against your actual repository, understanding real project context rather than a pasted snippet.

## What Is OpenAI Codex CLI? (The Rust-Built Terminal AI Agent)

OpenAI Codex CLI is an open-source, terminal-native AI coding agent that autonomously plans, writes, edits, and tests code within your local development environment. Unlike browser-based AI assistants, Codex CLI reads your entire codebase, executes shell commands, and manages file changes — operating as a true software engineering collaborator rather than a text-completion tool. Rebuilt in Rust as of June 2025 (now 95.6% Rust), the agent starts in milliseconds and consumes a fraction of the memory its Node.js predecessor required. As of April 2026, Codex CLI has surpassed 3 million weekly active users (confirmed by Sam Altman on April 8, 2026), 75,000+ GitHub stars, and 14.53 million npm downloads in March 2026 alone — a 177x increase year-over-year. With 696 releases in 12 months (nearly two per day), it is one of the fastest-evolving developer tools in the AI space. The key differentiator: Codex CLI operates under configurable approval policies, so you control how much autonomy the agent has before touching your files.

### Why the Rust Rewrite Matters

The June 2025 Rust rewrite transformed Codex CLI from a prototype into a production-grade tool. Startup time dropped from ~800ms to under 50ms, memory usage during large codebase scans fell by 60–70%, and binary distribution became cross-platform without Node.js as a dependency. For developers working in resource-constrained environments — CI runners, remote servers, Docker containers — these gains are material. The Rust core also enabled fine-grained sandbox controls that safely wall off filesystem and network access, which the previous JavaScript runtime couldn't enforce with the same precision.

---

## Installing Codex CLI on macOS, Windows, and Linux

Codex CLI installation takes under two minutes on any major platform. The three primary paths are npm (universal), Homebrew (macOS), and direct binary download (Linux/CI). Choose npm if you want the latest release immediately; choose Homebrew if you prefer managed updates integrated with your existing workflow. For CI pipelines or Docker images, the binary approach avoids runtime dependencies entirely. Before you install, confirm you have Node.js 18+ for the npm path or Homebrew 4.x for the brew path. The npm package `@openai/codex` has accumulated 32.8 million total downloads in the past 12 months, making it one of the most widely adopted developer CLI tools on the registry. Installation is the same whether you're targeting a personal MacBook, a Linux VPS, or a Windows machine via WSL2.

### macOS (Homebrew or npm)

```bash
# Option A: Homebrew (recommended for macOS)
brew install openai-codex

# Option B: npm global install
npm install -g @openai/codex

# Verify installation
codex --version
```

### Windows (PowerShell + WSL2)

Native Windows support runs through WSL2. PowerShell is supported with sandbox restrictions applied via Windows sandbox API.

```powershell
# Install WSL2 first if not present
wsl --install

# Then inside WSL2 terminal
npm install -g @openai/codex
```

For native PowerShell without WSL2:

```powershell
npm install -g @openai/codex
# Windows sandbox mode activates automatically — network calls are restricted
```

### Linux (npm or binary)

```bash
# npm path (requires Node.js 18+)
npm install -g @openai/codex

# Binary path (no Node.js needed, ideal for CI)
curl -fsSL https://releases.openai.com/codex/latest/codex-linux-x64 -o /usr/local/bin/codex
chmod +x /usr/local/bin/codex
```

---

## First Run: Authentication and Quick Start

Setting up Codex CLI authentication takes one command and about 60 seconds. Codex supports two auth paths: ChatGPT account login (browser OAuth flow) and direct API key injection. The ChatGPT account path is easier for individuals — it reuses your existing subscription and grants access to the latest Codex-specific model. The API key path is mandatory for CI/CD pipelines, team environments, and any context where a browser flow is unavailable. Once authenticated, Codex stores credentials in `~/.codex/auth.json` and reuses them across sessions. You do not need to re-authenticate per project; the credential is global. For teams, the recommended approach is injecting `OPENAI_API_KEY` as an environment variable to avoid credential files in shared environments. ChatGPT Plus and Team subscribers have Codex CLI access included in their plan; API-key users are billed per token at standard rates. After authentication, the recommended first action is running `codex "describe the architecture of this project"` on an existing codebase — this confirms connectivity and gives you a quick mental model of how Codex interprets your code before you ask it to change anything.

### Authenticating via ChatGPT Account

```bash
codex auth login
# Opens browser — approve in ChatGPT, token saved automatically
```

### Authenticating via API Key

```bash
export OPENAI_API_KEY="sk-..."
# Or add to your shell profile (~/.zshrc or ~/.bashrc)
echo 'export OPENAI_API_KEY="sk-..."' >> ~/.zshrc
```

### Your First Task

```bash
cd my-project
codex "add a JSON serialization function to utils.ts and write unit tests"
```

Codex reads the repository, proposes a plan, and (depending on your approval mode) either shows a diff for review or executes directly. The output includes changed files, test results, and a summary of what was done.

---

## Understanding the Three Approval Modes (Suggest, Auto Edit, Full Auto)

Codex CLI ships with three approval modes that control how much autonomy the agent has over your filesystem and shell. Choosing the right mode for the right context is the single most important configuration decision you'll make. **Suggest mode** (default) shows every proposed change as a diff and requires your explicit approval before writing a single file — ideal for unfamiliar codebases or sensitive production code. **Auto Edit mode** lets Codex write and modify files without per-change approval, but still asks before running shell commands like tests, installs, or builds — the sweet spot for active feature development on branches you own. **Full Auto mode** gives Codex complete autonomy: files, shell commands, and git operations all execute without interruption — best for isolated tasks in sandboxed environments or CI pipelines. As your trust in the agent grows and your sandbox configuration tightens, you can safely graduate from Suggest to Full Auto for routine tasks.

### Setting the Approval Mode

```bash
# Suggest mode (default — safe for first use)
codex --approval-mode suggest "refactor auth module"

# Auto Edit mode (writes files freely, asks before shell commands)
codex --approval-mode auto-edit "migrate all useState hooks to useReducer"

# Full Auto mode (fully autonomous — use in sandbox or on a branch)
codex --approval-mode full-auto "run all tests, fix failures, commit"
```

You can also set a default mode in `~/.codex/config.toml`:

```toml
[defaults]
approval_mode = "auto-edit"
```

### When to Use Each Mode

| Mode | File Writes | Shell Commands | Recommended For |
|---|---|---|---|
| Suggest | Needs approval | Needs approval | Unfamiliar repos, production hotfixes |
| Auto Edit | Automatic | Needs approval | Active feature branches, refactors |
| Full Auto | Automatic | Automatic | CI/CD pipelines, isolated sandboxes |

---

## AGENTS.md — How to Configure Codex for Your Project

AGENTS.md is an open standard file that tells AI coding agents — including Codex CLI, Claude Code, and compatible third-party tools — how to work in your specific project. It lives at the root of your repository and is automatically read by Codex on every invocation, functioning like a persistent system prompt scoped to your codebase. An effective AGENTS.md eliminates the need to repeat project-specific context in every command: your test commands, coding conventions, forbidden patterns, branch naming rules, and environment setup instructions belong here. In April 2026, AGENTS.md is increasingly treated as a first-class project artifact, often committed alongside `package.json` and `.eslintrc`. Think of it as documentation that your AI teammates read before touching a single file — the more specific and opinionated, the better the output quality.

### Example AGENTS.md

```markdown
# Project: Payments API

## Setup
- Node.js 20 LTS
- Run `npm install` before tasks
- Copy `.env.example` to `.env` and fill values for local DB

## Testing
- Unit tests: `npm test`
- Integration tests: `npm run test:int` (requires Docker)
- Always run unit tests before committing

## Conventions
- TypeScript strict mode — no `any` types
- Use named exports only — no default exports
- Prefer `zod` for runtime validation, not manual type guards

## Forbidden
- Never commit secrets or API keys
- Do not modify `src/migrations/` directly — use the CLI
- Do not add `console.log` to production code

## Branch Naming
- Features: `feat/TICKET-description`
- Fixes: `fix/TICKET-description`
```

### What to Include vs. Omit

| Include | Omit |
|---|---|
| Test commands and flags | Obvious conventions (use TypeScript → TS project) |
| Forbidden directories/patterns | Generic best practices |
| Environment setup steps | Framework documentation links |
| Project-specific naming conventions | Personal preferences |

---

## MCP Integration: Connecting Third-Party Tools to Codex

Model Context Protocol (MCP) integration transforms Codex CLI from a file editor into a full-stack development assistant with access to live external systems. MCP is an open standard that lets AI agents call external tools — browsers, databases, APIs, design tools — via a consistent interface. With MCP configured, Codex can scrape the live documentation of a library it needs to use, query your production database schema before writing a migration, or read Figma design specs before scaffolding a UI component. As of April 2026, over 200 community MCP servers are available, covering tools from Postgres and MySQL to Figma, GitHub, Slack, and Cloudflare Workers. The integration requires adding server definitions to `~/.codex/config.toml` — Codex handles the protocol negotiation automatically. Each MCP server runs as a subprocess managed by Codex, so you get isolated, per-session tool access without any persistent background service. Credentials are passed via environment variables rather than stored in config files, keeping secrets out of your repository.

### Configuring MCP Servers

```toml
# ~/.codex/config.toml

[[mcp_servers]]
name = "postgres"
command = "npx"
args = ["-y", "@modelcontextprotocol/server-postgres"]
env = { DATABASE_URL = "${DATABASE_URL}" }

[[mcp_servers]]
name = "github"
command = "npx"
args = ["-y", "@modelcontextprotocol/server-github"]
env = { GITHUB_TOKEN = "${GITHUB_TOKEN}" }

[[mcp_servers]]
name = "figma"
command = "npx"
args = ["-y", "@modelcontextprotocol/server-figma"]
env = { FIGMA_TOKEN = "${FIGMA_TOKEN}" }
```

### Practical MCP Use Cases

**Database-aware migrations:**
```bash
codex "analyze the users table schema and write a safe migration to add an email_verified column"
# Codex queries the live DB schema via MCP before writing migration code
```

**Design-to-code:**
```bash
codex "implement the LoginForm component from the Figma frame at [frame-url]"
# Codex reads actual design specs, not a screenshot
```

**GitHub-integrated workflow:**
```bash
codex "open a PR for the feature branch, link it to issue #142"
# Codex uses GitHub MCP to create the PR directly
```

---

## Advanced Configuration: Sandbox, Approval Policies, and config.toml

Advanced Codex CLI configuration via `~/.codex/config.toml` gives you fine-grained control over sandbox behavior, filesystem access policies, network restrictions, and per-project overrides. The sandbox system is one of Codex CLI's most important safety features — it limits what the agent can touch beyond the paths you explicitly whitelist, preventing runaway automation from modifying system files or making unintended network calls. Sandbox configuration became significantly more powerful with the Rust rewrite, which brought OS-level process isolation on macOS (via `sandbox-exec`) and Linux (via `seccomp`). For teams deploying Codex in CI, sandbox configuration is not optional — it is the primary safeguard ensuring agents operate within the intended blast radius. You can also use `CODEX_HOME` to maintain project-specific config profiles without modifying your global settings. Config keys are hot-reloaded between Codex sessions, so changes take effect immediately without reinstalling the CLI. The `[approval_policies]` section lets you override the global approval mode with per-operation granularity — for example, auto-approving file writes while still requiring confirmation for shell commands that delete or deploy resources.

### Full config.toml Reference

```toml
[defaults]
model = "codex-1"
approval_mode = "auto-edit"
context_window = 128000

[sandbox]
# Allow read access to the entire project
allow_read = ["."]
# Restrict writes to src/ and tests/ only
allow_write = ["src/", "tests/"]
# Block network access except for npm registry
allow_network = ["registry.npmjs.org"]
# Never allow these paths
deny_write = ["infrastructure/", ".env", "*.pem"]

[approval_policies]
# Auto-approve file writes, but require approval for destructive shell commands
shell_commands = "suggest"
file_writes = "auto"
git_operations = "auto"
```

### Per-Project Config via CODEX_HOME

```bash
# Use a project-specific config profile
export CODEX_HOME=~/projects/payments-api/.codex

# codex now reads ~/.../payments-api/.codex/config.toml
codex "add rate limiting to the auth endpoints"
```

---

## Multi-Agent Workflows with the OpenAI Agents SDK

Orchestrating Codex CLI as part of a multi-agent system via the OpenAI Agents SDK enables production-scale automation workflows that go far beyond what a single interactive session can accomplish. In a multi-agent setup, a coordinator agent breaks down a high-level goal (e.g., "ship this feature") into subtasks, spawns specialized Codex agents for each, collects outputs, runs validation, and gates the final commit behind automated checks. This architecture is increasingly common for CI/CD pipelines where agents handle the full loop: branch → implement → test → review → PR. The Agents SDK provides typed Python and TypeScript interfaces for spawning, monitoring, and composing agents, with built-in support for handoffs, guardrails, and tracing via OpenAI's observability dashboard. As of April 2026, teams at Stripe and GitHub have published case studies using this pattern for automated dependency upgrades and security patch automation.

### Example: Automated Bug Fix Pipeline

```python
from openai import agents

coordinator = agents.Agent(
    name="BugFixCoordinator",
    instructions="Break down bug reports into implementation tasks and delegate to Codex agents",
    tools=[agents.CodexTool(approval_mode="full-auto", sandbox=True)]
)

pipeline = agents.Pipeline([
    agents.Step("triage", coordinator),
    agents.Step("implement", agents.CodexAgent(task="fix the bug described in the issue")),
    agents.Step("test", agents.CodexAgent(task="run tests and fix any failures")),
    agents.Step("review", agents.CodeReviewAgent()),
    agents.Step("pr", agents.GitHubAgent(action="create_pr"))
])

result = pipeline.run(input="Fix bug #442: login form resets on validation error")
```

### Slash Commands in Interactive Mode

When running Codex interactively, slash commands switch context without leaving the session:

| Command | Action |
|---|---|
| `/model codex-1` | Switch model mid-session |
| `/approval auto-edit` | Change approval mode |
| `/context add src/auth/` | Add a directory to context |
| `/diff` | Show pending changes |
| `/commit` | Commit approved changes |
| `/reset` | Discard all pending changes |

---

## Codex CLI vs Claude Code: How to Use Both Effectively

Codex CLI and Claude Code are complementary tools that solve different parts of the AI-assisted development workflow, not direct competitors you must choose between. Codex CLI excels at autonomous, task-scoped operations: "implement this feature," "fix these failing tests," "migrate this API to the new schema." It operates in a fire-and-review model where you define a goal and let the agent work. Claude Code, by contrast, excels at interactive, exploratory sessions: understanding an unfamiliar codebase, debugging complex multi-service interactions, or pair-programming through a nuanced architectural decision. The key practical difference is conversational depth vs. autonomous execution depth. Developers who use both tools report a split of roughly 60/40 in favor of Codex CLI for implementation tasks and Claude Code for investigation and planning tasks. The two tools also share the AGENTS.md standard, so a well-written AGENTS.md file improves output quality for both simultaneously.

### Side-by-Side Comparison

| Dimension | Codex CLI | Claude Code |
|---|---|---|
| Primary mode | Autonomous execution | Interactive conversation |
| Ideal for | Feature implementation, test fixes, migrations | Codebase exploration, debugging, architecture |
| Context window | 128K tokens | 200K tokens |
| Approval model | Suggest / Auto Edit / Full Auto | Explicit approval per tool call |
| MCP support | Yes (config.toml) | Yes (settings.json) |
| CI/CD integration | Native via Full Auto + sandbox | Via headless mode |
| AGENTS.md support | Yes (primary format) | Yes (CLAUDE.md alias) |

### Recommended Split Workflow

```bash
# Phase 1: Understand with Claude Code
claude "explain how the payment processing pipeline works and identify potential race conditions"

# Phase 2: Implement with Codex CLI
codex --approval-mode auto-edit "add distributed locking to prevent the race condition in payment processing"

# Phase 3: Review with Claude Code
claude "review the changes in the last commit — do they fully address the race condition?"

# Phase 4: Ship with Codex CLI
codex --approval-mode full-auto "run integration tests, fix any failures, open a PR"
```

---

## Real Developer Workflow: Branch → Code → Review → Commit

A complete real-world Codex CLI workflow starts with a feature branch and ends with a reviewed, tested commit — the agent handles every step between those bookends. This workflow pattern takes advantage of Codex CLI's AGENTS.md awareness (no repeated context), its MCP integration (live database schema, GitHub API), and its approval mode graduation (Suggest for sensitive changes, Full Auto for mechanical tasks). The key practice that experienced Codex users consistently recommend: always start a new git branch before invoking Codex with Auto Edit or Full Auto mode. This ensures that every agent-made change is isolated, reviewable as a diff, and reversible with a single `git checkout main`. Teams that skip this step report harder-to-audit histories; teams that adopt it report higher confidence in merging agent-generated code.

### Step-by-Step: Feature Implementation

```bash
# 1. Start from a clean branch
git checkout -b feat/PROJ-442-add-2fa

# 2. Run Codex in Auto Edit mode (it will ask before shell commands)
codex --approval-mode auto-edit \
  "implement TOTP-based 2FA for the auth module. Use speakeasy library.
   Add unit tests. Follow the conventions in AGENTS.md."

# 3. Review the diff
git diff

# 4. Run tests manually or let Codex do it
codex "run tests and summarize results"

# 5. Approve the changes and commit
git add -p   # Review each hunk
git commit -m "feat(auth): add TOTP-based 2FA via speakeasy"

# 6. Push and open PR (optionally via Codex + GitHub MCP)
codex --approval-mode full-auto "push this branch and open a PR linking to PROJ-442"
```

### Pre-Commit Code Review Subagent

Codex includes a built-in code review subagent that activates before commits when configured:

```toml
# ~/.codex/config.toml
[git]
pre_commit_review = true
review_model = "codex-1"
block_on_issues = ["security", "hardcoded_secrets"]
warn_on_issues = ["performance", "test_coverage"]
```

With this configuration, every `git commit` triggers an automated review. Blocking issues prevent the commit; warnings are logged but allow it to proceed. This effectively gives every developer an automated code reviewer that runs at commit time, not just in CI.

---

## FAQ

**Q: Do I need an OpenAI API key to use Codex CLI?**

No — you can authenticate via your existing ChatGPT account using `codex auth login`, which opens a browser OAuth flow. An API key is required only for CI/CD pipelines, team environments, or contexts where a browser flow is unavailable. ChatGPT Plus and Team subscribers have Codex CLI access included; API key usage is billed per token.

**Q: How does Codex CLI handle large codebases with millions of lines?**

Codex CLI uses intelligent context selection rather than loading the entire codebase into the context window. It reads project structure, locates relevant files via semantic search and file tree analysis, and loads only the files pertinent to the current task — typically staying well within the 128K token context window. You can supplement this with `AGENTS.md` to explicitly point Codex at critical files or directories.

**Q: Is it safe to run Codex in Full Auto mode on production code?**

Only with sandbox restrictions configured. Full Auto mode on an unrestricted environment can modify any file the process has access to. The recommended practice is to configure `[sandbox]` in `config.toml` to limit `allow_write` to specific directories, and always run Full Auto on a git branch — never directly on `main`. For CI/CD use, combine Full Auto with Docker container isolation for defense-in-depth.

**Q: Can Codex CLI work offline?**

No — Codex CLI requires an active network connection to reach OpenAI's inference API. The Rust binary itself runs locally, but all model inference is server-side. For air-gapped environments, OpenAI provides an enterprise on-premises deployment option; contact their sales team for access.

**Q: How does AGENTS.md differ from a `.cursorrules` or `CLAUDE.md` file?**

AGENTS.md is the open standard proposed by OpenAI to unify AI agent configuration across tools. CLAUDE.md (used by Claude Code) and `.cursorrules` (used by Cursor) are tool-specific variants with similar purposes. Codex CLI reads `AGENTS.md` natively; Claude Code reads both `CLAUDE.md` and `AGENTS.md`. Writing your conventions in `AGENTS.md` maximizes compatibility across AI coding tools without duplicating configuration.