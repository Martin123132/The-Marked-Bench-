from __future__ import annotations

"""Command line runner for The Marked Bench standards."""

import argparse
import json
from pathlib import Path

from marked_bench.benchmark_leaderboard import build_leaderboard, write_leaderboard
from marked_bench.benchmark_release import write_release_manifest
from marked_bench.benchmark_registry import write_benchmark_registry
from marked_bench.benchmark_submission import (
    DISCLOSURE_FIELDS,
    build_leaderboard_submission,
    load_leaderboard_submission,
    validate_leaderboard_submission,
    write_leaderboard_submission,
)
from marked_bench.benchmark_technical_note import write_technical_note
from marked_bench.contradiction.benchmark_suite import (
    evaluate_prediction_file,
    evaluate_standard_suite,
    load_benchmark_report,
    validate_benchmark_report,
    write_benchmark_report,
    write_prediction_template,
    write_suite_manifest,
)
from marked_bench.contradiction.engine import Claim


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run The Marked Bench benchmark suites.")
    parser.add_argument(
        "--suite",
        default="contradiction",
        choices=["contradiction", "contradiction-adversarial"],
        help="Benchmark suite to run.",
    )
    parser.add_argument(
        "--system-name",
        default="ContradictionEngine",
        help="Name to store in the benchmark report.",
    )
    parser.add_argument(
        "--detector",
        default="contradiction-engine",
        choices=["contradiction-engine", "always-none"],
        help="Built-in detector to benchmark.",
    )
    parser.add_argument(
        "--report",
        default=None,
        help="Optional path to write the full JSON report.",
    )
    parser.add_argument(
        "--score-predictions",
        default=None,
        metavar="PATH",
        help="Score an external JSON or JSONL predictions file instead of a built-in detector.",
    )
    parser.add_argument(
        "--validate-report",
        default=None,
        help="Validate an existing JSON report instead of running a benchmark.",
    )
    parser.add_argument(
        "--create-submission",
        default=None,
        metavar="PATH",
        help="Write leaderboard submission metadata for a validated report and exit.",
    )
    parser.add_argument(
        "--validate-submission",
        default=None,
        metavar="PATH",
        help="Validate leaderboard submission metadata and its referenced report.",
    )
    parser.add_argument(
        "--submission-report",
        default=None,
        metavar="PATH",
        help="Report path referenced when creating a leaderboard submission.",
    )
    parser.add_argument(
        "--system-version",
        default=None,
        help="System version to store in submission metadata.",
    )
    parser.add_argument(
        "--submitter",
        default=None,
        help="Submitter name or organization to store in submission metadata.",
    )
    parser.add_argument(
        "--submission-notes",
        default="",
        help="Notes to store in submission metadata.",
    )
    parser.add_argument(
        "--disclosure",
        action="append",
        default=[],
        metavar="KEY=VALUE",
        help="Submission disclosure field. Supported keys: " + ", ".join(DISCLOSURE_FIELDS),
    )
    parser.add_argument(
        "--export-suite",
        default=None,
        help="Write the canonical suite manifest JSON and exit.",
    )
    parser.add_argument(
        "--export-registry",
        default=None,
        metavar="PATH",
        help="Write the machine-readable benchmark registry JSON and exit.",
    )
    parser.add_argument(
        "--export-release-manifest",
        default=None,
        metavar="PATH",
        help="Write a SHA-256 manifest for public benchmark release artifacts and exit.",
    )
    parser.add_argument(
        "--export-technical-note",
        default=None,
        metavar="PATH",
        help="Write the generated benchmark technical note and exit.",
    )
    parser.add_argument(
        "--export-prediction-template",
        default=None,
        metavar="PATH",
        help="Write a fillable prediction template for the selected suite and exit.",
    )
    parser.add_argument(
        "--build-leaderboard",
        nargs="+",
        default=None,
        metavar="REPORT",
        help="Build a leaderboard from one or more benchmark reports.",
    )
    parser.add_argument(
        "--leaderboard-output",
        default=None,
        help="Optional path to write the leaderboard JSON.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print the full JSON report instead of a compact summary.",
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.validate_report:
        validation = validate_benchmark_report(load_benchmark_report(args.validate_report))
        if args.json:
            print(json.dumps(validation, indent=2, sort_keys=True))
        else:
            print(f"Validation: {'pass' if validation['valid'] else 'fail'}")
            print(f"Suite: {validation['suite_id']} v{validation['suite_version']}")
            print(f"System: {validation['summary']['system_name']}")
            print(f"Overall score: {validation['summary']['overall_score']}")
            print(f"Errors: {len(validation['errors'])}")
            print(f"Warnings: {len(validation['warnings'])}")
        if not validation["valid"]:
            raise SystemExit(1)
        return

    if args.validate_submission:
        validation = validate_leaderboard_submission(load_leaderboard_submission(args.validate_submission))
        if args.json:
            print(json.dumps(validation, indent=2, sort_keys=True))
        else:
            print(f"Submission validation: {'pass' if validation['valid'] else 'fail'}")
            print(f"Suite: {validation['summary']['suite_id']} v{validation['summary']['suite_version']}")
            print(f"System: {validation['summary']['system_name']} {validation['summary']['system_version']}")
            print(f"Overall score: {validation['summary']['overall_score']}")
            print(f"Errors: {len(validation['errors'])}")
            print(f"Warnings: {len(validation['warnings'])}")
        if not validation["valid"]:
            raise SystemExit(1)
        return

    if args.create_submission:
        if not args.submission_report:
            parser.error("--create-submission requires --submission-report")
        if not args.system_version:
            parser.error("--create-submission requires --system-version")
        if not args.submitter:
            parser.error("--create-submission requires --submitter")
        try:
            disclosures = _parse_disclosures(args.disclosure)
            submission = build_leaderboard_submission(
                args.submission_report,
                system_version=args.system_version,
                submitter=args.submitter,
                notes=args.submission_notes,
                disclosures=disclosures,
            )
        except (OSError, ValueError) as exc:
            parser.error(str(exc))
        write_leaderboard_submission(submission, args.create_submission)
        print(f"Submission: {args.create_submission}")
        print(f"Report SHA-256: {submission['report_sha256']}")
        return

    if args.export_suite:
        write_suite_manifest(args.export_suite, suite=args.suite)
        print(f"Suite manifest: {args.export_suite}")
        return

    if args.export_registry:
        write_benchmark_registry(args.export_registry)
        print(f"Benchmark registry: {args.export_registry}")
        return

    if args.export_release_manifest:
        write_release_manifest(args.export_release_manifest)
        print(f"Release manifest: {args.export_release_manifest}")
        return

    if args.export_technical_note:
        write_technical_note(args.export_technical_note)
        print(f"Technical note: {args.export_technical_note}")
        return

    if args.export_prediction_template:
        write_prediction_template(args.export_prediction_template, suite=args.suite)
        print(f"Prediction template: {args.export_prediction_template}")
        return

    if args.build_leaderboard:
        leaderboard = build_leaderboard(args.build_leaderboard)
        if args.leaderboard_output:
            write_leaderboard(leaderboard, args.leaderboard_output)
        if args.json:
            print(json.dumps(leaderboard, indent=2, sort_keys=True))
        else:
            print(f"Leaderboard entries: {leaderboard['entry_count']}")
            print(f"Rejected reports: {leaderboard['rejected_count']}")
            for entry in leaderboard["entries"]:
                print(
                    f"#{entry['rank']} {entry['system_name']}: "
                    f"{entry['overall_score']:.2f} "
                    f"(failures={entry['failure_count']})"
                )
            if args.leaderboard_output:
                print(f"Leaderboard: {args.leaderboard_output}")
        if leaderboard["rejected_count"]:
            raise SystemExit(1)
        return

    if args.score_predictions:
        try:
            report = evaluate_prediction_file(args.score_predictions, system_name=args.system_name, suite=args.suite)
        except (OSError, ValueError) as exc:
            parser.error(str(exc))
    else:
        detector = _detector_from_name(args.detector)
        report = evaluate_standard_suite(detector=detector, system_name=args.system_name, suite=args.suite)
    if args.report:
        write_benchmark_report(report, Path(args.report))

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
        return

    print(f"Suite: {report['suite_id']} v{report['suite_version']}")
    print(f"System: {report['system_name']}")
    print(f"Cases: {report['case_count']}")
    print(f"Overall score: {report['overall_score']:.2f}")
    print(f"Type accuracy: {report['metrics']['type_accuracy']:.2f}")
    print(f"Detection F1: {report['metrics']['detection']['f1']:.2f}")
    print(f"Calibration Brier: {report['metrics']['calibration']['brier_score']:.4f}")
    print(f"Failures: {len(report['failures'])}")
    if args.report:
        print(f"Report: {args.report}")


def _detector_from_name(name: str):
    if name == "always-none":
        return _always_none_detector
    return None


def _always_none_detector(_claim: Claim):
    return None


def _parse_disclosures(items: list[str]) -> dict[str, str]:
    disclosures = {}
    valid_fields = set(DISCLOSURE_FIELDS)
    for item in items:
        if "=" not in item:
            raise ValueError(f"--disclosure must use KEY=VALUE, got {item!r}")
        key, value = item.split("=", 1)
        key = key.strip()
        if key not in valid_fields:
            raise ValueError(f"Unknown disclosure key {key!r}; supported keys: {', '.join(DISCLOSURE_FIELDS)}")
        disclosures[key] = value.strip()
    return disclosures


if __name__ == "__main__":
    main()
