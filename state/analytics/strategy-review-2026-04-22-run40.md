# Strategy Review — 2026-04-22 (Run 40)

**Phase:** 0 (Days 0-30) — External data only, no GSC signals yet

## Topic Discovery Summary

- **17 new topics added** → all 17 promoted to `queued` (passed all validation gates)
- Queue total: **550 queued** (up from 533)

### New Topics by Cluster

| Cluster | New Topics Added |
|---------|-----------------|
| AI workflow automation | +8 |
| AI for developers | +6 |
| LLM comparison | +2 |
| AI coding tools | +1 |

### Key Discoveries

**Google Opal (AI for developers)**
Google Labs launched Opal globally — a free no-code AI mini-app builder powered by Gemini. Competes with Lovable, Bolt, and v0 but with Google's free tier. Near-zero competition, KD 5, SV 350-500. Three articles added: review, comparison, tutorial.

**GPT-Image-2 (AI for developers)**
OpenAI launched `gpt-image-2` on April 21, 2026 — native reasoning in image generation, 99% typography accuracy, 2x speed over predecessor. API access in early May 2026. Two articles added: API guide + features overview.

**Workflow Automation Cluster Expansion**
The AI workflow automation cluster had only 36 queued topics — the thinnest cluster. Added 8 new topics covering:
- Windmill (open-source code-first alternative to n8n, KD 6-7)
- Inngest (event-driven step functions for AI, KD 5-6)
- Trigger.dev v3 (serverless background jobs, KD 5)
- Relay.app (no-code AI agent workflows, KD 5)
- n8n alternatives roundup (SV 600, KD 8)
- Hatchet (durable AI task orchestration, KD 4)

**Kimi Code K2.6 (LLM comparison)**
Moonshot's Kimi Code K2.6 launched April 13 at $0.60/M input tokens — 5x cheaper than Claude Sonnet 4.6. Early mover opportunity, KD 4, SV 250.

**Multi-Model LLM Architecture (LLM comparison)**
April 2026 practical insight: winning teams use Claude for coding agents, Gemini for large-context analysis, Qwen for multilingual, local model for latency. Guide gap confirmed, KD 8, SV 400.

## Cluster Status (post-run)

| Cluster | Queued | Published | Writing/Seeded |
|---------|--------|-----------|----------------|
| AI coding tools | 223 | 27 | 23 |
| AI for developers | 194 | 15 | 6 |
| LLM comparison | 67 | 4 | 2 |
| AI workflow automation | 53 | 5 | 0 |

## Strategy Adjustments

- No kd_range change (Phase 0, stay at 0-14)
- Priority: **workflow automation cluster** needs content production attention — only 5 published vs 53 queued
- **Google Opal** is a fast-moving opportunity (free, global, fresh launch) — prioritize for content production
- **GPT-Image-2** API content should ship before early May API launch date

## Phase 0 Observations

- Competitor coverage gap: workflow automation tools (Windmill, Inngest, Trigger.dev) are underserved across all major AI dev blogs
- Internal link opportunity: published n8n and Zapier articles can link to new workflow comparison content
- No GSC data available yet — next phase transition check: indexed_ratio > 0.9 AND days_since_launch > 30
