---
title: 'fx Coding Agent Review 2026: A Tiny, Open, Native Harness in Zig'
date: 2026-10-01T05:15:34+00:00
tags:
  - fx coding agent
  - vercel fx review
  - fx vs claude code
  - fx vs pi coding agent
  - zig coding agent
  - tiny coding agent harness
  - embeddable coding agent
  - libfx embed agent
  - fx acp server
  - fx ask json
  - vercel ai gateway coding agent
  - coding agent harness comparison 2026
description: "fx coding agent review: Vercel Labs' Zig harness ships a ~6.2 MiB native binary, four interfaces over one core, and a ~7K-token request floor."
draft: false
cover:
  image: "/images/fx-tiny-open-native-coding-agent.png"
  alt: "fx Coding Agent Review 2026: A Tiny, Open, Native Harness in Zig"
  relative: false
schema: "schema-fx-tiny-open-native-coding-agent"
---

The fx coding agent is Vercel Labs' experimental coding-agent harness and CLI, written in Zig and open sourced under Apache-2.0 in August 2026. It ships as a single native binary of roughly 6.2 MiB on Apple Silicon — no Node.js, no Python, no `node_modules` — and drives four interfaces (shell CLI, one-shot JSON, an ACP server, and a WebAssembly SDK) from one agent core. As of 2026-10-01 it is at 3,237 GitHub stars, v0.0.12, and is still explicitly labeled experimental with breaking changes between releases.

## What Is fx, and What Do "Tiny, Open, Native" Actually Mean?

The three words in the tagline are doing marketing work, but each maps to a concrete engineering decision you can verify in the repository.

**Tiny** refers to the runtime footprint, not the codebase. The macOS arm64 artifact is about 6.2–6.4 MiB, the Linux x86-64 build is 11.87 MB, and the README states a 7.8 MiB production ceiling enforced by release qualification on macOS arm64. Note the gap: the homepage advertises 6.39 MiB while the README quotes 7.8 MiB, because one is a representative Apple Silicon download and the other is a ceiling that every target must stay under. If you are sizing a container image, plan for 10–12 MB on Linux x86-64, not 6 MB.

**Open** means the full Zig source under Apache-2.0 — not a source-available license with a commercial carve-out. That matters less for cost than for auditability: the system prompt, the tool definitions, and the permission logic are all readable, which is unusual among shipping coding agents.

**Native** means machine code with no language runtime between you and the process, plus first-class WebAssembly targets. There is no interpreter startup, no package resolution step, and no dependency tree to reconcile on a build box.

For comparison, the same claim measured against an incumbent: `fx --help` completes in 2.7 ms on macOS arm64 where `claude --help` takes 112 ms, and the Claude Code installation it is being compared against consumes 197 MB. That is not a like-for-like comparison of capability, but it is a fair comparison of deployment cost, and deployment cost is the argument fx is actually making.

## fx at a Glance: Version, License, Binary Size, and Project Trajectory

Project facts checked against the GitHub API and npm registry on 2026-10-01:

| Attribute | Value (checked 2026-10-01) |
| --- | --- |
| Repository created | 2026-08-11 |
| First public tags | 2026-08-17 to 2026-08-18 |
| First HN launch thread | 2026-08-18, 318 points |
| Stars / forks / open issues | 3,237 / 364 / 250 |
| Language | Zig (29.8 MB of source) |
| License | Apache-2.0 |
| Latest release | v0.0.12, tagged 2026-09-30 |
| Release cadence | 8 releases in ~6 weeks (v0.0.5 → v0.0.12) |
| Contributors | 26 (top: 2,449 commits; second: 82) |
| npm package | `libfx`, 84 published versions, latest 0.0.12 |

A project at 3,237 stars six weeks after its first tag is moving fast, but it is a fraction of the incumbents. The same day's check found opencode at 211,204 stars, claude-code at 148,751, codex (Rust) at 127,446, and pi at 110,818. fx has roughly 1.5% of opencode's community. That is not a reason to avoid it — early adoption is where the leverage is — but it does mean your questions will be answered by a small team and 250 open issues, not a forum with a decade of accumulated answers.

The velocity is also a warning label. Eight releases in six weeks means the provider authentication flow, permission behavior, and command surface all changed substantially within days of launch. The v0.0.12 notes are a good illustration of two things at once: `fx sessions` against a 14,600-session store dropped from 95 seconds to 0.17 seconds (a 560x improvement, and evidence that the earlier version was unusable at scale), and libfx error codes for unsupported model settings were renamed — a breaking change to a public SDK in a point release.

