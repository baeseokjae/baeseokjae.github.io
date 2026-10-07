---
title: "MCP Proxy: Add MCP Support to Any REST API Without Code Changes"
date: 2026-10-01T08:18:32+00:00
tags:
  - MCP
  - REST API
  - MCP proxy
  - OpenAPI
  - AI agents
  - FastMCP
  - API gateway
  - tool calling
  - developer tools
description: "An MCP proxy turns an existing REST API into MCP tools from its OpenAPI spec — no backend rewrite. Here are the three zero-code paths and how to pick one."
draft: false
cover:
  image: "/images/mcp-proxy-rest-api-to-mcp.png"
  alt: "MCP Proxy: Add MCP Support to Any REST API Without Code Changes"
  relative: false
schema: "schema-mcp-proxy-rest-api-to-mcp"
---

An mcp rest api bridge works by reading your API's OpenAPI spec at runtime and translating each operation into an MCP tool. You keep the REST API exactly as it is, add a proxy or gateway in front of it, and point your agent at the MCP endpoint. Nothing in the backend is rewritten or redeployed.

That is the short answer, and it is genuinely accurate — with one important caveat that the marketing pages bury. "No code changes" describes the API, not the project. You still own a configuration surface, an authentication decision, and a curation judgment call. The teams that get burned are the ones who treat auto-conversion as the finished deliverable instead of step one.

This guide fixes the direction confusion first, then walks the three real zero-code paths (managed gateway, runtime spec proxy, generated project), explains how to lock the bridge down, and states plainly why mass-converting a 200-endpoint spec will make your agent slower and more expensive.

## REST to MCP or MCP to REST? Getting the direction right first

Almost every listicle about "converting APIs to MCP" mixes two opposite jobs. Getting the direction wrong means you install the wrong tool and then wonder why your agent cannot see your API.

