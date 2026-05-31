# Release Notes v0.3.5

The Marked Bench v0.3.5 adds schema conformance checks for public artifacts.

## What Changed

- Added `marked_bench.schema_validation`, a dependency-free validator for the
  JSON Schema subset used by the benchmark.
- Extended `scripts/validate_benchmark_artifacts.py` so checked registries,
  suite manifests, baseline reports, leaderboards, release manifests, and
  generated prediction templates are checked against public schemas.
- Fixed the suite manifest schema so the current multi-hop suite ID and version
  are accepted by schema validation.
- Made the artifact validator read JSON files with UTF-8 BOM tolerance.

## Why It Matters

A benchmark standard should be machine-checkable by external adopters. This
release makes schema conformance part of the normal CI gate, so public JSON
artifacts are checked against the schemas they advertise.

## Compatibility

Suite IDs, suite versions, suite hashes, report schema, prediction schema, and
baseline scores are unchanged from v0.3.4. This release hardens validation only.
