---
title: "Running LLM Commands on ESP32: Embedded AI Agent Hardware"
date: 2026-08-28T10:01:32+00:00
tags:
  - esp32
  - llm
  - embedded ai
  - edge ai
  - microcontroller
  - ai agent
description: "Yes — you can run LLM commands on an ESP32. A 28.9M-parameter model runs on-device at ~10 tokens/sec, but real instruction-following needs a bigger chip or the cloud."
draft: false
cover:
  image: "/images/esp32-llm-commands-embedded-2026.png"
  alt: "Running LLM Commands on ESP32: Embedded AI Agent Hardware"
  relative: false
schema: "schema-esp32-llm-commands-embedded-2026"
---

Yes, you can run LLM commands on an ESP32. A 28.9M-parameter language model runs fully on-device on an ESP32-S3 at about 9.88 tokens per second, with 25M parameters stored in flash using Google's Per-Layer Embeddings. However, models this small cannot follow instructions, answer questions, or write code — so true command execution requires either a more capable chip like the ESP32-P4 or a cloud-assisted setup.

## Why Run an LLM on a $6 Microcontroller

The ESP32 family is the most popular microcontroller line in the maker and IoT world, and it costs as little as $6 to $10 per board. Running a language model on it means you get local, private, offline inference on hardware that costs less than a cup of coffee. There is no cloud bill, no network dependency, and no data leaving your device.

For command-style interaction — wake-word detection, simple voice replies, or recognizing a fixed set of commands — an on-device model is fast enough. The appeal is real: a 28.9M-parameter model on an ESP32-S3 produces output at 9.88 tokens/sec end-to-end, which is usable for short responses and command recognition. The tradeoff is that these models are trained on narrow datasets like TinyStories, so they are not general-purpose assistants.

The key insight from the community is that memory, not compute, is the binding constraint. An ESP32-S3 has only 512KB of SRAM, but it can be paired with up to 8MB of PSRAM and 16MB of flash. Getting a useful model to fit inside those limits is the entire engineering challenge.

## The Memory Problem — SRAM, PSRAM, and Flash on ESP32

To understand why running an LLM on an ESP32 is hard, you have to understand the three-tier memory layout. Each tier has a different speed and size, and a model must be distributed across all three.

- **SRAM (512KB on the S3):** The fastest memory, used for activations and normalization weights. It is tiny, so only the most frequently accessed data lives here.
- **PSRAM (up to 8MB on the S3, 32MB on the P4):** Slower but much larger. This holds the core transformer weights and the head of the model.
- **Flash (16MB on the S3):** The slowest but largest tier. This is where the bulk of the embedding table lives, accessed via a flash lookup table.

The slvDev/esp32-ai project demonstrates this layout in practice. It stores 25M parameters in a flash lookup table using Google's Per-Layer Embeddings, keeping activations and norm weights in SRAM, the core and head in PSRAM, and the 25M-parameter embedding table in flash. At inference time, the model samples only about 450 bytes per token from that flash table, which keeps the memory bandwidth manageable.

This three-tier approach is what makes a 14.9MB model at 4-bit quantization feasible on a board with just 512KB of SRAM. Without it, the model simply would not fit.

## Per-Layer Embeddings: How 28.9M Parameters Fit in Flash

The breakthrough that makes on-device ESP32 LLMs practical is Google's Per-Layer Embeddings technique. Instead of keeping a full embedding matrix in fast memory, the approach stores the embedding table in flash and samples only the rows needed for the current token.

In the esp32-ai project, the model has 28.9M total parameters, of which 25M live in the flash lookup table. At each token, the system reads roughly 450 bytes from flash rather than loading the entire table. This is the difference between a model that fits and one that overflows the memory budget.

The result is a 14.9MB model at 4-bit quantization that runs end-to-end at 9.88 tokens/sec. The project ships two example models: Barista, which answers questions about espresso, and TinyStories, which generates short stories. Both are trained on the TinyStories dataset, which is why they cannot answer general questions, follow instructions, write code, or recall facts.

This is the fundamental limitation to understand: the technique makes a small model fit, but it does not make the model smarter. The model is only as capable as its training data.

## Choosing a Chip — ESP32-S3 vs ESP32-P4 for AI

If you are serious about running LLM commands on embedded hardware, the chip you choose matters more than almost anything else. The two main candidates are the ESP32-S3 and the ESP32-P4.