- **REST → MCP (the bridge):** you have a REST API and you want an AI agent to call it as MCP tools. The MCP server is the *new* surface; the REST API is the backend. Tools like FastMCP's `from_openapi()`, Kong's AI MCP Proxy plugin, Azure API Management's "Expose an API as an MCP server", and AWS API Gateway's MCP proxy support all do this.
- **MCP → REST (the reverse proxy):** you have an MCP server and you want ordinary HTTP/OpenAPI clients to call it. [`mcpo`](https://github.com/open-webui/mcpo) (4,387 stars, MIT) is the canonical tool here. It is regularly miscited in REST-to-MCP roundups because it sells the same benefits — auto-generated docs, standard auth, no stdio plumbing.

If your goal is "make my REST API callable by Claude, Cursor, or a Bedrock agent," you want the first direction. That is the rest of this article.

### Why does this matter more than it did a year ago?

Because the MCP surface itself has become large enough that almost every internal API now has an agent consumer waiting for it. The official MCP Registry held [30,375 unique servers](https://dev.to/amareswer/the-mcp-registry-by-the-numbers-38nc) (99,114 server-plus-version records) as of 2026-09-10 — roughly three times its May 2026 size. August 2026 alone saw 6,265 servers first published, more than the registry's entire first five months combined. Monthly MCP SDK downloads passed [97 million](https://cybertizeweb.com/blog/ai/mcp-adoption-report-2026/) (Python plus TypeScript) by March 2026, up from roughly 100,000 in November 2024.

The tooling grew to match. On the enterprise side, 41% of surveyed software organizations were in limited (29%) or broad (12%) production with MCP servers, and API/MCP gateways plus full self-hosting each account for roughly 30% of deployment models — with nearly 60% of developers preferring a hybrid of the two. That split is exactly the decision this article is about.

## What "no code changes" really means (and the one thing you still must change)

Every tool in this space advertises zero code changes. That claim is narrower than it sounds, and understanding the boundary saves you a failed sprint.

| Claimed | What is actually true |
|---|---|
| No changes to your API | True. The bridge reads OpenAPI and calls your existing HTTP routes. Your controllers, DTOs and deployment are untouched. |
| No new infrastructure | False in most cases. A runtime proxy is still a process you must run, monitor and authenticate. A managed gateway is infrastructure someone else runs — which is not the same as none. |
| No configuration | False. You must supply the spec, the auth credentials, the transport, and the inclusion/exclusion rules. |
| Nothing to maintain | Depends entirely on path. A generated TypeScript project is code you now own; a gateway plugin is a config block you version along with the rest of the gateway. |

The one thing you always change is the **tool surface your agent sees**. That is the real deliverable. The OpenAPI spec describes what humans need across 40+ operations with polymorphic bodies and pagination cursors; the agent needs eight outcome-shaped tools with honest descriptions. A bridge does not make that decision for you, and if you skip it, you have not shipped a feature — you have shipped a context tax.

## Three ways to bridge a REST API into MCP

Before the paths, the decision table. Every serious option in 2026 falls into one of three categories, and the differences that matter are who runs it, how much control you get, and what you now own.

| Approach | Example tools | New services to run | Control | What you own long-term |
|---|---|---|---|---|
| Managed gateway | Kong AI MCP Proxy, Azure APIM, AWS API Gateway | Zero (you configure an existing gateway) | Low to medium | Configuration, plus per-tier licensing |
| Runtime spec proxy | FastMCP `from_openapi()`, `mcp-openapi-proxy` | One process | High (FastMCP), low (mcp-openapi-proxy) | Uptime, auth, curation code |
| Generated project | `openapi-mcp-generator` | One deployable you own | Medium | A codebase: regeneration, dependencies, upgrades |
| OSS gateway / registry | IBM ContextForge | One stack (Docker/Helm) | High | Everything, including federation and policy |

Two adjacent tools appear in nearly every list and deserve a one-line verdict up front. `mcpo` is the reverse direction (MCP → REST) and is not a bridge. IBM ContextForge ([4,555 stars, 892 forks, Apache-2.0](https://github.com/IBM/mcp-context-forge), pushed 2026-10-01) is the most active open-source option, but it is a gateway and registry rather than a minimal converter — you adopt it when you are federating many MCP, REST and gRPC backends behind one endpoint, not when you want one API exposed.

## Path A: Managed gateway — zero new services to run

If you already run Kong, Azure API Management or AWS API Gateway, the fastest correct answer is usually the bridge you already pay for.

**Kong AI MCP Proxy** is a protocol bridge plugin with a `mode` parameter that switches between proxying MCP servers, converting a REST API into MCP tools, and aggregating tool sets into one MCP server. The flow is: MCP request → matched to an OpenAPI operation → converted into an upstream HTTP call → response wrapped back into MCP format. The endpoint is provisioned dynamically on the gateway; you do not host or scale a separate server. Crucially, the MCP traffic inherits the gateway features you already trust — OIDC or key auth, rate limiting, ACLs, logging and tracing, request transforms.

Two constraints to check before you commit: it requires Kong Gateway Enterprise 3.12+ (AI Gateway tier), and it must not be combined with other AI plugins on the same Service or Route.

**Azure API Management** takes the portal route: APIs → MCP Servers → "+ Create MCP server" → "Expose an API as an MCP server". You pick a managed API and version, then choose all operations or a specific subset to expose as tools; that selection is editable later in the Tools blade. Policies then supply JWT auth, rate limits and IP filtering on the MCP surface with no change to the backend. Known limitations, widely reported: it exposes tools only — no MCP resources or prompts — and it requires a paid tier, not Consumption.

**AWS API Gateway** added MCP proxy support in December 2025, turning existing REST APIs into MCP-compatible endpoints with no application modification. Protocol translation, dual authentication (agent identity plus outbound credentials) and semantic API discovery are handled by Bedrock AgentCore Gateway. Availability is restricted to the [nine AWS regions where Bedrock AgentCore operates](https://aws-news.com/article/2025-12-02-amazon-api-gateway-adds-mcp-proxy-support).

The gateway path is also, quietly, the security path. Only 8.5% of MCP servers implement the OAuth 2.1 with PKCE that has been mandatory for remote servers since the November 2025 spec revision, 53% expose credentials via hard-coded values in config files, and just 18% implement any access scoping for tool permissions. Centralizing credential policy, rate limiting and audit at a gateway is how you avoid being one of those statistics — which is a large part of why roughly 30% of deployments are gateway-based.

## Path B: Runtime proxy with FastMCP from_openapi() — about 15 lines

[FastMCP](https://gofastmcp.com/integrations/openapi) (27,946 stars, 2,412 forks, Apache-2.0) is the main Python MCP framework, and `FastMCP.from_openapi()` builds an MCP server directly from an OpenAPI spec — a dict, a URL, or a live FastAPI app. Each route becomes a tool by default, at runtime, with no generated project to maintain.

The shape of it:

```python
import httpx
from fastmcp import FastMCP

spec = httpx.get("https://api.example.com/openapi.json").json()

client = httpx.AsyncClient(
    base_url="https://api.example.com",
    headers={"Authorization": "Bearer YOUR_TOKEN"},
)

mcp = FastMCP.from_openapi(
    openapi_spec=spec,
    client=client,
    name="Example API",
)

if __name__ == "__main__":
    mcp.run()  # stdio by default; mcp.run(transport="http") for Streamable HTTP
```

Authentication lives on the `httpx` client, so the underlying API is untouched. The control surface is `RouteMap`, which maps methods, URL patterns and tags to `TOOL`, `RESOURCE`, `RESOURCE_TEMPLATE` or `EXCLUDE`. A first-pass guard looks like this:

```python
from fastmcp.server.openapi import RouteMap, MCPType

mcp = FastMCP.from_openapi(
    openapi_spec=spec,
    client=client,
    route_maps=[
        RouteMap(methods="*", pattern=r"^/admin/.*", mcp_type=MCPType.EXCLUDE),
        RouteMap(methods="*", tags={"internal"}, mcp_type=MCPType.EXCLUDE),
        RouteMap(methods=["GET"], pattern=r"^/users/\{[^/]+\}$", mcp_type=MCPType.RESOURCE_TEMPLATE),
        RouteMap(methods=["GET"], pattern=r"^/.*", mcp_type=MCPType.RESOURCE),
    ],
)
```

A clean mapping to start from, which several guides converge on: `GET` without parameters → resource, `GET` with path parameters → resource template, `POST`/`PUT`/`DELETE` → tool, query parameters flattened into the tool input schema, and auth handled in server configuration rather than per call.

FastMCP's own documentation is blunt that an auto-converted server performs worse than a curated one and recommends it for bootstrapping and prototyping rather than mirroring the whole API to clients. Take that seriously — it is the framework telling you the truth about itself.

**`mcp-openapi-proxy`** is the lowest-effort variant: `uvx mcp-openapi-proxy` reads `OPENAPI_SPEC_URL` at startup and dynamically exposes endpoints as tools. It supports a FastMCP "simple mode" (`OPENAPI_SIMPLE_MODE=true`) that exposes a fixed, hand-chosen tool set instead of every endpoint, plus JMESPath-based payload auth for APIs like Slack that want the token in the request body, and custom header names beyond `Bearer`. Its changelog is a useful catalogue of the failure modes auto-conversion produces: tool names truncated at `TOOL_NAME_MAX_LENGTH` collided and silently dropped tools, and array parameters emitted without an `items` schema were rejected by the OpenAI API.

## Path C: Generate a standalone server with openapi-mcp-generator

If your team is TypeScript-first and you want a typed, versioned artifact rather than a runtime process, generate a project instead of proxying. `openapi-mcp-generator` produces an MCP server from a spec, with an `x-mcp.exclude` extension and programmatic `filterFn` / `excludeOperationIds` hooks so internal endpoints never reach the agent.

The trade is straightforward. You gain a reviewable codebase, typed handlers and the ability to hand-edit tool descriptions — which is exactly where curation actually happens. You take on regeneration, dependency churn and a deployable to keep alive. For a single internal API consumed by one team, a runtime proxy is usually less work. For a public API vendor shipping MCP support to many customers, the generated artifact is the right shape because it can be versioned alongside your SDKs and pinned by consumers.

## Lock it down: auth, transport, and tool scoping

**Transport.** The current spec revision (2026-07-28) defines two standard transports: stdio and Streamable HTTP, where each message is an HTTP POST to a single MCP endpoint and replies come back as JSON or a request-scoped SSE stream. Older remote SSE implementations are superseded and carry a deprecation window — if you have a remote SSE setup, plan the migration now rather than during an incident.

**Auth.** OAuth 2.1 with PKCE is mandatory for remote servers, and almost nobody implements it. If your bridge terminates auth at a gateway, you fix that in one place for every tool instead of per server. If you self-host a runtime proxy, the credentials live in the proxy's environment: use a scoped service account or short-lived token, never a long-lived admin key, and never a hard-coded value in a config file that gets committed.

**Scoping.** Decide which operations are callable by which agent. The mapping table above shows the mechanics; the judgment is that read operations and write operations do not deserve the same exposure. A bridge that gives an autonomous agent `DELETE /everything` because it happened to be in the spec is not a convenience — it is an incident waiting for a trigger.

## Verify with MCP Inspector before your agent ever sees the tools

Do not debug the bridge through your agent's production traces. Generate, then inspect.

```bash
# FastMCP ships a dev server + Inspector for exactly this
fastmcp dev server.py
```

MCP Inspector shows you the actual tool list and the actual JSON schemas — the two things most likely to be wrong. Check four things explicitly:

1. **Every operation you intended is present.** Silent drops from name truncation are real, and they are invisible until an agent says it cannot do something.
2. **Tool names are unique and readable.** Collisions after a 56-character cap produce one surviving tool with a confusing name.
3. **Parameter schemas are valid.** Array and object parameters without an `items` schema will be rejected by OpenAI-compatible tool-calling APIs at call time, not registration time.
4. **No internal endpoints leaked.** Search the tool list for `admin`, `internal`, `debug`, `_test`, and anything with `DELETE` in it.

This is the cheapest five minutes in the whole project. The alternative is discovering that the agent has been calling a staging endpoint for a week.

## Curate before you ship: why 200 auto-generated tools make agents dumber

The FastMCP creator — the author of the most widely used OpenAPI-to-MCP converter — published [Stop Converting Your REST APIs to MCP](https://www.jlowin.dev/blog/stop-converting-rest-apis-to-mcp) with the line that should be pinned above every bridge project: an API built for a human will poison your AI agent.

Two failure modes, both structural rather than cosmetic.

**Literal context cost.** Every tool's name, description and parameter schema is re-processed on every reasoning step. A 200-tool server does not cost 200 tools' worth of tokens once; it costs a slice of every step the agent takes. Context pollution turns agents into obsessive API librarians, and it gets worse with every tool you add.

**Atomicity as an anti-pattern.** When each tool maps to one REST operation, the agent needs a full reasoning round trip per step. Composing "find the customer, check their open orders, refund the eligible one" becomes three or more model passes, each carrying the accumulated context forward.

The prescription is the same one the community has converged on independently: **bootstrap from OpenAPI, find the real agent workflows, then collapse to 5–15 outcome-oriented tools.** Trim response payloads so the agent gets the fields it reasons over rather than the full DTO. Write tool descriptions as instructions — what the tool does, when to reach for it, and what it returns — not as one-line summaries. Use `Tool.from_tool()` (or equivalent composition) to rename and merge operations into outcomes: one `refund_order` tool that internally makes the calls a human would.

Naming matters more than it looks. Follow `get_` / `list_` / `search_` / `create_` / `update_` / `delete_` plus `{action}_{resource}`. Avoid REST-path mirroring: `users_post` and `doStuff` tell a model nothing about when to use them.

There is a measured precedent for why this pays. In the code-mode research, a workflow that required 40 sequential tool calls and 262,159 characters of intermediate payload dropped to a single script and 903 characters — the model stopped being an API librarian and started being a reasoner. You get a fraction of that benefit from curation alone, without writing a single line of agent code.

## Production checklist: rate limits, audit logging, exclusions, version pinning

Before you call the bridge done, walk this list.

- **Exclude internal and admin routes explicitly.** Tag-based exclusion where the spec supports it, path-pattern exclusion otherwise. Never rely on "nothing sensitive is in the spec" — specs drift.
- **Rate-limit the MCP surface separately.** An agent retry loop is a different traffic shape from a human UI, and it will find your ceiling.
- **Log every tool invocation with the agent identity.** Gateway logging earns its keep here: you get tool-level audit for free, and you will need it the first time an agent does something surprising.
- **Pin the spec version and the proxy version.** Auto-conversion against a live spec means a backend deploy can silently change your tool surface. Snapshot the spec, diff it in CI, and promote changes deliberately.
- **Choose the transport deliberately.** stdio for local single-user setups; Streamable HTTP for remote and shared. Have a written position on the legacy SSE deprecation.
- **Re-run the Inspector check after every spec change.** It is the only cheap test that catches silent drops.
- **Decide who owns curation.** If the answer is "nobody," the tool count only grows, and the agent only gets slower.

## FAQ

### What is an MCP proxy in one sentence?

An MCP proxy reads your REST API's OpenAPI specification, translates each operation into an MCP tool, and forwards the resulting calls back to your existing HTTP endpoints — so an agent can use your API as MCP without any change to the API itself.

### Do I need to modify my REST API to add MCP support?

No. That is the point of every tool covered here. Kong's plugin, Azure APIM, AWS API Gateway's MCP proxy, FastMCP's `from_openapi()` and `openapi-mcp-generator` all consume your existing spec and call your existing routes. Authentication is configured on the bridge's side, in headers or a gateway policy.

### Which is better for a REST API to MCP bridge — a managed gateway or a self-hosted proxy?

Use a managed gateway (Kong, Azure APIM, AWS API Gateway) when you already run one and want auth, rate limiting and audit inherited for free — roughly 30% of MCP deployments are gateway-based, and the security statistics argue for it. Use a self-hosted runtime proxy like FastMCP when you need fine-grained curation, route-level transforms, or freedom from enterprise tier licensing. A large share of teams end up hybrid: gateway for policy, a curated proxy for the tool surface.

### Is mcpo a REST-to-MCP bridge?

No — it is the opposite direction. `mcpo` exposes an MCP server as an OpenAPI/REST HTTP server so that OpenAPI-only clients can call it. If your goal is to give an agent access to a REST API, `mcpo` is not the tool, despite appearing in many "REST to MCP" roundups.

### Why does my auto-generated MCP server make the agent slower?

Because every tool's name, description and parameter schema is re-processed on every reasoning step, and because one tool per REST operation forces a full model round trip per step. The converter's own author recommends against mass conversion: auto-convert to discover the surface, then collapse it to 5–15 outcome-oriented tools with descriptive names and trimmed response payloads before you let an agent near it.
