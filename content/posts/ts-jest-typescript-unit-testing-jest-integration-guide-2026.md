---
title: "ts-jest TypeScript Unit Testing Jest Integration Guide 2026"
date: 2026-05-18T09:04:57+00:00
tags: ["ts-jest", "TypeScript", "Jest", "unit-testing", "JavaScript"]
description: "Complete ts-jest setup guide for Jest 30 and TypeScript 5 in 2026: installation, configuration, ESM, monorepo, and common errors fixed."
draft: false
cover:
  image: "/images/ts-jest-typescript-unit-testing-jest-integration-guide-2026.png"
  alt: "ts-jest TypeScript Unit Testing Jest Integration Guide 2026"
  relative: false
schema: "schema-ts-jest-typescript-unit-testing-jest-integration-guide-2026"
---

ts-jest is the official TypeScript preprocessor for Jest, transforming `.ts` and `.tsx` source files into JavaScript that Jest can execute. With 22.7 million weekly npm downloads in 2026, it remains the standard integration layer for TypeScript projects using Jest.

## What Is ts-jest and Why It Still Matters in 2026

ts-jest is a TypeScript preprocessor for Jest that compiles `.ts` and `.tsx` files at test runtime using the TypeScript compiler (`tsc`). Unlike Babel-based approaches, ts-jest performs real TypeScript type checking during test execution, giving you full type safety without a separate compilation step. As of 2026, ts-jest v29.4.9 supports Jest 29–30 and TypeScript 5.x, with 22.7 million weekly npm downloads and 7,077+ GitHub stars. The package has 3,729 direct dependents on npm, making it deeply embedded in the JavaScript ecosystem.

The key reason ts-jest remains relevant in 2026 despite competitors like Vitest is its ecosystem compatibility. React Native projects require Jest's jsdom environment, and large legacy codebases with millions of lines of Jest tests cannot migrate overnight. ts-jest also provides the closest semantics to production TypeScript compilation because it uses the actual TypeScript compiler — meaning your test types match your production types exactly, with no transpile shortcuts. If you're running Jest 30 on a TypeScript 5 project and need type-safe tests with minimal setup, ts-jest is still the most direct path.

### How ts-jest Differs From @swc/jest and Babel

ts-jest uses the TypeScript compiler (`tsc`) to transform files, which means full type information is available. `@swc/jest` strips types without checking them (3-5x faster transforms, zero type safety). Babel with `@babel/preset-typescript` also strips types. For CI pipelines where correctness matters more than raw speed, ts-jest remains the default choice.

## Installing ts-jest with Jest 30 and TypeScript 5

Installing ts-jest correctly with Jest 30 and TypeScript 5 requires three packages: `jest`, `ts-jest`, and `@types/jest`. As of 2026, the compatible version combination is Jest ≥30.0.0, ts-jest ≥29.4.0, and TypeScript ≥5.0.0. Run the following to install the complete set of dependencies in one command, ensuring peer dependency alignment across the entire testing stack.

```bash
npm install --save-dev jest ts-jest @types/jest typescript
```

For a TypeScript project starting from scratch, also add a `tsconfig.json` if one doesn't exist:

```bash
npx tsc --init
```

Verify that your `tsconfig.json` includes `"module": "CommonJS"` (or `"NodeNext"` for ESM — covered separately below) and `"strict": true`. ts-jest reads your project's `tsconfig.json` by default, so mismatches between your tsconfig and jest config are a common source of errors.

After installation, confirm the version alignment:

```bash
npx ts-jest --version
# Expected: ts-jest/29.x.x with jest 30.x.x
```

### TypeScript 5 Compatibility Notes

TypeScript 5 introduced decorator changes (`experimentalDecorators` now defaults to `false`). If your codebase uses decorators (NestJS, TypeORM), add `"experimentalDecorators": true` to your tsconfig before running ts-jest. Also, TypeScript 5's stricter module resolution under `"moduleResolution": "bundler"` is not yet fully supported by ts-jest — stick with `"moduleResolution": "node16"` or `"node"` for test environments.

## Configuring ts-jest: Complete jest.config.ts Reference

