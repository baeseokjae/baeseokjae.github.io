---
title: "Sallyport: A Mac Vault Running Authenticated Agent Actions over MCP"
date: 2026-09-17T19:01:22+00:00
tags:
  - MCP
  - AI agents
  - secrets management
  - credential security
  - Claude Code
  - macOS
draft: false
cover:
  image: "/images/sallyport-mac-vault-authenticated-agent-actions-mcp.png"
  alt: "Sallyport: A Mac Vault Running Authenticated Agent Actions over MCP"
  relative: false
description: "Sallyport is a free Mac vault that runs authenticated API and SSH actions for AI agents over MCP, so the agent gets the operation, never the key."
schema: "schema-sallyport-mac-vault-authenticated-agent-actions-mcp"
---

Sallyport is a free Mac app that holds your API and SSH credentials in an encrypted local vault and executes authenticated actions for your AI agents over MCP. The agent gets the operation, never the key: there is no command that reveals a stored credential and no export route. It runs entirely on your Apple Silicon Mac, gated by Secure Enclave and Touch ID, with no account, cloud, or telemetry.

## Why Your AI Agent Shouldn't Hold Your Keys

Coding agents like Claude Code, Cursor, and Codex read `.env` files, shell variables, and config files to do their job — and so does every package they pull in. When a token sits in those locations, the agent and all its dependencies can read it, and a single malicious dependency or prompt injection can walk it out the door.

The result is not theoretical. Three recent supply-chain attacks targeted exactly these secrets on developer machines. In May 2026, the TanStack ecosystem was hit with 84 malicious package versions across 42 packages designed to harvest cloud credentials, GitHub tokens, and SSH keys at install time. In late 2025, the Shai-Hulud worm stole secrets on install and used the stolen credentials to infect the next round of packages. In August 2025, the Nx S1ngularity attack scanned developer machines for secrets and shipped the loot out through the GitHub CLI.

All three harvested keys from environment variables and files on disk. More quietly, a prompt-injected agent — following instructions, as it was built to do — can copy a token and send it somewhere new without any malware at all. GitGuardian's "State of Secrets Sprawl 2026" report (March 2026) found 28.65 million secrets exposed in public repositories, with AI-assisted commits showing a 3.2% leak rate. The same report surfaced 24,008 unique credentials inside MCP config files like `claude_desktop_config.json` and `.cursor/settings.json`, with Google API keys around 20% of MCP leaks and PostgreSQL connection strings accounting for roughly 14%.

The lesson is structural: the workload itself is untrusted. Traditional secret managers deliver the secret to the workload, which works fine when the workload is your own trusted binary — and fails badly when the workload is an agent that reads everything and obeys instructions. Sallyport exists because of this inversion.

## What Sallyport Is — A Local Mac Vault That Runs the Action, Not the Secret

Sallyport is a free, open-source (Apache-2.0) Mac application that inverts the secret-manager model. Instead of handing a credential to your agent, it executes the authenticated operation on the agent's behalf.

The flow looks like this. Your agent sends a request over MCP: "call this API" or "run this command on that host." Sallyport attaches the credential inside the app, executes the call, and returns the result. The key never appears in the agent's environment, and a sealed journal shows what ran and who approved it.

The project launched publicly on July 14, 2026, written mainly in Swift (with a Go core), and as of the September 2026 data update it holds around 201 GitHub stars and 6 forks across topics like `ai-agents`, `credentials`, `mcp`, `secrets-management`, and `security`. It requires an Apple Silicon Mac running macOS 14 or newer — Intel Macs are not supported.

The agent connection is a standard MCP server, so any MCP client can use the bundled `sp mcp` shim to reach `http.request`, `ssh.exec`, and configured upstream MCP servers. The tools Claude Code, Cursor, and Codex are what the project tests against.

## The Trust Model: A Fixed Decision Ladder (No Policy Language)

The most distinctive design choice is that Sallyport replaces policy configuration with a compiled decision ladder. Every action climbs the same four-step gate, and there is no policy language to misconfigure and no rules engine to rot.

1. **Vault gate.** The vault starts locked. Secure Enclave and Touch ID gate access to its data, and until the vault is unlocked Sallyport denies every agent action and all management operations except status.
2. **Per-call approval.** A key marked "Approval per call" requires a click or Touch ID for every single use — including inside an already-approved session.
3. **Session gate.** A new agent process shows one card with its code-signing authority. Approval lasts until the process exits, you revoke it, or the vault locks.
4. **Observe.** With per-session approval off, actions run without session cards and remain in the journal, with the vault gate and per-call approvals still enforced.

Mapped onto a procurement document, this is: zero standing privileges for a non-human identity, access granted just in time, and a human in the loop. Approvals use a click or Touch ID and resolve in process; they are not signed grants. A separate Secure Enclave signer signs audit rows and integrity anchors.

