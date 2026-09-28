---
title: "Wake Review: The Coding Agent Session Manager Your Agents Can Read"
date: 2026-09-28T19:13:24+00:00
tags:
  - coding agent session manager
  - wake macos app
  - claude code session manager mac
  - wake-mcp mcp server agent history
  - resume claude code session from a gui
  - sqlite fts5 agent session search
  - combine claude code and codex history
  - read-only agent transcript indexer privacy
  - agent session history over ssh remote
  - wake vs ctx
description: "Wake indexes 22 coding agents into one read-only Mac app, then hands that history back to your agents over MCP. A hands-on review of v0.8.5."
draft: false
cover:
    image: "/images/wake-macos-coding-agent-session-manager.png"
    alt: "Wake Review: The Coding Agent Session Manager Your Agents Can Read"
    relative: false
schema: "schema-wake-macos-coding-agent-session-manager"
---

Wake is a free, MIT-licensed macOS app that indexes the local sessions of 22 coding agents — Claude Code, Codex, Cursor, Gemini CLI and 18 more — into one read-only SQLite index searchable in under a millisecond. It also ships `wake-mcp` and `wake-cli`, so your other agents can query that archive themselves.

## Why does a coding agent session manager exist at all in 2026?

Because almost nobody runs one agent any more, and the reasoning behind your code is not in git.

JetBrains' 2026 Developer Ecosystem Survey, covering more than 15,000 professional developers between May and July 2026, found 90% using AI coding agents at work at least weekly and 68% using them daily. Adoption is also spread across competing tools rather than converging on one: Claude Code reached 39% adoption at work, up from 18% in January 2026, while Codex tripled from 3% to 16% and Cursor slipped from 18% to 12%. Multi-tool use is the norm — 59% of developers now run three or more AI programming tools and the average developer runs 2.3 at once, according to JetBrains' AI Pulse data, with 70% of engineering teams pairing Cursor with at least one other AI tool.

That fragmentation is not cosmetic. Every agent writes its own private format into its own hidden directory, and the two-tool default means your history is already split in half on day one.

| Agent | Where sessions live | Format |
|---|---|---|
| Claude Code | `~/.claude/projects/**/*.jsonl` | JSONL append per message |
| Codex CLI | `~/.codex/sessions` + `state_5.sqlite` | JSONL plus SQLite state |
| Cursor | `~/.cursor/projects/**/agent-transcripts` + IDE `state.vscdb` | JSONL plus SQLite blob store |
| Gemini CLI | `~/.gemini/tmp/**/chats` | JSON |
| OpenCode | `~/.local/share/opencode/opencode.db` | SQLite |
| Hermes Agent | `~/.hermes/state.db` and `profiles/*/state.db` | SQLite |
| DeepSeek Harness | `~/.dsh/sessions/**/session[.vN].jsonl[.zstd]` | zstd-compressed JSONL |

Losing that is worse than losing a chat log. As one published review of Wake frames it: the commit message says what changed, but the session says why the first two approaches did not work, which library version broke, and what the error text actually was. git history is complete for the code and empty for the reasoning. And the volume is now large — JetBrains found roughly 47% of work code is fully written by agents, with over half of developers writing less than 20% of their code by hand and 22% generating more than 80% of it with agents.

## What is Wake, and what is it deliberately not?

Wake is a native desktop application written in Rust on GPUI 0.2, the same UI framework that powers Zed, with `gpui-component` for the widget layer. It presents a three-pane workbench — projects and agents, session list, transcript — with a ⌘K command palette. The repository is `iAmCorey/Wake`, created 2026-08-18, with v0.1.0 shipping the next day and v0.8.5 on 2026-09-27.

The project is genuine by the numbers, not by marketing. As of 2026-09-28 it had 1,374 stars, 87 forks, 5 open issues and 2 watchers, is MIT licensed, and is overwhelmingly Rust (2.5 MB of Rust source against 35 KB of Python and smaller amounts of Shell, PowerShell and Swift). It shipped 42 releases in the 39 days between v0.1.0 and v0.8.5 — roughly one release per day — with 2,593 cumulative release-asset downloads, 181 commits from its sole author and another 10 committed under the name "claude". That star count also moved fast: 352 stars in early September, 684 by 2026-08-30 per 4Geeks, 731 with 48 forks per reveneau on 2026-09-03, about 780 per AlphaSignal, then 1,374 four weeks later. Roughly a 4x climb.

