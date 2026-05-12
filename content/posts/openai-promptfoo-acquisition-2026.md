---
title: "OpenAI Acquires PromptFoo: What It Means for AI Security Testing in 2026"
date: 2026-05-10T00:00:00+00:00
tags: ["promptfoo", "openai", "ai-security", "red-teaming", "llm-testing"]
description: "OpenAI acquired PromptFoo, the 21,151-star open-source LLM security testing tool. Here's what changes for developers, what stays the same, and what the deal signals for AI security in 2026."
draft: false
cover:
  image: "/images/openai-promptfoo-acquisition-2026.png"
  alt: "OpenAI Acquires PromptFoo: What It Means for AI Security Testing in 2026"
  relative: false
schema: "schema-openai-promptfoo-acquisition-2026"
---

OpenAI acquiring PromptFoo is not a talent grab — it is a strategic acknowledgment that AI security testing is no longer optional infrastructure. With 93% of organizations now shipping AI-generated code and only 12% applying equivalent security standards, the attack surface is enormous and growing. PromptFoo was the most mature open-source tool purpose-built for LLM red-teaming, and OpenAI buying it means the company is betting that security evaluation needs to be a first-class part of the developer workflow, not an afterthought bolted on by a third-party CLI.

## OpenAI Acquires PromptFoo: The AI Security Testing Landscape Shifts

The acquisition closed in May 2026 and immediately repositioned AI security testing from a niche DevOps concern into mainstream developer practice. PromptFoo had already crossed 21,151 GitHub stars before the deal — a signal that the developer community recognized the tool's value long before enterprise security teams caught up. OpenAI's move is directionally consistent with what the company has been doing across the stack: acquiring capabilities that strengthen its platform position rather than just its model performance. Security evaluation is exactly that kind of capability. Prior to the acquisition, LLM red-teaming existed in a fragmented ecosystem: PromptFoo handled prompt evaluation and automated vulnerability scanning, Garak covered model-level probing, Azure AI Safety focused on enterprise policy compliance, and Guardrails AI handled output validation. None of these were integrated natively into the API or development experience of any major model provider. The acquisition changes that calculus for OpenAI's developer ecosystem, and it puts pressure on Anthropic, Google DeepMind, and Mistral to respond with comparable tooling. The broader message is clear: the era where you could ship an LLM application without formal security evaluation is ending, and acquisition-backed platform integration is the mechanism accelerating that shift.

## What PromptFoo Does: 21,151 Stars and Why Developers Trust It

PromptFoo earned 21,151 GitHub stars by solving a specific problem well: it gave developers a reproducible, scriptable way to evaluate LLM behavior across prompts, models, and configurations before those prompts reached production. That sounds narrow, but the scope is larger than it appears. PromptFoo functions simultaneously as a prompt evaluation framework, an automated red-teaming engine, and a vulnerability scanner — all from a CLI or Node.js library that integrates with existing CI/CD pipelines in under an hour. The tool supports testing not just prompts but full agents and Retrieval-Augmented Generation (RAG) pipelines, which means security teams can evaluate multi-step agentic behaviors rather than single-turn responses. It has been actively maintained since 2023 with consistent release cadence, which in the open-source security tooling space is a meaningful differentiator — abandoned tools are common, and security tooling that falls behind model updates becomes useless fast. The automated vulnerability scanner covers the categories that matter most in 2026 production deployments: prompt injection, data leakage, jailbreak susceptibility, and unsafe content generation. Output is a structured report with severity levels, making it actionable for both developers and security reviewers. The depth of its evaluation configuration — supporting multi-turn conversations, custom assertion logic, and model comparison across providers — is what separates PromptFoo from simpler benchmarking tools. You can test the same prompt against GPT-4o, Claude 3.5 Sonnet, and Llama 3 in a single config file and get a comparative security posture report.

### Core PromptFoo Capabilities at a Glance

