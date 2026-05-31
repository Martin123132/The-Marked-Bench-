from __future__ import annotations

"""Machine-readable standard profile for benchmark releases."""

import json
from pathlib import Path
from typing import Any, Mapping

from marked_bench.benchmark_registry import build_benchmark_registry
from marked_bench.benchmark_release import RELEASE_ID
from marked_bench.schema_validation import load_json_schema, validate_json_schema


STANDARD_PROFILE_SCHEMA = "marked_bench.standard-profile.v1"
STANDARD_PROFILE_VALIDATION_SCHEMA = "marked_bench.standard-profile-validation.v1"
DEFAULT_STANDARD_PROFILE = Path("standard/marked_bench_standard_profile_v0_4_8.json")
DEFAULT_CHANGE_CONTROL = Path("standard/marked_bench_change_control_v0_4_8.json")
REPOSITORY_URL = "https://github.com/Martin123132/The-Marked-Bench-"
RELEASE_URL = "https://github.com/Martin123132/The-Marked-Bench-/releases/tag/v0.4.8"


def build_standard_profile(root: str | Path = ".") -> dict[str, Any]:
    """Build the public benchmark-standard profile descriptor."""

    del root
    registry = build_benchmark_registry()
    requirements = _standard_requirements()
    return {
        "schema": STANDARD_PROFILE_SCHEMA,
        "project": registry["project"],
        "benchmark_family": registry["benchmark_family"],
        "standardization_status": "public-standard-candidate",
        "release_id": RELEASE_ID,
        "repository_url": REPOSITORY_URL,
        "release_url": RELEASE_URL,
        "default_track": registry["default_track"],
        "tracks": [
            {
                "name": track["name"],
                "suite_id": track["suite_id"],
                "suite_version": track["suite_version"],
                "suite_hash": track["suite_hash"],
                "case_count": track["case_count"],
            }
            for track in registry["tracks"]
        ],
        "release_artifacts": {
            "registry": "benchmark_registry.json",
            "release_manifest": "releases/marked_bench_release_v0_4_8.json",
            "conformance_report": "conformance/marked_bench_conformance_v0_4_8.json",
            "standard_profile": DEFAULT_STANDARD_PROFILE.as_posix(),
            "change_control": DEFAULT_CHANGE_CONTROL.as_posix(),
            "scoring_compatibility": "standard/marked_bench_scoring_compatibility_v0_4_8.json",
            "scoring_spec": "standard/marked_bench_scoring_spec_v0_4_8.json",
            "adoption_packet": "adoption/marked_bench_adoption_packet_v0_4_8.json",
            "third_party_evidence_ledger": "adoption/third_party_evidence_ledger_v0_4_8.json",
            "implementation_kit": "adoption/marked_bench_implementation_kit_v0_4_8.json",
        },
        "standard_requirements": requirements,
        "requirement_summary": {
            "total": len(requirements),
            "satisfied": sum(1 for requirement in requirements if requirement["status"] == "satisfied"),
            "unsatisfied": sum(1 for requirement in requirements if requirement["status"] != "satisfied"),
        },
        "minimum_external_result_evidence": [
            "validated benchmark report",
            "leaderboard submission metadata",
            "submission bundle",
            "submission review for ranked entries",
            "result card for cited or ranked results",
            "publication packet for self-contained public result evidence",
            "result claim for short score statements",
            "suite_id, suite_version, and suite_hash",
        ],
        "comparability_rules": {
            "compare_only_same_suite_id": True,
            "compare_only_same_suite_version": True,
            "compare_only_same_suite_hash": True,
            "suite_hash_mismatch_invalidates_direct_comparison": True,
        },
        "claim_boundaries": {
            "not_safety_certification": True,
            "not_general_intelligence_claim": True,
            "not_third_party_adoption_without_verified_evidence": True,
            "public_suite_can_be_overfit": True,
        },
        "validation_commands": [
            _command("artifact_gate", "python scripts/validate_benchmark_artifacts.py"),
            _command("unit_tests", "python -m unittest discover -s tests"),
            _command(
                "conformance_report",
                "marked-bench --validate-conformance-report conformance/marked_bench_conformance_v0_4_8.json",
            ),
            _command(
                "standard_profile",
                "marked-bench --validate-standard-profile standard/marked_bench_standard_profile_v0_4_8.json",
            ),
            _command(
                "change_control",
                "marked-bench --validate-change-control standard/marked_bench_change_control_v0_4_8.json",
            ),
            _command(
                "adoption_packet",
                "marked-bench --validate-adoption-packet adoption/marked_bench_adoption_packet_v0_4_8.json",
            ),
            _command(
                "implementation_kit",
                "marked-bench --validate-implementation-kit adoption/marked_bench_implementation_kit_v0_4_8.json",
            ),
            _command(
                "scoring_compatibility",
                "marked-bench --validate-scoring-compatibility standard/marked_bench_scoring_compatibility_v0_4_8.json",
            ),
            _command(
                "scoring_spec",
                "marked-bench --validate-scoring-spec standard/marked_bench_scoring_spec_v0_4_8.json",
            ),
        ],
    }


