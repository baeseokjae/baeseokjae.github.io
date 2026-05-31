---
title: "JetBrains AI Tools Survey 2026: Key Findings for Dev Teams"
date: 2026-05-31T09:05:36+00:00
tags: ["ai-tools", "developer-survey", "github-copilot", "claude-code", "cursor", "productivity"]
description: "JetBrains AI Pulse survey of 10,000+ developers reveals 90% adoption, Claude Code's explosive rise, and the real productivity paradox."
draft: false
cover:
  image: "/images/jetbrains-survey-ai-tools-2026.png"
  alt: "JetBrains AI Tools Survey 2026: Key Findings for Dev Teams"
  relative: false
schema: "schema-jetbrains-survey-ai-tools-2026"
---

JetBrains' April 2026 AI Pulse survey of over 10,000 professional developers is the most rigorous snapshot of AI tool adoption available: 90% of developers now use at least one AI tool at work, Claude Code jumped from 3% to 18% work usage in under a year, and a longitudinal behavior study reveals developers are editing far more code than they realize.

## JetBrains April 2026 Survey: Methodology and Why It Matters

The JetBrains AI Pulse survey is one of the most credible data sources on AI tool adoption in software development. Conducted across 10,000+ professional developers in January 2026, it combines self-reported survey responses with the JetBrains HAX Study — a longitudinal analysis of two years of IDE log data from 800 developers (400 AI users, 400 non-users). This dual methodology separates JetBrains' research from typical vendor surveys: it captures actual behavior, not just what developers believe they're doing. JetBrains runs the survey as part of their AI Pulse series, with data points collected in April–June 2025, September 2025, and January 2026 — giving a true time-series view of how the market evolved. The company also publishes quarterly awareness and usage metrics across all major AI coding tools, making it the closest thing to an independent audit of market share in this space. 88 Fortune Global Top 100 companies use JetBrains tools, so the respondent pool skews toward professional developers in real enterprise contexts, not hobbyists.

The longitudinal design matters because perceptions diverge sharply from logged behavior. Developers consistently overestimate how productively they use AI and underestimate how much code they delete or rewrite. Methodology details are published alongside the findings, making it possible to audit sample bias and weight regional data. For dev teams making tooling decisions, the JetBrains survey is a more reliable benchmark than GitHub's self-reported Copilot metrics or vendor-sponsored productivity claims.

## Overall AI Adoption: 90% of Developers Now Use AI Tools at Work

AI tool adoption among professional developers reached an inflection point by January 2026: 90% of developers in the JetBrains survey regularly used at least one AI tool at work, up from roughly 76% in prior-year data. Among that group, 74% had adopted specialized AI tools built specifically for developers — as opposed to general-purpose chatbots like ChatGPT used informally. 51% of professional developers use AI tools daily, and nearly 9 in 10 who use AI report saving at least one hour per week; 1 in 5 saves 8 or more hours weekly. These numbers mark a qualitative shift: AI tools are no longer an experiment for early adopters but a baseline expectation of professional software development workflows in 2026.

The data also reveals tool consolidation isn't happening. Most developers use three or more AI tools concurrently — a general LLM chatbot for open-ended questions, an IDE-integrated tool for code completion, and increasingly an agentic tool for larger task automation. This fragmentation has real implications for team leads: standardizing on a single tool reduces friction and simplifies license management, but developers gravitate to different tools for different tasks. Teams that mandate one tool often see shadow usage of others anyway. The 90% adoption number sets the new baseline for team expectations: if you're not providing licensed AI tooling, developers are almost certainly using personal accounts or free tiers.

## Market Share Breakdown: GitHub Copilot, Claude Code, Cursor, and the Rising Challengers

GitHub Copilot leads on absolute market share but is losing ground at the top: 76% awareness and 29% work usage globally, with its strongest position in large enterprises (40% usage at companies with 5,000+ employees). Cursor and Claude Code are now tied at 18% work usage each, representing dramatically different trajectories. Cursor has 69% awareness and the highest conversion rate of any tool at 35.5% — meaning more than one-third of developers who know about Cursor end up using it at work. Claude Code grew from 31% awareness in April–June 2025 to 57% awareness by January 2026, an 84% increase in eight months, while work usage went from under 5% to 18% in the same period. Claude Code leads all tools on loyalty metrics: 91% customer satisfaction (CSAT) and a Net Promoter Score of 54.

