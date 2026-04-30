#!/usr/bin/env python3
"""
Pipeline Health Check (pipeline_health_check.py)

Replaces the LLM-based Supervisor agent with a lightweight Python script.
Runs as a cron job, performs simple checks, and writes a health report.

Checks performed:
  1. Stuck subtask issues (in_progress > 6h with no active run) — cancel
  2. Zombie subtask issues (in_progress with null executionRunId > 30 min) — cancel
  3. Topic queue watermark (queued < 10 in topics.json) — wake Strategist
  4. Missing cover images for published posts — log warning
  5. Missing schema files — log warning
  6. Issues assigned to disabled agents (SEO/Thumbnail) — cancel
  7. Write results to ~/blog/logs/supervisor-health-{date}.md
  8. Always exit 0 (never fail the cron)

Usage:
  python3 ~/blog/agents/supervisor/pipeline_health_check.py [--dry-run]
"""

import json
import urllib.request
import urllib.error
import sys
import os
from datetime import datetime, timezone, timedelta
from collections import Counter

# ============================================================
# Configuration
# ============================================================
COMPANY_ID = "ab752c4f-0e8b-4669-8e76-2746d00ae8c9"
BASE_URL = "http://127.0.0.1:3100/api"
HEADERS = {
    "X-Paperclip-Local-Board": "true",
    "Content-Type": "application/json"
}

SUPERVISOR_AGENT_ID = "9e1b92e9-11dd-41ba-8398-b951549a3696"
STRATEGIST_AGENT_ID = "458d5ac7-e504-4b95-af7a-a9fdf7151895"

# Thresholds
STUCK_HOURS = 6          # Subtask in_progress > 6h with no active run
ZOMBIE_MINUTES = 30      # Subtask in_progress with null executionRunId > 30 min
QUEUE_WATERMARK = 10     # Minimum queued topics before waking Strategist

# Disabled agents whose assigned issues should be cancelled
DISABLED_AGENT_NAMES = {"SEO", "Thumbnail"}

# Blog paths
BLOG_DIR = os.path.expanduser("~/blog")
TOPICS_FILE = os.path.join(BLOG_DIR, "research", "topics.json")
POSTS_DIR = os.path.join(BLOG_DIR, "content", "posts")
IMAGES_DIR = os.path.join(BLOG_DIR, "static", "images")
SCHEMAS_DIR = os.path.join(BLOG_DIR, "layouts", "partials")
STATE_DIR = os.path.join(BLOG_DIR, "state", "supervisor")
LOG_DIR = os.path.join(BLOG_DIR, "logs")

# State file for circuit breakers
STATE_FILE = os.path.join(STATE_DIR, "health-check-state.json")

# ============================================================
# API Helpers
# ============================================================

def api(method, url, data=None):
    """Make an API request to Paperclip."""
    req = urllib.request.Request(url, headers=HEADERS, method=method)
    if data:
        req.data = json.dumps(data).encode()
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode()[:500]
        return {"error": f"HTTP {e.code}", "body": body}
    except Exception as e:
        return {"error": str(e)}


def api_get_all_issues():
    """Fetch all issues from Paperclip."""
    result = api("GET", f"{BASE_URL}/companies/{COMPANY_ID}/issues")
    if isinstance(result, dict) and "error" in result:
        return []
    return result if isinstance(result, list) else []


def api_get_all_agents():
    """Fetch all agents from Paperclip."""
    result = api("GET", f"{BASE_URL}/companies/{COMPANY_ID}/agents")
    if isinstance(result, dict) and "error" in result:
        return []
    return result if isinstance(result, list) else []


def cancel_issue(issue_id, issue_identifier):
    """Cancel an issue. Returns True on success."""
    result = api("PATCH", f"{BASE_URL}/issues/{issue_id}", {"status": "cancelled"})
    if isinstance(result, dict) and "error" not in result:
        return True
    # Fallback: company-scoped
    result2 = api("PATCH", f"{BASE_URL}/companies/{COMPANY_ID}/issues/{issue_id}", {"status": "cancelled"})
    if isinstance(result2, dict) and "error" not in result2:
        return True
    return False


