---
title: "Magistral Review 2026: Mistral Open-Weight Reasoning Model That Beats DeepSeek R1"
date: 2026-04-30T12:08:00+00:00
tags: ["magistral", "mistral", "reasoning model", "open-weight AI", "deepseek r1"]
description: "Magistral is Mistral's first open-weight reasoning model. The 24B Small variant runs locally on a MacBook and scores 73.6% on AIME-24 — beating DeepSeek R1 Zero."
draft: false
cover:
  image: "/images/magistral-mistral-reasoning-model-review-2026.png"
  alt: "Magistral Review 2026: Mistral Open-Weight Reasoning Model That Beats DeepSeek R1"
  relative: false
schema: "schema-magistral-mistral-reasoning-model-review-2026"
---

Magistral is Mistral AI's first reasoning model family, released in 2025. The 24B open-weight Small variant runs on a single RTX 4090 or 32 GB MacBook, scores 70.7% on AIME-2024 pass@1, and is licensed Apache 2.0 — making it the most capable locally-deployable reasoning model available today.

## What Is Magistral? Mistral's First Reasoning Model Explained

Magistral is the reasoning model family from Mistral AI, a French AI company founded in 2023. It comes in two variants: Magistral Small, a 24-billion-parameter open-weight model released under Apache 2.0, and Magistral Medium, a larger mixture-of-experts (MoE) model available exclusively via API. Unlike most reasoning models that distill knowledge from proprietary giants like GPT-4o or Claude, Magistral was trained using Reinforcement Learning with Verifiable Rewards (RLVR) applied directly to the Mistral Medium 3 checkpoint — no distillation from other reasoning models was involved. This means its reasoning chain is genuinely self-developed, not borrowed. Magistral Medium scores 73.6% on AIME-2024 pass@1 — a 50% relative improvement over the base Mistral Medium 3 — and reaches 90% with majority voting at 64 samples. Magistral supports multilingual chain-of-thought reasoning across English, French, Spanish, German, Italian, Arabic, Russian, and Simplified Chinese, making it the first openly verifiable multilingual reasoning model from a European AI lab.

### How Does Magistral's RLVR Training Work?

RLVR (Reinforcement Learning with Verifiable Rewards) trains a model to reason through problems step-by-step by rewarding correct final answers rather than imitating a teacher model's thought process. For Magistral, Mistral combined supervised fine-tuning (SFT) with RL in sequence: SFT established a baseline reasoning style, and RL optimized for verifiable correctness. This combined SFT + RL approach delivered more than 5 percentage points of improvement over either technique used alone across multiple benchmarks. The result is a model whose reasoning traces are fully transparent and auditable — each chain-of-thought step is visible, which matters enormously in regulated industries like law, finance, and healthcare where "the model said so" is not a sufficient justification.

## Magistral Small vs Magistral Medium — Which Should You Choose?

Magistral Small and Magistral Medium serve fundamentally different deployment contexts, and choosing between them depends on your privacy requirements, hardware access, and budget. Magistral Small is a 24B open-weight model that you can download from HuggingFace and run on-premises. When quantized to 4-bit, it fits on a single NVIDIA RTX 4090 or a MacBook Pro with 32 GB unified memory. It scores 70.7% on AIME-2024 pass@1 and 83.3% with majority voting — strong enough for most professional reasoning tasks in mathematics, software engineering, and structured analysis. Magistral Medium is the larger commercial variant, available only via API at $2.00 per million input tokens. It scores 73.6% pass@1 and 90% majority vote at 64 samples, and is positioned for enterprise workloads that need maximum accuracy without hardware constraints. If you process sensitive data that cannot leave your infrastructure, Magistral Small is the only viable option. If you need the best accuracy and can use an external API, Magistral Medium delivers measurably better results.

| Feature | Magistral Small | Magistral Medium |
|---|---|---|
| Parameters | 24B | Undisclosed (MoE) |
| License | Apache 2.0 (open-weight) | Proprietary API |
| AIME-24 pass@1 | 70.7% | 73.6% |
| AIME-24 majority @64 | 83.3% | 90% |
| Local deployment | Yes (RTX 4090, 32 GB Mac) | No |
| Pricing | Free (self-hosted) | $2.00 / M input tokens |
| Multilingual | Yes | Yes |
| Context window | 128k | 128k |

### Does Context Window Size Matter in Practice?

Magistral supports a 128k context window in both variants, but Mistral's own technical report notes that performance degrades noticeably past 40k tokens. For most use cases — a lengthy legal brief, a financial report, a codebase segment — 40k tokens is sufficient. For very long research papers or large codebases requiring full-file context, plan on chunking inputs or using retrieval-augmented generation (RAG) rather than relying on the extended context window. This 40k practical limit puts Magistral on par with most production reasoning models, none of which reliably maintain quality across 128k without careful prompt engineering.

