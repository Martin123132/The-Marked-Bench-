# Release Notes v0.3.1

The Marked Bench v0.3.1 adds formal submission bundle validation for external
leaderboard entries.

## What Changed

- Added `marked_bench.leaderboard-submission-bundle.v1`.
- Added `schemas/submission_bundle.schema.json`.
- Added CLI commands for creating and validating submission bundles.
- Updated the benchmark registry to advertise the submission bundle schema.
- Updated submission guidance so leaderboard entries require a valid report,
  submission metadata, and submission bundle.

## Why It Matters

A benchmark standard needs reviewable, portable submission evidence. The bundle
manifest pins the report, submission metadata, and optional prediction file by
canonical SHA-256 digest, then records a review checklist for report validity,
submission validity, disclosure completeness, relative paths, and current file
hashes.

## CLI

```bash
marked-bench --create-submission-bundle my-submission-bundle.json --bundle-submission my-submission.json
marked-bench --validate-submission-bundle my-submission-bundle.json
```

Prediction evidence can be included with:

```bash
marked-bench --create-submission-bundle my-submission-bundle.json --bundle-submission my-submission.json --bundle-predictions predictions.jsonl
```

## Compatibility

The public suite IDs and suite hashes from v0.3.0 are unchanged. This is a
review and governance release, not a case-content release.
