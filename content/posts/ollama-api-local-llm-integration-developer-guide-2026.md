---
cover:
  alt: 'Ollama API Guide: Run Local LLMs with REST API and OpenAI-Compatible SDK'
  image: /images/ollama-api-local-llm-integration-developer-guide-2026.png
  relative: false
date: 2026-06-02 14:42:11+00:00
description: 'Complete Ollama API guide: REST endpoints, OpenAI-compatible /v1/ drop-in,
  Python SDK, embeddings, RAG pipelines, and Docker production deployment.'
draft: false
schema: schema-ollama-api-local-llm-integration-developer-guide-2026
tags:
- ollama
- local-llm
- rest-api
- openai-compatible
- python
- developer-guide
title: 'Ollama API Guide: Run Local LLMs with REST API and OpenAI-Compatible SDK'
---

Ollama is an open-source local LLM runtime that exposes a REST API on `http://localhost:11434`, letting you run Llama 4, Qwen3, DeepSeek R1, Gemma 4, and 4,500+ other models entirely on your machine — with zero per-token cost and no data leaving your network. The OpenAI-compatible `/v1/` layer means most existing SDK code works after a one-line `base_url` change.

## Why Local LLMs Went Mainstream in 2026

Local LLM adoption crossed a meaningful threshold in 2026, driven by economics, privacy regulation, and dramatically improved model quality in small footprints. Ollama surpassed 170,000 GitHub stars — the most starred local LLM runtime project on the platform — and monthly downloads grew from 100K in Q1 2023 to 52 million in Q1 2026, a 520x increase in three years. The stat that matters most for developer decision-making: 42% of developers now run at least some LLM workloads entirely on local machines, up from single digits in 2023. The economic case is straightforward — a team of five developers can spend $3,000–$30,000 in cloud LLM API costs over a three-month development cycle before shipping a single production feature. Local inference eliminates that cost entirely during the iteration phase. HuggingFace now hosts 135,000 GGUF-formatted models optimized for local inference, up from just 200 three years ago, giving developers access to a deep catalog. For regulated industries — healthcare, finance, government — local deployment isn't just economical, it's frequently mandatory: patient data, financial records, and classified documents cannot traverse cloud APIs. Ollama handles this by design.

### What Changed Between 2023 and 2026

The 2023 local LLM experience involved constant friction: manual GGUF downloads, complex llama.cpp invocations, no API compatibility, and GPU configuration that required reading three separate blog posts. Ollama's contribution was packaging all of this into a single binary with a clean HTTP API. In 2026, the API surface has stabilized around two layers: the native Ollama REST API for full model lifecycle control, and the OpenAI-compatible `/v1/` endpoints for dropping into existing code with zero changes. Hardware improvements matter too — Apple Silicon M3/M4 machines run 13B parameter models at 40+ tokens per second without a GPU, making high-quality inference accessible on standard developer laptops.

## What Is Ollama — Architecture and How the Server Works

Ollama is a Go-based server that wraps llama.cpp inference, model management, and an HTTP API into a single self-contained binary. When you start Ollama, it binds to port 11434 and manages models stored in `~/.ollama/models` (macOS/Linux) or `C:\Users\{user}\.ollama\models` (Windows). The server handles concurrent requests by queuing them against a single model instance — only one model loads at a time by default, with GPU VRAM being the binding constraint. The architecture is intentionally simple: no separate database process, no configuration files required to start, no authentication layer for local use. Models are stored in a content-addressed format derived from the Modelfile, which is a Dockerfile-like specification that declares the base model, system prompt, temperature, and other parameters. The REST API exposes two namespaces — `/api/` for native Ollama operations and `/v1/` for OpenAI-compatible operations. The underlying inference engine is llama.cpp, which means Ollama inherits its quantization support (Q4_K_M, Q8_0, FP16, etc.) and hardware acceleration backends: CUDA for NVIDIA GPUs, Metal for Apple Silicon, ROCm for AMD GPUs, and CPU fallback for any machine. Ollama typically achieves 15–20% faster inference than LocalAI for equivalent LLM workloads due to tighter integration with llama.cpp's optimization passes.

## Installation on macOS, Linux, and Windows

Ollama installs to a running server in under a minute on all three platforms. Each installs the `ollama` CLI and starts the background server automatically.

**macOS:**
```bash
brew install ollama
# or download from https://ollama.com/download/mac
ollama serve  # starts server; or it starts automatically via the macOS app
```

