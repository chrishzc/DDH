from __future__ import annotations

from dataclasses import asdict, dataclass, field

from ddh.contracts import content_digest
from ddh.failure import FailureBundle


@dataclass(frozen=True)
class AttemptFingerprint:
    inputs_digest: str
    candidate_digest: str
    strategy: str
    failure_reason: str

    @property
    def digest(self) -> str:
        return content_digest(self.__dict__)


@dataclass(frozen=True)
class RecoveryDisposition:
    outcome: str
    reason_code: str
    may_continue: bool


@dataclass(frozen=True)
class ProgressIdentity:
    candidate_generation: int = 0
    test_asset_generation: int = 0
    environment_generation: int = 0
    context_generation: int = 0
    impact_generation: int = 0
    approved_strategy: str = ""

    @property
    def digest(self) -> str:
        return content_digest(asdict(self))


@dataclass(frozen=True)
class RecoveryPolicy:
    transient_action_limit: int = 2
    equivalent_backend_attempt_limit: int = 1
    approved_backends: tuple[str, ...] = ()


@dataclass(frozen=True)
class RecoveryRouteRequest:
    failure: FailureBundle
    fingerprint: AttemptFingerprint
    progress: ProgressIdentity
    remaining_budget: int
    current_backend: str = ""
    available_backends: tuple[str, ...] = ()


@dataclass(frozen=True)
class RecoveryRoute:
    outcome: str
    reason_code: str
    action: str
    may_continue: bool
    requires_human: bool
    selected_backend: str = ""
    required_authority: tuple[str, ...] = ()


@dataclass
class RecoveryLedger:
    seen_attempts: set[str] = field(default_factory=set)
    transient_actions: int = 0
    backend_attempts: dict[str, int] = field(default_factory=dict)
    attempted_routes: list[str] = field(default_factory=list)

    def snapshot(self) -> dict[str, object]:
        return {
            "seen_attempts": sorted(self.seen_attempts),
            "transient_actions": self.transient_actions,
            "backend_attempts": dict(sorted(self.backend_attempts.items())),
            "attempted_routes": list(self.attempted_routes),
        }

    @classmethod
    def restore(cls, value: dict[str, object]) -> RecoveryLedger:
        return cls(
            set(value.get("seen_attempts", [])),
            int(value.get("transient_actions", 0)),
            {
                str(key): int(count)
                for key, count in dict(value.get("backend_attempts", {})).items()
            },
            [str(route) for route in value.get("attempted_routes", [])],
        )


