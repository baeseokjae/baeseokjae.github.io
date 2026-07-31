---
title: "Agent Scanner GitHub: AI Agent Detection Across Repositories in 2026"
date: 2026-07-31T21:03:08+00:00
tags:
  - agent scanner
  - AI agent detection
  - GitHub security
  - agent security
  - supply chain security
  - MCP security
  - EU AI Act
description: "A comprehensive review of the top 8 agent scanners for detecting AI agents across GitHub repositories, comparing features, detection methods, and use cases."
draft: false
cover:
  image: "/images/agent-scanner-github-ai-agent-detection-2026.png"
  alt: "Agent Scanner GitHub: AI Agent Detection Across Repositories in 2026"
  relative: false
schema: "schema-agent-scanner-github-ai-agent-detection-2026"
---

## What Is an Agent Scanner for GitHub AI Agent Detection?

An agent scanner for GitHub AI agent detection is a security tool that scans repositories to identify, inventory, and assess the security posture of autonomous AI agents, their skills, MCP server configurations, and tool permissions. These scanners emerged rapidly in 2026 after the ClawHavoc campaign planted over 1,200 malicious skills into agent marketplaces, and the market has since grown to over 95 open-source tools on GitHub. They serve as the first line of defense for organizations adopting AI agents at scale, enabling teams to detect shadow AI, enforce compliance with regulations like the EU AI Act, and prevent supply-chain attacks on agent ecosystems.

## The Rise of AI Agent Security Scanners in 2026

The first half of 2026 witnessed an explosion in AI agent security scanning tools. Before January 2026, the category barely existed. Then the ClawHavoc campaign demonstrated that agent marketplaces could be weaponized at scale — 1,200 malicious skills infiltrated platforms, and researchers catalogued over 6,000 malicious agent tools. The CVE-2026-25253 disclosure, the first remote code execution vulnerability in agent software, further accelerated demand.

By July 2026, GitHub hosted over 95 repositories dedicated to AI agent security scanning. The driving forces behind this growth include:

- **The ClawHavoc wake-up call:** Organizations realized that agent skills — downloaded and executed with minimal vetting — represent a massive attack surface.
- **EU AI Act compliance:** The August 2026 compliance deadline for AI agents has pushed enterprises to adopt scanning tools. An estimated 97% of AI agent code is reportedly non-compliant.
- **Supply chain security maturity:** The agent ecosystem now mirrors the npm/PyPI security crisis of the mid-2010s, and the community is responding with analogous tooling.
- **Open-source momentum:** Every major scanner in this review is open source under MIT or Apache-2.0 licenses, creating a community-driven security ecosystem.

## NVIDIA SkillSpector — The 14K-Star Market Leader

