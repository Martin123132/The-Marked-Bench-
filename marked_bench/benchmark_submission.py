from __future__ import annotations

"""Validate leaderboard submission metadata against benchmark reports."""

import hashlib
import json
import time
from pathlib import Path
from typing import Any, Mapping

from marked_bench.benchmark_leaderboard import report_sha256
from marked_bench.contradiction.benchmark_suite import load_benchmark_report, validate_benchmark_report


SUBMISSION_SCHEMA = "marked_bench.leaderboard-submission.v1"
SUBMISSION_VALIDATION_SCHEMA = "marked_bench.leaderboard-submission-validation.v1"
SUBMISSION_BUNDLE_SCHEMA = "marked_bench.leaderboard-submission-bundle.v1"
SUBMISSION_BUNDLE_VALIDATION_SCHEMA = "marked_bench.leaderboard-submission-bundle-validation.v1"

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
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    """Build a leaderboard submission file from a validated report."""

    path = _resolve_report_path(str(report_path), base_dir)
    stored_report_path = (
        _portable_relative_path(path.resolve(), Path(base_dir).resolve())
        if base_dir is not None
        else Path(report_path).as_posix()
    )
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
        "report_path": stored_report_path,
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


def build_submission_bundle(
    submission_path: str | Path,
    *,
    prediction_path: str | Path | None = None,
    base_dir: str | Path | None = None,
    notes: str = "",
) -> dict[str, Any]:
    """Build a portable review bundle manifest for a leaderboard submission."""

    root = Path(base_dir or Path.cwd()).resolve()
    resolved_submission_path = _resolve_bundle_path(submission_path, root)
    submission = load_leaderboard_submission(resolved_submission_path)
    validation = validate_leaderboard_submission(submission, base_dir=root)
    if not validation["valid"]:
        raise ValueError(f"submission validation failed: {validation['errors']}")

    report_path = str(submission["report_path"])
    resolved_report_path = _resolve_bundle_path(report_path, root)
    files = [
        _bundle_file_entry("submission", resolved_submission_path, root),
        _bundle_file_entry("report", resolved_report_path, root),
    ]
    if prediction_path is not None:
        files.append(_bundle_file_entry("predictions", _resolve_bundle_path(prediction_path, root), root))

    return {
        "schema": SUBMISSION_BUNDLE_SCHEMA,
        "created_at": round(time.time(), 3),
        "submission_path": _portable_relative_path(resolved_submission_path, root),
        "report_path": _portable_relative_path(resolved_report_path, root),
        "prediction_path": (
            _portable_relative_path(_resolve_bundle_path(prediction_path, root), root)
            if prediction_path is not None
            else None
        ),
        "system_name": submission["system_name"],
        "system_version": submission["system_version"],
        "submitter": submission["submitter"],
        "suite_id": submission["suite_id"],
        "suite_version": submission["suite_version"],
        "suite_hash": submission["suite_hash"],
        "report_sha256": submission["report_sha256"],
        "overall_score": submission["overall_score"],
        "files": files,
        "review_checklist": {
            "report_valid": True,
            "submission_valid": True,
            "disclosures_complete": _disclosures_complete(submission.get("disclosures")),
            "paths_are_relative": True,
            "file_hashes_current": True,
            "ready_for_leaderboard_review": True,
        },
        "notes": str(notes),
    }


def write_submission_bundle(bundle: Mapping[str, Any], path: str | Path) -> None:
    """Write a submission bundle manifest JSON file."""

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(bundle, indent=2, sort_keys=True), encoding="utf-8")


def load_submission_bundle(path: str | Path) -> dict[str, Any]:
    """Load a submission bundle manifest JSON file."""

    return json.loads(Path(path).read_text(encoding="utf-8"))


