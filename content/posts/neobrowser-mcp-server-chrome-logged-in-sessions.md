---
title: "NeoBrowser Review: An MCP Server That Drives Real Chrome With Your Logged-In Sessions"
date: 2026-10-01T08:40:59+00:00
tags:
  - MCP
  - browser automation
  - MCP server browser automation
  - Chrome CDP
  - Rust
  - NeoBrowser
  - Playwright MCP
  - chrome-devtools-mcp
  - browser-use
  - Claude in Chrome
  - session persistence
  - AI agents
description: "A Rust MCP server that drives your real Chrome over CDP and reuses your logged-in profile cookies. Honest benchmarks, but a broken install URL today."
draft: false
cover:
  image: "/images/neobrowser-mcp-server-chrome-logged-in-sessions.png"
  alt: "NeoBrowser Review: An MCP Server That Drives Real Chrome With Your Logged-In Sessions"
  relative: false
schema: "schema-neobrowser-mcp-server-chrome-logged-in-sessions"
---

An mcp server browser automation setup usually fails the same way: the agent launches a fresh, cookie-less Chromium, hits a login wall, and stalls. NeoBrowser is a Rust MCP server that takes the opposite approach — it drives your installed Google Chrome over CDP and can start already authenticated from your real profile.

That is the pitch, and the engineering behind it is real. Whether you should install it today is a harder question, and the answer involves a 404, a disputed differentiator, and four security questions the project's own launch thread left open.

This review holds those three things apart: what is verifiable in the code, what the README claims that no longer holds in 2026, and what the distribution story actually looks like right now. The single most important finding is at the end of the next section and it is about installability, not features.

## What is NeoBrowser and what does "driving real Chrome" actually mean?

NeoBrowser is an MCP (Model Context Protocol) server that exposes 43 browser-automation tools and drives the Chrome binary already installed on your machine through the Chrome DevTools Protocol, rather than downloading its own bundled browser. It is written in Rust, ships as a single static binary of roughly 4 MB, and its `rust/Cargo.toml` declares version 0.1.7, edition 2021, `rust-version = 1.82`, under the MIT license, described as "a fast, stealthy MCP browser-automation server that drives real Chrome."

The tool surface is verifiable, not marketing copy. The repository's [`docs/TOOLS.md`](https://github.com/t-soriano-sesame/neobrowser/blob/main/docs/TOOLS.md) contains exactly 43 tool headings, and they cluster into recognizable groups:

- **Navigation and reading:** `navigate`, `read`, `screenshot`, `page_info`, `wait`, `scroll`, `paginate`
- **Interaction:** `find`, `find_and_click`, `click`, `type`, `fill`, `form_fill`, `submit`, `dismiss_overlay`, `upload`, `download`
- **Session machinery:** `save_cookies`, `restore_cookies`, `save_session`, `session_info`, `login`
- **Tabs:** `new_tab`, `list_tabs`, `switch_tab`, `close_tab`
- **Recording:** `record_task`, `stop_recording`, `replay`
- **Diagnostics:** `console_logs`, `network_log`, `metrics`, `debug`
- **Search:** `search`, `search_images`, `search_videos`, `search_twitter_videos`

The session and recording groups are the interesting ones. `save_cookies` / `restore_cookies` and `record_task` / `replay` are exactly the primitives an agent needs to avoid re-authenticating on every run, and most competing servers do not expose them at all.

A detail worth knowing before you judge the codebase: the original Python implementation is retained inside the repository as a differential-testing oracle. The language breakdown still shows Python at 503,547 bytes versus Rust at 337,246 bytes, so the "Rust project" is currently a Rust project with a large Python reference implementation riding along. That is a legitimate engineering choice for cross-checking behavior, but it does mean the repository is not as lean as the single-binary story suggests.

## Why do browser MCP servers hit login walls in the first place?

Because the default architecture of browser automation is anonymous. Almost every browser MCP server — Playwright MCP, Puppeteer-based servers, hosted cloud browsers — starts from a clean profile. A clean profile means no cookies, no `localStorage`, no session tokens, and, critically, a fingerprint that looks like a first-time visitor with an empty history.

