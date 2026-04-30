---
title: "GPT-5.4 API Developer Guide 2026: 1M Context, Computer Use, and 5 Reasoning Levels"
date: 2026-04-30T09:04:26+00:00
tags: ["gpt-5.4 api", "openai", "llm", "developer guide", "computer use", "reasoning"]
description: "Complete GPT-5.4 API guide: 1M token context, 5 reasoning effort levels, native computer use, pricing tiers, and migration from gpt-4o/gpt-5.2."
draft: false
cover:
  image: "/images/gpt-5-4-api-developer-guide-2026.png"
  alt: "GPT-5.4 API Developer Guide 2026: 1M Context, Computer Use, and 5 Reasoning Levels"
  relative: false
schema: "schema-gpt-5-4-api-developer-guide-2026"
---

GPT-5.4 is OpenAI's most capable general-purpose model as of 2026, combining a 1,050,000-token context window, native computer use at 75% OSWorld accuracy, and five tunable reasoning effort levels in a single Chat Completions API drop-in. Released March 5, 2026, it replaces gpt-5.2 for most production workloads with no endpoint change required.

## What Is GPT-5.4? Release Date, Model Variants, and What's New

GPT-5.4 is OpenAI's flagship general-purpose language model released on March 5, 2026, and it represents the first mainline model to combine frontier reasoning, native computer control, and a 1-million-token context window in a single architecture. Unlike earlier specialized variants — o3 for reasoning or gpt-5.2 for general use — GPT-5.4 integrates GPT-5.3-codex coding capabilities directly, making it a unified backbone for agentic, analytical, and conversational workloads. On launch day, it scored 75.0% on the OSWorld-Verified computer use benchmark, surpassing the human expert baseline of 72.4% — a first for any general-purpose model. On knowledge work (GDPval), GPT-5.4 matches or outperforms industry professionals in 83% of comparisons across 44 occupations. There are two production variants: **gpt-5.4** (the standard model, priced at $2.50/$15 per million input/output tokens) and **gpt-5.4-pro** (optimized for high-stakes enterprise tasks at $30/$180 per million input/output tokens). Both share the same API surface and context window; the pro variant allocates more compute budget per inference by default.

### Model Variants at a Glance

| Model | Input Price | Output Price | Best For |
|---|---|---|---|
| gpt-5.4 | $2.50/M tokens | $15/M tokens | General API workloads, agents |
| gpt-5.4-pro | $30/M tokens | $180/M tokens | High-stakes enterprise, legal, finance |
| gpt-5.4-mini | See pricing page | See pricing page | Cost-sensitive high-volume use |

The **gpt-5.4-mini** variant is aimed at cost-sensitive, high-volume tasks like classification, extraction, and routing — where full reasoning headroom is unnecessary. For the majority of production API use, gpt-5.4 with tuned `reasoning.effort` is the right starting point.

## GPT-5.4 API Access: Endpoints, Authentication, and Drop-In Migration

GPT-5.4 is a drop-in replacement for any Chat Completions API caller — you change the `model` string and gain new capabilities immediately. The endpoint, authentication headers, message format, and streaming protocol are identical to gpt-4o and gpt-5.2. Organizations already on gpt-4o can migrate in under five minutes by updating a single environment variable. For gpt-5.2 users, the migration is equally straightforward: all previous parameters (`temperature`, `top_p`, `tool_choice`, `response_format`) continue to work unchanged. New GPT-5.4-specific parameters (`reasoning.effort`, `computer_use`) are optional — omitting them returns behavior equivalent to a standard chat completion. This backward compatibility is intentional: OpenAI's published migration guide classifies gpt-5.4 as a drop-in upgrade, not a breaking API change. Authentication uses the same `Authorization: Bearer sk-...` header and OpenAI SDK versions ≥ 2.0.0 include native GPT-5.4 support.

```python
from openai import OpenAI

client = OpenAI()  # reads OPENAI_API_KEY from environment

response = client.chat.completions.create(
    model="gpt-5.4",           # only change needed from gpt-4o
    messages=[
        {"role": "user", "content": "Explain the 1M context window use cases."}
    ]
)
print(response.choices[0].message.content)
```

