from __future__ import annotations

"""Machine-readable change-control profile for benchmark standard governance."""

import json
from pathlib import Path
from typing import Any, Mapping

from marked_bench.benchmark_registry import build_benchmark_registry
from marked_bench.benchmark_release import RELEASE_ID
from marked_bench.schema_validation import load_json_schema, validate_json_schema


CHANGE_CONTROL_SCHEMA = "marked_bench.change-control.v1"
CHANGE_CONTROL_VALIDATION_SCHEMA = "marked_bench.change-control-validation.v1"
DEFAULT_CHANGE_CONTROL = Path("standard/marked_bench_change_control_v0_4_8.json")
REPOSITORY_URL = "https://github.com/Martin123132/The-Marked-Bench-"
RELEASE_URL = "https://github.com/Martin123132/The-Marked-Bench-/releases/tag/v0.4.8"


def build_change_control(root: str | Path = ".") -> dict[str, Any]:
    """Build the public change-control profile for benchmark-standard updates."""

    del root
    registry = build_benchmark_registry()
    return {
        "schema": CHANGE_CONTROL_SCHEMA,
        "project": registry["project"],
        "benchmark_family": registry["benchmark_family"],
        "release_id": RELEASE_ID,
        "repository_url": REPOSITORY_URL,
        "release_url": RELEASE_URL,
        "default_track": registry["default_track"],
        "change_types": [
            _change_type(
                "suite_case_change",
                "Adding, correcting, retiring, or relabeling benchmark cases.",
                "new suite version or new track when released case meaning changes",
            ),
            _change_type(
                "new_track",
                "Adding a public benchmark track with its own suite ID, manifest, baselines, and leaderboard.",
                "new suite ID and version",
            ),
            _change_type(
                "schema_change",
                "Changing a public JSON artifact schema or validation contract.",
                "new release tag and documented compatibility note",
            ),
            _change_type(
                "scoring_change",
                "Changing labels, metrics, weights, rounding, calibration, or score interpretation.",
                "new release tag and updated scoring spec plus compatibility vectors",
            ),
            _change_type(
                "evidence_policy_change",
                "Changing result cards, claims, publication packets, or third-party evidence rules.",
                "new release tag and updated standard profile",
            ),
            _change_type(
                "governance_change",
                "Changing release, review, adoption, claim, or change-control process.",
                "new release tag and release notes",
            ),
        ],
        "proposal_requirements": [
            _requirement(
                "public_proposal",
                "A public issue or pull request states the change type, motivation, impacted artifacts, and compatibility impact.",
                [".github/ISSUE_TEMPLATE/standard_change.yml", ".github/PULL_REQUEST_TEMPLATE.md"],
                ["manual proposal review"],
            ),
            _requirement(
                "case_stability",
                "Released case IDs keep their meaning; incompatible case changes require a new suite version or track.",
                ["docs/GOVERNANCE.md", "docs/BENCHMARK_STANDARD.md"],
                ["manual case-stability review"],
            ),
            _requirement(
                "artifact_regeneration",
                "Affected manifests, registry entries, release artifacts, conformance reports, and docs are regenerated.",
                ["scripts/validate_benchmark_artifacts.py", "releases/README.md"],
                ["python scripts/validate_benchmark_artifacts.py"],
            ),
            _requirement(
                "scoring_compatibility",
                "Scoring changes update the scoring specification and deterministic compatibility vectors.",
                [
                    "docs/SCORING_SPEC.md",
                    "standard/marked_bench_scoring_spec_v0_4_8.json",
                    "standard/marked_bench_scoring_compatibility_v0_4_8.json",
                ],
                [
                    "marked-bench --validate-scoring-spec standard/marked_bench_scoring_spec_v0_4_8.json",
                    (
                        "marked-bench --validate-scoring-compatibility "
                        "standard/marked_bench_scoring_compatibility_v0_4_8.json"
                    ),
                ],
            ),
            _requirement(
                "evidence_gate",
                "Evidence-policy changes update adoption, implementation-kit, standard-profile, and evidence-ledger checks.",
                [
                    "adoption/marked_bench_adoption_packet_v0_4_8.json",
                    "adoption/marked_bench_implementation_kit_v0_4_8.json",
                    "standard/marked_bench_standard_profile_v0_4_8.json",
                    "adoption/third_party_evidence_ledger_v0_4_8.json",
                ],
                [
                    "marked-bench --validate-adoption-packet adoption/marked_bench_adoption_packet_v0_4_8.json",
                    (
                        "marked-bench --validate-implementation-kit "
                        "adoption/marked_bench_implementation_kit_v0_4_8.json"
                    ),
                    "marked-bench --validate-evidence-ledger adoption/third_party_evidence_ledger_v0_4_8.json",
                ],
            ),
        ],
        "workflow": [
            _workflow_step(1, "open_public_proposal", "Use the standard-change issue template or a pull request."),
            _workflow_step(2, "classify_change", "Choose the change type and identify affected public artifacts."),
            _workflow_step(3, "state_compatibility", "Declare whether suite hashes, scoring, schemas, or claims change."),
            _workflow_step(4, "update_evidence", "Regenerate checked artifacts and release notes for the new release."),
            _workflow_step(5, "run_gates", "Run artifact validation, tests, conformance, and relevant CLI validators."),
            _workflow_step(6, "publish_release", "Publish a release with the updated manifest and evidence artifacts."),
        ],
        "compatibility_rules": {
            "released_case_meaning_is_immutable": True,
            "suite_hash_change_blocks_direct_comparison": True,
            "schema_change_requires_schema_file_update": True,
            "scoring_change_requires_spec_and_vectors": True,
            "evidence_policy_change_requires_standard_profile_update": True,
            "release_notes_required_for_public_changes": True,
        },
        "decision_rules": {
            "public_review_required": True,
            "maintainer_acceptance_required": True,
            "automated_validation_required": True,
            "rejected_changes_remain_visible": True,
            "private_or_uninspectable_standard_changes_forbidden": True,
        },
        "intake_channels": [
            _channel(
                "standard_change_issue",
                ".github/ISSUE_TEMPLATE/standard_change.yml",
                "Structured intake for proposed standard, schema, scoring, evidence, or governance changes.",
            ),
            _channel(
                "benchmark_case_issue",
                ".github/ISSUE_TEMPLATE/benchmark_case.yml",
                "Structured intake for new cases and case-label disputes.",
            ),
            _channel(
                "pull_request_template",
                ".github/PULL_REQUEST_TEMPLATE.md",
                "Release hygiene and validation checklist for proposed repository changes.",
            ),
        ],
        "validation_commands": [
            _command("change_control", "marked-bench --validate-change-control standard/marked_bench_change_control_v0_4_8.json"),
            _command("artifact_gate", "python scripts/validate_benchmark_artifacts.py"),
            _command("unit_tests", "python -m unittest discover -s tests"),
            _command("conformance", "marked-bench --validate-conformance-report conformance/marked_bench_conformance_v0_4_8.json"),
        ],
    }


