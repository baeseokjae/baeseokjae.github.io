# Strategy Review - 2026-06-14

## Phase

Current phase: Phase 1 - First Signal Integration.

No non-review GSC or analytics files were present in `state/analytics/`, so this run stayed within Phase 1 behavior: external competitor discovery, topic inventory dedupe, and cluster audit.

## Queue Health

- Active queued topics before refill: 1
- New candidate topics added: 20
- Promoted to queued: 20
- Rejected: 0
- Priority range added: 5994-6013

## Competitor Sources Sampled

Firecrawl searches sampled current AI developer and agent-infrastructure competitors:

- BoundaryML/BAML
- Arcade
- Mastra
- Inngest
- Pydantic
- Arize Phoenix and OpenInference
- Helicone
- Trigger.dev
- LangChain
- OpenTelemetry
- HoneyHive
- Galileo
- Maxim

Selected additions came from sources with specific non-duplicate workflow gaps rather than broad repeated MCP/auth/sandbox listicles.

## Topics Added

All candidates were validated against `strategy.json` KD range 0-25, estimated search volume 200+, required title/slug/keyword fields, focus-topic fit, existing `topics.json` slugs, and published post filenames.

| Priority | Slug | Cluster | KD | SV |
| --- | --- | --- | --- | --- |
| 5994 | baml-prompt-schema-engineering-guide-2026 | AI for developers | 5 | 360 |
| 5995 | baml-vs-instructor-structured-output-comparison-2026 | AI for developers | 4 | 320 |
| 5996 | baml-graph-rag-extraction-guide-2026 | AI for developers | 4 | 260 |
| 5997 | pydantic-deep-agents-guide-2026 | AI for developers | 5 | 380 |
| 5998 | pydantic-deep-agents-vs-langchain-deep-agents-2026 | AI for developers | 5 | 300 |
| 5999 | pydantic-ai-multi-agent-patterns-guide-2026 | AI for developers | 5 | 340 |
| 6000 | pydantic-ai-capabilities-api-agent-hooks-guide-2026 | AI for developers | 4 | 240 |
| 6001 | arize-open-agent-spec-observability-guide-2026 | AI for developers | 4 | 280 |
| 6002 | openinference-agent-spec-instrumentation-guide-2026 | AI for developers | 4 | 260 |
| 6003 | arize-phoenix-google-adk-evals-guide-2026 | AI for developers | 5 | 300 |
| 6004 | arize-phoenix-bedrock-agents-observability-guide-2026 | AI for developers | 5 | 280 |
| 6005 | arize-phoenix-microsoft-foundry-agent-evals-guide-2026 | AI for developers | 5 | 260 |
| 6006 | langgraph-functional-api-guide-2026 | AI workflow automation | 5 | 360 |
| 6007 | langchain-interrupt-2026-product-launch-guide | AI workflow automation | 5 | 320 |
| 6008 | mastra-memory-gateway-guide-2026 | AI for developers | 4 | 300 |
| 6009 | mastra-server-adapters-express-hono-guide-2026 | AI for developers | 4 | 260 |
| 6010 | mastra-platform-agent-monitoring-guide-2026 | AI workflow automation | 5 | 280 |
| 6011 | maxim-ai-agent-simulation-guide-2026 | AI for developers | 5 | 300 |
| 6012 | maxim-ai-agent-quality-assurance-guide-2026 | AI for developers | 6 | 360 |
| 6013 | galileo-agent-guardrails-solutions-guide-2026 | AI for developers | 6 | 420 |

## Strategy Adjustment

Keep Phase 1 focused on concrete developer workflows:

- Type-safe prompt schema and structured-output layers
- Pydantic deep-agent runtimes and multi-agent patterns
- Open Agent Spec and OpenInference instrumentation
- Framework-specific ADK, Bedrock, and Foundry eval workflows
- LangGraph Functional API and production launch surfaces
- Mastra memory, server-adapter, and platform monitoring workflows
- Pre-release agent simulation and runtime guardrails

Avoid broad MCP/auth/sandbox listicles unless tied to a specific runtime, framework, or measurable production workflow.
