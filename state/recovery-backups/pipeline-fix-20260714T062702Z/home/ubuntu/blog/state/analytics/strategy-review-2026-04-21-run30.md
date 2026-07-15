# Strategy Review — 2026-04-21 (Run 30)

## Phase: 0 — External Data Only

## Queue Health

| Cluster | Queued | Published | Target |
|---|---|---|---|
| AI coding tools | 133 | 22 | 20+ ✓ |
| AI for developers | 72 | 9 | 20+ 🔶 |
| LLM comparison | 32 | 1 | 20+ 🔶 |
| AI workflow automation | 24 | 3 | 20+ 🔶 |

Queue is at 379+ queued topics. Content velocity remains the constraint.

## New Topics Added This Run: 17

### AI for developers (+12)
- `tokenmaxxing-ai-coding-trap-2026` — TechCrunch April 17 viral piece, KD 4, SV 350
- `ai-coding-roi-measurement-2026` — beyond vanity metrics, KD 5, SV 300
- `salesforce-agentic-work-units-guide-2026` — AWU counter-metric to tokenmaxxing, KD 4, SV 250
- `jetbrains-ai-developer-workflows-2026` — April 2026 research on actual impact, KD 5, SV 280
- `enterprise-ai-coding-shadow-it-2026` — 57% using AI without approval, KD 7, SV 320
- `eu-ai-act-developer-compliance-2026` — August 2026 enforcement deadline, KD 8, SV 400
- `ai-code-security-scanning-tools-2026` — Snyk vs Checkmarx vs Veracode vs Black Duck, KD 9, SV 450
- `enterprise-ai-coding-governance-2026` — shadow AI policies + compliance, KD 8, SV 350
- `jpmorgan-ai-coding-enterprise-case-study-2026` — 60K devs, 30% velocity gain, KD 6, SV 280
- `jellyfish-ai-coding-productivity-study-2026` — 7548 engineers, 2x PRs at 10x cost, KD 4, SV 260
- `ai-coding-accepted-code-quality-2026` — 80-90% acceptance rate misleading, KD 5, SV 300
- `cto-ai-coding-tool-checklist-2026` — enterprise eval framework, KD 7, SV 300

### AI coding tools (+4)
- `jetbrains-acp-agent-registry-guide-2026` — connect AI agents to IDE via ACP, KD 4, SV 230
- `jetbrains-central-agentic-platform-guide-2026` — Early Access Q2 2026, KD 4, SV 250
- `claude-code-developer-satisfaction-2026` — 91% satisfaction, NPS 54, loyalty leader, KD 4, SV 280
- `ai-coding-tool-switching-costs-2026` — BYOK portability + stealth friction, KD 5, SV 240

### LLM comparison (+1)
- `gpt-6-spud-api-preparation-guide-2026` — pretraining done, 78% Polymarket odds April 30, KD 5, SV 600

## Key Discoveries This Run

### 1. Tokenmaxxing Is the #1 New Developer Story (High Priority)
TechCrunch April 17 article went viral. Jellyfish data: 7,548 engineers, largest token budgets generated 2x PRs at 10x token cost. Real code acceptance rate drops from 80-90% to 10-30% after revisions. Salesforce launched AWU metric as counter-metric. No comprehensive developer guide exists yet.

### 2. GPT-6 (Spud) Anticipation Building
Pretraining confirmed complete March 24. Polymarket 78% odds by April 30. Developer angle: "how do I future-proof my API apps before GPT-6 drops?" — no one has written this yet.

### 3. Enterprise Governance Gap Exploding
57% of developers using AI without IT approval. EU AI Act enforcement August 2026. McKinsey 4,500-dev study (February 2026): 46% faster routine tasks but 23% higher bug density when not reviewed. Enterprise CTO content underserved despite high search intent.

### 4. JetBrains Research April 2026
New study on actual workflow impact (not adoption). ACP Agent Registry live. Central platform in Early Access Q2 2026. JetBrains audience (Java/Kotlin) underserved vs Cursor/Copilot content.

## Competitor Gap Analysis

- **TechCrunch**: breaking news on tokenmaxxing — no practical developer guide follow-up
- **JetBrains blog**: first-party research data — no how-to depth on findings
- **Jellyfish / Faros / METR**: engineering metrics data — no actionable dev guide layer
- **Checkmarx / Veracode**: security tool vendors — comparison gap vs neutral developer perspective

**Gaps to own**: tokenmaxxing practical guide, GPT-6 prep guide, enterprise governance, EU AI Act developer angle

## Cluster Priority Recommendation

1. **AI for developers** → tokenmaxxing + jellyfish study cluster (hot right now, low KD)
2. **LLM comparison** → GPT-6 prep guide ahead of launch (timing window closing)
3. **AI coding tools** → claude-code-developer-satisfaction (unique data angle, KD 4)

## Phase Transition Check
Phase 1 trigger: `indexed_ratio > 0.9 AND days_since_launch > 30` — not yet reached. Stay Phase 0.
