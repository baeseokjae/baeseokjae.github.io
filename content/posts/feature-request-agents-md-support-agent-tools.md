---
title: "AGENTS.md Agent Tooling: Why Native AGENTS.md Support Is the Standard Your Tools Need"
date: 2026-09-16T04:01:30+00:00
tags:
  - AGENTS.md
  - AI coding agents
  - Claude Code
  - Codex CLI
  - Developer tools
  - LLM tooling
description: "AGENTS.md is now the standard instruction file for coding agents — supported natively by 23 tools and used in 60k+ repos. Here's what tool support means and why it matters."
draft: false
cover:
  image: "/images/feature-request-agents-md-support-agent-tools.png"
  alt: "AGENTS.md agent tooling guide — the portable instruction file for coding agents"
  relative: false
schema: "schema-feature-request-agents-md-support-agent-tools"
---

AGENTS.md has become the de-facto standard instruction file for AI coding agents, and the demand for native support across agent tools is now the strongest portability signal in the developer-tooling market. As of 2026, over 60,000 open-source projects on GitHub ship an AGENTS.md, 23 tools read it natively, and the largest unmet feature request in the entire Claude Code tracker is precisely "Support AGENTS.md" — with more than 5,000 reactions. This guide explains what AGENTS.md is, why it won the format war, which tools support it natively, the gaps that remain, and what you should demand when adding AGENTS.md support to your own agent tool.

## What Is AGENTS.md and Why Did It Win?

An AGENTS.md file is a simple Markdown document that lives in a repository and tells a coding agent how to work in that codebase — think of it as a "README for agents." Unlike a README for humans, AGENTS.md is written for an AI coding agent to read at runtime, and it typically contains setup commands, code style rules, testing instructions, build commands, and conventions the agent must follow.

The format deliberately has almost no rules. There are no required fields and no frontmatter. It relies on the LLM agent interpreting human-readable guidance directly. This simplicity is exactly why it won: a plain Markdown file is universally readable, version-controllable, and reviewable, with zero tool-specific syntax. The ThoughtWorks Technology Radar (April 2026) rates AGENTS.md a notable technique and calls it foundational to "context engineering" — not just a file convention.

The win is best understood through adoption. On the 2026-07-19 GitHub snapshot, there were 158,592 indexed file matches for AGENTS.md versus 56,888 for `.github/copilot-instructions.md`, 46,772 for CLAUDE.md, and just 8,392 for Cursor's `.mdc` rules. In the RuleStack corpus (13 September 2026), 617 of 1,021 indexed repositories — 60.4% — carry an AGENTS.md, with a median file size of 857 words. The format isn't just growing; it has overtaken every competitor by a wide margin.

## The Fragmentation AGENTS.md Solved

Before AGENTS.md coalesced into a standard, every coding agent expected its own instruction file. Claude Code wanted CLAUDE.md, Gemini CLI wanted GEMINI.md, Copilot wanted copilot-instructions.md, Cursor wanted `.cursorrules`, and several tools wanted their own bespoke variants. A single team maintaining a repository for multiple agents faced a genuine burden: keep three to five parallel files of duplicated guidance in sync, or suffer inconsistency.

AGENTS.md collapsed all of that into one file. It directly solves the root-cause problem of the feature request you may be weighing: portability. Instead of writing instructions five times, you write a single AGENTS.md that every compatible agent reads. That one-file portability is the core value proposition, and it is the reason the request for support appears so frequently across tool trackers — including 173 distinct issues mentioning AGENTS.md in the Claude Code tracker alone.

## How the Standard Became Neutral

One reason AGENTS.md support is now a governance decision rather than a purely technical one is that the format sits under neutral stewardship. AGENTS.md originated from an industry working group spanning Google, OpenAI, Sourcegraph, Factory, and Cursor. On 2025-12-09, OpenAI and Anthropic jointly donated it to the Linux Foundation's Agentic AI Foundation (AAIF). That move matters strategically: a format owned by one vendor has no chance of cross-vendor adoption, but a format governed by a neutral Linux Foundation body makes it safe for any tool — including competitors — to adopt.

