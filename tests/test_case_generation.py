import json
import tempfile
import unittest
from pathlib import Path

from auditor_capture.case_generation import (
    DOMAINS,
    generate_borderline_cases,
    generate_cases,
    generate_cases_from_source_notes,
    generate_locked_stress_cases,
    load_source_note_packets,
)

SOURCE_NOTES_FIXTURE = Path("data/source_notes/source_grounded_integrity_stress_25.json")


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

    def test_source_note_generation_preserves_provenance(self) -> None:
        packets = load_source_note_packets(SOURCE_NOTES_FIXTURE)
        cases = generate_cases_from_source_notes(packets)
        self.assertEqual(len(cases), 25)
        case = cases[0]
        self.assertEqual(case["case_id"], "source_model_card_stale_approval_001")
        self.assertEqual(case["generation_lane"], "source_notes")
        self.assertIn("source_provenance", case)
        self.assertEqual(case["source_provenance"]["schema_version"], "v1")
        self.assertGreaterEqual(case["source_provenance"]["source_note_count"], 1)
        for evidence in case["admissible_evidence"] + case["inadmissible_or_private_evidence"]:
            self.assertIn("source_note_ids", evidence)
            self.assertTrue(evidence["source_note_ids"])

    def test_source_note_generation_rejects_unknown_source_note_ids(self) -> None:
        packets = load_source_note_packets(SOURCE_NOTES_FIXTURE)
        packets[0]["case_blueprint"]["admissible_evidence"][0]["source_note_ids"] = ["missing"]
        with self.assertRaises(ValueError):
            generate_cases_from_source_notes(packets)

    def test_source_note_loader_accepts_jsonl(self) -> None:
        packets = load_source_note_packets(SOURCE_NOTES_FIXTURE)
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "source_notes.jsonl"
            path.write_text(json.dumps(packets[0]) + "\n", encoding="utf-8")
            loaded = load_source_note_packets(path)
        self.assertEqual(loaded[0]["case_id"], "source_model_card_stale_approval_001")


if __name__ == "__main__":
    unittest.main()
