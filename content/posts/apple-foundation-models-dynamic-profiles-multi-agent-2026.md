---
cover:
  alt: 'Apple Foundation Models Dynamic Profiles: Multi-Agent iOS Workflows in 2026'
  image: /images/apple-foundation-models-dynamic-profiles-multi-agent-2026.png
  relative: false
date: 2026-06-14 16:04:26+00:00
description: Build multi-agent iOS workflows with Apple Foundation Models Dynamic
  Profiles, model routing, tools, and evaluations.
draft: false
schema: schema-apple-foundation-models-dynamic-profiles-multi-agent-2026
tags:
- Apple Foundation Models
- iOS AI
- Swift
title: 'Apple Foundation Models Dynamic Profiles: Multi-Agent iOS Workflows in 2026'
---

Apple Foundation Models Dynamic Profiles let iOS developers switch instructions, tools, generation settings, and model backends inside one `LanguageModelSession`. The practical result is context-preserving model routing: one app workflow can move between private on-device reasoning, Private Cloud Compute, and specialized external models without rebuilding every conversation state by hand.

## What are Apple Foundation Models Dynamic Profiles?

Apple Foundation Models Dynamic Profiles are declarative runtime profiles that change how a `LanguageModelSession` behaves for a specific phase of an AI workflow. Apple introduced them in WWDC26 Foundation Models sessions 241 and 242 alongside a broader 2026 stack: on-device models, image input, Private Cloud Compute, third-party model abstraction, the `fm` CLI, Python SDK, and an Evaluations framework. A profile can represent a planner, tool executor, summarizer, image analyst, or escalation agent while preserving the session transcript. The important shift is that developers no longer need to model every handoff as a hard boundary between separate chat sessions. A Dynamic Profile is best understood as a context-preserving configuration layer for agentic apps, not as a magic agent framework. The takeaway: Dynamic Profiles make multi-step iOS AI workflows easier to express while leaving routing, safety, and product design in the developer's hands.

Before Dynamic Profiles, I usually saw teams implement "agents" as separate service objects with their own prompts, histories, and model clients. That works until the first real user session crosses boundaries. The planner has relevant context, the executor needs only part of it, the summarizer needs a transformed view, and the compliance step must avoid private data. Dynamic Profiles turn those boundaries into explicit Swift concepts.

## What problem do Dynamic Profiles solve in multi-agent iOS apps?

Dynamic Profiles solve the transcript-copying and configuration-drift problem that appears when an iOS app needs multiple AI behaviors in one user journey. Apple says the 2026 Foundation Models framework can use on-device models, server models, custom skills, system tools, and Dynamic Profiles through one native Swift API, while Private Cloud Compute offers a 32,000-token context window for harder tasks. Without profiles, developers often create separate `LanguageModelSession` instances for each role and manually copy context between them. That creates bugs: missing tool results, duplicated user messages, stale instructions, and privacy leakage when sensitive transcript fragments reach a cloud model. Dynamic Profiles let the app select a role-specific configuration while keeping continuity where continuity is intended. The takeaway: they remove a lot of plumbing, but they do not remove the need to design clean workflow boundaries.

Consider a trip-planning app. One profile can collect user constraints on device, another can call calendar and maps tools, another can escalate to PCC for long-horizon reasoning, and another can summarize the plan for sharing. The user experiences one assistant. The app still has four operational modes with different permissions and latency expectations.

## How does DynamicProfile work inside one LanguageModelSession?

DynamicProfile works by letting a single `LanguageModelSession` apply different instructions, model choices, tools, and generation options as the workflow state changes. WWDC26 session 242 frames the API around dynamic context and agentic workflows, including dynamic instructions, model configuration per phase, transcript or history transforms, lifecycle modifiers, and orchestration patterns such as baton-pass and phone-a-friend. In practical Swift architecture, you define profiles around app states rather than around vague personalities. For example, a `ResearchProfile` can use browsing or document tools, a `PlannerProfile` can request structured JSON, and a `ReviewerProfile` can run with stricter safety instructions. The session remains the container, while the active profile controls the behavior for the next generation step. The takeaway: profile selection should be deterministic enough to debug, even when the model output is probabilistic.

I would avoid naming profiles after human roles unless the role maps to a concrete contract. `Concierge`, `Expert`, and `Assistant` are weak boundaries. `ExtractCalendarConstraints`, `RankCandidatePlans`, and `GenerateFinalSummary` are better because the expected inputs, tools, and output schema are easier to test.

### How should profiles map to Swift app state?