def wake_agent(agent_id, agent_name):
    """Wake an agent via the Paperclip API."""
    result = api("POST", f"{BASE_URL}/agents/{agent_id}/wakeup", {
        "source": "automation",
        "forceFreshSession": True
    })
    if isinstance(result, dict) and "error" not in result:
        return True
    return False


# ============================================================
# State / Circuit Breaker
# ============================================================

def load_state():
    """Load persistent state for circuit breakers."""
    try:
        with open(STATE_FILE) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"strategist_wakes": [], "cancelled_issues": {}}


def save_state(state):
    """Save persistent state."""
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def can_wake_strategist(state, now):
    """Rate-limit: max 1 Strategist wake per hour."""
    wakes = state.get("strategist_wakes", [])
    recent = [w for w in wakes
              if datetime.fromisoformat(w["time"].replace("Z", "+00:00")) > now - timedelta(hours=1)]
    return len(recent) == 0


# ============================================================
# Logging
# ============================================================

class HealthReport:
    """Accumulates log lines and builds the final markdown report."""

    def __init__(self):
        self.lines = []
        self.actions = []
        self.warnings = []

    def log(self, msg, level="INFO"):
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        line = f"[{ts}] [{level}] {msg}"
        print(line)
        self.lines.append(line)
        if level in ("WARN", "WARNING"):
            self.warnings.append(msg)
        if level == "ACTION":
            self.actions.append(msg)

    def to_markdown(self):
        now = datetime.now(timezone.utc)
        sections = []
        sections.append(f"# Pipeline Health Check")
        sections.append(f"Date: {now.strftime('%Y-%m-%d %H:%M UTC')}")
        sections.append("")
        if self.actions:
            sections.append("## Actions Taken")
            for a in self.actions:
                sections.append(f"- {a}")
            sections.append("")
        if self.warnings:
            sections.append("## Warnings")
            for w in self.warnings:
                sections.append(f"- {w}")
            sections.append("")
        sections.append("## Full Log")
        sections.append("```")
        for line in self.lines:
            sections.append(line)
        sections.append("```")
        return "\n".join(sections)


report = HealthReport()


# ============================================================
# Check 1: Stuck subtask issues (in_progress > 6h with no active run)
# ============================================================

def check_stuck_subtasks(issues, agents, now, dry_run):
    """Cancel subtask issues stuck in_progress for > 6h with no active agent run."""
    report.log("Check 1: Stuck subtask issues (>6h, no active run)")
    cancelled = 0

    # Build set of currently running agent IDs
    running_agent_ids = set()
    for a in agents:
        if a.get("status") == "running":
            running_agent_ids.add(a.get("id"))

    for issue in issues:
        if issue.get("status") != "in_progress":
            continue
        # Only subtask issues (have parentId)
        if not issue.get("parentId"):
            continue
        # Must have an assigned agent
        if not issue.get("assigneeAgentId"):
            continue

        started = issue.get("startedAt")
        if not started:
            continue

        try:
            started_dt = datetime.fromisoformat(started.replace("Z", "+00:00"))
        except (ValueError, TypeError):
            continue

        hours_elapsed = (now - started_dt).total_seconds() / 3600
        if hours_elapsed <= STUCK_HOURS:
            continue

        # Is the assigned agent actively running?
        assigned_id = issue.get("assigneeAgentId")
        exec_run_id = issue.get("executionRunId")

        # Has an active run AND the agent is running => not stuck
        if exec_run_id and assigned_id in running_agent_ids:
            continue

        identifier = issue.get("identifier", "N/A")
        title = (issue.get("title") or "")[:60]
        report.log(f"STUCK: {identifier} ({hours_elapsed:.1f}h, no active run) — {title}", "ACTION")

        if dry_run:
            report.log(f"[DRY RUN] Would cancel stuck subtask {identifier}")
            continue

        if cancel_issue(issue["id"], identifier):
            report.log(f"Cancelled stuck subtask {identifier}", "ACTION")
            cancelled += 1
        else:
            report.log(f"Failed to cancel stuck subtask {identifier}", "WARN")

    report.log(f"Stuck subtasks cancelled: {cancelled}")
    return cancelled


