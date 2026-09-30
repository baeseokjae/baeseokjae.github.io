---
title: "Palomar Registry: Lean Verified Mathematics, Explained (2026 Guide)"
date: 2026-09-30T18:13:32+00:00
tags:
  - palomar lean mathematics
  - lean verified mathematics registry
  - lean 4 proof verification
  - machine-checked mathematics
  - AI generated proofs verification
description: "Palomar is a registry of Lean 4 formalizations whose proofs pass a two-kernel machine check. Here is what it certifies, what it does not, and how to file."
draft: false
cover:
  image: "/images/palomar-lean-verified-mathematics.png"
  alt: "Palomar Registry: Lean Verified Mathematics, Explained (2026 Guide)"
  relative: false
schema: "schema-palomar-lean-verified-mathematics"
---

Palomar is a public, searchable registry of Lean 4 formalizations whose proofs have been machine-checked and whose statement was reviewed for fidelity to the informal claim. It is jointly incubated by the Lean Focused Research Organization (Lean FRO) and ICARM, announced publicly by Terence Tao on 18 August 2026, and it deliberately performs no human peer review.

That last clause is the part most coverage gets wrong, so it is worth stating before anything else: a Palomar entry certifies that a proof typechecks under two independent kernels, that no forbidden axiom was smuggled in, and that an automated reviewer found the Lean statement faithful to the stated informal one. It certifies nothing about whether the result is novel, interesting, or important.

## What Is the Palomar Registry, and What Is It Explicitly Not?

Palomar is an append-only index of Lean formalizations that have cleared automated verification, each pointing at an immutable commit of a public repository. The name is a reference to the Palomar Observatory sky survey: a catalogue you consult, not a referee you argue with.

The registry's own manifesto states the motivation in unusually blunt terms. Since the start of 2026 the volume and complexity of machine-assisted proofs has risen substantially, and bold claims about machine-assisted resolution of famous problems have been announced with poor vetting, insufficient transparency, and inadequate context — eroding what counts as an established mathematical fact. Palomar is the response to that erosion.

What it is not requires its own list:

- **Not a peer-reviewed journal.** The registry states plainly that it "adds no human editorial step: no one here reads the mathematics the way a referee would."
- **Not a preprint server.** Its role in the publishing pipeline is analogous to a repository or arXiv, but an arXiv posting carries no verification claim at all, and a Palomar entry carries a specific, narrow, machine-checked one.
- **Not a proof assistant.** Palomar verifies Lean only. It does not replace Lean, Mathlib, or your own CI, and it is not run by any of them.
- **Not a novelty certificate.** Registration certifies neither novelty, nor relevance, nor complete agreement between the formal and informal statement.

The useful mental model is a lighthouse rather than a courthouse. It tells you the rocks it can see. It does not tell you whether the ship is worth building.

## Who Runs Palomar: Lean FRO, ICARM and the Scientific Board

Palomar is jointly incubated by two organisations with different mandates. The Lean FRO is the engineering body behind Lean 4, Mathlib's tooling, and the Verso documentation system. ICARM, the Institute for Computer-Aided Reasoning in Mathematics, is the research-side institute; its directors Jeremy Avigad and Matthew Ballard are both on the board.

The initial scientific advisory board has nine members: Jeremy Avigad, Matthew Ballard, Jaume de Dios, Nestor Guillen, Bryna Kra, Kim Morrison, Terence Tao, Ravi Vakil and Akshay Venkatesh. Tao is not merely a signatory — he is one of four initial technical maintainers, alongside Matthew Ballard, Nestor Guillen and Jaume de Dios Pont.

That maintainer list matters for a practical reason. The registry's engineering is maintained by people who also work on the Lean ecosystem itself, which is why Palomar's requirements line up exactly with existing Mathlib Initiative standards rather than inventing a parallel format. The `formalization.yaml` standard it requires was developed by the Mathlib Initiative; the Comparator tool it runs is the Lean FRO's; the HTML rendering of main theorems is automatic via Verso.

There is an institutional tell in the ICARM announcement too. The stated strategic rationale is to keep mathematics central, independently auditable and publicly accessible — a formulation that reads less like a product pitch and more like a statement of what the incubators were afraid of losing.

## The Three Automated Checks Behind Every Entry

