#!/usr/bin/env python3
"""
Paperclip Pipeline Monitor & Language Validator

Performs two functions:
1. P3-3: Language validation - rejects Korean content before publication
2. P3-4: Pipeline health monitoring - generates daily report

Usage:
  python3 ~/blog/agents/paperclip-pipeline-monitor.py [--validate] [--report]
  
  --validate: Check recent posts for Korean content (language validation)
  --report:   Generate pipeline health dashboard
  
  Default: runs both
"""

import json
import urllib.request
import os
import re
from datetime import datetime, timezone, timedelta
from collections import Counter

COMPANY_ID = "52c3998a-6f9c-4454-9ef4-2c2cd574961b"
BASE_URL = "http://127.0.0.1:3100/api"
HEADERS = {"X-Paperclip-Local-Board": "true", "Content-Type": "application/json"}
POSTS_DIR = "/home/ubuntu/blog/content/posts"
RESEARCH_DIR = "/home/ubuntu/blog/research"
REPORT_DIR = "/home/ubuntu/blog/logs"

# ============================================================
# API Helpers
# ============================================================

def api(method, url, data=None):
    req = urllib.request.Request(url, headers=HEADERS, method=method)
    if data:
        req.data = json.dumps(data).encode()
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode()[:500]
        return {"error": f"HTTP {e.code}", "body": body}
    except Exception as e:
        return {"error": str(e)}

def log(msg, level="INFO"):
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    line = f"[{ts}] [{level}] {msg}"
    print(line)

# ============================================================
# P3-3: Language Validation
# ============================================================

def has_korean(text, threshold=0.05):
    """Check if text has Korean characters above threshold ratio."""
    if not text:
        return False, 0.0
    korean_chars = sum(1 for c in text if '\u3131' <= c <= '\u3163' or '\uac00' <= c <= '\ud7a3')
    total_alpha = max(1, sum(1 for c in text if c.isalpha()))
    ratio = korean_chars / total_alpha
    return ratio > threshold, ratio

def validate_language():
    """Check recent blog posts for Korean content violations."""
    log("=" * 50)
    log("P3-3: Language Validation Check")
    log("=" * 50)
    
    if not os.path.exists(POSTS_DIR):
        log(f"Posts directory not found: {POSTS_DIR}", "ERROR")
        return
    
    violations = []
    total_checked = 0
    
    # Check all .md files, sorted by modification time (most recent first)
    files = sorted(
        [f for f in os.listdir(POSTS_DIR) if f.endswith('.md')],
        key=lambda f: os.path.getmtime(os.path.join(POSTS_DIR, f)),
        reverse=True
    )
    
    for filename in files:
        filepath = os.path.join(POSTS_DIR, filename)
        total_checked += 1
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            log(f"  Cannot read {filename}: {e}", "WARN")
            continue
        
        is_korean, ratio = has_korean(content, threshold=0.05)
        if is_korean:
            violations.append({
                "file": filename,
                "ratio": ratio,
                "path": filepath
            })
    
    log(f"Checked {total_checked} posts")
    log(f"Korean content violations: {len(violations)}")
    
    if violations:
        for v in violations:
            log(f"  VIOLATION: {v['file']} ({v['ratio']:.1%} Korean)", "WARN")
    
    return violations

# ============================================================
# P3-4: Pipeline Health Report
# ============================================================

