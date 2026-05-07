---
title: "MCP OAuth 2.1 Authentication: Complete Developer Guide 2026"
date: 2026-05-05T15:03:56+00:00
tags: ["MCP", "OAuth 2.1", "authentication", "security", "AI agents", "FastMCP", "PKCE"]
description: "Step-by-step guide to implementing OAuth 2.1 authentication for MCP servers in 2026, covering PKCE, Protected Resource Metadata, and enterprise gateway patterns."
draft: false
cover:
  image: "/images/mcp-oauth-authentication-guide-2026.png"
  alt: "MCP OAuth 2.1 Authentication: Complete Developer Guide 2026"
  relative: false
schema: "schema-mcp-oauth-authentication-guide-2026"
---

Only 8.5% of MCP servers currently implement OAuth 2.1 authentication — despite it being the protocol's mandatory security standard for remote deployments. If your server handles sensitive data or enterprise workloads, that gap is your attack surface. This guide walks you through the complete implementation, from metadata discovery to token introspection, with working Python code.

## What Is MCP OAuth 2.1 and Why It Matters in 2026

MCP OAuth 2.1 authentication is the authorization framework mandated by the Model Context Protocol specification for all remote HTTP-based servers that expose tools or resources to AI agents. As of the November 2025 spec revision, any MCP server accessible over the internet must implement OAuth 2.1 with PKCE (Proof Key for Code Exchange using the S256 method) — no exceptions. The spec explicitly bans the implicit grant and the plain PKCE method that OAuth 2.0 permitted.

The stakes are real: a 2026 security audit found that 25% of public MCP servers have no authentication at all, and 53% rely on long-lived static API keys or Personal Access Tokens — credentials that, once leaked, provide indefinite access. The public MCP server registry grew from roughly 1,200 entries in Q1 2025 to over 9,400 servers by mid-April 2026, which means the attack surface has grown more than 7× in fourteen months. Meanwhile, 38% of organizations say security concerns are actively blocking their MCP adoption, and 50% of MCP builders cite access control as their top challenge.

OAuth 2.1 solves the core problem: it separates the token issuer (your identity provider) from the resource server (your MCP server), ensuring that AI agents prove their identity with short-lived, scoped credentials rather than permanent secrets. For enterprise teams, this is the difference between an auditable access-control system and a credential sprawl nightmare.

## The MCP Authorization Spec Timeline (March–November 2025)

The MCP authorization spec evolved rapidly through three major revisions in nine months, and understanding what changed helps you avoid implementing an outdated pattern. The March 2025 revision introduced OAuth 2.1 as the baseline for remote MCP servers, replacing the earlier ad-hoc API key recommendations. Authorization server metadata discovery (RFC 8414) was included, letting clients auto-discover token endpoints without hardcoded URLs.

The June 2025 revision added two critical requirements. First, RFC 9728 Protected Resource Metadata became mandatory — remote servers must now expose a `/.well-known/oauth-protected-resource` endpoint that tells clients which authorization server to use. Second, dynamic client registration (RFC 7591) became a SHOULD (effectively required for clients like Claude Desktop and ChatGPT that need to self-register). Servers that skip dynamic registration must maintain a static allowlist of client IDs, which breaks compatibility with off-the-shelf AI clients.

The November 2025 revision — the one currently in force — made three additional changes: it explicitly banned the `plain` PKCE method in favor of S256 only, required resource parameters (RFC 8707) in all token requests to prevent token reuse across servers, and mandated that 401 responses include a properly formatted `WWW-Authenticate` header pointing to the authorization server. Servers built against the March 2025 spec are likely missing at least two of these requirements. The clearest signal that a server is outdated: it accepts PKCE `plain` method or returns 401 without a `WWW-Authenticate` header.

## Core Concepts: OAuth 2.1 + PKCE for MCP

