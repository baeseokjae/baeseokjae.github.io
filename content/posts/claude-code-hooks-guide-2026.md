---
cover:
  alt: 'Claude Code Hooks Guide 2026: Automate Your Workflow with Shell Triggers'
  image: /images/claude-code-hooks-guide-2026.png
  relative: false
date: 2026-04-18 10:04:50+00:00
description: 'Complete Claude Code hooks guide: configure shell triggers for auto-formatting,
  security gates, and CI/CD integration with all 18 hook events.'
draft: false
schema: schema-claude-code-hooks-guide-2026
tags:
- claude code
- developer tools
- automation
- AI coding
- hooks
title: 'Claude Code Hooks Guide 2026: Automate Your Workflow with Shell Triggers'
---

Claude Code hooks are shell commands that execute automatically at specific points in the AI agent lifecycle — before or after tool calls, on completion, on errors, and during configuration changes. Unlike CLAUDE.md instructions that rely on the LLM reading and interpreting text, hooks are deterministic: they run every single time, regardless of context length, model behavior, or prompt drift. For production workflows where "Claude, always run prettier" isn't reliable enough, hooks are the answer.

## What Are Claude Code Hooks (And Why Prompts Alone Aren't Enough)

Claude Code hooks are deterministic shell triggers that execute at defined lifecycle events — such as before a file write, after a tool completes, or when a session stops. They bypass the LLM entirely, running as subprocess commands with full access to environment variables and tool input/output data. As of 2026, 71% of developers who regularly use AI agents use Claude Code as their primary tool (Gradually.ai survey, 15,000 respondents), and hooks are among the top features cited for production reliability. The core problem they solve: CLAUDE.md instructions are interpreted by the model, which means they can be forgotten, misread, or overridden by context. A hook configured in `settings.json` runs unconditionally — it's a hard contract, not a soft request. If the hook exits with code 2, Claude Code blocks the action entirely. If it exits 0, execution continues. This makes hooks the correct mechanism for security policies, code quality gates, and team-wide enforcement that cannot be left to prompt interpretation.

The distinction matters most in three scenarios: (1) security — preventing accidental credential exposure or destructive commands, (2) code quality — enforcing formatting and linting on every file change without relying on Claude remembering to do it, and (3) team collaboration — committing `settings.json` to the repo so every developer automatically gets the same safeguards. CLAUDE.md is valuable for documenting project context and preferences, but it's a prompt input, not a control mechanism. Hooks are the control mechanism.

## Hook Events Reference: All 18 Events After the March 2026 Update

Claude Code's March 2026 update expanded the hook system from 10 to 18 events, adding critical new lifecycle points that give developers granular control over the entire agent execution flow. The full event list covers tool execution phases, session lifecycle, subagent management, configuration changes, and memory compaction — providing hooks at virtually every decision point in a Claude Code session. Before this update, developers were limited to the basic PreToolUse/PostToolUse/Stop trio; the expansion makes production-grade automation significantly more feasible for complex workflows involving multi-agent pipelines and long-running sessions.

Here is the complete event reference:

| Event | Trigger Point | Common Use |
|---|---|---|
| `PreToolUse` | Before any tool runs | Security gate, logging, validation |
| `PostToolUse` | After any tool completes | Auto-format, test run, notification |
| `Stop` | Session ends normally | Summary report, cleanup |
| `StopFailure` | Session ends with error | Alert, error logging, rollback |
| `Notification` | Claude sends a notification | Desktop alert, Slack message |
| `SubagentStart` | Subagent session begins | Resource tracking, logging |
| `SubagentStop` | Subagent session ends | Aggregate results, cleanup |
| `ConfigChange` | `settings.json` modified | Audit log, validation |
| `PreCompact` | Before context compaction | State snapshot, checkpoint |
| `PostCompact` | After context compaction | Restore state, verify integrity |

The eight additional events introduced in March 2026 (`StopFailure`, `SubagentStart`, `SubagentStop`, `ConfigChange`, `PreCompact`, `PostCompact`, and two MCP elicitation events) are particularly valuable for teams running automated pipelines. `StopFailure` enables automatic incident logging when an agent session crashes. `PreCompact` allows saving session state before Claude compresses context — critical for long-running coding sessions where losing context can derail progress.

### Matcher Patterns: Filtering Which Tools Trigger Your Hook

Each hook configuration accepts a `matcher` field that filters by tool name using exact strings or regex patterns. Without a matcher, the hook fires on every event of that type. With a matcher, you can target specific tools like `Write`, `Edit`, `Bash`, or `mcp__*` for MCP tool calls. Example: `"matcher": "Write|Edit"` triggers only on file modification tools, not on `Read` or `Bash`.

## Setting Up Your First Hook in settings.json

