---
cover:
  alt: "Claude Code Network Sandbox SOCKS5 Null-Byte Bypass Guide 2026"
  image: /images/claude-code-network-sandbox-socks5-null-byte-bypass-guide-2026.png
  relative: false
date: 2026-06-22 00:00:00+00:00
description: "Complete guide to the Claude Code SOCKS5 null-byte sandbox bypass (v2.0.24–v2.1.89), how the parser differential worked, disclosure timeline, and mitigation steps."
draft: false
schema: schema-claude-code-network-sandbox-socks5-null-byte-bypass-guide-2026
tags:
- claude-code
- anthropic
- sandbox-bypass
- socks5
- null-byte-injection
- parser-differential
- agent-security
title: "Claude Code Network Sandbox SOCKS5 Null-Byte Bypass: The 5.5-Month Hole in Anthropic's Agent Egress Control"
---

Every Claude Code release from v2.0.24 (October 20, 2025) through v2.1.89 (March 31, 2026) shipped a network sandbox that was trivially bypassable with a single null byte. If you ran Claude Code with a wildcard allowlist like `*.google.com`, any code executing inside the sandbox — whether through prompt injection, a malicious dependency, or a compromised repo — could reach any host on the internet by sending a SOCKS5 hostname like `attacker-host.com\x00.google.com`. The JavaScript allowlist filter saw the trailing `.google.com` and approved the connection; the OS resolver truncated at the null byte and dialed `attacker-host.com`. This is a parser-differential vulnerability in its purest form, and as of June 2026, it still has no CVE assigned to Claude Code itself.

## How the Claude Code Network Sandbox Works

Claude Code's sandbox relies on two OS-level primitives — `bubblewrap` on Linux and `seatbelt` (sandbox-exec) on macOS — to isolate the Bash tool subprocess. These primitives strip the network namespace and pin all traffic to localhost ports where two proxy servers run on the host:

- An **HTTP proxy** handling HTTPS traffic against an allowlist
- A **SOCKS5 proxy** handling all other TCP traffic (SSH, database connections, raw TCP) against the same allowlist

The configuration lives in `~/.claude/settings.json`:

```json
{
  "sandbox": {
    "enabled": true
  },
  "allowedDomains": ["*.google.com"]
}
```

The sandbox injects `ALL_PROXY=socks5h://127.0.0.1:<port>` into the subprocess environment. Every TCP connection the subprocess makes goes through that SOCKS5 proxy, which checks the destination hostname against the configured allowlist before forwarding.

## The SOCKS5 Null-Byte Bypass: Root Cause Analysis

The vulnerability lives in the `@anthropic-ai/sandbox-runtime` library, versions 0.0.1 through 0.0.42. The SOCKS5 proxy implementation received a CONNECT request containing a DOMAINNAME field — raw bytes from the wire — and passed them directly into a JavaScript `endsWith()` check against the allowlist:

```javascript
// Vulnerable logic (sandbox-runtime <= 0.0.42)
function isAllowed(hostname) {
  return allowedDomains.some(pattern =>
    hostname.endsWith(pattern.replace('*.', '.'))
  );
}
```

The same raw bytes were then handed to libc's `getaddrinfo()` for DNS resolution. Here is where the disagreement happens:

| Layer | Sees | Interprets |
|-------|------|------------|
| JS `endsWith()` | `attacker.com\x00.google.com` | Ends with `.google.com` → **ALLOW** |
| libc `getaddrinfo()` | `attacker.com\0...` | C string terminates at `\x00` → resolves `attacker.com` |
| Network socket | `attacker.com` IP | Connects to the attacker's host |

JavaScript treats `\x00` (U+0000) as a valid UTF-16 code unit — the string is 30 characters long. C treats it as a null terminator — the string is 13 characters long. The same bytes, two interpretations. The attacker controls the bytes, and the filter and the resolver agree on different hostnames.

## Disclosure Timeline

The sandbox was bypassable from the moment it shipped GA. The timeline of what happened spans two distinct vulnerabilities:

