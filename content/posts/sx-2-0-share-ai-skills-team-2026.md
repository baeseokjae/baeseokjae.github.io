---
title: "Sx 2.0 Review: Share AI Skills with Your Team Through a Dropbox Folder"
date: 2026-07-20T07:01:36+00:00
tags:
  - sx
  - AI skills
  - team collaboration
  - AI tools
  - open source
description: "Sx 2.0 lets you share AI skills across your team using a shared Dropbox folder — no server, no git, no accounts required. Here's our full review."
draft: false
cover:
  image: "/images/sx-2-0-share-ai-skills-team-2026.png"
  alt: "Sx 2.0 Review: Share AI Skills with Your Team Through a Dropbox Folder"
  relative: false
schema: "schema-sx-2-0-share-ai-skills-team-2026"
---

Sx 2.0 is an open-source tool that turns a shared Dropbox folder into a complete AI skill distribution system for your team. Instead of emailing `.claude.md` files or maintaining a git repository of AI instructions, you drop a skill into a synced folder and every team member's AI clients — Claude Code, Cursor, Copilot, Codex, Gemini, Cline, and Kiro — pick it up automatically. It is built by Sleuth (Dylan Etkin, former Atlassian) and is available under the Apache-2.0 license.

## What Is Sx 2.0? — The 30-Second Version

Sx (pronounced "ess-ex") is a package manager for AI assets. Version 2.0, released in July 2026, introduces a desktop application alongside the existing CLI, a vault format v2 that stores skills as plain markdown on disk, an extension marketplace with 15 built-in extensions, and a shared-folder backend that uses Dropbox, Google Drive, or any synced directory as the distribution channel. The core idea is simple: write a skill once, put it in a shared folder, and every AI tool on your team can use it without manual copying or configuration.

## The Problem: AI Skills Are Trapped on Individual Machines

AI coding assistants have become indispensable for developers, but the skills, rules, and instructions that make them effective are surprisingly hard to share. A typical scenario: a senior engineer spends two hours crafting a meticulous `.claude.md` file with project conventions, testing patterns, and deployment checklists. They email it to the team. Three weeks later, half the team has an outdated version, two people never received it, and one person edited their local copy without telling anyone.

This is the AI skill distribution problem. According to a 2025 survey by Stack Overflow, 67% of developers using AI coding tools reported that inconsistent AI instructions across team members led to conflicting code patterns and wasted time. The problem gets worse as teams grow — each new member needs to be onboarded to the team's AI conventions manually, and there is no audit trail for who changed what or when.

Existing solutions fall short. Git repositories require every team member to be comfortable with the command line and pull requests. Obsidian vaults in shared folders store markdown but have no translation layer for AI clients. Email and Slack attachments are versioning nightmares. Sx 2.0 addresses this gap with a purpose-built tool that treats AI skills as first-class distributable assets.

## The Big Idea: A Shared Dropbox Folder Is Your Entire Backend

The most striking design decision in Sx 2.0 is that it requires zero server infrastructure. You do not need to host a registry, set up a database, or create user accounts. Instead, you point Sx at a shared folder — Dropbox, Google Drive, OneDrive, or any directory synced by a cloud storage service — and that folder becomes your team's skill registry.

Here is how it works in practice:

1. **Create a shared folder** on Dropbox (or any synced drive) and invite your team.
2. **Install Sx 2.0** on each team member's machine (desktop app or CLI).
3. **Point Sx at the shared folder** with `sx vault init --path /path/to/shared/folder`.
4. **Write or install skills** — they appear in the shared folder as plain markdown files.
5. **Every team member's AI clients** automatically discover and use the skills.

This approach is brilliant in its simplicity. It leverages the fact that most teams already use Dropbox or Google Drive for file sharing. There is no new infrastructure to learn, no new accounts to create, and no single point of failure. If the cloud storage service goes down, skills are still available from the local cache. The shared folder becomes a living, versioned repository of your team's collective AI knowledge.

