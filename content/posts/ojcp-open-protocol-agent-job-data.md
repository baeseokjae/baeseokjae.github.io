---
title: 'OJCP: The Open Job Context Protocol for Agent-Consumable Job Data'
date: 2026-10-01T00:05:47+00:00
tags:
- OJCP
- MCP
- AI agents
- WebMCP
- job data protocol
- hiring
description: OJCP (Open Job Context Protocol) is a draft v0.2 standard giving AI agents an MCP tool set for job search, applications and identity proof.
draft: false
cover:
  image: /images/ojcp-open-protocol-agent-job-data.png
  alt: 'OJCP: The Open Job Context Protocol for Agent-Consumable Job Data'
  relative: false
schema: schema-ojcp-open-protocol-agent-job-data
---

OJCP (Open Job Context Protocol) is a draft open standard that lets AI agents find, read and act on job postings through MCP tools instead of scraping career pages. A provider publishes a manifest at `/.well-known/ojcp.json`, implements the required `search_jobs` tool plus five recommended ones, and normalizes its apply paths. Current status: a living v0.2 draft with 80 GitHub stars.

Two disambiguations before anything else. First, this OJCP is not Ontario Job Creation Partnerships, the Canadian government program that owns the acronym in most search results; in this article OJCP means the agent-facing job data protocol authored by Recruitics CTO Austin Anderson and governed by a steering committee that includes Workday, CrossCountry Healthcare, Hiring.cafe, aiApply, scale.jobs, LoopCV and Tink. Second, OJCP is not a rival to the Model Context Protocol. The specification says it outright: "OJCP is not a competing protocol. It is a vertical application of MCP for the job data domain." MCP defines how agents call tools; OJCP defines which tools exist for job search, application and identity verification.

## What Is the OJCP Job Data Protocol, and What Is It Not?

OJCP is a three-part contract. A discovery layer (the well-known manifest), a tool layer (six standard MCP tools), and a trust layer (signed manifests, registry tiers, agent identity, and PII-free identity verification). Everything else in the specification — the schemas, the apply-path taxonomy, the caching rules — exists to make one of those three parts work reliably at machine speed.

What it is not matters just as much, because most early coverage oversells it:

- **Not a replacement for your ATS.** OJCP sits above Workday, Greenhouse, Lever and the rest. The `ats_direct` apply path explicitly hands the application to the employer's existing ATS.
- **Not a new transport.** There is no OJCP wire protocol. Tools travel over MCP; discovery travels over plain HTTPS.
- **Not a job board.** No provider is obliged to publish a public feed, and none of the current implements does so at scale.
- **Not finished.** The repository describes v0.2 as "a living draft," and section 17 of the specification is literally titled Open Questions.

### The Thesis Behind the Standard: Inference Cannot Produce Authorization

The most useful sentence in the entire project comes from the spec author's Hacker News comment: "Inference can't produce authorization… a more capable agent is also a more capable impersonator."

Unpack that and the design stops looking arbitrary. A modern LLM agent can read any application form, infer what each field wants, and fill it convincingly. What it cannot do is establish that a specific human authorized this specific submission to this specific employer. Inference is a capability claim; authorization is a consent claim. No amount of model quality converts one into the other. Every trust mechanism in OJCP — signed agent requests, registry trust tiers, consent scopes, verification proofs — exists because the protocol author took that distinction seriously rather than assuming a smarter agent is a safer agent.

## Why Scraping Career Pages Broke: The AI Application Flood in Numbers

The problem OJCP targets is not hypothetical, but it is also not as well measured as vendor marketing implies. Worth separating the evidence tiers.

**Numbers that trace to primary reports:**

| Finding | Figure | Source |
|---|---|---|
| Job seekers ghosted by an employer in the past year | 53% (up from 48% in 2025 and 38% in 2024) | Criteria Corp, 2026 Candidate Experience Report, covered by Fortune (March 2026) |
| Job seekers who have used AI to apply for jobs | 34% | Criteria Corp, 2026 Candidate Experience Report |
| Annual applications handled per recruiter | 746 in 2025, up from 146 in 2022 (a 411.8% increase) | Greenhouse, The Hire Standard benchmark, March 2026 |
| Post-interview ghosting | 61% of job seekers | Greenhouse, State of Job Hunting survey |

