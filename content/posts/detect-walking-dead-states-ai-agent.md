---
title: "Walking Dead State Detection: How AI Agents Find Unwinnable Game States (2026)"
date: 2026-10-01T00:14:10+00:00
tags:
  - walking dead state detection
  - softlock detection
  - unwinnable game state
  - reachability analysis
  - SCC game state graph
  - LLM playtesting agent
description: "Walking dead state detection proves when a game keeps accepting input but victory is already impossible. How static analysis and AI agents find those states."
draft: false
cover:
  image: "/images/detect-walking-dead-states-ai-agent.png"
  alt: "Walking Dead State Detection: How AI Agents Find Unwinnable Game States (2026)"
  relative: false
schema: "schema-detect-walking-dead-states-ai-agent"
---

Walking dead state detection is the practice of proving that a game can reach a state where it still accepts input, still renders, still answers every command — and victory has already become impossible. The player does not know it. The game does not crash. Detection means finding those states from the game's own logic, or from an agent that explores its way into them.

## What Is a Walking-Dead State, Exactly?

The term is design criticism, not engineering vocabulary, and it starts with the player rather than the code. Jimmy Maher's *The 14 Deadly Sins of Graphic Adventure Design* named the **walking-dead syndrome**: the human continues playing a game that has, unbeknownst to them, been rendered unwinnable. His worked example is *Uninvited* (1986). Walk past the mailbox in the Front Yard without looking inside it, step through the front door, and the door locks behind you forever. The mailbox held an item you now cannot get. As Maher puts it, "as soon as you go inside, you become a walking dead."

The mechanical condition underneath that experience is what the research literature calls a **softlock**. The FDG 2025 paper *Stuck in the Middle: Generating Levels without (or with) Softlocks* formalizes it as a state where "the player has not won or lost, but cannot make progress toward the goal." The distinction is worth holding onto for the rest of this article: a softlock is a property of the game state, a walking-dead state is a property of the player's situation. One causes the other, and tooling that conflates them is usually tooling that only measures the first.

| Failure mode | What breaks | Does the game stop? | Caught by crash telemetry? | Does the player know? |
|---|---|---|---|---|
| Crash | The process | Yes, immediately | Yes | Yes, at once |
| Avoidable death | The attempt | Yes — you reload | Sometimes | Yes, at once |
| Softlock | The game state | No — everything responds | No | Eventually, or never |
| Walking-dead state | The play session | No | No | Usually never — they just stop playing |

That last row is why this problem has economic teeth. A walking-dead state does not show up in a bug tracker as a defect. It shows up in a churn chart as a player who "lost interest."

## Why Does Walking-Dead State Detection Matter So Much?

Because the failure is structurally invisible to every instrument a live-ops team normally trusts. Bugnet's analysis of softlocks frames it as a data problem rather than a design problem: "players get stuck unable to progress while the game keeps running" produces no exception, no stack trace, no crash report. It describes the **silent majority** — most players who hit a softlock never report it, they simply leave. The worse the problem, the quieter it is. A quiet inbox proves nothing at all.

Crash telemetry catches the crash. It cannot catch the player standing in a room that has quietly become a tomb. And the review channel is biased in the same direction: a player who is frustrated by a wall writes a review; a player who has concluded, correctly, that the game is broken and unwinnable often just uninstalls. The worse the bug, the less likely it is to appear in the signal you are watching.

The engineering justification is simply scale. EA SEED reported that testing all maps and modes of *Battlefield V* for one hour requires **2,304 man-hours** — the equivalent of 288 people testing every single day. That is the number that makes scripted, human-driven exhaustive coverage impossible, and it is the number that makes an automated detector of unwinnable states worth building. You cannot staff your way to "every reachable state was checked."

The money is real too. NetEase's Wuji team analyzed **1,349 real bugs from four commercial online games**, and reported that one benchmark game carried 30 dedicated testers and roughly **$2M per year in direct bug losses**. Wuji's automated testing found three previously unknown bugs in commercial titles, later confirmed by the developers — evidence that this class of defect survives even heavy manual QA.

## Completability Is Not Softlock-Freedom — the One Distinction Everything Rests On

