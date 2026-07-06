---
cover:
  alt: 18 Best DevOps MCP Servers for 2026
  image: /images/devops-mcp-servers-guide-2026.png
  relative: false
date: 2026-04-27 07:04:35+00:00
description: The 18 best DevOps MCP servers for 2026 — covering Kubernetes, CI/CD,
  monitoring, IaC, cloud, and security with setup tips and stack recommendations.
draft: false
schema: schema-devops-mcp-servers-guide-2026
tags:
- DevOps
- MCP
- Kubernetes
- CI/CD
- Monitoring
- AI Tools
title: '18 Best DevOps MCP Servers for 2026: K8s, CI/CD, and Monitoring'
---

DevOps MCP servers are Model Context Protocol integrations that let AI agents — Claude, Cursor, Copilot, and others — directly control your CI/CD pipelines, Kubernetes clusters, monitoring dashboards, and infrastructure through natural language. Instead of switching between a dozen tools, you describe what you want, and an AI agent executes it using live context from your actual infrastructure.

This guide covers the 18 best DevOps MCP servers for 2026, organized by category: CI/CD, Kubernetes, monitoring, IaC, cloud, and incident management. Each entry includes what it does, when to use it, and which team types benefit most.

---

## What Are DevOps MCP Servers (and Why They Matter in 2026)

DevOps MCP servers are protocol-compliant bridges between AI coding assistants and the DevOps tools teams use every day — GitHub, Kubernetes, Grafana, Terraform, and more. The Model Context Protocol (MCP), originally developed by Anthropic and donated to the Linux Foundation's Agentic AI Foundation in December 2025, defines a standard interface for AI agents to call external tools without custom API glue code. By March 2026, MCP SDK downloads reached 97 million per month — up from roughly 100,000 in the first month, a 970x increase in 18 months. Over 10,000 public MCP servers are indexed across registries, and 80% of Fortune 500 companies are deploying AI agents in production workflows, the majority via MCP. For DevOps teams, this matters for one practical reason: 42 of the 50 most-searched MCP servers are used primarily by engineers — backend, DevOps, and AI development. The adoption curve has crossed from experiment to standard. Teams that integrate MCP-connected AI agents into their pipelines report measurable reductions in toil — from automated incident diagnosis to natural language Kubernetes management that replaces multi-command kubectl sessions.

---

## How We Evaluated These 18 DevOps MCP Servers

DevOps MCP server quality varies dramatically between community and vendor-maintained projects. We evaluated each server across six criteria: tool coverage (breadth of operations exposed), maintenance status (last commit, open issues, versioning), authentication model (API key vs. OAuth vs. service account), remote deployment support (stdio vs. HTTP/SSE), documentation quality, and real-world production reports from teams using them in 2026. Official vendor-maintained servers (GitHub, AWS, Azure, HashiCorp, Grafana Labs, Datadog) score highest on reliability and support SLAs. Community servers (Jenkins, Helm, ArgoCD) are mature in some cases but require more vetting. We include both because the "official" option doesn't always exist for every tool, and the community MCP ecosystem has produced some genuinely excellent implementations — particularly in the Kubernetes space, where containers/kubernetes-mcp-server has become the de facto standard. Servers are organized by DevOps category rather than ranked overall, because the best server for a GitHub Actions shop is irrelevant to a team running all-Jenkins pipelines.

---

## CI/CD MCP Servers

CI/CD MCP servers are Model Context Protocol integrations that allow AI agents to read pipeline state, trigger builds, inspect failed jobs, open pull requests, and manage workflows directly through natural language commands. They eliminate the context-switching cost of navigating pipeline UIs when debugging failures, reviewing test results, or coordinating deployments. Before MCP, a developer diagnosing a failing pipeline had to: open the CI/CD UI, navigate to the failing run, find the relevant log output, cross-reference with recent commits, then open a new terminal to run fix attempts. With a CI/CD MCP server, that entire investigation happens inside a single AI conversation turn. The four servers below cover the dominant CI/CD platforms in enterprise DevOps as of 2026 — GitHub Actions, GitLab CI, Jenkins, and Azure Pipelines — accounting for roughly 85% of enterprise CI/CD workloads. Each exposes a different API surface area, and teams typically integrate one primary CI/CD MCP server alongside source control operations, letting an AI agent go from "this PR is failing" to "here's the root cause, here's the fix, I've re-triggered the build" without leaving the assistant context.

