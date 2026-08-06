---
title: "Clai Command Line AI: Stdin to LLM to Stdout — A Unix-Philosophy Review"
date: 2026-08-06T04:05:51+00:00
tags:
  - Clai
  - command line AI
  - LLM tools
  - terminal AI
  - open source
  - Go
description: "Clai is a minimalist Go CLI tool that pipes stdin through an LLM to stdout — no sessions, no REPL, no lock-in. Here is how it compares to llm, fabric, aichat, and mods."
draft: false
cover:
  image: "/images/clai-ai-command-line-stdin-llm.png"
  alt: "Clai Command Line AI: Stdin to LLM to Stdout — A Unix-Philosophy Review"
  relative: false
schema: "schema-clai-ai-command-line-stdin-llm"
---

## What Is Clai? — Stdin to LLM to Stdout

Clai is a command-line AI tool that reads text from standard input, sends it to a large language model, and writes the response to standard output. That is it. No interactive REPL, no session state, no chat history, no plugin ecosystem, no GUI. Written in Go and released as a single binary, Clai embodies the Unix philosophy: do one thing well and compose with other tools via pipes. At version 0.3.0 as of July 2026, it is an early-stage project with a clear philosophical stance that sets it apart from every other AI CLI tool on the market.

## Why Does the Unix Philosophy Matter for AI Tools?

Doug McIlroy, the inventor of Unix pipes, famously said: "Write programs that do one thing and do it well. Write programs to work together. Write programs to handle text streams, because that is a universal interface." Clai is the first AI CLI tool to take this principle literally. Every other tool in the space has drifted toward platforms — adding sessions, plugins, chat modes, RAG pipelines, and agent frameworks. Clai refuses all of that by design.

The practical consequence is composability. Because Clai reads stdin and writes stdout, it fits into any existing shell pipeline:

```bash
git diff --cached | clai "Write a concise commit message" | pbcopy
curl https://example.com/article | clai "Summarize in 3 bullet points"
cat server.log | grep ERROR | clai "Explain what went wrong"
```

No other AI CLI tool integrates this cleanly because none of them are pure stdin/stdout tools. They all introduce some form of state, formatting, or interactive mode that breaks the pipe contract.

### The Anti-Platform Bet

The AI industry is racing to build platforms that capture users inside ecosystems. Clai makes the opposite bet: the terminal is already the platform. By refusing to add session state, Clai ensures that no user workflow becomes dependent on Clai itself. You can replace Clai with any other stdin/stdout tool tomorrow without changing your pipelines. This is a radical idea in 2026, when most AI tools are designed to maximize switching costs.

## What Are the Key Features of Clai?

Despite its minimalist philosophy, Clai packs meaningful functionality into its small surface area.

### Built-in Prompt System

Clai ships with a collection of curated prompts stored as Markdown files. Users can invoke them by name:

```bash
cat code.py | clai --prompt explain-code
cat README.md | clai --prompt improve-writing
```

Prompts are plain Markdown files with a simple frontmatter format. The community can contribute prompts without a package manager — just open a pull request. This is the Unix way: prompts are text files, not plugins.

### Multi-Provider Support

Clai supports six LLM providers out of the box:

| Provider | Type | Notes |
|----------|------|-------|
| OpenAI | Cloud | GPT-4o, GPT-4o-mini |
| Anthropic | Cloud | Claude 3.5 Sonnet, Claude 3 Opus |
| Google Gemini | Cloud | Gemini 1.5 Pro, Gemini 1.5 Flash |
| Vertex AI | Cloud | Enterprise GCP deployment |
| AWS Bedrock | Cloud | Enterprise AWS deployment |
| Ollama | Local | Fully offline, no data leaves your machine |

Any OpenAI-compatible endpoint also works, which covers hundreds of self-hosted and proxy options. This provider flexibility means Clai can be the single interface to every LLM you use, whether local or cloud.

### Reasoning Strategies

Clai supports four reasoning strategies that control how the LLM processes input:

1. **Chain-of-Thought (CoT)** — The model reasons step by step before answering. Best for math, logic, and multi-step problems.
2. **Tree-of-Thought (ToT)** — The model explores multiple reasoning paths simultaneously. Better for open-ended creative tasks.
3. **Chain-of-Draft (CoD)** — The model produces concise intermediate reasoning. Faster and cheaper than full CoT.
4. **Self-Refine** — The model generates an answer, critiques it, and refines it. Best for writing and code review.

