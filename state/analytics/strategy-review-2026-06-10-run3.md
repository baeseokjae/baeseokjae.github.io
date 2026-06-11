# Strategy Review - 2026-06-10 Run 3

## Phase 1 Status

- Current phase: Phase 1 (First Signal Integration)
- KD range: 0-25
- Search volume filter: 200+ estimated monthly searches
- Analytics files found: prior strategy reviews only; no separate GSC query export was present in `~/blog/state/analytics/`
- Queue health before run: 3051 total topics, 2383 queued
- Queue health after run: 3067 total topics, 2399 queued

## New Topics Added This Run (+16)

### AI For Developers (+15)

1. `databricks-agent-bricks-custom-agents-evaluation-guide-2026` - Databricks Agent Bricks custom agents evaluation. KD 5, SV 420
2. `databricks-autonomous-ai-assistant-agent-bricks-guide-2026` - Databricks autonomous AI assistant Agent Bricks. KD 5, SV 340
3. `databricks-production-compound-ai-systems-guide-2026` - Databricks production compound AI systems. KD 5, SV 360
4. `databricks-care-cost-compass-agent-system-case-study-2026` - Databricks Care Cost Compass agent system. KD 3, SV 220
5. `databricks-agent-bricks-auto-optimized-agents-guide-2026` - Databricks Agent Bricks auto-optimized agents. KD 5, SV 380
6. `elastic-kubernetes-observability-mcp-app-guide-2026` - Elastic Kubernetes Observability MCP App. KD 4, SV 300
7. `elastic-mcp-server-bedrock-agentcore-guide-2026` - Elastic MCP Server Bedrock AgentCore. KD 4, SV 280
8. `elastic-llm-observability-azure-ai-foundry-guide-2026` - Elastic LLM Observability Azure AI Foundry. KD 4, SV 260
9. `zapier-langchain-alternatives-2026` - LangChain alternatives 2026 Zapier. KD 7, SV 500
10. `zapier-mcp-vs-api-guide-2026` - MCP vs API Zapier. KD 6, SV 420
11. `llamatrace-arize-llamaindex-evaluation-platform-guide-2026` - LlamaTrace Arize LlamaIndex evaluation platform. KD 4, SV 320
12. `arize-ai-observability-tools-autonomous-agents-2026` - AI observability tools autonomous agents Arize. KD 6, SV 420
13. `arize-credential-theft-agent-harness-traces-guide-2026` - credential theft AI agent harness traces. KD 4, SV 260
14. `arize-ai-agent-evaluation-golden-datasets-guide-2026` - AI agent evaluation golden datasets Arize. KD 5, SV 340
15. `arize-google-agent-framework-observable-agents-guide-2026` - Google Agent Framework observable agents Arize. KD 4, SV 280

### AI Workflow Automation (+1)

1. `tray-agent-gateway-mcp-pricing-guide-2026` - Tray Agent Gateway for MCP pricing. KD 4, SV 240

## Candidate Validation

All promoted candidates passed:

- KD within configured range (0-25)
- Search volume estimate >= 200
- Unique slug across `topics.json` and published post filenames
- Required title, slug, and keyword present
- Cluster fits current focus topics or cluster priority

Rejected this run: 0

## Competitor Signals

- Databricks is pushing Agent Bricks as a full agent lifecycle and evaluation layer, with enough specificity for separate evaluation, autonomous assistant, compound AI system, and case-study topics.
- Elastic is positioning MCP and observability inside Microsoft/AWS agent ecosystems, especially Kubernetes observability skills and Bedrock AgentCore integrations.
- Zapier has fresh comparison-style content around LangChain alternatives and MCP vs API. I skipped broader Zapier MCP integration topics because similar slugs are already rejected or covered.
- LlamaIndex and Arize are converging on hosted evaluation workflows with trace logging, experiments, and debugging for agent systems.
- Arize is publishing sharper operational-security agent topics, especially credential theft detection through harness traces and golden-dataset evaluation from production traces.

## Strategy Adjustments

- Keep Phase 1 behavior. No Phase 2 performance logic was applied because no separate GSC query export exists yet.
- Add more weight to agent evaluation and observability: Agent Bricks, LlamaTrace, Arize traces, golden datasets, and credential-theft detection.
- Treat Databricks, Elastic, and Arize as enterprise implementation clusters, not broad AI news. These should link to existing AI agent testing, LLM observability, Databricks MCP, and enterprise AI coding governance coverage.
- Avoid broad workflow-automation repeats unless the angle is specific, such as Tray Agent Gateway for MCP pricing and governance.

## Sources Reviewed

- Databricks Agent Bricks and Evaluation: https://www.databricks.com/blog/announcing-mosaic-ai-agent-framework-and-agent-evaluation
- Databricks autonomous AI assistant: https://www.databricks.com/blog/build-autonomous-ai-assistant-mosaic-ai-agent-framework
- Databricks production compound AI systems: https://www.databricks.com/blog/mosaic-ai-build-and-deploy-production-quality-compound-ai-systems
- Databricks Care Cost Compass: https://www.databricks.com/blog/care-cost-compass-agent-system-using-mosaic-ai-agent-framework
- Databricks Agent Bricks: https://www.databricks.com/blog/introducing-agent-bricks
- Elastic Microsoft Build 2026 wrap-up: https://www.elastic.co/blog/microsoft-build-2026-wrap-up
- Elastic AWS re:Invent agentic AI partnership: https://www.elastic.co/blog/elastic-aws-reinvent-2025
- Elastic Microsoft partnership: https://www.elastic.co/blog/elastic-microsoft-ignite-2025-partnership
- Zapier LangChain alternatives: https://zapier.com/blog/langchain-alternatives/
- Zapier MCP vs API: https://zapier.com/blog/mcp-vs-api/
- Zapier Tray pricing / Agent Gateway: https://zapier.com/blog/tray-pricing/
- LlamaIndex and Arize evaluation platform: https://www.llamaindex.ai/blog/arize-ai-and-llamaindex-roll-out-joint-platform-for-evaluating-llm-applications
- Arize autonomous agent observability tools: https://arize.com/blog/best-ai-observability-tools-for-autonomous-agents-in-2026/
- Arize credential theft traces: https://arize.com/blog/how-to-detect-credential-theft-in-ai-agent-harness-traces/
- Arize agent evaluation: https://arize.com/blog/why-testing-ai-agents-is-non-negotiable/
- Arize Google Agent Framework: https://arize.com/blog/building-and-deploying-observable-ai-agents-with-google-agent-framework-and-arize/
