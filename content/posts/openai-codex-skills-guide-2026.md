---
title: "OpenAI Codex Skills Guide: Reusable Agent Behaviors for Developer Workflows"
date: 2026-05-17T06:04:39+00:00
tags: ["openai codex", "codex skills", "ai coding agents", "developer productivity", "agentic coding"]
description: "Master OpenAI Codex Skills — the reusable agent behavior system that encodes workflows once and deploys them indefinitely across dev teams."
draft: false
cover:
  image: "/images/openai-codex-skills-guide-2026.png"
  alt: "OpenAI Codex Skills Guide: Reusable Agent Behaviors for Developer Workflows"
  relative: false
schema: "schema-openai-codex-skills-guide-2026"
---

OpenAI Codex Skills are reusable, self-contained packages that encode a developer workflow once and let Codex invoke that workflow on demand — without re-prompting. If you've ever corrected Codex on the same PR review pattern three times, a skill makes that correction permanent.

## What Are OpenAI Codex Skills? (The Agent Macro Model)

A Codex Skill is a task-specific package of instructions, optional scripts, reference documents, and assets that Codex can invoke autonomously when it determines a skill is relevant. Launched as an experimental feature in December 2025 and reaching wide availability in early 2026, Skills solve a specific problem: AI coding agents are powerful but stateless — every new session forgets your team's conventions. Skills make those conventions persistent and composable.

Think of a skill as an "agent macro." You define a workflow once in a `SKILL.md` file — PR review conventions, release checklist steps, CI failure diagnosis procedures — and Codex loads that definition whenever it decides the skill applies. The critical insight is **progressive context disclosure**: Codex only reads a skill's name, description, and path during normal operation, pulling the full `SKILL.md` into context only when it decides to invoke the skill. This keeps each session's context lean even if you have dozens of skills installed.

The growth numbers validate the demand: Codex hit 4M+ weekly active developers by April 21, 2026 — up from 3M just two weeks earlier, and from 2M in March 2026. Enterprise Codex users (ChatGPT Business/Enterprise) grew 6x between January and April 2026. OpenAI's own SDK repos merged 457 PRs using skills-based workflows in just three months (December 2025–February 2026). The takeaway: Skills aren't a niche feature — they're the mechanism that turns Codex from a code completer into a team-scale automation platform.

## Skills vs. AGENTS.md — When to Use Each

AGENTS.md is always-on repository-level context that Codex loads into every session. It's the right place for universal project rules: coding style, test commands, branch naming, commit format, and "never do X" constraints. Every Codex task in that repo reads AGENTS.md unconditionally, which makes it high-value but also high-cost — it occupies context regardless of what the task is.

Skills, by contrast, are **on-demand and task-specific**. Codex reads only a skill's metadata (name + description) by default, loading the full `SKILL.md` only when it decides the skill is relevant to the current task. This makes skills the right tool for workflows that apply sometimes — PR review, changelog generation, deployment procedures — rather than always.

| Dimension | AGENTS.md | Skills |
|---|---|---|
| Loading | Always loaded | On-demand, metadata-first |
| Scope | Repo-wide defaults | Task-specific procedures |
| Location | Repo root | `~/.agents/skills/` or `.agents/skills/` |
| Trigger | Automatic | Codex decides based on context |
| Best for | Universal rules | Repeatable workflows |

The practical rule: if you're writing something that should govern every Codex session in the repo, it goes in AGENTS.md. If you're encoding a specific workflow you invoke repeatedly, it's a skill. Many teams use both: AGENTS.md sets the standards, skills define how to execute specific tasks against those standards.

A PR review skill, for example, might tell Codex exactly how to structure review comments, which files to prioritize, and what the team's "ship it" criteria are — but you only want that loaded when Codex is actually doing a PR review, not when it's generating tests or fixing a type error.

## Anatomy of a SKILL.md File (Structure + Example)

