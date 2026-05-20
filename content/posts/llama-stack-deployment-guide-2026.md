---
title: "llama-stack: Meta's Unified Deployment Stack for Llama 4 Models"
date: 2026-05-19T21:06:41+00:00
tags: ["llama-stack", "meta", "llama4", "llm-deployment", "open-source-ai"]
description: "Complete llama-stack tutorial for 2026: install, configure providers, build RAG pipelines, run agentic workflows, and add enterprise safety with PromptGuard."
draft: false
cover:
  image: "/images/llama-stack-deployment-guide-2026.png"
  alt: "llama-stack: Meta's Unified Deployment Stack for Llama 4 Models"
  relative: false
schema: "schema-llama-stack-deployment-guide-2026"
---

llama-stack is Meta's open-source framework that provides a standardized, provider-agnostic API layer for deploying Llama models across local machines, on-premises servers, and cloud environments. It abstracts inference, retrieval-augmented generation, agentic workflows, and safety into a single unified stack — so the same application code runs against Ollama on a laptop or vLLM on an H100 cluster by changing only the configuration file.

## What Is Llama Stack? Meta's Unified AI Deployment Framework

llama-stack is a composable deployment framework that standardizes how applications interact with Llama models regardless of where or how those models run. Llama models have been downloaded over 1.2 billion times by April 2025, making them the most widely adopted open-weight AI model family in the world — yet deployment has historically required building separate integration layers for each inference backend. llama-stack solves this by defining a set of provider-agnostic APIs (Inference, Safety, Memory, Agents, Tools) that map to interchangeable backends called providers. Switch from Ollama to vLLM to AWS Bedrock by changing a single field in a YAML configuration file, with zero application code changes. The framework ships with an OpenAI-compatible REST API, which means existing applications built against the OpenAI Python SDK can switch to llama-stack with a one-line endpoint change. Projected enterprise spending on Llama solutions reached $2.5 billion by 2026, with over 50% of Fortune 500 companies having piloted Llama solutions by March 2025. llama-stack is the deployment layer that makes that enterprise adoption operationally manageable.

## Why Llama Stack? Key Advantages Over LangChain, vLLM, and Ollama

llama-stack sits at a different layer of the AI stack than its most common comparisons. vLLM is a high-performance inference server — llama-stack can use vLLM as a provider. Ollama is a model management and serving tool — llama-stack can use Ollama as a provider. LangChain is an orchestration framework for building LLM applications — llama-stack can run LangChain-style agent workflows natively without requiring LangChain. The key distinction is that llama-stack is a unified deployment contract: it standardizes what APIs exist and how they behave across every backend, while the tools above each specialize in one layer. vLLM version 0.6.0 achieved 2.7x higher throughput and 5x faster time-per-output-token on Llama 8B compared to v0.5.3 — but realizing that performance improvement in a production application requires re-integration work unless you have an abstraction layer like llama-stack. The other critical advantage is built-in safety: PromptGuard and Llama Guard ship as first-class providers in llama-stack, not third-party add-ons. For enterprise deployments where content moderation is a compliance requirement, this integrated safety layer removes significant integration overhead.

## Llama 4 Models: Scout, Maverick, and Behemoth Overview

Llama 4 introduced a mixture-of-experts (MoE) architecture that dramatically changes the compute profile of Llama deployment in 2026. Llama 4 Scout has 17 billion active parameters with 16 experts and fits in a single NVIDIA H100 GPU — a significant reduction from Llama 3's memory requirements while delivering superior benchmark performance on most tasks. Llama 4 Maverick uses 17 billion active parameters with 128 experts and outperforms GPT-4o and Gemini 2.0 Flash across broad benchmarks despite a smaller active parameter count. Both Scout and Maverick are natively multimodal, processing images and text through the same unified model. Llama 4 Behemoth, the largest variant, targets research and frontier capability evaluation. For practical llama-stack deployments, Scout is the right choice for teams with single-GPU infrastructure or cost-sensitive production workloads. Maverick targets teams that need maximum reasoning and multimodal capability with multi-GPU access. llama-stack's inference API handles both identically — model selection is a configuration parameter, not an architecture change. The MoE architecture also changes inference provider requirements: vLLM's MoE optimizations and Ollama's quantization support are both relevant for different deployment contexts.

