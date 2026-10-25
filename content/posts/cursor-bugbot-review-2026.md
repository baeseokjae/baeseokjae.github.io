---
cover:
  image: /images/og-default.png
  alt: RockB editorial guides
  relative: false
date: 2026-05-03 18:04:28+00:00
description: 'What Cursor Bugbot flags by default versus by rule, how repository rollout works on five hosts, whether it can replace CodeQL, and how multi-repo billing runs.'
draft: false
schema: schema-cursor-bugbot-review-2026
tags:
- cursor
- code-review
- ai-security
- bugbot
- pull-requests
- codeql
title: 'Cursor Bugbot Review 2026: Coverage, Rollout, CodeQL and Multi-Repo Billing'
lastmod: '2026-10-22T15:20:00+00:00'
---

Bugbot reviews the pull-request diff and reports bugs, security issues and code-quality problems, with an explanation and a suggested fix for each finding. Everything a buyer needs to decide on it follows from how that sentence is scoped, and the documentation answers the four procurement questions unevenly: coverage is partly built in and partly written as rules, rollout is one access grant on GitHub but a per-repository toggle on four other hosts, Bugbot is not a CodeQL replacement, and billing is now per run rather than per seat.

This page is a documentation review with a pilot design attached. It does not publish a first-hand detection benchmark, and every performance figure below is attributed to Cursor rather than measured here.

## What Bugbot flags by default, and what needs a rule

| Check | Status in Cursor's documentation | What the buyer has to do |
|---|---|---|
| Bugs in the changed code | Documented default | Nothing beyond enabling the repository |
| Security issues | Documented default | Nothing beyond enabling the repository |
| Code-quality problems | Documented default | Nothing beyond enabling the repository |
| Test regressions | Not documented as a built-in detector | Write a rule; Cursor's own example is "Require tests for backend changes" |
| House style conventions | Not documented as a built-in detector | Repository rules or a project `.cursor/BUGBOT.md` |
| Dependency CVEs, secret scanning | Not documented on the pages reviewed | Keep whatever tooling already covers them |
| Licence checks on dependency files | Built-in License Scan, but it runs only when a rule fires - not a default | Write the rule; Cursor's example blocks GPL-2.0, GPL-3.0 and AGPL-3.0 |

The documentation names three review categories and stops there. It publishes no per-category detection rate and does not enumerate which vulnerability classes the security category covers, so read the first three rows as intent plus output format, not as a measured precision claim. The licence row is the one place where a scan is built in rather than inferred from a category: Cursor's own rule example fires when a pull request touches `package.json`, `pnpm-lock.yaml`, `yarn.lock`, `requirements.txt`, `go.mod` or `Cargo.toml`, runs the built-in License Scan over the changed dependencies, and raises a blocking Bug titled "Disallowed license detected" naming the offending packages, versions and licences. Nothing on the page says that scan runs without a rule, so budget for writing it. The test-regression row is the one that decides most pilot scopes: if a team expects Bugbot to notice that a backend change arrived without tests, that behaviour has to be configured, and Cursor's published example shows a blocking Bug raised when files under `server/`, `api/` or `backend/` change without matching test files.

## The rule model: rule text, a settings file and a shared switch

Cursor's summary sentence names three rule levels - team rules, repository rules and a project-level `.cursor/BUGBOT.md` - and the same page carries two further entries: learned rules, generated from pull requests as they are merged or closed, and manual rules created per repository in the dashboard. When several of them apply, the documented order of inclusion is Team Rules, then project `.cursor/BUGBOT.md` files (including nested ones), then learned rules, then manual rules, with each rule truncated at 30,000 characters and the merged block capped at 100,000. The practical consequence is a shared switch: learned and manual rules apply only while the organisation's Automatically Learn Rules setting is on, so turning learning off also stops manual rules from applying. Azure DevOps has no such switch and keeps hand-written repository rules. Learning is not free either - each learning run counts toward Bugbot usage like a review.

The settings file is separate from the rule text: `.cursor/config/bugbot.yaml` is read only from the pull request's base branch, capped at 64 KB, and versioned (`version: 1`). Its documented keys are `triggers.drafts`, `frequency` (`everyPush` or `oncePerPr`), `review.effort` (`low`, `default`, `high`, `smart`), `review.smartPrompt`, `review.incremental`, `review.prSummary.mode` (`disabled`, `description`, `comment`), `review.riskScore` and `autofix.mode` (`disabled`, `newBranch`, `existingBranch`), so the file - not only the dashboard - decides whether a PR summary is posted, whether a risk score appears and whether reviews are incremental.

