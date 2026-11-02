#!/usr/bin/env python3
"""Fault-injection harness: does a retried tool call duplicate its side effect?

Local only. No network except 127.0.0.1. No model calls.

Server: HTTP tool endpoint backed by SQLite. The "effect" is an INSERT into an
append-only ledger keyed by an idempotency key; a duplicate is a second row for
the same (scenario, payload).

Fault modes
  none                 commit, reply 200
  error_502_before     reply 502 before touching the ledger
  timeout_before       sleep past client timeout, never commit
  timeout_after        commit, then sleep past client timeout (client cannot tell)

Client policies
  a_blind_new_key      retry up to 3x, regenerating tool_call_id + Idempotency-Key
  b_reuse_key          retry up to 3x with the original tool_call_id as the key
  c_arg_hash_dedupe    retry up to 3x with fresh keys; server dedupes on tool+args hash
  d_no_retry           fail closed, no retry

Run: python3 tool_retry_fault_harness.py --out ledger.csv --faults 50
"""
import argparse
import csv
import hashlib
import json
import os
import sqlite3
import threading
import time
import urllib.error
import urllib.request
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

CLIENT_TIMEOUT_S = 0.12
SERVER_LATE_REPLY_S = 0.35

SCHEMA = """
CREATE TABLE IF NOT EXISTS effects(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  scenario TEXT NOT NULL,
  idem_key TEXT NOT NULL,
  tool TEXT NOT NULL,
  args_hash TEXT NOT NULL,
  payload TEXT NOT NULL,
  created_at REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS responses(
  idem_key TEXT PRIMARY KEY,
  status INTEGER NOT NULL,
  body TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS dedupe(
  tool TEXT NOT NULL,
  args_hash TEXT NOT NULL,
  effect_id INTEGER NOT NULL,
  PRIMARY KEY(tool, args_hash)
);
"""


class Store:
    def __init__(self, path):
        self.lock = threading.Lock()
        self.path = path
        c = sqlite3.connect(path)
        c.execute("PRAGMA journal_mode=WAL")
        c.executescript(SCHEMA)
        c.commit()
        c.close()

    def _conn(self):
        # journal mode is set once in __init__; per-request PRAGMA rewrites the
        # header and serialises on the database lock under concurrent handlers.
        return sqlite3.connect(self.path, timeout=10)

    def saved_response(self, idem_key):
        with self.lock:
            c = self._conn()
            row = c.execute("SELECT status, body FROM responses WHERE idem_key=?", (idem_key,)).fetchone()
            c.close()
            return row

    def commit(self, scenario, idem_key, tool, args_hash, payload, dedupe_mode):
        """Returns (status, body, committed_bool, dedupe_hit)."""
        with self.lock:
            c = self._conn()
            try:
                prev = c.execute("SELECT status, body FROM responses WHERE idem_key=?", (idem_key,)).fetchone()
                if prev:
                    return prev[0], prev[1], False, True
                if dedupe_mode:
                    hit = c.execute("SELECT effect_id FROM dedupe WHERE tool=? AND args_hash=?",
                                    (tool, args_hash)).fetchone()
                    if hit:
                        body = json.dumps({"effect_id": hit[0], "deduped": True})
                        c.execute("INSERT INTO responses VALUES(?,?,?)", (idem_key, 200, body))
                        c.commit()
                        return 200, body, False, True
                cur = c.execute(
                    "INSERT INTO effects(scenario,idem_key,tool,args_hash,payload,created_at) VALUES(?,?,?,?,?,?)",
                    (scenario, idem_key, tool, args_hash, payload, time.time()))
                eid = cur.lastrowid
                if dedupe_mode:
                    c.execute("INSERT OR IGNORE INTO dedupe(tool,args_hash,effect_id) VALUES(?,?,?)",
                              (tool, args_hash, eid))
                body = json.dumps({"effect_id": eid, "deduped": False})
                c.execute("INSERT INTO responses VALUES(?,?,?)", (idem_key, 200, body))
                c.commit()
                return 200, body, True, False
            finally:
                c.close()

    def count_effects(self, scenario, args_hash):
        with self.lock:
            c = self._conn()
            n = c.execute("SELECT COUNT(*) FROM effects WHERE scenario=? AND args_hash=?",
                          (scenario, args_hash)).fetchone()[0]
            c.close()
            return n


STORE = None
FAULT = "none"


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, *a):
        pass

    def do_POST(self):
        n = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(n).decode()
        req = json.loads(raw)
        key = self.headers.get("Idempotency-Key", "")
        fault = req.get("_fault", FAULT)
        args_hash = hashlib.sha256(json.dumps(req["args"], sort_keys=True).encode()).hexdigest()[:16]
        dedupe_mode = req.get("_policy") == "c_arg_hash_dedupe"

        if fault == "error_502_before":
            self._reply(502, json.dumps({"error": "bad_gateway"}))
            return
        if fault == "timeout_before":
            time.sleep(SERVER_LATE_REPLY_S)
            self._reply(504, json.dumps({"error": "gateway_timeout"}))
            return

        status, body, _committed, _dedupe = STORE.commit(
            req["scenario"], key, req["tool"], args_hash, json.dumps(req["args"], sort_keys=True), dedupe_mode)
        if fault == "timeout_after" and int(req.get("_attempt", 1)) == 1:
            # stall only the first attempt: one transient post-commit network stall
            time.sleep(SERVER_LATE_REPLY_S)
        self._reply(status, body)

    def _reply(self, status, body):
        b = body.encode()
        try:
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(b)))
            self.end_headers()
            self.wfile.write(b)
        except (BrokenPipeError, ConnectionResetError):
            pass


