---
title: "All-AI-Jailbreaks: The Definitive AI Jailbreak & Prompt Injection Archive for 2026"
date: 2026-08-26T16:01:38+00:00
tags:
  - AI Security
  - Prompt Injection
  - Jailbreak Research
  - LLM Security
  - Red Teaming
  - AI Robustness
description: "A review of the All-AI-Jailbreaks archive: 19 prompt-injection and jailbreak experiments across 9 model families, mapped to OWASP LLM01 and NIST guidance."
draft: false
cover:
  image: "/images/all-ai-jailbreaks-prompt-injection-archive-2026.png"
  alt: "All-AI-Jailbreaks: An Archive of Prompt-Injection & Jailbreak Experiments"
  relative: false
schema: "schema-all-ai-jailbreaks-prompt-injection-archive-2026"
---

The All-AI-Jailbreaks repository is a curated, actively maintained archive of 19 prompt-injection and jailbreak experiment files spanning at least nine major model families, including DeepSeek, Gemini, GLM, Grok, Kimi, Qwen, Sonnet, ChatGPT, and Antigravity. It is best understood not as a "how to jailbreak" list but as a structured red-teaming corpus that maps directly onto the OWASP Top 10 for LLM Applications, where prompt injection ranks as LLM01:2025 — the number-one vulnerability in the industry. This review explains what the archive contains, how its five research themes align with the OWASP taxonomy, and how it fits the broader 2026 AI-security ecosystem of automated red-teaming frameworks and defensive proxies.

## What Is the All-AI-Jailbreaks Archive?

All-AI-Jailbreaks is a GitHub repository created on 2026-08-18 and last pushed on 2026-08-20, making it a current, actively maintained 2026 resource. It is organized as a research corpus rather than a collection of ready-to-use exploits. The repository's own framing is explicit: it is a red-teaming and adversarial-robustness resource, not a guarantee of effectiveness for any given prompt.

The archive is tagged across nine security topics, including `adversarial-prompts`, `ai-robustness`, `jailbreak-research`, `llm-security`, `prompt-injection`, and `red-teaming`. This tagging is significant because it signals the intended audience: security researchers, red teams, and AI-safety engineers who need a reproducible reference set for testing model behavior under adversarial conditions.

| Attribute | Detail |
|-----------|--------|
| Repository | buryusu/All-AI-Jailbreaks |
| Created | 2026-08-18 |
| Last pushed | 2026-08-20 |
| Prompt files | 19 |
| Model families covered | 9 (DeepSeek, Gemini, GLM, Grok, Kimi, Qwen, Sonnet, ChatGPT, Antigravity) |
| Security topics tagged | 9 (incl. adversarial-prompts, ai-robustness, jailbreak-research, llm-security, prompt-injection, red-teaming) |
| Primary framing | Research / red-teaming corpus |

The repository also includes a suggested evaluation workflow: run prompts in an isolated test environment, record the model, version, settings, and date for every trial, and compare results across repeated trials. This emphasis on provenance and reproducibility is what separates a serious research archive from a casual list of tricks.

## Why Prompt Injection Is the #1 LLM Risk (OWASP LLM01)

The OWASP Top 10 for Large Language Model Applications ranks prompt injection as LLM01:2025 — the number-one vulnerability in the category. According to OWASP, prompt injection occurs when user prompts alter the model's intended behavior or override its instruction hierarchy. The taxonomy distinguishes two primary forms:

- **Direct prompt injection:** A user deliberately crafts a prompt to override the system instructions or bypass safety guardrails.
- **Indirect prompt injection:** Malicious instructions are embedded in content the model ingests from external sources, such as a webpage, document, or email, and the model follows them without the user's awareness.

Both forms are top-tier LLM security risks because they target the model's core trust boundary: the separation between system instructions and untrusted user or third-party input. When that boundary collapses, the model can leak data, execute unintended actions, or produce harmful output.

The All-AI-Jailbreaks archive is directly relevant to this taxonomy because its prompts are organized around the same failure modes that OWASP identifies. Understanding the archive is, in effect, understanding the practical attack surface behind LLM01.

## Inside the Archive: 19 Prompts Across 9 Model Families

