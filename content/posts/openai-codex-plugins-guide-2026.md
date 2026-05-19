---
title: "OpenAI Codex Plugins Guide: 90+ Enterprise AI Workflow Integrations (2026)"
date: 2026-05-19T00:04:41+00:00
tags: ["openai-codex", "enterprise-ai", "plugins", "workflow-automation", "devops"]
description: "Complete guide to OpenAI Codex's 90+ plugins for enterprise teams — categories, governance, CLI setup, custom development, and competitor comparison."
draft: false
cover:
  image: "/images/openai-codex-plugins-guide-2026.png"
  alt: "OpenAI Codex Plugins Guide: 90+ Enterprise AI Workflow Integrations"
  relative: false
schema: "schema-openai-codex-plugins-guide-2026"
---

OpenAI Codex plugins are pre-built integrations that connect Codex's AI coding agent to external tools — from Slack and GitHub to Jira and CircleCI — letting developers trigger multi-step workflows across your entire software stack without switching contexts. As of April 2026, the marketplace offers 90+ plugins across seven categories, and enterprise teams at Cisco, Rakuten, and Ramp are using them to automate developer workflows that previously required custom tooling.

## What Are OpenAI Codex Plugins? (The 2026 Plugin System Explained)

OpenAI Codex plugins are modular extensions that give the Codex AI agent access to external services, APIs, and tools beyond its default code-generation capabilities. Launched on March 26, 2026 with 20+ initial integrations, the plugin marketplace expanded to 90+ additional plugins in April 2026 alongside Codex's computer-use and in-app browser features. A plugin tells Codex *how* to interact with an external system — authenticating, reading data, writing back results — so the agent can operate on your behalf inside Slack, GitHub, Neon databases, or Figma without requiring custom API code. By April 21, 2026, Codex had reached 4 million+ weekly active developers (up from 3 million just two weeks prior), and ChatGPT Business and Enterprise Codex usage grew 6x since January 2026. Plugins are the engine driving that growth: they convert a standalone AI coding assistant into a cross-platform workflow orchestrator that operates where your teams already work.

The key distinction from simple API calls: Codex plugins are persistent connections with memory, governance controls, and admin policy enforcement. Enterprise IT admins can mandate specific plugins for all users, restrict others, and log all plugin-triggered actions to SIEM systems for compliance.

## Plugin Architecture: Skills, Apps, and MCP Servers

OpenAI Codex's plugin system has three distinct integration types, each designed for a different use case. Understanding which type to use determines how deeply Codex can act on your behalf, how much custom code you need to write, and what governance controls apply. Choosing the wrong type is the most common mistake enterprises make when first deploying Codex plugins — teams either under-invest with a shallow App integration when they need a full MCP server, or over-engineer a Skill for a straightforward service-to-service call.

**Skills** are lightweight, function-level extensions that expose a specific action or capability to Codex. A Skill might wrap a REST endpoint (e.g., "create a Linear ticket with these fields") or a local script (e.g., "run the test suite on this branch"). Skills are the fastest to author — you define a JSON schema describing the action, and Codex calls it like a function. Skills are stateless by design.

**Apps** are deeper integrations with OAuth2 authentication and bidirectional data flow. An App integration connects Codex to a SaaS platform (Slack, Notion, Google Drive) and enables reading *and* writing: reading channel history to understand context, then posting a summary. Apps handle token refresh automatically and appear in the plugin marketplace as first-class connectors.

**MCP Servers** (Model Context Protocol) are the most powerful integration type. An MCP server runs as a local or remote process that Codex communicates with over a standardized protocol. MCP servers enable arbitrary tool execution, long-running processes, database queries, and complex stateful workflows. For enterprise self-hosted tooling (internal CI systems, private Kubernetes clusters, custom data stores), MCP servers are the correct choice.

| Type | Auth | Stateful | Custom Code | Best For |
|------|------|----------|-------------|----------|
| Skill | API Key / None | No | Minimal (JSON schema) | Single-action wrappers |
| App | OAuth2 | Yes | Low (marketplace connector) | SaaS read/write integrations |
| MCP Server | Any | Yes | High (custom server) | Internal tooling, complex workflows |

## The Complete List of 90+ Codex Plugins by Category