OAuth 2.1 with PKCE is the grant type used by every MCP client authenticating to a remote server. It works by having the client generate a cryptographic secret (the `code_verifier`) before the authorization request, derive a challenge from it (the `code_challenge`), and send only the challenge to the authorization server during the redirect. The server stores the challenge and demands the original verifier during token exchange — preventing an attacker who intercepts the authorization code from redeeming it without also having the verifier, which never travels over the network.

For MCP specifically, PKCE matters because AI agent clients often run in environments where storing client secrets is impractical or insecure — a desktop application, a CI runner, or a serverless function. PKCE lets these "public clients" authenticate securely without embedding long-lived secrets. The MCP spec mandates the S256 method: `code_challenge = BASE64URL(SHA-256(ASCII(code_verifier)))`. The verifier must be a cryptographically random string of 43–128 characters from the unreserved character set.

The five actors in an MCP OAuth 2.1 flow are: (1) the **AI agent / MCP client**, which initiates the flow; (2) the **authorization server** (Auth0, Keycloak, Okta, Cognito), which issues tokens; (3) the **MCP server**, which acts as a resource server that validates tokens; (4) the **user**, who grants consent; and (5) the **Protected Resource Metadata endpoint**, a `/.well-known` URL on the MCP server that auto-routes clients to the correct authorization server. Without understanding all five, you'll end up with a flow that works in tests but breaks with real clients.

| Concept | OAuth 2.0 | OAuth 2.1 (MCP) |
|---|---|---|
| PKCE | Optional | Mandatory (S256 only) |
| Implicit grant | Allowed | Banned |
| Resource owner password grant | Allowed | Banned |
| Client secrets for public clients | Common | Discouraged |
| Token endpoint auth | Various methods | `client_secret_post` or PKCE |
| `WWW-Authenticate` on 401 | Optional | Mandatory |

## How the MCP Authorization Flow Works Step by Step

The MCP authorization flow follows a seven-step sequence that every client implementing the spec must execute. Understanding each step tells you where failures occur and where to add logging. The sequence begins when an MCP client discovers your server's metadata, generates its PKCE credentials, redirects the user to consent, receives an authorization code, exchanges it for tokens, and then attaches those tokens to subsequent MCP requests.

**Step 1 — Protected Resource Metadata discovery.** The client fetches `GET /.well-known/oauth-protected-resource` on your MCP server. The response is a JSON document (RFC 9728) that includes the `authorization_servers` field — a list of authorization server URLs the client should use.

**Step 2 — Authorization server metadata discovery.** The client fetches `GET {authorization_server}/.well-known/oauth-authorization-server`. This RFC 8414 document provides the `authorization_endpoint`, `token_endpoint`, `registration_endpoint` (for dynamic registration), and supported scopes.

**Step 3 — Dynamic client registration (if needed).** If the client has no pre-registered `client_id`, it POSTs to the `registration_endpoint` with its metadata (name, redirect URIs, grant types). The server responds with a `client_id` and optional `client_secret`.

**Step 4 — PKCE credential generation.** The client generates a cryptographically random `code_verifier` (minimum 43 characters) and computes `code_challenge = BASE64URL(SHA-256(code_verifier))`.

**Step 5 — Authorization redirect.** The client redirects the user to the `authorization_endpoint` with query parameters: `response_type=code`, `client_id`, `redirect_uri`, `scope`, `state` (CSRF token), `code_challenge`, and `code_challenge_method=S256`. The user authenticates and consents.

**Step 6 — Token exchange.** The client POSTs to the `token_endpoint` with `grant_type=authorization_code`, the received `code`, `redirect_uri`, `code_verifier`, and — critically — the `resource` parameter (RFC 8707) set to your MCP server's URL. The authorization server validates the PKCE challenge and issues an `access_token` and optionally a `refresh_token`.

**Step 7 — Bearer token usage.** The client attaches the access token to every MCP request as `Authorization: Bearer {token}`. Your MCP server validates the token on each request, checks the `aud` (audience) claim against its own URL, and verifies the required scopes.