| Capability | Description |
|---|---|
| Prompt Evaluation | Batch-test prompts against assertions across multiple models |
| Agent Testing | Evaluate multi-step agent behaviors and tool use |
| RAG Security | Test retrieval pipelines for data leakage and injection |
| Red-Teaming | Automated adversarial probing with 40+ attack strategies |
| Vulnerability Reports | Severity-ranked findings with remediation context |
| CI/CD Integration | CLI and Node.js API for pipeline-native testing |
| Provider Coverage | OpenAI, Anthropic, Cohere, Mistral, local models |

## Why OpenAI Bought a Security Testing Tool

OpenAI's acquisition rationale becomes obvious when you examine what the company needs to sustain enterprise adoption at scale. Enterprise buyers in 2026 do not deploy LLM applications without security validation requirements — regulated industries including finance, healthcare, and government have compliance mandates that now explicitly reference AI system testing. OpenAI needed a credible answer to the question every enterprise security team asks: "How do we know this model is safe before we put it in front of customers?" Buying PromptFoo gives OpenAI that answer in the form of a production-grade tool with an established developer reputation. There is also a platform lock-in dimension worth examining. By integrating PromptFoo into the OpenAI developer workflow, the company creates a security evaluation layer that naturally deepens dependency on OpenAI's API and tooling ecosystem. Developers who use OpenAI's integrated security testing are less likely to switch providers because their evaluation baselines and historical test results live inside OpenAI's platform. The acquisition also gives OpenAI direct influence over how security standards for LLM applications are defined at the tooling level — a form of standards leadership that complements its ongoing involvement in AI policy discussions. From a technical standpoint, OpenAI gains a team that has spent years thinking about LLM failure modes in production, which is directly valuable for improving model alignment and safety evaluation internally. The dual-use value — external developer tool and internal safety research — makes PromptFoo an unusually high-leverage acquisition for the price.

## What Changes for Existing PromptFoo Users

Per the acquisition announcement, PromptFoo will remain open-source post-acquisition, which is the answer most existing users needed first. The MIT-licensed codebase on GitHub is not being closed or converted to a proprietary product. For the 21,151+ developers who starred the repository and the teams running PromptFoo in production today, the day-to-day experience of using the CLI does not change immediately. What does change — and what makes the acquisition valuable for users — is the depth of integration with OpenAI's platform. PromptFoo users will gain access to richer model internals for evaluation purposes: better access to logprobs, token-level confidence scores, and model metadata that were previously limited by API constraints. This translates directly into more precise vulnerability detection, since many prompt injection and jailbreak attacks are detectable through output probability distributions rather than just final text. Longer term, the integration signals that OpenAI intends to make security evaluation a native part of its API offering rather than a third-party concern. Expect PromptFoo's red-teaming capabilities to appear as features in OpenAI's developer console, with tighter feedback loops between evaluation results and model fine-tuning workflows. For teams currently running PromptFoo in CI/CD pipelines, the acquisition also reduces vendor risk: the tool is now backed by one of the best-funded AI companies in the world, which means sustained maintenance and model compatibility updates as new versions of GPT models ship.

## AI Security Vulnerabilities: The 25.1% Problem with AI-Generated Code

The statistic that frames the urgency behind this acquisition: 25.1% of code samples generated by AI contain a confirmed security vulnerability. That is not a marginal edge case — it means roughly one in four code blocks your AI coding assistant produces carries a real exploitable flaw. Compound that with the organizational reality that 93% of development teams now use AI-generated code in some form, and only 12% apply security standards equivalent to what they apply to human-written code, and the scale of the exposure becomes clear. PromptFoo's role in addressing this is specific to the LLM application layer — it does not scan the code your AI generates for SAST findings (tools like Semgrep and Snyk do that), but it does test the behavior of the LLM application itself: does your chatbot leak system prompt contents? Can an attacker manipulate your RAG pipeline to return sensitive documents? Will your AI agent execute arbitrary instructions injected through user input? These are not hypothetical concerns. Prompt injection attacks against deployed LLM applications increased significantly through 2025 and into 2026 as more organizations shipped customer-facing AI features without adversarial testing. The 25.1% vulnerability rate in generated code is alarming on its own; the absence of behavioral security testing for the LLM applications wrapping that code creates a compounding risk surface. PromptFoo's automated scanning addresses exactly this gap — it runs the adversarial test cases that security teams lack the time and LLM-specific expertise to write manually, and it generates reports that give non-specialists actionable remediation paths.