A SKILL.md file is a Markdown document with a required structure and optional components that together define a complete, self-contained agent workflow. The required file is always `SKILL.md` at the skill's root — this is what Codex reads when it decides to invoke the skill. Optional additions include a `scripts/` directory for shell scripts Codex can execute directly, a `references/` directory for external docs, templates, or team standards the skill should follow, and an `assets/` directory for binary resources like configuration files or example outputs. The SKILL.md itself must include at minimum a skill name (H1), a short description, a "When to use this skill" section (the trigger metadata Codex reads during skill matching), and a numbered steps list. Without the trigger section, Codex can't reliably match the skill to incoming requests — it's the most critical structural element.

The full directory layout for a skill named `pr-review`:

```
.agents/skills/pr-review/
├── SKILL.md          # Required — the skill definition
├── scripts/
│   └── fetch-diff.sh # Optional — Codex can run these
└── references/
    └── review-checklist.md  # Optional — supporting docs
```

A production-ready `SKILL.md` for a PR review skill looks like this:

```
# PR Review

Review a pull request and provide structured feedback that matches
our team's quality bar.

**When to use this skill:**
When asked to review a PR, check a pull request, or audit changes
before merge.

**Steps:**

1. Fetch the PR diff using `gh pr diff {PR_NUMBER}`
2. Check for tests: every changed function must have a corresponding test
3. Check for doc updates: public API changes must update the relevant
   docs/ file
4. Review error handling: no bare `except:` or unchecked `.unwrap()`
5. Format review comments as inline GitHub comments, not a summary block
6. Label the PR: `approved`, `needs-changes`, or `needs-discussion`

**Output format:**
Use `gh pr review` to post inline comments. End with a summary comment
that lists blockers (if any) and a final verdict.
```

The **When to use this skill** section is critical — it provides the description metadata that Codex uses to match the skill to incoming tasks. Write it with trigger phrases that match how your team actually phrases requests: "review a PR," "check before merge," "audit changes."

## Where to Store Skills: Personal, Repo, and Catalog Tiers

Codex Skills have three distinct storage locations, each with a different scope and audience:

**Personal skills** live at `~/.agents/skills/` and are available across all of your Codex sessions on your machine. Use personal skills for workflows that are idiosyncratic to you — your preferred debugging approach, your personal release checklist, your documentation style. These never leave your machine and aren't shared with teammates.

**Repo-level skills** live at `.agents/skills/` inside the repository and are checked into git. When a teammate clones the repo, they inherit all team skills immediately. This is the mechanism that makes skills a living onboarding document: new developers get the team's institutional knowledge — PR procedures, deployment steps, test patterns — from day one without any manual setup.

**The official openai/skills catalog** is a curated set of ready-to-use skills maintained by OpenAI. There are three catalog tiers:

- `.system` — auto-installed skills that come with Codex by default
- `.curated` — high-quality community skills installable via the `$skill-installer` command
- `.experimental` — skills in review, available but not yet officially endorsed

Installing a curated skill is a single command:

```bash
codex install-skill gh-fix-ci
```

After installation, the skill appears in `.agents/skills/` and Codex can invoke it automatically. Curated skills are the fastest way to get started — they cover the most common developer pain-points and are reviewed by OpenAI before promotion from experimental.

## 9 Essential Codex Skills Every Developer Team Needs in 2026

These nine skills cover the highest-ROI use cases for most engineering teams in 2026. Each addresses a workflow that developers repeat daily and currently handle either manually or with one-off prompts that Codex forgets.

**1. PR Review (`pr-review`)** — Structured pull request review with team-specific criteria. Include your "must have tests," "check for API doc updates," and format preferences. This is the highest-value skill for most teams because PR review quality is inconsistent without it.

**2. CI Fix (`gh-fix-ci`)** — Diagnose and fix failing CI runs. The curated `gh-fix-ci` skill fetches the CI log, identifies the failure, and proposes a fix. Particularly valuable for flaky tests and environment-specific failures that junior developers struggle to diagnose quickly.

**3. Changelog Generation (`generate-changelog`)** — Extract merged PRs since the last release tag, categorize them (features, fixes, breaking changes), and produce a formatted `CHANGELOG.md` entry. Eliminates a task that developers consistently skip or do poorly under deadline pressure.