### 1. GitHub MCP Server — Best for GitHub-Centric Teams

The official GitHub MCP server, maintained by GitHub, is the most widely deployed DevOps MCP server in production as of 2026. It exposes file operations, repository management, issue and PR lifecycle, Actions workflow triggers, code search, and GitHub Security alerts through a single MCP interface. Teams using GitHub Actions as their primary CI/CD platform can use this server to let AI agents create PRs from code changes, inspect failing workflow runs, read test output, and merge approved changes — without leaving the AI assistant context. Authentication uses a GitHub Personal Access Token or GitHub App credentials. Remote deployment is supported via HTTP transport. For teams already using Claude or Cursor as a coding assistant, the GitHub MCP server is almost always the first DevOps integration to enable — the coverage-to-effort ratio is highest here.

**Key tools:** `create_pull_request`, `get_workflow_run`, `list_check_runs`, `create_issue`, `search_code`
**Setup:** `GITHUB_PERSONAL_ACCESS_TOKEN` env var, stdio or HTTP transport

### 2. GitLab MCP Server — Best for GitLab CI/CD Workflows

The GitLab MCP server, available in both community and official vendor builds, provides access to GitLab repositories, merge requests, CI/CD pipelines, issues, and the GitLab Container Registry. For teams running GitLab CI, this server lets AI agents inspect pipeline job logs, trigger manual pipeline stages, review merge request diffs, and manage GitLab Issues from within an AI conversation. The server supports both GitLab.com and self-hosted GitLab instances via configurable base URL, making it suitable for air-gapped enterprise environments where GitHub is not an option. Authentication supports personal access tokens and project-scoped tokens.

**Key tools:** `list_pipelines`, `get_job_log`, `create_merge_request`, `get_project`, `list_issues`
**Setup:** `GITLAB_PERSONAL_ACCESS_TOKEN` + optional `GITLAB_BASE_URL` for self-hosted

### 3. Jenkins MCP Server — Best for Jenkins-Heavy Pipelines

Jenkins remains the dominant CI/CD platform in enterprises with legacy infrastructure, and several MCP implementations have emerged to bridge it with AI agents. The most production-ready is kud/mcp-jenkins, which exposes 25–37 tools covering job management, build triggering, log retrieval, node status, and view configuration. For SREs who spend time diagnosing failed Jenkins pipelines, this server enables natural language queries like "show me the last 5 failed builds for the payment-service job and summarize the common failure pattern" — something that previously required clicking through Jenkins UI across multiple tabs. The server connects via the Jenkins REST API and supports authentication through API tokens.

**Key tools:** `get_build_log`, `trigger_build`, `list_jobs`, `get_node_status`, `abort_build`
**Setup:** `JENKINS_URL` + `JENKINS_USERNAME` + `JENKINS_API_TOKEN`

### 4. Azure DevOps MCP Server — Best for Microsoft/Azure Shops

The Azure DevOps MCP server provides AI agents with access to Azure Pipelines, Azure Repos, Work Items, Test Plans, and Artifacts. For organizations standardized on the Microsoft stack — Visual Studio, Azure, and Azure DevOps — this server closes the loop between AI-assisted development in VS Code (via GitHub Copilot or Claude Code) and the pipeline management layer. It supports OAuth authentication via Azure Entra ID (formerly Azure AD), making it suitable for enterprise identity management requirements. Teams can use it to query work item status, trigger pipeline runs, and link PR completion to sprint board updates.

**Key tools:** `get_pipeline_run`, `create_work_item`, `list_pull_requests`, `run_pipeline`, `get_test_results`
**Setup:** Azure DevOps Personal Access Token or Azure Entra OAuth

---

## Kubernetes & Container Orchestration MCP Servers

Kubernetes MCP servers are the fastest-growing category in the DevOps MCP ecosystem, driven by the inherent complexity of managing containerized workloads at scale. Kubernetes exposes hundreds of resource types, thousands of configuration options, and a CLI (kubectl) whose full command surface takes months to master. AI agents connected to a Kubernetes MCP server can diagnose pod failures, inspect resource states, apply manifests, roll back deployments, exec into containers, and explain cluster state — all without the engineer needing to compose kubectl commands manually. A 2025 survey of SRE teams found that Kubernetes troubleshooting consumes an average of 35% of on-call time; AI-assisted diagnosis via MCP servers is the primary lever teams are pulling to reduce that figure in 2026. This section covers the four most important K8s-related MCP servers: the official containers/kubernetes-mcp-server for direct cluster operations, ArgoCD for GitOps workflow management, Helm for Kubernetes package management, and Docker Hub MCP for container image discovery and security scanning. Together they cover the full Kubernetes application lifecycle from image to deployment to runtime management.

