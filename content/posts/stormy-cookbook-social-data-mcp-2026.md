---
title: "Stormy Cookbook: The Open-Source Social Data API and MCP Server for AI Agents"
date: 2026-07-27T19:02:02+00:00
tags:
  - Stormy social data MCP server
  - AI agents
  - social media API
  - MCP server
  - open source
  - influencer marketing
  - social data extraction
description: "Stormy Cookbook is an open-source social data API and MCP server that unifies TikTok, YouTube, Instagram, X, LinkedIn, and Reddit into one REST API and MCP toolset for AI agents."
draft: false
cover:
  image: "/images/stormy-cookbook-social-data-mcp-2026.png"
  alt: "Stormy Cookbook: The Open-Source Social Data API and MCP Server for AI Agents"
  relative: false
schema: "schema-stormy-cookbook-social-data-mcp-2026"
---

## What Is Stormy Cookbook?

Stormy Cookbook is an open-source project launched on July 27, 2026, that provides a unified REST API and Model Context Protocol (MCP) server for accessing social media data across six major platforms: TikTok, YouTube, Instagram, X (Twitter), LinkedIn, and Reddit. Instead of managing six separate API integrations with different authentication schemes, rate limits, and data formats, developers and AI agents can use Stormy as a single endpoint for social data. The project is MIT-licensed, has already gained 72 GitHub stars on launch day, and ships with 10 copy-pasteable recipes for common social data workflows.

## Why a Unified Social Data API Matters for AI Agents

Building an AI agent that needs social media data today means dealing with a fragmented landscape. TikTok has one API, YouTube has another, Instagram requires the Meta Graph API, X (Twitter) has its own v2 API, LinkedIn uses a completely different access model, and Reddit has yet another. Each platform has its own authentication flow, rate-limiting strategy, data schema, and pricing — or in some cases, no public API at all for certain data types.

For an AI agent developer, this creates a massive integration tax. Every new platform you want to support means weeks of reading documentation, implementing OAuth flows, handling rate limits, and normalizing data into a consistent format. Stormy eliminates this by providing a single REST API and MCP server that abstracts all six platforms behind one interface.

The MCP (Model Context Protocol) integration is particularly powerful. MCP is an open protocol developed by Anthropic that allows AI models to interact with external tools and data sources through a standardized interface. Because Stormy ships as an MCP server, any MCP-compatible client — Claude Code, Cursor, Codex CLI, ChatGPT with custom connectors, or any custom MCP host — can immediately access social data without writing any integration code. The agent simply discovers the available tools and calls them.

## Key Features at a Glance

Stormy Cookbook packs a remarkable amount of functionality into a clean, developer-friendly package. Here is a breakdown of the core capabilities:

| Feature | Details |
|---------|---------|
| **Platforms Covered** | TikTok, YouTube, Instagram, X (Twitter), LinkedIn, Reddit |
| **API Protocols** | REST API + MCP Server (Streamable HTTP transport) |
| **MCP Tools** | 10 tools: search_people, lookup_profile, find_emails, estimate_price, account_status, describe_social_data, start_social_job, get_social_job, list_social_jobs, cancel_social_job |
| **Pricing Model** | Pay-per-result ($0.01–$0.15), charged only on success |
| **Monthly Retainer** | $50/month with $25 included usage (2,500 credits) |
| **Durable Jobs** | Async job system for 25+ results, email batches, long-running work |
| **Verified Emails** | Email finding for Instagram, TikTok, and YouTube profiles |
| **License** | MIT (open source) |
| **Launch Date** | July 27, 2026 |

### The 10 MCP Tools

The MCP server exposes 10 tools that cover the full range of social data operations:

1. **search_people** — Find people across platforms by name, username, or criteria
2. **lookup_profile** — Get detailed profile information for a specific user
3. **find_emails** — Discover verified email addresses for influencers and creators
4. **estimate_price** — Get sponsorship pricing estimates for creators
5. **account_status** — Check whether an account is active, suspended, or deleted
6. **describe_social_data** — Get metadata about available social data types and fields
7. **start_social_job** — Launch a durable job for batch data collection
8. **get_social_job** — Poll the status and results of a running job
9. **list_social_jobs** — View all active and completed jobs
10. **cancel_social_job** — Stop a running job

