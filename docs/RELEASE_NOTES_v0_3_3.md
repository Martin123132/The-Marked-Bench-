# Release Notes v0.3.3

The Marked Bench v0.3.3 strengthens external validation and explanation review.

## What Changed

- Upgraded contradiction report schema metadata to
  `marked_bench.contradiction-benchmark-report.v2`.
- Upgraded prediction schema metadata to
  `marked_bench.contradiction-predictions.v2`.
- Added optional `rationale` and `evidence` fields to prediction records and
  per-case report results.
- Added report-level `explanation_audit` coverage for rationale and evidence
  availability.
- Updated public JSON schemas so the default multi-hop suite is accepted by
  external schema validators.

## Why It Matters

External submissions can now carry inspectable reasoning evidence alongside
their labels and confidence scores. The primary benchmark score is unchanged,
but reviewers can distinguish bare label submissions from submissions that
explain and cite their decision basis.

## Compatibility

Suite IDs, suite versions, and suite hashes are unchanged from v0.3.0. Baseline
scores are unchanged. Report and prediction schema identifiers are updated
because the public report shape now includes explanation-audit fields.

Legacy v1 prediction files are still accepted by the scorer when their suite
metadata matches the selected public track.
