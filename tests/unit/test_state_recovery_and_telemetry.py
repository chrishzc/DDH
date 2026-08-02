import json
import tempfile
import unittest
from pathlib import Path

from ddh.contracts import ContractError
from ddh.recovery import AttemptFingerprint, RecoveryController
from ddh.state import AtomicJsonStateStore
from ddh.telemetry import JsonlTelemetry, TelemetryEvent


class StateTests(unittest.TestCase):
    def test_compare_and_swap_rejects_stale_generation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = AtomicJsonStateStore(Path(directory))
            first = store.compare_and_swap("invocation", None, {"state": "ready"})
            self.assertEqual(0, first.generation)
            with self.assertRaisesRegex(ContractError, "generation_conflict"):
                store.compare_and_swap("invocation", None, {"state": "late"})

    def test_restart_loads_current_atomic_state(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            store = AtomicJsonStateStore(root)
            store.compare_and_swap("invocation", None, {"state": "ready"})
            restarted = AtomicJsonStateStore(root)
            self.assertEqual("ready", restarted.load("invocation").payload["state"])


class RecoveryTests(unittest.TestCase):
    def test_identical_failure_without_evidence_is_no_progress(self) -> None:
        controller = RecoveryController()
        fingerprint = AttemptFingerprint("input", "candidate", "strategy", "failure")
        first = controller.evaluate(fingerprint, False, False)
        second = controller.evaluate(fingerprint, False, False)
        self.assertTrue(first.may_continue)
        self.assertEqual("no_progress", second.reason_code)
        self.assertFalse(second.may_continue)

    def test_transient_recovery_is_bounded(self) -> None:
        controller = RecoveryController(transient_action_limit=2)
        dispositions = [
            controller.evaluate(
                AttemptFingerprint("input", str(index), "runner", "transient"),
                False,
                True,
            )
            for index in range(3)
        ]
        self.assertEqual(["recover", "recover", "blocked"], [item.outcome for item in dispositions])


class TelemetryTests(unittest.TestCase):
    def test_event_is_bounded_and_contains_no_raw_output(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "events.jsonl"
            telemetry = JsonlTelemetry(path)
            telemetry.emit(TelemetryEvent("started", "invocation", {"reason_code": "ok"}))
            event = json.loads(path.read_text())
            self.assertEqual("started", event["event_type"])
            self.assertNotIn("stdout", event["fields"])

    def test_sensitive_fields_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            telemetry = JsonlTelemetry(Path(directory) / "events.jsonl")
            with self.assertRaisesRegex(ValueError, "sensitive_field"):
                telemetry.emit(TelemetryEvent("bad", "invocation", {"prompt": "secret"}))


if __name__ == "__main__":
    unittest.main()
