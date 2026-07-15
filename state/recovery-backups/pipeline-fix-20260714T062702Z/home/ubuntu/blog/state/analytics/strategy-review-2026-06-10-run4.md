# Strategy Review - 2026-06-10 Run 4

## Phase 1 Status

- Current phase: Phase 1 (First Signal Integration)
- KD range: 0-25
- Search volume filter: 200+ estimated monthly searches
- Analytics files found: prior strategy reviews only; no separate GSC query export was present in `~/blog/state/analytics/`
- Queue health before run: 3067 total topics, 2390 queued
- Queue health after run: 3083 total topics, 2406 queued

## New Topics Added This Run (+16)

### AI Coding Tools (+15)

1. `snyk-agentic-development-lifecycle-security-risks-2026` - agentic development lifecycle security risks. KD 6, SV 460
2. `snyk-clinejection-supply-chain-attack-guide-2026` - Clinejection supply chain attack. KD 5, SV 360
3. `snyk-cursor-mcp-ai-generated-code-scanning-guide-2026` - Snyk Cursor MCP AI-generated code scanning. KD 5, SV 340
4. `snyk-mcp-server-secure-at-inception-guide-2026` - Snyk MCP Server secure at inception. KD 4, SV 280
5. `aikido-agent-skills-hallucinated-npx-commands-guide-2026` - agent skills hallucinated npx commands. KD 5, SV 420
6. `aikido-promptpwnd-github-actions-ai-agents-guide-2026` - PromptPwnd GitHub Actions AI agents. KD 5, SV 360
7. `aikido-malicious-vscode-extension-supply-chain-guide-2026` - malicious VS Code extension supply chain. KD 5, SV 320
8. `semgrep-openclaw-security-engineers-cheatsheet-2026` - OpenClaw security engineer cheatsheet. KD 4, SV 300
9. `semgrep-assistant-memories-zero-false-positive-sast-2026` - Semgrep Assistant Memories zero false positive SAST. KD 4, SV 260
10. `checkmarx-appsec-ai-2026-industry-outlook-guide` - AppSec AI 2026 industry outlook. KD 6, SV 420
11. `checkmarx-secure-ai-generated-code-dev-leaders-guide-2026` - secure AI-generated code dev leaders. KD 6, SV 380
12. `checkmarx-human-in-the-loop-ai-lies-security-guide-2026` - AI lies human-in-the-loop security. KD 4, SV 260
13. `checkmarx-ai-inventory-gap-supply-chain-guide-2026` - AI inventory gap software supply chain. KD 5, SV 320
14. `sonarsource-ai-code-security-relationship-guide-2026` - AI and code security SonarSource. KD 5, SV 300
15. `sonarqube-ai-agent-sql-injection-taint-analysis-guide-2026` - SonarQube AI agent SQL injection taint analysis. KD 4, SV 280

### AI For Developers (+1)

1. `semgrep-a2a-protocol-security-guide-2026` - A2A protocol security guide. KD 5, SV 340

## Candidate Validation

All promoted candidates passed:

- KD within configured range (0-25)
- Search volume estimate >= 200
- Unique slug across `topics.json` and published post filenames
- Required title, slug, and keyword present
- Cluster fits current focus topics or cluster priority

Rejected this run: 0

## Competitor Signals

- Snyk is framing agent security as a full lifecycle problem: untrusted tools, MCP servers, command execution, Cursor MCP scanning, and supply-chain attacks through agents.
- Aikido is publishing practical examples of agent skill and CI/CD prompt-injection failures, including hallucinated `npx` commands and GitHub Actions agent attacks.
- Semgrep adds useful security-engineer framing for OpenClaw and A2A, plus AI-powered memory for reducing false positive SAST workflows.
- Checkmarx is leaning into governance and inventory gaps: AI-generated code, human-in-the-loop failures, and lack of visibility into AI assets in the software supply chain.
- SonarSource provides concrete verification and taint-analysis angles around AI-generated code, including SQL injection produced by coding agents.

## Strategy Adjustments

- Keep Phase 1 behavior. No Phase 2 performance logic was applied because no separate GSC query export exists yet.
- Add an agent-security subcluster under AI coding tools: MCP risk, skill supply chain, prompt injection in CI/CD, AI inventory, taint analysis, and secure generated-code review.
- Avoid broad repeats like generic shadow-AI governance and developer trust-gap summaries because adjacent queued/published coverage already exists.
- Internal-link targets: enterprise AI coding security guardrails, AI SAST tools, AI-generated code security, GitHub Actions agent workflows, MCP security, and code-review automation.

## Sources Reviewed

- Snyk agentic development lifecycle: https://snyk.io/blog/agentic-development-lifecycle/
- Snyk Clinejection supply-chain attack: https://snyk.io/blog/cline-supply-chain-attack-prompt-injection-github-actions/
- Snyk Cursor MCP scanning: https://snyk.io/blog/scan-your-ai-generated-code-from-cursor-using-model-context-protocol-mcp/
- Snyk Secure at Inception: https://snyk.io/blog/secure-at-inception-black-hat-2025/
- Aikido hallucinated npx commands: https://www.aikido.dev/blog/agent-skills-spreading-hallucinated-npx-commands
- Aikido PromptPwnd GitHub Actions: https://www.aikido.dev/blog/promptpwnd-github-actions-ai-agents
- Aikido malicious VS Code extension: https://www.aikido.dev/blog/github-breached-vs-code-extension
- Semgrep OpenClaw cheat sheet: https://semgrep.dev/blog/2026/openclaw-security-engineers-cheat-sheet
- Semgrep A2A protocol security: https://semgrep.dev/blog/2025/a-security-engineers-guide-to-the-a2a-protocol
- Semgrep Assistant Memories: https://semgrep.dev/blog/2025/making-zero-false-positive-sast-a-reality-with-ai-powered-memory
- Checkmarx AppSec AI outlook: https://checkmarx.com/blog/ai-llm-tools-in-application-security/just-released-the-future-of-appsec-in-the-era-of-ai-2026-industry-outlook/
- Checkmarx secure AI-generated code: https://checkmarx.com/blog/the-cost-of-ai-velocity-5-actions-dev-leaders-must-take-to-secure-their-codebase-from-ai-vulnerabilities/
- Checkmarx AI lies security: https://checkmarx.com/blog/when-the-ai-lies-a-new-threat-emerges-for-human-in-the-loop-security/
- Checkmarx AI inventory gap: https://checkmarx.com/blog/ai-llm-tools-in-application-security/the-ai-inventory-gap-why-your-organization-has-no-idea-what-ai-assets-are-part-of-your-software-supply-chain/
- SonarSource AI and code security: https://www.sonarsource.com/blog/managing-the-tricky-relationship-between-ai-and-code-security
- SonarQube SQL injection taint analysis: https://www.sonarsource.com/blog/how-sonarqube-traces-a-sql-injection-your-ai-coding-agent-produced
