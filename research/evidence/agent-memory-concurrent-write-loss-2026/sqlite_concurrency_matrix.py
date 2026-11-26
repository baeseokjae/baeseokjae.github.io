#!/usr/bin/env python3
"""sqlite_concurrency_matrix.py -- multi-process agent-memory write harness.

Stdlib only (sqlite3 + multiprocessing). No service, no network, no paid API.

Patterns
  P1  single-statement UPSERT on UNIQUE(user_id,key)
  P2  client-side read-modify-write (SELECT then UPDATE/INSERT), the shape most
      memory libraries use; an optional small compute gap models embedding work
      between the read and the write
  P3  delete-then-insert "replace" inside BEGIN IMMEDIATE
  P4  P1 on a table with NO unique index (shows what the index buys)

Configurations
  delete_bt100ms : journal_mode=delete, busy_timeout=100ms
  wal_bt5s       : journal_mode=WAL,      busy_timeout=5000ms
  wal_bt30s      : journal_mode=WAL,      busy_timeout=30000ms

Every write attempt is recorded to a raw JSONL trace; a summary CSV is written
per (pattern, configuration). Re-running with the same seed reproduces the
fixture; timings will differ.

Usage:
  python3 sqlite_concurrency_matrix.py --out DIR [--writers 4] [--writes 500]
      [--repeats 1] [--rmw-delay-ms 2] [--deadline-s 240]
"""
import argparse
import csv
import json
import multiprocessing as mp
import os
import random
import signal
import sqlite3
import statistics
import sys
import time
from datetime import datetime, timezone

KEYS = 25
USER = "u1"
KINDS = ["observation", "decision", "superseding_decision", "preference"]
TEXT = {
    "observation": "worker observed build 4821 passing after retry",
    "decision": "planner chose strategy A for the migration",
    "superseding_decision": "planner superseded strategy A with strategy B",
    "preference": "operator prefers concise status reports",
}
PATTERNS = ["P1_upsert", "P2_read_modify_write", "P3_delete_insert", "P4_rmw_no_index"]
CONFIGS = [
    ("delete_bt100ms", "delete", 0.1),
    ("wal_bt5s", "wal", 5.0),
    ("wal_bt30s", "wal", 30.0),
]


def now_iso():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def build_fixture(n_writers, n_writes, seed=20261112):
    """Centrally generated intents: per-key monotonically increasing seq, so the
    newest intent for a key is unambiguous. Intents are shuffled into each
    writer's queue."""
    rng = random.Random(seed)
    per_key = {k: 0 for k in range(KEYS)}
    intents = []
    for i in range(n_writers * n_writes):
        k = rng.randrange(KEYS)
        per_key[k] += 1
        kind = rng.choice(KINDS)
        intents.append({
            "user_id": USER,
            "key": f"k{k:02d}",
            "text": f"{TEXT[kind]} #{per_key[k]}",
            "kind": kind,
            "seq": per_key[k],
            "updated_at": now_iso(),
        })
    queues = [[] for _ in range(n_writers)]
    for idx, it in enumerate(intents):
        queues[idx % n_writers].append(it)
    for q in queues:
        rng.shuffle(q)
    return queues


def schema_sql(with_index, pattern):
    cols = """CREATE TABLE memory (
        id INTEGER PRIMARY KEY,
        user_id TEXT NOT NULL,
        key TEXT NOT NULL,
        text TEXT NOT NULL,
        seq INTEGER NOT NULL,
        updated_at TEXT NOT NULL
    );"""
    if with_index:
        cols += "\nCREATE UNIQUE INDEX ux_memory_user_key ON memory(user_id, key);"
    if pattern != "P4_rmw_no_index":
        cols += "\nCREATE INDEX ix_memory_user ON memory(user_id);"
    return cols


def init_db(path, pattern, journal, busy_timeout):
    if os.path.exists(path):
        os.remove(path)
    con = sqlite3.connect(path, timeout=busy_timeout)
    con.execute(f"PRAGMA journal_mode={journal}")
    con.execute(f"PRAGMA synchronous=FULL")
    con.executescript(schema_sql(with_index=pattern != "P4_rmw_no_index", pattern=pattern))
    con.commit()
    con.close()


