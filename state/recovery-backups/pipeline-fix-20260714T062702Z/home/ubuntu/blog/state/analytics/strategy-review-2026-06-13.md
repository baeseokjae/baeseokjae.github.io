# Strategy Review - 2026-06-13

## Phase 1 Status

- Current phase: Phase 1 (First Signal Integration)
- KD range: 0-25
- Search volume filter: 200+ estimated monthly searches
- Analytics files found: prior strategy reviews only; no separate GSC query export was present in `~/blog/state/analytics/`
- Queue health before run: 3316 total topics, 1 active queued, 2608 queued throttled
- Queue health after run: 3331 total topics, 16 active queued, 2608 queued throttled

## New Topics Added This Run (+15)

### AI For Developers (+12)

1. `braintrust-topics-ga-pattern-discovery-guide-2026` - Braintrust Topics GA pattern discovery. KD 4, SV 320
2. `braintrust-agent-while-loop-tools-architecture-guide-2026` - Braintrust agent while loop tools architecture. KD 5, SV 380
3. `stytch-mcp-authentication-authorization-guide-2026` - Stytch MCP authentication authorization. KD 5, SV 340
4. `stripe-projects-agent-integrations-developer-controls-guide-2026` - Stripe Projects agent integrations developer controls. KD 5, SV 360
5. `honeyhive-evaluations-agent-development-lifecycle-2026` - HoneyHive evaluations agent development lifecycle. KD 4, SV 300
6. `honeyhive-agent-development-lifecycle-guide-2026` - HoneyHive agent development lifecycle. KD 4, SV 260
7. `langwatch-llm-agent-monitoring-tools-guide-2026` - LLM agent monitoring tools LangWatch. KD 5, SV 340
8. `langwatch-roojoom-agent-quality-control-case-study-2026` - Roojoom AI agent quality control LangWatch. KD 3, SV 220
9. `confident-ai-g-eval-agent-evaluation-guide-2026` - G-Eval agent evaluation Confident AI. KD 5, SV 380
10. `opik-agent-tracing-observability-guide-2026` - Opik agent tracing observability. KD 5, SV 360
11. `opik-ai-agent-evaluation-reliable-systems-guide-2026` - Opik AI agent evaluation reliable systems. KD 4, SV 300
12. `opik-custom-observability-dashboards-cost-latency-guide-2026` - Opik custom observability dashboards cost latency. KD 4, SV 240

### AI Workflow Automation (+2)

1. `vellum-nebula-alternatives-ai-workflow-evaluation-2026` - Nebula alternatives AI workflow evaluation. KD 4, SV 260
2. `vellum-low-code-ai-workflow-automation-tools-2026` - low-code AI workflow automation tools 2026. KD 6, SV 420

### LLM Comparison (+1)

1. `patronus-lynx-hallucination-detection-model-guide-2026` - Patronus Lynx hallucination detection model. KD 5, SV 360

## Candidate Validation

All promoted candidates passed:

- KD within configured range (0-25)
- Search volume estimate >= 200
- Unique slug across `topics.json` and published post filenames
- Required title, slug, and keyword present
- Cluster fits current focus topics or cluster priority

Rejected this run: 0

## Competitor Signals

- Braintrust is publishing production-eval workflow topics beyond generic eval tooling: pattern discovery via Topics GA and the canonical agent while-loop architecture.
- HoneyHive and LangWatch point to agent lifecycle evaluation and production quality control as active implementation problems, not just observability vendor reviews.
- Stytch offers a concrete MCP authentication and authorization implementation guide, which fits the requested auth subflow direction without reusing broad MCP overview topics.
- Stripe Projects has a developer-control angle around agent integrations, providers, billing, and model monitoring, distinct from the saturated AgentCore payments theme.
- Patronus Lynx is a specific hallucination-detection model topic that can support LLM comparison and eval-quality internal links.
- Opik and Confident AI reinforce trace-to-eval loops: agent tracing, G-Eval, reliable agent systems, dashboards, and cost/latency optimization.

## Strategy Adjustments

- Keep Phase 1 behavior. No Phase 2 performance logic was applied because no separate GSC query export exists yet.
- Active queue was the priority. The run added active `queued` topics rather than more `queued_throttled` inventory.
- Continue avoiding saturated themes already called out in `strategy.json`: broad MCP overviews, generic sandboxes, Temporal durable agents, AGENTS.md vs skills, Copilot SDK GA, AgentCore payments, and generic docs-to-MCP.
- Prioritize trace-to-eval loops, agent quality checks, MCP auth subflows, and vendor-specific implementation details until the active queue has a healthier buffer.

## Sources Reviewed

- Braintrust Topics GA: https://www.braintrust.dev/blog/topics-ga
- Braintrust agent architecture: https://www.braintrust.dev/blog/agent-while-loop
- Braintrust eval lessons: https://www.braintrust.dev/blog/five-lessons-evals
- ReadMe LLM-ready API docs: https://readme.com/blog/llm-ready-api-documentation
- Stytch MCP auth guide: https://stytch.com/blog/MCP-authentication-and-authorization-guide/
- Stripe Sessions 2026: https://stripe.com/blog/everything-we-announced-at-sessions-2026
- Stripe Projects agent integrations: https://stripe.com/blog/stripe-projects-adds-new-agents-providers-developer-controls
- HoneyHive insights: https://www.honeyhive.ai/blog
- Patronus Lynx: https://www.patronus.ai/blog/lynx-state-of-the-art-open-source-hallucination-detection-model
- Vellum Nebula alternatives: https://www.vellum.ai/blog/best-nebula-alternatives
- Vellum low-code workflow automation tools: https://www.vellum.ai/blog/top-low-code-ai-workflow-automation-tools
- LangWatch blog: https://langwatch.ai/blog
- Confident AI G-Eval: https://www.confident-ai.com/blog/g-eval-the-definitive-guide
- Opik agent tracing: https://www.comet.com/site/blog/ai-agent-tracing/
- Opik agent evaluation: https://www.comet.com/site/blog/