For teams using the Node.js SDK:

```typescript
import OpenAI from "openai";

const client = new OpenAI();

const response = await client.chat.completions.create({
  model: "gpt-5.4",
  messages: [{ role: "user", content: "What changed in GPT-5.4?" }],
});
```

Both examples require zero structural changes beyond the model name.

## The 5 Reasoning Effort Levels Explained (none to xhigh) with Code Examples

The `reasoning.effort` parameter is GPT-5.4's most important new knob for production developers, offering five distinct levels — `none`, `low`, `medium`, `high`, and `xhigh` — that directly control the model's internal chain-of-thought budget, latency, and per-token cost. At `none`, the model skips explicit reasoning steps and behaves like a fast instruct model; at `xhigh`, it allocates maximum compute to multi-step reasoning, which can cost 3–5x more than the same request at `low`. This replaces the blunt `temperature` dial for controlling response quality: you now tune *reasoning depth* rather than sampling randomness. For most production routing tasks, `low` or `medium` is sufficient. For code synthesis, complex analysis, or agentic planning where accuracy is critical, `high` or `xhigh` pays for itself by reducing error-correction loops. OpenAI benchmarks show that xhigh produces measurably better SWE-bench results (57.7%) than medium or low settings on the same model weights.

```python
# Classification / routing — low effort, fast and cheap
response = client.chat.completions.create(
    model="gpt-5.4",
    reasoning={"effort": "low"},
    messages=[{"role": "user", "content": "Classify this support ticket: 'My invoice is wrong'"}]
)

# Complex code synthesis — xhigh effort
response = client.chat.completions.create(
    model="gpt-5.4",
    reasoning={"effort": "xhigh"},
    messages=[{"role": "user", "content": "Refactor this 800-line Python module to async..."}]
)
```

### Choosing the Right Effort Level

| Task Type | Recommended Effort | Relative Cost |
|---|---|---|
| Classification, routing, extraction | none / low | 1x |
| Summarization, Q&A over documents | medium | 1.5–2x |
| Code review, debugging, analysis | high | 2–3x |
| Complex agentic planning, synthesis | xhigh | 3–5x |

A practical production strategy: default to `medium`, then gate `xhigh` behind a fallback path triggered when `medium` returns low-confidence outputs. This pattern cuts mean inference cost by 40–60% compared to running all requests at `xhigh`.

### Latency Expectations by Effort Level

`none` and `low` typically return first tokens in under 1 second for short prompts. `xhigh` on a complex prompt may take 10–30 seconds before streaming begins. Design your UX accordingly — streaming with `stream: true` is strongly recommended for `high` and `xhigh` requests so users see incremental output.

## 1 Million Token Context Window: How It Works and When to Use It

GPT-5.4 supports up to 1,050,000 input tokens in a single request, making it the first general-purpose model capable of ingesting an entire large codebase, a full book, or months of agent conversation history in one API call. The context window is priced in two tiers: input tokens up to 272,000 are billed at the standard rate ($2.50/M for gpt-5.4), while tokens beyond that threshold cost 2x input and 1.5x output. This means loading a 500K-token codebase costs roughly $3.00 in input fees at standard pricing — a viable alternative to building complex chunking and retrieval pipelines for many teams. The practical effect is that tasks previously requiring RAG infrastructure (embedding databases, chunking logic, retrieval tuning) can now be handled with a single structured prompt. That said, long-context requests still increase latency proportionally, and the model's effective attention over very long inputs degrades for needles buried deep in a haystack — retrieval-augmented approaches remain superior for precise lookup across millions of documents.

### Practical 1M Context Use Cases

**Full codebase analysis:** Load an entire monorepo (300K–600K tokens) and ask GPT-5.4 to trace a bug across files, identify dead code, or generate a migration plan. No chunking, no embedding index.

