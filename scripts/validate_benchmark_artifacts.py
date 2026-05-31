from __future__ import annotations

"""Validate checked-in benchmark manifests, reports, and leaderboards."""

import json
import os
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from marked_bench.benchmark_leaderboard import build_leaderboard  # noqa: E402
from marked_bench.benchmark_release import build_release_manifest  # noqa: E402
from marked_bench.benchmark_registry import build_benchmark_registry  # noqa: E402
from marked_bench.benchmark_technical_note import build_technical_note  # noqa: E402
from marked_bench.contradiction.benchmark_suite import (  # noqa: E402
    build_suite_manifest,
    validate_benchmark_report,
)


SUITE_MANIFESTS = {
    Path("suites/marked_bench_contradiction_standard_v0_1_0.json"): "contradiction",
    Path("suites/marked_bench_contradiction_adversarial_v0_2_0.json"): "contradiction-adversarial",
}

BASELINE_REPORTS = [
    Path("baselines/contradiction_engine_v0_1_0.json"),
    Path("baselines/always_none_v0_1_0.json"),
    Path("baselines/contradiction_engine_adversarial_v0_2_0.json"),
    Path("baselines/always_none_adversarial_v0_2_0.json"),
]

LEADERBOARDS = {
    Path("leaderboard/leaderboard_v0_1_0.json"): [
        Path("baselines/always_none_v0_1_0.json"),
        Path("baselines/contradiction_engine_v0_1_0.json"),
    ],
    Path("leaderboard/leaderboard_adversarial_v0_2_0.json"): [
        Path("baselines/always_none_adversarial_v0_2_0.json"),
        Path("baselines/contradiction_engine_adversarial_v0_2_0.json"),
    ],
}

BENCHMARK_REGISTRY = Path("benchmark_registry.json")
RELEASE_MANIFEST = Path("releases/marked_bench_release_v0_2_0.json")

REQUIRED_PUBLIC_FILES = [
    Path("README.md"),
    BENCHMARK_REGISTRY,
    RELEASE_MANIFEST,
    Path("CONTRIBUTING.md"),
    Path("CITATION.cff"),
    Path("docs/BENCHMARK_CARD.md"),
    Path("docs/ADOPTION_GUIDE.md"),
    Path("docs/BENCHMARK_STANDARD.md"),
    Path("docs/GOVERNANCE.md"),
    Path("docs/RELEASE_CHECKLIST.md"),
    Path("docs/RELEASE_NOTES_v0_2_0.md"),
    Path("docs/ROADMAP.md"),
    Path("docs/SUBMISSION_GUIDE.md"),
    Path("schemas/benchmark_registry.schema.json"),
    Path("schemas/contradiction_benchmark_report.schema.json"),
    Path("schemas/contradiction_predictions.schema.json"),
    Path("schemas/contradiction_suite_manifest.schema.json"),
    Path("schemas/leaderboard.schema.json"),
    Path("schemas/leaderboard_submission.schema.json"),
    Path("schemas/release_manifest.schema.json"),
    Path("releases/README.md"),
    Path("submissions/README.md"),
    Path(".github/PULL_REQUEST_TEMPLATE.md"),
    Path(".github/workflows/benchmark-ci.yml"),
]


def main() -> int:
    previous_cwd = Path.cwd()
    os.chdir(ROOT)
    try:
        errors: list[str] = []
        _validate_required_public_files(errors)
        _validate_benchmark_registry(errors)
        _validate_technical_note(errors)
        _validate_release_manifest(errors)
        _validate_suite_manifests(errors)
        _validate_baseline_reports(errors)
        _validate_leaderboards(errors)
    finally:
        os.chdir(previous_cwd)

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("Benchmark artifacts validated.")
    return 0


def _validate_suite_manifests(errors: list[str]) -> None:
    for path, suite in SUITE_MANIFESTS.items():
        actual = _read_json(path, errors)
        if actual is None:
            continue
        expected = build_suite_manifest(suite=suite)
        if actual != expected:
            errors.append(f"{path}: manifest does not match code-generated suite")


def _validate_required_public_files(errors: list[str]) -> None:
    for path in REQUIRED_PUBLIC_FILES:
        if not path.exists():
            errors.append(f"{path}: required public repo file is missing")