To a bot-detection system, that combination is a signal in itself. The project's own README concedes this plainly: "a fresh cookie-less profile is itself a signal." It also concedes the ceiling: "What no tool can promise is defeating interactive challenges — reCAPTCHA, Turnstile, or behavioral/reputation systems (DataDome) can still put up a wall."

That honesty is unusual in this category, and it sets up the actual product thesis. If you cannot beat a bot wall, you can at least stop walking into the cheap ones — the login gates, paywall prompts, and "verify you are human" interstitials that exist purely because the browser arrived with no identity. This is the layer NeoBrowser targets, and the framing is correct. The question a buyer should ask is not "does this work?" but "is this still a differentiator in 2026?" That question gets answered honestly later in this review, and the answer is more uncomfortable than the README implies.

For scale on why this category matters at all: the 2026 Imperva Bad Bot Report figures circulated widely put automated traffic at roughly 53% of all web traffic with about 40% of it classified as bad bots, and advanced bad-bot traffic growing roughly 12.5x year over year. Those numbers come from secondary summaries rather than a page served by Imperva itself at review time, so treat the exact percentages as directionally useful rather than authoritative. The strategic point holds either way: real-session automation is simultaneously the fix for login walls and the exact behavior every bot-detection vendor is tuning against.

## How does NeoBrowser reuse your logged-in Chrome session?

Two mechanisms, and they have different risk profiles. Understanding which one you are using is the single most important operational decision in this review.

**Path 1 — profile cookie injection (opt-in).** When `NEOBROWSER_REAL_PROFILE` is set, NeoBrowser decrypts cookies from your actual Chrome profile using the OS keystore — macOS Keychain, Linux secret-service, or Windows DPAPI — and injects them into the session the agent drives. Written cookie files are created with `0600` permissions. The README says Google, LinkedIn, and Microsoft session-identity cookies are deliberately excluded so that reusing a profile does not log you out of your real browser.

**Path 2 — attach mode.** With `NEOBROWSER_ATTACH_PORT=9222`, NeoBrowser connects to a Chrome instance you already started with `--remote-debugging-port=9222`. This is the safer path: nothing is decrypted, nothing is copied, and the README states the server never patches or kills the browser it attaches to. Several commenters in the launch thread noted they had built exactly this themselves with Chrome's own debugging flag, which is a fair observation — it is a well-understood technique, not a novel one.

A third detail matters for the security section: the JavaScript fingerprint patches are applied only to tabs NeoBrowser itself owns, never to an attached real Chrome. That is a defensible design decision and it is the one that keeps attach mode clean.

## Is the install working today? Read this before you copy the one-liner

No. The documented install path is broken as of 2026-10-01, and this is the review's hard finding.

`install.sh` hardcodes `REPO="pitiflautico/neobrowser"` and downloads its artifact from `https://github.com/pitiflautico/neobrowser/releases/latest/download`. Every one of those endpoints fails today:

| Asset | Expected | Status on 2026-10-01 (verified) |
| --- | --- | --- |
| `github.com/pitiflautico/neobrowser` | The project repository | HTTP 404 |
| `pitiflautico.github.io/neobrowser/` | Homepage / docs site | HTTP 404 |
| `raw.githubusercontent.com/pitiflautico/neobrowser/main/install.sh` | The installer | HTTP 404 |
| GitHub Releases (public copy) | Downloadable binaries | None exist (`[]`) |
| `t-soriano-sesame/neobrowser` | Only public copy of the code | HTTP 200, 0 stars, 3 forks |

I re-verified the first two rows and the Releases check directly before publishing this review rather than trusting the research brief alone. `pitiflautico` has 62 public repositories and none of them is named `neobrowser`. The only public copy of the source, `t-soriano-sesame/neobrowser`, was created 2026-08-17 and last pushed the same day; all 72 commits are authored by `pitiflautico`, and the repository sits at 0 stars, 3 forks, and 0 open issues.

