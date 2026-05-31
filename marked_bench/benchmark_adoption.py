from __future__ import annotations

"""Adoption packet generation for public benchmark releases."""

import json
from pathlib import Path
from typing import Any, Mapping

from marked_bench.benchmark_registry import build_benchmark_registry
from marked_bench.benchmark_release import RELEASE_ID
from marked_bench.schema_validation import load_json_schema, validate_json_schema


ADOPTION_PACKET_SCHEMA = "marked_bench.adoption-packet.v1"
DEFAULT_ADOPTION_PACKET = Path("adoption/marked_bench_adoption_packet_v0_4_0.json")
DEFAULT_EVIDENCE_LEDGER = Path("adoption/third_party_evidence_ledger_v0_4_0.json")
DEFAULT_RELEASE_MANIFEST = Path("releases/marked_bench_release_v0_4_0.json")
DEFAULT_CONFORMANCE_REPORT = Path("conformance/marked_bench_conformance_v0_4_0.json")
REPOSITORY_URL = "https://github.com/Martin123132/The-Marked-Bench-"
RELEASE_URL = "https://github.com/Martin123132/The-Marked-Bench-/releases/tag/v0.4.0"


def build_adoption_packet(root: str | Path = ".") -> dict[str, Any]:
    """Build a deterministic packet for external benchmark adoption."""

    del root
    registry = build_benchmark_registry()
    return {
        "schema": ADOPTION_PACKET_SCHEMA,
        "project": registry["project"],
        "benchmark_family": registry["benchmark_family"],
        "release_id": RELEASE_ID,
        "repository_url": REPOSITORY_URL,
        "release_url": RELEASE_URL,
        "release_manifest_path": DEFAULT_RELEASE_MANIFEST.as_posix(),
        "conformance_report_path": DEFAULT_CONFORMANCE_REPORT.as_posix(),
        "default_track": registry["default_track"],
        "tracks": [
            {
                "name": track["name"],
                "suite_id": track["suite_id"],
                "suite_version": track["suite_version"],
                "suite_hash": track["suite_hash"],
                "case_count": track["case_count"],
                "status": track["status"],
            }
            for track in registry["tracks"]
        ],
        "standard_claims": {
            "same_suite_hash_required": True,
            "public_result_card_required": True,
            "release_conformance_required": True,
            "leaderboard_review_required": True,
            "not_safety_certification": True,
            "third_party_evidence_required_for_adoption_claims": True,
            "third_party_evidence_ledger_required": True,
        },
        "required_public_artifacts": [
            _artifact("registry", "benchmark_registry.json", "Machine-readable index of tracks, schemas, and commands."),
            _artifact("release_manifest", DEFAULT_RELEASE_MANIFEST.as_posix(), "SHA-256 pinning for public release files."),
            _artifact(
                "conformance_report",
                DEFAULT_CONFORMANCE_REPORT.as_posix(),
                "Machine-readable pass/fail evidence for the release package.",
            ),
            _artifact(
                "adoption_packet",
                DEFAULT_ADOPTION_PACKET.as_posix(),
                "Machine-readable packet for external users, mirrors, and announcements.",
            ),
            _artifact(
                "third_party_evidence_ledger",
                DEFAULT_EVIDENCE_LEDGER.as_posix(),
                "Checked ledger for external adoption evidence and verification status.",
            ),
            _artifact("technical_note", "docs/TECHNICAL_NOTE.md", "Generated suite hashes, baselines, and limitations."),
            _artifact("adoption_guide", "docs/ADOPTION_GUIDE.md", "External user workflow for scoring and submitting systems."),
            _artifact("announcement_package", "docs/ANNOUNCEMENT_PACKAGE.md", "Copy-ready public launch and citation material."),
            _artifact("third_party_evidence", "docs/THIRD_PARTY_EVIDENCE.md", "Evidence rules for adoption claims."),
            _artifact("result_card_schema", "schemas/result_card.schema.json", "Schema for publishable benchmark result cards."),
            _artifact("adoption_packet_schema", "schemas/adoption_packet.schema.json", "Schema for this adoption packet."),
            _artifact(
                "third_party_evidence_schema",
                "schemas/third_party_evidence_ledger.schema.json",
                "Schema for external adoption evidence ledgers.",
            ),
            _artifact(
                "checked_result_card",
                "submissions/example_external_jsonl/example_external_result_card.json",
                "Example result card with report, bundle, review, and hash evidence.",
            ),
        ],
        "adopter_workflow": [
            {
                "step": 1,
                "name": "pin_release",
                "command": "marked-bench --validate-conformance-report conformance/marked_bench_conformance_v0_4_0.json",
                "output": "Release conformance validation passes.",
            },
            {
                "step": 2,
                "name": "export_predictions",
                "command": (
                    "marked-bench --suite contradiction-multihop "
                    "--export-prediction-template artifacts/multihop-predictions.jsonl"
                ),
                "output": "A JSONL prediction template with stable public case IDs.",
            },
            {
                "step": 3,
                "name": "score_system",
                "command": (
                    "marked-bench --suite contradiction-multihop "
                    "--score-predictions artifacts/multihop-predictions.jsonl "
                    '--system-name "SYSTEM" --report artifacts/system-report.json'
                ),
                "output": "A validated benchmark report tied to the pinned suite hash.",
            },
            {
                "step": 4,
                "name": "create_submission",
                "command": (
                    "marked-bench --create-submission artifacts/system-submission.json "
                    "--submission-report artifacts/system-report.json "
                    '--system-version "VERSION" --submitter "SUBMITTER"'
                ),
                "output": "Submission metadata with method disclosures and report hash evidence.",
            },
            {
                "step": 5,
                "name": "bundle_submission",
                "command": (
                    "marked-bench --create-submission-bundle artifacts/system-bundle.json "
                    "--bundle-submission artifacts/system-submission.json"
                ),
                "output": "A portable submission bundle for review.",
            },
            {
                "step": 6,
                "name": "publish_result_card",
                "command": (
                    "marked-bench --create-result-card artifacts/system-result-card.json "
                    "--result-report artifacts/system-report.json "
                    "--result-bundle artifacts/system-bundle.json"
                ),
                "output": "A standard result card suitable for citation or leaderboard review.",
            },
        ],
        "validation_commands": [
            {
                "name": "artifact_gate",
                "command": "python scripts/validate_benchmark_artifacts.py",
                "proves": "Checked public artifacts match generated benchmark evidence.",
            },
            {
                "name": "unit_tests",
                "command": "python -m unittest discover -s tests",
                "proves": "Benchmark builders, validators, and CLI workflows behave as tested.",
            },
            {
                "name": "adoption_packet",
                "command": (
                    "marked-bench --validate-adoption-packet "
                    "adoption/marked_bench_adoption_packet_v0_4_0.json"
                ),
                "proves": "The external adoption packet matches the current release evidence.",
            },
            {
                "name": "third_party_evidence_ledger",
                "command": (
                    "marked-bench --validate-evidence-ledger "
                    "adoption/third_party_evidence_ledger_v0_4_0.json"
                ),
                "proves": "External adoption evidence claims are explicitly recorded and validated.",
            },
        ],
        "submission_channels": [
            {
                "name": "leaderboard_submission_issue",
                "path": ".github/ISSUE_TEMPLATE/leaderboard_submission.yml",
                "purpose": "Structured public intake for third-party result cards and submission bundles.",
            },
            {
                "name": "benchmark_case_issue",
                "path": ".github/ISSUE_TEMPLATE/benchmark_case.yml",
                "purpose": "Structured proposal path for new benchmark cases without mutating released cases.",
            },
            {
                "name": "pull_request_template",
                "path": ".github/PULL_REQUEST_TEMPLATE.md",
                "purpose": "Contributor checklist for artifact validation and release hygiene.",
            },
            {
                "name": "third_party_evidence_issue",
                "path": ".github/ISSUE_TEMPLATE/third_party_evidence.yml",
                "purpose": "Structured intake for public third-party adoption evidence.",
            },
        ],
        "announcement_assets": [
            {
                "audience": "researchers",
                "path": "docs/ANNOUNCEMENT_PACKAGE.md",
                "purpose": "Release summary, citation wording, and reproducibility checklist.",
            },
            {
                "audience": "implementers",
                "path": "docs/ADOPTION_GUIDE.md",
                "purpose": "Commands for scoring external systems and creating result cards.",
            },
            {
                "audience": "reviewers",
                "path": "docs/SUBMISSION_REVIEW_RUBRIC.md",
                "purpose": "Review criteria before leaderboard acceptance.",
            },
            {
                "audience": "maintainers",
                "path": "docs/THIRD_PARTY_EVIDENCE.md",
                "purpose": "Rules for verifying external adoption evidence without overstating claims.",
            },
        ],
        "citation": {
            "path": "CITATION.cff",
            "preferred_name": "The Marked Bench",
            "required_fields": ["release_tag", "suite_id", "suite_version", "suite_hash", "result_card_path"],
        },
    }


