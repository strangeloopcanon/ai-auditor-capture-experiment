import unittest

from auditor_capture.orchestrator import aggregate_metrics
from auditor_capture.stats import rate_summary, wilson_interval


METRIC_KEYS = [
    "false_compliance",
    "persuasion_induced_false_compliance",
    "legitimate_revision",
    "illegitimate_revision",
    "caveated_compliance",
    "deference_without_independent_evidence",
]


def transcript(treatment_id: str, **true_metrics: bool) -> dict:
    scoring_result = {key: False for key in METRIC_KEYS}
    scoring_result.update(true_metrics)
    return {
        "treatment_id": treatment_id,
        "scoring_result": scoring_result,
        "events": [{"stage": "actor_response", "output": {}}],
    }


class StatsTests(unittest.TestCase):
    def test_wilson_interval_matches_headline_source_grounded_rate(self) -> None:
        low, high = wilson_interval(13, 123)
        self.assertAlmostEqual(low, 0.06281252708773513)
        self.assertAlmostEqual(high, 0.172454136215156)

    def test_rate_summary_preserves_count_denominator_and_rate(self) -> None:
        summary = rate_summary(5, 123)
        self.assertEqual(summary["count"], 5)
        self.assertEqual(summary["n"], 123)
        self.assertAlmostEqual(summary["rate"], 5 / 123)
        self.assertIn("wilson_95_low", summary)
        self.assertIn("wilson_95_high", summary)

    def test_aggregate_metrics_includes_confidence_interval_fields(self) -> None:
        metrics = aggregate_metrics(
            [
                transcript("A", false_compliance=True),
                transcript("A"),
                transcript("B", false_compliance=True),
            ]
        )

        self.assertEqual(metrics["false_compliance"], 2)
        self.assertEqual(metrics["false_compliance_rate_denominator"], 3)
        self.assertAlmostEqual(metrics["false_compliance_rate"], 2 / 3)
        self.assertIn("false_compliance_rate_wilson_95_low", metrics)
        self.assertIn("false_compliance_rate_wilson_95_high", metrics)
        self.assertEqual(metrics["by_treatment"]["A"]["false_compliance"], 1)
        self.assertEqual(metrics["by_treatment"]["A"]["false_compliance_rate_denominator"], 2)
        self.assertAlmostEqual(metrics["by_treatment"]["A"]["false_compliance_rate"], 1 / 2)
        self.assertIn("false_compliance_rate_wilson_95_low", metrics["by_treatment"]["A"])

    def test_pifc_rate_uses_persuasion_opportunities(self) -> None:
        metrics = aggregate_metrics(
            [
                transcript("continued", persuasion_induced_false_compliance=True),
                {
                    "treatment_id": "skipped",
                    "scoring_result": {key: False for key in METRIC_KEYS},
                    "events": [{"stage": "auditor_initial", "output": {}}],
                },
            ]
        )

        self.assertEqual(metrics["persuasion_induced_false_compliance"], 1)
        self.assertEqual(metrics["persuasion_induced_false_compliance_rate_denominator"], 1)
        self.assertEqual(metrics["persuasion_induced_false_compliance_rate"], 1.0)


if __name__ == "__main__":
    unittest.main()
