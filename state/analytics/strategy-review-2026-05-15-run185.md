# Strategy Review — 2026-05-15 (Run 185)

## Phase: 0 — Foundation (External Data Only)

## Summary

+16 new topics added. Total topics: 2,162. All 16 candidates promoted to "queued" (all passed KD 0-14 filter, SV 200+, cluster fit, no duplicates).

## New Topics Added

### AI coding tools (+5)
- **claude-managed-agents-outcomes-developer-guide-2026** — KD 4, SV 400: Outcomes beta (Code with Claude 2026), grading agent scores primary agent work, 10.1% quality lift; near-zero competition for specific Outcomes guide
- **claude-routines-async-automations-developer-guide-2026** — KD 4, SV 350: Claude Routines for async PR automations, June 15 2026 Agent SDK credits billing; practical setup guide underserved
- **claude-code-ci-autofix-pr-fixes-guide-2026** — KD 5, SV 400: CI auto-fix PR fixes launched at Code with Claude 2026; used at every Anthropic team but developer tutorial gap
- **vibesec-ai-code-security-guide-2026** — KD 4, SV 300: OX Security VibeSec embeds security into Cursor/Copilot at creation time, 24+ vulnerability types; distinct from post-scan SAST tools, near-zero competition
- **claude-finance-ai-agents-developer-guide-2026** — KD 4, SV 350: Claude Finance 10-agent package for financial services (pitch builder/market researcher/month-end closer); niche but early-mover advantage

### AI for developers (+5)
- **gemma-3-qat-consumer-gpu-developer-guide-2026** — KD 5, SV 500: Gemma 3 QAT brings 27B model quality to RTX 3090 (8GB effective VRAM), Ollama/LM Studio ready; high developer interest as most can't afford A100s
- **devenv-2-0-nix-ai-developer-environments-guide-2026** — KD 5, SV 350: devenv 2.0 March 2026 — MCP server at mcp.devenv.sh, CLAUDECODE/OPENCODE_CLIENT auto-detection, 5x faster C FFI backend; growing Nix adoption + AI dev env intersection underserved
- **minimax-m1-reasoning-model-api-developer-guide-2026** — KD 5, SV 400: first open-weight hybrid-attention reasoning model, 456B/45.9B active, 1M context, 75% FLOPs vs DeepSeek R1, Apache 2.0; developer API guide gap despite significant capability
- **trulens-rag-llm-evaluation-developer-guide-2026** — KD 6, SV 400: TruLens RAG Triad + OpenTelemetry agent tracing, Snowflake-backed OSS; distinct from Arize Phoenix (which we have) — different architecture and use case
- **microsoft-foundry-local-on-device-ai-developer-guide-2026** — KD 6, SV 500: Foundry Local GA 2026, on-device OpenAI-compatible serving, foundry-local-sdk in-process inference (no HTTP), VS Code Toolkit 100+ models; only phi-4-mini angle existed, need dedicated guide

### LLM comparison (+4)
- **deepeval-vs-ragas-vs-trulens-llm-evaluation-comparison-2026** — KD 7, SV 500: 3-way comparison fills gap — DeepEval (50+ metrics, CI gating) vs RAGAS (lightweight RAG-focused) vs TruLens (OTel tracing + RAG Triad); existing entries are individual guides, not comparison
- **openai-gpt-4o-gpt-4-1-deprecation-migration-guide-2026** — KD 9, SV 1200: GPT-4o/4.1/4.1-mini/o4-mini retired February 2026 — urgent migration need, highest SV in this batch; prompt re-tuning + cost analysis angle
- **phi-4-mini-vs-gemma-3-4b-vs-qwen-3-8b-edge-comparison-2026** — KD 7, SV 500: three-way edge comparison (vs existing bilateral phi-4-mini vs gemma-3-4b entry); adds Qwen 3 8B as 3rd candidate — HumanEval 76.0 best under 8B
- **minimax-m1-vs-deepseek-r1-vs-qwen3-235b-reasoning-benchmark-2026** — KD 7, SV 450: open reasoning model 3-way, complements MiniMax M1 guide with comparison angle; Apache 2.0 vs MIT license angle for enterprise devs

### AI workflow automation (+2)
- **dust-tt-ai-agent-workspace-developer-guide-2026** — KD 6, SV 350: Dust positions above workflow automation — adaptive agents with org context (Slack/Notion/Drive), MCP integration; featured as top n8n alternative 2026 with developer API
- **claude-agent-sdk-credits-billing-guide-2026** — KD 4, SV 350: urgent June 15 2026 deadline — Agent SDK + claude -p draws from separate credit pool, distinct from interactive limits; developer cost confusion is high, practical optimization guide needed

## Key Signals from This Run

1. **Code with Claude 2026 (May 6) created a cluster of underserved how-to content** — Outcomes, Routines, CI auto-fix, Claude Finance all launched but developer guides are thin. Early-mover window is 2-4 weeks.

2. **Gemma 3 QAT is the most significant local model story of May 2026** — frontier quality on consumer hardware unlocks a huge developer audience that can't run 27B at fp16. Ollama has models available now.

3. **OpenAI GPT-4o deprecation has the highest search volume in this batch (SV 1200)** — February 2026 retirement is generating urgent migration intent. GPT-3.5 migration guide precedent suggests this will spike further.

4. **MiniMax M1 is the open reasoning model gap** — we have MiniMax M2.5/M2.7 (data serving) but not M1 (reasoning/agents). 456B open-weight with 1M context at Apache 2.0 is highly competitive with DeepSeek R1.

5. **LLM evaluation frameworks are consolidating** — TruLens (Snowflake) + DeepEval (Confident AI) + RAGAS forming distinct tiers. Comparison guide fills growing developer decision query.

6. **VibeSec represents a new category**: security-at-creation vs security-post-scan. Distinct from Snyk/Semgrep/SonarQube which scan after the fact. Growing as AI-generated code quality becomes a security concern.

## Topical Cluster Audit (Phase 0)

- **AI coding tools**: 615 queued / 128 published (need 20+ to fill cluster → focus on publishing queue)
- **AI for developers**: 631 queued / 54 published (largest queue, strong pipeline)
- **LLM comparison**: 242 queued / 24 published (just above 20 target for cluster density)
- **AI workflow automation**: 240 queued / 20 published (at minimum density threshold — prioritize publish)

## Cluster Gaps Identified

- **AI workflow automation cluster needs internal links** — at exactly 20 published, cluster density is at minimum. No orphan articles visible from here but worth checking internal link structure once articles are published.
- **LLM comparison cluster lacks reasoning model comparison content** — most entries are instruct/chat models. New M1 vs R1 vs Qwen3 entry starts to fill this.

## No Strategy Changes Required

Phase 0 behavior is correct. kd_range (0-14) and SV (200+) thresholds are appropriate. focus_topics remain valid. No phase transition triggered (need indexed_ratio > 0.9 AND days_since_launch > 30).
