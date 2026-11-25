#!/usr/bin/env bash
# Reproduces the Qwen3-0.6B tool-router probe. Run from this directory.
# Requires: Ollama serving on 127.0.0.1:11434, python3 (stdlib only).
set -euo pipefail
cd "$(dirname "$0")"

{
  date -u +%Y-%m-%dT%H:%M:%SZ
  ollama --version
  nproc
  free -m | sed -n '1,2p'
  ollama list
  echo '--- qwen3:0.6b modelfile head ---'
  ollama show qwen3:0.6b --modelfile 2>&1 | head -12
  echo '--- /api/ps before sweep ---'
  curl -s -m 5 http://127.0.0.1:11434/api/ps
} | tee env.txt

# Sweep 1: the 128-token budget that reproduces the silent failure.
PROBE_NUM_PREDICT=128 python3 probe.py qwen3:0.6b 3 1,4,8 explicit

# Sweep 2: the same cells with a 512-token budget (thinking mode needs headroom).
PROBE_NUM_PREDICT=512 python3 probe.py qwen3:0.6b 2 4,8,12 explicit

# Optional control model, same fixture:
# PROBE_NUM_PREDICT=512 python3 probe.py qwen2.5:0.5b 2 4,8 explicit

python3 - <<'PY'
import csv, json, statistics
recs = [json.loads(l) for l in open('results.jsonl') if l.strip()]
def q(v, p):
    v = sorted(v); k = (len(v)-1)*p; f = int(k); c = min(f+1, len(v)-1)
    return round(v[f] + (v[c]-v[f])*(k-f), 3)
buckets = {}
for r in recs:
    buckets.setdefault((r['model'], r['n_tools']), []).append(r)
rows = []
for (m, n), rs in sorted(buckets.items()):
    ok = [r for r in rs if r.get('correct_tool') and (r.get('schema') or {}).get('valid')]
    w = [r['wall_s'] for r in rs]
    rows.append({'model': m, 'n_tools': n, 'reps': len(rs), 'correct_valid': len(ok),
                 'fail_no_call': sum(1 for r in rs if r.get('failure') == 'no_tool_call'),
                 'fail_wrong_tool': sum(1 for r in rs if r.get('failure') == 'wrong_tool'),
                 'fail_malformed': sum(1 for r in rs if r.get('failure') == 'malformed_args'),
                 'done_reason_length': sum(1 for r in rs if r.get('done_reason') == 'length'),
                 'wall_min': min(w), 'wall_median': round(statistics.median(w), 3),
                 'wall_p95': q(w, .95), 'wall_max': max(w)})
with open('summary.csv', 'w', newline='') as f:
    wr = csv.DictWriter(f, fieldnames=list(rows[0])); wr.writeheader(); wr.writerows(rows)
print(open('summary.csv').read())
PY
