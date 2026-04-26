---
title: "OpenAI Hosted Shell and Apply Patch: GPT-5.5 Compute Tools for Autonomous Code Execution"
date: 2026-04-25T10:05:54+00:00
tags: ["openai", "gpt-5.5", "autonomous-coding", "api", "developer-tools"]
description: "Complete guide to GPT-5.5's hosted shell and apply_patch tools for building autonomous coding agents via the OpenAI Responses API."
draft: false
cover:
  image: "/images/openai-hosted-shell-apply-patch-guide-2026.png"
  alt: "OpenAI Hosted Shell and Apply Patch: GPT-5.5 Compute Tools for Autonomous Code Execution"
  relative: false
schema: "schema-openai-hosted-shell-apply-patch-guide-2026"
---

GPT-5.5's hosted shell and `apply_patch` tools let you run autonomous coding agents that explore filesystems, execute commands, and apply precise code edits — all inside an OpenAI-managed Debian 12 sandbox with no infrastructure to maintain.

## What Are OpenAI's Compute Tools? Hosted Shell and Apply Patch Explained

OpenAI's compute tools are two purpose-built capabilities in the Responses API that give models direct access to code execution environments and structured file-editing primitives. The **hosted shell** tool provisions an ephemeral Debian 12 container where GPT-5.5 can run arbitrary shell commands — installing packages, running test suites, inspecting file trees, and producing downloadable artifacts via `/mnt/data`. The **`apply_patch` tool** gives the model a structured way to propose file modifications using the V4A diff format, which supports `create_file`, `update_file`, and `delete_file` operations with surgical precision. Together, these two tools form a closed loop: the model explores a codebase with shell commands, identifies what needs to change, and applies those changes via structured patches — without the host application needing to interpret or re-execute diffs. As of April 2026, these tools are only available through the Responses API (not the Chat Completions API) and require GPT-5.5 or compatible models. The combination represents OpenAI's most direct answer to Claude Code, GitHub Copilot Agent, and similar agentic coding platforms.

## GPT-5.5 (Spud): The Model That Powers These Tools

