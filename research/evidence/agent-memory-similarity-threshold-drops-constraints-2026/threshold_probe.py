#!/usr/bin/env python3
"""Deterministic constraint-vs-descriptive similarity probe (RockB research, 2026-11-14).

No network beyond localhost. Exact cosine over full vectors (no ANN index), so
approximation error cannot be confused with the threshold effect.

Usage: python3 threshold_probe.py > probe_results.json
"""
import json, math, hashlib, datetime, urllib.request, sys

OLLAMA = "http://127.0.0.1:11434/api/embed"
EMBEDDERS = ["all-minilm:latest", "snowflake-arctic-embed:33m"]

# Fixture: 6 constraint facts (prohibitions/requirements/exceptions) + 6 descriptive
# facts over the same entities. Written as full sentences, not negation stubs.
FACTS = [
    {"id": "c1", "kind": "constraint", "text": "Deployment to production on Fridays is prohibited for all teams."},
    {"id": "c2", "kind": "constraint", "text": "Only the platform on-call engineer may rotate the production API keys."},
    {"id": "c3", "kind": "constraint", "text": "Customer PII must not be copied into analytics notebooks."},
    {"id": "c4", "kind": "constraint", "text": "Any exception to the deployment freeze requires approval from the engineering director."},
    {"id": "c5", "kind": "constraint", "text": "Database migrations over ten minutes must run inside the maintenance window."},
    {"id": "c6", "kind": "constraint", "text": "Contractors are excluded from the incident command rotation."},
    {"id": "d1", "kind": "description", "text": "Backups run nightly at 02:00 UTC and are stored in the eu-west-1 bucket."},
    {"id": "d2", "kind": "description", "text": "The on-call rotation is published every Monday and covers seven days."},
    {"id": "d3", "kind": "description", "text": "Production API keys are rotated quarterly by the security team."},
    {"id": "d4", "kind": "description", "text": "The analytics notebook cluster runs on eight GPU nodes."},
    {"id": "d5", "kind": "description", "text": "The deployment pipeline uses a blue-green strategy with a ten minute soak."},
    {"id": "d6", "kind": "description", "text": "Incident reviews are written by the on-call engineer within three days."},
]
QUERIES = [
    {"id": "q1", "gold": "c1", "text": "May I deploy to production on Friday?"},
    {"id": "q2", "gold": "c2", "text": "Can I rotate the production API keys myself?"},
    {"id": "q3", "gold": "c3", "text": "Is it allowed to copy customer PII into an analytics notebook?"},
    {"id": "q4", "gold": "c5", "text": "Does a long database migration need the maintenance window?"},
    {"id": "q5", "gold": "d1", "text": "When do backups run and where are they stored?"},
    {"id": "q6", "gold": "d2", "text": "How is the on-call rotation scheduled?"},
]


def embed(model, texts):
    body = json.dumps({"model": model, "input": texts}).encode()
    req = urllib.request.Request(OLLAMA, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.load(r)["embeddings"]


def cos(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a)); nb = math.sqrt(sum(y * y for y in b))
    return dot / (na * nb)


def main():
    out = {"generated_at_utc": datetime.datetime.utcnow().isoformat() + "Z",
           "fixture_sha256": hashlib.sha256(json.dumps([FACTS, QUERIES], sort_keys=True).encode()).hexdigest(),
           "n_facts": len(FACTS), "n_queries": len(QUERIES), "embedders": {}}
    for model in EMBEDDERS:
        fvec = embed(model, [f["text"] for f in FACTS])
        qvec = embed(model, [q["text"] for q in QUERIES])
        dim = len(fvec[0])
        rows = []
        for q, qv in zip(QUERIES, qvec):
            scores = sorted(((cos(qv, fv), f["id"], f["kind"]) for f, fv in zip(FACTS, fvec)), reverse=True)
            gold = next(s for s in scores if s[1] == q["gold"])
            top = scores[0]
            # best descriptive competitor for the constraining queries
            best_desc = max((s for s in scores if s[2] == "description"), default=None)
            rows.append({"query": q["id"], "gold": q["gold"], "gold_score": round(gold[0], 3),
                         "gold_rank": [s[1] for s in scores].index(q["gold"]) + 1,
                         "top_id": top[1], "top_score": round(top[0], 3),
                         "best_descriptive_id": best_desc[1] if best_desc else None,
                         "best_descriptive_score": round(best_desc[0], 3) if best_desc else None,
                         "all_scores": [[s[1], s[2], round(s[0], 3)] for s in scores]})
        sweep = {}
        for i in range(4, 19):  # 0.20 .. 0.90 in 0.05 steps
            t = round(i * 0.05, 2)
            kept = [r for r in rows if r["gold_score"] >= t]
            cons = [r for r in rows if next(f for f in FACTS if f["id"] == r["gold"])["kind"] == "constraint"]
            cons_kept = [r for r in kept if next(f for f in FACTS if f["id"] == r["gold"])["kind"] == "constraint"]
            dropped_with_survivor = []
            for r in rows:
                if r["gold_score"] < t and r["best_descriptive_score"] is not None and r["best_descriptive_score"] >= t:
                    dropped_with_survivor.append(r["query"])
            sweep[str(t)] = {"constraint_recall": round(len(cons_kept) / len(cons), 3),
                             "overall_recall": round(len(kept) / len(rows), 3),
                             "dropped_gold_while_descriptive_survived": dropped_with_survivor}
        out["embedders"][model] = {"dimensions": dim, "rows": rows, "sweep": sweep}
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
