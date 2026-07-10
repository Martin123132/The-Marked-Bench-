from __future__ import annotations

"""Build a reviewer-facing baseline robustness diagnostic."""

import argparse
import hashlib
import json
import random
from collections import Counter
from pathlib import Path
from statistics import mean, median
from typing import Any, Mapping, Sequence


ROOT_PATH = Path(__file__).resolve().parent.parent

TRACKS = (
    {
        "track": "contradiction",
        "leaderboard": Path("leaderboard/leaderboard_v0_1_1.json"),
        "task_aware": "ContradictionEngine",
        "low_information": "HashPriorBaseline",
    },
    {
        "track": "contradiction-adversarial",
        "leaderboard": Path("leaderboard/leaderboard_adversarial_v0_2_0.json"),
        "task_aware": "ContradictionEngine",
        "low_information": "HashPriorBaseline",
    },
    {
        "track": "contradiction-multihop",
        "leaderboard": Path("leaderboard/leaderboard_multihop_v0_3_0.json"),
        "task_aware": "ContradictionEngine",
        "low_information": "HashPriorBaseline",
    },
    {
        "track": "contradiction-controls",
        "leaderboard": Path("leaderboard/leaderboard_controls_v0_4_0.json"),
        "task_aware": "ContradictionEngine",
        "low_information": "HashPriorBaseline",
    },
)

EXPECTED_LOW_INFORMATION_WATCHLIST = {
    "contradiction-multihop": (
        "explained watchlist: the task-aware reference lacks multi-hop coverage and the observed "
        "hash assignment is unusually favorable; keep this track watchlisted before expansion"
    ),
}

MULTIHOP_SUITE = Path("suites/marked_bench_contradiction_multihop_v0_3_0.json")
MULTIHOP_HASH_REPORT = Path("baselines/hash_prior_multihop_v0_3_0.json")
MULTIHOP_ENGINE_REPORT = Path("baselines/contradiction_engine_multihop_v0_3_0.json")
SENSITIVITY_SAMPLE_COUNT = 4096
SENSITIVITY_RANDOM_SEED = 20260710

# This order mirrors the hash-prior detector in marked_bench.benchmark_cli.
HASH_PRIOR_LABELS = (
    "none",
    "direct_negation",
    "property_mismatch",
    "definitional_violation",
    "universal_counterexample",
    "temporal_conflict",
)
CONTRADICTION_LABELS = tuple(label for label in HASH_PRIOR_LABELS if label != "none")

SCORE_COMPONENTS = (
    ("contradiction_macro_f1", "Contradiction macro F1"),
    ("type_accuracy", "Type accuracy"),
    ("binary_detection_f1", "Detection F1"),
    ("coverage_index", "Coverage index"),
)


def run_baseline_robustness(root: Path = ROOT_PATH) -> tuple[list[dict[str, Any]], list[str]]:
    results: list[dict[str, Any]] = []
    failures: list[str] = []

    for track in TRACKS:
        leaderboard_path = Path(track["leaderboard"])
        leaderboard = _read_json(root / leaderboard_path)
        entries = {
            str(entry.get("system_name")): entry
            for entry in leaderboard.get("entries", [])
            if isinstance(entry, dict)
        }
        task_aware = entries.get(str(track["task_aware"]))
        low_information = entries.get(str(track["low_information"]))
        track_name = str(track["track"])

        if task_aware is None:
            failures.append(f"{track_name}: missing task-aware baseline {track['task_aware']}")
            continue
        if low_information is None:
            failures.append(f"{track_name}: missing low-information baseline {track['low_information']}")
            continue

        task_rank = int(task_aware.get("rank", 0))
        low_rank = int(low_information.get("rank", 0))
        low_information_ahead = low_rank < task_rank
        expected_note = EXPECTED_LOW_INFORMATION_WATCHLIST.get(track_name)

        if low_information_ahead and expected_note is None:
            failures.append(f"{track_name}: low-information baseline unexpectedly outranks task-aware baseline")
        if not low_information_ahead and expected_note is not None:
            failures.append(f"{track_name}: watchlist entry is stale; low-information baseline no longer outranks")

        item: dict[str, Any] = {
            "track": track_name,
            "leaderboard": leaderboard_path.as_posix(),
            "task_aware": str(track["task_aware"]),
            "task_aware_rank": task_rank,
            "task_aware_score": float(task_aware.get("overall_score", 0.0)),
            "low_information": str(track["low_information"]),
            "low_information_rank": low_rank,
            "low_information_score": float(low_information.get("overall_score", 0.0)),
            "status": "watchlist" if low_information_ahead else "pass",
            "note": expected_note or "low-information baseline does not outrank task-aware baseline",
        }

        if track_name == "contradiction-multihop":
            diagnostic, diagnostic_failures = analyze_multihop_signal(root)
            item["diagnostic"] = diagnostic
            failures.extend(f"{track_name}: {failure}" for failure in diagnostic_failures)
            if low_information_ahead and not diagnostic_failures:
                item["status"] = "explained watchlist"

        results.append(item)

    return results, failures


