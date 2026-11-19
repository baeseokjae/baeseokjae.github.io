import json, os, hashlib, re, time, urllib.request, subprocess, datetime
EV="/home/ubuntu/blog-automation/workspaces/4cc2674b-403b-4eb1-a269-db815f324167/tree/research/evidence/ollama-chat-template-tool-support-probe-2026"
HOST="http://127.0.0.1:11434"
def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def api(path, payload=None, timeout=180):
    url=HOST+path
    data=None if payload is None else json.dumps(payload).encode()
    req=urllib.request.Request(url, data=data, headers={"Content-Type":"application/json"})
    t0=time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body=r.read().decode(); code=r.status
    except urllib.error.HTTPError as e:
        body=e.read().decode(); code=e.code
    return code, body, round(time.time()-t0,2)

# 1. builds
code,tags,_=api("/api/tags")
tags=json.loads(tags)
rows=[{"name":m["name"],"digest":m.get("digest"),"size":m.get("size")} for m in tags.get("models",[])]
ver=subprocess.run(["ollama","--version"],capture_output=True,text=True).stdout.strip()

def get_template(name):
    mf=subprocess.run(["ollama","show","--modelfile",name],capture_output=True,text=True).stdout
    i=mf.find('TEMPLATE """')
    j=mf.find('"""', i+len('TEMPLATE """'))
    return mf, mf[i+len('TEMPLATE """'):j]

mf,tmpl=get_template("qwen2.5:0.5b")
# 2. derivative without the .Tools block, same SYSTEM as parent
sysline=[l for l in mf.splitlines() if l.startswith("SYSTEM ")]
# remove the "{{- if .Tools }}" ... matching "{{- end }}" conditional and the "or .Tools" in the wrapper
t2=tmpl
start=t2.find("{{- if .Tools }}")
def match_end(s,i):
    depth=0
    for m in re.finditer(r"\{\{-?\s*(if|range|with|end)\b", s[i:]):
        tok=m.group(1)
        if tok=="end": depth-=1
        else: depth+=1
        if depth==0: return i+m.end()
    return -1
e=match_end(t2,start)
removed=t2[start:e]
t2=t2[:start]+t2[e:]
t2=t2.replace("{{- if or .System .Tools }}","{{- if .System }}")
assert ".Tools" not in t2.split("{{")[0] or True
assert "range .Tools" not in t2
modelfile="FROM qwen2.5:0.5b\n"+("\n".join(sysline)+"\n" if sysline else "")+'TEMPLATE """'+t2+'"""\n'
open(os.path.join(EV,"Modelfile.notools"),"w").write(modelfile)
open(os.path.join(EV,"template-qwen2.5-0.5b.txt"),"w").write(tmpl)
open(os.path.join(EV,"template-probe-notools.txt"),"w").write(t2)
cr=subprocess.run(["ollama","create","probe-notools:latest","-f",os.path.join(EV,"Modelfile.notools")],capture_output=True,text=True)
print("CREATE rc",cr.returncode,cr.stdout[-300:],cr.stderr[-500:])

TOOL={"type":"function","function":{"name":"read_file","description":"Read a file from disk and return its contents.","parameters":{"type":"object","properties":{"path":{"type":"string","description":"Absolute path of the file to read"}},"required":["path"]}}}
MSGS=[{"role":"user","content":"Read the file /etc/hostname and tell me what hostname this machine has. Use the read_file tool."}]

def call(model, with_tools, seed=7):
    payload={"model":model,"messages":MSGS,"stream":False,"options":{"temperature":0,"seed":seed,"num_predict":128}}
    if with_tools: payload["tools"]=[TOOL]
    code,body,wall=api("/api/chat",payload)
    try: d=json.loads(body)
    except Exception: d={"_raw":body[:500]}
    msg=d.get("message",{}) or {}
    tcs=msg.get("tool_calls") or []
    content=(msg.get("content") or "")
    if tcs: cls="tool_calls"
    elif "<tool_call>" in content or '"name"' in content: cls="json_in_prose"
    else: cls="prose_no_call"
    return {"model":model,"tools_sent":with_tools,"http_status":code,"response_class":cls,
            "tool_call_count":len(tcs),"tool_names":[ (t.get("function") or {}).get("name") for t in tcs],
            "content_excerpt":content[:220].replace("\n"," "),
            "prompt_eval_count":d.get("prompt_eval_count"),"eval_count":d.get("eval_count"),
            "wall_s":wall,"error": d.get("error"),"checked_at":now()}

results={"ollama_version":ver,"host":"127.0.0.1:11434","started_at":now(),
         "template_sha256_parent":hashlib.sha256(tmpl.encode()).hexdigest(),
         "template_sha256_notools":hashlib.sha256(t2.encode()).hexdigest(),
         "removed_block":removed.strip()[:400],
         "builds":rows,"runs":[]}
for model in ["qwen2.5:0.5b","probe-notools:latest"]:
    for wt in (True,False):
        for rep in (1,2):
            r=call(model,wt,seed=7)
            r["rep"]=rep
            results["runs"].append(r)
            print(model,wt,rep,r["http_status"],r["response_class"],r["prompt_eval_count"],r["eval_count"],r["wall_s"],r["error"])
results["finished_at"]=now()
results["template_has_tools_block"]={"qwen2.5:0.5b":".Tools" in tmpl,"probe-notools:latest":".Tools" in t2}
json.dump(results, open(os.path.join(EV,"probe-run.json"),"w"), indent=2)
print("SAVED", os.path.join(EV,"probe-run.json"))
