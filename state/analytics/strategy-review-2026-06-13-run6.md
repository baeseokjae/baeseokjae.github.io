# Strategy Review - 2026-06-13 Run 6

## Phase

Current phase: Phase 1, first signal integration. No non-review GSC or analytics files were present in `state/analytics/`, so this run used external competitor discovery plus inventory and internal-link checks.

## Queue State

- Topics before run: 3,296
- Active queued topics before run: 1
- Published posts checked: 580
- New queued topics added: 20
- Rejected candidates: 0
- New priority range: 5919-5938

## Competitor Sources Used

- GitHub Changelog: Copilot SDK GA and Copilot code-review team customization.
- OpenAI: Agents SDK evolution and Realtime API MCP server support.
- AWS Machine Learning Blog: Bedrock AgentCore payments, identity, coding-agent hosting, and Spring AI SDK for AgentCore.
- Cloudflare Docs: Agents, Code Mode MCP, payments capability, and OpenCode agent setup.
- Anthropic Engineering: MCP code execution, advanced tool use, and agent skills.
- Vercel Blog: AI SDK 6, AI Cloud, durable workflows, and AGENTS.md evals.
- Mintlify Blog: docs as AI interface, docs-to-MCP, real llms.txt examples, and Agent Score.
- WorkOS Blog: Pipes MCP, AI agent credentials, MCP security, and agent auth checklist.
- Braintrust Blog: six generations of AI agents, trace-to-dataset workflows, and Temporal integration.
- Docker Blog: Docker MCP Toolkit/Catalog and AI agent security.

## Topics Added

- `copilot-sdk-vs-openai-agents-sdk-2026`
- `copilot-sdk-vs-vercel-ai-sdk-6-2026`
- `copilot-code-review-custom-skills-vs-coderabbit-2026`
- `agentcore-identity-vs-workos-agent-auth-2026`
- `bedrock-agentcore-identity-oauth-github-tools-guide-2026`
- `spring-ai-bedrock-agentcore-java-agents-guide-2026`
- `bedrock-agentcore-payments-vs-google-ap2-2026`
- `cloudflare-agents-payments-guide-2026`
- `cloudflare-agents-vs-vercel-ai-cloud-2026`
- `opencode-cloudflare-agent-setup-guide-2026`
- `anthropic-code-execution-mcp-vs-cloudflare-codemode-2026`
- `dynamic-tool-discovery-vs-mcp-tool-loading-2026`
- `vercel-ai-cloud-vs-bedrock-agentcore-2026`
- `agent-ready-docs-score-checklist-2026`
- `mintlify-vs-readme-mcp-docs-2026`
- `workos-pipes-mcp-guide-2026`
- `braintrust-six-generations-ai-agents-evals-guide-2026`
- `braintrust-traces-to-datasets-guide-2026`
- `openai-realtime-api-mcp-server-support-guide-2026`
- `docker-mcp-toolkit-vs-cloudflare-codemode-2026`

## Validation

All promoted candidates passed the required checks:

- KD within strategy range 0-25.
- Search volume estimate at or above 200.
- Required title, slug, and keyword present.
- Slug absent from existing `topics.json`.
- Slug absent from published posts.
- Cluster matches current focus topics.

## Coverage Notes

The strongest saturated areas are broad MCP overviews, generic sandboxes, Temporal durable agents, AGENTS.md vs skills, Copilot SDK GA, AgentCore payments, and Mintlify docs-to-MCP. This run avoided exact re-adds and focused on comparison or implementation edges around those trends.

The lightweight inbound-link scan found 557 of 580 published posts with no inbound slug mentions. Treat that as a directional internal-link debt signal rather than a full crawler result, because it only checks explicit slug references in markdown.

## Strategy Adjustment

Keep Phase 1 focused on narrow developer-tooling gaps with clear source novelty:

- agent runtime comparisons
- auth and payment subflows
- trace-to-eval loops
- agent-ready documentation quality checks
- SDK/runtime decision guides

Avoid broad category repeats unless analytics later show clear demand.
