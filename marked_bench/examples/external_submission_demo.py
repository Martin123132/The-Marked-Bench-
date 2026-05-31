"""Create a complete external JSONL submission bundle.

This demo behaves like an outside system that does not import the detector. It
fills a prediction JSONL file, scores it into a report, creates submission
metadata, builds a review bundle, and validates that bundle.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from marked_bench.benchmark_submission import (
    build_leaderboard_submission,
    build_submission_bundle,
    validate_submission_bundle,
    write_leaderboard_submission,
    write_submission_bundle,
)
from marked_bench.contradiction.benchmark_suite import (
    build_prediction_template,
    evaluate_prediction_file,
    write_benchmark_report,
)


DEFAULT_SUITE = "contradiction-multihop"
DEFAULT_OUTPUT_DIR = Path("artifacts") / "external_submission_demo"


def run_demo(output_dir: str | Path = DEFAULT_OUTPUT_DIR, suite: str = DEFAULT_SUITE) -> dict[str, Any]:
    """Write a complete external-submission example and return its summary."""

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    prediction_path = output_path / "predictions.jsonl"
    report_path = output_path / "example_external_report.json"
    submission_path = output_path / "example_external_submission.json"
    bundle_path = output_path / "example_external_submission_bundle.json"

    _write_demo_predictions(prediction_path, suite=suite)
    report = evaluate_prediction_file(
        prediction_path,
        system_name="ExampleExternalJsonl",
        suite=suite,
    )
    write_benchmark_report(report, report_path)

    submission = build_leaderboard_submission(
        report_path.name,
        system_version="demo-1.0",
        submitter="The Marked Bench Examples",
        notes="Demonstrates the external JSONL submission workflow.",
        base_dir=output_path,
        disclosures={
            "system_description": "Example JSONL submitter that predicts none for every case.",
            "model": "none",
            "prompting": "none",
            "preprocessing": "none",
            "retrieval": "none",
            "postprocessing": "none",
            "training_data": "none",
            "runtime": "Python example script",
        },
    )
    write_leaderboard_submission(submission, submission_path)

    bundle = build_submission_bundle(
        submission_path.name,
        prediction_path=prediction_path.name,
        base_dir=output_path,
        notes="Demo bundle for reviewer workflow validation.",
    )
    write_submission_bundle(bundle, bundle_path)
    validation = validate_submission_bundle(bundle, base_dir=output_path)
    if not validation["valid"]:
        raise RuntimeError(f"demo bundle failed validation: {validation['errors']}")

    return {
        "suite_id": report["suite_id"],
        "suite_version": report["suite_version"],
        "system_name": report["system_name"],
        "overall_score": report["overall_score"],
        "prediction_path": prediction_path.as_posix(),
        "report_path": report_path.as_posix(),
        "submission_path": submission_path.as_posix(),
        "bundle_path": bundle_path.as_posix(),
        "bundle_valid": validation["valid"],
    }


def _write_demo_predictions(path: Path, *, suite: str) -> None:
    template = build_prediction_template(suite=suite)
    records = []
    for record in template["predictions"]:
        records.append(
            {
                "case_id": record["case_id"],
                "predicted": "none",
                "detector_score": 0.0,
                "detector_note": "Demo external system predicts no contradiction.",
                "rationale": "Demo external system predicts no contradiction for every case.",
                "evidence": [record["premise"], record["query"]],
            }
        )
    path.write_text(
        "\n".join(json.dumps(record, sort_keys=True) for record in records) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    summary = run_demo()
    print(f"Suite: {summary['suite_id']} v{summary['suite_version']}")
    print(f"System: {summary['system_name']}")
    print(f"Overall score: {summary['overall_score']:.2f}")
    print(f"Predictions: {summary['prediction_path']}")
    print(f"Report: {summary['report_path']}")
    print(f"Submission: {summary['submission_path']}")
    print(f"Bundle: {summary['bundle_path']}")
    print(f"Bundle valid: {summary['bundle_valid']}")


if __name__ == "__main__":
    main()
