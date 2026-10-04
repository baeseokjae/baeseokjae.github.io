---
title: "Saggar Review: A Mac Terminal That Organizes Sessions"
date: 2026-10-01T02:56:28+00:00
tags:
  - "Saggar terminal"
  - "Saggar Mac terminal"
  - "Saggar app review"
  - "Saggar vs cmux"
  - "Saggar pricing"
  - "Mac terminal that organizes sessions"
  - "terminal for AI coding agents"
  - "supervise multiple coding agents"
  - "Claude Code session manager"
  - "Codex CLI terminal manager"
  - "attention queue terminal Cmd+J"
  - "remote control coding agent sessions iPhone"
  - "native Mac terminal not Electron"
  - "macOS 26 Tahoe terminal app"
  - "supervision loop AI agents"
description: "Saggar terminal review: a free native Mac app that sorts Claude Code and Codex sessions into one attention queue, versus the free rival cmux."
draft: false
cover:
  image: "/images/saggar-mac-terminal-sessions.png"
  alt: "Saggar Review: A Mac Terminal That Organizes Sessions"
  relative: false
schema: "schema-saggar-mac-terminal-sessions"
---

Saggar terminal is a free, native macOS app that runs your agent shells in parallel and then sorts them into one ordered attention queue, so the question it answers is not how fast your terminal renders but which of your five running sessions needs you right now. Your prompt, every failure, and every finished job surface in a single list you walk with Cmd+J. Remote control of that queue from an iPhone costs USD 2.50 per month.

That is the short answer. The longer one is that Saggar's premise is narrower and better matched to 2026 behaviour than the marketing around agentic terminals usually admits, its closest rival is free and open source, and its author says so on his own comparison page.

## Saggar at a glance: what it is, who makes it, what it costs

Saggar is published by Marginal Utility, the studio behind Kiln, and its author is Max Clayton Clowes, who launched it on Hacker News on 17 August 2026 and answered objections inline for the rest of the thread. The app is written in native Swift and SwiftUI against macOS 26, explicitly not Electron, and it is a companion to the agent harness rather than a replacement for one: it does not spawn agents of its own, it attaches to the shells you already run.

| Spec | Detail |
|---|---|
| Price | Free (no account required); Pro USD 2.50 / GBP 1.99 per month, first month free |
| Platform | macOS 26 Tahoe or later, Apple Silicon only, no Linux or Windows build planned |
| Rendering | Native Swift/SwiftUI, not Electron; the vendor does not claim a GPU renderer |
| Agent detection | Seven named CLIs plus an "Other agents" fallback |
| Project state | Written to a `.saggar/` directory beside your code |
| Remote access | Pro only; account-gated pairing with explicit approval on the Mac |
| Repo | Closed source |

The detection list is the part worth reading closely, because it tells you how much of the app is heuristics versus integration: Claude Code, Codex CLI, Antigravity CLI, Pi, OpenCode, GitHub Copilot CLI and Kimi Code are recognised by name, and anything else falls through to a generic mode.

## The problem it is actually solving: five agents, one of them is stuck, and you cannot tell which

The pain Saggar describes is real and it is well documented outside the vendor's own pages. A 2026 review of cmux on vibecoding.app puts the failure in one sentence: running three Claude Code instances, a Codex agent and Gemini CLI in parallel tmux panes "works, but it's held together with duct tape. You can't tell which agent is waiting for input, which one finished, or which one hit an error without manually checking every pane."

That is the exact workflow Saggar targets. A developer running three CLI sessions in a single repo on one monitor does not have a rendering problem; they have an interrupt-routing problem. The failure mode is not slowness, it is an agent that finished four minutes ago while you were reading a diff in another pane, or an agent that has been blocked on a file-write permission prompt in a tab you forgot existed.

