---
title: "Devnors Data Python SDK Guide 2026: Legal and Business Data API for AI Agents"
date: 2026-07-28T04:02:29+00:00
tags:
  - Devnors Data Python SDK
  - Devnors Data API
  - Devnors Data legal API
  - Devnors Data enterprise API
  - Devnors Data MCP
  - Chinese legal data API Python
  - AI Agent data API China
  - devnors-data pip package
  - Devnors Data pricing
  - Devnors Data documentation
  - POST /v1/data/query
  - Devnors Data academic research API
  - Devnors Data content API
  - Devnors Data cloud API
description: "Learn how to use the Devnors Data Python SDK to query legal cases, enterprise records, academic research, and content data via a single unified API endpoint for AI agents."
draft: false
cover:
  image: "/images/devnors-data-python-sdk-2026.png"
  alt: "Devnors Data Python SDK Guide 2026: Legal and Business Data API for AI Agents"
  relative: false
schema: "schema-devnors-data-python-sdk-2026"
---

The Devnors Data Python SDK (`devnors-data` on PyPI) is a lightweight, MIT-licensed client library that gives AI agents and Python developers a single unified gateway to five data domains — legal cases, enterprise records, content indexes, cloud services, and academic research — through one API key and one `POST /v1/data/query` endpoint. With 68,787 legal cases indexed, automatic retry with exponential backoff, async support, and pay-per-use pricing starting at ¥0.01 per call, it is the most practical data API for building China-focused AI agents in 2026.

## What Is Devnors Data?

Devnors Data is a unified data API platform purpose-built for AI agents and developers who need structured, traceable data from Chinese sources. Unlike general-purpose data APIs that require separate integrations for each data type, Devnors Data consolidates five distinct data domains behind a single authentication scheme and a single query endpoint.

The platform launched with a legal data domain and rapidly expanded between July 22 and July 27, 2026, adding enterprise data, content indexes, cloud services, and academic research in a single week. This aggressive expansion reflects a clear product vision: become the default data layer for AI agents operating in the Chinese market.

### Data Domains Covered

| Domain | Launch Date | Key Endpoints | Example Use Case |
|--------|-------------|---------------|------------------|
| Legal | Initial | Legal cases, law articles, law catalog | Retrieve judgment documents for legal research |
| Enterprise | July 22-23, 2026 | Company detail, annual report, tax invoice, shixin/zhixing check | Verify company registration status |
| Content | July 22, 2026 | Keyword index, WeChat index, hot rank | Track trending topics on Chinese social media |
| Cloud | July 22, 2026 | Express tracking | Track logistics shipments |
| Academic Research | July 27, 2026 | Paper search, patent search, journal search, scholar search | Find Chinese academic papers by keyword |

Each domain returns structured JSON responses with official-source traceability, making the data suitable for automated decision-making in AI agent workflows.

## Getting Started with the Python SDK

The Devnors Data Python SDK is designed as a thin wrapper over the unified API gateway. It handles authentication, request serialization, response parsing, retry logic, and pagination so you can focus on building your application.

### Installation

Install the package from PyPI with a single command:

```bash
pip install devnors-data
```

The package requires Python 3.9 or later and depends on `httpx>=0.24` for HTTP transport. Version 0.1.1 is the current stable release as of July 2026.

### API Key Setup

