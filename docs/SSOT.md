# ADHD Authority and Index Boundary

## 1. Task Specification SSOT

For each task, the human-confirmed task specification is the SSOT for:

- the Agent's goal and selected scope;
- constraints, prohibitions, and risk boundaries;
- required behavior and acceptance criteria;
- referenced versions of long-term architecture and semantic rules.

The specification's form and required detail may vary with the selected
Global, Domain, Subsystem, Module, or lightweight documentation scope.

## 2. Long-term normative sources

- `docs/architecture/` records accepted structural rules and boundaries.
- `docs/semantic-specifications/` records accepted business and engineering
  behavior, scenarios, invariants, and verification requirements.
- `docs/decisions/` records accepted human decisions and amendments.

These sources become binding for a task through the task specification's fixed
references. A proposal is not a decision merely because it exists.

## 3. System Map

System Map is a long-maintained, actual-only architecture index. It helps Human,
Agent, and DDH locate components, relationships, impact closure, relevant
Context, and test candidates. It is not an SSOT, write authorization, risk
approval, or acceptance authority.

When a locally affected Map result is conflicted, incomplete, unavailable, or
not current enough for the query, DDH uses bounded live-source discovery for
that affected scope and schedules Map maintenance. The detailed fields,
statuses, APIs, and reconciliation mechanism remain open to revision while the
System Map design is unfinished.

## 4. Derived data

System Map query projections, generated schemas, test reports, Agent context,
runtime diagnostics, and UI state are derived data. They are not additional
SSOTs.

## 5. Conflict rule

- Current implementation fact: inspect live project assets.
- Task goal, scope, constraints, and completion: follow the fixed task
  specification.
- Accepted structural or behavioral rule: follow the version referenced by the
  task specification.
- A conflict requiring those human-confirmed boundaries to change requires a
  structured proposal and human decision before implementation continues.
