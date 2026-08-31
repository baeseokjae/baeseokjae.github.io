---
title: "Portable Handoff: How to Keep Context Between AI Chats, Models, and Coding Agents"
date: 2026-08-31T10:01:58+00:00
tags: ["AI coding agents", "agent memory", "context portability", "CLAUDE.md", "AGENTS.md", "Claude Code", "developer productivity"]
description: "Keep agent context portable across AI chats, models, and coding agents with a single source-of-truth handoff file — symlinked and imported everywhere."
draft: false
cover:
    image: "/images/portable-handoff-agent-context.png"
    alt: "Portable Handoff: Keep Context Between AI Chats, Models, and Coding Agents"
    relative: false
schema: "schema-portable-handoff-agent-context"
---

# Portable Handoff: How to Keep Context Between AI Chats, Models, and Coding Agents

AI coding agents start every session with a fresh context window, so anything you do not persist is re-learned from scratch. A portable handoff file solves this: you write your instructions, preferences, and project conventions once, then symlink or import that single source of truth into every agent you use — Claude, Gemini, Cursor, or Codex — so context follows you across chats, models, and tools without drifting.

## Why AI agents forget everything between chats (the amnesia problem)

Every coding agent you use opens a new session with an empty memory of your project. As Hendrycks and colleagues note in their 2025 definition of AGI, "without continual learning, AI systems suffer amnesia, forcing re-learned context each interaction." A coding agent is no different: unless you give it persistent memory, it re-learns your build commands, code style, and conventions every time you start a chat.

In Claude Code specifically, every session begins with a fresh context window, and your remembered instructions are the only thing carried over by default. The cost of this amnesia is real. Developers lose minutes to hours re-explaining their setup, and small mistakes — the wrong package manager, the ignored test command, the forgotten lint rule — creep back in whenever context is not portable.

The root cause is not the model. It is that context has to be *transferred* rather than *recalled*. A portable handoff file is the mechanism for that transfer, and once it exists it becomes the single reference every agent loads on startup.

## The two memory systems in Claude Code — CLAUDE.md vs auto memory

Claude Code gives you two distinct ways to carry context across sessions, and it helps to keep them separate:

1. **CLAUDE.md (user-and-project-written memory).** This is the file you control. It is loaded at the start of every session and describes your conventions, preferences, and workflows. You write it once and update it deliberately.
2. **Auto memory (Claude-written notes).** Claude Code automatically writes compact notes about things it learns while working, and it consults these notes when it needs to recall preferences or prior context.

The two are managed differently. CLAUDE.md is your durable, human-edited source of truth, while auto memory is a living scratchpad the agent maintains. If context matters enough to be stable, it belongs in CLAUDE.md; if it is a transient detail the agent observed, it may live in auto memory.

Because CLAUDE.md files are concatenated into the context at the start of every session, they consume tokens alongside the conversation — which is why concise instructions produce more reliable agents than sprawling ones. Every directory you work in can contribute a CLAUDE.md, and the file is checked in the current working directory and every directory above it, with folders closer to where you launched loading last.

## Choose your source of truth: AGENTS.md, CLAUDE.md, or both

The single biggest source of agent amnesia drift is that different tools read different instruction files. Claude Code reads `CLAUDE.md`, while Cursor and the Codex CLI read `AGENTS.md`. Write your instructions only in `CLAUDE.md` and Cursor will never see them; write only in `AGENTS.md` and Claude Code may miss them unless configured.

The pragmatic answer is to pick **one source of truth** and route it everywhere. `AGENTS.md` is emerging as the cross-tool convention because it is read by multiple agents natively. Claude Code itself reads `AGENTS.md`, and its `/init` command can generate a `CLAUDE.md` that incorporates `AGENTS.md`, Copilot rules (`.github/copilot-instructions.md`), `.devin/rules/`, `.windsurf/rules/`, and `.clinerules`.

The decision matrix looks like this:

| Choice | Best for | Trade-off |
|---|---|---|
| `AGENTS.md` only | Multi-tool teams using Cursor, Codex, Copilot | Claude Code reads it but may need a compatibility note |
| `CLAUDE.md` only | Claude Code heavy users | Other tools will miss your instructions |
| `AGENTS.md` + symlinked `CLAUDE.md` | Everything reads one shared file | Symlink keeps both names pointing to a single inode |

For most teams, the winner is a single shared `AGENTS.md` as the canonical file, symlinked to `CLAUDE.md` so Claude Code sees it automatically and there is exactly one place to edit.

## Three ways to keep files in sync — symlink, @-import, or pointer file

Once you have a shared source of truth, you need to make every tool read it without copying content. There are three proven patterns:

**1. Unix symlink.** The cleanest solution. Because both names resolve to one file, the content can never drift:

```bash
ln -s AGENTS.md CLAUDE.md
```

Since both names point to the same inode, editing either updates both instantly. This is the DRY principle applied to agent memory.

**2. @-reference / import.** If you want a shared file plus tool-specific additions, use Claude Code's import syntax. A `CLAUDE.md` can pull in another file with `@path` syntax (up to four hops deep), letting you keep the shared content separate from Claude-specific instructions while still loading both.

**3. Pointer file.** Create a small `CLAUDE.md` whose entire purpose is to redirect the agent to the real source:

```text
READ AGENTS.md FIRST
```

Placed in ALL CAPS at the top, this tells Claude Code to find and follow the shared instructions file without duplicating it. It is the oldest and most compatible approach when symlinks are unavailable.

