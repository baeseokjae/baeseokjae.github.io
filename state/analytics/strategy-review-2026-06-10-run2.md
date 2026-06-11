# Strategy Review - 2026-06-10 Run 2

## Phase 1 Status

- Current phase: Phase 1 (First Signal Integration)
- KD range: 0-25
- Search volume filter: 200+ estimated monthly searches
- Analytics files found: prior strategy reviews only; no separate GSC query export was present in `~/blog/state/analytics/`
- Queue health before run: 3033 total topics, 2366 queued
- Queue health after run: 3051 total topics, 2384 queued

## New Topics Added This Run (+18)

### AI For Developers (+9)

1. `modal-evals-inference-time-compute-scaling-guide-2026` - Modal evals inference-time compute scaling. KD 4, SV 260
2. `neon-agent-skills-2026-guide` - Neon Agent Skills 2026. KD 5, SV 420
3. `neon-full-stack-ai-agent-guide-2026` - Neon full-stack AI agent. KD 5, SV 380
4. `neon-agent-platforms-companion-skill-guide-2026` - Neon for agent platforms companion skill. KD 4, SV 300
5. `neon-mcp-safety-cheatsheet-guide-2026` - Neon MCP safety cheatsheet. KD 4, SV 280
6. `supabase-ai-agents-use-it-right-guide-2026` - Supabase AI agents use it right. KD 4, SV 260
7. `sentry-ai-agent-observability-guide-2026` - Sentry AI agent observability. KD 5, SV 360
8. `sentry-seer-ai-agent-legal-review-guide-2026` - Sentry Seer AI agent legal review. KD 3, SV 220
9. `sentry-mcp-server-guide-2026` - Sentry MCP Server. KD 4, SV 340

### AI Coding Tools (+6)

1. `windsurf-cascade-neon-mcp-database-guide-2026` - Windsurf Cascade Neon MCP database. KD 4, SV 340
2. `sentry-xcodebuildmcp-agent-ios-macos-guide-2026` - XcodeBuildMCP AI agents iOS macOS. KD 4, SV 300
3. `gitlab-duo-agent-platform-public-beta-guide-2026` - GitLab Duo Agent Platform public beta. KD 5, SV 420
4. `gitlab-agentic-tools-trust-guide-2026` - GitLab agentic tools trust. KD 4, SV 260
5. `gitlab-duo-cli-governance-guide-2026` - GitLab Duo CLI governance. KD 4, SV 280
6. `gitlab-agentic-coding-context-guide-2026` - GitLab agentic coding context. KD 5, SV 320

### LLM Comparison (+2)

1. `mellum2-private-ai-software-engineering-model-guide-2026` - Mellum2 private AI software engineering. KD 4, SV 320
2. `modal-llama-human-eval-search-scaling-guide-2026` - Modal Llama HumanEval search scaling. KD 3, SV 220

### AI Workflow Automation (+1)

1. `gitlab-automated-merge-request-workflow-guide-2026` - GitLab automated merge request workflow. KD 4, SV 300

## Candidate Validation

All promoted candidates passed:

- KD within configured range (0-25)
- Search volume estimate >= 200
- Unique slug across `topics.json` and published post filenames
- Required title, slug, and keyword present
- Cluster fits current focus topics or cluster priority

Rejected this run: 0

## Competitor Signals

- Neon is building a focused agent database story around Agent Skills, platform companion skills, Windsurf Cascade MCP, and MCP safety. This is a strong internal-link target for MCP, Postgres, and agent infrastructure content.
- Sentry's agent content has moved beyond observability into MCP, native Apple build/test agents, and legal review of its Seer agent. This supports both developer workflow and enterprise trust angles.
- GitLab is positioning Duo as an agent orchestration platform, with adjacent narratives around merge-request automation, CLI governance, trust, and context quality.
- Modal continues to publish applied evaluation and inference-time compute pieces that translate well into advanced LLM comparison and agent performance topics.
- JetBrains' Mellum2 positioning creates a low-KD private software-engineering model topic distinct from the already-covered JetBrains survey and Junie CLI review articles.

## Strategy Adjustments

- Keep Phase 1 behavior. No Phase 2 performance logic was applied because no separate GSC query export exists yet.
- Add more weight to database-backed agent workflows: Postgres branching, MCP safety, agent skills, and agent-driven database operations.
- Add enterprise trust and governance as a cross-cluster thread: GitLab Duo governance, Sentry legal review, and MCP safety should link back to AI agent governance and enterprise AI coding security coverage.
- Avoid additional generic survey and sandbox comparison topics for now; those are already covered or queued. Favor tool-specific operating guides and implementation checklists.

## Sources Reviewed

- JetBrains Junie CLI beta: https://blog.jetbrains.com/junie/2026/03/junie-cli-the-llm-agnostic-coding-agent-is-now-in-beta/
- JetBrains AI Blog: https://blog.jetbrains.com/ai/
- Modal top code agent sandboxes: https://modal.com/blog/top-code-agent-sandbox-products
- Modal evals and inference-time compute: https://modal.com/blog/qart-codes-evals
- Modal Llama HumanEval search scaling: https://modal.com/blog/llama-human-eval
- Neon Agent Skills: https://neon.com/blog/agent-skills-in-2026
- Neon full-stack AI agent: https://neon.com/blog/how-to-build-a-full-stack-ai-agent
- Neon for agent platforms: https://neon.com/blog/neon-for-agent-platforms
- Neon Windsurf Cascade MCP: https://neon.com/blog/cascade-and-neon-mcp
- Neon MCP safety cheatsheet: https://neon.com/blog/mcp-safety-cheatsheet
- Supabase agent guidance: https://supabase.com/blog
- Sentry Engineering: https://blog.sentry.io/engineering/
- Sentry MCP server: https://blog.sentry.io/yes-sentry-has-an-mcp-server-and-its-pretty-good/
- GitLab Duo Agent Platform: https://about.gitlab.com/blog/gitlab-duo-agent-platform-public-beta/
- GitLab automated MR workflow: https://about.gitlab.com/blog/transform-mrs-to-automated-workflow/
- GitLab agentic trust: https://about.gitlab.com/blog/building-trust-in-agentic-tools-what-we-learned-from-our-users/
- GitLab Duo CLI governance: https://about.gitlab.com/blog/gitlab-duo-cli-governance/
- GitLab agentic coding context: https://about.gitlab.com/blog/agentic-coding-only-as-good-as-context/
