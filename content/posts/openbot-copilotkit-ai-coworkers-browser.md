---
title: "CopilotKit OpenBot Review 2026: AI Coworkers That Each Get Their Own Browser"
date: 2026-09-30T07:08:48+00:00
tags: ["openbot ai coworkers", "copilotkit openbot", "copilotkit openbot review", "ai coworkers", "agent governance gateway", "fail-closed agent policy", "ai agent browser isolation", "ag-ui agent", "open source grok bot", "claude cowork alternative", "self-hosted ai agent platform"]
description: "CopilotKit OpenBot review: an MIT, self-hosted platform where every AI coworker gets its own browser, its own logins, and a fail-closed policy gateway."
draft: false
cover:
    image: "/images/openbot-copilotkit-ai-coworkers-browser.png"
    alt: "CopilotKit OpenBot Review 2026: AI Coworkers That Each Get Their Own Browser"
    relative: false
schema: "schema-openbot-copilotkit-ai-coworkers-browser"
---

CopilotKit OpenBot is an MIT-licensed, self-hosted platform where each AI coworker runs in its own container with its own Chromium browser, its own persistent logins, and where every action is decided against a fail-closed policy — and audited — before it can happen. As of 30 September 2026 it has 5,737 GitHub stars, 762 forks and 33 contributors.

This is a second, deliberately different look at the same product. Our [first OpenBot review](/openbot-ai-coworker-computer-2026/) covered the "a computer per coworker" model in September. This one answers the questions that review left open: which of the four products called OpenBot you actually want, what one browser per coworker costs you operationally, and — the part most coverage gets wrong — which hardening in OpenBot is enforced by the software versus which is merely documented and left off.

## What Is CopilotKit OpenBot?

OpenBot is the open-source, self-hosted half of CopilotKit's enterprise agent platform. The repository was created on 17 August 2026, announced publicly on 19 August, and is written mostly in TypeScript (roughly 83%) with about 12.8% Rust. CopilotKit raised a $27M Series A in May 2026 led by Glilot Capital, NFX and SignalFire, and OpenBot is the layer that lets a company run governed AI coworkers inside its own infrastructure instead of renting a hosted one.

The product's own description is unusually blunt about its maturity. The README carries two blockquotes worth reading before anything else:

> **A template, not a product.** OpenBot is meant to be cloned and made your own. There is no hosted version to sign up for, and nothing here is published as a package to depend on: every workspace in this repository is private.

> **Alpha, and under active development.** OpenBot is early. Expect rough edges and bugs, and expect things to move.

That framing matters because it separates OpenBot from almost every product it gets compared to. You are not buying a service; you are adopting a reference implementation of governed agent execution that you operate yourself, on your own hardware, with your own model key.

The honest one-line positioning: OpenBot does not compete with open-source agent frameworks on capability. It competes with hosted coworker products — Grok Bot, Claude Cowork — on governance, and it wants to host whatever framework you already have.

## Three Products Called OpenBot — Which One You Want

Search for "openbot" and you land on at least four different things. This is not a minor annoyance; the name collision is why "openbot ai coworkers" has no Google autocomplete while "openbot" and "openbot copilotkit" do. Search intent is split, so define which one you mean before you evaluate anything.

| Product | What it is | Where it lives | Who it is for |
|---|---|---|---|
| CopilotKit OpenBot | Self-hosted AI coworker platform; per-coworker browser container plus a fail-closed policy gateway and audit trail | github.com/CopilotKit/OpenBot (MIT) | Teams running governed agents inside their own infrastructure |
| ob-f/OpenBot | A $50 smartphone robot from Intel ISL; a phone becomes a wheeled robot with an Arduino board. Published as arXiv 2008.10631 in 2018 | github.com/ob-f/OpenBot | Robotics hobbyists and researchers |
| getopenbot.com | A paid cloud "coordinator" for coding agents such as Claude Code, Codex and Cursor, priced around $60/month | Hosted SaaS | Individual developers running coding agents |
| openbot.one | Another hosted agent workspace using the same bare name | Hosted SaaS | Small teams wanting a managed agent workspace |

If you arrived here from "openbot ai coworkers", you want the first row. If you want a robot, you want the second. If you want someone else to run it for you, the third and fourth rows exist — but note that CopilotKit's own commercial answer for that is "talk to an engineer", not a self-serve sign-up.

