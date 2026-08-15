---
title: "How to Build a Conversational AI Game: A Voice-Driven Murder Mystery"
date: 2026-08-15T01:02:31+00:00
tags:
  - conversational ai game
  - ai murder mystery game
  - voice ai game development
  - llm interactive fiction
  - talk to ai npcs
description: "Build a conversational AI game with the speech-to-text → LLM → text-to-speech pipeline. Here's how to create a voice-driven murder mystery players love."
draft: false
cover:
  image: "/images/voice-driven-ai-game-interview-2026.png"
  alt: "How to Build a Conversational AI Game: A Voice-Driven Murder Mystery"
  relative: false
schema: "schema-voice-driven-ai-game-interview-2026"
---

A conversational AI game is a game you play by talking to intelligent characters instead of pushing buttons. The core architecture is a speech-to-text → LLM → text-to-speech pipeline: the player speaks, the game transcribes their words, an LLM decides how the character responds, and text-to-speech speaks that response back aloud. This is the same loop used by Shadowlight, a voice-driven murder mystery played inside Minecraft that earned 24 points on Hacker News, and by Mantella, a Skyrim and Fallout 4 mod with roughly 400 GitHub stars. If you want to build one, this guide walks through the reference architecture, tool choices, and the UX pitfalls that separate a forgettable voice game from one players emotionally attach to.

## What Makes a Murder Mystery the Perfect Format for Conversational AI

Murder mysteries are uniquely suited to conversational AI because the entire gameplay loop is already conversation. A traditional mystery is about interrogating suspects, collecting conflicting testimony, and reasoning toward who is lying. That is exactly the interaction an LLM handles well: you ask a question, the character answers, and the tension lives in what they do not say. There is no twitch reflex, no physics engine, no complex state machine required — the "game" is dialogue state.

The community reception makes this concrete. Shadowlight's top Hacker News feedback was not about graphics or mechanics but emotional attachment: one commenter wrote that "it is so easy to grow attached to the NPCs when you can talk to them." A text-only mystery can still work, as SolveTheMurders.com shows with its procedurally generated cases and suspects. But voice adds an intimacy that typing cannot reproduce. Hearing a suspect hesitate, stumble, or sound evasive turns a puzzle into a relationship.

There is also a demonstrated market signal. The Conversational Game Theory project drew 121 points on Hacker News, and an article on automating interactive fiction logic generation with LLMs drew 100 points — both confirming that developers are actively exploring LLMs as story-logic engines. A murder mystery gives you a contained story where the LLM's strengths (dialogue, personality, deception) are central and its weaknesses (long-range planning, spatial reasoning) are largely irrelevant.

## The Reference Architecture — Speech-to-Text → LLM → Text-to-Speech

Every voice-driven conversational AI game shares the same five-stage loop. Understanding these stages is the foundation of voice AI game development.

| Stage | Role | Typical tools | Latency budget |
|-------|------|---------------|----------------|
| Speech-to-Text (ASR) | Convert the player's spoken words to text | Whisper, Deepgram, Google STT, Vosk | 200–500 ms |
| Dialogue state | Track who said what and what the player knows | Custom state machine or agent framework | n/a (logic) |
| LLM reasoning | Decide the character's response, personality, and secrets | GPT-4o, Claude, Llama 3, DeepSeek | 500–2,000 ms |
| Text-to-Speech (TTS) | Speak the response back with the character's voice | ElevenLabs, OpenAI TTS, Piper, Coqui | 200–400 ms |
| Turn-taking / orchestration | Manage interruptions, silence, and barge-in | Custom voice agent layer | n/a |

The pipeline itself is simple: the player speaks, ASR transcribes, the LLM generates a reply constrained by the character's memory and secrets, TTS voices it, and the loop repeats. Mantella is the cleanest proof this is the de-facto standard — its entire premise is the STT → LLM → TTS loop applied to Skyrim and Fallout 4 NPCs, and it runs fully local. For a murder mystery, you add one extra stage: you must keep the culprit's identity secret inside the LLM's context, which we cover later.

The total round-trip latency matters enormously. The best-case pipeline sums to roughly 1 to 3 seconds, which is already at the edge of what feels natural. If you add a slow ASR provider and a large LLM, your "conversation" becomes a stilted series of pauses, and players lose the immersion that makes the genre work.

