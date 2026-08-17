---
title: "Trending Radar 2026: Build a Self-Updating Weekly Radar of Trending GitHub Repos"
date: 2026-08-17T10:02:42+00:00
tags:
  - github
  - trending
  - automation
  - github-actions
  - developer-tools
  - open-source
description: "Build a self-updating weekly radar of trending GitHub repos using the trending page or search API, scheduled with GitHub Actions."
draft: false
cover:
  image: "/images/trending-radar-2026-self-updating-weekly-radar-of-trending-github-repos.png"
  alt: "Trending Radar 2026: Self-Updating Weekly Radar of Trending GitHub Repos"
  relative: false
schema: "schema-trending-radar-2026-self-updating-weekly-radar-of-trending-github-repos"
---

A self-updating weekly radar of trending GitHub repos is a scheduled pipeline that scrapes `github.com/trending` or the GitHub search API, deduplicates and ranks the results, and emits a markdown digest to your repo or blog with zero manual effort. In 2026, when AI tooling can add 100,000+ stars in a week, a manual weekly roundup is no longer fast enough. This guide shows you how to build one with GitHub Actions.

## Why You Need a Self-Updating GitHub Trending Radar in 2026

The pace of open-source growth has changed the game. A single repository can go from zero to 144,000+ stars within a week of creation, as seen with `deepseek-ai/deepseek-harness` in August 2026. By the time a human curates a weekly list by hand, the most important repos have already moved on. A self-updating radar captures the signal while it is still fresh.

There is also proven demand for automated trending tracking. The open-source `github-trending-repos` project has roughly 2,993 stars, which is strong evidence that developers want a programmatic way to watch what is rising on GitHub. The manual alternative — a community post listing weekly trending repositories — works, but it depends on someone remembering to do it every week.

A self-updating radar solves three concrete problems:

- **Freshness.** It runs on a schedule, so the data is always current.
- **Consistency.** It never forgets a week, unlike a human-curated digest.
- **Scale.** It can track dozens of languages and date ranges at once, which no manual process can match.

The core idea is simple: treat trending GitHub repos as a data feed, not a manual chore. Once you have that mental model, the rest is engineering.

## The Two Data Sources: github.com/trending vs. the GitHub Search API

Before you build anything, you need to choose your data source. There are two main options, and they have very different trade-offs.

| Data source | Pros | Cons |
|-------------|------|------|
| `github.com/trending` (scraped) | Canonical, human-curated ranking; filterable by language and date range | No official API; HTML scraping is fragile; weekly/monthly lists have known reliability gaps |
| GitHub search API (`created:>date&sort=stars`) | Official, stable JSON; no HTML parsing; supports complex queries | Rate limits apply; requires a token for higher limits; ranking is by stars, not GitHub's own trending algorithm |

The official trending page at `github.com/trending` is the canonical source for daily and weekly trending repositories. It is filterable by language and date range, which makes it attractive. However, it has no official API, so you must scrape HTML. That is fragile: GitHub can change the markup at any time and break your parser.

The GitHub search API is the more robust choice for automation. You can query for repositories created after a certain date and sort by stars, for example `created:>2026-08-10&sort=stars`. This returns clean JSON that is easy to parse and rank. The trade-off is rate limiting — unauthenticated requests are heavily throttled, so you will want a token.

For a production radar, many builders use both: the search API as the primary source and the trending page as a cross-check. That gives you the stability of JSON with the canonical ranking of the official page.

## Scraping the Official Trending Page (and Its Reliability Gaps)

If you decide to scrape `github.com/trending`, you need to understand its reliability problems. There are known gaps where the weekly and monthly lists have been reported empty for days at a time. This has been documented repeatedly on Hacker News, and it is a major reason developers build self-hosted radar solutions instead of relying on the page directly.

The scraping approach works like this:

1. Fetch `https://github.com/trending?since=weekly` (optionally with a `?l=python` language filter).
2. Parse the HTML to extract repository names, star counts, and descriptions.
3. Store the results in a structured format.

The fragility is the main risk. GitHub's HTML is not a stable API, and a single class-name change can silently break your pipeline. To mitigate this, you should:

- Pin your parser to a specific HTML structure and test it after every GitHub frontend change.
- Add a fallback to the search API if the trending page returns empty or malformed data.
- Log failures loudly so you know when the radar has gone quiet.

