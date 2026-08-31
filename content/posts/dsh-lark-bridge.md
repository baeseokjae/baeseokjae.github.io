---
title: "DSH Lark Bridge: Chat with DeepSeek Harness Agents on Feishu/Lark"
date: 2026-08-30T13:01:45+00:00
tags:
  - deepseek-harness
  - feishu
  - lark
  - dsh-plugin
  - ai-agents
  - developer-tools
description: "The DSH Lark bridge lets you chat with DeepSeek Harness agents on Feishu/Lark. This guide compares the top plugins and walks through a QR-scan setup with no public network."
draft: false
cover:
    image: "/images/dsh-lark-bridge.png"
    alt: "DSH Lark Bridge: Chat with DeepSeek Harness Agents on Feishu/Lark"
    relative: false
schema: "schema-dsh-lark-bridge"
---

A DSH Lark bridge is a plugin that connects DeepSeek Harness (DSH) coding agents to Feishu or Lark group chats, so you can send a task from your phone, DM, or a group and the bridge runs it in the correct Harness project and session. You do not need a public IP, domain, webhook, or NAT tunnel: the bridge keeps a WebSocket long connection to the Feishu/Lark Open Platform and relays tool-call approvals, questions, files, and status updates back to a single native card.

## What Is a DSH Lark Bridge (and Why Use One)

DeepSeek Harness (the `deepseek-ai/deepseek-harness` repository) is a plugin-architecture coding-agent framework built around the motto "Everything is a Plugin." It sits around a ~204k-star ecosystem and sees active development pushes through late August 2026. Because DSH is a local, self-hosted agent harness, it historically lived on your workstation or a private server — reachable only from a terminal.

A DSH Lark bridge changes that. It publishes a lightweight bot into Feishu (China) or Lark (international) and maps the messaging surface onto your harness:

- **A group or topic becomes a task inbox.** Each Feishu/Lark group maps to a Project, and each topic or thread maps to an isolated Session.
- **A message becomes one DSH Agent task.** Send a request, and the harness picks it up and executes it.
- **A single native card carries the whole lifecycle.** The bridge updates one card as work progresses, routes tool-call approvals and structured `ask_user_question` prompts back to the reader, and relays files and images.

The practical payoff is that you can drive a serious, long-running coding agent from a phone or a group chat — approve a risky file write, answer a clarifying question, watch intermediate tool calls stream in — without ever opening a terminal. For a solo developer with a laptop, or a small team sharing one harness host, this collapses the distance between "I had an idea" and "the agent did the work."

## Prerequisites: DeepSeek Harness, Node.js, API Key, and a Feishu/Lark Account

Before you can bridge DSH into Feishu/Lark, you need the pieces the harness and the plugins all assume are already running. The requirements are consistent across the leading bridge plugins:

| Requirement | Typical version / note |
|---|---|
| DeepSeek Harness (dsh) | Tested against 0.1.0-rc.6 (still a developer preview) |
| Node.js | ≥ 22 for most plugins; several require ≥ 24 |
| `DEEPSEEK_API_KEY` | Configured in the dsh harness so agents can call the model |
| Feishu / Lark account | A tenant where you can create a custom app / bot |
| Package manager | `pnpm` for build-from-source projects, `npx` for registry installs |

The single most common onboarding blocker is not the model key — it is the networking story. Historically, any bridge that wants to receive events from Feishu needed a public endpoint. The modern generation of DSH–Feishu bridges sidesteps this entirely by using Feishu's WebSocket long-connection API through the official `@larksuiteoapi/node-sdk`, so **no public IP, domain, webhook, or NAT tunnel is required** — a detail we will unpack in the WebSocket section below.

## The 6 Leading DSH↔Feishu/Lark Bridge Plugins Compared

As of August 2026 the ecosystem has produced at least half a dozen serious bridge projects. They differ meaningfully in setup friction, security model, reliability guarantees, and how aggressively they isolate workspaces. Here is the comparison matrix.