Binary size by target, from the v0.0.5 release assets:

| Target | Size |
| --- | --- |
| macOS arm64 | 6.43 MB (6.19 MiB measured) |
| Linux arm64 | 10.13 MB |
| Linux x86-64 | 11.87 MB |
| macOS x86-64 | 12.31 MB |

There are no Windows artifacts, which rules fx out for a meaningful share of enterprise developers regardless of everything else in this review.

## Is the "10-Microsecond Cold Start" Real? What the Benchmarks Actually Measure

The 10-microsecond figure is the most quoted and least useful number in the launch material. It measures the time before fx accepts input — the point at which the process is alive and the terminal is ready for keystrokes. It does not measure the time before anything useful happens, and it is not the number the project enforces on itself.

What the project actually enforces is a 2 ms mean wall-clock budget. With `FX_BENCH=1`, fx parses arguments, dispatches the CLI path, and exits before TTY initialization; the Linux CI job runs six command paths (`fx`, `help`, `status --json`, `background --json`, `doctor --json`, `sessions --json`) 100 times each and fails the pull request if the mean exceeds 2 ms. That is the honest engineering claim: latency as a merge gate. A regression in startup cost cannot be merged, which is a stronger guarantee than any benchmark screenshot.

Then there is the number that a user actually experiences. Launch to first model request measures 31 ms on macOS arm64 — still an order of magnitude faster than the 112 ms it takes `claude --help` to print a help screen, but 3,100 times slower than 10 microseconds. Any article repeating "10 microseconds" without that context is repeating a framing, not a measurement.

### Where does startup latency actually matter?

It matters when you start agents rather than run them. Hierarchical review fleets of 50–100 agents, one agent per pull request in CI, evaluation harnesses that spin up a fresh agent per test case, and disposable sandboxes that provision a coding agent for a single task — in all of those, process startup is paid hundreds of times per hour, and the difference between a 6 MB binary and a 250 MB installation is the difference between a container that fits and one that does not. One practitioner running review fleets at that scale framed it bluntly: 6 MB versus 250 MB is "can do" versus "cannot."

If you are a human typing `fx` once and working for two hours, startup latency is noise. Buy fx for something else, or do not buy it.

## Four Interfaces Over One Core: CLI, fx ask --json, fx acp, and libfx

This is the part of the product that has no direct equivalent in the incumbent harnesses, and it is the real reason to pay attention.

**1. Interactive shell.** fx behaves closer to a Unix shell than an IDE embedded in a terminal. Sessions auto-name the terminal tab (session name, workspace fallback, model as context), so multi-window work stays legible; `fx sessions`, `fx session resume last`, and `fx session resume --id <id>` form a proper command group.

**2. One-shot JSON.** `fx ask --json` runs a single request and returns machine-readable output. For CI and scripting this removes the entire category of TUI-scraping hacks that teams otherwise write to drive a coding agent from a pipeline.

**3. ACP server.** `fx acp` speaks the Agent Client Protocol over stdio, letting an editor or host own the interface while fx owns sessions, prompts, tool calls, and permission requests. Vercel shipped `@ai-sdk/harness-fx` to connect fx into the AI SDK harness layer over ACP, which means the agent can be one component in a larger orchestrated system rather than the system itself.

**4. WebAssembly SDK.** `libfx` exposes `createFxAgent()` on fx-core.wasm (headless) and `createFxTerminal()` on fx-term.wasm (interactive), both embeddable in JavaScript hosts, including a browser tab. The live demo at fx.sh/try runs the agent in the page. The browser build requires JavaScript Promise Integration (Chrome/Edge 137+).

The comparison to the nearest minimalist competitor is instructive: pi has print mode, JSON, RPC, and a TypeScript SDK, but it needs a JavaScript runtime and cannot run in a browser at all. If embedding an agent in a web page is your requirement, the field narrows to exactly one mature option.

The Wasm surface is not the native surface. It omits native process execution, OS sandboxing, native MCP, subagents, skills, auto-upgrade, arbitrary WASI filesystem access, and web search. Embeddability is bought with capability, and the buyer should know which capabilities they are giving up.

## How Much Does the fx Harness Cost Per Request?

Megabytes are a one-time cost. Tokens are a per-turn cost, and a harness's system prompt and tool definitions are charged on every single request. This is where "tiny" stops being a marketing word and becomes a budget line.

