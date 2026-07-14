---
title: "AI Coding Agent Dependency Bias: Why Your Assistant Plays Favorites"
date: 2026-07-14T12:00:00+00:00
tags: ["AI coding agents", "LLM training data bias", "dependency management", "Cursor", "Claude Code", "GitHub Copilot", "RAG for coding"]
description: "AI coding agents favor popular dependencies like React and Docker over niche alternatives. Here's why it happens and how to work around it."
draft: false
cover:
  image: "/images/coding-agents-play-favorites-dependencies.png"
  alt: "AI Coding Agent Dependency Bias"
  relative: false
schema: "schema-coding-agents-play-favorites-dependencies"
---

## Your AI Coding Assistant Has a Hidden Bias — and It's Reshaping the Software Ecosystem

I've been running AI coding agents daily for over a year now — Claude Code, Cursor, GitHub Copilot — and I've noticed something unsettling. When I ask them to generate a React component, the output is near-perfect on the first try. When I ask for the same thing in SvelteKit or Solid, I get hallucinated APIs, wrong imports, and code that looks like someone read a blog post from 2023 and guessed the rest.

This isn't random. Your AI coding assistant plays favorites with your dependencies, and the bias runs deep in the training data. If you're building on a niche stack, you're fighting an uphill battle that most developers don't even realize exists.

## Why AI Coding Agents Play Favorites: The Training Data Problem

The root cause is straightforward: LLMs are trained on what's available, not what's good.

GitHub hosts over 200 million repositories, but the distribution is anything but even. Python, JavaScript, and Java dominate. React has the largest open-source ecosystem on the platform by a wide margin. Dockerfiles and docker-compose.yml files are everywhere. Stack Overflow threads, blog posts, tutorials, and documentation — all of these training sources skew heavily toward the most popular tools.

When a model like Claude 4 Sonnet or GPT-4o was trained, it saw React examples tens of thousands of times more often than Solid or Svelte examples. The model didn't learn "how to write a frontend component" — it learned "how to write a React component" and generalized poorly from there.

### GitHub, Stack Overflow, and the Popularity Feedback Loop

Here's the cycle I've observed playing out in real time:

1. A framework gets popular → more GitHub repos, Stack Overflow questions, blog posts
2. LLM training crawls collect more data on that framework → the model generates it more accurately
3. Developers using AI tools get better results with the popular framework → they recommend it, use it more
4. The popular framework gets even more popular → step 1 repeats

This is the same feedback loop that drives search engine rankings and YouTube recommendations, but applied to code generation. The consequence is that your choice of dependencies directly determines how effective your AI coding tools will be.

### The Matthew Effect in AI-Assisted Development

Sociologists call this the Matthew Effect — "the rich get richer and the poor get poorer." In AI-assisted development, it means popular dependencies get better AI support, which makes them even more popular, which entrenches them further.

I've watched this happen with Docker vs Podman. Docker commands come out perfectly from every AI tool I've tested. Podman-specific features like rootless mode or `podman pod create`? The AI either ignores them entirely or generates Docker syntax that doesn't work. The developer then has to manually fix every output, which defeats the purpose of using an AI assistant in the first place.

## Real-World Examples of AI Dependency Bias

Let me give you specific cases I've encountered or verified through testing.

### Frontend Frameworks — React's Reign vs Svelte's Struggle

I asked Claude Code, Cursor's Composer, and GitHub Copilot Agent to generate the same component — a data table with sorting, filtering, and pagination — in three frameworks.

**React (with TanStack Table):** All three tools produced working code on the first attempt. The imports were correct, the hook usage matched the current API, and the TypeScript types were accurate.

**Svelte 5 (with runes):** Claude Code generated `$:` reactive declarations that were deprecated in Svelte 5. Cursor produced a mix of Svelte 4 and Svelte 5 syntax. Copilot Agent hallucinated a `svelte-table` package that doesn't exist.

**SolidJS:** All three tools struggled. Claude Code generated JSX that used `createEffect` where `createMemo` was appropriate. Cursor produced code that mixed Solid's signal syntax with React's `useState` patterns.

The difference isn't that React is easier to generate — it's that the training data contains orders of magnitude more React examples.

### Container Orchestration — Docker's Dominance vs Podman's Predicament

I maintain a CI pipeline that uses Podman for rootless container builds. Every time I ask an AI agent to help with it, I get Docker commands back.

Here's what happened when I asked Claude Code to "create a rootless Podman container with a bind mount":

```bash
# What Claude Code generated:
docker run -v /host/path:/container/path myimage

# What actually works with Podman rootless:
podman run --userns=keep-id -v /host/path:/container/path:Z myimage
```