The disambiguating convention worth adopting: write "CopilotKit OpenBot" when you mean the AI coworker platform. The bare name is contested and will keep getting more contested.

## What "Each Coworker Gets Its Own Browser" Actually Means

The phrase is literal, and the mechanism is a single environment variable with a large blast radius.

`COMPUTER_SUPERVISOR_URL` points the platform at a supervisor service that creates one container per Bot. Each container runs its own Chromium, holds its own persistent browser profile, mounts its own `/workspace` volume, and exposes its own file and shell tools. When that variable is absent, every Bot shares one `AGENT_COMPUTER_URL` instead — a materially weaker guarantee, and one of the most commonly missed configuration facts in third-party write-ups.

Why does a browser profile deserve a container of its own? Because a browser profile is an identity. Cookies, session tokens, saved logins and localStorage all live in that profile, and any agent driving that browser acts with whatever authority those sessions carry. A shared browser session means a research coworker can inherit the signed-in session of a publishing coworker, and your audit trail then records an action that a different role authorised.

Under the supervisor model, a bot asked to run `psql` against the product database finds nothing to connect to: PostgreSQL sits on a separate Docker network that only the API server and the migration job can reach. Computers bind to loopback and require a per-container token — `COMPUTER_TOKEN` is required or the computer refuses to start — so nothing on the host network can guess its way into a logged-in browser.

The supervisor itself holds the Docker socket, which is why the docs are explicit that you must not expose it outside the deployment network. Docker Compose binds it to `127.0.0.1:4500`, and a deployment running the server inside the compose network reaches it as `supervisor:4300` and needs no published port at all.

There are ceilings here too, and they matter for capacity planning. `COMPUTER_MAX_BROWSERS` defaults to 8 concurrent resident browsers, with the least recently used closed past that limit. `COMPUTER_BROWSER_IDLE_MS` closes an untouched browser after 30 minutes by default. If you run twelve coworkers and five of them need a browser simultaneously, they queue.

## The Gateway: Decided Before, Recorded After

OpenBot's central claim is that the gateway, not the browser, is the action boundary. The architecture documentation states the sequence as a fixed, ordered five-step path:

1. Resolve the target from the server-held snapshot or request subject.
2. Evaluate the current action policy.
3. Write an audit row for the decision.
4. Call the computer only when the decision forwards.
5. Write a second audit row if a forwarded action fails.

The ordering is the point. A bot cannot invent an element reference, because the reference it can act on comes from a snapshot the server took — so the model cannot fabricate a target and reach for it. And no forwarded action can complete without the row describing it already existing.

This is the distinction that gives the design its edge: most agent tooling records after the fact. The decision happens before, and the record includes refusals and failures, not only successes. The audit screen shows permitted, refused and failed rows together, which is what makes it usable for a review conversation rather than a debugging one.

A caution worth stating plainly: **computer actions are the one family that carries no initiator, and correctly so**. The architecture docs note that the computer tools are browser actions executed by the person's own session, so a headless run currently has no way to drive the computer at all. In other words, the governance story applies to the gateway-mediated families — files, shell, MCP, components — while today's browser control is inherently a person-present activity. Anyone claiming OpenBot gives you fully unattended browser automation governed under `initiator.kind` is overselling the current release.

## The CEL Policy Engine, Fail-Closed

Policies are written in CEL and live either in the `AGENT_COMPUTER_POLICY` environment variable or in the `/admin/boundaries` screen. The semantics are stated precisely in the README, and precision here is what earns a security reviewer's trust:

- Deny is evaluated before allow.
- A missing policy permits nothing.
- A broken rule refuses rather than opens.

The rule fields you can inspect are concrete: `tool.name`, `intent`, `bot.id`, `actor.id`, `page.url` and `page.host`, `element.ref`/`role`/`name`/`type`, `key`, `command`, `file.path`/`name`/`extension`, `mcp.server`/`tool`/`effect`, and `initiator.kind`/`initiator.id`.

The shipped default is deliberately permissive — `deny: []`, `allow: ['true']` — which is the correct default for a template and the wrong default for a deployment. Nothing about the fail-closed semantics helps you until you write rules.

### Why initiator.kind Matters More Than actor.id

`actor.id` records on whose authority an action was taken. A routine asserts its owner's identity, so a scheduled 9am job shows up as *Andrew* — exactly as it would if Andrew typed the request himself. That column alone cannot tell you whether anybody was in the room.

