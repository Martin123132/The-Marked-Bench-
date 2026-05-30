from __future__ import annotations

"""Build validated benchmark leaderboards from report files."""

import hashlib
import json
import time
from pathlib import Path
from typing import Any, Iterable

from marked_bench.contradiction.benchmark_suite import load_benchmark_report, validate_benchmark_report


LEADERBOARD_SCHEMA = "marked_bench.benchmark-leaderboard.v1"


def build_leaderboard(report_paths: Iterable[str | Path]) -> dict[str, Any]:
    """Build a sorted leaderboard from validated benchmark reports."""

    entries = []
    rejected = []
    for raw_path in report_paths:
        path = Path(raw_path)
        report = load_benchmark_report(path)
        validation = validate_benchmark_report(report)
        if not validation["valid"]:
            rejected.append(
                {
                    "report_path": str(path),
                    "errors": validation["errors"],
                    "warnings": validation["warnings"],
                }
            )
            continue
        entries.append(_entry_from_report(path, report, validation))

    entries.sort(
        key=lambda entry: (
            -float(entry["overall_score"]),
            int(entry["failure_count"]),
            str(entry["system_name"]).lower(),
        )
    )
    for rank, entry in enumerate(entries, start=1):
        entry["rank"] = rank

    return {
        "schema": LEADERBOARD_SCHEMA,
        "created_at": round(time.time(), 3),
        "entry_count": len(entries),
        "rejected_count": len(rejected),
        "entries": entries,
        "rejected": rejected,
    }


def write_leaderboard(leaderboard: dict[str, Any], path: str | Path) -> None:
    """Write a leaderboard JSON file."""

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(leaderboard, indent=2, sort_keys=True), encoding="utf-8")


def report_sha256(path: str | Path) -> str:
    """Return a cross-platform SHA-256 digest for a report file."""

    digest = hashlib.sha256()
    digest.update(_canonical_file_bytes(path))
    return digest.hexdigest()


def _canonical_file_bytes(path: str | Path) -> bytes:
    data = Path(path).read_bytes()
    if b"\0" in data:
        return data
    return data.replace(b"\r\n", b"\n")


def _entry_from_report(path: Path, report: dict[str, Any], validation: dict[str, Any]) -> dict[str, Any]:
    metrics = report["metrics"]
    return {
        "rank": None,
        "system_name": report["system_name"],
        "suite_id": report["suite_id"],
        "suite_version": report["suite_version"],
        "suite_hash": report["suite_hash"],
        "report_schema": report["schema"],
        "report_path": path.as_posix(),
        "report_sha256": report_sha256(path),
        "overall_score": report["overall_score"],
        "case_count": report["case_count"],
        "failure_count": validation["summary"]["failure_count"],
        "type_accuracy": metrics["type_accuracy"],
        "contradiction_macro_f1": metrics["contradiction_macro_f1"],
        "detection_f1": metrics["detection"]["f1"],
        "calibration_brier_score": metrics["calibration"]["brier_score"],
        "calibration_ece": metrics["calibration"]["expected_calibration_error"],
        "coverage_index": metrics["coverage_index"],
        "validation_warnings": validation["warnings"],
    }


__all__ = [
    "LEADERBOARD_SCHEMA",
    "build_leaderboard",
    "report_sha256",
    "write_leaderboard",
]