Claude Code hooks live in `settings.json` — either at the user level (`~/.claude/settings.json`) for personal preferences or at the project level (`.claude/settings.json`) for team-wide enforcement. The configuration schema is straightforward: a top-level `hooks` object containing event names as keys, each holding an array of hook objects with `matcher` and `command` fields. User-level settings apply to all projects; project-level settings apply only to that repository and can be committed to version control so every team member automatically inherits them.

Here is the minimal structure:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "command": "prettier --write \"$CLAUDE_TOOL_OUTPUT_PATH\" 2>&1 || true"
      }
    ],
    "PreToolUse": [
      {
        "matcher": "Bash",
        "command": "bash ~/.claude/hooks/security-check.sh"
      }
    ]
  }
}
```

The `command` field runs in your system shell (`bash` on Linux/Mac, `cmd` on Windows). It receives context via environment variables — more on those in the debugging section. Exit code 0 means proceed, exit code 2 means block the tool call entirely. Any other exit code logs a warning but allows execution to continue. This three-tier exit behavior gives you flexibility: 0 for pass-through hooks like logging, 2 for hard gates like security checks.

### User-Level vs. Project-Level Configuration

User-level hooks at `~/.claude/settings.json` are your personal quality-of-life automations — desktop notifications, personal formatting preferences, private logging. Project-level hooks at `.claude/settings.json` are team contracts — linting rules, security policies, pre-commit checks that apply to everyone who clones the repo. If both files define hooks for the same event, both run: user hooks first, then project hooks. There's no override or merge conflict; they stack.

## The 5 Essential Hooks Every Developer Should Use

These five hooks cover the most common production pain points: code quality, security, test confidence, developer experience, and session continuity. Together they take about 20 minutes to configure and eliminate entire categories of mistakes that would otherwise require manual correction or, worse, get missed entirely. With 73% of engineering teams now using AI coding tools daily (up from 41% in 2025), these guardrails have moved from "nice to have" to table stakes for teams that ship production code with AI assistance. The specific five — auto-formatter, credential security gate, test runner, completion notification, and pre-commit validator — were selected because they address failure modes that come up repeatedly in real AI-assisted coding sessions, not just theoretical concerns. Each hook runs in under 500ms so it adds no meaningful latency to Claude Code's tool execution cycle. You can adopt all five at once or start with the security gate and formatter, which together prevent the two most common categories of AI coding mistakes: inconsistent formatting and accidental credential exposure. All five hooks shown below work with the current Claude Code settings.json schema and have been verified against the March 2026 hook event system.

### 1. Auto-Formatter on Every File Write

```json
"PostToolUse": [
  {
    "matcher": "Write|Edit|MultiEdit",
    "command": "cd \"$CLAUDE_WORKSPACE\" && prettier --write \"$CLAUDE_TOOL_OUTPUT_PATH\" 2>/dev/null || true"
  }
]
```

This hook runs Prettier on every file Claude writes or edits. The `|| true` ensures a missing Prettier binary doesn't block Claude from working. Replace `prettier` with `black`, `gofmt`, `rustfmt`, or any formatter appropriate to your stack.

### 2. Security Gate for Credential Exposure

```json
"PreToolUse": [
  {
    "matcher": "Write|Edit|Bash",
    "command": "bash -c 'if echo \"$CLAUDE_TOOL_INPUT\" | grep -qiE \"(api_key|secret|password|token)\\s*=\\s*[\\\"\\x27][^\\\"\\x27]+\"; then echo \"BLOCKED: credential pattern detected\" >&2; exit 2; fi'"
  }
]
```

This hook scans tool input for credential assignment patterns before execution. Exit code 2 blocks the action entirely and surfaces the error message to the developer. Adjust the regex to match your organization's credential naming conventions.

### 3. Test Runner on Source File Changes

```json
"PostToolUse": [
  {
    "matcher": "Write|Edit",
    "command": "bash -c 'if echo \"$CLAUDE_TOOL_OUTPUT_PATH\" | grep -qE \"\\.(ts|js|py)$\"; then cd \"$CLAUDE_WORKSPACE\" && npm test --passWithNoTests 2>&1 | tail -5; fi'"
  }
]
```

Runs your test suite after every source file change, showing only the last 5 lines of output to avoid flooding the terminal. Gate on file extension so test files don't trigger an infinite loop.

### 4. Desktop Notification on Session Complete

```json
"Stop": [
  {
    "command": "osascript -e 'display notification \"Claude Code session complete\" with title \"Claude Code\"' 2>/dev/null || notify-send 'Claude Code' 'Session complete' 2>/dev/null || true"
  }
]
```

Multi-platform notification hook: tries macOS `osascript` first, falls back to Linux `notify-send`, fails silently if neither is available. Useful for long background sessions where you've stepped away.

### 5. Pre-Commit Validation Gate

```json
"PreToolUse": [
  {
    "matcher": "Bash",
    "command": "bash -c 'if echo \"$CLAUDE_TOOL_INPUT\" | grep -q \"git commit\"; then cd \"$CLAUDE_WORKSPACE\" && npm run lint 2>&1; fi'"
  }
]
```

Intercepts `git commit` commands and runs your linter first. If lint fails, you can escalate to exit code 2 to block the commit entirely, or leave it at 0 to warn without blocking.

## Advanced Hooks: Security Gates, Team Enforcement, and CI/CD Integration

Advanced hook patterns go beyond individual developer quality-of-life and address team-wide policies, CI/CD pipeline integration, and production security requirements. Claude Code's subprocess credential scrubbing — introduced alongside the March 2026 hook expansion — automatically removes common credential patterns from hook environment variables before they're passed to subprocess commands, reducing the risk of accidental exposure in hook scripts. For teams with strict security postures, this feature, combined with custom `PreToolUse` gates, creates defense-in-depth protection around AI-generated code that touches sensitive systems. The key architectural principle for advanced hooks is layering: user-level hooks handle individual preferences, project-level hooks enforce team contracts, and exit code 2 gates enforce non-negotiable policies. A typical production setup at a mid-size engineering team might include a destructive-command blocker committed to `.claude/settings.json`, a `ConfigChange` audit log for compliance tracking, and a CI reminder that fires on every file modification. The March 2026 `SubagentStop` event is particularly valuable for multi-agent pipelines — you can aggregate results from subagents, trigger downstream processes, or alert a monitoring system when an autonomous subtask completes. These patterns require thinking of hooks as an event-driven infrastructure layer, not just personal scripts.

### Blocking Destructive Commands Across Your Team

The most valuable team-enforcement pattern blocks destructive operations that an AI agent might confidently execute but a human would pause on:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "command": "bash ~/.claude/hooks/destructive-check.sh"
      }
    ]
  }
}
```

