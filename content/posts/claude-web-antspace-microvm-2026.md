---
title: "Reverse-Engineering Claude Web's Hidden Antspace MicroVM: What Firecracker Isolation Tells Us"
date: 2026-09-21T22:01:20+00:00
tags:
  - Claude Web microVM
  - Claude Code Antspace
  - Firecracker microVM
  - reverse engineering
  - Anthropic
  - agent sandbox
description: Claude Code Web runs each session in a Firecracker microVM on Anthropic's undocumented Antspace platform. Here's how the architecture was reverse-engineered, layer by layer.
draft: false
cover:
  image: "/images/claude-web-antspace-microvm-2026.png"
  alt: "Reverse-Engineering Claude Web's Hidden Antspace MicroVM"
  relative: false
schema: "schema-claude-web-antspace-microvm-2026"
---

Every Claude Code Web session you run doesn't execute on a shared server — it boots inside a dedicated Firecracker microVM managed by an undocumented Anthropic platform codenamed Antspace. That is the finding that emerged in March 2026 when developer AprilNEA ran a single `strace -p 1` command inside a Claude Code Web sandbox and exposed a five-layer architecture: a Firecracker microVM, an unstripped 27MB Go runner binary, a Rust process supervisor, a mature but completely undocumented deployment PaaS, and a web-app builder codenamed Baku. This post walks through how the discovery was made, what each layer reveals, and why it changes how you should think about isolating your own agent workloads.

## What a casual `strace -p 1` uncovered inside Claude Code Web

The entire investigation began with a single tool and a single process. AprilNEA attached `strace` to process ID 1 inside a Claude Code Web sandbox session. What looked like a normal container turned out to be something far more interesting. Instead of a generic container runtime, PID 1 was a custom binary named `environment-runner`, and the system underneath it was a full hardware-virtualized microVM — not a shared kernel container.

That one strace exposed three things immediately: the host ACPI tables carried a tell-tale OEM ID, the runner was an unstripped Go binary leaking Anthropic's internal package names, and a second binary called `process_api` was acting as a supervisor for spawned processes. This wasn't a hobbyist misconfiguration. It was the outward face of a product Anthropic had never publicly documented.

## Layer 1 — Fingerprinting the Firecracker MicroVM via ACPI FIRECK and FCAT

The first layer is the compute substrate. By reading the ACPI tables inside the session, the researcher found the OEM ID `FIRECK` and the creator ID `FCAT`. These are the fingerprints of Amazon's Firecracker, the open-source microVM technology that powers AWS Lambda and Fargate. Anthropic is not running its own hypervisor; it is orchestrating Firecracker, the same virtualization layer that already handles millions of AWS serverless functions.

A detailed inspection of the session confirmed the scale of this isolation. The Claude Code Web session ran a 4 vCPU Intel Xeon Cascade Lake machine at 2.80 GHz, with 16GB of RAM and a 252GB disk, on Linux kernel 6.18.5. In other words, each coding session gets a private, purpose-built VM — full hardware isolation between tenants rather than the process-isolated containers most agent platforms use.

The practical implication is significant. Firecracker boots in milliseconds and allocates as little as 5MB of memory overhead beyond the guest, which is precisely why it is the default for high-churn, per-request computing like serverless. Anthropic choosing it for agent sessions signals that it treats every Claude Code session like a short-lived, disposable unit of compute.

## Layer 2 — The unstripped Go binary and Anthropic's internal package tree

The second layer is the executable that actually initializes the environment. The `environment-runner` binary is a 27MB unstripped Go binary built with full debug symbols, and it was shipped to production without stripping. That single oversight is what made the entire architecture recoverable.

With debug symbols intact, the researcher could use `go version -m` and symbol-table greps to read Anthropic's internal package structure directly out of the binary. It was built from `github.com/anthropics/anthropic/api-go/environment-manager/`, giving away internal repo naming and a wealth of untagged structs and functions.

The lesson is a standing warning for any team shipping agent runtimes: stripping binaries is not an afterthought. Anthropic's entire internal architecture leaked because a Go binary hit production without `-ldflags="-s -w"`. If you build a sandbox or agent runner, strip symbols, obfuscate where practical, and treat the compiled artifact as a source of intelligence rather than a black box — because your competitors and curious engineers will.