### Durable Jobs System

One of the standout features is the durable jobs system. When you need more than 25 results, want to collect email addresses in bulk, or need to run a long data collection operation, you can start a job and poll for results. This avoids holding HTTP connections open for extended periods and makes large-scale social data collection practical for AI agents that need to process data asynchronously.

## Pricing Model

Stormy uses a pay-per-result pricing model that is refreshingly transparent. You are charged only when an API call returns a successful result — failed requests cost nothing.

| Data Type | Price per Result |
|-----------|-----------------|
| Cached profile or search result | $0.01 |
| Fresh profile lookup | $0.05 |
| Fresh discovery (search) | $0.08 |
| Verified email | $0.15 |

The cache-first approach is a smart economic design. If you are building a monitoring dashboard that checks the same 50 influencers daily, most of those lookups will hit the cache at $0.01 each — $0.50 per day for a full monitoring cycle. Fresh lookups are more expensive because they require live API calls to the underlying social platforms.

For heavier usage, the $50/month retainer includes $25 in usage credits (2,500 credits), effectively giving you a 50% discount on the first $25 of consumption. At scale, this makes Stormy significantly cheaper than maintaining direct integrations with six platforms, each of which may have its own paid tier.

## The 10 Recipes

The cookbook format is what sets Stormy apart from a standard API. Instead of dumping documentation, the project ships 10 ready-to-use recipes that solve real problems. Each recipe includes copy-pasteable code for both the REST API and MCP server.

### Recipe 1: Influencer Discovery
Search for influencers across multiple platforms by niche, follower count, engagement rate, or location. Returns unified results with profile links, follower counts, and estimated sponsorship prices.

### Recipe 2: Outreach List Builder
Combine influencer discovery with the find_emails tool to build complete outreach lists. Get verified emails for Instagram, TikTok, and YouTube creators in one workflow.

### Recipe 3: CRM Enrichment
Take a list of existing customer or partner social handles and enrich them with current follower counts, engagement metrics, and account status. Ideal for keeping CRM data fresh.

### Recipe 4: Competitor Analysis
Monitor competitor social presence across all six platforms. Track follower growth, posting frequency, and engagement trends over time using the durable jobs system for scheduled checks.

### Recipe 5: Social Media Monitoring
Set up ongoing monitoring for brand mentions, competitor activity, or industry trends. The cache-first pricing makes repeated queries economical — most checks hit the $0.01 cached tier.

### Recipe 6: Cross-Platform Research
Research a person or brand across all six platforms simultaneously. See their full social footprint — TikTok videos, YouTube channel, Instagram posts, X tweets, LinkedIn profile, and Reddit activity — in one unified view.

### Recipe 7: Reddit Listening
Monitor subreddits for mentions, track thread engagement, and identify trending discussions. Reddit data is notoriously hard to access at scale, and Stormy provides a clean interface for it.

### Recipe 8: Durable Jobs for Batch Processing
When you need more than 25 results or want to process email batches, use the durable jobs system. Start a job, get a job ID, and poll for completion. Jobs run asynchronously and can handle large volumes.

### Recipe 9: MCP Agent Workflows
Connect Stormy's MCP server to Claude Code, Cursor, Codex CLI, or ChatGPT. The agent discovers the 10 tools automatically and can chain them together — for example, discover influencers, look up their profiles, find their emails, and estimate sponsorship costs in a single agent session.

### Recipe 10: Error Handling and Retry Logic
Production-ready patterns for handling rate limits, partial results, and timeouts. Includes idempotency key support for safe retries on the durable jobs system.

## MCP Integration Guide

Stormy uses Streamable HTTP transport for its MCP server, which is the most widely compatible MCP transport. Here is how to connect it to popular AI agent platforms:

### Claude Code
```json
{
  "mcpServers": {
    "stormy": {
      "url": "https://mcp.stormy.ai/sse",
      "headers": {
        "Authorization": "Bearer YOUR_STORMY_API_KEY"
      }
    }
  }
}
```

### Cursor
Add the same configuration to your `.cursor/mcp.json` file. Cursor's AI features will automatically discover the 10 Stormy tools and make them available in chat and inline completions.

### Codex CLI
Codex CLI supports MCP servers through its configuration. Add the Stormy MCP endpoint and the agent can search social platforms, look up profiles, and find emails as part of its coding workflow.

### ChatGPT (Custom Connector)
ChatGPT's custom GPT feature supports MCP connectors. Configure the Stormy MCP endpoint and your GPT can access real-time social data during conversations.

### Any MCP Client
Because Stormy uses the standard MCP protocol with Streamable HTTP, it works with any MCP-compatible client. The agent calls `tools/list` to discover the 10 available tools, then calls `tools/call` with the appropriate parameters.

## REST API Quickstart

For developers who prefer direct API access, Stormy also provides a standard REST API. Here are quickstart examples:

### curl
```bash
# Search for AI influencers on TikTok
curl -H "Authorization: Bearer YOUR_API_KEY" \
  "https://api.stormy.ai/v1/search?platform=tiktok&query=AI%20influencer&limit=10"

# Look up a specific profile
curl -H "Authorization: Bearer YOUR_API_KEY" \
  "https://api.stormy.ai/v1/profile?platform=instagram&username=example_user"

# Find verified emails
curl -H "Authorization: Bearer YOUR_API_KEY" \
  "https://api.stormy.ai/v1/emails?platform=tiktok&username=creator_name"
```

### Python
```python
import requests

API_KEY = "your_stormy_api_key"
headers = {"Authorization": f"Bearer {API_KEY}"}

# Search for influencers
response = requests.get(
    "https://api.stormy.ai/v1/search",
    params={"platform": "youtube", "query": "machine learning", "limit": 5},
    headers=headers
)
results = response.json()

# Look up profile
profile = requests.get(
    "https://api.stormy.ai/v1/profile",
    params={"platform": "linkedin", "username": "some-profile"},
    headers=headers
).json()
```

