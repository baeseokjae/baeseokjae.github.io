---
title: "Pizza Bot Inbox for Background AI Agents: The Async Agent Pattern, Reviewed (2026)"
date: 2026-09-29T04:07:14+00:00
tags:
  - pizza bot inbox background ai agents
  - Pizza Bot AWS open source review
  - AI agent inbox pattern
  - background agents human in the loop
  - async agent inbox vs chat window
  - LangGraph checkpoint interrupt durable approval
  - self-hosted agent inbox open source
  - DeepAgents LangGraph local-first agent app
  - agent approval queue best practices
  - run background AI agents unattended
  - pizza bot vs LangChain agent inbox
  - agent work receipts and approval fatigue
description: "Pizza Bot is a local-first inbox for background AI agents, built on DeepAgents and LangGraph. Review of its queues, checkpoints, real limits and TCO."
draft: false
cover:
    image: "/images/pizza-bot-background-ai-agents-2026.png"
    alt: "Pizza Bot Inbox for Background AI Agents: The Async Agent Pattern, Reviewed (2026)"
    relative: false
schema: "schema-pizza-bot-background-ai-agents-2026"
---

Pizza Bot is a self-hosted, local-first inbox for background AI agents: you give an agent work, close the window, and it comes back with a result — or pauses in an Action queue when it needs your decision. It is a finished desktop application built on DeepAgents and LangGraph, Apache-2.0 licensed, not an SDK. The design brief behind it is the whole argument: *the interface assumes you are not watching.*

That single assumption rewrites almost every UI decision in the app, and it is why Pizza Bot is worth understanding even if you never install it. Chat windows assume you are present. Work that runs for twenty minutes, or overnight, or on a cron schedule, cannot be reviewed in a chat window without you sitting there scrolling. Pizza Bot's contribution is not the idea of an agent inbox — that idea has existed since at least November 2024 — but the packaging: one installable app containing a runtime, a scheduler, an approval queue, and durable on-disk state.

This review separates what the primary sources actually establish from what the launch coverage repeated. It covers the four queues, the LangGraph checkpoint mechanism that makes a paused approval outlive your session, the honest limitations the authors state themselves, and the enterprise risks analysts have already named.

## What is Pizza Bot, and what is it not?

Pizza Bot is an open-source, local-first application that runs long-running AI agents and surfaces their work as email-style threads. The repository `pizza-bot-app/pizza-bot` describes itself as "a local-first inbox for long-running AI agents, built with DeepAgents and LangGraph" — Apache-2.0, TypeScript, with topics including human-in-the-loop, local-first, MCP, deepagents, Electron, and amazon-bedrock.

It is not a framework and not a library. The AWS Open Source Blog announcement frames it explicitly as a finished application "for people who just need the work done" rather than for people building agents. That distinction matters more than it sounds: most agent tooling in 2026 ships as a framework you assemble, and assembly is exactly what non-specialists cannot do.

| What it is | What it is not |
|---|---|
| A self-hosted application with a runtime, scheduler, UI and storage bundled | A framework or SDK you embed in your own product |
| A local-first app: state lives in one folder (`~/.pizza-bot-oss` by default) | A cloud service; there is no hosted tier |
| Apache-2.0, TypeScript, community-owned in its own GitHub org | An AWS product — no AWS support, no SLA |
| A rebuild of an internal Amazon tool with 2,000+ internal users | Evidence that 2,000+ people use this open-source release |

The name comes from Amazon's "two-pizza team" convention, and the internal team calls itself "Chefs." Pizza Bot itself is a trademark of Amazon.com, Inc., even though the project now lives in a standalone community organization separate from Amazon. GitHub metadata checked on 2026-09-29 shows 402 stars, 35 forks and 18 open issues; the repo was created 2026-06-26 and last pushed 2026-09-26.

Two releases have shipped: v1.0.0 on 2026-09-08 and v1.1.0 on 2026-09-19, with Linux `.deb`/`.rpm` and macOS `.dmg`/`.zip` assets for x64 and arm64. Only the macOS builds are signed, so Windows and Linux users should expect OS security prompts on first launch. The New Stack notes the desktop ships for macOS, Windows and Linux, with browser and terminal clients alongside it.

### Where did it come from?

The genesis was "JoeBot" in April 2025 — a side-of-desk script by Joseph Dolivo, a principal technologist at AWS Startups, built to automate repetitive CRM logging. A colleague, Igor Fil, helped turn it into an MCP server running parameterized "recipes." It grew past 30 contributors and more than 2,000 users inside Amazon before the rebuild.