### 5. containers/kubernetes-mcp-server — Best Official K8s MCP

The containers/kubernetes-mcp-server, maintained under the containers GitHub organization, has become the de facto standard for Kubernetes MCP integration in 2026. It exposes Pod, Deployment, Service, ConfigMap, Namespace, and Event operations directly against a Kubernetes cluster via the Kubernetes API. Authentication uses the kubeconfig file, supporting both local development (via ~/.kube/config) and in-cluster service account tokens for production use. For SRE teams, the most common use case is incident diagnosis: "What pods are in CrashLoopBackOff in the production namespace, and what do their logs show?" This previously required 3-4 kubectl commands; with the MCP server, an AI agent can answer it in one conversational turn.

**Key tools:** `list_pods`, `get_pod_logs`, `describe_deployment`, `apply_manifest`, `delete_resource`
**Setup:** kubeconfig file or `KUBECONFIG` env var; supports multi-cluster contexts

### 6. ArgoCD MCP Server — Best for GitOps Workflows

The ArgoCD MCP server bridges AI agents with GitOps deployment pipelines. ArgoCD, the most widely deployed GitOps operator on Kubernetes, manages application definitions in Git and syncs them to clusters. The MCP server exposes application sync status, health state, rollback operations, and diff inspection. For teams running GitOps workflows, this server enables natural language deployment management: "Show me which applications are out of sync in production, explain the diff, and trigger a sync for the payment-service." It supports the ArgoCD gRPC API with token authentication, and works with both ArgoCD OSS and Argo CD Enterprise.

**Key tools:** `list_applications`, `get_app_sync_status`, `sync_application`, `rollback_application`, `get_app_diff`
**Setup:** `ARGOCD_SERVER` + `ARGOCD_AUTH_TOKEN`

### 7. Helm MCP Server — Best for Kubernetes Package Management

The Helm MCP server exposes Helm release management to AI agents — listing installed releases, inspecting chart values, running upgrades, and rolling back failed releases. For platform engineering teams managing dozens of Helm-deployed services, this server reduces the cognitive overhead of tracking what version of what chart is deployed where. A common use case: "Compare the current values for nginx-ingress in staging vs. production and flag any configuration differences." Authentication is inherited from the cluster kubeconfig; the server runs Helm operations directly against the current cluster context.

**Key tools:** `list_releases`, `get_release_values`, `upgrade_release`, `rollback_release`, `install_chart`
**Setup:** kubeconfig, Helm binary in PATH

### 8. Docker Hub MCP Server — Best for Container Discovery

The Docker Hub MCP server, part of Docker's official MCP catalog, provides AI agents with access to Docker Hub image search, tag listing, vulnerability scan results, and repository management. For platform engineers evaluating base images or debugging which image tag is running in a deployment, this server eliminates the need to navigate Docker Hub manually. Docker Desktop provides access to 200+ MCP servers via the Docker MCP Toolkit, making Docker Hub MCP straightforward to enable for teams already using Docker Desktop. It also surfaces Docker Scout security scan results, useful for shift-left security workflows.

**Key tools:** `search_images`, `list_tags`, `get_image_details`, `get_vulnerability_report`
**Setup:** Docker Hub credentials via Docker Desktop or `DOCKER_HUB_USERNAME` + `DOCKER_HUB_TOKEN`

---

## Monitoring & Observability MCP Servers

Monitoring MCP servers are where AI-assisted DevOps delivers the most immediate and measurable ROI. Debugging a production incident typically requires querying metrics to find anomalies, reading logs to identify error patterns, correlating alerts across services, and forming a root cause hypothesis — a process that spans three to five separate tools and takes a skilled SRE 20–45 minutes on average. Connecting an AI agent to Grafana, Prometheus, and Datadog via MCP servers collapses that process: the agent queries all three in a single investigation thread, surfaces the most likely root cause, and presents a structured summary. The key insight is that monitoring tools generate far more signal than engineers can process in real time during an incident; AI agents with MCP access can parallelize that signal processing at machine speed. In 2026, teams using AI agents with observability MCP integrations report 30–50% reductions in mean time to diagnosis for P1 incidents, according to early adopter case studies from the Grafana community. This section covers the three dominant monitoring platforms: Grafana Labs' mcp-grafana for all-in-one observability, the Prometheus MCP server for metrics and PromQL workflows, and the Datadog MCP server for enterprise-grade monitoring with APM and log management.

