---
cover:
  alt: 'ChatGPT Workspace Agents (Codex-Powered): Team Guide 2026'
  image: /images/chatgpt-workspace-agents-guide-2026.png
  relative: false
date: 2026-04-26 18:04:46+00:00
description: Complete team guide to ChatGPT Workspace Agents powered by Codex — build,
  deploy, and govern autonomous agents in Slack and across your stack.
draft: false
schema: schema-chatgpt-workspace-agents-guide-2026
tags:
- chatgpt
- workspace-agents
- codex
- openai
- team-automation
- enterprise-ai
title: 'ChatGPT Workspace Agents (Codex-Powered): Team Guide 2026'
---

ChatGPT Workspace Agents are autonomous AI workers powered by Codex that your team builds once and runs continuously — reading files, calling APIs, posting to Slack, updating Salesforce, and completing multi-step workflows without hand-holding. Launched April 22, 2026, they replace custom GPTs for Business and Enterprise users.

## What Are ChatGPT Workspace Agents? (Powered by Codex)

ChatGPT Workspace Agents are cloud-hosted autonomous AI workers that use OpenAI's Codex model as their execution engine. Unlike chatbots that respond to a single prompt and stop, workspace agents can plan multi-step workflows, call connected tools (Slack, Google Workspace, Salesforce, Notion), write and run code, retain memory across sessions, and continue working in the background until a task is complete. Launched on April 22, 2026, they represent OpenAI's clearest enterprise pivot to date: from conversational AI to operational AI.

The Codex backbone matters because it was purpose-built for reasoning over code and structured data — not just generating text. When your agent needs to pull a Salesforce opportunity, summarize Gong call transcripts, and post a formatted deal brief to a Slack channel, Codex handles the multi-tool orchestration reliably. OpenAI's own Sales Consultant built a deal-prep agent that replaced 5–6 hours of manual rep work per week — with no engineering team involved. That's the promise: workflow automation authored in plain language, executed at enterprise scale. Workspace agents are available in research preview on ChatGPT Business, Enterprise, Edu, and Teachers plans, with free access running until May 6, 2026.

### How Codex Powers Agent Execution

Codex gives workspace agents the ability to write short programs on the fly to accomplish sub-tasks — fetching structured data, transforming spreadsheet columns, or validating output before sending it downstream. This differs from tool-calling in standard ChatGPT: instead of selecting from a fixed menu of connectors, Codex can generate the exact logic needed for a specific step, then execute it in a sandboxed environment. The result is an agent that generalizes across tasks rather than following fixed scripts.

## Workspace Agents vs Custom GPTs: Key Differences Your Team Needs to Know

Workspace agents are a direct successor to Custom GPTs, and OpenAI plans to eventually deprecate Custom GPTs for Business and Enterprise accounts in their favor. The distinction is not cosmetic — these are fundamentally different products with different capabilities and use cases.

Custom GPTs are conversational wrappers: they have a custom system prompt, a few connected tools, and knowledge files. Every conversation starts fresh. They talk. Workspace agents, by contrast, take action. They can read a Slack message, query Salesforce, summarize a document in Google Drive, and write the output back to Notion — all in a single triggered run, without a human in the loop. They also maintain persistent memory across sessions, so an agent that learns your deal-review format in week one still applies it in week eight.

The trigger model is another major difference. Custom GPTs activate only when a user starts a conversation. Workspace agents support three trigger modes: a human request (chat or @mention in Slack), a scheduled time (run every Monday at 8 a.m.), and an event (a new Slack message in a specific channel). This makes them suitable for proactive, background work — not just reactive responses. For teams already running Custom GPTs for internal workflows, migration is the right next step, and most of the configuration (instructions, tools, knowledge) transfers directly.

| Feature | Custom GPTs | Workspace Agents |
|---|---|---|
| Memory across sessions | No | Yes |
| Can take actions | Limited | Full (read/write APIs) |
| Trigger types | Chat only | Chat, schedule, Slack event |
| Shared across team | Yes (GPT Store) | Yes (team workspace) |
| Codex execution | No | Yes |
| Pricing model | Included in plan | Credit-based after May 6 |

