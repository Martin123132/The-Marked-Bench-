from __future__ import annotations

"""Machine-checkable public result claims."""

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from marked_bench.benchmark_publication import load_publication_packet, validate_publication_packet
from marked_bench.benchmark_release import RELEASE_ID
from marked_bench.schema_validation import load_json_schema, validate_json_schema


RESULT_CLAIM_SCHEMA = "marked_bench.result-claim.v1"
RESULT_CLAIM_VALIDATION_SCHEMA = "marked_bench.result-claim-validation.v1"
RESULT_CLAIM_FILENAME = "result_claim.json"


def build_result_claim(
    publication_packet_path: str | Path,
    *,
    base_dir: str | Path | None = None,
    claim_url: str = "",
    evidence_url: str = "",
    notes: str = "",
) -> dict[str, Any]:
    """Build a citeable claim from a validated publication packet."""

    root = Path(base_dir or Path.cwd()).resolve()
    resolved_packet_path = _resolve_claim_path(publication_packet_path, root)
    packet = load_publication_packet(resolved_packet_path)
    packet_validation = validate_publication_packet(packet, base_dir=resolved_packet_path.parent)
    if not packet_validation["valid"]:
        raise ValueError(f"publication packet validation failed: {packet_validation['errors']}")

    score_display = _format_score(packet["overall_score"])
    suite_ref = f"{packet['suite_id']} v{packet['suite_version']}"
    claim_text = (
        f"{packet['system_name']} {packet['system_version']} scored {score_display} on "
        f"The Marked Bench {suite_ref} using suite hash {packet['suite_hash']} and "
        f"release {packet['release_id']}. This is a public benchmark result, not a safety certification."
    )

    return {
        "schema": RESULT_CLAIM_SCHEMA,
        "created_at": packet.get("created_at"),
        "release_id": packet.get("release_id"),
        "system_name": packet.get("system_name"),
        "system_version": packet.get("system_version"),
        "submitter": packet.get("submitter"),
        "suite_id": packet.get("suite_id"),
        "suite_version": packet.get("suite_version"),
        "suite_hash": packet.get("suite_hash"),
        "overall_score": packet.get("overall_score"),
        "case_count": packet.get("case_count"),
        "failure_count": packet.get("failure_count"),
        "claim": {
            "text": claim_text,
            "badge_label": f"Marked Bench {score_display} - {suite_ref}",
            "permitted_summary": "Public result on the pinned suite, version, and suite hash only.",
            "not_claims": [
                "Not a safety certification.",
                "Not a general intelligence claim.",
                "Not comparable across different suite hashes.",
                "Not evidence of third-party adoption unless separately verified in the evidence ledger.",
            ],
        },
        "evidence": {
            "publication_packet_path": _portable_relative_path(resolved_packet_path, root),
            "publication_packet_sha256": _file_sha256(resolved_packet_path),
            "result_card_sha256": packet.get("result_card_sha256"),
            "report_sha256": packet.get("report_sha256"),
            "claim_url": str(claim_url),
            "evidence_url": str(evidence_url),
        },
        "validation": _validation_entry(packet_validation),
        "standard_claims": {
            "same_suite_hash_required": True,
            "full_publication_packet_required": True,
            "result_card_required": True,
            "public_test_result": True,
            "not_safety_certification": True,
            "not_general_intelligence_claim": True,
            "third_party_adoption_requires_verified_evidence": True,
        },
        "notes": str(notes),
    }


def write_result_claim(claim: Mapping[str, Any], path: str | Path) -> None:
    """Write a result claim JSON file."""

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(claim, indent=2, sort_keys=True), encoding="utf-8")


def load_result_claim(path: str | Path) -> dict[str, Any]:
    """Load a result claim JSON file."""

    data = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError("result claim must be a JSON object")
    return data


