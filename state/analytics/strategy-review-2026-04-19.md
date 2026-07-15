# Strategy Review — 2026-04-19 (Run 16)

**Phase:** 0 (Days 0-30, external data only)
**Date:** 2026-04-19

---

## Topic Queue Status

| Cluster | Queued | Seeded | Published | Total |
|---|---|---|---|---|
| AI coding tools | 83 | 10 | 21 | 114 |
| AI for developers | 39 | 2 | 9 | 50 |
| LLM comparison | 22 | 1 | 1 | 24 |
| AI workflow automation | 16 | 0 | 3 | 19 |
| unclustered_legacy | 1 | 0 | 49 | 50 |

**Queue health:** Healthy. 160 queued total (well above 10 threshold).

---

## Competitor Gap Analysis

Searched competitor blogs (LogRocket, DEV.to, faros.ai, JetBrains Research, The New Stack) for topics with search volume 200+ and KD ≤14 that we haven't covered.

### Key gaps identified this run:

**AI code security (new sub-cluster emerging):**
- Snyk vs Semgrep SAST comparison — competitors (Corgea, AppSec Santa, DEV.to) ranking for this, we have nothing
- AI SAST tools comparison — Corgea, DryRun Security dominating, high developer intent
- Corgea AI-native SAST — very low KD (4), no major blog reviews yet
- SonarQube AI CodeFix — widely used, review gap in developer-focused blogs

**Local AI agents (growing trend):**
- Local AI agents guide (Ollama + Cline) — 5+ tutorials seen on DEV.to, LogRocket, geeky-gadgets
- AnythingLLM — local knowledge base + agent runtime, covered by generic AI blogs but not developer-focused sites

**Design-to-code workflow:**
- Figma MCP server guide — Figma launched MCP in June 2025, now expanding; LogRocket has one article, competitor gap for developer-focused tutorial

**PR automation:**
- Sweep AI — GitHub issue → PR automation, JetBrains integration; covered by aiagentslist.com and bestagentpick.com but no developer blog review
- Cursor BugBot — security scanning per PR, near-zero competition in dev blogs

**Workflow automation gaps:**
- n8n MCP integration — n8n is MCP-enabled but no tutorial yet in our niche
- Make.com AI Agents (Maia) — launched early 2026, competitor gap
- Make vs n8n two-way comparison — we have the 3-way but direct comparison has separate search intent

---

## Topical Cluster Audit

**AI coding tools (83 queued):** Well covered. Strong on IDE comparisons, terminal agents, LLM coding reviews. New gap: AI security tooling within coding workflow (BugBot, Sweep AI).

**AI for developers (39 queued):** Good. New security sub-cluster (SAST tools) added. Also local AI development increasingly searched.

**LLM comparison (22 queued):** Adequate. Covers major models. Consider expanding to inference benchmarks and cost-per-task comparisons.

**AI workflow automation (16 queued):** Thin relative to 20+ target. Added 5 new topics (+MCP integration, Make AI Agents, cost comparison, Make vs n8n, benchmarks). Now at 16 queued. Priority: continue adding here.

---

## Key Market Observations (April 2026)

1. **AI code security is emerging as a distinct cluster** — SAST tools are adding AI (Snyk Code, Semgrep Assistant, Checkmarx Assist). Developer intent is shifting from "is this secure?" to "fix it automatically."

2. **Local AI agents are mainstream** — 70B models handle 70-80% of daily tasks at cloud quality. Ollama crossed 52M monthly downloads. This is no longer niche.

3. **Figma MCP is a major workflow shift** — Design-to-code and code-to-design are both now supported. Competitor coverage thin in developer-focused blogs.

4. **AI coding market = $12.8B in 2026** — 84% of developers using or planning to adopt AI tools. Claude Code at 18% developer adoption (6x growth from April 2025).

5. **n8n MCP integration** — n8n instances can now be called by Claude and other AI tools via MCP. High tutorial intent, barely covered.

---

## Actions Taken This Run

- Added 16 new topics to topics.json (all validated → queued):
  - 4 AI coding tools: Sweep AI, Figma MCP, Cursor BugBot, Goose AI
  - 7 AI for developers: Snyk vs Semgrep, Corgea, Local AI agents, AnythingLLM, AI SAST comparison, SonarQube AI, AutoAgent
  - 5 AI workflow automation: n8n MCP, Make AI Agents, cost comparison, Make vs n8n, benchmarks
- Updated cluster counts in strategy.json

## Next Run Priorities

1. Add more AI workflow automation topics (target: 20+ queued)
2. Monitor AI code security cluster — may warrant its own cluster once 10+ topics added
3. Check unclustered_legacy (49 articles) — retroactive cluster assignment would improve internal link strategy
