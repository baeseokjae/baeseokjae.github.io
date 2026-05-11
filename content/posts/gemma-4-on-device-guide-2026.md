---
title: "Gemma 4 On-Device Deployment Guide: Run Google's Open Model Locally"
date: 2026-05-11T00:05:05+00:00
tags: ["Gemma 4", "local LLM", "on-device AI", "Ollama", "open source"]
description: "Run Gemma 4 locally with Ollama, LM Studio, or llama.cpp. Hardware requirements, quantization guide, mobile deployment, and fine-tuning with QLoRA."
draft: false
cover:
  image: "/images/gemma-4-on-device-guide-2026.png"
  alt: "Gemma 4 On-Device Deployment Guide"
  relative: false
schema: "schema-gemma-4-on-device-guide-2026"
---

Gemma 4 is Google's family of open-weights models released April 2, 2026 under Apache 2.0 — four sizes from a 2B mobile-ready model to a 31B dense powerhouse, all runnable locally without sending a single byte to Google's servers. This guide covers every deployment path: Ollama, LM Studio, Hugging Face Transformers, llama.cpp, Android, and iOS.

## What Is Gemma 4 and Why Run It On-Device?

Gemma 4 is Google DeepMind's fourth-generation open-weights language model family, released on April 2, 2026 under the Apache 2.0 license with no commercial restrictions. The family spans four sizes — E2B (~2.3B effective parameters), E4B (~4.5B), 26B MoE (only 3.8B active per token), and 31B Dense — each capable of running entirely on consumer hardware. At the top end, the 31B model scores 85.2% on MMLU Pro and 81.8% on HumanEval; the 26B MoE model sits at Arena AI ELO rank #3 globally at 1452 — all while being something you can run on a gaming laptop. Running Gemma 4 on-device eliminates API costs entirely, replacing per-token billing with a one-time GPU investment. More importantly, inference stays local: code, documents, customer data, and proprietary context never leave your machine. For enterprises bound by HIPAA, SOC 2, or internal data governance rules, that's not optional — it's the whole point. Apache 2.0 also means you can fine-tune on proprietary data and redistribute the result commercially, without any restrictions that come with Meta's Llama license or Mistral's community terms.

## Gemma 4 Model Variants: Choosing the Right Size for Your Hardware

Gemma 4 ships four distinct variants optimized for different hardware tiers, and picking the wrong one is the most common deployment mistake. The E2B and E4B are "edge" variants with 128K context windows, designed for mobile and low-power hardware. The 26B uses a Mixture-of-Experts architecture that activates only 3.8B parameters per inference pass — delivering roughly 97% of the 31B's quality at 8× less compute. The 31B Dense is the full-power option for workstations and servers.

| Variant | Effective Params | Active Params | Context | Best For |
|---------|-----------------|---------------|---------|----------|
| E2B | ~2.3B | 2.3B (Dense) | 128K | Mobile, Raspberry Pi, 4GB RAM |
| E4B | ~4.5B | 4.5B (Dense) | 128K | Mid-range phones, 8GB laptops |
| 26B MoE | 26B | 3.8B/token | 256K | Consumer GPUs, 16GB VRAM |
| 31B Dense | 31B | 31B | 256K | Workstation GPUs, Mac Ultra |

The MoE sweet spot: if you have an RTX 4090 (24GB VRAM), the 26B MoE at INT4 runs at 85 tokens/second on an AMD Ryzen AI MAX+ with 128GB unified memory — fast enough for real-time chat with 256K context. The 31B Dense needs ~18GB VRAM at INT4; the 26B MoE needs ~16GB. That 2GB difference decides whether you fit on a single 4090 or need two GPUs.

## Hardware Requirements by Model and Quantization Level

Hardware requirements for Gemma 4 vary significantly by quantization level, and choosing the right format is the difference between smooth inference and an out-of-memory crash. At INT4 quantization (Q4_K_M), the E2B needs only ~1.5GB VRAM, the E4B ~3GB, the 26B MoE ~16GB, and the 31B Dense ~18GB. INT8 roughly doubles these numbers; FP16 doubles again. For CPU-only inference, add 50–70% headroom for KV cache at typical sequence lengths. Google's Android Studio now supports Gemma 4 as the local model for agentic coding (announced April 2026), validated for the E2B and E4B on devices with 6GB+ RAM.

