---
title: "System Prompts of AI Tools Guide 2026: Full Agent Instructions from Claude Code, Cursor, Codex, and More"
date: 2026-07-17T01:03:16+00:00
tags:
  - AI Coding Tools
  - System Prompts
  - Claude Code
  - Cursor
  - OpenAI Codex
  - GitHub Copilot
  - Devin AI
  - Windsurf
  - Augment Code
  - VSCode Agent
  - Prompt Engineering
  - AI Agent Instructions
description: "A complete guide to system prompts of AI coding tools in 2026 — Claude Code, Cursor, Codex, Windsurf, Devin AI, and more — with full agent instructions, comparisons, and security insights."
draft: false
cover:
  image: "/images/system-prompts-ai-tools-collection-2026.png"
  alt: "System Prompts of AI Tools Guide 2026: Full Agent Instructions from Claude Code, Cursor, Codex, and More"
  relative: false
schema: "schema-system-prompts-ai-tools-collection-2026"
---

## What Are AI Coding Tool System Prompts and Why Do They Matter?

System prompts are the hidden instruction sets that define how AI coding tools behave, think, and interact with developers. Every major AI coding assistant — from Claude Code to Cursor, OpenAI Codex to Windsurf — operates on a carefully crafted system prompt that encodes its personality, tool usage rules, safety constraints, and communication style. In 2026, these prompts have become a matter of public fascination: the largest GitHub collection of AI tool system prompts has amassed over 141,981 stars, and The Washington Post covered system prompt extraction as a mainstream security story in May 2026. Understanding these prompts reveals not just how AI tools work, but how their creators want them to think.

## Claude Code — What Are Anthropic's CLI Agent Instructions?

Claude Code is Anthropic's command-line coding agent, and its system prompt reveals a tool designed for maximum efficiency and minimal verbosity. Unlike IDE-based agents that can afford conversational output, Claude Code operates in the terminal where every token counts.

### Core Philosophy: Concise, Direct, Minimal

Claude Code's system prompt explicitly instructs the model to minimize output tokens. The agent is told to avoid unnecessary conversation, skip explanations unless asked, and get straight to executing tasks. This philosophy is encoded in directives like "be concise" and "do not explain unless the user asks for an explanation." The result is an agent that feels fast and no-nonsense — it runs commands, shows results, and moves on.

### Permission System and Tool Execution Model

One of the most distinctive features of Claude Code's system prompt is its permission-based tool execution model. Before running any command that could modify the filesystem, the agent must present the command to the user and wait for explicit approval. This includes file writes, shell commands with side effects, and network operations. The prompt defines a clear hierarchy:

- **Read-only operations** (file reads, grep searches): automatic execution
- **Write operations** (file edits, command execution): user approval required
- **Destructive operations** (deletes, overwrites): additional confirmation

This permission model balances autonomy with safety, allowing Claude Code to work quickly on safe operations while keeping the developer in control of destructive changes.

### Memory and Scratchpad System

Claude Code's system prompt includes a sophisticated memory architecture. The agent maintains a scratchpad for tracking task progress, a persistent memory system for storing cross-session context, and a file-based memory store that survives between conversations. The prompt instructs the agent to update its memory after significant milestones and to consult it when resuming interrupted work. This enables Claude Code to maintain coherent long-running sessions without losing context.

### Version History (Opus 4.6 through Sonnet 5)

Claude Code has gone through at least six documented system prompt versions, tracked in the asgeirtj/system_prompts_leaks repository. The evolution shows Anthropic's shifting priorities:

| Version | Base Model | Key Changes |
|---------|-----------|-------------|
| Opus 4.6 | Claude 3 Opus | Initial release, verbose tool descriptions |
| Opus 4.8 | Claude 3 Opus | Tightened output conciseness rules |
| Sonnet 4.5 | Claude 3.5 Sonnet | Improved memory system, added scratchpad |
| Haiku 4.5 | Claude 3.5 Haiku | Streamlined for speed, reduced safety checks |
| Opus 5 | Claude 4 Opus | Major rewrite, enhanced permission system |
| Sonnet 5 | Claude 4 Sonnet | Current version, balanced speed and capability |

