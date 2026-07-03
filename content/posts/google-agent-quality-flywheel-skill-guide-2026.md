---
title: "Google Agent Quality Flywheel Skill Guide 2026: Testing and Grading Agents"
date: 2026-04-13T12:00:00+00:00
tags: ["AI agents", "Google ADK", "evaluation"]
description: "Build a Google agent quality flywheel skill with ADK evalsets, trace review, CI gates, and Vertex AI evaluation."
draft: false
cover:
  image: "/images/google-agent-quality-flywheel-skill-guide-2026.png"
  alt: "Google Agent Quality Flywheel Skill Guide 2026"
  relative: false
schema: "schema-google-agent-quality-flywheel-skill-guide-2026"
---

A Google agent quality flywheel skill is a reusable workflow that turns agent traces into graded eval cases, runs them locally and in CI, then feeds production failures back into the test suite. For coding agents, the goal is simple: stop trusting "done" and start checking behavior, tool use, and real state changes.

## What is a Google agent quality flywheel skill?

The phrase "Google agent quality flywheel skill" is not an official Google product name. I use it as a practical pattern for teams building agents with Google Agent Development Kit (ADK), Vertex AI Gen AI Evaluation, and a coding agent that can maintain its own eval suite.

The skill has four parts:

| Part | What it does | Where it runs |
| --- | --- | --- |
| Trace capture | Records prompts, tool calls, arguments, outputs, retries, and state changes | Local, CI, production |
| Grading | Scores final answers, trajectories, tool arguments, safety, and task completion | ADK evalsets, pytest, Vertex AI |
| Regression loop | Converts failures into reusable eval cases | Local repo and CI |
| Release gate | Blocks risky agent changes before deployment | CI/CD and experiment review |

I've found that the important shift is ownership. The coding agent should not only change code. It should notice when a task exposes a new failure mode, add that case to the evalset, and make the next run harder to break.

That is the flywheel: trace, grade, fix, gate, monitor, repeat.

## Why do coding agents need evals instead of only unit tests?

Unit tests are still necessary, but they do not answer the agent-quality question. A coding agent can pass the repository test suite and still behave badly.

Common examples:

- It edits the right file but ignores the user's constraint.
- It runs the wrong command and reports success anyway.
- It calls the right tool with a subtly wrong argument.
- It fixes one case by adding brittle special handling.
- It says the issue is done without creating the expected PR, comment, file, or API update.

Google ADK's evaluation docs make this distinction clear: agent evaluation needs both final-response quality and trajectory quality. That matters because agents are nondeterministic. Two runs with the same prompt may take different paths, call different tools, or stop at different points.

In practice, I split tests into two layers. Repository tests prove the product still works. Agent evals prove the agent did the right work in the right way.

For a coding agent, "right way" does not mean an exact sequence for every task. It means the trace contains enough evidence: relevant files read, correct tools used, command output interpreted correctly, expected state changed, and no unsupported claim in the final response.

I use the same distinction when designing [AI agent CI/CD evaluation](/posts/ai-agent-ci-cd-evaluation/): product correctness and agent behavior need separate gates because they fail in different ways.

## How does the quality flywheel work?

The loop is small enough to run every day:

1. Capture the trace from a real coding-agent task.
2. Review failures manually until the pattern is clear.
3. Convert the failure into an ADK evalset case.
4. Add objective checks where possible.
5. Use rubric or LLM-as-judge scoring only where judgment is required.
6. Run evals locally before changing prompts, tools, or skills.
7. Run evals in CI before shipping.
8. Monitor production traces and feed misses back into the suite.

LangChain's agent evaluation checklist recommends manually reviewing 20 to 50 real traces before building heavy eval infrastructure. That matches my experience. If you automate before you understand the traces, you usually automate the wrong question.

Start with a spreadsheet or a small JSONL file. Label failures by hand. Ask what actually went wrong:

- Did the agent misunderstand the task?
- Did it skip context gathering?
- Did it use the wrong tool?
- Did it pass the wrong arguments?
- Did it fail to verify the state change?
- Did the final answer overclaim?

Once the categories repeat, automate them.

## How do you build the inner loop with Google ADK evalsets?

Google ADK gives you the inner loop: local, fast, developer-owned evaluation. ADK supports test files for unit-test-like checks, evalsets for longer scenarios, Web UI evaluation, pytest, CLI evaluation, and conformance testing.

The most useful default ADK idea is that final answer matching is not enough. ADK includes built-in criteria for tool trajectory score, response match, semantic final response match, rubric-based response quality, rubric-based tool-use quality, hallucination, safety, multi-turn task success, and multi-turn trajectory quality.