An independent measurement pointed the undocumented `FX_GATEWAY_BASE_URL` / `FX_GATEWAY_CHAT_URL` environment variables at a local mock gateway and captured the exact request a two-word prompt produced in a clean environment:

| Component | Bytes | Share |
| --- | --- | --- |
| 17 tool definitions | 17,376 | 68.2% |
| Base system prompt | 5,531 | 21.7% |
| Runtime context | 2,456 | 9.6% |
| User prompt ("review this") | 59 | 0.2% |
| Total | 25,479 | 100% |

That is roughly 6,400–7,300 tokens of harness overhead before your prompt is considered. The comparable counted figure for Claude Code on the same measurement basis is 29,061 tokens. The gap is roughly 4x, and it is not because fx's system prompt is cleverer — it is because fx ships 17 tool definitions instead of dozens, and because MCP server schemas are not inlined.

The detail worth stealing regardless of which agent you run: fx ships `capability_search` and `mcp_select_tool` so that an MCP server's schemas load only when a tool is actually selected. Lazy tool loading is the single largest lever on per-request overhead in any agent with more than a dozen integrations, and a 68% tool-definition share shows what happens when you get it wrong.

You can reproduce the measurement yourself, and for reviewers who never install fx, the recipe is worth knowing: set the gateway base URL to a local mock, send one two-word prompt, and count bytes. Vendor claims are cheap; byte counts are not.

## Why Does fx Read ~/.claude/skills? The Skill-Catalog Tax

Here is the hidden cost. The same two-word prompt, measured in a normal user's HOME directory rather than a clean one, balloons from 25,479 bytes to 42,727 bytes — a 68% increase, with 16,247 of those extra bytes arriving as a single system message that lists other agents' skills.

fx scans 12 skill directories, including `~/.claude/skills`, `~/.codex/skills`, `~/.config/opencode/skills`, `~/.agents/skills`, and `~/.claw/skills`, and ships a catalog of skill names, descriptions, and paths on every turn. The catalog is capped by `skill_catalog_bytes` (default 16 KiB) and can be disabled entirely with `off`.

Two takeaways. First, if you already run Claude Code or Codex, fx inherits their skill directories by design — a deliberate interoperability choice, and also a per-turn tax you were not told about at install time. Second, if your per-request context budget is tight, `skill_catalog_bytes: off` is the first configuration change to make, before you touch the model.

## Which Models Can fx Use, and Where Does Billing Flow?

The default credential resolution order is: Vercel OIDC token → `AI_GATEWAY_API_KEY` → `fx login` OAuth → a saved API key. In practice that means every documented default path bills through Vercel AI Gateway, whose compiled default model is `moonshotai/kimi-k3`.

That is a real buying consideration, not a footnote. "Model-agnostic" here means the exits are documented and work, but the gravity is Vercel's gateway. The documented exits are:

- **Codex via ChatGPT subscription** — `fx login codex`, OAuth, tokens stored locally at `~/.fx/chatgpt-auth.json` and never sent through the gateway.
- **Grok via X Premium / SuperGrok** — `fx login grok`, xAI OAuth, stored at `~/.fx/grok-auth.json`, likewise never routed through the gateway.
- **Custom OpenAI-compatible connections** — named connections to any Chat Completions endpoint, which is how you reach Ollama, vLLM, or OpenRouter.

Two caveats on the local-model story. Local inference is configured as a custom connection, not as a one-flag mode, which is a heavier setup path than users coming from Ollama-first tools expect. And subscription OAuth is a personal-account mechanism: the `/fast` command on supported Codex models consumes ChatGPT credits at the higher Fast rate, which is fine for an individual and awkward for a team with a corporate billing policy.

On privacy, the picture is defensible: there is no product telemetry endpoint, and the auto-update check reads static release metadata every 30 minutes with no machine or installation identifier. It can be disabled with `FX_AUTO_UPGRADE=0`. Gateway-side, Vercel records model, token counts, latency, and cost but does not retain prompts after a request completes.

## Do fx Permissions Isolate Anything? Permissions vs Sandboxing

This is the section to read carefully, because conflating the two is how teams ship a vulnerability.

fx has three permission modes: `ask`, `auto` (default), and `full-access`. Auto mode runs routine work directly and escalates unresolved sensitive actions to a narrow safety-reviewer model — the same classifier shape, with the same caveats, as Claude Code's auto mode. Non-interactive runs (piped or redirected stdin) stay non-interactive and fail rather than waiting for an approval that can never arrive. That last behavior is correct for CI and surprising for anyone who assumed a prompt would block.

