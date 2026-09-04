---
cover:
  alt: 'Rungraph Agent Run Visualization 2026: Ask Your Agent What Happened in a Run with Interactive Graphs'
  image: /images/rungraph-agent-run-visualization-2026.png
  relative: false
date: 2026-09-04T07:02:15+00:00
description: Rungraph converts existing Claude Code, Codex, Hermes, opencode, and Cursor transcripts
  into interactive graphs and answers MCP queries about what happened in a run — no hooks
  or telemetry.
draft: false
schema: schema-rungraph-agent-run-visualization-2026
tags:
- rungraph
- agent-observability
- ai-coding-agents
- mcp
- developer-tools
- agent-monitoring
title: 'Rungraph 2026 Review: Ask Your Agent What Happened in a Run with Interactive Graphs'
---

Rungraph is an open-source, zero-instrumentation tool that reads the agent session transcripts already on your disk and renders them as interactive graphs. With a single `npx rungraph` command, it visualizes the orchestrator, subagents, and tool calls of any Claude Code, Codex, Hermes Agent, opencode, or Cursor run — then lets you ask, in plain language through an MCP server, "what happened?" and lights up the exact nodes the answer refers to.

## What Is Rungraph? Turning Agent Transcripts into Interactive Graphs

Rungraph is a JavaScript, open-source agent-run visualizer released on Hacker News in August 2026 by FayzanMalik. It sits on top of the session logs your coding agents already write to disk and converts them into a graph that you can explore interactively. The core idea is deliberately different from tracing and observability frameworks: there are no hooks, no wrappers, and no telemetry to install. Everything rungraph needs — the orchestrator turns, subagent spawns, tool calls, and human interventions — is already recorded in the transcripts your agents produce.

The tool's positioning is captured in its tagline: "Ask your agent what happened in a run." Instead of reading thousands of lines of silent terminal output, you load a run into rungraph's dashboard, and the work becomes a visual, interrogable artifact.

Rungraph currently works across five agents: Claude Code, Codex, Hermes Agent, opencode, and Cursor. It handles all five from a single command and requires no per-agent setup. This vendor-neutral design is a direct answer to the fragmented terminal-agent landscape of 2026, where Goose, Claude Code, opencode, and Pi coexist and each writes a different, unversioned session format to disk.

## How Rungraph Works: Retroactive, Zero-Instrumentation, Fully Local

The remarkable thing about rungraph is that it works **retroactively**. Because it reads transcripts already stored on disk, it can visualize runs that happened weeks before you ever installed the tool. There is no requirement to have "started recording" in advance.

- **No hooks:** Rungraph does not modify your agents or their runtime.
- **No wrappers:** You do not wrap your commands or change how you work.
- **No telemetry:** The tool makes no network requests — it is fully local. Your run data never leaves your machine.

To use it, you run a single command: `npx rungraph`. It scans the session stores of the supported agents, parses their transcripts, and opens an interactive dashboard. Under the hood, rungraph reads each agent's session format — Claude Code, Codex, Hermes, opencode, and Cursor — from disk. Some of those formats require Node version 22.13 or later: Hermes, opencode, and Cursor runs use rungraph's built-in SQLite reader, which needs that Node version.

One honest caveat is "coverage." Coding-agent transcript formats are undocumented and unversioned, so rungraph cannot interpret every record it encounters. The tool reports how much of a run it could read (for example, "read 95% of this run") and names the records it could not interpret. This transparency is what makes the tool trustworthy for a debugging workflow — you know when you are looking at a partial picture.

## The Graph: Orchestrator, Subagents, Tools, and Human Interventions as Nodes

The centerpiece of rungraph is the graph itself. At its most basic, it is a node-and-edge view of an agent run:

- **Nodes** represent the orchestrator, subagents, and individual tool calls.
- **Edges** represent spawn and return relationships — a subagent is spawned by the orchestrator, returns a result, and the path continues.
- **Human interventions** are marked on the path: permission denials, interrupts, and other human actions are visible rather than buried in logs.

This structure makes the shape of a run legible at a glance. You can immediately see when the orchestrator delegatated a task to a subagent, how many nested spawns occurred, and where a human stepped in to deny a permission or interrupt the flow.

Because a single large agent run can exceed 20,000 tokens if fully serialized, rungraph is designed around a "narrow then pull" query model. Rather than dumping the entire graph into your context, you focus on the nodes you care about and pull details on demand. This keeps both the dashboard and any connected LLM context efficient.

## Ask Your Agent What Happened — the MCP Layer and focus_nodes Deep Links

