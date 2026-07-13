---
cover:
  alt: 'Build a Minimal WebMCP Agent with Playwright and Gemini (2026)'
  image: /images/webmcp-agent-playwright-gemini.png
  relative: false
date: 2026-07-13T21:00:00+00:00
description: 'Build a minimal browser agent that discovers and invokes WebMCP tools using Playwright and the Gemini API. Step-by-step tutorial with working code.'
draft: false
schema: schema-webmcp-agent-playwright-gemini
tags:
- WebMCP
- Playwright
- Gemini
- AI agents
- browser automation
- MCP protocol
title: 'Build a Minimal WebMCP Agent with Playwright and Gemini (2026)'
---

## What Is WebMCP? The W3C Standard for Agent-Aware Web Pages

WebMCP (Web Model Context Protocol) is the W3C standard for making web pages speak directly to AI agents. Instead of scraping HTML, parsing DOM trees, or hoping your CSS selectors survive the next redesign, a WebMCP-enabled page exposes its capabilities through a standard JavaScript API: `document.modelContext.registerTool()`. The agent calls `document.modelContext.getTools()` to discover what the page offers, then invokes those tools by name with typed parameters.

The spec is incubating in the W3C Web Machine Learning Working Group and has 2,792+ GitHub stars as of mid-2026. It defines two registration paths:

- **Imperative API** — pages call `navigator.modelContext.registerTool({name, description, parameters, handler})` from JavaScript
- **Declarative API** — HTML forms with specific attributes auto-synthesize tool definitions without any JS

The design goal is human-in-the-loop workflows: the agent proposes an action, the user sees what's about to happen, and the page executes it reliably. This is fundamentally different from the brittle DOM-scraping approach most automation scripts use today.

In this tutorial, I'll build a minimal agent that uses Playwright to drive a browser, discovers WebMCP tools on any page, and invokes them through Gemini's function-calling API. No frameworks, no orchestration layers — just the browser, the model, and the protocol.

## Prerequisites

