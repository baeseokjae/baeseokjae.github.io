#!/usr/bin/env python3
"""Envelope fixture for a read-only debugging session.

Answers one question at each layer: does the read-only claim actually refuse
the write, and does the refusal leave a usable record?

Runs locally, standard library only, no network, no paid API, no language
model. The client below is scripted on purpose: it measures the enforcement
layers (database engine, policy gate, expression guard) and the audit record
they produce. It does NOT measure which tools a model would choose.

    python3 fixture_check.py            # writes observed.json next to this file
"""
import ast
import hashlib
import json
import sqlite3
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
DB = HERE / "fixture.db"
ENVELOPE = HERE / "envelope.json"

AUDIT_FIELDS = [
    "session_id", "seq", "ts_utc", "actor_agent_id", "actor_model_id",
    "policy_sha256", "tool", "args_sha256", "decision", "rule_id", "scope",
    "result_sha256", "result_bytes",
]

SEED_SQL = """
CREATE TABLE orders (
  id INTEGER PRIMARY KEY,
  status TEXT NOT NULL,
  total INTEGER NOT NULL,
  customer_email TEXT NOT NULL
);
INSERT INTO orders (id, status, total, customer_email) VALUES
  (1,'paid',20,'a@example.invalid'),
  (2,'paid',55,'b@example.invalid'),
  (3,'paid',140,'c@example.invalid'),
  (4,'refunded',75,'d@example.invalid'),
  (5,'paid',300,'e@example.invalid'),
  (6,'failed',10,'f@example.invalid');
CREATE VIEW v_orders AS SELECT id, status, total FROM orders;
"""

LOG_FIXTURE = [
    {"ts": "2026-11-15T22:04:01Z", "level": "error", "service": "orders-api", "msg": "charge declined: gateway returned 502"},
    {"ts": "2026-11-15T22:04:07Z", "level": "error", "service": "orders-api", "msg": "charge declined: gateway returned 502"},
    {"ts": "2026-11-15T22:06:12Z", "level": "info", "service": "orders-api", "msg": "deploy web-2f91 complete"},
]


def sha(data):
    if isinstance(data, str):
        data = data.encode()
    if not isinstance(data, bytes):
        data = json.dumps(data, sort_keys=True).encode()
    return hashlib.sha256(data).hexdigest()


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def build_db():
    if DB.exists():
        DB.unlink()
    con = sqlite3.connect(DB)
    con.executescript(SEED_SQL)
    con.commit()
    con.close()


def fingerprint(con):
    """Cheap whole-table fingerprint so we can prove nothing mutated."""
    rows = con.execute("SELECT id, status, total, customer_email FROM orders ORDER BY id").fetchall()
    return sha(json.dumps(rows))


# ---------------------------------------------------------------- layer tests
def database_layer():
    """What the engine itself refuses once the transaction is read-only."""
    con = sqlite3.connect(DB)
    con.execute("PRAGMA query_only = ON")
    probes = [
        ("INSERT into the base table", "INSERT INTO orders (id,status,total,customer_email) VALUES (99,'paid',1,'x@example.invalid')"),
        ("UPDATE the base table", "UPDATE orders SET status='refunded' WHERE id=3"),
        ("DELETE from the base table", "DELETE FROM orders WHERE id=3"),
        ("CREATE TABLE", "CREATE TABLE t (id INTEGER)"),
        ("SELECT through the view", "SELECT id, status, total FROM v_orders WHERE total > 50 ORDER BY id"),
        ("CREATE TEMP TABLE (temp schema)", "CREATE TEMP TABLE scratch AS SELECT 1 AS x"),
        ("write to the temp table", "INSERT INTO scratch VALUES (2)"),
    ]
    out = []
    for label, sql in probes:
        try:
            cur = con.execute(sql)
            rows = cur.fetchall() if sql.lstrip().upper().startswith(("SELECT", "INSERT")) else []
            out.append({"probe": label, "sql_head": sql.split()[0].upper(), "refused": False,
                        "error_type": None, "error": None, "rows_returned": len(rows)})
        except Exception as exc:  # noqa: BLE001 - the exception text is the evidence
            out.append({"probe": label, "sql_head": sql.split()[0].upper(), "refused": True,
                        "error_type": type(exc).__name__, "error": str(exc), "rows_returned": None})
    con.close()
    return out