The Codex plugin marketplace organizes 90+ integrations into seven primary categories: communication and collaboration, project management, CI/CD and DevOps, databases and data infrastructure, code review and security, design and documentation, and Microsoft enterprise productivity. OpenAI released 20 initial plugins on March 26, 2026, then expanded to 90+ additional plugins in April 2026 alongside the computer-use and in-app browser features — making Codex one of the largest enterprise AI plugin ecosystems available. Each category reflects a phase of the software development lifecycle where Codex can reduce context-switching: from ideation (project management, design) through building (databases, CI/CD) to shipping and monitoring (security, DevOps). Below is a representative breakdown with key plugins in each area. The full catalog is accessible via `codex plugin list --all` in the CLI or at platform.openai.com/codex/plugins. Plugin availability varies by region and subscription tier — Business and Enterprise plans have access to all 90+ plugins, while Plus users get the core marketplace subset.

### Communication & Collaboration Plugins (Slack, Gmail, Notion, Google Drive)

Communication plugins give Codex read and write access to the platforms where teams coordinate work, enabling it to post status updates, retrieve meeting notes, summarize threads, and file information automatically. Slack is the most-used Codex plugin by volume: developers configure Codex to post PR review summaries, deployment alerts, and bug triage notes directly to team channels — eliminating the manual copy-paste cycle that burns 20-30 minutes per incident. Gmail integration lets Codex draft replies to client-reported bugs, extract action items from email threads, and file issues without leaving the terminal. Notion integration covers reading and writing project wikis, sprint docs, and runbook pages. Google Drive access enables Codex to retrieve architecture docs, ingest PRDs as context, and write generated documentation back to shared drives. Microsoft 365 integration (Teams, Word, SharePoint) launched in April 2026 as part of the enterprise productivity cluster, making Codex viable in Microsoft-first environments where Google Workspace isn't used.

**Key plugins:** Slack, Gmail, Notion, Google Drive, Microsoft Teams, SharePoint, Outlook, Zoom, Box

### Project Management Plugins (Atlassian Rovo/JIRA, Linear, GitLab Issues)

Project management plugins connect Codex to ticketing and roadmap systems, letting the agent create, update, and query issues programmatically. Atlassian Rovo — launched as a dedicated Codex plugin in April 2026 — provides deep JIRA integration with semantic search across your backlog, enabling Codex to find duplicate tickets, link related issues, and estimate story points based on historical velocity. Linear's Codex plugin is popular with engineering-first teams: Codex can create Linear issues from TODO comments in code, auto-assign them based on code ownership, and close them when the corresponding PR merges. GitLab Issues integration covers the full GitLab workflow for teams that don't use GitHub, including milestones, labels, and merge request linking. For teams using multiple trackers simultaneously, Codex can sync state across systems — creating a Jira ticket and a corresponding Linear issue from a single natural-language command.

**Key plugins:** Atlassian Rovo (JIRA), Linear, GitLab Issues, GitHub Issues, Asana, Monday.com, Shortcut (formerly Clubhouse)

### CI/CD & DevOps Plugins (CircleCI, GitHub Actions, Render, Cloudflare)

CI/CD plugins give Codex direct access to pipeline systems, enabling it to trigger builds, read failure logs, diagnose test failures, and propose fixes — all from within a single agentic session. CircleCI's Codex plugin (launched April 2026) lets the agent inspect failed pipeline steps, retrieve logs, and generate patch commits that re-run the pipeline to verify the fix. This closes the inner loop that typically requires switching between terminal, CI dashboard, and code editor. GitHub Actions integration enables Codex to read workflow files, suggest optimizations for cache hit rates, and create new workflow files from natural language descriptions. Render integration supports deployment management — Codex can query deployment status, roll back a release, and set environment variables. Cloudflare integration covers Workers, Pages, and R2 — Codex can deploy edge functions and manage configurations via Workers API. For Kubernetes-heavy environments, an MCP server pattern is recommended over the App-layer plugins to retain full kubectl access.

**Key plugins:** CircleCI, GitHub Actions, Render, Cloudflare Workers, Vercel, Railway, Fly.io, Jenkins (via MCP), ArgoCD (via MCP)

### Database & Data Plugins (Neon by Databricks, Hugging Face)

Database plugins give Codex the ability to query, migrate, and manage data stores within a governed session. Neon by Databricks — one of the April 2026 additions — provides serverless Postgres access with branch-based development: Codex can spin up a database branch, run migrations against it, validate results, and delete the branch, all without touching production. Hugging Face integration enables Codex to pull models, datasets, and inference endpoints into coding sessions — useful for ML engineers building fine-tuning pipelines or evaluation harnesses. PlanetScale, Supabase, and MongoDB Atlas integrations follow the same pattern: Codex gets read/write access with credentials managed by the plugin's OAuth layer, not stored in plaintext in prompts.

