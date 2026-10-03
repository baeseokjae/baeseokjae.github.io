---
title: "Skadoosh Voice Agent Review: A Fully Local Rust Voice Framework (and a 404 Problem)"
date: 2026-10-01T01:59:08+00:00
tags:
  - rust
  - voice-ai
  - local-first
  - voice-agents
  - skadoosh
  - whisper
  - kokoro-tts
  - silero-vad
  - barge-in
  - ollama
description: "Skadoosh is a fully local Rust voice agent: whisper-rs STT, Silero VAD, Kokoro TTS and Ollama, with no API keys. Strong architecture, but its repo 404s."
draft: false
cover:
  image: "/images/skadoosh-local-voice-agent-rust.png"
  alt: "Skadoosh Voice Agent Review: A Fully Local Rust Voice Framework (and a 404 Problem)"
  relative: false
schema: "schema-skadoosh-local-voice-agent-rust"
---

Skadoosh is a dual-licensed (MIT OR Apache-2.0) Rust crate that runs a complete voice agent on your own machine: cpal microphone capture, Silero VAD, whisper-rs speech recognition, a streaming Ollama LLM, clause-level splitting, and ONNX Kokoro-82M text-to-speech back out through your speakers — with no API keys and no network calls. It is the most feature-complete all-local Rust voice agent published to crates.io, and it is also effectively unmaintained, because its documented GitHub repository returns HTTP 404.

Both halves of that sentence matter, and a review that only reports one of them is useless. The architecture here is genuinely interesting: 22,255 lines of Rust across 83 source files, `#![forbid(unsafe_code)]`, 188 test functions, a lock-free barge-in path, and a pluggable engine model that Pipecat fans will recognize immediately. What is not interesting is the distribution story — a vanished repository, two contradictory author identities, a default model whose own card says the project "has been deprecated," 389 lifetime downloads, and zero reverse dependencies.

This review walks the pipeline stage by stage, reproduces the honest latency math on consumer hardware, compares Skadoosh against Pipecat, LiveKit Agents, Hugging Face speech-to-speech, Moshi, pipecrab, Vox, and EchoKit, and explains exactly what you can and cannot verify from a crate whose source of truth is a tarball. Every number below is sourced and labeled — author claims are called author claims, and third-party benchmarks are named as such.

## What Is Skadoosh and What Does "Local Voice Agent in Rust" Actually Mean?

Skadoosh is a single Rust binary that closes the loop from microphone to speaker without a transport layer. There is no WebRTC signalling, no SIP bridge, no WebSocket session with a hosted model — the audio device *is* the transport, and the model runs in a child process on the same box.

That is a different category from what most "voice agent framework" articles cover. Pipecat and LiveKit Agents are pipeline and transport products: you assemble stages and connect them to telephony or a browser. Skadoosh skips the assembly and the transport, and ships one opinionated path — microphone in, agent reply out — that you can embed as a library or run as a CLI.

The crate's own numbers set the scale of the project. Version 0.12.1 (published 2026-08-23) unpacks to a 263,897-byte tarball containing 93 files, 83 of them Rust, with a `Cargo.lock` pinning 370 packages ([crates.io](https://crates.io/api/v1/crates/skadoosh)). rustdoc coverage is complete: 409 of 409 items documented, though only 4 of 210 items carry examples ([docs.rs](https://docs.rs/crate/skadoosh/latest)). Its runtime dependencies are mainstream and healthy — whisper-rs (1.37M downloads), cpal (22.3M), ort (20.2M), wasmtime (38.0M), and misaki-rs (72K) — so the supply-chain risk is concentrated in Skadoosh itself, not in what it pulls in.

Two design choices are unusual enough to note up front. First, the crate declares `#![forbid(unsafe_code)]` at the crate root, and a grep across `src/` finds no unsafe blocks at all — only three doc-comment mentions. That is a real constraint for a project that touches realtime audio callbacks, and it is why the barge-in path is built from an atomic epoch rather than a mutex. Second, the model weights are *not* vendored. You bring your own Ollama model, your own Whisper GGML file, and your own Kokoro ONNX bundle, which keeps the crate small but pushes the real install cost into a `download_models.sh` step.

## How Does the Seven-Stage Pipeline Actually Work?

The documented pipeline is a straight cascade, and every stage is a boxed trait object: `SttEngine`, `LlmBackend`, and `TtsEngine`. The flow is:

1. **cpal capture** — 16 kHz mono from the default input device.
2. **Silero VAD** — voice activity detection gating the utterance boundary.
3. **whisper-rs STT** — whole-utterance transcription of the captured buffer.
4. **Streaming LLM** — an OpenAI-compatible chat endpoint, Ollama by default.
5. **Clause splitting** — the reply text is broken at clause boundaries rather than sentence or paragraph boundaries.
6. **Kokoro ONNX TTS** — 82M-parameter synthesis via `ort`, phonemised by the misaki-rs grapheme-to-phoneme port.
7. **cpal playback** — output through the same audio subsystem, with echo cancellation from aec-rs.

Two stages deserve scrutiny, because they are where this architecture differs from the 2026 state of the art.

The VAD stage is cheap and reliable. Silero VAD processes a 30+ ms chunk in under 1 ms on a single CPU thread under an MIT license ([silero-vad](https://github.com/snakers4/silero-vad)), which means endpointing contributes essentially nothing to the latency budget. Skadoosh gates utterance end on roughly 300 ms of silence.

The STT stage is the architectural weak point. Skadoosh transcribes a *complete utterance* with whisper.cpp after the silence gate closes. whisper.cpp is mature and frugal — 75 MiB of disk and about 273 MB of RAM for `tiny`, 466 MiB and roughly 852 MB for `small` ([whisper.cpp](https://github.com/ggml-org/whisper.cpp)) — but it is not a streaming recognizer. By 2026, the Python ecosystem had already moved past this: RealtimeSTT's own CPU guidance names sherpa-onnx Nemotron-3.5 streaming (560 ms) and Parakeet TDT int8 as the production profile ([RealtimeSTT](https://github.com/KoljaB/RealtimeSTT)), and Hugging Face's speech-to-speech defaults to Parakeet TDT. Skadoosh's design means you pay the silence gate in full before transcription starts, and you get no partial transcripts while the user is still talking. On a fast desktop that is tens of milliseconds of regret. On a loaded machine it is the difference between a conversation and a walkie-talkie.

## The Two Features That Actually Decide Whether It Feels Conversational

Feature-count comparisons between voice frameworks are mostly noise. In practice, two things determine whether a local agent feels alive or feels like a fax machine: whether TTS can start before the LLM finishes, and whether you can interrupt it.

### Does clause-level streaming TTS Matter More Than Model Quality?

It matters more than people expect. A 1.5B local model generating at 4-8 tokens per second takes many seconds to write a three-sentence answer, and a pipeline that waits for the final token before synthesizing anything produces dead air for that entire duration.

Skadoosh splits the streamed reply at clause boundaries and dispatches each clause to Kokoro as soon as it closes. The first clause typically arrives after the opening sentence fragment, so time-to-first-audio tracks the model's time-to-first-token rather than its full generation time. Combined with Kokoro's characteristics — ELO 1059 on Artificial Analysis's speech leaderboard, fractionally ahead of Cartesia Sonic 3 at 1054, at roughly 80-120 ms time-to-first-audio on an M3 Pro ([Kokoro benchmark roundup](https://academy.kspl.tech/blog/voice-agents-2026-tts-latency-benchmark)) — the audio starts early and the backlog drains while you listen.

The trade-off is prosody. Synthesis driven by clause fragments loses the sentence-level intonation contour of a model that sees the whole reply. Skadoosh's README addresses this by modulating TTS speed with the model's emotional tone, which is a reasonable mitigation but not a substitute for whole-reply synthesis.

### Is the 5-10 ms Barge-In Number Real?

The mechanism is real and verifiable. The barge-in path uses an `AtomicU64` epoch that the caller increments on interruption; the realtime audio callback reads that epoch and compares it against the epoch it was launched with, and every queued clip push re-checks it before writing to the ring buffer. A stale callback or a stale clip silently discards its data instead of fighting for a lock. This is the correct way to do it in a realtime audio context, because a mutex on the audio thread is a priority-inversion hazard, and a design that `forbid`s unsafe code cannot reach for lock-free primitives that hide unsafe internally.

The *timing*, however, is an author claim. The "5-10 ms" figure appears in the README and has not been reproduced by any third party. What you can verify is that no lock is taken, no allocation happens in the callback, and the check is a single atomic load. What you cannot verify is the measured cutoff on your hardware, because no published end-to-end benchmark of Skadoosh exists at all.

The honest position: the crate exposes a `StageLatency` `AgentEvent` carrying `stt_ms`, `llm_ms`, `tts_ms`, and `playback_ms`. That is the right answer to an unverifiable claim — instrument it yourself. Anyone quoting 5-10 ms barge-in as a measured fact is repeating marketing.

## How Do You Install and Run Skadoosh?

Build prerequisites are Rust 1.88 or newer plus a native toolchain: `cmake`, `clang`, `libclang-dev`, `libasound2-dev`, `pkg-config`, and `espeak-ng` for Kokoro phonemisation ([SETUP.md](https://docs.rs/crate/skadoosh/latest/source/SETUP.md)). The `espeak-ng` dependency is worth flagging for commercial users — it is GPL-licensed and ships as a runtime requirement for speech synthesis, which needs a licence review before you embed this in a closed-source product.

After the binary builds, you fetch models with the bundled `download_models.sh`, pull the default LLM through Ollama, and run `skadoosh`. Two flags matter for evaluation: `--repl` for a text-only loop that skips audio entirely (invaluable for isolating whether a problem is your model or your microphone), and `--selftest` to validate the audio and model paths without holding a conversation.

On the hardware side, be realistic about the memory footprint. The default LLM is StealthyLM-Emotive, a Qwen2.5-1.5B 4-bit GGUF at 1.54B parameters — call it ~1.5 GB resident. Whisper `tiny.en` adds about 273 MB, Kokoro ONNX a few hundred megabytes more. Total system requirement lands near 2-3 GB, which is genuinely modest and far below the 16 GB unified memory or ~24 GB VRAM floor that Hugging Face documents for a fully local conversation stack ([speech-to-speech](https://github.com/huggingface/speech-to-speech)).

## The 5-Line SDK vs. the CLI

The advertised embedding story is short:

```rust
let mut agent = Agent::builder()
    .config(config)
    .build()?;
agent.run().await?;
```

Whether that abstraction holds up depends entirely on the traits. `SttEngine`, `LlmBackend`, and `TtsEngine` are the seams, and because every stage is a boxed trait object, you can substitute a different recognizer, a hosted LLM endpoint, or a different synthesizer without forking the pipeline. This is the same pluggability promise Pipecat makes in Python, executed in-process with no FFI marshalling of audio buffers between stages. That is not a cosmetic difference: a Python pipeline crossing into a native VAD or TTS library pays a copy per stage and inherits the interpreter's scheduling jitter, and the GIL means a busy Python stage can delay an audio callback that Rust would service deterministically.

The CLI is the more pragmatic entry point. `--repl` gives you a conversational loop with no audio, which is how you should evaluate whether the 1.5B model is good enough for your task before you invest in microphones and echo cancellation.

## Beyond a Basic Agent: WASM Plugins, Mesh, RAG, and Watchers

This is where Skadoosh stops resembling its competitors, and it is worth separating features that are genuinely rare from features that are merely listed.

**WASM plugin sandbox.** Tools are implemented as WebAssembly modules executed by wasmtime 30 with no filesystem and no network access, bounded by fuel metering. The LLM calls them as tools. Nothing in the Pipecat, LiveKit, or speech-to-speech feature sets offers an equivalent in-process capability sandbox, and fuel-bounded WASM is a defensible security posture for model-authored actions.

**LAN multi-agent mesh.** UDP discovery plus call forwarding lets several instances find each other and hand off conversations. This is unusual and mostly unproven — no public deployment of it exists.

**Local RAG.** Retrieval over `.txt` and `.md` files using an ONNX all-MiniLM-L6-v2 embedder, so your knowledge base never leaves the machine.

**Sandboxed `code_exec`.** Code execution in a subprocess sandbox, which is the highest-risk surface in the whole crate and the one most worth reading before enabling.

**Proactive `--watch` triggers.** File, process, and timer watchers that let the agent speak first. Combined with the JSON memory store and hold music during tool calls, the feature list reads like a product roadmap — which is precisely the concern. Shipping breadth this wide in 22 releases over six days means most of these paths have never been exercised outside the author's machine.

## How Does Skadoosh Compare to Pipecat, LiveKit, and the Rest?

| Framework | Language | Local-first? | Transport | Barge-in primitive | Ecosystem signal |
|---|---|---|---|---|---|
| **Skadoosh** | Rust | Yes — fully local by default | None (device audio) | Atomic epoch flush in the audio callback | Repo 404s; 389 downloads; 0 reverse deps |
| **Pipecat** | Python | No — hosted models assumed | Bring your own | Handled in the pipeline, not the audio layer | 16,100 stars, BSD-2-Clause, actively pushed |
| **LiveKit Agents** | Python | No — hosted inference | WebRTC/SIP built in | Session-level interruption | 14,434 stars, Apache-2.0, ~500-650 ms P95 |
| **HF speech-to-speech** | Python | Yes, with heavy hardware | OpenAI Realtime protocol | Realtime event semantics | 13,359 stars, production on Reachy Mini robots |
| **Moshi** | Python | Yes, GPU-class | Custom full-duplex | Two parallel audio streams | ~160 ms glass-to-glass, 7B backbone |
| **pipecrab** | Rust | Yes | None | Interrupt frame overtakes queued work | ~19 stars; Linux/Windows unverified |
| **Vox** | Rust | Yes | HTTP + WebSocket | "Live Talk" | ~46 stars; Whisper/Sherpa + multi-backend TTS |
| **EchoKit** | Rust | Yes | ESP32 hardware client | Device-level | ~592 stars; appliance, not a library |

The pattern is clear once you lay it out. Frameworks with large ecosystems (Pipecat, LiveKit, speech-to-speech) are Python and assume hosted inference by default; the Rust projects that are genuinely local-first are small, young, and largely unproven. Skadoosh sits at the far end of both axes — maximum local-first purity, minimum ecosystem validation.

Fora Soft's July 2026 vendor-neutral comparison lands a point that applies to all of them: the framework barely moves latency, because "your model choice sets the number." Speech-to-speech architectures land near 300 ms while an STT+LLM+TTS cascade runs 300-800 ms. Skadoosh is a cascade, so it inherits the cascade's floor.

## The Latency Reality Check: Where Does "Lightning-Fast" Hold Up?

Human conversational turn-taking averages about 200 ms across ten languages ([Stivers et al., PNAS 2009](https://genalphai.com/voice-agent-latency-designing-beyond-the-800ms-wall)), which is why the industry treats sub-800 ms as acceptable and over 1000 ms as broken. The 2026 budget looks like this: VAD/endpointing under 30 ms, streaming ASR first partial under 200 ms, LLM time-to-first-token 300-400 ms, TTS first byte 150-200 ms, barge-in stop under 200 ms, and end-to-end time-to-first-audio under 800 ms at P95.

Run Skadoosh's stages against that budget on CPU:

| Stage | Indicative cost | Source / status |
|---|---|---|
| Silero VAD | < 1 ms per 30+ ms chunk | Silero README (third-party) |
| Silence gate | ~300 ms (by design) | Skadoosh default |
| whisper-rs STT | 50-150 ms (indicative) | Third-party CPU benchmark, different hardware |
| LLM TTFT | 200-350 ms | Qwen2.5-1.5B on CPU via Ollama (third-party) |
| LLM generation | 4-8 tokens/s | Same benchmark; dominates long replies |
| Kokoro TTS first audio | 40-75 ms CPU / ~80-120 ms M3 Pro | Third-party benchmarks |
| Kokoro RTF (4 vCPU) | 0.57 mean (1.8x real time) | ONNX Runtime benchmark |
| Kokoro RTF (2 ARM cores) | 0.87-0.93x — **slower than real time** | ARM benchmark |

The verdict is hardware-dependent, and this is the single most important caveat in any Skadoosh review. On a four-core x86 machine the TTS stage keeps ahead of playback and the pipeline can plausibly land near the 800 ms bar. On two ARM cores — the Raspberry Pi and small-laptop class that "local voice agent" most naturally suggests — Kokoro drops below 1x real time, meaning the agent cannot speak as fast as it generates, and clauses queue up behind a synthesizer that is permanently behind schedule. Sentence splitting costs Kokoro about 8% throughput on that hardware, while Piper holds 8.2x on the same machine ([tts-cpu-benchmark](https://github.com/obole-ia/tts-cpu-benchmark)).

And the model is small. Qwen2.5-1.5B at 4-8 tokens per second is fine for commands, retrieval-grounded answers, and short tool calls. It is not a frontier model, and no amount of pipeline engineering makes it one. "Lightning-fast" describes the pipeline's latency, not its intelligence.

## What Does Zero Per-Minute Cost Actually Buy?

Fully local inference costs $0 per minute once deployed, against roughly $0.10-$2.00 per minute for a cloud voice agent including STT, LLM, TTS, and telephony ([buildmvpfast](https://buildmvpfast.com/blog/voice-ai-architecture-hybrid-on-device-2026)). A single voice-agent phone call runs $0.30-$0.50, and managed framework hosting sits near $0.01/min while the models themselves run about $0.04/min.

The market context explains why this niche exists at all: conversational AI was $11.58B in 2024 and is projected to reach $41.39B by 2030 at a 23.7% CAGR, with the voice-agent segment growing at 34.8%.

But cost is the weaker half of the local-first argument. The stronger half is regulatory. Voiceprints became a high-risk category under the EU AI Act in August 2025, and GDPR, CPRA, and HIPAA all impose constraints that are trivially satisfied by an architecture where audio never leaves the machine. For a healthcare triage bot or an HR intake agent, "no cloud, no API keys, no data leaving the device" is an architectural requirement rather than a cost optimization — and it is the one claim about Skadoosh that its 404'd repository cannot undermine, because you can audit the crate tarball directly.

## The Honest Concerns: The GitHub Repository Is a 404

This is the part a review has to lead with for anyone considering Skadoosh in production.

The declared repository, `github.com/Hot-Coco/Skadoosh`, returns HTTP 404 — verified by raw HTTP, by the GitHub API, and with an authenticated `gh` CLI token on 2026-10-01. The GitHub account or organization `Hot-Coco` does not exist either, and no Wayback Machine snapshot was ever captured. That means stars, forks, issues, CI status, and the CI badge printed in the README are all unverifiable.

The identities are contradictory. crates.io lists the owner as **TheLimeDev** (a GitHub account created 2025-04-16 with 3 public repos and 11 followers), while docs.rs attributes the crate to **Hot-Coco**. Two different identities on the same package is a supply-chain smell, not a crime, but it means there is no accountable party with a public track record.

The default model's own card is more damning. StealthyLM-Emotive was fine-tuned by the same author, and the README points at `huggingface.co/StealthyML/StealthyLM-Emotive`, which now redirects to `Monster-Code/StealthyLM-Emotive` — 278 downloads, 1 like. Its model card opens with "Skadoosh unfortunately has been deprecated" ([HF API](https://huggingface.co/api/models/Monster-Code/StealthyLM-Emotive)). The project's own author has said, in the one public artifact that survives, that the project is over.

Adoption numbers confirm the stakes. The crate first appeared 2026-08-19 and shipped roughly 22-23 releases (0.1.0 through 0.12.1) in under a week, accumulating **389 lifetime downloads** with per-version counts between 14 and 23. **Zero reverse dependencies.** There is no Hacker News discussion — Algolia returns zero hits for "skadoosh voice" and for `"local voice agent" rust`. No third party has published a benchmark, an issue, or a deployment.

Put together: ~22 releases in six days is churn, not maturity, and 389 downloads with zero dependents means nothing in the ecosystem has validated that any of it works outside the author's machine. Vocode provides the cautionary precedent — a well-starred voice-agent framework (3,797 stars, MIT) whose last push was 2024-11-15. Star counts do not imply maintenance, and the absence of a repository removes even that signal.

### Can You Audit a Crate With No Repository?

Yes, and you should. `cargo download skadoosh --version 0.12.1`, or fetch `static.crates.io/crates/skadoosh/skadoosh-0.12.1.crate` directly and unpack it. The tarball is the artifact cargo actually builds, so it is the authoritative source regardless of what any repository claims. What you will find is a well-documented, unsafe-free, heavily tested Rust codebase. What you will not find is a human to file a bug against — which is the whole problem.

## Security, Licensing, and Supply-Chain Review

The licence stack is mostly clean and worth enumerating, because it is one of the crate's genuine strengths:

| Component | Licence | Note |
|---|---|---|
| Skadoosh crate | MIT OR Apache-2.0 | Dual-licensed, standard Rust practice |
| Silero VAD | MIT | Third-party, upstream healthy |
| whisper-rs / whisper.cpp | MIT | 1.37M downloads |
| Kokoro-82M | Apache-2.0 | 11.5M HF downloads, 7,074 likes |
| StealthyLM-Emotive weights | Third-party model | 278 downloads; card says deprecated |
| espeak-ng (runtime dep) | **GPL** | Needs review for closed-source products |

The espeak-ng dependency is the one that will bite a commercial integrator: GPL phonemisation shipped as a runtime requirement for TTS can impose obligations your legal team needs to see before, not after, you ship.

On the security side, `#![forbid(unsafe_code)]` and rustls everywhere (no OpenSSL) are meaningful reductions in the classic C-dependency attack surface, and the WASM sandbox is genuinely restrictive when configured with fuel limits and no host bindings. The un-sandboxed-ish surfaces to scrutinize are `code_exec` (subprocess) and the mesh's UDP discovery, neither of which has any published threat model.

## Who Should Use Skadoosh in 2026?

**Use it if** you need a working reference implementation of a fully local Rust voice pipeline, you are comfortable compiling from crates.io and auditing a tarball, your hardware is four-plus x86 cores, and your tasks are short and tool-shaped rather than knowledge-heavy. It is an excellent teaching artifact — the barge-in epoch pattern and the trait-object stage model are worth reading even if you never run the binary.

**Fork it if** you want the local-first architecture but need a maintained dependency. The entire crate is 22,255 lines of MIT/Apache-2.0 Rust with 188 tests and a permissive licence; vendoring it and taking ownership is a realistic option, and it is the path I would take for anything production-facing. While you are in there, swap the whole-utterance whisper stage for streaming ASR, which is the single highest-leverage improvement available.

**Avoid it if** you need a supported dependency, an SLA, a security response process, a bug tracker, telephony, or a model that can reason about a domain. For those, LiveKit Agents gives you WebRTC, scaling, and a maintained stack; Hugging Face speech-to-speech gives you a local pipeline with a real community; Pipecat gives you the largest integration library in the field. None of them give you $0/min and a fully local default, which is exactly the trade you are making.

## Verdict

Skadoosh is the most complete all-local Rust voice agent framework on crates.io and one of the least trustworthy dependencies you could add to a project. The pipeline is well designed, the barge-in mechanism is genuinely correct, the feature breadth (WASM tool sandbox, mesh, RAG, watchers) has no direct equivalent in any competitor, and the licence stack is permissive. Against that: a 404'd repository, two conflicting author identities, a default model whose own card announces deprecation, 389 downloads, zero reverse dependencies, no benchmarks, and a TTS stage that falls below real time on the hardware class most people imagine when they hear "local voice agent."

Read it. Build it. Measure it with the `StageLatency` events it ships. But treat it as a source of architectural ideas and a fork candidate, not as a library you depend on.

## FAQ

### Does Skadoosh need a GPU?

No — the default path is CPU-only. The bundled LLM is a 4-bit Qwen2.5-1.5B GGUF running through Ollama, and Kokoro-82M with `ort` runs on CPU. That said, GPU acceleration matters for the user experience: Kokoro reaches roughly RTF 0.03 on GPU (a 10-second clip in about 0.3 seconds) versus 0.57 on four x86 cores and below 1x on two ARM cores. CUDA, CoreML, DirectML, and ROCm features exist, but on a two-core ARM machine text-to-speech will not keep up with playback.

### Which languages does it support?

The crate is language-agnostic, but every default is English-first: whisper `tiny.en` for recognition and Kokoro's `af` voice for synthesis. Changing recognition language means supplying a different Whisper model file, and changing synthesis language means a Kokoro voice key plus working phonemisation through misaki-rs. There is no built-in multilingual routing, and nothing in the project addresses non-English latency.

### Does it run on a Raspberry Pi or ARM?

It builds and runs, but the TTS stage is the limiting factor. On two Neoverse-N1 ARM cores Kokoro-82M measures 0.87-0.93x real time — slower than it speaks — while Piper holds 8.2x on the same machine. If you are targeting Pi-class hardware, swapping the synthesizer is mandatory rather than optional. Silero VAD and Whisper `tiny.en` are both comfortable on that class of hardware.

### Can I point it at a hosted LLM instead of Ollama?

Yes. The LLM stage is the `LlmBackend` trait, backed by a streaming OpenAI-compatible chat client, so any compatible endpoint works. Be aware of what that changes: routing the LLM to a hosted provider removes the "no data leaves the machine" guarantee that is the main compliance argument for using Skadoosh, since the transcript and the model's reply leave your network even though the audio does not.

### Is Skadoosh maintained?

Its own documentation says it was deprecated. The declared GitHub repository returns HTTP 404, the author's model card states the project "has been deprecated," and the crate shows 389 lifetime downloads with zero reverse dependencies and no issue tracker. Version 0.12.1, published 2026-08-23, is the last release. Treat the crate tarball as the final state of the project, not as an actively evolving library.
