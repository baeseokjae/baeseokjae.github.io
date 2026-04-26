---
title: "CAI Open-Source Security Agent Framework: Build and Deploy Offensive AI Security Agents"
date: 2026-04-25T15:04:16+00:00
tags: ["cybersecurity", "ai-agents", "penetration-testing", "open-source", "python"]
description: "Complete guide to CAI, the open-source cybersecurity AI framework that won 41/45 CTF flags and delivers 91% solve rates for automated pentesting."
draft: false
cover:
  image: "/images/cai-open-source-security-agent-guide-2026.png"
  alt: "CAI Open-Source Security Agent Framework: Build and Deploy Offensive AI Security Agents"
  relative: false
schema: "schema-cai-open-source-security-agent-guide-2026"
---

CAI (Cybersecurity AI) is an open-source framework from Alias Robotics that lets security engineers build, orchestrate, and deploy autonomous AI agents for offensive security tasks — from reconnaissance to exploitation, bug bounty automation to CTF solving. Install it with `pip install cai-framework`, point it at a target, and it handles the full pentest loop without step-by-step human direction.

## What Is CAI? The Open-Source Cybersecurity AI Framework Explained

CAI is an open-source cybersecurity AI framework developed by Alias Robotics that provides a structured, modular foundation for building autonomous security agents capable of performing offensive tasks — reconnaissance, vulnerability scanning, exploitation, and privilege escalation — with minimal human intervention. Unlike running an LLM against a system prompt and hoping for the best, CAI wraps the AI loop in a production-ready architecture: structured agent definitions, reusable tool libraries, handoff protocols between agents, input/output guardrails, and human-in-the-loop (HITL) checkpoints. The framework supports over 300 AI models including OpenAI GPT-4o, Anthropic Claude, DeepSeek, and local deployments via Ollama — meaning you can run fully air-gapped without a cloud dependency.

In 2025, CAI proved it was not a research toy. It won the Neurogrid CTF, capturing 41 of 45 available flags and the $50,000 top prize. In the Cyber Apocalypse CTF 2025, competing against 8,129 teams, it outperformed 99.7% of participants at peak — while only running for 3 of the 72 available hours. Across all major CTF events in 2025, CAI achieved a 99.04% mean percentile ranking. Against real-world targets like vulnbank.org, it identified SQL injection vulnerabilities allowing full account takeover. The framework delivers 91% solve rates and 98% cost reduction versus traditional security testing approaches.

## Installing CAI: From Zero to Running Your First Security Agent

CAI installation follows standard Python tooling and takes under five minutes on any system with Python 3.10+. The framework is distributed via PyPI, with optional extras for specific integrations.

```bash
# Basic installation
pip install cai-framework

# With all optional dependencies (recommended for security work)
pip install cai-framework[all]

# Verify installation
cai --version
```

Before running your first agent, set your model provider credentials. CAI reads these from environment variables:

```bash
# For Anthropic Claude (recommended for complex reasoning)
export ANTHROPIC_API_KEY="sk-ant-..."

# For OpenAI
export OPENAI_API_KEY="sk-..."

# For local Ollama (air-gapped environments)
# No API key needed — just ensure Ollama is running
```

The fastest way to validate the install is to run CAI's built-in interactive mode against a test target. The Alias Robotics team maintains a deliberately vulnerable practice environment:

```bash
# Launch CAI interactive mode
cai

# Inside the CAI shell, run against DVWA or a local test box
> target 10.10.10.10
> agent recon
> run
```

CAI's interactive mode gives you a REPL where you compose agent pipelines before executing them. For production use, you'll define agents programmatically in Python — which is where the real power surfaces.

## CAI's 8-Pillar Architecture: A Deep Dive

CAI is built around eight architectural pillars that together create a reliable, auditable security automation pipeline. Understanding these pillars is essential before building custom agents, because each one maps to a specific failure mode in naive LLM-based security automation.

**Agents** are the core execution unit. Each agent is a structured object with a defined role, a set of allowed tools, a system prompt scoped to its function, and optional handoff targets. You don't instantiate a generic "security AI" — you define a recon agent, an exploitation agent, a reporting agent, each with a narrow charter.