The market data says this is mainstream behaviour, not a niche. According to Stack Overflow's April 2026 pulse survey of roughly 1,100 respondents, 59% of developers now use AI agents at any frequency, nearly double the 31% recorded in the 2025 Developer Survey. But 63% of technologists rarely or never let agents run entirely on autopilot, and 60% block agents from making unapproved system changes. Only a minority orchestrate in the fully autonomous sense: 68% say they prefer predictable single-agent setups over complex multi-agent configurations.

In other words, the dominant 2026 pattern is one human supervising several semi-autonomous agents, which is precisely the pattern Saggar is built around. Its premise sits on the mainstream behaviour while full orchestration is still the minority case.

## The supervision loop: start work, leave it alone, handle what needs you, step away

Saggar's own framing of the workflow is a four-beat loop, and it is the fairest way to evaluate the app because each beat is testable.

Start work across projects. You open shells the way you always do, in whatever repo you are working in, and Saggar notices the agents those shells spawn rather than asking you to register them in a config file.

Leave working agents alone. A session that is churning quietly should never demand anything from you. If the app interrupts you for a session that is making progress, it has failed at its one job.

Handle what needs you. Permission prompts, a question the agent asked in prose, an error, and a job that finished all converge into one ordered list. This is the beat where Saggar claims its edge over per-pane notification badges.

Step away without losing the thread. The Pro tier's only structural addition is leaving the desk: you can queue work behind active sessions or answer a prompt from a phone, with the Mac still awake, online and running Saggar.

The honest caveat is on the fourth beat. Remote supervision is not a background service. If the Mac sleeps, or you quit the app, or the machine loses network, remote control stops. That is a reasonable design for a session supervisor but it is not the same thing as a persistent cloud workspace, and anyone comparing Saggar to Warp should hold those two categories apart.

## How Saggar knows a session needs you: process-tree walk, on-screen scan, and opt-in hooks

This is the technically interesting part of the product and the sharpest contrast with its main rival.

Saggar classifies a session using two independent mechanisms. First, it walks the process tree underneath each shell looking for known agent binaries. Second, when that walk fails, it scans on-screen terminal chrome for the visual signals agents emit. On top of those two fallbacks it offers opt-in provider hooks that report session starts, prompts, turn boundaries and exits directly.

cmux takes a different route entirely. Its notification system works through terminal escape sequences, OSC 9, OSC 99 and OSC 777, which agents emit and the terminal intercepts, turning them into a blue pane ring, a lit sidebar tab and an optional macOS notification.

| | Saggar | cmux |
|---|---|---|
| Detection mechanism | Process-tree walk, then on-screen chrome scan | OSC 9/99/777 escape sequences emitted by agents |
| Reliable when | Agent binary is known or hook is installed | Agent emits the OSC sequence correctly |
| Fails when | Agent is renamed, wrapped, or runs remotely over SSH | Agent does not emit sequences, or emits them to a nested terminal |
| Extra precision | Opt-in provider hooks for starts, prompts, turns, exits | Per-pane rings plus unread panel |
| Attention model | One ordered queue | Per-pane status indicators |

Both approaches share a weakness worth naming. If you run your agents over SSH on a remote box, process-tree walking sees `ssh`, not `claude`, and escape sequences terminate inside the remote pseudo-terminal. Neither tool is a remote-first product, and the research brief behind this review makes the same point about the wider field: session persistence across disconnection is tmux's job, not theirs.

## Statuses and the attention queue: needs you, working, idle, finished, failed

Saggar reduces every session to five statuses: needs you, working, idle, finished, failed. The list is re-read every two seconds, which is frequent enough that a permission prompt appears in the queue within a beat of the agent raising it.

The ordering is the product. Rather than five panes each carrying its own indicator that you must scan, there is one queue sorted so that things requiring a decision come first. Cmd+J walks it. If nothing else in this review is decisive, that is: a single keystroke that jumps you to the next thing that is genuinely waiting on you turns five parallel sessions into a to-do list instead of a wall of output.

The trade-off compared with per-pane rings is real and worth stating plainly. A badge on the pane tells you *where* attention is needed while keeping the terminal as the source of truth. A queue tells you *what* needs attention but abstracts the panes. The queue model is better when work is spread over more sessions than fit on screen; the badge model is better when you can already see every pane and just need a colour.

