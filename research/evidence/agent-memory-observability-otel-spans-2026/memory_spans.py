#!/usr/bin/env python3
"""Minimal, dependency-free instrumentation of a local SQLite memory store.

Emits spans that follow the OpenTelemetry GenAI semantic conventions for memory
operations (span type `gen_ai.memory.client`, operations create_memory /
search_memory / delete_memory). Output is OTLP/JSON shape so it can be replayed
into a Collector; no SDK or network needed. Spec status: Development (see
research brief for the pinned commit).
"""
import hashlib, json, os, random, sqlite3, time, uuid

STORE_ID = "fixture-store"
PROVIDER = "sqlite.local"          # custom value; gen_ai.provider.name is Conditionally Required
NAMESPACE = "fixture"

def _hex(n): return uuid.uuid4().hex[:n]
def _now(): return str(time.time_ns())

class Recorder:
    def __init__(self): self.resource_spans = []
    def span(self, trace, parent, name, kind, start, end, attrs, status=1):
        return {"traceId": trace, "spanId": _hex(16), "parentSpanId": parent,
                "name": name, "kind": kind, "startTimeUnixNano": start,
                "endTimeUnixNano": end,
                "attributes": [{"key": k, "value": v} for k, v in attrs.items()],
                "status": {"code": status}}
    def flush(self, spans):
        self.resource_spans.append({"resource": {"attributes": [
            {"key": "service.name", "value": {"stringValue": "memory-instrumentation-fixture"}}]},
            "scopeSpans": [{"scope": {"name": "rockb.memory.sqlite", "version": "0.1.0"},
                            "spans": spans}]})

def key_hash(key: str) -> str:
    return hashlib.sha256(key.encode()).hexdigest()[:16]

def connect(path):
    con = sqlite3.connect(path)
    con.execute("CREATE TABLE IF NOT EXISTS memory (ns TEXT, key TEXT, value TEXT, "
                "updated_at REAL, PRIMARY KEY (ns, key))")
    return con

def create_memory(con, rec, trace, parent, rows):
    """rows: list of (key, value). One span per batch write."""
    st, t0 = _now(), time.perf_counter()
    with con:
        for k, v in rows:
            con.execute("INSERT OR REPLACE INTO memory VALUES (?,?,?,?)",
                        (NAMESPACE, k, v, time.time()))
    attrs = {"gen_ai.operation.name": {"stringValue": "create_memory"},
             "gen_ai.provider.name": {"stringValue": PROVIDER},
             "gen_ai.memory.store.id": {"stringValue": STORE_ID},
             "gen_ai.memory.record.count": {"intValue": str(len(rows))},
             "memory.write.batch_keys": {"stringValue": ",".join(key_hash(k) for k, _ in rows[:3])},
             "memory.op.duration_ms": {"doubleValue": (time.perf_counter() - t0) * 1000}}
    return rec.span(trace, parent, "create_memory", 1, st, _now(), attrs)

def search_memory(con, rec, trace, parent, query, top_k=3):
    st, t0 = _now(), time.perf_counter()
    cur = con.execute("SELECT key, value FROM memory WHERE ns=? AND value LIKE ? LIMIT ?",
                      (NAMESPACE, f"%{query}%", top_k))
    hits = cur.fetchall()
    attrs = {"gen_ai.operation.name": {"stringValue": "search_memory"},
             "gen_ai.provider.name": {"stringValue": PROVIDER},
             "gen_ai.memory.store.id": {"stringValue": STORE_ID},
             "gen_ai.memory.record.count": {"intValue": str(len(hits))},
             "gen_ai.memory.query.text": {"stringValue": query},   # Opt-In in the spec
             "memory.hit": {"boolValue": bool(hits)},
             "memory.candidate_count": {"intValue": str(len(hits))},
             "memory.op.duration_ms": {"doubleValue": (time.perf_counter() - t0) * 1000}}
    return rec.span(trace, parent, "search_memory", 1, st, _now(), attrs), hits

