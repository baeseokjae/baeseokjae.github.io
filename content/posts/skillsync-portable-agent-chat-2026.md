---
title: "Skillsync Review 2026: Portable Agent Chat Sessions Across Coding Agents"
date: 2026-09-29T04:18:56+00:00
tags:
  - skillsync portable agent chat sessions
  - move AI chat sessions between coding agents
  - continue Claude Code session in Codex
  - txcript agent transcript converter
  - cross-harness session portability
  - portable agent session format
  - resume session in another agent
  - agent session handoff
  - skillsync vs continuo
  - skillsync review 2026
  - skillsync pricing free vs pro teams
  - local-first agent session search
  - claude code codex cursor session migration
  - MCP session search server
  - how to switch coding agents without losing context
  - agent context lock-in 2026
  - skillsync YC W26
  - export agent session to JSON
  - coding agent transcript translation
  - agent handoff debt token cost
description: "Skillsync moves a full AI chat session between coding agents with no summarizer rewriting it. How txcript works, what drops, and what it costs."
draft: false
cover:
    image: "/images/skillsync-portable-agent-chat-2026.png"
    alt: "Skillsync Review 2026: Portable Agent Chat Sessions Across Coding Agents"
    relative: false
schema: "schema-skillsync-portable-agent-chat-2026"
---

Skillsync portable agent chat sessions work by deterministic translation, not summarization: it reads a session transcript from one coding agent, converts it into the target agent's native format, and opens it so you continue where you left off. Tool calls and reasoning traces ride along. It is a YC W26 product built on an open-source Rust engine, txcript.

## What does Skillsync actually do (and what is it not)?