| Tool | Awareness | Work Usage | Conversion Rate | Notable Metric |
|------|-----------|------------|-----------------|----------------|
| GitHub Copilot | 76% | 29% | 23.7% | 40% usage in 5,000+ employee firms |
| Cursor | 69% | 18% | 35.5% | Highest conversion rate |
| Claude Code | 57% | 18% | ~31.6% | 91% CSAT, 54 NPS (best loyalty) |
| Google Antigravity | ~30% | 6% | — | 120% YoY awareness growth |

Cursor's commercial trajectory confirms the market position: $2B+ ARR as of February 2026, $29.3B valuation, 1M+ daily active users, with enterprise accounting for 60% of revenue. GitHub Copilot has approximately 20M total users and 4.7M paid subscribers. Claude Code's usage skews heavily toward US and Canada (24% work usage vs. 18% globally), suggesting the North American enterprise market is its current stronghold. Google Antigravity reached 6% adoption since launching in November 2025, with 120% year-over-year awareness growth — the fastest growth rate of any tool tracked in the survey, driven by the Google ecosystem, a free preview strategy, and multi-agent parallel processing capabilities.

## The Productivity Paradox: What Developers Perceive vs. What the Data Shows

The most provocative finding in JetBrains' 2026 research is the gap between perceived and measured productivity. Over 80% of developers in the survey reported that AI slightly or significantly increased their productivity. 50% said coding time decreased after AI adoption. Yet the JetBrains HAX Study — measuring actual logged IDE behavior over two years — found that experienced developers were 19% slower on task completion when using AI tools, despite perceiving themselves as 20% faster. This perception-reality inversion is the central productivity paradox: developers feel faster because AI removes the blank-page friction of starting a task, but the total cycle time (including review, correction, and integration of AI suggestions) often runs longer than writing the code themselves.

The HAX behavioral data makes the mechanism visible. AI users increased characters typed by approximately 600 per month compared to 75 for non-users — a 700% increase in raw editing activity. AI users also increased code deletions by roughly 100 per month versus 7 for non-users. Developers are writing and deleting dramatically more code, but they don't perceive this as extra work because AI is generating most of the initial draft. The result is a workflow that feels productive (you're always moving) but involves more total editing effort than developers realize. Context switching slightly increased despite AI tools being marketed as a way to reduce interruptions. Debugging behavior showed no significant change despite quality perception improvements. The implication for engineering managers: productivity gains from AI are real but uneven, and self-reported velocity metrics will be systematically inflated by developers who feel faster than they are.

## Code Quality Trade-offs: Increases, Decreases, and Hidden Rework Costs

Code quality outcomes from AI adoption are polarized: 43.5% of developers in the JetBrains survey reported quality increased after AI adoption, 6.5% said it decreased, and 50% saw no change. The aggregate number looks positive, but the HAX Study reveals a hidden rework cost that the survey doesn't capture. One in five lines of accepted AI code is later deleted. Seven percent of accepted AI code is heavily rewritten within a short window after acceptance. This means the true acceptance rate for AI suggestions — code that stays in production largely as written — is considerably lower than raw acceptance rate metrics suggest.

Structural quality signals confirm the concern. Code churn rose from 3.1% in 2020 to 5.7% in 2024, and code duplication increased from 8.3% to 12.3% of changed lines between 2021 and 2024. These trends correlate with the period of rapid AI tool adoption. The HAX Study explicitly notes no significant change in debugging behavior despite developers reporting quality perception improvements — meaning developers feel like they're writing better code but their debugging cadence hasn't changed. For teams evaluating AI tool ROI, this data suggests tracking post-merge churn and duplication rates alongside self-reported productivity. Over-indexing on "lines of code written" or "suggestions accepted" as success metrics will systematically miss the rework cost that eats into the productivity gain.

## Enterprise Considerations: Security, Trust, and Procurement Patterns

Enterprise AI adoption is structurally different from individual developer adoption, and the JetBrains data surfaces two critical gaps: security concern and trust decline. 81% of developers reported being concerned about security and data privacy when using AI agents — a number that rises in regulated industries and organizations with strict data residency requirements. Only 29% of developers trust AI outputs to be accurate as of 2026, down from 40% in 2024. As developers gain more experience with AI tools and observe failures firsthand, calibrated skepticism is growing. This trust decline is healthy from a quality standpoint but creates friction in workflows that assume AI suggestions can be accepted without deep review.

