import json
import unittest
from pathlib import Path

from auditor_capture.case_generation import generate_cases
from auditor_capture.orchestrator import (
    actor_response_requirement_text,
    auditor_final_review_requirement_text,
    final_audit_context,
    response_context,
    treatment_context_for_actor,
)


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

    def test_summary_neutral_treatment_is_not_disclosed(self) -> None:
        treatments = json.loads(
            Path("config/treatments.summary_neutral_integrity.json").read_text(encoding="utf-8")
        )

        self.assertEqual(len(treatments), 1)
        self.assertEqual(treatments[0]["treatment_id"], "RVS1_summary_not_disclosed_integrity")
        self.assertEqual(treatments[0]["evidence_access"], "actor_summary_only")
        self.assertEqual(treatments[0]["actor_auditor_access_disclosure"], "not_disclosed")

    def test_raw_vs_summary_neutral_treatments_share_actor_disclosure(self) -> None:
        treatments = json.loads(
            Path("config/treatments.raw_vs_summary_neutral_integrity.json").read_text(
                encoding="utf-8"
            )
        )

        self.assertEqual(
            {treatment["evidence_access"] for treatment in treatments},
            {"actor_summary_only", "raw_evidence_access"},
        )
        self.assertEqual(
            {treatment["actor_auditor_access_disclosure"] for treatment in treatments},
            {"not_disclosed"},
        )

    def test_auditor_only_treatment_fields_are_hidden_from_actor(self) -> None:
        treatment = {
            "treatment_id": "M1_raw_hidden_integrity",
            "relationship": "one_shot",
            "backcheck": "no_explicit_backcheck",
            "_auditor_final_review_mode": "unresolved_concern_accounting",
        }

        actor_context = treatment_context_for_actor(treatment)

        self.assertNotIn("_auditor_final_review_mode", actor_context)
        self.assertNotIn("treatment_id", actor_context)

    def test_auditor_access_fields_are_hidden_from_actor_decision(self) -> None:
        treatment = {
            "treatment_id": "H3_raw_hidden_access_integrity",
            "evidence_access": "raw_evidence_access",
            "actor_auditor_access_disclosure": "not_disclosed",
            "auditor_precommitment": "no_preregistration",
            "actor_visibility": "full_auditor_rationale",
            "auditor_integrity_reminder": "hidden",
            "selective_continuation": True,
            "persuasion": "argument_only",
            "relationship": "one_shot",
            "backcheck": "no_explicit_backcheck",
        }

        actor_context = treatment_context_for_actor(treatment)

        self.assertEqual(actor_context["persuasion"], "argument_only")
        self.assertEqual(actor_context["relationship"], "one_shot")
        self.assertEqual(actor_context["backcheck"], "no_explicit_backcheck")
        self.assertNotIn("evidence_access", actor_context)
        self.assertNotIn("actor_auditor_access_disclosure", actor_context)

    def test_accounting_treatment_adds_final_review_requirement(self) -> None:
        treatment = {"_auditor_final_review_mode": "unresolved_concern_accounting"}

        text = auditor_final_review_requirement_text(treatment)

        self.assertIn("For each initial `specific_concerns` item", text)
        self.assertIn("keep it in `remaining_concerns`", text)

    def test_state_tracking_stress_treatment_adds_actor_response_requirement(self) -> None:
        treatment = {"_actor_response_mode": "state_tracking_stress"}

        text = actor_response_requirement_text(treatment)

        self.assertIn("address the initial concerns out of order", text)
        self.assertIn("do not add new evidence IDs", text)

    def test_compressed_handoff_replaces_itemized_initial_report(self) -> None:
        case = generate_cases(1)[0]
        treatment = {
            "evidence_access": "raw_evidence_access",
            "auditor_precommitment": "no_preregistration",
            "backcheck": "no_explicit_backcheck",
            "relationship": "one_shot",
            "_auditor_final_context_mode": "compressed_handoff",
        }
        actor_output = {"cited_evidence_ids": [], "audit_packet_summary": "summary"}
        auditor_initial = {
            "initial_verdict": "suspicious",
            "initial_risk_score": 0.7,
            "claim_being_audited": "claim",
            "specific_concerns": ["first concern", "second concern"],
            "unsupported_claims": ["unsupported"],
            "evidence_requests": ["request"],
            "decision_criteria": ["criterion"],
        }
        actor_response = {"argument_summary": "response"}

        context = final_audit_context(
            case,
            treatment,
            actor_output,
            auditor_initial,
            actor_response,
        )

        report = context["initial_audit_report"]
        self.assertEqual(report["handoff_mode"], "compressed_state_tracking_handoff")
        self.assertEqual(report["concern_count_from_prior_workpaper"], 2)
        self.assertNotIn("specific_concerns", report)

    def test_compressed_handoff_adds_final_review_requirement(self) -> None:
        treatment = {"_auditor_final_review_mode": "compressed_handoff"}

        text = auditor_final_review_requirement_text(treatment)

        self.assertIn("compressed handoff", text)
        self.assertIn("incomplete state", text)


if __name__ == "__main__":
    unittest.main()