The default criteria are intentionally strict when no custom criteria are supplied: `tool_trajectory_avg_score` at `1.0` and `response_match_score` at `0.8`. I like that for workflows with one correct path, such as "read this issue, update this file, then patch this exact status." I relax it for coding tasks where multiple valid implementation paths exist.

A starter local command usually looks like this:

```bash
adk eval \
  --agent ./agents/coding_agent \
  --eval_set ./evals/coding_agent_regressions.json
```

If your repo uses pytest as the quality gate, wrap the ADK evals so they run beside normal tests:

```python
# tests/test_agent_regressions.py
import subprocess


def test_coding_agent_evalset_passes():
    result = subprocess.run(
        [
            "adk",
            "eval",
            "--agent",
            "./agents/coding_agent",
            "--eval_set",
            "./evals/coding_agent_regressions.json",
        ],
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
```

That is deliberately boring. I want the first version to be easy for any developer to run before touching prompts, tool policies, or skills.

## What should you grade in a coding-agent trace?

I grade seven things. Not every eval case needs all seven, but the panel keeps the team honest.

| Metric | What it catches | Best grader |
| --- | --- | --- |
| Final answer quality | Did the agent answer the user accurately? | Rubric or semantic match |
| Tool trajectory | Did it use the right class of tools in a valid order? | ADK trajectory score |
| Argument correctness | Were file paths, issue IDs, commands, and API payloads correct? | Code-based checks |
| State change verification | Did the expected file, test result, PR, or issue status change? | Code-based checks |
| Cost and latency | Did it solve the task with reasonable work? | Trace metadata |
| Safety and hallucination | Did it invent facts or make unsafe changes? | Rubric plus human review |
| Multi-turn memory | Did it preserve constraints across turns? | Multi-turn eval |

DeepEval frames agent metrics across reasoning, action, and execution. That taxonomy is useful, but for coding agents I avoid grading hidden reasoning directly. I care about observable planning signals, tool choices, arguments, outputs, and final state.

Argument correctness deserves special attention. When building agent workflows, I ran into many cases where the agent chose the right tool and still failed:

```json
{
  "tool": "patch_issue",
  "arguments": {
    "issueId": "BLO-738",
    "status": "done"
  }
}
```

That looks plausible until the assigned task is the write subtask `BLO-740`, not the parent article issue `BLO-738`. A final-response grader may miss it. A code-based argument check will not.

## How should you use ADK Web and trace view?

Use trace view as the debugging interface, not as a dashboard you glance at after everything fails.

ADK trace inspection is valuable because it lets you inspect events, model requests, model responses, tool calls, graph flow, and intermediate outputs. When an eval fails, the question is rarely "was the final answer bad?" The better question is "where did the run become unrecoverable?"

I usually annotate the failed trace like this:

| Trace moment | Question |
| --- | --- |
| Initial plan | Did the agent understand the real task? |
| First context read | Did it inspect the right source of truth? |
| Tool selection | Did it choose the cheapest reliable tool? |
| Tool arguments | Were paths, IDs, and payloads correct? |
| Error handling | Did it adjust after a failed command or API response? |
| Verification | Did it prove the state changed? |
| Final message | Did it report only what it verified? |

This is also where I decide whether the regression case should be exact or flexible. Exact trajectory grading is appropriate for compliance-like flows. For software tasks, I usually prefer looser trajectory checks plus strict state checks.

For example, I do not care whether the agent reads a TypeScript component with `sed`, `rg`, or an IDE API. I care that it reads the relevant component before editing, applies a minimal patch, and runs a verification command that can catch the bug.

## How do conformance tests and CI gates protect the flywheel?

Conformance tests are the contract tests for the agent itself. They answer: "Does this agent still follow the operating rules we rely on?"

For a coding agent, I like conformance tests for rules such as:

- Do not mark an issue done before saving the required work product.
- Do not report tests as passing unless the command actually ran.
- Do not edit files outside the assigned scope.
- Do not use destructive git commands without explicit approval.
- Do not treat a final answer as proof of a side effect.

Then CI should run three levels of checks:

```yaml
name: agent-quality

on:
  pull_request:
    paths:
      - "agents/**"
      - "skills/**"
      - "evals/**"

jobs:
  evals:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -r requirements-dev.txt
      - run: pytest tests/test_agent_regressions.py
      - run: adk eval --agent ./agents/coding_agent --eval_set ./evals/conformance.json
```

The gate should be strict for regressions that previously hit production. For exploratory capability evals, I prefer reporting trends without blocking every PR. Capability evals answer "what can the agent do?" Regression evals answer "did we break something we already promised?"

That distinction keeps the team from turning every experiment into a release blocker.

## How does Vertex AI Gen AI Evaluation fit into the outer loop?