### 9. Grafana MCP Server — Best All-in-One Observability MCP

The mcp-grafana server from Grafana Labs is an open-source Go binary that exposes 40+ tools covering Grafana dashboards, data source queries, alert rules, Loki log queries, and Grafana Incident management. As the most feature-complete observability MCP server available in 2026, it enables AI agents to perform complete incident diagnosis workflows: query metrics for anomalies, pull correlated logs from Loki, inspect alert history, and post findings to a Grafana Incident channel. The server is actively maintained by Grafana Labs, ensuring it stays current with Grafana Cloud and self-hosted Grafana releases. Authentication uses a Grafana service account token with appropriate read permissions.

**Key tools:** `query_datasource`, `list_dashboards`, `get_dashboard`, `list_alert_rules`, `query_loki`
**Setup:** `GRAFANA_URL` + `GRAFANA_SERVICE_ACCOUNT_TOKEN`

### 10. Prometheus MCP Server — Best for Metrics & PromQL

The Prometheus MCP server exposes the Prometheus HTTP API to AI agents, allowing natural language PromQL queries, metric discovery, alert rule inspection, and recording rule management. For SRE teams who know what they want to measure but struggle to write complex PromQL expressions, this server is a force multiplier: "Show me the 95th percentile request latency for the checkout service over the last 2 hours, broken down by status code." The server translates this into valid PromQL and returns structured results. It connects to any Prometheus-compatible endpoint including Thanos, VictoriaMetrics, and Grafana Mimir — making it broadly applicable beyond standalone Prometheus deployments.

**Key tools:** `query_range`, `instant_query`, `list_metrics`, `get_alert_rules`, `get_recording_rules`
**Setup:** `PROMETHEUS_URL`, optional basic auth or bearer token

### 11. Datadog MCP Server — Best for Enterprise Monitoring

The Datadog MCP server, available through Datadog's official integration channel, provides access to Datadog metrics, logs, APM traces, dashboards, monitors, and incidents. For enterprises standardized on Datadog — common in financial services, retail, and SaaS — this server enables AI agents to query live telemetry without requiring engineers to navigate Datadog's UI. The server supports the Datadog API v2 endpoints and handles authentication via Datadog API key and application key. Enterprise teams use it for automated incident triage: the AI agent queries monitors in alarm state, pulls correlated APM traces, and surfaces the service most likely responsible — reducing mean time to diagnosis.

**Key tools:** `query_metrics`, `search_logs`, `get_monitors`, `list_incidents`, `get_trace`
**Setup:** `DD_API_KEY` + `DD_APP_KEY` + `DD_SITE` (e.g., `datadoghq.com`)

---

## Infrastructure as Code MCP Servers

Infrastructure as Code MCP servers bring AI-assisted management to Terraform and Pulumi workflows — the two dominant IaC tools in enterprise DevOps as of 2026, together managing an estimated 70%+ of cloud infrastructure provisioned by engineering teams. IaC is a uniquely strong fit for AI assistance for three structural reasons: configurations are code that an AI can read and modify, plan outputs are structured diffs that map precisely to infrastructure changes, and state files encode the ground truth of what's actually deployed versus what the code declares. An AI agent with access to a Terraform MCP server can explain in plain language what a `terraform plan` will change before you apply it, identify why a resource is showing drift between state and reality, suggest fixes for plan failures, and generate new resource configurations from natural language descriptions. This closes the most common IaC bottleneck: the gap between knowing what infrastructure you want and knowing how to write correct Terraform or Pulumi code to declare it. Both servers covered below — HashiCorp's official Terraform MCP server and the Pulumi MCP server — operate against their respective cloud control planes rather than local CLI state, which means they work in remote execution environments and CI/CD pipelines, not just on a developer's laptop.

### 12. Terraform MCP Server (HashiCorp) — Best for IaC Automation

