---
title: "Agent CodeMode Review: How Coding Agent MCP Scripts Call Your Connected Servers"
date: 2026-10-01T06:39:48+00:00
tags:
  - coding agent mcp scripts
  - agent codemode
  - agent-codemode
  - code mode mcp
  - mcp code mode
  - call mcp servers from a script
  - claude code mcp oauth token keychain
  - claude code credentials keychain security
  - mcp token savings code mode
  - mcporter vs agent-codemode
  - cloudflare code mode mcp
  - anthropic programmatic tool calling
  - mcp tool call token overhead
  - typed mcp client typescript
  - mcp streamable http session
  - mcp stdio json-rpc from script
  - mcp credential blast radius
  - mcp servers registry statistics 2026
  - when to use code mode mcp
description: "Agent CodeMode review: a coding agent's MCP scripts call servers it already authenticated — 40 tool calls collapse into one script."
draft: false
cover:
  image: "/images/agent-codemode-mcp-scripts.png"
  alt: "Agent CodeMode Review: How Coding Agent MCP Scripts Call Your Connected Servers"
schema: "schema-agent-codemode-mcp-scripts"
---

agent-codemode (janwilmake/agent-codemode) is a MIT-licensed Node 18+ CLI and TypeScript library that lets a script your coding agent writes call the MCP servers that agent has already authenticated. It reads the OAuth tokens and stdio configs Claude Code already created, speaks Streamable HTTP or stdio JSON-RPC directly, and returns an exact answer instead of routing every intermediate result through the model.

## What Is agent-codemode and Which Number Does It Lead With?

The project is small, and it is deliberately pitched as small. Its own README says: "Be clear about what is and isn't new here." What it does is give a coding agent a way to skip the tool-call loop. Instead of the model calling 40 MCP tools in sequence, feeding each result back into context, the agent writes one script that calls those tools as ordinary functions and prints one result.

The headline measurement comes from a live 39-ticket Linear workspace, where the author fetched every In Progress ticket with its full body and counted occurrences of "mcp" across all of them. The two paths, as reported in the README:

| Path | Data into context | Round trips |
|---|---|---|
| Sequential MCP tool calls | 262,159 characters (~65,500 tokens) | 40 |
| One script | 903 characters (~226 tokens) | 1 |

That is roughly 290x less data entering the context window, or a 99.66% reduction for that task. The author is honest about the arithmetic: the token figures assume a 4-characters-per-token heuristic, and he states explicitly that the ratio, not the absolute token count, is the durable part of the claim.

That honesty matters, because the same number is routinely quoted without it. The 99.66% figure is a single-task context measurement, not an end-to-end saving. The closest independent production measurement in this space — Agent Swarm's live workflow-triage run from July 2026 — reports about 99.2% fewer tokens for the data-gathering step but only roughly half the total cost for the whole scheduled task, because the agent still has to reason over the summary and decide what to escalate. Any review that repeats 99.66% without that caveat is over-selling a real result.

## Why Do Coding Agents Need MCP Scripts at All?

Anthropic's engineering write-up on code execution with MCP names the two taxes that compound every time a model talks to a tool:

1. **Tool definitions loaded upfront.** Every connected server's schema spends context before the model has read the user's request.
2. **Intermediate results passed through the model.** When call B needs call A's output, call A's full output must enter context just to be copied into the next request.

A two-hour sales transcript flowing through two tools is roughly 50,000 extra tokens, and a large enough document breaks the context window entirely rather than merely costing money. Cloudflare's Kenton Varda and Sunil Pai put the same point more bluntly in September 2025 when they named the pattern: LLMs are better at writing code to call MCP than at calling MCP directly. Their reasoning is plausible and worth repeating — models have seen enormous amounts of real TypeScript and comparatively few contrived tool-call transcripts, and chained calls are exactly where the direct path hurts, because every intermediate value has to be materialized into the conversation.

The scaling problem is structural, not incidental. Bifrost and Maxim's controlled benchmark across 508 tools on 16 MCP servers measured 75.1 million input tokens for classic MCP against 5.4 million for code mode on the same query set — a 92.8% reduction, with both configurations passing 65 of 65 test queries. Their framing is the cleanest available: MCP token cost scales with catalog size, not with work done. A six-turn workflow across a hundred tools pays the full definition cost six times before producing a three-line answer.

## How Does agent-codemode Read the Credential Your Agent Already Minted?

This is the actual product, and it is the only row in the project's own comparison table that differs from every neighbour.