What matters more than the numbers is the architectural claim:

| Wake is | Wake is not |
|---|---|
| A read-only index over other tools' files | An agent runtime — it never runs a model call |
| A viewer, searcher and launcher | A code editor or an IDE replacement |
| An MCP server and CLI other agents can query | A summariser or an embeddings store |
| MIT licensed (`iAmCorey/Wake`) | A notarised, one-click install |

That last row of the "is not" column is the practical one: Wake never supplies a model, never executes a task, and never writes to another tool's data. It reads what Claude Code and Codex already wrote, normalises it, and — if you ask — reopens the session in your terminal. Sessio is the rival that does run agents, over the Agent Client Protocol; Wake deliberately does not.

## How does Wake read 22 agents without touching their files?

It ships one adapter per agent inside `crates/wake-core/src/adapters` — separate modules for claude, codex, qoder, copilot, cursor, cursor_ide, opencode, kiro, gemini, pi, omp, grok, grok_group, kimi, antigravity, dsh, hermes, openclaw, codebuddy, craft, devin and zcode, plus shared `parse_utils` and `sqlite_ro` helpers. Every agent directory is opened read-only, and credential files such as `auth.json` are never read.

The supported list as of v0.8.5 covers Claude Code, Codex CLI, Qoder CLI, Copilot CLI, Cursor (CLI transcripts plus IDE chat and composer history), OpenCode and OpenCode 2, Kiro, Gemini CLI, Pi, Oh My Pi, Grok Build, Kimi Code, Antigravity CLI, DeepSeek Harness, Hermes Agent, OpenClaw, CodeBuddy, WorkBuddy, ZCode, Craft Agents and Devin. Notably, Wake respects the environment overrides these tools themselves use: `QODER_CONFIG_DIR`, `HERMES_HOME`, `OPENCLAW_STATE_DIR`, `CODEBUDDY_CONFIG_DIR`, `WORKBUDDY_CONFIG_DIR`, `ZCODE_STORAGE_DIR` and `XDG_DATA_HOME`.

Two details are worth crediting because most competitors paper over them. First, the README's Model column is only filled for the agents whose local data actually records which LLM was used, and the Via column (CLI versus IDE extension versus desktop app) only for Codex, Hermes, OpenClaw and Craft Agents. A dash means the source data lacks the field, not that Wake is missing a feature. Second, the performance baseline is stated plainly: about 310 sessions and 800 MB of JSONL indexed in roughly five seconds, with subsequent launches effectively instant thanks to mtime-based incremental scanning, and search results under a millisecond.

The privacy stance is equally specific and, importantly, testable: no background HTTP client runs, the only network actions are a user-initiated update check against Wake's own public GitHub Release metadata and the SSH/rsync you configure yourself, and Wake's index at `~/Library/Application Support/wake/wake.db` can be rebuilt from scratch — with your stars, pins and delete-tombstones stored in a separate table that survives a rebuild.

## What does Wake's search do that grep cannot?

The index is SQLite FTS5 with **trigram** tokenisation, which is a specific and checkable decision rather than a marketing adjective. Trigram indexing is what makes CJK text searchable alongside code substrings like `useEffect(`, because it matches on character triples instead of word boundaries. A hit opens the transcript at the matched message — not at the top of a file the way a `grep -r ~/.claude` session dumps you. Session titles are searched too, with title hits ranked first, and results favour recently active sessions.

The trade-off is recall on paraphrased queries. Wake indexes the literal record and nothing else; there is no embedding layer and no summarisation step. If "find the session where I fixed the auth timeout" needs to work without the word "timeout" appearing anywhere, that is where ctx's optional local semantic mode, `valpere/session-indexer` (bge-m3 via Ollama) or crispy-recall differ. For code and error text — the queries people actually run against agent history — literal matching is the right default and the failure mode is visible rather than silent.

### How does one-click resume actually work?

Wake reopens the session in Terminal or iTerm at the original project directory, invoking the agent's own resume command — `claude --resume`, `codex resume` and so on. Linux and Windows builds use native terminal hosts.

There is one honest limit: Craft Agents, WorkBuddy and ZCode are desktop applications with no CLI resume path, so Wake indexes their sessions but cannot relaunch them. Those rows appear without a resume action rather than failing at the click.

