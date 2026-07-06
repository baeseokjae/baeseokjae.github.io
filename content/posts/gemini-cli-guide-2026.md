---
cover:
  alt: 'Gemini CLI Guide 2026: How to Use Google Gemini from the Terminal'
  image: /images/gemini-cli-guide-2026.png
  relative: false
date: 2026-04-16 01:01:43+00:00
description: 'Complete Gemini CLI guide 2026: install, authenticate, and use Google
  Gemini in your terminal with 1M token context and a generous free tier.'
draft: false
schema: schema-gemini-cli-guide-2026
tags:
- gemini-cli
- ai-coding-tools
- terminal
- google-gemini
- developer-tools
title: 'Gemini CLI Guide 2026: How to Use Google Gemini from the Terminal'
---

Gemini CLI is Google's open-source terminal AI agent that gives you access to Gemini 2.5 Pro — with a 1 million token context window — for free, with no credit card required. Install it with one `npm` command, sign in with your Google account, and you're ready to query, code, and automate from the terminal within 60 seconds.

## What Is Gemini CLI?

Gemini CLI is an open-source, Apache 2.0-licensed AI agent that runs directly in your terminal, powered by Google's Gemini models. Launched officially by Google in 2025 and now at v0.32.1 (March 2026) with Gemini 3 support, it has accumulated 96,600+ GitHub stars — making it one of the most popular developer tools in the AI ecosystem. Unlike proprietary desktop IDEs or subscription-gated copilots, Gemini CLI gives every developer free access to Gemini 2.5 Pro's 1 million token context window at 60 requests per minute and 1,000 requests per day — the industry's most generous free tier, with no credit card required. The tool spans a wide range of tasks: code generation, debugging, file manipulation, shell command execution, image analysis, PDF summarization, and deep research. Its open-source nature means you can inspect the code, contribute fixes, and audit exactly what happens with your data — something closed-source alternatives cannot offer.

## System Requirements and Prerequisites

Gemini CLI runs on any modern developer machine but has firm minimum requirements you should verify before installing. As of v0.32.1 (March 2026), the tool requires Node.js 20 or higher, at least 4 GB of RAM (16 GB recommended for large-context operations), and a supported operating system: macOS 15 Sequoia or later, Windows 11 24H2 or later, or Ubuntu 20.04 LTS or later. Shell compatibility varies — Bash and Zsh work fully out of the box, PowerShell 7+ is supported on Windows, but Fish shell has only limited support and may produce unexpected behavior. On Windows, the recommended setup is Windows Terminal running PowerShell 7+ or, for full Linux compatibility, WSL2 with Ubuntu. Checking prerequisites takes under two minutes and prevents the majority of installation failures — most reported issues trace back to an outdated Node.js version or an unsupported shell environment.

### Operating System Support

Gemini CLI supports macOS 15+, Windows 11 24H2+ (via PowerShell or WSL2), and Ubuntu 20.04+. On Windows, the recommended setup is Windows Terminal running PowerShell 7+ or WSL2 with Ubuntu. Fish shell has limited support; Bash and Zsh work out of the box. macOS users on Ventura (13) or Sonoma (14) may encounter issues and should upgrade to Sequoia (15).

### Node.js Version

Gemini CLI requires Node.js 20 or higher. Node.js 22 LTS is the recommended version for best performance and long-term support. You can check your version with `node --version` and install the latest LTS via `nvm install --lts` if needed. The tool also requires at least 4 GB of RAM, though 16 GB is recommended for large context operations involving million-token prompts.

## How to Install Gemini CLI

Gemini CLI offers seven installation methods. The recommended approach is a global npm install, which takes under 30 seconds on a typical connection:

```bash
npm install -g @google/gemini-cli
```

After installation, verify it works:

```bash
gemini --version
```

**Alternative installation methods:**

