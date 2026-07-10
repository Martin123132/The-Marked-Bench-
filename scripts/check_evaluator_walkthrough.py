from __future__ import annotations

"""Exercise the documented five-minute evaluator path without repo writes."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
from typing import Sequence


ROOT = Path(__file__).resolve().parent.parent
WALKTHROUGH = Path("docs/FIVE_MINUTE_EVALUATOR_WALKTHROUGH.md")
README = Path("README.md")
SUITE_MANIFEST = Path("suites/marked_bench_contradiction_multihop_v0_3_0.json")
EXAMPLE_PREDICTIONS = Path("submissions/example_external_jsonl/predictions.jsonl")
EXAMPLE_REPORT = Path("submissions/example_external_jsonl/example_external_report.json")

REQUIRED_WALKTHROUGH_FRAGMENTS = (
    "# Five-Minute Evaluator Walkthrough",
    "pip install -e .",
    "marked-bench --list-suites",
    "marked-bench --suite-info contradiction-multihop",
    (
        "marked-bench --suite contradiction-multihop --score-predictions "
        "submissions/example_external_jsonl/predictions.jsonl --system-name \"QuickstartExample\" "
        "--report artifacts/quickstart/report.json"
    ),
    "marked-bench --validate-report artifacts/quickstart/report.json",
    (
        "marked-bench --suite contradiction-multihop --export-prediction-template "
        "artifacts/quickstart/predictions.jsonl"
    ),
    "[external submission walkthrough](EXTERNAL_SUBMISSION_WALKTHROUGH.md)",
    "[LICENSE](../LICENSE)",
)


def main() -> int:
    errors: list[str] = []
    walkthrough_text = _read_text(WALKTHROUGH, errors)
    readme_text = _read_text(README, errors)

    for fragment in REQUIRED_WALKTHROUGH_FRAGMENTS:
        if fragment not in walkthrough_text:
            errors.append(f"{WALKTHROUGH}: missing required fragment {fragment!r}")
    if "[Five-minute evaluator walkthrough](docs/FIVE_MINUTE_EVALUATOR_WALKTHROUGH.md)" not in readme_text:
        errors.append(f"{README}: missing the five-minute evaluator walkthrough link")

    suite = _read_json(SUITE_MANIFEST, errors)
    checked_example = _read_json(EXAMPLE_REPORT, errors)

    with tempfile.TemporaryDirectory(prefix="marked-bench-walkthrough-") as temp_dir:
        output_root = Path(temp_dir)
        prediction_template = output_root / "predictions.jsonl"
        report_path = output_root / "report.json"

        list_result = _run_cli(["--list-suites"], "list suites", errors)
        if list_result and "contradiction-multihop" not in list_result.stdout:
            errors.append("list suites: multi-hop suite is not discoverable")

        suite_result = _run_cli(
            ["--suite-info", "contradiction-multihop"],
            "inspect multi-hop suite",
            errors,
        )
        if suite_result:
            for expected in (
                str(suite.get("suite_id", "")),
                f"v{suite.get('suite_version', '')}",
                str(suite.get("suite_hash", "")),
            ):
                if expected not in suite_result.stdout:
                    errors.append(f"inspect multi-hop suite: output is missing {expected!r}")

        export_result = _run_cli(
            [
                "--suite",
                "contradiction-multihop",
                "--export-prediction-template",
                str(prediction_template),
            ],
            "export prediction template",
            errors,
        )
        if export_result:
            _check_prediction_template(prediction_template, suite, errors)

        score_result = _run_cli(
            [
                "--suite",
                "contradiction-multihop",
                "--score-predictions",
                str(ROOT / EXAMPLE_PREDICTIONS),
                "--system-name",
                "QuickstartExample",
                "--report",
                str(report_path),
            ],
            "score checked example",
            errors,
        )
        if score_result:
            _check_report(report_path, suite, checked_example, errors)
            _run_cli(["--validate-report", str(report_path)], "validate generated report", errors)

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print("Evaluator walkthrough checks passed.")
    return 0


def _run_cli(args: Sequence[str], label: str, errors: list[str]) -> subprocess.CompletedProcess[str] | None:
    try:
        result = subprocess.run(
            [sys.executable, "-m", "marked_bench.benchmark_cli", *args],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        errors.append(f"{label}: could not run: {exc}")
        return None
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or f"exit {result.returncode}"
        errors.append(f"{label}: {detail}")
        return None
    return result


def _check_prediction_template(path: Path, suite: dict, errors: list[str]) -> None:
    try:
        records = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"export prediction template: invalid JSONL: {exc}")
        return
    expected_count = int(suite.get("case_count", -1))
    if len(records) != expected_count:
        errors.append(
            f"export prediction template: expected {expected_count} records, found {len(records)}"
        )
    case_ids = {str(record.get("case_id")) for record in records}
    if len(case_ids) != len(records):
        errors.append("export prediction template: case IDs are not unique")
    for index, record in enumerate(records, start=1):
        if "case_id" not in record or "predicted" not in record:
            errors.append(f"export prediction template: record {index} lacks case_id or predicted")


def _check_report(report_path: Path, suite: dict, checked_example: dict, errors: list[str]) -> None:
    report = _read_json(report_path, errors, absolute=True)
    expected_values = {
        "suite_id": suite.get("suite_id"),
        "suite_version": suite.get("suite_version"),
        "suite_hash": suite.get("suite_hash"),
        "case_count": suite.get("case_count"),
        "overall_score": checked_example.get("overall_score"),
    }
    for key, expected in expected_values.items():
        if report.get(key) != expected:
            errors.append(
                f"score checked example: {key} mismatch; expected {expected!r}, got {report.get(key)!r}"
            )
    if report.get("system_name") != "QuickstartExample":
        errors.append("score checked example: system_name was not retained")


def _read_text(path: Path, errors: list[str]) -> str:
    try:
        return (ROOT / path).read_text(encoding="utf-8")
    except OSError as exc:
        errors.append(f"{path}: could not read file: {exc}")
        return ""


def _read_json(path: Path, errors: list[str], *, absolute: bool = False) -> dict:
    target = path if absolute else ROOT / path
    try:
        data = json.loads(target.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"{path}: could not read JSON: {exc}")
        return {}
    if not isinstance(data, dict):
        errors.append(f"{path}: expected a JSON object")
        return {}
    return data


if __name__ == "__main__":
    raise SystemExit(main())
