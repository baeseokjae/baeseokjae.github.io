# Method: kv_budget_probe.py

Reproduce with:

```
PROBE_PORT=11517 PROBE_CTXS=2048,8192,32768 PROBE_CACHES=f16,q8_0 \
  PROBE_OUT=$TMPDIR/probe_raw.json python3 scripts/kv_budget_probe.py
# q8_0 saving requires Flash Attention:
OLLAMA_FLASH_ATTENTION=1 PROBE_CTXS=8192,32768 PROBE_CACHES=q8_0 \
  PROBE_OUT=$TMPDIR/probe_fa.json python3 scripts/kv_budget_probe.py
```

Script sha256 d0d18f34100fc3aa48a6f32de6bb18825b7ff1bc09c2f4aff1e0a8141bdfe252;
fixture sha256 9d32e15d6ebedba52d622cd6fd385cab5b79f2f9859e4ffc02ae26756e629ec1.

## Procedure

1. For each KV-cache type, start a private `ollama serve` on an unused loopback port with `OLLAMA_HOST`, `OLLAMA_MODELS=/usr/share/ollama/.ollama/models`, `OLLAMA_NUM_PARALLEL=1`, `OLLAMA_MAX_LOADED_MODELS=1` and the cache-type variable. A separate server is required because the variable is read at process start.
2. For each `num_ctx` in {2048, 8192, 32768}: `POST /api/generate` with `keep_alive=10m`, `num_predict=1`, `options.num_ctx=N`, wait 2 s for the allocator to settle, then sum `VmRSS` from `/proc/<runner>/status` for the child `ollama runner` processes of that server.
3. Record the CONTEXT column from `ollama ps` for the same server to confirm the requested context was the context actually loaded; unload with `keep_alive=0`; stop the server.
4. Recompute the slope between context sizes within one (cache type, Flash Attention) family so the fixed weights/overhead base cancels.

## Environment actually used

2026-11-01T06:12Z, Ollama 0.20.3, 2 vCPU, 12,213,612 kB RAM, no GPU (`nvidia-smi` absent), CPU-only backend (100% CPU in `ollama ps`). Model tag `qwen2.5:0.5b`, id a8b0c5157701, Q4_K_M, 397 MB on disk.

## Deviations and limits

- Paths live under `research/evidence/<slug>/scripts/` rather than the proposed top-level `scripts/`, so the research artifact stays self-contained and out of the Hugo build inputs.
- The probe sends a 1-token generation instead of the planned long head/tail fixture. Allocation is sized by `num_ctx` at load, which the data confirms (RSS scales with `num_ctx` while `prompt_eval_count` stays 30); a 32k-token prompt would have cost minutes of CPU prompt-eval without changing the allocation being measured. The fixture file is kept for replay and hashing.
- One sample per cell. Repeat-run noise observed between identical configurations (f16 vs. inert q8_0 at 32768) is 228 kB, three orders of magnitude below the 368 MB slope signal, so a single sample per cell is adequate for a slope at this scale but not for finer distinctions.
- No 27B/31B row was executed: this host has 12 GB RAM and no GPU. All large-model figures in the article come from the formula applied to published `config.json` values and must be labelled computed.