This is the single idea that separates a toy detector from a real one.

**Completability** asks whether *a* path exists from the start of the game to the goal. **Softlock-freedom** asks whether a path to the goal exists from *every* place the player can legally reach. Written out:

- Completability: ∃ a path start → goal.
- Softlock-freedom: ∀ reachable state *s*, ∃ a path *s* → goal.

A level can be perfectly winnable from the start and still strand a player who took a legal detour. This is exactly how adventure games, Metroidvanias and open-world quest chains fail, and it is why "we played it through and beat it" is not a completeness argument. It proves the existential quantifier and the game needed the universal one.

The FDG 2025 reachability-categorization work turns that universal into a generation-time constraint: classify every location as forward-reachable (reachable from the start), backward-reachable (can reach the goal), or a sink — an area where the player inevitably loses, like the bottom of a pit. The prevention rule is then mechanical: **every location forward-reachable from the start must also be backward-reachable from the goal, unless it is a sink.** Anything forward-reachable and not backward-reachable is a softlock waiting for a player to find it.

That constraint is not free, and the cost numbers are the most honest part of the paper. Generating levels with softlock-freedom takes roughly **3–5× longer** than plain path reachability. Allow softlocks in the generator and it costs 3–8×; add the extra requirement that softlocks stay disconnected from sinks and the cost climbs to **3–15×**. Verification is never the cheap part of level generation.

| Property | Quantifier | What it actually guarantees |
|---|---|---|
| Completability | ∃ path start → goal | The game can be won — by someone, on some route |
| Softlock-freedom | ∀ reachable *s*, ∃ path *s* → goal | No legal play can strand you |
| Reachability categorization | forward ∧ (backward ∨ sink) | Every place you can stand is either winnable from or a deliberate loss |
| Walking-dead state detection | ∀ reachable *s*, goal ∈ Reach(*s*) | The claim you actually want to make to players |

## The Static Approach: Decompile, Abstract-Interpret, Condense, Then Hunt Only the One-Way Edges

The strongest worked example of walking-dead state detection currently in public is **lucasartsifier**, whose README describes it plainly as a "Sierra softlock analyzer." It is a static analyzer: it never plays the game. It reads the game. Its pipeline has six stages.

| Stage | What it does | Why it exists |
|---|---|---|
| Decompile | Pull typed control-flow ASTs out of SCI bytecode | You cannot reason about what you cannot read |
| Extract | Identify rooms, scripts, items, registers, verbs | Build the vocabulary of the game world |
| Lift | Abstract-interpret player-affected state into guarded transitions | Turn imperative script code into a transition relation |
| Analyze | Tarjan SCC condensation + reachability fixpoints | Make the problem finite |
| Derive | Compute which crossings are unrecoverable | Find the actual stranding points |
| Patch | Compile and install guards, or refuse | Fix it, or decline to fix it |

The decompiler is a fork of sci-tools on a JSON-IR branch, roughly **277 additive lines**, whose purpose is to keep a typed AST instead of discarding it after printing. The analyzer itself is about **7,200 lines of Python 3 using only the standard library** — Tarjan, breadth-first search and fixpoint iteration, with no numpy, no networkx and no solver bindings. That is worth noting: the algorithmic core of a walking-dead detector is not exotic. It is graph reachability done carefully.

### Why strongly-connected components are the whole trick

The key insight, as the project states it, is that **only one-way edges between strongly-connected components can strand you — which is what makes the problem finite.**

Inside a strongly-connected component, everything reaches everything else. You can wander freely and always come back. Nothing inside a single SCC can trap you in a way you cannot also walk out of. The dangerous transitions are the irreversible ones *between* components: the door that locks behind you, the bridge that collapses, the one-way drop.

So the algorithm is: condense the room-transition graph into its SCCs, then look only at the edges between them. On *Leisure Suit Larry 2* the analyzer condensed **101 rooms into 27 strongly-connected components** tracked against **40 gating registers** — the flags and variables that record what the player has done. A 101-room game becomes a 27-node problem, and only a subset of the edges between those nodes need to be scrutinized.

