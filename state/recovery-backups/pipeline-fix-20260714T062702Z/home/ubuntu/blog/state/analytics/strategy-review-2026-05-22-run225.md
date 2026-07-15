# Strategy Review — Run 225 (2026-05-22)

## Phase: 0 (Foundation — external data driven)

## Summary

+8 new topics added. Total topics: 2531. Clusters: AI coding=675q, AI dev=690q, LLM cmp=325q, AI workflow=332q.

This run follows Run 224 (same day). Focus: Google I/O 2026 aftermath signals + enterprise MCP ecosystem expansion.

## Key Signals This Run

### 1. xAI Grok Build — New CLI coding agent in the arena (May 14)
xAI entered the coding agent race with Grok Build, a CLI tool with 8 parallel plan-search-build pipelines. Available first to SuperGrok Heavy ($300/mo). Notably reads CLAUDE.md/AGENTS.md files, compatible with existing agent workflows. Uses Agent Client Protocol (ACP) for embedding in other apps. Search intent is rising rapidly post-launch with near-zero competition on practical guides.

### 2. Google I/O 2026 — Antigravity 2.0 + Android AI coding (May 19)
Antigravity 2.0 launched with desktop app, CLI, and SDK. Gemini 3.5 Flash is the new headliner (4x faster than frontier models, outperforms Gemini 3.1 Pro on coding/agentic benchmarks). AI Studio now supports native Kotlin for building Android apps with one-click Cloud Run + Firebase deployment. This creates a new "Android vibe coding" category distinct from web vibe coding. Note: Gemini CLI is being sunset on June 18 — migration guides are timely.

### 3. Enterprise MCP ecosystem matures — AWS, Splunk, ServiceNow, SAP all joining
The MCP ecosystem is no longer just Claude/Cursor tools. AWS MCP Server GA (May 6) brings managed AI agent access to all AWS APIs with enterprise-grade IAM + CloudTrail. ServiceNow opened its full system of action to all AI agents via MCP. Splunk launched an MCP Server for observability data. AWS SAP MCP went GA in Bedrock AgentCore. This signals MCP is becoming enterprise infrastructure — practical integration guides are nearly absent.

### 4. Self-hosted AI coding agents for regulated enterprises (Coder Agents, May 6)
Coder launched self-hosted, model-agnostic AI coding agents for enterprises that need code to stay on-prem. 61% of engineering teams are running agents but most lack private infrastructure. This addresses a growing compliance gap in regulated industries (finance, healthcare, defense). Near-zero competition on enterprise self-hosted AI coding agent guides.

### 5. AI + Security integration deepens (Snyk + Claude)
Snyk integrated Claude models into its AI Security Platform, enabling vulnerability scanning of AI-generated code. This completes a loop: AI generates code → AI reviews security. Distinct from existing Snyk vs Semgrep comparison content; focuses on the Claude integration workflow for teams already using Snyk.

## Topics Added

| Slug | Cluster | KD | SV |
|------|---------|----|----|
| grok-build-developer-guide-2026 | AI coding tools | 4 | 350 |
| coder-agents-enterprise-self-hosted-guide-2026 | AI coding tools | 5 | 280 |
| google-ai-studio-android-kotlin-vibe-coding-2026 | AI coding tools | 5 | 300 |
| aws-mcp-server-developer-guide-2026 | AI for developers | 4 | 280 |
| snyk-claude-ai-code-security-guide-2026 | AI for developers | 5 | 300 |
| servicenow-mcp-ai-agent-integration-2026 | AI for developers | 5 | 250 |
| splunk-mcp-server-ai-observability-guide-2026 | AI for developers | 5 | 250 |
| aws-sap-mcp-bedrock-agentcore-guide-2026 | AI for developers | 4 | 220 |

All candidates passed validation: KD 0–14 ✓, SV 200+ ✓, no duplicate slugs ✓, fits focus_topics ✓

## Phase 0 Observations (Competitor Gap Analysis)

- **Enterprise MCP guides** are nearly absent in SERP — competitors cover MCP generally but not enterprise-specific integrations (AWS/SAP/Splunk/ServiceNow). First-mover opportunity.
- **Self-hosted AI coding agents** have growing enterprise search intent but zero quality guides. Coder Agents, Void, Tabby occupy this space — an enterprise comparison would be high-value.
- **Android vibe coding** is a distinct emerging category. Existing vibe coding guides focus on web (Bolt, Lovable, v0). AI Studio's native Kotlin support creates a new developer search intent.
- **Grok Build** represents xAI's first serious coding agent entry. Given Grok brand awareness, search intent will grow rapidly — getting in early is valuable.

## Cluster Status

| Cluster | Queued | Writing | Published |
|---------|--------|---------|-----------|
| AI coding tools | 675 | 15 | 183 |
| AI for developers | 690 | 15 | 101 |
| LLM comparison | 325 | 0 | 52 |
| AI workflow automation | 332 | 4 | 29 |
| Unclustered legacy | 1 | 0 | 48 |