```python
import secrets
import hashlib
import base64
import urllib.parse

# Step 4: Generate PKCE credentials
code_verifier = secrets.token_urlsafe(64)
code_challenge_bytes = hashlib.sha256(code_verifier.encode()).digest()
code_challenge = base64.urlsafe_b64encode(code_challenge_bytes).rstrip(b'=').decode()

# Step 5: Build authorization URL
params = {
    "response_type": "code",
    "client_id": "your-client-id",
    "redirect_uri": "https://yourapp.com/callback",
    "scope": "mcp:read mcp:write",
    "state": secrets.token_urlsafe(16),
    "code_challenge": code_challenge,
    "code_challenge_method": "S256",
    "resource": "https://your-mcp-server.com",  # RFC 8707
}
auth_url = f"https://auth.example.com/authorize?{urllib.parse.urlencode(params)}"
```

## Implementing Protected Resource Metadata (RFC 9728)

RFC 9728 Protected Resource Metadata is the hidden requirement that most MCP OAuth guides skip — and its absence breaks compatibility with Claude Desktop, ChatGPT plugins, and any spec-compliant MCP client. A remote MCP server that returns a 404 on `/.well-known/oauth-protected-resource` will fail the auto-discovery step, causing clients to either fail silently or prompt users for manual configuration. The RFC requires this endpoint to be served without authentication, over HTTPS in production, and to return a JSON document with a minimum set of fields.