| Plugin | Setup | Networking | Session / isolation | Security model | Standout feature |
|---|---|---|---|---|---|
| `imetn/dsh-lark-bridge` | `pnpm dlx ... setup --project "$PWD" --brand larkoffice\|lark` | WebSocket, no public server | Group→Project, topic→isolated Session | Card-button approval, structured question routing | Bidirectional controller with card detail presets (compact / standard / developer) |
| `bihangchi9-creator/dsh-lark-bridge` | `pnpm setup` — **must build first** (lib/ is git-ignored) | WebSocket | One group = one folder `<workspaceRoot>/<chatId>`; per-message `.attachments/<messageId>/` | QR registration wizard, allowlist /allow /disallow | Strict file isolation; persistent per-chat sessions survive restarts |
| `chenxin105/dsh-lark-bridge` | `dsh plugin --profile web add github:<user>/dsh-lark-bridge` | WebSocket | Inbound private-chat → in-process agent | Credential-resolved `tenant_access_token` with auto-refresh; `role('secret')` fields | Model-facing tools: send message, read doc, Bitable read/write, call agent |
| `amlyczz/dsh-lark-link` | npm `dsh-lark-link`; `/lark setup` scan QR (30s) | WebSocket | Per-chat context | Allowlist `open_id` control, `groupPolicy` (open/mention/keywords/reply), denyList | Zero message loss: outbound Outbox + inbound WAL replay; `/doctor` diagnostic ZIP |
| `ailoushu666/dsh-feishu-bridge` | `npx @deepseek-ai/dsh plugin --profile web add git+https://...` | WebSocket | Same DSH Session reused per chat, threads independent | Option-question cards for `ask_user_question` | Real-time 🔧 tool-call hints via throttle queue |
| `PlutoKeating/dsh-lark-bot` | `npx dsh-lark-bot@latest setup --profile dsh-lark; dsh --profile dsh-lark` | WebSocket | Per-session isolated git worktrees; `/session /archive /retention` | Multi-bot trusted handoff, /safemode core self-heal | Crash safety-net: dsh crash still replies in Feishu; `/jobs` auto-retry queue |

The registries that validate these installs (dsharness.org, dshfind.com, dshbase.com, dsh-plugin.org) point to a fast-growing plugin ecosystem around DSH↔Feishu bridges in 2026.

## Choosing the Right Bridge for Your Use Case

Your pick should hinge on three questions: who will install it, how much isolation you need, and whether you trust the reliability layer.

- **Choose `imetn/dsh-lark-bridge`** when you want a controller-grade bridge with a `--brand` flag for ByteDance `larkoffice.com` tenants and polished card presets (compact / standard / developer). It is tested against DSH 0.1.0-rc.6, so expect developer-preview rough edges.
- **Choose `bihangchi9-creator/dsh-lark-bridge`** when strict file isolation is non-negotiable — each chat gets its own `<workspaceRoot>/<chatId>` folder and per-message `.attachments/` storage, so groups never touch each other's files. Remember the critical rule: **build before install**, because `lib/` is git-ignored.
- **Choose `amlyczz/dsh-lark-link`** when you need at-least-once delivery guarantees and a real diagnostic path. Its outbound Outbox (JSONL, idempotent) plus inbound WAL replay and `/doctor` ZIP diagnostics make it the strongest reliability story.
- **Choose `ailoushu666/dsh-feishu-bridge`** when you want the leanest setup (official dsh plugin add, official `@larksuiteoapi/node-sdk`) and live tool-call visibility with interactive option questions.
- **Choose `PlutoKeating/dsh-lark-bot`** when you want parallel multi-task in one group, multi-role agents via `/role`, and a crash safety-net that keeps replying even if the harness dies.

## Step-by-Step Setup with a QR Scan (No Public Network Needed)

The lowest-friction path is the QR-scan onboarding shared by `amlyczz/dsh-lark-link` and `PlutoKeating/dsh-lark-bot`. The "30-second setup" story works because the bridge creates the Feishu app for you — it auto-subscribes to message events, group mention, and reaction permissions — so there is no portal spelunking.

1. **Install the plugin.**
   ```bash
   # amlyczz/dsh-lark-link
   npx dsh-lark-link setup --project "$PWD"  # or the registry install for your repo

   # PlutoKeating/dsh-lark-bot
   npx dsh-lark-bot@latest setup --profile dsh-lark
   ```
   Both require Node.js ≥ 24 (lark-bot accepts ≥ 22) and `@deepseek-ai/dsh` installed.

2. **Scan the QR to create the Feishu app.** The wizard auto-creates the bot and grants the message-event subscription perms it needs, so you never touch the Feishu Open Platform console for the common path.

3. **Start the harness with the bridge profile.**
   ```bash
   dsh --profile dsh-lark
   ```

4. **Add the bot to a group (or DM it) and confirm.** Send `/help` or `/lark` to verify the connection, then send a real task.

5. **Run `/doctor` or `/where` if anything is off** — the lark-link tool bundles a diagnostic ZIP (session log + redacted config) that is far faster to share than a wall of terminal output.

## How the WebSocket Connection Eliminates Public IP, Domain and Tunnels

The #1 reason self-hosted agent bridges stall is networking: "I don't want to expose my box." The DSH bridge ecosystem solved this at the platform level. Feishu's Open Platform supports **WebSocket long connections** for receiving events, and the plugins implement them via the official `@larksuiteoapi/node-sdk`.

