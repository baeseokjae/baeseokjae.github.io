---
cover:
  alt: 'GitHub Copilot Metrics: Accuracy, Coverage and Team Reports'
  image: /images/copilot-usage-metrics-accuracy-coverage-guide-2026.png
  relative: false
date: 2026-07-07 21:00:00+00:00
description: A practical deep-dive into GitHub Copilot usage metrics accuracy, data coverage gaps, and building reliable team-level reports. What the numbers actually mean and where they break down.
draft: false
lastmod: 2026-11-19 00:00:00+00:00
schema: schema-copilot-usage-metrics-accuracy-coverage-guide-2026
series:
- GitHub Copilot Enterprise
tags:
- github copilot
- developer productivity
- engineering metrics
- dora metrics
- ai coding
- enterprise
- data accuracy
title: 'GitHub Copilot Metrics: Accuracy, Coverage and Team Reports'
---

If you administer Copilot for a few hundred engineers, the usage dashboard answers a simple question badly: *can I trust these numbers?* This guide works through the three questions that decide the answer — how accurate the metrics are, what the telemetry does not cover, and how to produce per-team totals that the API does not publish. Every factual rule below is tied to GitHub's own documentation, re-read on 2026-11-19; the quantities GitHub does not publish are labelled as unpublished rather than filled in with an estimate.

## Accuracy: What the Numbers Actually Mean

