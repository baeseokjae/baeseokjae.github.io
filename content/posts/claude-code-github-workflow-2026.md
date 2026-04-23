---
title: "Claude Code GitHub Workflow 2026: PR Reviews, Commits, and CI Integration"
date: 2026-04-23T01:19:59+00:00
tags: ["Claude Code", "GitHub Actions", "CI/CD", "code review", "AI automation"]
description: "Complete guide to Claude Code GitHub workflow: automated PR reviews, CI failure auto-fix, and enterprise CI/CD integration using claude-code-action@v1."
draft: false
cover:
  image: "/images/claude-code-github-workflow-2026.png"
  alt: "Claude Code GitHub Workflow 2026: PR Reviews, Commits, and CI Integration"
  relative: false
schema: "schema-claude-code-github-workflow-2026"
---

Claude Code GitHub workflow integrates Anthropic's `claude-code-action@v1` directly into GitHub Actions, enabling automated PR reviews, CI failure auto-fixes, and structured code analysis — all triggered by `@claude` mentions or YAML automation rules with under $5/month in API costs for most teams.

## What Is Claude Code GitHub Actions?

Claude Code GitHub Actions is an official Anthropic action (`anthropics/claude-code-action@v1`) that runs the full Claude Code runtime inside a standard GitHub Actions runner. Launched September 29, 2025 as part of Claude Code 2.0 and built on Anthropic's Agent SDK, it gives AI code review capabilities directly inside your existing CI/CD pipeline without any third-party integrations. Instead of switching between your IDE, GitHub, and a separate AI tool, Claude operates directly inside the pull request lifecycle — reading diffs, running checks, posting structured review comments, and even pushing fix commits. At $3/MTok input and $15/MTok output (Claude Sonnet 4 pricing), a 400-line diff typically costs under $0.05, making it economically viable even at high PR volumes. With 84% of developers now using AI-assisted coding tools and AI code review adoption growing from 49.2% in January 2025 to 69% by October 2025, teams that haven't automated their review pipeline are falling behind on the metric that actually limits delivery velocity in 2026: review capacity, not development speed.

### Two Operating Modes

Claude Code GitHub Actions runs in two modes depending on your workflow configuration:

**Interactive mode** is triggered by `@claude` mentions in PR comments or issue comments. A developer comments `@claude review this for security issues` and Claude responds with a structured analysis, inline code suggestions, or direct commits to the branch. This mode is ideal for targeted, ad-hoc requests where a human explicitly wants Claude's input on a specific concern.

**Automation mode** uses a `prompt` parameter in the YAML workflow definition to run Claude headlessly on every PR, push, or CI event without any human trigger. This is the pattern used for pre-triage PR reviews, CI failure diagnosis, and structured quality gates that run as part of every merge pipeline.

## Quick Setup: Three Paths to Get Started

Getting Claude Code running in GitHub Actions requires about 10 minutes regardless of which setup path you choose. All three paths produce the same running workflow — they differ only in how you install the GitHub App and configure secrets. The fastest path is the CLI quickstart: inside your Claude Code terminal, run `/install-github-app`, which auto-installs the Anthropic GitHub App on your chosen repository, configures the `ANTHROPIC_API_KEY` secret in your repo settings, and creates a starter `.github/workflows/claude.yml` file. No manual YAML editing required for your first run. This path gets you from zero to working automated review in under five minutes. The manual path suits teams that prefer infrastructure-as-code for all CI configuration changes. Install the Anthropic GitHub App from the GitHub Marketplace, add `ANTHROPIC_API_KEY` to Settings > Secrets > Actions, then create the workflow YAML manually. The Claude Max plan OAuth path is for teams on the Max subscription — it routes billing through your existing Max plan rather than per-token API billing, eliminating the need for a separate API key secret entirely.

The minimum permission set your workflow needs is `contents: read`, `pull-requests: write`, and `issues: write` — scope to exactly these three unless a specific pattern requires more.

## The Four Core Workflow Patterns