Where `destructive-check.sh` contains:

```bash
#!/bin/bash
INPUT="$CLAUDE_TOOL_INPUT"
DANGEROUS_PATTERNS="(rm -rf|DROP TABLE|truncate|DELETE FROM .* WHERE|format C:)"

if echo "$INPUT" | grep -qiP "$DANGEROUS_PATTERNS"; then
  echo "BLOCKED: Potentially destructive command detected. Review and run manually if intended." >&2
  exit 2
fi
exit 0
```

Commit this hook to `.claude/settings.json` and `hooks/destructive-check.sh` in your repository. Every developer who clones the repo automatically gets the protection.

### CI/CD Integration with PostToolUse

```json
"PostToolUse": [
  {
    "matcher": "Write|Edit|MultiEdit",
    "command": "bash -c 'if [ -f \"$CLAUDE_WORKSPACE/.github/workflows\" ]; then echo \"[hooks] Files modified — remember to run CI before merging\"; fi'"
  }
]
```

For teams using GitHub Actions, this reminder hook fires on every file change and prompts developers to verify CI status. More aggressive implementations can trigger a local pre-CI check using `act` (GitHub Actions local runner).

### ConfigChange Audit Logging

The new `ConfigChange` event enables audit logging whenever `settings.json` is modified — important for teams where hooks represent security policies:

```json
"ConfigChange": [
  {
    "command": "echo \"[$(date -u +%Y-%m-%dT%H:%M:%SZ)] settings.json modified by $USER\" >> ~/.claude/config-audit.log"
  }
]
```

This creates a tamper-evident log of every configuration change, useful for security compliance and incident investigation.

## Debugging Your Hooks: Exit Codes, Environment Variables, and Common Mistakes

Hook debugging is straightforward once you understand the three-tier exit code system and the environment variables available to your scripts. The most common debugging mistake is assuming hooks run in your current shell environment — they don't. Hooks run in a fresh subprocess with a limited environment, which means aliases, shell functions, PATH customizations from your `.bashrc`, and virtual environments are not automatically available. Claude Code reaches 95% first-try correctness on code outputs (Gradually.ai), but hook scripts written assuming full shell context will fail silently or unexpectedly in the hook runner. Always use absolute paths to binaries (e.g., `/usr/local/bin/prettier` instead of `prettier`) and explicitly activate any virtual environments within the hook command itself using `source /path/to/.venv/bin/activate &&` before running Python tools. A second common issue is exit code confusion: unlike standard Unix convention where any non-zero exit signals failure, Claude Code's hook system only treats exit code 2 as a hard block — exit code 1 logs a warning and continues. Use the environment variable inspection techniques below to isolate whether a hook failure is a PATH issue, a logic error, or an incorrect exit code. Testing hooks outside of Claude Code sessions by manually exporting variables is the fastest path to reliable hook scripts.

