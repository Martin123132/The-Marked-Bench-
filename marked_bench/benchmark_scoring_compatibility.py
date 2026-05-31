from __future__ import annotations

"""Scoring compatibility vectors for external benchmark implementations."""

import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from marked_bench.benchmark_registry import build_benchmark_registry
from marked_bench.benchmark_release import RELEASE_ID
from marked_bench.contradiction.benchmark_suite import (
    BenchmarkCase,
    build_suite,
    evaluate_prediction_records,
)
from marked_bench.contradiction.engine import ContradictionType
from marked_bench.schema_validation import load_json_schema, validate_json_schema


SCORING_COMPATIBILITY_SCHEMA = "marked_bench.scoring-compatibility.v1"
SCORING_COMPATIBILITY_VALIDATION_SCHEMA = "marked_bench.scoring-compatibility-validation.v1"
DEFAULT_SCORING_COMPATIBILITY_PROFILE = Path("standard/marked_bench_scoring_compatibility_v0_4_8.json")
REPOSITORY_URL = "https://github.com/Martin123132/The-Marked-Bench-"
RELEASE_URL = "https://github.com/Martin123132/The-Marked-Bench-/releases/tag/v0.4.8"

VECTOR_NAMES = ("perfect", "always_none", "rotated_labels")
LABEL_ROTATION = {
    ContradictionType.DIRECT_NEGATION.value: ContradictionType.PROPERTY_MISMATCH.value,
    ContradictionType.PROPERTY_MISMATCH.value: ContradictionType.DEFINITIONAL_VIOLATION.value,
    ContradictionType.DEFINITIONAL_VIOLATION.value: ContradictionType.UNIVERSAL_COUNTEREXAMPLE.value,
    ContradictionType.UNIVERSAL_COUNTEREXAMPLE.value: ContradictionType.TEMPORAL_CONFLICT.value,
    ContradictionType.TEMPORAL_CONFLICT.value: ContradictionType.NONE.value,
    ContradictionType.NONE.value: ContradictionType.DIRECT_NEGATION.value,
}


def build_scoring_compatibility_profile(root: str | Path = ".") -> dict[str, Any]:
    """Build deterministic scoring compatibility vectors for all public tracks."""

    del root
    registry = build_benchmark_registry()
    vectors = [
        _build_vector(track["name"], vector_name)
        for track in registry["tracks"]
        for vector_name in VECTOR_NAMES
    ]
    return {
        "schema": SCORING_COMPATIBILITY_SCHEMA,
        "project": registry["project"],
        "benchmark_family": registry["benchmark_family"],
        "release_id": RELEASE_ID,
        "repository_url": REPOSITORY_URL,
        "release_url": RELEASE_URL,
        "purpose": "Give external implementations deterministic prediction vectors and expected score summaries.",
        "default_track": registry["default_track"],
        "vector_count": len(vectors),
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
        "scoring_contract": {
            "compare_only_same_suite_hash": True,
            "prediction_order_is_ignored": True,
            "all_case_ids_required_once": True,
            "overall_score_weights": {
                "contradiction_macro_f1": 0.45,
                "type_accuracy": 0.25,
                "binary_detection_f1": 0.20,
                "coverage_index": 0.10,
            },
            "detector_score_semantics": "Binary contradiction confidence on [0, 1].",
        },
        "vectors": vectors,
    }


def write_scoring_compatibility_profile(
    path: str | Path = DEFAULT_SCORING_COMPATIBILITY_PROFILE,
    root: str | Path = ".",
) -> None:
    """Write scoring compatibility vectors as stable JSON."""

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(build_scoring_compatibility_profile(root=root), indent=2, sort_keys=True),
        encoding="utf-8",
    )


def load_scoring_compatibility_profile(path: str | Path) -> dict[str, Any]:
    """Load a scoring compatibility profile."""

    data = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError("scoring compatibility profile must be a JSON object")
    return data