## Installing Llama Stack: pip, uv, and Docker Methods

llama-stack installs as a Python package and requires Python 3.10 or later. Three installation methods cover the main deployment scenarios: pip for quick start, uv for reproducible environments, and Docker for containerized production deployments.

**pip installation (simplest):**

```bash
pip install llama-stack
llama-stack --version
```

**uv installation (recommended for reproducible environments):**

```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create a project and install llama-stack
uv init my-llama-project
cd my-llama-project
uv add llama-stack

# Run commands through uv
uv run llama-stack --version
```

**Docker (production and team deployments):**

```bash
# Pull the official llama-stack image
docker pull meta-llama/llama-stack:latest

# Run the server with Ollama provider (Ollama must be running)
docker run -it \
  -p 8321:8321 \
  -v ~/.llama:/root/.llama \
  meta-llama/llama-stack:latest \
  llama-stack run ollama
```

After installation, verify the CLI is available:

```bash
llama-stack --help
# Lists: run, build, configure, download subcommands
```

The `llama-stack run` command starts the server using a named distribution or a custom YAML configuration file. The `llama-stack build` command creates a custom distribution combining specific providers for your use case.

## Configuring Your First Llama Stack Provider (Ollama Quickstart)

Ollama is the fastest path to a running llama-stack server for local development — it handles model downloading and management automatically. Start by installing Ollama and pulling a Llama 4 model, then start the llama-stack server pointing at Ollama as the inference provider.

**Step 1: Install Ollama and pull a model**

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull Llama 4 Scout (fits in single GPU or large RAM)
ollama pull llama4:scout

# Verify it's running
ollama list
```

**Step 2: Start llama-stack with the Ollama distribution**

```bash
llama-stack run ollama
# Server starts on http://localhost:8321
```

**Step 3: Test inference via the REST API**

```bash
curl http://localhost:8321/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama4:scout",
    "messages": [{"role": "user", "content": "Explain llama-stack in one paragraph."}]
  }'
```

**Step 4: Use the Python client SDK**

```python
from llama_stack_client import LlamaStackClient

client = LlamaStackClient(base_url="http://localhost:8321")

response = client.inference.chat_completion(
    model_id="llama4:scout",
    messages=[{"role": "user", "content": "What is llama-stack?"}]
)

print(response.completion_message.content.text)
```

The server exposes an OpenAI-compatible endpoint, so you can also use the `openai` Python SDK by changing only the `base_url`:

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8321/v1",
    api_key="not-needed"  # llama-stack uses no auth locally
)

response = client.chat.completions.create(
    model="llama4:scout",
    messages=[{"role": "user", "content": "Hello from OpenAI SDK!"}]
)
```

## Core APIs Deep Dive: Inference, RAG, Agents, Safety, and Tools

llama-stack defines five core API surfaces that every compliant provider must implement. Understanding what each API covers is essential for designing production deployments: Inference handles model text and multimodal generation, Memory handles vector storage and retrieval for RAG, Agents orchestrates multi-step tool-using workflows, Safety applies content filtering and guardrails, and Tools provides built-in tool implementations (web search, code execution, calculator). Each API is independently configurable — you can use Ollama for inference, a local ChromaDB for memory, and PromptGuard for safety simultaneously. The APIs communicate through a standardized JSON schema, which means you can inspect every request and response with standard HTTP tooling. For teams building production applications, the separation of concerns is the key design benefit: your RAG pipeline code does not change when you swap the vector database provider, and your agent orchestration code does not change when you upgrade from Llama 4 Scout to Maverick. This clean separation also enables incremental adoption — start with just the Inference API and add Memory and Safety as requirements emerge without restructuring the application.

