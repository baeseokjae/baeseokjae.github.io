---
title: 'All-AI-Jailbreaks Archive Review: What the Repository Can and Cannot Prove'
date: 2026-08-26 16:01:38+00:00
tags:
- AI Security
- Prompt Injection
- Jailbreak Research
- LLM Security
- Red Teaming
- AI Robustness
description: A dated audit of the All-AI-Jailbreaks repository, with a downloadable file inventory and a defensive evaluation worksheet.
draft: false
cover:
  image: /images/og-default.png
  alt: RockB editorial guides
  relative: false
schema: schema-all-ai-jailbreaks-prompt-injection-archive-2026
lastmod: '2026-10-20T07:02:10.628622+00:00'
---

All-AI-Jailbreaks is a collection of community prompt experiments. It can supply leads for defensive research, but a filename naming a model does not establish that the prompt works against that model today. This review examines the repository's inventory and documentation, not the effectiveness of its payloads.

The useful question is whether you can turn a claimed failure into a reproducible, authorized test of your own application. A collection size or a dramatic title is not an attack-success rate.

## A snapshot, not a live compatibility matrix

The repository snapshot checked on October 20, 2026 uses commit `7cc8d138892c9fb9b8bf2e3fbe862a73b4ba3f9d`. Its [repository metadata](https://api.github.com/repos/buryusu/All-AI-Jailbreaks) reports a latest push on September 9, 2026. That timestamp is evidence of a repository update, not of continued testing against current model releases.

The [downloadable inventory](/research/content-quality-2026-10/archive-inventory.json) records **31 files** in the pinned tree. Excluding six image assets, the README, three `CLAUDE` instruction files, and two launcher scripts leaves **19 candidate prompt files**. This is a reproducible file classification, not a count of independently validated attacks.

The README's named list and the file tree do not line up exactly: the named Grok item is absent from the inspected tree, while `2nd antigravity` appears in the tree. Product labels and model labels are also mixed. Treat the README as a navigation aid and verify the actual file revision before citing an experiment.

## What the inventory does not establish

A repository can contain several variants of one idea, old experiments, or prompts aimed at an interface rather than a standalone model. Counting each file as a distinct vulnerability would overstate the evidence.

The inventory does not determine which instructions were active, whether a response was edited, what tool permissions were available, or whether an action actually occurred. It also does not establish permission to redistribute the contents: public accessibility and a clear license are different facts.

For this audit, only metadata, filenames, and documentation were inspected. The launchers and prompt files were not executed or loaded into an agent workspace. Repository instruction files are part of the material being reviewed, not instructions for the reviewer.

## Convert a candidate into an application test

Use the [evaluation worksheet](/research/content-quality-2026-10/archive-evaluation.csv) to record the claim before testing it. Replace private information with synthetic markers and use an environment where you have permission to perform the evaluation.

| Question | Minimum evidence |
|---|---|
| What is the legitimate task? | A benign request with a known successful outcome |
| Where does untrusted content enter? | Retrieval document, tool result, uploaded file, or user input |
| Which boundary is challenged? | Answer content, private context, tool authorization, or external side effect |
| What exactly ran? | Model identifier, date, client, instructions, settings, and file revision |
| What happened? | Raw response plus application/tool log, with secrets removed |
| Does the task still work? | A paired benign control after applying a defense |

[OWASP LLM01](https://genai.owasp.org/llmrisk/llm01-prompt-injection/) is a risk-category identifier; it is not a prevalence ranking produced by this archive. The [OWASP prevention guidance](https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html) provides a better starting point for controls than assuming that one prompt filter solves the problem.

## Use separate outcome labels

Record at least three outcomes separately: the model attempted to violate the task boundary; the application accepted an unauthorized operation; and the user received protected information or an unintended result. A model can attempt a forbidden call while the application correctly blocks it.

Keep the total number of attempts and successful benign controls beside the failure count. If changing the defense causes every benign task to fail, report that loss of utility. If the model, retrieval pipeline, or permissions change, treat the next run as a new configuration.

The [automated red-teaming guide](/posts/automated-red-teaming-ai-agents/) includes an offline boundary example with an actual execution record. It is a useful regression fixture, but it is not evidence that the archive's prompts were tested or that any model is immune to injection.

## Revision note

**Updated October 20, 2026.** Removed the definitive-archive and blanket current-model coverage claims. Added a pinned inventory, the README/tree discrepancy, and a defensive evaluation method. No jailbreak success rate is claimed.

## Primary sources

Checked October 20, 2026: [archive meta](https://api.github.com/repos/buryusu/All-AI-Jailbreaks); [archive commit](https://api.github.com/repos/buryusu/All-AI-Jailbreaks/commits/main); [archive tree](https://api.github.com/repos/buryusu/All-AI-Jailbreaks/git/trees/main?recursive=1); [archive readme](https://raw.githubusercontent.com/buryusu/All-AI-Jailbreaks/main/README.md); [owasp injection](https://genai.owasp.org/llmrisk/llm01-prompt-injection/); [owasp defense](https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html).