ADK is the local loop. Vertex AI Gen AI Evaluation is the outer loop when you need scale, autorater configuration, rubrics, batch evaluation, and experiment comparison.

Google Cloud's June 13, 2025 evaluation update emphasized evaluation across the gen AI lifecycle: model selection, prompt iteration, batch evaluation, autorater customization, rubric-driven grading, and production-oriented agent evaluation. For agents, Google calls out the same core issue: final-answer grading is insufficient. You also need to evaluate tool choice, action sequence, memory use, and trajectory.

In practice, I use Vertex AI when:

- The eval dataset is large enough that local runs are slow.
- Multiple prompt or model versions need side-by-side comparison.
- Product managers or reviewers need experiment history.
- Rubrics need centralized calibration.
- Production traces need batch scoring.

Vertex AI Experiments is useful here because it gives the team a history of agent versions, prompt changes, model choices, and scores. That prevents a common failure mode: somebody improves one demo path while quietly degrading five support paths.

I usually keep the inner-loop ADK suite small and sharp, then mirror the important cases into Vertex AI for broader comparison.

## How do you calibrate LLM judges before trusting scores?

LLM-as-judge is useful, but it is not a replacement for human judgment. I use it for subjective output quality, rubric adherence, and semantic matching. I do not use it for file existence, command exit codes, issue status updates, or exact API payloads.

LangChain recommends starting judge calibration with at least 20 labeled examples and growing toward roughly 100 examples for production confidence. That is a good rule of thumb. The smaller the dataset, the more I treat the judge as a reviewer suggestion rather than a release gate.

My calibration process is:

1. Label 20 to 50 traces manually.
2. Write a rubric with failure examples, not just success criteria.
3. Run the judge against the labeled set.
4. Compare disagreements.
5. Tighten the rubric or split ambiguous criteria.
6. Re-run until judge errors are understood.
7. Keep a human-review lane for borderline failures.

For coding agents, the best judge prompt includes the task, relevant trace excerpts, expected side effects, and the final response. Without the expected side effects, the judge tends to over-reward confident summaries.

This is the same failure pattern I covered in [LLM as judge agent evaluation](/posts/llm-as-judge-agent-evaluation/): a judge can grade writing quality while missing whether the system actually changed.

## What failure taxonomy should the skill include?

A reusable skill should include a small failure taxonomy. Without one, every failure becomes a vague "agent quality" complaint.

Here is the taxonomy I use for coding agents:

| Category | Example | Preferred fix |
| --- | --- | --- |
| Context miss | Agent edits before reading the relevant file | Add context-read conformance check |
| Tool misuse | Correct tool, wrong issue ID | Add argument validator |
| Verification gap | Agent says tests pass without running tests | Require command evidence |
| State mismatch | File saved but schema not saved | Add state-change check |
| Overclaiming | Final answer says "deployed" when only committed | Add final-answer rubric |
| Brittle path | Exact tool sequence required for flexible task | Relax trajectory, tighten outcome |
| Memory loss | Multi-turn constraint forgotten | Add multi-turn eval |
| Cost drift | Agent uses expensive model or redundant calls | Add budget metric |

The taxonomy matters because fixes live in different places. A context miss may need a skill update. A tool misuse may need schema validation. A verification gap may need a final-response policy. A brittle-path failure may mean the eval itself is wrong.

## What does a starter ADK evalset look like?

The exact ADK evalset format may vary by project setup, but the structure below shows the pieces I want in every coding-agent regression case: task, expected tool behavior, expected state change, and grading criteria.

```json
{
  "eval_set_id": "coding-agent-regressions",
  "cases": [
    {
      "id": "issue-write-handoff-001",
      "description": "Writer agent must save post and schema before marking issue done.",
      "input": {
        "user": "Write the assigned article from the research brief and hand off to publisher."
      },
      "expected": {
        "tool_trajectory": [
          "read_research_brief",
          "write_post_file",
          "write_schema_partial",
          "patch_issue_done",
          "assign_publish_subtask"
        ],
        "state_changes": [
          "content/posts/google-agent-quality-flywheel-skill-guide-2026.md exists",
          "layouts/partials/schema-google-agent-quality-flywheel-skill-guide-2026.html exists",
          "BLO-740 status is done"
        ]
      },
      "criteria": {
        "tool_trajectory_avg_score": 0.8,
        "response_match_score": 0.8,
        "rubric": [
          "Does not mark done before both files are written.",
          "Reports only verified work.",
          "Uses the assigned write issue, not the parent issue, for completion."
        ]
      }
    }
  ]
}
```

Notice the trajectory threshold is `0.8`, not `1.0`. That is intentional. I do not want to fail the run because the agent used an equivalent file-writing tool. I do want to fail the run if it patches the issue before saving the schema.

