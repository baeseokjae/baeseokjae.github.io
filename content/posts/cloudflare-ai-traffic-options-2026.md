---
title: "Cloudflare AI Traffic Options 2026: New Routing and Caching for AI Workloads"
date: 2026-07-26T19:02:09+00:00
tags:
  - Cloudflare
  - AI Traffic
  - Bot Management
  - SEO
  - AI Crawlers
description: "Cloudflare's 2026 AI traffic options introduce a three-category bot taxonomy (Search, Agent, Training), BotBase visibility, Signed Agents, and a September 15 multi-purpose crawler default change."
draft: false
cover:
  image: "/images/cloudflare-ai-traffic-options-2026.png"
  alt: "Cloudflare AI Traffic Options 2026: New Routing and Caching for AI Workloads"
  relative: false
schema: "schema-cloudflare-ai-traffic-options-2026"
---

## Introduction — The Evolution of Cloudflare's AI Traffic Strategy

Cloudflare's 2026 AI traffic options introduce a fundamentally new approach to managing how artificial intelligence systems interact with websites. Instead of the binary "block all AI bots or allow everything" choice that defined earlier approaches, Cloudflare now offers a three-category taxonomy — Search, Agent, and Training — alongside new tools like BotBase for enterprise visibility, Signed Agents for cryptographic trust, and a critical September 15, 2026 default change that affects how multi-purpose crawlers like Googlebot, Applebot, and BingBot behave when Training is blocked. For website owners, publishers, and platform operators, understanding these options is no longer optional — it is essential for protecting content, preserving search visibility, and preparing for the agentic web era.

## The New Three-Category Taxonomy: Search, Agent, and Training

The centerpiece of Cloudflare's 2026 AI traffic strategy is a pragmatic three-category taxonomy that classifies bots by their behavior rather than a simplistic "AI or not" label. This shift matters because the same crawler can serve multiple purposes, and website owners need granular control over each use case.

### Search Crawlers — The Discovery Bargain

Search crawlers index content so it can appear in search engine results. Googlebot in its search capacity, BingBot, and other traditional search crawlers fall into this category. These bots provide a clear value exchange: they crawl your content in return for sending human visitors to your site through search results. Cloudflare's new taxonomy treats Search crawlers as the default allowed category because this mutual benefit is well-established. Website owners who block Search crawlers risk disappearing from search engine results entirely, making this the most cautious category to restrict.

### Agent Crawlers — User-Directed Bots

Agent crawlers operate on behalf of end users rather than bot operators. These are the emerging class of AI agents that browse the web to answer a specific user query, perform a task, or gather information in real time. Cloudflare's Signed Agents initiative, launched alongside the new taxonomy, provides cryptographic verification for these agents so website owners can distinguish legitimate user-directed bots from unauthorized scrapers. Agent crawlers represent a gray area in the content economy — they may drive less direct referral traffic than Search crawlers, but they serve real user intent. Cloudflare positions Agent traffic as a category that website owners can choose to allow, block, or meter on a case-by-case basis.

### Training Crawlers — Model Training Data Collection

Training crawlers collect data to train, fine-tune, or improve AI models. This category includes crawlers from companies like OpenAI, Anthropic, and Perplexity when they are operating in training mode. Unlike Search crawlers, Training crawlers offer no direct value exchange — they take content to improve a competitor's product without sending traffic back. Cloudflare's data shows that Training crawler activity has surged dramatically, and the new taxonomy gives website owners a clear, one-click option to block this category without affecting search visibility. This is the category most website owners will want to restrict, and Cloudflare has made it the simplest to configure.

## What Changes on September 15, 2026? The Multi-Purpose Crawler Default

The most time-sensitive change in Cloudflare's 2026 AI traffic options is the September 15, 2026 default behavior for multi-purpose crawlers. This date is a critical deadline that every Cloudflare customer should understand.

### How Googlebot, Applebot, and BingBot Are Affected

Googlebot, Applebot, and BingBot are multi-purpose crawlers — they operate in both Search and Training modes. Under Cloudflare's new rules, if a website owner blocks Training crawlers, these multi-purpose crawlers will be blocked entirely by default starting September 15, 2026. This means that blocking AI training data collection could also block Googlebot's search indexing capabilities, potentially causing a website to disappear from Google search results. This is not a bug — it is a deliberate design choice reflecting the reality that these crawlers cannot cleanly separate their search and training functions at the network level.

### Opting Out of the New Defaults

Website owners who want to block Training crawlers while preserving search indexing have options. Cloudflare provides configuration settings to explicitly allow multi-purpose crawlers in their Search capacity while blocking their Training function. This requires using the new content use level signals and the expanded robots.txt directives that Cloudflare has introduced. The key takeaway: do not simply toggle "Block AI Crawlers" without understanding the September 15 implications. Review your configuration before the deadline to avoid an accidental search deindexing.

## BotBase — Enterprise Visibility into Bot Behavior