The `--userns=keep-id` flag and the `:Z` SELinux label are Podman-specific. The AI simply doesn't know them because Podman examples are sparse in the training data compared to Docker's millions of Dockerfiles and Compose files.

### Backend Languages — Python and JavaScript Get All the Love

This extends beyond frameworks into languages themselves. I work with a Go codebase that uses `pgx` (PostgreSQL driver) and `sqlc` for query generation. When I ask AI agents to write database access code, they default to `database/sql` with raw queries — the most common pattern in Go training data — even when my project clearly uses `pgx` and `sqlc`.

The same happens with Rust. Ask for async HTTP server code and you'll get `actix-web` or `tokio` examples even when your project uses `axum`. The AI defaults to the most-represented option in its training distribution.

## The Agentic Workflow Chasm: When Bias Derails Autonomy

The bias problem gets worse when you move from autocomplete to autonomous agents.

With Copilot-style completions, you see the suggestion, accept or reject it, and move on. The cost of bias is a wrong suggestion that you ignore. Annoying, but manageable.

With agentic workflows — where Claude Code or Cursor's Agent mode plans and executes multi-step tasks — the bias compounds. The agent picks a popular library, writes code around it, hits an API that doesn't exist, tries to fix it by importing something else that also doesn't exist, and spirals into a loop of hallucinated fixes.

I've watched Claude Code spend 45 seconds generating a plan, then 3 minutes executing it, only to produce code that doesn't compile because it used a library API that was deprecated two versions ago. The time cost isn't just the generation — it's the debugging, the context switching, and the frustration.

### Why Enterprise AI Agent Adoption Is Stuck at 11%

Industry data shows enterprise full deployment of AI agents has been stagnant at around 11% for the past year. I think this dependency bias is a major, under-discussed reason.

Enterprise codebases are not greenfield React apps. They're a decade of accumulated decisions: proprietary frameworks, internal libraries, custom ORMs, legacy middleware, and niche infrastructure tools. When an AI agent can't handle any of these, it becomes a net negative — generating code that doesn't fit the architecture, suggesting dependencies that conflict with internal standards, and requiring more human review time than it saves.

The 11% who have succeeded are either (a) working on modern, mainstream stacks or (b) investing heavily in custom context injection to bridge the gap. Everyone else is stuck in pilot purgatory.

### Hallucinated APIs, Boilerplate, and Endless Loops

The practical symptom of dependency bias in agentic mode is the hallucination cascade. Here's the pattern I've seen repeat:

1. Agent reads your codebase, sees you use a niche library
2. Agent decides to "help" by adding a popular alternative instead
3. Agent generates code using the popular library's API
4. The code doesn't compile because the popular library isn't in your dependencies
5. Agent adds the dependency, but now there are conflicts
6. Agent tries to resolve conflicts by modifying your existing code
7. Everything breaks

I've had to `git stash` more times than I'd like to admit after letting an AI agent "fix" something in a codebase with non-standard dependencies.

## What This Means for Your Dependencies

If you're evaluating dependencies for a new project, the AI bias should be on your list of considerations alongside performance, ecosystem, and team expertise.

### The 'Dark Matter' of Undersupported Codebases

There's a growing class of codebases I call "dark matter" — projects built on frameworks and libraries that AI tools can't effectively help with. These codebases become increasingly expensive to maintain because:

- New developers can't use AI to ramp up on them
- Refactoring requires manual work that AI can't assist with
- Documentation generation produces inaccurate results
- Bug fixing becomes a solo effort

If your company has a proprietary framework or a niche stack, you're accumulating technical debt that compounds with every AI tool release. The gap between what AI can do for mainstream stacks and what it can do for yours will only widen.

### The Hidden Cost of Choosing a Niche Stack

I'm not saying you should abandon Svelte for React or Podman for Docker. But you should be honest about the cost. Every time you choose a less-popular dependency, you're accepting that your AI tools will be less effective.

For a solo developer or a small team, this can be a significant productivity hit. For a large team, it means every developer spends more time manually verifying AI output, which erodes the ROI of your AI tooling investment.

### Security Implications of AI-Preferred Dependencies

There's a subtler risk here. If AI agents consistently suggest React, Express, and Docker — the most popular options — they're also suggesting the most-attacked surfaces. Popular frameworks have more CVEs, more exploit code in the wild, and more attention from attackers.

An AI that defaults to `express` for every Node.js backend is steering you toward a framework with a well-documented history of middleware vulnerabilities. Sometimes the niche alternative is actually more secure — but the AI won't suggest it.

