---
title: "Salesforce Agentic Work Units (AWU) Explained for Developers"
date: 2026-06-02T00:04:47+00:00
tags: ["Salesforce", "Agentforce", "AI Agents", "AWU", "Developer Guide"]
description: "Salesforce AWU가 무엇인지, 어떻게 청구되며, 비용을 최적화하는 방법을 개발자 관점에서 완전히 설명합니다."
draft: false
cover:
  image: "/images/salesforce-agentic-work-units-guide-2026.png"
  alt: "Salesforce Agentic Work Units (AWU) Explained for Developers"
  relative: false
schema: "schema-salesforce-agentic-work-units-guide-2026"
---

Salesforce의 AWU(Agentic Work Unit)는 AI 에이전트가 완료한 **하나의 개별 작업**을 의미합니다. 토큰이 AI가 얼마나 많이 "말했는지"를 측정한다면, AWU는 AI가 실제로 얼마나 많은 **작업을 완료했는지**를 측정합니다. 개발자에게 AWU는 Agentforce 비용을 이해하고 예측하며 최적화하는 핵심 단위입니다.

## What Are Salesforce Agentic Work Units (AWU)?

An Agentic Work Unit is a discrete, measurable action completed by a Salesforce AI agent — one unit of work executed on behalf of a customer or employee, tracked independently of how many tokens that work consumed. Salesforce CEO Marc Benioff introduced the metric during the Q4 FY2026 earnings call on February 25, 2026, positioning AWUs as the industry-standard way to quantify AI agent productivity rather than raw token volume. As of Q1 FY2027, the platform has processed over 19 trillion AI tokens translating to 3.8 billion total AWUs, with 1.6 billion AWUs generated in a single quarter — a 111% quarter-over-quarter growth. The key insight for developers: AWU is **elastic**. Salesforce's stated goal is to deliver more AWUs from fewer tokens as model efficiency improves, meaning the same budget should fund progressively more agent work over time. Whether that promise holds depends directly on how well you architect your agents.

Understanding the precise boundary of what constitutes "one AWU" is the foundation of every cost and optimization decision you'll make on the platform. Each standard action in Agentforce corresponds to one AWU and consumes up to 10,000 tokens (~8,000 words of combined prompt + response). If your action exceeds that ceiling, Salesforce counts it as multiple actions — silently doubling or tripling your spend. Voice actions cost 1.5× more than standard actions.

## AWU vs. Tokens: Why the Distinction Matters for Developers

The AWU/token distinction represents a fundamental shift in how enterprises will budget and evaluate AI systems in 2026 and beyond. Tokens are a **resource consumption** metric — they measure LLM compute used. AWUs are an **outcome** metric — they measure work items completed. Salesforce's inference efficiency ratio (AWUs per token) is the number that tells you whether your agent implementation is getting more done with less. In practical terms: two Agentforce deployments spending the same budget in tokens could produce wildly different AWU counts depending on prompt design, retrieval efficiency, and action batching strategy.

For developers, this distinction shapes architectural decisions from the ground up. A customer service agent that resolves a billing dispute in one clean action (one AWU, 4,000 tokens) is more efficient than one that pings the LLM three times for clarification before completing the same task (three AWUs, 12,000+ tokens). The difference isn't just cost — it's the efficiency ratio that indicates whether your agent is genuinely automating work or just performing LLM theater. The platform has demonstrated that Service Agents grew 66% quarter-over-quarter to reach 232M AWUs in Q1, while Employee Agents experienced a 148% QoQ increase, signaling that real enterprise workloads — not demos — are driving these numbers.

Critical nuance: AWU measures **execution**, not accuracy. A triggered workflow that fails to resolve the customer's issue still counts as an AWU. This is a key criticism developers must internalize — you can rack up millions of AWUs while delivering zero business value. Always pair AWU tracking with outcome metrics (resolution rate, deflection rate, escalation rate) to avoid optimizing for the wrong signal.

## What Triggers an AWU? A Technical Breakdown of Agent Actions

