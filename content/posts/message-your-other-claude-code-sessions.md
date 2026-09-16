---
title: "Claude Code Session Messaging: How to Send Messages to Your Other Sessions"
date: 2026-09-16T16:02:58+00:00
tags:
  - Claude Code
  - AI coding agents
  - cross-session messaging
  - multi-session workflows
  - developer tools
  - agent coordination
description: "Claude Code cross-session messaging lets one terminal session tell another what changed. Learn how SendMessage, ListAgents, and @mentions work."
draft: false
cover:
  image: "/images/message-your-other-claude-code-sessions.png"
  alt: "Claude Code session messaging"
  relative: false
schema: "schema-message-your-other-claude-code-sessions"
---

If you run more than one Claude Code session at a time, you have probably played human courier: switching between terminals, copying a finding from one window, and pasting it into another. Claude Code session messaging, shipped in v2.1.224 on August 7, 2026, removes that copy-paste loop. One session can now tell another itself — by name — with a plain-text note that arrives at the other session's next tool round. This guide explains what cross-session messaging is, how to use it, what it can and cannot do, and how to coordinate parallel worktrees without becoming the messenger.

## Why Your Claude Code Sessions Weren't Talking (the Copy-Paste Problem)

Before v2.1.224, every Claude Code session lived in its own communication bubble. Two terminals working on the same repository could not exchange information directly. If you renamed a database column in terminal A and expected the migration code in terminal B to compile, you had to physically relay that change yourself — highlight the snippet, switch windows, paste it, and hope the receiving session incorporated it correctly.

This is the core problem cross-session messaging eliminates. The most common scenario the research brief highlights is the "two terminals, one renamed column" case: one session makes a breaking schema change while another session waits on a long migration or test run in the same codebase. Rather than babysitting both windows, you describe the outcome you want in plain language and let Claude find the target session and write the note.

Messaging also solves three recurring coordination patterns: handing off a finding or rename across sessions, waiting on long-running migration or test work, and safely working the same codebase from two terminals at once. In every case the human is removed from the message loop — Claude composes and delivers the communication for you.

## What Cross-Session Messaging Actually Is (a Note, Not Context)

The single most important distinction is that a session-to-session message is a plain text note, never the sender's conversation history, files, or context. When you ask one session to message another, only the message body travels.

This has a practical consequence: if you need to hand off full working context, messaging is the wrong tool. To transfer the entire context of a session, use `/resume` instead. Messaging is for notifications, findings, headers, and pointers — the short "I changed X, you should know" notes that keep parallel work synchronized without duplicating an entire conversation.

The recommended pattern is push the pointer, not the payload. If a session has produced a long artifact such as a schema, a design doc, or a test report, write that artifact to disk first, then send a short message containing the file path. The receiving session pulls the payload from disk. This keeps messages small, keeps files on your machine, and matches how SendMessage is designed to behave.

Because a message is a note rather than a full handoff, a send does not end with a delivered conversation. A message is delivered automatically — there is no polling — and is enqueued to be processed at the receiver's next tool round. If the receiving agent has completed already, sending it a message resumes it from its transcript, which makes messaging useful for waking a finished worker back into a task.

## Requirements: Before You Start

Not every Claude Code installation can use cross-session messaging. Confirm these five requirements first:

1. **Version.** Cross-session messaging requires Claude Code v2.1.224 or later (shipped August 7, 2026). Cross-machine initiation additionally needs v2.1.225+. Native Windows support requires v2.1.234 or later.
2. **Operating system.** Messaging works on macOS, Linux, and WSL 2. Native Windows support arrived later in v2.1.234. WSL2 and native Windows cannot reach each other because discovery is filesystem-based.
3. **Provider.** Messaging is not available on Bedrock, AWS, GCP, or Foundry deployments. It requires the standard Anthropic-backed path.
4. **Feature flags.** The feature-flag evaluation that enables messaging must stay enabled. Disabling the underlying eval removes discovery and sending.
5. **Shared filesystem for local messaging.** Two sessions can message each other locally only when they share a filesystem, because discovery is filesystem-based (see below). A container session cannot reach a host session.

If you tick all five boxes, the feature is on by default — there is nothing to enable.

## How to Ask One Session to Message Another

You do not compose a session-to-session message yourself. You describe the intent, and Claude calls the two tools that power the feature:

- **ListAgents** discovers reachable sessions and agents. In the slash-command surface this appears as `/list-agents` (and historically `/peers`). It builds the list of names you can message.
- **SendMessage** delivers a message to a named target. The tool accepts a teammate name, the name "main", any name returned by ListAgents, or a `worker [ref]` form for disambiguation.

A typical instruction looks like: "*Tell the session working on the migration that I renamed the `created_at` column to `created_on` in `schema.sql`.*" Claude runs ListAgents to resolve the target, then calls SendMessage to deliver the note.