Claude Code GitHub Actions supports four distinct workflow patterns, each solving a different problem in the development lifecycle. These patterns are not mutually exclusive — production teams typically run patterns 2 and 3 together, with pattern 1 available for ad-hoc developer requests. Understanding which pattern fits which use case prevents over-engineering your initial setup and lets you layer in complexity only when you need it. The four patterns are: interactive `@claude` comment trigger for developer-requested reviews, automated PR code review for pre-triage on every pull request, CI failure auto-fix for autonomous diagnosis and patch commits, and structured output for downstream pipeline decisions. Each pattern uses the same `anthropics/claude-code-action@v1` action but with different trigger events, permissions, and prompt configurations. Start with pattern 2 in advisory mode to validate review quality before enabling blocking gates or autonomous fix commits.

### Pattern 1: Interactive @claude Comment Trigger

The interactive pattern is the lowest-friction entry point — it adds no automatic pipeline steps and only activates when a developer explicitly requests help. Configure it by creating a workflow that listens to `issue_comment` and `pull_request_review_comment` events and checks for your trigger phrase.

```yaml
name: Claude Interactive
on:
  issue_comment:
    types: [created]
  pull_request_review_comment:
    types: [created]

permissions:
  contents: write
  pull-requests: write
  issues: write

jobs:
  claude:
    if: contains(github.event.comment.body, '@claude')
    runs-on: ubuntu-latest
    steps:
      - uses: anthropics/claude-code-action@v1
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
```

With this configuration, any comment containing `@claude` triggers Claude to read the full PR context and respond. You can change the trigger phrase by setting `trigger_phrase: "@ai"` or any custom string. Claude will respond inline to the comment, either with analysis or with a follow-up commit if you've asked it to fix something.

### Pattern 2: Automated PR Code Review

The automated PR review pattern is the most commonly deployed configuration. Claude runs on every opened or updated pull request, reads the diff, and posts a structured review comment before any human reviewer sees the PR. This pre-triage catches obvious bugs, style violations, and security issues so human reviewers can focus on architecture and business logic.

```yaml
name: Claude PR Review
on:
  pull_request:
    types: [opened, synchronize]
    paths-ignore:
      - '**.lock'
      - 'dist/**'
      - 'build/**'

permissions:
  contents: read
  pull-requests: write

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: anthropics/claude-code-action@v1
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
          prompt: |
            Review this pull request for:
            1. Bugs and logic errors
            2. Security vulnerabilities (OWASP Top 10)
            3. Performance issues
            4. Missing error handling
            Post findings as a formal GitHub PR review.
          post_as_review: "true"
          review_event: "COMMENT"
```

The `paths-ignore` block is one of the highest-leverage cost controls available. Excluding lock files, build artifacts, and auto-generated code reduces token consumption by 30–50% without losing meaningful review coverage. For a team of 10 engineers merging 20 PRs/day, this filtering brings monthly costs from ~$48 down to ~$24.

Setting `post_as_review: true` submits Claude's output as a formal GitHub PR Review object — it appears in the "Reviews" section alongside human reviews and counts toward required-review branch protection rules if configured that way.

### Pattern 3: CI Failure Auto-Fix

The CI failure auto-fix pattern is the highest-impact configuration in terms of developer time saved. When a CI check fails on a pull request, Claude automatically diagnoses the failure, creates a fix branch, pushes a corrective commit, and opens a PR for human review — all without developer intervention.

```yaml
name: Claude CI Auto-Fix
on:
  workflow_run:
    workflows: ["CI"]
    types: [completed]

permissions:
  contents: write
  pull-requests: write
  checks: read

jobs:
  auto-fix:
    if: |
      github.event.workflow_run.conclusion == 'failure' &&
      !startsWith(github.event.workflow_run.head_branch, 'claude-fix/')
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          ref: ${{ github.event.workflow_run.head_sha }}
      - uses: anthropics/claude-code-action@v1
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
          prompt: |
            The CI pipeline failed. Diagnose the failure from the workflow logs,
            identify the root cause, fix it, commit to a new branch named
            claude-fix/${{ github.event.workflow_run.head_branch }},
            and open a PR with a clear explanation of what you changed and why.
          claude_args: "--max-turns 10"
```

The `!startsWith(github.event.workflow_run.head_branch, 'claude-fix/')` condition is the loop prevention guard — without it, Claude's own fix commits trigger new CI runs, which if they fail trigger more fix attempts in an infinite loop. This guard is non-negotiable for production deployments.

