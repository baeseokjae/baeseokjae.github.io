---
title: 'Agent CodeMode MCP: Let Coding-Agent Scripts Call Your MCP Servers'
date: 2026-10-01T02:41:56+00:00
tags:
  - MCP
  - Code Mode
  - agent codemode MCP
  - Claude Code
  - coding agents
  - tool calling
  - AI for developers
description: "Agent CodeMode MCP lets a script your coding agent writes call the MCP servers the agent already authenticated — 40 tool calls become 1 script."
draft: false
cover:
  image: "/images/agent-codemode-scripts-call-mcp.png"
  alt: "Agent CodeMode MCP: Let Coding-Agent Scripts Call Your MCP Servers"
  relative: false
schema: "schema-agent-codemode-scripts-call-mcp"
---

Agent CodeMode MCP means letting the script your coding agent writes call the MCP servers your agent has already authenticated. Instead of the model making forty tool calls one at a time, it writes one script; the credential your agent minted is reused from disk. Measured: 40 calls and 262,159 characters become 1 script and 903 characters.

## What is Agent CodeMode, and why does it exist?

Code Mode is the pattern where an LLM writes code that calls tools, instead of calling each tool through the model's native tool-calling interface. Cloudflare's Kenton Varda and Sunil Pai named it in September 2025 with a thesis that reads as obvious once you see it: [LLMs are better at writing code to call MCP than at calling MCP directly](https://blog.cloudflare.com/code-mode/). Anthropic published the same architecture as vendor guidance on November 4, 2025 in [Code execution with MCP](https://www.anthropic.com/engineering/code-execution-with-mcp). The reasoning is about training data: models have seen a very large volume of real TypeScript, and comparatively little synthetic JSON tool-schema blobs.

The "Agent CodeMode" variant narrows the general pattern to one specific, practical situation: you are already running a coding agent — Claude Code, Cursor, Windsurf, Gemini CLI — and that agent has already completed the OAuth dance for every MCP server you connected. The design question becomes whether your *scripts* can use those credentials without a second authentication path.

### Why can't the model just call the MCP tool directly?

It can, and for a handful of calls it should. The problem appears at scale and is a cost problem with two distinct sources that most write-ups blur together. Cloudflare names the first: in the classic loop, every intermediate result must flow back into the model's context before the next decision, so a five-step chain pays five inference passes and drags four payloads the model never reads. Anthropic names both: tool definitions overload the context window, and intermediate tool results consume additional tokens — the same two-hour meeting transcript flows through context twice.

Separating those two costs matters because they have different fixes. Upfront tool definitions are fixed by typed clients or progressive discovery. Intermediate results are fixed by running the loop *inside* code, where data can be filtered before it ever reaches the model.

## How does code mode cut token usage? Two costs, two fixes

The table below separates the two cost sources and shows which mechanism attacks each one. Numbers are quoted from the cited source and marked where they are modeled rather than measured.

| Cost source | Classic tool calling | With Code Mode | Fix mechanism |
|---|---|---|---|
| Tool definitions in context | All schemas loaded upfront | Typed client read on demand, or `search()` | Codegen / progressive discovery |
| Intermediate results | Every result round-trips per turn | Filtered inside the script | Loop runs in code |
| Cloudflare API (all endpoints) | 1,170,523 tokens (full schemas) | ~1,000 tokens | Server-side `search()` + `execute()` |
| Anthropic's sample workflow | 150,000 tokens | 2,000 tokens | Code execution with MCP (−98.7%) |
| A 40-call Linear workspace | 262,159 chars (~65,500 tokens) | 903 chars (~226 tokens) | One script, one result |

Cloudflare's server-side implementation covers roughly 2,500 API endpoints behind two tools, `search()` and `execute()`, at a fixed footprint of about 1,000 tokens — down 99.9% from an equivalent native MCP server, which would consume [1.17 million tokens](https://blog.cloudflare.com/code-mode-mcp/). That figure exceeds the entire context window of current frontier models, which is the sharpest way to state why the naive approach has a ceiling.

The Linear measurement is the most useful one for a how-to because it is concrete: 40 sequential MCP tool calls in a live workspace of 39 tickets produced 262,159 characters (~65,500 tokens) of context, while the equivalent script returned 903 characters (~226 tokens) — [290× less, 99.66% saved](https://github.com/janwilmake/agent-codemode). That ratio is a floor, not a ceiling: in a tool-call loop those characters are re-read on every subsequent turn.

### Where does the saving actually come from in production?

Agent Swarm published a measured production job on July 8, 2026: 26 calls — one `workflow_list`, one `schedule_list`, and 24 per-workflow `workflow_listRuns` calls — collapsed into one script. The measured script path put [25,811 characters](https://www.agent-swarm.dev/blog/code-mode-token-savings) into the agent's context, versus roughly 3.26M characters on the modeled raw path (a 99.2% reduction). The character figure is measured; the 3.26M is modeled by extrapolating a sample of 4 workflows (6, 26, 53, and 227 runs, averaging 3,447 characters per run) across 920 recorded runs. Notably, the first version of that post was machine-drafted, was criticized on Hacker News, and was rewritten with explicit measured-versus-modeled labels — which is exactly the discipline to copy when you benchmark your own workflow.

Their operational rubric is the reusable part: past roughly ten items, or any bulk fan-out, write a script instead of N tool calls.

## What do the three major implementations do differently?

There are three distinct architectures, and they make different tradeoffs about where the code runs.

| Implementation | Where code runs | Tool surface | Client changes needed | Credentials |
|---|---|---|---|---|
| Cloudflare client-side Code Mode | Dynamic Worker / V8 isolate | Generated TypeScript API from server schema | Yes — agent must ship a sandbox | MCP server's own auth |
| Cloudflare server-side Code Mode | Dynamic Worker isolate | `search()` + `execute()` | None | MCP server's own OAuth 2.1 |
| Anthropic code execution with MCP | Agent's code environment | MCP servers as a filesystem of TS modules | Requires code-execution environment | MCP server's own auth |
| agent-codemode (local CLI) | Your shell | Per-server typed TS modules | Skill copy into `~/.claude/skills/` | **Inherited from your coding agent** |
| MCPorter / CLI-based discovery | Your shell | `mcporter`-managed definitions | CLI install | Own vault at `~/.mcporter/credentials.json` |

Cloudflare's isolates have [no filesystem, no environment variables to leak through prompt injection, and external fetches disabled by default](https://blog.cloudflare.com/code-mode-mcp/). Anthropic's version presents each MCP server's tools as a directory of `.ts` files the agent reads only when needed, and warns that running agent-generated code requires a secure execution environment with sandboxing, resource limits, and monitoring — operational overhead that direct tool calls avoid.

### What is the one row where agent-codemode is genuinely different?

Credentials. Every implementation in the table above requires you to supply something: an API key, an OAuth flow, a private vault. The `agent-codemode` CLI reads the OAuth token your coding agent already minted — on macOS, the Keychain entry `Claude Code-credentials`, and on Linux, `~/.claude/.credentials.json` — and speaks JSON-RPC to the MCP server directly. No API keys, no OAuth flow, no vault, and no model in the loop.

That is the whole trick, and it is worth being precise about why it works. Your agent already completed the authentication for `linear`, `axiom`, `fastmail`, or a self-hosted server. Those tokens sit on disk, reachable only by a model that decides to make one tool call at a time. The CLI turns that latent capability into an addressable one.

## How do you install agent-codemode and point it at authenticated servers?

Install it with Node 18 or newer, then confirm which servers already have a live token:

```bash
npm install -g agent-codemode    # also installs a shorter `codemode` alias

agent-codemode servers                 # who has a live token
agent-codemode tools linear            # what can it do
agent-codemode call linear list_issues --arg assignee=me --arg state="In Progress" --text
agent-codemode types --all             # typed TypeScript for every server you're logged into
```

`agent-codemode servers` is the load-bearing command. It merges server definitions from your coding agent's config files *and* the credential store, and shows which client each entry came from — so it doubles as a diagnostic when a server you thought was connected turns out not to be. The repository reads Cursor, Windsurf, VS Code, and Gemini CLI MCP configs as well as Claude Code's.

To make the agent actually prefer scripts over tool calls, copy the bundled skill into place — this is the step that changes behaviour, not the install:

```bash
mkdir -p ~/.claude/skills && cp -r .claude/skills/agent-codemode ~/.claude/skills/
```

An agent that knows this exists writes one script. An agent that does not keeps doing what it knows, one tool call at a time.

## What does your first script look like?

Start with a single CLI call to prove the credential path works end to end. Then move into TypeScript. The CLI generates a typed module per server from the live `tools/list`, so a wrong argument key or type is a compile error with no cast at the call site:

```ts
// Generated by agent-codemode from linear's tools/list. Do not edit by hand.
// Each generated module registers itself with `mcp`, so importing it is all
// that is required — a server you never generated types for keeps working.

import { linear } from "agent-codemode/types";

const issues = await linear.list_issues({ assignee: "me", state: "In Progress" });

// Filter inside the script: only the summary crosses into model context.
const summary = issues.map((i) => `${i.identifier} ${i.state}`).join("\n");
console.log(summary);
```

The important line is the filter. This is where the second cost source from the table gets eliminated: the loop runs in code, so the model sees a short summary rather than the full payload.

## How do you generate typed clients with agent-codemode types --all?

`agent-codemode types --all` emits one TypeScript module per authenticated server plus an index barrel. Every tool becomes a method, every input schema becomes an interface, and every description becomes a JSDoc comment. The generated modules self-register by merging into the `McpServers` interface, which is what makes an incorrect call a build-time failure rather than a runtime surprise.

The generation step is the answer to the first cost source: the type surface is loaded once, on demand, instead of placing every tool definition in context on every turn. On a 49-tool server, a third-party 2026 analysis models classic MCP at roughly [29,400 tokens per turn](https://botoi.com/blog/cloudflare-code-mode-mcp-token-tax) spent on tool descriptions — about 294,000 tokens across a ten-turn conversation — versus a one-time type-surface load for code mode. Treat that as modeling, not a benchmark: it comes from a single-server extrapolation rather than a measured workload.

## Can a script reconcile two trackers in one pass?

This is the workflow that justifies the setup. Suppose a Linear ticket closes but the corresponding GitHub issue stays open. The classic path is: list Linear issues, read the results, decide which ones to check, list GitHub issues, read those, compare, then make the update calls — six or more round-trips, each one dragging a payload back through the model.

Run in code, it is one execution: fetch both lists, compute the difference with native array methods, and return only the mismatches that need a human decision. Counting occurrences across 262,159 characters by reading them is something a model does approximately, and can get wrong while still having spent 65,500 tokens. Code gets it exactly right. Determinism is an underrated part of the pitch.

## How do you measure the win on your own workflow?

Do not trust the headline percentages — the right number for your setup depends on payload sizes and call counts. Measure four things:

1. **Call count** on the raw path (how many tool calls the task would need).
2. **Characters returned** to context on both paths, from the tool result logs.
3. **Re-reads** — multiply by the number of subsequent turns, because each result is re-sent as input on every later turn.
4. **Wall clock**, which the human notices before they notice the invoice. Forty sequential calls each stall on a model deciding what to ask next; a script makes the same forty requests back-to-back.

Label every number as measured or modeled, as the Agent Swarm post does. An honest small win is more useful than an inflated large one, and it is much harder to falsify.

## Can the script run without a model — cron and CI?

Yes, and this is the part that answers the reasonable objection that code mode on top of MCP on top of code mode is a useless extra layer. It is not a layer. It is the model *leaving*. A job that moves three tickets does not need reasoning; it needs the credential, and the credential is already there.

That means a scheduled task can call your MCP servers with no model in the loop and no tokens spent. The script outlives the session. Cron and CI become legitimate consumers of the same tools your interactive agent uses, authenticated the same way — which is a capability you do not get from native tool calling at all.

## Is executing model-written code safe?

This is now the real cost of code mode. Direct tool calling keeps the trust boundary at "the model picks a tool from a fixed list." Code mode moves it to "the model writes code you execute," and the sandbox becomes the security boundary.

The concrete evidence is Check Point Research's 2026 work on `workerd`, the runtime beneath both Cloudflare Workers and Code Mode sandboxes. They found [five memory-corruption bugs](https://research.checkpoint.com/2026/when-agentic-glue-melts/) in workerd's native C++ and turned them into two end-to-end attacks: a cross-tenant heap swipe using an out-of-bounds read in URLPattern, and a Code Mode sandbox escape that starts from a single prompt injection and reaches native code execution on the host via a use-after-free in `node:zlib`. Cloudflare rated the zlib and HTMLRewriter use-after-frees as Critical; the bugs were reported through HackerOne under coordinated disclosure, no CVEs were assigned, and proof-of-concept code was released at Black Hat USA 2026. Self-hosted `workerd` and Code Mode deployments should update to `v1.20260619.1`.

The design lesson is not "avoid code mode" — it is that the second-layer sandbox (Linux namespaces plus seccomp) is what contains a compromised process, and that a Node-compatibility surface reimplemented in C++ is a large amount of attacker-reachable native code. If you are choosing where that sandbox lives, our breakdown of [sandboxed agent harnesses for teams](/posts/onecli-sandboxed-agent-harness-teams/) covers the isolation models in the same design space. Practical mitigations for your own scripts:

- Run generated code in a sandbox with no ambient network egress and no environment variables.
- Pass tools into the execution context, never credentials. A script that reads a token from disk should be the *only* thing that reads it.
- Prefer running the model-generated script as a one-shot subprocess with a timeout and no inherited secrets.
- Keep the runner patched; a sandbox escape is a version-specific bug, not a permanent property.

## When is code mode the wrong choice?

Often. Classic tool calling is still correct under roughly three or four chained calls, for fewer than ten tools, and whenever your client is Claude Desktop, Cursor, or VS Code on classic MCP with no shell. The overhead is also real: code mode adds roughly [10–50 ms of compile and isolate startup per turn](https://botoi.com/blog/cloudflare-code-mode-mcp-token-tax) and it shifts the primary failure mode from "the model picked the wrong tool" to "the generated code threw at runtime."

There is also a credible competitor that gets most of the token win without executing model-written code. Speakeasy's Dynamic Toolsets report up to [160× token reduction](https://www.speakeasy.com/blog/how-we-reduced-token-usage-by-100x-dynamic-toolsets-v2) with roughly 96% input and 90% total reduction at 100% task success — dynamic discovery competes with code mode on token count while keeping the no-code-execution safety property. Their critique of pure semantic search is worth internalizing: with no visibility into what exists, the model sometimes never searches at all. Browserbase's framing lands in the same place from the other direction, reporting roughly [88% less context](https://www.browserbase.com/blog/code-mode-is-all-you-need) for a three-service parallel workflow composed with `Promise.all` and filtered before it reaches context.

| Choose this | When |
|---|---|
| Classic tool calling | ≤3–4 chained calls, <10 tools, no shell available |
| Dynamic tool discovery | You want token savings but must not execute model-written code |
| Client-side Code Mode | You control the client and can ship a sandbox |
| Server-side Code Mode | You are the tool provider and want zero client changes |
| agent-codemode scripts | You already run a coding agent with authenticated MCP servers |

## What breaks on Linux, Windows, and claude.ai connectors?

Three limits are worth knowing before you build on this. On Linux and Windows, the Keychain path is skipped and Claude's OAuth tokens are read from `~/.claude/.credentials.json`; the config-based (stdio, API-key) servers work as-is. OAuth inheritance is Claude-only today. And `claude.ai` connectors are explicitly not supported — they are configured under a `claude.ai config` scope and reaching them would require impersonating Claude Code, which the tool declines to do.

The ecosystem context is also worth stating plainly. `agent-codemode` is a single-maintainer tool: MIT licensed, about 30 GitHub stars, roughly 31 npm downloads in the most recent month, with zero runtime dependencies and no vendor backing. By contrast, the general-purpose `@utcp/code-mode` library saw 5,637 npm downloads in the same period at 1,577 stars under MPL-2.0, and `cloudflare/mcp` sits at 903 stars under Apache-2.0. The pattern is far bigger than any one CLI — which is the point. Bet on the pattern, then pick the implementation that fits your credential situation.

## Where is this heading?

The strongest evidence that code mode is substrate rather than a trick is that independent teams arrived at the same architecture within a couple of quarters: Cloudflare's client- and server-side implementations, Anthropic's code execution with MCP and Programmatic Tool Calling, the UTCP library, Deno-sandboxed open-source variants, and production measurements from Agent Swarm — with Check Point's security research as the necessary counterweight. Hacker News discussion spans from September 2025 ("Code Mode: the better way to use MCP," 84 points) through the Deno-sandbox post in November 2025 (76 points) to a February 2026 thread on cutting Claude Code context consumption by 98% (570 points). A year of sustained discussion, not a single launch spike.

For most teams the practical sequence is small: install the CLI, run `agent-codemode servers` to see what your agent has already authenticated, and convert exactly one repetitive workflow — the one past ten items — into a script. Then measure it honestly and decide whether the sandbox complexity is worth it for the next one.

Two adjacent reads if you are still choosing an approach. If you want the lower-level version of this — driving MCP from bash, a one-shot SDK script over stdio, or `mcp-call` — see our [bash and stdio MCP scripting walkthrough](/posts/agent-codemode-mcp-scripts-2026/). If the problem is the number of servers rather than the number of calls, [MCP gateway and registry options](/posts/mcp-gateway-registry-comparison-2026/) is the more relevant layer. And if you have never stood up a server at all, start with the [MCP server tutorial](/posts/mcp-server-tutorial-2026/).

## FAQ

### What does "agent codemode MCP" actually mean?

It means letting the code your coding agent writes call MCP servers directly, instead of routing every call through the model's native tool-calling loop. The agent produces a script; the script makes the calls and returns one filtered result to the model. The token win comes from removing intermediate results from context and loading tool definitions on demand rather than upfront.

### Do I need to set up API keys or an OAuth flow?

Not with `agent-codemode`. It reads the OAuth token your coding agent already minted — the macOS Keychain entry `Claude Code-credentials`, or `~/.claude/.credentials.json` on Linux — and speaks JSON-RPC to the MCP server itself. There is no separate `.env`, no vault, and no `auth` step. Servers configured with API keys or stdio still work; only the OAuth inheritance is Claude-specific today.

### How much context does code mode actually save?

Cloudflare reports roughly 1,000 tokens for two tools covering about 2,500 API endpoints, versus 1,170,523 tokens for an equivalent native MCP server (−99.9%). Anthropic measured 150,000 tokens reduced to 2,000 (−98.7%). A live 40-call Linear workspace measured 262,159 characters reduced to 903 (−99.66%, 290×). Your own numbers will differ — measure call count, characters, re-reads, and wall clock rather than trusting the headline.

### Is it safe to execute code the model wrote?

It moves the trust boundary, so the sandbox becomes the security control. Check Point found five memory-corruption bugs in `workerd` (two Critical), including a Code Mode sandbox escape reachable from a single prompt injection; self-hosted deployments should update to `v1.20260619.1`. Run generated code in an isolate with no network egress and no environment variables, pass tools rather than credentials into the execution context, and keep the runner patched.

### When should I skip code mode entirely?

Skip it for three or four chained calls, fewer than ten tools, or any client without a shell. If you want token savings without executing model-written code, dynamic tool discovery is a credible alternative — Speakeasy reports up to 160× reduction with no code execution. Code mode pays off at bulk fan-out: past roughly ten calls, or when the same job should run on a schedule with no model in the loop at all.
