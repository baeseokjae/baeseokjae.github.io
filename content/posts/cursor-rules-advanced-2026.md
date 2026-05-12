---
title: "Cursor Rules Advanced Guide 2026: Framework-Specific Configs & .mdc Best Practices"
date: 2026-05-12T00:04:11+00:00
tags: ["cursor", "cursor-rules", "mdc", "ai-coding", "developer-tools"]
description: "Master Cursor rules advanced configuration in 2026: .mdc frontmatter, four activation modes, framework templates for React/Next.js/FastAPI, and token optimization."
draft: false
cover:
  image: "/images/cursor-rules-advanced-2026.png"
  alt: "Cursor Rules Advanced Guide 2026: Framework-Specific Configs & .mdc Best Practices"
  relative: false
schema: "schema-cursor-rules-advanced-2026"
---

Cursor rules are per-project instruction files that tell the AI model how to behave, what patterns to follow, and which constraints to apply. With Cursor hitting 1M+ daily users and $2B+ annualized revenue by early 2026, correctly configuring `.mdc` rules is now the difference between a 20% productivity gain and AI output you have to rewrite every time.

## What Are Cursor Rules and Why Advanced Configuration Matters in 2026

Cursor rules are structured instruction files that shape how Cursor's AI behaves within your project — defining code style, framework conventions, architecture constraints, and domain-specific patterns. As of 2026, Cursor serves over 1 million daily users and 50,000 businesses, with custom rules adopted by 50% of enterprise teams. The original `.cursorrules` format still works for basic use, but the modern `.cursor/rules/` directory with `.mdc` files unlocks scope control that the legacy format cannot provide: rules can auto-attach to specific file types, activate on agent request, or stay manual. Without advanced configuration, all rules load for every conversation — a token tax that degrades model performance on complex tasks. Teams using well-structured rule hierarchies report 20–25% time savings on debugging and refactoring, and companies that properly configure agent rules merge 39% more PRs. If you're still using a single `.cursorrules` file for a multi-framework project, you're leaving most of that value on the table.

## Legacy .cursorrules vs Modern .mdc Format: What Changed?

The `.cursorrules` format is a single flat file in the project root. It loads globally for every chat session. It has zero scope control — every rule applies to every conversation, regardless of context. The critical 2026 gotcha: `.cursorrules` is **silently ignored in Cursor Agent mode**. If your team switched to agentic workflows and your rules mysteriously stopped working, this is why.

The modern `.cursor/rules/` directory solves these problems with `.mdc` (Markdown with Cursor metadata) files. Each `.mdc` file has a YAML frontmatter block that controls when and how the rule activates.

| Feature | `.cursorrules` | `.mdc` (`.cursor/rules/`) |
|---|---|---|
| Scope control | None — always global | Per-file, per-glob, or per-request |
| Agent mode support | Not supported (silently ignored) | Full support |
| Multiple rule files | Single file only | Unlimited, modular |
| Team sharing via Git | Yes | Yes |
| Activation modes | Always (implicit) | Always Apply, Auto Attach, Agent Requested, Manual |
| Subdirectory scoping | No | Yes — nested rules attach to local context |

The migration path is straightforward: create `.cursor/rules/`, split your `.cursorrules` content into focused `.mdc` files by concern, and add YAML frontmatter to each. The old file can remain as a fallback during transition.

## Anatomy of a .mdc File: YAML Frontmatter Deep Dive

A `.mdc` file is a Markdown document with a YAML frontmatter block that Cursor reads to determine activation behavior. The frontmatter has three fields that control everything: `description`, `alwaysApply`, and `globs`. Understanding these fields precisely is what separates a well-tuned rule system from a bloated one that eats your context window.

Here is a complete annotated example:

```yaml
---
description: "Enforce Next.js 15 App Router conventions: server components by default, client components only when needed, no Pages Router patterns"
alwaysApply: false
globs: ["app/**/*.tsx", "app/**/*.ts", "components/**/*.tsx"]
---
```

