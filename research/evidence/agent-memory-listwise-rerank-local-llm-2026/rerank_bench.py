#!/usr/bin/env python3
"""Listwise rerank experiment: 4 arms over the fixture.

A  baseline      - embedder order (arctic-embed:33m, cosine, k=10), no model call
B  rerank10      - qwen3:0.6b listwise over the top-10
C  rerank20      - same prompt over the top-20
D  reversed10    - identical top-10 candidates presented in reverse order (position control)

Writes results.csv (one row per query per arm), raw/<arm>/<qid>.txt (verbatim output),
and summary.json. Deadline-aware: --deadline stops starting new calls.
"""
import argparse, csv, json, math, os, time, urllib.request, datetime

OLLAMA = os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434")
EMBED_MODEL = "snowflake-arctic-embed:33m"
CHAT_MODEL = "qwen3:0.6b"
NUM_CTX = 4096
SEED = 42
TEMP = 0.0

def post(path, payload, timeout=300):
    req = urllib.request.Request(OLLAMA + path, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=timeout) as r:
        body = json.loads(r.read().decode())
    return body, time.time() - t0

def cos(a, b):
    d = sum(x*y for x, y in zip(a, b))
    na = math.sqrt(sum(x*x for x in a)); nb = math.sqrt(sum(y*y for y in b))
    return d/(na*nb) if na and nb else 0.0

def build_docs(fixture):
    docs, owner, kind = [], [], []
    for c in fixture["clusters"]:
        for f in c["forms"]:
            docs.append(f); owner.append(c["id"]); kind.append("answer")
        for d in c["decoys"]:
            docs.append(d); owner.append(c["id"]); kind.append("decoy")
        for d in c["neardup_decoys"]:
            docs.append(d); owner.append(c["id"]); kind.append("neardup")
    return docs, owner, kind

PROMPT = """You are reranking search results for an internal memory service.

Question: {q}

Candidates:
{block}

Return ONLY a JSON array of candidate ids, best first, most relevant to the question at the top. Include every id exactly once. Example: [3,1,4,2]"""

def prompt_for(q, ids_texts):
    block = "\n".join(f"[{i+1}] {t}" for i, t in enumerate(ids_texts))
    return PROMPT.format(q=q, block=block)

def parse_order(text, n):
    """Return (order, kind) where kind is ok|json_error|bad_ids|partial."""
    s = text.strip()
    i, j = s.find("["), s.rfind("]")
    if i == -1 or j == -1 or j < i:
        return None, "no_array"
    try:
        arr = json.loads(s[i:j+1])
    except Exception:
        return None, "json_error"
    if not isinstance(arr, list) or not arr:
        return None, "not_a_list"
    out = []
    for x in arr:
        try:
            v = int(x)
        except Exception:
            return None, "bad_ids"
        if 1 <= v <= n and v not in out:
            out.append(v)
    if not out:
        return None, "bad_ids"
    missing = [v for v in range(1, n+1) if v not in out]
    out.extend(missing)
    return out, ("ok" if not missing else "partial")

