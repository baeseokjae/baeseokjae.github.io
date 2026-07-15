# Strategy Review - 2026-06-12 Run 4

## Phase

- Current phase: Phase 1 (First Signal Integration).
- KD range enforced: 0-25.
- Search volume floor enforced: 200+.
- Queue trigger confirmed: active `queued` topics were at 1 before this run.
- Early analytics check: `/home/ubuntu/blog/state/analytics/` contains strategy-review artifacts but no standalone GSC query/performance export, so this run used external competitor data while preserving the Phase 1 KD expansion.

## Inputs Read

- `/home/ubuntu/blog/state/strategy.json`
- `/home/ubuntu/blog/research/topics.json`
- `/home/ubuntu/blog/content/posts/`
- `/home/ubuntu/blog/state/analytics/`

## Competitor Sources Used

- Rasa: https://rasa.com/blog/best-low-code-ai-agents-platforms-for-2026
- Vellum: https://www.vellum.ai/blog/top-low-code-ai-agent-platforms-for-product-managers
- Voiceflow: https://www.voiceflow.com/blog/ai-agent-builder
- Botpress: https://botpress.com/blog/ai-agent-frameworks
- Google Cloud: https://cloud.google.com/blog/products/ai-machine-learning/announcing-agents-to-payments-ap2-protocol
- Google Developers: https://developers.googleblog.com/developers-guide-to-ai-agent-protocols/
- IBM: https://www.ibm.com/think/topics/ai-agent-protocols
- Tyk: https://tyk.io/learning-center/agent-protocols-a-complete-guide-to-mcp-a2a-and-acp/
- GetStream: https://getstream.io/blog/ai-agent-protocols/
- Docker: https://www.docker.com/blog/how-to-secure-ai-agents/
- ARMO: https://www.armosec.io/blog/ai-agent-sandboxing-progressive-enforcement-guide/
- Northflank: https://northflank.com/blog/how-to-sandbox-ai-agents
- NVIDIA: https://developer.nvidia.com/blog/practical-security-guidance-for-sandboxing-agentic-workflows-and-managing-execution-risk/
- TrueFoundry: https://www.truefoundry.com/blog/enterprise-ai-agent-security-solutions
- HiddenLayer: https://www.hiddenlayer.com/news/hiddenlayer-unveils-new-agentic-runtime-security-capabilities-for-securing-autonomous-ai-execution
- Permiso: https://permiso.io/blog/ai-agent-runtime-security
- Augment Code: https://www.augmentcode.com/tools/intent-vs-devin
- Morph: https://www.morphllm.com/best-ai-coding-agents-2026
- Artificial Analysis: https://artificialanalysis.ai/agents/coding

## Topics Added