| Method | Command | Best For |
|--------|---------|----------|
| npm global (recommended) | `npm install -g @google/gemini-cli` | Most developers |
| npx (no install) | `npx @google/gemini-cli` | Quick trial |
| Homebrew (macOS) | `brew install gemini-cli` | macOS users |
| Docker | `docker run -it gcr.io/google-gemini/gemini-cli` | Sandboxed environments |
| Yarn global | `yarn global add @google/gemini-cli` | Yarn users |
| pnpm global | `pnpm add -g @google/gemini-cli` | pnpm users |
| Snap (Linux) | `snap install gemini-cli` | Ubuntu/Snap systems |

For teams evaluating the tool without committing to a global install, `npx` is ideal — it downloads and runs the latest version on the fly without any global state.

## Authentication Options

Gemini CLI offers three authentication methods, each suited to different use cases.

**Google OAuth (Free — Recommended for Most Developers)**

This is the default and easiest option. Run `gemini auth login` and a browser window opens to authenticate with your Google account. You get 60 requests per minute and 1,000 requests per day at zero cost — no credit card, no trial period. The free tier uses the same Gemini 2.5 Pro model as the paid API.

**Google AI Studio API Key (Pay-As-You-Go)**

For developers who exceed the free tier or need programmatic access, create an API key at aistudio.google.com and export it:

```bash
export GEMINI_API_KEY="your-api-key-here"
```

Gemini Flash models are particularly cost-effective for high-volume tasks like log parsing and automated scripts.

**Vertex AI (Enterprise)**

For enterprise teams with GCP billing, Vertex AI authentication unlocks SLA guarantees, regional data residency, and audit logging. Set up with `gcloud auth application-default login` and configure your project:

```bash
export GOOGLE_CLOUD_PROJECT="your-gcp-project-id"
```

## Free Tier Deep Dive

The Gemini CLI free tier is the most generous offering in the terminal AI agent market as of 2026. Here are the specifics:

- **60 requests per minute** (RPM) — enough for real interactive development sessions
- **1,000 requests per day** (RPD) — covers typical full-day developer usage
- **No credit card required** — authentication via Google account only
- **Same model access** — Gemini 2.5 Pro, identical to the paid API tier
- **1 million token context window** — ingest entire repositories in a single prompt

For context: GitHub Copilot Individual costs $10/month with no terminal access. Claude Code charges per token. Cursor Pro runs $20/month. Gemini CLI's free tier exceeds all of these for daily individual usage — the only cost is rate limits during burst periods.

## Key Features and Capabilities

Gemini CLI is built around a core set of tools that operate directly on your filesystem and shell environment. Understanding what each tool does helps you design effective prompts.

**Code Generation and Editing**

Gemini CLI can create new files, modify existing ones, and refactor across multiple files simultaneously. With a 1 million token context window, you can pass an entire medium-sized codebase as context. Example:

```bash
gemini "Add input validation to all API endpoints in src/routes/ and write unit tests for each"
```

**Google Search Grounding**

Unlike most AI coding tools, Gemini CLI has native Google Search integration. It can ground answers in real-time search results — useful for "what's the current syntax for X in library Y version Z?" queries where training data may be stale.

**Multimodal Input**

Gemini CLI accepts images, PDFs, and diagrams as input. Pass a screenshot of an error, an architecture diagram, or a UI mockup:

```bash
gemini "Here's a screenshot of the error: error.png — what's causing it and how do I fix it?"
```

**Non-Interactive Scripting Mode**

For CI/CD pipelines and automation scripts, use `--non-interactive` mode. This disables prompts and returns structured output suitable for piping:

```bash
gemini --non-interactive "Review this diff for security issues" < git.diff
```

**MCP Server Integration**

Gemini CLI supports the Model Context Protocol (MCP), allowing integration with external tools — databases, APIs, file systems, and custom services. Configure MCP servers in `~/.gemini/settings.json`.

## GEMINI.md, MCP Servers, and settings.json