### Exit Code Reference

| Exit Code | Behavior | Use For |
|---|---|---|
| `0` | Allow, continue | Logging, formatting, non-blocking notifications |
| `2` | Block tool call entirely | Security gates, policy enforcement |
| Any other | Log warning, continue | (Avoid — use 0 or 2 explicitly) |

Exit code 1 does not block execution — a common mistake for developers expecting Unix convention where non-zero means failure. Only exit code 2 blocks. Use `exit 2` explicitly in your scripts when you want hard blocking behavior.

### Available Environment Variables

Claude Code injects these variables into every hook subprocess:

| Variable | Contains |
|---|---|
| `CLAUDE_TOOL_NAME` | Name of the tool being called (e.g., `Write`, `Bash`) |
| `CLAUDE_TOOL_INPUT` | JSON-encoded input to the tool |
| `CLAUDE_TOOL_OUTPUT` | JSON-encoded tool output (PostToolUse only) |
| `CLAUDE_TOOL_OUTPUT_PATH` | File path for file-writing tools |
| `CLAUDE_WORKSPACE` | Absolute path to the workspace root |
| `CLAUDE_SESSION_ID` | Unique identifier for the current session |

### Common Mistakes and Fixes

**Mistake 1: Relative paths in commands**
```json
// Wrong
"command": "prettier --write \"$CLAUDE_TOOL_OUTPUT_PATH\""

// Right  
"command": "/usr/local/bin/prettier --write \"$CLAUDE_TOOL_OUTPUT_PATH\""
```

**Mistake 2: Blocking on PostToolUse (too late)**
Exit code 2 on a `PostToolUse` hook logs an error but cannot undo the tool that already ran. Use `PreToolUse` for blocking gates.

**Mistake 3: Missing null checks on CLAUDE_TOOL_OUTPUT_PATH**
Not all tools set `CLAUDE_TOOL_OUTPUT_PATH`. Always guard: `if [ -n "$CLAUDE_TOOL_OUTPUT_PATH" ]; then ...`

**Mistake 4: Forgetting the shell shebang**
If you reference an external script, ensure it's executable (`chmod +x`) and has a proper shebang (`#!/bin/bash`). Without the shebang, the OS doesn't know how to execute it.

### Testing Hooks Without Claude

Test your hook scripts directly in the terminal by manually setting environment variables:

```bash
export CLAUDE_TOOL_NAME="Bash"
export CLAUDE_TOOL_INPUT='{"command":"rm -rf /tmp/test"}'
export CLAUDE_WORKSPACE="/path/to/your/project"
bash ~/.claude/hooks/destructive-check.sh
echo "Exit code: $?"
```

This lets you iterate on hook logic without triggering full Claude Code sessions, which is especially important for security-gate hooks where a false positive would block legitimate work.

---

## FAQ

**What is the difference between Claude Code hooks and CLAUDE.md instructions?**
CLAUDE.md is a text file that Claude reads as part of its context — it informs the model's behavior but is interpreted by the LLM, not enforced by the system. Hooks in `settings.json` are deterministic shell commands that run unconditionally at lifecycle events. Hooks cannot be forgotten, ignored, or misinterpreted. Use CLAUDE.md for project context and preferences; use hooks for policies that must never fail.

**Can Claude Code hooks block an action permanently, or just warn?**
Exit code 2 hard-blocks the tool call and surfaces an error message to the developer. The action never executes. Exit code 0 allows execution to proceed. Any other exit code logs a warning but does not block. To permanently block a pattern, use `exit 2` in a `PreToolUse` hook targeting the relevant tools.

**How do I share hooks across my entire team?**
Create a `.claude/settings.json` file at your project root (not `~/.claude/settings.json`, which is user-level). Add your hooks there and commit it to version control. Every developer who clones the repository automatically gets the hooks applied to their Claude Code sessions for that project.

**What changed in the March 2026 hook update?**
The March 2026 update expanded the hook event system from 10 to 18 events. New events include `StopFailure`, `SubagentStart`, `SubagentStop`, `ConfigChange`, `PreCompact`, `PostCompact`, and two MCP elicitation support events. The update also added automatic subprocess credential scrubbing, which strips common credential patterns from hook environment variables before passing them to subprocess commands.

**How do I debug a hook that silently fails?**
Add explicit logging to stderr in your hook script: `echo "[hook debug] Tool: $CLAUDE_TOOL_NAME, Path: $CLAUDE_TOOL_OUTPUT_PATH" >&2`. Claude Code captures stderr output from hooks and displays it in the session. Then test the script manually by exporting the relevant environment variables and running the script directly in your terminal to isolate environment issues.