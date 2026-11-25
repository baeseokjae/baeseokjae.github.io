#!/usr/bin/env python3
"""EXP-MEMDEDUPE-THRESHOLD: pair separability + store consequence + token guard.

Stdlib only. Embeddings via Ollama /api/embed at http://127.0.0.1:11434/api/embed.
Writes pairs.json, results.jsonl, sweep.csv, summary.json into the out dir.
"""
import json, math, os, re, sys, time, urllib.request

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
URL = "http://127.0.0.1:11434/api/embed"
MODELS = ["all-minilm:latest", "snowflake-arctic-embed:33m", "nomic-embed-text:latest"]
TAUS = [round(0.80 + 0.005 * i, 4) for i in range(40)] + [0.999]

PAIRS = []
def add(pid, cls, a, b, prov):
    PAIRS.append({"id": pid, "class": cls, "a": a, "b": b, "provenance": prov})

# --- 16 paraphrase pairs: same fact, different wording (SHOULD merge)
add("P01", "paraphrase", "The checkout service listens on port 5432 in production.",
    "Production checkout traffic is served over TCP port 5432.", "port; same number, reworded")
add("P02", "paraphrase", "The billing API binds to port 8443.",
    "Billing API listens on 8443.", "port; terse restatement")
add("P03", "paraphrase", "The session cache TTL is 60 seconds.",
    "Session cache entries expire after 60 seconds.", "TTL; noun form vs verb form")
add("P04", "paraphrase", "The rate limiter window resets every 15 minutes.",
    "The rate limiter window length is 15 minutes.", "TTL/window; resets-every vs length")
add("P05", "paraphrase", "Primary Postgres runs in eu-west-1.",
    "The Postgres primary is hosted in the eu-west-1 region.", "region; hosted-in vs runs-in")
add("P06", "paraphrase", "Object storage buckets live in ap-southeast-2.",
    "S3 buckets are provisioned in ap-southeast-2.", "region; S3 synonym for object storage")
add("P07", "paraphrase", "The payment client retries 3 times before failing.",
    "Payment calls are retried up to 3 times.", "retry count; active vs passive")
add("P08", "paraphrase", "The webhook sender retries 5 times with exponential backoff.",
    "Webhook delivery is retried 5 times using exponential backoff.", "retry count; delivery vs sender")
add("P09", "paraphrase", "Log retention is 30 days.",
    "We keep logs for 30 days.", "retention; first person restatement")
add("P10", "paraphrase", "Database backups are retained for 90 days.",
    "Backups of the database are kept for 90 days.", "retention; kept vs retained")
add("P11", "paraphrase", "The internal REST endpoint for orders is /api/v2/orders.",
    "Orders are exposed at /api/v2/orders on the internal REST API.", "endpoint version; same path")
add("P12", "paraphrase", "The search endpoint is /api/v3/search.",
    "Search requests go to /api/v3/search.", "endpoint version; same path")
add("P13", "paraphrase", "Read queries for the orders table go to the replica.",
    "The orders table serves reads from a read replica.", "primary/replica; same routing")
add("P14", "paraphrase", "Analytics queries hit the read replica, not the primary.",
    "Analytics traffic is routed to a read replica instead of the primary.", "primary/replica; same routing")
add("P15", "paraphrase", "checkout_new_ui flag is enabled in production.",
    "The checkout_new_ui feature flag is on in production.", "feature flag; enabled vs on")
add("P16", "paraphrase", "The async_refunds flag is disabled for all tenants.",
    "async_refunds feature flag is off for every tenant.", "feature flag; disabled vs off")

# --- 16 critical pairs: one critical token changed (MUST NOT merge)
add("C01", "critical", "The checkout service uses port 5432 in production.",
    "The checkout service uses port 5432 in staging.", "environment word changed")
add("C02", "critical", "The billing API binds to port 8443.",
    "The billing API binds to port 8444.", "port digit changed")
add("C03", "critical", "The session cache TTL is 60 seconds.",
    "The session cache TTL is 600 seconds.", "TTL digit changed 60 -> 600")
add("C04", "critical", "The rate limiter window resets every 15 minutes.",
    "The rate limiter window resets every 50 minutes.", "window length changed")
