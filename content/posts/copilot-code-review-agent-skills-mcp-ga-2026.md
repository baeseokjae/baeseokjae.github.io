---
title: "GitHub Copilot Code Review with MCP and Agent Skills Now GA"
date: 2026-08-04T16:02:30+00:00
tags:
  - GitHub Copilot
  - MCP
  - Agent Skills
  - Code Review
  - AI Development Tools
  - GitHub
description: "GitHub Copilot code review now supports agent skills and MCP servers in GA, bringing team standards and third-party context into every pull request review."
draft: false
cover:
  image: "/images/copilot-code-review-agent-skills-mcp-ga-2026.png"
  alt: "GitHub Copilot Code Review with MCP and Agent Skills Now GA"
  relative: false
schema: "schema-copilot-code-review-agent-skills-mcp-ga-2026"
---

GitHub Copilot code review has reached a major milestone with the general availability of agent skills and MCP (Model Context Protocol) server support, announced on July 29, 2026. These features transform Copilot code review from a static analysis tool into an extensible platform that understands your team's coding standards, integrates with your existing toolchain, and delivers context-aware feedback on every pull request.

## What's New — Agent Skills and MCP Go GA

On July 29, 2026, GitHub announced that agent skills and MCP server support for Copilot code review are now generally available for all Copilot Pro, Pro+, Business, and Enterprise users. This marks the culmination of a public preview that began on June 2, 2026, and represents GitHub's most significant investment in code review intelligence to date.

The GA release brings three core capabilities to every Copilot-powered code review:

- **Agent skills** allow teams to define custom instructions, scripts, and resources that Copilot loads during code review. These skills live in `.github/skills` directories as `SKILL.md` files and can encode anything from coding style conventions to security checklists.
- **MCP server connections** pull live context from third-party platforms — issue trackers, documentation systems, service catalogs, and monitoring dashboards — directly into the review process.
- **Attribution labels** on skill and MCP-generated comments, so developers can see exactly which skill or MCP server produced each piece of feedback.

All MCP tool calls during code review are restricted to read-only operations, a deliberate security boundary that GitHub has maintained since the preview phase. The GitHub and Playwright MCP servers are enabled by default, giving teams immediate value without additional configuration.

## Agent Skills Deep Dive — Bringing Team Standards into Every Review

Agent skills are the most transformative part of this release. Instead of Copilot code review applying generic best practices, teams can now encode their specific standards, conventions, and workflows into reusable skill definitions that Copilot loads automatically when reviewing relevant code.

### How Agent Skills Work

An agent skill is a folder containing a `SKILL.md` file and optional scripts and resources. The Agent Skills specification is an open standard used by multiple AI coding systems, including Copilot, Claude Code, and others. Skills can be defined at two levels:

- **Project skills** stored in `.github/skills/` (or `.claude/skills/`, `.agents/skills/`) — these apply to everyone working on the repository.
- **Personal skills** stored in `~/.copilot/skills/` (or `~/.agents/skills/`) — these apply only to the individual developer.

When Copilot code review processes a pull request, it scans the relevant skill directories and loads any skills whose triggers match the code being reviewed. The skill's instructions become part of the review prompt, guiding Copilot to check for team-specific patterns, flag anti-patterns, and enforce conventions that generic AI models would not know about.

### Real-World Use Cases for Agent Skills

| Use Case | Example Skill | Impact |
|----------|--------------|--------|
| Coding standards | Enforce team-specific naming conventions, import ordering, or file structure | Consistent codebase without manual linting config |
| Security policies | Check for hardcoded credentials, missing input validation, or unsafe API usage | Catch security issues before they reach production |
| Architecture rules | Verify that new code follows layered architecture, dependency injection patterns, or repository conventions | Maintain architectural integrity as the codebase grows |
| Testing requirements | Ensure every new function has corresponding unit tests, or that test coverage meets thresholds | Enforce quality gates at review time |
| Documentation checks | Flag missing JSDoc comments, incomplete README updates, or missing API documentation | Keep documentation in sync with code changes |

### The Skill Ecosystem

The `gh skill` CLI command, available through the GitHub CLI, lets developers discover and install skills from GitHub repositories. Community collections have already emerged, including `anthropics/skills` and `github/awesome-copilot`, providing a growing library of pre-built skills that teams can adopt or customize.

Ecosystem tools are also maturing around skills management. Tools like APM (Agent Package Manager), AGENTS.lock for dependency locking, and skills-sync for keeping skills up to date across teams signal that agent skills are evolving into a full package management category for AI coding tools.

## MCP Server Connections — Pulling Context from Third-Party Tools

MCP server support is the second pillar of this release. While agent skills bring team-specific knowledge into reviews, MCP servers bring live, external context from the tools your team already uses.

