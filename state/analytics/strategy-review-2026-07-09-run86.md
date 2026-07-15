# Strategy Review - 2026-07-09 Run 86

## Phase 1: First Signal Integration

### Queue Status
- **Before**: 1 active queued + 2944 queued_throttled + 1 writing
- **After**: 21 active queued + 2944 queued_throttled + 1 writing
- **New topics discovered**: 20
- **Queued**: 20
- **Rejected**: 0 appended; duplicates and broad-fit topics were discarded before write
- **KD range**: 5, within Phase 1 range 0-25
- **Search volume**: 210-240, all above 200 minimum

### Discovery Sources
- GitHub Changelog and GitHub AI/ML feeds showed continued enterprise Copilot governance, OpenTelemetry, MDM, mobile agent, and npm install-time security activity, but the direct Copilot items were already covered locally.
- GitHub API repository searches surfaced fresh operational tools around MCP/skill scanning, Codex CLI telemetry, shared agent registries, worktree isolation, browser-agent handoff, and session conversion. GitHub API later returned rate limits for some follow-up queries, so those were recorded and not retried.
- Dev.to APIs for `mcp`, `claudecode`, `codex`, `opencode`, `githubcopilot`, `llmops`, `aiagents`, and `agenticai` corroborated demand around MCP security, token cost, Copilot telemetry, Codex workflow issues, and agent production failure modes.
- Competitor sitemaps/RSS checked: Codersera sitemap, AutomationAtlas sitemap, Composio sitemap, Firecrawl sitemap, Browserbase sitemap, Arcade RSS, Docker RSS, Cloudflare RSS, OpenAI RSS, GitHub feeds, plus Hacker News Algolia.

### Source Links
- GitHub Changelog feed: https://github.blog/changelog/feed/
- GitHub AI/ML feed: https://github.blog/ai-and-ml/feed/
- OpenAI RSS: https://openai.com/news/rss.xml
- Docker blog feed: https://www.docker.com/blog/feed/
- Cloudflare RSS: https://blog.cloudflare.com/rss/
- Arcade RSS: https://blog.arcade.dev/rss.xml
- Codersera sitemap posts: https://codersera.com/blog/sitemap-posts.xml
- AutomationAtlas sitemap: https://automationatlas.io/sitemap.xml
- Composio sitemap: https://www.composio.dev/sitemap.xml
- Firecrawl sitemap: https://www.firecrawl.dev/sitemap.xml
- Browserbase sitemap: https://www.browserbase.com/sitemap.xml
- Dev.to MCP API: https://dev.to/api/articles?tag=mcp&top=7&per_page=30
- Dev.to Claude Code API: https://dev.to/api/articles?tag=claudecode&top=7&per_page=30
- Dev.to Codex API: https://dev.to/api/articles?tag=codex&top=7&per_page=30
- Dev.to OpenCode API: https://dev.to/api/articles?tag=opencode&top=7&per_page=30
- Dev.to GitHub Copilot API: https://dev.to/api/articles?tag=githubcopilot&top=7&per_page=30
- Dev.to LLMOps API: https://dev.to/api/articles?tag=llmops&top=7&per_page=30
- Dev.to AI agents API: https://dev.to/api/articles?tag=aiagents&top=7&per_page=30
- Hacker News Algolia API: https://hn.algolia.com/api/v1/search_by_date
- GitHub API Codex CLI search: https://api.github.com/search/repositories?q=%22Codex%20CLI%22%20created:%3E2026-07-05&sort=stars&order=desc&per_page=30
- GitHub API OpenCode MCP search: https://api.github.com/search/repositories?q=%22OpenCode%22%20%22MCP%22%20created:%3E2026-07-01&sort=stars&order=desc&per_page=30
- GitHub API MCP scanner search: https://api.github.com/search/repositories?q=%22MCP%20server%22%20%22scanner%22%20created:%3E2026-07-01&sort=stars&order=desc&per_page=30
- GitHub API MCP benchmark search: https://api.github.com/search/repositories?q=%22MCP%22%20%22benchmark%22%20created:%3E2026-07-01&sort=stars&order=desc&per_page=30
- GitHub API browser agent search: https://api.github.com/search/repositories?q=%22browser%20agent%22%20created:%3E2026-07-01&sort=stars&order=desc&per_page=20
- GitHub API agent sandbox search: https://api.github.com/search/repositories?q=%22agent%22%20%22sandbox%22%20created:%3E2026-07-05&sort=stars&order=desc&per_page=20

### Queued Topics