The Criteria Corp report is based on responses from more than 2,500 job seekers worldwide; the Greenhouse benchmark draws on more than 640 million applications from 2022 to 2025. Greenhouse's own summary is blunt: "Applications surged while recruiting teams shrunk."

**Numbers that are vendor estimates, not research.** Recruitics' launch release states that about 70% of job seekers already use AI tools in their job search, that AI bots already generate more web traffic than humans, and that large employers now see nearly one-third of inbound applications coming from AI agents, mostly mismatched. Those three figures are labeled in the release itself as industry estimates with no primary study cited behind them. Treat them as directional. Note also that the Criteria Corp primary data reports 34% AI use in applying — materially lower than the 70% figure commonly repeated, which is a reminder to check the primary source before quoting.

### Why the Technical Failure Mode Matters More Than the Volume

Volume is a symptom. The mechanism is that the current integration surface is a human UI. As the spec author put it on Hacker News, applying agents today scrape career pages and "fight ATS forms with Playwright/Browser Use, which breaks constantly (or they get bot blocked)."

That brittleness has three consequences recruiters feel directly. First, an agent that cannot read a form accurately submits misaligned applications, which is exactly the "low-quality, mismatched" pattern Recruitics describes. Second, an agent that cannot see structured requirements cannot pre-assess fit, so it applies everywhere — which is why applications per recruiter ran to 411% growth. Third, an agent that cannot verify who it acts for has no way to distinguish a legitimate candidate-side assistant from an impersonator, which is why the protocol spends whole sections on identity rather than treating it as an afterthought.

A job board or ATS that publishes a machine-readable contract removes all three failure modes at once. That is the whole argument for OJCP in one sentence.

## How OJCP Works End to End: Manifest, Six MCP Tools, Seven Schemas

The implementation surface is smaller than the specification's 18 sections suggest. Four concepts carry it.

### Step 1: Manifest Discovery at /.well-known/ojcp.json

A provider publishes a JSON manifest at a fixed path. The HTTP response MUST carry `Content-Type: application/json`. The fields divide into three obligation tiers:

| Field | Obligation | Purpose |
|---|---|---|
| `ojcp_version` | MUST | Declares conformance version; accepts `"0.1"` and `"0.2"` |
| `provider.name` | MUST | Human-readable provider identity |
| `tools` | MUST | Array of implemented tool names |
| `mcp_endpoint` | SHOULD | URL an MCP client calls |
| `feed_endpoints` | SHOULD | Non-MCP job feed URLs |
| `apply_paths` | SHOULD | Declared application mechanisms |
| `auth` | SHOULD | Authentication requirements, including `agent_signatures` support |
| `rate_limits` | SHOULD | Declared request ceilings |
| `supported_verifiers` | SHOULD | Identity verifiers the provider accepts |
| `resume_upload` | MAY | Resume ingestion details |
| manifest signature | MAY | JWKS-backed integrity proof |

The manifest is deliberately cheap. A provider can publish one before implementing a single tool and still be discovered, which is the intended adoption on-ramp.

### Step 2: The Six Standard MCP Tools

Only one tool is mandatory.

| Tool | Status | What it does |
|---|---|---|
| `search_jobs` | MUST implement | Returns job postings matching query parameters |
| `get_job_detail` | RECOMMENDED | Full posting for one job identifier |
| `get_employer_context` | RECOMMENDED | Employer-level context for fit reasoning |
| `begin_application` | RECOMMENDED | Opens an application session |
| `submit_application` | RECOMMENDED | Submits against an open session |
| `check_application_status` | RECOMMENDED | Polls application state |

