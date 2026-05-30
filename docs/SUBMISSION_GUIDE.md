# Benchmark Submission Guide

This guide describes how to submit a system result to The Marked Bench
leaderboard.

## 1. Choose A Track

Current tracks:

- `contradiction`: foundation suite, `marked-bench-contradiction-standard` v0.1.0.
- `contradiction-adversarial`: harder suite, `marked-bench-contradiction-adversarial`
  v0.2.0.

The machine-readable track registry is `benchmark_registry.json`. It lists the
canonical suite manifests, report schemas, prediction schema, baseline reports,
leaderboard snapshots, suite hashes, and commands for each public track.

## 2. Generate A Report

For the packaged symbolic baseline:

```bash
marked-bench --suite contradiction --system-name "ContradictionEngine" --report my-report.json
```

For the adversarial track:

```bash
marked-bench --suite contradiction-adversarial --system-name "my-system" --report my-adversarial-report.json
```

Custom systems should call
`marked_bench.contradiction.benchmark_suite.evaluate_standard_suite(...)` with
their detector function and write the returned JSON report.

External systems do not need to use Python. Export a fillable prediction file,
run your system over each `premise` and `query`, then score the predictions:

```bash
marked-bench --suite contradiction-adversarial --export-prediction-template predictions.jsonl
marked-bench --suite contradiction-adversarial --score-predictions predictions.jsonl --system-name "my-system" --report my-adversarial-report.json
```

Each JSONL line should contain at least:

```json
{"case_id":"marked-adv-direct-001","predicted":"direct_negation","detector_score":0.91,"detector_note":"optional rationale"}
```

`detector_score` is optional, but when supplied it must be a finite number from
0 to 1. It is treated as confidence that the case contains a contradiction and
is used for Brier score and expected calibration error.

Valid `predicted` labels are:

- `direct_negation`
- `property_mismatch`
- `definitional_violation`
- `universal_counterexample`
- `temporal_conflict`
- `none`

Prediction submissions must cover every case exactly once. The schema is
`schemas/contradiction_predictions.schema.json`.

## 3. Validate The Report

```bash
marked-bench --validate-report my-report.json
```

Validation recomputes metrics from `case_results`, verifies suite metadata,
checks the canonical case list and `suite_hash`, and rejects tampered aggregate
scores, calibration metrics, slice metrics, and failure lists.

## 4. Add Submission Metadata

A leaderboard submission should include:

- system name and version
- submitter
- report path
- report SHA-256 digest
- suite hash
- detector/model/prompt/rule configuration notes
- any preprocessing, retrieval, or postprocessing used

The schema is `schemas/leaderboard_submission.schema.json`.

You can generate and validate this metadata with the CLI:

```bash
marked-bench --create-submission my-submission.json --submission-report my-adversarial-report.json --system-version "1.0.0" --submitter "name-or-org" --submission-notes "configuration summary"
marked-bench --validate-submission my-submission.json
```

Optional disclosure fields can be supplied as repeated `--disclosure KEY=VALUE`
arguments. Supported keys are `system_description`, `model`, `prompting`,
`preprocessing`, `retrieval`, `postprocessing`, `training_data`, and `runtime`.
Missing disclosure fields are recorded as `not disclosed` so reviewers can see
what was and was not provided.

## 5. Update Leaderboard

For foundation entries:

```bash
marked-bench --build-leaderboard baselines/*.json --leaderboard-output leaderboard/leaderboard_v0_1_0.json
```

For adversarial entries:

```bash
marked-bench --build-leaderboard baselines/*adversarial*.json --leaderboard-output leaderboard/leaderboard_adversarial_v0_2_0.json
```

## 6. Run Repository Checks

```bash
python -m unittest discover -s tests
python scripts/validate_benchmark_artifacts.py
```

Both commands must pass before a submission is ready for review.
