---
cover:
  alt: 'FLUX.1 Developer Guide: Best Open-Source Image Generation Model 2026'
  image: /images/flux-1-image-generation-developer-api-guide-2026.png
  relative: false
date: 2026-06-09 07:15:14+00:00
description: 'Complete FLUX.1 developer guide: model variants, Python API integration,
  LoRA fine-tuning, ComfyUI setup, and pricing benchmarks for 2026.'
draft: false
schema: schema-flux-1-image-generation-developer-api-guide-2026
tags:
- FLUX.1
- image generation
- AI
- Python
- open source
- developer guide
title: 'FLUX.1 Developer Guide: Best Open-Source Image Generation Model 2026'
---

FLUX.1 is a 12-billion parameter rectified flow transformer from Black Forest Labs that outperforms Stable Diffusion XL on photorealism, text rendering, and prompt adherence — available under Apache 2.0 for commercial use. This guide covers everything you need to integrate, fine-tune, and deploy FLUX.1 in production.

## What Is FLUX.1? Architecture and Why It Dominates Open-Source Image Generation

FLUX.1 is a 12-billion parameter rectified flow transformer developed by Black Forest Labs, released in August 2024 by the original Stable Diffusion researchers who founded the company after leaving Stability AI. Unlike earlier diffusion models that stack UNet decoders, FLUX.1 uses a transformer-based architecture with bidirectional attention across text and image tokens simultaneously, which enables dramatically better prompt adherence and coherent multi-subject compositions. The model achieves state-of-the-art scores on the ELO image quality leaderboard, beating Midjourney v6 and DALL-E 3 in independent benchmarks for photorealism, anatomical accuracy, and typographic rendering. Black Forest Labs released FLUX.1 [schnell] under Apache 2.0 license — the only fully commercial-grade tier — while [dev] uses a non-commercial research license. By October 2025, MLCommons added FLUX.1 as an official training benchmark in MLPerf, signaling its industrial adoption. The architecture's key innovation is its hybrid multimodal attention, which allows the model to model the correlation between image patches and text tokens jointly rather than conditioning image generation on a fixed text embedding. This translates to significantly better multi-subject scene generation and reliable text-in-image rendering that previous open-source models struggled with.

### Rectified Flow vs. DDPM: What Changes for Developers

Rectified flow transformers use a simpler, more direct path from noise to image compared to DDPM-based models like Stable Diffusion. The practical implication: FLUX.1 [schnell] generates high-quality images in just 1–4 sampling steps, versus 20–50 for SDXL, reducing per-image latency to under 1 second on an H800 GPU at 1024×1024 resolution. For developers building high-volume pipelines, this means Schnell's step count dramatically cuts inference costs when self-hosting — the GPU-minutes per image drops by 10–20× compared to SDXL with equivalent quality for standard use cases.

## FLUX.1 Model Variants Explained: Schnell vs Dev vs Pro (and When to Use Each)

FLUX.1 ships in three tiers that serve different use cases and budgets, and choosing the wrong one is the most common mistake developers make. FLUX.1 [schnell] is the fully Apache 2.0-licensed variant, generating images in 1–4 steps at approximately 75–80% the quality of [pro] — it is the right default for prototyping, storyboarding, A/B testing at volume, and any commercial product that needs cost-efficient throughput. FLUX.1 [dev] produces images at 90–95% the quality of [pro] and is licensed for non-commercial research and development; it uses guidance distillation from [pro] to achieve quality well beyond Schnell's range, making it the right choice for internal tools, demos, and user-facing features where the license permits. FLUX.1 [pro] is the Black Forest Labs-hosted commercial model, only accessible via BFL API at $0.03–$0.05/image, with no local self-hosting option; it delivers the reference quality level for production consumer products. In 2026, FLUX.2 [dev] (32B parameters, January 15, 2026 release) leads the Artificial Analysis open-weights leaderboard, but requires dual RTX 3090s locally — for most teams, FLUX.1 [dev] locally or FLUX.2 [dev] via API is the practical decision.

| Variant | License | Steps | Quality | Use Case |
|---|---|---|---|---|
| FLUX.1 [schnell] | Apache 2.0 | 1–4 | ~75–80% of Pro | Commercial, high-volume |
| FLUX.1 [dev] | Non-commercial | 20–50 | ~90–95% of Pro | R&D, demos, internal tools |
| FLUX.1 [pro] | API-only | Hosted | Reference (100%) | Production consumer apps |
| FLUX.2 [dev] | Non-commercial | 20–50 | Exceeds FLUX.1 Pro | Premium quality pipeline |