## PromptFoo vs Garak vs Azure AI Safety vs Guardrails AI

With OpenAI absorbing PromptFoo, the competitive landscape for LLM security tooling clarifies into distinct approaches that serve different use cases. Garak is the open-source model-level scanner from NVIDIA research — it probes the base model for inherent vulnerabilities (bias, toxicity, encoding attacks, jailbreaks at the model layer) rather than testing application-level behavior. Garak is the right tool when you are evaluating a model itself, or fine-tuning a model and need to verify the fine-tuning did not introduce new vulnerabilities. PromptFoo operates at the application layer — it tests how your specific prompt configuration, system prompt, and application logic behave under adversarial conditions. The two tools are complementary rather than competing, though PromptFoo's scope is broader for production application teams. Azure AI Safety evaluation is Microsoft's answer for teams already inside the Azure ecosystem: it offers content safety classifiers, groundedness evaluation for RAG, and prompt shield integration. Its coverage is narrower than PromptFoo's red-teaming suite but requires zero additional infrastructure if you are on Azure OpenAI Service. The trade-off is vendor lock-in and less configurability for custom attack scenarios. Guardrails AI takes a runtime validation approach — it wraps LLM API calls with validators that enforce output schemas, detect sensitive data, and block policy-violating responses in production. It is not a pre-deployment testing tool but a production guardrail. Teams doing serious LLM security work in 2026 typically run PromptFoo or Garak for pre-deployment red-teaming and Guardrails AI in production, treating the layers as complementary.

### Comparison: LLM Security Testing Tools 2026

| Tool | Layer | Approach | Open Source | Best For |
|---|---|---|---|---|
| PromptFoo | Application | Red-teaming + eval | Yes (MIT) | Pre-deployment app testing |
| Garak | Model | Probe-based scanning | Yes (Apache 2.0) | Model evaluation, fine-tune QA |
| Azure AI Safety | Application | Content safety + policy | No | Azure-locked enterprise teams |
| Guardrails AI | Runtime | Output validation | Yes (Apache 2.0) | Production guardrails |
| LlamaGuard | Model | Safety classification | Yes (Meta) | Input/output content filtering |

## How to Use PromptFoo for LLM Security Testing Today

