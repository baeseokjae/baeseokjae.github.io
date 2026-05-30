# Pipeline Health Check
Date: 2026-05-26 21:01 UTC

## Actions Taken
- RE-QUEUED: ROC-4269 → todo (missing: post schema cover)
- RE-QUEUED: ROC-4268 → todo (missing: post schema cover)
- RE-QUEUED: ROC-4270 → todo (missing: cover)

## Warnings
- Missing cover image: ai-coding-stack-2026.png (expected at /home/ubuntu/blog/static/images/ai-coding-stack-2026.png)
- Missing cover image: gemini-cli-vs-claude-code-vs-opencode-2026.png (expected at /home/ubuntu/blog/static/images/gemini-cli-vs-claude-code-vs-opencode-2026.png)
- Missing cover image: ai-documentation-generators-2026.png (expected at /home/ubuntu/blog/static/images/ai-documentation-generators-2026.png)
- Missing cover image: langsmith-vs-langfuse-vs-helicone-2026.png (expected at /home/ubuntu/blog/static/images/langsmith-vs-langfuse-vs-helicone-2026.png)
- Missing cover image: rag-pipeline-best-practices-2026.png (expected at /home/ubuntu/blog/static/images/rag-pipeline-best-practices-2026.png)
- Missing cover image: github-models-api-guide-2026.png (expected at /home/ubuntu/blog/static/images/github-models-api-guide-2026.png)
- Missing cover image: cursor-advanced-tips-2026.png (expected at /home/ubuntu/blog/static/images/cursor-advanced-tips-2026.png)
- Missing cover image: ai-tools-python-developers-2026.png (expected at /home/ubuntu/blog/static/images/ai-tools-python-developers-2026.png)
- Missing cover image: langfuse-guide-2026.png (expected at /home/ubuntu/blog/static/images/langfuse-guide-2026.png)
- Missing cover image: openai-batch-api-guide-2026.png (expected at /home/ubuntu/blog/static/images/openai-batch-api-guide-2026.png)
- Missing cover image: claude-opus-4-7-vs-4-6-comparison-2026.png (expected at /home/ubuntu/blog/static/images/claude-opus-4-7-vs-4-6-comparison-2026.png)
- Missing cover image: zeropath-review-2026.png (expected at /home/ubuntu/blog/static/images/zeropath-review-2026.png)
- Missing cover image: 1password-ai-agent-security-2026.png (expected at /home/ubuntu/blog/static/images/1password-ai-agent-security-2026.png)
- Missing cover image: azure-openai-assistants-foundry-migration-2026.png (expected at /home/ubuntu/blog/static/images/azure-openai-assistants-foundry-migration-2026.png)
- Missing cover image: ai-pr-review-time-optimization-2026.png (expected at /home/ubuntu/blog/static/images/ai-pr-review-time-optimization-2026.png)
- Missing cover image: ai-coding-acceleration-whiplash-2026.png (expected at /home/ubuntu/blog/static/images/ai-coding-acceleration-whiplash-2026.png)
- Missing cover image: claude-code-vulnerability-detection-guide-2026.png (expected at /home/ubuntu/blog/static/images/claude-code-vulnerability-detection-guide-2026.png)
- Missing cover image: github-trending-ai-projects-april-2026.png (expected at /home/ubuntu/blog/static/images/github-trending-ai-projects-april-2026.png)
- Missing schema: schema-ai-coding-stack-2026.html
- Missing schema: schema-gemini-cli-vs-claude-code-vs-opencode-2026.html
- Missing schema: schema-ai-documentation-generators-2026.html
- Missing schema: schema-langsmith-vs-langfuse-vs-helicone-2026.html
- Missing schema: schema-rag-pipeline-best-practices-2026.html
- Missing schema: schema-github-models-api-guide-2026.html
- Missing schema: schema-cursor-advanced-tips-2026.html
- Missing schema: schema-ai-tools-python-developers-2026.html
- Missing schema: schema-langfuse-guide-2026.html
- Missing schema: schema-openai-batch-api-guide-2026.html
- Missing schema: schema-claude-opus-4-7-vs-4-6-comparison-2026.html
- Missing schema: schema-zeropath-review-2026.html
- Missing schema: schema-1password-ai-agent-security-2026.html
- Missing schema: schema-azure-openai-assistants-foundry-migration-2026.html
- Missing schema: schema-ai-coding-acceleration-whiplash-2026.html
- Missing schema: schema-claude-code-vulnerability-detection-guide-2026.html

