# Task-success protocol for local coding models

A frozen, runnable harness that scores the **end state** of a small repository after an
agent task — `completed` / `partially` / `failed` — instead of tokens/second or a
leaderboard position. Standard library only, no network, no credentials.

This directory was produced while writing
`content/posts/local-coding-model-agent-task-success-2026.md`. The fixture numbers in
`fixture-report.json` are a **self-check of the harness**, never a measurement of a model.

## Files

| file | what it is |
| --- | --- |
| `tasks.json` | the frozen task set: four tasks (edit, add a test, fix a failing test, rename across files), a 12-step budget and a task-scoped suite per task |
| `sandbox/` | the frozen synthetic repository the tasks run against (`inventory` package + `tests`); hashed as a tree in every run header |
| `harness.py` | adapter contract, sandbox materialisation, per-task verifiers, run loop, scorer and `matrix.csv` writer |
| `models.py` | the adapters: five deterministic fixture doubles, plus `LocalOpenAICompatAdapter` for a real served model |
| `run_tasks.py` | CLI: run one adapter, write `transcript.json`, `matrix.csv`, `result.json` |
| `test_harness.py` | deterministic unit tests for the harness and the scorer |
| `fixture_report.py` | runs the self-check and records `fixture-tests.txt` + `fixture-report.json` |

## Adapter contract

```python
class TaskAdapter:
    name = "model-id + quantisation + endpoint"      # recorded in the run header
    def next_action(self, observation) -> dict: ...   # one action per call
```

`observation` is `{"task", "step", "files", "last_test_output", "steps_left"}`, where
`files` is the current repository as `{relpath: text}`. An action is one of:

```
{"op":"write","path":REL,"content":FULL_FILE}
{"op":"patch","path":REL,"find":EXACT_TEXT,"replace":NEW_TEXT}
{"op":"run_tests"}                                  # returns the suite output as feedback
{"op":"escalate","reason":"..."}                    # give up / hand to a human
{"op":"stop"}                                      # believe it is done
```

## Run it

```bash
python3 test_harness.py                                        # unit tests of the harness
python3 run_tasks.py --adapter reference --out "$TMPDIR/out"   # offline control
python3 run_tasks.py --adapter local --base-url http://127.0.0.1:8000 \
        --model <served-model-id> --out "$TMPDIR/out"          # a real served model
python3 fixture_report.py                                      # regenerate the self-check
```

`python3 run_tasks.py --adapter local ...` is the only command that measures a model. It
needs an OpenAI-compatible `/v1/chat/completions` endpoint (vLLM, llama.cpp server, Ollama
`/v1`, LM Studio, TGI), served with no authentication. Point it at a model you can see in
`GET /v1/models`, and record the endpoint, model id, quantisation, context length and
sampling parameters with the run — a completion rate without them is not reproducible.

## Scoring

A task's recorded `checks` are split into scored checks and suite-success guards; only the
scored ones grant credit, because the frozen `tests/test_store.py` is green and "the scoped
suite passes" is therefore not evidence that a task advanced.

* `completed` — every scored check passes
* `partially` — at least one scored check passes (e.g. the method exists, the suite is red)
* `failed` — none passes, or the adapter escalated

`matrix.csv` has one row per task (`task_id, category, status, checks_passed, checks_total,
steps, test_runs, escalations, wall_clock_s, suite_ok`) plus an aggregate row.

## Fixture doubles (harness self-check, not model measurements)

`reference` must complete all four tasks; each defect double must move only what it breaks:
`stall` (stops immediately), `loop` (spins to the step budget), `escalation` (hands every
task to a human), `partial-rename` (renames the definition and leaves the call sites).
Recorded on 2026-10-13 (UTC) with Python 3.12.3: 10 tests pass, `reference` 4/4 completed,
`stall` / `loop` / `escalation` 0/4, `partial-rename` 3 completed + 1 partially.

## Bounds

The sandbox is synthetic, the tasks are sequential in one working copy (so an early failure
is inherited by later tasks), and nothing here is a benchmark of a model, a vendor or a
harness other than this one. No model was loaded and no GPU time was used while writing the
article. Unknown monetary cost is unknown.
