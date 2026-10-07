---
title: "Coasty Review 2026: A Computer Use Agent API That Sells the Harness, Not the Model"
date: 2026-10-01T09:01:29+00:00
tags:
  - computer use agent api
  - coasty api review 2026
  - coasty api pricing per predict call
  - coasty os-world benchmark verified
  - coasty vs browser-use vs skyvern
  - computer use agent api comparison 2026
  - coasty mcp server setup claude cursor
  - byok computer use agent api
  - sandbox api keys computer use ci
  - computer use api for legacy desktop apps
  - predict sessions runs tasks workflows computer use api
  - coasty pricing per agent step
  - computer use api vs raw claude computer use tool
  - hosted computer use api vs e2b browserbase
  - coasty hipaa soc2 computer use agent
description: "Coasty review 2026: the computer use agent API sells a managed harness, not a model — plus what its 85.6% OSWorld claim actually verifies."
draft: false
cover:
  image: "/images/coasty-an-api-for-computer-use-agents.png"
  alt: "Coasty Review 2026: A Computer Use Agent API That Sells the Harness, Not the Model"
  relative: false
schema: "schema-coasty-an-api-for-computer-use-agents"
---

Coasty is a hosted computer use agent API: you send a screenshot and a plain-language instruction, and it returns typed mouse and keyboard actions, backed by managed cloud desktops, retries, schedules, and an audit trail. It sells the harness around a vision model, not the model itself — and its own benchmark numbers verify unevenly.

That second sentence is the entire review. Coasty is a YC S26 company that launched on Hacker News in July 2026 as "an API for computer-use agents," and the product it actually ships is not a smarter vision model. It is the operational layer that every team building on raw computer-use tool calls eventually has to write themselves: VM lifecycle, the screenshot-action loop, action execution, retries, human approval gates, scheduling, and a per-action evidence trail.

Judged as that harness, it is one of the more complete offerings in the category, with a genuinely useful free sandbox tier and a pricing model that is far more workload-dependent than the headline number suggests. Judged on the number its own marketing leads with — 82% to 85.6% on OSWorld — the evidence is vendor-published, independently unlisted, and measured on a benchmark that a newer, harder version has already rendered partly obsolete.

## What Coasty's computer-use API actually is — and what it isn't?

The core contract is deliberately boring, and that is a feature. Per Coasty's own API reference, "The Coasty Computer Use API gives your code the ability to see a screen and act on it." You post a screenshot plus an instruction; the model returns typed actions — clicks, keystrokes, scrolls, drags — with pixel coordinates; your program executes them and loops. There is no SDK to install and no websocket requirement for the core endpoints. It is plain REST at `https://coasty.ai/v1`, authenticated with an `X-API-Key` header.

That last detail is a real first-day trap: a meaningful share of the 401 `INVALID_API_KEY` reports come from pasting the literal string `Bearer` inside the `X-API-Key` value, because developers assume every modern API wants an Authorization header. Coasty accepts `Authorization: Bearer <key>` too, but the canonical header is `X-API-Key`, and mixing the two styles is the fastest way to get a key that looks correct and authenticates as nothing.

What Coasty is **not** is equally important. It is not a model provider. Anthropic's computer use documentation frames computer use as a model-level tool — "Give Claude screenshot, mouse, and keyboard control" — where you supply the loop, the machine, the execution, and the storage. OpenAI documents computer use the same way: the model returns actions and your application runs them. Both are primitives. Neither ships managed desktops, per-step price cards, workflow orchestration, compliance trails, or webhook triggers.

Coasty's entire commercial argument is that gap. The model that can click is increasingly a commodity; the loop that clicks reliably, recovers from a mis-click, pauses before sending a payment, and records a screenshot behind every action is not. That is the thing you are buying, and it is the thing to evaluate — not the benchmark slide.

There is one more framing to get right, because the marketing blurs it. Coasty's API page leads with "#1 Computer-Use AI Agent | 82% OSWorld Benchmark" and "No selectors. No DOM parsing. No brittle XPath. Just vision." Read carefully: the benchmark claim is about a *model* (their in-house one), while the product you buy is the *harness*. Those are different assets with different evidence, and conflating them is how buyers end up surprised in month two.

## What does the API surface actually cover?

