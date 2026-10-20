from __future__ import annotations

"""Build and exercise an installed wheel outside the repository and user site."""

import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile
import venv


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_VERSION = "0.4.10"


def run(args: list[str], cwd: Path, env: dict[str, str]) -> str:
    result = subprocess.run(
        args, cwd=cwd, env=env, capture_output=True, text=True, timeout=180, check=False
    )
    if result.returncode:
        raise RuntimeError(
            f"Command failed ({result.returncode}): {args!r}\n{result.stdout}\n{result.stderr}"
        )
    return result.stdout


def main() -> int:
    env = dict(os.environ)
    env.pop("PYTHONPATH", None)
    env.pop("PYTHONHOME", None)
    env["PYTHONNOUSERSITE"] = "1"
    env["PIP_DISABLE_PIP_VERSION_CHECK"] = "1"
    with tempfile.TemporaryDirectory(prefix="marked-bench-installed-") as temporary:
        work = Path(temporary)
        source = work / "source"
        source.mkdir()
        for name in ("setup.py", "LICENSE", "COMMERCIAL-LICENSE.md", "NOTICE.md"):
            shutil.copy2(ROOT / name, source / name)
        shutil.copytree(
            ROOT / "marked_bench", source / "marked_bench",
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
        )
        wheels = work / "wheels"
        run(
            [sys.executable, "-m", "pip", "wheel", "--no-deps", "--wheel-dir", str(wheels), str(source)],
            work, env,
        )
        wheel_files = list(wheels.glob("marked_bench-*.whl"))
        if len(wheel_files) != 1:
            raise RuntimeError("Expected exactly one built Marked Bench wheel")
        environment = work / "venv"
        venv.EnvBuilder(with_pip=True).create(environment)
        binaries = environment / ("Scripts" if os.name == "nt" else "bin")
        python = binaries / ("python.exe" if os.name == "nt" else "python")
        cli = binaries / ("marked-bench.exe" if os.name == "nt" else "marked-bench")
        run([str(python), "-m", "pip", "install", str(wheel_files[0])], work, env)
        location = json.loads(run(
            [
                str(python), "-I", "-c",
                "import importlib.metadata, json, pathlib, sys, marked_bench; "
                "p=pathlib.Path(marked_bench.__file__).resolve(); "
                "assert p.is_relative_to(pathlib.Path(sys.prefix).resolve()), str(p); "
                "print(json.dumps({'version': importlib.metadata.version('marked_bench'), "
                "'isolated_import': True}))",
            ],
            work, env,
        ))
        if location["version"] != EXPECTED_VERSION:
            raise RuntimeError(f"Unexpected installed version: {location}")
        discovered = run([str(cli), "--list-suites"], work, env)
        if "contradiction-multihop" not in discovered:
            raise RuntimeError("Installed CLI did not discover the multi-hop suite")
        info = run([str(cli), "--suite-info", "contradiction-multihop"], work, env)
        suite = json.loads(
            (ROOT / "suites/marked_bench_contradiction_multihop_v0_3_0.json").read_text(encoding="utf-8-sig")
        )
        if str(suite["suite_hash"]) not in info:
            raise RuntimeError("Installed suite hash differs from the pinned manifest")
        fixture = ROOT / "submissions/example_external_jsonl"
        predictions = work / "predictions.jsonl"
        shutil.copy2(fixture / "predictions.jsonl", predictions)
        expected = json.loads((fixture / "example_external_report.json").read_text(encoding="utf-8-sig"))
        report_path = work / "report.json"
        run(
            [str(cli), "--suite", "contradiction-multihop", "--score-predictions", str(predictions),
             "--system-name", "InstalledWheelExample", "--report", str(report_path)],
            work, env,
        )
        run([str(cli), "--validate-report", str(report_path)], work, env)
        report = json.loads(report_path.read_text(encoding="utf-8"))
        for key in ("suite_id", "suite_version", "suite_hash", "case_count", "overall_score"):
            if report[key] != expected[key]:
                raise RuntimeError(f"Installed report differs from the checked example: {key}")
        template = work / "template.jsonl"
        run(
            [str(cli), "--suite", "contradiction-multihop", "--export-prediction-template", str(template)],
            work, env,
        )
        rows = [json.loads(line) for line in template.read_text(encoding="utf-8").splitlines() if line.strip()]
        if len(rows) != suite["case_count"] or len({row["case_id"] for row in rows}) != len(rows):
            raise RuntimeError("Installed prediction template has missing or duplicate cases")
        if any("predicted" not in row for row in rows):
            raise RuntimeError("Installed prediction template lacks prediction fields")
        print(json.dumps({
            "platform": platform.system(),
            "python": platform.python_version(),
            **location,
            "suite_hash": report["suite_hash"],
            "overall_score": report["overall_score"],
            "case_count": len(rows),
            "predictions_sha256": hashlib.sha256(predictions.read_bytes().replace(b"\r\n", b"\n")).hexdigest(),
            "working_directory_outside_checkout": True,
            "console_entry_point": True,
        }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
