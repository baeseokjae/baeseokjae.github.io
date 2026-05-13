---
title: "DeepEval Tutorial 2026: Pytest-Native LLM Evaluation for Production AI"
date: 2026-05-12T21:03:44+00:00
tags: ["deepeval", "llm-evaluation", "pytest", "rag", "ai-testing", "ci-cd"]
description: "Step-by-step DeepEval tutorial covering pytest-native LLM testing, RAG metrics, G-Eval, agent evaluation, and CI/CD integration in 2026."
draft: false
cover:
  image: "/images/deepeval-tutorial-2026.png"
  alt: "DeepEval Tutorial 2026: Pytest-Native LLM Evaluation for Production AI"
  relative: false
schema: "schema-deepeval-tutorial-2026"
---

DeepEval is an open-source, pytest-native framework for evaluating LLM outputs using 50+ research-backed metrics — no labeled data required for most production use cases. Install it with `pip install deepeval`, write test cases like Python unit tests, and run `deepeval test run` from the CLI to catch regressions before they reach users.

## What Is DeepEval and Why Pytest-Native LLM Evaluation Matters in 2026

DeepEval is an open-source LLM evaluation framework built by Confident AI that treats model quality testing the same way software engineers treat unit testing: write test cases in Python, run them from the CLI, and fail the build when outputs degrade. As of May 2026, DeepEval has 15,291 GitHub stars, 250+ contributors, and is used by 150,000+ developers running over 100 million daily evaluations — including more than 50% of Fortune 500 companies for LLM quality assurance. The Apache 2.0 license means no usage restrictions in commercial products.

The "pytest-native" design is the key differentiator from notebook-centric tools like RAGAS or Weights & Biases Weave. Your evaluation suite lives in `tests/` alongside your application code. Every push triggers the same CI pipeline. When a model upgrade changes tone subtly enough to tank your faithfulness score, you catch it in the PR — not in a Monday incident review. In 2026, evaluation woven into CI/CD pipelines is table stakes for teams shipping production LLM features; DeepEval is the framework that makes that pattern feel natural to Python engineers already fluent in pytest.

## How to Install DeepEval and Configure Your Evaluation Environment

DeepEval installs as a standard Python package and requires only an LLM API key to run most metrics out of the box. The evaluation judge defaults to GPT-4o but supports any OpenAI-compatible endpoint, Anthropic Claude, or a local Ollama model — making it viable in air-gapped deployments. The setup takes under five minutes for a working evaluation harness against a real application endpoint.

```bash
pip install deepeval
```

Set your judge model credentials:

```bash
export OPENAI_API_KEY="sk-..."
# or for Claude-based judgment:
export ANTHROPIC_API_KEY="sk-ant-..."
```

Initialize the project (creates `.deepeval` config in current directory):

```bash
deepeval login  # optional: connects to Confident AI cloud dashboard
```

For teams using Anthropic Claude as the judge, configure the model in code:

```python
from deepeval.models import DeepEvalBaseLLM
from anthropic import Anthropic

class ClaudeJudge(DeepEvalBaseLLM):
    def __init__(self):
        self.client = Anthropic()

    def load_model(self):
        return self.client

    def generate(self, prompt: str) -> str:
        response = self.client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text

    async def a_generate(self, prompt: str) -> str:
        return self.generate(prompt)

    def get_model_name(self) -> str:
        return "claude-sonnet-4-6"
```

### Verifying the Installation

Run `deepeval test run` on a trivial test to confirm the environment is wired up:

```bash
deepeval test run tests/test_smoke.py -v
```

A passing smoke test confirms your judge model is reachable, metrics can score, and the CLI finds your test files. Add this as a pre-push hook or the first step in your CI pipeline.

## Core Concepts: LLMTestCase, EvaluationDataset, and Metrics