def analyze_multihop_signal(
    root: Path = ROOT_PATH,
    *,
    sample_count: int = SENSITIVITY_SAMPLE_COUNT,
) -> tuple[dict[str, Any], list[str]]:
    """Explain the multi-hop ranking with score and identifier sensitivity cuts."""

    if sample_count <= 0:
        raise ValueError("sample_count must be positive")

    suite = _read_json(root / MULTIHOP_SUITE)
    hash_report = _read_json(root / MULTIHOP_HASH_REPORT)
    engine_report = _read_json(root / MULTIHOP_ENGINE_REPORT)
    cases = [item for item in suite.get("cases", []) if isinstance(item, dict)]
    case_ids = [str(item.get("id")) for item in cases]
    expected = [str(item.get("expected")) for item in cases]
    failures: list[str] = []

    if len(case_ids) != int(suite.get("case_count", -1)):
        failures.append("suite case_count does not match the case records")
    if len(case_ids) != len(set(case_ids)):
        failures.append("suite case IDs are not unique")
    if set(suite.get("labels", [])) != set(HASH_PRIOR_LABELS):
        failures.append("suite labels no longer match the hash-prior label set")

    hash_predictions = _ordered_predictions(hash_report, case_ids, MULTIHOP_HASH_REPORT)
    engine_predictions = _ordered_predictions(engine_report, case_ids, MULTIHOP_ENGINE_REPORT)
    scoring_weights = {
        str(key): float(value)
        for key, value in suite.get("scoring", {}).get("overall_score_weights", {}).items()
    }
    required_weights = {key for key, _label in SCORE_COMPONENTS}
    if set(scoring_weights) != required_weights:
        failures.append("suite scoring weights no longer match the four-component scoring contract")

    observed_score = float(hash_report.get("overall_score", 0.0))
    engine_score = float(engine_report.get("overall_score", 0.0))
    observed_recalculated = _score_predictions(expected, hash_predictions, scoring_weights)
    if observed_recalculated["overall_score"] != observed_score:
        failures.append(
            "hash-prior report score does not reproduce from checked-in case predictions "
            f"({observed_score:.2f} != {observed_recalculated['overall_score']:.2f})"
        )

    salted_scores = []
    for salt in range(sample_count):
        predictions = []
        for case_id in case_ids:
            digest = hashlib.sha256(f"{salt}:{case_id}".encode("utf-8")).hexdigest()
            predictions.append(HASH_PRIOR_LABELS[int(digest[:8], 16) % len(HASH_PRIOR_LABELS)])
        salted_scores.append(_score_predictions(expected, predictions, scoring_weights))

    rng = random.Random(SENSITIVITY_RANDOM_SEED)
    permuted_scores = []
    for _index in range(sample_count):
        predictions = list(hash_predictions)
        rng.shuffle(predictions)
        permuted_scores.append(_score_predictions(expected, predictions, scoring_weights))

    salted_summary = _distribution_summary(salted_scores, observed_score, engine_score)
    permuted_summary = _distribution_summary(permuted_scores, observed_score, engine_score)
    component_rows = _component_rows(hash_report, engine_report, scoring_weights)

    if observed_score <= engine_score:
        failures.append("multi-hop hash-prior lead is stale")
    if salted_summary["share_at_or_above_observed"] > 0.05:
        failures.append("observed hash score is no longer an unusually favorable identifier assignment")
    if salted_summary["share_above_engine"] < 0.50:
        failures.append("task-aware coverage weakness no longer explains most salted hash comparisons")
    if int(engine_report.get("metrics", {}).get("detection", {}).get("true_positive", -1)) != 1:
        failures.append("task-aware multi-hop true-positive count changed; refresh the diagnosis")

    component_gap = round(sum(float(item["gap_points"]) for item in component_rows), 4)
    if abs(component_gap - (observed_score - engine_score)) > 0.02:
        failures.append("score component decomposition does not reconcile to the leaderboard gap")

    case_outcomes = []
    for case, engine_prediction, hash_prediction in zip(cases, engine_predictions, hash_predictions):
        expected_label = str(case["expected"])
        engine_correct = engine_prediction == expected_label
        hash_correct = hash_prediction == expected_label
        if engine_correct and hash_correct:
            outcome = "both correct"
        elif engine_correct:
            outcome = "engine only"
        elif hash_correct:
            outcome = "hash only"
        else:
            outcome = "neither correct"
        case_outcomes.append(
            {
                "case_id": str(case["id"]),
                "expected": expected_label,
                "engine_prediction": engine_prediction,
                "hash_prediction": hash_prediction,
                "outcome": outcome,
            }
        )

    diagnostic = {
        "status": "explained" if not failures else "review required",
        "suite_id": str(suite.get("suite_id")),
        "suite_version": str(suite.get("suite_version")),
        "case_count": len(cases),
        "unique_case_id_count": len(set(case_ids)),
        "expected_label_counts": _ordered_counts(expected),
        "hash_prediction_counts": _ordered_counts(hash_predictions),
        "observed_hash_score": observed_score,
        "engine_score": engine_score,
        "score_gap": round(observed_score - engine_score, 2),
        "observed_recalculated": observed_recalculated,
        "hash_detection": dict(hash_report.get("metrics", {}).get("detection", {})),
        "engine_detection": dict(engine_report.get("metrics", {}).get("detection", {})),
        "component_rows": component_rows,
        "salted_identifier_sensitivity": salted_summary,
        "fixed_label_mix_permutations": permuted_summary,
        "case_outcomes": case_outcomes,
        "case_outcome_counts": dict(sorted(Counter(item["outcome"] for item in case_outcomes).items())),
        "sample_count": sample_count,
        "random_seed": SENSITIVITY_RANDOM_SEED,
    }
    return diagnostic, failures