These strategies are applied via prompt engineering at the CLI level, not through model-specific APIs, which means they work across all supported providers.

### Structured Output

Clai can return structured data (JSON, YAML, CSV) by specifying an output format flag. This makes it usable in automated pipelines where the output feeds into another program:

```bash
cat changelog.md | clai --format json "Extract version numbers and dates"
```

The structured output mode is critical for Clai's pipeline-native design — it turns the LLM into a data transformation tool, not just a text generator.

## How Does Clai Compare to Alternatives?

The AI CLI tool landscape has several established players. Here is how Clai stacks up against the four main competitors.

### Feature Comparison Table

| Feature | Clai | llm (simonw) | fabric | aichat | mods (Charm) |
|---------|------|---------------|--------|--------|--------------|
| **Language** | Go | Python | Go | Rust | Go |
| **GitHub Stars** | ~3 | 12,316 | 43,329 | 10,329 | 4,531 |
| **Stdin/Stdout Only** | Yes | No | No | No | No |
| **Session/Chat Mode** | No | Yes | No | Yes | Yes |
| **Plugin System** | No | Yes | Yes (patterns) | Yes | No |
| **Local LLM Support** | Yes (Ollama) | Yes | Yes | Yes | Yes |
| **Reasoning Strategies** | 4 (CoT, ToT, CoD, Self-Refine) | No | No | No | No |
| **Structured Output** | Yes | Yes | Partial | Yes | No |
| **Pre-built Binaries** | Yes | Yes | Yes | Yes | Yes |
| **License** | MIT | Apache 2.0 | MIT | MIT | MIT |
| **Release Stage** | v0.3.0 (early) | v1.x (mature) | v1.x (mature) | v1.x (mature) | Deprecated |

### When to Choose Each Tool

**Choose Clai if** you want a pure pipeline tool that composes with grep, jq, curl, and git. You value the Unix philosophy and want zero lock-in. You are comfortable with an early-stage project (v0.3.0) and willing to watch it grow.

**Choose llm (simonw/llm) if** you want a mature Python tool with a rich plugin ecosystem. Simon Willison's llm has 12,316 GitHub stars, supports dozens of models through plugins, and has session/chat mode. It is the most popular general-purpose CLI LLM tool for good reason.

**Choose fabric (danielmiessler/fabric) if** you want a curated ecosystem of AI patterns and prompts. With 43,329 GitHub stars, fabric is the most starred AI CLI framework. Its pattern system is more opinionated and comprehensive than Clai's prompt collection, but it is also a heavier dependency.

**Choose aichat (sigoden/aichat) if** you want an all-in-one tool with RAG, function calling, and agent capabilities. Aichat supports 10+ LLM providers and has the richest feature set. It is the opposite of Clai's minimalism — which is exactly what some users want.

**Do not choose mods (charmbracelet/mods)** — it has been deprecated in favor of other Charm tools. Its 4,531 stars reflect past popularity, but the project is no longer maintained.

### The Minimalism Spectrum

```
Pure pipe tool ← Clai · llm · fabric · aichat → Full platform
```

Clai sits at the far left of this spectrum. Every other tool has drifted rightward by adding features that break the pipe contract. This is not inherently good or bad — it is a design trade-off. But it means Clai occupies a niche that no other actively maintained tool fills.

## How Do You Get Started with Clai?

Installation is straightforward. Clai provides pre-built binaries for macOS (both Intel and Apple Silicon) and Linux (both amd64 and arm64). You can also install via Homebrew tap or `go install`.

### Quick Install

```bash
# Homebrew
brew install maxrodrigo/tap/clai

# Go install
go install github.com/maxrodrigo/clai@latest

# Or download a binary from GitHub Releases
```

### Basic Configuration

Clai needs at least one LLM provider configured. The simplest path is Ollama for fully local operation:

```bash
# Set up Ollama provider
clai config set provider ollama
clai config set model llama3.1

# Or use OpenAI
clai config set provider openai
clai config set model gpt-4o-mini
clai config set openai-api-key sk-...
```

### Your First Pipeline

Once configured, Clai works in any shell pipeline:

```bash
# Summarize a web page
curl -s https://example.com/long-article | clai "Summarize this in 3 sentences"

# Explain an error
echo "TypeError: Cannot read properties of undefined (reading 'map')" | clai "Explain this error and suggest a fix"

# Translate text
echo "Bonjour le monde" | clai --prompt translate-to-english

# Extract structured data
ps aux | clai --format json "List the top 5 memory-consuming processes"
```

Each command reads from stdin, processes through the LLM, and writes to stdout. You can pipe the output into anything: `pbcopy`, `> file.md`, `| grep`, `| jq`, or another `clai` invocation.

## Who Is Clai For?

Clai is not for everyone. Its design makes deliberate trade-offs that serve specific users well.

### Ideal Clai Users

**Unix enthusiasts** who believe in the pipe philosophy and want AI tools that respect it. If you reach for `grep`, `awk`, and `jq` before opening a GUI, Clai will feel natural.

**Pipeline builders** who need AI as a composable step in automated workflows. CI/CD scripts, data processing pipelines, and code review automation benefit from a tool that never blocks on interactive input.

**Privacy-conscious developers** who run local models via Ollama. Clai's provider-agnostic design means you can use it entirely offline with no data leaving your machine.

**Terminal power users** who want a single AI interface across multiple providers. Clai's provider abstraction lets you switch between OpenAI, Anthropic, Gemini, and local models with a config change — no tool switching.

### Who Should Look Elsewhere

**Chat-oriented users** who want an interactive AI conversation in the terminal. Clai has no session mode. Use `aichat` or `llm` with its `chat` subcommand instead.

**Plugin seekers** who want to extend the tool with custom functionality. Clai has no plugin system. Prompts are the only extension point.

**Enterprise teams** who need a mature, battle-tested tool with a large community. Clai is v0.3.0 with approximately 3 GitHub stars. It is a promising project, not a production-grade platform.

## Verdict: Early but Promising

Clai is the most philosophically consistent AI CLI tool available in 2026. It is the only tool that fully commits to the Unix pipe model — stdin to LLM to stdout, nothing else. This purity is both its greatest strength and its most significant limitation.

### Strengths

- **True pipe composability** — works with any Unix tool in any pipeline
- **Zero lock-in** — no session state, no proprietary format, no switching costs
- **Multi-provider** — one interface for local and cloud LLMs
- **Reasoning strategies** — unique feature not found in any competitor
- **Structured output** — JSON, YAML, CSV for automated consumption
- **Single binary** — written in Go, no runtime dependencies

### Limitations

- **Very early stage** — v0.3.0 with minimal community adoption
- **No session/chat** — intentional, but limits use cases
- **No plugin system** — prompts only, no code extensions
- **Small community** — approximately 3 GitHub stars at launch
- **Limited documentation** — early-stage project documentation

### The Bottom Line

Clai is worth your attention if you value the Unix philosophy and want an AI tool that amplifies your existing workflow instead of replacing it. It is not ready to replace `llm` or `fabric` for most users today, but its design direction is the right one for a specific and underserved niche. Watch this project — if it gains community traction, it could become the `jq` of AI tools: small, focused, and indispensable.

## Frequently Asked Questions

### Is Clai free to use?

Yes, Clai is open source under the MIT License. The tool itself costs nothing. You pay only for the LLM API calls you make through your chosen provider, or nothing at all if you use a local model via Ollama.

### Does Clai work with local LLMs?

Yes. Clai supports Ollama out of the box, which lets you run models like Llama 3.1, Mistral, and Gemma entirely on your own machine. No data ever leaves your computer when using local models.

### How is Clai different from simonw/llm?

Clai is a pure stdin/stdout pipeline tool with no session state, no chat mode, and no plugin system. Simon Willison's llm has sessions, plugins, and a chat REPL. Clai is minimalist by design; llm is a platform. They serve different philosophies and different use cases.

### Can I use Clai in CI/CD pipelines?

Yes. Because Clai reads stdin and writes stdout with no interactive mode, it is ideal for automated pipelines. The structured output flag (--format json) makes it easy to parse results programmatically in scripts.

### What reasoning strategies does Clai support?

Clai supports four reasoning strategies: Chain-of-Thought (step-by-step reasoning), Tree-of-Thought (multiple parallel reasoning paths), Chain-of-Draft (concise intermediate reasoning), and Self-Refine (generate, critique, refine). These are applied via prompt engineering and work across all supported LLM providers.
