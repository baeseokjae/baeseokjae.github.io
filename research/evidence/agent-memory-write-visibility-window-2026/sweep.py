#!/usr/bin/env python3
"""Write-visibility-window sweep (agent-memory-write-visibility-window-2026).

Three adapters behind one interface, write(key,value) / search(key):
  (a) sync-control : embed + upsert before write() returns.
  (b) two-phase    : write() returns after the record-store commit; a background
                     worker embeds and commits to the vector index on a free-running
                     tick of T ms (ticks at T, 2T, 3T ... independent of writes).
  (c) batch-flush  : writes buffer, flushed every N writes or on the same tick.

Fake clock: (b)/(c) advance a simulated clock, so the stale/fresh classification
cannot depend on host jitter. The embedder cost injected into that timeline is the
REAL measured latency of the same text on this host. Real wall-clock numbers come
from the live-poll section, which uses a real thread and a real 1 s tick.

Fixture: 12 stable facts x 4 entity types, seeded before measurement; 30 correction
turns, each of which updates one fact and immediately reads it back (read-your-writes).
Per-turn clock advance 2000 ms = one agent turn; post-write read gap 50 ms.
"""
import json, math, os, statistics, threading, time, urllib.request

OLLAMA = "http://127.0.0.1:11434/api/embed"
MODEL = "all-minilm"
OUT = os.path.dirname(os.path.abspath(__file__))

def embed(text):
    body = json.dumps({"model": MODEL, "input": text}).encode()
    req = urllib.request.Request(OLLAMA, data=body, headers={"Content-Type": "application/json"})
    t0 = time.perf_counter()
    with urllib.request.urlopen(req, timeout=60) as r:
        d = json.load(r)
    return d["embeddings"][0], (time.perf_counter() - t0) * 1000.0

ENTITIES = [
    ("deploy_target", "api-service"), ("deploy_target", "billing-worker"),
    ("deploy_target", "search-gateway"), ("deploy_target", "ingest-cron"),
    ("token_rotation", "github-app"), ("token_rotation", "openai-key"),
    ("token_rotation", "grafana-sa"), ("token_rotation", "smtp-relay"),
    ("oncall_owner", "payments"), ("oncall_owner", "platform"),
    ("retention_days", "audit-log"), ("retention_days", "trace-spans"),
]
VALUES = {
    "deploy_target": ["db-07", "db-08", "db-09", "db-10", "db-11"],
    "token_rotation": ["90d", "60d", "45d", "30d", "14d"],
    "oncall_owner": ["mira", "tomas", "inez", "ravi", "jun"],
    "retention_days": ["400d", "365d", "180d", "120d", "90d"],
}

def rec(kind, ent, val, turn=0):
    return {"turn": turn, "fact_id": f"{kind}:{ent}", "kind": kind, "entity": ent,
            "value": val, "text": f"{kind} for {ent}: {val}",
            "query": f"current {kind.replace('_', ' ')} for {ent}"}