1. Sign up at [data.devnors.com](https://data.devnors.com) to receive your free trial quota.
2. Navigate to the developer console to generate an API key.
3. Set the key as an environment variable:

```bash
export DEVNORS_DATA_API_KEY="your-api-key-here"
```

The SDK reads `DEVNORS_DATA_API_KEY` from the environment by default, which is the recommended approach for production deployments. You can also pass the key directly to the client constructor.

### Quick Start Example

Here is the minimal code to query legal cases:

```python
from devnors_data import DevnorsData

client = DevnorsData()  # reads DEVNORS_DATA_API_KEY from env

# Query legal cases about contract disputes
response = client.legal_cases(
    query="contract dispute",
    page=1,
    page_size=10
)

for case in response.data:
    print(f"{case.case_id}: {case.title}")
```

The client automatically handles authentication headers, request formatting, and response deserialization. The same pattern works for every data domain.

## Core API Usage

### The Unified /v1/data/query Endpoint

Every SDK method ultimately sends a `POST` request to `https://data.devnors.com/v1/data/query`. The request body specifies the data domain, query parameters, and pagination options. The SDK abstracts this into domain-specific methods, but you can also call the raw endpoint directly if you need custom behavior.

The unified design means you only need one API key, one base URL, and one authentication mechanism for all five data domains. This is especially valuable for AI agents that need to switch between data types in a single workflow without managing multiple API integrations.

### Domain-Specific Methods

The SDK provides dedicated methods for each data domain:

```python
# Legal domain
cases = client.legal_cases(query="知识产权", page=1, page_size=20)
laws = client.legal_laws(query="公司法", page=1, page_size=10)
catalog = client.legal_law_catalog()

# Enterprise domain
company = client.enterprise_company_detail(tax_id="91440101MA5...")
annual = client.enterprise_annual_report(tax_id="91440101MA5...")
invoice = client.enterprise_tax_invoice(invoice_code="...")
shixin = client.enterprise_shixin_check(company_name="...")
zhixing = client.enterprise_zhixing_check(company_name="...")

# Content domain
keyword_index = client.content_keyword_index(keyword="AI", date="2026-07-28")
wechat_index = client.content_wechat_index(keyword="大模型", date="2026-07-28")
hot_rank = client.content_hot_rank(platform="douyin", date="2026-07-28")

# Cloud services
tracking = client.cloud_express_tracking(express_no="SF1234567890")

# Academic research
papers = client.research_paper_search(query="machine learning", page=1, page_size=10)
patents = client.research_patent_search(query="人工智能", page=1, page_size=10)
journals = client.research_journal_search(query="自然语言处理", page=1, page_size=10)
scholars = client.research_scholar_search(name="李飞飞", page=1, page_size=10)
```

Each method returns a structured response object with typed fields, making it easy to integrate with Python type checkers and IDE autocompletion.

### Async Client

For AI agents that handle multiple concurrent queries, the SDK provides an async client:

```python
from devnors_data import AsyncDevnorsData
import asyncio

async def query_multiple_domains():
    client = AsyncDevnorsData()

    # Run queries concurrently
    cases, company_data, papers = await asyncio.gather(
        client.legal_cases(query="patent infringement", page=1, page_size=5),
        client.enterprise_company_detail(tax_id="91440101MA5..."),
        client.research_paper_search(query="AI regulation", page=1, page_size=5)
    )

    print(f"Found {len(cases.data)} cases")
    print(f"Company: {company_data.name}")
    print(f"Found {len(papers.data)} papers")

asyncio.run(query_multiple_domains())
```

The async client uses `httpx.AsyncClient` under the hood and supports the same automatic retry and error handling as the synchronous client.

### Pagination with paginate()

For queries that return large result sets, the SDK provides a `paginate()` helper that automatically iterates through pages:

```python
# Iterate through all pages of legal cases
for page in client.paginate("legal_cases", query="商标侵权", page_size=50):
    for case in page.data:
        print(f"{case.case_id}: {case.title}")
    print(f"--- Page {page.page} of {page.total_pages} ---")
```

The `paginate()` method handles page tracking, respects rate limits between requests, and stops when all pages are consumed. This is essential for AI agents that need to process complete datasets rather than just the first page of results.

## Data Domains Deep Dive

### Legal Data

The legal domain is the original and most mature data domain on Devnors Data. As of July 2026, the platform has indexed 68,787 legal judgment documents with continuous updates every 30 days. The legal API supports three endpoints:

- **Legal Cases**: Search judgment documents by keyword, court, judge, or legal basis. Returns case ID, title, court name, judgment date, case type, and full judgment text.
- **Law Articles**: Query specific law articles by law name and article number. Returns the full text of the article with revision history.
- **Law Catalog**: Retrieve the complete catalog of Chinese laws and regulations organized by legal domain.

This data is particularly valuable for legal tech AI agents, compliance automation tools, and legal research platforms targeting the Chinese market.

### Enterprise Data

Launched July 22-23, 2026, the enterprise data domain provides access to Chinese company registration and compliance information:

- **Company Detail**: Look up a company by its unified social credit code (tax ID). Returns company name, registration status, legal representative, registered capital, business scope, and registration date.
- **Annual Report**: Retrieve the latest annual report filing for a company, including financial highlights and employee count.
- **Tax Invoice Verification**: Verify the authenticity of Chinese tax invoices by invoice code and number.
- **Shixin Check**: Check if a company or individual is on the失信被执行人 (dishonesty blacklist) maintained by Chinese courts.
- **Zhixing Check**: Query enforcement cases against a company, including case status and enforcement amount.

Enterprise data is priced at ¥0.2 per call (10,000 tokens) for company detail, with the annual report endpoint at ¥1 per call (50,000 tokens) being the most expensive endpoint on the platform.

### Content Data

The content domain, launched July 22, 2026, provides access to Chinese social media and content platform metrics:

- **Keyword Index**: Track search volume trends for keywords across Chinese search engines.
- **WeChat Index**: Monitor keyword popularity on WeChat's official accounts and Moments.
- **Hot Rank**: Retrieve trending topic rankings from platforms like Douyin (TikTok China), Weibo, and Baidu.

This domain is essential for AI agents performing social media monitoring, trend analysis, and content strategy in the Chinese market.

### Cloud Services

The cloud domain currently offers one endpoint:

- **Express Tracking**: Track logistics shipments by tracking number. Supports major Chinese carriers including SF Express, YTO, ZTO, Yunda, and China Post.

This is a practical addition for AI agents handling e-commerce logistics, supply chain monitoring, or customer service automation.

### Academic Research

The newest domain, launched July 27, 2026, provides access to Chinese academic research databases:

- **Paper Search**: Search Chinese academic papers by keyword, author, or institution. Returns title, authors, abstract, publication date, and citation count.
- **Patent Search**: Query Chinese patents by keyword, patent number, or applicant.
- **Journal Search**: Search for Chinese academic journals by name or ISSN.
- **Scholar Search**: Find Chinese researchers by name or institution, with their publication history.

At ¥0.01 per call (500 tokens), academic research is the most affordable domain, making it ideal for high-volume research automation.

## Error Handling and Retry

### Automatic Retry with Exponential Backoff

The SDK automatically retries failed requests on HTTP 429 (rate limited) and 5xx (server error) status codes. The retry strategy uses exponential backoff with jitter to avoid thundering herd problems:

```python
# Default retry behavior — automatic
response = client.legal_cases(query="contract dispute")

# The SDK retries on 429 and 5xx with:
# - Initial delay: 1 second
# - Backoff factor: 2x
# - Maximum retries: 3
# - Jitter: ±0.5 seconds
```

You can configure retry behavior when creating the client:

```python
from devnors_data import DevnorsData

client = DevnorsData(
    max_retries=5,
    retry_delay=2.0,
    retry_backoff=3.0
)
```

### Structured Error Types

The SDK raises typed exceptions for different error conditions:

| Error Type | HTTP Status | Description |
|-----------|-------------|-------------|
| `DevnorsDataError` | Various | Base exception for all SDK errors |
| `AuthenticationError` | 401 | Invalid or missing API key |
| `InsufficientBalanceError` | 402 | Account balance too low for the request |
| `RateLimitError` | 429 | Too many requests, retry after backoff |
| `ServerError` | 5xx | Devnors Data server error, will be retried |

This structured error handling allows AI agents to implement domain-specific fallback logic:

```python
from devnors_data import DevnorsData, InsufficientBalanceError

client = DevnorsData()

try:
    response = client.enterprise_company_detail(tax_id="91440101MA5...")
except InsufficientBalanceError:
    print("Insufficient balance — notify admin to top up")
    # Switch to cached data or fallback source
except AuthenticationError:
    print("API key invalid — check DEVNORS_DATA_API_KEY")
```

### Billing Errors

The 402 `InsufficientBalanceError` is unique to Devnors Data's pay-per-use model. When your account balance drops below the cost of a request, the API returns this error instead of silently failing or returning partial data. The SDK surfaces this as a clear exception so your AI agent can take appropriate action — notify an administrator, switch to a cached data source, or queue the request for later retry.

### Rate Limiting

The 429 `RateLimitError` includes a `retry_after` field indicating how long to wait before retrying. The SDK's automatic retry mechanism respects this field, but you can also handle it manually for fine-grained control:

```python
from devnors_data import DevnorsData, RateLimitError
import time

client = DevnorsData(max_retries=0)  # Disable auto-retry

try:
    response = client.legal_cases(query="patent")
except RateLimitError as e:
    wait_time = e.retry_after  # seconds
    print(f"Rate limited, waiting {wait_time}s...")
    time.sleep(wait_time)
    response = client.legal_cases(query="patent")
```

## Pricing and Billing

Devnors Data uses a transparent pay-per-use pricing model with no monthly fees, no prepayment requirements, and automatic refunds for failed calls.

### Token-Based Pricing

Each API call consumes a fixed number of tokens based on the endpoint. Tokens are purchased in bundles, with 1 CNY purchasing 50,000 tokens. The actual cost per call varies by data domain:

| Endpoint | Tokens per Call | Cost per Call (CNY) | Cache Hit Cost |
|----------|----------------|---------------------|----------------|
| Paper/Patent/Journal/Scholar Search | 500 | ¥0.01 | — |
| Legal Cases | 5,000 | ¥0.10 | ¥0.05 |
| Law Articles | 5,000 | ¥0.10 | ¥0.05 |
| Law Catalog | 5,000 | ¥0.10 | ¥0.05 |
| Keyword Index | 5,000 | ¥0.10 | ¥0.05 |
| WeChat Index | 5,000 | ¥0.10 | ¥0.05 |
| Hot Rank | 5,000 | ¥0.10 | ¥0.05 |
| Express Tracking | 5,000 | ¥0.10 | ¥0.05 |
| Company Detail | 10,000 | ¥0.20 | ¥0.10 |
| Shixin/Zhixing Check | 10,000 | ¥0.20 | ¥0.10 |
| Tax Invoice Verification | 10,000 | ¥0.20 | ¥0.10 |
| Annual Report | 50,000 | ¥1.00 | ¥0.50 |

### Cache Hit Pricing

For endpoints that support cache hits, the cost is reduced by 50% when the same query has been made recently and the result is served from cache. This makes repeated queries — common in AI agent workflows that poll for updates — significantly more affordable.

### Free Trial Quota

New accounts receive a free trial quota upon registration. This allows you to test all five data domains before committing to a paid plan. The trial quota is typically sufficient for several hundred legal case queries or thousands of academic research queries.

## MCP Server Integration

Beyond the Python SDK, Devnors Data also provides an MCP (Model Context Protocol) server that enables natural language data queries from AI assistants like Claude Desktop, Cursor, WorkBuddy, and Codex.

### Remote HTTP Mode

In remote HTTP mode, the MCP server connects to Devnors Data's API gateway and exposes each data domain as a natural language tool:

```
# Claude Desktop configuration
{
  "mcpServers": {
    "devnors-data": {
      "url": "https://data.devnors.com/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_API_KEY"
      }
    }
  }
}
```

Once configured, you can ask your AI assistant questions like "Find recent patent infringement cases in Shanghai" or "What is the current WeChat index for large language models?" and the assistant will query Devnors Data automatically.

### Local stdio Mode

For development environments, the MCP server can run locally via stdio:

```bash
npx @devnors/mcp-server --api-key YOUR_API_KEY
```

This mode is useful for local testing and integration with development tools like Cursor and Codex.

### Natural Language Query Examples

The MCP integration transforms complex API queries into simple natural language requests:

- "Search for Chinese academic papers about reinforcement learning published in 2025"
- "Check the shixin status of Beijing Tech Corp"
- "What are the trending topics on Douyin today?"
- "Find the full text of Article 20 of the Chinese Civil Code"
- "Track express number SF1234567890"

This makes Devnors Data accessible to non-technical users and accelerates development by eliminating the need to read API documentation for every query.

## Best Practices for AI Agents

### API Key Management

Store your API key in an environment variable (`DEVNORS_DATA_API_KEY`) rather than hardcoding it in source code. For AI agent deployments, use a secrets manager or encrypted environment file. The SDK's default behavior of reading from the environment encourages this best practice.

### Pagination for Large Result Sets

Always use the `paginate()` helper when you need complete results rather than a single page. The helper automatically respects rate limits and handles pagination state. For AI agents that need real-time responses, consider limiting page size and using the first page as a preview, then fetching additional pages in the background.

### Retry Configuration

The default retry settings (3 retries, 1-second initial delay, 2x backoff) work well for most use cases. For latency-sensitive AI agents, reduce `max_retries` to 1 or 2. For batch processing jobs where throughput matters more than latency, increase `max_retries` to 5 and set a longer initial delay.

### Combining Multiple Data Domains in One Workflow

The unified API design makes it straightforward to combine data from multiple domains in a single AI agent workflow:

```python
from devnors_data import DevnorsData

client = DevnorsData()

# 1. Research a company
company = client.enterprise_company_detail(tax_id="91440101MA5...")

# 2. Check for legal issues
cases = client.legal_cases(query=company.name, page=1, page_size=5)

# 3. Check dishonesty blacklist
shixin = client.enterprise_shixin_check(company_name=company.name)

# 4. Find recent academic papers mentioning the company
papers = client.research_paper_search(query=company.name, page=1, page_size=5)

# 5. Compile a comprehensive report
report = {
    "company_name": company.name,
    "registration_status": company.status,
    "legal_issues": [c.title for c in cases.data],
    "blacklisted": len(shixin.data) > 0,
    "recent_mentions": [p.title for p in papers.data]
}
```

This pattern — querying legal, enterprise, and research data about a single entity — is a common AI agent workflow for due diligence, compliance checks, and market research.

## Conclusion

### Why Devnors Data Is Ideal for China-Focused AI Agents

Devnors Data solves a fundamental problem for AI agents operating in the Chinese market: accessing structured, traceable data from Chinese sources through a single integration. The Python SDK's design philosophy — thin wrapper over a unified gateway, automatic retry, pagination, async support — aligns perfectly with the needs of AI agent developers who want to minimize integration overhead and maximize reliability.

The platform's rapid expansion from a legal-only API to five data domains in one week demonstrates a commitment to becoming the comprehensive data layer for China-focused AI applications. With 68,787 legal cases indexed, enterprise registration data, social media trend tracking, logistics tracking, and academic research all available through one API key and one endpoint, Devnors Data significantly reduces the integration burden for AI agent developers.

### Future Roadmap and Expanding Data Coverage

Based on the platform's release cadence — five domains launched in a single week — we can expect continued rapid expansion. The changelog shows weekly feature releases, suggesting new data domains and endpoints are in active development. Potential future additions could include real-time financial data, government procurement records, real estate transaction data, and additional social media platforms.

For AI agent developers building for the Chinese market in 2026, the Devnors Data Python SDK is not just a convenience — it is rapidly becoming an essential tool in the stack.

## Frequently Asked Questions

### What is the Devnors Data Python SDK and what does it do?

The Devnors Data Python SDK (`devnors-data` on PyPI) is a client library that provides a unified interface to the Devnors Data API, which covers five data domains: legal cases, enterprise records, content indexes, cloud services, and academic research. It handles authentication, request serialization, automatic retry with exponential backoff, and pagination so developers can query Chinese data sources with minimal code.

### How do I install the Devnors Data Python SDK?

Install it with `pip install devnors-data`. The package requires Python 3.9+ and depends on `httpx>=0.24`. After installation, set your API key as the `DEVNORS_DATA_API_KEY` environment variable and create a `DevnorsData()` client instance to start querying data.

### What data domains does Devnors Data cover?

Devnors Data covers five domains as of July 2026: legal (68,787 indexed cases, law articles, law catalog), enterprise (company detail, annual reports, tax invoice verification, shixin/zhixing checks), content (keyword index, WeChat index, hot rank), cloud services (express tracking), and academic research (papers, patents, journals, scholars).

### How much does the Devnors Data API cost?

Devnors Data uses pay-per-use pricing with no monthly fees. Academic research queries cost ¥0.01 per call (500 tokens), legal and content queries cost ¥0.10 per call (5,000 tokens), enterprise company detail costs ¥0.20 per call (10,000 tokens), and annual reports cost ¥1.00 per call (50,000 tokens). Cache hits reduce costs by 50%, and failed calls are automatically refunded.

### Can I use Devnors Data with AI assistants like Claude Desktop?

Yes. Devnors Data provides an MCP (Model Context Protocol) server that integrates with Claude Desktop, Cursor, WorkBuddy, and Codex. You configure it with your API key, then query any data domain using natural language — for example, "Find recent patent infringement cases in Shanghai" or "What is the current WeChat index for large language models?"
