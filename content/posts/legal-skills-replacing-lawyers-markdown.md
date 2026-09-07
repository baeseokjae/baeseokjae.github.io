---
title: "Legal Skills Markdown Agents: Replacing Lawyers with Markdown Files"
date: 2026-09-07T16:03:19+00:00
tags:
  - legal skills markdown agents
  - markdown legal documents
  - legislation as code
  - AI legal document drafting
  - legal agent skills
  - patent drafting AI
  - markdown contracts
  - versioned law git
description: "Legal skills markdown agents turn legal work into executable SKILL.md playbooks and versioned law files, displacing billable hours with a repo checkout."
draft: false
cover:
  image: "/images/legal-skills-replacing-lawyers-markdown.png"
  alt: "Legal Skills: Replacing Lawyers with Markdown Files"
  relative: false
schema: "schema-legal-skills-replacing-lawyers-markdown"
---

Legal skills markdown agents are turning legal work into executable playbooks: a public repo called `legal-skills` packages U.S. utility-patent work as SKILL.md files, checklists, and deterministic Python scripts that run a 316-item pre-filing audit without opening a matter. The claim is blunt — displace legal fees, not assist counsel — and it sits on a broader movement where legislation itself becomes versioned Markdown in git. This guide explains what the pattern is, why Markdown is the right format, where agents still fail, and what stays reserved to human lawyers.

## What "Replacing Lawyers with Markdown Files" Actually Means

The phrase sounds like a joke, but it describes a concrete engineering pattern. Instead of paying a firm to run a process, you encode the process itself as files: a `SKILL.md` that tells an AI agent what to do, checklists that enumerate every step, intake questionnaires that gather facts, and deterministic scripts that enforce the mechanical parts. The `legal-skills` repository by Greg Fodor is the clearest example. It frames patent work as a document pipeline that firms wrap in scarcity, letterhead, and a rate card — and then unwraps it.

The goal is not to make lawyers faster. It is to make the lawyer's process runnable by a model that costs less than lunch. Drafting and filing a U.S. utility patent application can cost roughly $18,000 at a firm; the repo offers a checkout-and-run alternative. A patent boutique associate is billed at about $400/hour for reading a draft once. When the process lives in versioned files, that reading is done by an agent that never bills an hour.

This is a different claim from "AI assists lawyers." It is the claim that most of what clients pay for is process, and process belongs in files — not firms.

## Why Markdown Is the Right Format for Legal Work

Markdown is plain text with lightweight structure: headings, lists, tables, and links. That makes it the ideal substrate for legal work for three reasons.

First, it is diffable. When a contract or a statute is a Markdown file, every change is a visible diff. You can see exactly what a revision altered, who made it, and when. This is the core value proposition of the "legislation as code" family: `legalize-es` (Spanish legislation in Markdown, versioned as git) has 1,879 GitHub stars, and `legalize-kr` (Korean) has 1,518. Each law is a file, each reform a commit, each promulgation date a real git timestamp.

Second, it is auditable. Git history is an immutable ledger of who changed what. For legal documents, where provenance and version matter, that is not a nice-to-have — it is the whole point.

Third, it separates content from typesetting. The "Markdown for Lawyers" idea dates to at least 2016, and its insight was that lawyerly content should not be welded to a word processor's layout. Write the substance in Markdown, render it to PDF or HTML when needed. The `lexicon.esq` project and `legal-markdown-js` both build on this: Markdown as the authoring format for contracts, with structured output and git-friendly tooling.

| Format | Diffable | Auditable | Versioned | Renders to PDF | Agent-runnable |
|--------|----------|-----------|-----------|----------------|----------------|
| Word .docx | No | No | No | Yes | Poor |
| PDF | No | No | No | Native | Poor |
| Markdown | Yes | Yes | Yes | Via tooling | Yes |

## The Agent-Skills Model: SKILL.md as an Executable Legal Playbook

The `legal-skills` repo runs three skills in order. The first, `patent-audit`, executes a 316-item pre-filing checklist. The second, `patent-examine`, runs a recurrent simulated USPTO examination loop. The third, `patent-workaround`, performs adversarial design-around testing. Together they simulate the full prosecution cycle without opening a matter.

The key design decision is that the model follows a contract, not a vibe. A `SKILL.md` file is a structured instruction set that tells the agent exactly what to do at each step. The model does not improvise a legal strategy; it executes a documented procedure. This is what makes the playbook "executable" — the intelligence is partly in the file, not only in the model.

The 316-item audit breaks down into four categories:

- **105 blocking items** — things that must be resolved before filing.
- **28 mechanical items** — handled by code, because models cannot reliably count or do date arithmetic.
- **169 assisted items** — the model works with evidence the user provides.
- **119 judgment items** — where the model reasons, but a human should review.

This distribution is the honest version of the claim. A large share of the work is mechanical or assisted, and that share is what gets displaced. The judgment items are where a human stays in the loop.

## Legislation as Code: Versioned Law in Git

