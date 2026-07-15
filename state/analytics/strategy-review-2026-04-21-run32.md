# Strategy Review — 2026-04-21 (Run 32)

## Phase: 0 — External Data Only

## Queue Health

| Cluster | Queued | Writing | Published | Target |
|---|---|---|---|---|
| AI coding tools | 187 | 8 | 24 | 20+ ✓ |
| AI for developers | 147 | 4 | 13 | 20+ 🔶 |
| LLM comparison | 48 | 0 | 4 | 20+ 🔶 |
| AI workflow automation | 30 | 0 | 5 | 20+ 🔶 |

Total queued: 413. Content velocity remains the constraint — queue is extremely healthy.

## New Topics Added This Run: 18

### AI coding tools (+10)
- `openai-codex-app-macos-guide-2026` — Codex macOS multi-agent command center, parallel agents + Git worktrees, KD 5, SV 350
- `windsurf-plan-mode-guide-2026` — Windsurf Plan Mode Wave 13 feature, structured task planning, KD 4, SV 280
- `jetbrains-ai-coding-tools-usage-2026` — JetBrains April 2026 survey: which tools devs actually use at work, KD 5, SV 280
- `computer-use-agents-comparison-2026` — Claude vs Codex vs Gemini computer use for developers, KD 6, SV 400
- `codex-background-computer-use-2026` — OpenAI Codex Background Computer Use April 16 launch guide, KD 5, SV 300
- `claude-opus-4-api-developer-guide-2026` — Claude Opus 4 API: $15/$75/M tokens, 200K context, xhigh effort, KD 5, SV 400
- `claude-4-api-migration-guide-2026` — Breaking API changes from Claude 3 to 4 (budget_tokens removed), KD 5, SV 380
- `ai-dev-tool-power-rankings-2026` — Power rankings digest: LogRocket/Pragmatic Engineer 2026 analysis, KD 6, SV 350
- `github-copilot-market-share-2026` — 37% market share but challengers closing in, KD 8, SV 420
- `claude-code-arr-ecosystem-analysis-2026` — Claude Code $2.5B ARR: ecosystem analysis, KD 4, SV 250

### AI for developers (+6)
- `code-agent-orchestra-patterns-2026` — What makes multi-agent coding actually work (Addy Osmani angle), KD 5, SV 300
- `jetbrains-ai-impact-developer-workflows-2026` — JetBrains: Understanding AI's real impact on developer workflows, KD 5, SV 260
- `ai-coding-layered-multi-tool-guide-2026` — 70% of devs use 2-4 tools: building a layered AI workflow, KD 6, SV 350
- `ai-coding-fortune-500-enterprise-guide-2026` — 78% Fortune 500 using AI coding in production, KD 7, SV 320
- `long-running-ai-coding-agents-guide-2026` — Execution loops vs single-prompt: long-running agent workflows, KD 5, SV 280
- `ai-generated-github-code-statistics-2026` — 51% of GitHub code is AI-generated: what this means for devs, KD 7, SV 450

### LLM comparison (+2)
- `qwen-3-6-local-deployment-2026` — Qwen 3.6-35B-A3B: 3B active params, 73.4% SWE-bench, local deploy guide, KD 4, SV 260
- `glm-5-1-swe-bench-pro-deployment-2026` — GLM-5.1: 744B MIT-licensed, 58.4% SWE-Bench Pro, deployment, KD 3, SV 240

## Key Discoveries This Run

### 1. April 2026 Model Release Wave — Most Crowded Month Ever
Nine significant models shipped from six organizations by April 14:
- **Claude 4 family** (April 2): Opus 4 ($15/$75/M), Sonnet 4 ($3/$15/M), 200K context — **BREAKING API CHANGES** (budget_tokens removed, xhigh effort level added)
- **GPT-5 Turbo** (April 7): native image/audio in same model, $10/$30/M
- **Gemini 2.5 Pro** (April 1): 1M token context, multimodal — already have topic
- **Qwen 3.6-35B-A3B**: 3B active params, 73.4% SWE-bench Verified, best MoE efficiency
- **GLM-5.1**: 744B MIT license, 58.4% SWE-Bench Pro — agentic coding leader

### 2. Computer Use Is Now a Standard Dev Tool
Three major approaches emerged:
- Claude: portable screenshot + mouse/keyboard, VM-agnostic
- Codex Background Computer Use (April 16): macOS-first parallel desktop sessions
- Gemini: DOM-aware browser automation from Project Mariner

No comprehensive developer comparison exists yet — high opportunity, KD 6.

### 3. OpenAI Codex macOS App (Feb 2026) — Gap Still Exists
Multi-agent command center with parallel agents + Git worktrees. How-to gap: no comprehensive guide on running parallel coding agents with Git worktrees in Codex. KD 5, SV 350.

### 4. Windsurf Plan Mode (Wave 13) — Unique Feature, Low Competition
Complements Arena Mode: structured task planning before committing to implementation. Works with megaplan command for extra-thorough planning. Near-zero dedicated guides, KD 4.

### 5. JetBrains Dual April 2026 Research Reports
Two distinct reports published:
1. "Which AI Coding Tools Do Developers Actually Use at Work?" — usage survey with specific tool breakdown
2. "Understanding AI's Impact on Developer Workflows" — impact study on actual workflow changes

Both are first-party data sources competitors can't replicate.

### 6. Market Scale Signal
- AI coding market: $12.8B in 2026 (up from $5.1B in 2024)
- 51% of GitHub commits are AI-generated/assisted
- Claude Code: $2.5B annualized run-rate revenue, weekly active users doubled YoY
- 78% Fortune 500 companies using AI coding in production

## Competitor Gap Analysis

- **LogRocket**: monthly AI dev tool rankings — no breakdown by use-case angle
- **Pragmatic Engineer**: AI tooling 2026 issue — no how-to follow-ups
- **JetBrains blog**: first-party survey data — no competitor has this angle covered
- **Faros/Jellyfish**: productivity data — no actionable developer guide layer
- **DigitalApplied.com**: Windsurf Wave 13 guide exists but no Plan Mode dedicated piece

**Gaps to own**: Claude 4 API migration guide (breaking changes = high search urgency), computer-use comparison, Codex macOS multi-agent how-to

## Cluster Priority Recommendation (This Run)

1. **AI coding tools** → `claude-4-api-migration-guide-2026` (breaking changes create immediate developer urgency)
2. **AI coding tools** → `claude-opus-4-api-developer-guide-2026` (fresh model, KD 5)
3. **AI coding tools** → `computer-use-agents-comparison-2026` (no competitor has this comparison yet)
4. **AI for developers** → `ai-generated-github-code-statistics-2026` (SV 450, data-driven content)

## Phase Transition Check
Phase 1 trigger: `indexed_ratio > 0.9 AND days_since_launch > 30` — not yet reached. Stay Phase 0.
Blog is ~8 days old (started ~April 13). Need ~22 more days before Phase 1 is possible.
