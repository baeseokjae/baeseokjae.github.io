---
title: 'machine0 Review 2026: Persistent CPU and GPU VMs From the CLI'
date: 2026-10-01T05:11:21+00:00
tags:
  - machine0 CLI VMs
  - machine0 persistent VM
  - machine0 review
  - persistent VMs for AI agents
  - GPU VMs for agents CLI
  - machine0 pricing
  - machine0 vs E2B
  - machine0 vs Modal
  - machine0 vs Daytona
  - agent sandbox vs persistent VM
  - MCP server VM management
  - machine0 profiles MCP credentials
  - 60 vCPU 240 GB cloud VM per minute
  - H200 GPU cloud VM per hour
  - long-running agent compute
description: "machine0 CLI VMs are persistent KVM machines for agents: full CPU/GPU VMs from 1 vCPU at $0.013/hr to 8x H200, driven by CLI or MCP. Review inside."
draft: false
cover:
  image: "/images/machine0-persistent-cpu-gpu-vms-cli.png"
  alt: "machine0 Review 2026: Persistent CPU and GPU VMs From the CLI"
  relative: false
schema: "schema-machine0-persistent-cpu-gpu-vms-cli"
---

machine0 CLI VMs are full KVM/QEMU virtual machines that stay on until you stop, suspend or destroy them — driven either from a command line where every command accepts `--json`, or from a remote MCP server. CPU machines start at 1 vCPU / 1 GB for $0.013/hr (~$9/month) and scale to 60 vCPU / 240 GB at $3.714/hr; GPU machines go from one RTX 4000 Ada at $0.836/hr up to 8x H200 with 1,128 GB of combined VRAM.

That is the short answer, and it is also the entire pitch. machine0 (Y Combinator S26, founded by Barnaby Malet) is not competing on cold starts, and it is not trying to be the cheapest compute on the market. It is betting that a specific class of agent workload — coding agents that run six to eight hours, auto-research and RL loops that run for days, 24/7 fleets like OpenClaw — no longer fits the ephemeral sandbox model that E2B, Modal and Daytona optimized for. This review covers what the product actually does on 2026-10-01, what it costs line by line, where the billing traps are, and who should not buy it.

## What exactly is machine0 — a sandbox or a computer?

