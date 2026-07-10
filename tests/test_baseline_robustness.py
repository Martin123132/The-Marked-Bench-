from __future__ import annotations

from pathlib import Path
import unittest

from scripts.check_baseline_robustness import (
    build_baseline_robustness_artifact,
    run_baseline_robustness,
)


class BaselineRobustnessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        root = Path(__file__).resolve().parent.parent
        cls.results, cls.failures = run_baseline_robustness(root)
        cls.multihop = next(
            item for item in cls.results if item["track"] == "contradiction-multihop"
        )
        cls.diagnostic = cls.multihop["diagnostic"]

    def test_multihop_signal_is_reproduced_and_explained(self) -> None:
        self.assertEqual(self.failures, [])
        self.assertEqual(self.multihop["status"], "explained watchlist")
        self.assertEqual(self.diagnostic["status"], "explained")
        self.assertEqual(self.diagnostic["case_count"], 18)
        self.assertEqual(self.diagnostic["unique_case_id_count"], 18)
        self.assertEqual(self.diagnostic["observed_hash_score"], 45.93)
        self.assertEqual(self.diagnostic["engine_score"], 24.14)
        self.assertEqual(self.diagnostic["observed_recalculated"]["overall_score"], 45.93)

    def test_identifier_sensitivity_supports_both_diagnosed_drivers(self) -> None:
        sensitivity = self.diagnostic["salted_identifier_sensitivity"]

        self.assertEqual(sensitivity["samples"], 4096)
        self.assertGreaterEqual(sensitivity["share_below_observed"], 0.95)
        self.assertLessEqual(sensitivity["share_at_or_above_observed"], 0.05)
        self.assertGreaterEqual(sensitivity["share_above_engine"], 0.50)

    def test_case_outcomes_reconcile(self) -> None:
        self.assertEqual(
            self.diagnostic["case_outcome_counts"],
            {
                "both correct": 3,
                "engine only": 6,
                "hash only": 3,
                "neither correct": 6,
            },
        )
        self.assertEqual(sum(self.diagnostic["expected_label_counts"].values()), 18)
        self.assertEqual(sum(self.diagnostic["hash_prediction_counts"].values()), 18)

    def test_reviewer_artifact_contains_method_and_limitations(self) -> None:
        artifact = build_baseline_robustness_artifact(self.results, self.failures)

        self.assertIn("## Technical summary", artifact)
        self.assertIn("## Detection breadth and chance alignment create the score gap", artifact)
        self.assertIn("## The observed hash score is unstable under identifier changes", artifact)
        self.assertIn("## Case-level comparison", artifact)
        self.assertIn("## Limitations and robustness checks", artifact)
        self.assertIn("held-out evaluation split", artifact)


if __name__ == "__main__":
    unittest.main()
