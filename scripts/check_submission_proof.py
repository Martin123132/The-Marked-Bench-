from __future__ import annotations

"""Validate and explain the checked publication-packet submission proof."""

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any, Mapping

ROOT_PATH = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_PATH))

from marked_bench.benchmark_claim import (
    build_result_claim,
    load_result_claim,
    validate_result_claim,
    write_result_claim,
)
from marked_bench.benchmark_publication import (
    build_publication_packet,
    load_publication_packet,
    validate_publication_packet,
    write_publication_packet,
)
from marked_bench.benchmark_result_card import (
    build_result_card,
    load_result_card,
    validate_result_card,
    write_result_card,
)
from marked_bench.benchmark_review import load_submission_review, validate_submission_review
from marked_bench.benchmark_submission import (
    load_leaderboard_submission,
    load_submission_bundle,
    validate_leaderboard_submission,
    validate_submission_bundle,
)
from marked_bench.contradiction.benchmark_suite import load_benchmark_report, validate_benchmark_report


PACKET_DIR = Path("submissions/example_publication_packet")
EVIDENCE_LEDGER = Path("adoption/third_party_evidence_ledger_v0_4_8.json")

RESULT_CARD_NOTES = "Checked example result card for the publication packet workflow."
PUBLICATION_PACKET_NOTES = "Checked example publication packet for the current public release."
RESULT_CLAIM_NOTES = "Checked example result claim for the publication packet workflow."

EXPECTED_REVIEW_DECISION = "needs_revision"
EXPECTED_REVIEW_RECOMMENDATION = "needs_revision"
EXPECTED_RUBRIC_SCORES = {
    "reproducibility": 2,
    "disclosure_quality": 1,
    "score_integrity": 2,
    "explanation_coverage": 1,
    "evidence_quality": 1,
    "limitations": 1,
}


def regenerate_submission_proof_dependents(root: Path = ROOT_PATH) -> None:
    """Rebuild artifacts that depend on the human-authored review decision."""

    packet_dir = root / PACKET_DIR
    card = build_result_card(
        "report.json",
        bundle_path="submission_bundle.json",
        review_path="submission_review.json",
        base_dir=packet_dir,
        notes=RESULT_CARD_NOTES,
    )
    write_result_card(card, packet_dir / "result_card.json")

    packet = build_publication_packet(packet_dir, notes=PUBLICATION_PACKET_NOTES)
    write_publication_packet(packet, packet_dir / "publication_packet.json")

    claim = build_result_claim(
        "publication_packet.json",
        base_dir=packet_dir,
        notes=RESULT_CLAIM_NOTES,
    )
    write_result_claim(claim, packet_dir / "result_claim.json")


