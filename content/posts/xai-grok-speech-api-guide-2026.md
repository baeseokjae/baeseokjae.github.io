---
title: "xAI Grok speech API STT TTS Guide for Developers in 2026"
date: 2026-06-15T19:04:14+00:00
tags: ["xai", "speech-api", "developer-tools"]
description: "Developer guide to xAI Grok speech API STT and TTS endpoints, pricing, streaming, code examples, and production patterns."
draft: false
cover:
  image: "/images/xai-grok-speech-api-guide-2026.png"
  alt: "xAI Grok speech API STT TTS Guide for Developers in 2026"
  relative: false
schema: "schema-xai-grok-speech-api-guide-2026"
---

The xAI Grok speech API gives developers separate STT and TTS endpoints for transcription, live captions, generated speech, and voice workflows. Use STT when audio becomes text, TTS when text becomes audio, and the Voice Agent API only when the product needs full two-way spoken conversation.

## What Is the xAI Grok Speech API in 2026?

The xAI Grok speech API is a set of production voice endpoints for speech-to-text, text-to-speech, and conversational voice applications under the Grok developer platform. xAI announced standalone Grok STT and TTS APIs on April 17, 2026, with STT general availability listed on April 15, 2026 and TTS general availability listed on March 16, 2026. For developers, the practical split matters more than the launch timeline: `/v1/stt` transcribes uploaded or streamed audio, `/v1/tts` generates audio from text, and the Voice Agent API handles full duplex speech workflows. The speech APIs target common app surfaces such as call analytics, meeting notes, accessibility captions, IVR prompts, podcast production, and voice agents. The core takeaway is simple: treat Grok speech as composable audio infrastructure, not as one monolithic voice product.

### Why does this matter for application teams?

The API split gives teams control over latency, cost, and failure handling. A compliance transcription job can run through batch STT without any TTS dependency. A read-aloud feature can use TTS without storing microphone audio. A support bot can chain STT, an LLM, and TTS when the conversation logic belongs in your app server.

## STT vs TTS vs Voice Agent API: Which Endpoint Should You Use?

STT, TTS, and Voice Agent API refer to three different voice architecture choices: STT converts audio to text, TTS converts text to audio, and Voice Agent API manages a complete spoken conversation loop. In xAI's 2026 docs, Grok STT pricing is listed at $0.10 per hour for REST batch transcription and $0.20 per hour for streaming, while Grok TTS pricing is listed at $15.00 per 1 million characters. That separate metering is useful because many products need only one side of the voice pipeline. Use STT for uploaded interviews, call recordings, live captions, and diarized meeting notes. Use TTS for generated narration, IVR responses, app accessibility, and spoken summaries. Use Voice Agent API only when interruption handling, turn taking, and two-way speech are the product. The takeaway: choose the smallest voice primitive that solves the workflow.

| Need | Best xAI API | Why |
|---|---:|---|
| Upload a recorded call and get text | Grok STT REST | Lowest complexity and batch pricing |
| Show live captions while someone speaks | Grok STT WebSocket | Interim results and lower latency |
| Generate a spoken onboarding message | Grok TTS REST | Simple request-response audio generation |
| Stream generated audio into a call | Grok TTS WebSocket | Faster playback start and telephony fit |
| Build a two-way voice assistant | Voice Agent API | Handles conversational audio loop |

### When should you avoid Voice Agent API?

Voice Agent API is the wrong default when your product already owns the conversation state. If you need deterministic routing, strict audit logs, or custom moderation around every LLM turn, a cascaded STT to LLM to TTS pipeline is easier to inspect. Voice Agent API makes sense when live spoken interaction is the main interface.

## Grok Speech to Text API: Endpoints, Pricing, Limits, and Features

Grok Speech to Text API is xAI's transcription service for uploaded files and realtime audio streams through REST and WebSocket interfaces. The public model docs list STT pricing at $0.10 per hour for REST and $0.20 per hour for streaming, with rate limits of 600 requests per minute, 10 requests per second, and 100 concurrent streaming sessions per team. The implementation guide says file uploads can be up to 500 MB, which is enough for many podcasts, meetings, and support-call batches without pre-splitting. Feature-wise, Grok STT supports multiple audio formats, multiple languages, keyterm prompting, word-level timestamps, diarization, multichannel audio, interim streaming results, inverse text normalization, and Smart Turn end-of-turn detection. In practice, those features matter most for business audio where names, numbers, speakers, and channels carry meaning. The takeaway: Grok STT is built for structured transcription workloads, not just plain captions.

### What does the REST upload look like?

REST upload works by sending multipart form data to `https://api.x.ai/v1/stt` with the audio file and transcription options. In production, keep this call on a trusted server because API keys should not be exposed in a browser or mobile client. Store the transcript, timestamps, and diarization metadata separately so downstream search and QA systems can use them.