**Key plugins:** Neon by Databricks, Hugging Face, Supabase, PlanetScale, MongoDB Atlas, Redis Cloud, Snowflake (via MCP), BigQuery (via MCP)

### Code Review & Security Plugins (CodeRabbit, Sentry, Datadog)

Code review and security plugins extend Codex into the quality and observability layer of the software lifecycle. CodeRabbit's Codex plugin (April 2026) integrates AI-powered code review directly: Codex can request a CodeRabbit review pass on its own output before committing, creating a self-review loop that catches issues before they reach human reviewers. Sentry integration gives Codex access to production error events — the agent can correlate a Sentry error fingerprint with the relevant code path and propose a targeted fix rather than guessing from stack traces. Datadog integration covers dashboards, monitors, and logs: Codex can read metric anomalies, correlate them with recent deploys, and generate runbook entries. Snyk and Semgrep integrations add SAST scanning to the loop — Codex can run a security scan against a proposed change and iterate until the finding is resolved.

**Key plugins:** CodeRabbit, Sentry, Datadog, Snyk, Semgrep, PagerDuty, New Relic, Grafana (via MCP)

### Design & Documentation Plugins (Figma, Box)

Design plugins connect Codex to the visual and document layers of product development. Figma integration lets Codex read component specifications, extract design tokens, and generate corresponding React/CSS code from a Figma file URL — reducing the designer-to-developer handoff gap. Box integration covers enterprise document storage: Codex can retrieve architecture decision records (ADRs), compliance documents, and technical specifications stored in Box, using them as context for code generation without requiring the developer to manually attach files. Confluence and Notion serve similar roles for teams that prefer those platforms.

**Key plugins:** Figma, Box, Confluence, Miro (via MCP), Adobe XD (via MCP)

### Microsoft Suite & Enterprise Productivity Plugins

Microsoft ecosystem integrations launched in April 2026, making Codex viable for the substantial portion of enterprise customers that standardize on Microsoft 365. Teams integration enables posting to channels and retrieving conversation history. SharePoint access covers document libraries and wiki pages. Azure DevOps integration adds JIRA-equivalent project management for Microsoft shops, including boards, pipelines (Azure Pipelines), and artifact management. Power BI integration is in preview, allowing Codex to query data models and generate DAX expressions. For enterprises on Microsoft's Copilot ecosystem, OpenAI positions Codex plugins as a complement rather than a replacement — Codex handles code-centric tasks while Copilot handles document and presentation tasks.

**Key plugins:** Microsoft Teams, SharePoint, Outlook, Azure DevOps, Azure Pipelines, OneDrive, Power BI (preview)

## Enterprise Governance: Managing Plugins at Scale with JSON Policies

Enterprise IT admins control Codex plugin availability through JSON policy files pushed via the OpenAI admin API, enabling department-wide rollout or restriction without touching individual user accounts. The policy system launched with three states: `INSTALLED_BY_DEFAULT` (plugin is active for all users in the org), `AVAILABLE` (users can install it themselves), and `NOT_AVAILABLE` (plugin is blocked). Cisco's IT team, for example, sets internal-only MCP server plugins to `INSTALLED_BY_DEFAULT` while restricting consumer SaaS plugins that haven't passed security review to `NOT_AVAILABLE` — ensuring engineers can't inadvertently send proprietary code to unapproved third-party services. Governance policies apply at the organization level or can be scoped to specific groups, enabling different policies for the infra team (full DevOps plugin access) versus the compliance team (read-only integrations). All plugin actions are logged with actor identity, timestamp, and payload hash, which can be streamed to SIEM systems like Splunk or Microsoft Sentinel via the audit log API. eDiscovery support means legal teams can retrieve all Codex-plugin interactions for a given user within a date range.

```json
{
  "plugins": {
    "slack": "INSTALLED_BY_DEFAULT",
    "github": "INSTALLED_BY_DEFAULT",
    "circleci": "AVAILABLE",
    "figma": "AVAILABLE",
    "consumer-app-x": "NOT_AVAILABLE"
  }
}
```

## How to Install and Configure Codex Plugins (CLI Guide)

Installing Codex plugins takes under two minutes for marketplace plugins and requires only the Codex CLI and appropriate service credentials. The CLI plugin management system uses `codex plugin` subcommands that mirror familiar package manager patterns, making adoption straightforward for developer teams already comfortable with npm or pip workflows. Enterprise admins can pre-install plugins via the API before users ever run a CLI command, ensuring day-one availability for onboarding developers.

