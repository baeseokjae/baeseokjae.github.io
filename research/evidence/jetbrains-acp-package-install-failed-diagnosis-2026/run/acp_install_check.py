#!/usr/bin/env python3
"""Reader-side pre-flight for an ACP registry entry that fails to install.

It answers one question: which layer of the documented install contract is
broken — index fetch, entry schema, platform distribution, artifact
reachability, artifact checksum, or the local runtime the entry needs.

It never claims to read IDE internals. `package_install_failed` is a client
log token with no published taxonomy, so this tool reports what it observed at
the network and filesystem layer and labels each failure with the layer it
belongs to.

Ordered checks, PASS/FAIL/SKIP per check, exit code 1 if any check FAILs.

Usage:
  python3 acp_install_check.py --registry http://127.0.0.1:8000/registry-for-jetbrains.json \
      --agent claude-acp --platform linux-x86_64
"""
import argparse
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request

UA = "acp-preflight/1.0 (+reader runnable; offline fixture ok)"


class Rows:
    def __init__(self):
        self.rows = []

    def add(self, check, status, detail, cause=""):
        self.rows.append({"check": check, "status": status, "detail": detail, "likely_cause": cause})

    def failed(self):
        return [r for r in self.rows if r["status"] == "FAIL"]

    def first_failure(self):
        failed = self.failed()
        return failed[0]["check"] if failed else None


