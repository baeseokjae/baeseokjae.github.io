# Strategy Review — 2026-04-25 (Run 50)

**Phase:** 0 (External Data Only — no GSC data yet)
**Topics added:** 15 (all promoted to "queued")
**Priority range:** 1136–1150

---

## New Topics Added

### AI coding tools (+8)
1. `mcp-rce-vulnerability-developer-guide-2026` — OX Security MCP architectural RCE, CVE-2026-30615, 150M+ downloads affected. KD 6, SV 350.
2. `jfrog-cursor-security-plugin-2026` — JFrog enterprise supply chain security plugin for 1M+ Cursor users. KD 4, SV 200.
3. `vercel-context-ai-breach-analysis-2026` — April 19 Vercel breach via Context AI OAuth chain. Developer security lessons. KD 5, SV 300.
4. `letta-code-developer-guide-2026` — Memory-first coding agent with persistent cross-session state. KD 4, SV 250.
5. `mcp-prompt-injection-prevention-guide-2026` — MCP tool poisoning, 7 clients studied, Palo Alto Unit 42 analysis. KD 6, SV 300.
6. `deepsource-ai-code-quality-guide-2026` — AI-powered autofix, CI integration, ranked in Augment Code monorepo benchmark. KD 5, SV 200.
7. `ai-code-review-open-source-tools-2026` — 10 open-source tools on 450K-file monorepo, distinct from paid tool comparisons. KD 7, SV 300.

### AI for developers (+4)
8. `microsoft-agent-framework-devui-guide-2026` — Browser-based agent debugger, real-time graph, tool call timing. KD 4, SV 250.
9. `sap-generative-ai-hub-crewai-guide-2026` — SAP AI Core + CrewAI + LiteLLM enterprise integration. KD 5, SV 200.
10. `azure-foundry-agents-service-guide-2026` — Azure-specific path for OpenAI Assistants API migration (not standard Responses API). KD 5, SV 300.
11. `azure-openai-assistants-foundry-migration-2026` — Migration-first guide with GitHub tool, RBAC/VNet/Entra differences. KD 5, SV 250.

### LLM comparison (+4)
12. `claude-sonnet-4-opus-4-deprecation-guide-2026` — June 15, 2026 retirement, urgent 7-week window. KD 5, SV 400.
13. `claude-sonnet-4-8-preview-2026` — Leaked from Claude Code npm source map (March 31). May 2026 expected. KD 4, SV 350.
14. `gemini-api-free-tier-changes-2026` — Pro models removed April 1, privacy risks on free tier, migration strategies. KD 5, SV 400.
15. `gemini-2-5-flash-thinking-budget-guide-2026` — Hybrid reasoning model config patterns, split billing, production pitfalls. KD 5, SV 350.

---

## Key Signals (Phase 0: Competitor Gap + Topical Cluster)

**MCP Security Surge:** Three distinct MCP security topics now warranted (rce-vulnerability, prompt-injection-prevention, supply-chain via jfrog). This is the fastest-growing subcluster — every developer using Cursor/Claude Code/Windsurf is affected. Competitors have thin coverage.

**API Deprecation Urgency:** Claude Sonnet 4/Opus 4 retiring June 15 + Azure Assistants API retiring August 26 + OpenAI Assistants API August 26 = three overlapping deprecation deadlines driving urgent developer search. Well-timed content can capture high-intent migration traffic.

**Memory-Persistent Agents:** Letta Code fills a gap vs Claude Code's per-session architecture. Distinct enough from letta-code-review-2026 to warrant a how-to guide. Cross-session memory is a growing developer priority as agents become production infrastructure.

**Free Tier Contraction:** Gemini API removing Pro from free tier (April 1) is creating active developer migration intent. Combined with thinking budget complexity in Gemini 2.5 Flash, two articles serve different audience intents (cost migration vs optimization).

**Azure vs OpenAI Migration Paths:** The Azure migration is NOT the same as the standard OpenAI Responses API path — Azure goes to Foundry Agent Service with enterprise governance. This distinction is underserved and creates a valuable "Azure developer" content angle.

---

## Cluster Status (Post-Run 50)

| Cluster | Queued | Writing/Seeded | Published |
|---------|--------|----------------|-----------|
| AI coding tools | 318 | 23 | 27 |
| AI for developers | 246 | 6 | 15 |
| LLM comparison | 104 | 4 | 4 |
| AI workflow automation | 62 | 0 | 5 |
| Unclustered legacy | 1 | — | 48 |

---

## Phase 0 Recommendations

- **No strategy changes needed.** kd_range (0–14) and focus_topics remain well-calibrated.
- **MCP security** is now a de facto sub-cluster within "AI coding tools" — 5 articles queued. Consider adding as a named sub-cluster in next run.
- **API deprecation** content should be prioritized for writing queue given June 15 deadline (7 weeks). Suggest bumping claude-sonnet-4-opus-4-deprecation-guide-2026 and azure-openai-assistants-foundry-migration-2026 to seeded.
- **Gemini free tier changes** article has highest time-sensitivity (retroactive search intent since April 1) — should also be prioritized.
