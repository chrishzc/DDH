from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ddh.contracts import AuthorityReference, ContractError, content_digest


REQUIRED_WORKLOAD_FIELDS = {
    "specification_id",
    "version",
    "risk_class",
    "goal",
    "expected_behavior",
    "write_scope",
    "prohibitions",
    "acceptance_scenarios",
    "budgets",
    "selected_nodes",
}


@dataclass(frozen=True)
class ConfirmationRecord:
    authority: AuthorityReference
    human_channel: str


@dataclass(frozen=True)
class WorkloadSpecification:
    authority: AuthorityReference
    goal: str
    risk_class: str
    expected_behavior: tuple[str, ...]
    write_scope: tuple[str, ...]
    prohibitions: tuple[str, ...]
    acceptance_scenarios: tuple[str, ...]
    budgets: dict[str, Any]
    selected_nodes: tuple[str, ...]


class SpecificationCompiler:
    def compile(
        self,
        document: dict[str, Any],
        confirmation: ConfirmationRecord,
    ) -> WorkloadSpecification:
        self._validate_fields(document)
        self._validate_types(document)
        self._validate_budgets(document["budgets"])
        authority = self._build_authority(document)
        self._validate_confirmation(authority, confirmation)
        return WorkloadSpecification(
            authority=authority,
            goal=document["goal"],
            risk_class=document["risk_class"],
            expected_behavior=tuple(document["expected_behavior"]),
            write_scope=tuple(document["write_scope"]),
            prohibitions=tuple(document["prohibitions"]),
            acceptance_scenarios=tuple(document["acceptance_scenarios"]),
            budgets=document["budgets"],
            selected_nodes=tuple(document["selected_nodes"]),
        )

    def _validate_fields(self, document: dict[str, Any]) -> None:
        if set(document) != REQUIRED_WORKLOAD_FIELDS:
            raise ContractError("specification_fields_invalid")
        required_values = (
            document["goal"],
            document["expected_behavior"],
            document["write_scope"],
            document["acceptance_scenarios"],
            document["selected_nodes"],
        )
        if not all(required_values):
            raise ContractError("specification_not_ready")

    def _validate_types(self, document: dict[str, Any]) -> None:
        scalar_fields = ("specification_id", "version", "goal", "risk_class")
        if any(not isinstance(document[field], str) for field in scalar_fields):
            raise ContractError("specification_scalar_type_invalid")
        sequence_fields = (
            "expected_behavior",
            "write_scope",
            "prohibitions",
            "acceptance_scenarios",
            "selected_nodes",
        )
        for field in sequence_fields:
            value = document[field]
            if not isinstance(value, list):
                raise ContractError("specification_sequence_type_invalid")
            if any(not isinstance(item, str) or not item for item in value):
                raise ContractError("specification_sequence_item_invalid")
            if len(value) != len(set(value)):
                raise ContractError("specification_sequence_duplicate")
        if not isinstance(document["budgets"], dict):
            raise ContractError("specification_budgets_type_invalid")
        if document["risk_class"] not in {"L1", "L2"}:
            raise ContractError("risk_class_not_supported")

    def _validate_budgets(self, budgets: dict[str, Any]) -> None:
        for name in ("agent_attempts", "effective_context_tokens"):
            if name not in budgets:
                continue
            value = budgets[name]
            if type(value) is not int or value <= 0:
                raise ContractError("specification_budget_invalid")

    def _build_authority(self, document: dict[str, Any]) -> AuthorityReference:
        return AuthorityReference(
            authority_id=document["specification_id"],
            version=document["version"],
            digest=content_digest(document),
        )

    def _validate_confirmation(
        self,
        authority: AuthorityReference,
        confirmation: ConfirmationRecord,
    ) -> None:
        if confirmation.authority != authority:
            raise ContractError("specification_confirmation_mismatch")
        if confirmation.human_channel not in {"local_cli", "trusted_host_ui"}:
            raise ContractError("confirmation_channel_untrusted")