The most distinctive feature of rungraph is its MCP (Model Context Protocol) server. It gives you a set of tools — `list_runs`, `get_graph`, `find_nodes`, `get_detail`, and `focus_nodes` — that let you interrogate a run conversationally.

The workflow is: you open rungraph's dashboard alongside your AI assistant, then ask the assistant a question like "what did the subagent that edited the config file actually do?" The MCP server resolves the answer, and `focus_nodes` highlights the exact nodes on the graph that the answer references. Instead of reading a text response and mentally mapping it onto the run, you see the relevant portion of the graph light up in front of you.

- **list_runs:** enumerate the runs rungraph has parsed.
- **get_graph:** retrieve the structure of a run.
- **find_nodes:** locate specific nodes by query.
- **get_detail:** pull full detail for a narrow set of nodes.
- **focus_nodes:** highlight nodes in the open dashboard — the visual answer.

This "ask your agent what happened" model turns a silent, finished transcript into something you can have a conversation with. It is particularly valuable for audits, code reviews, and debugging, where the question is often the hardest part: "which tool call touched this file?"

## Opinionated Signals: Retry Storms, Unresolved Errors, Interventions, Outliers

Most log viewers render every event with the same visual weight, forcing you to scan for what matters. Rungraph takes a different, opinionated approach via a **signal strip** that flags specific patterns on the run:

- **Retry storms:** Repeated retries of the same failing call are flagged, revealing where the agent struggled.
- **Unresolved errors:** Errors that were never resolved are surfaced so you know the run ended in a problematic state.
- **Interventions:** Human actions (permission denials, course corrections) are marked.
- **Outliers:** Unusually long or unusual nodes stand out.
- **Course changes:** Points where the agent changed direction are visible.

On a clean run, the signal strip sits at zero height — nothing flashes, nothing vies for your attention. It only activates when there is something worth seeing. This is what the brief calls "opinionated observability": rendering not everything equal, but the things that matter louder. For a developer reviewing whether a run went smoothly, this is the difference between staring at a wall of text and immediately knowing where to look.

## Replay, Minimap, and Sharing Runs as Vendor-Neutral Bundles

Two more interactive features round out the dashboard: live growth and replay.

Because rungraph reads transcripts, a run that is happening **right now** grows live as the agent works. You can watch the graph extend in real time rather than only after the run completes. A replay bar then lets you scrub back and forth through the run, inspecting the state of the graph at any point in time.

These graphs are built to be shared. Rungraph exports run bundles in a `.rungraph` format — a vendor-neutral package you can hand to a teammate, attach to a PR, or archive. An example from the project's README shows a bundle containing 2 runs, 143 nodes, 12 prompts, and 24 files touched, serialized to a 412KB file. Because a graph plus focused node deep links is a far more reviewable artifact than a pasted log, rungraph positions agent runs as *collaborative* artifacts in code review and team debugging.

## Security by Design: Secret Redaction in Export

Transcripts are a security hazard that is easy to overlook. When an agent runs a tool like a file reader, it records the file contents verbatim — so an agent that merely opens `.env` to read its keys has captured those keys in its session log. Any tool that re-shares or exports a run must handle this responsibly.

Rungraph addresses it in two ways on export:

- **Secret redaction:** Shared `.rungraph` bundles redact likely secrets automatically.
- **High-confidence blocking:** Export blocks on high-confidence secrets, including AWS keys and GitHub, Slack, and API tokens.

This is a meaningful security posture for a tool whose whole value proposition is sharing runs with other people. Because the data stays local until you explicitly export, and because export is aggressively redacted, rungraph avoids becoming a channel for leaking credential material that transcripts routinely capture.

## Rungraph vs. the Agent-Observability Landscape

Rungraph does not exist in a vacuum — the agent-observability space is crowded and moving fast in 2026. Here is how it stacks up against the main alternatives:

| Tool / Approach | Model | Instrumentation | Data locality | Best at |
|---|---|---|---|---|
| **Rungraph** | Graph-native visualization + MCP query | None (reads on-disk transcripts) | Fully local | Retroactive, shareable, graph exploration |
| **Agentlore** | Searchable team log over agent sessions | Reads session data | Local per team | Team/communal search & indexing |
| **LangChain SmithDB** | Purpose-built observability data layer | Central tracing | Cloud / hosted | Enterprise LLM trace analytics |
| **Grafana agent observability** | Standard-dashboard ingestion | Telemetry to Grafana | Aggregated / hosted | Folding agent runs into existing dashboards |
| **Log-file grepping** | Manual | None | Local | Ad-hoc inspection of a single run |

