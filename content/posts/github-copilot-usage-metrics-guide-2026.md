---
cover:
  alt: 'Diagram of GitHub Copilot usage metrics report families: aggregated enterprise and organization reports, per-user and user-teams reports joined on user_id to build team totals, with teams under five seated Copilot users excluded from the join.'
  image: /images/github-copilot-usage-metrics-guide-2026.png
  relative: false
date: 2026-07-07 20:15:00+00:00
lastmod: 2026-11-19 15:20:00+00:00
description: 'Complete guide to GitHub Copilot usage metrics in 2026: the five metric categories, data accuracy gotchas, API access patterns, team-level reporting, and common pitfalls that trip up engineering leaders.'
draft: false
schema: schema-github-copilot-usage-metrics-guide-2026
series:
- GitHub Copilot Enterprise
tags:
- github copilot
- developer productivity
- engineering metrics
- dora metrics
- ai coding
- enterprise
title: 'GitHub Copilot Usage Metrics: Categories and API Reporting'
---

If you're paying for GitHub Copilot Enterprise across a 200-person engineering org, you need to know whether it's actually moving the needle. The good news: [GitHub's Copilot usage metrics](https://docs.github.com/en/copilot/concepts/copilot-usage-metrics/copilot-metrics) now expose surprisingly detailed data through dashboards, REST APIs, and NDJSON exports. The bad news: the data has sharp edges that will mislead you if you don't understand how it's collected and attributed.

This guide works through what the documentation and the report shapes actually say — the five metric categories, how data flows from IDE and server-side telemetry into the dashboard, the API endpoints you'll need, and the attribution rules that will mislead a rollout or renewal review if you skip them. Every factual claim below is tied to a GitHub documentation page, linked beside the claim it supports; the illustrative comparisons in the body are labelled as illustrations rather than measurements.

## The Five Metric Categories

GitHub organizes Copilot usage metrics into [five categories](https://docs.github.com/en/copilot/concepts/copilot-usage-metrics/copilot-metrics). Here's what each one actually tells you.

### Adoption

Adoption measures how many of your licensed developers are actively using Copilot. The headline numbers are Daily Active Users (DAU) and Weekly Active Users (WAU); the [field reference](https://docs.github.com/en/copilot/reference/copilot-usage-metrics/copilot-usage-metrics) defines DAU as the number of unique users who used Copilot on a given day, and WAU as the number of unique users who used it during a seven-day window.

The interesting split here is in code review adoption. GitHub tracks two types of review users, both defined in the [field reference](https://docs.github.com/en/copilot/reference/copilot-usage-metrics/copilot-usage-metrics):

- **Active** — developers who manually request a Copilot code review, or apply a Copilot review suggestion
- **Passive** — developers who have Copilot automatically assigned to review their pull request without actively engaging with it

A team where most users are passive reviewers isn't really adopting the review feature. If you're running an enablement campaign, watch the active/passive ratio, not just total review users.

### Engagement

Engagement goes deeper than adoption — it measures *how* people use Copilot once they've opened it. The headline signal is average chat requests per active user, and the same reports carry activity breakdowns by IDE, language and feature, so you can see which surfaces people actually use. The [field reference](https://docs.github.com/en/copilot/reference/copilot-usage-metrics/copilot-usage-metrics) defines the chat-request metric and the `totals_by_ide`, `totals_by_language_feature` and `totals_by_feature` arrays the breakdowns come from.

Engagement depth is what separates teams using Copilot as an assistant from teams accepting autocomplete. Two teams can both report 80% DAU — one at two chat requests per active user per day, the other at fifteen — and only the second is exploring chat, agent mode and the rest of the surface. Those two figures are illustrative of the comparison, not measured benchmarks.

### Acceptance Rate

Acceptance rate measures how often developers accept Copilot's inline suggestions — formally, the percentage of suggestions accepted by users, per the [field reference](https://docs.github.com/en/copilot/reference/copilot-usage-metrics/copilot-usage-metrics). High acceptance usually suggests the suggestions are relevant and trusted.

But don't chase a high acceptance rate as a goal in itself. Take a hypothetical team that accepts 40% of suggestions on complex, novel code and one that accepts 80% on boilerplate: the first is plausibly getting more value. Those two rates are an illustration of the comparison, not measured acceptance rates from any tenant. Context matters.

### Lines of Code (LoC)

LoC metrics are the most visible and the most misleading. The [metrics concept page](https://docs.github.com/en/copilot/concepts/copilot-usage-metrics/copilot-metrics) describes the category as code suggested, added, or deleted in the editor, and the [field reference](https://docs.github.com/en/copilot/reference/copilot-usage-metrics/copilot-usage-metrics) breaks the same activity down by feature, IDE and language through the `loc_*` fields in its activity breakdown arrays.

The [concept page's](https://docs.github.com/en/copilot/concepts/copilot-usage-metrics/copilot-metrics) own advice is the right frame: "Look for patterns across these signals rather than treating any single number as a measure of productivity." That lands hardest on lines of code. A single accepted suggestion that replaces 50 lines of boilerplate with a 5-line idiomatic solution is worth more than 200 lines of generated getters and setters — an illustration of the point, not a measured comparison.

That said, LoC trends *are* useful when you track them alongside PR lifecycle data. If lines added is going up and median time to merge is going down, you're probably seeing real productivity gains.

### Pull Request Lifecycle

This is the most actionable category for engineering leaders. GitHub tracks PR creation counts, PR merge counts, time to merge, and review activity — the category table on the [metrics concept page](https://docs.github.com/en/copilot/concepts/copilot-usage-metrics/copilot-metrics) is the definition to check against.

The key insight: PR lifecycle metrics can show Copilot activity even when IDE usage metrics are empty. That's because, as the [metrics concept page](https://docs.github.com/en/copilot/concepts/copilot-usage-metrics/copilot-metrics) puts it, repository insights use server-side pull request and review data and do not depend on IDE telemetry. If a developer commits code written with Copilot in a terminal-based workflow (Copilot CLI, for example), the repository-level report can still carry that activity even if the IDE never reported anything.

## Data Sources and Accuracy

This is where most people get confused. Copilot metrics come from two telemetry paths, and they behave differently. GitHub's [coverage statement](https://docs.github.com/en/copilot/concepts/copilot-usage-metrics/copilot-metrics) is blunt about the boundary: usage metrics combine telemetry from IDEs, Copilot CLI and other supported surfaces, they aren't a complete record of all Copilot activity, and coverage varies by metric and report.

### Client-Side IDE Telemetry

This is the primary data source the docs describe: detailed IDE breakdowns require supported clients with telemetry enabled, which is the [concept page's](https://docs.github.com/en/copilot/concepts/copilot-usage-metrics/copilot-metrics) wording for the client-side path.

**What it covers:** Inline completions, chat interactions, agent mode sessions and code review requests — the per-user `used_*` indicators in the [field reference](https://docs.github.com/en/copilot/reference/copilot-usage-metrics/copilot-usage-metrics) are the closest documented inventory of these surfaces.

**What it misses:** Because detailed IDE breakdowns require supported clients with telemetry enabled, users on clients GitHub doesn't support for telemetry — or whose telemetry never arrives — drop out of the breakdown data. The [coverage section](https://docs.github.com/en/copilot/concepts/copilot-usage-metrics/copilot-metrics) states the requirement but publishes no share of users affected, and this article does not estimate one.

### Server-Side Telemetry

This is the fallback. GitHub can identify a user as active from server-side signals even when no client-side detail arrives. The [reference page](https://docs.github.com/en/copilot/reference/copilot-usage-metrics/copilot-usage-metrics) describes the record shape: aggregated reports contain one record per enterprise or organization, active-user counts include users identified through both client-side and server-side telemetry, and users surfaced only through server-side telemetry are counted in active-user totals but may not appear in the dimensional breakdown arrays (`totals_by_ide`, `totals_by_feature`).

**The catch:** Server-side users are counted toward DAU totals, but their dimensional breakdowns (LoC metrics, language breakdowns, etc.) can be missing. You'll see a user in your active user count with no lines of code attributed to them.

This creates a frustrating situation: your adoption numbers look healthy, but your per-user engagement metrics are artificially low because the server-side cohort has no breakdown data. In a heavily locked-down enterprise the server-side cohort can be the only evidence you have that some users are active at all — and GitHub publishes no figure for how large that cohort typically is.

### Data Latency

Data for a given day is available within two full UTC days after that day closes, per the [metrics concept page](https://docs.github.com/en/copilot/concepts/copilot-usage-metrics/copilot-metrics). If you're looking at Monday's numbers on Wednesday morning, that's normal. The REST API also offers `*-28-day/latest` report endpoints that return the most recent 28-day report, so you don't have to assemble a rolling window from daily files yourself.

The [REST API reference](https://docs.github.com/en/rest/copilot/copilot-usage-metrics) pins the availability boundary separately for each scope. On the enterprise report endpoints it states that reports are available starting from October 10, 2025, and that historical data can be accessed for up to 1 year from the current date. The organization report endpoints carry no equivalent availability or retention sentence, and GitHub's [reconciling usage metrics guide](https://docs.github.com/en/copilot/reference/copilot-usage-metrics/reconciling-usage-metrics) supplies the organization date: "Organization-level reports are available starting December 12, 2025." Both dates are documented availability, not an observed backfill, and the scope you query sets the earliest baseline a pre/post comparison can honestly use — an organization-level series starts roughly two months later than an enterprise one.

## API Deep Dive

The dashboard is fine for quick checks, but if you want to build real reporting, you need the API.

### The Copilot Usage Metrics API (Primary)

This is the API you should build against. According to the [Copilot usage metrics REST reference](https://docs.github.com/en/rest/copilot/copilot-usage-metrics), the API publishes report endpoint families at enterprise and organization scope — aggregated, per-user, user-teams and per-repository reports — and returns signed download links to the report files plus the report date or range, not an inline JSON body.

**Authentication:** Permissions differ by scope, as listed on each endpoint in the [reference](https://docs.github.com/en/rest/copilot/copilot-usage-metrics). Enterprise report endpoints need a fine-grained "View Enterprise Copilot Metrics" (read) permission, or a classic PAT/OAuth token with `manage_billing:copilot` or `read:enterprise`. Organization report endpoints need "View Organization Copilot Metrics" (read), or a classic token with `read:org`. Enterprise owners, billing managers and authorized users can call the enterprise endpoints; organization owners and authorized users can call the organization ones.

**Key endpoints:**

```
GET /enterprises/{enterprise}/copilot/metrics/reports/enterprise-1-day?day=DAY
GET /enterprises/{enterprise}/copilot/metrics/reports/enterprise-28-day/latest
GET /enterprises/{enterprise}/copilot/metrics/reports/users-1-day?day=DAY
GET /enterprises/{enterprise}/copilot/metrics/reports/users-28-day/latest
GET /orgs/{org}/copilot/metrics/reports/organization-1-day?day=DAY
GET /orgs/{org}/copilot/metrics/reports/organization-28-day/latest
GET /orgs/{org}/copilot/metrics/reports/users-1-day?day=DAY
GET /orgs/{org}/copilot/metrics/reports/users-28-day/latest
```

**Response format:** NDJSON, delivered via signed URLs with limited expiration. You download the file, not a JSON response body — the [reference](https://docs.github.com/en/rest/copilot/copilot-usage-metrics) describes the response as containing download links to the report files plus the specific date of the report. This means you can't just curl and pipe to jq — you need to follow the redirect and save the file.

Here's a two-step daily pull sketch. Step one asks the API for the report envelope; step two downloads the NDJSON files that the envelope's `download_links` array points at, because the API response never contains the metrics themselves. The sketch has not been run against a live organization — treat it as a shape to adapt, not as a finished job:

```bash
#!/bin/bash
# Sketch, not an executed reference implementation: no live organization was
# queried. Step 1 returns a JSON envelope that lists signed download links;
# step 2 fetches the NDJSON behind each link before that signature expires.
# The bearer token below is redacted in this listing - substitute your own.
set -euo pipefail
API="https://api.github.com"
ORG="my-org"
DAY=$(date -u -d "2 days ago" +%Y-%m-%d)
OUT="./copilot-metrics/$DAY"
mkdir -p "$OUT"

for report in organization users; do
  ENVELOPE="$OUT/${report}-${DAY}.envelope.json"
  curl -sS -L \
    -H "Authorization: Bearer ***" \
    -H "Accept: application/vnd.github+json" \
    "$API/orgs/$ORG/copilot/metrics/reports/${report}-1-day?day=$DAY" \
    -o "$ENVELOPE"

  # Envelope shape from the reference: {"download_links": [...], "report_day": "..."}
  jq -r '.download_links[]' "$ENVELOPE" | nl -ba -w1 -s' ' |
  while read -r idx link; do
    curl -sS -L "$link" -o "$OUT/${report}-${DAY}-part${idx}.ndjson"
  done
done

wc -l "$OUT"/*.ndjson
```

The exact link field names sit on the [REST reference page](https://docs.github.com/en/rest/copilot/copilot-usage-metrics), and they are the part of the response that changes — read them there rather than hard-coding a guess from this sketch.

### The Copilot User Management API (Separate)

This API handles license and seat assignment. It is **not** interchangeable with the usage metrics API — the [concept page](https://docs.github.com/en/copilot/concepts/copilot-usage-metrics/copilot-metrics) draws the same line, noting that usage metrics measure activity, not license assignments. I've seen teams try to compare seat counts from the user management API with active user counts from the usage API and draw wrong conclusions. They measure different things — one tracks who has a license, the other tracks who actually used the tool.

## Organization Attribution Model

This is the most confusing part of Copilot metrics, and the docs don't make it obvious.

Organization-level metrics are based on **organization membership**, not on where individual actions occur. That rule, and the seat requirement that gates it, are stated on GitHub's [reconciling usage metrics guide](https://docs.github.com/en/copilot/reference/copilot-usage-metrics/reconciling-usage-metrics): to appear in an enterprise's metrics, a user must have an active Copilot seat assigned within that enterprise, and once they do, their usage is attributed to every organization in that enterprise they belong to, regardless of where the seat is assigned. The [metrics concept page](https://docs.github.com/en/copilot/concepts/copilot-usage-metrics/copilot-metrics) states the reporting consequence: organization-level metrics can overlap because the same user can belong to multiple organizations, so don't add organization totals to calculate an enterprise total.

What follows from the reconciling guide's description:

- A user must have an active Copilot seat assigned within the enterprise to appear in its metrics at all; a seat in an organization outside the enterprise does not substitute for one inside it
- A single user's usage may appear in *multiple* organization dashboards if they belong to multiple orgs
- Enterprise-level reports deduplicate users across organizations; organization-level reports do not
- If licenses are assigned in a dedicated organization for administrative purposes, users still appear in the metrics for the other organizations in the enterprise they belong to

**The implication:** organization totals are not additive to an enterprise total. Because the enterprise report deduplicates users across organizations, a sum of org-level DAU overstates the enterprise figure by however many users span more than one org.

This is by design — org-level metrics are meant for visibility into adoption within a specific org, not for enterprise-wide rollups. If you need enterprise totals, use the enterprise-level endpoints directly.

## Team-Level Reporting

There's no dedicated team-level endpoint. [Team-level Copilot usage metrics](https://docs.github.com/en/copilot/reference/copilot-usage-metrics/team-level-metrics) is a documented join of two daily report families:

1. **Per-user usage report** (`*-users-1-day`) — each user's Copilot activity for the day, keyed by `user_id`
2. **User-teams report** (`*-user-teams-1-day`) — one row per `(user, team)` pair, with `user_id`, `user_login`, `day`, `organization_id` or `enterprise_id`, `team_id` and `slug`

The user-teams endpoints are:

```
GET /enterprises/{enterprise}/copilot/metrics/reports/user-teams-1-day?day=DAY
GET /orgs/{org}/copilot/metrics/reports/user-teams-1-day?day=DAY
```

Join on `user_id` and aggregate by `team_id`, keeping `slug` as the display name:

```python
import pandas as pd

# Both files are the daily reports for the same day.
users = pd.read_json("users-2026-11-17.ndjson", lines=True)       # *-users-1-day
teams = pd.read_json("user-teams-2026-11-17.ndjson", lines=True)  # *-user-teams-1-day

# One row per (user, team) pair, so a user in two teams adds to both.
joined = teams.merge(users, on="user_id", how="inner")

team_summary = joined.groupby(["team_id", "slug"]).agg(
    active_users=("user_id", "nunique"),
    credits_used=("ai_credits_used", "sum"),
).reset_index()

print(team_summary.sort_values("active_users", ascending=False).to_string(index=False))
```

`ai_credits_used` and the `used_*` feature indicators are the per-user fields the [reference page](https://docs.github.com/en/copilot/reference/copilot-usage-metrics/copilot-usage-metrics) documents; the same page states that per-user reports do not contain active-user counts, `pull_requests` or `totals_by_ai_adoption_phase`, so those have to come from the aggregated reports instead. This snippet was not executed here — there is no live tenant behind it — so treat the field names as a starting point to check against the report you actually download.

Two documented boundary conditions, both from the [team-level metrics page](https://docs.github.com/en/copilot/reference/copilot-usage-metrics/team-level-metrics), change the answer:

- **Under-threshold teams disappear.** Teams with fewer than 5 seated Copilot users on a given day are excluded from the user-teams report, so their members' activity exists in the per-user report but in no team row.
- **Team totals do not add back up to the entity total.** Summing team rows gives a figure below the organization or enterprise total, because users who only belong to sub-threshold teams are missing from every team aggregate.

That gives you per-team adoption and engagement numbers that you can pipe into a BI dashboard or a weekly Slack report — provided you label the shortfall rather than presenting the team sum as an entity total.

## Common Pitfalls

Here are the mistakes that most often break these reports:

**1. Comparing usage metrics to seat counts.** The [metrics concept page](https://docs.github.com/en/copilot/concepts/copilot-usage-metrics/copilot-metrics) is explicit that usage metrics measure activity, not license assignments, and that seat and license information belongs to the Copilot user management API. Don't put the two in the same chart.

**2. Summing org-level metrics to get enterprise totals.** Users are deduplicated at the enterprise level, so a sum of org DAU is not an enterprise figure.

**3. Ignoring server-side users.** Users counted only through server-side telemetry contribute to active-user totals but may not appear in the dimensional breakdown arrays. If that cohort is large, your per-feature averages look lower than the activity behind them — and there is no published figure telling you how large it is, so measure the gap in your own reports rather than assuming one.

**4. Treating LoC as a productivity metric.** Lines of code is directional at best. Put a hypothetical developer producing 100 lines of carefully reviewed, AI-assisted code beside one producing 500 lines of generated boilerplate and the line counts rank them the wrong way round; the numbers here illustrate the ranking problem, they are not measured output.

**5. Expecting real-time data.** The two-full-UTC-day processing delay means you're always looking at data from two days ago. Don't build real-time dashboards on top of this — build daily or weekly reports.

**6. Forgetting that PR metrics come from a different pipeline.** Repository-level reports use server-side pull request and review data, so they can contain activity even when IDE telemetry is absent. This is correct behavior, but it can confuse your reporting if you're not expecting it.

## Best Practices for Setting Up Dashboards

Here's what works in practice:

**Start with a weekly cadence.** Daily data is noisy and has the two-day lag. A weekly snapshot (every Monday for the previous week) smooths out the noise and gives you a consistent baseline.

**Track the right leading indicators.** Watch three things week over week:

- DAU / licensed seats (adoption ratio)
- Average chat requests per active user (engagement depth)
- Median time to merge (outcome)

If adoption is flat but engagement is up, that's fine — your existing users are getting deeper value. If adoption is up but engagement is flat, you're adding casual users who aren't really integrating Copilot into their workflow.

**Build a team-level view.** The user-teams join is worth the effort. Engineering managers care about their team's numbers, not the org-wide average. A team with low adoption might have a legitimate reason (they're in a maintenance phase, or their stack isn't well-supported), and you can't see that in the org-level aggregate.

**Cross-reference with DORA metrics.** If you're already tracking deployment frequency, lead time for changes, and change failure rate, overlay your Copilot adoption data on top. Do it as a correlation you state carefully: adoption and delivery trends moving together is a hypothesis worth testing, not attribution — Copilot metrics alone cannot tell you that the tool caused the change. For more on developer productivity measurement, check out my [AI Developer Productivity Metrics guide](/posts/ai-developer-productivity-metrics-2026/).

## The Bottom Line

GitHub Copilot's metrics pipeline is unusually detailed for an enterprise AI coding tool: five metric categories, several report families, and NDJSON exports you can reconcile yourself. But breadth doesn't mean simplicity. The attribution model, the dual telemetry sources, and the API structure all have sharp edges that will bite you if you don't understand them.

Build your reporting around the five metric categories, use the Usage Metrics API (not the User Management API), and always account for the 2-day data latency. If you do that, you'll have a solid foundation for understanding whether Copilot is actually making your engineering organization faster.

For a broader look at setting up Copilot across your organization, see the [GitHub Copilot Enterprise Guide](/posts/github-copilot-enterprise-guide-2026/). And if you're evaluating whether agent mode changes the metrics picture, the [Copilot Agent Mode guide](/posts/github-copilot-agent-mode-2026/) covers what's different when Copilot runs autonomously.
