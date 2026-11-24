#!/bin/sh
# Runs the fixture once and records the tool versions next to the results.
set -eu
HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
OUT=${1:-"$HERE/results"}
mkdir -p "$OUT"
python3 --version > "$OUT/environment.txt"
ollama --version >> "$OUT/environment.txt" 2>&1
ollama show nomic-embed-text --modelfile 2>/dev/null | head -5 >> "$OUT/environment.txt" || true
ollama list | grep -E 'nomic-embed-text|qwen2.5:0.5b' >> "$OUT/environment.txt" || true
python3 "$HERE/probe.py" "$OUT" 2>&1 | tee "$OUT/run.log"