| Model | INT4 (Q4_K_M) | INT8 | FP16 | CPU RAM (INT4) |
|-------|---------------|------|------|----------------|
| E2B | 1.5 GB VRAM | 3 GB | 6 GB | 4 GB |
| E4B | 3 GB VRAM | 6 GB | 12 GB | 8 GB |
| 26B MoE | 16 GB VRAM | 32 GB | 64 GB | 32 GB |
| 31B Dense | 18 GB VRAM | 36 GB | 72 GB | 48 GB |

For Mac users with Apple Silicon, VRAM and RAM are unified — an M3 Max with 48GB handles the 26B MoE at FP16 comfortably. For Windows/Linux with discrete GPUs: VRAM is the hard ceiling. Nothing exceeding VRAM capacity will load without splitting across GPUs or falling back to CPU offloading (which drops throughput by 5–10×).

### Quick Hardware Tier Guide

Match your hardware to the right Gemma 4 variant before installing anything:

- **4–6 GB RAM, no GPU** (phones, Pi 5): E2B Q4_K_M
- **8 GB RAM / 8 GB VRAM** (RTX 3070, M2): E4B Q4_K_M
- **16–24 GB VRAM** (RTX 4090, A10G): 26B MoE Q4_K_M
- **24+ GB VRAM or 64+ GB unified** (A100, Mac Ultra): 31B Dense FP16

## Quick Start: Run Gemma 4 Locally with Ollama (5-Minute Setup)

Ollama is the fastest path to running Gemma 4 locally — a single CLI command installs the model, manages quantization, and starts a local inference server with an OpenAI-compatible API. No Python environment, no CUDA setup, no manual model download required. Ollama handles model storage, hardware detection, and memory management automatically, making it the go-to choice for developers who want to evaluate Gemma 4 without a multi-hour setup. The trade-off: less control over quantization format than llama.cpp, and no GUI. For most developers starting out, Ollama is the right first step.

**Install Ollama (macOS/Linux):**

```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**Windows:** Download the installer from [ollama.ai](https://ollama.ai) and run it.

**Run Gemma 4 E4B (recommended starting point):**

```bash
ollama run gemma4:4b
```

**Run the 27B MoE variant:**

```bash
ollama run gemma4:27b
```

Ollama auto-selects Q4_K_M quantization by default, which hits the best quality/VRAM balance. The first run downloads the model (E4B: ~2.5GB, 27B: ~16GB), then drops you into an interactive chat.

**Use Ollama's OpenAI-compatible API:**

```bash
curl http://localhost:11434/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemma4:4b",
    "messages": [{"role": "user", "content": "Explain MoE in 3 sentences"}]
  }'
```

This endpoint is drop-in compatible with any OpenAI SDK — switch your `base_url` to `http://localhost:11434/v1` and set any non-empty `api_key`.

## Run Gemma 4 with LM Studio (GUI Method — No Terminal Required)

LM Studio provides a desktop GUI for downloading, configuring, and running local models without any command-line experience. It wraps llama.cpp under the hood, supports drag-and-drop model management, and exposes an OpenAI-compatible local server — all through a point-and-click interface. For teams where not everyone is comfortable with terminals, or for non-technical stakeholders who need to evaluate model quality directly, LM Studio removes friction. The downside versus Ollama: LM Studio is heavier (Electron app) and the server mode requires manually clicking "Start Server" each session.

**Setup steps:**

1. Download LM Studio from the official site for your OS (Windows, macOS, or Linux).
2. Open LM Studio → click **Discover** → search `gemma-4`.
3. Select the variant matching your hardware (see the VRAM table above).
4. Click **Download** — LM Studio fetches the GGUF from Hugging Face automatically.
5. Switch to the **Chat** tab and start a conversation, or open **Local Server** tab to enable the API.

**Recommended settings in LM Studio for Gemma 4:**

- **Context length**: Set to 8192–32768 for most tasks; push to 128K only if needed (E2B/E4B) — larger contexts consume more RAM per inference.
- **GPU layers**: Slide to maximum for your VRAM; if you hit OOM, reduce by 5 layers at a time.
- **Temperature**: 0.7 for creative tasks, 0.1–0.3 for code and factual Q&A.

