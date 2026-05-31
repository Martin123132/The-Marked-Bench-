from __future__ import annotations

"""Standard result cards for publishable benchmark results."""

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from marked_bench.benchmark_leaderboard import report_sha256
from marked_bench.benchmark_review import load_submission_review, validate_submission_review
from marked_bench.benchmark_submission import (
    load_leaderboard_submission,
    load_submission_bundle,
    validate_submission_bundle,
)
from marked_bench.contradiction.benchmark_suite import load_benchmark_report, validate_benchmark_report
from marked_bench.schema_validation import load_json_schema, validate_json_schema


RESULT_CARD_SCHEMA = "marked_bench.result-card.v1"
RESULT_CARD_VALIDATION_SCHEMA = "marked_bench.result-card-validation.v1"


def build_result_card(
    report_path: str | Path,
    *,
    bundle_path: str | Path | None = None,
    review_path: str | Path | None = None,
    base_dir: str | Path | None = None,
    notes: str = "",
) -> dict[str, Any]:
    """Build a portable, citeable result card from validated benchmark evidence."""

    root = Path(base_dir or Path.cwd()).resolve()
    resolved_report_path = _resolve_result_path(report_path, root)
    report = load_benchmark_report(resolved_report_path)
    report_validation = validate_benchmark_report(report)
    if not report_validation["valid"]:
        raise ValueError(f"report validation failed: {report_validation['errors']}")

    bundle = None
    bundle_validation = None
    submission = None
    resolved_bundle_path = None
    if bundle_path is not None:
        resolved_bundle_path = _resolve_result_path(bundle_path, root)
        bundle = load_submission_bundle(resolved_bundle_path)
        bundle_validation = validate_submission_bundle(bundle, base_dir=resolved_bundle_path.parent)
        if not bundle_validation["valid"]:
            raise ValueError(f"bundle validation failed: {bundle_validation['errors']}")
        submission = load_leaderboard_submission(resolved_bundle_path.parent / str(bundle["submission_path"]))

    review = None
    review_validation = None
    resolved_review_path = None
    if review_path is not None:
        resolved_review_path = _resolve_result_path(review_path, root)
        review = load_submission_review(resolved_review_path)
        review_validation = validate_submission_review(review, base_dir=resolved_review_path.parent)
        if not review_validation["valid"]:
            raise ValueError(f"review validation failed: {review_validation['errors']}")

    source_times = [
        value
        for value in [
            report.get("created_at"),
            bundle.get("created_at") if isinstance(bundle, Mapping) else None,
            review.get("created_at") if isinstance(review, Mapping) else None,
        ]
        if isinstance(value, (int, float)) and not isinstance(value, bool)
    ]
    created_at = round(max(source_times), 3) if source_times else None
    metrics = report["metrics"]
    publication = _publication_summary(bundle_validation, review, review_validation)

    return {
        "schema": RESULT_CARD_SCHEMA,
        "created_at": created_at,
        "system_name": report["system_name"],
        "system_version": _result_value(bundle, "system_version", "not disclosed"),
        "submitter": _result_value(bundle, "submitter", "not disclosed"),
        "suite_id": report["suite_id"],
        "suite_version": report["suite_version"],
        "suite_hash": report["suite_hash"],
        "report_schema": report["schema"],
        "report_path": _portable_relative_path(resolved_report_path, root),
        "report_sha256": report_sha256(resolved_report_path),
        "bundle_path": _portable_relative_path(resolved_bundle_path, root) if resolved_bundle_path else None,
        "bundle_sha256": _file_sha256(resolved_bundle_path) if resolved_bundle_path else None,
        "review_path": _portable_relative_path(resolved_review_path, root) if resolved_review_path else None,
        "review_sha256": _file_sha256(resolved_review_path) if resolved_review_path else None,
        "case_count": report["case_count"],
        "failure_count": len(report["failures"]),
        "overall_score": report["overall_score"],
        "metrics": {
            "type_accuracy": metrics["type_accuracy"],
            "contradiction_macro_f1": metrics["contradiction_macro_f1"],
            "detection_f1": metrics["detection"]["f1"],
            "calibration_brier_score": metrics["calibration"]["brier_score"],
            "calibration_ece": metrics["calibration"]["expected_calibration_error"],
            "coverage_index": metrics["coverage_index"],
            "explanation_ready_rate": report.get("explanation_audit", {}).get("explanation_ready_rate", 0.0),
        },
        "publication": publication,
        "disclosures": submission.get("disclosures", {}) if isinstance(submission, Mapping) else {},
        "standard_claims": {
            "same_suite_hash_required": True,
            "public_test_result": True,
            "not_safety_certification": True,
            "report_validator_required": True,
            "bundle_required_for_leaderboard_review": True,
        },
        "notes": str(notes),
    }


def write_result_card(card: Mapping[str, Any], path: str | Path) -> None:
    """Write a result card JSON file."""

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(card, indent=2, sort_keys=True), encoding="utf-8")


def load_result_card(path: str | Path) -> dict[str, Any]:
    """Load a result card JSON file."""

    data = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError("result card must be a JSON object")
    return data