**4. Test Generation (`generate-tests`)** — Generate unit and integration tests for specified functions or modules. Define your testing framework, coverage targets, and mock preferences in the skill so output matches your codebase's test style.

**5. Code Documentation (`document-code`)** — Generate or update docstrings, JSDoc, or Rustdoc for specified files. Include your documentation style guide in `references/` so output matches your conventions rather than generic AI output.

**6. Release Preparation (`prepare-release`)** — End-to-end release checklist: bump version, update changelog, run test suite, build artifacts, tag the commit, and generate release notes. A skill that replaces a five-page internal wiki page with an automated procedure.

**7. Address Review Comments (`gh-address-comments`)** — Available as a curated skill. Fetches all open review comments on a PR and systematically addresses them, filing each as resolved after applying the change. Turns multi-hour revision loops into a single Codex invocation.

**8. Deploy to Cloudflare/Netlify (`cloudflare-deploy`, `netlify-deploy`)** — Curated deployment skills that handle authentication, build steps, environment variable injection, and post-deploy smoke tests. Include your environment-specific configurations in the skill's `references/` directory.

**9. Notion Knowledge Capture (`notion-knowledge-capture`)** — Curated skill that extracts decisions, architectural choices, and post-mortems from a session and writes them to your team's Notion workspace. Addresses the "we solved this before but nobody documented it" problem that plagues most teams.

## The Official openai/skills Catalog: Curated Skills Breakdown

The `openai/skills` GitHub repository is the authoritative source for production-ready, OpenAI-reviewed skills. As of May 2026, the curated tier includes the following skills that cover the most common developer workflows:

| Skill | What It Does | Best For |
|---|---|---|
| `gh-fix-ci` | Fetches CI logs, diagnoses failures, proposes fixes | Any CI/CD pipeline |
| `gh-address-comments` | Systematically addresses all open PR review comments | Fast PR iteration |
| `cloudflare-deploy` | Full Cloudflare Pages/Workers deployment workflow | JAMstack teams |
| `netlify-deploy` | Full Netlify deployment with preview URLs | Frontend teams |
| `notion-knowledge-capture` | Writes session decisions to Notion | Teams on Notion |
| `pdf` | Extracts, parses, and summarizes PDF content | Document-heavy workflows |
| `imagegen` | Generates images via DALL-E for design prototyping | Design/product teams |
| `jupyter-notebook` | Creates and executes Jupyter notebooks | Data science teams |
| `develop-web-game` | End-to-end web game scaffolding and development | Game/creative projects |
| `linear` | Creates and updates Linear issues from Codex sessions | Linear-based teams |

Each curated skill has an `agents/openai.yaml` sidecar that configures advanced behavior: allowed shell commands, required environment variables, approval thresholds, and sandboxing settings. When you install a curated skill, this configuration is applied automatically.

The `.experimental` tier contains skills under review. They work but may have rough edges — use them in non-production workflows and report issues via the `openai/skills` GitHub tracker to help them reach curated status.

## Building Your First Custom Skill: Step-by-Step

Creating a custom skill takes about 15 minutes the first time and produces a reusable asset that saves that time on every subsequent invocation. The key design decisions are: what triggers the skill, what prerequisites it requires, what steps it executes, and what format its output takes. Get those four elements right and the skill will work reliably across team members, machines, and CI environments. This walkthrough builds a `release-prep` skill from scratch — a workflow that most engineering teams run manually today and that benefits immediately from automation. The skill will handle version bumping, changelog generation, git tagging, and GitHub release creation as a single Codex invocation. You can adapt the same structure to any repetitive workflow: deployment pipelines, test suite runs, documentation updates, or any multi-step procedure your team executes more than once a week.

**Step 1: Create the skill directory.**

```bash
mkdir -p .agents/skills/release-prep/scripts
mkdir -p .agents/skills/release-prep/references
```

**Step 2: Write the `SKILL.md`.**

