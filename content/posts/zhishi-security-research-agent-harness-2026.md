---
title: 'ZhiShi Review 2026: A Rust Agent Harness for Security Research'
date: 2026-08-28T16:01:54+00:00
tags:
- agent-harness
- security-research
- offensive-security
- vulnerability-research
- AI-agents
- penetration-testing
description: ZhiShi is an AGPL-3.0 agent harness for security research that combines a Tauri Rust shell with a TypeScript loop engine, driving CTF, fuzzing, and real CVE reproduction.
draft: false
cover:
  image: /images/zhishi-security-research-agent-harness-2026.png
  alt: 'ZhiShi Review 2026: A Rust Agent Harness for Security Research'
  relative: false
schema: "schema-zhishi-security-research-agent-harness-2026"
---

ZhiShi is an open-source agent harness purpose-built for security research — a human-in-the-loop workbench for binary exploitation, penetration testing, whitebox code audit, and AI security — that layers a domain-specific research loop on top of the MIT-licensed `@earendil-works/pi-agent-core` engine. It uses a Tauri (Rust) desktop shell wrapping a TypeScript/Node core, and publishes unusual evidence-first proof of capability: 100% Pwnable.kr CTF completion, 98% Hacker101, and a fully reproduced exploit chain for CVE-2026-34621 (Adobe Acrobat Reader, CVSS 8.6).

## What is ZhiShi? Positioning an agent harness for security research

The "agent harness for security research" framing matters because it is deliberately narrower — and more honest — than the generic "AI hacking tool" marketing common in 2026. ZhiShi does not claim to be a fully autonomous pentester. Instead it describes itself as a control plane for the researcher: the agent owns the execution environment, compiles and iterates on exploit code inside it, maintains an evidence-backed research archive, and pauses for human approval at defined safety gates.

Positioning itself as a harness rather than an agent framework lets ZhiShi solve a concrete operational problem: reproducibility. A research harness gives the agent durable state — the environment snapshot it created, the hypothesis it is testing, the evidence it has collected — so a multi-hour binary-exploitation session does not evaporate between LLM turns. This is the same architectural idea behind agent harnesses in general software engineering, applied specifically to offensive security.

The project is young and moving fast. The repository was created 2026-08-18 and sat at roughly 69 stars and 4 forks as of 2026-08-28 (source: GitHub API). That is a rapidly growing new project, which cuts both ways: it signals real community interest but also means the codebase and claims should be treated as early-stage and subject to change.

## The 'Rust' question — Tauri shell vs TypeScript/Node core

The title's "Rust agent harness" requires a precise reality check. The Rust component is the desktop application shell, built with Tauri (`src-tauri`). The harness core — the loop engine, tool orchestration, environment management, and research memory — is TypeScript/Node, requiring Node.js >= 22.

This split is worth understanding before you invest time, because it shapes both deployment and extension. The Tauri shell provides the cross-platform GUI (React + zustand + xterm, with SSE for live streams) and a small Rust footprint for desktop integration. The actual security logic lives in the Node sidecar that exposes the admin API the GUI talks to.

| Layer | Technology | Role |
|-------|-----------|------|
| Desktop shell | Tauri (Rust) + React/zustand/xterm | GUI, terminal, SSE live streams |
| Sidecar / admin API | TypeScript / Node.js (>= 22) | Bridges GUI to loop engine |
| Loop engine | `@earendil-works/pi-agent-core` (MIT) + custom | Orchestrates agent turns, tools, state |
| LLM vendors | kimi, deepseek, openai, moonshot, Tongyi, Zhipu, SiliconFlow | Model inference with key management |
| Environments | Docker, VMware, Hyper-V, VirtualBox, SSH | Agent-owned exec sandboxes |

The practical consequence: if you want to extend the harness, you are mostly writing TypeScript, not Rust. The Rust is a shell, not the brains. Users coming for a Rust-native security tooling experience should set expectations accordingly — the Rust surface is real but comparatively thin.

## Core architecture: GUI, sidecar, loop engine, and LLM providers

The end-to-end data flow is: GUI (React + zustand + xterm, SSE) → sidecar (admin API) → self-built loop engine → LLM vendors → environment (Docker/VM/SSH) with a `research_events` memory store.

A notable architectural decision is building the loop engine on top of `@earendil-works/pi-agent-core` (MIT) rather than writing the transport, state management, and attachment handling from scratch. The project explicitly credits pi for these capabilities. This is a build-versus-buy decision worth evaluating: instead of reinventing a generic agent loop, ZhiShi reuses a battle-tested generic core and concentrates its effort on the security-specific layer — environment fusion, native code iteration, evidence tracking, and safety gates.

The core engine tools are deliberately minimal and general: `env_exec`, `env_bg` (for long-running background tasks like fuzzing), `delegate_task` (spawning sub-agents such as a crash-triager), `research_log`, `research_archive`, `request_decision`, and `declare_completion`. These map cleanly onto a security-research workflow: spawn a fuzzer in the background, delegate crash triage to a sub-agent, log hypotheses, archive evidence, and request a human decision when the agent leaves its approved scope.

