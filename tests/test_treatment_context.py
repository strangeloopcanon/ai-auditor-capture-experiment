import json
import unittest
from pathlib import Path

from auditor_capture.case_generation import generate_cases
from auditor_capture.orchestrator import response_context


class TreatmentContextTests(unittest.TestCase):
    def test_actor_access_disclosure_is_in_response_context(self) -> None:
        case = generate_cases(1)[0]
        treatment = {
            "persuasion": "argument_only",
            "actor_visibility": "verdict_only",
            "actor_auditor_access_disclosure": "raw_evidence_disclosed",
            "relationship": "one_shot",
            "backcheck": "no_explicit_backcheck",
        }
        actor_output = {"cited_evidence_ids": [], "audit_packet_summary": "summary"}
        auditor_initial = {"initial_verdict": "suspicious"}

        context = response_context(case, treatment, actor_output, auditor_initial)

        self.assertIn("auditor_evidence_access_disclosure", context)
        self.assertIn("full raw admissible evidence", context["auditor_evidence_access_disclosure"])

    def test_hidden_access_treatments_have_four_cells(self) -> None:
        treatments = json.loads(
            Path("config/treatments.hidden_access_integrity.json").read_text(encoding="utf-8")
        )
        cells = {
            (treatment["evidence_access"], treatment["actor_auditor_access_disclosure"])
            for treatment in treatments
        }

        self.assertEqual(len(treatments), 4)
        self.assertEqual(
            cells,
            {
                ("actor_summary_only", "summary_only_disclosed"),
                ("actor_summary_only", "raw_evidence_disclosed"),
                ("raw_evidence_access", "not_disclosed"),
                ("raw_evidence_access", "raw_evidence_disclosed"),
            },
        )


if __name__ == "__main__":
    unittest.main()
