---
title: "ollama-llmwatch Review: Live Prefill Progress Monitoring for Ollama"
date: 2026-10-01T09:31:11+00:00
tags:
  - "ollama model monitoring"
  - "ollama llmwatch"
  - "ollama-llmwatch review"
  - "ollama live prefill progress"
  - "ollama prefill progress bar"
  - "ollama tok/s monitor"
  - "ollama server log monitoring"
  - "ollama prompt_eval_cached_count"
  - "ollama prompt cache monitoring"
  - "ollama ttft monitoring"
  - "local llm observability terminal"
  - "why is my local model slow prefill"
description: "ollama-llmwatch is a zero-dependency terminal monitor that tails Ollama's server log to show live prefill progress, tok/s, cache reuse and TTFT."
draft: false
cover:
  image: "/images/ollama-llmwatch-live-prefill-progress-monitoring.png"
  alt: "ollama-llmwatch Review: Live Prefill Progress Monitoring for Ollama"
  relative: false
schema: "schema-ollama-llmwatch-live-prefill-progress-monitoring"
---

ollama-llmwatch is a free, MIT-licensed Python terminal monitor that tails Ollama's own server log and turns it into a live prefill board: tok/s sparklines, prompt-cache reuse percentage, time-to-first-token, a progress bar with ETA, and plain-language diagnostic hints. It never calls the Ollama API and adds zero inference overhead.

## What Is ollama-llmwatch and Why Does Ollama Model Monitoring Need It?

Most Ollama monitoring tools watch the wrong layer. They scrape an API response, count tokens after the fact, or read a Prometheus endpoint that may not exist. None of them can tell you what is happening during prefill — the window where your prompt is being read and nothing at all is being emitted.

ollama-llmwatch takes a different route. It reads Ollama's server log file passively and reconstructs what the runner is doing right now. The project is a small, MIT-licensed Python TUI created in August 2026, sitting at 4 GitHub stars with roughly 70 PyPI downloads in the last month as of October 7, 2026 — genuinely early software in a genuinely underserved lane.

That lane exists because of a hole in Ollama itself. Issue #3144, "add /metrics endpoint," has been open since March 14, 2024 with 141 reactions and 48 comments, making it the most-requested observability feature in the repository. Two competing implementations are open right now: PR #16998 (July 1, 2026, an opt-in `GET /metrics` behind `OLLAMA_METRICS=1`, +936/-50 across 13 files) and PR #18508 (September 17, 2026, +407 across 4 files, described by its author as an alternative rather than a replacement). Streaming prefill progress was proposed separately in PR #13901 on January 25, 2026, and has sat open with zero comments ever since, described by its own author as a messy proof of concept.

Until one of those lands, there is no supported server-side metrics surface for Ollama. Every tool in this space is working around a missing server feature, and log-readers like llmwatch exist precisely because the log is the only place the information already lives.

## Why Does Ollama Send Nothing At All During Prefill?

Because of how the request lifecycle is structured. When you send a prompt to Ollama, the work splits into two phases:

1. **Prefill** — the model reads the entire prompt, building the KV cache. No tokens are emitted. From the API's point of view, nothing is happening.
2. **Generate** — the model emits tokens one at a time. This is what the streaming API reports.

The API gives you the first token, then a usage object at the end. In between, during prefill, the wire is silent. No token, no progress event, no usage. Every wire-level and API-level monitor is therefore structurally blind to the window where most of the wall-clock time actually goes.

How much time? The ollama-llmwatch README's own worked example is a coding agent sending 30,000–55,000 tokens of instructions every single turn. On an M1 Max running a 27B model, that is roughly **eight minutes of silent reading** before a single character appears — while the answer itself takes about twenty seconds. The tool's headline metric, the WAIT bar, measures exactly this. Its own sample board shows **91% of session time spent in prefill** across 12 requests totaling 18 minutes and 4 seconds.

