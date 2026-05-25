---
title: "Google Agentic Terminal Agent 2026: ReAct Loop + MCP + 1M Context Setup Guide"
date: 2026-05-23T04:15:40+00:00
tags: ["gemini-cli", "mcp", "agentic-ai", "google-adk", "terminal-agent"]
description: "Complete setup guide for Gemini CLI as an agentic terminal agent — ReAct loop internals, MCP server config, and 1M token context window best practices."
draft: false
cover:
  image: "/images/google-agentic-terminal-agent-guide-2026.png"
  alt: "Google Agentic Terminal Agent 2026: ReAct Loop + MCP + 1M Context Setup Guide"
  relative: false
schema: "schema-google-agentic-terminal-agent-guide-2026"
---

Gemini CLI is Google's open-source agentic terminal agent built on Gemini 2.5 Pro, offering a 1M token context window, a native ReAct reasoning loop, and MCP server integration — free at 1,000 requests/day with a personal Google account. Here's the complete setup and configuration guide for 2026.

## What Is Gemini CLI? Google's Open-Source Agentic Terminal Agent

Gemini CLI is a command-line interface that wraps Gemini 2.5 Pro's reasoning capabilities into an autonomous coding agent capable of reading files, running shell commands, calling external tools, and iterating on errors — all from your terminal. Unlike a simple chat interface, Gemini CLI implements a full ReAct (Reason-and-Act) loop where the model reasons about a goal, selects a tool, executes it, observes the result, and continues reasoning until the task is complete. Released in late 2025 and significantly updated in early 2026, it supports MCP (Model Context Protocol) for extending its toolset, and ships with built-in capabilities for Google Search grounding, file operations, and web fetching. The free tier offers 60 requests/minute and 1,000 requests/day with a personal Google account — enough for real development workflows. Gemini 2.5 Pro's 1M token context window is roughly 5x the capacity of standard Claude tiers and 8x that of GPT-4o, enabling full codebase analysis without chunking or RAG pipelines.

### How It Differs From Traditional CLI Tools

Gemini CLI isn't a shell wrapper or a code completion plugin. It's an autonomous loop: you describe a goal, and the agent plans, executes, observes results, and adapts — handling multi-step workflows that would require manual orchestration with any other tool. A 600K-token Next.js codebase was loaded in a single context window, and Gemini 2.5 Pro correctly identified a cross-module bug spanning four files without chunking. That's not possible with tools capped at 128K or 200K tokens.

## Inside the ReAct Loop: How Gemini CLI Reasons and Acts

Gemini CLI's agentic core implements a ReAct (Reason + Act) loop that processes every user prompt through a structured cycle: receive input → reason about goal and available tools → select tool → execute → observe output → reason again → repeat until done. This loop is not a fixed workflow — it's a dynamic planning system where the model decides at each step whether to call another tool, ask for clarification, or declare the task complete. Internally, the loop runs through `discoverMcpTools()`, which iterates configured MCP servers from `settings.json`, establishes connections, fetches tool definitions, and sanitizes schemas to match Gemini API format. When a shell command fails, the ReAct loop reads the error output and automatically attempts a fix — often correcting syntax errors, missing permissions, or wrong file paths without user intervention. This error-retry mechanism is what separates agentic terminals from simple prompt-and-response chat interfaces. As of 2026, 52% of executives in gen-AI-using organizations report deployed AI agents — and the terminal agent pattern is central to that adoption.

### Tool Discovery and Schema Validation

When Gemini CLI starts, it calls `discoverMcpTools()` for each server listed under `mcpServers` in `~/.gemini/settings.json`. The function opens a transport connection (Stdio, SSE, or HTTP), fetches the `tools/list` endpoint, and validates each returned schema against Gemini's function-calling spec. Tools with invalid schemas are silently skipped — so if a tool isn't appearing in `/mcp`, check the server's schema output for missing `type` fields or malformed JSON. The sanitized tools become available in the reasoning loop exactly like built-in tools.

### Error Retry and Self-Correction

When a command returns a non-zero exit code, Gemini CLI feeds the stderr output back into the reasoning loop. The model reasons about what went wrong, generates a corrected command, and retries — up to a configurable maximum. This means a command like `npm install` that fails due to a missing `.nvmrc` will trigger the agent to check the Node version, switch it, and retry — without you intervening. Set `maxRetries` in `settings.json` to control this behavior.

## Installation and Initial Authentication Setup