The published surface is larger than the "one call, four lines" pitch suggests. The OpenAPI 3.1 spec at `coasty.ai/openapi.json` — fetched and counted directly, not taken on faith — declares 65 paths and 81 operations. The spec's own tags group those into eight areas — machines, workflows, schedules, runs, keys, sessions, predict, and triggers — and they layer in a specific order of complexity, and knowing which layer you actually need is most of the integration decision.

| Layer | Endpoint | State | What it is for |
|---|---|---|---|
| Single-step decision | `POST /v1/predict` | Stateless | The workhorse: screenshot + instruction in, typed action out |
| Coordinates | `POST /v1/ground` | Stateless | Screenshot + element description in, x/y out |
| Deterministic parsing | `POST /v1/parse` | Stateless | Free pyautogui-style action parsing, no LLM cost |
| Stateful loop | `POST /v1/sessions` | Stateful | Server holds the loop context across steps |
| Agent run | `/v1/runs` | Stateful | The agent drives a task on a machine to completion |
| Fire-and-forget | `POST /v1/tasks` | Stateful | Provision, run, verify, clean up — one submission |
| Orchestration | `/v1/workflows` | Stateful | Branching and looping multi-step automations |
| Infrastructure | `/v1/machines` | Managed | Provision, start, stop, snapshot, connect, browse, terminal, files |
| Triggers | `/v1/schedules` | Managed | Cron and one-shot schedules, HMAC-signed webhook triggers |

Two caveats about that table. It lists nine of the spec's surfaces, not all of them: the machine-level control routes — `/v1/machines/{id}/actions`, `/actions/batch`, `/connection`, and `/screenshot`, with run evidence at `/v1/runs/{id}/screenshots` and `/v1/runs/{id}/log` — are what actually execute the clicks, and they carry their own scopes (`actions:exec`, `terminal:exec`, `files:read|write`, `browser:execute`). And two layers deserve special attention for anyone evaluating this as production infrastructure.

The first is `/v1/schedules`. Cron and one-shot schedules plus HMAC-signed webhook triggers turn the API from "a thing my application calls" into "a thing that runs when something else happens." Schedule *creation* is free (behind a 20-credit, $0.20 developer-wallet gate) and the per-fire cost is zero, but execution on a non-Unlimited account then bills the consumer subscription-credit balance at 10 credits per minute with a 20-credit minimum to start; BYOK bypasses those meters and debits zero platform credits. Schedules created through the API appear in the dashboard automatically, which sounds trivial until you have run a platform where programmatically created jobs are invisible to operators.

The second is `/v1/tasks`, and it carries a caveat that is easy to miss in the docs. Task runs require `runs:read`/`runs:write` scopes and support a hard `max_steps` (default 150, ceiling 1,000), a `deadline_seconds` wall, an `action_policy` whose cumulative `max_actions` is inherited by nested delegation, and an `on_awaiting_human` behavior of pause, fail, or cancel. But `POST /v1/tasks` deliberately makes human takeover impossible: it suppresses `awaiting_human` entirely and treats CAPTCHAs and email confirmations as part of the task. If your workflow has an irreversible step — a payment, a message send, a form submission — do not route it through `/v1/tasks`. Use `/v1/runs` or `/v1/workflows`, where the human gate still exists.

That distinction is the most operationally important sentence in Coasty's documentation, and it is buried.

### Can you test any of this before paying?

Yes, and this is a genuinely strong part of the offering. Sandbox keys run against mock VMs, return the same request and response shapes as live keys, complete in under 50 milliseconds, and bill zero credits. For CI pipelines that need to assert "our action executor handles a typed click response," that is a complete, free test path — and it exists before you ever connect a credit card.

## What does a computer use agent API actually cost?

The answer to "how much is a computer use agent API" is the same for Coasty as for the category: the per-call number is the smallest part of the bill. Coasty's pricing page advertises `$0.05` per `/v1/predict` and a `$99` flat "Unlimited" plan, and both numbers are real. Neither is the number your invoice will land on.

Start with the unit. One Coasty credit equals one cent. The documented metered rates are:

| Endpoint | Credits | USD | Notes |
|---|---|---|---|
| `POST /v1/predict` | 5 | $0.05 | Base rate; surcharges apply |
| `POST /v1/sessions` (open) | 10 | $0.10 | Fixed cost to open a stateful session |
| `POST /v1/sessions` (per step) | 4 | $0.04 | Each subsequent stateful predict |
| `POST /v1/ground` | 3 | $0.03 | Coordinate resolution |
| `POST /v1/parse` | 0 | Free | Deterministic; no LLM cost |
| Agent run (per completed step) | 5 | $0.05 | v3/v4/v5 engines |
| Agent run, legacy v1 engine | 8 | $0.08 | Per completed step on the v1 engine |

Now the part the pricing page leaves to the developer documentation: `$0.05` is a **base** rate, and the documented surcharges stack on top of it. Adding **+2 credits** per provider-visible prior trajectory screenshot, **+1 credit** per HD image larger than 1280x720, **+3 credits** on the legacy v1 engine (v3, v4, and v5 engines add zero), and **+1 credit** when `system_prompt` plus `instructions` exceeds 500 characters. Real predict cost is therefore a function of how much history you send, how large your screenshots are, which engine you pinned, and how verbose your prompt is — four variables, all under your control, none reflected in the headline price.

Then multiply. A run at the default `max_steps` of 150 steps at $0.05 per step is roughly **$7.50 in model charges per task** (scheduled execution is metered differently — 10 credits per minute of runtime rather than per step). Managed machine runtime is comparatively cheap — $0.05/hour for Linux, $0.09/hour for Windows while running, $0.01/hour stopped, and $0.01 per snapshot. For a 20-minute Linux task, machine time is under two cents against $7.50 of loop cost. The inversion matters: **cheap VM, expensive loop.** For context, E2B's Hobby tier is free with a $100 one-time usage credit and 20 concurrent sandboxes (Pro $150/month plus per-second usage, Enterprise from $3,000/month), and Browserbase's Developer tier is $20/month for 25 concurrent browsers and 100 browser hours before metered overage at $0.12/browser-hour. Compute is not where computer-use spend concentrates, at any vendor.

BYOK changes the arithmetic more than anything else on the pricing page. Coasty's `PUT /v1/llm/keys/{provider}` lets you route the entire harness — worker, grounding, code agent, compaction — through your own Anthropic or OpenAI account. LLM steps then bill **$0 in Coasty credits** while your provider bills your key directly, and machine runtime remains the only Coasty line item. If you already have negotiated model pricing or committed spend, this is the single highest-leverage cost control in the product.

Finally, separate the two wallets, because this is where buyers get confused. The subscription tiers — Starter at $19/month (200 credits, 1 machine, 3 swarm agents, 3 schedules), Plus at $50/month (600 credits, 2 machines, 6 agents, 10 schedules), and Unlimited at $99/month (unlimited credits, 2 machines, 5 agents, 10 schedules) — govern a **consumer credit balance**. Boost packs (150 credits/$19, 500/$49, 1,200/$99) require a paid subscription. The developer API wallet is metered separately. The `$99 Unlimited` plan does not make your API calls free, and a reader who assumes otherwise will discover the gap on their first production run.

## Does Coasty really score 82–85.6% on OSWorld?

This is the claim the marketing leads with, and it needs unpacking rather than repeating.

