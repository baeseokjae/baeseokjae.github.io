---
cover:
  alt: 'JetBrains ACP Agent Registry: Connect AI Agents to Your IDE'
  image: /images/jetbrains-acp-agent-registry-guide-2026.png
  relative: false
date: 2026-06-02 18:51:42+00:00
description: Learn how to use the JetBrains ACP Agent Registry to install Claude Code,
  Cursor, Gemini CLI and more directly into your IDE with one click.
draft: false
schema: schema-jetbrains-acp-agent-registry-guide-2026
tags:
- JetBrains
- AI Agents
- ACP
- IntelliJ IDEA
- Developer Tools
title: 'JetBrains ACP Agent Registry: Connect AI Agents to Your IDE (2026 Guide)'
---

The JetBrains ACP Agent Registry is a curated, one-click marketplace for AI coding agents inside IntelliJ IDEA, PyCharm, WebStorm, and other JetBrains IDEs. Launched January 28, 2026, it lets you install Claude Code, Cursor, Gemini CLI, and 30+ other agents in seconds — no manual JSON editing required.

## What Is the JetBrains ACP Agent Registry?

The JetBrains ACP Agent Registry is the world's first open, cross-editor AI agent marketplace, jointly built by JetBrains and Zed Industries and launched on January 28, 2026. It solves a problem that frustrated developers for years: every AI coding agent had its own proprietary installation process — download a binary, edit JSON config files, restart the IDE, repeat. The registry replaces that friction with a browser-like "one-click install" for any ACP-compatible agent directly inside IntelliJ IDEA, PyCharm, WebStorm, GoLand, and other JetBrains IDEs running version 2025.3 or later. As of mid-2026, the registry lists 30+ agents including Claude Code, Cursor, Gemini CLI, GitHub Copilot, OpenHands, Kimi CLI, Goose, Cline, and Koog (JetBrains' own Junie agent). The registry is open — any developer or company can submit an ACP-compatible agent for inclusion. Both JetBrains and Zed share the same backend registry, meaning an agent listed there works in both editors without duplication.

The registry matters because of the scale of developer adoption. A January 2026 JetBrains survey of 11,000 developers found that 90% now use AI at work, 22% already use AI coding agents, and 66% of companies plan to adopt agents within 12 months. The registry is how JetBrains intends to capture that transition — not by locking users into Junie, but by becoming the neutral platform where any agent can run.

## What Is ACP (Agent Client Protocol)?

ACP, or Agent Client Protocol, is an open standard that defines how an AI coding agent communicates with a host IDE or editor — think of it as the Language Server Protocol (LSP) moment for AI agents. Just as LSP (introduced with VS Code in 2016) let any language server plug into any editor without custom glue code, ACP lets any AI agent integrate with any ACP-supporting editor without proprietary adapters. The protocol handles bidirectional communication: the editor sends the agent context (open files, cursor position, selected code, project structure), and the agent returns actions (inline edits, shell commands, file creation) through a standardized message format. An `acp.json` manifest file describes how to start the agent process, what capabilities it exposes, and what MCP tools it can proxy through.

The "LSP for AI agents" analogy is precise. Before LSP, each language server (Go, Rust, Python) had to write custom integrations for VS Code, Vim, Emacs, and JetBrains separately — multiplying maintenance cost by the number of editors. Before ACP, the same problem plagued AI agents: Claude Code had an IntelliJ plugin, Cursor had its own editor, Copilot had its own extensions. ACP breaks that matrix. The protocol was developed with Zed as the reference implementation and JetBrains as the first major partner, giving it immediate reach to tens of millions of developers.

## How to Install Agents from the Registry (Step-by-Step)

Installing an AI agent from the JetBrains ACP registry takes under two minutes once your IDE is updated to version 2025.3 or later. The process works identically across IntelliJ IDEA, PyCharm, WebStorm, GoLand, and all other JetBrains IDEs — open **Settings → Tools → AI Agents → Registry**, browse the list of 30+ available agents, click **Install**, enter any required API keys, and you're running. There is no manual JSON editing, no binary path configuration, and no restart required. The registry automatically downloads the agent's `acp.json` manifest, wires it into the ACP runtime, and adds the agent to the AI panel dropdown. If an agent requires an external binary (like the `claude` CLI for Claude Code or the `cursor` binary for Cursor), the IDE surfaces a clear error message pointing you to the installation page — it does not silently fail. The end-to-end flow from "open registry" to "first agent response" reliably takes 90 seconds for agents with pre-installed binaries.

### Prerequisites

Installing via the ACP registry requires JetBrains IDE version 2025.3 or later. Open your IDE, go to **Help → Check for Updates**, and upgrade if needed. You also need a working installation of the agent itself on your system — for example, the `claude` CLI for Claude Code or `cursor` for Cursor. The registry handles the IDE connection, not the agent binary.

### Step 1: Open the ACP Registry Panel

In IntelliJ IDEA (or any JetBrains IDE), go to **Settings → Tools → AI Agents** (or press `Ctrl+Shift+A` and search "AI Agents"). You'll see a **Registry** tab alongside **Installed** and **Configure**. Click **Registry**.

