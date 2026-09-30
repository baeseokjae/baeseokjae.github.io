---
title: "Open Doc: The Document Framework Built for AI Agents"
date: 2026-09-30T04:15:07+00:00
tags:
  - document framework for ai agents
  - agent-native document framework
  - open-doc
  - open-doc review
  - open-doc tutorial
  - react documents for ai agents
  - ai agent report generation
  - ai agent pdf generation
  - print-fidelity documents agents
  - a4 page geometry react
  - mcp document server
  - mcp stateless streamable http
  - ai agent layout feedback loop
  - open-doc vs react-pdf
  - open-doc vs open-slide
  - headless pdf export cli
  - markdown to pdf agent workflow
  - open-doc check layout command
  - open-doc mcp 23 tools
  - document framework for ai agents 2026
  - open-doc vs pandoc typst
  - agent native documents 2026
  - open-document core npm
  - ai agent document workflow 2026
  - open-doc docx export
description: "open-doc is a React-first document framework for AI agents with real A4 page geometry and a layout checker — but 78 stars and no .docx export yet."
draft: false
cover:
  image: "/images/open-doc-document-framework-for-agents.png"
  alt: "Open Doc: The Document Framework Built for AI Agents"
  relative: false
schema: "schema-open-doc-document-framework-for-agents"
---

open-doc is an MIT-licensed, React-first document framework (`@open-document/core`) in which a coding agent writes each report as React components while the framework owns the paper: A4/B4/A3 page geometry, self-filling contents, page numbers, DOM-measured auto-pagination, layout diagnostics, and headless PDF/HTML/PNG/SVG export. It is genuinely early — 78 GitHub stars, one human contributor and 487 npm downloads last month (2026-09-30).

That gap is the whole story. If you are evaluating it, you are not choosing between a finished product and a finished product — you are deciding whether a well-argued, correctly-scoped design is worth reading end to end and trialling in an existing React/TypeScript shop.

## What open-doc actually is (and the one sentence that explains it)

The project's own description string is the article's title: *"The document framework built for agents."* Concretely:

- **Authored medium:** TSX. One document is one directory, `docs/<id>/index.tsx`.
- **Runtime:** a React renderer that renders a stack of real pages in the browser, plus a studio viewer with a live text inspector.
- **Agent surface:** 23 MCP tools mounted at `http://localhost:5273/mcp`, plus a set of skills that ship inside the scaffolder.
- **Verification surface:** `open-doc check`, a CLI that renders every page at true size and reports what broke, with source locations, exiting non-zero.
- **Output:** PDF (browser print pipeline), self-contained HTML, per-page PNG and SVG.

The one sentence that explains the design is the author's own analogy from the README: **"If open-slide is Google Slides for agents, open-doc is Google Docs."** A slide deck is a single 1920×1080 canvas — overflow is invisible because there is nowhere to overflow to. A document is a stack of A4 sheets that has to survive a printer, so it needs a page-break algorithm and, critically, a way to *tell someone when the algorithm failed*. That difference is why open-doc ships a layout checker and open-slide does not.

## The problem it names correctly — agents write well and format terribly

Most "AI document generation" tooling quietly assumes the hard part is prose. open-doc's opening argument is that the hard part is that the author cannot see the page. From the README, verbatim:

> "An agent writing React has no idea whether the paragraph it just added pushed the last three lines off the sheet."

That is a precise diagnosis, and it explains a failure mode anyone shipping agent-generated reports recognises: the model produces fluent, well-organised text, then the PDF arrives with a table split across two sheets, a heading stranded alone at the bottom of page 6, an image that silently failed to load, and three orphaned lines clipped past the trim edge. Nothing in the loop told the model. It wrote a plausible document and had no feedback channel to learn it was wrong.

The reframe is worth stating plainly because it is not obvious from the feature list: **open-doc's real product is the feedback loop, not the renderer.** The renderer is a browser print pipeline — the same one your browser's "Print to PDF" uses. The differentiator is that the agent can query the layout and get back "page 4 runs 37px past the sheet, at `p:41:12`" and then fix it.

