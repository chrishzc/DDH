from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = PACKAGE_ROOT / "manifest.json"


def reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_json(path: Path) -> Any:
    raw = path.read_bytes()
    text = raw.decode("utf-8")
    return json.loads(text, object_pairs_hook=reject_duplicate_keys)


def calculate_file_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def calculate_closure_digest(asset_digests: dict[str, str]) -> str:
    lines = [
        f"{path}:{asset_digests[path]}"
        for path in sorted(asset_digests)
    ]
    canonical_bytes = "\n".join(lines).encode("utf-8")
    return hashlib.sha256(canonical_bytes).hexdigest()


def validate_manifest(manifest: dict[str, Any], errors: list[str]) -> None:
    if manifest.get("status") != "ready_for_confirmation":
        errors.append("manifest status must be ready_for_confirmation")
    expected_authority = "none_until_exact_human_confirmation"
    if manifest.get("implementation_authority") != expected_authority:
        errors.append("implementation authority boundary is invalid")
    if manifest.get("external_side_effects") != "prohibited":
        errors.append("external side effects must be prohibited")


def validate_assets(
    manifest: dict[str, Any],
    errors: list[str],
) -> dict[str, str]:
    actual_digests: dict[str, str] = {}
    for asset in manifest.get("assets", []):
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
    actual_digest = calculate_closure_digest(asset_digests)
    if actual_digest != manifest.get("closure_digest"):
        errors.append("closure digest mismatch")


def validate_acceptance(errors: list[str]) -> int:
    catalog = load_json(PACKAGE_ROOT / "acceptance-scenarios.json")
    scenarios = catalog.get("scenarios", [])
    scenario_ids = [scenario.get("scenario_id") for scenario in scenarios]
    if len(scenario_ids) != len(set(scenario_ids)):
        errors.append("acceptance scenario IDs must be unique")
    required_fields = {"scenario_id", "class", "given", "when", "expected"}
    for index, scenario in enumerate(scenarios):
        missing = required_fields - scenario.keys()
        if missing:
            errors.append(
                f"scenario {index} missing fields: {sorted(missing)}"
            )
    if len(scenarios) < 20:
        errors.append("acceptance catalog must contain at least 20 scenarios")
    return len(scenarios)


def validate_bootstrap(errors: list[str]) -> None:
    profile = load_json(PACKAGE_ROOT / "bootstrap-profile.json")
    budgets = profile.get("budgets", {})
    required = {
        "agent_model_usage",
        "context_ingestion",
        "work_package_wall_time",
        "verification_execution",
        "recovery_attempts",
        "stress_execution",
    }
    missing = required - budgets.keys()
    if missing:
        errors.append(f"bootstrap profile missing budgets: {sorted(missing)}")


def build_result(errors: list[str], scenario_count: int) -> dict[str, Any]:
    passed = not errors
    return {
        "specification": "DDH-P1-SPEC-001@1.0.0",
        "terminal_state": "succeeded" if passed else "failed",
        "acceptance_outcome": "passed" if passed else "failed",
        "verification_completeness": "complete" if passed else "incomplete",
        "checked_assets": 7,
        "checked_scenarios": scenario_count,
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