An AWU is triggered every time an Agentforce agent executes a discrete action. Understanding exactly which platform operations count — and which do not — determines whether your architecture is cost-efficient or accidentally expensive. Standard Agentforce actions that trigger an AWU include: invoking an Apex action, executing a Flow, calling an external API via an action, running a query against Salesforce data using SOQL, and generating a response to a user turn. Non-action operations such as routing decisions, topic classification, and guard evaluations may or may not consume AWUs depending on their implementation — always test in a sandbox and monitor via Event Monitoring before deploying to production. Each AWU-triggering action is bounded by the 10,000-token ceiling; exceed it, and Salesforce counts the single action as multiple AWUs. For typical enterprise conversations handling moderate data volumes, most actions stay well under this ceiling — but document-heavy workflows (order history retrieval, full case thread summarization, or large knowledge-article injection) routinely breach it without developer awareness. Real-world benchmarks from production deployments show that 8-15% of actions in data-rich service workflows exceed the ceiling, silently multiplying AWU spend by 30-50% relative to developer expectations.

### Voice Actions vs. Standard Actions

Voice actions count as 1.5 AWUs (30 Flex Credits) compared to 1.0 AWU (20 Flex Credits) for standard actions. This reflects the additional compute for speech-to-text, turn management, and real-time response latency requirements. If you're building voice-enabled service agents, budget accordingly: a 10-action voice conversation costs $1.50 versus $1.00 for the same workflow in text. For high-volume voice deployments, that 50% premium can represent hundreds of thousands of dollars at scale.

### The 10,000-Token Action Boundary

Each standard action includes processing up to 10,000 tokens (~8,000 words) before a multiplier activates. Exceeding this boundary causes Salesforce to count the action as multiple actions. A single action that processes 22,000 tokens counts as three AWUs — and you may never see it happen unless you have observability tooling in place. This boundary is the single most important technical constraint developers need to design against.

## Agentforce Pricing Models: Flex Credits, Per-Conversation, and Per-User

Salesforce has shipped three distinct pricing models for Agentforce in roughly 18 months, reflecting the rapid iteration required when an entirely new billing paradigm hits market. As of mid-2026, the three active options are: **Flex Credits** ($500 per 100,000 credits; standard action = 20 credits/$0.10; voice = 30 credits/$0.15), **Per-Conversation** ($2 flat per conversation regardless of action count), and **Per-User Licensing** ($125/user/month for embedded agent access). Each model optimizes for a different usage pattern, and choosing the wrong one is the fastest way to overspend on Agentforce.

**Flex Credits** are optimal when your conversations are short (under 20 actions) and variable in volume. A 5-action conversation costs $0.50 — well below the $2 per-conversation flat rate. Once conversations average more than 20 actions, the flat rate becomes cheaper per interaction. The crossover math is simple: 20 actions × $0.10 = $2.00. Any conversation averaging more than 20 actions tips toward per-conversation pricing.

**Per-Conversation pricing** ($2 flat) wins when your agents handle complex, multi-step workflows that predictably exceed 20 actions. Enterprise support scenarios, multi-system orchestration, and document-processing workflows often fall in this category. If your average conversation involves 30-40 actions, flat pricing saves 33-50% versus Flex Credits.

**Per-User licensing** ($125/user/month) makes sense for Copilot-style deployments where named employees use agents daily. A user who triggers 10 conversations per day pays an effective rate of $0.42/conversation at $125/month — far below both alternatives. The math requires ~63+ active conversations per month to beat $2/conversation pricing, making this model viable only for heavy daily users.

### Choosing Your Model: A Decision Framework

| Usage Pattern | Recommended Model | Why |
|---|---|---|
| <20 actions/conversation, variable volume | Flex Credits | Pay only for what you use |
| >20 actions/conversation, consistent volume | Per-Conversation ($2) | Cap cost per interaction |
| Named users, 3+ conversations/day | Per-User ($125/month) | Amortizes over high frequency |
| Mixed voice + text workflows | Flex Credits | Voice/text action split control |
| Testing and development | Flex Credits | No monthly commitment |