Every registration passes three checks. Understanding which check does what is the whole game, because each one has a different failure mode and a different blind spot.

### Check 1 — Mechanical: Comparator, Lean's Kernel and NanoDa

This is the load-bearing check. Palomar uses the Lean FRO's Comparator tool to replay every exported proof, and it verifies through two kernels rather than one: Lean's own kernel and NanoDa, an independently implemented kernel.

Two kernels is the answer to the obvious objection that a single buggy checker could accept a false proof. The two implementations share no code lineage, so a soundness bug in one is unlikely to be reproduced by the other. The registry publishes the exact commit of each checker alongside the entry, so a reader who distrusts either one can inspect precisely what ran.

The mechanical gate also enforces the axiom policy. A proof can typecheck perfectly and still be worthless if it reaches for extra assumptions, so Comparator and the review pipeline reject four specific escape hatches:

- `sorryAx` — a proof that is admitted without proof.
- `Lean.ofReduceBool` — a trusted-implementation escape in the kernel.
- Any custom axiom defined by the submitter.
- Any unnamed missing definition.

The permitted set is exactly Lean's three standard axioms: `propext`, `Classical.choice` and `Quot.sound`. Those three are accepted because essentially all of ordinary mathematics already depends on them; anything beyond them is treated as a smuggled assumption rather than a foundation. This is why the registry's own framing describes the checks as covering three questions: that the proof typechecks, that there are no "cheats" such as extra axioms, and that the formal statement matches the informal claim.

### Check 2 — Non-mechanical: The LLM Statement-Fidelity Review

This check exists because the mechanical gate cannot do it.

A kernel can verify that a Lean term has the type you declared. It cannot verify that the type you declared says what you told the world your theorem says. If you formalize a weak, trivially true statement and label it with a famous conjecture's name, every kernel in the world will happily accept it. That gap — between the formal statement and the informal claim people are actually talking about — is the honest limit of the entire system, and Palomar hands it to a language model by design.

The review is described as LLM judgement of whether the informal and formal statements match. It is not a proof check; if the translation is faithful, there is no proof to check a second time. The Hacker News thread raised this as a "recursive verification" worry — who verifies the verifier? — and the answer that emerged in discussion is the correct one: you check translation fidelity, not the proof again.

The published review is **redacted**. It records that no blocking problem was identified and carries every comment, but it withholds the numeric scores. The registry explains why: the same commit scored 5 and then 4 on one axis across two runs of the same policy. Rather than publish a number it cannot stand behind, Palomar dropped the number. That is an unusually honest piece of systems design, and it is the single best indicator of how the maintainers think about automated judgement.

### Check 3 — Disclosure: formalization.yaml

The third check is not a verification at all. It is a disclosure regime, and it is the reason Palomar can stay neutral about AI.

Every entry requires a `formalization.yaml` file conforming to the Mathlib Initiative standard, with fields for recording collaboration, AI use (which models, and budgets), and adherence to social standards around licensing, referencing and attribution. The maintainer-side launch post states the policy directly: Palomar has no opinions about use of AI — entries range from fully hand-written to autonomously formalized — but the method must be disclosed.

That single design choice defuses the argument that has consumed most of the AI-mathematics conversation. Palomar does not need to adjudicate whether an AI wrote the proof, because the registry's claim never depended on the provenance. The disclosure fields make provenance a matter of record rather than a matter of trust.

The editorial review adds one more gate that nobody expected from an automated registry: a research-interest floor. A language model must answer yes to two questions before a result is registrable — could this warrant a research paper or serious note, and can a credible research area and a plausible researcher type be identified. It is mild gatekeeping, but it is gatekeeping, and it exists to keep the registry from filling with formally correct trivia.

## The Repository Layout Palomar Requires

The submission contract is strict in a way that surprises people who expect a portal with a form. Palomar does not accept a link to your paper or your repository in general. It accepts a specific project layout at a specific commit.

### Challenge, Solution and comparator.json

The required project files are:

```
lakefile.toml            # or lakefile.lean
lake-manifest.json       # must be committed
lean-toolchain
Challenge.lean           # readable statement module
Solution.lean            # proved solution module
comparator.json          # comparator configuration
formalization.yaml       # disclosure metadata
```