On macOS, Claude Code stores its MCP OAuth tokens in a single Keychain item with the service name `Claude Code-credentials`. Its `mcpOAuth` map is keyed by `<serverName>|<urlHash>` and carries `serverUrl`, `accessToken`, `refreshToken`, `clientId`, `issuer` and `expiresAt`. On Linux and Windows, the same OAuth material lives in `~/.claude/.credentials.json`. Separately, `~/.claude.json` (both top-level and per-project `mcpServers`) plus `.mcp.json` hold the stdio and API-key server definitions, and agent-codemode expands `${VAR}` references the way Claude Code does.

Because those are files and Keychain entries rather than an API, setup is zero. Every competing tool makes you re-authenticate: Cloudflare takes bindings you configure, MCPorter keeps its own vault at `~/.mcporter/credentials.json` and requires `mcporter auth` per server, and VoidMCP wants tokens registered through a CLI. agent-codemode reads the token your agent already minted and needs no auth step at all.

That difference decides behaviour more than it looks like it should. An agent mid-task reaches for whatever works right now, not for a tool that needs you to complete an OAuth flow first. Inheritance is what makes the script the path of least resistance — which is precisely why the security section below is not a footnote.

## How Do You Install and Run It?

The package is `agent-codemode@0.1.1`, published under MIT, requiring Node 18 or newer, with **no dependencies at all**. The tarball is 146,160 bytes unpacked across 52 files, and the published binaries are `agent-codemode` and its shorter alias `codemode`, both pointing at `dist/cli.js`.

Four subcommands cover the surface:

| Command | What it does |
|---|---|
| `codemode servers` | Lists the MCP servers discovered from your agent's config and credentials |
| `codemode tools <server>` | Lists that server's tools |
| `codemode call <server> <tool>` | Invokes one tool directly |
| `codemode types --all` | Reads each server's live `tools/list` and emits a typed `.ts` module per server plus an index barrel |

Exit codes are conventional and worth scripting against: `0` on success, `1` for credential, transport or usage errors, and `2` when the tool itself reported `isError`. That third code is the kind of detail that separates a tool designed for scripts from a CLI that merely happens to be scriptable.

## What Does the Typed API Look Like?

`types --all` is the part that changes how the agent writes code. It queries each server's live tool list and generates a declaration-merged module set, so generated modules merge into an `McpServers` interface. The practical consequence is that a side-effect import is the entire setup, wrong tool names are compile errors, and argument types are checked at the call site with no cast anywhere:

```ts
import "agent-codemode/types"; // declaration-merges McpServers
import { mcp } from "agent-codemode";

const issues = await mcp.linear.listIssues({ team: "ENG", state: "In Progress" });
```

The TypeScript API mirrors the CLI: an `mcp` proxy object, `callTool`, `listTools`, `resultText`, and `McpClient.fromClaudeCode`. On the wire there is nothing exotic — for remote servers it performs the standard Streamable HTTP MCP handshake (`initialize`, capture `Mcp-Session-Id`, `notifications/initialized`, then `tools/call`), and for stdio servers it spawns the configured subprocess and speaks newline-framed JSON-RPC. The registry data supports that transport choice as the mainstream one: of 30,375 unique servers catalogued as of September 2026, 54.8% are remote-only and 17,584 remote endpoints use streamable-http against just 1,073 on the deprecated SSE transport.

## What Does a Multi-Server Script Actually Look Like?

The worked shape is one script, several servers, no `.env` file. The agent writes something close to this and runs it as a subprocess:

```ts
import { mcp, resultText } from "agent-codemode";

const tickets = await mcp.linear.listIssues({ state: "In Progress" });
const bodies = await Promise.all(tickets.map(t => mcp.linear.getIssue({ id: t.id })));
const hits = bodies.flatMap(b => resultText(b).match(/mcp/gi) ?? []);

console.log(`${tickets.length} tickets, ${hits.length} mentions of "mcp"`);
```

Forty round trips collapse into one process, one context insertion, and an exact count. Note the shape of what the model sees: a single line of output. Note also what it does not see: any ticket body at all.

## Why Are claude.ai Connectors Not Supported?

They are refused on purpose, for two stated reasons. First, the token for a claude.ai connector such as Gmail or Calendar exists only in claude.ai's backend — there is nothing local to read. Second, the connector endpoint rejects any request whose `clientInfo.name` contains the string "claude", so the only way to make it work would be impersonating Claude Code. The project declines to do that, and a review should credit the refusal rather than list it as a missing feature.