HashiCorp's official Terraform MCP server provides AI agents with access to the Terraform Cloud and HCP Terraform APIs — exposing workspace management, run lifecycle (plan, apply, destroy), state inspection, and variable management. For teams using Terraform Cloud as their remote execution environment, this server enables workflows like: "Show me the last 5 runs for the production-networking workspace, explain what changed in each, and apply the pending plan if the changes look safe." It uses the Terraform Cloud API token for authentication and supports both Terraform Cloud SaaS and self-hosted TFE (Terraform Enterprise). For teams running open-source Terraform locally, community MCP servers expose the local Terraform CLI instead.

**Key tools:** `list_workspaces`, `get_run`, `apply_run`, `get_state`, `list_variables`
**Setup:** `TFC_TOKEN` for Terraform Cloud; local CLI variant uses Terraform binary

### 13. Pulumi MCP Server — Best for Code-First IaC Teams

The Pulumi MCP server connects AI agents to Pulumi Cloud for stack management, update history, resource inspection, and ESC (Environments, Secrets, and Configuration) access. Pulumi's code-first approach to IaC — using TypeScript, Python, Go, or C# instead of HCL — makes it especially AI-friendly: the agent can read, explain, and modify actual programming language code rather than a domain-specific configuration language. For platform engineering teams who have standardized on Pulumi, this server enables AI agents to inspect stack outputs, trace resource drift, and generate new Pulumi components. Authentication uses the Pulumi access token.

**Key tools:** `list_stacks`, `get_stack_outputs`, `get_update_history`, `preview_stack`, `get_resource`
**Setup:** `PULUMI_ACCESS_TOKEN`

---

## Cloud Provider MCP Servers

Cloud provider MCP servers give AI agents direct access to AWS and Azure control planes — enabling resource inventory queries, cost analysis, configuration audits, security posture reviews, and operational management tasks without leaving the AI assistant context. Cloud providers expose thousands of distinct API operations across dozens of services; MCP servers make that surface area navigable through natural language rather than requiring engineers to memorize SDK method names and parameter schemas. The AWS MCP server suite, officially released by Amazon in 2025 and actively extended through 2026, covers EC2, S3, RDS, Lambda, CloudFormation, CloudWatch, EKS, and more. For FinOps use cases specifically, cloud provider MCP servers deliver standout value: an AI agent can query EC2 fleet utilization across all regions, identify instances with under 5% average CPU over 30 days, cross-reference with Reserved Instance commitments, and calculate rightsizing savings — work that previously required hours of Cost Explorer navigation and manual spreadsheet analysis. The two servers covered below address the two dominant enterprise cloud platforms: Amazon Web Services (used by approximately 31% of cloud market share) and Microsoft Azure (used by approximately 25%). Google Cloud Platform has emerging MCP support but is not yet at the same maturity level for production DevOps workflows as of April 2026.

### 14. AWS MCP Server (Official) — Best for AWS-Heavy Workloads

Amazon's official AWS MCP server suite, released in 2025 and actively extended in 2026, provides AI agents with access to the full breadth of AWS services via the AWS SDK. The core server exposes EC2, S3, RDS, Lambda, CloudFormation, and CloudWatch operations, while specialized companion servers cover EKS, Bedrock, CodeCatalyst, and CDK. Authentication uses AWS credentials via standard methods: environment variables, `~/.aws/credentials`, or IAM role assumption. The FinOps use case is a standout: teams use the AWS MCP server to ask "which EC2 instances in us-east-1 have less than 5% average CPU over the last 30 days?" and get actionable rightsizing recommendations — work that previously required Cost Explorer and manual analysis.

**Key tools:** `describe_instances`, `list_s3_buckets`, `get_cloudwatch_metrics`, `describe_stacks`, `list_lambda_functions`
**Setup:** Standard AWS credentials (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, or IAM role)

### 15. Azure MCP Server — Best for Azure Cloud Management

The Azure MCP server, available in the Docker MCP Catalog and via official Microsoft channels, provides AI agents with Azure Resource Manager access — covering resource groups, virtual machines, storage accounts, Azure Kubernetes Service, and Azure Monitor. For Microsoft-stack organizations managing Azure infrastructure alongside Azure DevOps pipelines, pairing the Azure MCP server with the Azure DevOps MCP server creates an end-to-end AI-native management layer: from infrastructure provisioning to deployment pipeline execution in a single AI conversation. Authentication uses Azure CLI credentials or service principal credentials via environment variables.