## The feature nobody talks about: can your agents read your history?

This is the second product inside Wake and the reason it is not just another viewer. Wake bundles `wake-mcp`, a hand-written stdio JSON-RPC MCP server, exposing exactly five read-only tools:

| MCP tool | What it returns |
|---|---|
| `wake_search` | Full-text search over titles and transcripts, as `wake://session/<key>#<seq>` references |
| `wake_list_sessions` | Recent sessions scoped by project, agent, time window or starred status |
| `wake_get_session` | One transcript as compact Markdown with `[seq N]` markers, paginated via `from_seq` |
| `wake_list_projects` | Projects with indexed sessions, most recently active first |
| `wake_list_memories` | The memory files agents keep for themselves, grouped by project |

There is no delete tool and no star tool. The one write the server performs is resolving the default index path inside Wake's own data directory. Setup snippets live in Settings → Connect; `wake-mcp setup` prints them from a terminal. For Claude Code the line is:

```
claude mcp add --scope user wake -- "/Applications/Wake.app/Contents/MacOS/wake-mcp"
```

Codex takes an `[mcp_servers.wake]` block in `~/.codex/config.toml`. Alongside the MCP server, `wake-cli` exposes the same surface to shells — `wake-cli sessions --project "$PWD" --limit 5`, `wake-cli search "<term>" --project "$PWD"`, `wake-cli show <key>` — and its output is asserted byte-for-byte against the MCP tools in the test suite apart from a trailing newline. A connected MCP client and a shell script therefore see identical answers.

Two things make this more than a nice-to-have. `wake-cli refresh` can be scheduled from launchd or a systemd timer so the index stays current while the app is closed, and every listing reports how recent the index is; reading a transcript parses the agent's files directly, so it does not depend on that last scan. And `npx skills add iAmCorey/Wake` installs a bundled agent skill, with docs describing a Claude Code `SessionStart` hook that injects the project's recent sessions into the agent when it starts. v0.8.0's Copy Handoff adds a ready-to-paste note containing the session id and both ways to read it.

That is the workflow change: a session written by Claude Code can be retrieved by Codex by searching for the error string, which is exactly the multi-tool case the JetBrains numbers describe. Every rival viewer in this niche is a dead end for another agent.

## What else does the app show you?

**Insights** is the unexpected feature. A GitHub-style activity heatmap with streaks, hour/weekday/month breakdowns, and Agents/Projects/Models leaderboards switchable between sessions, tokens and prompts — plus an "Agents asking Wake" board showing how often each agent actually used Wake's MCP tools or CLI in the last seven days. That last board is a self-reporting adoption loop: the tool tells you whether your agents are really using it.

**The Memory page**, added in v0.8.0, is a quiet land grab. It puts each agent's own auto-memory — Claude Code auto-memory, Codex memories and per-session summaries, ZCode project memory — next to the instruction files you write by hand: `CLAUDE.md`, `AGENTS.md`, `GEMINI.md`, `.cursor/rules`, `.kiro/steering` and `copilot-instructions.md`, all in one searchable read-only view. It answers a question that gets harder with every tool you add: what did I tell this agent, and did the other one get told the same thing?

**Cleanup** lets you filter sessions by date, agent and project from the sidebar, sort by size, preview, then move files to Trash — with a tombstone recorded so a deleted session stays deleted after an index rebuild, plus a cleanup history.

## Do remote hosts over SSH actually work?

Yes, with asterisks. Settings → Remote hosts probes a remote for known agent directories and mirrors only those with rsync into `remotes/<host>/` under Wake's own data directory. Sessions get an `@host` badge and resume via a copied `ssh -t <host> 'cd <project> && codex resume <id>'` command.

The limitations are documented rather than hidden: SSH must work without prompts, because Wake runs without a terminal and can never answer a passphrase prompt; rsync is needed on both ends; remote sessions are read-only and cannot be trashed; Codex-style path overrides are not honoured on the remote; and Windows remotes are unsupported. Open issue #56 is the first real-world failure — remote sync breaks when a Windows local cache path containing `C:\` is parsed as an SSH host.

## How do you install Wake, and why does macOS block it?

