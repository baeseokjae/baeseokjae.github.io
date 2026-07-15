# Strategy Review — 2026-04-18 (Run 10)

## Phase: 0 (Foundation — External Data Only)

## Topics.json Sync (Housekeeping)

**48 retroactively tracked published articles added to topics.json**

Prior runs had been tracking 22 published articles; the actual posts/ directory contained 74. This run reconciles the gap:

- 48 articles that existed in posts/ but had no topics.json entry → added as `published`
- 4 articles with wrong status in topics.json → corrected to `published`:
  - `activepieces-review-2026` (was queued)
  - `ai-for-backend-developers-2026` (was queued)
  - `best-ai-code-review-tools-2026` (was rejected)
  - `claude-code-hooks-guide-2026` (was queued)

**Updated totals after sync:**

| Status | Count |
|--------|-------|
| published | 70 |
| queued | 111 |
| writing | 13 |
| seeded | 12 |
| rejected | 1 |
| **Total** | **207** |

**Note:** 33 of the 70 published articles are unclustered (pre-date cluster tagging). Retroactive cluster assignment is a lower-priority follow-up task.

---

## Topic Discovery — 7 New Topics Added

All 7 promoted to `queued`. KD and SV validated against strategy.json kd_range (0–14) and min SV 200.

### LLM Comparison (+4)

**Mistral Medium 3 Review 2026** — KD 5, SV 300
April 9 open-weight release. EU AI Act compliance metadata, strong European language support. $0.40/M input, $2.00/M output. Near-zero review coverage — early mover advantage.

**Arcee Trinity Review 2026** — KD 3, SV 200
399B Apache 2.0 model from Arcee AI. Trinity-Large-Preview was #1 used open model in the US (80.6B tokens peak). Enterprise-deployable without licensing restrictions. Very low competition.

**Qwen 3.6 Plus Coding Guide 2026** — KD 4, SV 250
Alibaba's open-weight model leads 5 of 8 coding benchmarks including LiveCodeBench and SWE-bench. Strongest open-weight choice for coding deployments. Near-zero SERP coverage.

**Mistral vs Qwen Comparison 2026** — KD 6, SV 250
EU vs China open-weight showdown. Mistral Medium 3 (EU compliance) vs Qwen 3.6 Plus (coding leader). Distinct strengths → clear comparison value. Low KD gap.

**Open Source LLM Coding Comparison 2026** — KD 9, SV 400
Six major open-weight labs now competing: Gemma 4, Qwen 3.6 Plus, GLM-5.1, Arcee Trinity, Llama 4, Mistral Medium 3. Developer decision article with strong search intent. Thin SERP coverage.

### AI Coding Tools (+2)

**JetBrains Central Review 2026** — KD 5, SV 300
Launched March 24, 2026. JetBrains' open system for agentic software development — IDE-agnostic agent coordination. Introduces JetBrains ACP protocol (parallel to Zed's ACP). Near-zero competition. Strong comparison angle with Cursor 3 Agents Window and Kiro.

**AI Developer Tools Survey 2026** — KD 7, SV 350
Based on JetBrains AI Pulse January 2026 survey (10,000+ professional developers, 8 languages):
- 90% regularly use at least one AI tool at work
- 74% use specialized AI coding tools (not just general chatbots)
- 22% use AI coding agents
- 66% of companies plan agent adoption within 12 months
- 51% of GitHub commits are AI-assisted

High-value data-driven article. Strong for organic backlinks. KD 7 sits just within range.

---

## Cluster Health (Post-Run 10)

| Cluster | Published | Queued | Writing | Status |
|---------|-----------|--------|---------|--------|
| AI coding tools | 13 | 47 | 9 | Well-stocked ✅ |
| AI for developers | 13 | 28 | 1 | Healthy ✅ |
| LLM comparison | 6 | 20 | 2 | Publishing needed ⚠️ |
| AI workflow automation | 5 | 15 | 0 | Publishing needed ⚠️ |
| unclustered | 33 | 1 | — | Retroactive tagging needed |

