---
cover:
  alt: 'Figma MCP Server Guide 2026: Design to Code with AI'
  image: /images/figma-mcp-design-to-code-2026.png
  relative: false
date: 2026-05-03 15:04:32+00:00
description: 'Complete guide to the Figma MCP server: setup, remote vs desktop, Code
  Connect, and real-world design-to-code workflows with AI agents in 2026.'
draft: false
schema: schema-figma-mcp-design-to-code-2026
tags:
- Figma
- MCP
- Design to Code
- AI Coding
- Cursor
- Claude Code
title: 'Figma MCP Server Guide 2026: Design to Code with AI'
---

The Figma MCP server turns your design files into a live context source for AI agents — eliminating the screenshot-and-describe loop that slows down design implementation. With one properly configured endpoint, tools like Cursor, Claude Code, and Windsurf can read your exact component hierarchy, tokens, and constraints in real time.

## What Is the Figma MCP Server? (And Why Developers Care in 2026)

The Figma MCP server is an implementation of the Model Context Protocol (MCP) that exposes your Figma design files as structured, queryable context for AI coding agents. Unlike exporting assets or taking screenshots, the MCP server streams design metadata — component names, layout constraints, spacing tokens, font styles, and the full layer tree — directly into the context window of whatever AI tool you're using. Figma officially launched bidirectional Claude Code integration (Design to Code + Code to Canvas) in February 2026, and since then adoption has accelerated sharply. The public MCP server registry expanded from 1,200 servers in Q1 2025 to 9,400+ by April 2026, and 78% of enterprise AI teams report at least one MCP-backed agent in production. For frontend developers, the Figma MCP server is the most direct path from a designer's intent to production-ready component code — without a handoff document, Zeplin export, or a six-round revision cycle.

### Why Traditional Design Handoffs Break Down

Traditional design handoffs break down because they freeze the design at export time. A static Figma export, Zeplin spec, or even a copied CSS value becomes stale the moment the designer iterates. Engineers then work from outdated specs, generating mismatch bugs that require another round of review. The Figma MCP server solves this by making the design a continuously-queried live reference — your AI agent re-reads the current file state every time it generates code, not the state from last Tuesday's export.

## Remote Server vs Desktop Server — Which Should You Use?

The Figma MCP server ships in two flavors, and choosing the wrong one will either block your workflow or add unnecessary complexity. The **remote server** connects to Figma's hosted endpoint at `https://mcp.figma.com/mcp` and is available on all Figma seats and plans — no Figma desktop app required. You authenticate with a personal access token, pass a file link in your prompt, and the server fetches the design data on demand. The **desktop server** runs locally through the Figma desktop app and requires a Dev seat or Full seat. It unlocks one major feature the remote server lacks: selection-based context — you can select a specific frame or component in Figma and have the MCP server automatically scope the context to just that element, rather than the whole file. Developers using MCP servers report 40–60% faster workflow completion vs. built-in AI capabilities alone, and most of that gain comes from the remote server alone for teams without a Dev seat.

| Feature | Remote Server | Desktop Server |
|---|---|---|
| Seat requirement | Any (Viewer, Editor) | Dev or Full seat |
| Figma desktop app required | No | Yes |
| Authentication | Personal access token | Desktop app session |
| Selection-based context | No | Yes |
| Skills / guided workflows | Yes | Yes |
| Works with Claude Code | Yes | Yes |
| Works with Cursor | Yes | Yes |
| Enterprise SSO | No | Yes |

**Recommendation:** Start with the remote server unless you specifically need selection-based context or are in an enterprise environment that requires the desktop app.

## How to Set Up the Figma Remote MCP Server (Step by Step)

Setting up the Figma remote MCP server takes under five minutes once you have a Figma personal access token. The token must have `file:read` scope; without it the server returns a 403 on every design fetch. Here is the full setup sequence:

**Step 1: Generate a Figma Personal Access Token**

1. Open Figma → Profile → Settings → Security
2. Scroll to "Personal access tokens"
3. Click "Generate new token"
4. Name it (e.g., `mcp-server`), set scope to `file:read`
5. Copy the token immediately — it won't be shown again

**Step 2: Add the MCP Server to Your AI Tool Config**

For Claude Code (`~/.claude/mcp.json` or project-level `.claude/mcp.json`):

