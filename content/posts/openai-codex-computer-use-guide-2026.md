---
cover:
  alt: 'OpenAI Codex Computer Use Guide 2026: Background Agents That Operate Your
    Mac'
  image: /images/openai-codex-computer-use-guide-2026.png
  relative: false
date: 2026-05-03 09:04:38+00:00
description: OpenAI Codex computer use lets background agents operate your Mac autonomously
  — here's the complete setup guide with security, plugins, and real use ca...
draft: false
schema: schema-openai-codex-computer-use-guide-2026
tags:
- openai-codex
- computer-use
- background-agents
- mac-automation
- ai-agents
title: 'OpenAI Codex Computer Use Guide 2026: Background Agents That Operate Your
  Mac'
---

OpenAI Codex computer use is a macOS feature released in April 2026 that lets AI background agents see your screen, click interface elements, and type across any app — without you being present. Agents run in a sandboxed virtual workspace, execute tasks in parallel, and hand results back when done.

## What Is OpenAI Codex Computer Use? (April 2026 Update Explained)

OpenAI Codex computer use is a macOS-only capability, launched on April 16, 2026, that gives background AI agents direct control over your desktop environment. Unlike traditional API-based automation, Codex perceives your screen visually, clicks buttons, fills forms, and navigates GUIs across any application — Finder, Notion, Slack, Excel, or a custom internal tool — without requiring that app to expose an API. The feature ships as part of the Codex desktop app alongside Atlas (an in-app browser), image generation via gpt-image-1.5, and Chronicle (a persistent memory system). As of April 21, 2026, Codex has more than 4 million weekly active developers, with 50% of users already deploying it for non-coding automation tasks. Computer use operates exclusively in a sandboxed virtual workspace, which means agents never touch your live desktop directly — they work in an isolated layer that mirrors your environment. The core value: a parallel fleet of agents can run reports, fill spreadsheets, and send Slack summaries while you stay focused on other work.

The April 2026 update marked a strategic pivot from pure coding assistant to what OpenAI calls a "superapp" — a single interface for coding, research, data analysis, and desktop automation. EU and UK rollouts are planned but not yet scheduled at time of publication.

## How to Set Up Codex Computer Use on Mac (Step-by-Step)

Setting up Codex computer use on Mac requires granting two macOS system permissions — Screen Recording and Accessibility — then activating the Computer Use plugin inside the Codex desktop app. Without both permissions, agents can observe the screen but cannot interact with UI elements. The setup takes under five minutes and does not require a developer account or command-line configuration. Here is the exact sequence: (1) Download or update the Codex desktop app from openai.com. (2) Open **System Settings → Privacy & Security → Screen Recording** and toggle Codex to on. (3) Open **System Settings → Privacy & Security → Accessibility** and toggle Codex to on. (4) Inside the Codex app, navigate to **Plugins**, search for "Computer Use," and install it. (5) Create a new thread, select GPT-5.5 as the model, and prefix your request with a GUI task description. The agent activates computer use only when you explicitly request GUI access — it will not activate automatically on every prompt. This design choice is intentional: Codex's security model gates desktop control behind explicit user intent, not ambient capability.

