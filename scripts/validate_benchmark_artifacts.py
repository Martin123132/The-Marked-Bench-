from __future__ import annotations

"""Validate checked-in benchmark manifests, reports, and leaderboards."""

import json
import os
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from marked_bench.benchmark_adoption import load_adoption_packet, validate_adoption_packet  # noqa: E402
from marked_bench.benchmark_claim import load_result_claim, validate_result_claim  # noqa: E402
from marked_bench.benchmark_conformance import load_conformance_report, validate_conformance_report  # noqa: E402
from marked_bench.benchmark_evidence import load_evidence_ledger, validate_evidence_ledger  # noqa: E402
from marked_bench.benchmark_implementation import load_implementation_kit, validate_implementation_kit  # noqa: E402
from marked_bench.benchmark_leaderboard import build_leaderboard  # noqa: E402
from marked_bench.benchmark_publication import load_publication_packet, validate_publication_packet  # noqa: E402
from marked_bench.benchmark_release import build_release_manifest  # noqa: E402
from marked_bench.benchmark_registry import build_benchmark_registry  # noqa: E402
from marked_bench.benchmark_result_card import load_result_card, validate_result_card  # noqa: E402
from marked_bench.benchmark_review import load_submission_review, validate_submission_review  # noqa: E402
from marked_bench.benchmark_submission import load_submission_bundle, validate_submission_bundle  # noqa: E402
from marked_bench.benchmark_technical_note import build_technical_note  # noqa: E402
from marked_bench.schema_validation import validate_json_file, validate_json_schema  # noqa: E402
from marked_bench.contradiction.benchmark_suite import (  # noqa: E402
    build_prediction_template,
    build_suite_manifest,
    evaluate_prediction_file,
    validate_benchmark_report,
)


SUITE_MANIFESTS = {
    Path("suites/marked_bench_contradiction_standard_v0_1_0.json"): "contradiction",
    Path("suites/marked_bench_contradiction_adversarial_v0_2_0.json"): "contradiction-adversarial",
    Path("suites/marked_bench_contradiction_multihop_v0_3_0.json"): "contradiction-multihop",
    Path("suites/marked_bench_contradiction_controls_v0_4_0.json"): "contradiction-controls",
}

BASELINE_REPORTS = [
    Path("baselines/contradiction_engine_v0_1_0.json"),
    Path("baselines/always_none_v0_1_0.json"),
    Path("baselines/contradiction_engine_adversarial_v0_2_0.json"),
    Path("baselines/always_none_adversarial_v0_2_0.json"),
    Path("baselines/contradiction_engine_multihop_v0_3_0.json"),
    Path("baselines/always_none_multihop_v0_3_0.json"),
    Path("baselines/contradiction_engine_controls_v0_4_0.json"),
    Path("baselines/always_none_controls_v0_4_0.json"),
]

LEADERBOARDS = {
    Path("leaderboard/leaderboard_v0_1_0.json"): [
        Path("baselines/always_none_v0_1_0.json"),
        Path("baselines/contradiction_engine_v0_1_0.json"),
    ],
    Path("leaderboard/leaderboard_adversarial_v0_2_0.json"): [
        Path("baselines/always_none_adversarial_v0_2_0.json"),
        Path("baselines/contradiction_engine_adversarial_v0_2_0.json"),
    ],
    Path("leaderboard/leaderboard_multihop_v0_3_0.json"): [
        Path("baselines/always_none_multihop_v0_3_0.json"),
        Path("baselines/contradiction_engine_multihop_v0_3_0.json"),
    ],
    Path("leaderboard/leaderboard_controls_v0_4_0.json"): [
        Path("baselines/always_none_controls_v0_4_0.json"),
        Path("baselines/contradiction_engine_controls_v0_4_0.json"),
    ],
}

CHECKED_SUBMISSION_PACKETS = [
    {
        "base_dir": Path("submissions/example_external_jsonl"),
        "bundle": Path("example_external_submission_bundle.json"),
        "predictions": Path("predictions.jsonl"),
        "report": Path("example_external_report.json"),
        "review": Path("example_external_submission_review.json"),
        "suite": "contradiction-multihop",
        "system_name": "ExampleExternalJsonl",
    },
]

