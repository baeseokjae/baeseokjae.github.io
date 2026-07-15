# Strategy Review - 2026-06-12 Run 3

## Phase

- Current phase: Phase 1 (First Signal Integration).
- KD range enforced: 0-25.
- Search volume floor enforced: 200+.
- Queue trigger confirmed: active `queued` topics were at 1 before this run.
- Early analytics check: `/home/ubuntu/blog/state/analytics/` contains strategy-review artifacts but no standalone GSC query/performance export, so this run stayed external-data-first while preserving Phase 1 KD expansion.

## Inputs Read

- `/home/ubuntu/blog/state/strategy.json`
- `/home/ubuntu/blog/research/topics.json`
- `/home/ubuntu/blog/content/posts/`
- `/home/ubuntu/blog/state/analytics/`

## Competitor Sources Used

- Fiddler AI: https://www.fiddler.ai/blog/evaluate-ai-observability-tools-coding-agents
- Augment Code: https://www.augmentcode.com/tools/best-ai-agent-observability-tools
- Arize AI: https://arize.com/blog/best-ai-observability-tools-for-autonomous-agents-in-2026/
- Honeycomb: https://www.honeycomb.io/resources/webinars/introducing-honeycomb-mcp-your-ai-agents-new-superpower
- Cequence Security: https://www.cequence.ai/blog/ai/even-the-best-ai-agents-leak-secrets-prompt-injection-is-why/
- Chrome for Developers: https://developer.chrome.com/docs/agents/security
- Knostic: https://www.knostic.ai/blog/ai-coding-agent-security
- Infosecurity Magazine: https://www.infosecurity-magazine.com/news/agentjacking-attacks-hijack-ai/
- TrueFoundry: https://www.truefoundry.com/blog/enterprise-ai-agent-security-solutions
- Palo Alto Unit 42: https://unit42.paloaltonetworks.com/ai-agent-prompt-injection/
- Pillar Security: https://www.pillar.security/blog/the-new-ai-attack-surface-3-ai-security-predictions-for-2026
- Rasa: https://rasa.com/blog/best-ai-agent-framework
- LangChain: https://www.langchain.com/resources/ai-agent-frameworks
- Olostep: https://www.olostep.com/blog/ai-agent-frameworks
- Firecrawl: https://www.firecrawl.dev/blog/best-ai-coding-agents
- Faros AI: https://www.faros.ai/blog/best-ai-coding-agents-2026
- Morph: https://www.morphllm.com/best-ai-coding-agents-2026
- MightyBot: https://mightybot.ai/blog/coding-ai-agents-for-accelerating-engineering-workflows/

## Topics Added

