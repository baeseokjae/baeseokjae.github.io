---
cover:
  alt: RockB — AI tools and engineering guides
  image: /images/og-default.png
  relative: false
title: "ToolReplay: Auditing an Agent Session for Non-Determinism and Scope Overreach"
date: 2026-10-08T14:42:00+00:00
tags:
  - "toolreplay"
  - "agent tool call audit"
  - "agent transcript replay"
  - "ai agent observability"
  - "permission overreach detection"
  - "hash chain audit log"
  - "deterministic replay"
  - "agent scope enforcement"
  - "tool call jsonl"
  - "unattended coding agent audit"
  - "agent audit cli"
  - "agent tool call trace 2026"
description: "ToolReplay v0.6.0 is a dependency-free Python CLI that replays a recorded agent tool-call transcript and reports non-determinism, redundant calls and permission overreach. A 2026 review with a reproduced run, the three detectors, and the blind spots the project documents itself."
draft: false
schema: "schema-toolreplay-agent-tool-call-audit-2026"
---

If you let a coding agent run unattended, the only durable record of what it did is the transcript of its tool calls. Dashboards show you totals; the transcript shows you the sequence. ToolReplay is a small, dependency-free Python CLI that reads one such transcript and answers three narrow questions about it: did the same call ever return two different answers, did the agent repeat a call that could not have changed anything, and did it call a tool it was never granted. It reads a JSON Lines file, and it does the work offline.

This review is based on a local reproduction of the tool's own shipped example on 2026-10-08, on two small transcripts constructed for this review, and on the project's published documentation. Every command and its exact output is printed below so the same checks can be repeated against the same public repository.

## What ToolReplay Is, Precisely