## Building the Voice Agent Loop: ASR, Dialogue State, and Turn-Taking

The hard part of a conversational AI game is not the LLM — it is orchestrating a natural spoken exchange. You need three subsystems working together.

**Automatic Speech Recognition (ASR).** The player's audio must become text with low latency and good accuracy in the player's accent and language. Whisper is a popular open choice; hosted options like Deepgram or Google Speech-to-Text trade cost for reduced setup. For a murder mystery, accuracy on names and evidence matters — a player saying "the butler's ledger" needs to be transcribed correctly, or the reasoning chain breaks.

**Dialogue state.** The game must remember who the player has interrogated, which clues they hold, and what each suspect has claimed. This is the difference between an LLM that is "just chat" and a game with real progression. In a simple implementation, the dialogue state is a JSON object passed into every LLM call; in a more advanced one, it is the persistent memory of an agent framework. The key rule: the state, not the model, owns the mystery's truth.

**Turn-taking.** Real conversation has interruptions, pauses, and barge-in — a player should be able to cut a suspect off mid-sentence. This is the least solved part of the loop. Krisp's article on improving turn-taking for AI voice agents, which drew 113 Hacker News points, makes the case that background-voice cancellation and robust endpointing are the key differentiators in voice UX. If your game cannot tell the difference between a player interrupting and background noise, the experience falls apart. Budget real engineering time here — it is the difference between "impressive demo" and "game people finish."

## Choosing Your Tools: Open-Source Agent Frameworks vs. Wiring LLMs from Scratch

You have two paths for the conversational logic: build on an existing open-source generative-AI agent framework, or wire the STT → LLM → TTS pipeline yourself.

| Factor | Open-source agent framework | Wiring LLMs from scratch |
|--------|----------------------------|--------------------------|
| Time to first playable | Fast — framework handles memory, state, tooling | Slow — you build everything |
| Control | Constrained by framework abstractions | Total |
| Maintainability | Framework updates come with risks | Your code, your rules |
| Example | Gron Games (43 HN points) | Mantella's custom Skyrim integration |
| Best for | Indie devs prototyping quickly | Teams with specific, unusual requirements |

Gron Games, a murder mystery built on an open-source generative-AI agent framework, reached 43 points on Hacker News — evidence that indie developers want a template for AI-driven game logic rather than reimplementing the wiring. A framework gives you memory management, multi-turn conversation handling, and often a built-in voice layer, which collapses the hardest engineering problems into configuration.

The from-scratch path is worth it only when your requirements are genuinely unusual. Mantella could not rely on a general framework because it had to integrate tightly with Skyrim's and Fallout 4's internal quest and dialogue systems, plus run fully local. For a standalone web murder mystery, an agent framework will get you to a playable build dramatically faster. My recommendation: prototype on a framework first, and only drop down to hand-wiring once you hit a specific limitation.

## Designing NPCs Players Actually Bond With (the Emotional Hook)

The single biggest lesson from the voice-game community is that emotional attachment to NPCs is the standout hook. When you talk to an NPC by voice, the brain treats the exchange as a real interaction — which is why the emotional stakes are so much higher than typing. Here is how to design suspects players actually bond with.

**Give every NPC a clear voice and a tell.** A suspect who answers in short, clipped sentences and changes topic when asked about the murder reads as nervous. One who jokes inappropriately reads as either innocent bravado or a liar. The LLM needs a persona prompt that defines vocabulary, emotional range, and verbal habits — not just backstory.

**Make memory consistent.** Players notice when an NPC contradicts themselves across a conversation. The NPC must remember earlier answers within a session, so their story stays coherent as the player interrogates them. This is where per-NPC memory state matters: each suspect gets their own conversation history, not a shared blob.

**Allow emotional progression.** The best feedback from Shadowlight players was getting attached to NPCs — which implies the NPCs changed toward the player. A suspect who starts hostile but warms up if the player is empathetic creates a bond. Design personality states that shift based on how the player treats the character.

**Keep the voice consistent.** A single TTS voice per character, ideally a distinctive one, is non-negotiable. If ElevenLabs or another provider can clone a unique voice per suspect, use it — voice identity is a large part of why players grow attached.

