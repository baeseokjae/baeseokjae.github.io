---
title: "ZCode GLM Coding Agent Silently Uploads Your Git History: What It Means"
date: 2026-09-29T22:26:53+00:00
tags:
  - zcode glm coding agent git history
  - zcode silently uploads git history
  - zcode aliyun oss upload
  - zcode upload-credential endpoint
  - zcode privacy policy workspace snapshot
  - does zcode upload my code
  - zcode repo wiki upload
  - disable zcode snapshot upload
  - zcode chattr +i checkpoints
  - is zcode open source
  - zcode 3.14.0 repo wiki removed
  - zai zcode open source apache 2.0
  - zcode git history leak
  - zcode app.asar reverse engineering
  - glm coding plan data privacy
  - coding agent telemetry audit
  - open source harness vs closed source harness
  - do not trust closed source ai harness
  - rotate secrets after ai agent upload
  - zai caict nsfocus audit
description: "ZCode silently packaged users' workspaces, encrypted them with a server-held key and shipped them to Alibaba Cloud OSS. Here is what that means for you."
draft: false
cover:
  image: "/images/zcode-glm-coding-agent-git-history-leak-2026.png"
  alt: "ZCode GLM Coding Agent Silently Uploads Your Git History: What It Means"
  relative: false
schema: schema-zcode-glm-coding-agent-git-history-leak-2026
---

The ZCode GLM coding agent silently uploaded user Git history: client version 3.12.3 packaged each logged-in user's whole workspace, encrypted it with an RSA key supplied by Z.ai's own server, and POSTed the archive straight to Alibaba Cloud OSS. No consent prompt. No policy disclosure. No working opt-out.

The short version of the verdict, before the detail: this was not inference-context transmission, the ordinary and largely unavoidable process of sending code to a model so it can reason about it. It was unattended whole-repository exfiltration, of a repository the user never selected, encrypted with a key the user can never use — which is also why the vendor's "we deleted it" assurance is not falsifiable from outside. The full timeline runs from a subscriber noticing 700MB of disk growth on 2026-09-17 to an Apache-2.0 source drop on 2026-09-21 and a follow-up client release on 2026-09-23.

What follows is the mechanism as reverse-engineered and packet-captured by a paying subscriber, the part of the payload that actually matters (it was your `.git`, not your source files), what Z.ai asserted versus what has been independently established, and a concrete checklist if you ever ran ZCode against a private repository.

## What ZCode was caught doing, end to end

On 2026-09-18 a paying GLM Coding Plan subscriber publishing as ferstar (J. F. Zhang) published a teardown of ZCode, Z.ai's first-party desktop coding agent for GLM. The trigger was mundane: while freeing disk space on a 256GB MacBook Air, the researcher noticed that `~/.zcode` had grown past 700MB, with `v2/checkpoints/` alone accounting for roughly 303MB.

Disassembling `app.asar` and capturing traffic produced the upload flow:

1. The client called `POST /api/v1/snapshot/upload-credential` on `zcode.z.ai`.
2. The server replied with a `snapshot_id`, an RSA **public** key, a size cap, a set of signed OSS form fields, and a callback URL.
3. The client packed the workspace into a `tar.gz`, encrypted it with AES-256-CTR, and wrapped the symmetric key with RSA-OAEP-SHA256 using the server's public key.
4. The client POSTed `tar.gz.enc` **directly to Alibaba Cloud OSS** via form POST, bypassing Z.ai's application servers entirely.
5. OSS called the Z.ai backend back to register the snapshot.

Two design details separate this from ordinary telemetry. First, the capture was unconditional: the sidecar process was instantiated at startup with no gating on user preferences, and the only precondition was a valid JWT from the token provider. Triggers were `captureBeforePrompt`, which fires before every prompt, and task completion tagged `repo-wiki-update`. Session logs showed up to 62 capture events from a single active session. Second, the encryption was envelope-style with a server-supplied public key, so the corresponding private key never touched the user's machine.

