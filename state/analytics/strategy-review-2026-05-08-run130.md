# Strategy Review — 2026-05-08 (Run 130)

## Phase: 0 (Foundation — external data only)

## Summary

+14 new topics added. Total topics: 1705 (1327 queued).

## New Topics Added

### AI coding tools (+5)
- **cursor-3-3-pr-review-parallel-agents-2026** — Cursor 3.3 (May 7, 2026): PR Review in Agents Window + Build Plan in Parallel + Split PRs. High search intent from existing Cursor users. KD 5, SV 600.
- **openai-symphony-codex-orchestration-2026** — OpenAI Symphony: open-source spec to orchestrate Codex agents from Linear. Ships Elixir reference impl. 6x PR velocity on internal teams. KD 4, SV 350.
- **claude-managed-agents-dreaming-multi-agent-2026** — Claude Managed Agents May 2026 update: "dreaming" (scheduled memory curation), multi-agent orchestration beta, outcomes-based evaluation. KD 5, SV 280.
- **ai-developer-productivity-metrics-2026** — DORA + SPACE + DX Core 4 for the AI era. Traditional metrics can't separate real productivity gains from AI-generated debt. Growing enterprise search intent. KD 7, SV 400.
- **code-with-claude-sf-2026-recap** — Code with Claude SF event recap: Anthropic shipped plugin URL loading, gateway model discovery, rate limit doubling (SpaceX Colossus deal, 220K GPUs). KD 4, SV 250.

### AI for developers (+8)
- **luma-uni-1-1-api-developer-guide-2026** — Luma Uni-1.1 API: reasoning-first image generation, 31s/img, 30% cheaper than competitors. REST API with text-to-image + natural language editing. KD 5, SV 300.
- **mcp-a2a-ag-ui-protocol-stack-2026** — MCP+A2A+AG-UI: the complete 2026 agentic protocol stack. MCP = tools, A2A = agent-to-agent, AG-UI = agent-to-frontend. Google/LangChain/AWS/Microsoft all adopted AG-UI. KD 6, SV 400.
- **copilotkit-ag-ui-react-agents-2026** — CopilotKit developer guide: React frontend stack for AI agents using AG-UI protocol. Static/dynamic generative UI patterns, streaming SSE, human-in-the-loop. KD 4, SV 280.
- **puter-js-free-llm-api-guide-2026** — Puter.js: access GPT-5.5, Claude Opus 4.7, Gemini 3.1 Pro, 400+ models free via browser script tag. No API keys, no backend. "User-pays" model. KD 3, SV 350.
- **motherduck-ai-analytics-agent-guide-2026** — MotherDuck: cloud DuckDB with prompt_sql() natural language queries, AI agent builder guide, MCP remote connector, 95%+ text-to-SQL functional correctness. KD 5, SV 300.
- **duckdb-mcp-server-ai-agent-guide-2026** — DuckDB MCP server: AI agents (Claude, GPT-4o, Ollama) connect directly to DuckDB via MCP for natural language analytics. Ships with DuckDB v1.5.2. KD 4, SV 280.
- **generative-ui-developer-guide-2026** — Generative UI patterns: static (frontend owns components, agent selects), dynamic (agent renders HTML), protocol-native (MCP Apps/AG-UI/A2UI). CopilotKit reference implementations. KD 6, SV 400.
- **iso-42001-ai-management-system-guide-2026** — ISO 42001: first formal AI Management System standard. Required for enterprise AI tooling contracts. Developer-facing guide to certification controls and evidence. KD 8, SV 350.

### LLM comparison (+1)
- **llama-factory-fine-tuning-guide-2026** — LLaMA Factory: unified fine-tuning for 100+ LLMs (Qwen/Llama/Gemma/Mistral). LoRA, QLoRA, DPO, KTO, ORPO. NVIDIA DGX Spark official playbook Feb 2026. KD 7, SV 500.

## Key Signals (Phase 0 — Competitor Gap Analysis)

1. **Protocol layer is fragmenting the developer surface** — MCP (tools), A2A (agent-agent), AG-UI (agent-frontend), A2UI (Google), MCP Apps (interactive HTML). Developers are confused about which protocol does what. The combined stack guide fills a clear navigation gap.

2. **Cursor 3.3 launched May 7** with PR Review + Build Plan in Parallel — zero dedicated how-to content outside the forum thread. High conversion from existing Cursor user base.

3. **OpenAI Symphony (April 27)** is an open-source spec that changes how teams think about coding agents — from "supervise a session" to "manage a project." Reference Elixir impl, model-agnostic in v1.1 (supports Kata/Claude Code). Near-zero coverage outside press releases.

4. **Anthropic doubled Claude Code rate limits May 6** via SpaceX Colossus deal (220K GPUs). The Code with Claude SF event filled with product news. Event recap content is early-mover with clear search intent from Claude Code users.

5. **Free LLM API angle is underserved** — Puter.js (400+ models, no keys, browser script tag), GitHub Models free tier, Gemini CLI 1000 req/day, Groq free tier. Developer cost sensitivity is at an all-time high. Puter.js specifically has no quality guide.

6. **LLaMA Factory** (100+ LLMs, unified WebUI, DGX Spark official) has 30K+ GitHub stars but no dedicated tutorial outside DataCamp. Fine-tuning intent is growing as open-weight models reach frontier quality.

## Cluster Status
- AI coding tools: 502 queued, 12 writing, 128 published
- AI for developers: 553 queued, 1 writing, 54 published
- LLM comparison: 155 queued, 7 writing, 24 published
- AI workflow automation: 130 queued, 2 writing, 20 published

## Phase 0 Observations
- All four clusters are growing steadily. AI for developers (553 queued) and AI coding tools (502 queued) remain dominant.
- Published count discrepancy vs previous notes: published counts are now higher — writers have been productive.
- No GSC data yet. Focus remains on external signal + competitor gap analysis.
- AI workflow automation cluster is thin on new topics this run — next run should target: Temporal.io AI workflows, Airbyte AI pipelines v2, Prefect 3 AI-native flows.
