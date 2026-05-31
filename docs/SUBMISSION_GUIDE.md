# Benchmark Submission Guide

This guide describes how to submit a system result to The Marked Bench
leaderboard.

## 1. Choose A Track

Current tracks:

- `contradiction`: foundation suite, `marked-bench-contradiction-standard` v0.1.0.
- `contradiction-adversarial`: harder suite, `marked-bench-contradiction-adversarial`
  v0.2.0.
- `contradiction-multihop`: default linked-evidence suite,
  `marked-bench-contradiction-multihop` v0.3.0.
- `contradiction-controls`: false-positive controls suite,
  `marked-bench-contradiction-controls` v0.4.0.

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

For the multi-hop track:

```bash
marked-bench --suite contradiction-multihop --system-name "my-system" --report my-multihop-report.json
```

For the controls track:

```bash
marked-bench --suite contradiction-controls --system-name "my-system" --report my-controls-report.json
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
{"case_id":"marked-adv-direct-001","predicted":"direct_negation","detector_score":0.91,"rationale":"valid conflicts with invalid for the same token and review window","evidence":["access token remained valid through the review window","access token was invalid during the review window"]}
```

`detector_score` is optional, but when supplied it must be a finite number from
0 to 1. It is treated as confidence that the case contains a contradiction and
is used for Brier score and expected calibration error.

`rationale` and `evidence` are optional but recommended. They are carried into
the benchmark report and summarized under `explanation_audit` so reviewers can
see whether a result has inspectable reasoning evidence.

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

## 5. Build A Review Bundle

Before a leaderboard entry is reviewed, package the report and submission
metadata into a bundle manifest. The bundle pins every referenced file by
canonical SHA-256 digest and records whether the report, metadata, disclosures,
relative paths, and file hashes are ready for review.

```bash
marked-bench --create-submission-bundle my-submission-bundle.json --bundle-submission my-submission.json
marked-bench --validate-submission-bundle my-submission-bundle.json
```

If a prediction file is part of the submission evidence, include it too:

```bash
marked-bench --create-submission-bundle my-submission-bundle.json --bundle-submission my-submission.json --bundle-predictions predictions.jsonl
```

Bundle manifests use `schemas/submission_bundle.schema.json`.

A complete local example is available. It writes predictions, a scored report,
submission metadata, a bundle, and a review template:

```bash
python -m marked_bench.examples.external_submission_demo
```

The repository also includes a checked example packet at
`submissions/example_external_jsonl/`. It can be validated without regenerating
anything:

```bash
marked-bench --validate-submission-bundle submissions/example_external_jsonl/example_external_submission_bundle.json
marked-bench --validate-submission-review submissions/example_external_jsonl/example_external_submission_review.json
```

## 6. Create A Result Card

Result cards summarize the validated score, suite identity, evidence files,
review status, and publication claims in one citeable JSON artifact:

```bash
marked-bench --create-result-card my-result-card.json --result-report my-adversarial-report.json --result-bundle my-submission-bundle.json --result-review my-review.json
marked-bench --validate-result-card my-result-card.json
```

Result cards use `schemas/result_card.schema.json`. They do not replace the
full report, bundle, or review; they point to those files and pin their hashes.

## 7. Update Leaderboard

For foundation entries:

```bash
marked-bench --build-leaderboard baselines/*.json --leaderboard-output leaderboard/leaderboard_v0_1_0.json
```

For adversarial entries:

```bash
marked-bench --build-leaderboard baselines/*adversarial*.json --leaderboard-output leaderboard/leaderboard_adversarial_v0_2_0.json
```

For multi-hop entries:

```bash
marked-bench --build-leaderboard baselines/*multihop*.json --leaderboard-output leaderboard/leaderboard_multihop_v0_3_0.json
```

For controls entries:

```bash
marked-bench --build-leaderboard baselines/*controls*.json --leaderboard-output leaderboard/leaderboard_controls_v0_4_0.json
```

## 8. Run Repository Checks

```bash
python -m unittest discover -s tests
python scripts/validate_benchmark_artifacts.py
```

Both commands must pass before a submission is ready for review.

## 9. Create A Review Rubric

Leaderboard maintainers should create a structured review file before accepting
an entry:

```bash
marked-bench --create-submission-review my-review.json --review-bundle my-submission-bundle.json --reviewer reviewer-name
marked-bench --validate-submission-review my-review.json
```

Fill the rubric scores in `my-review.json` after checking reproducibility,
disclosures, score integrity, explanation coverage, evidence quality, and
limitations. See `docs/SUBMISSION_REVIEW_RUBRIC.md`.
