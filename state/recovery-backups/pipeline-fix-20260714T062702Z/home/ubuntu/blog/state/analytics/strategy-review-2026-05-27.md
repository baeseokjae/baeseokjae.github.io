# Strategy Review — 2026-05-27

## Phase 1 Status

- **Current phase**: Phase 1 (First Signal Integration)
- **KD range**: 0-25
- **Search volume filter**: 200+ estimated monthly searches
- **Published posts tracked in topics.json**: 446
- **Queue health**: 2727 total topics, 2195 queued — healthy, no emergency shortage
- **Analytics files found**: prior strategy reviews only; no separate GSC query export was present in `~/blog/state/analytics/`

## New Topics Added This Run (+20)

### AI Coding Tools (+13)
1. `claude-agent-containment-guide-2026` — Claude agent containment. KD 5, SV 450
2. `codex-windows-sandbox-guide-2026` — Codex Windows sandbox. KD 4, SV 300
3. `codex-enterprise-safety-controls-guide-2026` — Codex enterprise safety controls. KD 5, SV 380
4. `github-copilot-app-technical-preview-guide-2026` — GitHub Copilot app technical preview. KD 6, SV 420
5. `github-copilot-agent-merge-guide-2026` — GitHub Copilot Agent Merge. KD 5, SV 300
6. `superset-multi-agent-ide-review-2026` — Superset multi-agent IDE. KD 4, SV 240
7. `sourcegraph-agentic-coding-big-code-guide-2026` — agentic coding big codebases. KD 6, SV 430
8. `sourcegraph-code-search-vs-deep-search-vs-mcp-2026` — code search vs deep search vs MCP. KD 5, SV 350
9. `codescalebench-coding-agents-benchmark-guide-2026` — CodeScaleBench coding agents benchmark. KD 4, SV 260
10. `amp-librarian-oracle-subagents-guide-2026` — Amp Librarian Oracle subagents. KD 4, SV 220
11. `codex-remote-devbox-ssh-guide-2026` — Codex remote devbox SSH. KD 5, SV 280
12. `deepsec-agent-security-harness-guide-2026` — DeepSec agent security harness. KD 3, SV 210
13. `multi-agent-development-control-plane-guide-2026` — multi-agent development control plane. KD 6, SV 400

### AI for Developers (+7)
1. `vercel-ai-gateway-production-index-2026` — Vercel AI Gateway production index. KD 6, SV 500
2. `vercel-chat-sdk-ai-tools-guide-2026` — Vercel Chat SDK AI tools. KD 5, SV 260
3. `modal-claude-managed-agents-sandboxes-guide-2026` — Modal Claude Managed Agents sandboxes. KD 4, SV 300
4. `claude-managed-agents-vs-agent-sdk-2026` — Claude Managed Agents vs Agent SDK. KD 5, SV 320
5. `applied-compute-specific-intelligence-agents-guide-2026` — Specific Intelligence agents. KD 4, SV 220
6. `enterprise-agent-rl-fine-tuning-guide-2026` — enterprise agent RL fine tuning. KD 6, SV 360
7. `gitbook-ai-crawler-docs-optimization-2026` — AI crawler documentation optimization. KD 5, SV 260

## Candidate Validation

All promoted candidates passed:

- KD within configured range (0-25)
- Search volume estimate >= 200
- Unique slug across `topics.json` and published post filenames
- Required title, slug, and keyword present
- Cluster fits current focus topics or cluster priority

Rejected this run: 0

## Competitor Signals

- Anthropic is making agent containment a first-class engineering topic after publishing concrete Claude containment lessons. This supports a security/sandboxing subcluster around Claude Code and enterprise agent deployment.
- OpenAI is publishing detailed Codex safety and Windows sandbox engineering posts. The gap is practical developer coverage that translates those controls into enterprise rollout checklists.
- GitHub's Copilot app technical preview creates new searches around desktop agent sessions, isolated work, and Agent Merge.
- Vercel is publishing production AI Gateway data and Chat SDK agent tooling. This supports model-routing and TypeScript agent implementation topics.
- Sourcegraph is pushing the “big codebase context” narrative: code search, Deep Search, MCP, and benchmarks for multi-repo agent work.
- Modal and Applied Compute point to the next enterprise layer: managed agent sandboxes and company-specific RL loops.

## Cluster Queue Snapshot

| Cluster | Queued |
|---|---:|
| AI coding tools | 728 |
| AI for developers | 731 |
| LLM comparison | 375 |
| AI workflow automation | 361 |

## Strategy Adjustments

- Keep Phase 1 behavior. No Phase 2 performance logic was applied because there is no separate GSC query export available.
- Add emphasis on “agent runtime safety” across AI coding tools and AI for developers: containment, sandboxing, telemetry, approval gates, and blast-radius reduction.
- Prioritize practical explainers over broad news rewrites. Competitors are publishing primary announcements; the opportunity is implementation guidance with checklists, diagrams, and rollout tradeoffs.
- Maintain cluster priority: AI coding tools and AI for developers remain the highest-yield clusters, while LLM comparison and workflow automation have enough queue depth.

## Sources Reviewed

- Anthropic Engineering — How we contain Claude across products: https://www.anthropic.com/engineering/how-we-contain-claude
- OpenAI — Running Codex safely at OpenAI: https://openai.com/index/running-codex-safely/
- OpenAI — Building a safe, effective sandbox to enable Codex on Windows: https://openai.com/index/building-codex-windows-sandbox/
- GitHub Changelog — GitHub Copilot app technical preview: https://github.blog/changelog/2026-05-14-github-copilot-app-is-now-available-in-technical-preview
- Vercel — Chat SDK now includes AI SDK tools: https://vercel.com/changelog/chat-sdk-now-includes-ai-sdk-tools
- Vercel — AI Gateway production index: https://vercel.com/blog
- Vercel — Superset multi-agent IDE customer story: https://vercel.com/blog/how-superset-built-the-ide-for-ai-agents-on-vercel
- Sourcegraph — Agentic Coding in 2026: https://sourcegraph.com/blog/agentic-coding
- Sourcegraph Blog index: https://sourcegraph.com/blog
- Modal — Claude Managed Agents with Modal Sandboxes: https://modal.com/blog/introducing-claude-managed-agents-with-modal-sandboxes
- Modal — Scaling Reinforcement Learning at Applied Compute: https://modal.com/blog/applied-compute-reinforcement-learning