```
# Release Preparation

Prepare a new release: bump version, update changelog, tag, and generate
release notes.

**When to use this skill:**
When asked to cut a release, prepare a release, bump the version, or
generate release notes.

**Prerequisites:**
- GITHUB_TOKEN env var set with repo write access
- gh CLI installed and authenticated
- Working on the main branch with a clean working tree

**Steps:**

1. Confirm the release type with the user: patch / minor / major
2. Run `npm version {type}` (or `cargo bump {type}` for Rust projects)
3. Run `./scripts/gen-changelog.sh` to update CHANGELOG.md
4. Commit: `git commit -am "chore: release v{VERSION}"`
5. Tag: `git tag v{VERSION}`
6. Push: `git push && git push --tags`
7. Create GitHub release: `gh release create v{VERSION} --generate-notes`

**Output:**
Confirm the release URL from `gh release create` output and post it
to #releases in Slack using `scripts/notify-slack.sh`.
```

**Step 3: Add supporting scripts.**

```bash
# scripts/gen-changelog.sh
#!/bin/bash
LAST_TAG=$(git describe --tags --abbrev=0)
git log ${LAST_TAG}..HEAD --oneline --no-merges | \
  awk '{$1=""; print "- " $0}' >> CHANGELOG.md
```

**Step 4: Test the skill by invoking it explicitly.**

```bash
codex "Use the release-prep skill to cut a patch release"
```

**Step 5: Iterate on the trigger description.** If Codex isn't picking up the skill automatically when you say "let's cut a release," refine the "When to use this skill" section to include more trigger phrases. Trigger specificity is the most common point of friction when first writing custom skills.

**Step 6: Commit to the repo.** Once the skill works reliably, commit `.agents/skills/release-prep/` so every teammate inherits it.

## Integrating Skills with GitHub Actions and CI/CD

Skills define **how** to execute a workflow; GitHub Actions automations define **when** to trigger it. The combination gives you full CI/CD integration without maintaining a separate automation layer.

The pattern: create a GitHub Actions workflow that calls Codex with a specific skill on a trigger event. Here's an example that runs the `pr-review` skill whenever a PR is opened against `main`:

