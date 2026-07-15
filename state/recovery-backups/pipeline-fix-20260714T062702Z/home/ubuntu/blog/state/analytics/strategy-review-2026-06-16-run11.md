# Strategy Review - 2026-06-16 run11

## Phase

Current phase: Phase 1 - First Signal Integration - early GSC signals + expanded KD range.

Phase 1 behavior applies: use external competitor/source discovery, read available analytics, and keep KD range expanded to 0-25. No dedicated GSC query export was present in `state/analytics` during this heartbeat, so this pass stayed external-data-led with the existing strategy-review history used as the early signal context.

## Queue State

- Active queued topics before run: 1
- Candidates evaluated: 20
- Duplicate/rejected candidates skipped before final write: 2
- Promoted to queued: 18
- New priority range: 6505-6522

## Competitor and Source Signals

- Anthropic is publishing deeper agent-runtime guidance around on-demand MCP tool loading, advanced tool use, the Claude Agent SDK, and filesystem/network sandboxing for Claude Code.
- Vercel and GitHub continue to move coding-agent education toward repository-level operating rules: AGENTS.md, custom instructions, agent skills, and environment setup.
- Sourcegraph is competing on enterprise code context with practical posts around context engineering, SCIP-backed MCP code intelligence, and CodeScaleBench for large/multi-repo agent evaluation.
- Sentry is pushing MCP-backed debugging and observability workflows through Seer, XcodeBuildMCP, and real project context for Next.js/Supabase stacks.
- Cloudflare's OpenCode code-review architecture is a current CI-native implementation angle that differs from broad AI code review listicles.
- OpenAI's Codex materials expose narrow follow-ups around the agent loop, parallel app workflows, and workspace agents for shared team automation.

## Topics Added

- 6505. Anthropic On-Demand MCP Tool Loading Guide 2026 (`anthropic-on-demand-mcp-tool-loading-guide-2026`) - AI for developers, KD 5, SV 360
- 6506. Claude Agent SDK Production Harness Guide 2026 (`claude-agent-sdk-production-harness-guide-2026`) - AI coding tools, KD 6, SV 420
- 6507. Claude Code Filesystem and Network Sandboxing Guide 2026 (`claude-code-filesystem-network-sandboxing-guide-2026`) - AI coding tools, KD 6, SV 520
- 6508. GitHub Copilot Custom Instructions Guide 2026: Agent-Ready Repository Rules (`github-copilot-custom-instructions-agent-rules-guide-2026`) - AI coding tools, KD 5, SV 420
- 6509. Vercel AGENTS.md vs Skills Evaluation Guide 2026 (`vercel-agents-md-vs-skills-evaluation-guide-2026`) - AI coding tools, KD 5, SV 340
- 6510. Sentry Next.js Supabase MCP Observability Guide 2026 (`sentry-nextjs-supabase-mcp-observability-guide-2026`) - AI for developers, KD 5, SV 300
- 6511. Cloudflare OpenCode AI Code Review Architecture Guide 2026 (`cloudflare-opencode-ai-code-review-architecture-guide-2026`) - AI coding tools, KD 5, SV 360
- 6512. Sourcegraph CodeScaleBench Enterprise Coding Agent Guide 2026 (`sourcegraph-codescalebench-enterprise-coding-agent-guide-2026`) - AI coding tools, KD 5, SV 300
- 6513. Sourcegraph Context Engineering for Coding Agents Guide 2026 (`sourcegraph-context-engineering-coding-agents-guide-2026`) - AI coding tools, KD 6, SV 520
- 6514. Sourcegraph SCIP MCP Code Intelligence Guide 2026 (`sourcegraph-scip-mcp-code-intelligence-guide-2026`) - AI coding tools, KD 4, SV 260
- 6515. Sentry Seer MCP Debugging Feedback Loop Guide 2026 (`sentry-seer-mcp-debugging-feedback-loop-guide-2026`) - AI for developers, KD 5, SV 340
- 6516. Sentry XcodeBuildMCP iOS Agent Debugging Guide 2026 (`sentry-xcodebuildmcp-ios-agent-debugging-guide-2026`) - AI for developers, KD 5, SV 300
- 6517. GitHub Copilot Visual Studio Custom Agents Guide 2026 (`github-copilot-visual-studio-custom-agents-guide-2026`) - AI coding tools, KD 5, SV 380
- 6518. GitHub Copilot Coding Agent Environment Setup Guide 2026 (`github-copilot-coding-agent-environment-setup-guide-2026`) - AI coding tools, KD 6, SV 440
- 6519. OpenAI Codex Agent Loop Architecture Guide 2026 (`openai-codex-agent-loop-architecture-guide-2026`) - AI coding tools, KD 6, SV 420
- 6520. OpenAI Codex App Parallel Agents Guide 2026 (`openai-codex-app-parallel-agents-guide-2026`) - AI coding tools, KD 5, SV 360
- 6521. OpenAI Workspace Agents ChatGPT Team Automation Guide 2026 (`openai-workspace-agents-chatgpt-team-automation-guide-2026`) - AI workflow automation, KD 6, SV 500
- 6522. GitHub Copilot Agent Mode vs Codex Cloud 2026 (`github-copilot-agent-mode-vs-codex-cloud-2026`) - AI coding tools, KD 7, SV 460

## Validation

Every promoted candidate passed the run checks: KD within 0-25, estimated search volume >= 200, required title/slug/keyword present, focus-topic or cluster-priority fit, no exact slug match in `research/topics.json`, and no published filename match in `content/posts`.

Two initially considered candidates were skipped because exact slugs already existed in `topics.json`: `vercel-ai-sdk-6-agents-guide-2026` and `cloudflare-dynamic-workflows-ai-agents-guide-2026`.

## Strategy Adjustment

Next strategist pass should avoid repeating this run's exact angles unless a materially new product launch adds implementation detail. The strongest remaining gap is implementation content that connects coding-agent context engineering, deterministic repository rules, MCP-backed debugging, and sandbox governance into practical team operating patterns.

## Sources Consulted

- https://www.anthropic.com/engineering/advanced-tool-use
- https://www.anthropic.com/engineering/code-execution-with-mcp
- https://www.anthropic.com/engineering/building-agents-with-the-claude-agent-sdk
- https://www.anthropic.com/engineering/claude-code-sandboxing
- https://vercel.com/blog/agents-md-outperforms-skills-in-our-agent-evals
- https://github.blog/ai-and-ml/github-copilot/5-tips-for-writing-better-custom-instructions-for-copilot/
- https://github.blog/changelog/2026-04-02-github-copilot-in-visual-studio-march-update/
- https://github.blog/ai-and-ml/github-copilot/onboarding-your-ai-peer-programmer-setting-up-github-copilot-coding-agent-for-success/
- https://sourcegraph.com/blog/context-engineering
- https://sourcegraph.com/blog/codescalebench-testing-coding-agents-on-large-codebases-and-multi-repo-software-engineering-tasks
- https://blog.sentry.io/seer-debug-with-ai-at-every-stage-of-development/
- https://blog.sentry.io/sentry-acquires-xcodebuildmcp/
- https://blog.sentry.io/nextjs-supabase-observability/
- https://blog.cloudflare.com/ai-code-review/
- https://openai.com/index/unrolling-the-codex-agent-loop/
- https://openai.com/index/introducing-the-codex-app/
- https://openai.com/index/introducing-workspace-agents-in-chatgpt/
