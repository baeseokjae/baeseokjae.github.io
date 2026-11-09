#!/usr/bin/env bash
# Dedicated-instance matrix runner. Each config gets a fresh server so that
# OLLAMA_MAX_LOADED_MODELS is actually applied and no model stays resident.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
PORT="${PORT:-11435}"
BASE="http://127.0.0.1:${PORT}"
OUT="$HERE/results.jsonl"
export OLLAMA_HOST="127.0.0.1:${PORT}"
export OLLAMA_MODELS="${OLLAMA_MODELS:-/usr/share/ollama/.ollama/models}"

start_server() {  # $1 = max loaded models
  OLLAMA_MAX_LOADED_MODELS="$1" OLLAMA_NUM_PARALLEL=1 OLLAMA_KEEP_ALIVE=5m \
    ollama serve >>"$HERE/server_${1}.log" 2>&1 &
  SRV=$!
  for _ in $(seq 1 40); do
    curl -sf "$BASE/api/version" >/dev/null 2>&1 && return 0
    sleep 0.25
  done
  return 1
}

stop_server() { kill "$SRV" 2>/dev/null; wait "$SRV" 2>/dev/null; sleep 0.3; }

run_config() {  # $1 label, $2 keep_alive, $3 max_loaded, $4 calls
  start_server "$3" || { echo "SERVER_START_FAILED $1"; return 1; }
  curl -s "$BASE/api/ps" >>"$HERE/ps_${1}.json"; echo >>"$HERE/ps_${1}.json"
  python3 "$HERE/probe.py" "$BASE" "$1" "$2" "$4" "$OUT" | tee -a "$HERE/stdout_${1}.log"
  curl -s "$BASE/api/ps" >>"$HERE/ps_${1}.json"; echo >>"$HERE/ps_${1}.json"
  stop_server
  sleep 0.5
}

: >"$OUT"
run_config B_ka5m_max1   5m   1 4
run_config D_kaNeg1_max3 -1   3 4
run_config C_ka5m_max3   5m   3 4
echo DONE
