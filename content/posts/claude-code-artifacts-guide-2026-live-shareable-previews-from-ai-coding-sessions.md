---
title: "Claude Code Artifacts Guide 2026: Live Shareable Previews from AI Coding Sessions"
date: 2026-06-30T12:00:00+00:00
tags: ["Claude Code", "AI Coding", "Developer Tools"]
description: "A practical guide to Claude Code artifacts: requirements, sharing, limits, security, prompts, and when to deploy a real app instead."
draft: false
cover:
  image: "/images/claude-code-artifacts-guide-2026-live-shareable-previews-from-ai-coding-sessions.png"
  alt: "Claude Code Artifacts Guide 2026"
  relative: false
schema: "schema-claude-code-artifacts-guide-2026-live-shareable-previews-from-ai-coding-sessions"
---

Claude Code artifacts are private, live-updating web pages generated from a Claude Code session. They are useful when terminal output is the wrong review surface: PR walkthroughs, incident timelines, architecture diagrams, and interactive summaries. They are not hosted apps, public previews, or replacements for a deployment pipeline.

I have found that the biggest value is not the visual polish. It is making an AI coding session inspectable by other engineers without forcing them to read a transcript, replay commands, or trust a summary. If Claude is debugging a deploy failure, reviewing a migration, or comparing UI states, an artifact gives the team one shared page that keeps changing as the session continues.

