#!/usr/bin/env python3
"""
Paperclip Auto-Reset Script (paperclip-auto-reset.py)

Monitors Paperclip agents for error states and automatically resets them.
Also detects stale in_progress issues (zombie tasks) and cleans them up.

This script is designed to be run as a cron job every 10 minutes.

Root causes addressed:
  - Agent error states with no auto-recovery (Supervisor lacks permission)
  - Stale execution locks (in_progress >4h with no executionRunId)
  - Zombie in_progress cluttering the pipeline
  - Platform-wide rate limit events (Anthropic weekly/session limits)

Usage:
  python3 ~/blog/agents/paperclip-auto-reset.py [--dry-run]
"""

import json
import urllib.request
import urllib.error
import sys
import os
import re
from datetime import datetime, timezone, timedelta

# ============================================================
# Configuration
# ============================================================
COMPANY_ID = "ab752c4f-0e8b-4669-8e76-2746d00ae8c9"
BASE_URL = "http://127.0.0.1:3100/api"
HEADERS = {
    "X-Paperclip-Local-Board": "true",
    "Content-Type": "application/json"
}

# Stale threshold: in_progress issues older than this are considered zombies
STALE_HOURS = 4

# Maximum consecutive error resets before escalating (prevent reset loops)
MAX_RESETS_PER_AGENT = 3
RESET_COOLDOWN_HOURS = 1  # Don't reset the same agent more than once per hour

# Disabled agents (decommissioned in Apr 2026 pipeline redesign) — skip reset, cancel their issues
DISABLED_AGENT_IDS = {
    "9e1b92e9-11dd-41ba-8398-b951549a3696",  # Supervisor (replaced by pipeline_health_check.py)
    "6dab6808-c362-4e11-819b-1f1647e84d40",  # SEO (Writer generates schema)
    "16f0b09a-d3f8-4885-aa2a-52e7d67d2267",  # Thumbnail (Writer runs gen_cover.py)
}

# Platform-wide rate limit detection
# Substrings that identify a rate/session limit error from Anthropic
PLATFORM_LIMIT_TRIGGERS = [
    "session limit", "weekly limit", "monthly limit",
    "you've hit your", "rate limit exceeded",
]

# Minimum fraction of error-state agents sharing the same rate-limit error to suppress
PLATFORM_LIMIT_THRESHOLD = 0.6  # 60%

# Log file
LOG_FILE = os.path.expanduser("~/blog/logs/auto-reset.log")

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

def log(msg, level="INFO"):
    """Log a message with timestamp."""
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    line = f"[{ts}] [{level}] {msg}"
    print(line)
    try:
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        with open(LOG_FILE, "a") as f:
            f.write(line + "\n")
    except Exception:
        pass

# ============================================================
# Reset State Tracker (prevents reset loops)
# ============================================================

STATE_FILE = os.path.expanduser("~/blog/logs/auto-reset-state.json")

def load_state():
    """Load reset state from file."""
    try:
        with open(STATE_FILE) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"resets": {}, "last_run": None}

def save_state(state):
    """Save reset state to file."""
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

# ============================================================
# Platform-Wide Rate Limit Detection
# ============================================================

