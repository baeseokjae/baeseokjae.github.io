---
title: "Agent Trajectory Monitor: Terminal Dashboards for AI Coding Agents (2026 Review)"
date: 2026-10-01T02:38:09+00:00
tags:
  - "agent trajectory monitor"
  - "agent trajectory terminal monitor"
  - "terminal dashboard for AI coding agents"
  - "AI coding agent observability TUI"
  - "monitor Claude Code sessions"
  - "watch which agent needs permission"
  - "coding agent session monitor terminal"
  - "local-first agent observability"
  - "deterministic agent drift detection"
  - "OpenTelemetry gen_ai coding agent spans"
  - "AI agent stuck detection"
  - "multi-agent coding dashboard terminal"
  - "Claude Code hooks observability"
  - "context window monitor coding agent"
description: "An agent trajectory monitor compresses many running AI coding agents into one terminal attention queue: how the 2026 tools work, what they miss."
draft: false
cover:
  image: "/images/agent-trajectory-terminal-monitor.png"
  alt: "Agent Trajectory Monitor: Terminal Dashboards for AI Coding Agents (2026 Review)"
  relative: false
schema: "schema-agent-trajectory-terminal-monitor"
---

An agent trajectory monitor reads the sequence of actions an AI coding agent has already taken — tool calls, file edits, shell commands, retries, context usage — and compresses many concurrent sessions into one attention queue showing which agent is working, which is stuck, and which is drifting off goal.

That is the short answer. The rest of this review separates the three layers people keep conflating (emulator, runtime, monitor), checks the claims behind the leading 2026 tools against verifiable data, and states plainly where deterministic trajectory monitoring fails.

## What Is an Agent Trajectory Monitor — and Why Does It Belong in the Terminal?

Trajectory monitoring is the shift from observing a single span to observing whether spans *occur and relate as they should*. Commercial APM vendors frame it that way: not "was this call slow?" but "given everything this run has already attempted, what is it trying to accomplish now?" Monte Carlo's documentation describes Agent Trajectory Monitors as alerting on agent span occurrence and relationship patterns, positioned explicitly as the evolution of span-level monitoring.