Dylan Etkin, the creator of Sx, explained on Hacker News that this design was intentional: "The goal was to make AI skill sharing as easy as dropping a file into a folder. Technical teams can use git. The rest of the world uses folders."

## Vault Format v2 — Plain Markdown, No Lock-In

Sx 2.0 introduces vault format v2, which stores every skill as a plain markdown file on disk. This is a deliberate departure from the binary or proprietary formats used by many AI tool registries. The benefits are significant:

- **Human-readable**: You can open any skill in any text editor.
- **Git-friendly**: The markdown files diff cleanly in version control.
- **Portable**: If you stop using Sx tomorrow, your skills are still just markdown files.
- **Searchable**: Standard desktop search tools index the files without special plugins.

Each skill file includes frontmatter with metadata — name, version, description, supported AI clients, permissions, and dependencies. The body of the file contains the actual skill instructions in plain markdown. This means a skill authored for Claude Code can be read by a human, edited in VS Code, and shared via email — all without Sx being involved.

The vault itself is a directory with a `.sx` subdirectory containing a lock file and configuration. The lock file is per-user, resolved against git identity, which means each team member can have different installed versions of the same skill without conflicts. This is a smart design borrowed from npm and other package managers that prevents the "works on my machine" problem.

## The Translation Layer — One Skill, Every AI Client

One of the most impressive features of Sx 2.0 is its translation layer. Different AI coding tools expect different formats for their instructions. Claude Code uses `.claude.md` files. Cursor uses `.cursorrules`. GitHub Copilot uses `.github/copilot-instructions.md`. Codex uses `AGENTS.md`. Without Sx, maintaining skills for multiple AI clients means writing the same instructions in multiple formats and keeping them in sync.

Sx 2.0 solves this by letting you write a skill once in its vault format and then translating it to the format expected by each AI client. When you install a skill with `sx install`, Sx automatically generates the appropriate files for every AI client configured on your machine. If your team uses Claude Code and Cursor, one skill installation produces both `.claude.md` and `.cursorrules` files.

The translation is not a simple copy-paste. Sx applies format-specific transformations, handling differences in how each client interprets frontmatter, sections, and directives. This means a skill can include instructions that only apply to certain clients, using conditional sections in the vault format.

As of July 2026, Sx 2.0 supports seven AI clients: Claude Code, Cursor, GitHub Copilot, Codex (by OpenAI), Gemini Code Assist, Cline, and Kiro. The extension system allows the community to add support for additional clients without waiting for the core team.

## Extensions — Because Your Team's Problems Aren't Their Roadmap

Sx 2.0 ships with an extension marketplace that includes 15 built-in extensions. Extensions are plugins that add functionality to Sx itself — they can define new commands, integrate with external services, or add validation rules for skills.

The extension system is permission-gated, which sets a new standard for AI tool plugin safety. Each extension declares the permissions it needs (read files, write files, network access, execute commands), and the user must approve these permissions before the extension runs. This is similar to the permission model used by mobile operating systems and is a welcome addition to the AI tooling ecosystem, where plugin security has been an afterthought.

Some of the notable built-in extensions include:

- **Git integration**: Automatically commit and push skill changes when the vault is updated.
- **Slack webhook**: Post a message to a Slack channel when a new skill version is published.
- **Lint**: Validate skill files for common errors and formatting issues.
- **Template**: Generate skill scaffolds from templates.
- **Stats**: Track which skills are installed and used across the team (anonymized).

The extension marketplace is community-driven. Anyone can publish an extension, and the permission-gating model means users can evaluate and approve extensions with confidence. This creates an ecosystem where specialized needs — compliance checks, industry-specific templates, custom integrations — can be addressed without bloating the core tool.

## Collections — Skills That Install as a Unit