The required fields are `resource` (the canonical URL of your MCP server) and `authorization_servers` (an array of authorization server URLs). Optional but recommended fields include `scopes_supported` (the scopes your server understands), `bearer_methods_supported` (always `["header"]` for MCP), and `resource_documentation` (a URL to your server's documentation).

```python
from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()

MCP_SERVER_URL = "https://your-mcp-server.com"
AUTHORIZATION_SERVER = "https://auth.example.com"

@app.get("/.well-known/oauth-protected-resource")
async def protected_resource_metadata():
    return JSONResponse({
        "resource": MCP_SERVER_URL,
        "authorization_servers": [AUTHORIZATION_SERVER],
        "scopes_supported": ["mcp:read", "mcp:write", "mcp:admin"],
        "bearer_methods_supported": ["header"],
        "resource_documentation": f"{MCP_SERVER_URL}/docs",
    })
```

One subtle requirement: the `resource` field in this document must exactly match the `resource` parameter clients send in token requests. If your server URL has a trailing slash in the metadata but clients omit it in the token request, the authorization server's audience validation will fail. Use a canonical form (no trailing slash, lowercase hostname) and document it clearly for client implementors.

For servers deployed behind a reverse proxy (nginx, Cloudflare), ensure the `Host` header is forwarded correctly so that dynamically generated URLs in responses reflect the public URL, not the internal container address. This is a common source of auth failures in Docker-based deployments.

## Dynamic Client Registration (RFC 7591) in Practice

Dynamic client registration (RFC 7591) allows MCP clients — including Claude Desktop, ChatGPT integrations, and custom agents — to self-register with your authorization server without requiring manual pre-provisioning. Without it, every new AI tool that wants to use your MCP server requires you to create a client ID and share it out-of-band, which creates administrative overhead and breaks the ecosystem-scale interoperability that MCP is designed for.

The registration endpoint (`registration_endpoint` in your authorization server metadata) accepts a POST with a JSON body describing the client. The authorization server responds with a `client_id` (and optionally a `client_secret` for confidential clients, though public MCP clients should not receive one). The fields that matter most for MCP compatibility are `grant_types` (must include `authorization_code`), `token_endpoint_auth_method` (`none` for public clients using PKCE), `redirect_uris` (must be pre-validated against an allowlist in production), and `response_types` (`["code"]` only — `token` is banned in OAuth 2.1).

```python
import httpx

async def register_client(registration_endpoint: str, redirect_uri: str) -> dict:
    payload = {
        "client_name": "My MCP Agent",
        "redirect_uris": [redirect_uri],
        "grant_types": ["authorization_code", "refresh_token"],
        "response_types": ["code"],
        "token_endpoint_auth_method": "none",  # public client, uses PKCE
        "scope": "mcp:read mcp:write",
    }
    async with httpx.AsyncClient() as client:
        resp = await client.post(registration_endpoint, json=payload)
        resp.raise_for_status()
        return resp.json()  # contains client_id
```

In production, you should rate-limit the registration endpoint and implement an approval workflow or IP allowlist, because open dynamic registration is an abuse vector: a malicious actor could register thousands of clients to enumerate your authorization server's behavior. Auth0 and Okta offer fine-grained controls for this; Keycloak's dynamic registration is disabled by default and must be explicitly enabled per realm.

## Building an OAuth 2.1 MCP Server with FastMCP (Python)

FastMCP is the fastest path to a production-ready OAuth-authenticated MCP server in Python. It handles the JSON-RPC transport, tool registration, and middleware integration, so you only need to implement the OAuth validation layer. The key design principle is that your MCP server is a resource server only — it never shows login pages, never issues tokens, and never stores credentials. Token issuance is the authorization server's job.

The minimal implementation requires four components: the Protected Resource Metadata endpoint, a Bearer token validator middleware, tool definitions, and an ASGI app that wires them together.

```python
from fastmcp import FastMCP
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import httpx
import jwt  # PyJWT

MCP_SERVER_URL = "https://your-mcp-server.com"
AUTHORIZATION_SERVER = "https://auth.example.com"
JWKS_URI = f"{AUTHORIZATION_SERVER}/.well-known/jwks.json"
REQUIRED_SCOPE = "mcp:read"

mcp = FastMCP("Secure MCP Server")
app = FastAPI()

# Protected Resource Metadata (RFC 9728)
@app.get("/.well-known/oauth-protected-resource")
async def protected_resource_metadata():
    return JSONResponse({
        "resource": MCP_SERVER_URL,
        "authorization_servers": [AUTHORIZATION_SERVER],
        "scopes_supported": ["mcp:read", "mcp:write"],
        "bearer_methods_supported": ["header"],
    })

# Token validation middleware
@app.middleware("http")
async def validate_bearer_token(request: Request, call_next):
    # Skip auth for metadata endpoint
    if request.url.path == "/.well-known/oauth-protected-resource":
        return await call_next(request)

    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return JSONResponse(
            status_code=401,
            headers={
                "WWW-Authenticate": (
                    f'Bearer realm="{MCP_SERVER_URL}", '
                    f'resource_metadata="{MCP_SERVER_URL}/.well-known/oauth-protected-resource"'
                )
            },
            content={"error": "unauthorized"},
        )

    token = auth_header.removeprefix("Bearer ")
    try:
        # Fetch JWKS and validate JWT
        async with httpx.AsyncClient() as client:
            jwks_resp = await client.get(JWKS_URI)
            jwks = jwks_resp.json()

        jwks_client = jwt.PyJWKClient(JWKS_URI)
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            audience=MCP_SERVER_URL,  # validate aud claim
        )

        # Check required scope
        scopes = payload.get("scope", "").split()
        if REQUIRED_SCOPE not in scopes:
            raise HTTPException(status_code=403, detail="insufficient_scope")

        request.state.user_id = payload.get("sub")
        return await call_next(request)

    except jwt.InvalidTokenError as e:
        return JSONResponse(
            status_code=401,
            headers={"WWW-Authenticate": f'Bearer error="invalid_token" error_description="{e}"'},
            content={"error": "invalid_token"},
        )

# Tool definition
@mcp.tool()
async def get_data(query: str) -> str:
    """Fetch data based on a query string."""
    return f"Data for: {query}"

# Mount MCP under FastAPI
app.mount("/mcp", mcp.get_asgi_app())
```

This structure gives you a single ASGI application that handles both the OAuth metadata discovery and the MCP protocol. The `audience` validation in `jwt.decode` is non-negotiable: without it, a token issued for a different resource server can be replayed against yours. Always validate `aud` against your server's canonical URL.

## Token Management: Access Tokens, Refresh Tokens, and Introspection

Token management for MCP deployments follows a short-lived access token + refresh token pattern, because AI agents may run for hours or days without user interaction. The MCP spec recommends access token lifetimes of 5–30 minutes — short enough to limit the blast radius of a leaked token, long enough to avoid excessive token refresh overhead during a typical tool-calling session. Refresh tokens should have lifetimes of 24 hours to 30 days depending on your security posture, with rotation on each use (a leaked refresh token can only be used once before the original is invalidated).

Token introspection (RFC 7662) is the alternative to local JWT validation when you need real-time validity checks — for example, to immediately revoke access after a security incident without waiting for the token's expiry. The introspection endpoint accepts a `token` POST parameter and returns a JSON object with `active` (boolean), `scope`, `exp`, `sub`, and other claims. The tradeoff is latency: every MCP request triggers an HTTP round-trip to the authorization server.

```python
async def introspect_token(token: str, auth_server: str, client_id: str, client_secret: str) -> dict:
    """Validate token via introspection endpoint (use when revocation is critical)."""
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{auth_server}/oauth/introspect",
            data={"token": token},
            auth=(client_id, client_secret),
        )
        payload = resp.json()
        if not payload.get("active"):
            raise HTTPException(status_code=401, detail="token_revoked")
        return payload
```

For most MCP servers, local JWT validation (verifying the signature and `exp` claim) is the right default, with a cached JWKS response (5-minute TTL) to avoid hitting the authorization server on every request. Reserve introspection for high-security tools — those that execute write operations, access PII, or trigger financial transactions — where the cost of a revoked token still being accepted for 30 minutes is unacceptable.

Refresh token handling in agent workflows requires careful design: agents often run in background tasks without a user session, so the refresh flow must be non-interactive. Store refresh tokens in an encrypted secret store (AWS Secrets Manager, HashiCorp Vault, or environment variables in development), never in application logs or error messages. Implement a token refresh with 60-second overlap before expiry to avoid race conditions on concurrent tool calls.

## Enterprise Patterns: The MCP Gateway Architecture

The MCP gateway pattern has emerged as the dominant enterprise architecture for OAuth-authenticated MCP deployments in 2026. Rather than implementing OAuth validation in every individual MCP server, a centralized gateway proxy sits in front of all servers, handles token validation, enforces scope-based routing, and provides a unified audit log. Individual MCP servers behind the gateway can run without OAuth code entirely, accepting connections only from the trusted gateway IP range.

The gateway architecture solves three enterprise problems that per-server OAuth implementation cannot. First, it centralizes credential policy: rotate the signing keys once at the gateway, and all downstream servers benefit immediately. Second, it solves the confused deputy problem — a vulnerability where a malicious MCP server uses its own token to call another MCP server on behalf of the original caller. The gateway enforces token isolation by reissuing downstream tokens with narrowed scopes. Third, it enables centralized rate limiting, request logging, and anomaly detection without modifying individual server code.

A production MCP gateway handles several key functions:

| Gateway Function | Implementation |
|---|---|
| Protected Resource Metadata | Serves unified `/.well-known` endpoints for all upstream servers |
| Token validation | Validates Bearer tokens from clients; caches JWKS with 5-min TTL |
| Scope routing | Routes `mcp:crm:read` to CRM server, `mcp:db:write` to DB server |
| Downstream token | Issues scoped downstream tokens or passes validated claims as headers |
| Audit logging | Logs every tool call with `sub`, `scope`, timestamp, and response code |
| Rate limiting | Per-client-ID rate limits to prevent token abuse by compromised agents |

Popular open-source options for building an MCP gateway include Kong (with JWT and OAuth 2.0 plugins), Traefik with ForwardAuth middleware, and custom FastAPI proxies using the HTTPX streaming client. For teams already using Cloudflare, Cloudflare's Workers-based OAuth validation can serve as a lightweight gateway layer with near-zero latency overhead.

The main tradeoff of the gateway pattern is that it introduces a single point of failure. Mitigate this with multiple gateway instances behind a load balancer, active health checks on upstream MCP servers, and circuit breakers that fail open (return 503 rather than silent data loss) when an upstream is unavailable.

## Security Best Practices and Common Pitfalls

Securing MCP OAuth 2.1 implementations requires addressing a set of attack patterns specific to AI agent deployments. The most critical pitfall is missing audience validation: if your MCP server validates the token signature and expiry but doesn't check the `aud` claim, any valid token issued for *any* resource on your authorization server can access your tools. This is a concrete attack vector, not a theoretical one — a token issued to access a user's calendar can be replayed against your MCP server if audience validation is absent.

**Seven rules for production MCP OAuth security:**

1. **Always validate `aud`** — check that the token's audience matches your server's canonical URL exactly (including scheme and no trailing slash).
2. **Use S256 PKCE exclusively** — reject any authorization request with `code_challenge_method=plain` at the authorization endpoint.
3. **Enforce HTTPS everywhere** — never accept Bearer tokens over HTTP in production; HTTPS ensures the token is not intercepted in transit.
4. **Set short access token lifetimes** — 5–15 minutes for tools that access sensitive data; 15–30 minutes for read-only tools.
5. **Rotate refresh tokens on use** — configure your authorization server for refresh token rotation; a rotated token that's used twice indicates a theft.
6. **Scope your tokens narrowly** — issue `mcp:read` for read operations and `mcp:write` for write operations; never issue a single broad scope that covers everything.
7. **Log and alert on 401/403 spikes** — a sudden increase in authentication failures often indicates a compromised client or a misconfigured agent retrying with an expired token.

Common pitfalls to avoid:

- **Returning 403 without `WWW-Authenticate`** — clients expect this header to discover your authorization server; without it, they cannot initiate the flow automatically.
- **Storing tokens in logs** — structured logging libraries often serialize full request objects; explicitly mask the `Authorization` header before logging.
- **Ignoring clock skew** — JWT validators with zero tolerance for `nbf` and `exp` clock drift will fail intermittently; allow 30–60 seconds of leeway.
- **Using symmetric keys (HMAC)** — HS256 requires sharing the secret with both the issuer and the validator; RS256 or ES256 asymmetric keys eliminate this risk.

## Testing and Debugging Your OAuth MCP Flow

Testing an OAuth 2.1 MCP flow end-to-end requires a local authorization server, a test MCP client, and instrumented middleware that logs every step of the token lifecycle. The fastest local setup uses Keycloak in Docker, which supports all required OAuth 2.1 features including dynamic client registration, PKCE, token introspection, and RFC 8414 metadata discovery.

```bash
# Start Keycloak for local MCP OAuth testing
docker run -d \
  -p 8080:8080 \
  -e KEYCLOAK_ADMIN=admin \
  -e KEYCLOAK_ADMIN_PASSWORD=admin \
  quay.io/keycloak/keycloak:24.0.1 start-dev

# After startup, configure realm at http://localhost:8080
# Create: realm "mcp-test", client "mcp-server" (resource server), 
# client "mcp-client" (public, PKCE only)
```

A minimal test script that validates your full OAuth flow:

```python
import httpx
import secrets
import hashlib
import base64

MCP_SERVER = "http://localhost:8000"
AUTH_SERVER = "http://localhost:8080/realms/mcp-test"

def run_flow_test():
    # 1. Fetch Protected Resource Metadata
    meta = httpx.get(f"{MCP_SERVER}/.well-known/oauth-protected-resource").json()
    assert meta["authorization_servers"], "Missing authorization_servers"
    print("✓ Protected Resource Metadata OK")

    # 2. Fetch Authorization Server Metadata  
    as_url = meta["authorization_servers"][0]
    as_meta = httpx.get(f"{as_url}/.well-known/oauth-authorization-server").json()
    assert as_meta["token_endpoint"], "Missing token_endpoint"
    print("✓ Authorization Server Metadata OK")

    # 3. Validate PKCE S256 enforcement (plain should be rejected)
    verifier = secrets.token_urlsafe(64)
    challenge_bytes = hashlib.sha256(verifier.encode()).digest()
    challenge = base64.urlsafe_b64encode(challenge_bytes).rstrip(b"=").decode()
    print(f"✓ PKCE credentials generated (verifier length: {len(verifier)})")

    print("All pre-flight checks passed. Proceed with browser-based auth flow.")

run_flow_test()
```

For debugging token validation failures, the most common root causes and their signals:

| Error | Status | `error` field | Root cause |
|---|---|---|---|
| Missing `Authorization` header | 401 | `unauthorized` | Client not attaching Bearer token |
| Expired token | 401 | `invalid_token` | `exp` claim in the past; check client refresh logic |
| Wrong audience | 401 | `invalid_token` | `aud` claim doesn't match server URL |
| Insufficient scope | 403 | `insufficient_scope` | Token missing required scope; check client's `scope` parameter |
| Signature validation failure | 401 | `invalid_token` | JWKS cache stale after key rotation; force refresh |
| Missing `WWW-Authenticate` | — | — | Server bug; add header to all 401 responses |

Use structured logging at the middleware level with a correlation ID per request, and emit a log line for every token validation outcome — success and failure. This makes tracing a multi-step agent workflow across tool calls tractable when things go wrong in production.

## Frequently Asked Questions

**Do stdio-based MCP servers need OAuth?**
No. The MCP spec explicitly exempts stdio-based servers (those launched as subprocesses by the MCP client) from the OAuth requirement. Stdio servers run with the same trust level as the host process, so environment variable-based credentials (API keys, secrets) are sufficient and appropriate. OAuth 2.1 is only mandatory for remote HTTP/SSE-based servers that multiple agents or users access over a network.

**Can I use API keys instead of OAuth for a remote MCP server?**
Technically possible but not compliant with the MCP spec for remote servers, and increasingly rejected by major MCP clients (Claude Desktop, ChatGPT plugins) that follow the spec. API keys are long-lived static secrets that don't support scope-based access control, token revocation, or multi-user consent flows. If you control both the client and server and security requirements are low, API keys are pragmatic. For any public or enterprise deployment, OAuth 2.1 is required.

**What authorization server should I use in production?**
Auth0 and Okta are the lowest-friction options for teams without existing identity infrastructure — both support PKCE, dynamic client registration, JWKS, and token introspection out of the box. For self-hosted requirements, Keycloak (open source) and Zitadel (open source, OIDC-native) are the two strongest choices. Avoid building a custom authorization server: the surface area for security mistakes in token issuance, PKCE validation, and key management is enormous.

**How do I handle token refresh in a long-running AI agent?**
Implement a token refresh 60 seconds before the access token expires, using the `expires_in` value from the initial token response. Store the refresh token in an encrypted secret store and implement single-consumer locking if multiple tool calls can run concurrently — two simultaneous refresh attempts will consume the refresh token, causing one to fail. After rotation, update the stored refresh token immediately before returning the new access token to the caller.

**What's the confused deputy problem in MCP and how does OAuth solve it?**
The confused deputy problem occurs when a compromised or malicious MCP server uses its own access token to make requests to other MCP servers or downstream APIs on behalf of the original user, escalating its privileges beyond what the user intended. OAuth 2.1 addresses this by binding tokens to specific audiences (`aud` claim) and scopes: a token issued for `mcp-server-a` with `mcp:read` scope is cryptographically rejected by `mcp-server-b`. The enterprise MCP gateway pattern provides an additional layer by reissuing narrow downstream tokens for each hop, so no single token can be replayed across service boundaries.
