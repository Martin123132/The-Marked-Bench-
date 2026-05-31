from __future__ import annotations

"""Third-party adoption evidence ledgers for benchmark standardization."""

import json
from pathlib import Path
from typing import Any, Mapping

from marked_bench.benchmark_claim import load_result_claim, validate_result_claim
from marked_bench.benchmark_registry import build_benchmark_registry
from marked_bench.benchmark_release import RELEASE_ID, file_sha256
from marked_bench.benchmark_result_card import load_result_card, validate_result_card
from marked_bench.benchmark_review import load_submission_review, validate_submission_review
from marked_bench.benchmark_submission import load_submission_bundle, validate_submission_bundle
from marked_bench.schema_validation import load_json_schema, validate_json_schema


EVIDENCE_LEDGER_SCHEMA = "marked_bench.third-party-evidence-ledger.v1"
DEFAULT_EVIDENCE_LEDGER = Path("adoption/third_party_evidence_ledger_v0_4_7.json")
DEFAULT_RELEASE_MANIFEST = Path("releases/marked_bench_release_v0_4_7.json")
DEFAULT_CONFORMANCE_REPORT = Path("conformance/marked_bench_conformance_v0_4_7.json")
DEFAULT_ADOPTION_PACKET = Path("adoption/marked_bench_adoption_packet_v0_4_7.json")


def build_evidence_ledger(entries: list[Mapping[str, Any]] | None = None) -> dict[str, Any]:
    """Build a deterministic third-party evidence ledger."""

    registry = build_benchmark_registry()
    ledger_entries = [dict(entry) for entry in (entries or [])]
    return {
        "schema": EVIDENCE_LEDGER_SCHEMA,
        "project": registry["project"],
        "benchmark_family": registry["benchmark_family"],
        "release_id": RELEASE_ID,
        "release_manifest_path": DEFAULT_RELEASE_MANIFEST.as_posix(),
        "conformance_report_path": DEFAULT_CONFORMANCE_REPORT.as_posix(),
        "adoption_packet_path": DEFAULT_ADOPTION_PACKET.as_posix(),
        "status": "awaiting-third-party-evidence" if not ledger_entries else "third-party-evidence-recorded",
        "entry_count": len(ledger_entries),
        "evidence_requirements": {
            "result_card_required": True,
            "submission_bundle_required": True,
            "submission_bundle_hash_required": True,
            "result_claim_required_for_public_score_claims": True,
            "review_hash_required_for_verified_status": True,
            "review_required_for_verified_status": True,
            "same_suite_hash_required": True,
            "public_url_or_committed_path_required": True,
            "no_unverified_adoption_claims": True,
        },
        "entries": ledger_entries,
    }


def write_evidence_ledger(
    path: str | Path = DEFAULT_EVIDENCE_LEDGER,
    *,
    entries: list[Mapping[str, Any]] | None = None,
) -> None:
    """Write a stable third-party evidence ledger."""

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(build_evidence_ledger(entries=entries), indent=2, sort_keys=True),
        encoding="utf-8",
    )


def load_evidence_ledger(path: str | Path) -> dict[str, Any]:
    """Load a third-party evidence ledger JSON file."""

    data = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError("third-party evidence ledger must be a JSON object")
    return data


