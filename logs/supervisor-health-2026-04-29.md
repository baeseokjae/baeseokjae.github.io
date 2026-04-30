# Pipeline Health Check
Date: 2026-04-29 21:01 UTC

## Actions Taken
- RECOVERED: ROC-1971 → done (all files present)

## Warnings
- Missing cover image: ai-coding-stack-2026.png (expected at /home/ubuntu/blog/static/images/ai-coding-stack-2026.png)
- Missing cover image: developer-ai-tool-survey-2026.png (expected at /home/ubuntu/blog/static/images/developer-ai-tool-survey-2026.png)
- Missing cover image: gemini-cli-vs-claude-code-vs-opencode-2026.png (expected at /home/ubuntu/blog/static/images/gemini-cli-vs-claude-code-vs-opencode-2026.png)
- Missing cover image: ai-documentation-generators-2026.png (expected at /home/ubuntu/blog/static/images/ai-documentation-generators-2026.png)
- Missing cover image: langsmith-vs-langfuse-vs-helicone-2026.png (expected at /home/ubuntu/blog/static/images/langsmith-vs-langfuse-vs-helicone-2026.png)
- Missing cover image: rag-pipeline-best-practices-2026.png (expected at /home/ubuntu/blog/static/images/rag-pipeline-best-practices-2026.png)
- Missing cover image: github-models-api-guide-2026.png (expected at /home/ubuntu/blog/static/images/github-models-api-guide-2026.png)
- Missing cover image: cursor-advanced-tips-2026.png (expected at /home/ubuntu/blog/static/images/cursor-advanced-tips-2026.png)
- Missing cover image: ai-tools-python-developers-2026.png (expected at /home/ubuntu/blog/static/images/ai-tools-python-developers-2026.png)
- Missing cover image: langfuse-guide-2026.png (expected at /home/ubuntu/blog/static/images/langfuse-guide-2026.png)
- Missing cover image: openai-batch-api-guide-2026.png (expected at /home/ubuntu/blog/static/images/openai-batch-api-guide-2026.png)
- Missing cover image: azure-openai-assistants-foundry-migration-2026.png (expected at /home/ubuntu/blog/static/images/azure-openai-assistants-foundry-migration-2026.png)
- Missing schema: schema-ai-coding-stack-2026.html
- Missing schema: schema-developer-ai-tool-survey-2026.html
- Missing schema: schema-gemini-cli-vs-claude-code-vs-opencode-2026.html
- Missing schema: schema-ai-documentation-generators-2026.html
- Missing schema: schema-langsmith-vs-langfuse-vs-helicone-2026.html
- Missing schema: schema-rag-pipeline-best-practices-2026.html
- Missing schema: schema-github-models-api-guide-2026.html
- Missing schema: schema-cursor-advanced-tips-2026.html
- Missing schema: schema-ai-tools-python-developers-2026.html
- Missing schema: schema-langfuse-guide-2026.html
- Missing schema: schema-openai-batch-api-guide-2026.html
- Missing schema: schema-azure-openai-assistants-foundry-migration-2026.html