### Pattern 4: Structured Output for Downstream Decisions

The structured output pattern treats Claude as a quality gate that produces machine-readable JSON consumed by downstream workflow steps. Instead of posting human-readable comments, Claude emits a structured assessment that other jobs check and fail on:

```yaml
- uses: anthropics/claude-code-action@v1
  id: quality-gate
  with:
    anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
    prompt: |
      Analyze this PR and output ONLY valid JSON:
      {"approved": boolean, "severity": "low"|"medium"|"high"|"critical",
       "issues": [{"file": string, "line": number, "description": string}]}

- name: Check Gate
  run: |
    APPROVED=$(echo '${{ steps.quality-gate.outputs.result }}' | jq '.approved')
    if [ "$APPROVED" != "true" ]; then exit 1; fi
```

## Configuring claude-code-action: YAML Reference and Key Parameters

Understanding the full parameter set lets you fine-tune behavior without trial and error. The most important parameters for production deployments are documented below, along with the breaking changes introduced in v1 that affect teams upgrading from earlier versions. The `system_prompt` / prompt instruction is the highest-leverage configuration option: write your team's coding standards once and every PR inherits them automatically. The `claude_args` passthrough lets you set `--max-turns`, `--model`, and `--verbose` without waiting for action updates. The `trigger_phrase` defaults to `@claude` but can be any string — useful for teams that want a less visually prominent trigger like `/review` or `@ai`. For formal review integration, `post_as_review: true` submits output as a GitHub PR Review object that appears in the approvals section alongside human reviews, and `review_event` controls whether Claude's review blocks merges (`REQUEST_CHANGES`), allows merges (`APPROVE`), or is purely informational (`COMMENT`).

| Parameter | Type | Description |
|---|---|---|
| `anthropic_api_key` | secret (required) | Anthropic API key. Always `${{ secrets.ANTHROPIC_API_KEY }}`. |
| `prompt` | string | Instruction Claude receives. Omit for interactive-only mode. |
| `claude_args` | string | CLI flags: `--max-turns`, `--model`, `--verbose` |
| `trigger_phrase` | string | Default `@claude`. Customize for your team. |
| `post_as_review` | boolean | `true` submits formal GitHub PR Review; `false` posts comment. |
| `review_event` | enum | `COMMENT`, `APPROVE`, or `REQUEST_CHANGES` |

**Breaking changes from v0 to v1:** Mode is now auto-detected (no more `mode: tag`/`mode: agent`). `direct_prompt` was renamed to `prompt`. CLI flags moved to `claude_args`. These three changes account for 90% of v0→v1 migration issues.

## Cost Optimization: Path Filtering, Concurrency, and Token Budgets

Most teams running 50 PRs/month see under $5/month in Claude Code GitHub Actions API costs — making the ROI calculation trivial against the documented savings of 40% reduction in review labor costs and $1.2M/year in defect remediation reduction for large teams. At $3/MTok input and $15/MTok output for Claude Sonnet 4, a 400-line diff costs under $0.05. A team of 10 engineers merging 20 PRs/day runs about $24/month with path filtering applied. A 50-developer team sees annual AI review savings of roughly $250,000 against costs under $300/year. Three controls give the most cost leverage: path filtering at the workflow trigger level, concurrency groups to prevent review stacking, and `--max-turns` caps on agent iteration depth.

**Path filtering** prevents the workflow from triggering at all when only excluded files changed:

```yaml
on:
  pull_request:
    paths-ignore:
      - '**.lock'
      - 'dist/**'
      - '*.generated.ts'
      - 'migrations/**'
```

**Concurrency groups** cancel in-progress reviews when a new commit arrives on the same PR:

```yaml
concurrency:
  group: claude-review-${{ github.event.pull_request.number }}
  cancel-in-progress: true
```

**`--max-turns` cap** bounds agent iteration: use `--max-turns 5` for lint/format fixes, `--max-turns 15` for complex CI failure diagnosis.

## Security Guardrails: Loop Prevention, Permissions, and CLAUDE.md Constraints

