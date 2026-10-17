---
title: "Cloud Agents Are Not Prisons: The Harness Portability Test"
date: 2026-10-08T14:47:00+00:00
tags:
  - "cloud agent lock-in 2026"
  - "ai agent harness lock-in"
  - "self-hosted ai agent execution"
  - "agent runtime portability mcp"
  - "portable agent skills across harnesses"
  - "agent skills lock-in"
  - "mcp tool definitions portability"
  - "session state checkpoint portability"
  - "prompt cache ownership"
  - "local ai coding agent setup 2026"
  - "ai agent portability audit 2026"
  - "claude code skills directory"
  - "codex config toml agents md"
  - "self-hosted coding llm vs managed copilot"
  - "ai agent switching cost"
description: "A four-surface test of how portable a cloud coding agent really is: agent skills, MCP tool definitions, session state and prompt-cache ownership, each checked against the vendor's own documentation."
draft: false
cover:
  image: "/images/cloud-agents-ai-prisons-local-execution-2026.png"
  alt: "Cloud Agents Are Not Prisons: The Harness Portability Test"
  relative: false
schema: "schema-cloud-agents-ai-prisons-local-execution-2026"
---

When engineering leads ask what actually locks them to a cloud coding agent, the honest answer is the harness — the skills, tool definitions, session state and cached context that sit around the model — not the model itself. Models commoditised fast enough that swapping one for another is now routine; the accumulated configuration around it is what resists moving. That is a specific, checkable claim, and this article checks it.

The test is deliberately narrow. It names four surfaces where harness lock-in would live — agent skills, MCP tool definitions, session/checkpoint state, and prompt-cache ownership — and asks one question of each: does the vendor's own documentation show the artifact is exportable, versioned and self-hostable? The verdict is not uniform, and that is the point. Two surfaces are portable, one is partial, and one is not portable at all on the documentation available today. This is a portability audit, not a tool ranking; if you are still picking a tool, the [Continue.dev vs GitHub Copilot comparison](/posts/continue-dev-vs-github-copilot-2026/) and the [multi-agent coding workflow guide](/posts/multi-agent-coding-workflow-2026/) cover that neighbouring ground.

## What this test is, and what it is not

This is a documentation test, not a benchmark. No agent was migrated between platforms, no provider was measured, and no migration cost was timed. Every quotation below is a verbatim excerpt from a page fetched on 2026-10-08, and each page is linked so you can re-read it and disagree. Where a claim could not be supported from the vendor's documentation, it was withdrawn rather than softened.

The seed version of this article carried a slogan in its title — "inevitable AI prisons." That slogan is unfalsifiable and it is not what the evidence supports. The narrowed thesis is smaller and survives scrutiny: lock-in concentrates in the harness, and you can measure how much of it is real one surface at a time.

## The four surfaces at a glance

| Surface | Verdict | What moves | What does not move |
|---|---|---|---|
| Agent skills | Portable | `SKILL.md` and its files; project instruction files | Automatic discovery, marketplace and cloud-side scanning |
| MCP tool definitions | Portable | The protocol, the schema, the `tools/list` definition | A vendor-hosted MCP *server*; server-assigned session IDs |
| Session / checkpoint state | Not portable | Nothing, as documented | The runtime session, its checkpoints and auto-memory |
| Prompt-cache ownership | Partial | The reusable prefix text you author | The provider-side KV cache itself |

Two portable, one partial, one not — that clears the brief's three-of-four threshold, but only because the test was narrowed to documentation-checkable claims.

## Surface 1 — Agent skills: a directory of Markdown you already own

Anthropic defines the artifact plainly: skills are "reusable, filesystem-based resources that give Claude domain-specific expertise" ([Agent Skills overview](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview.md)). In Claude Code the same page states that "Custom Skills in Claude Code are filesystem-based and don't require API uploads: place them in `~/.claude/skills/` (personal) or `.claude/skills/` (project)." A skill is a directory of text on your own disk. Nothing in that description is held in vendor custody.

