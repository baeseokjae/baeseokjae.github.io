# Strategy Review — 2026-04-13

## Phase: 0 (External Data Only — Days 0-30)

---

## Run 1 (Initial) — Earlier Today

### Queue Status Before Run 1
- topics.json: **empty (0 topics)**
- Triggered: LOW_WATERMARK (<10 queued topics)

### Topics Added: 20 total (19 queued + 1 rejected)

#### From Existing Research Files (9 topics → queued)

| Priority | Slug | Cluster | KD | Vol |
|----------|------|---------|-----|-----|
| 1 | claude-code-vs-github-copilot-2026 | AI coding tools | 8 | 1200 |
| 2 | cursor-vs-vscode-copilot-2026 | AI coding tools | 10 | 2200 |
| 3 | cursor-vs-windsurf-vs-zed-ai-ide-2026 | AI coding tools | 7 | 1800 |
| 4 | fine-tuning-vs-rag-vs-prompt-engineering-2026 | AI for developers | 9 | 900 |
| 5 | gemini-cli-guide-2026 | AI coding tools | 6 | 600 |
| 6 | langchain-vs-llamaindex-2026 | AI for developers | 11 | 1400 |
| 7 | prompt-engineering-techniques-2026 | AI for developers | 12 | 2800 |
| 8 | vector-database-comparison-2026 | AI for developers | 10 | 1600 |
| 9 | vibe-coding-guide-2026 | AI coding tools | 5 | 1100 |

#### New Topics Generated (11 topics → 10 queued + 1 rejected)

| Priority | Slug | Cluster | KD | Vol | Status |
|----------|------|---------|-----|-----|--------|
| 10 | mcp-server-tutorial-2026 | AI for developers | 4 | 500 | queued |
| 11 | claude-code-tutorial-2026 | AI coding tools | 6 | 800 | queued |
| 12 | gpt4o-vs-claude-vs-gemini-developer-2026 | LLM comparison | 13 | 3200 | queued |
| 13 | best-ai-code-review-tools-2026 | AI coding tools | 9 | 900 | **rejected** (already published) |
| 14 | windsurf-ide-review-2026 | AI coding tools | 5 | 700 | queued |
| 15 | n8n-vs-zapier-vs-make-automation-2026 | AI workflow automation | 12 | 1300 | queued |
| 16 | claude-api-python-guide-2026 | AI for developers | 7 | 900 | queued |
| 17 | ai-pair-programming-guide-2026 | AI coding tools | 8 | 750 | queued |
| 18 | devin-vs-claude-code-vs-swe-agent-2026 | AI coding tools | 6 | 600 | queued |
| 19 | openai-codex-vs-github-copilot-2026 | AI coding tools | 9 | 850 | queued |
| 20 | llm-context-window-comparison-2026 | LLM comparison | 7 | 450 | queued |

---

## Run 2 — 2026-04-13 (This Run)

### Queue Status Before Run 2
- topics.json: 20 topics (4 status=queued, 10 seeded, 1 published, 1 rejected, 1 writing)
- Triggered: LOW_WATERMARK (<10 queued)

### Competitor Gap Analysis

Sources searched: dev.to, NxCode, UIBakery, TrueFoundry, Emergent.sh, Vellum.ai, n8n Blog, BotCampusAI, Digidop, morphllm.com, JetBrains Research Blog, DataCamp, Simplescraper, Northflank, DevTk.AI

