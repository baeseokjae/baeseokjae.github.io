---
cover:
  alt: 'Cursor Rules Guide 2026: How to Write .cursorrules and .mdc Files for Your
    Project'
  image: /images/cursor-rules-guide-2026.png
  relative: false
date: 2026-04-18 15:29:10+00:00
description: 'Complete guide to writing Cursor rules in 2026: .cursorrules vs .mdc
  format, four activation modes, ready-to-use templates, and token budget tips.'
draft: false
schema: schema-cursor-rules-guide-2026
tags:
- cursor
- cursor rules
- ai coding
- developer tools
- IDE configuration
title: 'Cursor Rules Guide 2026: How to Write .cursorrules and .mdc Files for Your
  Project'
---

Cursor rules are project-level instructions that persist across every AI conversation in your editor — write them once and every Cursor session, every team member, and every new chat starts with your coding standards already loaded. Without rules, you repeat yourself every session; with them, the AI learns your stack once.

## What Are Cursor Rules and Why Do They Matter in 2026?

Cursor rules are configuration files that instruct the Cursor AI coding assistant how to behave within a specific project — defining your tech stack, coding style, naming conventions, and architectural preferences so you never have to re-explain them in each chat session. Cursor surpassed 1 million total users by late 2025, with 360,000+ paying subscribers and a $29.3 billion valuation after a $2.3B Series D round. At that scale, the context persistence problem became critical: teams found that without shared rules, every developer was training the AI differently, producing inconsistent output. Rules solve this by encoding your standards into the project repository itself. According to the 2025 Stack Overflow Developer Survey, 84% of developers now use or plan to use AI coding tools — up from 76% the year before — and Cursor is used by tens of thousands of teams at Nvidia, Adobe, Uber, Shopify, Stripe, and OpenAI. The takeaway: rules aren't optional polish; they are the mechanism that makes AI coding consistent and collaborative at team scale.

### Why the Old .cursorrules File Is No Longer Enough

The original `.cursorrules` single-file format loaded everything, every time — there was no scoping, no conditional activation, and no way to apply different instructions to frontend versus backend code. Teams ended up with one giant file that wasted tokens on irrelevant instructions. The modern `.cursor/rules/` directory with `.mdc` files solves this by letting you scope each rule to specific file patterns, activation conditions, or manual triggers.

## Understanding the Two Formats: .cursorrules vs .cursor/rules/*.mdc

The Cursor ecosystem currently supports two configuration formats: the legacy `.cursorrules` single file and the recommended `.cursor/rules/` directory containing `.mdc` files. The legacy format is a plain text or markdown file placed at the project root — simple to write, but it loads unconditionally in every request, burning tokens regardless of context. The modern `.mdc` format is a markdown file with YAML frontmatter that controls when and how the rule activates. Each `.mdc` file handles one concern: a separate file for React components, another for API routes, another for testing conventions. This modularity means a backend-only change doesn't load your frontend styling rules, saving hundreds of tokens per request. The `.cursor/rules/` directory was introduced as the recommended format to give teams the scope control that the original single-file approach couldn't provide. If you're starting a new project in 2026, go straight to `.mdc` files. If you have an existing `.cursorrules` file, migrate it by splitting it into topic-based `.mdc` files with appropriate glob patterns — the migration is mechanical and pays off immediately in token efficiency.

### Quick Migration Checklist

- Create `.cursor/rules/` directory at project root
- Split your `.cursorrules` into themed files (e.g., `react-components.mdc`, `api-routes.mdc`, `testing.mdc`)
- Add YAML frontmatter to each file with `alwaysApply: false` and appropriate `globs`
- Delete the old `.cursorrules` file
- Commit `.cursor/rules/` to version control so the whole team shares the same configuration

## The Anatomy of an .mdc Rule File

