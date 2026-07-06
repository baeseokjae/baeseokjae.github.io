---
title: "Agent Skills Marketplace Guide 2026: Claude, Codex, Cursor, and Gemini CLI"
date: 2026-07-06T12:00:00+00:00
tags: ["agent-skills", "claude-code", "codex", "cursor", "gemini-cli", "marketplace"]
description: "A practical 2026 guide to the agent skills marketplace landscape — comparing Claude Skills, Codex Skills, Cursor Marketplace, and Google's Skill Registry across install friction, governance, portability, and team adoption."
draft: false
cover:
  image: "/images/agent-skills-marketplace-guide-2026-claude-codex-cursor-and-gemini-cli.png"
  alt: "Agent Skills Marketplace Guide 2026"
  relative: false
---

If you've been using AI coding agents for more than a few months, you've hit the same wall I have: every new project needs the same setup — linting rules, test conventions, deployment scripts, API patterns — and you end up repeating yourself in prompts or pasting the same instructions into every new session. Agent skills are the fix, and in 2026 every major platform has shipped their own version. But they're not all the same, and picking the wrong one for your team costs real time.

I spent the last month running all four — Claude Skills, Codex Skills, Cursor Marketplace, and Google's Skill Registry — through real project workflows. Here's what actually works, where each falls short, and how to choose.

## What Counts as a Skill in 2026?

The core idea is consistent across platforms: a skill is a packaged bundle of instructions, scripts, and reference files that an AI agent loads dynamically when it needs to do a specific task. Think of it as a function call for your agent's behavior — you define the "how" once, and the agent picks it up when the context matches.

The format that's converging fastest is the **SKILL.md** file with YAML frontmatter — name, description, dependencies — plus optional supporting files for scripts, templates, and references. Anthropic published this as an open standard in December 2025, and both OpenAI and Google have adopted compatible formats. Cursor is the outlier, wrapping skills into a broader plugin system that also includes MCP servers, rules, hooks, and commands.

The practical difference matters: a pure SKILL.md skill is portable across Claude Code, Codex, and Gemini CLI. A Cursor plugin only works inside Cursor's editor and CLI. That portability gap is the single biggest decision factor for teams that aren't locked into one tool.

## Claude and Anthropic: The Open Standard

Anthropic's [Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills) launch was the moment the category crystallized. They didn't just ship a feature — they published a spec and said "this works across Claude.ai, Claude Code, the Claude Agent SDK, and the Developer Platform."

The architecture uses progressive disclosure: when Claude starts a session, it loads only each skill's name and description. It reads the full SKILL.md only when it decides the skill is relevant to the current task. This keeps context windows lean — I've seen sessions with 15+ installed skills where Claude only pulled in 2-3 for a given task.

What I've found most useful in practice is the executable code support. Skills can include Python or shell scripts that run deterministically — no token generation, no hallucination risk. For tasks like "parse this log file and extract error rates" or "validate this JSON against a schema," a script inside a skill is faster and more reliable than asking the LLM to do it inline.

The downside: Anthropic doesn't run a public marketplace. Skills are distributed through GitHub repos, internal wikis, or the [VoltAgent awesome-agent-skills]({{< ref "/posts/voltagent-awesome-agent-skills-guide-2026" >}}) community directory. Discovery is community-driven, which means quality varies and there's no curation.

## Codex and OpenAI: Task-Specific Reliability

OpenAI's [Codex Skills]({{< ref "/posts/openai-codex-skills-guide-2026" >}}) follow the same SKILL.md format but with a stronger emphasis on workflow reuse over code generation. The docs are explicit: skills exist to make Codex more reliable for repeatable workflows, not just to generate code faster.

The skill structure is a directory with SKILL.md plus optional subdirectories for scripts, references, assets, and agent metadata. Codex uses the same progressive disclosure pattern — name and description first, full content on match. Skills can be invoked explicitly by name or selected implicitly when the task description matches.

OpenAI ships a curated skill installer that handles installation and updates. There's also repository-scoped skills for teams — you define skills at the repo level and every team member's Codex picks them up automatically. This is the feature that makes Codex Skills practical for teams that don't want to manage skill distribution themselves.

The limitation I hit: Codex Skills are tied to Codex. You can't take a skill written for Codex and run it in Claude Code or Gemini CLI without reformatting, even though the SKILL.md format is compatible. OpenAI hasn't published a cross-platform distribution story.

## Cursor: Marketplace-First Distribution

