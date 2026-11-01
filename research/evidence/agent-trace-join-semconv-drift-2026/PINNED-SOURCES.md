#!/usr/bin/env python3
"""Build research/evidence/<slug>/ artifacts + research/<slug>.json for the research stage.

Every number below came from a real fetch performed 2026-10-31 UTC with curl/gh;
raw bytes are preserved under raw/ so the writer and reviewer can re-grep them.
"""
import csv, hashlib, json, pathlib, subprocess

TREE = pathlib.Path('/home/ubuntu/blog-automation/workspaces/112694a9-ac67-4713-9c7f-619fa9d60c9b/tree')
SLUG = 'agent-trace-join-semconv-drift-2026'
EV = TREE / 'research' / 'evidence' / SLUG
CHECKED = '2026-10-31T12:57:00Z'
GENAI_SHA = '6f98aef121ae3d5f224c5084d9fb4433bc6f7f67'
OAI_SHA = 'e355d69152d4f4730dfb03b63dbce53e8d9f5d8c'
TL_SHA = '8d9c93f37b352131f5871dcb6ecf5e79c19aeb40'
ADK_SHA = '8cd3b12c8a5d658c5e0d3ea0731d8be34a092a4a'

pinned = f"""# PINNED SOURCES - {SLUG}

All fetches performed 2026-10-31 (UTC), from the job tree, with the raw bytes
kept under `raw/`. `sha256` values below are of the saved files.

| id | artifact | ref | sha256 | checked_at |
|----|----------|-----|--------|------------|
| S1 | open-telemetry/semantic-conventions-genai `docs/registry/attributes/gen-ai.md` | commit {GENAI_SHA} | see EVIDENCE-SHA256.txt | {CHECKED} |
| S2 | open-telemetry/semantic-conventions-genai `docs/gen-ai/gen-ai-spans.md` | commit {GENAI_SHA} | see EVIDENCE-SHA256.txt | {CHECKED} |
| S3 | docs.claude.com Claude Code monitoring page (raw HTML, 1,056,403 bytes) | live page, no version pin (page states Traces beta) | see EVIDENCE-SHA256.txt | {CHECKED} |
| S4 | openai/openai-agents-python `src/agents/tracing/span_data.py` (+`spans.py`) | commit {OAI_SHA} | see EVIDENCE-SHA256.txt | {CHECKED} |
| S5 | traceloop/openllmetry `packages/opentelemetry-semantic-conventions-ai/opentelemetry/semconv_ai/__init__.py` | commit {TL_SHA} | see EVIDENCE-SHA256.txt | {CHECKED} |
| S6 | google/adk-python `src/google/adk/telemetry/tracing.py` | commit {ADK_SHA} | see EVIDENCE-SHA256.txt | {CHECKED} |

Repository provenance: `gh api repos/open-telemetry/semantic-conventions-genai`
returned `created_at=2026-05-05T03:08:44Z`, `pushed_at=2026-10-31T04:33:54Z`,
`default_branch=main`.

## Measurement method (reproducible)

```bash
SHA=$(gh api repos/open-telemetry/semantic-conventions-genai/commits/main --jq .sha)
curl -sS -o reg.md  "https://raw.githubusercontent.com/open-telemetry/semantic-conventions-genai/$SHA/docs/registry/attributes/gen-ai.md"
curl -sS -o spans.md "https://raw.githubusercontent.com/open-telemetry/semantic-conventions-genai/$SHA/docs/gen-ai/gen-ai-spans.md"
grep -c '^| .gen_ai.provider.name.' reg.md      # row-count of the attribute table entry
grep -o 'gen_ai\\.system[a-z_.]*' reg.md | sort | uniq -c
```

Observed on {CHECKED}:
- `reg.md`: 1 table row for `gen_ai.provider.name` (line 39, status **Development**,
  well-known values `openai`; `gcp.gen_ai`; `gcp.vertex_ai`), 5 lines mentioning it in total.
- `reg.md`: 4 substring hits for `gen_ai.system`, all of them `gen_ai.system_instructions`
  (lines 67, 316) or `gen_ai.system_instructions_ref` (lines 68, 336). **Zero rows with the
  exact attribute id `gen_ai.system`.**
- `spans.md`: 9 substring hits, all `gen_ai.system_instructions` / `gen_ai.system_instructions_ref`.
  The spans doc therefore does not teach `gen_ai.system` either.

This is a bounded grep over two files, not a registry-wide crawl. It answers one question:
does the current GenAI registry define the exact id `gen_ai.system`? It does not.