## The 10,000-Token Ceiling: How Prompt Design Affects Your AWU Spend

The 10,000-token action ceiling is the most underappreciated cost driver in Agentforce development. Developers who migrate from direct LLM API usage (where you pay per token) often don't realize that Agentforce bills by action with an implicit token cap — and that crossing the cap multiplies the AWU count, not just the cost. Poor prompt design that routinely pushes actions past 10,000 tokens can double or triple your AWU spend on identical workloads.

The primary culprits are: **context window stuffing** (injecting full records, email threads, or documents into every action without filtering), **verbose system prompts** (multi-page instruction sets that repeat with every action), **redundant retrieval** (fetching the same data multiple times within a single conversation), and **unconstrained response generation** (allowing agents to write multi-page summaries when a paragraph would suffice). Each of these is a controllable variable — and each one directly determines whether your agents stay under the 10,000-token ceiling.

### Concrete Techniques to Stay Under the Ceiling

Measure first. Use Agentforce Observability to log token consumption per action before you optimize. Identify the actions most frequently approaching or exceeding 10,000 tokens — those are your highest-ROI optimization targets.

**Retrieval filtering**: Instead of injecting a full case record (potentially 3,000-5,000 tokens), retrieve only the fields the agent actually needs for the current action. A billing dispute action needs account balance and recent transactions — not the full 24-month case history. Field-level retrieval can reduce per-action token consumption by 60-80% in data-rich scenarios.

**System prompt compression**: Audit your system prompt for instructions that apply to edge cases your agent rarely encounters. Move conditional instructions to context-dependent injection rather than always-on system prompt inclusion. A 2,000-token system prompt that's actually needed for 20% of interactions inflates token counts across 100% of actions.

**Response length constraints**: Add explicit output length constraints to action definitions. An action generating a case summary can produce an 800-word essay or a 150-word brief — the LLM will default to longer unless constrained. Constraining output length is the fastest optimization available.

## Monitoring AWU Usage with Agentforce Observability Tools

Agentforce Observability is Salesforce's built-in tooling for tracking agent execution, AWU consumption, and performance metrics. Without active observability, you're flying blind on cost — the 10,000-token ceiling violations and unexpected AWU spikes that inflate your bill happen silently unless you instrument for them. The platform's observability suite includes Event Monitoring (logs every agent action with token counts and AWU attribution), Agentforce Analytics dashboards (aggregate AWU trends by agent type, topic, and time), and custom SOQL queries against AgentWorkItems and related objects for programmatic cost attribution. Teams that implement AWU observability within the first two weeks of an Agentforce deployment consistently identify 20-40% reduction opportunities before they ever hit production at scale. The most common findings: single actions silently crossing the 10,000-token ceiling (often due to unconstrained knowledge article injection), topic classification triggering unnecessary LLM reasoning calls on deterministically classifiable intents, and retry logic generating duplicate AWUs when an action errors. None of these are visible without instrumentation in place. Start with Event Monitoring before you start optimizing — you can't improve what you can't measure.

### Setting Up AWU Monitoring in 4 Steps

**Step 1 — Enable Event Monitoring**: In Setup, navigate to Event Monitoring → Agentforce Events. Enable `AgentWorkItem` events and `AgentAction` events. These populate the EventLogFile object with per-action data including token counts and AWU attribution.

**Step 2 — Build an AWU dashboard**: Use CRM Analytics (formerly Tableau CRM) to create a dashboard tracking daily/weekly AWU consumption by agent type, topic, and conversation length distribution. The conversation length distribution is the most actionable view — it shows you what percentage of conversations fall above the 20-action per-conversation pricing crossover.

**Step 3 — Set AWU budget alerts**: Use Platform Events to trigger alerts when daily AWU consumption crosses thresholds. A simple Apex trigger on EventLogFile can calculate running AWU totals and fire a notification when you hit 80% of your daily budget ceiling.

