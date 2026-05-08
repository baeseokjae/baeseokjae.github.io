---
title: "AI Code Security in Agentic Workflows 2026: SAST Tools for Cursor and Claude Code"
date: 2026-05-08T12:04:34+00:00
tags: ["AI code security", "SAST tools", "agentic workflows", "Claude Code", "Cursor", "MCP security", "DevSecOps"]
description: "92% of AI-generated codebases contain critical vulnerabilities. Here's how to secure agentic coding workflows with the right SAST tools in 2026."
draft: false
cover:
  image: "/images/ai-code-security-agentic-workflows-2026.png"
  alt: "AI Code Security in Agentic Workflows 2026: SAST Tools for Cursor and Claude Code"
  relative: false
schema: "schema-ai-code-security-agentic-workflows-2026"
---

Agentic coding with Cursor and Claude Code ships real code at 10–50x the speed of manual development — and that speed advantage now applies equally to introducing vulnerabilities. According to the Sherlock Forensics AI Code Security Report 2026, 92% of AI-generated codebases contain at least one critical vulnerability, with an average of 8.3 exploitable findings per application. The answer is not to slow down AI coding but to integrate SAST tools that enforce security at machine speed inside the agentic loop.

## The AI Code Security Crisis: Why Agentic Workflows Changed Everything

AI-generated code introduces vulnerabilities at a rate that outpaces traditional security tooling, and the root cause is structural: agentic workflows produce code faster than any human-reviewed pull-request process can absorb. Veracode's 2025 GenAI Code Security Report found that AI introduced security vulnerabilities in 45% of cases across 100+ LLMs and 80 curated coding tasks. Sherlock Forensics reports that 92% of AI-generated codebases contain at least one critical vulnerability, averaging 8.3 exploitable findings per application. Meanwhile, 93% of organizations use AI-generated code in development workflows, yet only 12% apply the same security standards as traditional code, according to SQ Magazine's 2026 survey. The result is a widening gap between shipping velocity and security coverage — and attackers are exploiting it. In 2026, 1 in 5 organizations reported a serious security incident linked to AI-generated code, per Aikido Security's survey of 450 developers and security leaders. Traditional SAST tools compound the problem: they produce false positive rates between 30% and 70%, causing teams to ignore warnings entirely. The shift to agentic coding doesn't just accelerate code production — it creates multi-agent chains with emergent behavior, non-deterministic outputs, and tool-use surfaces (file system, shell, APIs) that traditional security models were never designed to analyze. The fundamental problem is a mismatch between static-era tooling and a dynamic-agent reality.

### Why Traditional SAST Breaks Under Agentic Conditions

Traditional SAST tools were designed for a world where humans write code, push it to a branch, and wait for a CI pipeline to run. Agentic tools like Claude Code or Cursor Composer can generate, test, and commit hundreds of lines per minute across multiple files simultaneously. A tool that takes 8 minutes to scan a PR provides zero protection when the agent has already pushed five more commits. The feedback loop must close inside the IDE, in seconds, not after the commit.

AI code also contains 1.7x more bugs overall than human code, including critical and major issues, across multiple industry studies cited in Arnica and Semgrep's 2026 reports. Agentic systems introduce additional attack surface that code scanners alone don't cover: MCP server trust, prompt injection through retrieved documents, hallucinated package names, and overly broad IAM permissions auto-generated in infrastructure code. Securing agentic workflows requires layering traditional SAST with new primitives specific to the agentic attack surface.

## Understanding the Agentic Development Lifecycle (ADLC) and Its Attack Surface

The Agentic Development Lifecycle (ADLC) is a framework introduced by Cycode in 2026 to describe the security-relevant stages of AI-assisted software development — covering how agents plan, execute, and commit code across multi-step workflows. Unlike the traditional SDLC, which assumes human review at every handoff, the ADLC operates at machine speed with autonomous decision-making across tool-use surfaces. The attack surface expands beyond source code to include MCP server connections, model context window poisoning, dependency resolution, infrastructure-as-code generation, and inter-agent communication. Each of these introduces a new class of vulnerability that appears at runtime or before code is written, not just in the final output. Cycode's 2026 research found that 73% of AI systems assessed in security audits showed exposure to prompt injection vulnerabilities, with attack success rates of 50–84%. The ADLC framework maps the security responsibility across four stages: Initialization (agent setup, MCP server configuration, tool authorization), Generation (code synthesis, dependency selection, context retrieval), Validation (testing, SAST scanning, review), and Deployment (CI/CD pipeline enforcement, secrets management). Most organizations in 2026 still treat security as a Validation-only concern, leaving the first two stages completely unprotected.