For stricter operational flows, I would raise trajectory matching to `1.0`. For implementation tasks, I usually keep path grading flexible and state grading strict.

## What mistakes make agent evals brittle?

The first mistake is exact-path grading for tasks with multiple valid solutions. If the eval says the agent must use one specific file-reading command, you will spend more time fighting the eval than improving the agent.

The second mistake is synthetic data overload. Synthetic cases are useful for coverage, but they are weak as the foundation. Real traces contain boring details that synthetic prompts miss: flaky commands, ambiguous issue descriptions, missing files, stale assumptions, and partial failures.

The third mistake is treating evals as a QA artifact instead of an engineering artifact. If the coding-agent team changes prompts, tools, or skills, that same team should own the regression suite.

The fourth mistake is using an LLM judge for objective checks. A judge should not decide whether a file exists. The filesystem can decide that. A judge should not infer whether an API call succeeded. The API response can decide that.

The fifth mistake is ignoring latency and cost. A coding agent that solves a task in 40 tool calls may pass correctness checks while still being unsuitable for production automation.

I saw this with [Google ADK agent evaluation](/posts/google-adk-agent-evaluation/): once teams add trace scoring, they often discover the agent was technically correct but operationally wasteful.

## What metric panel should production teams watch?

For production coding agents, I would start with this panel:

| Metric | Target |
| --- | --- |
| Regression eval pass rate | 100% on critical cases |
| Capability eval trend | Improving or stable by task family |
| Tool argument error rate | Near zero for IDs, paths, and API payloads |
| Verified completion rate | High and audited against real state changes |
| Overclaim rate | Zero tolerance on deployment, security, and data changes |
| Median tool calls per task | Stable or decreasing |
| P95 task latency | Within workflow budget |
| Human escalation rate | Tracked by task family |
| Production failure-to-eval conversion | Every confirmed failure becomes a case |

That last metric is the flywheel metric. If production failures do not become eval cases, the quality system is leaking.

Braintrust's 2026 observability guide makes a related point: production-ready traces need tool calls, reasoning steps or planning signals, state transitions, memory operations, timing, errors, retries, and identifiers. Without that trace substrate, you cannot reliably turn production behavior into offline evals.

For multi-agent systems, preserve parent-child span identifiers across handoffs. Otherwise, the downstream agent looks guilty when the upstream agent passed the wrong context.

## How do you put the skill into practice this week?

Start smaller than you think.

Day one: collect 20 real traces from coding-agent work. Do not build a dashboard. Read the traces.

Day two: label the top five failure categories. Separate objective failures from subjective failures.

Day three: create a small ADK evalset with five to ten high-signal cases. Include expected state changes, not just expected final text.

Day four: add a CI command that runs the regression evalset when `agents/`, `skills/`, or `evals/` changes.

Day five: calibrate one LLM judge rubric against human labels. Keep it advisory until the disagreements are boring and understood.

After that, add Vertex AI Gen AI Evaluation for larger batch runs, experiment comparison, and production trace scoring. Do not move everything to the outer loop too early. The inner loop needs to stay fast enough that developers use it before they push.

The skill itself should live beside the agent, not in a separate process document nobody opens. I would include:

- Evalset templates.
- Trace-review checklist.
- Failure taxonomy.
- Judge rubrics.
- CI commands.
- Rules for promoting production failures into regressions.
- Examples of good and bad final responses.

The payoff is not that the agent becomes perfect. It is that each real failure has somewhere to go. A month later, the same class of bug should be harder to ship.

## FAQ

### Is Google agent quality flywheel skill an official Google term?

No. It is an editorial pattern for combining Google ADK evalsets, Vertex AI Gen AI Evaluation, trace review, CI gates, and production monitoring into a repeatable agent-quality workflow.

### Should I use ADK or Vertex AI Gen AI Evaluation first?

Start with ADK for the local developer loop. Add Vertex AI Gen AI Evaluation when you need batch scoring, experiment tracking, centralized rubrics, autorater calibration, or production trace evaluation at larger scale.

### When should tool trajectory matching be strict?

Use strict trajectory matching when the workflow has one valid path, such as regulated handoffs, required approval steps, or exact API sequences. Use flexible trajectory scoring for coding tasks where several tool paths can produce the same verified outcome.

### Can LLM-as-judge grade coding agents reliably?

It can grade subjective qualities like helpfulness, rubric adherence, and semantic answer quality. It should not replace code-based checks for files, tests, command exit codes, issue status, API payloads, or other objective state changes.

### What is the smallest useful eval suite?

Five to ten real regression cases are enough to start if they come from actual traces and cover important failures. A small hand-reviewed suite is usually more useful than hundreds of unverified synthetic cases.
