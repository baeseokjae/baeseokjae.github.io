---
title: "Kotlin Benchmark for AI Coding Agents: How Well Do AI Agents Write Kotlin Compared to Python and TypeScript?"
date: 2026-08-02T01:06:55+00:00
tags:
  - Kotlin
  - AI Coding Agents
  - Benchmark
  - JetBrains
  - Claude Code
  - Junie
  - Codex
  - SWE-bench
  - Android Development
description: "JetBrains' Kotlin Benchmark reveals Claude Code leads at 85.71% resolution on 105 real-world tasks. See how Kotlin compares to Python and TypeScript for AI code generation."
draft: false
cover:
  image: "/images/kotlin-benchmark-ai-coding-agents-2026.png"
  alt: "Kotlin Benchmark for AI Coding Agents: How Well Do AI Agents Write Kotlin Compared to Python and TypeScript?"
  relative: false
schema: "schema-kotlin-benchmark-ai-coding-agents-2026"
---

## Introduction — The Rise of Kotlin-Specific AI Coding Benchmarks

For years, AI coding benchmarks have been dominated by Python and TypeScript. SWE-bench, HumanEval, and MBPP all lean heavily on these languages, leaving Kotlin developers wondering how well AI agents actually handle JVM-based code, Android development, and Kotlin-specific idioms. In July 2026, JetBrains changed that by releasing the official **Kotlin Benchmark for AI Coding Agents** — a rigorous, open-source evaluation framework built on Multi-SWE-bench infrastructure that measures how well AI coding agents resolve real-world Kotlin software engineering tasks.

The benchmark answers a question that has become increasingly urgent as AI coding tools proliferate: **how well do AI agents write Kotlin compared to Python and TypeScript?** The results are revealing — and they have significant implications for Android developers, Kotlin Multiplatform teams, and anyone evaluating AI coding agents for JVM-based projects.

## What Is the Kotlin Benchmark? — 105 Tasks, 8 Repos, SWE-bench Methodology

The Kotlin Benchmark is not a toy dataset of synthetic coding problems. It follows the same methodology as SWE-bench and Multi-SWE-bench, using real-world tasks drawn from actual merged pull requests in open-source Kotlin repositories.

### Task Selection and Dataset

The benchmark contains **105 tasks sourced from 8 open-source Kotlin repositories**:

| Repository | Description |
|---|---|
| ktlint | Official Kotlin linter maintained by Pinterest |
| detekt | Static code analysis for Kotlin |
| okhttp | Square's HTTP client for JVM and Android |
| dataframe | Kotlin DataFrame library by JetBrains |
| ORT | OSS Review Toolkit for license compliance |
| TeXiFy-IDEA | LaTeX support plugin for IntelliJ IDEA |
| Gradle Shadow | Gradle plugin for fat JARs |
| Android apps | Real Android application repositories |

Each task is a real merged GitHub PR. The agent receives the issue description and must produce a patch that passes the same test suite as the original human-authored fix. This is not about generating standalone code snippets — it is about understanding an existing codebase, reading issue reports, and making surgical, correct changes.

### Evaluation Infrastructure

The benchmark runs inside Docker containers with a layered-cache strategy that speeds up repeated evaluations. The test harness is built on **Multi-SWE-bench**, which already supports Java, Go, TypeScript, Rust, and other languages. Adding Kotlin to this infrastructure means the benchmark can be extended and compared across languages using the same evaluation methodology.

Kotlin also has existing model-focused evaluation assets: **Kotlin_HumanEval** and **Kotlin_QA** for syntax and core concepts. The new benchmark goes far beyond these by testing full software engineering capability — not just code generation but debugging, codebase navigation, and patch correctness.

## Leaderboard Breakdown — Claude Code, Junie, Codex, and More

The Kotlin Benchmark leaderboard at kotlinlang.org/benchmark ranks **16+ agent+model configurations** by resolution rate. Here are the top results:

| Rank | Agent | Model | Resolution Rate | Tasks Resolved |
|---|---|---|---|---|
| 1 | Claude Code | Opus 4.7 xhigh | **85.71%** | 90/105 |
| 2 | Junie | Opus 4.7 max | **81.9%** | 86/105 |
| 3 | Codex | GPT 5.5 xhigh | **81.9%** | 86/105 |
| 4 | Claude Code | Opus 4.7 high | ~78% | ~82/105 |
| 5 | Claude Code | Sonnet 4.7 | ~74% | ~78/105 |
| ... | ... | ... | ... | ... |
| 16 | Gemini CLI | Gemini 3.1 Pro | Lowest | — |