## Run Gemma 4 with Hugging Face Transformers (Python API)

Hugging Face Transformers gives you programmatic access to Gemma 4 with full control over inference parameters, batching, streaming, and custom pipelines — the right choice when you're building an application rather than chatting interactively. The 31B model can be fine-tuned with as little as 16GB VRAM using QLoRA via Unsloth, making Transformers the entry point for the entire Gemma 4 fine-tuning ecosystem. You'll need a Hugging Face account and a brief model-access request (auto-approved within minutes) for the gated Gemma 4 checkpoints.

**Install dependencies:**

```bash
pip install transformers accelerate bitsandbytes torch
huggingface-cli login  # enter your HF token
```

**Load and run Gemma 4 E4B in 4-bit:**

```python
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
import torch

model_id = "google/gemma-4-e4b-it"

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16,
)

tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    quantization_config=bnb_config,
    device_map="auto",
)

messages = [{"role": "user", "content": "What is Mixture of Experts?"}]
inputs = tokenizer.apply_chat_template(messages, return_tensors="pt").to("cuda")

with torch.no_grad():
    output = model.generate(inputs, max_new_tokens=512, do_sample=True, temperature=0.7)

print(tokenizer.decode(output[0][inputs.shape[1]:], skip_special_tokens=True))
```

**For the 26B MoE with multi-GPU:**

```python
model = AutoModelForCausalLM.from_pretrained(
    "google/gemma-4-26b-moe-it",
    device_map="auto",  # auto-splits across available GPUs
    torch_dtype=torch.bfloat16,
)
```

`device_map="auto"` handles GPU/CPU split automatically — if you're 2GB short of VRAM, it offloads the overflow to CPU RAM with minimal throughput penalty.

## Run Gemma 4 with llama.cpp (Maximum Control and Portability)

llama.cpp is the lowest-level local inference option — a pure C++ implementation that runs on any hardware (CPU, CUDA, Metal, ROCm, Vulkan) with no Python runtime required. It gives you per-layer GPU offloading, custom quantization formats, speculative decoding, and the smallest possible binary footprint. For embedded systems, Docker containers, or CI pipelines where Python is a liability, llama.cpp is the production-grade choice. The trade-off: you compile from source and work with GGUF files directly rather than HuggingFace model IDs.

**Build llama.cpp with CUDA support:**

```bash
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp
cmake -B build -DGGML_CUDA=ON
cmake --build build --config Release -j$(nproc)
```

**For Metal (Apple Silicon):**

```bash
cmake -B build -DGGML_METAL=ON
cmake --build build --config Release -j$(nproc)
```

**Download a Gemma 4 GGUF from Hugging Face:**

```bash
# E4B Q4_K_M — best balance of quality and speed
huggingface-cli download bartowski/gemma-4-e4b-it-GGUF \
  --include "gemma-4-e4b-it-Q4_K_M.gguf" \
  --local-dir ./models
```

**Run inference:**

```bash
./build/bin/llama-cli \
  -m ./models/gemma-4-e4b-it-Q4_K_M.gguf \
  -n 512 \
  --gpu-layers 999 \
  -p "Explain on-device AI in 3 sentences:"
```

`--gpu-layers 999` sends all layers to GPU; reduce to a specific number if you hit VRAM limits. Each layer is roughly 50–100MB depending on the model size — start at `--gpu-layers 20` and increase until you hit your ceiling.

**Start an OpenAI-compatible server:**

```bash
./build/bin/llama-server \
  -m ./models/gemma-4-e4b-it-Q4_K_M.gguf \
  --port 8080 \
  --gpu-layers 999
```

## Deploy Gemma 4 on Mobile: Android (LiteRT) and iOS (MLX Swift)

Gemma 4's E2B and E4B variants were designed explicitly for on-device mobile deployment — the E2B has a ~1.3GB disk footprint and uses only 2–3GB RAM at runtime (Q4_K_M), fitting comfortably on any Android or iOS phone released since 2022. Google's MediaPipe and LiteRT stack handles Android deployment with hardware-accelerated inference across CPU, GPU, and NPU; Apple's MLX framework and Core ML handle iOS with unified-memory efficiency on A17 Pro and M-series chips. The result is fully offline inference with no network calls, no API keys, and sub-second response latency on modern hardware. Android Studio officially added Gemma 4 as the local model for agentic coding in April 2026, signaling Google's commitment to the mobile deployment path. For privacy-sensitive mobile applications — medical reference tools, legal document assistants, offline translation — this combination of small model size and offline inference removes every regulatory barrier that cloud-dependent AI would introduce. The E4B at Q4_K_M runs at 25–40 tokens/second on a Pixel 9 Pro, which is faster than most users can read generated text.