Two behaviors are worth noting. First, printing output does not communicate — SendMessage must actually be called; the message is pushed, not pulled. Second, if you deny the SendMessage tool, the ListAgents tool also disappears, and with it messaging to subagents and agent-team teammates. The two tools are coupled for safety.

## Naming Sessions and the @-Mention Shortcut

Names are the address in cross-session messaging. A session's name comes from an explicit `/rename` or the `--name` flag; otherwise Claude derives a name from the working folder. When two sessions would collide on the same name, Claude disambiguates them by working directory.

Because the name is the addressing mechanism, deliberate naming matters in multi-session workflows. Sessions you plan to coordinate should get intentional, stable names via `/rename` before you depend on messaging them. A session called "migration-worker" is far less likely to be confused than two sessions both defaulting to a folder-derived label.

To name a target directly in your prompt, use the **@-mention typeahead**, which arrived in v2.1.232 on August 13, 2026. As you type `@`, Claude suggests reachable session and agent names, and you pick the target inline. This replaces the need to describe a session indirectly and reduces the chance of messaging the wrong worker.

## What Happens When a Message Arrives (Delivery + What It Looks Like)

When a message is sent to an active session, it is queued and delivered at the receiver's next tool round. The receiving agent sees a short note composed of one sentence, the sender's name, and a reply address — the message surface collapses to a Ctrl+O one-liner so its context footprint stays tiny.

Messages can also arrive proactive. Claude may send a note on its own when it notices that a change it made will affect another session, and a receiving session can be configured to auto-reply. This proactive behavior is what turns a set of independent sessions into something closer to a cooperating team.

Delivery limits keep the system safe against runaway chatter:

- **Rate limiting.** The receiving session rate-limits repeated messages from a given sender.
- **Duplicate suppression.** Identical repeats within a short window are dropped.
- **Queue cap.** At most 50 accepted messages are queued.
- **Idle-notice expiry.** One-shot idle notices expire after 12 hours.
- **Size cap.** Same-machine messages are capped at roughly one million characters; the sending session refuses oversized messages before they leave.

## The Safety and Permission Model (What a Message Can't Do)

A message carries information, not authority. The design treats this as a feature, and it is the reason you can let sessions message each other without opening a security hole. An incoming message:

- **Cannot approve a permission prompt.** Sending a message never authorizes an action in the receiving session.
- **Cannot change config or CLAUDE.md.** Incoming messages cannot modify settings.
- **Cannot execute slash commands.** A `/compact` or any other slash command arrives as literal text and is never executed.
- **Retains per-session permissions.** The receiving session's own permission prompts and rules still apply to anything it chooses to do.

The research brief's permission-laundering rule summarizes the model: never ask a peer to perform an action that is denied or blocked in your own session. Messaging is a communication channel, not a privilege escalation path — if you cannot do something, a peer cannot be used to do it around your restrictions.

## Getting a Notice When a Session Goes Idle

Because you cannot watch every session, messaging is useful for getting a notice when a long-running worker changes state. You can ask a session to message you or another session when it finishes a migration, completes a test run, or otherwise goes idle. This converts babysitting into a notification: you stay on the board until the session reports in, and you do not have to poll for status.

The anti-loop throttle described above keeps this from becoming a livelock — repeated identical notices are rate-limited and deduplicated, so an idle agent cannot flood the channel.

## Messaging Sessions on Other Machines and Cloud (Remote Control)

Cross-session messaging is not limited to one machine, but the transport differs and it costs an extra prerequisite.

Local, same-machine messages travel over a per-session Unix socket (a named pipe on Windows) and **never pass through Anthropic servers**. This is the privacy win: two sessions coordinating on your laptop exchange notes entirely on your machine.

Cross-machine and cloud messages route through Anthropic servers over **Remote Control**. To initiate a message to another machine:

1. Run Claude Code **v2.1.225 or later**.
2. Sign in to claude.ai so the target is visible to Remote Control.
3. Ensure the target session is connected to Remote Control; cloud and other-machine sessions appear in the listing only while that connection is live.

A session registered on a shared machine discovers peers by a JSON file and a per-user Unix socket bound when the session registers — that is the filesystem-based discovery that makes container-to-host messaging impossible and cross-machine messaging impossible without Remote Control.

## Controlling Inbound Messages (crossSessionInbound, Approval, isolatePeerMachines)

You control what inbound messages a non-interactive session accepts. For unattended workers, you can set `--settings crossSessionInbound=accept` so a `-p` (non-interactive) session accepts incoming messages without an approval dialog. By default, interactive sessions can present an approval dialog for inbound requests, and a bare (non-interactive) mode binds no socket at all, so it can receive nothing.

