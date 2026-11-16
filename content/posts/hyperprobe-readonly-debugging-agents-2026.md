---
title: "Read-Only Debugging Agents for Production: A Capability Envelope You Can Audit (2026)"
date: 2026-11-16T00:10:00+00:00
tags:
  - AI agents
  - production debugging
  - read-only access
  - audit trail
  - access control
  - observability
  - MCP
description: "Read-only is four separate controls, and only three are enforced by the system rather than by the agent's own behaviour. How to draw the capability envelope, where each layer leaks, and which fields make a debugging session auditable after the fact."
draft: false
cover:
  image: "/images/hyperprobe-readonly-debugging-agents-2026.png"
  alt: "Read-only debugging agents for production: a capability envelope you can audit"
  relative: false
schema: schema-hyperprobe-readonly-debugging-agents-2026
---

An agent that can look at a production incident is useful. An agent that can also change production is a second incident waiting for a bad day. Most teams resolve that tension by choosing one extreme: hand the agent the same credentials an on-call engineer uses, or keep it out of the incident entirely and go back to `kubectl` and grep.

The direct answer to the middle path is this: "read-only" is not one control, it is four, and they do not fail together. The agent's tool selection is advisory. The other three — the credential or API scope the call travels over, the database transaction mode, and the runtime guard on evaluated expressions — are enforced somewhere outside the agent's goodwill. A session is only as safe as the outermost enforced layer, and it is only auditable if the enforcement decision is recorded per call.

## Four layers, and only three of them are enforced by something other than the agent

When a vendor, a framework, or your own tool wrapper says a debugging capability is read-only, the guarantee is coming from one of these layers. They are not equivalent.

| Layer | Enforced by | What it stops | Typical failure |
|---|---|---|---|
| Agent tool selection | The agent's own policy loop | A write tool that was not offered | The agent holds a second credential, or the wrapper exposes an unlisted tool |
| Interface scope (API, MCP server, SQL user grants) | The remote server or the database grant | Operations the credential cannot perform | The credential is broader than the task and reused across sessions |
| Database transaction mode | The database engine | Statement classes the engine refuses inside a read-only transaction | The engine's own documented gaps, and anything outside SQL |
| Runtime expression guard | The language runtime | Evaluated expressions with detectable side effects | The guard is experimental, conservative, or absent for the runtime in use |

The first row is a promise. The second, third, and fourth rows are refusals that happen whether or not the agent agrees. If your only read-only control is the first row, you are trusting a language model to keep a promise under adversarial input, which is exactly the condition in which it will not. If your control is the third row, you get a hard stop at the engine — but only for the statement classes the engine documents, which is where the interesting gaps live.

## Drawing the capability envelope

An envelope is a written answer to one question: what may this agent do to this system, in this environment, for the length of this session? Three categories make it usable, and the third one is the one teams forget.

- **Observe.** Read the schema, read logs, read metrics, `EXPLAIN` a query without `ANALYZE`, read the deployed commit and config. These are the operations an incident actually needs, and every one of them has a read-only form.
- **Derive.** Aggregate, correlate by trace ID, diff two deploys, compute a rate. Derivation is where a debugging agent earns its place, because it turns reads into an answer. It is also where the line is easiest to blur, since "derive" invites `EXPLAIN ANALYZE`, which executes the plan and is therefore not a read.
- **Refused by design.** Any DDL or DML, any expression that can invoke a getter or a function, any process execution, any credential other than the session's own. The refusal must be visible to the agent — a silent empty result teaches the model that the tool is broken and invites a retry through another path.

The scope of the envelope is not just the operation list. It is the tuple of environment, database or service, and version, plus the limits: statement timeout, row cap, session duration, and capture budget. A read-only query without a row cap is a denial-of-service primitive, and an unbounded capture buffer inside a production process is a memory incident.

## Where the guarantee leaks

**PostgreSQL's read-only transaction is a high-level notion, and the documentation says so.** `SET TRANSACTION READ ONLY` disallows `INSERT`, `UPDATE`, `DELETE`, `MERGE`, and `COPY FROM` when the target is not a temporary table; all `CREATE`, `ALTER`, and `DROP` commands; `COMMENT`, `GRANT`, `REVOKE`, `TRUNCATE`; and `EXPLAIN ANALYZE` or `EXECUTE` of any of those. The same page says plainly that this "is a high-level notion of read-only that does not prevent all writes to disk" — and writes into temporary tables remain permitted. If a debugging agent can create and fill a temp table, it has a write path inside a nominally read-only transaction. See the [PostgreSQL SET TRANSACTION documentation](https://www.postgresql.org/docs/current/sql-set-transaction.html).