BENCHMARK_REGISTRY = Path("benchmark_registry.json")
RELEASE_MANIFEST = Path("releases/marked_bench_release_v0_4_3.json")
CONFORMANCE_REPORT = Path("conformance/marked_bench_conformance_v0_4_3.json")
ADOPTION_PACKET = Path("adoption/marked_bench_adoption_packet_v0_4_3.json")
EVIDENCE_LEDGER = Path("adoption/third_party_evidence_ledger_v0_4_3.json")
IMPLEMENTATION_KIT = Path("adoption/marked_bench_implementation_kit_v0_4_3.json")

REQUIRED_PUBLIC_FILES = [
    Path("adoption/README.md"),
    ADOPTION_PACKET,
    EVIDENCE_LEDGER,
    IMPLEMENTATION_KIT,
    Path("adoption/implementation_kit/README.md"),
    Path("adoption/implementation_kit/github_actions_validate_result.yml"),
    Path("adoption/implementation_kit/result_claim_badge.md"),
    Path("README.md"),
    BENCHMARK_REGISTRY,
    RELEASE_MANIFEST,
    CONFORMANCE_REPORT,
    Path("CONTRIBUTING.md"),
    Path("CITATION.cff"),
    Path("docs/BENCHMARK_CARD.md"),
    Path("docs/ADOPTION_GUIDE.md"),
    Path("docs/ANNOUNCEMENT_PACKAGE.md"),
    Path("docs/BENCHMARK_STANDARD.md"),
    Path("docs/GOVERNANCE.md"),
    Path("docs/SUBMISSION_REVIEW_RUBRIC.md"),
    Path("docs/RELEASE_CHECKLIST.md"),
    Path("docs/RELEASE_NOTES_v0_2_0.md"),
    Path("docs/RELEASE_NOTES_v0_3_0.md"),
    Path("docs/RELEASE_NOTES_v0_3_1.md"),
    Path("docs/RELEASE_NOTES_v0_3_2.md"),
    Path("docs/RELEASE_NOTES_v0_3_3.md"),
    Path("docs/RELEASE_NOTES_v0_3_4.md"),
    Path("docs/RELEASE_NOTES_v0_3_5.md"),
    Path("docs/RELEASE_NOTES_v0_3_6.md"),
    Path("docs/RELEASE_NOTES_v0_3_7.md"),
    Path("docs/RELEASE_NOTES_v0_3_8.md"),
    Path("docs/RELEASE_NOTES_v0_3_9.md"),
    Path("docs/RELEASE_NOTES_v0_3_10.md"),
    Path("docs/RELEASE_NOTES_v0_4_0.md"),
    Path("docs/RELEASE_NOTES_v0_4_1.md"),
    Path("docs/RELEASE_NOTES_v0_4_2.md"),
    Path("docs/RELEASE_NOTES_v0_4_3.md"),
    Path("docs/ROADMAP.md"),
    Path("docs/SUBMISSION_GUIDE.md"),
    Path("docs/THIRD_PARTY_EVIDENCE.md"),
    Path("schemas/benchmark_registry.schema.json"),
    Path("schemas/contradiction_benchmark_report.schema.json"),
    Path("schemas/contradiction_predictions.schema.json"),
    Path("schemas/contradiction_suite_manifest.schema.json"),
    Path("schemas/leaderboard.schema.json"),
    Path("schemas/leaderboard_submission.schema.json"),
    Path("schemas/submission_bundle.schema.json"),
    Path("schemas/submission_review.schema.json"),
    Path("schemas/publication_packet.schema.json"),
    Path("schemas/result_claim.schema.json"),
    Path("schemas/implementation_kit.schema.json"),
    Path("schemas/release_manifest.schema.json"),
    Path("schemas/conformance_report.schema.json"),
    Path("schemas/result_card.schema.json"),
    Path("schemas/adoption_packet.schema.json"),
    Path("schemas/third_party_evidence_ledger.schema.json"),
    Path("conformance/README.md"),
    Path("releases/README.md"),
    Path("submissions/README.md"),
    Path("submissions/example_external_jsonl/predictions.jsonl"),
    Path("submissions/example_external_jsonl/example_external_report.json"),
    Path("submissions/example_external_jsonl/example_external_submission.json"),
    Path("submissions/example_external_jsonl/example_external_submission_bundle.json"),
    Path("submissions/example_external_jsonl/example_external_submission_review.json"),
    Path("submissions/example_external_jsonl/example_external_result_card.json"),
    Path("submissions/example_publication_packet/predictions.jsonl"),
    Path("submissions/example_publication_packet/report.json"),
    Path("submissions/example_publication_packet/submission.json"),
    Path("submissions/example_publication_packet/submission_bundle.json"),
    Path("submissions/example_publication_packet/submission_review.json"),
    Path("submissions/example_publication_packet/result_card.json"),
    Path("submissions/example_publication_packet/publication_packet.json"),
    Path("submissions/example_publication_packet/result_claim.json"),
    Path(".github/PULL_REQUEST_TEMPLATE.md"),
    Path(".github/workflows/benchmark-ci.yml"),
    Path(".github/ISSUE_TEMPLATE/third_party_evidence.yml"),
]