**`description`** — The AI reads this field to decide whether to activate an Agent Requested rule. Write it as a precise statement of what the rule enforces, not a vague label. Bad: `"Next.js rules"`. Good: the example above. The description is your rule's semantic hook for the model.

**`alwaysApply`** — Boolean. When `true`, this rule loads in every conversation. Keep always-apply rules under 200 words total — every token here is a tax on every request. When `false`, activation depends on globs or agent decision.

**`globs`** — Array of glob patterns. When any referenced file matches, the rule auto-attaches. Supports standard glob syntax: `**/*.tsx`, `src/api/**/*.py`, `packages/*/src/**`.

Rules without `globs` and with `alwaysApply: false` become Agent Requested — the model decides whether to load them based on `description`.

## The Four Activation Modes Explained with Real Examples

Cursor `.mdc` rules support four distinct activation modes that determine when rule content is injected into the model's context. Choosing the wrong mode is the most common cause of rules being ignored or context windows being wasted. The four modes are Always Apply, Auto Attached, Agent Requested, and Manual. Each mode has a specific use case: Always Apply is for universal constraints that apply regardless of task; Auto Attached is for framework or file-type conventions; Agent Requested is for optional expert knowledge the AI can pull when relevant; Manual is for sensitive or large reference rules you include explicitly.

**Always Apply** — `alwaysApply: true`, no globs required. Use for: security policies, commit message format, output language constraints, global naming conventions. Keep this under 2,000 tokens combined across all always-apply rules. This is the total budget before you start seeing degraded performance.

```yaml
---
description: "Global security and output rules"
alwaysApply: true
---
- Never expose secrets or API keys in generated code
- All user inputs must be validated before use
- Use parameterized queries — no string concatenation in SQL
```

**Auto Attached** — `alwaysApply: false`, globs defined. Activates when matching files are open or referenced. Use for: framework rules, language-specific style, test file conventions.

```yaml
---
description: "React component rules"
alwaysApply: false
globs: ["**/*.tsx", "**/*.jsx"]
---
```

**Agent Requested** — `alwaysApply: false`, no globs, description written as a semantic signal. The AI decides whether to load the rule. Use for: architecture documentation, API client patterns, domain logic explanations.

```yaml
---
description: "Authentication flow: JWT refresh token rotation pattern, session storage strategy, and OAuth2 provider integration details"
alwaysApply: false
---
```

**Manual** — Explicitly included by typing `@ruleName` in the chat. Use for: large reference templates, migration guides, rarely-needed but important details.

## Framework-Specific Rule Configurations

Framework-specific Cursor rules are `.mdc` files scoped to a particular technology stack that encode opinionated decisions — component structure, import ordering, testing patterns, error handling — so the AI produces output aligned with your project's architecture without explicit per-prompt instructions. As of Cursor 3.2 and Composer 2 (2026), framework rules are the most impactful category: developers who configure stack-specific rules report 30–40% fewer round-trip corrections on generated code. The key insight is that one rule file per framework concern outperforms one monolithic rules file, because Auto Attached mode loads only the relevant rules for the files in context — a React rule doesn't load when you're editing a Python migration script. Below are production-ready templates for the four most common stacks: React 19 / Next.js 15 App Router, TypeScript strict mode, FastAPI with Python 3.11+, and Django 5.1+. Each template uses glob patterns verified against real projects and omits rules that are already enforced by the compiler or linter, keeping the rule files lean and semantically meaningful for the AI.

### React 19 and Next.js 15 App Router Rules