Profiles should map to explicit workflow states, not to button labels or prompt fragments. A good state model might include `intake`, `classify`, `retrieve`, `act`, `verify`, and `summarize`. Each state owns its allowed tools, output format, and model preference. That makes the profile switch auditable in logs and easier to reproduce in evaluations when a user reports a bad handoff.

## How should apps route local, Private Cloud Compute, and third-party models?

Model routing in Apple Foundation Models Dynamic Profiles should be based on privacy, latency, reasoning depth, cost, and capability rather than on a fixed preference for one model. Apple's third-generation AFM family includes AFM 3 Core, described as a 3-billion-parameter dense on-device model, and AFM 3 Core Advanced, a 20-billion-parameter sparse on-device model that activates 1 to 4 billion parameters per request. Apple also says AFM 3 Cloud Pro powers demanding use cases such as agentic tool use and complex reasoning, while WWDC26 session 339 describes `LanguageModelExecutor` as a way for local or server-based models to back a `LanguageModelSession`. The practical architecture is tiered: keep sensitive and short tasks local, use PCC for harder Apple-native reasoning, and use third-party models only where they clearly add capability. The takeaway: routing is a product policy, not just an API call.

| Route | Best fit | Avoid when | Profile example |
|---|---|---|---|
| On-device AFM | Private short tasks, low latency, offline-friendly flows | The task needs long context or heavy reasoning | Intake, classification, quick rewrite |
| Private Cloud Compute | Long context, complex planning, Apple privacy boundary | Network is unavailable or latency budget is tight | Multi-step planner, tool-use reviewer |
| Third-party executor | Specialized model strengths or enterprise model policy | Credentials cannot be safely proxied | Code reasoning, domain-specific review |

### What changes with LanguageModelExecutor?

`LanguageModelExecutor` matters because it turns the model backend into an implementation detail behind a common session abstraction. That does not mean third-party integration is free. Production apps still need secure credential proxying, request logging policies, App Attest or equivalent abuse controls, and clear user-facing privacy expectations. The executor abstraction reduces application code branching, not operational responsibility.

## How should teams design profiles by task phase, privacy, cost, and latency?

Teams should design Dynamic Profiles as workflow contracts that encode what the app is allowed to know, do, spend, and delay at each phase. Apple notes that developers in the App Store Small Business Program with fewer than 2 million total first-time App Store downloads can access next-generation Apple Foundation Models on Private Cloud Compute at no cloud API cost, which changes early-stage economics but not architecture discipline. A good profile definition should answer four questions: what data can enter, what tools can run, what model tier is allowed, and what output format is required. Cost-sensitive apps should prefer on-device profiles for routine classification and reserve PCC or third-party executors for tasks with measurable user value. Latency-sensitive apps should stream partial progress or split work into fast local and slower background phases. The takeaway: profiles should encode operational constraints as strongly as they encode prompts.

For example, a health journaling app might keep mood extraction on device, use PCC only for weekly pattern analysis after consent, and forbid third-party models entirely. A developer productivity app might do the opposite: local summarization for small notes, PCC for issue planning, and a third-party code model for repository-specific reasoning through a secure backend.

## How do transcript management and history transforms affect context windows?

Transcript management controls what each profile sees from the shared session history, and history transforms prevent multi-agent workflows from drowning in irrelevant context. Apple says the Private Cloud Compute language model has a 32,000-token context window, which is large for mobile workflows but still finite when tool results, images, user files, and repeated profile handoffs accumulate. Dynamic Profiles are useful because they can preserve continuity, but preserving everything is rarely the right move. A planner may need raw user constraints and retrieved facts, while an executor may need only the selected plan and authorized tool inputs. A reviewer may need tool-call traces but not the full conversational back-and-forth. The engineering goal is to transform history into the smallest truthful representation required for the next phase. The takeaway: context preservation is valuable only when paired with intentional context reduction.

In practice, I treat transcript transforms like database migrations for AI state. They should be deterministic, versioned where possible, and easy to inspect. If a profile handoff fails, you need to know whether the model reasoned badly or whether your transform starved it of a required fact.

### What should a history transform include?

A history transform should include user intent, durable constraints, selected facts, relevant tool outputs, and unresolved decisions. It should exclude repeated greetings, superseded plans, raw private data not needed by the next profile, and large documents that can be referenced by ID. The best transform is boring: a compact, structured state packet that a developer can read during incident review.

## How do tool calling and agent handoff patterns work?