SCHEMA_CONFORMANCE_FILES = {
    BENCHMARK_REGISTRY: Path("schemas/benchmark_registry.schema.json"),
    RELEASE_MANIFEST: Path("schemas/release_manifest.schema.json"),
    CONFORMANCE_REPORT: Path("schemas/conformance_report.schema.json"),
    Path("leaderboard/leaderboard_v0_1_0.json"): Path("schemas/leaderboard.schema.json"),
    Path("leaderboard/leaderboard_adversarial_v0_2_0.json"): Path("schemas/leaderboard.schema.json"),
    Path("leaderboard/leaderboard_multihop_v0_3_0.json"): Path("schemas/leaderboard.schema.json"),
    Path("leaderboard/leaderboard_controls_v0_4_0.json"): Path("schemas/leaderboard.schema.json"),
    Path("submissions/example_external_jsonl/example_external_report.json"): Path(
        "schemas/contradiction_benchmark_report.schema.json"
    ),
    Path("submissions/example_external_jsonl/example_external_submission.json"): Path("schemas/leaderboard_submission.schema.json"),
    Path("submissions/example_external_jsonl/example_external_submission_bundle.json"): Path("schemas/submission_bundle.schema.json"),
    Path("submissions/example_external_jsonl/example_external_submission_review.json"): Path("schemas/submission_review.schema.json"),
    Path("submissions/example_external_jsonl/example_external_result_card.json"): Path("schemas/result_card.schema.json"),
    Path("submissions/example_publication_packet/publication_packet.json"): Path("schemas/publication_packet.schema.json"),
    Path("submissions/example_publication_packet/result_claim.json"): Path("schemas/result_claim.schema.json"),
    ADOPTION_PACKET: Path("schemas/adoption_packet.schema.json"),
    EVIDENCE_LEDGER: Path("schemas/third_party_evidence_ledger.schema.json"),
    IMPLEMENTATION_KIT: Path("schemas/implementation_kit.schema.json"),
}


def main() -> int:
    previous_cwd = Path.cwd()
    os.chdir(ROOT)
    try:
        errors: list[str] = []
        _validate_required_public_files(errors)
        _validate_benchmark_registry(errors)
        _validate_technical_note(errors)
        _validate_release_manifest(errors)
        _validate_conformance_report(errors)
        _validate_adoption_packet(errors)
        _validate_evidence_ledger(errors)
        _validate_implementation_kit(errors)
        _validate_suite_manifests(errors)
        _validate_baseline_reports(errors)
        _validate_leaderboards(errors)
        _validate_checked_submission_packets(errors)
        _validate_checked_result_cards(errors)
        _validate_checked_publication_packets(errors)
        _validate_checked_result_claims(errors)
        _validate_schema_conformance(errors)
    finally:
        os.chdir(previous_cwd)

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("Benchmark artifacts validated.")
    return 0