Two consequences matter operationally. First, because the YAML is read from the base branch, a pull request that adds the config does not govern itself - it takes effect on the next pull request. Second, `autofix.mode` in the file can lower the dashboard's Autofix setting but not raise it, so the file is a restriction channel, not an override channel. Documented precedence for settings in that file - which is a different list from the rule-text order above - runs personal overrides, then repository YAML, then team or organisation dashboard settings; the documentation does not describe what happens when two rule sources give contradictory instructions, so keep one owner per level.

## Onboarding: what connecting a repository actually does

There is no published onboarding duration in any primary source reviewed here, so this section counts steps and admin dependencies instead of quoting hours.

The GitHub path is a grant-and-go flow: connecting turns Bugbot on for the repositories the connector is allowed to grant, and reviews begin on the next pull request. The documented trap is administrative - repositories stay off when someone who is not a team admin connects an enterprise team. On GitLab, Bitbucket, Azure DevOps and Origin, Bugbot is enabled per repository, so the default end state after a connection is "off until toggled" rather than "on for everything granted".

A practical rollout therefore has five steps: connect the source-control account with an admin who can grant scope; confirm which repositories are actually enabled; add team rules for the checks that are not default (tests above all); decide whether the YAML file or the dashboard owns frequency and effort; and settle the CI question in the next section. The step count is the same for one repository and for fifty. What changes at fifty is who holds the grant and whether the per-repository toggle is scripted or clicked.

## Rollout at organisation scale

Split the organisation-wide work into three layers, because only one of them is genuinely central:

| Layer | Scope | Documented mechanism |
|---|---|---|
| Rule text | Team or organisation | Team rules in the dashboard; one copy governs every enabled repository |
| Enablement | Per repository on GitLab, Bitbucket, Azure DevOps and Origin; granted scope on GitHub | Repository toggle or access grant |
| Review behaviour | Per repository | `.cursor/config/bugbot.yaml` on the base branch |

That table is the answer to "how long does organisation-wide rollout take": the standard is central, the enablement is not, and the dependency sits with whoever can grant repository access. A team that cannot get an admin to grant scope can write every rule it likes and still see no reviews. Bitbucket support is listed as public beta in Cursor's source-control table, so treat it as a supported host with a qualifier rather than a first-class target.

## Can Bugbot replace CodeQL? Three products, three jobs

Comparisons usually fail here by treating one product as the whole of Cursor's review line. There are three distinct jobs, and only one of them overlaps CodeQL's at-rest role.

| Product | Trigger | Output | Where the result lives |
|---|---|---|---|
| Bugbot | Pull request opened or updated; manual `cursor review` or `bugbot run` comment | Review comments with explanations and fix suggestions; a `Cursor Bugbot` check on GitHub | The pull request thread |
| Security Reviewer (Cursor Security Agents) | Pull request and merge request events | Pre-merge review; Origin, GitHub and GitLab only | The pull request; Bitbucket and Azure DevOps reviews are routed to Bugbot by Cursor's own docs |
| Vulnerability Scanner (Cursor Security Agents) | Cron, one schedule per scanner | At-rest findings, including pre-existing issues missed in PR review | Cursor-managed scanning; scopes above roughly 1,000 repositories can hit provider rate limits and should be split |
| CodeQL / code scanning | Schedule or repository events such as a push | Code-scanning alerts, with SARIF interop for third-party tools | GitHub's alert database and security tab |

So the honest answer to "can Bugbot replace CodeQL" is no, and the honest follow-up is that Bugbot is the wrong product to compare. Bugbot sees a diff, comments on it, and its documented API covers triggering reviews and reading per-review analytics; no SARIF output, alert store or alert lifecycle appears on the Bugbot or Security Agents pages. CodeQL produces alerts from whole-codebase analysis on a schedule or event, and those alerts carry a state machine inside GitHub that security teams already report on.

Four gaps a migration has to close, each stated as a documentation gap rather than a capability verdict:

- Alert export and SARIF: neither Bugbot nor Security Agents documents a SARIF emitter or code-scanning alert export on the pages reviewed. Absence across two pages is not a documentation audit, so ask the vendor directly.
- At-rest coverage: only Vulnerability Scanner scans code that is not in a pull request, and it carries one schedule per scanner.
- Compliance evidence: audit-log retention, accepted-risk workflow and historical alert exposure were not documented on the pages read. This is usually the blocking item for regulated teams, not detection quality.
- Host and licence surface: Security Reviewer covers Origin, GitHub and GitLab only, and code scanning itself requires GitHub Code Security for private organisation repositories - a CodeQL-side constraint that survives any reviewer swap.

A buyer checklist for a pilot, in order: list the alert queries the security team actually reports on; test whether Vulnerability Scanner can schedule the same cadence per repository group; confirm where an accepted risk is recorded after the swap; confirm the audit trail the auditor accepted last year still exists; and keep CodeQL running in parallel until the first scheduled scan has produced a comparable finding set.

