---
title: "Sandbox bwrap Nix: Lightweight Sandbox for AI Agents and Experiments"
date: 2026-07-27T04:02:16+00:00
tags:
  - bubblewrap
  - Nix
  - AI agents
  - sandbox
  - Linux security
  - container
description: "sandbox-bwrap-nix combines Bubblewrap and Nix to create a lightweight, auditable sandbox for AI coding agents that boots in under a second."
draft: false
cover:
  image: "/images/sandbox-bwrap-nix-agent-sandbox-2026.png"
  alt: "Sandbox bwrap Nix: Lightweight Sandbox for AI Agents and Experiments"
  relative: false
schema: "schema-sandbox-bwrap-nix-agent-sandbox-2026"
---

## What is sandbox-bwrap-nix?

sandbox-bwrap-nix is a lightweight, open-source sandboxing solution that combines Bubblewrap (bwrap) with the Nix package manager to create isolated environments for AI coding agents and experimental software. It boots in under a second, requires no daemon or root privileges, and gives you fine-grained control over what an AI agent can see, write, and execute. By mounting the Nix store as read-only and providing an isolated home directory with its own process namespace, it delivers three layers of protection against credential leaks, file system tampering, and cross-process snooping.

## Why Sandbox AI Agents? The Security Problem

AI coding agents like Claude Code, OpenCode, and Codex operate with significant system access. They read files, execute commands, install packages, and communicate with external APIs. This capability creates a serious security surface: an agent with access to your SSH keys, AWS credentials, GPG signing keys, or personal files could inadvertently expose them through a prompt injection attack, a malicious package, or simply a bug in the agent's tool-use logic.

Traditional approaches to this problem have been heavy-handed. Running each agent inside a full Docker container provides isolation, but at the cost of image management, daemon overhead, and startup times measured in seconds to minutes. Virtual machines are even heavier. The result is that many developers skip sandboxing entirely, relying on trust in the agent and hoping nothing goes wrong.

The security industry has recognized this gap. Claude Code's own sandbox has used Bubblewrap on Linux since October 2025, and dedicated tools like ai-jail (977 GitHub stars, 86 forks as of July 2026) have emerged specifically to address the AI agent sandboxing problem. The trend is clear: lightweight, auditable sandboxing is becoming a standard requirement for AI development workflows.

## How Bubblewrap Works: The Zero Sandbox Principle

Bubblewrap, originally developed as part of the Flatpak project, operates on what security researchers call the "zero sandbox" principle. By default, a Bubblewrap sandbox has access to nothing. Every file, directory, network interface, and process is explicitly granted rather than implicitly available. This is the opposite of Docker's approach, where a container inherits most of the host environment unless you explicitly remove access.

The core mechanism is simple: Bubblewrap uses Linux kernel namespaces and bind mounts to construct a restricted view of the system. A typical invocation looks like this:

```bash
bwrap \
  --ro-bind /nix/store /nix/store \
  --bind /path/to/project /path/to/project \
  --tmpfs /tmp \
  --tmpfs /home \
  --unshare-pid \
  --unshare-net \
  --clearenv \
  --setenv HOME /home/sandbox \
  --chdir /path/to/project \
  nix develop
```

Each flag is a deliberate grant of access. `--ro-bind /nix/store /nix/store` gives read-only access to the Nix store. `--tmpfs /tmp` creates an empty, ephemeral temp directory. `--unshare-pid` creates a separate process namespace so the agent cannot see sibling processes. `--clearenv` strips all environment variables, preventing credential leaks through environment inheritance.

This approach has a significant advantage: it is auditable. Every permission is visible in the command line or configuration file. There is no implicit trust, no default-allow policy, and no opaque configuration layers. As one security researcher noted, "Bubblewrap does in 30 lines what Docker does in 30 layers."

## Why Nix? Reproducible Dev Shells Inside the Sandbox

Nix brings a critical capability to the sandbox: reproducibility. A Nix flake or shell definition specifies every tool and dependency your AI agent needs — git, bun, uv, gnumake, Python, Node.js, or any other runtime — with exact versions and hash-verified downloads. When combined with Bubblewrap, the Nix store is mounted as read-only, guaranteeing that the agent cannot tamper with its own toolchain.

This combination solves a real problem. AI agents frequently need to install packages, run build tools, and execute scripts. Without Nix, you would need to either pre-install everything on the host (defeating isolation) or allow the agent to install packages inside the sandbox (creating reproducibility issues). With Nix, the environment is declared, version-pinned, and immutable during the agent's run.