def write_change_control(path: str | Path = DEFAULT_CHANGE_CONTROL, root: str | Path = ".") -> None:
    """Write the change-control profile as stable JSON."""

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(build_change_control(root=root), indent=2, sort_keys=True),
        encoding="utf-8",
    )


def load_change_control(path: str | Path) -> dict[str, Any]:
    """Load a change-control profile JSON file."""

    data = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError("change-control profile must be a JSON object")
    return data


def validate_change_control(profile: Mapping[str, Any], root: str | Path = ".") -> dict[str, Any]:
    """Validate a change-control profile against current release evidence."""

    root_path = Path(root)
    errors: list[str] = []
    warnings: list[str] = []

    schema_path = root_path / "schemas" / "change_control.schema.json"
    if schema_path.exists():
        schema = load_json_schema(schema_path)
        errors.extend(validate_json_schema(profile, schema, schema_path=schema_path))
    else:
        errors.append(f"{schema_path}: change-control schema is missing")

    expected = build_change_control(root_path)
    if dict(profile) != expected:
        errors.append("change-control profile does not match current release evidence")

    for path in _referenced_paths(profile):
        if not (root_path / path).exists():
            errors.append(f"{path}: referenced change-control path is missing")

    change_types = profile.get("change_types", [])
    requirements = profile.get("proposal_requirements", [])
    summary = {
        "release_id": profile.get("release_id", ""),
        "change_type_count": len(change_types) if isinstance(change_types, list) else 0,
        "proposal_requirement_count": len(requirements) if isinstance(requirements, list) else 0,
        "intake_channel_count": (
            len(profile.get("intake_channels", [])) if isinstance(profile.get("intake_channels"), list) else 0
        ),
    }
    return {
        "schema": CHANGE_CONTROL_VALIDATION_SCHEMA,
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
        "summary": summary,
    }


def _change_type(change_id: str, scope: str, versioning: str) -> dict[str, Any]:
    return {
        "id": change_id,
        "scope": scope,
        "versioning": versioning,
        "public_proposal_required": True,
        "release_notes_required": True,
        "conformance_update_required": True,
    }


def _requirement(
    requirement_id: str,
    statement: str,
    evidence_paths: list[str],
    validation_commands: list[str],
) -> dict[str, Any]:
    return {
        "id": requirement_id,
        "statement": statement,
        "evidence_paths": evidence_paths,
        "validation_commands": validation_commands,
    }


def _workflow_step(step: int, name: str, description: str) -> dict[str, Any]:
    return {"step": step, "name": name, "description": description}


def _channel(name: str, path: str, purpose: str) -> dict[str, str]:
    return {"name": name, "path": path, "purpose": purpose}


def _command(name: str, command: str) -> dict[str, str]:
    return {"name": name, "command": command}


def _referenced_paths(profile: Mapping[str, Any]) -> list[Path]:
    paths: list[Path] = [Path("schemas/change_control.schema.json"), Path("docs/CHANGE_CONTROL.md")]
    for key in ["proposal_requirements", "intake_channels"]:
        items = profile.get(key, [])
        if not isinstance(items, list):
            continue
        for item in items:
            if not isinstance(item, Mapping):
                continue
            if item.get("path"):
                paths.append(Path(str(item["path"])))
            evidence_paths = item.get("evidence_paths", [])
            if isinstance(evidence_paths, list):
                paths.extend(Path(str(path)) for path in evidence_paths)
    return sorted({path for path in paths if path.as_posix() not in {"", "."}})


__all__ = [
    "CHANGE_CONTROL_SCHEMA",
    "CHANGE_CONTROL_VALIDATION_SCHEMA",
    "DEFAULT_CHANGE_CONTROL",
    "build_change_control",
    "load_change_control",
    "validate_change_control",
    "write_change_control",
]