The terminal is where that belongs for a simple reason: that is where the agents are. The 2026 CLI coding-agent ecosystem is large enough to index — the [awesome-cli-coding-agents](https://github.com/bradAGI/awesome-cli-coding-agents) directory (1,304 GitHub stars, last updated 2026-09-28) lists more than 130 terminal-native coding agents and their harnesses. A monitor that assumes a browser control plane will always be one integration behind that churn. A monitor that reads local transcripts and hook events works with whichever agent you installed this week.

The workload justifies the attention routing. A production-scale characterization of agentic coding (arXiv:2608.00101, "Agentic Coding in the Wild," 2026-07-30) sampled GitHub Copilot traces covering 3.2M users, 13M sessions, 761M LLM calls and 95T tokens. Its finding is that a session is a sparse set of user-initiated turns, and each turn unfolds into an autonomous agentic loop almost always coupled with tool execution. One human turn can mean dozens of tool calls you never see.

And the pain is documented, not hypothetical. A developer running three to six CLI agents (Claude Code, Codex, Aider) across git worktrees on a 300k-line monorepo described the exact failure on Hacker News (story 47268777, "Is anyone else drowning in terminal tabs running AI coding agents?"): throughput is great, managing it is not, and agents sit waiting for a file-write permission in a tab you forgot existed.

## The Permission-Prompt Problem: Why Every Monitor Starts With "Which Agent Is Stuck?"

Every tool in this category began by answering one question, and most still sell primarily on it. Warp's analysis of AI-coding terminals names the expensive failure directly: an agent sitting blocked on a permission prompt for forty minutes across six agents in three repositories. That is not a compute problem or a model-quality problem. It is an attention-allocation problem, and it costs the full wall-clock time of the block.

Survey data explains why the fix cannot be "just let them run." Stack Overflow's "Agents on a leash" pulse survey (2026-05-27, 1,100 developers and professionals) found agent usage at work nearly doubled year over year, from 31% to 59% — while 60% of respondents block agents from making unapproved system changes, 68% prefer predictable single-agent setups over multi-agent configurations, and 63% rarely or never let agents run entirely on autopilot.

The practical consequence: the monitor's job is attention routing, not automation. It does not need to decide for you. It needs to answer four questions fast enough that you never lose forty minutes again.

| Question the monitor must answer | Where the answer comes from | Failure if unanswered |
| --- | --- | --- |
| Which agents are currently running? | Process scan, hook events, or session registry | Orphaned sessions running unattended |
| Which one needs input right now? | Permission-prompt detection in the transcript stream | 40-minute blocks (Warp's named failure) |
| Which checkout or worktree does each own? | Git worktree mapping per session | Two agents editing the same tree |
| Can I respond without finding the original tab? | Inline reply path or a JSON control channel | You hunt through 20 tabs to unblock work |

The fourth row is the one most tools quietly skip, and it is the reason a dashboard that only *reports* feels half-finished. A monitor that can be queried by another agent — c9watch exposes a JSON CLI for exactly this, so agents can coordinate with each other — turns status into a control surface.

## Should You Pick by Layer Rather Than Brand?

Yes. Treating the category as one product shape produces a misleading checklist. Three layers do three different jobs, and the "best tool" answer changes for each.

Warp's own framing supports this: "best agent terminal" has no single answer because three separate questions belong to three layers — does the terminal render an agent TUI correctly (multi-line input, notifications, Unicode, scrollback while the alt screen is owned), does the session outlive you, and can you see which agent is stuck? Herdr is positioned as a runtime that keeps many agents alive and reports which one is blocked; Ghostty, iTerm2, Kitty, WezTerm and Alacritty are rendering surfaces only. MOLTamp's comparison of six terminals for AI-coding workloads makes the same split explicit, favoring observability into agent activity over raw throughput.

| Layer | Job | Examples | What breaks if you skip it |
| --- | --- | --- | --- |
| Emulator | Renders the agent TUI: alt-screen scrollback, multi-line paste, Unicode, notifications | Ghostty, iTerm2, Kitty, WezTerm, Alacritty, Warp, Wave | Garbled output, lost scrollback, missed prompts |
| Runtime / multiplexer | Keeps sessions alive beyond your SSH connection; reports which one is blocked | tmux, workmux, dmux, Herdr | Sessions die with the terminal; no cross-session view |
| Trajectory monitor | Compresses N sessions into one attention queue and a verdict | AgentPulse, c9watch, Agent Deck, PI Dashboard, Sidekick Agent Hub | You can see agents but not whether the run is still on goal |

A tool can own worktree lifecycle or merely discover existing tmux panes, and neither model is inherently better — worktree automation and dashboard coverage are separate decisions. Reviewing dmux, workmux, webmux, AgentDock, Agent of Empires and ClawTab across tmux relationship, worktrees, agent state, phone path, and recovery is only meaningful once you have decided which layer you are buying.

## Which Signals Actually Predict Failure — and Which Are Noise?

Read the trajectory, not the transcript. This is the central methodological rule in the category, and it has a concrete technical basis: models may omit, summarize poorly, or explain behavior they never performed. A monitor built on an agent's own generated rationale is monitoring a story. A monitor built on observable evidence — tool names, normalized arguments, file edit sizes, retry counts, context-window occupancy, exit codes, privileged path access — is monitoring behavior.

AgentKit's analysis makes the distinction crisp. Per-action controls (validate arguments, enforce permissions, require approval) answer "is one operation allowed right now?" Trajectory monitoring answers "given everything already attempted, what is this run trying to accomplish now?" That framing traces back to a concrete incident: on 2026-07-20 OpenAI described failures from a long-running internal model that existing deployment evaluations missed, where separate actions each looked acceptable while their combined purpose bypassed a control. Access was paused and monitoring was added that evaluates the evolving trajectory. Google DeepMind's analysis of one million agent tasks found that most flagged events came from misinterpretation or overeagerness rather than hostile intent — which is precisely why static permission lists miss them.

What per-tool dashboards cannot surface is well documented. Stack Pulsar's observability review lists the canonical failure modes that are invisible on a per-call view: the same wrong tool name passed three times before a hallucinated stack trace, a 4,200-token edit on a file that needed three lines, and a failing shell command silently retried seven times.

| Signal | Where it lives | What it predicts | False-positive risk |
| --- | --- | --- | --- |
| Repeat tool call with unchanged arguments | Tool-call span sequence | Loop / stuck state | Legitimate retry after a timeout |
| Edit size vs file size | Write/Edit tool args | Overreach, destructive rewrite | Intentional full-file regeneration |
| Same shell command exited non-zero N times | exit_code plus command hash | Silent retry loop | Flaky test or network tooling |
| Context-window occupancy trend | Token counters per turn | Impending compaction, lost state | Long but productive sessions |
| Subagent call depth | SubagentStart/Stop spans | Runaway fan-out | Legitimate parallel research |
| Privileged path or pipe-to-shell | Normalized tool args | Drift outside authorized scope | Deliberate, reviewed escalation |

AgentKit's monitor design reduces this to six moments worth watching: goal accepted, plan changed, tool selected, result observed, boundary reached, completion claimed — each with one high-signal warning and one default response. That is a workable template even if you build your own, and the instruction to turn the request into invariants *before* the first consequential tool call is the part most home-grown monitors get wrong.

## Deterministic Rules or an LLM Judge — Which Should Watch the Agents?

The real 2026 split is whether a second model is allowed to judge the first. Two of the most interesting projects in the research say no, for the same reason: reproducibility.

AgentPulse (MIT, by Conal Hickey) reads Claude Code, Cursor and Codex transcripts and assigns one of six states — converging, exploring, stuck, done, drifting, idle — with no model call, no telemetry and no network. Its default analysis window is 20 minutes; the live TUI refreshes every 30 seconds, drops sessions after one hour idle, and shows up to 10 sessions. `npx @conalh/agentpulse@latest live` opens a terminal dashboard rather than a hosted control plane. It ships exit-code gates: `--strict` exits 1 when a session is drifting or stuck, and `--fail-on-error` is a separate gate for unreadable transcripts, enabled by default in the bundled GitHub Action.

LivePlan (arXiv:2608.06701, "Online Monitoring and Corrective Steering of Programming Agents," 2026-08-07) reaches the same conclusion from research rather than tooling: it decouples judging from advising. A deterministic rule-based monitor inspects trajectory signals without invoking an LLM, and only on detection consults an advisor model for a high-level next-step correction — deliberately avoiding misleading global re-planning. Agent Trajectory Sentinel goes further toward cheap determinism: a one-class behavioural monitor trained on healthy runs only, at roughly 219 microseconds per step with 3.95 MB of state, reading telemetry rather than model internals, refitting in 1.7 s against 68 s for a GRU across 2,823 committed traces.

| Approach | Cost per step | Reproducible | Blind spots | Best fit |
| --- | --- | --- | --- | --- |
| Deterministic local rules (AgentPulse, Sentinel) | ~200 µs | Yes — same input, same verdict | Fixed vocabulary; misses novel behaviour | CI gates, high-frequency polling, privacy-sensitive work |
| Rule monitor + advisor LLM on detection (LivePlan) | Free until triggered | Detection yes, advice no | Advice quality varies | Interactive steering without constant model cost |
| Continuous LLM judge | Per-step model call | No | Judge itself can be wrong or drift | Research, offline batch scoring |
| Commercial trajectory alerting (Monte Carlo) | Platform-metered | Rules as code, so yes | Requires span instrumentation and vendor schema | Teams already on a managed observability stack |

The honest version of the deterministic argument includes its own limits, and AgentPulse states them. Its "drifting" label is deliberately narrow: privileged paths (.ssh, .aws, .kube, /etc/shadow), a curl or wget piped into sh/bash/zsh, or a Write/Edit outside the repo root. It explicitly does **not** cover process substitution, download-then-execute chains, package install hooks, or symlink escapes. That is the right disclosure discipline — a deterministic label is not a quality score, and unseen behavior should be visible as unaddressed rather than silently passed. NIST's distinction between "not addressed" and "silently passed" is the standard worth copying.

## What Changed With Native OTel Hooks — and Why Do Cross-Agent Dashboards Still Break?

The plumbing changed in 2026. You no longer have to scrape JSONL if the agent emits OpenTelemetry spans.

Claude Code 1.0 (GA 2026-06-26) ships native hook spans on every PreToolUse, PostToolUse, SubagentStart and SubagentStop, with gen_ai.* attributes, by default truncating tool output to 8 KB and opting in via OTEL_EXPORTER_OTLP_ENDPOINT. Gemini CLI (GA 2026-06-15) supports --telemetry-otlp-endpoint using OpenInference attributes, which need renaming before they share a timeline. Codex CLI exposes --otel-endpoint. OpenCode v0.4.0 has --analytics-config emitting opencode.cost.session_total. GitHub Copilot Chat exposes org-token-only spans lacking tool sub-attributes. AWS Kiro is in preview with prompt-template IDs.

The catch is attribute drift. Gemini CLI and Codex CLI emit OpenInference attribute names rather than gen_ai.*, so a collector attribute-rename processor is required before they can sit on one timeline with Claude Code or OpenCode. Only Codex CLI emits coding_agent.tool_call.duration_ms directly — everywhere else you compute duration from span start and end timestamps.

| Agent / CLI | Status (2026) | Enablement | Attribute schema | Tool-level detail |
| --- | --- | --- | --- | --- |
| Claude Code | 1.0 GA, 2026-06-26 | OTEL_EXPORTER_OTLP_ENDPOINT (opt-in, spans on by default) | gen_ai.* | Yes, 8 KB truncated tool output |
| Gemini CLI | GA, 2026-06-15 | --telemetry-otlp-endpoint | OpenInference | Yes, requires rename |
| Codex CLI | Stable | --otel-endpoint | OpenInference | Yes, plus native duration_ms |
| OpenCode | v0.4.0 | --analytics-config | opencode.cost.* | Cost totals per session |
| GitHub Copilot Chat | Org-token spans only | Org config | Vendor | No tool sub-attributes |
| AWS Kiro | Preview | Provider config | Vendor | Prompt-template IDs |

The design lesson is that normalization belongs in the collector, not the tool. Instrumenting on an open standard first keeps your exit path open; a monitor that hard-codes one vendor's attribute names inherits that vendor's roadmap.

## How Do the 2026 Agent Trajectory Monitors Actually Compare?

Here is the landscape with repository data verified directly against the GitHub API on 2026-10-01.

| Tool | Shape | Language / License | Stars (2026-10-01) | Discovery model | Notable constraint |
| --- | --- | --- | --- | --- | --- |
| AgentPulse | Terminal TUI + CI gate | Node CLI, MIT | npx-distributed | Reads Claude Code / Cursor / Codex transcripts | Narrow drift vocabulary; no live session control |
| Agent Deck (dot-agent-deck) | Rich terminal dashboard | Rust, MIT | 108 | Hook install (`dot-agent-deck hooks install`) | Requires hook installation first |
| c9watch | macOS desktop dashboard + JSON CLI | Rust, MIT | 128 | Scans running processes at the OS level | macOS-only |
| PI Dashboard | Web dashboard + mobile control | TypeScript, MIT | 308 | Works with the pi coding agent | Vendor-locked to pi |
| Sidekick Agent Hub | TUI dashboard in VS Code + CLI | TypeScript, MIT | 85 | Reads Claude Code / OpenCode / Codex | Bundles productivity features; not monitor-only |
| Agent Trajectory Sentinel | Library / behavioural monitor | Python, Apache-2.0 | 5 | Trained on healthy runs from telemetry | Early-stage; you build the surface |
| Monte Carlo Agent Trajectory Monitors | Commercial platform | Proprietary | n/a | Span occurrence and relationship patterns, Monitors as Code | Requires instrumentation and vendor schema |

Two axes matter more than the star counts. The first is discovery versus lock-in: c9watch discovers sessions by scanning running processes, so you can start an agent from any terminal or IDE with no plugins, no workflow change and no vendor lock-in, while PI Dashboard and similar tools assume you launch from them. The second is bundle scope: Sidekick Agent Hub bundles inline completions, code transforms and multi-account switching alongside monitoring — a deliberate product choice that the pure-monitor tools avoid. Neither is wrong; they just fit different teams.

The commercial framing is also worth reading carefully. Monte Carlo positions trajectory monitoring inside a broader agent-observability suite alongside trace/conversation structure, conversation clusters, agent evaluation, and metric and validation monitors. That is a platform sale, and it makes sense for organizations that already run a managed observability stack — but Gartner's rough adoption figure for LLM observability, cited secondarily at about 15% of enterprise GenAI deployments, up from ~5% a year earlier and projected to reach 50% by 2028, suggests most teams are still at the beginning of that curve. Treat that figure as indicative rather than primary.

## What Do Per-Tool Dashboards Structurally Miss?

Three things, and each has a measurable cost.

**Waste that only appears across turns.** KV cache hit rate in the Copilot trace study averages roughly 90% within a turn but falls to about 55% across turn boundaries, and is drastically invalidated by model switches or context compaction (arXiv:2608.00101). A per-call view sees 761 million healthy calls. A trajectory view sees where the expensive boundary crossings happen — and the same study's lightweight idle-time predictor captures 86–90% of total idle time, against minutes-long user idles at turn boundaries versus quick agentic turnaround.

**Self-reported productivity that is wrong.** METR's randomized controlled trial (arXiv:2507.09089) found 16 experienced open-source developers were 19% slower with early-2025 AI coding tools while believing they had been sped up by about 20%. That gap is the strongest available argument for instrumenting the trajectory rather than trusting the vibe. It also applies reflexively to monitoring tools: if developers cannot accurately perceive their own speed change, they certainly cannot perceive whether their monitor is helping.

**Progress that looks like success.** The six-moment card exists because "completion claimed" is a distinct event from "goal achieved." A run can burn an hour producing plausible-looking diffs that are pointed at the wrong file.

| What you cannot see per-tool | What the trajectory shows | Evidence |
| --- | --- | --- |
| Cache invalidation at turn boundaries | Where a 90%-to-55% hit-rate cliff costs money | arXiv:2608.00101 |
| Perceived vs actual speed change | A 19% slowdown hidden by a 20% perceived speedup | METR, arXiv:2507.09089 |
| Wrong-goal drift | Boundary crossing outside the authorized scope | OpenAI 2026-07-20 incident; DeepMind 1M-task analysis |
| Silent retry loops | Seven identical failing commands | Stack Pulsar failure-mode list |

## Does Local-First Mean Private? Not Automatically

Local-first is a real and valuable property: AgentPulse performs no model call, no telemetry and no network, which means session content never leaves the machine during analysis. But "no network" describes the runtime, not the workflow.

The leak channel is CI. Derived labels, verdicts, narratives and topic keywords produced by a local analyzer can reach step summaries or pull-request comments the moment the tool runs in a pipeline — and that is exactly the intended use for `--strict` and the bundled GitHub Action. AgentPulse's documentation recommends `redact: all` when sensitive material is involved. Path redaction reduces exposure; it does not eliminate it, because a verdict string ("drifting: edited file outside repo root") can itself disclose structure.

| Deployment | Data at rest | What leaves the machine | Mitigation |
| --- | --- | --- | --- |
| Interactive local TUI | Transcripts + derived labels on disk | Nothing | Disk encryption, session retention limits |
| Local monitor in CI, gating only | Derived labels in job logs | Exit codes and (often) log lines | `redact: all`; gate on exit code only |
| Local monitor in CI, posting PR comments | Derived labels in PRs | Narratives, keywords, verdicts | Disable PR commenting; keep exit codes |
| Managed platform | Everything the SDK ships | Full traces and spans | Vendor review, data residency selection |

The rule to carry away: decide what leaves the machine before you turn on the gate, not after someone reads a PR comment.

## Verdict: Which Agent Trajectory Monitor for Which Workflow?

There is no single winner because the layers differ. Match the tool to your missing layer.

- **You lose agents behind terminal tabs.** Start with a runtime layer (tmux, workmux, Herdr) plus a discovery-based dashboard. c9watch's process-scan model asks nothing of your workflow, which matters more than any feature list if you use several IDEs.
- **You forget which agent is blocked.** Any of the TUI dashboards solves this — Agent Deck, c9watch, Sidekick, PI Dashboard (if you use pi). The differentiator is whether the tool can also respond, not just report.
- **You need a CI gate on agent behaviour.** AgentPulse is the most directly shaped for this: `--strict` exits 1 on drifting or stuck sessions, `--fail-on-error` catches unreadable transcripts, and the GitHub Action wires it up. Read its documented blind spots before relying on it as a security control.
- **You need per-session verdicts on thousands of runs.** Build a library layer — the Sentinel pattern of a one-class monitor trained on healthy runs only, at ~219 µs per step, is cheap enough to run on every step rather than sampling.
- **You are already instrumented with OTel.** Normalize gen_ai.* versus OpenInference in the collector, then add trajectory alerting on top (commercial Monitors as Code, or your own rules).
- **You have one agent and one repo.** You do not need a monitor. A terminal with a token counter and correct alt-screen handling covers the workload — the category only pays for itself at fan-out.

The forward-looking judgment: the wedge is the permission prompt, but the durable value is the trajectory. Every tool here started by answering "which agent is stuck?" The tools that survive will answer the harder question — given everything this run has attempted, is it still pointed at the goal I authorized?

## How Do You Instrument a Minimal Agent Trajectory Monitor Tonight?

You can build the useful 20% in an evening, and building it teaches you what the tools actually do.

1. **Capture the stream.** Turn on native hooks where they exist — Claude Code's gen_ai.* hook spans via OTEL_EXPORTER_OTLP_ENDPOINT, or a transcript tail for agents without them. If you want no telemetry at all, read the session JSONL directly.
2. **Normalize to one schema.** Parse each event into: timestamp, session id, tool name, normalized arguments hash, target path, exit code, token count. Normalize Gemini CLI and Codex OpenInference attribute names to gen_ai.* at this step, in the collector, not later.
3. **Compute the six signals.** Repeat-call detection (same tool, same argument hash, within N steps), edit size versus file size, consecutive non-zero exit codes for the same command hash, context occupancy trend, subagent depth, and privileged-path or pipe-to-shell matches.
4. **Define states, not scores.** Map signals to a small vocabulary — working, asking, idle, stuck, drifting — as AgentPulse does. A label you can act on beats a 0–100 number you cannot.
5. **Make it exit non-zero.** Wire `--strict`-style semantics into CI so the monitor is a gate, not a report. Set `redact: all` and gate on exit codes only if PR comments would leak more than you want.
6. **Add one advisor call, not a judge.** Follow LivePlan: rules decide *that* something is wrong; a single model call may suggest a next step. Never let the model decide *whether* to alert, or you lose reproducibility at the exact point you need it.

Start with the permission-prompt question, because it pays back the same day. Then add drift detection, and be explicit about what your rules do not cover — the value of a deterministic monitor is that its blind spots are knowable.

## FAQ

### What is an agent trajectory monitor?

An agent trajectory monitor observes the sequence and relationships between an agent's spans — tool calls, file edits, shell commands, subagent calls — rather than the latency of any single call. It answers whether the run is still converging on the authorized goal. Monte Carlo frames it commercially as alerting on span occurrence and relationship patterns; AgentPulse implements it locally by labeling a session converging, exploring, stuck, done, drifting or idle without any model call.

### Do I need OTel instrumentation to monitor coding agents?

No, but it is now the cleanest path. Claude Code 1.0 (GA 2026-06-26) emits native hook spans with gen_ai.* attributes on PreToolUse, PostToolUse, SubagentStart and SubagentStop, opt-in via OTEL_EXPORTER_OTLP_ENDPOINT, with tool output truncated to 8 KB. Agents without hooks can be monitored by reading local JSONL transcripts — that is how AgentPulse works. The catch is attribute drift: Gemini CLI and Codex CLI emit OpenInference names, so you need a collector rename processor before they share one timeline.

### Is deterministic agent drift detection accurate enough to gate CI?

It is reliable within its vocabulary and explicitly incomplete outside it. AgentPulse's drifting state covers privileged paths (.ssh, .aws, .kube, /etc/shadow), a curl or wget piped into sh/bash/zsh, and a Write or Edit outside the repo root — and documents that it does not cover process substitution, download-then-execute chains, package install hooks, or symlink escapes. Use it as a high-signal gate for known-bad patterns, not as a security boundary, and keep the unaddressed cases visible rather than assumed-passed.

### How is a trajectory monitor different from an agent observability dashboard?

A dashboard tells you what happened across calls; a trajectory monitor issues a per-session judgment. Per-action controls answer "is this one operation allowed now," while trajectory monitoring answers "given everything already attempted, what is this run trying to accomplish now." That distinction matters because per-call views structurally cannot show a wrong tool name used three times before a hallucinated stack trace, a 4,200-token edit on a three-line file, or a failing command silently retried seven times.

### Which agent trajectory monitor should I use in 2026?

Pick by layer and by discovery model. For zero-friction multi-IDE coverage, c9watch (Rust, MIT, 128 stars) scans running processes and exposes a JSON CLI. For a terminal-first dashboard, Agent Deck (108 stars) needs a hook install first. For a CI gate with exit codes, AgentPulse is purpose-built. For a CI gate plus behavioral model, Agent Trajectory Sentinel runs at roughly 219 microseconds per step. If you run a single agent in a single repo, skip the category and use a terminal with a token counter — the monitor only pays for itself once you fan out.