Configuring ts-jest requires a `jest.config.ts` file (or `.js`/`.mjs`) at your project root. Jest 30 natively supports `jest.config.ts`, eliminating the need for Babel transpilation during test initialization — a significant improvement over Jest 28. The configuration below is a production-ready starting point for a Node.js TypeScript project with all major ts-jest options documented inline. The most important fields are the `transform` entry (which wires ts-jest as the TypeScript preprocessor), `moduleNameMapper` (which resolves path aliases like `@/`), and `diagnostics` (which controls whether type errors fail the test run). Getting these three fields right eliminates 90% of ts-jest configuration issues seen in 2026 projects.

```typescript
import type { Config } from 'jest';

const config: Config = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  roots: ['<rootDir>/src'],
  testMatch: ['**/__tests__/**/*.ts', '**/*.spec.ts', '**/*.test.ts'],
  transform: {
    '^.+\\.tsx?$': ['ts-jest', {
      tsconfig: 'tsconfig.json',
      isolatedModules: true,     // fastest option — see next section
      diagnostics: {
        ignoreCodes: ['TS151001'] // suppress known ts-jest diagnostic
      }
    }]
  },
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1'  // resolve @ path aliases
  },
  collectCoverageFrom: [
    'src/**/*.ts',
    '!src/**/*.d.ts',
    '!src/**/index.ts'
  ]
};

export default config;
```

### Key Configuration Fields Explained

- **`preset: 'ts-jest'`** — shorthand that sets `transform`, `testMatch`, and `moduleFileExtensions` for TypeScript projects
- **`testEnvironment: 'node'`** — use `'jsdom'` for React/browser projects (requires `jest-environment-jsdom`)
- **`moduleNameMapper`** — critical for projects using TypeScript path aliases (`@/components` → `src/components`); without this, ts-jest will throw "Cannot find module" errors
- **`diagnostics`** — controls whether type errors fail tests; set `diagnostics: false` to disable type checking in ts-jest (useful when running `tsc --noEmit` separately in CI)

## isolatedModules — The Fastest Path to TypeScript Testing

`isolatedModules: true` is the single most impactful performance optimization available to ts-jest users, reducing transform time by 30-60% in typical projects. When enabled, ts-jest transforms each file independently without cross-file type information — identical to TypeScript's `--isolatedModules` flag. The trade-off is that some TypeScript features requiring cross-file analysis (const enums, namespace imports, ambient declarations) will throw errors at transform time.

Setting `isolatedModules: true` in ts-jest's transform options tells the compiler to skip the type-checking phase entirely during test runs. This makes ts-jest behave more like Babel or @swc/jest in terms of speed, while retaining TypeScript syntax parsing. For a 200-test suite, this can cut runtime from 12 seconds down to 5-7 seconds — a meaningful improvement in local development feedback loops.

```typescript
transform: {
  '^.+\\.tsx?$': ['ts-jest', {
    isolatedModules: true
  }]
}
```

### When NOT to Use isolatedModules

Avoid `isolatedModules: true` if your codebase relies on:
- `const enum` declarations (they require cross-file compilation)
- `.d.ts` ambient modules with re-exported types used in test assertions
- TypeScript `namespace` merging patterns

In these cases, keep `isolatedModules: false` (the default) and accept the slower compile time. For the majority of modern TypeScript codebases following ESM module conventions, `isolatedModules: true` is safe and strongly recommended.

## ESM Support with ts-jest (Experimental but Production-Ready)

ts-jest's ESM support in 2026 is experimental in name but production-viable in practice for Node.js projects. The configuration requires two environment-level changes alongside ts-jest options: setting `NODE_OPTIONS=--experimental-vm-modules` and using `extensionsToTreatAsEsm` in jest config. This setup enables native ES module syntax (`import`/`export`) in test files without CommonJS transformation.

ESM with ts-jest is necessary when your dependencies ship ESM-only packages (a growing list in 2026, including `node-fetch`, `chalk`, and many utility libraries). Without ESM mode, ts-jest will fail on these imports with `SyntaxError: Cannot use import statement in a module`.

