---
cover:
  image: /images/og-default.png
  alt: RockB editorial guides
  relative: false
date: 2026-05-05 15:03:56+00:00
description: Understand remote MCP authorization, token audience and tool-level access, then validate the implementation with a concrete negative-test checklist.
draft: false
schema: schema-mcp-oauth-authentication-guide-2026
tags:
- MCP
- OAuth 2.1
- authentication
- security
- AI agents
- FastMCP
- PKCE
title: 'MCP OAuth Authentication Guide: Discovery, Audience Validation and Access Tests'
lastmod: '2026-10-20T08:06:38.069366+00:00'
---

For a remote MCP server, the key question is not whether a request contains a bearer token. It is whether that token is valid for this server and whether its owner may perform the requested operation on the requested resource.

This guide follows the linked authorization specification and gives an implementation-review checklist. It does not claim that a short example is a complete authorization server. The previous adoption percentages and “working production implementation” framing were not supported by the available evidence.

## What MCP authorization covers

The [authorization specification](https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization) describes authorization for HTTP transports. Authorization is optional at the protocol level; HTTP implementations supporting it should follow the specification. Stdio implementations should instead obtain credentials through their environment rather than applying this remote HTTP flow.

In a protected HTTP deployment, the MCP server acts as a resource server. The authorization server authenticates the user and issues tokens. The client discovers the protected resource and authorization metadata, obtains a token, and presents it to the MCP endpoint.

The specification requires token audience validation and use of the resource indicator in the relevant requests. The [security guidance](https://modelcontextprotocol.io/docs/2026-07-28/tutorials/security/security_best_practices) also prohibits passing through tokens intended for another service. A token accepted by your downstream database or SaaS service is not automatically a valid MCP credential.

## Trace the complete request path

1. Request the protected endpoint without a token and inspect its authentication challenge and resource metadata.
2. Confirm that the advertised resource identity matches the intended MCP server. Resolve authorization metadata through the documented discovery process.
3. Complete authorization using the client's supported registration method and PKCE flow. Validate redirects and returned state.
4. Validate the access token at the resource server using the trusted issuer's supported method. Decoding a JWT without signature verification is not validation.
5. Check issuer, audience, expiry and granted scope. Then apply the application's resource and tenant permissions.
6. Only after those checks should the handler invoke the requested tool.

Treat discovered URLs and metadata as untrusted input until validated. Do not fetch arbitrary internal addresses on behalf of a client. Keep trusted issuer configuration explicit, avoid logging bearer tokens, and handle authorization-server outages by denying protected operations.

## Authentication does not decide tenant access

Consider a `read_invoice` tool taking an invoice identifier. A valid token establishes the caller and granted authority; the invoice ID in tool arguments still comes from an untrusted request. Resolve the invoice within the authenticated tenant or check a server-side ownership relation before returning it.

Never let a model-supplied `tenant_id` override the authenticated context. Scope such as `invoice:read` describes a permitted operation; it does not necessarily authorize every invoice in storage. Apply row- or object-level permissions independently of natural-language instructions.

Separate downstream credentials from incoming tokens. If the server calls another API, use the intended delegated or service credential flow with bounded permissions. Keep revocation and rotation behavior testable.

## Negative tests that should block release

The [MCP authorization acceptance sheet](/research/content-quality-batch2-2026-10/mcp-auth-acceptance.csv) includes the expected decision for missing credentials, expiry, wrong audience, insufficient scope, another tenant's resource, and an unavailable issuer.

For each test, retain the endpoint, sanitized claim summary, expected status, observed status and proof that the downstream handler did not run when access was denied. Use test tokens from a controlled issuer; do not paste production tokens into reports.

Test a valid request too. A server that rejects everything is unavailable, not correctly authorized. Repeat the same resource access through alternate tools or batch endpoints so the policy cannot be bypassed through another route. Set explicit clock-skew and key-rotation policy and test the transition around expiry.

The [offline tool-boundary example](/posts/automated-red-teaming-ai-agents/) demonstrates application authorization with synthetic records. It is separate from OAuth token verification and is not evidence that your issuer integration is secure.

## Implementation completion criteria

Ship when you can explain the discovery path, token trust boundary, permission decision and failure behavior with actual traces. Keep the issuer's library and protocol version documented. Review SDK upgrades against the specification instead of copying an old example indefinitely.

An implementation should fail safely when dependencies fail, avoid exposing secrets in errors, and let authorized clients recover from an expired session. These are observable behaviors. A percentage describing how many other servers adopted OAuth does not establish any of them.

## Revision note

**Updated October 20, 2026.** Removed unsourced OAuth adoption and exposure percentages, corrected protocol scope, and replaced the incomplete production-code claim with discovery, token-validation and tenant-boundary acceptance criteria.

## Primary sources

Checked October 20, 2026: [mcp auth](https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization); [mcp security](https://modelcontextprotocol.io/docs/2026-07-28/tutorials/security/security_best_practices).