`initiator.kind` answers that. The four values are:

| `initiator_kind` | `initiator_id` | What it means |
|---|---|---|
| `person` | none | Somebody was in the room. The default. |
| `deployment` | none | The deployment itself, at start-up or refusing a caller it could not identify. |
| `routine` | the routine's id | A schedule fired it, as its owner, with nobody there. |
| `handoff` | the Bot that handed on | Another Bot asked for this, on the person's behalf. |

The audit screen filters on this, and its **Nobody watching** view is `routine` and `handoff` together — the exact question of what ran on somebody's authority while they were away. `deployment` is deliberately excluded, because a boundary held at start-up is not work done on anybody's behalf.

The value travels inside a signed run assertion, so a Bot cannot relabel its own run; an unknown kind is read as `person` rather than trusted. That is a real security property, not a field name.

This is what enables the most interesting rule class in the product: refuse an MCP write on a `routine`-started run while allowing the same call when `initiator.kind == "person"`. Most agent governance tooling cannot express that sentence.

### Five Deny Rules Worth Copying

The policy engine is abstract until you read a rule. These map directly onto the documented field list:

- Refuse destructive shell: deny when `command` matches a recursive delete or a disk-format pattern, for every bot, no exceptions.
- Keep every bot off finance hosts: deny when `page.host` ends in your finance domain, regardless of which bot is driving or who started the run.
- Refuse MCP writes on unattended runs: deny when `mcp.effect == "write"` and `initiator.kind == "routine"`, so a schedule can read but never mutate.
- Never type into a credential field: deny when `element.type == "password"` — the bot should stop and ask, which is the designed behaviour anyway.
- Restrict file writes to the workspace: deny when `file.path` is outside `/workspace`, which stops a bot talked into writing to a host-mounted path.

Because deny is evaluated before allow and a broken rule refuses, a typo in any of these fails toward blocking rather than toward opening. That is the right direction for the mistake.

## Isolation, Egress and Secrets

The isolation story is more careful than the marketing suggests, and the details are where it holds up.

Computers bind to loopback with a per-container token. PostgreSQL lives on a separate Docker `data` network reachable only by the server and the migration job. Browser navigation is limited to plain http and https, and cloud-metadata-looking addresses are refused regardless of any other configuration — closing the standard credential-theft route through `169.254.169.254`. Critically, the same target validation applies to custom AG-UI agent endpoints, not just page navigation, and an endpoint's auth header is stored write-only.

Per-bot egress needs a separate file. The `EGRESS_PROXY_<BOT_ID>` and `EGRESS_PROXY_DEFAULT` variables live in `egress.env` at the repository root, not in `.env`, and the file is optional and gitignored. The separation is deliberate: `.env` holds the deployment's secrets and neither the browser container nor the supervisor is given those. Without the file, every bot's browser goes out directly, which is the default.

Secrets are handled with more discipline than most tools manage. Credentials are stored through `/admin/credentials`, encrypted at rest with `KEY_ENCRYPTION_KEY`, never returned by any API, and redacted from audit events. The trail records that a secret was requested and its character count — not its value. A shell command on the computer inherits only PATH, locale, terminal names and the proxy variables by default; userinfo is stripped from proxy URLs, so a password in `HTTP_PROXY` does not appear in `env`.

One more mechanism worth knowing: if a tool is not positively classified as a read, it is treated as a write. That default is why an MCP catalogue can ship connectors for Atlassian, Box, Slack, Salesforce and ServiceNow without each one needing a bespoke policy.

## Skills Are Instructions, Grants Are Capabilities

The cleanest mental model in the documentation is this split, and getting it wrong is the most common way a deployment ends up with more access than intended.

A skill is a written instruction — a description of how to do a job. Listing "find a document" on the Knowledge bot loads nothing. Until an administrator connects Google Drive and grants those tools, the skill is text.

Capabilities are granted separately and through different paths: MCP grants are per bot, deployment skills are granted by admins, and personal skills only load on bots their author owns. A coworker's *role* never confers capability. UI components publish deployment-wide and can be withheld per bot.

The audit consequence is straightforward: if you read a bot's skill list and assume it describes what the bot can do, you have misread the model. The grant list is the capability surface. Read the grant list.

