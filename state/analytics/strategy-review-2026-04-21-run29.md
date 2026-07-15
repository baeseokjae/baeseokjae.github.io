# Strategy Review — 2026-04-21 (Run 29)

## Phase: 0 — External Data Only

## Queue Health

| Cluster | Queued | Published | Target |
|---|---|---|---|
| AI coding tools | 128 | 22 | 20+ ✓ |
| AI for developers | 60 | 9 | 20+ 🔶 |
| LLM comparison | 31 | 1 | 20+ 🔶 |
| AI workflow automation | 24 | 3 | 20+ 🔶 |

Queue is healthy at 345+ queued topics total. Content velocity is the constraint, not topic supply.

## New Topics Added This Run: 18

### AI coding tools (+12)
- `tabby-ai-review-2026` — self-hosted Copilot alternative, KD 5, SV 350
- `self-hosted-ai-coding-comparison-2026` — Tabby vs Continue+Ollama vs Void, KD 7, SV 450
- `void-editor-review-2026` — open-source Cursor fork, KD 4, SV 380
- `ai-junior-developer-tools-2026` — Sweep/Devin/SWE-agent comparison, KD 7, SV 370
- `github-spark-review-2026` — GitHub no-code AI builder, KD 4, SV 270
- `local-ai-coding-privacy-guide-2026` — privacy-first AI coding, KD 7, SV 360
- `ai-coding-prompting-patterns-2026` — 15 patterns for better output, KD 5, SV 420
- `continue-dev-alternatives-2026` — open-source VS Code AI plugins, KD 6, SV 320
- `cursor-vs-claude-code-which-to-choose-2026` — decision guide, KD 8, SV 650
- `openai-codex-for-everything-review-2026` — April 16 desktop update review, KD 5, SV 320
- `codeium-windsurf-history-2026` — brand evolution explainer, KD 4, SV 260
- `ai-coding-workflow-best-practices-2026` — 12 senior engineer patterns, KD 6, SV 430

### AI for developers (+6)
- `ai-coding-acceleration-whiplash-2026` — Faros 2026: bugs +54%, PR review 5x, KD 4, SV 280
- `ai-pr-review-bottleneck-2026` — fix the 5x PR review slowdown, KD 5, SV 300
- `ai-coding-tool-adoption-statistics-2026` — JetBrains 10K dev survey findings, KD 6, SV 420
- `ai-coding-cost-per-developer-2026` — TCO analysis across 8 tools, KD 5, SV 310
- `ai-coding-team-setup-guide-2026` — enterprise AI rollout guide, KD 7, SV 380
- `jetbrains-survey-ai-tools-2026` — April 2026 survey data, KD 5, SV 260

## Key Discoveries This Run

### 1. Acceleration Whiplash (High Priority)
Faros 2026 AI Engineering Report (22K devs, 4K teams): bugs +54%, PR review 5x slower, 31% PRs merging without review. This story is barely covered. Strong developer concern angle, very low KD.

### 2. Self-Hosted AI Coding Underserved
Tabby, Continue+Ollama, Void Editor get far less coverage than Cursor/Copilot despite growing privacy demand. scopir.com is the main competitor — we can outrank with depth.

### 3. OpenAI Codex Desktop April 2026 Update
Computer use + 90+ plugins launched April 16. Gap: no single "Codex for Everything" comprehensive review exists yet.

### 4. JetBrains Survey Fresh Data
April 2026: Claude Code at 18% work adoption (tied Cursor), Copilot at 29%, 76% awareness. Data-driven angle, low competition.

## Competitor Gap Analysis

- **LogRocket**: monthly power rankings, no how-to depth
- **JetBrains blog**: survey data, no tool reviews
- **Faros.ai**: engineering metrics, no developer tool guides
- **scopir.com**: self-hosted AI niche — monitor closely

**Gaps to own**: self-hosted AI coding, AI team rollout, code quality data stories, prompting patterns

## Cluster Priority Recommendation

1. **AI for developers** → push acceleration whiplash + team setup to front of queue
2. **LLM comparison** → cursor-vs-claude-code (SV 650) is highest-value next publish
3. **AI workflow automation** → 24 queued is sufficient supply

## Phase Transition Check
Phase 1 trigger: `indexed_ratio > 0.9 AND days_since_launch > 30` — not yet reached. Stay Phase 0.
