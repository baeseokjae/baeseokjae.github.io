# Strategy Review — 2026-07-14 Run 107

## Phase 1: First Signal Integration

### Queue Status
- **Total topics**: 3,062 (up from 2,923 — restored from backup + 139 new)
- **Queued topics**: 2,433 (up from 2,294 — 139 new queued)
- **Published**: 711 (filesystem count)
- **Rejected**: 7 (unchanged — 0 new rejections)
- **Seeded/Writing**: 52

### Queue Health
- **139 new topics discovered and queued** in this run
- **0 duplicates** — all checked against 2,911 existing slugs and 711 published posts
- **0 rejected** — all passed KD range (0-25), focus topic, and field validation
- **topics.json was restored from backup** — the live file had been truncated to only 3 entries. Restored from `/home/ubuntu/blog/research/topics.json.bak` (2,923 entries) and merged with 139 new topics.

### Web Discovery Policy
Used lightweight retrieval only:
- **HN Algolia API** (4 queries): AI agent, MCP, coding agent, LLM/benchmark
- **Dev.to API** (3 queries): ai tag, agents tag, mcp tag (top 7 days)
- **GitHub Search API** (2 queries): AI projects, agent projects (last 7 days)
- **No browser navigation, screenshots, Playwright, or agent-browser used**

### New Topics by Cluster

**AI Coding Tools (30):**
1. FableCut: Browser Video Editor AI Agents Can Drive — Open Source Review 2026
2. Juggler: Open-Source GUI Coding Agent by the Creator of JUCE — Review 2026
3. Jacquard: A Programming Language for AI-Written, Human-Reviewed Code
4. Claude Code vs OpenCode: Token Overhead Comparison — 33K vs 7K Before Reading Prompt
5. Old and New Apps via Modern Coding Agents: Terry Tao's Developer Experience
6. Clawk: Give Coding Agents a Disposable Linux VM, Not Your Laptop — Review 2026
7. Mindwalk: Replay Coding-Agent Sessions on a 3D Map of Your Codebase
8. Benchmarking Coding Agents on Databricks' Multi-Million Line Codebase
9. Coding Agents Think Ahead of Time: Planning Paradigm Research Paper Analysis
10. Abralo: Run Several Claude Code Agents in One Window — Free Tool Review
11. Your Hand-Typed Slop Isn't Honest: The AI-Generated Code Quality Debate
12. I Deleted 200 Lines of Code I Didn't Write: Learning More from AI Code Than Writing It
13. How I Made a Rust Hot Path 27x Faster and Refused the AI Fix
14. AGENTS.md Kept True: Stop the Rot and Watch Your Agent Trust It
15. Ditto: Mine Claude Code and Codex Logs into a Local Agent Profile
16. Octop: Tencent Cloud's Self-Hosted Multi-User Multi-Agent AI Assistant
17. Awesome Gemini CLI Subagents: 51 Production-Ready Agents Collection
18. AgentMaker: General-Purpose Python Framework for LLM Agents and Multi-Agent Systems
19. Grok Delegate: Hand Work to Claude Code or Codex as Background Task
20. CrewCtl: Manage Claude Code, Codex CLI, Gemini CLI from One Center
21. Metis: Coding Agent CLI with Read, Bash, Edit, Write Tools and Session Management
22. Why the Codebase Is Your Biggest Context Bill: Output Compression Doesn't Fix It
23. One Developer, Five Terminals, Zero Awareness: Multi-Agent Coordination Challenges
24. A Running Cost Meter and MCP Tripwire Land in Visual Studio's June Update
25. ai-openclaw-cli: OpenClaw MCP CLI for Claude Code, Cursor, and 20+ AI Agents
26. Reinit: Agent Skill That Turns Coding-Agent Session History into Durable Repository Guidance
27. AgentRule-Skill: Structured Skill for Building Reliable AI Agents
28. Agent Scaffold: Scaffold Repeatable Agent Workflows into Any Project
29. Ally: Desktop AI Coding Assistant That Works with Local Projects
30. Knote: Local-First Markdown Editor with Reviewable AI Agent