def validate_submission_bundle(
    bundle: Mapping[str, Any],
    *,
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    """Validate a portable leaderboard submission review bundle."""

    root = Path(base_dir or Path.cwd()).resolve()
    errors: list[str] = []
    warnings: list[str] = []
    _expect_equal(bundle, "schema", SUBMISSION_BUNDLE_SCHEMA, errors)
    _require_string(bundle, "submission_path", errors)
    _require_string(bundle, "report_path", errors)
    _require_string(bundle, "system_name", errors)
    _require_string(bundle, "system_version", errors)
    _require_string(bundle, "submitter", errors)
    _require_string(bundle, "suite_id", errors)
    _require_string(bundle, "suite_version", errors)
    _require_string(bundle, "suite_hash", errors)
    _require_string(bundle, "report_sha256", errors)

    submission_path = str(bundle.get("submission_path", ""))
    report_path = str(bundle.get("report_path", ""))
    prediction_path = bundle.get("prediction_path")
    for key, value in [
        ("submission_path", submission_path),
        ("report_path", report_path),
        ("prediction_path", prediction_path),
    ]:
        if value and not _is_safe_relative_path(str(value)):
            errors.append(f"{key} must be a safe relative path")

    files = bundle.get("files")
    if not isinstance(files, list):
        errors.append("files must be a list")
        files = []
    file_entries = _validate_bundle_files(files, root, errors)

    submission = None
    submission_validation = None
    if submission_path:
        resolved_submission_path = _resolve_bundle_path(submission_path, root)
        if not resolved_submission_path.exists():
            errors.append(f"submission_path does not exist: {submission_path}")
        else:
            try:
                submission = load_leaderboard_submission(resolved_submission_path)
            except (OSError, json.JSONDecodeError) as exc:
                errors.append(f"could not load submission_path: {exc}")
            else:
                submission_validation = validate_leaderboard_submission(submission, base_dir=root)
                if not submission_validation["valid"]:
                    errors.append(f"referenced submission is invalid: {submission_validation['errors']}")
                warnings.extend(submission_validation["warnings"])

    report = None
    if report_path:
        resolved_report_path = _resolve_bundle_path(report_path, root)
        if not resolved_report_path.exists():
            errors.append(f"report_path does not exist: {report_path}")
        else:
            try:
                report = load_benchmark_report(resolved_report_path)
            except (OSError, json.JSONDecodeError) as exc:
                errors.append(f"could not load report_path: {exc}")
            else:
                report_validation = validate_benchmark_report(report)
                if not report_validation["valid"]:
                    errors.append(f"referenced report is invalid: {report_validation['errors']}")
                warnings.extend(report_validation["warnings"])

    if "submission" not in file_entries:
        errors.append("files must include a submission entry")
    if "report" not in file_entries:
        errors.append("files must include a report entry")
    if prediction_path and "predictions" not in file_entries:
        errors.append("files must include a predictions entry when prediction_path is set")

    if submission is not None:
        _expect_equal(bundle, "system_name", submission.get("system_name"), errors)
        _expect_equal(bundle, "system_version", submission.get("system_version"), errors)
        _expect_equal(bundle, "submitter", submission.get("submitter"), errors)
        _expect_equal(bundle, "suite_id", submission.get("suite_id"), errors)
        _expect_equal(bundle, "suite_version", submission.get("suite_version"), errors)
        _expect_equal(bundle, "suite_hash", submission.get("suite_hash"), errors)
        _expect_equal(bundle, "report_sha256", submission.get("report_sha256"), errors)
        _expect_equal(bundle, "overall_score", submission.get("overall_score"), errors)
    if report is not None:
        _expect_equal(bundle, "suite_id", report.get("suite_id"), errors)
        _expect_equal(bundle, "suite_version", report.get("suite_version"), errors)
        _expect_equal(bundle, "suite_hash", report.get("suite_hash"), errors)
        _expect_equal(bundle, "overall_score", report.get("overall_score"), errors)

    checklist = bundle.get("review_checklist")
    if not isinstance(checklist, Mapping):
        errors.append("review_checklist must be an object")
    else:
        for key in [
            "report_valid",
            "submission_valid",
            "disclosures_complete",
            "paths_are_relative",
            "file_hashes_current",
            "ready_for_leaderboard_review",
        ]:
            if checklist.get(key) is not True:
                errors.append(f"review_checklist.{key} must be true")

    return {
        "schema": SUBMISSION_BUNDLE_VALIDATION_SCHEMA,
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
        "summary": {
            "system_name": bundle.get("system_name"),
            "system_version": bundle.get("system_version"),
            "submitter": bundle.get("submitter"),
            "suite_id": bundle.get("suite_id"),
            "suite_version": bundle.get("suite_version"),
            "suite_hash": bundle.get("suite_hash"),
            "overall_score": bundle.get("overall_score"),
            "ready_for_leaderboard_review": not errors,
        },
    }


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


def _disclosures_complete(disclosures: Any) -> bool:
    return isinstance(disclosures, Mapping) and all(str(disclosures.get(field, "")).strip() for field in DISCLOSURE_FIELDS)


def _resolve_report_path(report_path: str, base_dir: str | Path | None) -> Path:
    path = Path(report_path)
    if path.is_absolute():
        return path
    return Path(base_dir or Path.cwd()) / path


def _resolve_bundle_path(path: str | Path, base_dir: Path) -> Path:
    raw_path = Path(path)
    if raw_path.is_absolute():
        return raw_path.resolve()
    return (base_dir / raw_path).resolve()


def _portable_relative_path(path: Path, base_dir: Path) -> str:
    try:
        return path.resolve().relative_to(base_dir.resolve()).as_posix()
    except ValueError as exc:
        raise ValueError(f"path is outside bundle base directory: {path}") from exc


def _is_safe_relative_path(path: str) -> bool:
    normalized = Path(path)
    return not normalized.is_absolute() and ".." not in normalized.parts


def _bundle_file_entry(role: str, path: Path, base_dir: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"{role} file does not exist: {path}")
    data = _canonical_file_bytes(path)
    return {
        "role": role,
        "path": _portable_relative_path(path, base_dir),
        "sha256": hashlib.sha256(data).hexdigest(),
        "bytes": len(data),
    }


def _validate_bundle_files(
    files: list[Any],
    base_dir: Path,
    errors: list[str],
) -> dict[str, Mapping[str, Any]]:
    entries: dict[str, Mapping[str, Any]] = {}
    for index, item in enumerate(files):
        if not isinstance(item, Mapping):
            errors.append(f"files[{index}] must be an object")
            continue
        role = str(item.get("role", ""))
        path = str(item.get("path", ""))
        if not role:
            errors.append(f"files[{index}].role is required")
            continue
        if role in entries:
            errors.append(f"duplicate file role: {role}")
            continue
        entries[role] = item
        if not path:
            errors.append(f"files[{index}].path is required")
            continue
        if not _is_safe_relative_path(path):
            errors.append(f"files[{index}].path must be a safe relative path")
            continue
        resolved_path = _resolve_bundle_path(path, base_dir)
        if not resolved_path.exists():
            errors.append(f"files[{index}].path does not exist: {path}")
            continue
        data = _canonical_file_bytes(resolved_path)
        expected_sha = hashlib.sha256(data).hexdigest()
        if item.get("sha256") != expected_sha:
            errors.append(f"files[{index}].sha256 mismatch for {path}")
        if item.get("bytes") != len(data):
            errors.append(f"files[{index}].bytes mismatch for {path}")
    return entries


def _canonical_file_bytes(path: str | Path) -> bytes:
    data = Path(path).read_bytes()
    if b"\0" in data:
        return data
    return data.replace(b"\r\n", b"\n")


def _require_string(submission: Mapping[str, Any], key: str, errors: list[str]) -> None:
    if not str(submission.get(key, "")).strip():
        errors.append(f"{key} is required")


def _expect_equal(submission: Mapping[str, Any], key: str, expected: Any, errors: list[str]) -> None:
    actual = submission.get(key)
    if actual != expected:
        errors.append(f"{key} mismatch: expected {expected!r}, got {actual!r}")


__all__ = [
    "DISCLOSURE_FIELDS",
    "SUBMISSION_BUNDLE_SCHEMA",
    "SUBMISSION_BUNDLE_VALIDATION_SCHEMA",
    "SUBMISSION_SCHEMA",
    "SUBMISSION_VALIDATION_SCHEMA",
    "build_leaderboard_submission",
    "build_submission_bundle",
    "load_leaderboard_submission",
    "load_submission_bundle",
    "validate_submission_bundle",
    "validate_leaderboard_submission",
    "write_leaderboard_submission",
    "write_submission_bundle",
]
