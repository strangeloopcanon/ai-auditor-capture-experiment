import unittest

from auditor_capture.case_generation import DOMAINS, generate_borderline_cases, generate_cases, generate_locked_stress_cases


class CaseGenerationTests(unittest.TestCase):
    def test_generates_requested_domain_counts(self) -> None:
        cases = generate_cases(4)
        self.assertEqual(len(cases), len(DOMAINS) * 4)
        counts = {domain: 0 for domain in DOMAINS}
        for case in cases:
            counts[case["domain"]] += 1
        self.assertEqual(set(counts.values()), {4})

    def test_includes_gold_mine_cases(self) -> None:
        cases = generate_cases(8)
        gold = [case for case in cases if case["ground_truth_label"]["gold_mine_type_2"]]
        self.assertGreaterEqual(len(gold), len(DOMAINS) * 2)

    def test_locked_stress_cases_remove_escape_hatches(self) -> None:
        cases = generate_locked_stress_cases(2)
        self.assertEqual(len(cases), len(DOMAINS) * 2)
        for case in cases:
            self.assertEqual(len(case["action_options"]), 1)
            self.assertTrue(case["locked_decision"]["enabled"])
            self.assertTrue(case["locked_decision"]["safe_alternative_removed"])
            action = case["locked_decision"]["required_action"]
            self.assertEqual(case["action_options"], [action])
            self.assertEqual(case["support_rules"][action]["default_support_label"], "unsupported")

    def test_borderline_cases_remove_escape_hatches_but_stay_weakly_supported(self) -> None:
        cases = generate_borderline_cases(2)
        self.assertEqual(len(cases), len(DOMAINS) * 2)
        for case in cases:
            self.assertEqual(len(case["action_options"]), 1)
            self.assertTrue(case["locked_decision"]["enabled"])
            self.assertTrue(case["locked_decision"]["safe_alternative_removed"])
            action = case["locked_decision"]["required_action"]
            self.assertEqual(case["action_options"], [action])
            self.assertEqual(case["support_rules"][action]["default_support_label"], "weakly_supported")
            self.assertEqual(case["ground_truth_label"]["justification_support_target"], "weakly_supported")


if __name__ == "__main__":
    unittest.main()
