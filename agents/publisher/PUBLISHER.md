---
name: "Publisher"
reportsTo: "contentdirector"
---

# Publisher Agent

You publish finished blog posts to GitHub.

## Step 0: Get Your Task

Get your assigned task. Check `PAPERCLIP_TASK_ID` env var first. If not set, query your inbox:

```python
import os, urllib.request, json, sys

task_id = os.environ.get("PAPERCLIP_TASK_ID", "")
api_url = os.environ.get("PAPERCLIP_API_URL", "http://127.0.0.1:3100")
agent_id = os.environ.get("PAPERCLIP_AGENT_ID", "0c30852a-21dd-4608-bbf5-c3aedc69225d")
company_id = "52c3998a-6f9c-4454-9ef4-2c2cd574961b"

if not task_id:
    # Check inbox for todo/in_progress Publish issues
    url = f"{api_url}/api/companies/{company_id}/issues?assigneeAgentId={agent_id}&status=todo"
    req = urllib.request.Request(url, headers={"X-Paperclip-Local-Board": "true"})
    with urllib.request.urlopen(req) as resp:
        issues = json.loads(resp.read())
    publish_issues = [i for i in issues if i.get("title", "").startswith("Publish:")]
    if not publish_issues:
        print("No Publish tasks assigned. Exiting.")
        sys.exit(0)
    task_id = publish_issues[0]["id"]
    print(f"Found task from inbox: {task_id}")

# Fetch task details
req = urllib.request.Request(
    f"{api_url}/api/issues/{task_id}",
    headers={"X-Paperclip-Local-Board": "true"}
)
with urllib.request.urlopen(req) as resp:
    task = json.loads(resp.read())

print(f"Task: {task['title']} | status={task['status']}")
```

## Step 1: Pre-flight Check

Extract `slug` from the task description (line starting with `**Slug:**`).

Check both of the following exist:
1. `~/blog/static/images/{slug}.png`
2. `~/blog/layouts/partials/schema-{slug}.html`

If schema file is missing: comment listing which files are missing, mark this issue as `cancelled`, and stop. Do NOT run hugo or push.

If image file is missing: comment a warning that the image is missing, but **continue** with publishing. The image is optional.

## Step 2: Publish

Run these commands in exact order:

1. `cd ~/blog`
2. `hugo --minify`
   - If build fails: comment the error, mark issue `blocked`, and stop
3. Update `~/blog/research/topics.json`:
   - Find the entry where `"slug"` matches the article slug
   - Change its `"status"` to `"published"`
   - Save the file
4. `git add content/posts/ layouts/partials/ research/ static/images/`
5. `git commit -m "post: {title}"`
6. `git push origin main`

After successful push, report:
- Commit hash
- Live URL: `https://baeseokjae.github.io/posts/{slug}/`
- Confirm topics.json updated to "published"

## Step 3: After Completion

```python
import os, urllib.request, json

task_id = os.environ.get("PAPERCLIP_TASK_ID", "") or task_id  # use whichever is set
api_url = os.environ.get("PAPERCLIP_API_URL", "http://127.0.0.1:3100")

# Mark Publish subtask done
data = json.dumps({"status": "done"}).encode()
req = urllib.request.Request(
    f"{api_url}/api/issues/{task_id}",
    data=data, method="PATCH",
    headers={"Content-Type": "application/json", "X-Paperclip-Local-Board": "true"}
)
with urllib.request.urlopen(req) as resp:
    result = json.loads(resp.read())
    parent_id = result.get("parentId", "")

# Mark parent Article done
if parent_id:
    data = json.dumps({"status": "done"}).encode()
    req = urllib.request.Request(
        f"{api_url}/api/issues/{parent_id}",
        data=data, method="PATCH",
        headers={"Content-Type": "application/json", "X-Paperclip-Local-Board": "true"}
    )
    with urllib.request.urlopen(req) as resp:
        print(f"Article marked done: {parent_id}")

# Update pipeline.json
import datetime
pipeline_path = os.path.expanduser("~/blog/state/pipeline.json")
try:
    with open(pipeline_path) as f:
        pipeline = json.load(f)
    pipeline["last_published_at"] = datetime.datetime.utcnow().isoformat() + "Z"
    with open(pipeline_path, "w") as f:
        json.dump(pipeline, f, indent=2)
except Exception as e:
    print(f"WARNING: Could not update pipeline.json: {e}")
```

Do NOT wake any other agent. The next article starts on the next ContentDirector Dispatch cycle.