## Full Log
```
[2026-04-29 21:01:24 UTC] [INFO] ============================================================
[2026-04-29 21:01:24 UTC] [INFO] Pipeline Health Check starting 
[2026-04-29 21:01:24 UTC] [INFO] Fetching Paperclip data...
[2026-04-29 21:01:24 UTC] [INFO] Pipeline: done=1384 backlog=29 todo=18 in_progress=3 cancelled=493
[2026-04-29 21:01:24 UTC] [INFO] 
[2026-04-29 21:01:24 UTC] [INFO] Check 1: Stuck subtask issues (>6h, no active run)
[2026-04-29 21:01:24 UTC] [INFO] Stuck subtasks cancelled: 0
[2026-04-29 21:01:24 UTC] [INFO] 
[2026-04-29 21:01:24 UTC] [INFO] Check 2: Zombie subtask issues (null executionRunId >30 min)
[2026-04-29 21:01:24 UTC] [INFO] Zombie subtasks cancelled: 0
[2026-04-29 21:01:24 UTC] [INFO] 
[2026-04-29 21:01:24 UTC] [INFO] Check 3: Topic queue watermark
[2026-04-29 21:01:24 UTC] [INFO] Queued topics: 919 (watermark: 10)
[2026-04-29 21:01:24 UTC] [INFO] Topic queue healthy, no action needed
[2026-04-29 21:01:24 UTC] [INFO] 
[2026-04-29 21:01:24 UTC] [INFO] Check 4: Missing cover images for published posts
[2026-04-29 21:01:24 UTC] [WARN] Missing cover image: ai-coding-stack-2026.png (expected at /home/ubuntu/blog/static/images/ai-coding-stack-2026.png)
[2026-04-29 21:01:24 UTC] [WARN] Missing cover image: developer-ai-tool-survey-2026.png (expected at /home/ubuntu/blog/static/images/developer-ai-tool-survey-2026.png)
[2026-04-29 21:01:24 UTC] [WARN] Missing cover image: gemini-cli-vs-claude-code-vs-opencode-2026.png (expected at /home/ubuntu/blog/static/images/gemini-cli-vs-claude-code-vs-opencode-2026.png)
[2026-04-29 21:01:24 UTC] [WARN] Missing cover image: ai-documentation-generators-2026.png (expected at /home/ubuntu/blog/static/images/ai-documentation-generators-2026.png)
[2026-04-29 21:01:24 UTC] [WARN] Missing cover image: langsmith-vs-langfuse-vs-helicone-2026.png (expected at /home/ubuntu/blog/static/images/langsmith-vs-langfuse-vs-helicone-2026.png)
[2026-04-29 21:01:24 UTC] [WARN] Missing cover image: rag-pipeline-best-practices-2026.png (expected at /home/ubuntu/blog/static/images/rag-pipeline-best-practices-2026.png)
[2026-04-29 21:01:24 UTC] [WARN] Missing cover image: github-models-api-guide-2026.png (expected at /home/ubuntu/blog/static/images/github-models-api-guide-2026.png)
[2026-04-29 21:01:24 UTC] [WARN] Missing cover image: cursor-advanced-tips-2026.png (expected at /home/ubuntu/blog/static/images/cursor-advanced-tips-2026.png)
[2026-04-29 21:01:24 UTC] [WARN] Missing cover image: ai-tools-python-developers-2026.png (expected at /home/ubuntu/blog/static/images/ai-tools-python-developers-2026.png)
[2026-04-29 21:01:24 UTC] [WARN] Missing cover image: langfuse-guide-2026.png (expected at /home/ubuntu/blog/static/images/langfuse-guide-2026.png)
[2026-04-29 21:01:24 UTC] [WARN] Missing cover image: openai-batch-api-guide-2026.png (expected at /home/ubuntu/blog/static/images/openai-batch-api-guide-2026.png)
[2026-04-29 21:01:24 UTC] [WARN] Missing cover image: azure-openai-assistants-foundry-migration-2026.png (expected at /home/ubuntu/blog/static/images/azure-openai-assistants-foundry-migration-2026.png)
[2026-04-29 21:01:24 UTC] [INFO] Missing cover images: 12
[2026-04-29 21:01:24 UTC] [INFO] 
[2026-04-29 21:01:24 UTC] [INFO] Check 5: Missing schema files
[2026-04-29 21:01:24 UTC] [WARN] Missing schema: schema-ai-coding-stack-2026.html
[2026-04-29 21:01:24 UTC] [WARN] Missing schema: schema-developer-ai-tool-survey-2026.html
[2026-04-29 21:01:24 UTC] [WARN] Missing schema: schema-gemini-cli-vs-claude-code-vs-opencode-2026.html
[2026-04-29 21:01:24 UTC] [WARN] Missing schema: schema-ai-documentation-generators-2026.html
[2026-04-29 21:01:24 UTC] [WARN] Missing schema: schema-langsmith-vs-langfuse-vs-helicone-2026.html
[2026-04-29 21:01:24 UTC] [WARN] Missing schema: schema-rag-pipeline-best-practices-2026.html
[2026-04-29 21:01:24 UTC] [WARN] Missing schema: schema-github-models-api-guide-2026.html
[2026-04-29 21:01:24 UTC] [WARN] Missing schema: schema-cursor-advanced-tips-2026.html
[2026-04-29 21:01:24 UTC] [WARN] Missing schema: schema-ai-tools-python-developers-2026.html
[2026-04-29 21:01:24 UTC] [WARN] Missing schema: schema-langfuse-guide-2026.html
[2026-04-29 21:01:24 UTC] [WARN] Missing schema: schema-openai-batch-api-guide-2026.html
[2026-04-29 21:01:24 UTC] [WARN] Missing schema: schema-azure-openai-assistants-foundry-migration-2026.html
[2026-04-29 21:01:24 UTC] [INFO] Missing schema files: 12
[2026-04-29 21:01:24 UTC] [INFO] 
[2026-04-29 21:01:24 UTC] [INFO] Check 6: Issues assigned to disabled agents (SEO/Thumbnail)
[2026-04-29 21:01:24 UTC] [INFO] Disabled-agent issues cancelled: 0
[2026-04-29 21:01:24 UTC] [INFO] 
[2026-04-29 21:01:24 UTC] [INFO] Check 6b: Blocked issue auto-recovery
[2026-04-29 21:01:24 UTC] [INFO] Found 3 blocked issues to evaluate
[2026-04-29 21:01:24 UTC] [INFO] BLOCKED: ROC-1724 — no slug found, likely non-blog issue, skipping
[2026-04-29 21:01:24 UTC] [INFO] BLOCKED ROC-1971: slug=devstral-2-review-2026 post=True schema=True cover=True
[2026-04-29 21:01:24 UTC] [ACTION] RECOVERED: ROC-1971 → done (all files present)
[2026-04-29 21:01:24 UTC] [INFO] BLOCKED: ROC-1842 — no slug found, likely non-blog issue, skipping
[2026-04-29 21:01:24 UTC] [INFO] Blocked issues recovered/re-queued: 1
[2026-04-29 21:01:24 UTC] [INFO] 
[2026-04-29 21:01:24 UTC] [INFO] ============================================================
[2026-04-29 21:01:24 UTC] [INFO] Summary: 1 actions taken
[2026-04-29 21:01:24 UTC] [INFO]   Stuck subtasks cancelled: 0
[2026-04-29 21:01:24 UTC] [INFO]   Zombie subtasks cancelled: 0
[2026-04-29 21:01:24 UTC] [INFO]   Strategist wakes: 0
[2026-04-29 21:01:24 UTC] [INFO]   Disabled-agent issues cancelled: 0
[2026-04-29 21:01:24 UTC] [INFO]   Blocked issues recovered/re-queued: 1
[2026-04-29 21:01:24 UTC] [INFO]   Missing cover images (warnings): 12
[2026-04-29 21:01:24 UTC] [INFO]   Missing schema files (warnings): 12
[2026-04-29 21:01:24 UTC] [INFO] Pipeline Health Check complete
```