**Step 1** — Update `package.json`:
```json
{
  "type": "module",
  "scripts": {
    "test": "NODE_OPTIONS=--experimental-vm-modules jest"
  }
}
```

**Step 2** — Update `jest.config.ts`:
```typescript
const config: Config = {
  preset: 'ts-jest/presets/default-esm',
  testEnvironment: 'node',
  extensionsToTreatAsEsm: ['.ts'],
  transform: {
    '^.+\\.tsx?$': ['ts-jest', {
      useESM: true
    }]
  },
  moduleNameMapper: {
    '^(\\.{1,2}/.*)\\.js$': '$1'  // strip .js extensions for ESM resolution
  }
};
```

**Step 3** — Update `tsconfig.json`:
```json
{
  "compilerOptions": {
    "module": "NodeNext",
    "moduleResolution": "NodeNext"
  }
}
```

### ESM Gotchas in 2026

The `moduleNameMapper` stripping `.js` extensions is critical — when TypeScript compiles ESM, it emits `import './foo.js'` even for `.ts` source files. Jest's resolver can't find `.ts` files at `.js` paths without this mapping. Also note: `jest.config.ts` itself must use `import`/`export` syntax when `"type": "module"` is set in `package.json`.

## Setting Up ts-jest for React TypeScript Projects

Setting up ts-jest for React TypeScript projects requires the jsdom test environment and JSX transform configuration in addition to the standard ts-jest setup. React 18+ uses the automatic JSX runtime, which changes how `@jsx` directives work in TypeScript. Failing to configure this correctly produces `React is not defined` errors even when React is installed.

Start by installing the additional dependencies:

```bash
npm install --save-dev jest-environment-jsdom @testing-library/react @testing-library/jest-dom @testing-library/user-event
```

Then configure `jest.config.ts` for React:

```typescript
import type { Config } from 'jest';

const config: Config = {
  preset: 'ts-jest',
  testEnvironment: 'jsdom',
  setupFilesAfterFramework: ['<rootDir>/src/setupTests.ts'],
  transform: {
    '^.+\\.tsx?$': ['ts-jest', {
      tsconfig: {
        jsx: 'react-jsx',
        jsxImportSource: 'react'
      },
      isolatedModules: true
    }]
  },
  moduleNameMapper: {
    '\\.(css|less|scss|sass)$': '<rootDir>/__mocks__/styleMock.js',
    '\\.(jpg|jpeg|png|gif|svg)$': '<rootDir>/__mocks__/fileMock.js'
  }
};

export default config;
```

Create a setup file for jest-dom matchers and static asset stubs:

```typescript
// src/setupTests.ts
import '@testing-library/jest-dom';
```

```javascript
// __mocks__/styleMock.js
module.exports = {};

// __mocks__/fileMock.js
module.exports = 'test-file-stub';
```

### Testing a React Component with ts-jest

```typescript
// src/components/Button.test.tsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Button } from './Button';

describe('Button', () => {
  it('calls onClick when clicked', async () => {
    const handleClick = jest.fn();
    render(<Button onClick={handleClick}>Click me</Button>);
    
    await userEvent.click(screen.getByRole('button'));
    
    expect(handleClick).toHaveBeenCalledTimes(1);
  });
});
```

## ts-jest in Monorepo Environments with Jest Projects API

ts-jest in monorepo environments works best with Jest 30's `projects` API, which lets a single `jest` command run tests across multiple packages with package-specific ts-jest configurations. This approach eliminates the need for separate `jest` invocations per package and centralizes CI test orchestration. Jest 30 improvements to project-level configurations can reduce CI/CD pipeline duration by 10-15 minutes in large monorepos compared to Jest 28 approaches.

The monorepo structure uses a root-level `jest.config.ts` that references per-package configurations:

```
monorepo/
├── jest.config.ts          # root config
├── packages/
│   ├── api/
│   │   ├── jest.config.ts  # api-specific config
│   │   └── tsconfig.json
│   └── ui/
│       ├── jest.config.ts  # ui-specific config
│       └── tsconfig.json
└── tsconfig.base.json      # shared tsconfig
```

