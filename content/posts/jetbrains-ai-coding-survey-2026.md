---
cover:
  alt: 'JetBrains AI Coding Tools Survey 2026: What 74% Adoption Really Means'
  image: /images/jetbrains-ai-coding-survey-2026.png
  relative: false
date: 2026-05-20 03:07:13+00:00
description: "JetBrains' January 2026 AI Pulse survey: 74% adopted specialized AI dev tools, but 18% per product. What each percentage measures and how to compare tools."
draft: false
lastmod: 2026-10-20
schema: schema-jetbrains-ai-coding-survey-2026
tags:
- ai-coding-tools
- developer-survey
- github-copilot
- claude-code
- cursor
title: 'JetBrains AI Coding Survey 2026: What 74% Adoption Really Means'
---

Two numbers from JetBrains Research get quoted side by side and look like a contradiction: 74% of developers have adopted specialized AI developer tools, and 18% use Claude Code or Cursor at work. Read as a single claim, that implies the category is three times bigger than the tools inside it, or that one percentage must be wrong.

Neither percentage is wrong. They answer different questions about different denominators, and the difference is exactly what you need to understand before quoting either one in a tool-selection decision.

## What the January 2026 AI Pulse survey actually measured

JetBrains Research ran the second wave of its AI Pulse survey in January 2026: a questionnaire localized into eight languages, completed by more than 10,000 professional developers worldwide, with roughly 90% of respondents falling into the Developer / Programmer / SWE job category. Recruitment ran through Instagram ads aimed at developers and coding professionals, Zhihu in China, and JetBrains' own research panel, which supplied roughly 16% of responses. The promotion and survey description deliberately avoided mentioning AI, so the sample would not skew toward AI enthusiasts or skeptics.

The results were weighted by raking against the Developer Ecosystem Survey 2025 along three dimensions: number of developers by region, coding experience, and familiarity with JetBrains products. That third dimension is the one to keep in mind when you read JetBrains' own product numbers, and the absence of company size from the weighting list matters if you want to generalise to enterprise populations.

Two dates matter here and are often merged into one. The data was fielded in January 2026; the article reporting it was published in April 2026. Growth comparisons in the post are against a September 2025 wave and an April–June 2025 wave.

