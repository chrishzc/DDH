from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = PACKAGE_ROOT.parents[3]
MANIFEST_PATH = PACKAGE_ROOT / "manifest.json"
SPECIFICATION = "DDH-P4-SPEC-001@1.0.0"
GROUPS = {
    "asset_catalog", "admission_and_non_bypass", "lifecycle_and_exceptions",
    "anti_weakening", "currentness_and_invalidation", "layered_quality_and_cost",
    "evidence_and_completion",
}


def reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_json(path: Path) -> Any:
    return json.loads(path.read_bytes().decode("utf-8"), object_pairs_hook=reject_duplicate_keys)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def closure(digests: dict[str, str]) -> str:
    return hashlib.sha256("\n".join(f"{p}:{digests[p]}" for p in sorted(digests)).encode()).hexdigest()


def validate_manifest(manifest: dict[str, Any], errors: list[str]) -> dict[str, str]:
    expected = {
        "specification_id": "DDH-P4-SPEC-001", "version": "1.0.0",
        "status": "ready_for_confirmation",
        "implementation_authority": "none_until_exact_human_confirmation",
        "external_side_effect_budget": 0,
        "catalog_authority": "rebuildable_discovery_index_only",
        "system_map_authority": "actual_architecture_index_not_ssot",
    }
    for field, value in expected.items():
        if manifest.get(field) != value:
            errors.append(f"manifest {field} must be {value}")
    if manifest.get("confirmation", {}).get("confirmed") is not False:
        errors.append("draft confirmation must remain false")
    if manifest.get("completion_claim") != "phase4_specification_package_only":
        errors.append("package must not claim runtime completion")
    assets = manifest.get("assets", [])
    if len(assets) != 8:
        errors.append("manifest must contain exactly eight closure assets")
    results: dict[str, str] = {}
    for asset in assets:
        rel = asset.get("path")
        if not isinstance(rel, str) or not rel or Path(rel).is_absolute() or ".." in Path(rel).parts:
            errors.append("manifest has invalid closure asset path")
            continue
        path = PACKAGE_ROOT / rel
        if not path.is_file():
            errors.append(f"missing asset: {rel}")
            continue
        actual = digest(path)
        results[rel] = actual
        if actual != asset.get("sha256"):
            errors.append(f"asset digest mismatch: {rel}")
    if closure(results) != manifest.get("closure_digest"):
        errors.append("closure digest mismatch")
    return results


def validate_acceptance(errors: list[str]) -> int:
    catalog = load_json(PACKAGE_ROOT / "acceptance-scenarios.json")
    scenarios = catalog.get("scenarios", [])
    ids = [item.get("scenario_id") for item in scenarios]
    if catalog.get("specification") != SPECIFICATION:
        errors.append("acceptance specification mismatch")
    if len(ids) != len(set(ids)):
        errors.append("scenario IDs must be unique")
    required = {"scenario_id", "capability_group", "class", "given", "when", "expected"}
    observed: set[str] = set()
    for index, item in enumerate(scenarios):
        missing = required - item.keys()
        if missing:
            errors.append(f"scenario {index} missing fields: {sorted(missing)}")
        if isinstance(item.get("capability_group"), str):
            observed.add(item["capability_group"])
    if len(scenarios) < 25:
        errors.append("at least 25 acceptance scenarios are required")
    if set(catalog.get("required_capability_groups", [])) != GROUPS or not GROUPS.issubset(observed):
        errors.append("required capability groups are incomplete")
    return len(scenarios)


def validate_snapshot(errors: list[str]) -> int:
    snapshot = load_json(PACKAGE_ROOT / "phase3-source-snapshot.json")
    if snapshot.get("snapshot_kind") != "committed_phase3_baseline" or snapshot.get("commit_identity") != "529eef0c13a8a0df4f135a7fca6142bc2e0a739d":
        errors.append("Phase 3 baseline must bind the committed Phase 3 reference")
    if snapshot.get("phase3_specification") != "DDH-P3-SPEC-001@1.0.0":
        errors.append("Phase 3 specification identity mismatch")
    if snapshot.get("phase3_closure_digest") != "8add85a45d96bdbc8b158405d87c510efcbe3403639c036034d8f83584053a00":
        errors.append("Phase 3 closure digest mismatch")
    files = snapshot.get("files", [])
    if len(files) < 10:
        errors.append("Phase 3 snapshot is incomplete")
    for item in files:
        path = REPOSITORY_ROOT / item.get("path", "")
        if not path.is_file() or digest(path) != item.get("sha256"):
            errors.append(f"Phase 3 snapshot mismatch: {item.get('path')}")
    return len(files)


def validate_content(errors: list[str]) -> None:
    model = (PACKAGE_ROOT / "verification-asset-model.md").read_text(encoding="utf-8")
    runtime = (PACKAGE_ROOT / "runtime-requirements.md").read_text(encoding="utf-8")
    boundary = (PACKAGE_ROOT / "implementation-boundary.md").read_text(encoding="utf-8")
    required = {
        "VerificationAssetManifest": model, "specification_not_ready": model,
        "assertions": model, "known-bad/mutation-style": model,
        "Test Auditor": runtime, "Mechanical Verification Executor": runtime,
        "Candidate -> Test Auditor -> admitted immutable manifest -> MVE": runtime,
        "actual architecture index": runtime, "live-source": runtime,
        "zero agent tokens": runtime, "side-effect budget is zero": boundary,
        "work_package_completed": (PACKAGE_ROOT / "goal.md").read_text(encoding="utf-8"),
    }
    for phrase, text in required.items():
        if phrase not in text:
            errors.append(f"required authority phrase missing: {phrase}")
    profile = load_json(PACKAGE_ROOT / "bootstrap-profile.json")
    if profile.get("external_operation_budget") != 0:
        errors.append("external operation budget must be zero")
    if profile.get("cost_controls", {}).get("routine_reevaluation_agent_token_budget") != 0:
        errors.append("routine re-evaluation must use zero agent tokens")
    if profile.get("admission", {}).get("candidate_to_executor_direct_handoff") is not False:
        errors.append("candidate direct executor handoff must be prohibited")


def main() -> int:
    errors: list[str] = []
    manifest = load_json(MANIFEST_PATH)
    assets = validate_manifest(manifest, errors)
    scenarios = validate_acceptance(errors)
    snapshot_files = validate_snapshot(errors)
    validate_content(errors)
    result = {
        "specification": SPECIFICATION,
        "terminal_state": "succeeded" if not errors else "failed",
        "acceptance_outcome": "passed" if not errors else "failed",
        "verification_completeness": "complete" if not errors else "incomplete",
        "checked_assets": len(assets),
        "checked_scenarios": scenarios,
        "checked_capability_groups": len(GROUPS),
        "checked_phase3_snapshot_files": snapshot_files,
        "total_error_count": len(errors),
        "errors": errors,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