**Root `jest.config.ts`:**
```typescript
import type { Config } from 'jest';

const config: Config = {
  projects: [
    '<rootDir>/packages/api/jest.config.ts',
    '<rootDir>/packages/ui/jest.config.ts'
  ],
  coverageDirectory: '<rootDir>/coverage',
  collectCoverageFrom: ['packages/*/src/**/*.ts']
};

export default config;
```

**Package-level `packages/api/jest.config.ts`:**
```typescript
import type { Config } from 'jest';

const config: Config = {
  displayName: 'api',
  preset: 'ts-jest',
  testEnvironment: 'node',
  rootDir: '.',
  transform: {
    '^.+\\.tsx?$': ['ts-jest', {
      tsconfig: '<rootDir>/tsconfig.json',
      isolatedModules: true
    }]
  }
};

export default config;
```

### Shared tsconfig for Monorepos

```json
// tsconfig.base.json
{
  "compilerOptions": {
    "strict": true,
    "module": "CommonJS",
    "moduleResolution": "node",
    "esModuleInterop": true,
    "declaration": true,
    "skipLibCheck": true
  }
}

// packages/api/tsconfig.json
{
  "extends": "../../tsconfig.base.json",
  "compilerOptions": {
    "outDir": "./dist",
    "rootDir": "./src"
  }
}
```

## ts-jest vs @swc/jest vs Vitest: Choosing Your Stack in 2026

ts-jest, @swc/jest, and Vitest represent three distinct philosophies for TypeScript testing in 2026, each with clear trade-offs around speed, type safety, and compatibility. Vitest runs 5-28x faster than Jest with ts-jest across benchmark scenarios, and for a 200-test suite this translates to 2-4 seconds (Vitest) versus 8-12 seconds (Jest+ts-jest). Despite this speed gap, ts-jest remains the correct choice for specific contexts: React Native projects, teams with deep Jest expertise, and existing codebases with thousands of Jest tests.

| Factor | ts-jest | @swc/jest | Vitest |
|--------|---------|-----------|--------|
| Transform speed | Slowest (uses tsc) | Fast (Rust compiler) | Fastest (Vite-native) |
| Type checking | Full (optional) | None (strips types) | None (strips types) |
| Jest API compat | 100% | 100% | ~95% (minor gaps) |
| React Native | Yes | Yes | No (limited) |
| ESM support | Experimental | Good | Native |
| Config complexity | Medium | Low | Low |
| Migration effort | Baseline | Low from ts-jest | Medium |

### When to Choose Each Option

**Choose ts-jest** when: you're on React Native, your team uses `jest.mock()` extensively with type-safe mocks, or you have a large existing Jest test suite where migration risk is high.

**Choose @swc/jest** when: you want a drop-in ts-jest replacement with 3-5x faster transforms, don't need type checking in tests (you run `tsc --noEmit` separately), and want zero config changes to existing Jest tests.

**Choose Vitest** when: you're starting a new project, your production bundler is Vite, or you need the fastest possible test feedback loop and are willing to migrate away from Jest APIs.

## Common ts-jest Errors and How to Fix Them

The most common ts-jest errors fall into three categories: module resolution failures, transform configuration mismatches, and type checking failures. Over 30% of repository setups with modern dependencies experience `transformIgnorePatterns` issues with ts-jest — typically caused by ESM-only npm packages that ts-jest doesn't transform by default. Understanding the root cause of each error category prevents hours of debugging. Module resolution failures (the "Cannot find module" error) almost always trace back to missing `moduleNameMapper` entries for TypeScript path aliases. Transform mismatches — particularly the `SyntaxError: Cannot use import statement outside a module` error — occur when an ESM-only npm package like `node-fetch`, `uuid`, or `chalk` is imported in a test but excluded from transformation by the default `transformIgnorePatterns`. Type checking failures, where tests pass in ts-jest but the production build fails `tsc`, typically indicate that `isolatedModules: true` is masking cross-file type errors that only full compilation catches. Each of the five errors below comes with a symptom, root cause diagnosis, and a concrete fix that works in Jest 29 and Jest 30.

