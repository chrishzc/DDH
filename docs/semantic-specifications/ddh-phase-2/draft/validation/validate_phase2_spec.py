from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = PACKAGE_ROOT / "manifest.json"
SPECIFICATION = "DDH-P2-SPEC-001@1.0.0"
REQUIRED_FAILURE_CLASSES = {
    "product_failed",
    "test_implementation_defect",
    "test_semantics_uncertain",
    "runner_failed",
    "tool_backend_unavailable",
    "context_insufficient",
    "system_map_unavailable",
    "candidate_stale",
    "test_asset_stale",
    "impact_underestimated",
    "scope_expansion_required",
    "external_side_effect_uncertain",
}


def reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_json(path: Path) -> Any:
    return json.loads(
        path.read_bytes().decode("utf-8"),
        object_pairs_hook=reject_duplicate_keys,
    )


def calculate_file_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def calculate_closure_digest(asset_digests: dict[str, str]) -> str:
    lines = [
        f"{path}:{asset_digests[path]}"
        for path in sorted(asset_digests)
    ]
    return hashlib.sha256("\n".join(lines).encode("utf-8")).hexdigest()


def validate_manifest(manifest: dict[str, Any], errors: list[str]) -> None:
    expected = {
        "status": "ready_for_confirmation",
        "implementation_authority": "none_until_exact_human_confirmation",
        "risk_class": "L2",
        "runtime_mode": "single_main_agent_serial",
        "external_side_effects": "prohibited",
        "parallel_runtime": "deferred_to_phase_3",
    }
    for field, value in expected.items():
        if manifest.get(field) != value:
            errors.append(f"manifest {field} must be {value}")
    baseline = manifest.get("phase1_baseline_commit")
    if not isinstance(baseline, str) or len(baseline) != 40:
        errors.append("phase1 baseline commit must be an exact SHA-1 identity")


def validate_assets(
    manifest: dict[str, Any],
    errors: list[str],
) -> dict[str, str]:
    actual_digests: dict[str, str] = {}
    assets = manifest.get("assets", [])
    if len(assets) != 7:
        errors.append("manifest must contain exactly seven closure assets")
    for asset in assets:
        relative_path = asset.get("path")
        if not isinstance(relative_path, str) or not relative_path:
            errors.append("manifest contains an invalid asset path")
            continue
        asset_path = PACKAGE_ROOT / relative_path
        if not asset_path.is_file():
            errors.append(f"missing asset: {relative_path}")
            continue
        actual_digest = calculate_file_digest(asset_path)
        actual_digests[relative_path] = actual_digest
        if actual_digest != asset.get("sha256"):
            errors.append(f"asset digest mismatch: {relative_path}")
    return actual_digests


def validate_closure(
    manifest: dict[str, Any],
    asset_digests: dict[str, str],
    errors: list[str],
) -> None:
    if calculate_closure_digest(asset_digests) != manifest.get("closure_digest"):
        errors.append("closure digest mismatch")


def validate_acceptance(errors: list[str]) -> int:
    catalog = load_json(PACKAGE_ROOT / "acceptance-scenarios.json")
    scenarios = catalog.get("scenarios", [])
    scenario_ids = [scenario.get("scenario_id") for scenario in scenarios]
    if len(scenario_ids) != len(set(scenario_ids)):
        errors.append("acceptance scenario IDs must be unique")
    required_fields = {
        "scenario_id",
        "class",
        "failure_class",
        "given",
        "when",
        "expected",
    }
    observed_failure_classes: set[str] = set()
    for index, scenario in enumerate(scenarios):
        missing = required_fields - scenario.keys()
        if missing:
            errors.append(f"scenario {index} missing fields: {sorted(missing)}")
        failure_class = scenario.get("failure_class")
        if isinstance(failure_class, str):
            observed_failure_classes.add(failure_class)
    if len(scenarios) < 24:
        errors.append("acceptance catalog must contain at least 24 scenarios")
    declared = set(catalog.get("required_failure_classes", []))
    if declared != REQUIRED_FAILURE_CLASSES:
        errors.append("declared required failure classes are incomplete")
    if not REQUIRED_FAILURE_CLASSES.issubset(observed_failure_classes):
        errors.append("not every required failure class has an executable scenario")
    return len(scenarios)


def validate_bootstrap(errors: list[str]) -> None:
    profile = load_json(PACKAGE_ROOT / "bootstrap-profile.json")
    if profile.get("runtime_mode") != "single_main_agent_serial":
        errors.append("bootstrap runtime mode must remain serial")
    budgets = profile.get("budgets", {})
    required = {
        "agent_model_usage",
        "context_ingestion",
        "work_package_wall_time",
        "verification_execution",
        "recovery_attempts",
        "failure_bundle",
        "stress_execution",
    }
    missing = required - budgets.keys()
    if missing:
        errors.append(f"bootstrap profile missing budgets: {sorted(missing)}")
    recovery = budgets.get("recovery_attempts", {})
    if recovery.get("identical_attempt_limit") != 0:
        errors.append("identical attempts must not be retried")
    if profile.get("external_operation_budget") != 0:
        errors.append("external operation budget must remain zero")


def build_result(errors: list[str], scenario_count: int) -> dict[str, Any]:
    passed = not errors
    return {
        "specification": SPECIFICATION,
        "terminal_state": "succeeded" if passed else "failed",
        "acceptance_outcome": "passed" if passed else "failed",
        "verification_completeness": "complete" if passed else "incomplete",
        "checked_assets": 7,
        "checked_scenarios": scenario_count,
        "checked_failure_classes": len(REQUIRED_FAILURE_CLASSES),
        "total_error_count": len(errors),
        "errors": errors,
    }


def main() -> int:
    errors: list[str] = []
    manifest = load_json(MANIFEST_PATH)
    validate_manifest(manifest, errors)
    asset_digests = validate_assets(manifest, errors)
    validate_closure(manifest, asset_digests, errors)
    scenario_count = validate_acceptance(errors)
    validate_bootstrap(errors)
    result = build_result(errors, scenario_count)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