Gemini CLI's customization system has three layers that work together to make the tool aware of your specific project, tools, and preferences. The first layer is `GEMINI.md`, a plain Markdown file you place at the root of any project to provide persistent context — stack details, coding conventions, and off-limits files — without repeating them in every prompt. The second layer is `settings.json` at `~/.gemini/settings.json`, which controls global defaults like sandbox mode, auto-approval behavior, and default model. The third layer is MCP server integration, which extends Gemini CLI's built-in tools with external services: databases, APIs, file systems, and custom automation. Together, these three mechanisms transform a generic AI terminal agent into a tool that understands your specific codebase, respects your team's conventions, and can reach out to your infrastructure. Setting up all three layers takes about 15 minutes and pays dividends in every subsequent session.

### GEMINI.md — Project-Level Context

Similar to `.cursorrules` or `CLAUDE.md`, you can create a `GEMINI.md` file at the root of any project to give Gemini persistent context about your codebase:

```markdown
# Project: Payment Service

**Stack**
- Node.js 22, TypeScript 5, Fastify 4
- PostgreSQL 16 with Prisma ORM
- Jest for testing, Biome for linting

**Conventions**
- All monetary values stored in cents (integer), never floats
- Use zod for all request validation
- Prefer functional patterns over class-based

**Off-Limits**
- Never modify db/migrations directly — use `prisma migrate dev`
```

Gemini CLI reads this file automatically when you run it from that directory. Project-level instructions take precedence over default behavior.

### settings.json Configuration

Global settings live at `~/.gemini/settings.json`. Key configuration options:

```json
{
  "defaultModel": "gemini-2.5-pro",
  "sandbox": true,
  "autoApprove": false,
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"]
    }
  }
}
```

### MCP Integration Example

To add a PostgreSQL MCP server for database-aware queries:

```json
{
  "mcpServers": {
    "postgres": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres"],
      "env": {
        "DATABASE_URL": "postgresql://localhost/mydb"
      }
    }
  }
}
```

Once configured, Gemini CLI can query your schema and write migrations with full awareness of your actual database structure.

## Safety Model: Sandbox Mode, Explicit Approvals, and Checkpointing

Gemini CLI's safety model is built around three mechanisms that prevent unintended changes. Every file modification and shell command requires explicit user approval by default — the CLI shows you exactly what will change before executing. You can type `y` to approve, `n` to reject, or `e` to edit the proposed change.

**Sandbox Mode** runs Gemini CLI inside a Docker or Podman container, isolating all filesystem and network access. Enable it globally in `settings.json` with `"sandbox": true` or per-session with `gemini --sandbox`. In sandbox mode, any command that would affect your host system requires an explicit breakout approval.

**Checkpointing** creates automatic snapshots before any batch of file changes. If a refactoring goes wrong, roll back with:

```bash
gemini checkpoint restore
```

This is especially valuable during large-scale refactors where multiple files change simultaneously. Unlike a simple `git stash`, checkpoints capture the exact state at each approval point, letting you step back incrementally.

## Real-World Workflows and Use Cases

Gemini CLI's combination of a 1 million token context window, Google Search grounding, multimodal input, and non-interactive scripting mode makes it uniquely suited for several developer workflows that other tools handle poorly. Where most AI coding tools force you to cherry-pick files to stay within a 64K or 128K context limit, Gemini CLI lets you reason about an entire codebase in a single prompt. Where other tools require web searches or browsing integrations, Gemini CLI grounds answers natively in real-time Google Search results. And where interactive tools fall short in automation, the `--non-interactive` mode enables Gemini CLI to run cleanly in CI/CD pipelines. The four most productive use cases — large codebase analysis, DevOps scripting, rapid prototyping, and documentation generation — each leverage a different combination of these capabilities and represent where Gemini CLI consistently outperforms narrower alternatives.

### Large Codebase Analysis

The 1 million token context window is Gemini CLI's most distinctive capability. A typical Node.js monorepo with 200+ files might total 150,000–300,000 tokens — well within a single context. This enables queries impossible with smaller-context tools:

```bash
gemini "Find all places where we directly mutate shared state across the entire src/ directory and suggest refactors"
```

### DevOps and Infrastructure Scripting

Gemini CLI excels at writing and debugging shell scripts, Dockerfiles, and CI/CD configurations. The Google Search grounding keeps syntax references current:

```bash
cat failing-deploy.log | gemini "Diagnose this Kubernetes deployment failure and write a corrected deployment.yaml"
```