### What MCP Brings to Code Review

When Copilot code review encounters a change that references an issue, a service endpoint, or a documented pattern, it can query the relevant MCP server for additional context. For example:

- An **issue tracker MCP** can pull the full description, comments, and acceptance criteria for a referenced issue, allowing the review to verify that the implementation matches the requirements.
- A **documentation MCP** can fetch the latest API documentation or coding guidelines, ensuring the review checks against the most current standards.
- A **service catalog MCP** can validate that new service endpoints, configuration changes, or dependency updates follow the organization's operational guidelines.

### Default MCP Servers

GitHub ships with two MCP servers enabled by default:

1. **GitHub MCP** — provides context about issues, pull requests, repositories, and code owners directly from the GitHub ecosystem.
2. **Playwright MCP** — enables Copilot to verify UI changes by understanding browser automation and testing patterns.

### Configuration and Management

MCP servers are configured at the repository level under **Settings → Copilot → MCP servers**. Authentication tokens are stored separately under **Settings → Secrets and variables → Agents**, keeping credentials secure and out of configuration files. Any existing MCP configurations that teams have set up for the Copilot cloud agent automatically apply to code review, eliminating duplicate setup work.

## Security and Governance — Read-Only MCP and Enterprise Controls

GitHub made a deliberate architectural decision with this release: all MCP tool calls during code review are limited to read-only operations. This means MCP servers can provide context and data to the review, but they cannot create, update, or delete resources.

### Why Read-Only Matters

The read-only constraint is critical for enterprise adoption. Code review is a sensitive gate in the development pipeline — it is the last line of defense before code reaches production. Allowing MCP servers to write data during review would introduce unacceptable risks:

- An MCP server could accidentally create issues, modify documentation, or trigger workflows based on incomplete review context.
- A compromised MCP server could use write access to exfiltrate data or tamper with external systems.
- Audit trails become significantly harder to maintain when review-time actions can modify external systems.

By enforcing read-only access, GitHub ensures that MCP servers enhance the review without expanding the blast radius of any potential compromise.

### Enterprise Governance Features

For Business and Enterprise customers, administrators can control review intensity at the repository level. The **Low** and **Medium** analysis tiers give admins granular control over how much compute and reasoning power is applied to each repository's pull requests. This is configured per repository, allowing teams to match review depth to code complexity.

## The Medium Analysis Tier — Matching Review Depth to Complexity

Alongside the agent skills and MCP GA, GitHub introduced the **Medium analysis tier** during the June 2026 public preview. This tier routes complex pull requests to higher-reasoning models for deeper analysis, while keeping the **Low tier** for straightforward changes that need fast, cost-efficient review.

### When to Use Each Tier

| Tier | Best For | Model Type | Cost Profile |
|------|----------|------------|--------------|
| Low | Simple bug fixes, dependency bumps, minor refactors | Fast, lightweight model | Minimal — ideal for high-volume repos |
| Medium | Architecture changes, security-sensitive code, complex business logic | Higher-reasoning model | Higher — invest where it matters |

The tier system lets teams optimize the cost-quality tradeoff. A repository of utility scripts might stay on Low tier for all reviews, while a repository handling payment processing or user authentication might default to Medium. Administrators set the tier per repository, and the setting is shared across Copilot code review and the cloud agent for consistency.

## Getting Started — Configuration and Best Practices

Getting started with agent skills and MCP for Copilot code review requires minimal setup. Here is a practical guide for teams ready to adopt these features.

### Step 1: Create Your First Agent Skill

Create a `.github/skills/` directory in your repository and add a `SKILL.md` file:

```markdown
# Code Style Skill

Review pull requests for adherence to the team's coding conventions.

## Instructions

1. Check that all new functions include TypeScript type annotations.
2. Verify that imports are organized: external libraries first, then internal modules, then styles.
3. Ensure error messages use the team's standard format: `[ComponentName] Description of the issue.`
4. Flag any console.log statements that should be removed before merge.
```

### Step 2: Configure an MCP Server

Navigate to your repository's **Settings → Copilot → MCP servers** and add a new server configuration. For example, to connect to a documentation MCP:

```json
{
  "mcpServers": {
    "docs": {
      "type": "url",
      "url": "https://mcp.internal.example.com/docs"
    }
  }
}
```

Store any required authentication tokens under **Settings → Secrets and variables → Agents**.

### Step 3: Set the Analysis Tier

In the same repository settings, choose between Low and Medium analysis tiers. Start with Medium for repositories where code quality is critical, and use Low for high-volume, low-risk repositories.

### Best Practices