## React as the authored medium: the file contract

The scaffold produces a workspace, and every document inside it is ordinary source:

```tsx
// docs/q3-report/index.tsx
export const meta: DocMeta = { /* title, theme, author, … */ };

export default [Cover, Contents, flow(<>, { footer: Footer })] satisfies DocEntry[];
```

Two authoring modes coexist in the same file: an array of **fixed pages** (`DocPage` entries, used for a cover or a contents page) and `flow(<>)` sections, which the framework paginates itself by measuring the real DOM rather than by estimating text heights.

The project states hard rules to the agent, and they are unusually disciplined: one `index.tsx` plus an `assets/` directory, **no sibling `.tsx` files**, no new dependencies, only `react` + `@open-document/core` + standard web APIs, and do not touch `package.json` or `open-doc.config.ts`. That last constraint matters more than it looks — it means an agent cannot "fix" a layout problem by adding a library, which is the single most common way agent-authored code degrades.

Why React at all, rather than a document DSL? The README's argument is that **React is a medium, not a format** — models have deep, heavily-trained priors on JSX, component composition and props, while a bespoke markup language is something a model must learn at inference time from a reference document. The bet is that fluent React beats awkward markup for the same author. The cost is equally real and worth naming: you inherit a browser print pipeline and its `@page` quirks, which the project has already hit once (a landscape `@page` descriptor bug fixed in 0.4.0).

## Real page geometry: A4, JIS B4 and A3, and why the list is short

open-doc deliberately supports exactly six sheets: **A4, JIS B4 (257 × 364 mm) and A3, each portrait or landscape.** Version 0.4.0 *removed* Letter, A5 and Legal.

That reads like an omission until you read the rationale: every supported sheet maps to paper a given print shop actually stocks, so a document always maps onto something a human can physically buy and bind. A4 is laid out at **794 × 1123 px @ 96 dpi** with a matching `@page` descriptor, so nothing is rescaled at print time — the px grid the framework lays out against *is* the print grid. Print fidelity here is a first-class constraint, not a rendering detail, and it is the thing that most distinguishes open-doc from a "generate an HTML file and hope" workflow.

## Auto-pagination that knows what not to break

Programmatic pagination is where most document generators embarrass themselves, usually by splitting a table down the middle. open-doc's packer carries explicit rules:

- **Headings never end a page** — a heading that would land at the foot of a page moves with its content.
- **Captions stay with their figures.**
- **Tables move whole** rather than splitting across sheets.

These are the same typographic rules a human typesetter applies, encoded as invariants the runtime enforces. The framework's page-break decisions are therefore deterministic with respect to content, not dependent on where an LLM guessed a `page-break` should go.

## The long-form furniture: footnotes, figures, cross-references and tables from CSV

The parts of document production that agents usually get wrong — numbering — are handled by the runtime:

- **`<Footnote>`** prints on whichever page its marker landed on, and the framework subtracts its height from that page's budget *before* the packer breaks the page. This is the detail that separates real pagination from decorative footnotes: the footnote can change where the page break falls.
- **`<Ref>`** renders "Figure 3" and adds "(p. 12)" only when the target is on another sheet.
- **`<ListOfFigures />` / `<ListOfTables />`** build the lists from the document itself.
- **`<DataTable>`** reads `.csv` / `.tsv` files at build time into arrays of objects, so table numbers stay synchronised with the prose around them, and numeric columns right-align with `tabular-nums` without being asked.

Numbering that maintains itself is a genuine correctness feature, not a convenience. Every manual figure number is a bug waiting for the next revision.

## The MCP server — 23 tools, stateless Streamable HTTP, and 409s instead of clobbered edits

Running `open-doc dev --mcp` mounts **23 tools** over stateless Streamable HTTP at `http://localhost:5273/mcp`, with no session handshake. Any MCP client can drive the document — including reading it, editing text, and rendering pages.