### Key ADLC Attack Vectors for Cursor and Claude Code Users

The six highest-risk attack vectors in the ADLC for developers using Cursor or Claude Code are: (1) **MCP server compromise** — malicious tool servers injecting instructions into the agent's context; (2) **prompt injection via retrieved documents** — web search or RAG results that redirect agent behavior; (3) **hallucinated dependencies** — roughly 20% of AI-generated package recommendations reference packages that don't exist, which attackers pre-register to deliver malware; (4) **overly broad IAM permissions** — 41% of AI-generated backend code includes overly permissive settings, with misconfigured IAM roles in nearly 50% of AI-assisted cloud deployments; (5) **secrets in generated code** — hardcoded API keys and credentials embedded in generated configuration files; (6) **supply chain attacks via fabricated SBOM** — agents generating infrastructure code that imports or references compromised packages without verification.

## OWASP Top 10 for Agentic Applications 2026: What Cursor and Claude Code Developers Must Know

The OWASP Top 10 for Agentic Applications 2026 is a ranked list of the most critical security risks specific to AI agents — distinct from the traditional web application OWASP Top 10 — covering threats that emerge when AI models plan and execute multi-step tasks autonomously. Published in early 2026, it addresses the reality that agentic systems interact with file systems, APIs, browsers, and databases on behalf of users, creating attack surfaces that traditional application security frameworks don't cover. The top three risks that directly affect Cursor and Claude Code users are: **Prompt Injection** (an attacker embeds instructions in a code comment, README, or retrieved document that redirects the agent's actions), **Insecure Tool Authorization** (the agent has broader tool permissions than the current task requires, enabling privilege escalation), and **Supply Chain Compromise via Fabricated Dependencies** (hallucinated package names resolved to attacker-controlled packages). For teams using Cursor or Claude Code in production workflows, these risks are not theoretical — they represent realistic attack paths that security teams documented in 2025–2026 penetration tests against agentic development environments.

### Mapping OWASP Agentic Risks to Concrete Controls

| OWASP Risk | Claude Code / Cursor Exposure | Recommended Control |
|---|---|---|
| Prompt Injection | Context window poisoning via MCP tools | MCP server allowlisting + Claude Code Hooks |
| Insecure Tool Auth | Overly broad file system / shell access | Minimal-permission tool configuration |
| Supply Chain (hallucinated deps) | AI package recommendations | Dependency lockfile enforcement + SCA scanning |
| Secrets Disclosure | API keys in generated files | Semgrep secrets rules + pre-commit hooks |
| Excessive Agency | Agent commits directly to main | Branch protection + SAST gate in CI |
| Insecure Output Handling | SQL/command injection in generated queries | SAST with taint analysis (Semgrep, Snyk) |
| Overreliance | No human review of AI-generated IaC | Checkov/KICS integration in CI |
| Data Poisoning | Malicious training data in fine-tuned models | Model provenance verification |
| Improper Error Handling | Stack traces exposed in AI-generated APIs | SAST error-handling checks |
| Insecure Plugins | Untrusted MCP servers with excessive permissions | MCP server security audit checklist |

## The MCP Security Threat: How Cursor and Claude Code Became Attack Vectors

MCP (Model Context Protocol) servers are the plugin interface that allows Cursor, Claude Code, VS Code, and Windsurf to call external tools — file systems, databases, APIs, browsers — from inside the agent's context window. In early 2026, security researchers disclosed a critical remote code execution vulnerability class affecting all major agentic IDEs: a poisoned MCP server could inject instructions directly into the model's context, causing the agent to execute arbitrary commands under the developer's credentials. The attack surface is larger than it appears: a single compromised MCP server in a developer's configuration file can exfiltrate API keys, modify source files, push malicious commits, or establish persistence across CI/CD pipelines. The fundamental security problem is that MCP servers operate with implicit trust — the agent treats tool output as authoritative context without cryptographic verification of server identity or output integrity. For Claude Code users, this means a malicious MCP server can override system prompt instructions entirely by injecting higher-priority context. For Cursor users, the same attack vector allows a poisoned MCP tool to redirect Composer actions mid-session. The practical defense is a combination of MCP server allowlisting (only pre-approved servers), read-only tool configuration for untrusted integrations, and Claude Code Hooks that intercept and validate tool outputs before they enter the context window.

### Implementing MCP Server Security for Claude Code

