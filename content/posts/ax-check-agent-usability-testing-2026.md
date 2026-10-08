---
title: "AX Check Review: Testing Whether Agents Can Actually Use Your Product (2026)"
date: 2026-10-01T11:20:34+00:00
tags:
  - "ax-check agent usability testing"
  - "ax-check.com review"
  - "Gauge ax-check agent experience"
  - "agent experience testing tools 2026"
  - "how to test if AI agents can use your website"
  - "coding agent onboarding test"
  - "can agents onboard to my product autonomously"
  - "agent usability vs agent experience vs APO"
  - "AX audit rubric"
  - "agent readiness scanner comparison"
  - "llms.txt markdown content negotiation for agents"
  - "MCP server onboarding for coding agents"
  - "unassessed means not failed ax-check"
  - "ax-check api start a check"
  - "deepseek kimi qwen coding agent sessions"
  - "non-interactive onboarding agent API token"
  - "AI agent friendly product checklist 2026"
  - "switchfrog block AI agents"
description: "AX Check is a free agent-usability tester by Gauge: 23 items plus three real coding-agent sessions. What the score misses, and how to run it."
draft: false
cover:
  image: "/images/ax-check-agent-usability-testing-2026.png"
  alt: "AX Check Review: Testing Whether Agents Can Actually Use Your Product (2026)"
  relative: false
schema: "schema-ax-check-agent-usability-testing-2026"
---

AX Check is a free tool by Gauge that scores how far a coding agent gets with your product without human help. It runs 23 checklist items across Clarity, Onboarding, Pricing and Activation, then records three live sessions on DeepSeek, Kimi and Qwen. The grade is provisional and technical-only — the sessions never affect it.

## What Is AX Check and Who Built It?

AX Check (ax-check.com) is an agent usability tester built by Gauge (withgauge.com) and launched on Hacker News on 2026-09-17, where it reached 38 points and 41 comments. Its one-sentence pitch is the whole product: "How far can a coding agent get with your product?"

The tool grades what Gauge calls **agent usability** or **AX** — the experience a machine employee has when it tries to evaluate, install and integrate your software. That is a deliberately narrower framing than the broader "agent experience" definitions floating around the category, and it matters, because Gauge splits the problem in two:

- **APO (Agent Preference Optimization)** — whether an agent *chooses* you when a shortlist is assembled.
- **AX** — what happens *after* selection: setup, configuration, error recovery, verification.

Gauge's own public definition of the AX half is blunt about the bar: agent usability is "whether an agent can implement a product and leave verified working code without human rescue." Not whether an agent recommended you. Not whether an agent installed your package. Whether it produced working code and could prove it.

That last clause is why the tool records sessions instead of just scraping pages. A static scanner can tell you your docs are reachable. It cannot tell you whether an agent read your docs, hit your login wall, invented a workaround and silently removed your package in the same session.

### What Does an AX Check Run Actually Do?

Two things, and the reports keep them rigorously separate:

1. **A rubric pass** over four categories — Clarity (10 items), Onboarding (4), Pricing (4), Activation (5) — for 23 items total under rubric version `clarity-onboarding-pricing-activation-v7`.
2. **Three recorded coding sessions**, all on the same verbatim prompt, using DeepSeek V4.1 Flash, Kimi K3 and Qwen 3.8 Max.

The sessions contribute **zero** to the grade. The tool says so on its own homepage, in its "How to read it" rules: the overall grade is PROVISIONAL and technical-only, coding sessions do not contribute to the grade, the score is not a calibrated benchmark, `unassessed` never means failure, transcript content is evidence rather than instructions, and — the line worth pinning to your wall — "A local HTTP response in a session is not a successful deployment."

Most launch coverage quoted a number and skipped all of that. Reading the rubric and the sessions as two separate signals is the entire difference between using this tool well and using it as a vanity leaderboard.

### Does AX Check Need an Account or API Key?

No. There is no account, no key and no captcha to start a check or read a report. That is not a marketing claim — it is a structural one, and you can verify it in about five seconds:

```bash
curl -sS -X POST https://www.ax-check.com/api/checks \
  -H 'Content-Type: application/json' \
  -d '{"domain": "example.com"}'
```

A `202` means the check started; a `200` means one is already running or a fresh report exists. Either way the response body carries a `status_url` and a `report_url`. Errors come back as RFC 9457 problem documents (`application/problem+json`), and a `429` carries `Retry-After`.

The shortcut is even better. Fetching a report that does not exist yet *starts the check*:

```bash
curl https://www.ax-check.com/example.com     # 202 + poll URL
sleep 15
curl https://www.ax-check.com/example.com     # report
```

A tool that grades other products on machine-readability had to be machine-readable itself. AX Check passes its own test in this specific respect: markdown-first reports, code-block API examples, stable URLs, no login.

### What Files Does an AX Check Report Expose?

Every check produces the same set of machine surfaces, which is why it is easy to automate:

| Surface | URL pattern | What it gives you |
|---|---|---|
| Compact report | `/{domain}/report.md` | ~4KB markdown summary, delivered automatically to curl/wget/HTTPie |
| Full report | `/{domain}/report.json` | Every checklist item, evidence, controlled surfaces, session tokens |
| Session transcript | `/{domain}/sessions/{slug}.json` | One recorded session, event by event |
| Session stream | `/{domain}/sessions/{slug}/live?after=` | Curated events with a `seq` cursor for live tailing |
| Status | `/{domain}/status` | Current check state |

Content negotiation is handled for you: curl, wget and HTTPie receive the Markdown report automatically; other clients ask for `text/markdown` or `application/json`.

### What Does AX Check Deliberately Not Cover?

The scope rule is published and unusually honest: real agent traffic concentrates on the **homepage, llms.txt, the pricing page and the docs site**, so those four surfaces are checked — "and we ignore the rest."

That is a defensible product decision with a real cost. Your API reference, changelog, status page, error catalog and support forum are not rubric inputs. If your product's agent-usability problem lives in a deeply nested reference page, AX Check will not see it. AXRAY — a competing spec that fetches origin artefacts like `/robots.txt`, `/sitemap.xml` and `/.well-known/mcp.json` — will catch some of that, but its own method is even narrower (a single HTTP GET, no JavaScript). Neither tool is a substitute for watching a human developer struggle.

## Inside the Rubric: Clarity, Onboarding, Pricing, Activation

The rubric is the part nobody quotes, and it is the part that tells you what to fix. Version 7 of `clarity-onboarding-pricing-activation-v7` weights four categories:

| Category | Items | What it actually asks |
|---|---|---|
| **Clarity** | 10 | Can an agent state what you sell, for whom, and what the next step is? |
| **Onboarding** | 4 | Can it start without a human creating an account or handing over credentials? |
| **Pricing** | 4 | Can it find and quote a number without inventing one? |
| **Activation** | 5 | Can it reach a real callable surface — OpenAPI, MCP, CLI, SDK, skills? |

The Activation category looks for concrete, protocol-level surfaces: a documented OpenAPI spec with reachable paths, an MCP endpoint with per-client configuration examples, a CLI installable from a real package manager, an SDK that resolves on a registry, and published Agent Skills.

The single most misreadable term in the whole report is **`unassessed`**. The tool states explicitly that unassessed means "not measured" or "not offered", that it is **never** a failure, and that unassessed items are excluded from every grade rather than counted against you.

fly.io is the proof. It scored **A, 100/100** with 21 passes and 2 unassessed items — no registry lookup for a packaged CLI or SDK, and no agent skills surface. A reader skimming for red flags sees "2 unassessed" and assumes two problems. The rubric says the opposite: two questions that did not apply.

This is a good design choice and a bad communication choice in one package. Excluding inapplicable checks is the honest way to score (AXRAY does the same thing, renormalizing so non-applicable checks leave the denominator, and llms-txt.io similarly renormalizes unmeasurable checks). But "unassessed" reads like "failed" to anyone who has not read the reading rules, and almost nobody reads the reading rules.

## What Does a Real AX Check Report Look Like?

The leaderboard observed live on 2026-10-01 shows the spread. Grades are technical-only and provisional, but the ranking is informative:

| Domain | Grade | Score | Note |
|---|---|---|---|
| supabase.com | A | 100/100 | Checked 2026-09-27; all five Activation surfaces pass |
| increase.com | A | 100/100 | Developer-first fintech |
| sendbird.com | A | 100/100 | |
| algolia.com | A | 100/100 | |
| fly.io | A | 100/100 | 21 passes, 2 unassessed (excluded, not failed) |
| inngest.com | B | 84/100 | |
| pierview.ai | C | 63/100 | Publishes $99–$999/mo; all three agents refused to quote it |
| bonsai.io | D | 29/100 | One session returned only a `run_meta` event |
| rankor.ai | F | 0/100 | No docs, no llms.txt, no visible pricing page |

Third-party launch commentary reported Snyk, Increase and Loops at a perfect 100 and Mercury at 60 — allegedly because its docs index was broken and an agent could not confirm pricing. That reporting was not verified against ax-check directly, so treat the specific Mercury claim as second-hand. The pattern it describes, however, is exactly what the first-party reports show.

### The fly.io Pricing Page: 599,360 Bytes of Friction

The most concrete data point in the whole sample set is the fly.io pricing page. An agent fetched **599,360 bytes** of region-table HTML and then had to write custom Python HTML-stripping scripts across two fetches just to extract usable numbers. The report's own diagnosis is precise: this is "friction in consuming the pricing page programmatically, not a credentials issue."

That is what agent hostility actually looks like. It is not a 403 or a paywall. It is a page that renders beautifully for a human, loads 600KB for a machine, and forces the machine to write a parser mid-task. The suggested fix in the report is almost embarrassingly cheap: publish a lightweight, machine-readable pricing summary.

