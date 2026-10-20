---
cover:
  image: /images/og-default.png
  alt: RockB editorial guides
  relative: false
date: 2026-05-03 18:04:28+00:00
description: Evaluate Bugbot using confirmed findings, missed defects and cost per accepted fix; distinguish supplier resolution claims from independent results.
draft: false
schema: schema-cursor-bugbot-review-2026
tags:
- cursor
- code-review
- ai-security
- bugbot
- pull-requests
title: 'Cursor Bugbot Review: Current Billing, Review Quality and a Measurable Pilot'
lastmod: '2026-10-20T08:06:38.069366+00:00'
---

An AI reviewer is useful when its comments lead to correct fixes without consuming more attention than they save. Counting comments is not enough: you need to know which findings are valid, what was missed and how much review effort remained.

This is a documentation review and a pilot design. It does not claim an independently measured Bugbot detection rate. The previous version mixed vendor statistics with unsupported vulnerability and adoption claims.

## What is documented and what the statistics mean

[Cursor's Bugbot documentation](https://cursor.com/docs/bugbot) covers repository setup, manual review triggers and rules such as `.cursor/BUGBOT.md`. Configure the intended repositories and permissions before assuming every pull request will be reviewed.

Cursor's [billing-change announcement](https://cursor.com/blog/may-2026-bugbot-changes) says Bugbot moved from seat-based subscriptions to usage-based billing, with existing plans transitioning on the renewal described there. The current documentation should be checked alongside the actual account plan; an older annual contract may differ.

That announcement reports an **80% resolution rate** for identified bugs by merge time. This is a supplier-reported measure. It is not the percentage of all defects Bugbot discovers, and it is not an independent estimate of correctness. The denominator matters: missed bugs do not enter a metric that starts with already identified findings.

## Design a pilot with an answerable question

Choose a repository and a defined change set. Include representative routine changes and a separate controlled set of known defects. Keep the two sets distinct: an artificial seeded bug may be easier to recognize than an accidental production defect.

Use the [review scorecard](/research/content-quality-batch2-2026-10/review-scorecard.csv). For every finding, record the affected commit, whether the issue is reproducible, its impact, whether a fix was accepted and how long review took. Have a human verify the finding before assigning credit.

For the controlled set, retain an answer key that the reviewer does not receive. Count missed known defects. For ordinary pull requests, do not report recall unless you have a credible way to identify the total defect population.

Run the same checks on the existing review process. Otherwise, a Bugbot result cannot show whether the tool added value beyond tests, static analysis and human review already in place.

## Measure useful outcomes and cost

Use separate measures:

| Measure | Definition |
|---|---|
| Finding precision | Confirmed valid findings / reviewed findings |
| Known-defect recall | Detected seeded defects / all seeded defects |
| Accepted fixes | Changes a reviewer verified and kept |
| Review burden | Time checking findings, including false positives |
| Cost per accepted fix | Billed pilot spend / accepted fixes |

For an illustration, if a pilot costs an assumed $24 and produces six accepted fixes, the billed cost per accepted fix is $4. That excludes reviewer time. If there are no accepted fixes, report the spend and zero fixes rather than inventing a finite ratio.

Compare review effort and outcomes at the same configuration. A higher effort setting can change both billed use and findings. Do not extrapolate a supplier's average cost to every repository or PR size.

## Rules and fix acceptance

Write rules that identify concrete repository requirements: authorization must be checked server-side, migrations need a rollback plan, and background jobs need idempotency. Avoid generic instructions to “find all bugs,” which provide no project-specific evidence.

Treat an offered fix as another patch. Inspect the changed behavior and require the relevant tests. A comment resolved in the hosting platform can mean it was dismissed or moved; the resolution flag alone does not establish a successful repair.

Keep secrets and private customer records out of rule files. Review repository access, data handling and team policy separately from detection quality.

## When to expand the pilot

Expand when confirmed findings justify the combined bill and review burden, and when failures have a clear owner. Keep existing tests and human approval for consequential changes. A quiet review does not mean the PR is free of defects.

Re-evaluate after major configuration or model changes. Save the reviewed commit and configuration with the result so future comparisons are meaningful.

## Revision note

**Updated October 20, 2026.** Removed unsupported vulnerability/adoption claims and an obsolete flat-price recommendation. Attributed the supplier's resolution metric correctly and added a pilot scorecard with explicit denominators.

## Primary sources

Checked October 20, 2026: [bugbot](https://cursor.com/docs/bugbot); [bugbot billing](https://cursor.com/blog/may-2026-bugbot-changes).