That is the whole argument for the tool in one number. If 91% of your session is prefill and your monitor only reports generation tok/s, you are optimizing the 9%.

## How Does ollama-llmwatch Work Without Calling the Ollama API?

It tails the server log file. That single design decision explains most of the tool's strengths and all of its limitations.

The log is verbose and structured. Every line is tagged with a slot and a task id, for example:

```
slot print_timing: id 0 | task 2313 | prompt processing, n_tokens = 4096, progress = 0.27
```

The tool watches those `print_timing` lines with `tail -F` and reconstructs state from them. Because it reads a file rather than joining the request path, it adds **no inference overhead whatsoever** — it cannot slow down a request because it is not in the request. Because it reads Ollama's log rather than Ollama's API, it works identically whether your client is a Python script, Claude Code, a Codex CLI, an IDE plugin, or something that does not speak HTTP at all. And because the log carries a slot/task id, it can attribute progress to individual requests, which is how the per-request recent table and the cache accounting work.

The trade-off is equally direct: **the log format is internal and unstable.** Ollama offers no stability guarantee for it. The project mitigates this by shipping tests against real captured logs in `tests/fixtures/*.log` to catch drift early, but a minor Ollama release that reshapes those lines will break the parser until the author catches up. That is an inherent cost of the log-reading approach, not a fixable bug.

Ollama's log lives in different places per platform, which the tool has to handle:

| Platform | Ollama log location |
|---|---|
| macOS | `~/.ollama/logs/server.log` |
| Linux (systemd) | `journalctl -u ollama` |
| Docker | container stdout / `docker logs` |
| Windows | `%LOCALAPPDATA%\Ollama\server.log` |

Notably, that asymmetry maps directly onto the tool's platform support record — see the limitations section below.

## What Do the Numbers on the Live Board Actually Mean?

The board is dense by design. Each panel answers a different question, and the diagnostic hints are what make it readable without you needing to carry a mental model of Ollama's internals.

| Panel | What it shows | The question it answers |
|---|---|---|
| PREFILL | tok/s peak / avg / low with sparklines | How fast is the prompt being read, and is it degrading? |
| GENERATE | tok/s peak / avg / low with sparklines | How fast is output coming out? |
| CACHE | Cache reuse percentage | How much of this prompt did I actually have to pay for? |
| TTFT | Time to first token: min / avg / max | How long before I see anything? |
| WAIT | Share of session spent reading vs generating | Which problem do I actually have? |
| SYSTEM | Swap warning | Is the model spilling out of memory? |
| Recent requests | Per-request table | Which request was the slow one? |
| Progress | Live progress bar with ETA | How much longer? |

The **hints** are the most useful part for anyone who has not memorized Ollama's internals. Instead of leaving you to interpret `n_tokens = 39528, progress = 0.0`, the tool states the conclusion:

- `! cache gone - rereading all 39,528 tok`
- `! same prompt 5x - likely stuck`
- `! 3 cancels in a row - client keeps timing out`
- `! slow: 40 vs 100 tok/s usual - 2 models loaded (34 GB), swapping`

That is a diagnostic layer, not a dashboard. The difference matters: a dashboard gives you numbers you must interpret; these lines give you a verdict you can act on.

### How does the progress bar stay honest?

By projection, with a clamp. Ollama only writes a progress line every **512 tokens**, which at typical prefill speeds means updates land 5–10 seconds apart. A bar that only moved every 5–10 seconds would be useless for an eight-minute prefill. So llmwatch takes the last measured rate and projects position forward, repainting roughly **10 times per second**, while clamping the estimate so the bar never claims work that has not happened yet. It is an honest interpolation rather than a fake, which is why it does not overshoot and then snap backwards.

### Why does it deliberately not show CPU or GPU percentage?

Because those numbers do not move when performance does. A GPU running locally sits pinned near 100% whether you are getting 13 tok/s or 8 tok/s — utilization is not a signal for inference speed, it is a signal that the GPU is busy. The tool's authors say so explicitly in the README. Instead, slowdowns are detected from **measured throughput** and its trend, which is the quantity you actually care about.

