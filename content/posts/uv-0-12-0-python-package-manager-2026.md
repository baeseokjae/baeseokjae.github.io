---
title: "Uv 0.12 Python Package Manager: Astral's Speed Demon Gets Smarter and Safer"
date: 2026-07-29T04:04:42+00:00
tags:
  - uv
  - python
  - package manager
  - astral
  - open source
  - review
description: "Uv 0.12.0 delivers 14+ breaking changes focused on safety, spec compliance, and production readiness while maintaining its 10-100x speed advantage over pip."
draft: false
cover:
  image: "/images/uv-0-12-0-python-package-manager-2026.png"
  alt: "Uv 0.12 Python Package Manager — Astral's Speed Demon Gets Smarter and Safer"
  relative: false
schema: "schema-uv-0-12-0-python-package-manager-2026"
---

Uv 0.12.0, released July 28, 2026 by Astral, is the most significant update yet for the Rust-based Python package manager that has taken the Python community by storm. With over 14 breaking changes, stricter security validation, a new default `src/` project layout, and continued 10-100x speed advantages over pip, uv 0.12.0 marks a clear transition from experimental speed demon to production-grade package management tool.

## What is uv? — The All-in-One Python Package Manager

Uv is a unified Python package and project manager written in Rust by Astral, the same company behind the Ruff linter. First released on October 2, 2023, uv has rapidly grown to replace an entire ecosystem of Python tooling: pip, pip-tools, pipx, poetry, pyenv, and virtualenv — all in a single binary. As of July 2026, uv has amassed 88,036 stars on GitHub with 3,406 forks, making it one of the most popular Python tools ever created.

What makes uv unique is its speed. Built in Rust with a focus on performance from day one, uv can install packages 10-100x faster than pip. In a benchmark published by tutorials.technology, installing 23 packages took pip 6.6 seconds on a warm cache, while uv completed the same task in just 0.15 seconds — a 44x improvement. This speed advantage compounds across every operation: dependency resolution, virtual environment creation, and project management all benefit from uv's Rust foundation.

## Uv 0.12.0 — A Maturity Milestone

Version 0.12.0 is not just another incremental release. It represents a philosophical shift for the project. While earlier versions focused on raw speed and feature parity with pip, 0.12.0 prioritizes correctness, security, and compliance with Python packaging standards. This is uv growing up.

The release notes, published on GitHub on July 28, 2026, list over 14 breaking changes. But unlike typical breaking releases that introduce disruptive new features, most of uv 0.12.0's breaking changes are safety improvements that will not affect the majority of users. The message from Astral is clear: uv is being hardened for enterprise and production use.

### Breaking Changes Overview (14+ Changes Focused on Safety and Spec Compliance)

The breaking changes in uv 0.12.0 cluster into several categories:

| Category | Change | Impact |
|----------|--------|--------|
| Project Layout | `uv init` defaults to `src/` layout with `uv_build` backend | New projects get a modern structure automatically |
| Archive Validation | Rejects `.tar.bz2`, `.tar.xz` per PEP 625 | Stricter spec compliance, fewer edge cases |
| Security | Rejects wheels that could replace Python interpreter | Prevents a class of supply-chain attacks |
| Security | Respects `--require-hashes` in requirements.txt | Enforces hash-pinned installs |
| Security | Rejects MD5-only hashes | Weak hash algorithm no longer accepted |
| Security | `SSL_CERT_FILE`/`SSL_CERT_DIR` honored strictly | More predictable certificate handling |
| Pre-releases | `if-necessary` mode replaces `if-necessary-or-explicit` | Smarter pre-release resolution |
| Lock Files | `pylock.toml` validation requires `packages` array | Lock file integrity enforced |
| Project Discovery | Project discovery relative to script path in `uv run` | More predictable behavior in scripts |
| venv | `uv venv --clear` requires `--force` for non-virtualenv dirs | Prevents accidental directory deletion |

Each of these changes serves a specific purpose. The archive format rejection, for example, aligns uv with PEP 625, which standardizes on `.tar.gz` for source distributions. The hash validation changes close a security gap where weak or missing hashes could allow tampered packages to be installed.

### Uv init Now Defaults to src/ Layout with uv_build

Perhaps the most visible change in uv 0.12.0 is the new default for `uv init`. When you create a new project, uv now generates a `src/` layout with the `uv_build` backend configured. This is a significant departure from the flat layout that Python projects have traditionally used.

The `src/` layout places your package code inside a `src/` directory, separating it from project configuration files, tests, and documentation. This structure has been recommended by the Python Packaging Authority (PyPA) for years, but many developers avoided it due to the complexity of configuring build backends. Simon Willison, a well-known Python developer, noted in his review of uv 0.12.0 that he had "avoided src layout out of inertia" but now thinks "it's time to switch."