### FLUX.1 vs Stable Diffusion XL: When to Switch

FLUX.1 produces better anatomy, faces, hands, and coherent multi-character scenes than SDXL in head-to-head comparisons. Text rendering in images — product labels, UI mockups, game assets with readable text — is significantly more reliable on FLUX.1. The one area SDXL retains an advantage is its larger LoRA ecosystem; SDXL has three years of community fine-tunes versus roughly two years for FLUX.1. If you have existing SDXL fine-tunes that work well, migrating to FLUX.1 means retraining. For new projects starting in 2026, FLUX.1 is the better foundation.

## Getting Started Locally: Installing FLUX.1 with the Diffusers Library

Running FLUX.1 locally requires either the Hugging Face `diffusers` library or ComfyUI, and the hardware requirements are non-trivial. The full FLUX.1 [dev] model demands at least 24GB VRAM — an RTX 4090, RTX 5090, or professional GPU equivalent. Quantized 8-bit or 4-bit versions via `bitsandbytes` can run on 12GB VRAM cards (RTX 4070 Ti, RTX 3080) at a modest quality penalty. The fastest path to testing locally is a `bfloat16` load via `diffusers`, which uses roughly 20–22GB VRAM. Install the dependencies and download the gated model weights from HuggingFace (you need to accept the [dev] license on the model card before the download works).

```bash
pip install diffusers transformers accelerate torch sentencepiece protobuf
huggingface-cli login
huggingface-cli download black-forest-labs/FLUX.1-dev
```

Basic inference with the `diffusers` pipeline:

```python
import torch
from diffusers import FluxPipeline

pipe = FluxPipeline.from_pretrained(
    "black-forest-labs/FLUX.1-dev",
    torch_dtype=torch.bfloat16
)
pipe.enable_model_cpu_offload()  # required if <24GB VRAM

image = pipe(
    prompt="A product photo of a glass bottle of olive oil on a marble counter, soft studio lighting, photorealistic",
    height=1024,
    width=1024,
    guidance_scale=3.5,
    num_inference_steps=28,
    max_sequence_length=512,
    generator=torch.Generator("cpu").manual_seed(0)
).images[0]

image.save("output.png")
```

For FLUX.1 [schnell], swap the model ID to `black-forest-labs/FLUX.1-schnell` and set `num_inference_steps=4, guidance_scale=0.0` — Schnell is a distilled guidance-free model and does not use classifier-free guidance.

### Memory Optimization for Consumer GPUs

If you're on a 12GB card, use sequential CPU offload and 4-bit quantization:

```python
from diffusers import FluxPipeline
from transformers import BitsAndBytesConfig
import torch

nf4_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16
)

pipe = FluxPipeline.from_pretrained(
    "black-forest-labs/FLUX.1-dev",
    quantization_config=nf4_config,
    torch_dtype=torch.bfloat16
)
pipe.enable_sequential_cpu_offload()
```

This drops peak VRAM usage to approximately 12–14GB at the cost of 15–25% slower inference.

## FLUX.1 API Integration: BFL Native API, fal.ai, and Replicate

The BFL (Black Forest Labs) native API uses an asynchronous request-poll-retrieve pattern that requires two HTTP calls per image: a POST to submit the generation job, then a GET to poll for the result URL once the job completes. This is different from synchronous APIs like DALL-E and requires your code to handle polling logic explicitly. The BFL API exposes FLUX.1 [pro], FLUX.1.1 [pro], FLUX.2 [pro], and FLUX.1 Kontext — models not available via Hugging Face. Pricing is $0.03/image for FLUX.2 [pro] and $0.04/image for FLUX.1 Kontext Pro (image-to-image editing), which is 25–75% cheaper than DALL-E 3. Third-party API providers like fal.ai, Replicate, and DeepInfra offer synchronous wrappers around FLUX.1 [schnell] and [dev] with simpler integration at slightly higher prices per call. For serverless production workloads where you don't want to manage polling infrastructure, fal.ai's Python SDK is the lowest-friction option.

BFL native API submit + poll pattern:

```python
import requests
import time

API_KEY = "your_bfl_api_key"
BASE_URL = "https://api.bfl.ml"

def generate_image(prompt: str, width: int = 1024, height: int = 1024) -> str:
    # Step 1: Submit generation request
    response = requests.post(
        f"{BASE_URL}/v1/flux-pro-1.1",
        headers={"x-key": API_KEY, "Content-Type": "application/json"},
        json={
            "prompt": prompt,
            "width": width,
            "height": height,
        }
    )
    response.raise_for_status()
    request_id = response.json()["id"]
    
    # Step 2: Poll for result
    while True:
        result = requests.get(
            f"{BASE_URL}/v1/get_result",
            headers={"x-key": API_KEY},
            params={"id": request_id}
        )
        result_data = result.json()
        status = result_data.get("status")
        
        if status == "Ready":
            return result_data["result"]["sample"]
        elif status in ("Error", "Content Moderated"):
            raise RuntimeError(f"Generation failed: {status}")
        
        time.sleep(0.5)

image_url = generate_image(
    "A 3D product render of red wireless headphones on white background, commercial photography"
)
print(f"Image URL: {image_url}")
```

### fal.ai Synchronous SDK

For simpler integration without polling management:

```python
import fal_client

result = fal_client.subscribe(
    "fal-ai/flux/schnell",
    arguments={
        "prompt": "A product photo of red wireless headphones on white background",
        "image_size": "landscape_4_3",
        "num_inference_steps": 4,
        "num_images": 1,
        "enable_safety_checker": True
    }
)

image_url = result["images"][0]["url"]
print(f"Image URL: {image_url}")
```

### Replicate Python SDK

```python
import replicate

output = replicate.run(
    "black-forest-labs/flux-schnell",
    input={
        "prompt": "Photorealistic product shot of glass water bottle on marble surface",
        "aspect_ratio": "1:1",
        "output_format": "webp",
        "output_quality": 90
    }
)

print(output[0])
```

## Python Code Examples: End-to-End Image Generation with Each Provider

A production-ready image generation module should abstract over multiple providers, handle retries, and support both synchronous and asynchronous interfaces depending on the workload. The pattern below wraps BFL, fal.ai, and diffusers behind a common interface, letting you swap providers via configuration without touching application code. This is critical for cost management: route high-volume batch jobs to Schnell via self-hosted diffusers, route user-facing real-time requests to BFL Pro or fal.ai, and fall back to an alternative provider if one goes down. The full implementation below covers provider selection, async batch processing, error handling, and rate limiting — everything you need for a production image pipeline.

```python
import asyncio
import os
import time
from dataclasses import dataclass
from enum import Enum
from typing import Optional

import fal_client
import requests
from diffusers import FluxPipeline
import torch


class Provider(Enum):
    BFL = "bfl"
    FAL = "fal"
    LOCAL = "local"


@dataclass
class GenerationRequest:
    prompt: str
    width: int = 1024
    height: int = 1024
    steps: Optional[int] = None
    seed: Optional[int] = None


class FluxImageGenerator:
    def __init__(self, provider: Provider = Provider.FAL):
        self.provider = provider
        self._local_pipe = None

    def _get_local_pipe(self):
        if self._local_pipe is None:
            self._local_pipe = FluxPipeline.from_pretrained(
                "black-forest-labs/FLUX.1-schnell",
                torch_dtype=torch.bfloat16
            )
            self._local_pipe.enable_model_cpu_offload()
        return self._local_pipe

    def generate(self, req: GenerationRequest) -> str:
        if self.provider == Provider.BFL:
            return self._generate_bfl(req)
        elif self.provider == Provider.FAL:
            return self._generate_fal(req)
        else:
            return self._generate_local(req)

    def _generate_bfl(self, req: GenerationRequest) -> str:
        api_key = os.environ["BFL_API_KEY"]
        r = requests.post(
            "https://api.bfl.ml/v1/flux-pro-1.1",
            headers={"x-key": api_key},
            json={"prompt": req.prompt, "width": req.width, "height": req.height}
        )
        r.raise_for_status()
        job_id = r.json()["id"]
        for _ in range(60):
            poll = requests.get(
                "https://api.bfl.ml/v1/get_result",
                headers={"x-key": api_key},
                params={"id": job_id}
            )
            data = poll.json()
            if data["status"] == "Ready":
                return data["result"]["sample"]
            time.sleep(1)
        raise TimeoutError("BFL generation timed out")

    def _generate_fal(self, req: GenerationRequest) -> str:
        result = fal_client.subscribe(
            "fal-ai/flux/schnell",
            arguments={
                "prompt": req.prompt,
                "image_size": f"{req.width}x{req.height}",
                "num_inference_steps": req.steps or 4,
            }
        )
        return result["images"][0]["url"]

    def _generate_local(self, req: GenerationRequest) -> str:
        pipe = self._get_local_pipe()
        gen = torch.Generator("cpu").manual_seed(req.seed or 0)
        image = pipe(
            prompt=req.prompt,
            height=req.height,
            width=req.width,
            num_inference_steps=req.steps or 4,
            guidance_scale=0.0,
            generator=gen
        ).images[0]
        path = f"/tmp/flux_{int(time.time())}.png"
        image.save(path)
        return path
```

