---
title: "Agent Walking-Dead State Detection: How to Detect and Patch Stalled AI Agents"
date: 2026-09-23T22:01:26+00:00
tags:
  - AI Agents
  - Agent Monitoring
  - Debugging
  - LLM Operations
  - Agent Reliability
description: Detect walking-dead AI agents that run forever but never finish. Learn progress-based detection, work-loop heartbeats, and recovery patterns.
draft: false
cover:
    image: "/images/walking-dead-state-detection-agents-sierra-2026.png"
    alt: "Agent Walking-Dead State Detection: How to Detect and Patch Stalled AI Agents"
    relative: false
schema: "schema-walking-dead-state-detection-agents-sierra-2026"
---

A "walking-dead" AI agent is a process that keeps running, consuming tokens and passing every liveness check, while producing no durable progress toward its task. You detect it not by watching whether the process is alive, but by tracking whether its work actually advances. In one documented case, a SWE-bench Verified agent stayed busy until it used 1.06 million tokens—inspecting, reasoning, and calling tools—yet never wrote the patch, and every health check reported it healthy. This guide shows you how to detect walking-dead states, separate liveness from progress, and patch stalled agents before they burn your budget.

## What is a walking-dead state in an AI agent?

A walking-dead agent is a process that is technically running but semantically stuck. It differs from a crash: a crash is visible and easy to detect, while a walking-dead state hides behind a green "alive" status. The process exists, the port responds, CPU and memory look normal, and no error is logged—yet the work has stopped moving.

The core reframing from monitoring research is that "alive/dead" is a false binary. Asking "is the agent alive?" is the wrong question because the answer is almost always yes. The right question is "is the agent making progress?" A walking-dead agent answers that with a quiet no, masked by every conventional health signal.

These failures are far from rare. A July 2026 preprint ("When Agents Do Not Stop" by Hou, Wang, Zhao, and Wang) scanned 6,549 public LLM-agent repositories and manually confirmed 68 infinite-agent-loop failures across 47 projects. Production telemetry shows the same shape: in one deployment, 12% of tasks marked "in_progress" were actually orphaned, with agents dead for hours while their state never changed.

## The three signals you are confusing: liveness, health, and progress

Monitoring agents reliably fails because people conflate three distinct signals. Treating them as one produces false negatives exactly where walking-dead agents hide.

| Signal | What it proves | What it misses | Typical probes |
|--------|----------------|----------------|----------------|
| **Liveness** | The process exists | Anything about the work | process exists, port responds, PID alive |
| **Health** | The system can operate | Whether work is moving | heartbeat HTTP 200, memory, CPU, error logs |
| **Progress** | Work is advancing | Nothing—this is the truth | lastProgressAt, monotonic step counter, semantic checkpoints |

Liveness and health monitoring catch a frozen process, but they catch none of the walking-dead condition. The agent that burned 1.06 million tokens on SWE-bench Verified passed every liveness and health check. A zombie loop is I/O-bound waiting on LLM responses—it does not spike CPU, does not increase memory, and logs no errors, which is precisely why conventional monitors never flag it.

The fix is to add a third, independent signal: progress. You monitor "is the agent advancing toward completion," not "is the agent breathing." This is the difference between a heartbeat that proves a process exists and a progress marker that proves it is not insane.

## Why heartbeats lie: work-loop heartbeat vs process-level heartbeat

A "heartbeat" only works if it is emitted from the right place. A process-level heartbeat on a background thread returns HTTP 200 even after the main processing loop has stalled, because the timer thread keeps running while the logic thread is frozen. A watchdog watching that heartbeat concludes "still alive" while the agent does nothing useful.

The correct design is a **work-loop heartbeat**: a beat emitted from inside the main processing loop, only when the loop actually advances. If the loop stalls, the beats stop. The heartbeat then means "moved forward," not "still alive."

Decoupling heartbeat from progress—beating on a timer instead of on advance—defeats the entire watchdog. The whole point of the signal is to detect that forward motion has stopped, so it must be tied to forward motion.

Critically, the watchdog that reads this signal must run as a **separate process**, not inside the agent. An in-process watchdog freezes together with the agent body it is supposed to watch. If the agent's loop hangs, so does its internal watchdog, and neither ever reports anything. A separate observer process reads the shared progress file and is insulated from the failure it is meant to catch.

## Detecting the stall: no-progress timeouts and semantic checkpoints

Wall-clock timeouts are the naive tool, and they fail because they cannot tell "agent crunching a 10-minute inference" from "zombie holding a lease forever." A fixed timeout either kills legitimate slow work or lets zombie loops run far too long.

The reliable pattern is a **semantic checkpoint** in addition to the heartbeat. Track two signals:

- **lastUpdatedAt**: the last heartbeat, which proves the agent is alive.
- **lastProgressAt**: the last semantic checkpoint, recorded only when the agent reaches a durable milestone (500 rows processed, each file edited, each mutation committed). This proves the agent is not insane.

The rule is simple: heartbeat lost OR progress stalled beyond a timeout means the agent is marked stalled and its task is released back to the pool. One design distinguishes "crunching hard" from "dead": a heartbeat proves alive, a checkpoint proves sane, and the two together let you tell them apart.

Monitoring research goes a step further and separates activity state from health state. A "waiting" agent that is unhealthy (its context is degraded, its loop is spinning) is a different situation from a "processing" agent that is unhealthy. The first needs a cancel and restart; the second needs an alert, not an interrupt.

Stall thresholds should be per-job-type. Store a `stall_sec` in job metadata, derived from the longest legitimate step and tuned to a p95 baseline. A 10-second stall might be normal for one task type and catastrophic for another.

## The hidden signal: tokens-per-completion and zombie-loop economics

Walking-dead agents are invisible to CPU, memory, and log monitors, but they have one unmistakable signature: token cost per completed unit of work climbs 10–100x. A zombie loop—a repair loop cycling on identical malformed LLM output—shows no CPU spike and no memory growth, but it reliably burns tokens without producing output.

This is why **tokens-per-task-completion** is a high-signal health metric. Input tokens account for 53.9% of agentic spend, and a single doomed fat-tail session that costs 10x the median can dwarf a whole week of healthy ones. In a 50-task SWE-bench Verified report, 51.4% of the $28.54 total model spend sat on the unresolved, non-converging side. A 30-attempt pilot showed the same shape: 38.9% of spend ($5.24 of $13.48) ended with no result file at all.