## Layer 3 — Antspace: Anthropic's undocumented deployment platform

The third layer is the most consequential finding: Antspace. Reading the decompiled client code reveals Antspace is an Anthropic PaaS that lets users deploy code to the cloud. Its deployment protocol is mature — three phases: create a deployment, upload a build artifact, and stream deployment status over `application/x-ndjson`. File upload is a single tar.gz archive, unlike Vercel's SHA-deduplication per file.

Remarkably, Antspace has zero public documentation. A search across Anthropic's site, GitHub, blog, docs, LinkedIn, job postings, conference talks, and patents returned nothing, and the version string was prefixed `staging-`. The protocol is fully developed and shipping, yet nothing about it is discoverable publicly. This strongly suggests it is real internal infrastructure that was pulled in to production to serve Claude Code Web before any formal product announcement.

## Layer 4 — Baku, the claude.ai web app builder, and its Supabase backend

The fourth layer ties Antspace to the broader Anthropic ecosystem. Baku is the internal codename for the claude.ai web app builder. The decompiled binaries show it uses a Vite + React + TypeScript template with a supervisord dev server. When you ask Claude to build a web app, Baku auto-provisions a Supabase backend through six built-in MCP tools.

The commercial implication is direct: Baku's default deploy target is Antspace, not Vercel. Vercel is only an alternative. That means Anthropic has quietly built a fully vertical pipeline — intent → Claude → Baku → Supabase → Antspace → live app — where the user never leaves Anthropic's ecosystem. This reframes Anthropic as a platform competitor and not merely a model provider.

## Layer 5 — BYOC: bringing your own cloud

The fifth layer is enterprise-oriented. The decompiled code contains an `envtype/byoc` package that implements bring-your-own-cloud (BYOC). This lets enterprises run `environment-runner` on their own infrastructure while Anthropic API continues to orchestrate. For regulated, hybrid-cloud, or compliance-heavy buyers, this is the control point: you keep the agents' execution substrate inside your own trust boundary while Anthropic manages the orchestration layer.

BYOC explains how Anthropic reconciles delivering cloud compute with enterprise data-sovereignty demands. Rather than forcing every customer onto its own Firecracker fleet, it offers a deployment mode where the runtime stays behind your firewall.

## The Snapstart pattern: how sessions boot in under 30ms

None of this would be usable for interactive coding if every session required a full VM cold boot. Fast VM boots are the difference between a responsive coding loop and a waiting-to-answer lag. Anthropic solves this with a pattern it calls Snapstart.

Instead of booting a fresh VM and installing the runtime per session, the system boots a template once, freezes it, and restores it from a snapshot. The session's `dmesg` showed a 48.5-hour gap between the template boot and the actual session restore, and the ext4 rootfs mount count was 11 — meaning the same rootfs image had been reused across 11 sessions. Block devices are hot-swapped at restore time. This deferred-mount pattern achieves near-instant session restoration, far faster than a traditional multi-gigabyte VM boot.

Snapstart matters because cold-start latency is the hidden cost of per-session isolation. Snapshot/restore trades a larger upfront boot for a near-zero subsequent boot, and it is the pattern any platform building disposable agent environments should replicate.

## process_api: the remote process supervisor wire protocol

Inside the microVM, `process_api` is the 3.1MB Rust/tokio binary that runs as PID 1 — the init and supervisor for anything the coding agent spawns. Decompiled via Ghidra, it became 3,599 functions and roughly 446,000 lines of C pseudocode. Its modules reveal the full lifecycle: `firecracker_init`, `control_server`, `cgroup`, `oom_killer`, `proc_handle`, `state`, and `adopter`.

The host talks to it over a WebSocket wire protocol. Authentication uses JWT, then a `ProcessConnection` handshake establishes a session for `CreateProcess`. From there, stdin/stdout/stderr are carried in binary framing, and the client can send `SendSignal`, `Resize`, `Detach`, and `KeepAlive` messages. A separate HTTP control API on port 2025 exposes `/status`, `/fs_sync`, `/shutdown`, `/auth_public_key`, `/mount_root` (the snapstart path), and `/container_name`. Disks are laid out as three block devices: `vda` is an ext4 read-write rootfs, `vdb` a squashfs containing the Claude Code binary, and `vdc` a squashfs for the environment runner.