### Step 2: Browse and Select an Agent

The registry panel shows all available agents with name, description, and compatibility badge. Use the search bar to find a specific agent. Each entry shows the agent's ACP version, supported languages, and whether it requires an external binary or API key.

### Step 3: One-Click Install

Click **Install** next to your chosen agent. The IDE downloads the `acp.json` manifest, validates it, and wires the agent into the ACP runtime. No manual file editing. For agents requiring an API key (Claude Code needs `ANTHROPIC_API_KEY`, Gemini CLI needs `GEMINI_API_KEY`), a credential dialog appears automatically.

### Step 4: Switch Agents in the AI Panel

After installation, open the **AI** panel (right sidebar or `Alt+Shift+A`). A dropdown at the top lets you switch between installed agents mid-session. You can run Claude Code for a complex refactor, then switch to Gemini CLI for a quick explanation — same project, no restart.

## Top Agents Available in the ACP Registry

The registry is open and growing, but these are the agents that practitioners are actually using in 2026:

| Agent | Strengths | API/Binary Required | Best For |
|---|---|---|---|
| Claude Code | Deep reasoning, long context, tool use | `claude` CLI + Anthropic API key | Complex refactoring, multi-file edits |
| Cursor | Code generation, autocomplete quality | `cursor` binary | Fast inline completions |
| Gemini CLI | Google ecosystem, free tier | `gemini` CLI + Google API key | Polyglot projects, research tasks |
| GitHub Copilot | GitHub integration, chat | GitHub account | GitHub-heavy teams |
| Koog (Junie) | JetBrains-native context, no extra binary | Built-in with AI Assistant | Teams already paying for AI Assistant |
| OpenHands | Open source, self-hostable | Docker | On-prem, privacy-sensitive orgs |
| Cline | MCP-first, extensible toolset | `cline` CLI | Teams with custom MCP servers |
| Goose | Block-coded, auditable steps | `goose` CLI | Process-heavy enterprise workflows |

**Claude Code** is the most capable for complex multi-file reasoning but requires an Anthropic API subscription. **Koog** is the lowest-friction starting point if you already have JetBrains AI Assistant — it runs natively with no extra binary. **OpenHands** is the only self-hostable option, making it the clear choice for air-gapped or compliance-constrained environments.

## How to Configure a Custom Agent via acp.json

For teams building internal agents — proprietary code review bots, domain-specific assistants, or agents that talk to internal APIs — the registry offers direct `acp.json` configuration without requiring a public listing.

An `acp.json` file is the agent's manifest. It lives alongside the agent's binary or startup script and tells the IDE how to launch the agent, what protocol version it speaks, and what capabilities it exposes:

```json
{
  "acp_version": "1.2",
  "name": "my-internal-agent",
  "display_name": "Acme Code Agent",
  "start_command": ["./acme-agent", "--port", "{{acp_port}}"],
  "capabilities": ["inline_edit", "chat", "command"],
  "mcp_servers": [
    {
      "name": "acme-tools",
      "url": "http://localhost:8080/mcp"
    }
  ],
  "env": {
    "ACME_API_URL": "${ACME_API_URL}"
  }
}
```

In JetBrains settings, go to **AI Agents → Configure → Add Custom Agent** and point to the `acp.json` file path. The IDE validates the manifest and surfaces any missing fields. The `{{acp_port}}` placeholder is resolved at runtime — the IDE picks a free port and injects it before starting the agent process.

The `mcp_servers` field is especially powerful for internal teams. List any MCP-compatible tool server, and the agent can call those tools as if they were native capabilities. An Acme-specific Jira server, a database query tool, or a documentation search server all become available inside IntelliJ with no additional integration work.

## ACP and MCP: How the Two Protocols Work Together

ACP and MCP (Model Context Protocol, from Anthropic) are complementary layers in the agentic IDE stack — not competing standards, despite the naming confusion. ACP answers the question "where does the agent live and how does it talk to the editor?" MCP answers "what external tools can the agent use?" Every serious agentic setup in 2026 uses both.

Here is how they stack:

```
┌─────────────────────────────────────┐
│           JetBrains IDE             │
│  ┌───────────────────────────────┐  │
│  │       ACP Runtime             │  │
│  │  (agent ↔ editor protocol)    │  │
│  └────────────────┬──────────────┘  │
│                   │ ACP messages     │
└───────────────────┼─────────────────┘
                    │
          ┌─────────▼──────────┐
          │   AI Agent Process │
          │  (Claude Code etc) │
          └─────────┬──────────┘
                    │ MCP calls
          ┌─────────▼──────────┐
          │   MCP Tool Servers │
          │  (IntelliJ MCP,    │
          │  Jira, DB, Files)  │
          └────────────────────┘
```

JetBrains ships an **IntelliJ MCP server** built-in. It exposes IDE operations — open file, run tests, get compiler errors, search symbols — as MCP tools. When an ACP agent runs inside the IDE, it automatically gets access to the IntelliJ MCP server, giving it a rich understanding of the project that goes beyond file content alone. Claude Code, for example, can call `run_tests` via MCP and see the failure output before writing a fix — a workflow impossible with file-only context.

