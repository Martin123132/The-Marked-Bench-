# Release Notes v0.4.5

The Marked Bench v0.4.5 adds deterministic scoring compatibility vectors for
external implementations.

## Added

- `marked_bench.benchmark_scoring_compatibility`, which builds and validates a
  checked scoring compatibility profile from the current public tracks.
- `schemas/scoring_compatibility.schema.json` for validating compatibility
  profile artifacts.
- `standard/marked_bench_scoring_compatibility_v0_4_5.json`, the checked
  current compatibility profile.
- CLI commands for exporting and validating compatibility vectors:
  `--export-scoring-compatibility` and `--validate-scoring-compatibility`.

## Changed

- Release conformance now checks scoring compatibility evidence.
- The benchmark registry, standard profile, adoption packet, implementation
  kit, release checklist, and announcement package now include the scoring
  compatibility profile.
- Current release paths move from v0.4.4 to v0.4.5.

## Compatibility

The public suites, case IDs, labels, and scoring weights are unchanged from
v0.4.4. This release adds cross-implementation scoring evidence around the
existing scoring contract.

## Validation

Regenerate and validate the release with:

```bash
marked-bench --export-scoring-compatibility standard/marked_bench_scoring_compatibility_v0_4_5.json
marked-bench --validate-scoring-compatibility standard/marked_bench_scoring_compatibility_v0_4_5.json
python scripts/validate_benchmark_artifacts.py
python -m unittest discover -s tests
```
