# Release Notes v0.3.6

The Marked Bench v0.3.6 adds a checked external-style submission packet and
makes that packet part of the normal artifact gate.

## What Changed

- Added `submissions/example_external_jsonl/` with JSONL predictions, a scored
  report, leaderboard submission metadata, a submission bundle, and a structured
  review file.
- Extended `scripts/validate_benchmark_artifacts.py` so the checked packet's
  report, bundle, review, prediction score, and referenced hashes are validated.
- Added the checked submission packet to the release manifest so downstream
  users can audit it as a pinned benchmark artifact.
- Updated submission and adoption docs to point at the checked packet as the
  reference shape for external systems.

## Why It Matters

External adoption needs a concrete packet to copy and verify. This release makes
the external-submission workflow inspectable from the repository itself instead
of only describing it in prose.

## Compatibility

Suite IDs, suite versions, suite hashes, scoring weights, report schema,
prediction schema, and baseline scores are unchanged from v0.3.5. This release
adds checked submission evidence and hardens validation around it.
