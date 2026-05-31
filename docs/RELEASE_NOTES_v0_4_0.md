# Release Notes v0.4.0

The Marked Bench v0.4.0 adds a public false-positive controls track for
contradiction detectors.

## Added

- New controls suite:
  `suites/marked_bench_contradiction_controls_v0_4_0.json`.
- New suite ID: `marked-bench-contradiction-controls`.
- New suite version: `0.4.0`.
- New baseline reports:
  `baselines/contradiction_engine_controls_v0_4_0.json` and
  `baselines/always_none_controls_v0_4_0.json`.
- New controls leaderboard:
  `leaderboard/leaderboard_controls_v0_4_0.json`.
- CLI support for `--suite contradiction-controls`.
- Public schemas, registry, release manifest, conformance report, adoption
  packet, and evidence ledger updated for the controls track.

## Track Purpose

The controls track targets false positives. It contains many non-contradiction
distractors covering paraphrase, scoped negatives, quantifier exceptions,
temporal changes, same-value numeric contexts, and harmless elaborations. It
also includes one anchor case for each contradiction label so systems cannot
win by predicting `none` for every case.

## Compatibility

Existing foundation, adversarial, and multi-hop suite cases are unchanged.
Existing result cards remain comparable when they pin the same suite ID, suite
version, and suite hash.

## Standardization Impact

This release makes the benchmark harder to game with over-sensitive
contradiction detectors and gives external adopters a dedicated false-positive
stress test alongside the foundation, adversarial, and multi-hop tracks.
