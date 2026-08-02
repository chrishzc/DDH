# Phase 0 Shared Contract Vocabulary

This vocabulary is package-local. It standardizes fixture language without
creating DDH runtime enums.

## Authority Terms

| Term | Meaning |
|---|---|
| `task_specification` | Human-confirmed task behavior and acceptance SSOT |
| `work_package_projection` | Rebuildable execution envelope derived from the task specification |
| `architecture_reference` | Accepted structural decision fixed by the task specification |
| `system_map_view` | Actual-only architecture index result; never authority |
| `external_operation_plan` | Exact high-risk plan requiring separate authority |

## Identity Terms

| Term | Prevents |
|---|---|
| `specification_version` | Absorbing work against changed behavior |
| `projection_generation` | Absorbing stale execution planning |
| `candidate_digest` | Verifying the wrong product／test snapshot |
| `partition_generation` | Accepting late or superseded writers |
| `invocation_id` | Confusing duplicate or reordered tool results |

Identity is minimal and typed. These terms do not recreate permanent
cross-version provenance.

## Mechanical Outcome Terms

| Outcome | Meaning |
|---|---|
| `accepted` | Input is valid for the current local transition |
| `rejected` | Input violates a fixed contract or boundary |
| `not_ready` | Required material is missing but no authority change is implied |
| `stale` | Input is well-formed but bound to an older version／generation／subject |
| `blocked` | Safe continuation is unavailable within current policy |
| `retry_safe` | A fixed route proves retry cannot add unintended effects |
| `recovery_required` | Fixed automatic recovery must run before reevaluation |
| `human_decision_required` | Continuing would change an authority-bearing field |
| `incomplete` | Required evaluation did not produce a terminal outcome |
| `not_applicable` | A dimension is explicitly inapplicable, not silently omitted |

## Required Scenario Shape

Every fixture scenario contains:

```text
scenario_id
contract_refs
given
when
expected
authority_source
immutable_fields
```

- `given` contains observed or fixed preconditions.
- `when` contains one event or transition.
- `expected` contains machine-observable outcome and next action.
- `authority_source` identifies the specification or accepted decision.
- `immutable_fields` names values automation cannot change to obtain success.

## Forbidden Authority Substitutions

The following can supply facts or advice but never authority:

- System Map or discovery metadata;
- source code or tests by themselves;
- prompt instructions without enforcement;
- Agent claims;
- historical PASS output;
- Attempt Ledger or long-term orchestration Memory;
- tool availability or credentials discovered at runtime.