Do not summarise CodeQL's language and build-mode coverage from a secondary source: use GitHub's own language matrix, because a repository in an unsupported language changes the migration answer entirely.

## Multi-repository billing: usage, not seats

Bugbot moved to usage-based billing for Teams and Individual plans, announced on 2026-05-11, with existing customers transitioning at their first renewal after 2026-06-08. The familiar $40 per seat per month figure therefore describes only contracts that have not yet renewed; quoting it as the current price is a factual error. Enterprise remains custom-priced, with pooled usage on the pricing page.

Cursor reports an average run cost of $1.00 to $1.50 depending on pull-request size and complexity. That is an average with no published distribution and no repository-size bands, so multi-repository spend is arithmetic over a stated range, not a quote:

- Assumption 1: 25 engineers, four pull-request updates per engineer per working day, 20 working days: 2,000 runs per month.
- Assumption 2: one run per update, no skipped runs, no discount.
- Result: 2,000 x $1.00 to $1.50 = **$2,000 to $3,000 per month**, before any effort or frequency change.

Change either assumption and the total moves linearly. Setting `frequency: oncePerPr` cuts the run count per pull request; pull requests above the default review-size limit are skipped and record no review usage, so large-PR-heavy repositories bill less than the arithmetic suggests. Effort is itself a billing control: Cursor reports that `high` effort finds 35% more bugs than `default` while the resolution rate stays at 80%, measured on internal runs with no sample size or confidence interval published, and effort levels are documented as available on usage-based plans only. Treat the 35% as a supplier claim and do not convert it into cost per fixed bug.

## What to measure in a pilot

Use the [review scorecard](/research/content-quality-batch2-2026-10/review-scorecard.csv) and keep two change sets apart: ordinary pull requests, and a controlled set with an answer key the reviewer never receives.

| Measure | Definition |
|---|---|
| Finding precision | Confirmed valid findings / reviewed findings |
| Known-defect recall | Detected seeded defects / all seeded defects |
| Accepted fixes | Changes a reviewer verified and kept |
| Review burden | Time checking findings, including false positives |
| Cost per accepted fix | Billed pilot spend / accepted fixes |

If a one-repository pilot consumes 120 runs at $1.25, spend is $150; with 30 accepted fixes that is $5 per accepted fix before reviewer time. With no accepted fixes, report the spend and zero fixes rather than a finite ratio. Run the same measurements against the existing review process, otherwise the pilot cannot show what Bugbot added beyond tests, static analysis and human review.

## The CI gate question

On GitHub the check is named `Cursor Bugbot`, and its default conclusion is neutral when Bugbot reports findings. Requiring that status therefore does not block a merge on unresolved findings by itself. A stricter behaviour exists as `fail-on-unresolved-issues`, described conditionally as available "if available for your organization" - do not assume it is enabled in your plan, and verify it in the account before writing a policy that depends on it.

## Verdict

**Adopt now** if the repositories are on GitHub, pull-request volume is high enough that reviewers are the bottleneck, and the team will write at least the test-regression rule the product does not ship. **Run a pilot** if hosts are GitLab, Bitbucket, Azure DevOps or Origin, where enablement is per repository and Bitbucket is public beta, or if the team already depends on a CodeQL gate. **Stay on CodeQL** - and evaluate Vulnerability Scanner alongside it, not instead of it - if the security programme needs alert lifecycles, SARIF export or an audit trail that the Cursor pages reviewed here do not document.

## Revision note and sources

**Updated October 22, 2026.** Rewritten from a pilot-design page into a procurement decision page: added the documented-default versus rule-driven coverage matrix, onboarding and organisation rollout, the CodeQL comparison across three Cursor products, and usage-based billing arithmetic. Removed the superseded per-seat pricing framing and the claim that Bugbot is Cursor's only reviewer. A correction pass the same day split the licence check out of the "not documented" row, named every documented configuration key, and added the rule-inclusion order and learning switch. The publication date is unchanged; this is a refresh of the same URL.

All product statements were checked against these pages on 2026-10-22. The captures were hashed locally for the review record; this article publishes no downloadable evidence files.

- [Bugbot documentation](https://cursor.com/docs/bugbot)
- [Bugbot billing change announcement, 2026-05-11](https://cursor.com/blog/may-2026-bugbot-changes)
- [Cursor pricing](https://cursor.com/pricing)
- [GitHub: About code scanning](https://docs.github.com/en/code-security/code-scanning/introduction-to-code-scanning/about-code-scanning)
- [Cursor Security Agents](https://cursor.com/docs/security-agents)
