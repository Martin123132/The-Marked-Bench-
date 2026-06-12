from __future__ import annotations

import json
from pathlib import Path
import unittest

from marked_bench.benchmark_scoring_spec import SCORE_WEIGHTS
from marked_bench.contradiction.benchmark_suite import evaluate_standard_suite


def _weighted_score(report: dict) -> float:
    metrics = report["metrics"]
    return round(
        100
        * (
            SCORE_WEIGHTS["contradiction_macro_f1"] * metrics["contradiction_macro_f1"]
            + SCORE_WEIGHTS["type_accuracy"] * metrics["type_accuracy"]
            + SCORE_WEIGHTS["binary_detection_f1"] * metrics["detection"]["f1"]
            + SCORE_WEIGHTS["coverage_index"] * metrics["coverage_index"]
        ),
        2,
    )


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


class ScoringSanityTests(unittest.TestCase):
    BASELINE_REPORTS = [
        Path("baselines/contradiction_engine_v0_1_0.json"),
        Path("baselines/always_none_v0_1_0.json"),
        Path("baselines/contradiction_engine_v0_1_1.json"),
        Path("baselines/always_none_v0_1_1.json"),
        Path("baselines/contradiction_engine_adversarial_v0_2_0.json"),
        Path("baselines/always_none_adversarial_v0_2_0.json"),
        Path("baselines/contradiction_engine_multihop_v0_3_0.json"),
        Path("baselines/always_none_multihop_v0_3_0.json"),
        Path("baselines/contradiction_engine_controls_v0_4_0.json"),
        Path("baselines/always_none_controls_v0_4_0.json"),
    ]
    SUITE_CHECKS = (
        "contradiction-v0.1.0",
        "contradiction",
        "contradiction-adversarial",
        "contradiction-multihop",
        "contradiction-controls",
    )

    def test_baseline_scores_are_bounded_and_formula_consistent(self) -> None:
        root = Path(__file__).resolve().parent.parent
        for relative_path in self.BASELINE_REPORTS:
            path = root / relative_path
            report = _load_json(path)

            score = float(report["overall_score"])
            self.assertGreaterEqual(score, 0.0)
            self.assertLessEqual(score, 100.0)
            self.assertEqual(report["overall_score"], _weighted_score(report))
            self.assertGreater(report["case_count"], 0)

    def test_strong_baselines_outperform_none_detector_baselines(self) -> None:
        for suite in self.SUITE_CHECKS:
            strong = evaluate_standard_suite(system_name="ScoringSanityStrong", suite=suite)
            weak = evaluate_standard_suite(lambda _claim: None, system_name="ScoringSanityWeak", suite=suite)

            self.assertGreater(
                strong["overall_score"],
                weak["overall_score"],
                f"{suite}: strong score should beat weak baseline",
            )


if __name__ == "__main__":
    unittest.main()
