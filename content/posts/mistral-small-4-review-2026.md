---
title: "Mistral Small 4 Review 2026: EU-Compliant, Open-Weight, $0.40/M Input"
date: 2026-05-08T00:00:00+00:00
tags: ["mistral","open-weight","eu-compliance","llm","review"]
description: "Mistral Small 4 is a 119B MoE model unifying reasoning, vision, and coding in a single open-weight release with full GDPR compliance and Apache 2.0 licensing."
draft: false
cover:
  image: "/images/mistral-small-4-review-2026.png"
  alt: "Mistral Small 4 Review 2026"
  relative: false
schema: "schema-mistral-small-4-review-2026"
---

Mistral Small 4 ships as an Apache 2.0 open-weight model with 119B total parameters and only 6.5B active per token through a 128-expert Mixture-of-Experts architecture. It handles reasoning, vision, and coding through a single endpoint, replaces three separate Mistral models, and is priced at $0.40/M input tokens through the Mistral API.

## Mistral Small 4 Review 2026: The EU-Compliant Open-Weight Model

Mistral Small 4 scores 28 on the AA Intelligence Index and outperforms GPT-OSS 120B on LiveCodeBench while generating outputs that are 20% shorter — a combination that matters directly for production cost. Released by Mistral AI, a Paris-based company, the model inherits EU data residency by default: API traffic stays inside the European Union without any additional configuration, which makes it the first credible option for GDPR-sensitive workloads that do not want to negotiate Standard Contractual Clauses with US cloud providers. Beyond compliance, the Apache 2.0 license removes all royalty and usage restrictions, meaning the same weights can be fine-tuned, redistributed, and embedded in commercial products without legal overhead. The model replaces Magistral for reasoning tasks, Pixtral for vision tasks, and Devstral for code tasks. It achieves 40% lower end-to-end latency and 3x higher throughput compared to Mistral Small 3, which makes it viable not just as a quality upgrade but as a direct cost reduction for teams already running Mistral in production. The model ID on the Mistral API is `mistral-small-2603` and weights are available on Hugging Face at 242 GB in BF16.

## Architecture: How 119B Parameters with 6.5B Active Works

The 119B total parameter count is the ceiling, not the runtime cost — each forward pass through Mistral Small 4 activates only 6.5B parameters because the model uses a Mixture-of-Experts (MoE) design with 128 specialist sub-networks, four of which handle any given token. This architecture is the same family as Mixtral 8x7B and Mixtral 8x22B, but scaled and retrained to cover multimodal inputs alongside text generation. The practical consequence is that inference compute scales with active parameters (6.5B), not total parameters (119B), which is why the model can deliver throughput 3x higher than Mistral Small 3 without requiring proportionally larger GPU clusters. The router — the component that selects which four experts handle each token — is trained end-to-end alongside the expert weights, so routing decisions are task-aware rather than fixed. Grouped-Query Attention (GQA) is applied across the architecture to reduce KV-cache memory pressure during long-context generation, which is critical for the 256K-token context window. The 256K window exceeds Claude Haiku 4.5 at 200K and GPT-4o Mini at 128K. The BF16 weight file totals 242 GB, which sets the floor for self-hosting memory requirements regardless of which GPU configuration is chosen. The `reasoning_effort` parameter — set to `low`, `medium`, or `high` — controls how many reasoning steps the model expands before producing output, giving engineers a direct handle on the cost-quality tradeoff within a single endpoint.

## Reasoning, Vision, and Coding: Three Jobs in One Model

Before Mistral Small 4, Mistral's product line split reasoning-heavy tasks to Magistral, image understanding to Pixtral, and code generation to Devstral — three separate model endpoints with separate pricing, separate version management, and separate integration overhead. Mistral Small 4 collapses all three into a single set of weights and a single API call, which simplifies architecture significantly for teams running mixed workloads. On coding specifically, the model reaches 92% on HumanEval while producing outputs 20% shorter than GPT-OSS 120B on LiveCodeBench, which is relevant because output token cost compounds at scale. Native image input supports document analysis, chart reading, and visual QA without routing to a secondary endpoint. The vision capability is not a bolt-on adapter — it is trained into the base model, which means image and text reasoning can interleave within a single context window. Reasoning depth is controlled through the `reasoning_effort` parameter: `low` for fast classification and routing tasks, `medium` for general generation, and `high` for multi-step debugging or proof-level reasoning. This parameter is set per API call, not at deployment time, so a single production deployment can serve all three workload profiles without spawning separate model instances. For teams that previously maintained separate fine-tunes or endpoints for code, vision, and reasoning tasks, consolidation onto Mistral Small 4 also reduces fine-tuning and evaluation surface area.

## Benchmark Performance: LiveCodeBench, Intelligence Index, and Real Tasks