For Enterprise Bot Management customers, Cloudflare introduced BotBase — a comprehensive visibility database showing all verified bots and their classified behaviors. BotBase represents a significant upgrade from the previous all-or-nothing bot visibility tools.

### Bot Classification Behaviors

BotBase classifies bots across multiple behavior categories beyond the core three: Search, Agent, Training, Transact (transactional bots like payment processors), Data Collection (analytics and monitoring), and more. Each verified bot in the database shows which behaviors it performs, giving enterprise customers unprecedented insight into exactly what each crawler does on their site. This visibility enables surgical blocking decisions — you can allow a bot's Search behavior while blocking its Training behavior, something that was impossible with earlier tools.

### Content Use Levels: Immediate, Reference, Full

Cloudflare also introduced three content use levels that extend the Content Signals specification in robots.txt:

- **Immediate**: The bot may access the content but must store nothing. This is the most restrictive level, suitable for content that should be seen but never retained.
- **Reference**: The bot may index and link back to the content (the default level). This mirrors traditional search engine behavior where content appears in results with attribution.
- **Full**: The bot may summarize, reproduce, or transform the content. This is the most permissive level, appropriate when you want AI systems to freely use your content.

These levels give website owners granular control over how their content is used after it is crawled, addressing a gap that existed in earlier bot management approaches.

## Signed Agents — Cryptographic Trust for the Agentic Web

Cloudflare's Signed Agents initiative introduces cryptographic verification for AI agent traffic. As AI agents become more prevalent — operating on behalf of users to browse the web, fill forms, and perform tasks — the ability to distinguish legitimate agents from malicious scrapers becomes critical.

Signed Agents work by extending Cloudflare's verified bot program with cryptographic signatures that prove an agent's identity and intent. Agents from participating platforms — including Browser Rendering, Browserbase, and Anchor Browser — carry these signatures, allowing website owners to make trust decisions based on verified identity rather than IP reputation or behavioral heuristics alone.

For website owners, Signed Agents offer a path forward that balances openness with protection. Instead of blocking all agent traffic out of fear, you can allow verified agents while still blocking unverified or suspicious traffic. This cryptographic trust layer is designed to scale with the growing agentic web, where Gartner predicts that by 2028, 33% of all internet interactions will involve AI agents.

## Making AI Search Smarter — The Research Program

Cloudflare launched a research program aimed at making AI search fundamentally more efficient and fair. The program addresses two interconnected problems: the massive waste in current crawling practices and the broken economic model for content creators.

### Cutting 50%+ Wasted Crawl Traffic

Cloudflare's research revealed that more than 50% of crawl traffic from good bots goes to re-fetching pages that have not changed. This staggering inefficiency means that half of all AI crawling bandwidth is wasted on redundant work. Cloudflare's network-level change detection — leveraging the fact that over 20% of the web sits behind Cloudflare — can signal to crawlers when content has actually changed, eliminating the need for constant re-fetching. For AI companies, this means lower crawling costs and fresher data. For website owners, it means less server load from unnecessary crawls.

### From Pay Per Crawl to Pay Per Use

Cloudflare is evolving the concept of Pay Per Crawl into Pay Per Use — a model where AI companies compensate content creators based on how their content is actually used rather than how many times it is crawled. Cloudflare is running experiments with major AI companies including Perplexity to test this model. The shift represents a potential new revenue stream for publishers who have seen traditional advertising and referral traffic decline. When Google shows an AI summary, users click a traditional search result link just 8% of the time — roughly half the click-through rate without a summary. Pay Per Use directly addresses this existential threat by tying compensation to consumption rather than clicks.

## Industry Context — AI Crawler Traffic Trends

Cloudflare's 2026 AI traffic options did not emerge in a vacuum. They are a response to dramatic shifts in how AI systems consume web content and how that consumption affects website owners.

### Googlebot Dominates AI Crawler Traffic

According to Cloudflare's Year in Review data, Googlebot crawled more than 200 times the share of pages reached by PerplexityBot. This dominance reflects Google's massive infrastructure advantage and its dual role as both a search engine and an AI training operation. The scale difference is so large that even small changes in Googlebot's behavior have outsized impacts on website server loads and bandwidth costs. Cloudflare's network, which handles over 81 million HTTP requests per second on average across 330+ cities in 125 countries, provides a unique vantage point for measuring these traffic patterns.

### The 8% Click-Through Problem with AI Summaries

The most alarming statistic for publishers is the 8% click-through rate when Google shows an AI summary. Traditional search results drive traffic to websites; AI summaries keep users on the search platform. This dynamic has created what Cloudflare CEO Matthew Prince calls an "existential threat" for content creators. Global Internet traffic grew 19% year-over-year in 2025, but the distribution of that traffic is shifting away from publisher websites and toward AI platforms. Cloudflare's AI traffic options are designed to give content creators more leverage in this evolving ecosystem.