**Key tools:** `list_resource_groups`, `get_vm_status`, `list_storage_accounts`, `get_aks_clusters`, `query_monitor_logs`
**Setup:** Azure CLI (`az login`) or `AZURE_CLIENT_ID` + `AZURE_CLIENT_SECRET` + `AZURE_TENANT_ID`

---

## Incident Management & Security MCP Servers

Incident management and security MCP servers address the two highest-stakes workflows in DevOps: responding to production outages where every minute of downtime has measurable business cost, and identifying security vulnerabilities before they reach production where the cost of remediation is 10–100x lower than post-breach response. PagerDuty, with over 25,000 enterprise customers in 2026, is the dominant on-call incident management platform; its MCP server connects AI agents to incident lifecycle management — alert acknowledgment, escalation, on-call queries, and postmortem creation. Snyk and Qualys represent two tiers of the security scanning market: Snyk for developer-first shift-left security in fast-moving teams, and Qualys for enterprise compliance requirements in regulated industries. These servers work best as part of a broader MCP stack rather than in isolation — incident diagnosis is most effective when the AI agent can simultaneously query PagerDuty for incident context, Grafana for correlated metrics, and Kubernetes for cluster state. Similarly, security MCP servers deliver more value when paired with GitHub or GitLab MCP servers, allowing the AI agent to surface a vulnerability finding and immediately open a remediation PR in the same conversation turn. The three servers below cover the core incident and security needs for the majority of DevOps teams.

### 16. PagerDuty MCP Server — Best for On-Call Incident Response

The PagerDuty MCP server exposes PagerDuty's incident management API to AI agents — covering incident creation, alert acknowledgment, escalation policy inspection, on-call schedule queries, and postmortem creation. For SRE teams using PagerDuty as their incident management platform, this server enables AI agents to participate in incident response: pulling the current incident list, identifying which team is on call, summarizing recent alert history for a service, and drafting postmortem timelines from incident metadata. Authentication uses the PagerDuty REST API key. When combined with Grafana or Datadog MCP servers, AI agents can perform end-to-end incident triage — from alert fire to root cause hypothesis — without engineer intervention for initial diagnosis.

**Key tools:** `list_incidents`, `get_incident`, `acknowledge_incident`, `list_oncalls`, `create_note`
**Setup:** `PAGERDUTY_API_KEY`

### 17. Snyk MCP Server — Best for Shift-Left Security Scanning

The Snyk MCP server integrates Snyk's vulnerability scanning into AI-assisted development workflows, exposing project vulnerability lists, license issue reports, dependency fix recommendations, and Snyk Code (SAST) findings. For DevSecOps teams implementing shift-left security, this server lets AI agents surface security issues at PR review time: "Does this change introduce any new critical vulnerabilities? What's the fix?" Snyk's AI-driven fix suggestions, exposed via the MCP server, can be applied directly by coding AI agents — closing the loop from vulnerability detection to remediation without leaving the development context. Authentication uses a Snyk API token associated with a Snyk organization.

**Key tools:** `list_projects`, `get_project_issues`, `get_fix_advice`, `test_code`, `get_dependency_graph`
**Setup:** `SNYK_TOKEN` + optional `SNYK_ORG_ID`

### 18. Qualys TotalAI MCP Server — Best for Enterprise Security Compliance

The Qualys TotalAI MCP server, released in early 2026, connects AI agents to the Qualys Cloud Security Platform for vulnerability management, policy compliance, container security, and web application scanning. For enterprise security teams operating in regulated industries (finance, healthcare, government), Qualys provides the compliance depth that lightweight scanners like Snyk don't cover — CIS Benchmarks, PCI DSS, HIPAA, and SOX policy assessments are all accessible via the MCP interface. AI agents can use this server to generate compliance status reports, identify misconfigurations in cloud workloads, and track remediation progress against SLAs. Authentication uses Qualys API credentials with appropriate platform URL for the appropriate region.

**Key tools:** `get_vulnerability_list`, `run_compliance_scan`, `get_policy_compliance`, `list_assets`, `get_container_findings`
**Setup:** `QUALYS_USERNAME` + `QUALYS_PASSWORD` + `QUALYS_API_URL`

---

## How to Choose the Right DevOps MCP Server Stack