Installing Gemini CLI takes under two minutes on any system with Node.js 18+: install via npm (`npm install -g @google/gemini-cli`), run `gemini` to trigger the OAuth flow, and authenticate with your personal Google account. The tool stores OAuth credentials in `~/.gemini/credentials.json` and reads all configuration from `~/.gemini/settings.json`. For team or CI environments, set the `GEMINI_API_KEY` environment variable instead of OAuth — this bypasses free-tier rate limits and routes requests through your billed API quota, which supports higher throughput and removes the 1,000 request/day ceiling. The personal free tier provides 60 requests/minute and 1,000 requests/day at no cost, making it practical for solo development workflows without any payment setup. Plan Mode, MCP server configuration, and context window settings are all managed via `settings.json` — no separate config command is needed after the initial install.

```bash
# Install globally
npm install -g @google/gemini-cli

# First run triggers OAuth
gemini

# Or set an API key for CI/team use
export GEMINI_API_KEY="your-key-here"
gemini "summarize the changes in this PR"
```

### Verifying Your Setup

Run `gemini --version` to confirm the install, and `gemini /tools` to see which built-in tools are available. If you've configured MCP servers, run `gemini /mcp` to check connection status and list available tools from each server. A healthy output shows each server name, status (`connected`), and a list of discovered tool names.

## Configuring MCP Servers in ~/.gemini/settings.json

MCP server configuration lives in `~/.gemini/settings.json` under the `mcpServers` block. Each entry names a server and specifies its launch command, arguments, and optional environment variables. Environment variables in the `env` block are auto-expanded at startup — this is the secure way to inject API keys and credentials without hardcoding them in the config file. To add a server, edit `settings.json` directly (there's no GUI config tool), then restart Gemini CLI. Use `gemini mcp enable <name>` and `gemini mcp disable <name>` to toggle servers without editing the file. Run `/mcp` inside a session to inspect connection status and confirm tools loaded correctly.

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/workspace"],
      "transport": "stdio"
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "transport": "stdio",
      "env": {
        "GITHUB_TOKEN": "${GITHUB_TOKEN}"
      }
    },
    "postgres": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres"],
      "transport": "stdio",
      "env": {
        "DATABASE_URL": "${DATABASE_URL}"
      }
    }
  }
}
```

### Enabling and Disabling Servers

```bash
# Toggle without editing settings.json
gemini mcp disable github
gemini mcp enable github

# Check status in a live session
gemini
> /mcp
```

## Transport Options: Stdio vs SSE vs Streamable HTTP

Gemini CLI supports three MCP transport protocols, and picking the right one depends on where your server runs and how it handles connections. Stdio is the default and most reliable option for local servers — Gemini CLI spawns the server as a child process, connects via stdin/stdout pipes, and manages the lifecycle automatically. SSE (Server-Sent Events) works for remote servers that push events over HTTP — useful when the MCP server is a persistent service rather than a per-request process. Streamable HTTP is the newest transport, designed for high-throughput scenarios where SSE's uni-directional model is limiting; it uses HTTP/2 streaming and handles bidirectional communication more efficiently. For local tools (filesystem, database, git), use Stdio. For shared team tools or cloud services, use SSE or Streamable HTTP with proper authentication headers.

```json
{
  "mcpServers": {
    "local-tool": {
      "command": "node",
      "args": ["./mcp-server.js"],
      "transport": "stdio"
    },
    "remote-tool": {
      "url": "https://tools.example.com/mcp/sse",
      "transport": "sse",
      "headers": {
        "Authorization": "Bearer ${REMOTE_TOOL_API_KEY}"
      }
    },
    "high-throughput-tool": {
      "url": "https://tools.example.com/mcp/stream",
      "transport": "http"
    }
  }
}
```

### When SSE Causes Problems

SSE connections drop silently if the server doesn't send keepalive events. If a remote MCP tool shows `connected` in `/mcp` but fails when invoked, add a timeout check: `gemini mcp test <name>`. Locally-run Stdio servers restart automatically on failure; remote SSE servers require your server infrastructure to handle reconnection.

## Leveraging the 1M Token Context Window for Large Codebases

Gemini 2.5 Pro's 1M token context window eliminates the chunking and RAG pipelines that smaller-context models require for large-codebase analysis. At roughly 4 characters per token, 1M tokens covers approximately 4MB of raw text — enough for most production monorepos, complete API documentation sets, or the combined source, test, and configuration files of a mid-size service. This is roughly 5x the capacity of standard Claude tiers and 8x that of GPT-4o, which means Gemini CLI can hold an entire backend service in context while the agent reasons across all files simultaneously. The practical sweet spot for reliable analysis sits around 600–700K tokens; accuracy begins to degrade near the extreme ceiling. Load a codebase by pointing Gemini CLI at a directory: `gemini "analyze the auth module" --context ./src`. No semantic search, no chunking, no approximate retrieval — the entire codebase is in the reasoning window at once.

### What to Load and What to Leave Out

Token budget allocation matters even with 1M tokens. Load source files, tests, and configuration. Exclude build artifacts (`node_modules`, `dist`, `.next`), binary files, and auto-generated code — they consume tokens without adding signal. Use `.geminiignore` (same syntax as `.gitignore`) to exclude patterns automatically.

```
# .geminiignore
node_modules/
dist/
.next/
*.min.js
coverage/
*.lock
```

### Real-World Codebase Analysis

A 600K-token Next.js codebase was analyzed by Gemini 2.5 Pro in a single context — the model identified a bug where a middleware caching layer was invalidating session tokens for a specific user-agent pattern, tracing the issue across four files (`middleware.ts`, `auth/session.ts`, `api/user.ts`, and a utility in `lib/cache.ts`). A chunked approach with RAG would have required the right semantic query to surface all four files simultaneously. With the full context loaded, the model found the interaction pattern without any query tuning.

## Integrating Google ADK for Multi-Agent Workflows

Google ADK (Agent Development Kit) integrates with Gemini CLI to add multi-agent orchestration on top of the terminal interface. ADK supports Python, Go, Java, and TypeScript as of 2026, and allows you to define sub-agents with specialized tools, route tasks between them, and aggregate results — all while using Gemini CLI as the user-facing frontend. ADK agents can act as MCP clients (consuming tools from MCP servers) and can themselves expose tools via MCP servers, making them composable. The most useful pattern is a supervisor agent that delegates to specialist agents: a code-review agent, a test-runner agent, and a deployment agent, each with different tool access and system prompts, orchestrated by a parent Gemini CLI session. This eliminates the friction between terminal convenience and the complex multi-step workflows that production engineering tasks require.

### Setting Up a Basic ADK Agent

```python
# agent.py — minimal ADK agent that Gemini CLI can invoke
from google.adk import Agent, Tool

