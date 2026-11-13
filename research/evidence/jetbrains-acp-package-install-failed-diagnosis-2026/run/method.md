# Method: loopback stub ACP registry, five injected install defects

Collected 2026-11-12 with the article's own scripts in this directory (`run/`).
Everything is local: loopback HTTP only, no vendor endpoint, no credentials, no
downloads of third-party code, no JetBrains IDE.

## What is modelled

Only the contract documented in the ACP registry `FORMAT.md`: one index
document (`version`, `agents[]`) whose entries carry inline `distribution`
blocks (`binary` keyed by platform, `npx`, `uvx`), and artifact files addressed
by URL. `acp_stub_registry.py` serves exactly two routes —
`/registry-for-jetbrains.json` and `/artifacts/<file>` — and appends one JSONL
record per request (method, path, status, bytes, latency_ms).

Nothing about the JetBrains client's internals is modelled. The log line in the
article is user-reported; the fixture does not claim to reproduce it.

## Cases

A fresh fixture directory and a fresh ephemeral loopback port are used per case.
The clean control (D0) exists to prove the checker does not fail a healthy
entry. Each defect removes or corrupts exactly one contract element:

| Case | Injection |
| --- | --- |
| D0_clean | index 200, artifact 200, declared sha256 matches served bytes |
| D1_index_404 | index route returns 404 (no fixture file present) |
| D2_missing_license_url | entry omits `license_url`, documented as required |
| D3_checksum_mismatch | served artifact bytes differ; index declares the correct sha256 |
| D4_artifact_unreachable | entry's `archive` URL points at a reserved-then-closed loopback port |
| D5_platform_gap | `distribution` declares only `darwin-aarch64`; no npx/uvx fallback |

## Run

```
python3 run_defects.py --out .
```

Writes `fixtures/<case>/`, `transcripts/<case>.jsonl`, `checker/<case>.txt` and
`results.json`. Deterministic apart from the ephemeral ports, which are recorded
in `results.json` and in the checker logs.

The `$ ...` header line in each `checker/<case>.txt` is generated from the argv
the runner actually executed (only the interpreter and script paths are reduced
to bare names), so the logged command cannot drift from the flags the checker
received. No `--ide-build` value is passed: there is no JetBrains IDE on this
host, so any build number here would be a placeholder presented as an
observation. `results.json` records `ide_build_checked: false` and says so.

## Observed result (published run)

- control exit 0; five defects exit 1 with five distinct first failing checks:
  `index_fetch`, `entry_schema`, `artifact_sha256`, `artifact_fetch`,
  `distribution_select`;
- no false PASS;
- 6 cases in 2.6 s wall clock (`wall_clock_s` in `results.json`);
- environment: Python 3.12.3, Node.js v24.21.0, npm 11.19.0,
  Linux 6.17.0-1019-oracle aarch64 (glibc 2.39); target platform evaluated as
  `linux-x86_64` and no artifact was executed.

## Deviations from the research plan, recorded rather than smoothed over

1. The plan's D5 was "entry declares a minimum IDE build above the test value".
   The registry `FORMAT.md` documents no minimum-IDE field, so publishing that
   case would have required inventing a field name. D5 was replaced with a
   documented failure class: no `binary` target for the host platform and no
   `npx`/`uvx` fallback. The IDE version floor (2025.3) is still covered in the
   article, but as a client-side check no registry response can answer.
2. The plan described per-agent `manifest.json` endpoints. The published index
   is a single document with inline `distribution` blocks, so the fixture
   models the index as documented rather than the planned three-endpoint shape.
3. No IDE was available, so no IDE-side log was produced and no exception chain
   is claimed.

## Limit

The fixture shows that the contract layer admits five failures that a single
`package_install_failed` token cannot separate. It does not show what the client
prints for each, which cannot be observed from outside the client.
