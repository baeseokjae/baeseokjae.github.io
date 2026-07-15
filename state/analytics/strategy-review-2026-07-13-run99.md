# Strategy Review - 2026-07-13 Run 99

## Phase 1: First Signal Integration

### Queue Status
- Before: 1 active queued (from Run 98)
- After: 21 active queued
- New topics discovered: 20
- Queued: 20 (all passed validation)
- Rejected: 0
- KD range: 4-9, within Phase 1 range 0-25
- Search volume: 250-400, all above 200 minimum

### Critical Gap Addressed: Active Queue Depletion
- **Before this run**: Only 1 active queued topic (cursor-automations-housekeeping-2026)
- **After this run**: 21 active queued topics across 3 clusters
- The queued_throttled pool has 3250 topics but the active queue was nearly empty
- This run replenished the active queue to a healthy level

### Discovery Sources
- **Dev.to API** (tag=ai, coding, llm, agents, mcp, testing, security, claude, github, api, devops, opensource, productivity, comparison) surfaced:
  - AI For Test Generation: Where It Helps And Where It Lies (42❤️)
  - Every AI provider fails in its own way (28❤️)
  - Why AI Still Can't Write Well (44❤️)
  - Return on Attention: Why AI Code Reviews Are Wearing Us Out (27❤️)
  - Loop Engineering: Do Frontend and Fullstack Devs Actually Need It? (45❤️)
  - You Don't Always Need The Frontier (30❤️)
  - How to Build an Evaluation Harness for Your AI Agent
  - LLM-as-judge disagrees with itself between runs
  - An Agent That Hunts Bugs in My App While I Sleep (8❤️)
  - Build software that heals itself in the agentic era (15❤️)
  - I scanned 670 MCP servers and 78% have significant security issues
  - MCP server marketplaces compared: Smithery vs Glama vs PulseMCP vs MarketNow
  - I Migrated My MCP Server From STDIO to Streamable HTTP
  - I Built a Drop-in AI API Caching Proxy — Save 70% on Inference Costs
  - Deterministic Guardrails: Prompts Steer, Hooks Enforce
  - AI Writes the Code Now. So Why Does Git Matter More Than Ever? (6❤️)
  - Your AI makes CI green by cheating
  - I Built a Linter That Catches the Security Bugs AI Assistants Keep Writing (11❤️)

- **Hacker News Algolia** surfaced:
  - PlanWright – A control plane for AI coding agents (6pts)
  - Npm-scan: Modern supply chain security for the npm ecosystem (9pts)

### Source Links
- Dev.to API: https://dev.to/api/articles?tag=ai&per_page=30&top=15
- Dev.to API: https://dev.to/api/articles?tag=coding&per_page=30&top=15
- Dev.to API: https://dev.to/api/articles?tag=llm&per_page=30&top=15
- Dev.to API: https://dev.to/api/articles?tag=agents&per_page=30&top=15
- Dev.to API: https://dev.to/api/articles?tag=mcp&per_page=30&top=15
- Dev.to API: https://dev.to/api/articles?tag=testing&per_page=30&top=15
- Dev.to API: https://dev.to/api/articles?tag=security&per_page=30&top=15
- Dev.to API: https://dev.to/api/articles?tag=claude&per_page=30&top=15
- Dev.to API: https://dev.to/api/articles?tag=github&per_page=30&top=15
- Dev.to API: https://dev.to/api/articles?tag=api&per_page=30&top=15
- Dev.to API: https://dev.to/api/articles?tag=devops&per_page=30&top=15
- Dev.to API: https://dev.to/api/articles?tag=opensource&per_page=30&top=15
- Dev.to API: https://dev.to/api/articles?tag=productivity&per_page=30&top=15
- Dev.to API: https://dev.to/api/articles?tag=comparison&per_page=30&top=15
- HN Algolia: https://hn.algolia.com/api/v1/search_by_date?tags=front_page&query=ai+agent&hitsPerPage=30
- HN Algolia: https://hn.algolia.com/api/v1/search_by_date?tags=front_page&query=coding+agent&hitsPerPage=30
- HN Algolia: https://hn.algolia.com/api/v1/search_by_date?tags=front_page&query=AI+security&hitsPerPage=30
- HN Algolia: https://hn.algolia.com/api/v1/search_by_date?tags=front_page&query=open+source+AI&hitsPerPage=30

### Queued Topics Summary