Provider-specific tools MUST use namespaced names in the form `{provider}:{tool_name}` — `acme:get_referral_link` or `greenhouse:schedule_interview`. Bare names are reserved for the six standard tools, and agents MUST recognize them. The namespace rule is what stops a provider from silently redefining `search_jobs` semantics for its own convenience; custom tools self-describe through MCP's standard `tools/list`.

### Step 3: The Seven Core Schemas

`manifest.json`, `job-posting.json`, `candidate-context.json`, `agent-declaration.json`, `eeo-data.json`, `verification-step.json`, `verification-proof.json` (plus `verifier-manifest.json` and separate input/response schemas under `tools/` and `responses/`).

Two details in this layer deserve attention. `job-posting.json` extends `schema.org/JobPosting` rather than replacing it, so existing structured data stays valid and SEO investment is not thrown away. OJCP adds domain fields on top: `skills_required`, `skills_preferred`, `team_context`, `urgency`, `application_volume_signal`, `requisition_id`, `department`, `hiring_manager`, `remote_policy` and `agent_notes` among them.

### Step 4: The Four-Step Agent Flow

A conforming agent's happy path runs: fetch and validate the manifest, call `search_jobs` with consent-scoped constraints, call `begin_application` with an `AgentDeclaration`, then `submit_application` and later `check_application_status`. Rate and freshness rules are normative rather than advisory — re-fetch a manifest at most hourly (`max-age=3600`), never cache search results longer than 15 minutes (`max-age=900`), cache `get_job_detail` for up to an hour, and never reuse an application session token (recommended TTL: 30 minutes).

Rate limits are enforced in both REST and MCP dialects: HTTP `429` with `Retry-After` on REST, JSON-RPC error `-32029` with `retry_after_seconds` on MCP. Agents must not retry before the window closes and should back off exponentially with jitter. These are the details that separate a spec you can implement from one you merely read.

## The Naming Gotcha: camelCase Fields Next to snake_case Tools

Section 4.1 contains the kind of detail that only appears if you actually read the specification. Fields inherited from schema.org keep their camelCase spelling — `employmentType`, `experienceLevel`, `jobLocation`, `baseSalary`. OJCP extension fields and tool parameters are snake_case — `skills_required`, `team_context`, `urgency`, `salary_min`.

Agents SHOULD handle both conventions. Implementers who normalize everything to one style break schema.org compatibility; implementers who do not normalize at all write field-mapping bugs on the first integration. Write the mapping table once, in one place, and test it against the conformance suite.

## Apply Paths: The Normalized Taxonomy and What supports_agent_submission Means

This is the single most useful artifact on the project site, because it converts a vague question ("can an agent apply here?") into a declared enum.

| Apply path type | Description | Agent submission support |
|---|---|---|
| `provider_hosted` | Provider controls the apply flow and delivers to the ATS | Full support |
| `ats_direct` | Apply directly via the ATS (Workday, Greenhouse, Lever and similar) | Varies |
| `platform_native` | A third-party platform owns the flow (Indeed Apply, Easy Apply) | Limited |
| `custom` | Catch-all for non-standard mechanisms (homegrown, conversational) | Varies |
| `email` | Legacy email-based application | Not supported |
| `external_redirect` | Redirect to an opaque external page | Not supported |

Read the table as an investment signal. If you are a job board and you declare `provider_hosted`, you are committing to own the application flow end to end — including delivery into the employer's ATS — and you unlock full agent submission. If you declare `email`, you have told every conforming agent to stop, which is honest but also a statement that your pipeline is not agent-addressable.

The `ats_direct` row is where the honest complexity lives. "Varies" is doing real work: whether agent submission works depends on the ATS vendor, the customer's configuration, and whether that vendor has adopted OJCP itself.

## Consent-Scoped Candidate Data: Fit Scoring Without Transmitting a Resume

The privacy architecture is the part of OJCP worth stealing even if you never adopt the standard.

`CandidateContext` is scoped by a consent ladder with four rungs, and each rung opens exactly the fields it needs:

| Consent scope | Fields it unlocks |
|---|---|
| `search_personalization` | skills, experience_years, location and employment preferences |
| `fit_scoring` | current_title, salary_expectation, work_authorization, `resume_embedding_hash` |
| `application_prefill` | name, email, resume_url |
| `full_profile` | Everything else the provider supports |

The normative behavior is the interesting part. A provider MUST drop out-of-scope fields rather than reject the request wholesale, and SHOULD emit a warning describing what was dropped. That inverts the usual API contract: instead of failing loudly and forcing the agent to resend with more data, the provider degrades gracefully and tells the agent what it could not use.

`resume_embedding_hash` is the field that makes the design work. A candidate-side agent can send a hash of a resume embedding so the provider can compute a fit score without ever receiving resume text — the ranking happens as a similarity operation over vectors, not as a document transfer. The provider returns `fit_score` and `fit_rationale` with search results, which is what lets a well-behaved agent decide *not* to apply to a mismatched role. That is the direct answer to "agents cannot assess fit before applying."

Note the design tension, though: fit scoring on an embedding hash still leaks information about a candidate to a provider that has not been authorized to hold their resume. The consent ladder is a meaningful improvement over sending the full document, not a proof of privacy. Whether an embedding hash is genuinely non-invertible against a known corpus is an open research question the specification does not settle.

## Trust in Both Directions: Agent Identity, Signed Manifests, JWKS and Registry Tiers

OJCP treats trust as a runtime input to agent behavior rather than a badge on a provider page.

**Provider side.** Manifests can be signed, with key discovery through a JWKS endpoint and a defined key-rotation procedure. The registry assigns one of three trust tiers:

| Trust tier | Requirements | Agent obligation |
|---|---|---|
| unverified | Manifest parses | Cap consent scope; withhold sensitive fields |
| verified | Signed manifest plus confirmed employer identity | Normal consent scopes permitted |
| audited | Passes conformance suite, security review, and 90 days with no abuse reports | Highest trust; widest scopes permitted |

Agents MUST cap `consent_scope` for weakly trusted providers and MAY filter results using a `min_trust_tier` parameter. This is the mechanism that makes trust actionable: a low-trust provider does not get a resume URL because the agent's own policy forbids transmitting it, regardless of what the provider requests.

**Agent side.** Section 8, backed by RFC 0001, gives agents a verifiable identity using HTTP Message Signatures (RFC 9421) on the Web Bot Auth wire profile. Ed25519 is recommended. The agent publishes keys at a signatures directory, names its key via the `Signature-Agent` header, and providers declare support under `auth.agent_signatures`. Origin binding uses the Public Suffix List.

The critical caveat is stated by the specification itself: a verified agent identity is a *hint about the agent*, not proof that a human authorized the action. Which is why the optional `user_mandate` on `AgentDeclaration` exists — and why RFC 0003, "action-bound user mandates," is still in progress. Identity and authorization remain two separate problems, and OJCP is honest that it has only solved the first.

## Identity Verification Without PII: ID.me, Clear and the subject_hash Trick

If an employer needs to know that the person applying is a real, verified individual — a genuine requirement in healthcare, finance and many regulated roles — OJCP provides a way to prove it without routing personal data through the protocol at all.

A third-party Identity Verifier (ID.me and Clear are the named examples) issues a JWS or JWE proof. Required claims are `iss`, `aud`, `sub`, `iat`, `exp` and `nonce`. The `nonce` is set to the `application_id`, which prevents replay across applications. Signing algorithms are ES256 (recommended), RS256, ES384 and RS384. Verifiers publish keys at `/.well-known/ojcp-verifier.json`, including `signing_algorithms` and a `public_keys_url` pointing at a JWKS.

The payoff: instead of the candidate's name, date of birth, address or government identifier, the proof carries a `subject_hash` — a SHA-256 hash of a canonical subject identifier, which the specification requires to be non-reversible. The employer learns "this verified person is the same person who applied" without learning anything else about them through this channel.

Two delivery models change your architecture, so pick deliberately:

| Model | How the proof travels | Agent behavior |
|---|---|---|
| `agent_submitted` | Verifier returns the proof to the agent; the agent includes it in `submit_application` | Agent carries and transmits the proof |
| `provider_managed` | Verifier delivers the proof straight to the provider via callback or iframe `postMessage` | Agent MUST NOT include proofs; provider polls |

`agent_submitted` is simpler to build and keeps the agent in control of the flow. `provider_managed` removes the proof from the agent's possession entirely, which is stronger from a data-minimization standpoint but requires the provider to implement an asynchronous polling path and a defined abandonment flow for sessions that never complete.

## WebMCP: Making an Existing Careers Page Agent-Ready Without a Server

Almost nobody writes this section up, and it is the cheapest path for a mid-size employer that will never stand up an MCP server.

WebMCP gives browsers two ways to expose tools to agents. The imperative route calls `document.modelContext.registerTool()` from page JavaScript. The declarative route requires no JavaScript at all: annotate existing HTML apply forms with `toolname`, `tooldescription` and `toolparamdescription` attributes, and the browser translates the annotated form into a tool an agent can call.

Detection is handled by the platform: a `SubmitEvent` exposing `agentInvoked` tells your existing submit handler that a non-human actor triggered the form. A provider can then apply different validation, different rate limits, or an identity-proof requirement to agent submissions while leaving the human path untouched.

The practical implication is that a careers page does not need to choose between "deploy an MCP server" and "stay scrapeable." Form annotations plus a `/.well-known/ojcp.json` manifest make an existing page agent-addressable in an afternoon, and the same tools work in the browser and over MCP. The project treats this as a documented interoperability path, and it is the strongest near-term adoption argument in the specification.

## Building an OJCP Provider: A Minimal Working Walkthrough

The implementation path, in dependency order.

**1. Publish the manifest.** Write `/.well-known/ojcp.json` and serve it as `Content-Type: application/json`. Include `ojcp_version`, `provider.name` and `tools`. Verify it validates:

```bash
npx @ojcp/conformance validate manifest.json
```

**2. Implement `search_jobs` first.** It is the only mandatory tool, and a provider that implements nothing else can still be listed and called. Return an array of postings whose first element validates against the JobPosting schema.

**3. Expose the tools over any MCP-compatible transport.** The reference provider uses `https://ojcp.dev/api/mcp`. Nothing OJCP-specific is required at the transport layer — this is exactly why "an agent that speaks MCP already speaks OJCP."

**4. Run the full conformance suite against your live domain.**

```bash
npx -y @ojcp/conformance https://your-provider.example
```

The suite runs ten named checks: manifest-valid, manifest-has-version, manifest-has-tools, manifest-has-search-jobs, manifest-has-mcp-endpoint, mcp-endpoint-reachable, search-jobs-returns-jobs, search-jobs-valid-schema, get-job-detail-returns-job and begin-application-returns-session. The conformance repository publishes a sample run against the reference provider reading "10 passed, 0 failed, 0 skipped" with 8 jobs returned — a reproducible baseline you can compare against.

**5. Register and get graded.** Add a provider entry to the registry repository by pull request: one reviewed JSON file per provider, with domain control proven by a signed manifest or a DNS TXT record. Registration surfaces the provider through the `find_ojcp_providers` MCP discovery tool, filterable by industry, employer name, location, `has_agent_apply` and `min_trust_tier`.

### The Conformance Reality Check You Should Reproduce Yourself

Here is the finding that no marketing page will tell you. Running the latest published conformance suite (v0.1.0) against the live reference provider on 2026-10-01 returned **8 passed, 2 failed**, not the 10/10 printed in the repository README:

```
npx -y @ojcp/conformance https://ojcp.dev
→ 8 passed  2 failed  0 skipped
```

Both failures — `manifest-valid` and `search-jobs-valid-schema` — report the same root cause: `/apply_paths/0: must be equal to one of the allowed values`. The live provider still emits the older string-form `apply_paths` array (`["provider_hosted", "ats_direct"]`, confirmed by fetching the manifest directly), while the published schema now expects apply-path *objects* carrying a `type` field.