## Which ChatGPT Plans Include Workspace Agents?

Workspace agents are available exclusively on paid team and enterprise plans — they are not included in ChatGPT Free or Plus subscriptions. As of April 2026, the eligible plans are ChatGPT Business ($20/user/month), ChatGPT Enterprise (variable pricing), ChatGPT Edu, and ChatGPT Teachers.

The current research preview period runs free of additional charge until May 6, 2026. After that date, workspace agents use a credit-based model tied to Codex consumption. OpenAI has introduced a separate "Codex-only seat" option for Business and Enterprise workspaces — these seats carry no rate limits and are billed purely on token consumption, making them cost-predictable for high-volume agent workloads. Teams activating new Codex seats during the promotional window (starting April 2, 2026) can earn up to $500 in credits — $100 per new seat, up to five seats.

For admins planning the transition off the free tier, the key variable is agent run frequency and the size of context windows per run. An agent that queries Salesforce once daily and posts a 500-word summary will consume far fewer credits than one that processes every inbound Slack message in a busy channel. OpenAI's usage dashboard will surface per-agent consumption data to help teams size their credit allocation before billing begins.

### Free Tier Deadline: What Teams Should Do Before May 6

Before May 6, use the free preview period to build, test, and iterate on every agent your team plans to keep. Run each agent through at least one full production scenario — real data, real integrations, real edge cases. That hands-on testing data will be your best input for estimating credit needs. Also confirm that workspace admins have connected all required integrations (Slack, Google Workspace, Salesforce) during the free window, so agents don't need reconfiguration when billing starts.

## Step-by-Step: How to Build Your First Workspace Agent

Building a workspace agent requires no engineering background. The interface is a form-based builder inside ChatGPT that accepts plain-language instructions for each configuration field. Here is the full process from zero to a deployed agent.

**Step 1: Access the Agent Builder.** In ChatGPT, open the left sidebar, navigate to your workspace, and select "Create Agent." This opens the agent configuration panel.

**Step 2: Write the Agent's Role and Responsibility Scope.** Describe what the agent is responsible for in one or two sentences. Be specific: "You are a deal-brief agent. Your job is to research each new Salesforce opportunity, summarize the most recent Gong call transcript, and post a formatted brief to the #deals Slack channel before 9 a.m. on the day of the first call."

**Step 3: Define Trigger Conditions.** Choose when the agent runs: on schedule (e.g., daily at 8 a.m.), on a Slack @mention, or when a human sends it a direct message in ChatGPT. You can combine triggers — schedule for recurring runs, @mention for ad-hoc requests.

**Step 4: Set Pause and Stop Rules.** Define conditions under which the agent should pause for human review rather than continue autonomously. Example: "If the opportunity value exceeds $500K, draft the brief but wait for Sales Manager approval before posting to Slack."

**Step 5: Select Tools and Integrations.** Choose which connected apps the agent can use. At launch, integrations include Slack, Gmail, Google Drive, Google Calendar, Google Docs, Google Sheets, Salesforce, Notion, Atlassian Rovo, and Microsoft apps. Grant only the tools the agent needs — principle of least privilege applies here exactly as it does in code.

**Step 6: Write Process Steps.** List the steps the agent should follow in order. Plain English is fine: "1. Pull the Salesforce opportunity record by account name. 2. Find the most recent Gong call for that account. 3. Summarize key pain points and next steps from the call. 4. Format the summary using the deal-brief template in Google Drive. 5. Post to #deals with a link to the full record."

**Step 7: Add Compliance Rules.** Specify what the agent must never do: "Never share financial data outside the #deals channel. Never post to external Slack channels. Always include the opportunity stage and close date in the brief."

**Step 8: Test and Deploy.** Run the agent against a real scenario using the "Test Run" feature. Review the output, adjust instructions where the agent deviates, and iterate. Once satisfied, set status to Active. The agent is now live for your team.

## Best Use Cases for Teams (With Real Examples)

Workspace agents deliver the highest ROI in workflows that are high-frequency, multi-step, and currently require a human to assemble information from multiple tools before acting. The common thread is not complexity — it's repetition.