The rebuild happened because the MCP server needed an MCP client, and the team concluded that non-technical users needed a real front end. As The New Stack puts it, "We had to meet people where they actually work." That is the honest origin story, and it explains the design priorities: not elegance, but adoption by people who will never open a terminal.

## Why does chat break down for background agent work?

Chat breaks down because it is a synchronous interface wrapped around asynchronous work. The AWS design post lists four requirements that drove Pizza Bot's design: inspect several sources, prepare a result in the background, ask before a consequential action, and come find the person who asked once done. None of those four describe a chat window.

Developers Digest sharpens this into six concrete failure modes you can test any chat-based agent harness against:

1. **Work finishes and nobody notices.** The run completes in a tab you closed three hours ago.
2. **The agent blocks on one permission request.** A single approval stalls an entire multi-step run with no signal.
3. **You lose track of which run needs review.** Five parallel threads, no queue semantics.
4. **A long transcript with no summarized result.** The answer exists at token 40,000.
5. **Completed and risky pending work share one stream.** Finished artifacts and an unresolved purchase approval look identical in a scrolling column.
6. **Scheduled runs are invisible unless they fail loudly.** A cron job that succeeded is indistinguishable from one that never fired.

Every one of these is a queueing problem, not a model problem. That framing is the most useful thing to take from the entire launch cycle: background agents are not chatbots with longer timeouts, they are work queues with human checkpoints.

The counter-argument from analysts is worth stating in the same breath, because it defines the ceiling. Bhupendra Chopra of Kanerika told InfoWorld that out-of-the-box skills remove app-building time but leave the integration work intact — and "integration is where most of the money in an enterprise agent deployment goes." Chopra's upside case is real, though: "It changes the economics of delegating work to agents… an inbox brings them in only when their judgment is needed, much like how executives delegate to their teams." Coding agents already proved the shape of that model — assign an issue, review the PR.

## The four queues that make agent work legible

Pizza Bot ships three visible queues plus an Activity panel; the pattern literature calls for four. Here is how they map.

| Queue | What lands there | Why it exists |
|---|---|---|
| **All** | Full thread history | The record, not the to-do list |
| **Unread** | Completed work not yet reviewed | Finished work that would otherwise be missed |
| **Action** | Work paused waiting on your approval or answer | Decisions only you can make |
| **Archived** (pattern literature) | Reviewed and closed runs | Keeps Unread and Action honest |

The **Activity** panel is the fourth surface: it shows delegated specialists running with their own transcripts. That is where tool-scoped subagents become visible rather than mysterious.

Threads can be organized into folders, and the README makes an important promise: folders do not hide matching work from the global Unread and Action queues. That detail is a design discipline — the moment a folder can suppress an approval request, you have rebuilt an inbox with unread mail hidden in subfolders.

Developers Digest prescribes a per-run "receipt" as the compact evidence unit: goal, inputs inspected, tools used, decisions made, artifacts, verification, remaining risks, next action. Pizza Bot does not formalize that as a named object, but every field maps onto something the app already stores — the thread history, the Activity panel, and the checkpoint record. If you are building your own internal agent tooling, the receipt is the single most copyable artifact from this whole exercise, because it is what lets a reviewer sign off in ninety seconds instead of reading a transcript.

The control-plane checklist underneath all of it is short:

- Status is visible without reopening every run.
- You can interrupt work without babysitting it.
- Every run leaves a receipt with enough evidence to review quickly.

## How do interrupts and checkpoints make a pause durable?

The inbox is what you see; a LangGraph interrupt plus a checkpointer is what makes the pause real. Without durable checkpoints there is no Action queue — only a spinner.

The mechanism, as The Clarity explains it plainly: the agent graph stops at a declared point, LangGraph writes state to a checkpoint, and the run resumes from that record. DeepAgents builds the agent on LangGraph, which checkpoints a run as it proceeds, so messages, tool activity, and a pending approval live on disk — SQLite plus ordinary files — rather than in memory. Runs survive closing the thread, reloading the page, or switching devices.

This is where most homegrown attempts fail. A "waiting for approval" state held in a process variable evaporates the moment the process restarts, and then the approval path is a lie: the user approves something and there is nothing left to resume. Pizza Bot's server owns state and answers over HTTP; clients are Electron desktop, browser, or terminal. Because the client is not the runtime, closing a window does not kill a run.