## Grok Text to Speech API: Voices, Speech Tags, Output Formats, and Pricing

Grok Text to Speech API is xAI's audio generation service for converting text into spoken output through REST or streaming interfaces. The current model docs list TTS pricing at $15.00 per 1 million characters, and the implementation guide lists five built-in voices: `eve`, `ara`, `rex`, `sal`, and `leo`. REST TTS input is limited to 15,000 characters per request, so long-form narration should be chunked by paragraph or section instead of by arbitrary character count. The API supports MP3, WAV, PCM, mu-law, and A-law output formats; MP3 is the general app default, while mu-law and A-law are useful for telephony systems. xAI also lists speech tags, speed controls, timestamp output, and custom voices, with custom voice support appearing in release notes on May 1, 2026. The takeaway: Grok TTS is strongest when expressive delivery and deployable audio formats both matter.

| Voice | Practical use | Notes |
|---|---|---|
| `eve` | Product demos and warm narration | Good default for consumer-facing clips |
| `ara` | Support and assistant flows | Useful when clarity matters more than drama |
| `rex` | Business and executive reads | Suits formal product or sales content |
| `sal` | Balanced narration | Works for neutral summaries |
| `leo` | Instructional content | Good fit for tutorials and explainers |

### How should you choose an output format?

Output format should follow the playback environment. Use MP3 for web apps, mobile playback, and cached narration. Use WAV or PCM when you need post-processing, precise waveform handling, or media pipeline compatibility. Use mu-law or A-law for phone networks where narrowband codecs are already expected.

## Quickstart: Transcribe an Audio File with Grok STT

Transcribing an audio file with Grok STT works by posting multipart form data to the STT endpoint with an audio file and optional hints such as language, keyterms, diarization, and output format. A practical first test is a 30 to 90 second WAV or MP3 file because it gives you enough speech to inspect timestamps, punctuation, speaker labels, and number formatting without waiting on a large upload. The implementation guide supports uploaded files and URL-based transcription, but I prefer local upload for the first integration because it removes fetch permissions, expiring URLs, and storage ACLs from the debugging path. After the first transcript succeeds, add language hints, domain keyterms, and diarization only when your evaluation data proves they help. The takeaway: start with a small controlled file, then add transcription options one at a time.

```bash
curl https://api.x.ai/v1/stt \
  -H "Authorization: Bearer $XAI_API_KEY" \
  -F "file=@support-call.mp3" \
  -F "language=en" \
  -F "diarize=true" \
  -F "format=json"
```

### What should you log from the first response?

The first response should be logged as structured data, not just printed as plain text. Capture request ID, duration, file size, language, transcript text, speaker segments, word timestamps, and any warning fields. Those logs make accuracy reviews and support tickets much easier when a customer reports a bad transcript.

## Quickstart: Generate Speech with Grok TTS

Generating speech with Grok TTS works by sending text, a voice, and an output format to the TTS endpoint, then saving or streaming the returned audio bytes. The REST input limit is 15,000 characters per request, so a realistic developer quickstart should test one short UI phrase, one paragraph, and one longer multi-paragraph sample before wiring TTS into production. That catches pronunciation, pacing, and chunk boundary problems early. For a web app, generate MP3 first because it is simple to store, cache, and play in standard browsers. For contact-center work, test mu-law or A-law before the first demo because telephony audio that sounds fine as MP3 can degrade after transcoding. The takeaway: validate voice, format, and chunking together because TTS quality is a pipeline property.

```bash
curl https://api.x.ai/v1/tts \
  -H "Authorization: Bearer $XAI_API_KEY" \
  -H "Content-Type: application/json" \
  --output welcome.mp3 \
  -d '{
    "text": "Your deployment finished successfully. Three checks still need review.",
    "voice": "ara",
    "output_format": "mp3"
  }'
```

### How should you chunk long text?

Long text should be chunked on semantic boundaries such as headings, paragraphs, or dialogue turns. Avoid splitting in the middle of a sentence just because a character counter reached a limit. Keep a stable chunk ID and source range so regenerated audio can replace one bad segment without rebuilding the whole asset.

## Streaming Patterns: Live Captions, Realtime TTS, and Cascaded Voice Agents

Streaming with the Grok speech API refers to using WebSocket connections so audio or generated speech can flow before a full request is complete. xAI's STT docs describe low-latency WebSocket transcription with interim results, and the model docs list 100 concurrent streaming sessions per team for STT; TTS docs also describe streaming output with rate limits of 3,000 RPM, 50 RPS, and 100 concurrent sessions per team. In an app, streaming changes the engineering problem from "call an API" to "manage a session." You need reconnect behavior, backpressure, partial result rendering, and a clear definition of final versus interim text. For cascaded voice agents, the usual pattern is microphone audio to STT, transcript to an LLM, response text to TTS, and audio playback to the user. The takeaway: streaming improves perceived latency but requires explicit session engineering.