```yaml
---
description: "Next.js 15 App Router conventions — server vs client components, data fetching, routing patterns"
alwaysApply: false
globs: ["app/**/*.tsx", "app/**/*.ts", "components/**/*.tsx"]
---

## Component Model
Next.js 15 App Router introduces a fundamental shift in how components are classified: every component is a Server Component by default unless explicitly marked otherwise. This distinction determines where rendering happens, what APIs are available, and how data flows through the tree. The AI must respect this boundary to avoid generating code that breaks at runtime — mixing server and client patterns is the most common source of hydration errors and unexpected behavior in App Router projects. Client components are not worse, they are simply different: they handle interactivity, browser APIs, and stateful logic. Server components handle data access, heavy computation, and anything that should never reach the client bundle. Getting this boundary right is the foundation of every other App Router convention.
- Default to Server Components — add 'use client' only when you need hooks, event listeners, or browser APIs
- Never use `getServerSideProps`, `getStaticProps`, or Pages Router patterns in the `app/` directory
- Colocate loading.tsx, error.tsx, and not-found.tsx with their route segments

## Data Fetching
App Router data fetching is built on React's extended `fetch` API and async Server Components, replacing the Pages Router pattern of `getServerSideProps` and `getStaticProps` entirely. The mental model is straightforward: fetch data where you need it, as close to the component that uses it as possible, using native `async/await` syntax. Waterfall fetches — where one await blocks another — are the primary performance bottleneck in Server Component trees. Parallel fetching with `Promise.all` eliminates that bottleneck. The `cache()` function and `revalidate` options on `fetch` replace custom caching layers and give fine-grained control over when data is considered stale. Understanding these primitives prevents the AI from reaching for client-side `useEffect` patterns that belong to the Pages Router era and degrade both performance and developer experience.
- Use async Server Components for data fetching — no useEffect for initial data
- Parallel data fetching: use Promise.all for independent requests
- Use `cache()` and `revalidate` options on fetch, not custom caching layers

## TypeScript
TypeScript integration in Next.js 15 App Router is deeper than in previous versions: Server Actions require typed params, route segment config types are enforced by the framework, and the `Metadata` type constrains what `generateMetadata` can return. Allowing implicit `any` in this environment undermines the entire value of TypeScript — the AI will generate code that compiles but hides type errors that surface only at runtime. Props interfaces must be explicit because Server Components pass data across the server boundary where type safety is the only contract. `React.FC` is broadly discouraged in the React community because it adds an implicit `children` prop and obscures return types; explicit annotations are always clearer. Server Action params validated with zod provide runtime safety that TypeScript alone cannot guarantee, since actions receive raw form data.
- All props interfaces explicitly typed — no implicit `any`
- Use `React.FC` sparingly — prefer explicit return type annotations
- Server Action params must be validated with zod before use
```

### TypeScript Strict Mode Rules

TypeScript strict mode rules enforce the compiler settings your team agreed on and prevent the AI from silently downgrading type safety when generating boilerplate.

```yaml
---
description: "TypeScript strict mode conventions — no implicit any, exhaustive type guards, discriminated unions"
alwaysApply: false
globs: ["**/*.ts", "**/*.tsx"]
---

## Type Safety
TypeScript strict mode enforces a set of compiler options — `strictNullChecks`, `noImplicitAny`, `strictFunctionTypes`, and others — that together eliminate the most common categories of runtime type errors. When the AI generates code without these constraints in mind, it produces patterns that pass loose TypeScript checks but fail strict mode, requiring developers to fix type errors manually. The `any` type is the most damaging: it silently disables type checking for everything it touches. Using `unknown` with explicit type guards is the correct alternative — it forces the developer and the AI to account for every possible shape of data. Discriminated unions with exhaustive switch statements are the idiomatic TypeScript pattern for modeling states that have mutually exclusive shapes; the `satisfies never` default case catches unhandled variants at compile time, preventing silent runtime failures when new variants are added.
- Never use `any` — use `unknown` and narrow with type guards
- Exhaustive switch statements: add `satisfies never` default case for discriminated unions
- Prefer `type` over `interface` for data shapes; use `interface` only for extension points

## Patterns to Avoid
Certain TypeScript patterns represent shortcuts that erode type safety over time and signal that the AI is not respecting the project's type discipline. Non-null assertions (`!`) tell TypeScript to trust the developer that a value is not null or undefined — a promise that is frequently broken, especially in generated code where the AI does not have full context of initialization order. Suppression directives like `@ts-ignore` hide real errors from the compiler and make codebases harder to upgrade safely. Unsafe `as Type` casts bypass structural type checking entirely and are a common source of subtle bugs where data does not match the assumed shape. Each of these patterns is sometimes necessary, but only with explicit justification and only when a proper type guard or narrowing approach is genuinely not feasible in that specific context.
- No non-null assertions (`!`) except in test files
- No `@ts-ignore` or `@ts-expect-error` without an explaining comment
- No `as Type` casts without a guard function verifying the shape
```

