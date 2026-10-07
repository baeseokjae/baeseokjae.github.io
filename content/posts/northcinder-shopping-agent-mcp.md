---
title: "NorthCinder Review 2026: A Buyer-Run, Ad-Neutral Shopping Agent MCP"
date: 2026-10-01T07:56:10+00:00
tags:
  - shopping agent mcp
  - northcinder review
  - buyer-run shopping agent
  - ad-neutral shopping agent
  - local-first shopping agent mcp
description: "NorthCinder is a local-first MCP server that ranks offers for the buyer and gates checkout behind a single-use mandate. Hands-on review and verdict."
draft: false
cover:
  image: "/images/northcinder-shopping-agent-mcp.png"
  alt: "NorthCinder Review 2026: A Buyer-Run, Ad-Neutral Shopping Agent MCP"
  relative: false
schema: "schema-northcinder-shopping-agent-mcp"
---

NorthCinder is a local-first MCP server that turns a general AI assistant into a buyer-side shopping researcher: it queries only the stores you configure, ranks offers against your own brief, labels sponsored placements beneath every organic result, and requires a signed, single-use approval before any checkout.

That is a genuinely unusual set of promises for 2026. Most agentic commerce tooling asks you to trust a marketplace, a hosted catalog, or a vendor's own ranking service. NorthCinder asks you to trust code you can read on your own laptop — and then, unusually, publishes a document explaining exactly where that trust stops being verifiable. This review installs it, probes it over MCP, reads the ranking and mandate internals, and then separates the two questions that get conflated in every vendor announcement: **does it work**, and **should you depend on it**.

The short answers are "yes, surprisingly cleanly" and "not yet, and the reason is coverage, not neutrality."

## What NorthCinder Actually Is (and What It Refuses to Be)

NorthCinder ships as an npm package (`northcinder@0.2.1`, MIT, repository `cinderline/northcinder`) and runs as a stdio MCP server. You point your existing AI app at it, and the app gains a set of shopping-research tools scoped to you. There is no hosted endpoint, no account, no telemetry egress, and no affiliate parameter anywhere in the adapters.

That last detail is the whole architecture. NorthCinder has no business model at all — nothing to sell, no referral fee to collect, no demand to route. That is why its ad-neutrality claim is cheap to implement rather than expensive to police. When a project earns money from placements, neutrality is a policy that must be enforced against commercial pressure. When a project earns nothing, neutrality is just the absence of an incentive.

What it refuses to be matters just as much. It is not a shopping bot that autonomously buys things. It is not a marketplace and does not aggregate a proprietary catalog. It does not hold your card details (it explicitly refuses raw card data). It does not place orders through a native store adapter until a human approves a specific, single-use mandate. The shape is consumer-side, read-heavy, per-buyer scoped, with cart handoff rather than merchant-side CRUD — the same lane as a personal research assistant, not the same lane as Shopify's merchant tooling.

The practical framing: NorthCinder is a **control layer** between your AI assistant and the retail web. The interesting engineering is not the search; it is the ranking rule table and the purchase mandate.

## We Installed and Probed It: 21 Tools and an Honest Empty Result

Claims about MCP servers are easy to make and easy to check, so we checked. On Node v24.20.0 with npm 12.0.2, on 2026-10-01:

- `npx northcinder@0.2.1 --version` printed `northcinder 0.2.1`. The package installs with **zero runtime dependencies** and a single optional dependency (`playwright-core ^1.61.1`) used only by the Amazon adapter.
- `northcinder init --config-dir ... --mode local -y` wrote a config directory with `0700` permissions containing `0600` files, including `mandate-key.json` — the signing key for purchase approvals. It printed the ready-to-paste `mcpServers` JSON block and reported a truthful coverage line: `amazon=not_configured, ebay=not_configured, etsy=not_configured, shopify=not_configured, woocommerce=not_configured`.
- A live stdio MCP session (`initialize` → `tools/list` → `tools/call`) returned `serverInfo` name `NorthCinder` version `0.2.1`, protocol version `2025-06-18`, with capabilities for tools, resources, and prompts. **21 tools** were advertised: `search_products`, `submit_browser_observations`, `submit_decision_evidence`, `get_buyers_brief`, `get_trust_signal`, `request_purchase_authorization`, `approve_purchase`, `decline_purchase`, `complete_checkout`, `list_orders`, `import_order`, `create_watch`, `list_watches`, `cancel_watch`, `get_profile`, `update_profile`, `record_feedback`, `review_preference_proposal`, `create_research_plan`, `record_order_outcome`, and `get_order`. Two resources follow the same model, plus a buyers-brief widget and two prompts.

