---
cover:
  alt: 'I Built a Linter That Catches Security Bugs AI Assistants Keep Writing'
  image: /images/linter-ai-security-bugs-2026.png
  relative: false
date: 2026-07-14T10:00:00+00:00
description: 'I scanned 132 AI-generated repos and found 27% had auth security bugs. So I built an open-source linter that catches what AI assistants systematically get wrong — OAuth, JWT, CORS, and session handling.'
draft: false
schema: schema-linter-ai-security-bugs-2026
tags:
- AI security
- linter
- static analysis
- OAuth
- DevSecOps
- open source
title: 'I Built a Linter That Catches Security Bugs AI Assistants Keep Writing'
---

I've been watching AI coding assistants write the same security bugs for two years. Not random bugs — the same predictable, systematic auth anti-patterns, over and over. So I built a linter that catches them before they ship.

Here's what I found when I scanned 132 AI-generated repositories: 27% had at least one authentication security finding. 18% had a HIGH+ severity finding. The most common pattern — non-constant-time secret comparison — showed up in 13% of repos. That's not a coincidence. That's a pattern.

## The Problem: AI Assistants Write Predictably Insecure Code

When you use an AI coding assistant daily, you start noticing the same mistakes. It's not that the code doesn't work — it usually does. The problem is that it works *insecurely*, and the insecurity follows a pattern.

I spent a few months cataloging what AI assistants get wrong in auth code. The list was depressingly consistent:

- **Non-constant-time secret comparison** (13% of repos): AI writes `if (user_input === secret)` instead of using `crypto.timingSafeEqual` or `hmac.compare`. This opens the door to timing attacks.
- **Auth tokens in browser storage** (8% of repos): AI stores JWTs in `localStorage` or `sessionStorage` instead of HTTP-only cookies. Any XSS vulnerability now leaks your auth tokens.
- **Session ID in URL** (8% of repos): AI appends session tokens as query parameters. They end up in server logs, referrer headers, and browser history.
- **Hard-coded API keys** (5% of repos): AI embeds secrets directly in source code. This one is so common I've stopped being surprised.

These aren't obscure vulnerabilities. These are OWASP Top 10, CWE-listed, well-documented anti-patterns. But AI assistants don't learn from security documentation — they learn from the training data, which is full of examples that work but aren't secure.

The deeper issue is that AI models optimize for *completion* — producing code that compiles and runs — not for *security*. A JWT stored in `localStorage` works perfectly in development. The security implications only surface in production, under attack.

## What I Built: A Linter That Catches What AI Keeps Getting Wrong

