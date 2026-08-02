# Authority, Scope and Risk Contract Family

- Package: `DDH-P0-SPEC-001` version `1.1.0`
- Contract family: `P0-AUTH-SCOPE-RISK`
- Status: Phase 0 executable specification projection
- Runtime authority: None

## 1. Purpose

This family defines the mechanical outcomes required when DDH:

- checks whether a Task Specification is ready for human confirmation;
- admits an exact human-confirmed Task Specification;
- derives and regenerates a Work Package Projection;
- classifies change authority independently from verification intensity;
- consumes the System Map through the capability-based consumer port;
- uses bounded live-source fallback without treating discovered facts as
  authority; and
- stops only the affected work when accepted authority is insufficient.

The family projects `SPEC-WP-001`, `DDH-RISK-001`, Decision 0019 and Decision
0025. It does not define a System Map schema or backend and does not create a
global Task lifecycle.

## 2. Authority Model

### 2.1 Task Specification

An exact human-confirmed Task Specification version is the task authority.
Readiness requires enough expected behavior to derive executable acceptance;
document length and field-count completeness are not readiness criteria.

The following sources cannot confirm or expand a Task Specification:

- Main Agent output;
- Work Package Projection;
- System Map facts;
- discovery metadata;
- prompt instructions;
- source code, tests or execution evidence; and
- orchestration memory or telemetry.

For L0, an explicit human request containing the goal, prohibition and
lightweight confirmation can be the minimal confirmed Task Specification. L1
and L2 require one confirmation of an exact version. L3 requires the relevant
human authority decision first and then a confirmed Task Specification that
references it.

### 2.2 Human authority roles

| Authority source | Exclusive authority-bearing fields |
|---|---|
| Demand Owner | goal, observable behavior, task scope, prohibitions, acceptance and task budget |
| Architecture Owner | architecture responsibility, schema, public or cross-domain contract and L3 architecture boundary |
| Profile Policy Owner | versioned project defaults for risk, quality, timeout, budget and retention |
| External Authority Owner | exact real provider, target and external operation plan |
| Main Agent | no confirmation authority; may draft, check readiness, project and report exceptions |
| Mechanical DDH component | no specification authority; may enforce, classify, validate and judge fixed inputs |

One human may hold several authority roles. The role labels distinguish the
source of a decision; they do not require a committee or a fixed approval
chain.

## 3. Task Specification Readiness

Readiness has these mechanical outcomes:

| Outcome | Meaning |
|---|---|
| `ready_for_confirmation` | Required expected behavior is explicit enough to produce executable acceptance. This does not authorize work. |
| `confirmed_ready` | The exact ready version was confirmed by the applicable human authority. |
| `specification_not_ready` | A business outcome, authority-bearing field or applicable layer requirement is missing or contradictory. |
| `authority_reference_missing` | An L3 or external requirement lacks the separately required authority decision. |
| `superseded` | A newer human-confirmed version replaces this version for new projections. |

After `confirmed_ready`, authority-bearing fields are immutable for that
version. Any change to goal, behavior, scope, prohibition, acceptance, risk
policy, budget ceiling or external permission requires a new human-confirmed
version. Current paths, System Map node resolution, Context selection,
partitioning, runner placement, retry ordering and bounded fallback do not.

## 4. Work Package Projection

A Work Package Projection is derived from:

```text
exact confirmed Task Specification
+ fixed project profile versions
+ current repository/candidate identity
+ actual System Map query results
+ bounded live-source facts when required
+ current execution capabilities
```

The projection contains resolved nodes and resources, read/write boundaries,
prohibitions, risk and verification profiles, budget allocation, candidate
identity, partitions, Context references, runner profile, recovery routes and
human escalation conditions.

The projection:

- cannot add write scope, weaken acceptance or increase a budget ceiling;
- cannot become a second task authority;
- can be regenerated automatically when authority fields are unchanged;
- is invalidated by a different Task Specification identity/digest, candidate
  generation, repository identity, resolved commit or relevant profile
  version; and
- must preserve the exact authority sources used to derive it.

Safe regeneration reasons include Context expansion, partition change,
parallel-to-serial fallback, runner recovery, test ordering, candidate rebuild
and System Map-to-live-source fallback.

## 5. Change Authority and Verification

Change authority and verification intensity are independent axes.

| Class | Authority boundary | Mechanical route |
|---|---|---|
| L0 | Non-behavioral documentation or non-governance assets | Direct work under minimal confirmed intent and lightweight verification; reclassify before behavioral or governance mutation |
| L1 | One primary node within existing contracts; reversible, bounded and no shared multi-writer integration | Autonomous local implementation and verification after confirmation |
| L2 | Multiple nodes, parallel work, shared integration or large internal refactor within existing contracts | Autonomous coordinated execution with stronger mediation and integration verification |
| L3 | Architecture, schema, public/data contract, expected behavior, scope expansion, permission/risk policy, budget increase, irreversible or real external operation | Stop affected work and request the applicable human authority |

