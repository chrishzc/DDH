# DDH Phase 1 CLI

The Phase 1 CLI is intentionally thin. Runtime orchestration remains a Python
core with typed Ports; the CLI provides the always-available offline human
confirmation channel.

## Run without installation

Python 3.13 or newer is required.

```powershell
$env:PYTHONPATH = (Resolve-Path src)
py -3 -m ddh.cli specification-digest C:\path\to\workload-specification.json
```

DDH itself has no third-party runtime dependency. Packaging tools are not
downloaded or installed as automatic recovery.

## Inspect a workload specification digest

```powershell
py -3 -m ddh.cli specification-digest C:\path\to\workload-specification.json
```

The command performs strict UTF-8 JSON parsing and prints the exact authority
identity and SHA-256 content digest. It does not confirm or execute the
workload.

## Confirm one exact workload specification

```powershell
py -3 -m ddh.cli confirm C:\path\to\workload-specification.json `
  --record C:\trusted-ddh-authority\confirmation.json
```

The command requires an interactive terminal and asks the human to type the
exact specification ID、version and digest. The record path must be outside
Agent-writable scope. Confirmation is not a legacy Checkpoint or permanent
approval chain.

## Host integration

Hosts embed `ddh.runtime.Phase1Runtime` and provide typed implementations of:

- `SystemMapPort`;
- `LiveSourceFallbackPort`;
- `AgentDriverPort`;
- `ContextSourcePort`;
- `IsolatedCandidateCapabilityPort` when that optional mutation mode is used;
- `VerificationAssetProvider`.

Agent work is host-pull. Agent results are untrusted proposals and cannot
declare PASS、completion、scope expansion or higher-layer state.

## Safety boundaries

- Original user workspaces are never modified.
- Candidate changes land only in disposable copies.
- Generic shell executors are rejected.
- Verification executes through direct argv in a disposable runner workspace.
- Candidate Bundles are not automatically applied.
- No network、credential、database、deployment、publication or release
  operation is implemented in Phase 1.

## Local verification

No third-party test dependency is required:

```powershell
$env:PYTHONPATH = (Resolve-Path src)
py -3 -m unittest discover -s tests -v
```

The package also exposes a pytest adapter for target projects that already
provide pytest. DDH does not install pytest automatically.

The required Windows 11 profile uses a self-hosted runner labelled
`ddh-windows-11`; GitHub-hosted `windows-2022` is compatibility evidence only.
Because the repository is public, the self-hosted job runs only when repository
owner `chrishzc` manually dispatches the workflow and opts into
`run_windows_11`. The runner should remain offline at all other times.
