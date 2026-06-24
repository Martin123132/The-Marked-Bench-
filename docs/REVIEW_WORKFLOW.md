# Review Workflow

Use this workflow to triage benchmark cases, baseline reports, leaderboard
submissions, and standard changes.

## Label States

- `triage-ready`: issue or PR has enough context for initial routing.
- `needs-evidence`: report, prediction, hash, provenance, or artifact evidence
  is missing.
- `needs-repro`: reproduction command, environment note, or deterministic input
  is missing.
- `scoring-review`: scoring, leaderboard ranking, or metric behavior needs
  reviewer attention.
- `accepted-baseline`: checked reference result has been accepted.
- `blocked-by-validation`: required validator fails or has not been run.
- `ready-for-review`: evidence is complete enough for reviewer decision.

## Review Order

1. Confirm the target suite and suite version.
2. Confirm all referenced artifacts exist and validate.
3. Compare report metadata against the target leaderboard track.
4. Check disclosure completeness and reviewer notes.
5. Apply final review decision in the submission review artifact.

## Required Evidence

- Benchmark report JSON.
- Prediction file when the result was externally scored.
- Submission metadata.
- Submission bundle.
- Review artifact for accepted leaderboard entries.
- Result card for cited or ranked results.
- Publication packet and result claim for public score statements.

## Validation Commands

```bash
python -m unittest discover -s tests
python scripts/validate_benchmark_artifacts.py
python -m marked_bench.benchmark_cli --check-standard-status
python scripts/check_scoring_sanity.py --artifact docs/SCORING_SANITY.md
python scripts/check_case_quality.py --artifact docs/CASE_QUALITY.md
python scripts/regenerate_release_artifacts.py --check
python scripts/check_review_workflow.py
python scripts/check_license_notice.py
```