**Important restrictions installed by design:**
- Codex cannot automate terminal apps or the Codex app itself (prevents security bypass loops)
- Codex cannot authenticate as an administrator or approve macOS security prompts
- Agents cannot persist beyond the current session without Automations enabled (see [Automations section](#automations-and-scheduling-make-codex-a-persistent-worker))

## How Background Agents Work in Codex

A Codex background agent is an autonomous task runner that operates inside a sandboxed virtual workspace, isolated from your live macOS session. When you assign a task to an agent — "summarize all unread Slack messages in #engineering and add action items to Notion" — Codex spins up a sandboxed clone of your desktop, executes the steps (reading Slack, writing to Notion), and delivers a structured result to your active thread. The sandbox mirrors your macOS environment including installed apps, but changes made by the agent do not affect your live session unless you explicitly apply them. This architecture is fundamentally different from Claude Code's computer use, which operates directly in your local environment. Codex's sandboxed approach trades some flexibility for a much stronger security boundary: a runaway agent cannot accidentally delete files, send emails, or modify system settings on your real machine. As of April 2026, the sandbox includes full browser access via the Atlas engine, which lets agents interact with web-based tools as well as native Mac apps.

The thread-based task model means each agent run is scoped to a conversation thread. You can inspect exactly what the agent did step by step, roll back to any checkpoint, and re-run from that point with modified instructions.

## Running Parallel Agents Without Interrupting Your Workflow

Parallel background agents are Codex's most powerful productivity multiplier: a single Mac can execute dozens of long-running tasks simultaneously, each in its own sandboxed workspace, without interrupting your active session. You assign tasks to separate threads — "analyze Q1 sales data," "draft PR review for repository X," "reconcile invoices in Sheet Y" — and Codex runs them concurrently in the background. You can switch tabs, write code, or step away entirely; agents continue working and notify you when each thread completes. This model is architecturally closer to a distributed task queue than a chatbot. Codex has seen 70% monthly token growth among active users since January 2026, a metric that tracks closely with parallel agent adoption: users who discover background agents typically scale up to 10–20 concurrent threads per session. The practical limit depends on your subscription tier — Plus users get a fixed token budget per month, while Pro ($100/month) delivers 5x the Codex usage of Plus ($20/month), making it meaningfully more capable for parallel workflows.

**Tips for effective parallel agent management:**
- Name threads descriptively ("Q1 Reconciliation — March invoices") so the completion notification is immediately actionable
- Use the Automations feature to chain agent outputs: when Thread A finishes, trigger Thread B with its output as context
- Monitor the sidebar's active thread indicator — a spinning icon means the agent is still running; a checkmark means it's ready for review

## The GPT-5.5 Model: Why It Powers Computer Use

GPT-5.5, launched on April 24, 2026, is the recommended model for Codex computer use and all agentic tasks because it was specifically optimized for multi-step planning, visual grounding, and tool-call reliability — the three capabilities computer use requires most. Earlier models like GPT-4o can technically run computer use tasks, but GPT-5.5 shows substantially higher accuracy on GUI element identification, fewer false clicks on ambiguous UI states, and better recovery when an expected screen state does not match the agent's plan. In OpenAI's internal benchmarks, GPT-5.5 reduced computer use task failure rates by roughly 40% compared to GPT-4o on the same test suite. For agentic workflows where a failed step can invalidate 20 minutes of prior work, that reliability gap matters significantly. You select the model per thread in Codex's model picker — there is no global default, which means you can run quick coding threads on a cheaper model and reserve GPT-5.5 for computer use sessions where reliability is critical.

GPT-5.5 also handles extended context more gracefully, which matters for long computer use sessions where the agent accumulates screenshots, action logs, and intermediate outputs across hundreds of steps.

## Codex Plugins for Mac Automation (90+ Available)

The April 2026 Codex update shipped over 90 new plugins that dramatically expand what background agents can automate on Mac. Each plugin bundles three components: Skills (task-specific instructions for how the agent should use the app), App integrations (OAuth-based API connections for reading and writing data), and MCP server configs (Model Context Protocol configurations that let agents interact with the app's full API surface). Notable additions include Atlassian Rovo, CircleCI, CodeRabbit, GitLab Issues, and the full Microsoft Suite — Word, Excel, Teams, Outlook, and OneDrive. Gmail, Google Drive, Slack, and Notion plugins were available pre-April and remain the most widely used for knowledge worker automation. Installing a plugin takes one click inside the Codex Plugins panel; authentication is handled via OAuth with no manual credential management. Plugins are additive: once installed, the agent can invoke them autonomously when a task requires them, without you specifying "use the Slack plugin" in every prompt.

**High-impact plugin combinations:**
| Workflow | Plugins Required |
|---|---|
| PR review → Slack summary | CodeRabbit + Slack |
| Invoice reconciliation | Google Drive + Excel |
| Sprint planning update | GitLab Issues + Notion |
| CI/CD failure notification | CircleCI + Slack |
| Email triage → task list | Gmail + Notion |

## Automations and Scheduling: Make Codex a Persistent Worker

Automations turn Codex from a session-bound assistant into a persistent background worker that runs tasks on a schedule, on triggers, or across days and weeks — even when your Mac is closed. An automation is a saved agent configuration that includes: a trigger (time-based cron, webhook, or app event), a thread template (the starting prompt and context), and an output action (post to Slack, update Notion, send email). Example automation: every Monday at 8 AM, Codex reads all Slack messages from the previous week's #engineering channel, extracts open action items, and posts a structured digest to Notion. Cloud-based triggers allow automations to queue and execute even when your local machine is offline — Codex runs the agent in the cloud and syncs results when your Mac reconnects. This is the feature that makes the "background agent while you sleep" use case literal, not metaphorical. Automations support conditional branching — if the agent detects a CI failure in the morning run, it can escalate via a different Slack channel rather than the standard digest channel. Scheduling cadences range from every 15 minutes to once per month.

Building an automation: Go to **Automations** in the left sidebar → **New Automation** → choose a trigger type → write the agent prompt template → set the output destination → activate. The agent preview will do a dry run before you activate, showing you exactly what steps it would take on real data.

## Security, Permissions, and Limitations You Must Know

Codex computer use is designed with a layered security model that limits blast radius by default: agents operate in a sandboxed virtual workspace that mirrors but does not modify your live macOS environment, and computer use activates only when you explicitly request GUI access in a prompt. The two required permissions — Screen Recording and Accessibility — are the minimum macOS grants needed for visual perception and UI interaction. Codex cannot elevate these permissions on its own. Critical hard limits enforced by the Codex security layer include: no automation of terminal apps (prevents agents from running arbitrary shell commands); no automation of the Codex app itself (prevents recursive self-modification); no administrator authentication (cannot approve macOS security dialogs, install system extensions, or run `sudo` commands); and no access to content outside the sandboxed workspace unless a plugin explicitly grants it. These constraints are not configuration options — they are hard-coded into the computer use module. For enterprise deployments, Codex also supports data residency controls and audit logging of all agent actions, which is critical for compliance-sensitive workflows like financial reconciliation or HR data processing.

**What Codex computer use cannot do:**
- Approve macOS security prompts or system extension installs
- Run terminal commands or execute code outside the Codex sandbox
- Bypass App Store sandboxing on apps with restricted entitlements
- Access encrypted keychain items or password managers

## Real-World Use Cases: Developers and Knowledge Workers

Codex computer use delivers measurable productivity gains in two distinct user profiles: developers running parallel CI/CD monitoring and code review workflows, and knowledge workers automating multi-app data tasks that previously required manual tab-switching. For developers, the highest-value pattern is the CodeRabbit + GitLab + Slack chain: a background agent watches for new PRs, triggers a CodeRabbit analysis, and posts a structured summary to the relevant Slack channel — without the developer touching any of those apps. For knowledge workers, the Gmail + Notion daily brief is the most common entry point: Codex reads the last 24 hours of email, extracts decisions and action items, and updates a Notion database, taking roughly 3 minutes of agent time to replace 30 minutes of manual triage. The 50% of Codex users deploying it for non-coding tasks as of April 2026 reflects genuine demand from operations, finance, and product teams — not just software engineers. Parallel execution compounds these gains: a finance analyst who previously spent Mondays on manual report generation can now dispatch five parallel reconciliation agents on Sunday night and arrive Monday to five completed reports waiting for review.

**Developer use cases:**
- Automated PR summaries via CodeRabbit, posted to Slack on merge
- CI/CD failure triage: CircleCI alerts → agent reads logs → posts root cause hypothesis to Jira
- Daily standup prep: agent reads GitHub activity and formats bullet-point update

**Knowledge worker use cases:**
- Weekly inbox digest with action items extracted to Notion
- Invoice matching across Google Drive spreadsheets
- Meeting follow-up: agent reads calendar + notes → sends structured summary to attendees

## Codex Computer Use vs. Alternatives (Claude, Cursor)

Codex computer use, Claude's computer use, and Cursor represent three architecturally distinct approaches to AI-driven desktop automation, each with meaningful trade-offs in security, flexibility, and scope. Codex operates in a sandboxed virtual workspace on Mac — agents mirror your desktop but cannot affect the live environment, making it the safest default for delegating tasks you haven't fully tested. Claude Code's computer use (via the Claude desktop app or API) runs in your local environment with direct access to your file system and terminal, which gives it more power for engineering tasks but requires more careful permission management. Cursor does not offer GUI computer use at all — it is scoped entirely to code editing and terminal operations within the IDE boundary. For pure coding workflows where you need file-system access, Claude Code's local approach is more flexible. For business automation involving multiple SaaS apps, Codex's plugin ecosystem (90+ integrations) and sandboxed parallel agents are a better fit. For most users, the decision comes down to trust model: Codex's sandbox trades some power for substantially lower risk of accidental data loss or unintended side effects.

| Feature | Codex Computer Use | Claude Computer Use | Cursor |
|---|---|---|---|
| Execution environment | Sandboxed virtual workspace | Local environment | IDE only |
| Parallel agents | Yes (multi-thread) | Limited | No |
| Plugin ecosystem | 90+ plugins | MCP tools | Extensions |
| Mac GUI interaction | Yes | Yes | No |
| Terminal access | Restricted (no admin) | Full | IDE terminal |
| Scheduling/Automations | Yes | No (manual) | No |
| Best for | SaaS + desktop automation | Engineering workflows | Code editing |

## Pricing: Which Plan Do You Need for Computer Use?

Codex computer use is available on ChatGPT Plus ($20/month), the new Pro tier ($100/month), and the advanced Pro tier ($200/month) — but the practical experience differs significantly between plans. Plus provides a baseline token allocation that supports light computer use: a few agent sessions per day with simple single-app tasks. The $100/month Pro tier delivers 5x more Codex usage than Plus, which translates to sustained parallel agent workflows, multi-hour automation chains, and heavier plugin usage without hitting rate limits mid-task. The $200/month Pro tier targets power users and small teams running 10+ concurrent agents with complex multi-day automation sequences. GPT-5.5, required for reliable computer use, counts against your Codex token budget — it is a more expensive model than GPT-4o, so Pro users will notice the higher per-token cost. For developers already on a ChatGPT Plus plan, upgrading to $100/month Pro is the threshold where parallel background agents become a genuine workflow tool rather than an occasional experiment.

**Tier summary:**
| Plan | Monthly Cost | Computer Use | Best For |
|---|---|---|---|
| ChatGPT Plus | $20 | Limited sessions | Occasional single-task use |
| Pro | $100 | 5x Plus allocation | Daily parallel agents, automation |
| Advanced Pro | $200 | Maximum allocation | Power users, multi-agent pipelines |

---

## FAQ

**Can Codex computer use run while my Mac is asleep or the lid is closed?**
Yes — with Automations enabled, Codex can run cloud-based agents that execute even when your local machine is offline. Results sync to your thread when your Mac reconnects. Without Automations, agents require an active macOS session.

**Does Codex computer use require a developer account or special access?**
No. Computer use is available to all ChatGPT Plus, Pro, and Advanced Pro subscribers via the Codex desktop app for Mac. No developer program enrollment or API key is needed for the GUI automation feature.

**What happens if a Codex background agent makes a mistake in the sandbox?**
Because agents operate in a sandboxed virtual workspace that mirrors but does not modify your live environment, mistakes are isolated. You review the agent's proposed changes before applying them. You can also roll back to any checkpoint in the thread and re-run from that point with corrected instructions.

**Is Codex computer use available on Windows or Linux?**
As of May 2026, computer use is macOS-only. OpenAI has indicated EU and UK rollouts are in progress, but no Windows or Linux support has been announced. Windows users can access Codex's coding and chat features but not GUI automation.

**How does Codex computer use differ from using a macro or script?**
Traditional macros and scripts require explicit programming of every step and break when UI changes. Codex computer use is model-driven: the agent perceives the current screen state visually and adapts its actions dynamically. If a button moves, the agent finds it; if a dialog appears unexpectedly, the agent reads it and responds. This makes Codex useful for automating apps that don't expose a stable API or scripting interface.