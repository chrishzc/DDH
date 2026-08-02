from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


PROHIBITED_EVENT_FIELDS = {
    "prompt",
    "source",
    "stdout",
    "stderr",
    "secret",
    "credential",
}


@dataclass(frozen=True)
class TelemetryEvent:
    event_type: str
    invocation_id: str
    fields: dict[str, Any]


class JsonlTelemetry:
    def __init__(self, path: Path, max_event_bytes: int = 8192) -> None:
        self._path = path
        self._max_event_bytes = max_event_bytes

    def emit(self, event: TelemetryEvent) -> None:
        if PROHIBITED_EVENT_FIELDS & event.fields.keys():
            raise ValueError("telemetry_sensitive_field_prohibited")
        record = {
            "timestamp": datetime.now(UTC).isoformat(),
            "event_type": event.event_type,
            "invocation_id": event.invocation_id,
            "fields": event.fields,
        }
        encoded = json.dumps(record, ensure_ascii=False, sort_keys=True)
        if len(encoded.encode("utf-8")) > self._max_event_bytes:
            raise ValueError("telemetry_event_too_large")
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with self._path.open("a", encoding="utf-8", newline="\n") as stream:
            stream.write(encoded + "\n")