This is the same idea that shows up in the academic literature under different names. Mawhorter and Smith's *Softlock Detection for Super Metroid with Computation Tree Logic* (FDG 2021) frames level designs as containing "errors called softlocks where a player traversing the level in an unintended manner can become permanently stuck," and uses CTL model checking over a model of the game rather than brute-force play — so detection is exhaustive over the model instead of over a finite set of playthroughs. Their follow-up replaced explicit search with symbolic breadth-first search over a BDD-encoded transition relation, buying reachability queries without paying a cost linear in the number of states. That formulation supports precisely the questions a walking-dead detector needs: *can I collect item A without beating boss B?* is the complete set of reachable states and shortest-path advice from any reachable state to any goal, asked as a query instead of a search.

Earlier model-based approaches cited in the same line of work include Petri nets, hyperstate space graphs and computation tree logic — a reminder that this problem has a formal-methods ancestry well before anybody attached an agent to it.

## Finding the Stranding: Required Later, Obtainable Now, Irreversibly Missable

With the graph condensed, the actual detection rule is a conjunction of three questions about each item or capability:

1. **Required later?** Is this item or flag needed downstream of some transition you might take?
2. **Obtainable now?** Can it still be picked up from where you stand?
3. **Irreversibly missable?** After this crossing, does access to it become permanently impossible?

All three together is a stranding condition. Any one of them absent is not. An item you cannot get and will never need is scenery. An item you need and can still get is a puzzle. The only thing that matters is the intersection — which is why a naive "did the player miss something?" checker produces noise, while a reachability-quotient checker produces a short list.

On the *Leisure Suit Larry 2* run, that intersection produced **15 item softlocks plus one disjunctive group** — a case where the stranding happens if the player misses any of several items rather than one named item. The full run recompiled **117 of 118 scripts into 10 patch files**.

The analyzer also carries a design principle worth stealing: **nothing is declared per title.** The start room, victory room, death signal and debug flags are all discovered from the game's own code. Validated across five games spanning both engine eras (SCI0 from 1988 through SCI1.1 in 1992) with no game-specific analysis code — *Leisure Suit Larry 2*, *King's Quest IV*, *King's Quest VI*, *Laura Bow 2* and *King's Quest V*. A detector that needs a hand-written config per game has not solved the problem; it has automated one instance of it.

## Guard Placement: Refuse at the Last Moment the Player Can Still Comply

Detection is half the job. The other half is what you do about it, and this is where most naive fixes make things worse.

The rule lucasartsifier uses: **place the guard at the last point where the player can still comply.** Demanding that a player drop something they can no longer drop is a wall, and the project treats a wall as worse than the bug it fixed. A guard that converts a silent walking-dead state into a visible, explainable refusal is good; a guard that converts it into an unexplained "you can't go that way" for the rest of the game is a different bug with the same name.

That single rule reshapes the tooling. You are not patching the room where the player got stuck — you are patching upstream, at the last checkpoint where the player still holds agency. Which means the analyzer has to compute, for every proposed guard site, whether the player can still satisfy the guard there. Guard placement is a design decision computed by the analyzer, not a string edit applied by the patcher.

The patch format is Sierra's own loose `script.NNN` override, and `RESOURCE.MAP` and the volume files are never modified — so deleting the overlay files reverts the game completely. Guard modes ship as Full, Lite and Off. Shipping a reversible patch matters more than it sounds: it means a player, a preservationist or a developer can audit the fix by removing it.

## Two-Sided Guards: When Carrying an Item Is the Fatal Mistake

Almost every article on softlocks treats the problem as **missing** something. The interesting cases are the mirror image, and this is the detail nearly nobody covers.

Some items are fatal to *hold* at a particular location. In *Leisure Suit Larry 2*, being in possession of the Spinach Dip is lethal in room 138. A correct guard set therefore needs **negative literals** — preconditions of the form "refuse this crossing if the player HAS this item" — not just the positive form "refuse if the player LACKS this item."

That asymmetry is why you cannot bolt a softlock check onto a simple inventory-requirement system. Requirement systems model what the player needs; walking-dead detection has to model what the player's possession *does*, in both directions. A guard language that only expresses positive preconditions will silently pass an entire class of unwinnable states — the ones where the player is punished for having been thorough.