This is a version-skew bug, not a collapse of the standard, and it has a clean explanation: the README's 10/10 figure is a published sample from an earlier state, while the draft has since moved on. But it is a genuinely useful signal for anyone planning to implement. The reference implementation is running behind its own schema, which means the conformance suite is strict enough to catch real drift — and that you should run it against your own endpoint before claiming conformance, not trust a README table.

Treat the pass counts in any published baseline as sample output, and re-verify before you publish numbers of your own. Conformance tooling also moves; the suite version you pull today may not be the version that graded last week's provider.

## OJCP vs Open Job Protocol (OJP/OTP) vs schema.org JobPosting

Three standards get compared to each other constantly, and they are not competing for the same slot.

| Standard | What it actually is | Layer | License | Adoption today |
|---|---|---|---|---|
| OJCP | MCP tool surface plus manifest discovery plus a trust and verification model | Protocol | CC BY 4.0 (spec), Apache-2.0 (code) | 3 implementing providers, 1 evaluating |
| Open Job Protocol (OJP) + Open Talent Protocol (OTP) | A vendor-neutral JSON document standard; OJP covers the job, OTP the candidate profile | Data format | MIT | Early; validator CLI and migration guides published |
| schema.org/JobPosting | Structured data markup embedded in web pages | SEO markup | Open W3C community vocabulary | Very wide — it is what search engines read |

The distinctions that matter when you decide what to build:

**OJCP is a protocol.** It defines tools, discovery, trust tiers and identity verification. It does not define a document format you can drop into a database; it defines how an agent asks for documents and how it proves who it is.

**OJP is a format.** A valid OJP v0.2 document needs ten required top-level fields (`schema_version`, `ojcp_id`, `created_at`, `updated_at`, `status`, `title`, `description`, `employment_type`, `organization`, `location`), uses flat snake_case keys with `additionalProperties: false`, and uses the ESCO skills taxonomy with a `must_have` / `nice_to_have` split agents can rank on. It is MIT licensed with no required registry or platform. Its own positioning is pointed: "schema.org/JobPosting serves Google, not hiring agents."

**schema.org/JobPosting is markup.** It exists primarily so search engines can render rich results. OJCP extends it rather than replacing it, which means your existing markup investment is not wasted — but neither standard treats markup as a sufficient agent contract.

No cross-standard adapter between OJCP and OJP is documented. If you are an employer with limited engineering time, the sequencing that wastes nothing is: keep your schema.org markup (search engines still matter), publish an OJCP manifest with `search_jobs` if you want agent traffic, and only then evaluate a full OJP export if a downstream system asks for one. As a decision heuristic for this quarter: a job board should implement OJCP's manifest and `search_jobs`; an enterprise with a single ATS should annotate forms for WebMCP; a data pipeline team with no agent traffic should not implement either yet.

## The Honest State of OJCP in 2026: Draft Spec, Thin Adoption, Governance Friction

The coalition is real. The adoption is not yet.

**What is verifiably live:** the repository at `ojcp-org/ojcp` shows 80 stars, 6 forks and 4 open issues, created 2026-04-22 and last pushed 2026-09-24, Apache-2.0 licensed. The reference provider at `ojcp.dev` answers with a valid manifest declaring all six tools. FoundRole runs an anonymous read-only MCP endpoint live since 2026-08, and freehire serves read-only search and detail over both REST and MCP since 2026-09. `reqspace.ai` is listed as evaluating.

**What is thin:** the companion repositories tell a sharper story than the star count. The conformance suite repository has 3 stars; the registry repository has 0 stars and has not been pushed since the day it was created (2026-08-10). The three implementing organizations are Recruitics's own reference provider plus two small read-only providers. No major ATS is running a public OJCP endpoint, and consumer tooling is only indirectly available — the spec author has said OJCP "might soon be implemented into" the open-source Job-Ops project.