On a WebSocket long-connection model, your client *initiates* the connection outbound to `open.feishu.cn` or `open.larksuite.com` and keeps it alive. Feishu pushes events (messages, mentions, reactions) down that existing connection. Because the connection is outbound, there is:

- **No public IP** — your harness host stays behind your NAT/Firewall.
- **No domain** — nothing to buy, configure, or renew.
- **No webhook endpoint** — no ingress route to secure.
- **No NAT tunnel / ngrok-style relay** — one less moving part and one less attack surface.

The bidirectional plugins layer the *sending* side on the same outbound channel. `imetn/dsh-lark-bridge`, for example, is explicitly designed as "WebSocket long connections, no public webhook server." If your use case is Feishu (China), the base URL is `https://open.feishu.cn/open-apis`; for Lark (international) it is `https://open.larksuite.com/open-apis`. ByteDance `larkoffice.com` tenants instead pass `--brand larkoffice`, and `chenxin105/dsh-lark-bridge` exposes a `baseURL` switch for exactly this split.

## Managing Sessions, Projects and Workspace Isolation

How a bridge scopes work determines whether five teammates can share one harness safely. The plugins converge on a few patterns:

- **Group → Project; topic/thread → Session.** `imetn/dsh-lark-bridge` maps each group to a project and each topic to an isolated session, so parallel conversations do not bleed into each other.
- **One chat = one project folder.** `bihangchi9-creator/dsh-lark-bridge` pins each chat id to a stable `<workspaceRoot>/<chatId>` directory. Groups literally cannot touch each other's files. Files and images land in isolated `.attachments/<messageId>/` per message, with sane limits (5 attachments, images ≤ 10 MB, other files ≤ 20 MB) and a 7-day sweep.
- **Session reuse with thread independence.** `ailoushu666/dsh-feishu-bridge` reuses the same DSH Session across messages in a chat to preserve context, while different threads stay independent.
- **Per-session git worktrees.** `PlutoKeating/dsh-lark-bot` isolates each session in its own git worktree, with `/session`, `/archive`, and `/retention` commands to prune old workspaces.
- **Persistent per-chat sessions.** Sessions in `bihangchi9-creator/dsh-lark-bridge` survive restarts; a `/new` command clears the current one. This is the difference between a stateless bot that forgets everything and a durable workspace that resumes mid-task.

If you are running parallel, long-lived agent jobs in shared groups, favor the folder-worktree isolation models over a single shared-session bridge.

## Approving Tool Calls and Answering Agent Questions from Cards

A coding agent without a human-in-the-loop approval gate is a liability. The bridge plugins build that gate into the Feishu/Lark card itself:

- **Card buttons approve or reject tool calls.** `imetn/dsh-lark-bridge` renders card buttons that let you approve a pending tool invocation (or decline it) without touching a keyboard.
- **Structured Agent questions resolve in-chat.** When the harness calls `ask_user_question`, `ailoushu666/dsh-feishu-bridge` surfaces an interactive option list — reply with the option number or text and the agent proceeds. `amlyczz/dsh-lark-link` uses intent-confirm cards for the same purpose, so an ambiguous decision is confirmed before any side effect.
- **Execution is visible.** Real-time tool-call hints (🔧) and intermediate replies stream through a throttle queue so you are not staring at an opaque "thinking..." card.
- **Replies link back to the triggering message** (DM and group `@bot` by default), keeping the thread readable.

The practical rule: choose a plugin whose approval/rejection flow runs on the card. If your agents can write to files or run commands, you want that gate to be one tap in Feishu, not a return trip to a terminal.

## Security: Credentials, Permission Tiers, and Allowlists

Feishu/Lark bridge plugins handle two classes of secret: the platform app credential and tool permissions for the agent. The ecosystem's approach varies, so read the security model before choosing.

- **Credential-resolved `tenant_access_token` with auto-refresh.** `chenxin105/dsh-lark-bridge` resolves tokens through an auth provider, refreshing automatically, and keeps each tenant's token fresh. App ID/Secret are read from env (`FEISHU_APP_ID` / `FEISHU_APP_SECRET`) rather than hard-coded, and the bridge stores them through a credentials domain after a one-time web UI onboarding dialog.
- **`role('secret')` fields stay out of `describe()`.** Sensitive config fields carry an explicit `secret` role so they never leak into a harness `describe()` response or diagnostics bundle.
- **Allowlists and permission tiers.** `amlyczz/dsh-lark-link` exposes an `open_id` allowlist, a `groupPolicy` (open / mention / keywords / reply), and a denyList fallback — so a bot only responds to the right people in the right contexts. Several plugins add explicit permission tiers (read / write / full) and owner-only admin commands (`/allow`, `/disallow`, `/model`, `/preset`).
- **No public ingress = smaller attack surface.** Because the bridge connects outbound over WebSocket, there is no public webhook URL for attackers to discover or abuse.

