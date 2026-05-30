from __future__ import annotations

"""Validate leaderboard submission metadata against benchmark reports."""

import json
import time
from pathlib import Path
from typing import Any, Mapping

from marked_bench.benchmark_leaderboard import report_sha256
from marked_bench.contradiction.benchmark_suite import load_benchmark_report, validate_benchmark_report


SUBMISSION_SCHEMA = "marked_bench.leaderboard-submission.v1"
SUBMISSION_VALIDATION_SCHEMA = "marked_bench.leaderboard-submission-validation.v1"

DISCLOSURE_FIELDS = (
    "system_description",
    "model",
    "prompting",
    "preprocessing",
    "retrieval",
    "postprocessing",
    "training_data",
    "runtime",
)


def build_leaderboard_submission(
    report_path: str | Path,
    *,
    system_version: str,
    submitter: str,
    notes: str = "",
    disclosures: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a leaderboard submission file from a validated report."""

    path = Path(report_path)
    report = load_benchmark_report(path)
    validation = validate_benchmark_report(report)
    if not validation["valid"]:
        raise ValueError(f"report validation failed: {validation['errors']}")

    return {
        "schema": SUBMISSION_SCHEMA,
        "created_at": round(time.time(), 3),
        "system_name": report["system_name"],
        "system_version": str(system_version),
        "submitter": str(submitter),
        "suite_id": report["suite_id"],
        "suite_version": report["suite_version"],
        "suite_hash": report["suite_hash"],
        "report_schema": report["schema"],
        "report_path": path.as_posix(),
        "report_sha256": report_sha256(path),
        "overall_score": report["overall_score"],
        "case_count": report["case_count"],
        "failure_count": len(report["failures"]),
        "validation_warnings": validation["warnings"],
        "disclosures": _normalize_disclosures(disclosures),
        "notes": str(notes),
    }


def write_leaderboard_submission(submission: Mapping[str, Any], path: str | Path) -> None:
    """Write a leaderboard submission JSON file."""

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(submission, indent=2, sort_keys=True), encoding="utf-8")


def load_leaderboard_submission(path: str | Path) -> dict[str, Any]:
    """Load a leaderboard submission JSON file."""

    return json.loads(Path(path).read_text(encoding="utf-8"))


def validate_leaderboard_submission(
    submission: Mapping[str, Any],
    *,
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    """Validate submission metadata and the referenced benchmark report."""

    errors: list[str] = []
    warnings: list[str] = []
    _expect_equal(submission, "schema", SUBMISSION_SCHEMA, errors)
    _require_string(submission, "system_name", errors)
    _require_string(submission, "system_version", errors)
    _require_string(submission, "submitter", errors)
    _require_string(submission, "suite_id", errors)
    _require_string(submission, "suite_version", errors)
    _require_string(submission, "suite_hash", errors)
    _require_string(submission, "report_schema", errors)
    _require_string(submission, "report_path", errors)
    _require_string(submission, "report_sha256", errors)

    disclosures = submission.get("disclosures")
    if not isinstance(disclosures, Mapping):
        errors.append("disclosures must be an object")
    else:
        for field in DISCLOSURE_FIELDS:
            if not str(disclosures.get(field, "")).strip():
                errors.append(f"disclosures.{field} is required")

    report = None
    validation = None
    report_path = str(submission.get("report_path", ""))
    if report_path:
        resolved_report_path = _resolve_report_path(report_path, base_dir)
        if not resolved_report_path.exists():
            errors.append(f"report_path does not exist: {report_path}")
        else:
            try:
                report = load_benchmark_report(resolved_report_path)
            except (OSError, json.JSONDecodeError) as exc:
                errors.append(f"could not load report_path: {exc}")
            else:
                actual_sha = report_sha256(resolved_report_path)
                if submission.get("report_sha256") != actual_sha:
                    errors.append(f"report_sha256 mismatch: expected {actual_sha!r}, got {submission.get('report_sha256')!r}")
                validation = validate_benchmark_report(report)
                if not validation["valid"]:
                    errors.append(f"referenced report is invalid: {validation['errors']}")
                warnings.extend(validation["warnings"])

    if report is not None:
        _expect_equal(submission, "system_name", report.get("system_name"), errors)
        _expect_equal(submission, "suite_id", report.get("suite_id"), errors)
        _expect_equal(submission, "suite_version", report.get("suite_version"), errors)
        _expect_equal(submission, "suite_hash", report.get("suite_hash"), errors)
        _expect_equal(submission, "report_schema", report.get("schema"), errors)
        _expect_equal(submission, "overall_score", report.get("overall_score"), errors)
        _expect_equal(submission, "case_count", report.get("case_count"), errors)
        _expect_equal(submission, "failure_count", len(report.get("failures", [])), errors)

    return {
        "schema": SUBMISSION_VALIDATION_SCHEMA,
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
        "summary": {
            "system_name": submission.get("system_name"),
            "system_version": submission.get("system_version"),
            "submitter": submission.get("submitter"),
            "suite_id": submission.get("suite_id"),
            "suite_version": submission.get("suite_version"),
            "suite_hash": submission.get("suite_hash"),
            "overall_score": submission.get("overall_score"),
        },
    }


def _normalize_disclosures(disclosures: Mapping[str, Any] | None) -> dict[str, str]:
    provided = disclosures or {}
    return {field: str(provided.get(field) or "not disclosed") for field in DISCLOSURE_FIELDS}


def _resolve_report_path(report_path: str, base_dir: str | Path | None) -> Path:
    path = Path(report_path)
    if path.is_absolute():
        return path
    return Path(base_dir or Path.cwd()) / path


def _require_string(submission: Mapping[str, Any], key: str, errors: list[str]) -> None:
    if not str(submission.get(key, "")).strip():
        errors.append(f"{key} is required")


def _expect_equal(submission: Mapping[str, Any], key: str, expected: Any, errors: list[str]) -> None:
    actual = submission.get(key)
    if actual != expected:
        errors.append(f"{key} mismatch: expected {expected!r}, got {actual!r}")


__all__ = [
    "DISCLOSURE_FIELDS",
    "SUBMISSION_SCHEMA",
    "SUBMISSION_VALIDATION_SCHEMA",
    "build_leaderboard_submission",
    "load_leaderboard_submission",
    "validate_leaderboard_submission",
    "write_leaderboard_submission",
]