That value comes with hard constraints. As of June 30, 2026, the official [Claude Code artifacts documentation](https://code.claude.com/docs/en/artifacts) describes artifacts as a beta feature for Team and Enterprise plans. They publish to private `claude.ai` URLs, can only be shared inside the same organization, and render as a single self-contained page. External scripts, stylesheets, fonts, images, `fetch`, XHR, and WebSocket calls are blocked by the content security policy.

If you are choosing between this and a real preview deployment, decide early. Claude Code artifacts are great for reviewable session output. Use your normal hosting stack, or something like Codex Sites, when you need persistence, public access, authentication logic, backend calls, or customer-facing reliability.

## What are Claude Code artifacts?

A Claude Code artifact is a live, interactive page published from a Claude Code session. The source can be HTML, HTM, or Markdown, and Claude publishes it to a private URL on `claude.ai`. When the session updates the artifact, the same URL updates in place, so teammates do not need a new link for every revision.

In practice, this changes the shape of a coding session. Instead of asking Claude to "summarize what changed," you can ask it to build a review page:

```text
Create a Claude Code artifact that explains this PR for a senior reviewer.
Include the changed files, risk areas, test status, and links back to the local paths.
Use severity labels for anything that deserves attention.
```

That is a much better surface than a wall of terminal text. It can include tabs, filters, diagrams, collapsible sections, inline code snippets, and lightweight controls. The artifact is still just a page, but that is enough for a lot of internal review workflows.

The important distinction is that the artifact is generated from the session, not from a production app runtime. It can show data Claude pulled during the session, but it cannot call your API when a viewer opens the page. It can render a dashboard, but the dashboard is a captured view, not a live service.

If you are also evaluating general AI coding workflows, my earlier notes on [coding agent token waste reduction](/posts/coding-agent-token-waste-reduction-guide-2026/) pair well with artifacts. Rich visual output is useful, but it also increases context and token usage if you ask the agent to generate too much CSS, JavaScript, or embedded data every iteration.

## What are the requirements in 2026?

The requirements are stricter than many developers expect. This is not a generic Claude API feature that works everywhere Claude Code can run.

| Requirement | Current behavior |
|---|---|
| Plan | Team or Enterprise |
| Status | Beta |
| Authentication | Claude Code session signed in with `/login` |
| Supported clients | Claude Code CLI and Claude desktop app 1.13576.0 or later |
| Unsupported provider paths | API keys, gateway tokens, Amazon Bedrock, Google Vertex AI, Microsoft Foundry |
| Default availability | Off by default in Agent SDK, GitHub Action, and MCP-server contexts |
| Source files | `.html`, `.htm`, or `.md` |
| Rendered size | 16 MiB or smaller |
| Sharing | Creator by default, then authenticated members of the same organization |
| Public sharing | Not supported |

When building internal AI tooling, I would treat these as deployment requirements, not documentation trivia. The `/login` requirement alone matters because many teams run coding agents through gateway tokens or cloud-provider model endpoints. Those sessions may be perfectly valid for coding, but they cannot publish artifacts under the documented rules.

The desktop version requirement also matters if your organization standardizes developer environments. Claude desktop 1.13576.0 or later is listed as supported, but the CLI is usually the simpler path for engineers already working inside repositories.

## How do you create and publish an artifact?

The happy path is short.

1. Start Claude Code in the repository or working directory you want it to inspect.
2. Make sure the session is authenticated with `/login`, not only an API key path.
3. Ask Claude to create an artifact, or accept when Claude proposes one.
4. Review the publish prompt before anything is published.
5. Open the private `claude.ai` URL.
6. Continue the session and ask Claude to update the artifact as the work changes.

Here is a prompt I would actually use during a PR review:

```text
Create a Claude Code artifact for this branch.

Audience: senior backend reviewer.
Include:
- concise purpose of the change
- files changed, grouped by responsibility
- risky assumptions
- tests run and tests still missing
- a table of behavior before vs after
- unresolved questions for review

Keep it self-contained. Do not rely on external images, fonts, or network calls.
```

The last line is deliberate. Artifacts run with a strict CSP, so asking for external dependencies wastes time. I would rather nudge Claude toward inline CSS, inline JavaScript, SVG, and small embedded examples from the start.

For an incident investigation, I would use a different shape:

```text
Build an artifact that tracks this deploy failure investigation.
Show a timeline, suspected causes, commands already run, evidence found,
and the next three checks. Update the artifact after each new finding.
```

That gives an engineering manager or on-call partner something useful to inspect while the debugging session is still moving.

## How does sharing work?

Artifacts are private to the creator by default. From the artifact page, the creator can share with specific people or everyone in the same organization, depending on the available organization settings. Viewers must be authenticated members of that organization.

There is no public link mode in the official docs. That is a feature, not an inconvenience, for many enterprise uses. A PR walkthrough, migration plan, or production incident timeline often contains sensitive details. Keeping the share boundary inside the organization is the right default.

The trade-off is obvious: artifacts are poor fits for customer demos, open-source project updates, recruiting portfolios, or public launch pages. If you need a URL that anyone can open, deploy a real page.

Viewers can inspect the artifact and its versions, but they are not co-editing the session. The editing loop still belongs to the Claude Code session. If a teammate wants a change, they can ask the session owner to revise it, or the owner can start another session and provide Claude the artifact URL for context.

## What can you build with Claude Code artifacts?

I would start with use cases where a static report is too flat, but a real application would be overkill.

| Workflow | Why an artifact helps |
|---|---|
| PR walkthrough | Turns changed files, risks, and test status into one review page |
| Incident timeline | Keeps evidence, hypotheses, and next checks visible during debugging |
| Architecture explanation | Gives reviewers a clickable map instead of a prose-only summary |
| Migration checklist | Tracks completed and pending steps while Claude edits code |
| UI comparison | Shows interaction states, animation options, or component variants |
| Data investigation | Captures a session-derived dashboard without standing up a backend |

The best artifacts I have seen in similar workflows are opinionated. They do not try to become a complete portal. They answer one review question well: "What changed?", "What failed?", "Which option should we pick?", or "What is left before merge?"

For Claude-specific model behavior and agent trade-offs, the post on [Claude Sonnet 5](/posts/claude-sonnet-5-review-2026/) is a useful companion. Artifacts expose the output quality of the model more visibly than terminal logs do, so weak structure and vague reasoning become obvious quickly.

## Which prompts work well?

Good artifact prompts specify the audience, the decision being made, and the constraints of the page.

### How should I prompt for a PR artifact?

```text
Create an artifact for reviewers of this PR.
Audience: maintainers who know the codebase but have not followed this branch.
Show the intent, changed modules, behavior changes, risk table, and test evidence.
Add a "review first" section with the files most likely to hide regressions.
```

### How should I prompt for a debugging artifact?

```text
Create a live investigation artifact for this production issue.
Use sections for timeline, signals, ruled-out causes, current hypothesis,
commands run, and next actions. Update it whenever we learn something new.
```

### How should I prompt for an architecture artifact?

```text
Build a single-page architecture artifact for this service.
Include the main runtime components, storage dependencies, external integrations,
request flow, failure points, and ownership notes. Use inline SVG if helpful.
```

### How should I prompt for a UI artifact?

```text
Create an artifact comparing three interaction designs for this component.
Include controls for viewing default, hover, loading, error, and disabled states.
Keep all CSS and JavaScript inline. Do not import external assets.
```

### How should I prompt for a migration artifact?

```text
Turn this migration plan into an artifact.
Show phases, prerequisites, rollback plan, verification commands, and owner notes.
Mark completed items as we finish them in the session.
```

These prompts work because they avoid asking for a generic "dashboard." The artifact should reflect the work currently happening inside Claude Code.

## Why is an artifact not an app?

This is the part teams need to internalize before they build process around artifacts.

Claude Code artifacts are single self-contained pages. The CSP blocks external scripts, stylesheets, fonts, images, `fetch`, XHR, and WebSocket calls. Artifacts cannot store form input, call a backend at view time, authenticate users themselves, or serve multiple routes.

That makes several common ideas non-starters:

| Idea | Why it does not fit |
|---|---|
| "Let's make a support dashboard" | No live backend calls or persistent database |
| "Let's collect reviewer feedback in the artifact" | No durable form storage |
| "Let's share this with customers" | No public sharing |
| "Let's use our design system CDN" | External scripts, styles, fonts, and images are blocked |
| "Let's build a multi-page internal tool" | Artifact is one self-contained page |

There is still room for interactivity. You can use inline JavaScript for tabs, filters, accordions, charts from embedded data, and small state changes in the browser. But the data has to ship with the artifact. If the viewer needs fresh data from a service, the artifact is the wrong surface.

The 16 MiB rendered-size limit also shapes design. Large base64 images, huge JSON blobs, and verbose generated JavaScript can push you over the limit quickly. In practice, I would ask Claude to summarize large datasets, use tables only where they add value, prefer inline SVG for diagrams, and avoid embedding screenshots unless the screenshot is central to the review.

## How do Claude Code artifacts compare with Codex Sites?

Claude Code artifacts and OpenAI Codex Sites solve different problems. The names sound adjacent because both can produce browser-viewable output from AI coding work, but the runtime model is different.

The official [Codex Sites documentation](https://developers.openai.com/codex/sites) describes a hosted site and app deployment surface with save and deploy stages, production URLs, Cloudflare Worker-compatible output, D1 database storage, R2 object storage, and access controls. That is much closer to an app hosting workflow.

| Capability | Claude Code artifacts | OpenAI Codex Sites | Lovable, Bolt, and v0 |
|---|---|---|---|
| Primary job | Share session output as a live internal page | Create and host websites, apps, and games | Generate apps or UI from prompts |
| Persistence | None | D1 database and R2 object storage available | Varies by tool and runtime |
| External network at view time | Blocked by CSP | Supported by hosted app runtime | Varies by deployed app |
| Sharing | Private by default, same organization only | Workspace, custom, or public access modes depending on project | Often external deployment or code export |
| Best use | PR walkthroughs, investigation timelines, internal diagrams | Durable internal tools, dashboards, games, and hosted sites | Greenfield app generation or production UI components |
| Wrong fit when | You need a backend, public link, persistence, or runtime APIs | You only need a lightweight session report | You need a session-native record grounded in Claude Code context |

My decision rule is simple: use artifacts when the output is part of the coding conversation. Use a deployment surface when the output needs to behave like software after the conversation ends.

The security angle is similar to the trade-offs in [Claude Code network sandboxing](/posts/claude-code-network-sandbox-socks5-null-byte-bypass-guide-2026/). Restricting network behavior reduces certain classes of risk, but it also means you cannot pretend the restricted surface is a general runtime.

## What should admins and security teams check?

For Team and Enterprise use, I would not roll artifacts out casually. They are private, but they can still expose internal codebase context, incident details, environment names, architectural diagrams, and sensitive operational notes to a wider internal audience.

Use this checklist before making artifacts part of team workflow:

| Check | Why it matters |
|---|---|
| Confirm feature enablement | Admins can enable or disable artifacts |
| Set retention policies | Private and shared artifacts may need different retention expectations |
| Review audit events | Artifact creation, sharing, and deletion should be observable |
| Allowlist viewer domains | Corporate networks may need access to `claude.ai` and sandboxed `*.claudeusercontent.com` |
| Define sharing rules | Engineers need to know when "everyone in org" is too broad |
| Use compliance tooling | Enterprise teams can list, retrieve, and delete artifacts through compliance workflows |
| Avoid unsupported environments | Check official constraints for HIPAA, CMEK, and Zero Data Retention orgs before rollout |

I would also write a short internal policy: no secrets, no customer personal data, no production tokens, no full incident dumps unless the incident channel already permits that audience. Artifacts are easier to consume than logs, which means mistakes spread faster.

## How do you troubleshoot common failures?

Most failures I would expect come from availability assumptions, not from HTML bugs.

### Why did Claude create local HTML instead of a share link?

Check the basics first:

1. The workspace is on Team or Enterprise.
2. The session is authenticated with `/login`.
3. The session is not using an API key, gateway token, Bedrock, Vertex AI, or Microsoft Foundry path.
4. The client is Claude Code CLI or Claude desktop 1.13576.0 or later.
5. Organization admins have enabled artifacts.
6. You are not in an Agent SDK, GitHub Action, or MCP-server context where artifacts are off by default.

If those are not true, Claude may still generate an HTML file, but that is not the same as publishing a Claude Code artifact.

### Why did publishing fail because of size?

Reduce embedded data. Ask Claude to remove base64 screenshots, summarize large arrays, replace raster images with inline SVG where possible, and split verbose sections into concise tables. The rendered artifact must stay at or under 16 MiB.

### Why can a teammate not open the artifact?

Verify that the artifact was shared with them or with the organization, that they are authenticated, and that they belong to the same organization. There is no public fallback link.

### Why is my chart not loading?

If the chart depends on a CDN library, external stylesheet, remote image, or runtime data fetch, it will not work under the documented CSP. Ask Claude to rewrite it with inline JavaScript and embedded data.

### Can I update an artifact from a different session?

Yes, but do not assume Claude can discover it automatically. Provide the artifact URL in the new session and ask Claude to revise it. I would still keep important source material in the repo or issue tracker, because the artifact should not become the only durable record.

## When should you use an artifact instead of a deployment?

Use a Claude Code artifact when the page is a communication layer around the session:

| Use an artifact when... | Deploy a real app when... |
|---|---|
| The audience is internal | The audience includes customers or the public |
| The data can be captured during the session | The data must be live at view time |
| One page is enough | You need routes, auth flows, or navigation |
| Review is the goal | Ongoing operation is the goal |
| No persistence is required | Users must save or submit data |
| Org-scoped sharing is acceptable | You need custom access rules |

I would use artifacts for review, diagnosis, explanation, and alignment. I would not use them for long-lived dashboards, customer demos, admin panels, release portals, or anything that needs a backend. That boundary is what keeps the feature useful instead of turning it into a fragile shadow deployment system.

## FAQ

### What are Claude Code artifacts?

Claude Code artifacts are live, interactive pages that Claude Code publishes from a coding session to a private `claude.ai` URL. They can update in place as the session continues.

### Can Claude Code artifacts be shared publicly?

No. As of the June 30, 2026 research date, the official docs describe organization-scoped sharing only. Viewers must be authenticated members of the same organization.

### Do Claude Code artifacts have a backend?

No. They are single self-contained pages. They cannot store form input, call APIs at view time, authenticate viewers themselves, or serve multiple routes.

### What plans support Claude Code artifacts?

Claude Code artifacts are documented as a beta feature for Team and Enterprise plans. Check the official docs before rollout because beta availability can change.

### How are Claude Code artifacts different from Codex Sites?

Artifacts are private session captures for internal review. Codex Sites is a hosted deployment surface for websites, apps, and games, with production URLs, persistence options, and access controls.