@Tool
def run_tests(path: str) -> str:
    """Run the test suite at the given path and return results."""
    import subprocess
    result = subprocess.run(["pytest", path, "--tb=short"], capture_output=True, text=True)
    return result.stdout + result.stderr

agent = Agent(
    name="test-runner",
    model="gemini-2.5-pro",
    tools=[run_tests],
    system_prompt="You are a test runner agent. Run tests and report failures with fix suggestions."
)
```

Register the ADK agent as an MCP server in `settings.json`, and Gemini CLI can call it as a tool in its ReAct loop.

### ADK Multi-Agent Pattern

```python
from google.adk import Agent, Router

code_reviewer = Agent(name="reviewer", tools=[read_pr, post_comment])
test_runner = Agent(name="tester", tools=[run_tests, read_coverage])
deployer = Agent(name="deployer", tools=[run_deploy, check_health])

supervisor = Router(
    agents=[code_reviewer, test_runner, deployer],
    model="gemini-2.5-pro",
    routing_prompt="Route tasks to the appropriate specialist agent based on the request."
)
```

## Gemini CLI vs Claude Code vs Codex CLI: 2026 Honest Comparison

Each of the three major agentic terminal tools — Gemini CLI, Claude Code, and Codex CLI — has a distinct sweet spot, and the right choice depends on your workflow, budget, and performance requirements. Gemini CLI wins on context window (1M tokens) and free tier (1,000 req/day at no cost), making it the clear choice for large-codebase analysis and cost-sensitive teams. Claude Code wins on code quality benchmarks, scoring 80.9% on SWE-bench Verified with 95% first-pass accuracy — measurably better for complex multi-file refactors where output correctness matters most. Codex CLI, rebuilt in Rust, achieves 77.3% on Terminal-Bench 2.0 and offers kernel-level sandboxing and the tightest MCP integration for security-sensitive environments. All three support MCP, all three implement ReAct-style agentic loops, and all three handle multi-step coding tasks autonomously. The differentiators are cost structure, context capacity, and benchmark accuracy on the specific task types you run most.

| Feature | Gemini CLI | Claude Code | Codex CLI |
|---|---|---|---|
| Context Window | 1M tokens | 200K tokens | 128K tokens |
| Free Tier | 1,000 req/day | No free tier | No free tier |
| SWE-bench Score | Not published | 80.9% | 77.3% (Terminal-Bench) |
| MCP Support | Yes (Stdio/SSE/HTTP) | Yes | Yes (kernel-level) |
| Plan Mode | Yes (March 2026) | Yes | Yes |
| Multi-Agent | Via ADK | Via Claude API | Via integrations |
| Best For | Large codebases, cost efficiency | Code quality, accuracy | Security-sensitive, performance |

### When to Use Each

Use Gemini CLI when you're analyzing a large codebase, want a free daily quota for experimentation, or need ADK-based multi-agent orchestration. Use Claude Code when output correctness on complex refactors or bug fixes is the priority. Use Codex CLI when operating in a sandboxed or security-restricted environment where kernel-level isolation matters. Many developers use Gemini CLI for exploration (leveraging the context window) and Claude Code for high-stakes changes (leveraging the accuracy benchmark).

## Security Best Practices: Env Variables, Sandboxing, and Audit Trails

Running an autonomous agent in your terminal introduces real security considerations — the agent has shell access, can read files, and can make network requests. The first line of defense is environment variable injection: never put API keys or credentials in the `args` array of `settings.json` (they appear in process listings); always use the `env` block with `${VAR_NAME}` expansion. The second is scope limitation: configure MCP filesystem servers with path restrictions, database servers with read-only credentials for exploration sessions, and network tools with domain allowlists. Gemini CLI's Plan Mode (added March 2026) provides a read-only phase where the agent proposes a plan before executing any file writes — enable it with `--plan-mode` or in `settings.json` as `"planMode": true`. For production systems, run Gemini CLI inside a container or VM rather than directly on your workstation, so the agent's shell access is bounded.

### settings.json Security Hardening

```json
{
  "planMode": true,
  "maxRetries": 3,
  "sandbox": {
    "enabled": true,
    "allowedPaths": ["/workspace", "/tmp"],
    "blockedCommands": ["rm -rf /", "sudo", "su"]
  },
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/workspace"],
      "env": {
        "READ_ONLY": "false"
      }
    },
    "database": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres"],
      "env": {
        "DATABASE_URL": "${DATABASE_READONLY_URL}"
      }
    }
  }
}
```

### Audit Logging

Enable session logging in `settings.json` with `"sessionLog": "~/.gemini/logs/"`. Each session creates a timestamped JSON file recording every tool call, argument, and result — useful for auditing what an agent did during an autonomous run, and essential for any team that needs traceability on AI-assisted code changes.

## Frequently Asked Questions

**Q: Is Gemini CLI free to use for serious development work?**
A: The free tier gives you 60 requests/minute and 1,000 requests/day with a personal Google account — enough for active development sessions. For CI pipelines, team use, or higher volume, set `GEMINI_API_KEY` to use your billed quota. Gemini 2.5 Pro API pricing as of 2026 is competitive with other frontier models at similar context sizes.

**Q: How do I debug an MCP server that shows as connected but whose tools fail?**
A: Run `gemini mcp test <server-name>` to invoke a test call and see the raw error. Check the server's stderr output (Stdio transport logs to `~/.gemini/logs/mcp-<name>.log` if session logging is enabled). Common causes: schema validation failure (missing `type` field in tool definition), environment variable not expanded (check `${VAR_NAME}` syntax), or the server process crashing silently.

**Q: Can I use Gemini CLI in CI/CD pipelines?**
A: Yes — set `GEMINI_API_KEY`, use `--non-interactive` mode to disable prompts, and pipe your task as stdin: `echo "run tests and report failures" | gemini --non-interactive`. For PR review automation, pair with an ADK agent that has a restricted GitHub MCP tool configured with a read-only token.

**Q: What's the difference between Plan Mode and the normal ReAct loop?**
A: In the standard ReAct loop, the agent can immediately execute file writes and shell commands as it reasons. Plan Mode adds a checkpoint: the agent runs a read-only exploration phase, proposes a written plan, waits for your approval, and only then proceeds to execute. Enable it per-session with `--plan-mode` or globally in `settings.json`. It significantly reduces unwanted side effects during exploratory tasks.

**Q: How does Gemini CLI handle secrets if my codebase contains them?**
A: Gemini CLI sends context to Google's API endpoints. Never load files containing production secrets, private keys, or credentials into the context window. Use `.geminiignore` to exclude `.env` files, key directories, and credential stores. For security-sensitive environments, prefer Codex CLI's kernel-level sandboxing or run Gemini CLI against a sanitized codebase copy rather than your live repository.
