---
title: "CodeGraph for Claude Code and Cursor Guide 2026: Install, Configure, and Measure the ROI"
date: 2026-07-06T14:00:00+00:00
tags: ["codegraph", "claude-code", "cursor", "mcp", "code-index", "ai-coding", "developer-tools"]
description: "A practical 2026 guide to installing and using CodeGraph with Claude Code and Cursor — covering setup, workflow, measurement, governance, and when it's not worth the overhead."
draft: false
cover:
  image: "/images/codegraph-for-claude-code-and-cursor-guide-2026.png"
  alt: "CodeGraph for Claude Code and Cursor Guide 2026"
  relative: false
---

By mid-2026, CodeGraph has become one of the fastest-growing developer tools on GitHub — 57,000+ stars, MIT license, and active development since January 2026. If you use Claude Code or Cursor on a codebase larger than a few thousand lines, you've probably seen the claims: 70% fewer tool calls, 59% lower token consumption, 49% faster response time. Those numbers come from benchmark repos, not every project, but the underlying idea is sound.

I've been running CodeGraph with both Claude Code and Cursor for the past few months across several production repos. This guide covers what I've found works, what doesn't, and how to decide whether it's worth adding to your stack.

## What CodeGraph Is and Why Claude Code and Cursor Users Care

CodeGraph is a local-first, pre-indexed code knowledge graph that exposes itself to AI coding agents through the Model Context Protocol (MCP). It parses your source files with tree-sitter AST extraction, stores the results in a local SQLite database with FTS5 full-text search, and serves queries through MCP tools like `codegraph_explore`, `codegraph_symbol_search`, and `codegraph_call_graph`.

What this means in practice: instead of your agent burning 15 `grep` and `read` calls to figure out who calls a function, it asks CodeGraph once and gets back a structured answer. The agent doesn't need to navigate the filesystem to understand your architecture — it has a pre-built map.

Claude Code and Cursor are the two most common targets because both support MCP natively. Claude Code uses `~/.claude/settings.json` for MCP server registration. Cursor uses `~/.cursor/mcp.json`. CodeGraph's installer handles both automatically.

## The Problem: Agents Waste Time Rebuilding a Map of Your Repo

Every time you start a Claude Code or Cursor session on a large repo, the agent has zero context about your codebase structure. It doesn't know which files define the routing layer, which functions handle database access, or how the authentication flow connects to the middleware chain. It has to discover all of that from scratch — one `grep` at a time.

I watched this happen on a 200,000-line TypeScript monorepo. Claude Code needed to understand the impact of changing a shared utility function. It spent 22 tool calls — grep, read, grep again, read more files — just tracing callers and callees before it could propose a change. With CodeGraph, that same question took two calls: `codegraph_call_graph` to get the callers, then `codegraph_explore` to read the relevant function signatures.

The waste isn't just token cost. It's session time, attention budget, and the increased chance the agent misses something because it stopped searching too early.

## How CodeGraph Works: Tree-Sitter, SQLite, FTS5, MCP, and Auto-Sync

CodeGraph's architecture is straightforward and worth understanding because it affects what you can trust:

- **Tree-sitter extraction** parses each source file into an AST and extracts functions, classes, methods, calls, imports, extends, and implements relationships. This is deterministic — no LLM summaries, no hallucinated relationships. What you get is what the parser found.
- **SQLite storage** with FTS5 full-text search lives in `.codegraph/codegraph.db` inside your project. The database is local, portable, and queryable with standard SQL if you want to inspect it directly.
- **MCP server** exposes tools like `codegraph_explore`, `codegraph_symbol_search`, `codegraph_call_graph`, and `codegraph_route_search`. The server runs as a subprocess launched by your agent's MCP client.
- **Auto-sync** watches your project files, debounces changes with a 2-second quiet window, filters to source files, and incrementally updates the graph. After you save a file, the index catches up within seconds.

The key design decision: CodeGraph indexes structure, not semantics. It knows that `authenticateUser` is called by `loginHandler` and calls `verifyToken`. It does not know what `authenticateUser` *does* in a business sense. That's fine — the agent reads the actual source for semantics. CodeGraph just eliminates the discovery overhead.

## When CodeGraph Helps Most

I've found CodeGraph delivers clear value in these scenarios:

**Large repos (50,000+ lines).** The discovery overhead scales with codebase size. On small projects, grep is fast enough that the MCP overhead isn't worth it.

**Call chain analysis.** Before refactoring a function, you need to know every caller. CodeGraph's `codegraph_call_graph` returns the full chain in one call. I use this constantly for impact analysis.

