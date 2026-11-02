#!/usr/bin/env python3
"""KV-cache memory probe for Ollama on this host.

For each (kv_cache_type, num_ctx) pair: start a private ollama server on an
unused loopback port, force a single model load with the requested num_ctx,
read the runner process RSS from /proc/<pid>/status, confirm the context that
was actually honoured via `ollama ps`, then unload.

No prompt evaluation beyond one token: llama.cpp allocates the KV cache when
the context is created, so RSS at load time is the signal we want.
"""
import json, os, signal, subprocess, sys, time, urllib.request

PORT = int(os.environ.get("PROBE_PORT", "11517"))
HOST = f"127.0.0.1:{PORT}"
BASE = f"http://{HOST}"
MODEL = "qwen2.5:0.5b"
MODELS = os.environ.get("OLLAMA_MODELS_DIR", "/usr/share/ollama/.ollama/models")
CTXS = [int(x) for x in os.environ.get("PROBE_CTXS", "2048,8192,32768").split(",")]
CACHES = os.environ.get("PROBE_CACHES", "f16,q8_0").split(",")
OUT = os.environ.get("PROBE_OUT", "probe_raw.json")
DEADLINE = float(os.environ.get("PROBE_DEADLINE_TS", str(time.time() + 240)))


def http(path, payload=None, timeout=180):
    url = BASE + path
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data,
                                headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())


def start_server(cache_type):
    env = dict(os.environ)
    env.update({
        "OLLAMA_HOST": HOST,
        "OLLAMA_MODELS": MODELS,
        "OLLAMA_KV_CACHE_TYPE": cache_type,
        "OLLAMA_NUM_PARALLEL": "1",
        "OLLAMA_MAX_LOADED_MODELS": "1",
        "OLLAMA_CONTEXT_LENGTH": "2048",
    })
    log = open(os.path.join(os.path.dirname(OUT) or ".", f"serve_{cache_type}.log"), "w")
    p = subprocess.Popen(["ollama", "serve"], env=env, stdout=log, stderr=log,
                         start_new_session=True)
    for _ in range(120):
        try:
            http("/api/version", timeout=2)
            return p
        except Exception:
            time.sleep(0.5)
    raise RuntimeError(f"server did not start for cache={cache_type}")


def runners(server_pid):
    """Return [(pid, VmRSS_kB)] for the model runner process(es)."""
    out = []
    for pid in os.listdir("/proc"):
        if not pid.isdigit():
            continue
        try:
            with open(f"/proc/{pid}/stat") as f:
                ppid = int(f.read().split(") ", 1)[1].split()[1])
            if ppid != server_pid:
                continue
            with open(f"/proc/{pid}/status") as f:
                status = f.read()
            rss = next((int(l.split()[1]) for l in status.splitlines()
                        if l.startswith("VmRSS:")), 0)
            cmd = open(f"/proc/{pid}/cmdline").read().replace("\0", " ")
            out.append({"pid": int(pid), "vmrss_kb": rss, "cmdline": cmd[:200]})
        except Exception:
            continue
    return out


def ps_context():
    env = dict(os.environ, OLLAMA_HOST=HOST)
    r = subprocess.run(["ollama", "ps"], env=env, capture_output=True, text=True)
    return r.stdout.strip()


raw = [{"ts_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "event": "start",
        "host": {"nproc": os.cpu_count(), "models_dir": MODELS,
                 "kernel": os.uname().release}}]
with open("/proc/cpuinfo") as f:
    for line in f:
        if line.startswith("model name"):
            raw[0]["host"]["cpu"] = line.split(":", 1)[1].strip()
            break
with open("/proc/meminfo") as f:
    raw[0]["host"]["memtotal_kb"] = int(f.readline().split()[1])

for cache in CACHES:
    if time.time() > DEADLINE - 45:
        raw.append({"event": "abort", "reason": "deadline", "cache": cache})
        break
    srv = start_server(cache)
    try:
        raw.append({"event": "server_started", "cache": cache, "pid": srv.pid})
        for ctx in CTXS:
            if time.time() > DEADLINE - 40:
                raw.append({"event": "abort", "reason": "deadline", "cache": cache, "ctx": ctx})
                break
            t0 = time.time()
            row = {"cache": cache, "num_ctx_requested": ctx,
                   "ts_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
            try:
                resp = http("/api/generate", {"model": MODEL, "prompt": "hi",
                                              "stream": False, "keep_alive": "10m",
                                              "options": {"num_ctx": ctx, "num_predict": 1}},
                            timeout=240)
                row["load_and_gen_s"] = round(time.time() - t0, 2)
                row["prompt_eval_count"] = resp.get("prompt_eval_count")
                row["eval_count"] = resp.get("eval_count")
                row["ollama_model"] = resp.get("model")
                time.sleep(2.0)  # let allocator settle before sampling
                rs = runners(srv.pid)
                row["runner_processes"] = rs
                row["vmrss_kb_total"] = sum(x["vmrss_kb"] for x in rs)
                row["ps"] = ps_context()
            except Exception as e:
                row["error"] = f"{type(e).__name__}: {e}"
            raw.append(row)
            print(json.dumps(row)[:400], flush=True)
            try:
                http("/api/generate", {"model": MODEL, "prompt": "hi", "stream": False,
                                       "keep_alive": 0, "options": {"num_predict": 1}},
                     timeout=120)
            except Exception:
                pass
            time.sleep(1.5)
            raw.append({"event": "after_unload", "cache": cache, "ctx": ctx,
                        "runners": runners(srv.pid)})
    finally:
        try:
            os.killpg(os.getpgid(srv.pid), signal.SIGTERM)
        except Exception:
            srv.kill()
        time.sleep(2)

raw.append({"event": "end", "ts_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())})
with open(OUT, "w") as f:
    json.dump(raw, f, indent=1)
print("WROTE", OUT)