## How to Fight Back: Mitigation Strategies

The bias is baked into the models, but you can work around it. Here's what I've found effective.

### RAG — Injecting Context at Runtime

Retrieval-Augmented Generation is the most practical mitigation today. Instead of relying on the model's training data, you feed it relevant documentation at query time.

I use a local RAG pipeline that indexes my project's dependencies' official docs. When I ask Claude Code or Cursor a question, the relevant docs are injected into the context. This dramatically reduces hallucinations for niche frameworks.

Tools like `context` (the CLI for MCP-based RAG) and `docs-crawler` can build these indexes automatically. Point them at your dependency's documentation site, and you get a searchable knowledge base that the AI can query.

### Custom Rules and Documentation (Cursor, Claude Code, Copilot)

Every major AI coding tool now supports some form of project-level instructions:

- **Cursor:** `.cursor/rules/` directory with `.mdc` files
- **Claude Code:** `CLAUDE.md` at the project root
- **GitHub Copilot:** `.github/copilot-instructions.md`

I wrote a detailed guide on [Cursor rules and .mdc files](/posts/cursor-rules-guide-2026/) that covers the syntax and activation modes. The key insight is that you should document your non-standard dependencies explicitly:

```markdown
# CLAUDE.md — Project Rules

## Database Layer
- We use `pgx` v5.x for PostgreSQL, NOT `database/sql`
- Query generation uses `sqlc` — do not write raw SQL strings
- Migrations use `golang-migrate`, not `prisma` or `gorm`

## Containerization
- All containers use Podman (rootless mode)
- Use `podman build` not `docker build`
- SELinux labels (`:Z`, `:z`) are required for bind mounts
```

This isn't perfect — the model can still fall back to its training biases — but it dramatically reduces the error rate. I covered the differences between these formats in my [.cursorrules vs CLAUDE.md vs AGENTS.md comparison](/posts/cursorrules-vs-claude-md-vs-agents-md-2026/).

### Fine-Tuning and Domain-Specific Models (For the Deep Pockets)

If you're in an enterprise with a proprietary stack, fine-tuning is the nuclear option. Train a model on your internal codebase, your dependency documentation, and your coding patterns. The result is an AI that actually understands your stack.

This is expensive — you need the data, the compute, and the MLOps pipeline to maintain it. But for organizations with large, unique codebases, it's the only way to get reliable AI assistance.

## Demanding a More Equitable AI Ecosystem

The dependency bias in AI coding tools isn't malicious — it's a statistical inevitability given how these models are trained. But it has real consequences for the software ecosystem. It entrenches incumbents, penalizes innovation, and creates a growing class of "dark matter" codebases that become increasingly expensive to maintain.

As developers, we should push for:

- **Better representation in training data** — model providers should actively curate diverse framework examples, not just scrape what's popular
- **Transparent bias reporting** — tools should tell you which frameworks they're confident about and which they're guessing on
- **First-class custom context support** — every AI coding tool should make it easy to inject project-specific knowledge

In the meantime, document your non-standard dependencies in your project rules, set up a RAG pipeline for your niche frameworks, and never trust an AI agent that reaches for `docker` when your project clearly uses `podman`.

## FAQ

### Why do AI coding agents perform better with popular frameworks?

AI coding agents are powered by LLMs trained on web-scale datasets. Popular frameworks like React, Docker, and Express have millions of examples in GitHub repositories, Stack Overflow threads, and technical documentation. The model sees these patterns thousands of times more often than niche alternatives, so it generates them more accurately.

### Can I fix AI dependency bias with better prompts?

Partially. Detailed prompts that specify your exact dependency versions and APIs help, but the underlying model still defaults to its training distribution. Project-level rules files (CLAUDE.md, .cursor/rules/) are more effective because they're applied consistently across all interactions.

### Does this bias affect all AI coding tools equally?

No. Tools with stronger context injection — like Claude Code with CLAUDE.md and Cursor with .cursor/rules — handle niche dependencies better than tools that rely primarily on training data. The gap is narrowing as tools improve their context handling, but the bias is still present in the underlying models.

### Is it safe to let AI agents choose dependencies for my project?

Not without supervision. AI agents tend to default to the most popular option, which may not fit your project's architecture, licensing requirements, or security posture. Always review dependency suggestions, especially for security-critical components.

### Will AI dependency bias get better or worse over time?

It depends on the model providers. If they continue training primarily on web-crawled data, the bias will worsen as popular frameworks generate even more content. If they invest in curated, diverse training datasets and better context injection, the gap can narrow. The trend in 2026 is toward better custom context support, which is the most practical path forward.