The archive's breadth is one of its strongest assets. Most jailbreak collections focus on a single model or vendor. All-AI-Jailbreaks instead spans nine model families, which makes it valuable for cross-model robustness testing.

| Model family | Relevance to the archive |
|--------------|--------------------------|
| DeepSeek | Open-weight model, frequent target of jailbreak research |
| Gemini | Google's flagship multimodal family |
| GLM | Zhipu AI's open-weight Chinese model family |
| Grok | xAI's model, known for looser default guardrails |
| Kimi | Moonshot AI's long-context model |
| Qwen | Alibaba's open-weight family |
| Sonnet | Anthropic's Claude Sonnet tier |
| ChatGPT | OpenAI's flagship consumer model |
| Antigravity | Emerging model family in the 2026 landscape |

The value of this breadth is that a prompt that fails against one model may succeed against another, and vice versa. For a red team, this cross-model coverage reveals which defenses are model-specific and which reflect generalizable weaknesses in the current generation of LLM alignment techniques. For a security team evaluating a vendor, the archive provides a ready-made battery of prompts to test whether a chosen model inherits known weaknesses from its family.

## The 5 Research Themes That Structure the Collection

The archive organizes its 19 prompt files around five research themes. Each theme corresponds to a distinct class of adversarial technique, and each maps to a specific concern in the OWASP LLM01 taxonomy.

**1. Instruction hierarchy.** These prompts probe whether a model can be made to treat user instructions as higher-priority than its system instructions. This is the core of direct prompt injection and the most fundamental jailbreak vector.

**2. Role and persona conditioning.** These prompts attempt to shift the model into a persona or role that bypasses its guardrails — for example, asking it to "act as" an unrestricted assistant or a fictional character with no safety constraints.

**3. Response-format control.** These prompts exploit the model's instruction-following behavior around output formatting, such as asking for content inside a code block, a table, or a translation that the safety layer fails to inspect.

**4. Cross-model variants.** These are prompts adapted or generalized across multiple model families, testing whether a technique that works on one model transfers to others.

**5. Adversarial robustness.** These prompts stress-test the model's overall resistance to manipulation, including combinations of the above techniques and novel obfuscation strategies.

Mapped to OWASP, themes 1 and 2 are classic direct prompt injection, theme 3 is a response-format bypass, and themes 4 and 5 are the cross-model and robustness dimensions that OWASP's guidance encourages security teams to evaluate continuously.

## How the Archive Fits the 2026 AI-Security Ecosystem

The All-AI-Jailbreaks archive does not exist in isolation. It sits at the input end of a growing 2026 AI-security ecosystem that includes both offensive tooling and defensive countermeasures.

On the offensive side, archives like this feed automated red-teaming frameworks. DeepTeam, an open-source framework from Confident AI, automates adversarial testing of prompts and agents against jailbreak and injection vectors. A curated archive provides the seed corpus that such frameworks use to generate and evaluate attacks at scale.

On the defensive side, the archive informs tools like Aegis.rs, an open-source Rust-based LLM security proxy that filters and guards against prompt injection at inference time. Understanding the attack surface documented in archives like All-AI-Jailbreaks is precisely what allows defensive proxies to recognize and block malicious patterns before they reach the model.

| Ecosystem layer | Example tool | Role |
|-----------------|--------------|------|
| Attack corpus | All-AI-Jailbreaks | Curated jailbreak and injection prompts |
| Offensive automation | DeepTeam | Automated red-teaming of prompts and agents |
| Defensive proxy | Aegis.rs | Inference-time filtering of injection attempts |
| Standards | OWASP LLM Top 10 | Canonical vulnerability taxonomy |
| Government guidance | NIST AI 100-2 | Adversarial ML terminology and mitigations |

This ecosystem is also anchored by authoritative standards. NIST AI 100-2e2025, the updated US-government reference for adversarial machine learning, categorizes evasion, poisoning, and prompt-injection-style attacks and concludes that there is "no silver bullet" against them. Defense, NIST argues, requires layered, continuous evaluation — which is exactly the workflow the All-AI-Jailbreaks archive is designed to support.

## The Reproducibility Problem: Why Prompts Drift

