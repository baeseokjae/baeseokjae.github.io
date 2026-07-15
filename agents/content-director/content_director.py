#!/usr/bin/env python3
"""ContentDirector automation for article pipeline dispatch and seeding."""

import argparse
import json
import os
import re
from datetime import datetime, timezone, timedelta
from pathlib import Path
import urllib.error
import urllib.parse
import urllib.request


COMPANY_ID = "52c3998a-6f9c-4454-9ef4-2c2cd574961b"
PROJECT_ID = "01417190-b574-464e-8bb8-f5015f787ef0"
GOAL_ID = "45dadd15-aa5a-4e7a-b077-7afa5005bd89"

CONTENT_DIRECTOR_ID = "4672ff4c-82e9-4dcb-b406-24aa4038043b"
RESEARCHER_ID = "3d8c41a6-2b8f-4421-b38c-ea74d8d293db"
WRITER_ID = "893607c4-da4b-48a7-afc1-483d3b08255f"
PUBLISHER_ID = "0c30852a-21dd-4608-bbf5-c3aedc69225d"
STRATEGIST_ID = "407a6c0d-6e14-4189-8de0-484c3236850d"

DISABLED_AGENT_IDS = {
    "6dab6808-0827-4f7c-bd5a-67b9d0f4d8b2",  # SEO
    "16f0b09a-d49e-4ed7-84fa-d45a04c72c4a",  # Thumbnail
    "bf9adfce-4e5f-4c4e-bb6c-8a35086e15b1",  # Supervisor
}

# The pipeline intentionally throttles topics to one queued item before each
# dispatch so publication cadence stays near 1 article / 3 hours.  Treat one
# queued topic as healthy; otherwise ContentDirector and the health check fight
# the throttle and wake Strategist every cycle.
LOW_WATERMARK = 1
SEED_BATCH_SIZE = 8

BASE_DIR = Path.home() / "blog"
STRATEGY_PATH = BASE_DIR / "state" / "strategy.json"
TOPICS_PATH = BASE_DIR / "research" / "topics.json"
RUN_LOG_DIR = BASE_DIR / "state" / "content_director_runs"

BASE_URL = os.environ.get("PAPERCLIP_API_URL", "http://127.0.0.1:3100").rstrip("/")
API_KEY = os.environ.get("PAPERCLIP_API_KEY", "").strip()

RUN_ID = os.environ.get("PAPERCLIP_RUN_ID", "").strip()

BASE_HEADERS = {
    "X-Paperclip-Local-Board": "true",
    "Content-Type": "application/json",
}
# Use local-board auth for all local automation.  Do NOT add Authorization here:
# Paperclip enforces "agent can only invoke itself" when a bearer token is
# present, which breaks ContentDirector -> worker wakeups with HTTP 403.
if RUN_ID:
    BASE_HEADERS["X-Paperclip-Run-Id"] = RUN_ID


def log(message, level="INFO"):
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    print(f"[{ts}] [{level}] {message}")


def run_log(lines):
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    RUN_LOG_DIR.mkdir(parents=True, exist_ok=True)
    path = RUN_LOG_DIR / f"{ts}-content-director.md"
    with path.open("w", encoding="utf-8") as fp:
        fp.write("# ContentDirector Run\n")
        fp.write(f"Timestamp: {ts}\n\n")
        fp.write("## Log\n")
        for line in lines:
            fp.write(f"- {line}\n")
    return path


def api_request(method, path, params=None, data=None):
    query = ""
    if params:
        query = f"?{urllib.parse.urlencode(params, doseq=True)}"
    url = f"{BASE_URL}{path}{query}"
    payload = json.dumps(data).encode("utf-8") if data is not None else None
    req = urllib.request.Request(url=url, data=payload, method=method)
    for k, v in BASE_HEADERS.items():
        req.add_header(k, v)

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            content = resp.read().decode("utf-8")
            if not content:
                return True, None
            return True, json.loads(content)
    except urllib.error.HTTPError as e:
        try:
            body = e.read().decode("utf-8", errors="replace")
        except Exception:
            body = ""
        return (
            False,
            {"error": f"HTTP {e.code}", "body": body[:1000]},
        )
    except Exception as e:
        return False, {"error": str(e)}