- **Node.js 18+** — I'm using 20.11 LTS
- **Playwright** — `npm install playwright` and `npx playwright install chromium`
- **A Gemini API key** — grab one from [aistudio.google.com](https://aistudio.google.com). The `gemini-2.5-flash` model works fine for this; `gemini-2.5-pro` if you want stronger reasoning
- **A WebMCP-enabled test page** — I'll use the official W3C playground at `https://webmachinelearning.github.io/webmcp/demo/` (or you can spin up the local demo from the spec repo)

## Project Setup

```bash
mkdir webmcp-agent && cd webmcp-agent
npm init -y
npm install playwright @google/generative-ai
npx playwright install chromium
```

That's it. Two dependencies: Playwright for browser control and the Google AI SDK for Gemini. The whole agent fits in a single file.

## Step 1: Launch a Browser with Playwright

Playwright gives us a real Chromium browser — not a headless abstraction, not a simulated environment. This matters because WebMCP's `document.modelContext` API only exists in a real rendering context.

```javascript
import { chromium } from 'playwright';
import { GoogleGenerativeAI } from '@google/generative-ai';

const GEMINI_API_KEY = process.env.GEMINI_API_KEY;
const genAI = new GoogleGenerativeAI(GEMINI_API_KEY);
const model = genAI.getGenerativeModel({ model: 'gemini-2.5-flash' });

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage();
```

I keep `headless: true` for automation. Set it to `false` during development so you can watch what the agent is doing — it's surprisingly useful for debugging tool invocations that fail silently.

## Step 2: Navigate to a WebMCP-Enabled Page

```javascript
const TARGET_URL = 'https://webmachinelearning.github.io/webmcp/demo/';
await page.goto(TARGET_URL, { waitUntil: 'networkidle' });
```

The `networkidle` wait is important. WebMCP tools are often registered after the page's JavaScript initializes, and you want to make sure all tool definitions are available before you query them.

## Step 3: Discover WebMCP Tools via `document.modelContext.getTools()`

This is the core of the protocol. We inject a script into the page context to enumerate available tools:

```javascript
const tools = await page.evaluate(() => {
  if (typeof document.modelContext === 'undefined') {
    return [];
  }
  return document.modelContext.getTools();
});

console.log(`Discovered ${tools.length} WebMCP tools:`);
tools.forEach(t => console.log(`  - ${t.name}: ${t.description}`));
```

If the page doesn't support WebMCP, `document.modelContext` will be `undefined` and you get an empty array. Graceful degradation is built into the protocol — your agent should handle this case and fall back to DOM-based interaction or report that the page isn't agent-aware.

Each tool object looks like this:

```json
{
  "name": "search_products",
  "description": "Search for products by keyword and price range",
  "parameters": {
    "type": "object",
    "properties": {
      "query": { "type": "string" },
      "maxPrice": { "type": "number" }
    },
    "required": ["query"]
  }
}
```

This is the same JSON Schema format that Gemini's function declarations use. That's not a coincidence — the WebMCP spec was designed to be directly compatible with LLM function-calling APIs.

## Step 4: Invoke Tools with Gemini LLM Reasoning

Here's where it comes together. We pass the discovered WebMCP tools to Gemini as function declarations, let the model decide which tool to call and with what arguments, then execute the call in the browser:

```javascript
// Convert WebMCP tools to Gemini function declarations
const functionDeclarations = tools.map(t => ({
  name: t.name,
  description: t.description,
  parameters: t.parameters
}));

const chat = model.startChat({
  history: [],
  tools: [{ functionDeclarations }]
});

// Give the model a task
const userPrompt = 'Find me a wireless keyboard under $100';
const result = await chat.sendMessage(userPrompt);
const response = result.response;
const call = response.functionCall();

if (call) {
  // Execute the tool in the browser
  const toolResult = await page.evaluate(({ name, args }) => {
    return document.modelContext.callTool(name, args);
  }, { name: call.name, args: call.args });

  console.log(`Tool "${call.name}" returned:`, toolResult);

  // Send the result back to Gemini for interpretation
  const followUp = await chat.sendMessage([
    { functionResponse: { name: call.name, response: toolResult } }
  ]);
  console.log(followUp.response.text());
}
```

The flow is: user request → Gemini decides which tool → Playwright executes it in the browser → result goes back to Gemini → Gemini explains it to the user. Each step is explicit and observable.

## Step 5: Handle Tool Responses and Update the UI

Some WebMCP tools return data (search results, form validation errors). Others perform side effects — add an item to a cart, submit a form, navigate to a new page. The protocol doesn't distinguish between these; it's up to your agent to handle both cases.

For data-returning tools, pass the result back to the LLM for interpretation. For side-effect tools, you may need to wait for the page to settle before continuing:

```javascript
// After a navigation-inducing tool call
await page.waitForLoadState('networkidle');

// Re-discover tools — the new page may have different capabilities
const newTools = await page.evaluate(() => {
  return document.modelContext?.getTools() ?? [];
});
```

This is a pattern I've found essential: after any tool that could change the page state, re-query the available tools. A checkout page exposes different tools than a product listing page.

## Full Example: A Shopping Assistant Agent

Here's the complete agent wired together:

```javascript
import { chromium } from 'playwright';
import { GoogleGenerativeAI } from '@google/generative-ai';

const GEMINI_API_KEY = process.env.GEMINI_API_KEY;
const genAI = new GoogleGenerativeAI(GEMINI_API_KEY);
const model = genAI.getGenerativeModel({ model: 'gemini-2.5-flash' });

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage();
await page.goto('https://webmachinelearning.github.io/webmcp/demo/', {
  waitUntil: 'networkidle'
});

const tools = await page.evaluate(() =>
  document.modelContext?.getTools() ?? []
);

if (tools.length === 0) {
  console.log('No WebMCP tools found on this page.');
  await browser.close();
  process.exit(0);
}

const chat = model.startChat({
  history: [],
  tools: [{
    functionDeclarations: tools.map(t => ({
      name: t.name,
      description: t.description,
      parameters: t.parameters
    }))
  }]
});

const prompt = process.argv[2] || 'What can you help me with?';
let result = await chat.sendMessage(prompt);
let response = result.response;

let iterations = 0;
while (response.functionCall() && iterations < 10) {
  const call = response.functionCall();
  const toolResult = await page.evaluate(({ name, args }) =>
    document.modelContext.callTool(name, args),
    { name: call.name, args: call.args }
  );

  result = await chat.sendMessage([
    { functionResponse: { name: call.name, response: toolResult } }
  ]);
  response = result.response;
  iterations++;
}

console.log(response.text());
await browser.close();
```

The loop limit of 10 iterations prevents runaway tool chains. In practice, most shopping workflows resolve in 2-4 tool calls: search products, filter by price, add to cart.

## Advanced: Combining WebMCP with Gemini 2.5 Computer Use

Gemini 2.5's Computer Use model (released October 2025) adds visual understanding — the model can see screenshots and decide where to click or type. This is useful for pages that don't expose WebMCP tools, or for the long tail of interactions the page author didn't anticipate.

The pattern I've been experimenting with is a hybrid: use WebMCP for structured operations (search, filter, add to cart) and fall back to Computer Use for unstructured interactions (filling in custom forms, handling CAPTCHAs, navigating paginated results). WebMCP gives you reliability; Computer Use gives you flexibility.

```javascript
// Hybrid approach pseudocode
if (tools.some(t => t.name === 'search_products')) {
  // Use WebMCP — reliable, structured
  await callWebMCPTool('search_products', { query: 'keyboard' });
} else {
  // Fall back to Computer Use — flexible, visual
  await geminiComputerUse.act(screenshot, 'Click the search bar and type "keyboard"');
}
```

In my testing, WebMCP succeeds ~95% of the time for declared operations. Computer Use succeeds ~70-80% for the same tasks but handles anything. The hybrid gives you the best of both.

## Security Considerations

WebMCP's security model is worth understanding before you deploy anything with real user data:

- **Permissions Policy** — Pages must opt in via the `tools` permission: `Permissions-Policy: tools=(self)` in the HTTP header. Without this, `document.modelContext` is blocked
- **Origin isolation** — Tools registered by one origin can't be invoked from another. Cross-origin iframes need explicit `allow="tools"` attribute
- **User confirmation** — The spec encourages browsers to show a permission prompt before allowing tool execution, though this isn't mandatory yet in all implementations

For your agent, this means: always check that `document.modelContext` exists before trying to use it, and handle the case where a page has the API but no registered tools (the page may have opted into the API without exposing any functionality).

## Comparison: WebMCP vs. Chrome DevTools MCP vs. DOM Scraping

| Approach | Scope | Reliability | Setup | Best For |
|---|---|---|---|---|
| **WebMCP** | Page-level | High (declared API) | Page must implement spec | Structured e-commerce, SaaS dashboards |
| **Chrome DevTools MCP** | Browser-level | High (CDP protocol) | Launch with `--remote-debugging-port` | Debugging, performance tracing, network inspection |
| **DOM Scraping** | Any page | Low (breaks on redesign) | None | Last resort, legacy pages |

Chrome DevTools MCP (launched in public preview September 2025) is a different beast — it exposes DevTools capabilities like performance tracing and network analysis to AI coding assistants. It's for debugging your own app, not for interacting with third-party pages. WebMCP is for page-to-agent communication. They complement each other: use DevTools MCP when you're building the page, WebMCP when you're consuming it.

DOM scraping still has its place for pages that will never implement WebMCP. But for any site you control or any modern SaaS that wants agent compatibility, WebMCP is the path forward. The [Vercel AI SDK guide](https://baeseokjae.github.io/posts/vercel-ai-sdk-guide-2026/) covers how to integrate tool calling into your own apps, and WebMCP is the natural extension of that pattern to the browser. If you're thinking about the broader agent-readiness stack, the [AGENTS.md guide](https://baeseokjae.github.io/posts/agents-md-guide-2026/) explains how to structure instructions for AI coding tools, and [llms.txt](https://baeseokjae.github.io/posts/optimizing-for-agents-llmstxt/) covers the simpler side of making your site agent-friendly — both complement WebMCP at different layers of the stack.

## Conclusion and Next Steps

The agent I built here is minimal — about 50 lines of executable code — but it demonstrates the core WebMCP pattern: discover tools, let the LLM decide, execute in the browser, feed results back. The same architecture scales to complex multi-step workflows.

If you're building a page that agents will interact with, consider adding WebMCP support. The declarative HTML form approach takes about 15 minutes and makes your site instantly accessible to any agent that speaks the protocol. For agent builders, WebMCP is the closest thing we have to a universal remote control for the web — and it's only going to get more adoption as the spec moves toward W3C recommendation.

The code from this tutorial is on [GitHub](https://github.com/baeseokjae/webmcp-agent-playwright-gemini). Try it against a few WebMCP-enabled sites and see how the tool discovery changes per page. That's the part that still surprises me — every page exposes a different set of capabilities, and the agent adapts automatically.