| Feature | ESP32-S3 | ESP32-P4 |
|---------|----------|----------|
| SRAM | 512KB | Larger (with DIRAM) |
| PSRAM | Up to 8MB | Up to 32MB |
| Flash | Up to 16MB | Up to 16MB+ |
| Clock | 240MHz | 400MHz |
| AI acceleration | None (ESP-DSP SIMD) | XespV (up to 30x speedup) |
| Max model size | ~28.9M params (single board) | ~180.9M params |
| Typical cost | ~$6-10 | ~$6-10 |
| Agent capability | Limited | Early Instruct/Agent (unstable) |

The ESP32-P4 is a major upgrade for AI workloads. It supports up to 32MB of PSRAM, runs at 400MHz, and includes XespV hardware acceleration that delivers up to 30x speedup on certain operations. The p-for-llm project runs a 180.9M-parameter model on the P4 at about 9 tokens/sec using a PLE-MoE-W1.58A8 architecture that mixes ternary, Q8, and FP16 storage totaling roughly 44MiB across flash and PSRAM.

The P4 also has early Instruct (ChatML) and Agent capabilities, though they are still unstable. If your goal is a real embedded AI agent that can follow commands, the P4 is the more promising path. The S3 is cheaper and more widely available, but it is limited to the smallest models.

## Setting Up the Toolchain (ESP-IDF, fetch_model.sh, deploy.sh)

Getting a model onto an ESP32 requires the ESP-IDF toolchain and a two-step workflow. The esp32-ai project provides a clean template you can follow.

First, install the ESP-IDF development environment. This is the standard Espressif toolchain for building and flashing firmware. Once it is set up, the workflow is:

1. **fetch_model.sh** — downloads the model and verifies its integrity. This ensures you have the correct weights before you try to flash them.
2. **deploy.sh** — compiles the firmware and flashes it to the board.

The model weights are transferred to the board over USB at startup in some setups, which keeps the flash footprint small. If you add an SD card, the P4 can run fully offline without needing to re-transfer weights on every boot.

For the S3, the AIWintermuteAI/esp32-llm project shows the optimization path: dual-core math, ESP-DSP SIMD dot products, a 240MHz CPU with 80MHz PSRAM overclock, and a larger instruction cache. These optimizations pushed a 260K-parameter model to 19.13 tokens/sec. Even a small model needs about 1MB of RAM, so choose a board with PSRAM and flash headroom.

## Building a Command-Ready On-Device Model

If you want an on-device model that can actually respond to commands, you need to think about what "command" means at this scale. A model trained on TinyStories cannot follow instructions, so you cannot just ask it to do things.

The realistic approach is to build a model that recognizes a fixed vocabulary of commands and produces short, predictable responses. This works well for voice replies and command recognition, where the output space is small and well-defined. The 9-20 tokens/sec throughput is fine for these use cases.

For a command-ready model, you would train or fine-tune on a dataset that matches your specific commands, then quantize to 4-bit or W1.58 to fit the memory budget. The quantization choice matters: 4-bit is the sweet spot for the S3, while the P4's W1.58A8 mixed-precision approach packs more parameters into the same footprint.

The key expectation to set: at this scale, the model is a command recognizer and short-response generator, not a general assistant. It can tell you the weather if you hard-code the logic, but it cannot reason about the world.

## Going Further — Multi-Board Distributed Inference and KV Caches

When a single board's flash is not enough, you can split the model across multiple boards. The wladimiravila/esp32s3-distributed-ai project runs a 56M-parameter LLM across three ESP32-S3 boards communicating over ESP-NOW.

The architecture uses a technique called Split-PLE, where the 50.3M-parameter embedding table is split across boards A and B so each fits in 16MB of flash. Board C hosts the WiFi and a web server, streaming generated text to a browser via Server-Sent Events (SSE). Board B keeps a 1.5MB KV cache in PSRAM (256 positions) so the transformer can attend to the full sequence.

This distributed approach shows how to scale past a single board's limits, but it adds real complexity. You now have to manage inter-board communication, synchronization, and the latency of ESP-NOW. It is a research-grade solution, not something you would deploy casually.

The KV cache is the other scaling lever. By keeping the key-value cache in PSRAM, the model can attend to longer sequences without recomputing. This is essential for anything beyond the shortest responses.

## When to Offload — Cloud-Assisted Voice and Agent Commands

