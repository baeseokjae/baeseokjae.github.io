---
title: "BugbountyRules Review: Agent Behavior Rules Security for Methodical AI Hunters"
date: 2026-10-01T06:12:53+00:00
tags:
  - agent behavior rules security
  - bugbountyrules skill
  - AI agent bug bounty skill
  - claude code security skill
  - 42 rules agent skill
  - agent skill behavioral discipline
  - AI agent false positive gate
  - hunter skeptic referee verification
  - coverage ledger agent
  - agent never conclude secure rule
  - progressive disclosure agent skill
  - autonomous pentest agent guardrails
  - agent skill supply chain security 2026
  - OWASP agentic skills top 10
  - scope enforcement AI agent
  - best AI pentest skill 2026
description: "BugbountyRules keeps 42 always-on agent behavior rules in context so a hunting agent stops shipping false positives, inflating severity, and quitting early."
draft: false
cover:
  image: "/images/bugbountyrules-agent-discipline.png"
  alt: "BugbountyRules Review: Agent Behavior Rules Security for Methodical AI Hunters"
  relative: false
schema: "schema-bugbountyrules-agent-discipline"
---

BugbountyRules is a Claude Code skill that keeps 42 always-active behavioral rules in context — scope, coverage, evidence, persistence — instead of payloads. It exists because an agent already knows what SQL injection is; it fails by shipping false positives, inflating severity, and quitting early. The rules govern method, not knowledge.

