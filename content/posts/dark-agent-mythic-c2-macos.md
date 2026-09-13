---
title: "Dark-Agent: The Mythic C2 Agent With an In-Memory BOF Loader for macOS and Linux"
date: 2026-09-13T04:01:01+00:00
tags:
  - red-team
  - mythic
  - c2
  - bof
  - coff
  - macos
  - linux
  - servicenow
  - open-source
draft: false
description: "Dark-Agent is the first open-source Mythic C2 agent with a full in-memory BOF loader for macOS and Linux. Used by ServiceNow Red Team since 2024, it loads Beacon Object Files in-process with zero disk writes."
cover:
    image: "/images/dark-agent-mythic-c2-macos.png"
    alt: "Dark-Agent: Mythic C2 Agent With In-Memory BOF Loader for macOS/Linux"
    relative: false
schema: "schema-dark-agent-mythic-c2-macos"
---

Dark-Agent is the first open-source Mythic C2 agent with a full in-memory BOF (Beacon Object File / COFF) loader purpose-built for macOS and Linux. Written in Crystal, it loads Beacon Object Files entirely in memory — no disk writes, no temporary files, no child processes — and has been used operationally by the ServiceNow Red Team since 2024.

## What Is Dark-Agent? A Mythic C2 Agent Purpose-Built for Linux and macOS

Mythic is an open-source, cross-platform C2 (command-and-control) framework that makes it easy to extend an agent and swap in alternative C2 profiles without recompiling. Most of the well-known Mythic agents — Apollo, Xenon, Poseidon, and the Java-based options — either focus on Windows or treat Unix as a second-class citizen. Dark-Agent, released by ServiceNow under an open license, is built explicitly to change that.

The gap it fills is real. Red teams operating against Linux servers and macOS workstations have historically had fewer first-class implant options that support the same offensive tooling as their Windows counterparts. Beacon Object Files — compiled C programs designed for Cobalt Strike's Beacon — have an enormous existing ecosystem of tools and techniques. Dark's core contribution is bringing that full ecosystem to Unix platforms with proper in-memory execution.

## The Core Innovation: A Full In-Memory BOF Loader for Unix

The centerpiece of Dark-Agent is its in-memory BOF loader. A BOF, or Beacon Object File, is a compiled object file (PE/COFF or, on Unix, ELF) that gets loaded into a running process and executed without being written to disk. This is the same technique that made Cobalt Strike BOFs popular: small, flexible, and hard to detect as a file-based artifact.

What Dark does differently from every open-source Mythic agent before it is that this loader works natively on Linux (x86_64 and aarch64) and macOS (including Apple Silicon arm64). Previous agents either loaded BOFs only on Windows or required awkward workarounds on Unix. Dark's loader runs the BOF inside the agent's own process — there are no forked child processes, no memory-map files under /tmp, and no memfd-backed temp files.

According to the project's documentation, Dark ships 25 BOFs and 15 built-in commands out of the box. The minimal baked-in offensive capability is deliberate: the initial drop is essentially just a loader, and operators extend capability by pushing BOFs over the C2 channel.

## Under the Hood — How Dark Loads and Executes BOFs (bof_load / bof_list / bof_exec)

The BofRegistry workflow is the heart of the design. It is split into three clear commands, each mapped to a function in the agent:

- **bof_load** pulls a compiled object file (COFF on Windows-style BOFs, ELF on Unix) from the Mythic file store over the C2 channel, then registers the raw bytes in the BofRegistry. Critically, nothing is mapped to executable memory at this stage — the file is just stored as bytes in memory.
- **bof_list** shows which BOFs are currently loaded in the registry. This gives the operator a quick inventory of what is available without re-uploading.
- **bof_exec** actually fires the loader, mapping the registered bytes and executing the entry point. Because the BOF stays registered, it can be re-executed repeatedly without re-uploading the object — a workflow efficiency that operators value.

The entry point for any BOF is `coffee()`, which keeps things familiar for operators who already build BOFs for Cobalt Strike. Dark also ships a `beacon.h` boilerplate header so that existing BOF development habits carry over.

The isolation trade-off is worth noting. Because Dark executes BOFs in-process (no subprocess), a crash inside a BOF can take the whole agent down. That is a deliberate architectural choice favoring a lower footprint and less process-level noise — and it is the main thing to understand before trusting an unvetted BOF on a live engagement.

## Why macOS and Apple Silicon Matter

MacOS support is Dark-Agent's standout differentiator. Most C2 frameworks and agents either ignore macOS entirely or support only the Intel architecture. Dark explicitly targets Apple Silicon (arm64) alongside macOS x86-64, which matters because M-series Macs are now the default hardware across enterprise fleets.

