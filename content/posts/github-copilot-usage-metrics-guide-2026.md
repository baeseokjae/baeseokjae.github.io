---
cover:
  alt: 'GitHub Copilot Usage Metrics Guide 2026: Accuracy, Coverage, and Team Reporting'
  image: /images/github-copilot-usage-metrics-guide-2026.png
  relative: false
date: 2026-07-07 20:15:00+00:00
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
---

If you're paying for GitHub Copilot Enterprise across a 200-person engineering org, you need to know whether it's actually moving the needle. The good news: GitHub now exposes surprisingly detailed usage metrics through dashboards, REST APIs, and NDJSON exports. The bad news: the data has sharp edges that will mislead you if you don't understand how it's collected and attributed.

I've spent the last few months working with Copilot's metrics pipeline across several enterprise deployments, and this guide covers what I've found — the five metric categories, how data actually flows from IDE to dashboard, the API endpoints you'll need, and the attribution gotchas that will trip you up.

## The Five Metric Categories

GitHub organizes Copilot usage metrics into five buckets. Here's what each one actually tells you.

### Adoption

Adoption measures how many of your licensed developers are actively using Copilot. The headline numbers are Daily Active Users (DAU) and Weekly Active Users (WAU).

The interesting split here is in code review adoption. GitHub tracks two types of review users:

- **Active** — developers who manually request a Copilot code review
- **Passive** — developers who receive auto-assigned reviews

A team where most users are passive reviewers isn't really adopting the review feature. If you're running an enablement campaign, watch the active/passive ratio, not just total review users.

### Engagement

Engagement goes deeper than adoption — it measures *how* people use Copilot once they've opened it. The key signal is average chat requests per active user, broken down by language and IDE.

I've found this is the metric that correlates best with team satisfaction. A team with 80% DAU but only 2 chat requests per user per day is probably just accepting inline completions without really exploring what Copilot can do. A team at 60% DAU but 15 chat requests per user is actively using it as a pair programmer.

### Acceptance Rate

Acceptance rate measures how often developers accept Copilot's inline suggestions. High acceptance means the suggestions are relevant and trusted.

But don't chase a high acceptance rate as a goal in itself. A team that accepts 40% of suggestions but is writing complex, novel code is getting more value than a team at 80% that's only writing boilerplate. Context matters.

### Lines of Code (LoC)

LoC metrics are the most visible and the most misleading. GitHub reports lines suggested, lines added (accepted and inserted), and lines deleted.

The official docs are careful to call this a "directional measure" — and they're right. Lines of code is a vanity metric if you look at it in isolation. A single accepted suggestion that replaces 50 lines of boilerplate with a 5-line idiomatic solution is worth more than 200 lines of generated getters and setters.

That said, LoC trends *are* useful when you track them alongside PR lifecycle data. If lines added is going up and median time to merge is going down, you're probably seeing real productivity gains.

### Pull Request Lifecycle

This is the most actionable category for engineering leaders. GitHub tracks PR creation counts, PR merge counts, median time to merge, and review suggestion activity.

The key insight: PR lifecycle metrics can show Copilot activity even when IDE usage metrics are empty. That's because PR data comes from repository activity, not IDE telemetry. If a developer commits code written with Copilot in a terminal-based workflow (Copilot CLI, for example), the PR will show Copilot attribution even if the IDE never reported anything.

## Data Sources and Accuracy

This is where most people get confused. Copilot metrics come from two sources, and they behave differently.

### Client-Side IDE Telemetry

This is the primary data source. When a developer uses Copilot in VS Code, JetBrains, or another supported IDE, the IDE sends telemetry events directly to GitHub.

**What it covers:** Inline completions, chat interactions, agent mode sessions, code review requests — basically everything that happens inside the IDE.

**What it misses:** Users behind corporate proxies, restrictive network configurations, or who have telemetry disabled in their IDE settings. In practice, I've seen 5-15% of users fall into this category depending on how locked-down the corporate network is.

### Server-Side Telemetry

This is the fallback. GitHub can detect that a user is active based on server-side signals — API calls, license checks, that sort of thing.