def generate_report():
    """Generate pipeline health dashboard."""
    log("=" * 50)
    log("P3-4: Pipeline Health Report")
    log("=" * 50)
    
    now = datetime.now(timezone.utc)
    issues = api("GET", f"{BASE_URL}/companies/{COMPANY_ID}/issues")
    agents = api("GET", f"{BASE_URL}/companies/{COMPANY_ID}/agents")
    
    if isinstance(issues, dict) and "error" in issues:
        log(f"Failed to fetch issues: {issues['error']}", "ERROR")
        return
    if isinstance(agents, dict) and "error" in agents:
        log(f"Failed to fetch agents: {agents['error']}", "ERROR")
        return
    
    # Pipeline summary
    status_count = Counter(i.get('status') for i in issues)
    total = len(issues)
    
    # Agent health
    error_agents = [a for a in agents if a.get('status') == 'error']
    idle_agents = [a for a in agents if a.get('status') == 'idle']
    running_agents = [a for a in agents if a.get('status') == 'running']
    
    # Stale in_progress
    stale_hours = 4
    stale_issues = []
    for i in issues:
        if i.get('status') != 'in_progress':
            continue
        started = i.get('startedAt')
        if not started:
            continue
        try:
            started_dt = datetime.fromisoformat(started.replace("Z", "+00:00"))
            hours = (now - started_dt).total_seconds() / 3600
            if hours > stale_hours:
                stale_issues.append((i, hours))
        except:
            pass
    
    # Pipeline throughput (last 24h)
    done_24h = 0
    for i in issues:
        if i.get('status') == 'done' and i.get('completedAt'):
            try:
                completed = datetime.fromisoformat(i['completedAt'].replace("Z", "+00:00"))
                if (now - completed).total_seconds() < 86400:
                    done_24h += 1
            except:
                pass
    
    # Build report
    report_lines = [
        f"# Paperclip Pipeline Health Report",
        f"Generated: {now.strftime('%Y-%m-%d %H:%M UTC')}",
        f"",
        f"## Overview",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Total Issues | {total} |",
        f"| Backlog | {status_count.get('backlog', 0)} |",
        f"| Todo | {status_count.get('todo', 0)} |",
        f"| In Progress | {status_count.get('in_progress', 0)} |",
        f"| Done | {status_count.get('done', 0)} |",
        f"| Cancelled | {status_count.get('cancelled', 0)} |",
        f"| Error | {status_count.get('error', 0)} |",
        f"| Completed (24h) | {done_24h} |",
        f"",
        f"## Agent Health",
        f"| Agent | Status | Heartbeat | MaxConc | Model |",
        f"|-------|--------|-----------|---------|-------|",
    ]
    
    for a in sorted(agents, key=lambda x: x.get('name','')):
        name = a.get('name')
        status = a.get('status','?')
        rt = a.get('runtimeConfig') or {}
        hb = rt.get('heartbeat', {})
        hb_status = "ON" if hb.get('enabled') else "OFF"
        mc = hb.get('maxConcurrentRuns', 1)
        ac = a.get('adapterConfig') or {}
        model = ac.get('model', '?')
        report_lines.append(f"| {name} | {status} | {hb_status} | {mc} | {model} |")
    
    report_lines.extend([
        f"",
        f"## Alerts",
    ])
    
    if error_agents:
        report_lines.append(f"- CRITICAL: {len(error_agents)} agent(s) in error state")
        for a in error_agents:
            report_lines.append(f"  - {a.get('name')}")
    
    if stale_issues:
        report_lines.append(f"- WARNING: {len(stale_issues)} issue(s) stale >{stale_hours}h")
        for i, h in stale_issues:
            report_lines.append(f"  - {i.get('identifier','?')} ({h:.1f}h): {(i.get('title') or '')[:50]}")
    
    if not error_agents and not stale_issues:
        report_lines.append(f"- All clear. No errors or stale issues.")
    
    # Pipeline flow analysis
    research_done = sum(1 for i in issues if i.get('status') == 'done' and 'research:' in (i.get('title') or '').lower())
    write_done = sum(1 for i in issues if i.get('status') == 'done' and ('write:' in (i.get('title') or '').lower() or 'article:' in (i.get('title') or '').lower()))
    seo_done = sum(1 for i in issues if i.get('status') == 'done' and 'seo:' in (i.get('title') or '').lower())
    thumb_done = sum(1 for i in issues if i.get('status') == 'done' and ('thumbnail:' in (i.get('title') or '').lower() or 'cover:' in (i.get('title') or '').lower()))
    pub_done = sum(1 for i in issues if i.get('status') == 'done' and 'publish:' in (i.get('title') or '').lower())
    
    report_lines.extend([
        f"",
        f"## Pipeline Flow",
        f"| Stage | Completed | Backlog | In Progress |",
        f"|-------|-----------|---------|-------------|",
    ])
    
    stages = [('Research', 'research:'), ('Write', 'write:'), ('SEO', 'seo:'), ('Thumbnail', 'thumbnail:'), ('Publish', 'publish:')]
    for stage_name, prefix in stages:
        stage_issues = [i for i in issues if (i.get('title') or '').lower().startswith(prefix)]
        s_done = sum(1 for i in stage_issues if i.get('status') == 'done')
        s_backlog = sum(1 for i in stage_issues if i.get('status') == 'backlog')
        s_ip = sum(1 for i in stage_issues if i.get('status') == 'in_progress')
        report_lines.append(f"| {stage_name} | {s_done} | {s_backlog} | {s_ip} |")
    
    # Content quality: published posts on disk
    if os.path.exists(POSTS_DIR):
        post_count = len([f for f in os.listdir(POSTS_DIR) if f.endswith('.md')])
        report_lines.extend([
            f"",
            f"## Content Stats",
            f"| Metric | Value |",
            f"|--------|-------|",
            f"| Published posts on disk | {post_count} |",
        ])
    
    # Write report
    os.makedirs(REPORT_DIR, exist_ok=True)
    date_str = now.strftime('%Y-%m-%d')
    report_path = os.path.join(REPORT_DIR, f"pipeline-report-{date_str}.md")
    report_text = "\n".join(report_lines)
    
    with open(report_path, 'w') as f:
        f.write(report_text)
    
    log(f"Report saved to: {report_path}")
    
    # Also print summary
    print(f"\n{'='*50}")
    print(f"DASHBOARD: {now.strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"{'='*50}")
    print(f"  Total issues: {total}")
    print(f"  Done: {status_count.get('done',0)} | Todo: {status_count.get('todo',0)} | In-progress: {status_count.get('in_progress',0)}")
    print(f"  Backlog: {status_count.get('backlog',0)} | Cancelled: {status_count.get('cancelled',0)}")
    print(f"  Agents: {len(running_agents)} running, {len(idle_agents)} idle, {len(error_agents)} ERROR")
    print(f"  Stale issues (>{stale_hours}h): {len(stale_issues)}")
    print(f"  Completed 24h: {done_24h}")
    if error_agents:
        for a in error_agents:
            print(f"  ERROR: {a.get('name')} in error state!")
    if stale_issues:
        for i, h in stale_issues:
            print(f"  STALE: {i.get('identifier','?')} ({h:.1f}h)")
    
    return {
        "total": total,
        "done": status_count.get('done', 0),
        "error_agents": len(error_agents),
        "stale_issues": len(stale_issues),
        "completed_24h": done_24h
    }

# ============================================================
# Entry Point
# ============================================================

if __name__ == "__main__":
    import sys
    
    args = sys.argv[1:]
    run_validate = "--validate" in args or len(args) == 0
    run_report = "--report" in args or len(args) == 0
    
    if run_validate:
        violations = validate_language()
        if violations:
            log(f"Language validation: {len(violations)} Korean content violations found", "WARN")
        else:
            log("Language validation: All clear, no Korean content violations")
    
    if run_report:
        result = generate_report()
