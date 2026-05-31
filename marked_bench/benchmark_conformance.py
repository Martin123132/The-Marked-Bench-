from __future__ import annotations

"""Machine-readable conformance reports for benchmark release packages."""

import json
import os
from pathlib import Path
from typing import Any, Mapping

from marked_bench.benchmark_leaderboard import build_leaderboard
from marked_bench.benchmark_registry import build_benchmark_registry
from marked_bench.benchmark_release import build_release_manifest
from marked_bench.benchmark_result_card import load_result_card, validate_result_card
from marked_bench.benchmark_review import load_submission_review, validate_submission_review
from marked_bench.benchmark_submission import load_submission_bundle, validate_submission_bundle
from marked_bench.contradiction.benchmark_suite import (
    build_prediction_template,
    build_suite_manifest,
    evaluate_prediction_file,
    validate_benchmark_report,
)
from marked_bench.schema_validation import load_json_schema, validate_json_file, validate_json_schema


CONFORMANCE_REPORT_SCHEMA = "marked_bench.conformance-report.v1"
DEFAULT_CONFORMANCE_REPORT = Path("conformance/marked_bench_conformance_v0_3_8.json")
DEFAULT_RELEASE_MANIFEST = Path("releases/marked_bench_release_v0_3_8.json")

SUITE_MANIFESTS = {
    Path("suites/marked_bench_contradiction_standard_v0_1_0.json"): "contradiction",
    Path("suites/marked_bench_contradiction_adversarial_v0_2_0.json"): "contradiction-adversarial",
    Path("suites/marked_bench_contradiction_multihop_v0_3_0.json"): "contradiction-multihop",
}

