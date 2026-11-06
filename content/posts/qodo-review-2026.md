---
cover:
  alt: 'Qodo Review 2026: AI Code Quality Platform (Formerly CodiumAI)'
  image: /images/qodo-review-2026.png
  relative: false
date: 2026-04-26 04:02:30+00:00
lastmod: 2026-11-02 18:36:00+00:00
description: Qodo Review (formerly CodiumAI) is credit-metered AI PR review. What
  the vendor-run 60.1% F1 benchmark measures, 2026 pricing, and plugin retirement.
draft: false
schema: schema-qodo-review-2026
tags:
- ai-code-review
- qodo
- codiumai
- developer-tools
- code-quality
title: 'Qodo Review 2026: AI Code Quality Platform (Formerly CodiumAI)'
---

Qodo is an AI code review platform, documented by the vendor as "Qodo Review (v2)" and sold on credit packs rather than seats-included review quotas. Two changes in 2026 matter more than any feature list: the product no longer has a permanent free tier, and the IDE plugin that older reviews describe as a core product was retired on November 1, 2026. The 60.1% F1 score that most "Qodo review" pages quote comes from a benchmark Qodo built and ran itself, so this page separates what the vendor documents from what an independent reader can actually verify.

## What Qodo is now

Qodo's documentation index describes the platform in one line: "Qodo is the AI code quality and governance platform for engineering teams. The current product is Qodo Review (v2). Qodo supports GitHub, GitLab, Bitbucket, Azure DevOps, and Gerrit, with multi-tenant, single-tenant, and on-premises deployment models." That sentence from [docs.qodo.ai/llms.txt](https://docs.qodo.ai/llms.txt) is the most current product statement available at the top level of the vendor's documentation, and it replaces the older three-product framing (Qodo Merge, Qodo Gen, PR-Agent) that still appears in most third-party coverage.

The same docs index lists "Qodo Merge, PR-Agent, Qodo Gen, Codiumate, Qodo IDE" under historical product names, with separate pages for deprecated v1 commands and for migration. So the lineup a reader encounters in older comparisons is largely renamed or retired rather than expanded. On the CodiumAI question in this article's title: Qodo's own index lists "Codiumate" as the historical name, and no primary source reviewed here gave a corporate rebrand date, funding details, or analyst placements — this page therefore makes no claims about them.

Git provider coverage is broader than the four platforms most reviews repeat: Gerrit is listed alongside GitHub, GitLab, Bitbucket, and Azure DevOps. Self-hosted and on-premises deployment are documented as Enterprise paths, not as part of the entry plan.

## Qodo 2.0 and the multi-agent review model