## Prove It or Don't Ship It: Re-Verifying the Guarded Model

The differentiator between a heuristic and an instrument is that an instrument asserts a *checked* property. Two safety conditions are enforced inside the pipeline itself:

1. The guarded model is **re-verified to prove the guards introduce no new softlocks.** The output is an asserted property, "NEW softlocks introduced: none," not a hope.
2. **The pipeline refuses to emit anything** if the guards fail verification, or if a script it edited will not compile.

That second clause is the important discipline. Most automated repair has no refusal path — it produces output because output is the deliverable. A pipeline that can decline to ship is a pipeline whose output you can trust, because the failure mode of a bad guard is not a cosmetic diff, it is a second softlock in a different room, invisible until a player finds it. You have replaced one walking-dead state with another and made it look like a fix.

There is no way to verify softlock-freedom by testing alone; the space of legal play is exponential. The only tractable proof obligation is over the model — which is exactly why static analysis earns its keep here, and why the FDG cost multiples (3–5×, up to 3–15×) are the honest price of a guarantee rather than a sample.

The project also states its limits plainly: **no game has yet had a single continuous start-to-finish run on a patched build.** *King's Quest V* comes closest, tested row by row. And the analyzer hits real trouble on the *Quest for Glory* games, where abstract state explosion prevents completion — the authors suspect that abstracting away player stats, combat and health consumables would fix it. Any article that promises "just add AI agents" without mentioning state explosion is hiding the hard part. The analyzer that handles 101 rooms and 27 components cannot finish a game whose state includes a character sheet.

## Know What to Leave Alone: Do Not Guard Everything

A detector that prevents every possible death is a detector that has destroyed the game.

The project deliberately keeps avoidable deaths in, and its rule for the distinction is the point: it separates unwinnable states from avoidable deaths **by reachability, not by the death condition.** A death you can still recover from where you stand is not a softlock. It is feedback. It teaches the player what the puzzle wants, and removing it removes the only signal the designer had for communicating the solution.

Maher observed the same trade-off from the design side: the later Lucasfilm Games adventures strained hardest to make the walking-dead syndrome impossible, and were often forced into contrivances that "arguably sacrifice too much of that all-important illusion of freedom." Locking every door behind you and refusing to take items prevents unwinnable states the way a padded room prevents falls. The right target is not "no player ever loses." It is "no player is ever silently doomed."

Maher also draws a line worth keeping in the taxonomy: accidental dead ends are different from **intentional traps inserted to pad play length**. The former is the bug. The latter is a design choice that the same tooling can detect just as easily — and would report with equal confidence.

## The Dynamic Approach: RL and LLM Agents That Explore Their Way Into Dead Ends

Everything above is static. The other half of the field plays the game, and the numbers there have moved a long way.

**TITAN** — *Leveraging LLM Agents for Automated Video Game Testing* (Zhejiang University, NetEase Fuxi AI Lab, SMU) — is the most useful recent reference because it decomposes the agent rather than reporting a score. Four components:

1. **Perceive and abstract** high-dimensional game states into something the model can reason about.
2. **Proactively optimize and prioritize** available actions instead of sampling uniformly.
3. **Long-horizon reasoning** with action-trace memory and reflective self-correction.
4. **LLM-based oracles** that detect functional and logic bugs and produce diagnostic reports.

Reported results: **95% task completion against 82% for the best automated baseline, and 15 bugs detected against 9** — including four previously unknown bugs. The ablation study reports the Reflective Reasoning Module contributes the most, and that all components are indispensable. Most importantly, TITAN is deployed in **eight real-world game QA pipelines**, which is the difference between a benchmark result and something a studio actually runs. Its motivation is explicitly the state-action space and long-horizon reasoning limits of earlier LLM game-playing approaches.

**Reinforcement-learning playtesting** predates the LLM wave and still supplies the deployment-scale numbers. EA/DICE's production experience reported **250 concurrent agents across 5 servers for *Battlefield 2042*, versus only 7 for *Dead Space*** — and roughly **45 seconds of reset overhead per episode**, which is the unglamorous constraint that dominates any planning: every failed attempt costs you a level load. EA SEED's agents could navigate **80% of test levels within 24 hours of training from scratch**, and found bugs in areas human testers had cleared for weeks.