def api_list_issues(status=None, parent_id=None, params=None):
    query = {}
    if status:
        query["status"] = status
    if parent_id is not None:
        query["parentId"] = parent_id
    if params:
        query.update(params)
    ok, result = api_request("GET", f"/api/companies/{COMPANY_ID}/issues", query)
    if not ok:
        log(f"Failed to load issues: {result}", "ERROR")
        return []
    if isinstance(result, list):
        return result
    return []


def api_create_issue(payload):
    ok, result = api_request(
        "POST",
        f"/api/companies/{COMPANY_ID}/issues",
        data=payload,
    )
    if not ok:
        log(f"Create issue failed: {result}", "ERROR")
        return None
    if isinstance(result, dict) and "error" in result:
        log(f"Create issue API error: {result}", "ERROR")
        return None
    return result


def api_patch_issue_any(issue_id, payload):
    for path in (
        f"/api/issues/{issue_id}",
        f"/api/companies/{COMPANY_ID}/issues/{issue_id}",
    ):
        ok, result = api_request("PATCH", path, data=payload)
        if not ok:
            continue
        if isinstance(result, dict) and "error" in result:
            continue
        return result or {}
    return None


def api_wakeup_agent(agent_id, source="on_demand"):
    payload = {
        "source": source,
        "triggerDetail": "manual",
        "forceFreshSession": True,
    }
    ok, result = api_request("POST", f"/api/agents/{agent_id}/wakeup", data=payload)
    if ok and not (isinstance(result, dict) and result.get("error")):
        return True
    log(f"Wakeup failed for {agent_id}: {result}", "ERROR")
    return False


def load_json(path):
    try:
        with path.open("r", encoding="utf-8") as fp:
            return json.load(fp)
    except Exception as e:
        raise RuntimeError(f"Failed to read {path}: {e}")


def save_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fp:
        json.dump(payload, fp, indent=2, ensure_ascii=False)


def count_status(topics, status):
    return sum(1 for t in topics if isinstance(t, dict) and t.get("status") == status)


def parse_description_for_meta(description):
    meta = {}
    if not description:
        return meta
    for line in str(description).splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip().lower()
        if key in {"slug", "keyword", "type"}:
            meta[key] = value.strip()
    return meta


def build_issue_description(topic):
    slug = (topic.get("slug") or "").strip()
    keyword = (topic.get("keyword") or "").strip()
    _type = (topic.get("type") or "").strip()
    return f"slug: {slug}\nkeyword: {keyword}\ntype: {_type}"


def select_priority(topics):
    return sorted(topics, key=lambda t: t.get("priority", 0), reverse=True)


def choose_parent_target(topics, article):
    article_id = article.get("identifier") or ""
    article_parent = article.get("parentId")
    article_title = article.get("title", "").strip()
    article_meta = parse_description_for_meta(article.get("description") or "")
    slug = article_meta.get("slug")

    matches = []
    for idx, topic in enumerate(topics):
        if not isinstance(topic, dict):
            continue
        if topic.get("status") not in {"seeded", "writing", "published"}:
            continue
        if topic.get("paperclip_issue") == article_id:
            return topic
        if article_parent and topic.get("paperclip_issue") == article_parent:
            return topic
        if slug and topic.get("slug") == slug:
            matches.append((idx, topic))
        elif article_title and topic.get("title") == article_title:
            matches.append((idx, topic))

    if not matches:
        return None
    matches.sort(key=lambda m: m[0])
    return matches[0][1]


def identifier_to_number(issue):
    identifier = issue.get("identifier", "")
    match = re.search(r"(\d+)$", identifier or "")
    if match:
        return int(match.group(1))
    return 10_000_000_000