**Recommended publishing focus:**
1. LLM comparison cluster — 20 queued but only 6 published; Claude Opus 4.7 review is oldest unserved intent
2. AI workflow automation — 15 queued with 0 in writing; n8n and Zapier topics are evergreen

---

## Key Market Signals — April 2026

### Open-Weight Coding Model Surge
Six major labs shipped competitive open-weight models in the first 12 days of April:
- **Qwen 3.6 Plus** (Alibaba) — coding benchmark leader, open license
- **Arcee Trinity** (399B, Apache 2.0) — #1 US open model by usage
- **GLM-5.1** (MIT) — coding benchmark beats GPT-5.4
- **Gemma 4** (Google, April 2) — Apache 2.0, #3 open model on Arena AI
- **Llama 4** (Meta) — competitive multimodal open weights
- **Mistral Medium 3** (April 9) — EU-focused open weights

**Editorial angle:** Open-source coding models are closing the gap with proprietary APIs faster than expected. An open-source coding comparison article (already queued) should be prioritized.

### JetBrains Developer Ecosystem Data (April 2026)
Fresh survey data (10K+ devs) with strong organic link potential:
- 90% of developers regularly use AI tools
- 22% already use coding agents
- 66% company-level agent adoption planned within 12 months
- 74% use specialized coding assistants (not just general chatbots)

This data can anchor multiple articles: AI developer survey roundup, JetBrains Central review, coding agent adoption guide.

### JetBrains Central: New Agentic Platform
March 24 launch creates a new article category: IDE-native agent coordination. Distinct from Cursor 3's Agents Window and Claude Code. Worth covering before competitors do.

---

## Publishing Priorities (Updated)

1. **claude-opus-4-7-review-2026** — 2-day-old flagship, highest urgency
2. **open-source-llm-coding-comparison-2026** — 6 new open models, fresh market signal
3. **qwen-3-6-coding-guide-2026** — coding benchmark leader, barely covered
4. **jetbrains-central-review-2026** — new platform, near-zero competition
5. **ai-developer-tools-survey-2026** — fresh data, backlink bait

---

## No Phase Changes This Run

Phase 0 → Phase 1 requires `indexed_ratio > 0.9 AND days_since_launch > 30`. Blog is ~18 days old. Continue Phase 0 strategy.

---

*Generated by Strategist agent — Run 10 — 2026-04-18*

---

# Addendum — Run 11 (2026-04-18, third heartbeat)

## Status Maintenance

- `writing` sync check: 13 topics in `writing` status confirmed — none have corresponding .md files yet (all legitimately in progress)

## Additional Topics Discovered (+3)

### AI Coding Tools
- **Anthropic Agentic Coding Trends Report 2026** — KD 6, SV 400. Official Anthropic report on 8 trends reshaping dev workflows. Key data: developers use AI 60% of work but fully delegate only 0–20% of tasks. High developer interest, strong backlink potential.
- **Cursor + Claude Code + Codex Composable Stack 2026** — KD 5, SV 300. The New Stack coverage highlights emerging narrative: Cursor (orchestration) + Claude Code (execution) + Codex (review) used as composable layers. OpenAI shipped official Claude Code plugin. Early mover on this workflow framing.

### AI for Developers
- **OpenAI Agents SDK v2 Guide 2026** — KD 5, SV 250. April 15 release. Configurable memory, sandbox-aware orchestration, Codex-like filesystem tools. Differentiates from existing `openai-agents-sdk-tutorial-2026` via update/v2 angle.

## Queue Totals (End of Run 11)
- **Total topics in topics.json:** 217
- **Queued:** 120
- **Published (tracked):** 71
- **Writing:** 13

*Addendum by Strategist agent — Run 11 — 2026-04-18*
