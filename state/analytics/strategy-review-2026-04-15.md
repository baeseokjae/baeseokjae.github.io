# Strategy Review — 2026-04-15

**Phase:** 0 (Foundation — external data only)
**Trigger:** Weekly schedule / topic queue replenishment (queue was at 9, below threshold)

---

## Topic Discovery Summary

- **20 new topics added** to `research/topics.json`
- All 20 validated as `queued` (pass all 4 criteria)
- Topics span priorities 41–60

### Validation Results (all 20 passed)

| Check | Result |
|---|---|
| KD within range (0–14) | ✓ All KD 3–12 |
| Not duplicate of existing topic/post | ✓ Verified against all 40 existing slugs + 53 published posts |
| Has keyword + slug + title | ✓ |
| Fits focus_topics or cluster_priority | ✓ |

### New Topics by Cluster

**AI coding tools (14 new):**
- `claude-code-codex-cli-gemini-cli-2026` — terminal CLI comparison, KD 10, SV 500
- `ai-coding-tools-pricing-2026` — pricing free vs paid, KD 12, SV 800
- `claude-md-setup-guide-2026` — CLAUDE.md config file how-to, KD 3, SV 250
- `windsurf-memories-guide-2026` — Windsurf Memories feature, KD 4, SV 300
- `bolt-new-vs-replit-vs-v0-2026` — browser-based builder comparison, KD 9, SV 700
- `claude-code-subagents-guide-2026` — parallel subagents pattern, KD 3, SV 200
- `openai-codex-cli-guide-2026` — Codex CLI (Rust rebuild), KD 6, SV 400
- `agentic-coding-patterns-2026` — 8 patterns guide, KD 7, SV 450
- `cursor-claude-code-workflow-2026` — using both tools together, KD 5, SV 300
- `windsurf-swe1-model-guide-2026` — SWE-1 model review, KD 4, SV 250
- `claude-code-plan-mode-guide-2026` — Plan Mode how-to, KD 3, SV 220
- `github-copilot-agent-mode-2026` — Copilot agent mode guide, KD 8, SV 500
- `ai-coding-tools-beginners-guide-2026` — beginner entry guide, KD 6, SV 400
- `cursor-background-agents-2026` — background agents guide, KD 4, SV 250
- `kiro-ai-ide-review-2026` — Kiro (AWS) IDE review, KD 3, SV 200
- `antigravity-ide-review-2026` — Antigravity IDE review, KD 3, SV 200

**AI for developers (3 new):**
- `best-mcp-servers-developers-2026` — MCP servers list, KD 8, SV 600
- `build-mcp-server-python-2026` — build MCP server how-to, KD 5, SV 350
- `llm-prompt-caching-guide-2026` — prompt caching cost guide, KD 5, SV 350

**LLM comparison (1 new):**
- `llm-api-pricing-comparison-2026` — API pricing all major models, KD 11, SV 900

---

## Competitor Gap Analysis (Phase 0)

Searched DEV.to, Hashnode, LogRocket, NxCode, DataCamp, and tool-specific blogs.

### What competitors are covering that we aren't:

1. **Terminal CLI wars** — Claude Code vs Codex CLI vs Gemini CLI comparison is heavily trafficked on DEV.to and DataCamp but absent from our blog. **Added.**

2. **Pricing breakdowns** — Multiple blogs covering tool pricing with free tier comparisons (NxCode, TLDL.io). High SV ~800. **Added.**

3. **Feature-specific how-tos** — CLAUDE.md, Plan Mode, Windsurf Memories, cursor background agents — competitors cover these but they're low KD with how-to intent. **Added.**

4. **Browser-based AI builders** — Bolt.new vs Replit vs v0 is a growing comparison cluster. Competitor coverage exists but thin. **Added.**

5. **Agentic coding patterns** — "8 patterns that ship 10x faster" style content performs well on DEV.to. We have comparison posts but no pattern guides. **Added.**

6. **New/emerging IDE tools** — Kiro (AWS), Antigravity. Near-zero KD, early mover advantage. **Added.**

7. **LLM API pricing** — Price dropped ~80% in 12 months; high developer interest in cost comparison. KD 11 but within range. **Added.**

### What we already have (no gap):
- Cursor vs Windsurf comparisons ✓
- Claude Code tutorials ✓
- MCP server tutorial ✓
- AGENTS.md guide ✓
- Cursor rules ✓
- Aider + Ollama ✓
- n8n/Zapier automation ✓

---

## Topical Cluster Audit

| Cluster | Queued | Published | Gap to 20+ |
|---|---|---|---|
| AI coding tools | 34 | ~9 | ✓ Exceeds 20 |
| AI for developers | 12 | ~0 | ✓ Exceeds 10, building toward 20 |
| LLM comparison | 5 | ~5 | Need 10+ more |
| AI workflow automation | 5 | ~4 | Need 10+ more |

**Priority recommendation:** AI for developers cluster has 12 queued but 0 published — encourage Writers to prioritize these once coding tools are flowing.

---

## Internal Link Opportunities (Orphan Analysis)

Based on published post list review, the following are likely orphaned (low inbound links):
- `ai-test-generation-tools-2026` — no related topics in cluster yet
- `build-ai-test-generator-gpt5-2026` — standalone, no comparison posts
- `local-ai-model-serving-frameworks-2026` — could link from Aider+Ollama post
- `perplexity-vs-chatgpt-vs-google-ai-search-2026` — developer angle thin

**Recommendation:** Add internal links from upcoming coding tool articles to these orphans where contextually relevant.

---

## Strategy Adjustments

No changes to `kd_range` (0–14), `focus_topics`, or `tone` for Phase 0.

**Added to `new_opportunities`:** 9 new opportunity signals based on competitor analysis:
- CLAUDE.md / Plan Mode / subagents how-tos
- LLM API pricing angle
- Windsurf SWE-1 feature coverage
- Agentic patterns content gap
- Kiro + Antigravity early mover
- GitHub Copilot agent mode
- LLM prompt caching
- Browser-based builders comparison

---

## Next Run Notes

- Phase 0 → Phase 1 trigger: `indexed_ratio > 0.9 AND days_since_launch > 30` — check back after May 13
- Queue is healthy at 29 queued after this run
- Consider adding AI workflow automation topics next run (only 5 queued)
- Monitor Windsurf Wave 9 / SWE-1 adoption — could be high-traffic topic by May