# ============================================================
# Check 2: Zombie subtask issues (null executionRunId > 30 min)
# ============================================================

def check_zombie_subtasks(issues, now, dry_run):
    """Cancel zombie subtask issues: in_progress with null executionRunId for >30 min."""
    report.log("Check 2: Zombie subtask issues (null executionRunId >30 min)")
    cancelled = 0

    for issue in issues:
        if issue.get("status") != "in_progress":
            continue
        # Only subtask issues (have parentId AND assigneeAgentId)
        if not issue.get("parentId"):
            continue
        if not issue.get("assigneeAgentId"):
            continue

        # Already has an executionRunId — not a zombie
        if issue.get("executionRunId"):
            continue

        started = issue.get("startedAt")
        if not started:
            # No startedAt but in_progress with no run — treat as zombie if updatedAt >30 min
            updated = issue.get("updatedAt")
            if updated:
                try:
                    updated_dt = datetime.fromisoformat(updated.replace("Z", "+00:00"))
                    minutes_elapsed = (now - updated_dt).total_seconds() / 60
                except (ValueError, TypeError):
                    continue
            else:
                # Can't determine age — skip
                continue
        else:
            try:
                started_dt = datetime.fromisoformat(started.replace("Z", "+00:00"))
                minutes_elapsed = (now - started_dt).total_seconds() / 60
            except (ValueError, TypeError):
                continue

        if minutes_elapsed <= ZOMBIE_MINUTES:
            continue

        identifier = issue.get("identifier", "N/A")
        title = (issue.get("title") or "")[:60]
        report.log(f"ZOMBIE: {identifier} ({minutes_elapsed:.0f} min, no execRunId) — {title}", "ACTION")

        if dry_run:
            report.log(f"[DRY RUN] Would cancel zombie subtask {identifier}")
            continue

        if cancel_issue(issue["id"], identifier):
            report.log(f"Cancelled zombie subtask {identifier}", "ACTION")
            cancelled += 1
        else:
            report.log(f"Failed to cancel zombie subtask {identifier}", "WARN")

    report.log(f"Zombie subtasks cancelled: {cancelled}")
    return cancelled


# ============================================================
# Check 3: Topic queue watermark
# ============================================================

def check_topic_queue(state, now, dry_run):
    """Count queued topics; if < 10, wake Strategist agent."""
    report.log("Check 3: Topic queue watermark")
    queued_count = 0

    try:
        with open(TOPICS_FILE, "r") as f:
            topics = json.load(f)
        queued_count = sum(1 for t in topics if t.get("status") == "queued")
    except FileNotFoundError:
        report.log(f"topics.json not found at {TOPICS_FILE}", "WARN")
    except json.JSONDecodeError:
        report.log(f"topics.json has invalid JSON", "WARN")
    except Exception as e:
        report.log(f"Error reading topics.json: {e}", "WARN")

    report.log(f"Queued topics: {queued_count} (watermark: {QUEUE_WATERMARK})")

    if queued_count < QUEUE_WATERMARK:
        report.log(f"Queue below watermark ({queued_count} < {QUEUE_WATERMARK}), need to wake Strategist")
        if not can_wake_strategist(state, now):
            report.log("Strategist wake rate-limited (already woken in last hour), skipping", "WARN")
            return 0

        if dry_run:
            report.log("[DRY RUN] Would wake Strategist agent")
            return 0

        if wake_agent(STRATEGIST_AGENT_ID, "Strategist"):
            report.log("Woke Strategist agent to refill topic queue", "ACTION")
            state.setdefault("strategist_wakes", []).append({"time": now.isoformat()})
            return 1
        else:
            report.log("Failed to wake Strategist agent", "WARN")
            return 0
    else:
        report.log("Topic queue healthy, no action needed")

    return 0


# ============================================================
# Check 4: Missing cover images for published posts
# ============================================================

