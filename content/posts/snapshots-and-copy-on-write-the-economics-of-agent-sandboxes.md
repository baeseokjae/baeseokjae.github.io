---
title: "Snapshots and Copy-on-Write: The Economics of Agent Sandboxes"
date: 2026-08-16T22:01:20+00:00
tags:
  - AI agents
  - sandboxing
  - Firecracker
  - copy-on-write
  - infrastructure
  - cost optimization
description: "Agent sandbox costs explode when you size for requested resources. Snapshots and copy-on-write let you pay for divergence, not the whole VM."
draft: false
cover:
  image: "/images/snapshots-and-copy-on-write-the-economics-of-agent-sandboxes.png"
  alt: "Snapshots and Copy-on-Write: The Economics of Agent Sandboxes"
  relative: false
schema: "schema-snapshots-and-copy-on-write-the-economics-of-agent-sandboxes"
---

Agent sandboxes get expensive because most platforms size them for the resources an agent *requests*, not the resources it actually *uses*. Snapshots and copy-on-write flip that equation: instead of paying for a full 128 GiB disk and 16 GiB of RAM per session, you pay only for the base image plus the small set of divergences each agent creates. The result is a cost model that scales with real usage, letting a single host run dozens of isolated agents instead of a handful.

## Why Agent Sandboxes Get Expensive Fast

An AI coding agent is a program that runs commands you did not write. It can `rm -rf` a directory, exfiltrate credentials, or install a malicious package — and because you cannot predict every command, you cannot safely run it on your own machine. The industry answer is to give each agent its own throwaway Linux box with strict egress policies, treating every agent as potentially adversarial and eliminating the blast radius.

The problem is that isolation is not free. A freshly booted Firecracker microVM is a sealed box with no screen, keyboard, or network until you wire it up — but a minimal microVM is not a minimal workload. Once a compiler, language server, browser, and build daemon start inside a 4 GiB guest, that guest can pull several GiB of pages into host RAM. Copying a 40 GiB ext4 image for every agent is absurd when most agents change only a few files.

The naive cost model is brutal. If you size each sandbox for peak requested resources, a single host saturates its vCPU, RAM, and disk after only 9 to 24 parallel agents. That is the core economic problem: **you are paying for the worst case of every session, even though most sessions touch only a handful of files and a fraction of their memory.**

## The Naive Approach: Full Snapshots and Why They Fail

The obvious fix is snapshots. Firecracker can serialize its vCPU, KVM, and device state into a `state.bin`, guest memory into a `mem.bin`, and the disk as a file. Combined, that gives you full state recovery — memory, disk, and processes — which is exactly what you need for long-lived sessions you resume months later.

But combined snapshots are massive. A sandbox with 16 GiB of requested RAM and 128 GiB of requested disk produces a worst-case full snapshot of roughly 144 GiB. Storing, transferring, and restoring that per session is not viable at fleet scale. The snapshot approach only works if you can avoid materializing the full state for every agent.

This is why the ephemeral one-shot contract — the CI-style model Stripe popularized — does not fit every use case. A CI job runs, finishes, and dies. A harness-agnostic long-lived agent session may resume weeks or months later and needs its full state back. The economics of full snapshots break precisely when you need persistence at scale.

## Content-Addressable Storage: Turning a 128 GiB Disk into a Manifest

The breakthrough is to stop treating each sandbox's disk as an independent 128 GiB blob and start treating it as a manifest of shared, immutable chunks. Cortex's approach splits the disk into fixed 16 MiB chunks, hashes each with SHA-256, and stores them in a content-addressable store.

The math is the payoff. Identical chunks are stored once across all sandboxes, and zeroed chunks are skipped entirely. A manifest maps each disk offset to a chunk hash. When an agent boots, it reads the manifest and fetches only the chunks it actually touches. A session that dirties 20 chunks adds at most 320 MiB of new disk data — even on a 128 GiB virtual disk.

