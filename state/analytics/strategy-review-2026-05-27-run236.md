# Strategy Review — 2026-05-27 (Run 236)

## Phase 1 Status

- **Current phase**: Phase 1 (First Signal Integration)
- **KD range**: 0–25
- **Search volume filter**: 200+ estimated monthly searches
- **Published posts tracked in topics.json**: 449
- **Queue health**: 2786 total topics, 2254 queued — healthy, no shortage
- **Analytics**: no separate GSC query export; prior strategy reviews only

## New Topics Added This Run (+20)

### AI Coding Tools (+10)
1. `antigravity-2-0-io-2026-new-features-guide` — Google Antigravity 2.0 new features. KD 7, SV 750
2. `antigravity-2-0-desktop-app-guide-2026` — Antigravity 2.0 desktop app multi-agent orchestration. KD 6, SV 500
3. `antigravity-2-0-sdk-custom-workflows-guide-2026` — Antigravity 2.0 SDK custom subagent workflows. KD 5, SV 420
4. `claude-code-1-3-doubled-rate-limits-guide-2026` — Claude Code 1.3 doubled rate limits. KD 5, SV 380
5. `amazon-q-developer-alternatives-migration-2026` — Amazon Q Developer EOL alternatives. KD 8, SV 480
6. `deepseek-v4-claude-code-integration-guide-2026` — DeepSeek V4 in Claude Code setup. KD 5, SV 340
7. `antigravity-enterprise-agent-platform-guide-2026` — Antigravity enterprise deployment. KD 6, SV 360
8. `composer-2-5-ai-coding-review-2026` — Composer 2.5 review vs Cursor. KD 6, SV 320
9. `claude-code-number-one-market-share-2026` — Claude Code #1 market share story. KD 9, SV 650
10. `ai-coding-developer-trust-gap-2026` — 84% adoption vs 29% trust analysis. KD 7, SV 420

### LLM Comparison (+5)
1. `gemini-3-5-flash-migration-thinking-level-guide-2026` — Gemini 3.5 Flash migration, thinking_level trap. KD 6, SV 420
2. `gemini-3-5-flash-thinking-optimization-guide-2026` — thinking_level low/medium/high for agents. KD 5, SV 280
3. `deepseek-v4-pro-vs-flash-which-to-use-2026` — DeepSeek V4 Pro vs Flash decision guide. KD 6, SV 380
4. `qwen-3-6-max-swe-bench-pro-analysis-2026` — Qwen 3.6 Max #1 on six benchmarks. KD 5, SV 320
5. `ai-ultra-google-100-plan-worth-it-2026` — Google AI Ultra $100/month plan review. KD 7, SV 460

### AI for Developers (+2)
1. `claude-opus-4-7-large-codebase-security-audit-2026` — Opus 4.7 1M-token security audit workflow. KD 5, SV 280
2. `google-io-2026-developer-tools-summary-2026` — Google I/O 2026 dev tools roundup. KD 10, SV 800

### AI Workflow Automation (+3)
1. `make-maia-ai-workflow-builder-guide-2026` — Make Maia natural language scenario builder. KD 5, SV 260
2. `n8n-vs-make-vs-zapier-ai-agents-2026` — 3-way AI agent automation comparison. KD 9, SV 680
3. `n8n-2-0-persistent-memory-rag-guide-2026` — n8n 2.0 persistent memory and RAG patterns. KD 6, SV 320

## Candidate Validation

All 20 promoted candidates passed:
- KD within configured range (0–25) ✓
- Search volume estimate ≥ 200 ✓
- Unique slug across topics.json and published post filenames ✓
- Required title, slug, and keyword present ✓
- Cluster fits focus_topics or cluster_priority ✓

Rejected this run: 0

## Key Competitor Signals

**Google I/O 2026 (May 19–20):**
- Antigravity 2.0 launched with 5 surfaces: desktop app, CLI, SDK, Managed Agents API, Enterprise Agent Platform. Gap: practical setup and migration guides for each surface.
- Gemini 3.5 Flash went GA; the `thinking_level` default changed from `high` to `medium`, silently degrading ported workloads. Low-hanging fruit: migration checklist with the `thinking_level: "low"` tip for coding agents.
- Google AI Ultra ($100/month) bundles Antigravity 5× usage limits — review angle for developer cost analysis.

