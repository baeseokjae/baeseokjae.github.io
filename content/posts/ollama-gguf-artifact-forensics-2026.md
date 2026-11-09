---
title: "What You Actually Pulled: Reading Quantisation, Parameter Count and Context Out of an Ollama GGUF File"
description: "A 31B tag pulls 18.99 GiB of layers — an 18,670,033,120-byte model blob against 61.4 GB for the same weights in bf16 — and nothing ollama prints says which quantisation is inside. An 8–32 MiB ranged read of the GGUF header returns the tensor table, so bits per weight, parameter count and the declared context field become numbers you can check before the download finishes."
date: 2026-11-06 00:00:00+00:00
lastmod: 2026-11-06 14:51:00+00:00
draft: false
schema: schema-ollama-gguf-artifact-forensics-2026
tags:
  - Ollama
  - GGUF
  - quantization
  - bits per weight
  - local LLM
  - artifact provenance
  - model sizing
---

You pulled a tag. The download is 18.99 GiB for a model the card calls 31B. The agent that needed long history behaves as if it had a fraction of the context the card advertises. The quality does not match the benchmark chart that made you choose the model in the first place. None of those three surprises is a property of the model. All three are properties of the artifact: which quantisation the tag actually resolved to, how many bits per weight that quantisation really costs, and which metadata value declares the context this particular build was made for.

This article answers those three questions from the bytes rather than from the tag name. Every figure below comes from a ranged HTTP read of the file header — 8 to 32 MiB out of a 5–19 GB file — so no weights were downloaded, no server was started, and no throughput, quality or VRAM claim is made or implied. Five artifacts were read on 2026-11-06: three published GGUF files and two Ollama registry blobs.

## The file on disk does not match the card