If you need real agent behavior — instruction following, factual answers, code generation — a fully on-device SLM will not cut it. The honest answer is that command execution at this level requires either a bigger chip or a cloud model.

The cloud-assisted path is well established. The ElatoAI project runs realtime voice AI on ESP32 backed by Cloudflare Durable Objects and Workers AI, using Deepgram for speech-to-text and text-to-speech. It supports 100+ voice models and secure WebSockets for conversations lasting more than 20 minutes. This is the "agent" path for command-style interaction: the ESP32 handles audio capture and playback, while the heavy lifting happens in the cloud.

The alternative is a local model on a more powerful device. The local-ai-toys project supports local LLMs and TTS (Qwen, Mistral) via MLX on ESP32 devices, bridging the gap between fully-on-device and fully-cloud.

The decision comes down to your constraints. If privacy, offline operation, and cost are paramount, accept the limits of an on-device SLM. If you need real intelligence, offload to the cloud and use the ESP32 as a smart peripheral.

## Practical Limits and What an Embedded SLM Can and Can't Do

It is worth being explicit about the limits, because the marketing around "AI on microcontrollers" often oversells what is possible.

**What an embedded SLM can do:**
- Generate short, predictable responses at 9-20 tokens/sec
- Recognize a fixed vocabulary of commands
- Produce voice replies and simple text output
- Run fully offline and privately on a $6 board

**What an embedded SLM cannot do:**
- Follow arbitrary instructions
- Answer factual questions
- Write or debug code
- Recall knowledge beyond its narrow training data
- Maintain long, coherent conversations without a KV cache

The 28.9M-parameter model on the S3 is trained on TinyStories, so it generates stories but cannot answer questions. The 180.9M-parameter model on the P4 has early Instruct and Agent capabilities, but they are unstable. The 260K-parameter tinyllamas model is a proof of concept that the authors themselves describe as "not very useful" for real tasks.

Set your expectations accordingly. An embedded SLM is a command recognizer and short-response generator, not a general assistant.

## Conclusion — Building a Real Embedded AI Agent

Running LLM commands on an ESP32 is genuinely possible, and the ecosystem is maturing fast. The ESP32-S3 can run a 28.9M-parameter model on-device at ~10 tokens/sec using Per-Layer Embeddings and a three-tier memory layout. The ESP32-P4 pushes this to 180.9M parameters with hardware acceleration and early agent capabilities.

The path to a real embedded AI agent depends on your definition of "agent." For fixed command recognition and short voice replies, a fully on-device SLM on an S3 or P4 is enough. For true instruction-following and reasoning, you need either a distributed multi-board setup or a cloud-assisted architecture where the ESP32 handles the interface and the cloud handles the intelligence.

Start with the esp32-ai workflow: install ESP-IDF, run fetch_model.sh and deploy.sh, and get a model flashing on a board with PSRAM and flash headroom. Then decide whether your commands fit in a small on-device model or whether you need to offload. Either way, the hardware is cheap, the tools are open source, and the field is moving quickly.

## FAQ

**Can you run an LLM on an ESP32?**
Yes. An ESP32-S3 can run a 28.9M-parameter language model fully on-device at about 9.88 tokens/sec, and an ESP32-P4 can run a 180.9M-parameter model at about 9 tokens/sec.

**What is the best ESP32 for running LLM commands?**
The ESP32-P4 is the best choice for AI because it supports up to 32MB of PSRAM, runs at 400MHz, and has XespV hardware acceleration with up to 30x speedup. The ESP32-S3 is cheaper but limited to the smallest models.

**How do you fit a language model into an ESP32's limited memory?**
By using a three-tier memory layout: activations and norm weights in SRAM, core and head weights in PSRAM, and the embedding table in flash. Google's Per-Layer Embeddings technique stores 25M parameters in flash and samples only ~450 bytes per token.

**Can an ESP32 LLM follow instructions or answer questions?**
Not reliably. Models trained on narrow datasets like TinyStories cannot follow instructions, answer questions, write code, or recall facts. Real instruction-following requires a bigger chip or a cloud model.

**What is the difference between on-device and cloud-assisted ESP32 AI?**
On-device AI runs a small model locally for privacy and offline operation, but it is limited to simple commands. Cloud-assisted AI uses the ESP32 for audio and interface while a cloud model (like Cloudflare Workers AI) handles the intelligence, enabling real agent behavior.
