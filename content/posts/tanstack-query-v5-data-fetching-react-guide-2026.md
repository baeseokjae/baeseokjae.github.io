---
title: "TanStack Query v5: Data Fetching and Caching for AI-Powered React Apps"
date: 2026-06-02T06:04:31+00:00
tags: ["TanStack Query", "React", "Data Fetching", "AI Apps", "Caching", "Next.js"]
description: "TanStack Query v5 guide for AI-powered React apps: streamedQuery, optimistic updates, cross-tab sync, SSR, and production patterns."
draft: false
cover:
  image: "/images/tanstack-query-v5-data-fetching-react-guide-2026.png"
  alt: "TanStack Query v5: Data Fetching and Caching for AI-Powered React Apps"
  relative: false
schema: "schema-tanstack-query-v5-data-fetching-react-guide-2026"
---

TanStack Query v5 is the server state library for React that handles caching, background refetching, and stale-while-revalidate out of the box — with 12M+ weekly downloads in 2026, it's become the default choice for teams building AI-powered applications that need real-time data and LLM streaming.

## Why TanStack Query v5 Is the Default Choice for AI-Powered React Apps in 2026

TanStack Query v5 (formerly React Query) is a server state management library that handles all the complexity between your React components and your data sources — caching, deduplication, background synchronization, loading states, and error recovery — with minimal configuration. As of June 2026, the library ships at version 5.100.14, has 48K+ GitHub stars (overtaking SWR's 32K in 2024), and sits at 12.3M weekly npm downloads — a 2.5x lead over SWR's 4.9M. That adoption reflects a real shift: AI-powered React apps need capabilities beyond simple data fetching. LLM responses stream over seconds, not milliseconds. Dashboards pull from three or more data sources simultaneously. Users open the same AI tool across five browser tabs. TanStack Query v5's new `streamedQuery`, `broadcastQueryClient`, and deep Suspense integration address these patterns directly, which is why teams building AI chatbots, real-time dashboards, and LLM-augmented features in 2026 are reaching for it first.

### What Changed from v4 to v5?

V5 introduced several breaking changes that matter for AI apps. The `useQuery` callback options `onSuccess`, `onError`, and `onSettled` were removed from the query level (they now live only on mutations). The `cacheTime` option was renamed to `gcTime` (garbage collection time) for clarity. Suspense queries got their own dedicated hooks: `useSuspenseQuery`, `useSuspenseInfiniteQuery`, and `useSuspenseQueries`. Most significantly, the experimental `streamedQuery` helper was added — purpose-built for consuming AsyncIterables from LLM APIs. If you're migrating from v4, budget time for these API changes.

## Core Concepts Every AI Developer Needs to Understand (Queries, Mutations, Cache)

TanStack Query separates server state into two primitives: queries (reads that can be cached, deduplicated, and refetched) and mutations (writes that trigger side effects). The cache sits between your components and your server, keyed by arrays you control. A query result with `staleTime: 30_000` stays fresh for 30 seconds — any component mounting during that window gets the cached value instantly without a network request. After stale, the cache serves the old data immediately while refetching in the background — the stale-while-revalidate pattern that makes AI dashboards feel fast. The `gcTime` (default: 5 minutes) controls how long inactive cache entries survive before garbage collection. For AI apps, these two numbers are your primary performance levers: high `staleTime` for expensive LLM-generated content that doesn't change often, low `staleTime` (or zero) for real-time data like chat histories. Understanding the lifecycle — fresh → stale → inactive → garbage collected — is the prerequisite to every other pattern in this guide.

### Query Keys: The Foundation of Everything

Query keys are arrays that uniquely identify each piece of cached data. The key `['users', userId]` caches per-user data separately from `['users', 'list']`. For AI apps, keys like `['chat', sessionId, 'messages']` let you invalidate a specific conversation's cache when a new LLM response arrives. Every cache operation — `invalidateQueries`, `setQueryData`, `prefetchQuery` — targets keys. Get key design right early; it determines how cleanly you can invalidate cache when AI state changes.

## Setting Up TanStack Query v5 in a Next.js or Vite React Project

Setting up TanStack Query v5 requires installing `@tanstack/react-query` and wrapping your app in `QueryClientProvider`. The setup is nearly identical across Vite and Next.js App Router, with one difference: in Next.js App Router you must instantiate `QueryClient` inside a `'use client'` component to avoid sharing state between server requests. Install the package with `npm install @tanstack/react-query`, and optionally install `@tanstack/react-query-devtools` for the browser devtools overlay. The DevTools are indispensable for AI apps — they show cache state, query status, and stale timing in real time, which is exactly what you need when debugging why an LLM response isn't refetching when expected. Version 5.100.14 ships with full TypeScript support and no additional type packages needed.

```tsx
// app/providers.tsx — Next.js App Router
'use client'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'
import { useState } from 'react'

export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(() => new QueryClient({
    defaultOptions: {
      queries: {
        staleTime: 60 * 1000, // 1 minute default
        gcTime: 5 * 60 * 1000, // 5 minutes garbage collection
      },
    },
  }))

  return (
    <QueryClientProvider client={queryClient}>
      {children}
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  )
}
```

Wrap `layout.tsx` with `<Providers>` and every Server Component route automatically gets access to the client-side cache in child Client Components.

## Streaming AI Responses with streamedQuery — The LLM-Native Approach

`streamedQuery` is TanStack Query v5's experimental answer to the LLM streaming problem. It wraps a function that returns an `AsyncIterable` and progressively updates the query cache as each chunk arrives, triggering React re-renders on every chunk without any manual state management. Before `streamedQuery`, teams wired up custom `useEffect` hooks, manually maintained partial-response state, and wrote cleanup logic for aborted streams — hundreds of lines of boilerplate per feature. With `streamedQuery`, the pattern collapses to a single hook call. The helper is stable enough for production use in 2026 (multiple large AI apps ship it), though the API carries the "experimental" label and could change between minor versions. For apps using the Vercel AI SDK, `streamedQuery` pairs naturally with `streamText` responses: the Vercel SDK yields an `AsyncIterable` that `streamedQuery` consumes directly, with automatic cache entry creation and incremental updates as tokens arrive.

```tsx
import { streamedQuery, useQuery } from '@tanstack/react-query'

const aiQueryOptions = (prompt: string) => ({
  queryKey: ['ai-response', prompt],
  queryFn: streamedQuery({
    queryFn: async ({ signal }) => {
      const response = await fetch('/api/chat', {
        method: 'POST',
        body: JSON.stringify({ prompt }),
        signal,
      })
      return response.body // ReadableStream → AsyncIterable via browser APIs
    },
  }),
  staleTime: Infinity, // LLM responses don't go stale
})

function AIResponse({ prompt }: { prompt: string }) {
  const { data, isLoading } = useQuery(aiQueryOptions(prompt))

  if (isLoading) return <span>Thinking...</span>
  return <div>{data?.join('')}</div> // data is string[] of chunks
}
```

The `signal` parameter wires abort automatically — navigating away cancels the in-flight LLM request. Set `staleTime: Infinity` for LLM responses: they don't change after generation, and you want them cached for the session.

## Optimistic Updates for AI Chatbot UX: Show Messages Before Server Confirms

Optimistic updates are the technique of immediately updating the UI as if a mutation succeeded, then rolling back if the server returns an error. For AI chatbots, this is essential: users expect to see their message appear in the chat instantly when they press Send, not after the LLM API round-trip completes. TanStack Query's mutation lifecycle — `onMutate`, `onError`, `onSettled` — gives you exact hooks for this pattern. In `onMutate`, you snapshot the current cache and inject the optimistic message. In `onError`, you restore the snapshot. In `onSettled`, you invalidate the query to fetch the real server state. This three-step pattern handles the edge case of out-of-order responses (two messages sent fast) and ensures the UI never gets permanently stuck in an optimistic state. Teams building production AI chatbots like internal Slack-style tools report 40–60% improvement in perceived responsiveness with this pattern, purely from eliminating the submit-to-appear delay.

```tsx
const sendMessage = useMutation({
  mutationFn: (message: string) => 
    fetch('/api/chat', { method: 'POST', body: JSON.stringify({ message }) }),
  
  onMutate: async (newMessage) => {
    await queryClient.cancelQueries({ queryKey: ['messages', sessionId] })
    const previous = queryClient.getQueryData(['messages', sessionId])
    
    queryClient.setQueryData(['messages', sessionId], (old: Message[]) => [
      ...old,
      { id: 'temp', content: newMessage, role: 'user', pending: true }
    ])
    
    return { previous }
  },
  
  onError: (err, vars, context) => {
    queryClient.setQueryData(['messages', sessionId], context?.previous)
  },
  
  onSettled: () => {
    queryClient.invalidateQueries({ queryKey: ['messages', sessionId] })
  },
})
```

## Cross-Tab AI State Sync with broadcastQueryClient (Experimental)

`broadcastQueryClient` is an experimental TanStack Query plugin that synchronizes cache state across browser tabs using the native Broadcast Channel API. When a user has your AI app open in three tabs and completes an action in one — uploading a document, finishing a chat session, updating AI settings — `broadcastQueryClient` propagates the cache invalidation to the other tabs automatically. Without it, the other tabs show stale data until the user manually refreshes. The plugin is plug-and-play: install `@tanstack/query-broadcast-client-experimental`, wrap your `QueryClient`, and cross-tab sync works automatically for all queries. The Broadcast Channel API is supported in all modern browsers and requires no server-side infrastructure — it operates entirely client-side through shared memory channels. For AI apps where users frequently compare outputs across tabs (a common pattern with LLM tools), this prevents the confusing UX of seeing different AI responses for the same prompt across windows.

```tsx
import { broadcastQueryClient } from '@tanstack/query-broadcast-client-experimental'

const queryClient = new QueryClient()

broadcastQueryClient({
  queryClient,
  broadcastChannel: 'my-ai-app', // unique channel name per app
})
```

Install the experimental package separately: `npm install @tanstack/query-broadcast-client-experimental`. The API is stable enough for production but may have breaking changes between minor v5 releases.

## Server-Side Rendering and Suspense Streaming for AI Applications

TanStack Query v5's SSR story uses `HydrationBoundary` to transfer prefetched server data to the client without a second network round-trip. In Next.js App Router, you prefetch queries in Server Components using `queryClient.prefetchQuery`, serialize the cache state with `dehydrate`, and pass it to `HydrationBoundary` in the client component tree. The client hydrates instantly from the dehydrated state — no loading flash on first render. For AI apps, this means an AI-generated summary, recommendation, or search result rendered on the server shows up immediately on the client without re-fetching. Combine this with `useSuspenseQuery` (the v5 hook that integrates with React Suspense) and Next.js streaming to progressively render AI-heavy pages: the server streams the shell immediately, then streams in AI-dependent sections as they complete. The v5 `useSuspenseQuery` hook is the replacement for the `suspense: true` option from v4 — it makes the component suspend while data loads, works with React's built-in `<Suspense>` boundaries, and enables streaming SSR without any additional configuration.

```tsx
// app/dashboard/page.tsx — Server Component
import { dehydrate, HydrationBoundary, QueryClient } from '@tanstack/react-query'

export default async function DashboardPage() {
  const queryClient = new QueryClient()
  
  await queryClient.prefetchQuery({
    queryKey: ['ai-insights', 'dashboard'],
    queryFn: fetchAIInsights,
  })

  return (
    <HydrationBoundary state={dehydrate(queryClient)}>
      <Suspense fallback={<InsightsSkeleton />}>
        <AIInsights />
      </Suspense>
    </HydrationBoundary>
  )
}
```

## TanStack Query vs SWR vs Apollo for AI Apps — Which Should You Pick?

The choice between TanStack Query, SWR, and Apollo comes down to feature requirements and bundle size tolerance. TanStack Query leads on features — `streamedQuery`, `broadcastQueryClient`, infinite queries, offline support, DevTools, and the most complete mutation lifecycle — at 13 KB gzipped. SWR is lighter at 4 KB but lacks streaming support and the mutation patterns AI chatbots need. Apollo is the choice only if you're already on GraphQL; for REST or custom AI APIs it adds unnecessary GraphQL infrastructure.

| Library | Bundle (gzipped) | Weekly Downloads | Streaming | Optimistic Updates | DevTools |
|---|---|---|---|---|---|
| TanStack Query v5 | ~13 KB | 12.3M | `streamedQuery` ✓ | Full lifecycle ✓ | Built-in ✓ |
| SWR 2.x | ~4 KB | 4.9M | Manual only | `mutate()` only | Third-party |
| Apollo Client 3.x | ~47 KB | 3.2M | Subscriptions | ✓ | Built-in ✓ |

For AI apps specifically: if you're building an LLM chatbot, document processor, or real-time AI dashboard, TanStack Query's streaming and mutation features justify the 9 KB over SWR. If you're building a simple data display app with no streaming requirements and bundle size is critical (mobile web), SWR is a reasonable choice. Apollo is rarely the right call for AI apps unless your entire data layer is already GraphQL.

## Query Key Factories and Cache Invalidation Patterns for AI Features

Query key factories are a pattern for centralizing query key definitions to prevent typos and make cache invalidation predictable at scale. The pattern is a plain object of functions that return key arrays, defined once and imported wherever you need to interact with the cache. For AI apps with multiple features — chat sessions, document analysis, AI recommendations — scattered string keys like `['chat', sessionId]` become unmaintainable. A factory like `chatKeys.messages(sessionId)` is refactorable, type-safe, and self-documenting. The invalidation payoff is significant: `queryClient.invalidateQueries({ queryKey: chatKeys.all })` clears all chat-related cache in one call, while `queryClient.invalidateQueries({ queryKey: chatKeys.messages(sessionId) })` targets a specific conversation. Selective invalidation is what separates a snappy AI app from one that re-fetches everything on every user action.

```tsx
export const chatKeys = {
  all: ['chat'] as const,
  sessions: () => [...chatKeys.all, 'sessions'] as const,
  session: (id: string) => [...chatKeys.sessions(), id] as const,
  messages: (sessionId: string) => [...chatKeys.session(sessionId), 'messages'] as const,
  aiResponse: (sessionId: string, messageId: string) => 
    [...chatKeys.messages(sessionId), messageId, 'ai'] as const,
}

// Invalidate all messages for a session when AI responds
queryClient.invalidateQueries({ queryKey: chatKeys.messages(sessionId) })

// Invalidate everything when user deletes their account
queryClient.invalidateQueries({ queryKey: chatKeys.all })
```

## Performance Tuning: staleTime, gcTime, and Background Refetch for AI Workloads

Tuning `staleTime` and `gcTime` is how you balance freshness against network cost for AI workloads. The defaults — `staleTime: 0`, `gcTime: 5 minutes` — mean every component mount triggers a background refetch. For AI apps where fetches are expensive (LLM API calls can cost $0.01–$0.10+ each), defaulting to aggressive refetching is wasteful. The right strategy segments data by update frequency. AI-generated content that doesn't change (a processed document summary, a one-time recommendation) should have `staleTime: Infinity` — fetch once, cache forever for the session. Real-time chat messages need `staleTime: 0` with `refetchInterval` for polling, or better, use `streamedQuery` for push-based updates. User preferences and settings can use `staleTime: 5 * 60 * 1000` (5 minutes) — fresh enough to catch updates, conservative enough to avoid unnecessary requests. Configure these at the `QueryClient` level as defaults, then override per-query where the data's freshness requirements differ.

```tsx
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 60_000,        // 1 minute: most app data
      gcTime: 10 * 60_000,      // 10 minutes: keep inactive cache longer
      retry: 2,                 // retry failed AI API calls twice
      retryDelay: attemptIndex => Math.min(1000 * 2 ** attemptIndex, 30_000),
    },
  },
})

// Per-query override for LLM-generated content
const { data } = useQuery({
  queryKey: ['summary', documentId],
  queryFn: () => generateSummary(documentId),
  staleTime: Infinity,  // Never re-fetch the same document summary
  gcTime: 30 * 60_000,  // Keep in cache for 30 minutes
})
```

## Production Checklist: Error Handling, Retry Logic, and DevTools for AI Apps

A production TanStack Query setup for AI apps needs error boundaries, retry logic calibrated to LLM API rate limits, and DevTools enabled in development. The library's default retry behavior (3 retries with exponential backoff) is usually too aggressive for LLM APIs — a 429 rate limit error from OpenAI or Anthropic means waiting seconds or minutes, not milliseconds. Set `retry: 1` or `retry: false` for LLM queries and handle rate limit errors explicitly. For error UI, pair `useSuspenseQuery` with React's `<ErrorBoundary>` so network failures surface cleanly instead of crashing the component tree. The TanStack Query DevTools browser panel shows every cache entry, its status (fresh/stale/fetching/error), and remaining stale time — run it in development to verify your `staleTime` configuration actually produces the caching behavior you expect. Before deploying AI features that call expensive LLM APIs, use the DevTools to confirm that parallel component mounts deduplicate to a single request and that cached responses serve without network hits.

```tsx
// Calibrated retry for LLM APIs
const { data, error } = useQuery({
  queryKey: ['llm-response', prompt],
  queryFn: () => callLLM(prompt),
  retry: (failureCount, error) => {
    // Don't retry 4xx errors (bad request, rate limit exceeded aggressively)
    if (error.status >= 400 && error.status < 500) return false
    return failureCount < 2
  },
  retryDelay: (attemptIndex) => Math.min(2000 * 2 ** attemptIndex, 60_000),
})
```

For observability, consider adding `queryClient.getQueryCache().subscribe()` to log cache events to your monitoring system. You get real-time visibility into how often queries miss cache and hit the LLM API — critical for cost control.

---

## FAQ

**Q: Do I need TanStack Query if I'm already using the Vercel AI SDK for streaming?**

The Vercel AI SDK (`useChat`, `useCompletion`) handles the streaming transport layer for LLM responses and works standalone. TanStack Query adds value on top when you need to cache AI responses across components, sync state across browser tabs with `broadcastQueryClient`, combine AI data with non-AI server data in the same cache, or manage optimistic updates for chat messages. For simple chatbot UIs, the AI SDK alone is sufficient. For complex AI dashboards or apps with multiple data sources, TanStack Query complements the AI SDK by managing the broader data layer.

**Q: What's the difference between staleTime and gcTime in v5?**

`staleTime` controls when data is considered stale (and eligible for background refetch on next mount/focus). `gcTime` controls when inactive cache entries are garbage collected from memory. Data can be stale but still in cache — components get the stale value instantly while a background refetch runs. When `gcTime` expires for an inactive entry, it's removed entirely and the next access triggers a fresh fetch with a loading state. In v4 this was called `cacheTime`; v5 renamed it to `gcTime` to clarify the distinction.

**Q: How does streamedQuery work with abort signals when users navigate away?**

`streamedQuery` automatically passes an `AbortSignal` to your query function via the `signal` parameter in the function context. When the component unmounts (user navigates away) or the query is cancelled, TanStack Query aborts the signal. If you pass this signal to `fetch()`, the in-flight HTTP request is cancelled at the browser level — stopping the LLM stream and preventing unnecessary token consumption. Always wire `signal` through to your fetch calls when using `streamedQuery`.

**Q: Can I use TanStack Query with React Server Components in Next.js App Router?**

Yes, with a specific pattern: you prefetch queries in Server Components using `queryClient.prefetchQuery` and serialize the result with `dehydrate`. This dehydrated state passes to `HydrationBoundary` in a Client Component, which hydrates the client cache. Client Components then use `useQuery` or `useSuspenseQuery` and get the prefetched data immediately without a loading state. The QueryClient itself must be instantiated in a `'use client'` boundary — never in Server Components — to avoid sharing state between concurrent requests.

**Q: Is TanStack Query suitable for apps with real-time WebSocket data alongside AI responses?**

Yes. TanStack Query doesn't manage the WebSocket connection itself, but you can use `queryClient.setQueryData` to push WebSocket messages directly into the cache from an effect or a WebSocket event handler. This pattern — external event source writes into the query cache, components read from the cache — works cleanly for real-time AI streaming dashboards. You get TanStack Query's cache management, DevTools, and component integration for free, with WebSocket handling only where it belongs: the connection layer.
