# Strategy Review - 2026-07-09 Run 84

## Phase 1: First Signal Integration

### Queue Status
- **Before**: 1 active queued + 2904 queued_throttled + 2 writing
- **After**: 21 active queued + 2904 queued_throttled + 2 writing
- **New topics discovered**: 20
- **Queued**: 20
- **Rejected**: 0 appended; duplicate and weak-fit ideas were discarded before write
- **KD range**: 5-6, within Phase 1 range 0-25
- **Search volume**: 220-300, all above 200 minimum

### Discovery Sources
- GitHub repository search surfaced Codex Hygiene, QuickAI, RabbitHole, ChatGPT2Codex, Prompt Ops Maker, Pickysteve, ClaudeDeck, CodeSherpa, One Context MCP, RuleSentry, Wardyn, SlopStop, WATO Protocol, AgentLens, Argos MCP, PageLens, Cortex Gateway, Formwork, and VZT Browser.
- Dev.to APIs for `mcp`, `claudecode`, `codex`, `githubcopilot`, `cursor`, `aiagents`, `aicoding`, `llmops`, and `security` corroborated demand around Claude Code OIDC gateways, token/cost profiling, hidden MCP/config risks, tool-call reliability, package-install safety, and agent verification.
- GitHub Changelog, GitHub AI/ML, OpenAI RSS, Docker RSS, Cloudflare RSS, Snyk RSS, Vercel Atom, Firecrawl sitemap, Browserbase sitemap, Composio sitemap, AutomationAtlas sitemap, and Anthropic sitemap were checked for corroboration and duplicate filtering.
- Hacker News Algolia was checked for Codex hygiene, Claude Code profiling/admin UI, MCP gateway audit logs, skill routers, trace/replay evals, and agent observability. It provided weaker corroboration than GitHub/API sources, so it was not the primary basis for queued topics.

### Source Links
- GitHub Changelog feed: https://github.blog/changelog/feed/
- GitHub AI/ML feed: https://github.blog/ai-and-ml/feed/
- OpenAI RSS: https://openai.com/news/rss.xml
- Docker blog feed: https://www.docker.com/blog/feed/
- Cloudflare RSS: https://blog.cloudflare.com/rss/
- Snyk RSS: https://snyk.io/blog/feed/
- Vercel Atom feed: https://vercel.com/atom
- Firecrawl sitemap: https://www.firecrawl.dev/sitemap.xml
- Browserbase sitemap: https://www.browserbase.com/sitemap.xml
- Composio sitemap: https://composio.dev/sitemap.xml
- AutomationAtlas sitemap: https://automationatlas.io/sitemap.xml
- Anthropic sitemap: https://www.anthropic.com/sitemap.xml
- Dev.to MCP API: https://dev.to/api/articles?tag=mcp&top=7&per_page=30
- Dev.to Claude Code API: https://dev.to/api/articles?tag=claudecode&top=7&per_page=30
- Dev.to Codex API: https://dev.to/api/articles?tag=codex&top=7&per_page=30
- Dev.to GitHub Copilot API: https://dev.to/api/articles?tag=githubcopilot&top=7&per_page=30
- Dev.to Cursor API: https://dev.to/api/articles?tag=cursor&top=7&per_page=30
- Dev.to AI agents API: https://dev.to/api/articles?tag=aiagents&top=7&per_page=30
- GitHub API, Codex MCP search: https://api.github.com/search/repositories?q=%22Codex%22%20%22MCP%22%20created:%3E2026-07-01&sort=stars&order=desc&per_page=15
- GitHub API, Claude Code MCP search: https://api.github.com/search/repositories?q=%22Claude%20Code%22%20%22MCP%22%20created:%3E2026-07-01&sort=stars&order=desc&per_page=15
- GitHub API, coding-agent security search: https://api.github.com/search/repositories?q=%22coding%20agent%22%20%22security%22%20created:%3E2026-07-01&sort=stars&order=desc&per_page=15
- GitHub API, MCP gateway search: https://api.github.com/search/repositories?q=%22MCP%20gateway%22%20agent%20created:%3E2026-07-01&sort=stars&order=desc&per_page=15
- GitHub API, agent eval MCP search: https://api.github.com/search/repositories?q=%22AI%20agent%22%20%22eval%22%20%22MCP%22%20created:%3E2026-07-01&sort=stars&order=desc&per_page=15