def _validate_benchmark_registry(errors: list[str]) -> None:
    registry = _read_json(BENCHMARK_REGISTRY, errors)
    if registry is None:
        return
    expected = build_benchmark_registry()
    if registry != expected:
        errors.append(f"{BENCHMARK_REGISTRY}: registry does not match code-generated registry")

    for path in registry.get("schemas", {}).values():
        _expect_existing_path(Path(path), errors, BENCHMARK_REGISTRY)
    for path in registry.get("governance_docs", []):
        _expect_existing_path(Path(path), errors, BENCHMARK_REGISTRY)

    tracks = registry.get("tracks", [])
    if not isinstance(tracks, list):
        errors.append(f"{BENCHMARK_REGISTRY}: tracks must be a list")
        return
    for track in tracks:
        if not isinstance(track, dict):
            errors.append(f"{BENCHMARK_REGISTRY}: track entries must be objects")
            continue
        _validate_registry_track(track, errors)


def _validate_registry_track(track: dict[str, Any], errors: list[str]) -> None:
    track_name = track.get("name", "<unknown>")
    manifest_path = Path(str(track.get("suite_manifest", "")))
    leaderboard_path = Path(str(track.get("leaderboard", "")))
    _expect_existing_path(manifest_path, errors, BENCHMARK_REGISTRY)
    _expect_existing_path(leaderboard_path, errors, BENCHMARK_REGISTRY)
    for report_path in track.get("baseline_reports", []):
        _expect_existing_path(Path(str(report_path)), errors, BENCHMARK_REGISTRY)

    manifest = _read_json(manifest_path, errors)
    if manifest is not None:
        for key in ["suite_id", "suite_version", "suite_hash", "case_count", "labels", "profile"]:
            if track.get(key) != manifest.get(key):
                errors.append(f"{BENCHMARK_REGISTRY}: {track_name} {key} does not match suite manifest")

    for report_path in track.get("baseline_reports", []):
        report = _read_json(Path(str(report_path)), errors)
        if report is None:
            continue
        validation = validate_benchmark_report(report)
        if not validation["valid"]:
            errors.append(f"{BENCHMARK_REGISTRY}: {report_path} is not a valid baseline report")
        if (
            report.get("suite_id") != track.get("suite_id")
            or report.get("suite_version") != track.get("suite_version")
            or report.get("suite_hash") != track.get("suite_hash")
        ):
            errors.append(f"{BENCHMARK_REGISTRY}: {report_path} suite metadata does not match {track_name}")

    leaderboard = _read_json(leaderboard_path, errors)
    if leaderboard is not None:
        for entry in leaderboard.get("entries", []):
            if (
                entry.get("suite_id") != track.get("suite_id")
                or entry.get("suite_version") != track.get("suite_version")
                or entry.get("suite_hash") != track.get("suite_hash")
            ):
                errors.append(f"{BENCHMARK_REGISTRY}: leaderboard entry suite metadata does not match {track_name}")


def _validate_technical_note(errors: list[str]) -> None:
    path = Path("docs/TECHNICAL_NOTE.md")
    try:
        actual = path.read_text(encoding="utf-8")
    except OSError as exc:
        errors.append(f"{path}: could not read file: {exc}")
        return
    expected = build_technical_note(ROOT)
    if actual != expected:
        errors.append(f"{path}: technical note does not match generated benchmark evidence")


def _validate_release_manifest(errors: list[str]) -> None:
    manifest = _read_json(RELEASE_MANIFEST, errors)
    if manifest is None:
        return
    try:
        expected = build_release_manifest(ROOT)
    except OSError as exc:
        errors.append(f"{RELEASE_MANIFEST}: could not build expected release manifest: {exc}")
        return
    if manifest != expected:
        errors.append(f"{RELEASE_MANIFEST}: release manifest does not match current public artifacts")


def _validate_baseline_reports(errors: list[str]) -> None:
    for path in BASELINE_REPORTS:
        report = _read_json(path, errors)
        if report is None:
            continue
        validation = validate_benchmark_report(report)
        if not validation["valid"]:
            errors.append(f"{path}: report validation failed: {validation['errors']}")


def _validate_leaderboards(errors: list[str]) -> None:
    for path, reports in LEADERBOARDS.items():
        actual = _read_json(path, errors)
        if actual is None:
            continue
        expected = build_leaderboard(reports)
        for key in ["schema", "entry_count", "rejected_count", "entries", "rejected"]:
            if actual.get(key) != expected.get(key):
                errors.append(f"{path}: {key} does not match validated reports")


def _read_json(path: Path, errors: list[str]) -> Any | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        errors.append(f"{path}: could not read file: {exc}")
    except json.JSONDecodeError as exc:
        errors.append(f"{path}: invalid JSON: {exc}")
    return None


def _expect_existing_path(path: Path, errors: list[str], source: Path) -> None:
    if not path.exists():
        errors.append(f"{source}: referenced path is missing: {path}")


if __name__ == "__main__":
    raise SystemExit(main())