**Tools** are Python functions exposed to agents as callable actions. CAI ships with pre-built tools for port scanning (nmap integration), web crawling, SQL injection probing, SSH connection management, and CVE lookup. You can extend this with your own tools decorated with `@cai_tool`.

**Handoffs** are the protocol by which one agent transfers control to another, passing context and artifacts. A recon agent that finds an open SSH port can hand off to an SSH brute-force agent with the discovered credentials list — without you writing the orchestration glue.

**Patterns** are reusable agent workflow templates. CAI ships patterns for vulnerability assessment, privilege escalation, lateral movement, and report generation.

**Turns** are the unit of agent execution. Each turn, the agent receives context, reasons, picks a tool or handoff, executes, and returns an observation. CAI tracks turn history for debugging and audit logs.

**Tracing** provides structured logs of every agent action, tool call, model inference, and handoff. Traces are exportable to JSON and integrate with observability platforms.

**Guardrails** are input and output filters that block unsafe commands, detect prompt injection attempts, and enforce scope constraints (e.g., "only target this IP range").

**HITL (Human-in-the-Loop)** checkpoints pause execution before high-risk actions — destructive exploits, data exfiltration, privilege escalation — and wait for human confirmation. You configure which action categories require approval.

## Building Your First Offensive Security Agent with CAI

A complete, functional CAI agent requires three components: a role definition, a tool set, and execution logic. Here is a minimal but real reconnaissance agent you can adapt for authorized testing:

```python
from cai import Agent, run
from cai.tools import nmap_scan, whois_lookup, dns_enumerate

recon_agent = Agent(
    name="ReconAgent",
    model="claude-sonnet-4-6",
    instructions="""
    You are a reconnaissance specialist. Your goal is to map the attack surface
    of the target system. Use nmap for port/service discovery, DNS enumeration
    for subdomain mapping, and WHOIS for ownership context.
    
    Always start with passive reconnaissance before active scanning.
    Report open ports, running services with version info, and any
    identified subdomains in a structured JSON format.
    
    Scope: {target}. Do not scan outside this scope.
    """,
    tools=[nmap_scan, whois_lookup, dns_enumerate],
)

result = run(recon_agent, target="10.10.10.10")
print(result.report)
```

The `run()` call handles the agentic loop — the agent reasons about which tool to call next, executes it, observes the result, and continues until it determines reconnaissance is complete or hits a turn limit.

For a more realistic workflow, chain a recon agent into a vulnerability assessment agent:

```python
from cai import Agent, run
from cai.tools import nmap_scan, nikto_scan, sqlmap_probe
from cai.handoffs import create_handoff

vuln_agent = Agent(
    name="VulnAssessAgent",
    model="claude-sonnet-4-6",
    instructions="""
    You receive a recon report. Your job is to identify exploitable vulnerabilities
    in the discovered services. Probe web services with nikto, test for SQL injection
    on identified endpoints with sqlmap in safe/read-only mode.
    
    Prioritize findings by CVSS score. Output a structured vulnerability report.
    """,
    tools=[nikto_scan, sqlmap_probe],
)

recon_agent.handoffs = [create_handoff(vuln_agent, condition="recon_complete")]

result = run(recon_agent, target="10.10.10.10")
```

When recon finishes, the framework automatically invokes the handoff condition, packages the recon context, and starts the vuln agent — no manual wiring required.

## Tools and Handoffs: Modular Security Automation at Scale

CAI's tool system is one of its strongest design decisions. Every action an agent can take is a Python function registered as a tool — this means every capability is auditable, testable, and replaceable without touching the agent logic.

The built-in tool library covers the full offensive security kill chain. Network tools include nmap, masscan, and netcat wrappers. Web tools cover dirbusting, parameter fuzzing, and HTTP request manipulation. Exploitation tools integrate Metasploit module execution and custom payload delivery. Post-exploitation tools handle shell management, file transfer, and privilege escalation checks.

Registering a custom tool requires a single decorator:

```python
from cai import cai_tool
import subprocess

@cai_tool
def run_custom_scan(target: str, port: int, flags: str = "") -> str:
    """
    Run a custom nmap scan against a specific port.
    
    Args:
        target: IP address or hostname to scan
        port: Port number to probe
        flags: Additional nmap flags (e.g., '-sV -sC')
    
    Returns:
        Raw nmap output as string
    """
    cmd = f"nmap {flags} -p {port} {target}"
    result = subprocess.run(cmd.split(), capture_output=True, text=True, timeout=60)
    return result.stdout
```

The docstring is critical — CAI's underlying LLM reads it to decide when and how to use the tool. Clear argument descriptions and return value documentation directly impact agent decision quality.

Handoffs solve the coordination problem in multi-agent security automation. When a recon agent discovers a web application, it shouldn't try to exploit it — that's a different role, different tools, different reasoning. Handoffs let you enforce this separation while preserving context continuity:

```python
from cai.handoffs import Handoff

# Define a conditional handoff: only trigger if a web service was found
web_handoff = Handoff(
    target=web_exploitation_agent,
    condition=lambda ctx: "http" in ctx.discovered_services,
    context_transform=lambda ctx: {
        "target_url": ctx.web_endpoints,
        "recon_data": ctx.full_report
    }
)
```

The `context_transform` function shapes what context gets passed to the next agent — you can strip irrelevant data, add metadata, or enrich with external lookups before the hand-off occurs.

## Guardrails and HITL: Running CAI Safely in Production

Running autonomous offensive AI agents without guardrails is how you end up in a compliance incident. CAI's guardrail system provides layered protection: input validation that blocks out-of-scope targets before any tool executes, output filtering that catches accidental credential logging, and semantic guardrails that use a secondary LLM call to classify action risk before execution.

Setting up scope-enforcement guardrails is the first thing to configure on any CAI deployment:

```python
from cai.guardrails import ScopeGuardrail, PromptInjectionGuardrail

scope_guard = ScopeGuardrail(
    allowed_targets=["10.10.10.0/24", "vulnbank.org"],
    block_on_violation=True,
    alert_on_violation=True,
)

injection_guard = PromptInjectionGuardrail(
    sensitivity="high",  # block if injection probability > 0.7
)

agent = Agent(
    name="PentestAgent",
    model="claude-sonnet-4-6",
    instructions="...",
    tools=[...],
    input_guardrails=[scope_guard, injection_guard],
)
```

The HITL system is where CAI's approach to responsible automation becomes operationally concrete. Rather than letting agents execute any action autonomously, you define a risk taxonomy and assign checkpoint requirements:

```python
from cai.hitl import HITLConfig, RiskLevel

hitl_config = HITLConfig(
    require_approval=[
        RiskLevel.DESTRUCTIVE,      # data deletion, service disruption
        RiskLevel.EXFILTRATION,     # file downloads, data extraction
        RiskLevel.PRIVILEGE_ESC,    # sudo, privilege escalation attempts
    ],
    auto_approve=[
        RiskLevel.PASSIVE_RECON,    # whois, DNS, passive scanning
        RiskLevel.ACTIVE_RECON,     # nmap, service fingerprinting
    ],
    approval_timeout=300,           # seconds before auto-deny
    approval_channel="slack",       # where approval requests go
)
```

When an agent attempts a destructive action, CAI pauses, serializes the action context, sends an approval request to your configured channel (Slack, email, webhook), and waits. If no approval arrives within the timeout, the action is denied and the agent proceeds to the next available path.

## Multi-Agent Patterns: Swarm, Hierarchical, and Parallel Coordination

CAI supports three primary multi-agent coordination patterns, each suited to different security automation scenarios. Choosing the wrong pattern is the most common mistake teams make when scaling beyond single-agent workflows.

**Swarm coordination** deploys multiple peer agents against the same target simultaneously. Each agent works a different attack vector — one probing web services, another testing authentication, a third checking for known CVEs in discovered software. Swarm is ideal for broad vulnerability assessment where time is the constraint. CAI's Dragos OT CTF performance (Rank 1 in hours 7-8, 32/34 challenges, 37% velocity advantage over top human teams) was largely achieved through swarm coordination across different challenge categories.

```python
from cai.patterns import SwarmPattern

swarm = SwarmPattern(
    agents=[web_recon_agent, auth_probe_agent, cve_scan_agent],
    coordination="parallel",
    merge_strategy="union",  # combine all findings into one report
)

result = swarm.run(target="10.10.10.10")
```