An `.mdc` rule file consists of two parts: a YAML frontmatter block that controls activation, and a markdown body that contains the actual instructions. The frontmatter has three key fields: `description` (a one-sentence summary the AI uses when deciding whether to apply agent-requested rules), `globs` (file patterns that trigger Auto/Glob activation), and `alwaysApply` (a boolean that forces the rule into every request when set to `true`). The markdown body is free-form — use headings, bullet lists, code blocks, and examples. Write instructions in the imperative voice: "Use TypeScript strict mode," not "TypeScript strict mode is preferred." Here is a minimal example for a React project rule file named `.cursor/rules/react-components.mdc`:

```yaml
---
description: React component conventions for this project
globs: ["src/components/**/*.tsx", "src/pages/**/*.tsx"]
alwaysApply: false
---

## React Component Rules

- Use functional components with hooks only. NEVER use class components.
- Export components as named exports, not default exports.
- Props interface name must match component name: `ButtonProps` for `Button`.
- Use Tailwind CSS utility classes. Do NOT write inline styles.
- Co-locate component tests in the same directory as the component file.
- Import order: React → third-party libraries → internal modules → styles.
```

The rule activates automatically when the user opens or edits any file matching `src/components/**/*.tsx` or `src/pages/**/*.tsx` — and stays dormant (saving tokens) for all other file types.

## Four Rule Activation Modes Explained

Cursor supports four distinct activation modes, each suited to a different type of coding standard. Understanding which mode to use is the single biggest factor in building an efficient, non-bloated rule configuration. The four modes are: **Always Apply**, **Auto Attached (Glob)**, **Agent Requested**, and **Manual**. Always Apply rules load in every single AI request — use this mode only for the most universal constraints like "write all code in TypeScript" or "never commit secrets to source files." Keep Always Apply rules under 200 words; every token they contain is charged against your context window on every request, which practitioners call the "token tax." Auto Attached rules trigger based on file patterns (globs) — they activate when the AI is working on a file that matches the pattern, making them ideal for framework-specific conventions like React component rules or database query patterns. Agent Requested rules include a `description` field that the AI reads to decide whether the rule is relevant to the current task — useful for specialized rules like security review checklists or performance optimization patterns. Manual rules are never applied automatically; they must be explicitly referenced with an `@rule-name` mention in the chat — ideal for infrequently used templates like a PR description format or a release checklist.

### Choosing the Right Mode

| Mode | When It Applies | Best For | Token Cost |
|------|----------------|----------|-----------|
| Always Apply | Every request | Universal constraints (language, secrets policy) | High — minimize |
| Auto Attached | File pattern match | Framework conventions, file-type rules | Medium |
| Agent Requested | AI decides | Optional patterns, specialized checklists | Low |
| Manual | Explicit @mention | Templates, one-off procedures | Zero unless referenced |

## Writing Your First Cursor Rules: A Step-by-Step Walkthrough

Writing effective Cursor rules follows a clear sequence: identify recurring friction, encode the fix precisely, and verify the AI applies it correctly. Start by observing where the AI makes the same mistake twice — that repetition is your signal that a rule is needed. Day one developers often write 20 rules before they've used the tool; experienced teams add rules incrementally as actual problems emerge. Here is a concrete walkthrough for a Next.js project. First, create the rules directory: `mkdir -p .cursor/rules`. Second, create your always-on global rule in `.cursor/rules/global.mdc` with `alwaysApply: true` — limit this to two or three universal constraints. Third, create a framework-specific rule in `.cursor/rules/nextjs.mdc` with a glob pattern targeting `src/**/*.tsx` and `src/**/*.ts`. Fourth, test by opening a component file and asking Cursor to generate a new component — verify it follows your conventions without prompting. Fifth, commit the `.cursor/rules/` directory to git so teammates inherit the same behavior immediately.

### Practical Example: Catching the Same Mistake

If Cursor keeps generating `console.log` statements in production code, add this to your global rule:

```
NEVER use console.log, console.warn, or console.error in production code.
Use the project logger at `src/lib/logger.ts` for all logging.
Reference the `logError` and `logInfo` functions — see the pattern in `src/lib/logger.ts`.
```