Because of these gaps, the trending page is best treated as a secondary or cross-check source, not your only source.

## Building the Radar with the GitHub Search API (created:>date&sort=stars)

The GitHub search API is the most reliable foundation for a self-updating radar. The key query pattern is:

```
https://api.github.com/search/repositories?q=created:>2026-08-10&sort=stars&order=desc
```

This returns repositories created after a given date, sorted by star count. It is a clean, official JSON endpoint, and it is exactly what you need to surface newly-created repos that are rising fast.

A minimal Python implementation looks like this:

```python
import os
import requests
from datetime import datetime, timedelta

def fetch_new_repos(days=7, token=None):
    since = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%d")
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    url = f"https://api.github.com/search/repositories"
    params = {"q": f"created:>{since}", "sort": "stars", "order": "desc", "per_page": 50}
    resp = requests.get(url, headers=headers, params=params)
    resp.raise_for_status()
    return resp.json()["items"]
```

The search API has rate limits, so you should authenticate with a token. Unauthenticated requests are limited to 10 search requests per minute, while authenticated requests get 30 per minute. For a weekly radar that runs once, this is more than enough.

One important nuance: sorting by stars surfaces all-time star counts, not star *growth*. A repo created this week with 5,000 stars will rank below an older repo with 50,000 stars. To surface genuinely rising repos, you need star-delta tracking, which we cover below.

## Scheduling the Radar with GitHub Actions for Zero-Touch Updates

The whole point of a self-updating radar is that it runs without you. GitHub Actions is the natural home for this because it is free for public repositories and has built-in cron scheduling.

A scheduled workflow looks like this:

```yaml
name: Trending Radar
on:
  schedule:
    - cron: "0 6 * * 1"   # every Monday at 06:00 UTC
  workflow_dispatch: {}    # allow manual runs

jobs:
  radar:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install requests
      - run: python radar.py
        env:
          GH_TOKEN: ${{ secrets.GH_TOKEN }}
      - name: Commit digest
        run: |
          git config user.name "radar-bot"
          git config user.email "radar-bot@users.noreply.github.com"
          git add digest.md
          git commit -m "Update weekly trending digest" || echo "No changes"
          git push
```

The `workflow_dispatch` trigger is important. It lets you run the radar manually when you want to test it or catch up after a missed run. The `GH_TOKEN` secret should be a fine-grained personal access token with read access to public repositories.

GitHub Actions has a known limitation: scheduled workflows can be delayed or skipped if the repository is inactive for 60 days. For a public repo that updates weekly, this is rarely a problem, but it is worth knowing. If your radar goes quiet, check the Actions tab for skipped runs.

## Deduplication, Ranking, and Star-Delta Tracking

Raw search results are noisy. A repo can appear in multiple weeks, and all-time star counts can hide the repos that are actually rising. You need three processing steps:

**Deduplication.** Track which repos you have already reported. Store a set of repository IDs (or full names) from previous runs, and skip anything you have already covered. This keeps your digest fresh instead of repeating the same repos every week.

**Ranking.** Decide what "trending" means to you. The simplest ranking is by star count, but a better one is by star *growth* over the tracking window. A repo that gained 2,000 stars this week is more interesting than one that gained 200, even if the latter has more total stars.

**Star-delta tracking.** This is the key to surfacing genuinely rising repos. Store the star count from the previous run, then compute the delta:

```python
delta = current_stars - previous_stars
```

Sort by delta instead of by absolute stars, and you will surface the repos that are actually accelerating. This is the difference between a "most popular" list and a true "trending radar."

A simple state file (JSON or SQLite) stored in your repo is enough to track deltas across runs. Each entry records the repo name, the previous star count, and the date it was first seen.

## Emitting a Weekly Markdown Digest to Your Repo or Blog

Once you have ranked results, you need to emit them in a useful format. A markdown digest is the most flexible output because it can be committed to a repo, rendered on a blog, or fed into a newsletter.

A digest entry looks like this:

```markdown
## Week of 2026-08-17

### 1. deepseek-ai/deepseek-harness
- **Stars:** 144,000+ (added ~120,000 this week)
- **Language:** Python
- **Why it matters:** AI agent tooling continues to dominate trending charts.

### 2. ...
```

The digest should include the star delta, the language, and a one-line reason the repo matters. If you are publishing to a blog, you can generate the markdown and commit it to your content directory, then let your static site generator handle the rendering.