### Android Deployment with MediaPipe and LiteRT

MediaPipe's LLM Inference API abstracts hardware acceleration across CPU, GPU (OpenGL), and NPU:

```kotlin
// build.gradle
implementation("com.google.mediapipe:tasks-genai:0.10.14")
```

```kotlin
val options = LlmInferenceOptions.builder()
    .setModelPath("/data/local/tmp/gemma4-e2b-q4.bin")
    .setMaxTokens(1024)
    .setPreferredBackend(LlmInferenceOptions.Backend.GPU)
    .build()

val llmInference = LlmInference.createFromOptions(context, options)

val result = llmInference.generateResponse("Summarize this document: $text")
```

Download the LiteRT-compatible `.bin` from Google's AI Edge model hub. The E2B at Q4 runs at ~25–40 tokens/second on a Pixel 9 Pro.

### iOS Deployment with MLX Swift

Apple Silicon iPhones (A17 Pro and later, M-series iPads) can run Gemma 4 E2B through MLX Swift:

```swift
import MLX
import MLXLLM

let modelConfig = ModelConfiguration(id: "mlx-community/gemma-4-e2b-4bit")
let model = try await LLMModel.load(configuration: modelConfig)

let result = try await model.generate(
    prompt: "Summarize: \(text)",
    maxTokens: 512
)
print(result)
```

MLX leverages unified memory — the same memory pool serves CPU and GPU — meaning an iPhone 15 Pro with 8GB can run E4B without swap. For A16 Bionic and older (6GB RAM), stick to E2B Q4.

## Quantization Guide: INT4 vs INT8 vs FP16 — What to Pick

Quantization compresses model weights from 32-bit or 16-bit floats into lower-precision integers, trading a small amount of accuracy for large reductions in VRAM usage and throughput gains. For Gemma 4, INT4 (specifically Q4_K_M in GGUF format, or NF4 in bitsandbytes) is the standard starting point for local deployment — it cuts VRAM roughly 4× versus FP16 with less than 1–2% accuracy degradation on most benchmarks. INT8 sits in the middle: useful when you have VRAM headroom and want marginally better quality than INT4 without the cost of FP16. FP16 is the baseline for fine-tuning and production API serving where accuracy is paramount and you have sufficient VRAM.

| Format | Quality Loss | VRAM vs FP16 | Throughput | Use Case |
|--------|-------------|---------------|------------|----------|
| FP16 | None | 1× | Baseline | Fine-tuning, API serving |
| INT8 (Q8_0) | ~0.5% | 0.5× | +20–30% | Midrange GPUs, quality-focused |
| INT4 (Q4_K_M) | ~1–2% | 0.25× | +50–80% | Consumer GPUs, recommended default |
| INT4 (Q2_K) | ~5–8% | 0.15× | +90–120% | CPU-only, extreme memory constraints |

**Recommendation by scenario:**

- **Development and evaluation**: Q4_K_M (Ollama default)
- **Production API serving with quality focus**: INT8 or FP16
- **Fine-tuning**: FP16 base weights + NF4 adapters (QLoRA)
- **Mobile/edge**: Q4_K_M for the best quality-to-size ratio
- **CPU-only on 8GB RAM**: Q4_K_M for E2B only; larger models won't fit

## Fine-Tuning Gemma 4 Locally with QLoRA (16GB VRAM)

Fine-tuning Gemma 4 on proprietary data is achievable on a single consumer GPU using QLoRA — the 31B model can be fine-tuned with as little as 16GB VRAM via Unsloth, which patches the training loop to eliminate redundant activations and cut memory usage by 60% versus standard Transformers fine-tuning. Apache 2.0 licensing means there are zero legal barriers to training on customer data and redistributing the result as a commercial product. The practical workflow: freeze base weights in 4-bit, attach low-rank adapter matrices (LoRA), train only the adapters, then merge or serve the adapter separately at inference time.

