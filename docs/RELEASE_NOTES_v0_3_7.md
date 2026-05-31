# Release Notes v0.3.7

The Marked Bench v0.3.7 adds machine-readable conformance reporting for the
release package.

## What Changed

- Added `marked_bench.benchmark_conformance`, which builds and validates a
  deterministic conformance report from the current registry, release manifest,
  suite manifests, baseline reports, leaderboards, schemas, prediction
  templates, and checked submission packet.
- Added `schemas/conformance_report.schema.json` and the checked report
  `conformance/marked_bench_conformance_v0_3_7.json`.
- Added CLI commands for exporting and validating conformance reports:
  `--export-conformance-report` and `--validate-conformance-report`.
- Added the conformance report to the release manifest so release-package
  consistency is itself a pinned artifact.

## Why It Matters

A benchmark standard needs a single portable proof that the release package is
internally coherent. Conformance reports give maintainers and adopters a
machine-checkable acceptance artifact instead of asking them to infer validity
from several separate files and commands.

## Compatibility

Suite IDs, suite versions, suite hashes, scoring weights, report schema,
prediction schema, baseline scores, and submission packet contents are
unchanged from v0.3.6. This release adds conformance evidence around the
existing benchmark package.
