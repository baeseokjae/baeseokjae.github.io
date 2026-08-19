---
title: "Machine0 VMs Review: Persistent CPU and GPU VMs From the CLI"
date: 2026-08-19T16:02:00+00:00
tags: ["machine0", "agent vm", "persistent gpu vm", "cli vm", "nixos", "yc s26"]
description: "Machine0 is a YC S26 CLI-first cloud for persistent CPU and GPU VMs with static IPs, per-minute billing, and NixOS reproducibility. Here's how it compares to Modal and E2B."
draft: false
cover:
    image: "/images/machine0-persistent-cpu-gpu-vms.png"
    alt: "Machine0 VMs Review: Persistent CPU and GPU VMs From the CLI"
    relative: false
schema: "schema-machine0-persistent-cpu-gpu-vms"
---

Machine0 is a Y Combinator Summer 2026 startup that gives you persistent CPU and GPU virtual machines controlled entirely from the command line. Unlike ephemeral serverless sandboxes such as Modal or E2B, every Machine0 VM is a full machine you own—with root access, your own drivers and CUDA stack, a static public IP, an HTTPS endpoint, and per-minute billing that stops the moment you suspend it.

## What Is Machine0? Persistent CPU & GPU VMs for Agents

Machine0 markets itself as an "agent-first cloud." Instead of renting a server through a web console or juggling Terraform files, you provision, manage, and destroy virtual machines entirely through CLI commands, each of which supports a `--json` output flag for scripting and agent orchestration. The core pitch is that this is not a sandbox: it is a persistent virtual machine that an AI agent (or a human developer) actually owns.

Founded as a Y Combinator Summer 2026 (YC S26) company, Machine0 runs on top of DigitalOcean infrastructure, with bring-your-own-cloud (BYOC) explicitly on the roadmap. The service ships NixOS or Ubuntu images across five regions—US East, US West, UK, EU, and Asia—and advertises a 99.99% uptime target. The entire platform is designed around one workflow: type a command, get a machine, point an agent at it, and let the agent work.

## Key Features — CLI-First, MCP, Static IPs, Suspend & Snapshot

### CLI-First Workflow With JSON Output

Every operation is a CLI command that returns machine-readable JSON. That design choice matters for two audiences. For humans, it makes provisioning scriptable and composable with standard Unix tools. For agents, it means a language model can create, resize, snapshot, and delete VMs without any web UI in the loop. The `--json` flag is not an afterthought; it is the contract the whole product is built around.

### Remote MCP Server for Agent Orchestration

Machine0 ships a remote Model Context Protocol (MCP) server. MCP is the emerging standard that lets AI tools like Claude Code and Codex reach external systems. With a remote MCP server, an agent can treat your VM fleet as a first-class tool: spin up a machine, run code on it, pull results, and tear it down—all through structured tool calls rather than raw shell prompts.

### Static IPs and HTTPS Endpoints by Default

Each VM receives its own static public IP and an HTTPS endpoint at `<vm>.mac0.io` with no NAT or tunnels. For agent-driven workloads this is a meaningful convenience: no reverse-proxy gymnastics, no ngrok session, no port-forwarding dance. The static IP is retained for as long as the VM exists, and it is lost only when the VM is deleted. This persistence is a deliberate part of the pricing model (more on that below).

### Suspend to Stop Billing, Snapshots, and Golden Images

A headline feature is suspend: you can pause a VM to stop compute billing entirely. While suspended, you pay only for image storage at $0.078 per GB per month. Combined with snapshots and the ability to turn any VM into a reusable "golden image," this gives you the economics of an on-demand service without losing the state of a persistent machine. You are effectively renting reserved capacity only when you actually need it running.

### Profiles Inject Credentials, MCP Servers, Prompts, and Env Vars

Machine0 "profiles" let you bundle MCP servers, credentials, prompts, and environment variables into a VM. The clever part is how these are consumed: OAuth token refresh happens inside the profile, and Claude Code and Codex pick the injected configuration up automatically. Credentials can be pulled and rotated, then re-injected without rebuilding the machine. This directly attacks the biggest friction in agent fleets—managing per-agent secrets and tool configuration.

## Machine0 vs Modal vs E2B: Persistent VM vs Ephemeral Sandbox

The sharpest way to understand Machine0 is contrast it with the serverless sandbox category. Modal and E2B are the representative players.