The `Challenge` module must be readable — it is where the formal statement lives, and it is what a reader is meant to be able to audit without wading through a proof. The `Solution` module is where the proof lives. That separation is structural, not stylistic: it is what lets the registry show a human the claim and let a machine handle the proof.

An official starter repository, `PalomarRegistry/PalomarTemplate`, provides the layout, pinned dependencies, documentation generation and CI checks. The registry also points at a complete worked example repository so you can see the shape of a finished submission rather than inferring it.

### Sizing Rules, Import Rules and the Allowed-Axiom Set

Four constraints cause most of the friction in real submissions.

**Sizing.** The Challenge source has a hard maximum of 1,000 lines and 100 KiB, with a warning threshold at 300 lines and 32 KiB — the registry would rather review 300 lines than 1,000. The checked-out repository itself is capped at 500 MiB. The soft limits are the practical target; if your statement needs more than 300 lines, the registry's implicit advice is that you have probably folded the proof into the statement.

**Imports.** The Challenge module's transitive imports must resolve to Lean core plus the pinned, allowlisted Mathlib or Tau Ceti closure, and to nothing else. Dependencies used only by the Solution may be arbitrary pinned Git dependencies. The logic is that the reader-facing statement must not depend on code the reader cannot see, while the proof may lean on whatever helps.

**No back-imports.** A project Palomar has already registered is **not** importable as a library on the basis of its registration, because each entry fixes a reviewable snapshot of its own statement. Registration is a citation, not an API.

**Immutability.** Submissions are pinned to a full 40-character Git commit SHA from a public GitHub repository. Palomar checks that immutable snapshot, not a branch or a tag that can move underneath it. A short SHA is not accepted.

The allowed-axiom set is `propext`, `Classical.choice` and `Quot.sound`, as described above. Assumptions must be stated as explicit hypotheses in the Challenge statement rather than smuggled in as axioms — which is the correct discipline in any case, since an explicit hypothesis is visible to the reader and a custom axiom is not.

## How to Submit to the Palomar Registry, Step by Step

The flow is short, and every step is a place where a real submission has failed.

1. **Build the project locally and prove it clean.** Run `lake build` and confirm the Challenge imports resolve only to core plus Mathlib or Tau Ceti. Confirm the Solution proves exactly the Challenge statement, with no weakening.
2. **Verify the axiom surface yourself.** Before filing, run `#print axioms` on the main theorem. Every axiom that appears must be one of `propext`, `Classical.choice` or `Quot.sound`. If you see anything else, the mechanical gate will find it too, and you will have spent a cycle for nothing.
3. **Write `formalization.yaml`.** Use the exact basename. A wrong filename is a filing error, and filing errors cost full submission cycles.
4. **Commit and take the full SHA.** `git rev-parse HEAD` and copy all 40 characters. Do not use a tag or a branch name.
5. **Push to a public GitHub repository.** GitHub is currently the only supported forge.
6. **Submit through the interactive site.** The submission UI publishes its own `llms.txt`, which means agent-assisted submission is a supported path. Tao's own guidance is that modern AI agents are quite helpful with the mechanical details while human review before filing remains strongly recommended.
7. **Wait for the automated pipeline.** Mechanical verification, the statement-fidelity review and the editorial review run in sequence.
8. **If registered, expect permanence.** The record, the review, and the repository and commit enter Palomar's append-only canonical history.

Two properties of that last step deserve separate emphasis, because people consistently underestimate them.

**Registration is effectively non-withdrawable.** Withdrawal is not available once registered. The only paths are publishing a new version, a lawful-request process, or an exceptional retraction by a named Moderator of one exact version with a public tombstone. Version URLs must stay resolvable forever.

**There is no appeal for an individual result, by design.** The registry's rationale is that reopening a few outcomes for whoever writes in would make the outcome depend on who complained. That is a defensible principle and a genuinely harsh user experience, and both things are true at once.

Palomar does keep a public preservation fork of every registered source, stored under the `PalomarArchive` GitHub organisation with a commit-hash-suffixed name. The fork's purpose is narrow and honest: it is a registry backup so that the entry remains inspectable if the original repository disappears. It is not a mirroring service and it is not a claim of ownership.

## What the Registry Looks Like at Scale Today

