---
title: "Superpowers + Claude Code: TDD Workflow Setup Guide 2026"
date: 2026-05-23T04:16:02+00:00
tags: ["Claude Code", "Superpowers", "TDD", "test-driven development", "AI coding", "developer tools"]
description: "How to set up the Superpowers framework with Claude Code for enforced TDD workflows — with real configuration examples and what changes in practice."
draft: false
cover:
  image: "/images/superpowers-claude-code-tdd-guide-2026.png"
  alt: "Superpowers + Claude Code: TDD Workflow Setup Guide 2026"
  relative: false
schema: "schema-superpowers-claude-code-tdd-guide-2026"
---

The biggest failure mode when using AI coding agents is letting them skip the test. Superpowers is an open-source framework — 99K+ GitHub stars, 2.5M+ VS Code extension downloads, official Claude Plugin Marketplace listing — that enforces test-driven development as a hard constraint on Claude Code rather than a suggestion. Here's how to set it up and what actually changes in practice.

## What Is the Superpowers Framework and Why TDD Enforcement Matters

Superpowers is a framework that installs as a system prompt layer between your requests and Claude Code's reasoning engine, enforcing a 5-phase TDD discipline on every coding task: requirements clarification, test writing, implementation, test passing, and refactoring. Unlike `.cursorrules` or a `CLAUDE.md` file that suggests behavior, Superpowers uses a structured agent protocol that blocks code generation until a failing test exists. The framework reached 99K+ GitHub stars and an official listing on the Anthropic Claude Plugin Marketplace, with 2.5M+ VS Code extension downloads as of 2026. The core insight behind Superpowers is that AI coding agents are optimistic — they generate code that looks correct and compiles cleanly, but fails in edge cases that a test suite would catch immediately. When you add TDD enforcement at the framework level, Claude Code can't take the shortcut of writing implementation first and hoping tests follow. The workflow discipline is structural, not optional. For developers who have shipped code with AI agents only to find regressions a week later, this matters significantly. The free tier is available for individual use with a Pro plan at $20/month for team features.

## Installing Superpowers with Claude Code

Installing Superpowers takes about five minutes. You need Claude Code running (CLI or VS Code extension) and either npm or pip available.

**Option 1: VS Code Extension (recommended for most developers)**

Install the Superpowers VS Code extension directly from the marketplace:

```
ext install superpowers-ai.superpowers
```

After installation, open VS Code settings and configure your Claude API key:

```json
{
  "superpowers.apiKey": "sk-ant-your-key-here",
  "superpowers.tddMode": "strict",
  "superpowers.testFramework": "auto"
}
```

Set `tddMode` to `strict` to block code generation before tests. `auto` detects your test framework from `package.json`, `pyproject.toml`, or `Cargo.toml`.

**Option 2: Claude Code CLI plugin**

```bash
claude plugin install superpowers
claude plugin configure superpowers --tdd-mode strict
```

**Option 3: Manual CLAUDE.md integration**

If you prefer not to use the extension, you can bootstrap Superpowers behavior by adding the framework's system prompt to your project's `CLAUDE.md`:

```bash
curl -o CLAUDE.md https://raw.githubusercontent.com/obra/superpowers/main/prompts/strict-tdd.md
```

The manual approach gives you full control over the prompt but loses the extension's IDE integrations (test status bar, coverage overlays).

## Configuring the TDD Workflow

The 5-phase Superpowers discipline maps onto Claude Code as a structured conversation pattern. Each phase produces a checkpoint that Superpowers tracks before allowing the next:

**Phase 1: Requirements Clarification.** Claude asks clarifying questions before writing any code. This prevents the "build the wrong thing" failure mode that's common with AI agents. Superpowers forces at least one clarification round on ambiguous requests.

**Phase 2: Test Writing.** Before any implementation code, Claude writes failing tests that describe the expected behavior. These tests must actually fail (Superpowers verifies this by running your test suite).

**Phase 3: Implementation.** Implementation code is written to make the failing tests pass. Nothing more.

**Phase 4: Test Passing.** Superpowers runs your test suite and verifies all target tests pass before marking the phase complete.

**Phase 5: Refactoring.** With a passing test suite as a safety net, Claude refactors implementation code for clarity and performance without changing behavior.

Configure the phases in `.superpowers/config.json`:

```json
{
  "phases": {
    "clarification": { "required": true, "min_questions": 1 },
    "test_first": { "required": true, "verify_failure": true },
    "implementation": { "max_lines_per_commit": 200 },
    "verify_passing": { "required": true, "fail_on_error": true },
    "refactor": { "enabled": true, "lint_check": true }
  },
  "test_command": "npm test",
  "coverage_minimum": 80
}
```

## Writing a Test First: What It Looks Like in Practice

Here's what the Superpowers workflow looks like on a real task — adding a rate limiter to an API endpoint.

You prompt Claude: "Add rate limiting to the `/api/generate` endpoint. Limit to 10 requests per minute per user."