**Install a plugin from the marketplace:**
```bash
codex plugin install slack
codex plugin install github
codex plugin install circleci
```

**Authenticate the plugin (OAuth2 flow opens in browser):**
```bash
codex plugin auth slack
# Opens browser → authorize → token stored in ~/.codex/credentials
```

**List installed plugins and their status:**
```bash
codex plugin list
# NAME       TYPE    STATUS    VERSION
# slack      app     active    1.4.2
# github     app     active    2.1.0
# circleci   app     active    1.0.5
```

**Add a custom MCP server:**
```bash
codex plugin add-mcp --name internal-ci \
  --command "node /path/to/mcp-server.js" \
  --env CI_TOKEN=$CI_TOKEN
```

**Use a plugin within a Codex session:**
```bash
codex "check CircleCI for the last failed build on main, find the failing test, and fix it"
# Codex automatically invokes the circleci plugin to retrieve logs
```

**Remove a plugin:**
```bash
codex plugin remove figma
```

Plugin credentials are stored in an encrypted local keychain (macOS Keychain, Linux Secret Service, or Windows Credential Manager) — Codex never transmits raw credentials to OpenAI servers. Enterprise deployments can instead use a central credential vault with the `--credential-provider` flag pointing to a HashiCorp Vault endpoint.

## Building Custom Codex Plugins: Skills, Apps, and MCP Servers

Custom Codex plugins follow a well-defined spec that any developer with API familiarity can implement in an afternoon for a Skill, or a few days for a full MCP server. The fastest path is a Skill wrapping an internal REST API — define the JSON schema, register it, and Codex can invoke it within minutes. For teams with proprietary internal tooling not covered by the marketplace, custom plugins are the primary way to bring Codex into existing workflows without rewriting those tools.

**Building a Skill (simplest):**

Create a `skill.json` describing your action:
```json
{
  "name": "deploy_staging",
  "description": "Deploy the current branch to the staging environment",
  "parameters": {
    "branch": { "type": "string", "description": "Branch name to deploy" },
    "environment": { "type": "string", "enum": ["staging", "preview"] }
  },
  "endpoint": "https://internal-deploy.example.com/api/deploy",
  "auth": { "type": "bearer", "token_env": "DEPLOY_TOKEN" }
}
```

Register the Skill:
```bash
codex plugin register-skill ./skill.json
```

**Building an MCP Server (maximum flexibility):**

An MCP server implements the Model Context Protocol, exposing tools as named functions with typed inputs and outputs. The OpenAI-provided MCP SDK handles the protocol framing:

```python
from openai_mcp import MCPServer, tool

server = MCPServer(name="internal-ci")

@tool
def get_pipeline_status(pipeline_id: str) -> dict:
    """Retrieve CI pipeline status from internal system"""
    return internal_ci_client.get_status(pipeline_id)

@tool
def trigger_deploy(branch: str, target: str) -> dict:
    """Trigger a deployment to the specified target environment"""
    return internal_deploy_client.deploy(branch=branch, target=target)

server.run()  # Listens on stdio by default
```

Connect the MCP server to Codex:
```bash
codex plugin add-mcp --name internal-ci --command "python3 /opt/mcp/ci_server.py"
```

For enterprise publishing (making your custom plugin available to your whole org), package the plugin and submit via the admin API. OpenAI reviews plugins for the public marketplace but allows private org-scoped plugins without review.

## Enterprise Use Cases: Cisco, Rakuten, Ramp, and Virgin Atlantic

Real enterprise deployments illustrate how Codex plugins move from demo to production value. These are not hypothetical workflows — they represent reported deployment patterns from OpenAI's enterprise partner announcements and public case study material.

**Cisco** uses Codex with GitHub, Sentry, and internal MCP server plugins to power an autonomous bug-triage workflow: when Sentry fires an alert, Codex retrieves the error context, finds the relevant code via GitHub, proposes a fix, and files a PR — all without engineer intervention. Cisco engineering leads reported 40% reduction in time-to-patch for P3/P4 bugs in the first deployment quarter.

**Rakuten** (Japanese e-commerce and fintech) integrated Codex with Jira, CircleCI, and Slack to close the sprint-ceremony gap: Codex attends planning by reading the Jira backlog, estimates complexity based on codebase analysis, and posts summaries to the Slack planning channel before engineers join. Teams reported 30-minute reduction per sprint planning session.

