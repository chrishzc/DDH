# Phase 1 Authority Reconciliation Matrix

**Status:** Derived planning index／not implementation authority  
**Date:** 2026-08-02  
**Target draft:** `DDH-P1-SPEC-001`

This matrix prevents already-confirmed contracts from being reopened as
implementation questions. Accepted decisions outrank confirmed proposals;
later accepted amendments outrank earlier examples. System Map and discovery
metadata are never authority.

## Classification

| Class | Meaning |
|---|---|
| `confirmed` | Accepted authority or confirmed contract; compile, do not re-ask |
| `selected` | Human selected an implementation option for the Phase 1 draft |
| `superseded` | A later accepted decision replaces the listed part |
| `example-only` | Illustrative scenario; not a DDH product feature |
| `deferred` | Intentionally outside Phase 1 |
| `still-open` | A real decision remains and must not be guessed |

## Accepted Decision Projection

| Source | Phase 1 classification | Projection |
|---|---|---|
| Decision 0001 | `confirmed`＋`superseded` | Clean successor and legacy read-only remain; product name is superseded by Decision 0027 |
| Decision 0002 | `confirmed` | System Map is actual-only architecture index and never task authority |
| Decision 0003 | `confirmed` | Use role-oriented names without forcing one process／Agent per role |
| Decision 0004 | `confirmed` | Executable contracts precede runtime; Phase 0 remains the behavioral fixture base |
| Decision 0005 | `confirmed`＋`example-only` | L1 single-Agent vertical slice remains; original generic example replaced by Decision 0029 |
| Decision 0006 | `confirmed`／bounded subset | Phase 1 implements only routes required by the L1 flow and no-progress safety |
| Decision 0008 | `confirmed`／bounded subset | Minimum credible Test Auditor and layered verification; full portfolio lifecycle deferred |
| Decision 0013 | `confirmed` | Modular Python runtime、Ports／Adapters、tool-neutral Verification Assets |
| Decision 0014 | `confirmed` | Python 3.13 minimum; target runtime independent |
| Decision 0016 | `confirmed` | UTF-8 JSON Contract Envelope v1、strict parse、atomic publication |
| Decision 0017 | `confirmed` | Minimal typed references; no permanent provenance chain |
| Decision 0018 | `confirmed` | Tiered local Change Guard; mixed valid／invalid patch is not absorbed |
| Decision 0019 | `confirmed` | Capability-based System Map Consumer Port and bounded fallback |
| Decision 0020 | `confirmed` | Layered quality profiles and independent add-ons |
| Decision 0021 | `confirmed` | Six separate budgets and adaptive bootstrap behavior |
| Decision 0022 | `confirmed` | Windows 11／Ubuntu 24.04 and Python 3.13／latest-stable matrix |
| Decision 0025 | `confirmed` | One exact Task Specification confirmation; no per-gate approval |
| Decision 0026 | `confirmed boundary` | Phase 0 completed; it did not authorize Phase 1 |
| Decision 0027 | `confirmed amendment` | Product、package and CLI identity are DDH／`ddh` |
| Decision 0028 | `superseded history` | Initial Phase 1-only fixture amendment; superseded by Decision 0029 |
| Decision 0029 | `confirmed amendment` | Phase 0 v1.1.0 and Phase 1 both use the cross-platform workspace fixture projection |

## Confirmed Proposal Projection

| Contract／proposal | Compile into Phase 1 | Do not infer |
|---|---|---|
| `SPEC-WP-001` | Task Specification SSOT、readiness、single confirmation、revision boundary | Exact physical schema was not previously fixed |
| `DDH-RISK-001` | L1／L2 autonomous execution and L3 exception boundary | Report is not approval |
| Context Curator specification | bounded Context、purposeful grants、System Map index use | Context grant never adds write authority |
| Change Guard specification | baseline、delta、freeze、Patch Admission、stale rejection | Prompt／Git hook is not containment |
| Test Auditor specification | scenario traceability、anti-weakening、currentness | Test author cannot self-admit weakened acceptance |
| Verification Runner specification | immutable Subject、typed result、bounded output、cleanup | Free-form stdout is not verdict |
| `DDH-COMP-001` | Work Package completion only | No automatic Subsystem／Domain／release promotion |
| `DDH-OBS-001` | bounded telemetry、local health、short retention | Telemetry is not authority、Evidence or Memory |
| `DOM-OLE-001` | non-blocking terminal event boundary only | Full Learning Steward is deferred |

## Human-selected Phase 1 Implementation Projection

| Item | Selected projection | Authority effect |
|---|---|---|
| Agent integration | Host-pull Agent Driver Port | Does not trust Agent claims for admission or completion |
| Mutation result | Patch proposal or isolated Candidate only | Direct user-worktree mutation is prohibited |
| Candidate materialization | Disposable repository copy | Original dirty worktree remains untouched |
| Product surface | Python core＋thin CLI | Host UI／MCP reuses Ports later |
| Runtime state | Per-Invocation Atomic JSON | Ephemeral state, not Attempt Ledger |
| Specification form | Specification Package with JSON authority root | One package SSOT, not dual Markdown／JSON authorities |
| Confirmation | Local CLI＋typed Host UI／MCP channel | One valid channel confirms one exact digest |
| Candidate handoff | Portable Candidate Bundle | Bundle PASS is not apply／integration／release |
| Telemetry encoding | Bounded per-Invocation JSONL | Physical encoding of `DDH-OBS-001`; short-lived |
| Reference workload | Cross-platform path normalization workspace | Disposable fixture, not product functionality |

## Deferred from Phase 1

- Multi-Agent partition／join and L2 parallel runtime.
- Full Verification Asset portfolio lifecycle.
- Learning Analyzer、Critic、Memory Registry and self-evolution.
- System Map backend or schema implementation.
- Real provider Adapter、network、deployment、database、credential or release.
- Git worktree／virtual overlay Candidate backends.
- SQLite state store、daemon and production MCP Server.
- Candidate apply into the user's real worktree.

## Current Open-state Result

No unresolved architecture choice is known for drafting
`DDH-P1-SPEC-001`. Exact thresholds may be projected from Task Specification、
approved profiles and Decision 0021 bootstrap rules; they are not permission to
weaken required acceptance.

The next human authority event is one confirmation of the completed exact
Phase 1 Task Specification Package. That confirmation, not this matrix,
authorizes implementation.