```json
{
  "mcpServers": {
    "figma": {
      "type": "http",
      "url": "https://mcp.figma.com/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_FIGMA_TOKEN"
      }
    }
  }
}
```

For Cursor (`.cursor/mcp.json` in your project or globally):

```json
{
  "mcpServers": {
    "figma": {
      "command": "npx",
      "args": ["-y", "figma-developer-mcp"],
      "env": {
        "FIGMA_API_TOKEN": "YOUR_FIGMA_TOKEN"
      }
    }
  }
}
```

**Step 3: Verify the Connection**

Restart your AI tool, then run a quick test prompt:

```
Fetch the component list from this Figma file:
https://www.figma.com/design/XXXX/My-Design-System
```

If the server is configured correctly, the agent lists all frames and components. If you see a 401 error, the token is wrong or expired.

### Setting Up the Desktop Server Instead

Setting up the desktop server requires Figma desktop app version 116.3 or later with a Dev or Full seat. Enable MCP under `Figma menu → Preferences → Enable MCP Server`. The local server runs on `http://localhost:3845/mcp`. Add this URL (with no auth headers) to your tool's MCP config. The desktop server exposes an additional `get_selection` tool that returns metadata for whatever frame or component is currently selected in the Figma canvas.

## Connecting Figma MCP to Cursor, Claude Code, and Windsurf

Connecting the Figma MCP server to your AI coding tool follows the same pattern across clients — define the server URL or command in the tool's MCP config file — but each tool has a slightly different config location and syntax. Cursor uses `.cursor/mcp.json` (project-level) or `~/.cursor/mcp.json` (global). Claude Code uses `.claude/mcp.json` at the project root or `~/.claude/mcp.json` globally. Windsurf reads `~/.codeium/windsurf/mcp_config.json`. VS Code with the Copilot extension reads `.vscode/mcp.json`. Zed reads `~/.config/zed/settings.json` under an `"experimental.context_servers"` key. All clients support both the HTTP endpoint (remote server) and the npm package wrapper `figma-developer-mcp` (local npx runner). The HTTP endpoint is simpler for teams because there is no node runtime dependency; the npx package is useful when you need to run a custom fork or an older pinned version.

### Testing the Integration in Cursor

Once the config file is in place, open a Cursor Chat window and enable MCP in the model picker. Paste a Figma frame URL and ask:

```
Using the Figma MCP server, get the layout and component structure of this frame:
https://www.figma.com/design/XXXX?node-id=123-456
```

A working integration returns structured JSON describing the frame dimensions, children, text content, fill colors, and spacing values. If Cursor returns a generic error about "no MCP tools available," the config file path is wrong — confirm it is at the root of the workspace, not inside a subfolder.

## Your First Design-to-Code Workflow with Figma MCP

A Figma MCP design-to-code workflow follows a repeatable three-step pattern: point the AI agent at a Figma frame URL, describe what component framework you're targeting, and let the agent generate code grounded in the actual design data rather than a screenshot approximation. The real-world time savings are substantial — dashboard interfaces with 8 complex UI components that previously took 2–3 days to implement are now completed in one afternoon. Here is an example first workflow using Claude Code with the remote server configured:

**Prompt:**
```
Using the Figma MCP server, implement this dashboard card component in React + Tailwind:
https://www.figma.com/design/XXXX?node-id=45-789

Match the exact spacing, typography, and color tokens. Use the component names from the Figma file as identifiers.
```

**What the agent does:**
1. Calls the Figma MCP `get_file_nodes` tool with the node ID
2. Reads the layer tree: component name (`DashboardCard`), children (`CardHeader`, `CardMetric`, `CardTrend`), spacing (`gap: 16`, `padding: 24`), fill (`#1A1A2E`)
3. Maps color fills to Tailwind classes or inline styles
4. Generates JSX using the exact component hierarchy from the design

**What you get without Code Connect:** Generic React JSX with hardcoded Tailwind classes. Functional but not using your actual design system components.

**What you get with Code Connect:** The agent imports `DashboardCard` from your actual package, uses your `useMetric` hook, and matches the variant props your design system exposes.

### Prompting Strategies That Get Better Results

Prompting strategies that improve Figma MCP output quality share one common principle: scope the context aggressively. A whole-file query returns thousands of layers and the agent spends token budget parsing irrelevant screens. Node-ID-scoped queries — using `?node-id=FRAME_ID` in the URL — focus the server on exactly the component you're implementing. For multi-component pages, run separate prompts per component rather than one giant prompt covering the full design.