def detect_platform_rate_limit(agents_in_error):
    """Check if 60%+ of error-state agents share the same rate-limit error.
    
    Uses heartbeat-run history to identify platform-wide Anthropic limit events
    (weekly/session/rate limits). When detected, suppresses individual agent resets
    that would be pointless and produce noise escalation issues.
    
    Handles both multi-agent (60% threshold) and single-agent (80% of own runs)
    rate-limit scenarios.
    
    Returns (is_platform_wide: bool, error_message: str|None, reset_time: str|None)
    """
    # Allow single-agent path to fall through to individual check below
    
    try:
        runs = api("GET", f"{BASE_URL}/companies/{COMPANY_ID}/heartbeat-runs?limit=20")
        if not isinstance(runs, list) or len(runs) < 3:
            return (False, None, None)
        
        agent_ids_in_error = {a.get('id') for a in agents_in_error}
        relevant = [r for r in runs if r.get('agentId') in agent_ids_in_error and r.get('error')]
        
        if len(relevant) < 3:
            return (False, None, None)
        
        # Count occurrences of each distinct rate-limit error
        error_counts = {}
        for r in relevant:
            err = r.get('error', '')
            if not err:
                continue
            err_lower = err.lower()
            is_limit = any(t in err_lower for t in PLATFORM_LIMIT_TRIGGERS)
            if is_limit:
                error_counts[err] = error_counts.get(err, 0) + 1
        
        if not error_counts:
            return (False, None, None)
        
        # Find the most common rate-limit error
        most_common = max(error_counts.items(), key=lambda x: x[1])
        common_err, count = most_common

        total_err = len(agent_ids_in_error)
        # For single-agent scenarios, use 80% of own runs threshold
        # For multi-agent scenarios, use 60% threshold
        threshold = 0.8 if total_err == 1 else PLATFORM_LIMIT_THRESHOLD
        relevant_count = len(relevant)
        if count >= int(relevant_count * threshold):
            # Fix: match times like "4:50am" (with colon) or "6pm" (without)
            reset_match = re.search(r'resets\s+(\d+(?::\d+)?[ap]m)\s*\(UTC\)', common_err)
            reset_time = reset_match.group(1) if reset_match else None
            return (True, common_err, reset_time)
        
        return (False, None, None)
    except Exception as e:
        log(f"Rate-limit check error: {e}", "DEBUG")
        return (False, None, None)

# ============================================================
# Core Functions
# ============================================================

def get_agents():
    """Get all agents with their current status."""
    agents = api("GET", f"{BASE_URL}/companies/{COMPANY_ID}/agents")
    if isinstance(agents, dict) and "error" in agents:
        log(f"Failed to get agents: {agents['error']}", "ERROR")
        return []
    return agents

def get_issues():
    """Get all issues."""
    issues = api("GET", f"{BASE_URL}/companies/{COMPANY_ID}/issues")
    if isinstance(issues, dict) and "error" in issues:
        log(f"Failed to get issues: {issues['error']}", "ERROR")
        return []
    return issues

def reset_agent(agent_id, agent_name):
    """Reset an agent from error to idle state using Board API."""
    # Try /api/agents/{id} first (Board-level access)
    result = api("PATCH", f"{BASE_URL}/agents/{agent_id}", {"status": "idle"})
    if "error" not in result:
        log(f"Reset agent {agent_name} ({agent_id[:8]}...) from error to idle", "ACTION")
        return True
    
    # Fallback: try company-scoped
    result2 = api("PATCH", f"{BASE_URL}/companies/{COMPANY_ID}/agents/{agent_id}", {"status": "idle"})
    if "error" not in result2:
        log(f"Reset agent {agent_name} via company route", "ACTION")
        return True
    
    log(f"Failed to reset {agent_name}: {result.get('error')}", "ERROR")
    return False

def wakeup_agent(agent_id, agent_name):
    """Send wakeup signal to an agent."""
    # Valid source values: "timer", "assignment", "on_demand", "automation"
    result = api("POST", f"{BASE_URL}/agents/{agent_id}/wakeup", {
        "source": "automation",
        "forceFreshSession": True
    })
    if "error" not in result and "id" in result:
        log(f"Woke up agent {agent_name} (run: {result.get('id', 'N/A')[:8]}...)", "ACTION")
        return True
    else:
        log(f"Wakeup failed for {agent_name}: {result.get('error', result.get('body', 'unknown'))}", "WARN")
        return False

def cancel_issue(issue_id, issue_identifier):
    """Cancel an issue."""
    result = api("PATCH", f"{BASE_URL}/issues/{issue_id}", {"status": "cancelled"})
    if "error" not in result:
        return True
    # Fallback
    result2 = api("PATCH", f"{BASE_URL}/companies/{COMPANY_ID}/issues/{issue_id}", {"status": "cancelled"})
    if "error" not in result2:
        return True
    log(f"Failed to cancel {issue_identifier}: {result.get('error')}", "ERROR")
    return False

# ============================================================
# Main Logic
# ============================================================