## LoRA Fine-Tuning: Training FLUX.1 on Your Own Images

LoRA (Low-Rank Adaptation) fine-tuning lets you train FLUX.1 to generate images in a custom style, reproduce a specific product, or consistently render a character — without retraining the full 12B parameters. LoRA fine-tuning FLUX.1 requires at least 12GB VRAM and 3–5 hours training time with a dataset of 20–50 images on a modern GPU (RTX 4090 or equivalent). The recommended tooling stack is ComfyUI with the ComfyUI-FluxTrainer extension, which wraps the `kohya-ss/sd-scripts` training loop with a visual node interface. You prepare a dataset of 20–50 captioned images (512×512 to 1024×1024), configure the LoRA rank (16 or 32 is standard, 64 for complex concepts), set learning rate to 1e-4 for FLUX.1 [dev], and run for 1000–2000 steps. The output is a `.safetensors` file that plugs directly into ComfyUI or the diffusers `load_lora_weights` API. A well-trained LoRA for a product style or fictional character converges within 1500 steps and produces recognizable results from text prompts using a trigger word.

Training a FLUX.1 LoRA via diffusers (simplified):

```python
from diffusers import FluxPipeline
from peft import LoraConfig, get_peft_model
import torch

# Load base model
pipe = FluxPipeline.from_pretrained(
    "black-forest-labs/FLUX.1-dev",
    torch_dtype=torch.bfloat16
)

# Configure LoRA
lora_config = LoraConfig(
    r=16,
    lora_alpha=16,
    target_modules=["to_q", "to_k", "to_v", "to_out.0"],
    lora_dropout=0.0,
    bias="none"
)

# Attach LoRA to transformer
pipe.transformer = get_peft_model(pipe.transformer, lora_config)
pipe.transformer.print_trainable_parameters()
# trainable params: ~12M || all params: 12B || trainable%: ~0.1%
```

Loading a trained LoRA for inference:

```python
pipe = FluxPipeline.from_pretrained(
    "black-forest-labs/FLUX.1-dev",
    torch_dtype=torch.bfloat16
)
pipe.load_lora_weights("./my_product_lora.safetensors")
pipe.enable_model_cpu_offload()

image = pipe(
    prompt="TRIGGERKEYWORD product on a clean white shelf, studio lighting",
    num_inference_steps=28,
    guidance_scale=3.5,
).images[0]
image.save("product_lora_output.png")
```

### Dataset Preparation Tips

