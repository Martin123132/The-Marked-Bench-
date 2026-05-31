from __future__ import annotations

"""Machine-readable registry for The Marked Bench public artifacts."""

import json
from pathlib import Path
from typing import Any, Mapping

from marked_bench.benchmark_leaderboard import LEADERBOARD_SCHEMA
from marked_bench.benchmark_review import REVIEW_SCHEMA
from marked_bench.benchmark_submission import SUBMISSION_BUNDLE_SCHEMA, SUBMISSION_SCHEMA
from marked_bench.contradiction.benchmark_suite import (
    PREDICTION_SCHEMA,
    REPORT_SCHEMA,
    SUITE_MANIFEST_SCHEMA,
    build_suite_manifest,
)


REGISTRY_SCHEMA = "marked_bench.benchmark-registry.v1"

_TRACKS: tuple[Mapping[str, Any], ...] = (
    {
        "name": "contradiction",
        "title": "Foundation contradiction detection",
        "status": "foundation",
        "suite": "contradiction",
        "suite_manifest": "suites/marked_bench_contradiction_standard_v0_1_0.json",
        "leaderboard": "leaderboard/leaderboard_v0_1_0.json",
        "baseline_reports": [
            "baselines/contradiction_engine_v0_1_0.json",
            "baselines/always_none_v0_1_0.json",
        ],
        "commands": {
            "run_baseline": "marked-bench --suite contradiction --report artifacts/foundation-report.json",
            "export_prediction_template": (
                "marked-bench --suite contradiction "
                "--export-prediction-template artifacts/foundation-predictions.jsonl"
            ),
            "score_predictions": (
                "marked-bench --suite contradiction "
                "--score-predictions artifacts/foundation-predictions.jsonl "
                "--system-name SYSTEM --report artifacts/foundation-system-report.json"
            ),
            "create_submission": (
                "marked-bench --create-submission submissions/foundation-system.json "
                "--submission-report artifacts/foundation-system-report.json "
                "--system-version VERSION --submitter SUBMITTER"
            ),
        },
    },
    {
        "name": "contradiction-adversarial",
        "title": "Adversarial contradiction detection",
        "status": "active",
        "suite": "contradiction-adversarial",
        "suite_manifest": "suites/marked_bench_contradiction_adversarial_v0_2_0.json",
        "leaderboard": "leaderboard/leaderboard_adversarial_v0_2_0.json",
        "baseline_reports": [
            "baselines/contradiction_engine_adversarial_v0_2_0.json",
            "baselines/always_none_adversarial_v0_2_0.json",
        ],
        "commands": {
            "run_baseline": (
                "marked-bench --suite contradiction-adversarial "
                "--report artifacts/adversarial-report.json"
            ),
            "export_prediction_template": (
                "marked-bench --suite contradiction-adversarial "
                "--export-prediction-template artifacts/adversarial-predictions.jsonl"
            ),
            "score_predictions": (
                "marked-bench --suite contradiction-adversarial "
                "--score-predictions artifacts/adversarial-predictions.jsonl "
                "--system-name SYSTEM --report artifacts/adversarial-system-report.json"
            ),
            "create_submission": (
                "marked-bench --create-submission submissions/adversarial-system.json "
                "--submission-report artifacts/adversarial-system-report.json "
                "--system-version VERSION --submitter SUBMITTER"
            ),
        },
    },
    {
        "name": "contradiction-multihop",
        "title": "Multi-hop contradiction detection",
        "status": "active",
        "suite": "contradiction-multihop",
        "suite_manifest": "suites/marked_bench_contradiction_multihop_v0_3_0.json",
        "leaderboard": "leaderboard/leaderboard_multihop_v0_3_0.json",
        "baseline_reports": [
            "baselines/contradiction_engine_multihop_v0_3_0.json",
            "baselines/always_none_multihop_v0_3_0.json",
        ],
        "commands": {
            "run_baseline": (
                "marked-bench --suite contradiction-multihop "
                "--report artifacts/multihop-report.json"
            ),
            "export_prediction_template": (
                "marked-bench --suite contradiction-multihop "
                "--export-prediction-template artifacts/multihop-predictions.jsonl"
            ),
            "score_predictions": (
                "marked-bench --suite contradiction-multihop "
                "--score-predictions artifacts/multihop-predictions.jsonl "
                "--system-name SYSTEM --report artifacts/multihop-system-report.json"
            ),
            "create_submission": (
                "marked-bench --create-submission submissions/multihop-system.json "
                "--submission-report artifacts/multihop-system-report.json "
                "--system-version VERSION --submitter SUBMITTER"
            ),
        },
    },
    {
        "name": "contradiction-controls",
        "title": "False-positive control contradiction detection",
        "status": "active",
        "suite": "contradiction-controls",
        "suite_manifest": "suites/marked_bench_contradiction_controls_v0_4_0.json",
        "leaderboard": "leaderboard/leaderboard_controls_v0_4_0.json",
        "baseline_reports": [
            "baselines/contradiction_engine_controls_v0_4_0.json",
            "baselines/always_none_controls_v0_4_0.json",
        ],
        "commands": {
            "run_baseline": (
                "marked-bench --suite contradiction-controls "
                "--report artifacts/controls-report.json"
            ),
            "export_prediction_template": (
                "marked-bench --suite contradiction-controls "
                "--export-prediction-template artifacts/controls-predictions.jsonl"
            ),
            "score_predictions": (
                "marked-bench --suite contradiction-controls "
                "--score-predictions artifacts/controls-predictions.jsonl "
                "--system-name SYSTEM --report artifacts/controls-system-report.json"
            ),
            "create_submission": (
                "marked-bench --create-submission submissions/controls-system.json "
                "--submission-report artifacts/controls-system-report.json "
                "--system-version VERSION --submitter SUBMITTER"
            ),
        },
    },
)