With Superpowers in strict mode, Claude's response starts with clarification:

> Before writing code: should the rate limit reset at the start of each minute (fixed window) or slide as requests arrive (sliding window)? What should happen when the limit is exceeded — return a 429 with retry-after, or silently drop? Are authenticated and anonymous users limited separately?

After clarification, Claude writes the test:

```typescript
describe('Rate limiter', () => {
  it('allows 10 requests per minute per user', async () => {
    const userId = 'test-user-1';
    for (let i = 0; i < 10; i++) {
      const res = await request(app).post('/api/generate').set('x-user-id', userId);
      expect(res.status).not.toBe(429);
    }
    const res = await request(app).post('/api/generate').set('x-user-id', userId);
    expect(res.status).toBe(429);
    expect(res.headers['retry-after']).toBeDefined();
  });

  it('tracks limits independently per user', async () => {
    for (let i = 0; i < 10; i++) {
      await request(app).post('/api/generate').set('x-user-id', 'user-a');
    }
    const res = await request(app).post('/api/generate').set('x-user-id', 'user-b');
    expect(res.status).not.toBe(429);
  });
});
```

Superpowers runs `npm test` and verifies these tests fail (they do — the endpoint doesn't have rate limiting yet). Only then does Claude write the implementation. This workflow catches the most common AI coding failure: writing an implementation that passes its own tests but misses edge cases.

## Performance Improvements in Practice

Superpowers TDD enforcement has measurable effects on code quality, review speed, and production reliability. Teams using Superpowers consistently report fewer regression bugs per sprint — the verify_failure checkpoint catches behavior changes that would otherwise pass CI and ship. Code review is faster because reviewers see tests alongside implementation, giving them a spec to evaluate the code against rather than inferring intent. Production debugging time decreases because the test suite documents expected behavior and makes it easier to pinpoint where behavior diverged. The specific impact varies by team and project, but the direction is consistent: more upfront time per task, less time fixing problems after merge. Enterprise case studies from Superpowers' ROI reports show teams reducing post-release bug reports by 30–45% after adopting the framework, with the heaviest benefits in API and business logic layers where edge cases are most costly.

The tradeoff is speed on individual tasks: initial task completion takes 20–30% longer with Superpowers because clarification and test-writing phases add round trips before implementation starts. For prototyping or spike work where correctness is less critical, this friction is real. Most teams configure a `--fast` flag that disables strict TDD for exploratory branches and enables it automatically on branches targeting `main`.

## Best Practices and Patterns

**Commit tests separately from implementation.** This makes code review easier and preserves the test-first intent in your git history. Superpowers can enforce this with a pre-commit hook: `superpowers hook install --require-test-commit`.

**Use coverage minimums per feature area, not globally.** A 90% global coverage target hides coverage gaps in critical paths. Configure Superpowers to enforce 100% coverage on your API layer and lower thresholds for UI components.

**Combine with TypeScript strict mode.** The type safety and test enforcement layers complement each other — TypeScript catches type errors at build time that tests catch at runtime. Running both eliminates a broad class of bugs before review.

**Don't enforce TDD on data migration scripts.** One-shot scripts that run once and then become dead code don't benefit from TDD investment. Configure Superpowers to skip enforcement in a `scripts/` or `migrations/` directory with:

```json
{
  "exclude_paths": ["scripts/", "migrations/", "*.seed.ts"]
}
```

## FAQ

**Q: Does Superpowers work with test frameworks other than Jest?**
Yes — Superpowers has built-in support for Jest, Vitest, Mocha, pytest, RSpec, Cargo test, and Go test. The `testFramework: "auto"` setting detects your framework from project config files. You can also configure a custom test command in `.superpowers/config.json` if you use an unusual test runner.

**Q: Can I use Superpowers with Cursor or Windsurf instead of Claude Code?**
Superpowers was built for Claude Code and works best with Claude models. Cursor and Windsurf have partial support through the VS Code extension API, but some phase enforcement features (verify_failure step, inter-phase blocking) require the Claude Code execution environment to work reliably.

**Q: What happens if Claude generates code before the test in strict mode?**
Superpowers intercepts the response and returns an error to Claude's context: "Implementation code detected before test. Please write failing tests first." Claude then backtracks and writes the test before implementation. In practice, after a few interactions Claude adapts to the expected workflow without prompting.

**Q: Does the Pro plan ($20/month) add meaningful features for solo developers?**
The free tier includes all TDD enforcement features. Pro adds team coverage dashboards, shared configuration management across a team, CI integration for coverage reporting, and priority support. For solo developers, the free tier is sufficient for most workflows.

**Q: How does Superpowers handle test generation for UI components?**
UI component testing is the weakest area. Superpowers can generate Jest + Testing Library tests for React/Vue components, but visual correctness testing (screenshot comparison, visual regression) is outside its scope. For UI-heavy projects, pair Superpowers with a visual testing tool like Chromatic or Percy for full coverage.
