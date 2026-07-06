---
title: "Dataverse Plugin for Coding Agents Guide 2026: Build Enterprise Apps From Agent Prompts"
date: 2026-07-06T12:00:00+00:00
tags: ["Dataverse", "MCP", "coding agents", "Claude Code", "GitHub Copilot", "Power Platform"]
description: "A production-minded guide to installing, configuring, and using the Dataverse plugin for Claude Code, GitHub Copilot, and Cursor in 2026 — with prompt patterns, governance, troubleshooting, and real enterprise workflows."
draft: false
cover:
  image: "/images/dataverse-plugin-coding-agents-guide-2026.png"
  alt: "Dataverse Plugin for Coding Agents Guide 2026"
  relative: false
schema: "schema-dataverse-plugin-coding-agents-guide-2026"
---

Microsoft's Dataverse plugin for coding agents landed in mid-2026 with support for Claude Code, GitHub Copilot, and Cursor. The idea is straightforward: instead of switching between a browser, PAC CLI, and the Power Platform admin center, you describe what you want in natural language and the agent handles the Dataverse work. In practice, the difference between a demo and a production workflow comes down to understanding what the plugin actually does under the hood, which tools it routes to, and where you still need governance.

I've been testing the plugin across several enterprise scenarios since the Build 2026 announcements. This guide covers installation, first prompts, real enterprise workflows, the tool routing model, governance gotchas, and the common errors that trip up teams moving from prototype to production.

## What Is the Dataverse Plugin for Coding Agents?

The Dataverse plugin is an open-source, MIT-licensed collection of Markdown skills with YAML frontmatter that coding agents can load and execute. Microsoft published it on GitHub at `microsoft/Dataverse-skills`, and it's available on the Claude, GitHub Copilot, and Cursor marketplaces.

When you install the plugin, your coding agent gains the ability to:

- Discover and describe Dataverse environments, tables, and metadata
- Create, read, update, and delete records
- Create and modify tables, columns, and relationships
- Import and export data
- Manage solutions and solution components
- Configure security roles, field-level security, business units, and auditing
- Run FetchXML queries and Power Fx expressions

The plugin does not talk to Dataverse directly. It routes work across four underlying interfaces depending on the task: the Dataverse MCP Server, the Dataverse SDK for Python, PAC CLI, and the Dataverse CLI. I'll cover that routing model in detail later, but the key point is that the plugin is a skill layer, not a new API.

## Dataverse Skills vs Dataverse MCP: The Difference That Matters

This is the most common confusion I see in teams adopting the plugin. The terms are used interchangeably in marketing, but they are different things.

**Dataverse Skills** (the plugin) is the set of agent-readable Markdown files that teach the coding agent *how* to work with Dataverse. Each skill file contains instructions, examples, and tool-selection guidance. When you install the plugin in Claude Code, the agent reads these skills and uses them to decide which underlying tool to call.

**Dataverse MCP Server** is the actual tool surface — the MCP endpoint at `https://{orgName}.crm.dynamics.com/api/mcp` that exposes tools like `search_data`, `create_record`, `describe`, and `read_query`. The plugin routes to MCP for interactive discovery and controlled actions.

The plugin also routes to PAC CLI for solution lifecycle work, the Dataverse SDK for Python for bulk operations, and the Dataverse CLI for environment management. The skill files are the agent's knowledge of *when* to use each interface.

If you already read my overview of [Dataverse as an Agent Data Platform](/posts/dataverse-agent-data-platform-2026/), the architecture there applies directly: the plugin is the agent-facing layer on top of the MCP, SDK, and CLI surfaces.

## Who Should Use It in 2026?

The plugin is useful for three groups, and the workflows differ for each:

**Developers building Dataverse solutions.** If you normally work in VS Code or Claude Code and need to create tables, write plugins, or manage solution components, the plugin saves the context-switch to the Power Platform admin center. I've found it most useful for rapid schema iteration — creating a table, adding columns, setting up relationships, and generating a test data set in one session without leaving the editor.

**RevOps and business analysts.** The plugin handles natural-language queries against CRM data. "Show me all accounts with renewal risk above 60% and no active support case" becomes a single prompt instead of a FetchXML debugging session. The trade-off is that you need to validate the query shape before trusting the results for reporting.

**Power Platform admins.** Security configuration, business unit setup, field-level security profiles, and auditing policies can all be managed through the plugin. The admin workflows are the highest-risk use case because a bad prompt can change security boundaries. I recommend read-only prompts first, then reviewed changes.

## Prerequisites: Environment, Permissions, PAC CLI, Agent Client, and MCP Access