| # | Priority | Slug | KD | Vol | Cluster |
|---|----------|------|----|-----|---------|
| 1 | 7928 | assay-ai-dev-stack-security-scanner-guide-2026 | 5 | 220 | AI for developers |
| 2 | 7929 | mcp-bastion-reliability-security-proxy-guide-2026 | 5 | 230 | AI for developers |
| 3 | 7930 | mcp-hardening-benchmark-cis-audit-guide-2026 | 5 | 220 | AI for developers |
| 4 | 7931 | mcp-trust-preflight-scanner-guide-2026 | 5 | 220 | AI for developers |
| 5 | 7932 | skillsentry-agent-skill-mcp-scanner-guide-2026 | 5 | 210 | AI for developers |
| 6 | 7933 | recall-bench-coding-agent-history-search-guide-2026 | 5 | 210 | AI workflow automation |
| 7 | 7934 | toolport-mcp-token-cost-benchmark-guide-2026 | 5 | 230 | AI for developers |
| 8 | 7935 | codex-cli-token-efficiency-benchmark-guide-2026 | 5 | 240 | AI coding tools |
| 9 | 7936 | codex-cli-mobile-pairing-guide-2026 | 5 | 230 | AI coding tools |
| 10 | 7937 | agent-watch-codex-claude-code-monitor-guide-2026 | 5 | 220 | AI coding tools |
| 11 | 7938 | codex-guard-runtime-control-guide-2026 | 5 | 220 | AI coding tools |
| 12 | 7939 | costmarshal-codex-cost-orchestration-guide-2026 | 5 | 220 | AI coding tools |
| 13 | 7940 | opencode-registry-skills-mcp-guide-2026 | 5 | 230 | AI coding tools |
| 14 | 7941 | opencode-webmcp-chromium-tools-guide-2026 | 5 | 220 | AI for developers |
| 15 | 7942 | lectern-shared-brain-coding-agents-guide-2026 | 5 | 230 | AI workflow automation |
| 16 | 7943 | nodify-sync-mcp-skills-secrets-guide-2026 | 5 | 220 | AI coding tools |
| 17 | 7944 | baton-ai-coding-session-converter-guide-2026 | 5 | 220 | AI workflow automation |
| 18 | 7945 | treebox-isolated-worktrees-coding-agents-guide-2026 | 5 | 230 | AI for developers |
| 19 | 7946 | runwitness-agent-receipts-guide-2026 | 5 | 220 | AI for developers |
| 20 | 7947 | volleybot-browser-agent-human-handoff-guide-2026 | 5 | 240 | AI workflow automation |

### Discarded Before Append
- Existing local coverage: GitHub Copilot OpenTelemetry export, managed settings via MDM, npm install-time security, Copilot mobile agent operations, broad OpenCode reviews, broad MCP gateway comparisons, Arcade auth comparisons, agent observability, and Agent Zero Trust repo intake scanning.
- Weak-fit or broad topics: generic social API friction, broad standards explainers, generic AI assistant rankings, non-developer automation posts, consumer/workplace AI news, and model-launch commentary without developer implementation intent.
- Unavailable or malformed sources were not retried through browser rendering: Anthropic RSS returned 404, Browserbase blog RSS returned 500, Vercel Atom returned malformed XML, Snyk RSS returned malformed XML, LangChain RSS returned malformed XML, and ByteIota sitemap returned 406.

### Cluster Audit
- **AI for developers**: Added Assay, MCP Bastion, MCP Hardening Benchmark, MCP Trust, SkillSentry, Toolport, OpenCode WebMCP, Treebox, and RunWitness. This strengthens the scanner, hardening, tool-cost, sandbox, and evidence cluster.
- **AI coding tools**: Added Codex CLI token benchmark, Codex mobile pairing, Agent Watch, Codex Guard, CostMarshal, OpenCode Registry, and Nodify. This expands local Codex/OpenCode operations coverage beyond generic tool reviews.
- **AI workflow automation**: Added Recall-Bench, Lectern, Baton, and VolleyBot for memory search, shared agent brains, session conversion, and browser-agent handoff.
- **LLM comparison**: No new comparison topics were added this run; the strongest opportunities were operational rather than model-choice articles.

### Internal Link Opportunities
- Priority future internal links should connect new MCP scanner topics to `agent-skills-supply-chain-security-guide-2026`, `mcp-stdio-security-warning-2026`, `mcp-gateway-security-limitations-guide-2026`, and `agent-zero-trust-repo-intake-scanner-guide-2026`.
- Codex operational topics should link back to Codex CLI guides, Codex usage/cost controls, and Claude Code vs Codex migration articles.
- Browser-agent handoff and sandbox topics should link to browser automation, AI agent sandbox infrastructure, and agent observability posts.

### Phase 1 Analytics Check
- Latest available analytics report: `research/analytics-2026-07-02.md`.
- GSC remains early: 15 impressions and 1 click over 2026-06-22 to 2026-06-29, led by `sonnet 5 benchmark` / `claude sonnet 5 benchmark` queries.
- No striking-distance keywords were detected. Phase 1 behavior followed: external source gaps and queue depth drove discovery, with benchmark demand noted but not over-weighted.

### Web Discovery Policy
- Used lightweight retrieval only: RSS/Atom feeds, XML sitemaps, JSON APIs, Hacker News Algolia, GitHub API, and direct endpoint retrieval through Python `urllib` with a browser-style user agent.
- Browser navigation, screenshots, Playwright, WebFetch rendering, agent-browser, and browser install/repair commands were not used.
- GitHub API rate limits were treated as a stopping condition for those specific follow-up queries rather than repeatedly retrying.

### Strategy Adjustments
- **kd_range**: Maintained at `{min: 0, max: 25}` for Phase 1.
- **focus_topics**: Unchanged: AI coding tools, LLM comparison, AI workflow automation, AI for developers.
- **cluster_priority**: Prepended Run 86 priorities for MCP/skill scanner tools, Codex CLI operational controls, cross-agent registry/portability, and agent runtime evidence/handoff.
- **new_opportunities**: Added Run 86 opportunity notes for preflight scanners, Codex operations telemetry, cross-agent portability, and runtime isolation/evidence.
- **refresh_targets**: Added monitoring targets for MCP scanners, Codex telemetry/control tools, cross-agent portability/control planes, and runtime evidence/handoff tools.

### Validation
- Checked every candidate slug against all existing `topics.json` slugs and all published post slugs before append.
- The 20 new queued topics introduced no duplicate slugs and no published-post slug overlaps.
- Required fields present for every new topic: title, slug, keyword, type, priority, status, search volume estimate, KD estimate, cluster, discovered_at.
- Every queued topic fits `focus_topics`, has estimated volume 200+, and falls inside Phase 1 KD range 0-25.
- Repository-wide duplicate scan still reports 11 pre-existing duplicate topic slugs unrelated to this run.