**The catch:** Server-side users are fully counted toward DAU totals, but their dimensional breakdowns (LoC metrics, language breakdowns, etc.) remain empty. You'll see a user in your active user count but with zero lines of code attributed to them.

This creates a frustrating situation: your adoption numbers look healthy, but your per-user engagement metrics are artificially low because the server-side cohort has no breakdown data. If you're running a heavily locked-down enterprise, expect 10-20% of your DAU to be server-side only.

### Data Latency

Data is available within 2 full UTC days after the day closes. If you're looking at Monday's numbers on Wednesday morning, that's normal. The dashboard shows a 28-day rolling window, and historical data goes back up to 1 year from the current date.

Reports are available starting October 10, 2025. Organization-level analytics started on December 12, 2025. If you're comparing pre- and post-Copilot metrics, those are your baseline boundaries.

## API Deep Dive

The dashboard is fine for quick checks, but if you want to build real reporting, you need the API.

### The Copilot Usage Metrics API (Primary)

This is the API you should build against. It provides unified telemetry across completions, chat, and agent modes at enterprise, organization, and user levels.

**Authentication:** You need a fine-grained token with "Enterprise Copilot Metrics" (read) or "Organization Copilot Metrics" (read) permission. If you're using a classic PAT or OAuth token, you need the `manage_billing:copilot` scope.

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

**Response format:** NDJSON, delivered via signed URLs with limited expiration. You download the file, not a JSON response body. This means you can't just curl and pipe to jq — you need to follow the redirect and save the file.

Here's a practical script I use for daily pulls:

```bash
#!/bin/bash
# Daily Copilot metrics pull — enterprise level
ORG="my-org"
TOKEN="$GITHUB_TOKEN"
DAY=$(date -u -d "2 days ago" +%Y-%m-%d)
OUTPUT_DIR="./copilot-metrics/$DAY"

mkdir -p "$OUTPUT_DIR"

# Download the signed URL and save
download_ndjson() {
  local url="$1"
  local output="$2"
  local signed_url=$(curl -sS -H "Authorization: Bearer $TOKEN" "$url" | head -1)
  curl -sS -L "$signed_url" -o "$output"
}

download_ndjson \
  "https://api.github.com/orgs/$ORG/copilot/metrics/reports/organization-1-day?day=$DAY" \
  "$OUTPUT_DIR/org-$DAY.ndjson"

download_ndjson \
  "https://api.github.com/orgs/$ORG/copilot/metrics/reports/users-1-day?day=$DAY" \
  "$OUTPUT_DIR/users-$DAY.ndjson"

echo "Metrics saved to $OUTPUT_DIR"
```

### The Copilot User Management API (Separate)

This API handles license and seat assignment. It is **not** interchangeable with the usage metrics API. I've seen teams try to compare seat counts from the user management API with active user counts from the usage API and draw wrong conclusions. They measure different things — one tracks who has a license, the other tracks who actually used the tool.

## Organization Attribution Model

This is the most confusing part of Copilot metrics, and the docs don't make it obvious.

Organization-level metrics are based on **organization membership**, not on where individual actions occur. Here's what that means in practice:

- A user must have an active Copilot seat assigned within the enterprise to appear in metrics at all
- A single user's usage may appear in *multiple* organization dashboards if they belong to multiple orgs
- The same user is counted only once in enterprise-level totals (deduplicated)
- If licenses are assigned in a dedicated "shell" org, users still appear in metrics for all other orgs they belong to

**The implication:** You cannot sum organization-level totals to get an enterprise-level total. The enterprise total deduplicates users across orgs, so the sum of org-level DAU will always be higher than the enterprise-level DAU.

This is by design — org-level metrics are meant for visibility into adoption within a specific org, not for enterprise-wide rollups. If you need enterprise totals, use the enterprise-level endpoints directly.

## Team-Level Reporting

There's no dedicated team-level endpoint. Instead, you build team metrics by joining two reports:

1. **User usage report** — per-user metrics for a given day
2. **User-teams report** — which teams each user belongs to

The user-teams endpoints are:

```
GET /enterprises/{enterprise}/copilot/metrics/reports/user-teams-1-day?day=DAY
GET /orgs/{org}/copilot/metrics/reports/user-teams-1-day?day=DAY
```

