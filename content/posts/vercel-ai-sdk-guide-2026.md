---
title: "Vercel AI SDK Guide 2026: Build Streaming AI Apps in TypeScript With One SDK"
date: 2026-04-22T05:37:21+00:00
tags: ["vercel ai sdk", "typescript", "ai development", "next.js", "streaming", "tool calling", "agents"]
description: "Complete guide to Vercel AI SDK in 2026 — streaming, tool calling, structured output, agents, and production deployment with code examples."
draft: false
cover:
  image: "/images/vercel-ai-sdk-guide-2026.png"
  alt: "Vercel AI SDK Guide 2026: Build Streaming AI Apps in TypeScript With One SDK"
  relative: false
schema: "schema-vercel-ai-sdk-guide-2026"
---

The Vercel AI SDK is a unified TypeScript library that lets you build streaming AI applications across OpenAI, Anthropic, Google, and 13+ other providers without rewriting your core logic when you switch models. Install it once, pick your provider, and ship production-ready AI features in hours instead of days.

## What Is the Vercel AI SDK and Why It Matters in 2026

The Vercel AI SDK is an open-source TypeScript toolkit for building AI-powered web applications with a provider-agnostic API, first-class streaming support, and framework-native UI hooks. As of April 2026, it has 11.5 million weekly npm downloads, 23.7K GitHub stars, and 614+ contributors — making it the most widely adopted TypeScript AI library for web developers. The SDK is organized into three layers: AI SDK Core handles server-side text generation, object generation, and tool calling; AI SDK UI provides React/Vue/Svelte hooks like `useChat` and `useCompletion` for building chat interfaces without managing stream state; and AI SDK RSC integrates with React Server Components for edge-compatible generative UI. The SDK supports 100+ LLM models across 16+ providers via the Vercel AI Gateway, including OpenAI GPT-4o, Anthropic Claude, Google Gemini, and open models on Together/Groq. In 2026 Vercel added three major features on top: Workflows (long-running durable agents), Sandbox (secure agent code execution), and AI Elements (prebuilt UI components). OpenCode — one of the most popular open-source coding agents — is built entirely on AI SDK, which validates its production-grade viability.

### The Three-Layer Architecture

The SDK cleanly separates concerns: Core runs on the server or edge, UI runs on the client, and RSC bridges the two with streaming server components. This separation means you can adopt incrementally — start with Core for a simple API route, add UI hooks when you need chat state management, and layer in RSC if you need server-driven generative UI.

### How It Fits the Vercel Ecosystem

AI Gateway gives you one API key to access 100+ models with automatic fallbacks and rate limit management. Sandbox provides a secure Node.js environment for agents that need to execute code. Workflows lets agents suspend and resume across function invocations, solving the serverless timeout problem for long-running tasks.

## Getting Started: Installing and Configuring AI SDK

Getting started with the Vercel AI SDK requires installing the `ai` core package plus one or more provider adapters. The setup takes under five minutes for a Next.js project and works equally well in any Node.js or edge runtime environment. The provider adapter pattern is the key architectural decision: you import a model from its provider package and pass it to AI SDK functions, meaning you can swap from OpenAI to Anthropic by changing a single import and model string — your business logic stays untouched. This design was explicitly chosen to prevent vendor lock-in, and in practice it means you can A/B test models in production, build fallback chains, or migrate providers without refactoring your entire codebase. The package size is small — `ai` is under 200KB minified — and it is designed to run on Vercel Edge Functions, Cloudflare Workers, and standard Node.js without adaptation. For new projects, the recommended starting point is a Next.js App Router app with the `edge` runtime on API routes, which gives you global distribution and sub-100ms cold starts.

```bash
npm install ai @ai-sdk/openai @ai-sdk/anthropic @ai-sdk/google
```

```typescript
// .env.local
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_GENERATIVE_AI_API_KEY=...
```

```typescript
// app/api/chat/route.ts
import { streamText } from 'ai'
import { openai } from '@ai-sdk/openai'

export const runtime = 'edge'

export async function POST(req: Request) {
  const { messages } = await req.json()
  
  const result = streamText({
    model: openai('gpt-4o'),
    messages,
  })
  
  return result.toDataStreamResponse()
}
```

### AI Gateway: One Key for 100+ Models

Vercel AI Gateway lets you use a single `VERCEL_API_KEY` to access models from OpenAI, Anthropic, Google, Mistral, and more. It handles rate limit rotation, cost tracking, and automatic retry logic. For teams that need to experiment with multiple providers without managing individual API key billing, Gateway is the fastest path to a multi-model setup.

