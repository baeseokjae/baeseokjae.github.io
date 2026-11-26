# Method

Probe: shape_probe.py (stdlib only, localhost:11434).
Env: Ollama 0.20.3; qwen3:0.6b digest 7df6b6e09427 (Q4_K_M); 2 vCPU / 11 GB; run 2026-11-15T12:14-12:16Z.
Run: python3 shape_probe.py <out_dir>
Files: 00_summary.json (types, statuses, counts), 01-02 non-stream request/response, 03-04 stream chunks, 05-06 cross-endpoint replay (status + error body).
Determinism: argument type, HTTP status and error body are stable; chunk counts, reasoning chars and wall times are this run's observations.
No credentials, no external network, no paid API.