**Setup with Unsloth (fastest option):**

```bash
pip install "unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git"
pip install --no-deps trl peft accelerate bitsandbytes
```

**Training script:**

```python
from unsloth import FastLanguageModel
from trl import SFTTrainer
from transformers import TrainingArguments
from datasets import load_dataset

model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="google/gemma-4-31b-it",
    max_seq_length=4096,
    dtype=None,  # auto-detect
    load_in_4bit=True,
)

model = FastLanguageModel.get_peft_model(
    model,
    r=16,           # LoRA rank — higher = more capacity, more memory
    target_modules=["q_proj", "v_proj", "k_proj", "o_proj"],
    lora_alpha=16,
    lora_dropout=0,
    bias="none",
)

dataset = load_dataset("your_org/your_dataset", split="train")

trainer = SFTTrainer(
    model=model,
    train_dataset=dataset,
    dataset_text_field="text",
    max_seq_length=4096,
    args=TrainingArguments(
        per_device_train_batch_size=2,
        gradient_accumulation_steps=4,
        warmup_steps=10,
        num_train_epochs=3,
        learning_rate=2e-4,
        fp16=not torch.cuda.is_bf16_supported(),
        bf16=torch.cuda.is_bf16_supported(),
        output_dir="./gemma4-finetuned",
    ),
)
trainer.train()
```

With an RTX 4090 (24GB), you can fine-tune the 26B MoE at `r=16` with batch size 4. The 31B Dense at 16GB VRAM requires `r=8` and batch size 1–2 with gradient accumulation.

## Real-World Use Cases: When to Choose On-Device Over API

On-device deployment wins decisively in scenarios where data confidentiality, latency, or cost predictability cannot be compromised. Running Gemma 4 locally means your legal contracts, source code, patient records, and financial data stay on your hardware — no API call, no risk of training data incorporation, no compliance gap to explain to auditors. Cost-wise, a single RTX 4090 at $1,000–1,500 replaces roughly $500–800/month in API costs for moderate-usage applications, breaking even in 2–3 months. The calculus flips for low-volume use cases — if you're making 50 API calls a day, the hardware investment doesn't pay off for years.

**Choose on-device when:**

- Data contains PII, PHI, financial records, or trade secrets
- Latency requirements are under 200ms (local inference beats API RTT)
- Monthly API costs exceed $300–500
- You need 100% uptime independent of third-party service status
- You're deploying to air-gapped environments

**Choose API when:**

- Inference volume is unpredictable or low
- You need the absolute latest model capabilities without re-deployment
- Your team lacks GPU hardware or ML ops expertise
- You need multimodal capabilities Gemma 4 doesn't support yet

## Gemma 4 On-Device Benchmark Results and Speed Tests

Gemma 4 delivers competitive throughput on consumer hardware, with the MoE architecture providing the most compelling performance-per-watt ratio. On an AMD Ryzen AI MAX+ with 128GB unified memory, the 26B MoE hits 85 tokens/second — fast enough that users can't read the output as fast as it generates. On an RTX 4090, the same model at Q4_K_M runs at 60–75 tokens/second. The 31B Dense on dual A100s reaches 120+ tokens/second. For comparison, the E4B on a Pixel 9 Pro runs at 25–40 tokens/second — more than sufficient for mobile chat applications where rendering and UX limit perceived speed.

| Hardware | Model | Quantization | Tokens/sec |
|----------|-------|-------------|-----------|
| AMD Ryzen AI MAX+ 128GB | 26B MoE | Q4_K_M | 85 |
| NVIDIA RTX 4090 24GB | 26B MoE | Q4_K_M | 65–75 |
| NVIDIA RTX 3090 24GB | 26B MoE | Q4_K_M | 45–55 |
| Apple M3 Max 48GB | 31B Dense | FP16 | 35–45 |
| Apple M3 Pro 18GB | 26B MoE | Q4_K_M | 50–60 |
| Apple M2 8GB | E4B | Q4_K_M | 35–50 |
| Google Pixel 9 Pro | E2B | Q4 (LiteRT) | 25–40 |
| CPU only (Ryzen 9 7950X, 64GB DDR5) | E4B | Q4_K_M | 8–12 |

