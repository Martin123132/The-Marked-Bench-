from __future__ import annotations

"""Command line runner for The Marked Bench standards."""

import argparse
import json
from pathlib import Path

from marked_bench.benchmark_adoption import (
    load_adoption_packet,
    validate_adoption_packet,
    write_adoption_packet,
)
from marked_bench.benchmark_claim import (
    build_result_claim,
    load_result_claim,
    validate_result_claim,
    write_result_claim,
)
from marked_bench.benchmark_conformance import (
    load_conformance_report,
    validate_conformance_report,
    write_conformance_report,
)
from marked_bench.benchmark_evidence import (
    load_evidence_ledger,
    validate_evidence_ledger,
    write_evidence_ledger,
)
from marked_bench.benchmark_leaderboard import build_leaderboard, write_leaderboard
from marked_bench.benchmark_publication import (
    PACKET_FILENAME,
    create_publication_packet,
    load_publication_packet,
    validate_publication_packet,
)
from marked_bench.benchmark_release import write_release_manifest
from marked_bench.benchmark_registry import write_benchmark_registry
from marked_bench.benchmark_review import (
    REVIEW_DECISIONS,
    build_submission_review,
    load_submission_review,
    validate_submission_review,
    write_submission_review,
)
from marked_bench.benchmark_result_card import (
    build_result_card,
    load_result_card,
    validate_result_card,
    write_result_card,
)
from marked_bench.benchmark_submission import (
    DISCLOSURE_FIELDS,
    build_leaderboard_submission,
    build_submission_bundle,
    load_leaderboard_submission,
    load_submission_bundle,
    validate_submission_bundle,
    validate_leaderboard_submission,
    write_leaderboard_submission,
    write_submission_bundle,
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
        choices=[
            "contradiction",
            "contradiction-adversarial",
            "contradiction-multihop",
            "contradiction-controls",
        ],
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
        "--create-submission-bundle",
        default=None,
        metavar="PATH",
        help="Write a portable review bundle manifest for a leaderboard submission and exit.",
    )
    parser.add_argument(
        "--validate-submission-bundle",
        default=None,
        metavar="PATH",
        help="Validate a leaderboard submission bundle manifest and its referenced files.",
    )
    parser.add_argument(
        "--create-submission-review",
        default=None,
        metavar="PATH",
        help="Write a structured reviewer rubric for a submission bundle and exit.",
    )
    parser.add_argument(
        "--validate-submission-review",
        default=None,
        metavar="PATH",
        help="Validate a structured submission review rubric and its referenced bundle.",
    )
    parser.add_argument(
        "--create-result-card",
        default=None,
        metavar="PATH",
        help="Write a standard result card for a benchmark report and exit.",
    )
    parser.add_argument(
        "--validate-result-card",
        default=None,
        metavar="PATH",
        help="Validate a standard result card and its referenced benchmark evidence.",
    )
    parser.add_argument(
        "--create-publication-packet",
        default=None,
        metavar="DIR",
        help="Write a complete public result packet directory and exit.",
    )
    parser.add_argument(
        "--validate-publication-packet",
        default=None,
        metavar="PATH",
        help="Validate a public result packet manifest and its referenced files.",
    )
    parser.add_argument(
        "--create-result-claim",
        default=None,
        metavar="PATH",
        help="Write a citeable result claim from a validated publication packet and exit.",
    )
    parser.add_argument(
        "--validate-result-claim",
        default=None,
        metavar="PATH",
        help="Validate a citeable result claim against its publication packet.",
    )
    parser.add_argument(
        "--export-conformance-report",
        default=None,
        metavar="PATH",
        help="Write a machine-readable benchmark release conformance report and exit.",
    )
    parser.add_argument(
        "--validate-conformance-report",
        default=None,
        metavar="PATH",
        help="Validate a conformance report against the current release evidence.",
    )
    parser.add_argument(
        "--conformance-release-manifest",
        default=None,
        metavar="PATH",
        help="Release manifest path to use when exporting a conformance report.",
    )
    parser.add_argument(
        "--export-adoption-packet",
        default=None,
        metavar="PATH",
        help="Write a machine-readable external adoption packet and exit.",
    )
    parser.add_argument(
        "--validate-adoption-packet",
        default=None,
        metavar="PATH",
        help="Validate an external adoption packet against the current release evidence.",
    )
    parser.add_argument(
        "--export-evidence-ledger",
        default=None,
        metavar="PATH",
        help="Write a third-party adoption evidence ledger and exit.",
    )
    parser.add_argument(
        "--validate-evidence-ledger",
        default=None,
        metavar="PATH",
        help="Validate a third-party adoption evidence ledger.",
    )
    parser.add_argument(
        "--bundle-submission",
        default=None,
        metavar="PATH",
        help="Submission metadata path referenced when creating a submission bundle.",
    )
    parser.add_argument(
        "--bundle-predictions",
        default=None,
        metavar="PATH",
        help="Optional prediction file path to include in a submission bundle.",
    )
    parser.add_argument(
        "--review-bundle",
        default=None,
        metavar="PATH",
        help="Submission bundle path referenced when creating a submission review.",
    )
    parser.add_argument(
        "--reviewer",
        default="unassigned",
        help="Reviewer name or handle to store in a submission review.",
    )
    parser.add_argument(
        "--review-decision",
        default="needs_review",
        choices=REVIEW_DECISIONS,
        help="Review decision to store in a submission review.",
    )
    parser.add_argument(
        "--review-notes",
        default="",
        help="Notes to store in a submission review.",
    )
    parser.add_argument(
        "--result-report",
        default=None,
        metavar="PATH",
        help="Report path referenced when creating a result card.",
    )
    parser.add_argument(
        "--result-bundle",
        default=None,
        metavar="PATH",
        help="Optional submission bundle path referenced when creating a result card.",
    )
    parser.add_argument(
        "--result-review",
        default=None,
        metavar="PATH",
        help="Optional submission review path referenced when creating a result card.",
    )
    parser.add_argument(
        "--result-notes",
        default="",
        help="Notes to store in a result card.",
    )
    parser.add_argument(
        "--publication-report",
        default=None,
        metavar="PATH",
        help="Report path to copy into a public result packet.",
    )
    parser.add_argument(
        "--publication-predictions",
        default=None,
        metavar="PATH",
        help="Optional prediction file to copy into a public result packet.",
    )
    parser.add_argument(
        "--publication-notes",
        default="",
        help="Notes to store in a public result packet manifest.",
    )
    parser.add_argument(
        "--claim-publication-packet",
        default=None,
        metavar="PATH",
        help="Publication packet path referenced when creating a result claim.",
    )
    parser.add_argument(
        "--claim-url",
        default="",
        help="Optional public URL where the result claim will be published.",
    )
    parser.add_argument(
        "--claim-evidence-url",
        default="",
        help="Optional public URL where the full evidence packet will be published.",
    )
    parser.add_argument(
        "--claim-notes",
        default="",
        help="Notes to store in a result claim.",
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

    if args.validate_submission_bundle:
        bundle_path = Path(args.validate_submission_bundle)
        validation = validate_submission_bundle(
            load_submission_bundle(bundle_path),
            base_dir=bundle_path.parent,
        )
        if args.json:
            print(json.dumps(validation, indent=2, sort_keys=True))
        else:
            print(f"Submission bundle validation: {'pass' if validation['valid'] else 'fail'}")
            print(f"Suite: {validation['summary']['suite_id']} v{validation['summary']['suite_version']}")
            print(f"System: {validation['summary']['system_name']} {validation['summary']['system_version']}")
            print(f"Overall score: {validation['summary']['overall_score']}")
            print(f"Ready for leaderboard review: {validation['summary']['ready_for_leaderboard_review']}")
            print(f"Errors: {len(validation['errors'])}")
            print(f"Warnings: {len(validation['warnings'])}")
        if not validation["valid"]:
            raise SystemExit(1)
        return

    if args.validate_submission_review:
        review_path = Path(args.validate_submission_review)
        validation = validate_submission_review(
            load_submission_review(review_path),
            base_dir=review_path.parent,
        )
        if args.json:
            print(json.dumps(validation, indent=2, sort_keys=True))
        else:
            print(f"Submission review validation: {'pass' if validation['valid'] else 'fail'}")
            print(f"Suite: {validation['summary']['suite_id']} v{validation['summary']['suite_version']}")
            print(f"System: {validation['summary']['system_name']} {validation['summary']['system_version']}")
            print(f"Overall score: {validation['summary']['overall_score']}")
            print(f"Decision: {validation['summary']['decision']}")
            print(f"Ready for decision: {validation['summary']['ready_for_decision']}")
            print(f"Recommendation: {validation['summary']['recommendation']}")
            print(f"Errors: {len(validation['errors'])}")
            print(f"Warnings: {len(validation['warnings'])}")
        if not validation["valid"]:
            raise SystemExit(1)
        return

    if args.validate_conformance_report:
        validation = validate_conformance_report(load_conformance_report(args.validate_conformance_report))
        if args.json:
            print(json.dumps(validation, indent=2, sort_keys=True))
        else:
            print(f"Conformance validation: {'pass' if validation['valid'] else 'fail'}")
            print(f"Release: {validation['summary']['release_id']}")
            print(f"Manifest: {validation['summary']['release_manifest_path']}")
            print(
                "Checks: "
                f"{validation['summary']['checks_passed']}/{validation['summary']['checks_total']}"
            )
            print(f"Artifacts: {validation['summary']['checked_artifact_count']}")
            print(f"Errors: {len(validation['errors'])}")
            print(f"Warnings: {len(validation['warnings'])}")
        if not validation["valid"]:
            raise SystemExit(1)
        return

    if args.validate_result_card:
        card_path = Path(args.validate_result_card)
        validation = validate_result_card(load_result_card(card_path), base_dir=card_path.parent)
        if args.json:
            print(json.dumps(validation, indent=2, sort_keys=True))
        else:
            print(f"Result card validation: {'pass' if validation['valid'] else 'fail'}")
            print(f"Suite: {validation['summary']['suite_id']} v{validation['summary']['suite_version']}")
            print(f"System: {validation['summary']['system_name']} {validation['summary']['system_version']}")
            print(f"Overall score: {validation['summary']['overall_score']}")
            print(f"Ready for leaderboard review: {validation['summary']['ready_for_leaderboard_review']}")
            print(f"Review decision: {validation['summary']['review_decision']}")
            print(f"Errors: {len(validation['errors'])}")
            print(f"Warnings: {len(validation['warnings'])}")
        if not validation["valid"]:
            raise SystemExit(1)
        return

    if args.validate_publication_packet:
        packet_path = Path(args.validate_publication_packet)
        validation = validate_publication_packet(
            load_publication_packet(packet_path),
            base_dir=packet_path.parent,
        )
        if args.json:
            print(json.dumps(validation, indent=2, sort_keys=True))
        else:
            print(f"Publication packet validation: {'pass' if validation['valid'] else 'fail'}")
            print(f"Suite: {validation['summary']['suite_id']} v{validation['summary']['suite_version']}")
            print(f"System: {validation['summary']['system_name']} {validation['summary']['system_version']}")
            print(f"Overall score: {validation['summary']['overall_score']}")
            print(f"Ready for publication: {validation['summary']['ready_for_publication']}")
            print(f"Files: {validation['summary']['file_count']}")
            print(f"Errors: {len(validation['errors'])}")
            print(f"Warnings: {len(validation['warnings'])}")
        if not validation["valid"]:
            raise SystemExit(1)
        return

    if args.validate_result_claim:
        claim_path = Path(args.validate_result_claim)
        validation = validate_result_claim(load_result_claim(claim_path), base_dir=claim_path.parent)
        if args.json:
            print(json.dumps(validation, indent=2, sort_keys=True))
        else:
            print(f"Result claim validation: {'pass' if validation['valid'] else 'fail'}")
            print(f"Suite: {validation['summary']['suite_id']} v{validation['summary']['suite_version']}")
            print(f"System: {validation['summary']['system_name']} {validation['summary']['system_version']}")
            print(f"Overall score: {validation['summary']['overall_score']}")
            print(f"Ready for citation: {validation['summary']['ready_for_citation']}")
            print(f"Errors: {len(validation['errors'])}")
            print(f"Warnings: {len(validation['warnings'])}")
        if not validation["valid"]:
            raise SystemExit(1)
        return

    if args.validate_adoption_packet:
        validation = validate_adoption_packet(load_adoption_packet(args.validate_adoption_packet))
        if args.json:
            print(json.dumps(validation, indent=2, sort_keys=True))
        else:
            print(f"Adoption packet validation: {'pass' if validation['valid'] else 'fail'}")
            print(f"Release: {validation['summary']['release_id']}")
            print(f"Default track: {validation['summary']['default_track']}")
            print(f"Tracks: {validation['summary']['track_count']}")
            print(f"Required artifacts: {validation['summary']['required_artifact_count']}")
            print(f"Errors: {len(validation['errors'])}")
            print(f"Warnings: {len(validation['warnings'])}")
        if not validation["valid"]:
            raise SystemExit(1)
        return

    if args.validate_evidence_ledger:
        validation = validate_evidence_ledger(load_evidence_ledger(args.validate_evidence_ledger))
        if args.json:
            print(json.dumps(validation, indent=2, sort_keys=True))
        else:
            print(f"Evidence ledger validation: {'pass' if validation['valid'] else 'fail'}")
            print(f"Release: {validation['summary']['release_id']}")
            print(f"Status: {validation['summary']['status']}")
            print(f"Entries: {validation['summary']['entry_count']}")
            print(f"Verified entries: {validation['summary']['verified_entry_count']}")
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

    if args.create_submission_bundle:
        if not args.bundle_submission:
            parser.error("--create-submission-bundle requires --bundle-submission")
        try:
            bundle_submission_path = Path(args.bundle_submission)
            bundle = build_submission_bundle(
                bundle_submission_path.name,
                prediction_path=args.bundle_predictions,
                base_dir=bundle_submission_path.parent,
            )
        except (OSError, ValueError) as exc:
            parser.error(str(exc))
        write_submission_bundle(bundle, args.create_submission_bundle)
        print(f"Submission bundle: {args.create_submission_bundle}")
        print(f"Report SHA-256: {bundle['report_sha256']}")
        return

    if args.create_submission_review:
        if not args.review_bundle:
            parser.error("--create-submission-review requires --review-bundle")
        try:
            review_bundle_path = Path(args.review_bundle)
            review = build_submission_review(
                review_bundle_path.name,
                reviewer=args.reviewer,
                decision=args.review_decision,
                notes=args.review_notes,
                base_dir=review_bundle_path.parent,
            )
        except (OSError, ValueError) as exc:
            parser.error(str(exc))
        write_submission_review(review, args.create_submission_review)
        print(f"Submission review: {args.create_submission_review}")
        print(f"Bundle SHA-256: {review['bundle_sha256']}")
        print(f"Recommendation: {review['summary']['recommendation']}")
        return

    if args.create_result_card:
        if not args.result_report:
            parser.error("--create-result-card requires --result-report")
        result_card_path = Path(args.create_result_card)
        try:
            card = build_result_card(
                args.result_report,
                bundle_path=args.result_bundle,
                review_path=args.result_review,
                base_dir=result_card_path.parent,
                notes=args.result_notes,
            )
        except (OSError, ValueError) as exc:
            parser.error(str(exc))
        write_result_card(card, result_card_path)
        print(f"Result card: {args.create_result_card}")
        print(f"Overall score: {card['overall_score']}")
        print(f"Ready for leaderboard review: {card['publication']['ready_for_leaderboard_review']}")
        return

    if args.create_publication_packet:
        if not args.publication_report:
            parser.error("--create-publication-packet requires --publication-report")
        if not args.system_version:
            parser.error("--create-publication-packet requires --system-version")
        if not args.submitter:
            parser.error("--create-publication-packet requires --submitter")
        try:
            packet = create_publication_packet(
                args.create_publication_packet,
                args.publication_report,
                prediction_path=args.publication_predictions,
                system_version=args.system_version,
                submitter=args.submitter,
                reviewer=args.reviewer,
                review_decision=args.review_decision,
                submission_notes=args.submission_notes,
                review_notes=args.review_notes,
                result_notes=args.result_notes,
                packet_notes=args.publication_notes,
                disclosures=_parse_disclosures(args.disclosure),
            )
        except (OSError, ValueError) as exc:
            parser.error(str(exc))
        packet_path = Path(args.create_publication_packet) / PACKET_FILENAME
        print(f"Publication packet: {packet_path}")
        print(f"Overall score: {packet['overall_score']}")
        print(f"Ready for publication: {packet['ready_for_publication']}")
        print(f"Files: {len(packet['files'])}")
        return

    if args.create_result_claim:
        if not args.claim_publication_packet:
            parser.error("--create-result-claim requires --claim-publication-packet")
        claim_path = Path(args.create_result_claim)
        try:
            claim = build_result_claim(
                args.claim_publication_packet,
                base_dir=claim_path.parent,
                claim_url=args.claim_url,
                evidence_url=args.claim_evidence_url,
                notes=args.claim_notes,
            )
        except (OSError, ValueError) as exc:
            parser.error(str(exc))
        write_result_claim(claim, claim_path)
        print(f"Result claim: {claim_path}")
        print(f"Claim: {claim['claim']['text']}")
        print(f"Ready for citation: {claim['validation']['valid']}")
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

    if args.export_conformance_report:
        kwargs = {}
        if args.conformance_release_manifest:
            kwargs["release_manifest_path"] = args.conformance_release_manifest
        write_conformance_report(args.export_conformance_report, **kwargs)
        print(f"Conformance report: {args.export_conformance_report}")
        return

    if args.export_adoption_packet:
        write_adoption_packet(args.export_adoption_packet)
        print(f"Adoption packet: {args.export_adoption_packet}")
        return

    if args.export_evidence_ledger:
        write_evidence_ledger(args.export_evidence_ledger)
        print(f"Evidence ledger: {args.export_evidence_ledger}")
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