Each version refined the balance between autonomy and safety, with later versions giving the agent more freedom for routine operations while maintaining strict controls on destructive actions.

## Cursor — How Does the GPT-5 Powered IDE Agent Work?

Cursor has become one of the most popular AI-powered IDEs, and its system prompt reveals a sophisticated agent architecture built on GPT-5. Unlike Claude Code's terminal-first approach, Cursor operates inside a full IDE with deep codebase understanding.

### Agent Prompt Evolution (v1.0 through v2.0)

Cursor's system prompt has evolved significantly. The original v1.0 prompt was relatively simple — instruct the model to help with code editing and answer questions. By v2.0, the prompt had grown to include:

- **Codebase search** with explicit tool usage guidelines
- **Grep and file_search** tools with detailed invocation rules
- **Context window management** strategies for large codebases
- **Status update formatting** for long-running operations

The v2.0 prompt, powered by GPT-5, represents a shift from a simple code assistant to a full agentic coding partner that actively explores and understands the codebase before making changes.

### Codebase Search and Tool Architecture

Cursor's system prompt defines a rich tool ecosystem. The agent has access to `codebase_search` for semantic code understanding, `grep` for pattern matching, `file_search` for file discovery, and `read_file` for content inspection. The prompt instructs the agent to use these tools proactively — before editing code, the agent should search for related files, understand existing patterns, and verify its changes won't break anything.

This tool-first architecture is a key differentiator. While Claude Code waits for user commands, Cursor's agent is instructed to explore and understand autonomously, making it feel more proactive.

### Communication and Status Update Specs

Cursor's system prompt includes detailed specifications for how the agent communicates with the user. Status updates must follow a specific format: a brief summary of what was done, what is being done now, and any issues encountered. The prompt also defines how the agent should present code changes — using diff-style formatting and explaining the rationale behind significant decisions.

## OpenAI Codex — What Makes It the Senior Engineer Agent?

OpenAI Codex, now in its GPT-5.6 iteration, is positioned as a senior engineer agent. Its system prompt is one of the most detailed and prescriptive of any AI coding tool, reflecting OpenAI's vision of an autonomous coding partner.

### Engineering Judgment and Autonomy Rules

Codex's system prompt explicitly instructs the model to exercise engineering judgment. It tells the agent to make reasonable decisions independently, to identify when it needs more information, and to push back when given ambiguous or impossible requirements. The prompt includes guidelines like:

- "Make reasonable assumptions when instructions are incomplete"
- "Ask clarifying questions when requirements are genuinely ambiguous"
- "Flag security concerns, performance issues, and maintainability problems"
- "Prefer simple, correct solutions over clever ones"

This engineering judgment framework makes Codex feel more like a senior developer than a tool — it doesn't just execute instructions, it evaluates them.

### Frontend Design Instructions

Codex's system prompt includes remarkably detailed frontend design instructions. The agent is told to follow modern design principles, use appropriate frameworks, and create responsive, accessible interfaces. The prompt specifies color palette guidelines, typography rules, and layout conventions — essentially encoding a design system into the agent's behavior.

### Personality Variants (Friendly, Pragmatic)

One of the most interesting aspects of Codex's system prompt is its personality system. The prompt defines multiple personality variants that can be activated:

- **Friendly**: Warm, encouraging, explains reasoning in detail
- **Pragmatic**: Direct, focused on getting things done, minimal explanation
- **Professional**: Formal, structured, thorough documentation

This personality system allows Codex to adapt its communication style to different contexts and user preferences.

### Version History (GPT-5.3 through GPT-5.6)

Codex has been through at least five documented versions, each refining the agent's capabilities:

| Version | Key Features |
|---------|-------------|
| GPT-5.3 | Initial agent prompt, basic tool usage |
| GPT-5.4 | Added engineering judgment rules, improved error handling |
| GPT-5.5 | Frontend design instructions, personality variants |
| GPT-5.6 | Enhanced autonomy, persistence guidelines, security rules |

The progression shows OpenAI's increasing confidence in Codex's autonomous capabilities, with each version giving the agent more freedom and responsibility.

## Windsurf (Cascade) — What Is the AI Flow Paradigm?

