"""Two-policy retry comparison over the frozen model-retirement fixture.

Round-2 measurement (see research/model-retirement-error-handling-2026.json).
Reuses the six verified envelopes from run-2026-11-01/envelopes (bodies untouched;
hashes in ../../hashes-run.txt) and the precedence-ordered classifier from that run.

Isolation: one Python process starts a ThreadingHTTPServer bound to 127.0.0.1:0,
serves from a daemon thread, and always ends in try/finally: shutdown(),
server_close(), thread.join(timeout=5). No signals, no process-name matching,
no background jobs, no network, no API keys.

Labels: labels.json declares its own write time (frozen_at) and ships with
labels.sha256. This script re-hashes the file and derives
summary.labels_frozen_before_run by comparing the declared timestamp with
run.started_utc -- computed, never asserted -- so the ordering a reader checks is
the one the artifact recorded.

Run (stdlib only, ~10 s), from this directory:

    cd research/evidence/model-retirement-error-handling-2026/reproduction
    python3 compare.py

Layout (since the 2026-11-25 relocation): compare.py + labels.json + labels.sha256
+ envelopes/ live here; outputs are written to out/. The original 2026-11-19 run
record stays untouched in ../retry-compare-2026-11-01/.
"""
import csv
import hashlib
import json
import os
import sys
import threading
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
ENV_DIR = os.path.join(HERE, "envelopes")
OUT_DIR = os.path.join(HERE, "out")
LABELS = os.path.join(HERE, "labels.json")
COUNTS = {}
SERVER_EVENTS = []

POLICIES = {
    # retry on anything that is not a success
    "retry_all": lambda status: status >= 400,
    # standard client behaviour: retry only 408/409/429 and 5xx
    "no_retry_4xx": lambda status: status in (408, 409, 429) or status >= 500,
}
ATTEMPTS = 3
BACKOFF_BASE_S = 0.2