### Error 1: "Cannot find module" for Path Aliases

**Symptom:** `Cannot find module '@/components/Button' from 'src/App.test.tsx'`

**Cause:** TypeScript path aliases (`@/`) are resolved by tsc during compilation but not by Jest's module resolver.

**Fix:** Add `moduleNameMapper` to `jest.config.ts`:
```typescript
moduleNameMapper: {
  '^@/(.*)$': '<rootDir>/src/$1'
}
```

### Error 2: SyntaxError on ESM Package Import

**Symptom:** `SyntaxError: Cannot use import statement outside a module` when importing packages like `node-fetch`, `uuid`, or `chalk`.

**Cause:** These packages ship ESM-only code. ts-jest's default `transformIgnorePatterns` excludes `node_modules`.

**Fix:** Override `transformIgnorePatterns` to allow specific packages:
```typescript
transformIgnorePatterns: [
  '/node_modules/(?!(node-fetch|uuid|chalk)/)'
]
```

### Error 3: "isolatedModules" const enum Error

**Symptom:** `Error: 'const enums' are not supported. Use '--isolatedModules' flag is required.`

**Cause:** `const enum` requires cross-file compilation context that `isolatedModules: true` skips.

**Fix:** Either remove `const enum` (replace with `enum` or `as const` objects), or disable `isolatedModules`:
```typescript
// Option A: change const enum to regular enum
enum Status { Active = 'active', Inactive = 'inactive' }

// Option B: disable isolatedModules (slower)
transform: { '^.+\\.tsx?$': ['ts-jest', { isolatedModules: false }] }
```

### Error 4: Types Don't Match Between Tests and Source

**Symptom:** Test passes but production build fails type checking.

**Cause:** ts-jest with `diagnostics: false` or `isolatedModules: true` may miss cross-file type errors.

**Fix:** Run `tsc --noEmit` as a separate CI step (see next section).

### Error 5: jest.config.ts Itself Fails to Load

**Symptom:** `SyntaxError` or `Cannot find module` when Jest tries to read `jest.config.ts`.

**Cause:** Jest 30 supports `jest.config.ts` natively, but older versions require ts-node or ts-jest/config imports.

**Fix:** For Jest 30+, ensure you're using the latest Jest. For older versions:
```bash
npm install --save-dev ts-node
```
Or rename to `jest.config.js` and use `require`.

## CI/CD Best Practices: Type Checking + ts-jest Together

The modern TypeScript CI strategy separates type checking from test execution into two parallel jobs, combining the speed of `isolatedModules: true` with the safety of full type checking. Type checking runs `tsc --noEmit` against the full TypeScript project, while tests run through ts-jest with `isolatedModules` enabled. This two-stage approach gives you the best of both worlds: fast test feedback loops and guaranteed type correctness before merge.

Running `tsc --noEmit` catches errors that ts-jest with `isolatedModules: true` misses — particularly cross-file type errors, incorrect generic inference, and structural type mismatches. On a large codebase, running both in parallel rather than serially can save 5-8 minutes per CI run.

**GitHub Actions example (parallel jobs):**
```yaml
name: CI

on: [push, pull_request]

jobs:
  type-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
      - run: npm ci
      - run: npx tsc --noEmit

  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
      - run: npm ci
      - run: npx jest --coverage --ci
```

### Caching Dependencies in CI

Cache the `node_modules` directory to avoid reinstalling ts-jest and TypeScript on every run:

```yaml
- uses: actions/cache@v4
  with:
    path: ~/.npm
    key: ${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}
```

### ts-jest Diagnostics Configuration for CI

In CI, you may want to fail on type errors that local development ignores. Set `diagnostics: true` with `warnOnly: false` for strict CI:

```typescript
transform: {
  '^.+\\.tsx?$': ['ts-jest', {
    isolatedModules: true,
    diagnostics: {
      warnOnly: false,       // fail the build on type errors
      exclude: ['/node_modules/'] // don't type-check dependencies
    }
  }]
}
```

For local development, flip `warnOnly: true` so type errors show as warnings without blocking your test run.

---

## FAQ

