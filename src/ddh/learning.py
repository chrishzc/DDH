"""Phase 6 bounded learning intake and orchestration-only Memory."""

from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from datetime import UTC, datetime, timedelta
from typing import Literal

from ddh.contracts import ContractError, canonical_json_bytes, content_digest


PRIORITIES = {"P0", "P1", "P2", "P3"}
MEMORY_CATEGORIES = {
    "parallelization", "partitioning", "initial_context", "expanded_context",
    "agent_tool_profile", "integration_handoff", "recovery_ordering",
    "summary_template", "parallel_to_serial_fallback",
}
PROHIBITED_KEYS = {"prompt", "conversation", "chain_of_thought", "source_diff", "workspace_copy", "stdout", "stderr", "secret", "credential"}
OUTAGE_TTL = {"P0": 14, "P1": 7, "P2": 3, "P3": 1}
CANDIDATE_TTL = {"P0": 90, "P1": 30, "P2": 14, "P3": 7}


@dataclass(frozen=True)
class AttemptLedger:
    ledger_id: str
    execution_identity: str
    specification_identity: str
    scope_identity: str
    risk_profile: str
    orchestration_versions: tuple[str, ...]
    attempts: tuple[str, ...]
    cost_summary: tuple[tuple[str, int], ...]
    failure_fingerprint: str
    recovery_route: str
    new_information: bool
    priority: Literal["P0", "P1", "P2", "P3"]
    terminal_outcome: str
    sealed: bool = False
    truncation_facts: tuple[str, ...] = ()

    def seal(self) -> "AttemptLedger":
        self._validate()
        sealed = replace(self, sealed=True)
        if len(canonical_json_bytes(asdict(sealed))) > 65_536:
            raise ContractError("attempt_ledger_size_exceeded")
        return sealed

    def _validate(self) -> None:
        if not self.ledger_id or not self.execution_identity or self.priority not in PRIORITIES:
            raise ContractError("attempt_ledger_identity_invalid")
        if set(self.attempts) & PROHIBITED_KEYS:
            raise ContractError("attempt_ledger_prohibited_content")
        if _contains_prohibited(asdict(self)):
            raise ContractError("attempt_ledger_prohibited_content")


@dataclass(frozen=True)
class PrefilterDisposition:
    outcome: Literal["consumed_deleted", "fold_candidate", "learning_input_unavailable_deleted"]
    reason_code: str
    requires_agent: bool = False


def prefilter(ledger: AttemptLedger, storage_available: bool = True) -> PrefilterDisposition:
    if not ledger.sealed:
        raise ContractError("attempt_ledger_not_sealed")
    if not storage_available:
        return PrefilterDisposition("learning_input_unavailable_deleted", "learning_input_unavailable")
    if not ledger.new_information or ledger.terminal_outcome in {"routine_success", "one_off_product_defect", "one_off_test_defect"}:
        return PrefilterDisposition("consumed_deleted", "routine_no_orchestration_signal")
    return PrefilterDisposition("fold_candidate", "orchestration_signal_detected")


class LearningHandoff:
    """Publishes the product result before any optional learning intake."""
    def publish_terminal_then_ingest(self, product_result: object, ledger: AttemptLedger, intake: "LearningIntake", now: datetime) -> tuple[object, PrefilterDisposition]:
        try:
            return product_result, intake.ingest(ledger, now)
        except (ContractError, OSError):
            return product_result, PrefilterDisposition("learning_input_unavailable_deleted", "learning_input_unavailable")


@dataclass(frozen=True)
class LearningCandidate:
    candidate_id: str
    normalized_pattern: str
    priority: Literal["P0", "P1", "P2", "P3"]
    applicability: str
    support_count: int
    counterevidence_count: int
    work_package_ids: tuple[str, ...]
    cost_summary: tuple[tuple[str, int], ...]
    created_at: datetime
    expires_at: datetime
    state: Literal["pending", "analyzing", "promoted", "rejected", "expired"] = "pending"


