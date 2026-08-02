from __future__ import annotations

from dataclasses import dataclass

from ddh.contracts import content_digest


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

