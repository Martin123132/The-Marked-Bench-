from __future__ import annotations

"""Structured review rubrics for leaderboard submission bundles."""

import hashlib
import json
import time
from pathlib import Path
from typing import Any, Mapping

from marked_bench.benchmark_submission import load_submission_bundle, validate_submission_bundle
from marked_bench.contradiction.benchmark_suite import load_benchmark_report


REVIEW_SCHEMA = "marked_bench.submission-review.v1"
REVIEW_VALIDATION_SCHEMA = "marked_bench.submission-review-validation.v1"
REVIEW_DECISIONS = ("needs_review", "accept", "needs_revision", "reject")

RUBRIC_DIMENSIONS: dict[str, dict[str, str | int]] = {
    "reproducibility": {
        "max_score": 2,
        "criterion": "The bundle, report, hashes, suite identity, and commands are reproducible.",
    },
    "disclosure_quality": {
        "max_score": 2,
        "criterion": "Model, prompting, preprocessing, retrieval, postprocessing, training data, and runtime are disclosed.",
    },
    "score_integrity": {
        "max_score": 2,
        "criterion": "The reported score is backed by a valid report and no unexplained metric mismatch.",
    },
    "explanation_coverage": {
        "max_score": 2,
        "criterion": "Rationale and evidence fields cover enough cases for meaningful review.",
    },
    "evidence_quality": {
        "max_score": 2,
        "criterion": "Evidence quotes or references support the predicted labels without leaking expected labels.",
    },
    "limitations": {
        "max_score": 2,
        "criterion": "Known limitations, failure modes, and benchmark-use caveats are stated clearly.",
    },
}

ACCEPT_RECOMMENDATION_MINIMUM = 9


def build_submission_review(
    bundle_path: str | Path,
    *,
    reviewer: str = "unassigned",
    decision: str = "needs_review",
    notes: str = "",
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    """Build a structured reviewer rubric template for a submission bundle."""

    root = Path(base_dir or Path.cwd()).resolve()
    resolved_bundle_path = _resolve_review_path(bundle_path, root)
    bundle = load_submission_bundle(resolved_bundle_path)
    bundle_validation = validate_submission_bundle(bundle, base_dir=resolved_bundle_path.parent)
    report = load_benchmark_report(resolved_bundle_path.parent / str(bundle["report_path"]))
    review = {
        "schema": REVIEW_SCHEMA,
        "created_at": round(time.time(), 3),
        "reviewer": str(reviewer),
        "decision": _normalize_decision(decision),
        "bundle_path": _portable_relative_path(resolved_bundle_path, root),
        "bundle_sha256": _file_sha256(resolved_bundle_path),
        "system_name": bundle.get("system_name"),
        "system_version": bundle.get("system_version"),
        "submitter": bundle.get("submitter"),
        "suite_id": bundle.get("suite_id"),
        "suite_version": bundle.get("suite_version"),
        "suite_hash": bundle.get("suite_hash"),
        "overall_score": bundle.get("overall_score"),
        "explanation_audit": report.get("explanation_audit", {}),
        "automated_checks": {
            "bundle_valid": bundle_validation["valid"],
            "bundle_error_count": len(bundle_validation["errors"]),
            "bundle_warning_count": len(bundle_validation["warnings"]),
            "ready_for_leaderboard_review": bundle_validation["summary"]["ready_for_leaderboard_review"],
        },
        "rubric": _empty_rubric(),
        "summary": _review_summary(_empty_rubric()),
        "notes": str(notes),
    }
    return review


def write_submission_review(review: Mapping[str, Any], path: str | Path) -> None:
    """Write a submission review JSON file."""

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(review, indent=2, sort_keys=True), encoding="utf-8")


def load_submission_review(path: str | Path) -> dict[str, Any]:
    """Load a submission review JSON file."""

    return json.loads(Path(path).read_text(encoding="utf-8"))