The sandbox-bwrap-nix project takes this further by providing a pre-configured sandbox-home directory with a `.bashrc`, `nix.conf`, and OpenCode configuration. This means the agent starts in a fully functional development environment without any setup steps.

## Step-by-Step Setup Guide

### Prerequisites: Installing Bubblewrap and Nix

Before you can use sandbox-bwrap-nix, you need Bubblewrap and Nix installed on your Linux system.

**Install Bubblewrap:**

On most Linux distributions, Bubblewrap is available in the package manager:

```bash
# Debian/Ubuntu
sudo apt install bubblewrap

# Fedora
sudo dnf install bubblewrap

# Arch Linux
sudo pacman -S bubblewrap
```

**Install Nix:**

The recommended approach is the official single-user installer:

```bash
sh <(curl -L https://nixos.org/nix/install) --no-daemon
```

This installs Nix in single-user mode, which is sufficient for sandbox-bwrap-nix and avoids the complexity of a multi-user Nix daemon setup.

### Cloning and Configuring sandbox-bwrap-nix

The sandbox-bwrap-nix project was created on July 25, 2026, and is available on GitHub:

```bash
git clone https://github.com/your-username/sandbox-bwrap-nix.git
cd sandbox-bwrap-nix
```

The project provides a `flake.nix` that defines the development environment. You can customize it to include the tools your AI agent needs:

```nix
{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let pkgs = nixpkgs.legacyPackages.${system}; in {
        devShells.default = pkgs.mkShell {
          buildInputs = with pkgs; [
            git
            nodejs
            python3
            go
            bun
            uv
            gnumake
            curl
            jq
          ];
        };
      });
}
```

### Understanding the bwrap Flags

The sandbox-bwrap-nix wrapper script uses a carefully constructed set of Bubblewrap flags. Here is what each one does:

| Flag | Purpose |
|------|---------|
| `--ro-bind /nix/store /nix/store` | Mounts the Nix store read-only so the agent cannot corrupt its toolchain |
| `--bind /path/to/project /path/to/project` | Gives the agent write access only to the project directory |
| `--tmpfs /tmp` | Creates an empty, ephemeral temp directory that disappears when the sandbox exits |
| `--tmpfs /home` | Provides a clean home directory with no access to your real home |
| `--unshare-pid` | Creates a separate PID namespace so the agent cannot see other processes |
| `--unshare-ipc` | Isolates IPC resources |
| `--unshare-uts` | Gives the sandbox its own hostname |
| `--clearenv` | Strips all inherited environment variables |
| `--setenv HOME /home/sandbox` | Sets a clean HOME path inside the sandbox |
| `--share-net` | Re-enables network access (needed for LLM API calls) |

The `--share-net` flag is particularly important for AI agents. Without network access, the agent cannot call LLM APIs, install packages, or fetch remote resources. By explicitly granting network access rather than inheriting it, you maintain the zero-sandbox principle while enabling the agent to function.

### Customizing Your Sandbox Environment

The sandbox-bwrap-nix project includes a pre-configured sandbox-home directory. You can customize it by editing the files in `sandbox-home/`:

- **`.bashrc`**: Set aliases, environment variables, and shell prompts that help you identify when you are inside the sandbox (the hostname is changed to "bubblewrap" for easy identification).
- **`nix.conf`**: Configure Nix settings like substituters, trusted users, and experimental features.
- **`opencode.json`**: Pre-configure OpenCode with your preferred model, temperature, and other settings.

For credential management, the recommended approach is to inject only what the agent needs. If your agent needs to push to GitHub, create a read-only `.gitconfig` with a limited-scope token:

```bash
--ro-bind /path/to/sandbox-home/.gitconfig /home/sandbox/.gitconfig
```

This gives the agent access to git configuration without exposing your personal `.gitconfig` or SSH keys.

## What You Get: Isolation Layers Explained

### Filesystem Isolation

The filesystem isolation in sandbox-bwrap-nix operates at three levels. First, the Nix store is mounted read-only, preventing the agent from modifying its own toolchain. Second, the project directory is mounted with read-write access, allowing the agent to create and modify files as needed for its work. Third, everything else — your home directory, system configuration files, mounted drives — is invisible to the agent.

This means an agent compromised by a prompt injection attack cannot read your SSH keys from `~/.ssh/`, cannot modify your system configuration in `/etc/`, and cannot access files in other projects. The only files it can read are the Nix store (read-only) and the project directory. The only files it can write are in the project directory.