BASELINE_REPORTS = [
    Path("baselines/contradiction_engine_v0_1_0.json"),
    Path("baselines/always_none_v0_1_0.json"),
    Path("baselines/contradiction_engine_adversarial_v0_2_0.json"),
    Path("baselines/always_none_adversarial_v0_2_0.json"),
    Path("baselines/contradiction_engine_multihop_v0_3_0.json"),
    Path("baselines/always_none_multihop_v0_3_0.json"),
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

CHECKED_RESULT_CARDS = [
    Path("submissions/example_external_jsonl/example_external_result_card.json"),
]

SCHEMA_CONFORMANCE_FILES = {
    Path("benchmark_registry.json"): Path("schemas/benchmark_registry.schema.json"),
    DEFAULT_RELEASE_MANIFEST: Path("schemas/release_manifest.schema.json"),
    DEFAULT_CONFORMANCE_REPORT: Path("schemas/conformance_report.schema.json"),
    Path("leaderboard/leaderboard_v0_1_0.json"): Path("schemas/leaderboard.schema.json"),
    Path("leaderboard/leaderboard_adversarial_v0_2_0.json"): Path("schemas/leaderboard.schema.json"),
    Path("leaderboard/leaderboard_multihop_v0_3_0.json"): Path("schemas/leaderboard.schema.json"),
    Path("submissions/example_external_jsonl/example_external_report.json"): Path(
        "schemas/contradiction_benchmark_report.schema.json"
    ),
    Path("submissions/example_external_jsonl/example_external_submission.json"): Path(
        "schemas/leaderboard_submission.schema.json"
    ),
    Path("submissions/example_external_jsonl/example_external_submission_bundle.json"): Path(
        "schemas/submission_bundle.schema.json"
    ),
    Path("submissions/example_external_jsonl/example_external_submission_review.json"): Path(
        "schemas/submission_review.schema.json"
    ),
    Path("submissions/example_external_jsonl/example_external_result_card.json"): Path(
        "schemas/result_card.schema.json"
    ),
}


def build_conformance_report(
    root: str | Path = ".",
    *,
    release_manifest_path: str | Path = DEFAULT_RELEASE_MANIFEST,
) -> dict[str, Any]:
    """Build a deterministic report proving release-package conformance."""

    root_path = Path(root)
    release_path = Path(release_manifest_path)
    registry = _read_json(root_path / "benchmark_registry.json")
    manifest = _read_json(root_path / release_path)
    checks = [
        _check_benchmark_registry(root_path),
        _check_release_manifest(root_path, release_path),
        _check_suite_manifests(root_path),
        _check_baseline_reports(root_path),
        _check_leaderboards(root_path),
        _check_schema_conformance(root_path),
        _check_prediction_templates(root_path),
        _check_submission_packets(root_path),
        _check_result_cards(root_path),
    ]
    failures = [f"{check['name']}: {error}" for check in checks for error in check["errors"]]
    track_count = len(registry.get("tracks", [])) if isinstance(registry, dict) else 0
    artifact_count = manifest.get("artifact_count", 0) if isinstance(manifest, dict) else 0
    release_id = manifest.get("release_id", "") if isinstance(manifest, dict) else ""

    return {
        "schema": CONFORMANCE_REPORT_SCHEMA,
        "project": "The Marked Bench",
        "benchmark_family": "contradiction-detection",
        "release_manifest_path": release_path.as_posix(),
        "release_id": release_id,
        "default_track": registry.get("default_track", "") if isinstance(registry, dict) else "",
        "track_count": track_count,
        "checked_artifact_count": artifact_count,
        "checked_schema_file_count": _schema_file_count(),
        "passed": not failures,
        "checks": checks,
        "failures": failures,
    }


def write_conformance_report(
    path: str | Path,
    root: str | Path = ".",
    *,
    release_manifest_path: str | Path = DEFAULT_RELEASE_MANIFEST,
) -> None:
    """Write a stable conformance report for the current benchmark release."""

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(
            build_conformance_report(root=root, release_manifest_path=release_manifest_path),
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )


def load_conformance_report(path: str | Path) -> dict[str, Any]:
    """Load a conformance report JSON file."""

    data = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError("conformance report must be a JSON object")
    return data


def validate_conformance_report(
    report: Mapping[str, Any],
    root: str | Path = ".",
) -> dict[str, Any]:
    """Validate a conformance report against the current release evidence."""

    root_path = Path(root)
    errors: list[str] = []
    warnings: list[str] = []

    schema_path = root_path / "schemas" / "conformance_report.schema.json"
    if schema_path.exists():
        schema = load_json_schema(schema_path)
        errors.extend(validate_json_schema(report, schema, schema_path=schema_path))
    else:
        errors.append(f"{schema_path}: conformance report schema is missing")

    release_manifest_path = Path(str(report.get("release_manifest_path", DEFAULT_RELEASE_MANIFEST)))
    expected = build_conformance_report(root_path, release_manifest_path=release_manifest_path)
    if dict(report) != expected:
        errors.append("conformance report does not match current benchmark release evidence")
    if report.get("passed") is not True:
        errors.append("conformance report did not pass all checks")

    passed_checks = [check for check in report.get("checks", []) if isinstance(check, Mapping) and check.get("status") == "pass"]
    summary = {
        "release_id": report.get("release_id", ""),
        "release_manifest_path": report.get("release_manifest_path", ""),
        "checks_passed": len(passed_checks),
        "checks_total": len(report.get("checks", [])) if isinstance(report.get("checks"), list) else 0,
        "checked_artifact_count": report.get("checked_artifact_count", 0),
    }
    return {
        "valid": not errors,
        "schema": report.get("schema", ""),
        "summary": summary,
        "errors": errors,
        "warnings": warnings,
    }


def _check_benchmark_registry(root: Path) -> dict[str, Any]:
    path = Path("benchmark_registry.json")
    actual = _read_json(root / path)
    errors: list[str] = []
    if actual is None:
        errors.append(f"{path}: missing or invalid JSON")
    elif actual != build_benchmark_registry():
        errors.append(f"{path}: registry does not match code-generated registry")
    return _check("benchmark_registry_current", errors, {"path": path.as_posix()})


def _check_release_manifest(root: Path, release_path: Path) -> dict[str, Any]:
    actual = _read_json(root / release_path)
    errors: list[str] = []
    artifact_count = 0
    if actual is None:
        errors.append(f"{release_path}: missing or invalid JSON")
    else:
        artifact_count = int(actual.get("artifact_count", 0))
        try:
            expected = build_release_manifest(root)
        except OSError as exc:
            errors.append(f"{release_path}: could not rebuild release manifest: {exc}")
        else:
            if actual != expected:
                errors.append(f"{release_path}: release manifest does not match current artifact hashes")
    return _check(
        "release_manifest_current",
        errors,
        {"path": release_path.as_posix(), "artifact_count": artifact_count},
    )


def _check_suite_manifests(root: Path) -> dict[str, Any]:
    errors: list[str] = []
    for path, suite in SUITE_MANIFESTS.items():
        actual = _read_json(root / path)
        if actual is None:
            errors.append(f"{path}: missing or invalid JSON")
            continue
        expected = build_suite_manifest(suite=suite)
        if actual != expected:
            errors.append(f"{path}: suite manifest does not match canonical builder")
    return _check("suite_manifests_current", errors, {"suite_count": len(SUITE_MANIFESTS)})


def _check_baseline_reports(root: Path) -> dict[str, Any]:
    errors: list[str] = []
    for path in BASELINE_REPORTS:
        report = _read_json(root / path)
        if report is None:
            errors.append(f"{path}: missing or invalid JSON")
            continue
        validation = validate_benchmark_report(report)
        if not validation["valid"]:
            errors.append(f"{path}: report validation failed: {validation['errors']}")
    return _check("baseline_reports_valid", errors, {"report_count": len(BASELINE_REPORTS)})


def _check_leaderboards(root: Path) -> dict[str, Any]:
    errors: list[str] = []
    for path, reports in LEADERBOARDS.items():
        actual = _read_json(root / path)
        if actual is None:
            errors.append(f"{path}: missing or invalid JSON")
            continue
        previous_cwd = Path.cwd()
        os.chdir(root)
        try:
            expected = build_leaderboard(reports)
        finally:
            os.chdir(previous_cwd)
        for key in ["schema", "entry_count", "rejected_count", "entries", "rejected"]:
            if actual.get(key) != expected.get(key):
                errors.append(f"{path}: {key} does not match validated reports")
    return _check("leaderboards_match_reports", errors, {"leaderboard_count": len(LEADERBOARDS)})


def _check_schema_conformance(root: Path) -> dict[str, Any]:
    errors: list[str] = []
    for path, schema_path in SCHEMA_CONFORMANCE_FILES.items():
        errors.extend(_schema_file_errors(root, path, schema_path))
    for path in SUITE_MANIFESTS:
        errors.extend(_schema_file_errors(root, path, Path("schemas/contradiction_suite_manifest.schema.json")))
    for path in BASELINE_REPORTS:
        errors.extend(_schema_file_errors(root, path, Path("schemas/contradiction_benchmark_report.schema.json")))
    return _check("public_json_schema_conformance", errors, {"file_count": _schema_file_count()})


def _check_prediction_templates(root: Path) -> dict[str, Any]:
    errors: list[str] = []
    schema_path = root / "schemas" / "contradiction_predictions.schema.json"
    try:
        schema = load_json_schema(schema_path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return _check("prediction_templates_conform", [f"{schema_path}: could not load schema: {exc}"], {})
    for suite in SUITE_MANIFESTS.values():
        schema_errors = validate_json_schema(build_prediction_template(suite=suite), schema, schema_path=schema_path)
        for error in schema_errors:
            errors.append(f"generated prediction template ({suite}): {error}")
    return _check("prediction_templates_conform", errors, {"suite_count": len(SUITE_MANIFESTS)})


def _check_submission_packets(root: Path) -> dict[str, Any]:
    errors: list[str] = []
    for packet in CHECKED_SUBMISSION_PACKETS:
        base_dir = Path(packet["base_dir"])
        bundle_path = base_dir / Path(packet["bundle"])
        predictions_path = base_dir / Path(packet["predictions"])
        report_path = base_dir / Path(packet["report"])
        review_path = base_dir / Path(packet["review"])

        report = _read_json(root / report_path)
        if report is None:
            errors.append(f"{report_path}: missing or invalid JSON")
        else:
            validation = validate_benchmark_report(report)
            if not validation["valid"]:
                errors.append(f"{report_path}: report validation failed: {validation['errors']}")

        try:
            scored_report = evaluate_prediction_file(
                root / predictions_path,
                system_name=str(packet["system_name"]),
                suite=str(packet["suite"]),
            )
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            errors.append(f"{predictions_path}: could not score predictions: {exc}")
        else:
            if report is not None:
                for key in ["suite_id", "suite_version", "suite_hash", "case_count", "overall_score"]:
                    if scored_report.get(key) != report.get(key):
                        errors.append(f"{report_path}: {key} does not match checked predictions")

        try:
            bundle = load_submission_bundle(root / bundle_path)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            errors.append(f"{bundle_path}: could not load bundle: {exc}")
        else:
            validation = validate_submission_bundle(bundle, base_dir=root / base_dir)
            if not validation["valid"]:
                errors.append(f"{bundle_path}: bundle validation failed: {validation['errors']}")

        try:
            review = load_submission_review(root / review_path)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            errors.append(f"{review_path}: could not load review: {exc}")
        else:
            validation = validate_submission_review(review, base_dir=root / base_dir)
            if not validation["valid"]:
                errors.append(f"{review_path}: review validation failed: {validation['errors']}")

    return _check("checked_submission_packets_valid", errors, {"packet_count": len(CHECKED_SUBMISSION_PACKETS)})


def _check_result_cards(root: Path) -> dict[str, Any]:
    errors: list[str] = []
    for path in CHECKED_RESULT_CARDS:
        try:
            card = load_result_card(root / path)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            errors.append(f"{path}: could not load result card: {exc}")
            continue
        validation = validate_result_card(card, base_dir=(root / path).parent)
        if not validation["valid"]:
            errors.append(f"{path}: result card validation failed: {validation['errors']}")
    return _check("checked_result_cards_valid", errors, {"card_count": len(CHECKED_RESULT_CARDS)})


def _schema_file_errors(root: Path, path: Path, schema_path: Path) -> list[str]:
    try:
        return [
            f"{path}: schema violation against {schema_path}: {error}"
            for error in validate_json_file(root / path, root / schema_path)
        ]
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        return [f"{path}: could not validate against {schema_path}: {exc}"]


def _read_json(path: Path) -> Any | None:
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        return None


def _check(name: str, errors: list[str], details: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "name": name,
        "status": "fail" if errors else "pass",
        "details": dict(details),
        "errors": errors,
    }


def _schema_file_count() -> int:
    return len(SCHEMA_CONFORMANCE_FILES) + len(SUITE_MANIFESTS) + len(BASELINE_REPORTS)


__all__ = [
    "CONFORMANCE_REPORT_SCHEMA",
    "DEFAULT_CONFORMANCE_REPORT",
    "DEFAULT_RELEASE_MANIFEST",
    "build_conformance_report",
    "load_conformance_report",
    "validate_conformance_report",
    "write_conformance_report",
]