Choosing the right DevOps MCP servers starts with mapping your team's biggest pain points to the tools they already use, not adopting the most impressive-sounding integrations. The most effective MCP stacks in 2026 are narrow: 3–5 servers that cover the tools a team touches every day, rather than 15 servers that cover every tool in the ecosystem. Start with your source control and CI/CD system — GitHub or GitLab MCP is almost always the highest-value first integration, since those platforms sit at the center of every development workflow. Add your primary monitoring platform next (Grafana, Prometheus, or Datadog), since incident diagnosis is where AI-assisted DevOps saves the most time per event. Infrastructure management comes third — Terraform or Pulumi MCP if you're doing active IaC work, AWS or Azure MCP if cloud resource queries are a daily task.

Four questions to guide selection:

1. **What tool do your engineers use most?** Start there. An MCP server for a tool you use daily delivers more value than one for a tool you use monthly.
2. **Is it vendor-maintained or community?** Vendor-maintained servers (GitHub, Grafana Labs, HashiCorp, AWS) have better SLA guarantees and stay current with API changes. Community servers can be excellent (kubernetes-mcp-server, Jenkins) but require vetting.
3. **Does it support remote deployment?** Teams using shared AI platforms (Claude.ai, Cursor for teams) need HTTP/SSE transport, not just stdio. Check transport support before committing.
4. **What's the authentication model?** API token, OAuth, or service account — ensure it fits your organization's identity management requirements. Enterprise environments with Entra ID or Okta will prefer OAuth-compatible servers.

---

## Recommended MCP Server Stacks by Team Type

Different team compositions benefit from different combinations of DevOps MCP servers. Below are three starting-point stacks based on common team profiles.

**Startup / Small Team (1–15 engineers):**
- GitHub MCP Server (source control + CI/CD)
- containers/kubernetes-mcp-server (if running K8s)
- Grafana MCP Server (observability)
- AWS MCP Server (cloud infrastructure)

This stack covers the full deployment lifecycle with four servers. GitHub handles code through CI/CD, Kubernetes manages runtime, Grafana provides observability, and AWS covers cloud resources.

**Mid-Size SRE Team (15–100 engineers):**
- GitHub or GitLab MCP Server
- ArgoCD MCP Server (GitOps deployments)
- Grafana MCP Server + Prometheus MCP Server
- PagerDuty MCP Server (incident management)
- Terraform MCP Server (IaC)

This stack adds GitOps and incident management, reflecting the operational complexity that emerges at this scale. Prometheus alongside Grafana enables PromQL-native queries for teams who work at the metrics layer directly.

**Enterprise / Platform Engineering Team (100+ engineers):**
- Azure DevOps MCP Server or GitHub Enterprise MCP Server
- containers/kubernetes-mcp-server (multi-cluster)
- Datadog MCP Server
- PagerDuty MCP Server
- Terraform MCP Server (HCP Terraform)
- Snyk MCP Server (security)
- Azure or AWS MCP Server

Enterprise stacks add Datadog for enterprise-grade observability, Snyk for shift-left security, and replace open-source tools with enterprise-tier equivalents where vendor support is required.

---

## DevOps MCP Servers: Comparison Table

| Server | Category | Maintainer | Auth Method | Remote Deployment | Best For |
|---|---|---|---|---|---|
| GitHub MCP Server | CI/CD | GitHub (Official) | PAT / GitHub App | Yes (HTTP) | GitHub-centric teams |
| GitLab MCP Server | CI/CD | Community/Vendor | PAT | Yes | GitLab CI/CD workflows |
| Jenkins MCP Server | CI/CD | Community | API Token | Via stdio | Jenkins-heavy pipelines |
| Azure DevOps MCP | CI/CD | Microsoft | OAuth (Entra) | Yes | Microsoft/Azure shops |
| kubernetes-mcp-server | Kubernetes | containers org | kubeconfig | Yes | K8s cluster operations |
| ArgoCD MCP Server | Kubernetes | Community | gRPC token | Yes | GitOps deployments |
| Helm MCP Server | Kubernetes | Community | kubeconfig | Via stdio | K8s package management |
| Docker Hub MCP | Containers | Docker (Official) | Docker Hub creds | Yes (Docker Desktop) | Container image discovery |
| Grafana MCP Server | Monitoring | Grafana Labs | Service Account | Yes | All-in-one observability |
| Prometheus MCP Server | Monitoring | Community | Bearer token | Yes | Metrics & PromQL |
| Datadog MCP Server | Monitoring | Datadog (Official) | API + App Key | Yes | Enterprise monitoring |
| Terraform MCP Server | IaC | HashiCorp (Official) | TFC Token | Yes | Terraform Cloud IaC |
| Pulumi MCP Server | IaC | Pulumi (Official) | Access Token | Yes | Code-first IaC teams |
| AWS MCP Server | Cloud | Amazon (Official) | IAM / AWS creds | Yes | AWS-heavy workloads |
| Azure MCP Server | Cloud | Microsoft | Azure CLI / SP | Yes | Azure cloud management |
| PagerDuty MCP Server | Incident Mgmt | Community | REST API Key | Yes | On-call incident response |
| Snyk MCP Server | Security | Snyk (Official) | API Token | Yes | Shift-left security |
| Qualys TotalAI MCP | Security | Qualys (Official) | Username/Password | Yes | Enterprise compliance |