There is an important caveat the AWS post states honestly rather than burying. Quitting the desktop app stops the server it started and ends that server's runs. Because runs are checkpointed you lose "the step in flight rather than the thread." In practice that is a good failure mode — you resume rather than restart — but it also means the two-machine rule applies to anyone who wants cron work to fire while the laptop is shut: run the server headlessly on an always-on host or in a container, then point desktop, browser and CLI clients at it.

Automations compound this. Pizza Bot supports cron schedules and secret-protected webhooks, and there is a specific detail worth praising: after the machine has been off or asleep, a slept-through schedule runs once, not once per missed occurrence. A month offline produces one result, not thirty. Most naive schedulers replay the backlog and produce a burst of stale work; suppressing it is the correct call.

## Hands-on: installing it, configuring a provider, and scheduling your first run

The install path is genuinely short, which is the point of shipping an app instead of a framework.

1. **Install the desktop app** from the v1.1.0 release assets for your platform (`.dmg` on macOS, `.deb`/`.rpm` on Linux, with x64 and arm64 builds). Expect a prompt on non-Mac platforms because only macOS builds are signed.
2. **Pick a model provider.** Anthropic, Amazon Bedrock, Google Gemini, OpenAI, OpenRouter, or local Ollama. Credentials go to the OS secret store, never to a browser client — a meaningful decision, because it means an attached browser tab cannot read your API keys.
3. **Confirm the data root.** Everything — threads, checkpoints, memories, attachments, settings, logs — sits in one folder, `~/.pizza-bot-oss` by default, overridable via `PIZZA_DATA_ROOT`. No telemetry. One folder to back up.
4. **Ask for something with a visible finish line.** A background task with a reviewable artifact is a better first run than a conversational prompt, because it exercises the Unread queue.
5. **Add an automation.** A cron schedule or a webhook gives you the second half of the product: work that starts with no open conversation.

Step 5 is where the product either earns its place or does not. An inbox for agent work is only interesting if work arrives while you are not there. If every run is triggered by you typing a prompt, you have reimplemented a chat window with extra ceremony.

The operational friction is concentrated in that same step, and it is worth being blunt about it: a laptop nobody is watching is often a laptop that is asleep. Scheduled agents on a closed lid do not run. The server has to live somewhere that stays up.

## Skills, MCP servers, and tool-scoped specialists

Pizza Bot's model of a "specialist" is refreshingly small: each `SKILL.md` becomes a worker with its own short MCP tool list. A skill declares `tools` and an `interruptOn` policy — a per-tool approval rule — with `allowedDecisions` including `edit`.

That `edit` decision is the detail I would steal first. The normal human-in-the-loop triad is approve, reject, or respond. Rejecting a proposed action usually means the agent starts over, which wastes the context it built. Allowing the human to *edit* the proposed action — fix the date, correct the recipient, adjust the amount — and then let the run continue is what makes an approval queue usable rather than punitive.

Two skills ship by default: a browser-automation skill backed by Microsoft's Playwright MCP server (37,674 stars on GitHub as of 2026-09-29) and a `pizza-bot-guide` skill. The app can also drive an existing Claude Code `.mcp.json` unchanged, which lowers the cost of trying it inside a workflow you already have.

Out-of-the-box tools are deliberately boring: filesystem list, read, write, edit and search inside its own scratch space; a `task` delegation tool; and a sandboxed QuickJS JavaScript interpreter with no network access and no host filesystem. That last one is a genuinely thoughtful boundary — a code-execution tool that cannot reach the network or the host disk is a much smaller liability than a general shell.

The architectural note that matters for anyone evaluating the codebase: the production graph engine is isolated to `packages/runtime-langgraph`, and frontends consume protocol projections. That is a swap seam. It means the UI is not welded to one runtime, even though LangGraph is the only shipped implementation today.

The capability-boundary argument deserves one more sentence, because it is the most transferable idea here: keeping a specialist's tool list *short* is what makes its reach reviewable at a glance. An agent with forty tools cannot be audited by a human before lunch. An agent with six can.

## Local-first, but is it safe? The real security boundary

Local-first is not the same as safe, and Pizza Bot's own documentation is more precise about this than most of its coverage.

What the project actually claims: `api-server` binds to 127.0.0.1 by default, app state stays under `PIZZA_DATA_ROOT`, credentials go to the OS secret store, and MCP servers and plugins are explicitly trusted code approved at install time. A non-loopback deployment requires an API token **and** an explicit origin allowlist — not one or the other.

