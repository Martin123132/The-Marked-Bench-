# Release Checklist

Use this before tagging or publishing a benchmark release.

## Required Checks

```bash
python -m unittest discover -s tests
python scripts/validate_benchmark_artifacts.py
git diff --check
```

## Artifact Checks

- Suite manifests are updated under `suites/`.
- Baseline reports are updated under `baselines/`.
- Leaderboard snapshots are updated under `leaderboard/`.
- `benchmark_registry.json` matches the code-generated registry.
- `releases/marked_bench_release_v0_3_8.json` matches the current public
  artifact hashes.
- `conformance/marked_bench_conformance_v0_3_8.json` validates against the
  current release evidence.
- `docs/TECHNICAL_NOTE.md` matches generated benchmark evidence.
- JSON schemas still match the public report shapes.
- Checked public JSON artifacts conform to their public schemas.
- Prediction template export and scoring commands run for each public suite.
- Submission metadata create and validate commands run against at least one
  valid report.
- Submission bundle create and validate commands run against at least one valid
  report/submission pair.
- Submission review create and validate commands run against at least one valid
  bundle.
- Result card create and validate commands run against at least one valid
  report/bundle/review packet.
- Checked submission packets under `submissions/` validate end-to-end.
- Documentation mentions every public track and suite version.
- `docs/BENCHMARK_CARD.md` reflects current scope and limitations.
- `docs/RELEASE_NOTES_v0_2_0.md` summarizes the public release.
- `docs/RELEASE_NOTES_v0_3_0.md` summarizes the public release.
- `docs/RELEASE_NOTES_v0_3_1.md` summarizes the public release.
- `docs/RELEASE_NOTES_v0_3_2.md` summarizes the public release.
- `docs/RELEASE_NOTES_v0_3_3.md` summarizes the public release.
- `docs/RELEASE_NOTES_v0_3_4.md` summarizes the public release.
- `docs/RELEASE_NOTES_v0_3_5.md` summarizes the public release.
- `docs/RELEASE_NOTES_v0_3_6.md` summarizes the public release.
- `docs/RELEASE_NOTES_v0_3_7.md` summarizes the public release.
- `docs/RELEASE_NOTES_v0_3_8.md` summarizes the public release.
- `docs/ADOPTION_GUIDE.md` explains how external systems should submit results.
- `docs/SUBMISSION_REVIEW_RUBRIC.md` explains how reviewers should score
  submissions before leaderboard acceptance.

## Release Notes

Record:

- suite IDs and versions
- suite hashes
- case counts
- suite profile and coverage-gate changes
- baseline scores
- calibration metric changes
- known limitations
- migration notes from previous suite versions

## Publication

- Push a clean git branch.
- Confirm GitHub Actions pass.
- Create a version tag.
- Attach or link suite manifests, baseline reports, leaderboard snapshots,
  conformance report, and checked result-card examples.
