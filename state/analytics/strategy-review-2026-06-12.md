# Strategy Review - 2026-06-12

## Phase

- Current phase: Phase 1 (First Signal Integration).
- KD range enforced: 0-25.
- Search volume floor enforced: 200+.
- Queue trigger confirmed: active `queued` topics were at 1 before this run.

## Inputs Read

- `/home/ubuntu/blog/state/strategy.json`
- `/home/ubuntu/blog/research/topics.json`
- `/home/ubuntu/blog/content/posts/`
- `/home/ubuntu/blog/state/analytics/` existing review history

## Competitor Sources Used

- LangChain blog: agentic engineering, Deep Agents, LangSmith code-first evals.
- Braintrust article/changelog: conversation analytics tools, Pydantic AI tool-call tracing.
- Docker blog: Docker MCP developer setup, securing AI agents.
- Vercel blog: Agentic Infrastructure, AI SDK 6, Next.js in ChatGPT apps.
- Competitive framework SERPs: LangGraph, CrewAI, Pydantic AI, OpenAI Agents SDK, Google ADK, Mastra.

## Topics Added

- 5721. LangChain Agentic Engineering Guide 2026: Beyond Single-Session Coding Agents (langchain-agentic-engineering-guide-2026) — AI coding tools; KD 6; SV 520; status queued.
- 5722. LangChain Deep Agents Architecture Guide 2026: Planning, Subagents, and Long-Horizon Tasks (langchain-deep-agents-architecture-guide-2026) — AI for developers; KD 6; SV 460; status queued.
- 5723. LangSmith Code-First Evaluation Framework Guide 2026: Catch Agent Regressions Before Users Do (langsmith-code-first-evaluation-framework-guide-2026) — AI for developers; KD 5; SV 340; status queued.
- 5724. AI Conversation Analytics Tools 2026: Braintrust vs LangSmith vs Langfuse vs Helicone (ai-conversation-analytics-tools-comparison-2026) — AI for developers; KD 7; SV 420; status queued.
- 5725. Braintrust Pydantic AI Tool-Call Tracing Guide 2026 (braintrust-pydantic-ai-tool-call-tracing-guide-2026) — AI for developers; KD 4; SV 260; status queued.
- 5726. Pydantic AI Observability Guide 2026: Traces, Tool Calls, and Eval Handoff (pydantic-ai-observability-guide-2026) — AI for developers; KD 6; SV 360; status queued.
- 5727. Docker MCP for AI Agents Guide 2026: Real-World Developer Setup (docker-mcp-ai-agent-developer-setup-2026) — AI coding tools; KD 6; SV 480; status queued.
- 5728. Docker AI Agent Security Guide 2026: Isolation, Tool Access, Identity, and Runtime Monitoring (docker-ai-agent-security-guide-2026) — AI coding tools; KD 7; SV 540; status queued.
- 5729. Docker MCP vs Cloudflare Remote MCP 2026: Local Agent Runtime or Edge MCP Platform? (docker-mcp-vs-cloudflare-remote-mcp-2026) — AI for developers; KD 5; SV 300; status queued.
- 5730. Vercel Agentic Infrastructure Guide 2026: Operations for AI-Native Software Teams (vercel-agentic-infrastructure-guide-2026) — AI workflow automation; KD 6; SV 400; status queued.
- 5731. Vercel AI SDK 6 Agents Guide 2026: Agents, Tools, MCP, DevTools, and Reranking (vercel-ai-sdk-6-agents-guide-2026) — AI for developers; KD 7; SV 620; status queued.
- 5732. Vercel AI SDK 6 MCP and DevTools Guide 2026: Debugging Tool Calls in React AI Apps (vercel-ai-sdk-6-mcp-devtools-guide-2026) — AI for developers; KD 5; SV 380; status queued.
- 5733. Next.js in ChatGPT Apps Guide 2026: Building MCP-Native App Integrations (nextjs-chatgpt-apps-mcp-guide-2026) — AI for developers; KD 6; SV 440; status queued.
- 5734. LangGraph vs CrewAI vs Pydantic AI 2026: Python Agent Framework Decision Guide (langgraph-vs-crewai-vs-pydantic-ai-2026) — AI for developers; KD 9; SV 700; status queued.
- 5735. OpenAI Agents SDK vs Google ADK 2026: Which Agent Framework Should Developers Use? (openai-agents-sdk-vs-google-adk-2026) — AI for developers; KD 8; SV 560; status queued.
- 5736. Mastra vs LangGraph 2026: TypeScript Agent Framework or Python Graph Runtime? (mastra-vs-langgraph-agent-framework-2026) — AI for developers; KD 6; SV 320; status queued.
- 5737. Durable Agents with Vercel Workflow SDK 2026: State, Tool Calls, and Long-Running Execution (durable-agents-workflow-sdk-guide-2026) — AI workflow automation; KD 5; SV 300; status queued.
- 5738. Agentic Engineering vs Agentic Coding 2026: What Changes When Agents Own the Workflow? (agentic-engineering-vs-agentic-coding-2026) — AI coding tools; KD 4; SV 280; status queued.
- 5739. Code-First AI Evals Guide 2026: Test Agents Like Software, Not Prompts (code-first-ai-evals-guide-2026) — AI for developers; KD 5; SV 360; status queued.

## Validation

- Added 19 topics; rejected 0.
- Every added candidate has title, slug, keyword, type, cluster, KD estimate, search volume estimate, and discovery date.
- Every added candidate is within KD 0-25 and has estimated search volume of at least 200.
- Slugs were checked against existing topics and published post filenames before insertion.
- Topics fit current focus topics or the stated priority to fill existing clusters.

## Strategy Adjustments

- Corrected active queue visibility in `strategy.json`: `topics.json` now has updated cluster counts and `last_strategy_run` reflects the real active queue, not stale estimated future queue sizes.
- Phase 1 behavior retained: external competitor gaps first, with the expanded KD max of 25.
- Recommended next editorial push: prioritize Vercel AI SDK 6, Docker MCP/security, and LangChain Deep Agents because those combine current competitor freshness with practical developer intent.
