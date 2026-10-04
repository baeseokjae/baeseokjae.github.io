---
title: 'Openleetcode Review: A Local LeetCode Runner With the Tests in the Repo'
date: 2026-10-01T02:59:00+00:00
tags:
  - Openleetcode
  - local LeetCode runner
  - LeetCode test cases
  - competitive programming tools
  - Piston execution backend
  - Haskell CLI
  - leetcode-cli alternative
description: "Openleetcode is a free local LeetCode runner that ships 1,410 open test manifests in its repo, so you judge solutions offline with no account or API."
draft: false
cover:
  image: "/images/openleetcode-local-leetcode-runner.png"
  alt: "Openleetcode Review: A Local LeetCode Runner With the Tests in the Repo"
  relative: false
schema: "schema-openleetcode-local-leetcode-runner"
---

Openleetcode is a free, open-source runner for LeetCode problems that executes your solution on your own machine. Its distinguishing feature is that the judge inputs live in the repository: 1,410 problem manifests with their expected outputs are published as a versioned, forkable artifact, so nothing is submitted to LeetCode and no account is required.

## What Is Openleetcode and How Does It Differ From Other LeetCode CLIs?

Openleetcode is a command-line tool written in Haskell that takes a solution file, matches it to a problem manifest, runs it through a small language-specific harness, and grades the result against test cases that ship with the tool. The author's own framing is that the [CLI is "just the glue"](https://github.com/therepanic/openleetcode) — the interesting artifact is the test corpus underneath it.

That framing is the whole product thesis. LeetCode's judge is closed. You submit, you get a verdict, and if you fail on input #47 you generally are not shown input #47. Every mainstream LeetCode CLI inherits that black box, because every mainstream LeetCode CLI is really an authenticated HTTP client for the same judge:

| | Openleetcode | leetcode-cli | leetcode.nvim | leetgo |
|---|---|---|---|---|
| Judge location | Local (Piston in Docker) | LeetCode's server | LeetCode's server | Local, plus optional submit |
| Test cases public | Yes, 1,410 manifests in-repo | No | No | No (built from statement examples) |
| Requires an account | No | Yes | Yes | Only to submit |
| Requires network to grade | No | Yes | Yes | No |
| Primary language | Haskell (Cabal) | JavaScript | Lua | Go |
| Approx. stars | 170 | 3,873 | 2,204 | 707 |
| License | Unlicense | MIT | MIT | MIT |

As checked on 2026-10-01, therepanic/openleetcode shows 170 stars, 6 forks and 11 open issues, was created on GitHub on 2026-01-12, last pushed 2026-09-04, and cut release v1.0.4 on 2026-08-17. It is a young, single-maintainer project — not a 4,000-star incumbent — and it should be evaluated that way.

## Why Does It Matter That the Test Cases Live in the Repo?

Because closed test suites are the single most frustrating property of online judges, and openleetcode is one of the very few tools that removes it.

The author says it directly: closed platforms never publish their test cases, and he explicitly rejected the "submit through the LeetCode API" approach that other tools take. That rejection has mechanical consequences. When you fail locally with openleetcode, you can open `tests/{problem}/manifest.yaml`, read the failing input, and add a print statement. When you fail with leetcode-cli, you get the same verdict LeetCode would have given you in the browser, minus the browser.

The second benefit is offline grading. Once Piston has installed the runtimes, judging happens on `localhost` — no network, no login token, no rate limits, no risk of a stray submission landing on your public profile. That matters for interview preparation on a plane, in a locked-down corporate network, or simply when you want to iterate fifty times in ten minutes without worrying about being throttled.

The third benefit is that the corpus is an artifact you can own. Fork it, add your own edge cases to a manifest, keep a private branch for the problems you actually study. No other tool in this niche gives you that, because no other tool has the tests to give.

## How Many LeetCode Problems Are Actually Covered?

Openleetcode ships **1,410 manifests**. LeetCode hosts **4,069 problems** in total as of 2026-10-01 per its own problems API — 3,284 free and 785 paid-only, split across 968 easy, 2,122 medium and 979 hard.

That puts coverage at roughly **34.6% of the entire problem set** and about **43% of the free-tier set**. The repository badge reads "1.4k", which matches the count of `manifest.yaml` files under `tests/` (the `tests/` tree holds 19,703 files in total, so the manifests are a small fraction of a much larger data directory).

What that means in practice:

- The famous problems are well covered. If you are grinding a curated list, a large share of it is likely present.
- Premium problems are explicitly out of scope. If you pay for LeetCode Premium, a good chunk of your paid content cannot be run here.
- Some categories are absent entirely. There is no support yet for Concurrency, Shell, SQL, Database, Design, or In-Place problems. Those are structural gaps, not a coverage shortfall — the manifest format does not model them today.

The honest framing is that this is a strong coverage number for a project nine months old and a weak one if you expect a drop-in replacement for the site.

## How Do You Install Openleetcode?

Docker is a hard prerequisite on Linux and macOS, and this is the part that surprises people.

The flow is:

1. Clone the repository.
2. Start the execution backend with Docker Compose (`engineer-man/piston` listening at `http://localhost:2000`).
3. Wait. The first backend start installs every supported language runtime, and it is slow.
4. Build the Haskell CLI with Cabal.
5. Run a problem and watch it grade locally.

The Piston dependency is worth understanding rather than treating as an implementation detail. Piston is the sandboxed execution engine — the same class of tool as [judge0](https://github.com/judge0/judge0) — and it exists precisely because running arbitrary submitted code unsandboxed is a bad idea. By defaulting to Piston over Docker, openleetcode inherits a mature sandbox instead of writing its own. That is the right engineering call, and it is also why "just run it locally" is not as trivial as it sounds: you are standing up a containerised judge.

Twelve language runtimes are supported: C++, Rust, Python 3, Python 2, Ruby, Java, C#, Kotlin, Go, Dart, Swift and TypeScript. The runtime templates deliberately mirror the official LeetCode environments so the harness you test against behaves like the one you would eventually submit to. Python 2 is a historical curiosity at this point, but its presence signals that the templates were copied from the platform's actual judge configuration rather than invented.

## How Does a Local Submission Actually Work?

The pipeline is a chain of small, inspectable steps:

**Solution file → matching manifest → language harness → execution backend → local judge.**

You keep your solution in a file that corresponds to a problem, openleetcode finds the manifest for that problem, generates or selects a thin harness for the language you chose, ships the code to Piston for execution, and compares the output to the expected results according to the manifest's rules. The Haskell CLI orchestrates; it does not contain the interesting logic.

This structure is why contributing to the corpus is unusually accessible. You do not need to read Haskell to add a test case — you need to write YAML. That split is intentional: the toolchain burden falls only on people changing the CLI itself, while the much larger surface area (1,410 manifests and growing) is open to anyone who understands a problem statement.

Test generation is likewise scriptable. Manifests support stress-test generation through a small DSL, so combinatorial and randomised testing is expressed as configuration rather than as bespoke code per problem.

## What Does a Test Manifest Look Like?

`TEST_FORMAT.md` is the contract, and it is the document to read first. A manifest is a YAML file with these fields:

- **`entry`** — how to call the solution, with per-language variants (a `params` form, or a `call` form for languages that need a different invocation).
- **`judge`** — the comparison strategy. `exact` demands byte-identical output; `ignore_order` accepts any ordering, which is what you want for problems whose answer is a set or a permutation.
- **`limits`** — `time_ms` and `memory_mb`, so each problem is judged against a declared budget rather than one global timeout.
- **`oracle`** — an optional Python 3 checker for problems where correctness cannot be expressed as a simple string comparison, such as "any valid answer" problems.
- **`seed`** — the random seed for generated cases, which is what makes a random test reproducible.
- **`tests`** — the cases themselves, either hand-written or generated.

Two design choices stand out. First, per-language `entry` definitions mean one manifest serves all twelve runtimes, so adding a language does not mean duplicating 1,410 files. Second, the judge is an enum plus an escape hatch: `exact` and `ignore_order` cover the common cases, and the oracle covers the rest. That is a pragmatic format rather than an over-engineered one.

The `limits` field is the subtle one. Because each manifest declares its own time and memory budget, a local run can approximate the platform's constraints — which is more than most local test setups do, and closer to what you actually need when a solution times out on LeetCode but passes your unit tests.

## Can You Contribute Without Writing Any Haskell?

Yes, and the project has built dedicated scaffolding for exactly that.

Three scripts carry most of the non-code contribution work:

- **`generate_prompt.py`** — produces the prompt used to draft a manifest for a problem.
- **`spartan.py`** — sends that prompt to an OpenRouter model and writes the drafted manifest into `generated_problems/`.
- **`molotov.py`** — fills in `sol.{lang}` solution stubs for those generated problems.

The author's own guidance about the model's output is refreshingly blunt: treat it "like a junior contributor with infinite patience." In other words, the LLM drafts, and a human reviews. The project states that generated manifests are very much in need of review, which means corpus quality is uneven by design — a deliberate trade of polish for throughput on a dataset that is otherwise too large to hand-write.

For anyone who has wanted to contribute to an open-source judge and bounced off the toolchain, this is the lowest-friction entry point in the project. You need a text editor and the ability to verify a problem statement, not a Cabal installation.

## What Are the Real Caveats?

**Uneven manifest quality.** The LLM-assisted pipeline above is the direct cause. Expect generated manifests to be correct on the happy path and thin on edge cases until someone reviews them. Cross-checking a manifest against the problem statement before trusting a verdict is reasonable diligence, not paranoia.

**Sync risk.** Problem statements on LeetCode rarely change, but edge cases do get patched. A manifest written in January may not reflect a hidden test added in September. The maintenance burden of a 1,410-problem corpus is real and ongoing, and the project's own stress-test DSL is partly a hedge against exactly this problem.

**Missing categories.** Concurrency, Shell, SQL, Database, Design and In-Place problems are not supported today. If your study plan leans on those, this tool will not cover it.

**Setup cost.** Docker, Piston, a slow first start, and a Haskell toolchain if you want to build the CLI yourself. That is a heavier install than `npm install -g leetcode-cli`, and the payoff is offline grading against public tests.

**Traction.** The Show HN launch on 2026-08-18 reached 73 points and 19 comments. Modest, but real — and the project was posted to Hacker News seven separate times between 2026-06-30 and 2026-08-18, which says something about the author's persistence as much as the audience's appetite. With 170 stars and 11 open issues, this is early-stage software. The 3,873-star leetcode-cli and the 2,204-star leetcode.nvim are more mature; the 707-star leetgo is more actively maintained, with a last push of 2026-09-24.

## Verdict: Who Should Actually Use Openleetcode?

Openleetcode is the right tool for a specific person: someone who prepares for interviews offline, wants to see the input that made their solution fail, and is willing to spend twenty minutes on Docker before the first problem runs.

It is the wrong tool if you want a one-command install, if you rely on Premium or SQL/Design problems, or if you need submission handled for you. For those cases, a mature API-driven client is the better answer — and the mature client's core advantage is simply that it has years of polish behind it.

The most useful way to think about openleetcode is as an open test corpus with a CLI attached. If that framing appeals to you, the 1,410 manifests are worth the setup. If it does not, no amount of CLI polish will make the Docker dependency worth it — and it is fair to say so plainly, because the install cost is the honest price of open tests.

## FAQ

**Does Openleetcode submit solutions to LeetCode?**

No. It grades everything locally against test manifests that ship in the repository. There is no API submission path, no authentication and no network call to LeetCode's judge. The author explicitly rejected the submit-via-API approach that other tools use.

**Do I need a LeetCode account to use it?**

No. Because grading happens locally through Piston, no account, session cookie or login token is involved. That also means your attempts never appear on a public profile.

**How many problems does Openleetcode cover?**

1,410 problems are covered by `manifest.yaml` files as of 2026-10-01, against 4,069 total LeetCode problems — about 34.6% of everything and roughly 43% of the free-tier set. Premium-only problems and the Concurrency, Shell, SQL, Design and In-Place categories are not supported yet.

**Is it safe to run untrusted code with Openleetcode?**

Yes, by inheritance rather than by invention. The default backend is Piston, a sandboxed execution engine that itself runs inside Docker on `localhost:2000`. The sandboxing is Piston's, not homegrown, and that is a point in the project's favour.

**Do I need to know Haskell to contribute test cases?**

No. Adding a problem means writing YAML against the manifest format documented in `TEST_FORMAT.md`, and the project ships `spartan.py` to draft manifests from prompts plus `molotov.py` to scaffold solution files. Haskell is only required if you want to modify the CLI itself.

**How does it compare to leetgo?**

Leetgo has more stars (707 vs 170), is written in Go, and is the most actively maintained tool in the group, with a last commit on 2026-09-24. Its local testing, however, is built from the example cases shown in the problem statement, not from a maintained open corpus. Openleetcode gives you a larger, editable, community-reviewed body of tests; leetgo gives you a smoother install and the option to submit.

**Why is the first run so slow?**

The first start of the Piston backend installs every supported language runtime — all twelve of them — and that install is a one-time cost. Subsequent runs reuse the installed runtimes and grade quickly.