## How Sallyport Executes Authenticated Operations over MCP (HTTP, SSH, Remote & Local MCP)

Sallyport supports three families of channels through the MCP gate, all walking the same ladder into the same journal.

**HTTP APIs.** Via `http.request`, the app makes the HTTPS call itself and injects the credential only during execution — for example `http.request → api.github.com`. Cross-host redirects do not carry the credential, so a redirect hop cannot leak your token to a different host.

**SSH.** Via `ssh.exec` (for example `ssh.exec → deploy@prod-03`), a stateless helper opens the connection while the app itself handles SSH signatures, pins host keys, and seals a session recording. The private key never enters the helper. Sallyport sees the full SSH command before it runs and checks the host key, which closes the "opaque command" gap that many SSH gateways ignore.

**MCP servers.** Sallyport can proxy local stdio or remote MCP servers through the same gate — for example piping `github.create_issue` from an upstream server through the approval and journaling layer. It seals and refreshes OAuth 2.1 tokens for these upstream servers, matching the direction the MCP spec has moved: the spec mandates OAuth 2.1 with mandatory PKCE, Dynamic Client Registration (RFC 7591), Resource Indicators (RFC 8707), Protected Resource Metadata (RFC 9728), and CIMD for authentication.

## Installing Sallyport and Pointing Your Agent at the MCP Gate

Setup takes about two minutes, according to the project README. The install command is:

```
brew install --cask olegsotnikov/tap/sallyport
```

(You can equally download the signed and notarized DMG from sallyport.dev or the Releases page.)

With the app installed, launch it, create the vault, add a credential, and point any MCP client at the gate with a command like:

```
claude mcp add sallyport -- /Applications/Sallyport.app/Contents/MacOS/sp mcp
```

That registers Sallyport as a regular MCP server in Claude Code, and the same pattern covers Cursor and Codex. Your first gated call — from install to approval prompt — should land in about two minutes. Release checksums are published with each release and in `https://sallyport.dev/downloads/manifest.json`, so you can verify what you are running.

## Approvals, the Audit Journal, and Secure Enclave / Touch ID

Sallyport packages the vault, the approvals, and the journal into one signed Mac app.

**Encrypted at rest.** The vault encrypts key names, providers, host bindings, SSH inventory, settings, and secret values — not just the values but the surrounding metadata.

**Touch ID for changes.** Configuration changes can require Touch ID, and a synthetic click cannot satisfy the biometric prompt. This defeats the classic malware trick of faking a click.

**Process provenance.** Each approval card shows the caller's code-signing authority and its parent chain, including any unsigned process. You see who is actually asking before you approve.

**Write-blind journal.** Sallyport encrypts agent runs and per-call activity as it writes them, then links the ciphertext with a hash chain. A tampered journal entry breaks the chain and is visible in the audit trail.

**Observe mode** removes session cards but retains the vault gate, per-call approval, and the journal — useful once a workflow is trusted, while keeping a record.

There is deliberately **no recovery** path: no export, no reveal, and no recovery key. If you lose the vault, you re-initialize it and re-issue the stored credentials at their providers.

## The 2026 MCP-Credential Problem — Why This Category Exists

The tool-building moment is real. Anthropic shipped MCP tunnels on May 19, 2026, so credentials no longer have to ride inside the agent's context — a structural fix that validates the "keep the key out of the agent" model. GitGuardian's 2026 data gives the problem a concrete shape: 28.6 million new secrets exposed in public GitHub commits in 2025, with 24,008 unique credentials surfaced inside MCP config files and 2,117 of those still valid. Google API keys account for about 20% of MCP leaks and PostgreSQL connection strings about 14%.

The uncomfortable part is that most of these secrets sit in `.env` files and configs that the agent is *supposed* to read — which is exactly why traditional secret managers are insufficient. A tool that returns a credential into an environment the agent can read has not actually solved the problem. Sallyport's answer is to make the agent the caller rather than the holder, so there is no key in its environment to skip past — even under YOLO-style flags that disable an agent's own confirmation prompts. As the project notes, those prompts never protected the keys; the keys were readable in the environment all along.

## Sallyport vs. Alternatives (1Password, wardn, rapg, Arcade.dev, SecureCode)

Several tools approach the same problem from different directions. The table below is a quick comparison.