LLM provider support is broad — eight built-in endpoints covering kimi, deepseek, openai, moonshot, Tongyi, Zhipu, and SiliconFlow — with key management and model switching. This matters for real use because different models are good at different parts of the research loop: a fast cheap model for routine env commands, a stronger model for exploit synthesis.

## The three pillars: environment fusion, native tools, native code

ZhiShi organizes its capability around three pillars, and the second and third are what distinguish it from a plain agent-plus-shell script.

Environment fusion means the agent owns the environment: it can create, run, snapshot, and roll back execution environments over Docker, VMware, Hyper-V, VirtualBox, and SSH targets. There are 7+ built-in environment recipes (dev, pwn, fuzz, rev, code-audit, pentest, ai-security, plus VM variants). The snapshot/rollback capability is critical for exploitation work — you can deliberately crash a target, inspect the crash, then restore a clean state and iterate.

Native tools means the harness discovers and uses tools already present in the target environment rather than bundling them. This keeps the attack surface aligned with a real target: the agent uses the gdb, pwntools, or fuzzer that a real researcher would actually reach for.

Native code means exploit, shellcode, and fuzz harnesses are compiled and iterated in-environment, not pre-written by the harness. The agent writes code, compiles it against the target's real toolchain, runs it, reads the result, and iterates. This is where the reproducibility value shows up: each iteration leaves state in the environment the agent controls.

## The research-archive dashboard and evidence-first memory model

A genuinely differentiated feature is the research-archive dashboard, laid out as a left stream / right archive split (roughly 6:4). It is structured memory built around the scientific method: hypotheses, evidence, conclusions, and open questions grow live as the session runs.

The evidence-first model is enforced with citations. Findings must cite V# evidence records, and when the agent falsifies or corrects a hypothesis it leaves an audit trail. This is an answer to one of the biggest problems in AI-assisted security research: the model confidently asserts a conclusion with no retrievable chain of evidence. ZhiShi's archive forces every conclusion to point back to concrete artifacts in the `research_events` store, making results auditable and, in principle, reproducible.

For security research specifically this is not a nicety — it is the difference between a claim you can defend and a claim you have to retract. A researcher taking a finding to a vendor (for a CVE filing) or to a client (for a pentest report) needs the evidence chain. The archive is designed to produce exactly that.

## Auto-loop research: budget, pause points, and human acceptance gates

ZhiShi's auto-loop agent lets a researcher launch a goal-directed research campaign with three locks set at the start: the goal, a budget, and an acceptance criteria. The budget bounds rounds, tokens, or time — a practical guardrail against the runaway-token problem that plagues long autonomous agent runs.

The loop runs with defined pause points. When the agent reaches a decision that falls outside its approved scope, or when it has assembled an acceptance package against the locked criteria, control returns to the human for a final sign-off. The system then produces an auto-generated report of what it did.

This human-in-the-loop design is the right call for offensive security and is worth highlighting as a model for other "autonomous" research tools. The acceptance package pattern — the agent gathers evidence that it has met the stated goal, and a human signs off — keeps the loop genuinely useful for exploratory research while preventing unbounded autonomous action. Budget locks plus human acceptance gates is a strong governance structure.

## Proven results: CTF clears, CVE reproductions, and whitebox findings

The project's credibility rests on published results, which is rarer than it should be in the "AI hacking" space. The README's 实战成果 (practical results) table reports:

| Target | Completion |
|--------|-----------|
| Pwnable.kr | 100% |
| Hacker101 CTF | 98% |
| HackThisSite | 96% |
| ROP Emporium | 91% |
| VulnHub | 90% |

Beyond CTF practice, ZhiShi claims real-world vulnerability research. The flagship is CVE-2026-34621 — Adobe Acrobat Reader prototype pollution, CVSS 8.6 — reproduced as a full end-to-end exploit chain from trigger to weaponization (source: CVE record + README). It also reports CVE-2026-0961 (Wireshark BLF file-parse crash / DoS, CVSS 5.5), the CVE-2025-1162/1163/1164/1170/1171 series, and a CVE-2026-66319 (Microsoft, pending). The broader pipeline claims 7 vulnerabilities in a Microsoft review queue and 200+ vulnerabilities from whitebox audits, with some filed to CVE, plus multiple Chrome and Firefox vulnerability analyses.

The Wireshark BLF case is a useful generalization test: it demonstrates the fuzz/crash-triage workflow, where the harness drives `env_bg` background fuzzing and a crash-triager sub-agent to find and reproduce parser crashes. This shows the harness moving beyond pwn/CTF into real-world bug hunting.

## Safety and dual-use: human-in-the-loop gates and legal authorization