def run_submission_proof(root: Path = ROOT_PATH) -> tuple[dict[str, Any], list[str]]:
    packet_dir = root / PACKET_DIR
    failures: list[str] = []

    try:
        report = load_benchmark_report(packet_dir / "report.json")
        submission = load_leaderboard_submission(packet_dir / "submission.json")
        bundle = load_submission_bundle(packet_dir / "submission_bundle.json")
        review = load_submission_review(packet_dir / "submission_review.json")
        card = load_result_card(packet_dir / "result_card.json")
        packet = load_publication_packet(packet_dir / "publication_packet.json")
        claim = load_result_claim(packet_dir / "result_claim.json")
        ledger = _read_json(root / EVIDENCE_LEDGER)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return {}, [f"could not load checked submission proof: {exc}"]

    validations = {
        "report": validate_benchmark_report(report),
        "submission": validate_leaderboard_submission(submission, base_dir=packet_dir),
        "submission bundle": validate_submission_bundle(bundle, base_dir=packet_dir),
        "submission review": validate_submission_review(review, base_dir=packet_dir),
        "result card": validate_result_card(card, base_dir=packet_dir),
        "publication packet": validate_publication_packet(packet, base_dir=packet_dir),
        "result claim": validate_result_claim(claim, base_dir=packet_dir),
    }
    for label, validation in validations.items():
        if validation.get("valid") is not True:
            failures.append(f"{label} validation failed: {validation.get('errors', [])}")

    identity = {
        "system_name": report.get("system_name"),
        "system_version": submission.get("system_version"),
        "submitter": submission.get("submitter"),
        "suite_id": report.get("suite_id"),
        "suite_version": report.get("suite_version"),
        "suite_hash": report.get("suite_hash"),
        "case_count": report.get("case_count"),
        "overall_score": report.get("overall_score"),
    }
    _check_identity(
        identity,
        {
            "submission": submission,
            "submission bundle": bundle,
            "submission review": review,
            "result card": card,
            "publication packet": packet,
            "result claim": claim,
        },
        failures,
    )

    rubric = review.get("rubric", {}) if isinstance(review.get("rubric"), Mapping) else {}
    rubric_scores = {
        name: rubric.get(name, {}).get("score") if isinstance(rubric.get(name), Mapping) else None
        for name in EXPECTED_RUBRIC_SCORES
    }
    if rubric_scores != EXPECTED_RUBRIC_SCORES:
        failures.append(
            f"completed review rubric changed: expected {EXPECTED_RUBRIC_SCORES}, got {rubric_scores}"
        )

    review_summary = review.get("summary", {}) if isinstance(review.get("summary"), Mapping) else {}
    expected_review_values = {
        "decision": EXPECTED_REVIEW_DECISION,
        "recommendation": EXPECTED_REVIEW_RECOMMENDATION,
        "rubric_total": sum(EXPECTED_RUBRIC_SCORES.values()),
        "rubric_max": 12,
        "completed_dimensions": 6,
        "ready_for_decision": True,
    }
    actual_review_values = {
        "decision": review.get("decision"),
        "recommendation": review_summary.get("recommendation"),
        "rubric_total": review_summary.get("rubric_total"),
        "rubric_max": review_summary.get("rubric_max"),
        "completed_dimensions": review_summary.get("completed_dimensions"),
        "ready_for_decision": review_summary.get("ready_for_decision"),
    }
    if actual_review_values != expected_review_values:
        failures.append(
            f"completed review outcome changed: expected {expected_review_values}, got {actual_review_values}"
        )

    publication = card.get("publication", {}) if isinstance(card.get("publication"), Mapping) else {}
    expected_publication = {
        "accepted": False,
        "ready_for_decision": True,
        "review_decision": EXPECTED_REVIEW_DECISION,
        "review_recommendation": EXPECTED_REVIEW_RECOMMENDATION,
    }
    actual_publication = {key: publication.get(key) for key in expected_publication}
    if actual_publication != expected_publication:
        failures.append(
            f"result-card publication boundary changed: expected {expected_publication}, got {actual_publication}"
        )
    if packet.get("ready_for_publication") is not True:
        failures.append("publication packet is not ready for publication")

    not_claims = claim.get("claim", {}).get("not_claims", [])
    required_not_claim = "Not evidence of third-party adoption unless separately verified in the evidence ledger."
    if required_not_claim not in not_claims:
        failures.append("result claim no longer preserves the third-party adoption boundary")
    if claim.get("standard_claims", {}).get("third_party_adoption_requires_verified_evidence") is not True:
        failures.append("result claim no longer requires verified evidence for third-party adoption")

    if ledger.get("entry_count") != 0 or ledger.get("entries") != []:
        failures.append("third-party evidence ledger is no longer empty; refresh the proof boundary")
    if ledger.get("status") != "awaiting-third-party-evidence":
        failures.append("third-party evidence ledger status changed; refresh the proof boundary")

    artifacts = _artifact_rows(packet_dir, root, validations)
    result = {
        "status": "pass" if not failures else "fail",
        "identity": identity,
        "review": {
            "reviewer": review.get("reviewer"),
            "decision": review.get("decision"),
            "summary": dict(review_summary),
            "rubric": {
                name: {
                    "score": entry.get("score"),
                    "max_score": entry.get("max_score"),
                    "notes": entry.get("notes"),
                }
                for name, entry in rubric.items()
                if isinstance(entry, Mapping)
            },
        },
        "publication": {
            "result_card_accepted": publication.get("accepted"),
            "result_card_ready_for_decision": publication.get("ready_for_decision"),
            "packet_ready_for_publication": packet.get("ready_for_publication"),
            "claim_ready_for_citation": validations["result claim"].get("valid"),
        },
        "evidence_ledger": {
            "path": EVIDENCE_LEDGER.as_posix(),
            "entry_count": ledger.get("entry_count"),
            "status": ledger.get("status"),
        },
        "artifacts": artifacts,
    }
    return result, failures