## What Is the prompt_eval_cached_count Trap in Ollama 0.33.3?

This is the single most valuable thing in the tool's documentation, and it applies to anyone measuring prefill throughput — whether or not they run llmwatch.

Ollama 0.33.3 shipped on September 2, 2026. It added `prompt_eval_cached_count` to `/api/generate` and `/api/chat`, and **redefined `prompt_eval_duration` to cover only the uncached prompt tokens**. Meanwhile `prompt_eval_count` still means the total prompt size.

That means the formula everyone has always used:

```
prefill tok/s = prompt_eval_count / prompt_eval_duration
```

now divides the **total** token count by the time for **only some** of them. The error scales with your cache-hit ratio — which means it is worst in exactly the steady-state agent loop developers actually care about, where the cache is warm and most of the prompt is cached.

In one measured example, the naive formula reported **4,375 tok/s where the honest figure was 115 tok/s** — a **38x over-report, with no error and no warning.** Ollama has its own `Metrics.Summary()` changed to handle this correctly, and `prompt_eval_cached_count` is declared as a nullable `*int` in `api/types.go` (`PromptEvalCachedCount *int, omitempty`), which means an absent field means *unknown*, not *zero*. Tooling that treats missing as zero will quietly produce nonsense.

### How Do You Calculate Prefill Throughput Correctly?

Subtract the cached tokens before dividing:

```
prefill tok/s = (prompt_eval_count - prompt_eval_cached_count) / prompt_eval_duration
```

That is the documented fix, and it is what Ollama's own metrics summary does internally.

The same cache fact is also exposed under three different names depending on which API surface you are using, which makes cross-tool comparison easy to get wrong:

| API surface | Field name | Meaning |
|---|---|---|
| Ollama native | `prompt_eval_cached_count` | Cached prompt tokens |
| OpenAI-compatible | `usage.prompt_tokens_details.cached_tokens` | Cached prompt tokens |
| Anthropic-compatible | `usage.cache_read_input_tokens` | Cached prompt tokens |

There is a further wrinkle: the Anthropic-compatible `input_tokens` field quietly changed to mean *total minus cached*. The same identical prompt reported `input_tokens` of 38 when cold and 1 when warm. If your cost or analytics pipeline consumes that field, your input token counts have silently changed meaning.

### Why Is Prompt Layout Worth 3.5x Locally?

Because KV-cache reuse is **prefix-ordered and all-or-nothing from the first divergent token.** Everything matching at the head of the prompt is reused; from the first differing token onward, everything is recomputed.

A measured example makes this concrete. Same model, same 324-token system prompt, identical wording — the only change was moving a 21-token timestamp from the top of the prompt to the bottom. Prefill fell from **64.6 ms to 18.6 ms**: a 3.5x difference, from layout alone.

Hosted providers document the advice — put stable content first, volatile content last. Locally, until you have a tool that reports cache reuse, you get **zero feedback about whether you are following it.** That is precisely what the CACHE panel and the `! cache gone` hint provide.

There is one measurement lesson worth internalizing, learned the hard way by the maintainer of a competing observability tool: comparing whether layout B reuses layout A's cache is the wrong question, because real traffic sends the same layout every turn with a fresh value. Each layout has to be sent **twice** — once with its own values, once with those values changed — and only the second send tells you the truth about cache behavior.

## Why Do Turn Times Look 35x Longer Than Request Times?

Because turn time is not request time, and for agent users the gap is enormous.

Measured on one machine with the same model: a median turn of **57.3 seconds at low reasoning effort** versus **33 minutes 29 seconds at high effort** (n=6 and n=5 respectively) — roughly a **35x difference**. Same hardware, same weights, same request shape. The variable is how much the model thinks before it answers.

This reframes what a monitoring tool should report. A per-request tok/s meter answers "how fast is the engine." An agent user needs "how long until I get my answer," and those are separated by reasoning effort, tool calls, multiple round trips, and repeated prefill across turns.

