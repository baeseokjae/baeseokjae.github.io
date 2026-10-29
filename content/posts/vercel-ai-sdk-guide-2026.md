---
cover:
  alt: 'Vercel AI SDK Guide 2026: which major your snippet targets'
  image: /images/vercel-ai-sdk-guide-2026.png
  relative: false
date: 2026-04-22 05:37:21+00:00
lastmod: 2026-10-26 16:25:00+00:00
description: Version-pinned Vercel AI SDK guide for 2026 — a local TypeScript compile matrix for ai@5, ai@6 and ai@7, plus the import, useChat and step-control changes that break the April snippets.
draft: false
schema: schema-vercel-ai-sdk-guide-2026
tags:
- vercel ai sdk
- typescript
- ai development
- next.js
- streaming
- tool calling
- agents
title: 'Vercel AI SDK Guide 2026: Verified Against ai@7 — Which Major Your Snippet Targets'
---

This guide is a compatibility page, not another first-run tutorial. The npm package `ai` now ships three maintained lines — `latest` 7.0.153, `ai-v6` 6.0.315 and `ai-v5` 5.0.281, read from the registry's [dist-tags document](https://registry.npmjs.org/-/package/ai/dist-tags) on 2026-10-26 — and the code surface changed between each of them. The original April 2026 version of this page printed snippets from the 4.x era without naming a major, so a reader who follows the install line today gets major 7 and code that no longer type-checks.

Everything below was re-checked against the packages themselves. Where this page says a snippet fails, a local `tsc --noEmit` run failed; where it says a snippet type-checks, that same run exited 0. The run's exact scripts, pinned versions and raw error logs are published in the evidence directory linked with the compile matrix below.

## Which major is my snippet? The 30-second check

A snippet's major is decided by three markers, and you only need the first one to know which migration you are facing. Run `npm ls ai` in the project, or read the import path in the file.

| Marker | 3.x / 4.x (legacy) | 5.x | 6.x | 7.x |
|---|---|---|---|---|
| `useChat` import | `ai/react` | `@ai-sdk/react` | `@ai-sdk/react` | `@ai-sdk/react` |
| Step control | `maxSteps: n` | `stopWhen: stepCountIs(n)` | `stopWhen: stepCountIs(n)` | `stopWhen: isStepCount(n)` |
| System prompt | `system` | `system` | `system` | `instructions` (alias `system` still typed) |
| Module format | CJS or ESM | dual: CJS `main` + ESM `module` | dual: CJS `main` + ESM `module` | ESM only (`"type": "module"`, no `require` export) |
| Node.js floor | 18+ | 18+ | 18+ | 22+ |