def parse_frontmatter_paths(post_path):
    if not post_path.exists():
        return None, None

    schema = None
    cover_image = None
    in_frontmatter = False
    in_cover = False
    try:
        with post_path.open("r", encoding="utf-8") as fp:
            for line in fp:
                line = line.rstrip("\n")
                if line.strip() == "---":
                    in_frontmatter = not in_frontmatter
                    if not in_frontmatter:
                        break
                    continue
                if not in_frontmatter:
                    continue

                if re.match(r"^\s*schema:\s*", line):
                    schema = line.split(":", 1)[1].strip().strip('"').strip("'")
                    in_cover = False
                    continue

                if re.match(r"^\s*cover:\s*$", line):
                    in_cover = True
                    continue
                if in_cover and re.match(r"^\s*image:\s*", line):
                    cover_image = line.split(":", 1)[1].strip().strip('"').strip("'")
                    continue
                if in_cover and re.match(r"^\S", line):
                    in_cover = False
    except Exception:
        return None, None

    if schema and schema.startswith("schema-"):
        schema_file = BASE_DIR / "layouts" / "partials" / f"{schema}.html"
    elif schema:
        schema_file = BASE_DIR / "layouts" / "partials" / f"{schema}.html"
    else:
        schema_file = None

    if cover_image and cover_image.startswith("/"):
        image_file = BASE_DIR / "static" / cover_image.lstrip("/")
    elif cover_image:
        image_file = BASE_DIR / "static" / "images" / cover_image
    else:
        image_file = None

    return schema_file, image_file


def has_required_files(topic_or_article, topic_slug=None):
    meta = parse_description_for_meta(topic_or_article.get("description") or "")
    slug = topic_slug or meta.get("slug")
    if not slug:
        return False

    post = BASE_DIR / "content" / "posts" / f"{slug}.md"
    if not post.exists():
        return False

    schema_file, image_file = parse_frontmatter_paths(post)
    if schema_file is None:
        schema_file = BASE_DIR / "layouts" / "partials" / f"schema-{slug}.html"
    if image_file is None:
        image_file = BASE_DIR / "static" / "images" / f"{slug}.png"

    image_ok = image_file.exists()
    if not image_ok and slug:
        for ext in (".png", ".jpg", ".jpeg", ".webp"):
            if (BASE_DIR / "static" / "images" / f"{slug}{ext}").exists():
                image_ok = True
                break

    return post.exists() and schema_file.exists() and image_ok


def create_article_issue(topic):
    payload = {
        "title": topic.get("title", "").strip(),
        "description": build_issue_description(topic),
        "goalId": GOAL_ID,
        "projectId": PROJECT_ID,
        "status": "backlog",
    }
    return api_create_issue(payload)


def create_subtask_issue(parent, topic, prefix):
    payload = {
        "title": f"{prefix}: {topic.get('title', '').strip()}",
        "description": build_issue_description(topic),
        "goalId": GOAL_ID,
        "projectId": PROJECT_ID,
        "parentId": parent.get("id"),
        "status": "backlog",
    }
    return api_create_issue(payload)


def set_issue_status_and_assignee(
    issue_id, status=None, assignee=None, clear_assignee=False
):
    payload = {}
    if status is not None:
        payload["status"] = status
    if assignee is not None:
        payload["assigneeAgentId"] = assignee
    elif clear_assignee:
        payload["assigneeAgentId"] = None

    if not payload:
        return None
    return api_patch_issue_any(issue_id, payload)


def cancel_issue(issue_id):
    return set_issue_status_and_assignee(issue_id, status="cancelled")


def get_child_issues(parent_id):
    return api_list_issues(parent_id=parent_id)


def get_project_goal_parent_articles(status):
    return [
        issue
        for issue in api_list_issues(status=status)
        if issue.get("parentId") is None
        and issue.get("projectId") == PROJECT_ID
        and issue.get("goalId") == GOAL_ID
    ]


def is_relevant_work_issue(issue):
    title = (issue.get("title") or "").strip()
    if not (title.startswith("Research:") or title.startswith("Write:") or title.startswith("Publish:")):
        return False
    # Restrict to this blog project to avoid blocking on unrelated workflows.
    return (
        issue.get("projectId") in (None, PROJECT_ID)
        and issue.get("goalId") in (None, GOAL_ID)
    )