## AI SDK Core: Text Generation and Streaming

AI SDK Core is the server-side engine that converts provider-specific APIs into a consistent interface for generating text, streaming responses, and calling tools. The two primary functions are `generateText` and `streamText`. `generateText` is for synchronous operations — you send a prompt and wait for the full response, which is ideal for batch jobs, summarization pipelines, and any context where the user is not watching a UI render in real time. `streamText` is the streaming counterpart: it returns a `ReadableStream` that you can pipe directly to a `Response` object, and it integrates with UI hooks via the `toDataStreamResponse()` method. Both functions accept the same options object — `model`, `messages`, `system`, `tools`, `maxSteps`, `temperature`, and more — so switching between them is a one-word change. Provider switching is similarly simple: swapping `openai('gpt-4o')` for `anthropic('claude-opus-4-7')` is the only change needed. Retry logic and fallbacks are handled with the `wrapLanguageModel` utility and the `fallback` provider, which tries a list of models in order if the primary returns an error. The consistency across providers is the single biggest productivity gain AI SDK offers compared to using provider SDKs directly.

```typescript
import { generateText, streamText } from 'ai'
import { anthropic } from '@ai-sdk/anthropic'

// One-shot generation
const { text } = await generateText({
  model: anthropic('claude-sonnet-4-6'),
  prompt: 'Summarize the key features of React 19 in 3 bullet points.',
})

// Streaming
const result = streamText({
  model: anthropic('claude-sonnet-4-6'),
  prompt: 'Write a guide on async/await in TypeScript.',
})

for await (const chunk of result.textStream) {
  process.stdout.write(chunk)
}
```

### Built-In Fallbacks and Retry Logic

```typescript
import { createFallback } from '@ai-sdk/provider-utils'
import { openai } from '@ai-sdk/openai'
import { anthropic } from '@ai-sdk/anthropic'

const resilientModel = createFallback([
  openai('gpt-4o'),
  anthropic('claude-sonnet-4-6'),
])
```

## Structured Output with Zod Schemas

`generateObject` and `streamObject` are AI SDK's solution to one of the biggest pain points in production AI: getting reliable, type-safe structured data from LLMs instead of freeform text that you then parse with fragile regexes. These functions accept a Zod schema and use the model's native structured output mode — JSON mode for OpenAI, tool-use-based extraction for Anthropic — to guarantee the response matches the schema shape. If the model returns malformed output, AI SDK retries automatically. This is not just a developer convenience: structured output is essential for any AI pipeline where the response feeds into downstream logic, databases, or APIs. Teams using `generateObject` in production report near-zero JSON parsing errors compared to prompt-based extraction, and the Zod types flow through the entire TypeScript type system so you get autocomplete on the AI response object. The `streamObject` variant lets you stream partial structured objects, enabling progressive UI rendering as the AI fills in fields — useful for forms, dashboards, or any interface where showing partial data is better than a blank loading state. For data extraction tasks — pulling product specs from HTML, extracting entities from documents, or parsing unstructured API responses — structured output with Zod is the recommended production approach.

```typescript
import { generateObject, streamObject } from 'ai'
import { openai } from '@ai-sdk/openai'
import { z } from 'zod'

const BlogPostSchema = z.object({
  title: z.string(),
  summary: z.string().max(200),
  tags: z.array(z.string()).max(5),
  seoScore: z.number().min(0).max(100),
  sections: z.array(z.object({
    heading: z.string(),
    keyPoints: z.array(z.string()),
  })),
})

const { object } = await generateObject({
  model: openai('gpt-4o'),
  schema: BlogPostSchema,
  prompt: 'Analyze this article and return structured metadata: ...',
})

console.log(object.title) // TypeScript knows the full type
```

### Streaming Structured Objects

```typescript
const { partialObjectStream } = streamObject({
  model: openai('gpt-4o'),
  schema: BlogPostSchema,
  prompt: 'Generate a blog post outline for: "AI agents in 2026"',
})

for await (const partial of partialObjectStream) {
  // partial.title appears as soon as the model generates it
  updateUI(partial)
}
```

## Building Chat UIs with AI SDK UI Hooks