Two columns deserve a warning. The 7.x column is not a blanket rename: `stepCountIs` and `system` both still type-check on 7.0.153, so a mixed codebase compiles while the migration guide tells you the new names. And the Node.js floor is an install-time fact, not a style preference — AI SDK 7.0 states that it requires Node.js 22 or later, tests on 22, 24 and 26, and no longer supports 18 or 20 ([7.0 migration guide](https://ai-sdk.dev/docs/migration-guides/migration-guide-7-0)).

## The compile matrix: what actually type-checks

Four small programs, three pinned majors, one command per file. The v5 and v6 columns used `stepCountIs`; the v7 column used `isStepCount`. Exit code 0 means `tsc --noEmit` accepted the file.

| Program | ai@5.0.281 | ai@6.0.315 | ai@7.0.153 |
|---|---|---|---|
| `streamText` + `result.textStream` | 0 | 0 | 0 |
| one tool + step-count stop condition | 0 | 0 | 0 |
| `useChat` from `@ai-sdk/react` | 0 | 0 | 0 |
| the April 2026 page's surface | 2 | 2 | 2 |

The last row is the finding. The old snippets do not partially work — they fail identically on all three maintained lines with exactly two errors, so the page you are reading could not have been salvaged by pinning to 5 or 6.

```text
legacy.tsx(2,25): error TS2307: Cannot find module 'ai/react' or its corresponding type declarations.
legacy.tsx(25,5): error TS2353: Object literal may only specify known properties,
  and 'maxSteps' does not exist in type 'CallSettings & { system?: string | undefined; ... }'
```

That second message is from the ai@5.0.281 run; on 7.0.153 the type name is `LanguageModelCallOptions` instead of `CallSettings`. The claim being checked is the same: `maxSteps` is gone, and the React hook is not reachable through `ai/react`.

Method, versions and every raw `tsc` log: [matrix.json](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/vercel-ai-sdk-guide-2026/results/matrix.json) and the [run README](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/vercel-ai-sdk-guide-2026/README.md). Node.js v24.21.0, TypeScript 5.9.3, strict mode, `skipLibCheck`, no bundler. No provider call was made — these are compile results, not model responses. The [rerun script](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/vercel-ai-sdk-guide-2026/run_matrix.sh) is self-contained: it creates its own projects under `$TMPDIR`, installs the pinned dependency sets and repeats all twelve checks in about 70 seconds, while the versions npm actually resolved — not just the ranges requested — are recorded in `results/npm-ls-v5.json`, `results/npm-ls-v6.json` and `results/npm-ls-v7.json`.

## Install that pins your major

`npm install ai` is the line that silently moves you between majors, because `latest` currently means 7.0.153. Pin the exact version and the provider adapter that matches it; the adapters moved in lockstep with the core package.

```bash
# major 7 — needs Node.js 22+
npm install ai@7.0.153 @ai-sdk/openai@4.0.102 @ai-sdk/react@4.0.157

# major 6 — ai 6.x pairs with @ai-sdk/* 3.x
npm install ai@6.0.315 @ai-sdk/openai@3.0.131 @ai-sdk/react@3.0.318

# major 5 — ai 5.x pairs with @ai-sdk/* 2.x
npm install ai@5.0.281 @ai-sdk/openai@2.0.136 @ai-sdk/react@2.0.284
```

The major-6 pairing is documented rather than guessed: the 6.0 migration guide lists `ai` at `^6.0.0`, `@ai-sdk/provider` at `^3.0.0`, `@ai-sdk/provider-utils` at `^4.0.0` and `@ai-sdk/*` at `^3.0.0` ([6.0 migration guide](https://ai-sdk.dev/docs/migration-guides/migration-guide-6-0)). The `@ai-sdk/react` versions above are the registry's matching dist-tags for those lines.

One more install-time constraint, and it is narrower than "the AI SDK is ESM now": on major 7, `ai@7.0.153` alone is ESM-only. Its package metadata declares `"type": "module"` and its `exports` map offers only `import`/`default` conditions, so a CommonJS app needs `"type": "module"` or `.mjs` files before the first import works, and the 7.0 migration guide confirms `require()` is no longer supported ([7.0 migration guide](https://ai-sdk.dev/docs/migration-guides/migration-guide-7-0), [registry metadata for ai@7.0.153](https://registry.npmjs.org/ai/7.0.153)). The same metadata, read on 2026-10-26, shows 5.x and 6.x were never ESM-only: `ai@5.0.281` and `ai@6.0.315` both declare `"main": "./dist/index.js"` alongside `"module": "./dist/index.mjs"` and an `exports` map with separate `import` and `require` conditions, so `require('ai')` resolves to the CommonJS build on those lines ([registry metadata for ai@6.0.315](https://registry.npmjs.org/ai/6.0.315)). If a CommonJS service is stuck on 6.x, that dual build is why nothing breaks until the upgrade crosses into 7.

## Streaming a response on each major

The streaming call itself is the most stable surface in the matrix — `streamText` with a model and a prompt type-checks on 5, 6 and 7 — but the option names around it are not. This is the v7 form:

```typescript
import { streamText } from 'ai';
import { openai } from '@ai-sdk/openai';

const result = streamText({
  model: openai('gpt-4o-mini'),
  instructions: 'Answer in one sentence.',   // 7.x name; 'system' still compiles
  prompt: 'Why is the sky blue?',
  onEnd: ({ text }) => {                     // 7.x name for onFinish
    console.log('done', text.length);
  },
});

for await (const delta of result.textStream) {
  process.stdout.write(delta);
}
```

On 5.x and 6.x the same file compiles after swapping `instructions` back to `system` and `onEnd` back to `onFinish`. The rename set is listed in the 7.0 migration guide's codemod table, which pairs each old name with its replacement: `rename-system-to-instructions`, `rename-on-finish-to-on-end`, `rename-on-step-finish-to-on-step-end`, `rename-experimental-on-start-to-on-start` ([7.0 migration guide](https://ai-sdk.dev/docs/migration-guides/migration-guide-7-0)). The codemod table proves a rename exists; it does not prove the old name throws, and on 7.0.153 it does not: the probe `streamText({ system: 'terse' })` exits 0.

## Tool loops: `maxSteps` → `stopWhen` → `isStepCount`

Multi-step tool calling is where the April snippets fail hardest, because `maxSteps` was removed in 5.0 and never came back. From AI SDK 5.0, the core functions take `stopWhen`, a condition evaluated after a step that produced tool results, and an array of conditions stops on any match ([5.0 migration guide](https://ai-sdk.dev/docs/migration-guides/migration-guide-5-0)).

```typescript
// 5.x and 6.x
import { generateText, stepCountIs, tool } from 'ai';
import { openai } from '@ai-sdk/openai';
import { z } from 'zod';

const result = await generateText({
  model: openai('gpt-4o-mini'),
  prompt: 'What is the temperature in Seoul?',
  tools: {
    weather: tool({
      description: 'Return the current temperature for a city',
      inputSchema: z.object({ city: z.string() }),
      execute: async ({ city }) => ({ city, tempC: 21 }),
    }),
  },
  stopWhen: stepCountIs(3),
});
```

```typescript
// 7.x — same file, one import name and one option value change
import { generateText, isStepCount, tool } from 'ai';
// ...
  stopWhen: isStepCount(3),
```

That pair is verified in both directions rather than copied from a table: `stepCountIs` compiles on 6.0.315 and on 7.0.153, while `isStepCount` compiles on 7.0.153 and fails on 6.0.315 with `TS2724: '"ai"' has no exported member named 'isStepCount'. Did you mean 'stepCountIs'?`. So if you are writing new code for a codebase you cannot upgrade yet, `stepCountIs` is the portable spelling and `isStepCount` is the 7-only one.

## Chat UI: the hook moved packages, then changed shape

The `useChat` hook moved out of `ai/react` and, in the same 5.0 release, stopped managing input state for you: it is transport-based, with a default `DefaultChatTransport` pointed at `/api/chat`, and you send messages explicitly instead of wiring `input` and `handleSubmit` ([useChat reference](https://ai-sdk.dev/docs/reference/ai-sdk-ui/use-chat)).

```tsx
'use client';
import { useChat } from '@ai-sdk/react';

export function Chat() {
  const { messages, sendMessage, status } = useChat();

  return (
    <div>
      {messages.map((m) => <p key={m.id}>{m.id}</p>)}
      <span>{status}</span>
      <button onClick={() => sendMessage({ text: 'Hello' })}>Send</button>
    </div>
  );
}
```

This exact file type-checks against all three majors in the matrix — `@ai-sdk/react` 2.0.284, 3.0.318 and 4.0.157 — which makes it the safest starting point when you do not yet know which major a project is on. The import paths per framework are documented alongside it: `@ai-sdk/react`, `@ai-sdk/svelte`, `@ai-sdk/vue` and `@ai-sdk/angular`, with `Chat` rather than `useChat` on Svelte and Angular.

## Migrating one major at a time

Do not jump 4.x to 7.x in one edit. The vendor ships codemods per major, and the 6.0 guide is explicit about the scope of each: `npx @ai-sdk/codemod v6` runs the v5 → v6 set, while `npx @ai-sdk/codemod upgrade` runs every codemod from v4, v5 and v6 — the difference matters because the broad command will rewrite code you have not reviewed yet ([6.0 migration guide](https://ai-sdk.dev/docs/migration-guides/migration-guide-6-0)). One major per commit, with `npm ls ai` and the two failing markers above as the check after each step.

The 6.0 guide also records a behavioural change that no compiler will catch for you: `convertToModelMessages` became async in 6.0 (the codemod is `add-await-converttomodelmessages`), so a v5 call site needs `await` even where the type inference happens to stay quiet.

## Dated adoption numbers, not undated ones

The previous version of this page cited 11.5 million weekly npm downloads and 23.7K GitHub stars "as of April 2026". The star figure has a verifiable replacement: the [GitHub REST API for vercel/ai](https://api.github.com/repos/vercel/ai) returned 27,523 stars on 2026-10-26. The weekly-download figure is not repeated here because it was not re-read from the npm downloads API in this refresh, and a number a reader cannot check is worse than no number. Stars are a point-in-time counter, not an adoption claim.

For the same reason there is no benchmark section: nothing in this refresh measured latency, token throughput or cost per request, so nothing here should be read as a performance comparison.

## What to read next

This page owns one question — which major a snippet targets and what changed between majors. For choosing between SDKs rather than versions, the site's existing comparisons cover that ground: [AI Agents SDK Comparison 2026](https://baeseokjae.github.io/posts/ai-agents-sdk-comparison-2026/), the [OpenAI Agents SDK v2 guide](https://baeseokjae.github.io/posts/openai-agents-sdk-v2-guide-2026/) and [Mastra AI Guide 2026](https://baeseokjae.github.io/posts/mastra-ai-guide-2026/). If you only need function-calling mechanics without the version history, the [LLM function calling guide](https://baeseokjae.github.io/posts/llm-function-calling-tool-use-guide-2026/) is the shorter path.

The version table above will go stale on its own schedule. The cheapest maintenance check is the one this refresh used: read the registry dist-tags, install the new patch of each maintained line into a scratch directory, and re-run the four-program matrix. If two consecutive releases leave the table wrong, the page should be treated as a compatibility reference rather than a tutorial to keep extending.