| Date | Event |
|------|-------|
| **2025-10-20** | Claude Code v2.0.24 ships network sandbox GA. Vulnerable to two bypasses from day one. |
| **2025-11-26** | Finding 1 (CVE-2025-66479) silently patched in v2.0.55: empty `allowedDomains: []` meant "block nothing" instead of "block everything." Same release still carries the SOCKS5 null-byte bypass. |
| **2025-12-02** | CVE-2025-66479 published against sandbox-runtime library only. Not against Claude Code. No user-facing advisory. |
| **2026-03-27** | sandbox-runtime commit `fd74a3f` adds `isValidHost()` rejecting `\x00`, `%`, CRLF, and non-DNS characters. |
| **2026-03-31** | Fix ships in Claude Code v2.1.88 per Anthropic (v2.1.90 per Guan). Changelog says nothing about a security fix. |
| **2026-04-01** | v2.1.90 broadly available. Still no security note. |
| **2026-04-03** | Aonan Guan reports to Anthropic via HackerOne. Closed as duplicate. |
| **2026-05-20** | Public disclosure by Guan. No CVE for Claude Code. No advisory published. |

## Two Bugs, Zero Advisories

This was the second complete sandbox bypass in five months. The two vulnerabilities cover different configurations:

| Dimension | CVE-2025-66479 | SOCKS5 Null-Byte (no CVE) |
|-----------|----------------|---------------------------|
| **Trigger** | `allowedDomains: []` | Wildcard allowlist (`*.google.com`) |
| **Filter sees** | Empty list → proxy not attached | endsWith match → allow |
| **OS sees** | No proxy → unrestricted egress | getaddrinfo truncates at \x00 → blocked host resolved |
| **Class** | Configuration semantics bug | Parser differential |
| **Affected** | v2.0.24–v2.0.54 (32 days) | v2.0.24–v2.1.89 (165 days) |
| **CVE for Claude Code** | None | None |
| **Advisory** | None (CVEs for library only) | None |

CVE-2025-66479 carries a CVSS score of 1.8 — which is almost absurd for a complete egress bypass. The SOCKS5 bypass has no CVE at all, even though it exposed roughly 130 releases over 5.5 months.

## The Attack Chain in Practice

The bypass alone is useless without code execution inside the sandbox. But prompt injection research — particularly the "Comment and Control" technique — shows that an attacker can place malicious instructions in a GitHub issue comment, a PR description, or a README file that Claude Code ingests during a session. The attack chain looks like this:

```
Step 1: Attacker embeds instructions in a GitHub issue comment
Step 2: Claude Code processes the issue during a PR review task
Step 3: Injected instructions trigger a sandboxed Bash command
Step 4: The Bash command reads ~/.aws/credentials, environment variables
Step 5: Exfiltrates data via SOCKS5 with crafted null-byte hostname
Step 6: Data reaches attacker server, bypasses standard HTTP egress logs
```

The data an attacker can extract includes:
- AWS credentials from `~/.aws/credentials` and `~/.aws/config`
- GitHub tokens from `~/.config/gh/hosts.yml`
- Cloud instance metadata via `169.254.169.254` (IMDS)
- Environment variables containing API keys and database URLs
- SSH private keys and corporate intranet resources
- Full source code accessible to the sandboxed process

## The Fix: isValidHost()

Anthropic's fix in sandbox-runtime 0.0.43 introduces an `isValidHost()` function that validates hostname characters before the allowlist matcher runs:

```javascript
// Fixed logic (sandbox-runtime >= 0.0.43)
function isValidHost(hostname) {
  // Reject null bytes, percent-encoding, CRLF, and non-DNS characters
  if (/[\x00%]/.test(hostname)) return false;
  if (hostname.includes('\r') || hostname.includes('\n')) return false;
  // Additional DNS character validation
  return /^[a-zA-Z0-9._-]+$/.test(hostname);
}
```

This prevents the parser differential by ensuring only valid DNS characters reach both the JavaScript filter and libc. But it raises a question: are there Unicode normalization or IDN homograph variants that could still slip through? The `isValidHost()` regex is strict, which is good, but security researchers will likely test the boundary.

## Why This Matters Beyond Anthropic

The SOCKS5 null-byte bypass is a textbook example of a **parser differential** — a class of vulnerability where two system components interpret the same input differently. These bugs are notoriously hard to catch in testing because both layers behave correctly in isolation. The JS function returns the right answer for its string model. libc returns the right answer for its string model. The bug only exists at the seam between them.