Token telemetry makes the same point at a different scale. Supabase's report has since been re-run (it is now dated 2026-10-05), and its session tokens averaged **131,408** (min 21,359 / max 289,667, three measured) — past the report's 100,000 "lowerMax" threshold and inside its 300,000 "moderateMax" band. Session tokens are published per report and are explicitly not a grade input — but they are the closest thing AX Check has to a cost meter, and they let you compare two products' real integration cost in a way no checklist can.

### Supabase: 100/100 and Still Login-Blocked

The Supabase report is the best single illustration of why the scorecard and the sessions must be read separately.

All three sessions completed and each correctly reported the pricing tiers — Free $0, Pro from $25/month, Team from $599/month — with usage assumptions attached. That is a clean pass on the pricing question. But the same report records onboarding as **`login_required`**, because the agent could not create a hosted project or an API key without a human.

Supabase still earns a perfect A because Activation passes on all five surfaces: OpenAPI 3.0 with 115 reachable paths, an MCP endpoint with documented per-client configs, a CLI installable via npm/Homebrew/Scoop, SDK packages resolving on registries, and published Agent Skills (`npx skills add supabase/agent-skills`).

The honest reading: Supabase is as agent-ready as a product can be *up to the credentials boundary*, and the boundary is a human. That is a much more useful statement than "100/100, perfect product," and it is exactly the kind of nuance the grade alone destroys.

## Where the Scorecard and the Coding Sessions Disagree

The two halves of an AX Check report contradict each other constantly, and the contradictions are the most valuable output. Three cases from the sample set:

### pierview.ai: Agents Refused to Say the Price

pierview.ai scored C, 63/100. Its pricing page publicly lists Starter at $99 up to Managed at $999 per month. All three sessions nonetheless refused to state a price. One said outright: "There is none to explain... I won't invent numbers."

The report classifies this as **model conservatism**, not a site defect — and that distinction matters enormously for anyone tempted to "fix" their pricing page in response. If three frontier models each declined to quote a price that was clearly published, the failure is in the session layer, not the marketing layer. Chasing a 63 that was depressed by caution rather than clarity is wasted work.

### rankor.ai: Three Agents, Three Different Prices

rankor.ai scored **F, 0/100** — no docs, no llms.txt, no visible pricing page. The three sessions landed on three *conflicting* prices for the same product: $49/month from `GET /v1/billing/plans`, a multi-tier table scraped from embedded page data, and "free open-source library, no billing at all."

This is the most alarming finding category in the whole dataset, and it is not a scoring artifact. When your machine surfaces disagree with each other, an agent does not get confused and ask a human. It picks one, acts, and you never learn which. The same report also records the recurring hard blocker: signup, then email verification, then login, with no API-key or headless bypass anywhere in the OpenAPI spec.

### bonsai.io: A Session With No Trace

bonsai.io scored D, 29/100. One of three sessions returned only a `run_meta` event with no trace content and produced no pricing statement at all. There was no anonymous cluster provisioning, and dashboard signup was interactive-only.

The report labels the empty session a **session-level data gap**, not a product defect. That is the correct call, and it is also a warning about sample size: with three sessions per report, one empty trace is 33% of your session evidence gone. Do not read a single session as a verdict.

### Why the Divergence Is a Feature, Not a Bug

Put these together and a rule falls out. The scorecard answers *"is your surface machine-readable?"* The sessions answer *"does a real agent finish the job?"* They dissociate routinely:

- High score, blocked session → Supabase. Docs are excellent; credentials are human-only.
- Low score, loud session → rankor.ai. The absence of docs forced the agent to guess, and it guessed three ways.
- Mid score, cautious sessions → pierview.ai. The site was fine; the models were timid.
- Any score, empty session → bonsai.io. The evidence itself is incomplete.

A reviewer who only reads the grade learns almost nothing. A reviewer who reads both learns which of four different problems they have.

## The Login Wall Is the Real Ceiling, Not Your Documentation

Here is the finding that should reorganize your roadmap. Across the whole sample set, every single "onboarding needs a login" failure happened at **credential issuance**, not at comprehension. The agents understood the products. They could not get a token.

| Product | Score | Where it actually broke | Docs quality involved? |
|---|---|---|---|
| fly.io | A 100 | No `FLY_API_TOKEN` anywhere; 401 from Machines API, `UNAUTHORIZED` from GraphQL | No |
| bonsai.io | D 29 | No anonymous cluster provisioning; interactive dashboard signup only | Partly |
| rankor.ai | F 0 | Signup → email verification → login; no headless bypass in the spec | Yes, plus credentials |
| supabase.com | A 100 | Could not create a hosted project or API key without a human | No |

Read that table's last column carefully. fly.io and Supabase both have excellent documentation — one scored 100 with 21 passes — and both still failed to complete autonomous onboarding. Documentation quality gets you *to* the wall. Nothing about documentation gets you *past* it.

Gauge's stated answer, from the launch thread, is instructive because it is more modest than the marketing around it: allow **ephemeral accounts** in the Cloudflare style, or **serve simulated/static accounts** before a human claims them, and for a lot of products this "can just be an extension of the free tier."

