from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from ddh.context import ContextEnvelope, ContextRequest
from ddh.contracts import AuthorityReference, ContractError, content_digest


@dataclass(frozen=True)
class WorkRequest:
    invocation_id: str
    specification: AuthorityReference
    candidate_generation: int
    goal: str
    write_scope: tuple[str, ...]
    acceptance_scenarios: tuple[str, ...]
    context: ContextEnvelope
    mutation_mode: str = "isolated_candidate"
    context_dispositions: tuple[str, ...] = ()
    risk_class: str = "L1"
    candidate_baseline_digest: str = ""
    repository_id: str = ""
    requested_ref: str = ""
    resolved_commit: str = ""
    prohibitions: tuple[str, ...] = ()
    budgets: dict[str, object] = field(default_factory=dict)
    escalation_conditions: tuple[str, ...] = ()


@dataclass(frozen=True)
class AgentResult:
    invocation_id: str
    specification: AuthorityReference
    candidate_generation: int
    result_type: str
    proposed_changes: dict[str, str | None]
    claimed_touched_paths: tuple[str, ...] = ()
    claimed_complete: bool = False
    context_request: ContextRequest | None = None


class AgentDriverPort(Protocol):
    def pull(self, request: WorkRequest) -> AgentResult: ...


class IsolatedCandidateCapabilityPort(Protocol):
    def proves(self, result: AgentResult) -> bool: ...


class AgentResultValidator:
    def validate(self, request: WorkRequest, result: AgentResult) -> None:
        if result.invocation_id != request.invocation_id:
            raise ContractError("agent_result_invocation_mismatch")
        if result.specification != request.specification:
            raise ContractError("agent_result_specification_mismatch")
        if result.candidate_generation != request.candidate_generation:
            raise ContractError("agent_result_stale_generation")
        if request.mutation_mode == "direct_user_workspace":
            raise ContractError("direct_user_workspace_prohibited")
        if result.result_type not in {
            "patch_proposal",
            "isolated_candidate",
            "context_request",
            "scope_change_required",
            "implementation_blocked",
            "cancelled",
        }:
            raise ContractError("agent_result_type_invalid")
        if result.result_type == "context_request" and result.context_request is None:
            raise ContractError("context_request_payload_missing")
        if result.result_type != "context_request" and result.context_request is not None:
            raise ContractError("unexpected_context_request_payload")


@dataclass(frozen=True)
class InboxSelection:
    current: AgentResult
    stale_count: int
    duplicate_count: int


class AgentResultInbox:
    def select_current(
        self,
        request: WorkRequest,
        results: tuple[AgentResult, ...],
    ) -> InboxSelection:
        validator = AgentResultValidator()
        current: dict[str, AgentResult] = {}
        stale_count = 0
        duplicate_count = 0
        for result in results:
            if not self._matches_subject(request, result):
                stale_count += 1
                continue
            validator.validate(request, result)
            digest = content_digest(_result_identity(result))
            if digest in current:
                duplicate_count += 1
            current[digest] = result
        if len(current) != 1:
            reason = "agent_result_missing" if not current else "agent_result_conflict"
            raise ContractError(reason)
        return InboxSelection(next(iter(current.values())), stale_count, duplicate_count)

    def _matches_subject(self, request: WorkRequest, result: AgentResult) -> bool:
        return (
            result.invocation_id == request.invocation_id
            and result.specification == request.specification
            and result.candidate_generation == request.candidate_generation
        )


def _result_identity(result: AgentResult) -> dict[str, object]:
    return {
        "result_type": result.result_type,
        "proposed_changes": result.proposed_changes,
    }


@dataclass
class ScriptedAgentAdapter:
    result: AgentResult

    def pull(self, request: WorkRequest) -> AgentResult:
        return self.result