## Code Connect: The Key to Generating Your Actual Components

Code Connect is Figma's open-source mapping layer that links a Figma component to its real codebase counterpart — the actual import path, prop names, and variant mappings — so that when an AI agent reads a Figma component via MCP, it can generate code using your specific library rather than inventing generic HTML. Without Code Connect, current beta reports show 85–90% styling inaccuracy in generated code, requiring significant manual correction. With Code Connect properly configured, the same agent prompt generates code that imports from your actual package: `import { Button } from '@your-org/design-system'` instead of `<button className="px-4 py-2 bg-blue-500">`. Code Connect files live in your codebase alongside the component they describe. A minimal example for a `Button` component looks like this:

```tsx
// Button.figma.tsx
import figma from '@figma/code-connect';
import { Button } from './Button';

figma.connect(Button, 'https://www.figma.com/design/XXXX?node-id=100-200', {
  props: {
    variant: figma.enum('Variant', {
      primary: 'primary',
      secondary: 'secondary',
      ghost: 'ghost',
    }),
    label: figma.string('Label'),
    disabled: figma.boolean('Disabled'),
  },
  example: ({ variant, label, disabled }) => (
    <Button variant={variant} disabled={disabled}>{label}</Button>
  ),
});
```

Publish the Code Connect mappings with `npx @figma/code-connect publish`. After publishing, the Figma MCP server automatically includes Code Connect metadata in every response that mentions a connected component. The investment is real — teams report 40–80 hours of initial setup time for a full Figma MCP + Code Connect pipeline — but teams that complete it reduce revision cycles from 4–5 rounds to typically just one.

### Which Components to Connect First

Which components to connect first is a strategic decision that shapes ROI. Prioritize leaf-level primitives used everywhere: Button, Input, Text, Badge, Icon. These appear in almost every screen, so Code Connect coverage on primitives cascades across all generated code. Skip complex composed components (DataTable, Modal with custom logic) until primitives are stable — the agent composes correctly once it has the building blocks.

## Code to Canvas — Pushing Code Back to Figma

Code to Canvas is the less-discussed half of Figma's bidirectional MCP integration: instead of reading a Figma design to generate code, you push code into Figma as editable vector layers. This workflow is useful when a developer has built a component variant that the designer wants to incorporate into the source-of-truth Figma file. The integration, launched as part of the February 2026 Claude Code partnership, uses the MCP server's `write` capability (currently Claude Code only; Cursor and Windsurf support is in beta). The prompt pattern is straightforward:

```
Generate a Figma frame from this React component and add it to the Components page in:
https://www.figma.com/design/XXXX

Component code:
[paste component JSX here]
```

The agent reads the component's JSX structure, maps props to Figma layer properties, and calls the MCP server's write endpoint to create a new frame. The output is fully editable — auto layout, component properties, and local styles are preserved. The limitation is that complex logic (conditional renders, data fetching) is flattened to a single state in the generated frame. The agent will pick the component's default props unless you explicitly specify the state to render.

## Real-World Results, Limitations, and What to Expect

Real-world Figma MCP results in 2026 are genuinely impressive but unevenly distributed — teams with mature, well-structured design systems see dramatic gains, while teams with disorganized Figma files see marginal improvement over a screenshot workflow. Dashboard interfaces with 8 complex UI components that previously took 2–3 days to implement are now completed in one afternoon with a well-configured setup. Revision cycles drop from 4–5 rounds to typically just one. However, the 85–90% styling inaccuracy rate without Code Connect is a real ceiling — expect to correct spacing, border-radius, and responsive behavior by hand unless your design system is fully connected. The 40–80 hour initial setup cost is also real; teams that skip it and use the remote server on a disorganized file with inconsistent naming will generate code that requires heavy editing.

### What the Figma MCP Server Does Not Do

The Figma MCP server does not generate pixel-perfect code autonomously. It provides structured context — the AI agent still interprets that context and generates code, and that interpretation can go wrong. It does not handle responsive breakpoints automatically unless they are defined as Figma variables. It does not generate animations or complex interaction states. It does not replace a design system — it amplifies one. If your Figma file has inconsistent naming, unlabeled layers, or missing Auto Layout, the MCP server faithfully exposes that inconsistency to the AI agent, which then produces inconsistent code.