| Tool | Approach | Where the key lives | Best for |
|---|---|---|---|
| **Sallyport** | Executor: vault runs the action, agent never sees the key | Local encrypted vault on the Mac; no export | Mac-only, on-device, approval-heavy security |
| **1Password Environments MCP** | Injector: secrets injected at runtime for an authorized process; MCP returns names, not values | Cloud-backed vault | Teams already on 1Password, macOS/Linux, Cursor & Codex |
| **wardn** | Proxy with placeholder tokens; real key injected at the network layer | Local proxy between agent and tools | Open-source, structural guarantee, Claude Code/Cursor |
| **rapg** | Local-first `run` wrapper that injects env-tagged secrets into child processes; transcript redaction | Local, master-password gated | Keeping secrets off disk and scrollback |
| **Arcade.dev** | Cloud action runtime that vaults credentials and executes with account permissions at use-time | Centralized cloud vault | Execution-time authorization across a fleet |
| **SecureCode / GitGuardian** | Zero-knowledge inject into a 0600 session file the tool sources | Local session file | Practical Claude Code secrets management |

The key contrast is between injectors and executors. 1Password, rapg, and SecureCode hand the credential to a process (which on a developer machine tends to be the agent). Sallyport and Arcade.dev instead execute on the agent's behalf and return the result, so nothing hands a usable credential to the agent in the first place. wardn is closer to Sallyport's spirit but uses a network-layer proxy with placeholder tokens rather than an in-app executor. Two differences matter for evaluation: Sallyport is entirely on-device and Mac-only, while Arcade.dev is a cloud runtime; and wardn replaces values at the network layer while Sallyport attaches and spends the key inside the vault app.

## What Sallyport Deliberately Does Not Do — Residual Risk and Limits

Sallyport's official docs are explicit about the boundary it does not cross. The guarantee is *credential isolation*: the stored key never leaves the app. That is not the same as guaranteeing every result is clean.

- **Results can contain secrets.** Executor responses are returned as received. A target service that echoes your key back in its own response is showing you its bug, and the journal shows you the call that caught it — but the value did pass back through the agent's context.
- **Upstream MCP results are not scrubbed either.** Configured upstream servers get the credential you bind to them, so bind the narrowest one you have and flag it for per-call approval. Tool descriptions from upstream servers also land in the model's context as instructions, so they are instructions the agent will follow.
- **No reveal, export, or recovery route.** This is deliberate — it closes the exfiltration path — but it means that losing the vault requires re-issuing credentials at their providers. There is no back door.
- **The agent still runs with your rights.** Sallyport does not sandbox the agent or the rest of your machine; it protects credentials specifically. Treat the MCP dependency like any dependency that runs with your privileges, and route its calls through the gate and the journal.

## Is Sallyport Right for You? A Practical Decision Checklist

Use this to decide quickly.

- **You run an Apple Silicon Mac on macOS 14+**, and every alternative that fits your stack is on-device-first. If you need Linux or Windows, Sallyport is not for you.
- **Your agent touches real infrastructure** — Cloudflare, GitHub, SSH hosts — where one leaked token is expensive. The executor model removes the credential from the agent's environment entirely.
- **You want a fixed, auditable trust model** rather than a policy language. The four-step ladder with per-call and per-session gates is deliberately hard to misconfigure.
- **You are happy to re-issue keys on vault loss** and value a no-recovery design that closes export exfiltration. If you need a team recovery story, a cloud vault like 1Password Environments may fit better.
- **You want to keep secrets fully on-device** with no cloud, no account, and no telemetry — and you are willing to audit a public Apache-2.0 codebase yourself.

If you are on a Mac with the agent touching real infrastructure and you want the workload to operate rather than possess your keys, Sallyport is a two-minute install to a first gated call — and the whole credential-spending path is public on GitHub for you to audit before you trust it with anything.

## FAQ

**Is Sallyport free and open source?**
Yes. The core is free and open source under Apache-2.0, with no account, no cloud service, and no telemetry. It runs entirely on your Mac. Planned enterprise components will use a commercial license.

**Does Sallyport ever reveal my keys to the agent?**
No. There is no command that reveals a stored credential, no export, and no recovery route. The app attaches the key inside itself, executes the call, and returns only the target's response. The key never appears in the agent's environment.

**Which MCP clients does Sallyport work with?**
Any MCP client can use the bundled `sp mcp` shim to reach `http.request`, `ssh.exec`, and configured upstream MCP servers. The project tests against Claude Code, Cursor, and Codex, and you register it with a command like `claude mcp add sallyport -- /Applications/Sallyport.app/Contents/MacOS/sp mcp`.

**What hardware and macOS do I need?**
An Apple Silicon Mac running macOS 14 or newer. Intel Macs are not supported. Installation takes about two minutes via `brew install --cask olegsotnikov/tap/sallyport`.

**What happens if I lose the vault?**
There is no recovery key, export, or reveal route by design. You re-initialize the vault and re-issue the stored credentials at their providers. That is the deliberate trade-off: closing the exfiltration path also means no back door.
