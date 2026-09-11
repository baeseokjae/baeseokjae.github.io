---
title: 'Vomit Claude Token Cleanup: Fix Verbose Output with a Separate LLM'
date: 2026-09-11T13:01:42+00:00
description: Vomit Claude token cleanup explained — how a small local LLM rewrites Claude's verbose token vomit into clean prose and cuts downstream token costs.
draft: false
cover:
  image: /images/vomit-clean-up-claude-token-output.png
  alt: 'Vomit Claude Token Cleanup: Fix Verbose Output with a Separate LLM'
  relative: false
tags:
- claude
- claude-code
- token-cost
- llm-orchestration
- local-llm
- prompt-engineering
- developer-tools
schema: "schema-vomit-clean-up-claude-token-output"
---

Claude's verbose output — long caveat lists, hedging, verification dumps, and "token vomit" — wastes paid tokens and human reading time every time you copy a reply into a PR, doc, or commit. Vomit fixes this by piping Claude's message through a separate, local LLM that rewrites it into concise prose before it ever reaches your screen. The cleanup pass runs on your own machine for zero hosted-token cost, and measured over 100 agent iterations it cut downstream token waste by roughly 20%. This guide shows you the root cause, how to set up Vomit, and why separating the reasoning model from the style model is a pattern worth stealing.

## What Is Claude's "Token Vomit" and Why Is It Expensive

"Token vomit" is the community term for the bloated, risk-averse prose Claude Code produces: numbered caveat lists, "I assumed X, please verify Y" hedging, verbose file-read summaries, and long search-result dumps that get pasted straight into the session and into your conversation history. On Hacker News after Vomit's launch, developers called Opus-class output "slop vomit" and complained that PR descriptions and comments copied from Claude are practically unreadable without editing.

The cost problem is structural, not cosmetic. Verbose tool output — file reads, logs, and search results — is over half of a typical Claude Code bill on benchmarks from Lineman.io's 2026 dev-team guide. The reason is context compounding: every turn re-sends the entire conversation as input. A bulky tool read that is consumed once is re-billed on every later turn, so session cost grows with session length. Every word of hedging you keep in the visible reply is also re-sent on every subsequent turn. Cleaning that output up is not a nicety; it is a direct lever on your token bill.

Because style consumes the same paid tokens as substance, asking for fewer words is a per-token economic decision. Verbose output does not just cost reading time; it inflates every future context window it rides in.

## Why Prompt-Fixing Fails (and What Actually Causes It)

The first instinct is to tell Claude to "be more concise." It fails for two reasons. First, Claude still burns your paid tokens trying to speak differently — the instruction itself costs input tokens on every turn, and the output is often still verbose. Second, as Vomit's author argues, spending token budget on "how to speak" instructions that Claude ignores or even makes worse is exactly the waste the tool is designed to remove.

Different users on the Hacker News thread found prompt and output-style tweaks ineffective and ended up preferring a deterministic second-LLM rewrite instead. Telling Claude to never write docs, delegating to a separate tool, and using a small subagent to reword long output were all user-built workarounds — evidence that style is not reliably fixable inside the reasoning model.

The root cause is architectural: a frontier reasoning model is optimized to reason and hedge, not to write crisp copy. Its "voice" is overcautious by design. No prompt reliably overrides a behavior that is deeply trained into the model; the reliable fix is to move the styling job to a different model built for concise generation.

## The Core Pattern: Separate the Reasoning LLM from the Style LLM

The pattern behind Vomit is simple and general: let a large reasoning model do the understanding, then hand the raw output to a small, cheap, often local model whose only job is to rewrite and format it. Separating reasoning from style means each model does what it is good at and neither wastes tokens fighting the other.

This is the same multi-LLM orchestration design that BuildZn documented for structured data: a primary LLM (Claude) does the reasoning, and a secondary cheaper LLM parses, validates, and reformats into strict JSON, YAML, or markdown. The cleanup pass is dramatically cheaper than a re-parse from the big model — roughly 70–80% fewer tokens, measured at about 150–200 input tokens for a Claude re-parse versus roughly 50 in plus 20–30 out with a 7B local model.

The second-LLM cleanup pattern generalizes everywhere: PR descriptions, commit messages, long-form doc output, and structured data all benefit from a deterministic post-processing pass. You are not asking a "better" model to rewrite Claude; you are asking a cheaper, more predictable one to compress it.

## Meet Vomit: A Local Second-LLM Cleanup Tool for Claude Code

Vomit (github.com/zachahn/vomit) is an open-source, GPL-3.0 Go tool released by Zach Ahn that turns Claude's token vomit into English by piping the message through a local LLM. It is fully local — no telemetry, no external dependencies, nothing leaves your machine.

Mechanically, it hooks into Claude Code through the `MessageDisplay` hook: it buffers Claude's output, forwards it to a local LLM, waits for the rewrite, then displays the cleaned version in the session UI. The editor model sees only Claude's message — it does not get file access or action context, only the text to compress. That isolation is what keeps the tool safe but also what limits its fidelity (more on that below).

A non-invasive "tail" mode shows the rewrites side-by-side instead of replacing Claude's display, which is the safe first step before letting Vomit overwrite your screen. When it does replace output, you can press ctrl-o in Claude Code to always see the original. As of the August 2026 launch, Vomit had 193 stars and 42 commits.

## Step-by-Step Setup: Install, Init, and Scrub

Setting up Vomit takes four commands and a local model. First, install the binary:

```bash
go install github.com/zachahn/vomit@latest
```

Then initialize the configuration and wire the Claude Code hook:

```bash
vomit init
vomit scrub -claude
```