EA SEED's most transferable finding is about reward design rather than model architecture: **reward thorough exploration, not the hunting of specific bugs.** A coverage-driven agent finds exploits nobody scripted. A bug-specific reward finds exactly the bugs you already knew about, which is the opposite of what an unknown-defect detector is for.

Narrower, more measurable dynamic results round out the picture:

| Approach | Reported result | Source |
|---|---|---|
| DQN playtesting agent (RLBGameTester) | 92.3% accuracy detecting collision bugs, 88.7% on progression-blocking issues across 15 test levels | Wagde & Bide, cited in RL game testing writeup |
| EA SEED (RL) | 80% of test levels navigated within 24h of fresh training | EA/aigamingdev summary |
| TITAN (LLM agent) | 95% task completion vs 82% baseline; 15 bugs vs 9 | arXiv 2509.22170 |
| VideoGameQA-Bench (VLM) | Visual glitch detection rose from 57.2% to 82.8% with GPT-4o; best open-weight (Qwen-2.5-VL) 70.0% | Taesiri et al. |
| Vendor RL claim | ~10M unique states/day vs ~2,000/week for a 5-person manual team; 50+ softlock incidents per project | Vendor case study — **unverified, treat as marketing** |

That last row is worth calling out explicitly, because this is exactly where the field's hype lives. A vendor reporting ten million states a day against a five-person manual team's two thousand a week is comparing two different things: state *visits* (which include trivially similar states) against test *cases* (which are curated). Without a definition of "unique state" and an independent audit, the number is not evidence. The peer-reviewed figures above it are small and specific; the marketing figure is enormous and unfalsifiable. Prefer the former.

## Static vs Dynamic vs Hybrid: Which One Can You Actually Verify?

The tired framing is "static analysis versus AI agents." The useful framing is: **which approach can discharge which proof obligation?**

Static analysis gives you exhaustiveness *over a model* and a re-checkable proof obligation. It can say "no state reachable in this abstraction can strand the player" and back it with a verification run that a skeptic can repeat. It cannot see anything the model abstracts away — which is exactly why it collapses on games with character stats and consumables.

Dynamic agents give you coverage of the *real* system, reproducible traces, and evidence of bugs the model never encoded. They cannot give you a proof, because sampling — however intelligent — does not cover an exponential space.

| | Static analysis | RL agent | LLM agent | Hybrid |
|---|---|---|---|---|
| Unit of trust | Proof over a model | Reproducible trace | Reproducible trace + report | Proof + trace |
| Weakness | State explosion; abstraction gaps | Reset cost; reward hacking | Cost per step; nondeterminism | Two systems to maintain |
| Best at | "No reachable state strands you" | Coverage at scale, 24/7 | Bug oracles, diagnostics, long-horizon reasoning | Guarding what you proved, exploring what you didn't model |
| Typical evidence | "NEW softlocks: none," checked | 80% of levels in 24h | 95% completion, 15 bugs vs 9 | Both artifacts |

The honest architecture is hybrid, and it maps cleanly onto the two failure questions: *is there a state that strands a player?* is a static question with a static answer, and *does the game actually behave that way?* is a dynamic question that only an agent or a player can answer. Use the agent to find the dead ends and to confirm that the real build behaves as the model claims; use the analyzer to prove the fix does not introduce a new one.

## Building Your Own Walking-Dead Detector: A Practical Checklist

If you are constructing this rather than reading about it, the sequence that the public work supports is:

1. **Model the state, don't just log the actions.** You need the things that gate transitions — flags, items, stats, one-way triggers. Log lines that record "player pressed X" are not a model.
2. **Condense before you search.** Find strongly-connected components, then examine only inter-component edges. This is what makes the problem finite; skipping it is what makes it blow up.
3. **Define the goal explicitly, and prove both quantifiers.** Completability (∃ a path) is table stakes. Softlock-freedom (∀ reachable *s*) is the deliverable. Report them separately, always.
4. **Compute the three-condition conjunction per item.** Required later, obtainable now, irreversibly missable. Report only the intersection, ranked by how many rooms are behind the stranding point.
5. **Place guards at the last point of compliance.** For each guard site, verify the player can still satisfy it. A guard nobody can comply with is a wall, and a wall is worse than the bug.
6. **Support negative preconditions.** Sometimes the fatal mistake is carrying the item, not missing it. A guard language that cannot say "refuse if the player HAS this" is incomplete.
7. **Re-verify the guarded model, and refuse to ship on failure.** Assert "new softlocks introduced: none" as a checked property. Emit nothing if verification fails or a patched script will not compile.
8. **Keep the informative deaths.** Decide which deaths survive by reachability, not by the death condition. Deleting feedback is not fixing a bug.
9. **Instrument the live build anyway.** Add stuck-state detection and an in-game report button so that every failure you did not model is captured with build, device and breadcrumbs. Group identical failures into one ranked issue with an occurrence count, tie each to the build it happened on, and verify the signature disappears in the next release. Assume the dev machine is the least representative device the game will ever run on.
10. **Budget for the explosion.** If your game has consumable stats and combat, expect the abstraction to explode — the public analyzer simply cannot complete on *Quest for Glory*. Plan to abstract stats away, or plan to accept incomplete coverage. Do not promise what the state space will not allow.

## Frequently Asked Questions About Walking Dead State Detection

### What is a walking dead state in a game?

A walking dead state is a situation where the player keeps playing a game that has, without their knowledge, become unwinnable. The term comes from adventure-game design criticism — Jimmy Maher's "walking-dead syndrome" — and describes the player's situation rather than the code. The mechanical condition that causes it is called a softlock: the FDG 2025 literature defines that as a state where the player has not won or lost, but cannot make progress toward the goal. The game keeps running and keeps accepting input in both cases, which is precisely why neither shows up in crash telemetry.

### Is a walking dead state the same as a softlock?

No, and the distinction is useful. A softlock is a property of the game state — a reachable configuration from which the goal is unreachable. A walking dead state is a property of the player's session — a human who has not yet realized they are in that configuration and keeps playing. One softlock can produce many walking-dead states, because the player may wander for hours before giving up. Tooling that only detects the mechanical condition is still correct; tooling that only tracks player behavior is not, because most players in a walking-dead state never report anything at all.

### Why doesn't crash reporting catch unwinnable states?

Because nothing crashes. A softlock produces a game that renders, responds to input, plays audio and saves progress — every subsystem reports healthy. Crash telemetry fires on exceptions and signal faults, and a softlock generates none of them. Bugnet's framing is that softlocks are a data problem rather than a design problem: the stuck player is invisible to the instruments a live-ops team normally trusts, and there is a silent majority who hit the wall and simply stop playing rather than filing anything. The worse and more confusing the bug, the quieter the signal, because the players most affected are the ones who leave.

### Can an AI agent detect softlocks by playing the game?

It can detect them and it can demonstrate them, but it cannot prove they are absent. TITAN, an LLM-agent testing system from Zhejiang University, NetEase Fuxi AI Lab and SMU, reports 95% task completion against an 82% automated baseline and 15 bugs detected against 9, and is deployed in eight real-world QA pipelines. Reinforcement-learning approaches have gone further in production — EA/DICE ran 250 concurrent agents on *Battlefield 2042*. But sampling, however intelligent, does not cover an exponential state space. Agents give you coverage and reproducible traces; only static analysis over a model gives you a proof obligation you can re-check. The workable design is hybrid: agents explore and reproduce, an analyzer proves the resulting guards introduce no new softlocks.

### How do you prevent a walking dead state without ruining the game?

By placing guards at the last point where the player can still comply, and by guarding only what actually strands them. In practice that means refusing a crossing while the player can still go back and fix it, never demanding they undo something they can no longer undo, and supporting negative preconditions — refusing a crossing because the player is *carrying* the wrong item, not only because they lack the right one. Just as importantly, leave avoidable deaths alone: a death you can still recover from is feedback that teaches the puzzle, and the decision about which deaths survive should be made by reachability, not by the death condition. The goal is not to remove all failure. It is to make sure failure is never silent.