Getting PromptFoo running against your LLM application takes under 15 minutes for the initial setup, and the investment pays for itself the first time it catches a prompt injection path before your code reaches staging. Install via npm with `npx promptfoo@latest init`, which scaffolds a default `promptfooconfig.yaml` in your project directory. The configuration file is where you define your targets (which models and API endpoints to test), your prompts (including your system prompt and any few-shot examples), and your test cases (either hand-written or auto-generated by PromptFoo's red-teaming module). For automated vulnerability scanning, the key command is `npx promptfoo redteam run` — this triggers PromptFoo's built-in adversarial probe suite, which covers 40+ attack strategies including indirect prompt injection, jailbreak sequences, data exfiltration attempts, and role-play manipulation. The output is a JSON or HTML report with findings ranked by severity (critical, high, medium, low) and attack category. For CI/CD integration, add `npx promptfoo eval --ci` to your pipeline and configure it to fail the build if any critical findings are detected. This enforces a security gate before deployment without requiring a manual security review on every change. For RAG applications specifically, configure the `rag` target type in your promptfooconfig to point at your retrieval endpoint — PromptFoo will probe it for context poisoning, document leakage, and over-retrieval vulnerabilities that are common failure modes in production RAG systems.

### Example promptfooconfig.yaml for Red-Teaming

```yaml
targets:
  - openai:gpt-4o

prompts:
  - "You are a helpful assistant. {{user_input}}"

redteam:
  plugins:
    - promptInjection
    - dataLeakage
    - jailbreak
    - harmfulContent
  strategies:
    - jailbreak
    - promptInjection

evaluateOptions:
  maxConcurrency: 4
```

Running `npx promptfoo redteam run` against this config exercises your application against the four highest-impact vulnerability classes and produces a severity-ranked report that a security reviewer can act on immediately, without needing deep LLM security expertise.

## What This Acquisition Means for the AI Security Ecosystem

The PromptFoo acquisition is a forcing function for the entire AI security ecosystem, and its impact extends well beyond the OpenAI developer community. When a major model provider acquires the leading open-source security evaluation tool and integrates it into its platform, it sets a new baseline expectation: deploying an LLM application without formal security evaluation becomes the exception rather than the norm. That shift has downstream effects on every layer of the stack. AI security market growth — already significant as enterprises accelerate LLM deployments — will accelerate further as the acquisition increases awareness that this category of tooling exists and is production-ready. Expect Anthropic, Google DeepMind, and Mistral to accelerate their own security evaluation offerings in response, either through acquisitions of their own (Garak and Guardrails AI are the obvious targets) or through significant internal investment. The open-source community effect is equally important: PromptFoo remaining open-source while receiving OpenAI's resources means the tool gets better faster, which benefits the entire ecosystem including teams that compete with OpenAI. That is a deliberate strategic choice — a closed PromptFoo would fragment the community and encourage competitors; an open one lets OpenAI benefit from continued community contributions while building proprietary integration value on top. For security engineers and developers working on LLM applications today, the practical takeaway is straightforward: start using PromptFoo now, before the OpenAI integration deepens. The tool's core red-teaming and evaluation capabilities are mature, provider-agnostic, and free. Getting security evaluation embedded in your development workflow now, before your compliance team mandates it or your enterprise customer asks for it in their security questionnaire, is the highest-leverage action available for teams shipping LLM applications in 2026.

---

## Frequently Asked Questions

**1. Will PromptFoo stay free to use after the OpenAI acquisition?**

Yes. OpenAI confirmed that PromptFoo will remain open-source post-acquisition under its existing MIT license. The core CLI and library are free to use against any LLM provider. OpenAI may introduce paid platform features — such as deeper API integrations or hosted evaluation dashboards — but the open-source base will continue to be maintained on GitHub.

**2. Does PromptFoo only work with OpenAI models?**

No. PromptFoo has always been provider-agnostic and continues to support Anthropic Claude, Cohere, Mistral, Llama (via Ollama or compatible endpoints), AWS Bedrock, Azure OpenAI Service, and any OpenAI-compatible API. The acquisition does not restrict its model support, though future integrations may offer deeper native features for OpenAI's APIs.

**3. What is the difference between PromptFoo red-teaming and traditional penetration testing?**

Traditional penetration testing is manual, time-bounded, and focuses on infrastructure and application vulnerabilities. PromptFoo red-teaming is automated, runs continuously in CI/CD, and focuses specifically on LLM behavioral vulnerabilities: prompt injection, jailbreaks, data leakage, and harmful content generation. The two approaches address different attack surfaces and are complementary — a mature LLM security program uses both.

**4. How does PromptFoo compare to just writing manual test cases for your LLM app?**

Manual test cases catch known failure modes. PromptFoo's automated red-teaming generates adversarial probes you would not write manually — it applies 40+ attack strategies including indirect prompt injection sequences, multi-turn jailbreak patterns, and encoding-based bypasses that require specialized LLM security knowledge to construct. The combination of manual test cases for expected behavior and automated red-teaming for adversarial resilience gives you coverage that neither approach provides alone.

**5. Should I switch from PromptFoo to a different tool now that OpenAI owns it?**

Not based on the acquisition alone. OpenAI has committed to keeping PromptFoo open-source, provider-agnostic, and community-maintained. If you are using PromptFoo to evaluate Anthropic or Mistral models, those use cases are unaffected. The only scenario where switching makes sense is if you have compliance requirements around vendor neutrality in your security tooling — in that case, Garak (Apache 2.0, NVIDIA research) is the most mature alternative for model-level evaluation.
