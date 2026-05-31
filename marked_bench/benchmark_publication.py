from __future__ import annotations

"""One-command public result packets for external benchmark results."""

import hashlib
import json
import shutil
from pathlib import Path
from typing import Any, Mapping

from marked_bench.benchmark_leaderboard import report_sha256
from marked_bench.benchmark_release import RELEASE_ID
from marked_bench.benchmark_result_card import (
    build_result_card,
    load_result_card,
    validate_result_card,
    write_result_card,
)
from marked_bench.benchmark_review import (
    build_submission_review,
    load_submission_review,
    validate_submission_review,
    write_submission_review,
)
from marked_bench.benchmark_submission import (
    build_leaderboard_submission,
    build_submission_bundle,
    load_leaderboard_submission,
    load_submission_bundle,
    validate_leaderboard_submission,
    validate_submission_bundle,
    write_leaderboard_submission,
    write_submission_bundle,
)
from marked_bench.contradiction.benchmark_suite import load_benchmark_report, validate_benchmark_report
from marked_bench.schema_validation import load_json_schema, validate_json_schema


PUBLICATION_PACKET_SCHEMA = "marked_bench.publication-packet.v1"
PUBLICATION_PACKET_VALIDATION_SCHEMA = "marked_bench.publication-packet-validation.v1"

PACKET_FILENAME = "publication_packet.json"
REPORT_FILENAME = "report.json"
SUBMISSION_FILENAME = "submission.json"
SUBMISSION_BUNDLE_FILENAME = "submission_bundle.json"
SUBMISSION_REVIEW_FILENAME = "submission_review.json"
RESULT_CARD_FILENAME = "result_card.json"


