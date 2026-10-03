---
title: "SiloLink MCP Bridge: Run Claude Code Sessions on Remote Machines"
date: 2026-10-01T01:48:47+00:00
tags:
  - SiloLink MCP bridge
  - SiloLink Claude Code
  - "@dsiloed/silo-link"
  - Claude Code remote session MCP
  - MCP bridge remote Claude Code sessions
  - claude code tmux remote session
  - multi-session Claude Code orchestration
description: "SiloLink is an MCP bridge that lets you drive Claude Code sessions on remote machines from Slack, Discord, Teams, or SMS. Setup, tools, and gotchas."
draft: false
cover:
  image: "/images/silolink-mcp-bridge-remote-claude-code.png"
  alt: "SiloLink MCP Bridge: Run Claude Code Sessions on Remote Machines"
  relative: false
schema: "schema-silolink-mcp-bridge-remote-claude-code"
---

SiloLink is a local Node daemon that exposes an MCP server on http://localhost:3579/mcp, so a Claude Code session running in tmux on a remote machine can register, poll for messages, and reply into a DSiloed conversation you drive from the web UI, Slack, Discord, Teams, or SMS.

That single sentence is the whole architecture, and it is also the source of every trade-off worth knowing before you install it. SiloLink does not replace Claude Code, does not proxy your model calls, and does not run a cloud sandbox. It is a bridge in the strict sense: your code, your filesystem, and your API credentials stay on the machine you already use, while the *conversation* lives in a vendor UI you can reach from a phone.

This guide covers the install and configuration path, the 14 MCP tools and which of them you should actually call, the poll-loop contract that keeps sessions alive, the headless permissions trap that trips up most first-time users, how SiloLink compares to Anthropic's first-party Remote Control and to self-hosted relays like agent-bridge and claude-relay, and where the trust boundary sits. Every technical claim below traces to the package README, the shipped source tree, or the npm registry.

## What Is SiloLink and What Problem Does the MCP Bridge Solve?

