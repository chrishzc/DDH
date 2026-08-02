from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from ddh.contracts import ContractError, content_digest
from ddh.system_map import ImpactClosure


@dataclass(frozen=True)
class ContextItem:
    selector: str
    content: str
    purpose: str

    @property
    def estimated_tokens(self) -> int:
        return max(1, len(self.content) // 4)


@dataclass(frozen=True)
class ContextEnvelope:
    generation: int
    items: tuple[ContextItem, ...]
    map_facts: tuple[str, ...]
    charged_tokens: int
    digest: str


@dataclass(frozen=True)
class ContextRequest:
    selector: str
    purpose: str
    supporting_evidence: str
    estimated_value: int
    estimated_tokens: int


@dataclass(frozen=True)
class ContextDisposition:
    outcome: str
    envelope: ContextEnvelope
    write_authority_changed: bool = False


class ContextSourcePort(Protocol):
    def read(self, selector: str, purpose: str) -> str | None: ...


class ContextCurator:
    def __init__(
        self,
        effective_context_tokens: int,
        initial_max_ratio: float = 0.15,
        single_grant_max_ratio: float = 0.05,
        allowed_purposes: tuple[str, ...] = (
            "acceptance",
            "impact",
            "implementation",
            "verification",
        ),
    ) -> None:
        self._capacity = effective_context_tokens
        self._initial_limit = int(effective_context_tokens * initial_max_ratio)
        self._grant_limit = int(effective_context_tokens * single_grant_max_ratio)
        self._allowed_purposes = allowed_purposes

    def materialize(
        self,
        items: tuple[ContextItem, ...],
        impact: ImpactClosure,
        required_selectors: tuple[str, ...] | None = None,
    ) -> ContextEnvelope:
        relevant = self._select_required(items, required_selectors)
        unique = self._deduplicate(relevant)
        charged = sum(item.estimated_tokens for item in unique)
        if charged > self._initial_limit:
            raise ContractError("initial_context_budget_exceeded")
        return self._envelope(0, unique, impact.consumed_facts, charged)

    def expand(
        self,
        current: ContextEnvelope,
        request: ContextRequest,
        trusted_content: str | None,
    ) -> ContextDisposition:
        if trusted_content is None:
            return ContextDisposition("denied_unavailable", current)
        if self._is_duplicate(current, request, trusted_content):
            return ContextDisposition("denied_duplicate", current)
        if request.purpose not in self._allowed_purposes:
            return ContextDisposition("denied_irrelevant", current)
        item = ContextItem(request.selector, trusted_content, request.purpose)
        if not request.supporting_evidence or request.estimated_value <= 0:
            return ContextDisposition("denied_irrelevant", current)
        if item.estimated_tokens > self._grant_limit:
            return ContextDisposition("requires_summary", current)
        return ContextDisposition("granted", self._append(current, item))

    def _is_duplicate(
        self,
        current: ContextEnvelope,
        request: ContextRequest,
        trusted_content: str,
    ) -> bool:
        requested_digest = content_digest(trusted_content)
        return any(
            item.selector == request.selector
            or content_digest(item.content) == requested_digest
            for item in current.items
        )

    def _select_required(
        self,
        items: tuple[ContextItem, ...],
        required_selectors: tuple[str, ...] | None,
    ) -> tuple[ContextItem, ...]:
        if required_selectors is None:
            return items
        required = set(required_selectors)
        return tuple(item for item in items if item.selector in required)

    def _append(
        self,
        current: ContextEnvelope,
        item: ContextItem,
    ) -> ContextEnvelope:
        total = current.charged_tokens + item.estimated_tokens
        if total > self._capacity // 2:
            raise ContractError("context_reasoning_reserve_violated")
        items = current.items + (item,)
        return self._envelope(current.generation + 1, items, current.map_facts, total)

    def _deduplicate(
        self,
        items: tuple[ContextItem, ...],
    ) -> tuple[ContextItem, ...]:
        unique: dict[str, ContextItem] = {}
        for item in items:
            unique.setdefault(content_digest(item.content), item)
        return tuple(unique.values())

    def _envelope(
        self,
        generation: int,
        items: tuple[ContextItem, ...],
        map_facts: tuple[str, ...],
        charged_tokens: int,
    ) -> ContextEnvelope:
        identity = {
            "generation": generation,
            "selectors": [item.selector for item in items],
            "map_facts": map_facts,
        }
        return ContextEnvelope(
            generation,
            items,
            map_facts,
            charged_tokens,
            content_digest(identity),
        )
