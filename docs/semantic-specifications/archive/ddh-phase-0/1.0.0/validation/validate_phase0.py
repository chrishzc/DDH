#!/usr/bin/env python3
"""Deterministic validation for DDH Phase 0 specification fixtures.

This is a Phase 0 Verification Asset, not DDH runtime or a product CLI.
It uses only the Python standard library and performs no network or external
side effects.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any


ERROR_LIMIT = 100
SCENARIO_ID = re.compile(r"^P0-[A-Z0-9]+(?:-[A-Z0-9]+)+$")
WINDOWS_ABSOLUTE_PATH = re.compile(r"^[A-Za-z]:[\\/]")
DECISION_ALIAS = re.compile(r"^(?:DEC|Decision)-(\d{4})$")
REFERENCE_TOKEN_CHAR = r"A-Za-z0-9_-"


class DuplicateKeyError(ValueError):
    """Raised when strict JSON input repeats an object key."""


def reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKeyError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def strict_json_load(path: Path, errors: list[str]) -> Any | None:
    raw = path.read_bytes()
    relative = path.as_posix()
    if raw.startswith(b"\xef\xbb\xbf"):
        errors.append(f"{relative}: UTF-8 BOM is prohibited")
        return None
    if b"\r" in raw:
        errors.append(f"{relative}: only LF line endings are allowed")
    try:
        text = raw.decode("utf-8", errors="strict")
        return json.loads(text, object_pairs_hook=reject_duplicate_keys)
    except (UnicodeDecodeError, json.JSONDecodeError, DuplicateKeyError) as exc:
        errors.append(f"{relative}: strict JSON parse failed: {exc}")
        return None


def add_error(errors: list[str], message: str) -> None:
    errors.append(message)


def nonempty_authority(value: Any) -> bool:
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, list):
        return bool(value) and all(isinstance(item, str) and item.strip() for item in value)
    return False


def iter_strings(value: Any):
    if isinstance(value, str):
        yield value
    elif isinstance(value, list):
        for item in value:
            yield from iter_strings(item)
    elif isinstance(value, dict):
        for item in value.values():
            yield from iter_strings(item)


def iter_key_values(value: Any, target_key: str):
    if isinstance(value, dict):
        for key, item in value.items():
            if key == target_key:
                yield item
            yield from iter_key_values(item, target_key)
    elif isinstance(value, list):
        for item in value:
            yield from iter_key_values(item, target_key)


def json_type_matches(value: Any, expected_type: str) -> bool:
    if expected_type == "object":
        return isinstance(value, dict)
    if expected_type == "array":
        return isinstance(value, list)
    if expected_type == "string":
        return isinstance(value, str)
    if expected_type == "boolean":
        return isinstance(value, bool)
    if expected_type == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected_type == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected_type == "null":
        return value is None
    return False


def resolve_local_schema_reference(root_schema: dict[str, Any], reference: str) -> Any:
    if not reference.startswith("#/"):
        raise ValueError(f"only local schema references are supported: {reference}")
    current: Any = root_schema
    for token in reference[2:].split("/"):
        token = token.replace("~1", "/").replace("~0", "~")
        current = current[token]
    return current


def schema_validation_errors(
    instance: Any,
    schema: dict[str, Any],
    root_schema: dict[str, Any],
    location: str = "$",
) -> list[str]:
    """Validate the JSON Schema keywords used by the Phase 0 schemas."""

    if "$ref" in schema:
        target = resolve_local_schema_reference(root_schema, schema["$ref"])
        return schema_validation_errors(instance, target, root_schema, location)
    if "oneOf" in schema:
        branch_errors = [
            schema_validation_errors(instance, branch, root_schema, location)
            for branch in schema["oneOf"]
        ]
        valid_count = sum(not errors for errors in branch_errors)
        if valid_count != 1:
            return [f"{location}: expected exactly one matching oneOf branch"]
        return []

    errors: list[str] = []
    expected_type = schema.get("type")
    if isinstance(expected_type, str) and not json_type_matches(instance, expected_type):
        return [f"{location}: expected JSON type {expected_type}"]
    if "const" in schema and instance != schema["const"]:
        errors.append(f"{location}: value does not match const")

    if isinstance(instance, dict):
        required = schema.get("required", [])
        for key in required:
            if key not in instance:
                errors.append(f"{location}.{key}: required property missing")
        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            for key in instance:
                if key not in properties:
                    errors.append(f"{location}.{key}: additional property prohibited")
        minimum = schema.get("minProperties")
        if isinstance(minimum, int) and len(instance) < minimum:
            errors.append(f"{location}: fewer than {minimum} properties")
        for key, value in instance.items():
            property_schema = properties.get(key)
            if isinstance(property_schema, dict):
                errors.extend(
                    schema_validation_errors(
                        value, property_schema, root_schema, f"{location}.{key}"
                    )
                )

    if isinstance(instance, list):
        minimum = schema.get("minItems")
        if isinstance(minimum, int) and len(instance) < minimum:
            errors.append(f"{location}: fewer than {minimum} items")
        if schema.get("uniqueItems") is True:
            canonical = [json.dumps(item, sort_keys=True, ensure_ascii=False) for item in instance]
            if len(set(canonical)) != len(canonical):
                errors.append(f"{location}: duplicate array items")
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for index, value in enumerate(instance):
                errors.extend(
                    schema_validation_errors(
                        value, item_schema, root_schema, f"{location}[{index}]"
                    )
                )

    if isinstance(instance, str):
        minimum = schema.get("minLength")
        if isinstance(minimum, int) and len(instance) < minimum:
            errors.append(f"{location}: shorter than {minimum} characters")
        pattern = schema.get("pattern")
        if isinstance(pattern, str) and re.search(pattern, instance) is None:
            errors.append(f"{location}: does not match pattern {pattern}")
    return errors


def find_boolean_key(value: Any, prohibited_keys: set[str]) -> bool:
    if isinstance(value, dict):
        for key, item in value.items():
            if key in prohibited_keys and item is True:
                return True
            if find_boolean_key(item, prohibited_keys):
                return True
    elif isinstance(value, list):
        return any(find_boolean_key(item, prohibited_keys) for item in value)
    return False


def find_material_key(value: Any, prohibited_keys: set[str]) -> bool:
    if isinstance(value, dict):
        for key, item in value.items():
            if key.lower() in prohibited_keys and item not in (None, False, "", [], {}):
                return True
            if find_material_key(item, prohibited_keys):
                return True
    elif isinstance(value, list):
        return any(find_material_key(item, prohibited_keys) for item in value)
    return False


def contains_exact_reference(text: str, reference: str) -> bool:
    pattern = rf"(?<![{REFERENCE_TOKEN_CHAR}]){re.escape(reference)}(?![{REFERENCE_TOKEN_CHAR}])"
    return re.search(pattern, text) is not None


def iter_observable_semantic_terms(value: Any):
    if isinstance(value, dict):
        for key, item in value.items():
            if isinstance(item, str):
                yield key.lower()
                yield item.lower()
            elif isinstance(item, bool):
                if item:
                    yield key.lower()
            elif isinstance(item, (int, float)):
                yield key.lower()
                yield str(item).lower()
            elif item:
                yield key.lower()
                yield from iter_observable_semantic_terms(item)
    elif isinstance(value, list):
        for item in value:
            yield from iter_observable_semantic_terms(item)
    elif isinstance(value, str):
        yield value.lower()


def coverage_class_matches(class_name: str, scenario: dict[str, Any]) -> bool:
    """Bind declared coverage classes to observable scenario semantics."""

    semantic_text = " ".join(iter_observable_semantic_terms(scenario))
    class_markers = {
        "success": (
            "accepted",
            "allowed",
            "completed",
            "confirmed_ready",
            "high_assurance",
            "integrated",
            "materialized",
            "passed",
            "published",
            "recorded",
            "routine_no_orchestration_signal",
            "succeeded",
        ),
        "rejection": (
            "approval_required",
            "block",
            "deny",
            "failed_not_executed",
            "impact_unknown",
            "not_ready",
            "reject",
            "specification_not_ready",
        ),
        "stale_or_invalidation": (
            "approval_required",
            "drift",
            "expiry",
            "invalidat",
            "maximum_age",
            "max_age",
            "mismatch",
            "outage_upper_bound",
            "rerun_required",
            "stale",
            "ttl",
            "wrong_subject",
        ),
        "recovery": (
            "automatic_harness_strengthening",
            "fallback",
            "fresh",
            "new_environment",
            "new_projection",
            "not_executed",
            "rebuild",
            "rebuilt",
            "reconcile",
            "recover",
            "repair",
            "retained",
            "retry",
            "succeeded",
        ),
        "race_or_duplicate": (
            "arrival",
            "concurrent",
            "conflict",
            "cross_branch",
            "cross_work_package",
            "duplicate",
            "idempotent",
            "isolation",
            "late",
            "order",
            "pending",
            "race",
        ),
        "budget": (
            "10000",
            "allocation",
            "bounded",
            "budget_conflict",
            "budget_exhausted",
            "budget_exception",
            "budget_remaining",
            "budget_request",
            "exhaust",
            "limit",
            "resource",
            "stress",
            "timeout",
            "truncat",
        ),
    }
    return any(marker in semantic_text for marker in class_markers[class_name])


def validate_fixture_family(
    path: Path,
    document: Any,
    fixture_schema: dict[str, Any],
    scenario_ids: set[str],
    scenario_sources: dict[str, str],
    scenario_expected_values: dict[str, set[str]],
    scenario_expected_objects: dict[str, dict[str, Any]],
    scenario_objects: dict[str, dict[str, Any]],
    scenario_families: dict[str, str],
    all_contract_refs: set[str],
    errors: list[str],
) -> None:
    relative = path.as_posix()
    for schema_error in schema_validation_errors(
        document, fixture_schema, fixture_schema
    ):
        add_error(errors, f"{relative}:{schema_error}")
    allowed_top = {"fixture_family", "contract_refs", "scenarios"}
    required_top = allowed_top
    if not isinstance(document, dict):
        add_error(errors, f"{relative}: fixture family must be an object")
        return
    if set(document) != required_top:
        add_error(
            errors,
            f"{relative}: top-level fields must be exactly {sorted(required_top)}",
        )
    if not isinstance(document.get("fixture_family"), str) or not document["fixture_family"]:
        add_error(errors, f"{relative}: fixture_family must be non-empty")
    family_refs = document.get("contract_refs")
    if not isinstance(family_refs, list) or not family_refs:
        add_error(errors, f"{relative}: contract_refs must be a non-empty array")
    else:
        all_contract_refs.update(ref for ref in family_refs if isinstance(ref, str))
    scenarios = document.get("scenarios")
    if not isinstance(scenarios, list) or not scenarios:
        add_error(errors, f"{relative}: scenarios must be a non-empty array")
        return

    required_scenario = {
        "scenario_id",
        "contract_refs",
        "given",
        "when",
        "expected",
        "authority_source",
        "immutable_fields",
    }
    for index, scenario in enumerate(scenarios):
        label = f"{relative}:scenarios[{index}]"
        if not isinstance(scenario, dict):
            add_error(errors, f"{label}: scenario must be an object")
            continue
        if set(scenario) != required_scenario:
            add_error(
                errors,
                f"{label}: fields must be exactly {sorted(required_scenario)}",
            )
        scenario_id = scenario.get("scenario_id")
        if not isinstance(scenario_id, str) or not SCENARIO_ID.fullmatch(scenario_id):
            add_error(errors, f"{label}: invalid scenario_id {scenario_id!r}")
        elif scenario_id in scenario_ids:
            add_error(errors, f"{label}: duplicate scenario_id {scenario_id}")
        else:
            scenario_ids.add(scenario_id)
            scenario_sources[scenario_id] = relative
            scenario_objects[scenario_id] = scenario
        refs = scenario.get("contract_refs")
        if not isinstance(refs, list) or not refs or not all(
            isinstance(ref, str) and ref for ref in refs
        ):
            add_error(errors, f"{label}: contract_refs must be non-empty strings")
        else:
            all_contract_refs.update(refs)
        if not isinstance(scenario.get("given"), (dict, str)):
            add_error(errors, f"{label}: given must be an object or non-empty string")
        if not isinstance(scenario.get("when"), (dict, str)):
            add_error(errors, f"{label}: when must be an object or non-empty string")
        expected = scenario.get("expected")
        if not isinstance(expected, dict) or not expected:
            add_error(errors, f"{label}: expected must be a non-empty object")
        elif isinstance(scenario_id, str):
            scenario_expected_values[scenario_id] = set(iter_strings(expected))
            scenario_expected_objects[scenario_id] = expected
            scenario_families[scenario_id] = document.get("fixture_family", "")
        if not nonempty_authority(scenario.get("authority_source")):
            add_error(errors, f"{label}: authority_source is missing")
        immutable = scenario.get("immutable_fields")
        if not isinstance(immutable, list) or not immutable or not all(
            isinstance(field, str) and field for field in immutable
        ):
            add_error(errors, f"{label}: immutable_fields must be non-empty strings")


def validate_contract_reference(
    reference: str,
    repository_root: Path,
    registry: set[str],
) -> bool:
    if reference.startswith("docs/"):
        return (repository_root / reference).is_file()
    if reference in registry:
        return True
    alias_match = DECISION_ALIAS.fullmatch(reference)
    if alias_match:
        return any(
            (repository_root / "docs" / "decisions").glob(
                f"{alias_match.group(1)}-*.md"
            )
        )

    dynamic_sources: list[Path] = []
    if reference.startswith("P0-"):
        dynamic_sources = sorted(
            (
                repository_root
                / "docs"
                / "semantic-specifications"
                / "ddh-phase-0"
                / "contract-families"
            ).glob("*.md")
        )
    elif reference.startswith(("OW-", "RC-PWC-", "DDH-EO-E2E-")):
        dynamic_sources = [
            repository_root
            / "docs"
            / "proposals"
            / "parallel_work_coordination_subsystem_specification.md",
            repository_root
            / "docs"
            / "proposals"
            / "candidate_integrity_and_mutation_subsystem_specification.md",
            repository_root
            / "docs"
            / "proposals"
            / "ddh_execution_and_orchestration_domain_overview.md",
            repository_root
            / "docs"
            / "proposals"
            / "context_broker_subsystem_specification.md",
        ]
    elif reference.startswith("PWC-"):
        dynamic_sources = [
            repository_root
            / "docs"
            / "proposals"
            / "parallel_work_coordination_subsystem_specification.md",
            repository_root
            / "docs"
            / "proposals"
            / "candidate_integrity_and_mutation_subsystem_specification.md",
        ]
    elif reference.startswith("SMQ-"):
        dynamic_sources = [
            repository_root
            / "docs"
            / "proposals"
            / "ddh_execution_and_orchestration_domain_overview.md"
        ]
    elif reference.startswith("TAQG-"):
        dynamic_sources = [
            repository_root
            / "docs"
            / "proposals"
            / "test_asset_quality_governance_subsystem_specification.md"
        ]
    elif reference.startswith(("MVE-", "CIM-MVE-", "RC-MVE-", "RC-DOM-")):
        dynamic_sources = [
            repository_root
            / "docs"
            / "proposals"
            / "mechanical_verification_execution_subsystem_specification.md",
            repository_root
            / "docs"
            / "proposals"
            / "ddh_execution_and_orchestration_domain_overview.md",
        ]
    return any(
        path.is_file()
        and contains_exact_reference(
            path.read_text(encoding="utf-8"), reference
        )
        for path in dynamic_sources
    )


def validate_golden_flow(
    path: Path,
    document: Any,
    scenario_ids: set[str],
    scenario_expected_values: dict[str, set[str]],
    flow_ids: set[str],
    errors: list[str],
) -> None:
    relative = path.as_posix()
    required = {
        "flow_id",
        "title",
        "scope_layer",
        "contract_refs",
        "initial_authority",
        "steps",
        "terminal_assertions",
    }
    optional = {"failure_routes"}
    if not isinstance(document, dict):
        add_error(errors, f"{relative}: golden flow must be an object")
        return
    missing = required - set(document)
    unknown = set(document) - required - optional
    if missing or unknown:
        add_error(
            errors,
            f"{relative}: missing={sorted(missing)} unknown={sorted(unknown)}",
        )
    flow_id = document.get("flow_id")
    if not isinstance(flow_id, str) or not SCENARIO_ID.fullmatch(flow_id):
        add_error(errors, f"{relative}: invalid flow_id {flow_id!r}")
    elif flow_id in flow_ids:
        add_error(errors, f"{relative}: duplicate flow_id {flow_id}")
    else:
        flow_ids.add(flow_id)
    steps = document.get("steps")
    if not isinstance(steps, list) or not steps:
        add_error(errors, f"{relative}: steps must be non-empty")
    else:
        orders = [step.get("order") for step in steps if isinstance(step, dict)]
        if orders != list(range(1, len(steps) + 1)):
            add_error(errors, f"{relative}: step order must be contiguous from 1")
        for step in steps:
            scenario_id = step.get("scenario_id") if isinstance(step, dict) else None
            if scenario_id not in scenario_ids:
                add_error(errors, f"{relative}: unknown step scenario {scenario_id}")
                continue
            expected_outcome = step.get("expected_outcome")
            if expected_outcome not in scenario_expected_values.get(scenario_id, set()):
                add_error(
                    errors,
                    f"{relative}: expected outcome {expected_outcome!r} is not projected "
                    f"by {scenario_id}",
                )
    for route in document.get("failure_routes", []):
        scenario_id = route.get("scenario_id") if isinstance(route, dict) else None
        if scenario_id not in scenario_ids:
            add_error(errors, f"{relative}: unknown failure route {scenario_id}")
    if flow_id == "P0-FLOW-EXT-001":
        assertions = document.get("terminal_assertions", {})
        if assertions.get("external_write_performed") is not False:
            add_error(errors, f"{relative}: Phase 7A cannot perform external writes")


def validate_envelope_examples(
    package_root: Path,
    json_documents: dict[Path, Any],
    envelope_schema: dict[str, Any],
    errors: list[str],
) -> None:
    valid_path = package_root / "shared" / "contract-envelope-valid-example.json"
    rejected_path = package_root / "shared" / "contract-envelope-rejected-example.json"
    expected_path = package_root / "shared" / "contract-envelope-expected-results.json"
    valid = json_documents.get(valid_path)
    rejected = json_documents.get(rejected_path)
    expected_results = json_documents.get(expected_path)

    valid_errors = schema_validation_errors(
        valid, envelope_schema, envelope_schema
    )
    for schema_error in valid_errors:
        add_error(errors, f"{valid_path.as_posix()}:{schema_error}")

    rejected_errors = schema_validation_errors(
        rejected, envelope_schema, envelope_schema
    )
    if not rejected_errors:
        add_error(
            errors,
            f"{rejected_path.as_posix()}: rejected example unexpectedly conforms",
        )
    missing_version_detected = any(
        "$.subject.task_specification.version" in schema_error
        for schema_error in rejected_errors
    )
    if not missing_version_detected:
        add_error(
            errors,
            f"{rejected_path.as_posix()}: missing authority version was not detected",
        )

    cases = expected_results.get("cases", []) if isinstance(expected_results, dict) else []
    expected_by_id = {
        case.get("case_id"): case.get("expected", {})
        for case in cases
        if isinstance(case, dict)
    }
    if expected_by_id.get("P0-ENV-001", {}).get("outcome") != "accepted":
        add_error(errors, f"{expected_path.as_posix()}: P0-ENV-001 must be accepted")
    rejected_expected = expected_by_id.get("P0-ENV-002", {})
    if rejected_expected.get("outcome") != "rejected":
        add_error(errors, f"{expected_path.as_posix()}: P0-ENV-002 must be rejected")
    if "subject.task_specification.version" not in rejected_expected.get(
        "missing_fields", []
    ):
        add_error(
            errors,
            f"{expected_path.as_posix()}: rejected field expectation is incomplete",
        )


def validate_coverage_matrix(
    document: Any,
    fixture_families: set[str],
    scenario_ids: set[str],
    scenario_objects: dict[str, dict[str, Any]],
    scenario_families: dict[str, str],
    errors: list[str],
) -> None:
    if not isinstance(document, dict):
        add_error(errors, "coverage matrix is missing or invalid")
        return
    required_classes = {
        "success",
        "rejection",
        "stale_or_invalidation",
        "recovery",
        "race_or_duplicate",
        "budget",
    }
    covered_families: set[str] = set()
    for family in document.get("families", []):
        if not isinstance(family, dict):
            add_error(errors, "coverage matrix family must be an object")
            continue
        family_name = family.get("fixture_family")
        if family_name in covered_families:
            add_error(errors, f"coverage matrix repeats family: {family_name}")
        covered_families.add(family_name)
        classes = family.get("required_classes", {})
        if set(classes) != required_classes:
            add_error(
                errors,
                f"coverage matrix {family_name}: classes must be "
                f"{sorted(required_classes)}",
            )
        for class_name in required_classes:
            members = classes.get(class_name)
            if not isinstance(members, list) or not members:
                add_error(
                    errors,
                    f"coverage matrix {family_name}.{class_name} must be non-empty",
                )
                continue
            for scenario_id in members:
                if scenario_id not in scenario_ids:
                    add_error(
                        errors,
                        f"coverage matrix references unknown scenario: {scenario_id}",
                    )
                elif scenario_families.get(scenario_id) != family_name:
                    add_error(
                        errors,
                        f"coverage matrix puts {scenario_id} in wrong family "
                        f"{family_name}",
                    )
                elif not coverage_class_matches(
                    class_name, scenario_objects[scenario_id]
                ):
                    add_error(
                        errors,
                        f"coverage matrix {scenario_id} has no observable "
                        f"{class_name} semantic marker",
                    )
    if covered_families != fixture_families:
        add_error(
            errors,
            "coverage matrix family set mismatch: "
            f"missing={sorted(fixture_families - covered_families)} "
            f"unknown={sorted(covered_families - fixture_families)}",
        )

    special = document.get("special_requirements", {})
    required_special = {
        "external_no_real_write",
        "learning_retention_acceptance",
        "legacy_mechanisms_are_not_active",
        "system_map_actual_only_non_authority",
        "wire_and_identity_required_scenarios",
    }
    if not isinstance(special, dict) or set(special) != required_special:
        add_error(
            errors,
            f"coverage matrix special requirements must be {sorted(required_special)}",
        )
        return
    for requirement, members in special.items():
        if not isinstance(members, list) or not members:
            add_error(errors, f"special requirement {requirement} must be non-empty")
            continue
        for scenario_id in members:
            if scenario_id not in scenario_ids:
                add_error(
                    errors,
                    f"special requirement {requirement} references unknown "
                    f"scenario {scenario_id}",
                )
    expected_external = {
        scenario_id for scenario_id in scenario_ids if scenario_id.startswith("P0-EXT-")
    }
    actual_external = set(special.get("external_no_real_write", []))
    if actual_external != expected_external:
        add_error(
            errors,
            "external_no_real_write must list every external scenario exactly",
        )


def validate_machine_readable_safety(
    json_documents: dict[Path, Any],
    errors: list[str],
) -> None:
    secret_keys = {
        "access_token",
        "credential_value",
        "password",
        "private_key",
        "raw_credential",
        "secret",
    }
    legacy_activation_keys = {
        "checkpoint_active",
        "checkpoint_enabled",
        "checkpoint_required",
        "frozen_task_active",
        "frozen_task_activated",
        "legacy_system_map_fallback_active",
        "provenance_chain_active",
        "provenance_receipt_active",
        "receipt_required",
        "source_lock_active",
        "source_lock_required",
    }
    for path, document in json_documents.items():
        for value in iter_strings(document):
            if (
                WINDOWS_ABSOLUTE_PATH.match(value)
                or value.startswith("\\\\")
                or value.startswith("/")
            ):
                add_error(
                    errors,
                    f"{path.as_posix()}: machine absolute path is prohibited",
                )
        if find_material_key(document, secret_keys):
            add_error(errors, f"{path.as_posix()}: embedded secret material is prohibited")
        if find_boolean_key(document, legacy_activation_keys):
            add_error(
                errors,
                f"{path.as_posix()}: removed legacy mechanism cannot be activated",
            )


def main() -> int:
    script_path = Path(__file__).resolve()
    package_root = script_path.parents[1]
    repository_root = script_path.parents[4]
    errors: list[str] = []

    json_documents: dict[Path, Any] = {}
    for path in sorted(package_root.rglob("*.json")):
        document = strict_json_load(path, errors)
        if document is not None:
            json_documents[path] = document

    fixture_schema_path = package_root / "validation" / "fixture-family.schema.json"
    envelope_schema_path = (
        package_root / "validation" / "contract-envelope-example.schema.json"
    )
    fixture_schema = json_documents.get(fixture_schema_path)
    envelope_schema = json_documents.get(envelope_schema_path)
    if not isinstance(fixture_schema, dict):
        add_error(errors, "fixture-family.schema.json is missing or invalid")
        fixture_schema = {}
    if not isinstance(envelope_schema, dict):
        add_error(errors, "contract-envelope-example.schema.json is missing or invalid")
        envelope_schema = {}

    manifest_path = package_root / "package-manifest.json"
    manifest = json_documents.get(manifest_path)
    if not isinstance(manifest, dict):
        add_error(errors, "package-manifest.json is missing or invalid")
        manifest_assets: list[Any] = []
    else:
        manifest_assets = manifest.get("assets", [])
        if manifest.get("external_side_effects") != "prohibited":
            add_error(errors, "package manifest must prohibit external side effects")
    manifested_paths: set[str] = set()
    for asset in manifest_assets:
        if not isinstance(asset, dict):
            add_error(errors, "package manifest asset must be an object")
            continue
        path_value = asset.get("path")
        if not isinstance(path_value, str) or not path_value:
            add_error(errors, "package manifest asset path is missing")
            continue
        if path_value in manifested_paths:
            add_error(errors, f"duplicate manifest asset: {path_value}")
        manifested_paths.add(path_value)
        resolved = (package_root / path_value).resolve()
        try:
            resolved.relative_to(package_root.resolve())
        except ValueError:
            add_error(errors, f"manifest asset escapes package: {path_value}")
            continue
        if asset.get("required") is True and not resolved.is_file():
            add_error(errors, f"required manifest asset missing: {path_value}")
    actual_package_files = {
        path.relative_to(package_root).as_posix()
        for path in package_root.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts
    }
    unmanifested = actual_package_files - manifested_paths
    if unmanifested:
        add_error(errors, f"unmanifested package assets: {sorted(unmanifested)}")

    scenario_ids: set[str] = set()
    scenario_sources: dict[str, str] = {}
    scenario_expected_values: dict[str, set[str]] = {}
    scenario_expected_objects: dict[str, dict[str, Any]] = {}
    scenario_objects: dict[str, dict[str, Any]] = {}
    scenario_families: dict[str, str] = {}
    all_contract_refs: set[str] = set()
    fixture_paths = sorted((package_root / "fixtures").glob("*.json"))
    for path in fixture_paths:
        validate_fixture_family(
            path,
            json_documents.get(path),
            fixture_schema,
            scenario_ids,
            scenario_sources,
            scenario_expected_values,
            scenario_expected_objects,
            scenario_objects,
            scenario_families,
            all_contract_refs,
            errors,
        )
    fixture_families = set(scenario_families.values())

    coverage_path = package_root / "traceability" / "coverage-matrix.json"
    validate_coverage_matrix(
        json_documents.get(coverage_path),
        fixture_families,
        scenario_ids,
        scenario_objects,
        scenario_families,
        errors,
    )

    external_write_keys = {
        "external_write",
        "external_write_executed",
        "external_write_performed",
        "real_external_write",
    }
    system_map_authority_keys = {
        "map_grants_scope",
        "scope_granted_by_map",
        "write_authority_granted_by_map",
        "write_permission_added",
    }
    for scenario_id, expected in scenario_expected_objects.items():
        if scenario_id.startswith("P0-EXT-"):
            if find_boolean_key(expected, external_write_keys):
                add_error(errors, f"{scenario_id}: Phase 7A cannot produce a real write")
            if expected.get("external_write") is not False:
                add_error(
                    errors,
                    f"{scenario_id}: external_write=false must be explicit",
                )
        if scenario_id.startswith("P0-SM-") and find_boolean_key(
            expected, system_map_authority_keys
        ):
            add_error(errors, f"{scenario_id}: System Map cannot grant authority")

    registry_path = package_root / "traceability" / "contract-registry.json"
    registry_document = json_documents.get(registry_path, {})
    registry = {
        item.get("contract_id")
        for item in registry_document.get("contracts", [])
        if isinstance(item, dict) and isinstance(item.get("contract_id"), str)
    }
    for item in registry_document.get("contracts", []):
        if not isinstance(item, dict):
            continue
        contract_path = item.get("path")
        if not isinstance(contract_path, str) or not (repository_root / contract_path).is_file():
            add_error(errors, f"contract registry path unresolved: {contract_path}")

    for path, document in json_documents.items():
        if path.name.endswith(".schema.json"):
            continue
        for references in iter_key_values(document, "contract_refs"):
            if not isinstance(references, list) or not all(
                isinstance(reference, str) and reference for reference in references
            ):
                add_error(errors, f"{path.as_posix()}: invalid contract_refs value")
                continue
            all_contract_refs.update(references)
    manifest_specification = (
        manifest.get("specification") if isinstance(manifest, dict) else None
    )
    if not isinstance(manifest_specification, str) or not manifest_specification:
        add_error(errors, "package manifest specification is missing")
    else:
        all_contract_refs.add(manifest_specification)

    for reference in sorted(all_contract_refs):
        if not validate_contract_reference(reference, repository_root, registry):
            add_error(errors, f"unresolved contract reference: {reference}")

    flow_ids: set[str] = set()
    for path in sorted((package_root / "golden-flows").glob("*.json")):
        validate_golden_flow(
            path,
            json_documents.get(path),
            scenario_ids,
            scenario_expected_values,
            flow_ids,
            errors,
        )

    validate_envelope_examples(
        package_root, json_documents, envelope_schema, errors
    )
    validate_machine_readable_safety(json_documents, errors)

    if len(scenario_ids) < 150:
        add_error(errors, f"expected at least 150 scenarios, found {len(scenario_ids)}")
    required_flows = {"P0-FLOW-L1-001", "P0-FLOW-L2-001", "P0-FLOW-EXT-001"}
    if not required_flows.issubset(flow_ids):
        add_error(errors, f"required golden flows missing: {sorted(required_flows - flow_ids)}")

    # Conceptual stress check: create no files and require bounded membership work.
    ordered_ids = sorted(scenario_ids)
    synthetic_checked = 0
    if ordered_ids:
        for index in range(10_000):
            if ordered_ids[index % len(ordered_ids)] not in scenario_ids:
                add_error(errors, "synthetic reference membership failed")
                break
            synthetic_checked += 1

    result = {
        "acceptance_outcome": "passed" if not errors else "failed",
        "checked_assets": len(manifested_paths),
        "checked_contract_references": len(all_contract_refs),
        "checked_flows": len(flow_ids),
        "checked_scenarios": len(scenario_ids),
        "errors": errors[:ERROR_LIMIT],
        "errors_truncated": len(errors) > ERROR_LIMIT,
        "reason_codes": [] if not errors else ["phase0_package_validation_failed"],
        "synthetic_references_checked": synthetic_checked,
        "terminal_state": "succeeded" if not errors else "failed",
        "total_error_count": len(errors),
        "verification_completeness": "complete" if not errors else "incomplete",
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