**Claude Code dominates the top 5 positions** on the leaderboard, with its Opus 4.7 xhigh configuration achieving the highest resolution rate at 85.71%. Junie and Codex are tied for second place at 81.9%, both also using Opus 4.7-class models. The Gemini CLI configurations with Gemini 3.1 Pro and Gemini 3 Flash rank lowest, suggesting that agent architecture matters as much as the underlying model.

### Key Observations

- **Claude Code + Opus 4.7 xhigh** achieved 85.71% resolution rate (90/105 tasks) — the clear leader
- **Junie + Opus 4.7 max** and **Codex + GPT 5.5 xhigh** both achieved 81.9% — a statistical tie for second
- Claude Code's dominance across multiple model tiers (Opus 4.7 xhigh, high, and Sonnet 4.7) suggests its agent architecture is particularly effective for Kotlin tasks
- The gap between the top configuration (85.71%) and the bottom suggests significant room for improvement, especially for open-weight models

## How Kotlin Compares to Python and TypeScript in AI Coding Benchmarks

This is the central question for most developers evaluating AI coding agents. How does Kotlin performance stack up against the languages that dominate AI coding benchmarks?

### SWE-bench Context

The original SWE-bench (Python) and SWE-bench Lite have been the standard for AI coding agent evaluation. Multi-SWE-bench extended this to Java, Go, TypeScript, and Rust. The Kotlin Benchmark is the first language-specific extension that uses the same methodology but focuses on a single language's ecosystem.

| Language | Benchmark | Top Resolution Rate | Notes |
|---|---|---|---|
| Python | SWE-bench Verified | ~72% (Junie) | Most mature benchmark, largest dataset |
| TypeScript | SWE-bench TS | ~68% | Growing dataset, strong TypeScript tooling |
| Kotlin | Kotlin Benchmark | **85.71%** | Smaller dataset (105 tasks), but real PRs |
| Java | Multi-SWE-bench | ~65% | Larger but less curated |
| Go | Multi-SWE-bench | ~70% | Strong for systems-level tasks |

### Why Kotlin Scores Higher

The Kotlin Benchmark's 85.71% top resolution rate is notably higher than typical SWE-bench scores for Python and TypeScript. Several factors explain this:

1. **Dataset size**: 105 tasks is smaller than SWE-bench's 2,294 tasks. Smaller datasets tend to have higher resolution rates because they are more carefully curated and may contain fewer edge cases.

2. **Kotlin's modern syntax**: Kotlin's concise, expressive syntax with null safety, extension functions, and coroutines may be easier for AI models to generate correctly compared to Java's verbosity or Python's dynamic typing.

3. **Repository quality**: The 8 selected repositories are well-maintained, well-tested open-source projects with clear issue descriptions and comprehensive test suites.

4. **Model recency**: The top results use the latest models (Opus 4.7, GPT 5.5) that benefit from training data that may include Kotlin code from GitHub.

### The Language Gap

Despite Kotlin's strong showing, the language gap in AI coding benchmarks remains real. Python and TypeScript have orders of magnitude more training data in AI model training sets. Kotlin, while growing rapidly, still represents a smaller fraction of public code on GitHub. The Kotlin Benchmark's high resolution rate suggests that modern AI models generalize well to Kotlin despite less training data — a promising sign for less common languages.

## Junie Deep Dive — JetBrains' LLM-Agnostic Coding Agent

Junie is JetBrains' own AI coding agent, and its performance on the Kotlin Benchmark is particularly noteworthy. Tied for second place at 81.9% with Codex, Junie demonstrates that JetBrains has built a competitive coding agent for its own ecosystem.

### Junie's Evolution

Junie left beta in June 2026 and has been making waves in the AI coding agent space. It placed **#1 on SWE-Rebench with 61.6% resolved and 72.7% pass@5**, outperforming Claude Code and Codex on that benchmark. On the Kotlin Benchmark, it matches Codex but trails Claude Code by about 4 percentage points.

### Key Features

| Feature | Description |
|---|---|
| **LLM-agnostic** | Supports Anthropic, OpenAI, Google, and local runtimes (Ollama, LM Studio) |
| **Plan mode** | Generates a structured document before writing code, reducing wasted tokens |
| **Agentic debugging** | Uses the IDE debugger — breakpoints, stack frames, expression evaluation |
| **Remote control** | Async task execution with progress checking from anywhere |
| **Code review** | Full project context via GitHub Actions, GitLab, and CLI |

### Home-Field Advantage?

One natural question is whether Junie benefits from being developed by JetBrains, the creators of Kotlin. The evidence is mixed. Junie's 81.9% on the Kotlin Benchmark is strong, but Claude Code (not a JetBrains product) leads at 85.71%. This suggests that while Junie is well-optimized for the Kotlin ecosystem, agent architecture and model quality matter more than ecosystem integration.