The v0.0.15 changelog adds a related guard worth noting — an administrator can no longer create a grant naming a skill that does not exist, because on a shared deployment that row would wait for whoever wrote a skill under that name next, and one person's instructions would end up answering everybody.

## Take the Wheel: Human Handover for 2FA and Login Walls

Bots do not handle 2FA. That is the design, not a gap.

When a coworker hits a login wall or a 2FA prompt, it stops and asks for help. A person takes control of the same live browser panel, completes the step, and hands it back. The profile persists, so subsequent runs stay signed in. Since v0.0.5 a person can seize control at any moment rather than only when the bot asks.

The governance detail is what happens during the handover. It is recorded as three control events — `computer.help_requested`, `computer.control_taken`, `computer.control_released` — and while a person is driving, bot actions are refused rather than queued. Refused, not deferred: nothing the bot attempted during human control sits in a queue waiting to fire when the human lets go. Secret entry is treated as separate from chat content, and the trail records the request and the character count, never the value.

For a security reviewer, this is the section that answers "what happens at 2am when the agent hits a wall?" Somebody takes the wheel, from somewhere, and the fact that they did is in the log.

## Hardening: What Ships Off, and What the Software Actually Enforces

This is the section no competing write-up has assembled in one place, and it is also where I found the most common factual error in circulation.

Several published takes list `OPENBOT_SINGLE_USER=true` as a "footgun you must disable before exposing an install". The first half is true; the second half is not how it works. The configuration documentation states it plainly:

> **With no provider at all, `OPENBOT_SINGLE_USER=true` is required.** A deployment that configures nothing to sign anybody in and does not say that was deliberate refuses to start, naming what to configure, because a public URL where every visitor is an administrator fails silently.

And further:

> **But not on a public address.** ... If `OPENBOT_PUBLIC_URL`, `OPENBOT_APP_URL` or any `TRUSTED_ORIGINS` entry is an address the public internet routes to, the deployment refuses to start and names it. Loopback is silent. A private address is allowed and warned about once at boot, because a home server, a Tailnet, a VPN address and a `.local` name are what this flag is mostly used for, and anybody on that network is the administrator.

So the accurate statement is stronger than "turn it off": you cannot expose a single-user OpenBot on a public address — it will not boot. Anyone on a private network that can reach it *is* the administrator, and that is a deliberate, warned-about trade-off, not an oversight. The failure mode to avoid is running it on a Tailnet or corporate VPN where you have not thought about who is on that network.

The rest of the switches are honestly off by default, and each one is a real deployment decision:

| Switch | Shipped state | What enabling it buys you | What the software enforces |
|---|---|---|---|
| `OPENBOT_SINGLE_USER` | `true` in `.env.example` | Nothing — it is the no-sign-in mode. Configure an OAuth provider instead (Google, Microsoft Entra, Okta) | Refuses to start on a public address; warns once on a private one |
| `COMPUTER_SUPERVISOR_URL` | empty | One container per Bot with its own browser profile instead of one shared computer | Nothing — an empty value silently falls back to a shared `AGENT_COMPUTER_URL` |
| `COMPUTER_RUNTIME=runsc` | empty | Runs supervised computers under gVisor | Nothing — opt-in only |
| `AGENT_COMPUTER_ALLOW_PRIVATE_HOSTS` | commented out | Lets a bot reach host services (rarely what you want) | A `NODE_ENV=production` deployment refuses to start while it is set |
| `egress.env` | absent | Per-bot egress proxy, so you can attribute one bot's traffic | Nothing — absent means every browser goes out directly |
| `INITIAL_ADMIN_EMAILS`, `BETTER_AUTH_SECRET` | unset | Real sign-in with an identity provider | Required with any provider; incomplete combinations are refused at start-up |
| `KEY_ENCRYPTION_KEY` | example value | Encrypted credential storage in production | `NODE_ENV=production` refuses the example key |
| TLS termination | not shipped | Your deployment stops being plaintext | Nothing — you front it |

Two rows deserve emphasis. The second one — a missing `COMPUTER_SUPERVISOR_URL` quietly collapsing the product's headline isolation into a shared browser — is the single highest-impact misconfiguration available, and nothing in the software stops you. The fifth — an absent `egress.env` meaning every bot's browser exits your network directly — is the one most likely to fail an egress audit.