def check_missing_cover_images():
    """Check published posts for missing cover images."""
    report.log("Check 4: Missing cover images for published posts")
    missing = 0

    # Read topics to find published slugs
    published_slugs = []
    try:
        with open(TOPICS_FILE, "r") as f:
            topics = json.load(f)
        published_slugs = [t.get("slug") for t in topics if t.get("status") == "published" and t.get("slug")]
    except Exception as e:
        report.log(f"Cannot read topics for published slugs: {e}", "WARN")

    # Also scan posts directory for frontmatter with draft=false
    if os.path.isdir(POSTS_DIR):
        for filename in os.listdir(POSTS_DIR):
            if not filename.endswith(".md"):
                continue
            slug = filename[:-3]  # strip .md
            filepath = os.path.join(POSTS_DIR, filename)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                # Quick check: if draft: true, skip
                if "draft: true" in content[:500]:
                    continue
                if slug not in published_slugs:
                    published_slugs.append(slug)
            except Exception:
                pass

    for slug in published_slugs:
        image_path = os.path.join(IMAGES_DIR, f"{slug}.png")
        if not os.path.exists(image_path):
            report.log(f"Missing cover image: {slug}.png (expected at {image_path})", "WARN")
            missing += 1

    if missing == 0:
        report.log("All published posts have cover images")
    else:
        report.log(f"Missing cover images: {missing}")

    return missing


# ============================================================
# Check 5: Missing schema files
# ============================================================

def check_missing_schemas():
    """Check published posts for missing schema HTML files."""
    report.log("Check 5: Missing schema files")
    missing = 0

    # Collect published slugs
    published_slugs = []
    try:
        with open(TOPICS_FILE, "r") as f:
            topics = json.load(f)
        published_slugs = [t.get("slug") for t in topics if t.get("status") == "published" and t.get("slug")]
    except Exception as e:
        report.log(f"Cannot read topics for schema check: {e}", "WARN")

    # Also check posts on disk that are non-draft
    if os.path.isdir(POSTS_DIR):
        for filename in os.listdir(POSTS_DIR):
            if not filename.endswith(".md"):
                continue
            slug = filename[:-3]
            filepath = os.path.join(POSTS_DIR, filename)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                if "draft: true" in content[:500]:
                    continue
                if slug not in published_slugs:
                    published_slugs.append(slug)
            except Exception:
                pass

    for slug in published_slugs:
        schema_path = os.path.join(SCHEMAS_DIR, f"schema-{slug}.html")
        if not os.path.exists(schema_path):
            report.log(f"Missing schema: schema-{slug}.html", "WARN")
            missing += 1

    if missing == 0:
        report.log("All published posts have schema files")
    else:
        report.log(f"Missing schema files: {missing}")

    return missing


# ============================================================
# Check 6b: Blocked issue auto-recovery
# ============================================================