**LLM Comparison (8):**
31. Migrating a Production AI Agent to GPT-5.6: 2.2x Faster, 27% Cheaper Case Study
32. Porting Gemma-4 (2B/4B/12B) to AWS Inferentia2: Deployment Guide
33. The Open-Weight Cliff: What Happens When Open Models Stop Improving
34. GLM 5.2 Running on a Slow Computer: Open-Source Model Optimization Case Study
35. Reame: CPU Inference Server That Gets Faster as It Runs — Review 2026
36. AMD Ryzen AI Halo: Hands-On Review for Local AI Development
37. Simple Benchmark: Ollama on Jetson Nano — Local LLM Deployment Performance
38. J-Wash: Jacobian-Brainwash Framework for Analyzing and Customizing LLMs

**AI Workflow Automation (23):**
39. From Prompt Files to Agent Skills: Unifying Content Automation Workflows
40. I Spent a Week Fixing the Wrong Skill: Lessons from Evaluating an AI PR Reviewer
41. I Cut My Agent Token Bill by 60%: Exact Cost Optimization Setup
42. How to Stop AI Agent Cost Blowups Before They Happen
43. Flawless: AI SRE AgenticOps for Kubernetes and Cloud Infrastructure
44. Generative Media Skills: Research-Backed Agent Skills for Image Video Audio
45. Didit Copilot: Shipping an AI Agent That Lives Inside the App
46. How I Turned Slack Into an AI Teammate That Opens Pull Requests
47. The (No Longer) Missing Multi-Agent Pattern: Triggering Dynamic Workflows from an Agent
48. Building a Document-RAG Agent on GCP's Agent Development Kit (ADK)
49. Delivered but Unbilled: Your AI Stream Logged Zero Tokens — FinOps Guide
50. Checkpoint-Skip Gate: Task Success 100%, Checkpoint Never Ran — Agent Reliability
51. Build Your Own Google Antigravity Agent in Slack: Integration Guide
52. I Fixed My AI Reviewer Then Kept Solving the Wrong Problem
53. InsightsTrack + Pulse: Teaching Claude Desktop to Read Web Analytics via MCP
54. Container-Native AI: Orchestrating Agent Infrastructure with Docker and GPU Scheduling
55. Surgical SEO: Automating WordPress Metadata Without Giving AI Full Access
56. Hybrid Container Governance: Scaling Patterns That Work for AI Workloads
57. Bringing GA4 into an MCP Server: Making Analytics Agent-Friendly
58. Lark ACP Bridge: Bridge Feishu/Lark Bots to Claude Code, Kiro CLI, Gemini, Copilot
59. OpenXFlow: Open-Source Visual AI Workflow Platform Powered by Skills, MCP, Agents
60. WorkBuddy: Embed AI Chat Agent Inside Obsidian
61. AI Collaboration Operating System: Lightweight AI-Native Collaboration for Solo Developers

