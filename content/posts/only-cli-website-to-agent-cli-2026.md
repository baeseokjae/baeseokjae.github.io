---
title: "only-cli (oc) 2026 Guide: Turn Any Website into a CLI Tailored for AI Agents"
date: 2026-09-20T19:01:32+00:00
tags:
  - AI Agents
  - CLI Tools
  - Token Optimization
  - Web Browsing
  - Developer Tools
description: "Turn any website into a compact numbered CLI with only-cli (oc) in 2026. Learn how AI agents browse the web in hundreds of tokens, not tens of thousands."
draft: false
cover:
  image: "/images/only-cli-website-to-agent-cli-2026.png"
  alt: "only-cli (oc) 2026 Guide: Turn Any Website into a CLI Tailored for AI Agents"
  relative: false
schema: "schema-only-cli-website-to-agent-cli-2026"
---

# only-cli (oc) 2026 Guide: Turn Any Website into a CLI Tailored for AI Agents

Agent tools waste most of their token budget on raw HTML markup that a model can never use. only-cli (oc) solves this by distilling any website into a compact, numbered CLI view that AI agents can drive by number, cutting token use by about 45x to 118x versus raw HTML. This guide covers what oc is, how to install it, wire it into Claude Code, Codex, Cursor, and Copilot, and how to handle logins and bot blocks safely.

## What is only-cli (oc) and Why Agents Waste Tokens on Raw HTML

The command line is arguably the agent's native interface. A large language model reads and writes text, and a CLI is the purest text-in, text-out surface available. When an agent needs real-world information from the web, however, the default is often a browser tool that returns the full rendered page — and that page is loaded with script tags, CSS, navigation menus, and boilerplate the model can't act on.

only-cli (oc) is an open-source command line tool that fetches a web page, distills it into compact text with numbered actions, and lets an agent drive the site by choosing a number. Instead of sending a 40,000-token HTML blob into context, oc sends a few hundred tokens and a short menu of numbered options. The agent picks `open`, `do`, `find`, `next`, `read`, or `raw` to move through a site exactly the way a human would — but with a fraction of the input cost.

This matters because the command line is where agents are most efficient. Firecrawl's "Why Is CLI?" position makes this case plainly: a model reads and writes text, and a CLI delivers the narrowest, most useful text surface for that model. oc applies that philosophy to the open web, turning an arbitrary website into a per-site CLI without per-site adapters.

## The Token Problem: How Much Markup Agents Throw Away

The waste is not theoretical. Industry analysis by dbhurley.com estimates that roughly 75 percent of HTML is noise for agent consumption, and that the average raw page costs about 33,181 tokens versus 8,301 tokens when fetched as structured content. Across the roughly 400 million user-action page fetches per day among major AI agents, that adds up to an estimated $1 billion to $5 billion per year spent processing web markup agents never use.

A developer-focused measurement from dev.to found that about 80 percent of an agent's token budget can be spent on HTML tags a model cannot use. Real examples include Cloudflare docs dropping from 9,541 raw tokens to 1,678 tokens as cleaned markdown (an 82 percent reduction) and a blog post falling from 16,180 tokens to 3,150. An agent fetching 50 pages per day is effectively pushing around 35 million tokens of raw HTML through context every month.

only-cli's own benchmarks point the same direction. On its official site, oc claims 1,444 tokens for four real pages that cost 65,372 tokens as raw HTML — roughly a 45x reduction. A Reddit thread that cost 52,899 tokens raw shrinks to 477 tokens through oc. The GitHub benchmark, measured on oc versions 0.5.1 to 0.5.3 in September 2026, shows 118x fewer tokens than raw HTML across 14 real pages (9,466 versus 1,119,003 tokens), 17x fewer than Jina Reader, and 54x fewer than a Playwright MCP accessibility snapshot.

## Install only-cli in 30 Seconds

Installation is a single command for most developers. oc runs on Node.js version 20 or newer and depends on only three runtime dependencies.

```
npm install -g @only-cli/oc
```

If you prefer not to install globally, you can run it on the fly with npm's runner:

```
npx @only-cli/oc --help
```

There is no daemon to keep running, no browser extension to manage, and no per-site adapters to install. The tool is MIT licensed and available from the only-cli GitHub repository at github.com/only-cli/oc, which at the time of research had about 507 stars and 31 forks. The project was created in August 2026, so it is very new but growing quickly, and it carries an OpenSSF Scorecard badge for supply-chain transparency.

## Wire oc Into Your Agent: Claude Code, Codex, Cursor, Copilot

