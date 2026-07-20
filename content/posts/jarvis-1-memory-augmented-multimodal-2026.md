---
title: "JARVIS-1: Open-World Multi-Task Agents with Memory-Augmented Multimodal LLMs — Full Review"
date: 2026-07-20T19:02:40+00:00
tags:
  - JARVIS-1
  - multimodal LLM
  - embodied AI
  - Minecraft agent
  - memory-augmented AI
  - open-world agent
  - lifelong learning
description: "JARVIS-1 is a memory-augmented multimodal LLM agent that completes 200+ Minecraft tasks with 5x reliability over prior SOTA through self-improving multimodal memory."
draft: false
cover:
  image: "/images/jarvis-1-memory-augmented-multimodal-2026.png"
  alt: "JARVIS-1: Open-World Multi-Task Agents with Memory-Augmented Multimodal LLMs"
  relative: false
schema: "schema-jarvis-1-memory-augmented-multimodal-2026"
---

## What Is JARVIS-1 and Why Does It Matter for Open-World AI Agents?

JARVIS-1 is an open-world multi-task agent that combines multimodal large language models with a growing memory system to complete over 200 different tasks in Minecraft using human-like control and observation spaces. Developed by Team CraftJarvis at Peking University and BIGAI, JARVIS-1 achieves a 5x reliability improvement over previous state-of-the-art agents on the challenging ObtainDiamondPickaxe task and near-perfect performance on short-horizon tasks like chopping trees. Its key innovation is a multimodal memory that blends pre-trained knowledge from the LLM with actual game survival experiences, enabling self-improvement without retraining.

## How Does JARVIS-1's Architecture Work?

JARVIS-1 follows a three-stage pipeline: multimodal perception, plan generation, and goal-conditioned control. Each stage is designed to handle the unique challenges of open-world environments where the agent must interpret visual observations, reason about long-term goals, and execute precise actions.

### How Does Multimodal Input Processing Work?

The agent receives visual observations from the Minecraft environment as RGB frames and textual instructions describing the task. A pre-trained multimodal language model processes both modalities jointly, mapping visual observations and text instructions into a shared representation space. This allows JARVIS-1 to understand what it sees (a tree, a crafting table, a furnace) in the context of what it needs to do (chop wood, craft tools, smelt ore).

Unlike pure text-based approaches like GITM that rely on structured action spaces and text-only knowledge, JARVIS-1 operates in a human-like observation space — it sees pixel frames just as a human player would. This makes the approach more transferable to real-world robotics scenarios where raw visual input is the norm.

### How Does Plan Generation Work with Multimodal LLMs?

Once the visual and textual inputs are processed, the multimodal LLM generates high-level plans. These plans decompose the task into sub-goals that the agent can execute sequentially. For example, to obtain a diamond pickaxe, the agent must plan: gather wood → craft a wooden pickaxe → mine stone → craft a stone pickaxe → mine iron ore → smelt iron → craft an iron pickaxe → mine diamonds → craft a diamond pickaxe.

The LLM's pre-trained knowledge provides commonsense reasoning about these dependencies — it knows that you need a furnace before you can smelt iron, and that you need a pickaxe before you can mine stone. This commonsense reasoning is what separates JARVIS-1 from pure reinforcement learning approaches that must discover these dependencies through trial and error.

### How Do Goal-Conditioned Controllers Execute Plans?

After the plan is generated, goal-conditioned controllers translate each sub-goal into low-level actions. These controllers are trained to execute specific behaviors — moving to a location, interacting with a block, crafting an item — given a goal state. The controllers bridge the gap between high-level symbolic planning and low-level embodied control, a critical challenge for any open-world agent.

## What Makes Multimodal Memory the Key Innovation?

The defining feature of JARVIS-1 is its multimodal memory system, which stores both visual and textual experiences from past episodes. This memory grows over time and directly influences future planning and execution.

### Pre-Trained Knowledge vs. Game Experience

