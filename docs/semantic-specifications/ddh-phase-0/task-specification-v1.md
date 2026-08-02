# DDH Phase 0 Task Specification v1.1.0

- Specification ID: `DDH-P0-SPEC-001`
- Status: Human-confirmed and authorized
- Confirmed date: 2026-08-02
- Authority: Decision 0026、Decision 0029 and the 2026-08-02 human directive
- Architecture scope: DDH MVP contract surface, Global level
- Risk class: L2 specification projection; L3 on semantic or architecture change
- External side effects: Prohibited

## 1. Agent Goal

Transform the accepted DDH architecture decisions and confirmed behavioral
contracts into a complete, internally consistent and reusable executable
contract fixture package from which Phase 1 runtime behavior and tool-neutral
Verification Assets can be implemented without guessing expected behavior.

## 2. Required Deliverables

1. A manifest of every MVP contract family and fixture asset.
2. Given／When／Then scenario catalogs for:
   - authority、Task Specification、Work Package and risk;
   - System Map consumption and bounded live-source fallback;
   - Context、parallel work、mutation mediation and candidate integrity;
   - Test Asset quality、verification execution and completion;
   - automatic recovery、learning intake and retention;
   - Phase 7A external high-risk simulation.
3. State tables for lifecycle-bearing local objects without creating a global
   Task lifecycle.
4. UTF-8 JSON Contract Envelope examples with valid and rejected outcomes.
5. L1 serial and L2 parallel end-to-end golden cases.
6. Contract → scenario → fixture → expected result traceability.
7. Deterministic, no-Agent validation of package structure and references.
8. A Phase 1 capability derivation showing which runtime capabilities each
   fixture will require.

## 3. Required Behavioral Coverage

Every applicable contract boundary must include:

- normal success;
- invalid input or rejection;
- stale／wrong subject／invalidation;
- safe automatic recovery;
- race／ordering／duplicate delivery;
- budget or bounded-resource behavior;
- expected mechanical result;
- authority source;
- fields and decisions automation cannot change.

The package must include full L1 single-Agent and L2 product／test parallel
flows, plus scope underestimation、test implementation defect、runner failure、
dirty worktree and external uncertain-result scenarios.

## 4. Allowed Writes

```text
docs/decisions/0026-phase-0-contract-fixture-package-authorization.md
docs/decisions/0029-phase-0-developer-tool-scenario-projection.md
docs/semantic-specifications/ddh-phase-0/**
docs/semantic-specifications/archive/ddh-phase-0/**
docs/semantic-specifications/README.md
docs/proposals/legacy_adad_capability_migration_matrix_and_ddh_mvp_plan.md
README.md
```

Existing accepted decisions and proposal contracts are read-only authority
inputs except for narrow status／cross-reference updates that do not alter
their semantics.

## 5. Prohibited Work

- No `src/`, runtime package, CLI, hook, daemon or scheduler.
- No System Map implementation, generated Bundle or schema redesign.
- No real mutation enforcement, Agent execution or provider connection.
- No credential, network, deployment, database or other external side effect.
- No legacy Frozen Task、Source Lock、Checkpoint、receipt or control plane.
- No copying legacy ADAD implementation.
- No lowering or inventing acceptance to close a fixture gap.

## 6. Source Priority

1. This Task Specification.
2. Accepted decisions `0001` through `0029`, with Decision 0029 superseding
   Decision 0028 as the current scenario-projection authority.
3. Confirmed contract proposals referenced by the fixture manifest.
4. Current architecture documents, subject to later amendments in accepted
   decisions.
5. Legacy ADAD snapshot only as read-only secondary capability evidence.

System Map is an actual architecture index and is not authority. Discovery
metadata、prompt constraints、Agent claims and proposal text without an accepted
decision cannot grant scope or acceptance.

## 7. Execution Model

The Main Agent retains the complete specification and integration authority.
Independent contract families may be authored in parallel when write zones do
not overlap. Shared envelope vocabulary、IDs、manifest and traceability are
centrally integrated.

Automatic correction is allowed for formatting、reference integrity、scenario
coverage and fixture consistency. If correction would change accepted
architecture or behavior, stop the affected lane and emit a structured
exception while continuing independent lanes.

## 8. Verification Profile

Required checks:

- strict UTF-8 JSON parsing;
- Contract Envelope field and version consistency;
- unique scenario／fixture IDs;
- every manifest asset exists;
- every fixture points to an existing scenario and contract;
- every scenario has an expected mechanical outcome;
- every required contract family covers success and rejection;
- cross-file references contain no absolute paths or secrets;
- L1 and L2 golden flows are complete and ordered;
- no prohibited legacy mechanism appears as an active requirement;
- no external simulator fixture can represent a real external write.

## 9. Budgets

- Agent work: bounded to the complete Phase 0 package.
- Context: load only the contract family currently authored plus shared
  vocabulary; Main Agent retains global integration context.
- Verification: deterministic local validation only.
- Recovery: formatting and reference failures may be repaired autonomously.
- Stress: validate at least 10,000 synthetic fixture references conceptually
  through bounded deterministic test design; do not generate permanent
  10,000-item artifacts.
- External budget: zero.

## 10. Completion

Phase 0 is complete only when:

1. every MVP contract family is represented in the manifest;
2. required normal、rejection、stale、recovery and race coverage is traceable;
3. L1 and L2 end-to-end golden cases are complete;
4. Phase 7A simulator cases cover approval drift and uncertain reconciliation;
5. package validation is deterministic and passes without an Agent;
6. no unresolved exception changes accepted semantics;
7. the Phase 1 capability derivation is complete.

Completion does not authorize Phase 1.