Claude Code's permission system provides three relevant controls for MCP security: server-level permission tiers (read-only vs. read-write), per-project `.claude/settings.json` allow/deny lists for specific tool calls, and Hooks — shell scripts that execute deterministically on defined events (pre-tool-call, post-tool-call, pre-commit). A minimal hardening configuration for a team using Claude Code with external MCP servers should: (1) restrict all MCP file-write tools to the project directory sandbox, (2) add a pre-tool-call hook that logs MCP server calls to an audit trail, (3) use a deny list for shell execution tools when the task doesn't require them, and (4) configure DryRun Security's MCP-native SAST server to intercept generated code before any file write completes.

## Top SAST Tools for Agentic Workflows in 2026 (Ranked and Compared)

The best SAST tools for agentic workflows in 2026 are those with sub-second IDE feedback, MCP-native or plugin integrations for Cursor and Claude Code, and low false positive rates that don't train developers to ignore alerts. Based on testing across 100+ LLMs and real-world agentic workflow deployments, the tools below represent the current state of the art — from free open-source options to enterprise platforms — ranked by fit for teams actively using Cursor and Claude Code. The critical differentiator from traditional SAST is real-time scanning inside the agent loop, not post-commit CI gating alone. Security enforcement must move at the speed of AI code generation.

| Tool | License | IDE Integration | MCP Server | False Positive Rate | Best For |
|---|---|---|---|---|---|
| Semgrep | Free / Pro | VS Code, Cursor, JetBrains | Yes (community) | Low (~15%) | Open-source teams, Claude Code |
| Snyk Code | Free tier / Paid | VS Code, Cursor, JetBrains | Yes | Low (~18%) | Developer-first security |
| DryRun Security | Paid | Claude Code, Cursor, Codex | Native | Very Low (<10%) | PR-level policy enforcement |
| Checkmarx One | Enterprise | VS Code, Cursor, Windsurf | Yes | Medium (~25%) | Enterprise compliance |
| Endor Labs | Paid | VS Code, Cursor | Yes | Very Low (<10%) | Supply chain + reachability |
| Mend SAST | Paid | VS Code, Cursor | Yes | Medium (~22%) | All-in-one SCA + SAST |

### Semgrep — Best Open-Source Integration for Claude Code and Cursor

Semgrep is the leading open-source static analysis framework for agentic workflows, offering a native VS Code extension that runs in Cursor, a community-maintained MCP server for Claude Code integration, and a rule registry with 3,000+ patterns covering OWASP Top 10, secrets detection, and AI-specific vulnerability classes. Semgrep's architecture — pattern-based AST matching rather than full data-flow analysis — makes it fast enough to run on every file save, providing the sub-second feedback loop that agentic workflows require. Semgrep Assistant, available in the Pro tier, adds LLM-powered triage that reduces false positives from the baseline ~30% down to approximately 15%, automatically classifying findings as exploitable, non-exploitable, or context-dependent. For Claude Code specifically, the community MCP server allows the agent itself to query Semgrep findings mid-session, enabling self-correction loops where Claude Code identifies a security finding in generated code and rewrites the vulnerable section before committing. The free tier covers all SAST rules for individual developers; teams need Pro ($40/month per developer) for the Assistant triage and team dashboards. Integration with Cursor requires installing the VS Code extension; integration with Claude Code requires adding the Semgrep MCP server to `.claude/mcp.json`.

### Snyk Code — Best Developer-First SAST with Agent Fix

Snyk Code is a commercial SAST tool with a free tier supporting up to 100 scans per month, offering native integrations for VS Code (and therefore Cursor), JetBrains IDEs, and an MCP server that connects to Claude Code and Codex CLI. Its primary differentiator is DeepCode AI Fix — an LLM-powered remediation feature that generates pull-request-ready code patches for detected vulnerabilities, integrating directly into agentic workflows rather than just flagging issues. In a 2026 head-to-head evaluation by vibe-eval.com, Snyk found 10 of 26 known vulnerabilities in AI-generated test code, with a false positive rate of approximately 18%. Snyk's strength lies in its unified SCA + SAST coverage: a single tool scanning both dependency vulnerabilities (SCA) and code-level issues (SAST) reduces toolchain complexity in agentic setups. The DeepCode Fix MCP integration is particularly valuable for Claude Code users because it enables a workflow where the agent generates code, Snyk Code scans it, and Claude Code automatically applies the suggested fix without breaking the development flow.

### DryRun Security — Best MCP-Native Policy Enforcement