def write_standard_profile(path: str | Path = DEFAULT_STANDARD_PROFILE, root: str | Path = ".") -> None:
    """Write the standard profile descriptor."""

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(build_standard_profile(root=root), indent=2, sort_keys=True),
        encoding="utf-8",
    )


def load_standard_profile(path: str | Path) -> dict[str, Any]:
    """Load a standard profile descriptor."""

    data = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError("standard profile must be a JSON object")
    return data


def validate_standard_profile(profile: Mapping[str, Any], root: str | Path = ".") -> dict[str, Any]:
    """Validate a standard profile against the current release evidence."""

    root_path = Path(root)
    errors: list[str] = []
    warnings: list[str] = []

    schema_path = root_path / "schemas" / "standard_profile.schema.json"
    if schema_path.exists():
        schema = load_json_schema(schema_path)
        errors.extend(validate_json_schema(profile, schema, schema_path=schema_path))
    else:
        errors.append(f"{schema_path}: standard profile schema is missing")

    expected = build_standard_profile(root_path)
    if dict(profile) != expected:
        errors.append("standard profile does not match current benchmark release evidence")

    requirements = profile.get("standard_requirements", [])
    if isinstance(requirements, list):
        for requirement in requirements:
            if isinstance(requirement, Mapping) and requirement.get("status") != "satisfied":
                errors.append(f"{requirement.get('id', '<unknown>')}: standard requirement is not satisfied")
    else:
        errors.append("standard_requirements must be a list")

    for path in _referenced_paths(profile):
        if not (root_path / path).exists():
            errors.append(f"{path}: referenced standard profile path is missing")

    summary = {
        "release_id": profile.get("release_id", ""),
        "standardization_status": profile.get("standardization_status", ""),
        "requirement_count": len(requirements) if isinstance(requirements, list) else 0,
        "satisfied_requirement_count": (
            sum(1 for requirement in requirements if isinstance(requirement, Mapping) and requirement.get("status") == "satisfied")
            if isinstance(requirements, list)
            else 0
        ),
    }
    return {
        "schema": STANDARD_PROFILE_VALIDATION_SCHEMA,
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
        "summary": summary,
    }