Two consequences follow. First, the advertised one-line install cannot work as published — it would try to fetch a release artifact from a repository that does not resolve. Second, the project's registry metadata still points at the dead URL: `server.json` declares `io.github.pitiflautico/neobrowser` at version 0.1.3 with `websiteUrl` on the 404ing GitHub Pages site, while `rust/Cargo.toml` declares 0.1.7. The two version strings disagree, and both identity fields reference a repository that is gone.

There is also an internal strategy file in the public copy whose stated mission is to take the repository to 10,000 stars with a recorded baseline of 0 stars on 2026-08-13, alongside a promotion playbook and a campaign-metrics file. It should be read as a distribution lesson, not a personal attack: the playbook explicitly forbids spam, astroturfing, and star-buying, and the visible outcome — a launch thread with 34 points, a repository at 0 stars, and a public copy nobody forked into use — is what careful, rule-following self-promotion looks like when the differentiator is contested. The lesson for anyone shipping a niche MCP server is blunt: a launch URL is infrastructure, and letting it 404 can erase a project's discoverability regardless of code quality.

**What to do instead.** If you want to evaluate NeoBrowser, build from source in the public copy (`rust/`), then register it manually. Do not run `install.sh`, and do not trust the README badges or `server.json` until they point at a live repository.

## Does NeoBrowser actually beat Playwright MCP?

Partially — and the honest part is the benchmark itself. NeoBrowser ships a self-run neutral comparison against Playwright MCP, and it publishes results where it loses.

| Metric | NeoBrowser | Playwright MCP |
| --- | --- | --- |
| Functional tasks executed (of 9) | 9/9 | 7/9 |
| Destination access success (of 9) | 9/9 | 7/9 |
| Average tool calls per task | 5.2 | 4.7 |
| Average latency per task | 4,760 ms | 2,597 ms |
| Adversarial: Google Images | bot wall | bot wall |
| Adversarial: Cloudflare NowSecure | CAPTCHA | CAPTCHA |

Three things about this table deserve emphasis, because vendor benchmarks rarely contain any of them.

It **concedes a real loss.** NeoBrowser is roughly twice as slow, and the benchmark says why: it forces compositor frames (`nudge_frame`) so deferred content actually renders before the agent reads the page. That is a deliberate trade of speed for correctness, and it is stated rather than hidden.

It **separates execution success from destination access.** A task can execute perfectly and still be blocked by a wall, and the benchmark scores those two axes independently. Most comparisons in this niche collapse them, which lets a detected wall inflate a success rate.

It **makes no bypass claim.** Both tools produced a bot wall on the Google Images row and a CAPTCHA on the Cloudflare row, and the file says so explicitly: "No evades-better claim is made," with the note that both were blocked on a single IP. The Playwright upload failure is additionally attributed to the neutral harness's mapping rather than to a Playwright incapability, while the persistence gap — Playwright MCP exposes no cookie save/restore tool — is called a genuine capability gap.

So: the 9/9 versus 7/9 headline is real, and so is the 2x latency penalty. If your agent's bottleneck is wall-clock time, that trade is expensive. If your agent's bottleneck is silently reading a half-rendered page and acting on stale content, the trade pays for itself.

## NeoBrowser vs Playwright MCP vs chrome-devtools-mcp vs browser-use vs Claude in Chrome

This is where the README's central claim stops holding. The README argues that "every browser MCP launches a fresh, fingerprintable headless browser with no cookies." In 2026 that is no longer the state of the art, and each cell below should be re-verified before you repeat it.

