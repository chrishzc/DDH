# Portable Workspace Reference Fixture

## Purpose

Provide a disposable developer-tool-native target repository that exercises
the complete Phase 1 L1 flow without adding target-domain features to DDH.

## Target Modules

### PathNormalizer

Input:

```text
workspace root
user-provided path
platform profile
```

Output:

```text
repository-relative canonical path
or typed rejection
```

Required behavior:

- `src\package\module.py` becomes `src/package/module.py`.
- `./src/package/../package/module.py` becomes
  `src/package/module.py`.
- `../secrets.txt` is rejected as `workspace_escape`.
- a Windows absolute path is rejected as `absolute_path_prohibited`.
- a UNC path is rejected as `unsupported_path_class`.
- canonicalization cannot traverse a symlink／junction escape.

### ManifestLoader

`ManifestLoader` consumes the canonical path and loads the referenced fixture
manifest. It is a read-only downstream dependency for the primary Work
Package.

The primary Agent may not modify `ManifestLoader`. Actual impact may add its
regression suite to verification closure. If satisfying the specification
truly requires changing it, the runtime must emit `scope_change_required`.

## Workload Write Boundary

```text
product write:
  src/path_normalizer.py

Verification Asset proposal:
  tests/candidate/**

read-only:
  src/manifest_loader.py
  tests/acceptance/**
  task-specification-package/**
  system-map-fixture/**

protected dirty resource:
  notes/user-local-change.txt
```

The dirty resource exists before DDH starts and must remain byte-identical in
the original workspace and semantically preserved in the Candidate baseline.

## System Map Fixture

The actual-only index describes:

```text
PortableWorkspace subsystem
├─ PathNormalizer module
└─ ManifestLoader module
   └─ depends on PathNormalizer canonical path contract
```

It supports branch／commit／view binding、direct dependency、reverse dependency
and resource resolution. An incomplete／unavailable variant forces bounded
live-source fallback. The fixture does not define the production System Map
schema or backend.

## Pre-seeded Defects

- Windows separators are not normalized.
- parent traversal can escape the workspace.
- `ManifestLoader` assumes canonical separators.

The accepted repair must remain inside the authorized product Module. The
downstream assumption is verified, not silently rewritten.

## Stress and Reliability Workloads

- 10,000 duplicate／late／out-of-order Agent Result references.
- 10,000 unrelated dirty-file manifest records without copying them into Agent
  Context.
- Context Request storm with duplicate and irrelevant selectors.
- bounded large patch and diagnostic output.
- Candidate churn with stale result submission.
- Agent timeout and process-tree cleanup.
- System Map unavailable with bounded fallback.
- Windows／Ubuntu canonical verdict parity.

Large conceptual inputs may be generated in memory; permanent 10,000-item
fixture corpora are not required.

