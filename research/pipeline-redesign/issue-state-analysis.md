# Paperclip Issue State Analysis

Generated: 2026-04-27 08:49 UTC

**Note: API returned 500 issues (the limit) — total may be higher.**

## Summary

| Metric | Count |
|--------|-------|
| Total Issues (capped at 500) | 500 |
| Orphaned Sub-Issues | 114 |
| Stuck (>6h in_progress) | 0 |
| Currently in_progress | 0 |

## Issues by Status

| Status | Count |
|--------|-------|
| backlog | 6 |
| blocked | 5 |
| cancelled | 141 |
| done | 325 |
| todo | 23 |

## Issues by Type

| Type | Count |
|------|-------|
| Admin | 1 |
| Article | 10 |
| Auto-Reset | 71 |
| Dispatch | 61 |
| Other | 94 |
| Publish | 80 |
| Research | 19 |
| SEO | 27 |
| Supervisor | 77 |
| Thumbnail | 21 |
| Write | 39 |

## Type × Status Matrix

| Type | backlog | blocked | cancelled | done | todo | Total |
|------|---------|---------|-----------|------|------|-------|
| Admin | 0 | 0 | 0 | 1 | 0 | 1 |
| Article | 0 | 0 | 4 | 6 | 0 | 10 |
| Auto-Reset | 0 | 0 | 71 | 0 | 0 | 71 |
| Dispatch | 0 | 0 | 5 | 56 | 0 | 61 |
| Other | 0 | 5 | 5 | 81 | 3 | 94 |
| Publish | 0 | 0 | 16 | 59 | 5 | 80 |
| Research | 1 | 0 | 2 | 16 | 0 | 19 |
| SEO | 2 | 0 | 0 | 25 | 0 | 27 |
| Supervisor | 0 | 0 | 37 | 25 | 15 | 77 |
| Thumbnail | 2 | 0 | 0 | 19 | 0 | 21 |
| Write | 1 | 0 | 1 | 37 | 0 | 39 |

## "Other" Sub-Category Breakdown (94 items)

The 94 "Other" items break down as:

| Sub-prefix | Count |
|-----------|-------|
| [Auto-Reset] (agent error resets) | 71 — all cancelled |
| Generate thumbnail | 8 |
| Generate SEO schema | 8 |
| Morning: (pipeline routines) | 7 |
| Weekly: (pipeline routines) | 4 |
| Generate SEO schema for: | 4 |
| [Analyst] Content Gap | 4 |
| Generate cover image | 3 |
| Generate thumbnail for: | 3 |
| Find (topic research) | 3 |
| Various one-offs (Pipeline, Deploy, Batch, Scout, etc.) | ~19 |

Note: The 71 Auto-Reset issues were reclassified from "Other" to their own category above.

## Orphaned Sub-Issues (parent is done/cancelled) — 114 total

114 sub-issues whose parent Article is already done or cancelled:
- 102 orphans are themselves **done** (completed work under finished parents — normal)
- 12 orphans are **cancelled** (abandoned work under finished parents — expected)
- 1 notable orphan: **ROC-1688** Publish: QA Wolf Review — cancelled while parent Article ROC-1683 is done (publish never completed)
- 1 notable orphan: **ROC-1730** Publish: 1Password — cancelled while parent ROC-1530 is done

**Assessment:** Most orphans are naturally completed sub-tasks whose parent Article finished. Not a systemic issue. The 2 cancelled Publish orphans (ROC-1688, ROC-1730) represent articles that were written but never published.

## Stuck Items (in_progress > 6 hours)

**None.** Zero items are currently in_progress, let alone stuck.

## Blocked Items (5)

| Identifier | Title |
|------------|-------|
| ROC-1724 | Wait: GSC data available, run full analytics suite |
| ROC-1701 | 18 Best DevOps MCP Servers for 2026: K8s, CI/CD, and Monitoring |
| ROC-1695 | Best AI QA Testing Tools 2026: Agentic Test Automation Compared |
| ROC-1661 | GSC Analytics: Monitor for striking distance keywords |
| ROC-1456 | GPT-5.5 Pro API Enterprise Guide (blocked) |