### Rapid Prototyping

The fast iteration loop — type a prompt, approve changes, see results — makes Gemini CLI ideal for throwaway prototypes and spike solutions. The free tier's 60 RPM supports aggressive back-and-forth without cost concerns.

### Documentation Generation

Feed Gemini CLI an entire module and generate comprehensive documentation:

```bash
gemini "Read src/auth/ and generate API documentation in Markdown format, including parameter types, return values, and error codes"
```

## Gemini CLI vs Claude Code vs Cursor vs GitHub Copilot (2026 Comparison)

| Feature | Gemini CLI | Claude Code | Cursor | GitHub Copilot |
|---------|-----------|-------------|--------|----------------|
| Price (free tier) | 1,000 req/day free | Token-based, no free tier | Free plan limited | Free for students |
| Context window | 1M tokens | 200K tokens | 128K tokens | 64K tokens |
| Terminal-native | Yes | Yes | No (IDE) | Partial (CLI) |
| Open source | Yes (Apache 2.0) | No | No | No |
| MCP support | Yes | Yes | No | No |
| Search grounding | Yes (Google Search) | No | No | No |
| Multi-file edits | Yes | Yes | Yes | Limited |
| Autonomous agents | Yes | Yes | Yes | Limited |
| Best for | High-volume, large context | Complex reasoning, safety | IDE users | IDE-first teams |

Gemini CLI wins on context size, price, and openness. Claude Code wins on reasoning depth and multi-step autonomous workflows — teams using Claude Code report 2–5× faster feature completion on complex tasks. The tools complement rather than replace each other.

## Performance Benchmarks: Speed vs Quality

Gemini CLI is optimized for speed and throughput over deliberative reasoning, and its benchmark profile reflects that design choice. In 2026 testing, Gemini Flash delivers ~0.8 seconds to first token — the fastest among major terminal AI agents — while Gemini Pro averages ~2.1 seconds, still competitive against Claude Sonnet and GPT-4.1. On HumanEval coding benchmarks, Gemini 2.5 Pro scores on par with Claude Sonnet 3.7 and GPT-4.1. Gemini 3.1 Pro Preview (available since v0.31.0) shows measurable improvement on multi-file reasoning tasks. The 60 RPM free tier is sufficient for continuous interactive sessions without throttling under normal development patterns. Where Gemini CLI lags is on complex multi-step reasoning tasks requiring careful dependency tracking across many files — here Claude Code's deliberative approach catches more subtle bugs and produces fewer regressions.

In 2026, Gemini CLI benchmarks show:

- **Latency**: ~0.8s to first token (Gemini Flash), ~2.1s (Gemini Pro) — faster than most alternatives
- **Throughput**: 60 RPM on free tier is sufficient for continuous interactive sessions
- **Context retention**: 1M tokens with minimal degradation up to ~800K tokens in practice
- **Code quality**: Gemini 2.5 Pro scores on par with GPT-4.1 and Claude Sonnet on HumanEval; Gemini 3.1 Pro Preview shows improvement on multi-file reasoning

The trade-off: Gemini CLI is optimized for speed and throughput. For tasks requiring careful multi-step reasoning across interdependent changes — large architectural refactors, security-sensitive code — Claude Code's deliberative approach catches more subtle issues.

## Hybrid Workflow Pattern: Gemini CLI + Other Tools

The most productive engineering teams in 2026 treat AI coding tools as complementary rather than competitive, assigning each tool to the workflow phase where it excels. Gemini CLI's strengths — free tier velocity, 1M token context, and fast iteration — make it ideal for the early exploratory phases of development. Claude Code's strengths — careful multi-step reasoning, visual diffs, and autonomous multi-file coordination — make it better for production-grade implementation and review. GitHub Copilot's tight IDE integration handles inline autocomplete and PR review within familiar editors. This three-tier hybrid pattern emerged organically among senior developers who found that using a single tool for every task consistently produced suboptimal results. The workflow below describes how these tools chain together across a typical feature development cycle, from initial exploration through production deployment.

