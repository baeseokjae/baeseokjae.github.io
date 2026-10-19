#!/usr/bin/env python3
"""Adapters for the task-success harness: deterministic fixture doubles plus one real
local-endpoint adapter.

The fixture doubles are scripted, deterministic, offline agents. They exist only to prove
the harness and the scorer behave (the reference double must complete every task; each
single-defect double must move only the column it breaks). They are NOT vendor systems and
their output is never a benchmark of any model.

`LocalOpenAICompatAdapter` is the real path: it talks to an OpenAI-compatible chat endpoint
(vLLM, llama.cpp server, Ollama's /v1, LM Studio, TGI). It is deliberately shipped and
deliberately NOT run by the fixture self-check, because it needs a served model.
"""
from __future__ import annotations

import json
import re
import time
import urllib.error
import urllib.request

SYSTEM_PROMPT = (
    "You are a coding agent operating on a small Python repository. "
    "Reply with ONE JSON action and nothing else. Allowed actions: "
    '{"op":"write","path":REL,"content":FULL_FILE} | '
    '{"op":"patch","path":REL,"find":EXACT_TEXT,"replace":NEW_TEXT} | '
    '{"op":"run_tests"} | {"op":"escalate","reason":"..."} | {"op":"stop"}'
)


# --------------------------------------------------------------------- fixture doubles
class FixtureAdapter:
    """Base class: a scripted, deterministic in-process double for harness self-checks."""

    name = "fixture"

    @property
    def plan(self):
        """Per task id, the ordered actions this double emits (overridden by subclasses)."""
        return {}

    def __init__(self):
        self._cursor = {}
        self._current = None

    def next_action(self, observation):
        task_id = observation["task"]["id"]
        if self._current != task_id:
            self._current = task_id
            self._cursor[task_id] = 0
        actions = self.plan.get(task_id, [{"op": "stop"}])
        index = self._cursor[task_id]
        if index >= len(actions):
            return {"op": "stop"}
        self._cursor[task_id] = index + 1
        return actions[index]


class ReferenceAdapter(FixtureAdapter):
    """Ideal agent: performs every task correctly. Must score completed on all four."""

    name = "fixture-reference"

    STORE_WITH_COUNT = '''class Store:
    """A tiny in-memory price store used as a frozen agent-task sandbox."""

    def __init__(self):
        self._items = {}

    def add(self, name, price):
        if price < 0:
            raise ValueError("price must be non-negative")
        self._items[name] = price

    def get(self, name):
        return self._items.get(name)

    def remove(self, name):
        return self._items.pop(name, None)

    def count(self):
        return len(self._items)

    def total(self):
        return sum(self._items.values())
'''

    STORE_WITH_INSERT = STORE_WITH_COUNT.replace("def add(", "def insert(")

    INIT_WITH_INSERT = "from .store import Store\nfrom .report import format_total\n\n__all__ = [\"Store\", \"format_total\"]\n"

    REPORT_FIXED = '''from .store import Store


def format_total(store):
    """Render the store total as a two-decimal string, e.g. 'total: 3.50'."""
    return "total: %.2f" % store.total()


def summarize(store, names):
    parts = ["%s=%s" % (name, store.get(name)) for name in names]
    return ", ".join(parts)
'''

    TEST_STORE_INSERT = '''import unittest

from inventory import Store


class StoreTests(unittest.TestCase):
    def test_add_and_get(self):
        store = Store()
        store.insert("bolt", 1.5)
        self.assertEqual(store.get("bolt"), 1.5)

    def test_negative_price_rejected(self):
        store = Store()
        with self.assertRaises(ValueError):
            store.insert("broken", -1.0)

    def test_remove(self):
        store = Store()
        store.insert("bolt", 1.5)
        self.assertEqual(store.remove("bolt"), 1.5)
        self.assertIsNone(store.get("bolt"))

    def test_total(self):
        store = Store()
        store.insert("bolt", 1.5)
        store.insert("nut", 2.0)
        self.assertEqual(store.total(), 3.5)


if __name__ == "__main__":
    unittest.main()
'''

    TEST_COUNT = '''import unittest

from inventory import Store


class CountTests(unittest.TestCase):
    def test_count_tracks_add_and_remove(self):
        store = Store()
        self.assertEqual(store.count(), 0)
        store.add("bolt", 1.5)
        self.assertEqual(store.count(), 1)
        store.remove("bolt")
        self.assertEqual(store.count(), 0)


if __name__ == "__main__":
    unittest.main()
'''

    TEST_COUNT_INSERT = TEST_COUNT.replace(".add(", ".insert(")

    TEST_REPORT_INSERT = ('''import unittest

from inventory import Store, format_total


class ReportTests(unittest.TestCase):
    def test_total_is_rendered_with_two_decimals(self):
        store = Store()
        store.insert("bolt", 1.5)
        store.insert("nut", 2.0)
        self.assertEqual(format_total(store), "total: 3.50")


if __name__ == "__main__":
    unittest.main()
''')

    @property
    def plan(self):
        return {
            "T1-add-method": [
                {"op": "write", "path": "inventory/store.py", "content": self.STORE_WITH_COUNT},
                {"op": "run_tests"},
                {"op": "stop"},
            ],
            "T2-add-test": [
                {"op": "write", "path": "tests/test_count.py", "content": self.TEST_COUNT},
                {"op": "run_tests"},
                {"op": "stop"},
            ],
            "T3-fix-failing-test": [
                {"op": "run_tests"},
                {"op": "write", "path": "inventory/report.py", "content": self.REPORT_FIXED},
                {"op": "run_tests"},
                {"op": "stop"},
            ],
            "T4-rename-across-files": [
                {"op": "write", "path": "inventory/store.py", "content": self.STORE_WITH_INSERT},
                {"op": "write", "path": "inventory/__init__.py", "content": self.INIT_WITH_INSERT},
                {"op": "write", "path": "tests/test_store.py", "content": self.TEST_STORE_INSERT},
                {"op": "write", "path": "tests/test_count.py", "content": self.TEST_COUNT_INSERT},
                {"op": "write", "path": "tests/test_report.py", "content": self.TEST_REPORT_INSERT},
                {"op": "run_tests"},
                {"op": "stop"},
            ],
        }