```yaml
# .github/workflows/codex-pr-review.yml
name: Codex PR Review
on:
  pull_request:
    branches: [main]

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run Codex PR Review
        uses: openai/codex-action@v1
        with:
          prompt: "Use the pr-review skill to review PR #${{ github.event.number }}"
          skill: pr-review
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

Skills dramatically reduce the complexity of these action definitions because the logic lives in SKILL.md, not in the workflow YAML. The workflow triggers the skill; the skill handles all the steps. This means updating the PR review procedure requires editing one SKILL.md file, not hunting through workflow YAML across multiple repositories.

Common automation triggers that pair well with specific skills:

| Trigger | Recommended Skill |
|---|---|
| PR opened against `main` | `pr-review` |
| CI job fails | `gh-fix-ci` |
| Push to release branch | `release-prep` |
| PR merged to `main` | `generate-changelog` |
| New issue labeled `needs-docs` | `document-code` |

For teams using Codex automations (the native Codex scheduling layer), you can configure these triggers directly in an `agents/automations.yaml` file without GitHub Actions. The skills remain the same — only the invocation mechanism changes.

## Real-World Results: How OpenAI Used Skills to Merge 457 PRs

The most concrete evidence for Codex Skills' productivity impact comes from OpenAI's own SDK maintenance operations. Between December 2025 and February 2026 — three months — OpenAI's own engineering team merged 457 pull requests across two SDK repositories using skills-based workflows. That's approximately 5 PRs per day, sustained, on repositories that also needed to stay in sync with rapidly changing APIs.

The skills they deployed covered four categories:

**Verification skills** — automated pre-merge checks for type safety, API contract compatibility, and test coverage thresholds. These replaced manual checklist steps that were frequently skipped under deadline pressure.

**Release preparation skills** — end-to-end release packaging that generated changelogs, bumped version numbers, created GitHub releases, and posted release notes. The release process went from a 2–3 hour manual procedure to a single Codex invocation.

**Integration testing skills** — skills that spun up test environments, ran the full integration suite against the latest API version, and filed issues for any new failures. This caught API breaking changes within hours of their introduction.

**PR review skills** — structured review of contributor PRs with team-specific quality criteria. This enabled the team to process external contributions at a rate that would have been impossible with manual review alone.

The broader lesson: 457 PRs in 3 months isn't an output metric — it's a maintenance metric. It means the SDK stayed current, bugs got fixed quickly, and contributor PRs didn't sit in the queue for weeks. Skills turned a high-friction maintenance process into a near-automated pipeline. The pattern is reproducible for any team maintaining a library, API, or platform that receives regular contributions.

## Best Practices for Reliable, Team-Shareable Skills

Building a skill that works once in your local environment is straightforward. Building one that works reliably for every teammate, in CI, across different machines and OS environments, requires deliberate design.

**Write trigger phrases that match real usage.** The "When to use this skill" section is not just documentation — it's the matching signal Codex uses to activate your skill. Include synonyms and common phrasings: "cut a release," "prepare a version bump," "tag for release," not just "release preparation." Broad, natural-language trigger coverage is the most impactful factor in skill reliability.

**Encode prerequisites explicitly.** List required environment variables, CLI tools, and repository state in the `SKILL.md` prerequisites section. If the skill requires `GITHUB_TOKEN`, `gh` CLI, and a clean working tree, say so. Codex will check prerequisites before starting and fail fast with a clear message rather than producing a broken intermediate state.

**Keep scripts idempotent.** Scripts in `scripts/` should be safe to run multiple times. If the script creates a git tag and the tag already exists, it should handle that gracefully rather than failing noisily. Idempotency makes skills reliable in CI environments where partial runs and retries are common.

**Version-control team skills.** Commit `.agents/skills/` to the repo. This means skill updates are tracked in git history, reviewed via PR, and deployed to all teammates on pull. Treat a skill update as a production change — it changes how Codex behaves for the entire team.

**Test skills with explicit invocation before relying on auto-matching.** When building a new skill, invoke it explicitly (`"Use the pr-review skill to..."`) rather than relying on auto-matching. Once the skill works correctly, refine the trigger description to improve auto-matching. Don't debug skill logic and trigger matching simultaneously.

**Separate skills by concern.** Resist the temptation to build one skill that does "everything release-related." A `bump-version` skill, a `generate-changelog` skill, and a `create-release` skill are each more reliable and reusable than a monolithic `full-release` skill. Compose them in a workflow when you need the full procedure.

**Document the output format explicitly.** Codex will produce well-structured output if you specify the format in the skill. "Post inline comments using `gh pr review`" produces different behavior than "summarize your findings." Output format specifications are the fastest way to make skill output match your team's expectations without iteration.

---

## FAQ

**What is the difference between a Codex Skill and an AGENTS.md file?**

AGENTS.md is always loaded for every Codex session in the repository — it provides universal project rules that apply unconditionally. A Codex Skill is loaded on-demand only when Codex determines the skill is relevant to the current task. Use AGENTS.md for standards that always apply (coding style, test commands), and Skills for procedures you invoke situationally (PR review, deployments, changelog generation).

**Can I share Codex Skills with my team?**

Yes. Skills stored in `.agents/skills/` inside a repository are checked into git and shared with everyone who clones the repo. This is the recommended approach for team workflows. Personal skills at `~/.agents/skills/` stay on your local machine and aren't shared.

**How does Codex decide which skill to use?**

Codex reads the name, description, and "When to use this skill" section of each installed skill. When you give Codex a task, it matches your request against these metadata fields and selects the most relevant skill, loading the full `SKILL.md` only after selection. Writing specific, natural-language trigger phrases in this section is the primary way to improve matching reliability.

**How do I install a skill from the official openai/skills catalog?**

Run `codex install-skill {skill-name}` in your terminal. For example, `codex install-skill gh-fix-ci` installs the CI fix skill into `.agents/skills/`. The skill is ready to use immediately after installation. You can also clone the `openai/skills` GitHub repo and copy skill directories manually.

**Can skills run shell commands and scripts?**

Yes. Skills can include a `scripts/` directory with shell scripts that Codex executes as part of the workflow. Codex has access to your terminal environment when running skills, so scripts can use `gh`, `git`, `npm`, `cargo`, and any other CLI tools available on your machine. For CI environments, ensure required tools are available in the CI runner image.
