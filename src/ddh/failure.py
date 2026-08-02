from __future__ import annotations

import re
from io import StringIO
from dataclasses import asdict, dataclass, replace

from ddh.contracts import (
    AuthorityReference,
    CandidateReference,
    ContractError,
    canonical_json_bytes,
    content_digest,
)
from ddh.verification import VerificationResult


FAILURE_CLASSES = frozenset(
    {
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
)
SECRET_LINE = re.compile(
    r"(?i)(authorization|credential|password|private[_ -]?key|secret|token)"
)
SECRET_VALUE = re.compile(
    r"(?i)(github_pat_[A-Za-z0-9_]+|gh[pousr]_[A-Za-z0-9_]+|bearer\s+\S+)"
)


@dataclass(frozen=True)
class FailureBundleLimits:
    maximum_total_bytes: int = 32_768
    maximum_traceback_excerpt_bytes: int = 8_192
    maximum_stdout_excerpt_bytes: int = 4_096
    maximum_stderr_excerpt_bytes: int = 4_096
    maximum_failed_scenarios: int = 100
    maximum_affected_nodes: int = 1_000
    maximum_affected_resources: int = 1_000
    maximum_attempt_summaries: int = 64


@dataclass(frozen=True)
class FailureProgress:
    candidate_generation: int = 0
    test_asset_generation: int = 0
    environment_generation: int = 0
    context_generation: int = 0
    impact_generation: int = 0
    approved_strategy: str = ""


@dataclass(frozen=True)
class FailureObservation:
    failure_class: str
    reason_code: str
    specification: AuthorityReference
    invocation_id: str
    candidate: CandidateReference | None = None
    verification_subject_id: str = ""
    test_asset_digests: tuple[str, ...] = ()
    failed_scenario_ids: tuple[str, ...] = ()
    affected_nodes: tuple[str, ...] = ()
    affected_resources: tuple[str, ...] = ()
    actual_diff_summary: tuple[str, ...] = ()
    architecture_query_result_id: str = ""
    live_source_confirmations: tuple[str, ...] = ()
    attempted_routes: tuple[str, ...] = ()
    remaining_budget: int = 0
    retryable: bool = False
    external_side_effect_uncertain: bool = False
    traceback_location: str = ""
    stdout: str = ""
    stderr: str = ""
    allowed_machine_actions: tuple[str, ...] = ()
    required_human_authority: tuple[str, ...] = ()
    progress: FailureProgress = FailureProgress()
    remaining_budgets: tuple[tuple[str, int], ...] = ()
    consumed_architecture_facts: tuple[str, ...] = ()


@dataclass(frozen=True)
class DiagnosticExcerpt:
    traceback_location: str
    stdout: str
    stderr: str
    output_truncated: bool
    omitted_traceback_bytes: int
    omitted_stdout_bytes: int
    omitted_stderr_bytes: int
    redacted: bool


@dataclass(frozen=True)
class FailureBundle:
    failure_class: str
    reason_code: str
    specification: AuthorityReference
    invocation_id: str
    candidate: CandidateReference | None
    verification_subject_id: str
    test_asset_digests: tuple[str, ...]
    failed_scenario_ids: tuple[str, ...]
    affected_nodes: tuple[str, ...]
    affected_resources: tuple[str, ...]
    actual_diff_summary: tuple[str, ...]
    architecture_query_result_id: str
    live_source_confirmations: tuple[str, ...]
    attempted_routes: tuple[str, ...]
    remaining_budget: int
    retryable: bool
    external_side_effect_uncertain: bool
    allowed_machine_actions: tuple[str, ...]
    required_human_authority: tuple[str, ...]
    diagnostics: DiagnosticExcerpt
    omitted_reference_count: int
    progress: FailureProgress = FailureProgress()
    remaining_budgets: tuple[tuple[str, int], ...] = ()
    consumed_architecture_facts: tuple[str, ...] = ()

    @property
    def bundle_id(self) -> str:
        return content_digest(asdict(self))

    @property
    def encoded_size(self) -> int:
        return len(canonical_json_bytes(asdict(self)))


class FailureClassifier:
    def classify_verification(
        self,
        result: VerificationResult,
        *,
        candidate_current: bool = True,
        asset_current: bool = True,
        semantics_known: bool = True,
        test_implementation_defect: bool = False,
    ) -> str:
        if not candidate_current:
            return "candidate_stale"
        if not asset_current:
            return "test_asset_stale"
        if not semantics_known:
            return "test_semantics_uncertain"
        if test_implementation_defect:
            return "test_implementation_defect"
        if result.retryable or result.verification_completeness != "complete":
            return "runner_failed"
        if result.acceptance_outcome == "failed":
            return "product_failed"
        raise ContractError("failure_not_classifiable")


class FailureBundleBuilder:
    def __init__(self, limits: FailureBundleLimits | None = None) -> None:
        self._limits = limits or FailureBundleLimits()

    def build(self, observation: FailureObservation) -> FailureBundle:
        self._validate(observation)
        diagnostics = self._diagnostics(observation)
        bundle = self._initial_bundle(observation, diagnostics)
        return self._fit_total_limit(bundle)

    def _validate(self, observation: FailureObservation) -> None:
        if observation.failure_class not in FAILURE_CLASSES:
            raise ContractError("failure_class_invalid")
        if not observation.reason_code or not observation.invocation_id:
            raise ContractError("failure_identity_incomplete")
        if observation.remaining_budget < 0:
            raise ContractError("failure_budget_invalid")
        if any(
            not name or type(value) is not int or value < 0
            for name, value in observation.remaining_budgets
        ):
            raise ContractError("failure_budget_invalid")
        if (
            observation.failure_class == "external_side_effect_uncertain"
            and not observation.external_side_effect_uncertain
        ):
            raise ContractError("external_uncertainty_fact_missing")

    def _diagnostics(self, observation: FailureObservation) -> DiagnosticExcerpt:
        traceback, traceback_omitted = _sanitize_and_bound(
            observation.traceback_location,
            self._limits.maximum_traceback_excerpt_bytes,
        )
        stdout, stdout_omitted = _sanitize_and_bound(
            observation.stdout,
            self._limits.maximum_stdout_excerpt_bytes,
        )
        stderr, stderr_omitted = _sanitize_and_bound(
            observation.stderr,
            self._limits.maximum_stderr_excerpt_bytes,
        )
        redacted = any(
            _contains_sensitive_text(value)
            for value in (
                observation.traceback_location,
                observation.stdout,
                observation.stderr,
            )
        )
        return DiagnosticExcerpt(
            traceback,
            stdout,
            stderr,
            any((traceback_omitted, stdout_omitted, stderr_omitted)),
            traceback_omitted,
            stdout_omitted,
            stderr_omitted,
            redacted,
        )

    def _initial_bundle(
        self,
        observation: FailureObservation,
        diagnostics: DiagnosticExcerpt,
    ) -> FailureBundle:
        scenario_ids, scenario_omitted = _bounded_references(
            observation.failed_scenario_ids,
            self._limits.maximum_failed_scenarios,
        )
        nodes, node_omitted = _bounded_references(
            observation.affected_nodes,
            self._limits.maximum_affected_nodes,
        )
        resources, resource_omitted = _bounded_references(
            observation.affected_resources,
            self._limits.maximum_affected_resources,
        )
        routes, route_omitted = _bounded_references(
            observation.attempted_routes,
            self._limits.maximum_attempt_summaries,
        )
        architecture_facts, architecture_omitted = _bounded_references(
            observation.consumed_architecture_facts,
            self._limits.maximum_affected_nodes,
        )
        remaining_budgets = observation.remaining_budgets or (
            ("recovery_actions", observation.remaining_budget),
        )
        normalized_progress = replace(
            observation.progress,
            approved_strategy=_bounded_text(
                observation.progress.approved_strategy,
                512,
            ),
        )
        return FailureBundle(
            observation.failure_class,
            observation.reason_code,
            observation.specification,
            observation.invocation_id,
            observation.candidate,
            _bounded_text(observation.verification_subject_id, 512),
            _unique_bounded(observation.test_asset_digests),
            scenario_ids,
            nodes,
            resources,
            _unique_bounded(observation.actual_diff_summary),
            _bounded_text(observation.architecture_query_result_id, 512),
            _unique_bounded(observation.live_source_confirmations),
            routes,
            observation.remaining_budget,
            observation.retryable,
            observation.external_side_effect_uncertain,
            _unique_bounded(observation.allowed_machine_actions),
            _unique_bounded(observation.required_human_authority),
            diagnostics,
            (
                scenario_omitted
                + node_omitted
                + resource_omitted
                + route_omitted
                + architecture_omitted
            ),
            normalized_progress,
            tuple(
                sorted(
                    {
                        _bounded_text(name, 128): value
                        for name, value in remaining_budgets
                    }.items()
                )
            ),
            architecture_facts,
        )

    def _fit_total_limit(self, bundle: FailureBundle) -> FailureBundle:
        while bundle.encoded_size > self._limits.maximum_total_bytes:
            reduced = _reduce_bundle(bundle)
            if reduced == bundle:
                raise ContractError("failure_bundle_minimum_exceeds_limit")
            bundle = reduced
        return bundle


@dataclass(frozen=True)
class ExceptionReport:
    reason_code: str
    requested_paths: tuple[str, ...]
    current_write_scope: tuple[str, ...]
    evidence: tuple[str, ...]
    allowed_next_steps: tuple[str, ...]
    current_authority_class: str = "L1"
    requested_authority_class: str = "L3"
    blocked_lane: str = "single_main_agent"
    blocked_transition: str = ""
    failure_bundle_id: str = ""
    affected_nodes: tuple[str, ...] = ()
    affected_resources: tuple[str, ...] = ()
    affected_contracts: tuple[str, ...] = ()
    architecture_query_result_id: str = ""
    live_source_confirmations: tuple[str, ...] = ()
    attempted_actions: tuple[str, ...] = ()
    remaining_budget: int = 0
    preserved_candidate_digest: str = ""
    preserved_diff: tuple[str, ...] = ()
    requested_authority_change: str = ""
    verification_impact: tuple[str, ...] = ()
    external_impact: tuple[str, ...] = ()
    options: tuple[str, ...] = ()
    unaffected_work: tuple[str, ...] = ()
    preserved_verification_subject: str = ""
    option_tradeoffs: tuple[str, ...] = ()

    @property
    def report_id(self) -> str:
        return content_digest(asdict(self))


def _contains_sensitive_text(value: str) -> bool:
    return bool(SECRET_LINE.search(value) or SECRET_VALUE.search(value))


def _sanitize_and_bound(value: str, byte_limit: int) -> tuple[str, int]:
    source_bytes = len(value.encode("utf-8"))
    retained: list[str] = []
    retained_bytes = 0
    stream = StringIO(value)
    while retained_bytes < byte_limit:
        line = stream.readline()
        if not line:
            break
        sanitized = (
            "[REDACTED]\n"
            if _contains_sensitive_text(line)
            else SECRET_VALUE.sub("[REDACTED]", line)
        )
        remaining = byte_limit - retained_bytes
        excerpt, omitted = _truncate_utf8(sanitized, remaining)
        retained.append(excerpt)
        retained_bytes += len(excerpt.encode("utf-8"))
        if omitted:
            break
    result = "".join(retained)
    return result, max(0, source_bytes - len(result.encode("utf-8")))


def _truncate_utf8(value: str, byte_limit: int) -> tuple[str, int]:
    encoded = value.encode("utf-8")
    if len(encoded) <= byte_limit:
        return value, 0
    retained = encoded[:byte_limit].decode("utf-8", errors="ignore")
    return retained, len(encoded) - len(retained.encode("utf-8"))


def _bounded_references(
    values: tuple[str, ...],
    maximum_count: int,
) -> tuple[tuple[str, ...], int]:
    unique = _unique_bounded(values)
    return unique[:maximum_count], max(0, len(unique) - maximum_count)


def _unique_bounded(values: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(sorted({_bounded_text(value, 512) for value in values if value}))


def _bounded_text(value: str, byte_limit: int) -> str:
    return _truncate_utf8(value, byte_limit)[0]


def _reduce_bundle(bundle: FailureBundle) -> FailureBundle:
    sequence_fields = (
        "affected_resources",
        "affected_nodes",
        "actual_diff_summary",
        "live_source_confirmations",
        "attempted_routes",
        "failed_scenario_ids",
        "test_asset_digests",
        "allowed_machine_actions",
        "required_human_authority",
        "consumed_architecture_facts",
    )
    for field in sequence_fields:
        values = getattr(bundle, field)
        if values:
            return replace(
                bundle,
                **{field: values[:-1]},
                omitted_reference_count=bundle.omitted_reference_count + 1,
            )
    diagnostics = bundle.diagnostics
    if diagnostics.stdout:
        stdout, omitted = _truncate_utf8(
            diagnostics.stdout,
            max(0, len(diagnostics.stdout.encode("utf-8")) // 2),
        )
        return replace(
            bundle,
            diagnostics=replace(
                diagnostics,
                stdout=stdout,
                output_truncated=True,
                omitted_stdout_bytes=diagnostics.omitted_stdout_bytes + omitted,
            ),
        )
    if diagnostics.stderr:
        stderr, omitted = _truncate_utf8(
            diagnostics.stderr,
            max(0, len(diagnostics.stderr.encode("utf-8")) // 2),
        )
        return replace(
            bundle,
            diagnostics=replace(
                diagnostics,
                stderr=stderr,
                output_truncated=True,
                omitted_stderr_bytes=diagnostics.omitted_stderr_bytes + omitted,
            ),
        )
    return bundle