def run(dry_run=False):
    """Main auto-reset routine."""
    state = load_state()
    now = datetime.now(timezone.utc)
    actions_taken = 0
    
    log("=" * 50)
    log(f"Auto-reset check starting {'(DRY RUN)' if dry_run else ''}")
    
    # --------------------------------------------------------
    # 0. Detect platform-wide rate limit BEFORE any reset actions
    # --------------------------------------------------------
    agents = get_agents()
    error_agents = [a for a in agents if a.get('status') == 'error' and a.get('id') not in DISABLED_AGENT_IDS]
    
    is_platform_limit, limit_error, limit_reset_time = detect_platform_rate_limit(error_agents)
    
    if is_platform_limit:
        reset_msg = f"resets {limit_reset_time} UTC" if limit_reset_time else "at unknown time"
        log(f"Platform-wide rate limit detected! {len(error_agents)} agent(s) hitting same error. "
            f"Suppressing resets until {reset_msg}.", "WARN")
        log(f"Limit error: {limit_error[:200]}", "WARN")
        
        # Skip directly to steps that don't involve resetting:
        # Step 2 (cleanup) + Step 3 (reporting)
        # But do NOT reset any agents or create escalation issues
    else:
        # --------------------------------------------------------
        # 1. Reset error-state agents (normal path)
        # --------------------------------------------------------
        log("Step 1: Checking for error-state agents...")
        
        # Skip disabled (decommissioned) agents entirely
        active_agents = [a for a in agents if a.get('id') not in DISABLED_AGENT_IDS]
        disabled_in_error = [a for a in agents if a.get('id') in DISABLED_AGENT_IDS and a.get('status') == 'error']
        if disabled_in_error:
            for da in disabled_in_error:
                log(f"Skipping disabled agent {da.get('name')} — forcing to idle", "INFO")
                reset_agent(da['id'], da['name'])
        
        if not error_agents:
            log("No agents in error state. Clean!")
        else:
            log(f"Found {len(error_agents)} agent(s) in error state")
            for agent in error_agents:
                name = agent.get('name', 'Unknown')
                aid = agent.get('id')
                
                # Check reset cooldown
                reset_history = state.get("resets", {}).get(aid, [])
                recent_resets = [r for r in reset_history 
                               if datetime.fromisoformat(r["time"].replace("Z", "+00:00")) > now - timedelta(hours=RESET_COOLDOWN_HOURS)]
                
                if len(recent_resets) >= MAX_RESETS_PER_AGENT:
                    log(f"ESCALATE: {name} has been reset {len(recent_resets)} times in {RESET_COOLDOWN_HOURS}h. Manual intervention needed!", "ESCALATE")
                    # Create a Paperclip issue for escalation
                    if not dry_run:
                        escalation = api("POST", f"{BASE_URL}/companies/{COMPANY_ID}/issues", {
                            "title": f"[Auto-Reset] {name} recurring error — {len(recent_resets)} resets in {RESET_COOLDOWN_HOURS}h",
                            "description": f"Agent {name} ({aid}) has been auto-reset {len(recent_resets)} times in the last {RESET_COOLDOWN_HOURS} hours. "
                                         f"This indicates a persistent underlying issue that cannot be resolved by automatic reset. "
                                         f"Last reset times: {json.dumps(recent_resets[-3:])}",
                            "priority": "high",
                            "status": "todo"
                        })
                        if "error" not in escalation:
                            log(f"Created escalation issue: {escalation.get('identifier', 'N/A')}", "ACTION")
                    continue
                
                if dry_run:
                    log(f"[DRY RUN] Would reset {name} from error to idle")
                    continue
                
                success = reset_agent(aid, name)
                if success:
                    # Wake up the agent after reset
                    wakeup_agent(aid, name)
                    # Record reset
                    state.setdefault("resets", {}).setdefault(aid, []).append({
                        "time": now.isoformat(),
                        "agent": name,
                        "from_status": "error"
                    })
                    actions_taken += 1
    
    # --------------------------------------------------------
    # 2. Cancel issues assigned to disabled agents + clean up zombies
    # --------------------------------------------------------
    log("Step 2: Checking for disabled-agent issues and stale in_progress...")
    issues = get_issues()
    
    # Cancel any non-done issues assigned to disabled agents
    disabled_issues = [i for i in issues 
                       if i.get('status') not in ('done', 'cancelled') 
                       and i.get('assigneeId') in DISABLED_AGENT_IDS]
    if disabled_issues:
        log(f"Found {len(disabled_issues)} issues assigned to disabled agents — cancelling")
        for di in disabled_issues:
            identifier = di.get('identifier', di.get('id', 'N/A')[:8])
            title = (di.get('title') or '')[:50]
            if cancel_issue(di['id'], identifier):
                log(f"Cancelled disabled-agent issue: {identifier} - {title}", "ACTION")
                actions_taken += 1
    
    in_progress = [i for i in issues if i.get('status') == 'in_progress']
    
    if not in_progress:
        log("No in_progress issues. Clean!")
    else:
        stale_count = 0
        for issue in in_progress:
            started = issue.get('startedAt')
            has_exec = bool(issue.get('executionRunId'))
            
            if not started:
                continue
            
            try:
                started_dt = datetime.fromisoformat(started.replace("Z", "+00:00"))
                hours_stale = (now - started_dt).total_seconds() / 3600
            except:
                continue
            
            # Flag as zombie if: no executionRunId AND stale >4h
            if not has_exec and hours_stale > STALE_HOURS:
                stale_count += 1
                identifier = issue.get('identifier', 'N/A')
                title = (issue.get('title') or '')[:50]
                
                if dry_run:
                    log(f"[DRY RUN] Would cancel zombie: {identifier} ({hours_stale:.1f}h stale, no exec run) - {title}")
                    continue
                
                success = cancel_issue(issue['id'], identifier)
                if success:
                    log(f"Cancelled zombie issue {identifier} ({hours_stale:.1f}h stale, no exec run)", "ACTION")
                    actions_taken += 1
            
            # Also flag if stale >12h even WITH executionRunId (truly stuck)
            elif has_exec and hours_stale > 12:
                stale_count += 1
                identifier = issue.get('identifier', 'N/A')
                title = (issue.get('title') or '')[:50]
                
                if dry_run:
                    log(f"[DRY RUN] Would cancel stuck: {identifier} ({hours_stale:.1f}h stale, has exec run) - {title}")
                    continue
                
                success = cancel_issue(issue['id'], identifier)
                if success:
                    log(f"Cancelled stuck issue {identifier} ({hours_stale:.1f}h stale, has exec run)", "ACTION")
                    actions_taken += 1
        
        if stale_count == 0:
            log("No stale in_progress issues. Clean!")
        else:
            log(f"Found {stale_count} stale in_progress issue(s)")

    # --------------------------------------------------------
    # 3. Check pipeline health (quick metrics)
    # --------------------------------------------------------
    log("Step 3: Pipeline health check...")
    from collections import Counter
    status_count = Counter(i.get('status') for i in issues)
    error_issues = [i for i in issues if i.get('status') == 'error']
    
    # If platform-wide limit, note it in the report
    if is_platform_limit:
        reset_msg = f"resets {limit_reset_time} UTC" if limit_reset_time else "at unknown time"
        log(f"PLATFORM-WIDE LIMIT: {len(error_agents)} agent(s) down — {reset_msg}", "WARN")

    log(f"Pipeline: done={status_count.get('done',0)} backlog={status_count.get('backlog',0)} "
        f"todo={status_count.get('todo',0)} in_progress={status_count.get('in_progress',0)} "
        f"cancelled={status_count.get('cancelled',0)} error={status_count.get('error',0)}")
    log(f"Agents: {len(agents)} total, {len(error_agents)} in error state")
    
    if error_issues:
        log(f"ERROR ISSUES FOUND: {len(error_issues)}", "WARN")
        for i in error_issues[:5]:
            log(f"  {i.get('identifier','?')}: {(i.get('title') or '')[:60]}")

    # Save state
    state["last_run"] = now.isoformat()
    save_state(state)
    
    log(f"Auto-reset complete. Actions taken: {actions_taken}")
    return actions_taken

# ============================================================
# Entry Point
# ============================================================

if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    actions = run(dry_run=dry_run)
    sys.exit(0 if actions >= 0 else 1)
