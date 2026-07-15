# Strategy Review — 2026-04-25 (Run 51)

## Phase: 0 (External Data Only)

## Topics Discovered: 18 new, all promoted to "queued"

### AI Coding Tools (+12)
| Slug | KD | SV | Angle |
|---|---|---|---|
| mcp-design-flaw-rce-mitigation-guide-2026 | 5 | 400 | OX Security April 16 architectural RCE, Anthropic declined fix, developer mitigation |
| owasp-mcp-top-10-developer-guide-2026 | 5 | 300 | MCP-specific OWASP Top 10 (distinct from Agentic Top 10) |
| windsurf-cve-2026-30615-fix-guide-2026 | 3 | 250 | Zero-click RCE in Windsurf IDE, patch guide |
| vibe-coding-production-failures-2026 | 6 | 350 | 7 real incidents, 1.5M API keys, case study format |
| opencode-review-lsp-guide-2026 | 4 | 300 | OpenCode 112K stars, LSP integration, 75+ providers, free |
| flowise-mcp-rce-cve-fix-guide-2026 | 3 | 200 | Critical Flowise MCP adapter RCE, self-hosted fix guide |
| mcp-stdio-command-injection-prevention-2026 | 4 | 250 | STDIO transport-level injection (distinct from prompt-level) |
| vibe-coding-enterprise-security-checklist-2026 | 5 | 300 | CISO/platform engineer checklist, SAST gates, SBOM |
| ox-security-mcp-supply-chain-action-plan-2026 | 4 | 250 | Post-disclosure 5-step ops action plan |
| codex-cli-cerebras-wse3-speed-guide-2026 | 3 | 200 | Codex-Spark on WSE-3 at 1000+ tok/s, terminal workflow guide |

### AI for Developers (+6)
| Slug | KD | SV | Angle |
|---|---|---|---|
| ai-agent-observability-tools-comparison-2026 | 7 | 400 | Braintrust vs Arize vs Datadog vs LangSmith buyer's guide |
| mcp-oauth-enterprise-security-guide-2026 | 4 | 250 | OAuth 2.1 + Entra ID + VNet for enterprise MCP deployments |
| jetbrains-ai-workflow-impact-study-2026 | 5 | 300 | JetBrains April 2026 workflow impact study (separate from adoption survey) |
| microsoft-agent-framework-1-0-migration-guide-2026 | 6 | 300 | AutoGen → MAF migration guide, GA April 3 2026 |
| latitude-ai-review-2026 | 4 | 200 | Latitude.so open-source LLM eval, MIT license, standalone review |
| ai-agent-observability-best-practices-2026 | 6 | 350 | Implementation patterns (OTEL, eval-gated CI/CD, cost attribution) |

### AI Workflow Automation (+2)
| Slug | KD | SV | Angle |
|---|---|---|---|
| hipocampus-review-2026 | 2 | 200 | Governed AI operators for Slack/GitHub, human-in-loop workflows |
| gumloop-series-b-enterprise-review-2026 | 5 | 300 | $50M Series B, Shopify/Ramp traction, credit pricing advantage |

## Key Signals This Run

**MCP Security Crisis Deepening**
- OX Security confirmed Anthropic's STDIO design is intentionally by-design — no protocol fix coming
- 200K servers exposed, 150M+ downloads affected across Python/TypeScript/Java/Rust SDKs
- 30+ CVEs filed in 60 days; Windsurf CVE-2026-30615 is zero-click
- Developer responsibility for sanitization is now permanent — guide content has long shelf life
- Flowise (30K+ GitHub stars) has its own MCP RCE — high self-hosted urgency

**Open-Source Terminal Agent Rise**
- OpenCode hit 112K GitHub stars — fastest-rising open-source terminal coding agent
- Distinguishes itself: LSP integration, 75+ providers, multi-session, free
- Competitive pressure on Claude Code ($20/mo) and Codex CLI (subscription)

**GPT-5.5 Shipped April 23 — Most Angles Already Covered**
- 88.7% SWE-bench, $5/$30/M, 1M context, gpt-5.5 and gpt-5.5-pro model IDs
- topics.json already has 8+ GPT-5.5 slugs from prior runs — no new topics needed

**AI Observability Market Heating Up**
- $2.69B market, 36.2% CAGR — developers still shipping agents before they can debug them
- Braintrust ($249/mo Pro) vs free/open alternatives (Arize Phoenix, Latitude.so) creating buyer confusion
- Comparison + best practices guides have high practical intent, moderate competition

**Gumloop Enterprise Validation**
- $50M Series B (March 2026), Shopify/Ramp/Gusto/Instacart as customers
- Credit pricing (non-AI steps free) is genuinely distinctive vs Zapier/Make
- Enterprise angle not yet covered in gumloop-review-2026 or gumloop-tutorial

## Cluster Counts (post-run)
- AI coding tools: 330 queued
- AI for developers: 250 queued
- LLM comparison: 104 queued
- AI workflow automation: 64 queued
- Total queued: 748

## Phase 0 Strategy Notes
No GSC data available. Competitor analysis shows MCP security is now the dominant developer concern in the AI coding cluster — 4 of 12 new coding topics are MCP security variants. This is appropriate: the OX disclosure created a durable gap (Anthropic won't fix at protocol level), so guides won't go stale quickly.