### FastAPI and Python 3.11+ Rules

```yaml
---
description: "FastAPI 0.115+ with Python 3.11+ — async endpoints, Pydantic v2 models, dependency injection patterns"
alwaysApply: false
globs: ["**/*.py", "app/api/**/*.py", "routers/**/*.py"]
---

## Endpoint Conventions
FastAPI's design is built around async-first execution and Pydantic-based schema validation — deviating from these conventions produces endpoints that are harder to test, slower under load, and inconsistent with the rest of the codebase. Synchronous route handlers block the event loop and negate FastAPI's concurrency advantages; every endpoint should be `async def`. Raw dict inputs and outputs bypass Pydantic's validation and serialization, which means no automatic OpenAPI schema generation, no input coercion, and no response model enforcement. HTTP status codes embedded as magic numbers inside response bodies instead of using the `status_code=` parameter break HTTP semantics and make API clients harder to write correctly. The dependency injection system for database sessions ensures connection lifecycle is managed by FastAPI rather than scattered across individual route handlers, which simplifies testing and prevents connection leaks.
- All endpoints must be async — no synchronous route handlers
- Use Pydantic v2 BaseModel for request/response schemas — no raw dicts
- HTTP status codes explicit: use `status_code=` parameter, not magic numbers in body
- Dependency injection for DB sessions: `db: AsyncSession = Depends(get_db)`

## Error Handling
FastAPI provides a structured error handling system through `HTTPException` and custom exception handlers that should be the sole mechanism for surfacing errors to API consumers. Raising `HTTPException` with a meaningful `detail` string gives clients actionable information and keeps error responses consistent across the API. Registering exception handlers in `main.py` centralizes error logic so that all routes benefit from the same behavior without duplicating try/except blocks in every handler. Inline exception handling inside routes is acceptable only for business logic errors that require context from the route itself. Logging with structlog instead of print statements ensures errors are captured in a structured format that works with log aggregation systems, supports context fields like request ID and user ID, and is filterable in production without code changes. Print statements disappear in containerized environments where stdout is not captured.
- Raise `HTTPException` with detail str, not generic 500
- Custom exception handlers registered in `main.py` — not inline try/except in routes
- Log errors with structlog — no print statements

## Type Hints
Python type hints in FastAPI serve a purpose beyond documentation: FastAPI reads them at runtime to generate OpenAPI schemas, validate inputs, serialize outputs, and wire up dependency injection. Missing or incomplete type hints break these mechanisms silently — the endpoint still works but schema generation produces incomplete docs, validation is skipped, and dependency injection may fail. Full type hints on all function signatures means every parameter, every dependency, and every return type is explicitly annotated. The `Annotated[]` syntax introduced in Python 3.9 and standardized in 3.11 is the idiomatic way to attach FastAPI metadata — validators, dependencies, query parameter constraints — to a type annotation without losing the type information itself. Return type annotations on route handlers enable response model validation and ensure the serialized output matches the declared schema.
- Full type hints on all function signatures
- Use `Annotated[]` for dependency injection metadata
- Return type annotations on all route handlers
```