Before connecting a real repository, set an allowlist, keep the bot's group permissions narrow, and confirm which of your agent's tools require approval.

## Reliability: Outbox, WAL Replay, and Connection Self-Healing

Agent bridges fail in unglamorous ways: a dropped WebSocket, a crashed harness, a reply lost between the model and the card. The strongest plugins engineer around each failure mode.

- **Outbound Outbox (at-least-once, idempotent).** `amlyczz/dsh-lark-link` appends outbound messages to a JSONL outbox before sending, then de-duplicates on re-delivery — so a crash between "I answered" and "Feishu delivered" does not lose the message, and a retry does not double-send it.
- **Inbound WAL replay.** The same plugin logs inbound events to a write-ahead log and replays on crash, so a task sent right before a restart is not silently dropped.
- **Connection self-heal with a QuotaGovernor.** Long connections inevitably drop; a QuotaGovernor re-establishes them and paces reconnects so you do not hammer Feishu's rate limits during an outage.
- **Crash safety-net.** `PlutoKeating/dsh-lark-bot` keeps replying in Feishu even if `dsh` itself crashes; `/safemode` boots a core-only self-healing config, and `/jobs` auto-retries queued tasks.
- **Reaction receipts.** Confirmed delivery is surfaced as reaction receipts (received, then DONE ✅), so you see at a glance whether the agent actually accepted the job.

For anything production-shaped, prefer a plugin with explicit outbox/WAL guarantees over one that fires a message and hopes.

## Common Pitfalls and Quick Troubleshooting (/doctor, build-before-install, brand flags)

Even the smoothest bridge has a few sharp edges. These are the four that trip up first-time users.

| Pitfall | Symptom | Fix |
|---|---|---|
| Installing before building | Harness fails to load the plugin | **Build first** — in `bihangchi9-creator/dsh-lark-bridge` the `lib/` directory is git-ignored, so `pnpm setup` (which builds, links, and registers) is mandatory, not optional |
| Wrong brand / region | App can't reach the Open Platform | Set the right base URL: `open.feishu.cn` (China), `open.larksuite.com` (international), or pass `--brand larkoffice` for ByteDance tenants |
| Stale or missing model key | Agents error on first call | Confirm `DEEPSEEK_API_KEY` is configured and hot-updatable in the harness (`/config` card on lark-bot) |
| Mystery failure, no logs | Slow debugging | Run `/doctor` (`amlyczz/dsh-lark-link`) to export a diagnostic ZIP with session log + redacted config, or `/where` / `/models` to verify state |

Remember that DeepSeek Harness 0.1.0-rc.6 is a **developer preview** — API surfaces move. Pin your plugin and harness versions together.

## FAQ: Feishu vs Lark, Costs, and When to Self-Host vs Use a Plugin Registry

**What is the difference between Feishu and Lark for this bridge?**
Feishu is ByteDance's collaboration app for the China market; Lark is the international build. They share the same Open Platform API but different base URLs: `https://open.feishu.cn/open-apis` for Feishu and `https://open.larksuite.com/open-apis` for Lark. ByteDance `larkoffice.com` tenants use a separate `--brand larkoffice` flag. Choose your region's platform and match the plugin's brand/baseURL accordingly.

**Does the bridge need a public IP, domain, or webhook?**
No. The modern plugins use Feishu's WebSocket long-connection API through `@larksuiteoapi/node-sdk`. Your harness connects outbound to the Open Platform and receives events over that persistent connection, so no public endpoint, domain, webhook, or NAT tunnel is required.

**Does it cost money to run a DSH Lark bridge?**
There is usually a fee to enable Feishu/Lark bot or long-connection capabilities in some open-platform tiers, plus you pay for the model calls your DeepSeek Harness agents make via `DEEPSEEK_API_KEY`. The bridge software itself is open source; you self-host it on your own Node.js ≥ 22 / ≥ 24 machine.

**When should I self-host a branch from source vs install from a plugin registry?**
Use a registry install (`dsh plugin add`, `npx`) for convenience and faster updates when the plugin validates on registries like dsharness.org, dshfind.com, dshbase.com, or dsh-plugin.org. Pull and build from source (e.g., with `pnpm setup`) when you need to patch behavior, need strict build-before-install guarantees, or the plugin has not been packaged.

**Which bridge should I pick for first contact?**
For a first install, choose a QR-scan plugin that auto-creates the Feishu app (`amlyczz/dsh-lark-link` for its reliability and `/doctor`, or `PlutoKeating/dsh-lark-bot` for multi-task and crash safety). Both eliminate the Open Platform console work, connect over WebSocket with no public network, and get you to a working "chat with an agent" in under a few minutes.