One of the most important lessons in the archive's own documentation is that model behavior drifts. A prompt that reliably bypasses a model's guardrails in one week may fail the next, because vendors continuously update alignment, safety filters, and instruction hierarchies. This is not a bug in the archive; it is a fundamental property of the systems it studies.

The practical consequence is that no jailbreak prompt should be treated as a permanent, guaranteed exploit. The archive's suggested evaluation workflow addresses this directly:

- Run every prompt in an **isolated test environment** so you are not testing against production systems or real user data.
- **Record the model, version, settings, and date** for every trial, so results are attributable and reproducible.
- **Compare across repeated trials**, because a single success or failure is not statistically meaningful given model nondeterminism.

This reproducibility discipline is also why the archive's contributing guidelines require provenance: every submitted prompt must document the target model, date, source, and the behavior being tested. Without that metadata, a jailbreak prompt is just an anecdote; with it, the prompt becomes a data point in a longitudinal study of model robustness.

## Responsible Red-Teaming: How to Use the Archive Safely

Because the archive contains working adversarial prompts, it must be used responsibly. The repository itself frames its content as research, and anyone working with it should follow the same discipline.

**Use an isolated environment.** Never run jailbreak prompts against production systems, live user data, or models connected to real tools and APIs. The risk of indirect prompt injection is that a successful jailbreak can trigger unintended actions with real-world consequences.

**Respect terms of service and law.** Testing a model you do not own, or probing a service in ways that violate its terms, can have legal and account-level consequences. Red-teaming is legitimate when it is authorized and scoped; it is not a license to attack systems you do not control.

**Document everything.** Follow the archive's provenance requirements. Record the model, version, settings, date, and the specific behavior under test. This turns an ad-hoc experiment into reproducible research.

**Report responsibly.** If you discover a novel, high-impact vulnerability, the responsible path is coordinated disclosure to the vendor rather than public release. The goal of red-teaming is to improve security, not to arm attackers.

**Pair offensive testing with defense.** Understanding jailbreak techniques is most valuable when it informs defensive measures — whether that means hardening your own prompts, deploying an inference-time proxy like Aegis.rs, or feeding findings into an automated red-teaming framework.

## Verdict: Is This Archive Worth Your Time?

For security researchers, red teams, and AI-safety engineers, the All-AI-Jailbreaks archive is a genuinely useful resource. Its cross-model breadth (nine families), its structured organization around five research themes, and its explicit commitment to provenance and reproducibility set it apart from the typical single-model jailbreak list.

Its main limitation is the reproducibility gap inherent to the field: prompts drift as models are updated, so the archive is a snapshot of the 2026 attack surface rather than a permanent reference. That is not a flaw in the archive itself — it is a property of the systems it studies, and the archive's own evaluation workflow is designed to account for it.

If you are building or deploying LLM applications, the archive is worth your time as a testing battery and a reference for understanding the OWASP LLM01 attack surface. If you are a casual user looking for "tricks," it is the wrong tool — and using it irresponsibly would be a mistake. Positioned correctly, All-AI-Jailbreaks is a valuable, current, and responsibly framed contribution to the 2026 AI-security ecosystem.

## FAQ

**What is the All-AI-Jailbreaks archive?**
It is a GitHub repository containing 19 curated prompt-injection and jailbreak experiment files spanning nine model families, organized as a research and red-teaming corpus rather than a list of ready-to-use exploits.

**Why is prompt injection ranked as the #1 LLM risk?**
The OWASP Top 10 for LLM Applications ranks prompt injection as LLM01:2025 because it targets the model's core trust boundary between system instructions and untrusted input, enabling data leakage, unintended actions, and harmful output.

**Which model families does the archive cover?**
The archive spans at least nine model families: DeepSeek, Gemini, GLM, Grok, Kimi, Qwen, Sonnet, ChatGPT, and Antigravity, making it valuable for cross-model robustness testing.

**How should I use the archive responsibly?**
Run prompts in an isolated test environment, record model/version/settings/date for every trial, respect terms of service, document provenance, and report novel vulnerabilities through coordinated disclosure.

**Why do jailbreak prompts stop working over time?**
Model behavior drifts because vendors continuously update alignment, safety filters, and instruction hierarchies. A prompt that works one week may fail the next, which is why the archive emphasizes repeated trials and full provenance.
