from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from ddh.contracts import ContractError


USABLE_OUTCOMES = {"usable_actual"}
FALLBACK_OUTCOMES = {
    "partial",
    "conflicted",
    "view_mismatch",
    "unavailable",
    "impact_unknown",
}


@dataclass(frozen=True)
class MapQuery:
    repository_id: str
    requested_ref: str
    resolved_commit: str
    selected_nodes: tuple[str, ...]
    purpose: str
    bounded_depth: int = 1
    changed_resources: tuple[str, ...] = ()


@dataclass(frozen=True)
class MapResult:
    outcome: str
    repository_id: str
    requested_ref: str
    resolved_commit: str
    view_id: str | None
    nodes: tuple[str, ...]
    relations: tuple[tuple[str, str], ...]
    resource_bindings: tuple[tuple[str, str], ...]
    omitted_areas: tuple[str, ...] = ()


@dataclass(frozen=True)
class ImpactClosure:
    nodes: tuple[str, ...]
    relations: tuple[tuple[str, str], ...]
    consumed_facts: tuple[str, ...]
    used_live_fallback: bool
    complete: bool


class SystemMapPort(Protocol):
    def query(self, query: MapQuery) -> MapResult: ...


class LiveSourceFallbackPort(Protocol):
    def discover(self, query: MapQuery, areas: tuple[str, ...]) -> MapResult: ...


class ImpactResolver:
    def __init__(
        self,
        system_map: SystemMapPort,
        live_fallback: LiveSourceFallbackPort,
    ) -> None:
        self._system_map = system_map
        self._live_fallback = live_fallback

    def resolve(self, query: MapQuery) -> ImpactClosure:
        map_result = self._system_map.query(query)
        self._validate_binding(query, map_result)
        missing = _missing_resources(query, map_result)
        if _is_complete_map_result(map_result, missing):
            return self._build_closure(map_result, False)
        if map_result.outcome not in FALLBACK_OUTCOMES:
            if map_result.outcome not in USABLE_OUTCOMES:
                raise ContractError("system_map_outcome_invalid")
        areas = tuple(sorted(set(map_result.omitted_areas + missing)))
        fallback = self._live_fallback.discover(query, areas)
        self._validate_binding(query, fallback)
        closure = self._build_closure(fallback, True)
        if _missing_resources(query, fallback):
            return ImpactClosure(
                closure.nodes,
                closure.relations,
                closure.consumed_facts,
                True,
                False,
            )
        return closure

    def _validate_binding(self, query: MapQuery, result: MapResult) -> None:
        actual = (
            result.repository_id,
            result.requested_ref,
            result.resolved_commit,
        )
        expected = (query.repository_id, query.requested_ref, query.resolved_commit)
        if actual != expected:
            raise ContractError("system_map_view_mismatch")

    def _build_closure(
        self,
        result: MapResult,
        used_fallback: bool,
    ) -> ImpactClosure:
        facts = tuple(
            [f"node:{node}" for node in result.nodes]
            + [f"relation:{left}->{right}" for left, right in result.relations]
            + [
                f"resource:{resource}->{node}"
                for resource, node in result.resource_bindings
            ]
        )
        return ImpactClosure(
            nodes=result.nodes,
            relations=result.relations,
            consumed_facts=facts,
            used_live_fallback=used_fallback,
            complete=result.outcome == "usable_actual",
        )


@dataclass
class StaticSystemMapAdapter:
    result: MapResult
    queries: list[MapQuery] = field(default_factory=list)

    def query(self, query: MapQuery) -> MapResult:
        self.queries.append(query)
        return self.result


@dataclass
class StaticLiveSourceAdapter:
    result: MapResult
    requested_areas: tuple[str, ...] = ()
    queries: list[MapQuery] = field(default_factory=list)

    def discover(self, query: MapQuery, areas: tuple[str, ...]) -> MapResult:
        self.requested_areas = areas
        self.queries.append(query)
        return self.result


def _missing_resources(
    query: MapQuery,
    result: MapResult,
) -> tuple[str, ...]:
    bound = {resource for resource, _ in result.resource_bindings}
    return tuple(
        resource
        for resource in query.changed_resources
        if resource not in bound
    )


def _is_complete_map_result(
    result: MapResult,
    missing_resources: tuple[str, ...],
) -> bool:
    return (
        result.outcome in USABLE_OUTCOMES
        and not result.omitted_areas
        and not missing_resources
    )