An NBD (Network Block Device) server bridges this content-addressed storage to Firecracker. Reads fetch chunks on demand, and an NVMe device acts as an LRU hot-chunk cache so frequently accessed chunks stay in fast storage. The disk you *requested* and the disk you *pay for* are now completely different numbers.

## Copy-on-Write: One Write, One New Chunk

Content addressing handles the read path, but writes still need a strategy. Copy-on-write (CoW) is that strategy. The first write to an immutable base chunk creates a private dirty copy; the base chunk stays shared and untouched. One write equals one new chunk.

This is the same idea behind filesystem snapshots and database MVCC, applied at the block level. Because base chunks are immutable, they can be shared safely across thousands of sandboxes with no locking. Because dirty chunks are private, each agent's divergences are isolated and cheap.

The economics are dramatic. A fleet of 1,000 sandboxes sharing a 40 GiB base image stores that base once, not 1,000 times. Each sandbox's incremental cost is proportional to the chunks it actually dirties — typically a few hundred MiB, not tens of GiB. Copy-on-write turns the disk from a per-session liability into a shared, amortized asset.

## The Harder Problem: Memory (MAP_PRIVATE and userfaultfd)

Disk has a clean boundary — the NBD server resolves reads — but memory does not. You cannot route every guest memory read through a server without destroying performance. Memory deduplication is the harder problem, and it requires kernel cooperation.

Cortex's approach content-addresses memory in 512 KiB chunks. The base shared memory file is mapped with `MAP_PRIVATE`, so clean pages share the page-cache backing across all sandboxes, while writes get private pages via the kernel's native copy-on-write. `userfaultfd` fills the sparse base shared-memory file on demand, and `UFFDIO_CONTINUE` preserves sharing for pages that are still clean.

The result is that memory cost follows the same logic as disk: you pay for the base shared memory plus the dirty RAM each session actually writes, not the full requested footprint. A 16 GiB sandbox that only dirties a few hundred MiB of pages costs a few hundred MiB of private memory, with the rest shared across the fleet.

## From Resource Density to Session Density

The second lever is time. Agents spend most of their time waiting — on humans, on network calls, on external tools — not computing. Sizing every retained session for peak active work is wasteful.

The fix is to capture idle sandboxes and evict them. Because snapshots are now cheap (a manifest plus a small set of dirty chunks), you can snapshot an idle sandbox, free its host resources, and restore it on demand when the agent wakes up. The autoscaler removes empty hosts entirely.

This shifts the metric from *resource density* to *session density*. You size for active work, not for every retained session. A host that could only run 9 to 24 peak-sized sandboxes can now hold hundreds of sessions, most of them snapshotted and idle, with only the active ones consuming real vCPU, RAM, and disk.

## The New Cost Model: Pay for Divergence, Not the Whole VM

Putting it together, the cost model transforms. The old model was:

> cost ∝ requested (vCPU + RAM + disk)

The new model is:

> cost ∝ α·vCPU + β·(base shared memory + dirty RAM) + γ·(base disk + dirty disk)

The first term is unavoidable — you pay for the compute an agent actually uses. The second and third terms collapse because base memory and base disk are shared across the fleet, and dirty memory and dirty disk are proportional to real divergence. You pay for what an agent *uses and changes*, not for what it *requests*.

This is the core economic insight of modern agent sandboxing: **pay for divergence, not for the whole VM.** It is what makes running thousands of isolated agents on a single machine economically sane.

## Isolation Is a Spectrum: Choosing the Right Sandbox Layer

Not every workload needs a microVM. Isolation is a spectrum with five levels:

| Level | Technology | Best for | Boot time / overhead |
|-------|-----------|----------|----------------------|
| Containers | runc, Docker | Internal, trusted code | ~ms, minimal |
| User-space kernels | gVisor | LLM-generated code | ~ms, moderate |
| MicroVMs | Firecracker, Kata, libkrun | Untrusted code, multi-tenant | ~125ms, ~5MB |
| Library OS | LiteBox | Minimal attack surface | ~ms, low |
| Confidential computing | AMD SEV-SNP, Intel TDX | Hostile tenants, compliance | higher |