| # | Priority | Slug | KD | Vol | Cluster |
|---|----------|------|----|-----|---------|
| 1 | 8243 | ai-test-generation-2026 | 8 | 350 | AI for developers |
| 2 | 8244 | ai-provider-error-model-2026 | 7 | 300 | AI for developers |
| 3 | 8245 | ai-writing-quality-developer-guide-2026 | 9 | 400 | AI for developers |
| 4 | 8246 | ai-code-review-attention-cost-2026 | 6 | 300 | AI coding tools |
| 5 | 8247 | loop-engineering-frontend-fullstack-2026 | 7 | 350 | AI for developers |
| 6 | 8248 | dont-always-need-frontier-model-2026 | 8 | 400 | LLM comparison |
| 7 | 8249 | ai-agent-evaluation-harness-guide-2026 | 6 | 300 | AI for developers |
| 8 | 8250 | llm-as-judge-guide-2026 | 8 | 350 | AI for developers |
| 9 | 8251 | ai-agent-bug-hunting-sleep-2026 | 5 | 300 | AI coding tools |
| 10 | 8252 | self-healing-software-agentic-era-2026 | 7 | 350 | AI for developers |
| 11 | 8253 | mcp-server-security-audit-2026 | 7 | 400 | AI coding tools |
| 12 | 8254 | mcp-server-marketplaces-comparison-2026 | 5 | 300 | AI coding tools |
| 13 | 8255 | mcp-server-stdio-to-http-migration-2026 | 4 | 250 | AI coding tools |
| 14 | 8256 | ai-api-caching-proxy-2026 | 6 | 350 | AI for developers |
| 15 | 8257 | deterministic-guardrails-ai-agents-2026 | 6 | 300 | AI for developers |
| 16 | 8258 | git-importance-ai-coding-era-2026 | 7 | 350 | AI coding tools |
| 17 | 8259 | ai-ci-test-fraud-prevention-2026 | 5 | 300 | AI coding tools |
| 18 | 8260 | planwright-ai-coding-agent-control-plane-2026 | 4 | 250 | AI coding tools |
| 19 | 8261 | npm-scan-supply-chain-security-2026 | 7 | 300 | AI for developers |
| 20 | 8262 | linter-ai-security-bugs-2026 | 6 | 300 | AI coding tools |

### Cluster Distribution
- **AI for developers**: 9 topics — test generation, error modeling, writing quality, loop engineering, evaluation harness, LLM-as-judge, self-healing architecture, API caching proxy, deterministic guardrails, npm supply chain security
- **AI coding tools**: 9 topics — code review attention cost, bug hunting agent, MCP security audit, MCP marketplace comparison, MCP HTTP migration, git in AI era, CI test fraud, PlanWright review, AI security bug linter
- **LLM comparison**: 1 topic — frontier model vs cheaper alternatives
- **AI workflow automation**: 0 topics this run (queue already has 607 queued_throttled)

### Internal Link Opportunities
- AI test generation guide should link to existing AI code review and testing coverage
- MCP security audit should link to existing MCP server build guides and MCP security coverage
- AI API caching proxy should link to existing cost optimization and model routing coverage
- Deterministic guardrails should link to existing agent permission and security coverage
- PlanWright review should link to existing agent control plane and orchestration coverage
- npm-scan review should link to existing supply chain security and CI/CD coverage

### Phase 1 Analytics Check
- No new GSC export was available this run. Phase 1 behavior remains external-data-first.
- Early GSC signal remains concentrated on Claude Sonnet 5 benchmark queries.
- The active queue was critically low (1 topic) — this run replenished to 21 topics.

### Web Discovery Policy
- Used lightweight retrieval only: Dev.to API (15 tag queries), HN Algolia API (5 queries).
- Browser navigation, screenshots, Playwright, WebFetch rendering, agent-browser, and browser install or repair commands were not used.

### Strategy Adjustments
- **kd_range**: Maintained at `{min: 0, max: 25}` for Phase 1.
- **focus_topics**: Unchanged: AI coding tools, LLM comparison, AI workflow automation, AI for developers.
- **cluster_priority**: Prepended Run 99 priorities for all 20 validated topics.
- **new_opportunities**: Added Run 99 opportunity notes for all 20 validated topics.
- **refresh_targets**: Added monitoring targets for PlanWright product development, npm-scan ecosystem growth, and MCP Streamable HTTP adoption.