### What does a cascaded voice agent look like?

A cascaded voice agent is a pipeline where each stage is separately observable. The client streams microphone audio to your server, the server streams STT to xAI, final turns go to the reasoning model, and the answer goes through TTS. This architecture adds glue code, but it gives you policy checks, retries, and transcripts at every boundary.

## Production Checklist: API Keys, Retries, Rate Limits, Cost Tracking, and Audio Quality

A production Grok speech integration is a server-side audio pipeline with explicit controls for credentials, retries, rate limits, cost, storage, and audio quality. The published limits are high enough for serious applications, including 600 RPM for STT REST, 100 concurrent STT streaming sessions per team, and 100 concurrent TTS sessions per team, but those numbers still need local throttles so one tenant or batch job cannot starve everything else. Keep xAI API keys on the server, issue short-lived upload URLs to clients, and never proxy raw keys into browser JavaScript. Retries should be idempotent for file jobs and conservative for streaming sessions because retrying live audio can duplicate transcript segments. Track STT hours and TTS characters as separate cost meters. The takeaway: production quality comes from predictable boundaries around a capable API.

| Concern | Practical control |
|---|---|
| API keys | Server-side calls, secret manager, rotation schedule |
| Retries | Idempotency key for batch jobs, reconnect policy for streams |
| Rate limits | Per-tenant queues and circuit breakers |
| Cost | Separate meters for STT hours, streaming hours, and TTS characters |
| Audio quality | Normalize sample rate, channels, clipping, and silence trimming |

### Which audio preprocessing steps are worth doing?

Audio preprocessing should remove avoidable failure modes without destroying useful signal. Normalize volume, reject empty files, detect clipping, preserve separate call channels when available, and store the original file for audit. Do not over-compress speech before transcription unless your evaluation set proves it helps.

## Benchmarks and Accuracy: How Should You Interpret xAI's WER Claims?

xAI's Grok STT benchmark claims should be read as vendor-published accuracy signals, not as a substitute for your own evaluation. In the April 17, 2026 launch post, xAI reported an overall word error rate of 6.9% for Grok STT, compared with 9.0% for ElevenLabs, 11.0% for Deepgram, and 12.9% for AssemblyAI. The same benchmark listed Grok STT at 5.0% WER on phone call entities, 2.4% on video and podcasts, 10.9% on meetings, and 9.3% on telephone audio. Those are useful numbers because they break out domains instead of giving only one blended score. Still, your real error rate will depend on accents, microphones, background noise, jargon, language mix, channel separation, and expected formatting. The takeaway: use xAI's benchmark to shortlist, then run a domain-specific test set before committing.

### What should be in a speech evaluation set?

A useful evaluation set should include 50 to 200 representative clips before you make a vendor decision. Include clean audio, bad audio, heavy accents, crosstalk, names, product terms, numbers, and the formats your users actually upload. Score both raw words and business fields because one missed account number can matter more than ten harmless filler words.

## Grok Speech API Use Cases for Developers

Grok speech API use cases fall into three groups: transcription products, generated-audio products, and voice interaction systems. For transcription, the obvious examples are meeting notes, sales-call review, contact-center QA, podcast search, medical or legal intake drafts, and live captions. For generated audio, use cases include app read-aloud, course narration, personalized onboarding, status alerts, IVR prompts, game dialogue prototypes, and accessibility output. For interaction systems, a cascaded STT to LLM to TTS design can power support assistants, field-service copilots, interview practice tools, and workflow agents that speak through a phone or browser. The 2026 feature set is especially relevant for business audio because diarization, multichannel support, word timestamps, speech tags, and telephony codecs reduce the custom media plumbing teams used to write themselves. The takeaway: map the use case to the audio direction first, then pick the endpoint.

| Use case | Direction | Useful Grok feature |
|---|---|---|
| Sales-call QA | Audio to text | Diarization and multichannel transcription |
| Podcast search | Audio to text | Word-level timestamps |
| Read-aloud articles | Text to audio | Voices and MP3 output |
| IVR prompts | Text to audio | mu-law and A-law formats |
| Browser voice assistant | Both | STT streaming plus TTS streaming |

### Where does Grok fit in an existing stack?

Grok usually fits behind your application server, not directly in the client. The server owns authentication, upload policy, transcript storage, prompt construction, TTS caching, and billing attribution. That placement also lets you swap vendors later because the client talks to your voice abstraction rather than directly to xAI.

## Grok Speech API vs ElevenLabs, Deepgram, AssemblyAI, and OpenAI