macOS 14 (Sonoma) or later is the primary platform, shipped as a Universal Binary for Apple Silicon and Intel. Download `Wake-<version>-macos.zip` from GitHub Releases, unzip, and drag `Wake` to Applications. Or build from source: `git clone https://github.com/iAmCorey/Wake`, then `scripts/make-app.sh` (add `--universal` for the combined build). Linux gets `.deb` and tar.gz for amd64/arm64 with a rootless `install.sh`, experimental since v0.2.5; Windows ships a `.zip` for x86_64, experimental since v0.2.7. On both, the data layer, rendering and search are fully tested, while terminal-resume targets and desktop integration have seen less real-desktop mileage.

The build is ad-hoc signed and not notarised, so Gatekeeper blocks the first launch of a downloaded copy. Right-click → Open, or `xattr -d com.apple.quarantine Wake.app`. The Windows binary is unsigned too and may trip SmartScreen. And there is still no Homebrew cask: the formulae.brew.sh API returns nothing for "wake", Homebrew/homebrew-cask has no `wake.rb`, and open issue #6 asks for a formula. Today the install story is "release zip plus a quarantine flag" or "clone and build with a Rust toolchain".

## What is not supported, and why?

- **Windsurf and Trae** — they encrypt their local data, so there is nothing readable on disk.
- **Amp, Factory (Droid) and Warp** — sessions live in the cloud, not locally.
- **Antigravity CLI** — indexed at metadata level only, for the same encryption reason.
- **Reasonix** — stores sessions locally but has not been mapped yet.

That is six named gaps across a field of roughly 28 agents, reported in the README rather than discovered by users. It is the behaviour you want from a tool whose entire value depends on format fidelity — and it is more honest than the universal-coverage claims common in this category.

## How does Wake compare with ctx, Sessio and the rest?

This is the crowded part of the story. At least nine other projects already own some version of the scan-index-search loop, which means search is not a differentiator.

| Tool | Stars | Licence | Form factor | What it adds over Wake |
|---|---|---|---|---|
| **Wake** | 1,374 | MIT | Native macOS (GPUI) | 22 adapters, one-click resume, MCP + CLI |
| **ctx** (`ctxrs/ctx`) | 1,140 | Apache-2.0 | CLI, cross-platform | `ctx blame` maps code lines to sessions, `ctx graph`, `ctx sift`, optional local semantic search |
| **Session Explorer** | 43 | none | Local web app | Runs in a browser, no native platform work |
| **session-indexer** | 42 | Apache-2.0 | Go CLI | Per-project semantic search via bge-m3 embeddings |
| **codex-history-viewer** | 39 | MIT | VS Code extension | Tagging, import and export of an archive |
| **Sessio** | 28 | none | Desktop (TypeScript) | Runs and forks agents over ACP, Telegram bridging |
| **Universal Session Viewer** | 18 | AGPL-3.0 | Electron | Continuation-chain detection, AI summaries |
| **Session Manager** | 10 | MIT | Tauri (cross-platform) | Fork-tree views, first-class remote SSH sources |

ctx is the real rival and deserves the comparison. It is CLI-first rather than a GUI, ships `ctx search`/`show`/`locate`/`blame`, positions explicitly against lossy "agent memory" products, and claims 50x better token efficiency than raw transcript search. Its Show HN thread hit 65 points and 43 comments in July 2026. Where it goes beyond Wake is code attribution — blaming lines of code back to the session that produced them — and where Wake goes beyond it is the GUI, the one-click terminal resume, and the breadth of 22 adapters against a narrower source list.

Sessio defines the other edge of the category: it can start and continue sessions inside the app, stream reasoning and tool calls, answer permission prompts in chat, and fork a session to a different agent while carrying context across. That is "browser plus runner"; Wake has staked out "browser plus agent-readable index". Both are defensible, and they are different products.

The honest summary is that Wake's defensible parts are the adapter count, the resume flow that puts you back in a real terminal in the right directory, and the MCP/CLI surface — not the search box.

## Is 22 agents a feature or a maintenance liability?

It is both, and the changelog shows the treadmill. DeepSeek Harness broke when dsh 0.1.6 changed its format and was fixed in 0.8.3. Cursor stopped writing token counts, so those columns went quiet. Codex's background threads — guardian auto-review, `/review`, compaction and memory-consolidation — were being indexed as if they were real sessions until 0.6.6 taught Wake to skip them from the first line's metadata, while `spawn_agent` sub-agents are kept and nested under their parent. An unidentifiable file stays visible rather than being hidden, on the principle that a stray row is better than a missing conversation. Craft Agents' duplication problem is handled the same way: because a Claude connection saves every conversation into Claude Code's history too, Wake hides the engine copy while the Craft session exists and lets it reappear as a Claude Code session if the Craft session is deleted.