## Living with it: projects, branches, layouts, and restoration after a restart

Saggar groups sessions by project, which in practice means repository. Git branches and worktrees are handled as separate session contexts, which matters because running the same agent on two branches of one repo in separate worktrees is now a common way to avoid agents colliding in the working tree.

Split panes and saved layouts let you reconstruct a multi-pane arrangement per project, and restoration after relaunch rebuilds the arrangement rather than the live processes. Read that carefully: saving a layout and reopening an app restores the shape of your workspace, not the running agent processes themselves. That is a weaker promise than session persistence, and it is the same gap flagged against cmux by its own reviewers, who list "no live session restore on relaunch" as a known weakness. Neither tool replaces tmux for surviving a reboot, and neither claims to.

The `.saggar/` directory is the more distinctive idea. Project state is written beside your code, so scratchpads, saved commands, layouts and scheduled tasks live in the repository and agents working in that repo can read them. That turns the convention into something a coding agent can consume directly, which is a clever alignment with the audience rather than a feature aimed at humans.

## Remote control and the security model: pairing, relay, envelopes, revocation

Saggar's security posture is the part of the design that received the most scrutiny at launch, and it is worth walking through properly because the objections were legitimate.

Pairing is gated on an account and requires explicit approval on the Mac. The Mac dials out to a Cloudflare relay and opens no inbound port, so your machine is never listening for connections. Traffic is sealed end to end, meaning the relay routes envelopes it cannot read. Signing out on the Mac revokes every paired device. Notably, pairing does not expire through inactivity, which is a deliberate convenience choice with a real cost: a phone you paired a year ago is still paired until you sign out.

The Hacker News thread is the best record of how this landed. One commenter wrote: "The remote control appears to use a third party relay, and I don't see encryption mentioned. I really want to use this, but I definitely don't trust a vibe coded relay to my shell." The founder's answer was that the third party is Cloudflare and the traffic is encrypted. A separate objection about trusting an unknown developer's binary with a shell session was never fully resolvable through argument, and cannot be; it is an acceptance decision, not a technical one.

The fair summary is that the architecture is conventional and defensible, the relay is operated by a large infrastructure provider rather than a bespoke server, and the residual risk is the app itself, not the transport. If you would not run an unsigned closed-source app that sees your shell, this is not the product that will change your mind.

## Saggar vs cmux: the free, open-source rival its own maker tells you to consider

You rarely get to quote a vendor conceding the comparison, and Saggar's compare page does it explicitly: "cmux and Saggar answer the same question and answer it in the same language... If you want a terminal built for agents and you want to read its source, the comparison is short: use cmux." The page carries a dated disclaimer that claims about cmux come from cmux's own documentation and were last checked in August 2026, and it includes a "Pick cmux" verdict block.

cmux is not a minor alternative. The GitHub API shows `manaflow-ai/cmux` at 27,532 stars on 1 October 2026, with the repository created on 28 January 2026 and still being pushed to the same day this review was written. That is roughly eight months old and it has accumulated an order of magnitude more visible community than a 70-point Show HN launch.

What cmux offers that Saggar does not: a GPL-3.0-or-later licence you can read and fork, GPU-accelerated rendering via libghostty, drop-in compatibility with an existing Ghostty config, a vertical sidebar showing branch, linked pull request status, working directory and listening ports, a built-in scriptable browser driven over a Unix socket at `/tmp/cmux.sock`, and per-project `cmux.json` actions. Its reviewers list macOS-only support, no live session restore, a young codebase with rough edges, occasional sandbox conflicts with agents, and a smaller ecosystem than tmux as the counterweights.

So where does Saggar actually win? Two places, both narrow and both real.

The first is the queue. cmux shows you status per pane; Saggar gives you one ordered list of things that need a decision and a single key to walk it. If your problem is that you cannot see every pane, that difference is worth a switch. If you can see every pane already, it is not.