GPT-5.5, codenamed "Spud," was released on April 23, 2026 — the first fully retrained base model since GPT-4.5. It is specifically optimized for agentic, multi-step workflows that involve tool use across long contexts. GPT-5.5 achieves **82.7% on Terminal-Bench 2.0**, the state-of-the-art benchmark for complex command-line workflows, and **58.6% on SWE-Bench Pro** for real-world GitHub issue resolution (compared to Claude Opus 4.7's 64.3% on the same benchmark). The model supports a **1M token context window** and natively integrates with hosted shell, `apply_patch`, computer use, Skills, MCP servers, and web search. Pricing is $5 per 1M input tokens and $30 per 1M output tokens — double the GPT-5.4 rate, reflecting the higher capability level. GPT-5.5 Pro ($30/$180 per 1M tokens) offers enhanced reasoning but notably does **not** support `apply_patch`, making standard GPT-5.5 the correct choice for autonomous code-editing agents. If your workflow requires multi-file refactoring, bug patching, or test generation at scale, GPT-5.5 is the model to use.

## How the Hosted Shell Works: Debian 12 Container Architecture

The hosted shell provisions an OpenAI-managed Debian 12 environment with controlled internet access that is isolated from your application's runtime and credentials. When you include `{"type": "shell"}` in the `tools` array and set `container` to `"container_auto"`, OpenAI automatically allocates a fresh container for each session. The model can execute any shell command — `apt-get install`, `pytest`, `git log`, `find`, `curl` — and the output streams back from the container runtime into the model's context. Files written to `/mnt/data` inside the container become downloadable artifacts available after the session. Container pricing is separate from token costs: $0.03/GB for 1GB sessions or $1.92/64GB for larger workloads, billed per 20-minute session window (pricing active from March 31, 2026). The architecture deliberately separates the **control harness** (your application code, API keys, environment variables) from the **compute layer** (the sandboxed container), which prevents the model from exfiltrating credentials or making unauthorized network calls. Containers are ephemeral by default — state does not persist between API calls unless you mount a persistent volume or use the `/mnt/data` artifact mechanism.

```python
from openai import OpenAI

client = OpenAI()

response = client.responses.create(
    model="gpt-5.5",
    tools=[{"type": "shell"}],
    container="container_auto",
    input="List all Python files in /workspace and count total lines of code.",
)

for event in response:
    if event.type == "shell_call":
        print(f"Running: {event.command}")
    elif event.type == "shell_call_output":
        print(f"Output: {event.output[:200]}")
```

### Container Session Lifecycle

A container session begins when the first shell command executes and ends after 20 minutes of inactivity or when explicitly closed. Within a session, the container maintains full filesystem state — installed packages, created files, environment variables set by earlier commands. This allows multi-turn interactions where the model installs dependencies in one turn and runs tests in the next without re-provisioning. When building long-running agents, structure your prompts to batch related operations within a single session window to minimize container provisioning overhead and cost.

## The Apply Patch Tool: V4A Diff Format for Precise Code Edits

The `apply_patch` tool gives GPT-5.5 a structured mechanism for proposing file modifications that your application can review, approve, or reject before execution. Unlike shell-based `sed` or `patch` commands that operate inside the sandbox, `apply_patch` emits structured `apply_patch_call` objects in the model's response output — the actual file changes happen in **your** filesystem, not the container's, giving you full control over what gets modified. The tool uses the **V4A diff format**, a compact patch syntax that supports three operations: `create_file` (with full content), `update_file` (with context lines and replacements), and `delete_file`. Enable it by adding `{"type": "apply_patch"}` to your tools array. The model generates patches that are precise, machine-readable, and auditable — each patch specifies exactly which lines change and why, making code review tractable even for large refactors. This design reflects a key architectural choice: the model proposes, the human (or application) disposes. You can add an approval gate, write the patches to a staging directory, run your test suite against them, and only apply on green.

```python
response = client.responses.create(
    model="gpt-5.5",
    tools=[
        {"type": "shell"},
        {"type": "apply_patch"},
    ],
    container="container_auto",
    input="""
    Read src/auth.py. The JWT token expiry is hardcoded to 3600 seconds.
    Refactor it to read from an environment variable JWT_EXPIRY_SECONDS with
    a fallback of 3600. Apply the patch when ready.
    """,
)

for event in response:
    if event.type == "apply_patch_call":
        # Review patch before applying
        print(event.patch)
        # Apply: event.apply() or handle manually
```

### V4A Diff Format in Practice

The V4A format is intentionally minimal. An `update_file` patch looks like this:

```
*** Update File: src/auth.py
@@
-JWT_EXPIRY = 3600
+JWT_EXPIRY = int(os.environ.get("JWT_EXPIRY_SECONDS", 3600))
```

Context lines (unchanged code around the edit) help the patch engine locate the right position even if line numbers have shifted. `create_file` patches include the full file content inline. `delete_file` patches require only the filename. The format is designed for model output — terse enough to fit in long context windows, structured enough to parse deterministically.

## Building an Autonomous Coding Agent: Shell + Apply Patch Workflow

The most powerful pattern combines hosted shell for exploration and `apply_patch` for modifications in a four-phase loop: **explore → plan → patch → verify**. In the explore phase, the model uses shell commands to understand the codebase structure, identify failing tests, and locate the code that needs to change. In the plan phase, it reasons through the changes required. In the patch phase, it emits `apply_patch_call` objects for each file to modify. In the verify phase, it runs the test suite inside the container to confirm the changes are correct. This loop can run fully autonomously or with a human-in-the-loop approval gate between patch and verify. The shell tool handles exploration and verification; `apply_patch` handles modifications. Neither tool is sufficient alone — shell-only agents write changes via `sed` or `tee`, which is fragile and hard to audit; `apply_patch`-only agents cannot run tests to verify correctness. The combination is what makes the workflow production-grade.

```python
from openai import OpenAI
import subprocess

client = OpenAI()

SYSTEM_PROMPT = """You are an autonomous coding agent. For each task:
1. Use shell to explore the codebase and understand the problem
2. Use shell to run existing tests to understand what's failing
3. Use apply_patch to propose precise code changes
4. Use shell to run tests again and verify your fix works
Report results when done."""

def run_agent(task: str, workspace: str):
    messages = [{"role": "user", "content": f"Workspace: {workspace}\n\nTask: {task}"}]

    while True:
        response = client.responses.create(
            model="gpt-5.5",
            tools=[
                {"type": "shell"},
                {"type": "apply_patch"},
            ],
            container="container_auto",
            system=SYSTEM_PROMPT,
            input=messages,
        )

        patches_applied = []
        for event in response:
            if event.type == "apply_patch_call":
                # Apply patch to local filesystem
                result = subprocess.run(
                    ["patch", "-p0"],
                    input=event.patch,
                    capture_output=True,
                    text=True
                )
                patches_applied.append({
                    "patch": event.patch,
                    "success": result.returncode == 0,
                    "output": result.stdout or result.stderr
                })

        if response.status == "completed":
            return {
                "patches": patches_applied,
                "summary": response.output_text
            }

        # Add tool results to message history and continue
        messages = response.messages
```

## Real-World Use Cases: Refactors, Bug Fixes, and Migrations

Hosted shell and `apply_patch` unlock several high-value automated workflows that were previously too complex or risky to automate. **Multi-file refactors**: renaming a function across 50 files, updating import paths after a package reorganization, or migrating from one ORM to another. The model explores the codebase, identifies all affected files, and emits a sequence of `apply_patch_call` objects — one per file — that can be reviewed as a batch before application. **Bug fixes from issue descriptions**: given a GitHub issue URL or error stack trace, the agent reproduces the bug in the container, locates the root cause, patches it, and runs the test suite to confirm resolution. **API migrations**: when a third-party SDK releases a breaking change, the agent reads the migration guide (via shell `curl`), identifies all call sites in your codebase, and patches them to the new API. **Test generation**: the agent reads a source file, generates corresponding test cases in the container's scratch space, validates they pass, then uses `apply_patch` to write the test file into your repository. **Dependency upgrades**: the agent runs `pip install --upgrade` or `npm update`, runs your test suite, identifies breakages, patches the affected code, and repeats until tests pass.

### When Not to Use the Hosted Shell

The hosted shell is not appropriate for operations that require access to production systems, customer data, or credentials. The container isolation prevents credential theft by design, but this also means the agent cannot directly connect to your production database or internal services. For workflows that require such access, use the `apply_patch` tool in isolation (without hosted shell) combined with your own local execution environment, where you control what tools and credentials the agent can access.

## Security Best Practices: Sandboxing, Path Validation, and Audit Logging

The hosted shell's container isolation eliminates the most dangerous attack vector — direct access to the host filesystem and credentials — but applications using `apply_patch` still need their own security controls. The key principle: **never apply patches to arbitrary paths without validation**. Validate that all patch targets are within your project root, reject patches that modify `.env` files, credentials, or CI/CD configuration, and require explicit approval for patches to production code paths. Implement an audit log that records every `apply_patch_call` with the full patch content, timestamp, model version, and the task prompt that generated it — this creates an immutable record for debugging and compliance. For multi-agent pipelines where one agent's output becomes another's input, add an intermediate validation step that checks patch syntax, target path safety, and changeset size before forwarding. Rate-limit the number of files a single agent run can modify to bound blast radius. Finally, always run your test suite after applying patches in CI, even if the agent reports success — test suite verification in the container is informative but not authoritative for your actual test environment.

```python
import os
from pathlib import Path

PROJECT_ROOT = Path("/workspace/myapp").resolve()
BLOCKED_PATTERNS = [".env", "credentials", "secrets", ".aws", ".ssh"]

def safe_apply_patch(patch_event, project_root=PROJECT_ROOT):
    """Validate and apply a patch only if targets are within project root."""
    lines = patch_event.patch.splitlines()
    targets = [l.split(": ", 1)[1] for l in lines if l.startswith("*** ")]

    for target in targets:
        target_path = (project_root / target).resolve()
        # Prevent path traversal
        if not str(target_path).startswith(str(project_root)):
            raise ValueError(f"Path traversal attempt: {target}")
        # Block sensitive files
        if any(p in str(target_path) for p in BLOCKED_PATTERNS):
            raise ValueError(f"Blocked sensitive path: {target}")

    # Safe to apply
    return subprocess.run(["patch", "-p0"], input=patch_event.patch, ...)
```

## Pricing Breakdown: API Costs, Container Sessions, and When to Use GPT-5.5 Pro

Understanding the cost structure is essential for building economically viable agents. Token costs and container costs are billed independently and accumulate differently across agent run types.

| Component | GPT-5.5 | GPT-5.5 Pro |
|-----------|---------|-------------|
| Input tokens | $5 / 1M | $30 / 1M |
| Output tokens | $30 / 1M | $180 / 1M |
| apply_patch | Supported | **Not supported** |
| Container (1GB) | $0.03/session | $0.03/session |
| Container (64GB) | $1.92/session | $1.92/session |
| Context window | 1M tokens | 1M tokens |

GPT-5.5 Pro's 6x token cost premium is only justified for tasks that require deep multi-step reasoning without tool use — complex architectural analysis, security audit reports, or algorithmic design. For any workflow that uses `apply_patch`, standard GPT-5.5 is the only option, as Pro explicitly does not support it. For high-volume batch workflows (nightly dependency updates, automated test generation across a monorepo), cache your system prompts and codebase context using the Responses API's caching layer to reduce input token costs by up to 75%. A typical bug-fix agent run that explores 20 files and applies 3 patches costs approximately $0.08–$0.15 in tokens plus $0.03 for the container session — well under $0.20 per resolved issue.

### Container Cost Optimization

Container sessions bill per 20-minute window, not per command. Batch multiple related operations within a single agent run to maximize utilization. If your workflow involves repeated runs against the same codebase (e.g., a nightly CI bot), use persistent volumes to avoid re-installing dependencies each session. For development and testing, use a local sandbox (Docker + the OpenAI API without `container_auto`) to avoid container costs entirely during iteration.

## GPT-5.5 vs Claude Code vs GitHub Copilot Agent: Agentic Coding Comparison

The autonomous coding agent space now has three dominant approaches, each with distinct architectural trade-offs that affect what workflows they handle best.

| Capability | GPT-5.5 (Shell + Patch) | Claude Code | GitHub Copilot Agent |
|------------|------------------------|-------------|----------------------|
| Hosted sandbox | OpenAI-managed Debian 12 | Local process | GitHub Actions runner |
| Code editing primitive | apply_patch (V4A) | Direct file writes | Direct file writes |
| Benchmark (SWE-Bench Pro) | 58.6% | 64.3% (Opus 4.7) | ~52% (est.) |
| Terminal-Bench 2.0 | 82.7% | Not published | Not published |
| Context window | 1M tokens | 200K tokens | 128K tokens |
| PR integration | Via API | Native Git | Native GitHub PRs |
| Audit trail | apply_patch_call log | Git diff | PR review thread |
| Pricing model | Per token + container | Subscription / API | Subscription |

GPT-5.5 leads on Terminal-Bench 2.0 (CLI workflows) and context length, making it the strongest choice for large monorepo refactors where full-codebase context matters. Claude Opus 4.7 leads on SWE-Bench Pro (real GitHub issues), making it stronger for nuanced bug diagnosis. Copilot Agent has the tightest GitHub integration but the smallest context window, limiting it to targeted, file-scoped changes. For teams already invested in the OpenAI API ecosystem, GPT-5.5 with hosted shell and `apply_patch` delivers a cohesive platform without additional infrastructure. For teams that need maximum accuracy on complex bugs, Claude Code remains the benchmark leader.

## Getting Started: Complete Code Example with Shell and Apply Patch

The following is a production-ready example that implements the full explore → patch → verify loop with error handling, patch validation, and result reporting. This pattern is suitable for CI/CD integration, nightly maintenance bots, or interactive developer tools.

```python
from openai import OpenAI
from pathlib import Path
import subprocess
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client = OpenAI()

PROJECT_ROOT = Path.cwd()
BLOCKED_PATHS = {".env", ".aws", ".ssh", "credentials"}

SYSTEM_PROMPT = """You are a senior software engineer running inside an OpenAI compute environment.
You have access to a hosted shell and the apply_patch tool.

Your workflow for every task:
1. Use shell to understand the codebase structure (ls, find, cat key files)
2. Use shell to run existing tests and understand the current state
3. Plan your changes carefully before patching
4. Use apply_patch for each file modification — never use shell to write files directly
5. Use shell to run tests after patching and verify your changes work
6. Report results: files changed, tests passed/failed, any caveats

Be precise. Be minimal. Only change what the task requires."""

def validate_patch(patch_text: str) -> bool:
    lines = patch_text.splitlines()
    for line in lines:
        if line.startswith("*** ") and ": " in line:
            target = line.split(": ", 1)[1].strip()
            target_path = (PROJECT_ROOT / target).resolve()
            if not str(target_path).startswith(str(PROJECT_ROOT)):
                logger.error(f"Path traversal blocked: {target}")
                return False
            if any(blocked in target for blocked in BLOCKED_PATHS):
                logger.error(f"Sensitive path blocked: {target}")
                return False
    return True

def apply_patch(patch_text: str) -> dict:
    if not validate_patch(patch_text):
        return {"success": False, "error": "Patch validation failed"}

    result = subprocess.run(
        ["patch", "-p0", "--dry-run"],
        input=patch_text,
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT
    )
    if result.returncode != 0:
        return {"success": False, "error": result.stderr}

    result = subprocess.run(
        ["patch", "-p0"],
        input=patch_text,
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT
    )
    return {
        "success": result.returncode == 0,
        "output": result.stdout,
        "error": result.stderr if result.returncode != 0 else None
    }

def run_coding_agent(task: str) -> dict:
    logger.info(f"Starting agent for task: {task[:80]}...")
    audit_log = []
    patches_applied = []

    response = client.responses.create(
        model="gpt-5.5",
        tools=[
            {"type": "shell"},
            {"type": "apply_patch"},
        ],
        container="container_auto",
        system=SYSTEM_PROMPT,
        input=task,
        stream=True,
    )

    for event in response:
        if event.type == "shell_call":
            logger.info(f"Shell: {event.command[:100]}")

        elif event.type == "apply_patch_call":
            logger.info("Patch proposed, validating...")
            audit_log.append({
                "type": "apply_patch_call",
                "patch": event.patch,
                "task": task,
            })
            result = apply_patch(event.patch)
            patches_applied.append(result)
            if result["success"]:
                logger.info("Patch applied successfully")
            else:
                logger.error(f"Patch failed: {result['error']}")

        elif event.type == "response.done":
            logger.info("Agent completed")

    return {
        "patches_applied": patches_applied,
        "patches_succeeded": sum(1 for p in patches_applied if p["success"]),
        "audit_log": audit_log,
        "summary": response.output_text if hasattr(response, "output_text") else "",
    }

if __name__ == "__main__":
    result = run_coding_agent(
        "Find all hardcoded timeout values in src/ and replace them with "
        "constants defined in src/config/timeouts.py. Create that file if it "
        "doesn't exist. Run the test suite to verify nothing breaks."
    )
    print(json.dumps(result, indent=2, default=str))
```

## FAQ

**Does the hosted shell have internet access?**
Yes, with restrictions. OpenAI-managed containers have controlled internet access that allows common package manager operations (`apt-get`, `pip install`, `npm install`) and public API calls, but blocks access to internal networks and restricts certain outbound protocols. This is intentional: the container needs to install dependencies but should not be able to reach your internal databases or VPNs.

**Can I use apply_patch without the hosted shell?**
Yes. The `apply_patch` tool operates independently of the hosted shell. If your application already manages code execution locally (e.g., in a Docker container you control), you can enable only `apply_patch` and handle all file operations yourself. The model will emit `apply_patch_call` events that your application applies to its own filesystem.

**Is GPT-5.5 better than Claude Code for autonomous coding?**
It depends on the benchmark. GPT-5.5 scores higher on Terminal-Bench 2.0 (82.7% vs. unreported for Claude Code), making it stronger for CLI-heavy workflows. Claude Opus 4.7 scores higher on SWE-Bench Pro (64.3% vs. GPT-5.5's 58.6%), making it better for complex real-world bug resolution. For teams in the OpenAI ecosystem, GPT-5.5 with hosted shell and `apply_patch` is the most integrated solution.

**What happens if a patch fails to apply?**
The `apply_patch` tool emits the patch as structured output — your application is responsible for applying it. If `patch -p0` fails (e.g., due to context mismatch), you can return the error to the model in a follow-up turn and ask it to generate a corrected patch. Build retry logic with a maximum of 2–3 attempts before surfacing the error to a human reviewer.

**How do I handle large codebases with GPT-5.5's 1M token context?**
GPT-5.5's 1M token context is large enough to hold approximately 30,000–40,000 lines of code. For monorepos larger than this, use the shell tool to identify the relevant subset of files (via `grep`, `find`, or language-specific analysis tools) and pass only those files as context. Structure your prompts to load files lazily — let the model request the files it needs rather than dumping the entire codebase upfront.