It is a computer. Every machine0 VM is a genuine KVM/QEMU virtual machine, not a container and not a gVisor sandbox, which means you get kernel-level access and the real GPU driver exposed inside the guest [per the founder on the launch thread](https://news.ycombinator.com/item?id=49348136). That single architectural choice cascades into everything else: you can load kernel modules, run Docker inside, attach a real NVIDIA driver, and keep a working tree alive for as long as you keep paying.

Fly.io's own taxonomy is the cleanest way to place it. In [fly.io's agent sandbox guide](https://fly.io/learn/agent-sandbox-providers/), agents buy one of three product shapes: a stateless code runner, a persistent computer, or a control plane that manages fleets of either. machine0 is squarely the second category, and the guide names the failure mode it avoids — "pick by feature list and you find out in week three that your coding agent's working tree evaporated at the ten-minute mark."

The founder's framing of the problem is worth quoting because it explains the product's shape. Agent workloads moved from ephemeral to always-on, and the four named pain points are resources (a few agents saturate RAM and CPU), security (`--yolo` on your laptop is one prompt injection away from exfiltrated credentials), availability (close the laptop and the agent dies mid-task), and isolation.

### Is it ephemeral like E2B, or persistent like a VPS?

Persistent by default, and this is the sharpest difference in the category. An [independent seven-product comparison published on dev.to](https://dev.to/saptadev27/cloud-computers-for-ai-agents-in-2026-a-practical-comparison-5dbd) found that machine0 and Fly.io Sprites persist indefinitely, while OpenComputer v2 caps at a hard eight hours and E2B, Vercel Sandbox and Modal cap a continuous session at 24 hours on paid plans.

| Product | Isolation | Max continuous lifetime | Billing model |
|---|---|---|---|
| machine0 | Full KVM/QEMU VM | Indefinite (until you destroy it) | Per-minute, always-on until suspended |
| Fly.io Sprites | Firecracker microVM | Indefinite | Per-second active with scale-to-zero |
| E2B | Firecracker microVM | 24 hours (paid) | Per-second full duration |
| Daytona | Container (VM/GPU classes) | 24 hours (paid) | Per-second full duration |
| Vercel Sandbox | Firecracker microVM | 24 hours (paid) | Per-second active CPU |
| Modal | gVisor | 24 hours (paid) | Per-second active with scale-to-zero |
| OpenComputer v2 | Full KVM VM | 8 hours | Per-second full duration |

That table is the whole buying decision compressed into four columns. Note the last column and the fourth row together: the usage-billed platforms charge nothing while your agent waits on a model, and machine0 charges for every second the VM is on.

## How does an agent drive its own fleet from the CLI or MCP?

Two interfaces, and both are aimed at an agent rather than a human clicking through a console. The CLI is deliberately small — `new`, `ls`, `rm` — and every command accepts `--json`, so a model parses structured output instead of scraping a table. The same surface is exposed as a remote MCP server, which means Claude Code, Codex or any MCP-capable harness can create and manage VMs as tool calls.

The founder's explicit positioning is: "One command spins up a persistent VM. Your agent drives it via CLI or MCP, building its own fleet from 1 vCPU up to 60 vCPU / 240 GB and 8xH100s."

The grammar matters more than it sounds. The strongest criticism on the launch thread was that the API is not a moat — one commenter argued it "could be vibecoded as a pile of scripts," and pointed out that AWS, GCP, Hetzner and DigitalOcean already have agent-orchestrable APIs. The founder's answer is not that the API is defensible but that it is cheaper in context and turns: a three-verb grammar saves tokens and avoids the orphaned artifacts that real cloud APIs leave behind — security groups, volumes, elastic IPs you forget to delete and pay for.

That is a fair answer, and it is the right way to evaluate machine0: not as unique infrastructure, but as a smaller interface over infrastructure that already exists. It runs on DigitalOcean today; [bring-your-own-cloud is on the roadmap, not shipped](https://news.ycombinator.com/item?id=49348136).

### What can the agent do without SSH?

Everything the fleet needs at the API level: create, list, inspect, suspend, snapshot, clone and destroy. Every VM gets a static public IP and HTTPS at `<vm>.mac0.io`, so a service your agent starts becomes reachable without you configuring DNS or a reverse proxy. The machines ship pre-loaded — the `ubuntu-24-04-loaded` image includes Docker, Node.js, Python, Go, Rust, Bun, Claude Code, Codex, OpenCode, tmux, zoxide, fzf, ripgrep and bat, per the [machine0 FAQ](https://docs.machine0.io/introduction/faq).

## What does machine0 cost? Full CPU, GPU and storage pricing

Pricing is per-minute and identical in all five regions, which is unusual and genuinely useful — no region arbitrage games. [The authoritative pricing page](https://docs.machine0.io/introduction/pricing) gives a floor and a ceiling that are 285x apart, so the marketing line "from $0.013/hr" deserves the criticism it got on launch ("It ranges from cold to orange!"). Here is the real spread.

| Tier | Spec | Price/hr | Approx. monthly |
|---|---|---|---|
| small | 1 vCPU / 1 GB / 25 GB | $0.013 | ~$9 |
| (mid CPU tiers) | scales between | — | — |
| 6xl | 60 vCPU / 240 GB / 900 GB | $3.714 | ~$2,711 |

Two CPU variants cut across those tiers. The `-nvme` variant puts newer-generation CPUs and NVMe disks behind the same vCPU/RAM/disk numbers for higher disk IOPS, and the `-premium` variant gives dedicated — not shared — vCPUs, which is their fastest single-thread tier. If you are running a compiler or a single-threaded agent loop, `-premium` is the tier that changes wall-clock time.

GPU pricing is where machine0 differentiates hardest, because most of the sandbox category has no GPU at all:

| GPU tier | VRAM | Price/hr |
|---|---|---|
| gpu-4000ada-1 (1x RTX 4000 Ada) | 20 GB | $0.836 |
| gpu-l40s-1 / gpu-6000ada-1 | 48 GB | $1.727 |
| gpu-mi300x-1 | 192 GB | $2.849 |
| gpu-h100-1 | 80 GB | $4.851 |
| gpu-h200-1 | 141 GB | $4.917 |
| 8x MI300X | 1,536 GB | $22.792 |
| 8x H100 | 640 GB | $38.808 |
| 8x H200 | 1,128 GB | $39.336 |

Note the version problem: machine0.io's marketing snippet still advertises the older H100 rate of $3.729/hr, while the docs pricing page and an independent write-up both show $4.851/hr. Treat the docs as current and the marketing banner as stale.

### What are the billing traps?

Three, and all three are documented and easy to hit.

First, stopped VMs bill at full rate. The [FAQ](https://docs.machine0.io/introduction/faq) is explicit: cloud resources remain reserved while a VM is merely stopped, so only suspend or destroy stops the meter. If you stop a 6xl machine and walk away for a week, you still owe roughly $624.

Second, suspend is where savings actually live. A suspended VM pays only image storage at $0.078/GB/month, and persistent disks cost about $0.1667/GB/month. Suspending a 900 GB image costs on the order of $70/month instead of $2,711 — a 97.5% reduction, which is the single most valuable habit for anyone running a fleet.

Third, auto-topup is on by default once a card is saved. There is a $5 minimum top-up and unused credits are refundable, but an always-on fleet plus auto-topup is a compounding-spend pattern worth watching for the first month.

### Is machine0 cheaper than E2B or Daytona?

At the same shape, for a busy agent, yes — by roughly 3x. The dev.to comparison measured a 2 vCPU / 4 GB machine running flat out for one hour: machine0 $0.052, versus E2B and Daytona at $0.166, Modal at $0.238 and OpenComputer at $0.378.

But the same review states the counter-case plainly: "machine0 bills while stopped, though, and the usage-billed ones cost far less when the agent is mostly waiting on a model." That is the crossover. If your agent spends most of its wall-clock time waiting for a model response — the typical tool-calling agent — a scale-to-zero platform wins on cost. If your agent is genuinely burning CPU or GPU continuously, machine0 wins.

An honest rule of thumb: estimate your duty cycle. Above roughly 50% busy, machine0's per-minute always-on model beats per-second active billing at comparable shapes. Below 20% busy, it does not.

## Suspend, snapshot and resume — what actually persists?

This is the most misunderstood part of the product, and the founder corrected it directly on the launch thread: there is **no CRIU**. "Snapshots are at the disk layer, not RAM... so processes restart, they don't resume mid-execution. Practically: anything that survives a reboot survives a suspend."

Read that carefully, because "suspend" is doing load-bearing work it does not deserve. A suspended machine0 VM is a disk snapshot. When you run `machine0 start`, the guest cold-boots from that disk. Files, installed packages, git working trees, Docker images, databases on disk, crontab entries — all survive. Running processes, in-memory state, open network connections, an in-flight model call — none survive.

That places machine0 in a specific column of the persistence taxonomy. In [LogRocket's five-dimension comparison of agent sandbox platforms](https://blog.logrocket.com/comparing-ai-agent-sandbox-platforms-e2b-modal-daytona-and-more/), persistence is not one thing: E2B pauses with memory intact, Daytona only on VM sandboxes, and the rest save the filesystem — matching machine0's documented disk-level suspend. A [23-platform landscape survey](https://rywalker.com/research/ai-agent-sandbox-sandboxes) frames the same caveat for the whole market: "does persistence mean a running process resumes? Not necessarily. Some products preserve only files, while others retain memory in specific pause modes."

So the correct mental model for machine0 suspend is: **a saved computer, not a paused process**. Structure agent work accordingly — write checkpoints to disk, make steps resumable, and do not expect a suspend to hold a 30-minute in-flight training run.

### What are snapshots and clones for?

Golden images. You can snapshot a configured VM and clone it, which turns a long provisioning sequence — install drivers, pull models, configure the agent harness — into a repeatable starting point. For fleet operators this is the feature that makes scaling sane: bake once, clone many, and keep the expensive setup off the critical path.

## What are profiles, and why are they the most agent-native feature?

Profiles bundle MCP connections, credentials, prompts and environment variables and inject them at VM creation, so each agent gets exactly the capabilities you choose and nothing else. When you SSH in, the VM's Claude Code or Codex picks them up automatically. Per the [YC launch page](https://www.ycombinator.com/launches/SBD-machine0-cloud-computers-for-agents), this is the mechanism that makes a fleet of agents manageable rather than a pile of hand-configured boxes.

It is also where the genuinely unsolved problem sits. Credential rotation is the open edge: the founder says OAuth refresh is handled inside the profile and re-injection is possible, but a commenter (bobbylarson) pressed the real objection — a process that read a credential at boot keeps the stale value in memory, so revocation mid-session is "not solved cleanly without short TTLs."

Note the security scoping carefully, because it is easy to over-credit a VM boundary. As the landscape survey puts it, a VM boundary, an egress policy and scoped credentials solve three different problems and must be verified separately: a full KVM VM isolates guest execution from the host, but it does not stop exfiltration through network destinations you allowed or credentials you granted. machine0's own defaults are sensible — [SSH-only with password auth disabled, root login disabled, ufw enabled with ports 22/80/443 open, and private keys that never leave your machine](https://docs.machine0.io/platform/security) — but they are defaults, not a complete security posture.

### Which is more agent-native: CLI JSON output or the MCP server?

The MCP server, for one specific reason: it removes an orchestration hop. If your harness already speaks MCP, adding the machine0 server means the agent can provision its own compute as a tool call — spawn a GPU box for a fine-tune, run it, destroy it — without you writing glue. The `--json` CLI is the fallback for harnesses without MCP and for your own scripting.

## machine0 vs E2B, Modal, Daytona and Fly.io Sprites

Different products, different optimization targets. None wins every dimension.

| Dimension | machine0 | E2B / Daytona | Modal | Fly.io Sprites |
|---|---|---|---|---|
| Cold start | Cold boot from disk — not competitive | ~717 ms / ~742 ms | ~2,437 ms | Fast microVM |
| Isolation | Full KVM VM | Firecracker microVM / containers | gVisor | Firecracker microVM |
| Persistence | Indefinite, disk-level | 24h session cap, memory-intact pause (E2B) | 24h cap, filesystem only | Indefinite, scale-to-zero |
| GPU | Up to 8x H200 (1,128 GB) | None listed | Limited / CPU-focused | No GPU parity |
| Pricing model | Per-minute always-on until suspended | Per-second full duration | Per-second active | Per-second active |
| Best for | Always-on agents, GPU work | Fast tool-call sandboxes | Bursty scale-to-zero | Persistent sandboxes |

The [LogRocket comparison](https://blog.logrocket.com/comparing-ai-agent-sandbox-platforms-e2b-modal-daytona-and-more/) measured cold starts of 742 ms for Daytona, 717 ms for E2B, 1,852 ms for Vercel and 2,437 ms for Modal. machine0 does not appear in that contest at all — it is not a millisecond tool-call runner. If your workload is "spawn, run this function, tear down," every platform on that list beats machine0. If your workload is "keep a computer alive for two days while a research loop iterates," machine0 is the shape that matches.

On GPUs the field thins dramatically. E2B and Blaxel list no GPU at all, which removes them from training, fine-tuning and RL use cases. That leaves machine0 with almost no direct competition inside the agent-sandbox category for GPU-backed, persistent, CLI-driven agents — a narrower claim than "best product," but a true one.

## NixOS and Ubuntu: reproducible or pre-installed?

Two image philosophies, both available. The `ubuntu-24-04-loaded` image is the pragmatic default: Docker, Node.js, Python, Go, Rust, Bun, Claude Code, Codex, OpenCode, tmux, zoxide, fzf, ripgrep and bat are already there, so an agent is productive minutes after `new` returns.

NixOS is the counter-argument to suspend-and-pray state preservation. Declarative flakes, deterministic builds and one-command rollbacks make the environment itself a version-controlled artifact — instead of trusting that a disk snapshot carries the right state forever, you can rebuild an identical machine from a definition. For fleets where reproducibility is a compliance requirement rather than a convenience, this matters.

One caveat worth flagging: the NixOS image shipped on an end-of-life release at launch (25.11), which the founder acknowledged and said he would republish. At a company moving at launch speed, check image freshness before baking a golden image you intend to keep.

## Security model, regions and uptime

Five regions — us-east (New York), us-west (San Francisco), uk (London), eu (Amsterdam) and asia (Singapore) — at identical per-minute pricing. One practical restriction: GPU sizes are offered in us-east, uk, eu and asia, but not us-west. If your workload is GPU-bound and your data residency requirement points at San Francisco, that is a hard blocker, not a preference.

machine0 quotes a 99.99% VM-level uptime SLA. Note the qualifier: VM-level, which is a different claim from end-to-end service availability, and worth reading in the actual agreement before you architect around it.

## Who should use machine0 — and who should not?

Use it if:

- Your agent runs for hours or days and dies when your laptop closes.
- You need GPU compute attached to a persistent agent (fine-tuning, RL, local inference) — the sandbox category largely cannot serve you.
- You are running a fleet and want profiles to inject MCP servers and credentials per agent instead of hand-configuring boxes.
- You want `--json` on every command so an orchestrator can parse state without scraping.
- You want full kernel access — Docker-in-Docker, kernel modules, real drivers — rather than a locked-down guest.

Do not use it if:

- Your workload is bursty tool calls that mostly wait on model responses; a scale-to-zero platform will cost dramatically less.
- Cold start matters more than persistence — 700 ms beats a disk boot.
- You need the absolute cheapest compute; the founder says directly that "we're not the cheapest compute on the market, but cheaper than most sandbox providers/neoclouds."
- You need mid-execution process resumption; suspend is disk-level, and that is not going to change without CRIU.
- You need bring-your-own-cloud today. It is roadmap, not shipped.

## Criticisms, open questions and the moat question

The launch thread's strongest arguments were structural, not technical, and they have not been answered:

- **The interface is not a moat.** The verbs `new`, `ls`, `rm` can be wrapped around any cloud API. The defense is developer experience and context economy, which is real but not exclusive.
- **Vendor lock-in.** A proprietary CLI over one cloud provider's infrastructure is a commitment. BYOC on the roadmap partially addresses it; shipping it would address it properly.
- **Credential revocation mid-session is unsolved.** Short TTLs are the suggested fix and there is no evidence they are implemented yet.
- **Pricing transparency.** Leading with "from $0.013/hr" for a lineup whose top tier is $3.714/hr drew justified pushback. The docs page is honest; the banner is not.
- **Launch-speed polish.** An EOL NixOS base image and experimental/beta labels on profiles and disks are normal for a YC S26 company, and also a reason to date any review you read.

None of these are disqualifying. All of them are the difference between buying a product and buying a promise.

## Verdict: is a CLI-driven persistent VM worth it for your agent workload?

Yes, for the workload it was built for — and it is unusually clear about which workload that is. machine0 CLI VMs are the right buy when your agent is genuinely busy for hours at a time, when you need a real GPU attached to a persistent box, or when you are running a fleet that needs credentials and MCP servers injected per machine. At 2 vCPU / 4 GB, running flat out, it costs $0.052/hr against $0.166 for E2B and Daytona — a 3x advantage that reverses the moment your agent goes idle.

The discipline that makes it cheap is suspend, not stop. Stopped VMs bill at full rate; suspended VMs bill at $0.078/GB/month for image storage. An operator who internalizes that one rule cuts a fleet's bill by an order of magnitude.

The parts that are still rough — mid-session credential revocation, BYOC, image freshness — are the parts of a company that is three months old. Judge machine0 as what it is: a well-shaped product for always-on agents with a small interface, honest docs, and an honest limitation list. If your agent runs for six hours straight, it is probably the right computer. If it runs for six seconds at a time, it is the wrong one.

## FAQ

**Does machine0 suspend preserve running processes?**
No. Suspend is a disk-layer snapshot, not a CRIU memory checkpoint. Your files, installed packages and working trees survive; running processes restart on `machine0 start` rather than resuming mid-execution. The founder's rule of thumb is exact: anything that survives a reboot survives a suspend.

**How much does a machine0 VM cost per month?**
It ranges from about $9/month for the smallest tier (1 vCPU / 1 GB / 25 GB at $0.013/hr) to roughly $2,711/month for a 6xl machine (60 vCPU / 240 GB / 900 GB at $3.714/hr). Billing is per-minute, identical in all five regions, with a $5 minimum top-up and refundable unused credits.

**Is machine0 cheaper than E2B or Daytona?**
For a busy agent at the same shape, yes — about 3x. A 2 vCPU / 4 GB machine running flat out for one hour costs $0.052 on machine0 versus $0.166 on E2B and Daytona. For bursty workloads that mostly wait on model responses, scale-to-zero platforms are cheaper because machine0 bills the whole time the VM is on.

**Do stopped machine0 VMs still cost money?**
Yes, at full rate. Cloud resources remain reserved while a VM is stopped. Only suspend (image storage at $0.078/GB/month) or destroy stops the compute meter. This is the most expensive mistake a new user can make.

**Does machine0 offer GPUs, and how large?**
Yes, up to 8x H200 at $39.336/hr with 1,128 GB of combined VRAM. GPU tiers include RTX 4000 Ada (20 GB, $0.836/hr), L40S and RTX 6000 Ada (48 GB, $1.727/hr), MI300X (192 GB, $2.849/hr), H100 (80 GB, $4.851/hr) and H200 (141 GB, $4.917/hr). GPUs are available in us-east, uk, eu and asia — not us-west.
