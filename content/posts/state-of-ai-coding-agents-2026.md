---
cover:
  alt: 'State of AI Coding Agents 2026: What Peer-Reviewed and Field Studies Actually Show'
  image: /images/state-of-ai-coding-agents-2026.png
  relative: false
date: 2026-05-25 21:04:58+00:00
description: Dated evidence tables separating controlled studies from vendor claims
  about AI coding agents in 2026, including what the research still cannot show.
draft: false
schema: schema-state-of-ai-coding-agents-2026
tags:
- ai-coding-agents
- software-development
- developer-productivity
- autonomous-ai
- enterprise-ai
title: 'State of AI Coding Agents 2026: What Peer-Reviewed and Field Studies Actually Show'
lastmod: 2026-10-23 00:00:00+00:00
---

The state of AI coding agents in 2026 is not one number, and the studies that actually control for something disagree on direction. A randomised trial on experienced open-source maintainers found that allowing early-2025 frontier AI tools made their own tasks 19% *slower*, while a Google enterprise trial and a 2022 GitHub Copilot experiment both found speed-ups — roughly 21% and 55.8%. Those results only look contradictory if you skip the populations, the task types and the tool generations behind them. Read together, they say something more useful and less quotable: the measured effect of AI-assisted coding depends heavily on who is coding, on what, with which generation of tool, and on how long the observation window is ([METR, arXiv:2507.09089](https://arxiv.org/abs/2507.09089v2)).

This page is a dated refresh of an earlier market narrative. The previous version opened with session metrics (23-minute sessions, 47 tool calls per session) and market sizing figures ($12.8 billion, 84% adoption, 51% daily use) presented as established fact. A bounded retrieval sweep on 2026-10-23 could not trace any of those specific figures to a primary source, so they are withdrawn from the body rather than relabelled as vendor data I had not read. What replaces them is what a reader arriving with research intent was actually looking for: a table of controlled studies with venue, sample size, design and effect direction, and a separate record of what this page no longer claims.

## What the controlled studies actually measured

| Study | Evidence type | N | Population and task | Tool generation | Design | Reported effect | Main limitation |
|---|---|---|---|---|---|---|---|
| METR, *Measuring the Impact of Early-2025 AI on Experienced Open-Source Developer Productivity* ([arXiv:2507.09089v2](https://arxiv.org/abs/2507.09089v2), 2025) | Working paper, not peer-reviewed | 16 developers, 246 tasks | Experienced maintainers on their own mature repositories, ~5 years prior experience each | Cursor Pro with Claude 3.5/3.7 Sonnet (early-2025 frontier) | Randomised per task: AI allowed vs. disallowed | Completion time **19% slower** with AI allowed; the same developers had forecast a 24% speed-up and afterwards still believed they had been 20% faster | Small volunteer sample, time-only outcome, results may not generalise |
| *How much does AI impact development speed? An enterprise-based randomized controlled trial* ([arXiv:2410.12944v3](https://arxiv.org/abs/2410.12944v3), 2024) | Working paper, author-affiliated with the vendor ecosystem | 96 engineers | Full-time Google software engineers, one complex enterprise-grade task | Three AI features of the company's internal tooling | Randomised controlled trial | About **21% less time on task**, with a wide confidence interval; developers who spend more hours per day coding benefited more | Single company, single task type |
| Perry et al., *Do Users Write More Insecure Code with AI Assistants?* ([arXiv:2211.03622v3](https://arxiv.org/abs/2211.03622v3), CCS '23) | Peer-reviewed (ACM CCS 2023) | 47 participants | Five security-related programming tasks in Python, JavaScript and C | codex-davinci-002, assistant-era | Controlled user study with and without assistant access | Participants with the assistant wrote **significantly less secure code** and were **more likely to believe** their code was secure | Pre-agentic model generation; laboratory tasks rather than production code |
| Peng et al., *The Impact of AI on Developer Productivity: Evidence from GitHub Copilot* ([arXiv:2302.06590v1](https://arxiv.org/abs/2302.06590v1), 2023) | Working paper, vendor-affiliated (Microsoft/GitHub) | 95 programmers | Upwork-recruited professionals, one synthetic task: an HTTP server in JavaScript | Copilot, 2022 generation, before general availability | Controlled experiment, treatment vs. control | Treatment group **55.8% faster** | Vendor-affiliated authors; one narrow task; self-selected freelance population |

Three points about that table matter more than any single row. First, exactly one of the four rows is peer-reviewed; the other three are arXiv working papers, and two of those three have authors affiliated with the companies whose tools they study. Second, no row measures a multi-week agentic workflow — every one of them measures time-on-task or task security inside a bounded study session. Third, none of the numbers can be averaged: the populations are disjoint, the tasks are different in kind, and the tool generations span 2022 to 2025.

## Why the three percentages do not cancel out

The temptation is to average 55.8%, 21% and −19% into a single "AI coding agents make developers X% faster" claim. That would be a scope error, not a synthesis. The Copilot experiment measured 95 freelancers building one well-specified synthetic server with a 2022 autocomplete-era tool ([arXiv:2302.06590v1](https://arxiv.org/abs/2302.06590v1)). The Google trial measured 96 engineers on a single complex enterprise task with company-internal features ([arXiv:2410.12944v3](https://arxiv.org/abs/2410.12944v3)). The METR trial measured 16 maintainers working on their own mature repositories where they already held roughly five years of context — precisely the situation in which an AI agent's suggestions compete with knowledge the developer already has ([arXiv:2507.09089v2](https://arxiv.org/abs/2507.09089v2)).

The METR result is worth reading closely for a second reason: the gap between belief and measurement. The same developers predicted a 24% speed-up before the tasks and estimated a 20% speed-up afterwards, while the instrumented measurement showed a 19% slowdown. Any survey that asks developers how much faster AI makes them is measuring that estimate, not the instrumented outcome. The productivity-metric argument itself is covered in more depth in [the AI coding productivity paradox analysis](/posts/ai-coding-productivity-paradox-research-2026/), which is the right place to continue that thread rather than re-arguing it here.

## The peer-reviewed record is thinner than the market narrative implies

The research-intent question behind this refresh was whether there is peer-reviewed evidence about human-AI pair programming and about the safety difference between assistants and autonomous agents. There is some, and it is narrower than the volume of 2026 commentary suggests. Security outcomes do have a peer-reviewed controlled study: the CCS '23 experiment found both worse code security and higher confidence among participants with assistant access ([arXiv:2211.03622v3](https://arxiv.org/abs/2211.03622v3)).

Peer-reviewed HCI venues also publish controlled user studies of *proactive* AI programming support — for example *Assistance or Disruption? Exploring and Evaluating the Design and Trade-offs of Proactive AI Programming Support* at CHI '25, which reports a within-subject code-editor experiment across three versions of the Codellaborator system with 18 participants ([ACM DL, DOI 10.1145/3706598.3713357](https://dl.acm.org/doi/10.1145/3706598.3713357)). It is cited here at venue, design and sample-size level only: its effect sizes and interaction measures were not extracted during this refresh, so no outcome figure from that study appears on this page. A future revision that reads the full text can promote it to an effect-bearing row; until then this page records only what its abstract states — proactive suggestions increased efficiency against the prompt-only baseline while also disrupting workflow — and no effect size.

## Autonomy versus assistant: what "safer" can and cannot mean yet

Asked directly, is a fully autonomous coding agent safer or less safe than a pair-programming assistant? The honest answer as of this refresh is that no controlled study answers that comparison head-to-head. There is no trial that randomises the same tasks across an autonomous-agent condition and an assistant condition and measures security, review burden and defect escape rate. Anyone presenting a confident ranking is extrapolating.

What the evidence does support is narrower and still decision-relevant. In the assistant era, having AI write code did not make participants more careful — it made them more confident while producing less secure code ([arXiv:2211.03622v3](https://arxiv.org/abs/2211.03622v3)). That finding is about self-assessment as much as about generated code, and it transfers to autonomy as a warning about review design rather than as a measured effect of autonomy. The practical consequence is that autonomy should be treated as a risk-control decision — reversibility, CI gates, human review on security-sensitive paths — rather than as a safety label that research has validated. The controlled comparison that would settle the question does not exist yet.

## Where the evidence is thin, and how this was checked

The evidence base behind this page was assembled as a bounded retrieval sweep, not an experiment: five candidate sources were queried by known identifier through the arXiv Atom API and an ACM Digital Library landing page, all five were retrieved, and raw payloads with SHA-256 hashes were kept as a private author verification log. That log is not published as a downloadable dataset, because the payloads are third-party HTML; the claims above rest on the abstracts and landing pages cited inline, which any reader can open at the URLs given.

The sweep has limits worth stating plainly. It was not an exhaustive crawl of CHI, ICSE or FSE proceedings, so the absence of other studies is not established — only that these five were verified within the time budget. Only two of the five sources are peer-reviewed, and just one of the four table rows is. For the CHI '25 study only its venue, design and sample size were read, not its outcome measures. No quality, maintainability or review-burden outcome was found in any controlled design, which means the entire "does the code get better" question is currently answered by vendor commentary rather than by measurement.

## What would change this picture

Three kinds of evidence would move this page from a caution to a conclusion. A preregistered multi-week field trial that measures defect escape rate and review burden alongside time, rather than time alone. A head-to-head randomised comparison of an autonomous workflow against an assistant workflow on security-sensitive tasks, so that "safer" becomes a measurable direction instead of a design preference. And independent replication of the METR slowdown on a larger, non-volunteer population of maintainers — the single result most often quoted out of context on this topic. Until at least one of those exists, the defensible position is that effect direction is population-dependent and that any single headline percentage is a scope error.

## Update log

**2026-10-23** — Evidence-layer refresh, same URL. Withdrawn the previously stated market-size and session metrics (the $12.8 billion market figure, 84% adoption, 51% daily use, 23-minute average session, 47 tool calls) because none could be traced to a primary source within this refresh's retrieval budget. Added the controlled-study table with venue, sample size, design, effect direction and limitations. Added the autonomy-versus-assistant section, which states explicitly that no head-to-head safety study exists. Added this log. Survey percentages are deliberately not restated here: they belong to [the developer AI tool survey round-up](/posts/developer-ai-tool-survey-2026/) and [the AI coding tool adoption statistics page](/posts/ai-coding-tool-adoption-statistics-2026/). Correction pass the same day: the two internal links to the productivity-paradox analysis were repointed to the published page at /posts/ai-coding-productivity-paradox-research-2026/, the earlier /posts/ai-coding-productivity-paradox-2026/ path having no article and no alias; the cited tool generations were corrected from "four years apart" to the 2022-2025 span actually covered; and the CHI '25 study was given its participant count (18) and DOI instead of a note saying the count was not extracted.

An update log is a dated record of what changed on this page. It is not a ranking claim, not a freshness signal, and not an assertion that the underlying research changed on this date — the studies cited above were published between 2022 and 2025.

## Related reading

- [The AI coding productivity paradox](/posts/ai-coding-productivity-paradox-research-2026/) — why measured productivity and reported productivity diverge, argued in full.
- [Developer AI tool survey 2026](/posts/developer-ai-tool-survey-2026/) — the home for survey percentages this page deliberately does not restate.
- [AI coding tool adoption statistics 2026](/posts/ai-coding-tool-adoption-statistics-2026/) — adoption and market-share figures with their own sourcing.
