---
date: 2026-11-03 00:30:00+00:00
lastmod: 2026-11-03 00:39:00+00:00
description: Pull a 32B model, get an 18-20 GB file, and nothing on the tag says why. Sum the manifest's weight layer, divide by the model's own parameter count, and the quantization becomes a number you can check before downloading.
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
title: 'The Tag Says Nothing About Bits: Reading a Local Model''s Real Quantization From Its Registry Manifest'
---

You ran `ollama pull qwen3:32b`. The progress bar stopped somewhere between 18 GB and 20 GB, the model answered, and nothing in the output told you what you had just downloaded. A 32-billion-parameter model needs 64 GB at bf16. You got a fifth of that. The tag said `32b` and stopped there: no `q4_K_M`, no `q8_0`, no indication that four bits per weight is what your download actually contains.

That gap is measurable before you download a single byte. An Ollama tag resolves to a registry manifest that lists each layer with its exact byte size, and the manifest's config blob carries the field the tag name omits. This article does that arithmetic on 14 tags across 7 model families and shows the numbers, the fetch times, and the code to reproduce them.

## The download that looks broken

For `qwen3:32b`, the weights layer in the manifest is 20,201,240,160 bytes. That single number explains the whole confusion:

- 20,201,240,160 bytes = 20.201 decimal GB (the figure a registry page, a download counter or a package listing reports)
- 20,201,240,160 bytes = 18.814 GiB (the same bytes in binary units — the "18.8 GB" that appears in blog posts and in tools that print GiB)

Both figures describe the same artifact, and which one a given tool prints is a formatting choice, not a different file. Nobody truncated the download and nobody shipped you a 2 GB shard of a 64 GB model. A 32B model at four bits per weight is supposed to be about 20 GB, and that is exactly what arrives. The "18 GB vs 48 GB" question that sends people to a search box is a unit mismatch layered on top of an unstated quantization level.

The manifest for that tag was fetched at 2026-11-03T00:22:45Z and its bytes hash to `030ee887880fc378860c2dd35101da424377520441ae4bfe7be6deff8ade7840`. Every number below is bound to a digest like that one, because registry tags can be re-pointed even though the blobs behind a digest are immutable.

## What the tag promises, and what the manifest proves

A tag name is a label, not a contract. `qwen3:32b` names a family and a size. `qwen3:32b-q8_0` names a family, a size and a quantization. `mistral:7b` names a family and a size while the file it points at is 4-bit. The manifest is where the file becomes specific:

1. `config.digest` — points at a small JSON blob. That blob has a `file_type` field. For [qwen3:32b](https://registry.ollama.ai/v2/library/qwen3/manifests/32b) it reads `Q4_K_M`; the config blob itself is [a digest-addressed read of 488 bytes](https://registry.ollama.ai/v2/library/qwen3/blobs/sha256:afdf5c7585b363536f93782f1e44f1b81db4237847cd8b4bd2c5c33b0d76c94b).
2. `layers[]` — each entry has `mediaType` and `size`. The weights are the layer with `mediaType: application/vnd.ollama.image.model`, and that layer alone is what the bits-per-weight arithmetic divides: it is the file that holds the tensors the quantization applies to.
3. The other layers are separate downloads with other jobs: `template`, `params` and `license` are metadata, and a multimodal tag adds `application/vnd.ollama.image.projector`. The metadata layers are small — 1,723 bytes of template, 11,338 of license and 120 of params on `qwen3:32b`, about 13 KB in total — but the projector is not: on `gemma3:4b` it is 851,251,104 bytes, another 34% on top of the 2,499,012,288-byte weight layer. So the pull is 3,350,272,259 bytes even though the weights are 2.5 GB. The projector is part of the download and not part of the bpw calculation; the two numbers answer different questions, and a table that shows only one of them is wrong about the other.
4. The layer digest — a second, independent fingerprint of the weights you are about to pull.

So one unauthenticated `GET` to the manifest, one to the config blob, decides which weights are being served. No key, no auth, no blob download: the 47 reads behind this article's table spanned 18.14 seconds of wall clock, which is under a second for the manifest-plus-config pair of a single tag on this host.

## Method: weight bytes × 8 ÷ parameter count

Bits per weight is a size accounting, and it only needs two honest inputs:

- **Weight bytes** from the manifest's model layer, as above.
- **Parameter count** from the model repository's own metadata — the `safetensors.total` field in Hugging Face's `/api/models/<repo>` response for the exact repository that model card names. Never estimated from file size, because that would make the whole calculation circular.

The nominal figures the measurement is compared against come from llama.cpp's own block definitions in [gguf-py/gguf/constants.py](https://raw.githubusercontent.com/ggml-org/llama.cpp/master/gguf-py/gguf/constants.py), not from a vendor's marketing page: a `Q4_K` block is 144 bytes per 256 weights (4.5 bpw), `Q6_K` is 210 bytes per 256 weights (6.5625 bpw), `Q8_0` is 34 bytes per 32 weights (8.5 bpw). A `Q4_K_M` file is a mixed layout that keeps some tensors at Q6_K, which puts a healthy file at roughly 4.85 bpw overall.

That gives a reconciliation test anyone can apply: if `weights_bytes × 8 ÷ parameters` lands within ±3% of the nominal bpw for the quant the config blob claims, the manifest arithmetic is trustworthy and the download is what it says it is. If it lands wildly off, either the parameter count is wrong or the file is not what the tag claims.

## The audit: 14 tags, 7 families

Each tag links to the manifest it was measured from. `file_type` is read from that manifest's config blob, not guessed from the tag name. Fetch window: 2026-11-03T00:22:44Z to 00:22:50Z, all HTTP 200.

The last column is what `ollama pull` actually transfers: weights plus every other layer in that manifest, summed from the same saved bytes. For the eleven tags without a projector layer it differs from the weights by at most 14 KB and can be ignored. For the three gemma3 tags it does not: 851 MB, 854 MB and 858 MB of projector ride along, which is why `gemma3:4b` costs 3.350 GB of disk and not 2.499 GB.

| Tag | `file_type` (from config) | Weight bytes | Decimal GB | GiB | Measured bpw | vs nominal | All-layer pull (bytes / decimal GB) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| [qwen3:4b](https://registry.ollama.ai/v2/library/qwen3/manifests/4b) | Q4_K_M | 2,497,280,480 | 2.497 | 2.326 | 4.967 | +2.41% | 2,497,293,444 / 2.497 |
| [qwen3:8b](https://registry.ollama.ai/v2/library/qwen3/manifests/8b) | Q4_K_M | 5,225,374,496 | 5.225 | 4.867 | 5.104 | +5.23% | 5,225,387,677 / 5.225 |
| [qwen3:32b](https://registry.ollama.ai/v2/library/qwen3/manifests/32b) | Q4_K_M | 20,201,240,160 | 20.201 | 18.814 | 4.933 | +1.71% | 20,201,253,341 / 20.201 |
| [qwen3:32b-q8_0](https://registry.ollama.ai/v2/library/qwen3/manifests/32b-q8_0) | Q8_0 | 35,132,291,680 | 35.132 | 32.719 | 8.579 | +0.93% | 35,132,304,861 / 35.132 |
| [llama3.1:8b](https://registry.ollama.ai/v2/library/llama3.1/manifests/8b) | Q4_K_M | 4,920,738,944 | 4.921 | 4.583 | 4.902 | +1.08% | 4,920,752,841 / 4.921 |
| [llama3.1:70b](https://registry.ollama.ai/v2/library/llama3.1/manifests/70b) | Q4_K_M | 42,520,398,176 | 42.520 | 39.600 | 4.821 | -0.59% | 42,520,412,073 / 42.520 |
| [gemma3:4b](https://registry.ollama.ai/v2/library/gemma3/manifests/4b) | Q4_K_M | 2,499,012,288 | 2.499 | 2.327 | 4.649 | -4.14% | 3,350,272,259 / 3.350 |
| [gemma3:12b](https://registry.ollama.ai/v2/library/gemma3/manifests/12b) | Q4_K_M | 7,309,830,496 | 7.310 | 6.808 | 4.798 | -1.07% | 8,164,039,587 / 8.164 |
| [gemma3:27b](https://registry.ollama.ai/v2/library/gemma3/manifests/27b) | Q4_K_M | 16,555,661,472 | 16.556 | 15.419 | 4.828 | -0.45% | 17,413,409,507 / 17.413 |
| [mistral:7b](https://registry.ollama.ai/v2/library/mistral/manifests/7b) | Q4_K_M | 4,372,811,712 | 4.373 | 4.072 | 4.826 | -0.48% | 4,372,823,897 / 4.373 |
| [mistral:7b-instruct-q8_0](https://registry.ollama.ai/v2/library/mistral/manifests/7b-instruct-q8_0) | Q8_0 | 7,696,794,208 | 7.697 | 7.168 | 8.495 | -0.05% | 7,696,805,637 / 7.697 |
| [deepseek-r1:8b](https://registry.ollama.ai/v2/library/deepseek-r1/manifests/8b) | Q4_K_M | 5,225,373,760 | 5.225 | 4.867 | 5.206 | +7.33% | 5,225,375,560 / 5.225 |
| [qwen2.5:0.5b](https://registry.ollama.ai/v2/library/qwen2.5/manifests/0.5b) | Q4_K_M | 397,807,936 | 0.398 | 0.370 | 6.442 | +32.82% | 397,820,829 / 0.398 |
| [phi4:14b](https://registry.ollama.ai/v2/library/phi4/manifests/14b) | Q4_K_M | 9,053,114,464 | 9.053 | 8.431 | 4.940 | +1.87% | 9,053,115,905 / 9.053 |

Ten of fourteen tags land inside ±3%. The four that do not are not broken downloads, and understanding why is the difference between a measurement and a superstition:

- **gemma3:4b at 4.649 bpw (-4.14%)** is *smaller* per weight than a textbook Q4_K_M, using the repository total of 4,300,079,472 parameters. A blended figure below 4.85 means part of that model carries fewer bits per weight than the Q4_K_M nominal, on average; which tensors, this audit does not identify. The 851 MB projector layer on this tag is not part of the divisor — it is a separate download — and whether the published parameter total counts parameters that live in that layer is not something this audit established.
- **qwen3:8b (+5.23%) and deepseek-r1:8b (+7.33%)** are *larger* per weight. Both are 8B-class models, where the token embedding and output projection are a big fraction of all parameters and are commonly kept at higher precision than the transformer blocks, which pushes the blended figure up. I did not inspect these files tensor by tensor, so treat that as the expected mechanism rather than a proven per-tensor result.
- **qwen2.5:0.5b at 6.442 bpw (+32.82%)** is the clearest case: at 494,032,768 parameters the embedding and output matrices are a large share of the model, so any precision kept on them dominates the blended number. A small model is exactly where the average diverges most from the block nominal.

The practical reading: bpw is a *range* per quant, not a constant. For Q4_K_M in this sample it spans 4.649 to 6.442, and a ±3% test on a model under 1B parameters will produce false alarms. The test tells you whether a download is plausible, not whether every tensor is where you think it is.

## One model, two quantizations, one comparison

Because parameter count is fixed per model, two tags of the same family compare directly on manifest bytes. `qwen3:32b` and `qwen3:32b-q8_0` both report 32,762,123,264 parameters. Weights go from 20,201,240,160 bytes to 35,132,291,680 bytes — a factor of 1.739 — and bpw from 4.933 to 8.579. That is the entire trade: you get more precision and pay 74% more disk and, at inference, more memory bandwidth per token. Whether Q8_0 is worth it for your workload is a quality question this audit does not answer.

The same table also settles a claim worth testing rather than repeating: the served quant is a property of the *tag*, not of your VRAM. `qwen3:32b` is Q4_K_M because the tag points at a Q4_K_M manifest, and `ollama pull qwen3:32b` will pull those exact bytes on a 12 GB laptop and on a 96 GB workstation alike. Ollama chooses between *tags* you name; it does not silently rebuild a different quant of the tag you asked for.

## Run it yourself

The reader script below is the compact form of the audit: it takes `family:tag` pairs, reads the manifest and its config blob, and prints weight bytes in both unit systems, the config's `file_type`, the origin server's own `Date` header, and a UTC timestamp taken *after* the body was read — never a hand-written time. It downloads no model blobs and needs no account.

```python
#!/usr/bin/env python3
"""One-shot manifest audit: weights bytes -> bits per weight, no blob download."""
import hashlib, json, sys, urllib.request
from datetime import datetime, timezone

def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "manifest-audit/1.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        body = r.read()
        return body, r.status, r.headers.get("Date"), datetime.now(timezone.utc).isoformat()

def manifest(family, tag):
    body, status, server_date, read_at = get(
        f"https://registry.ollama.ai/v2/library/{family}/manifests/{tag}")
    m = json.loads(body)
    weights = sum(l["size"] for l in m["layers"]
                  if l["mediaType"] == "application/vnd.ollama.image.model")
    cfg, _, _, _ = get(f"https://registry.ollama.ai/v2/library/{family}/blobs/{m['config']['digest']}")
    return {"tag": f"{family}:{tag}", "http_status": status, "server_date": server_date,
            "read_at_utc": read_at, "manifest_sha256": hashlib.sha256(body).hexdigest(),
            "weights_bytes": weights, "gb": round(weights / 1e9, 3),
            "gib": round(weights / 2**30, 3), "config_file_type": json.loads(cfg).get("file_type")}

if __name__ == "__main__":
    for spec in sys.argv[1:]:
        family, tag = spec.split(":", 1)
        print(json.dumps(manifest(family, tag)))
```

Run `python3 manifest_audit.py qwen3:32b phi4:14b` and you get back the same manifest hash this article records (`030ee887...` for `qwen3:32b`, `ac896e5b...` for `phi4:14b`), which is how you verify the tag has not been re-pointed since 2026-11-03. To get bits per weight, divide: `weights_bytes * 8 / parameters`, with the parameter total taken from the model repository's own metadata. Environment for this run: `ollama version is 0.20.3` on a 2 vCPU / 11 GB Linux host; the 47 reads behind the table took about 18 seconds of wall clock and downloaded no weights.

Everything above was computed from saved response bytes: raw manifests, config blobs, model-repository metadata and the llama.cpp constant table are kept in this article's evidence directory as a private author-side verification set, hashed in the review receipt so the numbers can be re-checked against what was actually fetched. They are not offered as a downloadable dataset — the script above regenerates the same rows on your machine, which is the more useful artifact anyway.

## What this does not tell you

- **bpw is not quality.** It is bytes per parameter. Two files at 4.9 bpw can differ in how badly they were quantized — which tensors were kept at higher precision, and with what calibration data. A perplexity or eval claim needs an eval, not this arithmetic.
- **Tags move.** These numbers are scoped to the digests and fetch times recorded above. A re-pointed tag will produce different bytes and a different hash; run the script rather than trusting a table, including this one.
- **14 tags is a sample, not a census.** Seven families, chosen to include one model at two quants and one model small enough to check against a local pull. Do not generalize the deviation figures to the whole library.
- **One row was cross-checked locally.** `qwen2.5:0.5b` was compared against the local blob store and `ollama list` on 2026-11-02: the weights digest and size matched the registry. The other 13 tags were never downloaded on this host.

If your download came out at 18.something GB for a 32B model, nothing is wrong. Read the config's `file_type`, multiply the weight bytes by 8, divide by the parameter count, and you will know which weights you are running before the first token is generated.

## Sources

All fetched 2026-11-03 during the run recorded above; every response was saved with its HTTP status, origin `Date` header and sha256 before being used.

Model repository metadata used for parameter totals: [Qwen3-4B](https://huggingface.co/api/models/Qwen/Qwen3-4B), [Qwen3-8B](https://huggingface.co/api/models/Qwen/Qwen3-8B), [Qwen3-32B](https://huggingface.co/api/models/Qwen/Qwen3-32B), [Llama-3.1-8B](https://huggingface.co/api/models/meta-llama/Llama-3.1-8B), [Llama-3.1-70B](https://huggingface.co/api/models/meta-llama/Llama-3.1-70B), [gemma-3-4b-it](https://huggingface.co/api/models/google/gemma-3-4b-it), [gemma-3-12b-it](https://huggingface.co/api/models/google/gemma-3-12b-it), [gemma-3-27b-it](https://huggingface.co/api/models/google/gemma-3-27b-it), [Mistral-7B-Instruct-v0.3](https://huggingface.co/api/models/mistralai/Mistral-7B-Instruct-v0.3), [DeepSeek-R1-Distill-Llama-8B](https://huggingface.co/api/models/deepseek-ai/DeepSeek-R1-Distill-Llama-8B), [Qwen2.5-0.5B](https://huggingface.co/api/models/Qwen/Qwen2.5-0.5B), [microsoft/phi-4](https://huggingface.co/api/models/microsoft/phi-4).

Model cards consulted for the rounded parameter figures the tags do not repeat: [Qwen3-32B card](https://huggingface.co/Qwen/Qwen3-32B/raw/main/README.md) ("Number of Parameters: 32.8B"), [Qwen3-8B card](https://huggingface.co/Qwen/Qwen3-8B/raw/main/README.md) ("Number of Parameters: 8.2B"), [Llama 3.1 model card](https://raw.githubusercontent.com/meta-llama/llama-models/main/models/llama3_1/MODEL_CARD.md), [Mistral-7B-Instruct-v0.3 card](https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.3/raw/main/README.md), [DeepSeek-R1-Distill-Llama-8B card](https://huggingface.co/deepseek-ai/DeepSeek-R1-Distill-Llama-8B/raw/main/README.md), [phi-4 card](https://huggingface.co/microsoft/phi-4/raw/main/README.md).

Quant block sizes: [llama.cpp gguf-py constants](https://raw.githubusercontent.com/ggml-org/llama.cpp/master/gguf-py/gguf/constants.py). Manifest reads for the remaining tags in the table are the per-row links above.

Related reading on this site: [the idealized params × bits ÷ 8 sizing formula and why real artifacts differ](https://baeseokjae.github.io/posts/best-local-llm-models-2026/), [a single-model setup guide with its own quant table](https://baeseokjae.github.io/posts/qwen-3-32b-local-guide-2026/), [the deployment checklist that asks you to record the quantization](https://baeseokjae.github.io/posts/qwen-3-full-lineup-guide-2026/), [model choice for coding assistants](https://baeseokjae.github.io/posts/best-ollama-models-coding-2026/), and [a provider-side quantization comparison](https://baeseokjae.github.io/posts/unsloth-dynamic-3-0-ggufs/).