- **Start small** — Create one or two skills that address your team's most common review feedback. Expand as the team gains confidence.
- **Use attribution** — The new attribution labels on skill and MCP comments help developers understand where feedback comes from. Encourage your team to read these labels to build trust in the system.
- **Iterate on skills** — Skills are not static. Review and update them as your team's conventions evolve. The `gh skill` CLI makes it easy to distribute updates.
- **Leverage shared configuration** — Since MCP configs for the cloud agent automatically apply to code review, set them up once and benefit everywhere.
- **Monitor and adjust tiers** — Review the quality of feedback on Low vs. Medium tier reviews periodically. Adjust per-repository settings based on observed outcomes.

## The Bigger Picture — GitHub's Platform Play and the Agent Skills Ecosystem

The GA of agent skills and MCP in Copilot code review is more than a feature release — it is a strategic move that positions GitHub at the center of the AI-assisted development ecosystem.

### Open Standards Leadership

The Agent Skills specification is an open standard, not a proprietary GitHub format. By making the specification available to other AI coding tools, GitHub is betting that interoperability will drive adoption faster than lock-in. Claude Code already supports the same skill format, and other tools are expected to follow. This creates a virtuous cycle: more tools supporting the standard means more skills being created, which makes the standard more valuable for everyone.

### The Emerging Skills Ecosystem

The community response has been rapid. Within weeks of the public preview, ecosystem tools began appearing:

- **APM (Agent Package Manager)** — A package manager for agent skills, similar to npm or pip, enabling versioned skill distribution.
- **AGENTS.lock** — A lock file format for pinning skill versions across a team, ensuring consistent review behavior.
- **Mother MCP** — A proxy server that aggregates multiple MCP endpoints behind a single interface, simplifying configuration.
- **skills-sync** — A tool for keeping personal and project skills synchronized across developer machines.

This ecosystem growth mirrors the early days of package management in the JavaScript and Python ecosystems, suggesting that agent skills are following a well-understood adoption curve.

### Competitive Positioning

GitHub's move also positions Copilot code review against a growing field of AI code review tools. By offering an extensible platform rather than a fixed set of review rules, GitHub differentiates on flexibility. Teams are not limited to whatever review patterns GitHub ships — they can encode any standard, integrate any tool, and build any workflow they need.

## Conclusion — What This Means for Development Teams

The GA of agent skills and MCP support marks a fundamental shift in what AI-powered code review can deliver. Copilot code review is no longer a static analysis tool that applies generic best practices — it is now a platform that understands your team's specific standards, integrates with your existing toolchain, and adapts to your workflow.

For development teams, the implications are clear:

- **Consistency improves** — Agent skills ensure that every review, regardless of who performs it, checks against the same team standards.
- **Context matters** — MCP connections bring live data from issue trackers, documentation, and service catalogs into the review, reducing false positives and missed issues.
- **Security is built in** — Read-only MCP and per-repository tier controls give enterprises the governance they need without sacrificing capability.
- **The ecosystem is growing** — Open standards and community tools mean that the investment in agent skills today will compound over time as the ecosystem matures.

GitHub Copilot code review with agent skills and MCP is available now for all Copilot Pro, Pro+, Business, and Enterprise users. Teams that invest in building their skill library and configuring MCP connections today will be well-positioned as the AI coding tools ecosystem continues to evolve.

## Frequently Asked Questions

### What are agent skills in GitHub Copilot code review?

Agent skills are customizable instruction sets stored as `SKILL.md` files in your repository's `.github/skills/` directory. They let you define team-specific coding standards, security policies, and review rules that Copilot automatically applies when reviewing pull requests. The Agent Skills specification is an open standard used by multiple AI coding tools.

### How do MCP servers work with Copilot code review?

MCP servers provide live context from third-party tools during code review. When Copilot reviews a pull request, it can query MCP servers for information from issue trackers, documentation systems, service catalogs, and other platforms. All MCP tool calls are restricted to read-only operations for security.

### Is there any additional cost for using agent skills or MCP in code review?

Agent skills and MCP support are included with all Copilot Pro, Pro+, Business, and Enterprise subscriptions at no additional cost. The Medium analysis tier may use higher-reasoning models that consume more compute, but there is no separate billing line item — it is part of your existing Copilot subscription.

### Can I use the same MCP configuration for both Copilot cloud agent and code review?

Yes. Any MCP servers you configure for the Copilot cloud agent automatically apply to code review. This shared configuration eliminates duplicate setup and ensures consistent behavior across both surfaces. You can also configure code-review-specific MCP servers if needed.

### How do I get started with creating agent skills for my team?

Create a `.github/skills/` directory in your repository, add a `SKILL.md` file with your team's instructions, and commit it. Copilot code review will automatically load the skill when reviewing relevant pull requests. You can also use the `gh skill` CLI command to discover and install pre-built skills from community collections like `github/awesome-copilot`.