However, Junie's LLM-agnostic design is a strategic advantage. Teams can swap underlying models as they improve, while Claude Code is tied to Anthropic's models. For organizations that want flexibility, Junie's approach may be more future-proof.

## Claude Code vs Codex vs Junie — Agent Architecture Comparison

The Kotlin Benchmark reveals that agent architecture is at least as important as the underlying model. Here is how the three top agents compare:

| Aspect | Claude Code | Codex | Junie |
|---|---|---|---|
| **Developer** | Anthropic | OpenAI (GitHub) | JetBrains |
| **Underlying Model** | Claude (Opus/Sonnet) | GPT-5.5 | LLM-agnostic |
| **Kotlin Benchmark** | 85.71% (best) | 81.9% | 81.9% |
| **SWE-Rebench** | ~58% | ~55% | 61.6% (best) |
| **IDE Integration** | CLI + VS Code | VS Code + CLI | IntelliJ + CLI |
| **Plan-then-code** | Yes | Yes | Yes (Plan mode) |
| **Debugger integration** | No | No | Yes |
| **Pricing** | Per-token API | Per-token API | Subscription + API |
| **Open source** | No | No | No |

### What Makes Claude Code Lead on Kotlin?

Claude Code's top position on the Kotlin Benchmark can be attributed to several factors:

1. **Strong code understanding**: Claude models have demonstrated exceptional code comprehension across languages, including Kotlin
2. **Effective tool use**: Claude Code's agent loop is optimized for software engineering tasks with file editing, shell commands, and test execution
3. **Opus 4.7 xhigh tier**: The highest compute tier provides more thorough reasoning at the cost of higher token usage

### Junie's Differentiator: Debugger Integration

Junie's ability to use the IntelliJ IDEA debugger — setting breakpoints, inspecting stack frames, and evaluating expressions — is a unique capability that no other top agent offers. This is particularly valuable for Kotlin development where understanding runtime behavior in the JVM is critical.

## Cost, Tokens, and Practicality — What the Numbers Don't Tell You

Resolution rate is only one dimension of agent performance. Cost and latency are equally important for practical use.

### Token Consumption

The Kotlin Benchmark tracks average token consumption per task. The top-performing configurations tend to use more tokens:

| Configuration | Resolution Rate | Avg Tokens (M) | Avg Latency |
|---|---|---|---|
| Claude Code + Opus 4.7 xhigh | 85.71% | ~8-10M | ~5-8 min |
| Claude Code + Opus 4.7 high | ~78% | ~5-7M | ~3-5 min |
| Claude Code + Sonnet 4.7 | ~74% | ~3-5M | ~2-4 min |
| Gemini CLI + Gemini 3.1 Pro | Lowest | ~2-3M | ~1-2 min |

The **cost vs. capability trade-off** is stark. The top configuration (Opus 4.7 xhigh) achieves the best results but at the highest token cost. For teams on a budget, Claude Code with Sonnet 4.7 may offer the best balance — 74% resolution at roughly half the token cost.

### Practical Recommendations

- **For critical production code**: Use Claude Code + Opus 4.7 xhigh for the highest accuracy
- **For everyday development**: Claude Code + Sonnet 4.7 or Junie + Opus 4.7 max offer strong results at lower cost
- **For cost-sensitive teams**: Consider Junie with a local model (Ollama/LM Studio) for offline tasks, reserving cloud models for complex work
- **For Android projects**: Junie's IntelliJ integration may offset its slightly lower benchmark score through better workflow integration

## Implications for Android and Kotlin Multiplatform Development

The Kotlin Benchmark includes Android application repositories, making it directly relevant to mobile developers. The results have several implications:

### Android Development

Android development has traditionally been slower to adopt AI coding tools compared to web development. The Kotlin Benchmark shows that AI agents are now capable of handling real Android tasks — fixing bugs, implementing features, and navigating Android-specific APIs.

For Android teams, this means:
- **Faster bug fixes**: AI agents can triage and fix common Android issues in minutes
- **Reduced boilerplate**: ViewModel setup, dependency injection, and navigation code can be generated reliably
- **Better test coverage**: Agents can write and fix unit tests for Android components

### Kotlin Multiplatform (KMP)

KMP adds complexity by targeting multiple platforms (Android, iOS, desktop, web) from a single Kotlin codebase. The benchmark's inclusion of diverse repository types suggests that AI agents can handle cross-platform Kotlin code, though dedicated KMP benchmarks would be valuable.

### The Android AI Gap