## Security hardening: init_on_free, CAP_SYS_RESOURCE, CRNG reseed, localhost blocking

For a product that would worry security reviewers, Antspace shows deliberate hardening. The guest enables `init_on_free`, which zeroes freed memory pages to make cold-boot and memory-extraction attacks harder. It drops `CAP_SYS_RESOURCE` after initialization so a compromised process cannot exhaust host or container resources. On snapshot restore it reseeds the CRNG so the restored VM cannot reuse a stale random state across sessions. And it passes `--block-local-connections` to prevent the coding agent from probing other tenants' local network services.

It is worth restating what this is not: no exploit was demonstrated, and no privilege escalation was found. This is standard operating-system introspection of an unstripped binary. The security story is hardening best practice you can crib for your own agent sandboxes — not a vulnerability disclosure.

## A reusable reverse-engineering methodology: the exact commands

The value of the AprilNEA writeup is that the technique is fully reusable. If you want to find out what really runs inside a sandboxed agent environment, this is the cookbook:

- `strace -p 1` on the init process to see system calls and hint at the supervisor.
- `dmesg | grep FIRECK` and check ACPI tables for the OEM ID `FIRECK` and creator ID `FCAT` to fingerprint a Firecracker microVM.
- `cat /proc/1/cmdline` to see how PID 1 was invoked.
- `go version -m` on any Go binary to read embedded build and module metadata.
- `objdump -t` and symbol-table greps against unstripped binaries to map out internal package and function names.
- Pull the binary to disk and run Ghidra for full decompilation of native supervisors.

These steps turn an opaque sandbox into a documented architecture in an afternoon, and they apply to any agent platform that ships binaries into customer-visible sessions.

## Why this matters for AI platform builders

The aggregate picture is that Firecracker-based microVM sandboxes are becoming the default infrastructure layer for serious coding-agent platforms. Anthropic is not experimenting; it built a deployment protocol, a web-app builder, a BYOC escape hatch, and a snapshot-restore runtime around it. The engineering discipline — full hardware isolation, near-instant restores, hardened memory handling — sets a new baseline for what users should expect from an agent platform.

For competitors and startups, Antspace demonstrates the endgame: a vertical pipeline where an AI handles intent and delivery, and the user never leaves the platform. Whether or not Antspace ever launches publicly, the architecture is the blueprint.

## What it means for you: isolating your own agent sandboxes

If you are building agents that can execute code, untrusted or not, the concrete takeaways are: give each session hardware isolation via Firecracker or similar rather than process-level containers, use snapshot/restore to hide the boot cost, strip symbols before shipping any runtime binary, zero freed memory and drop dangerous capabilities, and reseed entropy on restore. Most importantly, decide up front whether you will host the runtime or let enterprises bring their own cloud — because BYOC is fast becoming a purchase requirement, not a nice-to-have.

## FAQ

**Is the Antspace MicroVM a real security vulnerability in Claude Web?**
No. The investigation found no exploit, no privilege escalation, and no data-leak bug. It is introspection of an unstripped binary and standard OS-level inspection, not a vulnerability disclosure.

**What does the FIRECK ACPI fingerprint prove?**
The ACPI OEM ID `FIRECK` and creator ID `FCAT` identify the session as a Firecracker microVM — the same technology powering AWS Lambda and Fargate. It proves Anthropic uses hardware virtualization, not just container isolation, for Claude Code Web sessions.

**Why is Antspace undocumented if it ships in production?**
Antspace has zero public documentation across Anthropic's site, GitHub, docs, and job postings, and its version string is prefixed `staging-`. It appears to be real internal infrastructure that got pressed into production to serve Claude Code Web before any formal product announcement.

**How does a Claude Code session boot in under 30ms?**
It uses a Snapstart-style snapshot/restore pattern. A template VM boots once, freezes, and resumes from snapshot with block devices hot-swapped at restore. `dmesg` showed a 48.5-hour gap between template boot and session restore, and a rootfs reused across 11 sessions.

**Can I isolate my own agent workloads this way?**
Yes. The same stack — Firecracker for hardware isolation, snapshot/restore for fast boot, symbol stripping, hardened memory init, and capability dropping — is available to any team and is increasingly the baseline for serious agent platforms.