Notice three things: the `NEVER` keyword (strong language outperforms "prefer"), the reference to an actual file instead of copied code, and the function names so the AI knows exactly what to use.

## Framework-Specific Rule Templates

Ready-to-use rule templates save hours of trial-and-error and can be adapted to match your project's conventions within minutes. The most effective templates are scoped precisely by file pattern, kept under 60 lines per rule file, and reference actual files in the codebase rather than embedding large code blocks. Below are battle-tested starting points for three common stacks.

### React / Next.js Template

Save as `.cursor/rules/react-nextjs.mdc`:

```yaml
---
description: React and Next.js coding conventions
globs: ["src/**/*.tsx", "src/**/*.ts", "app/**/*.tsx", "app/**/*.ts"]
alwaysApply: false
---

## React / Next.js Rules

- App Router only. NEVER use Pages Router patterns.
- Server Components by default. Add 'use client' only when you need browser APIs or event handlers.
- Data fetching in Server Components using async/await — no useEffect for data fetching.
- Use `next/image` for all images. NEVER use raw `<img>` tags.
- Tailwind CSS for styling. No CSS modules, no styled-components.
- TypeScript strict mode. No `any` types without an explicit comment explaining why.
- Error boundaries with `error.tsx` files, loading states with `loading.tsx`.
- Use `zod` for all runtime validation — define schemas in `src/lib/schemas/`.
```

### Python / FastAPI Template

Save as `.cursor/rules/python-fastapi.mdc`:

```yaml
---
description: Python and FastAPI conventions for backend services
globs: ["**/*.py"]
alwaysApply: false
---

## Python / FastAPI Rules

- Python 3.12+. Use `match` statements over complex if/elif chains.
- Pydantic v2 models for all request/response schemas. No dict returns from endpoints.
- Async endpoints with `async def` everywhere. NEVER mix sync and async handlers.
- Dependency injection via FastAPI `Depends()` — see patterns in `src/dependencies.py`.
- Use `ruff` formatting rules (line length 88). NEVER use bare `except:` clauses.
- SQLAlchemy 2.0 ORM with `AsyncSession`. Transactions scoped to request lifecycle.
- All environment variables via `pydantic-settings` BaseSettings — see `src/config.py`.
- Type hints required on all function signatures and return types.
```

### Full-Stack (Next.js + Supabase) Template

Save as `.cursor/rules/supabase.mdc`:

```yaml
---
description: Supabase database and auth patterns
globs: ["src/lib/supabase/**", "src/app/api/**", "src/**/*supabase*"]
alwaysApply: false
---

## Supabase Rules

- Use the server-side Supabase client from `src/lib/supabase/server.ts` in Server Components.
- Use the browser client from `src/lib/supabase/client.ts` in Client Components only.
- NEVER expose the service role key client-side. All admin operations go through API routes.
- Row Level Security is enabled — test queries with the authenticated user context, not the service role.
- Use `supabase.from('table').select()` with explicit column lists. NEVER use `select('*')` in production.
```

## Advanced: Organizing Rules for Large Projects

Large projects with multiple distinct layers — frontend, backend, infrastructure, testing — need a hierarchical rule organization strategy to avoid token bloat and rule conflicts. The recommended approach is to create one rule file per concern, scope each file tightly with glob patterns, and use a single short `global.mdc` with `alwaysApply: true` for the handful of truly universal constraints. A well-organized `.cursor/rules/` directory for a mid-size full-stack application might look like this: `global.mdc` (always on, under 150 words), `react-components.mdc` (glob: `src/components/**`), `api-routes.mdc` (glob: `src/app/api/**`), `database.mdc` (glob: `src/lib/db/**`, `prisma/**`), `testing.mdc` (glob: `**/*.test.ts`, `**/*.spec.ts`), `security.mdc` (agent-requested, triggered by security-sensitive tasks). This structure means that when the AI is writing a React component, it loads `global.mdc` and `react-components.mdc` — and nothing else. When writing API routes, it loads `global.mdc` and `api-routes.mdc`. The testing conventions never pollute a component generation task.