| Option | Runtime | Real-session mechanism | Tool surface | Best for |
| --- | --- | --- | --- | --- |
| **NeoBrowser** | Rust single static binary, no Node/Python | Cookie decrypt + inject from real profile (opt-in), or attach to Chrome on port 9222 | 43 tools incl. cookie/session save-restore, tabs, playbooks, multi-source search | A zero-runtime-dependency, local-only server that lands authenticated with no extension and no cloud |
| **Playwright MCP** | Node 18+, bundled browser | Chrome extension connects to existing tabs and "leverages your logged-in sessions"; also `--user-data-dir` and `--storage-state` | Accessibility-tree driven; no cookie save/restore tool | The default for deterministic local automation |
| **chrome-devtools-mcp** | Node LTS + Puppeteer | Persistent user-data directories; connect to a running Chrome instance | DevTools-flavored automation plus performance traces | Coding agents that also need debugging and perf insight |
| **browser-use** | Python 3.11+ | `Browser.from_system_chrome()` reuses a profile but transfers cookies only — not `localStorage`, IndexedDB, or extensions | Agent-first abstractions | Autonomous task-in/result-out agents and cloud scale |
| **Claude in Chrome** | Chrome side panel, paid plan | Your own logged-in browser by construction | Product feature, not an embeddable MCP server | Non-developers automating their own sessions |

The numbers make the competitive pressure concrete. Playwright MCP carries 37,733 stars, published `@playwright/mcp` v0.0.83 on 2026-09-28, and saw roughly 28.7 million npm downloads in the last month. chrome-devtools-mcp, maintained by Google, sits at 52,827 stars with v1.10.1 published 2026-09-23 and about 8.1 million monthly npm downloads. browser-use is at 116,875 stars and sells cloud browsers at $0.02 per browser-hour with residential proxies at $5/GB. And Claude in Chrome has been generally available on every paid Claude plan since 2026-08-26, selling precisely NeoBrowser's pitch — reaching internal dashboards and vendor portals "with the logins you have" — inside Claude Code and Claude Cowork, the very tools most likely to install an MCP browser server.

That last point is the crux. The launch thread's most repeated reader objection was some version of "doesn't Claude already do this?", and the honest answer is that the specific capability — authenticated real-browser automation — is now a platform feature. NeoBrowser's remaining edge is narrower and more technical than the README sells: cookie-level profile reuse with **no browser extension**, **no Node or Python runtime**, and **no cloud dependency**, plus save/restore cookie tools that Playwright MCP genuinely lacks. That is a real edge. It is not "every other browser MCP launches a fresh cookie-less browser."

There is also a category-wide headwind worth naming. Playwright MCP's documentation now steers coding agents toward CLI-and-skills over MCP for token efficiency, reserving MCP for stateful agentic loops. For a server whose main offering is 43 verbose tools, that is a strategic problem independent of feature parity: the category itself is questioning whether a large MCP tool surface is the right shape for browser work.

## Is NeoBrowser stealthy, or just less fake?

It is deliberately non-spoofing, which is a more defensible position than most "stealth" claims. The README describes the approach as using the real Chrome binary with:

- `navigator.webdriver` forced to `undefined`
- User-Agent rewritten to match the actually installed Chrome version, so Client Hints stay internally consistent
- No `--disable-gpu`, so WebGL reports the real GPU rather than a software-rendering tell
- JavaScript patches applied only to tabs the server owns, never to an attached real Chrome

The distinction matters. A large share of "stealth" tooling works by patching fingerprint APIs to lie, which produces internally inconsistent values that detection vendors specifically look for — a WebGL vendor string that contradicts the driver, a User-Agent that contradicts the Client Hints headers. Running the real binary with a real GPU and a self-consistent version string is a weaker claim and a more durable one.

It also means there is no residential-proxy story and no CAPTCHA-solving story. Sites behind DataDome, Turnstile, or Cloudflare's interactive challenges stay behind them, and the project says so. If your evaluation criterion is "get past the wall," NeoBrowser is the wrong tool and its own documentation says as much. If your criterion is "stop tripping the cheap walls that only exist because the browser arrived anonymous," this is the right target.

## Security review: cookie decryption, SSRF guard, and the four questions still open

The security posture is better documented than most projects at this stage, and it is also incomplete in ways the launch thread identified precisely. Both belong in the review.

**What ships today:**