The verified support matrix is narrower and more honest than most tools' claims: remote HTTP MCP over OAuth works, self-hosted remote MCP works, plugin-scoped MCP servers such as `plugin:slack:slack` work, API-key HTTP and SSE servers configured with headers work, and stdio servers configured with env vars work. Linux and Windows OAuth are explicitly labelled best-effort and unverified, with the README asking for help confirming a full run.

There is also a live failure mode worth knowing before you build on it. Claude Code rotates refresh tokens single-use (the README cites anthropics/claude-code issue #59460), so a stale token held or cached by a script can be rejected outright. The documented recovery is to start Claude Code or run `claude mcp login <server>`. That is the credential-inheritance strategy's structural weakness: your reliability depends on a store another vendor controls.

## Is It Safe? The One-Keychain-Item Problem

This is the most useful section in the whole repo, and it is the strongest original contribution a review of it can make.

The project's `SECURITY.md` documents its own contract: it reads credentials but never writes, refreshes, rotates or deletes them; it never transmits a token anywhere except to the server that issued it; it never caches one (it re-reads the store on every call, because Claude Code rotates on its own schedule); it never prints secret material; and it raises loudly on expiry instead of silently degrading into an empty result.

Then it discloses the part that matters. On macOS, every MCP OAuth token a Claude Code session holds sits in one Keychain item that is readable **without any prompt** by any process running as you that Claude Code could have spawned — every hook, every local MCP subprocess, every `npx` package one of those pulls in, and every shell command an agent decides to run. As the author puts it, that is a property of the credential store, not of this package, and removing the package does not change it.

The consequence deserves stating plainly: if a production MCP server is one `npx` away from an untrusted postinstall script, that is worth knowing deliberately rather than discovering later. The doc's practical rules follow from it — treat your agent's MCP server list as a blast radius, and prefer read-scoped tokens wherever a server offers scopes.

The supply-side context makes the blast radius bigger than it sounds. The official MCP registry held 30,375 unique servers as of 2026-09-10, roughly triple its May 2026 size, and it records **no auth method, no security review and no uptime check**. About 62% of listed servers have only a single version and roughly 36% have not been updated in three months or more. Publishing is also top-heavy: the top 10 publishers hold 17.7% of all servers and 16,356 publishers have exactly one.

agent-codemode's own risk surface is genuinely small, and that is the fair reading. There is no network listener, no daemon, no background process and no persistent state: it runs, reads a credential, makes one JSON-RPC call, and exits. The one new capability is convenience. The doc names what convenience costs — a script holding your Linear token can close tickets at 3 a.m. with nobody reading the diff — which is why the example keeps destructive actions behind an explicit flag such as `--post`. Copy that pattern before you copy anything else.

## What Is Genuinely New Here, and What Is Not?

Almost nothing is new, and the project says so. Code mode was named by Kenton Varda and Sunil Pai at Cloudflare in September 2025. Cloudflare already collapsed an API of more than 2,500 endpoints — which would cost over 2 million tokens if each were a tool — into two tools, `search()` and `execute()`, in roughly 1,000 tokens of context, and `@cloudflare/codemode` recorded 625,217 npm downloads in the week of 2026-09-23..29. Anthropic ships Programmatic Tool Calling inside the Claude Developer Platform, reporting 37% fewer tokens on its research tasks plus a small accuracy gain, and its acknowledgements credit Cloudflare, LLMVM and "Code Execution as MCP". MCPorter (openclaw/mcporter) reached runtime, typed clients and per-server CLI generation first, with 5,039 stars and 538,183 weekly downloads.

The distribution gap frames the whole story in one line:

| Package | npm downloads, week of 2026-09-23..29 |
|---|---|
| @cloudflare/codemode | 625,217 |
| mcporter | 538,183 |
| mcp-use | 37,016 |
| @utcp/code-mode | 1,051 |
| @tmustier/code-mode-mcp | 10 |
| agent-codemode | 10 |

What remains after subtracting all of that is a 33-file, zero-dependency Node CLI whose only novel move is reading a file — or a Keychain item — that somebody else already wrote. That is a real feature, and it is also the maintenance risk, because the file it reads is controlled by another vendor.

## Is "agent codemode" One Project or Three?

Search for the phrase and you will land on three unrelated things. Disambiguating them is not pedantry; it prevents installing the wrong package.

| Project | Language | What it is |
|---|---|---|
| janwilmake/agent-codemode | TypeScript | The subject of this review: a CLI plus typed library that inherits your coding agent's MCP credentials |
| datalayer/agent-codemode | Python (BSD-3-Clause) | Different design entirely: generates typed Python bindings from MCP servers, runs agent code in a sandbox (eval, monty, docker, jupyter, colab, kaggle, modal variants), and can re-export the generated tools as an MCP server. 4 stars, 2 forks, last push 2026-09-26 |
| @cloudflare/codemode | TypeScript | Cloudflare's runtime for the same pattern, part of the cloudflare/agents monorepo (5,699 stars, last push 2026-09-30) |

## How Does agent-codemode Compare With Its Neighbours?

| | agent-codemode | MCPorter | @cloudflare/codemode | @utcp/code-mode |
|---|---|---|---|---|
| Credentials | Inherited from your agent (no auth step) | Own vault at `~/.mcporter/credentials.json`, `mcporter auth` per server | Bindings you configure | Config file + MCP server wiring |
| Sandbox | None — it is your shell | None | Yes (sandbox executor, approve/reject/rollback) | Isolated VM sandbox with timeouts |
| Typed clients | `types --all` emits per-server modules with declaration merging | `emit-ts` (`.d.ts` or client mode) | Typed OpenAPI-derived surface, `search()`/`execute()` | TypeScript against configured providers |
| Extra surface | 4 CLI verbs, 1 library | `generate-cli`, `serve` bridge, transport pooling, auto-OAuth, stable `--json` envelopes | Connectors, audit records, saved snippets, AI SDK / TanStack AI / Vite entry points | Multi-protocol (MCP, HTTP, File, CLI) orchestration |
| Maturity | 30 stars, 0 forks, ~10 weekly downloads, no commits since 2026-08-19 | 5,039 stars, 347 forks, pushed 2026-10-01, ~538k weekly downloads | ~625k weekly downloads, actively maintained | 1,578 stars, 108 forks, ~1,051 weekly downloads |

MCPorter does everything agent-codemode does and considerably more. The single difference agent-codemode claims is the credential row, and the README says so rather than pretending otherwise. One naming trap for readers following older links: the repo now lives at `openclaw/mcporter` (site `mcporter.sh`), and `steipete/mcporter` links redirect there.

## What Does the Evidence Say About Over-Claiming?

The most rigorous public benchmark in this space is `@tmustier/code-mode-mcp`, run against a deterministic 10-tool MCP server with claude-opus-4-8:xhigh, 8 task shapes across 4 conditions and 5 runs each — 160 scored runs, every one returning the exact expected answer. Its findings cut against a global mode switch:

- **There is no universal call-count threshold.** Six independent small lookups favoured direct tool calls; an 8-step dependent cursor chain and a 19-call list-and-fan-out stage favoured code mode. The recommendation is per-stage routing.
- **The wins are real where data volume is real.** One task fetched four datasets concurrently: direct MCP returned about 148,000 characters of raw records to the model where code mode returned about 100. Another took 8 model/tool cycles direct against one exec cell. A third aggregated 18 result blocks inside a single cell.
- **Hybrid cost is not zero.** Guided-hybrid median initial context was 4,328 tokens versus 3,261 for direct-only and 2,484 for code-mode-only. The discovery and guidance surface has to be paid for.
- **Unguided hybrids made avoidable mistakes** — guessing nested tool names, misparsing `result.content[0].text`, making redundant verification calls — and needed route changes. That is the direct counter-argument to "just ship a skill and behaviour changes by default."

Worth noting for citation hygiene: that benchmark repo is now deprecated in spirit (its description points readers to `nicobailon/pi-mcp-adapter`'s `mcpScript`), with 1 star and a last push of 2026-07-16. Cite it as evidence, not as a tool recommendation.

## When Should You Write a Script Instead of Calling a Tool?

Use task shape, not a call count. The heuristic below is drawn from the benchmark above and from Agent Swarm's published operational rule, which is the clearest version available: script it when a job means 10+ similar tool calls, a bulk fan-out, or heavy intermediate data you would otherwise discard; stay with direct tool calls for a handful of calls or when intermediate values must be in context.

| Write a script when | Call the tool directly when |
|---|---|
| 10 or more similar calls to the same server | A handful of calls, done |
| Bulk fan-out or parallel fetch across many records | The model must read each result to decide the next step |
| Heavy intermediate data you would otherwise discard | Intermediate values legitimately belong in context |
| A long deterministic chain where each step is mechanical | Approvals, ambiguous semantics, error recovery |
| The same job will run again tomorrow | Rich native results the model should see verbatim |

## What Is the Second Win Nobody Prices?

The script is a file. It runs tomorrow from cron or as a CI gate with no model and no tokens involved at all — which is the answer to the reasonable objection that code mode on top of MCP on top of code is a useless extra layer. Agent Swarm's numbers back the compounding effect: roughly 150 reusable scripts, about 25,000 executions in 30 days, and around 70% of their schedules using at least one. The counterweight is the author's own warning about a script that holds a live token and acts unattended.

## Should You Depend On It? The Maintenance Reality

Treat this as a verdict input, not a closing footnote. The repository was created 2026-08-18, last pushed 2026-08-19, and has been untouched since. It has 30 stars, 0 forks, 33 tracked files, 681 KB, no GitHub releases ever, and one open issue that is a promotional invite rather than a bug report. npm shows only versions 0.1.0 and 0.1.1, last modified 2026-08-18, and roughly 10 downloads in the week of 2026-09-23..29. The Show HN launch reached 4 points and 0 comments, so there is no community validation to imply. Linux and Windows support is explicitly unverified by the author. And a tool whose entire value proposition is reading a credential store that Anthropic controls will rot the moment that store changes — which the single-use refresh rotation issue already demonstrates.

## How Do You Copy the Idea in an Afternoon?

The core is small enough to reimplement, and that is a more durable takeaway than a verdict on a 30-star package. The whole trick, harness-agnostically:

1. Locate the agent's credential store — the Keychain item `Claude Code-credentials` on macOS, `~/.claude/.credentials.json` elsewhere for OAuth, plus `~/.claude.json` and `.mcp.json` for stdio and API-key servers.
2. Pick the entry for the server you want, keyed by name and URL hash.
3. For a remote server, speak Streamable HTTP MCP: `initialize`, capture `Mcp-Session-Id`, send `notifications/initialized`, then `tools/call`.
4. For a local server, spawn the configured subprocess and speak newline-framed JSON-RPC.
5. Print the result and exit non-zero on tool errors.

There is one behavioural piece that is not code at all, and it is the mechanism the author identifies behind the token ratio: an agent that knows the option exists writes one script, and an agent that does not keeps making twenty tool calls. That is why the project ships `.claude/skills/agent-codemode/SKILL.md`. The skill, not the library, is what changes the default.

## Verdict: Borrow the Pattern and the SECURITY.md

agent-codemode is a 30-star, single-maintainer, zero-dependency CLI whose one genuinely differentiated move is inheriting credentials the agent already holds. The token ratio it measures is real; the generalization is narrower than the number suggests, and the independent 160-run benchmark shows why — task shape, not call count, decides whether code mode wins, and unguided hybrids pay for their own guidance. If you already run MCPorter, you are not missing a capability. If you are designing a harness and want your agent to reach for scripts by default, read this repository's `SECURITY.md` first: the blast-radius disclosure about the single Keychain item is the most valuable artifact here, and it applies to your setup whether or not you install the package. Borrow the pattern, inherit the security reasoning, and hold the dependency at arm's length until it has commits newer than August 2026.

## FAQ

**What is agent-codemode in one sentence?**
It is a Node 18+ CLI and TypeScript library that lets a script your coding agent writes call the MCP servers that agent already authenticated, by reading the credentials Claude Code already stored instead of asking you to log in again.

**Is the 99.66% token saving claim reliable?**
It is a real measurement on one Linear task (262,159 characters over 40 tool calls versus 903 characters in one script), but it is a context-window measurement rather than an end-to-end saving. Independent production data shows about 99.2% fewer tokens for the data-gathering step and roughly half the total cost for the whole job, because the agent still reasons over the result.

**Does agent-codemode create a new security hole?**
No, and its own `SECURITY.md` says so. On macOS every MCP OAuth token lives in one Keychain item readable without a prompt by anything a Claude Code session can spawn. The package makes that existing exposure legible rather than creating it — removing the package does not change the exposure.

**How is it different from MCPorter or Cloudflare Code Mode?**
The only real difference is credentials: agent-codemode uses the token your agent already has, while MCPorter keeps its own vault and requires `mcporter auth` per server, and Cloudflare uses bindings you configure. On every other axis — typed clients, maturity, distribution, sandboxing — MCPorter and `@cloudflare/codemode` are ahead by orders of magnitude.

**When should I write an MCP script instead of calling tools directly?**
When a job needs 10 or more similar calls, a bulk fan-out, a long deterministic chain, or heavy intermediate data you would otherwise discard — and when the job will run again tomorrow without a model. Keep direct tool calls for a handful of calls, semantic decisions, approvals, and cases where intermediate values genuinely belong in the model's context.
