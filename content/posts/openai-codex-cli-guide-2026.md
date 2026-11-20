---
cover:
  alt: 'OpenAI Codex CLI Guide 2026: Terminal AI Coding with the Rust-Built Agent'
  image: /images/openai-codex-cli-guide-2026.png
  relative: false
date: 2026-04-24 18:04:05+00:00
description: "How OpenAI Codex CLI edits files: the *** Begin Patch envelope, the parser's
  grammar and its two boundary errors, the sandbox check behind auto-approve, and the
  apply_patch instruction the model actually reads."
draft: false
lastmod: 2026-11-18 00:00:00+00:00
schema: schema-openai-codex-cli-guide-2026
tags:
- ai-coding
- developer-tools
- ai-agents
- openai
- apply-patch
title: "OpenAI Codex CLI 2026: What apply_patch Actually Does, and Why the Tool Description Matters"
---

OpenAI Codex CLI is a terminal-based AI coding agent that reads your codebase, writes and edits files, runs tests, and commits changes — all from your command line. Unlike web-based AI tools, Codex CLI runs locally against your actual repository, understanding real project context rather than a pasted snippet.

*Revised 18 November 2026. This revision adds a mechanics section on the `apply_patch` tool — the envelope it emits, the grammar the parser enforces and the sandbox check that decides whether you are asked — and withdraws several usage figures that earlier revisions repeated without a primary source: weekly active users, npm download totals, GitHub stars, the share of the codebase written in Rust, and the claimed start-up and memory deltas. Those numbers could not be re-verified from source during this revision, so they are removed rather than restated. A correction pass the same day narrowed two statements to what the pinned source actually says: the slash-command table is a selection from a 66-variant enum rather than the enum itself, and patch auto-approval covers the profiles that apply no outer sandbox as well as the sandboxed branch.*

## What Is OpenAI Codex CLI? (The Rust-Built Terminal AI Agent)