Enterprise procurement patterns reflect GitHub Copilot's structural advantage: its 40% usage rate at companies with 5,000+ employees is nearly double its global average, driven by GitHub Enterprise licensing bundles, SSO integration, and audit trail capabilities that procurement teams require. Claude Code's 24% work usage in North America suggests Anthropic is making inroads with enterprise security and data handling commitments, but lacks GitHub's enterprise sales motion and existing toolchain integration. Cursor's 60% enterprise revenue share is notable given that Cursor is a standalone product rather than an integrated platform — it suggests enterprises are willing to pay for a differentiated IDE experience even without bundled licensing. For dev teams advising procurement: tool choice at scale should evaluate API data handling policies, audit logging, SSO/SCIM support, and per-seat pricing at volume — capabilities where Copilot currently has the most mature story, Claude Code is investing heavily, and Cursor is earlier in the journey.

## How Dev Teams Should Act on This Data in 2026

The JetBrains survey provides actionable guidance for four distinct decisions dev teams face in 2026. First, on tool standardization: the 90% adoption baseline means you're not choosing whether developers use AI — you're choosing whether they use licensed, policy-compliant tools or personal free-tier accounts with no data handling guarantees. Formalizing a supported tool list with clear data policy documentation is now a baseline IT and security responsibility, not an optional perk. Second, on productivity measurement: the HAX Study data makes it clear that self-reported productivity metrics and suggestion acceptance rates are insufficient. Teams need to track post-merge churn rates, code duplication trends, and debugging cycle times to get a complete picture of whether AI tools are improving or complicating net output.

Third, on tool selection by team profile: GitHub Copilot is the lowest-friction enterprise choice for organizations already on GitHub Enterprise with existing security reviews in place. Cursor is the best conversion-rate bet for developers who want an AI-native IDE experience and have flexibility in toolchain choice. Claude Code is the right bet for teams doing heavy agentic or multi-step automation workflows, where its loyalty metrics (91% CSAT, 54 NPS) and North American enterprise traction signal real differentiation. Fourth, on the trust gap: with only 29% of developers trusting AI output, the workflow bottleneck for most teams isn't generating AI suggestions — it's reviewing them efficiently. Investing in code review tooling, AI output linting, and team norms around how to evaluate AI suggestions is likely a higher-leverage intervention than switching tools again.

---

## FAQ

**Q1. What was the sample size of the JetBrains AI Pulse survey in 2026?**
The January 2026 JetBrains AI Pulse survey covered 10,000+ professional developers across multiple geographies. It also incorporates the JetBrains HAX Study, which analyzed two years of IDE log data from 800 developers (400 AI users, 400 non-users) for behavioral measurement alongside the survey responses.

**Q2. Which AI coding tool has the highest market share in 2026?**
GitHub Copilot leads on absolute work usage at 29% globally, rising to 40% at companies with 5,000+ employees. Claude Code and Cursor are tied at 18% work usage each. Cursor has the highest conversion rate (35.5%), while Claude Code has the strongest loyalty metrics with 91% CSAT and a 54 NPS.

**Q3. Is Claude Code actually better than GitHub Copilot for enterprise teams?**
They serve different strengths. GitHub Copilot has the most mature enterprise security, audit logging, and SSO integrations, making it the lower-friction choice for large organizations already on GitHub Enterprise. Claude Code leads on user satisfaction and loyalty, and its agentic workflow capabilities outperform Copilot for multi-step automation tasks. The right answer depends on your team's workflow complexity and existing toolchain.

**Q4. Why are developers saying AI makes them more productive if studies show they're slower?**
The perception gap is explained by the blank-page effect: AI removes the most aversive part of coding (starting from scratch), making work feel faster even when total cycle time increases. The JetBrains HAX Study shows developers editing and deleting far more code than they realize when using AI — the system feels productive because you're always moving, but reviewed and finalized output often takes longer overall.

**Q5. How should teams measure AI tool ROI beyond self-reported productivity?**
Track post-merge code churn rates (lines changed or deleted within a short window after merge), code duplication percentage trends, and debugging cycle times. Self-reported productivity and AI suggestion acceptance rates systematically overstate value because they miss the rework cost: one in five accepted AI suggestions is later deleted, and 7% is heavily rewritten. Combine behavioral metrics with survey data to get an accurate picture.