| Claim | What it does promise | What it does not promise |
|---|---|---|
| Local-only binding | Default is loopback; remote requires token + origin allowlist | That a misconfigured bind is impossible |
| No telemetry | The project does not phone home | That your model and tool traffic stays home |
| Local data folder | One folder holds threads, checkpoints, memories, attachments, logs | Backup, encryption at rest, or access control on that folder |
| MCP/plugins trusted | Trust is granted explicitly at install time | That a trusted server is a safe server |

Developers Digest makes the caveat crisply: don't treat local-first as automatically safe. MCP servers and plugins are trusted code, folder access must be granted deliberately, and model/tool requests still go to whatever endpoints you configure. If you point Pizza Bot at a hosted provider, your prompts leave the machine — "local-first" describes where state lives, not where inference happens.

The Clarity adds a durability question the launch coverage did not answer. State lives in a local SQLite file, and nothing is documented about backup, upgrade paths, or who else can read that file. On a single-user laptop that is a manageable risk. On a shared machine or a container host with multiple operators, an unencrypted SQLite file holding agent memories, tool arguments and attachments is a data governance item, not a footnote.

There is also an honest AWS-internal tension worth noting: AWS's own Strands Agents SDK has been generally available since May 2025, yet it does not appear in the Pizza Bot build, which uses LangGraph instead. A sample repo in the ecosystem calls Strands "a lighter-weight alternative to LangGraph for agents that don't need explicit graph control flow." Pizza Bot needs explicit graph control flow — that is precisely what makes the interrupt/checkpoint mechanism work — but the choice does mean the project is not a showcase for AWS's own agent runtime.

## Licensing, pricing, and total cost of ownership

The software is free and Apache-2.0. The cost is everything around it.

| Cost line | Reality in 2026 |
|---|---|
| License | Apache-2.0, no fee, no seat count |
| Support | None. Community project, explicitly no AWS support or SLA |
| Model inference | Your provider bill — Anthropic, Bedrock, Gemini, OpenAI, OpenRouter, or Ollama for local |
| Hosting | Your machine, unless you run the headless server for always-on schedules |
| Backups | Yours. One folder, no documented backup or upgrade path |
| Updates | Yours to apply; two releases in the first two weeks of availability |
| Monitoring | Largely yours — this is the risk analysts flag as invisible failure |

The AWS post states the maintenance position without hedging: keeping it running, backed up and updated is yours. That is the correct disclosure for a community project, and it should be read literally. There is no vendor to escalate to when a scheduled run silently stops.

Unwatched scheduled work also has an unwatched cost line. InfoWorld notes that scheduled runs can add cost while nobody is looking. The concrete mitigation is unglamorous: a spend ceiling per automation, and a notification on completion rather than only on failure.

## Honest limitations: what the 2,000-user number does and does not tell you

The most repeated figure in the coverage is "more than 2,000 users inside Amazon," used for meeting prep, follow-ups, email drafting, Slack summaries, CRM logging, day prioritization, and web research. It is a real number and it describes the wrong thing.

The 2,000+ figure describes the *earlier internal MCP-server era*, not the application released this month. The Clarity makes this point directly: the only usage figure available is internal to Amazon and predates the open-source release. There is no adoption number for the app itself. Its external demand signal is also modest and worth stating plainly — the Show HN thread scored 61 points with 37 comments (item 49713894), and a 90-day US Google Trends check found almost no durable demand for "Pizza Bot" or "AI agent inbox" as search terms, while broad "AI agents" stayed steady and "LangGraph" held a small baseline.

Two more self-reported limitations belong in any honest review. First, the internal skill and MCP marketplace that delivered most of Pizza Bot's day-one internal value was removed during the rebuild — so day-one value for a new user is materially lower than the internal history implies. Second, only macOS builds are signed, which shifts the trust decision to the user on Windows and Linux.

The skeptical case also lands on the novelty claim, and it is fair. LangChain CEO Harrison Chase introduced "ambient agents" in January 2025 with an email-assistant reference implementation on LangGraph, and LangChain shipped a standalone Agent Inbox in November 2024. Pizza Bot is itself a rebuild of an April 2025 internal script. The contribution is packaging and opinion, not invention — which is still meaningful, but is a different claim than "new pattern."

## Pizza Bot vs LangChain Agent Inbox, AgentMail, and ticket-tracker dispatch

