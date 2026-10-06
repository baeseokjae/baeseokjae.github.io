---
title: "Pi Coding Agent Configuration on Linux: Fix the Out-of-Place .pi Folder"
date: 2026-10-01T07:12:31+00:00
tags:
  - pi coding agent configuration
  - pi agent config folder linux
  - PI_CODING_AGENT_DIR
  - pi coding agent xdg base directory
  - pi coding agent .pi folder home directory
  - PI_CODING_AGENT_SESSION_DIR
  - pi coding agent config location change
  - pi coding agent dotfiles git
  - pi coding agent custom agent directory
  - pi coding agent PI_CONFIG_DIR not working
  - pi coding agent settings.json location
  - pi coding agent configuration guide linux
  - earendil-works pi
  - pi agent directory migration
  - pi coding agent auth.json location
  - how to move pi config folder
description: "Pi ignores XDG on Linux and writes to ~/.pi/agent. Move it with PI_CODING_AGENT_DIR — not PI_CONFIG_DIR — plus migration and dotfiles recipes."
draft: false
cover:
  image: "/images/pi-coding-agent-config-linux.png"
  alt: "Pi Coding Agent Configuration on Linux: Fix the Out-of-Place .pi Folder"
  relative: false
schema: "schema-pi-coding-agent-config-linux"
---

Pi does not follow the XDG Base Directory specification on Linux. Its user configuration lives in `~/.pi/agent`, and the only supported way to relocate it is the `PI_CODING_AGENT_DIR` environment variable. Set it to the *agent* directory — `~/.config/pi/agent`, never `~/.config/pi` — or authentication and model settings silently read as empty.

This guide covers what is actually inside that folder, why the widely cited `PI_CONFIG_DIR` variable does nothing, the three layouts that fit real workflows, and the verification commands that prove the move worked.

## Why Does Pi Put Its Configuration in $HOME on Linux?

Pi's coding agent resolves its user-level directory with a small function in `packages/coding-agent/src/config.ts`. If the environment variable is absent it falls back to `join(homedir(), CONFIG_DIR_NAME, "agent")`, where `CONFIG_DIR_NAME` defaults to `.pi`. On Linux that resolves to `~/.pi/agent` — a dotfolder in the home root, not `~/.config`.

That behavior has been contested repeatedly, and the issue history is the clearest evidence of how settled the maintainers consider it:

| Issue | Ask | Outcome |
|---|---|---|
| [#534](https://github.com/earendil-works/pi/issues/534) | Resolve prefix as `PI_CONFIG_DIR` → `XDG_CONFIG_HOME` → OS default | Opened and closed the same day; 30 +1 reactions, 16 comments |
| [#2870](https://github.com/earendil-works/pi/issues/2870) | Full XDG compliance across config, state, and cache | Closed; 80 total reactions (62 +1, 12 heart, 6 rocket) |
| [#2390](https://github.com/earendil-works/pi/issues/2390) | `PI_CONFIG_DIR` is ignored by the coding agent | Closed; maintainer confirmed the variable is for a different subsystem |
| [#5301](https://github.com/earendil-works/pi/issues/5301) | Opt-in XDG layout behind a `Paths`/`Roots` abstraction | Closed — "sorry, this isn't going to change for the time being" |

As of 2026-10-01, a search for open XDG-related issues in the repository returns zero results. Every proposal has been closed, and the maintainer's position is consistent across threads: existing users make automatic migration messy, so `PI_CODING_AGENT_DIR` remains the escape hatch.

The scale of the audience is what makes this a practical problem rather than a philosophical one. The `@earendil-works/pi-coding-agent` package recorded 11,878,758 downloads between 2026-08-31 and 2026-09-29, and the legacy `@mariozechner/pi-coding-agent` scope added 3,309,867 in the same window. The repository itself sits at 110,843 stars, 14,096 forks, and 234 open issues. A dev.to review of pi in 2026 named "`~/.pi/agent` ignores XDG on Linux" as the single largest community complaint of the year, citing a 56-point Hacker News thread.

## What Actually Lives Inside the .pi Folder?

Before moving anything, know what you are moving. Pi's official configuration documentation splits user-level assets into two groups: files you should back up and files you can regenerate.

| Path under `~/.pi/agent` | Contents | Regenerable? |
|---|---|---|
| `settings.json` | user settings | No — hand-written |
| `keybindings.json` | keybinding overrides | No |
| `mcp.json` | MCP server definitions | No |
| `models.json` | model/provider configuration | No |
| `auth.json` | stored credentials | No — secret |
| `extensions/`, `skills/`, `prompts/`, `themes/` | user assets | No |
| `bin/` | auto-downloaded `fd` and `ripgrep` | Yes |
| `pi-debug.log` (and other logs) | diagnostics | Yes |

Two consequences follow from that table.

First, `auth.json` is the reason this is a configuration topic with a security edge. Any migration step that copies the directory into a git repository, a container image, or a shared backup can leak credentials. The official security documentation also warns against mounting a host agent directory into a container you do not fully trust, because the credential file travels with it.

Second, the `bin/` directory explains a behavior that surprises people after a successful move: the first run after relocating the agent directory re-downloads `fd` and `ripgrep` into `<new agent dir>/bin`. Nothing breaks, but the old copy stays behind as dead weight if you moved rather than deleted.

Project-level configuration is separate. Pi reads `<current working directory>/.pi/` and only loads it after you approve project trust. The one documented exception is the session directory, which is resolved before trust is evaluated.

## The Variable That Does Not Exist: PI_CONFIG_DIR

Search results and older write-ups routinely tell you to `export PI_CONFIG_DIR=...`. That advice is wrong for the coding agent, and it is the most common way readers end up convinced that pi ignores environment variables entirely.

Issue #2390 documented exactly this: after setting `PI_CONFIG_DIR`, `~/.pi/agent` was still created. The maintainer's conclusion was unambiguous — `PI_CONFIG_DIR is for pods, not for the coding agent`. The variable belonged to a removed `pods` manager and was never wired into the coding agent's path resolution.

You can confirm this against the primary source. The official environment variable reference at `pi.dev/docs/latest/environment-variables` lists `PI_CODING_AGENT_DIR`, `PI_CODING_AGENT_SESSION_DIR`, `PI_PACKAGE_DIR` (for Nix/Guix), `PI_OFFLINE`, `PI_SKIP_VERSION_CHECK`, and telemetry controls. `PI_CONFIG_DIR` does not appear on that page at all.

If you set `PI_CONFIG_DIR` and saw no effect, nothing is broken — you configured a variable that the coding agent does not read.

## PI_CODING_AGENT_DIR Points at an Agent Directory, Not a Home

The name is the specification. `PI_CODING_AGENT_DIR` is not `PI_HOME`. Its default value is `~/.pi/agent` — the leaf directory that contains `settings.json` — not `~/.pi`.

The failure mode when you miss that distinction is quiet and expensive. Setting `PI_CODING_AGENT_DIR=~/.piz` makes pi look for `~/.piz/auth.json` and `~/.piz/models.json`. Those files do not exist, so pi starts with no authentication and no configured models and reports nothing obviously wrong. Setting `PI_CODING_AGENT_DIR=~/.piz/agent` behaves correctly. One path segment is the difference between a working setup and a confusing one, and the asymmetry exists because pi never appends `agent` to a value you supply — it only appends it to the default.

The design intent is visible in the naming. The `~/.pi` container is meant to hold several sibling agent directories — `~/.pi/agent`, `~/.pi/work`, `~/.pi/personal` — that you switch between by changing one variable. That is why the variable names a directory rather than a home.

This is not a new edge case, either. Pi's changelog records fixes for tilde expansion in this variable, for hardcoded paths in error messages, and for example expansion — all three in the release notes — which means the tilde form is supported, but absolute paths remain the safer choice in scripts, systemd units, and container entrypoints where no shell performs expansion.

## Designing the Target Layout: Config, State, and Cache

The most-reacted issue on this topic asked pi to respect all four XDG variables: `XDG_CONFIG_HOME`, `XDG_DATA_HOME`, `XDG_STATE_HOME`, and `XDG_CACHE_HOME`. Pi exposes two of those levers. Here is the layout that gets you closest with the variables that actually exist:

| Concern | XDG location | Pi control |
|---|---|---|
| Settings, auth, models, MCP, extensions | `$XDG_CONFIG_HOME/pi/agent` (`~/.config/pi/agent`) | `PI_CODING_AGENT_DIR` |
| Session transcripts | `$XDG_DATA_HOME/pi-sessions` (`~/.local/share/pi-sessions`) | `PI_CODING_AGENT_SESSION_DIR` |
| Downloaded binaries (`fd`, `ripgrep`) | stays in the agent directory | none — symlink if needed |
| Logs | stays in the agent directory | none — symlink if needed |
| Project overrides | `<project>/.pi/` | trust-gated, no variable |

This split is the practical answer to the objection that a single variable cannot separate configuration from state. It can, when you use both variables:

```sh
export PI_CODING_AGENT_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/pi/agent"
export PI_CODING_AGENT_SESSION_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/pi-sessions"
```

That pair appeared in the discussion of issue #2870 and is the layout to copy if you want a dotfiles-friendly configuration directory and a regenerable, large, never-backed-up session store. Sessions are the heavy, disposable half — separating them means your `~/.config` stays small enough to commit and diff, while transcripts live where backup tools can skip them.

For comparison, `opencode` is the reference implementation cited in that thread: it respects `~/.config`, `~/.local/share`, `~/.local/state`, and `~/.cache`, and even ships a `.gitignore` inside `~/.config/opencode`. Pi is two-thirds of the way there by design and will not go further, which is the honest framing to plan against.

Note what you cannot fix: because `bin/` and logs sit inside the agent directory, no environment variable makes pi write literally nothing to `$HOME`. If your goal is "zero dotfolders in `$HOME`", a single symlink is the remaining step.

## Recipe 1: A Clean XDG Install

For a fresh machine, point pi at XDG paths before the first run so the fallback never fires. Add both exports to `~/.bashrc` or `~/.zshrc`:

```sh
# ~/.bashrc or ~/.zshrc
export PI_CODING_AGENT_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/pi/agent"
export PI_CODING_AGENT_SESSION_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/pi-sessions"
```

Then create the directories explicitly and start pi:

```sh
mkdir -p "$PI_CODING_AGENT_DIR" "$PI_CODING_AGENT_SESSION_DIR"
exec "$SHELL" -l          # reload the profile
pi --version              # first run writes settings.json here, not to ~/.pi
```

Verification is a two-line check that `~/.pi` was never created and the expected files landed in the configured location:

```sh
ls -la "$PI_CODING_AGENT_DIR"
test -e "$HOME/.pi" && echo "unexpected: ~/.pi exists" || echo "clean: no ~/.pi"
```

The reason to create the directories yourself is that a read-only `$HOME` or a restricted container home will otherwise fail at the first write with an error that points at pi rather than at the filesystem.

## Recipe 2: Migrating an Existing ~/.pi Without Losing Sessions or Auth

Existing users carry two assets worth preserving: `auth.json` and the session history. The safest migration moves the whole tree and leaves a compatibility symlink so anything that still hardcodes `~/.pi` keeps working.

```sh
set -eu
TARGET="${XDG_CONFIG_HOME:-$HOME/.config}/pi"
mkdir -p "$TARGET"

# 1. Preserve a copy before touching anything.
cp -a "$HOME/.pi" "$HOME/.pi.bak.$(date -u +%Y%m%dT%H%M%SZ)"

# 2. Move the real tree (including the agent/ leaf) into the XDG location.
mv "$HOME/.pi/agent" "$TARGET/agent"
mv "$HOME/.pi"/* "$TARGET"/ 2>/dev/null || true
rmdir "$HOME/.pi" 2>/dev/null || true

# 3. Backward-compatibility symlink: ~/.pi resolves to the same real files.
ln -s "$TARGET" "$HOME/.pi"

# 4. Point pi at the leaf, not the parent.
export PI_CODING_AGENT_DIR="$TARGET/agent"
```

Then confirm pi still authenticates — this is the step that catches a missing `/agent`:

```sh
ls -l "$PI_CODING_AGENT_DIR/auth.json" "$PI_CODING_AGENT_DIR/models.json"
pi --version
```

If `auth.json` is missing or empty at that path, you pointed the variable at `$TARGET` instead of `$TARGET/agent`. Move the value one level deeper; nothing else needs to change.

Two honest caveats about the symlink approach. It works, and the community consensus in issue #534 confirmed that `ln -s ~/.config/pi ~/.pi` is a valid workaround. But it leaves a `~/.pi` entry in your home directory — now a symlink rather than a directory — so the "home pollution" complaint is reduced, not eliminated. If your `~/.config` is already managed by a dotfiles repository, the symlink is usually the best trade: tools that hardcode `~/.pi` and tools that read `$XDG_CONFIG_HOME` converge on the same real files.

## Recipe 3: CI, Containers, and Read-Only Homes

In ephemeral environments, put everything under the workspace and make it explicit. Nothing should depend on `$HOME`, because the home directory in a build container is frequently read-only or wiped between steps:

```sh
export PI_CODING_AGENT_DIR=/workspace/.pi/agent
export PI_CODING_AGENT_SESSION_DIR=/workspace/.pi/sessions
export PI_OFFLINE=1              # skip network checks in hermetic builds
export PI_SKIP_VERSION_CHECK=1   # avoids a startup HTTP call
mkdir -p "$PI_CODING_AGENT_DIR" "$PI_CODING_AGENT_SESSION_DIR"
```

This covers the read-only-home case that a single variable cannot: configuration and sessions diverge, so a `$HOME` you cannot write to stops mattering. If you need the binaries under one cache root as well, symlink `bin` out of the agent directory rather than trying to relocate it by variable.

The security note matters more in this recipe than in any other. Pi's own documentation warns that mounting a host agent directory into a container exposes the credentials in `auth.json` to anything running inside it. Treat a container mount of `~/.pi/agent` as equivalent to mounting your credential store, and prefer a dedicated agent directory with its own scoped auth for CI workloads.

## Managing the Configuration in Git Without Leaking Auth

The main practical payoff of a `~/.config/pi/agent` layout is that the directory is small, text-heavy, and worth tracking. The one file that must never be committed is `auth.json`.

A workable ignore file for the agent directory:

```gitignore
# ~/.config/pi/agent/.gitignore
auth.json
bin/
*.log
sessions/
```

Track `settings.json`, `keybindings.json`, `mcp.json`, `models.json`, `prompts/`, `themes/`, `skills/`, and `extensions/`. Those are the files where version history actually saves you time — a keybinding experiment or an MCP server list is exactly the kind of change you want to diff and revert.

Verify the ignore rule before your first push, not after:

```sh
cd "$PI_CODING_AGENT_DIR"
git check-ignore -v auth.json          # must print a matching rule
git status --short                     # auth.json must not appear
```

If you keep session history in the same repository by choice rather than by accident, expect that directory to dominate repository size within weeks. That is the concrete argument for keeping `PI_CODING_AGENT_SESSION_DIR` pointed at `~/.local/share` and out of the tracked tree.

## How Do I Verify the Configuration Path Actually Changed?

Three checks, in increasing order of confidence.

```sh
# 1. The variable is visible to the process that will launch pi.
printenv PI_CODING_AGENT_DIR PI_CODING_AGENT_SESSION_DIR

# 2. Only that directory is being written.
ls -la "$PI_CODING_AGENT_DIR"

# 3. Nothing new appeared in the home root.
find "$HOME" -maxdepth 1 -name '.pi*' -newermt '-10 minutes'
```

Check 1 fails most often for a mundane reason: the export lives in your interactive shell profile, but the process reading it is a cron job, a systemd unit, an SSH command, or a launchd agent with a different environment. Absolute paths in the unit file, plus the same two variables in the unit's `Environment=` block, are the reliable fix. Never rely on `~` inside a systemd unit — no shell is present to expand it.

Check 2 catches the missing-`/agent` mistake. Check 3 catches the case where pi wrote to the default location anyway because one of the two variables was not actually exported in the launching context.

If you change settings while pi is running, the in-session `/settings` command and a `/reload` apply the change without restarting the process. And whichever directory pi is pointed at, restart it before moving that directory — a running pi keeps writing to the old, now renamed path until it exits.

## Eight Mistakes That Silently Break the Configuration Path

1. Setting `PI_CONFIG_DIR`. It is not read by the coding agent; the export has no effect.
2. Pointing `PI_CODING_AGENT_DIR` at the parent directory. Omitting `/agent` yields an empty auth and model configuration with no error.
3. Exporting the variables only in the interactive shell. Cron, systemd, and CI inherit nothing.
4. Using `~` in a systemd unit or an exec-style call. Use absolute paths.
5. Expecting the auto-downloaded `fd` and `ripgrep` binaries in `bin/` to stay where they were. They land under the new agent directory on the next run.
6. Moving the directory while pi is running. The process keeps writing to the renamed path.
7. Committing `auth.json` after pointing the directory into a dotfiles repository. Check with `git check-ignore` before the first push.
8. Assuming the move also relocates sessions. Set `PI_CODING_AGENT_SESSION_DIR` separately.

Rolling back is genuinely easy, which is worth saying plainly: unset both variables, move the directory back to `~/.pi`, and pi uses the default again. There is no database or registry entry to repair, because the paths are resolved from the environment on every launch.

## Does the XDG Debate Change What You Should Do?

Both sides of this argument are reasonable, and the disagreement is about defaults rather than capability.

The case for changing pi's default: `~/.pi/agent` violates a specification almost every Linux CLI tool follows, it pollutes `$HOME` for users who keep that directory curated, and it breaks the assumption behind backup and dotfile tooling that reads `$XDG_CONFIG_HOME`. The 80 reactions on issue #2870 and the 56-point Hacker News thread show that this is not a fringe preference. The gap against peers is concrete: `opencode` respects all four XDG paths.

The case for leaving it: a default change requires migrating every existing user, and the maintainer consistently called that messy enough to reject. The proposals on the table were not unreasonable — the suggestion in #534 was a backward-compatible resolution order (check `PI_CONFIG_DIR`, then use `$HOME/.pi` if it exists, then fall back to XDG), which would have required no migration at all — and #5301 proposed an opt-in layout behind a `Paths`/`Roots` abstraction. Both were closed: "this isn't going to change for the time being." The counter-arguments in the community threads are also not empty: the escape hatch moves the directory in seconds, XDG can scatter an application's data across four locations, and a tool frequently run inside a VM or container has a weaker relationship with its home directory.

The practical reading is that one environment variable closes most of the gap, and knowing that `PI_CODING_AGENT_DIR` — not `PI_CONFIG_DIR` — is the mechanism, and that it names the leaf and not the home, is what prevents the silent failures. Everything else is a defaults argument you can work around in an evening.

## Frequently Asked Questions

**Is `PI_CONFIG_DIR` the correct variable for moving pi's configuration folder?**

No. `PI_CONFIG_DIR` belonged to a removed `pods` subsystem and is not read by the coding agent; the maintainer confirmed this in issue #2390 and the official environment variable reference does not list it. Use `PI_CODING_AGENT_DIR`.

**Where does pi store its configuration on Linux by default?**

User-level configuration lives in `~/.pi/agent`, containing `settings.json`, `keybindings.json`, `mcp.json`, `models.json`, `auth.json`, plus `extensions/`, `skills/`, `prompts/`, and `themes/`. Project-level configuration lives in `<project>/.pi/` and loads only after you approve project trust.

**Why does pi still create `.pi` after I set an environment variable?**

Because the variable you set was not the one pi reads. If you exported `PI_CONFIG_DIR`, nothing happens. If you exported `PI_CODING_AGENT_DIR` and the folder still appears at `~/.pi/agent`, the variable was not present in the environment of the process that launched pi — usually a cron job, systemd unit, or CI step rather than your interactive shell.

**Can I make pi fully XDG-compliant?**

You can relocate configuration and sessions with `PI_CODING_AGENT_DIR` and `PI_CODING_AGENT_SESSION_DIR`. You cannot relocate the auto-downloaded binaries and logs, which share the agent directory, so `$HOME` always keeps at least a symlink unless you point the agent directory elsewhere entirely. Full compliance was requested in issue #2870 and declined.

**Will moving the agent directory break my authentication?**

Only if you point the variable at the wrong level. `PI_CODING_AGENT_DIR=~/.config/pi` makes pi read `~/.config/pi/auth.json`, which does not exist. `PI_CODING_AGENT_DIR=~/.config/pi/agent` reads the file you actually moved. Verify with `ls -l "$PI_CODING_AGENT_DIR/auth.json"` before starting pi.