def stage_from_children(children):
    def latest_for(prefix):
        matches = [
            child
            for child in children
            if (child.get("title") or "").startswith(prefix + ":")
        ]
        if not matches:
            return None
        matches = sorted(
            matches,
            key=lambda item: item.get("updatedAt", "0"),
            reverse=True,
        )
        return matches[0]

    return latest_for("Research"), latest_for("Write"), latest_for("Publish")


def statuses_from_children(children, prefix):
    return {
        child.get("status")
        for child in children
        if (child.get("title") or "").startswith(prefix + ":")
    }


def wake_strategy_if_needed():
    if api_wakeup_agent(STRATEGIST_ID, "on_demand"):
        log("Woke Strategist due queue watermark check.", "ACTION")


def run_morning_seeding(topics):
    actions = []
    dirty = False
    queued_count = count_status(topics, "queued")
    actions.append(f"queued_topics={queued_count}")

    if queued_count < LOW_WATERMARK:
        actions.append(f"Queue below LOW_WATERMARK={LOW_WATERMARK}; waking Strategist and exiting")
        wake_strategy_if_needed()
        return actions, False

    queued = [t for t in topics if isinstance(t, dict) and t.get("status") == "queued"]
    selected = select_priority(queued)[:SEED_BATCH_SIZE]
    seeded = 0
    for topic in selected:
        title = (topic.get("title") or "").strip()
        if not title:
            continue

        parent = create_article_issue(topic)
        if not parent or not parent.get("id"):
            actions.append(f"FAILED: article create failed for '{title}'")
            continue

        sub_ok = True
        for prefix in ("Research", "Write", "Publish"):
            child = create_subtask_issue(parent, topic, prefix)
            if not child or not child.get("id"):
                actions.append(f"FAILED: {prefix} issue create for '{title}'")
                sub_ok = False

        if sub_ok:
            topic["status"] = "seeded"
            topic["paperclip_issue"] = parent.get("identifier") or parent.get("id")
            seeded += 1
            actions.append(f"Seeded: {title} -> {parent.get('identifier', parent.get('id'))}")
            dirty = True
        else:
            actions.append(f"Seeded incomplete, skipped status update: {title}")

    actions.append(f"Seeded {seeded} topics")
    return actions, dirty


def is_busy_with_research_or_write():
    blocked = []
    for issue in api_list_issues(status="in_progress") + api_list_issues(status="todo"):
        if not is_relevant_work_issue(issue):
            continue
        assignee = issue.get("assigneeAgentId")
        if assignee in DISABLED_AGENT_IDS:
            result = cancel_issue(issue.get("id"))
            if result is None:
                log(f"Could not cancel disabled-agent issue {issue.get('identifier')}", "WARN")
            else:
                log(f"Cancelled disabled-agent issue {issue.get('identifier')} for {assignee}", "ACTION")
            continue
        blocked.append(issue)
    if blocked:
        log(
            "Research/Write/Publish active, skipping.",
            "INFO",
        )
        return True
    return False