Copilot usage metrics come from two telemetry paths that do not tell the same story. The documentation is explicit that dashboard data is "primarily based on IDE telemetry and is supplemented by server-side telemetry to capture additional active users" ([view usage and adoption](https://docs.github.com/en/copilot/how-tos/administer-copilot/view-usage-and-adoption)).

### Client-Side vs Server-Side Telemetry

**Client-side IDE telemetry** is the primary source. When a developer uses Copilot in VS Code, JetBrains, Visual Studio, Xcode, Eclipse or another supported IDE, the extension reports the events — completions generated and accepted, chat requests, agent edits. This is where the dimensional data lives: language breakdowns, per-feature counts, lines-of-code metrics.

**Server-side telemetry** is the supplement. Copilot can record a user's activity server-side when no qualifying client telemetry arrives, which confirms that the user is active without observing what happens inside the editor; GitHub's documentation names server-side telemetry as the second source but does not enumerate which signals it covers. Users confirmed only this way are still counted in active-user totals, and in per-user reports they carry only the most recently detected IDE and extension version; their per-IDE, per-feature and lines-of-code breakdowns stay empty ([reconciling usage metrics](https://docs.github.com/en/copilot/reference/copilot-usage-metrics/reconciling-usage-metrics)).

That asymmetry is the trap. A user can appear in your active count with zero completions, zero chat requests and zero lines of code, and nothing on the dashboard warns you that the row is a different kind of observation. GitHub does not publish what share of active users this cohort represents, but the per-user daily report labels it: `client_telemetry_present` is `false` when Copilot recorded the user's activity server-side and no qualifying client telemetry arrived that day ([copilot usage metrics](https://docs.github.com/en/copilot/reference/copilot-usage-metrics/copilot-usage-metrics)). Counting rows where that field is `false` and dividing by the `daily_active_users` figure for the same day and scope gives the share of your active users that rests on server-side evidence alone. Two cautions come with the field: it is null or omitted when the signal is unknown or not evaluated — including for users whose only activity was Copilot cloud agent or Copilot code review — and `false` does not explain why telemetry is missing. A shortcut of counting rows whose per-feature counts are all zero is therefore an upper bound on that cohort rather than the documented definition, because it also catches the agent-only and review-only users whom the field deliberately leaves unset. Either way it is one query against data you already have, not a benchmark.

**What to do about it:** when computing per-user engagement metrics, keep only rows whose `client_telemetry_present` is `true` for the period, and treat null as unknown rather than as client-side activity. The denominator becomes "users with measurable activity" rather than "all active users". That gives a more honest picture of engagement depth, at the cost of a slightly lower headline adoption number — and you should say which denominator a report uses, because the two are not interchangeable.

### The Two-Full-UTC-Day Data Window

Data for a given day is available within two full UTC days after that day closes ([view usage and adoption](https://docs.github.com/en/copilot/how-tos/administer-copilot/view-usage-and-adoption)). The documentation states a maximum window, not a landing time: a Monday's data is complete by the end of Wednesday UTC, but nothing promises it appears on Tuesday morning.

The practical impact is the same either way: don't build real-time dashboards. Teams that wire Copilot metrics into a live panel spend Tuesday afternoon looking at zeroes. Build daily or weekly batch reports instead. A script that pulls the last complete day — or a Saturday-to-Friday week, which is fully closed two UTC days after Friday — gives clean, consistent snapshots.

### Attribution Accuracy: The Org Membership Trap

This is the one that trips up most engineering leaders. Organization-level metrics are based on **organization membership**, not on where the user's actions occurred ([reconciling usage metrics](https://docs.github.com/en/copilot/reference/copilot-usage-metrics/reconciling-usage-metrics)). A user with an active seat in the enterprise is attributed to every organization in that enterprise they belong to, regardless of where the seat is used.

Illustrative example: Alice belongs to both the Platform Engineering org and the Security org, and writes code in a Platform Engineering repository. Her usage appears in both org dashboards. Sum the DAU across your orgs and you count Alice twice.

Enterprise-level reports deduplicate users across organizations; organization-level reports do not. That is by design — org-level metrics describe adoption inside one org, not an enterprise rollup. If you build a consolidated report by summing org dashboards, the total will be wrong, and it will be wrong by an amount that grows as your engineers join more orgs.

**The fix:** use the enterprise-level endpoints (`/enterprises/{enterprise}/copilot/metrics/...`) for top-line numbers. Use org-level endpoints to understand adoption patterns within a specific org, and never sum them into an enterprise total.

## Coverage: What Gets Counted and What Doesn't

Coverage is the second dimension of accuracy. Even when telemetry is working, it does not cover every scenario.

### IDE and Version Coverage

Lines-of-code metrics require minimum IDE and Copilot Chat extension versions, and the minimums differ by feature. Users below the line still generate completions and chat activity, but contribute no LoC data, so LoC totals undercount until they upgrade ([lines of code metrics](https://docs.github.com/en/copilot/reference/copilot-usage-metrics/lines-of-code-metrics)):

| IDE | Feature | Minimum IDE version | Minimum Copilot Chat extension |
|-----|---------|--------------------:|-------------------------------:|
| Eclipse | code_completion | 4.31 | 0.9.3.202507240902 |
| Eclipse | chat_panel | 4.31 | 0.11.0.202508291001 |
| Eclipse | agent_edit | 4.31 | 0.10.0.202508110512 |
| JetBrains | code_completion, chat_panel, chat_inline, agent_edit | 2024.2.6 | 1.5.52-241 |
| Visual Studio | code_completion, chat_panel | 17.14.13 | 18.0.471.29466 |
| Visual Studio | chat_inline, agent_edit | 17.14.14 | 18.0.471.29466 |
| VS Code | code_completion | 1.104.0 | 0.31.0 |
| VS Code | chat_panel | 1.102.0 | 0.29.0 |
| VS Code | chat_inline | 1.103.2 | 0.30.3 |
| VS Code | agent_edit | 1.103.0 | 0.30.0 |
| Xcode | code_completion | 14.3.1 | 0.40.0 |
| Xcode | chat_panel | 15.0 | 0.43.0 |
| Xcode | agent_edit | 15.2 | 0.41.0 |

The pattern matters more than the individual cells: `agent_edit` and `chat_inline` generally carry the strictest minimum, so a fleet that is "current enough for completions" can still be below the line for the features you care about most. Collapsing the table to one version per IDE — as many secondary summaries do — overstates coverage for Visual Studio and Xcode in particular.

**What to check:** you do not have to guess the size of the problem. Per-user reports include `last_known_ide_version` and `last_known_plugin_version`, so you can count users below each minimum from the same export you use for reporting, per IDE and per feature. Report that count next to the LoC total; an LoC number without a coverage denominator invites the wrong conclusion.

### Agent Mode Coverage

Agent mode does not follow the "suggest then accept" flow that inline completions use. Instead of a suggestion event followed by an accept or reject event, agent edits are counted as `loc_added_sum` and `loc_deleted_sum` under the `agent_edit` feature bucket, and are excluded from suggested metrics ([lines of code metrics](https://docs.github.com/en/copilot/reference/copilot-usage-metrics/lines-of-code-metrics)).

This means agent activity has no acceptance count at all. If your team leans on agent mode, a completions acceptance rate looks worse than the value Copilot is delivering: code is being written, just not measured through accept events. Keep a separate agent view — agent edits, agent LoC added — instead of folding it into acceptance rate.

For more on how agent mode changes the Copilot experience, see the [Copilot Agent Mode guide](/posts/github-copilot-agent-mode-2026/).

### PR Lifecycle Coverage

Pull request lifecycle metrics come from a different pipeline: repository activity on GitHub.com rather than IDE telemetry. The documentation notes that PR metrics "may appear even if IDE usage metrics are absent, since pull request data is derived from repository activity" ([reconciling usage metrics](https://docs.github.com/en/copilot/reference/copilot-usage-metrics/reconciling-usage-metrics)).

This is a feature, not a bug — it captures Copilot work that IDE telemetry would miss, including CLI and web-UI workflows. It also means the PR series can run higher than the IDE series in organizations with terminal-heavy habits. GitHub publishes no magnitude for that gap, so measure it on your own data if you plan to quote it: reconcile the two series week by week and report the difference as an observation about your organization, not as a product constant.

## Team-Level Reporting: Building It Yourself

The usage metrics APIs do not publish a single pre-aggregated team report. Team totals are constructed by joining the daily user-teams report, which lists each user's team memberships for a day, with the daily per-user usage report, then aggregating by `team_id` ([team-level metrics](https://docs.github.com/en/copilot/reference/copilot-usage-metrics/team-level-metrics)).

### The Join Approach

The documented recipe is three steps:

1. Download the **per-user usage report** for a day — one row per (user, day, organization) with activity totals.
2. Download the **user-teams report** for the same day — one row per (user, team) membership.
3. Inner-join on `user_id`, `day` and `organization_id`, then group by `team_id` and `slug`.

The endpoints are:

```
GET /enterprises/{enterprise}/copilot/metrics/reports/user-teams-1-day?day=DAY
GET /orgs/{org}/copilot/metrics/reports/user-teams-1-day?day=DAY
```

The snippet below follows the schema and aggregation shown in the documentation. It is a short illustrative example, not a maintained package; add your own download and auth handling, which the docs describe separately.

```python
import pandas as pd

def build_team_report(date: str) -> pd.DataFrame:
    """One day of organization team metrics, via the documented join."""
    # NDJSON downloaded from the two daily report links.
    teams = pd.read_json(f"organization_user_teams_1_day-{date}.ndjson", lines=True)
    users = pd.read_json(f"organization_users_1_day-{date}.ndjson", lines=True)

    # One row per membership; one row per user-day-org. Join on the shared keys.
    joined = teams.merge(
        users,
        on=["user_id", "day", "organization_id"],
        how="inner",
    )

    return (
        joined.groupby(["team_id", "slug"], as_index=False)
        .agg(
            active_users=("user_id", "nunique"),
            code_acceptance_activity_count=("code_acceptance_activity_count", "sum"),
            loc_added_sum=("loc_added_sum", "sum"),
        )
        .sort_values("team_id")
    )
```

Two details of the schema are easy to get wrong. The user-teams file is already one row per membership — there is no `teams` array to explode — and the per-user report carries aggregate counters such as `user_initiated_interaction_count`, `code_acceptance_activity_count`, `loc_added_sum` and the `used_*` booleans, not precomputed per-feature acceptance rates. `active_users` in the output is a `COUNT(DISTINCT user_id)` you compute, not a field you read.

### Critical Gotchas

**Teams with fewer than 5 seated Copilot users are excluded** from the user-teams report. A three-person SRE squad will not appear in that day's membership file, even when its members are active, so its activity shows up in the per-user report and in no team aggregate. This is a documented privacy threshold, not a data bug.

**Users on multiple teams contribute to each team's totals.** Alice on both Frontend and API counts in both. Summing team rows double-counts her, and no team-level distinct count can also sum to the organization total — pick one of the two and say which.

**Team membership changes over time.** The user-teams report reflects a single day. Joining 28 days of activity against a single-day membership snapshot attributes all of it to whichever teams the user belonged to on the join day. Join each day's activity with that day's memberships, then aggregate the window.

For a broader look at setting up Copilot across your organization, see the [GitHub Copilot Enterprise Guide](/posts/github-copilot-enterprise-guide-2026/).

## Practical Recommendations

If you are building a reporting layer on top of these metrics, five habits cover most of the failure modes:

**1. Document your data sources.** In every report, note whether a number comes from client-side telemetry, server-side telemetry or a mix. "Active users" and "users with LoC data" are different populations, and a dashboard that silently swaps one for the other is worse than no dashboard.

**2. Reconcile enterprise against org on a schedule.** Pull the enterprise-level report and the sum of your org-level reports for the same window. The difference is the cross-org deduplication effect; if it grows, users are joining more orgs, which is worth knowing on its own.

**3. Track agent adoption separately.** Agent edits do not enter acceptance rate, so give them their own panel and watch the ratio of agent edits to inline completions. A rising ratio changes how the traditional metrics should be read.

For more on how agentic workflows change the metrics picture, see the [Agentic Code Review guide](/posts/github-copilot-agentic-code-review-2026/).

**4. Build around the two-day window, not against it.** Schedule pulls for data that is already complete, and make "not yet available" a first-class state in your pipeline instead of an error.

**5. Cross-reference with DORA metrics.** The ROI story is not in Copilot's dashboard; it is in deployment frequency, lead time and change failure rate. Overlay adoption on those, and treat teams that ship faster with stable failure rates as the success stories. The [general usage metrics guide](/posts/github-copilot-usage-metrics-guide-2026/) covers the metric categories in more detail.

## The Bottom Line

Copilot's usage metrics are detailed and well documented, but they are not turnkey. The dual telemetry paths, the org attribution model, the per-feature IDE minimums and the absence of a pre-aggregated team report all mean you have to understand the data before you can defend a number built on it.

Use the enterprise endpoints for top-line figures, respect the two-full-UTC-day window, separate users with measurable activity from users merely counted active, check version coverage before trusting LoC totals, and build team reports through the documented daily join. Do that, and the dashboard stops being a source of arguments and starts being evidence.