AI SDK UI is the client-side complement to Core, providing React hooks that manage chat state, streaming responses, and optimistic updates without requiring a single `useState` or `useEffect` for stream handling. The primary hook is `useChat`, which gives you `messages`, `input`, `handleInputChange`, `handleSubmit`, and `isLoading` — everything needed to build a ChatGPT-like interface in under 50 lines of React. Under the hood it connects to your AI route, handles stream parsing, and appends message chunks to state as they arrive. The `useCompletion` hook handles text completion use cases — autocomplete, writing suggestions, or any single-prompt UX. `useObject` streams structured objects from a `streamObject` route and exposes the partial object as it builds, enabling progressive form filling or AI-driven dashboard updates. All three hooks work with React, Vue, Svelte, and SolidJS — the framework-agnostic design means you can share backend patterns between projects built on different frontend stacks. The hooks integrate with React Suspense and Error Boundaries for graceful loading and error states without extra wiring.

```typescript
// app/components/Chat.tsx
'use client'
import { useChat } from 'ai/react'

export function Chat() {
  const { messages, input, handleInputChange, handleSubmit, isLoading } = useChat({
    api: '/api/chat',
  })

  return (
    <div>
      {messages.map(m => (
        <div key={m.id} className={m.role === 'user' ? 'user' : 'assistant'}>
          {m.content}
        </div>
      ))}
      <form onSubmit={handleSubmit}>
        <input value={input} onChange={handleInputChange} disabled={isLoading} />
        <button type="submit" disabled={isLoading}>Send</button>
      </form>
    </div>
  )
}
```

### Framework Support Comparison

| Hook | React | Vue | Svelte | SolidJS |
|------|-------|-----|--------|---------|
| `useChat` | ✅ | ✅ | ✅ | ✅ |
| `useCompletion` | ✅ | ✅ | ✅ | ✅ |
| `useObject` | ✅ | ✅ | ✅ | ✅ |
| `useAssistant` | ✅ | ❌ | ❌ | ❌ |

## Tool Calling: Giving Your AI Agent Superpowers

Tool calling in AI SDK is the mechanism that transforms a passive text generator into an active agent — the model describes which tools it wants to invoke, AI SDK executes them server-side, and the results feed back into the next model turn automatically. Tools are defined with the `tool` helper, which takes a `description` (natural language explanation for the model), `parameters` (a Zod schema for typed inputs), and an `execute` function (the actual implementation). The SDK handles the full tool-call cycle: formatting the tool description for the provider, parsing the model's structured tool-call output, executing the function with validated arguments, and appending the result to the conversation context. `maxSteps` controls how many tool-call cycles the agent can run before stopping, preventing infinite loops while allowing multi-step reasoning chains of 5–10 steps. Tool results stream to the client via `toDataStreamResponse()`, so users see intermediate tool outputs in real time rather than waiting for the final answer. In production applications, tool sets commonly include database query tools, web search, calculator functions, external API calls, and file operations — anything your server-side code can do, the agent can orchestrate. The Zod parameter schemas provide input validation at zero extra cost, catching malformed tool calls before they reach your database or external services.

```typescript
import { streamText, tool } from 'ai'
import { openai } from '@ai-sdk/openai'
import { z } from 'zod'

const result = streamText({
  model: openai('gpt-4o'),
  maxSteps: 5,
  tools: {
    getWeather: tool({
      description: 'Get current weather for a city',
      parameters: z.object({ city: z.string() }),
      execute: async ({ city }) => {
        const res = await fetch(`https://api.weather.com/${city}`)
        return res.json()
      },
    }),
    searchDatabase: tool({
      description: 'Search the product database',
      parameters: z.object({ query: z.string(), limit: z.number().default(5) }),
      execute: async ({ query, limit }) => {
        return db.products.search(query, { limit })
      },
    }),
  },
  messages: [{ role: 'user', content: 'What is the weather in Tokyo and do we sell umbrellas?' }],
})

