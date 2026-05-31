# Release Notes v0.4.6

The Marked Bench v0.4.6 adds a language-neutral scoring specification for
independent benchmark implementations.

## Added

- `marked_bench.benchmark_scoring_spec`, which builds and validates the
  normative scoring contract for labels, prediction validation, metric
  formulas, rounding, calibration, report semantics, and compatibility checks.
- `schemas/scoring_spec.schema.json` for validating scoring spec artifacts.
- `standard/marked_bench_scoring_spec_v0_4_6.json`, the checked current scoring
  specification.
- `docs/SCORING_SPEC.md`, generated from the same scoring spec JSON for human
  implementers.
- CLI commands for exporting and validating the scoring spec:
  `--export-scoring-spec`, `--validate-scoring-spec`, and
  `--export-scoring-spec-doc`.

## Changed

- Release conformance now checks the scoring spec JSON and generated Markdown
  document.
- The registry, standard profile, adoption packet, implementation kit,
  announcement package, roadmap, and release checklist now include scoring spec
  evidence.
- Current release paths move from v0.4.5 to v0.4.6.

## Compatibility

The public suites, case IDs, labels, scoring weights, and compatibility vectors
are unchanged from v0.4.5. This release makes the scoring contract easier to
reimplement outside Python.

## Validation

Regenerate and validate the release with:

```bash
marked-bench --export-scoring-spec standard/marked_bench_scoring_spec_v0_4_6.json
marked-bench --validate-scoring-spec standard/marked_bench_scoring_spec_v0_4_6.json
marked-bench --export-scoring-spec-doc docs/SCORING_SPEC.md
python scripts/validate_benchmark_artifacts.py
python -m unittest discover -s tests
```