DryRun Security is a 2025-founded security startup that built its product specifically for agentic coding environments, with MCP-native integrations for Claude Code, Cursor, and Codex CLI as its primary delivery mechanism. Unlike traditional SAST tools adapted for AI workflows, DryRun Security was designed to enforce code policy at the PR level within agent-generated workflows — catching issues at the moment the agent proposes a code change rather than after it's committed. Its false positive rate is under 10%, achieved through policy-as-code enforcement (rules are explicit policies, not heuristic scans) combined with context-aware analysis that understands what the agent was trying to accomplish. DryRun Security's MCP server allows Claude Code to query security policies before writing code, providing upfront guidance rather than after-the-fact detection. Pricing is team-based and primarily targets enterprise and mid-market teams; no free tier is available. For teams using Claude Code in enterprise environments with defined security policies (SOC 2, ISO 27001, PCI-DSS), DryRun Security's policy enforcement approach is the most mature purpose-built option in 2026.

### Checkmarx One — Best Enterprise SAST for Large Teams

Checkmarx One is an enterprise application security platform with full SAST, SCA, IaC scanning, and API security capabilities, integrating with VS Code, JetBrains, Cursor, and Windsurf through the Checkmarx Developer Assist plugin. It also offers Checkmarx One Assist — an AI-powered secure coding guidance feature that provides real-time security feedback inside the IDE alongside automated policy enforcement in CI/CD pipelines. In the agentic coding context, Checkmarx One's primary value proposition is compliance coverage: it maps findings directly to regulatory frameworks (NIST, PCI-DSS, SOC 2, ISO 27001), making it the default choice for financial services, healthcare, and government teams that need audit trails alongside security scanning. The false positive rate (~25%) is higher than newer AI-native tools but is mitigated by the AI triage features in the latest release. Checkmarx One is priced per developer seat with enterprise licensing; no self-serve pricing is published. Teams at Checkmarx's scale (10,000+ developers) use it as a compliance backbone while layering faster, lighter tools (Semgrep, Snyk) for real-time IDE feedback.

### Endor Labs — Best for Supply Chain and Reachability Analysis

Endor Labs is a software supply chain security platform that combines SCA with reachability analysis — determining whether a vulnerable dependency is actually called in the execution path, not just present in the dependency tree. This reachability-first approach reduces false positives for dependency alerts by approximately 80% compared to traditional SCA tools that flag all vulnerable packages regardless of whether they're reachable. For agentic workflows, Endor Labs directly addresses the hallucinated dependency threat: its dependency resolution scanning catches packages that don't exist in any public registry before they're installed, preventing dependency confusion attacks triggered by AI-generated package names. The MCP server integration allows Claude Code and Cursor to query Endor Labs' registry before adding a new dependency, embedding supply chain security into the code generation loop. Endor Labs is available via VS Code extension for Cursor integration; pricing is per repository with enterprise licensing for large-scale deployments.

### Mend SAST — Best All-in-One Agentic IDE Security

Mend (formerly WhiteSource) offers a unified SAST + SCA platform with VS Code and Cursor integration through the Mend IDE plugin, providing simultaneous code-level vulnerability scanning and dependency analysis in a single pane of glass. Mend's AI security assistant can suggest fixes for detected vulnerabilities inline, integrating into agentic workflows where Claude Code or Cursor Composer are generating code. Its differentiator is the breadth of language coverage — 30+ programming languages — combined with container and IaC scanning (Terraform, CloudFormation, Kubernetes), making it suitable for polyglot agentic environments that generate infrastructure code alongside application code. False positive rates (~22%) are competitive with traditional SAST tools. Mend is a strong choice for platform engineering teams managing AI-assisted infrastructure-as-code generation where a single tool covering application, dependency, and infrastructure scanning reduces operational overhead.

## How to Integrate SAST into Your Agentic Workflow Step by Step

Integrating SAST into an agentic workflow requires placing security enforcement at three layers simultaneously: inside the IDE (sub-second feedback), at the agent's tool-use boundary (MCP server or Claude Code Hooks), and in CI/CD (mandatory gate before merge). Most teams fail because they rely solely on CI/CD scanning — which runs after the agent has already generated, tested, and staged code — missing the window where fixing a vulnerability costs seconds rather than hours. A practical three-layer integration for a team using Claude Code or Cursor in 2026 looks like this: Layer 1 installs Semgrep's VS Code extension in Cursor (or adds the Semgrep MCP server to Claude Code) for real-time scanning on file save with automatic findings surfaced inline. Layer 2 configures Claude Code Hooks to run `semgrep scan --config=auto` on every pre-commit event, blocking commits that contain critical findings without human override. Layer 3 adds a SAST gate in GitHub Actions (or equivalent) using `semgrep ci` with a fail-on-high-severity policy that blocks PR merge for unacknowledged critical findings. This stack costs $0 for the open-source Semgrep rules and provides coverage at all three stages of the agentic commit lifecycle.

