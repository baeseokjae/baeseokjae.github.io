---
title: "Drawgent Review: Putting a Coding Agent on a Live Excalidraw Canvas (2026)"
date: 2026-10-01T11:37:44+00:00
tags:
  - "drawgent coding agent excalidraw"
  - "drawgent"
  - "drawgent excalidraw"
  - "coding agent on excalidraw canvas"
  - "excalidraw mcp server"
  - "excalidraw coding agent"
  - "diagram linked to code"
  - "diagram drift CI check"
  - "drawgent review"
  - "excalidraw ai agent 2026"
  - "agent whiteboard"
  - "architecture diagram agent"
  - "drawgent vs excalidraw-mcp"
  - "drawgent vs mcp_excalidraw"
  - "how to connect claude code to excalidraw"
  - "agent draws architecture from repository code"
  - "excalidraw room agent collaborator"
  - "ai agent laser gestures whiteboard"
description: "Drawgent is a local server that puts your own coding agent on a live Excalidraw canvas, with diagrams linked to real code. A 2026 review of v0.2.1."
draft: false
cover:
  image: "/images/drawgent-coding-agent-excalidraw-canvas-2026.png"
  alt: "Drawgent Review: Putting a Coding Agent on a Live Excalidraw Canvas"
  relative: false
schema: "schema-drawgent-coding-agent-excalidraw-canvas-2026"
---

Drawgent is a local server that connects your own coding agent — Claude Code, Codex, or opencode — to a live, persistent Excalidraw canvas that you and the agent edit together. It ships no agent and no API key. It drives the agent you already have installed, in the repository you already have open.

That is the whole idea in one paragraph, and it is a genuinely different one. Most "AI whiteboard" tools generate a picture from a prompt and hand you the PNG. Drawgent instead treats the canvas as a two-way work surface: the agent reads what you drew, you read what the agent drew, and — the part almost nobody else ships — individual shapes can be linked to files, line ranges, and symbols in your codebase, then checked in CI so your architecture documentation cannot silently drift.

This review covers what drawgent actually is, what it does that its competitors do not, and where the idea breaks down. Every factual claim below comes from the project's own [repository](https://tangled.org/yanndegat.tngl.sh/drawgent), its [README](https://tangled.org/yanndegat.tngl.sh/drawgent/blob/main/README.md) and its documentation at v0.2.1, cross-checked against the [Hacker News thread](https://news.ycombinator.com/item?id=49857729) that launched it. The primary sources were re-read on 2026-10-08; where a number had moved since the September launch, this review uses the 2026-10-08 value.

{{< figure src="/images/drawgent-coding-agent-excalidraw-canvas-2026.png" alt="Drawgent Review: Putting a Coding Agent on a Live Excalidraw Canvas" >}}

## What Is Drawgent, Exactly?

Drawgent is a counter-position to the MCP-server model. It is not an MCP server you wire into a chat client, and it is not a one-shot prompt-to-image generator. It is a single static binary — written in Rust, 12,011 lines across `src/*.rs`, with Rust making up 63.8% of the repository and JavaScript 31.9% for the editor and browser extension — that runs a local server on port 7300 by default, hosts the Excalidraw editor, and exposes 24 MCP tools on that same port.

The setup is two commands in a repository:

```bash
drawgent setup claude
drawgent up
```

The first writes the MCP configuration for your chosen agent. The second starts the server and opens the canvas. The README's claim that there is **no Node.js and no Docker required** is stated twice — in the README and in `docs/getting-started.md` — because that is the sharpest contrast with the rest of the field, where `npx -y some-whiteboard-mcp` is the standard onboarding and Node.js 18+ is a hard prerequisite.

The one dependency that is real is Chrome or Chromium. Drawgent uses `chromiumoxide 0.9` to drive a headless browser for screenshots, and the setup routine will find or install one. That is an honest engineering trade: it buys accurate rendering of the canvas for the agent's vision pass, at the cost of a heavyweight dependency that the author names in the README's Limits section rather than hiding.

