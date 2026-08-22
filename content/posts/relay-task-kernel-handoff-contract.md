---
title: "Relay Task Kernel: One Agent Handoff Contract Standard for Claude Code, Codex, Gemini CLI and Copilot"
date: 2026-08-22T01:01:54+00:00
tags:
  - agent handoff contract
  - multi-agent coding
  - Claude Code
  - Codex
  - Gemini CLI
  - GitHub Copilot
  - AGENTS.md
  - context memory
description: "One agent handoff contract standard for Claude Code, Codex, Gemini CLI and Copilot: Relay Task Kernel consolidates four rule files into one shared source of truth."
draft: false
cover:
  image: "/images/relay-task-kernel-handoff-contract.png"
  alt: "Relay Task Kernel: One Agent Handoff Contract Standard for Claude Code, Codex, Gemini CLI and Copilot"
  relative: false
schema: "schema-relay-task-kernel-handoff-contract"
---

The agent handoff contract standard you are looking for is Relay Task Kernel (RTK): a zero-dependency CLI that consolidates the four per-agent instruction files — AGENTS.md (Codex), CLAUDE.md (Claude Code), GEMINI.md (Gemini CLI), and .github/copilot-instructions.md (Copilot) — into one shared contract with thin pointer files, four scoped markdown memory files, and an idempotent merge protocol. Instead of maintaining the same rules four times and watching them drift apart, RTK gives every agent one source of truth. This guide explains the problem, how RTK works, the merge and memory contracts, presets, and how it compares to alternative handoff tools.

## The Problem: One Repo, Four Agent Rule Files, Zero Shared Memory

Modern developers do not pick one coding agent and stay loyal. Teams rotate Claude Code, OpenAI Codex, Google Gemini CLI, and GitHub Copilot in the same repository — often in the same week. The problem is that each harness reads a different instruction file:

| Agent | Instruction file it reads |
|-------|---------------------------|
| Claude Code | `CLAUDE.md` |
| OpenAI Codex | `AGENTS.md` |
| Google Gemini CLI | `GEMINI.md` |
| GitHub Copilot | `.github/copilot-instructions.md` |

If you have all four installed, the same project rule has to be written in four places. When one file gets updated and the others do not, three of the four agents silently keep operating on stale rules. This is the "four-files problem" that Relay Task Kernel is designed to solve.

Worse, the rules are only half of the context problem. Agent **memory** is equally fragmented. When a session ends with a Claude Code run and Codex starts fresh the next morning, the new agent has no idea what half-finished work is sitting in the repo, what decisions were made yesterday, or which mistakes it is told to avoid. A genuinely useful handoff contract standard has to address both rule files **and** memory.

## What Is Relay Task Kernel (RTK)? — One Contract, Zero Dependencies

Relay Task Kernel is an open-source, MIT-licensed CLI published by the `leamagic-cyber` GitHub account. It is intentionally tiny: **zero dependencies**, Node.js >= 18.17 required, and a small command surface. Its entire premise is that a handoff contract should be a *thin pointer layer* over one canonical source of truth, not a fourth place to duplicate content.

The core value proposition is stated in the project README:

> "RTK — One handoff contract that Claude Code, Codex, Gemini CLI and Copilot all read."

The tool makes the four per-agent files thin pointers that delegate to a single shared contract. You write the rules once, and every agent resolves to the same content regardless of which harness invoked it.

Compared to the leading coding agents it is designed to tame, RTK is intentionally minimal. For scale, Claude Code sits at roughly **142,298 GitHub stars**, OpenAI Codex at **~111,300**, and Gemini CLI at **~106,607** — each a mature, heavily used harness. RTK, by contrast, is a 2-star, single-author project created on 2026-08-17. That maturity gap matters and we return to it in the verdict.

## How the One-Contract Model Works

The core of the model is a machine-wide protocol plus a per-project overlay.

**Global protocol (`~/.rtk/`).** Running `npx github:leamagic-cyber/relay-task-kernel init --global` writes the machine-wide contract to `~/.rtk/`. This contains:

- `RTK.md` — the canonical global contract
- `rules/` — reusable rule fragments
- `templates/` — templates for the thin pointer files
- `schemas/` — JSON schemas for validating the contract

**Project overlay.** Running `rtk init` inside a repo creates:

- `START_HERE.md` — the entry point a fresh agent reads
- Thin entries for each agent (`AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `.github/copilot-instructions.md`) that all point to the shared contract
- `.rtk/project.md` — the project-specific overlay

**The `--all` flag.** Running `rtk init --all` does both the machine-wide write and the project overlay in one pass, which is the recommended starting command:

```bash
npx github:leamagic-cyber/relay-task-kernel init --all
```

**Tighten-only overlay rule.** A deliberate design constraint is that the project overlay may only *tighten* global rules, never loosen them. A single commit in a single repo cannot switch off a global safety rule. This prevents one project from silently weakening the standards every other project relies on.

The CLI surface includes `init`, `init --global`, `init --all`, `check`, `eject`, and `presets`, with flags such as `--dry-run`, `--yes`, `--dir`, `--preset`, `--no-backup`, `--crlf`, and `--set`. The `eject` command is the escape hatch: it converts the thin pointers back into self-contained files so you are never locked in.

## The Merge Contract: Idempotent, Non-Destructive, Reversible, Checkable

The hardest engineering problem in a shared-contract design is merging updated global rules back into already-created project files without clobbering the developer's own edits. RTK solves this with fenced regions wrapped in markers:

```text
<!-- RTK:BEGIN -->
...shared content...
<!-- RTK:END -->
```

Anything you write outside the markers is yours and survives every re-run. This yields four guarantees that matter for a tool that touches files on every agent run:

- **Idempotent.** Re-running the merge reports 0 changed files when nothing is out of date. No churn, no noisy diffs.
- **Non-destructive.** Your hand-edited text outside the RTK markers is never touched. If you add project-specific instructions above or below a block, they persist across every update.
- **Reversible.** Before each merge, RTK writes an automatic `.backup`, so a bad merge can be rolled back.
- **Checkable.** `rtk check` verifies that every expected block is still present and exits with a non-zero status (1) if a block has been deleted. A missing block is a red flag that an agent, or a human, edited around the contract.

This is a meaningful contrast to the "hand-edit four files" workflow, where silent drift is the default outcome. RTK makes drift detectable rather than invisible.

## Memory That Survives Sessions: The Four Scoped Markdown Files

Where most rule-file tools stop at instructions, RTK treats agent memory as a first-class citizen. Memory is modeled as four plain markdown files — not a database, not a vector store, deliberately zero-dependency:

| File | Holds |
|------|-------|
| `project-brief.md` | Why the project exists, its goals, scope, constraints |
| `current-state.md` | What is done, what is half-finished, what is blocked right now |
| `user-preferences.md` | How the user likes work done: style, conventions, tone |
| `mistakes-to-avoid.md` | Past incidents and the rules derived from them, so a fresh session does not repeat them |

The most important file is `current-state.md`. It holds half-finished work that a brand-new session cannot reconstruct from the code alone — the thing you most want to hand across a boundary. When Claude Code ends a session at 11 PM and Codex opens the repo at 9 AM, `current-state.md` is the bridge that prevents "start over from scratch" or "silently redo the same work."

The `mistakes-to-avoid.md` file also anchors a stronger safety claim: because it records real incidents, the rules embedded in the contract are evidence-driven rather than guessed. This is not hypothetical — RTK's own origin is an internal script that ran a Traditional Chinese content site of ~90 published articles daily, rotating Claude Code, Codex and Gemini. The rules in the first versions captured real incidents: a draft that got published before it was ready, an accidental production deploy, lost decisions from a restarted session.

## Hardening with Presets and Template Variables

Not every project has identical risk. RTK ships presets — small JSON additions, roughly ten lines each — that encode project-specific gates:

- **`content-site`** — adds a publishing gate so drafts never leak to production.
- **`oss-library`** — forbids agents from touching versions, tags, and releases, protecting the release contract of a public library.

A preset is a declarative, auditable block rather than a natural-language instruction that an agent might silently ignore. This is consistent with the tightening-only rule: presets make rules stronger, and the merge fence makes sure they stay present.

## RTK vs the Alternatives

RTK is not the only tool trying to solve the handoff and context problem. The ecosystem has at least four overlapping approaches, each with a different center of gravity:

| Tool | Focus | Stars | How it differs |
|------|-------|-------|----------------|
| **RTK** | Memory + thin pointers, one shared rule contract | 2 | Rule consolidation plus scoped markdown memory, merge fences |
| **brief-spec** | Type-aware, evidence-backed delivery contract | 14 | Emphasizes a typed handoff payload and evidence rather than shared rule files |
| **harness-all** | Local-first PM + Engineering harness | 27 | Bilingual PM+Eng workflow with contract handoffs, wider in scope than agent rule files |
| **MDDesign** | Design-first orchestration plugin | 13 | Centers DESIGN.md planning orchestration; cross-IDE but design-document-first |
| **coderail** | Governance kit aligned to a "North Star" | 7 | Governance and goal-alignment angle; K0–K6 kernel with drift checks |

The table is useful as a mental model: every tool agrees that "one source of truth" matters, but they carve the problem differently. RTK focuses on *memory plus thin pointers* — the simplest possible contract that makes four agents read one file. If your pain is more about delivering *evidence* between agents, brief-spec may be closer; if you want *governance* against the project North Star, coderail; if you want a full *planning-and-design* orchestration, MDDesign.

## The AGENTS.md Ecosystem Context

The RTK approach sits on top of a broader movement: **AGENTS.md has become a de facto standard**. Per the agents.md project, AGENTS.md is "a simple, open format for guiding coding agents" and is already used by **more than 60,000 open-source projects**. That is a large existing base of repos that treat a markdown file as the "README for agents."

This ecosystem context matters for two reasons. First, it lowers the adoption cost of RTK: because AGENTS.md is already the common denominator that Codex and many other harnesses read, a handoff contract that centers on AGENTS.md is interoperable with a large installed base. Second, it means the *fragmentation problem is real and growing* — every new harness that introduces its own instruction file adds another place for the same rule to be written. Gemini CLI explicitly supports `GEMINI.md` as a persistent per-project context file, which confirms that per-agent context files are an intentional, widespread pattern. That is precisely the pattern a consolidation tool like RTK addresses.

## Who Should Adopt a Handoff Contract (and Who Shouldn't)

**Adopt it if:**

- You run two or more of Claude Code, Codex, Gemini CLI, or Copilot in the same repository.
- You are tired of editing the same rule in four files and watching them drift.
- You frequently hand work from one agent session to another and lose context — where the "current state" of half-finished work is the #1 gap.
- You want safety rules that cannot be silently weakened by a single project.

**Wait, or skip it, if:**

- You use exactly one agent and one rule file. Consolidation buys you nothing and adds a layer.
- You need production stability today. RTK is a 2-star, days-old, single-author project; it has not survived the test of real-world bug reports.
- You prefer hand-authoring every file explicitly and distrust tooling that writes your instruction files.

A reasonable middle path is to *adopt the pattern, not the tool*: keep one canonical contract file, make the others thin includes, and review merges in version control. That gives you most of the value with none of the dependency.

## Verdict & When to Watch RTK

Relay Task Kernel is a well-designed answer to a genuinely painful problem. The four-files problem is real, the memory files address an even less-solved gap (cross-session state), and the merge contract's idempotent/non-destructive/reversible/checkable guarantees are the right engineering priorities. As a *pattern*, the one-contract-with-thin-pointers approach deserves to be a standard.

As a *tool*, RTK is early. At 2 stars and one day old it has not yet proven itself in the wild, and a handoff contract that touches your instruction files on every agent run is exactly the kind of tool you want battle-tested. The good news is that the pattern is dependency-light and easy to verify: you can read the source, run `--dry-run`, inspect the `.backup` files, and watch a single `rtk check` cycle before letting it anywhere near your production repo.

**Bottom line:** if you rotate multiple coding agents in one repo and you are losing state between sessions, watch Relay Task Kernel closely — and meanwhile copy the pattern. One source of truth, four thin pointers, and a `current-state.md` file is a handoff contract standard worth adopting regardless of which tool eventually wins.

## FAQ

### What is the agent handoff contract standard for multiple coding agents?

Relay Task Kernel (RTK) is the leading small-tool example of the standard: one shared contract (RTK.md) plus thin pointer files for AGENTS.md, CLAUDE.md, GEMINI.md, and .github/copilot-instructions.md, so all four agents read the same rules. The "standard" is the pattern of consolidating per-agent files into a single source of truth with non-destructive merges.

### Do I need RTK if I only use Claude Code?

Probably not. RTK's value comes from the multi-agent fragmentation: if you use a single agent reading a single file (for example only CLAUDE.md), you have no drift problem to solve, and adding a tool layer is unnecessary. Adopt it mainly when you rotate Claude Code, Codex, Gemini CLI, or Copilot in the same repo.

### How does RTK prevent instruction files from drifting apart?

The four agent files are generated as thin pointers to one shared contract, plus a merge protocol with fenced regions (RTK:BEGIN/END) that is idempotent, non-destructive, reversible with auto-backup, and checkable via `rtk check`. This is a deterministic source of truth instead of four manually-edited copies that silently diverge.

### What are the four memory files in RTK, and why do they matter?

They are `project-brief.md`, `current-state.md`, `user-preferences.md`, and `mistakes-to-avoid.md` — plain markdown files, not a database. `current-state.md` is the most important because it records half-finished work and recent decisions, so a fresh agent session does not have to re-explain the project or repeat past mistakes.

### Is Relay Task Kernel production-ready in 2026?

Not yet. RTK is a 2-star, ~0-dependency, single-author project created in mid-August 2026, so it has not had a wide adoption or battle-testing cycle. The *pattern* (one contract plus thin pointers) is safe to adopt today; the specific tool is worth watching and verifying with `rtk check` and `--dry-run` before you commit to it in production.