def recover_stuck_articles(topics):
    actions = []
    in_progress_articles = get_project_goal_parent_articles("in_progress")
    terminal_statuses = {"done", "cancelled"}

    for article in in_progress_articles:
        children = get_child_issues(article.get("id"))
        if not children:
            continue

        research = statuses_from_children(children, "Research")
        write = statuses_from_children(children, "Write")
        publish = statuses_from_children(children, "Publish")

        write_done = bool(write) and write <= terminal_statuses
        research_done = bool(research) and research <= terminal_statuses
        publish_terminal = not publish or publish <= terminal_statuses

        if not (write_done and research_done and publish_terminal):
            continue

        # Publish is done -> mark article done
        if "done" in publish:
            result = set_issue_status_and_assignee(article.get("id"), status="done")
            if result is not None:
                actions.append(f"Recovered article done: {article.get('identifier')}")
            else:
                actions.append(f"Recover failed marking done: {article.get('identifier')}")
            continue

        publish_issue = stage_from_children(children)[2]
        if publish_issue is None:
            # create a new publish issue and assign Publisher
            new_publish = create_subtask_issue(
                article,
                {
                    "title": article.get("title", ""),
                    "slug": parse_description_for_meta(article.get("description") or {}).get("slug", ""),
                    "keyword": parse_description_for_meta(article.get("description") or {}).get("keyword", ""),
                    "type": parse_description_for_meta(article.get("description") or {}).get("type", ""),
                },
                "Publish",
            )
            if new_publish and new_publish.get("id"):
                set_issue_status_and_assignee(
                    new_publish["id"],
                    status="todo",
                    assignee=PUBLISHER_ID,
                )
                actions.append(
                    f"Recovery created missing publish issue for {article.get('identifier')}"
                )
            else:
                actions.append(
                    f"Recovery failed creating publish issue for {article.get('identifier')}"
                )
            continue

        files_ready = has_required_files(article)
        if files_ready:
            updated = set_issue_status_and_assignee(
                publish_issue.get("id"),
                status="todo",
                assignee=PUBLISHER_ID,
            )
            if updated is not None:
                actions.append(
                    f"Recovery reassigned cancelled publish {publish_issue.get('identifier')} -> Publisher"
                )
            else:
                actions.append(
                    f"Recovery failed to reassign publish {publish_issue.get('identifier')} -> Publisher"
                )
        else:
            new_publish = create_subtask_issue(
                article,
                {
                    "title": article.get("title", ""),
                    "slug": parse_description_for_meta(article.get("description") or {}).get("slug", ""),
                    "keyword": parse_description_for_meta(article.get("description") or {}).get("keyword", ""),
                    "type": parse_description_for_meta(article.get("description") or {}).get("type", ""),
                },
                "Publish",
            )
            if new_publish and new_publish.get("id"):
                set_issue_status_and_assignee(
                    new_publish["id"],
                    status="todo",
                    assignee=PUBLISHER_ID,
                )
                actions.append(
                    f"Recovery recreated publish issue for {article.get('identifier')} -> Publisher"
                )
            else:
                actions.append(
                    f"Recovery failed recreating publish for {article.get('identifier')}"
                )
    return actions


def dispatch_one_article(topics):
    dirty = False
    actions = []
    backlog_articles = get_project_goal_parent_articles("backlog")
    if not backlog_articles:
        actions.append("No backlog article to dispatch")
        return actions, dirty
    backlog_articles.sort(key=identifier_to_number)
    article = backlog_articles[0]

    children = get_child_issues(article.get("id"))
    research_issue, write_issue, publish_issue = stage_from_children(children)

    research_status = research_issue.get("status") if research_issue else None
    write_status = write_issue.get("status") if write_issue else None
    publish_status = publish_issue.get("status") if publish_issue else None

    stage = None
    if research_status in (None, "backlog", "todo"):
        stage = "research"
    elif research_status == "done" and write_status in (None, "backlog", "todo"):
        stage = "write"
    elif research_status == "done" and write_status == "done" and publish_status in (None, "backlog", "todo"):
        stage = "publish"
    elif research_status == "done" and write_status == "done" and publish_status == "done":
        stage = "done"
    else:
        stage = "unknown"

    if stage == "done":
        result = set_issue_status_and_assignee(article.get("id"), status="done")
        if result is not None:
            actions.append(f"Dispatched article complete, marked done: {article.get('identifier')}")
            topic = choose_parent_target(topics, article)
            if topic and topic.get("status") != "published":
                topic["status"] = "published"
                dirty = True
        return actions, dirty

    if stage == "unknown":
        actions.append(
            f"No valid dispatch stage for {article.get('identifier')} (research={research_status}, write={write_status}, publish={publish_status})"
        )
        return actions, dirty

    target_issue = {
        "research": research_issue,
        "write": write_issue,
        "publish": publish_issue,
    }[stage]
    assignee = {
        "research": RESEARCHER_ID,
        "write": WRITER_ID,
        "publish": PUBLISHER_ID,
    }[stage]

    if not target_issue or not target_issue.get("id"):
        actions.append(f"No {stage} issue found for {article.get('identifier')}")
        return actions, dirty

    if stage == "research":
        parent_update = set_issue_status_and_assignee(
            article.get("id"), status="in_progress", assignee=CONTENT_DIRECTOR_ID
        )
        if parent_update is None:
            actions.append(f"Failed to set parent in_progress: {article.get('identifier')}")
            return actions, dirty

    issue_update = set_issue_status_and_assignee(target_issue.get("id"), status="todo", assignee=assignee)
    if issue_update is None:
        actions.append(f"Failed to dispatch {stage} for {article.get('identifier')}")
        reverted = set_issue_status_and_assignee(
            article.get("id"), status="backlog", clear_assignee=True
        )
        if reverted is None:
            actions.append(
                f"CRITICAL: Could not revert parent {article.get('identifier')} after failed dispatch"
            )
        else:
            actions.append(f"Reverted parent to backlog for {article.get('identifier')}")
        return actions, dirty

    topic = choose_parent_target(topics, article)
    if topic and topic.get("status") != "writing":
        topic["status"] = "writing"
        actions.append(f"Updated topic status to writing for {topic.get('slug','(missing slug)')}")
        dirty = True

    actions.append(
        f"Dispatched {stage} stage for {article.get('identifier')} to "
        f"{'researcher' if stage == 'research' else 'writer' if stage == 'write' else 'publisher'}"
    )

    if stage == "research":
        api_wakeup_agent(RESEARCHER_ID, "on_demand")

    return actions, dirty