The practical implication: ACP is the outer connector (IDE → agent), MCP is the inner tool system (agent → tools). VS Code lacks native ACP support as of mid-2026, which means VS Code extension-based agents cannot participate in this bidirectional protocol — they operate purely through extension APIs rather than the standardized ACP message stream.

## JetBrains Central — The Bigger Agentic Platform

The ACP registry is the on-ramp to a larger initiative: JetBrains Central. Announced in March 2026 and available as an Early Access Program with limited design partners, JetBrains Central is described as an "open system for agentic software development" — a control plane that orchestrates multiple agents across a development lifecycle, not just a single coding session. Think of it as the agent equivalent of a CI/CD pipeline: Central can assign tasks to specific agents, route outputs between them, enforce approval gates, and log decisions for auditing. It is built on ACP as the communication standard, which means any agent in the registry can become part of a Central-orchestrated workflow without modification. Early adopters report using Central to run a Cline agent for scaffolding, pass the output to Claude Code for refinement, and route the result through a custom review agent before creating a pull request — all triggered by a single natural-language specification.

JetBrains positions Central as the answer to the question "what happens after the agent writes the code?" The registry handles agent installation; Central handles agent orchestration. Together, they form what JetBrains calls the agentic IDE stack — a full-cycle system from code generation to deployment.

## Conclusion: Is the ACP Registry Worth Your Attention?

For any developer using a JetBrains IDE who is serious about AI-assisted development, the ACP registry is the most impactful upgrade available in 2026 — and it costs nothing to try. The registry launched January 28, 2026, and within five months grew to 30+ agents with more submitted weekly. The one-click setup removes the main adoption barrier, the open registry ensures you're never locked to JetBrains' own agent, and the ACP + MCP stack gives agents richer IDE context than any extension-based approach. The JetBrains survey data makes the urgency clear: 66% of companies plan to adopt AI coding agents within 12 months, and the developers who are already proficient with agentic workflows will have a significant productivity advantage. The ACP registry is the lowest-friction on-ramp to that proficiency. The practical starting point: upgrade to JetBrains 2025.3+, install one agent from the registry (Koog if you already have AI Assistant, Claude Code otherwise), and run it against a real task for 30 minutes. That hands-on session will reveal more than any benchmark or review article. The investment is a single afternoon; the compounding benefit is months of faster development.

---

## FAQ

The following questions cover the most common points of confusion about the JetBrains ACP Agent Registry — from version requirements and pricing to how ACP differs from MCP and whether you can build your own agent. These answers are written to be self-contained so you can jump directly to the question relevant to your situation without reading the full guide above. If your question isn't covered here, the official documentation at jetbrains.com/help/ai-assistant/acp.html and the protocol spec at agentclientprotocol.com are the authoritative sources. JetBrains also maintains an active community forum where registry submission questions are answered by the ACP team directly — typically within one to two business days. Registry additions happen on a rolling basis, so if an agent you want is not yet listed, checking back every few weeks is worthwhile as new submissions are approved continuously.

### What IDEs support the ACP Agent Registry?

The ACP Agent Registry is available in all JetBrains IDEs running version 2025.3 or later, including IntelliJ IDEA, PyCharm, WebStorm, GoLand, Rider, CLion, DataGrip, and Android Studio. Upgrade through **Help → Check for Updates** to access the registry panel under **Settings → Tools → AI Agents**.

### Is the ACP registry free to use?

The ACP registry itself is free — there is no charge to browse or install agents from it. However, individual agents may have their own pricing. Claude Code requires an Anthropic API key (pay-per-token), Gemini CLI has a free tier and paid tier, GitHub Copilot requires a Copilot subscription, and Koog requires a JetBrains AI Assistant subscription. OpenHands is fully open source.

### How is ACP different from MCP?

ACP (Agent Client Protocol) governs how an AI agent communicates with the host IDE — file context, cursor position, inline edits. MCP (Model Context Protocol) governs how an agent communicates with external tools — running tests, querying a database, calling an API. In a typical setup, the IDE talks to the agent via ACP, and the agent talks to tools via MCP. They operate at different layers and are designed to be used together.

### Can I build and submit my own agent to the ACP registry?

Yes. The registry is open. You need to implement the ACP protocol in your agent (the spec is at agentclientprotocol.com), create a valid `acp.json` manifest, and submit a pull request to the registry repository. JetBrains and Zed review submissions for protocol compliance before listing. There is no exclusivity requirement — you can list the same agent in both the JetBrains and Zed registries.

### Does the ACP registry work with VS Code?

Not natively. VS Code does not have built-in ACP support as of mid-2026. VS Code-based agents (Copilot Chat, Cline for VS Code) use VS Code's extension API rather than ACP, which means they don't participate in the standardized ACP message stream. Developers who need both VS Code and ACP-based workflows typically run their JetBrains IDE for the ACP-heavy tasks and VS Code separately — there is no cross-editor ACP bridge currently available.