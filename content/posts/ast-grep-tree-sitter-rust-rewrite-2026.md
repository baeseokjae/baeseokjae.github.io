---
title: "AST-grep Rewrote Tree-sitter in Rust: 30% Faster Code Analysis for AI Tools"
date: 2026-07-28T16:03:06+00:00
tags:
  - AST-grep
  - Tree-sitter
  - Rust
  - AI-assisted development
  - code analysis
  - parser performance
  - structural search
description: "AST-grep rewrote Tree-sitter's C core in Rust using ChatGPT, achieving 29.74% faster parsing and 22.2% faster end-to-end code analysis for AI tools."
draft: false
cover:
  image: "/images/ast-grep-tree-sitter-rust-rewrite-2026.png"
  alt: "AST-grep Rewrote Tree-sitter in Rust: 30% Faster Code Analysis for AI Tools"
  relative: false
schema: "schema-ast-grep-tree-sitter-rust-rewrite-2026"
---

## What Is the AST-grep Tree-sitter Rust Rewrite?

AST-grep, the popular structural code search tool with over 15,000 GitHub stars, rewrote Tree-sitter's C parsing core entirely in Rust using ChatGPT-assisted code generation. The result is a 29.74% improvement in raw parsing throughput and a 22.2% faster end-to-end code analysis pipeline, making it significantly faster for AI coding agents and developer tools that rely on syntax-tree-based code understanding.

## Why Did AST-grep Rewrite Tree-sitter in Rust?

Tree-sitter has been the gold standard for incremental parsing in code editors since its release. Its C core is battle-tested and powers syntax highlighting in editors like Neovim, VS Code, and Zed. But AST-grep's use case is fundamentally different from an editor's.

### The Problem with Tree-sitter's C Core for AI Workloads

Tree-sitter was designed for interactive editing, where incremental parsing — reusing the old syntax tree after small edits — is critical. AI coding agents, however, don't edit files character by character. They analyze entire codebases at once, searching for structural patterns across thousands of files. For this workload, incremental parsing is unnecessary overhead.

The C codebase also presented maintenance challenges. AST-grep is written in Rust, and maintaining a C foreign-function interface (FFI) to Tree-sitter introduced complexity, build friction, and limited optimization opportunities. By rewriting the parser in Rust, the team could eliminate the FFI boundary, remove features irrelevant to AI workloads, and apply Rust-specific optimizations like arena allocation.

### Removing Incremental Parsing: A Feature, Not a Bug

The most controversial decision in the rewrite was removing incremental old-tree reuse — a core Tree-sitter feature. For AI agent workloads that parse fresh code on every invocation, this feature was pure overhead. The Rust rewrite simply skips it, which simplifies the parser and contributes directly to the performance gains.

## How Did ChatGPT Assist in Writing the Rust Parser?

One of the most remarkable aspects of this project is that ChatGPT generated the majority of the Rust code. The AST-grep team used the AI model as a code generation engine, translating Tree-sitter's C parsing logic into idiomatic Rust.

### The AI-Assisted Rewrite Workflow

The team fed Tree-sitter's C source code to ChatGPT and asked it to produce equivalent Rust implementations. The AI handled the mechanical translation — converting C's manual memory management to Rust's ownership model, translating pointer arithmetic to safe Rust patterns, and restructuring C macros into Rust generics and traits.

However, the AI-generated code was not production-ready out of the box. The team described a "load-bearing wall" metaphor: AI made the rewrite possible by handling the bulk translation, but human expertise in profiling, benchmarking, and iterative optimization turned the translated code into a high-performance parser. The AI wrote the first draft; humans made it fast.

### What This Means for Systems Programming

This project demonstrates a new paradigm for systems-level rewrites. Traditionally, porting a mature C codebase to Rust requires months of manual effort. With AI-assisted code generation, the mechanical translation phase is dramatically compressed. The human effort shifts from "writing code" to "directing, profiling, and optimizing" — a fundamentally different skill set that combines domain expertise with AI orchestration.

## What Performance Gains Did the Rust Rewrite Achieve?

The rewrite was benchmarked extensively, and the results are documented across a four-part blog series. Here are the key numbers:

| Metric | C Baseline | Rust Rewrite | Improvement |
|--------|-----------|-------------|-------------|
| Raw parsing throughput | Baseline | +29.74% | **29.74% faster** |
| Tree traversal throughput | Baseline | +10.16% | **10.16% faster** |
| End-to-end ast-grep outline (user CPU) | 1.233s | 0.960s | **22.2% faster** |
| Memory usage (RSS, ast-grep run) | 26.52 MiB | 34.43 MiB | +29.8% more memory |
| TypeScript stress corpus peak | >1 GiB | 91.2 MiB | **~91% reduction** |

### Raw Parsing: The Headline 30% Gain

The raw parsing throughput improvement of 29.74% is the headline number. This measures how fast the parser can produce a syntax tree from source code, isolated from any application logic. The gain comes from several Rust-specific optimizations:

- **Arena allocation**: Instead of individual heap allocations for each syntax node, the Rust parser uses arena allocators that batch memory in contiguous blocks. This reduces allocation overhead and improves cache locality.
- **Compact indexes**: The Rust version uses smaller, more cache-friendly data structures for internal node representations.
- **Eliminated FFI overhead**: Without the C-to-Rust FFI boundary, function calls that previously crossed the language barrier are now direct Rust calls.

### End-to-End Performance: The Real-World Number

While the raw parser is 30% faster, the end-to-end ast-grep outline command — a realistic workload that parses code and extracts structural information — improved by 22.2% (0.960s vs 1.233s user CPU time). The gap between 30% and 22% is instructive: parser speed is only one component of total application performance. Other factors like I/O, tree traversal, and pattern matching also contribute to wall-clock time.

## How Did GLR Optimization Contribute to the Speedup?

Tree-sitter uses a Generalized LR (GLR) parsing algorithm, which can handle ambiguous grammars by maintaining a graph of possible parse states rather than a single stack. This is what makes Tree-sitter so robust for real-world code — it can parse incomplete or syntactically incorrect files that would choke a standard LR parser.

### The 99% Optimization Insight

During the rewrite, the AST-grep team made a critical observation: in real-world code analysis workloads, 99% of the parser stack follows a single straight path. The GLR graph — with its branching and merging — is rarely needed. This insight drove a key optimization: optimize for the common case (single-path parsing) and fall back to the full GLR machinery only when ambiguity is detected.

This is a textbook example of profile-driven optimization. Rather than optimizing the GLR algorithm in the abstract, the team measured actual workloads and discovered that the theoretical worst case (massive ambiguity) is practically nonexistent for the codebases AST-grep analyzes.

### Memory Layout and Arena Allocation

The Rust rewrite introduced arena-based memory management for syntax nodes. Instead of allocating each node individually on the heap — which causes fragmentation and poor cache behavior — the parser allocates nodes in contiguous memory regions. This has two benefits:

1. **Faster allocation and deallocation**: Arena allocation is essentially a bump-pointer operation, far cheaper than individual malloc/free cycles.
2. **Better cache locality**: Contiguous nodes are more likely to be in the CPU cache together, speeding up tree traversal.

The memory tradeoff is real: RSS increased by 29.8% (34.43 MiB vs 26.52 MiB) in the ast-grep benchmark. However, the TypeScript stress corpus tells a different story. Before optimization, peak memory exceeded 1 GiB. After arena optimization, it dropped to 91.2 MiB — a 91% reduction. The arena allocator prevents memory fragmentation that previously caused exponential growth on large files.

## What Is the Gap Between Parser Benchmarks and Application Performance?

This is one of the most important lessons from the rewrite. The raw parser benchmark shows a 30% improvement, but the end-to-end application only sees 22%. Why the gap?

### The Components of End-to-End Performance

An ast-grep command involves several stages:

1. **File I/O**: Reading source files from disk
2. **Parsing**: Building syntax trees (the 30% faster part)
3. **Tree traversal**: Walking the syntax tree to find matches
4. **Pattern matching**: Applying the user's search pattern
5. **Output formatting**: Displaying results

Only step 2 benefits from the parser rewrite. Steps 1, 3, 4, and 5 are unchanged. The 22.2% end-to-end improvement is actually quite impressive when you consider that parsing is only one component of the pipeline.

### The Initial Performance Regression

Interestingly, the first version of the Rust rewrite was actually slower than the C baseline. The AI-generated code, while functionally correct, lacked the optimizations that years of C development had accumulated. Only after profiling and iterative tuning — arena allocation, compact indexes, GLR optimization — did the Rust version surpass the C baseline.

This is a crucial lesson for anyone considering AI-assisted rewrites: the AI can generate correct code quickly, but making it fast requires the same profiling and optimization skills that traditional performance engineering demands.