def check_blocked_auto_recovery(issues, dry_run):
    """Auto-recover blocked issues:
    - If all files exist (post + schema + cover) → mark as done
    - If files missing → re-queue as todo with original assignee
    """
    report.log("Check 6b: Blocked issue auto-recovery")
    recovered = 0

    blocked = [i for i in issues if i.get("status") == "blocked"]
    if not blocked:
        report.log("No blocked issues found")
        return 0

    report.log(f"Found {len(blocked)} blocked issues to evaluate")

    for issue in blocked:
        identifier = issue.get("identifier", "N/A")
        title = (issue.get("title") or "")[:80]
        desc = (issue.get("description") or "")[:500].lower()

        # Extract slug from description or title
        slug = None
        import re
        # Try "slug: xxx" pattern in description
        slug_match = re.search(r'slug[:\s]+([a-z0-9][-a-z0-9]+[a-z0-9])', desc)
        if slug_match:
            slug = slug_match.group(1)
        else:
            # Try to extract from title like "Write: AI Testing Tools (slug)"
            title_text = (issue.get("title") or "")
            slug_match2 = re.search(r'\(([a-z0-9][-a-z0-9]+[a-z0-9])\)', title_text, re.IGNORECASE)
            if slug_match2:
                slug = slug_match2.group(1).lower()

        if not slug:
            # Also try extracting from description paths like ~/blog/content/posts/{slug}.md
            path_match = re.search(r'content/posts/([a-z0-9][-a-z0-9]+)', desc)
            if path_match:
                slug = path_match.group(1)

        if not slug:
            # Non-blog issue (analytics, maintenance, etc.) — skip
            report.log(f"BLOCKED: {identifier} — no slug found, likely non-blog issue, skipping")
            continue

        # Check if all required files exist
        post_path = os.path.join(POSTS_DIR, f"{slug}.md")
        schema_path = os.path.join(SCHEMAS_DIR, f"schema-{slug}.html")
        cover_path = os.path.join(IMAGES_DIR, f"{slug}.png")

        post_exists = os.path.exists(post_path)
        schema_exists = os.path.exists(schema_path)
        cover_exists = os.path.exists(cover_path)

        all_exist = post_exists and schema_exists and cover_exists

        identifier_str = identifier
        report.log(f"BLOCKED {identifier_str}: slug={slug} post={post_exists} schema={schema_exists} cover={cover_exists}")

        if dry_run:
            if all_exist:
                report.log(f"[DRY RUN] Would mark {identifier_str} as done (all files present)")
            else:
                report.log(f"[DRY RUN] Would re-queue {identifier_str} as todo (missing files)")
            continue

        if all_exist:
            # All files exist — mark as done
            result = api("PATCH", f"{BASE_URL}/issues/{issue['id']}", {"status": "done"})
            if isinstance(result, dict) and "error" not in result:
                report.log(f"RECOVERED: {identifier_str} → done (all files present)", "ACTION")
                recovered += 1
            else:
                report.log(f"Failed to mark {identifier_str} as done: {result.get('error', 'unknown')}", "WARN")
        else:
            # Missing files — re-queue as todo with original assignee
            assignee_id = issue.get("assigneeAgentId")
            patch_data = {"status": "todo"}
            if assignee_id:
                patch_data["assigneeAgentId"] = assignee_id
            result = api("PATCH", f"{BASE_URL}/issues/{issue['id']}", patch_data)
            if isinstance(result, dict) and "error" not in result:
                report.log(f"RE-QUEUED: {identifier_str} → todo (missing: " +
                           f"{'post ' if not post_exists else ''}" +
                           f"{'schema ' if not schema_exists else ''}" +
                           f"{'cover' if not cover_exists else ''})", "ACTION")
                recovered += 1
            else:
                report.log(f"Failed to re-queue {identifier_str}: {result.get('error', 'unknown')}", "WARN")

    report.log(f"Blocked issues recovered/re-queued: {recovered}")
    return recovered


# ============================================================
# Check 6: Issues assigned to disabled agents (SEO/Thumbnail)
# ============================================================

def check_disabled_agent_issues(issues, agents, dry_run):
    """Cancel issues assigned to disabled agents (SEO, Thumbnail)."""
    report.log("Check 6: Issues assigned to disabled agents (SEO/Thumbnail)")
    cancelled = 0

    # Find disabled agent IDs by name
    disabled_agent_ids = set()
    for a in agents:
        name = a.get("name", "")
        if name in DISABLED_AGENT_NAMES:
            disabled_agent_ids.add(a.get("id"))

    if not disabled_agent_ids:
        report.log("No disabled agents found in agent list")
        # Still check issues — the agent may have been removed but issues linger
        # Use name-based matching on assignee field

    for issue in issues:
        if issue.get("status") in ("done", "cancelled"):
            continue

        assigned_id = issue.get("assigneeAgentId")
        assigned_name = issue.get("assigneeAgentName") or ""

        is_disabled = False
        if assigned_id and assigned_id in disabled_agent_ids:
            is_disabled = True
        elif assigned_name and assigned_name in DISABLED_AGENT_NAMES:
            is_disabled = True

        if not is_disabled:
            # Also check if the issue title suggests it's for a disabled agent
            title = (issue.get("title") or "").lower()
            for da_name in DISABLED_AGENT_NAMES:
                if f"[{da_name.lower()}]" in title or f": {da_name.lower()}" in title:
                    # Too aggressive — only cancel if explicitly assigned
                    pass

        if not is_disabled:
            continue

        identifier = issue.get("identifier", "N/A")
        title = (issue.get("title") or "")[:60]
        report.log(f"DISABLED-AGENT: {identifier} assigned to disabled agent — {title}", "ACTION")

        if dry_run:
            report.log(f"[DRY RUN] Would cancel issue {identifier}")
            continue

        if cancel_issue(issue["id"], identifier):
            report.log(f"Cancelled issue {identifier} (disabled agent)", "ACTION")
            cancelled += 1
        else:
            report.log(f"Failed to cancel {identifier}", "WARN")

    report.log(f"Disabled-agent issues cancelled: {cancelled}")
    return cancelled