Mistral Small 4 records an AA Intelligence Index composite score of 28, which positions it as the strongest open-weight small model across the tasks measured in that benchmark suite as of May 2026. On LiveCodeBench — a coding benchmark that evaluates models on problems posted after common training cutoffs, reducing data contamination risk — Mistral Small 4 outperforms GPT-OSS 120B despite having fewer active parameters, and does so with outputs that are 20% shorter on average. Shorter correct outputs matter because output tokens are priced higher than input tokens across all major providers; a model that answers concisely without sacrificing accuracy directly reduces billing. On HumanEval, the model scores 92%, matching Claude Haiku 3.5 and Qwen 2.5 72B on that benchmark. The AA Long-Context Reasoning (LCR) metric shows a more distinctive result: Mistral Small 4 achieves a score of 0.72 using approximately 1,600 output characters, while Qwen-series models reach comparable scores using 5,800 to 6,100 characters — a 3.5x to 4x verbosity gap that translates directly into output token cost differences. Throughput improvements over Mistral Small 3 are measured at 3x requests-per-second, and end-to-end latency is 40% lower, which matters for latency-sensitive applications like real-time code completion or interactive document analysis.

| Benchmark | Mistral Small 4 | Notes |
|---|---|---|
| AA Intelligence Index | 28 | Composite score |
| HumanEval | 92% | Matches Haiku 3.5, Qwen 2.5 72B |
| LiveCodeBench | Beats GPT-OSS 120B | 20% shorter outputs |
| AA LCR | 0.72 (1,600 chars) | Qwen comparable score needs 5,800+ chars |
| Latency vs Small 3 | -40% | End-to-end completion time |
| Throughput vs Small 3 | 3x | Requests per second |

## Pricing: $0.40/M Input vs GPT and Claude Alternatives

At $0.40/M input tokens through the Mistral API — with $0.60/M output — Mistral Small 4 undercuts Claude Haiku 4.5 at $1.00/M input by a meaningful margin, and competes directly with GPT-4o Mini on cost while adding open-weight portability and EU data residency that GPT-4o Mini cannot match. Some API configurations and partner tiers list the input price as $0.15/M; the $0.40/M figure reflects standard public API pricing with reasoning capability enabled. Output is priced at $0.60/M across configurations. For a team processing 100M tokens per month on input, the difference between Mistral Small 4 and Claude Haiku 4.5 is $60 to $100 per month — meaningful at startup scale and significant at enterprise scale where monthly token volumes run into the billions. Qwen 2.5 72B is available through several inference providers at similar or lower cost, but the LCR verbosity gap means effective output cost is higher per task completed. GPT-4o Mini matches Mistral Small 4 on input price at some tiers but carries a proprietary license, US data routing by default, and no self-hosting option. The Apache 2.0 license on Mistral Small 4 means the pricing comparison for self-hosted deployments reduces entirely to GPU infrastructure cost, with zero model licensing fee added.

| Model | Input $/M | Output $/M | License | EU Residency |
|---|---|---|---|---|
| Mistral Small 4 | $0.40 | $0.60 | Apache 2.0 | Default |
| Claude Haiku 4.5 | $1.00 | $5.00 | Proprietary | Requires config |
| GPT-4o Mini | $0.15–0.40 | $0.60 | Proprietary | Requires config |
| Qwen 2.5 72B | varies | varies | Tongyi (restricted) | No |

## EU Compliance and Self-Hosting: The GDPR Advantage

Mistral AI is headquartered in Paris, and API data processed through the Mistral platform stays within the European Union by default — no transatlantic data transfer, no need to negotiate Standard Contractual Clauses with a US hyperscaler, and no reliance on adequacy decisions that can be challenged in court. For European enterprises in finance, healthcare, and legal services, this removes a structural compliance barrier that exists when using OpenAI or Anthropic APIs configured for US-region processing. The EU AI Act, phasing in through 2026, adds another layer of regulatory consideration: models processed through EU-based infrastructure and offered by an EU-based provider are easier to document for AI Act compliance purposes than models routed through third-country jurisdictions. The GDPR advantage is not theoretical — several German fintech and Dutch healthtech companies have adopted Mistral as their primary LLM provider specifically because EU data residency is the default, not an optional add-on requiring a separate enterprise agreement. For teams that need complete data isolation — including from the API provider itself — the Apache 2.0 license enables full on-premises deployment with no external data egress. The combination of EU-headquartered provider, EU-default API routing, and fully self-hostable open weights is unique among competitive-tier models as of May 2026.

## Self-Hosting Requirements and Apache 2.0 Licensing

