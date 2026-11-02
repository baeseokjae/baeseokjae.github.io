#!/usr/bin/env python3
"""readback_probe.py -- after a delete says OK, can the fact still be read?

Runs four deletion paths against one store, then six recall probes per path
(one verbatim, five paraphrased) and writes one JSONL record per probe with:

    path, target, probe_id, query, api_return, vector_present, raw_row_present,
    recall_ids, recall_hit, returned_text, history_row_returned_after_delete,
    history_contains_deleted_text, timestamp

Stdlib only. Python 3.9+.

Built-in adapter `reference` is a deliberately small SQLite store used as a
fixture check, NOT a vendor product and NOT a measurement of any vendor. Its
audit table imitates the pattern this article audits (a DELETE row keeping the
old text, and a read API that does not filter deleted rows), so the probe can
be shown detecting a leak; --history-filtered flips that read API to exclude
deleted rows, which must make the same probe report zero leaks. A clean result
from a store you wrote yourself is not evidence about anyone else's store.

To test your own store, implement the six methods in ADAPTER API below (about
40 lines), point --adapter at your module as path/to/file.py:ClassName, and keep
the four paths. Do not weaken the probes: each one must be a sentence a real
user could type, and recall_hit is decided by the sentinel string, not by you.
"""
import argparse
import json
import re
import sqlite3
import sys
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

STOP = set("the a an and or of to for in on at is was are were do does did "
           "this that it its with by from as be been being what when who "
           "which how our we i you they them their".split())


def tokens(text):
    return [w for w in re.findall(r"[a-z0-9]+", text.lower()) if w not in STOP]


def overlap(query, text):
    q, t = set(tokens(query)), set(tokens(text))
    return len(q & t) / (len(q) or 1)


class ReferenceStore:
    """Minimal memory store: one table for facts, one audit table, brute-force recall."""

    def __init__(self, history_filtered=False):
        self.db = sqlite3.connect(":memory:")
        self.db.row_factory = sqlite3.Row
        self.history_filtered = history_filtered
        self.db.executescript("""
            CREATE TABLE memories (id TEXT PRIMARY KEY, text TEXT, meta TEXT, created_at TEXT);
            CREATE TABLE audit (id TEXT PRIMARY KEY, memory_id TEXT, old_text TEXT,
                                event TEXT, is_deleted INTEGER, created_at TEXT);
        """)

    def add(self, text, metadata, created_at=None):
        mid = str(uuid.uuid4())
        created_at = created_at or datetime.now(timezone.utc).isoformat()
        self.db.execute("INSERT INTO memories VALUES (?,?,?,?)",
                        (mid, text, json.dumps(metadata), created_at))
        return mid

    def search(self, query, k=3):
        rows = self.db.execute("SELECT id, text FROM memories").fetchall()
        scored = sorted(((overlap(query, r["text"]), r["id"], r["text"]) for r in rows),
                        reverse=True)
        return [{"id": i, "text": t, "score": round(s, 3)}
                for s, i, t in scored[:k] if s > 0.2]

    def delete_by_id(self, memory_id):
        row = self.db.execute("SELECT text, created_at FROM memories WHERE id=?",
                              (memory_id,)).fetchone()
        if row is None:
            raise ValueError(f"memory {memory_id} not found")
        self.db.execute("DELETE FROM memories WHERE id=?", (memory_id,))
        self.db.execute("INSERT INTO audit VALUES (?,?,?,?,?,?)",
                        (str(uuid.uuid4()), memory_id, row["text"], "DELETE", 1,
                         datetime.now(timezone.utc).isoformat()))
        return {"message": "Memory deleted successfully!"}

    def delete_by_filter(self, metadata):
        clauses = " AND ".join(f"json_extract(meta,'$.{k}')=?" for k in metadata)
        rows = self.db.execute(f"SELECT id FROM memories WHERE {clauses}",
                               tuple(metadata.values())).fetchall()
        for r in rows:
            self.delete_by_id(r["id"])
        return {"message": f"{len(rows)} memories deleted"}

    def history(self, memory_id):
        sql = "SELECT memory_id, old_text, event, is_deleted FROM audit WHERE memory_id=?"
        if self.history_filtered:
            sql += " AND is_deleted=0"
        return [dict(r) for r in self.db.execute(sql, (memory_id,)).fetchall()]

    def recall_present(self, memory_id):
        return self.db.execute("SELECT 1 FROM memories WHERE id=?",
                               (memory_id,)).fetchone() is not None

    def raw_row_present(self, memory_id):
        return self.recall_present(memory_id)