def utcnow():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    timeout = 5

    def do_POST(self):
        n = int(self.headers.get("content-length") or 0)
        if n:
            self.rfile.read(n)
        self._respond()

    def _respond(self):
        if not self.path.startswith("/fixtures/"):
            self.send_error(404)
            return
        name = self.path[len("/fixtures/"):]
        COUNTS[name] = COUNTS.get(name, 0) + 1
        SERVER_EVENTS.append({"at": utcnow(), "path": name, "n": COUNTS[name]})
        with open(os.path.join(ENV_DIR, name), encoding="utf-8") as f:
            rec = json.load(f)
        payload = json.dumps(rec["body"]).encode()
        self.send_response(rec["http_status"])
        self.send_header("content-type", "application/json")
        self.send_header("content-length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)
        self.wfile.flush()

    def log_message(self, *a):
        pass


def classify(status, body):
    """Precedence-ordered, unchanged in spirit from run-2026-11-01/mock_replay.py."""
    err = body.get("error") if isinstance(body, dict) else None
    etype = err.get("type") if isinstance(err, dict) else None
    code = err.get("code") if isinstance(err, dict) else None
    msg = err.get("message", "") if isinstance(err, dict) else str(err or "")
    if code == "model_not_found":
        return "model_unavailable", "error.code=model_not_found"
    if status in (401, 403):
        return "auth", f"http_status={status}"
    if status == 429:
        return "rate_limit", "http_status=429"
    if status == 400 and "context" in msg.lower():
        return "context_length", "http_status=400+message"
    if status == 404 and isinstance(err, str) and "not found" in err.lower():
        return "model_unavailable", "http_status=404+error string (no typed field)"
    if status == 404 and etype == "not_found_error":
        return "model_unavailable", "http_status=404+error.type=not_found_error"
    if status in (500, 502, 503, 504):
        return "transient", f"http_status={status}"
    if status == 529 or etype == "overloaded_error":
        return "transient", "http_status=529"
    return "unknown", "no rule matched"


def run_cell(base, name, policy):
    should_retry = POLICIES[policy]
    t0 = time.time()
    issued, last = 0, None
    for i in range(ATTEMPTS):
        req = urllib.request.Request(
            base + "/fixtures/" + name, data=b'{"model":"pinned"}',
            headers={"content-type": "application/json"}, method="POST")
        issued += 1
        try:
            with urllib.request.urlopen(req, timeout=5) as r:
                last = r.status
        except urllib.error.HTTPError as e:
            last = e.code
        if not should_retry(last):
            break
        if i + 1 < ATTEMPTS:
            time.sleep(BACKOFF_BASE_S * (2 ** i))
    return {"client_attempts": issued, "wall_ms": int((time.time() - t0) * 1000),
            "final_status": last}


def parse_ts(value):
    """Parse the Z-suffixed timestamps this script writes; None if unparseable."""
    if not isinstance(value, str):
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
    except ValueError:
        try:
            return datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        except ValueError:
            return None


def main():
    with open(LABELS, encoding="utf-8") as f:
        labels = json.load(f)
    labels_sha = hashlib.sha256(open(LABELS, "rb").read()).hexdigest()
    labels_mtime = datetime.fromtimestamp(os.stat(LABELS).st_mtime, timezone.utc)

    names = sorted(n for n in os.listdir(ENV_DIR) if n.endswith(".json"))
    started = utcnow()
    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    server.timeout = 5
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever,
                              kwargs={"poll_interval": 0.05}, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{port}"
    cells, cls_rows = [], []
    try:
        for name in names:
            with open(os.path.join(ENV_DIR, name), encoding="utf-8") as f:
                rec = json.load(f)
            pred, basis = classify(rec["http_status"], rec["body"])
            row = labels["rows"].get(name, {})
            cls_rows.append({
                "fixture": name, "http_status": rec["http_status"],
                "verification": rec["verification"],
                "cause_label": row.get("cause"),
                "scope_label": row.get("scope_label"),
                "prediction": pred, "decision_field": basis,
                "cause_correct": pred == row.get("cause"),
                "scope_correct": pred == row.get("scope_label"),
                "body_sha256": hashlib.sha256(
                    json.dumps(rec["body"], sort_keys=True).encode()).hexdigest(),
            })
        for policy in ("retry_all", "no_retry_4xx"):
            for name in names:
                COUNTS[name] = 0
                before = len(SERVER_EVENTS)
                cell = run_cell(base, name, policy)
                cells.append({"fixture": name, "policy": policy,
                              "label": labels["rows"].get(name, {}).get("scope_label"),
                              "server_requests": len(SERVER_EVENTS) - before, **cell})
    finally:
        server.shutdown()
        closed = utcnow()
        server.server_close()
        thread.join(timeout=5)
        finished = utcnow()

    by_policy = {}
    for policy in POLICIES:
        for label in ("model_unavailable", "transient"):
            vals = {c["server_requests"] for c in cells
                    if c["policy"] == policy and c["label"] == label}
            by_policy.setdefault(policy, {})[label] = sorted(vals)
    verbatim = [r for r in cls_rows if r["verification"] == "verbatim"]
    started_dt = parse_ts(started)
    frozen_dt = parse_ts(labels.get("frozen_at"))
    # Derived from two timestamps, never asserted as a constant.
    frozen_before = bool(started_dt and frozen_dt and frozen_dt < started_dt)
    summary = {
        "labels_sha256": labels_sha,
        "labels_frozen_at_declared": labels.get("frozen_at"),
        "labels_file_mtime_utc": labels_mtime.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z",
        "run_started_utc": started,
        "labels_frozen_before_run": frozen_before,
        "labels_frozen_basis": ("labels.json frozen_at parsed and compared with run.started_utc; "
                                "false if either timestamp is missing or unparseable"),
        "rows": len(cls_rows),
        "verbatim_rows": len(verbatim),
        "verbatim_scope_correct": sum(r["scope_correct"] for r in verbatim),
        "verbatim_cause_correct": sum(r["cause_correct"] for r in verbatim),
        "all_scope_correct": sum(r["scope_correct"] for r in cls_rows),
        "unknown_predictions": sum(r["prediction"] == "unknown" for r in cls_rows),
        "requests_by_policy_and_label": by_policy,
        "distinguishable": by_policy["retry_all"]["model_unavailable"]
        != by_policy["retry_all"]["transient"],
    }
    out = {"run": {"started_utc": started, "server_close_utc": closed,
                   "finished_utc": finished, "bind": "127.0.0.1:0 (OS-assigned)",
                   "port_observed": port, "python": sys.version.split()[0],
                   "attempts_cap": ATTEMPTS, "backoff_base_s": BACKOFF_BASE_S,
                   "isolation": "single process, in-process daemon thread, "
                                "try/finally shutdown()/server_close()/join(timeout=5)",
                   "thread_alive_after_join": thread.is_alive()},
           "envelopes": "reused verbatim from run-2026-11-01/envelopes; copies in this directory's envelopes/ have identical sha256",
           "classification": cls_rows, "retry_cells": cells,
           "summary": summary, "server_events": SERVER_EVENTS}

    with open(os.path.join(OUT_DIR, "results.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    with open(os.path.join(OUT_DIR, "retry-policy-compare.csv"), "w", newline="",
              encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(cells[0].keys()))
        w.writeheader()
        w.writerows(cells)
    with open(os.path.join(OUT_DIR, "classification.csv"), "w", newline="",
              encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(cls_rows[0].keys()))
        w.writeheader()
        w.writerows(cls_rows)
    print(json.dumps({"port": port, "started": started, "finished": finished,
                      "summary": summary}, indent=1))


if __name__ == "__main__":
    main()
