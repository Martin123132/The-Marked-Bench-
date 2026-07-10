from __future__ import annotations

"""Language-neutral scoring specification for benchmark implementers."""

import json
from pathlib import Path
from typing import Any, Mapping

from marked_bench.benchmark_registry import build_benchmark_registry
from marked_bench.benchmark_release import RELEASE_ID
from marked_bench.contradiction.engine import ContradictionType
from marked_bench.schema_validation import load_json_schema, validate_json_schema


SCORING_SPEC_SCHEMA = "marked_bench.scoring-spec.v1"
SCORING_SPEC_VALIDATION_SCHEMA = "marked_bench.scoring-spec-validation.v1"
DEFAULT_SCORING_SPEC = Path("standard/marked_bench_scoring_spec_v0_4_9.json")
DEFAULT_SCORING_SPEC_DOC = Path("docs/SCORING_SPEC.md")
REPOSITORY_URL = "https://github.com/Martin123132/The-Marked-Bench-"
RELEASE_URL = "https://github.com/Martin123132/The-Marked-Bench-/releases/tag/v0.4.9"

SCORE_WEIGHTS = {
    "contradiction_macro_f1": 0.45,
    "type_accuracy": 0.25,
    "binary_detection_f1": 0.20,
    "coverage_index": 0.10,
}


def build_scoring_spec(root: str | Path = ".") -> dict[str, Any]:
    """Build the normative scoring specification for external scorers."""

    del root
    registry = build_benchmark_registry()
    labels = [label.value for label in ContradictionType]
    contradiction_labels = [label for label in labels if label != ContradictionType.NONE.value]
    return {
        "schema": SCORING_SPEC_SCHEMA,
        "project": registry["project"],
        "benchmark_family": registry["benchmark_family"],
        "release_id": RELEASE_ID,
        "repository_url": REPOSITORY_URL,
        "release_url": RELEASE_URL,
        "purpose": "Define language-neutral scoring semantics for independent Marked Bench implementations.",
        "default_track": registry["default_track"],
        "labels": labels,
        "contradiction_labels": contradiction_labels,
        "input_contract": {
            "prediction_order_is_ignored": True,
            "all_case_ids_required_once": True,
            "unknown_case_ids_are_invalid": True,
            "missing_case_ids_are_invalid": True,
            "duplicate_case_ids_are_invalid": True,
            "detector_score_range": [0.0, 1.0],
            "detector_score_default": 0.0,
            "detector_score_semantics": "Binary contradiction confidence on [0, 1].",
            "label_aliases": {
                "no_contradiction": "none",
                "non_contradiction": "none",
                "not_contradiction": "none",
                "null": "none",
            },
        },
        "scoring_pipeline": [
            "Normalize predicted labels to lowercase snake_case and apply label aliases.",
            "Validate that each canonical case_id appears exactly once.",
            "For each case, compute type_correct as predicted == expected.",
            "For each case, compute detection_correct from contradiction-vs-none polarity.",
            "Build a full label confusion matrix using expected labels as rows and predicted labels as columns.",
            "Compute per-label precision, recall, f1, and support from the confusion matrix.",
            "Compute binary contradiction detection metrics from none-vs-non-none polarity.",
            "Compute calibration metrics from detector_score and expected contradiction polarity.",
            "Compute slice metrics by domain, difficulty, capability, and tag.",
            "Compute the weighted overall score and failure list.",
        ],
        "metric_definitions": {
            "type_accuracy": "exact_type_correct / case_count",
            "contradiction_type_accuracy": "exact_type_correct_on_non_none_cases / non_none_case_count",
            "per_class_precision": "true_positive / max(true_positive + false_positive, 1)",
            "per_class_recall": "true_positive / max(true_positive + false_negative, 1)",
            "per_class_f1": "2 * precision * recall / max(precision + recall, 1e-9)",
            "contradiction_macro_f1": "mean(per_class_f1 for contradiction labels with support > 0)",
            "binary_detection_precision": "binary_true_positive / max(binary_true_positive + binary_false_positive, 1)",
            "binary_detection_recall": "binary_true_positive / max(binary_true_positive + binary_false_negative, 1)",
            "binary_detection_f1": "2 * precision * recall / max(precision + recall, 1e-9)",
            "coverage_index": "contradiction labels with support > 0 and recall > 0 divided by contradiction label count",
            "calibration_brier_score": "mean((detector_score - expected_binary_contradiction) ** 2)",
            "calibration_ece": "sum(bin_count / total * abs(mean_confidence - empirical_positive_rate)) over 10 bins",
            "overall_score": (
                "round(100 * (0.45 * contradiction_macro_f1 + 0.25 * type_accuracy + "
                "0.20 * binary_detection_f1 + 0.10 * coverage_index), 2)"
            ),
        },
        "rounding_contract": {
            "overall_score_decimals": 2,
            "metric_decimals": 6,
            "calibration_bin_decimals": 6,
            "rounding_function": "round half to even is acceptable when values are represented exactly as JSON numbers.",
        },
        "calibration_contract": {
            "bin_count": 10,
            "bin_interval": "Each bin is [index / 10, (index + 1) / 10); the final bin includes 1.0.",
            "positive_target": "1.0 when expected label is not none, else 0.0.",
        },
        "report_contract": {
            "required_summary_fields": [
                "suite_id",
                "suite_version",
                "suite_hash",
                "case_count",
                "overall_score",
                "metrics",
                "confusion_matrix",
                "failures",
                "case_results",
                "suite_cases",
            ],
            "comparability_key": ["suite_id", "suite_version", "suite_hash"],
            "compare_only_same_suite_hash": True,
        },
        "compatibility_artifacts": {
            "scoring_compatibility_profile": "standard/marked_bench_scoring_compatibility_v0_4_9.json",
            "scoring_compatibility_schema": "schemas/scoring_compatibility.schema.json",
            "validation_command": (
                "marked-bench --validate-scoring-compatibility "
                "standard/marked_bench_scoring_compatibility_v0_4_9.json"
            ),
        },
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
    }