## Keeping the Culprit Secret — Story Coherence and Per-NPC Memory

The hardest technical challenge in an LLM murder mystery is preventing the model from leaking the culprit. LLMs want to be helpful, and a direct question like "did you kill him?" can produce a confession even from the innocent character. You need deliberate prompt-engineering techniques.

**Isolate each NPC's knowledge.** Each suspect's context should contain only what they legitimately know, plus the shared "public" facts of the case. The culprit's prompt contains their secret; the innocent suspects' prompts contain an alibi they genuinely believe. Do not feed the full solution to every NPC. This is the per-NPC memory pattern: separate context per character, as the Whodunit LLM murder-mystery experiments demonstrate.

**Use system-level rules over instruction-level pleading.** A soft instruction like "do not reveal you are the killer" is unreliable. Stronger approaches include: (1) hard-coded refusal logic that routes certain questions away from the LLM, (2) instructing the innocent NPCs that they are *genuinely innocent* so no internal conflict tempts a confession, and (3) post-processing the LLM output to strip any line that leaks the secret before it reaches TTS.

**Constrain the answer space.** Instead of free generation, ask the LLM to select a reply from a set of templated options informed by dialogue state, then elaborate. This keeps the story on the rails and dramatically reduces the chance of spoilers. The tradeoff is less organic dialogue — so use a hybrid: constrained choices for dangerous questions, free generation for safe ones.

**Test for leaks relentlessly.** Build a QA script that asks every suspect "did you do it?" a hundred times and flags any confession. This is not optional; a single leaked culprit destroys the game.

## Local vs. Cloud Voice Models: Latency, Privacy, and Cost

A core decision is where your ASR, LLM, and TTS run. Mantella demonstrates the fully local approach for privacy and cost reasons; hosted APIs like OpenAI, Anthropic, ElevenLabs, and Deepgram trade those away for quality and zero infrastructure.

| Factor | Local models | Cloud APIs |
|--------|--------------|------------|
| Latency | Variable; fast on good GPUs, slow otherwise | Predictable, but network-bound |
| Privacy | Fully offline — nothing leaves the machine | Player audio and text leave the machine |
| Cost | Fixed hardware cost | Pay per token / per second |
| Quality | Good, improving fast (Llama, Whisper, Piper) | Usually best-in-class |
| Best for | Privacy-sensitive, offline, or cost-constrained | Polished consumer products |

For a murder mystery, the deciding factors are latency and privacy. Voice interaction is unforgiving of latency — a 4-second pause breaks immersion — so you need your slowest stage (the LLM) to be fast. Cloud APIs deliver the best models with predictable performance but add network round-trips and a per-player cost that scales with playtime. Local models keep everything private and cheap per player but require you to own sufficient GPU hardware and accept a possible quality gap.

A pragmatic hybrid is common: run the heavy LLM locally if you have the hardware, and use cloud TTS only for distinctive character voices. Whatever you choose, measure your end-to-end latency on real hardware before committing, because the "voice feel" depends on it.

## Handling Interruptions and Background Noise (the UX Differentiator)

If there is one unsolved problem that separates great voice games from demos, it is turn-taking. Players will interrupt suspects, mumble, have kids shouting in the background, and stop mid-sentence. A robust conversational AI game must handle all of it.

**Barge-in.** The player should be able to interrupt the TTS output and their new question takes priority. This requires the ASR to keep listening while TTS is speaking, plus logic to stop playback the moment speech is detected. Implement this with a hot-word or energy-based barge-in detector rather than waiting for the LLM round-trip.

