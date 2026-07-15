# Pipeline Health Check
Date: 2026-07-09 23:00 UTC

## Warnings
- Missing cover image: warp-terminal-open-source-shift.png (expected at /home/ubuntu/blog/static/images/warp-terminal-open-source-shift.png)

## Full Log
```
[2026-07-09 23:00:01 UTC] [INFO] ============================================================
[2026-07-09 23:00:01 UTC] [INFO] Pipeline Health Check starting 
[2026-07-09 23:00:01 UTC] [INFO] Fetching Paperclip data...
[2026-07-09 23:00:01 UTC] [INFO] Pipeline: done=29 backlog=0 todo=0 in_progress=0 cancelled=471
[2026-07-09 23:00:01 UTC] [INFO] 
[2026-07-09 23:00:01 UTC] [INFO] Check 1: Stuck subtask issues (>6h, no active run)
[2026-07-09 23:00:01 UTC] [INFO] Stuck subtasks cancelled: 0
[2026-07-09 23:00:01 UTC] [INFO] 
[2026-07-09 23:00:01 UTC] [INFO] Check 2: Zombie subtask issues (null executionRunId >30 min)
[2026-07-09 23:00:01 UTC] [INFO] Zombie subtasks cancelled: 0
[2026-07-09 23:00:01 UTC] [INFO] 
[2026-07-09 23:00:01 UTC] [INFO] Check 3: Topic queue watermark
[2026-07-09 23:00:01 UTC] [INFO] Queued topics: 21 (watermark: 10)
[2026-07-09 23:00:01 UTC] [INFO] Topic queue healthy, no action needed
[2026-07-09 23:00:01 UTC] [INFO] 
[2026-07-09 23:00:01 UTC] [INFO] Check 4: Missing cover images for published posts
[2026-07-09 23:00:01 UTC] [WARN] Missing cover image: warp-terminal-open-source-shift.png (expected at /home/ubuntu/blog/static/images/warp-terminal-open-source-shift.png)
[2026-07-09 23:00:01 UTC] [INFO] Missing cover images: 1
[2026-07-09 23:00:01 UTC] [INFO] 
[2026-07-09 23:00:01 UTC] [INFO] Check 5: Missing schema files
[2026-07-09 23:00:01 UTC] [INFO] All published posts have schema files
[2026-07-09 23:00:01 UTC] [INFO] 
[2026-07-09 23:00:01 UTC] [INFO] Check 6: Issues assigned to disabled agents (SEO/Thumbnail)
[2026-07-09 23:00:01 UTC] [INFO] No disabled agents found in agent list
[2026-07-09 23:00:01 UTC] [INFO] Disabled-agent issues cancelled: 0
[2026-07-09 23:00:01 UTC] [INFO] 
[2026-07-09 23:00:01 UTC] [INFO] Check 6b: Blocked issue auto-recovery
[2026-07-09 23:00:01 UTC] [INFO] No blocked issues found
[2026-07-09 23:00:01 UTC] [INFO] 
[2026-07-09 23:00:01 UTC] [INFO] Check 7: Slug consistency audit (Paperclip slug vs actual post slug)
[2026-07-09 23:00:01 UTC] [INFO] Slug mismatches found: 0, auto-fixed: 0
[2026-07-09 23:00:01 UTC] [INFO] 
[2026-07-09 23:00:01 UTC] [INFO] Check 8: Orphan agent-browser Chrome roots (> 15 min)
[2026-07-09 23:00:01 UTC] [INFO] No stale orphan agent-browser Chrome roots found
[2026-07-09 23:00:01 UTC] [INFO] 
[2026-07-09 23:00:01 UTC] [INFO] ============================================================
[2026-07-09 23:00:01 UTC] [INFO] Summary: 0 actions taken
[2026-07-09 23:00:01 UTC] [INFO]   Stuck subtasks cancelled: 0
[2026-07-09 23:00:01 UTC] [INFO]   Zombie subtasks cancelled: 0
[2026-07-09 23:00:01 UTC] [INFO]   Strategist wakes: 0
[2026-07-09 23:00:01 UTC] [INFO]   Disabled-agent issues cancelled: 0
[2026-07-09 23:00:01 UTC] [INFO]   Blocked issues recovered/re-queued: 0
[2026-07-09 23:00:01 UTC] [INFO]   Slug mismatches auto-fixed: 0
[2026-07-09 23:00:01 UTC] [INFO]   Orphan browser roots terminated: 0
[2026-07-09 23:00:01 UTC] [INFO]   Missing cover images (warnings): 1
[2026-07-09 23:00:01 UTC] [INFO]   Missing schema files (warnings): 0
[2026-07-09 23:00:01 UTC] [INFO] Pipeline Health Check complete
```