Cursor took a different bet. Instead of shipping a skill format and letting the community figure out distribution, they built a [Marketplace](https://cursor.com/blog/marketplace) that bundles plugins, skills, rules, hooks, commands, and MCP servers into one discovery surface.

The marketplace is curated — Cursor vets partners and plugins before listing them. The launch post emphasized coverage across the full product development lifecycle: design, development, testing, deployment. In practice, this means you can install a plugin that adds a testing framework, a set of rules for your team's coding conventions, and an MCP server for your deployment target, all from one interface.

Cursor's newer releases (2.4 and later) add team and workspace customization on top of the marketplace. You can publish private plugins for your organization, control which plugins are available to which teams, and manage updates centrally. For an engineering org of 20+ people, this governance layer is the killer feature — you don't want every developer independently installing skills from GitHub.

The trade-off: Cursor's plugin format is not portable. A Cursor plugin that wraps an MCP server and a set of rules won't work in Claude Code or Codex. If your team switches editors, you rebuild your skill library from scratch. Cursor is betting that switching costs keep you in their ecosystem.

## Google and Gemini CLI: Enterprise Registry

Google's approach is the most enterprise-oriented of the four. The [official skills repository](https://cloud.google.com/blog/topics/developers-practitioners/level-up-your-agents-announcing-googles-official-skills-repository) is installable via `npx skills install github.com/google/skills` and explicitly supports Antigravity, Gemini CLI, and third-party agents. Google is the only vendor that's committed to cross-tool portability from day one.

The Skill Registry is described as secure, private, and low-latency — it's designed for regulated teams that need to control who publishes and installs skills. If you're in finance, healthcare, or defense, this matters more than any feature comparison. Google also ships extension settings with structured configuration, secure secret storage, and workspace-scoped settings, which means you can distribute a skill that requires API keys without hardcoding them.

One wrinkle: consumer Gemini CLI access is transitioning to Antigravity CLI, with consumer requests stopping on June 18, 2026. If you're evaluating Gemini CLI for personal use, the timeline matters. For enterprise teams on Google Cloud, the transition is transparent — the Skill Registry and extension system carry over.

## Comparison: Which One for Your Situation?

| Dimension | Claude Skills | Codex Skills | Cursor Marketplace | Google Skill Registry |
|---|---|---|---|---|
| **Install** | Git clone or community repo | Curated installer or repo-scoped | One-click from marketplace UI | `npx skills install` |
| **Format** | SKILL.md (open) | SKILL.md (open) | Plugin bundle (proprietary) | SKILL.md (open) |
| **Portability** | Cross-platform (spec) | Codex only | Cursor only | Cross-platform (Antigravity, Gemini, 3rd-party) |
| **Governance** | None built-in | Repo-scoped teams | Team/workspace management | Private registry, secret store, scoped settings |
| **Discovery** | Community (GitHub, VoltAgent) | Curated installer | Curated marketplace | Official repository |
| **Best for** | Individual devs, open-source projects | Teams already on Codex | Engineering orgs locked into Cursor | Regulated enterprises on Google Cloud |

## Security and Trust

The security angle deserves its own callout. A skill is executable code running in your agent's context — it can read files, make API calls, and modify your workspace. I covered the threat model in detail in the [Agent Skills Supply Chain Security Guide]({{< ref "/posts/agent-skills-supply-chain-security-guide-2026" >}}), but the short version is: curated marketplaces (Cursor, Google's registry) reduce the risk of malicious skills but introduce a single point of control. Open registries (VoltAgent, GitHub) give you more choice but require you to audit every skill you install.

For teams that need both choice and safety, Google's private Skill Registry is the most mature option. For individual developers, Claude's open format plus community vetting through VoltAgent is practical — just don't install skills without reading the SKILL.md and scripts first.

## Where the Market Is Heading

Three trends are clear from the 2026 landscape:

**Portability is winning.** Anthropic's open SKILL.md format has become the de facto standard. OpenAI and Google both support it. Cursor is the holdout, and I expect pressure from enterprise buyers to change that — no one wants to rebuild their skill library when they switch tools.

**Governance is the differentiator.** Every platform can distribute skills. The ones that win enterprise adoption will be the ones that let teams control who publishes, who installs, and what skills can do. Google's Skill Registry and Cursor's team management are the early leaders here.

**Marketplaces are becoming platforms.** Cursor's bet — bundle skills, plugins, MCP servers, and team settings into one surface — is the direction everyone is moving. The question is whether the market wants one integrated platform or a composable stack of portable skills. I'm betting on composable, but Cursor's numbers suggest a lot of developers prefer the integrated experience.

If you're starting fresh in 2026, write your skills in the open SKILL.md format. They'll work in Claude Code, Codex, and Gemini CLI today, and they'll work in whatever comes next. Lock-in is the enemy of good tooling, and the skill format is the one place you can avoid it.

## FAQ

### Can I use the same skill file across Claude Code, Codex, and Cursor?

Yes and no. A skill written in the open SKILL.md format works in Claude Code, Codex CLI, and Gemini CLI without modification. Cursor supports Agent Skills in both the editor and CLI, but its Marketplace plugins use a proprietary format that doesn't transfer. If cross-platform portability matters, stick to the SKILL.md format and skip Cursor-specific plugin features.

### How many tokens does a skill add to my agent's context?

Progressive disclosure keeps it minimal — roughly 50-100 tokens per skill for the name and description. The full SKILL.md content loads only when the agent decides the skill is relevant to the current task. I've run sessions with 15+ installed skills and seen only 2-3 pulled in for any given task.

### Is Skills.sh free to use?

Yes. Skills.sh by Vercel is free — `npx skills add <owner/repo>` installs a skill from any public GitHub repo. There's no paid tier as of mid-2026. The platform tracks install counts (895K+ total across all time) and shows trending skills on a leaderboard, but there's no cost to publish or install.

### How do I audit a skill before installing it?

Read the SKILL.md and any scripts in the skill directory before running it. A skill can include executable Python or shell scripts that run in your agent's context — it can read files, make API calls, and modify your workspace. For skills from community sources like VoltAgent or GitHub, I always check the scripts directory first. Curated marketplaces like Cursor's and Google's Skill Registry reduce this risk through vetting, but they introduce a single point of control.

### What happens to Gemini CLI skills after the Antigravity transition?

Google has stated that the Skill Registry and extension system carry over to Antigravity CLI. Skills installed via `npx skills install` continue to work. The transition affects consumer Gemini CLI access (requests stop June 18, 2026), but enterprise teams on Google Cloud see no disruption. If you're on Gemini CLI today, your skills will work on Antigravity CLI without changes.
