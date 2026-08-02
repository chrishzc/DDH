import json
import tempfile
import unittest
from pathlib import Path

from ddh.confirmation import (
    authority_for_document,
    create_confirmation,
    expected_confirmation_phrase,
)
from ddh.contracts import (
    ContractEnvelope,
    ContractError,
    canonical_json_bytes,
    content_digest,
    parse_envelope,
    parse_strict_json,
    publish_atomic_json,
)
from ddh.specification import SpecificationCompiler


def workload_document() -> dict[str, object]:
    return {
        "specification_id": "WORKLOAD-001",
        "version": "1.0.0",
        "risk_class": "L1",
        "goal": "Normalize repository paths.",
        "expected_behavior": ["Windows separators become forward slashes."],
        "write_scope": ["src/path_normalizer.py"],
        "prohibitions": ["external_side_effects"],
        "acceptance_scenarios": ["PATH-001"],
        "budgets": {"agent_attempts": 2, "effective_context_tokens": 10000},
        "selected_nodes": ["PortableWorkspace/PathNormalizer"],
    }


class ContractTests(unittest.TestCase):
    def test_canonical_digest_is_key_order_independent(self) -> None:
        self.assertEqual(content_digest({"b": 2, "a": 1}), content_digest({"a": 1, "b": 2}))

    def test_authoritative_float_is_rejected(self) -> None:
        with self.assertRaisesRegex(ContractError, "authoritative_float_prohibited"):
            canonical_json_bytes({"threshold": 0.5})

    def test_duplicate_json_key_is_rejected(self) -> None:
        with self.assertRaisesRegex(ContractError, "duplicate JSON key"):
            parse_strict_json(b'{"value": 1, "value": 2}')

    def test_non_finite_json_number_is_rejected(self) -> None:
        with self.assertRaisesRegex(ContractError, "json_number_invalid"):
            parse_strict_json(b'{"value": NaN}')

    def test_jcs_key_order_uses_utf16_code_units(self) -> None:
        canonical = canonical_json_bytes({"\ue000": 1, "\U00010000": 2})
        self.assertEqual(
            '{"𐀀":2,"":1}'.encode("utf-8"),
            canonical,
        )

    def test_unknown_envelope_field_is_rejected(self) -> None:
        envelope = json.loads(
            ContractEnvelope(
                "ddh",
                "1.0.0",
                "work_request",
                "message-1",
                "correlation-1",
                {},
                {},
            ).to_bytes()
        )
        envelope["unknown"] = True
        with self.assertRaisesRegex(ContractError, "envelope_fields_invalid"):
            parse_envelope(json.dumps(envelope).encode())

    def test_atomic_json_leaves_no_pending_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "result.json"
            publish_atomic_json(target, {"outcome": "passed"})
            self.assertEqual({"outcome": "passed"}, json.loads(target.read_text()))
            self.assertFalse(target.with_name("result.json.pending").exists())


class SpecificationTests(unittest.TestCase):
    def test_exact_confirmation_compiles_workload(self) -> None:
        document = workload_document()
        authority = authority_for_document(document)
        phrase = expected_confirmation_phrase(authority)
        confirmation = create_confirmation(document, phrase, "trusted_host_ui")
        compiled = SpecificationCompiler().compile(document, confirmation)
        self.assertEqual(authority, compiled.authority)

    def test_missing_expected_behavior_rejects_before_work(self) -> None:
        document = workload_document()
        document["expected_behavior"] = []
        authority = authority_for_document(document)
        confirmation = create_confirmation(
            document,
            expected_confirmation_phrase(authority),
            "trusted_host_ui",
        )
        with self.assertRaisesRegex(ContractError, "specification_not_ready"):
            SpecificationCompiler().compile(document, confirmation)

    def test_confirmation_for_other_digest_is_rejected(self) -> None:
        document = workload_document()
        authority = authority_for_document(document)
        confirmation = create_confirmation(
            document,
            expected_confirmation_phrase(authority),
            "trusted_host_ui",
        )
        document["goal"] = "Changed after confirmation."
        with self.assertRaisesRegex(ContractError, "confirmation_mismatch"):
            SpecificationCompiler().compile(document, confirmation)

    def test_zero_agent_budget_is_rejected_before_execution(self) -> None:
        document = workload_document()
        document["budgets"] = {
            **document["budgets"],
            "agent_attempts": 0,
        }
        authority = authority_for_document(document)
        confirmation = create_confirmation(
            document,
            expected_confirmation_phrase(authority),
            "trusted_host_ui",
        )
        with self.assertRaisesRegex(ContractError, "budget_invalid"):
            SpecificationCompiler().compile(document, confirmation)


if __name__ == "__main__":
    unittest.main()