**Step 4 — Attribute AWU to business outcomes**: Join AWU event data to Case, Order, or custom object resolution data. An AWU without an outcome attribution is just a cost; an AWU linked to a resolved case is a measurable ROI unit.

## Developer Best Practices for AWU Optimization

Optimizing AWU consumption is not a post-launch concern — it's an architectural discipline that should be embedded from the first design review. The developers who achieve the best inference efficiency ratios share a common pattern: they treat every LLM call as an expensive resource and design agent workflows to minimize the number of calls required to complete each task.

The highest-impact optimization available to most teams is **action consolidation**: replacing three sequential single-purpose actions with one well-designed compound action. Instead of an agent querying account status (AWU 1), then querying open cases (AWU 2), then generating a response (AWU 3), a single Apex action that fetches both data sets and structures the prompt for the LLM in one operation reduces the interaction to one AWU. This pattern alone can reduce per-conversation AWU spend by 50-66% in data-retrieval-heavy workflows.

**Async processing for non-real-time work**: Not every agent action needs to be synchronous. Document summarization, report generation, and batch data enrichment can be offloaded to asynchronous Apex jobs or Platform Events. The agent triggers the job (one AWU) and returns a confirmation; the batch processing runs outside the agent conversation. This pattern dramatically reduces conversational AWU counts for workflows that previously blocked on long-running operations.

**Deterministic pre-processing**: Move classification, routing, and validation logic that doesn't require LLM reasoning into deterministic Apex code. If your agent classifies 15 intent categories and 12 of them have clear keyword signals, a 20-line Apex method handles those without touching the LLM — and without triggering an AWU. Reserve LLM calls for genuinely ambiguous, language-understanding tasks.

**Caching retrieved context**: Within a conversation, cache retrieved records and context in a custom platform object or a Named Credential-backed cache. If multiple actions in a conversation need the same account record, retrieve it once and reference the cached version. Repeated retrieval is a common source of redundant token consumption.

## Building Efficient Agentforce Apex Actions to Reduce AWU Consumption

Apex actions are the primary extension point for Agentforce, and their design has the most direct impact on AWU efficiency. A well-designed Apex action fetches exactly the data needed, formats it optimally for LLM consumption, and returns a structured response that minimizes the LLM's reasoning work. A poorly designed Apex action floods the LLM with raw data, forces multi-step reasoning that could be pre-computed, and generates responses that exceed the 10,000-token ceiling.

The core design principle: **Apex should think so the LLM doesn't have to**. Every data transformation, aggregation, and conditional logic that can be computed deterministically in Apex should be. The LLM's job is language understanding, generation, and handling genuine ambiguity — not sorting lists, calculating sums, or formatting dates.

### Apex Action Design Checklist

**Data selection**: Query only the fields the LLM will use. If your action retrieves an Order record, list explicitly which fields are LLM-relevant. A `SELECT *` on a complex object can easily add 1,000-3,000 tokens per action.

**Structured output formatting**: Return data as concise key-value pairs or structured JSON rather than narrative text. The LLM converts narrative to structured output more reliably when given structured input — and structured input uses fewer tokens than prose descriptions of the same data.

**Input validation in Apex, not prompt**: Validate action inputs (required fields, type checking, business rule verification) in Apex before the LLM processes them. A validation error caught in Apex costs zero AWUs; one caught through an LLM reasoning cycle costs one AWU.

**Batching related queries**: Combine multiple related SOQL queries into a single Apex action rather than individual actions. A single Apex action can execute 10 SOQL queries and return a consolidated payload — all as one AWU. Ten separate Apex actions doing the same work costs 10 AWUs.