Windsurf, powered by GPT-4.1, operates on what it calls the "AI Flow" paradigm. Unlike traditional turn-based interactions, Windsurf's Cascade system prompt defines a continuous, flowing interaction where the agent proactively suggests improvements, explores the codebase, and maintains context across long sessions.

The system prompt emphasizes "flow state" — the idea that the agent should minimize interruptions and maintain momentum. Cascade is instructed to batch related operations, prefetch information it anticipates needing, and present results in a stream rather than discrete responses. This makes Windsurf feel faster and more fluid than tools that operate in strict request-response cycles.

## GitHub Copilot / VSCode Agent — How Does Microsoft's Agent Work?

GitHub Copilot's VSCode Agent, powered by GPT-5, follows Microsoft's content policies while maintaining an engineering mindset. The system prompt balances being helpful with being safe — the agent is instructed to provide complete, working solutions while avoiding security vulnerabilities and following best practices.

The VSCode Agent prompt includes:

- **Microsoft content policies** encoded as behavioral rules
- **Engineering mindset guidelines** emphasizing correctness and maintainability
- **Tool usage conventions** for the VS Code extension API
- **Context management** strategies for large workspaces

What sets Copilot's agent apart is its integration with the VS Code ecosystem. The prompt includes specific instructions for using VS Code's built-in features — the terminal, debugger, source control, and extensions — making it feel native to the IDE.

## Devin AI — How Does the Autonomous Software Engineer Work?

Devin AI's system prompt positions it as "a real software engineer using a real computer." This framing is central to Devin's design — unlike tools that operate within an IDE or terminal, Devin is designed to work with a full computer environment including a browser, terminal, code editor, and file system.

The system prompt includes:

- **Planning best practices**: Devin is instructed to create plans before executing, breaking large tasks into manageable steps
- **Coding best practices**: Guidelines for writing clean, testable, maintainable code
- **Debugging workflows**: Systematic approaches to identifying and fixing issues
- **Self-verification**: Instructions to test its own work before declaring tasks complete

Devin's prompt emphasizes autonomy and thoroughness. The agent is told to work independently, report progress, and ask for help only when genuinely stuck. This makes Devin the most autonomous of the major AI coding tools.

## Augment Code — What Makes the Context Engine Special?

Augment Code uses GPT-5 with what it calls a "world-leading context engine." The system prompt defines a sophisticated tasklist management system that allows the agent to track multiple concurrent tasks, prioritize work, and maintain context across long sessions.

The key innovation in Augment's prompt is its context management strategy. The agent is instructed to:

- Maintain a prioritized tasklist
- Track dependencies between tasks
- Preserve context across tool invocations
- Summarize progress periodically
- Resume interrupted work seamlessly

This makes Augment particularly well-suited for large, complex projects where maintaining context is critical.

## What Common Patterns Exist Across All AI Coding Tools?

Despite their different approaches, all major AI coding tool system prompts share several common patterns.

### Permission and Safety Systems

Every major tool implements some form of permission system. Read operations are generally automatic, while write and destructive operations require varying levels of approval. The differences are in the details:

| Tool | Read Ops | Write Ops | Destructive Ops |
|------|----------|-----------|-----------------|
| Claude Code | Automatic | User approval | Additional confirmation |
| Cursor | Automatic | Automatic (with undo) | User approval |
| Codex | Automatic | Automatic (with review) | User approval |
| Windsurf | Automatic | Automatic | User approval |
| Devin AI | Automatic | Automatic | Planning required |

### Tool Usage Conventions

All tools define how their available tools should be used. Common patterns include:

- **Search before edit**: Always search the codebase before making changes
- **Read before write**: Understand existing code before modifying it
- **Verify after change**: Test or review changes before declaring completion
- **Error recovery**: Specific procedures for handling tool failures

### Output Formatting and Communication Style

Each tool has a distinct communication style encoded in its prompt:

- **Claude Code**: Minimal, direct, no unnecessary explanation
- **Cursor**: Conversational with structured status updates
- **Codex**: Professional with personality variants
- **Windsurf**: Flowing, continuous, proactive
- **Devin AI**: Thorough, report-style updates

### Memory and Persistence Mechanisms