def expr_guard(expr):
    """AST guard: calls and assignments are refused, attribute reads are not."""
    try:
        tree = ast.parse(expr, mode="eval")
    except SyntaxError as exc:
        return {"decision": "deny", "rule_id": "EXPR_CALL", "detail": f"syntax error: {exc.msg}"}
    for node in ast.walk(tree):
        if isinstance(node, (ast.Call, ast.Lambda, ast.NamedExpr, ast.ListComp, ast.DictComp)):
            name = type(node).__name__
            attr = ""
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                attr = f" (method {node.func.attr}())"
            return {"decision": "deny", "rule_id": "EXPR_CALL", "detail": f"refused: {name}{attr}"}
        if isinstance(node, (ast.Assign, ast.AugAssign, ast.AnnAssign)):
            return {"decision": "deny", "rule_id": "EXPR_ASSIGN", "detail": "refused: assignment"}
    return {"decision": "allow", "rule_id": None, "detail": "compare-only expression"}


def sql_guard(stmt):
    stripped = stmt.strip()
    if ";" in stripped.rstrip(";"):
        return {"rule_id": "SQL_MULTI_STATEMENT"}
    head = stripped.split()[0].upper() if stripped else ""
    if head not in ("SELECT", "WITH"):
        return {"rule_id": "SQL_NOT_SELECT"}
    return None


# ---------------------------------------------------------------- the session
class Session:
    def __init__(self, envelope):
        self.env = envelope
        self.policy_sha = sha(ENVELOPE.read_bytes())
        self.session_id = "sess-" + sha(f"{time.time()}")[:12]
        self.records = []
        self.calls = []

    def record(self, tool, args, decision, rule_id, result, detail):
        seq = len(self.records) + 1
        payload = result if result is not None else None
        blob = b"" if payload is None else json.dumps(payload, sort_keys=True).encode()
        self.records.append({
            "session_id": self.session_id,
            "seq": seq,
            "ts_utc": now(),
            "actor_agent_id": "agent:fixture-driver",
            "actor_model_id": None,          # scripted client: no model was used
            "policy_sha256": self.policy_sha,
            "tool": tool,
            "args_sha256": sha(json.dumps(args, sort_keys=True)),
            "decision": decision,
            "rule_id": rule_id,
            "scope": self.env["scope"],
            "result_sha256": None if payload is None else sha(blob),
            "result_bytes": None if payload is None else len(blob),
            "detail": detail,
        })

    def call(self, tool, args=None, sql=None, expr=None):
        args = args or {}
        declared = {t["name"]: t for t in self.env["tools"]}
        if tool not in declared:
            entry = {"refused": True, "rule_id": "UNKNOWN_TOOL",
                     "message_for_caller": f"DENIED by UNKNOWN_TOOL: '{tool}' is not declared in this envelope"}
            self.record(tool, args, "deny", "UNKNOWN_TOOL", None, entry["message_for_caller"])
            self.calls.append({"tool": tool, "decision": "deny", "rule_id": "UNKNOWN_TOOL"})
            return entry
        spec = declared[tool]
        if spec["decision"] == "deny":
            msg = f"DENIED by TOOL_DENIED: '{tool}' is declared but the envelope denies it ({spec['note']})"
            self.record(tool, args, "deny", "TOOL_DENIED", None, msg)
            self.calls.append({"tool": tool, "decision": "deny", "rule_id": "TOOL_DENIED"})
            return {"refused": True, "rule_id": "TOOL_DENIED", "message_for_caller": msg}
        if sql is not None:
            bad = sql_guard(sql)
            if bad:
                msg = f"DENIED by {bad['rule_id']}: statement was not executed"
                self.record(tool, {"sql": sql}, "deny", bad["rule_id"], None, msg)
                self.calls.append({"tool": tool, "decision": "deny", "rule_id": bad["rule_id"]})
                return {"refused": True, **bad, "message_for_caller": msg}
        if expr is not None:
            verdict = expr_guard(expr)
            if verdict["decision"] == "deny":
                msg = f"DENIED by {verdict['rule_id']}: {verdict['detail']}"
                self.record(tool, {"expr": expr}, "deny", verdict["rule_id"], None, msg)
                self.calls.append({"tool": tool, "decision": "deny", "rule_id": verdict["rule_id"]})
                return {"refused": True, "rule_id": verdict["rule_id"], "message_for_caller": msg}
        result = self.run(tool, args, sql, expr)
        self.record(tool, {"args": args, "sql": sql, "expr": expr}, "allow", None, result, "allowed")
        self.calls.append({"tool": tool, "decision": "allow", "rule_id": None})
        return {"refused": False, "result": result}

    def run(self, tool, args, sql, expr):
        con = sqlite3.connect(DB)
        con.execute("PRAGMA query_only = ON")           # second enforcement point
        try:
            if tool == "db_schema":
                rows = con.execute("SELECT type, name FROM sqlite_master WHERE name NOT LIKE 'sqlite_%' ORDER BY name").fetchall()
                return [{"type": t, "name": n} for t, n in rows]
            if tool == "db_query":
                return [dict(zip([c[0] for c in con.execute(sql).description], r))
                        for r in con.execute(sql).fetchmany(self.env["scope"]["max_rows"])]
            if tool == "log_query":
                level = args.get("level")
                return [r for r in LOG_FIXTURE if r["level"] == level]
            if tool == "metric_read":
                return {"service": "orders-api", "p95_ms": 412, "error_rate": 0.031}
            if tool == "probe_condition":
                captures = {"total": 55, "status": "paid"}
                return {"expr": expr, "evaluated": eval(  # noqa: S307 - guarded above
                    compile(ast.parse(expr, mode="eval"), "<probe>", "eval"), {}, captures)}
        finally:
            con.close()
        return None