def build_submission_proof_artifact(result: Mapping[str, Any], failures: list[str]) -> str:
    status = "PASS" if not failures else "FAIL"
    identity = result.get("identity", {}) if isinstance(result.get("identity"), Mapping) else {}
    review = result.get("review", {}) if isinstance(result.get("review"), Mapping) else {}
    summary = review.get("summary", {}) if isinstance(review.get("summary"), Mapping) else {}
    publication = result.get("publication", {}) if isinstance(result.get("publication"), Mapping) else {}
    ledger = result.get("evidence_ledger", {}) if isinstance(result.get("evidence_ledger"), Mapping) else {}
    lines = [
        "# Checked Submission Proof",
        "",
        f"Overall status: **{status}**",
        "",
        "## Proof boundary",
        "",
        "This is an internally maintained, external-style example that proves the public submission machinery.",
        "It is not an independent third-party result and it is not evidence of external adoption.",
        f"The evidence ledger remains `{ledger.get('status', 'unknown')}` with {ledger.get('entry_count', 0)} entries.",
        "",
        "## Pinned result identity",
        "",
        "| Field | Value |",
        "| --- | --- |",
        f"| System | `{identity.get('system_name', '')}` `{identity.get('system_version', '')}` |",
        f"| Submitter | `{identity.get('submitter', '')}` |",
        f"| Suite | `{identity.get('suite_id', '')}` v{identity.get('suite_version', '')} |",
        f"| Suite hash | `{identity.get('suite_hash', '')}` |",
        f"| Cases | {identity.get('case_count', '')} |",
        f"| Overall score | {float(identity.get('overall_score', 0.0)):.2f} |",
        "",
        "## Completed reviewer decision",
        "",
        f"Reviewer `{review.get('reviewer', '')}` recorded `{review.get('decision', '')}` with a "
        f"{summary.get('rubric_total', 0)}/{summary.get('rubric_max', 0)} rubric and "
        f"`{summary.get('recommendation', '')}` recommendation.",
        "The decision is intentionally not `accept`: the packet and score reproduce, but the placeholder all-none "
        "system does not provide substantive model disclosure, case-specific reasoning, or a complete failure-mode analysis.",
        "",
        "| Rubric dimension | Score | Reviewer note |",
        "| --- | ---: | --- |",
    ]
    rubric = review.get("rubric", {}) if isinstance(review.get("rubric"), Mapping) else {}
    for name in EXPECTED_RUBRIC_SCORES:
        entry = rubric.get(name, {}) if isinstance(rubric.get(name), Mapping) else {}
        lines.append(
            f"| {name.replace('_', ' ').title()} | {entry.get('score', '')}/{entry.get('max_score', 2)} | "
            f"{entry.get('notes', '')} |"
        )

    lines.extend(
        [
            "",
            "## Validated artifact chain",
            "",
            "| Role | Path | Schema or format | Validation | SHA-256 |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for artifact in result.get("artifacts", []):
        lines.append(
            f"| {artifact['role']} | `{artifact['path']}` | `{artifact['schema']}` | "
            f"{artifact['validation']} | `{artifact['sha256']}` |"
        )

    lines.extend(
        [
            "",
            "## Publication outcome",
            "",
            f"- Result-card accepted for leaderboard: `{str(publication.get('result_card_accepted')).lower()}`.",
            f"- Reviewer decision complete: `{str(publication.get('result_card_ready_for_decision')).lower()}`.",
            f"- Self-contained packet validates for publication: `{str(publication.get('packet_ready_for_publication')).lower()}`.",
            f"- Bounded result claim validates for citation: `{str(publication.get('claim_ready_for_citation')).lower()}`.",
            "- Third-party adoption evidence: `false`; that requires a separate verified evidence-ledger entry.",
            "",
            "A valid publication packet can document a weak or rejected system result. Publication readiness means the "
            "evidence is complete and internally consistent; it does not imply leaderboard acceptance or model quality.",
            "",
            "## Reproduce the proof",
            "",
            "```bash",
            "marked-bench --validate-report submissions/example_publication_packet/report.json",
            "marked-bench --validate-submission submissions/example_publication_packet/submission.json",
            "marked-bench --validate-submission-bundle submissions/example_publication_packet/submission_bundle.json",
            "marked-bench --validate-submission-review submissions/example_publication_packet/submission_review.json",
            "marked-bench --validate-result-card submissions/example_publication_packet/result_card.json",
            "marked-bench --validate-publication-packet submissions/example_publication_packet/publication_packet.json",
            "marked-bench --validate-result-claim submissions/example_publication_packet/result_claim.json",
            "python scripts/check_submission_proof.py --artifact docs/SUBMISSION_PROOF.md",
            "```",
            "",
            "## Limitations",
            "",
            "- The example is produced and reviewed by the project, not by an independent evaluator.",
            "- Its all-none predictions intentionally demonstrate a valid but weak result.",
            "- The proof confirms schemas, hashes, identity, review state, and claim boundaries; it does not establish adoption.",
        ]
    )

    if failures:
        lines.extend(["", "## Failures", ""])
        lines.extend(f"- {failure}" for failure in failures)
    return "\n".join(lines) + "\n"


def _check_identity(
    identity: Mapping[str, Any],
    artifacts: Mapping[str, Mapping[str, Any]],
    failures: list[str],
) -> None:
    fields = (
        "system_name",
        "system_version",
        "submitter",
        "suite_id",
        "suite_version",
        "suite_hash",
        "case_count",
        "overall_score",
    )
    for label, artifact in artifacts.items():
        for field in fields:
            if field in artifact and artifact.get(field) != identity.get(field):
                failures.append(
                    f"{label}: {field} mismatch; expected {identity.get(field)!r}, got {artifact.get(field)!r}"
                )


def _artifact_rows(
    packet_dir: Path,
    root: Path,
    validations: Mapping[str, Mapping[str, Any]],
) -> list[dict[str, Any]]:
    specs = (
        ("predictions", packet_dir / "predictions.jsonl", "JSONL prediction records", "submission bundle"),
        ("report", packet_dir / "report.json", "marked_bench.contradiction-benchmark-report.v2", "report"),
        ("submission", packet_dir / "submission.json", "marked_bench.leaderboard-submission.v1", "submission"),
        (
            "submission bundle",
            packet_dir / "submission_bundle.json",
            "marked_bench.leaderboard-submission-bundle.v1",
            "submission bundle",
        ),
        ("submission review", packet_dir / "submission_review.json", "marked_bench.submission-review.v1", "submission review"),
        ("result card", packet_dir / "result_card.json", "marked_bench.result-card.v1", "result card"),
        (
            "publication packet",
            packet_dir / "publication_packet.json",
            "marked_bench.publication-packet.v1",
            "publication packet",
        ),
        ("result claim", packet_dir / "result_claim.json", "marked_bench.result-claim.v1", "result claim"),
    )
    rows = []
    for role, path, schema, validation_key in specs:
        validation = validations.get(validation_key, {})
        valid = validation.get("valid") is True
        rows.append(
            {
                "role": role,
                "path": path.resolve().relative_to(root.resolve()).as_posix(),
                "schema": schema,
                "validation": "PASS" if valid else "FAIL",
                "sha256": _file_sha256(path),
            }
        )
    return rows


def _file_sha256(path: Path) -> str:
    data = path.read_bytes()
    if b"\0" not in data:
        data = data.replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest()


def _read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError(f"{path}: expected a JSON object")
    return data


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate the checked submission proof.")
    parser.add_argument(
        "--artifact",
        default=None,
        help="Optional output path for the reviewer-facing submission proof.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result, failures = run_submission_proof()
    if args.artifact:
        output = Path(args.artifact)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(build_submission_proof_artifact(result, failures), encoding="utf-8")
    for failure in failures:
        print(f"ERROR: {failure}")
    if failures:
        return 1
    print("Checked submission proof passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