def validate_evidence_ledger(ledger: Mapping[str, Any], root: str | Path = ".") -> dict[str, Any]:
    """Validate a third-party evidence ledger and any committed result evidence."""

    root_path = Path(root)
    errors: list[str] = []
    warnings: list[str] = []

    schema_path = root_path / "schemas" / "third_party_evidence_ledger.schema.json"
    if schema_path.exists():
        schema = load_json_schema(schema_path)
        errors.extend(validate_json_schema(ledger, schema, schema_path=schema_path))
    else:
        errors.append(f"{schema_path}: third-party evidence ledger schema is missing")

    entries = ledger.get("entries", [])
    if not isinstance(entries, list):
        errors.append("entries must be a list")
        entries = []
    if ledger.get("entry_count") != len(entries):
        errors.append("entry_count does not match entries length")
    if ledger.get("release_id") != RELEASE_ID:
        errors.append(f"release_id does not match current release: {RELEASE_ID}")
    if ledger.get("release_manifest_path") != DEFAULT_RELEASE_MANIFEST.as_posix():
        errors.append("release_manifest_path does not match current release")
    if ledger.get("conformance_report_path") != DEFAULT_CONFORMANCE_REPORT.as_posix():
        errors.append("conformance_report_path does not match current release")
    if ledger.get("adoption_packet_path") != DEFAULT_ADOPTION_PACKET.as_posix():
        errors.append("adoption_packet_path does not match current release")

    for path in [
        Path(str(ledger.get("release_manifest_path", ""))),
        Path(str(ledger.get("conformance_report_path", ""))),
        Path(str(ledger.get("adoption_packet_path", ""))),
    ]:
        if path.as_posix() and not (root_path / path).exists():
            errors.append(f"{path}: referenced evidence ledger path is missing")

    track_by_identity = {
        (track["suite_id"], track["suite_version"], track["suite_hash"]): track
        for track in build_benchmark_registry()["tracks"]
    }
    for index, entry in enumerate(entries):
        if not isinstance(entry, Mapping):
            errors.append(f"entries[{index}] must be an object")
            continue
        errors.extend(_entry_errors(root_path, entry, index, track_by_identity))

    summary = {
        "release_id": ledger.get("release_id", ""),
        "status": ledger.get("status", ""),
        "entry_count": len(entries),
        "verified_entry_count": len(
            [entry for entry in entries if isinstance(entry, Mapping) and entry.get("verification_status") == "verified"]
        ),
    }
    return {
        "valid": not errors,
        "schema": ledger.get("schema", ""),
        "summary": summary,
        "errors": errors,
        "warnings": warnings,
    }