Collections are a new feature in Sx 2.0 that groups related skills into a single installable unit. This is useful for teams that want to distribute a set of skills together — for example, a "Python Development" collection that includes skills for pytest conventions, Django patterns, type hinting rules, and deployment checklists.

When a team member installs a collection, all the skills in that collection are installed at once, with their dependencies resolved automatically. Collections can also specify version constraints, ensuring that everyone on the team gets compatible versions of related skills.

This feature addresses a common pain point in larger teams: skill sprawl. Without collections, teams end up with dozens of individual skills that are hard to discover and manage. Collections provide a logical grouping that mirrors how teams actually think about their tooling — by domain, project, or workflow.

## Sx 2.0 vs. The Competition

To understand where Sx 2.0 fits in the AI skill sharing landscape, it helps to compare it directly with the alternatives.

| Feature | Sx 2.0 | skillshare | Git Repo | Obsidian Vault |
|---|---|---|---|---|
| **GitHub Stars** | 282★ | 2,439★ | N/A | N/A |
| **Desktop App** | Yes (v2.0) | No (CLI only) | No | Yes |
| **Cloud Folder Backend** | Yes (Dropbox, Drive, etc.) | No | No | Yes (manual) |
| **AI Client Translation** | Yes (7 clients) | Yes (60+ tools) | No | No |
| **Extension System** | Yes (15 built-in) | No | No | Yes (community) |
| **Permission Gating** | Yes | No | N/A | No |
| **Version Management** | Lock file per user | Git-based | Git | No |
| **Non-Technical Users** | Yes (desktop app) | No (CLI only) | No | Yes |
| **License** | Apache-2.0 | MIT | N/A | Proprietary |
| **Created** | Dec 2025 | 2024 | N/A | 2020 |

**skillshare** (2,439★) is the most popular AI skill sync tool by GitHub stars. It is a Go-based CLI that syncs skills across 60+ AI CLI tools. Its main strength is breadth of tool support — it covers more AI clients than Sx. However, it is CLI-only, which means non-technical team members cannot use it. It also lacks a desktop app, extension system, and permission-gating model. skillshare requires git knowledge and terminal usage, which limits its adoption to engineering teams.

**Git repositories** are the default approach for many teams. They offer robust version control, code review workflows, and audit trails. But they require every team member to be comfortable with git, pull requests, and merge conflicts. For non-technical team members who contribute skills — product managers writing AI prompts, designers documenting design system rules — git is a barrier, not a solution.

**Obsidian vaults** in shared folders are popular because they are simple. Teams create a shared Obsidian vault on Dropbox and write markdown files with AI instructions. The problem is that Obsidian has no translation layer for AI clients. The markdown files sit in the folder but are not automatically picked up by Claude Code, Cursor, or Copilot. Team members must manually copy instructions into their AI tool configurations, which defeats the purpose of sharing.

Sx 2.0 differentiates by targeting the middle ground: teams that want the simplicity of a shared folder with the power of a package manager. It is less technical than git but more structured than a raw markdown folder.

## What the HN Community Thinks — The Good and The Skeptical

When Sx was posted on Hacker News as a Show HN, it received 44 points and 33 comments — a modest but engaged reception. The community response highlighted both the strengths and the concerns.

**The positive reactions** focused on the non-technical approach. Several commenters noted that their teams include product managers, designers, and other non-engineers who write AI prompts and instructions. For these teams, a shared folder is the only realistic distribution mechanism. One commenter wrote: "This is exactly what we need. Our PMs write great AI prompts but can't use git. A Dropbox folder is something they already understand."

**The skeptical reactions** centered on three concerns:

1. **Version management**: Without git's commit history, how do you track who changed what and when? Sx's lock file helps with dependency resolution but does not provide a full audit trail.

2. **Dropbox latency**: In teams with large skill libraries, Dropbox sync latency could cause temporary inconsistencies. If one team member updates a skill and another installs it before the sync completes, they get a stale version.

