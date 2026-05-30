# Strategy Review — 2026-05-28

## Phase 1 Status

- **Current phase**: Phase 1 (First Signal Integration)
- **KD range**: 0-25
- **Search volume filter**: 200+ estimated monthly searches
- **Published posts**: 485
- **Queue health**: 2814 total topics, 2274 queued — healthy, no shortage
- **Wake reason**: transient_failure_retry (routine topic discovery run)

## New Topics Added This Run (+20)

### AI Coding Tools (+14)
1. `claude-platform-aws-launch-guide-2026` — Claude Platform AWS. KD 6, SV 480
2. `claude-managed-agents-self-hosted-sandboxes-2026` — Claude Managed Agents self-hosted sandboxes. KD 5, SV 380
3. `claude-managed-agents-mcp-tunnels-guide-2026` — Claude Managed Agents MCP tunnels. KD 5, SV 320
4. `claude-compliance-api-enterprise-security-2026` — Claude Compliance API enterprise security. KD 6, SV 340
5. `claude-code-tool-search-tool-deferred-loading-2026` — Claude Code Tool Search Tool. KD 4, SV 280
6. `claude-code-goal-feature-guide-2026` — Claude Code goal feature. KD 4, SV 300
7. `cursor-agents-window-parallel-guide-2026` — Cursor Agents Window parallel. KD 7, SV 460
8. `cursor-worktree-best-of-n-guide-2026` — Cursor worktree best-of-n. KD 5, SV 260
9. `windsurf-devin-cloud-terminal-cli-guide-2026` — Windsurf Devin Cloud agent. KD 6, SV 380
10. `kiro-parallel-spec-task-execution-guide-2026` — Kiro parallel spec task. KD 4, SV 240
11. `codex-gpt-5-5-integration-guide-2026` — Codex GPT-5.5. KD 6, SV 420
12. `codex-history-search-mcp-oauth-guide-2026` — Codex history search MCP OAuth. KD 4, SV 240
13. `antigravity-2-0-gemini-3-5-flash-desktop-guide-2026` — Antigravity 2.0 desktop Gemini 3.5 Flash. KD 5, SV 340

### AI for Developers (+5)
1. `google-genkit-middleware-hooks-guide-2026` — Google Genkit middleware hooks. KD 5, SV 300
2. `llamaindex-google-agents-api-llamaparse-guide-2026` — LlamaIndex Google Agents API LlamaParse. KD 5, SV 280
3. `vellum-ai-production-agent-framework-guide-2026` — Vellum AI agent framework. KD 6, SV 320
4. `mastra-typescript-agent-framework-guide-2026` — Mastra TypeScript agent framework. KD 5, SV 360
5. `openai-agents-sdk-sandbox-mcp-guide-2026` — OpenAI Agents SDK sandbox MCP. KD 6, SV 400

### LLM Comparison (+1)
1. `gemini-spark-personal-ai-agent-guide-2026` — Gemini Spark personal AI agent. KD 6, SV 380

### AI Workflow Automation (+1)
1. `zapier-ai-agents-mcp-support-guide-2026` — Zapier AI Agents MCP. KD 7, SV 500

## Candidate Validation

All 20 promoted candidates passed:
- KD within configured range (0-25) ✓
- Search volume estimate >= 200 ✓
- Unique slug across topics.json and published post filenames ✓
- Required title, slug, keyword present ✓
- Cluster fits current focus topics ✓

Rejected this run: 0

## Competitor Signals

**Anthropic/Claude:**
- Claude Platform launched on AWS (native API + Managed Agents + MCP via IAM credentials)
- Claude Managed Agents shipped self-hosted sandboxes (public beta) and MCP tunnels (research preview) at Code with Claude London event May 19
- Claude Compliance API expanded with 28 enterprise security integrations
- Claude Code Tool Search Tool enables deferred loading with 88.1% accuracy on large MCP libraries
- Claude Code v2.1.139 shipped /goal feature for verifiable end-state autonomous workflows
- Claude Code doubled 5-hour usage limits for Pro/Max/Team/Enterprise

**Cursor:**
- Cursor 3.0 introduced Agents Window: full-screen tiled workspace with parallel multi-repo agents
- /worktree creates isolated git worktrees; /best-of-n runs same prompt across multiple models

**Windsurf:**
- Bundled Devin Cloud agent and Devin Terminal CLI at existing $20/mo Pro tier

**Kiro:**
- Parallel Spec task execution reduces multi-task workflows by up to 4x

**OpenAI/Codex:**
- GPT-5.5 now available in Codex as default for complex coding tasks
- Codex added history search with case-insensitive content matches
- MCP OAuth and per-server environment targeting added

**Google:**
- Genkit Middleware (May 14) added composable hooks for retries, fallbacks, tool approval gates
- LlamaIndex integrated with Google Agents API (May 20) for sandboxed document agents
- Antigravity 2.0 moved to standalone desktop app with Gemini 3.5 Flash as default
- Gemini Spark personal AI agent announced at Google I/O 2026

**New Frameworks:**
- Vellum AI: production-grade with prompt playground + evaluations + versioning + observability
- Mastra: TypeScript-first, workflow-driven with built-in observability
- OpenAI Agents SDK: native sandbox execution, MCP-native tool use, sub-agent handoffs

**Automation:**
- Zapier AI Agents out of beta + MCP support planned; goal-driven autonomous workflows

## Cluster Queue Snapshot

| Cluster | Topics Added |
|---------|-------------|
| AI coding tools | +14 |
| AI for developers | +5 |
| LLM comparison | +1 |
| AI workflow automation | +1 |

## Next Actions

- Queue remains healthy at 2274. No emergency discovery run needed.
- Priority cluster: AI coding tools (Cursor 3.0, Claude self-hosted, Codex GPT-5.5)
- Watch: Claude Platform on AWS penetration — potential high-volume enterprise searches
- Watch: Mastra TypeScript agent framework — early-mover opportunity in TypeScript AI space