### TypeScript
```typescript
const API_KEY = process.env.STORMY_API_KEY;

async function searchProfiles(platform: string, query: string) {
  const response = await fetch(
    `https://api.stormy.ai/v1/search?platform=${platform}&query=${encodeURIComponent(query)}&limit=10`,
    { headers: { Authorization: `Bearer ${API_KEY}` } }
  );
  return response.json();
}
```

## Stormy vs Competitors

The social data MCP server space is still young, but several alternatives exist. Here is how Stormy compares:

| Feature | Stormy Cookbook | Apify MCP Server | SocialData MCP | SocialFetch MCP |
|---------|----------------|-----------------|----------------|-----------------|
| **GitHub Stars** | 72 (launch day) | 2,296 | 7 | 1 |
| **Platforms** | 6 social networks | 3,000+ Actors (general) | Twitter, Instagram, YouTube, Telegram, Facebook | General social + web |
| **Social-First?** | Yes | No (general web scraping) | Yes | Partial |
| **MCP Tools** | 10 | Varies by Actor | Limited | Minimal |
| **Pricing** | Pay-per-result ($0.01–$0.15) | Per-Actor pricing | API key required | Unclear |
| **Open Source** | MIT license | Yes | Yes | Yes |
| **Verified Emails** | Yes | No | No | No |
| **Durable Jobs** | Yes | Via Actors | No | No |
| **Recipes/Guides** | 10 copy-pasteable recipes | Extensive docs | Minimal | Minimal |

**Apify MCP Server** is the dominant player with 2,296 stars, but it is a general web scraping platform, not social-media-specific. Its 3,000+ Actors cover everything from e-commerce to search engines, which means more complexity and a steeper learning curve for developers who only need social data.

**SocialData MCP Server** (7 stars) covers a similar set of platforms but is less mature, has a smaller community, and requires a SocialData.xyz API key. It lacks the durable jobs system and verified email features that make Stormy stand out.

**SocialFetch MCP** (1 star) and **MCP-rednote-assistant** (4 stars, Xiaohongshu-only) are either too early-stage or too niche to be direct competitors.

Stormy's differentiation is clear: it is the only open-source MCP server that is social-media-first, covers six major platforms, includes verified email finding, offers a transparent pay-per-result pricing model, and ships with ready-to-use recipes.

## Best Use Cases

### Influencer Discovery and Vetting
Marketing teams and agencies can use Stormy to discover influencers across platforms, vet them with profile data and engagement metrics, estimate sponsorship costs, and build outreach lists — all from a single API. The find_emails tool is particularly valuable here, as it eliminates the manual research step of finding contact information.

### Lead Generation for Creator Economy Platforms
Companies building tools for the creator economy can use Stormy to enrich their databases with social profile data, follower counts, and verified emails. The pay-per-result model means you only pay for successful lookups, making it economical for one-time enrichment projects.

### Competitive Intelligence
Monitor competitor social presence across all six platforms. Track follower growth, content strategy shifts, and engagement trends. The durable jobs system enables scheduled checks that run automatically.

### AI Agent Workflows
This is where Stormy truly shines. An AI agent using Claude Code or Cursor can discover influencers, look up their profiles, find their emails, and estimate sponsorship costs in a single session — chaining multiple MCP tools together without any custom integration code. The agent handles the orchestration; Stormy provides the data.

### Social Media Monitoring and Dashboards
Build dashboards that track brand mentions, industry trends, or competitor activity. The cache-first pricing makes repeated queries economical — most checks hit the $0.01 cached tier, so a dashboard checking 100 profiles daily costs about $1 per day.

## Getting Started

Getting started with Stormy Cookbook takes five minutes:

1. **Get an API key** — Sign up at stormy.ai and generate your API key
2. **Clone the cookbook** — `git clone https://github.com/OneInterface/stormy-cookbook`
3. **Pick a recipe** — Browse the 10 recipes in the `recipes/` directory and choose one that matches your use case
4. **Configure your client** — Set up the MCP server in Claude Code, Cursor, Codex CLI, or use the REST API directly
5. **Run it** — Execute the recipe with your API key

The recipes directory includes ready-to-run examples for each workflow. Each recipe has its own README with setup instructions, code samples, and expected output. The MCP server configuration is a single JSON block that you paste into your client's MCP settings.

## FAQ

### What is Stormy Cookbook?
Stormy Cookbook is an open-source (MIT) project that provides a unified REST API and MCP server for accessing social media data across TikTok, YouTube, Instagram, X (Twitter), LinkedIn, and Reddit. It ships with 10 copy-pasteable recipes for common social data workflows like influencer discovery, outreach list building, and competitor analysis.

### How does Stormy's pricing work?
Stormy uses a pay-per-result model: $0.01 for cached results, $0.05 for fresh profile lookups, $0.08 for fresh searches, and $0.15 for verified emails. You are only charged on successful results. A $50/month retainer is available with $25 in included usage credits.

### Which AI agents and tools can use Stormy's MCP server?
Any MCP-compatible client can use Stormy, including Claude Code, Cursor, Codex CLI, ChatGPT with custom connectors, and any custom MCP host. The server uses Streamable HTTP transport, the most widely compatible MCP transport protocol.

### How is Stormy different from the Apify MCP Server?
Stormy is social-media-first, covering six major platforms with 10 specialized MCP tools. Apify is a general web scraping platform with 3,000+ Actors but is not social-media-specific. Stormy also offers verified email finding, durable jobs, and transparent pay-per-result pricing that Apify does not match for social data use cases.

### Does Stormy support batch data collection?
Yes, Stormy includes a durable jobs system for batch operations. You can start a job for 25+ results, email batches, or long-running work using the start_social_job tool, then poll for completion with get_social_job. Jobs run asynchronously and support idempotency keys for safe retries.