---

## Frequently Asked Questions

DevOps MCP servers are a rapidly evolving category, and teams evaluating them consistently run into the same questions: what are they, are they safe for production, which ones have the best tool coverage, and how do you get started without spending two days on configuration. The answers below address the five questions we see most often from platform engineers and SRE teams who are evaluating MCP integrations for the first time in 2026. The MCP ecosystem has matured significantly since Anthropic's initial release — the Linux Foundation's Agentic AI Foundation now stewards the protocol, and vendor-maintained servers from GitHub, AWS, Grafana Labs, Datadog, HashiCorp, and Snyk have production track records. These answers reflect the current state as of April 2026 and will remain accurate through the remainder of the year absent significant protocol changes. For teams new to the MCP ecosystem, starting with the GitHub MCP server and one observability integration (Grafana or Datadog) delivers value within hours of setup — without requiring any custom code or infrastructure changes.

### What is a DevOps MCP server?

A DevOps MCP server is a software component that implements the Model Context Protocol (MCP) to expose DevOps tool functionality — Kubernetes operations, CI/CD pipeline management, monitoring queries, infrastructure commands — to AI agents. When connected to an AI assistant like Claude or Cursor, MCP servers give the AI direct access to your tools so it can take actions, not just give advice. Instead of the AI suggesting a kubectl command for you to run, an AI agent with a Kubernetes MCP server can run that command against your cluster and return the results within the same conversation turn.

### Are DevOps MCP servers production-safe?

This depends heavily on the specific server, its permission model, and how you configure it. Official vendor-maintained servers (GitHub, AWS, Datadog, HashiCorp) are designed for production use with appropriate access controls. Community servers vary in quality and should be audited before production deployment. Best practice is to use read-only credentials where possible, grant the minimum permissions needed, and test in staging before production. AI agents connected to write-capable MCP servers (applying Terraform plans, deleting Kubernetes resources) should have human-in-the-loop approval for destructive operations.

### Which DevOps MCP server has the most tool coverage?

Grafana Labs' mcp-grafana leads with 40+ exposed tools, covering dashboards, data sources, alerts, Loki log queries, and Grafana Incident management. The Jenkins MCP server (kud/mcp-jenkins) exposes 25–37 tools. The GitHub MCP server exposes 30+ tools across repositories, issues, PRs, Actions, and Security. For raw breadth across a DevOps workflow, pairing GitHub + Grafana + kubernetes-mcp-server covers the largest surface area for the smallest number of integrations.

### Do DevOps MCP servers work with all AI assistants?

Any AI assistant that implements the MCP client protocol can use MCP servers. As of 2026, this includes Claude (via Claude Desktop, Claude.ai, and Claude Code), Cursor, Windsurf, VS Code Copilot (with the MCP extension), Continue.dev, and many others. The MCP standard is model-agnostic — the same Kubernetes MCP server works identically regardless of whether the AI agent is Claude Sonnet, GPT-4o, or Gemini Pro.

### How do I get started with DevOps MCP servers if I'm new to MCP?

The fastest path to a working DevOps MCP setup: (1) Install Claude Desktop or Claude Code CLI. (2) Add the GitHub MCP server configuration to your MCP client config file — this requires only a GitHub Personal Access Token and one JSON config block. (3) Ask Claude to list your open PRs or describe a failing GitHub Actions workflow. Once you see it working, add a second server — the containers/kubernetes-mcp-server if you run Kubernetes, or the Grafana MCP server if observability is your priority. Start narrow, validate each server is working correctly, then expand. The Docker MCP Toolkit in Docker Desktop is also an accessible entry point, providing a GUI for enabling 200+ servers including many in this guide.