---
cover:
  alt: CallDiff 2026 — Diffs for Function Call Stacks Across Git Commits
  image: /images/calldiff-function-call-stack-diffs-2026.png
  relative: false
date: 2026-08-11T01:01:59+00:00
description: CallDiff 2026 diffs function call stacks across git commits in 22 languages — a
  tree-sitter-based call graph diff for agentic code review.
draft: false
tags:
- calldiff
- function call stack diff
- call graph diff
- agentic code review
- tree-sitter call graph
- codiff alternative
title: CallDiff 2026 — Diffs for Function Call Stacks Across Git Commits
schema: "schema-calldiff-function-call-stack-diffs-2026"
---

CallDiff is an open-source, tree-sitter-based CLI that shows how function call stacks change between two git commits, "like git diff, but for who-calls-whom." It compares call graphs across 22 languages (TypeScript, Python, Go, Rust, Java, C/C++, and more) so you can see which callees appeared, disappeared, or moved — instead of wading through buried line diffs. Built for AI-agent code review, it ships `diff`, `tree`, and `reach` commands plus machine-readable JSON output.

## What Is CallDiff and Why Do Call-Stack Diffs Matter for Agentic Review?

When an AI coding agent rewires call flow across a codebase, plain line diffs bury the shape of the change. You see dozens of removed and added lines, but the important question — *did the agent actually reroute this function to the intended new callee?* — stays hidden. CallDiff answers that question by diffing the call graph itself: which callees appeared, which disappeared, and which moved under an entrypoint.

The tool was created on 2026-08-07 by tanishqkancharla and already sits at 296 stars with 14 forks as of research on 2026-08-11 (GitHub API, api.github.com/repos/tanishqkancharla/calldiff). It is MIT-licensed, written in TypeScript, and installable via `npx calldiff@latest` or `npm install -g calldiff`.

The philosophy is an extension of the "shape-of-the-change" idea popularized by stacked-diff workflows. Jackson Gabbard's widely-cited post "Stacked Diffs Versus Pull Requests" argues that diff-shaped review beats PR-shaped review because engineers review the *shape* of a change, not just the file layout. CallDiff applies that same insight one level deeper: to the call graph, not the file diff.

## How Do You Install CallDiff and What Are the Three Commands?

Installation is a one-liner. With Node.js installed, run:

```bash
npx calldiff@latest
```

or globally:

```bash
npm install -g calldiff
```

On first use, CallDiff installs the tree-sitter grammars it needs into `~/.cache/calldiff/grammars`. You can override this location with the `CALLDIFF_GRAMMAR_CACHE` environment variable if you need a custom or shared cache path.

CallDiff exposes three commands:

| Command | What It Does | Required Flags |
|---|---|---|
| `diff` | Git-diff-shaped call-stack diff between two commits | none |
| `tree` | Plain ASCII call tree of a single commit | `--entry` |
| `reach` | All call paths from one symbol to another | `--entry` and `--to` |

The `diff` command is the core. It compares two git refs (for example `main` and `feature`) and produces an output shaped like `git diff`: `-` means a callee that is gone from the "from" commit, and `+` means a callee that is new in the "to" commit.

## How Do You Read a Call-Diff Output: ASCII Call Trees and +/- Semantics?

CallDiff prints colored ASCII call-stack trees by default. Each tree is rooted at an entrypoint, and the branches show which functions call which. When you run a diff, you get side-by-side or sequential trees where the +/- markers tell you precisely what changed in the call flow.

A minimal read: if a `-` appears under an entrypoint, that callee existed before and is now gone. If a `+` appears, a new callee was introduced. If a branch "moved," you'll see a function appear under a different parent — the same symbol relocated in the call graph. That moved-branch signal is exactly what a line diff cannot show you, and it is the most valuable output for verifying an agent's work.

For agents and scripts, you can switch the output format with `--format json|yaml|md|jsonl`. JSON output is the most useful for programmatic consumption: you can pipe it into CI checks, feed it into a review agent, or write assertions that a specific callee did or did not appear in the new call stack.

## CallDiff vs Codiff: 22 Languages vs 2

The closest direct competitor is codiff, a structural call-graph diff tool by issahammoud that is also built for coding agents. Both solve the same problem — showing what changed at the function/call level instead of the line level — but they diverge sharply on language support and ecosystem.