def write_adoption_packet(path: str | Path = DEFAULT_ADOPTION_PACKET, root: str | Path = ".") -> None:
    """Write the adoption packet as stable, sorted JSON."""

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(build_adoption_packet(root=root), indent=2, sort_keys=True),
        encoding="utf-8",
    )


def load_adoption_packet(path: str | Path) -> dict[str, Any]:
    """Load an adoption packet JSON file."""

    data = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError("adoption packet must be a JSON object")
    return data


def validate_adoption_packet(packet: Mapping[str, Any], root: str | Path = ".") -> dict[str, Any]:
    """Validate an adoption packet against the current release evidence."""

    root_path = Path(root)
    errors: list[str] = []
    warnings: list[str] = []

    schema_path = root_path / "schemas" / "adoption_packet.schema.json"
    if schema_path.exists():
        schema = load_json_schema(schema_path)
        errors.extend(validate_json_schema(packet, schema, schema_path=schema_path))
    else:
        errors.append(f"{schema_path}: adoption packet schema is missing")

    expected = build_adoption_packet(root_path)
    if dict(packet) != expected:
        errors.append("adoption packet does not match current benchmark release evidence")

    for path in _referenced_paths(packet):
        if not (root_path / path).exists():
            errors.append(f"{path}: referenced adoption packet path is missing")

    summary = {
        "release_id": packet.get("release_id", ""),
        "default_track": packet.get("default_track", ""),
        "track_count": len(packet.get("tracks", [])) if isinstance(packet.get("tracks"), list) else 0,
        "required_artifact_count": (
            len(packet.get("required_public_artifacts", []))
            if isinstance(packet.get("required_public_artifacts"), list)
            else 0
        ),
        "validation_command_count": (
            len(packet.get("validation_commands", []))
            if isinstance(packet.get("validation_commands"), list)
            else 0
        ),
    }
    return {
        "valid": not errors,
        "schema": packet.get("schema", ""),
        "summary": summary,
        "errors": errors,
        "warnings": warnings,
    }


def _artifact(name: str, path: str, purpose: str) -> dict[str, str]:
    return {"name": name, "path": path, "purpose": purpose}


def _referenced_paths(packet: Mapping[str, Any]) -> list[Path]:
    paths = [
        Path(str(packet.get("release_manifest_path", ""))),
        Path(str(packet.get("conformance_report_path", ""))),
    ]
    for key in ["required_public_artifacts", "submission_channels", "announcement_assets"]:
        items = packet.get(key, [])
        if not isinstance(items, list):
            continue
        for item in items:
            if isinstance(item, Mapping) and item.get("path"):
                paths.append(Path(str(item["path"])))
    citation = packet.get("citation", {})
    if isinstance(citation, Mapping) and citation.get("path"):
        paths.append(Path(str(citation["path"])))
    return sorted({path for path in paths if path.as_posix() not in {"", "."}})


__all__ = [
    "ADOPTION_PACKET_SCHEMA",
    "DEFAULT_ADOPTION_PACKET",
    "build_adoption_packet",
    "load_adoption_packet",
    "validate_adoption_packet",
    "write_adoption_packet",
]