- **Cookie handling is opt-in.** Profile reuse requires `NEOBROWSER_REAL_PROFILE`; it is not the default.
- **Cookie files are written `0600`.** Owner read/write only.
- **Session-identity cookies are excluded.** Google, LinkedIn, and Microsoft identity cookies are deliberately skipped so profile reuse does not log you out of your real browser.
- **Fetch paths are SSRF-guarded**, and the `login` tool is HTTPS-only.
- **A domain allowlist exists** — `NEOBROWSER_DOMAIN_ALLOWLIST=github.com,.docs.rs` causes `navigate` to reject unlisted domains. It was added after the launch thread raised the question. It is opt-in, and unset means no restriction.
- **Attach mode does not mutate the browser it attaches to.**
- **Local-only with no telemetry**, in explicit contrast to chrome-devtools-mcp, which collects usage statistics by default with opt-out flags.
- **The optional LLM fallback in `find` is off by default** and bills to your own `ANTHROPIC_API_KEY` if enabled.

**What the launch thread asked for and the project has not fully answered:**

1. **Human approval before destructive actions.** Submitting forms, deleting records, or completing purchases currently run without a confirmation gate by default. The thread asked for one; there is no documented general mechanism.
2. **A persistent audit record.** There is no durable log of which tool touched which domain on whose behalf — `console_logs` and `network_log` are per-session diagnostics, not an audit trail.
3. **Revocation.** Once a profile or allowlist grant exists, the thread asked how to revoke access previously granted. The allowlist is an environment variable, which is revocable, but there is no per-session credential model.
4. **Prompt-injection containment.** An agent driving your authenticated browser is a high-value injection target: a single hostile page can instruct it to exfiltrate or submit. The project does not document a containment strategy.
5. **Credential hygiene in logs.** A commenter reported "it spits out password in logs according to gif." The README does not address this head-on. If you evaluate NeoBrowser, treat log redaction as something to test yourself before pointing it at anything that matters.

None of this is unusual for a 0.1.x project, and the opt-in defaults are the right call. But a tool that decrypts your OS-keychain cookies should be held to a higher bar than a tool that drives an isolated browser, and the HN thread's asks are the correct bar. Until approval gates, an audit trail, and revocation exist, the responsible configuration is attach mode against a dedicated Chrome profile you can close and clear — not cookie injection from your daily driver.

Two more operational facts worth stating plainly: there is no hosted tier and no proxy rotation, so walled sites stay walled; and the server's own version metadata is inconsistent (`server.json` 0.1.3 versus `Cargo.toml` 0.1.7), which makes "which version am I running" harder to answer than it should be.

## Cost and context budget: 43 tools is a feature and a bill

Every MCP tool's name, description, and parameter schema is re-processed by the model on each reasoning step. A 43-tool server is therefore not free, and the honest way to evaluate it is per task, not per feature list.

Two cost axes to compare when you are choosing between these servers:

- **Context cost.** Playwright MCP is the default for many teams because its accessibility-tree output is compact, but its tool surface and interaction cost has been reported at roughly 5,000 tokens per interaction. A 43-tool NeoBrowser server has a larger static surface but produces different per-step payloads depending on whether you use `read`, `extract`, or `analyze`.
- **Dollar cost at scale.** browser-use's cloud tier at $0.02 per browser-hour plus $5/GB of residential proxy is cheap for a few tasks and expensive for a crawler. Kernel's comparison notes the trap in agent-style servers generally: a hosted server that routes act/observe/extract calls through a model stacks token bills on top of browser time.

Neither vendor listicle — PageBolt, ChatForest, or Kernel — treats "does it land already authenticated from my real profile" as a buying axis. They compare token cost, hosting model, and vision-versus-accessibility perception. That gap is the real opening for NeoBrowser, and it is a gap in the review discourse rather than a moat: the moment a mainstream comparison adds a session-persistence column, the two named alternatives win it on maintenance and ecosystem weight.

## Who should use NeoBrowser in 2026 — and who should not

**Use it if:** you want a zero-runtime-dependency, local-only MCP browser server that lands authenticated without a browser extension; you already run Chrome; you are comfortable building from the `rust/` directory of the public copy today; you value save/restore cookie tools and record/replay playbooks that the incumbents do not expose; and you can live with roughly 2x the latency for correctly rendered pages.