**GitHub:** [NVIDIA/SkillSpector](https://github.com/NVIDIA/SkillSpector)  
**Stars:** 14,002 | **Forks:** 1,164 | **License:** Apache-2.0 | **Language:** Python

NVIDIA SkillSpector is the undisputed market leader in AI agent skill security scanning. Created in March 2026 and actively maintained through July 2026, it has accumulated 14,002 GitHub stars and 1,164 forks — more than all other tools in this review combined.

SkillSpector focuses on detecting vulnerabilities, malicious patterns, and security risks specifically in agent skills. Its Python codebase and Apache-2.0 licensing make it accessible for enterprise adoption. With 93 open issues, the project shows active community engagement and ongoing development.

**Key strengths:**
- Largest community and ecosystem of any agent scanner
- NVIDIA backing ensures long-term maintenance
- Comprehensive vulnerability detection for agent skills
- Active issue tracker with rapid response times

**Limitations:**
- Focused primarily on skill-level scanning, not runtime detection
- No eBPF or kernel-level monitoring
- Limited support for non-Python agent frameworks

## AgentShield — Multi-Platform Security for Agent Configurations

**GitHub:** [affaan-m/agentshield](https://github.com/affaan-m/agentshield)  
**Stars:** 1,034 | **Forks:** 218 | **License:** MIT | **Language:** TypeScript

AgentShield has carved out a strong position as a multi-platform AI agent security scanner with 1,034 stars. Its key differentiator is platform versatility — it ships as a CLI tool, GitHub Action, ECC plugin, and GitHub App. This multi-format approach means teams can integrate it into CI/CD pipelines, IDE workflows, and repository-level scanning without friction.

AgentShield detects vulnerabilities in agent configurations, MCP servers, and tool permissions. It has strong support for the Anthropic ecosystem, including Claude Code, making it the go-to choice for teams building on Anthropic's agent platform.

**Key strengths:**
- Four deployment formats (CLI, GitHub Action, ECC plugin, GitHub App)
- Strong MCP server scanning capabilities
- TypeScript codebase aligns with modern JavaScript/TypeScript stacks
- MIT license with no restrictions

**Limitations:**
- Smaller community than SkillSpector
- Limited to configuration-level scanning (no runtime detection)
- Anthropic ecosystem focus may not suit all frameworks

## Ship-Safe — CI/CD and Supply Chain Security Focus

**GitHub:** [asamassekou10/ship-safe](https://github.com/asamassekou10/ship-safe)  
**Stars:** 773 | **Forks:** 84 | **License:** MIT | **Language:** JavaScript

Ship-Safe positions itself as a CLI security scanner for the agentic era, with 773 stars and a focused feature set. It detects CI/CD misconfigurations, agent permission risks, MCP tool injection, hardcoded secrets, and DMCA-flagged AI dependencies.

What sets Ship-Safe apart is its OWASP-aligned static analysis approach. By mapping findings to the OWASP framework, it provides security teams with familiar classification and remediation guidance. This alignment makes it easier for traditional AppSec teams to adopt agent security scanning without learning an entirely new taxonomy.

**Key strengths:**
- OWASP-aligned findings for easy integration with existing security workflows
- Broad detection scope (CI/CD, secrets, MCP injection, dependencies)
- JavaScript/Node.js ecosystem compatibility
- Lightweight CLI with fast scan times

**Limitations:**
- No runtime or kernel-level detection
- Smaller community and fewer integrations
- Limited framework support compared to SkillSpector

## AgentDiscover — Agentic Identity and Multi-Layer Inventory

**GitHub:** [Defend-AI-Tech-Inc/agent-discover-scanner](https://github.com/Defend-AI-Tech-Inc/agent-discover-scanner)  
**Stars:** 18 | **Forks:** 20+ | **License:** MIT | **Language:** Multi-language

AgentDiscover Scanner, despite its modest 18 stars, is described as an industry-standard Agentic Identity and Inventory Scanner. It employs a multi-layer detection approach combining static analysis, network heuristics, and eBPF (extended Berkeley Packet Filter) for runtime agent detection.

This tool automatically inventories autonomous agents built with LangChain, AutoGen, CrewAI, and PydanticAI. It is positioned as a foundational tool for AIBOM (AI Bill of Materials) compliance and AgentOps governance, with support for zero-trust architectures and shadow AI detection.

**Key strengths:**
- Multi-layer detection (static + network + eBPF)
- Runtime agent discovery in Kubernetes environments
- AIBOM generation for compliance
- Zero-trust and shadow AI detection capabilities

**Limitations:**
- Very small community and limited adoption
- Early-stage project with fewer integrations
- Higher complexity due to eBPF requirements

## ClawShield — Runtime Proxy Protection with eBPF

**GitHub:** [SleuthCo/clawshield-public](https://github.com/SleuthCo/clawshield-public)  
**Stars:** 130 | **Forks:** — | **License:** Apache-2.0 | **Language:** Go

ClawShield takes a fundamentally different approach to agent security. Rather than scanning repositories for vulnerable code, it operates as a security proxy for AI agents with defense-in-depth architecture. It combines a Go-based proxy, iptables firewall, and eBPF kernel monitor to inspect every message an agent sends and receives.

ClawShield scans each message for prompt injection, PII leakage, and secrets exposure. Its YAML-based policy engine allows teams to define custom security rules, and its audit logging provides a complete trail of agent activity. The project supports 5 AI agents with RAG knowledge bases.

**Key strengths:**
- Runtime protection, not just static analysis
- eBPF kernel-level monitoring for deep visibility
- Real-time prompt injection and PII detection
- YAML policy engine for custom rules
- Comprehensive audit logging

**Limitations:**
- Not a repository scanner — complementary, not a replacement
- Higher operational overhead (proxy deployment)
- Smaller community and fewer integrations

## Aguara — Open Source Security Engine for Supply-Chain Trust

**GitHub:** [garagon/aguara](https://github.com/garagon/aguara)  
**Stars:** 85 | **Forks:** 15 | **License:** Apache-2.0 | **Language:** Go

Aguara is an open-source security engine focused on AI agent and supply-chain trust. Built in Go with an Apache-2.0 license, it covers prompt injection detection, secrets discovery, tool poisoning analysis, and supply-chain security verification.

Aguara integrates with GitHub Actions, npm, pnpm, and PyPI, making it suitable for teams that need to scan dependencies across multiple package ecosystems. Its Go codebase offers strong performance characteristics for large-scale repository scanning.

**Key strengths:**
- Go-based for high-performance scanning
- Multi-ecosystem integration (npm, pnpm, PyPI, GitHub Actions)
- Supply-chain security focus
- Covers prompt injection, secrets, and tool poisoning

**Limitations:**
- Smaller community (85 stars)
- No runtime or eBPF detection
- Limited framework-specific support

## SkillFortify — Formal Verification for Mathematical Guarantees

**GitHub:** [varun369/skillfortify](https://github.com/varun369/skillfortify)  
**Stars:** 27 | **Forks:** — | **License:** — | **Language:** —

SkillFortify represents a paradigm shift in agent security scanning. It is the first formal verification scanner for AI agent skills, achieving an F1 score of 96.95%, precision of 100%, and recall of 94.07% on a benchmark of 540 skills. These results are backed by a peer-reviewed paper published on Zenodo.

Rather than relying on pattern matching or heuristics, SkillFortify applies formal methods to mathematically prove the absence of certain vulnerability classes. It supports 22 frameworks including MCP, LangChain, and CrewAI, and generates SBOM (Software Bill of Materials) documents for agent skills.

**Key strengths:**
- Formal verification provides mathematical guarantees
- Industry-leading accuracy metrics (F1=96.95%, Precision=100%)
- Peer-reviewed methodology
- 22 framework support
- SBOM generation for compliance

**Limitations:**
- Very early stage (27 stars)
- Formal verification may have higher false negative rates for novel attack patterns
- Limited community and ecosystem

## G0 — The Comprehensive Control Layer for AI Agents

**GitHub:** [guard0-ai/g0](https://github.com/guard0-ai/g0)  
**Stars:** 48 | **Forks:** — | **License:** AGPL-3.0 | **Language:** TypeScript

G0 (pronounced "guard-zero") describes itself as the control layer for AI agents. It ships with over 1,200 rules across 12 security domains, supporting 10 agent frameworks and 4,000+ adversarial payloads. Its workflow model covers the full lifecycle: discover, assess, test, monitor, and comply.

G0's TypeScript codebase and AGPL-3.0 license make it suitable for open-source projects, though the AGPL license may be a consideration for commercial use. Its comprehensive rule set and adversarial payload library make it one of the most thorough static analysis tools available.

**Key strengths:**
- Largest rule set (1,200+ rules across 12 domains)
- 4,000+ adversarial payloads for testing
- Full lifecycle coverage (discover → assess → test → monitor → comply)
- 10 framework support

**Limitations:**
- AGPL-3.0 license may restrict commercial use
- No runtime detection capabilities
- Smaller community (48 stars)

## Comparison Matrix — Features, Detection Methods, and Use Cases

| Tool | Stars | Detection Method | Key Focus | License | Language |
|------|-------|-----------------|-----------|---------|----------|
| SkillSpector | 14,002 | Static analysis | Agent skill vulnerabilities | Apache-2.0 | Python |
| AgentShield | 1,034 | Static analysis | Config, MCP, tool permissions | MIT | TypeScript |
| Ship-Safe | 773 | Static analysis (OWASP) | CI/CD, secrets, MCP injection | MIT | JavaScript |
| AgentDiscover | 18 | Static + network + eBPF | Agent inventory, AIBOM, shadow AI | MIT | Multi |
| ClawShield | 130 | Runtime proxy + eBPF | Prompt injection, PII, secrets | Apache-2.0 | Go |
| Aguara | 85 | Static analysis | Supply chain, prompt injection | Apache-2.0 | Go |
| SkillFortify | 27 | Formal verification | Mathematical vulnerability proof | — | — |
| G0 | 48 | Static analysis | Comprehensive rule engine | AGPL-3.0 | TypeScript |

| Tool | Runtime Detection | CI/CD Integration | MCP Scanning | SBOM/AIBOM | Framework Support |
|------|:-----------------:|:-----------------:|:------------:|:----------:|:-----------------:|
| SkillSpector | No | Yes | Partial | No | Python agents |
| AgentShield | No | Yes (GitHub Action) | Yes | No | Anthropic/Claude |
| Ship-Safe | No | Yes | Yes | No | General |
| AgentDiscover | Yes (eBPF) | Yes | No | Yes (AIBOM) | LangChain, AutoGen, CrewAI, PydanticAI |
| ClawShield | Yes (eBPF) | No (runtime proxy) | No | No | General (proxy-based) |
| Aguara | No | Yes (GitHub Actions) | No | No | General |
| SkillFortify | No | No | Yes | Yes (SBOM) | 22 frameworks |
| G0 | No | Yes | Yes | No | 10 frameworks |

## How to Choose the Right Agent Scanner for Your GitHub Repos

Selecting the right agent scanner depends on your specific use case and security requirements:

**For maximum community support and breadth:** Choose NVIDIA SkillSpector. Its 14,002 stars, active maintenance, and NVIDIA backing make it the safest bet for organizations that need a well-supported, actively developed tool.

**For Anthropic/Claude Code ecosystems:** Choose AgentShield. Its multi-format deployment (CLI, GitHub Action, ECC plugin, GitHub App) and strong MCP server scanning make it ideal for teams building on Anthropic's platform.

**For OWASP-aligned security teams:** Choose Ship-Safe. Its OWASP classification framework means traditional AppSec teams can adopt it without learning a new taxonomy.

**For runtime detection and agent inventory:** Choose AgentDiscover. Its multi-layer approach (static + network + eBPF) is the only option that provides runtime agent discovery in Kubernetes environments.

**For real-time runtime protection:** Choose ClawShield. If you need to monitor agent behavior in production — detecting prompt injection, PII leakage, and secrets in real time — ClawShield's proxy-based approach is unique.

**For mathematical guarantees:** Choose SkillFortify. If your compliance requirements demand provable security properties, formal verification is the only path.

**For comprehensive rule-based scanning:** Choose G0. Its 1,200+ rules and 4,000+ adversarial payloads provide the most thorough static analysis coverage.

## The Future of AI Agent Detection — Trends and Predictions

Several trends will shape the agent scanner landscape through the remainder of 2026 and into 2027:

**Convergence of static and runtime detection:** The most effective tools will combine repository scanning (static analysis) with runtime monitoring (eBPF, proxies). AgentDiscover and ClawShield represent early examples of this convergence.

**Formal verification becomes mainstream:** SkillFortify's peer-reviewed results (F1=96.95%) demonstrate that formal methods can outperform heuristic approaches. Expect more tools to adopt formal verification as the methodology matures.

**EU AI Act compliance drives adoption:** With the August 2026 deadline approaching and 97% of agent code reportedly non-compliant, compliance scanning will become a must-have feature rather than a differentiator.

**AIBOM standards emerge:** Just as SBOM became standard for software supply chain security, AIBOM (AI Bill of Materials) will become standard for agent ecosystems. Tools that generate AIBOM documents will have a compliance advantage.

**Consolidation ahead:** The current landscape of 95+ tools is unsustainable. Expect consolidation through acquisitions or feature absorption as the market matures, with NVIDIA SkillSpector well-positioned as the platform leader.

## Frequently Asked Questions

### What is an agent scanner for GitHub?

An agent scanner for GitHub is a security tool that scans repositories to detect AI agents, their skills, configurations, and MCP server setups. It identifies vulnerabilities, malicious patterns, and compliance issues in agent-related code, helping organizations secure their AI agent deployments.

### How do agent scanners detect AI agents in repositories?

Agent scanners use multiple detection methods: static analysis scans code for agent framework signatures (LangChain, AutoGen, CrewAI), configuration patterns (MCP server definitions), and known vulnerability patterns. Advanced scanners like AgentDiscover add network heuristics and eBPF-based runtime detection for agents operating in Kubernetes environments.

### Why did agent security scanners explode in popularity in 2026?

The ClawHavoc campaign in January 2026 planted 1,200 malicious skills into agent marketplaces, demonstrating the real-world risk of unvetted agent code. Combined with the CVE-2026-25253 RCE disclosure and the EU AI Act's August 2026 compliance deadline, organizations rushed to adopt scanning tools. The market grew from zero to 95+ tools in six months.

### Which agent scanner has the best detection accuracy?

SkillFortify leads in accuracy with an F1 score of 96.95%, precision of 100%, and recall of 94.07% on a 540-skill benchmark, backed by a peer-reviewed paper. However, its formal verification approach may miss novel attack patterns that heuristic tools would catch. The best choice depends on whether you prioritize mathematical guarantees or broad coverage.

### Do I need both a repository scanner and a runtime scanner?

Yes, for comprehensive security. Repository scanners (SkillSpector, AgentShield, Ship-Safe) catch vulnerabilities before deployment, while runtime scanners (ClawShield, AgentDiscover) detect attacks during operation. The emerging best practice is a defense-in-depth approach combining static analysis, CI/CD scanning, and runtime monitoring with eBPF or proxy-based protection.