### Django Rules

```yaml
---
description: "Django 5.1+ conventions — class-based views, ORM patterns, migrations discipline"
alwaysApply: false
globs: ["**/models.py", "**/views.py", "**/serializers.py", "**/migrations/**"]
---

## ORM
Django's ORM is powerful but its default behavior — lazy evaluation and implicit related object loading — is the primary source of N+1 query bugs in Django applications. When the AI generates code that iterates over a QuerySet and accesses a related object inside the loop without explicit prefetching, each iteration triggers a separate database query. On small datasets this is invisible; on production datasets it causes severe performance degradation. The rule is simple: every access to a related object must be preceded by `select_related()` for foreign keys or `prefetch_related()` for many-to-many and reverse relations. QuerySets should be evaluated in views or serializers, not inside model methods, because model methods are called repeatedly in loops and should remain query-free. Bulk operations replace per-instance saves inside loops and reduce database round trips from N to 1.
- Use `select_related()` and `prefetch_related()` explicitly — never rely on lazy loading in loops
- QuerySets are lazy — don't evaluate in model methods, evaluate in views or serializers
- Bulk operations: use `bulk_create()` and `bulk_update()` for multi-record writes

## Migrations
Django migrations are the authoritative record of database schema history — editing a migration after it has been applied to any shared environment breaks the migration graph and can cause `migrate` to fail or silently skip changes on other developers' machines and deployment environments. Each migration should represent one logical schema change so that rollbacks are targeted and the migration history remains readable as a changelog of intentional decisions. Combined schema and data migrations are particularly dangerous because they cannot be rolled back atomically: if a data migration fails partway through, the schema change may already be applied. Reverse migrations — the `reverse_sql` or reverse `operations` list — are required for every migration so that `migrate --backwards` works predictably. Teams that skip reverse migrations accumulate technical debt that makes emergency rollbacks impossible.
- Never edit migrations after they've been applied to staging or prod
- Each migration does one logical thing — no combined schema + data migrations
- Reverse migration (`operations` list) required for every migration

## Security
Django ships with CSRF protection enabled globally by default, and this default must be preserved — disabling it per-view is a security vulnerability, not a convenience. When a view requires CSRF exemption (e.g., a webhook endpoint with its own signature verification), the exemption must be documented with a comment explaining the alternative protection mechanism. User input must flow through `ModelForm` or Django REST Framework serializers, which enforce field-level validation, type coercion, and model-level constraints before any data reaches the database or business logic layer. Raw `request.POST` access bypasses all of these protections and is a common vector for mass assignment vulnerabilities, where an attacker submits extra fields that modify sensitive model attributes the developer did not intend to expose through that endpoint.
- CSRF protection enabled globally — no per-view exemptions without comment
- User input through `ModelForm` or DRF serializer — no raw `request.POST` access
```

## Organizing Rules for Complex Projects and Monorepos

Monorepo rule organization uses Cursor's support for nested `.cursor/rules/` directories — each package can have its own rules that auto-attach when files in that package directory are in context. This is the recommended structure for projects with multiple frameworks or distinct service boundaries. A frontend service and a backend service should never share the same framework rules; nested directories ensure they don't. The 5-level organization system used by experienced Cursor teams (2026) places rules at: global, project-root, package-root, feature-area, and file-type levels. Global rules (`alwaysApply: true`) sit at the root; package-specific rules sit inside each package directory. Cursor resolves rules by walking up the directory tree from the active file, so package-level rules always take precedence over root-level rules for files in that package.

**Recommended directory structure:**

```
.cursor/
  rules/
    core.mdc          # alwaysApply: true — global constraints
    security.mdc      # alwaysApply: true — security policies
    git.mdc           # alwaysApply: true — commit conventions

packages/
  web/
    .cursor/
      rules/
        nextjs.mdc    # Auto Attached to app/**/*.tsx
        testing.mdc   # Auto Attached to **/*.test.tsx
  api/
    .cursor/
      rules/
        fastapi.mdc   # Auto Attached to **/*.py
        openapi.mdc   # Agent Requested — API schema conventions
```

