#!/usr/bin/env python3
"""Plan VRAM for a local GGUF model: weights + KV cache + declared overhead.

Stdlib only. Numbers come from plan-fixtures.json, which was derived from each
model's own config.json at a pinned revision plus the published GGUF file sizes.
It answers "does this model + quant + context fit this card", not "how fast".

    python3 plan.py --list
    python3 plan.py --model qwen3-8b --quant Q4_K_M --context 40960 --vram 12
    python3 plan.py --model gemma-4-31b-it --quant Q4_K_M --context 32768 --vram 24

Fixture entry, one object per model under "models" in plan-fixtures.json.
Every key below is read by this script; `hybrid` is the only optional one.

    "my-model": {
      "repo": "org/repo",                     # printed in the header; informational
      "num_hidden_layers": 36,                # config.json num_hidden_layers
      "num_key_value_heads": 8,               # config.json num_key_value_heads
      "head_dim": 128,                        # config.json head_dim
      "max_position_embeddings": 40960,       # config.json max_position_embeddings
      "gguf_gib": {"Q4_K_M": 4.68},           # published file size / 1024**3, one entry per quant
      "hybrid": {                             # only for sliding-window configs
        "full_layers": 10,
        "sliding_layers": 50,
        "window": 1024,
        "global_head_dim": 512,
        "global_kv_heads": 4
      }
    }

`revision` is optional bookkeeping: it is never read by the arithmetic, only by the
fixtures file's own provenance note.

Exit codes: 0 fits, 1 does not fit, 2 bad input.
"""
import argparse
import json
import sys
from pathlib import Path

GIB = 1024 ** 3
BYTES_PER_ELEMENT = {"f16": 2.0, "q8_0": 34 / 32}


def load(models_path=None):
    path = Path(models_path or Path(__file__).with_name("plan-fixtures.json"))
    return json.loads(path.read_text())


def kv_bytes_per_token(model, kv_type="f16"):
    """Dense models: one slope. Hybrid models: slope + a fixed window term.

    Returns (bytes_per_token, fixed_bytes, note). A dense model's fixed term is 0.
    """
    bpe = BYTES_PER_ELEMENT[kv_type]
    if "hybrid" not in model:
        per_token = 2 * model["num_hidden_layers"] * model["num_key_value_heads"] * model["head_dim"] * bpe
        return per_token, 0.0, "dense"
    hybrid = model["hybrid"]
    per_token = 2 * hybrid["full_layers"] * hybrid["global_kv_heads"] * hybrid["global_head_dim"] * bpe
    fixed = (
        2
        * hybrid["sliding_layers"]
        * model["num_key_value_heads"]
        * model["head_dim"]
        * bpe
        * hybrid["window"]
    )
    return per_token, fixed, "hybrid"


def plan(model, quant, context, parallel=1, overhead_gib=1.0, kv_type="f16"):
    if context < 1:
        raise ValueError("context must be >= 1")
    if parallel < 1:
        raise ValueError("parallel must be >= 1")
    if quant not in model["gguf_gib"]:
        raise ValueError(f"no published size for {quant}; have {sorted(model['gguf_gib'])}")
    per_token, fixed, kind = kv_bytes_per_token(model, kv_type)
    kv_bytes = (per_token * context + fixed) * parallel
    weights = model["gguf_gib"][quant]
    kv_gib = kv_bytes / GIB
    total = weights + kv_gib + overhead_gib
    return {
        "kind": kind,
        "weights_gib": weights,
        "kv_bytes_per_token": per_token,
        "sliding_fixed_gib": fixed / GIB,
        "context": context,
        "parallel": parallel,
        "kv_gib": kv_gib,
        "overhead_gib": overhead_gib,
        "total_gib": total,
        "kv_type": kv_type,
    }


def main(argv=None):
    fixtures = load()
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--model", choices=sorted(fixtures["models"]))
    parser.add_argument("--quant", default="Q4_K_M")
    parser.add_argument("--context", type=int, default=8192)
    parser.add_argument("--parallel", type=int, default=1)
    parser.add_argument("--overhead-gib", type=float, default=1.0)
    parser.add_argument("--kv-type", choices=sorted(BYTES_PER_ELEMENT), default="f16")
    parser.add_argument("--vram", type=float, help="device memory in GiB; when given, the exit code reports fit")
    parser.add_argument("--list", action="store_true")
    args = parser.parse_args(argv)

    if args.list:
        for name, model in sorted(fixtures["models"].items()):
            kind = "hybrid" if "hybrid" in model else "dense"
            native = model.get("max_position_embeddings")
            native_text = f"{native:>7d}" if isinstance(native, int) else "    n/a"
            print(f"{name:22s} {kind:7s} native={native_text}  quants={','.join(sorted(model['gguf_gib']))}")
        return 0
    if not args.model:
        parser.error("--model is required unless --list is used")

    model = fixtures["models"][args.model]
    try:
        result = plan(model, args.quant, args.context, args.parallel, args.overhead_gib, args.kv_type)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    native = model.get("max_position_embeddings")
    native_label = f"native {native} tokens" if isinstance(native, int) else "native unknown"
    print(f"model    : {args.model} ({model.get('repo', 'repo not recorded')}, {native_label}, {result['kind']})")
    print(f"weights  : {result['weights_gib']:.2f} GiB  ({args.quant} GGUF file)")
    print(f"kv       : {result['kv_gib']:.2f} GiB  ({result['kv_type']}, {result['kv_bytes_per_token']:,.0f} B/token x {result['context']}"
          + (f" + {result['sliding_fixed_gib']:.2f} GiB fixed window per slot" if result["sliding_fixed_gib"] else "")
          + (f", x{result['parallel']} slots" if result["parallel"] > 1 else "") + ")")
    print(f"overhead : {result['overhead_gib']:.2f} GiB  (declared allowance, not measured)")
    print(f"total    : {result['total_gib']:.2f} GiB")
    if args.vram is None:
        return 0
    margin = args.vram - result["total_gib"]
    print(f"device   : {args.vram:.2f} GiB  margin {margin:+.2f} GiB")
    if margin < 0:
        print("verdict  : DOES NOT FIT - lower context, quantise the KV cache, or reduce parallel slots", file=sys.stderr)
        return 1
    print("verdict  : fits at the declared allowance")
    return 0


if __name__ == "__main__":
    sys.exit(main())
