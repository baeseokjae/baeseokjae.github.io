---
cover:
  alt: 'smolagents Python Executor Code Injection Guide 2026 (CVE-2026-4963)'
  image: /images/smolagents-python-executor-code-injection-guide-2026.png
  relative: false
title: "smolagents Python Executor Code Injection Guide 2026 (CVE-2026-4963)"
slug: smolagents-python-executor-code-injection-guide-2026
date: 2026-07-07
description: "CVE-2026-4963 is a critical code injection in Hugging Face smolagents <= 1.25.0-dev.0. Here's how the local Python executor sandbox fails, how attackers bypass it, and what to do about it."
tags: ["smolagents", "CVE-2026-4963", "code-injection", "python-executor", "ai-agent-security", "huggingface"]
categories: ["AI Security"]
topics: ["AI Agent Security", "Vulnerability Analysis"]
---

If you're running Hugging Face's smolagents in production with the local Python executor, stop what you're doing and read this. CVE-2026-4963 is a code injection vulnerability in smolagents <= 1.25.0-dev.0 that lets an attacker execute arbitrary Python code on the host machine. The NVD rates it **10.0 CRITICAL** (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H). The exploit is public. And here's the worst part — this is an **incomplete fix** for CVE-2025-9959, meaning the previous patch didn't actually close the hole.

I've spent the last few hours digging through the source code, the advisory, and the public exploit PoCs. Here's exactly how the sandbox breaks, why the blocklist approach is fundamentally flawed, and what you should do right now.

## What Is smolagents?

smolagents is Hugging Face's lightweight framework for building AI agents. The idea is simple: you give an LLM a set of tools, and it writes Python code to accomplish tasks. That generated code gets executed in a **local Python executor** — a custom AST interpreter in `src/smolagents/local_python_executor.py` that's supposed to sandbox the execution.

The executor parses the agent's code into an AST (Abstract Syntax Tree) and walks it node by node, evaluating only the operations it considers safe. It maintains a blocklist of dangerous modules (`os`, `subprocess`, `shutil`, `socket`, `sys`, etc.) and dangerous functions (`builtins.eval`, `builtins.exec`, `os.system`, etc.). It also maintains an allowlist of safe built-in functions (`print`, `len`, `range`, `math.sqrt`, etc.) and authorized imports.

The problem? **Blocklists don't work when the attacker controls the input.**

## The Vulnerability: Three Bypass Vectors

CVE-2026-4963 affects three functions in `local_python_executor.py`:

- `evaluate_augassign` — handles `+=`, `-=`, `*=`, etc.
- `evaluate_call` — handles function calls
- `evaluate_with` — handles `with` statements

Let me walk through each one.

### 1. Augmented Assignment Bypass

The `evaluate_augassign` function evaluates the target of an augmented assignment by calling `get_current_value`, which uses Python's `getattr()` to access attributes on objects:

```python
def get_current_value(target: ast.AST) -> Any:
    if isinstance(target, ast.Attribute):
        obj = evaluate_ast(target.value, state, static_tools, custom_tools, authorized_imports)
        return getattr(obj, target.attr)
```

Then it writes the result back using `set_value`, which calls `setattr()`:

```python
elif isinstance(target, ast.Attribute):
    obj = evaluate_ast(target.value, state, static_tools, custom_tools, authorized_imports)
    setattr(obj, target.attr, value)
```

There's no check on what `obj` is. If an attacker can get a reference to a dangerous object — say, a module like `os` — they can use `obj.__dict__ += something` or `obj.__class__ += something` to modify internal state. The sandbox only checks `ast.Name` targets against `static_tools`, but `ast.Attribute` targets pass through unchecked.

### 2. Function Call Bypass

The `evaluate_call` function handles method calls on objects obtained through attribute access:

```python
elif isinstance(call.func, ast.Attribute):
    obj = evaluate_ast(call.func.value, state, static_tools, custom_tools, authorized_imports)
    func_name = call.func.attr
    if not hasattr(obj, func_name):
        raise InterpreterError(...)
    func = getattr(obj, func_name)
```

The dangerous function check only looks at `func.__name__` and `func.__module__`:

```python
for qualified_function_name in DANGEROUS_FUNCTIONS:
    module_name, function_name = qualified_function_name.rsplit(".", 1)
    if (
        (static_tools is None or function_name not in static_tools)
        and result.__name__ == function_name
        and result.__module__ == module_name
    ):
        raise InterpreterError(f"Forbidden access to function: {function_name}")
```

This check is trivially bypassable. If you can get a reference to `os.system` through a different path — say, by accessing it as an attribute of a module object you smuggled in — the `__name__` and `__module__` still match, but the check only runs on the *result* of an expression, not on intermediate objects used in attribute chains.

The classic Python sandbox escape works here:

```python
().__class__.__bases__[0].__subclasses__()
```

This gives you every class loaded in the interpreter. From there, you find one with access to `builtins` or `os` and call it. The executor blocks `__` prefixed attributes in `evaluate_attribute`, but the subscript access in `evaluate_subscript` doesn't check for dunder methods on the *result* — only `evaluate_attribute` does.

### 3. With Statement Bypass

The `evaluate_with` function calls `__enter__` and `__exit__` on context manager objects:

```python
context_expr = evaluate_ast(item.context_expr, state, static_tools, custom_tools, authorized_imports)
enter_result = context_expr.__enter__()
```

If an attacker can construct or obtain an object with a malicious `__enter__` method — for example, by defining a class inside the executor (which `evaluate_class_def` allows) — they can execute arbitrary code during the `with` block setup.

## Why the Blocklist Approach Fails

This is the core lesson. smolagents' executor uses a **deny-list** strategy: it lists what's forbidden and allows everything else. This is the opposite of a **allow-list** strategy, where you list what's permitted and deny everything else.

The `DANGEROUS_MODULES` list has 9 entries. The `DANGEROUS_FUNCTIONS` list has 8 entries. But Python's standard library has hundreds of modules, and the number of ways to access them through class introspection, `__subclasses__()`, `__globals__`, and `__builtins__` is effectively infinite.

Here's a concrete example of what an attacker can do even with the blocklist in place:

```python
# Step 1: Get a reference to a class that has access to builtins
class X:
    pass

# Step 2: Walk the MRO to find object, then subclasses
# (The executor blocks __ in attribute access, but not in subscript)
# Step 3: Once you have a reference to a class with __init__.__globals__,
# you can access any module in its globals
```

The `evaluate_class_def` function allows defining new classes. The `evaluate_function_def` function allows defining new functions. Both of these create callable objects that get stored in `state` or `custom_tools`. Once a user-defined function exists, its `__globals__` attribute (if accessible) leaks the entire execution environment.

## The Incomplete Fix Problem

CVE-2026-4963 is explicitly labeled as an **incomplete fix for CVE-2025-9959**. This means the original vulnerability was reported, a patch was released, and the patch didn't actually fix it. The advisory notes that "the vendor was contacted early about this disclosure but did not respond in any way."

This pattern is unfortunately common in AI agent security. The attack surface is large, the sandboxing problem is hard, and one-off patches that add more entries to a blocklist rarely close all the bypass paths.

## Mitigation: What You Should Do

### Immediate (Today)

1. **Pin smolagents to a version before 1.25.0-dev.0** if you must use it, or better yet, **don't use the local Python executor at all**. Switch to the code execution tool pattern where the agent writes code but a separate, hardened sandbox (like gVisor, Firecracker microVM, or Docker with no-network and read-only rootfs) actually runs it.

2. **If you can't upgrade**, set `authorized_imports` to an empty list `[]` and never use `"*"`. This at least blocks the import vector. It won't stop class introspection attacks, but it raises the bar.

3. **Run smolagents in a container** with no network access, no write access to the host filesystem, and strict resource limits. Assume the sandbox will be bypassed — because it will.

### Medium-term

1. **Replace the AST interpreter with a proper sandbox**. Options include:
   - **Pyodide** — CPython compiled to WebAssembly, runs in a browser-like sandbox
   - **RestrictedPython** — a battle-tested subset of Python for untrusted code
   - **gVisor or Firecracker** — full OS-level isolation for each agent execution
   - **Subprocess with seccomp** — run Python in a subprocess with seccomp-bpf syscall filtering

2. **Audit any AI agent framework that uses AST-level sandboxing**. The pattern is inherently fragile. Every AST node type you support is a potential bypass surface. smolagents supports 30+ AST node types including `ClassDef`, `FunctionDef`, `With`, `Try`, `Raise`, `Delete`, and `AugAssign` — each one is a potential escape vector.

### Long-term

The industry needs a better approach to agent code execution. The current pattern — "let the LLM write Python, then run it in a sandbox" — is fundamentally risky because LLMs are good at finding edge cases. I've written about this before in my [AI Agent Security Best Practices](/posts/ai-agent-security-tools-2026/) post, and the conclusion is the same: **don't trust the sandbox, trust the isolation**.

## The Bigger Picture

CVE-2026-4963 is not an isolated incident. It's part of a pattern. We've seen similar issues in [PraisonAI](/posts/praisonai-cross-origin-agent-execution-vulnerability-guide-2026/), in various MCP server implementations, and in the [agent supply chain](/posts/agent-skills-supply-chain-security-guide-2026/). The fundamental problem is that AI agent frameworks are being built with security as an afterthought — sandboxing is bolted on after the fact, and the sandbox is always playing catch-up with the attacker.

The smolagents executor is a well-written piece of code for what it tries to do. The AST walking is clean, the error handling is thorough, and the code is readable. But no amount of clean code can make a blocklist-based sandbox secure against a determined attacker who controls the input.

If you're building an AI agent system today, assume the code executor will be compromised. Design your architecture so that a compromised executor can't access your production database, your API keys, or your customer data. That's the only defense that actually works.

## References

- [GitHub Advisory GHSA-54fq-v6x8-244g](https://github.com/advisories/GHSA-54fq-v6x8-244g)
- [NVD Entry for CVE-2026-4963](https://nvd.nist.gov/vuln/detail/CVE-2026-4963)
- [GitLab Advisory Database Entry](https://advisories.gitlab.com/pypi/smolagents/CVE-2026-4963/)
- [smolagents source code on GitHub](https://github.com/huggingface/smolagents)
- [AI Agent Security Tools 2026](/posts/ai-agent-security-tools-2026/)
- [Agent Skills Supply Chain Security Guide](/posts/agent-skills-supply-chain-security-guide-2026/)