- 5780. Low-Code AI Agent Platforms for Developers 2026: Rasa, Vellum, Voiceflow, and Botpress (low-code-ai-agent-platforms-developers-2026) - AI workflow automation; KD 7; SV 620; status queued.
- 5781. Rasa vs Voiceflow vs Botpress 2026: Low-Code Agent Builders Compared (rasa-vs-voiceflow-vs-botpress-ai-agent-builders-2026) - AI workflow automation; KD 5; SV 360; status queued.
- 5782. Vellum Low-Code AI Agent Platform Guide 2026: Evals, Workflows, and Governance (vellum-low-code-ai-agent-platform-guide-2026) - AI for developers; KD 4; SV 260; status queued.
- 5783. Voiceflow AI Agent Builder Guide 2026: Conversational Agents with Developer Handoff (voiceflow-ai-agent-builder-guide-2026) - AI workflow automation; KD 5; SV 300; status queued.
- 5784. Botpress AI Agent Framework Guide 2026: Free Builder, Integrations, and RAG (botpress-ai-agent-framework-guide-2026) - AI for developers; KD 5; SV 420; status queued.
- 5785. No-Code vs Low-Code AI Agent Builders 2026: Governance, Extensibility, and Cost (no-code-vs-low-code-ai-agent-builders-2026) - AI workflow automation; KD 6; SV 520; status queued.
- 5786. Low-Code AI Agents for Customer Support 2026: Voiceflow, Botpress, or Rasa? (low-code-ai-agents-customer-support-2026) - AI workflow automation; KD 6; SV 440; status queued.
- 5787. Agent Payments Protocol AP2 Developer Guide 2026: Mandates, Trust, and Checkout Flows (agent-payments-protocol-ap2-developer-guide-2026) - AI for developers; KD 5; SV 360; status queued.
- 5788. AP2 vs MCP vs A2A 2026: Payments, Tools, and Agent Collaboration (ap2-vs-mcp-vs-a2a-agent-protocols-2026) - AI for developers; KD 6; SV 300; status queued.
- 5789. ANP Agent Network Protocol Guide 2026: Discovery for Multi-Agent Systems (anp-agent-network-protocol-guide-2026) - AI for developers; KD 4; SV 240; status queued.
- 5790. AI Agent Protocol Router Guide 2026: Choosing MCP, A2A, AP2, and AG-UI per Workflow (ai-agent-protocol-router-guide-2026) - AI workflow automation; KD 5; SV 280; status queued.
- 5791. AI Agent Protocol Compatibility Guide 2026: MCP, A2A, ACP, ANP, AP2, and AG-UI (ai-agent-protocol-compatibility-guide-2026) - AI for developers; KD 5; SV 260; status queued.
- 5792. AI Agent Sandboxing Progressive Enforcement Guide 2026: Observe First, Lock Down Later (ai-agent-sandboxing-progressive-enforcement-guide-2026) - AI coding tools; KD 5; SV 360; status queued.
- 5793. MicroVM vs gVisor for AI Agent Sandboxes 2026: Isolation Tradeoffs for Developers (microvm-vs-gvisor-ai-agent-sandboxes-2026) - AI for developers; KD 5; SV 320; status queued.
- 5794. NVIDIA Agentic Workflow Sandboxing Guide 2026: Execution Risk Controls for Coding Agents (nvidia-agentic-workflow-sandboxing-guide-2026) - AI coding tools; KD 4; SV 240; status queued.
- 5795. AI Agent Runtime Firewall Guide 2026: Prompt Injection, Tool Policy, and Audit Logs (ai-agent-runtime-firewall-guide-2026) - AI workflow automation; KD 6; SV 420; status queued.
- 5796. Agent Identity Runtime Attribution Guide 2026: Trace Autonomous Actions to Credentials (agent-identity-runtime-attribution-guide-2026) - AI for developers; KD 4; SV 260; status queued.
- 5797. Devin vs Intent 2026: Autonomous Software Engineer or Developer-in-the-Loop Agent (devin-vs-intent-developer-in-the-loop-2026) - AI coding tools; KD 5; SV 300; status queued.
- 5798. Developer-in-the-Loop Coding Agents Guide 2026: Review Gates, Ownership, and Merge Safety (developer-in-the-loop-coding-agents-guide-2026) - AI coding tools; KD 5; SV 340; status queued.
- 5799. AI Coding Agent Autonomy Levels 2026: Copilot, IDE Agent, PR Agent, or Autonomous Engineer (ai-coding-agent-autonomy-levels-2026) - AI coding tools; KD 6; SV 520; status queued.

## Validation

- Added 20 topics; rejected 0.
- Active queued inventory increased from 1 to 21.
- Every added candidate has title, slug, keyword, type, cluster, KD estimate, search volume estimate, discovery date, and source.
- Every added candidate is within KD 0-25 and has estimated search volume of at least 200.
- Slugs were checked against existing `topics.json` entries and `/home/ubuntu/blog/content/posts/*.md` before insertion.
- Topics fit focus topics or cluster priority: AI workflow automation +7, AI for developers +8, AI coding tools +5, LLM comparison +0.

## Strategy Adjustments

- Updated `strategy.json` `last_updated`, `new_opportunities`, per-cluster queue counts, queued-throttled counts, and `last_strategy_run`.
- Kept Phase 1 behavior: early analytics were checked, but no separate GSC data file was available, so external competitor gap analysis remains primary.
- Recommended immediate writing priority: Low-Code AI Agent Platforms for Developers, Agent Payments Protocol AP2 Developer Guide, AI Agent Sandboxing Progressive Enforcement Guide, and Developer-in-the-Loop Coding Agents Guide.
