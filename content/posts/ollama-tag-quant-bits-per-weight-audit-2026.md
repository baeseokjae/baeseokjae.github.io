---
date: 2026-11-03 00:30:00+00:00
lastmod: 2026-11-09 07:40:19+00:00
description: A 32B Ollama tag can serve a 20.2 GB file. Read its declared quantization,
  separate model and projector bytes, and use matching tensor counts for bits per
  weight.
draft: false
schema: schema-ollama-tag-quant-bits-per-weight-audit-2026
tags:
- Ollama
- GGUF
- quantization
- local LLM
- model sizing
- bits per weight
- artifact provenance
title: Reading an Ollama Model's Quantization and Size From Its Registry Manifest
---

You ran `ollama pull qwen3:32b` and got a model file of about 20.2 GB, or 18.8 GiB. A nominal 32-billion-parameter model needs 64 GB for bf16 weights alone. The downloaded model file is about 31.6% of that nominal baseline, not one-fifth. The tag says `32b`, but it does not spell out the quantization recipe.

You can check the registry's declared quantization and file sizes before downloading model-weight blobs. An Ollama manifest lists layers and byte sizes; its small config blob supplies `file_type`. Turning those bytes into bits per weight takes another step: the parameter count must describe the tensors in the same file.

**Correction, November 9, 2026:** The original version confused ideal four-bit storage with a mixed-quantization file, used mismatched denominators for DeepSeek, Gemma and one Mistral tag, and treated an unsupported ±3% rule as an integrity check. This revision corrects the arithmetic, checks the tensor counts, and separates advertised file sizes from actual network and disk use.

## The download that looks broken

For `qwen3:32b`, the manifest's model layer is 20,201,240,160 bytes:

- **20.201 decimal GB**, using 1 GB = 1,000,000,000 bytes.
- **18.814 GiB**, using 1 GiB = 1,073,741,824 bytes.

Those are two representations of the same file. Unit conversion accounts for that difference; it cannot by itself explain a much larger gap such as 18 GB versus 48 GB.

The idealized four-bit calculation is `32,000,000,000 × 4 / 8 = 16,000,000,000` bytes, or 16 GB. Real `Q4_K_M` files use a mixture of tensor types plus block scales, other quantization data, GGUF metadata and alignment. They need not average exactly four bits per parameter.

Using this artifact's exact 32,762,123,264 tensor elements, the ideal four-bit payload would be 16.381 GB and a bf16 payload would be 65.524 GB. Its 20.201 GB model file is therefore about **30.8% of that exact bf16 baseline**, with a file-level average of **4.933 bits per stored tensor element**. These are weight-storage comparisons, not estimates of total inference RAM or VRAM.

The November 3 snapshot recorded manifest SHA256 `030ee887880fc378860c2dd35101da424377520441ae4bfe7be6deff8ade7840`. The November 9 recheck returned the same hash. Tags can move; a digest identifies the bytes referenced by that particular snapshot.

## What the manifest tells you

A tag name is a label. Some names include a quantization suffix, such as `qwen3:32b-q8_0`; others leave it out. Resolve the tag and inspect these fields:

1. **`config.digest`** points to a small JSON blob. For [qwen3:32b](https://registry.ollama.ai/v2/library/qwen3/manifests/32b), the [488-byte config](https://registry.ollama.ai/v2/library/qwen3/blobs/sha256:afdf5c7585b363536f93782f1e44f1b81db4237847cd8b4bd2c5c33b0d76c94b) declares `file_type: Q4_K_M` and `model_family: qwen3`. This is a file-level label, not a promise that every tensor has one storage type.
2. **`layers[]`** lists each layer's `mediaType`, `size` and `digest`. This audit uses the complete `application/vnd.ollama.image.model` file for its numerator. That includes the GGUF container's metadata and alignment as well as tensor data.
3. **Other layers have separate roles.** Templates, parameters and licenses are small in this sample. Multimodal Gemma also has an `application/vnd.ollama.image.projector` layer. On `gemma3:4b`, that layer is 851,251,104 bytes, about 34.1% of the 2,499,012,288-byte language-model file. Their sizes must be kept separate when calculating language-model bpw.
4. **The model-layer digest identifies the advertised artifact.** Checking a downloaded blob against that digest verifies its bytes against the manifest. Reading a matching size or quant label alone does not do that.

The sum of `layers[].size` is useful capacity information. It is **not an exact network-transfer or incremental-disk figure**: it excludes the config and manifest, downloads can reuse or resume cached blobs, and several tags can share one stored blob. HTTP overhead and filesystem allocation are separate concerns. [Ollama's pull implementation](https://github.com/ollama/ollama/blob/main/server/images.go) handles config downloads, cache reuse and digest verification separately.

## Method: match the file and the denominator

The table calculates:

`file_bpw = model_layer_bytes × 8 / stored_tensor_elements`

For the denominator, count the elements represented by the model file's tensor metadata: for each unique tensor name, multiply its dimensions, then sum across tensors. The tensor-count links in the table point to Ollama's tensor listings for the exact model blob. The correction recheck parsed those listings, rejected duplicate tensor names, and counted the tensors without downloading their weight data.

A Hugging Face repository's `safetensors.total` can be a useful cross-check, but it is not automatically the right divisor. The source repository must match the actual model version, and its scope must match the file. A multimodal total can include a vision component stored in another blob. Tied or duplicated weights also require attention when comparing source parameters with serialized tensor elements. Both Llama 3.1 blobs here store an additional 64-element `rope_freqs.weight` tensor. The table includes it, so its denominator describes serialized tensor elements rather than strictly learned parameters; the difference does not affect the displayed three-decimal bpw.

Exact quant-block sizes come from [llama.cpp's GGUF constants](https://github.com/ggml-org/llama.cpp/blob/master/gguf-py/gguf/constants.py): `Q4_K` stores 256 values in 144 bytes, or 4.5 bpw; `Q6_K` uses 210 bytes, or 6.5625 bpw; `Q8_0` stores 32 values in 34 bytes, or 8.5 bpw. Those block rates include scales and other block data, but not the whole GGUF container.

`Q4_K_M` is a mixed quantization recipe, not a universal 4.85 bpw constant. Architecture, tensor shapes, quantizer choices and higher-precision tensors affect the file average. The [quantizer source](https://github.com/ggml-org/llama.cpp/blob/master/src/llama-quant.cpp) shows both tensor-specific choices and fallbacks for incompatible shapes. There is no supported universal ±3% pass/fail test here. A plausible file size cannot prove the quantization layout, model quality or download integrity.

## The audit: 14 tags, 7 families

The original manifest reads ran on November 3, 2026. During the November 9 correction recheck, all 14 manifest hashes were unchanged. The byte sizes below are therefore the same artifacts; the denominator corrections change their interpretation. Each row links to its registry manifest and to its model-blob tensor listing. All 14 captured configs declare `Q4_K_M` or `Q8_0` as shown.

“Model bytes” means the complete model GGUF file. “Layer sum” means only the manifest's layer sizes, excluding config and manifest bytes. GB is decimal; GiB is binary. The tensor count excludes any separate projector blob.

| Tag | Declared type | Model bytes | GB / GiB | Stored tensor elements | File bpw | Layer sum (bytes) |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| [qwen3:4b](https://registry.ollama.ai/v2/library/qwen3/manifests/4b) | Q4_K_M | 2,497,280,480 | 2.497 / 2.326 | [4,022,468,096](https://ollama.com/library/qwen3:4b/blobs/3e4cb1417446) | 4.967 | 2,497,293,444 |
| [qwen3:8b](https://registry.ollama.ai/v2/library/qwen3/manifests/8b) | Q4_K_M | 5,225,374,496 | 5.225 / 4.867 | [8,190,735,360](https://ollama.com/library/qwen3:8b/blobs/a3de86cd1c13) | 5.104 | 5,225,387,677 |
| [qwen3:32b](https://registry.ollama.ai/v2/library/qwen3/manifests/32b) | Q4_K_M | 20,201,240,160 | 20.201 / 18.814 | [32,762,123,264](https://ollama.com/library/qwen3:32b/blobs/3291abe70f16) | 4.933 | 20,201,253,341 |
| [qwen3:32b-q8_0](https://registry.ollama.ai/v2/library/qwen3/manifests/32b-q8_0) | Q8_0 | 35,132,291,680 | 35.132 / 32.719 | [32,762,123,264](https://ollama.com/library/qwen3:32b-q8_0/blobs/de447d788da3) | 8.579 | 35,132,304,861 |
| [llama3.1:8b](https://registry.ollama.ai/v2/library/llama3.1/manifests/8b) | Q4_K_M | 4,920,738,944 | 4.921 / 4.583 | [8,030,261,312](https://ollama.com/library/llama3.1:8b/blobs/667b0c1932bc) | 4.902 | 4,920,752,841 |
| [llama3.1:70b](https://registry.ollama.ai/v2/library/llama3.1/manifests/70b) | Q4_K_M | 42,520,398,176 | 42.520 / 39.600 | [70,553,706,560](https://ollama.com/library/llama3.1:70b/blobs/de20d2cf2dc4) | 4.821 | 42,520,412,073 |
| [gemma3:4b](https://registry.ollama.ai/v2/library/gemma3/manifests/4b) | Q4_K_M | 2,499,012,288 | 2.499 / 2.327 | [3,880,101,888](https://ollama.com/library/gemma3:4b/blobs/f06e91e18fc7) | 5.152 | 3,350,272,259 |
| [gemma3:12b](https://registry.ollama.ai/v2/library/gemma3/manifests/12b) | Q4_K_M | 7,309,830,496 | 7.310 / 6.808 | [11,765,792,256](https://ollama.com/library/gemma3:12b/blobs/13576eb6dd8d) | 4.970 | 8,164,039,587 |
| [gemma3:27b](https://registry.ollama.ai/v2/library/gemma3/manifests/27b) | Q4_K_M | 16,555,661,472 | 16.556 / 15.419 | [27,009,007,616](https://ollama.com/library/gemma3:27b/blobs/3eb75691d2db) | 4.904 | 17,413,409,507 |
| [mistral:7b](https://registry.ollama.ai/v2/library/mistral/manifests/7b) | Q4_K_M | 4,372,811,712 | 4.373 / 4.072 | [7,248,023,552](https://ollama.com/library/mistral:7b/blobs/f5074b1221da) | 4.826 | 4,372,823,897 |
| [mistral:7b-instruct-q8_0](https://registry.ollama.ai/v2/library/mistral/manifests/7b-instruct-q8_0) | Q8_0 | 7,696,794,208 | 7.697 / 7.168 | [7,241,732,096](https://ollama.com/library/mistral:7b-instruct-q8_0/blobs/0624ba75c3ce) | 8.503 | 7,696,805,637 |
| [deepseek-r1:8b](https://registry.ollama.ai/v2/library/deepseek-r1/manifests/8b) | Q4_K_M | 5,225,373,760 | 5.225 / 4.867 | [8,190,735,360](https://ollama.com/library/deepseek-r1:8b/blobs/e6a7edc1a4d7) | 5.104 | 5,225,375,560 |
| [qwen2.5:0.5b](https://registry.ollama.ai/v2/library/qwen2.5/manifests/0.5b) | Q4_K_M | 397,807,936 | 0.398 / 0.370 | [494,032,768](https://ollama.com/library/qwen2.5:0.5b/blobs/c5396e06af29) | 6.442 | 397,820,829 |
| [phi4:14b](https://registry.ollama.ai/v2/library/phi4/manifests/14b) | Q4_K_M | 9,053,114,464 | 9.053 / 8.431 | [14,659,507,200](https://ollama.com/library/phi4:14b/blobs/fd7b6731c33c) | 4.940 | 9,053,115,905 |

The corrected rows reveal why the denominator matters:

- **DeepSeek-R1 8B:** The [official tag page](https://ollama.com/library/deepseek-r1:8b) identifies `DeepSeek-R1-0528-Qwen3-8B`, not the earlier Llama-based distilled model. The [matching repository](https://huggingface.co/api/models/deepseek-ai/DeepSeek-R1-0528-Qwen3-8B) has 8,190,735,360 parameters, agreeing with the blob's tensor count. That changes the result from **5.206 to 5.104 bpw**. The manifest hash is unchanged, so this was an incorrect source-model match, not a later tag update.
- **Gemma 3:** The language-model blobs contain 3,880,101,888, 11,765,792,256 and 27,009,007,616 tensor elements for the 4B, 12B and 27B tags. The original calculation divided those files by larger multimodal repository totals. With matching denominators, their file averages are **5.152, 4.970 and 4.904 bpw**. The old 4.649 figure for Gemma 4B did not demonstrate unusually low tensor precision. The separate projector layers are 851,251,104, 854,200,224 and 857,739,168 bytes.
- **Mistral Q8_0:** The `7b-instruct-q8_0` blob has 7,241,732,096 tensor elements and a 32,000-token vocabulary. The original denominator, 7,248,023,552, came from a different Mistral version. The matching blob count changes **8.495 to 8.503 bpw**. Similar family names do not establish identical source models.
- **Qwen2.5 0.5B:** Its **6.442 bpw** calculation is unchanged, but its explanation needs more than a general claim about embeddings. The blob's tensor listing shows Q8_0 token embeddings, many Q5_0 matrices, and a mixture of Q4_K, Q6_K and other tensor types. Its hidden width is 896, which is not divisible by the 256-value K-block size. llama.cpp's quantizer supports fallbacks from Q4_K to Q5_0 and from Q6_K to Q8_0 for incompatible shapes. The listed layout is consistent with that mechanism; it is not evidence of a corrupt file. The 494,032,768-element total includes no separately stored output.weight tensor.

## One model, two quantizations

The two Qwen3 32B blobs have the same 32,762,123,264 tensor elements. Their model files grow from 20,201,240,160 bytes at `Q4_K_M` to 35,132,291,680 bytes at `Q8_0`: **1.739 times the storage**, or about **73.9% more**. The file averages are 4.933 and 8.579 bpw.

That is a file-size comparison. It does not measure quality, tokens per second, runtime memory or memory traffic. Those depend on the implementation, offloading, batching, cache behavior and workload, and need their own measurements.

For a particular resolved model-blob digest, the artifact bytes do not change with your VRAM. Hardware still affects whether and how the model runs. This observation concerns the captured plain GGUF manifests; it does not assert that every tag, platform or future manifest-list selection always resolves to the same artifact.

## Run it yourself

Save this as `manifest_audit.py`. It reads a public library manifest and config, checks the config's declared digest and size, and reports model sizes and the layer sum. It does not download or verify the model-weight blobs. An optional parameter count produces file bpw; leave it out until you have matched the count to the blob's tensor metadata.

```python
#!/usr/bin/env python3
"""Read public library manifests; optional family:tag=parameter_count."""
import hashlib
import json
import re
import sys
import urllib.request
from datetime import datetime, timezone


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "manifest-audit/2.0"})
    with urllib.request.urlopen(req, timeout=30) as response:
        body = response.read()
        return body, response.headers.get("Date"), datetime.now(timezone.utc).isoformat()


def audit(spec):
    match = re.fullmatch(r"([A-Za-z0-9_.-]+):([A-Za-z0-9_.-]+)(?:=([1-9][0-9]*))?", spec)
    if not match:
        raise ValueError("Expected family:tag or family:tag=positive_parameter_count")
    family, tag, count = match.groups()
    base = f"https://registry.ollama.ai/v2/library/{family}"
    body, server_date, read_at = get(f"{base}/manifests/{tag}")
    manifest = json.loads(body)
    if "layers" not in manifest:
        raise ValueError("Not a plain model manifest; resolve its manifest list first")
    layers = manifest["layers"]
    model_layers = [x for x in layers if x["mediaType"] == "application/vnd.ollama.image.model"]
    if not model_layers:
        raise ValueError("No model layer; do not infer a parameter ratio")
    config_ref = manifest["config"]
    if not re.fullmatch(r"sha256:[0-9a-f]{64}", config_ref["digest"]):
        raise ValueError("Unsupported config digest")
    config_body, _, _ = get(f"{base}/blobs/{config_ref['digest']}")
    if (len(config_body) != config_ref["size"] or
            "sha256:" + hashlib.sha256(config_body).hexdigest() != config_ref["digest"]):
        raise ValueError("Config size or digest mismatch")
    config = json.loads(config_body)
    model_bytes = sum(x["size"] for x in model_layers)
    parameters = int(count) if count else None
    return {
        "tag": f"{family}:{tag}", "read_at_utc": read_at, "response_date": server_date,
        "manifest_sha256": hashlib.sha256(body).hexdigest(),
        "model_family": config.get("model_family"), "file_type": config.get("file_type"),
        "model_layers": model_layers, "model_bytes": model_bytes,
        "decimal_gb": round(model_bytes / 10**9, 3), "gib": round(model_bytes / 2**30, 3),
        "all_layer_bytes": sum(x["size"] for x in layers),
        "config_bytes": config_ref["size"], "manifest_bytes": len(body),
        "parameters_supplied": parameters,
        "file_bpw": round(model_bytes * 8 / parameters, 3) if parameters else None,
    }


if __name__ == "__main__":
    if not sys.argv[1:]:
        raise SystemExit("Usage: python3 manifest_audit.py family:tag[=parameter_count] ...")
    for spec in sys.argv[1:]:
        print(json.dumps(audit(spec)))
```

Run `python3 manifest_audit.py qwen3:32b=32762123264 phi4:14b`. The Qwen row includes `file_bpw: 4.933`; the Phi row leaves it `null` because no denominator was supplied. Compare the returned hashes with your saved snapshot. A later run is not guaranteed to return the same hash because tags can move.

`read_at_utc` is taken after the manifest body is read. `response_date` is the HTTP Date header and may reflect an intermediary's cached response; it is not a substitute for recording your own observation time. The script deliberately rejects manifest lists rather than silently choosing an artifact. It supports the plain public `library/family:tag` examples in this article, not every registry or authenticated model.

## What this does not tell you

- **File bpw is storage accounting, not quality.** Similar averages can hide different tensor layouts and quantization choices. An accuracy or perplexity claim needs an evaluation.
- **The registry declares the bytes.** This correction fetched manifests, configs and tensor metadata, not full model-weight blobs. It did not independently check every advertised tensor against downloaded weights.
- **Tags move and model identities matter.** Keep the manifest hash, layer digest, observation time and denominator provenance together. A family name and rounded “B” count are insufficient.
- **Fourteen tags are a sample.** These observations do not establish a universal range or pass/fail threshold for a quantization recipe.
- **Storage is not runtime memory.** KV cache, activations, work buffers, offloaded layers and backend choices are outside this audit.

Read `file_type` to learn the declared quantization recipe. Read layer sizes to plan storage. Match tensor scope before calculating file bpw, and verify blob digests when checking a download. Each step answers a different question.

## Sources and correction evidence

The row links identify the primary registry manifests and digest-specific tensor listings. The November 9 recheck preserved response times, response hashes, manifests, configs and the parsed tensor names, types and dimensions in the repository's correction evidence. The original November 3 CSV is retained as the historical record; it has not been silently rewritten to erase the corrected denominators.

For implementation details, see the linked llama.cpp constants and quantizer, and Ollama's pull implementation. The [Qwen2.5-0.5B-Instruct config](https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct/raw/main/config.json) documents its tied embeddings and dimensions. The [Mistral-7B-Instruct-v0.1 config](https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.1/raw/main/config.json) matches the Q8 artifact's vocabulary and RoPE settings, but matching architecture alone does not prove the exact weight lineage; the table uses the blob's counted elements instead.

Related reading on this site: [the idealized params × bits ÷ 8 sizing formula and why real artifacts differ](https://baeseokjae.github.io/posts/best-local-llm-models-2026/), [the Qwen3 32B setup guide](https://baeseokjae.github.io/posts/qwen-3-32b-local-guide-2026/), and [the deployment checklist that asks you to record quantization](https://baeseokjae.github.io/posts/qwen-3-full-lineup-guide-2026/).
