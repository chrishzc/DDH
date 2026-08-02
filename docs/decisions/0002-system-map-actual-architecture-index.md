# Decision 0002: System Map Is an Actual Architecture Index

- Status: Accepted
- Date: 2026-08-02
- Supersedes: the System Map authority statements in Decision 0001

## Decision

System Map is a long-maintained index of the project's **actual architecture**.
It is not an SSOT, task authority, write authorization, risk approval, or
acceptance authority.

For each task:

- the human-confirmed task specification is the SSOT for the Agent's goal,
  scope, constraints, required behavior, and completion criteria;
- live project assets are the evidence of the currently implemented state;
- System Map accelerates scope planning, impact analysis, Context selection,
  dependency traversal, test selection, and architecture visualization.

## Actual-only Active view

The Active System Map represents architecture that is evidenced as currently
implemented.

- An entity or relation that is only planned, proposed, or declared must not be
  presented as actual architecture.
- Proposed architecture may exist in a task specification, architecture
  proposal, or a separately identified UI overlay, but DDH must not consume it
  as the Active actual view.
- Agent-authored semantic details may supplement an observed entity only where
  the future System Map contract permits them. They cannot create an actual
  entity by declaration or override source-observed facts.
- DDH uses one published actual view. It does not maintain a second
  Agent-authored System Map as competing truth.

The exact evidence rules, authoring fields, resolver behavior, and publication
protocol remain part of the unfinished System Map design.

## Currentness and stale semantics

Currentness is local and evidence-bound, not a single project-wide freshness
claim.

System Map may need to distinguish, at the smallest useful scope:

- an observation or binding that is current enough for the requested query;
- an authored semantic detail whose supporting evidence has changed;
- an unresolved conflict between observed facts and authored semantics;
- a candidate update that has not entered the Active view;
- current observation that is unavailable or incomplete.

The exact status names, fields, state machine, timestamps, digests, and
reconciliation algorithm are deliberately not fixed by this decision.

This decision does not reintroduce legacy ADAD mechanisms such as:

- a global source-revision freshness chain;
- stable cross-version entity identity;
- a recurring human freshness checkpoint;
- a previous Bundle being treated as authority over current project assets.

## DDH consumer behavior

DDH may use a System Map result only as an index result:

1. Consume the published actual view, excluding proposals and declared-only
   overlays.
2. Treat locally conflicted, incomplete, or unavailable results as insufficient
   for that affected part of the query.
3. Use bounded live-source discovery as the fallback for the affected scope.
4. Record or schedule Map maintenance without allowing an index-tool failure to
   block otherwise safe implementation and verification.
5. Never use a System Map result to expand write scope, weaken acceptance, or
   approve an external side effect.

## Flexibility boundary

This decision fixes only the product meaning and DDH consumption boundary.
It does not freeze:

- Bundle or index schemas;
- enum and field names;
- source adapters or authoring interfaces;
- query language or service APIs;
- persistence, versioning, publication, or visualization technology;
- the detailed currentness and reconciliation implementation.

Those details may change as the separate System Map design is completed,
provided they preserve the decisions above.