def _entry_errors(
    root: Path,
    entry: Mapping[str, Any],
    index: int,
    track_by_identity: Mapping[tuple[Any, Any, Any], Mapping[str, Any]],
) -> list[str]:
    errors: list[str] = []
    identity = (entry.get("suite_id"), entry.get("suite_version"), entry.get("suite_hash"))
    if identity not in track_by_identity:
        errors.append(f"entries[{index}]: suite identity is not in the benchmark registry")

    result_card_path = _entry_path(entry, "result_card_path", errors, index)
    result_card_sha = _required_sha(entry, "result_card_sha256", errors, index)
    if result_card_path is None:
        errors.append(f"entries[{index}]: result_card_path is required")
    elif not (root / result_card_path).exists():
        errors.append(f"entries[{index}]: result card is missing: {result_card_path}")
    else:
        actual_sha = file_sha256(root / result_card_path)
        if result_card_sha and actual_sha != result_card_sha:
            errors.append(f"entries[{index}]: result_card_sha256 does not match {result_card_path}")
        try:
            card = load_result_card(root / result_card_path)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            errors.append(f"entries[{index}]: could not load result card: {exc}")
        else:
            validation = validate_result_card(card, base_dir=(root / result_card_path).parent)
            if not validation["valid"]:
                errors.append(f"entries[{index}]: result card validation failed: {validation['errors']}")
            for key in ["suite_id", "suite_version", "suite_hash", "system_name", "system_version"]:
                if entry.get(key) != card.get(key):
                    errors.append(f"entries[{index}]: {key} does not match result card")

    bundle_path = _entry_path(entry, "submission_bundle_path", errors, index)
    bundle_sha = _required_sha(entry, "submission_bundle_sha256", errors, index)
    if bundle_path is None:
        errors.append(f"entries[{index}]: submission_bundle_path is required")
    elif not (root / bundle_path).exists():
        errors.append(f"entries[{index}]: submission bundle is missing: {bundle_path}")
    else:
        actual_sha = file_sha256(root / bundle_path)
        if bundle_sha and actual_sha != bundle_sha:
            errors.append(f"entries[{index}]: submission_bundle_sha256 does not match {bundle_path}")
        try:
            bundle = load_submission_bundle(root / bundle_path)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            errors.append(f"entries[{index}]: could not load submission bundle: {exc}")
        else:
            validation = validate_submission_bundle(bundle, base_dir=(root / bundle_path).parent)
            if not validation["valid"]:
                errors.append(f"entries[{index}]: submission bundle validation failed: {validation['errors']}")
            for key in ["suite_id", "suite_version", "suite_hash", "system_name", "system_version", "submitter"]:
                if entry.get(key) != bundle.get(key):
                    errors.append(f"entries[{index}]: {key} does not match submission bundle")

    status = entry.get("verification_status")
    if status == "verified" and not entry.get("review_path"):
        errors.append(f"entries[{index}]: verified entries require review_path")
    if status == "verified" and not entry.get("review_sha256"):
        errors.append(f"entries[{index}]: verified entries require review_sha256")
    if entry.get("adoption_claim") is True and status != "verified":
        errors.append(f"entries[{index}]: adoption_claim requires verified status")

    review_path = _entry_path(entry, "review_path", errors, index)
    review_decision = entry.get("review_decision")
    if review_path is not None:
        review_sha = _required_sha(entry, "review_sha256", errors, index)
        if not (root / review_path).exists():
            errors.append(f"entries[{index}]: review is missing: {review_path}")
        else:
            actual_sha = file_sha256(root / review_path)
            if review_sha and actual_sha != review_sha:
                errors.append(f"entries[{index}]: review_sha256 does not match {review_path}")
            try:
                review = load_submission_review(root / review_path)
            except (OSError, ValueError, json.JSONDecodeError) as exc:
                errors.append(f"entries[{index}]: could not load submission review: {exc}")
            else:
                validation = validate_submission_review(review, base_dir=(root / review_path).parent)
                if not validation["valid"]:
                    errors.append(f"entries[{index}]: submission review validation failed: {validation['errors']}")
                for key in ["suite_id", "suite_version", "suite_hash", "system_name", "system_version", "submitter"]:
                    if entry.get(key) != review.get(key):
                        errors.append(f"entries[{index}]: {key} does not match submission review")
                if review_decision is not None and review_decision != review.get("decision"):
                    errors.append(f"entries[{index}]: review_decision does not match submission review")
    if entry.get("adoption_claim") is True and review_decision != "accept":
        errors.append(f"entries[{index}]: adoption_claim requires an accepted review decision")

    result_claim_path = _entry_path(entry, "result_claim_path", errors, index)
    result_claim_sha = str(entry.get("result_claim_sha256", ""))
    if result_claim_path is not None:
        if not result_claim_sha:
            errors.append(f"entries[{index}]: result_claim_sha256 is required when result_claim_path is set")
        if not (root / result_claim_path).exists():
            errors.append(f"entries[{index}]: result claim is missing: {result_claim_path}")
        else:
            actual_sha = file_sha256(root / result_claim_path)
            if result_claim_sha and actual_sha != result_claim_sha:
                errors.append(f"entries[{index}]: result_claim_sha256 does not match {result_claim_path}")
            try:
                claim = load_result_claim(root / result_claim_path)
            except (OSError, ValueError, json.JSONDecodeError) as exc:
                errors.append(f"entries[{index}]: could not load result claim: {exc}")
            else:
                validation = validate_result_claim(claim, base_dir=(root / result_claim_path).parent)
                if not validation["valid"]:
                    errors.append(f"entries[{index}]: result claim validation failed: {validation['errors']}")
                for key in ["suite_id", "suite_version", "suite_hash", "system_name", "system_version"]:
                    if entry.get(key) != claim.get(key):
                        errors.append(f"entries[{index}]: {key} does not match result claim")
    return errors


def _entry_path(
    entry: Mapping[str, Any],
    key: str,
    errors: list[str],
    index: int,
) -> Path | None:
    raw_value = entry.get(key)
    if raw_value in (None, ""):
        return None
    path = Path(str(raw_value))
    if path.is_absolute() or ".." in path.parts:
        errors.append(f"entries[{index}]: {key} must be a safe relative path")
        return None
    return path


def _required_sha(entry: Mapping[str, Any], key: str, errors: list[str], index: int) -> str:
    value = str(entry.get(key, ""))
    if not value:
        errors.append(f"entries[{index}]: {key} is required")
    return value


__all__ = [
    "DEFAULT_EVIDENCE_LEDGER",
    "EVIDENCE_LEDGER_SCHEMA",
    "build_evidence_ledger",
    "load_evidence_ledger",
    "validate_evidence_ledger",
    "write_evidence_ledger",
]