DeepEval's core data structure is `LLMTestCase`, a typed container that holds everything needed to evaluate one model interaction: the input, the model's actual output, an optional expected output, and any retrieval context for RAG pipelines. Metrics accept `LLMTestCase` instances directly, which means evaluation logic is decoupled from your application code — you can swap metrics without touching the test runner. `EvaluationDataset` wraps a list of test cases and integrates with `@pytest.mark.parametrize` to run the full suite as individual pytest items, each with its own pass/fail result in the test report. DeepEval recommends keeping metric counts per case to 2–3 generic system metrics plus 1–2 use-case-specific metrics — five metrics maximum per evaluation run — to avoid combinatorial noise in your signal.

```python
from deepeval.test_case import LLMTestCase
from deepeval.dataset import EvaluationDataset

# Single test case
case = LLMTestCase(
    input="What is the capital of France?",
    actual_output="The capital of France is Paris.",
    expected_output="Paris",
    retrieval_context=["France is a country in Western Europe. Its capital city is Paris."]
)

# Dataset for bulk evaluation
dataset = EvaluationDataset(test_cases=[
    LLMTestCase(
        input="Explain gradient descent",
        actual_output=my_llm("Explain gradient descent"),
        expected_output=None,  # referenceless metrics don't need this
    ),
    # ... more cases
])
```

### Running Assertions with assert_test()

`assert_test()` is the primitive that connects DeepEval metrics to pytest:

```python
import pytest
from deepeval import assert_test
from deepeval.metrics import AnswerRelevancyMetric

metric = AnswerRelevancyMetric(threshold=0.7, model="gpt-4o")

@pytest.mark.parametrize("test_case", dataset)
def test_answer_quality(test_case):
    assert_test(test_case, [metric])
```

When the metric score drops below `threshold`, `assert_test()` raises `AssertionError` with the exact score and reason — the same failure contract as any other pytest assertion.

## Built-in Metrics Deep Dive — RAG, Hallucination, and Answer Relevancy

DeepEval ships 50+ research-backed metrics covering RAG pipelines, hallucination detection, safety, conversational systems, and agent behavior. The five core RAG metrics each catch a distinct failure mode: `AnswerRelevancyMetric` checks whether the response addresses the query, `FaithfulnessMetric` verifies claims are grounded in retrieved context, `ContextualPrecisionMetric` scores whether retrieved chunks are actually relevant, `ContextualRecallMetric` checks whether necessary information was retrieved at all, and `ContextualRelevancyMetric` evaluates overall context quality. For hallucination detection specifically, `HallucinationMetric` uses an LLM judge to identify statements in the output that contradict or go beyond the provided context — a critical gate before responses reach end users. In production RAG systems, running all five metrics on a sample of daily traffic catches retrieval drift that would otherwise surface only through user complaints weeks later.

```python
from deepeval.metrics import (
    AnswerRelevancyMetric,
    FaithfulnessMetric,
    ContextualPrecisionMetric,
    ContextualRecallMetric,
    HallucinationMetric,
)

# RAG pipeline evaluation
rag_case = LLMTestCase(
    input="What causes transformer attention to scale quadratically?",
    actual_output=rag_pipeline.query("What causes transformer attention to scale quadratically?"),
    retrieval_context=rag_pipeline.retrieve("What causes transformer attention to scale quadratically?"),
)

metrics = [
    AnswerRelevancyMetric(threshold=0.7),
    FaithfulnessMetric(threshold=0.8),
    ContextualPrecisionMetric(threshold=0.6),
    HallucinationMetric(threshold=0.1),  # lower is better; fail above 10% hallucination rate
]

def test_rag_quality():
    assert_test(rag_case, metrics)
```

### Hallucination Detection in Practice

`HallucinationMetric` scores from 0.0 (no hallucination) to 1.0 (complete hallucination). The `threshold` parameter is an upper bound — set it to `0.1` to fail any case where more than 10% of the output contains ungrounded claims. Pair with `FaithfulnessMetric` (a lower bound measuring how well the output adheres to context) for full coverage of grounding failures.

```python
hallucination_metric = HallucinationMetric(
    threshold=0.1,
    model="gpt-4o",
    include_reason=True,  # surfaces which specific claims triggered the failure
)
```

## G-Eval: Flexible LLM-as-a-Judge Scoring with Custom Criteria