## Building a RAG Pipeline with Llama Stack Step by Step

A RAG (Retrieval-Augmented Generation) pipeline in llama-stack uses the Memory API for document storage and vector retrieval, combined with the Inference API for generation. The pipeline: ingest documents into a memory bank, query the memory bank for relevant chunks at runtime, inject the retrieved context into the model prompt, and generate a response grounded in the retrieved documents.

```python
from llama_stack_client import LlamaStackClient
from llama_stack_client.types import Document

client = LlamaStackClient(base_url="http://localhost:8321")

# Step 1: Create a memory bank (vector store)
client.memory.create(
    name="product-docs",
    config={
        "type": "vector",
        "embedding_model": "all-MiniLM-L6-v2",
        "chunk_size_in_tokens": 512,
    }
)

# Step 2: Ingest documents
documents = [
    Document(
        document_id="doc-001",
        content="llama-stack provides unified APIs for LLM inference...",
        metadata={"source": "docs", "section": "overview"}
    ),
    Document(
        document_id="doc-002",
        content="The Inference API supports streaming and non-streaming responses...",
        metadata={"source": "docs", "section": "inference"}
    )
]
client.memory.insert(bank_name="product-docs", documents=documents)

# Step 3: Query at inference time
def rag_query(question: str) -> str:
    # Retrieve relevant chunks
    results = client.memory.query(
        bank_name="product-docs",
        query=question,
        params={"max_chunks": 3, "score_threshold": 0.7}
    )

    # Build context from retrieved chunks
    context = "\n\n".join([r.content for r in results.chunks])

    # Generate grounded response
    response = client.inference.chat_completion(
        model_id="llama4:scout",
        messages=[
            {"role": "system", "content": f"Answer based on this context:\n{context}"},
            {"role": "user", "content": question}
        ]
    )
    return response.completion_message.content.text

answer = rag_query("How does the Inference API handle streaming?")
print(answer)
```

## Agentic Workflows: Using the Responses API and MCP Tools

llama-stack's Agents API enables multi-step tool-using workflows where the model reasons about which tools to call, executes them, and incorporates results into subsequent reasoning steps. The framework supports both built-in tools (web search, code execution) and MCP (Model Context Protocol) servers, which means any existing MCP-compatible tool server integrates directly without custom adapters.

```python
from llama_stack_client import LlamaStackClient
from llama_stack_client.lib.agents.agent import Agent
from llama_stack_client.lib.agents.event_logger import EventLogger

client = LlamaStackClient(base_url="http://localhost:8321")

# Create an agent with built-in tools
agent = Agent(
    client,
    model="llama4:scout",
    instructions="You are a helpful research assistant. Use web search to find current information.",
    tools=[
        {"type": "brave_search", "engine": "brave", "api_key": "your-brave-api-key"},
        {"type": "code_interpreter"}
    ],
    max_infer_iters=5  # maximum reasoning steps
)

# Create a session and run the agent
session_id = agent.create_session("research-session")
response = agent.create_turn(
    session_id=session_id,
    messages=[{"role": "user", "content": "What are the latest benchmarks for Llama 4 Maverick?"}]
)

# Stream and log agent events
for event in EventLogger().log(response):
    print(event)
```

**MCP tool integration** connects llama-stack to any existing MCP server:

```python
# Connect an MCP server as a tool source
mcp_tool = {
    "type": "mcp",
    "server_url": "http://localhost:3000",  # your MCP server
    "tools": ["file_read", "file_write", "execute_bash"]
}

agent = Agent(client, model="llama4:scout", tools=[mcp_tool], ...)
```

## Enterprise Safety: PromptGuard and Llama Guard Shields