## How to Configure Cloudflare AI Traffic Options (Step-by-Step)

Configuring Cloudflare's 2026 AI traffic options depends on your plan level. Here is how to get started.

### Free Tier Configuration

Free tier customers now have access to AI traffic controls that were previously reserved for paid plans. To configure:

1. Log in to the Cloudflare dashboard and navigate to Security > Bot Management.
2. Locate the new AI Traffic section, which shows the three-category taxonomy.
3. Toggle Training crawlers to "Block" to prevent AI model training on your content.
4. Review the multi-purpose crawler warning — if you block Training, confirm whether you want to also block Search functionality for Googlebot, Applebot, and BingBot.
5. If you want to block Training but preserve Search, use the explicit allowlist for multi-purpose crawlers in Search mode.
6. Save your configuration and verify with the new AI Traffic analytics dashboard.

### Enterprise Bot Management with BotBase

Enterprise customers get additional capabilities through BotBase:

1. Access BotBase from the Bot Management dashboard to see the full verified bot database.
2. Filter bots by behavior category (Search, Agent, Training, Transact, Data Collection).
3. For each bot, review its classified behaviors and content use level.
4. Create custom rules that allow or block specific behavior combinations.
5. Set content use level policies (Immediate, Reference, or Full) for different bot categories.
6. Monitor the AI Traffic analytics to see how your policies affect crawl volume and bot behavior.

## Best Practices for Website Owners in 2026

Based on Cloudflare's 2026 AI traffic options, here are the key recommendations for website owners:

1. **Act before September 15, 2026**: Review your AI traffic configuration before the multi-purpose crawler default change takes effect. If you block Training crawlers without an explicit Search allowlist for Googlebot, your search visibility could be affected.

2. **Use the three-category taxonomy**: Block Training crawlers by default, allow Search crawlers for visibility, and evaluate Agent crawlers on a case-by-case basis using Signed Agents verification.

3. **Leverage content use levels**: Set your content use policy to "Reference" as a baseline — this allows indexing and linking while preventing unauthorized reproduction. Upgrade to "Full" only for content you explicitly want AI systems to summarize and transform.

4. **Monitor BotBase analytics**: Even on the free tier, review the AI Traffic analytics to understand which bots are crawling your site and how your policies affect traffic patterns.

5. **Consider Pay Per Use opportunities**: If you are a publisher with high-quality content, explore Cloudflare's Pay Per Use experiments as a potential new revenue stream that does not depend on click-through rates.

6. **Implement Signed Agents policies**: As agent traffic grows, configure your site to allow verified Signed Agents while blocking unverified agent traffic. This future-proofs your bot management strategy.

## Conclusion — The Future of AI Traffic Management

Cloudflare's 2026 AI traffic options represent a maturation of the industry's approach to AI content consumption. The shift from binary "block AI or not" to a nuanced taxonomy of Search, Agent, and Training behaviors gives website owners the granular control they need to protect their content while preserving search visibility. The September 15, 2026 deadline for multi-purpose crawler defaults is a critical inflection point that every Cloudflare customer must address. Combined with BotBase visibility, Signed Agents for cryptographic trust, and the evolution toward Pay Per Use compensation, Cloudflare is positioning itself as a neutral broker between content creators and AI companies. For website owners, the message is clear: the era of passive bot management is over. Active, informed configuration of AI traffic options is now a core operational responsibility.

## FAQ

### What are Cloudflare's three new AI traffic categories in 2026?

Cloudflare introduced a three-category taxonomy for AI traffic: Search crawlers (indexing for search engines), Agent crawlers (user-directed bots), and Training crawlers (AI model training data collection). This replaces the previous binary "block AI or not" approach with granular, behavior-based controls.

### What happens on September 15, 2026 with Cloudflare AI traffic settings?

Starting September 15, 2026, multi-purpose crawlers like Googlebot, Applebot, and BingBot that combine Search and Training functions will be blocked entirely by default if a website owner has blocked Training crawlers. Website owners must explicitly configure an allowlist for Search functionality to preserve search indexing.

### How does Cloudflare BotBase work for enterprise customers?

BotBase is a comprehensive visibility database for Enterprise Bot Management customers that shows all verified bots and their classified behaviors across categories including Search, Agent, Training, Transact, and Data Collection. It enables surgical blocking decisions at the individual behavior level for each bot.

### What are Cloudflare content use levels in robots.txt?

Cloudflare introduced three content use levels: Immediate (bot may access but store nothing), Reference (bot may index and link back, the default), and Full (bot may summarize and reproduce content). These extend the Content Signals specification in robots.txt to give website owners control over how crawled content is used.

### How does Cloudflare's Pay Per Use model work for AI content?

Cloudflare is evolving Pay Per Crawl into Pay Per Use, where AI companies compensate content creators based on actual content usage rather than crawl frequency. The company is running experiments with AI companies like Perplexity to test this model, addressing the decline in traditional referral traffic caused by AI summaries.