G-Eval is DeepEval's most versatile metric: define evaluation criteria in plain English, and DeepEval uses chain-of-thought (CoT) decomposition to automatically build a scoring rubric without hand-crafted examples or labeled datasets. Unlike rigid rule-based metrics, G-Eval handles subjective quality dimensions — tone, technical depth, safety posture, brand voice adherence — that don't map cleanly to predefined metrics. The approach follows the G-Eval research paper: the LLM judge first generates evaluation steps from your criteria description, then scores each case against those steps on a 0–1 continuous scale. In practice, this means a product team can add a "sounds like a senior engineer, not a chatbot" criterion in an afternoon without writing any scoring code. G-Eval's CoT reasoning also surfaces actionable failure explanations rather than just a score, making it practical for debugging regression batches during model upgrades.

```python
from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCaseParams

# Custom criterion: evaluate technical depth for a developer tool
technical_depth_metric = GEval(
    name="TechnicalDepth",
    criteria=(
        "Evaluate whether the response demonstrates genuine technical depth. "
        "A high-scoring response: uses precise terminology, provides concrete examples, "
        "acknowledges tradeoffs, and avoids vague generalities. "
        "A low-scoring response: uses buzzwords without explanation, makes unsupported claims, "
        "or oversimplifies complex topics."
    ),
    evaluation_params=[
        LLMTestCaseParams.INPUT,
        LLMTestCaseParams.ACTUAL_OUTPUT,
    ],
    threshold=0.6,
    model="gpt-4o",
)

case = LLMTestCase(
    input="Explain why vector databases use HNSW indexing",
    actual_output=my_llm("Explain why vector databases use HNSW indexing"),
)

def test_technical_depth():
    assert_test(case, [technical_depth_metric])
```

### When to Use G-Eval vs. Built-in Metrics

Use built-in metrics (`FaithfulnessMetric`, `AnswerRelevancyMetric`) when the criterion maps directly to a researched definition — they're faster and more reproducible. Use G-Eval when you need to capture something domain-specific or stylistic that doesn't have a standard definition. G-Eval adds 1–3 seconds per evaluation due to CoT generation; run it on sampled batches in production rather than every request.

## Agent Evaluation — StepEfficiency, Tool Correctness, and Task Completion

Agent evaluation is the fastest-growing segment of LLM testing in 2026, and DeepEval's agent-specific metrics are purpose-built for multi-step agentic systems. `StepEfficiencyMetric` is particularly important for production cost control: it penalizes redundant tool calls and unnecessary reasoning loops that inflate token usage without improving output quality. A 10-step agent completing a task solvable in 3 steps is a latency and cost problem even if the final answer is correct. `ToolCorrectnessMetric` evaluates whether the agent called the right tools with correct arguments, and `TaskCompletionMetric` measures whether the agent's final output actually satisfied the original goal. Together, these three metrics give you correctness, efficiency, and goal-orientation signals — the minimum viable coverage for any production agent system.

```python
from deepeval.test_case import LLMTestCase, ToolCall
from deepeval.metrics import (
    TaskCompletionMetric,
    ToolCorrectnessMetric,
)

agent_case = LLMTestCase(
    input="Find all open GitHub issues labeled 'bug' and summarize them",
    actual_output=agent.run("Find all open GitHub issues labeled 'bug' and summarize them"),
    tools_called=[
        ToolCall(name="github_search", input={"query": "is:issue is:open label:bug"}),
        ToolCall(name="summarize", input={"text": "...issues content..."}),
    ],
    expected_tools=[
        ToolCall(name="github_search", input={"query": "is:issue is:open label:bug"}),
        ToolCall(name="summarize"),
    ],
)

agent_metrics = [
    TaskCompletionMetric(threshold=0.8),
    ToolCorrectnessMetric(threshold=0.9),
]

def test_agent_task():
    assert_test(agent_case, agent_metrics)
```

### Measuring Step Efficiency in Long Chains

For agents with reasoning traces, capture the full tool call sequence in `tools_called` and set `StepEfficiencyMetric` with a `threshold` matching your acceptable overhead ratio. A threshold of `0.7` means the agent must complete the task in no more than ~43% more steps than the theoretical minimum:

```python
from deepeval.metrics import StepEfficiencyMetric

efficiency = StepEfficiencyMetric(threshold=0.7)
```

## How to Integrate DeepEval into CI/CD Pipelines with GitHub Actions

Integrating DeepEval into GitHub Actions turns your evaluation suite into a quality gate — pull requests that regress LLM output quality below your thresholds fail the CI check and cannot merge without explicit override. This is the same pattern software teams use for code coverage thresholds, applied to model quality metrics. The key implementation detail: DeepEval exits with a non-zero status code when any metric threshold is violated, which GitHub Actions interprets as a build failure. For API cost control, scope CI evaluations to a representative sample (20–50 cases) rather than the full production dataset; run full-dataset evaluations nightly or on release tags. In 2026, teams shipping features on top of third-party LLM APIs — where the underlying model can be silently updated by the provider — treat these CI gates as insurance against unannounced model behavior changes degrading user experience.

```yaml
# .github/workflows/llm-eval.yml
name: LLM Evaluation

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

jobs:
  evaluate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install dependencies
        run: |
          pip install deepeval
          pip install -r requirements.txt

      - name: Run DeepEval suite
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: |
          deepeval test run tests/eval/ -v --exit-on-first-failure

      - name: Upload evaluation report
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: deepeval-report
          path: .deepeval/
```

### Caching Evaluation Results to Reduce API Costs

DeepEval supports result caching via `.deepeval/cache/`. Enable it to skip re-evaluating unchanged test cases between CI runs:

```python
from deepeval import evaluate

results = evaluate(
    test_cases=dataset,
    metrics=metrics,
    use_cache=True,      # skip cases with identical inputs/outputs from prior runs
    run_async=True,      # parallel evaluation — 3-5x faster on large suites
)
```

## Production Evaluation Patterns — Async, Referenceless, and Threshold-Based

Production LLM evaluation differs from offline testing in three ways: it must be non-blocking, it usually has no ground-truth labels, and it needs threshold-based alerting rather than binary pass/fail. DeepEval's async evaluation API runs metric scoring in a background task without blocking the response path — users get their answer immediately while evaluation happens asynchronously. Referenceless metrics like `AnswerRelevancyMetric` and `FaithfulnessMetric` score quality against the input and retrieved context alone, requiring no hand-labeled expected outputs. This means you can evaluate 100% of production traffic on day one without building a labeling pipeline first. Threshold-based alerting integrates with the Confident AI dashboard or your own observability stack: when the rolling average score for a metric drops below a threshold over a time window, trigger an alert before users notice the degradation. This is the closest LLM operations comes to classical SLO monitoring.

```python
import asyncio
from deepeval.metrics import AnswerRelevancyMetric, FaithfulnessMetric

async def evaluate_production_response(user_input: str, llm_output: str, context: list[str]):
    case = LLMTestCase(
        input=user_input,
        actual_output=llm_output,
        retrieval_context=context,
    )

    metrics = [
        AnswerRelevancyMetric(threshold=0.7, async_mode=True),
        FaithfulnessMetric(threshold=0.8, async_mode=True),
    ]

    # Non-blocking: scores are computed in background
    tasks = [m.a_measure(case) for m in metrics]
    scores = await asyncio.gather(*tasks)

    # Log to your observability stack
    for metric, score in zip(metrics, scores):
        log_metric(name=metric.__name__, score=score, input=user_input)

    return scores
```

### Sampling Strategy for Cost-Effective Production Monitoring