## Benchmark Results: How Magistral Performs on AIME, LiveCodeBench, and More

Magistral's benchmark results position it firmly in the top tier of open-weight reasoning models released through mid-2026. On AIME-2024 — the American Invitational Mathematics Examination, a standard benchmark for advanced mathematical reasoning — Magistral Medium scores 73.6% pass@1, improving to 90% with majority voting across 64 samples. Magistral Small scores 70.7% pass@1 and 83.3% majority. On LiveCodeBench v5, a benchmark for real-world programming tasks drawn from competitive coding platforms, Magistral Medium scores 59.4%. This is competitive but not class-leading — DeepSeek R1 outperforms on HumanEval (73.2% pass@1) and SWE-Verified (49.2%), indicating that Magistral is stronger at mathematical reasoning than at complex software engineering tasks. The multilingual performance gap is documented at 4.3–9.9% below English performance, which Mistral attributes to constrained reasoning language — the model tends to reason in English internally even when prompted in other languages, introducing a translation overhead.

| Benchmark | Magistral Small | Magistral Medium | DeepSeek R1 |
|---|---|---|---|
| AIME-24 pass@1 | 70.7% | 73.6% | ~72% (comparable) |
| AIME-24 majority @64 | 83.3% | 90% | 90% (R1-Zero) |
| LiveCodeBench v5 | — | 59.4% | — |
| HumanEval pass@1 | — | — | 73.2% |
| SWE-Verified | — | — | 49.2% |

## Magistral vs DeepSeek R1 — Head-to-Head Comparison

Magistral and DeepSeek R1 are the two most credible open reasoning models as of mid-2026, but they make very different engineering trade-offs. DeepSeek R1 uses 671 billion parameters in a dense architecture, requiring multi-node GPU clusters to run. Magistral Medium is MoE-based (exact parameter count undisclosed) and runs on Mistral's managed API, while Magistral Small runs on a single consumer GPU. On AIME-2024 majority voting at 64 samples, both models reach approximately 90% — meaning Magistral achieves comparable mathematical reasoning with dramatically fewer active parameters per forward pass, a significant efficiency advantage. Where DeepSeek R1 wins clearly is software engineering: its 73.2% HumanEval and 49.2% SWE-Verified scores reflect a heavier focus on code generation during training. Magistral's 59.4% LiveCodeBench v5 score places it behind R1 on coding but ahead of most other open-weight alternatives. The other decisive difference is regulatory posture: Magistral is built by a French company under EU jurisdiction, which means GDPR compliance is native and there are no data-routing concerns to non-EU territories. For organizations in regulated European industries, that alone may be the deciding factor.

| Criterion | Magistral Small | Magistral Medium | DeepSeek R1 |
|---|---|---|---|
| Parameters | 24B | MoE (undisclosed) | 671B dense |
| AIME-24 (majority) | 83.3% | 90% | 90% (R1-Zero) |
| Coding (HumanEval) | — | ~59% (LCB) | 73.2% |
| Local deployment | Yes | No | No (too large) |
| Jurisdiction | EU (France) | EU (France) | China |
| License | Apache 2.0 | Proprietary | MIT |
| Base architecture | Dense 24B | MoE | Dense 671B |

## How to Run Magistral Small Locally (Ollama / HuggingFace)

Magistral Small is the most accessible locally-deployable reasoning model available today, requiring only a consumer-grade GPU or a high-RAM Apple Silicon Mac. The model is available at `mistralai/Magistral-Small-2506` on HuggingFace and can be run without any API key or usage fees once downloaded. With Ollama, setup takes under five minutes on a supported machine. At 4-bit quantization, the model requires approximately 14 GB of VRAM — fitting on an RTX 4090 (24 GB) with headroom or on a MacBook Pro with 32 GB unified memory. Generation speed runs at approximately 38 tokens per second on an RTX 4090, which is slower than lightweight 7B models but fast for a 24B reasoning model. The full-precision version requires 48 GB+ and would need an A100 or equivalent workstation GPU. For most developers and researchers, 4-bit quantization offers near-identical reasoning quality with a much lower hardware barrier.

### Running Magistral Small with Ollama

```bash
# Install Ollama (if not already installed)
curl -fsSL https://ollama.ai/install.sh | sh

# Pull Magistral Small (quantized 4-bit)
ollama pull magistral-small

# Run interactively
ollama run magistral-small

# Or run via API
ollama run magistral-small "Solve: find all integer solutions to x^2 + y^2 = z^2 where x, y < 20"
```

### Running via HuggingFace Transformers

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