### Configuring Claude Code Hooks for SAST Enforcement

Claude Code Hooks are shell scripts defined in `.claude/settings.json` that execute deterministically on specific agent events — `pre_tool_call`, `post_tool_call`, `pre_commit`, and `stop`. Unlike LLM-based guardrails, Hooks run as external processes and cannot be overridden by prompt injection, making them the appropriate place to enforce non-negotiable security policies. A minimal SAST Hook configuration for Claude Code:

```json
{
  "hooks": {
    "pre_commit": {
      "command": "semgrep scan --config=auto --error --quiet .",
      "on_failure": "block"
    },
    "pre_tool_call": {
      "match": { "tool": "write_file" },
      "command": "semgrep scan --config=p/secrets --error --quiet $CLAUDE_TOOL_INPUT_PATH",
      "on_failure": "block"
    }
  }
}
```

This configuration blocks any commit containing findings at the pre-commit stage and scans every file the agent attempts to write for secrets before the write completes. The `on_failure: "block"` policy requires Claude Code to address the finding before proceeding, creating a self-correction loop rather than a simple alert.

## Secrets Management and Hallucinated Dependency Defense

Secrets management in agentic workflows requires deterministic enforcement at the tool-use layer, not post-hoc detection, because AI agents frequently generate configuration files, environment variable assignments, and infrastructure code that embeds credentials inline. The 2026 threat model for AI-generated secrets exposure has two distinct vectors: direct generation (the agent writes an API key into a `.env` file or Terraform variable) and context leakage (the agent retrieves a secret from the context window and includes it in generated code). GitGuardian's 2026 analysis found that AI-generated code commits contained 3.4x more hardcoded secrets than human-written commits, largely because developers prompt agents with example configurations that include real credentials. The defense strategy combines three controls: (1) Claude Code Hooks that run Semgrep's `p/secrets` ruleset on every file write, blocking writes that contain high-entropy strings matching known secret patterns; (2) `.gitignore` enforcement via a pre-commit Hook that prevents committing known secret file types (`.env`, `*.pem`, `*_credentials.json`); and (3) a secrets management integration (HashiCorp Vault, AWS Secrets Manager, 1Password) that the agent is configured to call for any credential retrieval rather than referencing values directly.

### Defending Against Hallucinated Dependency Attacks

Roughly 20% of AI-generated package recommendations reference dependencies that do not exist in any public package registry, according to Cycode's Securing the ADLC 2026 report. Attackers monitor AI-generated code repositories and package name patterns, then pre-register the hallucinated package names on npm, PyPI, and other registries to deliver malware to any developer who runs `npm install` or `pip install` based on AI suggestions. The practical defense requires three layers: (1) Endor Labs or similar SCA integration that checks whether a recommended package exists and has a legitimate registry history before the agent adds it to `package.json` or `requirements.txt`; (2) a Claude Code Hook or Cursor rule that requires human confirmation before any new dependency is added to a lock file; and (3) dependency pinning policies that require exact version hashes (not semver ranges) in lock files, preventing attackers from hijacking a semver range with a malicious patch release. Teams using Claude Code can configure the agent's system prompt to always prefer established packages with >1,000 weekly downloads and >6 months of registry history when multiple options exist.

## Building a Secure Agentic Coding Culture: Team Policies and Governance

Building a secure agentic coding culture in 2026 means treating security policies as first-class configuration that agents enforce autonomously, not guidelines that humans remember to apply. The governance framework for teams using Cursor and Claude Code should cover four areas: agent scope definition (what tools and file systems the agent may access), output validation policies (which SAST tools must pass before any generated code is committed), escalation paths (which finding classes require human security review, not just agent self-correction), and audit trail requirements (what logging of agent actions is required for compliance purposes). The key cultural shift from traditional DevSecOps is that security rules must be machine-readable and enforced at the API level — not documented in a README that agents may or may not retrieve. For Claude Code teams, this means encoding security policies in `.claude/settings.json` Hooks and in Semgrep custom rules specific to the organization's compliance requirements. For Cursor teams, it means configuring the `.cursorrules` file with explicit security-relevant instructions and ensuring CI/CD gates are non-bypassable. Organizations that treat agentic security as a post-launch concern will face the 1-in-5 serious incident rate that Aikido Security documented; organizations that bake security into the agent's operating parameters will not.

