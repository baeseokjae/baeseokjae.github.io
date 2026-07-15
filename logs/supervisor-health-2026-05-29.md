# Pipeline Health Check
Date: 2026-05-29 21:00 UTC

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
[2026-05-29 21:00:48 UTC] [INFO] ============================================================
[2026-05-29 21:00:48 UTC] [INFO] Pipeline Health Check starting 
[2026-05-29 21:00:48 UTC] [INFO] Fetching Paperclip data...
[2026-05-29 21:00:48 UTC] [INFO] Pipeline: done=51 backlog=0 todo=1 in_progress=2 cancelled=403
[2026-05-29 21:00:48 UTC] [INFO] 
[2026-05-29 21:00:48 UTC] [INFO] Check 1: Stuck subtask issues (>6h, no active run)
[2026-05-29 21:00:48 UTC] [INFO] Stuck subtasks cancelled: 0
[2026-05-29 21:00:48 UTC] [INFO] 
[2026-05-29 21:00:48 UTC] [INFO] Check 2: Zombie subtask issues (null executionRunId >30 min)
[2026-05-29 21:00:48 UTC] [INFO] Zombie subtasks cancelled: 0
[2026-05-29 21:00:48 UTC] [INFO] 
[2026-05-29 21:00:48 UTC] [INFO] Check 3: Topic queue watermark
[2026-05-29 21:00:48 UTC] [INFO] Queued topics: 2303 (watermark: 10)
[2026-05-29 21:00:48 UTC] [INFO] Topic queue healthy, no action needed
[2026-05-29 21:00:48 UTC] [INFO] 
[2026-05-29 21:00:48 UTC] [INFO] Check 4: Missing cover images for published posts
[2026-05-29 21:00:48 UTC] [WARN] Missing cover image: ai-coding-stack-2026.png (expected at /home/ubuntu/blog/static/images/ai-coding-stack-2026.png)
[2026-05-29 21:00:48 UTC] [WARN] Missing cover image: gemini-cli-vs-claude-code-vs-opencode-2026.png (expected at /home/ubuntu/blog/static/images/gemini-cli-vs-claude-code-vs-opencode-2026.png)
[2026-05-29 21:00:48 UTC] [WARN] Missing cover image: ai-documentation-generators-2026.png (expected at /home/ubuntu/blog/static/images/ai-documentation-generators-2026.png)
[2026-05-29 21:00:48 UTC] [WARN] Missing cover image: langsmith-vs-langfuse-vs-helicone-2026.png (expected at /home/ubuntu/blog/static/images/langsmith-vs-langfuse-vs-helicone-2026.png)
[2026-05-29 21:00:48 UTC] [WARN] Missing cover image: rag-pipeline-best-practices-2026.png (expected at /home/ubuntu/blog/static/images/rag-pipeline-best-practices-2026.png)
[2026-05-29 21:00:48 UTC] [WARN] Missing cover image: github-models-api-guide-2026.png (expected at /home/ubuntu/blog/static/images/github-models-api-guide-2026.png)
[2026-05-29 21:00:48 UTC] [WARN] Missing cover image: cursor-advanced-tips-2026.png (expected at /home/ubuntu/blog/static/images/cursor-advanced-tips-2026.png)
[2026-05-29 21:00:48 UTC] [WARN] Missing cover image: ai-tools-python-developers-2026.png (expected at /home/ubuntu/blog/static/images/ai-tools-python-developers-2026.png)
[2026-05-29 21:00:48 UTC] [WARN] Missing cover image: langfuse-guide-2026.png (expected at /home/ubuntu/blog/static/images/langfuse-guide-2026.png)
[2026-05-29 21:00:48 UTC] [WARN] Missing cover image: openai-batch-api-guide-2026.png (expected at /home/ubuntu/blog/static/images/openai-batch-api-guide-2026.png)
[2026-05-29 21:00:48 UTC] [WARN] Missing cover image: claude-opus-4-7-vs-4-6-comparison-2026.png (expected at /home/ubuntu/blog/static/images/claude-opus-4-7-vs-4-6-comparison-2026.png)
[2026-05-29 21:00:48 UTC] [WARN] Missing cover image: zeropath-review-2026.png (expected at /home/ubuntu/blog/static/images/zeropath-review-2026.png)
[2026-05-29 21:00:48 UTC] [WARN] Missing cover image: 1password-ai-agent-security-2026.png (expected at /home/ubuntu/blog/static/images/1password-ai-agent-security-2026.png)
[2026-05-29 21:00:48 UTC] [WARN] Missing cover image: azure-openai-assistants-foundry-migration-2026.png (expected at /home/ubuntu/blog/static/images/azure-openai-assistants-foundry-migration-2026.png)
[2026-05-29 21:00:48 UTC] [WARN] Missing cover image: ai-coding-acceleration-whiplash-2026.png (expected at /home/ubuntu/blog/static/images/ai-coding-acceleration-whiplash-2026.png)
[2026-05-29 21:00:48 UTC] [WARN] Missing cover image: claude-code-vulnerability-detection-guide-2026.png (expected at /home/ubuntu/blog/static/images/claude-code-vulnerability-detection-guide-2026.png)
[2026-05-29 21:00:48 UTC] [WARN] Missing cover image: github-trending-ai-projects-april-2026.png (expected at /home/ubuntu/blog/static/images/github-trending-ai-projects-april-2026.png)
[2026-05-29 21:00:48 UTC] [INFO] Missing cover images: 17
[2026-05-29 21:00:48 UTC] [INFO] 
[2026-05-29 21:00:48 UTC] [INFO] Check 5: Missing schema files
[2026-05-29 21:00:48 UTC] [WARN] Missing schema: schema-ai-coding-stack-2026.html
[2026-05-29 21:00:48 UTC] [WARN] Missing schema: schema-gemini-cli-vs-claude-code-vs-opencode-2026.html
[2026-05-29 21:00:48 UTC] [WARN] Missing schema: schema-ai-documentation-generators-2026.html
[2026-05-29 21:00:48 UTC] [WARN] Missing schema: schema-langsmith-vs-langfuse-vs-helicone-2026.html
[2026-05-29 21:00:48 UTC] [WARN] Missing schema: schema-rag-pipeline-best-practices-2026.html
[2026-05-29 21:00:48 UTC] [WARN] Missing schema: schema-github-models-api-guide-2026.html
[2026-05-29 21:00:48 UTC] [WARN] Missing schema: schema-cursor-advanced-tips-2026.html
[2026-05-29 21:00:48 UTC] [WARN] Missing schema: schema-ai-tools-python-developers-2026.html
[2026-05-29 21:00:48 UTC] [WARN] Missing schema: schema-langfuse-guide-2026.html
[2026-05-29 21:00:48 UTC] [WARN] Missing schema: schema-openai-batch-api-guide-2026.html
[2026-05-29 21:00:48 UTC] [WARN] Missing schema: schema-claude-opus-4-7-vs-4-6-comparison-2026.html
[2026-05-29 21:00:48 UTC] [WARN] Missing schema: schema-zeropath-review-2026.html
[2026-05-29 21:00:48 UTC] [WARN] Missing schema: schema-1password-ai-agent-security-2026.html
[2026-05-29 21:00:48 UTC] [WARN] Missing schema: schema-azure-openai-assistants-foundry-migration-2026.html
[2026-05-29 21:00:48 UTC] [WARN] Missing schema: schema-ai-coding-acceleration-whiplash-2026.html
[2026-05-29 21:00:48 UTC] [WARN] Missing schema: schema-claude-code-vulnerability-detection-guide-2026.html
[2026-05-29 21:00:48 UTC] [INFO] Missing schema files: 16
[2026-05-29 21:00:48 UTC] [INFO] 
[2026-05-29 21:00:48 UTC] [INFO] Check 6: Issues assigned to disabled agents (SEO/Thumbnail)
[2026-05-29 21:00:48 UTC] [INFO] Disabled-agent issues cancelled: 0
[2026-05-29 21:00:48 UTC] [INFO] 
[2026-05-29 21:00:48 UTC] [INFO] Check 6b: Blocked issue auto-recovery
[2026-05-29 21:00:48 UTC] [INFO] Found 43 blocked issues to evaluate
[2026-05-29 21:00:48 UTC] [INFO] BLOCKED: ROC-4495 — no slug found, likely non-blog issue, skipping
[2026-05-29 21:00:48 UTC] [INFO] BLOCKED: ROC-4496 — no slug found, likely non-blog issue, skipping
[2026-05-29 21:00:48 UTC] [INFO] BLOCKED: ROC-4491 — no slug found, likely non-blog issue, skipping
[2026-05-29 21:00:48 UTC] [INFO] BLOCKED: ROC-4492 — no slug found, likely non-blog issue, skipping
[2026-05-29 21:00:48 UTC] [INFO] BLOCKED: ROC-4429 — no slug found, likely non-blog issue, skipping
[2026-05-29 21:00:48 UTC] [INFO] BLOCKED: ROC-4425 — no slug found, likely non-blog issue, skipping
[2026-05-29 21:00:48 UTC] [INFO] BLOCKED: ROC-4395 — no slug found, likely non-blog issue, skipping
[2026-05-29 21:00:48 UTC] [INFO] BLOCKED: ROC-4392 — no slug found, likely non-blog issue, skipping
[2026-05-29 21:00:48 UTC] [INFO] BLOCKED: ROC-4380 — no slug found, likely non-blog issue, skipping
[2026-05-29 21:00:48 UTC] [INFO] BLOCKED: ROC-4378 — no slug found, likely non-blog issue, skipping
[2026-05-29 21:00:48 UTC] [INFO] BLOCKED: ROC-4374 — no slug found, likely non-blog issue, skipping
[2026-05-29 21:00:48 UTC] [INFO] BLOCKED: ROC-4341 — no slug found, likely non-blog issue, skipping
[2026-05-29 21:00:48 UTC] [INFO] BLOCKED: ROC-4337 — no slug found, likely non-blog issue, skipping
[2026-05-29 21:00:48 UTC] [INFO] BLOCKED: ROC-4335 — no slug found, likely non-blog issue, skipping
[2026-05-29 21:00:48 UTC] [INFO] BLOCKED: ROC-4334 — no slug found, likely non-blog issue, skipping
[2026-05-29 21:00:48 UTC] [INFO] BLOCKED: ROC-4330 — no slug found, likely non-blog issue, skipping
[2026-05-29 21:00:48 UTC] [INFO] BLOCKED: ROC-4328 — no slug found, likely non-blog issue, skipping
[2026-05-29 21:00:48 UTC] [INFO] BLOCKED: ROC-4323 — no slug found, likely non-blog issue, skipping
[2026-05-29 21:00:48 UTC] [INFO] BLOCKED: ROC-4315 — no slug found, likely non-blog issue, skipping
[2026-05-29 21:00:48 UTC] [INFO] BLOCKED: ROC-4311 — no slug found, likely non-blog issue, skipping
[2026-05-29 21:00:48 UTC] [INFO] BLOCKED: ROC-4253 — no slug found, likely non-blog issue, skipping
[2026-05-29 21:00:48 UTC] [INFO] BLOCKED: ROC-4243 — no slug found, likely non-blog issue, skipping
[2026-05-29 21:00:48 UTC] [INFO] BLOCKED: ROC-4234 — no slug found, likely non-blog issue, skipping
[2026-05-29 21:00:48 UTC] [INFO] BLOCKED: ROC-4221 — no slug found, likely non-blog issue, skipping
[2026-05-29 21:00:48 UTC] [INFO] BLOCKED: ROC-4220 — no slug found, likely non-blog issue, skipping
[2026-05-29 21:00:48 UTC] [INFO] BLOCKED: ROC-4203 — no slug found, likely non-blog issue, skipping
[2026-05-29 21:00:48 UTC] [INFO] BLOCKED: ROC-4198 — no slug found, likely non-blog issue, skipping
[2026-05-29 21:00:48 UTC] [INFO] BLOCKED: ROC-4195 — no slug found, likely non-blog issue, skipping
[2026-05-29 21:00:48 UTC] [INFO] BLOCKED: ROC-4188 — no slug found, likely non-blog issue, skipping
[2026-05-29 21:00:48 UTC] [INFO] BLOCKED: ROC-4173 — no slug found, likely non-blog issue, skipping
[2026-05-29 21:00:48 UTC] [INFO] BLOCKED: ROC-4174 — no slug found, likely non-blog issue, skipping
[2026-05-29 21:00:48 UTC] [INFO] BLOCKED: ROC-4152 — no slug found, likely non-blog issue, skipping
[2026-05-29 21:00:48 UTC] [INFO] BLOCKED: ROC-4130 — no slug found, likely non-blog issue, skipping
[2026-05-29 21:00:48 UTC] [INFO] BLOCKED: ROC-4104 — no slug found, likely non-blog issue, skipping
[2026-05-29 21:00:48 UTC] [INFO] BLOCKED: ROC-4079 — no slug found, likely non-blog issue, skipping
[2026-05-29 21:00:48 UTC] [INFO] BLOCKED: ROC-4062 — no slug found, likely non-blog issue, skipping
[2026-05-29 21:00:48 UTC] [INFO] BLOCKED: ROC-4046 — no slug found, likely non-blog issue, skipping
[2026-05-29 21:00:48 UTC] [INFO] BLOCKED: ROC-3992 — no slug found, likely non-blog issue, skipping
[2026-05-29 21:00:48 UTC] [INFO] BLOCKED: ROC-3964 — no slug found, likely non-blog issue, skipping
[2026-05-29 21:00:48 UTC] [INFO] BLOCKED: ROC-3943 — no slug found, likely non-blog issue, skipping
[2026-05-29 21:00:48 UTC] [INFO] BLOCKED: ROC-3917 — no slug found, likely non-blog issue, skipping
[2026-05-29 21:00:48 UTC] [INFO] BLOCKED: ROC-3907 — no slug found, likely non-blog issue, skipping
[2026-05-29 21:00:48 UTC] [INFO] BLOCKED: ROC-3879 — no slug found, likely non-blog issue, skipping
[2026-05-29 21:00:48 UTC] [INFO] Blocked issues recovered/re-queued: 0
[2026-05-29 21:00:48 UTC] [INFO] 
[2026-05-29 21:00:48 UTC] [INFO] ============================================================
[2026-05-29 21:00:48 UTC] [INFO] Summary: 0 actions taken
[2026-05-29 21:00:48 UTC] [INFO]   Stuck subtasks cancelled: 0
[2026-05-29 21:00:48 UTC] [INFO]   Zombie subtasks cancelled: 0
[2026-05-29 21:00:48 UTC] [INFO]   Strategist wakes: 0
[2026-05-29 21:00:48 UTC] [INFO]   Disabled-agent issues cancelled: 0
[2026-05-29 21:00:48 UTC] [INFO]   Blocked issues recovered/re-queued: 0
[2026-05-29 21:00:48 UTC] [INFO]   Missing cover images (warnings): 17
[2026-05-29 21:00:48 UTC] [INFO]   Missing schema files (warnings): 16
[2026-05-29 21:00:48 UTC] [INFO] Pipeline Health Check complete
```