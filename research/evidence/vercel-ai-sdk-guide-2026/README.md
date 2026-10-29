# Compile matrix for `vercel-ai-sdk-guide-2026`

Local author verification, run in this task's private scratch directory on
2026-10-26 (16:23:45Z–16:24:53Z, 70 s wall clock). Every exit code in the
article's compatibility section comes from the files in `results/`.

Published for readers: the programs, the dependency sets, the script and the raw
`tsc` output are all in this directory. Nothing here is a paid-vendor
measurement, and nothing here is a model or runtime benchmark.

## What was run

`bash run_matrix.sh` is self-contained. It creates three throwaway npm projects
under `$TMPDIR/mx`, copies `programs/package.v{5,6,7}.json` into them as their
`package.json`, copies the four programs in `programs/v{5,6,7}/`, runs
`npm install`, then type-checks each program on its own. It needs `node`, `npm`,
`python3` (used only to narrow `tsconfig.one.json` to one file) and network access
to the npm registry.

| project | `ai` | `@ai-sdk/openai` | `@ai-sdk/react` | TypeScript |
|---|---|---|---|---|
| `v5` | 5.0.281 | 2.0.136 | 2.0.284 | 5.9.3 |
| `v6` | 6.0.315 | 3.0.131 | 3.0.318 | 5.9.3 |
| `v7` | 7.0.153 | 4.0.102 | 4.0.157 | 5.9.3 |

`programs/package.v*.json` also carry `zod`, `react`, `@types/react` and
`@types/node` as caret ranges. The ranges are what was requested; what npm
actually installed is recorded per project in `results/npm-ls-v{5,6,7}.json`
(`npm ls --json --depth=0`, run inside each project after install). In this run
those records show `react` **19.3.1**, `@types/react` 19.3.0, `@types/node`
24.19.2 and the eight `ai`/`@ai-sdk`/`typescript`/`zod` versions as requested,
identical across the three projects. `results/matrix.json` keeps the requested
ranges and the resolved versions in two separate fields for exactly this reason.

`react` is the one dependency whose range cannot be tightened to an exact old
patch: `@ai-sdk/react` 3.0.318 and 4.0.157 declare the peer range
`^18 || ~19.0.1 || ~19.1.2 || ^19.2.1`, so an exact `react@19.2.0` install fails
with ERESOLVE. The projects therefore request `^19.2.0`, which npm resolves to a
19.x release at or above 19.2.1 — 19.3.1 in this run, per the `npm ls` records.

Each project type-checks four programs with `tsc --noEmit` (target ES2022, module
ESNext, moduleResolution bundler, strict, skipLibCheck, jsx react-jsx), one file
per `tsc` invocation so a failing file cannot hide another file's exit code:

- `stream.ts` — `streamText` + `result.textStream` + `result.usage`
- `tool.ts` — one `tool()` with a zod `inputSchema`, `execute`, and a step-count
  stop condition (`stepCountIs` on 5/6, `isStepCount` on 7)
- `chat.tsx` — `useChat` from `@ai-sdk/react`, using `messages`, `sendMessage`, `status`
- `legacy.tsx` — the published April 2026 article's surface verbatim:
  `import { useChat } from 'ai/react'`, `useChat({ api, maxSteps })`,
  `streamText({ maxSteps })`, `toDataStreamResponse()`

Six single-symbol probes per major are also compiled (`results/probes.jsonl`):
`stepCountIs`, `isStepCount`, `streamText({ system })`,
`streamText({ instructions })`, `streamText({ maxSteps })` and
`import { useChat } from 'ai/react'`.

## Which result file the article table uses

`results/summary.jsonl` holds the 12 per-file exit codes — one line per program
per major, each with `"scope": "single_file"`. **The article's exit-code table is
built from those lines.**

`results/project_runs.jsonl` holds the whole-project runs: one
`tsc -p tsconfig.json` per major that includes all four files, plus the three
`npm install` exit codes. Every whole-project run exits 2 on every major, because
`legacy.tsx` is in the same include set and poisons the run. Those lines are kept
for transparency, not because they describe a single program.

`results/matrix.json` is the machine-readable summary assembled from all three
record files plus the `npm ls` output.

## What was not run

- No provider call. No API key was used, so no token was generated and no
  response was streamed from a model. These are compile results only.
- No runtime execution, bundler build, React render or Next.js app. `tsc --noEmit`
  only, which is why the article never claims a snippet "runs" or "works".
- The legacy surface was not exercised at runtime: the type errors stop the
  check, so the article does not assert that it throws at runtime.
- No lockfile is published; dependencies were installed from the ranges in
  `programs/package.v*.json` at run time, and the resolved versions above are the
  ones this run actually used.

## Reproduce

```bash
bash run_matrix.sh     # self-contained; creates $TMPDIR/mx, writes $TMPDIR/mx/results
```

`run_matrix.sh` is the exact script the run used. It needs network access to the
npm registry and about 70 seconds on this host. It does not read any
pre-existing project directory and it refuses to run without `TMPDIR` being set
to a scratch path you own.

## Privacy

First-party code only: four short programs per major written for this check, plus
six one-line probes. No third-party source, credentials, tokens or customer data.
Safe to publish.