Firecracker boots in about 125ms with roughly 5MB of memory overhead, which is why it powers AWS Lambda, E2B, and Vercel Sandbox. The right choice depends on trust, latency, data sensitivity, and compliance. Internal code is fine in containers; LLM-generated code warrants gVisor or microVMs; user-uploaded binaries should be treated as hostile and run under hardware virtualization.

The hyperscaler signal is unambiguous. AWS built Firecracker for Lambda, Google built gVisor for Search and Gmail, and Azure uses Hyper-V for ephemeral agent sandboxes. Every major cloud built its strongest isolation primitive and pointed it at AI — none reached for plain containers. AWS, Azure, and GCP have all quietly migrated their control planes away from runc toward hardware-enforced isolation.

## Local vs Remote Sandboxing: Two Different Problems

Sandboxing agents is really two problems with different threat models. A local sandbox on a developer machine faces the *confused deputy* risk: prompt injection, poisoned MCP context, and hallucination. The controls are workspace boundaries, secret isolation, network egress policy, and visibility or reversibility.

A remote, multi-tenant sandbox faces *adversarial workloads*: a tenant who is actively trying to break out. The controls are isolation boundaries with defense in depth, no secrets inside the sandbox, egress as a chokepoint, resource and cost governance, and ephemerality.

One warning applies to both: a sandbox that is too annoying gets disabled, which is worse than no sandbox at all because it creates a false sense of security. Remote sandboxing is ultimately about ensuring that bad behavior cannot become a systemic incident.

## Key Takeaways for Building Cost-Efficient Agent Sandboxes

- **Size for usage, not requests.** Content-addressable storage and copy-on-write let you pay for divergence instead of the whole VM.
- **Share the base.** Identical chunks and clean memory pages are stored once across the fleet, not once per sandbox.
- **Treat memory as the hard problem.** Disk has an NBD boundary; memory needs `MAP_PRIVATE` and `userfaultfd` to keep clean pages shared.
- **Snapshot and evict idle sessions.** Agents wait more than they compute; size for active work, not every retained session.
- **Match isolation to trust.** Containers for internal code, microVMs for untrusted code, hardware virtualization for hostile tenants.
- **Follow the hyperscalers.** Every major cloud built a hardware-enforced isolation primitive for AI — none settled for containers.

## FAQ

**What is copy-on-write in an agent sandbox?**
Copy-on-write means the first write to an immutable base chunk creates a private dirty copy while the base stays shared. One write equals one new chunk, so each sandbox's incremental disk cost is proportional to the chunks it actually changes, not the full virtual disk size.

**Why are full microVM snapshots impractical at scale?**
A full snapshot serializes vCPU, KVM, device state, guest memory, and disk. A sandbox with 16 GiB of RAM and 128 GiB of disk produces a worst-case snapshot of roughly 144 GiB, which is too large to store, transfer, and restore per session across a large fleet.

**How does content-addressable storage reduce sandbox cost?**
The disk is split into fixed 16 MiB chunks, each hashed with SHA-256. Identical chunks are stored once across all sandboxes and zeroed chunks are skipped. A manifest maps offsets to hashes, so a session that dirties 20 chunks adds at most 320 MiB even on a 128 GiB virtual disk.

**What is the difference between resource density and session density?**
Resource density counts how many peak-sized sandboxes fit on a host (typically 9 to 24). Session density counts how many sessions a host can hold when idle ones are snapshotted and evicted. Because agents spend most time waiting, sizing for active work lets a host hold hundreds of sessions.

**Which sandbox isolation level should I use?**
It depends on trust. Containers are fine for internal, trusted code. LLM-generated code warrants gVisor or microVMs. User-uploaded binaries should be treated as hostile and run under hardware virtualization like Firecracker, Kata, or confidential computing. Firecracker boots in about 125ms with roughly 5MB of overhead.