This neutrality is what turns "support AGENTS.md" from a questionable ask into a safe, strategic one. Because no single company controls it, adopting AGENTS.md doesn't lock a tool into another vendor's roadmap. That is the key argument a product team can present when deciding to allocate engineering time to AGENTS.md support.

## Adoption Numbers That Matter

The statistics that justify an AGENTS.md feature request are concrete rather than anecdotal:

- **60,000+ GitHub projects** carry an AGENTS.md file, per the official agents.md homepage.
- The **2026-07-19 GitHub snapshot** recorded **158,592 indexed file matches** for AGENTS.md — roughly **2.8× the next format** (copilot-instructions.md at 56,888) and nearly **19× Cursor's `.mdc` rules** (8,392).
- The **RuleStack corpus (13 Sep 2026)** shows **617 of 1,021 repositories (60.4%)** with AGENTS.md and a median file of 857 words.
- **23 tools read AGENTS.md natively** as of 2026.
- The OpenAI **Codex monorepo** on GitHub carries **88 nested AGENTS.md files**, demonstrating deep monorepo usage.

These are not idle adoption figures — they represent real, heterogeneous repositories standardizing on one instruction format. Any agent tool that cannot read AGENTS.md today is actively out of step with the majority of the codebases its users bring to it.

## Who Reads AGENTS.md Today

The list of tools with native AGENTS.md support is broad and growing:

| Tool | Native AGENTS.md support | Notes |
|------|-------------------------|-------|
| OpenAI Codex CLI | Yes | Originator of the format |
| GitHub Copilot | Yes | Reads AGENTS.md natively |
| Cursor | Yes | |
| Windsurf | Yes | |
| Amp | Yes | |
| Aider | Yes | |
| Continue.dev | Yes | |
| Devin / Cognition | Yes | |
| Claude Code | No | Uses CLAUDE.md; support requested in issue #6235 |
| Gemini CLI | No | Uses GEMINI.md |

The table makes the gap obvious. The two highest-profile holdouts are Claude Code (which reads CLAUDE.md) and Gemini CLI (which reads GEMINI.md). Nearly every other major coding agent has already adopted AGENTS.md natively. This asymmetry is the entire reason feature-request issues for AGENTS.md support continue to accumulate.

## The Biggest Open Gap: Claude Code

The strongest quantified argument for AGENTS.md support is the demand registered on the Claude Code tracker. Issue #6235, titled "Support AGENTS.md," opened on 2025-08-21 and became the **largest unmet feature request in the entire tracker** — roughly **4× the next-biggest request**. At its peak it carried **5,200+ reactions and 300+ comments**, with 173 separate issues in the tracker mentioning AGENTS.md and a related issue adding another 220+ reactions.

What happened next turned the request into a governance decision. On **2026-08-17**, Anthropic closed issue #6235 as **"completed" after 361 days** — but without implementing native AGENTS.md reading. The closure pointed only to a workaround (the `@AGENTS.md` import pattern and symlink bridges) rather than a structural fix. Eight days later, on **2026-08-25**, Shopify CEO Tobias Lütke publicly threatened to ban Claude Code over the refusal. The issue was subsequently re-opened through a deliberate duplicate (#78977). The takeaway: native AGENTS.md support at Anthropic is no longer a technical question — it is a business decision made against the backdrop of the industry's single most-demanded feature.

## What to Put in an AGENTS.md

A well-formed AGENTS.md should give an agent everything it needs to work safely and correctly in the repository. Recommended sections:

- **Setup commands** — install steps, dependency bootstrapping, and environment configuration.
- **Build and run commands** — the exact commands to build, run, and test locally.
- **Code style and conventions** — linting rules, formatting, naming, and project-specific idioms.
- **Testing instructions** — how to run the test suite, what "green" looks like, and edge cases to respect.
- **Security considerations** — secret handling, sensitive paths, and operations the agent must never perform automatically.
- **Workflow contracts** — how to format commit messages, how to report progress, and any approval gates.