**Where the marketing and the repo disagree.** `ADOPTERS.md` lists Recruitics as the only seated steering member and still marks six of the nine seat rows "Open — Nominations welcome," while `GOVERNANCE.md` names nine holders. The project site's footer says Recruitics holds "one seat of seven" while the governance page says nine. The site's star badge reads "Star 52" against a GitHub API result of 80 — a stale badge, but a reminder to audit marketing surfaces against the API. And as covered above, the reference provider currently fails 2 of 10 of its own conformance tests.

**The governance design deserves credit, not just scrutiny.** `GOVERNANCE.md` specifies a nine-seat committee with one seat per company and no veto, a diversity constraint capping seats per market segment, an odd-number requirement, and an eleven-seat ceiling with two-year renewable terms. Most importantly, until 5 of 9 seats are filled by ratified appointees, all spec-affecting decisions require a public RFC with a minimum 30-day comment window plus documented rationale in `docs/decisions/`. Nominations were targeted to open 2026-05-01 with confirmed appointees by 2026-06-01 — dates the seat table, last reviewed 2026-07-28, shows were not met.

**The Hacker News reception was modest and partly skeptical.** The Show HN ran twice: 11 points and 2 comments on 2026-08-11, then 39 points and 10 comments on 2026-08-12. The main criticism was that the word "protocol" is diluted by an early single-vendor effort, and that reviewers could not find committee members other than Recruitics publicly listed. That second complaint is now partly answered — `GOVERNANCE.md` lists all nine holders — and the criticism itself is a fair signal of how much of this standard still rests on one company's execution. Recruitics has since committed to moving the project's infrastructure to a neutral open-source foundation before v1.0, which is the right answer to the concern if it is honored.

**The versioning discipline is genuinely good.** v0.1 published 2026-03-06; v0.2 published 2026-09-22 as a minor, additive change. The schema `$id` namespace deliberately stays at `/v0.1/` and `ojcp_version` accepts both `"0.1"` and `"0.2"`, so existing providers keep validating through the bump. v0.2 added verifiable agent identity, `url` and `official_job_url` on JobPosting as candidate-facing trust anchors, the `"0.2"` version string, and the governance and adopter documentation. An unreleased change tracked in issue #19 will let `jobLocation` accept an array of places so a multi-location posting can state every accepted location — with an explicit rule that providers MUST NOT reduce a multi-location posting to a single location.

## What to Watch

Four things will determine whether OJCP becomes infrastructure or remains a well-documented draft.

**Seat ratification.** The bootstrap RFC rule exists until 5 of 9 seats are ratified. Watch whether the six open rows fill with independent organizations — that single fact converts a vendor standard into an actual multi-party one.

**Registry maturity.** The registry is the discovery layer, and it is the thinnest part of the project: 0 stars, no pushes since creation, and `registry.ojcp.dev` does not resolve. A registry with a handful of verified employers changes the adoption conversation completely.

**Action-bound user mandates (RFC 0003).** The consent architecture is sound, but the authorization gap the author identified himself remains open. Until `user_mandate` is standardized, agent identity proves *who* is acting, not *that the human agreed*.

**Convergence with OJP.** Two unrelated JSON-plus-tool standards for the same problem is a familiar early-market pattern. Either the two projects converge on an adapter, or one becomes the default through adoption, or both stall as interesting drafts. If you are building a candidate-side agent today, wrap your internal format in an adapter layer so you can speak to either without a rewrite.

## Frequently Asked Questions About the OJCP Job Data Protocol

### Is OJCP the same as Ontario Job Creation Partnerships?

No. The acronym collision is unfortunate. Ontario Job Creation Partnerships is a Canadian government employment program administered by the Government of Ontario. OJCP in this article is the Open Job Context Protocol — an open specification for agent-consumable job data, authored by Austin Anderson (CTO of Recruitics) with a steering committee including Workday, CrossCountry Healthcare, Hiring.cafe, aiApply, scale.jobs, LoopCV and Tink. If your search results are showing provincial labour program pages, you want the other meaning.

### Does OJCP replace my ATS?

