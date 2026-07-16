---
title: "MCP Snoop Review 2026: Wireshark for MCP — Transparent Proxy for Tool Call Debugging"
date: 2026-07-16T21:05:12+00:00
tags:
  - MCP
  - debugging
  - observability
  - open-source
  - tool-review
description: "mcpsnoop is a transparent MCP proxy that captures every JSON-RPC frame between client and server in real time, making it the Wireshark for MCP debugging."
draft: false
cover:
  image: "/images/mcpsnoop-wireshark-mcp-2026.png"
  alt: "MCP Snoop Review 2026: Wireshark for MCP — Transparent Proxy for Tool Call Debugging"
  relative: false
schema: "schema-mcpsnoop-wireshark-mcp-2026"
---

## What is mcpsnoop? — Wireshark for MCP

mcpsnoop is an open-source transparent proxy for the Model Context Protocol (MCP) that sits between your MCP client and server, capturing every JSON-RPC frame in real time. Built in Go with a Bubble Tea terminal UI, it gives developers the same kind of deep packet inspection for MCP traffic that Wireshark provides for network packets. Launched in late June 2026, mcpsnoop reached 270 GitHub stars in just three weeks and is rapidly becoming the go-to tool for MCP debugging.

## The Problem — Why MCP Inspector Falls Short

The official MCP Inspector from MCPJam is the most popular MCP debugging tool with 2,068 stars, but it has a fundamental limitation: it connects to your MCP server as its own client. This means it never sees the actual traffic between your real client and server. When a tool silently isn't called, capabilities don't line up, or a call just hangs, MCP Inspector can't help you see what your actual client is sending or receiving.

This is the equivalent of debugging a network issue by running a separate ping test instead of looking at the actual packets on the wire. You need a tool that sits in the real data path — and that is exactly what mcpsnoop provides.

## How mcpsnoop Works — Transparent Proxy Architecture

mcpsnoop uses a dual-role architecture that separates the concerns of traffic capture and session inspection. The system has two components: a **shim** that forwards frames and copies them to a hub, and a **hub** that runs the TUI and stores session data.

### Stdio Shim Mode (mcpsnoop -- <server>)

In stdio mode, you wrap your MCP server command with mcpsnoop:

```bash
mcpsnoop -- npx @anthropic-ai/claude-code-server
```

The shim intercepts every stdin/stdout message between the client and server, forwards them transparently, and copies each JSON-RPC frame to the hub for live inspection. The client and server never know mcpsnoop is there — it is a completely transparent proxy.

### HTTP Reverse Proxy Mode (mcpsnoop http)

For HTTP-based MCP servers, mcpsnoop provides a reverse proxy mode:

```bash
mcpsnoop http --target http://localhost:8080
```

This starts an HTTP server that forwards all requests to the target MCP server while capturing every request and response for inspection. This mode is ideal for debugging MCP servers that communicate over HTTP/SSE.

### Dual-Role Design: Shim + Hub + TUI

The shim runs as a lightweight stdio forwarder that copies frames to the hub over a local connection. The hub aggregates frames from one or more shims, stores them in a session store, and feeds them to the Bubble Tea TUI for real-time display. This separation means you can run the shim on a remote machine and the hub locally, or run multiple shims feeding into a single hub for cross-session analysis.

## Key Features Deep Dive

### Live TUI with Real-Time Frame Inspection

The terminal UI is built with the Bubble Tea framework and provides a real-time view of every MCP frame flowing through the proxy. Each frame is displayed with its direction (client→server or server→client), method name, ID, status, and timing. You can scroll through the live stream, select individual frames to see their full JSON-RPC payload, and watch the conversation unfold in real time.

### Filtering System (tool:, method:, id:, dir:, kind:, status:)

mcpsnoop's filtering system is one of its most powerful features. You can filter the live frame stream using keybindings that support:

- **tool:** — Filter by tool name (e.g., `tool:search_files`)
- **method:** — Filter by JSON-RPC method (e.g., `method:tools/call`)
- **id:** — Filter by request ID
- **dir:** — Filter by direction (`dir:in` for server responses, `dir:out` for client requests)
- **kind:** — Filter by frame kind (request, response, notification, error)
- **status:** — Filter by status (success, error, pending)

This makes it trivial to isolate a single tool call among hundreds of frames in a busy session.

### Session Export (JSON, HTML, Text, OTLP)

mcpsnoop supports exporting captured sessions in multiple formats:

- **JSON** — Full structured export for programmatic analysis
- **HTML** — Interactive HTML report for sharing with team members who don't have mcpsnoop installed
- **Text** — Plain text log for quick review or inclusion in bug reports
- **OTLP (OpenTelemetry)** — Export to OpenTelemetry-compatible backends like Jaeger, Grafana Tempo, or Datadog for integration with existing observability infrastructure

The OTLP export is particularly valuable for teams that already use distributed tracing — it turns MCP tool calls into spans that appear alongside your application traces.

### CI Check Mode — Gate Builds on MCP Errors

