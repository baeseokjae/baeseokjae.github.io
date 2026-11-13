#!/usr/bin/env python3
"""Run the five injected install defects plus a clean control against the stub
ACP registry, and record one transcript per case.

Each case gets a fresh fixture directory, a fresh loopback server on an
ephemeral port, one checker invocation, and its own evidence files:

  fixtures/<case>/                     the exact index document served
  transcripts/<case>.jsonl             server-side request log
  checker/<case>.txt                   checker stdout/stderr + exit code
  results.json                         aggregated table

Deterministic: no network access, no credentials, no sleeps beyond a short
readiness poll on the child server's stdout.

Usage: python3 run_defects.py --out OUT_DIR [--python PYTHON]
"""
import argparse
import hashlib
import json
import os
import platform
import shlex
import shutil
import socket
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
PAYLOAD = b"stub-acp-agent-archive-v1\n" * 8          # the "release" bytes
PAYLOAD_SHA = hashlib.sha256(PAYLOAD).hexdigest()
TAMPERED = PAYLOAD + b"# re-published without a version bump\n"


def closed_port():
    """Reserve an ephemeral port and release it, so nothing listens there."""
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    with socket.socket() as probe:
        probe.settimeout(0.5)
        if probe.connect_ex(("127.0.0.1", port)) == 0:
            return closed_port()
    return port


def base_entry(artifact_url):
    return {
        "id": "claude-acp",
        "name": "Claude Agent",
        "version": "0.106.0",
        "description": "ACP wrapper for Anthropic's Claude (fixture copy)",
        "repository": "https://github.com/agentclientprotocol/claude-agent-acp",
        "authors": ["Anthropic", "Zed Industries", "JetBrains"],
        "license": "Apache-2.0",
        "license_url": "https://github.com/agentclientprotocol/claude-agent-acp/blob/main/LICENSE",
        "icon": "https://cdn.agentclientprotocol.com/registry/v1/latest/claude-acp.svg",
        "distribution": {
            "binary": {
                "linux-x86_64": {
                    "archive": artifact_url,
                    "sha256": PAYLOAD_SHA,
                    "cmd": "./claude-agent-acp",
                    "args": ["--acp"],
                }
            },
            "npx": {"package": "@agentclientprotocol/claude-agent-acp@0.106.0", "args": ["--acp"]},
        },
    }


def build_case(case, root, port):
    """Return (files_to_write, delete_index) for one case."""
    artifact_url = f"http://127.0.0.1:{port}/artifacts/claude-acp-linux-x86_64.tar.gz"
    entry = base_entry(artifact_url)
    files = {}

    if case == "D1_index_404":
        return {}, True

    if case == "D2_missing_license_url":
        entry.pop("license_url")
    elif case == "D3_checksum_mismatch":
        files["artifacts/claude-acp-linux-x86_64.tar.gz"] = TAMPERED
    elif case == "D4_artifact_unreachable":
        dead = closed_port()
        entry["distribution"]["binary"]["linux-x86_64"]["archive"] = (
            f"http://127.0.0.1:{dead}/artifacts/claude-acp-linux-x86_64.tar.gz"
        )
    elif case == "D5_platform_gap":
        entry["distribution"] = {
            "binary": {
                "darwin-aarch64": {
                    "archive": artifact_url,
                    "sha256": PAYLOAD_SHA,
                    "cmd": "./claude-agent-acp",
                }
            }
        }
    elif case != "D0_clean":
        raise SystemExit(f"unknown case {case}")

    files["registry-for-jetbrains.json"] = json.dumps(
        {"version": "1.0.0", "agents": [{"id": "other-acp", "name": "Other", "version": "1.0.0",
                                          "repository": "https://example.invalid/other",
                                          "license_url": "https://example.invalid/LICENSE",
                                          "distribution": {"npx": {"package": "other@1.0.0"}}}, entry]},
        indent=2,
    ) + "\n"
    if "artifacts/claude-acp-linux-x86_64.tar.gz" not in files:
        files["artifacts/claude-acp-linux-x86_64.tar.gz"] = PAYLOAD
    return files, False