def _validate_suite_manifests(errors: list[str]) -> None:
    for path, suite in SUITE_MANIFESTS.items():
        actual = _read_json(path, errors)
        if actual is None:
            continue
        expected = build_suite_manifest(suite=suite)
        if actual != expected:
            errors.append(f"{path}: manifest does not match code-generated suite")


def _validate_schema_conformance(errors: list[str]) -> None:
    for path, schema_path in SCHEMA_CONFORMANCE_FILES.items():
        _validate_json_file_against_schema(path, schema_path, errors)

    for path in SUITE_MANIFESTS:
        _validate_json_file_against_schema(path, Path("schemas/contradiction_suite_manifest.schema.json"), errors)
    for path in BASELINE_REPORTS:
        _validate_json_file_against_schema(path, Path("schemas/contradiction_benchmark_report.schema.json"), errors)

    prediction_schema = _read_json(Path("schemas/contradiction_predictions.schema.json"), errors)
    if prediction_schema is not None:
        for suite in SUITE_MANIFESTS.values():
            schema_errors = validate_json_schema(
                build_prediction_template(suite=suite),
                prediction_schema,
                schema_path=ROOT / "schemas" / "contradiction_predictions.schema.json",
            )
            for error in schema_errors:
                errors.append(f"generated prediction template ({suite}): {error}")


def _validate_json_file_against_schema(path: Path, schema_path: Path, errors: list[str]) -> None:
    schema_errors = validate_json_file(path, schema_path)
    for error in schema_errors:
        errors.append(f"{path}: schema violation against {schema_path}: {error}")


def _validate_required_public_files(errors: list[str]) -> None:
    for path in REQUIRED_PUBLIC_FILES:
        if not path.exists():
            errors.append(f"{path}: required public repo file is missing")


def _validate_benchmark_registry(errors: list[str]) -> None:
    registry = _read_json(BENCHMARK_REGISTRY, errors)
    if registry is None:
        return
    expected = build_benchmark_registry()
    if registry != expected:
        errors.append(f"{BENCHMARK_REGISTRY}: registry does not match code-generated registry")

    for path in registry.get("schemas", {}).values():
        _expect_existing_path(Path(path), errors, BENCHMARK_REGISTRY)
    for path in registry.get("governance_docs", []):
        _expect_existing_path(Path(path), errors, BENCHMARK_REGISTRY)

    tracks = registry.get("tracks", [])
    if not isinstance(tracks, list):
        errors.append(f"{BENCHMARK_REGISTRY}: tracks must be a list")
        return
    for track in tracks:
        if not isinstance(track, dict):
            errors.append(f"{BENCHMARK_REGISTRY}: track entries must be objects")
            continue
        _validate_registry_track(track, errors)


def _validate_registry_track(track: dict[str, Any], errors: list[str]) -> None:
    track_name = track.get("name", "<unknown>")
    manifest_path = Path(str(track.get("suite_manifest", "")))
    leaderboard_path = Path(str(track.get("leaderboard", "")))
    _expect_existing_path(manifest_path, errors, BENCHMARK_REGISTRY)
    _expect_existing_path(leaderboard_path, errors, BENCHMARK_REGISTRY)
    for report_path in track.get("baseline_reports", []):
        _expect_existing_path(Path(str(report_path)), errors, BENCHMARK_REGISTRY)

    manifest = _read_json(manifest_path, errors)
    if manifest is not None:
        for key in ["suite_id", "suite_version", "suite_hash", "case_count", "labels", "profile"]:
            if track.get(key) != manifest.get(key):
                errors.append(f"{BENCHMARK_REGISTRY}: {track_name} {key} does not match suite manifest")

    for report_path in track.get("baseline_reports", []):
        report = _read_json(Path(str(report_path)), errors)
        if report is None:
            continue
        validation = validate_benchmark_report(report)
        if not validation["valid"]:
            errors.append(f"{BENCHMARK_REGISTRY}: {report_path} is not a valid baseline report")
        if (
            report.get("suite_id") != track.get("suite_id")
            or report.get("suite_version") != track.get("suite_version")
            or report.get("suite_hash") != track.get("suite_hash")
        ):
            errors.append(f"{BENCHMARK_REGISTRY}: {report_path} suite metadata does not match {track_name}")

    leaderboard = _read_json(leaderboard_path, errors)
    if leaderboard is not None:
        for entry in leaderboard.get("entries", []):
            if (
                entry.get("suite_id") != track.get("suite_id")
                or entry.get("suite_version") != track.get("suite_version")
                or entry.get("suite_hash") != track.get("suite_hash")
            ):
                errors.append(f"{BENCHMARK_REGISTRY}: leaderboard entry suite metadata does not match {track_name}")