Also worth knowing: `NODE_ENV` does **not** decide whether sign-in is required. The docs are explicit that `NODE_ENV=production` refuses the example encryption key but has nothing to do with authentication. Assuming production mode implies authentication is a mistake this product's own docs call out.

## What It Costs to Run

OpenBot's licence costs nothing. The operational bill is the real price, and it is worth pricing per unit rather than in adjectives.

Things that must stay alive: PostgreSQL with pgvector, the API server on port 3001, the app on 3010, the supervisor, and one browser container per active coworker. `scripts/start.sh` starts PostgreSQL, `agent-computer`, `agent-bot`, `agent-langgraph` and the supervisor through Docker Compose, then starts the server and app on the host. The compose file also defines optional SPIRE services for attested identity, which `start.sh` does not start.

The unit that surprises people is Chromium. Four coworkers on shift means four resident Chromium instances, capped at eight by default with a 30-minute idle close. The machine must be reachable whenever anyone opens a channel, because coworkers are a chat surface, not a batch job.

Routines have their own ceilings, and the docs give the reason: a routine may fire at most every 15 minutes, because a model can be talked into anything a sentence can describe — including "every minute" — and the floor is what a sentence cannot talk it out of. A person may have at most 20 routines switched on at once, for the same reason: a conversation is an easy place to accumulate standing work without noticing. A failing routine posts exactly one message about it — the first failure after a success, not every failure — and ten consecutive failures switch the routine off with a final message.

`AGENT_STALL_TIMEOUT_MS` bounds a bot's stream: the documented behaviour is that a bot's turn is ended when the stream produces nothing. Note the primary source states it as "unset (off)" in the configuration table while the `.env.example` ships `60000`; treat the `.env` value as your deployment's actual setting rather than assuming a default.

And then there is the dependency that the MIT licence does not cover.

## What MIT Does Not Cover

The repository is MIT and no enterprise tier gates the audit log, SSO or SAML/OIDC. But the surrounding requirements are not MIT code:

- **CopilotKit Intelligence** is an external, separately licensed service that provides durable threads, memory and the realtime gateway. Every independent reviewer lands on the same point, and Zentor states it outright: the code being MIT does not make the whole deployment dependency-free. There is a free plan and a self-hosted option, and there is no degraded mode if it is unavailable.
- **Docker** is required as shipped. There is no supported path that skips it.
- **Bun 1.3+** is required to run the app and API server.
- **A model key you supply.** No model ships in the box.
- **An operator.** Somebody has to run five services and maintain a fork.

That list is the honest answer to "is OpenBot free?" — the software is free, the stack is not free of dependencies.

## What Changed Since v0.0.13 — and Why Week-Old Reviews Are Stale

The release cadence is the fastest-moving thing about this project: v0.0.12 (15 Sep), v0.0.13 (18 Sep), v0.0.14 (21 Sep), v0.0.15 (22 Sep). The most-cited third-party review was written against v0.0.12 on 18 September; three releases have shipped since.

The changelog is written for the operator, not the commit author. Its own stated rule is that a line belongs there when a deployment behaves differently afterwards, and does not when only the code moved. That makes it the right source to cite instead of secondhand summaries.

From the recent releases, the changes that affect a deployment:

- **v0.0.15 — a model provider's sign-in can stand in for an API key.** `OPENBOT_MODEL_OAUTH_FILE` mounts a `POST /api/model-provider/v1/chat/completions` route that answers ordinary Chat Completions requests using a Google or xAI OAuth grant, refreshing the access token 120 seconds before expiry and again on a provider 401. The caller authenticates with a separate local bearer compared in constant time, never with the provider's token, so a refresh token never leaves the server process. The credential file is refused unless it is a regular file under 64KB, owned and readable by nobody else, and a Google grant must name a quota project. Leave the variable unset — true for most deployments — and the route does not exist. The same release also fixed a provider 403 being misread as an expired sign-in.
- **v0.0.14 — one provider spec file.** `shared/model-providers.json` now holds the provider facts and each bot's default provider and model, read by the TypeScript bots through `shared/model-providers.ts` and the Python bots through `shared/model_providers.py`, with `BOT_PROVIDER` and `BOT_MODEL` still winning. The practical change: a wrong row now fails every bot at start-up instead of at its first model call, and an unrecognised `BOT_PROVIDER` is refused instead of quietly defaulting.
- **v0.0.13 — desktop setup and cross-platform keyboard fixes.** Fresh desktop setup installs its runtime before sign-in, OpenBot chooses its own local ports by binding them and writes them to the deployment `.env`, and driving a bot's browser no longer triggers the app's own keyboard shortcuts or scrolls the surrounding page.

