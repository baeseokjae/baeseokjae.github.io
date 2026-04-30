# Pipeline Health Check
Date: 2026-04-27 21:01 UTC

## Full Log
```
[2026-04-27 21:01:04 UTC] [INFO] ============================================================
[2026-04-27 21:01:04 UTC] [INFO] Pipeline Health Check starting 
[2026-04-27 21:01:04 UTC] [INFO] Fetching Paperclip data...
[2026-04-27 21:01:04 UTC] [INFO] Pipeline: done=1279 backlog=18 todo=2 in_progress=3 cancelled=474
[2026-04-27 21:01:04 UTC] [INFO] 
[2026-04-27 21:01:04 UTC] [INFO] Check 1: Stuck subtask issues (>6h, no active run)
[2026-04-27 21:01:04 UTC] [INFO] Stuck subtasks cancelled: 0
[2026-04-27 21:01:04 UTC] [INFO] 
[2026-04-27 21:01:04 UTC] [INFO] Check 2: Zombie subtask issues (null executionRunId >30 min)
[2026-04-27 21:01:04 UTC] [INFO] Zombie subtasks cancelled: 0
[2026-04-27 21:01:04 UTC] [INFO] 
[2026-04-27 21:01:04 UTC] [INFO] Check 3: Topic queue watermark
[2026-04-27 21:01:04 UTC] [INFO] Queued topics: 922 (watermark: 10)
[2026-04-27 21:01:04 UTC] [INFO] Topic queue healthy, no action needed
[2026-04-27 21:01:04 UTC] [INFO] 
[2026-04-27 21:01:04 UTC] [INFO] Check 4: Missing cover images for published posts
[2026-04-27 21:01:04 UTC] [INFO] All published posts have cover images
[2026-04-27 21:01:04 UTC] [INFO] 
[2026-04-27 21:01:04 UTC] [INFO] Check 5: Missing schema files
[2026-04-27 21:01:04 UTC] [INFO] All published posts have schema files
[2026-04-27 21:01:04 UTC] [INFO] 
[2026-04-27 21:01:04 UTC] [INFO] Check 6: Issues assigned to disabled agents (SEO/Thumbnail)
[2026-04-27 21:01:04 UTC] [INFO] Disabled-agent issues cancelled: 0
[2026-04-27 21:01:04 UTC] [INFO] 
[2026-04-27 21:01:04 UTC] [INFO] Check 6b: Blocked issue auto-recovery
[2026-04-27 21:01:04 UTC] [INFO] Found 2 blocked issues to evaluate
[2026-04-27 21:01:04 UTC] [INFO] BLOCKED: ROC-1724 — no slug found, likely non-blog issue, skipping
[2026-04-27 21:01:04 UTC] [INFO] BLOCKED: ROC-1842 — no slug found, likely non-blog issue, skipping
[2026-04-27 21:01:04 UTC] [INFO] Blocked issues recovered/re-queued: 0
[2026-04-27 21:01:04 UTC] [INFO] 
[2026-04-27 21:01:04 UTC] [INFO] ============================================================
[2026-04-27 21:01:04 UTC] [INFO] Summary: 0 actions taken
[2026-04-27 21:01:04 UTC] [INFO]   Stuck subtasks cancelled: 0
[2026-04-27 21:01:04 UTC] [INFO]   Zombie subtasks cancelled: 0
[2026-04-27 21:01:04 UTC] [INFO]   Strategist wakes: 0
[2026-04-27 21:01:04 UTC] [INFO]   Disabled-agent issues cancelled: 0
[2026-04-27 21:01:04 UTC] [INFO]   Blocked issues recovered/re-queued: 0
[2026-04-27 21:01:04 UTC] [INFO]   Missing cover images (warnings): 0
[2026-04-27 21:01:04 UTC] [INFO]   Missing schema files (warnings): 0
[2026-04-27 21:01:04 UTC] [INFO] Pipeline Health Check complete
```