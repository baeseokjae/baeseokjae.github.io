#!/usr/bin/env bash
# EXP-MEMDEDUPE-THRESHOLD-2026-11-10 — exact reproduction
# Requires a local Ollama daemon with the three encoder tags pulled:
#   ollama pull all-minilm:latest; ollama pull snowflake-arctic-embed:33m; ollama pull nomic-embed-text:latest
set -euo pipefail
OUT="${1:-./evidence}"
mkdir -p "$OUT"
ollama --version > "$OUT/environment.txt" 2>&1 || true
nproc >> "$OUT/environment.txt"
free -m | sed -n 2p >> "$OUT/environment.txt"
for m in all-minilm:latest snowflake-arctic-embed:33m nomic-embed-text:latest; do
  ollama show "$m" >> "$OUT/environment.txt" 2>&1; echo "--" >> "$OUT/environment.txt"
done
date -u >> "$OUT/environment.txt"
python3 run_experiment.py "$OUT"