Permissions are a policy layer. They decide whether fx will attempt an action. They are not an isolation boundary. At the verified revision, the source says an absent sandbox setting means no sandbox, and changing permission mode does not select one. macOS has an optional OS sandbox; the source states no OS sandbox implementation was available on unsupported hosts, including Linux, in that release.

The practical consequence: on Linux, fx executes commands and touches files with the authority of the process it runs as. Secrets visible to that process are visible to the agent and to anything the agent invokes. If your threat model includes prompt injection from repository content, the mitigation is a container or a VM, not a permission mode.

Two more surfaces with the same trap. The Node addon `libfx` is a `.node` file — executable native code holding the host process's authority; N-API is not a sandbox, even though the headless core advertises no native tools and cannot launch commands or read workspace files unless the host grants that capability. And the skeptical framing from the security write-up deserves to be repeated: the launch materials do not establish that fx completes coding tasks faster, cheaper, more accurately, or more safely than competing agents, and no public fx-specific comparative benchmark existed at verification time. Smaller binary is a proven claim. Better agent is not.

## fx vs Claude Code vs pi vs opencode: Which Harness Fits?

The useful taxonomy in this space is not "which agent is best" but "how much does the harness decide for you." pi (earendil-works/pi, MIT, TypeScript) minimizes features: it refuses MCP, subagents, permission popups, plan mode, built-in todos, and background bash by design, shipping four default tools — read, write, edit, bash. fx minimizes footprint while keeping the features. Claude Code minimizes assembly time by shipping a finished platform.

| Harness | Optimization | Default posture | Best fit |
| --- | --- | --- | --- |
| Claude Code | Assembly time | Full platform, opinionated | Teams that want a finished product now |
| pi | Features | Four tools, refuses the rest | Developers who want the smallest possible decision surface |
| fx | Footprint | 26 documented tools, MCP, subagents, skills — compressed runtime | Embedding, CI, per-task agents, browser/editor hosts |
| opencode | Community breadth | Large plugin ecosystem | Teams optimizing for ecosystem size |
| tmux + scripts | Nothing | No harness | You are building the harness yourself |

On the spectrum from finished product to raw component, fx sits below pi despite having more features, because fx is explicitly built to be embedded in larger systems. That is the single most important sentence in this review: fx's feature list is not competing with Claude Code's; it is competing with `tmux` plus a shell script plus a provider API client.

The strongest critique of fx is a feature complaint rather than a footprint complaint: 26 tools with a dedicated tool for nearly every file operation is more surface area than a modern model needs, and the argument "just use fewer tools" has real merit. The counter-argument is that fx's lazy MCP loading means the extra built-ins cost 17 definitions in the base payload, not 40. Both positions are defensible; measure your own payload before choosing.

A note on honesty in the minimalism ledger: fx is small in runtime surface, not in codebase size. The `src/` tree holds roughly 693k lines of Zig across 560 files. A 6 MB binary is a compilation artifact, not evidence of a simple program.

## How Do You Install and Configure fx?

The verified install path is a single script: `curl -fsSL https://fx.sh/setup.sh | bash`, which installs to `~/.local/bin`. Building from source requires Zig 0.16.0+ and `zig build -Doptimize=ReleaseSafe`.

Authentication has exactly three documented routes: `fx login` for Vercel AI Gateway OAuth, `fx setup` for a Gateway API key, or `fx login codex` / `fx login grok` for subscription-based access.

Beyond auth, the configuration surfaces that matter in practice:

- **Sessions** — persistent, resumable, auto-named per terminal tab; deterministic replay is supported.
- **AGENTS.md** — scoped resolution, so project-level agent instructions apply without a global config file.
- **MCP** — servers are selected on demand through `capability_search` and `mcp_select_tool` rather than inlined into every request.
- **Skills** — installable capabilities plus the cross-agent skill directories discussed above; cap or disable the catalog via `skill_catalog_bytes`.
- **Subagents** — session-backed, for delegating narrow work without spawning a second process.
- **Memory** — persists to `~/.fx/memories.json` and is retrieved on demand rather than injected into every request, which is the right call for token economics.
- **Compaction** — in v0.0.12, a prompt-too-long error triggers compaction plus one retry instead of failing the turn outright.