SiloLink (npm package `@dsiloed/silo-link`, CLI binary `silolink`) is an MIT-licensed local daemon that connects Claude Code sessions to [DSiloed](https://www.dsiloed.com) conversations. It was first published on 2026-03-26 and has shipped 98 versions through 2026-09-27, when version 1.19.23 landed. The npm registry reports Node 20 or newer as the engine requirement, and the package has accumulated 16,861 lifetime downloads with roughly 3,600-3,700 per month in steady state ([npm registry](https://registry.npmjs.org/@dsiloed/silo-link)).

The problem it solves is specific. You have a long-running Claude Code session on a box that is not your laptop - a build server, a home workstation, an always-on dev VM. You want to check on it, answer its permission prompts, and send it new instructions without SSH-ing in, without an open terminal, and without exposing the machine to the public internet. SiloLink turns that session into a chat participant you can message from anywhere the DSiloed conversation channels reach.

What SiloLink is not: it is not a model proxy, it is not a cloud coding environment, and it is not vendor-neutral. The daemon authenticates to the DSiloed backend and registers into that vendor's Agent Dashboard, which is the single biggest editorial caveat for anyone who wants a neutral bridge.

## How Does the SiloLink MCP Bridge Work Under the Hood?

The README's own diagram is the clearest explanation. A Claude Code process runs inside a tmux session and speaks MCP to SiloLink on port 3579. SiloLink simultaneously holds a WebSocket connection to the DSiloed backend over ActionCable and a REST control channel, exposing two channels to the server side: a ConversationChannel for messages and a ControlChannel for launch/stop commands.

Messages therefore flow in two directions at once. Inbound: a human types in the web UI, Slack, Discord, Teams, or SMS; the message lands on DSiloed; ActionCable pushes it to your daemon; SiloLink enqueues it per session; Claude Code picks it up on its next `remote_poll`. Outbound: Claude Code calls an MCP tool, SiloLink posts to the REST API, and the message appears in the conversation thread.

Three internal components do the work. A session manager keeps a registry validated across three maps every five minutes. A message queue holds a per-session inbound buffer with an acknowledgment protocol, which is why messages sent while a session is still starting are delivered on registration rather than lost. A launcher family - `claude-launcher.ts`, `gemini-launcher.ts`, `codex-launcher.ts` on top of `base-tmux-launcher.ts` - spawns and manages the tmux processes.

The documented defaults matter for debugging: HS256 JWTs with 24-hour validity auto-refreshed every 12 hours, WebSocket reconnection with exponential backoff from 1s to a 60s cap, echo prevention via tracked outbound message IDs plus prefix matching, a 30-second abort on every DSiloed API call, and idle session cleanup after one hour.

### What Actually Leaves Your Machine?

Source code, filesystem access, and model credentials do not transit the bridge. What does transit is conversation text: every prompt you send and every message Claude Code posts back travels through the DSiloed SaaS over an authenticated WebSocket. The credential that authenticates that channel lives in `~/.silolink/config.json` at mode 0600 as a JWT - the README states plainly that your password is never written to disk, only the token.

That is a real trust boundary, not a marketing one, and it is the design choice the self-hosted alternatives deliberately reject. Treat the config file as a production secret.

## What Do You Need Before Installing SiloLink?

Three prerequisites, none of them exotic:

- **Node.js 20 or newer.** The npm package declares `engines: { node: ">=20" }`.
- **tmux.** Every session SiloLink launches is a tmux session named `silolink-claude-<timestamp>`. Without tmux on the remote box, launching fails.
- **A DSiloed / Portablemind account** plus either a user login or an agent token, because the daemon has to authenticate before it can register sessions.

If you want the `mcp-remote` client path (covered below), `npx` needs to be able to fetch that package - it sees roughly 776,000 weekly downloads, so it is a well-trodden dependency.

## How Do You Install and Configure the SiloLink Daemon?

Installation is one command:

```bash
npm install -g @dsiloed/silo-link
```

Then run the configuration wizard:

```bash
silolink config
```

The wizard asks first whether this daemon runs as a **user** or an **agent**, and that answer is persisted as `identity_type`. It changes where spawned Claude Code sessions start, which matters because that directory is also where Claude Code reads `.mcp.json` and `CLAUDE.md` from.

| Identity | Credential path | Session launch directory | Best for |
|---|---|---|---|
| `user` (default) | Email/username + password, exchanged for a JWT at `POST /api/v1/users/login` | `projects_path`, or `repo_path` when a launch command supplies one | One human driving several remotes |
| `agent` | JWT pasted from the LLM Manager UI ("Generate SiloLink Token") | Staging directory `~/.silolink/staging/<env>/` | Machine identities, multi-agent fleets |

The user path is the single-environment remote-bridge case and typically pairs with `silolink setup-claude-md`, which injects the SiloLink protocol section into your `CLAUDE.md` once. The agent path never touches human credentials - useful when several agents share a host, since each gets its own staging directory instead of competing for one project directory.

Useful config keys: `claude_command`, `claude_working_directory`, `claude_auto_respawn`, `claude_idle_timeout_ms` (30,000 by default), `agent_provider` (`claude` by default, `gemini`, or `codex` - with `openai` accepted as an alias), `codex_command`, `codex_args`, `codex_resume_enabled` (false by default), and `mcp_port` (3579).

Start and inspect it with:

```bash
silolink start --daemon   # background
silolink status           # connection state and active sessions
silolink sessions         # list sessions
curl http://localhost:3579/health
# { "status": "ok", "sessions": 2, "cable": "connected" }
```

The health endpoint is the fastest way to separate "daemon down" from "Claude session down": `cable: "connected"` proves the ActionCable link is live even when zero sessions are running.

## How Do You Connect Claude Code to the SiloLink MCP Server?

SiloLink's MCP server is Streamable HTTP on `http://localhost:3579/mcp`, and the documented client snippet routes through the `mcp-remote` proxy:

```json
{
  "mcpServers": {
    "silolink": {
      "command": "npx",
      "args": ["mcp-remote", "http://localhost:3579/mcp"]
    }
  }
}
```

Why a proxy at all? Older and stdio-only MCP client configurations cannot speak HTTP to a server directly. The [mcp-remote](https://github.com/geelen/mcp-remote) package exists precisely to bridge that gap, which is why it carries about 1,608 stars and ~776k weekly downloads. Current Claude Code builds accept `--transport http`, which removes the proxy hop entirely; if you are troubleshooting a SiloLink connection and you are on a recent CLI, try the direct transport before debugging the proxy. The broader MCP transport landscape matters here too: the ecosystem has moved decisively to Streamable HTTP, [with roughly 93% of servers on that transport](https://nordicapis.com/10-interesting-mcp-statistics/) versus the deprecated SSE - so this is a client-side gap, not a server-side one. If the terms are still fuzzy, [API vs MCP: what actually differs](/posts/api-vs-mcp-difference-guide-2026/) is the right primer first.

### Where Should the MCP Config Live?

It must be in the directory Claude Code starts in - which, for a SiloLink-launched session, means the `projects_path` or `repo_path` the launcher chose. A config in your home directory will not be read by a session that starts in a project folder. This is the first thing to check when Claude Code reports no SiloLink tools.

## How Do You Launch Your First Remote Claude Code Session?

Two routes, both documented:

- **From the CLI:** `silolink launch` or `silolink launch -p "Work on the auth refactor"`.
- **From the web UI:** click **+** in the SiloLinks section of TeamChat, name the session, optionally add a prompt, then **Launch Session**.

The lifecycle is the same either way. SiloLink posts "Starting session..." then spawns the tmux process; Claude Code registers with the daemon and, roughly 20-30 seconds later, posts "Session ready!" as it enters the poll loop. You can watch it directly with `tmux attach -t silolink-claude-<timestamp>` and detach with Ctrl+B, D.

There is also an auto-launch path worth knowing about: when a message arrives on a SiloLink conversation with no active session, the daemon posts "Restarting session...", spawns Claude Code, and buffers the triggering message until the new session registers. That is what makes the bridge feel like a chat contact rather than a process you have to babysit.

Sessions are one per conversation, and multiple sessions run simultaneously. Idle sessions are cleaned up after one hour; `silolink stop` kills every tmux session and completes the agent sessions on DSiloed.

## What Is the SiloLink Poll-Loop Contract?

This is the part every integration gets wrong. SiloLink's own documentation recommends a non-blocking poll loop, and the canonical order for a session that is reattaching to existing work is:

1. `remote_register` - register the session and create or attach a conversation. Returns `{ session_id, conversation_id, conversation_url }`.
2. `remote_load_context` - fetch prior history and the last `claude_resume_id`. Returns `{ success, conversation_id, resume_id, message_count, history }`.
3. `remote_poll` - non-blocking check for the next message, typically in a ~3 second loop.

The ordering is not cosmetic. Session continuity depends on `remote_load_context` returning the stored `resume_id`; skip it and a respawned tmux pane comes back with no idea what it was doing. If you run multiple Claude Code sessions against one repo, the same discipline applies to your session identity - the [multi-session guide for Claude Code](/posts/message-your-other-claude-code-sessions/) covers the identity side of that problem.

`remote_poll` is preferred over `remote_wait_for_command` for a concrete reason stated in the tool docs: a blocking call that gets cancelled can lose a message, while a poll simply returns `{ success: true, pending: true }` and tries again. The trade-off is latency and idle token spend - you are paying for a loop instead of being woken by a push.

## Which of the 14 SiloLink MCP Tools Do You Actually Use?

The bridge exposes 14 tools. Medians matter here: MCP servers carry [a median of about five tools each](https://nordicapis.com/10-interesting-mcp-statistics/), so SiloLink sits well above typical surface area.

| Tool | Blocking? | Use it for |
|---|---|---|
| `remote_register` | No | Registering the session, attaching a conversation |
| `remote_load_context` | No | Restoring history and `resume_id` after a spawn |
| `remote_notify` | No | Fire-and-forget progress messages |
| `remote_ask` | Yes | Posting a question and waiting for a human reply |
| `remote_poll` | No | The recommended main loop |
| `remote_check_messages` | No | Draining all pending messages at once |
| `remote_wait_for_command` | Yes | Blocking wait (docs prefer `remote_poll`) |
| `remote_sessions` | No | Listing active sessions |
| `remote_unregister` | No | Unregistering and cleaning up |
| `remote_workspace_create` | No | Creating an isolated git worktree |
| `remote_workspace_claim` | No | Claiming files with conflict detection |
| `remote_workspace_check` | No | Auditing claims across all sessions |
| `remote_workspace_merge` | No | Merging the worktree branch back |
| `remote_workspace_list` | No | Listing active workspaces |

In practice a session uses five or six of these on every turn and the workspace tools on demand. `remote_ask` is the one to use sparingly in headless mode: it blocks, and an unanswered question stalls the session until the timeout.

## How Do You Reach Claude Code From Slack, Discord, Teams, or SMS?

Because the conversation lives on DSiloed, the delivery channel is the vendor's problem, not yours. The README names the DSiloed web UI, Slack, SMS, and Discord explicitly, and the [interactive demo's architecture diagram](https://www.dsiloed.com/apps/silolink-demo) labels the PortableMind node "Web UI / Slack / Teams / SMS". Messages typed in any of those surfaces arrive at the same conversation, and replies from Claude Code appear in the same thread.

The honest framing: this is a hosted conversation layer, not a Telegram bot you wrote yourself. You do not configure webhooks or bot tokens for the chat side - you configure one DSiloed account and pick a channel inside it. If your requirement is "one bridge, no vendor in the message path," this is where SiloLink loses, and peer-to-peer tools win.

## How Do You Run Parallel Sessions Without Clobbering Each Other?

SiloLink gives each session an optional git worktree plus advisory file claims:

```
Session A: feature/auth  ──►  ~/.silolink/worktrees/myapp/feature/auth/
Session B: feature/api   ──►  ~/.silolink/worktrees/myapp/feature/api/
```

Call `remote_workspace_create({ repo: "/home/user/myapp", branch: "feature/auth" })` and you get back `{ worktree_path, branch }`. `remote_workspace_claim({ files: [...] })` returns `{ claimed, conflicts }`, `remote_workspace_check({})` returns `{ all_claims }` across every session, and `remote_workspace_merge({})` returns `{ success, merged_branch }` after folding the branch back.

Read the word "advisory" carefully. The claims are soft locks with cross-session conflict notifications - they tell the other session that a file is taken, but they do not block a write. Two agents that ignore the warning will still clobber each other. If you are new to worktree isolation as a concurrency primitive, [the worktree guide](/posts/claude-code-worktrees-guide-2026/) is the mechanical background; here the point is that isolation is the hard guarantee and the lock is only a signal.

## Why Is `--dangerously-skip-permissions` Not Enough for Headless Sessions?

This is the highest-value gotcha in the whole setup, and it is documented from the shipped binary rather than the public schema. On every session spawn, SiloLink's `ClaudeLauncher.ensureBypassPermissionsConsent()` writes two things:

- `projects.<cwd>.hasTrustDialogAccepted` in `~/.claude.json` - pre-clearing the workspace trust dialog, which never saves trust for the home directory.
- a top-level `skipDangerousModePermissionPrompt: true` in `~/.claude/settings.json`.

The second write is the one people miss. Without that consent on file, Claude Code still re-prompts on the "dangerous pattern" class - `rm -rf`, `sudo`, and friends - even when launched with `--dangerously-skip-permissions` and even when the in-session footer shows the bypass mode as on. The footer reflects the mode; the consent key is the gate, and Claude Code's internal check reads it at the top level of the settings object, not nested under `permissions`. The published settings schema does not document the key as of Claude Code 2.1.x.

Verify it directly:

```bash
python3 -c 'import json; print(json.load(open("'"$HOME"'/.claude/settings.json")).get("skipDangerousModePermissionPrompt"))'
```

If that prints `False` or `None`, restart silolink so the launcher rewrites it. The writes are idempotent and shallow-merge, so theme, plugins, and your `permissions` block survive.

Some prompts are unavoidable by design: Claude Code keeps a hardcoded circuit breaker for catastrophic patterns like `rm -rf /` that re-prompts regardless of settings. Those need a human, which is exactly when the chat channel earns its keep.

If you would rather not bypass at all, the least-privilege alternative is to allow only the bridge's own tools:

```json
{ "permissions": { "allow": ["mcp__silolink__*"] } }
```

## How Do You Operate and Troubleshoot SiloLink?

| Symptom | Likely cause | Check |
|---|---|---|
| Claude Code sees no SiloLink tools | `.mcp.json` not in the session's start directory | `silolink status`, then confirm the launch dir |
| `mcp-remote` hangs or refuses the OAuth callback | Proxy transport issue | Retry with `--transport http` on a current CLI |
| Session ready but silent | Poll loop never started | `tmux attach` to the session, inspect the transcript |
| Repeated re-prompts for dangerous commands | Missing `skipDangerousModePermissionPrompt` | The `python3` check above |
| `cable: "disconnected"` in `/health` | Token rejected or network down | Re-run `silolink config`; backoff caps at 60s |
| Session died mid-task | Idle cleanup after one hour | Set `claude_auto_respawn`, confirm `remote_load_context` is used |

For usage and cost tracking, `silolink report-usage --cli claude` (also `gemini` and `codex`) posts the token usage of a session you ran yourself under your DSiloed user, which makes a Stop or SessionEnd hook a natural fit.

## SiloLink vs Anthropic Remote Control vs agent-bridge vs claude-relay

Anthropic's first-party [Remote Control](https://code.claude.com/docs/en/remote-control) shipped in February 2026 and overlaps SiloLink on the core use case - driving a locally executing Claude Code session from a phone. The differences are structural.

| Dimension | SiloLink | Anthropic Remote Control | agent-bridge | claude-relay |
|---|---|---|---|---|
| Transport path | Vendor SaaS (ActionCable + REST) | Vendor SaaS | Peer-to-peer over SSH | Loopback MCP + SSH local-forward |
| Sessions | Multiple per daemon, one tmux each | Multiple, default capacity 32 | Per-machine agent inboxes | One relay, many registered clients |
| Chat surfaces | Web UI, Slack, Discord, Teams, SMS | claude.ai/code, iOS, Android | Agent-to-agent channels | Terminal agents only |
| Auth model | HS256 JWT, 24h, 12h refresh | Pro/Max/Team/Enterprise subscription | Local SSH keys | Local registry file |
| Works with Bedrock/Vertex/custom `ANTHROPIC_BASE_URL` | Yes | No | Yes | Yes |
| Message delivery | Non-blocking poll (recommended) | Vendor-managed | Push channel events | Content-free Stop hook |
| License / maturity | MIT, 98 releases since 2026-03 | Proprietary | Open source, 8 stars, created 2026-04-12 | Open source, 4 stars, active 2026-09-30 |

The Remote Control constraints are worth stating plainly: it requires a Pro, Max, Team, or Enterprise subscription and does not support API keys; it is unavailable behind Amazon Bedrock, Google Cloud Agent Platform, Microsoft Foundry, and any custom `ANTHROPIC_BASE_URL` gateway; and it needs the workspace trust dialog accepted from a project directory, never from home. It also cannot be combined with `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` or `DISABLE_GROWTHBOOK`. SiloLink has none of those constraints, because it is not in the model path at all - which is precisely why it survives in an environment Remote Control refuses to run in.

Where the self-hosted tools win is the trust boundary. [agent-bridge](https://github.com/EthanSK/agent-bridge) keeps config, keys, inboxes, and logs on your own machines and pushes events rather than polling, with an explicit lesson from production: Claude Code's plugin host reaps idle plugins based on MCP tool-call frequency on stdio, so a channel-only plugin gets killed after each notification. [claude-relay](https://github.com/gvorwaller/claude-relay) refuses plaintext LAN WebSocket traffic outright and carries everything inside SSH. If "no vendor sees my prompts" is a hard requirement, choose one of those and accept more setup.

## Can You Bridge Non-Claude Agents Like Codex and Gemini?

Yes, and this is the section most coverage of SiloLink skips. `agent_provider` accepts `claude` (the default), `gemini`, or `codex` - the OpenAI CLI, with `openai` accepted as an alias - and the source tree ships `gemini-launcher.ts` and `codex-launcher.ts` alongside the Claude launcher. You can override per launch with `silolink launch -a codex`.

The Codex path differs in an important detail: it does not use the `npx mcp-remote` bridge. SiloLink writes `[mcp_servers.*]` tables with `url` plus `http_headers = { Authorization = "Bearer <jwt>" }` into `$CODEX_HOME/config.toml` and launches with `env CODEX_HOME=<home> codex ...`, because Codex speaks native streamable HTTP. Its tools are also named differently - `silolink__remote_register` rather than `mcp__silolink__remote_register`. `codex_resume_enabled` defaults to false, and `codex_args` defaults to `["--dangerously-bypass-approvals-and-sandbox"]`. The README states the Codex integration was validated against codex-cli 0.141.0.

## SiloLink MCP Bridge: Who Should Use It and Who Should Not

Use it if you want to command long-running coding sessions on remote machines from a chat client, you are comfortable with your conversation text transiting a vendor backend, and you value the multi-session orchestration plus usage reporting that a first-party one-human-one-session tool does not provide.

Do not use it if your prompts are regulated data, if you need the message path to stay inside your network, or if you need a bridge that is independent of the vendor that built it. In those cases the SSH-carried relays are the honest answer.

One number puts the security context in perspective: [38.7% of MCP servers where the auth method could be determined have no authentication at all, and 53% rely on long-lived static secrets](https://nordicapis.com/10-interesting-mcp-statistics/). Security concerns are also the top adoption blocker at 64% of surveyed software organizations. SiloLink at least keeps its MCP endpoint on loopback and gates the cloud credential behind a 0600 config file - which is the minimum bar, not a premium feature. If you are still assembling your tooling, [the practical MCP server shortlist](/posts/best-mcp-servers-for-developers-2026/) is a reasonable starting point.

## FAQ

### What is a SiloLink MCP bridge used for?

It connects Claude Code sessions running on a remote machine to a DSiloed conversation, so you can launch, monitor, and instruct those sessions from a web UI, Slack, Discord, Teams, or SMS without SSH or a public inbound port. The MCP server is local on port 3579; the conversation layer is hosted.

### Does SiloLink send my source code to DSiloed?

Source files and model credentials stay on your machine. Conversation text - the prompts you send and the messages Claude Code posts back - transits the DSiloed backend over an authenticated WebSocket, and the authenticating JWT is stored locally at `~/.silolink/config.json` with mode 0600.

### Why does Claude Code still ask for permission when launched with `--dangerously-skip-permissions`?

Because the bypass flag sets the mode but does not record consent. Claude Code's internal check reads a top-level `skipDangerousModePermissionPrompt` key in `~/.claude/settings.json`, which SiloLink writes on each spawn via `ensureBypassPermissionsConsent()`. If that key is missing, dangerous-pattern commands still prompt even though the footer shows bypass as on.

### Should I use `remote_poll` or `remote_wait_for_command`?

Use `remote_poll`. It is non-blocking and returns `{ success: true, pending: true }` when there is nothing new, so a cancelled loop cannot lose a message. `remote_wait_for_command` blocks until the next message and is documented as the less safe option.

### How do I keep continuity when a Claude Code session restarts?

Call `remote_load_context` immediately after `remote_register`. It returns the stored `claude_resume_id` along with `message_count` and `history`, which is what lets a freshly spawned tmux session resume the prior conversation instead of starting cold. Combine it with `claude_auto_respawn` and a worktree per session for the multi-agent case.