The qualifier matters, and the same vendor page supplies it: "**Custom Skills do not sync across surfaces**. Skills uploaded to one surface are not automatically available on others." So the file travels; the conveniences wrapped around it — automatic loading, marketplace distribution, cloud-side scanning — do not. Portable here means the artifact is exportable, not that its behaviour is guaranteed identical elsewhere.

Project instruction context sits on the same surface. Claude Code reads `CLAUDE.md` files — "markdown files that give Claude persistent instructions for a project, your personal workflow, or your entire organization" — written in plain text and read at the start of every session ([Claude Code memory](https://docs.claude.com/en/docs/claude-code/memory.md)). The same page records a version dependency worth noting: "Reading `AGENTS.md` directly requires Claude Code v2.1.277 or later." OpenAI's CLI mirrors the pattern from its own documentation: "Codex reads configuration details from more than one location. Your personal defaults live in `~/.codex/config.toml`, and you can add project overrides with `.codex/config.toml` files" ([Codex local configuration](https://developers.openai.com/codex/local-config.md)). Two vendors, plain files in both cases. The conventions are converging, not identical, so a shared file can produce different behaviour.

## Surface 2 — MCP tool definitions: an open, versioned protocol

Tool definitions are the second place a harness could hold you. They do not, because the definition format is a public standard. The Model Context Protocol specification states that it "defines the authoritative protocol requirements, based on the TypeScript schema in [schema.ts](https://github.com/modelcontextprotocol/specification/blob/main/schema/2025-06-18/schema.ts)" — a file that lives in a public repository under a pinned revision, 2025-06-18 ([MCP specification index](https://modelcontextprotocol.io/specification/2025-06-18/index.md)). A versioned spec with a public schema is the opposite of a proprietary format.

The mechanics are standardised too. The specification explains that MCP "allows servers to expose tools that can be invoked by language models," and that tool discovery is a defined call: "To discover available tools, clients send a `tools/list` request" ([Server features: tools](https://modelcontextprotocol.io/specification/2025-06-18/server/tools.md)). A tool definition you wrote against this spec is readable by any client that implements the spec.

Two honest limits. First, the protocol is portable; a given MCP *server* may still be a hosted dependency you do not control. Second, the transport layer reintroduces server-side state: "An MCP 'session' consists of logically related interactions between a client and a server, beginning with the initialization phase," and the Streamable HTTP transport assigns an `Mcp-Session-Id` that the server tracks ([Transports](https://modelcontextprotocol.io/specification/2025-06-18/basic/transports.md)). The tool *definition* moves cleanly; a live stateful session does not.

## Surface 3 — Session and checkpoint state: the wall that is still standing

This is the surface where the documentation gives the least comfort. Claude Code's memory page states the starting position directly: "Each Claude Code session begins with a fresh context window. Two mechanisms carry knowledge across sessions:" — the `CLAUDE.md` file you own, and auto memory, which the same page describes in one sentence: "Auto memory is machine-local. All worktrees and subdirectories within the same git repository share one auto memory directory. Files are not shared across machines or cloud environments." ([Claude Code memory](https://docs.claude.com/en/docs/claude-code/memory.md)). On the OpenAI side, the hosted path is equally explicit: Codex Cloud tasks "Start tasks from a published environment. Each task has its own workspace and can keep working while your computer is asleep" ([Codex Cloud](https://learn.chatgpt.com/docs/cloud.md)). The environment is the vendor's.

Neither page documents an export of a runtime session or its checkpoints. That is a real finding, but it must be stated at its true strength: the absence of a documented export is evidence of no documented export, not proof that none exists. A CLI-level resume flag is not an artifact format you can carry to another harness. This is the softest of the four verdicts for exactly that reason, and it is the one most likely to change on the next vendor documentation release.

## Surface 4 — Prompt-cache ownership: the cache is not yours, the prefix can be

Prompt caching is the partial case, and the distinction is worth making precisely. OpenAI's guide states what the cache actually holds: "The prompt cache stores key-value (KV) tensors, not the tokens themselves," and reuse is fragile — "Cache reuse requires the entire rendered prefix to match" ([OpenAI prompt caching](https://platform.openai.com/docs/guides/prompt-caching.md)). That is provider-side state keyed to an exact byte prefix, and it is not an artifact you can hand to a competing provider.

The reason it can still be owned is that the prefix is authored content. OpenAI documents that it "caches the model's full rendered context including OpenAI-provided instructions, developer messages" — meaning the cache key is built from the system prompt, the tool definitions, the instruction files and the conversation history, all of which you can version as source. The KV cache cannot move; the text that generates it is entirely yours, provided you keep it in files rather than in a vendor console.

The economics reinforce the same split. Anthropic documents that "By default, the cache has a 5-minute lifetime," and that "5-minute cache write tokens are 1.25 times the base input tokens price" ([Anthropic prompt caching](https://docs.claude.com/en/docs/build-with-claude/prompt-caching.md)). OpenAI states that "For GPT-5.6 and later, cache writes cost 1.25× the standard, uncached input-token rate" ([OpenAI prompt caching](https://platform.openai.com/docs/guides/prompt-caching.md)). Both are vendor-published list figures, not measured invoices — treat them as published rate behaviour, not spend. The practical conclusion is unglamorous: you cannot carry a cache, but you can guarantee it is cheap to rebuild by keeping the prefix in version control.

## The local-execution counter-case, as a labelled trade-off

The claim that local execution is the escape is stronger as a trade-off statement than as an inevitability, and it needs one measured anchor rather than slogans. The relevant anchor is the price of the machine itself, taken from the vendor's own store on 2026-10-08.

Apple's US store lists preconfigured Mac Studio configurations from $2,499 to $6,799 in list price (US store, checked 2026-10-08) ([Apple, Shop Mac Studio](https://www.apple.com/shop/buy-mac/mac-studio)). That is a primary vendor list price band for one desktop-class machine's starting build. This article does not bind a specific dollar amount to a named CPU/GPU configuration, because the fetched store markup does not evidence that pairing.

Read that anchor as what it is: a floor for one desktop-class machine's entry configuration. It excludes memory and storage upgrades, power, support, the operations labour of running a fleet, and the model-quality gap between a local model and a frontier hosted one. A list price is not a total cost of ownership, and this article does not present it as one.

What the anchor supports is a labelled trade: a local runtime converts exit cost from an engineering project into a capital purchase plus an operations obligation. It buys independence and marginal-cost-zero inference after the hardware, and it pays for them with a real operations burden and a capability lag. Cloud agents buy frontier reasoning and zero capital expenditure, and pay for them with dependency and a higher exit cost. Neither column is the right answer in general. The right answer is that you should be able to choose, and to know what the choice costs. For the concrete local-execution side of that trade, see the [self-hosted AI coding assistants comparison](/posts/self-hosted-ai-coding-comparison-2026/) and the [local AI agents guide](/posts/local-ai-agents-guide-2026/).

## The portability audit you can run this quarter

Abstract lock-in advice is useless, so here is the checkable version — one row per surface, each tied to the documentation above.

1. **Skills.** Locate every skill as a directory of plain text (`SKILL.md` plus assets) and confirm it lives in a repository you control rather than only in a vendor console. If a skill exists only inside a hosted product, it fails this test by the vendor's own statement that custom skills do not sync across surfaces.
2. **Instruction and configuration.** Confirm your project rules are plain files (`CLAUDE.md`, `AGENTS.md`, `.codex/config.toml`) under version control, and record the client versions that read them. Note the version dependency — reading `AGENTS.md` directly requires Claude Code v2.1.277 or later — so a teammate on an older client is a portability gap.
3. **Tool definitions.** Confirm your tools are declared against the pinned MCP revision and discoverable through a standard `tools/list` call, and separate them in your inventory from any hosted MCP *server* you do not operate. The protocol moves; the server may not.
4. **Session state.** List every workflow that depends on accumulated session or checkpoint state, and mark it unmovable until a documented export exists. This is the surface with no documented exit today, so treat it as the honest floor of your exit cost.
5. **Prompt-cache prefix.** Move the system prompt, tool definitions and instruction files that form the cache key into version control, so the prefix is rebuildable on any provider. You cannot move the KV cache; you can make regenerating it a checkout.

Run the five checks and you will know, per surface, whether your cloud agent deployment is a rental with a stated exit or a lease you cannot get out of. Many teams will find a rental with a reasonable exit. That is a legitimate outcome, and it is a better answer than a slogan.

## What this article withdraws from its earlier draft

The seed version of this piece rested on numbers that were never verified against a primary source in this run. They are withdrawn here rather than repeated:

- The IBM IBV figures (71% unable to switch, 91% unable to map dependencies, 68% data-residency difficulty) are removed; the IBM survey was not re-opened for this test.
- The Zapier migration figures (42% smooth, 58% overran) and the 41% / ~90% expectation numbers are removed for the same reason.
- The agentic-market size ($100B by 2028), the vendor revenue figure (approximately $14B annualised), Gartner's cancellation forecast (over 40%), the GitGuardian 28.65M-secrets count, and the hardware and throughput tables (DGX Spark, Strix Halo, RTX 3090, token-per-second rates) are all removed. None was re-verified against a primary source in this run.
- Two vendor marketing claims that the seed draft repeated (a "70% of companies" figure and an "~80% savings" hybrid figure) are dropped rather than carried with a label.

What remains is what the four linked vendor pages and the one vendor price page actually state, on the date each was checked.

## Quick answers

**Do you have to choose between cloud and local agent execution?** Not on the evidence here. The two portable surfaces — skills and MCP tool definitions — are portable in both directions, so a harness built on them can route to either. The surface that does not move, session and checkpoint state, is where the real lock-in sits, and it is the one to plan around first ([Claude Code memory](https://docs.claude.com/en/docs/claude-code/memory.md)).

**What is the smallest change that reduces harness lock-in?** Make the prompt-cache prefix a versioned artifact. OpenAI documents that the cache key is "the model's full rendered context including OpenAI-provided instructions, developer messages," and that reuse "requires the entire rendered prefix to match" ([OpenAI prompt caching](https://platform.openai.com/docs/guides/prompt-caching.md)). Moving that prefix into source control is nearly free and converts a cache you cannot carry into one you can always rebuild.

## Sources

Every source below was fetched by the author on 2026-10-08; the raw pages are a private local author check and are not published for download. Each URL is the exact page quoted above.

- [Anthropic — Agent Skills overview](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview.md)
- [Anthropic — Claude Code memory](https://docs.claude.com/en/docs/claude-code/memory.md)
- [Anthropic — Prompt caching](https://docs.claude.com/en/docs/build-with-claude/prompt-caching.md)
- [OpenAI — Codex local configuration](https://developers.openai.com/codex/local-config.md)
- [OpenAI — Codex Cloud](https://learn.chatgpt.com/docs/cloud.md)
- [OpenAI — Prompt caching](https://platform.openai.com/docs/guides/prompt-caching.md)
- [Model Context Protocol — specification, revision 2025-06-18](https://modelcontextprotocol.io/specification/2025-06-18/index.md)
- [Model Context Protocol — server tools](https://modelcontextprotocol.io/specification/2025-06-18/server/tools.md)
- [Model Context Protocol — transports](https://modelcontextprotocol.io/specification/2025-06-18/basic/transports.md)
- [Apple — Shop Mac Studio](https://www.apple.com/shop/buy-mac/mac-studio)