**Linux (one-line install):**
```bash
curl -fsSL https://ollama.com/install.sh | sh
# Server starts as a systemd service: systemctl status ollama
```

**Windows:**
Download the installer from `https://ollama.com/download/windows` — it installs a system tray app that starts the server at login.

**Verify the server is running:**
```bash
curl http://localhost:11434
# Returns: "Ollama is running"
```

**Pull your first model:**
```bash
ollama pull llama3.2          # 2B parameter, ~1.3GB
ollama pull qwen3:7b          # 7B parameter, ~4.7GB
ollama pull deepseek-r1:8b    # 8B, strong reasoning
ollama pull nomic-embed-text  # embedding model
```

Model sizes to know: 7B Q4_K_M ≈ 4.5GB RAM/VRAM, 13B Q4_K_M ≈ 8GB, 70B Q4_K_M ≈ 40GB. For machines with 16GB RAM, 7B–13B models are the practical sweet spot.

## The Native Ollama REST API — Every Endpoint Explained

The native Ollama REST API lives under `/api/` and provides full programmatic control over text generation, multi-turn chat, embeddings, and model lifecycle management — all over plain HTTP with JSON request and response bodies. The server binds to `http://localhost:11434` by default and requires no authentication for local use. There are seven primary endpoints in the native API: `/api/generate` for single-turn completions, `/api/chat` for multi-turn conversations, `/api/embed` for vector embeddings, `/api/tags` to list installed models, `/api/pull` to download models, `/api/delete` to remove models, and `/api/show` to inspect model metadata. Streaming is enabled by default — set `"stream": false` to receive a single JSON response instead of newline-delimited chunks. Every endpoint that runs inference accepts an `options` object where you can override model parameters: `temperature`, `top_p`, `num_ctx` (context length), `num_predict` (max output tokens), and `stop` sequences. All parameter changes are per-request; there is no persistent session state on the server side. Understanding which endpoint to use for which workload is the first step to building reliable Ollama-backed applications.

### Generate: /api/generate

The generate endpoint runs single-turn completions against a raw prompt.

```bash
curl http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama3.2",
    "prompt": "Explain Docker multi-stage builds in one paragraph.",
    "stream": false,
    "options": {
      "temperature": 0.7,
      "top_p": 0.9,
      "num_ctx": 4096
    }
  }'
```

Key parameters in `options`:
- `temperature` (0.0–2.0): randomness; 0.1 for factual tasks, 0.7–1.0 for creative
- `top_p` (0.0–1.0): nucleus sampling; 0.9 is a sensible default
- `num_ctx`: context window size in tokens; defaults to 2048, increase for long documents
- `num_predict`: max tokens to generate; -1 for unlimited
- `stop`: array of stop sequences

**With streaming (default):** Set `"stream": true` (or omit it) and the response comes as newline-delimited JSON objects, each containing a `response` field, ending with a final object where `"done": true`.

### Chat: /api/chat

The chat endpoint manages multi-turn conversations with a messages array, matching OpenAI's message format.

```bash
curl http://localhost:11434/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama3.2",
    "messages": [
      {"role": "system", "content": "You are a senior Python developer."},
      {"role": "user", "content": "What is the difference between __str__ and __repr__?"}
    ],
    "stream": false
  }'
```

The response includes a `message` object with `role: "assistant"` and `content`. For multi-turn, append the assistant response to the messages array and send again — Ollama is stateless; you own the conversation history.

### Embeddings: /api/embed

```bash
curl http://localhost:11434/api/embed \
  -H "Content-Type: application/json" \
  -d '{
    "model": "nomic-embed-text",
    "input": "Ollama makes local LLM inference simple."
  }'
```

Returns `{"embeddings": [[0.123, -0.456, ...]]}`. The `input` field accepts a string or array of strings for batch embedding. `nomic-embed-text` produces 768-dimensional vectors; `mxbai-embed-large` produces 1024-dimensional.

## OpenAI-Compatible API at /v1/ — Drop-In Replacement for Existing Apps

