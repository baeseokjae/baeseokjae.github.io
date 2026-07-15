# Strategy Review — 2026-04-20 (Run 23)

## Phase: 0 (Foundation — External Data Driven)

## Queue Status

| Cluster | Queued | Published | Total |
|---|---|---|---|
| AI coding tools | 136 | 22 | 158+ |
| AI for developers | 70 | 9 | 79+ |
| LLM comparison | 41 | 1 | 42+ |
| AI workflow automation | 28 | 3 | 31+ |
| unclustered_legacy | 1 | 49 | 50 |
| **Total queued** | **257** | — | — |

Queue is healthy at 257. No shortage risk.

## New Topics Added (15 queued, 1 rejected)

### AI coding tools (+6)
- `kilo-code-review-2026` — Cline fork with orchestrator mode, KD 4, SV 250
- `cline-alternatives-2026` — 5M VS Code installs, high comparison intent, KD 6, SV 500
- `claude-code-alternatives-2026` — growing terminal agent comparison intent, KD 7, SV 450
- `claude-code-vs-cline-2026` — direct comparison gap, KD 6, SV 350
- `open-source-ai-coding-agents-2026` — comprehensive ranking, KD 7, SV 500
- `ai-coding-tools-adoption-2026` — JetBrains 10K survey data angle, KD 5, SV 300

### AI for developers (+5, 1 rejected)
- `aikido-security-review-2026` — AI SAST at $300/month vs Veracode $15K/year, KD 5, SV 300
- `veracode-alternatives-2026` — strong comparison intent, KD 6, SV 350
- `aikido-vs-veracode-2026` — head-to-head, KD 5, SV 250
- `zeropath-review-2026` — autonomous PR auto-remediation, KD 3, SV 200
- REJECTED: `ai-generated-code-security-2026` — duplicate slug already exists

### LLM comparison (+3)
- `gpt-6-vs-claude-opus-4-7-vs-gemini-3-2026` — GPT-6 launched April 14, 2M context, HumanEval 95%+, KD 6, SV 500
- `claude-mythos-vs-gpt-6-2026` — frontier model comparison, KD 4, SV 300
- `best-llm-for-agents-2026` — high practical developer intent, KD 8, SV 450

### AI workflow automation (+2)
- `mastra-vs-agno-vs-strands-2026` — TypeScript vs Python agent framework gap, KD 5, SV 250
- `ai-agent-frameworks-overview-2026` — comprehensive 14-framework guide, KD 7, SV 400

## Phase 0 Competitor Gap Analysis

**Key signals found:**
- AI coding CLI tools have exploded (30+ tools per DEV.to survey) — our `ai-coding-cli-tools-comparison-2026` already covers this
- Cline at 5M VS Code installs — #1 open-source coding agent — high intent for alternatives/comparisons
- GPT-6 released April 14 — 2M context, 40% improvement, HumanEval 95%+ — LLM comparison cluster needs this
- AI-generated code security surged 170% in vulnerabilities — SAST/DAST articles needed; Aikido and ZeroPath are underrepresented
- Kilo Code (Cline/Roo fork) gaining traction — not previously in topics
- Security tools (Aikido, Veracode alternatives) have clear comparison intent and very low KD

**Competitor coverage gaps we're filling:**
- morphllm.com has "Cline alternatives" but no comprehensive open-source agent guide
- qodo.ai has Roo vs Cline but no broader ecosystem comparison
- No competitor has a good "AI coding tools adoption data 2026" piece (JetBrains survey angle)
- Security tooling (SAST/DAST) is almost entirely absent from AI coding tool blogs

## Cluster Audit

All four focus clusters have strong queues (28–136). Cluster priority is met for AI coding tools and AI for developers. LLM comparison and AI workflow automation have room to grow but are adequately seeded.

**Orphan concern:** 49 published articles in `unclustered_legacy` have no cluster assignment and likely 0 inbound links from cluster-specific content. Recommend retroactive cluster assignment when a content ops task is scheduled.

## Strategy Recommendation

No changes to `kd_range` (stay 0–14 in Phase 0). The security tooling angle (SAST/DAST for AI-generated code) is a new sub-niche worth prioritizing — low KD, strong developer pain point, no competition from AI coding blogs. Add to `new_opportunities` in next strategy update.

No phase transition yet — need indexed_ratio > 0.9 AND days_since_launch > 30 to enter Phase 1.