I built [OAuthLint](https://github.com/Auspeo/oauthlint) — a Semgrep-based linter with 160+ rules targeting OAuth, OIDC, JWT, session management, and CORS anti-patterns that AI tools systematically produce. It covers JavaScript/TypeScript, Python, Go, Rust, and Java, with dataflow (taint) analysis for tracking how secrets and tokens move through your code.

Why Semgrep? Because writing rules in Semgrep's pattern language is fast, and it supports cross-file dataflow analysis out of the box. I didn't want to build yet another AST walker — I wanted to write rules that express the actual security invariant being violated.

Here's what a rule looks like — catching non-constant-time secret comparison in Node.js:

```yaml
rules:
  - id: non-constant-time-secret-comparison
    patterns:
      - pattern: |
          if ($SECRET === $INPUT) { ... }
      - metavariable-regex:
          metavariable: $SECRET
          regex: (secret|token|key|password|hash|signature)
    message: >
      Non-constant-time comparison of $SECRET.
      Use crypto.timingSafeEqual() or a dedicated comparison function
      to prevent timing side-channel attacks.
    severity: HIGH
    languages: [javascript, typescript]
```

The rule is simple. The impact is not. A timing attack on a JWT secret can let an attacker forge tokens for any user.

For the more complex patterns — like auth tokens stored in browser storage — I used taint tracking:

```yaml
rules:
  - id: jwt-in-localstorage
    mode: taint
    pattern-sources:
      - pattern: |
          jwt.sign(...)
      - pattern: |
          jsonwebtoken.sign(...)
    pattern-sinks:
      - pattern: localStorage.setItem(...)
      - pattern: sessionStorage.setItem(...)
    message: >
      JWT token stored in browser storage.
      Use HTTP-only cookies instead to prevent XSS token theft.
    severity: HIGH
    languages: [javascript, typescript]
```

This catches the full flow: an AI generates a JWT on login, then stores it in `localStorage` 50 lines later. A simple regex linter would miss that. Taint analysis follows the data.

## The Research Behind It — What Bugs Actually Show Up

I didn't guess at the rules. I scanned 132 public GitHub repositories that were primarily AI-generated (identified through commit patterns, AI-generated file markers, and developer self-reporting). The results were worse than I expected.

**283 total auth anti-pattern findings** across 35 affected repositories. That's an average of 8.1 findings per affected repo. The distribution wasn't even — a handful of repos had 15+ issues, while most had 2-4.

The severity breakdown told the real story:

- **HIGH+ severity**: 18% of repos had at least one finding that could lead to account takeover, data breach, or privilege escalation.
- **MEDIUM severity**: Non-constant-time comparisons, missing CSRF tokens, permissive CORS policies.
- **LOW severity**: Verbose error messages exposing internals, missing security headers.

The most surprising finding? AI-generated code doesn't just make *different* mistakes than humans — it makes *more* of the same mistakes. A human developer who writes a JWT into `localStorage` once will probably learn not to do it again. An AI assistant will write it the same way every time, in every project, because it has no memory of the previous mistake.

This is backed up by broader research. A survey cataloged in the [AI coding code quality risks](/posts/ai-coding-code-quality-risks-2026/) analysis found that AI coding agents produce 8 primary bug categories: functional bugs, semantic errors, wrong logic, API misuse, type errors, hallucinated methods, arity mismatches, and duplicate logic. Misinterpretations — where the code deviates from the prompt intent — account for 20.77% of bugs. That's nearly a fifth of all AI-generated bugs being the model misunderstanding what you asked for.

## How It Works: From Regex to Dataflow Analysis

The linter uses three detection layers, each catching a different class of bug:

**Layer 1: Regex pattern matching** — Catches the obvious stuff: hard-coded API keys, `http://` URLs in auth flows, missing `secure` flags on cookies. Fast, cheap, runs in milliseconds. These rules are the low-hanging fruit.

**Layer 2: AST analysis** — Catches structural issues: missing `await` on async auth calls, incorrect middleware ordering in Express routes, missing CSRF token validation. These require understanding the code structure, not just string matching.

**Layer 3: Dataflow (taint) analysis** — Catches the subtle stuff: a secret generated in one function that ends up in a log statement 10 function calls later, a JWT that flows into `localStorage.setItem()` through a helper function. This is where Semgrep's engine shines.

The three layers are designed to be run in order. Layer 1 catches the obvious stuff immediately. Layer 2 catches structural issues. Layer 3 catches the bugs that would slip through code review.

Here's the CI configuration I use:

```yaml
# .github/workflows/oauthlint.yml
name: OAuthLint Security Scan
on: [push, pull_request]
jobs:
  oauthlint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: oauthlint/oauthlint-action@v1
        with:
          severity: HIGH
          languages: javascript,typescript,python
          fail-on: HIGH
```

The `fail-on: HIGH` flag means the CI pipeline blocks any PR with a HIGH severity finding. MEDIUM and LOW findings are reported but don't block — they're triaged in the PR review.

## Real Results: Catching Auth Bugs Before They Ship

Since I started running this on my own projects, I've caught:

- A JWT secret hard-coded in a config file that was about to be committed to a public repo.
- An OAuth callback URL that used `http://` instead of `https://` — the AI had copied the pattern from a local dev setup.
- A session management flow where the AI generated a new session token but never invalidated the old one (session fixation).
- A CORS policy that allowed `*` origins on an API that handled user authentication data.

Every single one of these was written by an AI assistant. Every single one would have shipped if the linter hadn't caught it.

The broader data backs this up. According to the [AI-generated code security statistics](/posts/ai-generated-code-security-statistics-2026/) from 2026, 45% of AI-generated code contains security vulnerabilities, and only 12% of organizations apply the same security standards to AI-generated code as they do to human-written code. That gap is where these bugs live.

## Integrating Into Your Workflow (CLI, CI, Editor)

The linter ships in three modes:

**CLI**: `npx oauthlint scan ./src` — runs all rules, outputs findings to stdout with file, line, severity, and a suggested fix. Good for local development and pre-commit hooks.

**GitHub Action**: The YAML snippet above. Blocks PRs with HIGH severity findings. I run this on every push to every branch.

**VS Code extension**: Inline annotations in the editor. When you're writing code and the AI suggests storing a token in `localStorage`, the extension underlines it in red before you even commit. This is the most effective mode because it catches bugs at the moment they're written, not hours later in CI.

The VS Code extension is the one I'd recommend most strongly. The feedback loop is instant — you see the security issue while you're still in the flow, not when you're waiting for a CI pipeline.

## Beyond Auth: The Broader Landscape of AI-Specific Linters

OAuthLint isn't the only tool in this space. The rise of dedicated AI-code linters signals a new category in developer tooling:

- **[Hallint](https://github.com/Asyncinnovator/hallint)** — An open-source TypeScript linter with 8 rules covering hardcoded secrets, SQL injection, unsafe eval, missing auth checks, XSS via innerHTML, permissive CORS, async without catch, and HTTP instead of HTTPS. It uses the same three-layer approach (regex, AST, optional LLM semantic review) and exits with code 1 on critical/high findings.

- **[Vouch](https://c-tonneslan-portfolio.vercel.app/writing/vouch-linter-for-ai-bugs)** — A Go CLI linter that detects AI hallucination patterns in build errors. It categorizes bugs as undefined-symbol, undefined-method, arity-mismatch, and type-mismatch — all by parsing `go build` output. No language server, no AST walking, no LLM needed. Just regex on build output. It's brutally simple and effective.

- **AINAScan** — A broader security scanner that includes AI-specific rules alongside traditional SAST checks.

The common thread: these tools are all open-source, free, and focused on a narrow, well-defined problem. They're not trying to replace SonarQube or Checkmarx. They're filling a specific gap that those tools don't address — the predictable, systematic bugs that AI assistants produce.

For a broader comparison of enterprise SAST tools, see the [AI code security scanning tools 2026](/posts/ai-code-security-scanning-tools-2026/) guide.

## Why Traditional Linters Aren't Enough

I ran the same 132 repos through ESLint's security plugin and Semgrep's default rule set. Here's what happened:

- ESLint's security plugin caught the hard-coded API keys and the `http://` URLs. It missed the JWT-in-localStorage pattern (no taint tracking) and the non-constant-time comparisons (no dataflow analysis).
- Semgrep's default rules caught more, but they're generic — they flag any use of `localStorage.setItem()` as a potential issue, which generates too many false positives to be useful. The AI-specific rules need to be tuned to the patterns AI assistants actually produce.

The difference is specificity. A generic SAST tool flags *all* uses of `localStorage` for auth tokens. An AI-specific linter flags the specific pattern where an AI assistant generates a JWT and stores it in `localStorage` in the same function — which is almost always a bug. The false positive rate drops from "annoying" to "negligible."

This is the same conclusion reached by the [AI code security debt crisis](/posts/ai-code-security-debt-crisis-2026/) analysis: AI-generated code contains 2.74x more vulnerabilities than human code, and traditional security tooling wasn't designed for the specific failure modes of LLM-generated code.

## Getting Started with Your Own AI-Specific Linting

You don't need to build a linter from scratch. Here's the minimal setup I'd recommend for any team using AI coding assistants:

1. **Install OAuthLint** (or Hallint, or both) in your CI pipeline. Set `fail-on: HIGH` and let MEDIUM/LOW findings be advisory.
2. **Add the VS Code extension** so developers see issues inline while coding.
3. **Write 3-5 custom rules** for the specific AI bugs your team has seen. Semgrep's rule language is straightforward — most rules are 10-20 lines of YAML.
4. **Run it on every PR**. Don't make it optional. If the linter blocks a PR, the developer fixes the issue before merging.

The ROI is immediate. Every bug caught by the linter is a bug that didn't need a security review, didn't need a hotfix, and didn't end up in a CVE report.

If you're using AI coding assistants in production — and most teams are — you need AI-specific linting. The bugs are predictable. The tools are free. The only question is whether you catch them before or after they ship.

---

*OAuthLint is MIT-licensed and available on [GitHub](https://github.com/Auspeo/oauthlint). Contributions welcome — especially rules for languages and frameworks I haven't covered yet.*