class RecoveryRouter:
    def __init__(
        self,
        policy: RecoveryPolicy | None = None,
        ledger: RecoveryLedger | None = None,
    ) -> None:
        self._policy = policy or RecoveryPolicy()
        self._ledger = ledger or RecoveryLedger()

    @property
    def ledger(self) -> RecoveryLedger:
        return self._ledger

    def route(self, request: RecoveryRouteRequest) -> RecoveryRoute:
        boundary = self._human_boundary(request.failure.failure_class)
        if boundary is not None:
            return boundary
        if request.remaining_budget <= 0:
            return self._exception(
                "recovery_budget_exhausted",
                "preserve_and_report",
                ("budget_increase",),
            )
        attempt_identity = self._attempt_identity(request)
        if attempt_identity in self._ledger.seen_attempts:
            return RecoveryRoute(
                "blocked",
                "no_progress",
                "bounded_stop",
                False,
                False,
            )
        route = self._automatic_route(request)
        if route.may_continue:
            self._ledger.seen_attempts.add(attempt_identity)
            self._ledger.attempted_routes.append(route.action)
        return route

    def _human_boundary(self, failure_class: str) -> RecoveryRoute | None:
        boundaries = {
            "test_semantics_uncertain": (
                "specification_gap",
                "request_specification_revision",
                ("expected_behavior", "acceptance"),
            ),
            "scope_expansion_required": (
                "scope_expansion_required",
                "request_scope_revision",
                ("write_scope",),
            ),
            "external_side_effect_uncertain": (
                "external_high_risk_flow_required",
                "route_external_high_risk_flow",
                ("external_operation",),
            ),
        }
        if failure_class not in boundaries:
            return None
        reason, action, authority = boundaries[failure_class]
        return self._exception(reason, action, authority)

    def _automatic_route(self, request: RecoveryRouteRequest) -> RecoveryRoute:
        simple_actions = {
            "product_failed": ("product_repair", "repair_product_in_scope"),
            "test_implementation_defect": (
                "test_repair",
                "repair_and_readmit_test_asset",
            ),
            "context_insufficient": ("context_expansion", "expand_context"),
            "system_map_unavailable": (
                "live_source_fallback",
                "query_bounded_live_source",
            ),
            "candidate_stale": (
                "candidate_refresh",
                "create_current_candidate_generation",
            ),
            "test_asset_stale": (
                "test_asset_readmission",
                "readmit_current_test_asset",
            ),
            "impact_underestimated": (
                "verification_expansion",
                "expand_verification_closure",
            ),
        }
        selected = simple_actions.get(request.failure.failure_class)
        if selected is not None:
            reason, action = selected
            return RecoveryRoute("recover", reason, action, True, False)
        if request.failure.failure_class == "runner_failed":
            return self._runner_route(request)
        if request.failure.failure_class == "tool_backend_unavailable":
            return self._backend_route(request)
        return RecoveryRoute(
            "blocked",
            "failure_route_unknown",
            "bounded_stop",
            False,
            False,
        )

    def _runner_route(self, request: RecoveryRouteRequest) -> RecoveryRoute:
        if self._ledger.transient_actions < self._policy.transient_action_limit:
            self._ledger.transient_actions += 1
            return RecoveryRoute(
                "recover",
                "runner_environment_rebuild",
                "rebuild_runner_environment",
                True,
                False,
            )
        return self._backend_route(request)

    def _backend_route(self, request: RecoveryRouteRequest) -> RecoveryRoute:
        backend = self._select_backend(request)
        if backend:
            self._ledger.backend_attempts[backend] = (
                self._ledger.backend_attempts.get(backend, 0) + 1
            )
            return RecoveryRoute(
                "recover",
                "approved_backend_fallback",
                "select_approved_backend",
                True,
                False,
                backend,
            )
        return self._exception(
            "platform_blocked",
            "preserve_and_report",
            ("new_recovery_policy",),
        )

    def _select_backend(self, request: RecoveryRouteRequest) -> str:
        available = set(request.available_backends)
        for backend in self._policy.approved_backends:
            if backend == request.current_backend or backend not in available:
                continue
            attempts = self._ledger.backend_attempts.get(backend, 0)
            if attempts < self._policy.equivalent_backend_attempt_limit:
                return backend
        return ""

    def _attempt_identity(self, request: RecoveryRouteRequest) -> str:
        return content_digest(
            {
                "fingerprint": request.fingerprint.digest,
                "progress": request.progress.digest,
            }
        )

    def _exception(
        self,
        reason_code: str,
        action: str,
        authority: tuple[str, ...],
    ) -> RecoveryRoute:
        return RecoveryRoute(
            "exception",
            reason_code,
            action,
            False,
            True,
            required_authority=authority,
        )


class RecoveryController:
    def __init__(self, transient_action_limit: int = 2) -> None:
        self._seen: set[str] = set()
        self._transient_action_limit = transient_action_limit
        self._transient_actions = 0

    def evaluate(
        self,
        fingerprint: AttemptFingerprint,
        has_new_evidence: bool,
        transient_infrastructure_failure: bool,
    ) -> RecoveryDisposition:
        identity = fingerprint.digest
        if identity in self._seen and not has_new_evidence:
            return RecoveryDisposition("blocked", "no_progress", False)
        self._seen.add(identity)
        if transient_infrastructure_failure:
            return self._transient_disposition()
        if has_new_evidence:
            return RecoveryDisposition("continue", "new_evidence", True)
        return RecoveryDisposition("continue", "different_attempt", True)

    def _transient_disposition(self) -> RecoveryDisposition:
        if self._transient_actions >= self._transient_action_limit:
            return RecoveryDisposition("blocked", "safe_recovery_exhausted", False)
        self._transient_actions += 1
        return RecoveryDisposition("recover", "transient_recovery_allowed", True)