The neighbours matter, because the right question is not "is Pizza Bot good?" but "which of these shapes fits my problem?"

| Option | Shape | What you supply | Best fit |
|---|---|---|---|
| **Pizza Bot** | Self-hosted app: runtime, scheduler, UI, storage | A machine that stays up; your provider key | Individuals and small teams who want the work done, and always-on scheduled agents |
| **langchain-ai/agent-inbox** | Inbox UX library over your own LangGraph deployment | A LangGraph deployment plus a LangSmith account | Teams that already run LangGraph and want the approval surface only |
| **Real email (AgentMail-style)** | Agent as a correspondent in a mailbox you already check | Mailbox plumbing and identity | Agents that must reach non-technical stakeholders where they already are |
| **Ticket-tracker dispatch** | Agent work as issues and PRs in Linear/Jira/GitHub | Issue workflow plus review discipline | Engineering orgs; the pattern coding agents already proved |

LangChain's Agent Inbox is the direct prior art, and its GitHub numbers are the honest benchmark: 1,093 stars and 157 forks, MIT licensed, created 2024-11-04. It is infrastructure you assemble, not an app — you clone it, add a LangSmith API key, and register an inbox per assistant with an assistant/graph ID plus a deployment URL. Its interop is defined by a schema contract: interrupts must conform to the `HumanInterrupt` input/output schema (`action_request` with `action`, `args`, `config`, and `allow_ignore`/`allow_accept`/`allow_edit`/`allow_respond` flags) before the inbox can render them.

That schema dependency is the cleanest axis of comparison. If you already have a LangGraph deployment and LangSmith, Agent Inbox gives you an approval surface without adopting someone else's runtime. If you do not, Pizza Bot bundles the runtime, scheduler, UI and storage into one desktop-installable app. The author himself made a version of this argument on Hacker News, answering comparisons against Linear agents, Paperclip, Herdr, GrokBot, and the perennial "why not just use real email?" — the answer being that Pizza Bot runs the execution loop itself and ships the whole app.

That is a real differentiator, and it is also why the substrate numbers are worth knowing: LangGraph at 42,435 stars, DeepAgents (Python) at 29,844, deepagentsjs at 1,585, and LangChain at 147,220, all pushed within days of 2026-09-29. Pizza Bot is a thin, opinionated layer on a very large and active foundation — which is good news for durability of the primitives and neutral news for Pizza Bot's own longevity.

## The pattern worth copying even if you never install it

Strip the product away and four things remain that you can implement in any stack.

**One: four queues.** Active, Action, Unread, Archived. The Action queue is the one that carries the design weight, because it is the only path by which an agent can obtain permission for a consequential action — and it should be the only path.

**Two: durable interrupts.** A pause must survive a process restart, a device switch, and a closed laptop lid. If your approval state is in memory, you do not have a human-in-the-loop system; you have a request for attention that may or may not still exist when the human responds.

**Three: per-run receipts.** Goal, inputs inspected, tools used, decisions made, artifacts, verification, remaining risks, next action. This is what converts "review" from a thirty-minute transcript read into a ninety-second check.

**Four: an `edit` decision alongside approve and reject.** Correcting a proposed action and continuing is strictly better than rejecting and restarting, both for token cost and for trust.

Then carry the four enterprise risks in your own design review, because they are real and none of them is solved by software alone:

- **Approval fatigue.** Dozens of approval threads train users to approve without reading. Mitigation: fewer, better-timed approval points — not more confirmation dialogs.
- **Stale approvals.** Information that was true when the agent paused may be invalid hours later, producing an outdated CRM update or a meeting invite for a slot that no longer exists. Mitigation: re-verify data freshness before an approved action executes.
- **Invisible failure.** As Phil Fersht of HFS Research told InfoWorld, "The inbox model can make bad work less visible… when somebody is watching an agent in a chat window, they can see it going off the rails." Mitigation: a completion notification that carries the receipt, not just an error channel.
- **Unwatched cost.** Scheduled runs spend while you sleep. Mitigation: per-automation ceilings and a cost line in the receipt.

## Verdict: who should self-host Pizza Bot in 2026 and who should wait

**Self-host it if** you are an individual technologist or a small platform team who wants background agents to produce reviewable artifacts, you can give the server a machine that stays awake, and you are comfortable owning backups, updates and monitoring. The three queues plus durable checkpoints solve a real problem that chat-shaped tooling does not, and Apache-2.0 with a one-folder data root is an easy thing to trial and delete.