**A side-effect guard refuses what it cannot rule out, not what is impure.** In the Chrome DevTools Protocol, `Runtime.evaluate` takes `throwOnSideEffect`, documented as "whether to throw an exception if side effect cannot be ruled out during evaluation", and the parameter is marked experimental. That wording is conservative in the right direction, but it is a refusal test, not a purity proof: an expression that does not trip the flag is not thereby shown to be side-effect free, and a specific V8 build or a vendor SDK may pass the flag through differently. The [CDP Runtime domain](https://chromedevtools.github.io/devtools-protocol/tot/Runtime/) lists the parameter and its experimental marker.

**The layer a probe runs in decides which guarantee you get.** A Python in-process probe uses either `sys.settrace` or the newer `sys.monitoring` namespace, added in 3.12, which lets a tool register callbacks for execution events and assigns each tool an integer identifier so concurrent tools do not interfere. That is an observation surface, not a read-only guarantee: enforcement there is whatever the tool's own policy layer implements on top. The [Python `sys.monitoring` documentation](https://docs.python.org/3/library/sys.monitoring.html) describes the callbacks and tool IDs and nothing about side effects.

**The second credential is the leak nobody instruments.** An agent denied a write tool will happily use a shell tool, an HTTP client, or an MCP server that was never in the envelope, if one is reachable. Envelope enforcement that lives only inside the agent's tool list does not survive a second tool server being mounted, which is why the credential scope and the network egress, not the tool list, are the controls that matter.

## What an auditable session record must contain

A transcript is not an audit record. A transcript shows what the agent said; an audit record shows what the system decided, and it is the second one that a security reviewer will ask for. Thirteen fields cover the questions that come up after an incident:

| Field | Question it answers |
|---|---|
| Session and run ID | Which investigation was this, and can it be replayed? |
| Sequence number | What order did the calls happen in, including refusals? |
| UTC timestamp | When, against which deploy and which incident window? |
| Acting agent identity | Which agent, under which task, with which instructions? |
| Model identifier and version | Which model chose these calls? |
| Envelope policy hash | Which exact policy bytes were in force? |
| Tool name and argument hash | What was attempted, without storing the arguments themselves? |
| Decision and rule ID | Allowed or denied, and which rule decided? |
| Target scope | Which environment, database, service, and version? |
| Result digest and byte count | What came back, and can it be proved unchanged? |
| Redaction events | What was removed before the record was written? |
| Retention and immutability | How long does this survive, and who can delete it? |
| Side-effect assertion | Did the refusal happen before or after any execution? |

The last two are the ones that turn a log into evidence. Deletable records are a data-hygiene feature, not an audit trail: if the captured payloads can be purged on request, the immutable part must live somewhere else, and the record has to say which part it is.

## Testing your own envelope instead of trusting its description

The check is small enough to run on a laptop, and the point is the negative assertions: it must prove that the write is refused, not that the read works. I wrote a fixture that does this and ran it locally. It has a seeded SQLite database with a read-only view, a deny-by-default envelope policy, a scripted client that attempts the calls a debugging agent would attempt, and a per-call audit record.

It is a local fixture, not a vendor measurement, and the client is scripted on purpose: no language model was invoked, so the run measures the enforcement layers and the record they produce, and says nothing about which tools a model would choose or whether it retries after a refusal.

The database layer refused six of seven statements. Five of them — the INSERT, the UPDATE, the DELETE, a `CREATE TABLE`, and a `CREATE TEMP TABLE` — raised `OperationalError: attempt to write a readonly database`, and the sixth, a follow-up insert into the temp table, raised `no such table: scratch` because the create had already been refused. The `SELECT` through the view returned rows. The tool layer saw nine calls: four allowed, five refused, and four distinct rules fired (`TOOL_DENIED`, `SQL_NOT_SELECT`, `SQL_MULTI_STATEMENT`, `EXPR_CALL`). Every refusal came back to the caller as a message naming the rule that fired, which is what makes the refusal useful to the agent rather than merely safe. The orders table fingerprint was identical before and after the session, and all six rows remained.

The audit record is where the run was least satisfying, and that is the useful finding. The fixture declares thirteen fields — `session_id`, `seq`, `ts_utc`, `actor_agent_id`, `actor_model_id`, `policy_sha256`, `tool`, `args_sha256`, `decision`, `rule_id`, `scope`, `result_sha256`, `result_bytes` — and that is not the thirteen-field set recommended in the table above. It carries no run identifier apart from the session, and it has no redaction-event, retention-or-immutability, or side-effect-assertion field: those three, plus a run ID, are the recommended fields the fixture does not implement, which is why its record cannot answer the last three questions in that table. Nine of the thirteen fields it does declare were non-null on every record. The four that were null somewhere were `actor_model_id`, `rule_id`, `result_sha256`, and `result_bytes`. The first is honest — no model ran. The other three are design bugs that a real deployment would inherit from a naive implementation: `rule_id` is null on the allowed path, so the record cannot say which rule permitted a call; and a denied call carries no result digest, so nothing in the record distinguishes "refused before execution" from "refused after partial execution". A record that omits the allow-path rule makes the permissive decisions unauditable.

The fixture ran against SQLite 3.45.1 under Python 3.12.3, and its temp-table behaviour differed from PostgreSQL's: `PRAGMA query_only` refused the temp-table create outright, while PostgreSQL documents temp-table writes as permitted inside a read-only transaction. That difference is the reason to state a guarantee per engine and per layer instead of writing "read-only" on the architecture diagram. The files are in the repository under `research/evidence/hyperprobe-readonly-debugging-agents-2026/` and the raw links resolve once the commit is published: [fixture_check.py](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/hyperprobe-readonly-debugging-agents-2026/fixture_check.py), the [envelope policy](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/hyperprobe-readonly-debugging-agents-2026/envelope.json), the [observed run record](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/hyperprobe-readonly-debugging-agents-2026/observed.json), and the [README with limits](https://raw.githubusercontent.com/baeseokjae/baeseokjae.github.io/main/research/evidence/hyperprobe-readonly-debugging-agents-2026/README.md). They contain only synthetic rows and an invented log fixture.

## HyperProbe as one implementation, with the vendor's claims attributed

HyperProbe is a YC S26 company that sells read-only probes for production services; its own documentation describes two workflows, placing and inspecting probes manually in VS Code, or letting an MCP-connected coding agent investigate an incident ([How It Works](https://docs.hyperprobe.co/how-it-works)). Its founders described the enforcement model in the [Launch HN thread](https://news.ycombinator.com/item?id=49185389), and their answer is a compact illustration of the layer problem. By default probes attach at a file, class, and line with metadata, which they describe as read-only and safe by default. Once a probe carries a condition, the guarantee becomes runtime-specific: on Node they rely on `throwOnSideEffect: true`; on Python and Java they do not permit method invocations in conditions at all and accept only a subset of comparison operators, with no assignment.

That restriction is the practical version of the getter problem. In the founder's own example, `total > 50` is permitted, `order.total > 50` is refused because a property access may run a getter that caches, logs, or writes, and `order.get_total() > 50` is refused under the ban on method invocations. Without a purity proof, denying property access as well as calls is the only way to keep a conditional probe read-only. The permitted operator subset is not enumerated in that thread, so treat it as "smaller than you assume" rather than as a specification.

On auditing, the founder's answer at launch was that an audit trail was on the roadmap and that probe-captured data could currently be deleted — while also raising the tension between immutable records and removing sensitive captured data. That is a point-in-time statement from the vendor, not a claim about the current build, and it is exactly the field-level gap the table above exists to catch: capture deletion and audit immutability have to be separate mechanisms, or the record is not evidence.

## Checklist before you hand an agent production read access

1. One credential per session, scoped to the database, service, and version in the envelope, expiring with the session.
2. `READ ONLY` (or the engine's equivalent) set as the default transaction mode for the agent's connection, not passed as an option the agent can omit.
3. Statement timeout and row cap enforced at the connection, not in the prompt.
4. Deny-by-default tool allowlist, with the tempting write tool present in the list and explicitly denied, so the refusal is a tested path rather than a missing feature.
5. Expression guard that refuses calls and assignments, tested against a getter and against an assignment.
6. `EXPLAIN` without `ANALYZE` in the observe set; `ANALYZE` classified as execution.
7. Capture redaction applied before the record is written, with the redaction events themselves recorded.
8. The thirteen audit fields present per call, including the allow-path rule and a pre-execution refusal marker.
9. A session cap on wall-clock time, call count, and captured bytes.
10. One off-switch that revokes the credential rather than asking the agent to stop.

Run items four and five against the real enforcement point and keep the output. A deny that was never exercised is a claim, and the difference between a claim and a control is one recorded refusal.

## FAQ

**Is read-only the same as safe?** No. Read-only bounds the operations, not the cost: an unbounded scan, a huge capture buffer, or an expensive regex over logs can degrade the system without writing anything. The envelope needs resource limits for the same reason it needs an operation list.

**Does `READ ONLY` prevent all writes?** Not in PostgreSQL's own words. The documentation calls it a high-level notion that does not prevent all writes to disk and permits writes into temporary tables, so treat it as the statement-class control it is and put the rest elsewhere.

**Is `throwOnSideEffect` a proof of purity?** No. It throws when a side effect cannot be ruled out, which is a conservative refusal test rather than a proof, and the parameter is experimental in the protocol listing.

**Can an audit trail coexist with deleting sensitive captures?** Yes, if they are different records. Keep the decision record and its digests immutable, and treat the captured payload as a separate, expiring artifact whose deletion is itself an audited event.

**Do I need a vendor to get this?** No. Two of the four layers are configurations you already own: a scoped credential and a read-only transaction mode. The work that a vendor adds is the runtime instrumentation and the MCP surface, and that is the part worth paying for only when in-process capture is what you actually need.

If the agent is only reading logs, metrics, and schemas over an API, the envelope is a policy file and a connection string. If you are further along in rollout, the wider controls sit next to this one: [agent security tooling](https://baeseokjae.github.io/posts/ai-agent-security-tools-2026/) covers the detection side, the [production go-live checklist](https://baeseokjae.github.io/posts/ai-agent-production-go-live-checklist-2026/) covers what has to be true before an agent touches production at all, and the [agentjacking mitigation guide](https://baeseokjae.github.io/posts/agentjacking-mitigation-guide-2026/) covers what happens when the agent can be steered by the content it reads.
