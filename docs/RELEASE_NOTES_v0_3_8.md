# Release Notes v0.3.8

The Marked Bench v0.3.8 adds standard result cards for publishable benchmark
results.

## What Changed

- Added `marked_bench.benchmark_result_card`, which builds and validates a
  portable result card from a benchmark report, optional submission bundle, and
  optional structured review.
- Added `schemas/result_card.schema.json` and the checked example card
  `submissions/example_external_jsonl/example_external_result_card.json`.
- Added CLI commands for result cards:
  `--create-result-card` and `--validate-result-card`.
- Added result-card validation to the artifact validator and conformance report.
- Added result-card artifacts to the release manifest and adoption docs.

## Why It Matters

External teams need a single, citeable artifact that says exactly what was
measured, which suite hash was used, which evidence files back the score, and
whether the result is ready for leaderboard review. Result cards make benchmark
results easier to compare, audit, cite, and publish without hand-written
summaries drifting from the underlying JSON evidence.

## Compatibility

Suite IDs, suite versions, suite hashes, scoring weights, report schema,
prediction schema, baseline scores, and checked submission packet scoring are
unchanged from v0.3.7. This release adds standardized publication evidence
around existing benchmark reports.