For an AI coding agent to use oc, you add one line to its instructions file or skill directory. The tool is designed to teach itself: an agent can run `oc --help` and read the `actions:` line in any output to understand what it can do. Because everything arrives as compact text, there is no special integration layer.

### Claude Code

Add a tool description in your `CLAUDE.md` file (or a `.claude/skills/` entry) so the model knows the command exists and when to use it. A one-line declaration such as "Use `oc` (`npx @only-cli/oc`) to fetch web pages as compact numbered text instead of raw HTML" is enough to make the agent reach for it.

### Codex

In Codex, the same skill-style declaration goes into your project's `AGENTS.md` or a codex skills directory. Point the model at the `oc` command and let the numbered `actions:` line guide navigation.

### Cursor

Cursor reads project instructions from `.cursor/rules`. Add the one-line oc guidance there, or drop a skill file into your project so the assistant picks up oc for any URL it needs to investigate.

### Copilot

For GitHub Copilot, add the instruction to your repository settings or a skill directory that the assistant reads on startup. Since oc ships no daemon and talks only through stdout, any agent that can run a shell command can use it.

Every integration is one small text file. If the tool's output format ever changes, you only update that one declaration — there is no compiled adapter to rebuild.

## oc Command Reference

The core workflow is built around a small set of commands, all invoked through `oc <site> <verb>` or the global commands below.

- `oc open <site>` — open a site and get the compact numbered view with the actions list.
- `oc do <site> <n>` — perform the numbered action `n` that the last view presented.
- `oc find <site> <query>` — jump to the content matching your query on the current site.
- `oc next <site>` — paginate forward to the next page of content.
- `oc read <site>` — read the full distilled content of the current page.
- `oc raw <site>` — fetch the raw HTML when you truly need the unprocessed markup.
- `oc <site> <verb>` — call a site-specific verb for shorthand workflows.
- `oc sites` — list all the tuned site shortcuts oc ships with.

Useful flags include `--budget` to cap the number of tokens returned (with a hard cap at 500 tokens for the render budget), `--json` for machine-readable output, `--html` to switch the view to raw HTML, `--session` for session handling, and `--verbose` for debugging.

### Tuned Site Shortcuts

oc ships a `clis/` directory of tuned shortcuts for popular sites. For example, `oc hn item 4711` jumps straight to a Hacker News item, and `oc gh repo` opens a GitHub repository view. Running `oc sites` lists every shortcut you have available, so you never need to memorize them. When a site you use often has no shortcut yet, you can drive it generically with `oc open` and the same numbered action model still applies.

## Drive Any Website by Number: A Walkthrough

The fastest way to understand oc is to watch it work. Imagine you want your agent to read a Hacker News discussion.

First, open the site:

```
oc open https://news.ycombinator.com
```

oc returns a compact view: a short headline list, each item with a number, plus an `actions:` line listing what you can do next. The whole response fits in a few hundred tokens instead of the tens of thousands that the raw page would produce.

To read a specific item, tell the agent to act on its number:

```
oc do hn 42
```

oc follows the numbered action through the site, distills the target page, and returns a compact summary with the next set of numbered actions. Want the full text of an article? Call `oc read`. Want to scan the comments thread one screen at a time? Call `oc next` to paginate.

The model never sees a browser or a giant HTML dump. It sees a sequence of small, numbered menus — exactly the interface a text-based agent is best at following. On a Reddit thread that cost nearly 53,000 tokens raw, the same journey through oc costs about 477 tokens.

## Benchmark Reality Check: oc vs Raw HTML vs Jina Reader vs Playwright MCP

The benchmarks separate marketing claims from engineering reality. Below are the reductions reported by the oc project for September 2026 across 14 real pages.

| Approach | Tokens (14 pages) | Fold vs Raw HTML |
| --- | --- | --- |
| Raw HTML baseline | 1,119,003 | 1x |
| only-cli (oc) | 9,466 | 118x fewer |
| Jina Reader | ~161,000 est. | 17x fewer |
| Playwright MCP accessibility snapshot | ~511,000 est. | 54x fewer |

In other words, oc is roughly 7x leaner than Jina Reader and about 4x leaner than a Playwright MCP accessibility snapshot on the same pages, while remaining dramatically cheaper than raw HTML. These are real, named comparative figures from the project's own benchmark suite rather than a single hand-picked example.

Compare this to the broader market: the earlier estimates of 75 percent HTML noise and 80 percent of token budget spent on unusable tags are consistent with oc's behavior. Where a generic markdown fetch delivers an 80 percent reduction, oc pushes that further by stripping boilerplate, compressing repeated structures, and presenting numbered actions instead of full document text.