### Common Setup Errors

- **401 errors**: Token missing `file:read` scope or expired — regenerate the token
- **Empty layer tree**: Wrong node ID in the URL — use the node selector in Figma (`Right-click → Copy link to selection`) to get the exact ID
- **Generic code despite Code Connect**: Code Connect metadata not published — run `npx @figma/code-connect publish` after editing `.figma.tsx` files
- **Cursor can't find MCP tools**: Config file is not at workspace root — move `.cursor/mcp.json` to the project root directory

## Best Practices for Teams Using Figma MCP at Scale

Best practices for teams scaling Figma MCP across multiple engineers center on three areas: Figma file hygiene, Code Connect coverage strategy, and shared AI agent configuration. Teams that succeed at scale treat their Figma file structure as a developer dependency — not an artifact that gets cleaned up "someday." Enforcing naming conventions (PascalCase for components, kebab-case for layers), using Auto Layout everywhere, and keeping design tokens as Figma variables (not hardcoded fills) makes the MCP context structurally consistent across files, which directly improves code generation quality. Sharing the MCP config file in the repository root means every developer on the team uses identical server configuration without per-machine setup. Storing the Figma access token in a shared secrets manager (rather than each developer's `.env`) prevents token drift and revocation surprises.

### Structuring Your Figma File for MCP

Structuring your Figma file for MCP output quality follows the same principles as structuring it for developer handoff, but with stricter enforcement. Name every component and layer descriptively — the MCP server returns layer names as-is, so `Frame 457` in the AI context produces `frame457` in the generated code. Use Figma Variables for all color, spacing, and typography tokens; the MCP server exposes variable names alongside values, and Code Connect can map them to your codebase token names. Enable Auto Layout on all container frames — without Auto Layout, the agent has to infer layout intent from absolute positioning, which produces brittle CSS. Keep each Figma page focused: a `Components` page, a `Screens` page, and a `Tokens` page are easier to query than a single sprawling canvas.

### Team Workflow Recommendations

- **Commit `.figma.tsx` Code Connect files alongside component source** — treat them as first-class code, not documentation
- **Run Code Connect publish in CI** — prevents stale mappings from drifting out of sync with the component implementation
- **Create a shared Figma MCP config file** in your repo's `.claude/mcp.json` and `.cursor/mcp.json` — no per-developer setup
- **Document the "canonical frame" for each screen** — a named, top-level frame that is always the reference for AI-driven implementation
- **Review generated code against the Figma source at PR time** — add a Figma frame URL to the PR description so reviewers can compare visually

---

## FAQ

**Does the Figma MCP server work with free Figma accounts?**
Yes. The remote server at `https://mcp.figma.com/mcp` works on all Figma plans including the free Starter plan. You only need a Figma account and a personal access token with `file:read` scope. The desktop server (for selection-based context) requires a Dev or Full seat.

**What is the difference between the Figma MCP server and Figma Dev Mode?**
Figma Dev Mode is a UI layer in the Figma app that shows developers CSS, spacing, and asset specs. The MCP server is a protocol endpoint that exposes the same underlying data to AI agents programmatically. Dev Mode is for manual inspection; the MCP server is for AI-driven code generation. You can use both — Dev Mode for understanding, MCP for generating.

**Can I use the Figma MCP server without Code Connect?**
Yes, but code quality is significantly lower. Without Code Connect, the agent generates generic HTML/JSX with hardcoded values. Current data suggests 85–90% styling inaccuracy without Code Connect, meaning most AI-generated code will need substantial manual correction. If your design system is small or you're prototyping, the remote server alone may be good enough; for production use, Code Connect is worth the investment.

**How do I scope the Figma MCP context to a single frame instead of the whole file?**
Append `?node-id=FRAME_ID` to the Figma URL in your prompt. Get the exact node ID by right-clicking a frame in Figma and selecting "Copy link to selection." This dramatically reduces the token footprint of the MCP response and focuses the agent on the component you're implementing.

**Does the Figma MCP server support frameworks other than React?**
Yes. The Figma MCP server is framework-agnostic — it returns design metadata, not React code. Code Connect has official support for React, iOS (SwiftUI), and Android (Jetpack Compose), and community packages cover Vue, Angular, Svelte, and HTML/CSS. The AI agent translates the design metadata into whatever framework you specify in your prompt.