One of mcpsnoop's most unique features is its CI check mode. You can run mcpsnoop in a CI pipeline and it will:

- Fail the build if any MCP errors occur
- Flag invalid JSON-RPC frames
- Warn on slow calls exceeding a configurable threshold
- Detect pending calls that never received a response
- Report warnings for suspicious patterns

This turns MCP debugging from a reactive firefighting exercise into a proactive quality gate. If your MCP server starts returning errors after a deployment, your CI pipeline catches it before it reaches production.

```bash
mcpsnoop --check -- npx @anthropic-ai/claude-code-server
```

### Remote SSH Tunnel — Debug Remote Servers

mcpsnoop supports SSH tunneling for debugging MCP servers running on remote machines. You can start a shim on a remote server and connect to it from your local machine:

```bash
mcpsnoop --ssh user@remote-server -- npx @anthropic-ai/claude-code-server
```

The TUI runs locally while the shim runs on the remote machine, giving you the same real-time inspection experience for remote MCP traffic.

### Secret Redaction — Safe Trace Sharing

When sharing MCP session traces for debugging or collaboration, you often need to redact sensitive information like API keys, tokens, or personal data. mcpsnoop provides three levels of secret redaction:

- **Key-based** — Redact values for specific JSON keys
- **JSONPath-based** — Redact values matching a JSONPath expression
- **Regex-based** — Redact values matching a regular expression pattern

Redaction rules can be configured in the `.mcpsnoop.toml` config file, making them reusable across sessions.

### Call Replay — Re-run Captured Tool Calls

mcpsnoop can replay captured tool calls against a server. This is invaluable for regression testing — if a tool call worked in one session but fails in another, you can replay the exact same request to isolate whether the issue is in the client, server, or network.

## mcpsnoop vs. Competitors

The MCP debugging ecosystem has grown rapidly, with at least six dedicated tools as of mid-2026. Here is how mcpsnoop compares:

| Feature | mcpsnoop | MCP Inspector | reloaderoo | mcp-interceptor | mcpobservatory |
|---|---|---|---|---|---|
| **Stars** | 270★ | 2,068★ | 125★ | 7★ | 4★ |
| **Language** | Go | TypeScript | TypeScript | TypeScript | Rust |
| **License** | MIT | MIT | MIT | MIT | Apache-2.0 |
| **Transparent proxy** | ✅ Yes | ❌ No (own client) | ✅ Yes | ✅ Yes | ✅ Yes |
| **Live TUI** | ✅ Bubble Tea | ✅ Web UI | ❌ CLI only | ❌ CLI only | ✅ Timeline |
| **CI check mode** | ✅ Yes | ❌ No | ❌ No | ❌ No | ❌ No |
| **OTLP export** | ✅ Yes | ❌ No | ❌ No | ❌ No | ❌ No |
| **SSH tunnel** | ✅ Yes | ❌ No | ❌ No | ❌ No | ❌ No |
| **Secret redaction** | ✅ Yes | ❌ No | ❌ No | ❌ No | ❌ No |
| **Call replay** | ✅ Yes | ❌ No | ❌ No | ❌ No | ✅ Yes |
| **Session export** | JSON, HTML, Text, OTLP | Limited | JSON | JSON | JSON |
| **Single binary** | ✅ Yes | ❌ No (Node.js) | ❌ No (Node.js) | ❌ No (Node.js) | ✅ Yes |
| **Created** | June 2026 | May 2025 | June 2025 | June 2025 | April 2026 |

### vs. MCP Inspector (2,068★)

MCP Inspector is the most established tool with the largest community, but it serves a different purpose. It is an evaluation and testing platform that connects to MCP servers as its own client — great for testing a server in isolation, but useless for debugging real client-server interactions. mcpsnoop is the better choice when you need to debug actual production traffic.

### vs. reloaderoo (125★)

reloaderoo is a capable debugging proxy with a CLI focus. It lacks the live TUI, CI check mode, OTLP export, and SSH tunnel features that mcpsnoop offers. reloaderoo is more mature (created June 2025) but has not kept pace with mcpsnoop's rapid feature development.

### vs. mcp-interceptor (7★)

mcp-interceptor is a lightweight proxy that focuses on request interception via a proxy URL. It is simple and gets the job done for basic debugging, but lacks the depth of features that mcpsnoop provides for serious MCP observability work.

### vs. mcpobservatory (4★)

mcpobservatory is the closest competitor to mcpsnoop in terms of positioning — a Rust-based drop-in proxy with timeline, replay, and diff capabilities. It is local-first with no telemetry and ships as a single binary. However, with only 4 stars and a much smaller community, it has not gained the same traction as mcpsnoop.

## Getting Started — Quick Setup Guide

Getting started with mcpsnoop takes less than a minute:

1. **Download the binary** from the [GitHub releases page](https://github.com/kerlenton/mcpsnoop/releases) — it is a single Go binary with no runtime dependencies.

2. **Wrap your MCP server:**
   ```bash
   mcpsnoop -- npx @anthropic-ai/claude-code-server
   ```

3. **Start inspecting:** The TUI opens automatically, showing live frames as they flow through the proxy.

4. **Filter and explore:** Use the keybindings to filter by tool, method, direction, or status. Select a frame to see its full JSON-RPC payload.

5. **Export when needed:** Press the export key to save the session as JSON, HTML, or text.

For HTTP servers:
```bash
mcpsnoop http --target http://localhost:8080 --port 9090
```

For CI pipelines:
```bash
mcpsnoop --check --threshold 5000 -- npx @anthropic-ai/claude-code-server
```

Configuration can be persisted in `.mcpsnoop.toml`:
```toml
[redact]
keys = ["apiKey", "token", "password"]
jsonpath = ["$.credentials.*"]
regex = ["sk-[a-zA-Z0-9]+"]

[check]
error_threshold = 0
slow_call_ms = 5000
warn_pending = true
```

## Real-World Use Cases

### Debugging Silent Tool Call Failures

The most common MCP debugging scenario: a tool is supposed to be called but never executes, or returns an unexpected result. With mcpsnoop, you can see exactly what the client sent and what the server responded with. If the server returned an error that the client silently ignored, you will see it in the frame stream. If the client never sent the request, you will see that too.

### CI/CD Pipeline Quality Gates for MCP

Teams deploying MCP servers can use mcpsnoop's CI check mode as a quality gate. Before deploying a new version of an MCP server, run the test suite through mcpsnoop with `--check`. If the new version introduces errors, slow responses, or invalid frames, the build fails. This catches regressions before they reach production.

### Post-Mortem Analysis of Agent Runs

When an AI agent produces unexpected results, mcpsnoop's session export lets you save the full MCP conversation for post-mortem analysis. Export to HTML for a shareable report, or export to OTLP to see MCP tool calls alongside application traces in your observability platform.

### Remote Server Debugging via SSH

If your MCP server runs on a remote machine or in a container, mcpsnoop's SSH tunnel mode lets you debug it from your local machine. The shim runs on the remote server, the TUI runs locally, and you see frames in real time as if the server were running locally.

## Limitations and Considerations

mcpsnoop is still very young — it reached v0.9.0 within 18 days of its first release. While the rapid iteration is impressive, it means the tool is not yet stable. Users should expect breaking changes between versions.

The tool currently supports stdio and HTTP modes, but does not support WebSocket-based MCP transports. If your MCP server uses WebSockets, you will need to use a different tool or wait for future releases.

The Bubble Tea TUI, while functional and fast, is not as polished as a web-based UI. Users accustomed to graphical debugging tools may find the terminal interface less intuitive at first.

mcpsnoop has 270 stars and a small community. While the developer is actively maintaining the project, long-term sustainability is not guaranteed. Teams adopting mcpsnoop should have a fallback debugging strategy.

## Verdict — Is mcpsnoop the Wireshark for MCP?

Yes, the comparison is fair. mcpsnoop does for MCP traffic what Wireshark does for network packets — it sits transparently in the data path, captures every frame in real time, and provides powerful filtering and inspection tools. No other MCP debugging tool offers the same combination of transparent proxy architecture, live TUI, CI check mode, OTLP export, SSH tunneling, and secret redaction.

For developers building MCP servers or clients, mcpsnoop is an essential addition to your debugging toolkit. It fills a gap that the official MCP Inspector cannot address — real client-server traffic inspection. The rapid development pace (9 releases in 18 days) and growing community suggest mcpsnoop is here to stay.

If you are doing any serious MCP development in 2026, you need mcpsnoop in your toolbox.

## FAQ

### What is mcpsnoop and how does it differ from MCP Inspector?

mcpsnoop is a transparent proxy that sits between your MCP client and server, capturing real traffic as it flows. MCP Inspector connects to your server as its own client and never sees actual client-server interactions. mcpsnoop is for debugging real production traffic; MCP Inspector is for testing servers in isolation.

### Can mcpsnoop be used in CI/CD pipelines?

Yes, mcpsnoop has a dedicated CI check mode (`--check`) that fails the build on MCP errors, invalid frames, slow calls, and pending calls that never received a response. This makes it a proactive quality gate for MCP server deployments.

### Does mcpsnoop support HTTP-based MCP servers?

Yes, mcpsnoop supports HTTP reverse proxy mode (`mcpsnoop http --target <url>`) for HTTP/SSE-based MCP servers. It also supports stdio mode for command-line MCP servers.

### Can I share mcpsnoop session traces with my team?

Yes, mcpsnoop supports session export to JSON, HTML, and text formats. The HTML export creates an interactive report that anyone can view in a browser without installing mcpsnoop. You can also export to OTLP for integration with OpenTelemetry-compatible observability platforms.

### Is mcpsnoop safe to use with production API keys and secrets?

Yes, mcpsnoop includes built-in secret redaction with three levels: key-based, JSONPath-based, and regex-based value scrubbing. You can configure redaction rules in `.mcpsnoop.toml` to automatically redact sensitive information before saving or sharing session traces.
