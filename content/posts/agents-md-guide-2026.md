---
cover:
  image: /images/og-default.png
  alt: RockB editorial guides
  relative: false
date: 2026-04-18 06:11:17+00:00
description: Write repository instructions that can be checked, understand tool-specific AGENTS.md loading rules, and verify which instructions actually apply.
draft: false
schema: schema-agents-md-guide-2026
tags:
- AGENTS.md
- AI coding
- developer tools
- Claude Code
- Cursor
- Codex
title: 'AGENTS.md Guide 2026: Instruction Discovery, Scope, and Verification'
lastmod: '2026-10-20T07:02:10.628622+00:00'
---

AGENTS.md is a convenient place to explain how work should be done in a repository. Its usefulness depends on whether the agent actually loads the file, whether the instructions match the current project, and whether the commands work.

Use this guide to create a small verified instruction file and a discovery worksheet. Treat support as a property of a particular client and version, not a promise attached to the filename.

## The format is shared; loading behavior is not

The [AGENTS.md project](https://agents.md/) describes a Markdown convention for agent instructions. Client implementations add their own search paths and precedence rules.

| Client | Behavior to verify in your installed version |
|---|---|
| Codex | Global instructions plus project-root-to-working-directory discovery; override files take precedence within a directory |
| Claude Code | Native AGENTS.md reading is available, but CLAUDE files and the project-instructions setting affect whether it loads |
| Cursor | Supports root and nested AGENTS.md, alongside its own rule system |
| GitHub Copilot | Agent instructions, repository-wide instructions, and path-specific instructions have different feature support |

[Codex documentation](https://learn.chatgpt.com/docs/agent-configuration/agents-md.md) specifies a default **32 KiB combined project-document limit**, not a universal line limit for each file. It selects at most one applicable file per directory, checking `AGENTS.override.md` before `AGENTS.md` and configured fallbacks.

[Claude Code documentation](https://code.claude.com/docs/en/memory) says native reading requires **v2.1.277 or later**, with session-specific qualifications. By default, applicable `CLAUDE.md`, `.claude/CLAUDE.md`, or `CLAUDE.local.md` files can suppress AGENTS.md loading; `claude-md-and-agents-md` changes that behavior. Claude does not interpret `AGENTS.override.md` as Codex does.

Consult [Cursor's rules documentation](https://cursor.com/docs/rules) and [Copilot's instruction documentation](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/add-custom-instructions/add-repository-instructions) for the particular surface you use. A rule that works in an editor session is not automatically proven to work in a hosted review job.

## Start with facts an agent cannot infer cheaply

Good candidates include a non-obvious test command, the boundary between generated and authored files, required environment setup, and the expected validation for a change. Avoid copying a long directory listing that will drift.

The [instruction worksheet](/research/content-quality-2026-10/instruction-discovery.csv) has fields for client version, working directory, discovered file, applicable scope, command, and observed result. Fill it in from the actual client session and command output.

For a project that really uses Python's standard-library unittest discovery, a small starting file could look like this:

```markdown
# Repository guidance

## Validation
Run `python3 -m unittest discover -s tests` from the repository root.
If dependencies or fixtures are missing, report the failure and its cause.

## Change scope
Keep generated outputs separate from their source files.
Explain behavior changes and the validation performed.

## Project-specific boundaries
Document the actual deployment or data-migration procedure here.
```

This is a template, not a statement about your project. Replace the command if the repository uses a different runner. Do not add instructions about nonexistent files, guessed package managers, or checks that only work on the author's machine.

## Verify discovery before debating wording

Create a harmless temporary instruction, such as asking for a distinctive label in a final report. Start a fresh agent session from the repository root, then from a relevant subdirectory. Inspect the client's documented instruction diagnostics where available and check the observed behavior.

If the marker is absent, examine the working directory, a higher-precedence file, file-size limits, and client feature support. Do not interpret the agent's confident claim that it “read everything” as sufficient evidence.

Remove the temporary marker after the check. Save the client version and loaded paths in the worksheet. Recheck after changing clients, moving the working directory, or introducing local instruction files.

For a nested package, keep its instructions focused on local exceptions. If the same rule appears in several places with different wording, choose one owner and link to it where the client supports that workflow.

## Measure whether the instructions help

Research on repository context files reports results under different tasks, agents, and instruction-generation methods. Compare the setups in [Evaluating AGENTS.md](https://arxiv.org/html/2602.11988v1) and [the agent-efficiency study](https://arxiv.org/html/2601.20404v1) before transferring an outcome to your repository. Neither establishes a universal speedup for every instruction file.

## Use a small maintenance loop

Select representative maintenance tasks and keep the baseline repository revision fixed. Compare task completion, corrective iterations, invalid commands, test failures, and review effort with and without the proposed instructions. Preserve failed runs as well as successful ones.

When an instruction causes confusion, repair the underlying command or scope before adding another paragraph. Review the file whenever a build command, package layout, or deployment process changes. An accurate short file is more useful than an elaborate file that describes a past version of the project.

## Revision note

**Updated October 20, 2026.** Removed the universal speedup, universal line-count rule, and blanket every-tool claim. Added version-sensitive loading behavior, a reproducible discovery protocol, and links to the original research with its limits.

## Primary sources

Checked October 20, 2026: [agents standard](https://agents.md/); [codex agents](https://learn.chatgpt.com/docs/agent-configuration/agents-md.md); [claude memory](https://code.claude.com/docs/en/memory); [cursor rules](https://cursor.com/docs/rules); [copilot instructions](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/add-custom-instructions/add-repository-instructions); [agents study](https://arxiv.org/html/2602.11988v1); [agents efficiency study](https://arxiv.org/html/2601.20404v1).