**Do not use it if:** you need a maintained install path or release artifacts today; you need a hosted tier, proxy rotation, or CAPTCHA handling; you want first-party maintenance and a security review process behind the tool; your team is standardizing on Playwright MCP's CLI-and-skills direction for token efficiency; or you need approval gates and an audit trail before pointing an agent at authenticated sessions.

## Verdict

NeoBrowser is a genuinely well-engineered, unusually honest niche MCP server wrapped in a distribution failure. The engineering claims hold up under verification — 43 tools counted in-repo, a single Rust binary under MIT, opt-in cookie handling with `0600` files and an SSRF guard, attach mode that does not mutate your browser, and a self-published benchmark that concedes a 2x latency loss and admits parity on walled pages instead of claiming a bypass.

The differentiator is real but narrower than the README argues. Cookie-level real-profile reuse with no extension, no Node, and no cloud is a specific technical advantage that Playwright MCP's extension model, chrome-devtools-mcp's persistent profiles, browser-use's `from_system_chrome()`, and Claude in Chrome's GA release each approach from a different angle — and all four have larger maintenance surfaces behind them.

The disqualifying problem is that you cannot install it the documented way right now: the launch repository, the GitHub Pages site, and `install.sh` all return 404, no Releases exist, the registry metadata points at the dead URL, and the only public copy sits at 0 stars with 3 forks. A project in this state is a source-build evaluation, not a dependency. Build it from `rust/`, attach it to a dedicated Chrome profile on a debug port, keep the domain allowlist set, and treat the missing approval gate and audit trail as things you must replace yourself before it touches an account you care about.

## FAQ

### Is NeoBrowser free and open source?

Yes — the code in the public copy is MIT-licensed, including the Rust server. The catch is not the license but the distribution: the advertised repository 404s, the installer points at a Releases feed that does not exist, and the only public copy is a static tree at 0 stars. Treat it as source-available code you build yourself, not a package you install with a one-liner.

### Does NeoBrowser decrypt my Chrome cookies?

Only when you opt in by setting `NEOBROWSER_REAL_PROFILE`. When enabled, it decrypts cookies from your real Chrome profile through the OS keystore — macOS Keychain, Linux secret-service, or Windows DPAPI — writes any cookie files with `0600` permissions, and deliberately excludes Google, LinkedIn, and Microsoft session-identity cookies so your real browser stays logged in. The safer alternative is `NEOBROWSER_ATTACH_PORT=9222`, which reuses an already-running Chrome without decrypting anything.

### Can NeoBrowser bypass Cloudflare, reCAPTCHA, or Turnstile?

No, and it does not claim to. Its own benchmark records a bot wall for NeoBrowser and Playwright MCP alike on Google Images and a CAPTCHA for both on a Cloudflare-protected page, on a single IP, with the explicit note that "no evades-better claim is made." The README states directly that interactive challenges and reputation systems can still put up a wall. There is no CAPTCHA solving and no residential-proxy tier — what NeoBrowser removes is the cheap penalty for arriving with an empty, cookie-less profile.

### How is NeoBrowser different from Playwright MCP's Chrome extension?

The extension attaches to existing tabs and rides your logged-in session; it is the easiest path and it is first-party maintained by Microsoft behind 37,733 stars. NeoBrowser's differences are structural: no browser extension, no Node or Python runtime, a single Rust binary, cookie-level profile reuse rather than tab attachment, and save/restore cookie and session tools that Playwright MCP does not expose. The benchmark's one clear capability gap in NeoBrowser's favor is persistence — Playwright MCP has no cookie save/restore tool.

### What if the pitiflautico/neobrowser URL still 404s when I try to install?

Then you are seeing the same state this review verified on 2026-10-01, and you should not run `install.sh` — it hardcodes that dead repository and will fail on the download. Build from the `rust/` directory of the public copy instead, point your MCP client at the resulting binary, and register it manually. Re-check periodically: if a live repository reappears with real Releases, the installability objection in this review disappears with it.