Image quality matters more than quantity: 20 sharp, well-lit images with consistent framing outperform 200 scraped low-quality ones. Caption each image with detailed descriptive text (avoid keyword stuffing — natural sentences work better with FLUX.1's T5 text encoder). Use augmentation sparingly; FLUX.1 is more sensitive to caption quality than earlier diffusion models because of the joint text-image attention architecture.

## ComfyUI Integration: Node-Based Workflows for Visual Pipelines

ComfyUI provides a node graph interface for building FLUX.1 inference pipelines without writing Python code, making it the preferred tool for artists and designers who need fine-grained control over sampling parameters, LoRA stacking, and image-to-image workflows. ComfyUI's native FLUX.1 support arrived with the `ComfyUI-GGUF` extension, which lets you load 4-bit and 8-bit quantized FLUX.1 checkpoints (Q4_K_M quantization runs on 10–12GB VRAM). The standard FLUX.1 [dev] workflow in ComfyUI chains: `Load Checkpoint` → `CLIP Text Encode (FLUX)` → `KSampler` → `VAE Decode` → `Save Image`. For LoRA workflows, insert a `Load LoRA` node between the checkpoint and the sampler, setting strength between 0.7–1.0 for style, 0.5–0.8 for character consistency. The ComfyUI API server mode exposes all node workflows as HTTP endpoints, making it practical to embed ComfyUI as a local inference microservice in larger applications.

### ComfyUI API Server Mode

Start ComfyUI with API access enabled, then submit workflows programmatically:

```python
import json
import requests
import websocket
import uuid

SERVER = "127.0.0.1:8188"

def queue_prompt(workflow: dict) -> str:
    client_id = str(uuid.uuid4())
    payload = {"prompt": workflow, "client_id": client_id}
    r = requests.post(f"http://{SERVER}/prompt", json=payload)
    return r.json()["prompt_id"]

def wait_for_result(prompt_id: str) -> list[str]:
    ws = websocket.WebSocket()
    ws.connect(f"ws://{SERVER}/ws?clientId={prompt_id}")
    while True:
        msg = json.loads(ws.recv())
        if msg["type"] == "executing" and msg["data"].get("node") is None:
            break
    ws.close()
    r = requests.get(f"http://{SERVER}/history/{prompt_id}")
    outputs = r.json()[prompt_id]["outputs"]
    return [img["filename"] for node in outputs.values() for img in node.get("images", [])]
```

## Hardware Requirements and Performance Benchmarks

FLUX.1 hardware requirements differ significantly by model variant, and undersizing will cause OOM errors or force quantization that degrades quality. The full FLUX.1 model requires at least 24GB VRAM — RTX 4090, RTX 5090, or professional datacenter GPUs — when loading in bfloat16. Quantized versions via bitsandbytes or GGUF (Q4_K_M) run on 12GB VRAM cards like RTX 4070 Ti or RTX 3080, with a 5–15% quality penalty at 4-bit quantization. FLUX.2 [dev] at 32B parameters requires dual RTX 3090s (48GB total VRAM) for local inference, which is cost-prohibitive for most individual developers; the practical recommendation for 2026 is FLUX.2 via API until consumer 48GB single-card GPUs become mainstream.

| GPU | VRAM | FLUX.1 [schnell] | FLUX.1 [dev] | FLUX.2 [dev] |
|---|---|---|---|---|
| RTX 3080 | 10GB | 4-bit quant only | 4-bit quant only | API only |
| RTX 4070 Ti | 12GB | 8-bit quant | 8-bit quant | API only |
| RTX 4090 / 5090 | 24GB | Full precision | Full precision | API only |
| Dual RTX 3090 | 48GB | Full precision | Full precision | Full precision |
| A100 80GB | 80GB | Full precision | Full precision | Full precision |

Performance benchmarks at 1024×1024:
- FLUX.1 [schnell] 4 steps: ~1.2 seconds on RTX 4090
- FLUX.1 [dev] 28 steps: ~12 seconds on RTX 4090
- FLUX.1 [schnell] 4 steps: ~0.7 seconds on H100

For cloud GPU rental, Lambda Labs and RunPod offer RTX 4090 instances at $0.50–$0.75/hour. At 1.2 seconds per Schnell image, you generate approximately 3,000 images per GPU-hour — an effective cost of ~$0.0002/image versus $0.03/image via BFL API, a 150× cost reduction at sufficient scale.

## Pricing Guide: BFL API vs Third-Party Providers in 2026

API pricing for FLUX.1 varies by 10–100× depending on provider and model tier, and choosing the right provider for each workload is the largest lever for controlling inference costs in production. Black Forest Labs' native BFL API is the primary source for FLUX.1 [pro] and FLUX.2 family models: FLUX.2 [pro] costs $0.03/image, FLUX.1 Kontext Pro (image-to-image editing) costs $0.04/image, and FLUX.2 Flex (cost-optimized) starts at $0.01/image. FLUX.2 Pro is approximately 25–75% cheaper than DALL-E 3 for equivalent quality, making it the default recommendation for commercial applications that don't require DALL-E 3's content policy profile. Third-party providers like fal.ai, Replicate, and DeepInfra host [schnell] and [dev] at prices ranging from $0.003–$0.015/image, offering significant savings for non-commercial or research use. For teams running high-volume generation at scale (100K+ images/month), self-hosting FLUX.1 [schnell] on spot GPU instances reduces costs to roughly $0.0002–$0.001/image depending on hardware pricing.

| Provider | Model | Price/Image | Notes |
|---|---|---|---|
| BFL API | FLUX.2 [pro] | $0.03 | Best quality, async polling |
| BFL API | FLUX.1 Kontext Pro | $0.04 | Image-to-image editing |
| BFL API | FLUX.2 Flex | $0.01 | Cost-optimized |
| fal.ai | FLUX.1 [schnell] | $0.003 | Synchronous SDK |
| fal.ai | FLUX.1 [dev] | $0.025 | Higher quality |
| Replicate | FLUX.1 [schnell] | $0.003 | Per-run billing |
| Self-hosted | FLUX.1 [schnell] | $0.0002–$0.001 | GPU rental dependent |

### Cost Optimization Strategies

Use Schnell for volume, Dev or Pro only when the user sees the result. Cache repeated prompt templates by storing seed + prompt hash pairs. Batch requests to third-party APIs where available. Set a hard cap on maximum resolution — 1024×1024 is the performance sweet spot and going to 2048×2048 quadruples compute cost with marginal user-visible quality gain at typical display sizes.

## FLUX.1 vs FLUX.2: Should You Upgrade in 2026?

FLUX.2 [dev], released January 15, 2026, is a 32-billion parameter model and currently leads the Artificial Analysis open-weights image generation leaderboard — it produces noticeably better anatomical accuracy, lighting coherence, and multi-subject composition than FLUX.1 [dev]. The catch is hardware: FLUX.2 locally requires dual RTX 3090s (48GB VRAM), which costs roughly $3,000–$4,000 in hardware or $1.50–$2.00/hour on cloud instances. For teams using FLUX via API, the upgrade decision is simpler: FLUX.2 [pro] at $0.03/image delivers the quality jump without local hardware constraints. The recommendation for 2026 is straightforward: use FLUX.1 [schnell] for local development and batch jobs where cost matters; use FLUX.2 [pro] via BFL API for production user-facing features; evaluate FLUX.2 locally only if you have existing 48GB VRAM infrastructure already deployed for other workloads. FLUX.1 still delivers excellent results for the majority of use cases, and the ecosystem of community LoRAs, ComfyUI nodes, and fine-tuning resources is larger and more mature for FLUX.1 than FLUX.2 at this stage.

### Migration Path from FLUX.1 to FLUX.2

FLUX.2 uses the same API interface as FLUX.1 on BFL and fal.ai — swap the model ID string and you're done. Existing LoRAs trained on FLUX.1 are not directly compatible with FLUX.2; you'll need to retrain on the larger base model. If you have active FLUX.1 LoRAs in production, the upgrade cost includes LoRA retraining time, which is the primary reason to stay on FLUX.1 if your current quality meets product requirements.

## Real-World Use Cases: Product Mockups, Marketing Assets, and Game Development

FLUX.1's combination of photorealism, reliable text rendering, and commercial licensing (Schnell tier) makes it the practical foundation for several high-value production pipelines in 2026. E-commerce teams use FLUX.1 [schnell] to generate on-demand product photography variations — placing existing product images in new environments, generating lifestyle shots in different seasonal settings, and A/B testing marketing imagery at a fraction of traditional photo studio costs. Game studios use FLUX.1 for concept art generation, texture synthesis, and character design exploration, where Schnell's 1-second inference allows real-time iteration within design tools. Marketing automation pipelines generate personalized banner ads, email headers, and social media assets at scale, using FLUX.1 via fal.ai or BFL API integrated with content management systems. FLUX.1 Kontext Pro adds image-to-image editing with character consistency at $0.04/image, which enables workflows like: take a product image → relight it → place it in a new background → generate variants with different color options — all maintaining the original product's identity across edits.

### Product Visualization Pipeline

A minimal product mockup generation pipeline:

```python
import fal_client
from PIL import Image
import io
import base64

def generate_product_mockup(
    product_image_path: str,
    background_prompt: str,
    num_variants: int = 4
) -> list[str]:
    with open(product_image_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()
    
    results = []
    for i in range(num_variants):
        result = fal_client.subscribe(
            "fal-ai/flux-kontext/schnell",
            arguments={
                "prompt": f"Place this product in the following scene: {background_prompt}. Keep the product identical, only change the background environment.",
                "image_url": f"data:image/jpeg;base64,{img_b64}",
                "num_inference_steps": 4,
                "seed": i * 1000
            }
        )
        results.append(result["images"][0]["url"])
    
    return results

# Usage
urls = generate_product_mockup(
    "product.jpg",
    "modern kitchen counter with natural window light, warm morning atmosphere",
    num_variants=4
)
```

### Game Asset Generation Workflow

For game studios generating texture and concept art:

```python
def generate_game_assets(concept: str, style: str, asset_type: str) -> list[str]:
    prompts = [
        f"{asset_type}: {concept}, {style}, game asset, clean background",
        f"{asset_type}: {concept} variant 2, {style}, game concept art",
        f"{asset_type}: {concept} variant 3, {style}, detailed texture reference",
    ]
    
    generator = FluxImageGenerator(provider=Provider.FAL)
    return [
        generator.generate(GenerationRequest(prompt=p, width=1024, height=1024))
        for p in prompts
    ]
```

## FAQ

The most common questions developers ask before adopting FLUX.1 center on licensing, hardware requirements, and how it stacks up against commercial alternatives like DALL-E 3. FLUX.1 is a model family with distinct tiers — the right choice depends on whether you need commercial rights (Schnell, Apache 2.0 licensed), maximum quality with self-hosted open weights (Dev, non-commercial research license), or a fully managed commercial API without local hosting overhead (Pro, available via BFL API, fal.ai, and Replicate only). Hardware requirements range from 12 GB VRAM with 4-bit quantization all the way to 24 GB VRAM for full bfloat16-precision inference on the Dev model. LoRA fine-tuning is well-supported on FLUX.1-Dev using consumer GPUs such as the RTX 4090 and is the standard path for custom character and style transfer. Cost comparisons against DALL-E 3 and Stable Diffusion XL shift substantially once self-hosting enters the equation — at 100K+ images per month, self-hosted Schnell costs less than $0.001 per image. The five answers below cover the recurring blockers that developers encounter when moving from prototype to production with FLUX.1.

### What license does FLUX.1 use?

FLUX.1 [schnell] is Apache 2.0 licensed, fully permitting commercial use. FLUX.1 [dev] uses a non-commercial research license that permits development and personal use but prohibits commercial deployment. FLUX.1 [pro] is accessible only via the BFL API under commercial terms — there are no weights to download.

### How much VRAM do I need to run FLUX.1 locally?

The full FLUX.1 model in bfloat16 precision requires 24GB VRAM (RTX 4090 or equivalent). With 4-bit quantization via bitsandbytes or GGUF format, you can run FLUX.1 on 12GB VRAM, though with a 5–15% quality penalty depending on quantization level.

### What is the difference between FLUX.1 Schnell and Dev?

FLUX.1 [schnell] generates images in 1–4 steps using a guidance-free distillation approach, producing results at approximately 75–80% the quality of [pro] with very fast inference. FLUX.1 [dev] takes 20–50 steps using classifier-free guidance, producing 90–95% of [pro] quality. Schnell is Apache 2.0 licensed; Dev is non-commercial only.

### Can I fine-tune FLUX.1 on custom images?

Yes. LoRA fine-tuning FLUX.1 [dev] requires at least 12GB VRAM and 20–50 captioned training images. Training takes 3–5 hours on a modern GPU for 1000–2000 steps. The recommended tools are ComfyUI with ComfyUI-FluxTrainer, or the `diffusers` training scripts with PEFT/LoRA. The resulting `.safetensors` file loads into both ComfyUI and diffusers pipelines.

### How does FLUX.1 compare to DALL-E 3 for developer use?

FLUX.1 [pro] and FLUX.2 [pro] via BFL API are 25–75% cheaper than DALL-E 3 at comparable quality levels. FLUX.1 [schnell] (Apache 2.0) can be self-hosted at ~$0.0002/image for high-volume workloads. DALL-E 3 has a more permissive content policy for certain use cases and tighter OpenAI platform integration, but FLUX.1 wins on cost, open-source access, and fine-tuning capability.