The `isolatePeerMachines` setting restricts cross-machine peer visibility, and the standard per-session permission model still governs what a receiving session will actually do with a message. Combined, `crossSessionInbound` and the permission system let you make a worker either fully open to coordination or locked down, depending on the task's sensitivity.

## Non-Interactive Sessions and the Inbox Socket (CLAUDE_CODE_MESSAGING_SOCKET Hooks)

Beyond Claude-to-Claude messaging, you can post into a session from code. The `CLAUDE_CODE_MESSAGING_SOCKET` environment variable points at a session's inbox socket, and any hook or shell script that knows the variable can write into the session.

This is the automation leverage in the feature set. A CI script or a `post_hook` can push a status line straight into a session's message queue, letting your build pipeline talk directly to the agent working on the code instead of leaving a notice the agent must notice. Because the incoming message is still just a note, the same safety rules apply — a script posting to the inbox can announce work, but it cannot approve actions or change config.

## Messaging vs the Other Multi-Session Features (Decision Table)

Claude Code now offers several ways to coordinate sessions, and messaging is only one. Use this table to pick the right tool for the job.

| Feature | Best for | Carries full context? | Cross-machine? |
| --- | --- | --- | --- |
| Cross-session messaging (SendMessage) | Short notes, findings, pointers, wake-ups | No — plain text only | Yes, via Remote Control (v2.1.225+) |
| `/resume` | Handing off a full conversation | Yes | Locally / across terminals on same machine |
| Agent teams | Multiple agents collaborating as a named team | Partial | Depends on setup |
| `/list-agents` + naming | Discovering and addressing peers | — | Lists connected sessions |
| Remote Control | Controlling sessions from another machine | Yes | Yes (requires claude.ai sign-in) |
| Channels | Dedicated communication surfaces | Varies | Yes |

The rule of thumb: if you need to move a decision or a notification, message it; if you need to move an entire conversation, `/resume` it; if you are building a persistent collaborating unit, use an agent team.

## Common Problems and Fixes (Troubleshooting Table)

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| Sessions can't find each other on the same machine | Container vs host, or WSL2 vs native Windows — no shared filesystem | Run both sessions on a shared filesystem |
| Cross-machine send fails | v2.1.224, missing sign-in, or target not Remote Control-connected | Upgrade to v2.1.225+, sign in to claude.ai, keep target connected |
| SendMessage reports success but nothing arrives | Delivery failure edge (fixed in v2.1.225) | Upgrade to v2.1.225+ and re-send |
| Messaging unavailable entirely | Provider is Bedrock/AWS/GCP/Foundry, or feature-flag eval disabled | Move to standard provider; re-enable the eval |
| Can't message a peer | SendMessage tool denied (removes ListAgents too) | Grant SendMessage |
| Wrong session addressed | Name collision between folder-derived names | `/rename` sessions deliberately |

## Wrap-Up: Stop Copy-Pasting Between Terminals

Claude Code session messaging, live since v2.1.224, finally turns your scattered terminals into a coordinated set of workers that can tell each other what changed, hand off findings, and wake one another up when long jobs finish. Remember the three rules that keep it safe and effective: a message is a note, not a full context handoff (use `/resume` for that); send the pointer, write the payload to disk; and never ask a peer to do what your own session cannot. With deliberate session names, the `@`-mention shortcut, and the message socket for hooks, the copy-paste loop between your own sessions is gone.

## FAQ

**What is Claude Code session messaging?**
It is a feature, shipped in Claude Code v2.1.224 on August 7, 2026, that lets one Claude Code session send a short plain-text note to another session on the same machine (or across machines via Remote Control), eliminating manual copy-paste coordination between terminals.

**How do I send a message to another Claude Code session?**
Describe the outcome in plain language and let Claude handle it. Claude uses ListAgents to find the reachable target session by name and SendMessage to deliver the note. For direct targeting, use the `@`-mention typeahead (v2.1.232+) in your prompt.

**Does a Claude Code message carry full context or files?**
No. A message is plain text only and never includes the sender's conversation history or files. To move full context, use `/resume`; to move a long artifact, write it to disk and send a pointer in a short message.

**Is Claude Code messaging safe?**
Yes, by design. An incoming message cannot approve a permission prompt, cannot change config or CLAUDE.md, and slash commands arrive as literal text that is never executed; the receiving session's own permissions still apply. Local messages travel over a Unix socket and never pass through Anthropic servers.

**What are the requirements for Claude Code cross-session messaging?**
You need Claude Code v2.1.224 or later on macOS, Linux, or WSL 2 (native Windows needs v2.1.234+), a non-Bedrock/AWS/GCP/Foundry provider, the messaging feature-flag eval enabled, and a shared filesystem for local messaging. Cross-machine messaging additionally requires v2.1.225+ and a Remote Control connection with claude.ai sign-in.