add("C05", "critical", "Primary Postgres runs in eu-west-1.",
    "Primary Postgres runs in us-east-1.", "region changed")
add("C06", "critical", "Object storage buckets live in ap-southeast-2.",
    "Object storage buckets live in ap-southeast-1.", "region suffix changed")
add("C07", "critical", "The payment client retries 3 times before failing.",
    "The payment client retries 5 times before failing.", "retry count changed")
add("C08", "critical", "The webhook sender retries 5 times with exponential backoff.",
    "The webhook sender retries 8 times with exponential backoff.", "retry count changed")
add("C09", "critical", "Log retention is 30 days.",
    "Log retention is 90 days.", "retention changed")
add("C10", "critical", "Database backups are retained for 90 days.",
    "Database backups are retained for 30 days.", "retention changed")
add("C11", "critical", "The internal REST endpoint for orders is /api/v2/orders.",
    "The internal REST endpoint for orders is /api/v1/orders.", "API version changed")
add("C12", "critical", "The search endpoint is /api/v3/search.",
    "The search endpoint is /api/v2/search.", "API version changed")
add("C13", "critical", "Read queries for the orders table go to the replica.",
    "Read queries for the orders table go to the primary.", "target swapped replica->primary")
add("C14", "critical", "Analytics queries hit the read replica, not the primary.",
    "Analytics queries hit the primary, not the read replica.", "targets swapped, same token multiset")
add("C15", "critical", "checkout_new_ui flag is enabled in production.",
    "checkout_new_ui flag is enabled in staging.", "environment word changed")
add("C16", "critical", "The async_refunds flag is disabled for all tenants.",
    "The async_refunds flag is enabled for all tenants.", "flag polarity flipped")

# --- 8 unrelated controls: must never merge
add("X01", "control", "The design team's offsite is booked for Lisbon in March.",
    "Redis eviction policy is allkeys-lru on the session cluster.", "unrelated topics")
add("X02", "control", "On-call rotation for the platform team changes every Monday at 09:00 UTC.",
    "The invoice PDF generator uses the Helvetica font family.", "unrelated topics")
add("X03", "control", "Customer Acme Corp requested SSO via Okta last quarter.",
    "The Kubernetes ingress controller runs version 1.9.4.", "unrelated topics")
add("X04", "control", "The mobile app's splash screen shows the company logo.",
    "Postgres autovacuum threshold is set to 50 for the orders table.", "unrelated topics")
add("X05", "control", "Marketing wants a new landing page for the Q3 campaign.",
    "The Kafka consumer group lag alert fires above 10000 messages.", "unrelated topics")
add("X06", "control", "The office printer is on the third floor near the kitchen.",
    "Terraform state is stored in an S3 bucket with versioning enabled.", "unrelated topics")
add("X07", "control", "Our CEO prefers meetings under 30 minutes.",
    "The gRPC health probe interval is 10 seconds.", "unrelated topics")
add("X08", "control", "The support team uses Zendesk for customer tickets.",
    "Celery workers run 4 concurrent processes per pod.", "unrelated topics")

with open(os.path.join(OUT, "pairs.json"), "w") as f:
    json.dump({"fixture_version": "widen-40-v1", "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
               "class_counts": {"paraphrase": 16, "critical": 16, "control": 8},
               "merge_expectation": {"paraphrase": "merge (duplicate capture)", "critical": "do not merge (false merge if merged)",
                                     "control": "do not merge"},
               "pairs": PAIRS}, f, indent=2)

def embed(model, texts):
    req = urllib.request.Request(URL, data=json.dumps({"model": model, "input": texts}).encode(),
                                 headers={"Content-Type": "application/json"})
    t0 = time.time()
    r = json.load(urllib.request.urlopen(req, timeout=180))
    return r, round(time.time() - t0, 3)

def cos(a, b):
    d = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a)); nb = math.sqrt(sum(y * y for y in b))
    return d / (na * nb) if na and nb else 0.0

def tokens(t):
    return re.findall(r"/api/v\d+|[a-z]{2}-[a-z]+-\d+|\d+(?:\.\d+)?|\b(?:production|prod|staging|stage|development|dev|primary|replica|enabled|disabled|on|off|port)\b", t.lower())

