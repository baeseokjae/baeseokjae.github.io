---
title: "Agent Shell Emacs 2026: Vendor-Neutral Chat with AI Agents from Emacs"
date: 2026-09-04T01:01:32+00:00
tags:
  - emacs
  - ai agent
  - agent client protocol
  - agent-shell
  - acp.el
  - claude code
  - codex
  - gemini cli
description: "agent-shell turns Emacs into a vendor-neutral AI agent shell via ACP. Install from MELPA, connect Claude, Codex, Gemini, or Goose, and chat from one buffer."
draft: false
cover:
    image: "/images/agent-shell-emacs-ai-agents-2026.png"
    alt: "Agent Shell Emacs 2026: Vendor-Neutral Chat with AI Agents from Emacs"
    relative: false
schema: "schema-agent-shell-emacs-ai-agents-2026"
---

agent-shell is a native Emacs shell that lets you talk to any AI coding agent from a single buffer, powered by ACP (Agent Client Protocol) rather than any single vendor. It supports 18+ agents including Claude Agent, Codex, Gemini CLI, Goose, and Grok Build, and by September 2026 it has grown to roughly 1,824 GitHub stars. You install it from MELPA, configure authentication with environment variables, and switch agents without leaving Emacs.

## What is agent-shell and why vendor-neutral AI agents matter

agent-shell is an Emacs Lisp package that provides a native shell for interacting with LLM-powered coding agents. Unlike a terminal wrapper or a web chat, it is built on `comint-mode`, the same foundation as `M-x shell` and `M-x term`, so you never dance between character and line modes. You type a prompt, the agent streams its response, and the whole conversation lives in a normal Emacs buffer you can search, kill, and yank.

The reason this matters in 2026 is vendor neutrality. The AI agent landscape is fragmented: Claude Code, OpenAI Codex, Google Gemini CLI, Goose, Grok Build, Cursor, Qwen Code, and a dozen more all speak slightly different dialects. Historically, integrating each one meant writing bespoke glue code, fighting incompatible APIs, and locking yourself into whichever vendor you picked first. agent-shell sidesteps all of that by speaking one protocol — ACP — so the agent is a pluggable detail rather than the center of your workflow.

## Understanding ACP (Agent Client Protocol) — the LSP moment for AI agents

ACP, the Agent Client Protocol, standardizes communication between code editors and coding agents. It is developed between Zed and Google, and it is deliberately analogous to LSP, which standardized language-server integration a decade ago. Just as LSP let one editor work with any language server, ACP lets one editor — or one Emacs buffer — work with any coding agent.

The protocol solves three concrete problems:

- **Integration overhead**: instead of N editors times M agents of bespoke glue, you write one ACP client and it works with every ACP-compliant agent.
- **Limited compatibility**: agents that only speak their own proprietary protocol become usable from any ACP client.
- **Developer lock-in**: you are no longer married to a single vendor's tooling; swap agents as easily as you swap language servers.

Under the hood, local agents run as sub-processes communicating via JSON-RPC over stdio, while remote agents use HTTP or WebSocket (still in progress). ACP v1 is stable and v2 is in draft, with official libraries in Kotlin, Java, Python, Rust, and TypeScript. agent-shell is built on `acp.el`, an Emacs Lisp implementation of ACP developed between Zed and Google, so the whole stack is native to Emacs.

## Installing agent-shell in Emacs (MELPA, use-package, Doom Emacs)

agent-shell and its dependency `acp.el` are both available on MELPA, so installation is a one-liner with `use-package`:

```elisp
(use-package agent-shell
  :ensure t)
```

This pulls in `acp.el` and `shell-maker` automatically. If you use Doom Emacs, add `agent-shell` to your `packages.el` and run `doom sync`:

```elisp
(package! agent-shell)
```

After installation, start a session with `M-x agent-shell`. The first time you run it, agent-shell offers shell prompts as soon as possible so you can start typing during init rather than waiting for the agent to finish booting. If you prefer a specific agent to be preselected, set `agent-shell-preferred-agent-config` to skip the picker entirely.

## Configuring authentication and environment variables

Most agents authenticate through environment variables rather than interactive login prompts. The exact variable depends on the agent, but the pattern is consistent: export the key in your shell environment before launching Emacs, and agent-shell passes it through to the agent sub-process.

For example, Claude Agent reads `ANTHROPIC_API_KEY`, OpenAI Codex reads `OPENAI_API_KEY`, and Google Gemini CLI reads `GOOGLE_API_KEY` (or uses `gcloud` application-default credentials). Goose no longer requires an OpenAI key by default, which makes it a convenient first agent to try. The safest approach is to add the relevant exports to your `~/.bashrc` or `~/.zshrc` and launch Emacs from a shell that has them set, so you never hard-code secrets into your Emacs config.

## Connecting your first agent (Claude Agent, Codex, Gemini CLI, Goose)

Once authentication is configured, connecting an agent is a matter of selecting it from the picker or configuring it explicitly. agent-shell uses `acp-make-client` to define each agent, and the configuration is uniform across vendors. Here is a representative example adapted from the project's documentation:

```elisp
(require 'agent-shell)

(setq agent-shell-preferred-agent-config
      '((:name "Claude Agent"
         :client (acp-make-client
                  :command "claude"
                  :args '("--print" "--output-format" "stream-json")))))
```

The same shape works for Codex, Gemini CLI, and Goose — you change the command and arguments, not the integration layer. Because every agent speaks ACP, the Emacs-side code is identical; only the sub-process command differs. This is the practical payoff of vendor neutrality: learning one agent's configuration teaches you all of them.

## Switching between 18+ agents from one buffer

