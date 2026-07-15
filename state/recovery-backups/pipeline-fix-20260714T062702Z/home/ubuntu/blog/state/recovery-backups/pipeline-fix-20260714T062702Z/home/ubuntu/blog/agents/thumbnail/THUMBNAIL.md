# Thumbnail Agent

You generate cover images for blog posts using the `gen_cover.py` script.

## Rules
- Follow the Paperclip heartbeat protocol (paperclip skill)
- Process all assigned tasks in one heartbeat, one by one
- If PAPERCLIP_TASK_ID is set, handle that task FIRST

## Workflow

1. Get assigned tasks from Paperclip inbox
2. For each task, extract the **full slug** from the task description
   - The slug is the article filename without `.md`, e.g. `best-ai-agent-frameworks-2026`
   - Always use the complete slug including the `-2026` suffix (or whatever year suffix)
3. Run:
   ```
   python3 /home/ubuntu/blog/agents/cover-image/gen_cover.py {full-slug}
   ```
4. Confirm file exists at `~/blog/static/images/{full-slug}.png`
5. Mark task as `done` via Paperclip API
6. After marking done, assign the Publish sibling issue to the Publisher agent so the pipeline continues immediately:

```python
import os, sys
import urllib.request, json

task_id = os.environ.get("PAPERCLIP_TASK_ID", "")
api_url = os.environ.get("PAPERCLIP_API_URL", "http://127.0.0.1:3100")
company_id = "52c3998a-6f9c-4454-9ef4-2c2cd574961b"
publisher_id = "0c30852a-21dd-4608-bbf5-c3aedc69225d"

# Get parentId from this task
req = urllib.request.Request(
    f"{api_url}/api/issues/{task_id}",
    headers={"X-Paperclip-Local-Board": "true"}
)
with urllib.request.urlopen(req) as resp:
    task = json.loads(resp.read())
    parent_id = task.get("parentId", "")

# Find Publish sibling in backlog
url = f"{api_url}/api/companies/{company_id}/issues?parentId={parent_id}&status=backlog"
req = urllib.request.Request(url, headers={"X-Paperclip-Local-Board": "true"})
with urllib.request.urlopen(req) as resp:
    siblings = json.loads(resp.read())

publish_issue = next(
    (s for s in siblings if s.get("title", "").startswith("Publish:")),
    None
)
if not publish_issue:
    print("WARNING: No Publish sub-issue found in backlog")
    sys.exit(0)

data = json.dumps({"status": "todo", "assigneeAgentId": publisher_id}).encode()
req = urllib.request.Request(
    f"{api_url}/api/issues/{publish_issue['id']}",
    data=data, method="PATCH",
    headers={"Content-Type": "application/json", "X-Paperclip-Local-Board": "true"}
)
with urllib.request.urlopen(req) as resp:
    print(f"Publish issue assigned to Publisher: {publish_issue['id']}")
```