The same measurement discipline applies to speculative decoding, where the tool's data is a useful cautionary tale. Acceptance rates measured on one M1 Max, same model, three prompt types:

| Workload | Draft acceptance | Speed effect |
|---|---|---|
| Code / structured output | 58–81% | ~1.5x faster |
| Rote output / lists | 93% | ~2x faster |
| Freeform prose | 18% | **0.6x — slower than no drafter** |

The same drafter makes you twice as fast or noticeably slower depending on what you ask for. Without per-workload measurement you cannot know which one you are getting — and the default assumption ("speculative decoding is a speedup") is wrong a third of the time.

Generation speed itself is bandwidth-bound and model-size-bound. On an M1 Max: 27B at Q4 runs 10–17 tok/s, 14B at Q4 runs 25–30 tok/s, and MoE models such as Qwen3-30B-A3B run much higher because only a fraction of weights are read per token. Note that these are generation numbers; prefill is a different regime and often the larger cost.

## Ollama llmwatch vs toptop vs ollama-metrics vs LLMxRay vs Langfuse

The category splits cleanly by data source, and each source determines which questions a tool can answer. This is the comparison table to keep.

| Tool | Data source | Live prefill progress? | Cache accounting? | GPU / KV / queue? | Best for |
|---|---|---|---|---|---|
| **ollama-llmwatch** | Ollama server log (`tail -F`) | **Yes** | **Yes, per request** | No (by design) | Always-on terminal pane beside your agent |
| **toptop** | HTTP metrics endpoints + Ollama `/api/ps` | No | No | Yes (KV, queue, TTFT, tok/s/watt) | Fleet view, Grafana, pasteable verdicts |
| **ollama-metrics** | Transparent reverse proxy | No | No | Partial | Prometheus sidecar with a ready Grafana dashboard |
| **LLMxRay** | Live daemon, browser UI | No | Yes (measured against live daemon) | Yes | Browser dashboard, cache-reuse measurement |
| **Langfuse / LangSmith / Helicone** | Wire-level request tracing | No | Provider-reported only | No | Cloud LLM observability and cost |

Two entries deserve more detail.

**toptop** is the closest direct competitor: Rust, GPLv3, roughly 18 stars, a single static binary with zero runtime dependencies, and explicitly branded "the local-inference observability layer for your terminal." It auto-discovers local inference servers and scrapes their metrics endpoints with no configuration — llama.cpp, vLLM and TGI Prometheus `/metrics`, plus Ollama's `/api/ps`. It shows live generation *and* prefill tok/s, KV-cache pressure, queue depth and TTFT, and adds tokens/sec/watt by fusing throughput with GPU power draw. `toptop --diagnose` prints a pasteable 72-column verdict such as `MEMORY-BANDWIDTH BOUND - bandwidth 92% / compute 24%`; Ollama users get `MODEL PARTLY ON CPU` or `MODEL RUNNING ON CPU`. It also exports Prometheus/JSON and runs a long-lived `:9709 /metrics` endpoint for Grafana, with a multi-host fleet view over SSH.

The key contrast is the data source. **toptop reads HTTP metrics endpoints; llmwatch reads the log.** toptop therefore sees KV state, queue depth, TTFT and GPU state, but it cannot see in-flight prefill progress or per-request cache accounting the way a log parser can. Neither is strictly better: they are answering different questions from different sources.

**ollama-metrics** represents the proxy-meter category: a transparent reverse proxy that forwards to Ollama and exposes token usage, request duration, inference speed, model memory and load status (~42 stars, last push June 24, 2025). Zero configuration, no modification to Ollama, a pre-built Grafana dashboard, configurable via `OLLAMA_HOST` / `PORT`, shipped as `ghcr.io/norskhelsenett/ollama-metrics`. Its structural limit is worth stating plainly: **it only knows about requests that go through it, and it only learns numbers at response time.** The silent prefill window is invisible to it.