def create_publication_packet(
    output_dir: str | Path,
    report_path: str | Path,
    *,
    prediction_path: str | Path | None = None,
    system_version: str,
    submitter: str,
    reviewer: str = "unassigned",
    review_decision: str = "needs_review",
    submission_notes: str = "",
    bundle_notes: str = "",
    review_notes: str = "",
    result_notes: str = "",
    packet_notes: str = "",
    disclosures: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Create a self-contained publication packet directory from a report."""

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    packet_report_path = output_path / REPORT_FILENAME
    _copy_input_file(Path(report_path), packet_report_path)

    packet_prediction_path = None
    if prediction_path is not None:
        source_prediction_path = Path(prediction_path)
        suffix = source_prediction_path.suffix if source_prediction_path.suffix in {".json", ".jsonl"} else ".jsonl"
        packet_prediction_path = output_path / f"predictions{suffix}"
        _copy_input_file(source_prediction_path, packet_prediction_path)

    submission_path = output_path / SUBMISSION_FILENAME
    submission = build_leaderboard_submission(
        REPORT_FILENAME,
        system_version=system_version,
        submitter=submitter,
        notes=submission_notes,
        disclosures=disclosures,
        base_dir=output_path,
    )
    write_leaderboard_submission(submission, submission_path)

    bundle_path = output_path / SUBMISSION_BUNDLE_FILENAME
    bundle = build_submission_bundle(
        SUBMISSION_FILENAME,
        prediction_path=packet_prediction_path.name if packet_prediction_path is not None else None,
        base_dir=output_path,
        notes=bundle_notes,
    )
    write_submission_bundle(bundle, bundle_path)

    review_path = output_path / SUBMISSION_REVIEW_FILENAME
    review = build_submission_review(
        SUBMISSION_BUNDLE_FILENAME,
        reviewer=reviewer,
        decision=review_decision,
        notes=review_notes,
        base_dir=output_path,
    )
    write_submission_review(review, review_path)

    result_card_path = output_path / RESULT_CARD_FILENAME
    card = build_result_card(
        REPORT_FILENAME,
        bundle_path=SUBMISSION_BUNDLE_FILENAME,
        review_path=SUBMISSION_REVIEW_FILENAME,
        base_dir=output_path,
        notes=result_notes,
    )
    write_result_card(card, result_card_path)

    packet = build_publication_packet(output_path, notes=packet_notes)
    write_publication_packet(packet, output_path / PACKET_FILENAME)
    return packet


def build_publication_packet(packet_dir: str | Path, *, notes: str = "") -> dict[str, Any]:
    """Build a deterministic manifest for an existing publication packet directory."""

    root = Path(packet_dir)
    report_path = root / REPORT_FILENAME
    submission_path = root / SUBMISSION_FILENAME
    bundle_path = root / SUBMISSION_BUNDLE_FILENAME
    review_path = root / SUBMISSION_REVIEW_FILENAME
    result_card_path = root / RESULT_CARD_FILENAME

    report = load_benchmark_report(report_path)
    submission = load_leaderboard_submission(submission_path)
    bundle = load_submission_bundle(bundle_path)
    review = load_submission_review(review_path)
    card = load_result_card(result_card_path)

    report_validation = validate_benchmark_report(report)
    submission_validation = validate_leaderboard_submission(submission, base_dir=root)
    bundle_validation = validate_submission_bundle(bundle, base_dir=root)
    review_validation = validate_submission_review(review, base_dir=root)
    result_card_validation = validate_result_card(card, base_dir=root)

    files = [
        _packet_file_entry("report", report_path, root),
        _packet_file_entry("submission", submission_path, root),
        _packet_file_entry("submission_bundle", bundle_path, root),
        _packet_file_entry("submission_review", review_path, root),
        _packet_file_entry("result_card", result_card_path, root),
    ]
    prediction_path = bundle.get("prediction_path")
    if prediction_path:
        files.append(_packet_file_entry("predictions", root / str(prediction_path), root))
    files.sort(key=lambda entry: entry["path"])

    source_times = [
        value
        for value in [
            report.get("created_at"),
            submission.get("created_at"),
            bundle.get("created_at"),
            review.get("created_at"),
            card.get("created_at"),
        ]
        if isinstance(value, (int, float)) and not isinstance(value, bool)
    ]
    created_at = round(max(source_times), 3) if source_times else None
    validations = {
        "report": _validation_entry(report_validation),
        "submission": _validation_entry(submission_validation),
        "submission_bundle": _validation_entry(bundle_validation),
        "submission_review": _validation_entry(review_validation),
        "result_card": _validation_entry(result_card_validation),
    }

    return {
        "schema": PUBLICATION_PACKET_SCHEMA,
        "created_at": created_at,
        "release_id": RELEASE_ID,
        "system_name": report.get("system_name"),
        "system_version": submission.get("system_version"),
        "submitter": submission.get("submitter"),
        "suite_id": report.get("suite_id"),
        "suite_version": report.get("suite_version"),
        "suite_hash": report.get("suite_hash"),
        "report_sha256": report_sha256(report_path),
        "result_card_sha256": _file_sha256(result_card_path),
        "overall_score": report.get("overall_score"),
        "case_count": report.get("case_count"),
        "failure_count": len(report.get("failures", [])) if isinstance(report.get("failures"), list) else None,
        "files": files,
        "validations": validations,
        "ready_for_publication": all(entry["valid"] for entry in validations.values()),
        "standard_claims": {
            "self_contained_public_result_packet": True,
            "same_suite_hash_required": True,
            "report_validator_required": True,
            "submission_bundle_required": True,
            "result_card_required": True,
            "not_safety_certification": True,
        },
        "notes": str(notes),
    }


def write_publication_packet(packet: Mapping[str, Any], path: str | Path) -> None:
    """Write a publication packet manifest."""

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(packet, indent=2, sort_keys=True), encoding="utf-8")


def load_publication_packet(path: str | Path) -> dict[str, Any]:
    """Load a publication packet manifest."""

    data = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError("publication packet must be a JSON object")
    return data


def validate_publication_packet(
    packet: Mapping[str, Any],
    *,
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    """Validate a publication packet manifest and every referenced artifact."""

    root = Path(base_dir or Path.cwd()).resolve()
    errors: list[str] = []
    warnings: list[str] = []

    schema_path = _find_schema_path(root)
    if schema_path is not None:
        schema = load_json_schema(schema_path)
        errors.extend(validate_json_schema(packet, schema, schema_path=schema_path))
    else:
        warnings.append("schemas/publication_packet.schema.json was not found; skipped schema validation")

    if packet.get("schema") != PUBLICATION_PACKET_SCHEMA:
        errors.append(f"schema must be {PUBLICATION_PACKET_SCHEMA!r}")

    files = packet.get("files")
    if not isinstance(files, list):
        errors.append("files must be a list")
        files = []
    roles = _validate_packet_files(files, root, errors)
    for role in ["report", "submission", "submission_bundle", "submission_review", "result_card"]:
        if role not in roles:
            errors.append(f"files must include a {role} entry")

    if not errors:
        try:
            expected = build_publication_packet(root, notes=str(packet.get("notes", "")))
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            errors.append(f"could not rebuild publication packet: {exc}")
        else:
            if dict(packet) != expected:
                errors.append("publication packet does not match referenced benchmark evidence")
            for name, entry in expected["validations"].items():
                if not entry["valid"]:
                    errors.append(f"{name} validation failed")

    validations = packet.get("validations")
    ready = isinstance(validations, Mapping) and all(
        isinstance(entry, Mapping) and entry.get("valid") is True for entry in validations.values()
    )
    return {
        "schema": PUBLICATION_PACKET_VALIDATION_SCHEMA,
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
        "summary": {
            "system_name": packet.get("system_name"),
            "system_version": packet.get("system_version"),
            "submitter": packet.get("submitter"),
            "suite_id": packet.get("suite_id"),
            "suite_version": packet.get("suite_version"),
            "overall_score": packet.get("overall_score"),
            "file_count": len(files),
            "ready_for_publication": ready and packet.get("ready_for_publication") is True,
        },
    }


def _copy_input_file(source: Path, destination: Path) -> None:
    resolved_source = source.resolve()
    resolved_destination = destination.resolve()
    if resolved_source == resolved_destination:
        return
    if not resolved_source.exists():
        raise FileNotFoundError(f"input file does not exist: {source}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(resolved_source, resolved_destination)


def _packet_file_entry(role: str, path: Path, base_dir: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"{role} file does not exist: {path}")
    data = _canonical_file_bytes(path)
    return {
        "role": role,
        "path": _portable_relative_path(path.resolve(), base_dir.resolve()),
        "sha256": hashlib.sha256(data).hexdigest(),
        "bytes": len(data),
    }


def _validate_packet_files(files: list[Any], base_dir: Path, errors: list[str]) -> set[str]:
    roles: set[str] = set()
    for index, item in enumerate(files):
        if not isinstance(item, Mapping):
            errors.append(f"files[{index}] must be an object")
            continue
        role = str(item.get("role", ""))
        path = str(item.get("path", ""))
        if not role:
            errors.append(f"files[{index}].role is required")
            continue
        if role in roles:
            errors.append(f"duplicate file role: {role}")
            continue
        roles.add(role)
        if not path:
            errors.append(f"files[{index}].path is required")
            continue
        if not _is_safe_relative_path(path):
            errors.append(f"files[{index}].path must be a safe relative path")
            continue
        resolved_path = (base_dir / path).resolve()
        if not resolved_path.exists():
            errors.append(f"files[{index}].path does not exist: {path}")
            continue
        data = _canonical_file_bytes(resolved_path)
        expected_sha = hashlib.sha256(data).hexdigest()
        if item.get("sha256") != expected_sha:
            errors.append(f"files[{index}].sha256 mismatch for {path}")
        if item.get("bytes") != len(data):
            errors.append(f"files[{index}].bytes mismatch for {path}")
    return roles


def _validation_entry(validation: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema": validation.get("schema", ""),
        "valid": bool(validation.get("valid")),
        "error_count": len(validation.get("errors", [])) if isinstance(validation.get("errors"), list) else 0,
        "warning_count": len(validation.get("warnings", [])) if isinstance(validation.get("warnings"), list) else 0,
    }


def _file_sha256(path: str | Path) -> str:
    digest = hashlib.sha256()
    digest.update(_canonical_file_bytes(path))
    return digest.hexdigest()


def _canonical_file_bytes(path: str | Path) -> bytes:
    data = Path(path).read_bytes()
    if b"\0" in data:
        return data
    return data.replace(b"\r\n", b"\n")


def _portable_relative_path(path: Path, base_dir: Path) -> str:
    try:
        return path.resolve().relative_to(base_dir.resolve()).as_posix()
    except ValueError as exc:
        raise ValueError(f"path is outside publication packet base directory: {path}") from exc


def _is_safe_relative_path(path: str) -> bool:
    normalized = Path(path)
    return not normalized.is_absolute() and ".." not in normalized.parts


def _find_schema_path(root: Path) -> Path | None:
    for base in [root, *root.parents]:
        candidate = base / "schemas" / "publication_packet.schema.json"
        if candidate.exists():
            return candidate
    return None


__all__ = [
    "PACKET_FILENAME",
    "PUBLICATION_PACKET_SCHEMA",
    "PUBLICATION_PACKET_VALIDATION_SCHEMA",
    "build_publication_packet",
    "create_publication_packet",
    "load_publication_packet",
    "validate_publication_packet",
    "write_publication_packet",
]