Tool calling and agent handoff patterns work by giving each profile a bounded set of actions and a clear rule for when another profile should take over. WWDC26 session 242 names baton-pass and phone-a-friend orchestration as first-party patterns for multi-agent Foundation Models workflows. Baton-pass means one profile completes its phase and transfers a prepared state to the next profile. Phone-a-friend means a profile temporarily consults another profile or model for a specialized subtask, then resumes control. These patterns are safer than allowing every profile to call every tool at every point in the session. The app can restrict calendar writes to an execution profile, retrieval to a research profile, and final user-visible wording to a summarizer profile. The takeaway: handoffs should narrow authority, not expand it accidentally.

Here is the rule I use: if a tool can change user data, spend money, send a message, or contact an external service, it belongs behind an explicit phase gate. The model can recommend an action earlier, but a dedicated execution profile should validate inputs and request confirmation when the action has real-world consequences.

| Pattern | Control flow | Best use | Risk |
|---|---|---|---|
| Baton-pass | Profile A finishes, Profile B continues | Linear workflows like research to plan to execute | Bad state packet poisons the next phase |
| Phone-a-friend | Profile A asks Profile B for help, then resumes | Specialized checks like policy or code review | Hidden latency and unclear responsibility |
| Supervisor | A routing profile delegates to worker profiles | Complex apps with many task types | Over-centralized prompt becomes brittle |

## What production architecture works for a multi-agent iOS workflow?

A production multi-agent iOS workflow should separate UI state, AI session state, profile routing, tool execution, and observability into distinct layers. Apple's 2026 Foundation Models updates make the model interface more unified, but production reliability still comes from conventional software boundaries: typed state, retry policy, authorization checks, request IDs, and durable logs. I would structure an app around a workflow coordinator that owns the `LanguageModelSession`, a profile registry that defines allowed models and tools, and tool adapters that enforce permissions before any side effect. The coordinator should decide when to use local AFM, PCC, or a third-party executor based on the current state and policy. UI code should not concatenate prompts or choose model backends directly. The takeaway: Dynamic Profiles belong in an architecture, not scattered through view callbacks.

A minimal architecture looks like this:

| Layer | Responsibility | Example |
|---|---|---|
| SwiftUI view | Displays state and collects consent | "Approve calendar update" |
| Workflow coordinator | Advances phases and selects profiles | Intake to planning to execution |
| Profile registry | Defines instructions, tools, models, options | `PlanTripProfile` |
| Tool adapter | Validates and runs side effects | Calendar, files, network |
| Evaluation harness | Replays traces and checks regressions | Tool-call trajectory tests |

### Where should privacy checks live?

Privacy checks should live outside the prompt and inside the routing and tool layers. Prompt instructions help, but they are not a policy engine. If a profile is not allowed to send contact names to a cloud model, the coordinator should remove or redact that data before the request. If a profile cannot write to calendar, the tool adapter should reject the call even if the model asks confidently.

## How should teams test Dynamic Profiles with evaluations and tool-call traces?

Teams should test Dynamic Profiles by replaying complete workflow traces, not just by scoring final answers. WWDC26 session 241 lists an Evaluations framework, the `fm` CLI, Python SDK, and Foundation Models utilities as major updates, which matters because multi-agent failures usually happen between steps. A final summary can look good even if the planner ignored a constraint, the executor called the wrong tool, or the reviewer saw a transformed history that removed a critical fact. Evaluation cases should capture the initial user request, selected profile sequence, transformed transcripts, model route, tool calls, tool results, and final response. Tests should assert both outcome quality and process constraints, such as "never call a write tool before confirmation." The takeaway: evaluate the trajectory, not only the prose.

I like three test buckets. Golden path tests prove the intended workflow still works after prompt or model changes. Adversarial tests check privacy, tool misuse, and prompt injection. Regression tests lock down real bugs from production traces after redaction. Each bucket should include at least one handoff assertion, because handoffs are where multi-agent apps tend to fail quietly.

## What are the common pitfalls, beta caveats, and migration notes?

Common Dynamic Profiles pitfalls include vague profile boundaries, over-sharing transcript history, granting broad tool access, routing everything to the most expensive model, and treating beta API names as stable. Independent developer writeups after WWDC26 have already noted that Foundation Models beta APIs may change before final release, which is normal for a new framework surface. The migration risk is not just syntax churn. Apps that build profile logic directly into views, prompts, or one-off closures will be harder to adjust when Apple changes naming, lifecycle hooks, or utilities. The safer migration path is to isolate profile definitions, routing policy, and history transforms behind small internal protocols. That gives your app one place to update when the SDK shifts. The takeaway: design for API movement while keeping product behavior stable.