- 5760. Coding Agent Observability Evaluation Guide 2026: Traces, Sandboxes, and Policy Enforcement (coding-agent-observability-evaluation-guide-2026) - AI coding tools; KD 6; SV 480; status queued.
- 5761. Fiddler vs LangSmith vs Arize 2026: Coding Agent Observability Compared (fiddler-vs-langsmith-vs-arize-coding-agent-observability-2026) - AI workflow automation; KD 5; SV 260; status queued.
- 5762. Honeycomb Hosted MCP Guide 2026: Observability Data Inside AI Coding Agents (honeycomb-hosted-mcp-guide-2026) - AI for developers; KD 4; SV 240; status queued.
- 5763. Agentjacking Attacks Guide 2026: How Coding Agents Get Hijacked Through Tool Events (agentjacking-attacks-coding-agents-guide-2026) - AI coding tools; KD 4; SV 320; status queued.
- 5764. AI Agent Credential Indirection Guide 2026: Stop Prompt Injection from Leaking API Keys (ai-agent-credential-indirection-guide-2026) - AI for developers; KD 5; SV 360; status queued.
- 5765. WebMCP Security Guide 2026: Guardrails for Browser-Based AI Agents (webmcp-security-guide-2026) - AI for developers; KD 4; SV 300; status queued.
- 5766. AI Coding Agent Threat Model 2026: Sandboxes, Permissions, and Runtime Policy (ai-coding-agent-threat-model-2026) - AI coding tools; KD 6; SV 460; status queued.
- 5767. Enterprise AI Agent Security Platform Comparison 2026: Gateways, Runtime Controls, and Audit (enterprise-ai-agent-security-platform-comparison-2026) - AI workflow automation; KD 7; SV 520; status queued.
- 5768. Indirect Prompt Injection in AI Agents 2026: Hidden Web Content Defense Guide (indirect-prompt-injection-ai-agents-guide-2026) - AI for developers; KD 6; SV 420; status queued.
- 5769. Agent-to-Agent Attack Propagation Guide 2026: Securing Multi-Agent Workflows (agent-to-agent-attack-propagation-guide-2026) - AI workflow automation; KD 4; SV 260; status queued.
- 5770. Rasa CALM Agent Framework Guide 2026: Enterprise Governance for Production Agents (rasa-calm-agent-framework-guide-2026) - AI for developers; KD 5; SV 260; status queued.
- 5771. Microsoft Agent Framework vs OpenAI Agents SDK 2026: Enterprise Runtime or Minimal API (microsoft-agent-framework-vs-openai-agents-sdk-2026) - AI for developers; KD 6; SV 340; status queued.
- 5772. Mastra vs Microsoft Agent Framework 2026: TypeScript Agents or Enterprise Runtime (mastra-vs-microsoft-agent-framework-2026) - AI for developers; KD 4; SV 240; status queued.
- 5773. LlamaIndex Workflows vs LangGraph 2026: Data-Heavy Agents or Graph Runtime (llamaindex-workflows-vs-langgraph-2026) - AI for developers; KD 5; SV 300; status queued.
- 5774. AI Agent Framework Production Readiness Checklist 2026: Orchestration, Memory, Evals, and Governance (ai-agent-framework-production-readiness-checklist-2026) - AI workflow automation; KD 6; SV 420; status queued.
- 5775. SWE-Bench vs Terminal-Bench 2026: Which Coding Agent Benchmark Matters? (swe-bench-vs-terminal-bench-coding-agents-2026) - LLM comparison; KD 5; SV 380; status queued.
- 5776. AI Coding Agent Benchmark Scorecard 2026: Harness Depth, Cost, and Accuracy (ai-coding-agent-benchmark-scorecard-2026) - AI coding tools; KD 6; SV 620; status queued.
- 5777. OpenCode vs Codex CLI 2026: Open-Source Terminal Agent or Hosted Coding Agent (opencode-vs-codex-cli-2026) - AI coding tools; KD 6; SV 440; status queued.
- 5778. AI Coding Agent Harness Design Guide 2026: Reproducible Tests for Autonomous Code Changes (ai-coding-agent-harness-design-guide-2026) - AI coding tools; KD 5; SV 340; status queued.
- 5779. Remote Coding Agents vs Local CLI Agents 2026: Security, Cost, and Context Tradeoffs (remote-vs-local-coding-agents-2026) - AI coding tools; KD 5; SV 360; status queued.

## Validation

- Added 20 topics; rejected 0.
- Active queued inventory increased from 1 to 21.
- Every added candidate has title, slug, keyword, type, cluster, KD estimate, search volume estimate, discovery date, and source.
- Every added candidate is within KD 0-25 and has estimated search volume of at least 200.
- Slugs were checked against existing `topics.json` entries and `/home/ubuntu/blog/content/posts/*.md` before insertion.
- Topics fit focus topics or cluster priority: AI coding tools +7, AI for developers +8, AI workflow automation +4, LLM comparison +1.

## Strategy Adjustments

- Updated `strategy.json` `last_updated`, `new_opportunities`, per-cluster active queue counts, queued-throttled counts, and `last_strategy_run`.
- Kept Phase 1 behavior: early analytics are checked, but no separate GSC data file was available, so external competitor gap analysis remains primary.
- Recommended immediate writing priority: Agentjacking Attacks Guide, Coding Agent Observability Evaluation Guide, WebMCP Security Guide, and SWE-Bench vs Terminal-Bench because each has a timely source signal and a differentiated angle from existing published coverage.