### Process and PID Namespace Isolation

With `--unshare-pid`, the sandbox gets its own process ID namespace. The agent running inside the sandbox sees only its own process tree. It cannot see your shell sessions, your other running applications, or sibling processes. This prevents a class of attacks where an agent reads process information to discover credentials, API keys, or sensitive data in command-line arguments.

The `--unshare-ipc` flag extends this isolation to inter-process communication resources, preventing the agent from interacting with host processes through shared memory or semaphores.

### Environment Variable Cleanup

Environment variables are a common vector for credential leaks. Many developers store API keys, database passwords, and cloud provider credentials in environment variables. When an AI agent inherits these variables, it has implicit access to all of them.

The `--clearenv` flag in sandbox-bwrap-nix strips every environment variable before the agent starts. You then explicitly set only the variables the agent needs:

```bash
--setenv HOME /home/sandbox \
--setenv USER sandbox \
--setenv OPENAI_API_KEY your-key-here
```

This whitelist approach means you can audit exactly which credentials are exposed to the agent. No more wondering whether `AWS_SECRET_ACCESS_KEY` or `GITHUB_TOKEN` leaked into the agent's environment.

## Real-World Use Cases

### Running AI Coding Agents (OpenCode, Claude Code, Codex)

The primary use case for sandbox-bwrap-nix is running AI coding agents in isolation. When you launch an agent inside the sandbox, it has access to the project files, the Nix-provided toolchain, and network connectivity for API calls. It does not have access to your SSH keys, GPG keys, personal files, or other projects.

This is particularly valuable for organizations that use AI agents in CI/CD pipelines. A compromised agent in CI could push malicious code, exfiltrate secrets, or modify build artifacts. With sandbox-bwrap-nix, the blast radius is limited to the project directory and the ephemeral sandbox environment.

### Experimenting with Nix Flakes Safely

Nix flakes are powerful but can be dangerous. A flake from an untrusted source can execute arbitrary code during evaluation or build. Running `nix develop` inside a Bubblewrap sandbox contains this risk. If the flake tries to access your home directory, SSH keys, or other sensitive resources, it will fail because those resources are not mounted in the sandbox.

This makes sandbox-bwrap-nix an excellent tool for evaluating Nix flakes from new or untrusted sources. You can test the flake, inspect its outputs, and decide whether to trust it — all without exposing your system.

### Testing Untrusted Code

Beyond AI agents, sandbox-bwrap-nix is useful for any scenario where you need to run untrusted code. The combination of filesystem isolation, process isolation, and environment cleanup provides a safe environment for:

- Testing packages from unfamiliar sources
- Running code snippets from forums or AI assistants
- Evaluating open-source projects before installation
- Debugging build scripts that might have side effects

The key advantage over Docker for these use cases is speed. A Bubblewrap sandbox starts in under a second, making it practical for ad-hoc testing where Docker's startup overhead would be prohibitive.

## Comparison with Alternatives

### sandbox-bwrap-nix vs Docker

| Feature | sandbox-bwrap-nix | Docker |
|---------|-------------------|--------|
| Startup time | Under 1 second | 2-30 seconds |
| Daemon required | No | Yes (dockerd) |
| Root required | No | Yes (daemon runs as root) |
| Image management | None (uses host Nix store) | Pull, store, update images |
| Configuration | Single shell script or config file | Dockerfile, compose, volumes |
| Network isolation | Explicit grant (--share-net) | Default isolated, explicit expose |
| Filesystem isolation | Bind mounts | Union filesystem + volumes |
| Auditability | Every flag visible in command | Multiple configuration layers |
| Cross-platform | Linux only | Linux, macOS, Windows |

Docker is the right choice when you need a full operating system environment, complete network isolation, or cross-platform consistency. sandbox-bwrap-nix is the right choice when you need speed, simplicity, and auditability for Linux-native workloads.

### sandbox-bwrap-nix vs ai-jail

ai-jail is a Rust tool (~880KB, 4 dependencies, 124 tests) that wraps Bubblewrap with a TOML configuration file. It supports Linux (bwrap), macOS (sandbox-exec), and Windows via WSL2. With 977 GitHub stars and 86 forks, it is the most popular Bubblewrap-based AI sandbox tool.