The design decision worth highlighting is that **the MCP tools and the browser UI share one implementation**. That is a correctness property, not an architectural elegance: it means a tool call and a human click cannot diverge in behaviour.

Concurrency is handled with optimistic concurrency control. Text writes take an `expected` value — the content the agent last read — and a write against stale content is **refused with HTTP 409 instead of silently clobbering a concurrent human edit**. For a collaborative authoring loop where a person is editing in the studio while an agent edits through MCP, this is the difference between a safe tool and a data-loss generator. Comments persist as `@doc-comment` markers that a later `/apply-comments` pass picks up.

## `open-doc check`: giving a blind agent eyes

This is the strongest, most checkable part of the project, and it is where the article's centre of gravity belongs.

`open-doc check` renders every page at true size and reports a concrete failure taxonomy:

| What the checker finds | Why it matters in print |
| --- | --- |
| Content clipped past the sheet edge | Lines silently disappear in the PDF — the most common agent failure |
| Blank sheets | Usually a stray page break or an empty `DocPage` |
| Headings stranded at a page foot | Reads as a formatting error to any human reviewer |
| Type too small to print legibly | Survives on screen, fails on paper |
| Images that failed to load | Renders as an empty box, invisible to a text-only agent |

Crucially, each finding carries a **source `line:column` locator** — the README's sample output reads like `p.4 content runs 37px past the sheet`, `p.7 image failed to load`, `p.6 heading ends the page`, each pointing back at the offending line. And the command **exits non-zero**, which means the same tool that advises an agent doubles as a CI gate. A pipeline can refuse to publish a document that overflows. That is the concrete answer to "how does an agent avoid clipped content on A4 pages" — not better prompting, but a check the agent can act on and a build that fails when it does not.

## Headless export and Markdown import

**Out:** PDF (browser print pipeline at true page size, so what you see is what prints), self-contained HTML (zipped when the document has assets), per-page PNG and SVG. Headless export needs an optional peer dependency — **playwright + chromium** — rather than a bundled browser. There is **no `.docx` export** (see limitations below).

**In:** `open-doc import notes.md --id q3-notes --contents` converts Markdown into a real document — a `flow()` body, a cover, a self-filling contents page, GFM tables, and local images copied into the document's `assets/` — and what you get is *ordinary authored TSX* you can then edit by hand or by agent. That bidirectional story (import, co-author, export) is what makes it usable as a pipeline step rather than a one-way generator.

Deployment is deliberately boring: `open-doc build` emits a plain static site that drops onto Vercel, Cloudflare Pages, Netlify or any static host.

## Install and ship a first document, step by step

The real path, in order:

```bash
# 1. Scaffold a documents workspace
npx @open-document/cli init my-docs
cd my-docs

# 2. Studio + viewer on :5273 (also serves the MCP endpoint with --mcp)
pnpm dev
open-doc dev --mcp          # mounts 23 tools at http://localhost:5273/mcp

# 3. Author: run /create-doc with your coding agent
#    (asks four scoping questions and establishes source material before writing)

# 4. Verify the layout — the step people skip and regret
open-doc check

# 5. Ship
open-doc export --pdf       # or --format html|png|svg
open-doc build              # static site for your host
```

The `/create-doc` skill is worth calling out as a design choice. It asks four scoping questions, insists on establishing source material first, and — in the project's own words — **"will not invent your numbers."** Prompt engineering treated as versioned, shipped source, distributed as a skill rather than as documentation. The other shipped skills are `/doc-authoring` (the technical reference), `/current-doc` (resolves "this page" by reading `node_modules/.open-doc/current.json`), `/apply-comments` and `/create-theme`.

## The 2026 MCP context — why a stateless protocol is what made this design viable

open-doc's MCP endpoint assumes a protocol shape that only became standard a few weeks before the project appeared. The **MCP `2026-07-28` revision** changed exactly the things that make a tool server like this simple to run:

- **Sessions removed** (SEP-2567) — protocol-level sessions and the `Mcp-Session-Id` header are gone, and list endpoints no longer vary per connection.
- **Handshake removed** (SEP-2575) — the `initialize` / `notifications/initialized` dance is gone; every request carries protocol version and client capabilities in `_meta`.
- **`server/discover` became a mandatory RPC** so clients can negotiate a version up front.
- **Multi round-trip requests** (SEP-2322) — servers return `resultType: "input_required"` with `inputRequests` instead of pushing server-initiated requests.
- **SSE stream resumability and `Last-Event-ID` removed** — a broken stream loses the in-flight request, and clients MUST re-issue with a new request id. That is directly relevant when an agent's long `render_page` call dies mid-render.
- **Smaller changes that bite local tool servers:** required `Mcp-Method` / `Mcp-Name` headers on Streamable HTTP POSTs (SEP-2243), `ttlMs` + `cacheScope` on list results (SEP-2549), deterministic `tools/list` ordering for prompt-cache hits, and resource-not-found moving from `-32002` to `-32602`.

A stateless protocol means an MCP document server does not have to hold per-client state, re-establish anything, or reconcile a reconnect — it is just a request handler over the same implementation the browser uses. open-doc offers a `legacy: 'stateless'` mode that serves 2025-era clients from the same endpoint, which is a sensible hedge for anyone whose client has not caught up. For the broader protocol landscape, see our [MCP, A2A and ACP comparison](/posts/ai-agent-protocols-mcp-a2a-acp-2026/) and the [plain-language MCP vs API explainer](/posts/api-vs-mcp-difference-guide-2026/).

## How it compares

All figures below were collected on **2026-09-30** from the GitHub and npm APIs; they move, so treat them as a snapshot. "Downloads" is npm downloads for the last month.

| Project | Stars | Downloads/mo | What it is | Best for |
| --- | --- | --- | --- | --- |
| **open-doc** (`@open-document/core`) | 78 | 487 | Agent-native document workspace: page geometry, checker, MCP tools, themes | A person and an agent co-authoring a printable report in a React shop |
| [react-pdf](/posts/ai-documentation-generator-tools-2026/) (`@react-pdf/renderer`) | 16,813 | 22,574,136 | React-to-PDF renderer with its own layout engine | High-volume programmatic PDFs inside an application |
| Typst | 56,342 | 12,920 | Markup-based typesetting compiler with fast incremental builds | Deterministic, compiler-driven typesetting |
| Pandoc | 46,452 | 6,780 | Universal markup converter | Markdown to *anything*, including real `.docx` |
| Quarto | 6,032 | — | Scientific/technical publishing system on Pandoc | Books, reports, reproducible research |
| WeasyPrint | 9,649 | 1,419 | HTML/CSS to PDF with real paged-media support | Server-side HTML-to-print pipelines |
| open-slide (sibling project) | 8,587 | — | Agent-native *deck* framework, 1920×1080 canvas | Slides, not documents |
| MarkItDown | 187,655 | — | Files and office documents *into* Markdown | Ingestion for agents |

Three comparisons deserve a sentence each because they are the ones readers actually search for.

**open-doc vs react-pdf** is not a contest — it is a category difference. react-pdf is a renderer with its own layout engine and a PDF-specific component set (`Document`, `Page`, `View`, `Text`); it is what you reach for when a service must produce PDFs at scale inside an existing app. open-doc is a document *workspace* with a viewer, inspector, themes, skills, an MCP endpoint and a layout checker that tells the agent *which page overflowed and at which line:column*. react-pdf has roughly 46,000× the downloads, and it does not give an agent a feedback loop about clipped content.

**open-doc vs open-slide** is the same author-side philosophy in a different medium, and the star gap is instructive: 8,587 stars for the deck framework against 78 for the document framework. Same skill pattern (`/create-*` with four scoping questions, `@…-comment` markers, `/apply-comments`), but a deck exports an editable PPTX where each page becomes native text boxes and shapes — done entirely in the browser, no headless browser needed. Documents have a paginated paper contract, which is precisely why open-doc needs a checker and open-slide does not.