Enterprise deployments require content moderation at both input (prompt injection detection) and output (harmful content filtering). llama-stack integrates PromptGuard and Llama Guard as first-class safety shields through the Safety API. PromptGuard runs as a lightweight microservice with only 86 million parameters, enabling fast CPU-based safety classification without a GPU — critical for high-throughput deployments where adding a GPU for safety would double infrastructure costs. Llama Guard performs more nuanced multi-category safety classification (violence, hate speech, sexual content, dangerous information) on both prompts and completions. The Safety API applies shields in the agent workflow automatically: every message passes through configured shields before reaching the model and every completion passes through output shields before returning to the client. Violation handling is configurable — log-only for monitoring, block for enforcement, or custom callbacks for audit trails. Red Hat's production deployment patterns for Llama Stack demonstrate shield configurations that achieve enterprise safety compliance (EU AI Act content moderation requirements, NIST AI RMF implementation) without measurable latency impact from PromptGuard's CPU-based classification.

```python
# Configure safety shields in the run configuration (YAML)
# shields:
#   - provider_id: meta-reference
#     shield_id: prompt-guard
#     config:
#       violation_level: ERROR  # ERROR blocks, WARN logs only

# Apply shields in agent creation
agent = Agent(
    client,
    model="llama4:scout",
    instructions="You are a helpful assistant.",
    input_shields=["prompt-guard"],    # screen incoming messages
    output_shields=["llama-guard"],    # screen model outputs
)
```

## Production Deployment: vLLM, AWS Bedrock, and Azure OpenAI Providers

For production deployments, Ollama's throughput limitations become a bottleneck. vLLM is the recommended inference provider for on-premises GPU clusters: vLLM shows roughly 2.3x higher throughput than Ollama under 8 concurrent users. For cloud deployments, llama-stack supports AWS Bedrock and Azure OpenAI as inference providers, enabling teams to use managed Llama model endpoints without self-hosting GPU infrastructure.

**vLLM provider configuration:**

```yaml
# llama-stack-config.yaml
inference:
  - provider_id: vllm
    provider_type: remote::vllm
    config:
      url: http://vllm-server:8000
      max_tokens: 8192

models:
  - model_id: llama4-scout
    provider_id: vllm
    provider_model_id: meta-llama/Llama-4-Scout-17B-16E-Instruct
```

**Start the server with custom config:**

```bash
llama-stack run --config llama-stack-config.yaml
```

**AWS Bedrock provider:**

```yaml
inference:
  - provider_id: bedrock
    provider_type: remote::bedrock
    config:
      region: us-east-1
      # Uses AWS credentials from environment or IAM role

models:
  - model_id: llama4-scout
    provider_id: bedrock
    provider_model_id: meta.llama4-scout-17b-v1:0
```

For multi-provider production setups, llama-stack supports routing different models to different providers within a single server instance — Scout on AWS Bedrock for cost-sensitive queries and Maverick on a local vLLM cluster for high-complexity reasoning, all behind the same API endpoint.

## Llama Stack vs Alternatives: When to Choose What

llama-stack is not the right choice for every deployment scenario. The decision depends on whether you need provider portability, built-in safety, or the richest ecosystem of integrations and community tooling. LangChain remains the better choice for teams that need the broadest library of pre-built chains, integrations, and community examples — llama-stack's ecosystem is smaller, though growing rapidly. vLLM alone is the right choice if you need maximum raw inference throughput and are committed to a single model provider — llama-stack adds a network hop and abstraction layer that has a measurable (though small) latency cost at very high request rates. Ollama alone is the right choice for local development and individual developer workflows where the full llama-stack server is unnecessary overhead. llama-stack is the right choice when: you need to run the same application code across multiple inference backends (local dev, staging on-prem, production cloud); you require production-grade safety integration without building it yourself; you want OpenAI API compatibility without vendor lock-in to OpenAI; or you are building enterprise applications where the standardized API contract simplifies compliance and audit. The MCP support makes llama-stack particularly well-positioned for teams already invested in MCP tool servers, since those tools port directly into llama-stack agents without rebuilding.

---

## FAQ