What Coasty says: its in-house model scores **85.6%** on OSWorld — with results and traces published at `github.com/coasty-ai/coasty-osworld` — and its public model is **82.81%** on the official OSWorld leaderboard (the founder's HN comment writes that figure as "82.8%"). The vendor's benchmark blog makes a stronger version of the argument, claiming 82% against "OpenAI's Operator scored 38% on OSWorld" and "Anthropic's Computer Use barely beats it at 22%." UiPath's Screen Agent — which was ranked #1 on OSWorld-Verified and is powered by Claude Opus 4.5 — does not appear in that post at all, which is a convenient omission for a page arguing that Anthropic's approach does not work.

Two specific problems appear in that comparison. First, the "22%" figure is the score from Anthropic's **2024 launch** of computer use, not a current Claude model score. Juxtaposing a two-year-old launch number against a present-day result is a rhetorical move, not a benchmark comparison — and the independent leaderboard that lists Claude Sonnet 4.6 at 72.5% is a much less flattering contrast. Second, the numbers mix sources: some are self-reported by Coasty, some are from the official leaderboard, and the reader is invited to treat them as one table.

What independent evaluation says: the awesomeagents.ai computer-use leaderboard (updated March 2026) lists Claude Opus 4.6 at **72.7%**, Claude Sonnet 4.6 at **72.5%**, and Qwen3 VL 235B at **66.7%**, against a human baseline of **72.4%** — and **Coasty does not appear in the independently evaluated table at all**. The leaderboard explicitly separates entries "assessed by the research team" from those "self-reported by provider." GPT-5.4's 75.0% sits in the self-reported column. Coasty's number is not even in that column, because it is on Coasty's own site.

Then there is the verification path the vendor points to. Coasty's "independently verified" leaderboard URL is `osworld-v1.xlang.ai`. A direct fetch on 2026-10-01, and again on 2026-10-07, returned HTTP 200 and ~153 KB of HTML containing **zero occurrences of "Coasty" or "82.81"**, because the "OSWorld-Verified Results" block renders client-side behind a "Loading verified benchmark data..." placeholder. A reviewer can confirm the public trace repository; they cannot confirm the 82.81% on the page the vendor cites for verification.

The honest framing for a buyer is therefore narrow and precise: **best-in-class on OSWorld-Verified as self-reported, unlisted on independent evaluation.** That is a materially weaker claim than "82% OSWorld," and it is still not a bad one — 82% would put a Coasty-class model above every independently assessed system in March 2026.

### Why is OSWorld the wrong test anyway?

Because a newer version of it already collapsed the field. OSWorld 2.0, revised July 2026, contains 108 long-horizon tasks with a median duration of roughly **1.6 human hours each**. On it, the best agent reaches only **20.6% binary completion** and requires approximately **318 tool calls per task** — about 10.6 times the tool-call volume of the original benchmark. Meanwhile third-party trackers of OSWorld-Verified's September 2026 board put self-reported scores on top (Qwen3.8-Max at 86.1%, Claude Mythos Preview at 85.4%), labelled self-reported by Alibaba and Anthropic respectively.

The implication for procurement is direct. A computer-use API marketed as "85% reliable" is quoting a micro-task suite where each task is a few minutes of UI work. Your workflow is not that. If you are automating an insurance portal claim, a multi-app reimbursement, or a legacy mainframe screen flow, the number that predicts your outcome is the long-horizon one — and nobody is near 85% there. Benchmark against your own 20 tasks, on your own screens, with your own failure tolerance.

## Coasty vs browser-use, Skyvern, Stagehand, and raw Claude computer use

The category splits cleanly along one axis, and it is not accuracy. It is who owns the loop.

| Option | Type | Language / interface | You own | Evidence |
|---|---|---|---|---|
| Coasty | Hosted API | REST + MCP, any stack | Task design and policy | 82–85.6% OSWorld, self-reported |
| Skyvern | Hosted API | REST, computer vision | Task design | Planner-Actor-Validator architecture |
| browser-use | Open-source library | Python, DOM-first | The loop, retries, hosting | 89.1% WebVoyager (586 live tasks) |
| Stagehand | Open-source library | TypeScript on Playwright | The loop, caching, hosting | ~75% agent primitive in third-party comparison |
| Claude computer use | Model tool | Anthropic API | Everything: loop, VM, storage, audit | Independently assessed ~72.5–72.7% OSWorld |
| OpenAI computer use | Model tool | OpenAI API | Everything: loop, VM, storage, audit | Self-reported 75.0% OSWorld-Verified |

Read the browser-use row twice. An MIT-licensed Python library that you host yourself scores **89.1% on WebVoyager** across 586 live web tasks — higher than every OSWorld figure in this article, though the benchmarks are not comparable and WebVoyager is exclusively web work. The point is not that browser-use is better than Coasty. The point is that if your automation lives entirely inside a browser on sites you can reach directly, **DOM-first open source is already competitive**, and it costs you LLM tokens and engineering time instead of credits and subscription fees.

Stagehand occupies the pragmatic middle: TypeScript methods layered on Playwright, with action caching to cut repeat-run cost. It keeps your existing Playwright test infrastructure alive, which for teams with a mature browser-testing practice is worth more than a benchmark.

Where hosted APIs genuinely win is everywhere the DOM is not. Legacy insurance portals, mainframe green screens, 20-year-old desktop applications, Citrix-published internal tools, and thick-client Windows software have no reliable DOM and no clean API. Vision-driven control is not a preference there; it is the only path. That is precisely the case independent reviewers identify as Coasty's strongest: MakerStack's July 2026 review scores it **7.5/10**, calls it "the most credible RPA replacement of the year, with self-healing vision automation and a real free tier," and then draws the boundary the vendor would rather you not read — "skip Coasty if your systems already have clean APIs," because code will be cheaper and more reliable.

Both of those statements are correct, and they define the buying decision more sharply than any benchmark table. One caveat on that review: it repeats the vendor's 82% OSWorld figure uncritically and the site monetises placements, so treat its 7.5/10 as a product opinion rather than an evaluation.

## Security, governance, and lock-in

Coasty's security model has more substance than most in this category, and one genuinely sharp edge.

The substance: per-session VM isolation, deny-by-default typed actions where `action_type` plus params are authoritative and raw code is never executed, human-in-the-loop approval gates before irreversible steps, and a screenshot behind every action for audit. Notably absent is any CAPTCHA-solver or proxy-evasion marketing — a restraint that matters if you are buying this for a regulated workflow, because vendors that sell evasion rarely survive compliance review. The docs also carry the retention mechanics (AES-256-GCM screenshot storage decisions, account-lifetime audit rows), which is the level of detail an enterprise reviewer actually needs.

The sharp edge: a key minted without an explicit scopes array receives **20 default scopes**, and exactly three of them are opt-in privilege escalations — `connection:read`, which returns plaintext SSH keys and VNC passwords; `browser:execute`, which permits arbitrary JavaScript inside the VM browser; and `keys`, which mints new API keys. The containment rule is sound — a key can never mint a key holding scopes it does not itself hold — but the practical consequence is that a CI key with default scopes is a liability you did not consciously accept. Audit every key's scope list before it goes in a pipeline.

Two claims deserve attribution rather than acceptance. Coasty's compliance position — SOC 2 and HIPAA, with zero-data-retention via an enterprise platform — was asserted by the founder in the Hacker News launch thread (`news.ycombinator.com/item?id=48922706`, 44 points, 26 comments, posted 2026-07-15). The public developer documentation describes retention and encryption mechanics but links no SOC 2 report and no HIPAA BAA. Founder-stated is not the same as artifact-verified; ask for the report during procurement.

The same launch thread contains the review's most valuable primary source — but attribute it precisely, because two different people are talking. The limitation comes from a practitioner in the thread (HN user `sneefle`, 2026-07-16): a React controlled select "can render the right value after a click while the framework's internal state never updated, so every pixel says done and the submitted payload says null." The founder's reply (2026-07-17) concedes the point and describes the counter — layered, outcome-based checks against source data and expected invariants: "A UI saying 'success' is weak evidence that the underlying work is correct." That is the right architectural answer, and it is also an admission that per-step visual confirmation is not sufficient evidence of completion. Build your verification on outcomes, not on what the screen shows.

On lock-in, the answer splits cleanly. The protocol layer is portable: plain REST, an OpenAPI 3.1 spec, no SDK lock-in, no browser driver to maintain, and BYOK covering the whole harness. You can lift your integration and point it elsewhere. The value layer is not portable: the 1,000+ OAuth-secured applications and 20,000+ individual tools reachable through Composio, the accumulated audit trail, and the schedule/workflow configuration all stay behind. And the governance signal is mixed — independent API-readiness scoring gives Coasty a **Kin Score of 59.3/100** as of 2026-10-04 (Discoverability 64.3, Contract Quality 61.6, Access Clarity 76.3; the first score, dated 2026-08-29, was 59.6) but a **Contract Governance facet of 4.5/100**, meaning a good spec with weak deprecation and versioning discipline. Watch the changelog yourself; do not assume the versioning will be gentle.

### Is the open-source story what it looks like?

Not quite. The GitHub footprint is thin relative to the marketing. As of 2026-10-07, the `coasty-ai` organization lists `coasty-osworld` (4 stars, OSWorld results and traces, last pushed 2026-06-28), `llmhub-api` (3 stars), `computer-use-cookbook` (8 stars), and `open-cowork` (145 stars, MIT) — the last being an unrelated open-source Claude Co-Work alternative. The published OSWorld artifacts are per-domain result dumps (chrome, gimp, libreoffice variants, multi_apps, os, thunderbird, vlc, vs_code). There is **no open-source server for the `/v1` API**. The traces are published; the product is not open source, and treating the repository presence as a portability guarantee would be a mistake.

### What about the MCP path?

For coding agents, this is the intended integration. Coasty's MCP server (`npx -y @coasty/mcp`) works in Claude Desktop, Claude Code, Cursor, Windsurf, and VS Code Copilot Agent. Count its tools carefully, though: the package's own README documents **24 tools across 4 groups + 2 prompts** (Predict, Machines, Schedules, Account), while the company's site and its API-directory listing say "26 tools" across five groups including "discovery" — a group that does not exist in the README's tool listing. The remote endpoint is listed as `api.coasty.ai/mcp`; the OpenAPI spec's own MCP entry points at `coasty.ai/mcp`, which returned 404 to a direct fetch. If you are already working inside one of those clients, MCP is a materially faster path to a working prototype than writing REST calls by hand — and it is the route a third-party setup writeup recommends as step three.

## When does a computer use agent API earn its place?

Five questions decide it, and none of them are about benchmark points.

**Does the target system have a clean API?** If yes, stop. Write the integration. Every reviewer of this category, including Coasty's own favorable one, says the same thing: a documented endpoint is cheaper, faster, more reliable, and easier to audit than a vision model clicking through a UI. The vision layer is for the systems that have no endpoint — legacy portals, desktop thick clients, mainframe screens, internal tools nobody will ever expose.

**Is the work long-horizon or short-horizon?** Short tasks that take a person two minutes are where computer-use APIs perform closest to their marketing. Long multi-hour workflows are where the 20.6% OSWorld 2.0 completion rate lives. Price the failure rate into your labor budget: a 20% completion rate on a 318-step task is not a tool, it is an experiment.

**Can you gate the irreversible steps?** If your workflow sends money, sends messages, or submits filings, you need `awaiting_human`, which means `/v1/runs` or `/v1/workflows` — not `/v1/tasks`. If your process cannot tolerate a pause, the honest answer is that this category, not just Coasty, is not ready for that step.

**What does the full invoice look like?** Not $0.05 per predict. It is $7.50-ish of model charges for a 150-step run, plus cents of machine time, plus the probability that 30% of runs need a human to finish. Model the whole thing before you commit, and bring BYOK keys if you already have provider spend.

**Will you be on Coasty in two years?** The Kin Score's 4.5/100 contract-governance facet and the thin public repo both point the same direction: keep your integration thin, keep your task definitions in your own repository, and use BYOK so your model relationship is not mediated. Lock-in here is optional if you design for it.

### Verdict

Coasty is a legitimate, unusually complete computer-use harness with a real free sandbox tier, a portable REST surface, BYOK across the whole pipeline, sane security defaults, and an honest operational boundary its own reviewers state plainly. Independent review puts it at 7.5/10, and that feels right.

Judge it on the harness and it earns its place in a stack automating software that has no API. Judge it on the 85.6% and you will be buying a number on a benchmark that independent evaluators do not list, on a task distribution that a newer benchmark has already shown frontier agents fail at four times out of five.

Buy the harness. Verify against your own twenty tasks. Ignore the leaderboard.

## FAQ

**Is Coasty free to try?**

Yes. Sandbox API keys run against mock VMs, return the same request and response shapes as live keys, respond in under 50 milliseconds, and bill zero credits. You can build and run a CI suite against them before ever entering payment details. Paid tiers start at $19/month (Starter, 200 credits) and run to $99/month (Unlimited, unlimited credits). `POST /v1/parse` is also permanently free and deterministic, since it performs no LLM inference.

**How much does one Coasty API call actually cost?**

The advertised rate is 5 credits, or $0.05, per `POST /v1/predict`. Documented surcharges then stack: +2 credits per provider-visible prior trajectory screenshot, +1 credit per HD image above 1280x720, +1 credit when the system prompt plus instructions exceed 500 characters, and +3 credits if you pin the legacy v1 engine. Agent runs bill $0.05 per completed step on the current engine and $0.08 on legacy v1. A default 150-step run is therefore roughly $7.50 in model charges, against machine runtime of $0.05/hour for Linux.

**Does BYOK really make Coasty free?**

No, but it removes the largest line item. `PUT /v1/llm/keys/{provider}` routes the entire harness — worker, grounding, code agent, compaction — through your own Anthropic or OpenAI account, so LLM steps bill $0 in Coasty credits while your provider charges your key directly. Managed machine runtime remains billable at $0.05/hour (Linux) or $0.09/hour (Windows) running, $0.01/hour stopped. You are trading Coasty credits for your own provider pricing, not eliminating cost.

**Is the 85.6% OSWorld score independently verified?**

No. Coasty's in-house model figure of 85.6% and its public model figure of 82.81% are both vendor-published; the public traces live at `github.com/coasty-ai/coasty-osworld`. The independent computer-use leaderboard as of March 2026 lists Claude Opus 4.6 at 72.7% and Claude Sonnet 4.6 at 72.5% against a 72.4% human baseline, and does not list Coasty at all. The vendor's cited verification URL, `osworld-v1.xlang.ai`, returned zero occurrences of "Coasty" or "82.81" in direct fetches on 2026-10-01 and 2026-10-07 because its results table loads client-side.

**Can Coasty automate anything, or are there limits?**

Two limits are structural. First, `/v1/tasks` deliberately suppresses `awaiting_human` and treats CAPTCHAs and email confirmations as part of the task, so it cannot be used for workflows requiring human approval before an irreversible step — use `/v1/runs` or `/v1/workflows` instead, where pause, fail, and cancel behaviors exist. Second, vision-based control is the wrong tool wherever a clean API exists; that is the vendor's own reviewers' conclusion, and it is correct. Coasty's strongest fit is legacy and desktop software with no API, on tasks short enough that failure is recoverable.

## Sources and check times

Every figure above was checked against the source listed beside it; the times are the review window for
this article (2026-10-07, UTC).

- Coasty public OpenAPI 3.1 specification — https://coasty.ai/openapi.json (paths, operations, scopes,
  `max_steps`, `max_actions`, `/v1/tasks` behaviour, BYOK wording)