def build_baseline_robustness_artifact(results: list[dict[str, Any]], failures: list[str]) -> str:
    status = "PASS" if not failures else "FAIL"
    diagnostic = next(
        (item.get("diagnostic") for item in results if item.get("track") == "contradiction-multihop"),
        None,
    )
    lines = [
        "# Baseline Robustness Diagnostic",
        "",
        "## Technical summary",
        "",
        f"- Overall guard status: **{status}**.",
    ]

    if isinstance(diagnostic, dict):
        salted = diagnostic["salted_identifier_sensitivity"]
        hash_detection = diagnostic["hash_detection"]
        engine_detection = diagnostic["engine_detection"]
        lines.extend(
            [
                (
                    "- The multi-hop ranking gap is explained, not removed: `HashPriorBaseline` scores "
                    f"{diagnostic['observed_hash_score']:.2f} versus {diagnostic['engine_score']:.2f}, a "
                    f"{diagnostic['score_gap']:.2f}-point lead."
                ),
                (
                    f"- The observed hash assignment is unusually favorable: only "
                    f"{_percent(salted['share_at_or_above_observed'])} of "
                    f"{salted['samples']:,} deterministic salted-ID variants score as highly."
                ),
                (
                    "- The task-aware reference is also underpowered for this track: it finds "
                    f"{engine_detection['true_positive']} of 10 contradiction cases, while the hash baseline "
                    f"finds {hash_detection['true_positive']} by predicting a contradiction on 15 of 18 cases."
                ),
                (
                    f"- Identifier luck alone is not the full cause: {_percent(salted['share_above_engine'])} "
                    "of salted-ID variants still beat the current engine. The leaderboard order must remain an "
                    "explained watchlist item until a genuinely multi-hop reference baseline is added."
                ),
            ]
        )
    else:
        lines.append("- The detailed multi-hop diagnosis could not be produced.")

    lines.extend(
        [
            "",
            "## Track comparison",
            "",
            "Low-information baselines are diagnostic references, not task-aware systems.",
            "",
            "| Track | Task-aware rank | Task-aware score | Low-information rank | Low-information score | Status | Note |",
            "| --- | ---: | ---: | ---: | ---: | --- | --- |",
        ]
    )
    for item in results:
        lines.append(
            "| {track} | {task_aware_rank} | {task_aware_score:.2f} | "
            "{low_information_rank} | {low_information_score:.2f} | {status} | {note} |".format(**item)
        )

    if isinstance(diagnostic, dict):
        lines.extend(
            [
                "",
                "## Detection breadth and chance alignment create the score gap",
                "",
                "The scoring decomposition reconciles the complete leaderboard difference. Positive gaps favor the hash baseline.",
                "",
                "| Component | Weight | Engine points | Hash points | Gap points |",
                "| --- | ---: | ---: | ---: | ---: |",
            ]
        )
        for item in diagnostic["component_rows"]:
            lines.append(
                f"| {item['label']} | {_percent(item['weight'])} | {item['engine_points']:.2f} | "
                f"{item['hash_points']:.2f} | {item['gap_points']:+.2f} |"
            )

        lines.extend(
            [
                "",
                "Detection F1 and coverage contribute most of the lead because broad non-`none` guesses receive "
                "credit when the engine abstains on multi-hop contradictions. Type accuracy favors the engine, but "
                "not enough to offset those components.",
                "",
                "## The observed hash score is unstable under identifier changes",
                "",
                "Both sensitivity checks preserve the 18 expected labels and the public scoring formula.",
                "",
                "| Sensitivity check | Samples | Median score | 95th percentile | Beat engine | At or above observed |",
                "| --- | ---: | ---: | ---: | ---: | ---: |",
            ]
        )
        for label, key in (
            ("Salted identifier namespaces", "salted_identifier_sensitivity"),
            ("Fixed hash-label mix, permuted across cases", "fixed_label_mix_permutations"),
        ):
            summary = diagnostic[key]
            lines.append(
                f"| {label} | {summary['samples']:,} | {summary['median']:.2f} | {summary['p95']:.2f} | "
                f"{_percent(summary['share_above_engine'])} | "
                f"{_percent(summary['share_at_or_above_observed'])} |"
            )

        lines.extend(
            [
                "",
                "The result supports two simultaneous conclusions: the exact `45.93` score is a chance-favorable "
                "ID assignment, and the engine's missing multi-hop coverage makes the ranking vulnerable to many "
                "low-information assignments.",
                "",
                "## Case-level comparison",
                "",
                "| Case | Expected | Engine prediction | Hash prediction | Exact-label outcome |",
                "| --- | --- | --- | --- | --- |",
            ]
        )
        for item in diagnostic["case_outcomes"]:
            lines.append(
                f"| `{item['case_id']}` | `{item['expected']}` | `{item['engine_prediction']}` | "
                f"`{item['hash_prediction']}` | {item['outcome']} |"
            )

        lines.extend(
            [
                "",
                "## Scope, data, and metric definitions",
                "",
                f"- Population: all {diagnostic['case_count']} cases in "
                f"`{diagnostic['suite_id']}` v{diagnostic['suite_version']}.",
                f"- Grain: one expected and predicted contradiction label per unique case ID; "
                f"{diagnostic['unique_case_id_count']} unique IDs were verified.",
                "- Overall score: weighted points from contradiction macro F1 (45%), exact type accuracy (25%), "
                "binary contradiction detection F1 (20%), and contradiction-label coverage (10%).",
                "- Comparison baseline: checked-in `ContradictionEngine` and `HashPriorBaseline` reports for the "
                "same immutable suite hash.",
                "",
                "Expected label mix:",
                "",
                "| Label | Expected cases | Hash predictions |",
                "| --- | ---: | ---: |",
            ]
        )
        for label in HASH_PRIOR_LABELS:
            lines.append(
                f"| `{label}` | {diagnostic['expected_label_counts'][label]} | "
                f"{diagnostic['hash_prediction_counts'][label]} |"
            )

        lines.extend(
            [
                "",
                "## Methodology",
                "",
                "1. Recompute the observed hash score directly from the checked-in case predictions.",
                "2. Attribute the leaderboard gap to the four public weighted score components.",
                f"3. Generate {diagnostic['sample_count']:,} deterministic alternative hash assignments by "
                "prefixing each case ID with an integer namespace before SHA-256 mapping.",
                f"4. Generate {diagnostic['sample_count']:,} deterministic permutations of the observed hash "
                f"label mix using seed `{diagnostic['random_seed']}`.",
                "5. Compare each simulated score with the observed hash score and current engine score.",
                "",
                "Run or regenerate this artifact with:",
                "",
                "```bash",
                "python scripts/check_baseline_robustness.py --artifact docs/BASELINE_ROBUSTNESS.md",
                "```",
                "",
                "## Limitations and robustness checks",
                "",
                "- This is a descriptive sensitivity analysis over a small 18-case public suite, not a claim of "
                "causal or statistical model superiority.",
                "- The suite manifest publishes expected labels. This analysis checks scoring and baseline behavior; "
                "it does not provide resistance to answer lookup or benchmark gaming.",
                "- A blind ranking would require a held-out evaluation split, non-revealing evaluation identifiers, "
                "and controlled access to expected labels.",
                "- The simulation is deterministic and CI-friendly. Its thresholds intentionally fail when the "
                "engine, suite, reports, or interpretation changes, forcing a reviewer to refresh the public note.",
                "",
                "## Recommended next steps",
                "",
                "1. Preserve published multi-hop suite v0.3.0 and its case IDs unchanged.",
                "2. Keep the current leaderboard marked as an explained watchlist, not evidence that the hash baseline "
                "is a stronger contradiction system.",
                "3. Before expanding the track, add a genuinely multi-hop task-aware reference and require it to beat "
                "low-information sensitivity medians across detection, type, and coverage components.",
                "4. If future claims need gaming resistance, design a separately versioned held-out evaluation path.",
                "",
                "## Further questions",
                "",
                "- Which deterministic multi-hop reasoning baseline should become the next task-aware reference?",
                "- Should a future public release separate transparent development cases from held-out ranking cases?",
            ]
        )

    if failures:
        lines.extend(["", "## Failures", ""])
        for failure in failures:
            lines.append(f"- {failure}")

    return "\n".join(lines) + "\n"