**Wait if** you need a supported, governed enterprise interface. There is no SLA, no vendor escalation path, and the state file's backup and access-control story is undocumented. Regulated and risk-averse organizations should treat Pizza Bot as an experimentation tool rather than a replacement for governed interfaces — which is exactly what analysts predicted about its adoption path: bottom-up with individual technologists and small platform teams.

**Build the pattern either way.** Four queues, durable interrupts, per-run receipts, and an edit decision are stack-agnostic. The most durable lesson of the Pizza Bot launch is not that an inbox beats a chat window as a slogan — it is that the inbox is the easy part. The interrupt and the checkpoint are what make it true.

## FAQ

### What is Pizza Bot in one sentence?

Pizza Bot is a local-first, self-hosted inbox application for long-running AI agents, built on DeepAgents and LangGraph and released Apache-2.0 by a community project spun out of an internal Amazon tool. You hand an agent work, close the window, and review finished results in an Unread queue or answer its questions in an Action queue. It is a finished app, not an SDK.

### How is Pizza Bot different from LangChain's Agent Inbox?

LangChain's Agent Inbox is a UX layer you assemble on top of an existing LangGraph deployment and a LangSmith account — 1,093 stars, MIT, created 2024-11-04, and interrupts must conform to the `HumanInterrupt` schema before it can render them. Pizza Bot bundles runtime, scheduler, UI and storage into one installable app. If you already run LangGraph, Agent Inbox is the narrower dependency; if you do not, Pizza Bot is the shorter path.

### Does Pizza Bot really run agents while I am away?

Partly. Runs are checkpointed by LangGraph to SQLite and files on disk, so a paused approval outlives the session, the device, and the process, and cron schedules and webhooks can start work with no open conversation. But quitting the desktop app stops the server it started and ends that server's runs, and a sleeping laptop runs nothing. For genuinely unattended schedules, run the headless server on an always-on host or in a container and point your clients at it. A missed schedule while the machine was off runs once, not once per occurrence.

### Is the "2,000+ users" figure evidence that Pizza Bot is proven?

No. That figure describes the earlier internal Amazon MCP-server era, not the open-source application released this month, and it is internal usage rather than external adoption. The app's external signals are modest: a Show HN thread at 61 points and 37 comments, and a 90-day Google Trends check showing almost no durable demand for the exact terms "Pizza Bot" or "AI agent inbox." There is also a real value gap — the internal skill and MCP marketplace that delivered most of the day-one internal value was removed during the rebuild, and only macOS builds are signed.

### What is the biggest risk of an agent inbox pattern?

Approval fatigue combined with stale approvals. An agent that files dozens of approval threads conditions users to approve without reading, and an action that was correct when the agent paused may be wrong hours later — an outdated CRM write or a meeting invite for a slot that no longer exists. The mitigations analysts recommend are design-level, not UI-level: fewer and better-timed approval points, and a freshness re-check before any approved action executes. Invisible failure is the companion risk — in Fersht's words, watching an agent in a chat window lets you see it going off the rails, and an inbox can hide that.

## Sources and verification notes

Everything above traces to primary artifacts checked on 2026-09-29: the AWS Open Source Blog announcement of Pizza Bot; The New Stack's report on the JoeBot origin and internal adoption; InfoWorld's analyst counterweight of 2026-09-16 quoting Bhupendra Chopra (Kanerika) and Phil Fersht (HFS Research); The Clarity's skeptical read of the novelty and durability claims; Developers Digest on the queue-and-receipt pattern, the six chat failure modes, and its 90-day Google Trends check; the GitHub repos `pizza-bot-app/pizza-bot` and `langchain-ai/agent-inbox`; the Hacker News thread for item 49713894; and the AWS blog's stated limitations.

Three figures are weaker than the headline version and are labelled as such in place. The "2,000+ users" number is internal Amazon usage of the predecessor MCP server, not the open-source app. The 37,674-star Playwright MCP figure describes Microsoft's server, not Pizza Bot. The Google Trends finding is a third-party 90-day US check, which is directional evidence about search demand rather than a market measurement.

Repository statistics (402 stars, 35 forks, 18 open issues; release dates v1.0.0 on 2026-09-08 and v1.1.0 on 2026-09-19; substrate star counts) are point-in-time values from the GitHub REST API on 2026-09-29 and will drift.