The `/v1/` namespace is where Ollama becomes immediately practical for teams with existing OpenAI SDK integrations. Supported endpoints mirror the OpenAI API surface: `/v1/chat/completions`, `/v1/completions`, `/v1/embeddings`, and `/v1/models`. Authentication accepts any non-empty string as the API key — use `"ollama"` or any placeholder. The critical migration path: if you have code calling `api.openai.com`, changing `base_url` to `http://localhost:11434/v1` is the entire migration for the core chat and embedding workflows. No other code changes needed. This compatibility layer was the key architectural decision that drove Ollama's adoption past competitors — developers don't need to learn a new API surface to use it. Supported chat features include system messages, multi-turn history, `temperature`/`top_p`/`max_tokens` parameters, streaming via SSE, and function/tool calling on models that support it (Llama 3.1+, Qwen2.5+). Unsupported OpenAI features include: logprobs, fine-tuning endpoints, assistants API, files API, and image generation. For those features, you either don't need them locally or they require model-specific handling.

```bash
# Same curl you'd use against OpenAI, just different base URL
curl http://localhost:11434/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ollama" \
  -d '{
    "model": "llama3.2",
    "messages": [{"role": "user", "content": "Write a Python hello world"}]
  }'
```

## Python Integration: Native ollama Library vs OpenAI SDK

Python is the dominant language for LLM integration work, and Ollama supports two distinct SDK paths: the native `ollama` Python library (which mirrors the REST API directly), and the `openai` Python SDK pointed at Ollama's `/v1/` compatibility layer. The native `ollama` library, installed via `pip install ollama`, wraps every `/api/` endpoint with typed Python functions — `ollama.generate()`, `ollama.chat()`, `ollama.embed()`, `ollama.pull()`, `ollama.list()` — and handles streaming, async, and error handling out of the box. The `openai` SDK path requires no new library if you already have it installed — just pass `base_url='http://localhost:11434/v1'` and any string as `api_key`, and all existing code that calls `client.chat.completions.create()` or `client.embeddings.create()` works unchanged. The right choice is practical: if you're starting fresh or want the full Ollama feature set (model management, Modelfile inspection, etc.), use the native library. If you have existing OpenAI SDK code and want a zero-change migration path for local development, use the OpenAI SDK with a custom base URL. Both approaches produce identical inference results.

### Native ollama Library

```python
pip install ollama
```

```python
import ollama

# Synchronous generate
response = ollama.generate(model='llama3.2', prompt='What is GGUF format?')
print(response['response'])

# Chat with history
messages = [
    {'role': 'system', 'content': 'You are a helpful coding assistant.'},
    {'role': 'user', 'content': 'Explain Python generators.'}
]
response = ollama.chat(model='llama3.2', messages=messages)
print(response['message']['content'])

# Streaming
for chunk in ollama.generate(model='llama3.2', prompt='Count to 5.', stream=True):
    print(chunk['response'], end='', flush=True)

# Embeddings
result = ollama.embed(model='nomic-embed-text', input='Hello world')
vector = result['embeddings'][0]
```

### OpenAI SDK Pointed at Ollama

For existing code — or when you want the same SDK interface to swap between Ollama and OpenAI based on environment:

```python
from openai import OpenAI
import os

client = OpenAI(
    base_url='http://localhost:11434/v1',
    api_key='ollama'  # any string works
)

response = client.chat.completions.create(
    model='llama3.2',
    messages=[{'role': 'user', 'content': 'What is RAG?'}]
)
print(response.choices[0].message.content)

# Embeddings
embedding = client.embeddings.create(
    model='nomic-embed-text',
    input='Document text to embed'
)
vector = embedding.data[0].embedding
```

**Env-based switching pattern** — useful for CI (use cloud) vs local dev (use Ollama):

```python
import os
from openai import OpenAI

if os.getenv('USE_LOCAL_LLM', 'false').lower() == 'true':
    client = OpenAI(base_url='http://localhost:11434/v1', api_key='ollama')
    model = 'llama3.2'
else:
    client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])
    model = 'gpt-4o-mini'
```

## Streaming Responses, Embeddings, and Multi-Turn Chat with Code

Streaming is the default behavior for every generation endpoint in Ollama and is the correct choice for user-facing applications — it makes responses feel fast even when model throughput is 15–20 tokens per second, because the first token appears in under a second rather than the user waiting 10–30 seconds for the full response. Ollama streaming works by sending newline-delimited JSON objects as the model generates each token. In the native API, each chunk contains a `response` field (for `/api/generate`) or a `message.content` field (for `/api/chat`), plus a `done: false` flag. The final chunk has `done: true` and includes performance metadata: `eval_count` (tokens generated), `eval_duration` (nanoseconds), `prompt_eval_count`, and `total_duration`. For the OpenAI-compatible `/v1/` endpoint, streaming follows the SSE (Server-Sent Events) format with `data: {"choices": [...]}` lines ending with `data: [DONE]`. Multi-turn chat requires you to maintain the message history client-side — Ollama is stateless; each request must include the full conversation history from the start. Embeddings do not stream; they return synchronously as a single JSON response.