def one_write(con, pattern, it, delay_ms):
    """Performs one write attempt. Returns (ok, error_name, detail)."""
    if pattern == "P1_upsert":
        con.execute(
            """INSERT INTO memory (user_id, key, text, seq, updated_at)
               VALUES (?,?,?,?,?)
               ON CONFLICT(user_id, key) DO UPDATE SET
                 text=excluded.text, seq=excluded.seq, updated_at=excluded.updated_at
               WHERE excluded.seq >= memory.seq""",
            (it["user_id"], it["key"], it["text"], it["seq"], it["updated_at"]),
        )
        return True, None, None
    if pattern in ("P2_read_modify_write", "P4_rmw_no_index"):
        row = con.execute(
            "SELECT id, seq FROM memory WHERE user_id=? AND key=?", (it["user_id"], it["key"])
        ).fetchone()
        if delay_ms:
            time.sleep(delay_ms / 1000.0)
        if row is None:
            try:
                con.execute(
                    "INSERT INTO memory (user_id, key, text, seq, updated_at) VALUES (?,?,?,?,?)",
                    (it["user_id"], it["key"], it["text"], it["seq"], it["updated_at"]),
                )
            except sqlite3.IntegrityError:
                # Only reachable on the indexed schema when another writer won the insert race.
                con.execute(
                    "UPDATE memory SET text=?, seq=?, updated_at=? WHERE user_id=? AND key=? AND seq<=?",
                    (it["text"], it["seq"], it["updated_at"], it["user_id"], it["key"], it["seq"]),
                )
        else:
            if row[1] > it["seq"]:
                return True, None, "skipped_stale"
            con.execute(
                "UPDATE memory SET text=?, seq=?, updated_at=? WHERE id=?",
                (it["text"], it["seq"], it["updated_at"], row[0]),
            )
        return True, None, None
    if pattern == "P3_delete_insert":
        con.execute("BEGIN IMMEDIATE")
        try:
            con.execute("DELETE FROM memory WHERE user_id=? AND key=?", (it["user_id"], it["key"]))
            con.execute(
                "INSERT INTO memory (user_id, key, text, seq, updated_at) VALUES (?,?,?,?,?)",
                (it["user_id"], it["key"], it["text"], it["seq"], it["updated_at"]),
            )
            con.commit()
            return True, None, None
        except Exception:
            con.rollback()
            raise
    raise ValueError(pattern)


def writer_proc(db_path, pattern, busy_timeout, queue, delay_ms, out_q, stop_at):
    con = sqlite3.connect(db_path, timeout=busy_timeout, isolation_level=None)
    con.execute(f"PRAGMA busy_timeout={int(busy_timeout * 1000)}")
    for it in queue:
        if time.time() > stop_at:
            out_q.put(("deadline", None))
            break
        t0 = time.perf_counter()
        try:
            ok, err, detail = one_write(con, pattern, it, delay_ms)
            dt = time.perf_counter() - t0
            out_q.put(("write", (it["key"], it["seq"], ok, err, detail, dt)))
        except sqlite3.OperationalError as e:
            dt = time.perf_counter() - t0
            out_q.put(("write", (it["key"], it["seq"], False, "OperationalError", str(e), dt)))
    con.close()


def evaluate(db_path, writes, fixture_max_seq):
    con = sqlite3.connect(db_path)
    rows = con.execute("SELECT key, seq, COUNT(*) FROM memory GROUP BY key").fetchall()
    dup_keys = [k for k, s, c in rows if c > 1]
    final = {k: s for k, s, c in rows}
    integrity = con.execute("PRAGMA integrity_check").fetchone()[0]
    con.close()
    lost_writes = 0
    lost_keys = 0
    for k, mx in fixture_max_seq.items():
        if k in final and final[k] < mx:
            lost_keys += 1
    for (key, seq, ok, err, detail, dt) in writes:
        if ok and detail != "skipped_stale" and seq > final.get(key, -1):
            lost_writes += 1
    return {
        "final_rows": len(rows),
        "final_max_seq": sum(final.values()),
        "duplicate_keys": len(dup_keys),
        "lost_update_writes": lost_writes,
        "lost_update_keys": lost_keys,
        "integrity_check": integrity,
    }