These are the most frequently asked questions about ts-jest configuration, migration, and troubleshooting in 2026. The answers cover the most common pain points developers encounter when integrating TypeScript with Jest: transformer selection, performance optimization, ESM compatibility, error resolution, and framework choice. Each answer is actionable — covering not just what to do, but why the decision matters for your specific project context. Whether you're setting up ts-jest for the first time, migrating from an older version, or deciding between ts-jest and Vitest, these answers reflect the current state of the TypeScript testing ecosystem as of ts-jest v29.4.9 and Jest 30. The ts-jest package receives 22.7 million weekly downloads and is the default TypeScript transformer for Jest-based projects worldwide, making these questions relevant to the majority of TypeScript development teams in 2026.

### What is the difference between ts-jest and Babel for TypeScript testing?

ts-jest uses the actual TypeScript compiler (`tsc`) to transform test files, which means it can optionally perform real type checking during the test run. Babel with `@babel/preset-typescript` strips types entirely without any validation — it transpiles faster but catches zero type errors. The practical consequence: with ts-jest and `diagnostics: true`, a type mismatch in a test file fails the test run before any test executes. With Babel, the same error is silent. In 2026, the recommended pattern for projects that need both speed and safety is ts-jest with `isolatedModules: true` (fast transforms, no cross-file type analysis) plus `tsc --noEmit` as a parallel CI job (full type checking, no test execution).

### How do you migrate from ts-jest 29.4.x to Jest 30?

Upgrade `jest` and `@types/jest` to `30.x`, then update `ts-jest` to the latest v29.4.x (which supports both Jest 29 and 30). The main breaking change is the configuration format: the legacy `globals['ts-jest']` style is removed in Jest 30. Replace it with the array transform format: `transform: { '^.+\\.tsx?$': ['ts-jest', { tsconfig: 'tsconfig.json' }] }`. You can also convert `jest.config.js` to `jest.config.ts` — Jest 30 supports TypeScript config files natively without ts-node. Run `npx jest --clearCache` after upgrading to clear stale transform caches that can cause false errors on first run.

### Does isolatedModules: true disable TypeScript type checking completely?

No — it disables cross-file type analysis, not intra-file type checking. With `isolatedModules: true`, ts-jest transforms each file independently without loading the full TypeScript project graph. Type errors within a single file (wrong argument type, missing property on a local interface defined in the same file) are still caught. What is disabled is analysis that requires importing type information from other modules — `const enum` declarations, namespace imports, and type constraints that reference types from separate files. To get full cross-file type safety alongside `isolatedModules: true`, run `tsc --noEmit` as a separate CI step.

### How do you fix SyntaxError when ts-jest imports ESM packages?

Override `transformIgnorePatterns` to include the ESM-only package in ts-jest's transform pipeline. The default pattern excludes all of `node_modules`, but ESM-only packages like `node-fetch`, `uuid`, `chalk`, and `nanoid` must be transformed. The fix: `transformIgnorePatterns: ['/node_modules/(?!(node-fetch|uuid|chalk)/)']`. For multiple packages, extend the alternation group using pipe separators. A more complete solution for projects with many ESM dependencies is enabling ts-jest's ESM mode (`useESM: true` in the transform options) combined with `--experimental-vm-modules` in the Node.js test runner — this avoids maintaining a growing exclusion list.

### Should you use ts-jest or Vitest for a new TypeScript project in 2026?

For most new TypeScript projects not targeting React Native, Vitest is the better default — it is 5–28x faster than ts-jest, has first-class ESM support built in, and requires minimal configuration for TypeScript projects. ts-jest remains the correct choice for React Native projects (which require Jest's jsdom environment and React Native-specific jest presets), large existing Jest codebases where migration cost outweighs speed gains, and projects that depend heavily on Jest-specific APIs (`jest.mock()`, `jest.spyOn()`, `jest.useFakeTimers()`) where Vitest's behavioral differences introduce migration risk. If you need Jest API compatibility with faster transforms, `@swc/jest` is a drop-in ts-jest replacement using SWC (a Rust-based compiler) at 10–30x the speed without type checking.