The most informative single call was the one that returned nothing. With no stores configured, `search_products` returned zero finalists with the message "No offer met your criteria — nothing is padded in to fill the list," a per-store coverage table explaining the exact `not_configured` reason for each of the five adapters, and the line "Ranking verification not applicable: no results to verify."

That is the correct behavior and it is rarer than it should be. The default failure mode of a shopping aggregator with thin coverage is to quietly widen the query until something comes back. NorthCinder returns an empty, explained result instead. A tool that tells you it has no answer is a tool you can reason about; a tool that always has an answer is one you have to audit.

The server's stderr was equally candid about its own posture: the local UI runs on loopback, tokenized approval links are written only into buyer-local state, the checkout rail is `cart-permalink`, mail-drop ingest is disabled, and approval pushes are off unless you set `NORTHCINDER_UI_NTFY_TOPIC`.

### Two schema gotchas worth knowing before you write a client

Both are real and both cost time:

1. **`search_products` takes `text`, not `query`.** Passing `query` fails schema validation with "expected string, received undefined."
2. **Money is in minor units.** Prices are integers in cents with a 3-letter ISO currency, so an example call looks like `{text: "black wool running shoes", maxPrice: {amount: 13000, currency: "USD"}}` — that is $130.00, not $13,000.

These are small, but they are the kind of detail that makes a hand-verified review different from a README summary. If a third-party write-up describes a NorthCinder call without mentioning `text` or minor units, it likely never ran one.

## The Ranking Rule Table, and What Sponsored Placement Is Forbidden to Do

NorthCinder's ordering is not an LLM judgment call. It is a published, additive weight table (`RANK_WEIGHTS` in `docs/RANKING.md`), which means the same offer set fed to it twice produces the same order:

| Signal | Weight |
|---|---|
| Price is best | +40 |
| Over budget | −25 |
| Full spec match | +30 |
| Each spec missed | −10 |
| Delivery meets requirement | +10 |
| Each delivery requirement missed | −15 |
| In stock | +5 |
| Pre-order | −5 |
| Out of stock | −20 |
| Merchant trust: trusted | +10 |
| Merchant trust: known | +5 |
| Merchant flagged | −40 |
| Ethics criteria fully matched | +8 |
| **Sponsored** | **0** |

The sponsored row is the one that carries the argument. Sponsored placement contributes **exactly zero points**, and it is additionally confined to a strictly lower tier than every non-sponsored offer. So sponsorship cannot buy rank, cannot buy a tie, and cannot appear above an organic result — not because a policy says so, but because the arithmetic and the tier rule have no path for it to happen.

This is worth contrasting with the industry norm, where sponsored placement is typically an ordering input or a boost multiplier. A referral-fee model and an affiliate-parameter-aware ranking function are the same thing seen from two angles: one determines the other. NorthCinder's ranking function does not know what a commission is, which is the structural reason its neutrality claim holds up.

## What the Neutrality Audit Proves — and the Sentence That Limits It

The project ships a generated neutrality audit (`docs/NEUTRALITY-AUDIT.md`) built on a fixed seed (`20260705`) so reruns are byte-identical. It records three passing batteries:

- **250 re-rankings** across 50 offer sets × 5 shuffles, with **0 divergences** — the order is invariant to input ordering.
- **99 sponsored-flag flips**, with **0 rank improvements**, **0 score changes**, and **0 offers left above an organic offer** — flipping sponsorship changes nothing.
- **11 single-dimension attribute probes**, with **0 deltas diverging** from the published weights (the sponsored probe measured exactly 0, as expected).

Those are meaningful results. Determinism and sponsorship-invariance are precisely the properties you want to be able to falsify, and they are stated in a way that lets you falsify them.

Now the sentence that limits all of it. `RANKING.md` states plainly that client-side re-ranking can only prove the order *over the inputs the service disclosed* — and that a dishonest service could fabricate trust levels, strip a sponsored flag, or curate which offers it returns at all, and still pass with `rankingVerified: true`.

Read that twice, because it is the most honest thing published in agentic commerce this year. It means the verification chain proves **the ranker did what the ranker says**, not that the offer set is complete or the inputs are real. A service that quietly deletes the cheapest competitor before ranking it has not violated any weight — it has violated the supply of inputs.

So the correct claim for NorthCinder is narrower than "neutral": it is **neutral over disclosed inputs, with a verifiable rule table, on data you largely supply yourself.** And that last clause is not a marketing add-on. Local-first is what makes the trust claim testable at all. If the buyer-side state lived in a hosted service, neutrality would become a promise from the same party you are supposed to distrust — which is exactly the position BuyWhere and Zinc are in, however good their intentions.

## Purchase Approval as a Single-Use Capability: Request, Approve, Complete

The mandate gate is the part of NorthCinder most worth stealing, and it generalizes well past shopping. The flow is three stages:

1. **Request authorization.** `request_purchase_authorization` produces a scoped request bound to a specific offer, a quantity of exactly one, and a signing key from `mandate-key.json` that never leaves the local config directory.
2. **Approve.** `approve_purchase` requires a one-time code delivered to the human, consumed against a single-use nonce ledger, so an approval cannot be replayed, shared, or reused for a second item.
3. **Complete.** `complete_checkout` executes through the cart-permalink rail, or hands off to a native store adapter that must independently confirm the order.

The properties that make this pattern a genuine capability token rather than a confirmation dialog:

- **Single-use nonce.** Approval is consumed, not cached. This is the difference between a permission and a permission *instance*.
- **Quantity-one binding.** The mandate is tied to one offer and one unit, so a "yes" cannot be stretched into a larger purchase.
- **Raw card details refused.** The system declines to become a place where card numbers live, which removes the most attractive breach target.
- **Cart-permalink fallback.** When no adapter can complete the order, the agent hands you a link and the purchase happens in your browser, under your own session and your own credentials.

The last point is where NorthCinder's ambition visibly stops. Zinc's Zinc GPT reference agent wires an LLM plus SerpAPI, Stripe, and Zinc's purchasing rail to complete **real paid orders end to end**, and Zinc publishes a checklist for judging community shopping MCPs — does it place a real paid order, who holds the retailer account, what happens on stockouts, CAPTCHAs, and address failures. Against that checklist, NorthCinder deliberately answers "a human clicks the link." That is a defensible design choice for a buyer-side tool, and it is not the same capability as a purchasing rail. Do not buy NorthCinder expecting Zinc.

## Merchant Trust: 1,095 Days, Top-1M Rank, and Why "Unknown" Is Not "Unsafe"

`docs/TRUST.md` defines a four-level trust table with hard numeric thresholds, not vibes:

- **Known** requires both a domain age of at least **1,095 days** (three years) *and* a popularity rank inside the **top 1,000,000**.
- **Trusted** sits above that bar.
- **Flagged** requires deny-grade evidence — a local deny seed or a curated fraud list. It **can never** be produced by automated age/rank/platform heuristics, which prevents a stale domain from being silently blacklisted.
- **Unknown** is simply the floor for "no history," explicitly not a negative judgment.

Two design decisions stand out. First, the inputs are measurements and curation hits only — no seller-controlled input can raise a merchant's trust level, so a storefront cannot buy its way up. Second, the refusal to auto-flag is what keeps the system honest at the bottom of the long tail: a new but legitimate shop lands at `unknown` (+0 points) rather than being penalized like fraud. The −40 flagged penalty is reserved for actual evidence.