Around six weeks after launch, Palomar is no longer a thought experiment. As of 30 September 2026, the registry's machine-readable API reports 383 registered results across 304 source projects, while the home-page counters read 346 registered results and 270 source projects. The gap is not an error: the API counts every active version of every result, while the front page counts newest-only. Anyone comparing the two numbers should know which one they are reading.

Growth is faster than a casual reader would expect from an academic initiative. The newest 200 entries alone span 6 September to 30 September 2026 — about 25 days — which implies a run rate on the order of eight registrations per day.

The recent-entry data is more interesting than the totals:

| Metric | Recent 200 entries |
|---|---|
| Trust level | 199 "high", 1 "qualified" |
| Status | 200 "registered" |
| Version 1 | 183 entries |
| Version 2 | 13 entries |
| Version 3 | 3 entries |
| Version 4 | 1 entry |
| Distinct authors | 145 |
| Most prolific author | Arthur Freitas Ramos (18 entries) |

Two things stand out. First, trust levels are overwhelmingly "high" — the "qualified" tier is rare enough to be a rounding error in this window, which suggests the mechanical gate is doing its filtering upstream. Second, corrections are uncommon: 183 of 200 entries are still at version 1, so the append-only design is not being churned by constant republication.

Subject concentration follows the shape of the formalization community rather than the shape of mathematics as a whole:

| arXiv category | Entries in recent 200 |
|---|---|
| math.NT (number theory) | 55 |
| math.CO (combinatorics) | 55 |
| math.LO (logic) | 25 |
| math.PR (probability) | 24 |
| math.DS (dynamical systems) | 17 |
| math.MG (metric geometry) | 14 |
| math.CA (classical analysis) | 11 |
| math.FA (functional analysis) | 11 |
| math.GR (group theory) | 10 |

Number theory and combinatorics lead by a wide margin, which is exactly where recent machine-assisted results have clustered and where Mathlib's coverage is deepest.

### Cost accounting at a level academic infrastructure rarely publishes

Palomar publishes its operating costs, which is unusual enough to be a story in itself. The current aggregate run rate is **$7,608.20 per year**, or $634.02 per month, broken down as follows:

| Cost centre | Annual |
|---|---|
| OpenAI (review pipeline) | $6,008.76 |
| GitHub Actions | $1,516.44 |
| Cloudflare Workers Paid | $60.00 |
| Domains | $23.00 |
| **Total** | **$7,608.20** |

The LLM review is by a wide margin the dominant cost, which is the price of the statement-fidelity check. More notable: the published forecast annualises the observed rate to 10,342 submissions, 6,388 completed reviews and 3,248 registrations per year — meaning roughly half of completed reviews end in registration, and the other half are refused.

Palomar also publishes an independent billing reconciliation. Retained conversation logs reprice to $911.61 against $926.80 of OpenAI billed model cost over the same complete-day window, a coverage of 98.4%. The registry states that it refuses to publish a refreshed estimate below 90% coverage. For anyone who has tried to audit an AI-mediated pipeline, this is the most interesting artifact on the site: an infrastructure operator publicly grading its own accounting and setting a floor below which it will not report.

## What a Palomar Entry Does Not Certify

This is the section to read if you are about to cite a Palomar entry.

When you write "this is on Palomar", you are entitled to claim exactly four things:

1. The proof typechecks under Lean's kernel and the independent NanoDa kernel, at the published commits.
2. No disallowed axiom appears in the dependency trace — no `sorryAx`, no `Lean.ofReduceBool`, no custom axiom, no unnamed missing definition.
3. An automated reviewer found the formal statement faithful to the stated informal claim, and recorded no blocking problem.
4. The artifact is pinned to an immutable public commit, preserved in a registry fork.

You are **not** entitled to claim:

- **Novelty.** The registry is explicit that it certifies neither novelty nor relevance. A well-known theorem formalized cleanly is a perfectly valid entry.
- **Correctness of the informal claim as stated in prose.** The fidelity check is automated and fallible. It is a screen, not a proof.
- **Human endorsement.** No referee read the mathematics. The scientific advisory board lends governance, not per-entry review.
- **Error-freedom of the surrounding project.** Palomar verifies the Challenge and Solution modules under the stated import restrictions. It does not audit your repository.
- **Anything about other proof assistants.** Palomar currently verifies Lean only.