### Team Conventions for Version-Controlled Rules

Commit `.cursor/rules/` to your main branch and treat rule files like any other code — require review for changes, use descriptive commit messages, and document breaking changes in the PR description. When a rule is added to fix a recurring AI mistake, reference the rule file in your PR description so future reviewers understand why the constraint exists.

## The Token Budget: Why Rule Length Matters and How to Optimize

Every token in a Cursor rule file is loaded into the context window before your prompt — which means long rules directly reduce the number of tokens available for your actual code and conversation. A 1,000-line rule file consumes 2,000+ tokens before the model reads a single word of your request. For Always Apply rules, the cost is paid on every single request; for Auto Attached rules, the cost is paid every time a matching file is open. The recommended ceiling is 200 words for Always Apply rules and 500 lines total per rule file. Practical token optimization follows three principles. First, reference files instead of copying code: "Follow the pattern in `src/components/Button.tsx`" costs 12 tokens; copying the Button component into the rule file might cost 400. Second, write directives, not explanations: "Use named exports" (4 tokens) is better than a paragraph explaining why named exports are preferable (40+ tokens). Third, delete rules that no longer apply — outdated rules are both token-wasteful and actively harmful if the AI follows a deprecated pattern.

### Token Cost Comparison

| Rule Length | Token Cost | Context Window Impact |
|-------------|-----------|----------------------|
| 50 words (Always Apply) | ~75 tokens | Negligible |
| 200 words (Always Apply) | ~300 tokens | Acceptable ceiling |
| 1,000 lines (Always Apply) | 2,000+ tokens | Severely degrades performance |
| 500 lines (Auto Attached) | ~1,000 tokens | Acceptable for scoped rules |

## Common Mistakes That Make Cursor Rules Fail

The most common Cursor rule mistakes share a pattern: they're vague where they should be precise, they load everything when they should scope carefully, and they embed code that belongs in source files. Understanding these failure modes helps you write rules that actually change AI behavior rather than rules that get ignored or cause worse output. The six most damaging mistakes are: using weak language ("prefer," "consider," "try to"), missing library version specificity (the AI mixes Next.js 13 and 14 syntax without a version anchor), copying code blocks instead of referencing files (stale code in rules is worse than no code), writing Always Apply rules that exceed 200 words (token tax compounds across every request), writing vague scope that applies rules to unrelated files (a React rule that also loads for Python files), and writing rules before observing actual AI mistakes (premature rules add noise without solving real problems). The fix for each failure is mechanical: replace "prefer" with "NEVER" or "ALWAYS," add version numbers explicitly, replace code blocks with file references, trim Always Apply rules to under 200 words, tighten glob patterns, and delete rules that were written speculatively rather than in response to observed behavior.

### Before vs. After: Fixing a Weak Rule

**Weak (will often be ignored):**
```
Try to use TypeScript where possible and consider using functional components.
```

**Strong (reliably applied):**
```
ALWAYS use TypeScript. NEVER use JavaScript files (.js) — create .ts or .tsx only.
NEVER use class components. Use functional components with hooks exclusively.
```

## Cursor Rules vs Other AI Config Files

Understanding where Cursor rules fit among other AI configuration formats helps teams working across multiple tools avoid duplication and conflicting instructions. The four main formats in 2026 are: `.cursor/rules/*.mdc` (Cursor-specific, project-scoped), `CLAUDE.md` (Claude Code-specific, directory-aware), `copilot-instructions.md` (GitHub Copilot, repository-scoped), and `.windsurfrules` (Windsurf IDE). Cursor rules and CLAUDE.md serve similar purposes but are read by different tools — Cursor ignores CLAUDE.md and Claude Code ignores `.cursor/rules/`. Teams using both tools maintain separate files, though the content often overlaps substantially. The key difference is activation mechanism: Cursor rules have four modes (Always Apply, Glob, Agent Requested, Manual), while CLAUDE.md is always loaded for the directory where it's placed. Copilot instructions (`github/copilot-instructions.md`) apply repository-wide with no scoping mechanism — a single file for all contexts. `.windsurfrules` follows the legacy single-file pattern similar to the old `.cursorrules`. For teams standardizing on Cursor, `.mdc` files offer the most granular control of any format in the current ecosystem.

