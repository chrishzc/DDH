# Phase 6 Runtime Requirements

## Three-layer intake

Each execution run with attempts owns one immutable, seal-once Individual
Attempt Ledger capped at 64 KiB. It contains only bounded orchestration facts:
execution/spec/scope/risk/profile identities, Agent/template/Context versions,
partition/generation, attempt sequence, cost, failure fingerprint, recovery
route, new-information signal, priority, and terminal outcome.

It excludes prompts, conversations, chain of thought, source diff/workspace
copy, unbounded output, repeated tracebacks, secrets, credentials, and
unsupported Agent opinions. It is neither acceptance evidence nor an audit log.

Every sealed Ledger first runs a zero-Agent deterministic prefilter. Routine
success and one-off product/test defects are consumed and deleted; known
patterns update bounded support then delete; orchestration signals atomically
fold into a Learning Candidate before the source Ledger is deleted. Crash
replay is idempotent and cannot double-count support.

Learning Candidates contain normalized pattern, applicability, support and
counterevidence counts, cost summary, priority, and minimal examples. They are
not compressed Ledger archives. Long-term Memory is self-contained and never
depends on deleted raw material.

## Trigger and retention profile

P0 schedules one unsafe mutation/recovery/permission/scope or evolution
regression signal after the current mutation transaction is safe. P1 triggers
at two comparable occurrences or one hour. P2 triggers across at least two Work
Packages and three occurrences, or daily idle batch. P3 triggers at five
occurrences and receives no dedicated model call below threshold.

Individual Ledger fold/delete deadline is at most 24 hours after successful
fold. Outage upper bounds are P3 24 hours, P2 72 hours, P1 7 days, P0 14 days.
Learning Candidate maximum ages are P3 7 days, P2 14 days, P1 30 days, P0 90
days. Every candidate ends promoted, known-no-change, rejected,
insufficient-evidence, superseded, or `analysis_expired_without_memory_change`
and is deleted with temporary trial artifacts.

## Memory and controlled evolution

Long-term Memory is limited to parallelization/partitioning, initial/expanded
Context, Agent/tool profile, integration/handoff ordering, approved recovery
ordering, summary/Context templates, and parallel-to-serial fallback. Every
version carries applicability, recommendation, prohibited uses,
support/counterevidence, confidence, profile compatibility, expiry, conflict,
and rollback data.

Only the Main Agent receives bounded Guidance Cards at approved orchestration
transitions. Child Agents cannot read the Store. Store unavailable falls back
to single main Agent, bounded initial Context, and no optional parallelism.

Promotion requires separated Analyzer, independent Critic, offline replay,
shadow evaluation, bounded low-risk canary, metric improvement,
counterexample handling, reproducibility, and rollback readiness. Candidate
authors cannot publish, change replay corpus, expected metrics, or trial
results. Regression suspends/rolls back only orchestration Memory and never
product source, tests, Candidate, user diff, or completion.