Qodo announced Qodo 2.0 on 2026-02-04 in a post titled "Introducing Qodo 2.0 and the next generation of AI code review". The architecture description is specific: review work is split across specialized agents, each handling a focused responsibility with its own dedicated context instead of competing for attention in a single pass, and a judge agent then "resolves conflicts, removes duplicates, and filters out low-signal results," so only findings above a confidence and relevance threshold reach the final review ([Qodo 2.0 announcement](https://www.qodo.ai/blog/introducing-qodo-2-0-agentic-code-review/)).

That is a vendor description of its own architecture, not a measured result. No public source reviewed here documents how many agents run, how they are orchestrated, or what the judge agent's confidence threshold actually is. The practical takeaway for a buyer is narrower: the current product is multi-agent and includes a filtering stage, which is one explanation a vendor would offer for fewer low-signal comments — and one a trial can test directly on your own pull requests.

## The 60.1% F1 benchmark, read carefully

The benchmark figure comes from a Qodo methodology post published the same day, "How We Built a Real-World Benchmark for AI Code Review". The design is stated plainly: 100 real pull requests containing a total of 580 issues, evaluated by pitting the Qodo model against "7 other leading AI code review platforms", with each tool's inline comments compared against ground truth by an LLM-as-a-judge system, and Qodo reported at an F1 score of 60.1% ([benchmark methodology](https://www.qodo.ai/blog/how-we-built-a-real-world-benchmark-for-ai-code-review/)).

| Benchmark attribute | What the vendor states |
|---|---|
| Pull requests evaluated | 100 real PRs |
| Injected issues | 580 total |
| Tools compared | Qodo plus 7 others (8 total) |
| Scoring | LLM-as-a-judge against validated ground truth |
| Qodo result | F1 60.1%; recall 56.7% |
| Artifacts | Said to be public in Qodo's benchmark GitHub organization |

Three qualifications belong next to that table. First, the defects are injected by the vendor into merged PRs, so the ground truth reflects Qodo's own selection of bug classes rather than a neutral corpus. Second, the judge is an LLM, so scoring inherits that model's judgment. Third, the prose reviewed here does not name the seven compared tools, and the announcement separately attributes the 60.1 F1 to a recall-optimized "exhaustive mode" while also presenting 60.1 as Qodo's headline overall F1 — an ambiguity readers should treat as unresolved rather than pick a side on.

None of that makes the number meaningless; it makes it a vendor benchmark. Use it to compare configurations Qodo ships, not to rank Qodo against tools you have not measured on your own code. Any page claiming an "independent" eight-tool benchmark with per-competitor scores, including a specific GitHub Copilot catch rate, is going beyond what Qodo's own posts state.

## Pricing: a 14-day trial, then credits

The pricing page states the model without hedging: "We don't offer a permanent free tier. After your trial, pick a paid plan to keep reviewing." The trial itself is 14 days with unlimited reviews and unlimited credits and no credit card required, with the page adding that "A credit card is only required when you pick a paid plan."

After the trial, cost is metered in credits rather than per seat. The page's own price line reads "$.012/credit, pooled across the team" — rendered with no leading zero, which reads as a display typo for $0.012 rather than a deliberate price. Credit packs are listed at 2,500, 5,000, and 20,000 credits, shown as roughly 18, 36, and 144 reviews per month, with the ability to "switch packs anytime" and "no annual commitment on Pro Team plan" ([Qodo pricing](https://www.qodo.ai/pricing/)).

| Plan | What the page shows | Notes |
|---|---|---|
| Free 14 Day Trial | Unlimited reviews, unlimited credits, no credit card | Ends after 14 days |
| Pro Team | $30, monthly billing, no commitment, "Designed for up to 30 users" | Credit packs 2,500 / 5,000 / 20,000 (~18 / ~36 / ~144 reviews/mo), customer-set monthly overage cap, strict data retention |
| Enterprise | Custom, "For 30+ users" | SSO/SAML and audit logs, governance analytics, BYOK, single-tenant SaaS or on-prem |

Two cautions on that table. The "$30" figure appears without a unit on the rendered page, so treat it as the listed starting price and confirm whether it is per user at checkout before budgeting. And "reviews per month" is the vendor's own approximation: a credit is drawn per review with smaller PRs drawing fewer and larger or more complex reviews drawing more, which the page states explicitly in its credit FAQ. A team whose PRs sit at the large end will land well below the headline review counts.

## Open source: PR-Agent is not the free tier

The repository that most reviews call "Qodo's open-source foundation" now describes itself differently: "PR-Agent is an open-source, AI-powered code review agent and a community-maintained legacy project of Qodo. It is distinct from Qodo's primary AI code review offering" ([PR-Agent README](https://raw.githubusercontent.com/The-PR-Agent/pr-agent/main/README.md)). The GitHub repository description is even more direct — "This project is not the Qodo free tier" — and the code sits under The-PR-Agent, not Qodo's own organization, at roughly 13.9k stars as of 2026-11-02T18:26Z ([repository metadata](https://api.github.com/repos/The-PR-Agent/pr-agent)).

Operationally, PR-Agent remains a genuine self-hosting option: MIT-licensed and not archived, deployable as a CLI, GitHub Action, Docker image, self-hosted service, or webhook receiver, and pointed at any model reachable through LiteLLM, including Azure OpenAI, AWS Bedrock, Vertex AI, Databricks, OpenRouter, and Ollama. What it is not is a route to free Qodo Review: it is a separate, community-maintained codebase, so its review quality and roadmap are not the same product you are evaluating in a Qodo trial. This page quotes no per-review API cost estimate for self-hosting, because none was measured here.

## What to check in a trial

The trial is the only place where the vendor's claims meet your repository, and four checks cover most of the risk:

- **Credit burn per PR.** The dashboard reports real-time balance and burn rate; record credits consumed across your ten largest and ten smallest recent PRs before choosing a pack size.
- **Overage behaviour.** Pro Team exposes a customer-set monthly overage cap — set it below your approved budget before the first billing cycle, not after.
- **Local and pre-PR workflows.** The IDE plugin retired on November 1, 2026 and no longer functions, including in existing installations; plugin settings, chat history, custom review agents, and rules are not retained or migrated, and users are directed to the Agentic Toolbox for local review ([deprecation entry](https://docs.qodo.ai/llms.txt)). Confirm the replacement covers whatever the plugin used to do for your team.
- **Defect mix.** Qodo's benchmark injects defects into real PRs; if your risk concentrates in a class the benchmark does not target, the 60.1 F1 figure says little about your experience.

## FAQ

**Is Qodo free?** No. There is a 14-day trial with unlimited reviews and no credit card, and the pricing page states plainly that there is no permanent free tier after it.

**Is the 60.1% F1 benchmark independent?** No. Qodo designed, ran, and published it, including the injected defects and the LLM judge. It has not been independently reproduced in the sources reviewed here.

**Does the Qodo IDE plugin still work?** No. It was retired on November 1, 2026 and no longer functions in any plan or deployment type; pull request review is unaffected.

**Is PR-Agent the same as Qodo Review?** No. PR-Agent is a community-maintained legacy open-source project under The-PR-Agent, distinct from Qodo's current review product and explicitly described by its maintainers as not the Qodo free tier.
