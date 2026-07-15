# Strategy Review — 2026-07-14 Run 105

## Phase 1: First Signal Integration

### Queue Status
- **Queued topics**: 23 (up from 1 — critically low was replenished)
- **Published**: 715 (reconstructed from filesystem — 367 new posts since last backup)
- **Queued (throttled)**: 3,024
- **Rejected**: 18
- **Seeded/Writing**: 10

### Queue Health
- 23 queued topics = ~1 week of publishing at current pace
- **Queue was critically low** (only 1 queued topic) — this run discovered 22 new topics
- Cluster distribution of new topics: AI coding tools (9), AI for developers (6), AI workflow automation (4), LLM comparison (4)
- **LLM comparison cluster still underrepresented** in queued (now 7 total) vs published — needs continued prioritization

### Topic Discovery Summary (Run 105)
- **22 new topics discovered and queued** from HN Algolia API + Dev.to API
- **0 duplicates** — all checked against existing 3,849 topic slugs and 704 published posts
- **0 rejected** — all passed KD range (0-25), focus topic, and field validation
- **Web Discovery Policy**: Used lightweight retrieval only: HN Algolia API (6 queries), Dev.to API (3 queries). No browser navigation, screenshots, Playwright, or agent-browser used.

### New Topics by Cluster

**AI Coding Tools (9):**
1. OpenCode vs Claude Code vs Crush: Open-Source Terminal AI Coding Agents Compared 2026
2. Plandex v2 Review 2026: Open-Source AI Coding Agent for Large Projects
3. Cq: Stack Overflow for AI Coding Agents — Platform Review 2026
4. Yolobox: Run AI Coding Agents with Full Sudo Without Nuking Your Home Directory
5. Optio: Orchestrate AI Coding Agents in Kubernetes from Ticket to PR
6. AI Coding Agents Are Removing Programming Language Barriers: How It Works
7. Some Uncomfortable Truths About AI Coding Agents in 2026
8. AI Coding Tools Make Developers Slower But They Think They're Faster: Study Analysis

**LLM Comparison (4):**
9. Gemma 4 12B Review 2026: Google's Encoder-Free Multimodal Model Benchmarked
10. DiffusionGemma: 4x Faster Text Generation — Google's Text-Diffusion Model Explained
11. GPT-5.6 Sol vs Claude Fable 5 vs Gemini 3.1 Pro: 2026 Mid-Year Coding Benchmark
12. Qwythos-9B-v2: Addressing Looping in 1M-Token LLMs — New Open Model Review

**AI Workflow Automation (4):**
13. n8n AI Workflow Automation 2026: Flexible Agent Pipelines for Technical Teams
14. Tracecat: Open-Source Security Alert Automation and SOAR Alternative 2026
15. DryMerge: Automate Workflows with Plain English — AI Automation Tool Review 2026
16. Patchwork: Open-Source Framework to Automate Development Gruntwork 2026

**AI for Developers (6):**
17. GitLost: How GitHub's AI Agent Was Tricked into Leaking Private Repositories
18. Windows 11 AI Agent Runs in Background with Access to Personal Folders: Privacy Analysis
19. Microsoft's Open-Source Tools Were Hacked to Steal AI Developer Passwords: What Happened
20. OWASP Agentic Top 10 Explained for Practitioners: AI Agent Security Risks 2026
21. Confident AI vs Opik vs Relari: LLM Evaluation Frameworks Compared 2026
22. Cua-Bench: Benchmarking AI Agents in GUI Environments — What Developers Need to Know

### Emerging Trends (from HN Algolia + Dev.to)

1. **AI agent security crisis deepens** — GitLost (539pts) shows GitHub's AI agent can be tricked into leaking private repos. Windows 11 ships an AI agent with personal folder access (703pts). Microsoft's open-source tools hacked to steal AI developer passwords (561pts). This is the dominant developer concern this week. Three new topics address this directly.

2. **Google's Gemma 4 family expands** — Gemma 4 12B (1062pts), QAT models for mobile (406pts), DiffusionGemma (327pts). Google is aggressively releasing open models across form factors. Major content opportunity for reviews and comparisons.

3. **MCP ecosystem continues growing** — Safari MCP Server (272pts), Blender MCP (151pts), Postgres MCP (167pts), MCP SDK in Bash (144pts), MCP-Shield (134pts), Strata (133pts). MCP is becoming the universal integration layer for AI agents.

4. **Agent evaluation tooling matures** — Confident AI (117pts), Opik (86pts), Relari (106pts), Cua-Bench (40pts). The evaluation framework space is heating up with multiple open-source entrants.

5. **AI coding agent skepticism grows** — "AI coding tools make developers slower" study (38pts), "Some uncomfortable truths" (80pts), "Are there real examples?" (86pts). The honeymoon phase is ending — balanced analysis content is in demand.

6. **Workflow automation renaissance** — n8n (195pts), Tracecat (264pts), Patchwork (116pts), DryMerge (180pts), Workflow86 (48pts). Multiple new entrants in the AI workflow automation space.

### Infrastructure Note
- **topics.json was missing** (file was deleted/lost) — restored from latest backup (2026-07-09T2206Z) and supplemented with 367 published posts reconstructed from filesystem
- **content/posts/ directory** does not exist — posts live at `/home/ubuntu/blog/posts/` (704 posts on disk)

### Strategy Adjustments

**kd_range**: Maintained at `{min: 0, max: 25}` for Phase 1.

**focus_topics**: Unchanged — AI coding tools, LLM comparison, AI workflow automation, AI for developers.

**cluster_priority**:
1. AI coding tools (9 new + existing = well-stocked)
2. LLM comparison (4 new — still understocked, continue prioritizing)
3. AI for developers (6 new — well-stocked)
4. AI workflow automation (4 new — well-stocked)

**new_opportunities**: Added 91 entries from Run 105 discovery (HN Algolia + Dev.to).

**refresh_targets**: Added 11 new monitoring targets for GitLost, Windows 11 AI agent, Gemma 4, DiffusionGemma, Safari MCP, GitHub Copilot harness, n8n, OWASP Agentic Top 10, evaluation frameworks, Cua-Bench, and GPT-5.6 vs Fable 5.

### Recommendations
1. **Next discovery run**: Continue prioritizing LLM comparison cluster — only 7 queued vs 42+ published
2. **Content refresh**: Claude Sonnet 5 review is ranking — consider updating with latest benchmark data
3. **AI agent security series**: GitLost + Windows 11 + Microsoft hack + OWASP Top 10 create a natural 4-article security series
4. **Gemma 4 coverage**: Google's open model family is generating massive HN interest — review and comparison articles will perform well
5. **Monitor GSC**: First real signals appearing — next report should show more pages indexed