Before the plugin works, you need five things in place:

**1. A Dataverse environment with MCP enabled.** The MCP server must be enabled and configured for your Power Platform environment. Admins control this through the Power Platform admin center under environment settings. Without this step, the plugin's MCP-routed commands will fail with connection errors.

**2. An authenticated PAC CLI session.** The plugin uses PAC CLI for auth, solution management, and environment operations. Run `pac auth create --url https://{org}.crm.dynamics.com` to establish a session. The plugin checks for an active auth profile before attempting most operations.

**3. The right Dataverse role.** The plugin inherits your Dataverse role. A System Administrator can do everything. A basic user role can read records but not create tables. I strongly recommend using a dedicated app registration or service principal with scoped permissions rather than your personal admin account, especially in shared or production environments.

**4. An MCP-compatible agent client.** Claude Code, GitHub Copilot (VS Code extension or CLI), and Cursor all support MCP clients. Each has slightly different setup steps. Claude Desktop also works but is less common for development workflows.

**5. The plugin installed.** Installation varies by client. For Claude Code, you add the plugin from the Claude marketplace or clone the GitHub repo and reference it in your Claude Code config. For GitHub Copilot, you install from the Copilot extension marketplace. For Cursor, you add it through the Cursor settings under MCP servers.

## How to Install the Dataverse Skills Plugin

The installation steps depend on your agent client. Here are the three paths I've tested:

**Claude Code.** The cleanest path is the Claude marketplace. Search for "Dataverse Skills" and install. Alternatively, clone the repo and add it to your Claude Code configuration:

```json
{
  "mcpServers": {
    "dataverse": {
      "command": "npx",
      "args": ["-y", "@microsoft/dataverse-mcp"]
    }
  }
}
```

**GitHub Copilot (VS Code).** Install the "Dataverse Skills" extension from the VS Code marketplace. After installation, Copilot detects Dataverse-related prompts and routes them through the plugin automatically. You can also use the GitHub Copilot CLI with the `--dataverse` flag if you prefer terminal-based workflows.

**Cursor.** Add the Dataverse MCP server in Cursor settings under Features > MCP Servers. Point it to the same `@microsoft/dataverse-mcp` package. Cursor's MCP support is newer and I've hit more edge cases here, particularly around tool timeout settings for long-running operations like data imports.

After installation, verify the plugin is active by running a simple discovery prompt: "List the tables in my Dataverse environment." If the agent returns table names, the plugin is connected.

## First Prompt: Connect to Your Dataverse Environment

Your first prompt should be a read-only discovery. This validates auth, MCP connectivity, and the agent's ability to route to the right tool:

> "Connect to my Dataverse environment at https://myorg.crm.dynamics.com and describe the account table. Show me the columns, data types, and any relationships."

A working plugin will return the table schema. If it fails, the most common causes are:

- No active PAC CLI auth profile — run `pac auth create` first
- MCP server not enabled for the environment — check admin settings
- The agent client doesn't have MCP support enabled — check your client config
- Wrong environment URL — the plugin needs the full Dynamics URL, not a Power Apps maker portal URL

Once discovery works, move to a data query:

> "Find the 10 most recently created accounts in my Dataverse environment. Show me the name, primary contact, and created date."

This tests the `search_data` or `read_query` tool routing. If the agent returns results, you have a working pipeline.

## Build an Enterprise App From a Prompt

The Build 2026 demo used a coffee shop scenario (Zava Coffee) to show end-to-end app creation. Here's a realistic enterprise version:

> "Create a new Dataverse table called 'Vendor Compliance' with columns for vendor name (text), compliance score (decimal), last review date (date), compliance status (choice: Compliant, Non-Compliant, Pending Review), and assigned reviewer (lookup to user). Add a relationship to the account table. Create a main form and a view showing non-compliant vendors sorted by score ascending."

The plugin routes this across multiple tools: `create_table` for the schema, `describe` to inspect the account table for the relationship, and potentially PAC CLI for form and view creation. The agent handles the sequencing, but you should inspect the result:

- Did it create the right columns with the right types?
- Is the choice column properly configured?
- Does the lookup relationship point to the correct target?
- Are the form and view usable in a model-driven app?

I've found that the plugin is good at schema creation but occasionally misinterprets column types. A "decimal" column might end up as a "float" or "money" type if the prompt isn't specific. Always verify the generated schema before promoting it.

## Import and Validate Real Business Data

The plugin can import data from CSV or Excel into Dataverse tables. This is where the routing model matters: for small imports (under 100 rows), the plugin uses MCP record creation. For larger imports, it should route to the Dataverse SDK for Python or the data import tools.