**Sales: Deal Brief Agent.** Researches each new Salesforce opportunity, pulls Gong call summaries, and posts a formatted brief to Slack before the first call. OpenAI's own implementation replaced 5–6 hours of weekly prep work per sales rep. For a team of 20 reps, that's 100–120 hours per week redirected to selling.

**Engineering: PR Review Summary Agent.** Monitors a GitHub PR channel for new pull requests, reads the diff and linked ticket, generates a plain-English summary of changes and risk areas, and posts it to the team's review Slack channel. Reduces time engineers spend context-switching between tools before starting a review.

**HR/People Ops: Onboarding Agent.** Triggered when a new employee row is added to a Google Sheet, the agent creates a Notion onboarding page from a template, posts welcome instructions to Slack, and schedules a 30-day check-in in Google Calendar. What took an HR manager 45 minutes per hire now runs automatically.

**Support: Escalation Triage Agent.** Monitors a Zendesk or support Slack channel, identifies tickets above a severity threshold, and posts a triage summary with suggested owner and priority to an internal channel. Runs on a 15-minute schedule during business hours.

**Finance: Weekly Expense Report Agent.** Pulls expense submissions from a Google Sheet or Expensify export, flags anomalies against policy, and posts a formatted summary to the finance Slack channel every Monday morning.

The pattern across all of these: the agent replaces the human as the connector between tools, not as the decision-maker. Humans still approve, redirect, and adjust — the agent handles the assembly.

## Deploying Workspace Agents in Slack

Deploying a workspace agent directly in Slack is one of the most practical configurations for teams, because it puts the agent where work already happens. OpenAI supports two Slack deployment modes: @mention activation and channel monitoring.

In @mention mode, any team member can trigger the agent by mentioning it in a Slack message: `@DealBriefAgent prep for Acme Corp`. The agent reads the message, executes its workflow, and posts a reply in the thread. This is ideal for on-demand, request-driven use cases where the team wants control over when the agent runs.

In channel monitoring mode, the agent watches a specified Slack channel for events — new messages, specific keywords, or message patterns — and runs automatically when the trigger condition is met. This is ideal for background workflows like support triage, where you don't want a human to have to explicitly invoke the agent every time.

To connect an agent to Slack, navigate to the agent's integration settings, select Slack, and authenticate with your workspace. You'll specify which channels the agent can read and post to. Admins can restrict channels at the workspace level to prevent agents from accessing sensitive Slack data.

One practical note: agents deployed in Slack still respect ChatGPT workspace permissions. If a user's ChatGPT account doesn't have access to a specific Salesforce field, the agent running on their behalf won't access it either. Permissions flow through the individual user's connected account, not the agent itself.

## Integrations: Slack, Salesforce, Google Drive, Notion & More

Workspace agents launched with a substantial integration library covering the most common enterprise SaaS tools. Each integration uses OAuth to connect a user's account and exposes read/write capabilities to the agent — subject to the tool-level permissions you grant in the agent builder.

At launch, integrations include:

- **Slack** — read messages, post messages, monitor channels, send DMs
- **Gmail** — read email, draft and send messages, label threads
- **Google Drive** — read and write documents, search files, create folders
- **Google Sheets** — read and update spreadsheet data, append rows
- **Google Calendar** — read events, create and update calendar entries
- **Google Docs** — read, edit, and create documents
- **Salesforce** — read opportunity, account, and contact records; update fields
- **Notion** — read pages and databases, create and update content
- **Atlassian Rovo** — access Jira issues and Confluence pages
- **Microsoft apps** — Teams, Outlook, OneDrive (via Microsoft connector)

OpenAI has stated additional integrations are in development for the post-preview release. The architecture is extensible: enterprises with custom internal tools can use OpenAI's API to build custom action connectors, similar to how custom GPT actions worked but with the full agent execution context available.

A key constraint: each integration is scoped to the individual user's account. An agent built by a Sales Consultant connects to that person's Salesforce and Slack. If the team wants a shared agent that accesses a shared service account, the agent needs to be configured under that shared account or a designated service user.

## Pricing & Credits: What Happens After May 6, 2026

