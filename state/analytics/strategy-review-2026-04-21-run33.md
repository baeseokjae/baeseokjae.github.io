# Strategy Review — 2026-04-21 (Run 33)

**Phase:** 0 (Foundation — external data only)
**Trigger:** heartbeat_timer (weekly strategy run)
**Queue before:** 411 queued / 542 total topics

## Topic Discovery

Searched competitor blogs and recent AI news for gaps in coverage. Focused on:
- New Google ADK ecosystem (launched April 2025, growing fast)
- AWS Strands Agents SDK (powers Kiro + Amazon Q)
- OpenAI deprecation urgency (Assistants API → August 2026)
- Llama 4 April 2026 release (Scout/Maverick)
- AI coding tool pricing angle (growing developer cost anxiety)
- Groq fast inference (free tier + OpenAI-compatible API)

## New Topics Added: 16

| Slug | KD | SV | Cluster | Status |
|------|----|----|---------|--------|
| google-adk-tutorial-2026 | 5 | 300 | AI for developers | queued |
| google-adk-vs-langgraph-vs-crewai-2026 | 8 | 400 | AI for developers | queued |
| strands-agents-sdk-tutorial-2026 | 3 | 200 | AI for developers | queued |
| openai-assistants-api-migration-responses-api-2026 | 6 | 350 | AI for developers | queued |
| llama-4-scout-maverick-api-guide-2026 | 6 | 400 | LLM comparison | queued |
| ai-coding-tools-pricing-comparison-2026 | 8 | 500 | AI coding tools | queued |
| deploy-llama-4-vllm-ollama-2026 | 5 | 250 | AI for developers | queued |
| google-adk-multi-agent-guide-2026 | 5 | 250 | AI for developers | queued |
| openai-agents-sdk-v2-tutorial-2026 | 5 | 300 | AI for developers | queued |
| groq-api-developer-guide-2026 | 5 | 350 | AI for developers | queued |
| google-adk-a2a-protocol-guide-2026 | 4 | 200 | AI for developers | queued |
| amazon-bedrock-agentcore-guide-2026 | 4 | 200 | AI for developers | queued |
| google-gemma-4-developer-guide-2026 | 5 | 350 | LLM comparison | queued |
| llama-4-local-deployment-guide-2026 | 5 | 300 | AI for developers | queued |
| ai-coding-tool-monthly-cost-guide-2026 | 7 | 400 | AI coding tools | queued |
| multi-agent-framework-comparison-2026 | 8 | 500 | AI for developers | queued |

**All 16 validated and promoted to "queued"** (KD 3-8, all within 0-14 range; SV 200-500; no duplicates).

## Cluster Analysis (Phase 0)

### Competitor Gap Signals
- **Google ADK cluster** entirely missing — Google launched ADK in April 2025 and competitors now have dedicated tutorials. We have zero ADK coverage.
- **AWS Strands** — Newly open-sourced, powering Kiro + Amazon Q. Zero competitor coverage yet.
- **Llama 4 API** — Released April 5, 2026. Competitors have basic guides but MoE architecture + 10M token context angle is underserved.
- **AI tool pricing** — Developer cost anxiety is at peak (tokenmaxxing backlash). Pricing comparison angle is high intent with moderate KD.

### Topical Cluster Health
| Cluster | Queued | Published |
|---------|--------|-----------|
| AI coding tools | 189 | 24 |
| AI for developers | 159 | 13 |
| LLM comparison | 50 | 4 |
| AI workflow automation | 30 | 5 |

Queue is healthy across all clusters. Priority: publish from existing queue before adding more.

### Internal Link Opportunities (Orphan Check)
- Published articles on Strands Agents, ADK, and Llama 4 local deployment will have zero inbound links from existing posts — these new topics provide natural linking targets for future articles.
- Existing cluster: `best-ai-agent-frameworks-2026.md` can link to new ADK/Strands articles.

## Strategy Adjustments
- **No KD range change** — Phase 0, maintaining 0-14.
- **New cluster emerging**: "Agent frameworks" — enough topics now for a sub-cluster within "AI for developers". Watch for Phase 1 signal.
- **OpenAI deprecation urgency** — `openai-assistants-api-migration-responses-api-2026` should be prioritized for publication given August 2026 deadline creating timely search intent.

**Queue after:** 427 queued / 558 total topics