An L1 projection may strengthen automatically to L2 when actual impact remains
inside confirmed scope and contracts. Neither an Agent nor memory, telemetry,
System Map or a cost signal may lower the class. High-assurance verification
may apply to an L1 change; strong verification does not grant additional write
authority.

Unknown verification risk selects stronger verification. Unknown permission or
authority stops affected work.

## 6. System Map Consumer Port

DDH consumes normalized capabilities, not a fixed System Map schema, enum,
storage engine or API:

1. resolve a human-selected Global, Domain, Subsystem or Module scope to nodes;
2. query ancestors and architecture level;
3. query direct dependencies and direct reverse dependencies;
4. map source, schema and configuration resources to nodes;
5. report coverage, omission and local currentness for the query; and
6. bind the result to repository, requested ref, resolved commit, applicable
   candidate/worktree and System Map view identity.

Normalized outcomes are:

- `usable_actual`
- `partial`
- `conflicted`
- `view_mismatch`
- `unavailable`
- `impact_unknown`

System Map results are actual-architecture evidence only. They cannot grant
scope, risk, acceptance, Verification Asset selection, completion or external
authority.

### 6.1 Required consumption

When applicable, a query must be triggered and materially consumed during:

- initial scope resolution;
- parallel partitioning and Context materialization;
- actual-delta reconciliation;
- join and candidate freeze;
- Verification Asset selection;
- failure repair; and
- completion evaluation.

Material consumption means the downstream projection records the query
identity and the nodes or relations actually used. Merely issuing a query is
not sufficient.

### 6.2 Bounded fallback

For `partial`, `conflicted`, `view_mismatch` or `unavailable`, live-source
fallback is limited to the affected area. A candidate uses:

```text
baseline actual view
+ actual candidate delta
+ resource-to-node binding
+ bounded live-source discovery for the changed area
```

Fallback may resolve facts and expand the verification closure, but it cannot
expand write authority. If the bounded fallback still yields
`impact_unknown`, impact closure and any dependent completion claim are
rejected. Planned or declared-only relationships never enter the actual
closure.

## 7. Ordering, Race and Recovery Rules

1. Projection admission compares exact Task Specification identity and digest,
   candidate identity, repository identity and relevant profile versions.
2. If a specification revision wins concurrently with admission, the older
   projection is invalidated before it can authorize a write.
3. Concurrent queries for different resolved commits or branches remain
   isolated; facts cannot be merged by branch name alone.
4. Querying another branch is read-only and must not checkout, switch or modify
   the current worktree.
5. A runner, Context, partition or System Map adapter failure may regenerate
   the projection without human confirmation when authority fields remain
   fixed.
6. A required scope expansion, business outcome, contract change, permission
   or budget increase stops only the affected lane and produces a structured
   exception. Unaffected safe lanes may continue.
7. Duplicate projections or query deliveries are idempotent by exact identity;
   a conflicting duplicate is rejected rather than merged.

## 8. Budget Boundaries

- Projection regeneration consumes the fixed task budget; it cannot increase
  the budget ceiling.
- Context expansion and live fallback must remain bounded to the affected
  closure.
- Large-Domain queries place only bounded summaries and needed Q0/Q1 facts into
  Agent Context.
- Exhausting the accepted budget stops the affected lane with preserved
  candidate state and a structured exception; the Main Agent cannot grant more
  budget.
- Deterministic reference validation must be capable of streaming at least
  10,000 logical references without requiring a permanent 10,000-item fixture
  file or Agent execution.

## 9. Required Structured Exception

An authority exception includes:

```text
current Task Specification identity and clause
current and proposed authority class
blocked lane or transition
trigger and observed evidence
actual affected nodes and contracts
System Map query and bounded live-source confirmation
safe actions attempted
preserved candidate or diff
requested authority change
verification, budget and external impact
options and tradeoffs
unaffected work that can continue
```

The report is not approval.

## 10. Fixture Coverage

The executable examples are in
`fixtures/authority-scope-and-risk.json`. They cover:

- normal L0, L1 and L2 admission;
- readiness and non-authoritative-source rejection;
- stale specification, projection and System Map views;
- automatic projection and fallback recovery;
- specification/admission and multi-branch query races;
- budget exhaustion and bounded large-Domain Context;
- L1-to-L2 strengthening and L3 affected-lane stop; and
- System Map consumption without granting write authority.

The normative transition constraints are projected in
`state-tables/authority-work-package-and-risk.md`.