No. OJCP is a layer above the ATS, not a substitute for it. The `ats_direct` apply path explicitly routes applications to your existing system (Workday, Greenhouse, Lever and similar), and the `provider_hosted` path has the job board or provider control the flow and deliver into the ATS on your behalf. Your ATS remains the system of record. What OJCP changes is how agents reach it: through a discovered manifest and typed MCP tools instead of scraping and form-fighting.

### Is OJCP just MCP with a job schema bolted on?

Not quite — it is a vertical application of MCP, and that framing is deliberate rather than dismissive. MCP supplies the transport and the tool-calling convention; OJCP supplies the domain contract: which six tools exist, what a job manifest must declare, how apply paths are normalized, how consent scopes gate candidate fields, and how provider trust and agent identity are verified. The practical consequence is that an MCP client needs no new transport code to speak OJCP — it needs to discover a manifest. That is the standard's strongest adoption argument, and also why it adds capability rather than competing.

### Is OJCP free to implement, and what does it cost me in engineering time?

The specification and schemas are CC BY 4.0 and the code and tooling are Apache-2.0, so licensing costs nothing. Engineering cost depends on how far you go. The minimum viable step — publishing `/.well-known/ojcp.json` with `search_jobs` — is measured in hours for a team that already has a job API. Full support, including `begin_application`, `submit_application`, consent-scoped `CandidateContext`, signed manifests and identity verification, is a real project. The recommended sequence is to ship the manifest and `search_jobs`, run `npx @ojcp/conformance` against your live domain, and only then decide whether the apply flow is worth owning.

### Can a job seeker use OJCP today?

Indirectly, and not as a product. There is no consumer OJCP app. What exists is a candidate-side agent ecosystem: `reqspace.ai` is listed as evaluating a candidate-side auto-apply agent built on `AgentDeclaration`, and the spec author has said OJCP may be adopted into the open-source Job-Ops tooling. The candidate-visible benefit is architectural rather than immediate — `check_application_status` turns application status into a required, pollable API for conforming providers, which reframes ghosting from a cultural complaint into a data-availability problem. If a provider can be called and simply does not answer, that is now a schema violation rather than a rude silence, which matters given that Criteria Corp's 2026 research found 53% of job seekers were ghosted in the past year.

## Sources

- OJCP specification (v0.2 draft, 18 sections): https://spec.ojcp.dev/0.1/
- OJCP project site and live reference provider: https://ojcp.dev/
- Reference provider manifest: https://ojcp.dev/.well-known/ojcp.json
- Specification repository: https://github.com/ojcp-org/ojcp
- Governance charter: https://github.com/ojcp-org/ojcp/blob/main/GOVERNANCE.md
- Adopter list: https://github.com/ojcp-org/ojcp/blob/main/ADOPTERS.md
- Change history: https://github.com/ojcp-org/ojcp/blob/main/CHANGELOG.md
- Conformance suite: https://github.com/ojcp-org/conformance
- Provider registry: https://github.com/ojcp-org/registry
- Recruitics launch press release: https://info.recruitics.com/resources/recruitics-leads-launch-of-open-source-standard-to-end-the-ai-job-application-crisis-clone
- Show HN thread: https://news.ycombinator.com/item?id=49273922
- Open Job Protocol: https://openjobprotocol.org/
- Criteria Corp, 2026 Candidate Experience Report: https://www.criteriacorp.com/research/2026-candidate-experience-report
- Greenhouse, The Hire Standard benchmark (March 2026): https://www.greenhouse.com/recruiting-benchmarks

Related reading on this site: [the MCP ecosystem explained](/posts/mcp-ecosystem-2026/), [AI agent identity frameworks](/posts/ai-agent-identity-framework-guide-2026/), [agent workflow planner/executor patterns](/posts/agent-workflow-mcp-planner-executor-2026/), [MCP vs A2A protocol comparison](/posts/mcp-vs-a2a-protocol-2026/), and [AI in HR and talent acquisition 2026](/posts/ai-hr-talent-acquisition-recruitment-2026/).