JARVIS-1's memory has two sources. First, the pre-trained multimodal LLM brings vast knowledge about the world — how tools work, what materials are needed for crafting, the structure of the Minecraft tech tree. Second, the agent accumulates actual game experiences: what happened when it tried to smelt iron without fuel, where it found diamonds, which sequence of actions led to success.

The combination is powerful. Pre-trained knowledge gives the agent a strong starting point, while game experience allows it to adapt to the specific environment and recover from mistakes. This mirrors how humans learn — we start with general knowledge and refine it through practice.

### Self-Improvement Through Growing Memory: The Epoch 1→3 Analysis

The JARVIS-1 project page demonstrates self-improvement across three training epochs on the ObtainDiamondPickaxe task:

| Epoch | Outcome | Key Failure / Improvement |
|-------|---------|--------------------------|
| Epoch 1 | Fails | Agent attempts to smelt iron but has no furnace |
| Epoch 2 | Fails | Agent builds a furnace but lacks fuel (coal/wood) |
| Epoch 3 | Succeeds efficiently | Agent mines extra logs for fuel before smelting, completing the full chain |

In Epoch 1, the agent's pre-trained knowledge told it to smelt iron, but it didn't know a furnace was needed. After failing, the memory recorded this gap. In Epoch 2, the agent built a furnace but didn't gather fuel — another failure recorded. By Epoch 3, the accumulated multimodal memory contained both failures, and the agent planned ahead: mine extra wood for fuel, build the furnace, then smelt. The task succeeded efficiently.

This three-epoch trajectory is remarkable because no model weights were updated. The agent improved purely through its growing memory, demonstrating that multimodal memory can substitute for expensive retraining in many scenarios.

## What Performance Benchmarks Does JARVIS-1 Achieve?

JARVIS-1 was evaluated across a comprehensive suite of Minecraft tasks, from simple atomic actions to complex multi-step crafting chains spanning the entire tech tree.

### Short-Horizon Tasks: Near-Perfect Performance

On short-horizon tasks — actions that require only a few steps, such as chopping a tree, mining dirt, or crafting a wooden plank — JARVIS-1 achieves near-perfect performance. These tasks benefit from the agent's strong pre-trained knowledge and the fact that fewer steps mean fewer opportunities for error accumulation.

### Long-Horizon Tasks: 5x Improvement on ObtainDiamondPickaxe

The ObtainDiamondPickaxe task is the standard benchmark for Minecraft agents. It requires the agent to navigate the full tech tree: collect wood, craft tools, mine progressively better materials, and finally craft a diamond pickaxe. JARVIS-1 achieves a 5x reliability improvement over previous state-of-the-art agents on this task.

| Metric | JARVIS-1 | Prior SOTA | Improvement |
|--------|----------|------------|-------------|
| ObtainDiamondPickaxe success rate | 5x more reliable | Baseline | 5x improvement |
| Short-horizon task accuracy | Near-perfect | Variable | Significant |
| Total tasks supported | 200+ | ~70 (DEPS) | 2.85x more tasks |
| Self-improvement method | Growing memory (no retrain) | Skill library (Voyager) | No GPU needed |

### 200+ Tasks Across the Minecraft Tech Tree

JARVIS-1 can complete over 200 different tasks spanning the entire Minecraft technology tree. This includes atomic tasks (chop a tree, mine stone), programmatic tasks (craft a pickaxe, build a furnace), and open-ended tasks (explore a cave, survive a night). The breadth of tasks demonstrates that memory-augmented multimodal LLMs can generalize across diverse objectives without task-specific fine-tuning.

## How Does JARVIS-1 Compare to Other Minecraft Agents?

Several notable approaches have tackled the Minecraft agent problem. Here is how JARVIS-1 stacks up against its predecessors and competitors.

### Voyager: The LLM-Powered Skill Library

Voyager, published in May 2023, was the first LLM-powered embodied lifelong learning agent in Minecraft. It uses GPT-4 via blackbox queries and features three components: an automatic curriculum, a skill library of executable code, and iterative prompting. Voyager obtained 3.3x more unique items, traveled 2.3x longer distances, and achieved 15.3x faster tech tree milestones than prior SOTA.