return result.toDataStreamResponse()
```

### Multi-Step Agent Loop

With `maxSteps: 5`, the model can: call `getWeather` → get Tokyo weather → call `searchDatabase` for umbrellas → combine results → return final answer. Each step is visible to the user via streaming tool call indicators rendered automatically by `useChat`.

## Building AI Agents with Multi-Step Reasoning

An AI agent in the Vercel AI SDK context is a `streamText` or `generateText` call with tools enabled and `maxSteps` set above 1 — the model reasons, calls tools, observes results, and reasons again until it reaches a conclusion or exhausts its step budget. This loop pattern is what separates agents from chatbots: rather than answering from static training knowledge, the agent actively queries databases, fetches URLs, or calls APIs to gather real-time information before formulating a response. The key to a production-grade agent is memory and context management: you control what goes in `messages`, so you can implement sliding window context, summarization, or retrieval-augmented generation by fetching relevant documents before calling the model. For RAG integration, the standard pattern is to embed the user query, retrieve top-k chunks from a vector store (Pinecone, Supabase pgvector, or Upstash), and prepend them as a system message. The agent then has access to both retrieved context and its tool-calling ability, so it can fetch additional information if the retrieved chunks are insufficient. OpenCode's architecture demonstrates this at scale: it uses AI SDK with file system tools, runs multi-step reasoning loops to understand a codebase, and streams results back to a terminal UI — all without custom streaming infrastructure because AI SDK handles it.

```typescript
// Research agent with RAG
async function researchAgent(query: string) {
  const relevantDocs = await vectorStore.search(query, { topK: 5 })
  
  const result = streamText({
    model: openai('gpt-4o'),
    maxSteps: 8,
    system: `You are a research agent. Use context and tools to answer thoroughly.
    
Context from knowledge base:
${relevantDocs.map(d => d.content).join('\n\n')}`,
    messages: [{ role: 'user', content: query }],
    tools: {
      searchWeb: tool({ /* web search implementation */ }),
      fetchUrl: tool({ /* URL fetching implementation */ }),
      saveNote: tool({ /* note saving implementation */ }),
    },
  })
  
  return result.toDataStreamResponse()
}
```

## Vercel Workflows: Long-Running Agents That Survive

Vercel Workflows is a 2026 addition to the AI SDK ecosystem that solves the most critical limitation of serverless AI agents: function timeout. Standard serverless functions on Vercel time out after 30 seconds (Pro plan) or 5 minutes (Enterprise), which is insufficient for agents that need to search the web, process large documents, run multi-stage pipelines, or wait for human approval. Workflows introduces durable execution — agent tasks are broken into named steps that can suspend (persist state to managed storage), wait for external events, and resume exactly where they left off across multiple function invocations without losing context. This makes genuinely complex agentic pipelines feasible on serverless infrastructure: a content generation pipeline can run for 20+ minutes as it researches, drafts, and revises content, with the agent suspending between phases. The `@vercel/workflows` package integrates directly with AI SDK's `generateText` and `streamText` — you wrap agent logic in a `workflow` function and use `step.run()` to define resumable checkpoints. Human-in-the-loop approval is supported via `step.waitForEvent()`, which suspends the workflow until a webhook fires. In 2026, Workflows is the recommended architecture for any AI task that may exceed 30 seconds or requires coordination between multiple agents.

```typescript
import { workflow, step } from '@vercel/workflows'
import { generateText } from 'ai'
import { anthropic } from '@ai-sdk/anthropic'

