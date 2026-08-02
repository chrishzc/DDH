import unittest

from ddh.agent_driver import AgentResult, AgentResultInbox, WorkRequest
from ddh.context import ContextEnvelope
from ddh.contracts import AuthorityReference


class AgentResultStressTests(unittest.TestCase):
    def test_ten_thousand_stale_duplicate_and_late_results_are_bounded(self) -> None:
        authority = AuthorityReference("SPEC", "1", "sha256:spec")
        context = ContextEnvelope(0, (), (), 0, "sha256:context")
        request = WorkRequest(
            "invocation-current",
            authority,
            7,
            "goal",
            ("src/**",),
            ("SCENARIO",),
            context,
        )
        stale = tuple(
            AgentResult(
                f"invocation-old-{index}",
                authority,
                index % 7,
                "patch_proposal",
                {},
            )
            for index in range(9998)
        )
        current = AgentResult(
            request.invocation_id,
            authority,
            request.candidate_generation,
            "patch_proposal",
            {"src/module.py": "fixed"},
        )
        selection = AgentResultInbox().select_current(
            request,
            stale + (current, current),
        )
        self.assertEqual(current, selection.current)
        self.assertEqual(9998, selection.stale_count)
        self.assertEqual(1, selection.duplicate_count)


if __name__ == "__main__":
    unittest.main()
