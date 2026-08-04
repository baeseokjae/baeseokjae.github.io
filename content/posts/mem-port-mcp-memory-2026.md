---
title: "Mem-Port MCP Memory Server 2026: Portable Long-Term Agentic Memory on a Thumb Drive"
date: 2026-08-01T01:03:28+00:00
tags:
  - MCP
  - memory
  - AI agents
  - Claude Code
  - Cursor
  - Windsurf
  - SurrealDB
  - portable memory
description: "Mem-Port is a zero-dependency MCP memory server using embedded SurrealDB that gives AI agents portable, shared long-term memory across any copilot."
draft: false
cover:
  image: "/images/mem-port-mcp-memory-2026.png"
  alt: "Mem-Port MCP Memory Server 2026: Portable Long-Term Agentic Memory on a Thumb Drive"
  relative: false
schema: "schema-mem-port-mcp-memory-2026"
---

## What is Mem-Port and Why Portable Agentic Memory Matters

Mem-Port is an open-source MCP (Model Context Protocol) memory server that gives AI coding agents persistent, portable long-term memory using an embedded SurrealDB database. Unlike traditional memory solutions that lock agent context to a single machine or tool, Mem-Port lets you carry your AI agent's entire memory — facts, episodes, skills, and entity relationships — between machines, copilots, and teams as a single portable JSON bundle. Think of it as a thumb drive for your AI's brain.

The MCP ecosystem has grown to over 1,182 repositories tagged with memory/server on GitHub as of August 2026, reflecting a fundamental shift: developers no longer want AI agents that forget everything between sessions. Portable agentic memory solves the problem of siloed context — where Claude Code knows your project structure but Cursor has no idea what Claude already learned. Mem-Port bridges that gap with a zero-external-dependency architecture that runs anywhere Node.js does.

## How Mem-Port Solves the Siloed Memory Problem

Every AI coding tool today maintains its own context window. Claude Code remembers what you discussed in its session. Cursor has its own chat history. Windsurf keeps its own project context. None of them share memory by default. This means you repeat instructions, re-explain project conventions, and re-teach your preferred patterns to each tool individually.

Mem-Port solves this by acting as a central memory server that multiple copilots connect to simultaneously via the MCP protocol. When Claude Code learns a new fact about your codebase — say, that your API uses camelCase for response fields and snake_case for database columns — that fact is stored in Mem-Port's graph database. When you open Cursor five minutes later, it queries the same Mem-Port server and retrieves that fact automatically. The memory is shared, persistent, and survives across sessions, machines, and even team members.

The key architectural insight is Mem-Port's use of embedded SurrealDB, which combines graph storage, vector search, and document storage in a single database engine. There is no need to run a separate Postgres instance, a Qdrant vector database, or a Neo4j graph database. One binary, one process, zero external dependencies.

## Quick Start — Running Mem-Port in Under a Minute

Getting Mem-Port running takes less than 60 seconds. You need Node.js 18 or later installed on your machine.

```bash
# Install globally via npm
npm install -g @rsl-innovation/mem-port

# Start the MCP server
npx @rsl-innovation/mem-port
```

That is it. The server starts on the default port and is immediately ready to accept MCP connections from any compatible AI copilot. The first time it runs, it creates an embedded SurrealDB database in the current directory. No Docker containers, no Postgres setup, no API key configuration.

For a more customized setup, you can pass environment variables:

```bash
MEM_PORT=3101 npx @rsl-innovation/mem-port
```

This starts the server on port 3101 instead of the default 3100. The server logs its startup status and available tools to stdout, so you can verify it is running correctly.

## Connecting Your AI Copilot (Claude Code, Cursor, Windsurf)

Once Mem-Port is running, you connect your AI coding tools by adding an MCP server entry to their configuration files.

### Claude Code

Add to your `~/.claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "mem-port": {
      "command": "npx",
      "args": ["@rsl-innovation/mem-port"]
    }
  }
}
```

### Cursor

In Cursor, go to Settings → MCP Servers and add a new server with the command:

```
npx @rsl-innovation/mem-port
```

### Windsurf

Windsurf supports MCP servers through its configuration. Add the same npx command to the MCP server list in Windsurf settings.

All three copilots can connect to the same Mem-Port instance simultaneously. When Claude Code saves a memory, Cursor and Windsurf can read it immediately. This is the multi-copilot shared memory pattern that makes Mem-Port unique.

## The 12 MCP Tools — What Each One Does

Mem-Port exposes 12 MCP tools that cover the full range of memory operations. Here is a complete reference:

| Tool | Purpose | When to Use |
|------|---------|-------------|
| `save_memory` | Store a fact or piece of information | Recording project conventions, API endpoints, configuration values |
| `search_memory` | Semantic search across stored memories | Finding relevant context before starting a task |
| `save_episode` | Record a complete interaction or session | Logging debugging sessions, code reviews, or design decisions |
| `list_episodes` | Browse recorded episodes | Reviewing past work or finding a specific session |
| `save_skill` | Store a reusable procedure or workflow | Saving deployment steps, testing patterns, or coding conventions |
| `search_skills` | Find skills by semantic similarity | Discovering relevant procedures for the current task |
| `list_skills` | List all stored skills | Inventory of available procedures |
| `get_skill` | Retrieve a specific skill by name | Loading a known procedure for execution |
| `forget_skill` | Remove a skill from memory | Cleaning up outdated or incorrect procedures |
| `get_entity` | Retrieve a named entity and its relationships | Looking up a person, service, or component and its connections |
| `relate_entities` | Create a relationship between two entities | Modeling how components, people, or services interact |
| `forget_memory` | Delete a specific memory | Removing incorrect or outdated information |
| `export_library` | Export all memory as a portable .memport.json bundle | Backing up or transferring memory between machines |
| `import_library` | Import a .memport.json bundle | Restoring memory on a new machine or sharing with a team |

The semantic search capability uses a local embedding model (Xenova/all-MiniLM-L6-v2) that runs entirely on your machine. No API key is needed, no data leaves your computer, and searches return results based on meaning rather than keyword matching.

## Three-Scope Architecture — Personal, Team, and Project Memory

Mem-Port implements a three-scope isolation model using the `library-id` header in the Streamable HTTP transport. This is one of its most powerful features for teams.

**Personal scope** — Your individual memories, skills, and episodes. No one else on your team can see or modify these. Use this for personal preferences, custom workflows, and private notes.

**Team scope** — Shared memory accessible by everyone on your team. Team conventions, shared API documentation, common troubleshooting steps, and collective knowledge live here. When one team member saves a useful debugging technique, everyone benefits.

**Project scope** — Memory scoped to a specific project repository. Project-specific conventions, architecture decisions, and domain knowledge that should not leak between projects. When you switch from your frontend project to your backend project, the memory context switches cleanly.

This isolation is enforced at the transport layer. Each copilot connection specifies which scope it is operating in via the `library-id` header, and Mem-Port routes all read and write operations to the correct database scope. No data leakage, no accidental context mixing.

## Skills — Portable Procedures Across Copilots

Skills in Mem-Port are reusable procedures that any connected copilot can discover and execute. Unlike traditional AI agent memory that stores raw facts, skills store structured workflows.

For example, you can save a deployment procedure as a skill:

```
save_skill: "deploy-to-staging"
Content: |
  1. Run `npm run build` and verify no errors
  2. Run `npm test` and confirm all tests pass
  3. Tag the commit with `git tag v$(date +%Y%m%d)-staging`
  4. Push to staging branch: `git push origin main:staging`
  5. Verify deployment at https://staging.example.com
  6. Run smoke tests against staging endpoint
```

Once saved, any copilot — Claude Code, Cursor, or Windsurf — can search for "deploy to staging" and retrieve the exact procedure. The skill is portable because it lives in Mem-Port's database, not in a tool-specific configuration file. You do not need to convert formats, copy-paste between tools, or maintain parallel documentation.