**Endpointing.** Your game must decide when the player has *finished* speaking so it can start the LLM. Too aggressive and you cut them off; too lenient and every pause adds a dead second. This is where background-voice cancellation (the subject of Krisp's 113-point Hacker News article) matters — the system must distinguish "player is done" from "background noise just stopped."

**Noise robustness.** ASR accuracy drops in noisy environments. Test your pipeline with real-world audio, not clean mic recordings. Consider noise suppression before ASR, and design gameplay so that a misheard word (a "butler's ledger" becoming "butler's leg") degrades gracefully rather than breaking the case.

**Timeouts and recovery.** If the player says nothing, or the ASR returns garbage, the NPC should prompt naturally ("Go on...", "Well?"). Never let dead air sit — silence is the fastest immersion killer in a voice game.

## Embedding in a Sandbox World vs. Standalone Web Game — Distribution Tradeoffs

Finally, decide where your conversational AI game lives. Shadowlight embedded its murder mystery inside Minecraft, while SolveTheMurders and Gron run as web games. Each approach changes your reach, technical constraints, and distribution.

| Factor | Embedded in a sandbox (Minecraft) | Standalone web game |
|--------|-----------------------------------|---------------------|
| Distribution | Rides an existing player base | Must drive your own traffic |
| World fidelity | Reuse the sandbox's visuals and physics | Build your own (or go text-only) |
| Technical friction | Modding/plugin constraints | Full control over stack |
| Example | Shadowlight (24 HN points) | Gron, SolveTheMurders |

Embedding gives you instant visual worldbuilding and a built-in audience — Minecraft already has millions of players, so a murder mystery inside it reaches people who would never install a standalone mystery app. The cost is that you are constrained by the host's plugin APIs and must make your voice loop coexist with the host game's own systems.

A standalone web game gives you total control over the stack, the ability to ship to any device with a browser, and easier instrumentation of player behavior for playtesting. The cost is that you must build or acquire the visual world, and you bear the full burden of distribution. For a first conversational AI game, starting text-first on the web and adding voice later is the lower-risk path; embedding in a beloved sandbox is the higher-reach one.

## Testing Your Game: Playtesting, Latency Budgets, and Iterating on Player Frustration

A conversational AI game fails or succeeds in playtesting, because the "feel" of a voice conversation is hard to predict from code. Build a testing loop early.

**Set a hard latency budget.** Define your acceptable end-to-end round-trip (a good target is under 2 seconds, ideally under 1.5). Profile each stage — ASR, LLM, TTS — and optimize the slowest one first. A slow pipeline will dominate every other design decision, so measure before you polish.

**Watch for the three frustration killers.** The first is latency (every pause feels like a loading screen). The second is mishearing (players get annoyed when their words are mangled). The third is spoilers (a single leaked culprit makes the whole game pointless). Test all three explicitly and repeatedly.

**Playtest with strangers, not friends.** Friends know your game's intent and forgive its rough edges. Strangers will reveal where the conversation breaks down, where NPCs contradict themselves, and where players get stuck. Run short, frequent tests with the cheapest possible build — even a text-prototype of the dialogue logic — before investing in full voice production.

**Instrument everything.** Log every turn, every ASR transcription, every LLM response, and every time the player interrupts. This data tells you where players get frustrated far more reliably than anecdote. Iterate on the dialogue-state design and prompts based on real usage, not intuition.

## Frequently Asked Questions

**What is a conversational AI game?**
A conversational AI game is a game whose core interaction is talking to intelligent characters, powered by a speech-to-text → LLM → text-to-speech pipeline. Players speak to AI-driven NPCs instead of using menus or buttons, as in voice-driven murder mysteries like Shadowlight or Mantella.

**How do you build an AI murder mystery game?**
You build a voice loop: transcribe the player's speech with ASR, maintain a dialogue state that tracks clues and suspicions, generate each suspect's response with an LLM (giving each character its own memory and secrets), and speak the reply with TTS. Tools like Whisper, an LLM such as Llama or GPT-4o, and a TTS provider cover the pipeline.

**How do you stop an AI NPC from revealing the culprit?**
Keep each suspect's context limited to what they legitimately know, give innocent characters alibis they genuinely believe, constrain dangerous answers to pre-approved templates, and post-process LLM output to strip any spoiler. Then QA-test by asking every suspect "did you do it?" repeatedly.

**Can I build a conversational AI game locally?**
Yes. Mantella demonstrates a fully local STT → LLM → TTS pipeline for Skyrim and Fallout 4 using local models. The tradeoff is that you need sufficient GPU hardware and accept a potential quality gap versus hosted APIs, in exchange for privacy and no per-player token cost.

**What is the hardest part of voice AI game development?**
Turn-taking — handling interruptions, barge-in, endpointing, and background noise. Real conversation is messy, and a system that cannot distinguish a player interrupting from background noise breaks immersion. This unsolved UX problem is the biggest differentiator between a polished voice game and a demo.