```apex
// Efficient: one action, one AWU, multiple data sources
@InvocableMethod(label='Get Customer Context')
public static List<CustomerContext> getCustomerContext(List<CustomerContextRequest> requests) {
    CustomerContextRequest req = requests[0];
    
    // Batch all queries into single action
    Account acct = [SELECT Id, Name, AccountNumber, Industry, AnnualRevenue 
                    FROM Account WHERE Id = :req.accountId LIMIT 1];
    
    List<Case> openCases = [SELECT Id, Subject, Status, CreatedDate 
                            FROM Case WHERE AccountId = :req.accountId 
                            AND Status != 'Closed' ORDER BY CreatedDate DESC LIMIT 5];
    
    List<Order> recentOrders = [SELECT Id, OrderNumber, TotalAmount, Status 
                                FROM Order WHERE AccountId = :req.accountId 
                                ORDER BY CreatedDate DESC LIMIT 3];
    
    // Return structured, LLM-optimized payload
    CustomerContext ctx = new CustomerContext();
    ctx.accountSummary = buildAccountSummary(acct);  // Pre-formatted
    ctx.openCaseCount = openCases.size();
    ctx.topCaseSubjects = extractSubjects(openCases);  // Pre-extracted
    ctx.recentOrderTotal = sumOrders(recentOrders);   // Pre-calculated
    
    return new List<CustomerContext>{ ctx };
}
```

This single action replaces three separate actions (account query → case query → order query), reducing AWU consumption by 66% for the same data retrieval work.

## AWU Controversy: Is It a Meaningful Metric or Marketing Spin?

The AWU metric has a vocal group of critics among enterprise analysts, and their arguments deserve serious consideration by any developer building on Agentforce. The core criticism, articulated by CustomerThink and others: **AWU measures machine exertion, not enterprise value**. An agent can execute thousands of AWUs while achieving nothing commercially — a triggered workflow that fails to resolve a customer issue still registers as a completed AWU. This parallels the "bad query" metric that dominated the early SaaS era, where databases reporting millions of queries per day created an impression of utilization that obscured whether users were actually succeeding at their tasks.

The criticism is technically valid. AWU is an activity metric, not an outcome metric. Salesforce itself acknowledges this in its documentation, noting that AWU measures "total volume of work the platform performs on behalf of customers" — not whether that work produced the intended result. A 1.6 billion AWU quarter could represent 1.6 billion successful outcomes or 1.6 billion failed attempts; the AWU number alone doesn't distinguish between them.

### When AWU Is (and Isn't) Useful

AWU is genuinely useful for: **capacity planning** (understanding compute demand growth), **cost attribution** (mapping spend to business units or use cases), **architecture benchmarking** (comparing AWU efficiency across agent implementations), and **trend analysis** (identifying which agent types are growing in usage). AWU is a misleading signal when used as a proxy for: agent quality, business ROI, customer satisfaction, or whether a given deployment is creating real value.

The practical developer takeaway: use AWU as your cost and efficiency ledger, but maintain a parallel set of outcome metrics — resolution rate, escalation rate, time-to-resolution, customer satisfaction score. When your AWU count rises 20%, you want to know whether that reflects 20% more value delivered or 20% more failed attempts consuming compute. The answer determines whether to invest in scaling or in fixing.

## Getting Started with the Agentforce Agent API and AWU Tracking

The Agentforce Agent API provides programmatic access to agent interactions and is the integration point for external systems to trigger agent actions and receive AWU-attributed results. For developers building custom integrations — CRM connectors, custom service portals, embedded agent experiences — the Agent API is the primary interface. Understanding its request/response structure is essential for both implementing integrations and tracking AWU consumption at the programmatic level.

Each Agent API request that triggers an agent action generates one or more AWUs depending on the action count within the conversation turn. The API response includes execution metadata — including action count, which maps directly to AWU consumption — allowing developers to implement cost attribution at the API call level without relying solely on Event Monitoring post-hoc analysis.

### Key Implementation Steps

**Authentication**: Agentforce API uses Connected Apps with OAuth 2.0. Configure your Connected App with the `Agentforce API` OAuth scope. For server-to-server integrations, use the JWT Bearer Token flow — it doesn't require user interaction and supports programmatic authentication at scale.

