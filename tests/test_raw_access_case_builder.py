import unittest
from pathlib import Path

from auditor_capture.case_generation import load_source_note_packets
from scripts.build_raw_access_ab_cases import STALE_EXTENSION_TERMS, build_extension_packets


SOURCE_NOTES_FIXTURE = Path("data/source_notes/source_grounded_integrity_stress_25.json")


class RawAccessCaseBuilderTests(unittest.TestCase):
    def test_extension_packets_use_new_contexts_without_stale_template_terms(self) -> None:
        packets = load_source_note_packets(SOURCE_NOTES_FIXTURE)
        extension_packets = build_extension_packets(packets, start_index=16, end_index=30)
        payload = repr(extension_packets)

        self.assertEqual(len(extension_packets), 75)
        self.assertIn("fraud dispute review", payload)
        self.assertIn("supply-chain vendor screening", payload)
        self.assertIn("data/source_notes/source_grounded_raw_access_ab_150.json", payload)
        for stale_term in STALE_EXTENSION_TERMS:
            self.assertNotIn(stale_term, payload)

    def test_fresh_replication_contexts_are_available(self) -> None:
        packets = load_source_note_packets(SOURCE_NOTES_FIXTURE)
        extension_packets = build_extension_packets(packets, start_index=31, end_index=60)
        payload = repr(extension_packets)

        self.assertEqual(len(extension_packets), 150)
        self.assertIn("retirement plan servicing", payload)
        self.assertIn("clinical trial adverse-event intake", payload)
        self.assertIn("data/source_notes/source_grounded_raw_vs_summary_replication_150.json", payload)
        for stale_term in STALE_EXTENSION_TERMS:
            self.assertNotIn(stale_term, payload)


if __name__ == "__main__":
    unittest.main()