def validate_result_claim(
    claim: Mapping[str, Any],
    *,
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    """Validate a result claim against its publication packet evidence."""

    root = Path(base_dir or Path.cwd()).resolve()
    errors: list[str] = []
    warnings: list[str] = []

    schema_path = _find_schema_path(root)
    if schema_path is not None:
        schema = load_json_schema(schema_path)
        errors.extend(validate_json_schema(claim, schema, schema_path=schema_path))
    else:
        warnings.append("schemas/result_claim.schema.json was not found; skipped schema validation")

    if claim.get("schema") != RESULT_CLAIM_SCHEMA:
        errors.append(f"schema must be {RESULT_CLAIM_SCHEMA!r}")

    evidence = claim.get("evidence")
    packet_path = ""
    if not isinstance(evidence, Mapping):
        errors.append("evidence must be an object")
    else:
        packet_path = str(evidence.get("publication_packet_path", ""))
        if not packet_path:
            errors.append("evidence.publication_packet_path is required")
        elif not _is_safe_relative_path(packet_path):
            errors.append("evidence.publication_packet_path must be a safe relative path")
        else:
            resolved_packet_path = _resolve_claim_path(packet_path, root)
            if not resolved_packet_path.exists():
                errors.append(f"evidence.publication_packet_path does not exist: {packet_path}")
            elif evidence.get("publication_packet_sha256") != _file_sha256(resolved_packet_path):
                errors.append("evidence.publication_packet_sha256 does not match publication packet")

    if packet_path and not errors:
        try:
            expected = build_result_claim(
                packet_path,
                base_dir=root,
                claim_url=str(evidence.get("claim_url", "")) if isinstance(evidence, Mapping) else "",
                evidence_url=str(evidence.get("evidence_url", "")) if isinstance(evidence, Mapping) else "",
                notes=str(claim.get("notes", "")),
            )
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            errors.append(f"could not rebuild result claim: {exc}")
        else:
            if dict(claim) != expected:
                errors.append("result claim does not match referenced publication packet evidence")

    validation = claim.get("validation")
    ready = isinstance(validation, Mapping) and validation.get("valid") is True
    return {
        "schema": RESULT_CLAIM_VALIDATION_SCHEMA,
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
        "summary": {
            "system_name": claim.get("system_name"),
            "system_version": claim.get("system_version"),
            "submitter": claim.get("submitter"),
            "suite_id": claim.get("suite_id"),
            "suite_version": claim.get("suite_version"),
            "overall_score": claim.get("overall_score"),
            "ready_for_citation": ready and not errors,
        },
    }


def _validation_entry(validation: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema": validation.get("schema", ""),
        "valid": bool(validation.get("valid")),
        "error_count": len(validation.get("errors", [])) if isinstance(validation.get("errors"), list) else 0,
        "warning_count": len(validation.get("warnings", [])) if isinstance(validation.get("warnings"), list) else 0,
    }


def _format_score(score: Any) -> str:
    return f"{float(score):.2f}"


def _file_sha256(path: str | Path) -> str:
    digest = hashlib.sha256()
    digest.update(_canonical_file_bytes(path))
    return digest.hexdigest()


def _canonical_file_bytes(path: str | Path) -> bytes:
    data = Path(path).read_bytes()
    if b"\0" in data:
        return data
    return data.replace(b"\r\n", b"\n")


def _resolve_claim_path(path: str | Path, base_dir: Path) -> Path:
    raw_path = Path(path)
    if raw_path.is_absolute():
        return raw_path.resolve()
    return (base_dir / raw_path).resolve()


def _portable_relative_path(path: Path, base_dir: Path) -> str:
    try:
        return path.resolve().relative_to(base_dir.resolve()).as_posix()
    except ValueError as exc:
        raise ValueError(f"path is outside result claim base directory: {path}") from exc


def _is_safe_relative_path(path: str) -> bool:
    normalized = Path(path)
    return not normalized.is_absolute() and ".." not in normalized.parts


def _find_schema_path(root: Path) -> Path | None:
    for base in [root, *root.parents]:
        candidate = base / "schemas" / "result_claim.schema.json"
        if candidate.exists():
            return candidate
    return None


__all__ = [
    "RESULT_CLAIM_FILENAME",
    "RESULT_CLAIM_SCHEMA",
    "RESULT_CLAIM_VALIDATION_SCHEMA",
    "build_result_claim",
    "load_result_claim",
    "validate_result_claim",
    "write_result_claim",
]