Comparing Grok speech API with ElevenLabs, Deepgram, AssemblyAI, and OpenAI is mainly a question of workflow fit, not a universal winner. xAI's own April 2026 launch benchmark reports Grok STT at 6.9% overall WER against ElevenLabs at 9.0%, Deepgram at 11.0%, and AssemblyAI at 12.9%, but that is one published benchmark from the vendor launching the product. Deepgram and AssemblyAI have mature transcription ecosystems, ElevenLabs is widely associated with expressive voice generation, and OpenAI has broad multimodal and developer-platform reach. Grok's strongest pitch in 2026 is the combined STT and TTS package: low listed STT pricing, business-audio transcription features, five built-in TTS voices, speech tags, streaming, telephony codecs, and custom voices. The takeaway: shortlist Grok when you want both transcription and generated speech under one xAI account, then test against your exact audio.

| Provider | Strong fit | What to validate |
|---|---|---|
| xAI Grok | Combined STT/TTS workflows and business audio | Real WER, voice fit, regional needs |
| ElevenLabs | Expressive TTS-heavy products | STT accuracy and total cost |
| Deepgram | Realtime transcription stacks | Domain accuracy and pricing at scale |
| AssemblyAI | Transcription workflows and analysis | Latency and feature coverage |
| OpenAI | Multimodal app platforms | Voice latency, model choice, and ecosystem fit |

### How should you run a vendor bake-off?

A vendor bake-off should use the same files, prompts, output requirements, and scoring rules for every provider. Measure transcription error, entity accuracy, speaker handling, latency, developer effort, retry behavior, voice preference, and total cost. Run the test through your planned architecture, because direct dashboard demos hide integration friction.

## Common Pitfalls: Grok vs Groq, Stale Pricing, and When Not to Use Voice Agent API

Common Grok speech API pitfalls are usually naming confusion, outdated launch coverage, and overusing the most complex voice product. Grok is xAI's model and API brand, while Groq is a separate company known for fast inference infrastructure; developers searching "Grok voice API" and "Groq speech API" can easily land on the wrong docs. Pricing is another trap: the research brief found third-party posts with conflicting TTS prices, while current xAI model docs list Grok TTS at $15.00 per 1 million characters and Grok STT at $0.10 per REST hour or $0.20 per streaming hour. Finally, do not jump to Voice Agent API when a simple STT or TTS endpoint solves the product requirement. The takeaway: verify the vendor, verify current pricing, and pick the narrowest endpoint that works.

### What should you check before launch?

Before launch, check that your docs link to xAI, not Groq; your pricing constants match current xAI model docs; your API keys are server-side; your retry logic does not duplicate audio; and your dashboards split STT hours from TTS characters. Those checks prevent the most expensive early mistakes.

## FAQ

The xAI Grok speech API FAQ for developers mostly centers on endpoint choice, pricing, limits, streaming, and vendor confusion. As of the 2026 research brief, the concrete numbers to remember are $0.10 per hour for Grok STT REST, $0.20 per hour for Grok STT streaming, $15.00 per 1 million characters for Grok TTS, 500 MB maximum uploaded audio files in the STT guide, and 15,000 characters per REST TTS request. Those numbers are enough to estimate first-pass costs and design sane request boundaries. The bigger engineering decision is whether your product needs transcription, speech generation, or full voice interaction. Most teams should start with one endpoint and one narrow workflow before building a full conversational voice system. The takeaway: answer the architecture question first, then optimize pricing, streaming, and voice quality.

### Is the xAI Grok speech API the same as the Voice Agent API?

No. The speech APIs are lower-level STT and TTS primitives, while the Voice Agent API is for full duplex spoken conversations. If your app already manages turns, prompts, tools, and state, compose STT and TTS yourself. If the voice conversation is the product, evaluate Voice Agent API.

### How much does Grok STT cost?

Grok STT public model docs list REST transcription at $0.10 per hour and streaming transcription at $0.20 per hour. Treat those as separate meters in your billing model because batch uploads and live streams have different user behavior, retry patterns, and concurrency requirements.

### How much does Grok TTS cost?

Grok TTS public model docs list pricing at $15.00 per 1 million characters. Because TTS is character-metered, normalize whitespace, avoid regenerating unchanged chunks, and cache final audio assets when license terms and product behavior allow it.

### Which Grok TTS voice should I start with?

Start with `ara` for support or assistant flows, `sal` for neutral narration, and `leo` for instructional content. Then test all five built-in voices with real product copy. Voice choice is subjective, so use user feedback rather than developer preference alone.

### Can I call Grok STT or TTS directly from the browser?

You should not call Grok STT or TTS directly from the browser with a long-lived API key. Put a server-side proxy in front of xAI, authenticate your users there, enforce upload and rate policies, and return only the transcript or generated audio your client needs.