Primary source: [Which AI Coding Tools Do Developers Actually Use at Work?](https://blog.jetbrains.com/research/2026/04/which-ai-coding-tools-do-developers-actually-use-at-work/) (JetBrains Research, Mikhail Bogdanov).

## Three denominators: 90%, 74%, and 18%

The three headline figures are nested, not competing:

| Figure | What it counts | Population |
|---|---|---|
| 90% | Regularly used at least one AI tool at work for coding and development tasks, chatbots included | All developers, January 2026 |
| 74% | Had adopted specialized AI tools for developers — assistants, editors, agents — explicitly "not just chatbots like ChatGPT" | All developers, January 2026 |
| 18% | Used one specific product (Claude Code, or Cursor) for work | All developers, January 2026 |

The 74% figure is the category figure: it says three-quarters of developers have picked up at least one specialized tool. The 18% figure is a per-product figure, and in this wave it happens to be shared by Claude Code and Cursor, which now tie for second place behind GitHub Copilot. If you need a sentence for a slide, "roughly three in four developers use specialized AI coding tools, and roughly one in five uses any given leading agent" is the accurate version. "18% of developers use AI coding tools" is not.

## Tool-by-tool adoption at work

GitHub Copilot remains the most widely known and most widely used specialized tool: 76% awareness and 29% adoption at work, with growth in both awareness and adoption stalled since the previous year. JetBrains also reports that Copilot is adopted by 40% of developers in companies with over 5,000 employees — a company-size-scoped figure that should not be quoted as a global adoption number, and one that uses a 5,000-employee threshold, not 10,000.

| Tool | Awareness | Work adoption |
|---|---|---|
| GitHub Copilot | 76% | 29% |
| Claude Code | 57% | 18% |
| Cursor | 69% | 18% |
| OpenAI Codex | 27% | 3% |
| Google Antigravity | not published | 6% |
| JetBrains AI Assistant | not published | 9% |
| JetBrains Junie | not published | 5% |

Cursor is still the second most well-known AI dev tool at 69% awareness, but its growth in both awareness and adoption has slowed; its 18% work adoption is now level with Claude Code rather than ahead of it. JetBrains reports 11% of developers using JetBrains AI Assistant and/or Junie, which decomposes into 9% for AI Assistant and 5% for Junie — the gap between 11% and 14% is direct evidence of overlap between products. Antigravity, launched by Google in November, reached 6% adoption by January 2026. Codex's 3% is explicitly time-bound: JetBrains notes the figure predates the Codex desktop app launch and its promotion inside ChatGPT.

Chatbots are a separate surface and belong in their own table, not merged into the tool column: 28% of developers use the ChatGPT chatbot for coding work, 8% use Gemini, and 7% use Claude's chatbot. None of those numbers can be added to a coding-agent number, because they measure a different interface to a related model.

## Why the tool percentages cannot be summed

Adding Copilot's 29%, Claude Code's 18%, Cursor's 18%, Codex's 3%, Antigravity's 6% and the JetBrains tools already overshoots 74%, and the overshoot is the point: developers use more than one tool, so per-tool adoption rates describe overlapping populations. JetBrains publishes aggregates rather than microdata, so the size of any pairwise overlap is not available; the 11% union for AI Assistant and Junie is the only overlap figure the post exposes.

The practical consequence for procurement is that per-tool percentages answer "how common is this tool?" and never "what share of the category does this tool hold?" You can rank tools by adoption; you cannot compute market share by division.

## What the growth numbers do and do not say

Claude Code is the clearest growth story in the dataset: awareness of 31% in April–June 2025, 49% in September 2025, and 57% in January 2026, alongside work adoption of 18% — which JetBrains describes as a 1.5x increase over September 2025 and a 6x increase over roughly 3% in April–June 2025. Two cautions apply. The September 2025 level is not printed in the post; it is derivable as approximately 12% from the stated 1.5x, so it should be labelled as derived. And the 6x is JetBrains' own rounding of roughly 3% up to 18%.

Geographic detail is available for one tool only: Claude Code reaches 24% adoption in the US and Canada, against 18% globally. JetBrains also reports Claude Code's product loyalty metrics as the highest on the market, with CSAT of 91% and NPS of 54 on a -100 to +100 scale. No CSAT or NPS figures for Copilot, Cursor or any other tool appear in this post, so any comparative satisfaction ranking built on this source alone is unsupported — the 91% and 54 describe Claude Code users and nothing else.

## Corrections to earlier versions of this article

This article was originally published on 20 May 2026 and has been corrected against the primary sources. Readers who cited the earlier text should update the following:

- The earlier version presented 18% as the adoption rate for specialized coding tools as a category. The category figure is 74%; 18% is a per-product rate shared by Claude Code and Cursor.
- Cursor's awareness was given as approximately 55%. JetBrains reports 69%.
- A "120% growth rate" for Google Antigravity and a Cursor CSAT of approximately 85% appeared in the earlier text. Neither figure is in the cited source; both have been removed.
- A 75% startup versus 56% enterprise split attributed to this survey has been removed. Those numbers did not appear in the cited JetBrains sources.
- Claims that roughly 9 in 10 developers save at least an hour a week, and that 40% of less-experienced developers find reviewing AI code takes more effort than writing their own, could not be located in the cited companion report and have been removed rather than re-attributed.
- The methodology section previously said responses were weighted by developer seniority and company size. The stated weighting dimensions are region, coding experience, and familiarity with JetBrains products.

## What the companion workflow-impact report does say

JetBrains' separate workflow-impact article combines IDE telemetry with a survey of 62 professional developers who already use AI tools, and its survey results are narrower than the numbers often attributed to it. Over 80% of those respondents reported that AI coding tools slightly or significantly increased their productivity, while two respondents reported a decrease. On code editing, about half reported no perceived change in their editing behaviour since adopting AI tools, about 40% reported a slight or significant increase, and about 7% reported a decrease.

Those figures come from a 62-person self-report survey, not from the 10,000+ AI Pulse sample, and they describe perceived change rather than measured throughput. Any claim that a specific number of hours per week are saved does not appear in the report as published.

Primary source: [AI Impact on Developer Workflows](https://blog.jetbrains.com/research/2026/04/ai-impact-developer-workflows/).

## How to use these numbers when choosing tools

Three rules keep this dataset from being misread in an evaluation document. First, quote the category figure when you are arguing about whether specialized tooling has arrived, and quote per-product figures when you are comparing vendors; never swap one for the other. Second, keep the population attached to the number — global versus US and Canada, all company sizes versus 5,000-plus employees — because JetBrains publishes several populations and the labels are easy to drop. Third, treat the satisfaction data as single-product evidence: 91% CSAT establishes that Claude Code users are satisfied, not that competitors are not.

For your own decision the survey is a starting point on prevalence, not an outcome measurement. The useful next step is a bounded pilot on your own repositories with a pre-agreed measure, because none of these percentages tell you whether a tool will reduce review time on your codebase.

## FAQ

### Is 18% the share of developers using specialized AI coding tools?

No. 74% of developers had adopted specialized AI tools for developers by January 2026, excluding chatbots. 18% is the work-adoption rate for a single product, and in this wave Claude Code and Cursor both sit at that level.

### Why is the 74% category figure higher than every individual tool?

Because developers use more than one tool, and because the category includes IDE assistants, editors and agents beyond the products JetBrains charts individually. The post does not publish the full membership of the category or the overlap between products, so 74% is a statement about adoption of the category, not a sum of the tool rows.

### Does Copilot's 29% mean 29% of all developers use Copilot at work?

Yes for the global population in January 2026, but that is a different claim from the 40% figure, which is limited to developers in companies with over 5,000 employees. Both are JetBrains' self-reported survey estimates, not licence or seat telemetry.

## Sources and verification notes

- JetBrains Research, [Which AI Coding Tools Do Developers Actually Use at Work?](https://blog.jetbrains.com/research/2026/04/which-ai-coding-tools-do-developers-actually-use-at-work/), published April 2026 on January 2026 fieldwork.
- JetBrains Research, [AI Impact on Developer Workflows](https://blog.jetbrains.com/research/2026/04/ai-impact-developer-workflows/).

Both pages were retrieved and archived on 20 October 2026 and every number above was checked against the archived text; no new survey, benchmark or experiment was run for this article, and the archived copies are a private local author verification rather than a published dataset.