The primary teardown is at [blog.ferstar.org](https://blog.ferstar.org/en/posts/zcode-silent-workspace-snapshot-upload/). Independent framing and additional forensics appear in the [tokenstead.ai account](https://tokenstead.ai/guides/zcode-silent-git-history-upload) and the [cellcog.ai claim-graded write-up](https://cellcog.ai/blog/zcode-open-sourced-after-git-uploads/).

One correction matters here, because a widely syndicated secondary write-up got it wrong: the headline 313MB commercial-repository snapshot **failed 564 times and never left the machine**. The researcher confirmed via router connection tracking that it sat in a local pending queue. The archive that the server actually *accepted* was a separate small public-repo workspace of 538 files, roughly 15KB after compression and encryption. The mechanism is damning enough on its own; it does not need the exaggeration, and repeating the exaggeration is the fastest way to lose an argument with someone who has read the original.

## Why a 313MB archive sat on the user's disk that he could not open

Start here, not with the upload. The encrypted archive on the researcher's own disk could not be decrypted by him, or by the application that had just created it, because the decryption key lived only in Z.ai's cloud. That single property carries most of the analysis.

Everything downstream follows from it. The user could not inspect the payload before it left, verify what had left after, or independently confirm that anything was deleted later. He could delete the local pending file — and did — but a fresh 313MB archive was re-packaged within 30 minutes, with the retry counter advancing from 564 to 565. Deleting the artifact is whack-a-mole against a supervisor process that recreates it.

The mitigation that actually held was kernel-level: setting an immutable flag on `~/.zcode/v2/checkpoints` (`chattr +i` on Linux, `chflags uchg` on macOS). The trade-off is explicit and worth stating: that also disables ZCode's checkpoint rollback and timeline UI, because the same directory serves both.

## The real payload was your `.git`, not your source files

This is the section that converts a privacy story into an incident-response task. A snapshot of "your code" sounds bounded. A snapshot of the git object store is not: it is the entire lineage of the repository since its first commit.

In the archive the researcher dissected, the manifest was 42,411 files:

| Component | Size | Share of payload | Why it matters |
|---|---|---|---|
| `.git/lfs` | 196.1 MB | 56.8% | Every large binary ever fetched, including assets not currently checked out |
| `.git/objects` | 102.2 MB | 29.6% | The full content-addressed history, all branches, including rewritten commits |
| `.git/logs` (reflogs) | 0.6 MB | 0.2% | Records of checkouts, resets and rebase operations that "removed" a secret |
| Source code and docs | 46.2 MB | 13.4% | The working tree — the only part users typically imagine was shared |

The `.git` directory alone was about 86.6% of the payload. Practically, that means a workspace upload ships:

- **Credentials deleted in later commits.** A database password removed in a follow-up commit is still a blob in the object store, retrievable by anyone holding the history.
- **Unpushed branch names.** Branch names leak unreleased product plans, customer names, ticket identifiers and internal codenames, even when the branches themselves were never pushed to a remote.
- **`.git/config` contents.** Internal hostnames, remote URLs, sometimes embedded tokens in remote URLs, and local repository paths that reveal directory structure outside the repository.
- **The LFS cache.** Every binary asset ever fetched, which is why LFS was the single largest component of the archive.
- **Reflog archaeology.** The reflog tells a reader when you force-pushed, what you reset away, and roughly when.

The operational consequence is blunt: if ZCode touched a repository, the safe assumption is that **every secret that ever appeared anywhere in that repository's history has been exposed**, not merely the secrets in the current `HEAD`. Rotating only the secrets visible in your present working tree is an incomplete response.

## Which key holds the private half settles the "it was backup" defense

Envelope encryption with a server-delivered public key is a decisive technical fact, and it is the cleanest test for any future claim of this kind.

Legitimate backup and cross-device synchronization put keys in the user's hands. Git remotes authenticate as you; Time Machine keys are yours; encrypted cloud backup hands you a recovery key. In this flow, the client generated an AES-256-CTR key, wrapped it with an RSA public key that arrived from the server during credential negotiation, and shipped the wrapped key alongside the ciphertext. The private key needed to unwrap it existed only on Z.ai's side. No key anywhere on the researcher's system could open his own archive.

A system where only the vendor can decrypt your data is not a backup. It is collection with a backup's user-visible shape. And it produces a specific, unfixable epistemic problem: "we destroyed it immediately" is unverifiable from outside by construction, because nobody outside the vendor can read the data or audit its lifecycle. Reuters noted precisely this — users could not open, verify or independently confirm deletion of their own uploaded files, which is why the company's statements could not settle the matter.

## The two toggles that do not turn it off

ZCode shipped two settings that read like an off switch. Neither is one:

| Setting | Internal flag | What it actually controls |
|---|---|---|
| "Optimize Experience" | `optimizeAgentExperienceEnabled` | Authorization for using data in **model training** only |
| "Repo Snapshot Indexing" | `repoSnapshotIndexingEnabled` | Server-side indexing of snapshots that have **already been uploaded** |

Both toggles govern what happens *after* data exists on the server. Neither gates the sidecar that creates and uploads the archive, which was instantiated unconditionally at startup with no preference check. There was, in the audited build, no user-reachable setting that stopped the capture/upload path — the only precondition being a valid login token.

The generalizable rule is worth carrying to every other agent harness you evaluate: **a privacy control you cannot verify in source code or by packet capture is marketing, not a control.** Toggle labels are a claim about behavior; a network capture is evidence of behavior.

The second corroborating finding is just as sharp. A captured copy of ZCode's system prompt and tool schema — a ~131KB prompt and a 31-tool surface archived by [OrcaPromptVault](https://github.com/Continuum-AI-Corp/OrcaPromptVault) — contains no snapshot, upload or telemetry tool at all, and no mention of Aliyun, OSS, uploads or privacy anywhere in the instructions. The upload pipeline lived outside the agent's tool loop, as a host-level sidecar. That is exactly why no agent-level permission prompt, approval gate, or tool-call review could ever have surfaced it to the user: the agent never performed the upload, so the agent could never ask about it.

## What is the "Repo Wiki" explanation, and does it hold up?

Z.ai did not dispute that uploads occurred. On 2026-09-18 at 17:44 Beijing time it posted a statement in its Feishu user community attributing the traffic to "codebase indexing" for a Repo Wiki feature, saying the data was "destroyed immediately" after wiki generation, that the feature had defaulted on earlier in the product's life, and that the issue "has been fixed." It promised an open-source release, third-party review, and an extra weekly quota reset for affected users.

The sequence that followed is documented well enough to grade claim by claim:

| Date (UTC) | Event |
|---|---|
| 2026-07-01 | ZCode launches publicly on Hacker News as "ZCode – Harness for GLM-5.2" (511 points, 355 comments), positioned as a first-party Claude Code competitor for GLM |
| 2026-09-17 | Subscriber notices `~/.zcode` past 700MB |
| 2026-09-18 10:35 +0800 | Teardown published; the thread reaches 342 points and 115 comments, the post passes 1.6M impressions |
| 2026-09-18 17:44 +0800 | Feishu statement: Repo Wiki indexing, data destroyed immediately, issue fixed |
| 2026-09-20 12:01 | `github.com/zai-org/ZCode` repository created |
| 2026-09-20 21:14 | "feat: open source" commit lands — 6,973 files, roughly 1.03M lines, in a single commit; PRs locked, issues disabled |
| 2026-09-21 01:23 | ZCode account statement: remediation complete, apology, cites CAICT and NSFOCUS findings |
| 2026-09-22 | Reuters and The Register publish; Reuters reports Z.ai disabled certain features |
| 2026-09-23 | Client v3.14.3 ships; public repo gains a matching commit |

There is an internal contradiction in the explanation that the published code does not resolve in the vendor's favor. Z.ai's stated rationale was that checkpoint restore required the uploads. But in the code as published, checkpoints are local git diffs under `~/.zcode/checkpoints/` produced by the bundled git CLI — not a server-dependent mechanism. A local-only checkpoint implementation is not a reason to ship a workspace archive to object storage.

The timing of the Repo Wiki attribution is also worth noting against the capture triggers: `captureBeforePrompt` fires before *every* prompt, and session logs showed up to 62 capture events in one session. A wiki-indexing feature that runs once per repository is a poor fit for a hook that fires on every prompt.

## What I verified in the published source myself

Claims about open-source remediation deserve direct checking rather than repetition of the vendor's summary. My own read of `zai-org/ZCode` via the GitHub API and code search on 2026-09-29:

| Check | Result |
|---|---|
| Repository history | 3 commits total — "Initial commit" (2026-09-20), "feat: open source" (2026-09-20), "feat: update v3.14.3" (2026-09-23). One tag: v3.14.3. License Apache-2.0. |
| Collaboration surface | `has_issues=false`, `has_wiki=false`, `has_discussions=false` — issues disabled, PRs locked |
| Traction | 7,163 stars, 2,171 forks, 44 watchers |
| `repoSnapshot` in code | 0 hits |
| `snapshot/upload` in code | 0 hits |
| `aliyuncs` in code | 0 hits (the single match elsewhere is a model-API base URL config, unrelated to OSS) |
| Sanity control | `gitCheckpointService` = 9 hits, `ripgrep` = 31 hits — the search does find real strings, so the zeros are meaningful |

So the vendor's claim that the automatic repo-snapshot pipeline is absent from the published source is consistent with the code as published. Two refinements matter for anyone who wants to reason precisely:

**Absence of the caller is not removal of the capability.** The published client still ships a real OSS form-POST upload path in `packages/services/src/feedback/feedbackHttpClient.ts`, implementing `/feedback/attachment/upload-credential`, `buildOssFormFields()` and `uploadOssForm()` — used for user-initiated feedback attachments with a ticket ID and a size cap. That is a distinct, user-triggered feature and not the sidecar, but it means the OSS form-upload plumbing itself was never removed, only the automatic workspace caller. There are also residual `upload-credential` tokens, one of them (`networkTelemetryAggregator.ts`) a bare string inside a network-error classifier vocabulary — a classifier, not an upload path.

**Matching version tags do not make a binary reproducible.** The repo's only tag is v3.14.3, matching the 2026-09-23 commit message and the shipped client. But as ferstar notes, a matching version tag does not prove a proprietary compiled binary is byte-identical to public source. A Hacker News item on 2026-09-25 explicitly raises this divergence question. Treat "the public source is what shipped" as unproven.

The open-source release is genuinely inspectable, and the inspection supports the remediation claims. It is not, however, auditability of the change: with two commits at release and a flattened dump, nobody can diff how the pipeline was excised, review the original implementation, or see what else traveled on the same code path. Open-sourcing after an incident is damage control that happens to be verifiable. It is not a security property, and it should not be scored as one.

## If you ran ZCode against a private repo, do this

This is the durable part, and it does not expire with the news cycle.

**1. Rotate every secret that ever appeared anywhere in the repository's history.** Not the secrets in your current tree — every one that has ever been committed. Use `git log -p` plus `git rev-list --all --objects` and a secret scanner over full history, not just `HEAD`. Include database passwords, API keys, cloud credentials, JWT signing keys, CI tokens, and webhook secrets. Deleting a commit is not deletion.

**2. Lock the checkpoint directory if the client is still installed.** `chattr +i ~/.zcode/v2/checkpoints` on Linux or `chflags uchg` on macOS. Accept the cost: checkpoint rollback and timeline features stop working. Deleting archives manually does not work; a fresh archive reappeared within 30 minutes in the observed case.

**3. Keep secrets out of versioned paths entirely.** Use [sops](https://github.com/getsops/sops) or a secrets manager CLI (1Password CLI, Vault) so live credentials are injected at runtime rather than stored in the repository. If a secret is never in the working tree, it cannot enter the object store.

**4. Sandbox or containerize any proprietary harness on repositories you do not own outright.** Give it a working directory that contains only what the task needs, e.g. `git clone --depth 1` into a scratch path or `git worktree`, with no access to your full history. A short clone is not just a speed trick; it is a blast-radius limit.

**5. Separate "I want GLM" from "I will run Z.ai's closed harness."** The open weights remain available through harnesses you control or can inspect. This is the entire content of the open-weights argument, and it only pays off if you exercise it.

**6. Establish a client-code boundary policy before adopting any agent harness.** For repositories containing third-party or customer code, the simplest hard boundary is keeping the agent signed out, or off the machine, when source cannot leave your network.

That last point connects to the most underweighted dimension of this incident. Reuters reported a corporate complaint from Chengming Technology that six company coding workspaces had been uploaded without consent, including complete source code, database passwords and employees' personal information. That claim was later reported as retracted on the basis of "wrong evidence," and it should be presented as a reported-and-retracted claim rather than as established fact. The structural risk it describes is real regardless of the retraction: a developer installing an agent harness transfers third-party customer code and colleague PII across a border and into a bucket the company does not control, with no data-processing agreement, no disclosure, and no opt-out. If you run engineering for a company that handles client code, that is a policy gap you own.

## The line this crosses: inference context versus whole-repo capture

There is a real and reasonable defense of AI coding tools in general: to answer a question about code, a model must see code, and sending relevant context to inference is inherent to the product category. Every tool in this space does it, including the open-weight ones.

That defense does not apply here, and the distinction is worth keeping clean:

| | Inference-context transmission | ZCode workspace snapshotting (3.12.3) |
|---|---|---|
| Scope | Files the agent reads to answer the current request | Entire workspace, `.git` included, regardless of relevance |
| Timing | During the request | At startup and before every prompt, up to 62 events per session |
| Consent | Implicit in using the assistant on a file | None — no prompt, no disclosure, no effective toggle |
| Visibility | Usually represented by a policy describing submitted code | Policy mentioned only "text, files, and code submitted during conversations" |
| Decryptability | Server-side processing (ordinary) | Encrypted with a vendor-only key, unreadable by the user |
| Retention claim | Vendor policy | "Destroyed immediately" — unverifiable from outside |

Consenting to send code to a model to get an answer is not consent to ship the repository, its history, and its LFS cache to an object storage bucket. The privacy policy in force covered the first and never described the second — no mention of whole-workspace snapshots, the git object database, reflogs, or repeated background uploads tied to login state, in the policy, the FAQ or the changelog.

## Open weights are not an open harness

The sharpest way to read this incident is against the sales narrative. Z.ai launched ZCode in July 2026 explicitly as a first-party harness for GLM, weeks after the Claude Code hidden-telemetry controversy had made closed-harness trust the live issue in the developer community. Open weights were the argument: no kill switch, no vendor able to degrade your model, no black box between you and your inference. An executive publicly answered on X that the company would not implement anything beyond what was listed on the ZCode website.

Workspace snapshotting was never listed on the ZCode website. The harness is where the trust boundary actually lives — weights you can download tell you nothing about a client you cannot read, and the client is what has filesystem access, a login token, and network reach. "Do not trust closed-source AI harnesses," as security commentator Petri Kuittinen put it, is not a slogan about licensing philosophy; it is a statement about which component can silently act on your disk.

Z.ai's January 2026 listing on the Hong Kong Stock Exchange explains the intensity of the reputational response, but not the technical severity. The technical severity is moderate: one small public-repo workspace was confirmed accepted by a bucket that has since been emptied and deleted, plus an upload pipeline that most clearly demonstrates the *capability*, not a mass-scale leak. The trust cost is high because the gap between what was sold (open weights as the escape from vendor-controlled tooling) and what shipped (an undocumented, non-optional, vendor-keyed upload path) is exactly the gap the sales pitch promised to close.

## Verdict: what is confirmed, what is company claim, what is unproven

Graded honestly, because the difference between these three columns is the difference between a fact and a press release:

| Claim | Grade |
|---|---|
| ZCode uploaded users' workspace data | Confirmed — by Z.ai's own statements, and by Reuters reporting that Z.ai disabled features after the issue |
| The `.git` object store, LFS cache and reflogs were in the payload | Confirmed — local plaintext manifest from the researcher's own machine |
| The upload used a server-supplied public key with a private key only Z.ai held | Confirmed — reverse-engineering and packet capture, independently consistent with Reuters' account of why users could not open their own files |
| "It was the Repo Wiki codebase-indexing feature" | Company account, and a poor fit for a sidecar that fired before every prompt |
| "Data was destroyed immediately" | Unverifiable from outside, by construction |
| "The 313MB commercial repository was uploaded" | **Wrong** — 564 failed attempts, never left the machine. Correcting this strengthens the case |
| "Fully open source" | Code is public and the pipeline is absent from it; history is a flattened dump with issues disabled, and binary-versus-source equivalence is unproven |
| "The code was never used to train GLM" | Company denial, no external check available |
| The bucket was emptied and all objects deleted | Third-party audit findings, cited by Z.ai: CAICT found the bucket in a zero-data state; NSFOCUS found the bucket and all objects deleted with no remaining path transmitting local files |

What the audits cannot do is as important as what they show. A bucket audit performed on 2026-09-20 cannot reconstruct the lifecycle of data uploaded before 2026-09-18, cannot answer who held the RSA private key or for how long, and cannot test a "destroyed immediately" claim that was made two days before the audit. Both full CAICT and NSFOCUS reports were still unpublished as of the September 21 statement, which leaves the primary evidence for the remediation as an assertion relayed by the vendor.

Threads worth following if you care how this resolves: publication of the full audit reports, a reproducible build so the shipped binary can be compared against the published source, and any third-party review of the current client.

The durable lesson fits in a sentence. The vulnerability was not that a model saw your code. It was that a client you could not read, running with your credentials, had permission to decide what left your machine — and that no toggle, policy or agent-level approval could have shown it to you.

## FAQ

**Did ZCode actually upload my code?**

ZCode versions up to and including 3.12.3 packaged the whole workspace of any logged-in user, encrypted it with a server-supplied RSA public key, and uploaded it to Alibaba Cloud OSS. Z.ai has not disputed that uploads occurred — it attributed them to a "Repo Wiki" codebase-indexing feature. In the specific workspace the researcher dissected, the large 313MB commercial-repo archive failed 564 times and never left the machine; a separate small public-repo workspace of 538 files was accepted by the server.

**Is ZCode open source now, and does that fix it?**

The source is public under Apache-2.0, but the release is a flattened dump: 6,973 files in a single "feat: open source" commit on 2026-09-20, with the repository's prior development history absent, pull requests locked, and issues disabled. My own code search on 2026-09-29 confirmed zero hits for `repoSnapshot`, `snapshot/upload` and `aliyuncs`, which supports the claim that the automatic pipeline was removed. It does not prove the shipped binary matches the public source.

**Which settings in ZCode disable the upload?**

In the audited build, none. "Optimize Experience" (`optimizeAgentExperienceEnabled`) governs model-training authorization only, and "Repo Snapshot Indexing" (`repoSnapshotIndexingEnabled`) governs server-side indexing of snapshots already uploaded. The snapshot sidecar was instantiated at startup with no preference gating and needed only a valid login token, so there was no user-reachable switch that stopped the capture and upload path. Remediation came in the client updates, not as a toggle.

**If I ran ZCode on a private repository, what should I do first?**

Rotate every secret that ever appeared anywhere in that repository's history, not only the ones in your current working tree — roughly 86.6% of the uploaded payload was the `.git` directory, which contains deleted-in-a-later-commit credentials, unpushed branch names, reflogs and the LFS cache. Then lock `~/.zcode/v2/checkpoints` with `chattr +i` (Linux) or `chflags uchg` (macOS) if the client is still installed, accepting that checkpoint rollback stops working.

**Why does the encryption key matter so much?**

Because it determines whether the vendor's statements are checkable. Each snapshot was encrypted with a locally generated AES-256-CTR key that was then wrapped with an RSA public key delivered by Z.ai's server; the matching private key never touched the user's machine. The user therefore could not read his own uploaded archive, could not verify what it contained, and cannot independently confirm that it was deleted. A system only the vendor can decrypt is collection rather than backup — and it makes "we deleted it" unfalsifiable from the outside.

## Related reading

- [Self-hosted AI coding: open weights versus managed harnesses](/posts/self-hosted-ai-coding-comparison-2026/)
- [Building a composable AI coding stack: Cursor, Claude Code, Codex](/posts/composable-ai-coding-stack-cursor-claude-codex-2026/)
- [Agent skills supply chain security](/posts/agent-skills-supply-chain-security-guide-2026/)
- [Securing AI agents with least privilege](/posts/secure-ai-agents-least-privilege-2026/)

Sources: [ferstar teardown](https://blog.ferstar.org/en/posts/zcode-silent-workspace-snapshot-upload/) (primary reverse engineering and packet capture), [tokenstead.ai](https://tokenstead.ai/guides/zcode-silent-git-history-upload), [cellcog.ai](https://cellcog.ai/blog/zcode-open-sourced-after-git-uploads/), [Reuters](https://www.reuters.com/legal/litigation/chinas-zai-disables-ai-coding-assistant-features-after-security-issue-2026-09-21/), [The Register](https://www.theregister.com/security/2026/09/22/zai-says-sorry-for-slurping-up-your-code-open-sources-zcode/5298300/), [runtimewire](https://runtimewire.com/article/zai-zcode-uploads-git-history-without-opt-out), [zai-org/ZCode on GitHub](https://github.com/zai-org/ZCode), [OrcaPromptVault](https://github.com/Continuum-AI-Corp/OrcaPromptVault).
