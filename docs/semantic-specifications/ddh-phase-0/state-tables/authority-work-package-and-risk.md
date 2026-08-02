# Authority, Work Package and Risk State Tables

- Package: `DDH-P0-SPEC-001` version `1.1.0`
- Contract family: `P0-AUTH-SCOPE-RISK`
- Runtime authority: None

These tables describe lifecycle-bearing local objects. They do not create a
global Task lifecycle, a Frozen Task, a Checkpoint or a control plane.

## 1. Task Specification Version

Each row applies to one immutable specification version.

| Current state | Event | Guard | Next state | Mechanical result |
|---|---|---|---|---|
| `draft` | readiness check | Expected behavior and applicable layer requirements are explicit and consistent | `ready_for_confirmation` | Emit readiness result; no execution authority |
| `draft` | readiness check | Business outcome, authority field or layer requirement is missing/contradictory | `readiness_blocked` | Emit `specification_not_ready` with exact gaps |
| `readiness_blocked` | corrected draft checked | All gaps resolved without claiming confirmation | `ready_for_confirmation` | Emit a new draft digest; no execution authority |
| `ready_for_confirmation` | exact human confirmation | Applicable human authority confirms identity and digest | `confirmed_ready` | Version becomes immutable and may be projected |
| `ready_for_confirmation` | Agent, prompt, System Map, metadata or test claims confirmation | Source is not human authority | `ready_for_confirmation` | Reject admission |
| `confirmed_ready` | authority-bearing field change requested | Any goal, behavior, scope, prohibition, acceptance, risk, budget ceiling or permission changes | `confirmed_ready` | Preserve version; require a new draft/version |
| `confirmed_ready` | newer version confirmed | New version has applicable human authority | `superseded` | Reject new projection admission from old version |
| `superseded` | existing candidate evaluation | Candidate was validly admitted before supersession | `superseded` | Reconcile affected projection/candidate; never silently re-authorize |

## 2. Work Package Projection Generation

| Current state | Event | Guard | Next state | Mechanical result |
|---|---|---|---|---|
| `absent` | generate | Exact Task Specification is `confirmed_ready` and inputs are identifiable | `generated` | Derive bounded execution envelope |
| `absent` | generate | Specification unconfirmed, superseded or missing required authority | `blocked` | Reject with authority/readiness reason |
| `generated` | boundary validation | Projection is a subset of confirmed scope, acceptance is unchanged and budget is within ceiling | `admitted` | Allow only represented local execution |
| `generated` | boundary validation | Projection expands write scope, weakens acceptance or increases budget | `blocked` | Reject projection; preserve specification |
| `admitted` | safe operational change | Context, partition, runner, ordering, fallback or candidate generation changes without authority change | `invalidated` | Stop using old generation and request regeneration |
| `invalidated` | regenerate | Exact authority still current and new operational inputs are bounded | `generated` | Create a new generation without human confirmation |
| `admitted` | authority version/digest changes | New or conflicting authority becomes current | `invalidated` | Prevent further writes under old generation |
| `admitted` | duplicate delivery | Exact projection identity and digest match | `admitted` | Idempotent no-op |
| `admitted` | conflicting duplicate | Same logical identity has a different digest | `blocked` | Reject both as a conflict pending canonical resolution |
| `admitted` | accepted budget exhausted | No accepted automatic route remains within ceiling | `blocked` | Preserve candidate and emit structured exception |

## 3. System Map Query Consumption

| Current state | Event | Guard | Next state | Mechanical result |
|---|---|---|---|---|
| `not_requested` | applicable scope/impact transition | Query purpose and bounded depth are known | `requested` | Bind request to repository, ref, resolved commit and view |
| `requested` | result received | Outcome is `usable_actual` and binding matches | `usable` | Make actual nodes/relations available for explicit consumption |
| `requested` | result received | Outcome is partial/conflicted/view-mismatch/unavailable | `fallback_required` | Limit fallback to affected area |
| `requested` | result received | Binding is stale or wrong-subject | `rejected` | Do not consume facts; re-query correct subject |
| `fallback_required` | bounded live discovery | Actual closure is resolved | `usable` | Record Map result plus live facts and affected area |
| `fallback_required` | bounded live discovery | Closure remains unknown | `impact_unknown` | Block impact-complete and dependent completion claims |
| `usable` | downstream projection records used facts | Query identity and consumed nodes/relations are recorded | `consumed` | Permit dependent calculation, subject to other authority |
| `usable` | completion evaluation | No downstream consumption record exists | `rejected` | Reject impact-complete claim |
| `consumed` | resolved commit/candidate/view changes | Binding no longer matches | `stale` | Invalidate dependent projection and re-query |
| `stale` | correct bounded re-query succeeds | New result is usable and explicitly consumed | `consumed` | Replace old consumption; never merge incompatible facts |

## 4. Risk Classification for an Affected Lane

Risk classification is recomputed from canonical facts. Verification profile
selection is recorded separately.

| Current class | Observed fact | Next class/route | Mechanical result |
|---|---|---|---|
| L0 | Only confirmed non-behavioral work is touched | L0 | Continue with lightweight verification |
| L0 | Runtime behavior, governance asset, contract or external effect is touched | Reclassify | Stop the mutation until L1/L2/L3 classification succeeds |
| L1 | More authorized nodes require coordination but contracts, scope and permissions remain fixed | L2 | Strengthen mediation and verification automatically |
| L1 or L2 | Higher business criticality or unknown verification risk | Same authority class plus stronger verification | Add verification only; do not grant writes |
| L1 or L2 | Architecture/schema/public contract/expected behavior/write scope/permission/budget must change | L3 affected-lane stop | Preserve candidate and emit structured exception |
| Any | Agent, memory, telemetry or System Map requests downgrade | Unchanged | Reject downgrade source |
| Any | Canonical facts prove a different class | Deterministically recomputed class | New projection generation; acceptance cannot be weakened |
| L3 stop | Applicable human decision and new Task Specification are confirmed | Reclassify from new canonical inputs | Does not by itself authorize a real external operation |

## 5. Race Resolution

| Race | Winner rule | Losing input treatment |
|---|---|---|
| Old projection admission vs newly confirmed Task Specification | Canonical confirmed specification version at admission commit | Old projection becomes invalid and cannot authorize a write |
| Same branch name with different resolved commits | Exact resolved commit and view identity | Old query becomes stale |
| Concurrent queries for two branches | Repository + requested ref + resolved commit + view tuple | Results remain isolated; no cross-branch merge |
| Duplicate projection delivery | Exact identity + digest | Matching duplicate is idempotent; mismatch is rejected |
| Candidate delta vs baseline Map publication | Actual candidate identity and delta at evaluation | Reconcile bounded changed area; do not treat planned facts as actual |
| Budget exhaustion vs automatic recovery | Already accepted budget accounting | Recovery may finish only if it stays within the accepted ceiling |

## 6. Recovery Boundaries

Automatic recovery may:

- rebuild a projection;
- expand bounded Context;
- serialize parallel work;
- change an approved runner/tool route;
- re-query or use bounded live-source fallback;
- rebuild a candidate; and
- strengthen L1 to L2 coordination.

Automatic recovery may not:

- invent missing expected behavior;
- change a confirmed authority field;
- add write scope or an external side effect;
- lower verification or risk;
- increase the accepted budget ceiling; or
- treat System Map facts as permission.

When automatic routes are exhausted, only the affected lane is blocked. The
exception preserves the candidate/diff and identifies unaffected work that can
continue.