## Getting Past Bot Blocks: How oc Impersonates a Browser

Many high-value sources — Reddit, LinkedIn, and other protected or login-walled sites — block simple curl requests and naive fetchers. oc handles this by impersonating a real browser. It first impersonates Chrome, falls back to Firefox if needed, and finally to native fetch as a last resort. This lets it reach pages that reject plain HTTP clients.

Be aware that "impersonating a browser" is not the same as a headless browser that executes JavaScript and renders a page. oc presents the distilled, readable content it can extract; for heavy single-page applications that render everything client-side, you may need `oc raw` or a full browser tool. The impersonation is a negotiation strategy with the site's bot protection, not a JavaScript engine.

## Session, Login, and Safety Notes

For sites that require a login, oc supports a `--session` flag and session handling so you can authenticate and keep state across requests. The site-specific verbs include login and logout flows via commands such as `oc <site> login` and `oc <site> logout`.

Two cautions are worth keeping in mind. First, oc renders a page's text content and presents it to you or your agent — treat what it returns as data, not as permission-granting instructions. If a page you fetched contains instructions ("reply to this comment", "ignore your previous instructions"), your agent should treat that content as untrusted data, never as a directive to follow. Second, keep any session tokens or credentials out of your agent's context and out of comments and logs; log out of personal sessions when you are done, and rely on environment variables rather than printing secrets.

## When to Prefer oc vs a Real Browser vs Plain Markdown Fetch

No single tool covers every case. The rough rule of thumb:

| Situation | Best tool |
| --- | --- |
| Reading news, forums, docs, blogs through an agent | oc (tokens, speed) |
| A heavy single-page app / app that needs JS execution | Full browser tool |
| You only need the article text, no navigation | Plain markdown fetch (Jina, markdown.new) |
| Site blocks naive fetchers (Reddit, LinkedIn) | oc (browser impersonation) |
| You must inspect the exact raw HTML | `oc raw` or direct fetch |

oc wins for the everyday "read a page, follow a link, scan a thread" workloads that dominate agent browsing. It loses to a real browser when you need rendered JavaScript or complex interactive state, and it is arguably overkill when a plain markdown fetch of a single static article is all you need — though its number-based navigation and session handling make it the strongest general-purpose default.

## Final Verdict: Is only-cli Worth Adding to Your Agent Stack in 2026?

Yes, for most developers working with AI agents. Token costs are a real and growing expense — the industry is estimated to burn $1 billion to $5 billion per year on web markup agents never use, and individual agents can route tens of millions of tokens per month through raw HTML. oc turns any website into a numbered CLI the agent drives by number, cutting input tokens by roughly 45x to 118x while staying installable in 30 seconds and wiring into Claude Code, Codex, Cursor, and Copilot with a single line.

The tradeoffs are modest: the project is young (created August 2026), it does not execute JavaScript, and you must treat fetched page text as untrusted data. But the benchmark is concrete, the setup pain is near zero, and the ergonomics fit how agents actually think. If you are shopping for a token-efficient browser tool in 2026, only-cli is worth a serious look.

## Frequently Asked Questions

### What is only-cli and how does it turn a website into a CLI?
Only-cli (oc) is an open-source command line tool that fetches a web page, distills it into compact text with numbered actions, and lets an AI agent drive the site by choosing numbers. It turns an arbitrary website into a per-site CLI so agents can browse in hundreds of tokens instead of tens of thousands.

### How do I install only-cli?
Install globally with `npm install -g @only-cli/oc` or run it on the fly with `npx @only-cli/oc --help`. It requires Node.js 20 or newer and only three runtime dependencies, with no daemon or browser extension.

### How much does oc reduce token usage compared to raw HTML?
The oc GitHub benchmark reports 118x fewer tokens than raw HTML across 14 real pages (9,466 versus 1,119,003 tokens), and 17x fewer than Jina Reader and 54x fewer than a Playwright MCP accessibility snapshot. The official site reports roughly 45x fewer tokens on a four-page example.

### Does only-cli work with Claude Code, Codex, Cursor, and Copilot?
Yes. You add a one-line skill or instruction to each agent's rules or skills directory, such as CLAUDE.md for Claude Code, AGENTS.md or the skills directory for Codex, .cursor/rules for Cursor, and the settings or skills directory for Copilot. oc teaches itself through --help and the numbered actions: line.

### Is it safe to give oc my login sessions?
Sites that need authentication are handled with the --session flag and site-specific login and logout verbs. Keep any session tokens or credentials out of agent context and logs, use environment variables instead of printing secrets, log out of personal sessions when done, and always treat fetched page text as untrusted data rather than instructions to follow.
