# Strategy Review - 2026-07-14 Run 102

## Phase 1: First Signal Integration

### Queue Status
- Before: 21 active queued (above LOW_WATERMARK of 10)
- After: 84 active queued (21 existing + 63 new)
- New topics discovered: 63 unique candidates from Dev.to + HN Algolia
- Queued: 63 (all passed validation)
- Rejected: 0
- KD range: 4-8, within Phase 1 range 0-25
- Search volume: 250-500, all above 200 minimum

### Queue Health
- **Before this run**: 21 queued topics — already above LOW_WATERMARK
- **After this run**: 84 queued topics — healthy buffer for 4+ weeks of publishing
- The queue is now well-stocked across all 4 focus clusters

### Discovery Sources
- **Dev.to API** (tag=ai, agents, mcp) surfaced 19 new candidates:
  - AI for developers cluster: 12 topics queued
  - AI coding tools cluster: 2 topics queued
  - AI workflow automation cluster: 5 topics queued
- **HN Algolia API** (3 queries: AI agent coding, MCP server, Claude Code/Cursor) surfaced 44 new candidates:
  - AI coding tools cluster: 25 topics queued (new tool reviews, security tools, sandboxing)
  - AI workflow automation cluster: 12 topics queued (MCP servers, security, optimization)
  - AI for developers cluster: 7 topics queued (agent lessons, environmental impact, career)

### Top Engagement Signals from Discovery
- **HN 1274pts** OpenCode open-source AI coding agent → queued as review
- **HN 570pts** MCP server that reduces Claude Code context by 98% → queued as review
- **HN 445pts** Semble code search for agents using 98% fewer tokens → queued as review
- **HN 380pts** AI coding agent needs to reduce maintenance costs → queued as guide
- **HN 367pts** Crush glamourous AI coding agent for terminal → queued as review
- **HN 272pts** Safari MCP Server for web developers → queued as review
- **HN 257pts** Plandex v2 open source AI coding agent → queued as review
- **HN 225pts** Cq Stack Overflow for AI coding agents → queued as review
- **HN 216pts** Smart model routing in Claude, Codex and Cursor → queued as how-to
- **HN 195pts** Vibe Kanban board to manage AI coding agents → queued as review
- **HN 185pts** GitMCP automatic MCP server for every GitHub repo → queued as review
- **HN 168pts** MCP-Scanner scan MCP servers for vulnerabilities → queued as review
- **HN 161pts** ProofShot give AI coding agents eyes to verify UI → queued as review
- **HN 158pts** Poison everywhere: no MCP server output is safe → queued as guide
- **HN 148pts** AI coding agents removing programming language barriers → queued as guide
- **HN 134pts** MCP-Shield detect security issues in MCP servers → queued as review
- **HN 133pts** Strata one MCP server for thousands of tools → queued as review
- **Dev.to 61❤️** The Myth of the Post-Documentation Era → queued as guide
- **Dev.to 52❤️** Being an Engineer in the AI Era → queued as guide
- **Dev.to 30❤️** How I Turned Slack Into an AI Teammate That Opens PRs → queued as how-to

### Queued Topics Summary (63 new)

| Cluster | Count | Key Topics |
|---------|-------|------------|
| AI coding tools | 27 | OpenCode, Crush, Plandex v2, Cq, Vibe Kanban, ProofShot, Yolobox, Optio, Kontext CLI, yolo-cage, TheAuditor, JACoB, Wispbit, Semble, Smart model routing, Claudable, Nia, Async, KeelTest, Sieve, Runtime, Ponytrail, Grov, Notes on rolling out Cursor/Claude Code, linter for AI security bugs, more rules make agents dumber |
| AI for developers | 19 | Post-documentation era, engineer in AI era, senior devs refusing AI, AI agent needs receipts, HITL not governance, agent keeps making mistakes, AI pentests AI, who checks done, benchmarks lying, dual-tier memory, 0-to-production deployment, decoupling prompt engineering, Lathe, Mission Control, Cost.dev, electricity use, Claude deletes database, learned building agent for year, uncomfortable truths |
| AI workflow automation | 17 | Slack AI teammate PRs, progressive MCP routing, vet MCP server, hardening MCP server, mcp2cli, ht-mcp, Armour, Browser MCP, MCP context reduction, Safari MCP, GitMCP, MCP-Scanner, Poison everywhere, MCP-Shield, Strata, Terraform MCP, Mapbox MCP |

### Key Trends Identified

1. **MCP Security is the #1 emerging category** — 8 new MCP security/optimization tools (MCP-Scanner, MCP-Shield, Poison everywhere, Armour, vet MCP server, hardening MCP server, progressive routing, context reduction). This is a major content opportunity cluster.

2. **Open-source coding agent explosion** — OpenCode (1274pts HN), Crush (367pts), Plandex v2 (257pts), JACoB (40pts) all launched. The open-source agent ecosystem is maturing rapidly.

3. **Agent sandboxing and security** — Yolobox, yolo-cage, Runtime, Kontext CLI all address the same pain point: how to run agents safely. This is a coherent cluster for comparison content.

4. **Agent verification and audit** — ProofShot, TheAuditor, Ponytrail, Sieve, "who checks done" all address agent output verification. Growing reliability concern.

5. **MCP tool ecosystem diversification** — Safari MCP, GitMCP, Terraform MCP, Mapbox MCP, Strata show MCP expanding beyond basic tool integration into specialized domains.

### Phase 1 Analytics Check
- No new GSC export was available this run. Phase 1 behavior remains external-data-first.
- The queue is now well-stocked at 84 topics — sufficient for 4+ weeks of publishing at current pace.
- Recommend next run focus on LLM comparison cluster (currently underrepresented at 3 queued topics).

### Web Discovery Policy
- Used lightweight retrieval only: Dev.to API (3 tag queries), HN Algolia API (3 queries).
- Browser navigation, screenshots, Playwright, WebFetch rendering, agent-browser, and browser install or repair commands were not used.

### Strategy Adjustments
- **kd_range**: Maintained at `{min: 0, max: 25}` for Phase 1.
- **focus_topics**: Unchanged: AI coding tools, LLM comparison, AI workflow automation, AI for developers.
- **cluster_priority**: Prepended Run 102 priorities for all 63 validated topics.
- **new_opportunities**: Added 55 Run 102 opportunity notes from Dev.to and HN.
- **refresh_targets**: Added 12 new monitoring targets for OpenCode, Crush, Plandex v2, Cq, ProofShot, Semble, Browser MCP, MCP-Scanner/Shield, GitMCP, Strata, and Runtime.
