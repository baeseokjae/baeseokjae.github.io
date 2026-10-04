---
title: '1667 Review: A Terminal UI for Writing Fiction With LLMs'
date: 2026-10-01T02:57:24+00:00
description: 1667 is a free, local-first terminal UI for writing fiction with LLMs that keeps every generated take on a branching story tree instead of overwriting it.
tags:
- terminal UI fiction LLM
- 1667 review
- terminal AI writing tool
- local-first AI writing tool
- write fiction in the terminal
- BYOK AI writing tool
- Ollama fiction writing
draft: false
schema: "schema-1667-terminal-ui-fiction-language-models"
cover:
  image: "/images/1667-terminal-ui-fiction-language-models.png"
  alt: '1667 Review: A Terminal UI for Writing Fiction With LLMs'
  relative: false
---

1667 is a free, open-source terminal UI for writing fiction with language models. Every paragraph the model generates is kept as a sibling "take" on a branching story tree you navigate with the arrow keys, so rejected drafts are never overwritten. It is local-first and works with OpenAI, Anthropic, Ollama or any compatible endpoint.

## What Is 1667, the Terminal UI for Writing Fiction With LLMs?

1667 is a full-screen, keyboard-driven terminal environment purpose-built for drafting fiction with large language models. Its [GitHub description](https://github.com/1667-ai/1667) says it plainly: "A full-screen terminal environment for writing fiction with language models." There is no browser tab, no Electron shell and no web editor — the entire program runs in your terminal. The vendor's own documentation lives at [1667.ai](https://1667.ai/).

The name is the product thesis. 1,667 words per day multiplied by 30 days equals roughly 50,000 words, the classic pace that finishes a first draft in a month. The tool is built around that cadence rather than around one-click generation: the model writes one passage, stops, and waits for you to decide what happens next.

Three design decisions define it:

- **The take tree.** Regenerating does not discard the previous paragraph. Each generation becomes a sibling branch you can return to later.
- **One paragraph at a time.** Space continues, Enter supplies a direction, and the model produces a single take and then waits. There is no "generate my whole novel" button.
- **Local-first storage.** Stories live in a project folder you choose; API keys sit in a private file outside that folder.

As verified on 2026-10-01, the project is Apache-2.0, was created on GitHub 2026-08-04, and shows 26 stars, 0 forks and 7 open issues against a last push of 2026-09-29. The npm CLI package `@1667-ai/cli` has 105 published versions going back to 2026-07-26, with `latest` at 0.10.9 and `beta` at 0.11.0-beta.5.

## How Does the Take Tree Change the Drafting Workflow?

The take tree is the real product, and it is the feature that separates 1667 from nearly every other AI writing tool on the market. When you ask for a continuation, the model does not hand you one paragraph and overwrite your draft — it creates a take, and that take becomes a node on a tree.

Left and Right flip between sibling takes at the same point in the story. Pressing D deletes a take you do not want. Regenerating adds another sibling rather than destroying the previous one. The practical consequence is that rejection becomes reversible: if you cut a scene in chapter three and decide two weeks later that the earlier version was better, it is still there.

Most competitors implement the opposite model. A chat interface is a linear stream — you type, the model replies, and the earlier reply is either buried in scrollback or gone entirely. Even purpose-built fiction tools generally regenerate in place, which forces the writer to make a keep-or-discard decision before they have enough context to make it well.

The map view (`m`) is what makes a tree of takes legible. It cycles through three lenses:

| Map lens | What it shows |
|---|---|
| Path | Only the currently selected story line, i.e. the manuscript as it stands |
| Tree | Every branch, including takes you have not selected |
| Mass | Word-count bars per line, so you can see structural weight at a glance |

That third lens is the interesting one. Word-count bars turn the story tree into something closer to a project dashboard — you can see which subplot has run long and which chapter is thin without reading a word.

## Why Does Local-First Privacy Matter for AI Fiction Writing?

Fiction is unusually sensitive material. Unpublished manuscripts are the writer's competitive asset, and cloud drafting tools necessarily hold a copy. 1667's answer is structural rather than a policy promise: the software has no account system to log into and no server to phone home to.

According to the vendor's own documentation, 1667 ships with **no account, no analytics, no telemetry, no crash reporter and no install ID**. Stories are stored in a project folder you pick, and API keys live in a private file outside that folder. An update check is enabled by default and can be disabled in settings.

That is the direct inverse of the cloud SaaS model. Sudowrite is a browser-based service positioned as "the non-judgemental AI writing partner," with an account, a credit balance and bundled proprietary models — Muse 1.5 and Ballad — alongside 30-plus industry models, and no bring-your-own-key option on the lower tiers. Novelcrafter is a web platform organised around a Codex story bible, with bring-your-own-key AI unlocking only from the Hobbyist tier upward.

To be precise about what local-first does and does not mean here: the *software* is local, but the *model* may not be. If you point 1667 at OpenAI, your prose still leaves the machine. The privacy claim only becomes complete when you pair it with a local endpoint.

## Which Models Does 1667 Work With — Cloud, Local, or Both?

1667 is model-agnostic by design. The settings screen exposes presets for OpenAI, Anthropic, OpenRouter, Ollama, LM Studio, llama.cpp and KoboldCpp, plus a custom endpoint option. A local model needs no API key at all.

The documented starting defaults are:

| Setting | Default value | Range |
|---|---|---|
| Temperature | 0.8 | Adjustable |
| Max output tokens | 2,048 | Adjustable |
| Context window | 32,768 | 1 to 1,000k |
| Cache policy | off | — |
| Update check | on | Disableable |

The 32,768-token default context window is the number to watch. A novel-length project will outgrow it, and the adjustable ceiling of 1,000k tokens means the practical limit is your model's own context length, not the tool's. Temperature 0.8 is a sensible default for prose — high enough to produce varied takes, not so high that the model stops making sense, which matters when the whole workflow depends on generating *several* candidates and choosing between them.

The local-model path is where the combination gets interesting. Ollama, LM Studio, llama.cpp and KoboldCpp all run on your own hardware, which means an offline drafting loop with no key, no account and no per-token cost. Generation is slower and the prose quality depends entirely on which model you load — see our [best local LLM models guide](/posts/best-local-llm-models-2026/) for what is actually viable on consumer hardware in 2026, and our [Aider plus Ollama setup guide](/posts/aider-ollama-local-coding-2026/) for the general shape of wiring a local endpoint into a tool.

## How Do You Install 1667 and Write the First Paragraph?

1667 ships four installation paths, which is unusually broad for a pre-1.0 project:

| Install method | Command / requirement | Platform |
|---|---|---|
| Shell script | `curl` installer from 1667.ai | macOS arm64/x64, glibc 2.17+ Linux |
| PowerShell | Windows installer script | Windows x64 |
| npm | `@1667-ai/cli` (Node 22) | Cross-platform |
| Source | Bun 1.3.14 + Node 22 | All supported |

The npm route installs the [`@1667-ai/cli` package](https://www.npmjs.com/package/@1667-ai/cli) on Node 22. Once installed, the onboarding story is deliberately small. The starter key set is documented as eight keys, and the full command reference runs to roughly 40 commands — a scope that fits on a reference card rather than requiring a manual.

The workflow itself is three keys:

1. **Space** continues the current line of prose. The model writes one take and stops.
2. **Enter** supplies a *direction* — a nudge about what should happen next — and again produces a single take.
3. **Left/Right** flips between sibling takes at the current point so you can compare them before keeping one.

For writers migrating from other tools, 1667 provides importers for SillyTavern (chats, swipes, character cards, World Info) and NovelAI (stories, scenarios, Lorebooks, retry history). That matters more than it looks: it means a writer with years of accumulated character cards and lore is not starting from an empty project folder.

## 1667 vs Sudowrite vs Novelcrafter: Which Fits Your Workflow?

These three tools do different jobs, and the pricing structures encode the difference. 1667 is free software that you pay your model provider for, or nothing at all with a local model. The other two are subscriptions.

| Dimension | 1667 | Sudowrite | Novelcrafter |
|---|---|---|---|
| Price | Free (Apache-2.0) | $10–$44/mo | $4–$20/mo |
| Billing unit | None — you pay your endpoint | Credits (225k–2M/mo) | Flat monthly |
| Interface | Terminal, keyboard-only | Browser | Browser |
| Model access | BYOK — any endpoint, presets for 8 providers | Bundled proprietary (Muse 1.5, Ballad) + 30+ models | BYOK, unlocks from Hobbyist tier |
| Local model support | Yes (Ollama, LM Studio, llama.cpp, KoboldCpp) | No | No |
| Account required | No | Yes | Yes |
| Drafting model | Branching take tree | 300-word continuations with options | Codex-first scene beats |
| Whole-novel generation | No | Yes (Story Engine) | No |
| Organisation layer | Story tree + word-count map | Story Bible | Codex wiki with character/location tracking |
| Migrations | SillyTavern, NovelAI importers | — | — |

Sudowrite's [pricing page](https://www.sudowrite.com/pricing) lists Hobby & Student at $10/month for 225,000 credits, Professional at $22/month for 450,000 credits (1,000,000 listed), and Max at $44/month for 2,000,000 credits, with unused credits rolling over for 12 months. Novelcrafter's [pricing page](https://www.novelcrafter.com/pricing) lists Scribe at $4, Hobbyist at $8, Artisan at $14 and Specialist at $20 per month, with AI as bring-your-own-key and available only from Hobbyist upward; the platform also claims a community of 220,000-plus authors on a 21-day free trial.

The credit-versus-flat distinction matters for budgeting. Sudowrite bills in credits, so heavy regeneration spends real money and the cheapest way to economise is to generate fewer takes — which is precisely the behaviour a divergence-based drafting tool wants to encourage. 1667 has the opposite incentive structure: with a local model, generating ten takes costs the same as generating one, and the tree is designed to hold all of them. If you want the wider landscape of paid tools, our [best AI content writing tools](/posts/best-ai-content-writing-tools-2026/) roundup covers that side of the market.

## Why Did 1667's Launch Trigger 94 Hacker News Comments?

The [Show HN post for 1667](https://news.ycombinator.com/item?id=49330604) landed on 2026-08-17 and reached 37 points with 94 comments — and the thread was strongly polarised. This is worth reading as evidence about the market, not just about the tool.

The author, refsab, later said in the thread that the launch post "marketed it the wrong way" and that he had started receiving a lot of hate mail. His counter-framing is unusual and worth quoting for what it reveals about intent: he positions 1667 as "a form of low tech holodeck" and as "choose your own adventure," explicitly not as a machine for producing slop books.

That distinction is the whole argument. A tool marketed as *generate my novel* invites the objection that it removes the writer. A tool marketed as *generate options, and I choose* is a different proposition — closer to an instrument than an author. The take tree is the architectural expression of that second framing: the software is structurally biased toward the human making decisions, because the model's output is never committed to the manuscript automatically.

The counter-position in the same thread came from writers who reject generation entirely — the "assist, do not generate" school, represented by tools that plan storylines and give structural feedback instead of producing prose. That is a coherent rival philosophy, and it is the sharpest criticism of 1667's core premise: if the value of drafting is the struggle, handing the struggle to a model is the wrong trade no matter how many branches the tree holds.

For a wider view of how LLM-assisted writing is being received, our [ChatGPT vs Claude vs Gemini writing comparison](/posts/chatgpt-vs-claude-vs-gemini-writing-2026/) looks at the underlying model differences that drive prose quality.

## Is 1667 Worth Using, and What Are Its Limits?

The honest verdict is that 1667 is a genuinely novel UX wrapped around young, small-scale software — and the maturity question deserves a straight answer.

**Where it is strong:**

- The take tree is not a marketing gimmick. It is a real workflow change that no major competitor replicates, and it produces a reviewable history of every decision you made.
- Local-first design removes an entire category of concern for unpublished work — there is no account, no telemetry stream and no install ID.
- Bring-your-own-endpoint plus four local-model integrations means the marginal cost of drafting can be genuinely zero.
- Apache-2.0 with no paid tier and no upsell means no feature is withheld behind a subscription.

**Where it is limited:**

- It is pre-1.0 software. Stable is 0.10.9 with 0.11.0-beta.5 in prerelease, and the version history shows an actively shifting codebase.
- The project is small. 26 stars, 0 forks and 7 open issues as of 2026-10-01 is an early-stage repository, and the bus factor is real.
- It is text-only. There is no graphics, video or publishing pipeline — it is a drafting environment, not a content platform, and a [third-party review from 2026-08-17](https://kompozy.io/reviews/1667) scored it 4.0/5 while making exactly this point.
- It does not organise your manuscript. Sudowrite's Story Bible and Novelcrafter's Codex exist because novel-length projects need character and continuity tracking; 1667's tree is a drafting structure, not a story bible.
- The terminal is a filter. If you do not already live in a terminal, the keyboard-first UX is a cost, not a feature.

**Who it is for:** writers who already work in a terminal, fiction writers who want to run a local model for privacy or cost reasons, and anyone frustrated by regenerating in place and losing the version they actually wanted.

**Who it is not for:** authors who want a single generated draft, writers who need story-bible continuity management, and anyone who needs support guarantees from a funded vendor.

The broader context is that AI writing tools are a large and growing category. Third-party industry trackers put the AI writing tools market at roughly $4.2B in 2026 heading toward about $12B by 2030, with the AI novel-writing segment around $450M in 2025 moving toward roughly $1.6B by 2032 at about 19.9% CAGR. Treat those as directional estimates rather than measured figures. What matters for the review is the shape of the competition: 1667 is betting that a subset of that market wants *less* — fewer features, less cloud, more control over the branch point.

## FAQ

### What is 1667 and what does it do?

1667 is a free, open-source, full-screen terminal application for writing fiction with large language models. It generates one passage at a time and stores every generated take as a sibling branch on a navigable story tree, so rejected drafts are preserved rather than overwritten. It is local-first and works with cloud or local model endpoints.

### Is 1667 really free?

Yes. 1667 is Apache-2.0 licensed with no paid tier and no account. You pay only your model provider — or nothing at all if you point it at a local endpoint such as Ollama, LM Studio, llama.cpp or KoboldCpp, which requires no API key.

### Can I use 1667 with a local model like Ollama?

Yes. 1667 ships presets for Ollama, LM Studio, llama.cpp, KoboldCpp and custom endpoints alongside OpenAI, Anthropic and OpenRouter. Running a local model gives you an offline drafting loop with no key, no account and no per-token cost, though generation speed and prose quality depend on the model you load.

### How is 1667 different from Sudowrite or Novelcrafter?

1667 is free, terminal-based and bring-your-own-model, while Sudowrite and Novelcrafter are paid browser subscriptions. Sudowrite bills $10–$44/month in credits and bundles its own fiction-tuned models; Novelcrafter runs $4–$20/month with bring-your-own-key AI from the Hobbyist tier. 1667's distinguishing feature is the take tree, which keeps every generated branch instead of regenerating in place.

### Is 1667 private, and does it send my writing anywhere?

The software itself keeps no account, no analytics, no telemetry, no crash reporter and no install ID, and stores stories in a project folder you choose with API keys in a separate private file. However, if you configure a cloud endpoint, your prose is sent to that provider. Privacy is only complete when you pair 1667 with a local model.