### Queued Topics

| # | Priority | Slug | KD | Vol | Cluster |
|---|----------|------|----|-----|---------|
| 1 | 7887 | codex-hygiene-context-tool-surface-guide-2026 | 5 | 300 | AI coding tools |
| 2 | 7888 | quickai-claude-code-token-profiler-review-2026 | 5 | 260 | AI coding tools |
| 3 | 7889 | rabbithole-mcp-knowledge-canvas-agent-guide-2026 | 5 | 260 | AI for developers |
| 4 | 7890 | chatgpt2codex-local-mcp-actions-guide-2026 | 5 | 280 | AI coding tools |
| 5 | 7891 | prompt-ops-maker-verification-prompts-agent-guide-2026 | 5 | 230 | AI for developers |
| 6 | 7892 | pickysteve-skill-router-prompt-injection-guide-2026 | 5 | 220 | AI for developers |
| 7 | 7893 | claudedeck-claude-code-web-ui-review-2026 | 5 | 240 | AI coding tools |
| 8 | 7894 | codesherpa-git-native-structural-memory-guide-2026 | 5 | 230 | AI coding tools |
| 9 | 7895 | one-context-mcp-shared-project-memory-guide-2026 | 5 | 240 | AI workflow automation |
| 10 | 7896 | rulesentry-hidden-unicode-agent-config-guide-2026 | 5 | 230 | AI for developers |
| 11 | 7897 | wardyn-coding-agent-governance-control-plane-review-2026 | 5 | 260 | AI coding tools |
| 12 | 7898 | slopstop-hallucinated-package-blocker-guide-2026 | 6 | 300 | AI for developers |
| 13 | 7899 | wato-protocol-coding-agent-fleet-gates-guide-2026 | 5 | 220 | AI coding tools |
| 14 | 7900 | agentlens-local-agent-trace-replay-eval-guide-2026 | 5 | 280 | AI workflow automation |
| 15 | 7901 | argos-mcp-agent-observability-cost-latency-guide-2026 | 5 | 240 | AI workflow automation |
| 16 | 7902 | pagelens-mcp-ai-agent-legibility-audit-guide-2026 | 5 | 220 | AI for developers |
| 17 | 7903 | cortex-gateway-oauth-mcp-agent-tool-access-guide-2026 | 5 | 250 | AI workflow automation |
| 18 | 7904 | formwork-kernel-enforced-agent-sandbox-mcp-guide-2026 | 5 | 230 | AI for developers |
| 19 | 7905 | vzt-browser-credential-vault-agent-review-2026 | 5 | 240 | AI workflow automation |
| 20 | 7906 | claude-code-oidc-gateway-headless-agents-guide-2026 | 6 | 280 | AI coding tools |

### Discarded Before Append
- Duplicate or already-covered source angles: GitHub Copilot managed settings, Codex as JetBrains agent provider, Vercel Agent, Docker AI agent isolation, Cloudflare x402/AI traffic controls, Firecrawl Web Search MCP, Agent Zero Trust, ContextVC, Retok, ccmux, and broad OpenAI model/product posts.
- Weak-fit topics: consumer social-agent posts, broad AI standards explainers without developer implementation detail, generic AI security budget posts, and non-developer automation pages.
- Search-signal-only ideas without enough source specificity: broad Copilot telemetry observability, broad Cursor/Copilot pricing comparisons, and generic "best AI coding tools" competitor posts.