Workspace agents are free during the research preview period, which ends May 6, 2026. After that date, agent runs consume Codex credits, which are purchased or earned through the promotional program.

The credit model is consumption-based: you pay for the tokens the agent uses during each run. A simple agent that reads a 500-word Slack message and posts a 200-word summary will use far fewer credits than one that reads a 50-page Google Drive document, queries Salesforce three times, and generates a structured report. OpenAI has not published a per-token credit rate as of this writing, but the Codex-only seat pricing is described as competitive with GPT-4 API pricing.

**Promotional credits:** Eligible ChatGPT Business workspaces earn $100 in credits for each new Codex seat activated, up to $500 total (five seats). This promotion started April 2, 2026. If your workspace hasn't activated Codex seats yet, doing so before May 6 maximizes your credit runway for the post-free period.

**Codex-only seats:** These are a separate seat type from standard ChatGPT Business seats. A Codex-only seat user can run workspace agents and access Codex but does not get the full ChatGPT conversational interface. This is designed for power users who primarily interact with agents rather than chat — and they have no rate limits.

**Budgeting guidance:** Estimate monthly credits by auditing your planned agents for run frequency × average context size × number of active agents. For most small to medium teams (under 50 users, 3–5 agents), the promotional credits should cover two to three months of post-free usage at moderate volume.

## Admin Controls, Permissions & Governance for Enterprise Teams

Workspace agents introduce new governance surface area for IT and security teams. Admins control which users can create agents, which integrations are available at the workspace level, and what data those agents can access.

Workspace-level controls are managed in the ChatGPT admin console. Key settings include: who can create agents (all users, specific groups, or admins only), which integrations are enabled (an admin can disable Salesforce at the workspace level even if individual users have connected it), and whether agents can run autonomously or require manager approval before becoming active.

Agent-level audit logs are available for Enterprise plans. These logs record every agent run — timestamp, trigger type, tools called, data accessed, and output posted. For regulated industries (finance, healthcare, legal), these logs are the audit trail required by compliance policies. Retention and export settings for these logs should be configured before agents go into production.

Permissions follow the principle of connected accounts: an agent runs under the identity of the user who built it, using that user's OAuth tokens for each connected integration. This means agents inherit the user's access controls — if a user can't read a Salesforce field, their agent can't either. For enterprise deployments, this also means agents are subject to the same data loss prevention (DLP) and access review policies as the human user.

**Recommended admin setup checklist:**

1. Decide who can create agents and set workspace-level creator permissions
2. Audit which integrations are appropriate for your data classification policies and disable any that aren't
3. Define a mandatory review step for agents that will post to public Slack channels or send email
4. Enable audit logging and set retention to match your compliance policy
5. Document a process for reviewing and deactivating agents when the creator leaves the organization

## ChatGPT Workspace Agents vs Microsoft Copilot vs Google Workspace AI

Workspace agents are entering a market where Microsoft Copilot and Google have been shipping enterprise AI automation for over a year. The comparison matters for teams choosing a primary platform or evaluating where to consolidate.

ChatGPT Workspace Agents, Microsoft Copilot Agents, and Google Workspace AI all allow non-technical users to build autonomous workflows that connect SaaS tools. The differentiators are model quality, integration depth, and the depth of control over agent behavior.

**Model and reasoning quality:** ChatGPT workspace agents are powered by Codex, which has a strong advantage in tasks that require code generation and multi-step reasoning over structured data. Microsoft Copilot uses GPT-4o (via Azure OpenAI) and has deep integration with the Microsoft 365 graph. Google Workspace AI uses Gemini and has native integration with Google's data layer. For teams already in Google Workspace, Google's agents have data access advantages. For mixed or Microsoft-heavy stacks, Copilot Agents have structural advantages. For teams that prioritize model capability and integration breadth, ChatGPT Workspace Agents are competitive.

**Integration breadth:** At launch, ChatGPT Workspace Agents support more third-party integrations (Salesforce, Notion, Atlassian) than Microsoft Copilot's native agent builder, which is focused primarily on Microsoft 365 connectors. Google's integration library is narrower still but growing.