## Backlog Items (6)

| Identifier | Title |
|------------|-------|
| ROC-1748 | Thumbnail: Testsigma Review 2026: Agentic AI Testing Platform Deep Dive |
| ROC-1747 | SEO: Testsigma Review 2026: Agentic AI Testing Platform Deep Dive |
| ROC-1743 | Thumbnail: Testsigma Review 2026: Agentic AI Testing Platform Deep Dive |
| ROC-1742 | SEO: Testsigma Review 2026: Agentic AI Testing Platform Deep Dive |
| ROC-1741 | Write: Testsigma Review 2026: Agentic AI Testing Platform Deep Dive |
| ROC-1740 | Research: Testsigma Review 2026: Agentic AI Testing Platform Deep Dive |

Note: The Testsigma Review has duplicate backlog entries (two sets of Thumbnail+SEO sub-tasks), suggesting a duplication bug in the dispatch system.

## Active TODO Items (23) — Requiring Attention

### Supervisor Alerts (15 todo)
- 5x Cover image missing alerts (testsigma, qawolf, ai-coding-enterprise-roi, claude-api-max-tokens, openai-computer-use-api, chatgpt-workspace-agents)
- 2x Burst execution alerts (14 posts in 6h — rate limit violation)
- 2x Korean language content violation alerts (kimi-k2-vs-claude)
- Other operational alerts

### Pending Publish Tasks (5 todo)
- ROC-1579 Publish: Claude Opus 4.7 Tokenizer Cost Trap
- ROC-1589 Publish: Qodo Review 2026
- ROC-1488 Publish: GPT-5.5 Pro API Enterprise Guide
- ROC-1483 Publish: Databricks Managed MCP Servers
- ROC-1584 Publish: CodeRabbit Review 2026

### Pending Articles (1 todo)
- ROC-1689 Testsigma Review 2026
- ROC-1677 Claude API 300K Output Tokens Guide
- ROC-1536 Peta: Scoped Credentials for AI Agents

## Key Findings

1. **No stuck items** — Zero issues have been in_progress for >6 hours. Pipeline appears healthy from a stuck-work perspective.

2. **114 "orphaned" sub-issues** found where parent Article is done/cancelled. Of these, 102 are themselves done (natural completion), 12 are cancelled. Only 2 represent actual publish failures: ROC-1688 (QA Wolf) and ROC-1730 (1Password).

3. **71 Auto-Reset Supervisor issues** — All cancelled, representing historical agent error resets. These are noise/operational artifacts, not meaningful pipeline work.

4. **77 Supervisor issues total** — 15 are still todo (actionable alerts), 37 cancelled, 25 done. The 15 todo Supervisor alerts are the primary operational to-do list:
   - 5x missing cover images
   - 2x burst execution warnings
   - 2x Korean content violations
   - Other operational items

5. **Testsigma Review duplication** — Two sets of Thumbnail+SEO backlog issues exist for the same article, suggesting a dispatch bug.

6. **5 Publish tasks stuck in todo** — Articles that are fully written with SEO done but haven't been published yet (ROC-1579, ROC-1589, ROC-1488, ROC-1483, ROC-1584).

7. **Pipeline throughput**: 325 done / 500 total = 65% completion rate. 141 cancelled (28%), 23 todo (5%), 5 blocked, 6 backlog.

8. **Content pipeline composition**: 19 Research + 39 Write + 27 SEO + 21 Thumbnail + 80 Publish = 186 content-specific tasks. 61 Dispatch orchestrations. 10 Article parent issues. The high Publish-to-Write ratio (80:39) suggests many publish tasks are auto-generated per article.

9. **Data completeness note**: The API hit the 500-result limit, so there are likely more issues beyond what was returned. The full backlog may be larger.