```python
import os

# Load all Python files in a repo
def load_repo(path: str) -> str:
    files = []
    for root, _, fnames in os.walk(path):
        for fname in fnames:
            if fname.endswith(".py"):
                fpath = os.path.join(root, fname)
                content = open(fpath).read()
                files.append(f"### {fpath}\n{content}")
    return "\n\n".join(files)

repo_content = load_repo("./my-project")

response = client.chat.completions.create(
    model="gpt-5.4",
    messages=[
        {"role": "system", "content": "You are a senior code reviewer."},
        {"role": "user", "content": f"Review this codebase for security issues:\n\n{repo_content}"}
    ]
)
```

**Long agent session replay:** Persist full conversation history across days or weeks of an agentic workflow and let GPT-5.4 reason over its own prior decisions. This eliminates the need for external memory stores in many agent architectures.

**Multi-document contract analysis:** Load 50+ contract PDFs (converted to text) in one request and ask the model to identify conflicting clauses across documents — a task that was previously impractical without custom orchestration.

### When Not to Use 1M Context

- When you need sub-second latency — large contexts add seconds of prefill time
- When the same document set is queried repeatedly — a vector index is more economical than re-sending 500K tokens each time
- When the relevant information is localized — use targeted retrieval and a shorter context for 10x lower cost

## Native Computer Use API: Architecture, OSWorld 75% Benchmark, and Getting Started

GPT-5.4's computer use capability is a first-class API feature that enables the model to observe a desktop environment through screenshots and issue mouse clicks, keyboard input, and application commands — without requiring custom automation code like Selenium or Playwright. At 75.0% on the OSWorld-Verified benchmark (surpassing the 72.4% human expert baseline), GPT-5.4 is the most capable general-purpose model for desktop automation as of 2026. The architecture is straightforward: you send the model a screenshot (base64 or URL), describe a task, and receive a structured action response that your client executes. The model then receives the updated screenshot and continues the loop until the task is complete. GPT-5.4 processes screenshots at full resolution with native vision — no downscaling or OCR preprocessing required — which significantly improves accuracy on small UI elements like checkboxes, dropdown menus, and text fields that trip up lower-resolution approaches.

### Computer Use API Quick Start

```python
import base64
from PIL import ImageGrab

def get_screenshot() -> str:
    img = ImageGrab.grab()
    img.save("/tmp/screen.png")
    with open("/tmp/screen.png", "rb") as f:
        return base64.b64encode(f.read()).decode()

def computer_use_step(screenshot_b64: str, task: str, history: list) -> dict:
    response = client.chat.completions.create(
        model="gpt-5.4",
        tools=[{"type": "computer_use"}],
        tool_choice="required",
        messages=history + [
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{screenshot_b64}"}},
                    {"type": "text", "text": task}
                ]
            }
        ]
    )
    return response.choices[0].message

# Example: automate a browser form
history = [{"role": "system", "content": "You control a desktop. Complete tasks by clicking and typing."}]
task = "Open Chrome, navigate to example.com, and fill in the contact form with test data."

screenshot = get_screenshot()
action = computer_use_step(screenshot, task, history)
print(action)  # {"tool_calls": [{"type": "computer_use", "action": "click", "x": 450, "y": 230}]}
```

### What Computer Use Replaces

GPT-5.4's computer use scores above human baseline on OSWorld tasks that previously required brittle selector-based automation (Selenium, Playwright) or specialized RPA tools (UiPath, Automation Anywhere). For exploratory or exception-heavy workflows — where the UI state varies and hard-coded selectors break — the vision-driven approach is substantially more robust. For high-volume, predictable workflows with stable UIs, traditional automation remains faster and cheaper.

## Full Tool Support Overview: Function Calling, Tool Search, MCP, Hosted Shell

GPT-5.4 supports the complete OpenAI tool ecosystem: function calling (same syntax as gpt-4o), tool search for dynamic capability discovery, Model Context Protocol (MCP) for structured external integrations, hosted shell for sandboxed code execution, and computer use for desktop automation. All tools can be combined in a single request — the model reasons over which tools to invoke and in what order, making it a capable orchestrator for multi-step agentic pipelines. Tool search is new in gpt-5.4: rather than defining all available tools upfront, you can expose a tool catalog and let the model retrieve and call relevant tools dynamically, significantly reducing prompt size for large tool ecosystems.