seeds = [rec(k, e, VALUES[k][0]) for k, e in ENTITIES]
turns = [rec(k, e, VALUES[k][1 + ((i // len(ENTITIES)) % 4)], i + 1)
         for i, (k, e) in enumerate([ENTITIES[i % len(ENTITIES)] for i in range(30)])]

# ---- measure the embedder term once, cache vectors ----
vec, ems = {}, {}
t_all = time.perf_counter()
for r in seeds + turns:
    if r["text"] not in vec:
        v, ms = embed(r["text"]); vec[r["text"]] = v; ems[r["text"]] = ms
embed_wall = time.perf_counter() - t_all
et = sorted(ems.values())

class Base:
    T = 0; N = 1
    def __init__(self):
        self.kv, self.idx = {}, {}
    def search(self, r):
        hit = self.idx.get(r["fact_id"])
        return None if hit is None else hit[0]
    def commit(self, items):
        cost = max((ems[x["text"]] for x in items), default=0.0)
        for x in items:
            self.idx[x["fact_id"]] = (x["value"], vec[x["text"]])
        return cost
    def seed(self, r, now_ms):
        """Seed through the fast path so every fact has a prior value."""
        self.kv[r["fact_id"]] = r["value"]
        self.commit([r])
        return now_ms

class SyncControl(Base):
    name = "sync-control"
    def write(self, r, now_ms):
        self.kv[r["fact_id"]] = r["value"]
        return now_ms + self.commit([r])          # embed + upsert inline
    def tick(self, now_ms): return now_ms

class TwoPhase(Base):
    name = "two-phase-async"
    def __init__(self, interval_ms):
        super().__init__(); self.T = interval_ms; self.pending = {}; self.next_tick = interval_ms
    def write(self, r, now_ms):
        self.kv[r["fact_id"]] = r["value"]        # record store commit, index deferred
        self.pending[r["fact_id"]] = r
        return now_ms
    def tick(self, now_ms):
        if self.T <= 0 and self.pending:
            cost = self.commit(self.pending.values()); self.pending = {}; return now_ms + cost
        if self.T <= 0: return now_ms
        while self.next_tick <= now_ms:
            if self.pending:
                cost = self.commit(self.pending.values()); self.pending = {}
                self.next_tick += self.T
                return now_ms + cost
            self.next_tick += self.T
        return now_ms

class BatchFlush(Base):
    name = "batch-flush"
    def __init__(self, interval_ms, batch):
        super().__init__(); self.T = interval_ms; self.N = batch; self.buf = []; self.next_tick = interval_ms
    def write(self, r, now_ms):
        self.kv[r["fact_id"]] = r["value"]; self.buf.append(r)
        if len(self.buf) >= self.N: self.commit(self.buf); self.buf = []
        return now_ms
    def tick(self, now_ms):
        if self.T <= 0: return now_ms
        if not self.buf:                       # ticker keeps free-running on an empty buffer
            while self.next_tick <= now_ms: self.next_tick += self.T
            return now_ms
        if self.next_tick <= now_ms:
            while self.next_tick <= now_ms: self.next_tick += self.T
            cost = self.commit(self.buf); self.buf = []
            return now_ms + cost
        return now_ms

GAP_MS, ADVANCE_MS = 50.0, 2000.0

def run(ad):
    now = 0.0
    for s in seeds:
        now = ad.seed(s, now)
    now = max(now, ad.T + 1.0)                    # let the seed commit land
    rows = []
    for r in turns:
        now = ad.tick(now)                        # the ticker runs during the turn, before the write
        now = ad.write(r, now)
        now = ad.tick(now)
        q_at = now + GAP_MS
        ad.tick(q_at)                             # a tick inside the read gap
        got = ad.search(r)
        outcome = "fresh" if got == r["value"] else ("stale-value" if got else "nothing")
        rows.append({"turn": r["turn"], "fact_id": r["fact_id"], "expected": r["value"],
                     "returned": got, "outcome": outcome,
                     "commit_interval_ms": ad.T, "batch": ad.N})
        now = q_at + ADVANCE_MS
    return rows

configs = [("sync-control", lambda: SyncControl())]
configs += [(f"two-phase-async/T={T}ms", (lambda T=T: TwoPhase(T))) for T in (0, 250, 1000, 5000)]
configs += [(f"batch-flush/T={T}ms/N={N}", (lambda T=T, N=N: BatchFlush(T, N)))
            for T in (1000, 5000) for N in (1, 8, 32)]

results = []
with open(os.path.join(OUT, "fixture.jsonl"), "w") as f:
    for s in seeds: f.write(json.dumps(dict(s, role="seed")) + "\n")
    for t in turns: f.write(json.dumps(dict(t, role="correction")) + "\n")

with open(os.path.join(OUT, "results.jsonl"), "w") as f:
    for name, mk in configs:
        rows = run(mk())
        stale = sum(r["outcome"] == "stale-value" for r in rows)
        rec_ = {"config": name, "n_turns": len(rows), "turn_gap_ms": GAP_MS,
                "turn_advance_ms": ADVANCE_MS, "stale_value_reads": stale,
                "fresh_reads": sum(r["outcome"] == "fresh" for r in rows),
                "no_result_reads": sum(r["outcome"] == "nothing" for r in rows),
                "stale_share": round(stale / len(rows), 3),
                "embedder_model": MODEL, "embed_dims": 384}
        results.append(rec_)
        for row in rows:
            f.write(json.dumps(dict(row, config=name)) + "\n")

# ---- live wall-clock poll: real thread, real 1 s tick, real embedder ----
live = []
for trial in range(5):
    store, lock, stop = {"kv": {}, "idx": {}}, threading.Lock(), threading.Event()
    def worker():
        while not stop.is_set():
            with lock: pend = dict(store["kv"])
            for fid, (val, text) in pend.items():
                v, _ = embed(text)
                with lock: store["idx"][fid] = (val, v)
            stop.wait(1.0)
    threading.Thread(target=worker, daemon=True).start()
    time.sleep(0.05)
    tok = f"CANARY-{trial}-{int(time.time() * 1000)}"
    fid, text = "deploy_target:api-service", f"deploy target for api-service: {tok}"
    t0 = time.perf_counter()
    with lock: store["kv"][fid] = (tok, text)
    seen = None
    while time.perf_counter() - t0 < 10.0:
        with lock: got = store["idx"].get(fid)
        if got and got[0] == tok:
            seen = (time.perf_counter() - t0) * 1000.0; break
        time.sleep(0.01)
    stop.set(); time.sleep(0.02)
    live.append({"trial": trial, "visibility_ms": None if seen is None else round(seen, 1)})

vis = [x["visibility_ms"] for x in live if x["visibility_ms"]]
summary = {
    "host": os.uname().nodename, "nproc": os.cpu_count(),
    "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "embedder": {"model": MODEL, "dims": 384, "endpoint": OLLAMA},
    "embed_unique_texts": len(vec), "embed_total_wall_s": round(embed_wall, 3),
    "embed_single_ms_median": round(statistics.median(et), 1),
    "embed_single_ms_p95": round(et[max(0, int(len(et) * 0.95) - 1)], 1),
    "embed_single_ms_min": round(et[0], 1), "embed_single_ms_max": round(et[-1], 1),
    "turn_gap_ms_simulated": GAP_MS, "turn_advance_ms_simulated": ADVANCE_MS,
    "live_poll": live,
    "live_poll_visibility_ms_median": round(statistics.median(vis), 1) if vis else None,
    "live_poll_visibility_ms_min": round(min(vis), 1) if vis else None,
    "live_poll_visibility_ms_max": round(max(vis), 1) if vis else None,
}
with open(os.path.join(OUT, "environment.json"), "w") as f:
    json.dump(summary, f, indent=2)
print(json.dumps(summary, indent=2))
for r in results: print(json.dumps(r))
