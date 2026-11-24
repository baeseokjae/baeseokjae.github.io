#!/usr/bin/env python3
"""Multi-hop recall probe for a local vector store (stdlib + local Ollama only).

Builds a synthetic 120-fact store of two-hop chains, embeds it with three local
Ollama embedders, retrieves by exact cosine in pure Python, and measures:

  * bridge coverage@5 / @20  - is the second (bridging) fact even in the set?
  * exact-answer accuracy    - does a local reader model return the gold value?
  * prompt tokens + latency  - what each arm costs on a CPU-only host

Arms: single-shot top-5, single-shot top-20, decomposition (model rewrites the
question, each sub-query retrieved and the union taken), oracle (both gold facts).

Usage:
  python3 multihop_probe.py --out ../evidence/<slug> [--reader qwen2.5:0.5b]
                            [--deadline-epoch 1764000000]

No third-party packages, no network access beyond 127.0.0.1:11434.
"""
import argparse
import json
import math
import os
import time
import urllib.request

OLLAMA = os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434")
ENCODERS = ["all-minilm:latest", "snowflake-arctic-embed:33m", "nomic-embed-text:latest"]
SHORT = {"all-minilm:latest": "allminilm", "snowflake-arctic-embed:33m": "arctic33m",
         "nomic-embed-text:latest": "nomic"}

REGIONS = ["eu-west", "eu-central", "us-east", "us-west",
           "ap-southeast", "ap-northeast", "sa-east", "af-south"]
DBS = {"eu-west": "aurora-eu-1", "eu-central": "aurora-eu-2", "us-east": "dynamo-east",
       "us-west": "spanner-west", "ap-southeast": "mongo-sg-3", "ap-northeast": "mongo-tokyo-1",
       "sa-east": "spanner-sa-1", "af-south": "cassandra-cpt-2"}
TEAMS = ["Checkout", "Payments", "Identity", "Search", "Fulfilment", "Catalog", "Growth", "Platform"]
ROTATIONS = {"Checkout": "Payments SRE", "Payments": "Ledger SRE", "Identity": "Security Ops",
             "Search": "Relevance SRE", "Fulfilment": "Logistics SRE", "Catalog": "Data Platform",
             "Growth": "Experimentation SRE", "Platform": "Core Infra"}
COST_CENTRE = {"eu-west": "CC-1201", "eu-central": "CC-1202", "us-east": "CC-2101",
               "us-west": "CC-2102", "ap-southeast": "CC-3301", "ap-northeast": "CC-3302",
               "sa-east": "CC-4401", "af-south": "CC-5501"}
QUEUES = {"Checkout": "CHK-QUEUE", "Payments": "PAY-QUEUE", "Identity": "IDN-QUEUE",
          "Search": "SRCH-QUEUE", "Fulfilment": "FUL-QUEUE", "Catalog": "CAT-QUEUE",
          "Growth": "GRW-QUEUE", "Platform": "PLT-QUEUE"}
LANG = ["Go", "Python", "Rust", "TypeScript", "Java"]

PREFIX = ["orders", "billing", "inventory", "search", "notify", "auth", "ledger", "shipment",
          "pricing", "session"]
SUFFIX = ["api", "worker", "sync", "indexer"]
SERVICES = [f"{p}-{s}" for s in SUFFIX for p in PREFIX]  # 40