def start_server(python, fixture_dir, transcript, port):
    proc = subprocess.Popen(
        [python, str(HERE / "acp_stub_registry.py"), "--root", str(fixture_dir), "--log", str(transcript),
         "--port", str(port)],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
    )
    deadline = time.time() + 10
    while time.time() < deadline:
        line = proc.stdout.readline()
        if line.startswith("PORT "):
            return proc, int(line.split()[1])
        if proc.poll() is not None:
            raise SystemExit("stub registry exited: " + (proc.stderr.read() or "")[:400])
    proc.kill()
    raise SystemExit("stub registry did not report a port within 10 s")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--python", default=sys.executable)
    args = parser.parse_args()
    started = time.perf_counter()
    out = args.out.resolve()
    cases = ["D0_clean", "D1_index_404", "D2_missing_license_url", "D3_checksum_mismatch",
             "D4_artifact_unreachable", "D5_platform_gap"]

    results = {
        "fixture": "loopback stub ACP registry serving the documented index contract",
        "platform_under_test": "linux-x86_64",
        "payload_sha256": PAYLOAD_SHA,
        "payload_bytes": len(PAYLOAD),
        "ide_build_checked": False,
        "host_note": ("No JetBrains IDE is present on this host: no IDE build value is passed to the checker and no "
                      "IDE-side log is produced. The article's log line is user-reported, not reproduced here."),
        "cases": [],
    }

    for case in cases:
        case_dir = out / "fixtures" / case
        if case_dir.exists():
            shutil.rmtree(case_dir)
        (case_dir / "artifacts").mkdir(parents=True)

        # the index embeds absolute artifact URLs, so reserve the port first,
        # write the fixtures that reference it, then bind the server to it.
        transcript = out / "transcripts" / f"{case}.jsonl"
        transcript.parent.mkdir(parents=True, exist_ok=True)
        transcript.write_text("")
        port = closed_port()

        files, delete_index = build_case(case, case_dir, port)
        for rel, content in files.items():
            target = case_dir / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            if isinstance(content, bytes):
                target.write_bytes(content)
            else:
                target.write_text(content)

        transcript.write_text("")
        proc, port = start_server(args.python, case_dir, transcript, port)
        registry = f"http://127.0.0.1:{port}/registry-for-jetbrains.json"
        # No --ide-build is passed: there is no JetBrains IDE on this host, so any
        # build value here would be a placeholder dressed up as an observation.
        checker_argv = [args.python, str(HERE / "acp_install_check.py"), "--registry", registry,
                        "--agent", "claude-acp", "--platform", "linux-x86_64"]
        try:
            run = subprocess.run(checker_argv, capture_output=True, text=True, timeout=120)
        finally:
            proc.terminate()
            proc.wait(timeout=10)

        # The header is generated from the executed argv, not typed alongside it,
        # so it cannot drift from the flags the checker actually received. Only the
        # interpreter and script paths are reduced to bare names.
        shown = [Path(checker_argv[0]).name, Path(checker_argv[1]).name] + checker_argv[2:]
        logged_command = "$ " + " ".join(shlex.quote(part) for part in shown)

        checker_dir = out / "checker"
        checker_dir.mkdir(parents=True, exist_ok=True)
        (checker_dir / f"{case}.txt").write_text(
            logged_command + "\n"
            + run.stdout + ("\n[stderr]\n" + run.stderr if run.stderr.strip() else "")
            + f"\n[exit {run.returncode}]\n"
        )

        rows = [l for l in run.stdout.splitlines() if l.startswith("[")]
        failing = [r.split(":")[0].replace("[FAIL]", "").strip() for r in rows if r.startswith("[FAIL]")]
        requests = [json.loads(l) for l in transcript.read_text().splitlines() if l.strip()]
        results["cases"].append({
            "case": case,
            "checker_exit": run.returncode,
            "failing_checks": failing,
            "first_failing_check": failing[0] if failing else None,
            "checks_run": len(rows),
            "requests": requests,
            "transcript": f"transcripts/{case}.jsonl",
        })
        print(f"{case:24s} exit={run.returncode} failing={failing} requests={len(requests)}")

    versions = {
        "python": sys.version.split()[0],
        "node": subprocess.run(["node", "--version"], capture_output=True, text=True).stdout.strip() or None,
        "npm": subprocess.run(["npm", "--version"], capture_output=True, text=True).stdout.strip() or None,
        "platform": platform.platform(),
        "machine": platform.machine(),
        "collected_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    results["versions"] = versions
    results["wall_clock_s"] = round(time.perf_counter() - started, 2)
    results["summary"] = {
        "cases": len(results["cases"]),
        "distinct_first_failures": sorted({c["first_failing_check"] for c in results["cases"] if c["first_failing_check"]}),
        "false_pass": [c["case"] for c in results["cases"] if c["case"] != "D0_clean" and c["checker_exit"] == 0],
        "control_passed": next(c["checker_exit"] == 0 for c in results["cases"] if c["case"] == "D0_clean"),
    }
    (out / "results.json").write_text(json.dumps(results, indent=2) + "\n")
    print(json.dumps(results["summary"], indent=1))


if __name__ == "__main__":
    main()