**Agent control:** ChatGPT workspace agents offer the most granular control over agent behavior through plain-language configuration — trigger conditions, pause rules, process steps, compliance rules. Microsoft Copilot's agent builder is simpler but less flexible. Google's agent configuration is the least mature at this writing.

| Dimension | ChatGPT Workspace Agents | Microsoft Copilot Agents | Google Workspace AI |
|---|---|---|---|
| Underlying model | Codex (OpenAI) | GPT-4o (Azure) | Gemini |
| Best for | Mixed stack, code-heavy tasks | Microsoft 365-centric teams | Google Workspace-native teams |
| Third-party integrations | Broadest at launch | Microsoft-focused | Growing |
| Agent control granularity | High | Moderate | Low |
| Pricing model | Credit-based (post-May 6) | Copilot+ seats | Included with Workspace |
| Non-technical builder | Yes | Yes | Yes |

For teams on ChatGPT Business or Enterprise already, workspace agents are the natural next step — no new vendor, no new SSO integration, and the team's existing ChatGPT familiarity transfers directly to agent building.

## Getting Started Checklist for Teams

A structured rollout ensures your team gets value from workspace agents before the free tier ends and builds governance habits that scale as agent count grows.

**Week 1: Foundation**
- [ ] Confirm your workspace is on Business, Enterprise, Edu, or Teachers plan
- [ ] Activate Codex seats for power users to claim promotional credits ($100/seat, up to $500)
- [ ] Connect integrations your team uses: Slack, Google Workspace, Salesforce, Notion
- [ ] Set workspace-level creator permissions in the admin console
- [ ] Enable audit logging (Enterprise)

**Week 2: Build your first three agents**
- [ ] Identify three high-repetition workflows that cross two or more tools
- [ ] Build each agent using the step-by-step process above
- [ ] Test each agent with real data in a staging Slack channel before going live
- [ ] Define pause/stop rules for each agent that routes edge cases to a human

**Week 3: Deploy and measure**
- [ ] Deploy agents to production channels and trigger points
- [ ] Track time saved per agent over the first week of live runs
- [ ] Collect team feedback on output quality and adjust instructions accordingly
- [ ] Document each agent's purpose, owner, and data access in a shared Notion page

**Before May 6: Finalize**
- [ ] Review agent run logs to estimate credit consumption per agent per month
- [ ] Set a credit budget in the admin console (Enterprise)
- [ ] Decide which agents to keep active post-free tier based on time-savings ROI

## FAQ

**Do ChatGPT Workspace Agents require engineering skills to build?**
No. OpenAI designed the agent builder for non-technical users. You write instructions in plain language — role, trigger, process steps, compliance rules — and the Codex backend handles the execution logic. The Sales Consultant example from OpenAI's own team was built end-to-end without involving engineering.

**What happens to our existing Custom GPTs when workspace agents launch?**
Your Custom GPTs continue to function, but OpenAI has announced plans to eventually deprecate Custom GPTs for Business and Enterprise in favor of workspace agents. There is no hard cutoff date announced yet, but teams should plan migration. Most configuration from a Custom GPT (system prompt, knowledge files, connected actions) transfers directly to a workspace agent.

**Can workspace agents access data from outside our organization?**
Agents can access any integration you connect — including external services like Salesforce or Notion — but only using the OAuth credentials of the agent creator. Agents cannot access data from other organizations' ChatGPT workspaces. Admins can restrict which integrations are available at the workspace level.

**How is workspace agent pricing calculated after May 6, 2026?**
Pricing is credit-based, tied to Codex token consumption per agent run. Token usage varies by the size of inputs (documents read, messages processed) and outputs (text generated, code executed). Codex-only seats are pay-as-you-go with no rate limits. Standard Business/Enterprise seats will have credit allocations included — specifics will be published before May 6.

**Can we run workspace agents in Slack without users needing a ChatGPT account?**
Users who @mention or interact with an agent in Slack do not need a separate ChatGPT account — the agent runs under the creator's workspace account. However, the agent builder and configuration interface are only accessible to users with a ChatGPT Business/Enterprise seat. Team members can trigger and receive output from agents without seats; they just can't build or edit them.