def _validate_technical_note(errors: list[str]) -> None:
    path = Path("docs/TECHNICAL_NOTE.md")
    try:
        actual = path.read_text(encoding="utf-8")
    except OSError as exc:
        errors.append(f"{path}: could not read file: {exc}")
        return
    expected = build_technical_note(ROOT)
    if actual != expected:
        errors.append(f"{path}: technical note does not match generated benchmark evidence")


def _validate_release_manifest(errors: list[str]) -> None:
    manifest = _read_json(RELEASE_MANIFEST, errors)
    if manifest is None:
        return
    try:
        expected = build_release_manifest(ROOT)
    except OSError as exc:
        errors.append(f"{RELEASE_MANIFEST}: could not build expected release manifest: {exc}")
        return
    if manifest != expected:
        errors.append(f"{RELEASE_MANIFEST}: release manifest does not match current public artifacts")


def _validate_conformance_report(errors: list[str]) -> None:
    try:
        report = load_conformance_report(CONFORMANCE_REPORT)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        errors.append(f"{CONFORMANCE_REPORT}: could not load conformance report: {exc}")
        return
    validation = validate_conformance_report(report, root=ROOT)
    if not validation["valid"]:
        errors.append(f"{CONFORMANCE_REPORT}: conformance validation failed: {validation['errors']}")


def _validate_adoption_packet(errors: list[str]) -> None:
    try:
        packet = load_adoption_packet(ADOPTION_PACKET)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        errors.append(f"{ADOPTION_PACKET}: could not load adoption packet: {exc}")
        return
    validation = validate_adoption_packet(packet, root=ROOT)
    if not validation["valid"]:
        errors.append(f"{ADOPTION_PACKET}: adoption packet validation failed: {validation['errors']}")


def _validate_evidence_ledger(errors: list[str]) -> None:
    try:
        ledger = load_evidence_ledger(EVIDENCE_LEDGER)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        errors.append(f"{EVIDENCE_LEDGER}: could not load evidence ledger: {exc}")
        return
    validation = validate_evidence_ledger(ledger, root=ROOT)
    if not validation["valid"]:
        errors.append(f"{EVIDENCE_LEDGER}: evidence ledger validation failed: {validation['errors']}")


def _validate_implementation_kit(errors: list[str]) -> None:
    try:
        kit = load_implementation_kit(IMPLEMENTATION_KIT)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        errors.append(f"{IMPLEMENTATION_KIT}: could not load implementation kit: {exc}")
        return
    validation = validate_implementation_kit(kit, root=ROOT)
    if not validation["valid"]:
        errors.append(f"{IMPLEMENTATION_KIT}: implementation kit validation failed: {validation['errors']}")


def _validate_baseline_reports(errors: list[str]) -> None:
    for path in BASELINE_REPORTS:
        report = _read_json(path, errors)
        if report is None:
            continue
        validation = validate_benchmark_report(report)
        if not validation["valid"]:
            errors.append(f"{path}: report validation failed: {validation['errors']}")