For a newsletter-style format, you can pipe the same markdown into an email template. The key is that the pipeline produces structured data first, and the digest is just one view of it.

## Filtering by Language and Date Range

Not everyone wants a general trending list. You can filter the radar by language and date range to make it more useful for a specific audience.

For the search API, language filtering is built into the query:

```
q=created:>2026-08-10+language:python&sort=stars
```

For the trending page, you append a language parameter:

```
https://github.com/trending/python?since=weekly
```

You can run the radar once per language and merge the results, or let the user pick a language at runtime. A common pattern is to define a list of languages in a config file and loop over them:

```python
LANGUAGES = ["python", "typescript", "rust", "go", "ai"]
for lang in LANGUAGES:
    results = fetch_new_repos(lang=lang)
    digest.extend(results)
```

Date range filtering lets you control the window. A 7-day window is standard for a weekly radar, but you can use 30 days for a monthly digest or 1 day for a daily one. The search API's `created:>` filter makes this trivial.

## Separating AI/Agent Hype from Durable Engineering Value

In 2026, the biggest challenge is not finding trending repos — it is separating AI/agent hype from durable engineering value. AI tooling dominates the trending charts, and a naive radar will surface mostly AI repos every week.

To cut through the noise, add a curation layer to your radar:

- **Check for real usage.** A repo with high stars but few forks, few issues, and little recent commit activity may be hype. Look at the ratio of stars to forks and the commit cadence.
- **Track longevity.** A repo that stays on the radar for multiple weeks is more likely to have durable value than a one-week spike.
- **Apply a category filter.** If your audience is not AI-focused, exclude AI/agent repos or put them in a separate section.
- **Add a human review step.** The best radars combine automation with a light human pass. Automation collects the candidates; a human writes the "why it matters" line.

The goal is a radar that surfaces genuinely useful engineering, not just whatever is loudest this week. Star count is a popularity signal, not a quality signal.

## Putting It All Together: A Complete Self-Updating Radar Pipeline

Here is the full pipeline, end to end:

1. **Schedule.** A GitHub Actions cron job fires every Monday at 06:00 UTC.
2. **Fetch.** The radar queries the GitHub search API for repos created in the last 7 days, sorted by stars. Optionally, it cross-checks the trending page.
3. **Process.** It deduplicates against previous runs, computes star deltas, and ranks by growth.
4. **Curate.** It applies language filters and a hype-detection heuristic, then writes a markdown digest.
5. **Publish.** It commits the digest to the repo (or blog content directory) and pushes.
6. **Repeat.** The state file persists, so next week's run knows what it already covered.

The total code is a few hundred lines of Python plus a small YAML workflow. You can have a working radar in an afternoon, and it will run forever with zero manual effort.

The GitHub search API is the most reliable foundation, the trending page is a useful cross-check, and star-delta tracking is what makes the radar genuinely useful. Add GitHub Actions for scheduling, and you have a self-updating weekly radar of trending GitHub repos that keeps you ahead of the curve in 2026.

## FAQ

### What is a GitHub trending radar?
A GitHub trending radar is an automated pipeline that periodically collects trending GitHub repositories, ranks them, and produces a digest. It runs on a schedule (usually weekly) so you always have a fresh view of what is rising on GitHub without checking manually.

### What is the best data source for tracking trending GitHub repos?
The GitHub search API is the most reliable because it returns clean JSON and supports queries like `created:>date&sort=stars`. The official `github.com/trending` page is canonical but requires HTML scraping and has known reliability gaps where weekly and monthly lists can be empty.

### How do I schedule a self-updating radar?
Use a GitHub Actions scheduled workflow with a cron expression, for example `cron: "0 6 * * 1"` for every Monday at 06:00 UTC. Add a `workflow_dispatch` trigger so you can also run it manually. Store your GitHub token as a repository secret.

### How do I surface genuinely rising repos instead of just the most starred?
Track star deltas. Store the star count from the previous run, compute the difference on the next run, and sort by that delta rather than by absolute stars. This surfaces repos that are accelerating, not just the all-time most popular.

### How do I avoid AI/agent hype dominating my radar?
Add a curation layer: check the ratio of stars to forks, look at commit cadence and recent activity, track whether a repo stays on the radar for multiple weeks, and apply a category filter. Combine automation with a light human review pass to write the "why it matters" line.
