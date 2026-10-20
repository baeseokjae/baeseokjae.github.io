---
cover:
  image: /images/og-default.png
  alt: RockB editorial guides
  relative: false
date: 2026-05-12 00:00:00+00:00
description: Check maintenance, permissions, provider routing and total cost before choosing an open-source coding agent; avoid stale rankings and install-count claims.
draft: false
schema: schema-open-source-ai-coding-agents-2026
tags:
- cline
- roo-code
- kilo-code
- aider
- open-source-ai
title: 'Open-Source AI Coding Agents: Cline, Roo Code, Kilo and Aider Evaluation'
lastmod: '2026-10-20T08:06:38.069366+00:00'
---

An open repository tells you something about inspectability and licensing. It does not establish that a tool is actively maintained, that its default workflow is private or that model usage is free.

This comparison checks the projects' current documentation and gives a common pilot protocol. It does not report a hands-on ranking or use GitHub stars as a substitute for task performance.

## What the current repositories say

| Project | Documented workflow | What deserves attention |
|---|---|---|
| Cline | Agent interfaces with Plan/Act and configurable approvals | Auto-approval changes the human-control boundary |
| Roo Code | Mode-based agent design; README now contains a shutdown notice | Existing installations and forks need a maintenance review |
| Kilo | Coding-agent interfaces and provider/model routing | Check which gateway or account receives requests |
| Aider | Terminal pair programming with repository mapping | Check model support, edit behavior and Git workflow |

[Cline's README](https://raw.githubusercontent.com/cline/cline/main/README.md) describes both approval-based and autonomous options. It is inaccurate to promise that every operation always requires confirmation.

[Roo Code's README](https://raw.githubusercontent.com/RooCodeInc/Roo-Code/main/README.md) explicitly states that the extension was shut down. Historical capabilities do not make it a current maintained recommendation. [Kilo's README](https://raw.githubusercontent.com/Kilo-Org/kilocode/main/README.md) and [Aider's README](https://raw.githubusercontent.com/Aider-AI/aider/main/README.md) describe different interfaces and model integration paths; inspect the exact package and release you intend to use.

## Inspect permission and data paths

Record which operations can happen without a prompt: reading files, writing files, running commands, opening browsers and calling remote tools. Test a harmless denied action and confirm the enforcement occurs outside the model's natural-language reasoning.

Map inference requests, embeddings, logs and MCP calls to their destinations. Bring-your-own-key can mean direct provider billing, but a gateway or managed service may still sit in the path. Check the actual configuration.

Use a disposable repository for the pilot. Keep production credentials and customer data out of the first evaluation. Source-code visibility helps inspection but does not eliminate dependency or extension-update risk.

## Run the same coding tasks

Use the [coding-agent pilot sheet](/research/content-quality-batch2-2026-10/coding-agent-pilot.csv) with a known starting commit. Include a small feature with tests, a regression repair, a repository-navigation question and a task that should be denied by permissions.

Hold the model and budget constant where possible. If a tool requires another model or service, document the difference. Record the prompts, permission settings, changed files, tests, human corrections and failed attempts.

Compare accepted patches, not generated lines or apparent confidence. Check whether the agent preserved unrelated work and respected repository instructions. A task completed only after an unrecorded human hint is not the same condition as an unaided run.

## License and maintenance are separate checks

Read the license shipped with the exact extension, CLI or package. Repository components, hosted services and underlying model weights can have different terms. Do not assume a fork inherits every operational promise of its predecessor.

Check recent releases, supported editor versions, vulnerability reporting and who owns updates in your organization. For an inactive project, decide whether you can maintain a fork or migrate. The [Continue comparison](/posts/continue-dev-vs-github-copilot-2026/) illustrates why maintenance status can outweigh an older feature matrix.

## Estimate total cost and make a bounded decision

Add model charges, hosted-service fees, infrastructure and time spent reviewing or fixing output. Free source code does not imply zero operating cost. An agent that uses more iterations can cost more even when it has no seat fee.

Choose a tool after its pilot meets your repository and permission requirements. Keep the evaluation record and recheck after major upgrades. There is no defensible universal winner from the evidence gathered for this revision; there is a practical way to compare the workflows you need.

## Revision note

**Updated October 20, 2026.** Removed unsupported install counts, funding/user statistics, API-budget estimates and rankings. Added current shutdown/maintenance context, configurable permission distinctions and a common task-evaluation sheet.

## Primary sources

Checked October 20, 2026: [cline](https://raw.githubusercontent.com/cline/cline/main/README.md); [roo](https://raw.githubusercontent.com/RooCodeInc/Roo-Code/main/README.md); [kilo](https://raw.githubusercontent.com/Kilo-Org/kilocode/main/README.md); [aider](https://raw.githubusercontent.com/Aider-AI/aider/main/README.md).
