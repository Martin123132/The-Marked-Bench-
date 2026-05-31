from __future__ import annotations

"""Generate the public technical note for benchmark releases."""

import json
from pathlib import Path
from typing import Any

from marked_bench.benchmark_registry import build_benchmark_registry


TECHNICAL_NOTE_PATH = "docs/TECHNICAL_NOTE.md"


def build_technical_note(root: str | Path = ".") -> str:
    """Build a Markdown technical note from current public artifacts."""

    root_path = Path(root)
    registry = build_benchmark_registry()
    lines = [
        "# Technical Note",
        "",
        f"Project: {registry['project']}.",
        "",
        (
            "This note summarizes the checked benchmark release artifacts for "
            f"`{registry['benchmark_family']}`. It is generated from the suite "
            "manifests, baseline reports, leaderboards, and benchmark registry."
        ),
        "",
        "## Public Tracks",
        "",
        "| Track | Suite ID | Version | Cases | Suite Hash | Baseline Best |",
        "| --- | --- | ---: | ---: | --- | ---: |",
    ]
    for track in registry["tracks"]:
        leaderboard = _read_json(root_path / track["leaderboard"])
        best_score = leaderboard["entries"][0]["overall_score"] if leaderboard["entries"] else None
        lines.append(
            "| {name} | `{suite_id}` | `{suite_version}` | {case_count} | `{suite_hash}` | {best_score} |".format(
                name=track["name"],
                suite_id=track["suite_id"],
                suite_version=track["suite_version"],
                case_count=track["case_count"],
                suite_hash=track["suite_hash"],
                best_score=_format_score(best_score),
            )
        )

    lines.extend(
        [
            "",
            "## Suite Composition",
            "",
        ]
    )
    for track in registry["tracks"]:
        profile = track["profile"]
        lines.extend(
            [
                f"### {track['name']}",
                "",
                f"- Cases: {profile['case_count']}",
                f"- Contradiction cases: {profile['contradiction_case_count']}",
                f"- Control cases: {profile['control_case_count']}",
                f"- Difficulties: {_format_counts(profile['difficulty_counts'])}",
                f"- Domains: {_format_counts(profile['domain_counts'])}",
                f"- Labels: {_format_counts(profile['label_counts'])}",
                f"- Quality gates: {_format_quality_gates(profile['quality_gates'])}",
                "",
            ]
        )

    lines.extend(
        [
            "## Baseline Evidence",
            "",
            "| Track | System | Overall | Type Acc. | Detection F1 | Brier | ECE | Failures |",
            "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for track in registry["tracks"]:
        leaderboard = _read_json(root_path / track["leaderboard"])
        for entry in leaderboard["entries"]:
            lines.append(
                "| {track} | {system} | {overall} | {type_accuracy} | {detection_f1} | {brier} | {ece} | {failures} |".format(
                    track=track["name"],
                    system=entry["system_name"],
                    overall=_format_score(entry["overall_score"]),
                    type_accuracy=_format_metric(entry["type_accuracy"]),
                    detection_f1=_format_metric(entry["detection_f1"]),
                    brier=_format_metric(entry["calibration_brier_score"]),
                    ece=_format_metric(entry["calibration_ece"]),
                    failures=entry["failure_count"],
                )
            )

    lines.extend(
        [
            "",
            "## Reproducibility Contract",
            "",
            "- Suite comparisons must pin `suite_id`, `suite_version`, and `suite_hash`.",
            "- Public reports must pass `marked-bench --validate-report REPORT`.",
            "- Leaderboard submissions must pass `marked-bench --validate-submission SUBMISSION`.",
            "- Public release artifacts are pinned by `releases/marked_bench_release_v0_3_0.json`.",
            "- Repository artifact drift is checked by `python scripts/validate_benchmark_artifacts.py`.",
            "",
            "## Current Limitations",
            "",
            "- Current suites are compact public English-language tracks.",
            "- Public cases can be overfit; hidden/private evaluation remains future work.",
            "- Baseline systems are reference points, not claims of state-of-the-art performance.",
            "",
            "## Registry",
            "",
            "The machine-readable registry is `benchmark_registry.json`.",
            "",
        ]
    )
    return "\n".join(lines)


def write_technical_note(path: str | Path = TECHNICAL_NOTE_PATH, root: str | Path = ".") -> None:
    """Write the generated technical note."""

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(build_technical_note(root=root), encoding="utf-8")


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _format_counts(counts: dict[str, int]) -> str:
    return ", ".join(f"{key}={value}" for key, value in sorted(counts.items()))


def _format_quality_gates(gates: dict[str, Any]) -> str:
    return ", ".join(f"{key}={value}" for key, value in sorted(gates.items()))


def _format_score(value: Any) -> str:
    if value is None:
        return "n/a"
    return f"{float(value):.2f}"


def _format_metric(value: Any) -> str:
    return f"{float(value):.4f}"


__all__ = [
    "TECHNICAL_NOTE_PATH",
    "build_technical_note",
    "write_technical_note",
]