Skillsync is a macOS desktop app plus a CLI (`skl`) plus an MCP server. Its one-line pitch, as listed on the [Y Combinator company page](https://www.ycombinator.com/companies/skillsync), is "Notion for AI chats" — a searchable, portable store of every session you have ever run, across every harness you use. The marketing page frames it as: "Your AI sessions made portable across every agent and teammate."

Concretely, it does three things:

- **Resume** a session on a local coding agent, or move it to a different one mid-stream.
- **Search** every past session locally as portable context.
- **Share** sessions, skills and memory with teammates through a workspace layer.

What it is *not* is equally important. It is not an orchestration layer, not a multi-agent runtime, and not an agent router. It does not run your session in the cloud and hand you a terminal. It is a translation and retrieval layer sitting on top of the agents you already use — described by a third-party analyst at [metadatamarketer.com](https://metadatamarketer.com/skillsync-review-tool/) as "ffmpeg or pandoc for agent sessions."

That analogy is the right lens. Pandoc does not write your document; it converts the format so the document survives a move. Skillsync's claim is the same, one level up.

## How does deterministic conversion differ from asking an agent to write a summary?

This is the single most important architectural fact about Skillsync, and it came straight from the founder during the [Launch HN thread](https://news.ycombinator.com/item?id=49743049) on 2026-09-17:

> "there's no ai here. Everything is retained including tool calls, reasoning and handed off to the other agent"

That matters because the obvious alternative — tell your agent to keep a work journal in markdown — is a *generative* handoff. A journal is produced from a prompt, so anything the prompt did not ask about is gone. A commenter in the same thread (pjm331) made exactly this critique, and the founder conceded the framing while defending the mechanism: "Porting is cheap, since it's just a format conversion. Getting a new session back up to speed from notes usually isn't."

Here is the distinction in table form:

| Dimension | Markdown work journal | Deterministic transcript port |
|---|---|---|
| What survives | Only what the prompt asked for | Every record: messages, tool calls, reasoning, lineage |
| Failure mode | Silent omission you cannot detect | Explicit loss of records the destination cannot represent |
| Audit trail | Reconstructed narrative | Primary evidence, byte-preserved where supported |
| Cost model | Tokens to summarize | CPU to translate |
| Reproducibility | Prompt-dependent | Same input, same output |

For an individual developer, the journal often wins on effort. For anything you need to defend later — an incident fix, a compliance review, a handoff to a colleague who has to trust the change — the difference between a narrative and the actual transcript is the whole game.

## What is txcript, the engine underneath?

txcript is the [open-source core](https://github.com/skillsynchq/txcript) — a Rust library, CLI and WASM build that converts session transcripts between harnesses, licensed Apache-2.0. As of 2026-09-29 the repository shows 142 stars, 12 forks, 8 contributors and 23 open issues, created 2026-06-25 and pushed the same day as this review. Distribution is real but early: 647 all-time crates.io downloads (v0.14.4 latest, first published 2026-07-01) and 2,275 npm downloads in the last 30 days, of which 643 came in the last 7 days.

The adapter split is where the review gets honest:

| Adapter capability | Harnesses |
|---|---|
| Read **and** continue | Claude Code, Codex, OpenCode, Cursor CLI, Cursor desktop, pi, Campfire, Cowork, Grok CLI, fx, Antigravity |
| Read only | Hermes Agent, Amp |
| Live-account sources (read only) | Claude Chat, ChatGPT, Cloud Cowork |

Eleven of the seventeen adapters can hand a session back with full continuation. Hermes Agent — the runtime this blog's automation runs on — is read-only, which means you can bring a Hermes session into Claude Code but not the reverse. That is a concrete limitation worth knowing before you build a workflow around it.

There is also a neutral "Simple" interchange JSON that any unadapted agent can consume, and `txcript export` writes it. That is the escape hatch: even if your harness has no adapter, you can hand it a documented JSON shape rather than a screenshot of a chat.

The CLI surface a review can actually walk through: `list`, `query`, `view`, `crop`, `export`, `continue`, `resume`, plus `txcript mcp`, which exposes read-only tools to any MCP client. Rust 1.96+ is required to build from source; prebuilt binaries cover macOS, Linux and Windows.

## Why did session portability become a real problem in 2026?

Because developers stopped using one agent. The [Developer Ecosystem Survey 2026](https://blog.jetbrains.com/research/2026/08/ai-coding-agent-adoption-2026/), covering 15,000+ professional developers, found that 90% used AI coding agents at work at least weekly between May and July 2026, and 68% used them daily.

The same data shows the market fragmenting rather than consolidating:

- Claude Code reached roughly 39% adoption at work, up from 18% in January 2026 (47% in the US).
- Codex grew about 5x to 16%.
- GitHub Copilot fell to 21%.
- Cursor slipped to 12%.
- OpenCode reached 7%.

When four or five agents each hold double-digit share, the practical reality is that one developer runs two or three side by side and picks per task. That choice becomes expensive the moment a session is not portable, because the context you accumulated is locked to the harness that produced it. Choosing an agent early stops being a preference and becomes a bet.

The cost of *not* porting is now measurable. A study on "Handoff Debt" ([arXiv:2606.02875](https://arxiv.org/abs/2606.02875), KC & Budathoki, v2 2026-08-30) measured 181 handoff-point tasks with 724 takeover runs per successor model, and found that context-bearing handoffs cut median agent events by **20–59%** and cumulative prompt tokens by **42–63%** compared with a repository-only takeover. In other words: the agent that receives the conversation does dramatically less flailing than the agent that has to rediscover the state of the world from the repo.

Now put that next to how agent bills are actually shaped. One developer's measured corpus of 722 sessions, 150,902 model calls and 34.56 billion tokens found that **97.05% of billed tokens were cache reads**, and that under list pricing context handling was **87.8% of cost versus 12.2% for generation** — re-reading context cost 4.59x everything the models wrote ([dev.to write-up](https://dev.to/arsentev/97-of-what-my-coding-agent-billed-for-was-re-reading-its-own-context-4o2)).

An instrumented production compression gateway across Claude Code/Codex with Claude Sonnet and GPT-5 ([arXiv:2609.22114](https://arxiv.org/abs/2609.22114)) adds the corollary: tool-schema filtering removes a fixed ~21K–57K tokens per typical turn and is the only reliably positive lever, while file-read compression saves only about 2% of the cached prefix per turn but accumulates quadratically (~3350·N² tokens).

Read those three findings together and portability stops looking like convenience. Carrying the real transcript instead of re-deriving state is a **token-cost control**, and the numbers say the re-derivation is the expensive half of agent work.

## How does Skillsync compare with the alternatives?

The honest competitive frame is that "move a session" became a commodity in the second half of 2026. The moat is not the move; it is adapter fidelity depth plus the layer around it.

| Tool | Language / platform | Harness coverage | Stars (2026-09-29) | Team layer |
|---|---|---|---|---|
| txcript / Skillsync | Rust, cross-platform + macOS app | 17 adapters, 11 continue-capable | 142 | Yes — shared sessions, skills, memory |
| [Continuo](https://usecontinuo.dev/) | Swift, macOS only, v0.3.1, MIT | 3 (Claude Code, Codex, OpenCode) | 10 | No |
| [session-migrate](https://github.com/xhluca/session-migrate) | Python | Claims 18 harnesses | 118 | No |
| [agent-session-bridge](https://github.com/connectwithprakash/agent-session-bridge) | Python (PyPI v0.5.0, 3.11+) | 3 (Claude Code, Codex, Hermes) | 0 | No |

Two things stand out. First, Continuo — built by a commenter in the same HN thread — owns a feature Skillsync does not have: user control over *how much* of the conversation to bring, which the Skillsync founder publicly complimented. Second, session-migrate is three months younger and already within striking distance on stars while claiming a comparable adapter count. On raw "can it move my session," these tools are close.

The differentiation is therefore threefold: adapter breadth with continuation support, the neutral interchange JSON as a non-proprietary escape hatch, and the workspace layer that turns an individual utility into a team product.

## What carries over — and what silently does not?

Fidelity is where a review earns its keep. The txcript README is upfront: "Agent-specific records and unsupported fields can be lost." Three separate failure modes stack up here.

**1. Translation loss.** If the destination format cannot represent a record the source produced, that record is dropped. This is bounded and knowable, but you have to check per adapter pair.

**2. The receiving agent's own compaction.** This is the one people miss. Co-founder Narsagna, in the HN thread: *"With longer sessions, the receiving agent sometimes decides to compact it. But the whole transcript still exists and is accessible."* The degradation happens inside the destination harness' context management, not in the translation step. You cannot fix it by improving the converter — only by choosing how much to hand over.

**3. The environment gap.** The destination supplies its own system instructions and tools, and project files must be brought separately. Portable *conversation* is not portable *environment*. Moving a session into a harness with a different tool set means the conversation references capabilities that no longer exist on the other side.

The direction limitation matters too: it is one-way today. You can go from a chat or consumer session *into* a coding agent, but merging a colleague's session into an already-open one is explicitly not supported yet. And cross-machine sync works via SSH or by exporting `run.json` and continuing it locally — not via a shared live session.

## What does Skillsync cost, and what is behind the paywall?

The [pricing page](https://skillsync.com/pricing) is clear on the boundary and opaque on the number. For individuals, the free tier is generous: all local sessions searchable, continue on any agent, a personal skill library installed on every agent, analytics, plus the CLI and MCP server. Portability itself is not the paid wall — **collaboration is**.

| Tier | What you get | Price |
|---|---|---|
| Free | Local session search, continue on any agent, personal skill library, analytics, CLI + MCP | $0 |
| Pro Teams | Shared workspaces, cloud sync, self-improvement, up to 10 seats | Not published ("Book a demo") |
| Enterprise | Unlimited users/workspaces, custom harness integrations, priority support | Not published |

The workspace model splits three things teams share: **sessions** (teammates can read, search, and pick up a session on their own agent), **skills** (one library installed across every member's agents), and **memory** (workspace notes and learned skills that load into Codex or Claude Code when a session starts).

For a buyer-facing review, the missing public number for Pro Teams and Enterprise is the main commercial caveat. "Book a demo" pricing is normal at this stage, but it means you cannot model the cost of a 10-seat rollout from the website alone.

## Hands-on: what does the workflow actually look like?

The CLI sequence for moving a session is short enough to walk through:

```bash
txcript list                      # discover sessions across harnesses
txcript query "rate limit fix"    # search across all of them
txcript view <session-id>         # inspect the transcript
txcript crop <session-id>         # trim to the relevant span
txcript export <session-id>       # write neutral interchange JSON
txcript continue <session-id> --to codex
txcript resume <session-id>
```

The `crop` step is the quiet workhorse. It is how you address the compaction problem deliberately rather than letting the destination decide: hand over the 40 turns that matter instead of 400 and accept a lossy auto-compaction. `txcript mcp` then lets any MCP client query that session store as a tool rather than a manual step — one server in your config, and your agent can read its own history. With 20,000+ public MCP servers now catalogued (MCP.so 21,000+, Glama.ai 23,000+) and 67 million local MCP server downloads in April 2026 alone, exposing a session store over MCP is a natural fit for the ecosystem's current shape.

One real papercut surfaced live in the launch thread and is worth repeating as a caveat: the email on the Privacy page bounced. The founder republished `founders@skillsync.com`. Small thing, but a reminder that a W26-stage product still has W26-stage plumbing.

## Is the local-first privacy claim real?

The claim is explicit: sessions, skills and memory stay on each machine until a member shares them. The engineering supports it — the format itself is the open standard, the core is Apache-2.0, and there is no account-scoped pipeline that has to touch your session to convert it. You can build from source and read the converter.

Two caveats keep this from being a clean endorsement. First, adapter breadth for the *live-account* sources — Claude Chat, ChatGPT, Cloud Cowork — relies on reusing an app login rather than a documented export path, which is a private-API dependency that can break without notice. Second, local-first at the individual tier becomes cloud sync at Pro Teams. The privacy posture is genuinely different per tier, and the tier that most needs scrutiny for a sensitive repo is the one you pay for.

## Practical workflows that justify the tool

**Phone to desk.** Brainstorm a design in a consumer chat on your phone, then continue in Claude Code at the desk with the full reasoning and tool history alongside. This is the workflow that sold the launch thread.

**Multi-agent by task.** Prototype in Antigravity, harden in Claude Code, review in Codex — moving the session instead of restarting it. Given the 42–63% cumulative-token reduction measured for context-bearing handoffs, this is where the cost story cashes out.

**Ship a session, not a summary.** Instead of pasting a Slack summary of why a change was made, send the session and let the reviewer see the evidence.

## Limitations and who should wait

- **One-way only.** No merging a colleague's session into a live one.
- **Read-only adapters.** Hermes Agent and Amp can receive but not continue.
- **Environment ≠ conversation.** Tools, system instructions and project files must be brought separately.
- **Destination-side compaction.** The receiving harness may compress your long transcript; crop deliberately.
- **Undisclosed team pricing.** You cannot budget Pro Teams from the website.
- **Governance question.** With an Apache-2.0 core, 8 contributors and 23 open issues, how much of the roadmap is community-driven versus commercial? The archived-ChatGPT-chats fix is the encouraging data point: user solfox filed issue #52 (archived Codex/ChatGPT chats were invisible to discovery), submitted PR #53, and the maintainer merged it the same day, 2026-09-17. That is a working contribution loop — the model, not the exception.

**Wait if** you use exactly one agent and intend to keep using it. **Adopt the free tier now if** you run two or more agents and have ever re-explained your codebase to a new one. **Evaluate Pro Teams if** your team has to justify tool switches to people who need to see the reasoning, not a summary of it.

## Verdict

Skillsync is a small, well-scoped tool sitting on a genuinely structural problem: context is the most expensive thing in agent work, and it has been locked to whichever harness produced it. The deterministic, no-summarizer architecture is the right call for anything that has to be trusted later, and the open-source core plus neutral interchange format means the lock-in risk is on the destination harness, not on Skillsync. txcript at 142 stars and 8 contributors is early, the adapter split is uneven, and the team tier is unpriced — but the free tier is the whole portability feature with no wall in front of it, which makes trying it a low-stakes decision.

## FAQ

**Is Skillsync open source?**
The conversion engine is. txcript is Apache-2.0 on GitHub, with a Rust library, CLI and WASM build you can compile yourself. The macOS app, the `skl` CLI and the team workspace layer are the commercial product around it — an open-core split.

**Does it work with Hermes or Antigravity?**
Both have adapters, with different capabilities. Antigravity supports read *and* continue. Hermes Agent is read-only: you can bring a Hermes session into another harness, but you cannot continue a foreign session inside Hermes. Amp is also read-only, and the live-account sources (Claude Chat, ChatGPT, Cloud Cowork) are read-only by nature.

**Can you merge two sessions together?**
Not today. The direction is one-way — from a chat or consumer session into a coding agent. Merging a colleague's session into an already-open one is explicitly unsupported. Cross-machine sync works by SSH or by exporting `run.json` and continuing it locally.

**What does it cost?**
The individual tier is free and includes local session search, continuing on any agent, a personal skill library, analytics, and the CLI plus MCP server. Pro Teams adds shared workspaces, cloud sync and up to 10 seats, and Enterprise adds unlimited seats and custom harness integrations — neither price is published, so both require a demo request.

**Does the receiving agent lose my reasoning traces?**
Not in the translation — the founder states there is no AI in the conversion, and tool calls and reasoning are retained. Degradation happens later, inside the receiving harness: with long sessions the destination may decide to compact. The full transcript still exists and is accessible, and `txcript crop` gives you direct control over how much to hand over.