llama-stack is Meta's newest infrastructure layer for Llama model deployment, and teams evaluating it consistently encounter the same practical questions: how it differs from vLLM and Ollama, whether it imposes latency overhead, how to handle authentication in production, and which provider to start with for local development. Llama models have crossed 1.2 billion downloads and $2.5 billion in projected enterprise spending for 2026 — the deployment tooling ecosystem around them is maturing fast. llama-stack's standardized API contract is the key value proposition for teams scaling from prototype to production without rewriting application code each time the infrastructure changes. Whether you are evaluating llama-stack for a greenfield LLM product or considering it as a migration path from a direct vLLM or LangChain integration, the answers below address the most common decision blockers based on real production deployment patterns and the current llama-stack feature set as of May 2026.

### How does llama-stack differ from just using vLLM or Ollama directly?

vLLM and Ollama are inference servers — they run models and expose APIs. llama-stack is a deployment framework that uses inference servers as providers. When you use vLLM directly, your application code is coupled to vLLM's API surface. When you use llama-stack with a vLLM provider, your application code targets llama-stack's standardized APIs, and vLLM is a swappable backend. The practical difference: switching from vLLM to AWS Bedrock in a direct integration requires application code changes; in a llama-stack integration, it requires only a configuration change. llama-stack also adds the Memory, Agents, and Safety APIs that vLLM and Ollama do not provide, meaning RAG pipelines and agentic workflows built on llama-stack do not require LangChain or similar orchestration libraries.

### Does llama-stack add significant latency compared to calling vLLM directly?

The latency overhead is small and typically unmeasurable in production scenarios. llama-stack's server adds a local HTTP hop between your application and the inference provider — on the same machine or same network segment, this adds single-digit milliseconds. For most production use cases where Llama 4 Scout inference itself takes 200–2000ms depending on prompt length, a 5ms framework overhead is negligible. The only scenario where it matters is extremely high-frequency, latency-sensitive inference where every millisecond counts — in that case, calling vLLM directly with a hardcoded provider is more appropriate than adding any abstraction layer.

### Which provider should you start with for local development?

Ollama is the recommended starting point for local development. It handles model download, quantization, and GPU/CPU management automatically — you run `ollama pull llama4:scout` and it works. The `llama-stack run ollama` command starts the full server in seconds. For teams without a dedicated GPU, Ollama's quantized model support enables Llama 4 Scout to run on a machine with 16GB RAM (using Q4 quantization), making local development accessible without specialized hardware. Switch to vLLM for staging and production environments where throughput matters — vLLM's 2.3x throughput advantage over Ollama under concurrent load justifies the additional setup complexity.

### How does authentication work in production llama-stack deployments?

Local llama-stack servers run without authentication by default — the API key field accepts any value. For production deployments, authentication is handled at the infrastructure layer: put an API gateway or reverse proxy (Nginx, Kong, AWS API Gateway) in front of the llama-stack server, and enforce authentication there. llama-stack itself does not implement API key management or OAuth — it relies on the surrounding infrastructure for access control. For team deployments where multiple users or services access the same llama-stack server, the recommended pattern is a network-level API gateway that issues tokens per client and proxies requests to llama-stack, preserving the simplicity of llama-stack's internal API while enforcing access control at the perimeter.

### Can llama-stack run Llama 4 Maverick on consumer hardware?

Llama 4 Maverick with 128 experts requires multi-GPU infrastructure — it does not fit in a single consumer GPU at full precision. On consumer hardware, the practical option is heavily quantized versions (Q2 or Q3) of Maverick using Ollama, which reduce memory requirements substantially at the cost of output quality. For the best balance of capability and consumer hardware accessibility, Llama 4 Scout (17B active parameters, 16 experts) with Q4 quantization runs effectively on an NVIDIA RTX 4090 or a machine with 32GB RAM via CPU inference. llama-stack supports both configurations — configure the provider for Ollama with the quantized model identifier, and the application code is identical regardless of which quantization level runs underneath.