The new `uv init` also creates a packaged project with a `[build-system]` section and `[project.scripts]` entry point, making it easy to define CLI commands for your package. This brings uv's project initialization in line with modern Python packaging best practices and signals Astral's confidence in `uv_build` as a stable, production-ready build backend.

### Stricter Archive and Hash Validation

Uv 0.12.0 tightens validation on two fronts: archive formats and hash algorithms.

On the archive side, uv now rejects `.tar.bz2` and `.tar.xz` source distributions, accepting only `.tar.gz` archives per PEP 625. This change simplifies uv's archive handling pipeline and ensures compatibility with the broader Python ecosystem, which has standardized on gzip-compressed tarballs.

On the hash side, uv 0.12.0 introduces two important changes. First, it now respects `--require-hashes` in `requirements.txt`, meaning that if you specify hash-pinned dependencies, uv will enforce them strictly. Second, uv rejects MD5-only hashes, requiring at least SHA-256 or stronger algorithms. MD5 has been considered cryptographically broken since 2004, and its continued presence in Python packaging has been a lingering security concern. Uv 0.12.0 takes a stand: weak hashes are no longer acceptable.

### Security Hardening: Interpreter Protection and SSL Cert Handling

Two security improvements in uv 0.12.0 deserve special attention.

First, uv now rejects wheel files that could replace the Python interpreter itself. This prevents a class of supply-chain attacks where a malicious package could disguise itself as the Python binary, potentially hijacking all Python operations on a system. While such attacks are rare in practice, the fact that uv proactively prevents them demonstrates Astral's commitment to security.

Second, uv 0.12.0 strictly honors `SSL_CERT_FILE` and `SSL_CERT_DIR` environment variables. In previous versions, uv's certificate handling could deviate from system expectations, leading to confusing SSL errors or, worse, silent certificate validation failures. The new behavior ensures that uv respects the system's certificate configuration, making it more predictable in enterprise environments with custom certificate authorities. Additionally, a new `--cert` flag has been added to `uv pip` commands, giving users explicit control over certificate paths.

### Improved Pre-release Resolution (if-necessary Mode)

Uv 0.12.0 replaces the `if-necessary-or-explicit` pre-release resolution mode with a simpler `if-necessary` mode. The change is subtle but important.

In the old mode, uv would consider pre-release versions only when explicitly requested or when no stable version satisfied the dependency constraints. The new `if-necessary` mode refines this: uv now considers pre-releases only when they are genuinely necessary to resolve the dependency graph. This brings uv closer to pip's behavior while being smarter about when pre-releases are appropriate.

For most users, this change means fewer surprises. If your project depends on a package that has only pre-release versions available, uv will find and use them. But if a stable version exists, uv will prefer it — even if a newer pre-release is technically available.

### Stabilized Features: TOML 1.0 SDists and Auto ulimit

Two features that were previously experimental have been stabilized in uv 0.12.0.

TOML 1.0-compatible source distributions are now fully supported. This means that packages using `pyproject.toml` with TOML 1.0 features (such as inline tables, dotted keys, and array-of-tables) will work correctly with uv. This stabilization is important because the Python packaging ecosystem is increasingly moving toward TOML-based configuration, and TOML 1.0 introduced several features that earlier versions of uv could not parse.

The automatic open-file limit adjustment on Unix systems has also been stabilized. Uv now automatically raises the open-file limit (`ulimit -n`) on Linux and macOS when needed, capped at 1,048,576. This prevents "too many open files" errors when working with large dependency trees or monorepos, a common pain point for developers managing complex Python projects.

## Performance Benchmarks — Still the Fastest

Despite the focus on safety and compliance in 0.12.0, uv has not sacrificed its core advantage: speed. The benchmarks remain impressive:

| Operation | pip | uv | Speedup |
|-----------|-----|----|---------|
| Install 23 packages (warm cache) | 6.6s | 0.15s | 44x |
| Install 23 packages (cold cache) | ~12s | ~0.8s | 15x |
| Dependency resolution (complex graph) | ~30s | ~1.5s | 20x |
| Virtual environment creation | ~2s | ~0.1s | 20x |

Source: tutorials.technology benchmarks, May 2026; Astral documentation.

These numbers make uv the fastest Python package manager by a wide margin. Even with the additional validation and security checks introduced in 0.12.0, uv maintains its speed advantage because the Rust foundation handles the heavy lifting efficiently.

It is worth noting that uv's speed is not just about raw installation time. The developer experience improvement from sub-second operations is significant. When `uv sync` completes in 0.2 seconds instead of 6 seconds, you run it more often. You iterate faster. You stay in flow. This qualitative improvement is harder to measure but equally important.