model_id = "mistralai/Magistral-Small-2506"
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    torch_dtype=torch.bfloat16,
    device_map="auto",
    load_in_4bit=True  # requires bitsandbytes
)

messages = [{"role": "user", "content": "Prove that sqrt(2) is irrational."}]
inputs = tokenizer.apply_chat_template(messages, return_tensors="pt").to(model.device)
outputs = model.generate(inputs, max_new_tokens=2048, temperature=0.6)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
```

### Optimal Inference Settings

For best results with Magistral Small, use temperature 0.6–0.7 and top-p 0.9. Lower temperatures produce more deterministic but occasionally less creative reasoning chains. For majority voting tasks (where you sample 8–32 responses and pick the most common answer), temperature 0.8 improves diversity and overall accuracy. Avoid greedy decoding (temperature 0) for complex problems — Magistral's RLVR training was optimized for stochastic sampling.

## Magistral Pricing: API Cost vs OpenAI o3 and Claude

Magistral Medium's API pricing makes it one of the most cost-effective reasoning models available via managed endpoint. At $2.00 per million input tokens, it undercuts OpenAI o3 (approximately $10–15/M input tokens depending on tier) and sits below Claude Sonnet's $3.00/M input rate. For organizations running high-volume reasoning workloads — contract analysis, financial modeling, automated code review — this cost difference compounds rapidly. A workload consuming 100 million input tokens per month costs $200 with Magistral Medium versus $1,000–1,500 with comparable OpenAI o3 usage. The 37% output cost advantage over o3 (per published comparisons on aicostcheck.com) adds further savings on generation-heavy tasks. Magistral Small, run locally, eliminates API costs entirely at the expense of hardware investment and maintenance overhead. For teams with existing GPU infrastructure, the total cost of ownership strongly favors local deployment after roughly 3–6 months of sustained use.

| Model | Input (per 1M tokens) | Notes |
|---|---|---|
| Magistral Medium | $2.00 | Best reasoning value |
| Claude Sonnet | $3.00 | Strong all-around |
| GPT-4o | $5.00 | Broad capability |
| OpenAI o3 | $10–15 | Flagship reasoning |
| Magistral Small | $0 (self-hosted) | Hardware cost only |

## Enterprise Use Cases: Law, Finance, Healthcare, and Software Engineering

Magistral's transparent, step-by-step reasoning chain makes it particularly well-suited for regulated industries where decisions must be auditable and explainable. In legal practice, Magistral can analyze contract clauses, identify conflicting provisions, and flag non-standard terms — with each conclusion traceable through a visible reasoning path that can be reviewed by human counsel. In finance, it handles quantitative analysis, regulatory compliance checks, and structured data interpretation with the same auditability. Healthcare applications include differential diagnosis support and clinical trial protocol analysis, where the ability to inspect the model's reasoning is a regulatory prerequisite in many jurisdictions. For software engineering teams, Magistral's 59.4% LiveCodeBench v5 score makes it a solid choice for code review, bug localization, and algorithmic problem-solving — not the strongest coding model, but competitive when paired with its reasoning transparency. Enterprise teams generally access Magistral Medium via API for maximum accuracy, while research and security-conscious teams deploy Magistral Small locally to keep data on-premises. The EU jurisdiction adds another practical advantage: organizations subject to GDPR or the EU AI Act can use Magistral without the legal overhead of cross-border data transfer agreements.

### Is Magistral Suitable for Healthcare Applications?

Magistral's auditability makes it one of the few AI reasoning models appropriate for clinical decision support in jurisdictions with strict AI transparency requirements. The model's visible chain-of-thought output allows clinical informatics teams to review exactly how a conclusion was reached — a requirement under both EU AI Act Article 13 (transparency obligations) and emerging FDA software-as-a-medical-device guidance. That said, Magistral is not a certified medical device and should not be deployed as a standalone diagnostic tool. Its role is as a reasoning assistant that surfaces information and flags considerations, with final clinical judgment remaining with licensed practitioners.

## Limitations and Known Issues

Magistral has several documented limitations that prospective users should understand before deployment. The most significant is its tendency to enter infinite thinking loops on edge cases — problems that are ambiguous, paradoxical, or fall outside its training distribution can cause the model to generate extended chains of reasoning without reaching a conclusion, consuming tokens and time without producing useful output. This behavior is documented by multiple independent evaluators and is a known limitation of RLVR-trained reasoning models generally. Second, Magistral's multilingual reasoning performance is 4.3–9.9% lower than English across the languages it supports. Mistral attributes this to the model reasoning internally in English even when prompted in other languages, adding an implicit translation step. Third, the 128k context window degrades meaningfully past 40k tokens — the model's attention mechanism loses coherence on very long documents, making long-context tasks unreliable without chunking. Finally, at approximately 38 tokens per second on an RTX 4090, Magistral Small is slower than lightweight 7B or 13B models. For latency-sensitive applications, this matters. Magistral's Flash Answers mode in Le Chat offers up to 10× faster throughput for conversational use, but this mode is only available via the Le Chat product interface, not the raw API.

### Known Issue: Infinite Thinking Loops

When Magistral encounters an ambiguous or under-specified problem, it may continue generating reasoning steps indefinitely rather than returning a best-effort answer. Mitigation strategies include: (1) setting a `max_tokens` budget for the thinking chain explicitly, (2) adding a system prompt instruction like "If the problem is ambiguous, state your assumptions and proceed," and (3) using temperature 0.6 rather than higher values, which reduces exploratory branching in the reasoning chain.

## Magistral in 2026 — What Changed with Mistral Small 4?

The Magistral family has evolved significantly since its initial 2025 launch, with developments in 2026 that change how the technology should be evaluated. Magistral Small 1.2 and Medium 1.2 were released in September 2025, delivering incremental benchmark improvements without architectural changes. The more significant development came in March 2026 when Mistral released Mistral Small 4, a unified model that merges Magistral's reasoning capability with Pixtral's multimodal vision processing and Devstral's software engineering specialization into a single model. This consolidation means the standalone Magistral product line is effectively a foundation layer rather than a long-term product destination. For planning purposes: teams building on Magistral Small 24B can expect the capability to eventually migrate into Mistral Small 4 and successor unified models. Devstral 2, released alongside these updates, positions as a dedicated coding specialist built on Magistral's reasoning backbone — offering stronger software engineering performance (closer to DeepSeek R1's coding benchmarks) at the expense of general reasoning breadth. For organizations starting new reasoning projects in 2026, evaluating Mistral Small 4 alongside standalone Magistral is advisable.

---

## FAQ

The following questions cover the most common points of confusion about Magistral Mistral, based on developer forums, HuggingFace discussions, and enterprise procurement inquiries tracked through early 2026. Magistral is frequently mischaracterized as a distilled model or a fine-tune of a larger proprietary system — it is neither. It is an independently RLVR-trained reasoning model built directly on Mistral Medium 3. Its open-weight Small variant (24B, Apache 2.0) is unique among high-performing reasoning models in that it can be run locally, fine-tuned, and deployed in air-gapped environments. The Medium variant offers the highest accuracy at $2.00/M input tokens — the lowest price among reasoning-tier API models as of mid-2026. These answers reflect the model as of the 2506 release; Mistral Small 4 (March 2026) incorporates Magistral's reasoning and should be evaluated separately for new projects starting after that date.

### What is Magistral and who makes it?

Magistral is Mistral AI's first reasoning model family. Mistral AI is a French AI company founded in 2023. Magistral comes in two variants: Magistral Small (24B, open-weight, Apache 2.0) and Magistral Medium (proprietary API). Both use RLVR training on top of the Mistral Medium 3 base, with no distillation from other reasoning models. Magistral Medium scores 73.6% on AIME-2024 pass@1.

### Does Magistral beat DeepSeek R1?

On mathematical reasoning benchmarks (AIME-2024), Magistral Medium and DeepSeek R1 Zero both reach 90% with majority voting — making them essentially equivalent on math. Magistral wins on efficiency: it achieves these results with far fewer parameters. DeepSeek R1 wins on coding (73.2% HumanEval vs Magistral's ~59.4% LiveCodeBench). The choice depends on your primary workload.

### Can I run Magistral Small locally?

Yes. Magistral Small (24B) can be run locally using Ollama (`ollama pull magistral-small`) or the HuggingFace Transformers library. At 4-bit quantization, it requires approximately 14 GB VRAM — fitting on a single RTX 4090 or a MacBook Pro with 32 GB unified memory. Generation speed is approximately 38 tokens per second on an RTX 4090. The model is free to download and use under Apache 2.0.

### What is Magistral Medium's API pricing?

Magistral Medium is priced at $2.00 per million input tokens via the Mistral API — approximately 37% cheaper on output than OpenAI o3 and below Claude Sonnet's $3.00/M input rate. For high-volume enterprise workloads, this translates to significant cost savings. The API is available at api.mistral.ai and requires a Mistral account.

### What happened to Magistral in 2026?

Magistral Small 1.2 and Medium 1.2 shipped in September 2025 with incremental improvements. In March 2026, Mistral released Mistral Small 4, which merges Magistral's reasoning, Pixtral's vision capabilities, and Devstral's coding specialization into a single unified model. Devstral 2 was also released as a dedicated coding model built on Magistral's reasoning backbone. The standalone Magistral product line remains available but is increasingly a foundation for these unified successor models.