**Session initialization**: Each conversation starts with a session initiation request to `/services/data/v62.0/einstein/ai-agent/agents/{agentId}/sessions`. The response returns a `sessionId` used for all subsequent turns in the conversation.

**Sending messages**: Send conversation turns to `/services/data/v62.0/einstein/ai-agent/sessions/{sessionId}/messages`. Each message can trigger multiple agent actions depending on topic complexity.

**Reading AWU data programmatically**: Query `AgentWorkItem` via SOQL or the REST API to retrieve per-session AWU consumption data. Join to `EventLogFile` for token-level detail.

```python
# Example: Track AWU consumption per API session
import requests

def get_session_awu_count(session_id, access_token, instance_url):
    query = f"""
    SELECT COUNT(Id) awu_count, SUM(TokensConsumed__c) total_tokens
    FROM AgentWorkItem 
    WHERE SessionId__c = '{session_id}'
    """
    response = requests.get(
        f"{instance_url}/services/data/v62.0/query",
        headers={"Authorization": f"Bearer {access_token}"},
        params={"q": query}
    )
    return response.json()["records"][0]
```

**Implementing cost guards**: Before processing each conversation turn, check the running AWU count against a per-session budget ceiling. If a session is approaching the budget limit, route to a human agent rather than consuming additional AWUs on a conversation that may not resolve successfully.

---

## FAQ

**AWU란 정확히 무엇이며, 토큰과 어떻게 다른가요?**
AWU(Agentic Work Unit)는 Agentforce AI 에이전트가 완료한 하나의 개별 작업입니다. 토큰이 LLM이 처리한 텍스트 양을 측정하는 반면, AWU는 에이전트가 실제로 수행한 작업 수를 측정합니다. 표준 액션 하나 = 1 AWU = 최대 10,000토큰이며, 이 한도를 초과하면 복수의 AWU로 계산됩니다.

**Agentforce의 세 가지 요금제 중 어느 것을 선택해야 하나요?**
대화당 20개 미만의 액션을 사용하는 경우 Flex Credits($0.10/액션)가 유리합니다. 대화가 복잡하고 액션이 20개를 초과하는 경우 대화당 $2 정액제가 낫습니다. 매일 에이전트를 집중적으로 사용하는 지정 사용자(월 63회 이상 대화)라면 사용자당 $125/월 라이선스가 최적입니다.

**AWU 소비를 최대한 줄이려면 어떻게 해야 하나요?**
가장 효과적인 방법은 액션 통합입니다. 여러 개의 개별 Apex 액션을 하나의 복합 액션으로 합치고, 데이터 조회 시 필요한 필드만 선택하며, 시스템 프롬프트를 간결하게 유지하고, 비실시간 작업은 비동기 처리로 오프로드하는 것입니다. 또한 10,000토큰 한도를 초과하는 액션을 식별하기 위해 Agentforce Observability를 반드시 모니터링해야 합니다.

**AWU가 실패한 작업도 계산하나요?**
네. AWU는 실행을 측정하며, 성공 여부를 측정하지 않습니다. 에이전트가 고객 문제를 해결하지 못하더라도 트리거된 워크플로우는 AWU로 계산됩니다. 이것이 AWU를 비용 추적에만 사용하고, 해결율·에스컬레이션율 등 비즈니스 결과 지표를 별도로 관리해야 하는 이유입니다.

**Agentforce AWU를 프로그래밍 방식으로 추적하려면 어떻게 시작하나요?**
Event Monitoring에서 AgentWorkItem 이벤트를 활성화하고, OAuth 2.0 JWT Bearer 플로우로 Connected App을 구성한 다음, AgentWorkItem 객체를 SOQL로 쿼리하여 세션별 AWU 소비를 파악하십시오. 각 Agent API 응답에 포함된 액션 카운트 메타데이터를 활용하면 사후 Event Monitoring에 의존하지 않고 API 호출 수준에서 비용을 귀속할 수 있습니다.