Skills are also searchable semantically. You can ask your copilot "how do I deploy?" and Mem-Port returns the relevant skill even if the exact words "deploy to staging" are not in your query.

## Exporting and Importing Memory Between Machines

The export/import system is what makes Mem-Port truly portable. Running the export tool produces a `.memport.json` file — a plain JSON bundle containing all memories, episodes, skills, entities, and their relationships.

```bash
# Export all memory
npx @rsl-innovation/mem-port export > my-memory-backup.memport.json

# Import on another machine
npx @rsl-innovation/mem-port import my-memory-backup.memport.json
```

The `.memport.json` file is plain JSON, which means it is human-readable, diffable, and commitable to git. You can check your memory bundle into your project repository, share it with team members via pull request, or carry it on a USB drive between machines.

This is the "thumb drive for AI memory" metaphor in action. You can work on a desktop machine at the office, export your memory, carry the JSON file to your laptop at home, import it, and your AI copilot picks up exactly where you left off. All facts, all skills, all entity relationships — intact.

The import operation merges incoming data with existing memory, so you can incrementally sync between machines without losing data on either side.

## Running Mem-Port as a Persistent Service (macOS launchd / Linux systemd)

For production use, you want Mem-Port running as a background service that starts on boot and survives crashes.

### macOS (launchd)

Create `~/Library/LaunchAgents/com.mem-port.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.mem-port</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/npx</string>
        <string>@rsl-innovation/mem-port</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>WorkingDirectory</key>
    <string>/Users/yourname/mem-port-data</string>
    <key>StandardOutPath</key>
    <string>/Users/yourname/Library/Logs/mem-port.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/yourname/Library/Logs/mem-port.error.log</string>
</dict>
</plist>
```

Load and start:

```bash
launchctl load ~/Library/LaunchAgents/com.mem-port.plist
launchctl start com.mem-port
```

### Linux (systemd)

Create `/etc/systemd/system/mem-port.service`:

```ini
[Unit]
Description=Mem-Port MCP Memory Server
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/npx @rsl-innovation/mem-port
WorkingDirectory=/opt/mem-port
Restart=always
RestartSec=5
User=youruser
Environment=NODE_ENV=production

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable mem-port
sudo systemctl start mem-port
sudo systemctl status mem-port
```

With the service running, your copilots connect to `http://localhost:3100` and memory persists across reboots, crashes, and network interruptions.

## Configuration Reference (Environment Variables)

Mem-Port is configured through environment variables. Here is the complete reference:

| Variable | Default | Description |
|----------|---------|-------------|
| `MEM_PORT` | `3100` | HTTP port for the MCP server |
| `MEM_HOST` | `localhost` | Host address to bind to |
| `MEM_DB_PATH` | `./mem-port.db` | Path to the SurrealDB database file |
| `MEM_LOG_LEVEL` | `info` | Logging verbosity (debug, info, warn, error) |
| `MEM_MAX_MEMORIES` | `10000` | Maximum number of memories to store |
| `MEM_EMBEDDING_MODEL` | `Xenova/all-MiniLM-L6-v2` | Local embedding model for semantic search |
| `MEM_CORS_ORIGIN` | `*` | CORS allowed origins for HTTP transport |

The default configuration works for most use cases. You only need to customize `MEM_DB_PATH` if you want the database in a specific location, or `MEM_PORT` if port 3100 is already in use.

## Comparison with Alternatives (Engram, Nocturne, Stash, MCP-Mem0)

| Feature | Mem-Port | Engram | Nocturne Memory | Stash | MCP-Mem0 |
|---------|----------|--------|-----------------|-------|----------|
| **Database** | Embedded SurrealDB (graph + vector + document) | SQLite + FTS5 | Custom (Python) | Postgres | Mem0 service |
| **External Dependencies** | None (Node.js only) | None (Go binary) | Python + deps | Postgres required | Mem0 API key |
| **Stars** | Newer project | 5,778 | 1,288 | 757 | 678 |
| **Language** | TypeScript | Go | Python | Go | Python |
| **Semantic Search** | Built-in (local embedding) | FTS5 only (keyword) | Vector-based | FTS5 only | Via Mem0 |
| **Multi-Copilot** | Yes (simultaneous) | Yes | Yes | Yes | Yes |
| **Portable Export** | .memport.json bundles | No | No | No | No |
| **Skills System** | Yes (searchable procedures) | No | No | No | No |
| **Three-Scope Isolation** | Yes (library-id) | No | No | No | No |
| **API Key Required** | No | No | No | No | Yes (Mem0) |
| **License** | MIT | MIT | MIT | Apache 2.0 | MIT |

