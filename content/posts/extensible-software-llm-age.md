---
title: 'Extensible Software in the Age of LLMs: How to Ship a Core Users Can Extend Safely'
date: 2026-09-30T12:53:00+00:00
tags:
- extensible software
- LLM
- plugin architecture
- object capabilities
- sandboxing
- MCP
description: Extensible software in the age of LLMs means a small accountable core plus a sandboxed extension point that hands code capabilities, not credentials.
draft: false
schema: schema-extensible-software-llm-age
cover:
  image: /images/extensible-software-llm-age.png
  alt: 'Extensible Software in the Age of LLMs: How to Ship a Core Users Can Extend Safely'
  relative: false
---

Making software **extensible software in the age of LLMs** is a product-boundary decision before it is a runtime decision. Keep a small, accountable core; put the long tail of one-user requests on an extension point; and give untrusted extension code a narrow capability instead of a credential. The sandbox you choose matters less than the boundary you draw.

That is the short version of the argument Jeremy Morrell published on 2026-08-18 in ["Extensible software in the age of LLMs"](https://jeremymorrell.dev/blog/extensible-software-in-the-age-of-llms/), which reached the Hacker News front page at 177 points and 88 comments the next day ([HN item 49363668](https://news.ycombinator.com/item?id=49363668)). This guide turns that essay into a decision process: when to expose an extension point, what to hand it, which isolation primitive fits, and when the answer is that you should not build one at all.

## What Does "Extensible Software LLM" Actually Mean?

"Extensible software in the age of LLMs" describes applications whose feature surface is deliberately smaller than their behavior surface: a maintained core ships stable extension points, and users add the features they personally need — increasingly by describing them in prose that a model turns into code.

Three things distinguish this from a 2015-style plugin API:

1. **Authoring cost collapsed.** A request like "send every article I fave longer than 4000 words to my e-reader" is now a prompt, not a quarter of engineering time.
2. **The boundary is security-relevant.** If a model writes the extension, you cannot assume a human read it before it ran.
3. **Extension points are the durable API.** The hooks you expose outlive individual features, so they deserve the design budget you used to spend on features.

The mechanism is familiar. The economics are not.

## Why Did Web Software Stop at the Head of the Demand Curve?

Morrell's diagnosis starts with a constraint most product teams feel but rarely name: **attention is finite, and every feature you add taxes every user who did not ask for it.**

The result is that web software clusters at the head of the demand curve. The most common workflows get polished, because they justify the cost of building, shipping, documenting and maintaining a feature. The long tail — the one person who needs CSV export in a specific shape, the team that wants a Slack digest every Tuesday — gets a webhook and a shrug.

Webhooks are the tell. They are the industry's default answer to "I want something custom," and they push the entire burden onto the user: you must now run a separate service, host it, secure it, and keep it alive. A webhook is not an extension point; it is a delegation of infrastructure.

The old excuse was honest arithmetic. One-user features cost a week of engineering, and a week of engineering for one user does not survive a roadmap review. So products accumulated vetoes instead of features.

## What Changed When LLMs Made Software-for-One Cheap?

The veto is gone. Morrell's central claim is that LLMs made **"Software for One"** cheap: people can now ask for a one-off tool and get it. The bottleneck moved.

It is no longer "can a user build the thing?" The remaining gaps are:

- **Deploy** — where does that generated code actually run?
- **Secure** — what can it touch?
- **Share** — how do two people use the same extension?

The 2026 numbers show the supply side already answered the authoring question. Extension supply is now abundant; trust, versioning, discovery and distribution are the scarce goods:

| Ecosystem | Count | Read on |
|---|---|---|
| npm packages keyworded `mcp-server` | 9,264 | 2026-09-30 |
| npm packages keyworded `claude-code-plugin` | 556 | 2026-09-30 |
| npm packages keyworded `opencode-plugin` | 2,186 | 2026-09-30 |
| MCP registry servers (Smithery) | 11,245 | 2026-09-01 |
| MCP registry servers (PulseMCP) | 21,982 | 2026-09-01 |
| MCP registry servers (mcp.so, self-reported) | ~23,000 | 2026-07-01 |
| WordPress.org plugins | 69,937 | 2026-09-30 |
| Obsidian community plugins | 8,241 | 2026-09-30 |
| Firefox add-ons (AMO) | 621,529 | 2026-09-30 |
| Shopify App Store (advertised) | 16,000 | 2026-09-30 |

Always name the registry when you cite an MCP server count. The spread between Smithery, PulseMCP and mcp.so is roughly 2x for the same month, and a bare number is indefensible in a review.

The monetization picture is bleaker than the supply picture. An agent-extension census on 2026-08-12 counted 79,848 listings — 58,766 agent skills, 8,433 MCP servers, 10,264 marketplaces, 2,385 plugins — with 164,841,042 cumulative installs and **only 55 of 79,827 listings (0.07%) carrying a price**. Roughly 1,404 listings ask users to bring their own API key. A supply-rich, monetization-poor economy is exactly what you would expect when authoring is free and distribution is unsolved.

## What Does the LLM-Native Software Pattern Look Like in Practice?

Morrell's worked example is **Pi**, which he describes as LLM-native software: a battle-tested core that is almost endlessly extensible just by asking, where users share their customizations with each other. Extension requests are plain prose. The extension point is stable, and the surface is not a single hook but a family:

- tools
- commands
- events
- UI
- in-place reload, with extensions bundled into shareable packages

The limits matter as much as the pattern. A terminal-native, single-user tool can afford a permissive extension model because the blast radius is one person's machine. Move the same architecture onto the web — where the software holds other people's records — and every assumption inverts.

Two more 2026 proof points show the pattern is real, not theoretical:

- **opencode** refactored so that nearly everything is an internal plugin: 68 of them covering built-in agents, integrations and config loading, each individually disableable, with the team stating they "properly dogfood our plugin APIs" (opencode/dax, 2026-08-13). The repo sits at **211,057 GitHub stars and 27,956 forks**, MIT licensed, TypeScript.
- **Claude Code** treats a plugin as a directory of components — skills, agents, hooks and MCP servers — declared by `.claude-plugin/plugin.json` and distributed through marketplaces.

If your own built-in features are not plugins, your plugin API is probably wrong.

## Where Should the Boundary Sit?

This is the section most coverage skips. Dustcrawl's read of the essay reduces it to one rule: **"A solid core plus sandboxed extensions beats a fatter product."** Its gloss on the agent question is sharper still: *it is not "let the agent rewrite the app" — keep the core boring and let the long tail live outside it.*

Morrell connects this to Simon Willison's argument about conceptual integrity and counting lines of code. The logic: agents deleted the old veto (time), so a new filter has to take its place. That filter is conceptual integrity — if the request is a one-user bump, **do not merge it into the core.**

Practically, that means writing down the boundary before you write the sandbox:

| Request type | Where it belongs | Why |
|---|---|---|
| Fixes a bug for everyone | Core | It is the product's job |
| Changes behavior for everyone | Core, after design review | It is a product decision, not a config |
| Helps one user's workflow | Extension point | Zero cost to every other user |
| Needs a credential you do not have | Extension point + capability | You cannot safely hold it for them |
| Needs to run for hours | Extension point + durable execution | Out of scope for a request/response core |
| Needs your data in a specific shape | Extension point, read-side | Narrow, verifiable, reversible |

The test is not "can we build it?" It is "does this make the core worse for the other 99%?"

## What Does a Good Extension Point Look Like in 2026?

Three shapes dominate, and they are converging:

| System | Extension unit | Loading mechanism | Distribution |
|---|---|---|---|
| Pi | tools, commands, events, UI hooks | Reloaded in place inside the harness | Shareable packages |
| Claude Code | skills, agents, hooks, MCP servers | `.claude-plugin/plugin.json` manifest | Plugin marketplaces |
| opencode | JS/TS modules exporting hook objects (`tool.execute.before`) | `~/.opencode/plugins/` or npm, installed with bun at startup | npm |
| MCP | tools exposed over a protocol | Server process the host connects to | Registries (Smithery, PulseMCP, mcp.so) |

Two design notes that survive the comparison:

- **Hooks beat plugin manifests for behavior, manifests beat hooks for distribution.** opencode's hook-object model is easy to author but hard to version; Claude Code's manifest is easy to distribute but needs a component model.
- **MCP is the distribution layer, not the trust boundary.** The MCP spec was donated to the Linux Foundation on 2025-12-09, and the Agentic AI Foundation grew from 49 founding members to 247 by 2026-08-13. Protocol adoption does not answer "what can this extension do to my data?"

For prior art, note that **Salesforce has run this pattern since 2007**: Apex for logic, `@RestResource` HTTP endpoints, Schedulable cron, `USER_MODE` for permission-aware execution, tenant isolation, and no webserver to deploy — AWS S3 and EC2 shipped in 2006, for reference. The essay calls it "a precursor to modern serverless." The lesson is not that you should copy Apex. It is that multi-tenant programmable platforms have been operationally survivable for nearly two decades when the boundary is enforced by the platform rather than by convention.

## Where Does an Extension Point Pay Off First?

Morrell names four frontiers — and the common thread is that each is currently served by webhooks that force you to run a separate service:

1. **AI agents.** [Code Mode-style tool access](/posts/agent-codemode-mcp-scripts-2026/) converts MCP tools into a typed API so the model writes code against it. Cloudflare claims this saves "up to 80% in inference tokens and cost" (Kenton Varda and Sunil Pai, 2025-09-26) by processing data programmatically instead of round-tripping it through the model. Treat that as a vendor claim, not a neutral benchmark.
2. **Internal corporate platforms.** Every company has a long tail of internal workflows that will never be a SaaS product.
3. **Support platforms.** Custom escalation logic, custom routing, custom reporting — per customer, per quarter.
4. **Observability platforms.** Custom checks and derived metrics are the canonical long-tail feature request.

For the sandbox side of this decision, the [code execution sandbox pricing comparison](/posts/code-execution-sandbox-pricing-comparison-2026/) covers what the primitives actually cost. For how agent harnesses are already structuring these extension surfaces, see the [Claude Code dev-team stack guide](/posts/claude-code-dev-team-stack-skills-mcp-2026/) and the [Codex plugins and integrations guide](/posts/codex-plugins-integrations-guide-2026/). If you want a working open-source reference implementation of an extensible agent, [Goose](/posts/goose-open-source-extensible-ai-agent-2026/) is the closest thing to a readable one — and if you are still weighing protocol-level integration against plain APIs, the [API vs MCP comparison](/posts/api-vs-mcp-difference-guide-2026/) frames that tradeoff.

## Why Does the Obsidian Trust Model Break on the Web?

Obsidian's plugin ecosystem works, and it works for one reason Morrell states plainly: **stakes are low.** A community plugin can "basically do anything," and the project defends itself with automated and manual review plus verified authors. For a local notes app, that is a reasonable trade — you can read the plugin source, back up your vault, and uninstall.

The trade collapses when the software holds customer records, financial transactions or private messages. Three failure modes become live:

- **Exfiltration.** Unrestricted plugins read whatever the process can read. In Obsidian that is your notes; in a CRM it is your customers.
- **Credential forwarding.** An extension that receives your API key can send it to a third party. Now the key is compromised and you cannot revoke the extension's knowledge of it.
- **Resource attack in both directions.** Infinite loops take the service down; free-compute crypto mining takes your margin down.

Add **Spectre-class side-channel concerns** — memory-safety isolation is not the same as security isolation — and the conclusion is that "reviewed by a human" is a mitigation, not a boundary.

## Capabilities, Not API Keys

The most useful technical idea in the essay is the rejection of the default pattern. The bad pattern is: hand the extension a token, then build a filtering proxy in front of the API.

```text
// The token + filtering proxy pattern (avoid)
const key = process.env.CRM_API_KEY;
const client = new CrmClient(key);
// ...plus per-endpoint filter logic that must track every API change
await client.get("/contacts", { /* you must prove this cannot leak PII */ });
```

Morrell's objection is practical: filtering logic for one operation on one endpoint is already large, and **"starting with a lot of power and then trying to restrict it precisely is a hard problem."** Even fine-grained scopes rarely express "only this one email."

The inversion is object capabilities. Hand the code exactly one approved function:

```text
// The capability pattern (prefer)
export function sendDigest(articles: Article[]): Promise<void>;
// The extension receives `sendDigest` and nothing else.
// No token, no client, no ambient network access.
// Per Morrell: "the code can only take actions via the references it has been passed."
```

The IFTTT analogy is the clearest illustration: an IFTTT applet gets `twitter.post_new_tweet()`, not a Twitter API key. It can do the one thing and nothing adjacent.

Two bonuses that matter in 2026:

- **Capabilities are a better prompt surface.** Generating logic from a TypeScript definition of capabilities is easier and more token-efficient than handing a model a pile of OpenAPI JSON. The security boundary and the generation interface are the same artifact.
- **Capabilities are auditable.** A capability list is short enough to review per extension, which is what makes LLM-authored extensions tractable at all.

Cloudflare's own framing of bindings is the same idea: the essay's footnote 4 notes that bindings and Service Workers work on an Object Capability RPC system, and Kenton Varda described Cloudflare OS running an app's client code in a null-origin iframe denied everything deniable, talking only through a Cap'n Web RPC session to the parent frame — while the app's server runs in a Dynamic Worker sandbox. The client can talk to its own server and nothing else. [Cap'n Web](https://github.com/cloudflare/capnweb) is worth knowing as an object-capability RPC protocol you can layer on any of the runtimes below.

## Which Isolation Primitive Should You Choose?

Morrell's requirement list is the shopping list, and it is identical to what an agent execution sandbox needs:

1. **~$0 when idle**, with tiny fractions of a cent per execution
2. **Single-digit-millisecond cold starts**
3. **Enforceable limits** on CPU, memory, network request count and size, response size, and log volume
4. **Fault and security isolation**, including Spectre-class concerns
5. **A narrow action surface** — capabilities, per the previous section

Against those requirements, four primitive families are in play:

| Primitive | Examples | Startup | Best for | Main cost |
|---|---|---|---|---|
| Embeddable interpreter | Lua, QuickJS | Microseconds | Small logic, tight embedding | You build the limits and the API surface |
| V8 isolates | workerd, celld, isolated-vm, Rivet secure-exec | Single-digit ms | JS-native logic, high density | JS-only; isolate boundaries need care |
| microVMs | Firecracker, libkrun, AWS Lambda MicroVMs, `@deno/sandbox`, smolvm, Tensorlake, Daytona | ~1s | POSIX, full binaries, arbitrary runtimes | Startup latency and operational weight |
| WASM + WASI | Wasmtime, wasmtime-based hosts | Milliseconds | Untrusted code with host-defined capabilities | Toolchain complexity; starts from a blank slate |

Why WASM appears in the list even though it is harder: it **starts from a blank slate, and the host defines the capabilities that get passed in** — which is precisely the capability model, expressed in a compiler target. Cloudflare Dynamic Workers is the closest production-ready fit as of 2026, explicitly positioned as "a lightweight alternative to containers for securely sandboxing code you don't trust," with the underlying runtime (`cloudflare/workerd`, 8,791 stars, Apache-2.0) available to run yourself.

Attribute the recommendation honestly: **Morrell works at Cloudflare and discloses it in the essay**, and one HN commenter called the piece "an ad for sandboxes + the idea of OCaps." He agreed with that characterization in the thread. Read the Cloudflare material as one well-informed practitioner's recommendation, not a neutral survey.

Also note these options are not mutually exclusive. microVMs remain genuinely useful for **authoring, bundling and testing** extensions even if you execute them in a V8 isolate — the isolation primitive you run is not the only one you use.

## What Do You Still Have to Build Yourself?

Shipping the sandbox is maybe 30% of the platform. Morrell lists what remains, and none of it is optional:

- **Observability.** OpenTelemetry inside the runtime, so a failing extension is debuggable by its author and accountable to you.
- **Per-tenant storage.** Per-user SQLite or Durable Object facets, or R2 buckets — extensions need somewhere to keep state that is not your core database.
- **Durable execution.** Long-running extension work needs a workflow engine (e.g. Dynamic Workflows), not a request handler.
- **Source control inside the product.** Versioning, diffing and rollback for extensions is table stakes, not a nice-to-have.
- **Hosted LLMs with token budgets and rate limits.** If extensions call models, someone has to cap the spend.
- **In-runtime JS transpilation.** Tools like sucrase so authoring needs no separate build VM.

Two cautionary data points explain why the retrofitted version is so much worse:

- **OpenHands V0** accumulated ad hoc extension points and ended at **140+ fields, 15 classes and 2.8K lines of configuration code** — "a brittle system where small changes often cascaded into unrelated failures." V1's fix was structural: stateless by default with one source of truth, strict separation of concerns so the core evolves independently, and a typed component model so developers extend declaratively without touching the core (arXiv 2511.03690).
- **SelfEvolve** (arXiv 2604.16314) shows runtime self-extension working: a generated function is verified in a sandbox, promoted into the running system via `importlib.reload()` with no restart, and added to a knowledge base for reuse — **92.7% average Pass@1 (51/55) across 11 tasks, 61.8% better than the best baseline (AutoGen)**. The paper is also honest about the risk: a newly integrated function does not guarantee the rest of the system stays correct. That is the correctness problem you inherit the moment extensions become durable artifacts.

## When Is a Separate Small App Better Than an Extension Point?

Include the dissent, because it is strong. A top-level HN commenter (0xbadcafebee) argues that extension-by-accumulation **reproduces the complexity problem inside the host app**, and that the proven alternative is composing separate small programs:

> "you don't add a file search extension to your application; you make one completely separate app, called grep, and call it from any application."

This is the Unix position, and it is correct more often than platform builders admit. Build an extension point when:

- the extension needs **your data or your authorization model**, which a separate program cannot have;
- the value comes from **running inside your UI**, where a second app is a worse experience;
- the extension is **small, frequent and user-specific**, so separate deployment is overkill;
- you are willing to **own the platform forever** — because "platforms are hard: hard to design, hard to run, hard to debug," in Morrell's own words, after a decade of running them.

Do not build one when the need is a data export (ship an export), a scheduled job (ship a webhook that is genuinely sufficient), or an integration you could solve by being a better API client. And set expectations on participation inequality: Morrell concedes in his footnote 1 that a small percentage of users will author most extensions no matter how easy authoring becomes. A platform of 10,000 users producing 12 real extensions is a normal outcome, not a failure.

## What Is a Realistic Staged Adoption Path?

Do not launch a platform. Sequence it:

**Stage 1 — Make the surface real.** Versioning and source control for extensions inside the product, a stable hook set, and a documented boundary that says what will never be a core feature. This stage is unglamorous and it is where most of the long-term cost lives.

**Stage 2 — Add capabilities.** Replace ambient credentials with a short, typed capability list. Every extension gets references, not secrets. This is the security step that makes LLM authorship defensible, and it is also the prompt-surface improvement.

**Stage 3 — Buy a sandbox primitive.** Adopt a V8 isolate, interpreter or WASM host that meets the five requirements, and enforce limits on CPU, memory, network and logs on day one. Remember the Heroku lesson: a popular getting-started guide shipped `while True: print('hello world!')` — an infinite loop in a tutorial is a denial-of-service against your own platform, and limits plus isolation are the minimum, not either one alone.

**Stage 4 — Wire in durable execution, storage and observability.** Extensions that keep state and run for minutes need all three. This is where the platform becomes operational rather than demoable.

If you build nothing else, build Stage 1 and Stage 2. A narrow capability list and in-product version control deliver most of the safety of a real sandbox at a fraction of the complexity.

## FAQ

### Is "extensible software llm" just a plugin API with a new name?

The mechanism is familiar; the economics are not. The authoring cost collapsed, so users can now speak functionality into existence. That moves the design constraint from "how do I stop feature requests?" to "where do I allow code to run, and what can it touch?" A 2026 extension point is a plugin API plus a sandbox boundary plus a capability list plus in-product version control.

### Why not just give extensions a scoped API key?

Because restricting a powerful credential precisely is the hard problem. You end up writing per-endpoint filter logic that must track every change in the backing API, and even fine-grained scopes rarely express "only this one email." Capabilities invert it: the code receives references it can call, holds no credential, and cannot leak or reach anything it was not handed.

### Do I need a microVM to run user extensions?

Usually not. MicroVMs buy POSIX and full binaries at roughly a second of startup. If your extensions are logic, API calls and small workflows, a V8 isolate, an embeddable interpreter, or WASM+WASI is a better cost and latency fit. MicroVMs are still useful for authoring, bundling and testing extensions, and none of the options are mutually exclusive.

### How do I keep one bad extension from taking the service down?

Enforce limits on CPU, memory, network request count and size, response size, and log volume and rate. Isolate faults as well as security — infinite loops and memory bombs are availability attacks. Limits plus a real isolation boundary are the minimum; either one alone is not enough.

### Can I let an LLM write extensions safely?

That is the point of the capability model: a narrow capability list is both a safe boundary and a better prompt surface, because TypeScript capability definitions beat a pile of OpenAPI JSON on token efficiency and clarity. SelfEvolve shows runtime-generated functions can be verified in a sandbox and promoted into a running system without a restart (92.7% Pass@1 across 11 tasks) while openly flagging correctness risk to the rest of the system. Treat generated extensions as durable artifacts that need version control and rollback.

## Sources and Further Reading

- Jeremy Morrell, [Extensible software in the age of LLMs](https://jeremymorrell.dev/blog/extensible-software-in-the-age-of-llms/) (2026-08-18)
- [Hacker News discussion, item 49363668](https://news.ycombinator.com/item?id=49363668) (177 points, 88 comments) — including replies from the author and Kenton Varda
- [Dustcrawl: solid core plus sandboxed extensions](https://www.dustcrawl.com/blog/agentic/2026-08-20/)
- [Windflash daily report](https://windflash.us/daily-report/en/2026-08-20)
- [Interactive explainer of the essay](https://extensible-software.k3.demos.sulat.com/)
- [SelfEvolve: runtime self-extension](https://arxiv.org/abs/2604.16314) (arXiv 2604.16314)
- [The OpenHands Software Agent SDK](https://arxiv.org/abs/2511.03690) (arXiv 2511.03690)
- [Cloudflare Code Mode](https://blog.cloudflare.com/code-mode/) and [Dynamic Workers](https://developers.cloudflare.com/dynamic-workers/)
- [opencode plugin docs](https://opencode.ai/docs/plugins/) and [Claude Code plugins](https://docs.claude.com/en/docs/claude-code/plugins)
- [MCP ecosystem statistics](https://agentscamp.com/guides/mcp/mcp-ecosystem-statistics) and [agent economy census](https://skillselion.com/research/ai-agent-statistics)