The same pattern scales from a single patent to an entire legal corpus. The `legalize` family treats legislation as a Git repository: each law is a Markdown file, each revision is a commit with the real promulgation date. `legalize-es` (Spanish) is the largest at 1,879 stars; `legalize-kr` (Korean) follows at 1,518; the pattern also extends to Greek and the core `legalize-dev/legalize` project.

Why does this matter? Because law is versioned by nature. A statute is amended, repealed, and re-enacted. When that history lives in git, you get three properties for free:

- **Diffability** — see exactly what a reform changed.
- **Auditability** — trace every change to a commit and a date.
- **Reproducibility** — rebuild any historical version of the law on demand.

This is the same value proposition as the patent playbook, applied to the law itself. If process belongs in files, so does the law the process operates on.

## Where AI Agents Still Fail (and Why Deterministic Checks Matter)

The `legal-skills` README is explicit about a hard limit: models cannot count, do date arithmetic, or exhaustively cross-reference. That is why the repo ships deterministic Python scripts. The mechanical parts of the audit — counting items, checking dates, cross-referencing requirements — are enforced by code, not by the model's best guess.

This is the crucial engineering insight. An LLM is a probabilistic text generator. It is excellent at drafting, summarizing, and reasoning about open-ended questions. It is unreliable at anything that requires exact enumeration or arithmetic. A 316-item checklist is exactly the kind of task where a model will confidently skip item 214 or miscompute a deadline.

The solution is to split the work by nature:

- **Mechanical** → deterministic code. No model involved.
- **Assisted** → model + evidence the user supplies.
- **Judgment** → model reasons, human reviews.

This division is what makes the whole system trustworthy enough to run without opening a matter. The model does what models are good at; the code does what code is good at; the human does what only a human can do.

## What Stays Reserved to Human Lawyers

The `legal-skills` repo carries a heavy "not legal advice" disclaimer, and it is not boilerplate. The skills do not file, sign, or appear before any tribunal. Some acts stay reserved to a registered practitioner by law — signing a filing, appearing in court, and making duty-of-candor calls to a patent office.

This is the honest boundary of the "replace lawyers with markdown" thesis. What gets displaced is process: the reading, the drafting, the checklist-running, the cross-referencing. What does not get displaced is the set of acts that the legal system reserves to licensed humans. A Markdown file cannot sign a declaration under penalty of perjury. An agent cannot appear before the USPTO. And the judgment calls about candor and disclosure are exactly the kind of thing a court will hold a human responsible for.

So the accurate framing is not "no lawyers." It is "far fewer billable hours for process, and a sharper focus on the acts that only a licensed human can perform."

## How to Start: A Practical Guide

If you want to apply this pattern, you do not need to start with a 316-item patent audit. Start small.

1. **Pick a repeatable legal process** you already do — a contract review, a compliance checklist, a filing checklist.
2. **Write it as a SKILL.md** — a structured instruction set that tells an agent what to do at each step.
3. **Separate the mechanical from the judgment.** Anything that requires counting, dates, or exhaustive cross-referencing goes into a deterministic script. Everything else can be model-assisted.
4. **Version everything in git.** Your process, your checklists, and your drafts should all be diffable and auditable.
5. **Keep a human on the judgment items.** The goal is to shrink the billable surface, not to remove accountability.

The `legal-skills` repo is the reference implementation for the patent domain. The `legalize` family shows the pattern at the scale of an entire legal corpus. `lexicon.esq` and `legal-markdown-js` show the authoring and tooling side. Together they form a coherent stack: Markdown for content, git for versioning, SKILL.md for agent instructions, and deterministic code for the mechanical parts.

## The Future of Legal Fees

The economic backdrop is a repricing of the billable hour. Legal's AI repricing is estimated at a $900 billion market — the "Death of the Billable Hour" thesis. When a process that a firm bills at $400/hour can be run by a model that costs less than lunch, the rate card itself is under pressure.

The direction is clear. Process moves into versioned files. Agents execute documented playbooks. Deterministic code enforces the mechanical parts. And the billable hour — the unit that made process expensive — gets repriced by the same technology that made it cheap.

## FAQ

**What are legal skills markdown agents?**
They are executable legal playbooks written as SKILL.md files that tell an AI agent how to run a legal process — like a 316-item patent pre-filing audit — with deterministic scripts enforcing the mechanical parts.

**Can Markdown really replace a lawyer?**
Not entirely. It displaces the process work — reading, drafting, checklist-running, cross-referencing — but signing, filing, appearing before a tribunal, and duty-of-candor calls stay reserved to licensed practitioners.

**Why is Markdown better than Word or PDF for legal documents?**
Markdown is plain text, so it is diffable, auditable, and versionable in git. You can see exactly what a revision changed, trace it to a commit, and rebuild any historical version on demand.

**What is "legislation as code"?**
It is the pattern of managing law as a Git repository — each law a Markdown file, each reform a commit with the real promulgation date. The `legalize` family applies it to Spanish, Korean, and Greek legislation.

**Where do AI agents still fail in legal work?**
They cannot reliably count, do date arithmetic, or exhaustively cross-reference. That is why the mechanical parts of a legal playbook are enforced by deterministic Python scripts rather than by the model.
