from __future__ import annotations

"""Regenerate deterministic public release artifacts in dependency order."""

import argparse
from pathlib import Path
import sys

ROOT_PATH = Path(__file__).resolve().parent.parent
SCRIPT_PATH = ROOT_PATH / "scripts"
sys.path.insert(0, str(ROOT_PATH))
sys.path.insert(0, str(SCRIPT_PATH))

from check_case_quality import build_case_quality_artifact, run_case_quality
from check_baseline_robustness import build_baseline_robustness_artifact, run_baseline_robustness
from check_scoring_sanity import build_scoring_sanity_artifact, run_scoring_sanity
from check_submission_proof import (
    build_submission_proof_artifact,
    regenerate_submission_proof_dependents,
    run_submission_proof,
)
from marked_bench.benchmark_adoption import write_adoption_packet
from marked_bench.benchmark_change_control import write_change_control
from marked_bench.benchmark_conformance import write_conformance_report
from marked_bench.benchmark_evidence import write_evidence_ledger
from marked_bench.benchmark_implementation import write_implementation_kit
from marked_bench.benchmark_registry import write_benchmark_registry
from marked_bench.benchmark_release import write_release_manifest
from marked_bench.benchmark_scoring_compatibility import write_scoring_compatibility_profile
from marked_bench.benchmark_scoring_spec import write_scoring_spec, write_scoring_spec_markdown
from marked_bench.benchmark_standard_profile import write_standard_profile
from marked_bench.benchmark_technical_note import write_technical_note
from marked_bench.contradiction.benchmark_suite import write_suite_manifest


GENERATED_PATHS = (
    "suites/marked_bench_contradiction_standard_v0_1_1.json",
    "benchmark_registry.json",
    "docs/TECHNICAL_NOTE.md",
    "standard/marked_bench_standard_profile_v0_4_9.json",
    "standard/marked_bench_scoring_compatibility_v0_4_9.json",
    "standard/marked_bench_scoring_spec_v0_4_9.json",
    "docs/SCORING_SPEC.md",
    "adoption/marked_bench_adoption_packet_v0_4_9.json",
    "adoption/marked_bench_implementation_kit_v0_4_9.json",
    "adoption/third_party_evidence_ledger_v0_4_9.json",
    "standard/marked_bench_change_control_v0_4_9.json",
    "docs/SCORING_SANITY.md",
    "docs/CASE_QUALITY.md",
    "docs/BASELINE_ROBUSTNESS.md",
    "submissions/example_publication_packet/result_card.json",
    "submissions/example_publication_packet/publication_packet.json",
    "submissions/example_publication_packet/result_claim.json",
    "docs/SUBMISSION_PROOF.md",
    "releases/marked_bench_release_v0_4_9.json",
    "conformance/marked_bench_conformance_v0_4_9.json",
)


def regenerate_release_artifacts(root: Path = ROOT_PATH) -> None:
    write_suite_manifest(root / "suites" / "marked_bench_contradiction_standard_v0_1_1.json", suite="contradiction")
    write_benchmark_registry(root / "benchmark_registry.json")
    write_technical_note(root / "docs" / "TECHNICAL_NOTE.md")
    write_standard_profile(root / "standard" / "marked_bench_standard_profile_v0_4_9.json")
    write_scoring_compatibility_profile(root / "standard" / "marked_bench_scoring_compatibility_v0_4_9.json")
    write_scoring_spec(root / "standard" / "marked_bench_scoring_spec_v0_4_9.json")
    write_scoring_spec_markdown(root / "docs" / "SCORING_SPEC.md")
    write_adoption_packet(root / "adoption" / "marked_bench_adoption_packet_v0_4_9.json")
    write_implementation_kit(root / "adoption" / "marked_bench_implementation_kit_v0_4_9.json")
    write_evidence_ledger(root / "adoption" / "third_party_evidence_ledger_v0_4_9.json")
    write_change_control(root / "standard" / "marked_bench_change_control_v0_4_9.json")

    scoring_results, scoring_failures = run_scoring_sanity()
    (root / "docs" / "SCORING_SANITY.md").write_text(
        build_scoring_sanity_artifact(scoring_results, scoring_failures),
        encoding="utf-8",
    )
    if scoring_failures:
        raise ValueError("scoring sanity failed: " + "; ".join(scoring_failures))

    quality_results, quality_failures = run_case_quality()
    (root / "docs" / "CASE_QUALITY.md").write_text(
        build_case_quality_artifact(quality_results, quality_failures),
        encoding="utf-8",
    )
    if quality_failures:
        raise ValueError("case quality failed: " + "; ".join(quality_failures))

    robustness_results, robustness_failures = run_baseline_robustness(root)
    (root / "docs" / "BASELINE_ROBUSTNESS.md").write_text(
        build_baseline_robustness_artifact(robustness_results, robustness_failures),
        encoding="utf-8",
    )
    if robustness_failures:
        raise ValueError("baseline robustness failed: " + "; ".join(robustness_failures))

    regenerate_submission_proof_dependents(root)
    proof_result, proof_failures = run_submission_proof(root)
    (root / "docs" / "SUBMISSION_PROOF.md").write_text(
        build_submission_proof_artifact(proof_result, proof_failures),
        encoding="utf-8",
    )
    if proof_failures:
        raise ValueError("checked submission proof failed: " + "; ".join(proof_failures))

    conformance_path = root / "conformance" / "marked_bench_conformance_v0_4_9.json"
    if not conformance_path.exists():
        conformance_path.parent.mkdir(parents=True, exist_ok=True)
        conformance_path.write_text("{}\n", encoding="utf-8")

    # The release manifest hashes conformance, and conformance verifies the
    # manifest. Three passes let a newly seeded version reach a stable pair.
    for _pass in range(3):
        write_release_manifest(root / "releases" / "marked_bench_release_v0_4_9.json", root=root)
        write_conformance_report(
            conformance_path,
            root=root,
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Regenerate deterministic release artifacts.")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Fail if regenerated artifacts would differ, without leaving rewrites in the working tree.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.check:
        return _check_current()
    regenerate_release_artifacts()
    print("Release artifacts regenerated.")
    return 0


def _check_current() -> int:
    before = _snapshot(ROOT_PATH)
    try:
        regenerate_release_artifacts()
        after = _snapshot(ROOT_PATH)
    finally:
        _restore(ROOT_PATH, before)

    changed = [
        relative_path
        for relative_path in GENERATED_PATHS
        if before.get(relative_path) != after.get(relative_path)
    ]
    if changed:
        for path in changed:
            print(f"ERROR: generated artifact is stale: {path}")
        return 1
    print("Release artifacts are current.")
    return 0


def _snapshot(root: Path) -> dict[str, bytes | None]:
    snapshot: dict[str, bytes | None] = {}
    for relative_path in GENERATED_PATHS:
        path = root / relative_path
        snapshot[relative_path] = path.read_bytes() if path.exists() else None
    return snapshot


def _restore(root: Path, snapshot: dict[str, bytes | None]) -> None:
    for relative_path, data in snapshot.items():
        path = root / relative_path
        if data is None:
            if path.exists():
                path.unlink()
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)


if __name__ == "__main__":
    raise SystemExit(main())
