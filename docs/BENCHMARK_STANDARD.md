# The Marked Bench Contradiction Benchmark Standard

The Marked Bench contradiction benchmark is a versioned, reproducible test
suite for systems that classify contradictions between a premise and a query.

It is meant to be a public standard for this project area: every score is tied
to a suite ID, suite version, deterministic suite hash, case list, report
schema, confusion matrix, and per-class metrics.

## Suite Identity

- Foundation suite ID: `marked-bench-contradiction-standard`
- Foundation suite version: `0.1.0`
- Adversarial suite ID: `marked-bench-contradiction-adversarial`
- Adversarial suite version: `0.2.0`
- Multi-hop suite ID: `marked-bench-contradiction-multihop`
- Multi-hop suite version: `0.3.0`
- Report schema: `marked_bench.contradiction-benchmark-report.v1`
- Canonical builder: `marked_bench.contradiction.benchmark_suite.build_standard_suite`

Every manifest, report, leaderboard entry, registry track, and leaderboard
submission carries `suite_hash`: a SHA-256 digest of the ordered canonical case
records. Public comparisons should pin `suite_id`, `suite_version`, and
`suite_hash`.

## What It Measures

The benchmark covers five contradiction classes plus non-contradiction controls:

- `direct_negation`
- `property_mismatch`
- `definitional_violation`
- `universal_counterexample`
- `temporal_conflict`
- `none`

Cases include stable IDs, domain tags, difficulty tags, capability tags, and
plain-language notes.

Each suite manifest includes a `profile` block with label, domain, difficulty,
capability, and tag counts. It also records basic quality gates: minimum case
count, coverage of every contradiction label, presence of control cases,
multiple domains, and multiple difficulty levels.

## Scoring

The report includes:

- `overall_score`: weighted 0-100 score.
- `type_accuracy`: exact contradiction-class accuracy across all cases.
- `contradiction_type_accuracy`: exact class accuracy on contradiction cases.
- `contradiction_macro_f1`: macro F1 across contradiction classes.
- `coverage_index`: share of contradiction classes with non-zero recall.
- `detection`: binary contradiction-vs-none metrics.
- `calibration`: binary confidence calibration from `detector_score`.
- `per_class`: precision, recall, F1, and support for every label.
- `slices`: diagnostic performance by domain, difficulty, capability, and tag.
- `confusion_matrix`: expected label by predicted label.
- `failures`: all missed exact-label cases.

The source tree also includes JSON schemas for public infrastructure:

- `schemas/benchmark_registry.schema.json`
- `schemas/contradiction_benchmark_report.schema.json`
- `schemas/contradiction_predictions.schema.json`
- `schemas/contradiction_suite_manifest.schema.json`
- `schemas/leaderboard.schema.json`
- `schemas/leaderboard_submission.schema.json`
- `schemas/release_manifest.schema.json`

For a high-level summary of intended use, non-use, limitations, and
reproducibility expectations, see `docs/BENCHMARK_CARD.md`.
For a generated release summary with suite hashes, composition, baselines, and
reproducibility commands, see `docs/TECHNICAL_NOTE.md`.

The current overall score weights are:

- 45% contradiction macro F1
- 25% type accuracy
- 20% binary detection F1
- 10% class coverage

This keeps the benchmark from rewarding detectors that merely say
"contradiction" without identifying the kind of contradiction.

Slice metrics are included for diagnosis and review. They are not additional
leaderboard weights in the current release, but they make it clear whether a
system is failing specific difficulty bands, domains, capabilities, or tags.

`detector_score` is interpreted as confidence that the case contains a
contradiction. It must be a finite value from 0 to 1. The report includes
binary Brier score, expected calibration error, confidence bins, mean
confidence, and empirical positive rate.

## Run The Baseline

```bash
python -m marked_bench.examples.benchmark_standard_demo
```

The demo writes:

```text
artifacts/marked_bench_contradiction_benchmark_report.json
```

`artifacts/` is ignored because reports are generated evidence, not source.

After installing the package, the command-line runner is:

```bash
marked-bench --report artifacts/marked_bench_contradiction_benchmark_report.json
```

Use `--json` to print the full report to stdout.

Validate an existing report before leaderboard submission:

```bash
marked-bench --validate-report artifacts/marked_bench_contradiction_benchmark_report.json
```

Build a leaderboard from valid reports:

```bash
marked-bench --build-leaderboard baselines/always_none_v0_1_0.json baselines/contradiction_engine_v0_1_0.json --leaderboard-output leaderboard/leaderboard_v0_1_0.json
```

Export the registry that points to every public track, schema, suite manifest,
baseline, and leaderboard:

```bash
marked-bench --export-registry benchmark_registry.json
```

Export the release manifest that pins public benchmark artifacts by SHA-256:

```bash
marked-bench --export-release-manifest releases/marked_bench_release_v0_3_0.json
```

Run the harder adversarial track:

```bash
marked-bench --suite contradiction-adversarial --report artifacts/marked_bench_contradiction_adversarial_report.json
```

Run the multi-hop track:

```bash
marked-bench --suite contradiction-multihop --report artifacts/marked_bench_contradiction_multihop_report.json
```

The checked-in symbolic baseline lives at:

```text
baselines/contradiction_engine_v0_1_0.json
```

The checked-in suite manifest lives at:

```text
suites/marked_bench_contradiction_standard_v0_1_0.json
```

The checked-in adversarial suite manifest lives at:

```text
suites/marked_bench_contradiction_adversarial_v0_2_0.json
```

The checked-in multi-hop suite manifest lives at:

```text
suites/marked_bench_contradiction_multihop_v0_3_0.json
```

## Score A Custom Detector

```python
from marked_bench.contradiction.benchmark_suite import evaluate_standard_suite


def detect(claim):
    # Return Contradiction(...) or None.
    ...


report = evaluate_standard_suite(detect, system_name="my-detector")
print(report["overall_score"])
```

For systems outside Python, export a JSONL prediction template and score it
back into the same report schema:

```bash
marked-bench --suite contradiction-adversarial --export-prediction-template artifacts/predictions.jsonl
marked-bench --suite contradiction-adversarial --score-predictions artifacts/predictions.jsonl --system-name "my-detector" --report artifacts/my-detector.json
```

Every leaderboard entry should also include submission metadata that pins the
report SHA-256 digest, suite identity, score, submitter, system version, and
method disclosures:

```bash
marked-bench --create-submission artifacts/my-detector-submission.json --submission-report artifacts/my-detector.json --system-version "1.0.0" --submitter "name-or-org"
marked-bench --validate-submission artifacts/my-detector-submission.json
```

## Standardization Rules

- Do not edit the meaning of existing case IDs after publication.
- Add cases by bumping `SUITE_VERSION`.
- Keep all reports JSON serializable.
- Report every failure, not only aggregate scores.
- Compare systems only when they use the same `suite_id` and `suite_version`.
- Treat `suite_hash` mismatches as incompatible results even if the version
  string is the same.
- Preserve non-contradiction controls so false positives remain visible.
- Reject leaderboard reports that do not pass the built-in validator.
- Keep `python scripts/validate_benchmark_artifacts.py` passing after any
  baseline, suite, or leaderboard change.

## Current Status

Version `0.1.0` is a foundation suite. Version `0.2.0` adds an adversarial
track with longer context, implicit contradictions, paraphrase traps, and
distractor controls. Version `0.3.0` adds a multi-hop track for linked-evidence
contradictions. The next step toward a larger public standard is adding
model-generated explanation review and third-party submissions.