def validate_submission_review(
    review: Mapping[str, Any],
    *,
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    """Validate a structured reviewer rubric against its submission bundle."""

    root = Path(base_dir or Path.cwd()).resolve()
    errors: list[str] = []
    warnings: list[str] = []
    _expect_equal(review, "schema", REVIEW_SCHEMA, errors)
    _require_string(review, "reviewer", errors)
    _require_string(review, "decision", errors)
    _require_string(review, "bundle_path", errors)
    _require_string(review, "bundle_sha256", errors)

    decision = str(review.get("decision", ""))
    if decision not in REVIEW_DECISIONS:
        errors.append(f"decision must be one of: {', '.join(REVIEW_DECISIONS)}")

    bundle = None
    bundle_path = str(review.get("bundle_path", ""))
    if bundle_path and not _is_safe_relative_path(bundle_path):
        errors.append("bundle_path must be a safe relative path")
    elif bundle_path:
        resolved_bundle_path = _resolve_review_path(bundle_path, root)
        if not resolved_bundle_path.exists():
            errors.append(f"bundle_path does not exist: {bundle_path}")
        else:
            bundle_sha256 = _file_sha256(resolved_bundle_path)
            if review.get("bundle_sha256") != bundle_sha256:
                errors.append(f"bundle_sha256 mismatch: expected {bundle_sha256!r}, got {review.get('bundle_sha256')!r}")
            try:
                bundle = load_submission_bundle(resolved_bundle_path)
            except (OSError, json.JSONDecodeError) as exc:
                errors.append(f"could not load bundle_path: {exc}")
            else:
                bundle_validation = validate_submission_bundle(bundle, base_dir=resolved_bundle_path.parent)
                if not bundle_validation["valid"]:
                    errors.append(f"referenced bundle is invalid: {bundle_validation['errors']}")
                warnings.extend(bundle_validation["warnings"])

    if bundle is not None:
        for key in [
            "system_name",
            "system_version",
            "submitter",
            "suite_id",
            "suite_version",
            "suite_hash",
            "overall_score",
        ]:
            _expect_equal(review, key, bundle.get(key), errors)

    rubric = _validate_rubric(review.get("rubric"), errors)
    expected_summary = _review_summary(rubric)
    _expect_equal(review, "summary", expected_summary, errors)

    if decision in {"accept", "needs_revision", "reject"} and not expected_summary["ready_for_decision"]:
        errors.append(f"decision {decision!r} requires completed rubric scores")
    if decision == "accept" and expected_summary["recommendation"] != "accept":
        errors.append("decision 'accept' requires an accept-level rubric recommendation")

    return {
        "schema": REVIEW_VALIDATION_SCHEMA,
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
        "summary": {
            "system_name": review.get("system_name"),
            "system_version": review.get("system_version"),
            "submitter": review.get("submitter"),
            "suite_id": review.get("suite_id"),
            "suite_version": review.get("suite_version"),
            "overall_score": review.get("overall_score"),
            "decision": review.get("decision"),
            "ready_for_decision": expected_summary["ready_for_decision"],
            "rubric_total": expected_summary["rubric_total"],
            "rubric_max": expected_summary["rubric_max"],
            "recommendation": expected_summary["recommendation"],
        },
    }


def _empty_rubric() -> dict[str, dict[str, Any]]:
    return {
        name: {
            "score": None,
            "max_score": spec["max_score"],
            "criterion": spec["criterion"],
            "notes": "",
        }
        for name, spec in RUBRIC_DIMENSIONS.items()
    }


def _validate_rubric(raw_rubric: Any, errors: list[str]) -> dict[str, dict[str, Any]]:
    if not isinstance(raw_rubric, Mapping):
        errors.append("rubric must be an object")
        return _empty_rubric()
    rubric: dict[str, dict[str, Any]] = {}
    for name, spec in RUBRIC_DIMENSIONS.items():
        raw_entry = raw_rubric.get(name)
        if not isinstance(raw_entry, Mapping):
            errors.append(f"rubric.{name} must be an object")
            rubric[name] = dict(_empty_rubric()[name])
            continue
        score = raw_entry.get("score")
        if score is not None:
            if isinstance(score, bool) or not isinstance(score, int):
                errors.append(f"rubric.{name}.score must be null or an integer")
            elif score < 0 or score > int(spec["max_score"]):
                errors.append(f"rubric.{name}.score must be between 0 and {spec['max_score']}")
        if raw_entry.get("max_score") != spec["max_score"]:
            errors.append(f"rubric.{name}.max_score must be {spec['max_score']}")
        if str(raw_entry.get("criterion", "")) != str(spec["criterion"]):
            errors.append(f"rubric.{name}.criterion does not match the standard rubric")
        rubric[name] = {
            "score": score if isinstance(score, int) and not isinstance(score, bool) else None,
            "max_score": spec["max_score"],
            "criterion": spec["criterion"],
            "notes": str(raw_entry.get("notes", "")),
        }
    extra = sorted(set(raw_rubric) - set(RUBRIC_DIMENSIONS))
    for name in extra:
        errors.append(f"rubric.{name} is not a recognized rubric dimension")
    return rubric


def _review_summary(rubric: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    scores = [entry.get("score") for entry in rubric.values()]
    completed = [score for score in scores if isinstance(score, int) and not isinstance(score, bool)]
    rubric_max = sum(int(spec["max_score"]) for spec in RUBRIC_DIMENSIONS.values())
    ready = len(completed) == len(RUBRIC_DIMENSIONS)
    total = sum(completed) if ready else None
    recommendation = "needs_review"
    if ready and total is not None:
        if total >= ACCEPT_RECOMMENDATION_MINIMUM and all(score > 0 for score in completed):
            recommendation = "accept"
        elif any(score == 0 for score in completed):
            recommendation = "reject"
        else:
            recommendation = "needs_revision"
    return {
        "completed_dimensions": len(completed),
        "dimension_count": len(RUBRIC_DIMENSIONS),
        "rubric_total": total,
        "rubric_max": rubric_max,
        "accept_recommendation_minimum": ACCEPT_RECOMMENDATION_MINIMUM,
        "ready_for_decision": ready,
        "recommendation": recommendation,
    }


def _normalize_decision(decision: str) -> str:
    value = str(decision or "needs_review").strip().lower().replace("-", "_")
    if value not in REVIEW_DECISIONS:
        return "needs_review"
    return value


def _file_sha256(path: str | Path) -> str:
    digest = hashlib.sha256()
    digest.update(_canonical_file_bytes(path))
    return digest.hexdigest()


def _canonical_file_bytes(path: str | Path) -> bytes:
    data = Path(path).read_bytes()
    if b"\0" in data:
        return data
    return data.replace(b"\r\n", b"\n")


def _resolve_review_path(path: str | Path, base_dir: Path) -> Path:
    raw_path = Path(path)
    if raw_path.is_absolute():
        return raw_path.resolve()
    return (base_dir / raw_path).resolve()


def _portable_relative_path(path: Path, base_dir: Path) -> str:
    try:
        return path.resolve().relative_to(base_dir.resolve()).as_posix()
    except ValueError as exc:
        raise ValueError(f"path is outside review base directory: {path}") from exc


def _is_safe_relative_path(path: str) -> bool:
    normalized = Path(path)
    return not normalized.is_absolute() and ".." not in normalized.parts


def _require_string(review: Mapping[str, Any], key: str, errors: list[str]) -> None:
    if not str(review.get(key, "")).strip():
        errors.append(f"{key} is required")


def _expect_equal(review: Mapping[str, Any], key: str, expected: Any, errors: list[str]) -> None:
    actual = review.get(key)
    if actual != expected:
        errors.append(f"{key} mismatch: expected {expected!r}, got {actual!r}")


__all__ = [
    "ACCEPT_RECOMMENDATION_MINIMUM",
    "REVIEW_DECISIONS",
    "REVIEW_SCHEMA",
    "REVIEW_VALIDATION_SCHEMA",
    "RUBRIC_DIMENSIONS",
    "build_submission_review",
    "load_submission_review",
    "validate_submission_review",
    "write_submission_review",
]