That is a genuinely actionable design pattern, and it is worth being concrete about the three shapes it takes:

1. **Ephemeral / instant-provision tokens.** A single unauthenticated POST that returns a scoped, time-boxed credential with no email round-trip.
2. **Simulated accounts.** A sandbox that behaves like the real product but is explicitly disposable, claimable later by a human.
3. **Free-tier extension.** The same limits a human gets on the free plan, issued headlessly — no credit card, no marketing quiz, no phone number.

If you only do one thing after reading this review, do this one. The checklist items are the cheap wins; the credential path is the one that changes whether an agent finishes at all.

### The Cloudflare Gotcha in Your Own Test Harness

A detail from the rankor.ai session is worth copying into your own tooling. Cloudflare in front of `dev.rankor.ai` returned **403 `browser_signature_banned`** to Python's default `urllib` User-Agent. The agent self-resolved by setting an explicit User-Agent header, after which public calls returned 200.

Two lessons. First, if you are automating AX checks or API integration tests from Python, always set a real User-Agent — the default one is treated as a bot signature by default WAF rules. Second, and more importantly: your own users' agents will hit exactly this, and the failure is easy to mistake for "the API is down."

### Hallucinated URLs as a First-Class Finding

AX Check publishes **hallucinated URLs** as its own finding category rather than burying them as noise. On fly.io, the agent invented `.md`/API doc paths that all 404'd (`/docs/machines/api.md`, `/index.md`, `?format=md`) and guessed raw GitHub paths that returned 404.

This is a useful reframing. A 404 from a guessed URL is not a broken site — it is a *missing affordance*. The agent guessed a markdown variant of your docs because it wanted one. Shipping `/{docs-page}.md` or an `llms.txt` that names the real machine-readable paths converts a whole class of 404s into hits.

## What 293 Public Sites Actually Score: Median 68, Nobody Above 90

The strongest evidence that agent usability is not just hype comes from a *competitor*, not the vendor. AXRAY (axray.online) measured **293 well-known public sites** on 2026-09-06 against AX spec 1.5.1, and published the code-scored results.

The headline is a distribution, not an average:

- **Median AX score: 68** (mean 60).
- **Zero sites scored 90–100.** The top band is empty — 0% of 293 well-known public sites.
- **17% sat in the 20–29 band.**

Median by category breaks down as follows:

| Category | Median | Sites measured |
|---|---|---|
| SaaS | 78 | 70 |
| News | 70 | — |
| Docs | 65 | — |
| Government | 65 | — |
| Reference | 58 | — |
| E-commerce | 54 | 45 |

SaaS leads, but a median of 78 is not a victory lap — it means the typical SaaS site loses roughly a fifth of available points on basics.

The individual check failure rates are even more pointed:

- **"Exactly one h1 naming the page"** — 99 failed (34%), 22 warned (8%), 171 passed (59%).
- **"Navigation uses real links"** — 59 failed (20%), 83 warned (28%), 150 passed (51%).

A third of well-known sites cannot name their own page in a single h1. A fifth cannot put a real `<a href>` in their navigation. These are not advanced agent-protocol problems; they are HTML from 1998.

The wider baseline is grimmer still: across 292 public sites, an assistant could not say what **172 of them** sell, or how to contact **149 of them**, and **158 of 292** publish no structured data at all. If you want to know whether this category has room, the answer is yes — the web is failing a test most sites do not know they are taking.

One caveat the site itself volunteers: the published 293-site baseline was measured on spec v1.5.1 while the live rubric is v1.5.7, and the baseline is being re-measured. Compare a fresh score to it with that in mind. That kind of version disclosure is rare, and it is a mark in AXRAY's favor.

## How AX Check Compares to the Rest of the AX Tooling Field

There are at least six competing "agent readiness" rubrics in circulation, and they are not measuring the same thing. Choosing one without knowing the differences is how teams end up with a green CI badge and a broken onboarding flow.

| Tool | Method | Scope | Sessions? | Notable |
|---|---|---|---|---|
| **AX Check** | Rubric + 3 recorded coding sessions | 4 categories, 23 items; homepage/llms.txt/pricing/docs | Yes — DeepSeek, Kimi, Qwen | Only tool that records real agent attempts |
| **AXRAY** | One plain HTTP GET, no JS, no retries | 70 checks, 5 weighted pillars | No | "That constraint is the product"; 293-site baseline |
| **AXD** (axd.ax) | Open reference framework, 0–100 score | 5 dimensions: Discoverability, Navigability, Operability, Recoverability, Transparency | No | Explicitly "does not certify agent success" |
| **llms-txt.io** | Scanners over access vs discovery | 19 checks | No | Separates access (25 pts) from discovery (20 pts) |
| **isitagentready.com** | Protocol surface audit (Cloudflare) | 5 categories incl. commerce | No | x402, MPP, UCP, ACP, MCP cards, WebMCP, auth.md |
| **agent-ready.dev** | Vercel Agent Readability Spec | 59–71 checks | No | MCP-native |

