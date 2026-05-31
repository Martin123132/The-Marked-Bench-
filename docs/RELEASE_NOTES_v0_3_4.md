# Release Notes v0.3.4

The Marked Bench v0.3.4 adds a structured submission review rubric.

## What Changed

- Added `marked_bench.benchmark_review` for building and validating review
  rubric files.
- Added CLI commands:
  - `marked-bench --create-submission-review REVIEW --review-bundle BUNDLE`
  - `marked-bench --validate-submission-review REVIEW`
- Added `schemas/submission_review.schema.json`.
- Added `docs/SUBMISSION_REVIEW_RUBRIC.md`.
- Updated the benchmark registry and release manifest to advertise the review
  schema and rubric document.

## Why It Matters

Benchmark standards need reviewable governance, not only scores. The review
rubric gives leaderboard maintainers a consistent way to evaluate
reproducibility, disclosures, score integrity, explanation coverage, evidence
quality, and limitations before accepting a public entry.

## Compatibility

Suite IDs, suite versions, suite hashes, report schema, prediction schema, and
baseline scores are unchanged from v0.3.3. This release adds review governance
infrastructure only.