## Store Coverage Is the Real Blocker

Everything above describes a well-specified system. This section describes why you still should not deploy it as your shopping stack today. None of the five adapters is turnkey.

| Store | What it needs | Practical status |
|---|---|---|
| Shopify | Has moved to UCP (`/api/ucp/mcp`); requires an **HTTPS UCP agent-profile URL you host yourself**. The deprecated Storefront Catalog endpoint is maintained only until 2026-06-15. | Blocked on you hosting a profile document |
| WooCommerce | An explicit host list exposing the public Store API on the buyer's target sites | Workable, but manual per store |
| eBay | Buy Browse requires an **approved Developers Program keyset**, with a separate production gate | Approval-gated |
| Etsy | An **approved Personal App**, then a separate Commercial Access review; the docs forbid scraping | Double approval-gated |
| Amazon | Read-only Playwright driving **the buyer's own Chrome profile**. No checkout at all. | Research only |

The Amazon row carries an extra irony: NorthCinder rejects Amazon's Creators API because its Associate tag is an affiliate mechanism, which conflicts with the entire no-affiliate model. The project is consistent, and it pays for that consistency with capability.

The Shopify row carries a sharper one. NorthCinder's independence claim is layered **on top of the protocol it criticises** — Google and Shopify's UCP covers discovery, cart, identity, checkout, and orders through a `/.well-known/ucp` manifest, which the project's own README calls convenient but not independent advice. So the buyer-side ranker sits on a merchant-defined catalog contract, and the project's answer to "is the offer set complete?" is now partly Shopify's answer.

Coverage, not ranking, is the blocker — and it is upstream of NorthCinder entirely. The honest verdict for a builder is therefore: **fork the mandate gate and the ranker, wire your own catalog.** Those two subsystems are the durable contribution. The adapters are the part you would rewrite anyway.

## 1,215 Stars, 13 Weekly npm Installs, 6 Commits: How to Read the Numbers That Matter

Here is where a review earns its keep. NorthCinder has 1,215 GitHub stars, and those stars do not describe the project that was actually measured.

| Metric (2026-10-01) | Value |
|---|---|
| GitHub stars | 1,215 |
| Forks | 10 |
| Watchers/subscribers | 5 |
| Open issues | 0 |
| Commits (all time) | 6 |
| Contributors | 1 |
| npm downloads, last week | 13 |
| npm downloads, last month | 56 |
| Last push | 2026-08-22 |

Do the division and it gets stark: roughly **93 stars for every weekly install**. A project with 1,215 stars and 13 weekly downloads is not being used. It is being bookmarked.

The trajectory explains it. The repo was created 2026-08-17T11:42:31Z. By 2026-08-19, third-party snapshots recorded about 1,190 stars — two days. By 2026-08-20, 1,197 ("399 stars a day"). By 2026-09-03, 1,219 stars with 8 forks. On 2026-10-01, 1,215 stars with 10 forks. Roughly **1,200 of 1,215 stars landed in the first three days**, and the count has been flat for six weeks. The star-history chart shows the same shape: a vertical spike, then a horizontal line.

The development record matches the flat line. Six commits total, all authored as "NorthCinder maintain" between 2026-08-17 and 2026-08-22, with one contributor. Five merged pull requests, and every one of them is a **grammar fix from an outside user**; the five closed issues are the matching grammar reports. There is **zero substantive external code contribution**. There is also no Hacker News submission at all — Algolia story search returns 0 hits — so there is no organic discussion thread, and only two GitHub Discussions from 2026-08-29: a merchant-identity pitch asking $0.10 USDC per call over x402, and a cold outreach from an ops agent. Both have zero maintainer replies.

