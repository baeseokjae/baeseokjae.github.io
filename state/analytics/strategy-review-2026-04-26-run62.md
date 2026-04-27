# Strategy Review — 2026-04-26 (Run 62)

## Phase 0 — External Data Only

### Topics Discovered: 17 (all promoted to "queued")

#### AI Coding Tools (+11)
| Slug | KD | SV |
|---|---|---|
| gemini-cli-subagents-guide-2026 | 5 | 400 |
| google-agents-cli-guide-2026 | 4 | 250 |
| ibm-contextforge-mcp-gateway-review-2026 | 5 | 250 |
| spring-ai-mcp-server-tutorial-2026 | 6 | 300 |
| mcp-rce-vulnerability-by-design-fix-2026 | 7 | 500 |
| mcp-connector-poisoning-npm-security-2026 | 6 | 300 |
| open-source-mcp-gateways-comparison-2026 | 7 | 350 |
| gemini-cli-custom-subagents-tutorial-2026 | 4 | 250 |
| lovable-penetration-testing-security-2026 | 5 | 300 |
| gpt-5-5-terminal-bench-agentic-guide-2026 | 6 | 350 |
| mcpx-lunar-dev-enterprise-mcp-review-2026 | 5 | 250 |

#### AI For Developers (+4)
| Slug | KD | SV |
|---|---|---|
| vercel-ai-supply-chain-attack-lessons-2026 | 5 | 250 |
| google-agents-cli-vs-adk-comparison-2026 | 5 | 250 |
| ai-agent-sandboxes-comparison-2026 | 7 | 400 |
| mcp-security-enterprise-ciso-guide-2026 | 8 | 400 |

#### LLM Comparison (+2)
| Slug | KD | SV |
|---|---|---|
| claude-mythos-pricing-access-guide-2026 | 5 | 300 |
| gpt-5-5-omnimodal-api-guide-2026 | 6 | 400 |

---

### Key Signals This Run

**GPT-5.5 "Spud" (April 23, 2026)**
- 88.7% SWE-bench, 82.7% Terminal-Bench 2.0
- Natively omnimodal: text, image, audio, video in single model
- $5/$30M tokens, 40% fewer output tokens than GPT-5.4
- Claude Opus 4.7 still leads on SWE-bench Pro (64.3% vs 58.6%) and MCP-Atlas (79.1% vs 75.3%)

**Gemini CLI Subagents (April 15, 2026)**
- Delegate complex tasks to specialist agents via @name syntax
- Custom subagents defined with YAML frontmatter .md files
- Built-in: @cli_help, @codebase_investigator, @generalist
- Each subagent gets own context window + curated toolset

**Google Agents CLI (April 2026)**
- End-to-end agent development lifecycle CLI
- `uvx google-agents-cli` injects skills into coding assistants
- Covers build → eval → deploy on Google Cloud (Agent Runtime / Cloud Run / GKE)
- Complements ADK — ADK defines agents, Agents CLI deploys them

**MCP "By Design" RCE Vulnerability**
- Critical design flaw in official MCP SDK (Python/TypeScript/Java/Rust)
- Affects 200K+ servers, 150M+ downloads
- Cursor, VS Code, Windsurf, Claude Code, Gemini CLI all affected
- Windsurf CVE-2026-30615: zero-interaction exploit
- Anthropic declined architecture change — "expected behavior"
- HIGH PRIORITY: security cluster forming, developer urgency acute

**MCP Supply Chain Incidents**
- Vercel breach April 19: compromised Context AI employee → database breach
- @azure-devops/mcp npm package missing auth layer (April 3)
- MCP connector poisoning via compromised npm packages

**IBM ContextForge MCP Gateway**
- Open source, Apache 2.0, multi-protocol: MCP + A2A + REST + gRPC
- Multi-cluster Kubernetes via Redis-backed federation
- 40+ plugins, OpenTelemetry tracing
- Enterprise competitor to MCPX (Lunar.dev) and Docker MCP Gateway

**AI Agent Sandboxes**
- E2B and Daytona emerging as key secure execution infrastructure
- Cloudflare Project Think adding durable agent execution
- Growing as prerequisite for enterprise agentic deployments

---

### Cluster Status After Run 62
- AI coding tools: 384 queued / 16 seeded / 7 writing / 27 published
- AI for developers: 305 queued / 1 seeded / 5 writing / 15 published
- LLM comparison: 134 queued / 2 seeded / 0 writing / 4 published
- AI workflow automation: 68 queued / 0 seeded / 0 writing / 5 published

### Competitor Gap Analysis (Phase 0)
- MCP security content is UNDERSERVED — competitors have awareness posts but no developer how-to for patching/protecting
- Gemini CLI subagents: Google's own blog has the announcement, no third-party how-to guides yet — early mover window
- IBM ContextForge: zero independent reviews despite strong GitHub presence
- AI agent sandboxes: no comparison piece exists despite 3 major players (E2B, Daytona, Cloudflare)
- Spring AI + MCP: Java developer audience largely ignored by AI content creators

### Topical Cluster Integrity
- MCP security articles now spanning: supply chain, CISO guide, RCE fix, connector poisoning, enterprise gateways — forming a coherent security cluster
- Gemini CLI cluster expanding: guide, free tier, plan mode, subagents, custom subagents — strong pillar coverage
- Google agent tooling cluster forming: ADK tutorial, Agents CLI guide, ADK vs Agents CLI comparison — new cluster emerging