**open-doc vs Pandoc/Quarto/Typst** is the fidelity-versus-breadth trade. The markup toolchain wins decisively on output formats — `.docx`, LaTeX, EPUB, ODT — and loses on layout feedback: none of them can tell an agent "the table on page 7 overflows by 40px." open-doc's counter-argument to Typst is that agents write prose well and markup badly, and that React is a medium the model already has deep priors for; Typst's counter-argument is determinism — a compiler has no browser print pipeline, no font race and no `@page` descriptor that Chromium might drop.

One more framing worth keeping: **"agent documents" is two problems.** Ingestion (getting existing files into a form the model can read) and production (emitting a printable artifact). MarkItDown — at 187,655 stars, an order of magnitude bigger than anything else here — solves the first. open-doc only solves the second, and in a real pipeline they compose: MarkItDown ingests, the agent reasons, open-doc produces.

## Limitations and open issues

Read this section before you put it in front of a team.

- **No `.docx` export.** Issue [#35](https://github.com/simonliu-ai-product/open-doc/issues/35), filed 2026-09-21, requests an editable Word file precisely because reviewers want track changes and Word comments. PDF is currently the end of the line. If your organisation's sign-off process runs in Word, that is a review-workflow problem, not a rendering problem, and it disqualifies open-doc today.
- **The MCP escape hatch is currently broken.** Issue [#34](https://github.com/simonliu-ai-product/open-doc/issues/34) (2026-09-08): `allowedHosts` from `open-doc.config.ts` is never passed to the MCP plugin, so `/mcp` returns `403 Invalid Host` for any non-loopback host — including a Docker Compose service name. The endpoint validates `Host` and `Origin` against loopback (blocking DNS rebinding, 403 on both rejections) and authenticates nothing, so anything beyond loopback needs an authenticating reverse proxy. Do not expose it.
- **Single-column viewer.** Issue [#36](https://github.com/simonliu-ai-product/open-doc/issues/36): no two-up or grid view, despite fit-page / fit-width / 100% zoom controls.
- **Adoption is minimal, and the curve is falling.** Created 2026-08-17, 78 stars, 7 forks, 9 open issues, one human contributor (LiuYuWei, 12 commits; the other committers are `github-actions[bot]` and `dependabot[bot]`). 23 lifetime commits, 2 in the trailing four weeks. Core downloads: 976 over 45 days — **459 in launch week, 23 in the last full week**, a ~95% decay. Six core versions shipped in the first 18 days; the latest release is core 0.6.0 / mcp 0.3.2 on 2026-09-03.
- **The marketing page is three minor versions stale** — it still advertises "v0.3.0 is on npm" while npm serves 0.6.0. A small but honest signal of how thin the operation is.
- **Naming collisions.** `RyanYahya/OpenDoc` (created 2026-09-12, 2 stars) carries a near-identical description and appeared twelve days after this one went public. Searching "OpenDoc" also surfaces older, unrelated projects. Check which OpenDoc you found.

Note also what the download split implies: `@open-document/mcp` pulled **445 downloads** last month against core's 487. The MCP surface is not a subset of the audience — it *is* the audience. People are reaching for this as an agent tool, not as a rendering library.

## Who should use open-doc — and who should not

**Use it if** you have a recurring, human-reviewed printable report — monthly board pack, quarterly investor update, technical whitepaper — authored by a coding agent inside an existing React/TypeScript shop, where a person steers in chat while the agent writes, and where "does this fit on the page" currently costs a manual review cycle. The `open-doc check` CI gate and the "no proprietary format, it diffs in git" property are the real wins: your documents become readable, reviewable source that shows up in a pull request like anything else, instead of a binary `.docx` nobody can diff.

**Do not use it if** you need high-volume server-side PDF generation (react-pdf), markup-first scientific publishing (Pandoc, Quarto, Typst), anything that must end as `.docx` with track changes, or a hosted service with an SLA. And do not deploy the MCP endpoint beyond loopback while issue #34 is open.

The candid summary: this is a well-argued design you can read end to end in an afternoon, with a genuinely novel contribution — a layout checker that closes the loop for a blind author. It is not yet a load-bearing dependency.

## FAQ

### What is open-doc in one paragraph?

An MIT-licensed React-first document framework (`@open-document/core`) where a coding agent writes each report as React components while the framework supplies real A4/JIS B4/A3 page geometry, a self-filling contents page, running page numbers, DOM-measured auto-pagination, layout diagnostics and PDF/HTML/PNG/SVG export. Scaffold it with `npx @open-document/cli init my-docs`, then `open-doc dev` for the studio on port 5273.

### Can it run headless in CI, and how does that work?

Yes. `open-doc check` renders every page at true size, reports clipped content, blank sheets, stranded headings, too-small type and failed images with source `line:column` locations, and exits non-zero — so the same command that advises an agent can fail a build. Headless export additionally needs `playwright` with chromium, an optional peer dependency rather than a bundled browser. See our notes on [code-mode MCP tooling](/posts/agent-codemode-mcp-scripts-2026/) for how agents typically consume tool surfaces like this.

### Does it export to Word (.docx)?

No. Output is PDF, HTML, per-page PNG and SVG. Issue #35 requests `.docx` specifically because organisations that review in Word need track changes and comments. Until that lands a PDF is the end of the line; use Pandoc if Word is a hard requirement.

### Which agents can drive it, and does it need a browser?

Anything that writes files or speaks MCP. Skills ship inside the scaffolder (`/create-doc`, `/doc-authoring`, `/current-doc`, `/apply-comments`, `/create-theme`) for agents that read skill directories, and `open-doc dev --mcp` mounts 23 tools at `http://localhost:5273/mcp` for any MCP client. A browser is required — deliberately, since PDF export uses the browser print pipeline at true page size so that what you see is what prints. Those skills follow the pattern covered in the [agent skills marketplace guide](/posts/agent-skills-marketplace-guide-2026-claude-codex-cursor-and-gemini-cli/).

### How mature is it, and is the MCP endpoint safe to expose?

Very early: created 2026-08-17, 78 stars, 7 forks, one human contributor, roughly 487 npm downloads a month for core, and a decay from 459 downloads in launch week to 23 in the last full week. On safety, no — not as shipped. The endpoint validates `Host` and `Origin` against loopback (403 on both) to block DNS rebinding and authenticates nothing, so anything beyond loopback needs an authenticating reverse proxy, and issue #34 means the intended `allowedHosts` escape hatch returns 403 anyway.

## Sources and further reading

- open-doc repository, README, MCP package README, core CHANGELOG and authoring skill: `github.com/simonliu-ai-product/open-doc`
- Product page (advertising v0.3.0): `costaffs.app/tools/open-doc/`
- Issues [#35](https://github.com/simonliu-ai-product/open-doc/issues/35) (`.docx`), [#34](https://github.com/simonliu-ai-product/open-doc/issues/34) (`allowedHosts` / 403), [#36](https://github.com/simonliu-ai-product/open-doc/issues/36) (two-up view)
- npm registry and downloads API: `@open-document/core`, `@open-document/mcp`, `@open-document/cli`
- MCP specification `2026-07-28` changelog (SEP-2567, SEP-2575, SEP-2322, SEP-2243, SEP-2549)
- Comparators: `react-pdf`, `typst/typst`, `jgm/pandoc`, `quarto-dev/quarto-cli`, `Kozea/WeasyPrint`, `microsoft/markitdown`, `open-slide/open-slide`
- Related reading on this site: [MCP, A2A and ACP in 2026](/posts/ai-agent-protocols-mcp-a2a-acp-2026/), [AI documentation generator tools](/posts/ai-documentation-generator-tools-2026/), [AI code documentation tools](/posts/ai-code-documentation-tools-2026/), [cross-agent context over MCP](/posts/agents-memory-cross-agent-context-mcp/)