class StallAdapter(FixtureAdapter):
    """Defect: declares the work finished without touching the repository."""

    name = "fixture-stall"

    @property
    def plan(self):
        return {task: [{"op": "stop"}] for task in
                ("T1-add-method", "T2-add-test", "T3-fix-failing-test", "T4-rename-across-files")}


class LoopAdapter(FixtureAdapter):
    """Defect: repeats a no-op edit and a test run until the step budget is exhausted."""

    name = "fixture-loop"

    @property
    def plan(self):
        spin = [{"op": "run_tests"}] * 12
        return {task: list(spin) for task in
                ("T1-add-method", "T2-add-test", "T3-fix-failing-test", "T4-rename-across-files")}


class EscalationAdapter(FixtureAdapter):
    """Defect: hands every task to a human at the first step."""

    name = "fixture-escalation"

    @property
    def plan(self):
        return {task: [{"op": "escalate", "reason": "no confident fix"}] for task in
                ("T1-add-method", "T2-add-test", "T3-fix-failing-test", "T4-rename-across-files")}


class PartialRenameAdapter(ReferenceAdapter):
    """Defect: renames the definition but leaves the call sites, so T4 is only partial."""

    name = "fixture-partial-rename"

    @property
    def plan(self):
        plan = dict(super().plan)
        plan["T4-rename-across-files"] = [
            {"op": "write", "path": "inventory/store.py", "content": self.STORE_WITH_INSERT},
            {"op": "run_tests"},
            {"op": "stop"},
        ]
        return plan


FIXTURES = {
    "reference": ReferenceAdapter,
    "stall": StallAdapter,
    "loop": LoopAdapter,
    "escalation": EscalationAdapter,
    "partial-rename": PartialRenameAdapter,
}


# ------------------------------------------------------------------ real local adapter
class LocalOpenAICompatAdapter:
    """Drive a served open-weight model through the same task loop.

    The endpoint must speak the OpenAI-compatible /v1/chat/completions shape with no
    authentication (vLLM, llama.cpp server, Ollama /v1, LM Studio, TGI). Nothing is hidden:
    the exact url, model id and sampling parameters are part of the recorded transcript
    header, because a task-success number without them is not reproducible.
    """

    def __init__(self, base_url, model, *, temperature=0.0, max_tokens=1024, seed=0,
                 timeout_s=180, name=None):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.seed = seed
        self.timeout_s = timeout_s
        self.name = name or "local:%s@%s" % (model, self.base_url)

    def _prompt(self, observation):
        task = observation["task"]
        files = "\n".join("--- %s ---\n%s" % (rel, text)
                          for rel, text in sorted(observation["files"].items()))
        last = observation["last_test_output"] or "(no test run yet)"
        return (
            "TASK (%s): %s\n\nSTEPS LEFT: %d\n\nREPOSITORY:\n%s\n\nLAST TEST OUTPUT:\n%s\n"
            % (task["category"], task["prompt"], observation["steps_left"], files, last[-4000:])
        )

    def next_action(self, observation):
        payload = json.dumps({
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "seed": self.seed,
            "messages": [{"role": "system", "content": SYSTEM_PROMPT},
                         {"role": "user", "content": self._prompt(observation)}],
        }).encode()
        request = urllib.request.Request(
            self.base_url + "/v1/chat/completions", data=payload,
            headers={"Content-Type": "application/json"}, method="POST",
        )
        started = time.monotonic()
        try:
            with urllib.request.urlopen(request, timeout=self.timeout_s) as response:
                body = json.loads(response.read().decode())
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            return {"op": "escalate", "reason": "endpoint error after %.1fs: %s"
                                                % (time.monotonic() - started, exc)}
        text = body["choices"][0]["message"]["content"]
        match = re.search(r"\{.*\}", text, re.S)
        if not match:
            return {"op": "escalate", "reason": "no JSON action in model reply"}
        try:
            action = json.loads(match.group(0))
        except json.JSONDecodeError:
            return {"op": "escalate", "reason": "malformed JSON action"}
        return action
