from __future__ import annotations

"""Release manifest generation for public benchmark artifacts."""

import hashlib
import json
from pathlib import Path
from typing import Any, Iterable

from marked_bench.benchmark_registry import REGISTRY_SCHEMA, build_benchmark_registry


RELEASE_MANIFEST_SCHEMA = "marked_bench.benchmark-release-manifest.v1"
RELEASE_ID = "marked-bench-contradiction-standard-release-0.3.9"

ROOT_PUBLIC_ARTIFACTS = (
    "README.md",
    "CONTRIBUTING.md",
    "CITATION.cff",
    "LICENSE",
    "benchmark_registry.json",
)

BENCHMARK_SOURCE_ARTIFACTS = (
    "setup.py",
    "marked_bench/benchmark_adoption.py",
    "marked_bench/benchmark_conformance.py",
    "marked_bench/benchmark_cli.py",
    "marked_bench/benchmark_leaderboard.py",
    "marked_bench/benchmark_registry.py",
    "marked_bench/benchmark_release.py",
    "marked_bench/benchmark_review.py",
    "marked_bench/benchmark_result_card.py",
    "marked_bench/benchmark_submission.py",
    "marked_bench/benchmark_technical_note.py",
    "marked_bench/schema_validation.py",
    "marked_bench/contradiction/__init__.py",
    "marked_bench/contradiction/benchmark_suite.py",
    "marked_bench/contradiction/engine.py",
    "marked_bench/examples/external_submission_demo.py",
    "marked_bench/examples/benchmark_standard_demo.py",
    "scripts/validate_benchmark_artifacts.py",
    "tests/test_benchmark_suite.py",
)

SUPPORT_ARTIFACTS = (
    "adoption/README.md",
    "baselines/README.md",
    "conformance/README.md",
    "leaderboard/README.md",
    "releases/README.md",
    "submissions/README.md",
    ".github/PULL_REQUEST_TEMPLATE.md",
    ".github/workflows/benchmark-ci.yml",
    ".github/ISSUE_TEMPLATE/benchmark_case.yml",
    ".github/ISSUE_TEMPLATE/config.yml",
    ".github/ISSUE_TEMPLATE/leaderboard_submission.yml",
)

SUBMISSION_EXAMPLE_ARTIFACTS = (
    "submissions/example_external_jsonl/predictions.jsonl",
    "submissions/example_external_jsonl/example_external_report.json",
    "submissions/example_external_jsonl/example_external_submission.json",
    "submissions/example_external_jsonl/example_external_submission_bundle.json",
    "submissions/example_external_jsonl/example_external_submission_review.json",
    "submissions/example_external_jsonl/example_external_result_card.json",
)

CONFORMANCE_ARTIFACTS = (
    "conformance/marked_bench_conformance_v0_3_9.json",
)

ADOPTION_ARTIFACTS = (
    "adoption/marked_bench_adoption_packet_v0_3_9.json",
)


def build_release_manifest(root: str | Path = ".") -> dict[str, Any]:
    """Build a deterministic manifest for public benchmark release artifacts."""

    root_path = Path(root)
    registry = build_benchmark_registry()
    artifacts = _collect_artifacts(registry)
    entries = [_artifact_entry(root_path, path, category) for path, category in artifacts]
    entries.sort(key=lambda entry: entry["path"])
    return {
        "schema": RELEASE_MANIFEST_SCHEMA,
        "release_id": RELEASE_ID,
        "project": registry["project"],
        "benchmark_family": registry["benchmark_family"],
        "registry_schema": REGISTRY_SCHEMA,
        "registry_path": "benchmark_registry.json",
        "registry_sha256": file_sha256(root_path / "benchmark_registry.json"),
        "default_track": registry["default_track"],
        "tracks": [
            {
                "name": track["name"],
                "suite_id": track["suite_id"],
                "suite_version": track["suite_version"],
                "suite_hash": track["suite_hash"],
            }
            for track in registry["tracks"]
        ],
        "artifact_count": len(entries),
        "artifacts": entries,
    }


def write_release_manifest(path: str | Path, root: str | Path = ".") -> None:
    """Write the release manifest as stable, sorted JSON."""

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(build_release_manifest(root=root), indent=2, sort_keys=True),
        encoding="utf-8",
    )


def file_sha256(path: str | Path) -> str:
    """Return a cross-platform SHA-256 digest for a public artifact."""

    digest = hashlib.sha256()
    digest.update(canonical_file_bytes(path))
    return digest.hexdigest()


def canonical_file_bytes(path: str | Path) -> bytes:
    """Return bytes with text newlines normalized for reproducible manifests."""

    data = Path(path).read_bytes()
    if b"\0" in data:
        return data
    return data.replace(b"\r\n", b"\n")


def _collect_artifacts(registry: dict[str, Any]) -> list[tuple[str, str]]:
    artifacts: list[tuple[str, str]] = []
    artifacts.extend((path, "root") for path in ROOT_PUBLIC_ARTIFACTS)
    artifacts.extend((path, "source") for path in BENCHMARK_SOURCE_ARTIFACTS)
    artifacts.extend((path, "support") for path in SUPPORT_ARTIFACTS)
    artifacts.extend((path, "conformance") for path in CONFORMANCE_ARTIFACTS)
    artifacts.extend((path, "adoption") for path in ADOPTION_ARTIFACTS)
    artifacts.extend((path, "submission-example") for path in SUBMISSION_EXAMPLE_ARTIFACTS)
    artifacts.extend((path, "schema") for path in registry["schemas"].values())
    artifacts.extend((path, "governance") for path in registry["governance_docs"])

    for track in registry["tracks"]:
        artifacts.append((track["suite_manifest"], f"track:{track['name']}:suite"))
        artifacts.append((track["leaderboard"], f"track:{track['name']}:leaderboard"))
        artifacts.extend((path, f"track:{track['name']}:baseline") for path in track["baseline_reports"])

    return _dedupe_artifacts(artifacts)


def _dedupe_artifacts(artifacts: Iterable[tuple[str, str]]) -> list[tuple[str, str]]:
    deduped: dict[str, str] = {}
    for path, category in artifacts:
        normalized = Path(path).as_posix()
        deduped.setdefault(normalized, category)
    return list(deduped.items())


def _artifact_entry(root: Path, path: str, category: str) -> dict[str, Any]:
    artifact_path = root / path
    if not artifact_path.exists():
        raise FileNotFoundError(f"release artifact is missing: {path}")
    return {
        "path": Path(path).as_posix(),
        "category": category,
        "sha256": file_sha256(artifact_path),
        "bytes": len(canonical_file_bytes(artifact_path)),
    }


__all__ = [
    "RELEASE_ID",
    "RELEASE_MANIFEST_SCHEMA",
    "build_release_manifest",
    "canonical_file_bytes",
    "file_sha256",
    "write_release_manifest",
]