| Property | Drawgent v0.2.1 (as read 2026-10-08) |
|---|---|
| License | GPL-3.0-or-later |
| Language | Rust 63.8%, JavaScript 31.9% |
| Stars / forks / commits | 12 / 2 / 50 |
| Install | Single static binary (Linux x86_64, aarch64, musl static) |
| Runtime deps | Chrome/Chromium for the renderer; no Node.js, no Docker |
| Default port | 7300 |
| Agent drivers | Claude Code (built-in bridge), Codex (built-in bridge), opencode (native ACP), any ACP agent |
| MCP tools | 24 across reading, drawing, notes/status, boards and code; the 5 code tools are dropped in canvas-only mode |

The repository lives at [tangled.org/yanndegat.tngl.sh/drawgent](https://tangled.org/yanndegat.tngl.sh/drawgent) — a single-author project (yann.degat) on Tangled, an AT Protocol forge, not GitHub — and the `v0.2.1` tag was cut on 2026-09-29, three days after its Hacker News launch.

## Why Did Drawgent Reach the Hacker News Front Page?

The launch post, "Drawgent: Coding agent on a live Excalidraw canvas," hit the Hacker News front page on 2026-09-26 with **178 points and 48 comments** (read 2026-10-08; it stood at 177 and 46 when this review's research started on 2026-10-01, so the numbers were still climbing) and drew secondary coverage within 24 hours — including an automated write-up at kenashe.ai, which says up front that it had only the one-line pitch to work from. For a twelve-star repository, that is an unusual amount of attention, and it is worth understanding why.

The argument drawgent is making is that chat is a lossy serialization of a graph. If you want an agent to understand three services and the arrows between them, you type prose describing a structure that is natively spatial, and you hope the model reconstructs the same topology you had in your head. The canvas bet is that a diagram does not erase the shape of the problem — you point at the box, and there is no reconstruction step to get wrong.

That is the most transferable idea in the project, and it is the reason the thread engaged seriously rather than dismissing it. The comments that pushed back were not about feasibility. They were about a deeper question — whether the canvas makes the agent *more correct* or merely *more legible* — which I take up in its own section below.

## The Feature Nothing Else Ships: Diagrams Linked to Code

If you read only one section of this review, read this one. Code links are the single least-copied feature in the entire comparison set.

In drawgent, a shape can carry a link to a **file, a line range, and a symbol**. The Code tab reports each link's status as one of four values:

- **ok** (✅) — the symbol is where the link says it is
- **moved** (↕) — the symbol is now at other lines; a fix is offered
- **stale** (⚠) — the symbol is gone
- **missing** (❌) — the file is gone; a file with the same name elsewhere is suggested

That is a small feature with a large consequence. It reframes the architecture diagram from a picture into a *testable artifact*. Drawgent exposes `drawgent check`, and the documented intent is that you run it in CI: when someone refactors a service and the boxes no longer point at real code, the build fails. `drawgent check --fix` repairs moved symbols and renamed files in place rather than forcing you to hunt them down by hand; the command exits 1 when links are broken, which is what makes it usable as a CI gate.

Compare that to what every competitor does. The official Excalidraw MCP app server, mcp_excalidraw, and Whiteboard MCP all produce diagrams *about* a system. None of them can tell you whether the diagram is still true. The drift problem — the reason architecture documents rot within a quarter and then get deleted — is the problem drawgent actually attacks, and it is the strongest reason to run it over the alternatives.

```bash
drawgent check --diagram docs/architecture.excalidraw
```

Boards can also be committed as clean, diffable `.excalidraw` files, so the diagram follows `git pull` like any other source file, is reviewable in a pull request, and can be validated by the same pipeline that validates code.

## Point Instead of Describing: Laser Gestures and Canvas Notes

The second differentiator is spatial interaction, and it is the one that surprises people in a demo.

Drawgent recognizes **laser gestures** — the Excalidraw laser tool (press `K`) — combined with *what the stroke was drawn over*. The supported vocabulary is deliberately small and legible:

| Gesture | What drawgent reads it as | Example task it offers |
|---|---|---|
| Circle / scribble | select what it encloses | *Drill down into it* (its internals, read from the code), *Check it against the code* |
| Arrow A → B | from → to: connect, data flow | *Trace A → B in the code* (draws the real path with its hops) |
| Arrow to empty space | put it, or what comes next, there | *Move it there, re-layout* |
| Line between two shapes | how are these related? | *Find what couples them* |
| Zigzag / line through a shape | cross it out | *Remove it from the architecture*, with the impact on the code |
| ✓ | approve, keep | *Check it against the code*, *Build it* |
| Tap (a dot), ✕ | this shape, or this spot | *Explain it*, *Drill down* |
| ↔ / ↕ | more room here | *Make room and re-balance* |

Tasks are picked from what the gesture sits on: code tasks are only offered when the zone holds shapes linked to code, and a zone with no code links never gets a code-refactor proposal.

Two seconds after a stroke settles, the agent proposes **two to three concrete tasks** plus an "Other…" option in the panel. You pick one; work starts. You never typed a prompt.

There is a second channel for typed intent without a chat box: write a note on the canvas beginning with `AGENT:`. Once typing settles — the default is **2500 ms** — the note fires and the agent responds with a green `DONE:` note on the same canvas. The default room display name for the agent is `🤖 Agent`.

The interaction model is the product's strongest demo and its most subjective feature. If your team already thinks in boxes and arrows, this will feel like a shorter path to the same request. If your team thinks in sentences, it will feel like a novelty layered on a chat box you will keep using anyway — a fair criticism, and one the author does not really answer in the docs.

## Draw, Look, Adjust: How the Agent Actually Sees the Canvas

This is the technical core, and it is where drawgent is more careful than the field.

The agent has three ways to perceive the canvas, and they trade accuracy against cost deliberately:

1. **`get_scene`** — reads the canvas incrementally and returns structured element data. Cheap, token-efficient, and the default for most turns.
2. **`get_screenshot`** — returns a cropped PNG rendered by headless Chrome. Expensive, and it burns multimodal tokens, but it is ground truth for what the diagram *looks* like.
3. **`check_layout`** — a geometry lint that runs with no screenshot at all.

That third tool is the interesting one. `check_layout` reports overlapping elements, elements outside the viewport, unreadable spacing, and similar geometric defects as structured text. For a small or cheap model — or for a model with no vision at all — that is the difference between a layout pass that costs a few hundred text tokens and one that costs a multimodal image every iteration. It is a direct answer to the most common technical objection to this whole category: that models are bad at estimating bounding boxes and pixel coordinates.

The write side of the loop is similarly complete: `add_graph` for auto-laid-out node-and-edge structures, `add_mermaid` for flowchart, sequence, and class diagrams, `add_elements` and `update_elements` for element-level control, `make_space` to carve out room for new content, `delete_elements` with an arrow-bridging reconnect behavior so removing a node does not orphan its edges, and `undo_changes`.

Agent edits land on the **normal undo stack**. `Ctrl+Z` reverts a single edit, and there is one control to revert an entire agent turn — a small detail that matters a great deal in practice, because it is what makes it safe to let an agent write to a document you care about.

## "Build What I Drew": Turning Canvas Edits Into Code

The second half of the code-link story is the inverse direction. Drawgent can take a diagram edit and turn it into implementation work, with status markers drawn on the canvas itself: **planned**, **in-progress**, **done**, and **blocked**.

In practice this means you can sketch the change you want — a new service box, an arrow into an existing one — and hand that sketch to the agent as the specification, then watch the markers advance on the drawing as the work lands. The diagram stops being documentation that describes the code after the fact and becomes the surface on which the change is specified and tracked.

Whether that is better than writing a ticket is a real question, and I do not think drawgent has settled it. What is not in question is that no other tool in this comparison set does it. mcp_excalidraw matches drawgent on the draw-look-adjust loop, but it has no code links, no build-what-I-drew, no CI link check, and no gesture layer — and it ships as an agent *skill* for Claude Code, Codex, or OpenCode rather than driving the agent itself, which means it cannot see or run the repository the way a drawgent-driven session does.

## Rooms: Joining a Document Your Team Already Has

Drawgent can join a live collaboration room — either an `excalidraw.com` room or a self-hosted Excalidraw document — as one more named collaborator (default `🤖 Agent`) through its own WebSocket relay (`tokio-tungstenite`). There is also a Firefox MV3 extension that adds a drawgent sidebar to the document you already have open, so laser strokes drawn in that tab become gestures.

That is the feature that makes it usable in a team setting rather than as a solo tool. It also comes with four documented limits that you should read before planning around it, because they are the kind of thing that produces a silent hang rather than an error:

- **A browser must have the document open.** On a self-hosted server drawgent relays edits through the peers' tabs rather than saving the document itself; the edit is lost if drawgent stops before a tab writes it. (Rooms on excalidraw.com are the exception: drawgent loads and saves those in Firestore itself, so it can work alone there.)
- **Only documents in a live collaboration room work.** Having the document open in a tab is not enough. Private documents frequently open no collaboration room, and in that case drawgent **waits indefinitely** instead of failing loudly.
- **Password-protected documents are unsupported** — end-to-end encrypted with a key you type rather than one carried in the link. A room whose link contains its `{key}` (excalidraw.com's format) *is* supported and is AES-GCM encrypted in transit.
- **Main board only; images and files are not synced.**

The first and second limits are the ones that will bite. A tool that hangs forever on a private document is not broken — the docs tell you why — but it is a rough edge, and the failure mode costs you an afternoon the first time you hit it.

## How Does Drawgent Compare to Other Excalidraw and Whiteboard Agents?

The honest answer is that drawgent is entering a field with three very different incumbents, and it loses on distribution to all of them while winning on integration depth.

Star counts and push dates below were read from each project's own forge on 2026-10-08.

| Tool | Model | Stars | Last push | Code links | Persistent canvas | Gestures |
|---|---|---|---|---|---|---|
| **Drawgent** | Drives your local agent on a live canvas | 12 | 2026-09-29 | Yes (file + lines + symbol, CI check) | Yes | Yes (laser + notes) |
| **excalidraw/excalidraw-mcp** (official) | One-shot widget in chat | 5,487 | 2026-03-24 | No | No | No |
| **yctimlin/mcp_excalidraw** | Agent skill + 26-tool MCP server | 2,509 | 2026-10-05 | No | Yes | No |
| **Whiteboard MCP** | Commercial prompt→diagram SaaS | n/a | n/a | No | No | No |
| **Reladraw** | Declarative placement language | 1,089 | 2026-10-03 | No | Partial | No |

**Official Excalidraw MCP app server** ([excalidraw/excalidraw-mcp](https://github.com/excalidraw/excalidraw-mcp), 5,487 stars, 517 forks, TypeScript as read 2026-10-08) is the first-party reference point, and drawgent's own docs credit it — the drawing guide is "adapted from the official excalidraw-mcp guide (MIT)." It is hosted and remote-first at `mcp.excalidraw.com`, plus a Claude Desktop `.mcpb` extension, meaning zero local infrastructure. But it is a chat widget, not a workbench: its closest rival characterises it as giving the model "two tools: a format reference and `create_view`" (that is [mcp_excalidraw's](https://github.com/yctimlin/mcp_excalidraw) own comparison table, a competitor's read, and its README does show only an install, two example prompts and no canvas API), and diagrams stream inline into the conversation rather than into a canvas the agent can re-read. The Hacker News thread openly debated whether it is abandoned — it has not been pushed since 2026-03-24 and carries 61 open issues. No code links, no persistent state, no undo integration, no room participation.

**yctimlin/mcp_excalidraw** (2,509 stars, 282 forks, MIT, last pushed 2026-10-05, as read 2026-10-08) is the strongest direct rival, and the one whose README draws the same line the rest of the category does: the official server is "prompt in, diagram out (one-shot widget)," while this project is "programmatic element-level control (CLI + 26 MCP tools)." It matches drawgent on `describe_scene`, `get_canvas_screenshot`, snapshot/restore, Mermaid conversion, shareable URLs, viewport control, and multi-agent concurrency. Where it stops is precisely where drawgent starts: no code links, no build-what-I-drew, no gestures, no CI check. And it has a 200x larger audience.

**Whiteboard MCP** is the commercial framing of the same slot: "Give your AI the power to draw. Architecture diagrams, flowcharts, sketches — generated from a single chat message." One-line `npx -y whiteboard-mcp` in `.mcp.json`, `~/.claude.json`, `.cursor/mcp.json`, `.vscode/mcp.json`, or Windsurf config; 30-second onboarding; a documented support list covering Claude Code, Cursor, VS Code, Windsurf, Zed, OpenCode, Antigravity, and Amp; and a freemium funnel ("14-day free trial · No credit card required") that drawgent simply does not have. But it is prompt→diagram generation, the exact one-shot model both drawgent and mcp_excalidraw reject.

**Reladraw** ([reladraw/reladraw](https://github.com/reladraw/reladraw), 1,089 stars, Apache-2.0, [Show HN](https://news.ycombinator.com/item?id=49858513) at 414 points and 119 comments) is the opposite paradigm, and it surfaced inside drawgent's own thread. It is "a diagram language where you decide where to place things" — relative placement constraints instead of an agent estimating bounding boxes — and it argues drawgent's premise is wrong. If agents are bad at spatial reasoning, don't give them a freeform canvas; constrain placement in a declarative language. It also confirms the shared technical objection is real enough that someone built an entire tool to route around it.

**tldraw** kept coming up in the thread as the more agent-programmable substrate, with commenters explicitly asking whether anyone had tried it against Excalidraw. It is not an agent product — it is canvas infrastructure with a typed programmatic API — but it is the standing alternative answer whenever [Excalidraw](https://github.com/excalidraw/excalidraw)'s 133,681-star, MIT-licensed base is questioned (stars as read 2026-10-08).

## The Hard Problems Nobody Has Solved

A review that only lists features is a spec sheet. Here is where drawgent's idea is genuinely unresolved.

**Is a sketch unambiguous enough to act on?** Intent ambiguity is worse in a picture than in a sentence. One box with an arrow to another could mean "A calls B," "A depends on B," "A becomes B," or "these are related, figure it out." A wrong commitment on a fuzzy diagram is worse than a wrong commitment on a fuzzy sentence, because you believed the picture was unambiguous. Drawgent's `AGENT:` notes and its 2-3 proposed tasks mitigate this — the agent states what it thinks you meant before acting — but the mitigation is a confirmation step, not a solution.

**Does drawing it back look like understanding without being it?** This is the sharpest critique, and it was made publicly within a day of launch. A visual interface makes the agent's confidence *more legible*, not more correct. A clean diagram of what the agent plans to do looks like comprehension; in reality it is the same guess a chat reply would have made, rendered in boxes that feel authoritative because you draw boxes like that yourself. The canvas is a better place to catch a mistake **and** a better place to be fooled by one. Note what this critique rests on: the public piece that made it, [kenashe.ai's 2026-09-27 write-up](https://kenashe.ai/blog/2026-09-27-drawgent-puts-a-coding-agent-on-an-excalidraw-canvas-what-a-visual-work-surface/), is an automated digest, disclosed as such, and says outright that it had only the Hacker News one-liner and could not confirm how drawgent runs. The argument is worth reading on its own terms; it is not evidence about the product. I find it persuasive, and drawgent's answer — the drill-down, trace and laser loop is built for interrogating a diagram rather than just generating one — is a good answer that does not fully settle it.

**The hand-drawn aesthetic is doing rhetorical work.** A subthread in the launch discussion argued that part of Excalidraw's appeal is that people still believe its output is hand-made, so there is "a lot of attention be gained/exploited" with tools like it — with the blunt counter-reply from another commenter that it is "a new way of wasting people's time with my slop… god this is bleak." Any honest review has to sit with this. Drawgent cannot be blamed for it, but it does benefit from it.

**And the counter-thesis, from the same thread:** "the value I get from producing a diagram is derived from the thinking." If the agent draws it for you, you may have skipped the understanding you were actually after. Drawgent's loop is designed for interrogation rather than generation, which is the right response — but it is still a tool whose best demo involves not thinking very hard about the structure you are looking at.

There is also the question of whether Excalidraw's JSON is a good agent substrate at all. One commenter reported building a native SVG/PNG renderer instead, on the theory that agents are "heavily trained on specific formats (e.g. SVG) and are conversely pretty bad at niche formats." Others described the model "dealing with a lot of JSON data and estimating/computing with bounding box and pixel point numbers." Drawgent's answer to that — `check_layout`, `make_space`, `add_graph` auto-layout — is the right shape of answer, but it is a mitigation of a substrate problem, not an elimination of it.

## Where Drawgent Stands Today

Drawgent is v0.2.1, tagged 2026-09-29 and still the only release. As read on 2026-10-08 it has 12 stars, 2 forks, 50 commits and 140 files, and it is a single-author project under GPL-3.0-or-later. It is a promising alpha with a real idea, not a product.

The author names most of the weak points himself, which is itself a quality signal:

- The renderer **hard-depends on Chrome or Chromium**.
- Claude Code's `--attach` is a **fork** of the agent, because Claude Code offers no public way to inject messages into a running terminal session.
- Codex live attach **"hasn't been tested against a logged-in Codex yet."**
- macOS builds are **cross-compiled, not notarized, and untested on a real Mac.**
- Rooms silently wait forever on private documents, as documented above.

Permissions are handled well for an alpha: three modes, default-safe. `canvas` (canvas tools run free; anything else asks in the panel) is the default, `ask` makes every tool call ask, and `all` approves everything and is documented as appropriate only in sandboxes.

What to watch next: a tested macOS build, a working Codex live attach, a real CI adoption story for `drawgent check`, and any third-party code review of those 12,011 lines of Rust — particularly the WebSocket room relay and the `.excalidraw` round-trip fidelity, where commenters in the launch thread flagged element-level JSON churn and where bugs would most plausibly live.

## Verdict: Who Should Run Drawgent Today?

**Try it now** if you are a working engineer who already has Claude Code or opencode installed and a repository you personally find hard to hold in your head. The "understand a codebase" walkthrough is the most concrete thing drawgent does and the easiest to reproduce: clone a repo you have never seen, run `drawgent up`, ask it to map the repo as a treemap sized by line count, then laser-circle a box to drill into its internals and laser-arrow from A to B to trace the real call, queue, or HTTP path. That loop is worth an afternoon, and it is not something a chat window does well.

**Adopt it seriously** if diagram drift is a specific, named pain in your organization. The code-link plus `drawgent check` combination is the only CI-gated architecture-diagram check in this comparison set, and it is the reason to pick drawgent over competitors with a hundred times its distribution. Local-binary, agent-agnostic depth — no Node.js, no Docker, your login, your config, your repository — is a defensible position even against 2,509-star rivals, because the integration is the product.

**Wait** if you need anything production-shaped. Untested macOS and Codex attach, a silent-hang failure mode in rooms, a Chrome dependency, and a single-author 0.2.x codebase are not a platform to build process on. And if you need it to be reachable by a team of thirty who already live in Cursor and VS Code, note that drawgent offers nothing like Whiteboard MCP's funnel.

**Skip it entirely** if what you actually want is a picture from a prompt. Drawgent is slower than that on purpose. It is a tool for interrogating a diagram, and if you do not want to interrogate anything, the effort is pure overhead.

## FAQ

**Is drawgent free?**
Yes. It is GPL-3.0-or-later, with no warranty, no account and no hosted service — you download a single static binary from the project's tags page. You still pay for your own agent (Claude Code, Codex, or opencode), because drawgent drives the agent rather than shipping one.

**Does drawgent need an API key?**
No key of its own. It uses your existing agent CLI and your existing login, which makes it the agent-agnostic counterpart to tools that require you to bring a provider key.

**Which coding agents does drawgent work with?**
Claude Code and Codex through bridges built into drawgent, opencode natively over ACP, and any other ACP-speaking agent via `drawgent serve --agent mine='my-acp-agent --stdio'`. Note that Codex live `--attach` is documented as untested against a logged-in Codex, so treat that path as experimental.

**Can drawgent stop my architecture documentation from drifting?**
That is the feature it is most alone in shipping. Shapes link to a file, a line range, and a symbol; the Code tab reports `ok`, `moved`, `stale`, or `missing`; `drawgent check --fix` repairs moved symbols; and the same command is designed to run in CI so a broken link fails the build.

**Does drawgent work with a shared excalidraw.com room?**
Yes — it joins as one more collaborator, default name `🤖 Agent` — but only if the document is in a live collaboration room. A private document often opens none, and in that case drawgent waits indefinitely rather than erroring. Documents encrypted with a key you type are unsupported; a room whose link carries its key (excalidraw.com's format) is supported and encrypted in transit. Images and files are not synced.

**Is drawgent a replacement for Mermaid?**
No. It can draw Mermaid (`add_mermaid` supports flowchart, sequence, and class diagrams), but its pitch is that a diagram should be a live, hand-editable, code-linked surface rather than a text block that renders once. Several practitioners in the launch thread argued Mermaid remains the most agent-friendly medium today; drawgent's counter is the human side — Mermaid cannot be edited by hand in a room, cannot carry a laser gesture, and cannot hold a code link on a shape.

## Sources

Every factual claim in this review was checked against the project's own primary sources on 2026-10-08, listed here so you can repeat the check.

- drawgent repository and project page (stars, forks, commits, language breakdown, `v0.2.1` tag) — https://tangled.org/yanndegat.tngl.sh/drawgent
- drawgent `README.md` at `main` (single binary, install table, no Node.js and no Docker, Limits section) — https://tangled.org/yanndegat.tngl.sh/drawgent/blob/main/README.md
- `README.md` Limits and setup (code-link statuses, `AGENT:` note settle time, port, tools) — https://tangled.org/yanndegat.tngl.sh/drawgent/blob/main/docs/reference.md
- `docs/code-and-diagrams.md` (code links, the four Code-tab statuses, `drawgent check --fix`, *Build what I drew*) — https://tangled.org/yanndegat.tngl.sh/drawgent/blob/main/docs/code-and-diagrams.md
- `docs/laser-and-gestures.md` (gesture vocabulary and the tasks each one offers) — https://tangled.org/yanndegat.tngl.sh/drawgent/blob/main/docs/laser-and-gestures.md
- `docs/canvas.md` (chat panel, `AGENT:` notes, undo, `.excalidraw` files in the repo) — https://tangled.org/yanndegat.tngl.sh/drawgent/blob/main/docs/canvas.md
- `docs/agents.md` (the two built-in bridges, `--attach`, permission modes, ACP) — https://tangled.org/yanndegat.tngl.sh/drawgent/blob/main/docs/agents.md
- `docs/rooms.md` (room model and its Limits section) — https://tangled.org/yanndegat.tngl.sh/drawgent/blob/main/docs/rooms.md
- `docs/getting-started.md` (platform requirements: "No Node.js, no Docker") — https://tangled.org/yanndegat.tngl.sh/drawgent/blob/main/docs/getting-started.md
- `docs/browser-extension.md` (the Firefox MV3 sidebar) — https://tangled.org/yanndegat.tngl.sh/drawgent/blob/main/docs/browser-extension.md
- Hacker News launch thread, "Drawgent: Coding agent on a live Excalidraw canvas" (2026-09-26) — https://news.ycombinator.com/item?id=49857729
- Hacker News, "Show HN: Reladraw" (points and comment count) — https://news.ycombinator.com/item?id=49858513
- Official Excalidraw MCP app server (stars, forks, last push, README) — https://github.com/excalidraw/excalidraw-mcp
- yctimlin/mcp_excalidraw (stars, forks, last push, the comparison table quoted above) — https://github.com/yctimlin/mcp_excalidraw
- Whiteboard MCP (commercial framing, install matrix, freemium funnel) — https://whiteboard-mcp.com
- Reladraw (stars, license, relative-placement model) — https://github.com/reladraw/reladraw
- Excalidraw itself (stars, MIT license — the substrate every tool here depends on) — https://github.com/excalidraw/excalidraw
- kenashe.ai, "Drawgent puts a coding agent on an Excalidraw canvas" (2026-09-27) — cited only as the public framing of the confidence-versus-correctness critique; it is an automated digest that states it could not confirm how drawgent runs — https://kenashe.ai/blog/2026-09-27-drawgent-puts-a-coding-agent-on-an-excalidraw-canvas-what-a-visual-work-surface/

What this review does **not** claim: the drawgent binary was never run for this piece. No `drawgent up`, no MCP tool call, no room join and no `drawgent check` in CI was performed, so every behavioural statement above is read from the documentation and the repository rather than measured first-hand. The Codex live attach and the macOS builds are documented by the author as untested, and are treated as unknown here, not working.

**Is drawgent production-ready?**
No. The `v0.2.1` tag landed 2026-09-29 (three days after the 2026-09-26 Hacker News post), and as read on 2026-10-08 the project has 12 stars, an untested macOS build, an untested Codex live attach and a hard Chrome/Chromium dependency. Treat it as a promising alpha with a genuinely differentiated idea behind it.
