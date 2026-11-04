#!/usr/bin/env bash
# Reproducible driver for EXP-OLLAMA-SLOTS-2026-11-04
# Configs: A = existing server on 11434 (vendor default config, untouched)
#          B = dedicated instance on 11500, OLLAMA_NUM_PARALLEL=2
#          C = dedicated instance on 11501, OLLAMA_NUM_PARALLEL=4
set -u
cd "$(dirname "$0")"
OUT="$PWD/results.jsonl"
: > "$OUT"
LOG="${TMPDIR:-/tmp}/ollama_slots_logs"
mkdir -p "$LOG"

{
  echo "== host =="
  date -u +%Y-%m-%dT%H:%M:%SZ
  ollama --version
  uname -srm
  nproc
  free -m | head -2
  echo "== defaults check =="
  curl -s http://127.0.0.1:11434/api/ps
  echo
} > host.txt 2>&1

# ---- config A: default server, already running ----
python3 probe.py --label A-n1 --concurrency 1 --reps 4 --out "$OUT" > "$LOG/A-n1.json" 2>&1
curl -s http://127.0.0.1:11434/api/ps > ps_A.txt
python3 probe.py --label A-n2 --concurrency 2 --reps 4 --out "$OUT" > "$LOG/A-n2.json" 2>&1

# ---- config B: NUM_PARALLEL=2 on port 11500 ----
OLLAMA_HOST=127.0.0.1:11500 OLLAMA_NUM_PARALLEL=2 OLLAMA_MAX_QUEUE=1 \
OLLAMA_KEEP_ALIVE=120s OLLAMA_MODELS=/usr/share/ollama/.ollama/models \
  ollama serve > "$LOG/server_b.log" 2>&1 &
BPID=$!
for i in $(seq 1 40); do curl -s -m 1 http://127.0.0.1:11500/api/version >/dev/null && break; sleep 0.5; done
python3 probe.py --label B-n1 --base-url http://127.0.0.1:11500 --concurrency 1 --reps 2 --out "$OUT" > "$LOG/B-n1.json" 2>&1
curl -s http://127.0.0.1:11500/api/ps > ps_B.txt
python3 probe.py --label B-n2 --base-url http://127.0.0.1:11500 --concurrency 2 --reps 4 --out "$OUT" > "$LOG/B-n2.json" 2>&1
grep -i -E 'parallel|queue|slot' "$LOG/server_b.log" | head -20 > server_b_lines.txt
kill $BPID 2>/dev/null; wait $BPID 2>/dev/null

# ---- config C: NUM_PARALLEL=4 on port 11501 ----
OLLAMA_HOST=127.0.0.1:11501 OLLAMA_NUM_PARALLEL=4 OLLAMA_MAX_QUEUE=1 \
OLLAMA_KEEP_ALIVE=120s OLLAMA_MODELS=/usr/share/ollama/.ollama/models \
  ollama serve > "$LOG/server_c.log" 2>&1 &
CPID=$!
for i in $(seq 1 40); do curl -s -m 1 http://127.0.0.1:11501/api/version >/dev/null && break; sleep 0.5; done
curl -s http://127.0.0.1:11501/api/ps > ps_C.txt
python3 probe.py --label C-n4 --base-url http://127.0.0.1:11501 --concurrency 4 --reps 3 --out "$OUT" > "$LOG/C-n4.json" 2>&1
grep -i -E 'parallel|queue|slot' "$LOG/server_c.log" | head -20 > server_c_lines.txt
kill $CPID 2>/dev/null; wait $CPID 2>/dev/null

wc -l "$OUT" > run_stats.txt
date -u +%Y-%m-%dT%H:%M:%SZ >> run_stats.txt
echo DONE