**LLMxRay** (~11 stars, Apache-2.0, npm package `llmxray` v0.6.0, roughly 380 downloads in the last month) is a browser-based local LLM observatory with chat, streaming, reasoning, RAG, introspection and metrics. Its maintainer published the definitive write-up on Ollama 0.33.3 breaking the standard prefill formula, and it ships a page that measures cache reuse against your live daemon rather than estimating it. It is a dashboard rather than a terminal companion — a different lane from llmwatch's always-on pane.

Finally, **Langfuse / LangSmith / Helicone** and agent-level meters such as agentacct (~766 stars) and tokentelemetry (~376 stars) sit in adjacent territory. Those tools answer "what did this cost me" by attributing tokens and dollars per run, task or work step. llmwatch answers "why is this request slow right now." Different questions, different data sources, no overlap in what they can see.

## How Do You Install and Run ollama-llmwatch?

The install story is deliberately simple, and the dependency count is the selling point: **zero runtime dependencies, Python 3.9+.**

```bash
# via uv
uv tool install ollama-llmwatch

# via pipx
pipx install ollama-llmwatch
```

Note the package name: it is `ollama-llmwatch` on PyPI, not `llmwatch`, because the name `llmwatch` was already taken. Both entry points are installed — `ollama-llmwatch` and `llmwatch` — so either command starts the board.

There is also a single-file mode for people who would rather not install anything. Because the project ships a regenerated bundled script (`llmwatch.py` produced by `tools/bundle.py`), you can run the file directly. That is a real option on a machine where you cannot or will not install packages.

Once running, the CLI back-end covers non-interactive use:

```bash
llmwatch --plain          # no TUI, plain output
llmwatch --last           # just the last request
llmwatch --json           # machine-readable
llmwatch --codex          # Codex-shaped output
llmwatch --history --days 7
llmwatch --turns --days 7
llmwatch --compare A B    # compare two runs
llmwatch --export csv
llmwatch --no-history
llmwatch --debug-unparsed
```

For OpenAI-compatible servers that are not Ollama, there is a `--proxy` mode on port 8081, aimed at mlx-lm, LM Studio and vLLM. Those servers' logs carry no token counts, so the proxy supplies what the log cannot. llama.cpp is the documented exception and uses `--log` instead, because its log does carry the needed information.

History lands in SQLite at `~/.local/share/ollama-llmwatch/history.db`, in `requests` and `turns` tables, storing timings, model names and effort levels. There is deliberately **no column that could hold prompt text** — a privacy decision worth noting for anyone running the tool on work prompts.

`--debug-unparsed` is the escape hatch to reach for if a new Ollama release changes the log format: it shows you exactly which lines the parser is dropping.

### What are the Linux caveats?

Real ones, and the author states them rather than hiding them. The tool was developed and verified on **macOS**. The Linux path (journald) and the Docker path are, in the author's own words, "written but unverified." Windows is not supported. So if you run Ollama under systemd on Linux — the most common server deployment — you are on an unverified code path. It may work; you are the test.

## What Can ollama-llmwatch Not Do?

An honest limitations list, in descending order of practical importance:

- **Remote servers.** It reads a local log. Monitoring an Ollama instance on another host means getting the log to you first.
- **Internal log format dependency.** Ollama offers no stability guarantee for the lines the parser depends on. Fixture-based tests catch drift, but they do not prevent it.
- **macOS-only verification.** Linux and Docker are written-but-unverified; Windows unsupported.
- **No GPU, KV or queue visibility.** By design — it reads throughput instead. If you need bandwidth-bound vs compute-bound verdicts, that is toptop's lane.
- **Very early adoption.** 4 stars, 0 forks, 0 subscribers, 0 open issues; PyPI downloads of 69 in the last month, 14 in the last week, 1 in the last day (as of October 7, 2026). 13 closed issues suggest the author is responsive, but there is no community depth.
- **Release skew.** The latest published PyPI version is **0.9.1** (uploaded August 18, 2026), while the GitHub CHANGELOG and README badge already describe **0.9.2** (the package split into `llmwatch/` modules with `llmwatch.py` regenerated by `tools/bundle.py`). Version 0.8.0 shipped to GitHub and **never reached PyPI at all**. Published versions are 0.5.1, 0.5.2, 0.5.3, 0.6.0, 0.7.0, 0.9.1 — gaps included. If you install from PyPI you may not get what the README describes.

