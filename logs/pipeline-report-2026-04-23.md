# Paperclip Pipeline Health Report
Generated: 2026-04-23 18:26 UTC

## Overview
| Metric | Value |
|--------|-------|
| Total Issues | 1172 |
| Backlog | 75 |
| Todo | 41 |
| In Progress | 0 |
| Done | 799 |
| Cancelled | 255 |
| Error | 0 |
| Completed (24h) | 100 |

## Agent Health
| Agent | Status | Heartbeat | MaxConc | Model |
|-------|--------|-----------|---------|-------|
| Analyst | error | ON | 3 | claude-haiku-4-5-20251001 |
| ContentDirector | error | ON | 3 | claude-sonnet-4-6 |
| Publisher | idle | ON | 3 | claude-haiku-4-5-20251001 |
| Researcher | idle | ON | 3 | claude-sonnet-4-6 |
| SEO | idle | ON | 3 | claude-haiku-4-5-20251001 |
| Strategist | idle | ON | 3 | claude-sonnet-4-6 |
| Supervisor | idle | ON | 3 | claude-sonnet-4-6 |
| Thumbnail | idle | ON | 3 | claude-haiku-4-5-20251001 |
| Writer | idle | ON | 3 | claude-sonnet-4-6 |

## Alerts
- CRITICAL: 2 agent(s) in error state
  - ContentDirector
  - Analyst

## Pipeline Flow
| Stage | Completed | Backlog | In Progress |
|-------|-----------|---------|-------------|
| Research | 89 | 0 | 0 |
| Write | 93 | 0 | 0 |
| SEO | 48 | 25 | 0 |
| Thumbnail | 50 | 24 | 0 |
| Publish | 98 | 1 | 0 |

## Content Stats
| Metric | Value |
|--------|-------|
| Published posts on disk | 134 |
---

# Pipeline Audit — 2026-04-23 21:07 UTC

## Overview
| Metric | Value |
|--------|-------|
| Overall Status | WARNING |
| Topic Queue | 577 queued (OK) |
| Articles Last 6h | 3 (OK ≤4) |
| Disk Usage | 44% (OK) |

## Auto-Fixes (Tier 1)
- **18 seeded→queued** topics migrated
- **22 stale sessions** deleted (paperclip workspaces >50k)

## HIGH Issues Created
| Issue | Severity | Detail |
|-------|----------|--------|
| ROC-1251 | HIGH | claude-code-codex-cli-gemini-cli-2026: 6,039 Korean chars |
| ROC-1253 | HIGH | cursor-vs-windsurf-vs-copilot-2026: 5,635 Korean chars (ROC-1246 재생성) |
| ROC-1255 | HIGH | Analyst adapter_failed — ROC-993 max retries exceeded |

## Blocked Issues
- **ROC-993** Daily Analytics: blocked (adapter_failed) — human intervention needed
- **ROC-951** Dispatch Next Article: blocked (process_lost) — ROC-1249 replacement created

## Normal
- No error agents (all idle/running)
- Cover images OK for recent articles
- Recurring LOW: 0 internal links
