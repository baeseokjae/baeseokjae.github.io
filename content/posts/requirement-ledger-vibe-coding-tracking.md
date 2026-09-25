---
title: "Vibe Coding Requirements Tracking: Stop the Drift and Know What You Actually Wanted"
date: 2026-09-25T01:01:26+00:00
tags: ["vibe coding", "requirements tracking", "requirement ledger", "requirement drift", "prompt drift", "AI software development", "spec-driven development"]
description: "Requirement drift is vibe coding's hidden killer. Learn to build a requirement ledger that locks your intent, constraints, and decisions into the repo so you never lose the why."
draft: false
cover:
    image: "/images/requirement-ledger-vibe-coding-tracking.png"
    alt: "Vibe coding requirements tracking: from vibe coding to knowing what you actually wanted"
    relative: false
schema: "schema-requirement-ledger-vibe-coding-tracking"
---

Vibe coding lets you ship software by describing what you want in plain language, but the real failure isn't bad code — it's requirement drift. You start with a clear intent, and within a few long sessions the goal quietly buries itself under debugging noise, and neither the model nor you can reconstruct what you actually wanted. A requirement ledger — a versioned record of intent, constraints, and decisions kept in the repository — externalizes that memory and keeps every new session anchored to the original purpose.

## What Vibe Coding Actually Does to Your Requirements

Andrej Karpathy coined the term "vibe coding" in February 2025, and it became Collins Dictionary's Word of the Year for 2025. The premise is seductive: you describe the outcome, the AI generates it, and you iterate until it feels right. Today that workflow is no longer a hobby. According to the Sonar State of Code Developer Survey, developers report that 42% of their code is now AI-generated or assisted, up from 6% in 2023 and projected to reach 65% by 2027. Data Explained and MIT Technology Review report that 92% of U.S. developers now cite using AI coding tools daily, and AI generates roughly 41% of code worldwide.

What all these numbers miss is the structural problem the workflow introduces. In traditional development, writing a requirement forced you to think it through — you had to decide what the feature was before you asked anyone to build it. Vibe coding skips that step. You hand the model a fuzzy prompt, it produces a working result, and the fuzzy intent evaporates. The code becomes the only concrete thing you own, and code is famously terrible at explaining why it exists. A developer who never wrote the requirement down cannot later audit whether the code matches it, because there is no reference point.

The consequence is that requirement drift is now the most dangerous risk in long-running solo and small-team projects — more dangerous, in practice, than code quality or security holes. Both failure modes are serious, but a bug is visible and fixable. Drift is invisible: it accumulates one silent iteration at a time until the project is doing something you never intended.

## Why Requirement Drift Happens (The Model Forgets, and So Do You)

Drift isn't malice or incompetence on anyone's part. It is a joint memory failure, and it hits the human and the model differently.

The model's context window is finite. In a long session, the early goals — "this must respect these constraints," "this table must never be deleted," "this data must stay local" — get pushed out by debugging noise, error traces, and the incremental chatter of a hundred small fixes. The model does not remember the original tradeoffs you made, and it cannot reconstruct them. In fact it will often rationalize the wrong direction: given a plausible but altered interpretation, it generates code that feels consistent with the current context and quietly pushes the drift deeper. As one detailed write-up from knightli.com notes, both the model and the human forget: early goals get buried under debugging noise, and vibe coding skips the thinking that fuzzy requirements used to force.

The human side is just as fragile. You remember today's version of the intent — the one that has already been reshaped by every concession and quick fix since the project began. Humans are terrible at noticing their own goal posts moving. You don't feel the requirement changing because each step is small, defensible, and local. By week three you have confidently committed to a product description that has drifted a thousand tiny decisions away from what you told yourself you were building.

Red Hat's engineering team frames the technical half of the trap well: instructions become obsolete the moment code is generated. The generated code becomes the de facto source of truth, and since you never wrote the requirement down, the code is the only record you have — and it explains what you did, not what you meant. This is also why "functionality flickering" happens: unspecified details get filled in differently on every regeneration, so a button is blue one day and green the next, with no reason either way.

Here are the telltale signs you are already drifting, gathered from practitioners:

- The same bug gets fixed again and again in different places
- The AI modifies modules that are unrelated to the change you asked for
- You cannot explain why a particular directory, file, or function exists
- Your docs and your behavior no longer match
- You keep saying "that's close, but it's not what I asked for" without being able to say exactly what you asked for

If any of these feel familiar, the fix is not to try harder in the prompt box. The fix is to build a requirement ledger.

## What Is a Requirement Ledger?

A requirement ledger is a versioned record of intent, decisions, and constraints that lives in the repository and represents the authoritative statement of what you are building. It is not a prompt file, and it is not documentation for readers. It is the working contract between you and the model — the thing every generation reads before it writes, and the thing you consult to decide whether the model actually delivered.