The context for that last point matters: the category is small because the problem is real. Ollama itself is at 182,491 stars and 18,137 forks, llama.cpp at 130,606, vLLM at 93,342, with recent releases v0.35.0 (September 28, 2026) and v0.40.0-rc0 (September 25, 2026). Meanwhile cache-related prefill defects are active on Ollama's own tracker: #16051 (open, MLX bf16 cold prefill 60–400x slower than warm even when the model fits in RAM), #18505 (open, MLX nvfp4 requests stalling in prefill at `processed = total - 1` for minutes under single-slot load), #18267 (closed, prefix-cache restore truncated to a multiple of 8192 cost a fixed 17–27s re-prefill after every cold prompt), and #17829 (closed, MLX had no prompt caching between requests at all — full re-prefill every agent step). Prefill throughput is an active obsession in r/LocalLLaMA for good reason.

## How Do You Actually Reduce Prefill Wait?

The diagnostic value of the tool is that it tells you which of these to do. Prefill and generation have different bottlenecks, and the fixes are not interchangeable.

**1. Shrink the prompt.** Prefill cost scales with prompt length. If your WAIT bar says 91% of session time is prefill, prompt size is your lever — not inference flags. Trimming a 40,000-token instruction block is worth more than every sampler setting combined.

**2. Put stable content first.** KV reuse is prefix-ordered and all-or-nothing from the first differing token, worth 3.5x in the measured example above. Move timestamps, session ids, user names and any per-turn value to the **bottom** of the prompt and leave the system prompt and static instructions at the top.

**3. Verify with the second send.** Do not test whether layout B reuses layout A's cache. Send each layout twice — once with its values, once with them changed — and only trust the second measurement.

**4. Check for swap and multi-model residency.** The SYSTEM panel warns on swap, and the hint `! slow: 40 vs 100 tok/s usual - 2 models loaded (34 GB), swapping` is the canonical version of this problem. If two models are resident and the machine is swapping, every phase slows down until one is unloaded.

**5. Consider MoE models for throughput.** MoE architectures such as Qwen3-30B-A3B run far faster than dense models of similar size because only a fraction of weights is read per token. If you are bandwidth-bound, this is the structural fix rather than the tuning fix.

**6. Measure speculative decoding per workload before trusting it.** 93% acceptance on lists (2x faster) versus 18% on prose (0.6x, slower than no drafter) is the whole story. Turn it on for code, off for prose, and measure rather than assume.

**7. Watch the WAIT bar, not just tok/s.** It is the tool's headline metric for a reason: it tells you which of prefill and generation is actually consuming your session.

## Verdict: Who Should Run ollama-llmwatch?

The honest verdict is that this is **novel in category and very early in maturity** — and both halves of that sentence are true.

What it does that nothing else does: it shows in-flight prefill progress, per-request cache accounting, and the WAIT split, because it reads the one place that information exists. If you run a local coding agent against a large model on a Mac and you have ever watched a blank terminal for minutes wondering whether it was working, this tool answers that question directly, with a progress bar that does not lie and hints that tell you what to do about it.

What to expect from a four-star tool: roughly 70 PyPI downloads last month, macOS-verified only, an unverified Linux path, an internal log format Ollama does not promise to keep, and a PyPI release that trails the GitHub README. Zero runtime dependencies and a genuinely responsive 13-closed-issue history are real mitigations, and a single-file run mode means the risk of installing it is close to zero.