class LearningIntake:
    """In-memory reference store; raw ledgers are never retained after disposition."""
    def __init__(self) -> None:
        self._candidates: dict[str, LearningCandidate] = {}
        self._consumed_ledgers: set[str] = set()

    def ingest(self, ledger: AttemptLedger, now: datetime) -> PrefilterDisposition:
        sealed = ledger.seal()
        disposition = prefilter(sealed)
        if sealed.ledger_id in self._consumed_ledgers:
            return PrefilterDisposition("consumed_deleted", "ledger_already_disposed")
        self._consumed_ledgers.add(sealed.ledger_id)
        if disposition.outcome != "fold_candidate":
            return disposition
        key = content_digest((sealed.failure_fingerprint, sealed.recovery_route, sealed.priority))
        current = self._candidates.get(key)
        if current is None:
            current = LearningCandidate(
                key, sealed.failure_fingerprint, sealed.priority, sealed.scope_identity,
                0, 0, (), sealed.cost_summary, now, now + timedelta(days=CANDIDATE_TTL[sealed.priority]),
            )
        packages = tuple(sorted(set(current.work_package_ids + (sealed.execution_identity,))))
        self._candidates[key] = replace(current, support_count=current.support_count + 1, work_package_ids=packages)
        return disposition

    def candidate(self, candidate_id: str) -> LearningCandidate | None:
        return self._candidates.get(candidate_id)

    def expire(self, now: datetime) -> tuple[str, ...]:
        expired = tuple(key for key, item in self._candidates.items() if now >= item.expires_at)
        for key in expired:
            self._candidates.pop(key)
        return expired

    def analysis_due(self, candidate: LearningCandidate, now: datetime) -> bool:
        age = now - candidate.created_at
        if candidate.priority == "P0": return candidate.support_count >= 1
        if candidate.priority == "P1": return candidate.support_count >= 2 or age >= timedelta(hours=1)
        if candidate.priority == "P2": return candidate.support_count >= 3 and len(candidate.work_package_ids) >= 2
        return candidate.support_count >= 5


@dataclass(frozen=True)
class OrchestrationMemory:
    memory_id: str
    version: int
    category: str
    applicability: str
    recommendation: str
    prohibited_uses: tuple[str, ...]
    support_count: int
    counterevidence_count: int
    confidence_milli: int
    expires_at: datetime
    state: Literal["active", "suspended", "rolled_back", "expired"] = "active"

    def __post_init__(self) -> None:
        if self.category not in MEMORY_CATEGORIES:
            raise ContractError("orchestration_memory_category_prohibited")
        if not 0 <= self.confidence_milli <= 1000:
            raise ContractError("orchestration_memory_confidence_invalid")


@dataclass(frozen=True)
class GuidanceCard:
    memory_identity: str
    transition_kind: str
    recommendation: str
    applicability: str
    confidence_milli: int
    prohibited_uses: tuple[str, ...]


@dataclass(frozen=True)
class PromotionEvidence:
    author_identity: str
    critic_identity: str
    replay_identity: str
    trial_writer_identity: str
    policy_valid: bool
    replay_passed: bool
    shadow_passed: bool
    canary_passed: bool
    metric_improved: bool
    counterexamples_handled: bool
    rollback_ready: bool

    def valid(self) -> bool:
        identities = {self.author_identity, self.critic_identity, self.replay_identity, self.trial_writer_identity}
        return len(identities) == 4 and all(identities) and all((self.policy_valid, self.replay_passed, self.shadow_passed, self.canary_passed, self.metric_improved, self.counterexamples_handled, self.rollback_ready))


class MemoryRegistry:
    def __init__(self) -> None:
        self._items: dict[str, OrchestrationMemory] = {}

    def promote(self, memory: OrchestrationMemory, evidence: PromotionEvidence) -> OrchestrationMemory:
        if not evidence.valid():
            raise ContractError("orchestration_memory_promotion_rejected")
        identity = f"{memory.memory_id}@{memory.version}"
        self._items[identity] = memory
        return memory

    def guidance(self, transition_kind: str, is_main_agent: bool, now: datetime) -> tuple[GuidanceCard, ...]:
        if not is_main_agent:
            raise ContractError("child_agent_memory_access_prohibited")
        return tuple(
            GuidanceCard(f"{item.memory_id}@{item.version}", transition_kind, item.recommendation, item.applicability, item.confidence_milli, item.prohibited_uses)
            for item in self._items.values() if item.state == "active" and now < item.expires_at
        )

    def suspend_on_regression(self, identity: str) -> OrchestrationMemory:
        try: item = self._items[identity]
        except KeyError as error: raise ContractError("orchestration_memory_unknown") from error
        suspended = replace(item, state="suspended")
        self._items[identity] = suspended
        return suspended

    @staticmethod
    def unavailable_baseline() -> tuple[str, str, bool]:
        return ("single_main_agent", "bounded_initial_context", False)


def _contains_prohibited(value: object) -> bool:
    if isinstance(value, dict):
        return bool(PROHIBITED_KEYS & value.keys()) or any(_contains_prohibited(item) for item in value.values())
    if isinstance(value, (tuple, list)):
        return any(_contains_prohibited(item) for item in value)
    return False