def validate_scoring_compatibility_profile(
    profile: Mapping[str, Any],
    root: str | Path = ".",
) -> dict[str, Any]:
    """Validate scoring compatibility vectors against current scoring code."""

    root_path = Path(root)
    errors: list[str] = []
    warnings: list[str] = []

    schema_path = root_path / "schemas" / "scoring_compatibility.schema.json"
    if schema_path.exists():
        schema = load_json_schema(schema_path)
        errors.extend(validate_json_schema(profile, schema, schema_path=schema_path))
    else:
        errors.append(f"{schema_path}: scoring compatibility schema is missing")

    expected = build_scoring_compatibility_profile(root_path)
    if dict(profile) != expected:
        errors.append("scoring compatibility profile does not match current scoring evidence")

    vectors = profile.get("vectors", [])
    summary = {
        "release_id": profile.get("release_id", ""),
        "vector_count": len(vectors) if isinstance(vectors, list) else 0,
        "track_count": len(profile.get("tracks", [])) if isinstance(profile.get("tracks"), list) else 0,
    }
    return {
        "schema": SCORING_COMPATIBILITY_VALIDATION_SCHEMA,
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
        "summary": summary,
    }


def _build_vector(suite: str, vector_name: str) -> dict[str, Any]:
    cases = build_suite(suite)
    predictions = _prediction_records(cases, vector_name)
    report = evaluate_prediction_records(predictions, system_name=f"compatibility-{vector_name}", suite=suite)
    return {
        "name": vector_name,
        "suite": suite,
        "input_predictions": predictions,
        "expected_summary": _report_summary(report),
    }


def _prediction_records(cases: Sequence[BenchmarkCase], vector_name: str) -> list[dict[str, Any]]:
    if vector_name not in VECTOR_NAMES:
        raise ValueError(f"unknown compatibility vector: {vector_name}")
    records = []
    for case in cases:
        predicted = _predicted_label(case, vector_name)
        records.append(
            {
                "case_id": case.id,
                "predicted": predicted,
                "detector_score": _detector_score(predicted, vector_name),
                "rationale": f"Scoring compatibility vector: {vector_name}.",
                "evidence": [case.id],
            }
        )
    return records


def _predicted_label(case: BenchmarkCase, vector_name: str) -> str:
    expected = case.expected.value
    if vector_name == "perfect":
        return expected
    if vector_name == "always_none":
        return ContradictionType.NONE.value
    if vector_name == "rotated_labels":
        return LABEL_ROTATION[expected]
    raise ValueError(f"unknown compatibility vector: {vector_name}")


def _detector_score(predicted: str, vector_name: str) -> float:
    if vector_name == "rotated_labels":
        return 0.5
    return 0.0 if predicted == ContradictionType.NONE.value else 1.0


def _report_summary(report: Mapping[str, Any]) -> dict[str, Any]:
    metrics = report["metrics"]
    calibration = metrics["calibration"]
    detection = metrics["detection"]
    return {
        "suite_id": report["suite_id"],
        "suite_version": report["suite_version"],
        "suite_hash": report["suite_hash"],
        "case_count": report["case_count"],
        "overall_score": report["overall_score"],
        "type_accuracy": metrics["type_accuracy"],
        "contradiction_macro_f1": metrics["contradiction_macro_f1"],
        "binary_detection_f1": detection["f1"],
        "coverage_index": metrics["coverage_index"],
        "calibration_brier_score": calibration["brier_score"],
        "calibration_ece": calibration["expected_calibration_error"],
        "failure_count": len(report["failures"]),
        "failure_case_ids": [failure["case_id"] for failure in report["failures"]],
        "confusion_matrix": report["confusion_matrix"],
    }


__all__ = [
    "DEFAULT_SCORING_COMPATIBILITY_PROFILE",
    "SCORING_COMPATIBILITY_SCHEMA",
    "SCORING_COMPATIBILITY_VALIDATION_SCHEMA",
    "build_scoring_compatibility_profile",
    "load_scoring_compatibility_profile",
    "validate_scoring_compatibility_profile",
    "write_scoring_compatibility_profile",
]