The core idea is borrowed from an older discipline. Software architects have used Architecture Decision Records (ADRs) for years to capture intent, the alternatives that were ruled out, and the consequence of each choice. Applying that discipline to vibe coding gives you a way to write down the original tradeoffs — which the AI cannot reconstruct on its own — and carry them forward.

The key shift in mindset is this: the diff is the conversation, but the source of truth is the ledger. Git tells you what changed, but it does not tell you why, or which change reflected intent versus which was an accident of context loss. The ledger holds the why.

A good requirement ledger is a small living document — a single file or a small directory in the repo root — that anyone (human or model) reads at the start of a session. In spirit it is the "current truth" document that the prompt-drift discussion recommends: one page stating the user, the success criteria, and the non-negotiables, read at the start of every session.

## The Four Layers of a Requirement Ledger

You can collapse the practice into four layers, each answering a different question. Together they give you full coverage of intent.

**1. Intent (the Why).** This is the top of the project. The problem being solved, the user, the target outcome. If you can articulate why this project exists in one or two sentences, the model can reject suggestions that serve a different goal. This layer is what most vibe-coding projects are missing entirely.

**2. Requirements (the What).** The concrete features and behaviors the build must deliver. Each entry should be independently verifiable — a testable outcome, not a vibe. This is where you convert "make it feel fast" into "the initial render completes in under 200ms on a mid-range phone." Testable outcomes are explicitly described as the best cure for prompt drift, because a requirement you can test is a requirement that cannot silently mean something else.

**3. Constraints (the Boundaries).** Everything the build must not do or must respect: performance budgets, security rules, platform limits, third-party dependencies, the "Out of Scope" list. This is the section that prevents scope creep before it happens. As the anti-drift workflow guides point out, an explicit Out of Scope statement is the cheapest drift insurance you can buy, because it gives the model a defined boundary for rejection instead of a vague one.

**4. Decisions and Consequences (the Trade-offs).** The ADR layer. Each entry records a decision, the alternatives that were considered and ruled out, and the consequence of the choice. When the model later offers a change that looks cleaner, you can check it against the ledger: "We explicitly ruled out a database for this because it must work offline and single-file. Do not reintroduce one." The AI cannot reconstruct this history; only the ledger can carry it.

## Build Your Own: A Template You Can Copy

Here is a minimal, copyable skeleton that lives in a file like `REQUIREMENTS.md` at your repo root. Keep it flat, keep it current, and prune it ruthlessly — it should stay one page for a small project, not become a novel.

```markdown
# {Project Name}

## Intent (the why)
One or two sentences: who it is for and the problem it solves.

## Requirements (the what) — each must be testable
- [ ] REQ-1: <verifiable behavior>, e.g. "sorts the list by date, newest first, verified by clicking the column header"
- [ ] REQ-2: <verifiable behavior>

## Constraints (the boundaries)
- MUST NOT use a network at runtime
- MUST work single-file with no external DB
- Performance: render < 200ms on mid-range hardware

## Out of Scope (explicitly not doing)
- No user accounts in v1
- No mobile app

## Decisions (ADR-style)
### D-1: <Decision>
- Alternative ruled out: <choice + why>
- Consequence: <what this forces later>

## Changelog
- 2026-09-20: added REQ-2, rejected reintroducing DB (see D-1)
```

Commit this file to the repository. Tell the model to read it at the start of every session, and tell it that a change not reflected in this file is not a requirement. When you accept a change, update the ledger in the same commit you merge — so the git history and the ledger stay synchronized. Remember the warning from the workflow guides: the worst mistake is generating artifacts and immediately implementing without reading them. Read the ledger, then generate. Treat each artifact as a gate, not a formality.

## The Spec-Led Regeneration Loop (Refine, Don't Patch)

Once your ledger exists, you can adopt the practice that Red Hat's engineers recommend and that separates disciplined vibe coding from amateur drifting: spec-led regeneration beats patch-led repair.

When something breaks or the output diverges from your intent, your instinct as a developer is to patch the code — find the offending line and tell the model to fix it. Whack-a-mole. Patch-led repair is exactly how drift compounds, because each patch is a new small decision entered outside the ledger, and the specification never gets corrected to match reality.

The spec-led loop flips this. The spec (your ledger) is the authoritative blueprint the code must conform to. When something breaks, you go back to the spec, correct or refine the requirement, and then regenerate rather than repair. The model works from the corrected requirement, the code converges on the spec, and the ledger stays the single source of truth. When behavior diverges, the answer is always "the spec wins, refine and regenerate" — never "fix the code and let the spec catch up later."

This also gives you a cleaner way to handle the temptation to accept a wrong-but-plausible direction. The AI cannot reconstruct the tradeoffs you made; if a suggestion violates a recorded decision, your ledger lets you reject it with evidence rather than with an argument the drift has already eroded.

