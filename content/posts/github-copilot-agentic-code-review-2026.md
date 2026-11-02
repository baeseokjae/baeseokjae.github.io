---
cover:
  alt: 'GitHub Copilot code review: plans, setup and cost per review'
  image: /images/github-copilot-agentic-code-review-2026.png
  relative: false
date: 2026-05-23 18:01:19+00:00
description: Copilot code review is on every paid Copilot plan, not just Business. What it does, how to enable it, which fix path is preview, and what a review costs.
draft: false
lastmod: '2026-10-30T15:25:08+00:00'
schema: schema-github-copilot-agentic-code-review-2026
tags:
- github-copilot
- code-review
- ai
- pull-request
- devtools
title: 'GitHub Copilot Code Review: Plans, Setup, and Cost (2026)'
---

GitHub Copilot code review reads the changes in a pull request and posts comments tagged High, Medium, or Low severity. It is supported on GitHub.com, GitHub CLI, GitHub Mobile, VS Code, Visual Studio, Xcode and JetBrains IDEs, with Azure DevOps in public preview. It is included in every paid Copilot plan and excluded from Copilot Free.

Two details decide whether you can adopt it as it stands. By default Copilot submits a "Comment" review rather than an approval, so a branch rule that requires an approving review is not satisfied by Copilot until you configure it to approve. And the autonomous fix path is not generally available: passing suggestions to Copilot cloud agent is documented as public preview and subject to change. The [concepts page](https://docs.github.com/en/copilot/concepts/agent-capabilities/agent-powered-workflows-and-operations/code-review) states both facts directly.

## What the review does, and what it does not

Copilot reviews code in any language and comments on it from multiple angles. Where it can, it attaches a suggested change you apply with a couple of clicks — one suggestion at a time, or several together in a single commit. Comments behave like human review comments: you can react to them, reply, resolve them and hide them. Anything you write in reply is visible to people but not to Copilot, and Copilot does not answer.

The "agentic" label refers to two documented capabilities: full project context gathering, which analyses the whole repository instead of only the diff, and the handoff of suggestions to Copilot cloud agent. Both are switched on automatically for plans that include code review. If GitHub Actions is unavailable, or the workflows Copilot code review uses fail, reviews are still produced — they simply lose the agentic extras. That degradation behaviour comes from the same [concepts page](https://docs.github.com/en/copilot/concepts/agent-capabilities/agent-powered-workflows-and-operations/code-review), and it is the reason a review can look thinner on a repository whose Actions configuration is locked down.

## Which plan you actually need

The most common stale claim about this feature is that it requires Copilot Business or Enterprise. It does not. GitHub's own plan line for the feature reads "Available for all paid Copilot plans", and the [billing documentation](https://docs.github.com/en/billing/concepts/product-billing/github-copilot-licenses) supplies the list prices.

| Plan | List price | Code review included |
|---|---|---|
| Copilot Free | No cost, limited features | No |
| Copilot Pro | $10 per calendar month | Yes |
| Copilot Pro+ | $39 per calendar month | Yes |
| Copilot Max | $100 per calendar month | Yes |
| Copilot Business | $19 per user per month, billed monthly | Yes |
| Copilot Enterprise | Two licensing models: no Copilot seat charge through GitHub Enterprise Cloud, or Copilot Standalone at $10 per user per month | Yes |

Enterprise is sold under two licensing models, so no single seat price covers both. The Copilot access plan provides Copilot through GitHub Enterprise Cloud with no Copilot seat charge, or as Copilot Standalone for $10 USD per user per month without a GitHub Enterprise Cloud license; it carries no included usage allowance, is rolling out to eligible enterprises, and moving to it is voluntary. Enterprises that stay on Copilot Business or Copilot Enterprise pay a monthly fee per assigned seat, and the billing page points readers to a separate page for enterprise eligibility, pricing and a comparison of the two models. Prices here are list prices in USD as published on the billing page on 30 October 2026; treat them as dated.

### Reviews for people who hold no license

Organizations on Business or Enterprise can also let members who have no Copilot license use code review on GitHub.com — not in IDEs. Two policies must be enabled, in order: "AI credits paid usage" first, which allows the organization or enterprise to incur charges, then "Allow members without a Copilot license to use Copilot code review in GitHub.com". The second policy is disabled by default, is the most restrictive setting, and once it is set at enterprise level it is visible but not editable at the organization level. It applies only in repositories under an organization where the policy has been enabled explicitly.

Those users get no monthly AI-credit allowance for code review. Their consumption is billed to the organization or enterprise as paid additional usage and is not attributed to any individual's budget.

## Turning it on

1. **Check the organization policy first.** If you receive Copilot through an organization, that organization must enable the Copilot code review option in its policy settings; this gates reviews on GitHub.com and GitHub Mobile.
2. **Request a review manually.** On a pull request, open the Reviewers sidebar and click Request next to Copilot. GitHub states this usually takes less than 30 seconds. The [how-to page](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/request-a-code-review/use-code-review) also documents requesting `copilot-pull-request-reviewer[bot]` as a reviewer through the REST API.
3. **Or automate it.** Automatic review is configured in three separate places: a user setting, available on Pro, Pro+, Max and with Business or Enterprise licenses but not for managed user accounts; a repository ruleset; and an organization ruleset. User settings and ruleset configuration are evaluated separately — neither inherits from nor overrides the other.
4. **Set the effort default.** Repository and organization administrators choose the default review effort level used for automatic reviews.
5. **Verify on a throwaway pull request.** Confirm the review arrives, that severity labels appear, and whether your ruleset treats a Comment review as satisfying a required approval.

One interaction is easy to miss. In personal repositories only the owner or a direct collaborator can request a review, and automatic reviews from personal settings do not run for people who are not authorized — but automatic reviews configured by repository or organization rulesets still run. If you enable automation before agreeing on budgets, reviews can start spending without any individual opting in.

## The fix path: what is stable and what is preview

"Fix with Copilot" is the button on a review comment. Clicking it creates a draft comment where you describe what to change; you then choose whether Copilot opens a new pull request against your branch or commits to the current pull request. Two features must be enabled first: Copilot code review and Copilot cloud agent.

Treat that handoff as a pilot, not as infrastructure. GitHub labels passing suggestions to Copilot cloud agent as public preview and subject to change, so a workflow that depends on it can change without notice. The step that is stable is the plain suggestion you accept yourself — inline, applied in a click or two, committed singly or as a group.

## What a review costs

Two meters run, and they are billed separately. AI credits pay for the model interaction; the amount depends on the model used and the number of tokens processed. GitHub Actions minutes pay for the agentic capabilities. A quoted per-review credit figure is therefore not the whole bill.

| Review effort level | Typical range per review | Approximate average |
|---|---|---|
| Lite | $0.05 to $1.00 | $0.25 |
| Balanced | $0.25 to $5.00 | $1.50 |
| Max | $1.50 to $25.00 | $10.00 |

GitHub describes these as estimates only. Consumption generally increases with pull request size and with repository custom instructions, actual costs can fall outside the ranges, and the figures may change as models evolve. The table explicitly excludes GitHub Actions minutes, so read the credit numbers as the first of two line items, not as a per-review price.

Agentic steps run on standard GitHub-hosted runners by default. Larger GitHub-hosted runners are available and are billed at a higher per-minute rate; self-hosted runners consume no Actions minutes. If an organization has disabled GitHub-hosted runners, the agentic capabilities become unavailable and reviews fall back to the more limited review. The feature degrades rather than failing, and the documentation does not say that a degraded review is labelled as such, so compare a fallback review against a normal one before relying on either.

### A worked range

Take 200 reviews a month at Balanced effort and use only GitHub's published ranges. The AI-credit component works out to 200 × $0.25 = $50 at the low end and 200 × $5.00 = $1,000 at the high end, before Actions minutes. The same volume at Lite effort is 200 × $0.05 = $10 to 200 × $1.00 = $200. The spread is the point: the published range is more than an order of magnitude wide, so a team planning a budget needs its own distribution from real pull requests rather than an average.

Attribution follows who asked. An automatic review requested by a repository setting is billed to the pull request author; a review a person requests manually is billed to that person; pull requests authored by bots, or reviews requested by a bot, are billed to the organization. On Business and Enterprise, budgets govern access: when the applicable user budget, organization budget, cost center budget or enterprise spending limit is exhausted, code review is blocked along with the other AI-credit features.

## Limits worth knowing before you enable it

- **Default approvals.** Unless configured otherwise, Copilot's Comment review does not count toward required approvals for the pull request.
- **No model choice.** Model switching is not supported; Copilot code review uses a fixed mix of models and prompts. It may use models that are not enabled on your organization's Models settings page, because that page only controls Copilot Chat.
- **Actions dependency.** Without Actions, reviews still arrive, but without repository-wide context gathering or the cloud-agent handoff.
- **One-way conversation.** Replies you write on Copilot's comments are for humans; Copilot does not read them or respond.
- **Free tier excluded.** Copilot Free does not include code review, and users on it have no AI-credit allowance for it.

## A short adoption checklist

1. Confirm the plan tier and, for Business or Enterprise, decide whether you want the no-license path — and budget for it, since those reviews are additional usage.
2. Turn on the organization policy before changing repository settings.
3. Choose a default effort level deliberately; start low and raise it only where review quality on real pull requests justifies the cost.
4. Enable automatic review on the branches that matter rather than everywhere, so volume stays predictable.
5. Set budgets and confirm attribution, especially if bots open pull requests in your repositories.
6. Run ten real pull requests, then read the AI-credit and Actions-minute lines in billing instead of extrapolating from the published table.
7. Decide explicitly whether Copilot's review should count as an approval. By default it does not.

## What changed in this revision, and why

This page was first published on 23 May 2026 and substantially revised on 30 October 2026 after re-checking GitHub's documentation. Five corrections matter to anyone who saw the earlier version. Code review was described as requiring a Business or Enterprise subscription; it is available on all paid plans, with Free excluded. The autonomous fix was described as generally available; the cloud-agent handoff is in public preview. Billing was described as Actions minutes converted into AI credits from 1 June 2026; the documented model is two separate components, AI credits for the review and Actions minutes for the agentic steps. And figures for review volume, the share of actionable comments, average comments per review, and competitor catch rates were withdrawn — none had a primary source, and vendor-reported rates built on different denominators cannot be compared as though they shared a method. The enterprise row also said the billing page published no per-user figure; it does publish Copilot Standalone at $10 USD per user per month and no Copilot seat charge through GitHub Enterprise Cloud, so both licensing models are now stated instead of a single seat price.

If you are budgeting this against the rest of your Copilot spend, the [Copilot usage metrics guide](/posts/copilot-usage-metrics-accuracy-coverage-guide-2026/) covers how to read consumption reporting after you switch it on.

## Sources

- [GitHub Docs — GitHub Copilot code review (concepts)](https://docs.github.com/en/copilot/concepts/agent-capabilities/agent-powered-workflows-and-operations/code-review), checked 30 October 2026
- [GitHub Docs — Using GitHub Copilot code review](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/request-a-code-review/use-code-review), checked 30 October 2026
- [GitHub Docs — GitHub Copilot licenses (billing)](https://docs.github.com/en/billing/concepts/product-billing/github-copilot-licenses), checked 30 October 2026

No live Copilot review was executed for this article: no licensed repository was available while it was written. Everything above is documented behaviour and published list pricing, re-checked on the date shown. Where the documentation does not publish a number — a latency distribution, a measured cost distribution, a catch rate — this page does not supply one.