The significance goes beyond "it runs on a Mac." Running a Beacon Object File, which was originally a Windows concept, natively in memory on Apple Silicon requires an ELF and architecture-appropriate loading path. Dark closes a gap that Poseidon and the Windows-focused agents left wide open: Linux and macOS operators can now use the same BOF tooling that Windows operators have enjoyed.

This is not theoretical. Apple Silicon Macs are common in sensitive environments — developers, executives, and security teams themselves — and a red team that cannot operate on them is operating with a blind spot.

## Platform Support and Build Matrix

Dark cross-compiles all four supported targets from a single Mythic Docker container:

- macOS arm64 (Apple Silicon)
- macOS x86-64 (Intel)
- Linux arm64 (aarch64)
- Linux x86_64

The agent is written in Crystal, which produces a single native binary with no runtime dependency on a garbage collector. It also statically links OpenSSL, so there is no libssl dependency to worry about on the target Linux host.

The build workflow is simple: `./build.sh -b` builds for Linux, and `./build.sh -B` builds for macOS aarch64 (this one requires Zig and a macOS SDK). Everything happens inside the standard Mythic Docker container, so the setup is reproducible and consistent with how most red teams already deploy Mythic.

## C2 Profiles, Encryption, and Malleable Traffic

Dark ships two C2 profiles: **HTTP** and **HTTPX**, the latter being Mythic's malleable profile format. The HTTPX configuration included in the repo is a working jQuery-based profile, which means operators can adopt realistic-looking web traffic rather than obviously synthetic beaconing.

Configuration options cover the usual operational concerns:

- **AES-256-CBC encryption toggle** for the traffic channel
- **Domain rotation** with round-robin or fail-over strategies, so a taken-over domain can be rotated out without rebuilding the agent
- **Transforms** such as base64 and URL encoding
- **Message placement** in HTTP headers, URL parameters, cookies, or the request body

These options matter because they let operators shape the agent's network footprint to blend with a target environment instead of advertising that a C2 connection is happening.

## The 25 BOFs and 15 Built-in Commands

Dark ships a curated set of BOFs and commands with MITRE ATT&CK mappings so operators can see exactly which technique they are exercising. The documented mappings include:

| Technique ID | Name | Example use in Dark |
| --- | --- | --- |
| T1059 | Command and Scripting Interpreter | Command execution via BOF |
| T1082 | System Information Discovery | Host/OS fingerprinting |
| T1070 | Indicator Removal on Host | Cleanup and log manipulation |
| T1129 | Shared Modules / BOF Execution | The in-memory BOF loader itself |
| T1033 | System Owner / User Discovery | Username and identity enumeration |
| T1016 | System Network Configuration Discovery | Network interface and IP discovery |

The full list totals 25 BOFs and 15 built-in commands. The point of shipping them pre-built is that an operator can get operational the moment the agent is installed, then extend with custom BOFs rather than baking more capability into the initial payload.

## Writing Your Own BOFs

Because Dark uses the familiar `coffee()` entry point and ships `beacon.h`, developers who have built BOFs for other platforms can adapt quickly. The project also integrates with **Forge**, Mythic's build tooling for generating BOFs, so the authoring pipeline is first-class within the ecosystem.

There is also a **direct mode**: you can build a standalone COFF loader to test a BOF locally without standing up a full Mythic server. This dramatically speeds up the development-and-test loop — iterate on the BOF, run it through the standalone loader, verify behavior, then push to the live agent.

## Dark vs. the Alternatives: Fawkes, Kassandra, Woopsie, Poseidon

To understand where Dark sits, it helps to compare it against the other active Mythic agents:

| Agent | Language | Platforms | BOF support | Key strength | Key limitation |
| --- | --- | --- | --- | --- | --- |
| **Dark-Agent** | Crystal | Linux + macOS | In-memory, native, in-process | First-class Unix BOF loader, Apple Silicon | In-process crash risk |
| **Fawkes** | Java | Win/Linux/macOS | Inline via Forge | 213 commands, broadest coverage | Bigger footprint, not Unix-first |
| **Kassandra** | — | Win/Linux/macOS | Isolated subprocess | Crash isolation protects agent | Subprocess spawn is noisier |
| **Woopsie** | Java | Win/Linux/macOS | Windows only | GraalVM Native Image, WebSocket | No Unix BOF support |
| **Poseidon** | Swift | macOS (mostly) | Limited | Apple-native feel | Not really a BOF loader |