## Full Log
```
[2026-05-26 21:01:00 UTC] [INFO] ============================================================
[2026-05-26 21:01:00 UTC] [INFO] Pipeline Health Check starting 
[2026-05-26 21:01:00 UTC] [INFO] Fetching Paperclip data...
[2026-05-26 21:01:01 UTC] [INFO] Pipeline: done=2477 backlog=181 todo=245 in_progress=3 cancelled=1255
[2026-05-26 21:01:01 UTC] [INFO] 
[2026-05-26 21:01:01 UTC] [INFO] Check 1: Stuck subtask issues (>6h, no active run)
[2026-05-26 21:01:01 UTC] [INFO] Stuck subtasks cancelled: 0
[2026-05-26 21:01:01 UTC] [INFO] 
[2026-05-26 21:01:01 UTC] [INFO] Check 2: Zombie subtask issues (null executionRunId >30 min)
[2026-05-26 21:01:01 UTC] [INFO] Zombie subtasks cancelled: 0
[2026-05-26 21:01:01 UTC] [INFO] 
[2026-05-26 21:01:01 UTC] [INFO] Check 3: Topic queue watermark
[2026-05-26 21:01:01 UTC] [INFO] Queued topics: 2155 (watermark: 10)
[2026-05-26 21:01:01 UTC] [INFO] Topic queue healthy, no action needed
[2026-05-26 21:01:01 UTC] [INFO] 
[2026-05-26 21:01:01 UTC] [INFO] Check 4: Missing cover images for published posts
[2026-05-26 21:01:01 UTC] [WARN] Missing cover image: ai-coding-stack-2026.png (expected at /home/ubuntu/blog/static/images/ai-coding-stack-2026.png)
[2026-05-26 21:01:01 UTC] [WARN] Missing cover image: gemini-cli-vs-claude-code-vs-opencode-2026.png (expected at /home/ubuntu/blog/static/images/gemini-cli-vs-claude-code-vs-opencode-2026.png)
[2026-05-26 21:01:01 UTC] [WARN] Missing cover image: ai-documentation-generators-2026.png (expected at /home/ubuntu/blog/static/images/ai-documentation-generators-2026.png)
[2026-05-26 21:01:01 UTC] [WARN] Missing cover image: langsmith-vs-langfuse-vs-helicone-2026.png (expected at /home/ubuntu/blog/static/images/langsmith-vs-langfuse-vs-helicone-2026.png)
[2026-05-26 21:01:01 UTC] [WARN] Missing cover image: rag-pipeline-best-practices-2026.png (expected at /home/ubuntu/blog/static/images/rag-pipeline-best-practices-2026.png)
[2026-05-26 21:01:01 UTC] [WARN] Missing cover image: github-models-api-guide-2026.png (expected at /home/ubuntu/blog/static/images/github-models-api-guide-2026.png)
[2026-05-26 21:01:01 UTC] [WARN] Missing cover image: cursor-advanced-tips-2026.png (expected at /home/ubuntu/blog/static/images/cursor-advanced-tips-2026.png)
[2026-05-26 21:01:01 UTC] [WARN] Missing cover image: ai-tools-python-developers-2026.png (expected at /home/ubuntu/blog/static/images/ai-tools-python-developers-2026.png)
[2026-05-26 21:01:01 UTC] [WARN] Missing cover image: langfuse-guide-2026.png (expected at /home/ubuntu/blog/static/images/langfuse-guide-2026.png)
[2026-05-26 21:01:01 UTC] [WARN] Missing cover image: openai-batch-api-guide-2026.png (expected at /home/ubuntu/blog/static/images/openai-batch-api-guide-2026.png)
[2026-05-26 21:01:01 UTC] [WARN] Missing cover image: claude-opus-4-7-vs-4-6-comparison-2026.png (expected at /home/ubuntu/blog/static/images/claude-opus-4-7-vs-4-6-comparison-2026.png)
[2026-05-26 21:01:01 UTC] [WARN] Missing cover image: zeropath-review-2026.png (expected at /home/ubuntu/blog/static/images/zeropath-review-2026.png)
[2026-05-26 21:01:01 UTC] [WARN] Missing cover image: 1password-ai-agent-security-2026.png (expected at /home/ubuntu/blog/static/images/1password-ai-agent-security-2026.png)
[2026-05-26 21:01:01 UTC] [WARN] Missing cover image: azure-openai-assistants-foundry-migration-2026.png (expected at /home/ubuntu/blog/static/images/azure-openai-assistants-foundry-migration-2026.png)
[2026-05-26 21:01:01 UTC] [WARN] Missing cover image: ai-pr-review-time-optimization-2026.png (expected at /home/ubuntu/blog/static/images/ai-pr-review-time-optimization-2026.png)
[2026-05-26 21:01:01 UTC] [WARN] Missing cover image: ai-coding-acceleration-whiplash-2026.png (expected at /home/ubuntu/blog/static/images/ai-coding-acceleration-whiplash-2026.png)
[2026-05-26 21:01:01 UTC] [WARN] Missing cover image: claude-code-vulnerability-detection-guide-2026.png (expected at /home/ubuntu/blog/static/images/claude-code-vulnerability-detection-guide-2026.png)
[2026-05-26 21:01:01 UTC] [WARN] Missing cover image: github-trending-ai-projects-april-2026.png (expected at /home/ubuntu/blog/static/images/github-trending-ai-projects-april-2026.png)
[2026-05-26 21:01:01 UTC] [INFO] Missing cover images: 18
[2026-05-26 21:01:01 UTC] [INFO] 
[2026-05-26 21:01:01 UTC] [INFO] Check 5: Missing schema files
[2026-05-26 21:01:01 UTC] [WARN] Missing schema: schema-ai-coding-stack-2026.html
[2026-05-26 21:01:01 UTC] [WARN] Missing schema: schema-gemini-cli-vs-claude-code-vs-opencode-2026.html
[2026-05-26 21:01:01 UTC] [WARN] Missing schema: schema-ai-documentation-generators-2026.html
[2026-05-26 21:01:01 UTC] [WARN] Missing schema: schema-langsmith-vs-langfuse-vs-helicone-2026.html
[2026-05-26 21:01:01 UTC] [WARN] Missing schema: schema-rag-pipeline-best-practices-2026.html
[2026-05-26 21:01:01 UTC] [WARN] Missing schema: schema-github-models-api-guide-2026.html
[2026-05-26 21:01:01 UTC] [WARN] Missing schema: schema-cursor-advanced-tips-2026.html
[2026-05-26 21:01:01 UTC] [WARN] Missing schema: schema-ai-tools-python-developers-2026.html
[2026-05-26 21:01:01 UTC] [WARN] Missing schema: schema-langfuse-guide-2026.html
[2026-05-26 21:01:01 UTC] [WARN] Missing schema: schema-openai-batch-api-guide-2026.html
[2026-05-26 21:01:01 UTC] [WARN] Missing schema: schema-claude-opus-4-7-vs-4-6-comparison-2026.html
[2026-05-26 21:01:01 UTC] [WARN] Missing schema: schema-zeropath-review-2026.html
[2026-05-26 21:01:01 UTC] [WARN] Missing schema: schema-1password-ai-agent-security-2026.html
[2026-05-26 21:01:01 UTC] [WARN] Missing schema: schema-azure-openai-assistants-foundry-migration-2026.html
[2026-05-26 21:01:01 UTC] [WARN] Missing schema: schema-ai-coding-acceleration-whiplash-2026.html
[2026-05-26 21:01:01 UTC] [WARN] Missing schema: schema-claude-code-vulnerability-detection-guide-2026.html
[2026-05-26 21:01:01 UTC] [INFO] Missing schema files: 16
[2026-05-26 21:01:01 UTC] [INFO] 
[2026-05-26 21:01:01 UTC] [INFO] Check 6: Issues assigned to disabled agents (SEO/Thumbnail)
[2026-05-26 21:01:01 UTC] [INFO] Disabled-agent issues cancelled: 0
[2026-05-26 21:01:01 UTC] [INFO] 
[2026-05-26 21:01:01 UTC] [INFO] Check 6b: Blocked issue auto-recovery
[2026-05-26 21:01:01 UTC] [INFO] Found 97 blocked issues to evaluate
[2026-05-26 21:01:01 UTC] [INFO] BLOCKED: ROC-4330 — no slug found, likely non-blog issue, skipping
[2026-05-26 21:01:01 UTC] [INFO] BLOCKED: ROC-4328 — no slug found, likely non-blog issue, skipping
[2026-05-26 21:01:01 UTC] [INFO] BLOCKED: ROC-4323 — no slug found, likely non-blog issue, skipping
[2026-05-26 21:01:01 UTC] [INFO] BLOCKED: ROC-4315 — no slug found, likely non-blog issue, skipping
[2026-05-26 21:01:01 UTC] [INFO] BLOCKED: ROC-4311 — no slug found, likely non-blog issue, skipping
[2026-05-26 21:01:01 UTC] [INFO] BLOCKED: ROC-4253 — no slug found, likely non-blog issue, skipping
[2026-05-26 21:01:01 UTC] [INFO] BLOCKED: ROC-4243 — no slug found, likely non-blog issue, skipping
[2026-05-26 21:01:01 UTC] [INFO] BLOCKED: ROC-4234 — no slug found, likely non-blog issue, skipping
[2026-05-26 21:01:01 UTC] [INFO] BLOCKED: ROC-4221 — no slug found, likely non-blog issue, skipping
[2026-05-26 21:01:01 UTC] [INFO] BLOCKED: ROC-4220 — no slug found, likely non-blog issue, skipping
[2026-05-26 21:01:01 UTC] [INFO] BLOCKED: ROC-4203 — no slug found, likely non-blog issue, skipping
[2026-05-26 21:01:01 UTC] [INFO] BLOCKED: ROC-4198 — no slug found, likely non-blog issue, skipping
[2026-05-26 21:01:01 UTC] [INFO] BLOCKED: ROC-4195 — no slug found, likely non-blog issue, skipping
[2026-05-26 21:01:01 UTC] [INFO] BLOCKED: ROC-4188 — no slug found, likely non-blog issue, skipping
[2026-05-26 21:01:01 UTC] [INFO] BLOCKED: ROC-4173 — no slug found, likely non-blog issue, skipping
[2026-05-26 21:01:01 UTC] [INFO] BLOCKED: ROC-4174 — no slug found, likely non-blog issue, skipping
[2026-05-26 21:01:01 UTC] [INFO] BLOCKED: ROC-4152 — no slug found, likely non-blog issue, skipping
[2026-05-26 21:01:01 UTC] [INFO] BLOCKED: ROC-4130 — no slug found, likely non-blog issue, skipping
[2026-05-26 21:01:01 UTC] [INFO] BLOCKED: ROC-4104 — no slug found, likely non-blog issue, skipping
[2026-05-26 21:01:01 UTC] [INFO] BLOCKED: ROC-4079 — no slug found, likely non-blog issue, skipping
[2026-05-26 21:01:01 UTC] [INFO] BLOCKED: ROC-4062 — no slug found, likely non-blog issue, skipping
[2026-05-26 21:01:01 UTC] [INFO] BLOCKED: ROC-4046 — no slug found, likely non-blog issue, skipping
[2026-05-26 21:01:01 UTC] [INFO] BLOCKED: ROC-3992 — no slug found, likely non-blog issue, skipping
[2026-05-26 21:01:01 UTC] [INFO] BLOCKED: ROC-3964 — no slug found, likely non-blog issue, skipping
[2026-05-26 21:01:01 UTC] [INFO] BLOCKED: ROC-3943 — no slug found, likely non-blog issue, skipping
[2026-05-26 21:01:01 UTC] [INFO] BLOCKED: ROC-3917 — no slug found, likely non-blog issue, skipping
[2026-05-26 21:01:01 UTC] [INFO] BLOCKED: ROC-3907 — no slug found, likely non-blog issue, skipping
[2026-05-26 21:01:01 UTC] [INFO] BLOCKED: ROC-3879 — no slug found, likely non-blog issue, skipping
[2026-05-26 21:01:01 UTC] [INFO] BLOCKED: ROC-3858 — no slug found, likely non-blog issue, skipping
[2026-05-26 21:01:01 UTC] [INFO] BLOCKED: ROC-3826 — no slug found, likely non-blog issue, skipping
[2026-05-26 21:01:01 UTC] [INFO] BLOCKED: ROC-3827 — no slug found, likely non-blog issue, skipping
[2026-05-26 21:01:01 UTC] [INFO] BLOCKED: ROC-3809 — no slug found, likely non-blog issue, skipping
[2026-05-26 21:01:01 UTC] [INFO] BLOCKED: ROC-3789 — no slug found, likely non-blog issue, skipping
[2026-05-26 21:01:01 UTC] [INFO] BLOCKED: ROC-3764 — no slug found, likely non-blog issue, skipping
[2026-05-26 21:01:01 UTC] [INFO] BLOCKED: ROC-3728 — no slug found, likely non-blog issue, skipping
[2026-05-26 21:01:01 UTC] [INFO] BLOCKED: ROC-3703 — no slug found, likely non-blog issue, skipping
[2026-05-26 21:01:01 UTC] [INFO] BLOCKED: ROC-3683 — no slug found, likely non-blog issue, skipping
[2026-05-26 21:01:01 UTC] [INFO] BLOCKED: ROC-3634 — no slug found, likely non-blog issue, skipping
[2026-05-26 21:01:01 UTC] [INFO] BLOCKED: ROC-3616 — no slug found, likely non-blog issue, skipping
[2026-05-26 21:01:01 UTC] [INFO] BLOCKED: ROC-3593 — no slug found, likely non-blog issue, skipping
[2026-05-26 21:01:01 UTC] [INFO] BLOCKED: ROC-3531 — no slug found, likely non-blog issue, skipping
[2026-05-26 21:01:01 UTC] [INFO] BLOCKED: ROC-3298 — no slug found, likely non-blog issue, skipping
[2026-05-26 21:01:01 UTC] [INFO] BLOCKED: ROC-1724 — no slug found, likely non-blog issue, skipping
[2026-05-26 21:01:01 UTC] [INFO] BLOCKED ROC-4269: slug=codex-plugins-integrations-guide-2026 post=False schema=False cover=False
[2026-05-26 21:01:01 UTC] [ACTION] RE-QUEUED: ROC-4269 → todo (missing: post schema cover)
[2026-05-26 21:01:01 UTC] [INFO] BLOCKED ROC-4268: slug=claude-design-vs-canva-ai-2026 post=False schema=False cover=False
[2026-05-26 21:01:01 UTC] [ACTION] RE-QUEUED: ROC-4268 → todo (missing: post schema cover)
[2026-05-26 21:01:01 UTC] [INFO] BLOCKED ROC-4270: slug=ai-pr-review-time-optimization-2026 post=True schema=True cover=False
[2026-05-26 21:01:01 UTC] [ACTION] RE-QUEUED: ROC-4270 → todo (missing: cover)
[2026-05-26 21:01:01 UTC] [INFO] BLOCKED: ROC-4333 — no slug found, likely non-blog issue, skipping
[2026-05-26 21:01:01 UTC] [INFO] BLOCKED: ROC-4289 — no slug found, likely non-blog issue, skipping
[2026-05-26 21:01:01 UTC] [INFO] BLOCKED: ROC-4329 — no slug found, likely non-blog issue, skipping
[2026-05-26 21:01:01 UTC] [INFO] BLOCKED: ROC-4283 — no slug found, likely non-blog issue, skipping
[2026-05-26 21:01:01 UTC] [INFO] BLOCKED: ROC-4326 — no slug found, likely non-blog issue, skipping
[2026-05-26 21:01:01 UTC] [INFO] BLOCKED: ROC-4320 — no slug found, likely non-blog issue, skipping
[2026-05-26 21:01:01 UTC] [INFO] BLOCKED: ROC-4314 — no slug found, likely non-blog issue, skipping
[2026-05-26 21:01:01 UTC] [INFO] BLOCKED: ROC-4254 — no slug found, likely non-blog issue, skipping
[2026-05-26 21:01:01 UTC] [INFO] BLOCKED: ROC-4235 — no slug found, likely non-blog issue, skipping
[2026-05-26 21:01:01 UTC] [INFO] BLOCKED: ROC-4222 — no slug found, likely non-blog issue, skipping
[2026-05-26 21:01:01 UTC] [INFO] BLOCKED: ROC-4204 — no slug found, likely non-blog issue, skipping
[2026-05-26 21:01:01 UTC] [INFO] BLOCKED: ROC-4201 — no slug found, likely non-blog issue, skipping
[2026-05-26 21:01:01 UTC] [INFO] BLOCKED: ROC-4040 — no slug found, likely non-blog issue, skipping
[2026-05-26 21:01:01 UTC] [INFO] BLOCKED: ROC-4196 — no slug found, likely non-blog issue, skipping
[2026-05-26 21:01:01 UTC] [INFO] BLOCKED: ROC-4036 — no slug found, likely non-blog issue, skipping
[2026-05-26 21:01:01 UTC] [INFO] BLOCKED: ROC-4189 — no slug found, likely non-blog issue, skipping
[2026-05-26 21:01:01 UTC] [INFO] BLOCKED: ROC-4028 — no slug found, likely non-blog issue, skipping
[2026-05-26 21:01:01 UTC] [INFO] BLOCKED: ROC-4175 — no slug found, likely non-blog issue, skipping
[2026-05-26 21:01:01 UTC] [INFO] BLOCKED: ROC-4172 — no slug found, likely non-blog issue, skipping
[2026-05-26 21:01:01 UTC] [INFO] BLOCKED: ROC-4153 — no slug found, likely non-blog issue, skipping
[2026-05-26 21:01:01 UTC] [INFO] BLOCKED: ROC-4133 — no slug found, likely non-blog issue, skipping
[2026-05-26 21:01:01 UTC] [INFO] BLOCKED: ROC-4024 — no slug found, likely non-blog issue, skipping
[2026-05-26 21:01:01 UTC] [INFO] BLOCKED: ROC-4105 — no slug found, likely non-blog issue, skipping
[2026-05-26 21:01:01 UTC] [INFO] BLOCKED: ROC-4016 — no slug found, likely non-blog issue, skipping
[2026-05-26 21:01:01 UTC] [INFO] BLOCKED: ROC-4063 — no slug found, likely non-blog issue, skipping
[2026-05-26 21:01:01 UTC] [INFO] BLOCKED: ROC-4049 — no slug found, likely non-blog issue, skipping
[2026-05-26 21:01:01 UTC] [INFO] BLOCKED: ROC-3993 — no slug found, likely non-blog issue, skipping
[2026-05-26 21:01:01 UTC] [INFO] BLOCKED: ROC-3944 — no slug found, likely non-blog issue, skipping
[2026-05-26 21:01:01 UTC] [INFO] BLOCKED: ROC-3920 — no slug found, likely non-blog issue, skipping
[2026-05-26 21:01:01 UTC] [INFO] BLOCKED: ROC-3908 — no slug found, likely non-blog issue, skipping
[2026-05-26 21:01:01 UTC] [INFO] BLOCKED: ROC-3882 — no slug found, likely non-blog issue, skipping
[2026-05-26 21:01:01 UTC] [INFO] BLOCKED: ROC-3861 — no slug found, likely non-blog issue, skipping
[2026-05-26 21:01:01 UTC] [INFO] BLOCKED: ROC-3828 — no slug found, likely non-blog issue, skipping
[2026-05-26 21:01:01 UTC] [INFO] BLOCKED: ROC-3792 — no slug found, likely non-blog issue, skipping
[2026-05-26 21:01:01 UTC] [INFO] BLOCKED: ROC-3765 — no slug found, likely non-blog issue, skipping
[2026-05-26 21:01:01 UTC] [INFO] BLOCKED: ROC-3731 — no slug found, likely non-blog issue, skipping
[2026-05-26 21:01:01 UTC] [INFO] BLOCKED: ROC-3704 — no slug found, likely non-blog issue, skipping
[2026-05-26 21:01:01 UTC] [INFO] BLOCKED: ROC-3686 — no slug found, likely non-blog issue, skipping
[2026-05-26 21:01:01 UTC] [INFO] BLOCKED: ROC-3635 — no slug found, likely non-blog issue, skipping
[2026-05-26 21:01:01 UTC] [INFO] BLOCKED: ROC-3619 — no slug found, likely non-blog issue, skipping
[2026-05-26 21:01:01 UTC] [INFO] BLOCKED: ROC-3594 — no slug found, likely non-blog issue, skipping
[2026-05-26 21:01:01 UTC] [INFO] BLOCKED: ROC-3591 — no slug found, likely non-blog issue, skipping
[2026-05-26 21:01:01 UTC] [INFO] BLOCKED: ROC-3534 — no slug found, likely non-blog issue, skipping
[2026-05-26 21:01:01 UTC] [INFO] BLOCKED: ROC-3458 — no slug found, likely non-blog issue, skipping
[2026-05-26 21:01:01 UTC] [INFO] BLOCKED: ROC-3454 — no slug found, likely non-blog issue, skipping
[2026-05-26 21:01:01 UTC] [INFO] BLOCKED: ROC-3442 — no slug found, likely non-blog issue, skipping
[2026-05-26 21:01:01 UTC] [INFO] BLOCKED: ROC-3438 — no slug found, likely non-blog issue, skipping
[2026-05-26 21:01:01 UTC] [INFO] BLOCKED: ROC-3082 — no slug found, likely non-blog issue, skipping
[2026-05-26 21:01:01 UTC] [INFO] BLOCKED: ROC-2911 — no slug found, likely non-blog issue, skipping
[2026-05-26 21:01:01 UTC] [INFO] BLOCKED: ROC-2762 — no slug found, likely non-blog issue, skipping
[2026-05-26 21:01:01 UTC] [INFO] BLOCKED: ROC-1842 — no slug found, likely non-blog issue, skipping
[2026-05-26 21:01:01 UTC] [INFO] Blocked issues recovered/re-queued: 3
[2026-05-26 21:01:01 UTC] [INFO] 
[2026-05-26 21:01:01 UTC] [INFO] ============================================================
[2026-05-26 21:01:01 UTC] [INFO] Summary: 3 actions taken
[2026-05-26 21:01:01 UTC] [INFO]   Stuck subtasks cancelled: 0
[2026-05-26 21:01:01 UTC] [INFO]   Zombie subtasks cancelled: 0
[2026-05-26 21:01:01 UTC] [INFO]   Strategist wakes: 0
[2026-05-26 21:01:01 UTC] [INFO]   Disabled-agent issues cancelled: 0
[2026-05-26 21:01:01 UTC] [INFO]   Blocked issues recovered/re-queued: 3
[2026-05-26 21:01:01 UTC] [INFO]   Missing cover images (warnings): 18
[2026-05-26 21:01:01 UTC] [INFO]   Missing schema files (warnings): 16
[2026-05-26 21:01:01 UTC] [INFO] Pipeline Health Check complete
```