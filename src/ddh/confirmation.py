from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

from ddh.contracts import AuthorityReference, ContractError, content_digest, publish_atomic_json
from ddh.specification import ConfirmationRecord


def authority_for_document(document: dict[str, object]) -> AuthorityReference:
    return AuthorityReference(
        str(document["specification_id"]),
        str(document["version"]),
        content_digest(document),
    )


def expected_confirmation_phrase(authority: AuthorityReference) -> str:
    return (
        f"CONFIRM {authority.authority_id}@{authority.version} "
        f"{authority.digest}"
    )


def create_confirmation(
    document: dict[str, object],
    phrase: str,
    human_channel: str,
) -> ConfirmationRecord:
    authority = authority_for_document(document)
    if phrase != expected_confirmation_phrase(authority):
        raise ContractError("confirmation_phrase_mismatch")
    if human_channel not in {"local_cli", "trusted_host_ui"}:
        raise ContractError("confirmation_channel_untrusted")
    return ConfirmationRecord(authority, human_channel)


def publish_confirmation(path: Path, confirmation: ConfirmationRecord) -> None:
    publish_atomic_json(path, asdict(confirmation))