The registry is also explicit that its checks fall well short of human peer review. That admission comes from the people who built it, which is why the honest framing is "machine-checked and statement-screened" rather than "verified mathematics" in the colloquial sense of the phrase.

## Practical Failure Modes and Lessons From Real Submissions

The theory is clean; the practice is where people lose days. Practitioner write-ups have documented failure modes that are worth internalising before you file.

**A correct proof can still be refused.** One documented submission cleared the mechanical gate clean — proof typechecked, axioms clean — and was then refused by the editorial review. Refusals are private, and there is no appeal. The refusal reasons were not published, which is by design rather than an oversight, but it means a submitter can spend a cycle and learn nothing specific from the outcome.

**A filing error can cost a full cycle.** The same practitioner account documents an expensive filing mistake that consumed roughly 4 hours and 45 minutes of queue and verification time despite mathematically correct content. The registry's pipeline is not cheap to re-run, and a bad filename or a stray import burns the whole run.

**The import surface is the most common structural mistake.** If your Challenge module transitively reaches anything outside Lean core plus the pinned Mathlib or Tau Ceti closure, the submission fails mechanically. Solution-only dependencies may be arbitrary pinned Git dependencies, so the fix is usually to move the heavy imports into the Solution — but the Challenge must stand alone against the allowlisted closure.

**The `formalization.yaml` basename is exact.** This is a small, irritating, entirely avoidable failure, and it is documented repeatedly by people who hit it.

**GitHub-only is a real constraint.** The main objection cluster in the Hacker News discussion — 186 points and 39 comments — was the hard dependency on GitHub: availability, single point of failure, and no support for other forges. The mitigation is real but partial. Palomar uses GitHub as a costless immutable datastore and forks every registered source into the preservation archive, so a deleted upstream repository does not erase the entry. It does not fix the fact that you must have a public GitHub repository to register in the first place.

## Palomar vs the Rest of the Formal-Mathematics Stack

Palomar is often described imprecisely in comparison pieces, so it is worth being exact about what sits next to what.

| System | What it is | What Palomar adds or lacks relative to it |
|---|---|---|
| **arXiv** | Preprint server, no verification claim | Palomar claims machine-checking and statement review; arXiv claims nothing |
| **Mathlib** | The Lean 4 mathematics library | Palomar verifies against Mathlib; Mathlib does not index proofs of standalone results |
| **Tau Ceti** | Mathlib-adjacent allowlisted project | Palomar accepts its closure as an allowed import for the Challenge |
| **CSLib** | Computer-science-oriented Lean library | Complementary; Palomar is the registry layer, CSLib is content |
| **Hex** | Lean formalization project infrastructure | Complementary tooling ecosystem |
| **Reservoir** | Lean package index | Reservoir catalogues packages; Palomar catalogues verified statements |
| **theoremdb.org** | Theorem database | Lacks the Comparator and `formalization.yaml` gate; a listing, not a verification |
| **Metamath's metamath.org** | Centralised verified set, different assistant | Same family of idea, different proof assistant and a single canonical set |

The honest summary of the comparison table is that Palomar is not competing with any of these. It is the only layer in the stack whose job is to make a verified statement citable at a fixed commit with a public record of what was and was not checked.

### Where the registry may go next

Palomar currently verifies Lean only, but the project is explicit that expansion to other proof assistants is open and it publishes the requirements any expansion would have to meet: an existing verification pipeline, a statement/solution separation, HTML rendering, dependency display, a security review, a CI cost assessment, and a working sample of 10 to 100 projects. That is a demanding bar, and publishing it is a way of saying the door is open without pretending the work is small.

One detail in the design suggests the maintainers expect a long horizon: entry IDs and version URLs are meant to stay resolvable permanently. The example entry `PALOMAR-2026-08-13-000001` is Tao's own test submission — his formalization of the proof of Sendov's conjecture — and it is a deliberate reference implementation as much as a registration.

## Should You Submit? The Honest Incentive Question

The most-repeated question in the community discussion was simple: what is the incentive to file at all?

The answer given in-thread is the arXiv analogy, and it holds up. Nobody is compelled to post to arXiv either. Researchers do it because a stable, citable artifact beats an announcement on a social platform. Palomar's version of that argument is sharper, because the artifact it produces is machine-checkable: a link to a Palomar entry conveys a specific verification claim that a link to a blog post, a repository, or a thread does not.