The unsloth repository `unsloth/gemma-4-31B-it-GGUF` lists its bf16 build as two shards of 49,950,156,960 and 11,463,033,568 bytes, which is 61,413,190,528 bytes or 57.2 GiB ([repository index](https://huggingface.co/api/models/unsloth/gemma-4-31B-it-GGUF?blobs=true)). The same index lists `gemma-4-31B-it-Q4_K_M.gguf` at 18,323,733,440 bytes. That is 17.07 GiB, 18.32 decimal GB, and 3.35× smaller than the bf16 build.

So "18 GB, not 48 GB" contains two separate confusions. The 18 figure is real: it is the 4-bit file, and it looks smaller in GiB than in decimal GB because binary units divide by 1,073,741,824. The 48 figure corresponds to nothing in that repository — the bf16 weights there are 61.41 decimal GB, and a Q8_0 build of the same weights lands at 8.5 bits per weight rather than 16. Once the quantisation is known, both sizes are arithmetic.

The catch is that `31B` is a name, not a specification. The name tells you the parameter class; it says nothing about the 4.77 bits per weight the file actually spends. `ollama show` prints a Modelfile back at you, and that Modelfile is a description of how to load the blob, not of what is inside it. The manifest audit in [the tag-size article](https://baeseokjae.github.io/posts/ollama-tag-quant-bits-per-weight-audit-2026/) takes the first step: it divides a manifest's model-layer bytes by the parameter total published by the model repository, and states plainly that it did not inspect tensors. This piece takes the second step and reads the tensor table, so numerator and denominator come from the same file.

## GGUF is a directory inside a file

A GGUF file begins with the magic `GGUF`, a version, a tensor count and a metadata key/value count, then a metadata block of typed key/value pairs, then one tensor-info record per tensor holding its name, dimensions, quantisation type and byte offset. The weight data starts after that array, padded to the alignment boundary, and each tensor offset is relative to the start of the data section rather than to the start of the file ([GGUF specification](https://github.com/ggml-org/ggml/blob/master/docs/gguf.md)).

That layout is what makes a header read sufficient. The tensor-info array carries the type of every tensor and the size of every dimension, so the full weight map — how many bytes at which precision, how many elements in total — is available before a single weight is fetched. The weights themselves are only needed to run the model, not to describe it.

## Reading it without downloading it

The probe sends two requests per artifact. A `HEAD` gives `Content-Length`, the exact size of the file. A `GET` with `Range: bytes=0-33554431` returns the first 32 MiB, which is enough for the metadata block, the tokenizer arrays and the tensor-info array of a 262,144-token vocabulary.

The window has to clear the header, and how much that takes is a property of the file, not a constant. A 1 MiB window fails on the Gemma file before the tensor table is complete (`EOFError: window ended at 1048576; need 13 more`), and 8 MiB still fails there (`window ended at 8388608; need 8 more`) because the 262,144-token vocabulary pushes the weight section out to byte 15,834,176. The same 8 MiB window was already enough for both Qwen3 files, whose weight sections start at 5,956,416 and 5,956,384 bytes. In the saved batch three artifacts parsed at 32 MiB — the Gemma file and both registry blobs — and two parsed at 8 MiB (Qwen3-8B-Q4_K_M at 14:34:01Z, Qwen3-8B-Q8_0 at 14:34:04Z); a later 32 MiB rerun of Qwen3-8B-Q4_K_M at 14:41:15Z reproduced the same values. The parser raises on a short window instead of returning the tensors it managed to read, which matters: a silently truncated tensor list still produces a plausible-looking bits-per-weight number that is simply wrong.

The five successful reads ran between 14:34:01Z and 14:34:33Z on 2026-11-06, each returning HTTP 206 and taking 1.41–4.03 s of wall clock. The two registry blobs answered fastest (1.41 s and 1.62 s) and the Gemma file slowest (4.03 s), a spread that tracks the origin rather than the 8- or 32-MiB span. The SHA-256 of each fetched span was recorded so a later rerun can prove it read the same bytes.

## Worked example: gemma-4-31B-it Q4_K_M

The file's header declares architecture `gemma4`, 60 blocks, 262,144 tokens of context, and 833 tensors. Adding up the dimensions gives 30,697,345,596 stored elements — the parameter count of this file, not of the family. Multiplying each tensor's element count by its type's block width gives 18,307,897,584 bytes of weights.

| Quantisation | Tensors | Bytes | Share of weight bytes |
| --- | --- | --- | --- |
| Q4_K (4.5 bpw nominal) | 356 | 15,006,007,296 | 81.96% |
| Q6_K (6.5625 bpw nominal) | 55 | 3,296,563,200 | 18.01% |
| F32 (32 bpw) | 422 | 5,327,088 | 0.03% |

8 × 18,307,897,584 ÷ 30,697,345,596 = 4.7712 bits per weight. The 422 F32 tensors are almost all small norms and biases: they are 422 of the 833 tensor records but 0.03% of the bytes.

The reconciliation is what makes that ratio trustworthy rather than decorative. The weight section begins at byte 15,834,176, so the file's published size leaves 18,307,899,264 bytes for weights. The tensor table accounts for 18,307,897,584 of them — a residue of 1,680 bytes, 0.00001%, which is the alignment padding after the final tensor. A wrong block table, a missed tensor or a misread dimension cannot land on that total by accident.

## Why "4-bit" is 4.77 and "8-bit" is 8.50

Block geometry explains the gap between the label and the measurement. In llama.cpp's quantisation table a K-quant block covers 256 elements: Q4_K spends 144 bytes per block (4.5 bpw), Q6_K spends 210 (6.5625 bpw), and Q8_0 — a 32-element block — spends 34 (8.5 bpw) ([constants.py](https://raw.githubusercontent.com/ggml-org/llama.cpp/master/gguf-py/gguf/constants.py)).

A `Q4_K_M` file is a mixture. The `_M` variant keeps selected tensors at a higher precision, so on the Gemma file 18.01% of weight bytes are Q6_K and the blended figure is 4.7712 rather than 4.5. The Qwen3-8B Q4_K_M file shows the same mechanism at a different ratio: 3,704,979,456 bytes of Q4_K, 1,315,614,720 of Q6_K and 1,232,896 of F32 over 8,190,735,360 elements, giving 4.9049 bpw with 26.20% of weight bytes at Q6_K. The Q8_0 build of the same 8.19B parameters spends 8,702,328,832 bytes at Q8_0 plus the same 1,232,896 bytes of F32 and measures 8.5009.

The practical consequence: "4-bit" and "8-bit" are labels for a mixture, and the blended figure moves with how much of the file the quantizer kept at higher precision. If the number matters — and it does when you are deciding whether a file fits in VRAM or on a laptop disk — it has to be summed from the tensors.

## The tag is not the file

An Ollama tag resolves to a registry manifest, and that manifest names layers with exact byte sizes and digests. Reading the model layer of `gemma4:31b` and parsing it the same way gives a different file from the same-named Hugging Face build.

| Artifact | Bytes | Q4_K bytes | Q6_K bytes | Parameters | bpw |
| --- | --- | --- | --- | --- | --- |
| HF `gemma-4-31B-it-Q4_K_M.gguf` | 18,323,733,440 | 15,006,007,296 | 3,296,563,200 | 30,697,345,596 | 4.7712 |
| Ollama `gemma4:31b` model layer | 18,670,033,120 | 14,250,442,752 | 4,398,428,160 | 30,697,345,596 | 4.8614 |

Same architecture, same 60 blocks, same 262,144-token context field, same parameter count — 346,299,680 more bytes, and a different mixture: 23.58% of the tag's weight bytes are Q6_K against 18.01% in the Hugging Face file. The manifest's own `from` field names the upstream publisher tag `dhiltgen/gemma4:31b-it-mtp-q4_K_M-llamacpp`, not a Hugging Face repository, so size and mixture similarity cannot establish which repository this blob was converted from. Treat provenance as unknown and check the bytes you have.

The same divergence appears at 8B. The Ollama `qwen3:8b` model layer is 5,225,374,496 bytes against 5,027,783,488 for `Qwen3-8B-Q4_K_M.gguf`, and it carries 301,989,888 bytes of F16 tensors the Hugging Face Q4_K_M does not, with 1,253,683,200 bytes of Q6_K against 1,315,614,720. Bits per weight: 5.0979 versus 4.9049, over an identical 8,190,735,360 parameters.

A tag can also be more than one model. `gemma4:31b` is projector 1,200,726,368 + model 18,670,033,120 + draft 514,687,072 bytes — 20,385,446,560 weight-bearing bytes, and 20,385,457,992 bytes across every layer including template, license and params. That is 18.99 GiB of download for a file advertised as 31B at 4-bit. The projector is a separate artifact with its own cost profile, covered in [the projector article](https://baeseokjae.github.io/posts/local-vlm-tag-projector-image-token-cost-2026/); it is not part of a weights-only bits-per-weight ratio, and adding it to the denominator would make the number meaningless.

## Which context value wins

Three different quantities get called "the context length", and they are not interchangeable.

The first is the field inside the artifact. Parsing the metadata block gives `gemma4.context_length = 262144` and `qwen3.context_length = 40960`. For the Qwen3-8B files that 40,960 is the positional-embedding allocation the vendor ships in `config.json` as `max_position_embeddings`; it is not a statement of the length the weights were trained on.

The second is the model card's own framing, which states the limits separately: "Context Length: 32,768 natively and 131,072 tokens with YaRN". The card then explains where 40,960 comes from: "The default max_position_embeddings in config.json is set to 40,960. This allocation includes reserving 32,768 tokens for outputs and 8,192 tokens for typical prompts, which is sufficient for most scenarios involving short text processing" ([Qwen3-8B card](https://huggingface.co/Qwen/Qwen3-8B)). Read as three numbers rather than one: 32,768 native, 131,072 with YaRN scaling, and 40,960 as a padded default that splits into an 8,192-token prompt budget and 32,768 reserved for generation. An agent carrying a 30k-token tool history is asking for more prompt than that arrangement allows, on a card whose headline number reads "40,960".

The third is the runtime option, and it is the one that decides what is actually served. Ollama's Modelfile reference defines `PARAMETER num_ctx 4096` as setting "the context window size to 4096, this controls how many tokens the LLM can use as context to generate the next token" ([Modelfile reference](https://docs.ollama.com/modelfile.md)), and a tag's `params` layer is where such a value would be baked in. Both tags' params layers are readable: the registry blob URL answers HTTP 307 to a presigned object URL, and following it returns 64 bytes for `gemma4:31b` (`draft_num_predict`, `temperature`, `top_k`, `top_p`) and 120 bytes for `qwen3:8b` (`repeat_penalty`, `stop`, `temperature`, `top_k`, `top_p`). Neither contains `num_ctx`, so neither tag pins a window. What is established is the boundary: the artifact's declared length is not the served length, the tag's params do not set it, and the value that does comes from a server default or a per-request option. [The truncation diagnosis](https://baeseokjae.github.io/posts/ollama-silent-context-truncation-2026/) covers what the server does when a conversation exceeds that cap.

## A five-minute checklist before trusting a tag

1. Run `ollama show --modelfile qwen3:8b` and read the `PARAMETER` lines and the architecture line. That is the loading recipe, not the file contents.
2. Take the file's exact size: `curl -sI <resolve-url> | grep -i content-length`, or read the model layer's `size` from the registry manifest at `https://registry.ollama.ai/v2/library/<family>/manifests/<tag>`.
3. Compare that size with the size the same-named file has in the model repository. A mismatch means the tag is a different requantisation, which is normal, not a bug — but it means benchmarks measured on the repository file do not automatically describe your file.
4. Fetch the first 32 MiB and parse the header with the script below. You get the quantisation mix, the parameter count, the declared context and the bits per weight in one pass.
5. Sanity-check the ratio against block geometry: a Q4_K_M file at 7B or larger typically blends to the high 4s, and anything inside 4.5–5.2 is a normal mixture; a Q8_0 file lands near 8.5. A figure outside that band means the parser or the fixture is wrong.
6. Read `context_length` from the same output and set `num_ctx` deliberately. Do not inherit a default and then debug the model's memory.

## What this check cannot tell you

The measurement is a weights-only ratio: metadata, tokenizer arrays and alignment padding are excluded by construction, which is why the reconciliation compares against `Content-Length` minus the data offset rather than the whole file. It says nothing about output quality, tokens per second, VRAM in use or whether the mixture is a good one — all of those need a running server and a workload, and none was measured here. It covers five artifacts: three published GGUF files and two registry blobs, with no IQ-series, Q3, Q5 or MXFP4 file parsed. Ollama tags are mutable, so every size and digest here is true for 2026-11-06 and can change when a tag is re-pushed. And the ratio cannot prove where a blob came from; it can only prove what is inside the bytes you fetched.

## Reproduce it

Save this as `probe_range.py` and run `python3 probe_range.py <gguf-url>`. It downloads no weights, needs no account, and prints one JSON record per artifact.

```python
#!/usr/bin/env python3
"""Read a GGUF header over HTTP Range: quant mix, bits-per-weight, parameters, context."""
import json
import struct
import sys
import urllib.request

# (elements_per_block, bytes_per_block) from llama.cpp gguf-py/gguf/constants.py
BLOCK = {"F32": (1, 4), "F16": (1, 2), "BF16": (1, 2), "Q4_0": (32, 18), "Q4_1": (32, 20),
         "Q5_0": (32, 22), "Q5_1": (32, 24), "Q8_0": (32, 34), "Q2_K": (256, 84),
         "Q3_K": (256, 110), "Q4_K": (256, 144), "Q5_K": (256, 176), "Q6_K": (256, 210),
         "Q8_K": (256, 292)}
SCALAR = {0: "B", 1: "b", 2: "H", 3: "h", 4: "I", 5: "i", 6: "f", 7: "?",
          10: "Q", 11: "q", 12: "d"}
ENUM = {0: "F32", 1: "F16", 2: "Q4_0", 3: "Q4_1", 4: "Q4_1", 5: "Q5_0", 6: "Q5_0",
        7: "Q5_1", 8: "Q8_0", 9: "Q8_1", 10: "Q2_K", 11: "Q3_K", 12: "Q4_K",
        13: "Q5_K", 14: "Q6_K", 15: "Q8_K", 30: "BF16"}


class Reader:
    def __init__(self, buf):
        self.b, self.p = buf, 0

    def take(self, n):
        if self.p + n > len(self.b):
            raise EOFError(f"window ended at {len(self.b)}; need {n} more")
        out = self.b[self.p:self.p + n]
        self.p += n
        return out

    def scalar(self, fmt):
        return struct.unpack("<" + fmt, self.take(struct.calcsize(fmt)))[0]

    def string(self):
        return self.take(self.scalar("Q")).decode("utf-8", "replace")

    def skip_value(self, vtype):
        if vtype in SCALAR:
            self.take(struct.calcsize(SCALAR[vtype]))
        elif vtype == 8:
            self.take(self.scalar("Q"))
        elif vtype == 9:
            inner, count = self.scalar("I"), self.scalar("Q")
            for _ in range(count):
                self.skip_value(inner)
        else:
            raise ValueError(f"unknown metadata value type {vtype}")


def probe(url, span=32 * 1024 * 1024):
    req = urllib.request.Request(url, headers={"Range": f"bytes=0-{span - 1}",
                                              "User-Agent": "gguf-range-probe/1.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        buf, status = resp.read(), resp.status
        length = int(resp.headers["Content-Range"].rsplit("/", 1)[1])
    r = Reader(buf)
    if r.take(4) != b"GGUF":
        raise ValueError("not a GGUF file")
    version, n_tensors, n_kv = r.scalar("I"), r.scalar("Q"), r.scalar("Q")
    meta = {}
    for _ in range(n_kv):
        key = r.string()
        if SCALAR.get((vtype := r.scalar("I"))):
            meta[key] = r.scalar(SCALAR[vtype])
        elif vtype == 8:
            meta[key] = r.string()
        else:
            r.skip_value(vtype)
    tensors = []
    for _ in range(n_tensors):
        name = r.string()
        dims = [r.scalar("Q") for _ in range(r.scalar("I"))]
        tensors.append((name, dims, ENUM.get(r.scalar("I"), "?"), r.scalar("Q")))
    data_start = (r.p + 31) // 32 * 32
    mix, elements, nbytes = {}, 0, 0
    for _name, dims, qtype, _off in tensors:
        count = 1
        for d in dims:
            count *= d
        if qtype not in BLOCK:
            raise ValueError(f"block table missing {qtype}")
        per, width = BLOCK[qtype]
        size = count // per * width
        mix[qtype] = mix.get(qtype, 0) + size
        elements += count
        nbytes += size
    arch = meta.get("general.architecture", "?")
    return {"url": url, "http_status": status, "content_length": length,
            "range_bytes": len(buf), "gguf_version": version,
            "architecture": arch, "file_type": meta.get("general.file_type"),
            "context_length": meta.get(f"{arch}.context_length"),
            "block_count": meta.get(f"{arch}.block_count"),
            "parameter_count": elements, "weight_bytes": nbytes,
            "bits_per_weight": round(8 * nbytes / elements, 4),
            "quant_mix_bytes": dict(sorted(mix.items())),
            "tensor_count": n_tensors, "header_data_start": data_start,
            "weight_section_bytes": length - data_start}


if __name__ == "__main__":
    print(json.dumps(probe(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 32 << 20), indent=1))
```

Run against the Gemma file, the script prints `content_length: 18323733440`, `parameter_count: 30697345596`, `bits_per_weight: 4.7712`, `header_data_start: 15834176` and the three-entry quantisation mix — the figures in the table above, reproduced from a fresh ranged read on 2026-11-06 at 14:41Z.

The run records behind those numbers — the probe output, the window-failure records, the registry manifests, the two params-layer bodies, the fetched spec and the method note — are kept in this article's evidence directory under `research/evidence/ollama-gguf-artifact-forensics-2026/` as a private author-side verification set, hashed in the review receipt so each figure can be re-checked against what was actually fetched. They are not offered as a downloadable dataset, and no reader-facing archive is promised; the script above regenerates every row on your machine.

## Sources

- GGUF file format specification, `ggml-org/ggml`: https://github.com/ggml-org/ggml/blob/master/docs/gguf.md
- Ollama Modelfile reference (`PARAMETER num_ctx`): https://docs.ollama.com/modelfile.md
- `unsloth/gemma-4-31B-it-GGUF` file index with per-file sizes and SHA-256: https://huggingface.co/api/models/unsloth/gemma-4-31B-it-GGUF?blobs=true
- `Qwen/Qwen3-8B-GGUF` file index: https://huggingface.co/api/models/Qwen/Qwen3-8B-GGUF?blobs=true
- Ollama registry manifest for `gemma4:31b`: https://registry.ollama.ai/v2/library/gemma4/manifests/31b
- Ollama registry manifest for `qwen3:8b`: https://registry.ollama.ai/v2/library/qwen3/manifests/8b
- Ollama `gemma4:31b` params layer (64 B, follows a 307 to object storage): https://registry.ollama.ai/v2/library/gemma4/blobs/sha256:2365fbb6d97bf654fdda0353b7505baa2254c662122cff0f153e4b47e6220ded
- Ollama `qwen3:8b` params layer (120 B, follows a 307 to object storage): https://registry.ollama.ai/v2/library/qwen3/blobs/sha256:cff3f395ef3756ab63e58b0ad1b32bb6f802905cae1472e6a12034e4246fbbdb
- Qwen3-8B model card (40,960-token allocation): https://huggingface.co/Qwen/Qwen3-8B
- llama.cpp quantisation block sizes, `gguf-py/gguf/constants.py`: https://raw.githubusercontent.com/ggml-org/llama.cpp/master/gguf-py/gguf/constants.py