The pattern is a product that has been hardening its edges quickly. That is a reason to watch it. It is also a reason not to quote a review written a week ago.

## What Is Still Missing or Unproven

Honesty here is what separates a review from a press release.

- **Alpha by its own description**, with "expect rough edges and bugs" in the README.
- **No npm package and no hosted version**; every workspace in the repository is private, so there is nothing to depend on, only something to fork.
- **No SLA.** Support is community-only, and production adoption is unverified.
- **No degraded mode** when CopilotKit Intelligence is unavailable.
- **Third-party maturity scoring is unflattering at the enterprise end.** Independent scoring puts overall quality at 6/10 (docs 7, activity 9, community 7, code 7) and labels it not production-ready; audience-fit reads hobby 3/5, startup 3/5, SMB 2/5, enterprise 2/5. That is a direct counterweight to the enterprise marketing, from a source that is not a competitor.
- **`channels.allowed_groups` is declared but inert.** This is the detail worth surfacing because it is stated in the project's own docs: the tenant package requires an `allowed_groups` field per channel, it is validated and stored, and **nothing reads it**. Group-based rules have nothing to evaluate because `users.groups` is populated by no sign-in path. Channel access is decided by `channel_memberships` instead, and every channel route refuses a caller without a row. The docs describe the group field as a declaration waiting for a future feature. Report it as a stated limitation, not a vulnerability — but do not deploy believing a group-based control is protecting anything.
- **Local models are not officially tested.** Nothing local ships in the box.

## OpenBot vs Grok Bot, Claude Cowork, Browser Use and Playwright MCP

| | CopilotKit OpenBot | Grok Bot / Claude Cowork | Browser Use / Playwright MCP |
|---|---|---|---|
| Licence | MIT, self-hosted | Proprietary, hosted | Open source, library |
| Where it runs | Your infrastructure, Docker Compose | Vendor cloud | Wherever you call it |
| Per-agent browser | Yes — one container and profile per coworker | Shared cloud session | One browser per run, no isolation guarantee |
| Policy decided before action | Yes — fail-closed CEL at the gateway | Confirmation prompts | No |
| Audit of refusals and failures | Yes, `/admin/audit` | Not exposed to you | No |
| Human takeover | Audited, with control events; seize control any time | Within the vendor UI | Manual, outside any trail |
| Scheduled unattended runs | Routines, with `initiator.kind` separating them from people | Vendor-defined | You build it |
| SSO / SAML / OIDC | Yes, ungated by licence tier | Vendor-managed | No |
| Maturity | Alpha, v0.0.15, ~6 weeks old | Generally available | Mature libraries |

The clean framing, and the one the product's own reviewers keep arriving at: Browser Use and Playwright MCP give an agent *a* browser. OpenBot gives each agent its own browser container with persistent logins, puts a policy gateway and audit log between agent and browser, brings files, shell and MCP tools under the same gate, and wraps it in a multi-user chat product with SSO. It is a platform, not a library — and it is designed to host the libraries.

Against hosted competitors, the trade is explicit. You get governance, data residency and an audit trail you control. You pay in operational burden, an alpha maturity level, and an external dependency on CopilotKit Intelligence. If your security review killed a hosted coworker pilot over where the data went, that trade is the reason to look here.

## How to Evaluate It in an Hour

You do not need to run it for a month to form a view. The evaluation that matters is whether the audit page is something your compliance lead would sign off on.

1. Clone the repository and pin to v0.0.15 rather than tracking `main`.
2. Run the setup path with Bun 1.3+ and Docker. Loopback only — do not point `OPENBOT_PUBLIC_URL` at anything public yet.
3. Set `COMPUTER_SUPERVISOR_URL` so each bot gets its own container. Without it you are evaluating a different product.
4. Ask the General Assistant for the top story on Hacker News. This exercises the browser path and produces audit rows you can read.
5. Write three deny rules in `/admin/boundaries` — a shell command, a host, and a password field. Then ask the assistant to fill out `httpbin.org/forms/post` and watch a rule fire.
6. Open `/admin/audit` and read it. Permitted, refused and failed rows all appear together, and the **Nobody watching** filter isolates anything that ran on someone's authority while they were away.