### Streaming with Native API

```python
import ollama

def stream_response(prompt: str, model: str = 'llama3.2'):
    for chunk in ollama.generate(model=model, prompt=prompt, stream=True):
        print(chunk['response'], end='', flush=True)
        if chunk.get('done'):
            print()  # newline at end
            print(f"Tokens: {chunk.get('eval_count', 0)}, "
                  f"Speed: {chunk.get('eval_count', 0) / chunk.get('eval_duration', 1) * 1e9:.1f} t/s")

stream_response("Explain async/await in Python in 3 sentences.")
```

### Multi-Turn Chat State Management

```python
import ollama
from dataclasses import dataclass, field
from typing import List

@dataclass
class ChatSession:
    model: str
    system_prompt: str = ""
    history: List[dict] = field(default_factory=list)
    
    def __post_init__(self):
        if self.system_prompt:
            self.history.append({'role': 'system', 'content': self.system_prompt})
    
    def send(self, user_message: str) -> str:
        self.history.append({'role': 'user', 'content': user_message})
        response = ollama.chat(model=self.model, messages=self.history)
        assistant_msg = response['message']['content']
        self.history.append({'role': 'assistant', 'content': assistant_msg})
        return assistant_msg

session = ChatSession(model='llama3.2', system_prompt='You are a senior Go developer.')
print(session.send("What is a goroutine?"))
print(session.send("How does that compare to Python threads?"))
```

### Async Streaming for Web Applications

```python
import asyncio
import ollama

async def async_stream(prompt: str):
    async_client = ollama.AsyncClient()
    async for chunk in await async_client.generate(
        model='llama3.2', prompt=prompt, stream=True
    ):
        yield chunk['response']

# FastAPI integration
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

app = FastAPI()

@app.get("/generate")
async def generate(prompt: str):
    return StreamingResponse(
        async_stream(prompt),
        media_type="text/event-stream"
    )
```

## Model Management via API: Pull, List, Copy, Delete, Inspect

The Ollama REST API exposes full model lifecycle management through dedicated endpoints, making the CLI entirely optional for teams building automated deployment pipelines, model management dashboards, or CI workflows that need to ensure specific models are available before running tests. The five management endpoints are: `GET /api/tags` (list installed models with size, digest, and modification timestamp), `POST /api/pull` (download a model from the Ollama library with optional streaming progress), `DELETE /api/delete` (remove an installed model), `POST /api/copy` (duplicate a model under a new name — useful for custom Modelfile variants), and `POST /api/show` (return the full Modelfile, parameter defaults, template, and quantization metadata for an installed model). Pull operations stream progress as newline-delimited JSON objects with `status`, `completed`, and `total` bytes fields — you can build a progress bar directly from the stream. All management operations are synchronous from the caller's perspective except pull, which can take several minutes for large models. The Ollama library on the public registry contains 4,500+ models as of May 2026, including Llama 4, Qwen3, DeepSeek R1, Gemma 4, Mistral, and the full range of embedding models.

### List Installed Models

```bash
curl http://localhost:11434/api/tags
```

Returns an array of model objects with `name`, `size`, `digest`, and `modified_at` fields.

```python
import requests

def list_models():
    resp = requests.get('http://localhost:11434/api/tags')
    models = resp.json()['models']
    for m in models:
        size_gb = m['size'] / (1024**3)
        print(f"{m['name']:<30} {size_gb:.1f}GB")

list_models()
```

### Pull a Model

```bash
curl http://localhost:11434/api/pull \
  -d '{"model": "qwen3:7b", "stream": false}'
```

With progress streaming (stream: true), each JSON line includes a `status` and optionally `completed`/`total` bytes.

### Delete a Model

```bash
curl -X DELETE http://localhost:11434/api/delete \
  -d '{"model": "llama3.2"}'
```

### Inspect Model Details

```bash
curl http://localhost:11434/api/show \
  -d '{"model": "llama3.2"}'
```