That inversion is the whole point of the project. Nearly every "AI security skill" on the market is a knowledge pack: a longer list of things to look for. BugbountyRules ([github.com/sanjarbiy/bugbountyrules](https://github.com/sanjarbiy/bugbountyrules)) takes the opposite position, and its README states the thesis bluntly — the agent's problem is not that it does not know what an IDOR is, it is that it will not reload prior state after a context compaction, will not distinguish a confirmed finding from a plausible one, and will declare a surface clean the moment it runs out of ideas. Those are behaviours. Behaviours are what the 42 rules target.

Below: what the skill actually contains, the three failures its own measurements are built around, how the verification gate and coverage ledger work, how it compares to the closest alternatives, and why installing any third-party behavioral skill is now a supply-chain decision.

## What Is BugbountyRules, and How Is It Not a Payload Pack?

It is a single always-loaded behavioural core plus a deeply bundled, on-demand knowledge base.

The always-on layer is `SKILL.md` — 1,489 lines, 42 rules, verified by parsing the repository file on 2026-10-01. Those rules define how an agent hunts: what it must do before a request, how it proves a finding, when it is allowed to stop, and what language it may and may not use in a report. None of them ship an exploit.

The on-demand layer is the arsenal: a bundled `portswigger-kb` with 32 vulnerability-class folders and 93 sub-folders (roughly 271 files in the tree), a `reference/` directory of 8 files, plus `writeup-library.md`, `waf-bypass-arsenal.md`, `vuln-taxonomy.md`, `vulnerability-rating-taxonomy.json`, and a `scripts/` directory. Only the behavioural core sits in context by default; the technique library loads when a specific class becomes relevant.

The repository is small and young. Per the GitHub API on 2026-10-01: MIT license, 35 stars, 6 forks, 0 open issues, created 2026-08-17, last push 2026-08-18, roughly 855 KB. That is a deliberate design constraint, not a shortcoming to paper over — the architecture only works because the always-loaded part is behaviour and the heavy part is deferred.

## Why Is Behaviour, Not Knowledge, the Bottleneck?

Because the knowledge problem is largely solved and the discipline problem visibly is not.

Autonomous agents now produce results that would have been implausible three years ago. XBOW submitted 1,060+ autonomous vulnerability reports on HackerOne and became the first AI system at #1 on the US leaderboard; in one published comparison it matched a 20-year veteran pentester's 85% solve rate on a 104-challenge suite in 28 minutes against the human's roughly 40 hours ([xbow.com](https://xbow.com/blog/we-ran-1060-autonomous-attacks)). Wiz's Red Agent surfaced 17,000+ unique findings across about 1,000 customer environments in its first month, with access-control failures accounting for 54% of discoveries and exposed secrets for 61% of critical/high findings ([CSA research note](https://labs.cloudsecurityalliance.org/research/csa-research-note-ai-autonomous-red-team-agent-findings-2026)). A single AI agent reached top-3 on multiple HackerOne business leaderboards on a ~$5,000/month budget, filing 150 reports in its primary window with 19 (12.7%) accepted or triaged, 64.4% of severity-rated findings critical or high, and 0% N/A on critical findings ([FireCompass, July 2026](https://firecompass.com/blog-ai-penetration-testing-hackerone-top-3-press-release)).

Demand is there too. HackerOne's 9th Hacker-Powered Security Report records valid AI vulnerability reports up 210% (prompt injection up 540%) and programs with AI in scope up 270%, against 580,000+ validated vulnerabilities, $81M paid out and about $3B in breach losses avoided ([hackerone.com/report](https://www.hackerone.com/report/hacker-powered-security)).

And yet, in the same report, 58% of surveyed security researchers say AI misses business logic or chained exploits, and only 12% believe it could replace them. That gap is not a knowledge gap — it is a judgment gap. An agent that cannot tell a real chained ATO from a suggestive response body is not missing a payload, it is missing a rule.

## What Are the Three Failures That Cost Money?

The skill names three, and each one comes with a measurement rather than an assertion.

| Failure mode | What it looks like in practice | Mechanism the skill applies |
|---|---|---|
| False positives | Plausible-but-unproven findings flood the report | Hunter → Skeptic → Referee gate |
| Severity inflation | Every finding becomes critical | Per-metric anchoring; hedging language banned |
| Quitting early | "Surface appears secure" after a shallow pass | Coverage ledger, depth ladders, stuck loop |

The false-positive number is the one worth sitting with. The repository states that a small model handed eight findings waved through 3 of the 4 textbook false positives it was given and inflated severity on 6 of 8. That is a 75% false-positive pass rate on planted, unambiguous traps — not adversarial edge cases, textbook ones. For a triager on the receiving end, an agent with that profile is not a contributor, it is a queue.

Severity inflation is the second-order version of the same problem. A report is not a claim about what could happen; it is a claim about what did happen, under stated preconditions, with a stated impact. Per-metric anchoring forces the agent to justify each scored dimension separately instead of assigning a single flattering number, and banning hedging language removes the escape hatch of writing "could potentially lead to" where a demonstration was required.

Quitting early is the cheapest failure to miss, because a clean report and an abandoned hunt look identical from the outside.

## How Do the Hunt Reflex and Operational Flow Work?

Two runtime mechanisms turn 42 static rules into a repeatable sequence.

The **Hunt Reflex** is a pre-move checklist: before the agent issues a request, it checks the rule set that applies to that move. The purpose is to make discipline reflexive rather than retrospective — a rule read after a failed attempt only produces a better excuse.

The **Operational Flow** is the longer loop: load prior state → probe tool pack → read scope → passive recon → map surface → hunt → verify → report. Two steps in that sequence are load-bearing. "Read scope" comes before any probe; "load prior state" comes first of all, because an agent recovering from a context compaction with no restored state is the duplicate-generating failure the skill measured directly.

The flow also encodes a ratio that experienced hunters already follow: roughly 60–70% of time in reconnaissance and mapping, not payload firing. An agent that rushes to exploitation is not aggressive, it is uninformed — and uninformed attackers produce the highest-severity noise.

## What Does Progressive Disclosure Actually Buy You?

It makes governance nearly free at the token level.

A 1,489-line behavioural core is always in context. A 32-class knowledge base with 93 sub-folders is not. That split means the rules that prevent errors are present on every single action, while the technique descriptions that only matter for one class of target are loaded on demand. The consequence is that an agent can be governed without carrying a library — the constraint that makes a rule-heavy skill practical at all.

The distinction matters when you compare approaches. A 93-skill library where every skill loads separately has breadth, but no single always-on artefact that guarantees the agent's *behaviour* is consistent across the whole engagement. Progressive disclosure is the design answer to "how do I enforce 42 rules without paying 42 rules of context on every turn."

## Which Rule Clusters Carry the Weight?

Five clusters do most of the work.

**Rule 0, Adaptive Thinking.** The skill is explicitly anti-robotic. Tools listed in it are examples, not mandates; every target is different; the rule ships an anti-pattern list of robotic behaviour to avoid. This is a deliberate contrast with static "look for these patterns" security checklists. A rigid checklist is the failure mode, not the fix.

**Scope discipline, Rules 1 and 9.** Rule 1 exists because one out-of-scope request can get you banned from a programme — scope enforcement is legal safety, not housekeeping. Rule 9 covers the two-way error: an agent must not write off in-scope assets merely because of where they are hosted.

**State and duplication, Rules 21, 28 and 29.** Roughly 1 in 5 actions on real engagements were exact duplicates, and around 20% of actions were wasted because prior state was not reloaded after context compaction. Those are the measurements the coverage ledger rules are built on.

**Honest reporting, Rules 24 and 25.** Rule 25 refuses to let the agent conclude "secure" while surface remains unexamined; Rule 24 explicitly permits an honest zero over a fabricated finding. Together they invert the incentive that autonomous pentest agents are usually optimised for — benchmark score rather than report quality.

**Multi-engine routing, Rules 3.12 and 3.14.** Rule 3.12 offloads bulk reading to a local LLM as a context firewall, keeping the hunting context clean. Rule 3.14 routes findings and "secure" conclusions to a frontier peer agent for a kill-gate and a resurrection-gate — an external check on both over-claiming and premature closure.

## How Does the Hunter → Skeptic → Referee Gate Stop False Positives?

By making the agent argue against itself before it is allowed to write a report.

The gate puts one persona in the position of finding, a second in the position of attacking the finding, and a third in the position of adjudicating between them. It is adversarial self-review, and it is aimed squarely at the 3-of-4 false-positive pass rate the project measured in an ungated model.

The gate is not a novelty. It maps closely onto the control categories OWASP formalised for agentic systems — reasoning-integrity and rogue-agent controls — where the risk is not a malicious tool but an agent confidently asserting an unfounded conclusion. A verification gate that requires a demonstrable reproduction, plus a severity justified per metric, plus language that cannot hedge its way around a missing proof, is the practical implementation of that control in a hunting context.

## What Is the Coverage Ledger, and Why Does It Kill Duplicates?

The ledger is a running record of which surfaces have been examined, to what depth, and with what result — so an agent that reconsiders a target has to consult what it already knows rather than re-probe from memory.

It attacks waste from two directions. The first is exact duplication: ~1 in 5 actions on real engagements were repeats. The second is context-loss duplication: about 20% of actions were wasted because prior state was not reloaded after compaction. Both are the same underlying defect — an agent that treats every moment as a fresh start will pay for the same knowledge twice.

Depth ladders and a stuck loop complete the mechanism. Instead of a binary "tested / not tested", each surface carries a depth level, so "I tried one payload" and "I worked the class properly" are no longer the same entry. The stuck loop gives the agent a defined response to being out of ideas that is not silence and not a fabricated finding.

## Why Is Scope Discipline a Legal Question, Not a Tidiness One?

Because the downside is not a missed finding, it is exclusion from the programme.

An out-of-scope request is a real-world action against a system the operator was not authorised to touch, and bug bounty programmes treat it accordingly — the README's framing is that a single such request can get you banned. A rule that lives in the always-loaded core is the only kind that can fire *before* the request goes out, which is why scope enforcement belongs with behaviour rather than with technique.

Rule 9 closes the other half of the loop: an agent must not dismiss an asset that is genuinely in scope simply because of where it is hosted. Both directions of scope error cost the operator money — one in credibility, the other in coverage.

## What Do the Local-LLM Offload and the Frontier Peer Agent Add?

They turn a single agent into a small pack with separate failure domains.

Rule 3.12's local-LLM offload is a context firewall: bulk reading — long response bodies, large source files, documentation dumps — is processed outside the primary hunting context, so the agent's working memory is spent on reasoning instead of transcription. Rule 3.14's frontier peer agent is the opposite trade: expensive, but it provides an independent reviewer for both findings and "secure" conclusions.

The pairing is what makes the kill-gate meaningful. A gate applied by the same context that produced the finding is a gate applied by a party with an interest in the outcome. An external reviewer with no stake in the claim and no shared context is a materially different check — and the resurrection-gate direction (challenging a *negative* conclusion) is the half that most agent pipelines omit entirely.

## How Does BugbountyRules Compare to Other Agent Security Skills?

Three architectures are competing for the same job.

| | BugbountyRules | Murrtada's bb skills | Sentry's security-review |
|---|---|---|---|
| Structure | One always-on behavioural core | 93 single-SKILL.md library | One review skill + many references |
| Emphasis | Depth of behaviour | Breadth of vulnerability classes | Confidence-tiered review |
| Verification | Hunter → Skeptic → Referee | 7-question verify-or-kill gate | HIGH/MEDIUM/LOW confidence |
| Strongest claim | Rules govern the agent globally | Primitive chaining (A→B→C) | Data-flow tracing discipline |
| Weakness | Single author, unproven at scale | No single global behavioural guarantee | Review-focused, not hunt-focused |

[github.com/murrtada/bug-bounty-agent-skills](https://github.com/murrtada/bug-bounty-agent-skills) is the closest ecosystem competitor: 93 offensive-security skills (`bb-methodology`, `bb-recon`, `bb-verify`, `bb-report` and a `hunt-*` family) rather than one core. Its verify-or-kill triage gate runs 7 questions on every finding before report-writing, and its `hunt-*` skills ship as primitives with explicit "chain to X" sections — so CSRF becomes account takeover and SSRF becomes cloud-metadata compromise. Per-class gate/verify/kill tables define what counts as proof, with rules like "OOB callback or it didn't happen" for blind SSRF. It covers modern classes including OWASP's ASI01–ASI10 agentic categories, CI/CD and GitHub Actions abuse, HTTP/2 single-packet races, and protocol-version shadow APIs. Verified 2026-10-01: NOASSERTION license, 1 star, created 2026-08-28, last push 2026-09-26, ~831 KB.

It is methodology-as-library. BugbountyRules is methodology-as-discipline. A hands-on comparison of five Claude Code security skills reached the same conclusion about what separates good from mediocre: the winning entry (Sentry's) defined a confidence system, carried false-positive awareness, and traced data flows rather than reciting patterns — "the difference between a thin checklist and a methodology is the difference between noise and signal" ([timonweb.com](https://timonweb.com/ai/i-checked-5-security-skills-for-claude-code-only-one-is-worth-installing/)). That review also documents the install-count trap: an aggregator repo carrying 900+ skills inflated the top-ranked skill's installs, which is why distribution metrics are not quality signals here.

## What Is the Ecosystem Risk of Installing a Behavioural Skill?

A behavioural skill is an executable instruction bundle, and it inherits the entire agent-skill supply chain problem.

The category is now formally named. OWASP's Top 10 for Agentic Applications (ASI01–ASI10) was published 2025-12-09 with 100+ contributors, and **ASI04, Agentic Supply Chain Vulnerabilities**, covers exactly what agents load at runtime: MCP servers, plugins, prompt templates, tool descriptors, and skills ([OWASP ASI overview](https://blckalpaca.at/en/knowledge-base/ai-agents/ai-agent-security-owasp/owasp-agentic-asi-top-10-2026)). A companion Agentic Skills Top 10 (AST10) project promotes the skills layer to a first-class vulnerable component. The same source documents grounded incidents: postmark-mcp, the first malicious MCP server found in the wild (Koi Security, September 2025); EchoLeak, CVE-2025-32711, CVSS 9.3; and a Gemini memory-poisoning attack (Rehberger, February 2025). In Galileo AI's December 2025 simulation, one compromised agent poisoned 87% of downstream decisions within four hours.

The scale numbers are worse than most teams assume. A large-scale study scanning 42,447 agent skills found 26.1% exhibit at least one security vulnerability, and about 5.2% show signs of likely malicious intent. ClawHub hosted 49,592 community skills as of April 2026, implying 2,500+ potentially malicious packages. The ClawHavoc campaign introduced 1,184 malicious skills to ClawHub, and five of them still evaded the updated ClawScan and VirusTotal between February and May 2026 ([CSA research note](https://labs.cloudsecurityalliance.org/research/csa-research-note-ai-agent-skill-scanner-bypass-20260629-csa/)).

Scanner coverage is not the answer, and there is a structural reason. Trail of Bits bypassed ClawHub's malicious skill detector, Cisco's agent skill scanner, and all three scanners integrated into skills.sh; three of the four malicious skills were conceived and implemented in under an hour using standard tricks plus reading the scanner source. The bypasses included roughly 100,000 newlines to push a payload past ClawHub's truncation window, malicious `.pyc` bytecode sitting next to benign source, DOCX/ZIP archive indirection, and social-engineering the LLM-as-judge layer with compliance-policy-sounding prose ([Trail of Bits](https://blog.trailofbits.com/2026/06/03/the-sorry-state-of-skill-distribution/)). Their conclusion is the ecosystem's framing: no amount of scanning or LLM analysis can reliably detect malicious content in agent skills — marketplaces are one layer, not a gate. One scanner-bypassing skill reportedly reached ~26,000 agents including corporate accounts, a vendor-reported figure that has not been independently verified ([CSO Online](https://csoonline.com/article/4188840/how-a-malicious-ai-agent-skill-passed-security-checks-and-reached-26000-users.html)).

The structural limit is worth stating precisely: formal static analysis cannot reason about natural-language instructions in a `SKILL.md`, because the consuming LLM interprets them at runtime. Even SkillFortify, reporting 96.95% F1 on a 540-skill benchmark, does not close that gap. An always-loaded behavioural skill is precisely the artefact class this research says scanners cannot validate.

The practical mitigations follow from the OWASP design principles of least agency and strong observability: treat scanner passage as one signal among many, verify publisher identity out-of-band, and manually read the behavioural directives in `SKILL.md` before you let them into an agent's context on every turn.

## What Are the Honest Limits?

BugbountyRules is a single-author project with 35 stars, 6 forks, zero open issues, and a repository history spanning two days (created 2026-08-17, last push 2026-08-18). It has not been independently benchmarked, and its numbers are its own.

Its most interesting verifiability claim is also its least tested. The repo ships `run-eval.sh`, which puts a rule's own text in front of an independent agent to check whether the rule actually instructs behaviour rather than merely reading well. That is a genuinely good idea — a rule set that can be evaluated for instructiveness is more than a prose artefact — but the results are not published against a third-party baseline, and no external party has reproduced them.

Two things the skill does not do: it does not replace the exploit knowledge in the bundled KB, and it does not make an agent correct. It makes an agent honest about what it knows. The economics explain why that is worth anything: one manual penetration test of a single application costs $2,400–$10,000, and complex engagements run to $40,000 or more ([nhimg.org](https://nhimg.org/articles/ai-agents-are-reshaping-penetration-testing-economics)). An agent that converts that spend into triager noise produces negative value; an agent that produces twelve validated findings beats one that produces eighty plausible ones.

## Who Should Install It, and How Do You Start?

It fits teams already running an agent against authorised targets — bug bounty programmes, internal red team scopes, CTF-style engagements — who have hit the false-positive wall rather than the knowledge wall.

A sensible adoption path:

1. Read `SKILL.md` yourself, line by line. It is 1,489 lines of behavioural directives and it will be in your agent's context on every turn; treat it like code you are about to run.
2. Confirm the repository's provenance out-of-band, and pin the commit you reviewed rather than tracking a branch.
3. Verify that Rule 1's scope handling matches your actual programme rules — scope enforcement is the one failure with legal consequences.
4. Start with the behaviour rules and the bundled KB off. Run a scoped engagement and check the false-positive rate before adding the technique layer.
5. If you need class breadth more than behavioural depth, pair it with a library-style skill set such as Murrtada's rather than expecting one core to cover both.

## FAQ

**What is BugbountyRules in one sentence?**
A Claude Code skill holding 42 always-active behavioural rules — scope, coverage, evidence, persistence — that govern how an agent hunts rather than which payloads it fires.

**How many rules does it actually define?**
Exactly 42, inside a 1,489-line `SKILL.md`, verified by parsing the repository file on 2026-10-01.

**What is the Hunter → Skeptic → Referee gate?**
An adversarial self-review that runs before report-writing: one pass finds, one pass attacks the finding, one adjudicates. It exists because a small model given eight findings waved through 3 of the 4 textbook false positives and inflated severity on 6 of 8.

**What is the coverage ledger for?**
Tracking which surfaces were examined and to what depth, so the agent does not repeat work. Roughly 1 in 5 actions on real engagements were exact duplicates, and about 20% were wasted because prior state was not reloaded after context compaction.

**Is installing a third-party agent skill safe if a scanner passed it?**
No. Trail of Bits bypassed ClawHub, Cisco and all three skills.sh scanners, and a scan of 42,447 agent skills found 26.1% with at least one vulnerability. Read the behavioural directives yourself, verify the publisher out-of-band, and treat scanner passage as one signal, not a gate.