**Hierarchical coordination** uses a manager agent to direct specialist agents. The manager receives the initial objective, decomposes it into subtasks, assigns agents, and synthesizes results. This pattern is best for complex, multi-phase engagements where the sequence matters:

```python
from cai.patterns import HierarchicalPattern

pentest_manager = Agent(
    name="PentestManager",
    model="claude-opus-4-7",  # stronger model for orchestration
    instructions="Decompose the pentest objective into phases. Coordinate specialists.",
    handoffs=[recon_agent, web_agent, exploitation_agent, reporting_agent],
)

engagement = HierarchicalPattern(manager=pentest_manager)
result = engagement.run(objective="Full pentest of 10.10.10.10", scope="10.10.10.0/24")
```

**Chain-of-Thought coordination** passes enriched context sequentially through a pipeline. Output from each agent becomes the input to the next. Use this for workflows where each phase depends entirely on the previous one's findings:

```python
from cai.patterns import ChainPattern

pentest_chain = ChainPattern(
    stages=[recon_agent, vuln_agent, exploitation_agent, post_exploit_agent, reporting_agent]
)

result = pentest_chain.run(target="10.10.10.10")
```

For CTF scenarios where challenges are independent, swarm wins. For red team engagements with clear kill-chain phases, hierarchical with a strong orchestrator model delivers better results. Chain is best for bug bounty automation where the pipeline is fixed and sequential.

## CAI's CTF Track Record: Benchmark Results That Matter

CTF performance is the most rigorous available benchmark for offensive security AI — challenges are designed by experts, scored objectively, and run against identical conditions for all participants. CAI's 2025 results are the most compelling case for production adoption of any open-source security framework.

The headline numbers tell a clear story. At Neurogrid CTF 2025, CAI captured 41 of 45 available flags and took the $50,000 first prize — outright, not in a separate "AI track." At Cyber Apocalypse CTF 2025, competing against 8,129 teams from the global security community, CAI outperformed 99.7% of teams at peak performance while only running for 3 of the 72 available hours. Had it competed for the full duration, the gap would have been larger. Across all tracked CTF events in 2025, CAI maintained a 99.04% mean percentile ranking.

The Dragos ICS/OT CTF is particularly significant because OT security is considered one of the hardest domains — specialized protocols, legacy systems, limited public tooling. CAI achieved Rank 1 during the competition's peak hours (7-8), completing 32 of 34 challenges with a 37% velocity advantage over top human teams. This is not a domain where general-purpose AI typically excels.

Speed benchmarks reveal the magnitude of the capability gap. CAI solves specific challenge types up to 3,600 times faster than human competitors, with an average of 11x faster across all challenge categories. CAI v0.6.0 beats the next-best AI agent framework by 2.6x in Attack & Defense CTF formats — the most operationally realistic competition format.

The practical implication for security teams: CAI's CTF performance correlates with real-world pentest efficiency. The same multi-agent coordination, tool chains, and reasoning patterns that flag CTF challenges also identify vulnerabilities in production systems.

## CAI vs. PentestGPT vs. PentAGI: Choosing the Right Framework

Three open-source AI security frameworks dominate the 2026 landscape. Choosing between them requires honest evaluation of your team's constraints and use case requirements.

| Framework | CTF Performance | Real-World Testing | Model Support | Air-Gap Capable | Active Maintenance |
|-----------|----------------|---------------------|---------------|-----------------|-------------------|
| **CAI** | 99.04% mean percentile | High (vulnbank.org SQL injection, multiple CVEs) | 300+ models | Yes (Ollama) | Active (Alias Robotics) |
| **PentestGPT** | Limited benchmarks | Moderate | OpenAI/Anthropic | No | Moderate |
| **PentAGI** | Competitive | Moderate | OpenAI primary | No | Active |
| **hackingBuddyGPT** | Research-focused | Limited | OpenAI | No | Research cadence |

**CAI** is the right choice when you need production-grade performance, multi-agent orchestration, air-gapped deployment, or broad model flexibility. The HITL and guardrail system is the most mature of the three. The trade-off: steeper learning curve due to richer architecture.