The second is the phone. Saggar's first-party iOS client ships with Pro at USD 2.50 per month with the first month free. cmux's iOS app sits behind a paid Founder's Edition and TestFlight distribution. If supervising from a phone is the thing you actually want, Saggar's path to it is shorter and cheaper.

## Saggar vs the rest: Warp, tmux, dmux, Claude Squad, Ghostty, and your editor

cmux is the closest rival, but it is not the only one, and a review that only compares those two is grading on the vendor's chosen axis.

| Tool | Category | Model | Where it wins |
|---|---|---|---|
| Saggar | Agentic terminal (Mac) | One ordered attention queue, five statuses | Solo Mac devs supervising 3+ sessions; phone supervision |
| cmux | Agentic terminal (Mac, open source) | Per-pane rings, sidebar with PR/branch/ports | Anyone who wants to read or fork the source; Ghostty users |
| Warp | Cloud orchestration platform | Hosted, broader platform scope | Teams wanting a shared, hosted control plane |
| tmux | Multiplexer | Manual panes, persistence | Surviving disconnection and reboots; runs anywhere |
| dmux | tmux wrapper | Auto-creates git worktrees per pane | Worktree-per-agent workflows, 1,600+ stars |
| Claude Squad | tmux wrapper | Manages multiple agent sessions | Multi-agent session management, 7,700+ stars |
| Ghostty | General emulator | Fast rendering, no agent awareness | People who want speed and no agent magic |

The multiplexer ecosystem deserves more credit than it usually gets in these comparisons. Industry surveys of the 2026 agent-tool market describe tmux as "the de facto infrastructure for the entire multi-agent ecosystem," with dmux at 1,600-plus stars generating automatic git worktrees per pane, Claude Squad at 7,700-plus stars managing multiple agent sessions, and ccmanager at 1,100-plus stars supporting eight or more agent CLIs with session state detection.

If you are on Linux, on Windows, or in a shop that needs one consistent story across platforms, that is your column and it is not a consolation prize. tmux also gives you the one thing no agentic terminal currently provides: sessions that survive closing your laptop.

For a general emulator, Ghostty remains the answer for people who want speed and no opinion about agents, which is also why cmux's ability to read Ghostty's config file is such a strong migration story.

## Pricing: what is genuinely free and what Pro actually buys

The pricing split is unusually clean, and it is worth being precise because "free with a paid tier" descriptions often blur it.

The Mac app is free, requires no account, and a fresh install sends nothing off the machine. Everything that makes Saggar Saggar for a person sitting at the desk, meaning session detection, the five statuses, the attention queue, projects, panes and layouts, is in the free tier.

Pro costs USD 2.50 or GBP 1.99 per month with the first month free, and adds remote control, automations, queued sessions, local supervision decision history and push notifications.

Look at that list and a pattern appears: nearly everything Pro sells is about the app being useful when you are not at the Mac, or about remembering what you decided. Queued sessions let you stage work behind an active session; decision history records what you approved; push notifications reach you off the desk. For a developer who works at one machine all day, the free tier is not crippled. For someone who wants to check on a long-running refactor from a phone, USD 2.50 is the cheapest part of the workflow.

## Rough edges and limits: macOS 26 Tahoe, Apple Silicon only, closed source, alpha maturity

The launch thread is a more honest list of defects than any product page, and it is where several of the sharpest objections were raised and partly resolved.

The platform requirement drew the most heat. Saggar requires macOS 26 Tahoe or later, and one commenter's objection was blunt: "Requires macOS 26 Tahoe or later. Why? Tahoe hasn't even reached its first birthday and plenty of us are still on Sequoia... There's nothing a terminal needs from Tahoe specifically." The founder's answer was that macOS 26 is simply his lowest build and test target, and that he would look at lowering it. Apple Silicon only, with other platforms not ruled out but Electron explicitly rejected.

Launch-day signup was broken in the ordinary early-product way: confirmation emails that never arrived, a Content-Security-Policy rule blocking the site's own captcha, and a GitHub link returning 404. Multi-Mac pairing was requested in the thread and shipped during it, with the founder confirming "there was only a small bit of code forcing 1-1 pairing so this SHOULD work now" and a user confirming afterwards.