> "Import this CSV of vendor compliance data into the Vendor Compliance table. Map the columns: company_name -> vendor_name, score -> compliance_score, review_date -> last_review_date, status -> compliance_status. Skip rows where score is empty."

The plugin will attempt to parse the CSV, map columns, and create records. For imports over a few hundred rows, I've seen the agent fall back to generating a Python script using the Dataverse SDK and running it locally. That's actually the right behavior — MCP record creation one call at a time is not efficient for bulk loads.

After import, validate:

> "Count the records in the Vendor Compliance table. Show me 5 sample rows to verify the data looks correct."

## Query and Update CRM Records in Natural Language

The plugin shines for ad-hoc CRM queries that would normally require FetchXML or advanced Find:

> "Find all accounts in the 'Enterprise' segment with an active opportunity worth over $50,000 where the account owner is in the 'West' region. Show me the account name, opportunity value, owner name, and close date."

The agent translates this into a FetchXML query or uses `search_data` with filters. I've found the results are usually correct for straightforward queries, but complex multi-table joins can produce unexpected results. Always spot-check the generated FetchXML if the query matters for reporting.

For updates, the plugin handles record mutations:

> "Update the compliance status to 'Non-Compliant' for all vendors in the Vendor Compliance table where the score is below 40 and the last review date is more than 90 days ago."

This is a higher-risk operation. The plugin should confirm the scope before executing. If it doesn't ask for confirmation, that's a gap in your governance setup — I'll cover that in the governance section.

## Configure Security, Field-Level Access, Business Units, and Auditing

The admin workflows are the most powerful and the most dangerous. The plugin can configure security roles, field-level security profiles, business units, and auditing policies:

> "Create a field-level security profile called 'Compliance Readers' that grants read-only access to the compliance_score and compliance_status columns on the Vendor Compliance table. Assign it to the 'Sales Team' business unit."

> "Enable auditing on the Vendor Compliance table. Configure it to log all read and update operations on the compliance_score column."

These prompts work, but I strongly recommend running them in a development environment first. A misconfigured security profile can expose sensitive data or block legitimate access. The plugin does not have a dry-run mode — it executes changes immediately based on your role permissions.

My rule: never run security or auditing prompts against a production environment without a peer review. The plugin makes it easy to change security boundaries, and easy is not always safe.

## What Happens Under the Hood: PAC CLI, MCP, Python SDK, and Web API

The plugin's routing logic is the most important thing to understand for production use. When you give the agent a prompt, it decides which interface to use based on the task:

| Task | Interface | Why |
| --- | --- | --- |
| Environment discovery, auth | PAC CLI | PAC CLI handles auth profiles and environment metadata |
| Table/record discovery | Dataverse MCP (`search`, `describe`, `search_data`) | MCP is designed for interactive discovery |
| Record CRUD (single) | Dataverse MCP (`create_record`, `update_record`, `delete_record`) | Fast, governed, auditable |
| Schema changes | Dataverse MCP (`create_table`, `update_table`, `delete_table`) | Controlled through MCP tool allowlists |
| Bulk data operations | Dataverse SDK for Python | Deterministic, testable, batchable |
| Solution management | PAC CLI | PAC CLI is the standard for solution lifecycle |
| Complex queries | Dataverse MCP (`read_query`) or FetchXML via Web API | Depends on query complexity |
| File operations | Dataverse MCP (`init_file_upload`, `commit_file_upload`, `file_download`) | MCP handles the file transfer protocol |

The plugin's skill files encode this routing logic. When the agent reads a skill file for "data import," it learns to prefer the Python SDK for bulk operations. When it reads the "table management" skill, it learns to use MCP schema tools.

This design is smart, but it means the plugin's behavior depends on the quality of the skill files. If a skill file is missing or outdated, the agent may route to a suboptimal interface. Microsoft's GitHub repo is actively maintained — as of July 2026, it had 49 commits and 160 stars — but you should test routing behavior with your specific prompts.

## Governance Checklist Before You Let Teams Use It

The plugin makes Dataverse operations easy. That's the feature and the risk. Before you let a team use it broadly, I'd check these items:

- **Environment separation.** The plugin should point to a development or sandbox environment first, not production. Configure this through the PAC CLI auth profile and the MCP server URL.
- **Role scoping.** The Dataverse role used by the plugin should be the minimum required for the team's tasks. A developer building tables needs a different role than an analyst querying records.
- **MCP tool allowlists.** The Dataverse MCP server supports tool-level allowlists. Restrict destructive tools (`delete_record`, `delete_table`, `delete_skill`) to specific roles or environments.
- **Approval for destructive actions.** The plugin does not have built-in approval gates. You need to layer those on through Power Platform managed environments or custom review workflows.
- **Audit logging.** Enable Dataverse auditing before the plugin goes live. Every MCP tool call is logged, but you need auditing configured to capture the detail.
- **Cost tracking.** External MCP tool calls consume Copilot Credits. Set up monitoring before the first production prompt.
- **Prompt review process.** Treat agent prompts like code changes. A bad prompt can delete records, change security, or expose data. Have a review process, at least for admin-level prompts.

