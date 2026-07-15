# Strategy Review - 2026-06-13 Run 5

## Phase

Current phase: Phase 1 - First Signal Integration.

No non-review GSC or Search Console export files were present under `state/analytics/`. This run used external competitor discovery, local topic deduplication, published-post slug checks, and the configured Phase 1 KD range of 0-25.

## Trigger

The active queue had dropped to 1 topic, below the strategist threshold of 10 queued topics. The run focused on rebuilding active queued inventory while avoiding duplicate slugs already present in `research/topics.json` or `content/posts/`.

## Inputs Checked

- `state/strategy.json`
- `research/topics.json`
- `content/posts/`
- `state/analytics/`
- Competitor and product blogs in AI coding agents, agent runtime security, agent evaluation, identity/OAuth for agents, and agent-ready API documentation

## Competitor Signals

- GitHub is splitting Copilot positioning across coding agent, agent mode, custom CLI agents, and the agent-native desktop app. Existing inventory already covered Copilot SDK and Playwright MCP debugging, so this run kept narrower active-queue gaps around custom CLI agents and coding-agent-vs-agent-mode positioning.
- Docker continues to turn AI coding-agent security incidents into sandbox and governance messaging. Existing runtime-security coverage is broad, so this run kept the concrete incident/horror-story angle.
- Anthropic's tool-writing guidance creates a practical gap around tool schemas, descriptions, eval feedback, and agent-assisted tool iteration, distinct from the already-covered Agent Skills topic.
- AWS AgentCore coverage is expanding beyond generic runtime/observability into payments, authorization-code MCP connection flows, and API Gateway-to-MCP exposure.
- LangChain is emphasizing trace-first eval readiness and agent improvement loops rather than generic observability listicles.
- Northflank is publishing around runtime subcategories: ephemeral environments, self-hosted sandboxes, and Runloop alternatives.
- WorkOS and Auth0 are pushing sharper agent-identity patterns: on-behalf-of OAuth, multi-hop delegation, scoped agent credentials, third-party access tokens, and MCP/Auth0 integration.
- ReadMe and Mintlify are moving API documentation into agent consumption: LLM-ready API docs and generated MCP servers from docs.

## Topics Added

Added 20 queued topics to `research/topics.json`.

Priority range: 5898-5918.

Cluster distribution:

- AI coding tools: 2
- AI for developers: 16
- AI workflow automation: 2

All added topics passed validation:

- KD within configured range 0-25.
- Estimated search volume at least 200.
- No exact slug duplicate in `topics.json`.
- No matching published post slug in `content/posts/`.
- Has title, slug, and keyword.
- Fits configured focus topics or current cluster priority.

## Added Slugs

- `github-copilot-custom-agents-cli-guide-2026`
- `github-copilot-coding-agent-vs-agent-mode-guide-2026`
- `anthropic-writing-effective-tools-for-agents-guide-2026`
- `aws-agentcore-payments-agentic-commerce-guide-2026`
- `aws-agentcore-mcp-authorization-code-flow-guide-2026`
- `aws-api-gateway-to-agentcore-mcp-guide-2026`
- `langchain-agent-evaluation-readiness-checklist-2026`
- `langchain-agent-improvement-loop-traces-guide-2026`
- `northflank-ephemeral-execution-environments-agents-guide-2026`
- `northflank-self-hosted-ai-sandboxes-guide-2026`
- `northflank-runloop-alternatives-ai-sandbox-guide-2026`
- `workos-ai-agent-on-behalf-of-oauth-guide-2026`
- `workos-ai-agent-multi-hop-delegation-guide-2026`
- `workos-ai-agent-credentials-guide-2026`
- `workos-logging-ai-agents-into-web-apps-guide-2026`
- `auth0-third-party-access-tokens-ai-agents-guide-2026`
- `auth0-mcp-agentic-match-guide-2026`
- `readme-llm-ready-api-documentation-checklist-2026`
- `readme-mcp-server-api-docs-guide-2026`
- `mintlify-docs-mcp-server-generation-guide-2026`

## Deduplication Notes

Skipped or avoided near-duplicate angles already represented in inventory:

- Copilot SDK GA and Playwright MCP UI debugging, already present as queued_throttled topics.
- Cloudflare Dynamic Workers and Docker AI governance, already present as queued_throttled topics.
- Anthropic Agent Skills and generic harness engineering, already present as queued_throttled/seeded topics.
- Persistent sandbox and generic runtime-security topics, already covered in queued_throttled or published inventory.
- Broad llms.txt and generic AI-ready documentation explainers, already represented by existing docs topics.

## Source Signals Used

- GitHub Blog: From one-off prompts to workflows: How to use custom agents in GitHub Copilot CLI - `https://github.blog/ai-and-ml/github-copilot/from-one-off-prompts-to-workflows-how-to-use-custom-agents-in-github-copilot-cli/`
- GitHub Blog: The difference between coding agent and agent mode in GitHub Copilot - `https://github.blog/developer-skills/github/less-todo-more-done-the-difference-between-coding-agent-and-agent-mode-in-github-copilot/`
- Anthropic Engineering: Writing effective tools for AI agents - `https://www.anthropic.com/engineering/writing-tools-for-agents`
- AWS ML Blog: Technical deep dive: AgentCore payments and innovation in agentic commerce - `https://aws.amazon.com/blogs/machine-learning/technical-deep-dive-agentcore-payments-and-innovation-in-agentic-commerce/`
- AWS ML Blog: Connecting MCP servers to Amazon Bedrock AgentCore Gateway using authorization code flow - `https://aws.amazon.com/blogs/machine-learning/connecting-mcp-servers-to-amazon-bedrock-agentcore-gateway-using-authorization-code-flow/`
- AWS ML Blog: Connect API Gateway to AgentCore Gateway with MCP - `https://aws.amazon.com/blogs/machine-learning/streamline-ai-agent-tool-interactions-connect-api-gateway-to-agentcore-gateway-with-mcp/`
- LangChain Blog: Agent Evaluation Readiness Checklist - `https://www.langchain.com/blog/agent-evaluation-readiness-checklist`
- LangChain Blog: The Agent Improvement Loop Starts with a Trace - `https://www.langchain.com/blog/traces-start-agent-improvement-loop`
- Northflank Blog: Ephemeral execution environments for AI agents in 2026 - `https://northflank.com/blog/ephemeral-execution-environments-ai-agents`
- Northflank Blog: Self-hosted AI sandboxes: Guide to secure code execution in 2026 - `https://northflank.com/blog/self-hosted-ai-sandboxes`
- Northflank Blog: Top Runloop alternatives for AI agent sandbox infrastructure in 2026 - `https://northflank.com/blog/runloop-alternatives`
- WorkOS Blog: OAuth's On-Behalf-Of flow for AI agents - `https://workos.com/blog/oauth-on-behalf-of-ai-agents`
- WorkOS Blog: AI agents and the multi-hop delegation problem - `https://workos.com/blog/oauth-multi-hop-delegation-ai-agents`
- WorkOS Blog: Securing agentic apps: Give your AI agents their own credentials - `https://workos.com/blog/ai-agent-credentials`
- WorkOS Blog: Logging AI agents into web apps: From cookie hacks to proper OAuth - `https://workos.com/blog/logging-ai-agents-into-web-apps`
- Auth0 Blog: Handling Third-Party Access Tokens Securely in AI Agents - `https://auth0.com/blog/third-party-access-tokens-secure-ai-agents/`
- Auth0 Blog: MCP + Auth0: An Agentic Match Made in Heaven - `https://auth0.com/blog/mcp-and-auth0-an-agentic-match-made-in-heaven/`
- ReadMe Blog: How to Get Your API Documentation LLM-Ready - `https://readme.com/blog/llm-ready-api-documentation`
- ReadMe Blog: Give AI Agents Direct Access to Your API with ReadMe's MCP Server - `https://readme.com/blog/api-documentation-mcp-server-readme`
- Mintlify Blog: Generate MCP servers from your docs - `https://www.mintlify.com/blog/generate-mcp-servers-for-your-docs`

## Strategy Update

Updated `state/strategy.json` with a new Phase 1 opportunity note and refreshed `cluster_priority`.

Recommendation for the next run: keep queue refill focused on fresh low-KD developer-tooling gaps, but require narrow source-backed angles because broad OAuth, MCP, sandbox, agent-skills, llms.txt, observability, and Copilot SDK coverage is now heavily represented.