## Anti-Drift Workflows That Already Exist (and How to Borrow From Them)

You do not need to invent this from scratch. Several open, existing workflows formalize the ledgers above, and you can borrow whichever matches your style. The anti-drift catalog from vibecoding.app lists the main family:

- **PRD.md** — a standing product-requirements document capturing goals and constraints; close to the "Intent + Requirements" layers above.
- **GitHub Spec-Kit** — a bundled spec/plan/tasks structure that turns each plan into an inspectable artifact before implementation.
- **Planning with Files** — persist context across sessions by writing plans and decisions to the repo instead of trusting the chat.
- **Ralph Wiggum Loop** — an autonomous-style loop for projects that should proceed independently with the ledger as guardrail.
- **Superpowers** — a methodology library of reusable patterns for prompt-led development.

Whichever you choose, the two rules hold across all of them: treat each spec/plan/tasks artifact as a gate and review it before proceeding, and never `/implement` immediately after generating the artifact without reading it. The workflow's purpose is to force the thinking that vibe coding skips — the same thinking the requirement-ledger instinct restores.

## When the Ledger Pays Off: Signs You've Avoided the Three-Month Wall

The payoff is not immediate; it is felt at the point where most vibe-coded projects die. Solo projects following pure vibe coding tend to hit a wall around the three-month mark, when the accumulated drift makes the codebase unreconcilable with the product in your head and you can no longer explain why anything exists. A ledgered project hits that same moment and survives it.

Here is what it looks like when the ledger is working:

- A bug appears and you fix the same thing once, at the source, because the requirement was clear enough to test against
- A brand-new session (or a fresh model) picks up your code and reproduces your intent within minutes instead of recreating it from scratch
- You can reject a suggestion with a reason ("that violates D-1") and the model accepts it as authoritative
- Your docs and behavior match, because both are downstream of the same source of truth
- You can look at the file six months later and recall exactly why the strange directory exists

The evidence base is sobering about how easy the alternative is to slide into. A December 2025 study of open-source repositories found that AI-generated code introduced security vulnerabilities in 45% of development tasks, and IBM reports that as of late 2025, AI-generated code represents 22% of all merged code on GitHub. Those are technical risks, but they share a root cause with drift: code entering the repository that no one has properly vetted against a recorded intent. Trust is already scarce — 96% of developers do not fully trust that AI-generated code is functionally correct, and 61% say AI often produces code that looks correct but is not reliable. A ledger is your mitigation for exactly that mistrust: it gives you a testable standard to verify against instead of a vague feeling to hope against.

## Final Takeaway: Conversations Are Fast, Project Memory Must Be Stable

Vibe coding makes conversations cheap and fast, and that is its superpower. But a conversation is ephemeral — it is designed to be lost. A project is the opposite: it must carry its meaning forward across weeks, models, and fresh sessions. When you let the conversation be the only memory, drift is guaranteed, because neither the model's context window nor your own recollection can hold the original intent reliably.

A requirement ledger externalizes that memory. It is cheap to build, lives in version control, and forces the thinking that vibe coding skips. It turns "vibe coding requirements tracking" from a vague worry into a boring, reliable practice: write the intent down, keep the constraints honest, record the decisions, and regenerate from the spec instead of patching the code. The diff stays your conversation, but the ledger becomes your truth. That is how you stop wondering whether the code is what you actually wanted — and start knowing it.

## FAQ

**What is vibe coding requirements tracking?**
It is the practice of recording your project's intent, testable requirements, constraints, and decisions in a versioned file inside the repository, so that every AI generation reads it and you can verify the output against it. It exists to stop requirement drift — the silent compounding of scope changes in long AI-assisted sessions.

**Why does requirement drift happen in vibe coding?**
Both sides forget. The model's context window pushes early goals out under debugging noise and cannot reconstruct the original tradeoffs, while the human loses the original intent because each small concession reshapes the goal imperceptibly. Code becomes the only source of truth, and code cannot explain why it exists.

**What is a requirement ledger?**
A requirement ledger is a living, versioned document in your repo that records the why (intent), the what (testable requirements), the boundaries (constraints and out-of-scope), and the trade-offs (decisions and consequences) of your project, borrowing from software-architecture ADR practice.

**How do I prevent scope creep in vibe coding?**
Keep an explicit "Out of Scope" section in your requirement ledger and make it enforceable. Because the boundary is written down and read by the model every session, the AI can reject scope creep instead of unknowingly extending it.

**What is the difference between patching and spec-led regeneration?**
Patching fixes a broken or drifted behavior by editing the code directly, which compounds drift because each tiny fix is a decision outside the ledger. Spec-led regeneration refines the spec first and regenerates from it, keeping the spec as the authoritative blueprint the code must conform to.