Security and stability in CI/CD require defense-in-depth. Three guardrails are non-negotiable for production deployments of Claude Code GitHub Actions. First, loop prevention via branch naming conventions ensures Claude's own fix commits cannot re-trigger the workflow that created them — this is an infinite loop risk unique to agentic CI workflows and must be explicitly handled. Second, minimal permission scoping in the workflow `permissions` block limits blast radius: grant only `contents: write`, `pull-requests: write`, and `issues: write` unless a specific pattern requires more. Never grant `admin` or `actions: write` to a Claude workflow. Third, `CLAUDE.md` behavioral constraints define permanent guardrails in code that persist across every Claude Code execution including CI runs. These three controls work together: loop prevention handles agentic recursion, permission scoping limits what Claude can affect, and `CLAUDE.md` specifies what Claude should never do regardless of what it's asked.

Create `.claude/CLAUDE.md` at your repository root:

```markdown
# CI Guardrails

Never modify .github/workflows/** files.
Never commit secrets, API keys, or credentials.
Never push directly to main or master branches.
Never modify package.json dependency versions without explicit instruction.
Fix branches must use the claude-fix/ prefix.
```

Claude reads this file on every invocation, applying constraints uniformly to both interactive and automation mode runs.

## Enterprise Deployment: AWS Bedrock and Google Vertex AI Integration

For enterprise teams with data residency requirements or existing cloud commitments, Claude Code GitHub Actions supports four authentication backends — AWS Bedrock and Google Vertex AI route data through your own cloud infrastructure rather than directly through Anthropic's API. This satisfies data residency requirements, lets teams use existing cloud spend commitments, and eliminates direct Anthropic billing relationships for procurement-sensitive organizations. Both cloud integrations use OIDC for keyless authentication, eliminating the need to manage long-lived API key secrets in GitHub. AWS Bedrock integration requires an IAM role with `bedrock:InvokeModel` permission and a GitHub OIDC trust policy scoped to your repository. Google Vertex AI integration uses Workload Identity Federation with a service account that has Vertex AI User role. Both integrations support all four workflow patterns without any changes to your prompts or review logic — only the authentication block and a few action parameters change.

**AWS Bedrock OIDC setup:**

```yaml
- uses: aws-actions/configure-aws-credentials@v4
  with:
    role-to-assume: arn:aws:iam::YOUR_ACCOUNT:role/claude-code-github-actions
    aws-region: us-east-1

- uses: anthropics/claude-code-action@v1
  with:
    use_bedrock: "true"
    aws_region: us-east-1
    # No anthropic_api_key needed
```

**Google Vertex AI OIDC setup:**

```yaml
- uses: google-github-actions/auth@v2
  with:
    workload_identity_provider: projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/POOL/providers/PROVIDER
    service_account: claude-code@PROJECT.iam.gserviceaccount.com

- uses: anthropics/claude-code-action@v1
  with:
    use_vertex: "true"
    vertex_region: us-central1
    vertex_project_id: YOUR_PROJECT_ID
```

## The State of AI Code Review in 2026

The market data reflects a clear trajectory: AI code review is transitioning from early-adopter experiment to baseline infrastructure, with the AI code review market projected to reach $750M with 9.2% CAGR through 2033. Code assistant adoption grew from 49.2% in January 2025 to 69% by October 2025, peaking at 72.8% in August 2025. GitHub handles 82M+ pushes and 43M+ merged PRs per month, and 41% of commits are now AI-assisted. Review capacity — not development speed — is the primary constraint on delivery velocity in 2026. Leading AI review tools detect 42–48% of real-world runtime bugs with 85–95% overall accuracy and 5–15% false positive rates. Teams with mature AI review pipelines report 40% reductions in review labor costs and $1.2M/year in reduced defect remediation expenses at scale. CodeRabbit holds the largest market share at 2M+ repositories and 13M+ reviewed PRs reviewed, making it the most widely deployed platform. Claude Code's advantage in this landscape is integration depth: it runs the full Claude Code agent runtime rather than a review-only tool, enabling autonomous fix commits, multi-file refactors, and CI failure resolution that comment-based tools cannot do. For teams already using Claude Code as their primary IDE AI, the GitHub Actions integration extends the same conventions, `CLAUDE.md` configuration, and tool access to every PR in the pipeline.

## Troubleshooting Common Issues

Most Claude Code GitHub Actions failures fall into three categories that account for the overwhelming majority of support questions:

**Authentication errors** (`401 Unauthorized`): GitHub secrets are case-sensitive — verify the secret name in your YAML exactly matches the name in repository Settings > Secrets > Actions. For Bedrock/Vertex OIDC, check the trust policy subject claim matches your repository path (`repo:org/repo:ref:refs/heads/main`).

**Missing permissions** (`Resource not accessible by integration`): Add the missing scope to the `permissions` block. PR comments need `pull-requests: write`. Issue comment triggers need `issues: write`. Auto-fix commits need `contents: write`. CI log access needs `checks: read`.

**Loop prevention triggering on legitimate PRs**: The branch prefix check `!startsWith(..., 'claude-fix/')` only excludes branches starting with exactly `claude-fix/`. If your fix branches use a different prefix, update the guard to match. If legitimate branches are unexpectedly excluded, check that branch names don't accidentally start with `claude-fix/`.

**`@claude` not responding to inline review comments**: The `issue_comment` event covers top-level PR comments only. Add `pull_request_review_comment` to the `on:` block to also handle inline review thread comments.

## Best Practices: System Prompts, Review Standards, and Team Conventions

A well-configured system prompt is the difference between generic AI feedback and targeted review that enforces your specific team standards. Write your prompt to answer three questions: what does Claude know about your codebase, what standards should it enforce, and what format should it use? Encoding your standards once in the system prompt means every PR review inherits them without developer action — no checklist to remember, no style guide to look up. Keep the system prompt in your workflow YAML (for CI automation) and synchronized with your `.claude/CLAUDE.md` file (for interactive and local usage). When team standards evolve, update both files together. For teams new to AI code review, start with Pattern 2 in advisory `COMMENT` mode for the first two weeks — observe what Claude flags, calibrate the prompt against false positives, and only switch to `REQUEST_CHANGES` blocking mode after validating review quality against your specific codebase. A production-grade system prompt for a TypeScript/Node.js service:

```
You are a senior engineer reviewing PRs for our Node.js microservices backend.
Stack: TypeScript strict mode, Express, PostgreSQL with Knex, Jest.

Enforce:
- All database queries use parameterized statements (no string interpolation)
- All async Express handlers wrapped in asyncHandler() middleware  
- New env vars validated in config/env.ts on startup
- Tests cover happy path, error cases, and edge cases

Format:
- One-paragraph summary of what the PR does
- ## Critical Issues for blocking problems
- ## Suggestions for non-blocking improvements
- File and line number for every issue
- Final APPROVE or REQUEST_CHANGES recommendation
```

## FAQ

**What's the difference between claude-code-action and CodeRabbit?**
Claude Code GitHub Actions runs the full Claude Code agent runtime, enabling agentic actions (commits, fix PRs, file writes) beyond just commenting. CodeRabbit focuses on review comments at scale (2M+ repos, 13M+ PRs reviewed) but cannot autonomously fix CI failures or execute multi-step code changes. Use Claude Code when you want an AI that acts, not just advises.

**How do I prevent Claude from reviewing auto-generated files or lock files?**
Add a `paths-ignore` list to the `on: pull_request` trigger in your workflow YAML. Files matching those glob patterns won't trigger the workflow at all when they're the only files changed. This is the highest-impact cost control and prevents noise from non-human-written code.

**Can I use Claude Code GitHub Actions on a private repository?**
Yes. Private repos use identical configuration. Ensure the GitHub App installed via `/install-github-app` has access to the private repo, and that `ANTHROPIC_API_KEY` is set in that repo's Settings > Secrets > Actions.

**How do I handle Claude making changes I don't want in auto-fix mode?**
Add explicit prohibitions to `.claude/CLAUDE.md` and your workflow prompt. Specify files and directories Claude should never modify (workflow files, `package.json` dependency versions, migrations). Require all auto-fix PRs to go through human review by never having Claude push to protected branches directly.

**What model does claude-code-action use by default, and how do I change it?**
It defaults to the latest Claude Sonnet model. To pin a specific model, pass `--model claude-sonnet-4-6` via `claude_args`. For high-volume cost-sensitive pipelines, consider `claude-haiku-4-5` for straightforward lint/format checks and Sonnet for security and logic reviews.