def _validate_checked_submission_packets(errors: list[str]) -> None:
    for packet in CHECKED_SUBMISSION_PACKETS:
        base_dir = packet["base_dir"]
        bundle_path = base_dir / packet["bundle"]
        predictions_path = base_dir / packet["predictions"]
        report_path = base_dir / packet["report"]
        review_path = base_dir / packet["review"]
        if not bundle_path.exists():
            errors.append(f"{bundle_path}: checked submission bundle is missing")
            continue
        if not predictions_path.exists():
            errors.append(f"{predictions_path}: checked submission predictions are missing")
            continue
        if not report_path.exists():
            errors.append(f"{report_path}: checked submission report is missing")
            continue
        if not review_path.exists():
            errors.append(f"{review_path}: checked submission review is missing")
            continue

        report = _read_json(report_path, errors)
        if report is not None:
            validation = validate_benchmark_report(report)
            if not validation["valid"]:
                errors.append(f"{report_path}: checked submission report validation failed: {validation['errors']}")

        try:
            scored_report = evaluate_prediction_file(
                predictions_path,
                system_name=str(packet["system_name"]),
                suite=str(packet["suite"]),
            )
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            errors.append(f"{predictions_path}: could not score checked submission predictions: {exc}")
        else:
            if report is not None:
                for key in ["suite_id", "suite_version", "suite_hash", "case_count", "overall_score"]:
                    if scored_report.get(key) != report.get(key):
                        errors.append(f"{report_path}: {key} does not match checked submission predictions")

        try:
            bundle = load_submission_bundle(bundle_path)
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{bundle_path}: could not load checked submission bundle: {exc}")
        else:
            validation = validate_submission_bundle(bundle, base_dir=base_dir)
            if not validation["valid"]:
                errors.append(f"{bundle_path}: checked submission bundle validation failed: {validation['errors']}")

        try:
            review = load_submission_review(review_path)
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{review_path}: could not load checked submission review: {exc}")
        else:
            validation = validate_submission_review(review, base_dir=base_dir)
            if not validation["valid"]:
                errors.append(f"{review_path}: checked submission review validation failed: {validation['errors']}")


def _validate_checked_result_cards(errors: list[str]) -> None:
    paths = [Path("submissions/example_external_jsonl/example_external_result_card.json")]
    for path in paths:
        try:
            card = load_result_card(path)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            errors.append(f"{path}: could not load checked result card: {exc}")
            continue
        validation = validate_result_card(card, base_dir=path.parent)
        if not validation["valid"]:
            errors.append(f"{path}: checked result card validation failed: {validation['errors']}")


def _validate_checked_publication_packets(errors: list[str]) -> None:
    paths = [Path("submissions/example_publication_packet/publication_packet.json")]
    for path in paths:
        try:
            packet = load_publication_packet(path)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            errors.append(f"{path}: could not load checked publication packet: {exc}")
            continue
        validation = validate_publication_packet(packet, base_dir=path.parent)
        if not validation["valid"]:
            errors.append(f"{path}: checked publication packet validation failed: {validation['errors']}")


def _validate_checked_result_claims(errors: list[str]) -> None:
    paths = [Path("submissions/example_publication_packet/result_claim.json")]
    for path in paths:
        try:
            claim = load_result_claim(path)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            errors.append(f"{path}: could not load checked result claim: {exc}")
            continue
        validation = validate_result_claim(claim, base_dir=path.parent)
        if not validation["valid"]:
            errors.append(f"{path}: checked result claim validation failed: {validation['errors']}")


def _validate_leaderboards(errors: list[str]) -> None:
    for path, reports in LEADERBOARDS.items():
        actual = _read_json(path, errors)
        if actual is None:
            continue
        expected = build_leaderboard(reports)
        for key in ["schema", "entry_count", "rejected_count", "entries", "rejected"]:
            if actual.get(key) != expected.get(key):
                errors.append(f"{path}: {key} does not match validated reports")


def _read_json(path: Path, errors: list[str]) -> Any | None:
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except OSError as exc:
        errors.append(f"{path}: could not read file: {exc}")
    except json.JSONDecodeError as exc:
        errors.append(f"{path}: invalid JSON: {exc}")
    return None


def _expect_existing_path(path: Path, errors: list[str], source: Path) -> None:
    if not path.exists():
        errors.append(f"{source}: referenced path is missing: {path}")


if __name__ == "__main__":
    raise SystemExit(main())