The structural limits are harder to fix than the launch bugs. The app is closed source while the nearest rival is GPL-3, so anyone who wants to audit a tool that sees their shell has no path to do so. Saggar is not listed at all in at least one 2026 survey of agentic-era terminals, which is a fair proxy for ecosystem size and mindshare. And the Show HN launch scored 70 points with 21 comments, against a rival with 27,532 GitHub stars.

## Who should use Saggar, and who should not

Use it if you develop on an Apple Silicon Mac running macOS 26 or later, you routinely keep three or more agent sessions alive across repositories, and your recurring failure is losing track of which one stopped. The attention queue is the feature that pays for the install, and the free tier contains it.

Also use it if supervising from a phone is a genuine requirement rather than a nice-to-have. That is the one thing USD 2.50 per month buys that nothing free in this space matches cleanly.

Skip it if you are on Linux or Windows, or your team needs one consistent tool across platforms. Skip it if your work depends on sessions surviving disconnection or reboot, in which case tmux or Zellij is still the answer and always was. Skip it if you run agents over SSH on remote machines, because both of Saggar's detection mechanisms are local and neither survives the SSH boundary. Skip it if you need to read the source of anything that sees your shell. And skip it if you are happy with four panes you can see at once, because a queue solves a problem you do not have.

## Verdict

Saggar is a well-targeted product built on an honest premise: in 2026, running several coding agents at once is normal, and the scarce resource is your attention rather than your CPU. Its one genuinely differentiating mechanic, a single ordered queue over prompts, failures and finished work plus five statuses refreshed every two seconds, addresses a documented failure that every parallel-agent developer recognises. Its free tier is real rather than a demo, its remote supervision is priced at the cost of a coffee, and its security model is conventional and defensible rather than clever and risky.

It is also a closed-source, Apple-Silicon-only, macOS 26-only app whose own author tells open-source-minded developers to use cmux instead, and whose closest rival has 27,532 GitHub stars against a 70-point launch. The right way to read that concession is not as weakness but as calibration: Saggar knows exactly which developer it is for, and it is not trying to be everyone's terminal.

If you are that developer, the free app is worth an afternoon. If you are not, cmux is free and you can read the code.

## FAQ

**Is Saggar terminal free?**
Yes. The native Mac app is free, requires no account, and sends nothing off the machine on a fresh install. Pro costs USD 2.50 or GBP 1.99 per month with the first month free and adds remote control, automations, queued sessions, decision history and push notifications.

**What is the difference between Saggar and cmux?**
cmux is a free, GPL-3.0 open-source agent terminal built on libghostty with per-pane notification rings, a sidebar showing branch and pull request status, and a scriptable browser. Saggar is closed source and organises sessions into one ordered attention queue walked with Cmd+J. Saggar's own comparison page recommends cmux if open source or Ghostty config compatibility matters.

**Does Saggar work on Linux or Windows?**
No. Saggar requires macOS 26 Tahoe or later on Apple Silicon, and the vendor states plainly that there is no Linux or Windows build and none is planned. Other platforms are not permanently ruled out, but Electron has been explicitly rejected as an approach.

**How does Saggar detect that an agent needs my attention?**
Saggar walks the process tree under each shell looking for known agent binaries such as Claude Code, Codex CLI or Antigravity CLI, and falls back to scanning on-screen terminal chrome when that fails. Opt-in provider hooks can report session starts, prompts, turns and exits directly. cmux instead relies on OSC 9, 99 and 777 escape sequences emitted by the agents themselves.

**Can I control my agent sessions from my phone?**
Yes, with Pro. Pairing is gated on an account and requires explicit approval on the Mac. The Mac dials out to a Cloudflare relay and opens no inbound port, traffic is sealed end to end, and signing out on the Mac revokes every paired device. The Mac must be awake, online and running Saggar for remote control to work.
