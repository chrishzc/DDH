from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ddh.contracts import ContractError, parse_strict_json, publish_atomic_json


@dataclass(frozen=True)
class InvocationState:
    generation: int
    payload: dict[str, Any]


class AtomicJsonStateStore:
    def __init__(self, root: Path) -> None:
        self._root = root

    def load(self, invocation_id: str) -> InvocationState | None:
        path = self._path(invocation_id)
        if not path.exists():
            return None
        value = parse_strict_json(path.read_bytes())
        return InvocationState(value["generation"], value["payload"])

    def compare_and_swap(
        self,
        invocation_id: str,
        expected_generation: int | None,
        payload: dict[str, Any],
    ) -> InvocationState:
        current = self.load(invocation_id)
        current_generation = current.generation if current else None
        if current_generation != expected_generation:
            raise ContractError("state_generation_conflict")
        next_generation = 0 if current is None else current.generation + 1
        state = InvocationState(next_generation, payload)
        self._publish(invocation_id, state)
        return state

    def _publish(self, invocation_id: str, state: InvocationState) -> None:
        self._root.mkdir(parents=True, exist_ok=True)
        target = self._path(invocation_id)
        data = {"generation": state.generation, "payload": state.payload}
        publish_atomic_json(target, data)

    def _path(self, invocation_id: str) -> Path:
        if "/" in invocation_id or "\\" in invocation_id:
            raise ContractError("invocation_id_invalid")
        return self._root / f"{invocation_id}.json"