### Cluster Audit
- **AI coding tools**: Added Codex Hygiene, QuickAI, ChatGPT2Codex, ClaudeDeck, CodeSherpa, Wardyn, WATO Protocol, and Claude Code OIDC Gateway. This strengthens operational coverage around Codex/Claude context surfaces, token/cost profiling, local actions, team UI, memory, governance, and auth.
- **AI for developers**: Added RabbitHole MCP, Prompt Ops Maker, Pickysteve, RuleSentry, SlopStop, PageLens, and Formwork. These are implementation/security topics rather than generic agent explainers.
- **AI workflow automation**: Added One Context MCP, AgentLens, Argos MCP, Cortex Gateway, and VZT Browser. These expand shared memory, observability, OAuth gateway, and browser-credential workflow coverage.
- **LLM comparison**: No broad comparison topic was added because the strongest queue gap is still agent operations and security.

### Internal Link Opportunities
- Lightweight post-link scan found **582 orphan posts** out of 679 published posts with no detected inbound links.
- Recent high-priority orphan examples include `ai-agent-tooling-layer-selection-2026`, `api-vs-mcp-difference-guide-2026`, `claude-code-dev-team-stack-skills-mcp-2026`, `github-copilot-sdk-ga-guide-2026`, `mcp-gateway-registry-comparison-2026`, `anthropic-oidc-gateway-for-claude-code-2026`, `codegraph-vs-graphify-ai-coding-agents-2026`, `sonarqube-mcp-server-copilot-guide-2026`, and `coding-agent-debug-logs-guide-2026`.
- Priority internal-link clusters: Codex guides, Claude Code guides, MCP gateway/security posts, Copilot governance posts, agent observability posts, and AI coding-agent security posts.

### Phase 1 Analytics Check
- `state/analytics/` contains strategy-review markdown. Separate analytics reports are available under `research/`.
- Latest checked report: `research/analytics-2026-07-02.md`.
- GSC remains early: 15 impressions and 1 click over 2026-06-22 to 2026-06-29, led by `sonnet 5 benchmark` / `claude sonnet 5 benchmark` queries. No striking-distance keywords were detected.
- Phase 1 behavior followed: early GSC benchmark signal was noted, but queue recovery and external competitor/source gaps drove this run.

### Web Discovery Policy
- Used lightweight retrieval only: RSS/Atom feeds, XML sitemaps, JSON APIs, Hacker News Algolia, GitHub API, and direct endpoint retrieval through Python `urllib`.
- Browser navigation, screenshots, Playwright, WebFetch rendering, and browser repair/install commands were not used.
- Sourcegraph RSS returned localhost links and was not used for queued topics. Codersera root sitemap returned only a small sitemap index during this run; it was not retried with browser rendering.

### Strategy Adjustments
- **kd_range**: Maintained at `{min: 0, max: 25}` for Phase 1.
- **focus_topics**: Unchanged: AI coding tools, LLM comparison, AI workflow automation, AI for developers.
- **cluster_priority**: Prepended Run 84 priorities for Codex/Claude context hygiene, skill routing and verification prompts, local agent governance, config/package security, and observability/AI-legibility audits.
- **new_opportunities**: Added Run 84 opportunity notes for context-surface hygiene, skill routing, local governance, config/package-install security, and agent observability.
- **refresh_targets**: Added monitoring targets for Codex Hygiene/QuickAI/ChatGPT2Codex/OIDC gateway, Pickysteve/Prompt Ops Maker/RabbitHole, ClaudeDeck/Wardyn/WATO/One Context/CodeSherpa, RuleSentry/SlopStop/Formwork/VZT Browser, and AgentLens/Argos/PageLens/Cortex Gateway.

### Validation
- Checked every candidate slug against all existing `topics.json` slugs and all published post slugs before append.
- The 20 new queued topics introduced no duplicate slugs and no published-post slug overlaps.
- Required fields present for every candidate: title, slug, keyword, type, priority, status, search volume estimate, KD estimate, cluster, discovered_at.
- Every queued candidate fits `focus_topics`, has estimated volume 200+, and falls inside Phase 1 KD range 0-25.
- Repository-wide duplicate scan still reports 11 pre-existing duplicate topic slugs unrelated to this run.