export const contentPipeline = workflow(async ({ input }: { input: { topic: string } }) => {
  // Each step is resumable — survives function timeout
  const research = await step.run('research', async () => {
    const { text } = await generateText({
      model: anthropic('claude-opus-4-7'),
      prompt: `Research: ${input.topic}. Return key facts and sources.`,
    })
    return text
  })

  const draft = await step.run('draft', async () => {
    const { text } = await generateText({
      model: anthropic('claude-sonnet-4-6'),
      prompt: `Using this research: ${research}\n\nWrite a 1000-word article about ${input.topic}.`,
    })
    return text
  })

  return { research, draft }
})
```

## Production Deployment and Scaling

Deploying a Vercel AI SDK application to production requires careful attention to runtime selection, cost management, and observability. For runtime selection, Edge Functions are the right choice for streaming chat routes because they have lower cold-start latency and are globally distributed across 30+ regions — users in Tokyo get a fast response without routing to a US datacenter. Node.js runtime is better for heavy tool execution, large file processing, or anything requiring Node-specific APIs. Cost management starts with the `maxTokens` parameter to cap spending per request, and AI Gateway adds team-level spend limits and per-model cost tracking with dashboards. For rate limiting on API routes, `@vercel/kv` with a sliding window counter is the standard pattern: each user or IP gets N requests per minute, excess requests return 429 with a `retry-after` header. Observability is critical for catching silent model failures: the `onFinish` callback in `streamText` and `generateText` lets you log token usage, model name, latency, and finish reason to your analytics pipeline, enabling cost attribution per feature and alerting on abnormal token consumption. Vercel's built-in function logs surface AI SDK error events automatically for debugging.

```typescript
export async function POST(req: Request) {
  const { messages } = await req.json()
  
  // Rate limiting check
  const ip = req.headers.get('x-forwarded-for') ?? 'anonymous'
  const { success } = await ratelimit.limit(ip)
  if (!success) return new Response('Rate limit exceeded', { status: 429 })

  const result = streamText({
    model: openai('gpt-4o'),
    messages,
    maxTokens: 2000,
    temperature: 0.7,
    onFinish: ({ usage, finishReason }) => {
      analytics.track('ai_completion', {
        tokens: usage.totalTokens,
        finishReason,
        model: 'gpt-4o',
      })
    },
  })
  
  return result.toDataStreamResponse()
}
```

## AI SDK vs LangChain vs Mastra: Framework Comparison

Choosing between Vercel AI SDK, LangChain.js, and Mastra in 2026 depends primarily on your stack, agent complexity, and how important streaming and bundle size are to your application. Vercel AI SDK is the right choice for TypeScript web developers building streaming-first applications — it is the lightest of the three (under 200KB), has the best Next.js and Edge Function integration, and provides the most seamless streaming API with minimal boilerplate. LangChain.js has the broadest ecosystem: pre-built chains, 50+ vector store integrations, document loaders, memory modules, and a large community cookbook — making it better for teams needing to quickly assemble complex RAG pipelines from components rather than writing integration code themselves. Mastra, which emerged in late 2025, sits between the two: TypeScript-native like AI SDK but with an opinionated agent framework including built-in memory, durable workflow primitives, and multi-agent coordination, targeting developers who need more structure than AI SDK provides without LangChain's abstraction overhead. The bundle size difference is meaningful for edge and browser deployments where LangChain.js's 2MB+ footprint can impact cold start times. For most Next.js applications in 2026, AI SDK is the practical default and LangChain or Mastra are reached for only when specific missing features justify the additional complexity.

| Feature | Vercel AI SDK | LangChain.js | Mastra |
|---------|--------------|-------------|--------|
| Bundle size | ~200KB | ~2MB+ | ~500KB |
| Streaming | First-class | Good | Good |
| Tool calling | Native | Via chains | Native |
| Structured output | Zod-native | Manual | Zod-native |
| Long-running agents | Via Workflows | Partial | Built-in |
| Next.js/Edge | Excellent | Moderate | Good |
| Pre-built integrations | 16+ providers | 50+ | 20+ |
| TypeScript types | Excellent | Good | Excellent |
| Learning curve | Low | High | Medium |

## FAQ

**What is the difference between AI SDK Core and AI SDK UI?**
AI SDK Core (`generateText`, `streamText`, `generateObject`) runs on the server and handles model calls. AI SDK UI (`useChat`, `useCompletion`, `useObject`) runs on the client and manages stream state, message history, and UI updates. In a Next.js app, Core lives in `app/api/` routes and UI hooks live in client components. You can use Core without UI (for backend pipelines) but UI requires a Core-powered API endpoint.

**Can I use Vercel AI SDK without Vercel hosting?**
Yes. The AI SDK is a pure npm package with no dependency on Vercel's infrastructure. You can use it in any Node.js server, AWS Lambda, Cloudflare Workers, or on-premise environment. Vercel-specific features like Workflows and AI Gateway require Vercel hosting, but AI SDK Core and UI work on any JavaScript runtime.

**How do I switch between AI providers in Vercel AI SDK?**
Change one line: swap the model import and the model string. Replace `openai('gpt-4o')` with `anthropic('claude-sonnet-4-6')`. The rest of your code — messages, tools, streaming — stays identical. This is the main design goal: provider portability without refactoring business logic.

**What is the recommended way to add memory to an AI SDK agent?**
The SDK does not manage memory itself — you control `messages`. Store conversation history in a database (KV, Postgres, or Upstash), retrieve the last N turns before each request, and pass them as `messages`. For long-term memory across sessions, embed user facts and retrieve them via vector search, prepending relevant memories to the system prompt before each request.

**Does Vercel AI SDK support multi-modal inputs like images and PDFs?**
Yes. Models that support vision (GPT-4o, Claude Opus 4, Gemini Pro Vision) accept `content` arrays with `{ type: 'image', image: url }` or `{ type: 'file', data: base64, mimeType: 'application/pdf' }` parts alongside text. AI SDK normalizes these into the provider's expected format automatically, so you write the same code regardless of which vision model you use.