Offensive tooling carries obvious dual-use tension, and ZhiShi does not ignore it. The architecture bakes in human-in-the-loop safety: rule hard-gates, output sanitization, and an out-of-scope human-approval modal that fires before the agent takes actions outside its declared scope. Combined with the acceptance-package sign-off, this means the harness is designed to keep a human accountable for consequential actions.

The licensing is a deliberate governance choice: AGPL-3.0. That is a strong copyleft license that discourages the kind of closed-source commercialization of offensive tooling that would be harder to audit. The README also carries a legal-authorization caveat, reminding users they are responsible for ensuring they have permission to test any target.

Responsible disclosure matters: the project reports findings to vendors and files to CVE rather than dumping 200+ vulnerabilities publicly without coordination. That is the professionally responsible pattern for vulnerability research, and it is worth noting as a positive signal about the project's intent.

## How ZhiShi compares to generic agent cores (pi) and other security agents

The cleanest way to think about ZhiShi is as a specialization: it takes a generic agent core (`@earendil-works/pi-agent-core`) and builds a domain-specific harness on top. A generic agent framework gives you transport, state, and tool calling; it does not give you environment snapshots, exploit compilation loops, or an evidence-cited research archive. ZhiShi's contribution is precisely that security-specific layer.

The tradeoff versus building your own loop from scratch is the familiar one: reusing pi gets you battle-tested transport and state management faster, but it also means ZhiShi's loop is constrained by pi's abstractions. For most users this is a good trade — you inherit stability and focus your effort on the domain logic that differentiates you.

Compared to other "AI pentest" or "AI hacking" tools of 2026, ZhiShi differentiates on evidence discipline and environment ownership rather than on raw autonomous capability. Many competitors demo an impressive single exploit; ZhiShi publishes completion percentages, reproduced CVEs, and an audit-trail archive. That is a meaningful credibility difference, even accounting for the fact that these are self-reported.

## Verification status and limits of self-reported claims

ZhiShi reports a strong internal verification story: 2370+ unit tests all green, with `tsc --noEmit`, `eslint`, and `depcruise` architecture checks at zero errors. It also mentions live dogfooding (ret2win, a three-domain 1.1.8 challenge, a cJSON four-round 1.4.6 run) and GUI end-to-end walkthroughs across versions 1.3.0–1.3.8.

These are meaningful signals of engineering rigor, but they are self-reported. An independent reviewer cannot fully verify the CTF percentages, the 200+ whitebox findings, or the Microsoft review queue from the public repository alone. The CVEs are verifiable — CVE-2026-34621 and CVE-2026-0961 are real published records — but the volume claims and completion percentages rest on the project's own accounting.

That is not a reason to dismiss the project; it is a reason to treat the headline numbers as claims to validate through your own runs rather than as independent benchmarks. The fact that some flagship results (the Adobe exploit) are externally verifiable via CVE records raises the confidence you can reasonably place in the rest, but it does not make the rest independently proven.

## Verdict: who should use ZhiShi and what to watch

ZhiShi is best suited to security researchers who want a reproducible, evidence-first harness for exploitation, pentest, code audit, or AI-security work — especially those who value the audit-trail archive and the human-in-the-loop safety gates over raw autonomous speed. The AGPL-3.0 license, Node-based extensibility, and broad LLM support make it approachable for researchers who already live in a TypeScript toolchain.

What to watch: the project is very new (created 2026-08-18), so the community, roadmap, and long-term maintenance are unproven. The "Rust" branding overstates the Rust surface — it is a Tauri shell over a Node core. And the most impressive claims are self-reported, so budget time to reproduce a few results before committing a serious research pipeline to it. On balance, ZhiShi is one of the more credible and better-governed offensive-security harnesses to appear in 2026, and it is worth a close look.

## FAQ

### Is ZhiShi actually written in Rust?

The desktop shell is Rust, via Tauri, but the harness core — loop engine, tools, environment management, and research memory — is TypeScript/Node (Node.js >= 22). Extending the harness means writing TypeScript, not Rust.

### What license is ZhiShi released under?

ZhiShi is AGPL-3.0 licensed, a strong copyleft license that allows use and modification while requiring derivative works to share the same license. It also carries a legal-authorization caveat about responsible use.

### What real vulnerabilities has ZhiShi reproduced?

Its flagship is CVE-2026-34621 (Adobe Acrobat Reader prototype pollution, CVSS 8.6), reproduced as an end-to-end exploit chain. It also reports CVE-2026-0961 (Wireshark BLF DoS) and a series of 2025-era CVEs, plus 200+ whitebox findings.

### What is the research-archive dashboard?

It is a structured-memory panel (left stream / right archive) where hypotheses, evidence, conclusions, and open questions grow live, with mandatory V# evidence citations. Falsified or corrected hypotheses leave an audit trail for reproducibility.

### Is ZhiShi a fully autonomous hacking tool?

No. ZhiShi frames itself as a human-in-the-loop harness. It enforces budget locks, pause points, out-of-scope human-approval modals, and a final human sign-off on auto-loop acceptance packages, keeping a human accountable for consequential actions.