The runaway cases are dramatic. One reported subagent recursion consumed 1.2M+ tokens in about 30 minutes with the agent tree still growing; another burned roughly 4M tokens in under 5 minutes, and a 50+ level recursion depth was observed (Claude Code #68619 family).

Token-per-completion turns this invisible waste into a monitorable signal. When cost per completed unit spikes by 10x, you do not need to see the loop—you just see the bill and know something is spinning.

## Patching the state: two-stage termination and checkpoint-recoverable work

Once a stall is detected, the recovery action matters as much as the detection. A blanket restart throws away warm context and can make things worse, so pair detection with a deliberate recovery policy.

**Two-stage termination** is the safe kill sequence. Send SIGTERM first so the agent gets a window to clean up and record an "aborted" note. Only if it fails to exit within the window do you escalate to SIGKILL. This preserves any partial work the agent wrote and leaves a durable trace of how the run ended instead of a silent disappearance.

**Checkpoint-recoverable work** is what makes restarts cheap. Externalize state at semantic milestones so any stalled task can resume from its last checkpoint instead of cold-starting. In production data, tasks recovered via checkpoint resume complete 3.2x faster than cold starts, and they avoid recomputing idempotent work. This enables exactly-once semantics for non-idempotent operations and lets you release a stalled task back to the pool "with checkpoint intact."

Loop detection also needs a mechanism. State hashing is a proven approach: hash the prompt plus tool call plus output each step, and if the same hash appears 3+ times within a window, it is looping. An exact-repeat detector works at the action level too: if the same tool call returns the same failure repeatedly, tell the agent to change approach, and let a successful observation clear the streak. Exempt healthy read-only polling so you do not flag legitimate waits.

## A recovery decision matrix (activity x health -> action)

A recovery decision matrix maps each (activity x health) combination to the correct action, replacing a one-size-fits-all restart.

| Activity state | Health state | Recommended action |
|----------------|--------------|---------------------|
| **Waiting** | Healthy | Keep waiting; nothing wrong |
| **Waiting** | Unhealthy | Cancel the call, restart fresh |
| **Processing** | Healthy | Continue normally |
| **Processing** | Degraded | Alert, do not interrupt |
| **Looping / non-converging** | Any | Break the loop with a directive, then verify |
| **Stalled (no progress)** | Any | Two-stage kill, then resume from checkpoint |

The two key cases to internalize: a "Waiting + Unhealthy" agent should be cancelled and restarted (it is unlikely to recover on its own), while a "Processing + Degraded" agent should be allowed to finish with an alert rather than being interrupted mid-valuable-work. A guardian that is a pure observer—reading the state store but never producing state itself—prevents the monitor from becoming another source of state corruption.

One warning from the research: context saturation maps to "Degraded," which means a soft warning, not a restart. Filling a context window is not the same as looping; restarting a context-saturated agent can actually lose a lot of useful state and the LLM's attention. Treat saturation as a warning to let the agent wrap up, not a signal to kill it.

## A minimal reference implementation (watchdog + progress marker)

Here is a minimal pattern you can adopt immediately. The agent writes a progress file with two fields, and a separate watchdog process reads it.

```python
# agent.py -- inside the work loop, on each advance
import json, time, os
PROGRESS = "/var/run/agent-state/progress.json"
def mark_progress(step, note):
    with open(PROGRESS, "w") as f:
        json.dump({"step": step, "lastUpdatedAt": time.time(),
                   "lastProgressAt": time.time(), "note": note}, f)

# Call mark_progress() ONLY when work actually advances:
# mark_progress(rows_done, f"processed {rows_done} rows")
# mark_progress(edit_count, f"edited {edit_count} files")
```

```python
# watchdog.py -- separate process, reads the shared file
import json, time
PROGRESS, STALL_SEC = "/var/run/agent-state/progress.json", 300
while True:
    time.sleep(15)
    try:
        with open(PROGRESS) as f:
            s = json.load(f)
        idle = time.time() - s["lastProgressAt"]
        if idle > STALL_SEC:
            print(f"STALLED: no progress for {idle:.0f}s at step {s['step']}; killing")
            # SIGTERM, wait, then SIGKILL
    except FileNotFoundError:
        print("STALLED: progress file missing; agent never advanced")
```

The key point is that `lastProgressAt` only updates on real advance, and the watchdog runs outside the agent. A heartbeat alone is not enough—a timer-driven heartbeat can fire while the work loop is frozen. The progress marker, updated only at semantic milestones, is the signal that proves the agent is not spinning.

## Preventing stalls at the source: topology, explicit transitions, idempotency

Detection is necessary, but prevention beats it. Several design choices reduce walking-dead states at their source, before a watchdog ever has to fire.

**DAG-shaped agent topologies.** Explicit completed/failed transitions between stages prevent the open-ended loops that arise when an agent can wander between states indefinitely. A well-defined task graph leaves fewer ways to get lost.

**Hard budgets.** A token or time budget caps the worst case. Budgets cannot tell busy work from progress, but they stop a runaway session before it bankrupts a month of token spend. Place a budget checkpoint early—around 60% of the token budget, while tools still work—to write the best partial artifact and ask a blunt convergence question.

**Idempotency keys.** Enforce exactly-once semantics for every mutation. When a stalled task is released and retried, an idempotency key guarantees the retry does not double-apply side effects. This is what makes checkpoint-resume safe.

**Exact-repeat detection baked in.** Hashing each step and flagging repeated hashes, or detecting repeated identical tool failures, stops the most common loop shapes cold.

**Let the stop decision live outside the model.** A model caught in a reasoning loop may never decide to stop on its own. The stop decision belongs to the watchdog and the budget monitor, not to the agent being monitored.

Finally, when you have to stop, save partial work before removing tools. A final no-tools handoff round should produce a human-readable stop reason, not a terse "Agent failed." This turns a failure into an actionable trace.

## FAQ

**What is a walking-dead AI agent?**
A walking-dead agent is a process that keeps running and passing liveness checks while producing no durable progress toward its task. Unlike a crash, it is invisible to conventional health monitoring because CPU, memory, and logs all look normal.

**How do I detect a stalled AI agent that is still running?**
Stop relying on liveness or process-level heartbeats. Add a progress signal: a monotonic step counter and a `lastProgressAt` timestamp written only when work actually advances, read by a separate watchdog process. Mark the task stalled when progress stalls beyond its job-specific timeout.

**Why does a heartbeating agent still get stuck?**
Because a timer-driven heartbeat continues while the work loop is frozen. Use a work-loop heartbeat that fires only on forward advance, and run the watchdog as a separate process so it does not freeze with the agent body it is supposed to watch.

**What is tokens-per-completion, and why does it matter?**
It is model spend divided by units of work completed. Walking-dead agents spike this 10–100x because zombie loops burn tokens without producing output, while staying invisible to CPU, memory, and log monitors. It is the hidden, reliable health signal for loops.

**How do I patch a walking-dead agent without losing work?**
Use two-stage termination (SIGTERM to let it clean up and record an abort note, SIGKILL only after a window) and externalize state at semantic checkpoints so a stalled task resumes from its last checkpoint instead of cold-starting. Checkpoint resume completes tasks about 3.2x faster than cold starts and enables exactly-once recovery.

## Sources

- plori.ai/blog/stop-ai-agent-stuck-in-loop (citing "When Agents Do Not Stop" preprint, July 2026)
- zylos.ai/research/2026-04-03-dual-layer-state-machines-process-monitoring-ai-agents
- agent-swarm.dev/blog/deep-dive-task-state-machine-recovery
- getunblocked.com/blog/why-ai-agents-burn-tokens
- gist.github.com/yurukusa (citing anthropics/claude-code #68619)
- mechanicai.dev/blog/fix-ai-agent-crashes.php