| Feature | CallDiff | Codiff |
|---|---|---|
| Languages | 22 (TS, Python, Go, Rust, Java, C/C++, C#, Ruby, PHP, Kotlin, Swift, Scala, Lua, Elixir, Bash, Haskell, Zig, Solidity, OCaml, JS/JSX/TSX) | 2 (Python, TypeScript) |
| Install | `npx calldiff@latest` / `npm install -g calldiff` | `pip install codiff` |
| Language | TypeScript | Python |
| Diff modes | `diff`, `tree`, `reach` | `diff` (working tree vs HEAD, or `--base`/`--head`) |
| Agent output | `--format json|yaml|md|jsonl` | `--format mermaid` |
| CI/action | n/a (built on incur, MCP-ready) | GitHub Action on Marketplace |
| Stars (2026-08-11) | 296 | 7 |
| Offline | Yes (syntactic) | Yes (no LLM, no embeddings) |

The single strongest objective advantage is breadth: 22 languages versus codiff's 2. In a polyglot 2026 codebase, that is the difference between a tool you can standardize on and one you can only use in isolated corners. Codiff compensates with Mermaid diagram output for PR descriptions and a ready-made GitHub Action, and both are fully offline and syntactic. But if your team touches Python *and* TypeScript *and* Go, CallDiff's 22-language reach is decisive.

## Is CallDiff Agent-First? JSON, --llms, skills add, and MCP

CallDiff is designed to be consumed by AI agents, not just humans. That agent-first orientation shows up in several concrete features:

- **`--format json|yaml|md|jsonl`**: machine-readable output so an agent or CI script can parse the call-flow diff directly.
- **`--llms`**: an incur-native flag that emits an LLM-friendly rendering of the tool's help and behavior.
- **`skills add` and `mcp add`**: CallDiff builds on the incur CLI framework (wevm/incur, 594 stars, TypeScript), which lets you register CallDiff as an MCP server or add it as an agent skill.
- **CTAs after diffs**: incur prints call-to-action prompts after diffs, guiding the next review step.

The underlying framework, wevm/incur, describes itself as a "CLI framework for agents and humans." That dual target is the whole point: CallDiff is built to slot into agent toolchains as easily as it sits in a human developer's terminal. The tool even nudges users to have agents walk through their changes — the prompt is "dearest clod, walk me through the code changes you made using `npx calldiff@latest`."

## What Are CallDiff's Realistic Limitations?

CallDiff is syntactic (AST-based via tree-sitter), not a full typechecker. That design choice buys speed, error tolerance, and 22-language breadth, but it carries real limits you should know before trusting it blindly:

- **Dynamic calls won't resolve.** If a function is called through a variable, dispatch table, or reflection, the AST has no static binding to follow, so CallDiff cannot trace it.
- **Entrypoint inference is conservative.** CallDiff only reports entrypoints whose expanded call trees changed, and it catches exported functions — not every internal helper.
- **Grammars install on first use.** The first run can be slow while tree-sitter grammars download into the cache; plan for that in CI.

These are the standard trade-offs of static call-graph extraction. CallDiff is a review aid, not a runtime profiler. It tells you what the code *says* is called at a structural level; it does not tell you what is actually executed under load. For verifying agent rewiring, that is usually exactly what you want — a fast, deterministic, offline check of call-flow intent.

## A Walkthrough: Verifying an Agent Rewired a Call Flow Across Commits

Here is the practical workflow that makes CallDiff shine. Imagine an agent claimed it moved authentication logic from a legacy `auth/` module into a new `iam/` service, and you want to verify the rewiring without reading 200 lines of diff.

```bash
# 1. Install
npx calldiff@latest

# 2. Diff the two commits you care about
calldiff diff main feature

# 3. Machine-check the result in CI or from an agent
calldiff diff main feature --format json | jq '.entrypoints[].callees'
```

In step 2 you read the ASCII call tree: you should see `-` markers under the old `auth.authenticate` entrypoint and `+` markers under the new `iam.authorize` entrypoint, with the callee branches relocated. That relocation is the proof the agent actually rerouted the flow. In step 3 you can automate the assertion: check that no `-` remains under `iam.authorize` and that the expected new callee appears.

For a full review loop, hand the tool to an agent: paste "dearest clod, walk me through the code changes you made using `npx calldiff@latest`" and let it produce a call-flow walkthrough from the structured output.

## Who Should Use CallDiff and How Does It Fit a 2026 Review Stack?

CallDiff is for two audiences:

1. **Teams reviewing AI-agent changes.** If your workflow includes agents rewriting call flow, line diffs are no longer enough. CallDiff surfaces whether the call graph was rewired as intended — the check that matters most.
2. **Polyglot teams that want one review tool.** With 22 languages, you can standardize call-graph review across Python, TypeScript, Go, Rust, Java, and more, where codiff only covers Python and TypeScript.

It fits naturally alongside your existing review stack: use `git diff` for the file-level shape, CallDiff for the call-graph shape, and CI assertions over the JSON output for automated verification of agent changes. It is MIT-licensed, offline, syntactic, and free — the only costs are the first-use grammar download and the honest caveat that dynamic calls stay invisible.

If you are reviewing agent-produced rewiring in 2026, CallDiff is the fastest way to see who-calls-whom change between commits.

## FAQ

**What is CallDiff?**
CallDiff is an open-source CLI that diffs function call stacks between two git commits, "like git diff, but for who-calls-whom." It uses tree-sitter AST parsing to compare call graphs across 22 languages and is built for agentic code review.

**How do I install CallDiff?**
Run `npx calldiff@latest` or `npm install -g calldiff`. It is MIT-licensed and written in TypeScript. On first use it downloads the tree-sitter grammars it needs into `~/.cache/calldiff/grammars`.

**What languages does CallDiff support?**
22 languages: TypeScript, TSX, JavaScript, JSX, Python, Go, Rust, Java, Ruby, C, C++, C#, PHP, Kotlin, Swift, Scala, Lua, Elixir, Bash, Haskell, Zig, Solidity, and OCaml.

**How is CallDiff different from codiff?**
CallDiff supports 22 languages versus codiff's 2 (Python and TypeScript), and at research time had 296 stars versus codiff's 7. Codiff adds Mermaid output and a GitHub Action; CallDiff adds JSON/YAML/MD/JSONL output, `tree` and `reach` commands, and MCP/skills integration via the incur framework.

**Does CallDiff resolve dynamic calls?**
No. CallDiff is syntactic (AST-based), not a full typechecker, so dynamic or dispatched calls won't resolve. It's best used as a fast, offline check of static call-flow intent, not as a runtime profiler.