ToolReplay is version 0.6.0 at commit `a9f1374479e91ecfcb837658285bfc7a2258dd0b`, the head of `main` in the repository [brandynfisher/ToolReplay](https://github.com/brandynfisher/ToolReplay). It requires Python 3.11 or newer, declares no third-party runtime dependency, and performs no network access; the package metadata and the version string agree at 0.6.0, and the project is MIT-licensed. The name and version are read from the [package metadata](https://raw.githubusercontent.com/brandynfisher/ToolReplay/main/pyproject.toml), the [package init](https://raw.githubusercontent.com/brandynfisher/ToolReplay/main/src/toolreplay/__init__.py) and the tool's own `version` output.

Five subcommands cover the whole surface, and they are deliberately split: replay judges a session against itself and needs no extra input, while scope needs a declared permission file. The [README](https://raw.githubusercontent.com/brandynfisher/ToolReplay/main/README.md) states the reasoning: you can replay a session you have no scope file for, and you can check scope without caring whether the session replayed cleanly.

| Command | What it does | Extra input |
|---|---|---|
| `seal <transcript>` | Prints the hash-chained sealed transcript as JSONL | none |
| `replay <transcript>` | Reports non-determinism, redundant calls and the divergence index | none |
| `verify <sealed>` | Recomputes the chain and names the first broken link | none |
| `scope <transcript> <scope>` | Checks every call against a declared scope file | scope file |
| `version` | Prints the version | none |

The input is not a provider-native trace. It is a four-field JSON Lines record that the tool defines — `index`, `tool`, `args`, `response`, one invocation per line, with no other fields allowed — and its parser refuses malformed input rather than repairing it. A producer has to emit that format; OpenTelemetry spans or vendor JSON have to be converted first. The strictness is stated in the [README](https://raw.githubusercontent.com/brandynfisher/ToolReplay/main/README.md) as a design decision: an audit tool that silently drops an unknown field would be reporting on a session slightly different from the one on disk. Two calls count as identical only when their canonical JSON encoding of tool and args matches with sorted keys, so key order does not matter, and the response is canonicalised the same way.

## The Reproduction: The Shipped Example, Re-run

The repository ships a sample transcript and shows its expected output. Re-cloning the recorded commit and running the two documented commands on the review box returned the same lines the documentation shows, with the same exit codes:

```
$ python -m toolreplay replay samples/session-dirty.jsonl
calls: 6
divergence: index 5
findings: 2
index 2: redundant-call: tool 'read_file' repeats the identical call at index 1 with no state change between them
index 5: non-determinism: tool 'search' returned a different response than the identical call at index 3
[exit code 1]

$ python -m toolreplay scope samples/session-dirty.jsonl samples/scope.json
calls: 6
findings: 1
index 4: permission-overreach: tool 'write_file' is not in the declared scope for agent 'docs-reader'
[exit code 1]
```

Two further checks on the same checkout: replaying the shipped clean sample returns `calls: 4`, `divergence: none`, `findings: 0` and exit code 0, and running the repository's own unit suite with `python -m unittest discover -s tests` reports `Ran 34 tests` and `OK`. Timing from a single run on the review box was 0.014 seconds against the 0.019 seconds the README prints; the suite is stdlib-only, so no test dependency had to be installed. Sealing the same session twice produced byte-identical files, and two replay runs produced byte-identical reports — the deterministic, timestamp-free output the README promises.

## The Three Detectors, Stated as Rules

Non-determinism is reported when a call that is byte-identical after canonical encoding carries a different recorded response; the first such index becomes the divergence point. In the shipped sample, the `search` for `install` recorded 3 hits at index 3 and 7 hits at index 5, so the tool marks index 5 as the divergence. The [README](https://raw.githubusercontent.com/brandynfisher/ToolReplay/main/README.md) is explicit about why this matters for an agent rather than a person: an agent that asks the same question twice and gets two answers cannot be replayed or debugged reliably, because the step that used the first answer may have made a decision the second answer would have changed.

A redundant call is reported only when two identical calls are separated by nothing that could have changed state. A call counts as a possible state change if its tool is in a fixed mutator list — `write_file`, `delete_file`, `create_file`, `move_file`, `run_command` — or if it is any call different from the repeated one. In the sample, index 1 and index 2 both read `docs/intro.md` with nothing between them, so index 2 is flagged. The rule is deliberately conservative, and the README says so: it would rather miss a redundancy than invent one.

Permission overreach is reported when a call's tool name is not in the `allowed_tools` list of a supplied scope file, matched exactly and case-sensitively. The shipped scope file declares one agent to be a reader, per the [sample scope](https://raw.githubusercontent.com/brandynfisher/ToolReplay/main/samples/scope.json): `{"agent": "docs-reader", "allowed_tools": ["read_file", "list_dir", "search"]}`. The write at index 4 is therefore overreach, and the report names both the offending tool and the agent it belongs to. This is the one result that maps directly onto a security question, and the tool frames it as such in its own documentation: did this agent only do what it was allowed to do?

## What the Shipped Sample Is Not

A correction that matters before any of those findings are quoted. The sample is not a captured production session. The repository's own [sample fixtures README](https://raw.githubusercontent.com/brandynfisher/ToolReplay/main/samples/README.md) says the files are "hand-authored test vectors, not captured production data", written to exercise every code path. The six-line [dirty sample](https://raw.githubusercontent.com/brandynfisher/ToolReplay/main/samples/session-dirty.jsonl) is a demonstration of the detectors, not evidence about how agents behave in the field. Any write-up that presents it as a real agent session — including a vendor's own marketing framing — is overstating it, and this review treats it strictly as a fixture.

## Sealing: Tamper-Evident, Not a Signature

`seal` turns each record into a chain link whose SHA-256 digest folds in the previous digest, with a genesis link of 64 zero hex characters. Verification recomputes the chain and checks two things per link: that the stored previous digest equals the digest of the link before it, and that the stored digest matches the record as recomputed. On an intact file the report is one line, `chain: intact`, exit 0.

The tamper probe is the part worth repeating, because it is cheap and the failure output is precise. Changing `{"hits":3}` to `{"hits":4}` at index 3 and re-verifying produced:

```
$ python -m toolreplay verify tampered.jsonl
chain: broken
first broken link: index 3
expected: 34d19a9dfb112baa07afa37994ddcbbebe2973674385f3942340653d08d205bd
found: 40aadf3b8156217f0b5b1d95010b6b79f82a26ccf5e780aed0f5f311f865028a
[exit code 1]
```

Both digests match the values printed in the [README](https://raw.githubusercontent.com/brandynfisher/ToolReplay/main/README.md), which is a good sign for the tool's own documentation hygiene. The limits are equally explicit there: the chain is not a signature. Anyone who can edit the file can re-seal it into a fresh, internally consistent chain, so the chain proves that a sealed file has not been edited since sealing — not that the sealer was honest.

## Two Boundary Probes You Can Repeat

The most useful thing this review did was probe the two edges the README names. Both probe transcripts are short enough to print in full. The first adds one call outside the declared scope to a five-line session, using `delete_file`, which is a mutator in the default list:

```
{"index": 0, "tool": "list_dir", "args": {"path": "docs"}, "response": {"entries": ["intro.md", "guide.md"]}}
{"index": 1, "tool": "read_file", "args": {"path": "docs/intro.md"}, "response": {"bytes": 214}}
{"index": 2, "tool": "delete_file", "args": {"path": "docs/guide.md"}, "response": {"ok": true}}
{"index": 3, "tool": "search", "args": {"query": "install"}, "response": {"hits": 3}}
{"index": 4, "tool": "search", "args": {"query": "install"}, "response": {"hits": 3}}
```

Scope flags index 2 as permission-overreach for `docs-reader`, exit 1. Replay on the same file reports `divergence: none` with one finding — the repeated search at index 4 is redundant, and because the two responses are identical it is correctly not called non-deterministic. That pairing is the useful signal: a repeat with the same answer and no state change between is waste, not a determinism problem.

The second probe tests the documented blind spot directly. One line, the permitted tool pointed at a forbidden target:

```
{"index": 0, "tool": "read_file", "args": {"path": "/etc/passwd"}, "response": {"bytes": 1}}
```

Run against the shipped scope, this produces `calls: 1`, `findings: 0` and exit code 0. The name-based scope check sees a permitted tool name and passes it. That is not a defect finding; it is the project's own documented limitation, reproduced, and the [README](https://raw.githubusercontent.com/brandynfisher/ToolReplay/main/README.md) lists argument-aware scope first on its roadmap.

A third check confirmed the exit-code split. A transcript with one extra unknown field exits 2 with `error: line 1: unexpected field(s): extra`, which is the "the tool could not run" code rather than the "the tool ran and found something" code — the distinction a CI gate needs. The [README](https://raw.githubusercontent.com/brandynfisher/ToolReplay/main/README.md) documents the three codes as 0 for clean, 1 for findings or a broken chain, and 2 for a usage, parse or missing-file error.

## The Blind Spots, In the Project's Own Words

ToolReplay's limitations section is unusually candid, and it is the single best reason to trust the tool's reports within its scope. It replays recorded responses and never calls real tools, so a problem that was never recorded cannot be found. Redundancy detection assumes no hidden state change it cannot see: if another process edits a file between two identical reads, the second read may be flagged as redundant when it was not, and a custom mutating tool outside the fixed list is treated as read-only. Non-determinism is detected only between byte-identical calls, so the tool cannot judge whether two different responses are semantically equivalent, and it cannot see non-determinism in a call that never repeats. Scope matching is name-based and case-sensitive only. Sealing is tamper-evident, not a signature.

| Question | ToolReplay's answer | Where it stops |
|---|---|---|
| Did a repeated call return something different? | Yes, with the first diverging index | Only for calls that repeat byte-identically |
| Was a call wasted? | Yes, when nothing between two identical calls could change state | Hidden state changes and non-listed mutators are invisible |
| Did the agent exceed its grant? | Yes, by tool name, case-sensitively | Not by argument or target |
| Has the transcript been edited since sealing? | Yes, down to the first broken link | Not against a dishonest re-sealer |
| What actually happened to the filesystem? | Nothing measured; recorded responses only | The tool never re-executes the session |

## A Snapshot of the Repository Itself

The [GitHub repository API](https://api.github.com/repos/brandynfisher/ToolReplay) returned, on 2026-10-08: created 2026-09-14, last push 2026-09-14, 182 stars, 21 forks, Python, default branch `main`, MIT licence, and `has_issues` false — issue tracking is disabled, so there is no public issue thread to corroborate anything. Two details are worth flagging rather than repeating uncritically. The homepage metadata field still points at an unrelated URL, and the [release objects](https://api.github.com/repos/brandynfisher/ToolReplay) were all published on 2026-09-14 with author `brandynfisher`, while the [CHANGELOG](https://raw.githubusercontent.com/brandynfisher/ToolReplay/main/CHANGELOG.md) prints authored release dates from 2021-06-14 through 2026-03-12. The release history as authored reads as a multi-year project; as published on the forge it is a single day in September 2026. Treat the CHANGELOG dates as authored history, not independently timestamped releases. Star and fork counts are a point-in-time snapshot and will drift.

## Where This Fits

ToolReplay audits an existing transcript rather than producing a score, which separates it from the [eval-harness comparisons](/posts/open-source-agent-eval-harness-comparison-2026/) that generate benchmarks. It is narrower than the [agent observability tooling landscape](/posts/ai-agent-observability-tools-2026/) and the [OpenTelemetry tracing standard](/posts/ai-agent-observability-opentelemetry-2026/), because it ingests one format and does not instrument a running agent. Its sealed chain is a record, not the richer [provenance records](/posts/trace-file-lineage-agent-provenance-2026/) a lineage system carries, and it does not help you decide what an agent should be [allowed to do](/posts/secure-ai-agents-least-privilege-2026/) — it tells you whether it stayed inside a declaration you already made.

## Should You Use It

For a team that already records agent tool calls into its own JSONL, ToolReplay is a good fit: it is small enough to read, it refuses to guess at malformed input, it exits non-zero on findings so it drops into CI as the command itself, and its reports are deterministic enough to commit and diff between runs. Those are the properties that make an audit artifact trustworthy, and the tool's documentation is honest about the four things it cannot see.

It is not a general audit system. It has no argument-level scope enforcement, no signature over the final digest, no machine-readable report format, and no ingestion path for OpenTelemetry or vendor traces. If your agent emits a provider-native trace today, ToolReplay will not read it without you writing a converter, and a converter that loses a field it does not understand would defeat the strictness the tool is built around. It also should not be read as evidence about how agents generally behave: the shipped sample is a fixture, and one reproduced example is one example.

## Sources

Primary sources re-checked on 2026-10-08, listed so the same checks can be repeated:

- Project repository — https://github.com/brandynfisher/ToolReplay
- README (commands, findings rules, transcript format, seal/verify, exit codes, limitations, roadmap, verification counts) — https://raw.githubusercontent.com/brandynfisher/ToolReplay/main/README.md
- CHANGELOG (authored release dates) — https://raw.githubusercontent.com/brandynfisher/ToolReplay/main/CHANGELOG.md
- Sample fixtures README ("hand-authored test vectors, not captured production data") — https://raw.githubusercontent.com/brandynfisher/ToolReplay/main/samples/README.md
- Shipped scope declaration — https://raw.githubusercontent.com/brandynfisher/ToolReplay/main/samples/scope.json
- Shipped dirty sample transcript — https://raw.githubusercontent.com/brandynfisher/ToolReplay/main/samples/session-dirty.jsonl
- Package metadata (version, Python floor, licence) — https://raw.githubusercontent.com/brandynfisher/ToolReplay/main/pyproject.toml
- Package version string — https://raw.githubusercontent.com/brandynfisher/ToolReplay/main/src/toolreplay/__init__.py
- Repository metadata API (created/pushed dates, stars, forks, licence, issue-tracking flag, homepage field) — https://api.github.com/repos/brandynfisher/ToolReplay
- Reproduction record for this review, published with the post (exact commands, stdout, exit codes and transcript hashes for every run above) — https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/toolreplay-agent-tool-call-audit-2026/first-party-run-2026-10-08.json

The reproduction described above was run locally by the author on a review box, cloning the public repository at the recorded commit. The two boundary-probe transcripts are printed in full in this article, the run record with every command and exit code is published alongside the post at the link above, and the shipped sample and scope file are public in the repository — so every check here is repeatable from primary sources without reading this author's machine. Downloaded third-party source snapshots and other local working files are not republished. No claim is made about other teams' usage, adoption, or security outcomes, and no benchmark score, cost figure, or vendor comparison is asserted.