### Recommended Team Policy Checklist for Agentic Security

- [ ] All developers using Claude Code or Cursor have Semgrep (or equivalent) installed and active in the IDE
- [ ] Pre-commit Hooks are configured to block critical SAST findings before any agent commit
- [ ] MCP server configurations are reviewed and restricted to project-directory scope
- [ ] Dependency additions require human confirmation (no silent `package.json` updates by agents)
- [ ] Secrets scanning runs on every file write via Claude Code Hooks
- [ ] CI/CD pipeline includes mandatory SAST gate with fail-on-critical policy
- [ ] Supply chain scanning (Endor Labs or Snyk) runs on every dependency resolution
- [ ] Agent audit logs are enabled and retained for 90 days minimum
- [ ] Security findings are reviewed weekly and SAST rules updated quarterly
- [ ] Hallucinated dependency awareness training is included in developer onboarding

## FAQ

The most common questions about AI code security in agentic workflows center on tool selection, configuration, and the specific threat vectors that Claude Code and Cursor introduce. The answers below reflect the 2026 state of SAST tooling, MCP security research, and real-world deployments in organizations that have moved from traditional DevSecOps to agentic-first development. Key context: 92% of AI-generated codebases contain critical vulnerabilities, 93% of organizations use AI-generated code, and only 12% apply equivalent security standards — meaning most developers working with Cursor or Claude Code today are operating without adequate coverage. The questions below address the highest-impact gaps: dependency security, commit-time enforcement, MCP server risks, and infrastructure code scanning. Each answer provides a specific, actionable recommendation rather than general guidance, because in agentic security the difference between a configured control and an unconfigured one is the difference between catching a vulnerability in seconds versus discovering it in a post-incident review.

### What is the biggest security risk in using Claude Code or Cursor for development in 2026?

The biggest risk is the combination of hallucinated dependencies and prompt injection via MCP servers. Roughly 20% of AI-generated package recommendations point to nonexistent packages that attackers pre-register, and 73% of AI systems in 2026 audits were vulnerable to prompt injection. Both risks can be mitigated with Semgrep scanning (secrets and code vulnerabilities) plus dependency verification before installation.

### Is Semgrep good enough for securing agentic workflows, or do I need a paid tool?

Semgrep's free tier with the `auto` and `p/secrets` rulesets covers the most common vulnerability classes in AI-generated code and is sufficient for individual developers and small teams. The free tier covers real-time IDE scanning in Cursor and MCP server integration with Claude Code. Teams needing AI-powered false positive triage, SOC 2 compliance reporting, or centralized dashboards should upgrade to Semgrep Pro (~$40/month per developer).

### How do I configure Claude Code to block commits that contain security vulnerabilities?

Add a `pre_commit` Hook to `.claude/settings.json` that runs `semgrep scan --config=auto --error .` with `"on_failure": "block"`. This causes Claude Code to halt any commit containing Semgrep findings at critical or high severity, requiring the agent to self-correct before the commit completes. For secrets specifically, add a second Hook on `pre_tool_call` for `write_file` events running `semgrep scan --config=p/secrets`.

### What are MCP server security risks and how do I minimize them?

MCP servers execute with the same trust level as the developer's shell session, making them a high-value attack target. A compromised MCP server can inject instructions into Claude Code's context, exfiltrate repository contents, or modify files outside the project directory. Minimize risk by: (1) only connecting MCP servers from vendors with published security disclosures, (2) restricting MCP file-write tools to the project directory sandbox in `.claude/settings.json`, (3) auditing MCP server source code before use, and (4) disabling MCP servers when not actively needed.

### Do SAST tools work on AI-generated infrastructure code (Terraform, CloudFormation)?

Yes — Checkmarx One, Mend SAST, and Snyk all support IaC scanning for Terraform, CloudFormation, Kubernetes manifests, and Dockerfiles. For teams generating infrastructure code with Claude Code, adding `checkov` (open-source) or `tfsec` as a Claude Code Hook for IaC file writes provides free coverage. Checkov covers 750+ IaC security policies and integrates easily into the same Hook configuration as Semgrep, covering the misconfigured IAM roles that appear in ~50% of AI-generated cloud deployments.