Self-hosting Mistral Small 4 requires hardware that most teams do not have on-hand: at minimum, 4x NVIDIA HGX H100, or 2x HGX H200, or 1x DGX B200. The BF16 weights total 242 GB, setting the GPU VRAM floor before runtime overhead is added. Cloud rental of a 4x H100 SXM configuration runs approximately $25–32 per hour in 2026, or roughly $18,000–$23,000 per month for continuous operation. Purchasing equivalent hardware outright costs $200K–$300K for the GPU cluster alone, before networking, storage, and operational overhead. The Apache 2.0 license itself imposes no cost — commercial use, fine-tuning, redistribution, and embedding in proprietary products are all permitted without royalties or usage reporting. The license is also patent-permissive, which removes the patent retaliation clauses that complicate some open-source AI deployments in corporate legal contexts. The economic case for self-hosting becomes viable when monthly token volume exceeds roughly 10 billion tokens (at which point cloud API cost approaches or exceeds hardware rental cost) or when regulatory requirements mandate air-gapped infrastructure that cannot make outbound API calls at all. For most teams processing fewer than 10 billion tokens per month, the Mistral API at $0.40/M input is the lower-cost option after accounting for GPU rental, DevOps, and reliability engineering. EU-based cloud providers like OVHcloud, Deutsche Telekom Open Telekom Cloud, and Scaleway support the hardware configurations required for self-hosted deployment while maintaining EU data sovereignty end-to-end.

## Who Should Use Mistral Small 4?

Mistral Small 4 earns a rating of 8.4 out of 10 as the strongest open-weight small model for combined reasoning, vision, and coding tasks in 2026, but the right fit depends on specific requirements rather than benchmark scores alone. Teams that benefit most are those with GDPR or EU AI Act obligations that make US-routed API calls legally risky — for these teams, Mistral Small 4 removes compliance friction that no amount of benchmark performance from OpenAI or Anthropic can resolve. Open-source projects and startups that need to embed an LLM into a commercial product without licensing encumbrance get that from Apache 2.0 with no workarounds required. Teams running mixed workloads — code generation, document analysis, and image understanding in the same product — benefit from consolidating onto a single model endpoint rather than maintaining separate integrations for each capability. Cost-sensitive API consumers processing hundreds of millions of tokens per month will see meaningful savings compared to Claude Haiku 4.5, and comparable or lower cost versus GPT-4o Mini with the added benefit of self-hosting optionality. Teams that should look elsewhere: those needing maximum reasoning depth on complex multi-step mathematical or logical problems, where frontier closed models like Claude Opus 4 or GPT-5 series still hold a clear lead; teams already deeply integrated into the OpenAI or Anthropic ecosystem where switching costs outweigh the pricing and licensing advantages; and teams requiring the most mature third-party tooling ecosystem for monitoring, fine-tuning pipelines, and observability, where OpenAI's ecosystem remains more developed. For everyone else, Mistral Small 4 is the default recommendation for open-weight production deployments in 2026.

---

## FAQ

**What are the hardware requirements to self-host Mistral Small 4?**

Self-hosting requires a minimum of 4x NVIDIA HGX H100, 2x HGX H200, or 1x DGX B200. The model weights in BF16 format total 242 GB, which sets the baseline GPU VRAM requirement before runtime overhead. Most teams without existing high-end GPU infrastructure will find the Mistral API more cost-effective unless they are processing more than 10 billion tokens per month or have regulatory requirements for fully air-gapped deployments.

**How does the reasoning_effort parameter affect billing?**

The `reasoning_effort` parameter (`low`, `medium`, `high`) controls how many internal reasoning steps the model expands before producing output. Higher effort levels generate more output tokens during the reasoning phase, which increases output token billing. For classification, routing, and simple generation tasks, `low` or `medium` keeps costs down. Reserve `high` for complex debugging, multi-step code generation, or tasks where answer quality justifies the additional output token cost.

**Does Mistral Small 4 handle images natively, or is it an add-on?**

Native image input is built into the base model — it is not a separate adapter or a secondary endpoint call. Document analysis, chart reading, and visual question answering are handled within the same context window as text. This replaces the previous Pixtral model for most image understanding tasks and eliminates the need to maintain a separate vision endpoint in production.

**Is Mistral Small 4 genuinely GDPR-compliant for processing personal data?**

Mistral AI is a French company and API traffic is processed within EU infrastructure by default, satisfying the geographic data residency requirement for most GDPR use cases. However, GDPR compliance also requires a signed Data Processing Agreement (DPA) with Mistral AI as your data processor — using EU-located infrastructure alone is not sufficient without a DPA in place. For workloads requiring complete data isolation from any third party, self-hosting under the Apache 2.0 license on EU-region infrastructure is the appropriate path.

**How does Mistral Small 4 compare to Qwen 2.5 72B on real-world cost?**

Benchmark scores between the two models are comparable on HumanEval, but Mistral Small 4's output verbosity advantage on the AA LCR metric is significant: Mistral achieves similar reasoning scores using roughly 1,600 output characters where Qwen requires 5,800 to 6,100 characters for equivalent results. Since output tokens are billed per token, Qwen's verbosity translates to 3.5x to 4x higher effective output cost per task for long-context reasoning workloads. For short-context tasks where both models are equally concise, the cost difference narrows, and Qwen may have pricing advantages through specific inference providers.