Who should skip it: anyone monitoring remote Ollama hosts, anyone who needs Prometheus/Grafana integration or fleet-wide views (use toptop or ollama-metrics), anyone who needs GPU utilization and power draw numbers (toptop), and anyone on Windows.

The most transferable thing here is not the tool — it is the measurement lesson. The `prompt_eval_cached_count` redefinition quietly made the standard prefill formula over-report by up to 38x, and cache-ordering alone is worth 3.5x. Even if you never install llmwatch, check your own prefill math against Ollama 0.33.3, and check where your volatile prompt content sits.

## FAQ

**What is ollama-llmwatch?**
It is a free, MIT-licensed Python terminal monitor for Ollama with zero runtime dependencies and Python 3.9+ support. It tails Ollama's server log passively to display live prefill progress, generation tok/s, prompt-cache reuse, time-to-first-token, and a WAIT bar showing what share of your session went to reading versus generating. It never calls the Ollama API, so it adds no inference overhead.

**Does ollama-llmwatch slow down my Ollama requests?**
No. It reads the server log file with `tail -F` and never joins the request path, so it adds zero inference overhead. This is the structural advantage of the log-reading approach over proxy meters, which sit in front of Ollama and only learn their numbers at response time.

**Why does Ollama show no progress during prefill?**
Ollama's API emits the first token and a usage object at the end, with nothing in between. Prefill — reading the prompt and building the KV cache — produces no tokens, so the wire is silent. Server-side streaming prefill progress was proposed in PR #13901 (January 25, 2026) and remains open with no comments, and there is still no `/metrics` endpoint (issue #3144, open since March 2024).

**What is prompt_eval_cached_count and why does it matter?**
Ollama 0.33.3 (September 2, 2026) added `prompt_eval_cached_count` and redefined `prompt_eval_duration` to cover only the uncached prompt tokens, while `prompt_eval_count` still means the total prompt size. The classic formula `prompt_eval_count / prompt_eval_duration` therefore over-reports prefill throughput by roughly your cache-hit ratio — up to 38x in one measured case, with no warning. The correct formula is `(prompt_eval_count - prompt_eval_cached_count) / prompt_eval_duration`.

**Is ollama-llmwatch better than toptop or ollama-metrics?**
They answer different questions. llmwatch is the only one that shows live in-flight prefill progress and per-request cache accounting, because it reads the log. toptop scrapes metrics endpoints and adds KV-cache pressure, queue depth, tokens/sec/watt and bandwidth-versus-compute verdicts. ollama-metrics is a Prometheus sidecar with a ready Grafana dashboard, but is blind to prefill because it only learns numbers at response time. Choose by data source, not by feature count.

## Sources

- ollama-llmwatch repository and README — https://github.com/bingcheng45/ollama-llmwatch
- PyPI package metadata and download stats — https://pypi.org/pypi/ollama-llmwatch/json and https://pypistats.org/api/packages/ollama-llmwatch/recent
- Ollama prefill metrics analysis (prompt_eval_cached_count, cache ordering, 38x over-report) — https://lognebudo.github.io/llmxray/docs/en/articles/ollama-prefill-metrics.html
- Ollama API usage docs and types — https://github.com/ollama/ollama/blob/main/docs/api/usage.mdx and https://github.com/ollama/ollama/blob/main/api/types.go
- Ollama issue #3144 (no /metrics endpoint), PRs #16998 and #18508, PR #13901 (streaming prefill progress) — https://github.com/ollama/ollama/issues/3144
- toptop — https://github.com/ur-grue/toptop
- ollama-metrics — https://github.com/NorskHelsenett/ollama-metrics
- LLMxRay — https://github.com/LogneBudo/llmxray
- Ollama troubleshooting (log locations) — https://docs.ollama.com/troubleshooting
- agentacct (agent cost accounting dashboard) — https://github.com/mikehasa/agentacct
- tokentelemetry (agent token telemetry) — https://github.com/VasiHemanth/tokentelemetry
