# Release Notes v0.1.1

Foundation suite `0.1.1` expands the active `marked-bench-contradiction-standard`
track while preserving the published `0.1.0` foundation suite for legacy
comparisons.

## What Changed

- Added six new foundation cases across status polarity, unit mismatch,
  definitional denial, evidence counterexamples, temporal review drift, and
  harmless evidence elaboration.
- Added active `0.1.1` suite, baseline, and leaderboard artifacts.
- Added `HashPriorBaseline`, a deterministic low-information reference baseline
  for leaderboard calibration.
- Added scoring and case-quality reviewer artifacts.

## Compatibility

- Existing `0.1.0` case IDs and artifacts remain checked and validated.
- Public comparisons must continue to pin `suite_id`, `suite_version`, and
  `suite_hash`.
- The `contradiction` alias points to active foundation suite `0.1.1`.
- Use `contradiction-v0.1.0` when reproducing legacy foundation reports.

## Validation

The release package is expected to pass:

```bash
python -m unittest discover -s tests
python scripts/validate_benchmark_artifacts.py
python -m marked_bench.benchmark_cli --check-standard-status
python scripts/check_scoring_sanity.py --artifact docs/SCORING_SANITY.md
python scripts/check_case_quality.py --artifact docs/CASE_QUALITY.md
```