def _ordered_predictions(report: Mapping[str, Any], case_ids: Sequence[str], path: Path) -> list[str]:
    records = [item for item in report.get("case_results", []) if isinstance(item, dict)]
    by_case = {str(item.get("case_id")): str(item.get("predicted")) for item in records}
    if len(by_case) != len(records):
        raise ValueError(f"{path}: duplicate case predictions")
    if set(by_case) != set(case_ids):
        missing = sorted(set(case_ids) - set(by_case))
        extra = sorted(set(by_case) - set(case_ids))
        raise ValueError(f"{path}: case coverage mismatch; missing={missing}, extra={extra}")
    return [by_case[case_id] for case_id in case_ids]


def _score_predictions(
    expected: Sequence[str],
    predicted: Sequence[str],
    weights: Mapping[str, float],
) -> dict[str, float]:
    if len(expected) != len(predicted):
        raise ValueError("expected and predicted labels must have equal length")
    confusion = {
        actual: {guess: 0 for guess in HASH_PRIOR_LABELS}
        for actual in HASH_PRIOR_LABELS
    }
    for actual, guess in zip(expected, predicted):
        if actual not in confusion or guess not in confusion[actual]:
            raise ValueError(f"unknown score label: expected={actual!r}, predicted={guess!r}")
        confusion[actual][guess] += 1

    class_f1 = []
    covered = 0
    for label in CONTRADICTION_LABELS:
        true_positive = confusion[label][label]
        false_positive = sum(confusion[other][label] for other in HASH_PRIOR_LABELS if other != label)
        false_negative = sum(confusion[label][other] for other in HASH_PRIOR_LABELS if other != label)
        support = sum(confusion[label].values())
        precision = true_positive / max(true_positive + false_positive, 1)
        recall = true_positive / max(true_positive + false_negative, 1)
        if support > 0:
            class_f1.append(2 * precision * recall / max(precision + recall, 1e-9))
        if support > 0 and recall > 0:
            covered += 1

    type_accuracy = sum(actual == guess for actual, guess in zip(expected, predicted)) / max(len(expected), 1)
    detection_true_positive = sum(
        actual != "none" and guess != "none" for actual, guess in zip(expected, predicted)
    )
    detection_false_positive = sum(
        actual == "none" and guess != "none" for actual, guess in zip(expected, predicted)
    )
    detection_false_negative = sum(
        actual != "none" and guess == "none" for actual, guess in zip(expected, predicted)
    )
    detection_precision = detection_true_positive / max(
        detection_true_positive + detection_false_positive,
        1,
    )
    detection_recall = detection_true_positive / max(
        detection_true_positive + detection_false_negative,
        1,
    )
    detection_f1 = 2 * detection_precision * detection_recall / max(
        detection_precision + detection_recall,
        1e-9,
    )
    contradiction_macro_f1 = sum(class_f1) / max(len(class_f1), 1)
    coverage_index = covered / max(len(CONTRADICTION_LABELS), 1)
    overall_score = round(
        100
        * (
            weights["contradiction_macro_f1"] * contradiction_macro_f1
            + weights["type_accuracy"] * type_accuracy
            + weights["binary_detection_f1"] * detection_f1
            + weights["coverage_index"] * coverage_index
        ),
        2,
    )
    return {
        "overall_score": overall_score,
        "type_accuracy": round(type_accuracy, 6),
        "contradiction_macro_f1": round(contradiction_macro_f1, 6),
        "detection_f1": round(detection_f1, 6),
        "coverage_index": round(coverage_index, 6),
    }


