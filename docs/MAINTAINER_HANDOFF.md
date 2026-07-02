# Maintainer Handoff

Use this handoff when preparing changes, reviewing submissions, or publishing a
release.

## Before A PR

1. Confirm the branch starts from current `main`.
2. Keep public case IDs stable; add new coverage through a new suite version or
   new track.
3. Regenerate deterministic artifacts after changing public evidence.
4. Run the local checks listed in `CONTRIBUTING.md`.
5. Include exact report paths, hashes, and validation output in the PR body.

## Required Local Checks

```bash
python -m unittest discover -s tests
python scripts/validate_benchmark_artifacts.py
python -m marked_bench.benchmark_cli --check-standard-status
python scripts/check_scoring_sanity.py --artifact docs/SCORING_SANITY.md
python scripts/check_case_quality.py --artifact docs/CASE_QUALITY.md
python scripts/check_baseline_robustness.py --artifact docs/BASELINE_ROBUSTNESS.md
python scripts/regenerate_release_artifacts.py --check
python scripts/check_review_workflow.py
python scripts/check_license_notice.py
```

## Submission Review

1. Validate the report with `marked-bench --validate-report PATH`.
2. Confirm suite ID, suite version, suite hash, and report schema match the
   intended leaderboard.
3. Require submission metadata, bundle, review file, and result card for
   accepted public entries.
4. Require publication packet and result claim for public score statements.
5. Record reviewer notes when a result depends on prompting, retrieval,
   preprocessing, postprocessing, or undisclosed model behavior.

## Release Hygiene

- Keep `docs/PROJECT_STATUS.md` current when project posture changes.
- Keep `docs/BASELINE_ROBUSTNESS.md` current when leaderboard baselines change.
- Keep `docs/RELEASE_CHECKLIST.md` aligned with CI.
- Keep license and commercial-use language synchronized across `LICENSE`,
  `COMMERCIAL-LICENSE.md`, `NOTICE.md`, and `README.md`.
- Do not merge release-affecting changes when `scripts/regenerate_release_artifacts.py --check`
  reports drift.