Engram is the most popular MCP memory project with 5,778 stars, and it is an excellent choice if you want a battle-tested Go binary with SQLite storage. However, it lacks semantic search (FTS5 only), portable export, and the skills system. Nocturne Memory offers visual memory and rollback capabilities but is Python-based and lacks the portability features. Stash requires a Postgres database, adding operational overhead. MCP-Mem0 depends on the Mem0 cloud service, requiring an API key and internet connectivity.

Mem-Port's key differentiators are its zero-external-dependency architecture, portable export/import system, skills framework, and three-scope isolation — all in a single npm package.

## Known Limitations and Gotchas

**Node.js requirement.** Mem-Port requires Node.js 18 or later. If your environment does not have Node.js, you need to install it first. Engram and Stash ship as standalone Go binaries with no runtime dependency, which is an advantage in constrained environments.

**Database file location.** By default, the SurrealDB database file is created in the current working directory. If you start Mem-Port from different directories, you get different databases. Always set `MEM_DB_PATH` to an absolute path when running as a service.

**Memory capacity.** The default limit of 10,000 memories is generous for individual use but may need tuning for team deployments. Each memory includes its embedding vector, so memory usage grows with the number of stored items. Monitor disk usage if you are storing large numbers of episodes or skills.

**No built-in authentication.** Mem-Port does not include authentication or encryption. If you run it on a network-accessible host, restrict access with a firewall or reverse proxy. The server is designed for local or trusted network use.

**Embedding model size.** The default embedding model (Xenova/all-MiniLM-L6-v2) is approximately 90MB when loaded. The first semantic search may be slow as the model loads into memory. Subsequent searches are fast as the model stays cached.

**Export file size.** Large memory stores produce large `.memport.json` files. A store with 10,000 memories and their embeddings can produce a multi-megabyte export file. This is fine for git storage but may be slow to import on resource-constrained machines.

## FAQ

**Q: Does Mem-Port work with any MCP-compatible AI tool?**
A: Yes. Mem-Port implements the standard MCP protocol and works with any client that supports MCP servers, including Claude Desktop, Claude Code, Cursor, Windsurf, and custom MCP clients. The Streamable HTTP transport ensures broad compatibility.

**Q: Can I run Mem-Port on a server and have multiple team members connect to it?**
A: Yes. Mem-Port supports multiple simultaneous connections. Each connection can specify a different `library-id` to isolate personal, team, and project memory scopes. This makes it suitable for small team deployments where everyone shares a central memory server.

**Q: Is my data private when using Mem-Port?**
A: Yes. All data is stored locally in the embedded SurrealDB database on your machine. The embedding model runs locally with no API calls. No data leaves your computer unless you explicitly export a `.memport.json` bundle and share it. There is no telemetry, no cloud dependency, and no external service.

**Q: How does Mem-Port compare to using Claude's built-in memory or Cursor's project rules?**
A: Built-in memory in tools like Claude and Cursor is tool-specific and does not transfer between tools. Mem-Port provides a universal memory layer that works across all MCP-compatible tools simultaneously. It also adds features those tools lack: semantic search, entity relationship modeling, skills as portable procedures, and export/import between machines.

**Q: Can I use Mem-Port without npm or Node.js?**
A: No. Mem-Port is a TypeScript package published on npm. You need Node.js 18+ to run it. If you cannot install Node.js, consider Engram (Go binary) or Stash (Go binary with Postgres) as alternatives that do not require a JavaScript runtime.