I've found that parser differentials are especially common in agent security boundaries because agents sit at the intersection of multiple language runtimes. The Node.js process running the proxy passes data to a C library for DNS resolution. A Python agent might pass shell commands through `subprocess.Popen` with `shell=True`. Every language boundary is a potential differential. Every implicit type conversion between layers is an opportunity for bypass.

The architectural lesson is clear: **validate at the trust boundary in the format the downstream consumer uses**. The SOCKS5 proxy should have validated the hostname against DNS character rules *before* checking the allowlist, then passed only validated bytes to `getaddrinfo()`. Better yet, it should have resolved the hostname to an IP, then checked the IP against the allowlist — eliminating the JS/C string disagreement entirely.

## Mitigation and Hardening Steps

If you have ever run Claude Code in production, here is what you need to do:

**Immediate actions:**
1. Confirm your Claude Code version: `claude --version`. Anything below v2.1.90 is vulnerable.
2. Upgrade: `npm install -g @anthropic-ai/claude-code@latest`
3. Pin the version in your Dockerfiles, Brewfiles, and CI configuration.
4. Audit outbound egress logs for SOCKS5 traffic (TCP port 1080) originating from machines that ran vulnerable versions.
5. Rotate AWS credentials, GitHub tokens, and other secrets the sandboxed process could access.

**Configuration hardening:**
- Avoid wildcard allowlists. Use explicit hostnames where possible.
- Add `denyRead` entries for `~/.aws/`, `~/.ssh/`, `~/.config/gh/`, and `~/.kube/`.
- Strip sensitive environment variables from the sandboxed process.
- Set `sandbox.failIfUnavailable: true` and `sandbox.allowUnsandboxedCommands: false`.
- Block cloud metadata endpoints (`169.254.169.254`) at the network layer.

**Architectural recommendations:**
- Use disposable VMs or containers for untrusted repositories. Do not give long-lived credentials to an agent session.
- Separate human credentials from agent credentials. Use short-lived, scoped tokens via OAuth device flow or STS.
- Implement external egress controls beyond the agent's built-in sandbox — a corporate proxy or firewall that enforces the egress policy independently.
- Treat project-level agent configuration (`.claude/settings.json`, `.mcp.json`, `CLAUDE.md`) as executable code. Review it the same way you review a Dockerfile.

For deeper context on agent security tooling, see the [AI Agent Security Tools 2026 guide](/posts/ai-agent-security-tools-2026/) and the [Claude Code Vulnerability Detection Guide](/posts/claude-code-vulnerability-detection-guide-2026/).

## Frequently Asked Questions

### Which Claude Code versions were affected?

All releases from v2.0.24 (October 20, 2025) through v2.1.89 (March 31, 2026) — approximately 130 versions over 5.5 months. If you used Claude Code during that window with the network sandbox enabled and a wildcard allowlist, you were vulnerable.

### How do I check my current Claude Code version?

Run `claude --version` in your terminal. If the output is lower than 2.1.90, upgrade immediately with `npm install -g @anthropic-ai/claude-code@latest`.

### Does this bypass work without a wildcard allowlist?

No. The bypass requires a wildcard pattern like `*.google.com` in the `allowedDomains` setting. If you list exact hostnames only — `["api.anthropic.com", "github.com"]` — the null-byte technique will not match those suffixes after the truncation. However, note that the earlier CVE-2025-66479 meant that an empty `allowedDomains: []` disabled the proxy entirely for the first 32 days of the sandbox's life.

### Did Anthropic notify users about this vulnerability?

No. Anthropic did not publish a security advisory, flag the fix in the v2.1.90 changelog, assign a CVE for Claude Code, or contact users directly. The only CVE issued, CVE-2025-66479, was assigned to the upstream sandbox-runtime library, not to Claude Code itself. Most users learned about the bypass through third-party security journalism or Aonan Guan's disclosure post.

### What other data could an attacker exfiltrate using this bypass?

In combination with prompt injection, an attacker could extract AWS credentials, GitHub personal access tokens, environment variables containing API keys, cloud instance metadata, SSH private keys, corporate intranet resources, and any source code the sandboxed process could read. Since SOCKS5 does not generate standard HTTP access logs, this traffic is harder to detect in conventional logging pipelines.