The key contrast is **instrumentation philosophy**. SmithDB and Grafana's approach assume you build tracing into the pipeline and funnel event data into a central system. Agentlore positions run visibility as a team-collaboration problem focused on searchability. Rungraph, by contrast, is zero-instrumentation and local-first: it performs retroactive visualization of transcripts you already have, with graph structure plus MCP-driven interrogation as the interface. Where SmithDB answers enterprise "trace everything" needs, rungraph answers the individual developer's "what actually happened here?" need.

The Grafana adapter for Hermes Agent is a useful data point: it shows the observability ecosystem racing to ingest agent-run data into standard dashboards. Rungraph's differentiator is that it needs none of that infrastructure — there is nothing to ingest because the data is already on your disk.

## Who Rungraph Is For, Limitations, and 2026 Context

Rungraph is best suited to developers who already work with terminal and CLI coding agents and want to understand, audit, or share what their agents did. It is especially relevant in 2026, when terminal agents have gone fully mainstream — comparisons of Goose, Claude Code, opencode, and Pi are common — and where the coexistence of multiple agents fragments run and session formats. A vendor-neutral graph that reads them all is a practical answer to that fragmentation.

The tool's main limitations are honest ones:

- **Coverage is not 100%.** Because transcript formats are undocumented, rungraph may fail to interpret some records. It reports a coverage percentage and names what it could not read.
- **Node requirements.** Hermes, opencode, and Cursor use rungraph's SQLite reader, which requires Node 22.13+.
- **Local-first by design.** If you need centralized, enterprise-wide tracing across a fleet of agents, rungraph is not that; SmithDB or Grafana ingestion is.
- **Young project.** At research time it had 24 stars and 2 forks — useful and capable, but not battle-tested across a large community yet.

For the Hermes Agent user specifically, rungraph has native support — a nice alignment for anyone running Hermes-managed pipelines who also wants to see how individual runs unfolded.

## Verdict — Is Rungraph Worth Adding to Your Agent Workflow?

Rungraph solves a real, growing problem in a clever way. If you use Claude Code, Codex, Hermes Agent, opencode, or Cursor, and you have ever wished you could actually *see* what your agent did — or explain it to a teammate without pasting a wall of log text — rungraph is worth a try. The zero-instrumentation, retroactive design means there is no cost to adopting it: you can point it at runs you already have and get value immediately.

The MCP "ask your agent what happened" workflow, the opinionated signal strip, and the shareable `.rungraph` bundles make it genuinely useful for debugging and code review, not merely a pretty visualization. Be mindful of its coverage limitations and the Node 22.13 requirement, and treat exported bundles with the same caution you would any transcript (rungraph redacts, but transcripts are sensitive by default).

**Bottom line:** For individual developers and small teams who want to understand and share agent runs without rearchitecting their observability stack, rungraph is a strong, low-friction addition to the toolkit in 2026.

## FAQ

### What is a rungraph agent run?

A rungraph agent run is a visualization of one coding-agent session loaded from the transcript already stored on disk. Rungraph renders the orchestrator, subagents, and tool calls as nodes with spawn/return edges, marks human interventions, and lets you replay and query the run. It supports Claude Code, Codex, Hermes Agent, opencode, and Cursor with one `npx rungraph` command and no hooks or telemetry.

### How do I ask my agent what happened in a run?

Rungraph ships an MCP server with tools like `list_runs`, `get_graph`, `find_nodes`, `get_detail`, and `focus_nodes`. You connect it to your AI assistant, ask a question about the run in plain language, and `focus_nodes` highlights the exact nodes the answer references in the open dashboard — turning a silent transcript into a question-answerable, visual artifact.

### Is rungraph really zero-instrumentation?

Yes. Rungraph reads the session transcripts your agents already write to disk; it does not install hooks, wrap your commands, or send telemetry. It works retroactively on runs that happened before you installed it, and it makes no network requests — the tool is fully local.

### What agent observability tools compare with rungraph?

The main alternatives are Agentlore (a searchable team log over agent sessions), LangChain SmithDB (a purpose-built enterprise tracing data layer), and Grafana agent observability for Hermes (ingesting run data into standard dashboards). Rungraph differs by being zero-instrumentation, local-first, and graph-native, with MCP-driven interrogation rather than centralized tracing.

### How does rungraph handle secrets when exporting runs?

Agent transcripts capture file contents verbatim, so merely opening `.env` can log its keys. On export, rungraph redacts likely secrets and blocks on high-confidence ones such as AWS keys and GitHub, Slack, or API tokens, so shared `.rungraph` bundles do not leak credential material.
