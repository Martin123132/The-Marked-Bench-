# Adoption Guide

This guide is for teams that want to use The Marked Bench as a reproducible
contradiction-detection benchmark.

## Pin The Evaluation

Every published result should pin:

- suite ID
- suite version
- suite hash
- report schema
- exact report JSON
- explanation-audit coverage, when rationale/evidence fields are submitted

The current default public track is `contradiction-multihop`:

```bash
marked-bench --suite contradiction-multihop --export-prediction-template predictions.jsonl
marked-bench --suite contradiction-multihop --score-predictions predictions.jsonl --system-name "your-system" --report your-system-report.json
marked-bench --validate-report your-system-report.json
```

Do not compare systems across different suite hashes.

## Submit A Result

1. Generate or score a full report.
2. Validate the report.
3. Generate submission metadata.
4. Build and validate a submission bundle.
5. Disclose model, prompting, preprocessing, retrieval, postprocessing,
   training data, and runtime details.
6. Include `rationale` and `evidence` in prediction records when the system can
   expose its decision basis.

```bash
marked-bench --create-submission your-submission.json --submission-report your-system-report.json --system-version "1.0.0" --submitter "name-or-org"
marked-bench --validate-submission your-submission.json
marked-bench --create-submission-bundle your-submission-bundle.json --bundle-submission your-submission.json
marked-bench --validate-submission-bundle your-submission-bundle.json
```

Leaderboard entries without a valid report, submission file, and submission
bundle should not be ranked.

Accepted leaderboard entries should also have a validated submission review
file using `docs/SUBMISSION_REVIEW_RUBRIC.md`.

For a complete local example that writes predictions, report, submission
metadata, bundle evidence, and a review template, run:

```bash
python -m marked_bench.examples.external_submission_demo
```

## Cite The Benchmark

Use `CITATION.cff` and include the release tag, suite ID, suite version, and
suite hash in papers, benchmark reports, or model cards.

## Maintain Compatibility

- Keep existing case IDs stable after release.
- Add new coverage through a new suite version or track.
- Regenerate suite manifests, reports, leaderboards, registry, technical note,
  and release manifest after public artifact changes.
- Run `python scripts/validate_benchmark_artifacts.py` before publishing.