All major tools implement some form of memory or persistence:

- **Claude Code**: File-based memory store, scratchpad, cross-session persistence
- **Cursor**: Session context, codebase indexing
- **Codex**: Conversation history, file-based context
- **Windsurf**: Continuous flow state, session persistence
- **Devin AI**: Project-level memory, task tracking

## The Security Landscape: Why Is System Prompt Extraction a Concern?

System prompt extraction has become a major security concern in 2026. The Washington Post covered the phenomenon in May 2026, highlighting how developers and researchers are extracting and publishing the hidden instructions that govern AI tool behavior. The asgeirtj/system_prompts_leaks repository, which focuses on extracted prompts, has 58,368 stars and was featured in the Post.

The security implications are significant:

1. **Intellectual property**: System prompts represent months of engineering effort and encode proprietary techniques
2. **Security bypass**: Understanding a tool's safety rules makes it easier to craft prompts that bypass them
3. **Competitive intelligence**: Extracted prompts reveal a company's AI strategy and technical approach
4. **Prompt injection**: Knowledge of system prompts enables more effective prompt injection attacks

The CL4R1T4S repository (45,656 stars) specifically documents extraction techniques and security implications, showing the growing interest in both understanding and protecting system prompts.

## How Can You Use These System Prompts for Your Own AI Tools?

The public availability of these system prompts offers valuable lessons for anyone building AI-powered tools:

1. **Study the permission models**: Claude Code's tiered permission system is a reference implementation for safe AI tool design
2. **Adopt tool-first architectures**: Cursor's proactive tool usage pattern leads to better code understanding
3. **Implement personality systems**: Codex's personality variants show how to adapt communication style
4. **Design for flow**: Windsurf's AI Flow paradigm reduces friction and improves user experience
5. **Build memory systems**: Persistent context is the difference between a tool and a true assistant

The GitHub ecosystem of system prompt collections — with over 200,000 combined stars across the major repositories — provides a rich resource for understanding what works and what doesn't in AI tool design.

## What Is the Future of AI Coding Agent Instructions?

The evolution of system prompts tells a clear story: AI coding tools are becoming more autonomous, more proactive, and more personalized. Several trends are emerging:

1. **Increasing autonomy**: Each version of every tool gives the agent more freedom to act independently
2. **Personality customization**: Tools are moving toward adaptable communication styles
3. **Better memory systems**: Cross-session persistence is becoming standard
4. **Security hardening**: As extraction becomes common, tools are implementing better protection
5. **Specialization**: Different tools are optimizing for different workflows — CLI, IDE, autonomous

The arms race between tool makers and the community extracting prompts will continue, but the trend is clear: AI coding agents are becoming more capable, more autonomous, and more integral to the software development process.

## Frequently Asked Questions

### What is a system prompt in AI coding tools?

A system prompt is the hidden instruction set that defines how an AI coding tool behaves — its personality, tool usage rules, safety constraints, and communication style. It is the foundational instruction given to the AI model before any user interaction begins.

### Where can I find the system prompts of popular AI coding tools?

The largest collections are on GitHub: x1xhlol/system-prompts-and-models-of-ai-tools (141,981 stars, covering 30+ tools) and asgeirtj/system_prompts_leaks (58,368 stars, focusing on chatbot and coding tool prompts). Both are updated regularly.

### How do Claude Code and Cursor system prompts differ?

Claude Code's prompt emphasizes minimal output and permission-based tool execution, making it ideal for terminal workflows. Cursor's prompt is more conversational and proactive, with deep codebase search capabilities and structured status updates, optimized for IDE-based development.

### Is system prompt extraction legal?

The legality of system prompt extraction is a gray area. While viewing and sharing extracted prompts is generally protected as research or commentary, using extracted prompts to bypass safety measures or replicate proprietary tools may violate terms of service. The Washington Post's coverage in May 2026 highlighted this as an emerging legal and ethical issue.

### How often do AI coding tools update their system prompts?

Major tools update their system prompts with each model version release. Claude Code has gone through at least 6 documented versions, Codex through 5 versions, and Cursor through 2 major versions. Updates typically occur every 3-6 months, with minor refinements happening more frequently.