def main():
    envelope = json.loads(ENVELOPE.read_text())
    build_db()

    con = sqlite3.connect(DB)
    before = fingerprint(con)
    con.close()

    t0 = time.perf_counter()
    db = database_layer()
    s = Session(envelope)
    s.call("db_schema")
    s.call("log_query", {"service": "orders-api", "level": "error"})
    s.call("db_query", sql="SELECT id, status, total FROM v_orders WHERE total > 50 ORDER BY id")
    s.call("update_order_status", {"order_id": 3, "status": "refunded"})
    s.call("db_query", sql="UPDATE orders SET status='refunded' WHERE id=3")
    s.call("db_query", sql="SELECT 1; DROP TABLE orders")
    s.call("shell", {"cmd": "psql -c 'delete from orders'"})
    s.call("probe_condition", {"order_id": 3}, expr="order.get_total() > 50")
    s.call("probe_condition", {"order_id": 3}, expr="total > 50")
    elapsed_ms = round((time.perf_counter() - t0) * 1000, 1)

    con = sqlite3.connect(DB)
    after = fingerprint(con)
    remaining = con.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
    con.close()

    present = [f for f in AUDIT_FIELDS if all(r.get(f) is not None for r in s.records)]
    missing = [f for f in AUDIT_FIELDS if f not in present]
    denied = [c for c in s.calls if c["decision"] == "deny"]
    rules = sorted({c["rule_id"] for c in denied})

    observed = {
        "slug": "hyperprobe-readonly-debugging-agents-2026",
        "generated_at": now(),
        "what_this_is": "Local fixture check of the enforcement layers and the audit record. Scripted client, no language model, no network, no vendor system.",
        "environment": {"python": sys.version.split()[0], "sqlite": sqlite3.sqlite_version,
                        "os": sys.platform},
        "database_layer": db,
        "tool_layer": {
            "calls": s.calls,
            "attempted": len(s.calls),
            "allowed": len(s.calls) - len(denied),
            "denied": len(denied),
            "rules_fired": rules,
        },
        "audit": {
            "fields_declared": AUDIT_FIELDS,
            "fields_populated_on_every_record": present,
            "fields_missing": missing,
            "records": s.records,
        },
        "integrity": {
            "orders_fingerprint_before": before,
            "orders_fingerprint_after": after,
            "unchanged": before == after,
            "rows_remaining": remaining,
        },
        "limits": [
            "Scripted client: which tools a model chooses, and whether it retries after a refusal, was not measured.",
            "The expression guard is a small AST allow/deny check written for this fixture, not a vendor implementation and not Runtime.evaluate's throwOnSideEffect.",
            "SQLite PRAGMA query_only is a different mechanism from PostgreSQL SET TRANSACTION READ ONLY; the two are compared in the article, not substituted for each other.",
            "Single-process, single-file database on a laptop-class host: no concurrency, latency or overhead claim is supported by this run.",
        ],
    }
    (HERE / "observed.json").write_text(json.dumps(observed, indent=2) + "\n")
    print(json.dumps({
        "elapsed_ms": elapsed_ms,
        "db_probes_refused": sum(1 for p in db if p["refused"]),
        "db_probes_total": len(db),
        "db_refusals": {p["probe"]: (p["error_type"] + ": " + p["error"]) if p["refused"] else "ALLOWED"
                        for p in db},
        "tool_calls": len(s.calls),
        "allowed": observed["tool_layer"]["allowed"],
        "denied": len(denied),
        "rules_fired": rules,
        "audit_present": len(present),
        "audit_missing": missing,
        "db_unchanged": observed["integrity"]["unchanged"],
    }, indent=2))


if __name__ == "__main__":
    main()