def rank_of(order, answer_positions):
    for r, pos in enumerate(order, 1):
        if pos in answer_positions:
            return r
    return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--evidence", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--queries", type=int, default=30)
    ap.add_argument("--arms", default="B,C,D")
    ap.add_argument("--deadline", default=None)
    ap.add_argument("--minrank", type=int, default=1)
    ap.add_argument("--maxrank", type=int, default=10)
    ap.add_argument("--tag", default="")
    a = ap.parse_args()
    dl = None
    if a.deadline:
        dl = datetime.datetime.fromisoformat(a.deadline.replace("Z", "+00:00")).timestamp()

    fixture = json.load(open(os.path.join(a.evidence, "fixture.json")))
    docs, owner, kind = build_docs(fixture)
    queries = [(c["id"], c["query"]) for c in fixture["clusters"]][:a.queries]
    print(f"docs={len(docs)} queries={len(queries)} arms={a.arms} num_ctx={NUM_CTX}", flush=True)

    de = [post("/api/embed", {"model": EMBED_MODEL, "input": d})[0]["embeddings"][0] for d in docs]
    qe = {qid: post("/api/embed", {"model": EMBED_MODEL, "input": q})[0]["embeddings"][0] for qid, q in queries}

    os.makedirs(a.out, exist_ok=True)
    for arm in ("A", "B", "C", "D"):
        os.makedirs(os.path.join(a.out, "raw", arm), exist_ok=True)
    csvp = os.path.join(a.out, "results.csv")
    new = not os.path.exists(csvp)
    f = open(csvp, "a", newline="")
    fields = ["qid", "arm", "k", "query", "baseline_rank", "arm_rank", "hit@1", "rr",
              "parse_kind", "prompt_tokens", "output_tokens", "wall_s", "tok_per_s", "model", "notes"]
    w = csv.DictWriter(f, fieldnames=fields)
    if new:
        w.writeheader()

    for qid, q in queries:
        scored = sorted(((cos(qe[qid], de[j]), j) for j in range(len(docs))), reverse=True)
        top = [j for s, j in scored]
        base_rank = next(r+1 for r, j in enumerate(top) if owner[j] == qid and kind[j] == "answer")
        if not (a.minrank <= base_rank <= a.maxrank):
            continue
        rows = [dict(qid=qid, arm="A", k=10, query=q, baseline_rank=base_rank, arm_rank=base_rank,
                     **{"hit@1": int(base_rank == 1)}, rr=round(1/base_rank, 4), parse_kind="n/a",
                     prompt_tokens=0, output_tokens=0, wall_s=0, tok_per_s=0, model=EMBED_MODEL,
                     notes="embedder order, no model call")]
        for arm, k, rev in (("B", 10, False), ("C", 20, False), ("D", 10, True)):
            if arm not in a.arms.split(","):
                continue
            if dl and time.time() > dl - 30:
                print(f"deadline reached before {arm}/{qid}", flush=True); continue
            cand = top[:k]
            if rev:
                cand = list(reversed(cand))
            texts = [docs[j] for j in cand]
            p = prompt_for(q, texts)
            try:
                body, wall = post("/api/generate", {"model": CHAT_MODEL, "prompt": p, "stream": False,
                                                    "think": False, "format": "json", "options": {
                                                        "num_ctx": NUM_CTX, "temperature": TEMP, "seed": SEED}})
                resp = body.get("response", "")
                ev = body.get("eval_count", 0); ed = body.get("eval_duration", 0)
                pe = body.get("prompt_eval_count", 0)
                tps = round(ev / (ed/1e9), 2) if ed else 0
            except Exception as e:
                resp, wall, ev, ed, pe, tps = "", 0, 0, 0, 0, 0
                print(f"ERROR {arm}/{qid}: {e}", flush=True)
            open(os.path.join(a.out, "raw", arm, f"{qid}.txt"), "w").write(resp)
            order, pkind = parse_order(resp, len(cand))
            if order:
                # map local prompt positions back to global doc indices
                mapped = [cand[pos-1] for pos in order]
                arm_rank = rank_of(mapped, {j for j, o in enumerate(owner) if o == qid and kind[j] == "answer"}) or 99
            else:
                arm_rank = base_rank
            rows.append(dict(qid=qid, arm=arm, k=k, query=q, baseline_rank=base_rank, arm_rank=arm_rank,
                             **{"hit@1": int(arm_rank == 1)}, rr=round(1/arm_rank, 4) if arm_rank else 0,
                             parse_kind=pkind, prompt_tokens=pe, output_tokens=ev,
                             wall_s=round(wall, 2), tok_per_s=tps, model=CHAT_MODEL,
                             notes="reversed order control" if rev else f"listwise top-{k}, num_ctx={NUM_CTX}"))
            print(f"{qid} {arm} base={base_rank} -> {arm_rank} parse={pkind} "
                  f"ptok={pe} otok={ev} wall={wall:.1f}s tps={tps}", flush=True)
        for r in rows:
            w.writerow(r)
        f.flush()

    f.close()
    print("DONE", flush=True)

if __name__ == "__main__":
    main()