**AI for Developers (78):**
62. GitLost: How GitHub's AI Agent Was Tricked into Leaking Private Repositories
63. Microsoft Flint: A Visualization Language for AI Agents — Complete Guide 2026
64. Kastor: Terraform-Style Specs for AI Agents — Infrastructure as Code for Agents
65. Reverse-Engineering Web Apps into Agent Tools: A Practical Guide
66. Who Manages the Agents? Governance Challenges in Multi-Agent Systems
67. BillAI Bass: AI-Powered Big Mouth Billy Bass Using Strands Agents — Novel Agent Use Case
68. Context.dev: API to Get Structured Data from Any Website for AI Agents
69. The State of MCP Security 2026: Comprehensive Analysis and Best Practices
70. Bigger Context Windows Didn't Make Our RAG Smarter: Lessons Learned
71. Being an Engineer in the AI Era: Role Evolution and Career Guide 2026
72. A Vibe Is Not a Verdict: Building AI Tools That Say 'I Don't Know'
73. The Project File Is the Interface: Letting AI Agents Drive a Video Editor
74. The Agent Faked a Test Log, Then Believed It: Self-Editing Harness Provenance Problem
75. How We Test an AI Product Without Burning Credit: Budget Testing Guide
76. An Agent That Hunts Bugs in My App While I Sleep: Nocturnal Testing Agent Guide
77. An Alternative to LLM Quality Gates: Deterministic Routing and Sampling
78. Prompt Engineering, Context Engineering, Loop Engineering: What Actually Changed
79. Six Experiments on Adversarial Verification: The 75% Wall That Didn't Move
80. Alberta Ran 50 AI Agents in Parallel: Everyone Shared the Same Number
81. The Citation Lied Without Lying: Hard Limits of AI Memory Gates
82. MCP for TypeScript Developers: What It Actually Solves Beyond the Hype
83. AI Agents Cheat on Pull Requests: I Mined 327 of Them to Prove It
84. The Two Scariest Parts of Autonomous Agents: Runaway Loops and Exposed APIs
85. Prompt Caching Is an Architectural Pattern, Not a Cost Optimization
86. From SDLC to AI-DLC: Coding Agents Are Only the Beginning
87. My Agent Kept Writing Sleep Loops: Giving It a Better Primitive
88. Everyone Is Hoping AI Fails: Building the Net Anyway
89. Loop Engineering: The Six-Layer Architecture Behind Self-Improving Agents
90. Your AI Agent Doesn't Need More Tools: It Needs Receipts
91. Your AI Agent Says Done: Who Checks That from Outside the Agent?
92. Claude Code Beyond the Prompt: Your First MCP Server Tutorial
93. Best AI Agent Authentication Platforms 2026: Comparison Guide
94. WebMCP: Making Your Site Usable by AI Agents
95. Dual-Tier Memory Architecture for AI Agents: L1 Scratchpad and L2 Vault
96. SQLite + Vector Search: Dependency-Free AI Memory Pipeline Under 10ms
97. How to Vet an MCP Server Before You Install It: Security Guide
98. Hardening an MCP Server: Production-Ready Jira/Confluence Integration
99. I Scanned 8,764 MCP Servers for Security Vulnerabilities: What I Found
100. Building AI Agents That Survive Restarts: Persistent Memory Done Right
101. Local Vulnerability Research Pipeline: 14B Code LLM Reviews Source Files
102. Agent Pulse: Evidence-Backed AI Industry Intelligence and Trends
103. Cpp2Rust: Translating C++ to Safe Rust Automatically — AI-Assisted Migration Tool
104. Mandate Freshness Gate: Valid Signature, Revoked Authority — Agent Security Pattern
105. I Built an Error Notebook for My AI Agent: 266 Rules, 66 Interceptions
106. A Reproducible Result Can Still Be a Lie: AI Evaluation Reliability
107. The AI Orientation Tax: It's Missing Context, Not Discipline
108. Smarter Coding Agents Are Better Liars: Agent Hallucination Analysis
109. The Cold Start: Learning a Programming Language by Submitting a Program
110. How a Preinstall Hook Silently Ran Malware on npm Install: Supply Chain Security
111. I Created a Protocol for AI Agents to Talk to Each Other: ACP (Agent Communication Protocol)
112. From REST to MCP: The Design Shift for AI-Native APIs
113. PVM: Give Any LLM Long-Term Memory Without API Keys or GPU in ~800 Lines Python
114. MCP Observatory: Building Trustworthy AI Agents Through Observability
115. I Rolled Back My MCP Skills Experiment: Lessons Learned
116. What Building a Remote MCP Server Taught Me About Authentication
117. My MCP Server Kept Crashing: Error Recovery Pattern That Saved It
118. AI Agents Can Now Accept Payments in 10 Countries: MCP Payment Integration Guide
119. I Built an MCP Server for X (Twitter): 14 Tools in ~600 Lines
120. The Week in Review: Agents Got Wallets, Rails, Marketplaces — Still No Settlement
121. Beyond the Cloud: Why Local-First AI Infrastructure Is the Only Choice for 2026
122. The Old Way of Publishing MCP Servers Is Gone: What Replaced It
123. Tools vs Raw Commands: The Token Cost Theory
124. I Got Featured on OWASP ZAP Blog: Building an AI Layer on Top of It
125. gVisor vs Firecracker for AI Agent Sandboxing: Auditing 8,764 MCP Servers
126. Response to gVisor vs Firecracker: What We Learned Auditing 8,764 MCP Servers
127. I Migrated My MCP Server From STDIO to Streamable HTTP: Migration Guide
128. Why I Rejected an Event Bus for My Solo Agent Fleet: State Is Truth, Events Are Rumors
129. SQLite + Vector Search: The Dependency-Free AI Memory Stack Outperforming Pinecone
130. Why I Built Glyphic as Infrastructure, Not an App: MCP-First Design
131. How an Unbounded fastmcp Version Constraint Took Down Production
132. Give Your AI Assistant a Private Memory: Local Search Engine Integration
133. I Turned My Obsession With Trustworthy AI Agents Into MCP Observatory
134. MemRaw: An Open Experiment in Memory for AI Agents — The Whole Memory Always in Prompt
135. Moneyclaw: OpenClaw Agents for Prepaid Wallet, Virtual Card, OTP — Fintech Agent Tools
136. Warden: Docker-Based AI Agent Sandboxing Platform
137. Liyuan: AI Agent-Centric Role-Playing App with Memory Ledger and Decision Cards
138. AEGIS-Core: Cognitive Runtime Layer for AI Engineering with Planning and Memory
139. Product Design Harness: Agentic Design Process with Designer-in-the-Loop