Function calling syntax is unchanged from previous models:

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current weather for a location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string", "description": "City name"},
                    "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]}
                },
                "required": ["location"]
            }
        }
    }
]

response = client.chat.completions.create(
    model="gpt-5.4",
    tools=tools,
    messages=[{"role": "user", "content": "What's the weather in Tokyo?"}]
)
```

MCP integration allows GPT-5.4 to connect to external systems (databases, APIs, file systems) through a standardized protocol, enabling persistent agent sessions with consistent tool interfaces across turns.

## GPT-5.4 API Pricing Deep Dive: Standard vs. Pro vs. Long-Context Tiers

GPT-5.4 pricing has three dimensions that developers must account for: model tier (standard vs. pro), context length (standard vs. long-context surcharge), and output volume. Standard gpt-5.4 costs $2.50 per million input tokens and $15 per million output tokens — roughly 2x the cost of gpt-4o at launch but with substantially higher capability. GPT-5.4-pro costs $30/$180 per million input/output tokens, a 12x premium over standard, justified for regulated industries (legal, finance, healthcare) where higher accuracy reduces downstream error costs. The long-context surcharge applies beyond 272,000 input tokens: input pricing doubles to $5/M and output pricing rises to $22.50/M for gpt-5.4 standard. For gpt-5.4-pro, long-context rates scale proportionally. This pricing structure rewards efficient context management — trimming system prompts, compressing conversation history, and using retrieval to avoid unnecessary long-context billing is directly profitable at scale.

### Cost Estimation Examples

| Workload | Model | Tokens | Estimated Cost |
|---|---|---|---|
| Simple Q&A | gpt-5.4 | 1K in / 500 out | ~$0.010 |
| Document summary (50 pages) | gpt-5.4 | 40K in / 2K out | ~$0.130 |
| Full codebase review (400K tokens) | gpt-5.4 | 400K in / 5K out | ~$2.075 |
| Enterprise contract analysis | gpt-5.4-pro | 200K in / 10K out | ~$7.80 |

For high-volume workloads (>10M tokens/day), OpenAI offers volume pricing tiers — contact OpenAI sales for enterprise pricing.

### When to Choose gpt-5.4 vs. gpt-5.4-pro

Choose **gpt-5.4** for: API integrations, code generation, agentic workflows, content generation, and any workload where errors are recoverable.

Choose **gpt-5.4-pro** for: legal document review, financial modeling, medical information synthesis, or any domain where a single error has significant downstream cost exceeding the $30/M input premium.

## GPT-5.4 vs. Claude Opus 4.6 vs. Gemini 3.1 Pro: Benchmark Comparison

GPT-5.4 leads on computer use and knowledge work benchmarks but faces strong competition from Claude Opus 4.6 (Anthropic) and Gemini 3.1 Pro (Google) on coding and long-document reasoning tasks. On the OSWorld-Verified benchmark, GPT-5.4 scores 75.0% — Claude Opus 4.6 scores approximately 68% and Gemini 3.1 Pro reaches roughly 62%, making GPT-5.4 the clear leader for desktop automation. On SWE-bench Pro (real-world software engineering), GPT-5.4 at xhigh reasoning scores 57.7%, which is competitive with but not dominant over Claude Opus 4.6's reported 55–58% range. On GDPval (knowledge work across 44 occupations), GPT-5.4 leads at 83% versus the mid-70s for competitors. For developers choosing a flagship model, the decision typically hinges on use case: GPT-5.4 for computer use and knowledge work, Claude Opus 4.6 for long-document fidelity and nuanced instruction following.

### Benchmark Comparison Table

| Benchmark | GPT-5.4 | Claude Opus 4.6 | Gemini 3.1 Pro |
|---|---|---|---|
| OSWorld (computer use) | **75.0%** | ~68% | ~62% |
| SWE-bench Pro (coding) | **57.7%** | ~56% | ~53% |
| GDPval (knowledge work) | **83.0%** | ~76% | ~74% |
| Human baseline (OSWorld) | 72.4% | — | — |

Note: Claude Opus 4.6 and Gemini 3.1 Pro figures are approximations based on published benchmarks as of Q1 2026; official numbers may vary by evaluation methodology.

### API Cost Comparison

At standard pricing, GPT-5.4 ($2.50/M input) is competitively priced against Claude Opus 4.6 ($3.00/M input) and Gemini 3.1 Pro ($2.00/M input). GPT-5.4-pro ($30/M input) is positioned above all standard competitor offerings and targets enterprise use cases where accuracy premium is justifiable.

## Best Practices and Production Recommendations

Production-ready GPT-5.4 deployments share several patterns that distinguish robust integrations from fragile prototypes. The most important is **matching reasoning effort to task complexity at the routing layer**: use a lightweight classifier (even gpt-5.4-mini at `none` effort) to route incoming requests to the appropriate effort level before forwarding to gpt-5.4. This alone typically reduces per-request cost by 30–50% without measurable quality loss at the application level. Second, **implement structured output validation** for all tool-calling workflows — gpt-5.4 is highly reliable but not infallible, and downstream systems should validate JSON structure before acting on tool call arguments. Third, **monitor long-context billing proactively**: instrument token counts before each request and alert when a conversation history approaches the 272K threshold so you can summarize or truncate before incurring the 2x surcharge. Finally, for computer use agents, implement **screenshot diffing** to detect when an action had no visible effect — this prevents infinite loops where the model keeps clicking a button that isn't registering.

### Production Checklist

- Set `reasoning.effort` explicitly — don't rely on defaults for cost-sensitive workloads
- Use `stream: true` for all requests with `high` or `xhigh` effort to improve perceived latency
- Track `usage.total_tokens` per response and alert above 272K input
- Validate tool call JSON with a schema before executing side effects
- For computer use: implement action timeout + screenshot diff to detect stuck states
- Cache frequent system prompts with the Prompt Caching API to reduce input token costs
- Use `gpt-5.4-mini` for pre-filtering and routing, gpt-5.4 for execution

### Migration from gpt-4o in 3 Steps

1. Update `model="gpt-4o"` to `model="gpt-5.4"` in all API calls
2. Add `reasoning={"effort": "medium"}` as a default; tune per endpoint based on latency requirements
3. Test with your existing prompt suite — gpt-5.4 is backward-compatible but often returns longer, more detailed responses at `medium`+ effort, which may affect downstream parsers

---

## FAQ

**What is GPT-5.4 and when was it released?**

GPT-5.4 is OpenAI's most capable general-purpose model as of 2026, released on March 5, 2026. It combines a 1,050,000-token context window, five reasoning effort levels (`none` through `xhigh`), native computer use, and full tool support in a single Chat Completions API model.

**How do I access the GPT-5.4 API?**

Access GPT-5.4 through the standard OpenAI Chat Completions API by setting `model="gpt-5.4"`. It requires an OpenAI API key with access to GPT-5.4 (available to all paid API tiers as of Q2 2026). No endpoint changes or new authentication methods are needed.

**What is the `reasoning.effort` parameter and which level should I use?**

`reasoning.effort` controls how much internal chain-of-thought reasoning the model performs. Use `low` or `none` for classification and simple extraction, `medium` for most conversational and summarization tasks, and `high` or `xhigh` for complex code synthesis, agentic planning, or high-stakes analysis. xhigh costs 3–5x more than low but delivers measurably better accuracy on complex tasks.

**How much does GPT-5.4 cost compared to GPT-5.4-pro?**

Standard gpt-5.4 costs $2.50 per million input tokens and $15 per million output tokens. GPT-5.4-pro costs $30/$180 per million input/output tokens — 12x more expensive but optimized for accuracy-critical enterprise workloads. Input tokens beyond 272K are billed at 2x the standard rate for both variants.

**Can GPT-5.4 replace Selenium or Playwright for browser automation?**

For exploratory, exception-heavy, or visually complex automation tasks, GPT-5.4's computer use (75% OSWorld accuracy) is a strong alternative to selector-based automation. For high-volume, stable UI workflows where selectors are reliable, traditional automation remains faster and cheaper. Most teams use GPT-5.4 computer use for the hard cases — onboarding flows, exception handling, testing dynamic UIs — while keeping Playwright for predictable, high-frequency tasks.