def build_scoring_spec_markdown(root: str | Path = ".") -> str:
    """Build the human-readable scoring spec from the machine-readable spec."""

    spec = build_scoring_spec(root=root)
    lines = [
        "# Scoring Specification",
        "",
        f"Project: {spec['project']}.",
        "",
        (
            "This document is generated from the machine-readable scoring spec. "
            "It is the language-neutral contract for independent scorers."
        ),
        "",
        "## Identity",
        "",
        f"- Release: `{spec['release_id']}`",
        f"- Default track: `{spec['default_track']}`",
        f"- Schema: `{spec['schema']}`",
        "",
        "## Labels",
        "",
    ]
    lines.extend(f"- `{label}`" for label in spec["labels"])
    lines.extend(
        [
            "",
            "## Input Contract",
            "",
        ]
    )
    for key, value in spec["input_contract"].items():
        lines.append(f"- `{key}`: {value}")
    lines.extend(
        [
            "",
            "## Scoring Pipeline",
            "",
        ]
    )
    lines.extend(f"{index}. {step}" for index, step in enumerate(spec["scoring_pipeline"], start=1))
    lines.extend(
        [
            "",
            "## Metric Definitions",
            "",
        ]
    )
    for key, value in spec["metric_definitions"].items():
        lines.append(f"- `{key}`: {value}")
    lines.extend(
        [
            "",
            "## Overall Score Weights",
            "",
        ]
    )
    for key, value in SCORE_WEIGHTS.items():
        lines.append(f"- `{key}`: {value}")
    lines.extend(
        [
            "",
            "## Compatibility",
            "",
            (
                "Independent implementations should validate against "
                "`standard/marked_bench_scoring_compatibility_v0_4_9.json`."
            ),
            "",
            "```bash",
            spec["compatibility_artifacts"]["validation_command"],
            "```",
            "",
            "## Public Tracks",
            "",
            "| Track | Suite ID | Version | Cases | Suite Hash |",
            "| --- | --- | ---: | ---: | --- |",
        ]
    )
    for track in spec["tracks"]:
        lines.append(
            "| {name} | `{suite_id}` | `{suite_version}` | {case_count} | `{suite_hash}` |".format(**track)
        )
    lines.append("")
    return "\n".join(lines)


def write_scoring_spec(path: str | Path = DEFAULT_SCORING_SPEC, root: str | Path = ".") -> None:
    """Write the scoring spec JSON artifact."""

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(build_scoring_spec(root=root), indent=2, sort_keys=True),
        encoding="utf-8",
    )


def write_scoring_spec_markdown(path: str | Path = DEFAULT_SCORING_SPEC_DOC, root: str | Path = ".") -> None:
    """Write the generated scoring spec Markdown document."""

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(build_scoring_spec_markdown(root=root), encoding="utf-8")


def load_scoring_spec(path: str | Path) -> dict[str, Any]:
    """Load a scoring spec JSON artifact."""

    data = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError("scoring spec must be a JSON object")
    return data


def validate_scoring_spec(spec: Mapping[str, Any], root: str | Path = ".") -> dict[str, Any]:
    """Validate a scoring spec against the current release."""

    root_path = Path(root)
    errors: list[str] = []
    warnings: list[str] = []

    schema_path = root_path / "schemas" / "scoring_spec.schema.json"
    if schema_path.exists():
        schema = load_json_schema(schema_path)
        errors.extend(validate_json_schema(spec, schema, schema_path=schema_path))
    else:
        errors.append(f"{schema_path}: scoring spec schema is missing")

    expected = build_scoring_spec(root_path)
    if dict(spec) != expected:
        errors.append("scoring spec does not match current scoring contract")

    for path in _referenced_paths(spec):
        if not (root_path / path).exists():
            errors.append(f"{path}: referenced scoring spec path is missing")

    summary = {
        "release_id": spec.get("release_id", ""),
        "track_count": len(spec.get("tracks", [])) if isinstance(spec.get("tracks"), list) else 0,
        "label_count": len(spec.get("labels", [])) if isinstance(spec.get("labels"), list) else 0,
    }
    return {
        "schema": SCORING_SPEC_VALIDATION_SCHEMA,
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
        "summary": summary,
    }


def _referenced_paths(spec: Mapping[str, Any]) -> list[Path]:
    artifacts = spec.get("compatibility_artifacts", {})
    paths = []
    if isinstance(artifacts, Mapping):
        for key, value in artifacts.items():
            if key.endswith("_profile") or key.endswith("_schema"):
                paths.append(Path(str(value)))
    return sorted({path for path in paths if path.as_posix() not in {"", "."}})


__all__ = [
    "DEFAULT_SCORING_SPEC",
    "DEFAULT_SCORING_SPEC_DOC",
    "SCORING_SPEC_SCHEMA",
    "SCORING_SPEC_VALIDATION_SCHEMA",
    "build_scoring_spec",
    "build_scoring_spec_markdown",
    "load_scoring_spec",
    "validate_scoring_spec",
    "write_scoring_spec",
    "write_scoring_spec_markdown",
]
