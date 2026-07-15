# Strategy Review — 2026-05-02 (Run 85)

## Phase
Phase 0 (Foundation): External data only, no GSC signals yet.

## Topics Added: 18

### AI Coding Tools (+13)
- `claude-managed-agents-guide-2026` — Claude Managed Agents complete guide, April 8 public beta, $0.08/session-hr, Notion/Rakuten/Asana in production. KD 5, SV 350.
- `anthropic-agent-sdk-guide-2026` — Anthropic Agent SDK (Python/TypeScript), local prototype path to managed production. KD 4, SV 250.
- `claude-managed-agents-cost-optimization-2026` — Cost optimization: caching, model selection (Haiku/Sonnet/Opus), retry patterns. KD 4, SV 250.
- `openai-agents-sdk-v2-subagents-guide-2026` — OpenAI Agents SDK April 15 update: subagents, code mode, sandboxed execution. KD 5, SV 300.
- `google-project-jitro-jules-v2-guide-2026` — Google Project Jitro: outcome/KPI-driven coding agent, persistent workspace. KD 4, SV 300.
- `gpt-5-5-pro-coding-workflow-guide-2026` — GPT-5.5 Pro coding workflows, 82.7% Terminal-Bench 2.0. KD 5, SV 300.
- `anthropic-managed-agents-vs-openai-agents-sdk-2026` — Comparison guide for developers choosing a production agent runtime. KD 6, SV 350.
- `claude-managed-agents-pricing-guide-2026` — Real cost breakdown: session-hours × token costs, free tier, batch limits. KD 3, SV 250.
- `openai-agents-sdk-sandbox-guide-2026` — Safe code execution in OpenAI Agents SDK, Python first then TypeScript. KD 4, SV 250.
- `claude-api-skill-guide-2026` — Claude API skill integration: CodeRabbit, JetBrains, Warp, Resolve AI. KD 3, SV 200.
- `google-jules-v2-coding-agent-review-2026` — Full review of Jules V2 / Jitro, next-gen autonomous coding agent. KD 5, SV 300.
- `claude-design-api-guide-2026` — Claude Design: visual creation (prototypes, slides, one-pagers), April 17 launch. KD 4, SV 250.
- `anthropic-claude-api-cost-optimization-2026` — Full cost guide: Managed Agents + prompt caching + batch API strategies. KD 5, SV 350.

### AI For Developers (+3)
- `gemini-nano-4-android-developer-guide-2026` — Gemini Nano 4 via AICore developer preview; 4x faster, 60% less battery, 140+ languages. KD 5, SV 300.
- `google-io-2026-developer-recap` — Post-event recap of May 19-20 Google I/O: agentic coding keynote, Gemini updates, Android 17. KD 6, SV 600.
- `atlassian-confluence-ai-agents-guide-2026` — Atlassian Confluence Remix (visual AI tool open beta) + third-party agent integration guide. KD 6, SV 300.

### LLM Comparison (+2)
- `gpt-5-5-developer-guide-2026` — GPT-5.5 (April 23): 88.7% SWE-bench Verified, 82.7% Terminal-Bench 2.0, 1M context, $5/$30 per M tokens. KD 7, SV 500.
- `grok-5-developer-guide-2026` — Grok 5 developer guide: 6T parameter MoE model, Q2 2026 expected, multimodal. KD 5, SV 400.

## Key Market Signals

**1. Anthropic Managed Agents is the production layer competitors don't have yet.**
Launched April 8 public beta at $0.08/session-hour + standard token costs. Five named enterprise customers (Notion, Rakuten, Asana, Vibecode, Sentry) shipped production workloads before beta launched. The Agent SDK for local prototyping + Managed Agents for production creates a compelling developer path. Tutorial gap is significant — most coverage is early beta announcements, not production guides.

**2. Google Project Jitro redefines what a coding agent is.**
Rather than prompt-and-execute, Jitro/Jules V2 is outcome-driven: set a KPI (e.g., lower error rate, better test coverage), the agent identifies codebase changes to hit it. Google I/O 2026 (May 19-20) is the likely announcement moment. Near-zero coverage despite DevOps.com and DEV Community breaking the story in April. Early coverage advantage available.

**3. GPT-5.5 (April 23) creates a new benchmark leader in terminal coding.**
88.7% SWE-bench Verified and 82.7% Terminal-Bench 2.0 surpass Claude Opus 4.7 on terminal-specific tasks. Three variants: standard, Thinking, Pro. $5/$30 per M tokens (double GPT-5.4 but 72% fewer output tokens vs Claude). Developer guide gap is present — existing coverage is launch announcements, not practical how-to.

**4. OpenAI Agents SDK April 15 update is underreported.**
Subagents (hierarchical agent spawning), code mode, and sandboxed execution (Python first, TypeScript coming) represent a major platform capability jump. TechCrunch covered the launch but practical tutorials are absent.

## Strategy Assessment (Phase 0)

- Queue depth is healthy at 1,016+ topics — no urgency signals.
- Cluster priorities remain consistent: AI Coding Tools (479 queued) and AI For Developers (417 queued) are primary.
- No phase transition warranted — GSC data still absent, indexed ratio unknown.
- New_opportunities list in strategy.json updated with run 85 signals.
- Next run: continue monitoring Google I/O 2026 (May 19-20) for post-event coverage opportunities.