The maintainers' own social-media catchphrase — "But is it on Palomar?" — has become a de facto trust marker for AI-era mathematics claims, and that is the incentive in its most compressed form. In a year when machine-assisted proofs of famous problems are being announced at a rate nobody can vet by hand, having a registry entry is the difference between a claim and a checkable claim.

The counter-arguments are real and should be weighed honestly:

- **Permanence is a commitment.** Non-withdrawable registration means a mistaken statement is on the record forever, in an append-only history you cannot appeal.
- **Cost is asymmetric.** Filing costs you a build, a disclosure file, and a verification cycle that can run hours. Registration costs Palomar about $1.90 per completed review at current rates — trivial for them, not trivial for you.
- **Refusals are opaque.** A clean mechanical pass can still be refused with no public reason and no appeal path.
- **The claim is narrower than the headline.** If you need novelty or human endorsement, Palomar is the wrong instrument.

The reasonable position for most people is the one the registry itself implies. If you have a Lean formalization that stands alone against the allowlisted closure, that typechecks with clean axioms, and that you are willing to have pinned permanently — file it. It costs a few hours and produces the only kind of mathematics artifact in 2026 that a reader can re-verify without trusting anyone's prose, including yours.

## FAQ

**What is the Palomar registry in one sentence?**

Palomar is a public, append-only registry of Lean 4 formalizations whose proofs have been machine-checked through Lean's kernel and the independent NanoDa kernel, with an automated review of whether the formal statement matches the informal claim. It is incubated by the Lean FRO and ICARM and performs no human peer review.

**Does a Palomar entry mean the mathematics has been peer reviewed?**

No. The registry states that it adds no human editorial step and that no one there reads the mathematics the way a referee would. A Palomar entry certifies machine-checking, a clean axiom surface, and an automated statement-fidelity screen. It certifies neither novelty, nor relevance, nor human endorsement.

**How do I submit to the Palomar registry?**

Push a public GitHub repository containing `lakefile.toml`, a committed `lake-manifest.json`, `lean-toolchain`, a readable `Challenge.lean`, a proved `Solution.lean`, `comparator.json` and `formalization.yaml`. Verify locally with `lake build` and `#print axioms`, take the full 40-character commit SHA, and submit that immutable snapshot through the interactive site. Registration is permanent once accepted.

**Which axioms does Palomar allow?**

Only Lean's three standard axioms: `propext`, `Classical.choice` and `Quot.sound`. It rejects `sorryAx`, `Lean.ofReduceBool`, any custom axiom, and any unnamed missing definition. Anything beyond the three standard axioms must be stated as an explicit hypothesis in the Challenge statement rather than added as an axiom.

**Why are Palomar's review scores withheld?**

Because the same commit scored 5 and then 4 on one axis across two runs of the same review policy. Rather than publish a number it cannot reproduce, Palomar publishes the review with every comment included, records whether a blocking problem was found, and withholds the scores. It is a deliberate refusal to attach false precision to an automated judgement.

## Sources and Further Reading

- Terence Tao, "Palomar: A Registry of Lean Verified Mathematics", 18 August 2026 — https://terrytao.wordpress.com/2026/08/18/palomar-a-registry-of-lean-verified-mathematics/
- Palomar statement and manifesto — https://palomar-registry.org/statement
- Palomar about and verification model — https://palomar-registry.org/about
- Palomar submission requirements — https://palomar-registry.org/how-to-submit
- Palomar cost and workload accounting — https://palomar-registry.org/costs
- ICARM institutional announcement, 21 August 2026 — https://icarm.io/news/announcing-palomar-a-registry-of-lean-verified-mathematics/
- Kim Morrison, launch post — https://kim-em.github.io/blog/2026-8-19-announcing-the-palomar-registry/
- Hacker News discussion (186 points, 39 comments) — https://news.ycombinator.com/item?id=49355968
- Registry data API — https://data.palomar-registry.org/api/v1/results
- Entry PALOMAR-2026-08-13-000001 (Sendov's conjecture) — https://palomar-registry.org/entry?id=PALOMAR-2026-08-13-000001&version=1