def crit_tokens(t):
    """Critical-token multiset: numbers, API versions, regions, env words, primary/replica, flag polarity."""
    toks = tokens(t)
    keep = []
    for x in toks:
        if x in ("primary", "replica", "production", "prod", "staging", "stage", "development", "dev",
                 "enabled", "disabled", "port") or re.fullmatch(r"\d+(?:\.\d+)?", x) or x.startswith("/api/") or re.fullmatch(r"[a-z]{2}-[a-z]+-\d+", x):
            keep.append(x)
    return sorted(keep)

def norm_env(x):
    return {"prod": "production", "stage": "staging", "dev": "development"}.get(x, x)

def guard_ok(a, b):
    ka = [norm_env(t) for t in crit_tokens(a)]
    kb = [norm_env(t) for t in crit_tokens(b)]
    return ka == kb

results = []
matrix_rows = []
for model in MODELS:
    texts = []
    for p in PAIRS:
        texts.append(p["a"]); texts.append(p["b"])
    r, secs = embed(model, texts)
    embs = r["embeddings"]
    dim = len(embs[0])
    rec = {"kind": "embed_call", "model": model, "texts": len(texts), "dim": dim,
           "wall_seconds": secs, "prompt_eval_count": r.get("prompt_eval_count"),
           "total_duration_ns": r.get("total_duration"), "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    results.append(rec)
    scores = {}
    for i, p in enumerate(PAIRS):
        s = cos(embs[2 * i], embs[2 * i + 1])
        scores[p["id"]] = s
        results.append({"kind": "pair", "model": model, "id": p["id"], "class": p["class"],
                        "cosine": round(s, 6), "guard_pass": guard_ok(p["a"], p["b"])})
    # sweep
    best = None
    for tau in TAUS:
        fp = sum(1 for p in PAIRS if p["class"] == "critical" and scores[p["id"]] >= tau)
        tp = sum(1 for p in PAIRS if p["class"] == "paraphrase" and scores[p["id"]] >= tau)
        ctl = sum(1 for p in PAIRS if p["class"] == "control" and scores[p["id"]] >= tau)
        prec = tp / (tp + fp) if (tp + fp) else 0.0
        rec_ = tp / 16.0
        f1 = 2 * prec * rec_ / (prec + rec_) if (prec + rec_) else 0.0
        row = {"model": model, "tau": tau, "duplicate_capture": tp, "false_merge": fp, "controls_merged": ctl,
               "precision": round(prec, 4), "recall": round(rec_, 4), "f1": round(f1, 4)}
        matrix_rows.append(row)
        if best is None or f1 > best["f1"]:
            best = dict(row)
    # guard arm at tau = 0.95 and at best-f1 tau
    guard_rows = []
    for tau in (0.95, 0.99, best["tau"]):
        g_tp = sum(1 for p in PAIRS if p["class"] == "paraphrase" and scores[p["id"]] >= tau and guard_ok(p["a"], p["b"]))
        g_fp = sum(1 for p in PAIRS if p["class"] == "critical" and scores[p["id"]] >= tau and guard_ok(p["a"], p["b"]))
        # guard-blocked false merges that raw cosine would have merged
        raw_fp = sum(1 for p in PAIRS if p["class"] == "critical" and scores[p["id"]] >= tau)
        raw_tp = sum(1 for p in PAIRS if p["class"] == "paraphrase" and scores[p["id"]] >= tau)
        guard_rows.append({"model": model, "tau": tau, "guard_duplicate_capture": g_tp, "guard_false_merge": g_fp,
                           "raw_duplicate_capture": raw_tp, "raw_false_merge": raw_fp,
                           "merges_blocked_by_guard": raw_fp - g_fp})
    # store arm: 30-fact store, 30 incoming writes (14 paraphrase duplicates, 16 critical new facts)
    store = [PAIRS[i]["a"] for i in range(16)] + [PAIRS[i]["a"] for i in range(16, 30)]
    store_embs = [embs[2 * i] for i in range(16)] + [embs[2 * i] for i in range(16, 30)]
    writes = [(PAIRS[i]["b"], "duplicate", embs[2 * i + 1]) for i in range(14)] + \
             [(PAIRS[i]["b"], "new_fact", embs[2 * i + 1]) for i in range(16, 32)]
    store_rows = []
    for tau in (None, 0.95, 0.99):
        cur = list(store_embs); cur_txt = list(store)
        skipped_dup = skipped_new = 0
        for txt, cls, e in writes:
            mx = max((cos(e, c) for c in cur), default=0.0)
            if tau is None:
                merge = False
            else:
                merge = mx >= tau
            if merge:
                if cls == "duplicate": skipped_dup += 1
                else: skipped_new += 1
            else:
                cur.append(e); cur_txt.append(txt)
        store_rows.append({"model": model, "tau": tau, "store_size_after": len(cur),
                           "duplicates_collapsed": skipped_dup, "duplicate_writes": 14,
                           "distinct_facts_lost": skipped_new, "new_fact_writes": 16,
                           "highest_cosine_seen": round(max((max((cos(e, c) for c in list(store_embs)), default=0.0) for _, _, e in writes), default=0.0), 4)})
    cls_stats = {}
    for cls in ("paraphrase", "critical", "control"):
        vals = sorted(scores[p["id"]] for p in PAIRS if p["class"] == cls)
        cls_stats[cls] = {"min": round(vals[0], 4), "median": round(vals[len(vals) // 2], 4),
                          "max": round(vals[-1], 4), "n": len(vals)}
    sep = {"lowest_paraphrase": cls_stats["paraphrase"]["min"], "highest_critical": cls_stats["critical"]["max"],
           "margin": round(cls_stats["paraphrase"]["min"] - cls_stats["critical"]["max"], 4),
           "clean_separation": (cls_stats["paraphrase"]["min"] - cls_stats["critical"]["max"]) > 0.02}
    # which critical pair scores highest, which paraphrase lowest
    top_crit = max(((scores[p["id"]], p["id"]) for p in PAIRS if p["class"] == "critical"))
    top_par = min(((scores[p["id"]], p["id"]) for p in PAIRS if p["class"] == "paraphrase"))
    results.append({"kind": "encoder_summary", "model": model, "dim": dim, "class_stats": cls_stats,
                    "separation": sep, "best_f1_row": best, "highest_critical_pair": {"id": top_crit[1], "cosine": round(top_crit[0], 6)},
 "lowest_paraphrase_pair": {"id": top_par[1], "cosine": round(top_par[0], 6)},
                    "guard": guard_rows, "store_arm": store_rows,
                    "tau_window_both_errors_nonzero": [r["tau"] for r in matrix_rows if r["model"] == model and r["duplicate_capture"] > 0 and r["false_merge"] > 0][:1] +
                                                      [r["tau"] for r in matrix_rows if r["model"] == model and r["duplicate_capture"] > 0 and r["false_merge"] > 0][-1:]})

with open(os.path.join(OUT, "results.jsonl"), "w") as f:
    for r in results:
        f.write(json.dumps(r) + "\n")
with open(os.path.join(OUT, "sweep.csv"), "w") as f:
    f.write("model,tau,duplicate_capture,false_merge,controls_merged,precision,recall,f1\n")
    for r in matrix_rows:
        f.write("%s,%s,%d,%d,%d,%s,%s,%s\n" % (r["model"], r["tau"], r["duplicate_capture"], r["false_merge"],
                                               r["controls_merged"], r["precision"], r["recall"], r["f1"]))
summ = [r for r in results if r["kind"] == "encoder_summary"]
with open(os.path.join(OUT, "summary.json"), "w") as f:
    json.dump({"fixture": "widen-40-v1", "taus": TAUS, "encoders": summ}, f, indent=2)

for r in summ:
    print("==", r["model"], "dim", r["dim"])
    print("   stats", json.dumps(r["class_stats"]))
    print("   separation", json.dumps(r["separation"]))
    print("   best_f1", json.dumps(r["best_f1_row"]))
    print("   highest_critical", r["highest_critical_pair"], "lowest_paraphrase", r["lowest_paraphrase_pair"])
    print("   tau_window", r["tau_window_both_errors_nonzero"])
    for g in r["guard"]:
        print("   guard", json.dumps(g))
    for s in r["store_arm"]:
        print("   store", json.dumps(s))
print("done")
