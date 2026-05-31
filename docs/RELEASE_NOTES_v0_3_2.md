# Release Notes v0.3.2

The Marked Bench v0.3.2 adds an end-to-end external submission demo.

## What Changed

- Added `marked_bench.examples.external_submission_demo`.
- The demo writes a prediction JSONL file, scores it into a benchmark report,
  creates leaderboard submission metadata, builds a submission bundle, and
  validates the bundle.
- Updated README, adoption guide, and submission guide with the demo command.
- Replaced legacy project license branding with benchmark-specific The Marked
  Bench license metadata.

## Why It Matters

External submitters now have a concrete working reference for the full
submission path. This reduces friction for third-party leaderboard entries and
makes the benchmark easier to adopt as a standard process.

## Run It

```bash
python -m marked_bench.examples.external_submission_demo
marked-bench --validate-submission-bundle artifacts/external_submission_demo/example_external_submission_bundle.json
```

Generated files are written under `artifacts/external_submission_demo/`.

## Compatibility

The public suite IDs and suite hashes from v0.3.0 are unchanged. This release
adds adoption tooling only.