| File | Tool | Scope Control | Activation Modes | Version Control |
|------|------|--------------|-----------------|-----------------|
| `.cursor/rules/*.mdc` | Cursor | Per-file glob | 4 modes | Yes |
| `CLAUDE.md` | Claude Code | Directory-aware | Always loaded | Yes |
| `copilot-instructions.md` | GitHub Copilot | Repo-wide only | Single mode | Yes |
| `.windsurfrules` | Windsurf | Project-wide | Single mode | Yes |
| `.cursorrules` (legacy) | Cursor | Project-wide | Always loaded | Yes |

## Best Practices Summary

Effective Cursor rules follow a consistent set of principles that experienced teams converge on after trial and error. Write rules reactively, not speculatively: add a rule only when the AI repeats the same mistake twice. Use strong imperative language: "NEVER," "ALWAYS," and "MUST" outperform "prefer," "consider," and "try to." Reference files, don't embed code: `"Follow the pattern in src/components/Button.tsx"` is more maintainable than copying the component into the rule. Keep Always Apply rules under 200 words to control the token tax. Scope Auto Attached rules tightly with precise glob patterns. Commit `.cursor/rules/` to version control so the entire team shares identical AI behavior — treat rule changes like code changes, with review and clear commit messages. Delete outdated rules promptly; a stale rule is worse than no rule because the AI will follow deprecated patterns. Finally, test each rule by asking Cursor to generate code that the rule should influence, and verify the output matches your expectations before shipping the rule to the team.

---

## FAQ

**What is the difference between .cursorrules and .mdc files?**

`.cursorrules` is the legacy single-file format that loads unconditionally in every request — it has no scoping, no activation modes, and consumes tokens even when irrelevant to the current task. `.mdc` files in the `.cursor/rules/` directory are the modern format, supporting YAML frontmatter that controls whether the rule always loads, loads for specific file patterns, loads when the AI deems it relevant, or loads only when manually referenced. For any project started in 2026, use `.mdc` files exclusively.

**How long should my Cursor rules be?**

Always Apply rules should stay under 200 words — every word costs tokens on every single request. Auto Attached rules (triggered by file patterns) can be up to 500 lines, since they only load when relevant files are open. Agent Requested and Manual rules have less strict limits but should still be under 300 lines for readability and response quality. If a rule file is getting long, split it into multiple topic-specific files with tighter glob scopes.

**Should I commit .cursor/rules/ to version control?**

Yes, always. The `.cursor/rules/` directory should be committed to your main branch and treated like any other code. Version-controlling your rules means new team members get the same AI behavior immediately, rule changes go through code review, and you can track when and why rules were added or removed. Add a note to your project's README or onboarding docs explaining that Cursor rules live in `.cursor/rules/`.

**How do I know when to add a new Cursor rule?**

Add a rule when the AI makes the same mistake twice in the same project context. One occurrence might be a prompt issue; two occurrences signals a missing rule. Avoid writing rules speculatively on day one — teams that write 20 rules before using the tool create token bloat without solving real problems. Start with a minimal `global.mdc` (2-3 constraints, under 150 words) and add rules as you observe friction.

**Can I use Cursor rules with Claude Code or GitHub Copilot?**

No. Cursor rules (`.cursor/rules/*.mdc` and the legacy `.cursorrules`) are read only by Cursor. Claude Code reads `CLAUDE.md` files, and GitHub Copilot reads `github/copilot-instructions.md`. If your team uses multiple AI tools, you'll need to maintain separate configuration files for each — though the content often overlaps, so you can write one set of standards and adapt the format for each tool.