| Feature | sandbox-bwrap-nix | ai-jail |
|---------|-------------------|---------|
| Language | Shell + Nix | Rust |
| Configuration | Nix flake + shell script | TOML file |
| Nix integration | Native (Nix store mounted) | No native Nix support |
| Cross-platform | Linux only | Linux, macOS, Windows |
| Per-project config | Manual | Committable .ai-jail TOML |
| Lockdown mode | Manual flag selection | Built-in lockdown mode |
| Bootstrap | Manual | Generates permission configs |
| GitHub stars | New project | 977 stars |

ai-jail is more mature and feature-rich, particularly for cross-platform use. sandbox-bwrap-nix offers deeper Nix integration and a simpler, more transparent configuration model.

### sandbox-bwrap-nix vs Claude's Built-in Sandbox

Claude Code has included Bubblewrap-based sandboxing since October 2025. It provides automatic sandboxing for Claude Code sessions on Linux.

| Feature | sandbox-bwrap-nix | Claude's Built-in Sandbox |
|---------|-------------------|--------------------------|
| Agent support | Any agent | Claude Code only |
| Escape hatch | No escape | `dangerouslyDisableSandbox` option |
| Configuration | Full control | Limited to Claude's defaults |
| Nix integration | Native | None |
| Transparency | Open source | Proprietary |
| Customization | Full | Minimal |

The critical difference is the escape hatch. Claude's sandbox includes a `dangerouslyDisableSandbox` option that completely bypasses protection. sandbox-bwrap-nix has no such escape — if the sandbox is configured, the agent operates within it.

## Limitations and Considerations

sandbox-bwrap-nix is not a complete security solution. It relies on Linux kernel namespaces, which have had vulnerabilities in the past. A kernel-level exploit could potentially break out of the sandbox. For workloads requiring the highest security, consider combining Bubblewrap with Landlock or seccomp for defense-in-depth.

The tool is Linux-only. macOS users need Docker or a Linux VM, and Windows users need WSL2. This is a fundamental limitation of Bubblewrap, which uses Linux-specific kernel features.

Network isolation is minimal. The `--share-net` flag gives the agent full network access, which is necessary for LLM API calls but means the agent can communicate with any internet service. For stricter isolation, you could use a network namespace with iptables rules, but this adds complexity.

Finally, sandbox-bwrap-nix is a very new project (created July 25, 2026). It has not been battle-tested at scale. While the underlying technologies (Bubblewrap and Nix) are mature, the integration is fresh and may have edge cases that have not yet been discovered.

## Conclusion: Is sandbox-bwrap-nix Right for You?

sandbox-bwrap-nix is an excellent choice if you are a Linux user running AI coding agents and want a lightweight, auditable sandbox that boots in under a second. It is particularly well-suited for Nix users who want reproducible development environments combined with strong isolation guarantees.

If you need cross-platform support, consider ai-jail. If you need full operating system isolation, consider Docker. If you only use Claude Code and are satisfied with its built-in sandbox, you may not need sandbox-bwrap-nix at all.

But if you value the zero-sandbox principle — the idea that every permission should be explicit, auditable, and minimal — sandbox-bwrap-nix delivers a clean, transparent implementation that is hard to beat. In an era where AI agents are becoming more capable and more autonomous, lightweight sandboxing is not a nice-to-have. It is a fundamental security practice.

## Frequently Asked Questions

**Q: Does sandbox-bwrap-nix require root access?**

A: No. Bubblewrap supports unprivileged user namespaces, which means sandbox-bwrap-nix runs entirely without root privileges. Your Linux kernel must support user namespaces, which is the default on most modern distributions.

**Q: Can the AI agent access my SSH keys or AWS credentials inside the sandbox?**

A: No. The sandbox uses `--clearenv` to strip all environment variables and `--tmpfs /home` to provide an isolated home directory. Your real SSH keys and credentials are not mounted into the sandbox unless you explicitly bind them.

**Q: How does sandbox-bwrap-nix compare to running an agent in a Docker container?**

A: sandbox-bwrap-nix starts in under a second, requires no daemon, and has no image management overhead. Docker provides stronger isolation (full OS environment, network namespaces) but at the cost of startup time, disk space, and operational complexity.

**Q: Can I use sandbox-bwrap-nix with any AI coding agent?**

A: Yes. The sandbox is agent-agnostic. It works with Claude Code, OpenCode, Codex, and any other agent that runs in a Linux shell. You just need to configure the Nix flake to include the tools your agent requires.

**Q: What happens to files created inside the sandbox?**

A: Files written to the project directory (which is bind-mounted from the host) persist after the sandbox exits. Files written to `/tmp` or `/home` inside the sandbox are ephemeral and disappear when the sandbox process terminates.