### Emerging Trends (from HN Algolia + Dev.to + GitHub)

1. **Token overhead becomes a competitive metric** — Claude Code sending 33K tokens before reading the prompt vs OpenCode's 7K (693pts HN) is the biggest story. Developers are waking up to the cost of agent overhead. Major content opportunity for comparison and optimization guides.

2. **MCP security matures into a dedicated category** — State of MCP Security PDF (37pts), I scanned 8,764 MCP servers (Dev.to), MCP vetting guides, hardening guides, and sandbox comparisons (gVisor vs Firecracker) all appearing simultaneously. MCP security is becoming its own sub-niche.

3. **Agent provenance and verification crisis** — "The Agent Faked a Test Log" (22❤️), "AI Agents Cheat on Pull Requests" (4❤️), "Your AI Agent Says Done. Who Checks?" (2❤️), "A Reproducible Result Can Still Be a Lie" (1❤️). The trust problem in agent outputs is a growing theme.

4. **Agent cost optimization becomes mainstream** — "I Cut My Agent Token Bill by 60%", "How to Stop AI Agent Cost Blowups", "Delivered but Unbilled: Zero Tokens", "Tools vs Raw Commands: Token Cost Theory". Agent FinOps is emerging as a practical need.

5. **Open-source coding agent ecosystem explodes** — Juggler (115pts), Clawk (213pts), OpenCode (693pts), Abralo (37pts), Metis, AgentMaker, CrewCtl, Grok Delegate. The open-source agent tooling space is fragmenting rapidly.

6. **Agent memory architecture patterns diversify** — Dual-Tier Memory (L1/L2), SQLite + Vector Search, PVM (no API keys), MemRaw (whole memory in prompt), Building Agents That Survive Restarts. Multiple competing approaches to agent memory.

7. **MCP payment and commerce integration** — AI agents accepting payments in 10 countries, MCP payment servers, agent wallets and marketplaces. The agent economy infrastructure layer is being built.

### Infrastructure Note
- **topics.json was truncated** (only 3 entries) — restored from backup (2,923 entries) and merged with 139 new topics = 3,062 total
- **Backup used**: `/home/ubuntu/blog/research/topics.json.bak` (2,923 entries, dated 2026-07-14T19:26Z)
- **Published posts**: 711 on filesystem

### Strategy Adjustments

**kd_range**: Maintained at `{min: 0, max: 25}` for Phase 1.

**focus_topics**: Unchanged — AI coding tools, LLM comparison, AI workflow automation, AI for developers.

**cluster_priority**:
1. AI coding tools (30 new — well-stocked at 2,433 queued)
2. AI for developers (78 new — largest cluster, well-stocked)
3. AI workflow automation (23 new — well-stocked)
4. LLM comparison (8 new — still understocked relative to demand, continue prioritizing)

### Recommendations
1. **LLM comparison cluster still needs prioritization** — only 8 new vs 78 for AI for developers. The GPT-5.6 migration case study, Gemma-4 deployment guide, and AMD Ryzen AI Halo review are strong additions but more are needed.
2. **Token overhead comparison content** — Claude Code vs OpenCode (693pts HN) is the highest-signal story this week. A detailed comparison/review would perform well.
3. **MCP security series** — State of MCP Security + vetting guide + hardening guide + sandbox comparison create a natural 4-article security series.
4. **Agent FinOps series** — Token cost theory + cost blowup prevention + 60% bill reduction + unbilled tokens create a practical cost optimization series.
5. **Agent provenance series** — Faked test logs + PR cheating + external verification + reproducible lies create a trust/verification series.
6. **Monitor GSC** — Phase 1 continues; early signals should be appearing in analytics reports.