def build_benchmark_registry() -> dict[str, Any]:
    """Return the public benchmark registry as JSON-serializable data."""

    return {
        "schema": REGISTRY_SCHEMA,
        "project": "The Marked Bench",
        "benchmark_family": "contradiction-detection",
        "default_track": "contradiction-multihop",
        "schemas": {
            "benchmark_registry": "schemas/benchmark_registry.schema.json",
            "suite_manifest": "schemas/contradiction_suite_manifest.schema.json",
            "benchmark_report": "schemas/contradiction_benchmark_report.schema.json",
            "predictions": "schemas/contradiction_predictions.schema.json",
            "leaderboard": "schemas/leaderboard.schema.json",
            "leaderboard_submission": "schemas/leaderboard_submission.schema.json",
            "submission_bundle": "schemas/submission_bundle.schema.json",
            "submission_review": "schemas/submission_review.schema.json",
            "release_manifest": "schemas/release_manifest.schema.json",
            "conformance_report": "schemas/conformance_report.schema.json",
            "result_card": "schemas/result_card.schema.json",
            "adoption_packet": "schemas/adoption_packet.schema.json",
            "third_party_evidence_ledger": "schemas/third_party_evidence_ledger.schema.json",
        },
        "schema_ids": {
            "suite_manifest": SUITE_MANIFEST_SCHEMA,
            "benchmark_report": REPORT_SCHEMA,
            "predictions": PREDICTION_SCHEMA,
            "leaderboard": LEADERBOARD_SCHEMA,
            "leaderboard_submission": SUBMISSION_SCHEMA,
            "submission_bundle": SUBMISSION_BUNDLE_SCHEMA,
            "submission_review": REVIEW_SCHEMA,
            "conformance_report": "marked_bench.conformance-report.v1",
            "result_card": "marked_bench.result-card.v1",
            "adoption_packet": "marked_bench.adoption-packet.v1",
            "third_party_evidence_ledger": "marked_bench.third-party-evidence-ledger.v1",
        },
        "governance_docs": [
            "docs/ADOPTION_GUIDE.md",
            "docs/ANNOUNCEMENT_PACKAGE.md",
            "docs/BENCHMARK_STANDARD.md",
            "docs/BENCHMARK_CARD.md",
            "docs/TECHNICAL_NOTE.md",
            "docs/GOVERNANCE.md",
            "docs/SUBMISSION_REVIEW_RUBRIC.md",
            "docs/THIRD_PARTY_EVIDENCE.md",
            "docs/RELEASE_NOTES_v0_2_0.md",
            "docs/RELEASE_NOTES_v0_3_0.md",
            "docs/RELEASE_NOTES_v0_3_1.md",
            "docs/RELEASE_NOTES_v0_3_2.md",
            "docs/RELEASE_NOTES_v0_3_3.md",
            "docs/RELEASE_NOTES_v0_3_4.md",
            "docs/RELEASE_NOTES_v0_3_5.md",
            "docs/RELEASE_NOTES_v0_3_6.md",
            "docs/RELEASE_NOTES_v0_3_7.md",
            "docs/RELEASE_NOTES_v0_3_8.md",
            "docs/RELEASE_NOTES_v0_3_9.md",
            "docs/RELEASE_NOTES_v0_3_10.md",
            "docs/RELEASE_NOTES_v0_4_0.md",
            "docs/SUBMISSION_GUIDE.md",
            "docs/RELEASE_CHECKLIST.md",
        ],
        "tracks": [_build_track(track) for track in _TRACKS],
    }


def write_benchmark_registry(path: str | Path) -> None:
    """Write the public benchmark registry as stable, sorted JSON."""

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(build_benchmark_registry(), indent=2, sort_keys=True),
        encoding="utf-8",
    )


def _build_track(track: Mapping[str, Any]) -> dict[str, Any]:
    manifest = build_suite_manifest(suite=str(track["suite"]))
    return {
        "name": track["name"],
        "title": track["title"],
        "status": track["status"],
        "suite_id": manifest["suite_id"],
        "suite_version": manifest["suite_version"],
        "suite_hash": manifest["suite_hash"],
        "case_count": manifest["case_count"],
        "labels": manifest["labels"],
        "profile": manifest["profile"],
        "suite_manifest": track["suite_manifest"],
        "report_schema": REPORT_SCHEMA,
        "prediction_schema": PREDICTION_SCHEMA,
        "leaderboard": track["leaderboard"],
        "baseline_reports": list(track["baseline_reports"]),
        "commands": {
            **dict(track["commands"]),
            "validate_report": "marked-bench --validate-report REPORT",
            "validate_submission": "marked-bench --validate-submission SUBMISSION",
            "create_submission_bundle": (
                "marked-bench --create-submission-bundle BUNDLE "
                "--bundle-submission SUBMISSION"
            ),
            "validate_submission_bundle": "marked-bench --validate-submission-bundle BUNDLE",
            "create_result_card": (
                "marked-bench --create-result-card CARD "
                "--result-report REPORT --result-bundle BUNDLE"
            ),
            "validate_result_card": "marked-bench --validate-result-card CARD",
            "build_leaderboard": (
                "marked-bench --build-leaderboard REPORT... "
                f"--leaderboard-output {track['leaderboard']}"
            ),
        },
    }


__all__ = [
    "REGISTRY_SCHEMA",
    "build_benchmark_registry",
    "write_benchmark_registry",
]