**Key principles:**
- One `.mdc` file per concern — not one file per layer
- Keep each rule file under 500 lines
- Prefix filenames for clarity: `always-`, `auto-`, `agent-` corresponding to activation mode

## Team Sharing and Version Control Best Practices

Committing `.cursor/rules/` to Git is the correct approach for team-wide rule enforcement — it makes rules part of the codebase review process and ensures everyone uses the same AI configuration. As of 2026, Cursor's Team Rules dashboard lets organization admins define rules that propagate to all team members' instances, but project-level Git rules are still the primary governance mechanism for most teams. The workflow is: propose rule changes via PR, review in the same process as code changes, merge to main. This makes rules auditable and prevents one developer's configuration from silently differing from the rest of the team. For enterprises, coupling Cursor's Team Rules dashboard with Git-committed project rules provides two layers: organization-wide policies (security, compliance) managed centrally, and project-specific conventions managed by each team.

Add this to your `.gitignore` to keep the rules but exclude personal overrides:

```gitignore
# Keep project rules in Git
!.cursor/rules/

# Exclude personal Cursor settings
.cursor/settings.json
```

**Rule governance workflow:**
1. Developer notices AI making the same mistake three times — time to add a rule
2. Draft `.mdc` file with appropriate activation mode
3. Open PR with rule change, request review from team lead
4. Merge; rule takes effect on next Cursor session for all team members

## Token Budget Optimization: Keeping Rules Lean and Effective

Token budget optimization for Cursor rules means keeping the total `alwaysApply` rule content under 2,000 tokens combined — roughly 1,500 words — to avoid degrading model performance on complex requests. Every token in an always-apply rule is loaded into context for every conversation, regardless of relevance. This is the single most common performance mistake in Cursor rule configuration: developers add 5,000-token always-apply rules and wonder why the AI starts hallucinating on unrelated tasks. The fix is activation mode discipline: most rules should be Auto Attached or Agent Requested, not always-apply. Individual rule files should stay under 500 lines. The "200-word rule" for individual always-apply files is a practical ceiling — it forces you to prioritize the constraints that matter most and defer everything else to scoped rules.

**Token budget by activation mode:**

| Mode | Token Cost | When to Use |
|---|---|---|
| Always Apply | Every request | Universal constraints only — security, output format |
| Auto Attached | Matching requests only | Framework, language, file-type conventions |
| Agent Requested | When AI decides | Architecture docs, domain patterns |
| Manual | When you include it | Reference templates, migration guides |

**Optimization checklist:**
- Audit always-apply rules: anything over 200 words per file needs splitting
- Move framework rules to Auto Attached with precise globs
- Replace descriptive prose with bullet points — same semantic signal, fewer tokens
- Put the most important constraint first — AI attention is front-loaded

## Common Mistakes and How to Debug Rules Not Working

The most common reason Cursor rules stop working is the `.cursorrules` / Agent mode incompatibility: if you're using Cursor's agent (which became the default in 2026), the root `.cursorrules` file is silently ignored. The fix is migrating to `.cursor/rules/*.mdc`. The second most common cause is misconfigured globs — a glob of `**/*.tsx` written as `*.tsx` won't match files in subdirectories. The third is always-apply overload: when combined always-apply token count exceeds 2,000–3,000 tokens, the model's attention on those rules degrades measurably, causing it to skip constraints that appear later in the loaded content.