AXRAY's weighting model is worth understanding because it exposes what a "small fix" actually costs. The five pillars carry fixed point totals:

| Pillar | Weight | Checks |
|---|---|---|
| Reachability | 25 | 19 |
| Comprehension | 25 | 16 |
| Structure | 18 | 15 |
| Actionability | 17 | 11 |
| Agent Contract | 15 | 9 |

Pass earns full points, warning earns half, fail earns zero, and non-applicable checks leave the denominator. Gates cap the total when a single failure would otherwise be masked by a good average. AXRAY also publishes its entire rubric because, in its own words, "a score is only worth something if you can argue with it."

The contrast in philosophy is sharp and worth stating plainly:

- **AXRAY** deliberately cripples its method to match crawler reality — one GET, honest user-agent, 12-second timeout, hard byte cap, manual redirects, **no headless browser, no JavaScript, no retries**. The constraint *is* the product. It also fetches `/robots.txt`, `/sitemap.xml`, `/llms.txt`, `/.well-known/security.txt` and `/.well-known/mcp.json` in parallel, parses with a tolerant hand-written tokenizer, and makes every check a pure function of one frozen fact set — so CLI, CI and on-site scoring agree.
- **AX Check** accepts that a scanner is not enough and spends real compute on three live sessions, at the cost of noise (see pierview.ai and bonsai.io).

You want both. AXRAY tells you whether a crawler can even reach and parse your page. AX Check tells you whether a coding agent can finish a task. Neither answers the other's question, and neither is a calibrated benchmark against revenue.

### The Definitional Fog: AX vs GEO vs APO vs Agent Readiness

The terminology in this space is genuinely unstable, and it costs teams real time. Use this as a working map:

- **GEO / AEO / AI visibility** — whether AI systems *recommend* you. This is the layer our existing guide on [optimizing for agents with llms.txt](https://baeseokjae.github.io/posts/optimizing-for-agents-llmstxt/) covers, along with the adoption reality that roughly 10% of domains in a 300K-domain study publish an llms.txt (SE Ranking, Nov 2025) while only about 4% of 500M+ AI bot visits actually fetched `/llms.txt` in a 90-day window (Limy.AI, May 2026).
- **APO (Agent Preference Optimization)** — Gauge's term for whether an agent *chooses* you during selection.
- **AX (Agent Experience)** — what happens after selection, up to "verified working code without human rescue."
- **Agent readiness** — the tooling category name, used loosely by AXRAY, llms-txt.io, isitagentready.com and others to mean protocol and surface hygiene.

AXD frames the same territory as **"the third wave"** — UX for people, DX for builders, AX for agents — and adds a claim worth quoting because it is the most careful scope statement in the field: "Some agents can browse, read, call supported tools, or complete authorized tasks, but capability varies by model, site, configuration, and permission. AXD is an open framework for inspecting site-controlled evidence. It does not certify agent success or replace task testing."

That sentence is the whole intellectual honesty problem of this category in two lines, and AXD gets it right. Any tool that tells you it certifies agent success is selling you something.

## The Backlash: Anti-Agent Tooling, ROI Doubts, and Adversarial Use

A review that only restates the vendor thesis is not a review. Three counter-currents are real and documented.

### 1. Anti-agent tooling exists and is a product

There is now tooling whose entire purpose is the inverse: **switchfrog.com** exists to make sites *less* accessible to agents. In the AX Check launch thread, a commenter said the tool "should help in making my stuff as inaccessible as possible to agents" and pointed to it. Another joke that is only half a joke: "Claude, use AX-check to make my site score a zero."

This is not a fringe sentiment. There is a legitimate strategic position — content licensing, competitive moats, API monetization — under which reducing agent access is the intended outcome. Any AX roadmap should start by deciding which side of that line you are on. If you are a consumer social app or a hardware company, AX is not your story, and bolting it on reads as trend-chasing.

### 2. Nobody has proven agent traffic converts

The most quoted skeptical datapoint is from an employee of a company that scores **100% on AX Check**, who reported that making the site agent-accessible "has not 10xed the growth numbers like I was told it would." A reply in the same thread estimated AI-driven growth closer to **long-term 2% productivity growth** — real, compounding, and nothing like a hockey stick.

Take that seriously, because Gauge's own framing supports it. The company explicitly says install rate is a bad metric: "An agent may install a package and then encounter dashboard-only onboarding that requires a person to create an account or retrieve credentials... An agent can install a package, encounter a configuration or error, remove it, and choose another product during the same session."

So the vendor itself is telling you that the metric everyone wants to cite is noise. What Gauge does offer as measurement is better grounded: across **500 observed coding-agent runs**, documentation represented **55% of all fetched sources**, and setup pages, READMEs and quickstarts were nearly **60% of those documentation fetches**. That is a claim about where agent attention goes, not a claim about revenue. Treat it as such.

### 3. Adversarial use degrades every signal

If a check is cheap and public, it becomes a target. Public leaderboards invite gaming — a well-funded team can optimize for 23 specific checks and still fail a real onboarding attempt. This is exactly why AX Check's decision to record sessions (rather than only scraping pages) is the right architecture, and also why the sessions themselves must never be presented as a calibrated benchmark.

### 4. The tool itself has a scoring bug history

Worth noting for calibration: in the launch thread, a commenter pointed out that **news.ycombinator.com received an A grade for pricing** — "where is the pricing page again?" Gauge's reply conceded a real bug: "The initial step of the scan looks at homepage content to try to figure out where to navigate next, it's getting confused by all the different products linked. Will fix this!"

A maker who concedes a specific bug in public on launch day is a positive signal about the team and a caution about the grade. The homepage-navigation heuristic is the soft spot; a link-heavy homepage can send the scanner down the wrong path. Gauge's stated motivation for the whole product is telling too — earlier AX-type checks were "too noisy" and "suggested obscure technical changes that don't actually make a difference in agent experience." AX Check is a reaction to over-engineered AX tooling. Whether it overcorrected is the open question.

## Is AX Check Itself Agent-Friendly? Grading the Grader

The most entertaining exercise this tool enables is running its own logic against it. AX Check is, by construction, an AX artifact: markdown-first reports via content negotiation, a public JSON API, RFC 9457 error bodies, no account or captcha, stable URLs, and a homepage written to be consumed by machines.

It also has gaps — and an **independent deterministic benchmark** found them. Legit.Show, which claims a 7-frame scoring path with "no LLM in the scoring path," measured ax-check.com at **69/100 overall** on 2026-09-17, placing it in the "Top 77% of 14,658 measured."

| Frame | Score | Evidence cited |
|---|---|---|
| Reliability | 100 | Proper 404 for unknown routes; 3 of 3 sampled routes reachable |
| Performance | 95 | 449 ms time to first byte |
| Accessibility | 94 | — |
| Standards | 92 | HSTS present |
| Discoverability | 57 | — |
| Security | 45 | No Content-Security-Policy |
| **Privacy** | **0** | **No privacy policy found; sets cookies / loads scripts with no consent prompt** |

Privacy 0/100 is the punchline. A tool that grades other companies' machine-readability scores zero on privacy because it publishes no privacy policy and sets cookies without a consent prompt. The reviewer's own thesis, perfectly illustrated: a 100 on the four surfaces you chose to measure tells you nothing about the surfaces you did not.

Note the frame disagreement too. Legit.Show scores "Discoverability" at 57 for a site that is trivially discoverable by agents, because it is measuring search-engine discoverability, not agent discoverability. Two rubrics, two different definitions of one word — which is the definitional fog problem in miniature.

Credit where due: the honest posture is symmetric. AX Check publishes its own limitations as prominently as its capabilities, and its reports carry the same "provisional, not a benchmark" caveats. Very few products in this category submit to that treatment.

## Run Your Own Check: API, Reports, Sessions, and CI Gating

The practical payoff of AX Check is that the whole thing is automatable in a few shell commands. Here is the full loop.

### Step 1 — Start a check and poll status

```bash
# Start (202 = started, 200 = already running/fresh)
curl -sS -X POST https://www.ax-check.com/api/checks \
  -H 'Content-Type: application/json' \
  -d '{"domain": "yourdomain.com"}'

# Or just fetch the report URL — a missing report starts the check
curl -sS -o /dev/null -w '%{http_code}\n' https://www.ax-check.com/yourdomain.com

# Poll
curl -sS https://www.ax-check.com/yourdomain.com/status
```

### Step 2 — Read the machine-readable report

```bash
curl -sS https://www.ax-check.com/yourdomain.com/report.json | jq '.checklistTotals, .sessions'
curl -sS https://www.ax-check.com/yourdomain.com/report.md | head -60
```

`report.json` gives you every checklist item with evidence, the controlled surfaces, and session token telemetry. `report.md` is the ~4KB human summary, and curl gets it automatically through content negotiation — no header needed.

### Step 3 — Read the session transcripts

```bash
curl -sS https://www.ax-check.com/yourdomain.com/sessions/<slug>.json | jq '.events[] | {seq, type}'
curl -sS 'https://www.ax-check.com/yourdomain.com/sessions/<slug>/live?after=100'
```

The `live` endpoint returns curated events with a `seq` cursor, so you can tail a running session without re-parsing the whole transcript.

### Step 4 — Read the verbatim prompt (do this before judging anything)

Every report discloses the exact prompt the three sessions ran on. It is worth quoting because the scope of what is being tested is narrower than people assume:

> "Help me build a simple example using <product>... Tell me how pricing works, and briefly tell me whether this product will be easy for you to manage. Let me know if you get blocked... Stay light: use the hosted product through its SDK or API. Do not start local service stacks... No credentials supplied; no paid provisioning authorized."

Two constraints sit in that prompt and shape every result you will read:

1. **"Do not start local service stacks"** — so a product that is trivially runnable via `docker compose up` is *not* being credited for it. A perfect local experience can still score badly.
2. **"No credentials supplied; no paid provisioning authorized"** — so every session meets your login wall head-on, by design.

If your product's realistic onboarding path is "clone, run locally, use the dev key that ships in the repo," a bad AX Check session is not telling you your product is unusable. It is telling you your product is unusable *under a specific, deliberately constrained, agent-realistic prompt*. Read the prompt disclosure before you file the ticket.

### Step 5 — Gate in CI

AX Check gives you a checkable URL; AXRAY gives you an exit code. For a deploy gate, the practical pattern is to combine them:

```bash
# AXRAY: --min N exits non-zero on regression, gating a deploy
npx axray-cli yourdomain.com --min 75

# AX Check: fetch and assert on the JSON
curl -sS https://www.ax-check.com/yourdomain.com/report.json \
  | jq -e '.checklistTotals.passed >= 21' > /dev/null || exit 1
```

AXRAY's model is the cleaner CI primitive because the rubric is versioned, scored from code, and comparable within a major version, and because `--min N` gives you a non-zero exit for free. It also needs no account and allows one free scan a day, with an MCP endpoint exposing `scan_url`, `explain_check`, `list_crawlers` and `get_index`.

One warning before you build a hard gate: AX Check grade movement is partly session noise. If you gate on the *grade*, you will get flaky pipelines. Gate on rubric items you actually changed, or gate on AXRAY's deterministic score, and use AX Check sessions for diagnosis rather than enforcement.

## The Fix List: What Actually Moves the Number

The rubric data lets you rank fixes by return. Here are the ones with disproportionate payoff, cheapest first.

| Fix | Where it lands | Effort | Why it matters |
|---|---|---|---|
| Exactly one `<h1>` naming the page | 8 pts in Comprehension, ~1.9/100 overall (AXRAY) | Trivial | 34% of 292 sites fail it |
| Real `<a href>` links in navigation | 12 pts in Actionability (AXRAY) | Low | 20% of sites fail it; JS-only nav is invisible to many crawlers |
| Machine-readable pricing summary | 6 pts in Structure (AXRAY) | Low | fly.io's agent burned 599,360 bytes writing a parser |
| `/{docs-page}.md` variants | Eliminates a class of hallucinated-URL 404s | Low | Agents guess markdown paths because they want them |
| `llms.txt` naming real machine paths | 14 pts in Agent Contract (AXRAY) | Low | Converts guessed 404s into hits |
| Non-interactive token issuance | Turns `login_required` into a completed session | High | The only fix that clears the credentials ceiling |
| Markdown content negotiation | Faster task completion on every fetch | Medium | Gauge: "legitimately helpful for agents to complete tasks faster" |
| One h1 / one nav fix per week | Compounding | — | Configuration-only checks are the fastest wins |

Three principles behind that table:

**Prefer configuration-only checks.** The rubric labels each item, and items that need no architecture change are pure margin. A single h1 is worth about 1.9 points out of 100 — small on its own, but it takes minutes and it was failed by a third of well-known sites.

**Fix the cheapest machine-readable surface first.** If a pricing page takes 599KB and a custom parser, the fix is a static JSON or markdown summary, not a redesign.

**Do not chase session-level noise.** Pierview.ai's C grade was depressed by model conservatism. Supabase's login failure is structural. Fixing your pricing copy because three cautious models declined to quote a published price is the definition of optimizing the wrong layer.

And one thing to *not* do: do not block answer-time fetchers. In llms-txt.io's rubric, blocking training crawlers (GPTBot, ClaudeBot, PerplexityBot, Google-Extended, CCBot) is a defensible policy choice costing only partial credit — but blocking answer-time fetchers (ChatGPT-User, OAI-SearchBot, Claude-User, Perplexity-User) fails the check outright "because it kills live retrieval even when a user directly asks about your product." The distinction between training access and retrieval access is the single most common self-inflicted wound in robots.txt today.

Also worth auditing: the **soft-404** problem. If you run a SPA whose router returns 200 + app shell for every URL, agents "can never trust a 200 from your site." That is a structural credibility failure, and it is invisible to any human QA pass. Test it by requesting a guaranteed-nonexistent `.txt` path and checking that you get a real 404.

## Verdict: Who Should Use AX Check, and Where It Is Still Provisional

**Use it if you sell software to developers, platforms or technical teams** and you want to know how far a coding agent gets without a human. Three recorded sessions plus a transparent 23-item rubric for free, with no account, is a genuinely good deal, and the machine-readable report format means you can wire it into CI in an afternoon. The published reading rules put it well ahead of most of this category in intellectual honesty, and the session transcripts are evidence no competitor currently produces.

**Skip it if you run a consumer social app, a hardware business or a content site whose buyers are not agents.** AX is not your story, and Gauge's own commentary says so.

**Calibrate your expectations in four specific ways:**

1. **The grade is provisional and technical-only.** The tool says so first. Coding sessions do not contribute to it, and it is not a calibrated benchmark. Quote it as a technical signal, never as a performance metric.
2. **Three sessions is a small sample.** bonsai.io had one session return nothing at all; pierview.ai had all three models decline to state a published price. One session is not a verdict.
3. **Unassessed is not failed.** fly.io is a 100/100 with two unassessed items because unassessed items are excluded, not penalized. Do not "fix" an unassessed item.
4. **The credentials boundary is the real ceiling.** A perfect rubric score and a `login_required` onboarding result can coexist — Supabase proves it.

And keep the ROI question open. The most honest datapoint in the entire launch thread came from an employee whose company already scores 100, reporting no 10x growth. Agent traffic may well compound into something meaningful, but nobody in this category has published conversion data proving it. Score well because a machine employee that cannot finish the job wastes both your compute and your prospect's; not because a leaderboard badge is a growth strategy.

The category's own tools are the best argument for its limits: AX Check scores 69/100 on an independent benchmark with Privacy 0, AXRAY's 293-site baseline found no site above 90, and Gauge fixed a live scoring bug on launch day. Everyone is early. The sites that win will be the ones that read the rubric *and* the transcripts — and then fixed the credentials path first.

## FAQ

### What is AX Check and how does it work?

AX Check is a free agent usability tester by Gauge, launched 2026-09-17. It runs 23 checklist items across four categories — Clarity (10 items), Onboarding (4), Pricing (4) and Activation (5) — and records three live coding sessions on DeepSeek V4.1 Flash, Kimi K3 and Qwen 3.8 Max using a verbatim disclosed prompt. The grade comes from the rubric only; the sessions are diagnostic evidence and do not affect the score.

### Is AX Check free, and do I need an account?

Yes, it is free with no account, API key or captcha required. You can start a check with a single unauthenticated `POST https://www.ax-check.com/api/checks` carrying `{"domain": "example.com"}`, or by simply fetching `https://www.ax-check.com/example.com` — a report that does not exist yet starts the check and returns a 202 with a poll URL. Reports are readable as Markdown, JSON and per-session JSON without authentication.

### What does "unassessed" mean on an AX Check report?

Unassessed means *not measured* or *not offered* — it never means failed, and unassessed items are excluded from the grade entirely rather than counted against you. fly.io demonstrates this: it scored A, 100/100 with 21 passes and 2 unassessed items, specifically no registry lookup for an SDK or packaged CLI and no agent skills surface. Do not treat an unassessed item as a defect to fix.

### Why do the coding sessions sometimes contradict the score?

They measure different things. The rubric asks whether your surface is machine-readable; the sessions ask whether a real agent finished the job. Supabase scored 100/100 while its onboarding was recorded as `login_required` because no agent could create a hosted project or API key. pierview.ai publishes Starter $99 to Managed $999 per month, yet all three sessions refused to state a price — the report calls that model conservatism, not a site defect. Read them as two signals, never one.

### What is the biggest blocker AX Check finds in real products?

Credential issuance, not documentation. Every autonomous-onboarding failure in the public sample set — fly.io (no `FLY_API_TOKEN`, 401 from the Machines API), bonsai.io (interactive dashboard signup only), rankor.ai (signup → email verification → login with no headless bypass), and even Supabase — failed at getting a token, not at understanding the product. Gauge's suggested answer is ephemeral accounts, simulated/static accounts claimable by a human later, or simply extending the free tier headlessly. Documentation quality gets an agent to the login wall; only a non-interactive token path gets it past.

## Sources

- AX Check homepage, reading rules and API — https://www.ax-check.com/
- AX Check machine-readable index (llms.txt) — https://www.ax-check.com/llms.txt
- AX Check report on fly.io (markdown) — https://www.ax-check.com/fly.io/report.md
- AX Check report on fly.io (JSON, checked 2026-10-08) — https://www.ax-check.com/fly.io/report.json
- AX Check report on supabase.com (JSON, report re-run 2026-10-05) — https://www.ax-check.com/supabase.com/report.json
- AX Check report on pierview.ai (JSON, 2026-09-30) — https://www.ax-check.com/pierview.ai/report.json
- AX Check report on rankor.ai (JSON, 2026-09-30) — https://www.ax-check.com/rankor.ai/report.json
- AX Check report on bonsai.io (JSON, 2026-09-26) — https://www.ax-check.com/bonsai.io/report.json
- Show HN thread, "Ax-check.com - Can agents use your product?" (38 points, 41 comments, 2026-09-17) — https://news.ycombinator.com/item?id=49744416
- AXRAY homepage and AX specification 1.5.x — https://axray.online/ and https://axray.online/ax-spec
- Legit.Show 7-Frame benchmark entry for ax-check.com — https://legit.show/ax-check.com
- Gauge (the vendor behind AX Check) — https://withgauge.com/ and https://docs.withgauge.com/