def _standard_requirements() -> list[dict[str, Any]]:
    return [
        _requirement(
            "stable_suite_identity",
            "Every public track has a stable suite ID, version, hash, and manifest.",
            ["benchmark_registry.json", "suites/marked_bench_contradiction_multihop_v0_3_0.json"],
            ["marked-bench --export-registry benchmark_registry.json"],
        ),
        _requirement(
            "public_json_schemas",
            "Public artifacts have checked JSON schemas.",
            ["schemas/benchmark_registry.schema.json", "schemas/contradiction_benchmark_report.schema.json"],
            ["python scripts/validate_benchmark_artifacts.py"],
        ),
        _requirement(
            "validated_reports",
            "Benchmark reports can be validated before publication.",
            ["schemas/contradiction_benchmark_report.schema.json", "baselines/contradiction_engine_multihop_v0_3_0.json"],
            ["marked-bench --validate-report REPORT"],
        ),
        _requirement(
            "baseline_and_leaderboard_evidence",
            "Baseline reports and leaderboard snapshots are checked against each other.",
            ["baselines/contradiction_engine_multihop_v0_3_0.json", "leaderboard/leaderboard_multihop_v0_3_0.json"],
            ["python scripts/validate_benchmark_artifacts.py"],
        ),
        _requirement(
            "external_prediction_scoring",
            "Non-Python systems can export templates and score JSON or JSONL predictions.",
            ["README.md", "schemas/contradiction_predictions.schema.json"],
            ["marked-bench --suite contradiction-multihop --score-predictions PREDICTIONS --report REPORT"],
        ),
        _requirement(
            "submission_bundle_review",
            "External results have submission metadata, bundle evidence, and a review rubric.",
            [
                "schemas/submission_bundle.schema.json",
                "docs/SUBMISSION_REVIEW_RUBRIC.md",
                "submissions/example_external_jsonl/example_external_submission_bundle.json",
            ],
            ["marked-bench --validate-submission-bundle BUNDLE", "marked-bench --validate-submission-review REVIEW"],
        ),
        _requirement(
            "result_card_publication",
            "Cited or ranked results have result cards tied to reports, bundles, reviews, and hashes.",
            ["schemas/result_card.schema.json", "submissions/example_external_jsonl/example_external_result_card.json"],
            ["marked-bench --validate-result-card CARD"],
        ),
        _requirement(
            "publication_packet",
            "Public result folders can be self-contained and hash-checked.",
            ["schemas/publication_packet.schema.json", "submissions/example_publication_packet/publication_packet.json"],
            ["marked-bench --validate-publication-packet PACKET"],
        ),
        _requirement(
            "result_claim_boundaries",
            "Short score statements are hash-pinned and carry explicit overclaim boundaries.",
            ["schemas/result_claim.schema.json", "submissions/example_publication_packet/result_claim.json"],
            ["marked-bench --validate-result-claim CLAIM"],
        ),
        _requirement(
            "release_manifest_hashing",
            "Release files are pinned by path, bytes, and SHA-256 digest.",
            ["releases/marked_bench_release_v0_4_8.json", "schemas/release_manifest.schema.json"],
            ["marked-bench --export-release-manifest releases/marked_bench_release_v0_4_8.json"],
        ),
        _requirement(
            "release_conformance",
            "A single conformance report validates the full release package.",
            ["conformance/marked_bench_conformance_v0_4_8.json", "schemas/conformance_report.schema.json"],
            ["marked-bench --validate-conformance-report conformance/marked_bench_conformance_v0_4_8.json"],
        ),
        _requirement(
            "change_control",
            "Standard changes use a checked public proposal, compatibility, versioning, and validation process.",
            [
                "standard/marked_bench_change_control_v0_4_8.json",
                "schemas/change_control.schema.json",
                "docs/CHANGE_CONTROL.md",
                ".github/ISSUE_TEMPLATE/standard_change.yml",
            ],
            ["marked-bench --validate-change-control standard/marked_bench_change_control_v0_4_8.json"],
        ),
        _requirement(
            "adoption_packet",
            "External users have a checked handoff packet for release adoption.",
            ["adoption/marked_bench_adoption_packet_v0_4_8.json", "schemas/adoption_packet.schema.json"],
            ["marked-bench --validate-adoption-packet adoption/marked_bench_adoption_packet_v0_4_8.json"],
        ),
        _requirement(
            "third_party_evidence_gate",
            "Third-party adoption claims require checked public evidence, bundle and review hashes, and verification status.",
            ["adoption/third_party_evidence_ledger_v0_4_8.json", "docs/THIRD_PARTY_EVIDENCE.md"],
            ["marked-bench --validate-evidence-ledger adoption/third_party_evidence_ledger_v0_4_8.json"],
        ),
        _requirement(
            "implementation_kit",
            "External repositories get copy-ready CI validation for public result artifacts.",
            [
                "adoption/marked_bench_implementation_kit_v0_4_8.json",
                "adoption/implementation_kit/github_actions_validate_result.yml",
            ],
            ["marked-bench --validate-implementation-kit adoption/marked_bench_implementation_kit_v0_4_8.json"],
        ),
        _requirement(
            "scoring_compatibility_vectors",
            "External scoring implementations have deterministic prediction vectors and expected summaries.",
            [
                "standard/marked_bench_scoring_compatibility_v0_4_8.json",
                "schemas/scoring_compatibility.schema.json",
            ],
            [
                "marked-bench --validate-scoring-compatibility "
                "standard/marked_bench_scoring_compatibility_v0_4_8.json"
            ],
        ),
        _requirement(
            "scoring_spec",
            "Independent implementations have a language-neutral scoring contract.",
            [
                "standard/marked_bench_scoring_spec_v0_4_8.json",
                "schemas/scoring_spec.schema.json",
                "docs/SCORING_SPEC.md",
            ],
            ["marked-bench --validate-scoring-spec standard/marked_bench_scoring_spec_v0_4_8.json"],
        ),
        _requirement(
            "benchmark_only_scope",
            "The repository scope is benchmark-only and excludes unrelated toolkit material.",
            ["README.md", "docs/BENCHMARK_CARD.md"],
            ["manual benchmark-only scope scan before release"],
        ),
    ]


def _requirement(
    requirement_id: str,
    statement: str,
    evidence_paths: list[str],
    validation_commands: list[str],
) -> dict[str, Any]:
    return {
        "id": requirement_id,
        "statement": statement,
        "status": "satisfied",
        "evidence_paths": evidence_paths,
        "validation_commands": validation_commands,
    }


def _command(name: str, command: str) -> dict[str, str]:
    return {"name": name, "command": command}


def _referenced_paths(profile: Mapping[str, Any]) -> list[Path]:
    paths: list[Path] = []
    release_artifacts = profile.get("release_artifacts", {})
    if isinstance(release_artifacts, Mapping):
        for path in release_artifacts.values():
            paths.append(Path(str(path)))
    requirements = profile.get("standard_requirements", [])
    if isinstance(requirements, list):
        for requirement in requirements:
            if not isinstance(requirement, Mapping):
                continue
            evidence_paths = requirement.get("evidence_paths", [])
            if isinstance(evidence_paths, list):
                paths.extend(Path(str(path)) for path in evidence_paths)
    return sorted({path for path in paths if path.as_posix() not in {"", "."}})


__all__ = [
    "DEFAULT_STANDARD_PROFILE",
    "STANDARD_PROFILE_SCHEMA",
    "STANDARD_PROFILE_VALIDATION_SCHEMA",
    "build_standard_profile",
    "load_standard_profile",
    "validate_standard_profile",
    "write_standard_profile",
]
