---
title: "ACP Install Failed: What JetBrains' package_install_failed Log Line Actually Tells You (2026)"
description: "The line 'Agent installation failed for acp.registry.claude-acp: package_install_failed' names a package and one generic token, not a failing step. Six loopback cases against a stub ACP registry show five distinct server-side signatures that all collapse into that same message, plus an ordered seven-check pre-flight you can run before reinstalling."
date: 2026-11-12 00:00:00+00:00
lastmod: 2026-11-12 19:08:00+00:00
draft: false
schema: schema-jetbrains-acp-package-install-failed-diagnosis-2026
tags:
  - JetBrains
  - ACP
  - agent registry
  - install failure
  - package_install_failed
  - Claude Agent
  - AI Assistant
  - troubleshooting
  - Node.js runtime
  - SHA-256 verification
---

You clicked Install in the AI Assistant agent list, the agent never appeared in AI Chat, and the log shows one line:

```
WARN - #c.i.a.a.r.r.acpagentinstallationstate - Agent installation failed for acp.registry.claude-acp: package_install_failed
```

That line is what a reader pasted into a search engine on 2026-11-06, and it is the entire failure report: a package id, a colon, and a token that says "package install failed". It does not say which step failed, what the HTTP status was, or whether anything was downloaded at all.

Here is the direct answer this article can defend. `package_install_failed` is a single bucket name for the client's installation path, and the documented installation path has seven places that can fail before an agent ever starts a JSON-RPC session: fetching the registry index, finding your agent's entry in it, the entry's schema, selecting a distribution for your platform, downloading the artifact, matching the artifact's SHA-256, and resolving a runtime the entry needs. Every one of those failures can end in the same sentence. The token is not a diagnosis; it is a label on an empty box.

What does narrow it is a check order. This article publishes a runnable pre-flight (`acp_install_check.py`) and the six-case fixture used to test it, including the one case where the checker must return PASS so you know a clean install does not produce a false alarm.

## What the string actually contains

Three parts, none of them a stage:

- `acp.registry.claude-acp` — the registry id, `claude-acp`, prefixed by the source it came from. This tells you the install came from the registry rather than from a hand-written [`acp.json`](https://www.jetbrains.com/help/ai-assistant/acp.html), which is a different code path with a different failure surface.
- `package_install_failed` — the bucket. It reads like "the package did not install", which is true of every failure in the install path.
- `#c.i.a.a.r.r.acpagentinstallationstate` — a client-internal class reference. It is not documented anywhere in JetBrains' published help, and this article does not expand the abbreviation. Guessing that `a.a.r.r` means "agent assistant registry resolver" would be invention dressed as evidence.

The JetBrains help page describes installation as three automatic steps: "Downloads the required agent files", "Downloads and manages a Node.js or Python runtime if required", and "Prepares the agent for use" ([AI Assistant ACP documentation](https://www.jetbrains.com/help/ai-assistant/acp.html)). Three documented steps, zero documented error taxonomy. A four-word token cannot span them.

## The contract the installer is actually reading

The ACP registry is not a per-agent manifest service. It is one index document whose entries carry their own distribution blocks ([registry FORMAT.md](https://raw.githubusercontent.com/agentclientprotocol/registry/main/FORMAT.md)):

- the index has a `version` and an `agents` array;
- each entry has `id`, `name`, `version`, `description`, `repository`, `authors`, `license`, and a required `license_url` — the format says the field "is required and must link to the agent's license text or terms of service", with one named exemption;
- each entry has a `distribution` object with one or more of `binary` (keyed by platform: `darwin-aarch64`, `linux-x86_64`, `windows-x86_64`, plus `-musl` variants), `npx`, and `uvx`;
- each binary target may carry `archive`, `sha256`, `cmd`, `args`, `env` — the SHA-256 is documented as an integrity check, and the field is optional;
- installer formats such as `.dmg`, `.pkg`, `.deb`, `.rpm`, `.msi` are explicitly not supported, only `.zip`, `.tar.gz`, `.tgz`, `.tar.bz2`, `.tbz2` or a raw binary.

JetBrains IDEs read a dedicated index at `cdn.agentclientprotocol.com`, not the generic one, and there is a separate preview channel ([registry README](https://raw.githubusercontent.com/agentclientprotocol/registry/main/README.md)). The live JetBrains index is a single JSON document, and the entry for `claude-acp` at version 0.106.0 declares both a per-platform binary with a SHA-256 and an `npx` fallback ([registry-for-jetbrains.json](https://cdn.agentclientprotocol.com/registry/v1/latest/registry-for-jetbrains.json)). The index also carries an `environments.node` block pinning Node.js 24.22.1 with per-platform hashes — that is the shape of the "downloads and manages a Node.js runtime" promise, though nobody documents the client actually consuming that block, so treat it as correlation.

The corresponding npm package declares `engines.node: ">=22"` and a `claude-agent-acp` bin ([npm metadata](https://registry.npmjs.org/@agentclientprotocol/claude-agent-acp), [package.json](https://raw.githubusercontent.com/agentclientprotocol/claude-agent-acp/main/package.json)). The registry README also says every listed agent is CI-verified for `authMethods` in the ACP handshake, and the launch post says only agents supporting Agent Auth or Terminal Auth are featured ([JetBrains registry launch](https://blog.jetbrains.com/ai/2026/01/acp-agent-registry/)). That matters for expectations: an agent passing the auth conformance check is not the same as an agent whose archive exists for your platform.

One correction to our own earlier coverage: [our registry guide](https://baeseokjae.github.io/posts/jetbrains-acp-agent-registry-guide-2026/) says that when an agent needs an external binary, "the IDE surfaces a clear error message pointing you to the installation page — it does not silently fail." That claim is too generous. Nothing here is silent, but a message that names only a package and a bucket is not the clear pointer the guide promised, and the guide's menu path ("Settings → Tools → AI Agents → Registry") no longer matches the current documentation, which places agents under "Settings | Tools | AI Assistant | Agents". Both statements are documentation drift, and readers who followed either one deserved better than this log line.

## Six cases, one message

Documentation tells you which fields exist. It cannot tell you which field broke. So the fixture serves the real contract on loopback and breaks it one field at a time.

The stub registry (`acp_stub_registry.py`) serves exactly two routes: the index at `/registry-for-jetbrains.json` and artifacts under `/artifacts/`. It logs every request — method, path, status, bytes, latency — to a JSONL transcript, so the server-side signature of each defect is a record rather than a description. The runner (`run_defects.py`) builds a fresh fixture per case, binds a fresh ephemeral port, runs the checker once, and stores the transcript beside the checker output.

Environment for the published run: Python 3.12.3, Node.js v24.21.0, npm 11.19.0, Linux 6.17.0 on aarch64, loopback only, no network, no credentials. The checker is told to evaluate `linux-x86_64` as the target platform and never executes an artifact; nothing in this fixture downloads or runs third-party code. All six cases together took 2.6 seconds of wall clock (recorded as `wall_clock_s` in `results.json`). No IDE build is passed to the checker, because there is no JetBrains IDE on the host that produced these records.

| Case | What the server actually did | Failing check | Exit | Signature visible in the log line? |
| --- | --- | --- | --- | --- |
| D0 clean | 200 index (1425 bytes), 200 artifact (208 bytes), hash matches | none | 0 | n/a — a healthy install is the control |
| D1 index 404 | index route returns 404, no agent data ever sent | `index_fetch` | 1 | No. Same bucket. |
| D2 entry schema | index 200, entry present, `license_url` missing | `entry_schema` | 1 | No. Same bucket. |
| D3 checksum | index 200, artifact 200 (246 bytes), served bytes hash differently | `artifact_sha256` | 1 | No. Same bucket. |
| D4 unreachable artifact | index 200, artifact host refuses the connection; the transcript contains no artifact request at all | `artifact_fetch` | 1 | No. Same bucket. |
| D5 platform gap | index 200, entry declares only `darwin-aarch64`, no `npx`/`uvx` fallback | `distribution_select` | 1 | No. Same bucket. |

Five injected defects produced five distinct failing checks and zero false passes, and the clean control passed every check that could run on the host. The transcript for D4 is one line long — the index request — because the artifact request never reached a server. That absence is itself a signature: a refused connection leaves no server-side record, which is exactly why an install failure with an empty download log looks the same as a schema rejection.

What the experiment does not show: it does not reproduce the IDE. There is no JetBrains IDE on the machine that produced these records, so the log line is treated as user-reported and the client's internal mapping from failure to message is not claimed. The fixture proves that the contract layer admits five failures that a single token cannot separate. It does not prove what the client prints for each, and it cannot, from the outside.

## The pre-flight, in order

Run these in order and stop at the first FAIL. Each check costs seconds and eliminates whole layers. The script prints PASS, FAIL or SKIP per check and exits non-zero on the first failure, but you can do the first three by hand in a terminal.

1. **Index reachability.** `curl -sS -o /dev/null -w '%{http_code}\n' https://cdn.agentclientprotocol.com/registry/v1/latest/registry-for-jetbrains.json`. A 200 means the client can at least read the catalog. A 403 or 407 means a proxy or egress filter, not an agent problem. A DNS failure means your network path, full stop. If you are on the preview channel, the URL ends `-preview.json`, and those distributions are documented as not verified for reachability — a preview entry can legitimately point at something that is not there.
2. **Your IDE build.** The registry shipped as beta for IDE versions 2025.3 and later, with a matching AI plugin update ([launch post](https://blog.jetbrains.com/ai/2026/01/acp-agent-registry/)). An older build is a plausible cause class and is checkable locally in Help → About. The registry format itself encodes no minimum-IDE field, so no server response will ever tell you this; it is a client-side gate.
3. **Your entry's schema.** Fetch the index and confirm the entry has `id`, `name`, `version`, `repository`, `license_url` and `distribution`. `license_url` is documented as required. A registry entry can be structurally invalid and still be published for a while, which is why D2 is a real failure mode rather than a hypothetical.
4. **A distribution for your platform.** Look inside `distribution.binary` for your exact key (`linux-x86_64` is glibc x86-64; Alpine needs `linux-x86_64-musl`). The format is explicit that a missing musl target must be treated as unavailable rather than silently substituted with a glibc build. If there is no binary for you, the `npx` or `uvx` fallback is the path — and that path has its own runtime requirement.
5. **Artifact reachability.** Take the `archive` URL from the entry and fetch it. A 404 means the index points at a release that has been withdrawn; the client will report a generic install failure, and the registry is the thing that is wrong. A connection refused, as in D4, means the host is unreachable from your machine only.
6. **Checksum.** `sha256sum` the downloaded bytes and compare with the entry's `sha256`. A mismatch is not a corrupted agent; it is bytes that are not the declared release, which in practice means a truncated download, a proxy that rewrote content, or a republished file that did not bump its version. The format lists the field as optional, so a SKIP here is legitimate and not a failure.
7. **Runtime.** If the entry resolves to `npx`, you need Node on PATH — the shipped package declares `node >= 22`. If a binary distribution exists and Node does not, the runtime check is irrelevant and the script says SKIP rather than inventing a verdict.

Two conditions the checker cannot see and you must check yourself: WSL is documented as unsupported for ACP agents in JetBrains IDEs, so an install attempted from a WSL-hosted project is not a supported configuration; and an offline or air-gapped machine needs a mirror for both the registry host and the artifact host, not just npm.

## Reading the log without leaking your session

You can raise log detail. The AI Assistant help page documents enabling the `llm.agent.extended.logging` registry key, which captures "all requests sent to agents and their responses" ([AI Assistant ACP documentation](https://www.jetbrains.com/help/ai-assistant/acp.html)). That is the right switch for a transport-level failure and the wrong thing to paste into a public issue: agent requests contain your prompts, file paths and repository names. Before sharing, redact to the lines around the failure and strip request bodies.

Note what extended logging will and will not give you. The agent handshake is JSON-RPC over stdio, so once an agent launches you get request and response frames ([ACP protocol overview](https://agentclientprotocol.com/protocol/overview.md)). An install failure happens *before* that handshake exists, which is why raising agent log verbosity often produces nothing at all — there is no session to log. Absence of ACP frames is consistent with every one of the five defects above.

## If every check passes

Then the failure is in the client's own install path, not in the contract, and the useful report is a set of facts rather than a stack of retries. Include: IDE product and build, AI plugin version, OS and architecture, the exact index URL, the entry's `version` and `sha256` from the index, the HTTP status you observed for the archive, and the SHA-256 of the bytes you actually received. That last pair is the discriminator a maintainer needs, because it separates "we published it and you cannot reach it" from "you received something else".

Two honest limits on that report. The registry index is regenerated hourly, so capture the entry you saw rather than describing it from memory. And the preview channel is documented as never launched, never auth-checked and never probed for reachability — if you opted into preview, a broken artifact is expected behaviour, not a bug report.

## Reproduce it

Everything is first-party and offline. The scripts, the six fixtures and every transcript are in the article's evidence directory; no vendor code, credentials or downloads are included:

- checker: [acp_install_check.py](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/jetbrains-acp-package-install-failed-diagnosis-2026/run/acp_install_check.py)
- stub registry: [acp_stub_registry.py](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/jetbrains-acp-package-install-failed-diagnosis-2026/run/acp_stub_registry.py)
- runner: [run_defects.py](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/jetbrains-acp-package-install-failed-diagnosis-2026/run/run_defects.py)
- aggregate record and environment: [results.json](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/jetbrains-acp-package-install-failed-diagnosis-2026/run/results.json)
- method, including the two recorded deviations from the research plan: [method.md](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/jetbrains-acp-package-install-failed-diagnosis-2026/run/method.md)
- server-side transcripts, one per case: [D0_clean](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/jetbrains-acp-package-install-failed-diagnosis-2026/run/transcripts/D0_clean.jsonl), [D1_index_404](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/jetbrains-acp-package-install-failed-diagnosis-2026/run/transcripts/D1_index_404.jsonl), [D2_missing_license_url](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/jetbrains-acp-package-install-failed-diagnosis-2026/run/transcripts/D2_missing_license_url.jsonl), [D3_checksum_mismatch](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/jetbrains-acp-package-install-failed-diagnosis-2026/run/transcripts/D3_checksum_mismatch.jsonl), [D4_artifact_unreachable](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/jetbrains-acp-package-install-failed-diagnosis-2026/run/transcripts/D4_artifact_unreachable.jsonl), [D5_platform_gap](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/jetbrains-acp-package-install-failed-diagnosis-2026/run/transcripts/D5_platform_gap.jsonl)
- checker output and exit code, one per case: [D0_clean](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/jetbrains-acp-package-install-failed-diagnosis-2026/run/checker/D0_clean.txt), [D1_index_404](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/jetbrains-acp-package-install-failed-diagnosis-2026/run/checker/D1_index_404.txt), [D2_missing_license_url](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/jetbrains-acp-package-install-failed-diagnosis-2026/run/checker/D2_missing_license_url.txt), [D3_checksum_mismatch](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/jetbrains-acp-package-install-failed-diagnosis-2026/run/checker/D3_checksum_mismatch.txt), [D4_artifact_unreachable](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/jetbrains-acp-package-install-failed-diagnosis-2026/run/checker/D4_artifact_unreachable.txt), [D5_platform_gap](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/jetbrains-acp-package-install-failed-diagnosis-2026/run/checker/D5_platform_gap.txt)

```
python3 run_defects.py --out .
python3 acp_install_check.py --registry http://127.0.0.1:8000/registry-for-jetbrains.json \
  --agent claude-acp --platform linux-x86_64
```

Point the second command at the real index instead of a loopback port and it becomes the pre-flight described above; the fixture is only there so the checker's verdicts can be audited against known-bad inputs.

If you are still deciding which agent to install rather than why one failed, the protocol layer is covered in [MCP, A2A and ACP compared](/posts/ai-agent-protocols-mcp-a2a-acp-2026/); if your failure is after launch rather than during install, process spawn and lifecycle failures are the closer analogue in [MCP stdio transport lifecycle](/posts/mcp-stdio-transport-lifecycle-2026/); and the agent in the measured log line is Anthropic's, covered in [the Claude Code tutorial](/posts/claude-code-tutorial-2026/).

The one-sentence version: the log line tells you the install did not complete, and nothing else. The check order above tells you where — and if all seven pass, you now have the evidence to say the problem is not on your machine.