# ============================================================
# Main
# ============================================================

def run(dry_run=False):
    """Run all health checks."""
    now = datetime.now(timezone.utc)
    state = load_state()

    report.log("=" * 60)
    report.log(f"Pipeline Health Check starting {'(DRY RUN)' if dry_run else ''}")

    # Fetch data
    report.log("Fetching Paperclip data...")
    issues = api_get_all_issues()
    agents = api_get_all_agents()

    if not issues and not agents:
        report.log("No issues or agents fetched — API may be down", "WARN")

    # Pipeline summary (quick snapshot)
    status_count = Counter(i.get("status") for i in issues)
    report.log(f"Pipeline: done={status_count.get('done',0)} backlog={status_count.get('backlog',0)} "
               f"todo={status_count.get('todo',0)} in_progress={status_count.get('in_progress',0)} "
               f"cancelled={status_count.get('cancelled',0)}")

    # Run all checks
    report.log("")
    stuck_cancelled = check_stuck_subtasks(issues, agents, now, dry_run)
    report.log("")
    zombie_cancelled = check_zombie_subtasks(issues, now, dry_run)
    report.log("")
    strategist_wakes = check_topic_queue(state, now, dry_run)
    report.log("")
    missing_images = check_missing_cover_images()
    report.log("")
    missing_schemas = check_missing_schemas()
    report.log("")
    disabled_cancelled = check_disabled_agent_issues(issues, agents, dry_run)
    report.log("")
    blocked_recovered = check_blocked_auto_recovery(issues, dry_run)
    report.log("")

    # Summary
    total_actions = stuck_cancelled + zombie_cancelled + strategist_wakes + disabled_cancelled + blocked_recovered
    report.log("=" * 60)
    report.log(f"Summary: {total_actions} actions taken")
    report.log(f"  Stuck subtasks cancelled: {stuck_cancelled}")
    report.log(f"  Zombie subtasks cancelled: {zombie_cancelled}")
    report.log(f"  Strategist wakes: {strategist_wakes}")
    report.log(f"  Disabled-agent issues cancelled: {disabled_cancelled}")
    report.log(f"  Blocked issues recovered/re-queued: {blocked_recovered}")
    report.log(f"  Missing cover images (warnings): {missing_images}")
    report.log(f"  Missing schema files (warnings): {missing_schemas}")
    report.log("Pipeline Health Check complete")

    # Save state
    save_state(state)

    # Write report to file
    try:
        os.makedirs(LOG_DIR, exist_ok=True)
        date_str = now.strftime("%Y-%m-%d")
        report_path = os.path.join(LOG_DIR, f"supervisor-health-{date_str}.md")
        with open(report_path, "w") as f:
            f.write(report.to_markdown())
        report.log(f"Report written to {report_path}")
    except Exception as e:
        report.log(f"Failed to write report: {e}", "WARN")

    return total_actions


# ============================================================
# Entry Point
# ============================================================

if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    try:
        run(dry_run=dry_run)
    except Exception as e:
        # Never fail the cron — catch all exceptions
        print(f"[FATAL] Pipeline health check failed: {e}", file=sys.stderr)
    sys.exit(0)