**Claude Code / Anthropic:**
- Claude Code 1.3 doubled rate limits on May 6; Anthropic reports ~$2.5B run-rate making it the #1 AI coding tool in 8 months. Both create high-search "how did this happen" and "what does this mean for teams" angles.
- Claude Opus 4.7 confirmed 1M-token context, ~40k-50k tokens/minute throughput. Security audit use case (500+ previously unknown CVEs discovered during pre-release testing) is concrete and differentiated.

**DeepSeek:**
- V4 Pro and Flash released April 23–24 with MIT license, OpenAI-compatible API, and strong SWE-bench numbers. Developer interest in running it inside Claude Code is a new integration angle not yet covered.

**AWS:**
- Amazon Q Developer announced end-of-support. Creates search demand for "Q Developer alternatives" and migration content.

**n8n / Automation platforms:**
- n8n 2.0 (January 2026) added native LangChain and 70+ AI nodes. Persistent memory (Postgres-backed) and RAG (vector store integration) are the uncovered deep-dive angles.
- Make launched Maia, an AI assistant that builds scenarios from natural language — no dedicated guide exists in our queue yet.

**Model benchmarks:**
- Qwen 3.6 Max hit #1 on SWE-bench Pro, Terminal-Bench 2.0, SkillsBench, QwenClawBench, QwenWebBench, and SciCode simultaneously — unique "open-weight model tops six at once" angle.

## Cluster Queue Snapshot

| Cluster | Published | Queued |
|---|---:|---:|
| AI coding tools | 187 | 750 |
| AI for developers | 111 | 759 |
| LLM comparison | 53 | 381 |
| AI workflow automation | 30 | 364 |

## Strategy Notes

- Phase 1 maintained. No GSC export available; external competitor signals drive topic selection.
- **Antigravity 2.0 subcluster**: enough unique surfaces (desktop, CLI, SDK, Enterprise) to warrant 3–4 dedicated setup guides vs. one mega-review. The existing `antigravity-vs-cursor-vs-claude-code-2026` is published; focus new content on v2.0 mechanics.
- **Trust gap angle** is a differentiated editorial play: most blogs track adoption stats, few examine the falling trust story — worth a long-form data-driven piece.
- **DeepSeek V4 in Claude Code** is a practical integration angle competitor blogs have not saturated.
- **Amazon Q EOL** is time-sensitive; prioritize this slug for early pickup by the ContentDirector.

## Sources Reviewed

- Google Developers Blog — I/O 2026 developer highlights: https://developers.googleblog.com/all-the-news-from-the-google-io-2026-developer-keynote/
- TechCrunch — Antigravity 2.0 with desktop app and CLI: https://techcrunch.com/2026/05/19/google-launches-antigravity-2-0-with-an-updated-desktop-app-and-cli-tool-at-io-2026/
- Gemini API Docs — Gemini 3.5 Flash: https://ai.google.dev/gemini-api/docs/models/gemini-3.5-flash
- NxCode — Gemini 3.5 Flash developer guide: https://www.nxcode.io/resources/news/gemini-3-5-flash-developer-guide-agentic-coding-2026
- DigitalApplied — AI coding adoption 50 statistics: https://www.digitalapplied.com/blog/ai-coding-adoption-statistics-2026-50-data-points
- LushBinary — AI coding agents comparison 2026: https://lushbinary.com/blog/ai-coding-agents-comparison-cursor-windsurf-claude-copilot-kiro-2026/
- Verdent Guides — DeepSeek V4 in Claude Code: https://www.verdent.ai/guides/deepseek-v4-in-claude-code
- Amazon Web Services — Q Developer end-of-support: https://noise.getoto.net/2026/04/30/amazon-q-developer-end-of-support-announcement/
- Finbyz Tech — n8n 2.0 LangChain agentic workflows: https://finbyz.tech/n8n/insights/n8n-2-0-langchain-agentic-workflows
- JetBrains Research — Which AI coding tools do developers actually use: https://blog.jetbrains.com/research/2026/04/which-ai-coding-tools-do-developers-actually-use-at-work/
- PADISO — Claude Opus 4.7 1M token context window: https://www.padiso.co/blog/building-with-claude-opus-4-7-1m-token-context-window/
- Knightli — GPT-5.5 vs Claude Opus 4.7 vs DeepSeek V4 vs Qwen 3.6 Max: https://knightli.com/en/2026/04/28/coding-ai-benchmark-gpt55-claude-opus47-deepseek-v4-qwen36max/