# ---------------------------------------------------------------- ADAPTER API
# Any store works if the class exposes: add(text, metadata, created_at=None)->id,
# search(query, k=3)->[{"id","text","score"}], delete_by_id(id)->the call's own
# return value, delete_by_filter(metadata)->same, history(id)->rows or list,
# recall_present(id)->bool, raw_row_present(id)->bool.
# ----------------------------------------------------------------


def resolve_forget_intent(store, instruction, k=3):
    """Stand-in for a 'forget this' tool: score candidates, delete the best one."""
    hits = store.search(instruction.replace("forget", ""), k=k)
    if not hits:
        return None, []
    return hits[0]["id"], hits


def run(store_factory, fixture, out_path):
    now = datetime.now(timezone.utc)
    records, summary = [], {}
    for path in fixture["deletion_paths"]:
        fact = next(f for f in fixture["facts"] if f["key"] == path["target"])
        store = store_factory()
        ids = {f["key"]: store.add(f["text"], {"user_id": fixture["tenant"]["user_id"],
                                               "topic": f["topic"]},
                                   created_at=(now - timedelta(days=30)).isoformat()
                                   if f["key"] in ("f6", "f7") else now.isoformat())
               for f in fixture["facts"]}
        target = ids[fact["key"]]

        if path["path"] == "delete_by_id":
            api_return = store.delete_by_id(target)
        elif path["path"] == "delete_by_filter":
            api_return = store.delete_by_filter({"user_id": fixture["tenant"]["user_id"],
                                                 "topic": fact["topic"]})
        elif path["path"] == "forget_intent":
            resolved, hits = resolve_forget_intent(
                store, "forget the name of the security questionnaire contact")
            api_return = store.delete_by_id(resolved) if resolved else {"message": "no candidate"}
        elif path["path"] == "ttl_expiry":
            api_return = expire(store, now, ttl_days=7)
        else:
            raise SystemExit(f"unknown path {path['path']}")

        hist = store.history(target)
        hist_text = json.dumps(hist)
        path_leaks = 0
        for probe in fact["probes"]:
            hits = store.search(probe["query"])
            hit = any(fact["sentinel"].lower() in h["text"].lower() for h in hits)
            path_leaks += int(hit)
            records.append({
                "path": path["path"],
                "target": fact["key"],
                "target_text_sentinel": fact["sentinel"],
                "probe_id": probe["id"],
                "query": probe["query"],
                "api_return": api_return,
                "vector_present": store.recall_present(target),
                "raw_row_present": store.raw_row_present(target),
                "recall_ids": [h["id"] for h in hits],
                "recall_hit": hit,
                "returned_text": [h["text"] for h in hits],
                "history_row_returned_after_delete": bool(hist),
                "history_contains_deleted_text": fact["sentinel"].lower() in hist_text.lower(),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })
        summary[path["path"]] = {
            "probes": len(fact["probes"]),
            "recall_hits": path_leaks,
            "history_returns_deleted_text": fact["sentinel"].lower() in hist_text.lower(),
            "failed": path_leaks > 0 or fact["sentinel"].lower() in hist_text.lower(),
        }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as fh:
        for rec in records:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    return records, summary


def expire(store, now, ttl_days):
    """TTL sweep: delete rows whose created_at is older than the TTL.

    Uses the adapter's own hook when it has one; otherwise falls back to the
    reference store's table, so a vendor adapter must implement expire_older_than().
    """
    cutoff = (now - timedelta(days=ttl_days)).isoformat()
    if hasattr(store, "expire_older_than"):
        return store.expire_older_than(cutoff)
    rows = store.db.execute("SELECT id, created_at FROM memories").fetchall()
    stale = [r["id"] for r in rows if r["created_at"] < cutoff]
    for mid in stale:
        store.delete_by_id(mid)
    return {"message": f"ttl sweep deleted {len(stale)}"}


def load_adapter(spec):
    if spec == "reference":
        return lambda: ReferenceStore()
    if spec == "reference-filtered":
        return lambda: ReferenceStore(history_filtered=True)
    module_path, _, cls = spec.partition(":")
    sys.path.insert(0, str(Path(module_path).resolve().parent))
    mod = __import__(Path(module_path).stem)
    return getattr(mod, cls)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--store", default="reference",
                    help="reference | reference-filtered | path/to/adapter.py:ClassName")
    ap.add_argument("--fixture", default="fixtures/memory_facts.json")
    ap.add_argument("--out", default=None, help="JSONL output path")
    args = ap.parse_args()

    fixture = json.loads(Path(args.fixture).read_text())
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = Path(args.out or f"results/{args.store.replace(':','-').replace('/','_')}-{stamp}.jsonl")
    records, summary = run(load_adapter(args.store), fixture, out)
    print(json.dumps({"store": args.store, "records": len(records), "out": str(out),
                      "per_path": summary}, indent=2))


if __name__ == "__main__":
    main()
