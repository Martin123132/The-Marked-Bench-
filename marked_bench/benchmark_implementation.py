from __future__ import annotations

"""Implementation kit metadata for external benchmark adopters."""

import json
from pathlib import Path
from typing import Any, Mapping

from marked_bench.benchmark_registry import build_benchmark_registry
from marked_bench.benchmark_release import RELEASE_ID
from marked_bench.schema_validation import load_json_schema, validate_json_schema


IMPLEMENTATION_KIT_SCHEMA = "marked_bench.implementation-kit.v1"
IMPLEMENTATION_KIT_VALIDATION_SCHEMA = "marked_bench.implementation-kit-validation.v1"
DEFAULT_IMPLEMENTATION_KIT = Path("adoption/marked_bench_implementation_kit_v0_4_6.json")
REPOSITORY_URL = "https://github.com/Martin123132/The-Marked-Bench-"
RELEASE_URL = "https://github.com/Martin123132/The-Marked-Bench-/releases/tag/v0.4.6"


def build_implementation_kit(root: str | Path = ".") -> dict[str, Any]:
    """Build the external implementation kit descriptor."""

    del root
    registry = build_benchmark_registry()
    return {
        "schema": IMPLEMENTATION_KIT_SCHEMA,
        "project": registry["project"],
        "benchmark_family": registry["benchmark_family"],
        "release_id": RELEASE_ID,
        "repository_url": REPOSITORY_URL,
        "release_url": RELEASE_URL,
        "purpose": "Help external teams run, validate, cite, and submit Marked Bench results in their own repositories.",
        "release_artifacts": {
            "registry": "benchmark_registry.json",
            "release_manifest": "releases/marked_bench_release_v0_4_6.json",
            "conformance_report": "conformance/marked_bench_conformance_v0_4_6.json",
            "standard_profile": "standard/marked_bench_standard_profile_v0_4_6.json",
            "scoring_compatibility": "standard/marked_bench_scoring_compatibility_v0_4_6.json",
            "scoring_spec": "standard/marked_bench_scoring_spec_v0_4_6.json",
            "adoption_packet": "adoption/marked_bench_adoption_packet_v0_4_6.json",
            "third_party_evidence_ledger": "adoption/third_party_evidence_ledger_v0_4_6.json",
            "implementation_kit": DEFAULT_IMPLEMENTATION_KIT.as_posix(),
        },
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
        "public_schemas": {
            "publication_packet": "schemas/publication_packet.schema.json",
            "result_claim": "schemas/result_claim.schema.json",
            "implementation_kit": "schemas/implementation_kit.schema.json",
            "standard_profile": "schemas/standard_profile.schema.json",
            "scoring_compatibility": "schemas/scoring_compatibility.schema.json",
            "scoring_spec": "schemas/scoring_spec.schema.json",
        },
        "kit_files": [
            _kit_file(
                "guide",
                "adoption/implementation_kit/README.md",
                "Human workflow for using the external implementation kit.",
            ),
            _kit_file(
                "github_actions_template",
                "adoption/implementation_kit/github_actions_validate_result.yml",
                "Copyable CI workflow for validating publication packets and result claims.",
            ),
            _kit_file(
                "result_claim_badge_template",
                "adoption/implementation_kit/result_claim_badge.md",
                "Markdown badge and citation snippet template for public result claims.",
            ),
        ],
        "required_local_artifacts": [
            _artifact("publication_packet", "marked-bench-result/publication_packet.json"),
            _artifact("result_claim", "marked-bench-result/result_claim.json"),
        ],
        "external_ci_commands": [
            _command("install", "python -m pip install git+https://github.com/Martin123132/The-Marked-Bench-.git@v0.4.6"),
            _command(
                "validate_publication_packet",
                "marked-bench --validate-publication-packet marked-bench-result/publication_packet.json",
            ),
            _command("validate_result_claim", "marked-bench --validate-result-claim marked-bench-result/result_claim.json"),
        ],
        "release_validation_commands": [
            _command(
                "release_conformance",
                "marked-bench --validate-conformance-report conformance/marked_bench_conformance_v0_4_6.json",
            ),
            _command(
                "adoption_packet",
                "marked-bench --validate-adoption-packet adoption/marked_bench_adoption_packet_v0_4_6.json",
            ),
            _command(
                "evidence_ledger",
                "marked-bench --validate-evidence-ledger adoption/third_party_evidence_ledger_v0_4_6.json",
            ),
            _command(
                "implementation_kit",
                "marked-bench --validate-implementation-kit adoption/marked_bench_implementation_kit_v0_4_6.json",
            ),
            _command(
                "standard_profile",
                "marked-bench --validate-standard-profile standard/marked_bench_standard_profile_v0_4_6.json",
            ),
            _command(
                "scoring_compatibility",
                "marked-bench --validate-scoring-compatibility standard/marked_bench_scoring_compatibility_v0_4_6.json",
            ),
            _command(
                "scoring_spec",
                "marked-bench --validate-scoring-spec standard/marked_bench_scoring_spec_v0_4_6.json",
            ),
        ],
        "submission_requirements": {
            "publication_packet_required": True,
            "result_claim_required": True,
            "same_suite_hash_required": True,
            "public_url_or_committed_path_required": True,
            "third_party_evidence_requires_review": True,
            "not_safety_certification": True,
        },
        "version_pinning": {
            "release_tag": "v0.4.6",
            "install_reference": "git+https://github.com/Martin123132/The-Marked-Bench-.git@v0.4.6",
            "compare_only_same_suite_hash": True,
        },
    }


