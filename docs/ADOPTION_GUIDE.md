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

The current default public track is `contradiction-adversarial`:

```bash
marked-bench --suite contradiction-adversarial --export-prediction-template predictions.jsonl
marked-bench --suite contradiction-adversarial --score-predictions predictions.jsonl --system-name "your-system" --report your-system-report.json
marked-bench --validate-report your-system-report.json
```

Do not compare systems across different suite hashes.

## Submit A Result

1. Generate or score a full report.
2. Validate the report.
3. Generate submission metadata.
4. Disclose model, prompting, preprocessing, retrieval, postprocessing,
   training data, and runtime details.

```bash
marked-bench --create-submission your-submission.json --submission-report your-system-report.json --system-version "1.0.0" --submitter "name-or-org"
marked-bench --validate-submission your-submission.json
```

Leaderboard entries without a valid report and submission file should not be
ranked.

## Cite The Benchmark

Use `CITATION.cff` and include the release tag, suite ID, suite version, and
suite hash in papers, benchmark reports, or model cards.

## Maintain Compatibility

- Keep existing case IDs stable after release.
- Add new coverage through a new suite version or track.
- Regenerate suite manifests, reports, leaderboards, registry, technical note,
  and release manifest after public artifact changes.
- Run `python scripts/validate_benchmark_artifacts.py` before publishing.