An early observer flagged the divergence when it was smaller. EnterpriseDNA's AI Pulse for 2026-08-19 questioned the trajectory directly: "1,190 stars on GitHub in two days... Except the rest of the numbers don't back that up. Only 4 forks and 5 watchers. For a project with over a thousand stars, that's a strange gap." Six weeks later, the gap is quantified: 1,215 stars, 10 forks, 5 subscribers, 13 weekly installs.

None of this is an accusation, and the review should be careful not to make one. Star counts can spike from a single aggregator post or newsletter mention without any manipulation. But the background matters, because GitHub stars are a measurably contaminated signal in exactly this category: an ICSE 2026 measurement study identified roughly **6 million suspected fake stars across 18,617 repositories and 301k accounts**, with AI/LLM repositories the largest non-malicious category and stars selling for **$0.03 to $0.85** each from at least a dozen vendors. Dagster's investigation found fake stars help for under two months and then become a liability.

The teaching point is procedural, not moral: **read the commit log and the npm download graph before the star number.** Six commits from one author and 13 weekly installs tell you what 1,215 stars cannot. StarScout-style tooling exists precisely because this check is now routine diligence.

### The third-party reviews of this project are also a cautionary tale

Within days of launch, the repo was being re-summarised by AI-generated discovery sites. One attributes NorthCinder to a GitHub account `jdshfhds` with a clone URL for `jdshfhds/northcinder` **that does not exist**. Another is a content-marketing restatement of the README with no evidence of execution. If you were evaluating shopping agent MCP servers by reading reviews, you would have been misled twice. Run your own `npx`.

### One contradiction to know about

The release pages contradict the project's own retraction. v0.2.1 retracted the unsupported routine-use host/model claim — "no combination is currently qualified" — yet the v0.2.0 release notes still advertise "Routine research support is qualified for Codex CLI 0.147.0 with gpt-5.6-luna at medium reasoning over local STDIO MCP." Two live pages, opposite claims. Praise the retraction; note the staleness; and treat the in-repo docs and the v0.2.1 changelog as authoritative over the release page.

## How NorthCinder Compares With BuyWhere, Zinc, and Shopify's MCP

All four products call themselves neutral. Only one has nothing to sell.

| | NorthCinder | BuyWhere | Zinc / Zinc GPT | Shopify MCP + UCP |
|---|---|---|---|---|
| Buyer-side or merchant-side | Buyer-side | Multi-merchant catalog | Purchasing rail | Merchant-side |
| Where ranking lives | Buyer's own code | Vendor's catalog service | Vendor's search + LLM glue | Merchant catalog |
| Sponsorship in ranking | 0 points, tier-demoted | Affiliate link tracking out of the box | Per-transaction incentive (MPP) | N/A (merchant scope) |
| Revenue model | None | Referral fees, merchant partnerships, demand routing | Transaction fees | Merchant platform |
| Real order completion | No — cart-permalink handoff | Via merchant links | Yes — real paid orders | Yes, in merchant scope |
| Catalog breadth | Whatever you configure (5 adapters, none turnkey) | 300M+ products, 900k+ merchants | Amazon, Walmart, Target, Best Buy, 50+ US retailers | Shopify merchants |
| What "neutral" means | Ranking code you can inspect | No inventory, no platform to favour | No inventory, pay per transaction | N/A |

BuyWhere's defense is instructive and completely different: it argues that because it has no inventory to sell and no platform to favour, "neutral" means a **multi-merchant catalog** rather than buyer-owned ranking code. It indexes 300M+ products across 900k+ merchants in Singapore, Malaysia, Indonesia, Thailand, the Philippines, Vietnam, and the US, exposes MCP-native tools (`search_products`, `get_product`, `compare_products`, `get_price_history`, `check_availability`, `get_alternatives`, `get_categories`, `get_trending`), and monetizes through referral fees and demand routing rather than API subscriptions — shipping affiliate link tracking out of the box. It also markets a 50–100 line SerpAPI-to-MCP comparison, which frames the decision in **integration cost** terms NorthCinder does not address, and its free tier covers 1,000 calls/month over streamable HTTP at `api.buywhere.ai/mcp`.