**Key gaps identified vs competitors:**
- **Setup/how-to intent unserved:** Pipeline is comparison-heavy. Competitors rank for "how to set up Cursor AI," ".cursorrules guide," "Windsurf install tutorial" — lower KD than head comparisons, high conversion intent.
- **AGENTS.md standard:** New open standard for AI coding agent instructions (Claude Code, Copilot, Cursor, Windsurf, Devin all support it). Near-zero SERP competition. First-mover window open.
- **Open-source coding alternatives:** Continue.dev (VS Code extension), Aider (terminal) are growing but competitor blogs almost entirely focus on Cursor/Copilot. Low KD.
- **LLM generation gap:** Existing topics reference GPT-4o/Claude 3.5. Market has moved to Claude Opus 4.6, GPT-5, Gemini 3.x. "Best LLM for coding 2026" = est. 1,800/mo SV, KD 13 — still in range.
- **Automation tutorial gap:** n8n blog ranks for "best workflow tools" but tutorial format ("build your first AI workflow in n8n") is poorly covered. Activepieces and Pipedream: growing tools, minimal independent review content.
- **Local coding + privacy niche:** Aider + Ollama offline setup: very low KD, niche but rapidly growing among security-conscious devs.

### Topics Added: 20 (all → queued)

#### AI coding tools (10 new)

| Priority | Slug | KD | Vol |
|----------|------|----|-----|
| 21 | cursor-ai-setup-guide-2026 | 8 | 600 |
| 22 | aider-ai-review-2026 | 5 | 350 |
| 23 | replit-agent-review-2026 | 7 | 500 |
| 24 | claude-code-github-workflow-2026 | 6 | 300 |
| 25 | continue-dev-review-2026 | 5 | 300 |
| 26 | cursor-rules-guide-2026 | 6 | 400 |
| 27 | agents-md-guide-2026 | 3 | 250 |
| 28 | windsurf-setup-tutorial-2026 | 7 | 500 |
| 29 | best-free-ai-coding-tools-2026 | 10 | 700 |
| 30 | github-copilot-workspace-review-2026 | 9 | 450 |

#### LLM comparison (2 new)

| Priority | Slug | KD | Vol |
|----------|------|----|-----|
| 31 | best-llm-for-coding-2026 | 13 | 1800 |
| 32 | claude-opus-4-vs-gpt-5-coding-2026 | 12 | 800 |

#### AI workflow automation (4 new)

| Priority | Slug | KD | Vol |
|----------|------|----|-----|
| 33 | n8n-ai-workflow-tutorial-2026 | 7 | 450 |
| 34 | pipedream-vs-n8n-2026 | 9 | 350 |
| 35 | activepieces-review-2026 | 4 | 250 |
| 36 | zapier-ai-features-guide-2026 | 9 | 550 |

#### AI for developers (4 new)

| Priority | Slug | KD | Vol |
|----------|------|----|-----|
| 37 | openai-responses-api-tutorial-2026 | 7 | 400 |
| 38 | ai-for-backend-developers-2026 | 8 | 350 |
| 39 | aider-ollama-local-coding-2026 | 5 | 300 |
| 40 | build-ai-agent-from-scratch-2026 | 8 | 650 |

### Validation (all 20 passed)
- KD within 0–14 range ✓
- No duplicate slugs vs topics.json or published posts ✓
- keyword + slug + title present ✓
- Fits focus_topics or cluster_priority ✓

---

## Cluster Coverage After Run 2

| Cluster | Queued | Published | Gap to 20 |
|---------|--------|-----------|-----------|
| AI coding tools | 20 | 9 | Target reached ✓ |
| AI for developers | 9 | 0 | 11 more needed |
| LLM comparison | 4 | 5 | 11 more needed |
| AI workflow automation | 5 | 4 | 11 more needed |

---

## Strategy Adjustments (Phase 0)

1. **No phase change.** Still Phase 0. No GSC data.
2. **AI coding tools cluster target reached** (20+ queued). Shift priority to filling other clusters next run.
3. **Content type rebalance:** Comparison-heavy pipeline supplemented with 10 how-to/setup/review articles.
4. **Model generation gap:** Priority 31–32 address LLM comparison with current model names. Writer agents should use 2026 model names in titles/H1.
5. **AI workflow automation is next weakest** (5 queued, 4 published). Prioritize in next run if queue drops.

---

## Next Strategist Run Triggers
- Queue drops below 10 queued topics again
- Weekly schedule (next: 2026-04-20)
