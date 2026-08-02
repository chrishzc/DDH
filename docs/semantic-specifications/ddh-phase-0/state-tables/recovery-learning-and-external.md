# Recovery, Learning, and External Local State Tables

These are local object lifecycles. They do not form a global Task state
machine.

## Recovery Route

| Current fact | Guard | Next action | Forbidden shortcut |
|---|---|---|---|
| `tool_backend_unavailable` | approved alternate exists | rebuild projection and retry same subject | edit product／acceptance |
| `same_failure_no_new_evidence` | same fingerprint and hypothesis | choose different diagnosis or stop | repeat identical attempt |
| `impact_underestimated` | verification-only expansion | extend closure and tests | grant write scope |
| `impact_underestimated` | outside-scope repair required | structured scope revision | hidden outside-scope write |
| `budget_exhausted` | no approved reserve | preserve and report | lower tests or extend budget |

## Individual Ledger and Learning Candidate

| Object | Current | Event | Next |
|---|---|---|---|
| Ledger | `sealed` | routine prefilter | `consumed → deleted` |
| Ledger | `sealed` | known pattern | support update → `deleted` |
| Ledger | `sealed` | orchestration signal | atomic candidate fold → `deleted` |
| Candidate | `pending` | Analyzer／Critic accepted | Memory version published → `deleted` |
| Candidate | `pending` | rejected／insufficient／superseded | terminal disposition → `deleted` |
| Candidate | `pending` | maximum age | `analysis_expired_without_memory_change → deleted` |

## External Operation

| Current | Event | Guard | Next |
|---|---|---|---|
| `draft` | preflight passes | exact identities complete | `approval_required` |
| `approval_required` | human approves | exact plan digest | `approved` |
| `approved` | any identity drifts | none | `approval_required` |
| `approved` | Trusted Executor starts | Adapter capability valid | `executing` |
| `executing` | observed postcondition | target matches | `succeeded` |
| `executing` | request outcome unknown | retry safety unproven | `uncertain` |
| `uncertain` | reconciliation proves state | current target observed | `succeeded` or `not_executed` |
| `uncertain` | state cannot be proven | none | `human_decision_required` |