def delete_memory(con, rec, trace, parent, key, reason):
    st, t0 = _now(), time.perf_counter()
    with con:
        n = con.execute("DELETE FROM memory WHERE ns=? AND key=?", (NAMESPACE, key)).rowcount
    attrs = {"gen_ai.operation.name": {"stringValue": "delete_memory"},
             "gen_ai.provider.name": {"stringValue": PROVIDER},
             "gen_ai.memory.store.id": {"stringValue": STORE_ID},
             "gen_ai.memory.record.id": {"stringValue": key_hash(key)},
             "gen_ai.memory.record.count": {"intValue": str(n)},
             "memory.evicted_reason": {"stringValue": reason},
             "memory.op.duration_ms": {"doubleValue": (time.perf_counter() - t0) * 1000}}
    return rec.span(trace, parent, "delete_memory", 1, st, _now(), attrs)

def main(out_dir):
    db = os.path.join(out_dir, "memory.sqlite")
    if os.path.exists(db): os.remove(db)
    con, rec = connect(db), Recorder()

    facts = [(f"fact-{i:02d}", f"fixture fact {i} about topic{'ab'[i % 2]}") for i in range(50)]
    # induced stale fact: written once, then overwritten by a later write without invalidation of an
    # in-memory cache held by the agent (simulated by reading before the overwrite)
    stale = ("fact-stale", "user timezone is UTC+8")
    facts.append(stale)

    t_write = _hex(32); p_write = _hex(16)
    s = [rec.span(t_write, "", "invoke_agent memory-fixture", 1, _now(), _now(),
                  {"gen_ai.operation.name": {"stringValue": "invoke_agent"},
                   "gen_ai.agent.name": {"stringValue": "memory-fixture"}})]
    s.append(create_memory(con, rec, t_write, p_write, facts))
    rec.flush(s)

    t_read = _hex(32); p_read = _hex(16)
    s = [rec.span(t_read, "", "invoke_agent memory-fixture", 1, _now(), _now(),
                  {"gen_ai.operation.name": {"stringValue": "invoke_agent"},
                   "gen_ai.agent.name": {"stringValue": "memory-fixture"}})]
    sp, hits_before = search_memory(con, rec, t_read, p_read, "timezone")
    s.append(sp)

    # the value changes upstream; the agent's cached answer is now stale
    con.execute("UPDATE memory SET value=?, updated_at=? WHERE ns=? AND key=?",
                ("user timezone is UTC+9 (Asia/Seoul)", time.time(), NAMESPACE, "fact-stale"))
    con.commit()
    sp2, hits_after = search_memory(con, rec, t_read, p_read, "timezone")
    s.append(sp2)
    rec.flush(s)

    t_evict = _hex(32); p_evict = _hex(16)
    s = [rec.span(t_evict, "", "invoke_agent memory-fixture", 1, _now(), _now(),
                  {"gen_ai.operation.name": {"stringValue": "invoke_agent"},
                   "gen_ai.agent.name": {"stringValue": "memory-fixture"}})]
    s.append(delete_memory(con, rec, t_evict, p_evict, "fact-stale", "superseded_by_newer_value"))
    rec.flush(s)

    with open(os.path.join(out_dir, "spans.json"), "w") as f:
        json.dump({"resourceSpans": rec.resource_spans}, f, indent=1)

    counts = {}
    for rs in rec.resource_spans:
        for ss in rs["scopeSpans"]:
            for sp in ss["spans"]:
                counts[sp["name"]] = counts.get(sp["name"], 0) + 1
    print("span counts:", json.dumps(counts, sort_keys=True))
    print("pre-update hits:", hits_before)
    print("post-update hits:", hits_after)
    print("rows remaining:", con.execute("SELECT COUNT(*) FROM memory").fetchone()[0])
    print("traces:", 3, "total spans:", sum(counts.values()))
    con.close()

if __name__ == "__main__":
    import sys
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
