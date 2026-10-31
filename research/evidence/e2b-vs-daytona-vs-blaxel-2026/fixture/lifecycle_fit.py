#!/usr/bin/env python3
"""Offline lifecycle-fit check for E2B / Daytona / Blaxel.

Reads capability-matrix.json (documented flags transcribed from vendor docs on
the checked_at date) and workloads.json (your requirements), then reports which
documented option satisfies each requirement.

What this does NOT do: it never calls a provider, never measures latency, cost
or reliability, and never infers a capability a vendor page does not state. A
"meets" result means the documentation claims the flag, nothing more.

Usage:
    python3 lifecycle_fit.py [--matrix capability-matrix.json] [--workloads workloads.json]
                             [--json fit-report.json]
"""

import argparse
import json
import pathlib
import sys

FLAG_LABELS = {
    "pause_resume": "pause/resume between sessions",
    "memory_on_pause": "in-memory process state survives the pause",
    "filesystem_on_pause": "filesystem survives the pause",
    "archive_filesystem_only": "filesystem-only archive lifecycle",
    "fork": "fork/snapshot into another sandbox",
}


def load(path: pathlib.Path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def evaluate(option, profile):
    caps = option["capabilities"]
    misses, unverified = [], []
    for flag, required in profile["requires"].items():
        if not required:
            continue
        if flag not in caps:
            unverified.append(f"{flag} (not documented on the checked page)")
        elif caps[flag] is not True:
            misses.append(f"{FLAG_LABELS.get(flag, flag)} is not documented as supported")
    window = caps.get("continuous_runtime_hours")
    needed = profile.get("max_single_session_hours")
    runtime_note = None
    if needed is not None:
        if window is None:
            runtime_note = f"single-session limit for {needed}h not stated on the checked page"
            unverified.append("continuous_runtime_hours")
        elif not caps.get("pause_resume") and needed > window:
            misses.append(f"{needed}h session exceeds the documented {window}h continuous window")
        elif needed > window:
            runtime_note = f"{needed}h session exceeds the {window}h window; only pause/resume extends it"
    status = "unmet" if misses else ("verify" if unverified else "meets")
    return {"status": status, "misses": misses, "unverified": unverified, "runtime_note": runtime_note}


def main():
    here = pathlib.Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--matrix", type=pathlib.Path, default=here / "capability-matrix.json")
    parser.add_argument("--workloads", type=pathlib.Path, default=here / "workloads.json")
    parser.add_argument("--json", type=pathlib.Path, default=here / "fit-report.json")
    args = parser.parse_args()

    matrix, workloads = load(args.matrix), load(args.workloads)
    print(f"lifecycle-fit check | documented flags checked {matrix['checked_at']} | offline, no provider calls")
    report = {"slug": matrix["slug"], "checked_at": matrix["checked_at"], "profiles": []}

    for profile in workloads["profiles"]:
        print(f"\n[{profile['id']}] {profile['description']}")
        rows = []
        for option in matrix["options"]:
            result = evaluate(option, profile)
            rows.append({"provider": option["provider"], "variant": option["variant"], **result})
            label = f"{option['provider']} / {option['variant']}"
            print(f"  {result['status']:<6} {label}")
            for miss in result["misses"]:
                print(f"         - {miss}")
            for gap in result["unverified"]:
                print(f"         ? verify: {gap}")
            if result["runtime_note"]:
                print(f"         note: {result['runtime_note']}")
        report["profiles"].append({"id": profile["id"], "requires": profile["requires"], "options": rows})

    met = sum(1 for p in report["profiles"] for o in p["options"] if o["status"] == "meets")
    total = sum(len(p["options"]) for p in report["profiles"])
    print(f"\nsummary: {met}/{total} provider-variant pairs meet every documented requirement of their profile")
    print("limits: flags are vendor documentation, not measurements; price, latency and reliability are out of scope")
    args.json.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {args.json.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