Evaluating every production request with LLM-as-a-Judge metrics is expensive. Use a stratified sampling approach: evaluate 100% of low-confidence outputs (detect these via your model's logprobs or a cheap classifier), 10% of standard traffic uniformly, and 100% of flagged conversations (user thumbs-down, error states, long sessions). This targets evaluation budget at the cases most likely to reveal real problems.

## DeepEval vs RAGAS vs TruLens vs Braintrust — When to Use Each

DeepEval is the right choice when your team thinks in code, wants CI/CD integration as a first-class feature, and needs broad metric coverage across RAG, agents, safety, and custom criteria. It is not the only strong option in 2026, and picking the wrong tool creates friction that undermines adoption. RAGAS is purpose-built for RAG pipeline evaluation with deeper retrieval-chain diagnostics than DeepEval, but it lacks agent metrics and has no native CI/CD integration. TruLens focuses on observability integration — it pairs well with LangChain and LlamaIndex and provides tracing alongside eval, but its metric library is narrower. Braintrust (reviewed separately) prioritizes product and PM dashboards with A/B experiment workflows and a polished web UI, making it the right choice when non-engineers need to participate in evaluation — but it's a managed SaaS platform, not an open-source library. The decision usually comes down to who runs evaluations and where they live: engineers in CI choose DeepEval, data scientists in notebooks choose RAGAS, product teams in dashboards choose Braintrust.

| Framework | Best For | CI/CD Native | Open Source | Agent Metrics | RAG Depth |
|-----------|----------|:---:|:---:|:---:|:---:|
| **DeepEval** | Code-first engineering teams | ✅ | ✅ | ✅ | Good |
| **RAGAS** | RAG pipeline specialists | ❌ | ✅ | ❌ | Excellent |
| **TruLens** | LangChain/LlamaIndex observability | Partial | ✅ | Partial | Good |
| **Braintrust** | Product/PM A-B testing dashboards | Partial | ❌ | Limited | Good |

### Migration Path from RAGAS to DeepEval

If your team currently uses RAGAS, DeepEval's RAG metrics cover the same ground and the migration is mostly a data-structure swap. Replace `ragas.metrics` imports with `deepeval.metrics`, convert your evaluation rows to `LLMTestCase` objects, and wrap each case in `assert_test()`. The pytest harness handles the rest. Teams that migrate typically report better CI integration and broader metric coverage, at the cost of RAGAS's more granular retrieval-chain attribution.

---

## Frequently Asked Questions

**Q: Does DeepEval require internet access or a specific LLM API to run?**

DeepEval requires an LLM judge to score most metrics — by default it uses OpenAI GPT-4o. However, you can configure any OpenAI-compatible endpoint, including local Ollama models, using the `DeepEvalBaseLLM` base class. For completely offline evaluation, point the judge at a local model serving an OpenAI-compatible API (e.g., `ollama serve`). The `--model` parameter accepts a custom model class at the CLI level.

**Q: How do I handle flaky evaluation results caused by LLM judge nondeterminism?**

Set `temperature=0` on your judge model for maximum reproducibility. For metrics where score variance still matters, run each case through the metric 3 times and take the median — DeepEval supports `n_retries` on most metrics for this purpose. In CI, treat scores below threshold by more than 0.05 as definite failures; scores within 0.05 of the threshold as warnings requiring human review rather than automatic build failures.

**Q: Can DeepEval evaluate streaming LLM responses?**

DeepEval evaluates complete outputs, not streams. Accumulate the full streamed response into a string before constructing the `LLMTestCase`. For production monitoring with streaming responses, buffer the output in your application layer, evaluate asynchronously after streaming completes, and log the score to your observability stack. The latency impact on the user experience is zero.

**Q: What's the cheapest way to run DeepEval on a large evaluation dataset?**

Enable caching (`use_cache=True`) to skip re-evaluating unchanged cases. Use async evaluation (`run_async=True`) to parallelize API calls. Choose `gpt-4o-mini` or `claude-haiku-4-5` as the judge model for lower-stakes metrics — they score within 5-8% of GPT-4o on most standard metrics while costing 10-20x less. Reserve the strongest judge model for G-Eval and custom criteria that require deeper reasoning.

**Q: How does DeepEval handle multi-turn conversation evaluation?**

DeepEval supports conversational evaluation through `ConversationalTestCase`, which wraps a list of `LLMTestCase` objects representing each turn. Conversational metrics like `ConversationRelevancyMetric` and `KnowledgeRetentionMetric` score the full dialogue arc rather than individual turns. This is essential for evaluating chatbots, support agents, and multi-step assistants where quality degrades across turns rather than within a single response.