Returns the full Modelfile, parameters, template, and model metadata including context length, quantization type, and parameter count.

### Copy a Model

```bash
curl http://localhost:11434/api/copy \
  -d '{"source": "llama3.2", "destination": "my-custom-llama"}'
```

Useful for creating named variants with custom system prompts via Modelfiles without downloading additional weights.

## Building a Local RAG Pipeline with Ollama + ChromaDB

A local RAG pipeline using Ollama for both embeddings and generation, with ChromaDB as the vector store, achieves production-quality retrieval with zero external API costs. Properly configured Ollama deployments achieve 40–60% cost savings compared to cloud APIs while maintaining comparable performance on RAG tasks. The stack: `nomic-embed-text` for document embeddings (768 dimensions, 8K context), `llama3.2` or `qwen3:7b` for generation, ChromaDB for vector storage and retrieval. The architecture is entirely local — documents, embeddings, and query results never leave the machine.

```python
pip install chromadb ollama
```

```python
import ollama
import chromadb
from chromadb.utils import embedding_functions

# Custom embedding function using Ollama
class OllamaEmbeddingFunction(embedding_functions.EmbeddingFunction):
    def __init__(self, model: str = 'nomic-embed-text'):
        self.model = model
    
    def __call__(self, input: list[str]) -> list[list[float]]:
        result = ollama.embed(model=self.model, input=input)
        return result['embeddings']

# Initialize ChromaDB
client = chromadb.Client()
embed_fn = OllamaEmbeddingFunction()
collection = client.create_collection(
    name='docs',
    embedding_function=embed_fn
)

# Index documents
docs = [
    "Ollama is an open-source local LLM runtime.",
    "RAG combines retrieval with generation for accurate answers.",
    "ChromaDB is an open-source vector database for embeddings.",
    "Python async/await enables non-blocking concurrent execution.",
]
collection.add(
    documents=docs,
    ids=[f"doc_{i}" for i in range(len(docs))]
)

def rag_query(question: str, n_results: int = 3) -> str:
    results = collection.query(query_texts=[question], n_results=n_results)
    context = "\n".join(results['documents'][0])
    
    prompt = f"""Answer the question based ONLY on the context below.
    
Context:
{context}

Question: {question}

Answer:"""
    
    response = ollama.generate(model='llama3.2', prompt=prompt)
    return response['response']

print(rag_query("What is Ollama?"))
print(rag_query("How does RAG work?"))
```

For production RAG, replace ChromaDB's in-memory store with its persistent client (`chromadb.PersistentClient(path="./chroma_db")`) and add chunking for large documents using `langchain_text_splitters.RecursiveCharacterTextSplitter`.

## Production Deployment: Docker Compose, GPU Config, and Multi-Model Serving

Running Ollama in Docker makes the setup reproducible across team machines, staging environments, and CI pipelines, and is the recommended approach for shared team infrastructure where developers need access to the same models without each person managing a local install. The official Docker image is `ollama/ollama:latest` — it bundles the Ollama binary, CUDA libraries for NVIDIA GPU support, and a working entrypoint. For NVIDIA GPU access, the NVIDIA Container Toolkit must be installed on the host, after which the Docker Compose `deploy.resources.reservations.devices` block passes GPU access into the container. Apple Silicon GPU access is only available via the native macOS binary, not Docker. The key environment variables for production tuning are `OLLAMA_NUM_PARALLEL` (concurrent inference slots — each slot uses its own VRAM allocation), `OLLAMA_MAX_LOADED_MODELS` (how many models stay hot in memory), and `OLLAMA_KEEP_ALIVE` (how long an idle model stays loaded before being evicted). For high-availability setups, multiple Ollama instances behind an nginx or HAProxy load balancer is a proven pattern — each instance manages its own model state independently, and the load balancer distributes requests across the pool.

### Docker Compose for Team Development

```yaml
# docker-compose.yml
version: '3.8'
services:
  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_models:/root/.ollama
    environment:
      - OLLAMA_HOST=0.0.0.0
      - OLLAMA_NUM_PARALLEL=2      # concurrent requests
      - OLLAMA_MAX_LOADED_MODELS=2 # models in memory simultaneously
    restart: unless-stopped
    # For NVIDIA GPU:
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]

  # Pull models on startup
  ollama-init:
    image: curlimages/curl:latest
    depends_on:
      - ollama
    command: >
      sh -c "sleep 5 &&
             curl -s http://ollama:11434/api/pull -d '{\"model\": \"llama3.2\"}' &&
             curl -s http://ollama:11434/api/pull -d '{\"model\": \"nomic-embed-text\"}'"
    restart: "no"

volumes:
  ollama_models:
```