3. **The "why not just use git" argument**: Some commenters argued that teaching non-technical team members basic git is a better long-term investment than building a tool that works around their lack of git knowledge.

Dylan Etkin responded to these concerns on HN, explaining that Sx is designed for teams where git is not an option — not as a replacement for git where git works well. He also noted that the desktop app in v2.0 includes a sync status indicator that shows whether the local vault is up to date with the shared folder.

## Who Is Sx 2.0 For? (And Who It Isn't)

Sx 2.0 is ideal for:

- **Mixed teams** with both technical and non-technical members who contribute AI skills.
- **Small to medium teams** (5-50 people) that already use Dropbox or Google Drive for collaboration.
- **Teams using multiple AI clients** and tired of maintaining skills in multiple formats.
- **Organizations** that want to experiment with AI skill sharing without committing to infrastructure.

Sx 2.0 is less suitable for:

- **Large enterprises** that need full audit trails, RBAC, and compliance reporting.
- **Teams already happy with git-based workflows** for skill management.
- **Solo developers** who do not need to share skills with anyone.
- **Teams that do not use any of the seven supported AI clients.**

## Pricing and Licensing — Apache-2.0, Free, Open Source

Sx 2.0 is completely free and open source under the Apache-2.0 license. There is no paid tier, no enterprise license, and no feature gating. The source code is available on GitHub at github.com/sleuth-io/sx. The desktop app is distributed as a binary download for macOS, Windows, and Linux.

The Apache-2.0 license is permissive and business-friendly. It allows commercial use, modification, distribution, and sublicensing, with the condition that modified files carry prominent notices. This makes Sx suitable for use in corporate environments without legal concerns.

## Verdict — A Smart Pivot That Opens AI Skills to Everyone

Sx 2.0 represents a thoughtful evolution from a CLI-only tool to a platform that bridges the gap between technical and non-technical skill authors. The desktop app, shared-folder backend, extension marketplace, and permission-gating model address real pain points that existing tools like skillshare and git repositories do not solve.

The shared-folder-as-backend approach is the standout innovation. It is not technically sophisticated — and that is precisely the point. By meeting teams where they already are (in a Dropbox folder), Sx removes the adoption friction that has kept AI skill sharing confined to engineering teams.

The extension system with permission gating sets a new standard for plugin safety in the AI tooling ecosystem. As AI tools become more powerful and more integrated into development workflows, the ability to audit and approve what plugins can do will become increasingly important.

Sx 2.0 is not a replacement for git-based workflows in teams that already use them effectively. But for the vast majority of teams that do not — and for the growing number of non-technical contributors who write AI skills — Sx 2.0 is the most practical solution available today.

## Frequently Asked Questions

**Is Sx 2.0 free to use?**
Yes, Sx 2.0 is completely free and open source under the Apache-2.0 license. There is no paid tier, no enterprise license, and no feature gating. The desktop app and CLI are both free to download and use.

**Which AI clients does Sx 2.0 support?**
Sx 2.0 supports seven AI clients as of July 2026: Claude Code, Cursor, GitHub Copilot, Codex (by OpenAI), Gemini Code Assist, Cline, and Kiro. The extension system allows the community to add support for additional clients.

**Do I need a Dropbox account to use Sx 2.0?**
No, Sx 2.0 works with any synced folder. You can use Dropbox, Google Drive, OneDrive, or even a local network share. The shared folder is just a directory that all team members have access to.

**How does Sx 2.0 handle skill versioning?**
Sx 2.0 uses a per-user lock file resolved against git identity. Each team member can have different installed versions of the same skill without conflicts. The vault format v2 stores skills as plain markdown, which means they can also be versioned with git if desired.

**Can non-technical team members use Sx 2.0?**
Yes, the desktop app in Sx 2.0 is designed for non-technical users. It provides a graphical interface for browsing, installing, and managing skills without requiring terminal usage or git knowledge. The shared-folder backend also aligns with workflows that non-technical team members already use.