def _component_rows(
    hash_report: Mapping[str, Any],
    engine_report: Mapping[str, Any],
    weights: Mapping[str, float],
) -> list[dict[str, Any]]:
    hash_values = _report_metric_values(hash_report)
    engine_values = _report_metric_values(engine_report)
    rows = []
    for key, label in SCORE_COMPONENTS:
        weight = float(weights[key])
        hash_points = round(100 * weight * hash_values[key], 4)
        engine_points = round(100 * weight * engine_values[key], 4)
        rows.append(
            {
                "key": key,
                "label": label,
                "weight": weight,
                "engine_points": engine_points,
                "hash_points": hash_points,
                "gap_points": round(hash_points - engine_points, 4),
            }
        )
    return rows


def _report_metric_values(report: Mapping[str, Any]) -> dict[str, float]:
    metrics = report.get("metrics", {})
    return {
        "contradiction_macro_f1": float(metrics.get("contradiction_macro_f1", 0.0)),
        "type_accuracy": float(metrics.get("type_accuracy", 0.0)),
        "binary_detection_f1": float(metrics.get("detection", {}).get("f1", 0.0)),
        "coverage_index": float(metrics.get("coverage_index", 0.0)),
    }


def _distribution_summary(
    rows: Sequence[Mapping[str, float]],
    observed_score: float,
    engine_score: float,
) -> dict[str, float | int]:
    scores = sorted(float(item["overall_score"]) for item in rows)
    return {
        "samples": len(scores),
        "min": scores[0],
        "p05": _quantile(scores, 0.05),
        "median": round(median(scores), 4),
        "p95": _quantile(scores, 0.95),
        "max": scores[-1],
        "mean": round(mean(scores), 4),
        "share_below_observed": round(sum(score < observed_score for score in scores) / len(scores), 6),
        "share_at_or_above_observed": round(
            sum(score >= observed_score for score in scores) / len(scores),
            6,
        ),
        "share_above_engine": round(sum(score > engine_score for score in scores) / len(scores), 6),
    }


def _quantile(sorted_values: Sequence[float], probability: float) -> float:
    return float(sorted_values[round((len(sorted_values) - 1) * probability)])


def _ordered_counts(values: Sequence[str]) -> dict[str, int]:
    counts = Counter(values)
    return {label: int(counts.get(label, 0)) for label in HASH_PRIOR_LABELS}


def _percent(value: float) -> str:
    return f"{100 * float(value):.1f}%"


def _read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError(f"{path}: expected a JSON object")
    return data


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run baseline robustness diagnostics.")
    parser.add_argument(
        "--artifact",
        default=None,
        help="Optional output path for a reviewer-facing baseline robustness artifact.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    results, failures = run_baseline_robustness()

    if args.artifact:
        Path(args.artifact).parent.mkdir(parents=True, exist_ok=True)
        Path(args.artifact).write_text(build_baseline_robustness_artifact(results, failures), encoding="utf-8")

    for failure in failures:
        print(f"ERROR: {failure}")

    if failures:
        return 1
    print("Baseline robustness checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