However, Voyager relies entirely on text-based prompting of GPT-4 and does not use multimodal input. It cannot see the game world — it only receives text descriptions. JARVIS-1 improves on this by processing visual observations directly, making it more suitable for real-world applications where text descriptions are unavailable.

### GITM: Text-Based LLM Knowledge and Memory

Ghost in the Minecraft (GITM) uses LLMs with text-based knowledge and memory, achieving a +47.5% improvement in success rate on the ObtainDiamond task. It was the first agent to procure all items in the Minecraft Overworld technology tree. Notably, GITM requires no GPU for training — only 32 CPU cores.

GITM's structured action space is both a strength and a limitation. It enables efficient planning but restricts the agent to predefined actions. JARVIS-1's human-like observation space is more flexible and transferable.

### DEPS: Interactive Planning with Goal Selection

DEPS (Describe, Explain, Plan and Select) introduced an interactive planning approach for zero-shot multi-task agents handling 70+ Minecraft tasks. Its goal selector module ranks parallel candidate sub-goals, achieving nearly double overall performance versus baselines. DEPS also demonstrated effectiveness in ALFWorld and tabletop manipulation environments.

### Plan4MC: Skill RL and Graph-Based Planning

Plan4MC combines skill reinforcement learning with planning for open-world long-horizon tasks. It introduces three types of fine-grained basic skills with intrinsic rewards, including a novel Finding-skill for exploration. Its LLM-based skill graph enables structured planning across 40 diverse Minecraft tasks, making it the most sample-efficient demonstration-free RL method at the time.

### OmniJARVIS: Unified VLA Tokenization (Successor)

OmniJARVIS, published in July 2024 by the same research group, represents the next evolution. It introduces unified Vision-Language-Action tokenization with a self-supervised behavior encoder that produces discretized tokens. OmniJARVIS creates unified token sequences for instructions, memories, thoughts, observations, and actions, enabling a single model to reason, plan, answer questions, and act. It achieves excellent results on atomic, programmatic, and open-ended tasks.

### Comparison Table

| Feature | JARVIS-1 | Voyager | GITM | DEPS | Plan4MC | OmniJARVIS |
|---------|----------|---------|------|------|---------|------------|
| Multimodal input | Yes (vision + text) | No (text only) | No (text only) | No (text only) | No (text only) | Yes (unified tokens) |
| Memory type | Multimodal (growing) | Skill library (code) | Text-based memory | None | Skill graph | Unified token memory |
| Tasks supported | 200+ | Unlimited (curriculum) | Full tech tree | 70+ | 40 | 200+ |
| Self-improvement | Growing memory | Iterative prompting | N/A | N/A | RL training | Unified tokens |
| GPU needed | Yes (multimodal LLM) | No (GPT-4 API) | No (32 CPU cores) | No (API) | Yes (RL) | Yes |
| Publication | Nov 2023 | May 2023 | May 2023 | Feb 2023 | Mar 2023 | Jul 2024 |

## What Are the Critical Limitations of JARVIS-1?

Despite its impressive results, JARVIS-1 has several limitations worth examining.

**Computational requirements.** JARVIS-1 requires a multimodal LLM for inference, which demands GPU resources. This contrasts with GITM, which runs on 32 CPU cores, and Voyager, which uses the GPT-4 API. For researchers without GPU access, JARVIS-1's approach may be less accessible.

**Minecraft-specific evaluation.** All benchmarks are conducted within Minecraft. While Minecraft is a rich open-world environment, it is still a game with simplified physics and clear reward structures. Transfer to real-world robotics — with noisy sensors, continuous action spaces, and physical constraints — remains unproven.

**Memory growth management.** The multimodal memory grows over time as the agent accumulates experiences. Without a forgetting or summarization mechanism, the memory could become unwieldy after thousands of episodes. The paper does not fully address how memory scales with long-term deployment.

**Dependency on pre-trained models.** JARVIS-1's performance is bounded by the capabilities of its underlying multimodal LLM. If the LLM lacks knowledge about a particular domain or makes reasoning errors, the agent inherits those limitations. The self-improvement mechanism can compensate for some gaps but cannot overcome fundamental model weaknesses.