The `scrub -claude` command is what hooks the `MessageDisplay` step so Vomit intercepts Claude's output and runs it through your local model before display. After `vomit init`, point Vomit at your preferred local LLM endpoint — it works with Ollama, Apfel, or any OpenAI-compatible endpoint, and the recommended default is GPT-OSS 20B running through Llama.app.

If you have never run `go install` for this binary before, `vomit init` will walk you through the model endpoint configuration so the scrub hook knows where to send messages. Keep ctrl-o handy: it always shows the untouched original so you can audit any rewrite instantly.

## Choosing a Cleanup Model: Local vs Cloud

The cleanup model choice is a privacy-and-latency tradeoff. The Vomit approach is deliberately local-first: running on your own machine adds zero hosted-API token charge on top of Claude's bill, and your raw message text never leaves your hardware. That is the strongest privacy posture for code you do not want sharing with another hosted service.

Recommended local options, per the project:

| Model | Endpoint | Notes |
|-------|----------|-------|
| GPT-OSS 20B | Llama.app | Author's recommended default; small enough to run locally, writes cleanly |
| Any Ollama model | Ollama | Easy setup, model-agnostic; Mistral 7B is a proven cheap cleaner in the BuildZn write-up |
| Any OpenAI-compatible | Custom | Works with Apfel or compatible local servers |

A hosted cleanup model is possible but cancels part of the value: every rewrite then costs metered tokens, and your message text crosses to a second vendor. Local cleanup keeps the pass free and private, at the cost of local compute and a few hundred extra milliseconds of latency — tens to low-hundreds of ms on the BuildZn benchmarks.

The surprising finding, which Vomit's author highlights, is that OpenAI's free, small 20B open-source GPT-OSS model writes clearer prose than frontier Opus on this task. You may already own a better style model on your own laptop.

## Cost & Privacy Reality Check: What It Saves and What It Can't

The most common misconception is that a second-LLM cleanup cuts Claude's original bill. It cannot. Vomit is a workflow tool, not a Claude discount: it never recovers or reduces tokens Claude already generated and billed. The financial upside is different and real:

- Avoiding a paid second rewrite turn from the big model — a 70–80% token saving versus asking Claude to re-parse its own output, per BuildZn.
- Cutting the downstream re-parse tokens whenever that output feeds another parse or validation step — roughly 20% lower downstream token waste across a 100-iteration workflow.
- Saving human reading and review time on every pasted PR, doc, or comment.

Pricing context from aipricing.guru (August 2026): Claude Sonnet 5 runs about $40/M input and $25/M output. When the cleanup pass runs locally, Vomit adds no hosted-token charge at all — you pay only your machine's compute. The practical recommendation from that analysis: local cleanup benefits developers who already run a local model, because there is no extra metered API call and the editor does not need repo access since it only edits the message.

## The Pattern Beyond Vomit: Clean Output for JSON, Markdown, Docs

Vomit is one implementation of a general architecture you can reuse. The "cleanup model" pattern works for structured data, not just screen prose: a primary LLM reasons, then a secondary cheap model validates and reformats into strict JSON, YAML, or markdown tables. BuildZn's trade-recommendation workflow used exactly this split with Mistral 7B via Ollama and measured 70–80% cheaper cleanup passes and roughly 20% lower overall downstream token waste — over 100 iterations — with temperature near 0.01 for deterministic output.

The same separation applies to PR descriptions, commit messages, and docs: write with the reasoning model, then compress and format with a small model. In each case the division of labor is what saves money — a cheap model does not reduce the reasoning model's cost, but it makes every downstream consumer of the text cheaper to feed and faster to read.

## Risks, Gotchas, and Safe Usage

The cleanup model introduces risks you should manage before it replaces your display:

- **Hallucination.** Because the local LLM sees only Claude's message with no file or action context, it can invent details or drop nuance. The editor does not verify facts; it only compresses text. Always audit the original before trusting a rewrite.
- **Omitted nuance.** Compressing hedging can strip caveats you actually needed. Side-by-side/tail mode makes the difference visible before you commit.
- **Slow rewrites.** A local model adds latency on every displayed message — tens to low-hundreds of ms. For long outputs the pause is noticeable before Vomit replaces the text.
- **Fidelity loss.** A smaller model may misunderstand technical terms or code snippets and mangle them, so keep ctrl-o access to the original at all times.

Safe usage defaults: start in non-invasive tail/side-by-side mode, let a human (or the main agent) validate fidelity against hallucination, and do not route anything mission-critical through the editor until you trust it on that specific output shape.

## FAQ

**Does Vomit reduce Claude's original API bill?**
No. Vomit cannot recover tokens Claude already generated and billed. It saves money by avoiding a paid second rewrite turn, cutting downstream re-parse tokens (~20% lower downstream waste measured over 100 iterations), and reducing human reading time.

**Is the cleanup LLM ever given access to my files?**
No. Vomit passes the editor model only Claude's message text — no file, action, or repo access. That isolation is what keeps the tool safe, but it also means the editor can hallucinate because it has no context beyond the message.

**Can I see the original Claude output after Vomit rewrites it?**
Yes. Press ctrl-o in Claude Code to toggle back to the original message. Vomit also offers a non-invasive "tail" mode that shows rewrites side-by-side instead of replacing the display.

**Does Vomit work with any model, or only GPT-OSS 20B?**
Vomit works with any OpenAI-compatible LLM endpoint — Ollama, Apfel, or a custom local server. GPT-OSS 20B via Llama.app is the author's recommended default, but Mistral 7B and other local models are supported.

**Is running the cleanup locally cheaper and more private than hosted cleanup?**
Yes. Local cleanup adds zero hosted-API token charge and keeps message text on your hardware. The tradeoffs are local compute usage and added latency (tens to low-hundreds of ms per rewrite).