| Dimension | Machine0 (persistent VM) | Modal / E2B (ephemeral sandbox) |
|-----------|--------------------------|----------------------------------|
| Machine ownership | Full VM you own (root) | Sandboxed, no root |
| Kernel & drivers | Your own kernel, drivers, CUDA | Shared runtime; no own drivers/CUDA |
| GPU access | Fixed GPU per size, passed straight through | Ephemeral GPU assignment |
| State persistence | Persists until you delete it | Ephemeral by design; state lost between runs |
| Static IP / endpoint | Static IP + HTTPS `<vm>.mac0.io` | No static public IP |
| Billing | Per-minute; suspend stops compute billing | Per-invocation / per-second serverless |
| Use case sweet spot | Agent fleets, training, agentic backends | Bursty, stateless serverless functions |

The distinction the founders emphasize is that Machine0 is not a cheaper sandbox; it is a different category. In their words from the Launch HN thread, a Machine0 VM is a persistent machine you own—root access, your own drivers, your own CUDA, your own kernel—with the GPU passed straight through. A Modal sandbox is an ephemeral compute environment you borrow for the duration of a task.

This has real consequences. If you need to install a custom driver, run your own kernel modules, pin a specific CUDA version, or keep state alive across many agent interactions over hours or days, a persistent VM is the natural fit. If you need to run a burst of stateless GPU functions and nothing more, an ephemeral sandbox is cheaper and simpler.

## NixOS Reproducibility & the Drift-Free Promise

One of Machine0's most interesting differentiators is its default NixOS images built around flakes. A NixOS flake is a declarative specification of the entire system—packages, services, users, config. Machine0 lets you point a VM at a flake and have it provisioned reproducibly. The community reception on the Show HN thread was emphatic on this point: state drift becomes impossible because you cannot modify a VM outside the flake.

This is a meaningful moat against config-drift clouds. In a traditional Ubuntu or Rocky box managed by hand or with Ansible, the running system slowly diverges from the source of truth. With a flake, the machine is either the flake or it is not—and the flake itself is portable to any NixOS provider. Several commenters noted this makes the "exe.dev plus Nix value-add" proposition genuinely compelling.

The flip side is a learning curve. NixOS is notoriously different from conventional Linux administration. The counterargument, raised in the same thread, is that agents change the calculus: you do not need to memorize Nix syntax when you can simply point an agent at a VM and say "make a machine that does X," letting it write the flake and iterate. For agent-first users, the declarative model is a feature, not a tax.

Ubuntu images are also available, preinstalled with Docker, Node, Python, Claude Code, and Codex, for users who prefer a familiar environment.

## Machine0 Pricing & Cost Model (CPU and GPU Tiers)

Machine0 uses per-minute billing with a minimum $5 top-up and unused credits refundable. CPU VMs start at $0.013 per hour (roughly $9 per month for the smallest 1 vCPU / 1 GB size) and scale up to a 6xl instance with 60 vCPUs and 240 GB RAM at $3.714 per hour (about $2,711 per month). The full CPU range spans these extremes.

GPU VMs start at $0.836 per hour for a single RTX 4000 Ada (about $610 per month) and scale to an 8x H200 configuration with 1,128 GB of VRAM at $39.336 per hour (roughly $28,715 per month). Available GPUs include H100, H200, L40S, MI300X, and RTX 4000/6000 Ada.

| Tier | Config | Hourly | Approx. monthly (always-on) |
|------|--------|--------|------------------------------|
| CPU | 1 vCPU / 1 GB | $0.013 | ~$9 |
| CPU | 60 vCPU / 240 GB (6xl) | $3.714 | ~$2,711 |
| GPU | 1x RTX 4000 Ada | $0.836 | ~$610 |
| GPU | 8x H200 (1,128 GB VRAM) | $39.336 | ~$28,715 |

The suspend feature is where the pricing model earns its keep. Because you are billed per minute only while running, and only for cheap image storage while suspended, you can keep an expensive GPU machine around at near-zero cost between bursts of work. The founders position this as the middle ground between serverless (pay only for what runs, but lose control and state) and reserved instances (full control, but you pay for idle capacity). It is not the cheapest compute on the market—the team is explicit about that—but it is cheaper than most sandbox providers and neoclouds for agent workloads, and customers are paying for the agent-first DX and performance.

## Real-World Use Cases: Agent Fleets, Training, and Agentic Backends

The founders name three primary use cases, and the Show/Launch HN threads corroborate them with real usage:

### 1. Agent Fleets for Software Factories

The flagship pattern is a pilot agent that scopes work and delegates to sub-agents, each running on its own VM. In the founders' own accounts, at least one customer runs hundreds of VMs for sustained multi-hour or multi-day compute. Each sub-agent gets an isolated, full machine with its own static IP, secrets, and environment—then suspends it when done.

### 2. Model Training and RL Environments Orchestrated by Agents