Every one of those files is a private, undocumented implementation detail of a tool on its own release cadence. Wake has 42 releases in 39 days and effectively one maintainer, which is the source of both its responsiveness and its risk. reveneau named the strategic problem when the project was still at v0.2: the index can drift whenever an agent ships a new version.

There is a second-order risk worth naming. Wake has **no Hacker News presence at all** — the Algolia API returns zero stories and zero comments for `iAmCorey Wake` — so its 4x star climb happened through GitHub trending and aggregator coverage rather than adversarial scrutiny. The near-identical Show HNs for Cass, Dexicon, Darc and a generic local-first Claude Code history tool sank at 2 to 4 points. Almost nobody has argued with Wake's claims, which is why the claims worth testing are the operational ones: index drift after an agent update, remote mirror limits, and Gatekeeper friction.

## So should you install Wake?

**Install it if** you run two or more coding agents and have ever asked which project that fix was in; you want the same history searchable from Claude Code, Codex and a shell script; your agent directories are on macOS and you care that nothing is written back to them; or you want a literal, verifiable index of the real record instead of a summarised memory layer.

**Skip it, or wait, if** you are Windows- or Linux-first and need first-class desktop integration rather than an experimental port; you need notarised, Homebrew-installable software for a managed fleet; you need semantic recall on paraphrased queries rather than literal search; you need agents *running* inside the app, which is Sessio's territory; or your agents are Windsurf, Trae, Amp, Droid or Warp, whose data Wake cannot legally or practically reach.

For everyone in the first group, the two-minute version is this: download the release, clear the quarantine flag, let it scan, then add `wake-mcp` to your other agents. The scan is the setup. The MCP connection is the part that changes how you work.

## FAQ

### Is Wake free and open source?

Yes on both counts. The repository at `github.com/iAmCorey/Wake` is MIT licensed and the prebuilt binaries are free to download, in contrast with tools in this niche that ship AGPL-3.0 or PolyForm Noncommercial terms. That matters if you want to embed session search in an internal tool or ship it inside a company workflow.

### Does Wake replace Claude Code, Codex or Cursor?

No. It never runs an agent and never supplies a model. It reads what those tools have already written to disk, indexes it, and can reopen a session in your terminal using the agent's own resume command — `claude --resume`, `codex resume` and so on. Sessio is the rival that does run agents, over the Agent Client Protocol; Wake deliberately does not.

### Does Wake modify my Claude Code, Codex or Cursor files?

No. Every agent directory is opened read-only and Wake never writes to another tool's files or databases, and credential files such as `auth.json` are never read. Your stars, pins and delete-tombstones live in Wake's own index at `~/Library/Application Support/wake/wake.db`, which can be rebuilt from scratch without losing them. That is verifiable in the source and against your own `~/.claude` before you trust it.

### Can another agent read my Wake history?

Yes, and it is the most interesting part of the tool. It bundles `wake-mcp`, a read-only MCP server exposing five tools — `wake_search`, `wake_list_sessions`, `wake_get_session`, `wake_list_projects` and `wake_list_memories` — plus `wake-cli`, which prints identical output for shells. Add it to Claude Code with `claude mcp add --scope user wake -- "/Applications/Wake.app/Contents/MacOS/wake-mcp"`, or to Codex through a `[mcp_servers.wake]` block in `~/.codex/config.toml`. One caveat: fresh search and listing results come from Wake's index, so either keep the app running or schedule `wake-cli refresh` from launchd or a systemd timer.

### Can Wake search Chinese, Japanese or Korean text, and does it use AI?

It searches CJK text and code substrings such as `useEffect(` in the same query, because the FTS5 index uses trigram tokenisation rather than word boundaries, and a result opens the transcript at the matched message instead of the top of a file. It does not use AI: there is no embedding model and no summarisation layer, deliberately. If you need semantic recall on paraphrased queries, that is where ctx's optional local semantic mode, `valpere/session-indexer` with bge-m3 via Ollama, or crispy-recall differ from Wake's literal index.
