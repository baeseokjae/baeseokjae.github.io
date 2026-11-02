# Formula check: qwen2.5:0.5b, measured vs. computed KV-cache slope

Run: 2026-11-01T06:12:16Z .. 06:13:31Z (UTC). Ollama 0.20.3, CPU-only, 2 vCPU, 12,213,612 kB RAM.
Raw: `raw/probe_raw_f16_and_q8_no_fa.json`, `raw/probe_raw_q8_with_flash_attention.json`. Table: `kv-budget-2026-11-01.csv`.

## Inputs from the model's own config

`https://huggingface.co/Qwen/Qwen2.5-0.5B/raw/main/config.json` (checked 2026-11-01):

- num_hidden_layers = 24
- num_key_value_heads = 2 (GQA; num_attention_heads = 14)
- hidden_size = 896 -> head_dim = 896 / 14 = 64
- max_position_embeddings = 32768
- The installed tag reports the same shape: `ollama show qwen2.5:0.5b` -> architecture qwen2, context length 32768, embedding length 896, quantization Q4_K_M.

## Computed slope

bytes/token = 2 (K and V) * n_layers * n_kv_heads * head_dim * bytes_per_element

- f16: 2 * 24 * 2 * 64 * 2 = 12,288 B/token = 12.00 KiB/token
- q8_0: 34 B per 32 elements = 1.0625 B/element -> 2 * 24 * 2 * 64 * 1.0625 = 6,528 B/token = 6.38 KiB/token

## Measured vs. computed

| KV cache | Flash Attention | slope measured | slope computed | error |
|---|---|---|---|---|
| f16 | off | 11.98 KiB/token (367,920 kB over 30,720 tokens, 2048 -> 32768) | 12.00 | -0.20 % |
| q8_0 | off | 12.00 KiB/token | 12.00 | 0 % (no saving: the setting was inert) |
| q8_0 | on (`OLLAMA_FLASH_ATTENTION=1`) | 6.37 KiB/token (156,660 kB over 24,576 tokens, 8192 -> 32768) | 6.38 | -0.01 % |

f16 residual after removing the slope is the same base at each context: 494,748 - 12.0*2048 = 470,172 kB and 862,668 - 12.0*32768 = 469,452 kB, i.e. a 720 kB spread on a ~470 MB base (0.15 %). That base is the Q4_K_M weights plus graph/allocator overhead, not context.

## The q8_0 null result, explained

With `OLLAMA_KV_CACHE_TYPE=q8_0` and no Flash Attention, RSS at 32768 tokens differed from f16 by 228 kB — the flag had no effect. Ollama's own documentation states the precondition explicitly: the K/V cache "can be quantized to significantly reduce memory usage **when Flash Attention is enabled**" (`OLLAMA_KV_CACHE_TYPE`, default `f16`; q8_0 "uses approximately 1/2 the memory of f16"). Re-running the same two cells with `OLLAMA_FLASH_ATTENTION=1` reproduced the halving: 0.532x the f16 slope, matching the 34/32-byte packing.

Note the base also moves with Flash Attention (8192: 567,752 kB f16 -> 521,648 kB q8_0+FA), so the article must compare slopes, not single RSS values.

## What this does and does not establish

- Establishes, on this host and this tag: KV allocation is made at model load from `num_ctx` and grows linearly at the formula's rate; `num_ctx` was honoured exactly as requested (see `ollama ps` CONTEXT column in the CSV).
- Does not establish throughput, quality, GPU behaviour, or any 27B-32B figure. The 0.5B model was chosen only because it fits on a 12 GB CPU box; large-model numbers in the article are computed from config and must stay labelled computed.
- The probe sends a 1-token generation. That is deliberate: the allocation happens at context creation, and the measurement shows it scaling with `num_ctx` while prompt length stays constant at 30 tokens. A long fixture prompt would add minutes of CPU prompt-eval without changing the allocated cache.