**Ramp** (B2B fintech) uses Codex plugins to automate compliance check workflows: Codex reads new code changes, runs Semgrep SAST scans via plugin, checks against internal policy rules stored in Notion, and files Linear tickets for any violations — replacing a manual compliance review step that previously required a dedicated security engineer rotation.

**Virgin Atlantic** uses Microsoft Teams and Azure DevOps plugins to coordinate cross-team releases: Codex monitors pipeline status in Azure DevOps, posts deployment readiness summaries to Teams channels, and can trigger rollbacks via the Azure DevOps plugin when error rates spike.

These use cases share a common pattern: plugins eliminate the manual data-fetching and status-posting that consumes developer time without producing code.

## Codex Plugins vs. Competitors: Claude Code, GitHub Copilot, Cursor

The enterprise AI coding assistant market in 2026 has three viable plugin ecosystems, each with different strengths. Choosing the right platform depends on your existing tool stack, governance requirements, and whether you prioritize breadth of marketplace coverage or depth of custom extension support.

| Dimension | Codex Plugins | Claude Code Extensions | GitHub Copilot Extensions |
|-----------|--------------|------------------------|--------------------------|
| Marketplace size | 90+ (April 2026) | ~40 (community MCP servers) | ~30 (verified extensions) |
| Enterprise governance | JSON policy files, org-level admin | CLAUDE.md rules, settings.json | GitHub org settings |
| Custom plugin type | Skill / App / MCP server | MCP server | VS Code extension API |
| Auth management | Encrypted keychain + vault support | Manual MCP config | GitHub OAuth |
| Audit logging | Full SIEM integration | Limited | GitHub audit log |
| Microsoft ecosystem | Strong (April 2026 additions) | Weak | Native (GitHub = Microsoft) |
| Google ecosystem | Strong (Drive, Gmail, Meet) | Moderate | Weak |

Claude Code's extension model is more developer-friendly for custom MCP servers — the MCP ecosystem is language-agnostic and Claude Code has slightly more flexible tool-calling. However, it lacks the centralized marketplace and enterprise governance controls. Claude Code accounts for approximately 4% of all GitHub public commits, indicating significant developer adoption — but Codex's 4 million+ weekly active users and 6x enterprise growth give it distribution advantage.

GitHub Copilot Extensions benefit from native GitHub integration and are the natural choice for teams already paying for GitHub Enterprise Cloud. The extension model is VS Code-centric, making it less suitable for teams that use terminal-first workflows.

For enterprises selecting a primary platform: **Codex plugins win on governance controls and marketplace breadth**; Claude Code wins on MCP flexibility and model quality per benchmark; Copilot Extensions win on GitHub-native integration. Most large enterprises are running two of the three in parallel, with Codex handling autonomous agentic workflows and Copilot or Claude Code handling interactive coding assistance.

## Security, Compliance, and Audit Logging for Enterprise Deployments

Enterprise Codex plugin security operates across four layers: authentication, authorization, data handling, and audit. Each layer has specific controls that compliance and security teams evaluate during vendor review. OpenAI published a SOC 2 Type II report for Codex Enterprise in Q1 2026 and supports SCIM provisioning for identity management, satisfying most enterprise security checklists without customization.

**Authentication:** Plugin credentials are stored in OS-native encrypted keystores. For enterprise deployments, a `--credential-provider` flag delegates credential retrieval to HashiCorp Vault, AWS Secrets Manager, or Azure Key Vault — ensuring no credentials touch local disk in plaintext. OAuth tokens are short-lived (1-hour access tokens, 30-day refresh tokens) and scoped to the minimum required permissions per plugin.

**Authorization:** The JSON policy system (described in the Governance section) is the primary authorization control. Plugins can't be installed without appearing in the policy allow-list. Codex itself operates within a sandboxed execution environment for agentic tasks — it cannot access local filesystem paths outside the working directory unless explicitly granted via the `--allow-fs` flag.

**Data handling:** Code context sent to Codex is processed under OpenAI's Enterprise Data Processing Agreement (DPA). Enterprise customers have zero data retention by default — code snippets used in Codex sessions aren't stored for model training. Plugin-mediated data (e.g., Slack messages read by Codex) is subject to both OpenAI's DPA and the respective SaaS vendor's data terms.

**Audit logging:** All plugin invocations are logged with: actor (user ID), timestamp, plugin name, action called, parameters (redacted at policy-defined sensitivity level), and response status. Logs are available via the Admin API for 90 days and can be streamed to Splunk, Microsoft Sentinel, or other SIEM systems via webhook. For eDiscovery, legal teams can retrieve all interactions for a given user within a date range via the Admin API.