The principle mirrors code: one source of truth, routed everywhere. When you update project conventions, you update one file and every tool picks it up next session.

## A portable handoff workflow you can copy (write once, reuse everywhere)

Here is a concrete, copyable workflow that keeps context portable without adding daily maintenance:

**Step 1 — Create one canonical file.** Start with a single `AGENTS.md` at your project root. Include the essentials: how to build and test, your lint and style rules, the architecture map, and any commands you never want an agent to get wrong.

**Step 2 — Symlink it for Claude Code.**

```bash
ln -sf AGENTS.md CLAUDE.md
```

Now Claude Code, Cursor, and Codex CLI all load the same canonical instructions.

**Step 3 — Keep per-tool specifics minimal.** If a tool genuinely needs something different, add a thin layer on top rather than a second copy. For Claude-only notes, rely on `@`-references or a pointer file so you never maintain parallel duplicates.

**Step 4 — Export once, reuse everywhere.** Because the file is plain Markdown, the same handoff works across Claude, Gemini CLI, Cursor, and Codex. Write the context once; every agent loads it on startup.

**Step 5 — Review on a schedule.** Agent memory files rot just like documentation. Treat `AGENTS.md` as living code — update it when conventions change, and prune dead instructions to keep token usage low.

## Keep personal rules private with CLAUDE.local.md

Not everything belongs in a shared, committed file. Personal preferences — your editor keybindings, your preferred branch strategy, one-off formatting tastes — should stay out of `AGENTS.md` and live in `CLAUDE.local.md`, which is gitignored by default.

The hierarchy works by scope:

| Scope | File | Committed? |
|---|---|---|
| Organization | `/etc/claude-code/CLAUDE.md` | No |
| User | `~/.claude/CLAUDE.md` | No |
| Project (shared) | `./AGENTS.md` → `./CLAUDE.md` | Yes |
| Local (personal) | `CLAUDE.local.md` | No (gitignored) |

The rule is simple: shared truth goes in the committed project file; personal truth goes in the gitignored local file. That keeps a portable, reviewable source of truth while still letting each engineer work the way they like.

## Make the handoff survive a long session (/compact, auto memory)

Even with a perfect handoff file, a single conversation can outgrow its context window. Two Claude Code features keep context stable during long sessions:

- **`/compact`** summarizes the conversation when context runs low, distilling what has been discussed into a tighter form so work can continue without losing the thread.
- **Auto memory** keeps Claude-written notes about your preferences and prior context, so even mid-session the agent can consult what it has learned rather than re-asking.

Because `CLAUDE.md` is loaded at session start and consumes tokens alongside the conversation, keeping it concise directly improves reliability over long sessions — every unnecessary line competes with the actual conversation for the context window.

## Portability across models and tools (Gemini CLI, Cursor, Codex)

The whole point of a portable handoff is that it is not locked to one vendor. Because your handoff file is plain Markdown, the same `AGENTS.md` loads in Claude Code, Cursor, the Codex CLI, and, with the right plugin or import step, Gemini CLI and other models.

This cross-model portability is becoming its own product category, which is a strong signal of demand. Tools exist specifically to sync and port agent memory files across agents, and plugins can export context once and reuse it in another agent. The pattern behind all of them is identical: define context in a neutral, portable form, then let each tool read that same form.

For a development team, the payoff is that an engineer can switch models — or a team can standardize on one — without anyone re-explaining the project. The handoff file travels with the code.

## Pitfalls to avoid (drift, contradictions, oversized memory files)

Portable handoff works only if the file stays trustworthy. Watch for these three failure modes:

1. **Drift.** The classic killer: instructions written to `CLAUDE.md` and `AGENTS.md` as separate copies, then updated in only one place. Fix it permanently with a symlink or `@`-reference so there is never a second copy to forget.
2. **Contradictions.** Two files saying different things about the same workflow confuse agents and produce inconsistent behavior. A single source of truth eliminates the conflict at the root.
3. **Oversized memory files.** Every line of `CLAUDE.md` consumes tokens at every session start. Bloated instruction files degrade reliability across all tools. Keep only what is durable and prune the rest.

Treat your agent memory files like any other code: version them, review them, and keep them DRY.

## FAQ

**What is a portable handoff file for AI agents?**
A portable handoff file — typically `AGENTS.md` or `CLAUDE.md` — is a plain-text document that carries your project instructions, preferences, and conventions from one AI session to the next, and across different AI tools and models, so context does not have to be re-explained every time.

**Why do AI coding agents forget context between chats?**
Coding agents open each session with a fresh context window and, without persistent memory, must re-learn your setup from scratch every time — the "amnesia" problem. A handoff file loaded at session start is the fix.

**Should I use AGENTS.md or CLAUDE.md?**
Use a single `AGENTS.md` as your canonical source of truth because it is the cross-tool convention read by Cursor and Codex, then symlink it to `CLAUDE.md` so Claude Code reads the same file. Pick one file and route it everywhere.

**How do I keep AGENTS.md and CLAUDE.md in sync?**
The most reliable way is a symlink (`ln -s AGENTS.md CLAUDE.md`), so both names resolve to one file and can never drift. Alternatives are an `@`-reference/import or a pointer file that redirects the agent to the shared source.

**Does portable context work across different AI models?**
Yes. Because a handoff file is plain Markdown, the same file loads in Claude Code, Gemini CLI, Cursor, and the Codex CLI, with the right import step. Cross-model context portability is an active product category precisely because developers want one handoff that follows them everywhere.