The most productive developers in 2026 use Gemini CLI as part of a toolkit rather than an all-in-one solution. A common hybrid workflow:

1. **Exploration and prototyping with Gemini CLI** — use the 1M context to understand a large codebase, generate boilerplate, or spike out an approach quickly
2. **Deep implementation with Claude Code** — switch to Claude Code for production features requiring careful reasoning and multi-file coordination
3. **Review and CI with GitHub Copilot** — use Copilot's IDE integration for inline completions and PR reviews

This pattern combines Gemini CLI's free-tier velocity with Claude Code's reasoning depth and Copilot's IDE fluency. No single tool wins on all dimensions.

## Troubleshooting Common Issues

Gemini CLI issues fall into four predictable categories: Node.js version mismatches, authentication failures, sandbox container problems, and rate limit errors. The majority of installation failures trace back to running an outdated Node.js — checking `node --version` before filing a bug report resolves about 40% of reported issues. Authentication failures are almost always caused by browser or network problems during the OAuth flow, or missing environment variable exports for API key auth. Sandbox issues invariably mean Docker Desktop isn't running or lacks sufficient permissions. Rate limit errors (HTTP 429) during free-tier usage indicate burst usage exceeding 60 RPM, which rarely affects interactive sessions but can surface in tight automation loops. This section covers the fix for each scenario with the exact commands to run, so you can diagnose and resolve the most common problems in under five minutes.

### Node.js Version Errors

```
Error: requires Node.js 20+
```

Fix: `nvm install 22 && nvm use 22`

### Authentication Failures

If `gemini auth login` fails to open a browser or hangs, try:

```bash
gemini auth login --no-browser
```

This prints a URL to paste manually. For API key auth, ensure the key is exported in the same shell session where you run Gemini CLI.

### Sandbox Not Starting

Docker Desktop must be running for sandbox mode. If you see `Error: sandbox container failed to start`:

```bash
docker info  # Verify Docker is running
gemini --sandbox  # Retry with explicit sandbox flag
```

### Rate Limit Errors (429)

If you hit 60 RPM on the free tier, the CLI surfaces a `RESOURCE_EXHAUSTED` error. Solutions: add a brief pause between automated calls, switch to an AI Studio API key for pay-as-you-go, or use Gemini Flash for lower-cost high-volume operations.

### GEMINI.md Not Loading

Ensure the file is in the directory where you launch Gemini CLI (not a parent directory). Use `gemini --context GEMINI.md` to explicitly specify the path if needed.

## FAQ

**Q: Is Gemini CLI actually free?**

Yes. The Google OAuth authentication path gives you 60 requests per minute and 1,000 requests per day at no charge, with no credit card required. This uses Gemini 2.5 Pro — the same model available on the paid API. For most individual developers, the free tier covers full-day usage.

**Q: How does the 1 million token context window work in practice?**

You can pass entire codebases, multiple documents, or long conversation histories as context. In practice, performance begins to degrade slightly above ~800K tokens, but for typical use cases — a medium-sized repo plus your query — 1M tokens is more than sufficient. Competitors like Claude Code offer 200K tokens; GitHub Copilot offers 64K.

**Q: Can I use Gemini CLI in CI/CD pipelines?**

Yes. Use `--non-interactive` mode with an AI Studio API key (not Google OAuth, which requires browser authentication). This mode disables interactive prompts and outputs results as structured text suitable for shell piping and automated workflows.

**Q: Is Gemini CLI safe to use on production code?**

Gemini CLI requires explicit approval for every file modification and shell command by default. Sandbox mode adds Docker-level isolation. For production code, always run with `"autoApprove": false` in settings.json and review every proposed change before approving. Use checkpoints before large batch operations.

**Q: What is GEMINI.md and do I need it?**

GEMINI.md is an optional project-level configuration file that gives Gemini persistent context about your codebase — stack, conventions, off-limits files, and preferences. It's equivalent to `.cursorrules` for Cursor or `CLAUDE.md` for Claude Code. You don't need it for basic use, but it dramatically improves output quality in established projects by eliminating repeated context-setting.