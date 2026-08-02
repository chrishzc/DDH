from __future__ import annotations

import hashlib
import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any
from uuid import UUID


MAX_JSON_BYTES = 1_048_576
MAX_JSON_DEPTH = 32
MAX_JSON_ITEMS = 10_000
MAX_JSON_STRING_LENGTH = 262_144
MAX_SAFE_INTEGER = 9_007_199_254_740_991


class ContractError(ValueError):
    """Raised when authoritative contract data is invalid."""


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ContractError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _measure_depth(value: Any, depth: int = 0) -> int:
    if isinstance(value, dict):
        children = (_measure_depth(item, depth + 1) for item in value.values())
        return max(children, default=depth)
    if isinstance(value, (list, tuple)):
        children = (_measure_depth(item, depth + 1) for item in value)
        return max(children, default=depth)
    return depth


def _reject_constant(value: str) -> None:
    raise ContractError(f"json_number_invalid:{value}")


def _validate_authoritative_value(value: Any) -> None:
    if isinstance(value, float):
        raise ContractError("authoritative_float_prohibited")
    if isinstance(value, int) and abs(value) > MAX_SAFE_INTEGER:
        raise ContractError("authoritative_integer_out_of_range")
    if isinstance(value, str):
        _validate_string(value)
    if isinstance(value, dict):
        if len(value) > MAX_JSON_ITEMS:
            raise ContractError("json_object_too_large")
        for key, item in value.items():
            if not isinstance(key, str):
                raise ContractError("json_object_key_not_string")
            _validate_string(key)
            _validate_authoritative_value(item)
    if isinstance(value, (list, tuple)):
        if len(value) > MAX_JSON_ITEMS:
            raise ContractError("json_array_too_large")
        for item in value:
            _validate_authoritative_value(item)


def _validate_string(value: str) -> None:
    if len(value) > MAX_JSON_STRING_LENGTH:
        raise ContractError("json_string_too_large")
    if any(0xD800 <= ord(character) <= 0xDFFF for character in value):
        raise ContractError("json_unpaired_surrogate")


def parse_strict_json(raw: bytes, max_bytes: int = MAX_JSON_BYTES) -> Any:
    if len(raw) > max_bytes:
        raise ContractError("json_payload_too_large")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ContractError("json_not_utf8") from error
    value = json.loads(
        text,
        object_pairs_hook=_reject_duplicate_keys,
        parse_constant=_reject_constant,
    )
    if _measure_depth(value) > MAX_JSON_DEPTH:
        raise ContractError("json_payload_too_deep")
    _validate_authoritative_value(value)
    return value


def canonical_json_bytes(value: Any) -> bytes:
    _validate_authoritative_value(value)
    return _canonical_text(value).encode("utf-8")


def _canonical_text(value: Any) -> str:
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    if isinstance(value, (list, tuple)):
        return "[" + ",".join(_canonical_text(item) for item in value) + "]"
    if isinstance(value, dict):
        return _canonical_object(value)
    raise ContractError("authoritative_json_type_invalid")


def _canonical_object(value: dict[str, Any]) -> str:
    keys = sorted(value, key=lambda item: item.encode("utf-16-be"))
    members = [
        f"{_canonical_text(key)}:{_canonical_text(value[key])}"
        for key in keys
    ]
    return "{" + ",".join(members) + "}"


def content_digest(value: Any) -> str:
    digest = hashlib.sha256(canonical_json_bytes(value)).hexdigest()
    return f"sha256:{digest}"


@dataclass(frozen=True)
class AuthorityReference:
    authority_id: str
    version: str
    digest: str


@dataclass(frozen=True)
class CandidateReference:
    candidate_id: str
    generation: int
    digest: str


@dataclass(frozen=True)
class InvocationReference:
    invocation_id: str

    def __post_init__(self) -> None:
        UUID(self.invocation_id)


@dataclass(frozen=True)
class TypedResult:
    terminal_state: str
    acceptance_outcome: str
    verification_completeness: str
    reason_code: str
    retryable: bool


@dataclass(frozen=True)
class ContractEnvelope:
    protocol: str
    protocol_version: str
    message_type: str
    message_id: str
    correlation_id: str
    subject: dict[str, Any]
    payload: dict[str, Any]

    def to_bytes(self) -> bytes:
        return canonical_json_bytes(asdict(self))


ENVELOPE_FIELDS = {
    "protocol",
    "protocol_version",
    "message_type",
    "message_id",
    "correlation_id",
    "subject",
    "payload",
}


def parse_envelope(raw: bytes) -> ContractEnvelope:
    value = parse_strict_json(raw)
    if not isinstance(value, dict) or set(value) != ENVELOPE_FIELDS:
        raise ContractError("envelope_fields_invalid")
    if value["protocol"] != "ddh" or value["protocol_version"] != "1.0.0":
        raise ContractError("protocol_incompatible")
    return ContractEnvelope(**value)


def publish_atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pending = path.with_name(f"{path.name}.pending")
    pending.write_bytes(canonical_json_bytes(value))
    os.replace(pending, path)