def run_cell(pattern, cfg_name, journal, bt, writers, writes, repeat, delay_ms, base, deadline):
    db_path = os.path.join(base, f"{pattern}__{cfg_name}__r{repeat}.db")
    init_db(db_path, pattern, journal, bt)
    fixture = build_fixture(writers, writes)
    fixture_max_seq = {}
    for q in fixture:
        for it in q:
            fixture_max_seq[it["key"]] = max(fixture_max_seq.get(it["key"], 0), it["seq"])
    out_q = mp.Queue()
    stop_at = deadline
    procs = [
        mp.Process(target=writer_proc, args=(db_path, pattern, bt, q, delay_ms, out_q, stop_at))
        for q in fixture
    ]
    started = time.time()
    for p in procs:
        p.start()
    records = []
    expected = sum(len(q) for q in fixture)
    deadline_hit = False
    while len(records) < expected:
        try:
            kind, payload = out_q.get(timeout=max(0.2, min(5.0, stop_at - time.time())))
        except Exception:
            if time.time() > stop_at or not any(p.is_alive() for p in procs):
                break
            continue
        if kind == "write":
            records.append(payload)
        else:
            deadline_hit = True
            break
    for p in procs:
        p.join(timeout=5)
        if p.is_alive():
            p.terminate()
    elapsed = time.time() - started
    with open(os.path.join(base, f"{pattern}__{cfg_name}__r{repeat}.jsonl"), "w") as f:
        for r in records:
            f.write(json.dumps({
                "key": r[0], "seq": r[1], "ok": r[2], "error": r[3],
                "detail": r[4], "latency_s": round(r[5], 6),
            }) + "\n")
    ok_writes = [r for r in records if r[2]]
    errors = {}
    for r in records:
        if not r[2]:
            errors[r[3]] = errors.get(r[3], 0) + 1
    lat = sorted(r[5] for r in records) or [0.0]
    p95 = lat[min(len(lat) - 1, int(0.95 * len(lat)))]
    ev = evaluate(db_path, records, fixture_max_seq)
    row = {
        "pattern": pattern, "config": cfg_name, "repeat": repeat,
        "writers": writers, "writes_requested": expected, "writes_seen": len(records),
        "writes_ok": len(ok_writes), "errors": json.dumps(errors),
        "error_count": len(records) - len(ok_writes),
        "lost_update_writes": ev["lost_update_writes"], "lost_update_keys": ev["lost_update_keys"],
        "duplicate_keys": ev["duplicate_keys"], "final_rows": ev["final_rows"],
        "p95_latency_s": round(p95, 6), "elapsed_s": round(elapsed, 2),
        "integrity_check": ev["integrity_check"], "deadline_hit": deadline_hit,
        "db_bytes": os.path.getsize(db_path),
    }
    os.remove(db_path)
    return row


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--writers", type=int, default=4)
    ap.add_argument("--writes", type=int, default=500)
    ap.add_argument("--repeats", type=int, default=1)
    ap.add_argument("--repeat-offset", type=int, default=0)
    ap.add_argument("--rmw-delay-ms", type=float, default=2.0)
    ap.add_argument("--deadline-s", type=float, default=240.0)
    ap.add_argument("--patterns", default=",".join(PATTERNS))
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    deadline = time.time() + args.deadline_s
    patterns = args.patterns.split(",")
    rows = []
    summary_path = os.path.join(args.out, "summary.csv")
    fields = ["pattern", "config", "repeat", "writers", "writes_requested", "writes_seen",
              "writes_ok", "error_count", "errors", "lost_update_writes", "lost_update_keys",
              "duplicate_keys", "final_rows", "p95_latency_s", "elapsed_s", "integrity_check",
              "deadline_hit", "db_bytes"]
    if not os.path.exists(summary_path):
        with open(summary_path, "w", newline="") as f:
            csv.DictWriter(f, fieldnames=fields).writeheader()
    for repeat in range(args.repeat_offset, args.repeat_offset + args.repeats):
        for pattern in patterns:
            for cfg_name, journal, bt in CONFIGS:
                if time.time() > deadline - 15:
                    print(f"[stop] deadline before {pattern}/{cfg_name} r{repeat}")
                    with open(summary_path, "a", newline="") as f:
                        w = csv.DictWriter(f, fieldnames=fields)
                        for r in rows:
                            w.writerow(r)
                    return 0
                row = run_cell(pattern, cfg_name, journal, bt, args.writers, args.writes,
                               repeat, args.rmw_delay_ms, args.out, min(deadline, time.time() + 120))
                rows.append(row)
                with open(summary_path, "a", newline="") as f:
                    csv.DictWriter(f, fieldnames=fields).writerow(row)
                print(json.dumps(row), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
