
import json, sys, time, urllib.request, math, hashlib
FIX = json.load(open(sys.argv[1]))
BASE = "http://127.0.0.1:11434"
MODELS = ["all-minilm:latest", "snowflake-arctic-embed:33m", "nomic-embed-text:latest"]
GRANS = ["whole_document", "three_sentence", "single_sentence"]
K = 8
def post(path, payload):
    req = urllib.request.Request(BASE+path, data=json.dumps(payload).encode(), headers={"Content-Type":"application/json"})
    with urllib.request.urlopen(req, timeout=120) as r: return json.loads(r.read().decode())
def embed(m, t):
    o=[]
    for i in range(0,len(t),16): o.extend(post("/api/embed",{"model":m,"input":t[i:i+16]})["embeddings"])
    return o
def chunks(s, g):
    if g=="whole_document": return [(" ".join(s), list(range(1,len(s)+1)))]
    if g=="three_sentence": return [(" ".join(s[i:i+3]), list(range(i+1,i+1+len(s[i:i+3])))) for i in range(0,len(s),3)]
    return [(x,[i+1]) for i,x in enumerate(s)]
def nrm(v):
    n=math.sqrt(sum(x*x for x in v)); return [x/n for x in v] if n else v
def cos(a,b): return sum(x*y for x,y in zip(a,b))
t0=time.time(); out=[]
for m in MODELS:
    for g in GRANS:
        idx=[]; meta=[]
        for d,s in FIX["documents"].items():
            for txt,sp in chunks(s,g):
                idx.append(txt); meta.append({"doc":d,"sent":sp,"chars":len(txt)})
        V=[nrm(x) for x in embed(m,idx)]
        def rank(q):
            qv=nrm(embed(m,[q])[0])
            return sorted(range(len(V)), key=lambda i: -cos(qv,V[i]))
        sf=[]; tf=[]
        for qt in FIX["single_fact_queries"]:
            r=rank(qt["question"])
            pos=next((i for i,j in enumerate(r) if meta[j]["doc"]==qt["doc"] and qt["needle_sentence_1based"] in meta[j]["sent"]), None)
            sf.append({"q":qt["question"],"needle_rank0":pos,"top1_sent":meta[r[0]]["sent"],"top1_doc":meta[r[0]]["doc"]})
        for qt in FIX["two_fact_queries"]:
            r=rank(qt["question"]); need=set(qt["needle_sentences_1based"])
            ranks=[next((i for i,j in enumerate(r) if meta[j]["doc"]==qt["doc"] and s in meta[j]["sent"]), None) for s in sorted(need)]
            both_anywhere_in_top8 = all(x is not None and x<K for x in ranks)
            tf.append({"q":qt["question"],"needle_ranks0":ranks,"both_in_top8":both_anywhere_in_top8,
                       "top5_docs":[meta[r[i]]["doc"] for i in range(min(5,len(r)))]})
        ctx=[sum(meta[j]["chars"] for j in rank(qt["question"])[:3]) for qt in FIX["single_fact_queries"]]
        out.append({"model":m,"granularity":g,"vectors":len(idx),"dim":len(V[0]),
                    "single_hit1":sum(1 for x in sf if x["needle_rank0"]==0),"single_hit3":sum(1 for x in sf if x["needle_rank0"] is not None and x["needle_rank0"]<3),
                    "single_hit8":sum(1 for x in sf if x["needle_rank0"] is not None and x["needle_rank0"]<8),
                    "two_hit1":sum(1 for x in tf if x["needle_ranks0"][0]==0 and x["needle_ranks0"][1]==0),
                    "two_hit3":sum(1 for x in tf if all(r is not None and r<3 for r in x["needle_ranks0"])),
                    "two_both_in_top8":sum(1 for x in tf if x["both_in_top8"]),
                    "n_single":len(sf),"n_two":len(tf),
                    "mean_ctx_top3_chars":round(sum(ctx)/len(ctx)),"ctx_top3_chars":ctx,
                    "single_detail":sf,"two_detail":tf})
raw={"fixture_sha256":hashlib.sha256(json.dumps(FIX,sort_keys=True).encode()).hexdigest(),
     "measured_at_utc":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),"k_recorded":K,
     "wall_elapsed_s":round(time.time()-t0,2),"rows":out}
json.dump(raw,open(sys.argv[2],"w"),indent=2)
for r in out: print(r["model"],r["granularity"],"| single %d/%d h1 %d/%d h3 %d/%d h8"%(
    r["single_hit1"],r["n_single"],r["single_hit3"],r["n_single"],r["single_hit8"],r["n_single"]),
    "| two h1 %d/%d h3 %d/%d top8 %d/%d"%(r["two_hit1"],r["n_two"],r["two_hit3"],r["n_two"],r["two_both_in_top8"],r["n_two"]),
    "| ctx",r["mean_ctx_top3_chars"],"| vec",r["vectors"],"d",r["dim"])