## What Lessons Does This Project Offer for AI-Assisted Systems Programming?

The AST-grep Tree-sitter rewrite is a case study in the future of systems programming. Here are the key takeaways:

### AI as a Force Multiplier, Not a Replacement

ChatGPT wrote the bulk of the Rust code, but human engineers directed the effort, profiled the results, and iterated on performance. The AI compressed the translation phase from months to weeks, but the optimization phase still required deep expertise in parsing algorithms, memory management, and Rust's performance characteristics.

### Profile Before You Optimize

The 99% single-path GLR insight came from profiling real workloads, not from theoretical analysis. The team didn't guess where the bottlenecks were — they measured them. This principle applies to any performance optimization project: measure first, optimize second.

### Removing Features Is a Legitimate Optimization

The decision to remove incremental parsing and native Wasm grammar loading was controversial but correct for AST-grep's use case. Not every feature from the original codebase needs to survive a rewrite. Understanding which features are "load-bearing" for your specific workload and which are dead weight is a critical skill.

### Rust's Ownership Model Pays Off

The Rust rewrite eliminated an entire class of memory bugs that plague C codebases. While the C version of Tree-sitter is battle-tested, the Rust version gains compile-time memory safety guarantees. For a parser that processes untrusted source code, this is a significant security advantage.

## How Does This Impact AI Coding Tools and the Ecosystem?

The implications extend far beyond AST-grep itself. Tree-sitter is the backbone of code analysis for many AI coding tools, including:

- **CodeRabbit**: Uses AST-grep for AI-native code review and linting, combining structural search with LLM analysis for code quality at scale.
- **CodeRLM**: A Tree-sitter-backed code indexing system for LLM agents that improves code understanding through syntax-tree-aware indexing.
- **VT Code**: An AST-aware Rust TUI coding agent that integrates both Tree-sitter and AST-grep for terminal-based AI coding.

### Faster Code Analysis for Agentic Workflows

AI coding agents analyze entire codebases to understand context before generating code. A 22% faster end-to-end analysis means agents can process more code in less time, leading to better context understanding and more accurate code generation. For agentic workflows that parse thousands of files per session, this performance improvement compounds significantly.

### The Growing Tree-sitter Ecosystem

The Tree-sitter ecosystem is expanding rapidly. The Rust rewrite repo itself has already attracted attention, and the broader community is watching closely. If the Rust version proves stable and performant, it could become the foundation for a new generation of Rust-native code analysis tools.

### What This Means for Developer Tooling

Faster parsing means faster IDE features, faster linting, faster code search, and faster AI code generation. Every tool that depends on syntax-tree analysis benefits from a faster Tree-sitter. The Rust rewrite doesn't just make AST-grep faster — it raises the performance ceiling for the entire ecosystem of tools built on Tree-sitter.

## Frequently Asked Questions

### Is the Rust rewrite of Tree-sitter a drop-in replacement for the C version?

No. The Rust rewrite removes incremental parsing and native Wasm grammar loading, which are features designed for interactive editing. It is optimized for AI agent workloads and batch code analysis, not for use as an editor plugin. If you need incremental parsing for an editor, the C version remains the right choice.

### How much faster is the Rust version in real-world use?

End-to-end ast-grep commands run approximately 22% faster in user CPU time. Raw parsing is 30% faster. The exact improvement depends on your workload — codebases with many large files benefit more than those with many small files, where I/O overhead dominates.

### Did ChatGPT write all the Rust code?

ChatGPT generated the initial translation from C to Rust, but the team performed extensive profiling and optimization to achieve the performance gains. The AI handled the mechanical translation; humans optimized the result. The final code is a collaboration between AI generation and human performance engineering.

### Does the Rust rewrite use more memory?

In typical workloads, the Rust version uses about 29.8% more RSS (34.43 MiB vs 26.52 MiB). However, for large files, the arena allocator prevents memory fragmentation, resulting in dramatically lower peak memory — 91.2 MiB vs over 1 GiB for the C version on a TypeScript stress corpus.

### Will the Rust rewrite replace the C version of Tree-sitter?

For AST-grep's use case, yes. For the broader Tree-sitter ecosystem, it depends on whether the community adopts the Rust version for editor integration. The C version remains the standard for interactive editing due to its incremental parsing support. The two versions may coexist for different use cases.