def write_implementation_kit(path: str | Path = DEFAULT_IMPLEMENTATION_KIT, root: str | Path = ".") -> None:
    """Write the implementation kit descriptor."""

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(build_implementation_kit(root=root), indent=2, sort_keys=True),
        encoding="utf-8",
    )


def load_implementation_kit(path: str | Path) -> dict[str, Any]:
    """Load an implementation kit descriptor."""

    data = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError("implementation kit must be a JSON object")
    return data


def validate_implementation_kit(kit: Mapping[str, Any], root: str | Path = ".") -> dict[str, Any]:
    """Validate the implementation kit against the current release."""

    root_path = Path(root)
    errors: list[str] = []
    warnings: list[str] = []

    schema_path = root_path / "schemas" / "implementation_kit.schema.json"
    if schema_path.exists():
        schema = load_json_schema(schema_path)
        errors.extend(validate_json_schema(kit, schema, schema_path=schema_path))
    else:
        errors.append(f"{schema_path}: implementation kit schema is missing")

    expected = build_implementation_kit(root_path)
    if dict(kit) != expected:
        errors.append("implementation kit does not match current benchmark release evidence")

    for path in _referenced_paths(kit):
        if not (root_path / path).exists():
            errors.append(f"{path}: referenced implementation kit path is missing")

    summary = {
        "release_id": kit.get("release_id", ""),
        "kit_file_count": len(kit.get("kit_files", [])) if isinstance(kit.get("kit_files"), list) else 0,
        "external_ci_command_count": (
            len(kit.get("external_ci_commands", [])) if isinstance(kit.get("external_ci_commands"), list) else 0
        ),
    }
    return {
        "schema": IMPLEMENTATION_KIT_VALIDATION_SCHEMA,
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
        "summary": summary,
    }


def _kit_file(name: str, path: str, purpose: str) -> dict[str, str]:
    return {"name": name, "path": path, "purpose": purpose}


def _artifact(name: str, path: str) -> dict[str, str]:
    return {"name": name, "path": path}


def _command(name: str, command: str) -> dict[str, str]:
    return {"name": name, "command": command}


def _referenced_paths(kit: Mapping[str, Any]) -> list[Path]:
    paths: list[Path] = []
    release_artifacts = kit.get("release_artifacts", {})
    if isinstance(release_artifacts, Mapping):
        for path in release_artifacts.values():
            paths.append(Path(str(path)))
    public_schemas = kit.get("public_schemas", {})
    if isinstance(public_schemas, Mapping):
        for path in public_schemas.values():
            paths.append(Path(str(path)))
    for key in ["kit_files"]:
        items = kit.get(key, [])
        if not isinstance(items, list):
            continue
        for item in items:
            if isinstance(item, Mapping) and item.get("path"):
                paths.append(Path(str(item["path"])))
    return sorted({path for path in paths if path.as_posix() not in {"", "."}})


__all__ = [
    "DEFAULT_IMPLEMENTATION_KIT",
    "IMPLEMENTATION_KIT_SCHEMA",
    "IMPLEMENTATION_KIT_VALIDATION_SCHEMA",
    "build_implementation_kit",
    "load_implementation_kit",
    "validate_implementation_kit",
    "write_implementation_kit",
]
