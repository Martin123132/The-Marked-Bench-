"""Regression checks for submission paths, including real filesystem links."""

from __future__ import annotations

import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock

from marked_bench import benchmark_submission as submissions


class SubmissionSecurityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="marked-bench-security-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name) / "packet"
        self.root.mkdir()
        self.outside = Path(self.temporary.name) / "outside"
        self.outside.mkdir()
        (self.outside / "input.json").write_text("{}", encoding="utf-8")

    def assert_builder_rejects_before_io(self, submission_path, prediction_path=None) -> None:
        with (
            mock.patch.object(submissions, "load_leaderboard_submission") as load,
            mock.patch.object(submissions, "_canonical_file_bytes") as read,
            self.assertRaisesRegex(ValueError, "outside bundle base directory"),
        ):
            submissions.build_submission_bundle(
                submission_path, prediction_path=prediction_path, base_dir=self.root
            )
        load.assert_not_called()
        read.assert_not_called()

    def test_builder_rejects_outside_submission_before_reading(self) -> None:
        for path in ("../outside/input.json", self.outside / "input.json"):
            with self.subTest(path=str(path)):
                self.assert_builder_rejects_before_io(path)

    def test_builder_rejects_outside_predictions_before_reading(self) -> None:
        for path in ("../outside/input.json", self.outside / "input.json"):
            with self.subTest(path=str(path)):
                self.assert_builder_rejects_before_io("submission.json", path)

    def test_builder_rejects_real_directory_link_escape_before_reading(self) -> None:
        link = self.root / "linked"
        if os.name == "nt":
            result = subprocess.run(
                ["cmd", "/c", "mklink", "/J", str(link), str(self.outside)],
                capture_output=True, text=True, check=False,
            )
            if result.returncode:
                self.skipTest(f"junction creation unavailable: {result.stderr.strip()}")
            self.addCleanup(link.rmdir)
        else:
            try:
                link.symlink_to(self.outside, target_is_directory=True)
            except (OSError, NotImplementedError) as exc:
                self.skipTest(f"symlink creation unavailable: {exc}")
            self.addCleanup(link.unlink)
        self.assert_builder_rejects_before_io("linked/input.json")
        self.assert_builder_rejects_before_io("submission.json", "linked/input.json")

    def test_validator_does_not_read_or_hash_outside_manifest_paths(self) -> None:
        for path in ("../outside/input.json", str(self.outside / "input.json")):
            with self.subTest(path=path):
                bundle = {
                    "submission_path": path,
                    "report_path": path,
                    "prediction_path": path,
                    "files": [{"role": "report", "path": path}],
                }
                with (
                    mock.patch.object(submissions, "load_leaderboard_submission") as load,
                    mock.patch.object(submissions, "load_benchmark_report") as report,
                    mock.patch.object(submissions, "_canonical_file_bytes") as read,
                ):
                    result = submissions.validate_submission_bundle(bundle, base_dir=self.root)
                self.assertFalse(result["valid"])
                for name in ("submission_path", "report_path", "prediction_path", "files[0].path"):
                    self.assertTrue(any(name in error for error in result["errors"]))
                load.assert_not_called()
                report.assert_not_called()
                read.assert_not_called()

    def test_contained_submission_rejects_absolute_outside_report_before_reading(self) -> None:
        with mock.patch.object(submissions, "load_benchmark_report") as report:
            result = submissions.validate_leaderboard_submission(
                {"report_path": str(self.outside / "input.json")},
                base_dir=self.root,
                contained_report_root=self.root,
            )
        self.assertFalse(result["valid"])
        self.assertTrue(any("within the bundle root" in error for error in result["errors"]))
        report.assert_not_called()

    def test_builder_accepts_contained_absolute_paths_and_preserves_portability(self) -> None:
        root = Path(__file__).resolve().parents[1] / "submissions/example_publication_packet"
        bundle = submissions.build_submission_bundle(
            root / "submission.json", prediction_path=root / "predictions.jsonl", base_dir=root
        )
        self.assertEqual(bundle["submission_path"], "submission.json")
        self.assertEqual(bundle["prediction_path"], "predictions.jsonl")
        result = submissions.validate_submission_bundle(bundle, base_dir=root)
        self.assertTrue(result["valid"], result["errors"])


if __name__ == "__main__":
    unittest.main()