def call(url, payload, key):
    data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, method="POST",
                                 headers={"Content-Type": "application/json", "Idempotency-Key": key})
    try:
        with urllib.request.urlopen(req, timeout=CLIENT_TIMEOUT_S) as r:
            return r.status, r.read().decode(), len(data)
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode(), len(data)
    except (TimeoutError, urllib.error.URLError, ConnectionResetError) as e:
        return 0, f"{type(e).__name__}", len(data)


def run_scenario(url, policy, fault, scenario_id, payload_text, rows):  # attempt-aware fault
    args = {"target": "issue_tracker", "body": payload_text, "case": scenario_id}
    call_id = f"call_{uuid.uuid4().hex[:12]}"
    first_call_id = call_id
    args_hash = hashlib.sha256(json.dumps(args, sort_keys=True).encode()).hexdigest()[:16]
    attempts = 0
    resent_chars = 0
    call_id_changed = False
    attempt_rows = []
    for attempt in range(1, 5):
        if policy == "d_no_retry" and attempt > 1:
            break
        if policy == "a_blind_new_key":
            key = f"idem_{uuid.uuid4().hex}"
            if attempt > 1:
                call_id = f"call_{uuid.uuid4().hex[:12]}"
        elif policy == "b_reuse_key":
            key = first_call_id
        elif policy == "c_arg_hash_dedupe":
            key = f"idem_{uuid.uuid4().hex}"
        else:
            key = first_call_id
        if call_id != first_call_id:
            call_id_changed = True
        # token/cost proxy: a retried step resends the whole transcript
        resent = len(payload_text) if attempt == 1 else len(payload_text) + 1800
        resent_chars += resent
        status, body, sent = call(url, {"scenario": scenario_id, "tool": "issue_tracker",
                                        "args": args, "_fault": fault, "_policy": policy,
                                        "tool_call_id": call_id, "_attempt": attempt}, key)
        attempts += 1
        attempt_rows.append((attempt, status, key[:20], call_id, resent))
        if status == 200:
            break
    total_effects = STORE.count_effects(scenario_id, args_hash)
    rows.append({
        "scenario": scenario_id, "policy": policy, "fault_mode": fault,
        "attempts": attempts, "effects_committed": total_effects,
        "duplicate_detected": int(total_effects > 1),
        "call_id_changed": int(call_id_changed),
        "prompt_chars_resent": resent_chars,
        "final_status": status,
        "attempt_trace": json.dumps(attempt_rows),
    })


def main():
    global STORE, FAULT
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="ledger.csv")
    ap.add_argument("--faults", type=int, default=50)
    ap.add_argument("--db", default=None)
    a = ap.parse_args()
    db = a.db or os.path.join(os.path.dirname(os.path.abspath(a.out)), "effects.sqlite")
    if os.path.exists(db):
        os.remove(db)
    STORE = Store(db)
    srv = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    port = srv.server_address[1]
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    url = f"http://127.0.0.1:{port}/tool"

    payload_text = ("You are an agent. Transcript: " + ("lorem ipsum dolor sit amet " * 70))[:2000]
    rows = []
    t0 = time.time()
    # control 1: no fault at all, blind policy -> must be exactly 1 effect per trial
    for i in range(a.faults):
        run_scenario(url, "a_blind_new_key", "none", f"ctrl_none_{i}", payload_text, rows)
    # control 2 / cells
    for fault in ("timeout_before", "timeout_after", "error_502_before"):
        for policy in ("a_blind_new_key", "b_reuse_key", "c_arg_hash_dedupe", "d_no_retry"):
            for i in range(a.faults):
                run_scenario(url, policy, fault, f"{policy}__{fault}__{i}", payload_text, rows)
    elapsed = time.time() - t0
    fields = ["scenario", "policy", "fault_mode", "attempts", "effects_committed",
              "duplicate_detected", "call_id_changed", "prompt_chars_resent",
              "final_status", "attempt_trace"]
    with open(a.out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    # aggregate
    agg = {}
    for r in rows:
        k = (r["policy"], r["fault_mode"])
        d = agg.setdefault(k, {"trials": 0, "dupes": 0, "attempts": 0, "chars": 0})
        d["trials"] += 1
        d["dupes"] += r["duplicate_detected"]
        d["attempts"] += r["attempts"]
        d["chars"] += r["prompt_chars_resent"]
    summary = {"rows": len(rows), "elapsed_s": round(elapsed, 2), "faults_per_cell": a.faults,
               "client_timeout_s": CLIENT_TIMEOUT_S, "server_late_reply_s": SERVER_LATE_REPLY_S,
               "cells": [{"policy": k[0], "fault_mode": k[1], "trials": v["trials"],
                          "duplicate_trials": v["dupes"],
                          "duplicate_rate": round(v["dupes"] / v["trials"], 4),
                          "mean_attempts": round(v["attempts"] / v["trials"], 3),
                          "mean_prompt_chars_resent": round(v["chars"] / v["trials"], 1)}
                         for k, v in sorted(agg.items())]}
    print(json.dumps(summary, indent=2))
    with open(os.path.join(os.path.dirname(os.path.abspath(a.out)), "summary.json"), "w") as f:
        json.dump(summary, f, indent=2)


if __name__ == "__main__":
    main()