def fetch(url, timeout=10):
    started = time.perf_counter()
    request = urllib.request.Request(url, headers={"User-Agent": UA, "Cache-Control": "no-store"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        body = response.read()
        return response.status, body, round((time.perf_counter() - started) * 1000, 1)


def node_version(binary):
    path = shutil.which(binary)
    if not path:
        return None, None
    try:
        out = subprocess.run([binary, "--version"], capture_output=True, text=True, timeout=10).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return path, None
    return path, out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", required=True)
    parser.add_argument("--agent", default="claude-acp")
    parser.add_argument("--platform", default="linux-x86_64")
    parser.add_argument("--ide-build", default=None, help="informational only; no registry field encodes it")
    parser.add_argument("--timeout", type=float, default=10.0)
    args = parser.parse_args()

    rows = Rows()
    print(f"registry : {args.registry}")
    print(f"agent    : {args.agent}")
    print(f"platform : {args.platform} (host: {platform.system().lower()}-{platform.machine()})")
    print("")

    index = None
    # 1. index reachability and parseability
    try:
        status, body, elapsed = fetch(args.registry, args.timeout)
        print(f"index_fetch: HTTP {status} in {elapsed} ms, {len(body)} bytes")
        index = json.loads(body)
        rows.add("index_fetch", "PASS", f"HTTP {status}, {len(body)} bytes, valid JSON")
    except urllib.error.HTTPError as exc:
        rows.add("index_fetch", "FAIL", f"HTTP {exc.code} for {args.registry}",
                 "registry host reachable, index path rejected — URL/channel wrong or blocked by a proxy")
    except urllib.error.URLError as exc:
        rows.add("index_fetch", "FAIL", f"{exc.reason} for {args.registry}",
                 "DNS, TLS, proxy or firewall blocks the registry host before any agent data is read")
    except (json.JSONDecodeError, ValueError) as exc:
        rows.add("index_fetch", "FAIL", f"index body is not JSON: {exc}",
                 "captive portal or proxy injected a non-registry document")

    entry = None
    if index is not None:
        agents = index.get("agents") if isinstance(index, dict) else None
        if not isinstance(agents, list):
            rows.add("entry_present", "FAIL", "index has no agents[] list",
                     "served document is not a registry index (wrong channel or truncated download)")
        else:
            entry = next((a for a in agents if isinstance(a, dict) and a.get("id") == args.agent), None)
            if entry:
                rows.add("entry_present", "PASS", f"id={args.agent!r} found in {len(agents)} entries")
            else:
                rows.add("entry_present", "FAIL", f"id={args.agent!r} absent from {len(agents)} entries",
                         "agent unpublished, renamed, or the preview/stable channel you fetched is not the one that lists it")

    if entry is not None:
        required = ["id", "name", "version", "repository", "license_url", "distribution"]
        missing = [f for f in required if not entry.get(f)]
        if missing:
            rows.add("entry_schema", "FAIL", "missing required field(s): " + ", ".join(missing),
                     "registry-side entry is invalid; license_url is documented as required (dimcode exempt)")
        else:
            rows.add("entry_schema", "PASS", f"required fields present; version={entry['version']}")

        dist = entry.get("distribution") if isinstance(entry.get("distribution"), dict) else {}
        binary = dist.get("binary") if isinstance(dist.get("binary"), dict) else {}
        target = binary.get(args.platform) if isinstance(binary, dict) else None
        npx, uvx = dist.get("npx"), dist.get("uvx")
        if target:
            rows.add("distribution_select", "PASS", f"binary target {args.platform} declared")
        elif npx or uvx:
            kind = "npx" if npx else "uvx"
            rows.add("distribution_select", "PASS", f"no {args.platform} binary; {kind} fallback declared")
        else:
            rows.add("distribution_select", "FAIL",
                     f"no binary target for {args.platform} and no npx/uvx fallback; keys={sorted(binary)}",
                     "platform gap in the registry entry: this host cannot install the declared distributions")

        artifact_url = target.get("archive") if target else None
        payload = None
        if artifact_url:
            try:
                status, payload, elapsed = fetch(artifact_url, args.timeout)
                rows.add("artifact_fetch", "PASS", f"HTTP {status}, {len(payload)} bytes in {elapsed} ms")
            except urllib.error.HTTPError as exc:
                rows.add("artifact_fetch", "FAIL", f"HTTP {exc.code} for {artifact_url}",
                         "artifact published in the index is not served (404/403) — stale entry or revoked release")
            except urllib.error.URLError as exc:
                rows.add("artifact_fetch", "FAIL", f"{exc.reason} for {artifact_url}",
                         "artifact host unreachable from this machine only — DNS/proxy/firewall, not the agent")
        elif target:
            rows.add("artifact_fetch", "SKIP", "binary target declares no archive URL")

        if target and payload is not None:
            declared = (target.get("sha256") or "").lower()
            actual = hashlib.sha256(payload).hexdigest()
            if not declared:
                rows.add("artifact_sha256", "SKIP", "entry declares no sha256 (optional per FORMAT.md)")
            elif actual == declared:
                rows.add("artifact_sha256", "PASS", actual)
            else:
                rows.add("artifact_sha256", "FAIL", f"declared {declared[:16]}… served {actual[:16]}…",
                         "served bytes are not the declared release: truncated download, proxy rewriting, or a republished file")
        elif target:
            rows.add("artifact_sha256", "SKIP", "no artifact bytes to hash")

        needs_node = bool(npx) and not target
        node_path, node_out = node_version("node")
        npm_path, npm_out = node_version("npm")
        if needs_node and not node_path:
            rows.add("runtime_node", "FAIL", "entry installs via npx and no node on PATH",
                     "runtime dependency missing; install Node or use a binary distribution")
        elif node_path:
            rows.add("runtime_node", "PASS", f"node {node_out} at {node_path}; npm {npm_out or 'absent'} ({npm_path or '-'})")
        else:
            rows.add("runtime_node", "SKIP", "binary distribution; no node/npm required by the entry")

    print("")
    for row in rows.rows:
        print(f"[{row['status']:4}] {row['check']}: {row['detail']}")
        if row["likely_cause"]:
            print(f"       likely cause: {row['likely_cause']}")

    proxies = {k: v for k, v in os.environ.items() if k.lower() in ("http_proxy", "https_proxy", "no_proxy", "all_proxy")}
    print("")
    print("environment: " + (", ".join(f"{k}={v}" for k, v in sorted(proxies.items())) or "no proxy variables set"))
    if args.ide_build:
        print(f"ide_build: {args.ide_build} (informational; the registry format documents no minimum-IDE field)")

    first = rows.first_failure()
    if first:
        print(f"RESULT: FAIL — first failing check: {first}")
        return 1
    print("RESULT: PASS — every contract check that could run on this host passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