**Route and handler discovery.** In web frameworks, finding which handler maps to which route usually requires scanning router files. CodeGraph's `codegraph_route_search` handles this directly.

**Onboarding to unfamiliar code.** When I join a new project or revisit one I haven't touched in months, CodeGraph answers "what does this module export?" and "what depends on this interface?" without me or the agent reading every file.

**Test-target selection.** Before running tests, I ask CodeGraph which test files exercise a changed function. It's faster than grep for `describe` blocks and `it` strings.

## When CodeGraph Is Not Worth the Overhead

Be honest about the cases where CodeGraph adds more friction than value:

- **Small repos under 10,000 lines.** The `codegraph init` step takes longer than the time you'd save.
- **Throwaway prototypes.** If the repo won't exist next week, don't bother.
- **Single-file fixes.** You don't need a code graph to edit one file.
- **Unsupported languages.** CodeGraph supports the major languages (TypeScript, Python, Go, Rust, Java, etc.) but if your project is heavy on a niche language, check the tree-sitter grammar list first.
- **Teams that can't maintain agent config.** If your team doesn't keep `CLAUDE.md` or `.cursorrules` up to date, they won't maintain CodeGraph either. The tool is only as good as the discipline around it.

## Install CodeGraph and Register It With Claude Code and Cursor

The install process is one command, but I'll walk through what actually happens so you can debug it if something goes wrong.

```bash
npx @colbymchenry/codegraph install
```

This does three things:
1. Downloads the platform-specific binary (macOS/Linux/Windows, x64/arm64) to a cache directory.
2. Detects which MCP-compatible agents you have installed by checking for their config files.
3. Registers the CodeGraph MCP server in each agent's config.

For **Claude Code**, it adds an entry to `~/.claude/settings.json`:

```json
{
  "mcpServers": {
    "codegraph": {
      "command": "codegraph",
      "args": ["mcp"]
    }
  }
}
```

For **Cursor**, it adds to `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "codegraph": {
      "command": "codegraph",
      "args": ["mcp"]
    }
  }
}
```

After install, restart your agent. Claude Code needs a full restart. Cursor needs a window reload (Cmd+Shift+P → "Developer: Reload Window").

If you're on an older Claude Code version (pre-v2.x), check the [CodeGraph release notes](https://github.com/colbymchenry/codegraph/releases) for compatibility. The MCP protocol has had breaking changes, and mismatched versions cause silent failures.

## Initialize a Project and Confirm the Index Is Working

Navigate to your project and run:

```bash
codegraph init
```

This scans all source files, builds the tree-sitter ASTs, populates the SQLite database, and starts the file watcher. On a 100,000-line TypeScript project, this takes about 30-60 seconds. On a million-line monorepo, closer to 5 minutes.

After init, you should see a `.codegraph/` directory at your project root. Inside it:

```
.codegraph/
  codegraph.db       # SQLite database with FTS5
  codegraph.db.wal   # SQLite WAL file (active during writes)
```

To confirm the index is working, run:

```bash
codegraph explore "find all functions that call authenticateUser"
```

If you get a structured result with function names and file locations, the index is live. If you get an error, check that `.codegraph/codegraph.db` exists and has a non-trivial file size.

## Claude Code Workflow: Prompts, Permissions, and Tool-Call Patterns

Once CodeGraph is registered, Claude Code automatically discovers the MCP tools. You don't need to enable anything manually. The key workflow change is in how you prompt.

Instead of:

> "Find all the places that call `validateInput` and tell me what they do with the result."

Try:

> "Use codegraph to find all callers of `validateInput`, then read the caller functions and summarize the error handling patterns."

The first prompt makes Claude Code fall back to grep and read. The second explicitly directs it to use the MCP tool, which is faster and more complete.

I've found it useful to add a note to `CLAUDE.md`:

```
## CodeGraph

- Use `codegraph_explore` for architecture, flow, and impact questions.
- Use `codegraph_call_graph` before refactoring any exported function.
- After editing, check the staleness banner — if the graph is stale, run `codegraph sync`.
```

Claude Code respects `CLAUDE.md` instructions and will reach for CodeGraph tools more consistently with this guidance.

One thing to watch: Claude Code may ask for permission before running MCP tools depending on your auto-allow settings. If you're in a long session, the repeated permission prompts get annoying. I configure auto-allow for the `codegraph_*` tools in `~/.claude/settings.json`:

```json
{
  "mcpServers": {
    "codegraph": {
      "command": "codegraph",
      "args": ["mcp"]
    }
  },
  "autoAllowTools": ["codegraph_explore", "codegraph_symbol_search", "codegraph_call_graph", "codegraph_route_search"]
}
```

## Cursor Workflow: MCP Registration, Agent Rules, and Practical Queries

Cursor's MCP support works slightly differently. After `codegraph install`, the server is registered in `~/.cursor/mcp.json`. Cursor's agent (Composer or the chat agent) discovers the tools automatically.

The main difference from Claude Code: Cursor doesn't have a `CLAUDE.md` equivalent that the agent reads as system context. Instead, you add rules in `.cursorrules` or through Cursor's Settings → Rules for AI. I add:

```
Use codegraph_explore for codebase navigation questions. When asked about callers, callees, or dependencies of a function, prefer codegraph_call_graph over manual file reads.
```

Cursor's agent tends to be more aggressive about using its built-in codebase indexing (which is quite good in Cursor 2026). CodeGraph adds value specifically for call graph analysis and cross-file dependency tracing, where Cursor's built-in index is weaker.

For practical queries in Cursor, I use the chat panel:

> "codegraph: show me the route handlers that depend on the auth middleware"

The "codegraph:" prefix isn't required — the agent routes to the MCP tool based on the query content — but I've found it helps the agent choose the right tool faster.

## Using `codegraph_explore`: Questions That Work Better Than Grep

The `codegraph_explore` tool accepts natural language queries and returns structured results. Here are the questions I've found most effective:

- "What functions does this module export?" — Returns the public API surface.
- "Who calls `sendEmail`?" — Returns every call site with file and line number.
- "Show me the inheritance chain of `BaseController`." — Returns the class hierarchy.
- "What routes are defined in the admin module?" — Returns route-to-handler mappings.
- "Find all files that import from `@shared/utils`." — Returns import dependency graph.

Compare this to grep: `grep -r "sendEmail" src/` returns every line that mentions the string, including comments, variable names, and false positives. CodeGraph returns only actual call sites because it parsed the AST.

## Measuring the ROI: Tool Calls, File Reads, First-Edit Time, and Missed Impact

The published benchmarks — 70% fewer tool calls, 59% lower tokens, 49% faster response — are median results across seven benchmark repos. Your mileage will vary. Here's how to measure it for your own team:

1. **Pick one workflow.** Don't try to measure everything at once. Pick a common task: adding a new API endpoint, refactoring a shared utility, or updating a database migration.
2. **Run it without CodeGraph.** Count tool calls, file reads, and time to first edit. Record whether the agent missed any call sites.
3. **Run the same task with CodeGraph.** Use the same prompt. Count the same metrics.
4. **Compare.** The difference in tool calls before the first edit is the most reliable signal. File reads before first edit is a close second.

I ran this on a NestJS API project (80,000 lines, 400+ files). Adding a new endpoint that touched the controller, service, and repository layers went from 18 tool calls and 12 file reads without CodeGraph to 4 tool calls and 3 file reads with it. The agent also caught a dependency I would have missed — a middleware that needed updating — because `codegraph_call_graph` returned the full chain.

The less obvious metric: **missed-impact incidents.** Before CodeGraph, I'd occasionally get a review comment saying "you also need to update the X handler." After CodeGraph, those comments dropped to near zero because the agent had the full call graph.

## Keeping the Graph Fresh: Auto-Sync, Manual Sync, Staleness Banners, and CI Options

CodeGraph's auto-sync handles the common case: you edit a file, save it, and within 2-3 seconds the graph updates. But there are edge cases:

- **Branch switches.** If you `git checkout` to a different branch, the file watcher may not catch all the changes. Run `codegraph sync` after switching branches.
- **Large rebases.** After a rebase that touches hundreds of files, the incremental sync can lag. Run `codegraph sync --force` to rebuild from scratch.
- **CI environments.** If you want CodeGraph available in CI (for automated impact analysis or test selection), you can run `codegraph init` as part of your build. The `.codegraph/` directory is developer-local by default — don't commit it to git. Add it to `.gitignore`.

The agent shows a staleness banner when the graph is out of date. If you see it, run `codegraph sync` before continuing. The banner is conservative — it shows up after any file change, even if the change doesn't affect the indexed symbols. I've learned to trust it.

## Security and Governance: Local Indexes, Agent Config Files, and Supply Chain Review

CodeGraph is local-first, which is good for security. The index never leaves your machine. But there are governance considerations:

- **MCP server supply chain.** CodeGraph's MCP server is a binary downloaded by npm. The npm package is `@colbymchenry/codegraph` and the binary is platform-specific. If your organization requires signed binaries or approved package registries, this needs review.
- **Agent config files.** `codegraph install` modifies `~/.claude/settings.json` and `~/.cursor/mcp.json`. These files control what MCP servers your agent can launch. Review the changes before accepting them — the same mechanism that loads CodeGraph can load any MCP server.
- **Auto-allow permissions.** If you configure auto-allow for `codegraph_*` tools, understand that you're giving the agent permission to run arbitrary MCP tools. The risk is low for CodeGraph specifically (it only reads files), but the pattern matters for security posture.
- **`.codegraph/` in shared environments.** If you use shared development servers or dev containers, the `.codegraph/` directory is per-user. Don't share it across users — the SQLite database contains file paths and symbol names that are workspace-specific.

For enterprise teams, I recommend treating CodeGraph like any other developer tool dependency: add it to your approved tool list, review the MCP server configuration, and include it in your onboarding documentation. The [agent skills supply chain security guide](/posts/agent-skills-supply-chain-security-guide-2026/) covers this in more detail.

## Team Adoption Playbook: Start With One Repo and One Workflow

If you're bringing CodeGraph to a team, don't roll it out as a mandate. Here's what worked for me:

1. **Pick one repo.** Choose the largest, most complex codebase your team owns. The ROI is highest there.
2. **Pick one workflow.** Route changes, SDK API updates, or refactoring — whichever your team does most often.
3. **Install and init for one developer.** Let them run it for a week and report back on tool call counts and missed-impact catches.
4. **Share the measurement.** Show the before/after numbers. Developers care about concrete metrics, not "it's faster."
5. **Add to onboarding docs.** Include the install, init, and `CLAUDE.md` / `.cursorrules` snippets in your team's onboarding guide.

The developers who resist are usually the ones working on small, focused changes. They're right — CodeGraph doesn't help them much. The developers who adopt it are the ones doing cross-cutting refactors, impact analysis, and large feature work.

## Troubleshooting Common CodeGraph Setup Problems

**"codegraph: command not found" after install.** The installer adds the npm global bin to your PATH, but you may need to restart your shell or source your profile. Run `npx @colbymchenry/codegraph install` again — it's idempotent.

**MCP tools not showing up in Claude Code.** Check `~/.claude/settings.json` for the codegraph entry. If it's missing, run `codegraph install` again. If it's present but tools don't appear, restart Claude Code completely.

**MCP tools not showing up in Cursor.** Check `~/.cursor/mcp.json`. If the entry is there, reload the window. If tools still don't appear, check Cursor's MCP logs in Help → Toggle Developer Tools → Console.

**"codegraph init" is slow on large repos.** This is expected. The first init parses every source file. Subsequent inits are incremental. If you need to speed it up, exclude directories you don't need indexed (node_modules, build output, generated code) — CodeGraph respects `.gitignore` by default.

**Auto-sync not catching changes.** Check that the file watcher is running. `codegraph status` shows whether the watcher is active. If it's not, restart it with `codegraph watch`.

## FAQ: CodeGraph for Claude Code and Cursor in 2026

**Does CodeGraph work with Claude Code v2.x?** Yes. The MCP protocol is stable in v2.x. If you're on an older version, check the release notes.

**Does CodeGraph work with Cursor's Composer?** Yes. Composer discovers MCP tools the same way the chat agent does.

**Can I use CodeGraph without MCP?** No. MCP is the only transport. If your agent doesn't support MCP, CodeGraph won't work.

**Does CodeGraph send my code anywhere?** No. Everything is local. The SQLite database stays on your machine. The MCP server runs as a local subprocess.

**Should I commit `.codegraph/` to git?** No. Add it to `.gitignore`. It's a developer-local cache. Each developer should run `codegraph init` after cloning.

**How much disk space does the index use?** On a 200,000-line TypeScript project, about 15-20 MB. The SQLite database is compact.

**Does CodeGraph support monorepos?** Yes. Run `codegraph init` at the monorepo root. It indexes all packages. You can also run it per-package if you want separate indexes.

**What happens when I switch branches?** The auto-sync catches file changes, but after a large branch switch, run `codegraph sync` to be safe.

CodeGraph isn't a magic bullet. It won't make your agent write better code or catch every edge case. What it does is eliminate the discovery tax — the wasted tool calls and file reads that agents burn just figuring out where things are. For anyone working on a codebase large enough that grep feels slow, that's a meaningful improvement.
