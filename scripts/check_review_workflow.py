from __future__ import annotations

"""Check that reviewer workflow labels, docs, and PR checks stay aligned."""

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parent.parent

REQUIRED_LABELS = (
    "triage-ready",
    "needs-evidence",
    "needs-repro",
    "scoring-review",
    "accepted-baseline",
    "blocked-by-validation",
    "ready-for-review",
)

REQUIRED_COMMANDS = (
    "python -m unittest discover -s tests",
    "python scripts/validate_benchmark_artifacts.py",
    "python -m marked_bench.benchmark_cli --check-standard-status",
    "python scripts/check_scoring_sanity.py --artifact docs/SCORING_SANITY.md",
    "python scripts/check_case_quality.py --artifact docs/CASE_QUALITY.md",
    "python scripts/check_baseline_robustness.py --artifact docs/BASELINE_ROBUSTNESS.md",
    "python scripts/check_evaluator_walkthrough.py",
    "python scripts/check_submission_proof.py --artifact docs/SUBMISSION_PROOF.md",
    "python scripts/regenerate_release_artifacts.py --check",
    "python scripts/check_review_workflow.py",
    "python scripts/check_license_notice.py",
)


def main() -> int:
    errors: list[str] = []
    labels_text = _read_text(Path(".github/labels.yml"), errors)
    workflow_text = _read_text(Path("docs/REVIEW_WORKFLOW.md"), errors)
    pr_template_text = _read_text(Path(".github/PULL_REQUEST_TEMPLATE.md"), errors)

    labels = _extract_labels(labels_text)
    for label in REQUIRED_LABELS:
        if label not in labels:
            errors.append(f".github/labels.yml: missing required label {label!r}")
        if f"`{label}`" not in workflow_text:
            errors.append(f"docs/REVIEW_WORKFLOW.md: missing required label {label!r}")

    for command in REQUIRED_COMMANDS:
        if command not in workflow_text:
            errors.append(f"docs/REVIEW_WORKFLOW.md: missing required command {command!r}")
        if command not in pr_template_text:
            errors.append(f".github/PULL_REQUEST_TEMPLATE.md: missing required command {command!r}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print("Review workflow checks passed.")
    return 0


def _read_text(path: Path, errors: list[str]) -> str:
    try:
        return (ROOT / path).read_text(encoding="utf-8")
    except OSError as exc:
        errors.append(f"{path}: could not read file: {exc}")
        return ""


def _extract_labels(text: str) -> set[str]:
    return {
        match.group(1).strip().strip('"').strip("'")
        for match in re.finditer(r"^\s*-\s*name:\s*(.+?)\s*$", text, re.MULTILINE)
    }


if __name__ == "__main__":
    raise SystemExit(main())