```bash
docker compose up -d
```

### GPU Configuration

**NVIDIA:** Install the NVIDIA Container Toolkit, then the Docker Compose above works as-is. Verify with:
```bash
docker exec ollama nvidia-smi
```

**Apple Silicon:** GPU acceleration is automatic when running the native macOS binary — Metal is detected without configuration. Docker on macOS does not have Metal access; run the native binary for GPU use.

**NVIDIA without Docker:**
```bash
export CUDA_VISIBLE_DEVICES=0  # use GPU 0
ollama serve
```

**CPU-only fallback:** All operations work without GPU — just slower. `OLLAMA_INTEL_GPU=1` enables Intel Arc GPU support on Linux.

### Environment Variables for Production Tuning

| Variable | Default | Purpose |
|---|---|---|
| `OLLAMA_HOST` | `127.0.0.1:11434` | Bind address; use `0.0.0.0` for network access |
| `OLLAMA_NUM_PARALLEL` | 1 | Concurrent request slots |
| `OLLAMA_MAX_LOADED_MODELS` | 1 | Models to keep in VRAM simultaneously |
| `OLLAMA_KEEP_ALIVE` | `5m` | How long to keep model loaded after last request |
| `OLLAMA_MODELS` | `~/.ollama/models` | Custom model storage path |
| `OLLAMA_DEBUG` | `false` | Verbose logging |

**Key tuning decision:** `OLLAMA_KEEP_ALIVE="-1"` keeps the model permanently loaded — eliminates cold-start latency (5–30 seconds) at the cost of dedicated VRAM.

### Serving Multiple Models

With `OLLAMA_MAX_LOADED_MODELS=2` and sufficient VRAM, Ollama serves a generation model and embedding model simultaneously — the common RAG pattern. Requests to a model that isn't loaded trigger an automatic load (evicting the LRU model if at capacity).

For high-concurrency production deployments, run multiple Ollama instances on different ports and load-balance with nginx:

```nginx
upstream ollama_cluster {
    server localhost:11434;
    server localhost:11435;
    server localhost:11436;
}
server {
    listen 8080;
    location / {
        proxy_pass http://ollama_cluster;
        proxy_read_timeout 300s;
    }
}
```

---

## FAQ

**Q: Does Ollama work without a GPU?**
Yes. All models run on CPU with automatic fallback. A 7B model runs at 5–15 tokens/second on a modern CPU — usable for development and batch processing, though slower than GPU. Apple Silicon Macs are a special case: the M-series chips use unified memory for both CPU and GPU, achieving 30–60 tokens/second on 7B models without a discrete GPU.

**Q: How do I use Ollama with LangChain?**
Install `langchain-ollama` and use `ChatOllama` and `OllamaEmbeddings`:
```python
from langchain_ollama import ChatOllama, OllamaEmbeddings
llm = ChatOllama(model="llama3.2", temperature=0)
embeddings = OllamaEmbeddings(model="nomic-embed-text")
```
This plugs directly into any LangChain chain, agent, or retriever.

**Q: What's the difference between /api/generate and /api/chat?**
`/api/generate` takes a single `prompt` string and is stateless — the model sees exactly what you send. `/api/chat` takes a `messages` array (system/user/assistant roles) and is designed for multi-turn conversations. Under the hood, `/api/chat` formats the messages into the model's chat template automatically. Use `/api/chat` for conversational interfaces and `/api/generate` for completion tasks where you want full control over the prompt.

**Q: Can I run multiple models at the same time?**
Yes, with `OLLAMA_MAX_LOADED_MODELS` set to 2 or higher. Each loaded model occupies VRAM independently. Requests round-robin or queue per-model. The practical limit is VRAM: two 7B Q4_K_M models need ~9GB VRAM total.

**Q: How do I add a custom system prompt permanently?**
Create a Modelfile:
```
FROM llama3.2
SYSTEM "You are a senior DevOps engineer specializing in Kubernetes."
PARAMETER temperature 0.3
```
Then: `ollama create my-devops-model -f Modelfile`. The new model shows up in `/api/tags` and accepts API calls like any other model.