Because the file is plain Markdown with no required structure, teams adapt these sections freely. For monorepos, nested AGENTS.md files deliver the real upgrade over a single CLAUDE.md: each subdirectory can carry its own AGENTS.md, and the **closest-file-wins precedence** rule deterministically selects the nearest file as you descend the tree. The OpenAI Codex monorepo, with its 88 nested files, is the canonical demonstration of this pattern.

## Migration Bridges Until Native Support Lands

If your tool currently lacks native AGENTS.md support, teams still have two practical bridges today:

- **The symlink bridge** — `ln -s AGENTS.md CLAUDE.md` (or GEMINI.md) creates an alias so a non-supporting tool reads the same content. The file stays a single source of truth on disk.
- **The `@AGENTS.md` import pattern** — the documented default in some tools, which imports AGENTS.md content into the tool's own instruction context without requiring the file to be read natively.

Each bridge trades a little overhead for immediate portability. They are valuable stopgaps, but they are not the structural fix — they still require per-tool setup and drift risk when filenames change. Native support removes that overhead entirely.

## Checklist for Teams Requesting AGENTS.md Support

Whether you are filing a feature request or planning to implement AGENTS.md support in your own tool, use this checklist to make the case concrete:

1. **Dual-read compatibility** — read AGENTS.md natively while still honoring the tool's legacy file (CLAUDE.md, GEMINI.md) so existing users are not broken.
2. **Closest-file-wins precedence** — implement deterministic nested-file resolution so monorepos behave predictably.
3. **`AGENTS.md` discovery** — search the working tree from the repository root down, honoring the nearest file.
4. **Skills integration (`.agents/skills`)**: discover and load bundled skills from the repository alongside AGENTS.md.
5. **A validation template** — provide a starting AGENTS.md and schema hints so users can author correct files.
6. **Neutral-stewardship acknowledgment** — cite the Linux Foundation AAIF ownership to justify adoption as safe and strategic.

Quantified demand — the 5,000+ reactions on #6235, the 60.4% corpus share — is the strongest evidence to attach to the request.

## The Bottom Line

AGENTS.md is the de-facto standard for coding-agent instructions, and it won because it is simple, portable, and neutrally governed. The portability payoff — one file that works across every agent tool — is exactly what enterprises want, and the quantified demand makes that clear. Tools that already support it natively are aligned with the standard; the remaining holdouts are now making a governance decision, not a technical one. If you use a tool that still cannot read AGENTS.md, filing (or accelerating) a feature request for native support is the single highest-leverage action you can take — the standard has already won, and tooling has not fully caught up.

## FAQ

**What is an AGENTS.md file?**
An AGENTS.md is a Markdown file in a repository that gives an AI coding agent setup commands, code style rules, testing instructions, and conventions — effectively a "README for agents." It has no required fields or frontmatter and relies on the agent interpreting human-readable guidance.

**Which agent tools support AGENTS.md natively?**
OpenAI Codex CLI, GitHub Copilot, Cursor, Windsurf, Amp, Aider, Continue.dev, and Devin/Cognition read AGENTS.md natively. Claude Code and Gemini CLI are the notable holdouts, relying on CLAUDE.md and GEMINI.md instead.

**What is the difference between AGENTS.md and CLAUDE.md?**
AGENTS.md is the vendor-neutral standard supported by 23 tools, while CLAUDE.md is Claude Code's own legacy instruction file. On any repository, having both means maintaining duplicated guidance; AGENTS.md eliminates that duplication by serving as a single portable source.

**Does Claude Code read AGENTS.md?**
No. Claude Code reads CLAUDE.md, not AGENTS.md, as of 2026. Native AGENTS.md support was requested in issue #6235 — the largest unmet feature request in the tracker — and was closed as "completed" on 2026-08-17 without a native read, pointing instead to workarounds like the `@AGENTS.md` import and symlink bridges.

**Why does AGENTS.md matter in a monorepo?**
Nested AGENTS.md files let each package or subdirectory carry its own instructions, resolved by a deterministic closest-file-wins precedence rule. The OpenAI Codex monorepo, with 88 nested files, is the canonical example — a concrete upgrade over a single CLAUDE.md.