- Coasty published pricing document — https://coasty.ai/api/pricing (credit rates, surcharges, run-step
  and machine rates, subscription and boost tiers, `testKeysBill: false`, schedule meters)
- Coasty's MCP integration guide — https://coasty.ai/blog/drive-coasty-from-cursor-and-claude-with-mcp
- First-party MCP server package and tool list — https://www.npmjs.com/package/@coasty/mcp
- Launch HN thread with the founder's SOC 2/HIPAA, 85.6% and verification answers —
  https://news.ycombinator.com/item?id=48922706
- Published OSWorld results and traces — https://github.com/coasty-ai/coasty-osworld
- The vendor's own OSWorld benchmark posts — https://coasty.ai/blog/osworld-benchmark-2026-results-human-vs-ai-computer-use
  and https://coasty.ai/blog/osworld-benchmark-results-2026-ai-computer-use-agents-ranked
- Independent OSWorld / OSWorld-Verified leaderboard — https://awesomeagents.ai/leaderboards/computer-use-leaderboard
- OSWorld 2.0 paper — https://arxiv.org/abs/2606.29537
- APIs.io Kin Score for Coasty — https://apis.io/badge/coasty
- MakerStack review — https://makerstack.co/reviews/coasty-review
- Anthropic's computer use tool documentation — https://docs.claude.com/en/docs/agents-and-tools/computer-use
- Anthropic's original computer use announcement (the 14.9% figure) —
  https://www.anthropic.com/news/developing-computer-use
- OpenAI's computer use tool guide — https://developers.openai.com/api/docs/guides/tools-computer-use
- browser-use WebVoyager report — https://browser-use.com/posts/sota-technical-report
- Skyvern architecture — https://www.skyvern.com/docs/developers/getting-started/introduction
- E2B pricing — https://e2b.dev/pricing ; Browserbase pricing — https://www.browserbase.com/pricing
- Composio tool catalogue (the 20,000+ tools figure) — https://composio.dev/toolkits
