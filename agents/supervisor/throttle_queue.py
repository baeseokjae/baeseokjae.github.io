#!/usr/bin/env python3
"""
throttle_queue.py
Run before each dispatch. Ensures only 1 queued topic is available per cycle.
- Restores previously throttled topics back to 'queued'
- Then keeps only the highest-priority 1 topic as 'queued'
- Moves surplus to 'queued_throttled'

This enforces exactly 1 post per dispatch cycle (= 3-hour intervals).
"""

import json
import os
import sys
from datetime import datetime, timezone

TOPICS_PATH = os.path.expanduser("~/blog/research/topics.json")
LOG_PATH = os.path.expanduser("~/blog/logs/throttle-queue.log")


def log(msg):
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_PATH, "a") as f:
        f.write(line + "\n")


def main():
    if not os.path.exists(TOPICS_PATH):
        log(f"ERROR: topics.json not found at {TOPICS_PATH}")
        sys.exit(1)

    with open(TOPICS_PATH, "r") as f:
        topics = json.load(f)

    original_queued = sum(
        1 for t in topics if isinstance(t, dict) and t.get("status") == "queued"
    )
    throttled_count = sum(
        1 for t in topics if isinstance(t, dict) and t.get("status") == "queued_throttled"
    )

    # Step 1: Restore previously throttled -> queued
    restored = 0
    for t in topics:
        if isinstance(t, dict) and t.get("status") == "queued_throttled":
            t["status"] = "queued"
            restored += 1

    # Step 2: Re-throttle — keep only 1 highest-priority queued
    queued = [t for t in topics if isinstance(t, dict) and t.get("status") == "queued"]

    if len(queued) <= 1:
        log(
            f"Queue OK: {len(queued)} queued (restored {restored} from throttled). "
            f"No throttling needed."
        )
        with open(TOPICS_PATH, "w") as f:
            json.dump(topics, f, indent=2, ensure_ascii=False)
        return

    # Sort by priority descending (highest priority first)
    queued.sort(key=lambda t: t.get("priority", 0), reverse=True)

    # Keep first, throttle the rest
    throttled_this_cycle = 0
    for t in queued[1:]:
        t["status"] = "queued_throttled"
        throttled_this_cycle += 1

    with open(TOPICS_PATH, "w") as f:
        json.dump(topics, f, indent=2, ensure_ascii=False)

    # Show what we kept
    kept = queued[0]
    log(
        f"Throttled pipeline: "
        f"{original_queued} queued → kept 1 ('{kept.get('slug', '?')}', "
        f"priority={kept.get('priority', '?')}), "
        f"throttled {throttled_this_cycle}, restored {restored} from prev cycle"
    )


if __name__ == "__main__":
    main()