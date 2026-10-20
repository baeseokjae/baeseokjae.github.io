---
title: 'SonarQube MCP Server for GitHub Copilot: Correct Setup and Verification'
date: 2026-07-05
lastmod: '2026-10-20T07:02:10.628622+00:00'
description: Configure SonarQube MCP over stdio in VS Code, distinguish Cloud and Server settings, and verify that analysis results match the code you changed.
draft: false
schema: schema-sonarqube-mcp-server-copilot-guide-2026
cover:
  alt: 'SonarQube MCP Server for GitHub Copilot: Correct Setup and Verification'
  image: /images/sonarqube-mcp-server-copilot-guide-2026.png
  relative: false
---

SonarQube MCP gives an assistant a way to work with SonarQube information. The most useful setup check is whether the assistant can identify the correct project and analysis revision. A connected process alone does not prove that the current working tree passed a quality gate.

This guide uses the documented container and a VS Code configuration. The configuration was checked as JSON and against the official setup instructions; no authenticated SonarQube deployment was exercised for this review.

## Use the MCP transport the client expects

The [official server README](https://raw.githubusercontent.com/SonarSource/sonarqube-mcp-server/master/README.md) identifies `sonarsource/sonarqube-mcp` as the container image and shows `1.19.0.2785` as a pinned-version example. In the stdio setup, the editor launches Docker with `-i` and communicates through its input/output streams. This is not an HTTP service exposed at `/analyze` on a published port.

[VS Code's MCP documentation](https://code.visualstudio.com/docs/agent-customization/mcp-servers) uses a `servers` object in `.vscode/mcp.json`. Keep token entry separate from the checked-in configuration.

## A Server configuration to adapt

Download the [Server configuration](/research/content-quality-2026-10/sonarqube-vscode.json), inspect it, and place its contents in `.vscode/mcp.json` in a repository you trust:

```json
{
  "inputs": [
    {"type": "promptString", "id": "sonar-token", "description": "SonarQube user token", "password": true},
    {"type": "promptString", "id": "sonar-url", "description": "SonarQube Server URL"}
  ],
  "servers": {
    "sonarqube": {
      "type": "stdio",
      "command": "docker",
      "args": ["run", "--init", "--pull=always", "-i", "--rm", "-e", "SONARQUBE_TOKEN", "-e", "SONARQUBE_URL", "sonarsource/sonarqube-mcp:1.19.0.2785"],
      "env": {
        "SONARQUBE_TOKEN": "${input:sonar-token}",
        "SONARQUBE_URL": "${input:sonar-url}"
      }
    }
  }
}
```

The tag is a documented reproducible example, not a claim that it is the latest release. Check its compatibility with your SonarQube deployment before adopting it. Docker must be available to the editor process, and the URL must be reachable from the container.

Use a user token with access limited to the projects you need. Do not paste the real value into a repository file or an assistant conversation. Review the available tools and their permissions before enabling automatic approval.

## Cloud and Server are different configurations

For SonarQube Cloud, the documented setup passes `SONARQUBE_TOKEN` and `SONARQUBE_ORG`; the US region also needs `SONARQUBE_URL=https://sonarqube.us`. Self-hosted Server uses the user token and its Server URL. Update both the environment mapping and the Docker `-e` arguments when changing these settings.

Do not copy a Cloud organization setting into a Server configuration and assume it is harmless. Select the setup for the service you actually use, then verify project access.

## Verify the whole quality workflow

Start with a read-only task: identify a known project and retrieve its current findings using the tools exposed by your installed server. Consult the [tool reference](https://docs.sonarsource.com/sonarqube-mcp-server/reference/tools) rather than inventing an endpoint or assuming every tool is available in every setup.

| Check | Evidence to keep | What a failure means |
|---|---|---|
| MCP server starts | Client connection log without tokens | Docker, image, transport, or environment issue |
| Intended project is visible | Project key and organization | Wrong service, token scope, or project selection |
| Findings match expected analysis | Branch and analyzed revision | Results may describe older or different code |
| Proposed patch is valid | Local tests and reviewed diff | A suggested fix can introduce a regression |
| New analysis finishes | Scanner/CI result for the changed revision | An edited file alone does not refresh project analysis |
| Quality gate is evaluated | Gate result tied to that analysis | Avoid treating stale success as approval of the patch |

If the editor connects but no project appears, investigate permissions before changing prompts. If analysis is stale, run the appropriate scanner or CI workflow. If Docker cannot reach a service on the host, inspect container networking; publishing a new MCP port does not solve a stdio configuration error.

This sequence provides an auditable outcome: the reviewed change, its actual analysis, and the resulting gate decision belong to the same revision.

## Revision note

**Updated October 20, 2026.** Replaced the incorrect container name, detached-port setup, and invented REST endpoints with documented stdio configuration. Removed unsupported competitor quality rankings. Retained the original publication date.

## Primary sources

Checked October 20, 2026: [sonar readme](https://raw.githubusercontent.com/SonarSource/sonarqube-mcp-server/master/README.md); [vscode mcp](https://code.visualstudio.com/docs/agent-customization/mcp-servers); [sonar tools](https://docs.sonarsource.com/sonarqube-mcp-server/reference/tools).