**PentestGPT** is optimized for web application testing with a simpler mental model. Good for teams that primarily do bug bounty web testing and want to start quickly without learning CAI's 8-pillar architecture. Limited multi-agent support.

**PentAGI** takes a more general-purpose agent approach and performs well on structured pentest methodologies. Better documentation for teams new to AI-assisted pentesting. Less proven in competitive benchmarks.

For security teams doing serious offensive work — red team engagements, bug bounty at scale, CTF competition, OT security assessment — CAI is the only production-ready option. For teams exploring AI-assisted pentesting for the first time, PentestGPT offers a lower entry point.

## Responsible Use, Legal Boundaries, and Ethical Considerations

AI-powered offensive security tools amplify capability dramatically — which means the legal and ethical requirements that apply to traditional pentesting apply with greater force to CAI-based automation. The framework will do what you tell it to, faster and more thoroughly than most human teams. This is the point. It also means the consequences of misuse are proportionally larger.

The fundamental legal requirement is unchanged: you must have written authorization before scanning or testing any system you do not own. CAI's speed and automation mean an accidental misconfiguration of the `allowed_targets` scope can cause more unintended scanning in 60 seconds than a careless human could cause in an hour. Configure the `ScopeGuardrail` before running any agent in a non-local environment, and treat the scope configuration as a critical security control, not an optional feature.

Responsible disclosure applies to AI-discovered vulnerabilities. If you run CAI in bug bounty mode and it finds a critical vulnerability, the same responsible disclosure obligations that apply to human-discovered bugs apply to AI-discovered ones. CAI does not change the ethics of vulnerability research — it changes the speed at which you accumulate findings that require responsible handling.

For red team engagements, establish HITL checkpoints at every phase boundary. The HITL system exists precisely for this: a human should confirm that the engagement is proceeding within scope and intent before moving from recon to exploitation, and again before post-exploitation activities. CAI's configurability makes this easy to enforce; skipping it to save time is a professional risk management failure.

Air-gapped deployments via Ollama address a real enterprise concern: many security teams cannot send target data and scan results to external model providers due to data handling policies. CAI's multi-model support makes local deployment practical — modern 70B models running on on-premises hardware deliver sufficient reasoning quality for most pentest automation tasks.

## Frequently Asked Questions

**Is CAI legal to use for security testing?**
CAI is legal to use when you have explicit written authorization to test the target system. Like all offensive security tools, using CAI against systems you do not have permission to test is illegal under the Computer Fraud and Abuse Act (US), Computer Misuse Act (UK), and equivalent laws in most jurisdictions. The framework includes scope guardrails specifically to help prevent accidental out-of-scope testing.

**What hardware do I need to run CAI locally without a cloud API?**
For local deployment via Ollama, you need a machine with at least 16GB RAM for smaller models (7B-13B parameter range) or 40GB+ VRAM for larger models (70B) that deliver production-quality reasoning. An NVIDIA GPU with CUDA support significantly improves inference speed. For cloud-connected deployments, standard developer hardware is sufficient — CAI itself is lightweight.

**How does CAI handle credential management?**
CAI does not store credentials in plaintext logs or agent context by default. The framework's output filtering guardrail can be configured to redact credential patterns before they appear in traces or reports. For production use, integrate with your secrets management system (HashiCorp Vault, AWS Secrets Manager) and inject credentials via environment variables rather than passing them in agent instructions.

**Can CAI be used for bug bounty automation?**
Yes — this is one of CAI's primary production use cases. The multi-agent handoff system is well-suited to the recon → vulnerability identification → proof-of-concept → reporting pipeline that bug bounty work requires. Configure strict scope guardrails matching the program's in-scope definition, enable HITL before any exploitation step, and use the built-in reporting tools to generate disclosure-ready vulnerability reports.

**What models work best for different CAI agent roles?**
The community consensus in 2026: use Claude Opus 4.7 or GPT-4o for orchestrator/manager agents where complex reasoning and multi-step planning are needed. Use Claude Sonnet 4.6 for specialist agents (recon, exploitation, post-exploit) where speed and tool use efficiency matter more than deep reasoning. For air-gapped deployments, Qwen2.5-72B via Ollama performs comparably to GPT-4o for most security automation tasks.
