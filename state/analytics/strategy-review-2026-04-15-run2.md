# Strategy Review — 2026-04-15 (Run 2)

## Trigger
Topic queue fell below 10 (was 4 queued). Strategist triggered for topic replenishment.

## Phase
**Phase 0** — External data only. No GSC. Competitor gap analysis + cluster audit.

## Topic Queue Status (Before / After)
| Status | Before | After |
|--------|--------|-------|
| queued | 4 | 24 |
| researched | 28 | 28 |
| seeded | 13 | 13 |
| published | 6 | 6 |
| writing | 2 | 2 |
| rejected | 1 | 1 |
| **Total** | **54 → 61** | **81** |

## Competitor Gaps Identified

Searched competitor content from: Codecademy, DEV.to, LogRocket, Codeant.ai, NxCode, deployhq.com, daily.dev, Medium.

### High-value gaps not yet covered:
1. **.cursorrules vs CLAUDE.md vs AGENTS.md** — Multiple competitor articles, 2026 format war is a real search query
2. **Cursor vs Windsurf vs Copilot** — Different from existing Zed comparison, high SV (800)
3. **MCP vs A2A protocol** — Google's A2A gaining traction, developer confusion = search intent
4. **Claude Code hooks** — DEV.to trending content, near-zero existing SEO coverage
5. **JetBrains AI comparison** — Underserved audience (Java/Kotlin devs ~35% of market)
6. **Qwen3-Coder + Kimi K2** — Emerging open-source models with early-mover advantage
7. **MCP gateway tools** — Enterprise MCP deployments growing, gateways underrepresented
8. **Claude Code + GitHub Actions** — CI/CD integration angle not covered, real developer need
9. **n8n AI agent nodes** — Beyond basic automation, agentic n8n workflows underserved

## New Topics Added (20 total → all promoted to "queued")

All passed validation:
- ✓ KD within range (0–14)
- ✓ Search volume ≥ 200
- ✓ No duplicate slugs
- ✓ Fits focus_topics or cluster_priority

| # | Slug | KD | SV | Cluster |
|---|------|----|----|---------|
| 61 | cursorrules-vs-claude-md-vs-agents-md-2026 | 5 | 600 | AI coding tools |
| 62 | cursor-vs-windsurf-vs-copilot-2026 | 12 | 800 | AI coding tools |
| 63 | mcp-vs-a2a-protocol-2026 | 7 | 400 | AI for developers |
| 64 | claude-code-best-practices-2026 | 8 | 500 | AI coding tools |
| 65 | claude-code-hooks-guide-2026 | 4 | 250 | AI coding tools |
| 66 | llm-coding-workflow-guide-2026 | 10 | 400 | AI coding tools |
| 67 | jetbrains-ai-vs-github-copilot-vs-cursor-2026 | 9 | 400 | AI coding tools |
| 68 | gemini-cli-vs-codex-cli-2026 | 7 | 350 | AI coding tools |
| 69 | mcp-gateway-tools-comparison-2026 | 5 | 300 | AI for developers |
| 70 | ai-coding-tools-for-teams-2026 | 11 | 350 | AI coding tools |
| 71 | qwen3-coder-review-2026 | 4 | 250 | LLM comparison |
| 72 | amazon-q-developer-review-2026 | 8 | 300 | AI coding tools |
| 73 | tabnine-vs-github-copilot-2026 | 11 | 450 | AI coding tools |
| 74 | kimi-k2-vs-claude-vs-gpt5-coding-2026 | 5 | 300 | LLM comparison |
| 75 | claude-code-github-actions-2026 | 7 | 350 | AI coding tools |
| 76 | agentic-ide-cursor-windsurf-antigravity-2026 | 6 | 300 | AI coding tools |
| 77 | windsurf-vs-cursor-performance-2026 | 9 | 300 | AI coding tools |
| 78 | configure-ai-coding-assistants-guide-2026 | 8 | 400 | AI coding tools |
| 79 | continue-dev-vs-github-copilot-2026 | 9 | 250 | AI coding tools |
| 80 | n8n-ai-agent-nodes-guide-2026 | 8 | 350 | AI workflow automation |

## Cluster Audit

| Cluster | Queued | Published | At 20+ target? |
|---------|--------|-----------|----------------|
| AI coding tools | 51 | 9 | ✓ Well above |
| AI for developers | 14 | 0 | — Growing |
| LLM comparison | 7 | 5 | — Needs more |
| AI workflow automation | 6 | 4 | — Needs more |

## Key Observations (Phase 0)

1. **AI coding tools cluster is saturated** — 51 queued is enough to sustain content velocity for weeks. Writers should prioritize highest SV topics first (cursor-vs-windsurf-vs-copilot-2026 at SV 800, cursor-vs-windsurf-vs-zed at SV 1800+).
2. **LLM comparison cluster needs attention** — Only 7 queued with 5 published. Qwen3-Coder and Kimi K2 added as low-KD opportunities.
3. **AI for developers cluster** — 14 queued, solid. MCP protocol topics are the highest-value additions (growing developer ecosystem).
4. **Emerging topics to monitor** — A2A protocol adoption, Qwen3/Kimi open-source models, enterprise MCP deployments. These will gain SV over next 60 days.

## Strategy Adjustments
No changes to kd_range or focus_topics needed. Current Phase 0 strategy is working.
Next strategy review: trigger when queue drops below 10 again, or on 2026-05-01 weekly review.