Two design details worth praising because they are counter to the grain: `semantic_search` is explicitly lexical rather than an embedding index, and fx does not pretend otherwise; large tool results are held out behind byte-range handles read via `read_tool_result` instead of being pasted wholesale into context. Both are context-discipline decisions that reduce silent token burn.

## Who Should Use fx Today — and Who Should Wait?

Adopt fx now if you are building CI images, disposable evaluation containers, agent-per-task sandboxes, editor or ACP hosts, or anything that embeds an agent inside a larger program. The deployment argument is unambiguous: one executable removes `node_modules`, a virtualenv, a language package manager, and a separately provisioned runtime from the image, and upgrades and rollbacks become one file plus a checksum. When you spawn a hundred agents an hour, that is the whole story.

Wait, or plan around the gaps, if any of the following apply:

- **You need Windows.** There are no Windows artifacts.
- **You need isolation on Linux.** There is no OS sandbox; run fx inside a container or VM.
- **You need stability guarantees.** It is v0.0.x with breaking changes, including renames in the public libfx SDK.
- **You need the documented tool list to match the binary.** The docs list about 26 tools while a captured v0.0.7 payload contained 17, with different names (the docs say `shell`, the payload said `terminal`; web search arrived as `perplexity_search`). Take the docs as intent and the payload as fact.
- **You need local inference as a first-class mode.** It works, through a documented OpenAI-compatible custom connection, not a single flag.
- **You need proof it codes better.** Nobody has published that proof, including Vercel.

## Verdict: An Embeddable Agent Runner, Not a Daily Driver

fx is the most interesting thing that happened to coding-agent deployment in 2026, and it is not yet a replacement for your current assistant. Reviewers converged on the same conclusion from different angles: excellent as an embeddable harness, not yet a daily driver.

Judge it as what it is — an open implementation of a disposable, embeddable agent runner. The startup budget is enforced in CI. The request payload is a quarter of the incumbent's. The four interfaces over one core are a genuine category difference, and the WebAssembly surface has no equivalent in the minimalist competition. Against that: 250 open issues, no Windows, no Linux sandbox, v0.0.x churn, and a documented-versus-actual tool mismatch.

The right test is narrow and cheap. Point fx at a mock gateway, count the bytes your own configuration actually sends, and try `fx ask --json` in one pipeline that currently scrapes a TUI. If those two experiments pay for themselves, you have an answer. If your work is one developer in one terminal for two hours, the 10-microsecond number will never appear on your invoice.

## FAQ

**Is the fx coding agent production-ready in 2026?**
No, and Vercel does not claim otherwise. It is labeled experimental, it is on v0.0.x, and breaking changes ship in point releases — libfx error codes were renamed in v0.0.12. It is production-usable for embedded, CI, and per-task agent workloads where you control the version, and it is not a stable daily-driver replacement for a mature coding assistant.

**How large is the fx binary, and does size actually matter?**
For fx, plan for about 6.2–6.4 MiB on macOS arm64 and 10.13–11.87 MB on Linux, against a 7.8 MiB README production ceiling and no Windows build. Size matters when you start agents rather than run them: one executable removes Node, Python, and package managers from CI images, and a 50–100 agent review fleet becomes feasible where a 250 MB installation per agent is not.

**How much context does fx send before my prompt?**
Roughly 25.5 KB — about 6,400–7,300 tokens — for a two-word prompt in a clean environment, of which 68.2% is 17 tool definitions. In a populated HOME directory the same request grows to 42.7 KB because fx scans 12 skill directories, including `~/.claude/skills`, and ships a skill catalog each turn. Cap it with `skill_catalog_bytes` or disable it with `off`.

**Does fx sandbox the commands it runs?**
No, not in the sense of isolation. fx has `ask`, `auto`, and `full-access` permission modes, which are policy rather than a boundary; the source states that an absent sandbox setting means no sandbox and that no OS sandbox implementation was available on Linux in the verified release. The Node addon has the host process's authority. Treat fx as unsandboxed and wrap it in a container or VM.

**Can fx run local models like Ollama, and does it work offline?**
Yes to local models, through a named custom connection to any OpenAI-compatible Chat Completions endpoint (Ollama, vLLM, OpenRouter) rather than a dedicated local mode. Not fully offline: the default path bills through Vercel AI Gateway with `moonshotai/kimi-k3` as the compiled default model, and auto-update checks read release metadata every 30 minutes unless you set `FX_AUTO_UPGRADE=0` or use Codex/Grok subscription OAuth.