OpenAI Codex CLI is an open-source, terminal-native AI coding agent that plans, writes, edits, and tests code within your local development environment. Unlike browser-based AI assistants, it reads your codebase, executes shell commands, and manages file changes — a repository-scoped engineering agent rather than a text-completion tool. The source lives in the [openai/codex repository](https://github.com/openai/codex/tree/cc7a62e19cb4703495e3a6d01e1af076e8223833); the CLI is the Rust workspace under `codex-rs/` in that tree, and this revision reads it at commit `cc7a62e19cb4703495e3a6d01e1af076e8223833` (18 November 2026).

The differentiator against chat-based assistants is the approval machinery, not the model: every file edit and every shell command passes through a policy check, so autonomy is a configuration decision rather than a default. That is also why the mechanics matter. The agent does not write files the way a human writes a diff, and the check that decides whether you are prompted has specific, readable conditions. Both are in the mechanics section below.

### Why the Rust Rewrite Matters

Codex CLI ships as a compiled binary that runs without a Node.js runtime, which matters for CI runners, remote servers and container images where the npm path would add a toolchain to maintain. The Rust core is also what makes OS-level sandbox enforcement practical: patch application and command execution route through process isolation, so a policy decision has teeth instead of being advisory. This guide does not restate vendor performance figures for that rewrite; the observable consequence for an operator is the approval and sandbox path described below.

---

## Installing Codex CLI on macOS, Windows, and Linux

Codex CLI installs from npm (universal), Homebrew (macOS), the standalone installer, or a release binary (Linux/CI); the channels and archive names below are the ones the repository's [README](https://raw.githubusercontent.com/openai/codex/cc7a62e19cb4703495e3a6d01e1af076e8223833/README.md) lists at the pinned commit. Choose npm if you want the latest release immediately; choose Homebrew if you prefer managed updates integrated with your existing workflow. For CI pipelines or Docker images, the binary approach avoids runtime dependencies entirely. Before you install, confirm you have Node.js 16 or newer for the npm path — that is the `engines` field the published package declares in its [registry metadata](https://registry.npmjs.org/@openai/codex/latest). Installation is the same whether you're targeting a personal MacBook, a Linux VPS, or a Windows machine via WSL2.

### macOS (Homebrew or npm)

```bash
# Option A: Homebrew (recommended for macOS)
brew install --cask codex

# Option B: npm global install
npm install -g @openai/codex

# Verify installation
codex --version
```

### Windows (PowerShell + WSL2)

Native Windows support runs through WSL2. PowerShell is supported with sandbox restrictions applied via Windows sandbox API.

```powershell
# Install WSL2 first if not present
wsl --install

# Then inside WSL2 terminal
npm install -g @openai/codex
```

For native PowerShell without WSL2:

```powershell
npm install -g @openai/codex
# Windows sandbox mode activates automatically — network calls are restricted
```

### Linux (npm or binary)

```bash
# npm path (requires Node.js 16+ per the published engines field)
npm install -g @openai/codex

# Binary path (no Node.js needed, ideal for CI)
curl -fsSL https://chatgpt.com/codex/install.sh | sh

# The installer pulls from releases.openai.com and falls back to GitHub Releases.
# To take an archive by hand, use e.g. codex-x86_64-unknown-linux-musl.tar.gz
# from github.com/openai/codex/releases/latest; the archive holds one binary.
```

---

## First Run: Authentication and Quick Start

Setting up Codex CLI authentication takes one command. Codex supports two auth paths: ChatGPT account login (browser OAuth flow) and direct API key injection. The ChatGPT account path is easier for individuals — it reuses your existing subscription and grants access to the latest Codex-specific model. The API key path is mandatory for CI/CD pipelines, team environments, and any context where a browser flow is unavailable. Once authenticated, Codex stores credentials in `~/.codex/auth.json` and reuses them across sessions. You do not need to re-authenticate per project; the credential is global. For teams, the recommended approach is injecting `OPENAI_API_KEY` as an environment variable to avoid credential files in shared environments. Codex is included in the Plus, Pro, Business, Edu and Enterprise ChatGPT plans; API-key users are billed per token at standard rates. After authentication, the recommended first action is running `codex "describe the architecture of this project"` on an existing codebase — this confirms connectivity and gives you a quick mental model of how Codex interprets your code before you ask it to change anything.

### Authenticating via ChatGPT Account

```bash
codex login
# Opens browser — approve in ChatGPT, token saved automatically
```

### Authenticating via API Key

```bash
export OPENAI_API_KEY="sk-..."
# Or add to your shell profile (~/.zshrc or ~/.bashrc)
echo 'export OPENAI_API_KEY="sk-..."' >> ~/.zshrc
```

### Your First Task

```bash
cd my-project
codex "add a JSON serialization function to utils.ts and write unit tests"
```

Codex reads the repository, proposes a plan, and (depending on your approval mode) either shows a diff for review or executes directly. The output includes changed files, test results, and a summary of what was done.

---

## The Two Knobs: Approval Policy and Sandbox Mode

Codex CLI does not expose one "autonomy level" setting. It exposes two independent flags, and the pair is what determines how much the agent can do without you. From the installed `codex-cli 0.170.0` help output on 18 November 2026:

- `-a, --ask-for-approval <APPROVAL_POLICY>` — when the model must ask before executing a command. The flag accepts exactly two values: `on-request` ("the model decides when to ask the user for approval") and `never` ("never ask for user approval; execution failures are immediately returned to the model"). `codex -a untrusted` fails argument parsing with `possible values: on-request, never`, and the upstream configuration reference states that `untrusted` is unsupported. The Rust enum behind the setting still has an `UnlessTrusted` variant, but the CLI flag does not expose it.
- `-s, --sandbox <SANDBOX_MODE>` — the filesystem policy for model-generated shell commands, with the values `read-only`, `workspace-write` and `danger-full-access`.

This is the correction most guides still get wrong, including earlier revisions of this page: there is no `--approval-mode suggest|auto-edit|full-auto` flag in the current CLI. If you are following a tutorial that uses one, it predates the current flag set. The vocabulary that survives is the *combination*: autonomous runs are `--sandbox workspace-write` with `--approve-for-me`, which routes approval requests through automatic review inside that sandbox rather than prompting you.

### Setting the Policy

```bash
# Conservative: read-only sandbox, ask when the model requests it
codex -a on-request -s read-only "refactor auth module"

# Day-to-day: writable workspace, model decides when to ask
codex -a on-request -s workspace-write "migrate all useState hooks to useReducer"

# Unattended: writable workspace, approvals routed to automatic review
codex -s workspace-write --approve-for-me "run all tests, fix failures, commit"
```

The two flags are also settable through `-c key=value` overrides, which is how you pin them in CI without editing a config file:

```bash
codex -c approval_policy="never" -s workspace-write "run the test suite and fix failures"
```

Do not reach for `--dangerously-bypass-approvals-and-sandbox` to make an unattended run work. Its own help text calls it "EXTREMELY DANGEROUS" and says it is intended solely for environments that are already sandboxed from the outside — and, as the mechanics section below shows, bypassing the sandbox changes the meaning of the approval decision rather than removing it.

### When to Use Which Pair

| Combination | File Writes | Shell Commands | Recommended For |
|---|---|---|---|
| `-a on-request -s read-only` | Needs approval | Read-only, asks on request | Unfamiliar repos, production hotfixes |
| `-a on-request -s workspace-write` | Inside workspace | Asks when the model requests | Active feature branches, refactors |
| `-s workspace-write --approve-for-me` | Inside workspace | Auto-reviewed in sandbox | CI/CD pipelines, isolated sandboxes |

---

## What Codex CLI Actually Sends When It Edits a File

Codex CLI does not send a unified diff. When the model edits a file it emits a line-delimited text envelope, and a dedicated crate parses that envelope into hunks before anything touches the filesystem. The grammar is published as a doc comment at the top of [`codex-rs/apply-patch/src/parser.rs`](https://raw.githubusercontent.com/openai/codex/cc7a62e19cb4703495e3a6d01e1af076e8223833/codex-rs/apply-patch/src/parser.rs) at the pinned commit, quoted here verbatim:

```text
start: begin_patch environment_id? hunk+ end_patch
begin_patch: "*** Begin Patch" LF
environment_id: "*** Environment ID: " filename LF
end_patch: "*** End Patch" LF?
hunk: add_hunk | delete_hunk | update_hunk
add_hunk: "*** Add File: " filename LF add_line+
delete_hunk: "*** Delete File: " filename LF
update_hunk: "*** Update File: " filename LF change_move? change?
filename: /(.+)/
add_line: "+" /(.+)/ LF -> line
change_move: "*** Move to: " filename LF
change: (change_context | change_line)+ eof_line?
change_context: ("@@" | "@@ " /(.+)/) LF
change_line: ("+" | "-" | " ") /(.+)/ LF
eof_line: "*** End of File" LF
```

Three things this settles that a reader usually has to guess at:

1. **It is not a diff.** There are no `---`/`+++` file headers, no `diff --git`, no line numbers. The target file is named once, by the `*** Update File: ` marker, and located by the context lines inside the hunk.
2. **The grammar requires a hunk; the parser does not enforce that.** `hunk+` in the `start` rule means a conforming payload carries at least one file operation. The Rust parser is laxer than the grammar it documents: boundary checking compares only the first and last line, and [`StreamingPatchParser::finish`](https://raw.githubusercontent.com/openai/codex/cc7a62e19cb4703495e3a6d01e1af076e8223833/codex-rs/apply-patch/src/streaming_parser.rs) returns whatever hunks it collected, so a bare `*** Begin Patch` / `*** End Patch` pair parses to zero hunks. The empty action is stopped one layer down — `assess_patch_safety()` rejects it with the reason `empty patch` before any path check runs.
3. **The markers are literal strings with a trailing space.** `*** Add File: `, `*** Update File: ` and `*** Move to: ` are string constants in the same file; drop the space after the colon and the line stops matching the marker.

Two markers are easy to miss because third-party guides rarely quote them. `*** Environment ID: <id>` attaches an optional identifier to the parsed argument struct, and `*** End of File` marks a change anchored at the end of the file — the `eof_line?` slot at the tail of the `change` rule. The parser stores those values; it does not translate them into a diff on disk.

### The two errors the parser returns, and why they are exact strings

Parsing does not check applicability. The module comment is explicit that the parser only validates shape — "It does not attempt to actually check that the patch can be applied to the filesystem" — so a syntactically valid payload can still fail when the change is applied. Application lives in the sibling modules (`file_update`, `seek_sequence`) re-exported from [`codex-rs/apply-patch/src/lib.rs`](https://raw.githubusercontent.com/openai/codex/cc7a62e19cb4703495e3a6d01e1af076e8223833/codex-rs/apply-patch/src/lib.rs).

Boundary checking in strict mode is a comparison against the two marker constants, after trimming whitespace on the first and last lines. There are exactly two failure messages, and they are asserted in the module's own tests:

- `The first line of the patch must be '*** Begin Patch'`
- `The last line of the patch must be '*** End Patch'`

Because the comparison happens on trimmed lines, a trailing space after `*** Begin Patch` still parses in strict mode — one of the module's tests relies on that. The module comment describes the parser as "a little more lenient than the explicit spec". Lenient mode adds a second acceptance path: a payload wrapped in a `<<'EOF'` … `EOF` heredoc is unwrapped first, then the inner lines face the same strict boundary check. That is why a transcript showing ``apply_patch <<'EOF'`` followed by a patch body is the same tool with a shell wrapper, not a different format.

## Where the Approval Decision Happens

Approval is not a property of the patch text. It is computed from the patch's target paths plus the session's approval policy and permission profile, in `assess_patch_safety()` in [`codex-rs/core/src/safety.rs`](https://raw.githubusercontent.com/openai/codex/cc7a62e19cb4703495e3a6d01e1af076e8223833/codex-rs/core/src/safety.rs). The function is short enough to state as a decision table:

| Condition, evaluated in order | Result |
|---|---|
| The patch has no file changes | `Reject` with reason `empty patch` |
| Approval policy is `UnlessTrusted` | `AskUser`, before any path check |
| Every target path is writable, and the permission profile is disabled/external or a platform sandbox is available | `AutoApprove` |
| Paths are not all writable, and the policy is `Never` (or `Granular` with sandbox approval off) | `Reject` |
| Anything else | `AskUser` |

The two rejection strings are fixed text: `writing outside of the project; rejected by user approval settings`, and `writing is blocked by read-only sandbox; rejected by user approval settings` for a managed profile with no writable roots. Note what the third row is doing: `AutoApprove` skips the prompt, and it does so for two different reasons. The condition is a conjunction — the patch is constrained to writable paths, and then either a platform sandbox is available or the permission profile is `Disabled` or `External`. In the sandbox branch the code comment explains the reasoning: a path inside the writable set can still be a hard link to something outside it, so the patch is assumed to run in a sandbox. The comment's next line names the other branch outright — "Disabled and External profiles intentionally do not apply an outer sandbox" — so under those two profiles a patch can be auto-approved with no outer sandbox at all. (The path check itself short-circuits to true when the configured policy grants full-disk write access, since no per-path writable-root test can constrain that any further.)

[`codex-rs/core/src/apply_patch.rs`](https://raw.githubusercontent.com/openai/codex/cc7a62e19cb4703495e3a6d01e1af076e8223833/codex-rs/core/src/apply_patch.rs) then maps those three outcomes onto the tool runtime:

- `AutoApprove` becomes `ExecApprovalRequirement::Skip { bypass_sandbox: false }` — the approval prompt is skipped and the patch is not flagged to bypass the sandbox. Whether an outer sandbox exists at all is decided by the permission profile, per the `Disabled`/`External` branch above.
- `AskUser` becomes `ExecApprovalRequirement::NeedsApproval`, delegated to the tool runtime "including cached approvals", so an earlier yes to the same shape of change can carry forward within the session.
- `Reject` becomes a `FunctionCallError::RespondToModel` whose message is `patch rejected: <reason>`.

That last mapping has a practical consequence: a rejection is returned to the model as an error it can read, not a hard session failure. A model that reads `patch rejected: writing outside of the project` may respond by proposing a different path — which is a retry you did not ask for, not a crash.

### Which mode name maps to which policy

The policy type in the safety check is `AskForApproval`, and the configuration reference documents three values for `approval_policy`: `on-request`, `never`, and the struct form `{ granular = { ... } }`. The enum in `safety.rs` carries two further variants, `UnlessTrusted` and `Granular`, that the documented values do not reach through the `-a` flag; treat any other mode name you see in a tutorial as a pre-rename convention. What the source does establish is the boundary case worth remembering: `UnlessTrusted` asks before the writable-path check runs at all, while `Never` and `Granular` fall through to it — and `Never` rejects rather than asking when the paths fail the check.

## What the Model Is Told About apply_patch

The tool description is not a mandate. The instruction the model reads is per-model prompt text, and at the pinned commit the `gpt-5.2-codex` prompt file ([`codex-rs/core/gpt-5.2-codex_prompt.md`](https://raw.githubusercontent.com/openai/codex/cc7a62e19cb4703495e3a6d01e1af076e8223833/codex-rs/core/gpt-5.2-codex_prompt.md)) says:

> Try to use apply_patch for single file edits, but it is fine to explore other options to make the edit if it does not work well. Do not use apply_patch for changes that are auto-generated (i.e. generating package.json or running a lint or format command like gofmt) or when scripting is more efficient (such as search and replacing a string across a codebase).

Two carve-outs follow from that sentence, and they change how you should review a Codex session. First, a formatter, a codegen step or a `gofmt` run will not arrive as a patch — it arrives as a shell command. Second, a mechanical rename across many files is explicitly pointed at scripting rather than at the patch tool. So a review process that only inspects `*** Begin Patch` blocks is inspecting a subset of the edits, not all of them.

The prompt is also revision-specific. Prompt files are per-model artefacts inside the repository, and they change between releases; the quote above records the `gpt-5.2-codex` file at commit `cc7a62e19cb4703495e3a6d01e1af076e8223833` on 18 November 2026, not a stable product contract across models.

## Reading a Payload Line by Line

The installed CLI in this environment is `codex-cli 0.170.0`, and it exposes no public `apply-patch` subcommand — the internal entry point is gated behind the `--codex-run-as-apply-patch` argv flag defined in the crate, and invoking it against a piped fixture exits with `stdin is not a terminal`. So the payload below is a hand-built illustration of the grammar, not a recorded run. Read it against the rules above:

```text
*** Begin Patch
*** Update File: src/config.py
@@ def load_config(path):
 import json
-    return json.loads(path.read_text())
+    return json.loads(Path(path).read_text())
*** End Patch
```

What the parser does with each line: `*** Begin Patch` opens the envelope; `*** Update File: src/config.py` names the single target file; `@@ def load_config(path):` is a context anchor whose tail is a free-form hint, used to help locate the region in the file; the line beginning with one space is unchanged context; `-` is removed text; `+` is added text; `*** End Patch` closes the envelope. There is no line numbering and no hunk header count — the `@@` line carries a label, not a `-1,7 +1,7` range.

This is also where a common misreading dies. Because the payload looks diff-like, people assume the numbers or the anchor line are authoritative. In this grammar the anchor is a hint and the surrounding context lines are the actual match material, which is why an update hunk that renames an import can still land on the wrong function if the context you supplied is generic.

## Practical Consequences for Reviewers and CI

If you audit agent sessions, the envelope gives you cheap, reliable markers:

```bash
# Count file-edit tool calls in a captured session log
grep -c '^\*\*\* Begin Patch' session.log

# List every path a turn tried to modify, without parsing diffs
grep -E '^\*\*\* (Add|Update|Delete) File: |^\*\*\* Move to: ' session.log
```

Four operational points follow from the source read above:

- **Audit by resolved path, not by diff shape.** The tool names files explicitly, so the question "what could this turn write?" is answerable from the markers. For a `*** Move to: ` hunk, both the source and destination paths are checked against the writable set, which is why renames deserve a second look rather than being treated as in-place edits.
- **Do not treat an absent prompt as an absent sandbox — or as a present one.** `AutoApprove` is taken for two reasons: a sandbox will run the patch, or the permission profile is `Disabled`/`External`, which by design applies no outer sandbox. The skipped thing is the prompt. In the second case the hard-link caveat the code comment raises has no outer sandbox behind it, so the path check that approved the patch is the only gate the write passed. If you changed the profile to get a patch through, you also changed the meaning of the approval you saw.
- **Separate syntactic rejection from policy rejection.** `The first line of the patch must be '*** Begin Patch'` and `empty patch` are model-side formatting failures. `patch rejected: ...` is a policy outcome. They belong in different alert channels, because only the second one is a permissions question.
- **Read the prompt file for the model you actually run.** The carve-outs that push edits into shell commands live in the per-model prompt, not in the CLI, so the same session can behave differently after a model switch without any configuration change on your side.

None of the above requires running the tool. It requires reading one grammar comment, two boundary tests, one safety function and one prompt file at a known commit — which is also the honest limit of this section: the mechanics are quoted from source, and no patch was executed in this environment.

---

## AGENTS.md — How to Configure Codex for Your Project

AGENTS.md is an open standard file that tells AI coding agents — including Codex CLI, Claude Code, and compatible third-party tools — how to work in your specific project. It lives at the root of your repository and is automatically read by Codex on every invocation, functioning like a persistent system prompt scoped to your codebase. An effective AGENTS.md eliminates the need to repeat project-specific context in every command: your test commands, coding conventions, forbidden patterns, branch naming rules, and environment setup instructions belong here. In April 2026, AGENTS.md is increasingly treated as a first-class project artifact, often committed alongside `package.json` and `.eslintrc`. Think of it as documentation that your AI teammates read before touching a single file — the more specific and opinionated, the better the output quality.

### Example AGENTS.md

```markdown
# Project: Payments API

## Setup
- Node.js 20 LTS
- Run `npm install` before tasks
- Copy `.env.example` to `.env` and fill values for local DB

## Testing
- Unit tests: `npm test`
- Integration tests: `npm run test:int` (requires Docker)
- Always run unit tests before committing

## Conventions
- TypeScript strict mode — no `any` types
- Use named exports only — no default exports
- Prefer `zod` for runtime validation, not manual type guards

## Forbidden
- Never commit secrets or API keys
- Do not modify `src/migrations/` directly — use the CLI
- Do not add `console.log` to production code

## Branch Naming
- Features: `feat/TICKET-description`
- Fixes: `fix/TICKET-description`
```

### What to Include vs. Omit

| Include | Omit |
|---|---|
| Test commands and flags | Obvious conventions (use TypeScript → TS project) |
| Forbidden directories/patterns | Generic best practices |
| Environment setup steps | Framework documentation links |
| Project-specific naming conventions | Personal preferences |

---

## MCP Integration: Connecting Third-Party Tools to Codex

Model Context Protocol (MCP) integration transforms Codex CLI from a file editor into a full-stack development assistant with access to live external systems. MCP is an open standard that lets AI agents call external tools — browsers, databases, APIs, design tools — via a consistent interface. With MCP configured, Codex can read the documentation of a library it needs to use, query your database schema before writing a migration, or read design specs before scaffolding a UI component. The integration requires adding server definitions to `~/.codex/config.toml` — Codex handles the protocol negotiation automatically. Each MCP server runs as a subprocess managed by Codex, so you get isolated, per-session tool access without any persistent background service. Credentials are passed via environment variables rather than stored in config files, keeping secrets out of your repository.

### Configuring MCP Servers

```toml
# ~/.codex/config.toml

[mcp_servers.postgres]
command = "npx"
args = ["-y", "@modelcontextprotocol/server-postgres"]
env = { DATABASE_URL = "${DATABASE_URL}" }

[mcp_servers.github]
command = "npx"
args = ["-y", "@modelcontextprotocol/server-github"]
env = { GITHUB_TOKEN = "${GITHUB_TOKEN}" }

[mcp_servers.figma]
command = "npx"
args = ["-y", "@modelcontextprotocol/server-figma"]
env = { FIGMA_TOKEN = "${FIGMA_TOKEN}" }
```

### Practical MCP Use Cases

**Database-aware migrations:**
```bash
codex "analyze the users table schema and write a safe migration to add an email_verified column"
# Codex queries the live DB schema via MCP before writing migration code
```

**Design-to-code:**
```bash
codex "implement the LoginForm component from the Figma frame at [frame-url]"
# Codex reads actual design specs, not a screenshot
```

**GitHub-integrated workflow:**
```bash
codex "open a PR for the feature branch, link it to issue #142"
# Codex uses GitHub MCP to create the PR directly
```

---

## Advanced Configuration: Sandbox, Approval Policies, and config.toml

Advanced Codex CLI configuration via `~/.codex/config.toml` gives you fine-grained control over sandbox behavior, filesystem access policies, network restrictions, and per-project overrides. The sandbox system is one of Codex CLI's most important safety features — it limits what the agent can touch beyond the paths you explicitly whitelist, preventing runaway automation from modifying system files or making unintended network calls. The sandbox is enforced at the process level, and the same policy objects feed the patch-approval check described in the mechanics section above. For teams deploying Codex in CI, sandbox configuration is not optional — it is the primary safeguard ensuring agents operate within the intended blast radius. You can also use `CODEX_HOME` to maintain project-specific config profiles without modifying your global settings. Config keys are hot-reloaded between Codex sessions, so changes take effect immediately without reinstalling the CLI. Granular approval is expressed on `approval_policy` itself — `approval_policy = { granular = { ... } }` with per-category booleans (`sandbox_approval`, `rules`, `mcp_elicitations`, `request_permissions`, `skill_approval`) — not as a separate `[approval_policies]` table.

### config.toml Reference (keys the upstream reference documents)

The keys below are the ones the [configuration reference](https://developers.openai.com/codex/config-file/config-reference) documents, read on 18 November 2026. An earlier revision of this page printed a `[defaults]` table with `context_window`, a `[sandbox]` table with `allow_read` / `allow_write` / `allow_network` / `deny_write`, and an `[approval_policies]` table with per-operation modes. None of those keys exists in that reference, so they are removed rather than restated.

```toml
# ~/.codex/config.toml
model = "gpt-5.2-codex"
approval_policy = "on-request"          # on-request | never | { granular = { ... } }
model_context_window = 128000           # optional per-model override

# Sandbox policy for model-generated shell commands
sandbox_mode = "workspace-write"        # read-only | workspace-write | danger-full-access

[sandbox_workspace_write]
# Extra writable roots beyond the workspace directory
writable_roots = ["/home/me/projects/shared"]
# Keep network access off inside the sandbox
network_access = false
```

### Per-Project Config via CODEX_HOME

```bash
# Use a project-specific config profile
export CODEX_HOME=~/projects/payments-api/.codex

# codex now reads ~/.../payments-api/.codex/config.toml
codex "add rate limiting to the auth endpoints"
```

---

## Multi-Agent Workflows with the OpenAI Agents SDK

Orchestrating Codex CLI as part of a multi-agent system via the OpenAI Agents SDK enables production-scale automation workflows that go far beyond what a single interactive session can accomplish. In a multi-agent setup, a coordinator agent breaks down a high-level goal (e.g., "ship this feature") into subtasks, spawns specialized Codex agents for each, collects outputs, runs validation, and gates the final commit behind automated checks. This architecture is increasingly common for CI/CD pipelines where agents handle the full loop: branch → implement → test → review → PR. The Agents SDK provides typed Python and TypeScript interfaces for spawning, monitoring, and composing agents, with support for handoffs, guardrails and tracing. The example below is a sketch of the pattern, not a runnable integration: the `agents.CodexTool` and `Pipeline` surface shown here is illustrative, and the current SDK reference should be checked before wiring it into a pipeline.

### Example: Automated Bug Fix Pipeline

```python
from openai import agents

coordinator = agents.Agent(
    name="BugFixCoordinator",
    instructions="Break down bug reports into implementation tasks and delegate to Codex agents",
    tools=[agents.CodexTool(approval_mode="full-auto", sandbox=True)]
)

pipeline = agents.Pipeline([
    agents.Step("triage", coordinator),
    agents.Step("implement", agents.CodexAgent(task="fix the bug described in the issue")),
    agents.Step("test", agents.CodexAgent(task="run tests and fix any failures")),
    agents.Step("review", agents.CodeReviewAgent()),
    agents.Step("pr", agents.GitHubAgent(action="create_pr"))
])

result = pipeline.run(input="Fix bug #442: login form resets on validation error")
```

### Slash Commands in Interactive Mode

When running Codex interactively, slash commands switch context without leaving the session. The enum in [`codex-rs/tui/src/slash_command.rs`](https://raw.githubusercontent.com/openai/codex/cc7a62e19cb4703495e3a6d01e1af076e8223833/codex-rs/tui/src/slash_command.rs) at the pinned commit declares 66 variants; the table below is a selection of eleven commonly used ones, not the enum itself. Every description quoted in it is the string that file's `description()` method returns for that variant:

| Command | Action (source string) |
|---|---|
| `/model` | "choose what model and reasoning effort to use" — opens a picker, takes no model argument |
| `/permissions` | "choose what Codex is allowed to do" |
| `/diff` | "show git diff (including untracked files)" |
| `/status` | "show current session configuration and token usage" |
| `/plan` | "switch to Plan mode" |
| `/review` | "review my current changes and find issues" |
| `/new` | "start a new chat during a conversation" |
| `/compact` | "summarize conversation to prevent hitting the context limit" |
| `/init` | "create an AGENTS.md file with instructions for Codex" |
| `/mcp` | `list MCP tools; /mcp verbose or /mcp login <name> [--environment <id>]` |
| `/quit` | "exit Codex" |

An earlier revision of this page listed `/approval`, `/context`, `/commit` and `/reset`. None of those four names exists among the enum's 66 variants, so they are removed instead of re-caveated.

---

## Codex CLI vs Claude Code: How to Use Both Effectively

Codex CLI and Claude Code are complementary tools that solve different parts of the AI-assisted development workflow, not direct competitors you must choose between. Codex CLI excels at autonomous, task-scoped operations: "implement this feature," "fix these failing tests," "migrate this API to the new schema." It operates in a fire-and-review model where you define a goal and let the agent work. Claude Code, by contrast, excels at interactive, exploratory sessions: understanding an unfamiliar codebase, debugging complex multi-service interactions, or pair-programming through a nuanced architectural decision. The key practical difference is conversational depth versus autonomous execution depth: one tool is built to hold a long investigation open, the other to finish a scoped task. They overlap on project instructions — Codex reads `AGENTS.md`, Claude Code reads `CLAUDE.md` — so keeping conventions in a file each tool reads avoids maintaining two setups.

### Side-by-Side Comparison

| Dimension | Codex CLI | Claude Code |
|---|---|---|
| Primary mode | Autonomous execution | Interactive conversation |
| Ideal for | Feature implementation, test fixes, migrations | Codebase exploration, debugging, architecture |
| Context window | Set by the selected model | Set by the selected model |
| Approval model | `-a` policy + `-s` sandbox flags | Explicit approval per tool call |
| MCP support | Yes (config.toml) | Yes (settings.json) |
| CI/CD integration | Native via `--approve-for-me` + sandbox | Via headless mode |
| AGENTS.md support | Yes (primary format) | Yes (CLAUDE.md alias) |

### Recommended Split Workflow

```bash
# Phase 1: Understand with Claude Code
claude "explain how the payment processing pipeline works and identify potential race conditions"

# Phase 2: Implement with Codex CLI
codex -a on-request -s workspace-write "add distributed locking to prevent the race condition in payment processing"

# Phase 3: Review with Claude Code
claude "review the changes in the last commit — do they fully address the race condition?"

# Phase 4: Ship with Codex CLI
codex -s workspace-write --approve-for-me "run integration tests, fix any failures, open a PR"
```

---

## Real Developer Workflow: Branch → Code → Review → Commit

A complete real-world Codex CLI workflow starts with a feature branch and ends with a reviewed, tested commit — the agent handles every step between those bookends. This workflow pattern takes advantage of Codex CLI's AGENTS.md awareness (no repeated context), its MCP integration (live database schema, GitHub API), and its two-knob approval setup (a read-only sandbox for sensitive changes, `--approve-for-me` for mechanical tasks). The key practice that experienced Codex users consistently recommend: always start a new git branch before invoking Codex with a writable sandbox. This ensures that every agent-made change is isolated, reviewable as a diff, and reversible with a single `git checkout main`. Teams that skip this step report harder-to-audit histories; teams that adopt it report higher confidence in merging agent-generated code.

### Step-by-Step: Feature Implementation

```bash
# 1. Start from a clean branch
git checkout -b feat/PROJ-442-add-2fa

# 2. Run Codex with a writable sandbox and on-request approvals
codex -a on-request -s workspace-write \
  "implement TOTP-based 2FA for the auth module. Use speakeasy library.
   Add unit tests. Follow the conventions in AGENTS.md."

# 3. Review the diff
git diff

# 4. Run tests manually or let Codex do it
codex "run tests and summarize results"

# 5. Approve the changes and commit
git add -p   # Review each hunk
git commit -m "feat(auth): add TOTP-based 2FA via speakeasy"

# 6. Push and open PR (optionally via Codex + GitHub MCP)
codex -s workspace-write --approve-for-me "push this branch and open a PR linking to PROJ-442"
```


## FAQ

**Q: Do I need an OpenAI API key to use Codex CLI?**

No — you can authenticate via your existing ChatGPT account using `codex login`, which opens a browser OAuth flow. An API key is required only for CI/CD pipelines, team environments, or contexts where a browser flow is unavailable. Codex is included in the Plus, Pro, Business, Edu and Enterprise ChatGPT plans; API key usage is billed per token.

**Q: How does Codex CLI handle large codebases with millions of lines?**

Codex CLI uses intelligent context selection rather than loading the entire codebase into the context window. It reads project structure, locates relevant files via semantic search and file tree analysis, and loads only the files pertinent to the current task — typically staying well inside the selected model's context window. You can supplement this with `AGENTS.md` to explicitly point Codex at critical files or directories.

**Q: Is it safe to run Codex with approvals turned off on production code?**

Only with sandbox restrictions configured. With approvals disabled (`-a never`) and a writable sandbox, the agent can modify any file the process can reach. The recommended practice is `sandbox_mode = "workspace-write"` with a `[sandbox_workspace_write]` `writable_roots` list in `config.toml` to bound where writes can land, and always run auto-approved sessions on a git branch — never directly on `main`. For CI/CD use, keep the workspace-write sandbox and add container isolation for defence in depth.

**Q: Can Codex CLI work offline?**

No. The binary runs locally, but model inference happens on OpenAI's servers, so the CLI needs network access to the inference API. Nothing in this guide covers an air-gapped deployment path.

**Q: How does AGENTS.md differ from a `.cursorrules` or `CLAUDE.md` file?**

AGENTS.md is the open standard proposed by OpenAI to unify AI agent configuration across tools. CLAUDE.md (used by Claude Code) and `.cursorrules` (used by Cursor) are tool-specific variants with similar purposes. Codex CLI reads `AGENTS.md` natively; Claude Code reads both `CLAUDE.md` and `AGENTS.md`. Writing your conventions in `AGENTS.md` maximizes compatibility across AI coding tools without duplicating configuration.