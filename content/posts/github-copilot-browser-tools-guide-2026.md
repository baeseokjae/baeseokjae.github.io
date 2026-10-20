---
title: 'GitHub Copilot Browser Tools in VS Code: Setup, Verification and Regression Evidence'
date: 2026-07-03 12:00:00+00:00
tags:
- GitHub Copilot
- VS Code
- AI Agents
- Browser Testing
description: Use VS Code browser tools for a scoped UI check, capture reproducible evidence, and distinguish agent exploration from a regression test.
draft: false
cover:
  image: /images/og-default.png
  alt: RockB editorial guides
  relative: false
schema: schema-github-copilot-browser-tools-guide-2026
lastmod: '2026-10-20T08:06:38.069366+00:00'
---

Browser tools can help an agent inspect the application it just changed. The useful outcome is a reproducible account of a user flow: what was opened, what was clicked, what changed, and which assertion established success.

This guide uses current VS Code documentation and a proposed checkout example. It does not report a Copilot product trial. The earlier personal story about fixing a country-switching checkout bug lacked a retained run record and is now presented as a test scenario.

## Enable and scope the browser session

[VS Code's browser-tools documentation](https://code.visualstudio.com/docs/agents/run/browser-tools) says browser tools are built in and do not require an external MCP server. The relevant setting is `workbench.browser.enableChatTools`, enabled by default in the documented workflow. Organization policy and available agent tools can still affect access.

Start an agent session, identify the application URL and describe the expected behavior. An agent normally opens an isolated tab unless an existing tab is shared. Do not assume it inherits your login or cookies. For a local app, state the actual port and use a test account with test data.

The [official walkthrough](https://code.visualstudio.com/docs/agents/guides/browser-agent-testing-guide) combines starting the app, interacting with it, finding a defect and verifying a fix. Administrators can restrict reachable domains. Review browser actions and their parameters in the conversation; a screenshot alone does not establish that the complete workflow passed.

## A concrete checkout verification task

Use this prompt after substituting your development URL:

> Open the local checkout with a test cart. Select a country, enter a valid postal code, then change country. Check that validation follows the newly selected country. Report the starting state, actions and observed validation. If you fix the app, repeat the flow and add a deterministic regression test. Do not submit a real order.

The [browser acceptance sheet](/research/content-quality-batch2-2026-10/browser-acceptance.csv) covers country switching, keyboard operation, page reload and network failure. Fill the observed-result column during your run; it is deliberately blank in the download.

First reproduce the defect without changing code. Capture a screenshot or trace at the failing state, alongside the URL, viewport and commit. Next identify the state transition responsible for validation. After a focused patch, repeat the original flow and a neighboring case, such as switching back to the original country.

The persistent result matters. A page can display a success message while failing to save the record. For a settings screen, reload and confirm the saved value. For checkout, inspect the test backend or mocked request rather than relying on a green notification.

## Exploration versus a regression suite

An exploratory agent chooses actions as it goes. A regression test fixes the starting state, actions and assertions so another run can reproduce them. Browser-assisted discovery is useful input to that test, but the conversation is not the whole test suite.

When converting a finding into Playwright or your existing runner, prefer stable accessible labels or explicit test IDs. Reset test data between runs. Assert the visible behavior and, when relevant, the persisted state. Avoid arbitrary sleeps that hide race conditions. Save a failing trace so a reviewer can distinguish a selector failure from an application defect.

Keep the human review questions simple: did the test fail before the patch, does it pass after it, and does it assert the reported defect? A passing test that never changes country cannot verify the country-switching example.

## Troubleshooting and evidence to keep

| Symptom | First check | Evidence worth keeping |
|---|---|---|
| Browser tool missing | Setting, tool selection and organization policy | Available tools and relevant setting |
| Page cannot be reached | Development server, port and domain restrictions | Failed URL and tool error |
| Login missing | Isolated tab versus shared session | Test-account state, without credentials |
| UI works once but fails after reload | Backend persistence and request failures | Reload sequence and response status |
| Agent says “fixed” without a repeat run | Ask for the original reproduction again | Before/after assertions |

Do not expose customer data in screenshots, traces or prompts. Browser inspection does not grant permission for production purchases, account deletion or administrative changes. Keep billing assumptions separate too: model use and tool-supported work must be assessed against your actual Copilot plan.

## Revision note

**Updated October 20, 2026.** Removed unsupported firsthand checkout experience and the unverified availability framing. Added current settings, isolated-session limitations, a concrete acceptance sheet and reproducible review criteria.

## Primary sources

Checked October 20, 2026: [vscode browser](https://code.visualstudio.com/docs/agents/run/browser-tools); [vscode browser guide](https://code.visualstudio.com/docs/agents/guides/browser-agent-testing-guide).