The meaningful trade-offs are between Dark, Fawkes, and Kassandra. Fawkes is broader and carries more total commands, but spread across many platforms; Dark is deliberately lean and Unix-first with pre-built BOFs. Kassandra runs BOFs in an isolated subprocess, which protects the agent from a crashing BOF but adds a process-spawn footprint that Dark avoids by running in-process.

The right choice depends on the environment. If the target set is Windows-heavy, Fawkes or Apollo may be a better fit. If the engagement is Linux servers and macOS workstations — the exact segment Dark targets — the first-class, in-memory Unix BOF loader is the differentiator.

## Operational Provenance: ServiceNow Red Team Since 2024

Dark is not a hobby project. The ServiceNow Red Team has been using it operationally since 2024, well before the public open-source release. That is a meaningful signal: the loader has been exercised against modern defenses in real engagements, and the "on arrival" design is a product of that operational feedback.

The public release, with the repository created in August 2026 (gathering roughly 100 stars and 13 forks in its early days), carries an explicit intent from ServiceNow: let operators break it, open issues, write bad BOFs, and harden it through community use. It is already listed in the Mythic v4.0.0 community overview, signaling that the framework maintainers treat it as a first-class agent.

## Strengths and Honest Trade-offs

Strengths:

- **First Unix-native in-memory BOF loader** for Mythic, closing a real gap.
- **Operationally proven** by a real red team since 2024.
- **Stealth-lean design**: zero disk writes, no temp/memfd files, no child processes, BOFs run in-process.
- **Apple Silicon support**, which most agents ignore.
- **Static OpenSSL and Crystal's native binary**, meaning no libssl or runtime dependency on target.

Honest trade-offs:

- **In-process execution risk**: a crashing BOF kills the agent, unlike Kassandra's isolated subprocess.
- **Young public codebase**: the open-source release is recent (2026), so the community hardening is still early.
- **Lean by design**: only a loader ships, so operators must be comfortable pushing BOFs over the wire rather than relying on baked-in commands.
- **macOS build requires Zig + a macOS SDK**, a slightly heavier dependency for the Apple Silicon target.

## How to Get Started

Getting Dark running follows the standard Mythic agent flow: install the agent into your Mythic server (for example via the mythicmeta community overview or building the Docker image from the repo), cross-compile your four targets with `./build.sh`, and drop the binary on the target. Then `bof_load` your compiled BOFs over the C2 channel, confirm with `bof_list`, and execute with `bof_exec`.

For development, use direct mode with the standalone COFF loader to test BOFs locally against a mock harness before you ever touch a live server.

## Key Takeaways for Red Teams

If your engagements touch Linux or macOS — and most modern ones do — Dark-Agent is worth evaluating. It brings the mature BOF ecosystem to Unix for the first time as a first-class, in-process, in-memory loader, with operational provenance from ServiceNow's own red team and a working, hardened design philosophy. The Apple Silicon support alone puts it ahead of most alternatives for enterprise Mac fleets, and the lean payload philosophy means the compromise surface of the initial drop stays small.

Weigh the in-process crash risk against the footprint benefits, pick the environments where a Unix-first loader matters, and Dark becomes a legitimate new tool in the red-team arsenal.

## FAQ

### What is a BOF (Beacon Object File) loader?
A Beacon Object File is a compiled C object file (COFF on Windows-style tooling, ELF on Unix) that a C2 agent maps into memory and executes without writing it to disk. A BOF loader is the code that performs that in-memory execution, letting operators run small, flexible post-exploitation tools that leave no file-based artifact.

### Why is Dark-Agent significant for macOS and Linux?
Dark-Agent is the first open-source Mythic C2 agent with a full, native in-memory BOF loader for macOS (including Apple Silicon) and Linux. Previously, full BOF loading was largely a Windows capability, forcing Unix-focused red teams to work around the gap.

### Is Dark-Agent production-grade or experimental?
It is operationally proven. The ServiceNow Red Team has used Dark since 2024 in real engagements, and the public open-source release in August 2026 is an explicit invitation to harden it further. It is listed in the Mythic v4.0.0 community overview as a first-class agent.

### What are the main trade-offs of running BOFs in-process?
Executing BOFs in-process means no child processes and zero disk/process-spawn footprint, which reduces observability. The trade-off is that a crashing BOF can kill the entire agent, whereas an agent like Kassandra that runs BOFs in an isolated subprocess protects the agent at the cost of a larger footprint.

### How do I test a BOF without a full Mythic server?
Dark offers a direct/standalone mode where you build a standalone COFF loader and execute a BOF locally. This lets you iterate on a BOF, verify its behavior, and only then push validated BOFs to a live agent over the C2 channel.