That is the axis the review should land on: **neutrality as data coverage versus neutrality as code you can inspect.** BuyWhere wins on coverage and loses on incentive alignment — an affiliate-tracking catalog is structurally the ranking input NorthCinder forbids. NorthCinder wins on inspectability and loses on usefulness today. If you need a working catalog this quarter, BuyWhere and Zinc are the answers; if you need a defensible architecture for buyer-owned controls, read NorthCinder's `checkout/packages/` and `docs/TRUST.md` first.

## Why This Pattern Matters Now: Google AI Mode's 21.6% Price Gap and Amazon's Lockdown

Strip away the star count and the unanswered adapter questions and there is still a good reason to care about buyer-side ranking: the empirical case arrived this year.

A 23-day controlled study by Productrise (Hugo Huijer, published 2026-09-01) tracked more than 2 million listings across more than 100,000 SERPs and AI Mode responses in the US and UK from 9–31 August 2026. Among products appearing in **both** Google AI Mode and traditional search on the same day, the AI Mode lead price averaged **21.6% higher**. Across all priced listings the median was **$149 versus $100** — about 49% higher. Only **1.28%** of traditional-search products appeared in AI Mode at all. When prices disagreed, AI Mode was pricier **68.4%** of the time (median +22.2%), and the lead seller differed **49.6%** of the time. AI Mode also showed **3.9 products per query** versus 27.8 in traditional search.

The coverage of that study has been carried by Search Engine Journal and PPC Land, and reasonable people can argue about what drives the gap — surface differences, ranking differences, or availability differences. What it establishes is narrower and sufficient: **agent-mediated product discovery has its own incentives and its own price distribution, and it does not match the search results you are used to.** When the assistant picks three products instead of thirty, the ranking function is the entire market. Owning that function is no longer a philosophical preference.

Meanwhile the platform side is closing, not opening. Amazon blocked Meta's Muse agent from shopping its site in September 2026, on the stated grounds that "continued access by an unauthorized AI agent violates Amazon's Conditions of Use." Its Perplexity case ran an injunction on 10 March 2026, a Ninth Circuit reversal on 4 August 2026, and a denied rehearing on 10 September 2026, leaving contract and ToS claims as the open avenue. Amazon's own Buy for Me identifies itself and lets brands opt out. The direction of travel is clear: platforms intend to control which agents transact, and a buyer-side ranker that runs locally with the buyer's own credentials is one of the few architectures that does not require a platform's permission.

For scale, this is not a niche: agentic commerce is estimated at **USD 5.7B in 2025 and USD 7.7B in 2026**, reaching **USD 65.5B by 2033** at a 35.7% CAGR, with North America at 38.2% share (Grand View Research). Juniper Research puts total agentic commerce transaction value at **$8B in 2026 rising to $3.5T by 2031** — 43,240% growth across 24 vendors. MCP itself is no longer the constraint: monthly SDK downloads moved from 97M at the December 2025 Linux Foundation donation to roughly **204M/month for the npm TypeScript SDK** and **319M/month for PyPI's `mcp` package** by September 2026, with public server counts between ~11,000 and ~22,000 and the Agentic AI Foundation at 247 members.

## Verdict: Read the Checkout Package, Fork the Mandate Gate, Do Not Deploy It as Your Shopping Stack

NorthCinder is the clearest written specification yet for buyer-side commerce controls, and it is honest about its own limits in a way that almost nothing else in this category is. `RANKING.md` telling you that `rankingVerified: true` cannot detect a fabricated trust level or a curated offer set is worth more than a hundred "bank-grade neutrality" marketing pages, because it tells you what to verify yourself.

Adopt it, with scoping:

- **Read first, install second.** Start with `checkout/packages/` and `docs/TRUST.md`. The mandate gate — request, one-time-code approval, single-use nonce ledger, quantity-one binding, no raw card data — is a reusable pattern for any agent that can spend money. Steal the pattern even if you never run the server.
- **Then read the ranker.** The published weight table plus the fixed-seed audit is a testable neutrality contract. It proves determinism and sponsorship-invariance over disclosed inputs, and that is exactly what it claims to prove. It does not prove catalog completeness, and the docs say so.
- **Do not deploy it as your shopping stack today.** No adapter works out of the box; the project is dormant since 2026-08-22; and 1,215 stars against 13 weekly npm installs means you would be one of the first real users, debugging alone against a two-month-old bundle with six commits behind it.
- **Calibrate expectations against the alternatives.** Zinc and BuyWhere actually complete commerce; Shopify's official MCP surface will be the default for the merchants locked into it. NorthCinder is the reference architecture, not the rail.
- **Then do your own `npx`.** The two schema gotchas (`text` not `query`; money in minor units) and the honest empty result take about fifteen minutes to reproduce. That is less time than you would spend reading one more AI-generated review of it.

The one-line verdict: **a genuinely well-specified buyer-side control layer that nobody is using yet, published by a project too honest to pretend otherwise.** Treat it as the spec, and treat deployment as a project you have not started.

## Frequently Asked Questions

### Is NorthCinder free, and is it safe to run?

Yes to free: it is MIT-licensed with no account, no hosted component, and no telemetry, so the running cost is a Node process. Safety is architectural rather than certified — the config directory is created `0700` with `0600` files including the mandate signing key, the local UI binds to loopback, approval links are written only to buyer-local state, and the server refuses raw card details entirely. The residual risk is not the code, it is the store adapters: the Amazon adapter drives your real Chrome profile, and any adapter you configure inherits whatever credentials you supply.

### Does NorthCinder place orders for me automatically?

No, and that is a design choice rather than a limitation. Order completion runs through three stages — request authorization, one-time-code approval, complete checkout — and the approval is bound to a single offer, a quantity of exactly one, and a single-use nonce, so it cannot be replayed or stretched. When no active adapter can complete the order, the fallback is a cart permalink you open yourself. If you need end-to-end paid orders placed by an agent, Zinc is the rail built for that, and it publishes exactly the checklist (stockouts, CAPTCHAs, address failures) NorthCinder's design sidesteps.

### Which stores does the shopping agent MCP actually support today?

Five adapters are advertised and none is turnkey. Shopify has moved to UCP and needs an HTTPS agent-profile URL you host yourself. WooCommerce needs an explicit host list exposing the public Store API. eBay's Buy Browse needs an approved Developers Program keyset with a separate production gate. Etsy needs an approved Personal App plus a Commercial Access review, and its docs forbid scraping. Amazon is read-only Playwright against your own Chrome profile with no checkout. With none configured, `search_products` correctly returns an empty, explained coverage table instead of padded results.

### The repo has 1,215 GitHub stars — why not just use it?

Because the star count is the least informative number in the repository. Alongside 1,215 stars there are 10 forks, 5 watchers, 6 commits from a single contributor, 0 open issues, 5 merged grammar-fix PRs as the only outside contribution, no Hacker News thread, and roughly 13 npm downloads in the last week against 56 in the last month — a ~93:1 star-to-install ratio. About 1,200 of those stars landed in the first three days of August 2026 and the count has been flat since, with no commits after 2026-08-22. Given ICSE 2026's finding of ~6 million suspected fake stars across 18,617 repos selling for $0.03–$0.85, read the commit log and download graph before the star number.

### What is the actual neutral-ranking claim, stated precisely?

It is narrow and it is testable: sponsored placement contributes exactly 0 points and is tier-demoted below every organic offer, re-ranking is deterministic (250 re-rankings, 0 divergences), sponsored-flag flips cause 0 rank improvements (99 flips), and single-dimension probes match the published weights (11 probes, 0 divergences) on a fixed seed of `20260705`. What it does **not** prove is catalog completeness or input honesty — `RANKING.md` says outright that a dishonest service could fabricate trust levels, strip a sponsored flag, or curate the offer set and still return `rankingVerified: true`. Neutrality you can inspect is strictly narrower than neutrality you can trust.