agent-shell supports 18+ ACP-driven agents, including Claude Agent, Codex, Gemini CLI, Goose, Grok Build, Cursor, Kimi Code CLI, CodeBuddy, Kiro CLI, Qwen Code, Auggie, Mistral Vibe, Factory Droid, Pi, Oh My Pi, Opencode, and Antigravity. Recent releases have also added Oh My Pi (omp) and Grok Build (xAI), and moved Cursor onto its official Cursor CLI.

Switching between them is a first-class operation. You can start a new session with a different agent, or use `agent-shell-preferred-agent-config` to preselect one and skip the picker. Because the conversation format is standardized by ACP, you can run the same prompt against Claude, Codex, and Gemini in separate buffers and compare the results side by side — something that is painful with vendor-specific tools.

## Chat mode, activity grouping, and prompt queueing in 2026

The 0.73 release marked a turning point: agent-shell entered the chat. Chat mode fuses comint with traditional chat-like labelling and is enabled by default. If you prefer the classic shell feel, disable it with `(setq agent-shell-chat-mode-enabled nil)`.

Two other 2026 features make long agent sessions manageable:

- **Activity grouping**: tool calls and thinking are collapsed by default so the buffer stays readable. Expand them with `agent-shell-activity-group-expand-by-default`, or set it to `'latest` to expand only the most recent group.
- **Prompt queueing**: consolidated under `agent-shell-prompt-queue.el`, you can queue, resume, and remove prompts. This is invaluable when you want to fire several prompts at an agent and let it work through them in order.

## Composing prompts from anywhere and TAB navigation

`M-x agent-shell-prompt-compose` lets you craft a prompt from any buffer, not just the agent shell. This is a huge workflow win: you can be editing a file, select a region, and compose a prompt that references it without copying text around. `C-c C-c` sends the prompt fire-and-forget, while `C-u C-c C-c` queues another one.

Markdown rendering also got smarter. Lists get normalized padding and indentation, and TAB navigation works across source blocks, links, and images, with hints shown as you move. If you want custom rendering, `agent-shell-markdown-render-functions` lets you plug in your own renderers — for example, `agent-shell-math-renderer` renders LaTeX as SVG directly in the buffer.

## Going local-first with Opencode and Ollama

One of the most compelling 2026 use cases is fully local AI. Because agent-shell is agent-agnostic, you can pair Opencode with a local Ollama model such as Qwen2.5:7b and run an entire agent workflow without sending a single prompt to a cloud API. This matters for privacy-sensitive work, air-gapped environments, and anyone who wants to avoid per-token costs.

The setup is the same as any other agent: configure Opencode as an ACP client, point it at your local Ollama endpoint, and start a session. The traffic stays on your machine, and you get the full agent-shell experience — chat mode, activity grouping, prompt queueing — over a local model. It is a reminder that vendor neutrality is not just about choosing between cloud vendors; it is about choosing whether to use a cloud at all.

## Extending agent-shell with the companion ecosystem

agent-shell has grown a rich ecosystem of companion packages that extend it far beyond a bare shell:

- **emacs-skills** — give agents reusable skills
- **agent-shell-sidebar** — a persistent sidebar for agent state
- **agent-shell-bookmark** — bookmark agent conversations
- **agent-shell-workspace** and **agent-shell-manager** — manage multiple workspaces and sessions
- **agent-review** — review agent output
- **ob-agent-shell** — run agents from Org Babel blocks
- **agent-shell-tramp** — use agents over TRAMP for remote files
- **agent-shell-dashboard** and **agent-shell-hq** — dashboards and higher-level orchestration

There are also image utilities for clipboard paste (`pngpaste`, `wl-paste`, `xclip`) and per-platform screenshots, so you can feed images to multimodal agents directly from Emacs. The ecosystem is a strong signal that agent-shell is not a toy but a platform.

## Troubleshooting and tips

- **Agent won't start**: check that the agent binary is on your `PATH` and that the relevant API key is exported in the environment Emacs was launched from.
- **No traffic visible**: run `M-x agent-shell-view-traffic` to inspect the raw ACP JSON traffic between Emacs and the agent. This is the fastest way to see what is actually being sent.
- **Testing without cost**: agent-shell can save traffic to disk and replay it as a fake agent, giving you cheap, fast, deterministic tests without burning tokens.
- **Too much chatter**: enable activity grouping or set `agent-shell-activity-group-expand-by-default` to `'latest` to collapse tool calls and thinking.
- **Theming**: use `agent-shell-faces.el` to control faces and match your theme.

## FAQ

**What is agent-shell for Emacs?**
agent-shell is a native Emacs shell, built on comint-mode, for interacting with AI coding agents. It is powered by ACP (Agent Client Protocol) and supports 18+ agents from a single buffer.

**Is agent-shell vendor-neutral?**
Yes. Because it speaks ACP rather than any single vendor's protocol, you can use Claude Agent, Codex, Gemini CLI, Goose, Grok Build, and many others interchangeably from the same Emacs interface.

**How do I install agent-shell?**
Install it from MELPA with `(use-package agent-shell :ensure t)`. It depends on `acp.el` and `shell-maker`, which are pulled in automatically. Doom Emacs users add `(package! agent-shell)` and run `doom sync`.

**Which agents does agent-shell support?**
It supports 18+ ACP-driven agents, including Claude Agent, Codex, Gemini CLI, Goose, Grok Build, Cursor, Qwen Code, Mistral Vibe, Opencode, and Antigravity, with new agents added regularly.

**Can I run agent-shell with a local model?**
Yes. Pair Opencode with a local Ollama model such as Qwen2.5:7b to run a fully local, privacy-friendly agent workflow entirely from Emacs without cloud API calls.