## Community Adoption — 88k Stars and Growing

Uv's community adoption tells a compelling story. With 88,036 GitHub stars as of July 2026, uv has surpassed Poetry (which has approximately 30,000 stars) and become the most-starred Python package management tool on GitHub. This growth trajectory is remarkable for a tool that was first released less than three years ago.

The adoption is not just about stars. Major Python projects and organizations are adopting uv for their workflows. The tool's ability to replace pip, pip-tools, pipx, poetry, pyenv, and virtualenv with a single binary makes it attractive for CI/CD pipelines, Docker images, and developer onboarding. When a new team member joins, instead of installing and configuring half a dozen tools, they install one: uv.

The Python community's reception of uv has been overwhelmingly positive, though not without criticism. Some developers express concern about the pace of breaking changes, while others question whether a single company (Astral) having so much influence over Python tooling is healthy for the ecosystem. These are valid concerns, but they have not slowed uv's adoption.

## Should You Upgrade?

For most users, upgrading to uv 0.12.0 is a low-risk, high-reward decision. Here is a quick decision guide:

**Upgrade immediately if:**
- You create new Python projects regularly (you will benefit from the `src/` layout defaults)
- You care about supply-chain security (hash validation, interpreter protection)
- You work in an enterprise environment with custom SSL certificates
- You want the latest pre-release resolution improvements

**Test carefully before upgrading if:**
- You have complex CI/CD pipelines that may be affected by the archive format changes
- You rely on `.tar.bz2` or `.tar.xz` source distributions (rare, but possible)
- You use MD5-only hashes in your requirements files (you should upgrade your hashes anyway)
- You have scripts that depend on the old `uv init` flat layout

**No action needed if:**
- You are already using uv for basic package installation and virtual environment management
- You do not use `uv init` or create new projects frequently

The upgrade path is straightforward: `uv self update` or download the latest binary from the GitHub releases page. Uv 0.12.0 is available on PyPI, Homebrew, and via the official installation script at docs.astral.sh/uv.

## The Road to 1.0

The question on every uv user's mind is: when will uv hit 1.0? Version 0.12.0 brings us closer to that milestone, but Astral has not announced a specific timeline.

What is clear is that uv is approaching 1.0 territory. The focus on security, spec compliance, and stability in 0.12.0 are hallmarks of a tool preparing for a stable release. The breaking changes in this version are overwhelmingly safety improvements rather than feature additions, suggesting that Astral is prioritizing correctness over new capabilities.

The remaining questions before 1.0 likely include:
- Full stabilization of the plugin system
- Complete PEP 723 (inline script metadata) support
- Maturation of the `uv_build` backend
- Resolution of the remaining edge cases in dependency resolution

Given the pace of uv's development — 12 major versions in under 3 years — a 1.0 release within the next 6-12 months seems plausible. But Astral has shown a willingness to take their time and get it right, and the community has rewarded that patience with continued adoption.

## FAQ

### What is uv 0.12.0 and why is it important?

Uv 0.12.0 is the latest major release of Astral's Rust-based Python package manager, released July 28, 2026. It is important because it introduces over 14 breaking changes focused on security hardening, spec compliance, and production readiness — marking uv's transition from an experimental speed tool to a mature package manager suitable for enterprise use.

### How much faster is uv than pip in 2026?

Uv remains 10-100x faster than pip. In benchmarks, installing 23 packages takes pip 6.6 seconds on a warm cache while uv completes the same task in 0.15 seconds — a 44x improvement. Cold cache installations show approximately 15x speedup, and dependency resolution for complex graphs is roughly 20x faster.

### What are the breaking changes in uv 0.12.0?

The major breaking changes include: `uv init` now defaults to `src/` layout with `uv_build` backend, rejection of `.tar.bz2` and `.tar.xz` archives per PEP 625, rejection of wheels that could replace the Python interpreter, strict `--require-hashes` enforcement, rejection of MD5-only hashes, stricter SSL certificate handling, improved pre-release resolution, and `pylock.toml` validation requirements.

### Do I need to change my existing projects for uv 0.12.0?

No. The breaking changes in uv 0.12.0 primarily affect new projects created with `uv init` and edge cases involving archive formats, hash algorithms, and security validation. Existing projects will continue to work without modification. The `src/` layout change only applies to new projects, not existing ones.

### Is uv ready for production use?

Yes. Uv 0.12.0's focus on security hardening, spec compliance, and strict validation makes it suitable for production and enterprise use. The tool has 88,000+ GitHub stars, is maintained by Astral (the well-funded company behind Ruff), and is being adopted by major Python projects. While it has not yet reached a 1.0 release, uv 0.12.0 demonstrates the maturity and stability expected of production-grade software.