The other mistake is overselling "multi-agent" to users. Most users do not care how many profiles are involved. They care that the app is responsive, private, correct, and reversible when it is about to act. Use Dynamic Profiles to improve those outcomes, not to make the architecture visible.

### How should existing Foundation Models apps migrate?

Existing apps should migrate one workflow at a time. Start with the place where you already switch prompts, tools, or sessions manually. Replace that boundary with an explicit profile, preserve the old behavior with evaluation tests, then add history transforms. Avoid changing model route, prompt, and tool permissions in the same release unless you can measure the blast radius.

## What does an example research, plan, execute, and summarize workflow look like?

An example Dynamic Profiles workflow for iOS can use four phases: research, plan, execute, and summarize, each with a different profile inside one `LanguageModelSession`. In a personal productivity app, the research profile could inspect notes and calendar availability on device, the planning profile could use PCC for a 32,000-token scheduling problem, the execution profile could call calendar tools only after explicit approval, and the summary profile could produce a concise user-facing update. The profile sequence is not about pretending four agents are chatting. It is about changing model capability, permissions, context, and output format at the point where the product need changes. The shared session preserves enough continuity to feel coherent, while transforms keep each phase focused. The takeaway: a good workflow feels like one assistant to the user and four bounded contracts to the developer.

For a concrete implementation, I would start with typed phase outputs:

| Phase | Input | Output | Allowed tools |
|---|---|---|---|
| Research | User request, local notes | Facts and constraints | Read-only notes, calendar availability |
| Plan | Constraints, candidate slots | Ranked plan JSON | None or retrieval only |
| Execute | Approved plan | Tool calls and status | Calendar write, reminder create |
| Summarize | Execution result | Human-readable recap | None |

This keeps the AI workflow testable. If the calendar event is wrong, you can inspect whether the research phase missed a constraint, the plan phase ranked badly, or the execution phase used the wrong structured field.

## FAQ: Dynamic Profiles, PCC, Claude/Gemini, and App Store readiness

Apple Foundation Models Dynamic Profiles raise practical questions about availability, model choice, privacy, third-party providers, and release readiness because they sit at the boundary between Swift app architecture and AI operations. In 2026, Apple presents Dynamic Profiles alongside Private Cloud Compute, third-party model abstraction through `LanguageModelExecutor`, system tools, evaluations, and the third-generation AFM model family. That combination makes multi-agent workflows much more realistic on iOS, but it also creates new engineering choices. Teams need to decide which tasks stay on device, which can use PCC, when a third-party model is justified, how tool permissions are enforced, and what must be tested before App Store release. The answers below focus on production tradeoffs instead of API trivia. The takeaway: Dynamic Profiles are ready to design around, but every workflow still needs policy, testing, and fallback behavior.

### Are Dynamic Profiles the same as AI agents?

Dynamic Profiles are not the same as full autonomous agents. They are a Foundation Models mechanism for changing session behavior across workflow phases. You can use them to build agentic apps, but autonomy comes from your coordinator, tools, routing policy, and state machine. The profile is the configuration boundary; the product architecture decides what action is allowed.

### Can Dynamic Profiles use Private Cloud Compute?

Dynamic Profiles can be designed to route eligible phases to Private Cloud Compute when the task needs stronger reasoning or a larger context window. Apple says PCC provides a 32,000-token context window in the 2026 Foundation Models stack. Use PCC for high-value reasoning, not for routine local tasks that an on-device model handles well.

### Can I use Claude or Gemini with Foundation Models workflows?

Third-party models can fit into Foundation Models workflows through the 2026 model abstraction pattern described around `LanguageModelExecutor`. The app still needs a secure server-side credential strategy, provider policy, logging controls, and privacy review. Treat third-party routing as an explicit profile decision, not as a silent fallback for every failure.

### Do Dynamic Profiles remove the need for prompt engineering?

Dynamic Profiles reduce prompt sprawl, but they do not remove prompt design. Each profile still needs clear instructions, output constraints, tool permissions, and failure handling. The difference is that those instructions can be scoped to a phase instead of overloaded into one giant system prompt that tries to handle every possible app state.

### What should I test before shipping a Dynamic Profiles app?

Test the profile sequence, transcript transforms, model routes, tool-call permissions, and final outputs. Include privacy cases, prompt injection attempts, offline or slow-network behavior, and fallback paths when PCC or a third-party executor is unavailable. For multi-agent workflows, a passing final answer is not enough; the intermediate decisions need to be correct too.