TTFT (time-to-first-token) on GPU hardware is typically 200–500ms for Q4 models at standard context lengths. CPU-only inference adds 1–3 seconds of TTFT latency — noticeable in interactive applications, acceptable for batch processing.

## Troubleshooting Common Errors (OOM, Slow Inference, Model Load Failures)

The most common Gemma 4 local deployment failures fall into three categories: out-of-memory (OOM) crashes during model load, slow inference caused by CPU fallback, and model load failures from mismatched file formats or missing dependencies. OOM is the most frequent — it almost always means the selected quantization level exceeds available VRAM, and the fix is to switch to a lower-bit format or use a smaller model variant. Slow inference (under 5 tokens/second on GPU hardware) usually means the model silently fell back to CPU due to driver issues or insufficient VRAM for the selected layer count. Load failures are typically missing `bitsandbytes` for Python paths or wrong GGUF format version for llama.cpp.

**OOM during load:**
```
CUDA error: out of memory
RuntimeError: CUDA out of memory. Tried to allocate X GiB
```
Fix: Switch from Q8_0 to Q4_K_M, or from FP16 to INT4. In llama.cpp, reduce `--gpu-layers` by 10 at a time.

**Slow inference (CPU fallback):**
```bash
# Check if GPU is actually being used in llama.cpp:
./llama-cli --verbose ... | grep "GPU"
# Should show: "llm_load_tensors: GPU = 1, offloaded layers = N"
```
If offloaded layers = 0, the model fell back to CPU. Fix: update GPU drivers, reinstall llama.cpp with `-DGGML_CUDA=ON`, or reduce `--gpu-layers` to what fits.

**Transformers model load failure:**
```
OSError: google/gemma-4-e4b-it is a gated model. Please log in.
```
Fix: `huggingface-cli login` — you need a HF account and must accept Gemma 4's terms (auto-approved in minutes).

**LM Studio "model failed to load":**
Check that you downloaded a GGUF file, not a `.safetensors` (which LM Studio doesn't support). In the model browser, filter by "GGUF" format explicitly.

**Ollama "model not found":**
```bash
ollama list  # check installed models
ollama pull gemma4:4b  # explicit pull if run failed
```

---

## FAQ

**Q: Can I run Gemma 4 26B on an RTX 3080 (10GB VRAM)?**
No — the 26B MoE at Q4_K_M requires ~16GB VRAM, which exceeds a 10GB card. Use E4B Q4_K_M (~3GB) or the 26B with aggressive CPU offloading at a significant throughput penalty. An RTX 3080 Ti (12GB) still falls short; a 4090 (24GB) is the minimum for comfortable 26B deployment.

**Q: Does Gemma 4 require a Hugging Face account for Ollama?**
No. Ollama hosts its own model library and downloads Gemma 4 directly without any HF account or token. A HF account is only required when using `AutoModelForCausalLM.from_pretrained()` with the `google/gemma-4-*` model IDs, due to the gated model terms.

**Q: What's the difference between the Gemma 4 base and instruct variants?**
The base model (`gemma-4-*-pt`) is a raw language model without instruction tuning — useful for fine-tuning and research. The instruct variant (`gemma-4-*-it`) is fine-tuned to follow chat instructions with a specific prompt format. For local deployment and chat applications, always use the `-it` variant. Ollama serves the instruct variant by default.

**Q: Can Gemma 4 run on Windows without WSL?**
Yes. Ollama has a native Windows installer. LM Studio has a native Windows app. llama.cpp builds natively on Windows with CMake + Visual Studio Build Tools. Only the Hugging Face Transformers path requires Python, which runs natively on Windows. There is no requirement for WSL2, though WSL2 can help if you hit driver compatibility issues.

**Q: Is Gemma 4 fine-tuned on a different computer usable on my local machine?**
Yes — the Apache 2.0 license allows you to fine-tune on any hardware, save the adapter weights (PEFT/LoRA format) or a merged GGUF, and run it anywhere. With Unsloth's export tools: `model.save_pretrained_gguf("gemma4-custom", tokenizer, quantization_method="q4_k_m")` outputs a portable GGUF you can load in llama.cpp or LM Studio on any machine.