## Getting Started: 5-Step Enterprise Rollout Plan for Codex Plugins

An enterprise Codex plugin rollout follows a predictable pattern: start narrow (two or three core plugins for a pilot team), validate governance and security controls, then expand by team and plugin category. Skipping the pilot phase is the most common mistake — enterprises that roll out all 90+ plugins to all users simultaneously encounter authentication confusion, governance gaps, and support overload. Cisco's rollout lead reported that a 4-week pilot with 15 engineers produced the governance policy file that scaled cleanly to 2,000+ engineers in week five.

**Step 1: Identify your 3 core plugins.** For most engineering teams, GitHub + Slack + your CI system (CircleCI, GitHub Actions, etc.) covers 80% of the friction points Codex can eliminate. Start here.

**Step 2: Author your governance policy.** Define which plugins are `INSTALLED_BY_DEFAULT`, which are `AVAILABLE`, and which are `NOT_AVAILABLE`. Review with InfoSec before deployment. Use the template below as a starting point:

```json
{
  "plugins": {
    "github": "INSTALLED_BY_DEFAULT",
    "slack": "INSTALLED_BY_DEFAULT",
    "circleci": "INSTALLED_BY_DEFAULT",
    "linear": "AVAILABLE",
    "sentry": "AVAILABLE",
    "figma": "AVAILABLE"
  },
  "audit_log_webhook": "https://siem.internal.example.com/codex-events",
  "credential_provider": "vault://secrets/codex-plugins"
}
```

**Step 3: Run a 2-week pilot with a volunteer team.** Collect time-on-task metrics before and after for three workflows: bug triage, PR review notification, and CI failure diagnosis. These three workflows have the clearest before/after deltas.

**Step 4: Document your MCP server needs.** After the pilot, you'll have a clear list of internal tools not covered by marketplace plugins. Assign a platform team sprint to build MCP server wrappers for the top two or three tools.

**Step 5: Expand org-wide with phased rollout.** Push the governance policy org-wide via Admin API. Use `INSTALLED_BY_DEFAULT` only for validated plugins; leave others `AVAILABLE` for self-service discovery. Review audit logs weekly for the first month.

For enterprises with Accenture, Capgemini, CGI, Cognizant, Infosys, PwC, or TCS as system integrators, these firms have certified Codex plugin deployment practices as of Q2 2026 — engaging one of them can compress a 12-week rollout to 4-6 weeks.

---

## FAQ

**Q: How many Codex plugins are available in 2026?**

As of April 2026, OpenAI has released 90+ plugins in the Codex marketplace, up from 20+ at the initial March 26, 2026 launch. The marketplace grows monthly; the current full list is available at platform.openai.com/codex/plugins or via `codex plugin list --all`.

**Q: Can I use Codex plugins without a ChatGPT Enterprise subscription?**

Codex plugins are available across ChatGPT Plus, Business, and Enterprise plans, but enterprise governance features (JSON policy files, SIEM integration, eDiscovery, SCIM) require a Business or Enterprise subscription. Individual Plus users can install plugins manually from the marketplace but don't get org-level admin controls.

**Q: How do Codex plugins handle API credentials and secrets?**

Codex stores plugin credentials in your OS-native encrypted keystore (macOS Keychain, Linux Secret Service, Windows Credential Manager). Enterprise deployments can use the `--credential-provider` flag to delegate credential retrieval to HashiCorp Vault, AWS Secrets Manager, or Azure Key Vault, ensuring no secrets touch local disk. Codex never sends raw credentials to OpenAI servers.

**Q: What's the difference between a Codex Skill and an MCP server plugin?**

A Skill is a stateless, lightweight wrapper around a single API action (e.g., "create a Linear ticket"). It's defined in JSON and requires minimal code. An MCP server is a full process that Codex communicates with over the Model Context Protocol, supporting arbitrary tool definitions, stateful sessions, and complex multi-step operations. Use Skills for simple API wrapping; use MCP servers for internal systems with complex logic.

**Q: How do Codex plugins compare to GitHub Copilot Extensions for enterprise teams?**

Codex plugins have a larger marketplace (90+ vs. ~30), stronger enterprise governance controls, and better non-GitHub SaaS coverage. Copilot Extensions have native GitHub integration and VS Code IDE embedding. For teams that primarily live in GitHub and VS Code, Copilot Extensions may be more ergonomic. For terminal-first teams running autonomous agentic workflows, Codex plugins provide more complete enterprise tooling.