def run_dispatch(topics):
    actions = []
    dirty = False
    queued_count = count_status(topics, "queued")
    actions.append(f"queued_topics={queued_count}")
    if queued_count < LOW_WATERMARK:
        wake_strategy_if_needed()

    if is_busy_with_research_or_write():
        actions.append("Research/Write/Publish active; skipping dispatch.")
        return actions, dirty

    actions.extend(recover_stuck_articles(topics))
    dispatch_actions, changed = dispatch_one_article(topics)
    actions.extend(dispatch_actions)
    return actions, dirty or changed


def main():
    parser = argparse.ArgumentParser(description="Run ContentDirector routines.")
    parser.add_argument(
        "--routine",
        choices=["morning", "dispatch", "auto"],
        default="dispatch",
        help="Run mode. morning runs seeding only. dispatch runs pipeline handoff.",
    )
    parser.add_argument(
        "--routine-utc-hour",
        type=int,
        default=None,
        help="Internal helper for determining auto mode (for testing).",
    )
    args = parser.parse_args()

    routine = args.routine
    if routine == "auto":
        now = datetime.now(timezone.utc)
        if args.routine_utc_hour is not None:
            now_hour = args.routine_utc_hour
        else:
            now_hour = now.hour
        # 06:00 KST maps to 21:00 UTC
        if now_hour == 21:
            routine = "morning"
        else:
            routine = "dispatch"

    try:
        strategy = load_json(STRATEGY_PATH)
    except Exception as e:
        strategy = {}
        log(str(e), "ERROR")

    if strategy:
        log(f"strategy.json loaded (phase={strategy.get('current_phase', 'n/a')})")
    else:
        log("strategy.json not loaded; continuing with fallback defaults", "WARN")

    try:
        topics = load_json(TOPICS_PATH)
    except Exception as e:
        log(str(e), "ERROR")
        return

    if not isinstance(topics, list):
        log(f"topics.json invalid format: expected list, got {type(topics).__name__}", "ERROR")
        return

    actions = [f"Routine: {routine}"]
    changed = False

    if routine == "morning":
        run_actions, dirty = run_morning_seeding(topics)
        actions.extend(run_actions)
    else:
        run_actions, dirty = run_dispatch(topics)
        actions.extend(run_actions)

    if dirty and isinstance(topics, list):
        save_json(TOPICS_PATH, topics)

    for action in actions:
        log(action)

    log_path = run_log(actions)
    log(f"Run log saved: {log_path}")


if __name__ == "__main__":
    main()