Despite the strong Kotlin results, Android development presents unique challenges for AI agents:
- **Android SDK complexity**: The Android API surface is vast and changes rapidly
- **Gradle build system**: Build configuration issues are a common source of errors
- **Device fragmentation**: Testing on real devices vs. emulators adds complexity
- **XML layouts**: Many Android projects still use XML for UI, which AI agents handle less well than Compose

## Future Directions — More Metrics, More Models, More Languages

The Kotlin Benchmark is version 1.0, and JetBrains has outlined several areas for expansion:

### Planned Improvements

1. **Android/KMP coverage**: Dedicated Android and Kotlin Multiplatform tasks
2. **Cost/quality/performance metrics**: Beyond resolution rate to include token efficiency, execution time, and solution quality
3. **More open-weight models**: Evaluation of Llama, Mistral, Qwen, and other open models on Kotlin tasks
4. **Language comparison framework**: Direct comparison of agent performance across Python, TypeScript, Java, and Kotlin using the same methodology

### What Developers Should Watch

- **Open-weight model progress**: If open models can reach 70%+ on the Kotlin Benchmark, it would democratize AI-assisted Kotlin development
- **Android-specific benchmarks**: A dedicated Android benchmark would be more useful for mobile teams
- **Real-time leaderboard updates**: The leaderboard at kotlinlang.org/benchmark is updated as new agent configurations are evaluated

## Conclusion — What the Kotlin Benchmark Means for Developers

The Kotlin Benchmark for AI Coding Agents is a significant milestone for the Kotlin ecosystem. It provides the first rigorous, standardized way to evaluate how well AI agents handle real-world Kotlin software engineering tasks — and the results are impressive.

**Claude Code with Opus 4.7 xhigh leads at 85.71%**, with Junie and Codex close behind at 81.9%. These numbers suggest that modern AI coding agents are highly capable at Kotlin development, potentially even more so than for Python and TypeScript on a per-task basis. The benchmark validates that Kotlin's modern syntax and strong typing work well with AI code generation.

For developers and teams evaluating AI coding agents for Kotlin projects, the key takeaways are:

1. **Claude Code is the current leader** for Kotlin tasks, especially with Opus-class models
2. **Junie offers unique advantages** for IntelliJ users, including debugger integration and LLM flexibility
3. **Cost matters**: The top configuration is expensive — consider Sonnet-tier models for everyday work
4. **The gap is closing**: Junie and Codex are within 4 percentage points of the leader, and competition is driving rapid improvement
5. **Kotlin is well-served by AI**: Despite less training data than Python or TypeScript, AI agents perform strongly on Kotlin tasks

The Kotlin Benchmark is not just a leaderboard — it is a tool that will drive improvement in AI coding agents for the JVM ecosystem. As more models are evaluated and the benchmark expands to cover Android and KMP, it will become an essential resource for any team using AI in Kotlin development.

## FAQ

### What is the Kotlin Benchmark for AI Coding Agents?

The Kotlin Benchmark is an open-source evaluation framework released by JetBrains in July 2026 that measures how well AI coding agents resolve real-world Kotlin software engineering tasks. It contains 105 tasks from 8 open-source Kotlin repositories and is built on Multi-SWE-bench infrastructure. Each task requires the agent to produce a correct patch for a real merged GitHub PR.

### Which AI coding agent performs best on Kotlin tasks?

Claude Code with Opus 4.7 xhigh leads the Kotlin Benchmark with an 85.71% resolution rate (90/105 tasks). Junie with Opus 4.7 max and Codex with GPT 5.5 xhigh are tied for second at 81.9%. Claude Code dominates the top 5 positions on the leaderboard.

### How does Kotlin compare to Python and TypeScript for AI code generation?

On the Kotlin Benchmark, the top resolution rate of 85.71% is higher than typical SWE-bench scores for Python (~72%) and TypeScript (~68%). However, the Kotlin dataset is smaller (105 tasks vs. thousands), which partially explains the higher scores. Modern AI models generalize well to Kotlin despite less training data compared to Python and TypeScript.

### Is Junie better than Claude Code for Kotlin development?

It depends on your priorities. Claude Code achieves a higher resolution rate on the Kotlin Benchmark (85.71% vs. 81.9%). However, Junie offers unique advantages for IntelliJ IDEA users, including debugger integration, LLM-agnostic model support, and plan mode. Junie also leads SWE-Rebench (61.6% vs. ~58% for Claude Code), showing strength on a different benchmark.

### Can AI coding agents handle Android development tasks?

Yes. The Kotlin Benchmark includes Android application repositories, and top agents achieve strong results on these tasks. However, Android development presents unique challenges including SDK complexity, Gradle build configuration, and device fragmentation. Dedicated Android benchmarks would provide more specific guidance for mobile teams.
