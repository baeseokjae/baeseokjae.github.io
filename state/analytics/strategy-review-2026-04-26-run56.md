# Strategy Review — 2026-04-26 (Run 56)

**Phase:** 0 (Days 0-30, external data only)
**Published posts:** 164
**Total queued:** 815 (AI coding tools: 350, AI for developers: 282, LLM comparison: 119, AI workflow automation: 64, unclustered legacy: 1)

## Topics Added This Run: 17

### LLM Comparison (+3)
| Slug | KD | SV | Signal |
|------|----|----|--------|
| openai-o4-mini-developer-guide-2026 | 5 | 400 | o4-mini: 92.7% AIME, 68.1% SWE-bench, 50% cheaper than o3, tool use via CoT |
| openai-o3-pro-developer-guide-2026 | 5 | 350 | o3-pro: when vs o4-mini, cost justification, reasoning deep dive |
| glm-5-1-vs-llama-4-open-source-coding-2026 | 6 | 350 | GLM-5.1 754B MIT vs Llama 4 Scout 10M context — open-source coding showdown |

### AI Coding Tools (+2)
| Slug | KD | SV | Signal |
|------|----|----|--------|
| bolt-new-v2-review-2026 | 7 | 450 | Bolt.new V2 Team Templates, design-to-code, published vs bolt-new-vs-replit-vs-v0 |
| glm-5-1-coding-agents-setup-guide-2026 | 4 | 300 | GLM-5.1 MIT + Cline/Roo Code/Claude Code integration guide, from Lushbinary coverage |

### AI for Developers (+7)
| Slug | KD | SV | Signal |
|------|----|----|--------|
| langgraph-platform-deployment-guide-2026 | 7 | 350 | LangGraph Platform: 400 companies, self-hosted/hybrid enterprise, GA |
| langgraph-2-0-guide-2026 | 8 | 400 | LangGraph 2.0 Feb 2026 — guardrail nodes, new production patterns |
| ai-coding-real-cost-2026 | 6 | 500 | 70% token waste, $200/mo tier convergence, Simon Willison signal |
| ai-coding-tools-enterprise-soc2-compliance-2026 | 8 | 350 | 79% lack SOC2 attestation — enterprise buying blocker |
| comp-ai-compliance-platform-guide-2026 | 3 | 250 | Comp AI: April 7 2026 open-source SOC2/HIPAA/GDPR, near-zero competition |
| gemini-enterprise-agent-platform-guide-2026 | 5 | 350 | Vertex AI renamed → Gemini Enterprise Agent Platform at Cloud Next 2026 |
| google-adk-vs-vertex-ai-agent-engine-2026 | 5 | 350 | ADK (build) vs Agent Engine (deploy) developer decision — missing guide |

### AI Workflow Automation (+5)
| Slug | KD | SV | Signal |
|------|----|----|--------|
| microsoft-copilot-studio-review-2026 | 8 | 400 | GPT-4.1 default upgrade, 1400+ integrations, distinct from comparison articles |
| zapier-copilot-ai-workflows-guide-2026 | 6 | 400 | Zapier Copilot for AI workflow building + MCP support planned |
| tines-vs-torq-soar-comparison-2026 | 7 | 350 | SOAR category maturing — Torq fastest-growing, Tines gold standard |
| torq-hypersoar-review-2026 | 5 | 250 | Torq Socrates omni-agent, 95% Tier-1 alert resolution, early review gap |
| n8n-make-zapier-ai-native-comparison-2026 | 9 | 500 | Which is most AI-native — distinct from existing n8n-vs-zapier-vs-make (published) |

## Key Market Signals (Phase 0 External Data)

**GPT-6 (April 14 2026):** Symphony architecture, 2M context window, $2.5/M input, 40%+ better on coding/reasoning/agent tasks vs GPT-5.4. Developer guides proliferating but benchmark comparison vs Claude Opus 4.7 gap open. Already have multiple GPT-6 topics queued.

**Claude Mythos Preview (April 7 2026):** 93.9% SWE-bench Verified, 82.0% Terminal-Bench 2.0, invitation-only via Project Glasswing. Zero-day vulnerability discovery angle. Topics queued; no published article yet — high priority.

**GLM-5.1 (April 7 2026):** 754B MoE MIT license, beats Claude Opus 4.6 and GPT-5.4 on SWE-Bench Pro. Available on HuggingFace. Works with Cline/Roo Code/Claude Code. Early mover opportunity.

**AI Coding Budget Reality:** $200/month tier convergence (Claude Code Max, Cursor Ultra, ChatGPT Pro). Simon Willison viral post on Claude Code pricing confusion. 70% token waste in agent runs documented. Developers loudly debating. High search intent.

**LangGraph 2.0 (Feb 2026):** Major rewrite codifying 3 years of production patterns. 400 companies on LangGraph Platform. Guardrail nodes simplify compliance. Strong tutorial gap.

**SOAR/AI Security Automation:** Torq HyperSOC Socrates agent claiming 95% Tier-1 resolution. Growing enterprise security automation market. Tines vs Torq vs Splunk SOAR comparison underserved.

## Cluster Audit (Phase 0)

**AI coding tools (350 queued, 27 published):** Healthy. Devin 3, Cursor 3, GLM-5.1 angles added. Orphan check: most published articles interlink but Claude Code guides could cross-link more.

**AI for developers (282 queued, 15 published):** SOC2, compliance, real-cost angles fill important enterprise gap. LangGraph 2.0 + Platform add production deployment depth.

**LLM comparison (119 queued, 4 published):** o4-mini and o3-pro fill OpenAI reasoning model gap. GLM-5.1 vs Llama 4 fills open-source comparison gap.

**AI workflow automation (64 queued, 5 published):** Thinnest cluster. SOAR and Copilot Studio entries add enterprise automation dimension. Zapier Copilot fills no-code AI workflow builder gap.

## Internal Link Opportunities (Phase 0)

- `best-ai-agent-frameworks-2026.md` → link from new LangGraph 2.0 and Platform articles
- `n8n-ai-workflow-tutorial-2026.md` → internal link target from new n8n AI-native comparison
- `cursor-3-guide-2026.md` → link from Bolt.new V2 review (vibe coding comparison angle)
- `vllm-vs-ollama-production-2026.md` → link from GLM-5.1 vs Llama 4 article

## Strategy Adjustments

No changes to kd_range or focus_topics warranted. Workflow automation cluster still thinnest — continue prioritizing. Enterprise security/compliance angle (SOC2, AI security) is an emerging sub-cluster worth tracking.