I covered the broader governance architecture in the [Dataverse agent data platform article](/posts/dataverse-agent-data-platform-2026/), but the plugin-specific takeaway is: the plugin inherits your existing governance gaps. If your Dataverse environment has over-broad roles or no audit logging, the plugin will make those problems more visible, not create new ones.

## Cost, Licensing, and Copilot Credit Considerations

External AI-agent access to Dataverse MCP tools is charged in Copilot Credits starting December 15, 2025. The billing has two tiers:

- **Premium rate:** `search_data` — the broad data discovery tool
- **Basic rate:** All other MCP tools including `search` (metadata), `describe`, `read_query`, record actions, and table actions

This changes how you design agent prompts. Repeated `search_data` calls for every turn of a conversation can add up quickly. I've started adding explicit instructions in my system prompts: "Use `search_data` only when you need broad data discovery. Prefer `read_query` for known query shapes and `describe` for metadata lookups."

The plugin itself is free and open source (MIT license). The cost is in the MCP tool calls the plugin routes to. If you're using Dynamics 365 Premium or Microsoft 365 Copilot licenses, some Dataverse data access is covered, but the details depend on your specific licensing agreement.

## Common Errors and Fixes

I've collected the most common errors from testing and community reports:

| Error | Likely Cause | Fix |
| --- | --- | --- |
| "MCP client not allowed" | The MCP server is not enabled for the environment, or the client isn't in the allowlist | Check Power Platform admin center > environment settings > MCP server configuration |
| "No active auth profile" | PAC CLI is not authenticated | Run `pac auth create --url https://{org}.crm.dynamics.com` |
| "Tool not found" | The agent is trying to use a tool name from an older version of the MCP surface | Update the plugin to the latest version; old tool names like `list_tables` and `fetch` were removed in 2026 |
| "Schema or logical name issue" | The agent is using a display name instead of the logical name | Use the logical name (e.g., `account` not `Account`) in prompts, or let the agent discover it via `describe` |
| "Timeout on data import" | The MCP tool call timed out for a large operation | Break the import into smaller batches or use the Python SDK path |
| "Permission denied" | The authenticated user doesn't have the required Dataverse role | Check the user's role assignment and security role privileges |
| "Copilot Credit limit exceeded" | Too many MCP tool calls, especially `search_data` | Review the agent's tool usage pattern and add caching or query optimization |

## Example Prompts for Developers, Analysts, and Admins

**Developer prompts:**

- "Create a solution called 'Vendor Management' with publisher prefix 'vmg'. Add the Vendor Compliance table to the solution."
- "Generate a Power Fx formula that calculates the compliance score as a weighted average of audit score (60%) and self-assessment score (40%)."
- "Export the Vendor Management solution as a managed solution and save it to ./solutions/."

**Analyst prompts:**

- "Show me the monthly trend of compliance scores for the last 6 months. Group by compliance status."
- "Find all accounts where the primary contact's email domain is not the same as the account's domain."
- "Create a chart showing the distribution of compliance scores by business unit."

**Admin prompts:**

- "List all security roles in the environment. Show me which ones have delete privileges on the account table."
- "Enable auditing on the opportunity table. Configure it to log update operations on the estimated value and close date columns."
- "Create a business unit called 'Compliance Team' under the root business unit. Assign the Compliance Readers security role to it."

## Final Verdict: Where Agent-Driven Dataverse Development Fits

The Dataverse plugin for coding agents is genuinely useful for the right workflows. Schema iteration, ad-hoc queries, data imports, and security configuration all benefit from the reduced context-switching. I've found it most valuable in the early stages of a project when you're exploring the data model and testing relationships.

The caveats are real. The plugin does not add governance — it inherits yours. The MCP tool surface changed significantly in 2026 and may change again. The billing model for external agents means you need cost monitoring from day one. And the plugin's routing logic depends on skill files that are still evolving.

My recommendation: install it in a development environment, run the discovery and query prompts, validate the results, and build your governance checklist before expanding to production. The plugin is ready for developer productivity in 2026. Whether it's ready for your production compliance workflow depends on how well you've configured the environment it connects to.