def build_fixture():
    facts, hop_a, hop_b, team_b = [], {}, {}, {}
    for i, svc in enumerate(SERVICES):
        region = REGIONS[i % len(REGIONS)]
        team = TEAMS[i % len(TEAMS)]
        hop_a[svc] = {}
        # fact 1: service -> region
        t = i % 3
        if t == 0:
            text = f"The {svc} service runs in the {region} region."
        elif t == 1:
            text = f"{svc} is deployed to {region} and serves production traffic from there."
        else:
            text = f"Production for {svc} is hosted in the {region} region."
        hop_a[svc]["region_fact"] = len(facts)
        facts.append({"id": len(facts), "text": text, "kind": "service_region"})
        # fact 2: service -> team
        t = i % 2
        if t == 0:
            text = f"The owning team for {svc} is the {team} team."
        else:
            text = f"{svc} is maintained by the {team} team."
        hop_a[svc]["team_fact"] = len(facts)
        facts.append({"id": len(facts), "text": text, "kind": "service_team"})
        # distractors on the same services
        if i < 8:
            facts.append({"id": len(facts),
                          "text": f"{svc} is written in {LANG[i % len(LANG)]} and ships from a monorepo.",
                          "kind": "distractor_service_lang"})
    for region in REGIONS:
        hop_b[region] = {}
        t = REGIONS.index(region) % 2
        if t == 0:
            text = f"The {region} region stores primary data in the {DBS[region]} cluster."
        else:
            text = f"Persistent data for {region} lives in the {DBS[region]} cluster."
        hop_b[region]["db_fact"] = len(facts)
        facts.append({"id": len(facts), "text": text, "kind": "region_db"})
        facts.append({"id": len(facts),
                      "text": f"Cloud spend for the {region} region is billed to cost centre {COST_CENTRE[region]}.",
                      "kind": "distractor_region_cost"})
    for team in TEAMS:
        t = TEAMS.index(team) % 2
        if t == 0:
            text = f"The {team} team rotates on-call through the {ROTATIONS[team]} group."
        else:
            text = f"On-call for the {team} team is handled by {ROTATIONS[team]}."
        team_b[team] = {"rotation_fact": len(facts)}
        facts.append({"id": len(facts), "text": text, "kind": "team_rotation"})
        facts.append({"id": len(facts),
                      "text": f"The {team} team files its incidents in the {QUEUES[team]} queue.",
                      "kind": "distractor_team_queue"})
    assert len(facts) == 120, len(facts)

    multi, single = [], []
    # 20 two-hop questions: 12 service->region->db, 8 service->team->on-call
    for n in range(20):
        svc = SERVICES[(n * 2) % len(SERVICES)]
        region = REGIONS[SERVICES.index(svc) % len(REGIONS)]
        team = TEAMS[SERVICES.index(svc) % len(TEAMS)]
        phrasing = ["templated", "natural", "keyword"][n % 3]
        if n < 12:
            gold, bridged = DBS[region], hop_b[region]["db_fact"]
            g1 = hop_a[svc]["region_fact"]
            qs = {
                "templated": f"Which database cluster holds the primary data for {svc}?",
                "natural": f"I need to find the database behind {svc} - if it went down, which cluster would I look at?",
                "keyword": f"{svc} database cluster primary data",
            }
            q = qs[phrasing]
        else:
            gold, bridged = ROTATIONS[team], team_b[team]["rotation_fact"]
            g1 = hop_a[svc]["team_fact"]
            qs = {
                "templated": f"Which on-call group handles incidents for the team that owns {svc}?",
                "natural": f"If {svc} pages someone at 3am, which rotation actually picks it up?",
                "keyword": f"{svc} owning team on-call rotation group",
            }
            q = qs[phrasing]
        multi.append({"id": f"M{n:02d}", "question": q, "phrasing": phrasing,
                      "service": svc, "gold": gold, "fact_hop1": g1, "fact_hop2": bridged,
                      "answer_type": "database" if n < 12 else "rotation"})
    for n in range(20):
        svc = SERVICES[(n * 2 + 1) % len(SERVICES)]
        region = REGIONS[SERVICES.index(svc) % len(REGIONS)]
        team = TEAMS[SERVICES.index(svc) % len(TEAMS)]
        if n < 10:
            qs = [f"Which region does {svc} run in?", f"Where is {svc} deployed?",
                  f"{svc} deployment region"]
            single.append({"id": f"S{n:02d}", "question": qs[n % 3], "service": svc,
                           "gold": region, "fact_hop1": hop_a[svc]["region_fact"],
                           "fact_hop2": None, "answer_type": "region", "phrasing": "templated"})
        else:
            qs = [f"Which team owns {svc}?", f"Who maintains {svc}?",
                  f"{svc} owning team"]
            single.append({"id": f"S{n:02d}", "question": qs[n % 3], "service": svc,
                           "gold": team, "fact_hop1": hop_a[svc]["team_fact"],
                           "fact_hop2": None, "answer_type": "team", "phrasing": "templated"})
    return {"facts": facts, "multi": multi, "single": single,
            "regions": REGIONS, "databases": DBS, "teams": TEAMS, "rotations": ROTATIONS}