Because VMs are persistent and give you root over your own CUDA and drivers, they suit RL training loops and other environments where an agent must bring up a training job, monitor it, checkpoint, and resume. The snapshot and golden-image features let you capture a known-good environment and reuse it across training runs.

### 3. Backend for Agentic Products

A persistent VM can act as the durable backend for an agent-powered product, holding state, running long-lived services, and serving the agent's outputs over the HTTPS endpoint. Users in the HN threads also report hosting OpenClaw and web apps successfully, and finding Machine0 works well with Claude Code.

## Community Reception on Hacker News (Pro & Con)

Machine0 has generated genuine community discussion. The Show HN thread drew 96 points and 37 comments; the Launch HN thread drew 80 points and 43 comments.

On the positive side, commenters praised the NixOS flake value proposition, the reproducibility, and how well the platform pairs with Claude Code. The static-IP-retention and snapshot interplay with flake-based provisioning were called out as thoughtful touches.

On the critical side, the recurring concerns were:

- **DigitalOcean lock-in and markup.** Since Machine0 runs on top of DigitalOcean, some users questioned whether they were paying a premium over raw DO capacity and whether the abstraction justified it. The team's answer is that the value is in the agent-first DX and control plane, not raw unit economics, and that BYOC will give users their own underlying cloud on the roadmap.
- **NixOS learning curve.** As discussed, the declarative model has a real learning cost, even if agents soften it.
- **Per-minute pricing mental math.** Continuous users found it harder to predict monthly bills than with flat-rate reserved instances.
- **Static-IP retention semantics.** Because the IP is retained only while the VM exists and is lost on delete, users had to think carefully about lifecycle management to avoid surprises.

## Machine0 vs the Broader 'VM for Agents' Landscape

Machine0 does not compete only with Modal and E2B. The "VM for agents" space is crowded, and the competitive field includes E2B, Blaxel, Morph, Daytona, Runloop, shellbox.dev, and exe.dev, with Fly.io's sprites also mentioned in the HN thread as an agent-VM competitor.

Machine0's positioning against this field is consistent: it offers GPUs, much larger machines, and full control down to the kernel and drivers, and it claims to be cheaper for compute-intensive agent workloads than the lightweight options. exe.dev was cited as a similar tool, with Machine0's Nix integration as the differentiator. Fly.io sprites are lighter-weight; Machine0 counters with bigger hardware and deeper VM control.

The unifying theme of the "persistent VM for agents" category is that it sits between classic IaaS and serverless: you get real, owned, persistent machines (unlike serverless sandboxes) with the on-demand, per-minute economics and automation ergonomics that agents need.

## Verdict — Who Should (and Shouldn't) Use Machine0

Machine0 is the right tool if you are building or running agent fleets that need persistent, owned machines with real GPUs, static IPs, reproducible NixOS builds, and per-minute economics that let you suspend expensive hardware between bursts. It shines for RL training environments, long-lived agent backends, and software-factory patterns where a pilot agent delegates to many sub-agents, each on its own isolated VM.

It is likely the wrong tool if you only need to run bursty, stateless serverless functions—where Modal or E2B is simpler and cheaper—or if you prefer conventional Linux administration over the NixOS learning curve, or if you are sensitive to running on top of DigitalOcean and want direct control of your underlying cloud before BYOC ships.

The bottom line: Machine0 is a focused, opinionated, agent-first take on the persistent VM, and for teams that want to hand full, owned machines to their agents, it is a compelling and distinctive option.

## FAQ

### What is Machine0?

Machine0 is a Y Combinator Summer 2026 startup that provides persistent CPU and GPU virtual machines controlled entirely from the command line, aimed at AI-agent-driven and developer workloads.

### How is Machine0 different from Modal or E2B?

Modal and E2B are ephemeral serverless sandboxes with no root access and no own kernel or drivers, while Machine0 gives you a persistent VM you fully own—root, drivers, CUDA, static IP, and HTTPS endpoint.

### How much does Machine0 cost?

CPU VMs start at $0.013 per hour and reach $3.714 per hour for 60 vCPUs; GPU VMs start at $0.836 per hour for an RTX 4000 Ada and reach $39.336 per hour for 8x H200. Billing is per minute, with a $5 minimum top-up.

### Can I stop paying for a Machine0 VM when I'm not using it?

Yes. Suspending a VM stops compute billing entirely; while suspended you pay only image storage at $0.078 per GB per month, and you can resume or snapshot anytime.

### Does Machine0 run on my own cloud?

Not yet. Machine0 currently runs on DigitalOcean infrastructure, but bring-your-own-cloud (BYOC) is on the roadmap.