**Evaluation methodology.** The 5x reliability improvement figure is impressive, but the paper does not provide extensive statistical analysis across multiple seeds or environments. Reproducibility and variance across runs would strengthen the claims.

## What Are the Future Directions for Memory-Augmented Multimodal Agents?

The trajectory from Voyager to JARVIS-1 to OmniJARVIS suggests several clear research directions.

**Unified tokenization.** OmniJARVIS's approach of representing instructions, memories, thoughts, observations, and actions as a unified token sequence points toward a future where a single model handles all aspects of agent behavior without separate planning and control modules.

**Scalable memory architectures.** As agents accumulate more experiences, efficient memory retrieval and summarization become critical. Future work will likely explore hierarchical memory, attention-based retrieval, and learned forgetting mechanisms.

**Transfer to robotics.** The ultimate test for open-world agents is deployment on physical robots. JARVIS-1's human-like observation space makes it a strong candidate for transfer, but the gap between Minecraft and the real world remains substantial.

**Multi-agent collaboration.** Minecraft supports multiplayer environments. Extending JARVIS-1 to multi-agent settings where agents share memories and coordinate tasks is a natural next step.

**Sample efficiency.** While JARVIS-1 improves through memory rather than retraining, it still requires multiple episodes to accumulate useful experiences. Combining memory augmentation with more sample-efficient exploration strategies could accelerate learning.

## Conclusion

JARVIS-1 represents a significant step forward in open-world multi-task agents by demonstrating that memory-augmented multimodal LLMs can achieve reliable, self-improving performance across 200+ diverse tasks. Its 5x reliability improvement on the ObtainDiamondPickaxe benchmark and near-perfect short-horizon task performance validate the approach of combining pre-trained multimodal knowledge with growing experiential memory.

The evolution from Voyager's skill library approach to JARVIS-1's multimodal memory to OmniJARVIS's unified tokenization shows a clear trajectory toward more integrated, capable agents. While limitations remain — particularly around computational requirements, Minecraft-specific evaluation, and memory scaling — the direction is promising for anyone building generalist embodied AI systems.

For researchers and practitioners, JARVIS-1 offers a compelling architecture that balances pre-trained knowledge with experiential learning, achieving self-improvement without the cost of model retraining. As the field moves toward unified vision-language-action models, the lessons from JARVIS-1's multimodal memory design will likely influence the next generation of open-world agents.

## Frequently Asked Questions

### What is JARVIS-1?

JARVIS-1 is an open-world multi-task agent that uses a memory-augmented multimodal large language model to complete over 200 different tasks in Minecraft. It processes visual observations and text instructions to generate plans, executes them through goal-conditioned controllers, and improves over time by accumulating multimodal memories of its experiences.

### How is JARVIS-1 different from Voyager?

Voyager uses GPT-4 with a skill library of executable code and iterative prompting but operates on text descriptions only. JARVIS-1 processes visual observations directly through a multimodal LLM and uses a growing multimodal memory system rather than a code-based skill library. JARVIS-1 also achieves a 5x reliability improvement on the ObtainDiamondPickaxe task.

### Does JARVIS-1 require GPU training?

JARVIS-1 requires a GPU to run its multimodal LLM for inference, but it does not require model retraining or fine-tuning. The agent improves through its growing memory system, not through weight updates. This is different from approaches like Plan4MC that require reinforcement learning training.

### What tasks can JARVIS-1 complete?

JARVIS-1 can complete over 200 different Minecraft tasks spanning atomic actions (chopping trees, mining stone), programmatic tasks (crafting tools, building furnaces), and open-ended tasks (exploring caves, surviving nights). It covers the full Minecraft technology tree from basic wood collection to diamond tool crafting.

### What is OmniJARVIS and how does it relate to JARVIS-1?

OmniJARVIS is the successor to JARVIS-1, published in July 2024 by the same research group. It introduces unified Vision-Language-Action tokenization where instructions, memories, thoughts, observations, and actions are all represented as a single token sequence. This allows a single model to reason, plan, answer questions, and act without separate modules.