def post(path, payload, timeout=180):
    req = urllib.request.Request(OLLAMA + path, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def embed(model, texts):
    out = post("/api/embed", {"model": model, "input": texts})
    return out["embeddings"]


def norm(v):
    n = math.sqrt(sum(x * x for x in v))
    return [x / n for x in v] if n else v


def cosine(a, b):
    return sum(x * y for x, y in zip(a, b))


def rank(qvec, mat, k):
    scored = sorted(((cosine(qvec, v), i) for i, v in enumerate(mat)), key=lambda x: (-x[0], x[1]))
    return [i for _, i in scored[:k]]


def normalize_answer(s):
    keep = [c.lower() if c.isalnum() else " " for c in s]
    return " ".join("".join(keep).split())


def grade(answer, gold):
    a, g = normalize_answer(answer).replace(" ", ""), normalize_answer(gold).replace(" ", "")
    if not g:
        return False
    return g in a


READER_SYS = ("You answer questions using only the FACTS. Reply with the value only, "
              "nothing else. If the facts do not contain the answer, reply UNKNOWN.")
DECOMP = ("Split the question into the smallest set of sub-questions needed to answer it. "
          "One sub-question per line, no numbering, no explanation.\nQuestion: ")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--reader", default="qwen2.5:0.5b")
    ap.add_argument("--deadline-epoch", type=float, default=0.0)
    ap.add_argument("--arms", default="oracle,top5,top20,decomp")
    ap.add_argument("--encoders", default=",".join(ENCODERS))
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    deadline = args.deadline_epoch or (time.time() + 900)
    t0 = time.time()

    fx = build_fixture()
    with open(os.path.join(args.out, "fixture.json"), "w") as f:
        json.dump(fx, f, indent=1)

    fact_texts = [f["text"] for f in fx["facts"]]
    questions = fx["multi"] + fx["single"]
    qtexts = [q["question"] for q in questions]

    models = [m for m in ENCODERS if m in args.encoders.split(",")]
    store, qvec, dims = {}, {}, {}
    for model in models:
        t = time.time()
        mats = [norm(v) for v in embed(model, fact_texts)]
        qs = [norm(v) for v in embed(model, qtexts)]
        store[model] = mats
        qvec[model] = qs
        dims[model] = len(mats[0])
        print(f"embedded {model} dim={dims[model]} in {time.time()-t:.1f}s", flush=True)

    # ---------- retrieval-only matrix (no reader) ----------
    retrieval = {}
    for model in models:
        rows = []
        for j, q in enumerate(questions):
            r5 = rank(qvec[model][j], store[model], 5)
            r20 = rank(qvec[model][j], store[model], 20)
            r50 = rank(qvec[model][j], store[model], 50)
            row = {"qid": q["id"], "question": q["question"], "gold": q["gold"],
                   "hop1": q["fact_hop1"], "hop2": q["fact_hop2"],
                   "hop1_rank": (r50.index(q["fact_hop1"]) + 1) if q["fact_hop1"] in r50 else None,
                   "hop2_rank": (r50.index(q["fact_hop2"]) + 1) if q["fact_hop2"] in r50 else None,
                   "top5": r5, "both_in_top5": None, "both_in_top20": None}
            row["both_in_top5"] = all(x in r5 for x in (q["fact_hop1"], q["fact_hop2"])) if q["fact_hop2"] is not None else q["fact_hop1"] in r5
            row["both_in_top20"] = all(x in r20 for x in (q["fact_hop1"], q["fact_hop2"])) if q["fact_hop2"] is not None else q["fact_hop1"] in r20
            rows.append(row)
        retrieval[model] = rows
        m = [r for r in rows if r["qid"].startswith("M")]
        s = [r for r in rows if r["qid"].startswith("S")]
        print(f"{SHORT[model]}: multi both@5 {sum(r['both_in_top5'] for r in m)}/{len(m)} "
              f"both@20 {sum(r['both_in_top20'] for r in m)}/{len(m)} | "
              f"single hit@5 {sum(r['both_in_top5'] for r in s)}/{len(s)}", flush=True)
    with open(os.path.join(args.out, "results-retrieval.json"), "w") as f:
        json.dump({"dims": dims, "encoders": models, "n_facts": len(fact_texts),
                   "rows": retrieval}, f, indent=1)

    # ---------- decomposition sub-queries (one model call per multi question) ----------
    subs, decomp_log = {}, []
    if "decomp" in args.arms:
        for q in fx["multi"]:
            if time.time() > deadline - 240:
                decomp_log.append({"qid": q["id"], "status": "skipped_deadline"})
                continue
            t = time.time()
            try:
                r = post("/api/generate", {"model": args.reader, "prompt": DECOMP + q["question"],
                                           "stream": False,
                                           "options": {"temperature": 0, "seed": 42, "num_predict": 60}})
                raw = r.get("response", "")
            except Exception as exc:  # noqa: BLE001
                raw = ""
                decomp_log.append({"qid": q["id"], "status": f"error:{exc}"})
            lines = [x.strip(" -.0123456789") for x in raw.splitlines() if x.strip()]
            lines = [x for x in lines if len(x) > 8][:4]
            subs[q["id"]] = lines
            decomp_log.append({"qid": q["id"], "raw": raw, "parsed": lines,
                               "parseable": bool(lines), "seconds": round(time.time() - t, 2)})
        with open(os.path.join(args.out, "decomposition.json"), "w") as f:
            json.dump(decomp_log, f, indent=1)

    subvec = {}
    if subs:
        flat = [s for v in subs.values() for s in v]
        for model in models:
            got = {}
            for qid, lines in subs.items():
                if not lines:
                    continue
                got[qid] = [norm(v) for v in embed(model, lines)]
            subvec[model] = got
        print(f"embedded {len(flat)} sub-queries x {len(models)} encoders", flush=True)

    # ---------- reader arms ----------
    arm_sets = {}
    for model in models:
        for j, q in enumerate(questions):
            base = {"top5": retrieval[model][j]["top5"],
                    "top20": rank(qvec[model][j], store[model], 20)}
            for arm, ids in base.items():
                arm_sets[(model, arm, q["id"])] = ids
            if "decomp" in args.arms and q["id"].startswith("M"):
                lines = subs.get(q["id"], [])
                vecs = subvec.get(model, {}).get(q["id"], [])
                picked, seen = [], set()
                for v in vecs:
                    for i in rank(v, store[model], 5):
                        if i not in seen:
                            seen.add(i)
                            picked.append(i)
                arm_sets[(model, "decomp", q["id"])] = picked[:10]
            if q["fact_hop2"] is not None:
                arm_sets[(model, "oracle", q["id"])] = [q["fact_hop1"], q["fact_hop2"]]
            else:
                arm_sets[(model, "oracle", q["id"])] = [q["fact_hop1"]]

    arms = [a for a in args.arms.split(",") if a]
    reader_rows, partial = [], False
    order = []
    for arm in ["oracle", "top5", "top20", "decomp"]:
        if arm not in arms:
            continue
        for model in models:
            for q in questions:
                if arm == "decomp" and not q["id"].startswith("M"):
                    continue
                order.append((arm, model, q))
    for arm, model, q in order:
        if time.time() > deadline - 120:
            partial = True
            break
        ids = arm_sets[(model, arm, q["id"])]
        facts_txt = "\n".join(f"{n+1}. {fact_texts[i]}" for n, i in enumerate(ids))
        prompt = f"{READER_SYS}\n\nFACTS:\n{facts_txt}\n\nQUESTION: {q['question']}\nANSWER:"
        t = time.time()
        try:
            r = post("/api/generate", {"model": args.reader, "prompt": prompt, "stream": False,
                                       "options": {"temperature": 0, "seed": 42, "num_predict": 16}})
            ans, ptok = r.get("response", "").strip(), r.get("prompt_eval_count")
        except Exception as exc:  # noqa: BLE001
            ans, ptok = f"<error: {exc}>", None
        row = {"arm": arm, "encoder": SHORT[model], "qid": q["id"], "type": "multi" if q["id"].startswith("M") else "single",
               "question": q["question"], "gold": q["gold"], "retrieved": ids,
               "answer": ans, "correct": grade(ans, q["gold"]),
               "prompt_tokens": ptok, "seconds": round(time.time() - t, 2),
               "both_in_set": all(x in ids for x in (q["fact_hop1"], q["fact_hop2"])) if q["fact_hop2"] is not None else q["fact_hop1"] in ids}
        reader_rows.append(row)
        with open(os.path.join(args.out, "results-reader.json"), "w") as f:
            json.dump({"reader": args.reader, "arms": arms, "partial": True,
                       "n_planned": len(order), "n_done": len(reader_rows),
                       "wall_seconds": round(time.time() - t0, 2), "rows": reader_rows}, f, indent=1)
        if len(reader_rows) % 20 == 0:
            print(f"reader {len(reader_rows)}/{len(order)} {time.time()-t0:.0f}s", flush=True)

    out = {"reader": args.reader, "arms": arms, "partial": partial,
           "n_planned": len(order), "n_done": len(reader_rows),
           "wall_seconds": round(time.time() - t0, 2), "rows": reader_rows}
    with open(os.path.join(args.out, "results-reader.json"), "w") as f:
        json.dump(out, f, indent=1)

    # ---------- summary ----------
    def cell(arm, enc, typ, field="correct"):
        rs = [r for r in reader_rows if r["arm"] == arm and r["encoder"] == enc and r["type"] == typ]
        if not rs:
            return None
        return {"n": len(rs), "hits": sum(r[field] for r in rs),
                "mean_tokens": round(sum((r["prompt_tokens"] or 0) for r in rs) / len(rs), 1),
                "mean_seconds": round(sum(r["seconds"] for r in rs) / len(rs), 2)}
    summary = {"encoders": {SHORT[m]: {"dim": dims[m],
                                       "retrieval_multi_both5": f"{sum(r['both_in_top5'] for r in retrieval[m] if r['qid'].startswith('M'))}/20",
                                       "retrieval_multi_both20": f"{sum(r['both_in_top20'] for r in retrieval[m] if r['qid'].startswith('M'))}/20",
                                       "retrieval_single_hit5": f"{sum(r['both_in_top5'] for r in retrieval[m] if r['qid'].startswith('S'))}/20",
                                       "mean_hop2_rank_multi": round(sum(r['hop2_rank'] for r in retrieval[m] if r['qid'].startswith('M') and r['hop2_rank']) / max(1, len([r for r in retrieval[m] if r['qid'].startswith('M') and r['hop2_rank']])), 1)}
                            for m in models},
               "reader": args.reader, "partial": partial,
               "cells": {f"{a}|{SHORT[m]}|{t}": cell(a, SHORT[m], t)
                         for a in arms for m in models for t in ("multi", "single")}}
    with open(os.path.join(args.out, "summary.json"), "w") as f:
        json.dump(summary, f, indent=1)
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
