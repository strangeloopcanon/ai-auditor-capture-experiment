import json
import unittest
from pathlib import Path

from auditor_capture.call_budget import plan_budget
from auditor_capture.case_generation import generate_cases
from auditor_capture.orchestrator import assign_balanced_stratified


class CallBudgetTests(unittest.TestCase):
    def test_full_mvp_without_judge_is_4200_calls(self) -> None:
        treatments = json.loads(Path("config/treatments.json").read_text(encoding="utf-8"))
        budget = plan_budget(150, treatments, include_appeals_judge=False)
        self.assertEqual(budget["calls_per_case_across_treatments"], 28)
        self.assertEqual(budget["total_calls"], 4200)

    def test_full_mvp_with_judge_is_5400_calls(self) -> None:
        treatments = json.loads(Path("config/treatments.json").read_text(encoding="utf-8"))
        budget = plan_budget(150, treatments, include_appeals_judge=True)
        self.assertEqual(budget["calls_per_case_across_treatments"], 36)
        self.assertEqual(budget["total_calls"], 5400)

    def test_balanced_stratified_assignment_keeps_target_counts(self) -> None:
        cases = generate_cases(50)
        treatments = json.loads(Path("config/treatments.json").read_text(encoding="utf-8"))
        assignments = assign_balanced_stratified(cases, treatments)
        counts = {}
        for _, treatment in assignments:
            counts[treatment["treatment_id"]] = counts.get(treatment["treatment_id"], 0) + 1
        self.assertEqual(counts["C1_raw_no_response"], 19)
        self.assertEqual(counts["C2_summary_no_response"], 19)
        self.assertEqual(counts["C6_summary_argument_preregistered"], 19)
        self.assertEqual(counts["C7_summary_urgency_client_pressure"], 18)
        self.assertEqual(counts["C8_summary_urgency_backcheck"], 18)

    def test_balanced_stratified_assignment_seed_is_reproducible(self) -> None:
        cases = generate_cases(10)
        treatments = json.loads(Path("config/treatments.borderline.json").read_text(encoding="utf-8"))
        first = assign_balanced_stratified(cases, treatments, seed=20260516)
        second = assign_balanced_stratified(cases, treatments, seed=20260516)

        first_pairs = [(case["case_id"], treatment["treatment_id"]) for case, treatment in first]
        second_pairs = [(case["case_id"], treatment["treatment_id"]) for case, treatment in second]
        self.assertEqual(first_pairs, second_pairs)


if __name__ == "__main__":
    unittest.main()