Here's how I do the join in practice:

```python
import pandas as pd
import json

# Load the NDJSON files
users = pd.read_json("users-2026-07-05.ndjson", lines=True)
teams = pd.read_json("user-teams-2026-07-05.ndjson", lines=True)

# Flatten the team memberships
team_members = teams.explode("teams")

# Join user metrics with team membership
team_metrics = team_members.merge(
    users,
    left_on="user_id",
    right_on="id",
    how="inner"
)

# Aggregate by team
team_summary = team_metrics.groupby("teams").agg({
    "copilot_ide_code_completions_acceptance_rate": "mean",
    "copilot_ide_chat_total_requests": "sum",
    "user_id": "nunique"
}).rename(columns={"user_id": "active_users"})

print(team_summary.to_string())
```

This gives you per-team adoption and engagement numbers that you can pipe into a BI dashboard or a weekly Slack report.

## Common Pitfalls

After working with this data across several orgs, here are the mistakes I see most often:

**1. Comparing usage metrics to seat counts.** The usage API and the user management API measure different things. Don't put them in the same chart.

**2. Summing org-level metrics to get enterprise totals.** Users are deduplicated at the enterprise level. The sum of org DAU will always exceed enterprise DAU.

**3. Ignoring server-side users.** If 15% of your DAU is server-side only, your per-user engagement metrics are missing that cohort's breakdown data. Your average chat requests per user will look lower than reality.

**4. Treating LoC as a productivity metric.** Lines of code is directional at best. A developer who writes 100 lines of high-quality, AI-assisted code is probably more productive than one who writes 500 lines of generated boilerplate.

**5. Expecting real-time data.** The 2-day processing delay means you're always looking at data from two days ago. Don't build real-time dashboards on top of this — build daily or weekly reports.

**6. Forgetting that PR metrics come from a different pipeline.** PR lifecycle data can show Copilot attribution even when IDE telemetry is absent. This is correct behavior, but it can confuse your reporting if you're not expecting it.

## Best Practices for Setting Up Dashboards

Here's what I've found works well in practice:

**Start with a weekly cadence.** Daily data is noisy and has the 2-day lag. A weekly snapshot (every Monday for the previous week) smooths out the noise and gives you a consistent baseline.

**Track the right leading indicators.** I watch three things week over week:

- DAU / licensed seats (adoption ratio)
- Average chat requests per active user (engagement depth)
- Median time to merge (outcome)

If adoption is flat but engagement is up, that's fine — your existing users are getting deeper value. If adoption is up but engagement is flat, you're adding casual users who aren't really integrating Copilot into their workflow.

**Build a team-level view.** The user-teams join is worth the effort. Engineering managers care about their team's numbers, not the org-wide average. A team with low adoption might have a legitimate reason (they're in a maintenance phase, or their stack isn't well-supported), and you can't see that in the org-level aggregate.

**Cross-reference with DORA metrics.** If you're already tracking deployment frequency, lead time for changes, and change failure rate, overlay your Copilot adoption data on top. I've seen orgs where high-Copilot-adoption teams ship 20-30% more frequently with no change in failure rate — that's the real ROI story. For more on developer productivity measurement, check out my [AI Developer Productivity Metrics guide](/posts/ai-developer-productivity-metrics-2026/).

## The Bottom Line

GitHub Copilot's metrics pipeline is the most mature of any AI coding tool on the market — competitors like Cursor and Claude Code don't offer anything close to this level of enterprise reporting. But maturity doesn't mean simplicity. The attribution model, the dual telemetry sources, and the API structure all have sharp edges that will bite you if you don't understand them.

Build your reporting around the five metric categories, use the Usage Metrics API (not the User Management API), and always account for the 2-day data latency. If you do that, you'll have a solid foundation for understanding whether Copilot is actually making your engineering organization faster.

For a broader look at setting up Copilot across your organization, see the [GitHub Copilot Enterprise Guide](/posts/github-copilot-enterprise-guide-2026/). And if you're evaluating whether agent mode changes the metrics picture, the [Copilot Agent Mode guide](/posts/github-copilot-agent-mode-2026/) covers what's different when Copilot runs autonomously.