def validate_result_card(
    card: Mapping[str, Any],
    *,
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    """Validate a result card against its referenced benchmark evidence."""

    root = Path(base_dir or Path.cwd()).resolve()
    errors: list[str] = []
    warnings: list[str] = []

    schema_path = _find_schema_path(root)
    if schema_path is not None:
        schema = load_json_schema(schema_path)
        errors.extend(validate_json_schema(card, schema, schema_path=schema_path))
    else:
        warnings.append("schemas/result_card.schema.json was not found; skipped schema validation")

    if card.get("schema") != RESULT_CARD_SCHEMA:
        errors.append(f"schema must be {RESULT_CARD_SCHEMA!r}")

    report_path = str(card.get("report_path", ""))
    bundle_path = card.get("bundle_path")
    review_path = card.get("review_path")
    for key, value in [
        ("report_path", report_path),
        ("bundle_path", bundle_path),
        ("review_path", review_path),
    ]:
        if value and not _is_safe_relative_path(str(value)):
            errors.append(f"{key} must be a safe relative path")

    if report_path and not errors:
        try:
            expected = build_result_card(
                report_path,
                bundle_path=str(bundle_path) if bundle_path else None,
                review_path=str(review_path) if review_path else None,
                base_dir=root,
                notes=str(card.get("notes", "")),
            )
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            errors.append(f"could not rebuild result card: {exc}")
        else:
            if dict(card) != expected:
                errors.append("result card does not match referenced benchmark evidence")

    publication = card.get("publication")
    ready = isinstance(publication, Mapping) and publication.get("ready_for_leaderboard_review") is True
    return {
        "schema": RESULT_CARD_VALIDATION_SCHEMA,
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
        "summary": {
            "system_name": card.get("system_name"),
            "system_version": card.get("system_version"),
            "submitter": card.get("submitter"),
            "suite_id": card.get("suite_id"),
            "suite_version": card.get("suite_version"),
            "overall_score": card.get("overall_score"),
            "ready_for_leaderboard_review": ready,
            "review_decision": publication.get("review_decision") if isinstance(publication, Mapping) else None,
            "review_recommendation": publication.get("review_recommendation") if isinstance(publication, Mapping) else None,
        },
    }


def _publication_summary(
    bundle_validation: Mapping[str, Any] | None,
    review: Mapping[str, Any] | None,
    review_validation: Mapping[str, Any] | None,
) -> dict[str, Any]:
    ready_for_leaderboard_review = (
        bool(bundle_validation["valid"]) if isinstance(bundle_validation, Mapping) else False
    )
    review_valid = bool(review_validation["valid"]) if isinstance(review_validation, Mapping) else False
    review_summary = review_validation.get("summary", {}) if isinstance(review_validation, Mapping) else {}
    review_decision = str(review.get("decision", "not_reviewed")) if isinstance(review, Mapping) else "not_reviewed"
    review_recommendation = str(review_summary.get("recommendation", "not_reviewed"))
    return {
        "report_valid": True,
        "bundle_valid": ready_for_leaderboard_review,
        "review_valid": review_valid,
        "ready_for_leaderboard_review": ready_for_leaderboard_review,
        "review_decision": review_decision,
        "review_recommendation": review_recommendation,
        "ready_for_decision": bool(review_summary.get("ready_for_decision", False)),
        "accepted": review_valid and review_decision == "accept" and review_recommendation == "accept",
    }


def _result_value(source: Mapping[str, Any] | None, key: str, default: str) -> str:
    if isinstance(source, Mapping):
        value = str(source.get(key, "")).strip()
        if value:
            return value
    return default


def _file_sha256(path: str | Path) -> str:
    digest = hashlib.sha256()
    digest.update(_canonical_file_bytes(path))
    return digest.hexdigest()


def _canonical_file_bytes(path: str | Path) -> bytes:
    data = Path(path).read_bytes()
    if b"\0" in data:
        return data
    return data.replace(b"\r\n", b"\n")


def _resolve_result_path(path: str | Path, base_dir: Path) -> Path:
    raw_path = Path(path)
    if raw_path.is_absolute():
        return raw_path.resolve()
    return (base_dir / raw_path).resolve()


def _portable_relative_path(path: Path, base_dir: Path) -> str:
    try:
        return path.resolve().relative_to(base_dir.resolve()).as_posix()
    except ValueError as exc:
        raise ValueError(f"path is outside result-card base directory: {path}") from exc


def _is_safe_relative_path(path: str) -> bool:
    normalized = Path(path)
    return not normalized.is_absolute() and ".." not in normalized.parts


def _find_schema_path(root: Path) -> Path | None:
    for base in [root, *root.parents]:
        candidate = base / "schemas" / "result_card.schema.json"
        if candidate.exists():
            return candidate
    return None


__all__ = [
    "RESULT_CARD_SCHEMA",
    "RESULT_CARD_VALIDATION_SCHEMA",
    "build_result_card",
    "load_result_card",
    "validate_result_card",
    "write_result_card",
]