**Debugging steps:**
1. Open Cursor Settings → Rules — verify which rules are listed as active
2. Check the Composer/Agent context panel — loaded rules appear in the context summary
3. Test with `@ruleName` in chat to manually load a rule and confirm it applies
4. Check glob syntax: use [glob.js tester](https://globster.xyz/) to verify your patterns match intended files
5. Check total always-apply token count: paste all always-apply content into a tokenizer

**Common mistakes table:**

| Mistake | Symptom | Fix |
|---|---|---|
| Using `.cursorrules` with Agent mode | Rules silently ignored | Migrate to `.mdc` format |
| `alwaysApply: true` on large rules | AI skips constraints | Split into scoped rules |
| Wrong glob path (e.g., `*.tsx` not `**/*.tsx`) | Rule never attaches | Fix glob to include subdirectories |
| Duplicate rules across files | Conflicting behavior | Consolidate, keep one source of truth |
| No description on Agent Requested rules | AI never activates the rule | Write a specific, semantic description |

## Advanced Patterns: Rules That Write Rules

The "rule that writes rules" is a meta-rule that instructs Cursor to auto-generate new project-specific rules when it identifies patterns that should be standardized. This is an advanced technique used by senior engineering teams to let the AI help maintain the rule system rather than requiring manual rule authoring for every new pattern. The implementation is a single `.mdc` file with `alwaysApply: false` and a description that signals to the agent when to activate it. When the AI notices it has made the same correction three times in a conversation, or when a developer manually triggers it with `@rule-generator`, the meta-rule instructs the AI to draft a new `.mdc` file and propose it as a PR.

```yaml
---
description: "Rule generator: create new .mdc rules when a recurring pattern or correction is identified in the current session"
alwaysApply: false
---

When you identify a pattern that has been corrected or enforced more than twice in this session:

1. Propose a new `.mdc` rule file with this structure:
   - Filename: `auto-{concern}.mdc` in `.cursor/rules/`
   - Activation: Auto Attached with appropriate glob if file-type specific, Agent Requested otherwise
   - Content: bullet points, under 200 words, most important constraint first

2. Explain why this pattern warrants a rule (recurrence count, scope, impact)

3. Ask the developer to confirm before saving the file

The "3 strikes" threshold: if the same correction appears 3 times, propose a rule automatically.
```

This pattern transforms rules from a static configuration into a living documentation system that evolves with your project's actual patterns.

---

## FAQ

**Can I use both `.cursorrules` and `.cursor/rules/` at the same time?**

Yes, but with a caveat. In non-agent chat sessions, `.cursorrules` loads as normal. In Agent mode, `.cursorrules` is silently ignored and only `.mdc` rules apply. The safest approach during migration is to duplicate critical rules in both formats temporarily, then remove `.cursorrules` once you've confirmed the `.mdc` equivalents are working.

**How do I know if my rules are actually being loaded?**

Open the Composer or Agent panel and check the context summary — loaded rules are listed there. You can also type `@ruleName` to manually reference a specific rule and confirm it's readable. For Auto Attached rules, open a file matching the glob pattern and check the context panel again.

**What's the maximum number of `.mdc` files I can have?**

There's no documented hard limit. Practical constraint is total token count: all loaded rules (always-apply + auto-attached for current files) should stay under 4,000–6,000 tokens combined to avoid performance degradation. With focused, lean files under 200 words each, you can have 30+ rule files without hitting this ceiling.

**Should I commit `.cursor/rules/` to Git?**

Yes, for team projects. Rules are part of your project's development standards and should be reviewed, versioned, and applied consistently. Add `.cursor/settings.json` to `.gitignore` (personal settings) but keep the `rules/` directory tracked.

**How do Auto Attached globs work with monorepos?**

In a monorepo, place `.cursor/rules/` directories inside individual package directories. Globs in those files are relative to the directory containing the `.cursor/` folder. So `packages/web/.cursor/rules/nextjs.mdc` with glob `app/**/*.tsx` attaches when files matching `packages/web/app/**/*.tsx` are in context. Root-level `.cursor/rules/` files apply to the entire workspace.