Step 6 is the whole evaluation. The design claim is that the record exists before the action; the audit page either demonstrates that or it does not.

## Who Should Run OpenBot — and Who Should Not

**A good fit:**
- Platform engineers who want a working reference implementation of policy-gated tool calls, rather than a design document.
- Teams whose agents already speak AG-UI and who want a governance layer that rides the protocol instead of the framework — so changing from LangGraph to Mastra does not cost you your policy layer.
- Organisations where a security review already rejected a hosted coworker product over data residency.
- Teams willing to maintain a fork and run five services.

**Not a good fit:**
- A solo developer who wants a personal agent. Hosted products are better at this and always will be.
- Anyone allergic to maintaining a fork, or who needs something to depend on. The repository's own README says there is nothing here to depend on.
- Pure browser automation. Use Browser Use; OpenBot is the building around that library, not a replacement for it.
- Teams that want a fully unattended browser agent today. Per the architecture docs, computer actions are person-session actions right now.

## Verdict

CopilotKit OpenBot is the most serious attempt I have seen at making agent governance the product rather than a checkbox. The ordered gateway sequence — resolve, decide, record, act, record on failure — is a genuinely different design from the log-after-the-fact model that most tooling ships, and `initiator.kind` is a field almost nothing else in this category can express: the difference between a person typing and a schedule firing with nobody in the room.

The honesty cuts both ways. It is six weeks old and calls itself a template rather than a product. The headline isolation depends on one environment variable you can silently omit. Its memory layer is a separately licensed external service with no degraded mode. Independent scoring rates it 2/5 for SMB and enterprise fit, and the group-based channel control the tenant package requires decides nothing today.

So: worth a pinned clone and an afternoon on a spare machine, with `COMPUTER_SUPERVISOR_URL` set and an OAuth provider configured instead of leaving single-user mode on. Worth adopting into production for governed, unattended agent work only once you have an operator, a fork maintenance plan, and a policy file you have actually tested against a live refusal.

The gateway is the product. Computer use is not the novel claim — isolation plus a fail-closed policy is. Judge it on the audit page, not the star count.

## FAQ

### Is CopilotKit OpenBot free for commercial use?

Yes. The repository is MIT-licensed, and no enterprise tier gates the audit log, SSO or SAML/OIDC support. But the MIT licence covers the code, not the whole stack: durable threads and memory go through CopilotKit Intelligence, which is a separate, separately licensed service with a free plan and a self-hosted option. You also supply Docker, Bun 1.3+, a model key, and an operator.

### Does OpenBot require CopilotKit Intelligence?

For durable threads and memory, yes — there is no degraded mode if it is unavailable. It sits outside the repository, is licensed separately, and offers both a free plan and a self-hostable option. It also provides the realtime gateway. Plan for it as a production dependency rather than an optional add-on.

### Do I have to turn off OPENBOT_SINGLE_USER to deploy OpenBot safely?

Not quite — and this is where most coverage gets it wrong. `OPENBOT_SINGLE_USER=true` is required when no identity provider is configured, because a deployment that says nothing about how people sign in refuses to start. What protects you is that OpenBot refuses to start at all on a public address with that flag set. On a private address it starts with a single boot-time warning, and anyone who can reach that network is the administrator. The real fix is configuring Google, Microsoft Entra or Okta sign-in with `INITIAL_ADMIN_EMAILS`, not flipping the flag.

### Can OpenBot coworkers handle 2FA or a login wall?

No, by design. A bot that hits a login wall or a 2FA prompt asks for help; a person takes the wheel in the same panel, signs in, and hands it back. The browser profile persists, so later runs stay signed in. Handovers are recorded as `computer.help_requested`, `computer.control_taken` and `computer.control_released`, and while a person is driving, bot actions are refused rather than queued. Since v0.0.5 a person can seize control at any time without waiting to be asked.

### How is OpenBot different from Browser Use or Playwright MCP?

Those give an agent a browser. OpenBot gives each agent its own browser container with a persistent profile and its own logins, and puts a fail-closed CEL policy gateway and an audit trail between the agent and the browser — extending the same gate over file, shell, MCP and component actions. It also wraps that in a multi-user chat product with channels, SSO and an audited human takeover. The short version: they are libraries, OpenBot is the building around them, and it is designed to host them.
